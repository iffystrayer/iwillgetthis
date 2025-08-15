from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum
from database import Base
import enum
from datetime import datetime
from typing import Dict, Any, List, Optional


class ModelType(enum.Enum):
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


class ModelStatus(enum.Enum):
    TRAINING = "training"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    TESTING = "testing"


class PredictionConfidence(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class AlertSeverity(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ACKNOWLEDGED = "acknowledged"


class DataSource(enum.Enum):
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


class AIModel(Base):
    """Machine Learning models for predictive analytics"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Model classification
    model_type = Column(SQLEnum(ModelType), nullable=False)
    algorithm = Column(String(100))  # e.g., "random_forest", "neural_network", "gradient_boosting"
    version = Column(String(20), default="1.0")
    
    # Model status and metadata
    status = Column(SQLEnum(ModelStatus), default=ModelStatus.TRAINING)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Training configuration
    training_data_sources = Column(JSON)  # List of data sources used for training
    feature_columns = Column(JSON)  # List of feature columns used
    target_column = Column(String(100))  # Target prediction column
    training_parameters = Column(JSON)  # Model hyperparameters
    
    # Model performance metrics
    accuracy_score = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    roc_auc_score = Column(Float)
    mean_squared_error = Column(Float)
    r2_score = Column(Float)
    
    # Model lifecycle
    trained_at = Column(DateTime(timezone=True))
    last_evaluated_at = Column(DateTime(timezone=True))
    next_retrain_date = Column(DateTime(timezone=True))
    
    # Model artifacts
    model_path = Column(String(500))  # Path to saved model file
    feature_importance = Column(JSON)  # Feature importance scores
    model_metadata = Column(JSON)  # Additional model metadata
    
    # Configuration
    prediction_threshold = Column(Float, default=0.5)
    is_production = Column(Boolean, default=False)
    auto_retrain = Column(Boolean, default=True)
    retrain_frequency_days = Column(Integer, default=30)
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    predictions = relationship("AIPrediction", back_populates="model")
    evaluations = relationship("ModelEvaluation", back_populates="model")
    alerts = relationship("AIAlert", back_populates="model")


class AIPrediction(Base):
    """Individual predictions made by AI models"""
    __tablename__ = "ai_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    
    # Prediction details
    entity_type = Column(String(50), nullable=False)  # "risk", "asset", "incident", etc.
    entity_id = Column(Integer, nullable=False)
    prediction_type = Column(String(100), nullable=False)
    
    # Prediction results
    predicted_value = Column(Float)  # Numeric prediction
    predicted_category = Column(String(100))  # Categorical prediction
    confidence_score = Column(Float)  # 0.0 to 1.0
    confidence_level = Column(SQLEnum(PredictionConfidence), default=PredictionConfidence.MEDIUM)
    
    # Prediction context
    input_features = Column(JSON)  # Features used for this prediction
    prediction_reason = Column(Text)  # AI-generated explanation
    contributing_factors = Column(JSON)  # List of factors that influenced prediction
    
    # Risk assessment
    risk_score = Column(Float)  # 0.0 to 10.0
    risk_level = Column(String(20))  # "low", "medium", "high", "critical"
    impact_assessment = Column(Text)
    likelihood_assessment = Column(Text)
    
    # Temporal data
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    prediction_horizon_days = Column(Integer)  # How far into future this predicts
    valid_until = Column(DateTime(timezone=True))
    
    # Validation and feedback
    actual_outcome = Column(Float)  # Actual outcome (for model evaluation)
    outcome_recorded_at = Column(DateTime(timezone=True))
    prediction_accuracy = Column(Float)  # How accurate this specific prediction was
    
    # Metadata
    prediction_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    model = relationship("AIModel", back_populates="predictions")


class ModelEvaluation(Base):
    """Model performance evaluations over time"""
    __tablename__ = "model_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    
    # Evaluation details
    evaluation_name = Column(String(255))
    evaluation_type = Column(String(50))  # "scheduled", "manual", "post_incident"
    evaluated_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    mean_squared_error = Column(Float)
    r2_score = Column(Float)
    
    # Evaluation dataset
    test_data_size = Column(Integer)
    test_data_period_start = Column(DateTime(timezone=True))
    test_data_period_end = Column(DateTime(timezone=True))
    
    # Comparison with previous evaluations
    performance_change = Column(Float)  # Percentage change from last evaluation
    performance_trend = Column(String(20))  # "improving", "stable", "declining"
    
    # Detailed results
    confusion_matrix = Column(JSON)
    classification_report = Column(JSON)
    feature_importance_changes = Column(JSON)
    evaluation_results = Column(JSON)
    
    # Recommendations
    recommendations = Column(Text)
    requires_retraining = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    model = relationship("AIModel", back_populates="evaluations")
    evaluated_by = relationship("User", foreign_keys=[evaluated_by_id])


class AIAlert(Base):
    """AI-generated alerts and recommendations"""
    __tablename__ = "ai_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    prediction_id = Column(Integer, ForeignKey("ai_predictions.id"))
    
    # Alert details
    alert_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Alert classification
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    category = Column(String(100))  # "risk", "compliance", "security", "operational"
    subcategory = Column(String(100))
    
    # Alert status
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN)
    priority = Column(Integer, default=3)  # 1 (highest) to 5 (lowest)
    
    # Alert triggers
    trigger_condition = Column(Text)
    threshold_exceeded = Column(Float)
    anomaly_score = Column(Float)
    
    # Affected entities
    affected_entity_type = Column(String(50))  # "asset", "risk", "user", etc.
    affected_entity_id = Column(Integer)
    affected_entities = Column(JSON)  # List of multiple affected entities
    
    # AI insights
    ai_analysis = Column(Text)
    root_cause_analysis = Column(Text)
    confidence_score = Column(Float)
    
    # Recommendations
    recommended_actions = Column(JSON)  # List of recommended actions
    remediation_steps = Column(Text)
    business_impact = Column(Text)
    urgency_justification = Column(Text)
    
    # Timeline
    first_detected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True))
    
    # Resolution
    resolution_notes = Column(Text)
    resolution_actions_taken = Column(JSON)
    false_positive_reason = Column(Text)
    
    # Metadata
    tags = Column(JSON)
    custom_fields = Column(JSON)
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    model = relationship("AIModel", back_populates="alerts")
    prediction = relationship("AIPrediction", foreign_keys=[prediction_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])


class AIInsight(Base):
    """AI-generated insights and recommendations"""
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Insight classification
    insight_type = Column(String(100), nullable=False)
    category = Column(String(100))  # "trend", "pattern", "anomaly", "optimization"
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    detailed_analysis = Column(Text)
    
    # Insight scoring
    relevance_score = Column(Float)  # How relevant this insight is
    confidence_score = Column(Float)  # AI confidence in this insight
    impact_score = Column(Float)  # Potential business impact
    urgency_score = Column(Float)  # How urgently this should be addressed
    
    # Data sources and analysis
    data_sources = Column(JSON)  # List of data sources analyzed
    analysis_period_start = Column(DateTime(timezone=True))
    analysis_period_end = Column(DateTime(timezone=True))
    key_metrics = Column(JSON)  # Key metrics that led to this insight
    
    # Supporting evidence
    supporting_data = Column(JSON)  # Data points supporting this insight
    visualizations = Column(JSON)  # Chart/graph configurations
    related_entities = Column(JSON)  # Related risks, assets, etc.
    
    # Recommendations
    recommendations = Column(JSON)  # List of actionable recommendations
    potential_savings = Column(String(100))  # Estimated cost savings
    risk_reduction = Column(String(100))  # Estimated risk reduction
    implementation_effort = Column(String(50))  # "low", "medium", "high"
    
    # Lifecycle
    status = Column(String(50), default="active")  # "active", "implemented", "dismissed"
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    
    # Tracking
    view_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    sharing_count = Column(Integer, default=0)
    
    # Audit fields
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # When insight becomes stale
    is_active = Column(Boolean, default=True)
    
    # Relationships
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])


class AIDataset(Base):
    """Datasets used for training and evaluation"""
    __tablename__ = "ai_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Dataset details
    dataset_type = Column(String(50))  # "training", "validation", "test", "production"
    data_source = Column(SQLEnum(DataSource))
    
    # Data quality metrics
    total_records = Column(Integer)
    features_count = Column(Integer)
    missing_values_percentage = Column(Float)
    data_quality_score = Column(Float)
    
    # Time range
    data_start_date = Column(DateTime(timezone=True))
    data_end_date = Column(DateTime(timezone=True))
    
    # Schema and metadata
    schema_definition = Column(JSON)
    feature_statistics = Column(JSON)
    data_distribution = Column(JSON)
    outlier_analysis = Column(JSON)
    
    # Storage and access
    storage_path = Column(String(500))
    file_format = Column(String(50))  # "csv", "parquet", "json", "database"
    compressed_size_mb = Column(Float)
    access_permissions = Column(JSON)
    
    # Lineage and versioning
    version = Column(String(20), default="1.0")
    parent_dataset_id = Column(Integer, ForeignKey("ai_datasets.id"))
    transformation_steps = Column(JSON)
    
    # Usage tracking
    used_by_models = Column(JSON)  # List of model IDs using this dataset
    last_accessed_at = Column(DateTime(timezone=True))
    access_count = Column(Integer, default=0)
    
    # Audit fields
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    parent_dataset = relationship("AIDataset", remote_side=[id])


class AIExperiment(Base):
    """Machine learning experiments and model comparisons"""
    __tablename__ = "ai_experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Experiment details
    experiment_type = Column(String(50))  # "model_comparison", "hyperparameter_tuning", "feature_selection"
    objective = Column(String(100))  # Primary metric to optimize
    
    # Experiment configuration
    models_tested = Column(JSON)  # List of model configurations tested
    hyperparameters = Column(JSON)  # Hyperparameter ranges tested
    feature_sets = Column(JSON)  # Different feature combinations tested
    
    # Results
    best_model_config = Column(JSON)
    best_performance_score = Column(Float)
    all_results = Column(JSON)  # All experiment results
    
    # Analysis
    insights = Column(Text)
    recommendations = Column(Text)
    feature_importance_ranking = Column(JSON)
    
    # Experiment lifecycle
    started_by_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(50), default="running")  # "running", "completed", "failed", "cancelled"
    
    # Resources used
    compute_time_minutes = Column(Integer)
    memory_usage_mb = Column(Float)
    storage_used_mb = Column(Float)
    
    # Reproducibility
    random_seed = Column(Integer)
    environment_info = Column(JSON)
    code_version = Column(String(100))
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    started_by = relationship("User", foreign_keys=[started_by_id])