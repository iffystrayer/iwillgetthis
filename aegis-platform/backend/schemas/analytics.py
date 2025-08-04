from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for schema validation
class MetricTypeEnum(str, Enum):
    RISK_SCORE = "risk_score"
    COMPLIANCE_RATE = "compliance_rate"
    VULNERABILITY_COUNT = "vulnerability_count"
    INCIDENT_COUNT = "incident_count"
    ASSESSMENT_COUNT = "assessment_count"
    TRAINING_COMPLETION = "training_completion"
    VENDOR_RISK = "vendor_risk"
    ASSET_COVERAGE = "asset_coverage"
    CONTROL_EFFECTIVENESS = "control_effectiveness"
    BUSINESS_IMPACT = "business_impact"

class AggregationTypeEnum(str, Enum):
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    TREND = "trend"
    VARIANCE = "variance"

class TimeGranularityEnum(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class ReportTypeEnum(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_REGISTER = "risk_register"
    COMPLIANCE_STATUS = "compliance_status"
    VULNERABILITY_REPORT = "vulnerability_report"
    INCIDENT_ANALYSIS = "incident_analysis"
    TRAINING_METRICS = "training_metrics"
    VENDOR_SCORECARD = "vendor_scorecard"
    AUDIT_REPORT = "audit_report"
    TREND_ANALYSIS = "trend_analysis"
    CUSTOM = "custom"

class DashboardTypeEnum(str, Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    RISK_MANAGEMENT = "risk_management"
    VENDOR_MANAGEMENT = "vendor_management"
    ASSET_MANAGEMENT = "asset_management"
    TRAINING = "training"
    CUSTOM = "custom"

class PredictionModelEnum(str, Enum):
    LINEAR_REGRESSION = "linear_regression"
    TIME_SERIES = "time_series"
    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ARIMA = "arima"
    PROPHET = "prophet"

class TrendDirectionEnum(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"

# Metric Definition Schemas

class MetricDefinitionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metric_type: MetricTypeEnum
    category: Optional[str] = Field(None, max_length=100)
    data_source: Optional[str] = Field(None, max_length=255)
    calculation_formula: Optional[str] = None
    aggregation_type: AggregationTypeEnum = AggregationTypeEnum.SUM
    dimensions: Optional[List[str]] = []
    filters: Optional[Dict[str, Any]] = {}
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    higher_is_better: bool = True
    refresh_frequency: Optional[str] = Field("daily", max_length=50)
    historical_retention_days: int = Field(365, ge=1, le=3650)
    requires_approval: bool = False
    active: bool = True
    version: str = Field("1.0", max_length=20)

class MetricDefinitionCreate(MetricDefinitionBase):
    pass

class MetricDefinitionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    active: Optional[bool] = None
    refresh_frequency: Optional[str] = Field(None, max_length=50)

class MetricDefinitionResponse(MetricDefinitionBase):
    id: int
    metric_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True

# Metric Value Schemas

class MetricValueBase(BaseModel):
    timestamp: datetime
    time_granularity: TimeGranularityEnum
    value: float
    previous_value: Optional[float] = None
    baseline_value: Optional[float] = None
    dimensions: Optional[Dict[str, Any]] = {}
    context: Optional[Dict[str, Any]] = {}
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    data_completeness: Optional[float] = Field(None, ge=0.0, le=1.0)
    calculation_method: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class MetricValueCreate(MetricValueBase):
    metric_definition_id: int

class MetricValueResponse(MetricValueBase):
    id: int
    metric_definition_id: int
    anomaly_detected: bool
    anomaly_score: Optional[float]
    source_records_count: Optional[int]
    source_last_updated: Optional[datetime]
    created_at: datetime
    calculated_at: datetime

    class Config:
        from_attributes = True

# KPI Configuration Schemas

class KPIConfigurationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    business_owner: Optional[str] = Field(None, max_length=255)
    target_value: float
    target_period: Optional[str] = Field(None, max_length=50)
    excellent_threshold: Optional[float] = None
    good_threshold: Optional[float] = None
    poor_threshold: Optional[float] = None
    weight: float = Field(1.0, ge=0.0, le=1.0)
    criticality: Optional[str] = Field(None, max_length=50)
    display_order: int = Field(0, ge=0)
    chart_type: Optional[str] = Field(None, max_length=50)
    color_coding: Optional[Dict[str, Any]] = {}
    alert_enabled: bool = True
    alert_recipients: Optional[List[str]] = []
    alert_thresholds: Optional[Dict[str, Any]] = {}
    active: bool = True

class KPIConfigurationCreate(KPIConfigurationBase):
    metric_definition_id: int

class KPIConfigurationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_value: Optional[float] = None
    excellent_threshold: Optional[float] = None
    good_threshold: Optional[float] = None
    poor_threshold: Optional[float] = None
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    active: Optional[bool] = None

class KPIConfigurationResponse(KPIConfigurationBase):
    id: int
    kpi_id: str
    metric_definition_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Dashboard Schemas

class DashboardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    dashboard_type: DashboardTypeEnum
    category: Optional[str] = Field(None, max_length=100)
    layout_config: Optional[Dict[str, Any]] = {}
    theme_config: Optional[Dict[str, Any]] = {}
    refresh_interval: int = Field(300, ge=30, le=3600)
    is_public: bool = False
    allowed_roles: Optional[List[str]] = []
    allowed_users: Optional[List[str]] = []
    is_template: bool = False
    personal_settings: Optional[Dict[str, Any]] = {}
    active: bool = True
    version: str = Field("1.0", max_length=20)

class DashboardCreate(DashboardBase):
    parent_dashboard_id: Optional[int] = None

class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    theme_config: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = Field(None, ge=30, le=3600)
    is_public: Optional[bool] = None
    active: Optional[bool] = None

class DashboardResponse(DashboardBase):
    id: int
    dashboard_id: str
    parent_dashboard_id: Optional[int]
    view_count: int
    last_viewed: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True

# Dashboard Widget Schemas

class DashboardWidgetBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    widget_type: str = Field(..., max_length=100)
    data_source: Optional[Dict[str, Any]] = {}
    metrics: Optional[List[str]] = []
    filters: Optional[Dict[str, Any]] = {}
    time_range: Optional[Dict[str, Any]] = {}
    chart_config: Optional[Dict[str, Any]] = {}
    display_options: Optional[Dict[str, Any]] = {}
    size_config: Optional[Dict[str, Any]] = {}
    position_x: int = Field(0, ge=0)
    position_y: int = Field(0, ge=0)
    width: int = Field(4, ge=1, le=12)
    height: int = Field(3, ge=1, le=12)
    drill_down_enabled: bool = False
    drill_down_config: Optional[Dict[str, Any]] = {}
    export_enabled: bool = True
    active: bool = True

class DashboardWidgetCreate(DashboardWidgetBase):
    dashboard_id: int

class DashboardWidgetUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    data_source: Optional[Dict[str, Any]] = None
    chart_config: Optional[Dict[str, Any]] = None
    position_x: Optional[int] = Field(None, ge=0)
    position_y: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, ge=1, le=12)
    height: Optional[int] = Field(None, ge=1, le=12)
    active: Optional[bool] = None

class DashboardWidgetResponse(DashboardWidgetBase):
    id: int
    widget_id: str
    dashboard_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Report Template Schemas

class ReportTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: ReportTypeEnum
    category: Optional[str] = Field(None, max_length=100)
    template_config: Dict[str, Any]
    data_sources: Optional[List[str]] = []
    parameters: Optional[Dict[str, Any]] = {}
    supported_formats: Optional[List[str]] = ["PDF", "Excel", "CSV"]
    default_format: str = Field("PDF", max_length=20)
    page_layout: Optional[Dict[str, Any]] = {}
    can_be_scheduled: bool = True
    default_schedule: Optional[Dict[str, Any]] = {}
    is_public: bool = False
    allowed_roles: Optional[List[str]] = []
    required_permissions: Optional[List[str]] = []
    regulatory_mapping: Optional[List[str]] = []
    approval_required: bool = False
    retention_days: int = Field(2555, ge=1, le=3650)
    active: bool = True
    version: str = Field("1.0", max_length=20)

class ReportTemplateCreate(ReportTemplateBase):
    pass

class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    template_config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    default_format: Optional[str] = Field(None, max_length=20)
    active: Optional[bool] = None

class ReportTemplateResponse(ReportTemplateBase):
    id: int
    template_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Generated Report Schemas

class GeneratedReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    generated_for: Optional[str] = Field(None, max_length=255)
    parameters_used: Optional[Dict[str, Any]] = {}
    data_period_start: Optional[datetime] = None
    data_period_end: Optional[datetime] = None
    format: str = Field(..., max_length=20)

class GeneratedReportCreate(GeneratedReportBase):
    template_id: int

class GeneratedReportUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    generation_completed: Optional[datetime] = None
    file_size_bytes: Optional[int] = Field(None, ge=0)
    file_path: Optional[str] = Field(None, max_length=1000)
    records_processed: Optional[int] = Field(None, ge=0)
    data_completeness: Optional[float] = Field(None, ge=0.0, le=1.0)
    error_message: Optional[str] = None

class GeneratedReportResponse(GeneratedReportBase):
    id: int
    report_id: str
    template_id: int
    generation_started: datetime
    generation_completed: Optional[datetime]
    file_size_bytes: Optional[int]
    file_path: Optional[str]
    download_url: Optional[str]
    records_processed: Optional[int]
    data_completeness: Optional[float]
    warnings: Optional[List[str]]
    errors: Optional[List[str]]
    status: str
    error_message: Optional[str]
    retry_count: int
    expiry_date: Optional[datetime]
    password_protected: bool
    requires_approval: bool
    approved_by: Optional[str]
    approval_date: Optional[datetime]
    approval_status: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Prediction Configuration Schemas

class PredictionConfigurationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_metric: str = Field(..., max_length=255)
    model_type: PredictionModelEnum
    model_parameters: Optional[Dict[str, Any]] = {}
    feature_columns: Optional[List[str]] = []
    training_data_query: Optional[str] = None
    training_period_days: int = Field(365, ge=30, le=1095)
    minimum_data_points: int = Field(30, ge=10, le=1000)
    prediction_horizon_days: int = Field(30, ge=1, le=365)
    confidence_interval: float = Field(0.95, ge=0.5, le=0.99)
    update_frequency: str = Field("daily", max_length=50)
    active: bool = True
    model_version: str = Field("1.0", max_length=20)

class PredictionConfigurationCreate(PredictionConfigurationBase):
    pass

class PredictionConfigurationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    model_parameters: Optional[Dict[str, Any]] = None
    prediction_horizon_days: Optional[int] = Field(None, ge=1, le=365)
    confidence_interval: Optional[float] = Field(None, ge=0.5, le=0.99)
    active: Optional[bool] = None

class PredictionConfigurationResponse(PredictionConfigurationBase):
    id: int
    prediction_id: str
    last_trained: Optional[datetime]
    training_accuracy: Optional[float]
    validation_accuracy: Optional[float]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Prediction Result Schemas

class PredictionResultBase(BaseModel):
    prediction_date: datetime
    target_date: datetime
    predicted_value: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    input_features: Optional[Dict[str, Any]] = {}
    model_version: Optional[str] = Field(None, max_length=20)
    data_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    anomaly_indicators: Optional[List[str]] = []

class PredictionResultCreate(PredictionResultBase):
    prediction_configuration_id: int

class PredictionResultUpdate(BaseModel):
    actual_value: Optional[float] = None
    prediction_error: Optional[float] = None
    validated_at: Optional[datetime] = None

class PredictionResultResponse(PredictionResultBase):
    id: int
    result_id: str
    prediction_configuration_id: int
    actual_value: Optional[float]
    prediction_error: Optional[float]
    created_at: datetime
    validated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Analytics Job Schemas

class AnalyticsJobBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    job_type: str = Field(..., max_length=100)
    description: Optional[str] = None
    configuration: Dict[str, Any]
    schedule: Optional[str] = Field(None, max_length=100)
    priority: int = Field(5, ge=1, le=10)

class AnalyticsJobCreate(AnalyticsJobBase):
    pass

class AnalyticsJobUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[str] = Field(None, max_length=50)

class AnalyticsJobResponse(AnalyticsJobBase):
    id: int
    job_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    records_processed: Optional[int]
    success_count: Optional[int]
    error_count: Optional[int]
    warnings: Optional[List[str]]
    errors: Optional[List[str]]
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True

# Analytics Insight Schemas

class AnalyticsInsight(BaseModel):
    insight_type: str = Field(..., max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    impact_level: str = Field(..., max_length=50)
    confidence: float = Field(..., ge=0.0, le=1.0)
    data_points: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    related_metrics: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Risk Forecast Schemas

class RiskScenario(BaseModel):
    scenario_name: str = Field(..., max_length=100)
    probability: float = Field(..., ge=0.0, le=1.0)
    description: Optional[str] = None
    impact_level: Optional[str] = Field(None, max_length=50)

class MitigationStrategy(BaseModel):
    strategy_name: str = Field(..., max_length=100)
    expected_impact: float = Field(..., ge=0.0, le=1.0)
    cost_estimate: Optional[float] = Field(None, ge=0)
    implementation_time_days: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None

class ForecastPeriod(BaseModel):
    period_start: datetime
    period_end: datetime
    risk_level: float = Field(..., ge=0.0, le=100.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_risks: List[str] = []
    trend_direction: TrendDirectionEnum

class RiskForecast(BaseModel):
    metric_name: str = Field(..., max_length=255)
    current_value: float
    forecast_periods: List[ForecastPeriod]
    risk_scenarios: List[RiskScenario]
    mitigation_strategies: List[MitigationStrategy]
    confidence_level: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime

# Dashboard Data Schemas

class MetricSummary(BaseModel):
    metric_id: str
    metric_name: str
    current_value: float
    previous_value: Optional[float] = None
    target_value: Optional[float] = None
    trend_direction: TrendDirectionEnum
    change_percentage: Optional[float] = None
    status: str = Field(..., max_length=50)  # on_target, above_target, below_target
    last_updated: datetime

class KPISummary(BaseModel):
    kpi_id: str
    kpi_name: str
    current_value: float
    target_value: float
    performance_percentage: float = Field(..., ge=0.0, le=200.0)
    status: str = Field(..., max_length=50)  # excellent, good, poor
    trend_direction: TrendDirectionEnum
    last_updated: datetime

class DashboardData(BaseModel):
    dashboard_id: str
    dashboard_name: str
    metrics: List[MetricSummary]
    kpis: List[KPISummary]
    insights: List[AnalyticsInsight]
    alerts: List[Dict[str, Any]] = []
    last_refreshed: datetime = Field(default_factory=datetime.utcnow)

# Executive Dashboard Schemas

class ExecutiveSummary(BaseModel):
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_trend: TrendDirectionEnum
    critical_issues_count: int = Field(..., ge=0)
    compliance_rate: float = Field(..., ge=0.0, le=100.0)
    incident_count_mtd: int = Field(..., ge=0)
    vendor_risk_score: float = Field(..., ge=0.0, le=100.0)
    training_completion_rate: float = Field(..., ge=0.0, le=100.0)
    top_risks: List[Dict[str, Any]] = []
    upcoming_assessments: List[Dict[str, Any]] = []
    recent_incidents: List[Dict[str, Any]] = []

class ComplianceDashboard(BaseModel):
    overall_compliance_rate: float = Field(..., ge=0.0, le=100.0)
    frameworks: List[Dict[str, Any]] = []
    overdue_assessments: int = Field(..., ge=0)
    upcoming_audits: List[Dict[str, Any]] = []
    compliance_gaps: List[Dict[str, Any]] = []
    remediation_progress: float = Field(..., ge=0.0, le=100.0)

class SecurityDashboard(BaseModel):
    security_posture_score: float = Field(..., ge=0.0, le=100.0)
    active_vulnerabilities: int = Field(..., ge=0)
    critical_vulnerabilities: int = Field(..., ge=0)
    patch_compliance_rate: float = Field(..., ge=0.0, le=100.0)
    security_incidents_mtd: int = Field(..., ge=0)
    threat_intel_alerts: List[Dict[str, Any]] = []

# Search and Filter Schemas

class MetricSearchFilter(BaseModel):
    metric_type: Optional[MetricTypeEnum] = None
    category: Optional[str] = None
    active_only: Optional[bool] = True
    has_target: Optional[bool] = None
    search_term: Optional[str] = None
    limit: Optional[int] = Field(50, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)

class TimeRangeFilter(BaseModel):
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularityEnum = TimeGranularityEnum.DAY

class AnalyticsQueryFilter(BaseModel):
    metrics: Optional[List[str]] = []
    time_range: TimeRangeFilter
    dimensions: Optional[Dict[str, Any]] = {}
    aggregation: Optional[AggregationTypeEnum] = AggregationTypeEnum.AVERAGE
    include_predictions: bool = False
    include_trends: bool = True