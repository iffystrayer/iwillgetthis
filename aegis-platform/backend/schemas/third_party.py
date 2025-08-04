from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for schema validation
class VendorStatusEnum(str, Enum):
    PROSPECT = "prospect"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"

class VendorTierEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class RiskLevelEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class AssessmentStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_UPDATE = "requires_update"

class ContractStatusEnum(str, Enum):
    DRAFT = "draft"
    UNDER_NEGOTIATION = "under_negotiation"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"

class MonitoringStatusEnum(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ALERT = "alert"
    CRITICAL = "critical"
    OFFLINE = "offline"

class ComplianceStatusEnum(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    PENDING_REVIEW = "pending_review"
    EXCEPTION_GRANTED = "exception_granted"

# Vendor Management Schemas

class VendorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    legal_name: Optional[str] = Field(None, max_length=500)
    business_name: Optional[str] = Field(None, max_length=500)
    vendor_type: Optional[str] = Field(None, max_length=100)
    primary_contact_name: Optional[str] = Field(None, max_length=255)
    primary_contact_email: Optional[str] = Field(None, max_length=255)
    primary_contact_phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=255)
    business_model: Optional[str] = Field(None, max_length=255)
    number_of_employees: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[float] = Field(None, ge=0)
    founding_year: Optional[int] = Field(None, ge=1800, le=2100)
    tier: VendorTierEnum = VendorTierEnum.LOW
    status: VendorStatusEnum = VendorStatusEnum.PROSPECT
    criticality: RiskLevelEnum = RiskLevelEnum.LOW
    services_provided: Optional[List[str]] = []
    service_categories: Optional[List[str]] = []
    data_types_accessed: Optional[List[str]] = []
    systems_accessed: Optional[List[str]] = []
    contract_value_annual: Optional[float] = Field(None, ge=0)
    contract_value_total: Optional[float] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=255)
    certifications: Optional[List[Dict[str, Any]]] = []
    compliance_frameworks: Optional[List[str]] = []
    security_attestations: Optional[List[Dict[str, Any]]] = []
    relationship_manager: Optional[str] = Field(None, max_length=255)
    vendor_account_manager: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = []

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    legal_name: Optional[str] = Field(None, max_length=500)
    business_name: Optional[str] = Field(None, max_length=500)
    vendor_type: Optional[str] = Field(None, max_length=100)
    tier: Optional[VendorTierEnum] = None
    status: Optional[VendorStatusEnum] = None
    criticality: Optional[RiskLevelEnum] = None
    contract_value_annual: Optional[float] = Field(None, ge=0)
    overall_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    relationship_manager: Optional[str] = Field(None, max_length=255)

class VendorResponse(VendorBase):
    id: int
    vendor_id: str
    overall_risk_score: float
    last_risk_assessment: Optional[datetime]
    next_assessment_due: Optional[datetime]
    onboarding_date: Optional[datetime]
    contract_start_date: Optional[datetime]
    contract_end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Risk Assessment Schemas

class VendorRiskAssessmentBase(BaseModel):
    assessment_name: str = Field(..., min_length=1, max_length=500)
    assessment_type: Optional[str] = Field(None, max_length=100)
    assessment_methodology: Optional[str] = Field(None, max_length=255)
    scope_description: Optional[str] = None
    due_date: Optional[datetime] = None
    information_security_score: float = Field(0.0, ge=0.0, le=100.0)
    data_protection_score: float = Field(0.0, ge=0.0, le=100.0)
    operational_risk_score: float = Field(0.0, ge=0.0, le=100.0)
    financial_risk_score: float = Field(0.0, ge=0.0, le=100.0)
    compliance_risk_score: float = Field(0.0, ge=0.0, le=100.0)
    business_continuity_score: float = Field(0.0, ge=0.0, le=100.0)
    reputational_risk_score: float = Field(0.0, ge=0.0, le=100.0)
    strengths: Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []
    gaps: Optional[List[str]] = []
    recommendations: Optional[List[str]] = []

class VendorRiskAssessmentCreate(VendorRiskAssessmentBase):
    vendor_id: int
    assessment_start_date: datetime = Field(default_factory=datetime.now)

class VendorRiskAssessmentUpdate(BaseModel):
    assessment_name: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[AssessmentStatusEnum] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    information_security_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    data_protection_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    operational_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    financial_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    compliance_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    business_continuity_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    reputational_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    overall_risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    overall_risk_level: Optional[RiskLevelEnum] = None
    completed_date: Optional[datetime] = None

class VendorRiskAssessmentResponse(VendorRiskAssessmentBase):
    id: int
    assessment_id: str
    vendor_id: int
    status: AssessmentStatusEnum
    progress_percentage: float
    overall_risk_score: float
    overall_risk_level: RiskLevelEnum
    previous_risk_score: Optional[float]
    risk_trend: Optional[str]
    assessment_start_date: datetime
    assessment_end_date: Optional[datetime]
    next_assessment_due: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Contract Management Schemas

class VendorContractBase(BaseModel):
    contract_name: str = Field(..., min_length=1, max_length=500)
    contract_type: Optional[str] = Field(None, max_length=100)
    contract_number: Optional[str] = Field(None, max_length=255)
    effective_date: datetime
    expiration_date: datetime
    auto_renewal: bool = False
    renewal_notice_days: int = Field(90, ge=0, le=365)
    termination_notice_days: int = Field(30, ge=0, le=365)
    contract_value: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", max_length=10)
    payment_terms: Optional[str] = Field(None, max_length=255)
    payment_schedule: Optional[str] = Field(None, max_length=100)
    liability_cap: Optional[float] = Field(None, ge=0)
    contract_owner: Optional[str] = Field(None, max_length=255)
    business_owner: Optional[str] = Field(None, max_length=255)
    legal_reviewer: Optional[str] = Field(None, max_length=255)

class VendorContractCreate(VendorContractBase):
    vendor_id: int

class VendorContractUpdate(BaseModel):
    contract_name: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[ContractStatusEnum] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    contract_value: Optional[float] = Field(None, ge=0)
    renewal_date: Optional[datetime] = None
    termination_date: Optional[datetime] = None
    termination_reason: Optional[str] = None

class VendorContractResponse(VendorContractBase):
    id: int
    contract_id: str
    vendor_id: int
    status: ContractStatusEnum
    renewal_date: Optional[datetime]
    termination_date: Optional[datetime]
    renewal_alerts_sent: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Monitoring Schemas

class VendorMonitoringBase(BaseModel):
    monitoring_type: str = Field(..., max_length=100)
    monitoring_frequency: str = Field(..., max_length=50)
    automated_monitoring: bool = True
    security_posture_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    service_availability: Optional[float] = Field(None, ge=0.0, le=100.0)
    response_time_ms: Optional[int] = Field(None, ge=0)
    compliance_status: ComplianceStatusEnum = ComplianceStatusEnum.PENDING_REVIEW
    financial_health_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    credit_rating: Optional[str] = Field(None, max_length=10)
    news_sentiment: Optional[float] = Field(None, ge=-1.0, le=1.0)

class VendorMonitoringCreate(VendorMonitoringBase):
    vendor_id: int

class VendorMonitoringUpdate(BaseModel):
    monitoring_frequency: Optional[str] = Field(None, max_length=50)
    automated_monitoring: Optional[bool] = None
    security_posture_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    service_availability: Optional[float] = Field(None, ge=0.0, le=100.0)
    compliance_status: Optional[ComplianceStatusEnum] = None
    financial_health_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    status: Optional[MonitoringStatusEnum] = None

class VendorMonitoringResponse(VendorMonitoringBase):
    id: int
    monitoring_id: str
    vendor_id: int
    status: MonitoringStatusEnum
    last_check_date: Optional[datetime]
    next_check_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Incident Management Schemas

class VendorIncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    incident_type: str = Field(..., max_length=100)
    severity: RiskLevelEnum
    business_impact: Optional[str] = Field(None, max_length=100)
    affected_users: Optional[int] = Field(None, ge=0)
    financial_impact: Optional[float] = Field(None, ge=0)
    regulatory_impact: bool = False
    discovered_date: datetime
    root_cause: Optional[str] = None
    incident_manager: Optional[str] = Field(None, max_length=255)
    priority: Optional[str] = Field(None, max_length=20)

class VendorIncidentCreate(VendorIncidentBase):
    vendor_id: int

class VendorIncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    severity: Optional[RiskLevelEnum] = None
    business_impact: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=100)
    resolved_date: Optional[datetime] = None
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None

class VendorIncidentResponse(VendorIncidentBase):
    id: int
    incident_id: str
    vendor_id: int
    reported_date: Optional[datetime]
    acknowledged_date: Optional[datetime]
    resolved_date: Optional[datetime]
    status: str
    resolution_summary: Optional[str]
    vendor_incident_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Action Items Schemas

class VendorActionItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    priority: RiskLevelEnum = RiskLevelEnum.MEDIUM
    assigned_to: Optional[str] = Field(None, max_length=255)
    vendor_contact: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    estimated_effort_hours: Optional[float] = Field(None, ge=0)
    implementation_plan: Optional[str] = None
    business_justification: Optional[str] = None
    cost_estimate: Optional[float] = Field(None, ge=0)

class VendorActionItemCreate(VendorActionItemBase):
    assessment_id: int

class VendorActionItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[RiskLevelEnum] = None
    assigned_to: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=100)
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    completed_date: Optional[datetime] = None

class VendorActionItemResponse(VendorActionItemBase):
    id: int
    action_id: str
    assessment_id: int
    status: str
    progress_percentage: float
    completed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Alert Schemas

class VendorAlertBase(BaseModel):
    alert_type: str = Field(..., max_length=100)
    severity: RiskLevelEnum
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    metric_name: Optional[str] = Field(None, max_length=255)
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None

class VendorAlertCreate(VendorAlertBase):
    monitoring_id: int

class VendorAlertUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=100)
    acknowledged_by: Optional[str] = Field(None, max_length=255)
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = Field(None, max_length=255)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

class VendorAlertResponse(VendorAlertBase):
    id: int
    alert_id: str
    monitoring_id: int
    status: str
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    escalation_level: int
    triggered_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# SLA Monitoring Schemas

class SLAMonitoringBase(BaseModel):
    sla_name: str = Field(..., min_length=1, max_length=255)
    sla_description: Optional[str] = None
    metric_name: str = Field(..., min_length=1, max_length=255)
    metric_unit: Optional[str] = Field(None, max_length=50)
    target_value: float
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    measurement_period: Optional[str] = Field(None, max_length=50)
    penalty_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    reporting_frequency: Optional[str] = Field(None, max_length=50)

class SLAMonitoringCreate(SLAMonitoringBase):
    contract_id: int

class SLAMonitoringUpdate(BaseModel):
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    current_value: Optional[float] = None
    status: Optional[str] = Field(None, max_length=100)

class SLAMonitoringResponse(SLAMonitoringBase):
    id: int
    sla_id: str
    contract_id: int
    current_value: Optional[float]
    breach_count: int
    last_breach_date: Optional[datetime]
    consecutive_breaches: int
    service_credits_earned: Optional[float]
    penalties_applied: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Supply Chain Schemas

class SupplyChainNodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    node_type: Optional[str] = Field(None, max_length=100)
    tier_level: int = Field(1, ge=1, le=10)
    criticality_level: RiskLevelEnum = RiskLevelEnum.LOW
    services_provided: Optional[List[str]] = []
    dependency_level: Optional[str] = Field(None, max_length=100)
    single_point_of_failure: bool = False
    replacement_time_days: Optional[int] = Field(None, ge=0)
    switching_cost: Optional[float] = Field(None, ge=0)
    visibility_level: Optional[str] = Field(None, max_length=100)

class SupplyChainNodeCreate(SupplyChainNodeBase):
    parent_node_id: Optional[int] = None
    primary_vendor_id: Optional[int] = None

class SupplyChainNodeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    node_type: Optional[str] = Field(None, max_length=100)
    tier_level: Optional[int] = Field(None, ge=1, le=10)
    criticality_level: Optional[RiskLevelEnum] = None
    dependency_level: Optional[str] = Field(None, max_length=100)
    operational_status: Optional[str] = Field(None, max_length=100)

class SupplyChainNodeResponse(SupplyChainNodeBase):
    id: int
    node_id: str
    parent_node_id: Optional[int]
    primary_vendor_id: Optional[int]
    inherent_risk_score: float
    residual_risk_score: float
    concentration_risk: float
    operational_status: str
    last_assessment_date: Optional[datetime]
    next_assessment_due: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Due Diligence Schemas

class VendorDueDiligenceBase(BaseModel):
    due_diligence_type: str = Field(..., max_length=100)
    scope_areas: Optional[List[str]] = []
    financial_statements_reviewed: bool = False
    credit_check_completed: bool = False
    financial_stability_rating: Optional[str] = Field(None, max_length=10)
    legal_entity_verification: bool = False
    regulatory_compliance_check: bool = False
    sanctions_screening: bool = False
    security_assessment_completed: bool = False
    privacy_assessment_completed: bool = False
    business_continuity_plan_reviewed: bool = False
    disaster_recovery_tested: bool = False
    reference_checks_completed: bool = False
    technology_stack_review: bool = False
    overall_rating: Optional[str] = Field(None, max_length=50)

class VendorDueDiligenceCreate(VendorDueDiligenceBase):
    vendor_id: int

class VendorDueDiligenceUpdate(BaseModel):
    financial_statements_reviewed: Optional[bool] = None
    credit_check_completed: Optional[bool] = None
    financial_stability_rating: Optional[str] = Field(None, max_length=10)
    security_assessment_completed: Optional[bool] = None
    privacy_assessment_completed: Optional[bool] = None
    overall_rating: Optional[str] = Field(None, max_length=50)
    reviewed_by: Optional[str] = Field(None, max_length=255)
    review_date: Optional[datetime] = None
    approved_by: Optional[str] = Field(None, max_length=255)
    approval_date: Optional[datetime] = None

class VendorDueDiligenceResponse(VendorDueDiligenceBase):
    id: int
    due_diligence_id: str
    vendor_id: int
    bankruptcy_risk_score: Optional[float]
    operational_resilience_score: Optional[float]
    industry_reputation_score: Optional[float]
    cybersecurity_maturity_level: Optional[str]
    reviewed_by: Optional[str]
    review_date: Optional[datetime]
    approved_by: Optional[str]
    approval_date: Optional[datetime]
    valid_until: Optional[datetime]
    renewal_required: bool
    next_review_due: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Dashboard and Analytics Schemas

class VendorRiskDashboard(BaseModel):
    total_vendors: int
    active_vendors: int
    critical_vendors: int
    high_risk_vendors: int
    overdue_assessments: int
    contract_renewals_due: int
    active_incidents: int
    sla_breaches: int
    average_risk_score: float
    risk_trend: str
    top_risk_categories: List[Dict[str, Any]]
    vendor_distribution: Dict[str, int]
    recent_assessments: List[Dict[str, Any]]
    upcoming_renewals: List[Dict[str, Any]]

class VendorPortfolioSummary(BaseModel):
    vendor_count: int
    total_contract_value: float
    average_contract_value: float
    vendors_by_tier: Dict[str, int]
    vendors_by_status: Dict[str, int]
    vendors_by_risk_level: Dict[str, int]
    top_spending_categories: List[Dict[str, Any]]
    geographic_distribution: Dict[str, int]
    certification_coverage: Dict[str, int]

# Search and Filter Schemas

class VendorSearchFilter(BaseModel):
    name: Optional[str] = None
    vendor_type: Optional[str] = None
    tier: Optional[VendorTierEnum] = None
    status: Optional[VendorStatusEnum] = None
    criticality: Optional[RiskLevelEnum] = None
    industry: Optional[str] = None
    risk_score_min: Optional[float] = Field(None, ge=0.0, le=100.0)
    risk_score_max: Optional[float] = Field(None, ge=0.0, le=100.0)
    contract_value_min: Optional[float] = Field(None, ge=0)
    contract_value_max: Optional[float] = Field(None, ge=0)
    assessment_overdue: Optional[bool] = None
    contract_expiring_days: Optional[int] = Field(None, ge=0, le=365)
    tags: Optional[List[str]] = []
    limit: Optional[int] = Field(50, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)

class AssessmentSearchFilter(BaseModel):
    vendor_id: Optional[int] = None
    assessment_type: Optional[str] = None
    status: Optional[AssessmentStatusEnum] = None
    risk_level: Optional[RiskLevelEnum] = None
    overdue_only: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: Optional[int] = Field(50, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)