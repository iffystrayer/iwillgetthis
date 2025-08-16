"""
Enhanced Role-Based Access Control (RBAC) Router for Aegis Risk Management Platform
Provides comprehensive RBAC endpoints for enterprise permission management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from auth import get_current_active_user
from models.user import User
from models.rbac import (
    Permission, EnhancedRole, EnhancedUserRole, RoleRequest, 
    PermissionGrant, AccessControlList, RoleUsageLog
)
from models.audit import AuditLog
from services.rbac_service import rbac_service
from schemas.rbac import (
    PermissionCreate, PermissionResponse, RoleCreate, RoleUpdate, RoleResponse,
    UserRoleAssignmentCreate, UserRoleAssignmentResponse, RoleRequestCreate, RoleRequestResponse,
    RoleRequestApproval, PermissionGrantCreate, PermissionGrantResponse,
    ACLCreate, ACLResponse, UserPermissionStatus, PermissionCheckRequest, PermissionCheckResponse,
    BulkRoleAssignment, BulkRoleAssignmentResponse, BulkPermissionGrant, BulkPermissionGrantResponse,
    RBACAnalytics, ComplianceReport, RoleCleanupRequest, RoleCleanupResponse
)

router = APIRouter()


def require_admin_permission(current_user: User = Depends(get_current_active_user)):
    """Dependency to check admin permissions"""
    # Check if user has admin role (simplified check - enhance based on your RBAC implementation)
    if not hasattr(current_user, 'roles') or not any(role.name == "Admin" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    return current_user


# Permission Management Endpoints
@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Create a new permission (Admin only)"""
    
    result = rbac_service.create_permission(
        name=permission.name,
        resource=permission.resource,
        action=permission.action,
        display_name=permission.display_name,
        description=permission.description,
        scope=permission.scope,
        category=permission.category,
        is_sensitive=permission.is_sensitive,
        db=db
    )
    
    return result


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    category: Optional[str] = Query(None, description="Filter by category"),
    resource: Optional[str] = Query(None, description="Filter by resource"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all permissions with optional filtering"""
    
    query = db.query(Permission).filter(Permission.is_active == True)
    
    if category:
        query = query.filter(Permission.category == category)
    if resource:
        query = query.filter(Permission.resource == resource)
    
    permissions = query.order_by(Permission.category, Permission.name).all()
    return permissions


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific permission"""
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission


# Role Management Endpoints
@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Create a new role with permissions and hierarchy (Admin only)"""
    
    result = rbac_service.create_role(
        name=role.name,
        display_name=role.display_name,
        description=role.description,
        level=role.level,
        permissions=role.permissions,
        parent_roles=role.parent_roles,
        created_by=current_user,
        db=db
    )
    
    return result


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    include_inactive: bool = Query(False, description="Include inactive roles"),
    level: Optional[int] = Query(None, description="Filter by role level"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all roles with optional filtering"""
    
    query = db.query(EnhancedRole)
    
    if not include_inactive:
        query = query.filter(EnhancedRole.is_active == True)
    if level is not None:
        query = query.filter(EnhancedRole.level == level)
    
    roles = query.order_by(EnhancedRole.level, EnhancedRole.name).all()
    
    # Add current user count for each role
    for role in roles:
        user_count = db.query(EnhancedUserRole).filter(
            EnhancedUserRole.role_id == role.id,
            EnhancedUserRole.is_active == True,
            EnhancedUserRole.status == "active"
        ).count()
        role.current_user_count = user_count
    
    return roles


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific role with permissions and hierarchy"""
    
    role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Add current user count
    user_count = db.query(EnhancedUserRole).filter(
        EnhancedUserRole.role_id == role_id,
        EnhancedUserRole.is_active == True,
        EnhancedUserRole.status == "active"
    ).count()
    role.current_user_count = user_count
    
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Update a role (Admin only)"""
    
    role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Update basic fields
    for field, value in role_update.dict(exclude_unset=True).items():
        if field == "permissions":
            rbac_service.assign_permissions_to_role(role_id, value, db)
        elif field == "parent_roles":
            rbac_service.set_role_parents(role_id, value, db)
        else:
            setattr(role, field, value)
    
    role.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(role)
    
    # Log role update
    audit_log = AuditLog(
        event_type="role_updated",
        entity_type="role",
        entity_id=role.id,
        user_id=current_user.id,
        action="Role updated",
        description=f"Updated role '{role.name}'",
        source="admin_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return role


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Delete a role (Admin only)"""
    
    role = db.query(EnhancedRole).filter(EnhancedRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system role"
        )
    
    # Check if role has active assignments
    active_assignments = db.query(EnhancedUserRole).filter(
        EnhancedUserRole.role_id == role_id,
        EnhancedUserRole.is_active == True
    ).count()
    
    if active_assignments > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role with {active_assignments} active assignments"
        )
    
    # Soft delete
    role.is_active = False
    role.updated_at = datetime.utcnow()
    db.commit()
    
    # Log role deletion
    audit_log = AuditLog(
        event_type="role_deleted",
        entity_type="role",
        entity_id=role.id,
        user_id=current_user.id,
        action="Role deleted",
        description=f"Deleted role '{role.name}'",
        source="admin_ui",
        risk_level="medium"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": f"Role '{role.name}' deleted successfully"}


# User Role Assignment Endpoints
@router.post("/user-roles", response_model=UserRoleAssignmentResponse)
async def assign_role_to_user(
    assignment: UserRoleAssignmentCreate,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Assign a role to a user (Admin only)"""
    
    result = rbac_service.assign_role_to_user(
        user_id=assignment.user_id,
        role_id=assignment.role_id,
        assigned_by=current_user,
        is_temporary=assignment.is_temporary,
        valid_until=assignment.valid_until,
        assignment_reason=assignment.assignment_reason,
        department_scope=assignment.department_scope,
        db=db
    )
    
    return result


@router.get("/users/{user_id}/roles", response_model=List[UserRoleAssignmentResponse])
async def get_user_roles(
    user_id: int,
    include_expired: bool = Query(False, description="Include expired assignments"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all roles assigned to a user"""
    
    # Users can only view their own roles unless they're admin
    if user_id != current_user.id and not any(role.name == "Admin" for role in getattr(current_user, 'roles', [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own roles"
        )
    
    user_roles = rbac_service.get_user_roles(user_id, include_expired, db)
    return user_roles


@router.get("/roles/{role_id}/users", response_model=List[UserRoleAssignmentResponse])
async def get_role_users(
    role_id: int,
    include_expired: bool = Query(False, description="Include expired assignments"),
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Get all users assigned to a role (Admin only)"""
    
    role_users = rbac_service.get_role_users(role_id, include_expired, db)
    return role_users


@router.delete("/user-roles/{assignment_id}")
async def remove_user_role(
    assignment_id: int,
    removal_reason: Optional[str] = Query(None, description="Reason for removal"),
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Remove a role assignment from a user (Admin only)"""
    
    assignment = db.query(EnhancedUserRole).filter(EnhancedUserRole.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    rbac_service.remove_role_from_user(
        assignment.user_id, assignment.role_id, current_user, removal_reason, db
    )
    
    return {"message": "Role assignment removed successfully"}


# Role Request Workflow
@router.post("/role-requests", response_model=RoleRequestResponse)
async def create_role_request(
    request: RoleRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a role assignment request"""
    
    result = rbac_service.create_role_request(
        user_id=request.user_id,
        role_id=request.role_id,
        requested_by=current_user,
        justification=request.justification,
        business_need=request.business_need,
        urgency=request.urgency,
        requested_duration_days=request.requested_duration_days,
        db=db
    )
    
    return result


@router.get("/role-requests", response_model=List[RoleRequestResponse])
async def get_role_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get role requests (users see their own, admins see all)"""
    
    query = db.query(RoleRequest)
    
    # Non-admin users can only see their own requests
    is_admin = any(role.name == "Admin" for role in getattr(current_user, 'roles', []))
    if not is_admin:
        query = query.filter(RoleRequest.requested_by_id == current_user.id)
    
    if status:
        query = query.filter(RoleRequest.status == status)
    if user_id and is_admin:
        query = query.filter(RoleRequest.user_id == user_id)
    
    requests = query.order_by(RoleRequest.created_at.desc()).all()
    return requests


@router.put("/role-requests/{request_id}/approve")
async def approve_role_request(
    request_id: int,
    approval: RoleRequestApproval,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Approve or reject a role request (Admin only)"""
    
    request = db.query(RoleRequest).filter(RoleRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role request not found"
        )
    
    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request is not pending"
        )
    
    # Update request status
    request.status = "approved" if approval.decision == "approve" else "rejected"
    request.approver_id = current_user.id
    request.approval_decision = approval.approval_decision
    request.approved_at = datetime.utcnow()
    
    # If approved, create the role assignment
    if approval.decision == "approve":
        valid_until = None
        if approval.assignment_duration_days:
            valid_until = datetime.utcnow() + timedelta(days=approval.assignment_duration_days)
        elif request.requested_duration_days:
            valid_until = datetime.utcnow() + timedelta(days=request.requested_duration_days)
        
        rbac_service.assign_role_to_user(
            user_id=request.user_id,
            role_id=request.role_id,
            assigned_by=current_user,
            is_temporary=valid_until is not None,
            valid_until=valid_until,
            assignment_reason=f"Approved request: {request.justification}",
            db=db
        )
    
    db.commit()
    
    # Log approval/rejection
    audit_log = AuditLog(
        event_type="role_request_processed",
        entity_type="role_request",
        entity_id=request.id,
        user_id=current_user.id,
        action=f"Role request {request.status}",
        description=f"Role request {request.status} by admin: {approval.approval_decision}",
        source="admin_ui",
        risk_level="medium"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": f"Role request {request.status} successfully"}


# Permission Grant Management
@router.post("/permission-grants", response_model=PermissionGrantResponse)
async def grant_permission_to_user(
    grant: PermissionGrantCreate,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Grant a permission directly to a user (Admin only)"""
    
    result = rbac_service.grant_permission_to_user(
        user_id=grant.user_id,
        permission_id=grant.permission_id,
        granted_by=current_user,
        grant_reason=grant.grant_reason,
        is_temporary=grant.is_temporary,
        valid_until=grant.valid_until,
        resource_scope=grant.resource_scope,
        db=db
    )
    
    return result


@router.get("/users/{user_id}/permission-grants", response_model=List[PermissionGrantResponse])
async def get_user_permission_grants(
    user_id: int,
    include_expired: bool = Query(False, description="Include expired grants"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get direct permission grants for a user"""
    
    # Users can only view their own grants unless they're admin
    if user_id != current_user.id and not any(role.name == "Admin" for role in getattr(current_user, 'roles', [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own permission grants"
        )
    
    query = db.query(PermissionGrant).filter(
        PermissionGrant.user_id == user_id,
        PermissionGrant.is_active == True
    )
    
    if not include_expired:
        query = query.filter(
            (PermissionGrant.valid_until.is_(None)) |
            (PermissionGrant.valid_until > datetime.utcnow())
        )
    
    grants = query.order_by(PermissionGrant.created_at.desc()).all()
    return grants


# Permission Checking
@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_user_permission(
    check: PermissionCheckRequest,
    user_id: Optional[int] = Query(None, description="User ID to check (defaults to current user)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if a user has a specific permission"""
    
    target_user_id = user_id or current_user.id
    
    # Users can only check their own permissions unless they're admin
    if target_user_id != current_user.id and not any(role.name == "Admin" for role in getattr(current_user, 'roles', [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only check your own permissions"
        )
    
    has_permission = rbac_service.check_permission(
        user_id=target_user_id,
        permission_name=check.permission,
        resource_id=check.resource_id,
        resource_type=check.resource_type,
        db=db
    )
    
    # Determine source of permission (simplified)
    source = "none"
    role_name = None
    
    if has_permission:
        user_permissions = rbac_service.get_user_permissions(target_user_id, db)
        if check.permission in user_permissions:
            source = "role"  # Could be enhanced to distinguish between role, direct_grant, acl
    
    return PermissionCheckResponse(
        has_permission=has_permission,
        permission=check.permission,
        source=source,
        role_name=role_name,
        resource_type=check.resource_type,
        resource_id=check.resource_id
    )


@router.get("/users/{user_id}/permissions", response_model=UserPermissionStatus)
async def get_user_permission_status(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive permission status for a user"""
    
    # Users can only view their own status unless they're admin
    if user_id != current_user.id and not any(role.name == "Admin" for role in getattr(current_user, 'roles', [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own permission status"
        )
    
    # Get user permissions
    permissions = rbac_service.get_user_permissions(user_id, db)
    
    # Get role assignments
    roles = rbac_service.get_user_roles(user_id, include_expired=False, db=db)
    
    # Get direct grants
    direct_grants = db.query(PermissionGrant).filter(
        PermissionGrant.user_id == user_id,
        PermissionGrant.is_active == True,
        (PermissionGrant.valid_until.is_(None)) |
        (PermissionGrant.valid_until > datetime.utcnow())
    ).all()
    
    # Get pending requests
    pending_requests = db.query(RoleRequest).filter(
        RoleRequest.user_id == user_id,
        RoleRequest.status == "pending"
    ).all()
    
    # Get ACL entries
    acl_entries = db.query(AccessControlList).filter(
        AccessControlList.subject_type == "user",
        AccessControlList.subject_id == user_id,
        AccessControlList.is_active == True,
        (AccessControlList.valid_until.is_(None)) |
        (AccessControlList.valid_until > datetime.utcnow())
    ).all()
    
    return UserPermissionStatus(
        user_id=user_id,
        permissions=permissions,
        roles=roles,
        direct_grants=direct_grants,
        pending_requests=pending_requests,
        acl_entries=acl_entries
    )


# Bulk Operations
@router.post("/bulk/role-assignments", response_model=BulkRoleAssignmentResponse)
async def bulk_assign_role(
    assignment: BulkRoleAssignment,
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Bulk assign role to multiple users (Admin only)"""
    
    successful_assignments = []
    failed_assignments = 0
    errors = []
    
    for user_id in assignment.user_ids:
        try:
            result = rbac_service.assign_role_to_user(
                user_id=user_id,
                role_id=assignment.role_id,
                assigned_by=current_user,
                is_temporary=assignment.is_temporary,
                valid_until=assignment.valid_until,
                assignment_reason=assignment.assignment_reason,
                db=db
            )
            successful_assignments.append(result)
        except Exception as e:
            failed_assignments += 1
            errors.append({
                "user_id": str(user_id),
                "error": str(e)
            })
    
    return BulkRoleAssignmentResponse(
        total_users=len(assignment.user_ids),
        successful_assignments=len(successful_assignments),
        failed_assignments=failed_assignments,
        errors=errors,
        assignments=successful_assignments
    )


# Analytics and Reporting
@router.get("/analytics", response_model=RBACAnalytics)
async def get_rbac_analytics(
    current_user: User = Depends(require_admin_permission),
    db: Session = Depends(get_db)
):
    """Get RBAC usage analytics (Admin only)"""
    
    # Basic statistics
    total_roles = db.query(EnhancedRole).filter(EnhancedRole.is_active == True).count()
    total_permissions = db.query(Permission).filter(Permission.is_active == True).count()
    total_active_assignments = db.query(EnhancedUserRole).filter(
        EnhancedUserRole.is_active == True,
        EnhancedUserRole.status == "active"
    ).count()
    
    pending_requests_count = db.query(RoleRequest).filter(RoleRequest.status == "pending").count()
    
    temporary_assignments_count = db.query(EnhancedUserRole).filter(
        EnhancedUserRole.is_active == True,
        EnhancedUserRole.is_temporary == True,
        EnhancedUserRole.valid_until > datetime.utcnow()
    ).count()
    
    # This is a simplified response - in production, you'd implement detailed analytics
    return RBACAnalytics(
        total_roles=total_roles,
        total_permissions=total_permissions,
        total_active_assignments=total_active_assignments,
        role_usage_stats=[],  # Implement detailed role usage statistics
        permission_usage_stats=[],  # Implement detailed permission usage statistics
        pending_requests_count=pending_requests_count,
        temporary_assignments_count=temporary_assignments_count,
        compliance_violations=[]  # Implement compliance violation detection
    )


# Cache Management
@router.post("/cache/clear")
async def clear_rbac_cache(
    current_user: User = Depends(require_admin_permission)
):
    """Clear RBAC permission and hierarchy caches (Admin only)"""
    
    rbac_service.clear_all_caches()
    
    return {"message": "RBAC caches cleared successfully"}