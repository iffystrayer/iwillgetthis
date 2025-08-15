from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Enums matching the model enums
class ModelType(str, Enum):
    RISK_PREDICTION = "risk_prediction"
    THREAT_DETECTION = "threat_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    COMPLIANCE_FORECASTING = "compliance_forecasting"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    INCIDENT_PREDICTION = "incident_prediction"
    ASSET_RISK_SCORING = "asset_risk_scoring"
    CONTROL_EFFECTIVENESS = "control_effectiveness"
    BUSINESS_IMPACT = "business_impact"
    TREND_ANALYSIS = "trend_analysis"


class ModelStatus(str, Enum):
    TRAINING = "training"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    TESTING = "testing"


class PredictionConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ACKNOWLEDGED = "acknowledged"


class DataSource(str, Enum):
    RISK_REGISTER = "risk_register"
    ASSET_INVENTORY = "asset_inventory"
    VULNERABILITY_SCANS = "vulnerability_scans"
    INCIDENT_LOGS = "incident_logs"
    COMPLIANCE_DATA = "compliance_data"
    AUDIT_REPORTS = "audit_reports"
    THREAT_INTELLIGENCE = "threat_intelligence"
    SECURITY_EVENTS = "security_events"
    USER_BEHAVIOR = "user_behavior"
    NETWORK_TRAFFIC = "network_traffic"


# AI Model schemas
class AIModelBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    model_type: ModelType
    algorithm: Optional[str] = Field(None, max_length=100)
    version: str = Field("1.0", max_length=20)
    training_data_sources: Optional[List[DataSource]] = None
    feature_columns: Optional[List[str]] = None
    target_column: Optional[str] = Field(None, max_length=100)
    training_parameters: Optional[Dict[str, Any]] = None
    prediction_threshold: float = 0.5
    is_production: bool = False
    auto_retrain: bool = True
    retrain_frequency_days: int = 30


class AIModelCreate(AIModelBase):
    pass


class AIModelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    algorithm: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=20)
    status: Optional[ModelStatus] = None
    training_parameters: Optional[Dict[str, Any]] = None
    prediction_threshold: Optional[float] = None
    is_production: Optional[bool] = None
    auto_retrain: Optional[bool] = None
    retrain_frequency_days: Optional[int] = None


class AIModelResponse(AIModelBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: ModelStatus
    created_by_id: int
    accuracy_score: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc_score: Optional[float] = None
    mean_squared_error: Optional[float] = None
    r2_score: Optional[float] = None
    trained_at: Optional[datetime] = None
    last_evaluated_at: Optional[datetime] = None
    next_retrain_date: Optional[datetime] = None
    model_path: Optional[str] = None
    feature_importance: Optional[Dict[str, float]] = None
    model_metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# AI Prediction schemas
class AIPredictionBase(BaseModel):
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    prediction_type: str = Field(..., max_length=100)
    predicted_value: Optional[float] = None
    predicted_category: Optional[str] = Field(None, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: PredictionConfidence = PredictionConfidence.MEDIUM
    input_features: Optional[Dict[str, Any]] = None
    prediction_reason: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    risk_level: Optional[str] = Field(None, max_length=20)
    impact_assessment: Optional[str] = None
    likelihood_assessment: Optional[str] = None
    prediction_horizon_days: Optional[int] = None
    prediction_metadata: Optional[Dict[str, Any]] = None


class AIPredictionCreate(AIPredictionBase):
    model_id: int


class AIPredictionUpdate(BaseModel):
    predicted_value: Optional[float] = None
    predicted_category: Optional[str] = Field(None, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: Optional[PredictionConfidence] = None
    prediction_reason: Optional[str] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    risk_level: Optional[str] = Field(None, max_length=20)
    actual_outcome: Optional[float] = None
    prediction_metadata: Optional[Dict[str, Any]] = None


class AIPredictionResponse(AIPredictionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    model_id: int
    prediction_date: datetime
    valid_until: Optional[datetime] = None
    actual_outcome: Optional[float] = None
    outcome_recorded_at: Optional[datetime] = None
    prediction_accuracy: Optional[float] = None
    created_at: datetime


# Model Evaluation schemas
class ModelEvaluationBase(BaseModel):
    evaluation_name: Optional[str] = Field(None, max_length=255)
    evaluation_type: str = Field(..., max_length=50)
    test_data_size: Optional[int] = None
    test_data_period_start: Optional[datetime] = None
    test_data_period_end: Optional[datetime] = None
    recommendations: Optional[str] = None
    requires_retraining: bool = False


class ModelEvaluationCreate(ModelEvaluationBase):
    model_id: int
    evaluated_by_id: int


class ModelEvaluationUpdate(BaseModel):
    evaluation_name: Optional[str] = Field(None, max_length=255)
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    recommendations: Optional[str] = None
    requires_retraining: Optional[bool] = None


class ModelEvaluationResponse(ModelEvaluationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    model_id: int
    evaluated_by_id: Optional[int] = None
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    mean_squared_error: Optional[float] = None
    r2_score: Optional[float] = None
    performance_change: Optional[float] = None
    performance_trend: Optional[str] = Field(None, max_length=20)
    confusion_matrix: Optional[Dict[str, Any]] = None
    classification_report: Optional[Dict[str, Any]] = None
    feature_importance_changes: Optional[Dict[str, float]] = None
    evaluation_results: Optional[Dict[str, Any]] = None
    created_at: datetime


# AI Alert schemas
class AIAlertBase(BaseModel):
    alert_type: str = Field(..., max_length=100)
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    severity: AlertSeverity
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    priority: int = Field(3, ge=1, le=5)
    trigger_condition: Optional[str] = None
    threshold_exceeded: Optional[float] = None
    anomaly_score: Optional[float] = None
    affected_entity_type: Optional[str] = Field(None, max_length=50)
    affected_entity_id: Optional[int] = None
    affected_entities: Optional[List[Dict[str, Any]]] = None
    ai_analysis: Optional[str] = None
    root_cause_analysis: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    recommended_actions: Optional[List[str]] = None
    remediation_steps: Optional[str] = None
    business_impact: Optional[str] = None
    urgency_justification: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class AIAlertCreate(AIAlertBase):
    model_id: Optional[int] = None
    prediction_id: Optional[int] = None


class AIAlertUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[AlertStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    assigned_to_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    resolution_actions_taken: Optional[List[str]] = None
    false_positive_reason: Optional[str] = None


class AIAlertResponse(AIAlertBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    model_id: Optional[int] = None
    prediction_id: Optional[int] = None
    status: AlertStatus
    first_detected_at: datetime
    last_updated_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assigned_to_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    resolution_actions_taken: Optional[List[str]] = None
    false_positive_reason: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# AI Insight schemas
class AIInsightBase(BaseModel):
    insight_type: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    title: str = Field(..., max_length=500)
    summary: str
    detailed_analysis: Optional[str] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    impact_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    urgency_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    data_sources: Optional[List[DataSource]] = None
    analysis_period_start: Optional[datetime] = None
    analysis_period_end: Optional[datetime] = None
    key_metrics: Optional[Dict[str, Any]] = None
    supporting_data: Optional[Dict[str, Any]] = None
    visualizations: Optional[Dict[str, Any]] = None
    related_entities: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    potential_savings: Optional[str] = Field(None, max_length=100)
    risk_reduction: Optional[str] = Field(None, max_length=100)
    implementation_effort: Optional[str] = Field(None, max_length=50)


class AIInsightCreate(AIInsightBase):
    pass


class AIInsightUpdate(BaseModel):
    summary: Optional[str] = None
    detailed_analysis: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    reviewed_by_id: Optional[int] = None
    review_notes: Optional[str] = None


class AIInsightResponse(AIInsightBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    view_count: int
    bookmark_count: int
    sharing_count: int
    generated_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool


# Dataset schemas
class AIDatasetBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    dataset_type: str = Field(..., max_length=50)
    data_source: Optional[DataSource] = None
    total_records: Optional[int] = None
    features_count: Optional[int] = None
    missing_values_percentage: Optional[float] = None
    data_quality_score: Optional[float] = None
    data_start_date: Optional[datetime] = None
    data_end_date: Optional[datetime] = None
    schema_definition: Optional[Dict[str, Any]] = None
    feature_statistics: Optional[Dict[str, Any]] = None
    storage_path: Optional[str] = Field(None, max_length=500)
    file_format: Optional[str] = Field(None, max_length=50)
    compressed_size_mb: Optional[float] = None
    version: str = Field("1.0", max_length=20)
    transformation_steps: Optional[List[str]] = None


class AIDatasetCreate(AIDatasetBase):
    created_by_id: int


class AIDatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    data_quality_score: Optional[float] = None
    schema_definition: Optional[Dict[str, Any]] = None
    feature_statistics: Optional[Dict[str, Any]] = None


class AIDatasetResponse(AIDatasetBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    parent_dataset_id: Optional[int] = None
    data_distribution: Optional[Dict[str, Any]] = None
    outlier_analysis: Optional[Dict[str, Any]] = None
    access_permissions: Optional[Dict[str, Any]] = None
    used_by_models: Optional[List[int]] = None
    last_accessed_at: Optional[datetime] = None
    access_count: int
    created_by_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Experiment schemas
class AIExperimentBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    experiment_type: str = Field(..., max_length=50)
    objective: str = Field(..., max_length=100)
    models_tested: Optional[List[Dict[str, Any]]] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    feature_sets: Optional[List[str]] = None
    insights: Optional[str] = None
    recommendations: Optional[str] = None
    random_seed: Optional[int] = None
    environment_info: Optional[Dict[str, Any]] = None
    code_version: Optional[str] = Field(None, max_length=100)


class AIExperimentCreate(AIExperimentBase):
    started_by_id: int


class AIExperimentUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    best_model_config: Optional[Dict[str, Any]] = None
    best_performance_score: Optional[float] = None
    all_results: Optional[Dict[str, Any]] = None
    insights: Optional[str] = None
    recommendations: Optional[str] = None
    completed_at: Optional[datetime] = None


class AIExperimentResponse(AIExperimentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    best_model_config: Optional[Dict[str, Any]] = None
    best_performance_score: Optional[float] = None
    all_results: Optional[Dict[str, Any]] = None
    feature_importance_ranking: Optional[Dict[str, float]] = None
    started_by_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    compute_time_minutes: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    storage_used_mb: Optional[float] = None
    is_active: bool
    created_at: datetime


# Request/Response schemas for complex operations
class ModelTrainingRequest(BaseModel):
    model_id: int
    dataset_id: int
    training_config: Optional[Dict[str, Any]] = None
    validation_split: float = Field(0.2, ge=0.1, le=0.5)
    cross_validation_folds: int = Field(5, ge=2, le=10)
    early_stopping: bool = True


class PredictionRequest(BaseModel):
    model_id: int
    entity_type: str
    entity_id: int
    input_features: Dict[str, Any]
    prediction_horizon_days: Optional[int] = None
    explain_prediction: bool = False


class BulkPredictionRequest(BaseModel):
    model_id: int
    entities: List[Dict[str, Any]]  # List of {entity_type, entity_id, input_features}
    prediction_horizon_days: Optional[int] = None
    batch_size: int = Field(100, ge=1, le=1000)


class ModelComparisonRequest(BaseModel):
    model_ids: List[int] = Field(..., min_length=2, max_length=10)
    test_dataset_id: Optional[int] = None
    metrics: List[str] = ["accuracy", "precision", "recall", "f1_score"]


class AnomalyDetectionRequest(BaseModel):
    entity_type: str
    entity_ids: Optional[List[int]] = None
    time_range_start: datetime
    time_range_end: datetime
    sensitivity: float = Field(0.8, ge=0.1, le=1.0)
    features: Optional[List[str]] = None


class RiskForecastRequest(BaseModel):
    entity_type: str = "risk"
    time_horizon_days: int = Field(30, ge=1, le=365)
    risk_categories: Optional[List[str]] = None
    confidence_threshold: float = Field(0.7, ge=0.1, le=1.0)
    include_mitigation_scenarios: bool = False


# Response schemas for analytics operations
class ModelPerformanceMetrics(BaseModel):
    model_id: int
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    confusion_matrix: Optional[Dict[str, Any]] = None
    feature_importance: Optional[Dict[str, float]] = None
    evaluation_date: datetime


class RiskForecastResponse(BaseModel):
    forecast_date: datetime
    forecast_horizon_days: int
    total_risks_predicted: int
    risk_level_distribution: Dict[str, int]
    high_risk_entities: List[Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    confidence_intervals: Dict[str, Any]
    recommendations: List[str]


class AnomalyDetectionResponse(BaseModel):
    analysis_date: datetime
    entities_analyzed: int
    anomalies_detected: int
    anomaly_details: List[Dict[str, Any]]
    normal_behavior_baseline: Dict[str, Any]
    sensitivity_used: float
    false_positive_probability: Optional[float] = None


class AIAnalyticsDashboard(BaseModel):
    summary: Dict[str, Any]
    model_performance_overview: List[ModelPerformanceMetrics]
    recent_predictions: List[AIPredictionResponse]
    active_alerts: List[AIAlertResponse]
    trending_insights: List[AIInsightResponse]
    system_health: Dict[str, Any]


# Filter and query schemas
class AIAnalyticsFilter(BaseModel):
    model_types: Optional[List[ModelType]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_levels: Optional[List[str]] = None
    entity_types: Optional[List[str]] = None
    alert_severities: Optional[List[AlertSeverity]] = None
    categories: Optional[List[str]] = None