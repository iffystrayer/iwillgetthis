"""
Enhanced Role-Based Access Control (RBAC) Service for Aegis Risk Management Platform
Provides advanced permission management, role hierarchy, and access control
"""

import json
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from models.user import User
from models.rbac import (
    Permission, EnhancedRole, EnhancedUserRole, RoleRequest, 
    PermissionGrant, AccessControlList, RoleUsageLog, role_hierarchy
)
from models.audit import AuditLog


class RBACService:
    """Comprehensive RBAC service with enterprise features"""
    
    def __init__(self):
        # Cache for permission resolution to improve performance
        self._permission_cache = {}
        self._role_hierarchy_cache = {}
    
    # Permission Management
    def create_permission(self, name: str, resource: str, action: str, 
                         display_name: str = None, description: str = None,
                         scope: str = "global", category: str = None,
                         is_sensitive: bool = False, db: Session = None) -> Permission:
        """Create a new permission"""
        
        # Check if permission already exists
        existing = db.query(Permission).filter(Permission.name == name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission '{name}' already exists"
            )
        
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            display_name=display_name or f"{action.title()} {resource}",
            description=description,
            scope=scope,
            category=category,
            is_sensitive=is_sensitive,
            compliance_required=is_sensitive,  # Sensitive permissions require compliance
            audit_required=True
        )
        
        db.add(permission)
        db.commit()
        db.refresh(permission)
        
        return permission
    
    def get_permissions_by_category(self, category: str = None, db: Session = None) -> List[Permission]:
        """Get permissions by category"""
        query = db.query(Permission).filter(Permission.is_active == True)
        
        if category:
            query = query.filter(Permission.category == category)
        
        return query.order_by(Permission.category, Permission.name).all()
    
    # Role Management
    def create_role(self, name: str, display_name: str = None, description: str = None,
                   level: int = 0, permissions: List[int] = None, parent_roles: List[int] = None,
                   created_by: User = None, db: Session = None) -> EnhancedRole:
        """Create a new role with permissions and hierarchy"""
        
        # Check if role already exists
        existing = db.query(EnhancedRole).filter(EnhancedRole.name == name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{name}' already exists"
            )
        
        role = EnhancedRole(
            name=name,
            display_name=display_name or name,
            description=description,
            level=level,
            created_by_id=created_by.id if created_by else None
        )
        
        db.add(role)
        db.commit()
        db.refresh(role)
        
        # Add permissions
        if permissions:
            self.assign_permissions_to_role(role.id, permissions, db)
        
        # Set up role hierarchy
        if parent_roles:
            self.set_role_parents(role.id, parent_roles, db)
        
        # Log role creation
        if created_by:
            audit_log = AuditLog(
                event_type="role_created",
                entity_type="role",
                entity_id=role.id,
                user_id=created_by.id,
                action="Role created",
                description=f"Created role '{name}' with {len(permissions or [])} permissions",
                source="admin_ui",
                risk_level="low"
            )
            db.add(audit_log)
            db.commit()
        
        # Clear hierarchy cache
        self._role_hierarchy_cache.clear()
        
        return role
    
    def assign_permissions_to_role(self, role_id: int, permission_ids: List[int], db: Session = None):
        """Assign permissions to a role"""
        
        role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        permissions = db.query(Permission).filter(
            Permission.id.in_(permission_ids),
            Permission.is_active == True
        ).all()
        
        # Clear existing permissions
        role.permissions.clear()
        
        # Add new permissions
        for permission in permissions:
            role.permissions.append(permission)
        
        db.commit()
        
        # Clear permission cache
        self._permission_cache.clear()
    
    def set_role_parents(self, role_id: int, parent_role_ids: List[int], db: Session = None):
        """Set parent roles for role hierarchy"""
        
        role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Validate parent roles exist
        parent_roles = db.query(EnhancedRole).filter(
            EnhancedRole.id.in_(parent_role_ids),
            EnhancedRole.is_active == True
        ).all()
        
        if len(parent_roles) != len(parent_role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more parent roles not found"
            )
        
        # Check for circular dependencies
        for parent_role in parent_roles:
            if self._would_create_cycle(role_id, parent_role.id, db):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Adding parent role '{parent_role.name}' would create a circular dependency"
                )
        
        # Clear existing parent relationships
        role.parent_roles.clear()
        
        # Add new parent relationships
        for parent_role in parent_roles:
            role.parent_roles.append(parent_role)
        
        db.commit()
        
        # Clear hierarchy cache
        self._role_hierarchy_cache.clear()
    
    def _would_create_cycle(self, child_id: int, potential_parent_id: int, db: Session) -> bool:
        """Check if adding a parent would create a circular dependency"""
        
        visited = set()
        
        def check_ancestors(role_id: int) -> bool:
            if role_id in visited:
                return True  # Cycle detected
            
            if role_id == child_id:
                return True  # Would create cycle
            
            visited.add(role_id)
            
            # Get parent roles
            parent_ids = db.query(role_hierarchy.c.parent_role_id).filter(
                role_hierarchy.c.child_role_id == role_id
            ).all()
            
            for (parent_id,) in parent_ids:
                if check_ancestors(parent_id):
                    return True
            
            return False
        
        return check_ancestors(potential_parent_id)
    
    # User Role Assignment
    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by: User,
                           is_temporary: bool = False, valid_until: datetime = None,
                           assignment_reason: str = None, department_scope: str = None,
                           db: Session = None) -> EnhancedUserRole:
        """Assign a role to a user"""
        
        # Validate user and role exist
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
        # Check if assignment already exists
        existing = db.query(EnhancedUserRole).filter(
            EnhancedUserRole.user_id == user_id,
            EnhancedUserRole.role_id == role_id,
            EnhancedUserRole.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has this role"
            )
        
        # Check role requirements
        approval_required = role.requires_approval
        
        # Create role assignment
        user_role = EnhancedUserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by_id=assigned_by.id,
            assignment_reason=assignment_reason,
            is_temporary=is_temporary,
            valid_until=valid_until,
            department_scope=department_scope,
            status="pending" if approval_required else "active",
            approval_required=approval_required
        )
        
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        
        # Log role assignment
        audit_log = AuditLog(
            event_type="role_assigned",
            entity_type="user",
            entity_id=user_id,
            user_id=assigned_by.id,
            action="Role assigned",
            description=f"Assigned role '{role.name}' to user {user.email}",
            source="admin_ui",
            risk_level="medium" if role.requires_mfa else "low"
        )
        db.add(audit_log)
        db.commit()
        
        # Clear permission cache for user
        self._clear_user_permission_cache(user_id)
        
        return user_role
    
    def remove_role_from_user(self, user_id: int, role_id: int, removed_by: User, 
                             removal_reason: str = None, db: Session = None):
        """Remove a role from a user"""
        
        user_role = db.query(EnhancedUserRole).filter(
            EnhancedUserRole.user_id == user_id,
            EnhancedUserRole.role_id == role_id,
            EnhancedUserRole.is_active == True
        ).first()
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )
        
        # Deactivate the role assignment
        user_role.is_active = False
        user_role.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Log role removal
        role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
        user = db.query(User).filter(User.id == user_id).first()
        
        audit_log = AuditLog(
            event_type="role_removed",
            entity_type="user",
            entity_id=user_id,
            user_id=removed_by.id,
            action="Role removed",
            description=f"Removed role '{role.name}' from user {user.email}. Reason: {removal_reason}",
            source="admin_ui",
            risk_level="medium"
        )
        db.add(audit_log)
        db.commit()
        
        # Clear permission cache for user
        self._clear_user_permission_cache(user_id)
    
    # Permission Resolution and Checking
    def get_user_permissions(self, user_id: int, db: Session = None) -> Set[str]:
        """Get all permissions for a user (including inherited from roles)"""
        
        cache_key = f"user_permissions_{user_id}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]
        
        permissions = set()
        
        # Get direct permission grants
        direct_grants = db.query(PermissionGrant).join(Permission).filter(
            PermissionGrant.user_id == user_id,
            PermissionGrant.is_active == True,
            or_(
                PermissionGrant.valid_until.is_(None),
                PermissionGrant.valid_until > datetime.utcnow()
            ),
            Permission.is_active == True
        ).all()
        
        for grant in direct_grants:
            permissions.add(grant.permission.name)
        
        # Get permissions from roles
        user_roles = db.query(EnhancedUserRole).filter(
            EnhancedUserRole.user_id == user_id,
            EnhancedUserRole.is_active == True,
            EnhancedUserRole.status == "active",
            or_(
                EnhancedUserRole.valid_until.is_(None),
                EnhancedUserRole.valid_until > datetime.utcnow()
            )
        ).all()
        
        for user_role in user_roles:
            role_permissions = self.get_role_permissions(user_role.role_id, db, include_inherited=True)
            permissions.update(role_permissions)
        
        # Cache the result
        self._permission_cache[cache_key] = permissions
        
        return permissions
    
    def get_role_permissions(self, role_id: int, db: Session = None, include_inherited: bool = True) -> Set[str]:
        """Get all permissions for a role (including inherited from parent roles)"""
        
        cache_key = f"role_permissions_{role_id}_{include_inherited}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]
        
        permissions = set()
        
        # Get direct role permissions
        role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
        if not role:
            return permissions
        
        for permission in role.permissions:
            if permission.is_active:
                permissions.add(permission.name)
        
        # Get inherited permissions from parent roles
        if include_inherited:
            parent_roles = self.get_role_ancestors(role_id, db)
            for parent_role_id in parent_roles:
                parent_permissions = self.get_role_permissions(parent_role_id, db, include_inherited=False)
                permissions.update(parent_permissions)
        
        # Cache the result
        self._permission_cache[cache_key] = permissions
        
        return permissions
    
    def get_role_ancestors(self, role_id: int, db: Session = None) -> Set[int]:
        """Get all ancestor roles in the hierarchy"""
        
        cache_key = f"role_ancestors_{role_id}"
        if cache_key in self._role_hierarchy_cache:
            return self._role_hierarchy_cache[cache_key]
        
        ancestors = set()
        visited = set()
        
        def collect_ancestors(current_role_id: int):
            if current_role_id in visited:
                return  # Prevent infinite loops
            
            visited.add(current_role_id)
            
            # Get direct parent roles
            parent_ids = db.query(role_hierarchy.c.parent_role_id).filter(
                role_hierarchy.c.child_role_id == current_role_id
            ).all()
            
            for (parent_id,) in parent_ids:
                ancestors.add(parent_id)
                collect_ancestors(parent_id)
        
        collect_ancestors(role_id)
        
        # Cache the result
        self._role_hierarchy_cache[cache_key] = ancestors
        
        return ancestors
    
    def check_permission(self, user_id: int, permission_name: str, resource_id: int = None,
                        resource_type: str = None, db: Session = None) -> bool:
        """Check if user has a specific permission"""
        
        # Get user permissions
        user_permissions = self.get_user_permissions(user_id, db)
        
        # Check direct permission
        if permission_name in user_permissions:
            # Log permission usage
            self._log_permission_usage(user_id, permission_name, True, resource_type, resource_id, db)
            return True
        
        # Check resource-specific ACL
        if resource_id and resource_type:
            acl_granted = self._check_acl_permission(user_id, permission_name, resource_type, resource_id, db)
            if acl_granted:
                self._log_permission_usage(user_id, permission_name, True, resource_type, resource_id, db)
                return True
        
        # Log permission denial
        self._log_permission_usage(user_id, permission_name, False, resource_type, resource_id, db)
        return False
    
    def _check_acl_permission(self, user_id: int, permission_name: str, 
                             resource_type: str, resource_id: int, db: Session = None) -> bool:
        """Check resource-specific ACL permissions"""
        
        # Check direct user ACL
        user_acl = db.query(AccessControlList).join(Permission).filter(
            AccessControlList.resource_type == resource_type,
            AccessControlList.resource_id == resource_id,
            AccessControlList.subject_type == "user",
            AccessControlList.subject_id == user_id,
            AccessControlList.is_active == True,
            Permission.name == permission_name,
            or_(
                AccessControlList.valid_until.is_(None),
                AccessControlList.valid_until > datetime.utcnow()
            )
        ).first()
        
        if user_acl:
            return True
        
        # Check role-based ACL
        user_roles = db.query(EnhancedUserRole).filter(
            EnhancedUserRole.user_id == user_id,
            EnhancedUserRole.is_active == True,
            EnhancedUserRole.status == "active"
        ).all()
        
        for user_role in user_roles:
            role_acl = db.query(AccessControlList).join(Permission).filter(
                AccessControlList.resource_type == resource_type,
                AccessControlList.resource_id == resource_id,
                AccessControlList.subject_type == "role",
                AccessControlList.subject_id == user_role.role_id,
                AccessControlList.is_active == True,
                Permission.name == permission_name,
                or_(
                    AccessControlList.valid_until.is_(None),
                    AccessControlList.valid_until > datetime.utcnow()
                )
            ).first()
            
            if role_acl:
                return True
        
        return False
    
    def _log_permission_usage(self, user_id: int, permission_name: str, access_granted: bool,
                             resource_type: str = None, resource_id: int = None, db: Session = None):
        """Log permission usage for audit purposes"""
        
        permission = db.query(Permission).filter(Permission.name == permission_name).first()
        
        if permission and permission.audit_required:
            usage_log = RoleUsageLog(
                user_id=user_id,
                permission_id=permission.id,
                action_performed=permission_name,
                resource_type=resource_type,
                resource_id=resource_id,
                access_granted=access_granted
            )
            
            db.add(usage_log)
            db.commit()
    
    # Permission Grants (Direct permissions outside of roles)
    def grant_permission_to_user(self, user_id: int, permission_id: int, granted_by: User,
                                grant_reason: str, is_temporary: bool = False,
                                valid_until: datetime = None, resource_scope: Dict = None,
                                db: Session = None) -> PermissionGrant:
        """Grant a permission directly to a user"""
        
        # Validate user and permission
        user = db.query(User).filter(User.id == user_id).first()
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        
        # Check if grant already exists
        existing = db.query(PermissionGrant).filter(
            PermissionGrant.user_id == user_id,
            PermissionGrant.permission_id == permission_id,
            PermissionGrant.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already granted to user"
            )
        
        # Create permission grant
        grant = PermissionGrant(
            user_id=user_id,
            permission_id=permission_id,
            granted_by_id=granted_by.id,
            grant_reason=grant_reason,
            is_temporary=is_temporary,
            valid_until=valid_until,
            resource_scope=resource_scope
        )
        
        db.add(grant)
        db.commit()
        db.refresh(grant)
        
        # Log permission grant
        audit_log = AuditLog(
            event_type="permission_granted",
            entity_type="user",
            entity_id=user_id,
            user_id=granted_by.id,
            action="Direct permission granted",
            description=f"Granted permission '{permission.name}' to user {user.email}. Reason: {grant_reason}",
            source="admin_ui",
            risk_level="medium" if permission.is_sensitive else "low"
        )
        db.add(audit_log)
        db.commit()
        
        # Clear permission cache
        self._clear_user_permission_cache(user_id)
        
        return grant
    
    # Cache Management
    def _clear_user_permission_cache(self, user_id: int):
        """Clear permission cache for a specific user"""
        cache_key = f"user_permissions_{user_id}"
        if cache_key in self._permission_cache:
            del self._permission_cache[cache_key]
    
    def clear_all_caches(self):
        """Clear all permission and hierarchy caches"""
        self._permission_cache.clear()
        self._role_hierarchy_cache.clear()
    
    # Role Request Workflow
    def create_role_request(self, user_id: int, role_id: int, requested_by: User,
                           justification: str, business_need: str = None,
                           urgency: str = "normal", requested_duration_days: int = None,
                           db: Session = None) -> RoleRequest:
        """Create a role assignment request for approval"""
        
        # Validate user and role
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
        # Check if request already exists
        existing = db.query(RoleRequest).filter(
            RoleRequest.user_id == user_id,
            RoleRequest.role_id == role_id,
            RoleRequest.status == "pending"
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pending role request already exists"
            )
        
        # Create role request
        request = RoleRequest(
            user_id=user_id,
            role_id=role_id,
            requested_by_id=requested_by.id,
            request_type="assign",
            justification=justification,
            business_need=business_need,
            urgency=urgency,
            requested_duration_days=requested_duration_days
        )
        
        db.add(request)
        db.commit()
        db.refresh(request)
        
        # Log role request
        audit_log = AuditLog(
            event_type="role_request_created",
            entity_type="role_request",
            entity_id=request.id,
            user_id=requested_by.id,
            action="Role request created",
            description=f"Requested role '{role.name}' for user {user.email}",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return request
    
    # Utility Methods
    def get_user_roles(self, user_id: int, include_expired: bool = False, db: Session = None) -> List[EnhancedUserRole]:
        """Get all roles assigned to a user"""
        
        query = db.query(EnhancedUserRole).filter(
            EnhancedUserRole.user_id == user_id,
            EnhancedUserRole.is_active == True
        )
        
        if not include_expired:
            query = query.filter(
                or_(
                    EnhancedUserRole.valid_until.is_(None),
                    EnhancedUserRole.valid_until > datetime.utcnow()
                )
            )
        
        return query.all()
    
    def get_role_users(self, role_id: int, include_expired: bool = False, db: Session = None) -> List[EnhancedUserRole]:
        """Get all users assigned to a role"""
        
        query = db.query(EnhancedUserRole).filter(
            EnhancedUserRole.role_id == role_id,
            EnhancedUserRole.is_active == True
        )
        
        if not include_expired:
            query = query.filter(
                or_(
                    EnhancedUserRole.valid_until.is_(None),
                    EnhancedUserRole.valid_until > datetime.utcnow()
                )
            )
        
        return query.all()


# Global RBAC service instance
rbac_service = RBACService()