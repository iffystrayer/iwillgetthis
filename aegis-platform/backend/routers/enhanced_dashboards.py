"""Enhanced dashboard API endpoints with comprehensive analytics and reporting"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from auth import get_current_user
from models.user import User
from services.dashboard_analytics_service import dashboard_analytics_service
from utils.audit_helpers import log_user_action, log_system_event

logger = logging.getLogger(__name__)

router = APIRouter()

# ===================
# EXECUTIVE DASHBOARDS
# ===================

@router.get("/executive/overview")
@log_user_action(
    event_type="dashboard_access",
    entity_type="dashboard",
    action="view_executive_overview",
    description="Access executive dashboard overview"
)
async def get_executive_overview(
    time_range: str = Query("30d", description="Time range for analytics (7d, 30d, 90d, 1y)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive executive dashboard with AI-powered insights"""
    
    try:
        dashboard_data = await dashboard_analytics_service.generate_executive_dashboard(
            db=db, 
            time_range=time_range
        )
        
        # Log dashboard generation
        log_system_event(
            db=db,
            event_type="dashboard_generation",
            entity_type="dashboard",
            action="generate_executive",
            description=f"Executive dashboard generated for {time_range} time range",
            user_id=current_user.id,
            details={
                "time_range": time_range,
                "total_risks": dashboard_data.get("core_metrics", {}).get("risks", {}).get("total", 0),
                "high_risks": dashboard_data.get("core_metrics", {}).get("risks", {}).get("high_priority", 0),
                "insights_count": len(dashboard_data.get("ai_insights", []))
            }
        )
        
        return JSONResponse(content=dashboard_data)
        
    except Exception as e:
        logger.error(f"Executive dashboard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

@router.get("/executive/real-time")
async def get_executive_real_time_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time executive metrics for live monitoring"""
    
    try:
        # Generate lightweight real-time metrics
        real_time_data = await dashboard_analytics_service._get_core_metrics(
            db, 
            datetime.utcnow() - timedelta(hours=24)
        )
        
        # Add real-time status indicators
        real_time_data["status"] = {
            "last_updated": datetime.utcnow().isoformat(),
            "system_health": "operational",
            "active_alerts": 0  # Would be calculated from actual alerts
        }
        
        return JSONResponse(content=real_time_data)
        
    except Exception as e:
        logger.error(f"Real-time metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Real-time metrics failed: {str(e)}")

@router.get("/executive/kpi-summary")
async def get_executive_kpi_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get executive KPI summary for quick status overview"""
    
    try:
        # Get core metrics for KPI calculation
        core_metrics = await dashboard_analytics_service._get_core_metrics(
            db, 
            datetime.utcnow() - timedelta(days=30)
        )
        
        risk_analytics = await dashboard_analytics_service._get_risk_analytics(
            db, 
            datetime.utcnow() - timedelta(days=30)
        )
        
        compliance_posture = await dashboard_analytics_service._get_compliance_posture(db)
        
        # Calculate KPIs
        kpi_summary = {
            "security_posture_score": _calculate_security_posture_score(core_metrics, risk_analytics),
            "compliance_score": compliance_posture.get("overall_score", 0),
            "operational_efficiency": _calculate_operational_efficiency(core_metrics),
            "risk_management_effectiveness": risk_analytics["closure_metrics"]["closure_rate"],
            "overall_health_score": 0,  # Will be calculated from other scores
            "trend_indicators": {
                "security_trend": "stable",
                "compliance_trend": "improving",
                "efficiency_trend": "improving"
            }
        }
        
        # Calculate overall health score
        kpi_summary["overall_health_score"] = round(
            (kpi_summary["security_posture_score"] + 
             kpi_summary["compliance_score"] + 
             kpi_summary["operational_efficiency"] + 
             kpi_summary["risk_management_effectiveness"]) / 4, 1
        )
        
        return JSONResponse(content=kpi_summary)
        
    except Exception as e:
        logger.error(f"KPI summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"KPI summary failed: {str(e)}")

# ===================
# OPERATIONAL DASHBOARDS
# ===================

@router.get("/operational/workbench")
@log_user_action(
    event_type="dashboard_access",
    entity_type="dashboard",
    action="view_operational_workbench",
    description="Access operational workbench dashboard"
)
async def get_operational_workbench(
    time_range: str = Query("7d", description="Time range for analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get operational dashboard optimized for analysts and system owners"""
    
    try:
        dashboard_data = await dashboard_analytics_service.generate_operational_dashboard(
            db=db,
            user_id=current_user.id,
            time_range=time_range
        )
        
        return JSONResponse(content=dashboard_data)
        
    except Exception as e:
        logger.error(f"Operational dashboard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Operational dashboard failed: {str(e)}")

@router.get("/operational/team-performance")
async def get_team_performance_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team performance metrics and analytics"""
    
    try:
        # Get team performance data
        team_data = await dashboard_analytics_service._get_team_performance(
            db, 
            datetime.utcnow() - timedelta(days=30)
        )
        
        return JSONResponse(content=team_data)
        
    except Exception as e:
        logger.error(f"Team performance dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Team performance failed: {str(e)}")

# ===================
# RISK DASHBOARDS
# ===================

@router.get("/risk/portfolio")
@log_user_action(
    event_type="dashboard_access",
    entity_type="dashboard",
    action="view_risk_portfolio",
    description="Access risk portfolio dashboard"
)
async def get_risk_portfolio_dashboard(
    time_range: str = Query("90d", description="Time range for risk analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive risk portfolio dashboard"""
    
    try:
        dashboard_data = await dashboard_analytics_service.generate_risk_dashboard(
            db=db,
            time_range=time_range
        )
        
        return JSONResponse(content=dashboard_data)
        
    except Exception as e:
        logger.error(f"Risk dashboard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk dashboard failed: {str(e)}")

@router.get("/risk/heat-map")
async def get_risk_heat_map(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk heat map visualization data"""
    
    try:
        heat_map_data = await dashboard_analytics_service._generate_risk_heat_map(db)
        return JSONResponse(content=heat_map_data)
        
    except Exception as e:
        logger.error(f"Risk heat map generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk heat map failed: {str(e)}")

@router.get("/risk/forecast")
async def get_risk_forecast(
    horizon_days: int = Query(90, description="Forecast horizon in days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered risk forecasting data"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=180)  # Use 6 months of historical data
        forecast_data = await dashboard_analytics_service._generate_risk_forecast(db, start_date)
        
        return JSONResponse(content={
            "forecast_horizon_days": horizon_days,
            "forecast_data": forecast_data,
            "confidence_level": 0.85,
            "generated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Risk forecast generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk forecast failed: {str(e)}")

# ===================
# COMPLIANCE DASHBOARDS
# ===================

@router.get("/compliance/overview")
@log_user_action(
    event_type="dashboard_access",
    entity_type="dashboard",
    action="view_compliance_overview",
    description="Access compliance overview dashboard"
)
async def get_compliance_overview(
    framework_id: Optional[int] = Query(None, description="Filter by specific framework"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive compliance dashboard"""
    
    try:
        dashboard_data = await dashboard_analytics_service.generate_compliance_dashboard(
            db=db,
            framework_id=framework_id
        )
        
        return JSONResponse(content=dashboard_data)
        
    except Exception as e:
        logger.error(f"Compliance dashboard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Compliance dashboard failed: {str(e)}")

@router.get("/compliance/gap-analysis")
async def get_compliance_gap_analysis(
    framework_id: Optional[int] = Query(None, description="Framework ID for gap analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed compliance gap analysis"""
    
    try:
        gap_analysis = await dashboard_analytics_service._perform_compliance_gap_analysis(
            db, framework_id
        )
        
        return JSONResponse(content=gap_analysis)
        
    except Exception as e:
        logger.error(f"Gap analysis generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")

# ===================
# SECURITY METRICS DASHBOARDS
# ===================

@router.get("/security/metrics-overview")
@log_user_action(
    event_type="dashboard_access",
    entity_type="dashboard",
    action="view_security_metrics",
    description="Access security metrics dashboard"
)
async def get_security_metrics_overview(
    time_range: str = Query("30d", description="Time range for security metrics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive security metrics dashboard"""
    
    try:
        dashboard_data = await dashboard_analytics_service.generate_security_metrics_dashboard(
            db=db,
            time_range=time_range
        )
        
        return JSONResponse(content=dashboard_data)
        
    except Exception as e:
        logger.error(f"Security metrics dashboard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Security metrics dashboard failed: {str(e)}")

@router.get("/security/threat-landscape")
async def get_threat_landscape(
    time_range: str = Query("30d", description="Time range for threat analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get threat landscape analysis"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=dashboard_analytics_service._parse_time_range(time_range))
        threat_data = await dashboard_analytics_service._analyze_threat_landscape(db, start_date)
        
        return JSONResponse(content=threat_data)
        
    except Exception as e:
        logger.error(f"Threat landscape analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Threat landscape failed: {str(e)}")

# ===================
# CUSTOM DASHBOARDS
# ===================

@router.post("/custom/generate")
@log_user_action(
    event_type="dashboard_generation",
    entity_type="dashboard",
    action="generate_custom",
    description="Generate custom dashboard"
)
async def generate_custom_dashboard(
    dashboard_config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate custom dashboard based on user configuration"""
    
    try:
        # Validate dashboard configuration
        required_fields = ["dashboard_name", "metrics", "time_range"]
        for field in required_fields:
            if field not in dashboard_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Schedule custom dashboard generation in background
        background_tasks.add_task(
            _generate_custom_dashboard_async,
            db,
            current_user.id,
            dashboard_config
        )
        
        return JSONResponse(content={
            "message": "Custom dashboard generation started",
            "dashboard_name": dashboard_config["dashboard_name"],
            "status": "processing"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom dashboard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Custom dashboard generation failed: {str(e)}")

@router.get("/templates")
async def get_dashboard_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available dashboard templates"""
    
    templates = [
        {
            "id": "executive_standard",
            "name": "Executive Standard",
            "description": "Standard executive dashboard with KPIs and risk overview",
            "category": "executive",
            "widgets": ["kpi_summary", "risk_overview", "compliance_status", "critical_alerts"]
        },
        {
            "id": "risk_analyst",
            "name": "Risk Analyst Workbench",
            "description": "Comprehensive risk analysis and management dashboard",
            "category": "operational",
            "widgets": ["risk_portfolio", "heat_map", "trends", "treatment_status"]
        },
        {
            "id": "compliance_manager",
            "name": "Compliance Manager",
            "description": "Compliance tracking and gap analysis dashboard",
            "category": "compliance",
            "widgets": ["framework_status", "gap_analysis", "evidence_tracking", "audit_readiness"]
        },
        {
            "id": "security_operations",
            "name": "Security Operations",
            "description": "Security metrics and operational monitoring",
            "category": "security",
            "widgets": ["security_metrics", "incident_response", "threat_landscape", "vulnerability_management"]
        }
    ]
    
    return JSONResponse(content={
        "templates": templates,
        "total_templates": len(templates)
    })

# ===================
# DASHBOARD UTILITIES
# ===================

@router.get("/data-refresh")
async def refresh_dashboard_data(
    dashboard_type: str = Query(..., description="Type of dashboard to refresh"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh dashboard data and clear cache"""
    
    try:
        # Clear relevant cache
        dashboard_analytics_service.metric_cache.clear()
        dashboard_analytics_service.last_cache_update.clear()
        
        return JSONResponse(content={
            "message": f"Dashboard data refreshed for {dashboard_type}",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Dashboard refresh failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard refresh failed: {str(e)}")

@router.get("/export/{dashboard_type}")
async def export_dashboard_data(
    dashboard_type: str,
    format: str = Query("json", description="Export format (json, csv, pdf)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export dashboard data in specified format"""
    
    try:
        # Generate dashboard data based on type
        if dashboard_type == "executive":
            data = await dashboard_analytics_service.generate_executive_dashboard(db)
        elif dashboard_type == "risk":
            data = await dashboard_analytics_service.generate_risk_dashboard(db)
        elif dashboard_type == "compliance":
            data = await dashboard_analytics_service.generate_compliance_dashboard(db)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown dashboard type: {dashboard_type}")
        
        # For now, return JSON format (CSV and PDF would need additional processing)
        if format.lower() == "json":
            return JSONResponse(content=data)
        else:
            return JSONResponse(content={
                "message": f"Export format '{format}' not yet implemented",
                "available_formats": ["json"]
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard export failed: {str(e)}")

# Helper functions
def _calculate_security_posture_score(core_metrics: Dict[str, Any], risk_analytics: Dict[str, Any]) -> float:
    """Calculate overall security posture score"""
    
    # Risk factor (lower is better)
    risk_factor = max(0, 100 - core_metrics["risks"]["high_priority_percentage"])
    
    # Task management factor
    task_factor = max(0, 100 - core_metrics["tasks"]["overdue_percentage"])
    
    # Risk closure effectiveness
    closure_factor = risk_analytics["closure_metrics"]["closure_rate"]
    
    # Weighted average
    score = (risk_factor * 0.4 + task_factor * 0.3 + closure_factor * 0.3)
    return round(score, 1)

def _calculate_operational_efficiency(core_metrics: Dict[str, Any]) -> float:
    """Calculate operational efficiency score"""
    
    # Task completion rate
    total_tasks = core_metrics["tasks"]["total"]
    completed_tasks = core_metrics["tasks"]["completed_this_period"]
    overdue_tasks = core_metrics["tasks"]["overdue"]
    
    if total_tasks == 0:
        return 100.0
    
    completion_rate = (completed_tasks / total_tasks) * 100
    overdue_penalty = (overdue_tasks / total_tasks) * 20
    
    efficiency = max(0, completion_rate - overdue_penalty)
    return round(efficiency, 1)

async def _generate_custom_dashboard_async(db: Session, user_id: int, config: Dict[str, Any]):
    """Background task for custom dashboard generation"""
    
    try:
        # Custom dashboard generation logic would go here
        # This is a placeholder for the actual implementation
        logger.info(f"Generating custom dashboard for user {user_id}: {config['dashboard_name']}")
        
        # Would store the generated dashboard in the database
        # and notify the user when complete
        
    except Exception as e:
        logger.error(f"Custom dashboard generation failed for user {user_id}: {e}")