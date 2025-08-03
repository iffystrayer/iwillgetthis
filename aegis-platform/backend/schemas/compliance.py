"""
Pydantic schemas for Compliance Management system
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ComplianceFrameworkEnum(str, Enum):
    SOX = "sox"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST_800_53 = "nist_800_53"
    NIST_CSF = "nist_csf"
    CIS_CONTROLS = "cis_controls"
    COBIT = "cobit"
    FFIEC = "ffiec"
    FISMA = "fisma"
    FedRAMP = "fedramp"
    SOC_2 = "soc_2"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    CUSTOM = "custom"


class ComplianceStatusEnum(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"
    IN_PROGRESS = "in_progress"
    REQUIRES_REVIEW = "requires_review"
    EXEMPTED = "exempted"
    NOT_APPLICABLE = "not_applicable"


class ControlTypeEnum(str, Enum):
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATING = "compensating"
    DIRECTIVE = "directive"
    ADMINISTRATIVE = "administrative"
    TECHNICAL = "technical"
    PHYSICAL = "physical"


class TestingFrequencyEnum(str, Enum):
    CONTINUOUS = "continuous"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    AD_HOC = "ad_hoc"


class EvidenceTypeEnum(str, Enum):
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    CONFIGURATION = "configuration"
    AUDIT_REPORT = "audit_report"
    TEST_RESULT = "test_result"
    CERTIFICATE = "certificate"
    POLICY = "policy"
    PROCEDURE = "procedure"
    INTERVIEW = "interview"
    OBSERVATION = "observation"


# Base Schemas
class UserSummary(BaseModel):
    """Lightweight user summary for compliance display"""
    id: int
    email: str
    full_name: Optional[str] = None


# Framework Schemas
class ComplianceFrameworkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    framework_type: ComplianceFrameworkEnum
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=50)
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    
    authority: Optional[str] = Field(None, max_length=200)
    scope: Optional[str] = None
    industry_focus: Optional[str] = Field(None, max_length=100)
    geographic_scope: Optional[str] = Field(None, max_length=100)
    
    control_families: Optional[Dict[str, str]] = {}
    framework_hierarchy: Optional[Dict[str, Any]] = {}
    
    active: bool = True
    mandatory: bool = False
    custom_framework: bool = False
    
    automated_assessment: bool = False
    assessment_frequency: TestingFrequencyEnum = TestingFrequencyEnum.QUARTERLY


class ComplianceFrameworkCreate(ComplianceFrameworkBase):
    pass


class ComplianceFrameworkUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    framework_type: Optional[ComplianceFrameworkEnum] = None
    description: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    
    authority: Optional[str] = None
    scope: Optional[str] = None
    industry_focus: Optional[str] = None
    geographic_scope: Optional[str] = None
    
    control_families: Optional[Dict[str, str]] = None
    framework_hierarchy: Optional[Dict[str, Any]] = None
    
    active: Optional[bool] = None
    mandatory: Optional[bool] = None
    
    automated_assessment: Optional[bool] = None
    assessment_frequency: Optional[TestingFrequencyEnum] = None


class ComplianceFrameworkResponse(ComplianceFrameworkBase):
    id: int
    framework_id: str
    total_controls: int = 0
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator: Optional[UserSummary] = None
    
    # Aggregated data
    assessment_count: Optional[int] = 0
    last_assessment_date: Optional[datetime] = None
    overall_compliance_score: Optional[float] = None
    
    class Config:
        from_attributes = True


# Control Schemas
class ComplianceControlBase(BaseModel):
    control_id: str = Field(..., min_length=1, max_length=100)
    control_number: Optional[str] = Field(None, max_length=50)
    control_family: Optional[str] = Field(None, max_length=100)
    control_title: str = Field(..., min_length=1, max_length=500)
    control_objective: Optional[str] = None
    
    description: str = Field(..., min_length=1)
    implementation_guidance: Optional[str] = None
    assessment_procedures: Optional[str] = None
    
    control_type: ControlTypeEnum
    control_class: Optional[str] = Field(None, max_length=50)
    priority: str = Field("medium", regex="^(low|medium|high|critical)$")
    
    baseline_impact: Optional[str] = Field(None, regex="^(low|moderate|high)$")
    privacy_control: bool = False
    security_control: bool = True
    operational_control: bool = False
    
    implementation_status: ComplianceStatusEnum = ComplianceStatusEnum.NOT_ASSESSED
    implementation_notes: Optional[str] = None
    compensating_controls: Optional[List[str]] = []
    
    testing_frequency: TestingFrequencyEnum = TestingFrequencyEnum.ANNUALLY
    testing_methodology: Optional[str] = None
    
    automated_testing: bool = False
    automation_tool: Optional[str] = Field(None, max_length=100)
    automation_script: Optional[str] = None
    
    parent_control_id: Optional[int] = None
    dependent_controls: Optional[List[str]] = []
    related_controls: Optional[List[str]] = []
    
    active: bool = True


class ComplianceControlCreate(ComplianceControlBase):
    framework_id: int


class ComplianceControlUpdate(BaseModel):
    control_title: Optional[str] = Field(None, min_length=1, max_length=500)
    control_objective: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1)
    implementation_guidance: Optional[str] = None
    assessment_procedures: Optional[str] = None
    
    control_type: Optional[ControlTypeEnum] = None
    control_class: Optional[str] = None
    priority: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
    
    implementation_status: Optional[ComplianceStatusEnum] = None
    implementation_notes: Optional[str] = None
    compensating_controls: Optional[List[str]] = None
    
    testing_frequency: Optional[TestingFrequencyEnum] = None
    testing_methodology: Optional[str] = None
    last_test_date: Optional[datetime] = None
    next_test_date: Optional[datetime] = None
    
    automated_testing: Optional[bool] = None
    automation_tool: Optional[str] = None
    automation_script: Optional[str] = None
    
    dependent_controls: Optional[List[str]] = None
    related_controls: Optional[List[str]] = None
    
    active: Optional[bool] = None


class ComplianceControlResponse(ComplianceControlBase):
    id: int
    framework_id: int
    
    last_test_date: Optional[datetime] = None
    next_test_date: Optional[datetime] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    framework: Optional[Dict[str, Any]] = None
    parent_control: Optional[Dict[str, Any]] = None
    assessment_count: Optional[int] = 0
    last_assessment_score: Optional[float] = None
    finding_count: Optional[int] = 0
    evidence_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Assessment Schemas
class ComplianceAssessmentBase(BaseModel):
    assessment_name: str = Field(..., min_length=1, max_length=300)
    assessment_type: str = Field("internal", max_length=50)
    assessment_scope: Optional[str] = None
    
    start_date: datetime
    end_date: Optional[datetime] = None
    planned_completion_date: Optional[datetime] = None
    
    assessment_team: Optional[List[int]] = []
    external_auditor: Optional[str] = Field(None, max_length=200)
    
    assessment_methodology: Optional[str] = None
    assessment_criteria: Optional[str] = None


class ComplianceAssessmentCreate(ComplianceAssessmentBase):
    framework_id: int
    lead_assessor: int


class ComplianceAssessmentUpdate(BaseModel):
    assessment_name: Optional[str] = Field(None, min_length=1, max_length=300)
    assessment_scope: Optional[str] = None
    
    end_date: Optional[datetime] = None
    planned_completion_date: Optional[datetime] = None
    
    status: Optional[str] = Field(None, max_length=50)
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    assessment_team: Optional[List[int]] = None
    external_auditor: Optional[str] = None
    
    overall_compliance_score: Optional[float] = Field(None, ge=0, le=10)
    executive_summary: Optional[str] = None
    detailed_report_path: Optional[str] = Field(None, max_length=500)


class ComplianceAssessmentResponse(ComplianceAssessmentBase):
    id: int
    assessment_id: str
    framework_id: int
    
    status: str = "planned"
    progress_percentage: int = 0
    
    # Results summary
    overall_compliance_score: Optional[float] = None
    compliant_controls: int = 0
    non_compliant_controls: int = 0
    partially_compliant_controls: int = 0
    not_assessed_controls: int = 0
    
    # Findings summary
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    
    executive_summary: Optional[str] = None
    detailed_report_path: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    framework: Optional[Dict[str, Any]] = None
    lead_assessor: Optional[UserSummary] = None
    team_members: Optional[List[UserSummary]] = []
    
    class Config:
        from_attributes = True


# Control Assessment Schemas
class ControlAssessmentBase(BaseModel):
    assessment_date: datetime
    assessment_method: str = Field(..., max_length=100)
    
    compliance_status: ComplianceStatusEnum
    effectiveness_rating: str = Field(..., regex="^(effective|partially_effective|ineffective)$")
    confidence_level: str = Field("medium", regex="^(low|medium|high)$")
    
    compliance_score: Optional[float] = Field(None, ge=0, le=10)
    maturity_level: Optional[int] = Field(None, ge=1, le=5)
    implementation_percentage: Optional[float] = Field(None, ge=0, le=100)
    
    testing_performed: Optional[str] = None
    evidence_reviewed: Optional[str] = None
    assessment_notes: Optional[str] = None
    limitations: Optional[str] = None
    
    deficiencies_identified: Optional[str] = None
    compensating_controls_evaluated: Optional[str] = None
    recommendations: Optional[str] = None
    
    requires_follow_up: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None


class ControlAssessmentCreate(ControlAssessmentBase):
    assessment_id: int
    control_id: int
    assessor: Optional[int] = None


class ControlAssessmentUpdate(BaseModel):
    compliance_status: Optional[ComplianceStatusEnum] = None
    effectiveness_rating: Optional[str] = Field(None, regex="^(effective|partially_effective|ineffective)$")
    confidence_level: Optional[str] = Field(None, regex="^(low|medium|high)$")
    
    compliance_score: Optional[float] = Field(None, ge=0, le=10)
    maturity_level: Optional[int] = Field(None, ge=1, le=5)
    implementation_percentage: Optional[float] = Field(None, ge=0, le=100)
    
    testing_performed: Optional[str] = None
    evidence_reviewed: Optional[str] = None
    assessment_notes: Optional[str] = None
    limitations: Optional[str] = None
    
    deficiencies_identified: Optional[str] = None
    recommendations: Optional[str] = None
    
    requires_follow_up: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None


class ControlAssessmentResponse(ControlAssessmentBase):
    id: int
    assessment_id: int
    control_id: int
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    assessment: Optional[Dict[str, Any]] = None
    control: Optional[Dict[str, Any]] = None
    assessor: Optional[UserSummary] = None
    evidence_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Finding Schemas
class ComplianceFindingBase(BaseModel):
    finding_title: str = Field(..., min_length=1, max_length=500)
    finding_description: str = Field(..., min_length=1)
    finding_type: str = Field(..., max_length=50)
    
    severity: str = Field(..., regex="^(critical|high|medium|low)$")
    risk_level: Optional[str] = Field(None, regex="^(critical|high|medium|low)$")
    business_impact: Optional[str] = None
    compliance_impact: Optional[str] = None
    
    root_cause: Optional[str] = None
    contributing_factors: Optional[List[str]] = []
    
    remediation_plan: Optional[str] = None
    remediation_deadline: Optional[datetime] = None
    
    validation_required: bool = True
    validation_method: Optional[str] = Field(None, max_length=100)
    
    related_findings: Optional[List[str]] = []
    external_references: Optional[List[str]] = []


class ComplianceFindingCreate(ComplianceFindingBase):
    assessment_id: int
    control_id: Optional[int] = None
    remediation_owner: Optional[int] = None


class ComplianceFindingUpdate(BaseModel):
    finding_title: Optional[str] = Field(None, min_length=1, max_length=500)
    finding_description: Optional[str] = Field(None, min_length=1)
    finding_type: Optional[str] = None
    
    severity: Optional[str] = Field(None, regex="^(critical|high|medium|low)$")
    risk_level: Optional[str] = None
    business_impact: Optional[str] = None
    compliance_impact: Optional[str] = None
    
    root_cause: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    
    remediation_plan: Optional[str] = None
    remediation_owner: Optional[int] = None
    remediation_deadline: Optional[datetime] = None
    remediation_status: Optional[str] = Field(None, max_length=50)
    remediation_notes: Optional[str] = None
    
    status: Optional[str] = Field(None, max_length=50)
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    validated_date: Optional[datetime] = None
    validated_by: Optional[int] = None


class ComplianceFindingResponse(ComplianceFindingBase):
    id: int
    finding_id: str
    assessment_id: int
    control_id: Optional[int] = None
    
    remediation_status: str = "open"
    remediation_notes: Optional[str] = None
    
    status: str = "open"
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    validated_date: Optional[datetime] = None
    
    identified_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    assessment: Optional[Dict[str, Any]] = None
    control: Optional[Dict[str, Any]] = None
    remediation_owner: Optional[UserSummary] = None
    validator: Optional[UserSummary] = None
    evidence_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Evidence Schemas
class ComplianceEvidenceBase(BaseModel):
    evidence_name: str = Field(..., min_length=1, max_length=300)
    evidence_type: EvidenceTypeEnum
    description: Optional[str] = None
    
    file_path: Optional[str] = Field(None, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)
    
    collection_date: datetime
    collection_method: Optional[str] = Field(None, max_length=100)
    
    validated: bool = False
    validation_date: Optional[datetime] = None
    validation_notes: Optional[str] = None
    
    confidentiality_level: str = Field("internal", regex="^(public|internal|confidential|restricted)$")
    retention_period_days: int = Field(2555, gt=0)  # 7 years default
    
    active: bool = True


class ComplianceEvidenceCreate(ComplianceEvidenceBase):
    control_assessment_id: Optional[int] = None
    control_id: Optional[int] = None
    finding_id: Optional[int] = None
    collected_by: int


class ComplianceEvidenceUpdate(BaseModel):
    evidence_name: Optional[str] = Field(None, min_length=1, max_length=300)
    evidence_type: Optional[EvidenceTypeEnum] = None
    description: Optional[str] = None
    
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    
    validated: Optional[bool] = None
    validation_date: Optional[datetime] = None
    validation_notes: Optional[str] = None
    
    confidentiality_level: Optional[str] = Field(None, regex="^(public|internal|confidential|restricted)$")
    retention_period_days: Optional[int] = Field(None, gt=0)
    
    active: Optional[bool] = None


class ComplianceEvidenceResponse(ComplianceEvidenceBase):
    id: int
    evidence_id: str
    
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    
    custody_log: Optional[List[Dict[str, Any]]] = []
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    control_assessment: Optional[Dict[str, Any]] = None
    control: Optional[Dict[str, Any]] = None
    finding: Optional[Dict[str, Any]] = None
    collector: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Dashboard and Analytics Schemas
class ComplianceDashboardData(BaseModel):
    """Compliance dashboard summary data"""
    total_frameworks: int
    active_assessments: int
    total_controls: int
    total_findings: int
    
    frameworks_by_status: Dict[str, int]
    controls_by_status: Dict[str, int]
    findings_by_severity: Dict[str, int]
    assessments_by_status: Dict[str, int]
    
    overdue_assessments: int
    overdue_remediations: int
    compliance_trend: Dict[str, Any]
    
    top_frameworks_by_score: List[Dict[str, Any]]
    recent_assessments: List[Dict[str, Any]]
    critical_findings: List[Dict[str, Any]]


class ComplianceMetricsData(BaseModel):
    """Compliance metrics and KPIs"""
    framework_id: Optional[int] = None
    measurement_period: Dict[str, datetime]
    
    overall_compliance_percentage: float
    average_maturity_level: float
    control_effectiveness_percentage: float
    
    compliance_by_framework: Dict[str, float]
    compliance_by_control_family: Dict[str, float]
    maturity_by_control_family: Dict[str, float]
    
    remediation_metrics: Dict[str, Any]
    assessment_metrics: Dict[str, Any]
    trend_analysis: Dict[str, Any]


class ComplianceReportFilter(BaseModel):
    """Filters for compliance reports"""
    frameworks: Optional[List[int]] = None
    control_families: Optional[List[str]] = None
    compliance_statuses: Optional[List[ComplianceStatusEnum]] = None
    severities: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_findings: bool = True
    include_evidence: bool = False
    maturity_level_min: Optional[int] = Field(None, ge=1, le=5)
    maturity_level_max: Optional[int] = Field(None, ge=1, le=5)


class BulkComplianceOperation(BaseModel):
    """Bulk operations on compliance items"""
    operation: str  # update_status, assign_assessor, bulk_assess, etc.
    item_type: str  # controls, assessments, findings
    item_ids: List[int]
    operation_data: Dict[str, Any]


class BulkComplianceOperationResponse(BaseModel):
    """Response for bulk compliance operations"""
    success: bool
    operation: str
    item_type: str
    processed_count: int
    success_count: int
    error_count: int
    errors: List[str] = []
    updated_items: List[int] = []


# Specialized Schemas
class ComplianceGapAnalysisResponse(BaseModel):
    """Compliance gap analysis results"""
    framework_id: int
    analysis_date: datetime
    
    overall_compliance_percentage: float
    compliant_controls: int
    non_compliant_controls: int
    partially_compliant_controls: int
    not_assessed_controls: int
    
    critical_gaps: List[Dict[str, Any]]
    high_priority_gaps: List[Dict[str, Any]]
    remediation_roadmap: List[Dict[str, Any]]
    
    estimated_remediation_effort: Dict[str, Any]
    recommended_actions: List[str]


class ComplianceScorecardResponse(BaseModel):
    """Compliance scorecard data"""
    framework_id: int
    assessment_id: int
    scorecard_date: datetime
    
    overall_score: float
    maturity_score: float
    effectiveness_score: float
    implementation_score: float
    
    control_family_scores: Dict[str, float]
    trend_analysis: Dict[str, Any]
    benchmark_comparison: Dict[str, Any]
    
    executive_summary: str
    key_strengths: List[str]
    improvement_areas: List[str]
    recommendations: List[str]


class ComplianceFrameworkTemplate(BaseModel):
    """Template for creating compliance frameworks"""
    framework_type: ComplianceFrameworkEnum
    name: str
    description: str
    control_templates: List[Dict[str, Any]]
    default_settings: Dict[str, Any]