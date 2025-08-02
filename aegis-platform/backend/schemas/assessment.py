from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssessmentStatusEnum(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ControlImplementationStatusEnum(str, Enum):
    IMPLEMENTED = "implemented"
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    NOT_APPLICABLE = "not_applicable"
    PLANNED = "planned"


class AssessmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    framework_id: int
    asset_id: Optional[int] = None
    scope_description: Optional[str] = None
    assessment_type: str = "control_assessment"
    methodology: Optional[str] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    lead_assessor_id: Optional[int] = None
    tags: Optional[str] = None  # JSON array
    custom_fields: Optional[str] = None  # JSON object


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scope_description: Optional[str] = None
    assessment_type: Optional[str] = None
    methodology: Optional[str] = None
    status: Optional[AssessmentStatusEnum] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    lead_assessor_id: Optional[int] = None
    overall_score: Optional[int] = None
    maturity_level: Optional[str] = None
    tags: Optional[str] = None
    custom_fields: Optional[str] = None
    is_active: Optional[bool] = None


class AssessmentResponse(AssessmentBase):
    id: int
    status: AssessmentStatusEnum
    actual_completion_date: Optional[datetime] = None
    created_by_id: int
    overall_score: Optional[int] = None
    maturity_level: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AssessmentControlBase(BaseModel):
    assessment_id: int
    control_id: int
    implementation_status: ControlImplementationStatusEnum
    implementation_score: Optional[int] = None
    effectiveness_rating: Optional[str] = None
    control_narrative: Optional[str] = None
    testing_procedures: Optional[str] = None
    evidence_summary: Optional[str] = None
    assessor_notes: Optional[str] = None
    testing_date: Optional[datetime] = None
    next_testing_date: Optional[datetime] = None


class AssessmentControlCreate(AssessmentControlBase):
    pass


class AssessmentControlUpdate(BaseModel):
    implementation_status: Optional[ControlImplementationStatusEnum] = None
    implementation_score: Optional[int] = None
    effectiveness_rating: Optional[str] = None
    control_narrative: Optional[str] = None
    testing_procedures: Optional[str] = None
    evidence_summary: Optional[str] = None
    assessor_notes: Optional[str] = None
    testing_date: Optional[datetime] = None
    next_testing_date: Optional[datetime] = None
    review_status: Optional[str] = None
    review_comments: Optional[str] = None


class AssessmentControlResponse(AssessmentControlBase):
    id: int
    ai_generated_narrative: Optional[str] = None
    ai_confidence_score: Optional[int] = None
    ai_last_updated: Optional[datetime] = None
    review_status: str = "pending"
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AssessmentSummary(BaseModel):
    total_controls: int
    implemented: int
    not_implemented: int
    partially_implemented: int
    not_applicable: int
    planned: int
    completion_percentage: float
    overall_score: Optional[int] = None
    maturity_level: Optional[str] = None