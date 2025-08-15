from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Enums matching the model enums
class WorkflowType(str, Enum):
    RISK_APPROVAL = "risk_approval"
    TASK_APPROVAL = "task_approval"
    ASSESSMENT_APPROVAL = "assessment_approval"
    EVIDENCE_APPROVAL = "evidence_approval"
    USER_ACCESS_REQUEST = "user_access_request"
    BUDGET_APPROVAL = "budget_approval"
    EXCEPTION_REQUEST = "exception_request"
    CUSTOM = "custom"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class WorkflowStepType(str, Enum):
    APPROVAL = "approval"
    REVIEW = "review"
    NOTIFICATION = "notification"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    AUTOMATED = "automated"


class WorkflowInstanceStatus(str, Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ERROR = "error"


class WorkflowStepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    REJECTED = "rejected"
    ERROR = "error"


class ActionType(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    COMMENT = "comment"
    REASSIGN = "reassign"
    ESCALATE = "escalate"
    REQUEST_INFORMATION = "request_information"
    CANCEL = "cancel"


# Base schemas
class WorkflowStepBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    step_type: WorkflowStepType
    step_order: int
    is_required: bool = True
    can_skip: bool = False
    allow_parallel: bool = False
    assignee_type: Optional[str] = Field(None, max_length=50)
    assignee_id: Optional[int] = None
    auto_assign_rule: Optional[Dict[str, Any]] = None
    approval_required: bool = True
    min_approvals: int = 1
    unanimous_required: bool = False
    timeout_hours: Optional[int] = None
    reminder_hours: int = 24
    escalation_assignee_id: Optional[int] = None
    condition_expression: Optional[Dict[str, Any]] = None
    allowed_actions: Optional[List[ActionType]] = None
    on_approve_action: Optional[Dict[str, Any]] = None
    on_reject_action: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class WorkflowStepCreate(WorkflowStepBase):
    workflow_id: int


class WorkflowStepUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    step_type: Optional[WorkflowStepType] = None
    step_order: Optional[int] = None
    is_required: Optional[bool] = None
    can_skip: Optional[bool] = None
    allow_parallel: Optional[bool] = None
    assignee_type: Optional[str] = Field(None, max_length=50)
    assignee_id: Optional[int] = None
    auto_assign_rule: Optional[Dict[str, Any]] = None
    approval_required: Optional[bool] = None
    min_approvals: Optional[int] = None
    unanimous_required: Optional[bool] = None
    timeout_hours: Optional[int] = None
    reminder_hours: Optional[int] = None
    escalation_assignee_id: Optional[int] = None
    condition_expression: Optional[Dict[str, Any]] = None
    allowed_actions: Optional[List[ActionType]] = None
    on_approve_action: Optional[Dict[str, Any]] = None
    on_reject_action: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class WorkflowStepResponse(WorkflowStepBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    workflow_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class WorkflowBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    workflow_type: WorkflowType
    category: Optional[str] = Field(None, max_length=100)
    version: str = Field("1.0", max_length=20)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    is_default: bool = False
    trigger_conditions: Optional[Dict[str, Any]] = None
    auto_trigger: bool = False
    default_timeout_hours: int = 72
    escalation_enabled: bool = True
    escalation_timeout_hours: int = 24
    notification_template_id: Optional[int] = None
    notify_on_start: bool = True
    notify_on_completion: bool = True
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class WorkflowCreate(WorkflowBase):
    steps: Optional[List[WorkflowStepBase]] = []


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    workflow_type: Optional[WorkflowType] = None
    category: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=20)
    status: Optional[WorkflowStatus] = None
    is_default: Optional[bool] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    auto_trigger: Optional[bool] = None
    default_timeout_hours: Optional[int] = None
    escalation_enabled: Optional[bool] = None
    escalation_timeout_hours: Optional[int] = None
    notification_template_id: Optional[int] = None
    notify_on_start: Optional[bool] = None
    notify_on_completion: Optional[bool] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_by_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    steps: List[WorkflowStepResponse] = []


# Workflow Instance schemas
class WorkflowInstanceBase(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    context_data: Optional[Dict[str, Any]] = None
    priority: str = Field("medium", max_length=20)
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class WorkflowInstanceCreate(WorkflowInstanceBase):
    workflow_id: int


class WorkflowInstanceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[WorkflowInstanceStatus] = None
    current_assignee_id: Optional[int] = None
    context_data: Optional[Dict[str, Any]] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, max_length=20)
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class WorkflowInstanceResponse(WorkflowInstanceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    workflow_id: int
    status: WorkflowInstanceStatus
    current_step_id: Optional[int] = None
    initiated_by_id: int
    current_assignee_id: Optional[int] = None
    initiated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    final_outcome: Optional[str] = None
    outcome_reason: Optional[str] = None
    escalation_level: int
    last_escalated_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Workflow Step Instance schemas
class WorkflowStepInstanceBase(BaseModel):
    step_order: int
    step_data: Optional[Dict[str, Any]] = None


class WorkflowStepInstanceCreate(WorkflowStepInstanceBase):
    workflow_instance_id: int
    workflow_step_id: int


class WorkflowStepInstanceUpdate(BaseModel):
    status: Optional[WorkflowStepStatus] = None
    assigned_to_id: Optional[int] = None
    outcome: Optional[str] = Field(None, max_length=50)
    outcome_reason: Optional[str] = None
    step_data: Optional[Dict[str, Any]] = None


class WorkflowStepInstanceResponse(WorkflowStepInstanceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    workflow_instance_id: int
    workflow_step_id: int
    status: WorkflowStepStatus
    assigned_to_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    outcome: Optional[str] = None
    outcome_reason: Optional[str] = None
    reminder_sent_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    escalated_to_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Workflow Action schemas
class WorkflowActionBase(BaseModel):
    action_type: ActionType
    action_description: Optional[str] = None
    comment: Optional[str] = None
    attachments: Optional[List[str]] = None


class WorkflowActionCreate(WorkflowActionBase):
    workflow_instance_id: int
    step_instance_id: Optional[int] = None
    on_behalf_of_id: Optional[int] = None


class WorkflowActionResponse(WorkflowActionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    workflow_instance_id: int
    step_instance_id: Optional[int] = None
    performed_by_id: int
    on_behalf_of_id: Optional[int] = None
    result_status: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    performed_at: datetime


# Workflow Template schemas
class WorkflowTemplateBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    workflow_type: Optional[WorkflowType] = None
    template_data: Dict[str, Any]
    version: str = Field("1.0", max_length=20)
    is_system_template: bool = False
    is_public: bool = True
    tags: Optional[List[str]] = None


class WorkflowTemplateCreate(WorkflowTemplateBase):
    pass


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    workflow_type: Optional[WorkflowType] = None
    template_data: Optional[Dict[str, Any]] = None
    version: Optional[str] = Field(None, max_length=20)
    is_system_template: Optional[bool] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    usage_count: int
    created_by_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Workflow Role schemas
class WorkflowRoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_system_role: bool = False
    permissions: Optional[List[str]] = None
    members: Optional[List[int]] = None


class WorkflowRoleCreate(WorkflowRoleBase):
    pass


class WorkflowRoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_system_role: Optional[bool] = None
    permissions: Optional[List[str]] = None
    members: Optional[List[int]] = None


class WorkflowRoleResponse(WorkflowRoleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Workflow execution request schemas
class WorkflowExecutionRequest(BaseModel):
    action_type: ActionType
    comment: Optional[str] = None
    attachments: Optional[List[str]] = None
    reassign_to_id: Optional[int] = None  # For reassignment actions
    escalate_to_id: Optional[int] = None  # For escalation actions


class WorkflowTriggerRequest(BaseModel):
    workflow_id: int
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    context_data: Optional[Dict[str, Any]] = None
    priority: str = Field("medium", max_length=20)
    custom_fields: Optional[Dict[str, Any]] = None


# Summary and dashboard schemas
class WorkflowSummary(BaseModel):
    total_workflows: int
    active_workflows: int
    pending_instances: int
    overdue_instances: int
    completed_today: int
    approval_rate: float
    average_completion_time_hours: float


class WorkflowDashboard(BaseModel):
    summary: WorkflowSummary
    my_pending_actions: List[WorkflowStepInstanceResponse]
    recent_workflows: List[WorkflowInstanceResponse]
    overdue_workflows: List[WorkflowInstanceResponse]


# Bulk operation schemas
class BulkWorkflowAction(BaseModel):
    workflow_instance_ids: List[int]
    action_type: ActionType
    comment: Optional[str] = None
    
    
class BulkWorkflowActionResult(BaseModel):
    success_count: int
    failure_count: int
    results: List[Dict[str, Any]]