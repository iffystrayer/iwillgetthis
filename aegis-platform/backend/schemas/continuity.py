from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ContinuityPlanStatusEnum(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    OUTDATED = "outdated"
    ARCHIVED = "archived"

class BusinessImpactLevelEnum(str, Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"

class RecoveryPriorityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"

class ContinuityTestStatusEnum(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ActivationStatusEnum(str, Enum):
    INACTIVE = "inactive"
    STANDBY = "standby"
    PARTIAL_ACTIVATION = "partial_activation"
    FULL_ACTIVATION = "full_activation"
    RECOVERY_MODE = "recovery_mode"

# Business Continuity Plan Schemas

class BusinessContinuityPlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    version: str = Field(default="1.0", max_length=20)
    scope: Optional[str] = None
    business_units: List[str] = Field(default_factory=list)
    geographic_scope: List[str] = Field(default_factory=list)
    objectives: Optional[str] = None
    assumptions: Optional[str] = None
    dependencies: Dict[str, Any] = Field(default_factory=dict)
    review_frequency_months: int = Field(default=12, ge=1, le=60)

class BusinessContinuityPlanCreate(BusinessContinuityPlanBase):
    created_by: str = Field(..., min_length=1, max_length=255)

class BusinessContinuityPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=20)
    scope: Optional[str] = None
    business_units: Optional[List[str]] = None
    geographic_scope: Optional[List[str]] = None
    objectives: Optional[str] = None
    assumptions: Optional[str] = None
    dependencies: Optional[Dict[str, Any]] = None
    status: Optional[ContinuityPlanStatusEnum] = None
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    review_frequency_months: Optional[int] = Field(None, ge=1, le=60)
    updated_by: Optional[str] = None

class BusinessContinuityPlanResponse(BusinessContinuityPlanBase):
    id: int
    plan_id: str
    status: ContinuityPlanStatusEnum
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

# Business Impact Analysis Schemas

class BusinessImpactAnalysisBase(BaseModel):
    business_process: str = Field(..., min_length=1, max_length=500)
    process_owner: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    impact_level: BusinessImpactLevelEnum
    rto_hours: float = Field(..., ge=0, le=168)  # Max 1 week
    rpo_hours: float = Field(..., ge=0, le=24)   # Max 24 hours
    financial_impact_hourly: Optional[float] = Field(None, ge=0)
    financial_impact_daily: Optional[float] = Field(None, ge=0)
    operational_impact: Optional[str] = None
    regulatory_impact: Optional[str] = None
    reputational_impact: Optional[str] = None
    minimum_service_level: Optional[float] = Field(None, ge=0, le=100)
    critical_dependencies: Dict[str, Any] = Field(default_factory=dict)
    required_resources: Dict[str, Any] = Field(default_factory=dict)
    peak_periods: List[str] = Field(default_factory=list)
    seasonal_considerations: Optional[str] = None

    @validator('minimum_service_level')
    def validate_service_level(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Service level must be between 0 and 100 percent')
        return v

class BusinessImpactAnalysisCreate(BusinessImpactAnalysisBase):
    continuity_plan_id: int = Field(..., gt=0)

class BusinessImpactAnalysisUpdate(BaseModel):
    business_process: Optional[str] = Field(None, min_length=1, max_length=500)
    process_owner: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    impact_level: Optional[BusinessImpactLevelEnum] = None
    rto_hours: Optional[float] = Field(None, ge=0, le=168)
    rpo_hours: Optional[float] = Field(None, ge=0, le=24)
    financial_impact_hourly: Optional[float] = Field(None, ge=0)
    financial_impact_daily: Optional[float] = Field(None, ge=0)
    operational_impact: Optional[str] = None
    regulatory_impact: Optional[str] = None
    reputational_impact: Optional[str] = None
    minimum_service_level: Optional[float] = Field(None, ge=0, le=100)
    critical_dependencies: Optional[Dict[str, Any]] = None
    required_resources: Optional[Dict[str, Any]] = None
    peak_periods: Optional[List[str]] = None
    seasonal_considerations: Optional[str] = None

class BusinessImpactAnalysisResponse(BusinessImpactAnalysisBase):
    id: int
    analysis_id: str
    continuity_plan_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Disaster Recovery Procedure Schemas

class RecoveryStepBase(BaseModel):
    step_number: int = Field(..., ge=1)
    description: str = Field(..., min_length=1)
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    responsible_role: Optional[str] = None
    automated: bool = Field(default=False)
    script_path: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[int] = Field(default_factory=list)  # Step numbers this depends on
    validation_criteria: Optional[str] = None

class DisasterRecoveryProcedureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=255)
    priority: RecoveryPriorityEnum
    target_rto_hours: float = Field(..., ge=0, le=168)
    target_rpo_hours: float = Field(..., ge=0, le=24)
    estimated_recovery_time: Optional[float] = Field(None, ge=0)
    preparation_steps: List[RecoveryStepBase] = Field(default_factory=list)
    activation_triggers: List[str] = Field(default_factory=list)
    recovery_steps: List[RecoveryStepBase] = Field(default_factory=list)
    validation_steps: List[RecoveryStepBase] = Field(default_factory=list)
    required_personnel: List[str] = Field(default_factory=list)
    required_equipment: List[str] = Field(default_factory=list)
    required_facilities: List[str] = Field(default_factory=list)
    estimated_cost: Optional[float] = Field(None, ge=0)
    automated: bool = Field(default=False)
    automation_script: Optional[str] = None
    manual_intervention_required: bool = Field(default=True)
    test_frequency_months: int = Field(default=6, ge=1, le=24)

class DisasterRecoveryProcedureCreate(DisasterRecoveryProcedureBase):
    continuity_plan_id: int = Field(..., gt=0)

class DisasterRecoveryProcedureUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=255)
    priority: Optional[RecoveryPriorityEnum] = None
    target_rto_hours: Optional[float] = Field(None, ge=0, le=168)
    target_rpo_hours: Optional[float] = Field(None, ge=0, le=24)
    estimated_recovery_time: Optional[float] = Field(None, ge=0)
    preparation_steps: Optional[List[RecoveryStepBase]] = None
    activation_triggers: Optional[List[str]] = None
    recovery_steps: Optional[List[RecoveryStepBase]] = None
    validation_steps: Optional[List[RecoveryStepBase]] = None
    required_personnel: Optional[List[str]] = None
    required_equipment: Optional[List[str]] = None
    required_facilities: Optional[List[str]] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    automated: Optional[bool] = None
    automation_script: Optional[str] = None
    manual_intervention_required: Optional[bool] = None
    test_frequency_months: Optional[int] = Field(None, ge=1, le=24)
    last_tested: Optional[datetime] = None
    test_success_rate: Optional[float] = Field(None, ge=0, le=100)

class DisasterRecoveryProcedureResponse(DisasterRecoveryProcedureBase):
    id: int
    procedure_id: str
    continuity_plan_id: int
    last_tested: Optional[datetime] = None
    test_success_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Continuity Test Schemas

class TestObjectiveBase(BaseModel):
    objective: str = Field(..., min_length=1)
    success_criteria: str = Field(..., min_length=1)
    measurement_method: Optional[str] = None

class TestScenarioBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(tabletop|walkthrough|simulation|full_test)$")
    estimated_duration_hours: Optional[float] = Field(None, ge=0, le=24)
    target_rto_hours: Optional[float] = Field(None, ge=0, le=168)
    target_rpo_hours: Optional[float] = Field(None, ge=0, le=24)
    procedures_to_test: List[str] = Field(default_factory=list)
    expected_decisions: List[str] = Field(default_factory=list)
    steps: List[Dict[str, Any]] = Field(default_factory=list)

class ContinuityTestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    test_type: str = Field(..., pattern="^(Tabletop|Walkthrough|Simulation|Full Test)$")
    scope: Optional[str] = None
    scheduled_date: datetime
    objectives: List[TestObjectiveBase] = Field(default_factory=list)
    scenarios: List[TestScenarioBase] = Field(default_factory=list)
    participants: List[str] = Field(default_factory=list)
    observers: List[str] = Field(default_factory=list)

    @validator('scheduled_date')
    def validate_scheduled_date(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Scheduled date must be in the future')
        return v

class ContinuityTestCreate(ContinuityTestBase):
    continuity_plan_id: int = Field(..., gt=0)
    test_coordinator: Optional[str] = Field(None, max_length=255)

class ContinuityTestUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    test_type: Optional[str] = Field(None, pattern="^(Tabletop|Walkthrough|Simulation|Full Test)$")
    scope: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[ContinuityTestStatusEnum] = None
    test_coordinator: Optional[str] = Field(None, max_length=255)
    objectives: Optional[List[TestObjectiveBase]] = None
    scenarios: Optional[List[TestScenarioBase]] = None
    participants: Optional[List[str]] = None
    observers: Optional[List[str]] = None

class ContinuityTestResponse(ContinuityTestBase):
    id: int
    test_id: str
    continuity_plan_id: int
    status: ContinuityTestStatusEnum
    test_coordinator: Optional[str] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    overall_success: Optional[bool] = None
    rto_achieved: Optional[float] = None
    rpo_achieved: Optional[float] = None
    issues_identified: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    test_report: Optional[str] = None
    lessons_learned: Optional[str] = None
    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Plan Activation Schemas

class PlanActivationBase(BaseModel):
    trigger_event: str = Field(..., min_length=1, max_length=500)
    activation_level: ActivationStatusEnum
    activation_reason: str = Field(..., min_length=1)
    expected_duration: Optional[float] = Field(None, ge=0)  # Hours
    affected_business_units: List[str] = Field(default_factory=list)
    activated_procedures: List[str] = Field(default_factory=list)
    personnel_notified: List[str] = Field(default_factory=list)

class PlanActivationCreate(PlanActivationBase):
    continuity_plan_id: int = Field(..., gt=0)
    activated_by: str = Field(..., min_length=1, max_length=255)

class PlanActivationUpdate(BaseModel):
    activation_level: Optional[ActivationStatusEnum] = None
    current_status: Optional[str] = Field(None, max_length=100)
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    stakeholder_notifications: Optional[List[Dict[str, Any]]] = None
    communication_log: Optional[List[Dict[str, Any]]] = None
    success_metrics: Optional[Dict[str, Any]] = None
    actual_rto: Optional[float] = Field(None, ge=0)
    actual_rpo: Optional[float] = Field(None, ge=0)
    lessons_learned: Optional[str] = None
    deactivated_by: Optional[str] = Field(None, max_length=255)
    deactivation_time: Optional[datetime] = None
    deactivation_reason: Optional[str] = None

class PlanActivationResponse(PlanActivationBase):
    id: int
    activation_id: str
    continuity_plan_id: int
    activated_by: str
    activation_time: datetime
    current_status: Optional[str] = None
    completion_percentage: float = Field(default=0.0)
    stakeholder_notifications: List[Dict[str, Any]] = Field(default_factory=list)
    communication_log: List[Dict[str, Any]] = Field(default_factory=list)
    success_metrics: Dict[str, Any] = Field(default_factory=dict)
    actual_rto: Optional[float] = None
    actual_rpo: Optional[float] = None
    lessons_learned: Optional[str] = None
    deactivated_by: Optional[str] = None
    deactivation_time: Optional[datetime] = None
    deactivation_reason: Optional[str] = None
    actual_end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Procedure Execution Schemas

class ProcedureExecutionBase(BaseModel):
    execution_context: str = Field(default="Manual", max_length=100)

class ProcedureExecutionCreate(ProcedureExecutionBase):
    procedure_id: int = Field(..., gt=0)
    activation_id: Optional[int] = Field(None, gt=0)
    executed_by: str = Field(..., min_length=1, max_length=255)

class ProcedureExecutionUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    end_time: Optional[datetime] = None
    successful: Optional[bool] = None
    rto_met: Optional[bool] = None
    rpo_met: Optional[bool] = None
    issues_encountered: Optional[List[str]] = None
    deviations_from_plan: Optional[str] = None
    notes: Optional[str] = None
    evidence_collected: Optional[List[Dict[str, Any]]] = None
    actual_recovery_time: Optional[float] = Field(None, ge=0)
    actual_data_loss: Optional[float] = Field(None, ge=0)
    resource_utilization: Optional[Dict[str, Any]] = None

class ProcedureExecutionResponse(ProcedureExecutionBase):
    id: int
    execution_id: str
    procedure_id: int
    activation_id: Optional[int] = None
    executed_by: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    status: Optional[str] = None
    completion_percentage: float = Field(default=0.0)
    successful: Optional[bool] = None
    rto_met: Optional[bool] = None
    rpo_met: Optional[bool] = None
    issues_encountered: List[str] = Field(default_factory=list)
    deviations_from_plan: Optional[str] = None
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    notes: Optional[str] = None
    evidence_collected: List[Dict[str, Any]] = Field(default_factory=list)
    actual_recovery_time: Optional[float] = None
    actual_data_loss: Optional[float] = None
    resource_utilization: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Continuity Metrics Schemas

class ContinuityMetricsBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=255)
    metric_type: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    target_name: Optional[str] = Field(None, max_length=255)
    target_value: Optional[float] = None
    tolerance_threshold: Optional[float] = Field(None, ge=0)

class ContinuityMetricsCreate(ContinuityMetricsBase):
    current_value: Optional[float] = None

class ContinuityMetricsUpdate(BaseModel):
    metric_name: Optional[str] = Field(None, min_length=1, max_length=255)
    metric_type: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    target_name: Optional[str] = Field(None, max_length=255)
    target_value: Optional[float] = None
    tolerance_threshold: Optional[float] = Field(None, ge=0)
    current_value: Optional[float] = None
    trend: Optional[str] = Field(None, max_length=50)
    last_test_value: Optional[float] = None
    last_incident_value: Optional[float] = None
    status: Optional[str] = Field(None, max_length=50)
    action_required: Optional[bool] = None

class ContinuityMetricsResponse(ContinuityMetricsBase):
    id: int
    metric_id: str
    current_value: Optional[float] = None
    measurement_date: Optional[datetime] = None
    trend: Optional[str] = None
    historical_values: Dict[str, Any] = Field(default_factory=dict)
    last_test_value: Optional[float] = None
    last_incident_value: Optional[float] = None
    status: Optional[str] = None
    action_required: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Continuity Resource Schemas

class ContinuityResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    resource_type: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    available: bool = Field(default=True)
    capacity: Optional[float] = Field(None, ge=0)
    current_utilization: Optional[float] = Field(None, ge=0, le=100)
    location: Optional[str] = Field(None, max_length=500)
    contact_information: Dict[str, Any] = Field(default_factory=dict)
    specifications: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    criticality_level: Optional[str] = Field(None, max_length=50)
    dependencies: List[str] = Field(default_factory=list)
    dependents: List[str] = Field(default_factory=list)
    backup_resources: List[str] = Field(default_factory=list)
    alternative_sources: List[str] = Field(default_factory=list)

class ContinuityResourceCreate(ContinuityResourceBase):
    pass

class ContinuityResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    resource_type: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    available: Optional[bool] = None
    capacity: Optional[float] = Field(None, ge=0)
    current_utilization: Optional[float] = Field(None, ge=0, le=100)
    location: Optional[str] = Field(None, max_length=500)
    contact_information: Optional[Dict[str, Any]] = None
    specifications: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    maintenance_schedule: Optional[List[Dict[str, Any]]] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    replacement_date: Optional[datetime] = None
    acquisition_cost: Optional[float] = Field(None, ge=0)
    maintenance_cost_annual: Optional[float] = Field(None, ge=0)
    replacement_cost: Optional[float] = Field(None, ge=0)
    criticality_level: Optional[str] = Field(None, max_length=50)
    dependencies: Optional[List[str]] = None
    dependents: Optional[List[str]] = None
    backup_resources: Optional[List[str]] = None
    alternative_sources: Optional[List[str]] = None

class ContinuityResourceResponse(ContinuityResourceBase):
    id: int
    resource_id: str
    maintenance_schedule: List[Dict[str, Any]] = Field(default_factory=list)
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    replacement_date: Optional[datetime] = None
    acquisition_cost: Optional[float] = None
    maintenance_cost_annual: Optional[float] = None
    replacement_cost: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Dashboard and Summary Schemas

class ContinuitySummary(BaseModel):
    total_plans: int = 0
    active_plans: int = 0
    total_procedures: int = 0
    recent_tests: int = 0
    active_activations: int = 0
    overdue_reviews: int = 0

class ContinuityMetricsSummary(BaseModel):
    plans_tracked: int = 0
    average_rto: float = 0.0
    average_rpo: float = 0.0
    compliance_rate: float = 0.0
    critical_issues: List[str] = Field(default_factory=list)

class ContinuityDashboard(BaseModel):
    summary: ContinuitySummary
    active_plans: List[Dict[str, Any]] = Field(default_factory=list)
    recent_tests: List[Dict[str, Any]] = Field(default_factory=list)
    active_activations: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: ContinuityMetricsSummary
    upcoming_tests: List[Dict[str, Any]] = Field(default_factory=list)
    overdue_reviews: List[Dict[str, Any]] = Field(default_factory=list)

# Test Execution Schemas

class TestExecutionRequest(BaseModel):
    test_id: int = Field(..., gt=0)
    coordinator: str = Field(..., min_length=1, max_length=255)

class TestExecutionResult(BaseModel):
    overall_success: bool
    success_rate: float = Field(..., ge=0, le=1)
    rto_achieved: Optional[float] = None
    rpo_achieved: Optional[float] = None
    issues_identified: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    scenarios_tested: int = 0
    scenarios_passed: int = 0

# Search and Filter Schemas

class ContinuityPlanFilter(BaseModel):
    status: Optional[ContinuityPlanStatusEnum] = None
    business_unit: Optional[str] = None
    geographic_scope: Optional[str] = None
    review_overdue: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class ProcedureFilter(BaseModel):
    priority: Optional[RecoveryPriorityEnum] = None
    category: Optional[str] = None
    automated: Optional[bool] = None
    test_overdue: Optional[bool] = None
    rto_max: Optional[float] = Field(None, ge=0)
    rpo_max: Optional[float] = Field(None, ge=0)

class TestFilter(BaseModel):
    status: Optional[ContinuityTestStatusEnum] = None
    test_type: Optional[str] = None
    success: Optional[bool] = None
    scheduled_after: Optional[datetime] = None
    scheduled_before: Optional[datetime] = None
    completed_after: Optional[datetime] = None
    completed_before: Optional[datetime] = None