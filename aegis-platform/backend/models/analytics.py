from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM as SQLEnum
from datetime import datetime
import uuid
from enum import Enum

Base = declarative_base()

class MetricType(Enum):
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

class AggregationType(Enum):
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    TREND = "trend"
    VARIANCE = "variance"

class TimeGranularity(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class ReportType(Enum):
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

class DashboardType(Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    RISK_MANAGEMENT = "risk_management"
    VENDOR_MANAGEMENT = "vendor_management"
    ASSET_MANAGEMENT = "asset_management"
    TRAINING = "training"
    CUSTOM = "custom"

class PredictionModel(Enum):
    LINEAR_REGRESSION = "linear_regression"
    TIME_SERIES = "time_series"
    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ARIMA = "arima"
    PROPHET = "prophet"

# Core Analytics Models

class MetricDefinition(Base):
    __tablename__ = "metric_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"MET-{uuid.uuid4().hex[:8].upper()}")
    
    # Metric identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    category = Column(String(100))  # risk, compliance, security, operational
    
    # Calculation configuration
    data_source = Column(String(255))  # Source table/view
    calculation_formula = Column(Text)  # SQL or calculation logic
    aggregation_type = Column(SQLEnum(AggregationType), default=AggregationType.SUM)
    
    # Dimensional attributes
    dimensions = Column(JSON)  # Grouping dimensions (time, department, asset_type, etc.)
    filters = Column(JSON)  # Default filters to apply
    
    # Metadata
    unit_of_measure = Column(String(50))  # %, count, $, days, etc.
    target_value = Column(Float)  # Target/goal value
    threshold_warning = Column(Float)  # Warning threshold
    threshold_critical = Column(Float)  # Critical threshold
    higher_is_better = Column(Boolean, default=True)  # Direction of improvement
    
    # Calculation settings
    refresh_frequency = Column(String(50))  # real-time, hourly, daily, weekly
    historical_retention_days = Column(Integer, default=365)
    requires_approval = Column(Boolean, default=False)
    
    # Status and lifecycle
    active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Relationships
    metric_values = relationship("MetricValue", back_populates="metric_definition")
    kpis = relationship("KPIConfiguration", back_populates="metric_definition")

class MetricValue(Base):
    __tablename__ = "metric_values"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_definition_id = Column(Integer, ForeignKey("metric_definitions.id"))
    
    # Time dimension
    timestamp = Column(DateTime, nullable=False, index=True)
    time_granularity = Column(SQLEnum(TimeGranularity), nullable=False)
    
    # Value and context
    value = Column(Float, nullable=False)
    previous_value = Column(Float)  # Previous period value for trend calculation
    baseline_value = Column(Float)  # Baseline for comparison
    
    # Dimensional breakdown
    dimensions = Column(JSON)  # Dimension values (department: "IT", asset_type: "server")
    context = Column(JSON)  # Additional context data
    
    # Quality and reliability
    confidence_score = Column(Float)  # Confidence in the metric value (0-1)
    data_completeness = Column(Float)  # % of expected data points included
    calculation_method = Column(String(255))  # Method used for calculation
    
    # Annotations
    anomaly_detected = Column(Boolean, default=False)
    anomaly_score = Column(Float)  # Anomaly detection score
    notes = Column(Text)  # Manual annotations
    
    # Data lineage
    source_records_count = Column(Integer)  # Number of source records
    source_last_updated = Column(DateTime)  # When source data was last updated
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    metric_definition = relationship("MetricDefinition", back_populates="metric_values")

class KPIConfiguration(Base):
    __tablename__ = "kpi_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"KPI-{uuid.uuid4().hex[:8].upper()}")
    metric_definition_id = Column(Integer, ForeignKey("metric_definitions.id"))
    
    # KPI identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    business_owner = Column(String(255))  # Business stakeholder responsible
    
    # Targets and thresholds
    target_value = Column(Float, nullable=False)
    target_period = Column(String(50))  # monthly, quarterly, annually
    
    # Performance bands
    excellent_threshold = Column(Float)  # Green zone
    good_threshold = Column(Float)  # Yellow zone
    poor_threshold = Column(Float)  # Red zone
    
    # Weighting and importance
    weight = Column(Float, default=1.0)  # Relative importance (0-1)
    criticality = Column(String(50))  # high, medium, low
    
    # Reporting configuration
    display_order = Column(Integer, default=0)
    chart_type = Column(String(50))  # line, bar, gauge, scorecard
    color_coding = Column(JSON)  # Color scheme configuration
    
    # Alerting
    alert_enabled = Column(Boolean, default=True)
    alert_recipients = Column(JSON)  # List of email addresses
    alert_thresholds = Column(JSON)  # Conditions for alerts
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    metric_definition = relationship("MetricDefinition", back_populates="kpis")

# Dashboard and Visualization Models

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"DASH-{uuid.uuid4().hex[:8].upper()}")
    
    # Dashboard identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    dashboard_type = Column(SQLEnum(DashboardType), nullable=False)
    category = Column(String(100))  # executive, operational, functional
    
    # Configuration
    layout_config = Column(JSON)  # Grid layout configuration
    theme_config = Column(JSON)  # Color scheme, fonts, etc.
    refresh_interval = Column(Integer, default=300)  # Seconds
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(JSON)  # List of roles with access
    allowed_users = Column(JSON)  # List of specific users
    
    # Personalization
    is_template = Column(Boolean, default=False)
    parent_dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    personal_settings = Column(JSON)  # User-specific customizations
    
    # Status and lifecycle
    active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Usage tracking
    view_count = Column(Integer, default=0)
    last_viewed = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Relationships
    parent_dashboard = relationship("Dashboard", remote_side=[id])
    widgets = relationship("DashboardWidget", back_populates="dashboard")

class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"WID-{uuid.uuid4().hex[:8].upper()}")
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    
    # Widget identification
    title = Column(String(255), nullable=False)
    description = Column(Text)
    widget_type = Column(String(100), nullable=False)  # chart, table, scorecard, gauge, map
    
    # Data configuration
    data_source = Column(JSON)  # Data query/source configuration
    metrics = Column(JSON)  # List of metric IDs to display
    filters = Column(JSON)  # Widget-specific filters
    time_range = Column(JSON)  # Time period configuration
    
    # Visualization configuration
    chart_config = Column(JSON)  # Chart-specific settings
    display_options = Column(JSON)  # Colors, fonts, formatting
    size_config = Column(JSON)  # Width, height, responsive settings
    
    # Layout and positioning
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)
    
    # Interactivity
    drill_down_enabled = Column(Boolean, default=False)
    drill_down_config = Column(JSON)  # Drill-down navigation configuration
    export_enabled = Column(Boolean, default=True)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

# Reporting Models

class ReportTemplate(Base):
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"RPT-{uuid.uuid4().hex[:8].upper()}")
    
    # Template identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    report_type = Column(SQLEnum(ReportType), nullable=False)
    category = Column(String(100))  # compliance, risk, security, operational
    
    # Template configuration
    template_config = Column(JSON, nullable=False)  # Report structure and layout
    data_sources = Column(JSON)  # Required data sources
    parameters = Column(JSON)  # Configurable parameters
    
    # Output configuration
    supported_formats = Column(JSON)  # PDF, Excel, CSV, HTML
    default_format = Column(String(20), default="PDF")
    page_layout = Column(JSON)  # Page size, orientation, margins
    
    # Scheduling
    can_be_scheduled = Column(Boolean, default=True)
    default_schedule = Column(JSON)  # Default scheduling configuration
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(JSON)
    required_permissions = Column(JSON)
    
    # Quality and compliance
    regulatory_mapping = Column(JSON)  # Which regulations this report satisfies
    approval_required = Column(Boolean, default=False)
    retention_days = Column(Integer, default=2555)  # 7 years default
    
    # Status
    active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    generated_reports = relationship("GeneratedReport", back_populates="template")
    scheduled_reports = relationship("ScheduledReport", back_populates="template")

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"GEN-{uuid.uuid4().hex[:8].upper()}")
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    
    # Report metadata
    title = Column(String(500), nullable=False)
    description = Column(Text)
    generated_for = Column(String(255))  # User who requested the report
    
    # Generation details
    parameters_used = Column(JSON)  # Parameters applied during generation
    data_period_start = Column(DateTime)
    data_period_end = Column(DateTime)
    generation_started = Column(DateTime, default=datetime.utcnow)
    generation_completed = Column(DateTime)
    
    # Output details
    format = Column(String(20), nullable=False)
    file_size_bytes = Column(Integer)
    file_path = Column(String(1000))  # Path to generated file
    download_url = Column(String(1000))  # Temporary download URL
    
    # Quality metrics
    records_processed = Column(Integer)
    data_completeness = Column(Float)  # % of expected data included
    warnings = Column(JSON)  # Non-fatal issues during generation
    errors = Column(JSON)  # Errors encountered
    
    # Status and lifecycle
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Access and security
    access_log = Column(JSON)  # Who accessed the report and when
    expiry_date = Column(DateTime)  # When the report expires
    password_protected = Column(Boolean, default=False)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(255))
    approval_date = Column(DateTime)
    approval_status = Column(String(50))  # pending, approved, rejected
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="generated_reports")

class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"SCH-{uuid.uuid4().hex[:8].upper()}")
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    
    # Schedule identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Scheduling configuration
    cron_expression = Column(String(100), nullable=False)  # Cron format
    timezone = Column(String(50), default="UTC")
    
    # Report configuration
    parameters = Column(JSON)  # Fixed parameters for this schedule
    output_format = Column(String(20), default="PDF")
    
    # Distribution
    recipients = Column(JSON, nullable=False)  # Email addresses
    subject_template = Column(String(500))
    body_template = Column(Text)
    
    # Execution tracking
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Status
    active = Column(Boolean, default=True)
    paused = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="scheduled_reports")

# Predictive Analytics Models

class PredictionConfiguration(Base):
    __tablename__ = "prediction_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"PRED-{uuid.uuid4().hex[:8].upper()}")
    
    # Prediction identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_metric = Column(String(255), nullable=False)  # What we're predicting
    
    # Model configuration
    model_type = Column(SQLEnum(PredictionModel), nullable=False)
    model_parameters = Column(JSON)  # Model-specific hyperparameters
    feature_columns = Column(JSON)  # Input features for prediction
    
    # Training configuration
    training_data_query = Column(Text)  # SQL query for training data
    training_period_days = Column(Integer, default=365)
    minimum_data_points = Column(Integer, default=30)
    
    # Prediction settings
    prediction_horizon_days = Column(Integer, default=30)  # How far ahead to predict
    confidence_interval = Column(Float, default=0.95)  # Confidence level
    update_frequency = Column(String(50), default="daily")
    
    # Model performance tracking
    last_trained = Column(DateTime)
    training_accuracy = Column(Float)  # Model accuracy on training data
    validation_accuracy = Column(Float)  # Model accuracy on validation data
    
    # Status and lifecycle
    active = Column(Boolean, default=True)
    model_version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    predictions = relationship("PredictionResult", back_populates="configuration")

class PredictionResult(Base):
    __tablename__ = "prediction_results"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"PRES-{uuid.uuid4().hex[:8].upper()}")
    prediction_configuration_id = Column(Integer, ForeignKey("prediction_configurations.id"))
    
    # Prediction details
    prediction_date = Column(DateTime, nullable=False)  # When prediction was made
    target_date = Column(DateTime, nullable=False)  # Date being predicted
    
    # Prediction results
    predicted_value = Column(Float, nullable=False)
    confidence_lower = Column(Float)  # Lower bound of confidence interval
    confidence_upper = Column(Float)  # Upper bound of confidence interval
    confidence_score = Column(Float)  # Overall confidence (0-1)
    
    # Actual outcome (for validation)
    actual_value = Column(Float)  # Actual value when known
    prediction_error = Column(Float)  # Difference between predicted and actual
    
    # Context and features
    input_features = Column(JSON)  # Feature values used for prediction
    model_version = Column(String(20))  # Version of model used
    
    # Quality indicators
    data_quality_score = Column(Float)  # Quality of input data (0-1)
    anomaly_indicators = Column(JSON)  # Detected anomalies in input
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)  # When actual value was recorded
    
    # Relationships
    configuration = relationship("PredictionConfiguration", back_populates="predictions")

# Analytics Processing Models

class AnalyticsJob(Base):
    __tablename__ = "analytics_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"JOB-{uuid.uuid4().hex[:8].upper()}")
    
    # Job identification
    name = Column(String(255), nullable=False)
    job_type = Column(String(100), nullable=False)  # metric_calculation, report_generation, prediction
    description = Column(Text)
    
    # Job configuration
    configuration = Column(JSON, nullable=False)  # Job-specific configuration
    schedule = Column(String(100))  # Cron expression or "on-demand"
    priority = Column(Integer, default=5)  # 1-10, higher is more important
    
    # Execution tracking
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Results and metrics
    records_processed = Column(Integer)
    success_count = Column(Integer)
    error_count = Column(Integer)
    warnings = Column(JSON)
    errors = Column(JSON)
    
    # Resource usage
    cpu_time_seconds = Column(Float)
    memory_peak_mb = Column(Float)
    disk_io_mb = Column(Float)
    
    # Retry and recovery
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=300)
    
    # Dependencies
    depends_on_jobs = Column(JSON)  # List of job IDs this job depends on
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

class DataQualityMetric(Base):
    __tablename__ = "data_quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    quality_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"DQ-{uuid.uuid4().hex[:8].upper()}")
    
    # Data source identification
    source_table = Column(String(255), nullable=False)
    source_column = Column(String(255))
    data_category = Column(String(100))  # risks, assets, compliance, etc.
    
    # Quality dimensions
    completeness = Column(Float)  # % of non-null values
    accuracy = Column(Float)  # % of values passing validation rules
    consistency = Column(Float)  # % of values consistent with related data
    timeliness = Column(Float)  # How current the data is
    validity = Column(Float)  # % of values matching expected format/range
    
    # Quality assessment details
    total_records = Column(Integer)
    null_count = Column(Integer)
    invalid_count = Column(Integer)
    duplicate_count = Column(Integer)
    outlier_count = Column(Integer)
    
    # Quality rules and validation
    validation_rules = Column(JSON)  # Rules used for quality assessment
    quality_issues = Column(JSON)  # Specific issues found
    recommendations = Column(JSON)  # Recommendations for improvement
    
    # Timestamps
    assessed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)