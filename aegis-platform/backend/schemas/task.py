from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TaskStatusEnum(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskTypeEnum(str, Enum):
    REMEDIATION = "remediation"
    MITIGATION = "mitigation"
    ASSESSMENT = "assessment"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    COMPLIANCE = "compliance"
    OTHER = "other"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: TaskTypeEnum = TaskTypeEnum.REMEDIATION
    category: Optional[str] = None
    subcategory: Optional[str] = None
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    risk_id: Optional[int] = None
    asset_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    milestone_description: Optional[str] = None
    requires_approval: bool = False
    estimated_cost: Optional[str] = None
    cost_center: Optional[str] = None
    depends_on_tasks: Optional[str] = None  # JSON array
    blocks_tasks: Optional[str] = None  # JSON array
    tags: Optional[str] = None  # JSON array
    custom_fields: Optional[str] = None  # JSON object


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[TaskTypeEnum] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    priority: Optional[TaskPriorityEnum] = None
    status: Optional[TaskStatusEnum] = None
    assigned_to_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    progress_percentage: Optional[int] = None
    milestone_description: Optional[str] = None
    requires_approval: Optional[bool] = None
    approval_status: Optional[str] = None
    approval_comments: Optional[str] = None
    estimated_cost: Optional[str] = None
    actual_cost: Optional[str] = None
    cost_center: Optional[str] = None
    depends_on_tasks: Optional[str] = None
    blocks_tasks: Optional[str] = None
    tags: Optional[str] = None
    custom_fields: Optional[str] = None
    is_active: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    status: TaskStatusEnum
    completed_date: Optional[datetime] = None
    actual_hours: Optional[int] = None
    progress_percentage: int = 0
    ai_generated_plan: Optional[str] = None
    ai_suggested_actions: Optional[str] = None
    ai_confidence_score: Optional[int] = None
    ai_last_updated: Optional[datetime] = None
    approval_status: Optional[str] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_comments: Optional[str] = None
    actual_cost: Optional[str] = None
    created_by_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskCommentBase(BaseModel):
    task_id: int
    comment: str
    comment_type: str = "general"
    is_internal: bool = False


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskCommentResponse(TaskCommentBase):
    id: int
    user_id: int
    is_system_generated: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskEvidenceBase(BaseModel):
    task_id: int
    evidence_id: int
    relationship_type: str = "supporting"
    description: Optional[str] = None


class TaskEvidenceCreate(TaskEvidenceBase):
    pass


class TaskEvidenceResponse(TaskEvidenceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskSummary(BaseModel):
    total_tasks: int
    by_status: dict
    by_priority: dict
    overdue_count: int
    my_open_tasks: int
    awaiting_review_count: int