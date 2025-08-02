from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EvidenceTypeEnum(str, Enum):
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    CONFIGURATION = "configuration"
    POLICY = "policy"
    PROCEDURE = "procedure"
    CERTIFICATE = "certificate"
    SCAN_RESULT = "scan_result"
    REPORT = "report"
    OTHER = "other"


class EvidenceStatusEnum(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class EvidenceBase(BaseModel):
    title: str
    description: Optional[str] = None
    evidence_type: EvidenceTypeEnum
    category: Optional[str] = None
    subcategory: Optional[str] = None
    version: str = "1.0"
    owner_id: Optional[int] = None
    access_level: str = "private"
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    compliance_scope: Optional[str] = None  # JSON array
    tags: Optional[str] = None  # JSON array
    custom_fields: Optional[str] = None  # JSON object


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    evidence_type: Optional[EvidenceTypeEnum] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    owner_id: Optional[int] = None
    access_level: Optional[str] = None
    status: Optional[EvidenceStatusEnum] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    compliance_scope: Optional[str] = None
    review_comments: Optional[str] = None
    tags: Optional[str] = None
    custom_fields: Optional[str] = None
    is_active: Optional[bool] = None


class EvidenceResponse(EvidenceBase):
    id: int
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_hash: Optional[str] = None
    content_summary: Optional[str] = None
    ai_analysis: Optional[str] = None
    ai_confidence_score: Optional[int] = None
    ai_last_analyzed: Optional[datetime] = None
    previous_version_id: Optional[int] = None
    is_current_version: bool = True
    status: EvidenceStatusEnum
    uploaded_by_id: int
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_comments: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EvidenceControlBase(BaseModel):
    evidence_id: int
    control_id: int
    relationship_type: str = "supporting"
    relevance_score: Optional[int] = None
    description: Optional[str] = None


class EvidenceControlCreate(EvidenceControlBase):
    pass


class EvidenceControlResponse(EvidenceControlBase):
    id: int
    ai_relevance_analysis: Optional[str] = None
    ai_confidence_score: Optional[int] = None
    ai_last_analyzed: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class EvidenceUpload(BaseModel):
    title: str
    description: Optional[str] = None
    evidence_type: EvidenceTypeEnum
    category: Optional[str] = None
    tags: Optional[List[str]] = None