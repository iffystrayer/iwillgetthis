"""AI Analytics Router - API endpoints for predictive analytics and ML models"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.ai_analytics import (
    AIModel, AIPrediction, ModelEvaluation, AIAlert, AIInsight,
    AIDataset, AIExperiment, ModelType, ModelStatus, AlertSeverity
)
from schemas.ai_analytics import (
    # Model schemas
    AIModelCreate, AIModelUpdate, AIModelResponse,
    # Prediction schemas
    AIPredictionCreate, AIPredictionUpdate, AIPredictionResponse,
    PredictionRequest, BulkPredictionRequest,
    # Evaluation schemas
    ModelEvaluationCreate, ModelEvaluationUpdate, ModelEvaluationResponse,
    # Alert schemas
    AIAlertCreate, AIAlertUpdate, AIAlertResponse,
    # Insight schemas
    AIInsightCreate, AIInsightUpdate, AIInsightResponse,
    # Dataset schemas
    AIDatasetCreate, AIDatasetUpdate, AIDatasetResponse,
    # Experiment schemas
    AIExperimentCreate, AIExperimentUpdate, AIExperimentResponse,
    # Request schemas
    ModelTrainingRequest, ModelComparisonRequest,
    AnomalyDetectionRequest, RiskForecastRequest,
    # Response schemas
    ModelPerformanceMetrics, RiskForecastResponse, AnomalyDetectionResponse,
    AIAnalyticsDashboard, AIAnalyticsFilter
)
from auth import get_current_active_user
from services.ai_analytics_service import AIAnalyticsService

router = APIRouter()

def get_ai_analytics_service(db: Session = Depends(get_db)) -> AIAnalyticsService:
    """Get AI analytics service instance"""
    return AIAnalyticsService(db)

# =====================
# AI MODELS MANAGEMENT
# =====================

@router.post("/models", response_model=AIModelResponse)
async def create_ai_model(
    model: AIModelCreate,
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Create a new AI model configuration."""
    
    try:
        ai_model = await ai_service.create_risk_prediction_model(
            name=model.name,
            description=model.description,
            algorithm=model.algorithm,
            feature_columns=model.feature_columns or [],
            target_column=model.target_column,
            created_by_id=current_user.id,
            training_parameters=model.training_parameters
        )
        return ai_model
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create AI model: {str(e)}"
        )

@router.get("/models", response_model=List[AIModelResponse])
async def get_ai_models(
    model_type: Optional[ModelType] = Query(None),
    status_filter: Optional[ModelStatus] = Query(None),
    active_only: bool = Query(True),
    limit: Optional[int] = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all AI models with optional filtering."""
    
    query = db.query(AIModel)
    
    if model_type:
        query = query.filter(AIModel.model_type == model_type)
    
    if status_filter:
        query = query.filter(AIModel.status == status_filter)
    
    if active_only:
        query = query.filter(AIModel.is_active == True)
    
    query = query.order_by(desc(AIModel.created_at))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

@router.get("/models/{model_id}", response_model=AIModelResponse)
async def get_ai_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific AI model."""
    
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI model not found"
        )
    
    return model

@router.put("/models/{model_id}", response_model=AIModelResponse)
async def update_ai_model(
    model_id: int,
    model_update: AIModelUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an AI model configuration."""
    
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI model not found"
        )
    
    update_data = model_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    
    return model

@router.post("/models/{model_id}/train")
async def train_ai_model(
    model_id: int,
    training_request: ModelTrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Train an AI model."""
    
    try:
        # Start training in background
        background_tasks.add_task(
            ai_service.train_predictive_model,
            model_id,
            training_request.dataset_id,
            training_request.validation_split
        )
        
        return {"message": "Model training started", "model_id": model_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start model training: {str(e)}"
        )

@router.post("/models/{model_id}/evaluate", response_model=ModelEvaluationResponse)
async def evaluate_ai_model(
    model_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Evaluate an AI model performance."""
    
    try:
        evaluation = await ai_service.evaluate_model(
            model_id=model_id,
            test_data_period_start=start_date,
            test_data_period_end=end_date,
            evaluated_by_id=current_user.id
        )
        return evaluation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model evaluation failed: {str(e)}"
        )

# =====================
# PREDICTIONS
# =====================

@router.post("/predictions", response_model=AIPredictionResponse)
async def create_prediction(
    prediction_request: PredictionRequest,
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Generate a prediction using an AI model."""
    
    try:
        prediction = await ai_service.generate_risk_prediction(
            model_id=prediction_request.model_id,
            entity_type=prediction_request.entity_type,
            entity_id=prediction_request.entity_id,
            input_features=prediction_request.input_features,
            prediction_horizon_days=prediction_request.prediction_horizon_days or 30
        )
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction generation failed: {str(e)}"
        )

@router.post("/predictions/bulk")
async def create_bulk_predictions(
    bulk_request: BulkPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Generate bulk predictions."""
    
    try:
        # Process predictions in background
        def process_bulk_predictions():
            for entity in bulk_request.entities:
                ai_service.generate_risk_prediction(
                    model_id=bulk_request.model_id,
                    entity_type=entity["entity_type"],
                    entity_id=entity["entity_id"],
                    input_features=entity["input_features"],
                    prediction_horizon_days=bulk_request.prediction_horizon_days or 30
                )
        
        background_tasks.add_task(process_bulk_predictions)
        
        return {
            "message": "Bulk prediction generation started",
            "entity_count": len(bulk_request.entities)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bulk prediction failed: {str(e)}"
        )

@router.get("/predictions", response_model=List[AIPredictionResponse])
async def get_predictions(
    model_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get predictions with optional filtering."""
    
    query = db.query(AIPrediction)
    
    if model_id:
        query = query.filter(AIPrediction.model_id == model_id)
    
    if entity_type:
        query = query.filter(AIPrediction.entity_type == entity_type)
    
    if entity_id:
        query = query.filter(AIPrediction.entity_id == entity_id)
    
    if start_date:
        query = query.filter(AIPrediction.prediction_date >= start_date)
    
    if end_date:
        query = query.filter(AIPrediction.prediction_date <= end_date)
    
    query = query.order_by(desc(AIPrediction.prediction_date))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

@router.put("/predictions/{prediction_id}/outcome", response_model=AIPredictionResponse)
async def update_prediction_outcome(
    prediction_id: int,
    actual_outcome: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update prediction with actual outcome for model validation."""
    
    prediction = db.query(AIPrediction).filter(AIPrediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    prediction.actual_outcome = actual_outcome
    prediction.outcome_recorded_at = datetime.utcnow()
    
    # Calculate prediction accuracy
    if prediction.predicted_value:
        prediction.prediction_accuracy = 1.0 - abs(
            (prediction.predicted_value - actual_outcome) / max(prediction.predicted_value, actual_outcome)
        )
    
    db.commit()
    db.refresh(prediction)
    
    return prediction

# =====================
# ANOMALY DETECTION
# =====================

@router.post("/anomalies/detect", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Detect anomalies in entity behavior."""
    
    try:
        anomalies = await ai_service.detect_anomalies(
            entity_type=request.entity_type,
            time_range_start=request.time_range_start,
            time_range_end=request.time_range_end,
            sensitivity=request.sensitivity
        )
        
        return AnomalyDetectionResponse(
            analysis_date=datetime.utcnow(),
            entities_analyzed=len(request.entity_ids) if request.entity_ids else 0,
            anomalies_detected=len(anomalies),
            anomaly_details=anomalies,
            normal_behavior_baseline={},
            sensitivity_used=request.sensitivity
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Anomaly detection failed: {str(e)}"
        )

# =====================
# RISK FORECASTING
# =====================

@router.post("/forecasts/risk", response_model=RiskForecastResponse)
async def generate_risk_forecast(
    request: RiskForecastRequest,
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Generate risk forecasts."""
    
    try:
        # This would use trained models to forecast risk trends
        # For now, return a simulated response
        forecast = RiskForecastResponse(
            forecast_date=datetime.utcnow(),
            forecast_horizon_days=request.time_horizon_days,
            total_risks_predicted=50,  # Simulated
            risk_level_distribution={"high": 5, "medium": 25, "low": 20},
            high_risk_entities=[],
            trend_analysis={"direction": "increasing", "confidence": 0.7},
            confidence_intervals={"lower": 0.2, "upper": 0.8},
            recommendations=["Monitor high-risk entities closely", "Review mitigation strategies"]
        )
        
        return forecast
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Risk forecasting failed: {str(e)}"
        )

# =====================
# AI ALERTS
# =====================

@router.get("/alerts", response_model=List[AIAlertResponse])
async def get_ai_alerts(
    status_filter: Optional[str] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    limit: Optional[int] = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated alerts."""
    
    query = db.query(AIAlert).filter(AIAlert.is_active == True)
    
    if status_filter:
        query = query.filter(AIAlert.status == status_filter)
    
    if severity:
        query = query.filter(AIAlert.severity == severity)
    
    query = query.order_by(desc(AIAlert.first_detected_at))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

@router.put("/alerts/{alert_id}/acknowledge", response_model=AIAlertResponse)
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Acknowledge an AI alert."""
    
    alert = db.query(AIAlert).filter(AIAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    alert.assigned_to_id = current_user.id
    
    db.commit()
    db.refresh(alert)
    
    return alert

# =====================
# AI INSIGHTS
# =====================

@router.get("/insights", response_model=List[AIInsightResponse])
async def get_ai_insights(
    category: Optional[str] = Query(None),
    days_back: int = Query(30, le=365),
    limit: Optional[int] = Query(20, le=50),
    current_user: User = Depends(get_current_active_user),
    ai_service: AIAnalyticsService = Depends(get_ai_analytics_service)
):
    """Get AI-generated insights."""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days_back)
        end_date = datetime.utcnow()
        
        insights = await ai_service.generate_insights(
            analysis_period_start=start_date,
            analysis_period_end=end_date
        )
        
        if category:
            insights = [i for i in insights if i.category == category]
        
        # Sort by relevance score
        insights.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        
        return insights[:limit] if limit else insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )

# =====================
# MODEL COMPARISON
# =====================

@router.post("/models/compare", response_model=List[ModelPerformanceMetrics])
async def compare_models(
    request: ModelComparisonRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Compare performance of multiple AI models."""
    
    models = db.query(AIModel).filter(AIModel.id.in_(request.model_ids)).all()
    
    if len(models) != len(request.model_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more models not found"
        )
    
    metrics = []
    for model in models:
        model_metrics = ModelPerformanceMetrics(
            model_id=model.id,
            model_name=model.name,
            accuracy=model.accuracy_score,
            precision=model.precision_score,
            recall=model.recall_score,
            f1_score=model.f1_score,
            roc_auc=model.roc_auc_score,
            feature_importance=model.feature_importance,
            evaluation_date=model.last_evaluated_at or model.trained_at or model.created_at
        )
        metrics.append(model_metrics)
    
    # Sort by accuracy (descending)
    metrics.sort(key=lambda x: x.accuracy or 0, reverse=True)
    
    return metrics

# =====================
# ANALYTICS DASHBOARD
# =====================

@router.get("/dashboard", response_model=AIAnalyticsDashboard)
async def get_ai_analytics_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI analytics dashboard data."""
    
    # Get summary statistics
    total_models = db.query(AIModel).filter(AIModel.is_active == True).count()
    active_models = db.query(AIModel).filter(
        and_(AIModel.is_active == True, AIModel.status == ModelStatus.ACTIVE)
    ).count()
    total_predictions = db.query(AIPrediction).count()
    active_alerts = db.query(AIAlert).filter(AIAlert.is_active == True).count()
    
    # Get recent predictions
    recent_predictions = db.query(AIPrediction).order_by(
        desc(AIPrediction.prediction_date)
    ).limit(10).all()
    
    # Get active alerts
    alerts = db.query(AIAlert).filter(
        AIAlert.is_active == True
    ).order_by(desc(AIAlert.first_detected_at)).limit(10).all()
    
    # Get recent insights
    insights = db.query(AIInsight).filter(
        AIInsight.is_active == True
    ).order_by(desc(AIInsight.generated_at)).limit(5).all()
    
    # Get top performing models
    top_models = db.query(AIModel).filter(
        and_(AIModel.is_active == True, AIModel.accuracy_score.isnot(None))
    ).order_by(desc(AIModel.accuracy_score)).limit(5).all()
    
    model_performance = [
        ModelPerformanceMetrics(
            model_id=model.id,
            model_name=model.name,
            accuracy=model.accuracy_score,
            precision=model.precision_score,
            recall=model.recall_score,
            f1_score=model.f1_score,
            roc_auc=model.roc_auc_score,
            evaluation_date=model.last_evaluated_at or model.created_at
        )
        for model in top_models
    ]
    
    dashboard = AIAnalyticsDashboard(
        summary={
            "total_models": total_models,
            "active_models": active_models,
            "total_predictions": total_predictions,
            "active_alerts": active_alerts,
            "model_accuracy_avg": sum(m.accuracy or 0 for m in top_models) / len(top_models) if top_models else 0
        },
        model_performance_overview=model_performance,
        recent_predictions=recent_predictions,
        active_alerts=alerts,
        trending_insights=insights,
        system_health={
            "status": "healthy",
            "last_updated": datetime.utcnow(),
            "models_requiring_retrain": db.query(AIModel).filter(
                and_(
                    AIModel.is_active == True,
                    AIModel.next_retrain_date <= datetime.utcnow()
                )
            ).count()
        }
    )
    
    return dashboard