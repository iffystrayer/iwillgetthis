"""
Pydantic schemas for Risk Register system
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class RiskCategoryEnum(str, Enum):
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    TECHNOLOGY = "technology"
    REPUTATIONAL = "reputational"
    ENVIRONMENTAL = "environmental"
    SECURITY = "security"
    LEGAL = "legal"
    SUPPLIER = "supplier"


class RiskStatusEnum(str, Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    TREATING = "treating"
    MONITORING = "monitoring"
    CLOSED = "closed"
    ESCALATED = "escalated"


class RiskLikelihoodEnum(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CERTAIN = "certain"


class RiskImpactEnum(str, Enum):
    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"


class RiskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TreatmentStrategyEnum(str, Enum):
    AVOID = "avoid"
    MITIGATE = "mitigate"
    TRANSFER = "transfer"
    ACCEPT = "accept"
    EXPLOIT = "exploit"


class TreatmentStatusEnum(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


# Base Schemas
class RiskRegisterBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category: RiskCategoryEnum
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = []
    
    # Risk Assessment
    inherent_likelihood: RiskLikelihoodEnum
    inherent_impact: RiskImpactEnum
    
    # Business Context
    business_unit: Optional[str] = None
    process_area: Optional[str] = None
    geographic_scope: Optional[str] = None
    
    # Financial Impact
    potential_financial_impact_min: Optional[float] = Field(None, ge=0)
    potential_financial_impact_max: Optional[float] = Field(None, ge=0)
    currency: str = "USD"
    
    # Timeline
    risk_horizon: Optional[str] = None
    first_identified_date: datetime
    next_review_date: Optional[datetime] = None
    
    # Ownership
    risk_owner_id: int
    risk_manager_id: Optional[int] = None
    escalation_contact_id: Optional[int] = None
    
    # Regulatory and Compliance
    regulatory_requirements: Optional[List[str]] = []
    compliance_impact: Optional[str] = None
    
    # External Factors
    external_dependencies: Optional[List[str]] = []
    market_conditions_impact: Optional[str] = None
    
    # Custom Fields
    custom_fields: Optional[Dict[str, Any]] = {}
    
    @validator('potential_financial_impact_max')
    def validate_financial_impact_max(cls, v, values):
        if v is not None and 'potential_financial_impact_min' in values:
            min_val = values['potential_financial_impact_min']
            if min_val is not None and v < min_val:
                raise ValueError('Maximum financial impact must be greater than or equal to minimum')
        return v


class RiskRegisterCreate(RiskRegisterBase):
    pass


class RiskRegisterUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[RiskCategoryEnum] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    
    inherent_likelihood: Optional[RiskLikelihoodEnum] = None
    inherent_impact: Optional[RiskImpactEnum] = None
    residual_likelihood: Optional[RiskLikelihoodEnum] = None
    residual_impact: Optional[RiskImpactEnum] = None
    
    business_unit: Optional[str] = None
    process_area: Optional[str] = None
    geographic_scope: Optional[str] = None
    
    potential_financial_impact_min: Optional[float] = Field(None, ge=0)
    potential_financial_impact_max: Optional[float] = Field(None, ge=0)
    
    risk_horizon: Optional[str] = None
    next_review_date: Optional[datetime] = None
    
    risk_owner_id: Optional[int] = None
    risk_manager_id: Optional[int] = None
    escalation_contact_id: Optional[int] = None
    
    status: Optional[RiskStatusEnum] = None
    
    regulatory_requirements: Optional[List[str]] = None
    compliance_impact: Optional[str] = None
    external_dependencies: Optional[List[str]] = None
    market_conditions_impact: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class UserSummary(BaseModel):
    """Lightweight user summary for risk display"""
    id: int
    email: str
    full_name: Optional[str] = None


class RiskRegisterResponse(RiskRegisterBase):
    id: int
    risk_id: str
    
    # Calculated scores
    inherent_score: Optional[float] = None
    inherent_priority: Optional[RiskPriorityEnum] = None
    residual_likelihood: Optional[RiskLikelihoodEnum] = None
    residual_impact: Optional[RiskImpactEnum] = None
    residual_score: Optional[float] = None
    residual_priority: Optional[RiskPriorityEnum] = None
    
    # Status
    status: RiskStatusEnum
    is_active: bool
    
    # Dates
    last_review_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # User relationships
    risk_owner: Optional[UserSummary] = None
    risk_manager: Optional[UserSummary] = None
    escalation_contact: Optional[UserSummary] = None
    
    # Counts
    treatment_count: Optional[int] = 0
    control_count: Optional[int] = 0
    incident_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Risk Treatment Schemas
class RiskTreatmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    strategy: TreatmentStrategyEnum
    
    action_plan: Optional[str] = None
    success_criteria: Optional[str] = None
    resource_requirements: Optional[str] = None
    
    planned_start_date: Optional[datetime] = None
    planned_completion_date: Optional[datetime] = None
    
    estimated_cost: Optional[float] = Field(None, ge=0)
    currency: str = "USD"
    budget_approval_required: bool = False
    
    treatment_owner_id: int
    assigned_team: Optional[List[int]] = []
    
    expected_likelihood_reduction: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_impact_reduction: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    dependencies: Optional[List[str]] = []
    constraints: Optional[str] = None
    monitoring_plan: Optional[str] = None
    kpis: Optional[List[Dict[str, Any]]] = []


class RiskTreatmentCreate(RiskTreatmentBase):
    risk_id: int


class RiskTreatmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    strategy: Optional[TreatmentStrategyEnum] = None
    
    action_plan: Optional[str] = None
    success_criteria: Optional[str] = None
    resource_requirements: Optional[str] = None
    
    planned_start_date: Optional[datetime] = None
    planned_completion_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    budget_approved: Optional[bool] = None
    
    treatment_owner_id: Optional[int] = None
    assigned_team: Optional[List[int]] = None
    
    status: Optional[TreatmentStatusEnum] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    expected_likelihood_reduction: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_impact_reduction: Optional[float] = Field(None, ge=0.0, le=1.0)
    actual_likelihood_reduction: Optional[float] = Field(None, ge=0.0, le=1.0)
    actual_impact_reduction: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    dependencies: Optional[List[str]] = None
    constraints: Optional[str] = None
    monitoring_plan: Optional[str] = None
    kpis: Optional[List[Dict[str, Any]]] = None


class RiskTreatmentResponse(RiskTreatmentBase):
    id: int
    treatment_id: str
    risk_id: int
    
    actual_start_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    actual_cost: Optional[float] = None
    budget_approved: bool = False
    
    status: TreatmentStatusEnum
    progress_percentage: int = 0
    
    actual_likelihood_reduction: Optional[float] = None
    actual_impact_reduction: Optional[float] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    treatment_owner: Optional[UserSummary] = None
    milestone_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Risk Assessment Schemas
class RiskAssessmentBase(BaseModel):
    assessment_type: str = Field(..., min_length=1)
    assessment_date: datetime
    
    methodology_used: Optional[str] = None
    assessment_criteria: Optional[str] = None
    data_sources: Optional[List[str]] = []
    
    likelihood_rating: RiskLikelihoodEnum
    likelihood_rationale: str = Field(..., min_length=1)
    likelihood_confidence: Optional[str] = "medium"
    
    impact_rating: RiskImpactEnum
    impact_rationale: str = Field(..., min_length=1)
    impact_confidence: Optional[str] = "medium"
    
    financial_impact: Optional[float] = Field(None, ge=0)
    operational_impact: Optional[str] = None
    reputational_impact: Optional[str] = None
    compliance_impact: Optional[str] = None
    strategic_impact: Optional[str] = None
    
    assessment_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_comments: Optional[str] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    risk_id: int


class RiskAssessmentUpdate(BaseModel):
    assessment_type: Optional[str] = None
    methodology_used: Optional[str] = None
    assessment_criteria: Optional[str] = None
    data_sources: Optional[List[str]] = None
    
    likelihood_rating: Optional[RiskLikelihoodEnum] = None
    likelihood_rationale: Optional[str] = None
    likelihood_confidence: Optional[str] = None
    
    impact_rating: Optional[RiskImpactEnum] = None
    impact_rationale: Optional[str] = None
    impact_confidence: Optional[str] = None
    
    financial_impact: Optional[float] = Field(None, ge=0)
    operational_impact: Optional[str] = None
    reputational_impact: Optional[str] = None
    compliance_impact: Optional[str] = None
    strategic_impact: Optional[str] = None
    
    is_validated: Optional[bool] = None
    validation_notes: Optional[str] = None
    assessment_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_comments: Optional[str] = None


class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    assessment_id: str
    risk_id: int
    
    overall_score: Optional[float] = None
    priority_rating: Optional[RiskPriorityEnum] = None
    
    is_validated: bool = False
    validated_by_id: Optional[int] = None
    validation_date: Optional[datetime] = None
    validation_notes: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    assessor: Optional[UserSummary] = None
    validator: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Risk Control Schemas
class RiskControlBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    control_type: str = Field(..., min_length=1)
    
    implementation_status: Optional[str] = "planned"
    control_owner_id: int
    
    design_effectiveness: Optional[str] = None
    operational_effectiveness: Optional[str] = None
    next_testing_date: Optional[datetime] = None
    
    is_automated: bool = False
    frequency: Optional[str] = None
    
    implementation_cost: Optional[float] = Field(None, ge=0)
    ongoing_cost: Optional[float] = Field(None, ge=0)
    resource_requirements: Optional[str] = None
    
    monitoring_procedures: Optional[str] = None
    performance_metrics: Optional[List[Dict[str, Any]]] = []


class RiskControlCreate(RiskControlBase):
    risk_id: int


class RiskControlUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    control_type: Optional[str] = None
    
    implementation_status: Optional[str] = None
    control_owner_id: Optional[int] = None
    
    design_effectiveness: Optional[str] = None
    operational_effectiveness: Optional[str] = None
    last_testing_date: Optional[datetime] = None
    next_testing_date: Optional[datetime] = None
    
    is_automated: Optional[bool] = None
    frequency: Optional[str] = None
    
    implementation_cost: Optional[float] = Field(None, ge=0)
    ongoing_cost: Optional[float] = Field(None, ge=0)
    resource_requirements: Optional[str] = None
    
    monitoring_procedures: Optional[str] = None
    performance_metrics: Optional[List[Dict[str, Any]]] = None


class RiskControlResponse(RiskControlBase):
    id: int
    control_id: str
    risk_id: int
    
    last_testing_date: Optional[datetime] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    control_owner: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Risk Dashboard and Analytics
class RiskDashboardData(BaseModel):
    """Risk dashboard summary data"""
    total_risks: int
    risks_by_status: Dict[str, int]
    risks_by_priority: Dict[str, int]
    risks_by_category: Dict[str, int]
    
    overdue_treatments: int
    upcoming_reviews: int
    recent_incidents: int
    
    risk_trend: Dict[str, Any]  # Risk trend over time
    treatment_effectiveness: Dict[str, Any]
    top_risks: List[Dict[str, Any]]


class RiskHeatmapData(BaseModel):
    """Risk heatmap visualization data"""
    matrix_data: List[List[Dict[str, Any]]]  # 2D grid of risks
    likelihood_labels: List[str]
    impact_labels: List[str]
    risk_counts: Dict[str, int]


class RiskReportFilter(BaseModel):
    """Filters for risk reports"""
    categories: Optional[List[RiskCategoryEnum]] = None
    statuses: Optional[List[RiskStatusEnum]] = None
    priorities: Optional[List[RiskPriorityEnum]] = None
    business_units: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    risk_owner_ids: Optional[List[int]] = None
    include_closed: bool = False


class BulkRiskOperation(BaseModel):
    """Bulk operations on risks"""
    operation: str  # update_status, assign_owner, bulk_review, etc.
    risk_ids: List[int]
    operation_data: Dict[str, Any]


class BulkRiskOperationResponse(BaseModel):
    """Response for bulk risk operations"""
    success: bool
    operation: str
    processed_count: int
    success_count: int
    error_count: int
    errors: List[str] = []
    updated_risks: List[int] = []