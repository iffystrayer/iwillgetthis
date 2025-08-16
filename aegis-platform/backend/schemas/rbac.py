"""
Enhanced RBAC (Role-Based Access Control) Schemas for Aegis Risk Management Platform
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime


# Permission schemas
class PermissionBase(BaseModel):
    name: str = Field(..., description="Unique permission name (e.g., 'assets:read')")
    resource: str = Field(..., description="Resource type (e.g., 'assets', 'users')")
    action: str = Field(..., description="Action type (e.g., 'read', 'write', 'delete')")
    scope: str = Field("global", description="Permission scope: 'global', 'department', 'own'")


class PermissionCreate(PermissionBase):
    display_name: Optional[str] = Field(None, description="User-friendly display name")
    description: Optional[str] = Field(None, description="Permission description")
    category: Optional[str] = Field(None, description="Permission category")
    is_sensitive: bool = Field(False, description="Requires additional approval")


class PermissionResponse(PermissionBase):
    id: int
    display_name: str
    description: Optional[str]
    category: Optional[str]
    is_sensitive: bool
    compliance_required: bool
    audit_required: bool
    is_active: bool
    is_deprecated: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., description="Unique role name")
    display_name: Optional[str] = Field(None, description="User-friendly display name")
    description: Optional[str] = Field(None, description="Role description")


class RoleCreate(RoleBase):
    level: int = Field(0, description="Role level in hierarchy (0=highest)")
    permissions: Optional[List[int]] = Field([], description="List of permission IDs")
    parent_roles: Optional[List[int]] = Field([], description="List of parent role IDs")
    requires_approval: bool = Field(False, description="Assignment requires approval")
    requires_mfa: bool = Field(False, description="Role usage requires MFA")
    max_concurrent_users: Optional[int] = Field(None, description="Max concurrent assignments")
    supports_temporary_assignment: bool = Field(False, description="Supports time-based assignments")
    default_assignment_duration_days: Optional[int] = Field(None, description="Default assignment duration")


class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[int]] = None
    parent_roles: Optional[List[int]] = None
    requires_approval: Optional[bool] = None
    requires_mfa: Optional[bool] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    level: int
    is_system_role: bool
    can_be_delegated: bool
    requires_approval: bool
    requires_mfa: bool
    max_concurrent_users: Optional[int]
    supports_temporary_assignment: bool
    default_assignment_duration_days: Optional[int]
    compliance_level: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    permissions: List[PermissionResponse] = []
    parent_roles: List['RoleResponse'] = []
    child_roles: List['RoleResponse'] = []
    current_user_count: Optional[int] = None
    
    class Config:
        from_attributes = True


# User role assignment schemas
class UserRoleAssignmentBase(BaseModel):
    user_id: int
    role_id: int


class UserRoleAssignmentCreate(UserRoleAssignmentBase):
    assignment_reason: Optional[str] = Field(None, description="Reason for assignment")
    assignment_context: Optional[str] = Field(None, description="Context: promotion, project, etc.")
    is_temporary: bool = Field(False, description="Is this a temporary assignment")
    valid_until: Optional[datetime] = Field(None, description="Assignment expiration date")
    department_scope: Optional[str] = Field(None, description="Limit to specific department")
    project_scope: Optional[str] = Field(None, description="Limit to specific project")


class UserRoleAssignmentResponse(UserRoleAssignmentBase):
    id: int
    assigned_by_id: int
    assignment_reason: Optional[str]
    assignment_context: Optional[str]
    is_temporary: bool
    valid_from: datetime
    valid_until: Optional[datetime]
    department_scope: Optional[str]
    project_scope: Optional[str]
    status: str
    approval_required: bool
    approved_by_id: Optional[int]
    approved_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool
    created_at: datetime
    
    # Related objects
    role: RoleResponse
    assigned_by: Optional[Dict[str, Any]] = None
    approved_by: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# Role request schemas
class RoleRequestCreate(BaseModel):
    user_id: int
    role_id: int
    justification: str = Field(..., description="Justification for role request")
    business_need: Optional[str] = Field(None, description="Business need description")
    urgency: str = Field("normal", description="Request urgency: low, normal, high, critical")
    requested_duration_days: Optional[int] = Field(None, description="Requested assignment duration")


class RoleRequestResponse(BaseModel):
    id: int
    user_id: int
    role_id: int
    requested_by_id: int
    request_type: str
    justification: str
    business_need: Optional[str]
    urgency: str
    requested_duration_days: Optional[int]
    status: str
    approver_id: Optional[int]
    approval_decision: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    
    # Related objects
    user: Dict[str, Any]
    role: RoleResponse
    requested_by: Dict[str, Any]
    approver: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class RoleRequestApproval(BaseModel):
    request_id: int
    decision: str = Field(..., description="'approve' or 'reject'")
    approval_decision: Optional[str] = Field(None, description="Approval/rejection reasoning")
    assignment_duration_days: Optional[int] = Field(None, description="Override assignment duration")


# Permission grant schemas
class PermissionGrantCreate(BaseModel):
    user_id: int
    permission_id: int
    grant_reason: str = Field(..., description="Reason for granting permission")
    grant_context: Optional[str] = Field(None, description="Context: emergency, project, etc.")
    is_temporary: bool = Field(False, description="Is this a temporary grant")
    valid_until: Optional[datetime] = Field(None, description="Grant expiration date")
    resource_scope: Optional[Dict[str, Any]] = Field(None, description="Specific resources")


class PermissionGrantResponse(BaseModel):
    id: int
    user_id: int
    permission_id: int
    granted_by_id: int
    grant_reason: str
    grant_context: Optional[str]
    is_temporary: bool
    valid_from: datetime
    valid_until: Optional[datetime]
    resource_scope: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    
    # Related objects
    permission: PermissionResponse
    granted_by: Dict[str, Any]
    
    class Config:
        from_attributes = True


# Access control list schemas
class ACLCreate(BaseModel):
    resource_type: str = Field(..., description="Type of resource")
    resource_id: int = Field(..., description="ID of specific resource")
    subject_type: str = Field(..., description="'user', 'role', or 'group'")
    subject_id: int = Field(..., description="ID of user/role/group")
    permission_id: int = Field(..., description="Permission to grant")
    access_level: str = Field("read", description="Access level: read, write, admin")
    grant_reason: Optional[str] = Field(None, description="Reason for ACL entry")
    valid_until: Optional[datetime] = Field(None, description="ACL expiration date")


class ACLResponse(BaseModel):
    id: int
    resource_type: str
    resource_id: int
    subject_type: str
    subject_id: int
    permission_id: int
    access_level: str
    granted_by_id: int
    grant_reason: Optional[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    # Related objects
    permission: PermissionResponse
    granted_by: Dict[str, Any]
    
    class Config:
        from_attributes = True


# User permission and role status
class UserPermissionStatus(BaseModel):
    user_id: int
    permissions: Set[str] = Field(..., description="All permissions for user")
    roles: List[UserRoleAssignmentResponse] = Field(..., description="All role assignments")
    direct_grants: List[PermissionGrantResponse] = Field(..., description="Direct permission grants")
    pending_requests: List[RoleRequestResponse] = Field(..., description="Pending role requests")
    acl_entries: List[ACLResponse] = Field(..., description="Resource-specific ACL entries")


# Permission check schemas
class PermissionCheckRequest(BaseModel):
    permission: str = Field(..., description="Permission to check")
    resource_type: Optional[str] = Field(None, description="Type of resource")
    resource_id: Optional[int] = Field(None, description="ID of specific resource")


class PermissionCheckResponse(BaseModel):
    has_permission: bool
    permission: str
    source: str = Field(..., description="Source of permission: role, direct_grant, acl")
    role_name: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None


# Bulk operations schemas
class BulkRoleAssignment(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs")
    role_id: int = Field(..., description="Role to assign")
    assignment_reason: Optional[str] = Field(None, description="Reason for bulk assignment")
    is_temporary: bool = Field(False, description="Temporary assignment")
    valid_until: Optional[datetime] = Field(None, description="Assignment expiration")


class BulkRoleAssignmentResponse(BaseModel):
    total_users: int
    successful_assignments: int
    failed_assignments: int
    errors: List[Dict[str, str]] = Field([], description="Assignment errors")
    assignments: List[UserRoleAssignmentResponse] = Field(..., description="Created assignments")


class BulkPermissionGrant(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs")
    permission_id: int = Field(..., description="Permission to grant")
    grant_reason: str = Field(..., description="Reason for bulk grant")
    is_temporary: bool = Field(False, description="Temporary grant")
    valid_until: Optional[datetime] = Field(None, description="Grant expiration")


class BulkPermissionGrantResponse(BaseModel):
    total_users: int
    successful_grants: int
    failed_grants: int
    errors: List[Dict[str, str]] = Field([], description="Grant errors")
    grants: List[PermissionGrantResponse] = Field(..., description="Created grants")


# Analytics and reporting schemas
class RoleUsageStatistics(BaseModel):
    role_id: int
    role_name: str
    total_users: int
    active_users: int
    recent_usage_count: int
    average_session_duration: Optional[float]
    most_used_permissions: List[Dict[str, Any]]


class PermissionUsageStatistics(BaseModel):
    permission_id: int
    permission_name: str
    total_users_with_permission: int
    usage_count_last_30_days: int
    most_frequent_users: List[Dict[str, Any]]
    resource_usage_breakdown: Dict[str, int]


class RBACAnalytics(BaseModel):
    total_roles: int
    total_permissions: int
    total_active_assignments: int
    role_usage_stats: List[RoleUsageStatistics]
    permission_usage_stats: List[PermissionUsageStatistics]
    pending_requests_count: int
    temporary_assignments_count: int
    compliance_violations: List[Dict[str, Any]]


# Security and compliance schemas
class SecurityViolation(BaseModel):
    violation_type: str
    user_id: int
    role_id: Optional[int]
    permission_id: Optional[int]
    description: str
    severity: str
    detected_at: datetime
    resolved: bool = False


class ComplianceReport(BaseModel):
    report_date: datetime
    total_users_reviewed: int
    excessive_permissions_count: int
    stale_assignments_count: int
    missing_approvals_count: int
    violations: List[SecurityViolation]
    recommendations: List[str]


# Admin management schemas
class RoleCleanupRequest(BaseModel):
    remove_expired_assignments: bool = Field(True, description="Remove expired assignments")
    remove_unused_roles: bool = Field(False, description="Remove roles with no users")
    cleanup_stale_permissions: bool = Field(True, description="Clean up unused permissions")
    days_threshold: int = Field(90, description="Days to consider as stale")


class RoleCleanupResponse(BaseModel):
    assignments_removed: int
    roles_removed: int
    permissions_cleaned: int
    cleanup_summary: Dict[str, Any]