from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RiskCategoryEnum(str, Enum):
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"


class RiskStatusEnum(str, Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class RiskMatrixBase(BaseModel):
    name: str
    description: Optional[str] = None
    likelihood_levels: str  # JSON array
    impact_levels: str  # JSON array
    risk_scores: str  # JSON matrix
    risk_levels: str  # JSON mapping


class RiskMatrixCreate(RiskMatrixBase):
    pass


class RiskMatrixUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    likelihood_levels: Optional[str] = None
    impact_levels: Optional[str] = None
    risk_scores: Optional[str] = None
    risk_levels: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class RiskMatrixResponse(RiskMatrixBase):
    id: int
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RiskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: RiskCategoryEnum
    subcategory: Optional[str] = None
    risk_type: Optional[str] = None
    source: Optional[str] = None
    source_reference: Optional[str] = None
    asset_id: Optional[int] = None
    affected_systems: Optional[str] = None  # JSON array
    business_process: Optional[str] = None
    risk_matrix_id: Optional[int] = None
    inherent_likelihood: Optional[int] = None
    inherent_impact: Optional[int] = None
    threat_source: Optional[str] = None
    vulnerability: Optional[str] = None
    existing_controls: Optional[str] = None
    control_effectiveness: Optional[str] = None
    treatment_strategy: Optional[str] = None
    treatment_rationale: Optional[str] = None
    owner_id: Optional[int] = None
    target_resolution_date: Optional[datetime] = None
    tags: Optional[str] = None  # JSON array
    custom_fields: Optional[str] = None  # JSON object


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RiskCategoryEnum] = None
    subcategory: Optional[str] = None
    risk_type: Optional[str] = None
    source: Optional[str] = None
    source_reference: Optional[str] = None
    asset_id: Optional[int] = None
    affected_systems: Optional[str] = None
    business_process: Optional[str] = None
    risk_matrix_id: Optional[int] = None
    inherent_likelihood: Optional[int] = None
    inherent_impact: Optional[int] = None
    residual_likelihood: Optional[int] = None
    residual_impact: Optional[int] = None
    threat_source: Optional[str] = None
    vulnerability: Optional[str] = None
    existing_controls: Optional[str] = None
    control_effectiveness: Optional[str] = None
    treatment_strategy: Optional[str] = None
    treatment_rationale: Optional[str] = None
    status: Optional[RiskStatusEnum] = None
    owner_id: Optional[int] = None
    target_resolution_date: Optional[datetime] = None
    actual_resolution_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    tags: Optional[str] = None
    custom_fields: Optional[str] = None
    is_active: Optional[bool] = None


class RiskResponse(RiskBase):
    id: int
    inherent_risk_score: Optional[float] = None
    residual_likelihood: Optional[int] = None
    residual_impact: Optional[int] = None
    residual_risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    ai_generated_statement: Optional[str] = None
    ai_risk_assessment: Optional[str] = None
    ai_confidence_score: Optional[int] = None
    ai_last_updated: Optional[datetime] = None
    status: RiskStatusEnum
    identified_date: datetime
    actual_resolution_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class RiskScoreBase(BaseModel):
    risk_id: int
    likelihood_score: Optional[int] = None
    impact_score: Optional[int] = None
    total_score: Optional[float] = None
    risk_level: Optional[str] = None
    score_type: str  # inherent, residual
    likelihood_rationale: Optional[str] = None
    impact_rationale: Optional[str] = None
    scoring_methodology: Optional[str] = None


class RiskScoreCreate(RiskScoreBase):
    pass


class RiskScoreResponse(RiskScoreBase):
    id: int
    scored_by: Optional[int] = None
    scored_at: datetime
    
    class Config:
        from_attributes = True


class RiskSummary(BaseModel):
    total_risks: int
    by_status: dict
    by_category: dict
    by_risk_level: dict
    high_priority_count: int
    overdue_count: int