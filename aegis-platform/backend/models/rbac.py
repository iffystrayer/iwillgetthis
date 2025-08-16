"""
Enhanced Role-Based Access Control (RBAC) Models for Aegis Risk Management Platform
Supports hierarchical roles, granular permissions, and dynamic access control
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# Association table for role hierarchy (parent-child relationships)
role_hierarchy = Table(
    'role_hierarchy',
    Base.metadata,
    Column('parent_role_id', Integer, ForeignKey('enhanced_roles.id'), primary_key=True),
    Column('child_role_id', Integer, ForeignKey('enhanced_roles.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


# Association table for role-permission relationships
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('enhanced_roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('granted_by', Integer, ForeignKey('users.id')),
    Column('granted_at', DateTime(timezone=True), server_default=func.now())
)


class Permission(Base):
    """Granular permissions for system resources and actions"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "assets:read", "users:create"
    resource = Column(String(50), nullable=False)  # e.g., "assets", "users", "reports"
    action = Column(String(50), nullable=False)  # e.g., "read", "write", "delete", "admin"
    scope = Column(String(50), default="global")  # "global", "department", "own"
    
    # Permission metadata
    display_name = Column(String(200))  # User-friendly name
    description = Column(Text)
    category = Column(String(50))  # Group related permissions
    
    # Security and compliance
    is_sensitive = Column(Boolean, default=False)  # Requires additional approval
    compliance_required = Column(Boolean, default=False)  # SOX, GDPR compliance
    audit_required = Column(Boolean, default=True)  # Log all uses of this permission
    
    # Lifecycle management
    is_active = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    deprecation_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    roles = relationship("EnhancedRole", secondary=role_permissions, back_populates="permissions")


class EnhancedRole(Base):
    """Enhanced roles with hierarchy and advanced features"""
    __tablename__ = "enhanced_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200))
    description = Column(Text)
    
    # Role hierarchy and inheritance
    level = Column(Integer, default=0)  # Role level in hierarchy (0=highest)
    is_system_role = Column(Boolean, default=False)  # System-defined, cannot be deleted
    can_be_delegated = Column(Boolean, default=True)  # Can be assigned by other users
    
    # Role scope and limitations
    max_concurrent_users = Column(Integer)  # Limit concurrent assignments
    department_restricted = Column(Boolean, default=False)  # Restrict to specific departments
    allowed_departments = Column(JSON)  # List of allowed departments
    
    # Time-based role assignments
    supports_temporary_assignment = Column(Boolean, default=False)
    default_assignment_duration_days = Column(Integer)  # Default temp assignment duration
    
    # Security settings
    requires_approval = Column(Boolean, default=False)  # Assignment requires approval
    requires_mfa = Column(Boolean, default=False)  # Role usage requires MFA
    session_timeout_minutes = Column(Integer)  # Custom session timeout
    
    # Compliance and auditing
    compliance_level = Column(String(20), default="standard")  # "standard", "high", "critical"
    audit_level = Column(String(20), default="standard")  # Auditing intensity
    
    # Lifecycle management
    is_active = Column(Boolean, default=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    user_role_assignments = relationship("EnhancedUserRole", back_populates="role")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    # Self-referencing hierarchy relationships
    parent_roles = relationship(
        "EnhancedRole",
        secondary=role_hierarchy,
        primaryjoin=id == role_hierarchy.c.child_role_id,
        secondaryjoin=id == role_hierarchy.c.parent_role_id,
        back_populates="child_roles"
    )
    child_roles = relationship(
        "EnhancedRole",
        secondary=role_hierarchy,
        primaryjoin=id == role_hierarchy.c.parent_role_id,
        secondaryjoin=id == role_hierarchy.c.child_role_id,
        back_populates="parent_roles"
    )


class EnhancedUserRole(Base):
    """Enhanced user-role assignments with advanced features"""
    __tablename__ = "enhanced_user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("enhanced_roles.id"), nullable=False)
    
    # Assignment metadata
    assigned_by_id = Column(Integer, ForeignKey("users.id"))
    assignment_reason = Column(Text)
    assignment_context = Column(String(100))  # "promotion", "project", "temporary", etc.
    
    # Time-based assignments
    is_temporary = Column(Boolean, default=False)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))  # NULL for permanent assignments
    
    # Scope limitations
    department_scope = Column(String(100))  # Limit role to specific department
    project_scope = Column(String(100))  # Limit role to specific project
    resource_scope = Column(JSON)  # Limit role to specific resources
    
    # Status and approval
    status = Column(String(20), default="active")  # "pending", "active", "suspended", "expired"
    approval_required = Column(Boolean, default=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Usage tracking
    last_used = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    
    # Lifecycle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("EnhancedRole", back_populates="user_role_assignments")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])


class RoleRequest(Base):
    """Role assignment requests for approval workflows"""
    __tablename__ = "role_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("enhanced_roles.id"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request details
    request_type = Column(String(20), nullable=False)  # "assign", "remove", "extend"
    justification = Column(Text, nullable=False)
    business_need = Column(Text)
    urgency = Column(String(20), default="normal")  # "low", "normal", "high", "critical"
    
    # Time-based request details
    requested_duration_days = Column(Integer)  # For temporary assignments
    requested_valid_from = Column(DateTime(timezone=True))
    requested_valid_until = Column(DateTime(timezone=True))
    
    # Approval workflow
    status = Column(String(20), default="pending")  # "pending", "approved", "rejected", "withdrawn"
    approver_id = Column(Integer, ForeignKey("users.id"))
    approval_decision = Column(Text)  # Approval/rejection reasoning
    approved_at = Column(DateTime(timezone=True))
    
    # System tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("EnhancedRole")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approver = relationship("User", foreign_keys=[approver_id])


class PermissionGrant(Base):
    """Direct permission grants to users (outside of roles)"""
    __tablename__ = "permission_grants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    
    # Grant metadata
    granted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    grant_reason = Column(Text, nullable=False)
    grant_context = Column(String(100))  # "emergency", "project", "delegation"
    
    # Scope and limitations
    resource_scope = Column(JSON)  # Specific resources this grant applies to
    conditions = Column(JSON)  # Additional conditions for the grant
    
    # Time constraints
    is_temporary = Column(Boolean, default=False)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    revoked_by_id = Column(Integer, ForeignKey("users.id"))
    revoked_at = Column(DateTime(timezone=True))
    revoke_reason = Column(Text)
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("Permission")
    granted_by = relationship("User", foreign_keys=[granted_by_id])
    revoked_by = relationship("User", foreign_keys=[revoked_by_id])


class AccessControlList(Base):
    """Resource-specific access control lists"""
    __tablename__ = "access_control_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False)  # "asset", "risk", "report", etc.
    resource_id = Column(Integer, nullable=False)  # ID of the specific resource
    
    # Subject (who gets access)
    subject_type = Column(String(20), nullable=False)  # "user", "role", "group"
    subject_id = Column(Integer, nullable=False)  # ID of user/role/group
    
    # Access details
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    access_level = Column(String(20), default="read")  # "read", "write", "admin"
    
    # Grant metadata
    granted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    grant_reason = Column(Text)
    
    # Time constraints
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    permission = relationship("Permission")
    granted_by = relationship("User")


class RoleUsageLog(Base):
    """Audit log for role and permission usage"""
    __tablename__ = "role_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("enhanced_roles.id"))
    permission_id = Column(Integer, ForeignKey("permissions.id"))
    
    # Usage details
    action_performed = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    access_granted = Column(Boolean, nullable=False)
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(255))
    
    # Risk and compliance
    risk_score = Column(Integer, default=0)  # 0-100 risk assessment
    compliance_flags = Column(JSON)  # Compliance-related metadata
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    role = relationship("EnhancedRole")
    permission = relationship("Permission")