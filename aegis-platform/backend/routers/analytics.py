from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.analytics import (
    MetricDefinition, MetricValue, KPIConfiguration, Dashboard, DashboardWidget,
    ReportTemplate, GeneratedReport, PredictionConfiguration, PredictionResult,
    AnalyticsJob, DataQualityMetric
)
from schemas.analytics import (
    # Metric schemas
    MetricDefinitionCreate, MetricDefinitionUpdate, MetricDefinitionResponse,
    MetricValueCreate, MetricValueResponse,
    # KPI schemas
    KPIConfigurationCreate, KPIConfigurationUpdate, KPIConfigurationResponse,
    # Dashboard schemas
    DashboardCreate, DashboardUpdate, DashboardResponse,
    DashboardWidgetCreate, DashboardWidgetUpdate, DashboardWidgetResponse,
    # Report schemas
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateResponse,
    GeneratedReportCreate, GeneratedReportUpdate, GeneratedReportResponse,
    # Prediction schemas
    PredictionConfigurationCreate, PredictionConfigurationUpdate, PredictionConfigurationResponse,
    PredictionResultCreate, PredictionResultUpdate, PredictionResultResponse,
    # Analytics job schemas
    AnalyticsJobCreate, AnalyticsJobUpdate, AnalyticsJobResponse,
    # Data schemas
    DashboardData, ExecutiveSummary, ComplianceDashboard, SecurityDashboard,
    MetricSummary, KPISummary, AnalyticsInsight, RiskForecast,
    # Filter schemas
    MetricSearchFilter, TimeRangeFilter, AnalyticsQueryFilter,
    # Enums
    MetricTypeEnum, DashboardTypeEnum, ReportTypeEnum, TrendDirectionEnum
)
from auth import get_current_active_user
from analytics_engine import AdvancedAnalyticsEngine

router = APIRouter()

# Initialize analytics engine
analytics_engine = AdvancedAnalyticsEngine()

# =====================
# METRIC DEFINITIONS
# =====================

@router.post("/metrics", response_model=MetricDefinitionResponse)
async def create_metric_definition(
    metric: MetricDefinitionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new metric definition."""
    
    db_metric = MetricDefinition(
        **metric.dict(),
        created_by=current_user.username,
        updated_by=current_user.username
    )
    
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    
    return db_metric

@router.get("/metrics", response_model=List[MetricDefinitionResponse])
async def get_metric_definitions(
    filter_params: MetricSearchFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all metric definitions with optional filtering."""
    
    query = db.query(MetricDefinition)
    
    if filter_params.metric_type:
        query = query.filter(MetricDefinition.metric_type == filter_params.metric_type)
    
    if filter_params.category:
        query = query.filter(MetricDefinition.category == filter_params.category)
    
    if filter_params.active_only:
        query = query.filter(MetricDefinition.active == True)
    
    if filter_params.has_target is not None:
        if filter_params.has_target:
            query = query.filter(MetricDefinition.target_value.isnot(None))
        else:
            query = query.filter(MetricDefinition.target_value.is_(None))
    
    if filter_params.search_term:
        search = f"%{filter_params.search_term}%"
        query = query.filter(or_(
            MetricDefinition.name.ilike(search),
            MetricDefinition.description.ilike(search)
        ))
    
    query = query.offset(filter_params.offset or 0)
    
    if filter_params.limit:
        query = query.limit(filter_params.limit)
    
    return query.all()

@router.get("/metrics/{metric_id}", response_model=MetricDefinitionResponse)
async def get_metric_definition(
    metric_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific metric definition."""
    
    metric = db.query(MetricDefinition).filter(
        MetricDefinition.metric_id == metric_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric definition not found"
        )
    
    return metric

@router.put("/metrics/{metric_id}", response_model=MetricDefinitionResponse)
async def update_metric_definition(
    metric_id: str,
    metric_update: MetricDefinitionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a metric definition."""
    
    metric = db.query(MetricDefinition).filter(
        MetricDefinition.metric_id == metric_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric definition not found"
        )
    
    update_data = metric_update.dict(exclude_unset=True)
    update_data["updated_by"] = current_user.username
    
    for field, value in update_data.items():
        setattr(metric, field, value)
    
    db.commit()
    db.refresh(metric)
    
    return metric

@router.delete("/metrics/{metric_id}")
async def delete_metric_definition(
    metric_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a metric definition."""
    
    metric = db.query(MetricDefinition).filter(
        MetricDefinition.metric_id == metric_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric definition not found"
        )
    
    # Soft delete by setting active to False
    metric.active = False
    metric.updated_by = current_user.username
    
    db.commit()
    
    return {"message": "Metric definition deleted successfully"}

# =====================
# METRIC VALUES
# =====================

@router.post("/metrics/{metric_id}/values", response_model=MetricValueResponse)
async def create_metric_value(
    metric_id: str,
    value: MetricValueCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new metric value."""
    
    # Verify metric exists
    metric = db.query(MetricDefinition).filter(
        MetricDefinition.metric_id == metric_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric definition not found"
        )
    
    db_value = MetricValue(
        metric_definition_id=metric.id,
        **value.dict()
    )
    
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    
    return db_value

@router.get("/metrics/{metric_id}/values", response_model=List[MetricValueResponse])
async def get_metric_values(
    metric_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(100, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get metric values for a specific metric."""
    
    # Verify metric exists
    metric = db.query(MetricDefinition).filter(
        MetricDefinition.metric_id == metric_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric definition not found"
        )
    
    query = db.query(MetricValue).filter(
        MetricValue.metric_definition_id == metric.id
    )
    
    if start_date:
        query = query.filter(MetricValue.timestamp >= start_date)
    
    if end_date:
        query = query.filter(MetricValue.timestamp <= end_date)
    
    query = query.order_by(desc(MetricValue.timestamp))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

# =====================
# KPI CONFIGURATIONS
# =====================

@router.post("/kpis", response_model=KPIConfigurationResponse)
async def create_kpi_configuration(
    kpi: KPIConfigurationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new KPI configuration."""
    
    # Verify metric exists
    metric = db.query(MetricDefinition).filter(
        MetricDefinition.id == kpi.metric_definition_id
    ).first()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric definition not found"
        )
    
    db_kpi = KPIConfiguration(**kpi.dict())
    
    db.add(db_kpi)
    db.commit()
    db.refresh(db_kpi)
    
    return db_kpi

@router.get("/kpis", response_model=List[KPIConfigurationResponse])
async def get_kpi_configurations(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all KPI configurations."""
    
    query = db.query(KPIConfiguration)
    
    if active_only:
        query = query.filter(KPIConfiguration.active == True)
    
    return query.order_by(KPIConfiguration.display_order).all()

@router.get("/kpis/{kpi_id}", response_model=KPIConfigurationResponse)
async def get_kpi_configuration(
    kpi_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific KPI configuration."""
    
    kpi = db.query(KPIConfiguration).filter(
        KPIConfiguration.kpi_id == kpi_id
    ).first()
    
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI configuration not found"
        )
    
    return kpi

# =====================
# DASHBOARDS
# =====================

@router.post("/dashboards", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new dashboard."""
    
    db_dashboard = Dashboard(
        **dashboard.dict(),
        created_by=current_user.username,
        updated_by=current_user.username
    )
    
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    
    return db_dashboard

@router.get("/dashboards", response_model=List[DashboardResponse])
async def get_dashboards(
    dashboard_type: Optional[DashboardTypeEnum] = Query(None),
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all dashboards."""
    
    query = db.query(Dashboard)
    
    if dashboard_type:
        query = query.filter(Dashboard.dashboard_type == dashboard_type)
    
    if active_only:
        query = query.filter(Dashboard.active == True)
    
    # Filter by access permissions (simplified)
    query = query.filter(or_(
        Dashboard.is_public == True,
        Dashboard.created_by == current_user.username
    ))
    
    return query.all()

@router.get("/dashboards/{dashboard_id}/data", response_model=DashboardData)
async def get_dashboard_data(
    dashboard_id: str,
    time_range: Optional[str] = Query("30d"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get real-time data for a dashboard."""
    
    dashboard = db.query(Dashboard).filter(
        Dashboard.dashboard_id == dashboard_id
    ).first()
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Generate dashboard data using analytics engine
    try:
        dashboard_data = await analytics_engine.generate_dashboard_data(
            dashboard_id=dashboard_id,
            time_range=time_range,
            db=db
        )
        return dashboard_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard data: {str(e)}"
        )

# =====================
# REPORTS
# =====================

@router.post("/reports/templates", response_model=ReportTemplateResponse)
async def create_report_template(
    template: ReportTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new report template."""
    
    db_template = ReportTemplate(
        **template.dict(),
        created_by=current_user.username
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.get("/reports/templates", response_model=List[ReportTemplateResponse])
async def get_report_templates(
    report_type: Optional[ReportTypeEnum] = Query(None),
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all report templates."""
    
    query = db.query(ReportTemplate)
    
    if report_type:
        query = query.filter(ReportTemplate.report_type == report_type)
    
    if active_only:
        query = query.filter(ReportTemplate.active == True)
    
    return query.all()

@router.post("/reports/generate", response_model=GeneratedReportResponse)
async def generate_report(
    report: GeneratedReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a report from a template."""
    
    # Verify template exists
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == report.template_id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )
    
    db_report = GeneratedReport(
        **report.dict(),
        generated_for=current_user.username,
        status="pending"
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Schedule report generation in background
    background_tasks.add_task(
        analytics_engine.generate_report_async,
        report_id=db_report.report_id,
        template=template,
        parameters=report.parameters_used or {},
        db=db
    )
    
    return db_report

@router.get("/reports", response_model=List[GeneratedReportResponse])
async def get_generated_reports(
    status: Optional[str] = Query(None),
    limit: Optional[int] = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get generated reports."""
    
    query = db.query(GeneratedReport).filter(
        GeneratedReport.generated_for == current_user.username
    )
    
    if status:
        query = query.filter(GeneratedReport.status == status)
    
    query = query.order_by(desc(GeneratedReport.created_at))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

# =====================
# PREDICTIONS
# =====================

@router.post("/predictions", response_model=PredictionConfigurationResponse)
async def create_prediction_configuration(
    prediction: PredictionConfigurationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new prediction configuration."""
    
    db_prediction = PredictionConfiguration(
        **prediction.dict(),
        created_by=current_user.username
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction

@router.get("/predictions", response_model=List[PredictionConfigurationResponse])
async def get_prediction_configurations(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all prediction configurations."""
    
    query = db.query(PredictionConfiguration)
    
    if active_only:
        query = query.filter(PredictionConfiguration.active == True)
    
    return query.all()

@router.post("/predictions/{prediction_id}/run")
async def run_prediction(
    prediction_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run a prediction model."""
    
    prediction = db.query(PredictionConfiguration).filter(
        PredictionConfiguration.prediction_id == prediction_id
    ).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction configuration not found"
        )
    
    # Schedule prediction run in background
    background_tasks.add_task(
        analytics_engine.run_prediction_async,
        prediction_id=prediction_id,
        db=db
    )
    
    return {"message": "Prediction scheduled successfully"}

@router.get("/predictions/{prediction_id}/results", response_model=List[PredictionResultResponse])
async def get_prediction_results(
    prediction_id: str,
    limit: Optional[int] = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get prediction results."""
    
    prediction = db.query(PredictionConfiguration).filter(
        PredictionConfiguration.prediction_id == prediction_id
    ).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction configuration not found"
        )
    
    query = db.query(PredictionResult).filter(
        PredictionResult.prediction_configuration_id == prediction.id
    ).order_by(desc(PredictionResult.created_at))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

# =====================
# EXECUTIVE DASHBOARDS
# =====================

@router.get("/dashboards/executive/summary", response_model=ExecutiveSummary)
async def get_executive_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get executive summary dashboard data."""
    
    try:
        summary = await analytics_engine.generate_executive_summary(db=db)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating executive summary: {str(e)}"
        )

@router.get("/dashboards/compliance", response_model=ComplianceDashboard)
async def get_compliance_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get compliance dashboard data."""
    
    try:
        dashboard = await analytics_engine.generate_compliance_dashboard(db=db)
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating compliance dashboard: {str(e)}"
        )

@router.get("/dashboards/security", response_model=SecurityDashboard)
async def get_security_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get security dashboard data."""
    
    try:
        dashboard = await analytics_engine.generate_security_dashboard(db=db)
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating security dashboard: {str(e)}"
        )

# =====================
# ANALYTICS INSIGHTS
# =====================

@router.get("/insights", response_model=List[AnalyticsInsight])
async def get_analytics_insights(
    metric_ids: Optional[List[str]] = Query(None),
    time_range: Optional[str] = Query("30d"),
    limit: Optional[int] = Query(10, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered analytics insights."""
    
    try:
        insights = await analytics_engine.generate_insights(
            metric_ids=metric_ids,
            time_range=time_range,
            limit=limit,
            db=db
        )
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )

@router.get("/forecasts/risk", response_model=List[RiskForecast])
async def get_risk_forecasts(
    metrics: Optional[List[str]] = Query(None),
    horizon_days: Optional[int] = Query(90, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered risk forecasts."""
    
    try:
        forecasts = await analytics_engine.generate_risk_forecasts(
            metrics=metrics,
            horizon_days=horizon_days,
            db=db
        )
        return forecasts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating risk forecasts: {str(e)}"
        )

# =====================
# ANALYTICS JOBS
# =====================

@router.post("/jobs", response_model=AnalyticsJobResponse)
async def create_analytics_job(
    job: AnalyticsJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new analytics job."""
    
    db_job = AnalyticsJob(
        **job.dict(),
        created_by=current_user.username
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job

@router.get("/jobs", response_model=List[AnalyticsJobResponse])
async def get_analytics_jobs(
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    limit: Optional[int] = Query(50, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics jobs."""
    
    query = db.query(AnalyticsJob)
    
    if status:
        query = query.filter(AnalyticsJob.status == status)
    
    if job_type:
        query = query.filter(AnalyticsJob.job_type == job_type)
    
    query = query.order_by(desc(AnalyticsJob.created_at))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

# =====================
# DATA QUALITY
# =====================

@router.get("/data-quality", response_model=List[Dict[str, Any]])
async def get_data_quality_metrics(
    source_table: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get data quality metrics."""
    
    query = db.query(DataQualityMetric)
    
    if source_table:
        query = query.filter(DataQualityMetric.source_table == source_table)
    
    results = query.order_by(desc(DataQualityMetric.assessed_at)).all()
    
    return [
        {
            "quality_id": result.quality_id,
            "source_table": result.source_table,
            "source_column": result.source_column,
            "data_category": result.data_category,
            "completeness": result.completeness,
            "accuracy": result.accuracy,
            "consistency": result.consistency,
            "timeliness": result.timeliness,
            "validity": result.validity,
            "overall_score": (
                (result.completeness or 0) + 
                (result.accuracy or 0) + 
                (result.consistency or 0) + 
                (result.timeliness or 0) + 
                (result.validity or 0)
            ) / 5,
            "assessed_at": result.assessed_at,
            "quality_issues": result.quality_issues,
            "recommendations": result.recommendations
        }
        for result in results
    ]

# =====================
# ANALYTICS QUERY
# =====================

@router.post("/query")
async def execute_analytics_query(
    query_filter: AnalyticsQueryFilter,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Execute a custom analytics query."""
    
    try:
        results = await analytics_engine.execute_analytics_query(
            query_filter=query_filter,
            db=db
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing analytics query: {str(e)}"
        )