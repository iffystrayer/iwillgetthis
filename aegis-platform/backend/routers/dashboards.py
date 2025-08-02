from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List, Any
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.asset import Asset
from models.risk import Risk
from models.task import Task
from models.assessment import Assessment, AssessmentControl
from models.framework import Framework
from auth import get_current_active_user

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get overall dashboard overview for all users."""
    
    # Asset metrics
    total_assets = db.query(func.count(Asset.id)).filter(Asset.is_active == True).scalar()
    critical_assets = db.query(func.count(Asset.id)).filter(
        Asset.is_active == True,
        Asset.criticality == "critical"
    ).scalar()
    
    # Risk metrics
    total_risks = db.query(func.count(Risk.id)).filter(Risk.is_active == True).scalar()
    high_risks = db.query(func.count(Risk.id)).filter(
        Risk.is_active == True,
        Risk.risk_level.in_(["high", "critical"])
    ).scalar()
    
    # Open risks by category
    open_risks = db.query(func.count(Risk.id)).filter(
        Risk.is_active == True,
        Risk.status.in_(["identified", "assessed", "mitigating"])
    ).scalar()
    
    # Task metrics
    total_tasks = db.query(func.count(Task.id)).filter(Task.is_active == True).scalar()
    open_tasks = db.query(func.count(Task.id)).filter(
        Task.is_active == True,
        Task.status.in_(["open", "in_progress"])
    ).scalar()
    
    overdue_tasks = db.query(func.count(Task.id)).filter(
        Task.is_active == True,
        Task.due_date < datetime.utcnow(),
        Task.status.in_(["open", "in_progress"])
    ).scalar()
    
    # Assessment metrics
    total_assessments = db.query(func.count(Assessment.id)).filter(
        Assessment.is_active == True
    ).scalar()
    
    active_assessments = db.query(func.count(Assessment.id)).filter(
        Assessment.is_active == True,
        Assessment.status.in_(["draft", "in_progress"])
    ).scalar()
    
    completed_assessments = db.query(func.count(Assessment.id)).filter(
        Assessment.is_active == True,
        Assessment.status == "completed"
    ).scalar()
    
    return {
        "assets": {
            "total": total_assets,
            "critical": critical_assets
        },
        "risks": {
            "total": total_risks,
            "high_priority": high_risks,
            "open": open_risks
        },
        "tasks": {
            "total": total_tasks,
            "open": open_tasks,
            "overdue": overdue_tasks
        },
        "assessments": {
            "total": total_assessments,
            "active": active_assessments,
            "completed": completed_assessments
        }
    }


@router.get("/ciso-cockpit")
async def get_ciso_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get CISO cockpit dashboard with executive-level insights."""
    
    # Risk posture trend (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    risk_trend = db.query(
        func.date_trunc('month', Risk.created_at).label('month'),
        func.count(Risk.id).label('count')
    ).filter(
        Risk.created_at >= six_months_ago,
        Risk.is_active == True
    ).group_by(func.date_trunc('month', Risk.created_at)).all()
    
    # Risk level distribution
    risk_levels = db.query(
        Risk.risk_level,
        func.count(Risk.id).label('count')
    ).filter(
        Risk.is_active == True,
        Risk.risk_level.isnot(None)
    ).group_by(Risk.risk_level).all()
    
    # Top risks (highest risk score)
    top_risks = db.query(Risk).filter(
        Risk.is_active == True,
        Risk.status.in_(["identified", "assessed", "mitigating"])
    ).order_by(desc(Risk.inherent_risk_score)).limit(10).all()
    
    # Compliance maturity by framework
    frameworks_maturity = []
    frameworks = db.query(Framework).filter(Framework.is_active == True).all()
    
    for framework in frameworks:
        total_controls = db.query(func.count(AssessmentControl.id)).join(Assessment).filter(
            Assessment.framework_id == framework.id,
            Assessment.status == "completed"
        ).scalar()
        
        implemented_controls = db.query(func.count(AssessmentControl.id)).join(Assessment).filter(
            Assessment.framework_id == framework.id,
            Assessment.status == "completed",
            AssessmentControl.implementation_status == "implemented"
        ).scalar()
        
        maturity_score = 0
        if total_controls > 0:
            maturity_score = (implemented_controls / total_controls) * 100
        
        frameworks_maturity.append({
            "framework": framework.name,
            "maturity_score": round(maturity_score, 1),
            "total_controls": total_controls,
            "implemented_controls": implemented_controls
        })
    
    # Business impact areas
    impact_areas = db.query(
        Risk.category,
        func.count(Risk.id).label('count'),
        func.avg(Risk.inherent_risk_score).label('avg_score')
    ).filter(
        Risk.is_active == True
    ).group_by(Risk.category).all()
    
    return {
        "risk_trend": [
            {"month": item.month.strftime('%Y-%m'), "count": item.count}
            for item in risk_trend
        ],
        "risk_distribution": [
            {"level": item.risk_level, "count": item.count}
            for item in risk_levels
        ],
        "top_risks": [
            {
                "id": risk.id,
                "title": risk.title,
                "risk_level": risk.risk_level,
                "score": risk.inherent_risk_score,
                "category": risk.category
            }
            for risk in top_risks
        ],
        "compliance_maturity": frameworks_maturity,
        "impact_areas": [
            {
                "category": item.category,
                "risk_count": item.count,
                "avg_score": round(float(item.avg_score or 0), 1)
            }
            for item in impact_areas
        ]
    }


@router.get("/analyst-workbench")
async def get_analyst_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get analyst workbench dashboard with tactical workload management."""
    
    # My open tasks
    my_tasks = db.query(Task).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_active == True,
        Task.status.in_(["open", "in_progress"])
    ).order_by(Task.due_date.asc().nullslast()).limit(10).all()
    
    # Upcoming assessments
    upcoming_assessments = db.query(Assessment).filter(
        Assessment.is_active == True,
        Assessment.status.in_(["draft", "in_progress"]),
        Assessment.target_completion_date.isnot(None)
    ).order_by(Assessment.target_completion_date.asc()).limit(5).all()
    
    # Recent high-risk findings (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_high_risks = db.query(Risk).filter(
        Risk.created_at >= week_ago,
        Risk.is_active == True,
        Risk.risk_level.in_(["high", "critical"])
    ).order_by(desc(Risk.created_at)).limit(10).all()
    
    # Evidence awaiting review
    from models.evidence import Evidence
    pending_evidence = db.query(Evidence).filter(
        Evidence.is_active == True,
        Evidence.status == "under_review"
    ).order_by(desc(Evidence.created_at)).limit(5).all()
    
    # Tasks awaiting my review
    tasks_for_review = db.query(Task).filter(
        Task.is_active == True,
        Task.status == "awaiting_review"
    ).order_by(desc(Task.updated_at)).limit(5).all()
    
    # Workload summary
    total_assigned = db.query(func.count(Task.id)).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_active == True
    ).scalar()
    
    overdue_assigned = db.query(func.count(Task.id)).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_active == True,
        Task.due_date < datetime.utcnow(),
        Task.status.in_(["open", "in_progress"])
    ).scalar()
    
    return {
        "my_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "progress": task.progress_percentage
            }
            for task in my_tasks
        ],
        "upcoming_assessments": [
            {
                "id": assessment.id,
                "name": assessment.name,
                "target_date": assessment.target_completion_date.isoformat() if assessment.target_completion_date else None,
                "status": assessment.status
            }
            for assessment in upcoming_assessments
        ],
        "recent_high_risks": [
            {
                "id": risk.id,
                "title": risk.title,
                "risk_level": risk.risk_level,
                "created_at": risk.created_at.isoformat()
            }
            for risk in recent_high_risks
        ],
        "pending_evidence": [
            {
                "id": evidence.id,
                "title": evidence.title,
                "type": evidence.evidence_type,
                "uploaded_at": evidence.created_at.isoformat()
            }
            for evidence in pending_evidence
        ],
        "tasks_for_review": [
            {
                "id": task.id,
                "title": task.title,
                "submitter": task.assigned_to_id,
                "submitted_at": task.updated_at.isoformat()
            }
            for task in tasks_for_review
        ],
        "workload_summary": {
            "total_assigned": total_assigned,
            "overdue": overdue_assigned
        }
    }


@router.get("/system-owner-inbox")
async def get_system_owner_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get system owner inbox dashboard with assigned tasks and alerts."""
    
    # My assigned remediation tasks
    my_remediation_tasks = db.query(Task).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_active == True,
        Task.task_type.in_(["remediation", "mitigation"]),
        Task.status.in_(["open", "in_progress"])
    ).order_by(Task.priority.desc(), Task.due_date.asc().nullslast()).all()
    
    # Controls requiring attestation (from my owned assets)
    my_assets = db.query(Asset).filter(
        Asset.owner_id == current_user.id,
        Asset.is_active == True
    ).all()
    
    asset_ids = [asset.id for asset in my_assets]
    
    controls_for_attestation = []
    if asset_ids:
        assessments_with_my_assets = db.query(Assessment).filter(
            Assessment.asset_id.in_(asset_ids),
            Assessment.is_active == True,
            Assessment.status.in_(["in_progress", "under_review"])
        ).all()
        
        for assessment in assessments_with_my_assets:
            pending_controls = db.query(AssessmentControl).filter(
                AssessmentControl.assessment_id == assessment.id,
                AssessmentControl.implementation_status == "not_implemented"
            ).limit(5).all()
            
            for control in pending_controls:
                controls_for_attestation.append({
                    "assessment_id": assessment.id,
                    "assessment_name": assessment.name,
                    "control_id": control.id,
                    "control_title": control.control.title if control.control else "Unknown"
                })
    
    # Overdue items
    overdue_tasks = db.query(Task).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_active == True,
        Task.due_date < datetime.utcnow(),
        Task.status.in_(["open", "in_progress"])
    ).all()
    
    # Recent alerts/notifications
    recent_alerts = []
    
    # Add high-priority tasks assigned in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_high_priority = db.query(Task).filter(
        Task.assigned_to_id == current_user.id,
        Task.is_active == True,
        Task.priority.in_(["high", "critical"]),
        Task.created_at >= week_ago
    ).all()
    
    for task in new_high_priority:
        recent_alerts.append({
            "type": "high_priority_task",
            "message": f"High priority task assigned: {task.title}",
            "created_at": task.created_at.isoformat(),
            "task_id": task.id
        })
    
    return {
        "remediation_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "progress": task.progress_percentage,
                "status": task.status
            }
            for task in my_remediation_tasks
        ],
        "controls_for_attestation": controls_for_attestation[:10],  # Limit to 10
        "overdue_items": [
            {
                "id": task.id,
                "title": task.title,
                "due_date": task.due_date.isoformat(),
                "days_overdue": (datetime.utcnow() - task.due_date).days
            }
            for task in overdue_tasks
        ],
        "recent_alerts": sorted(recent_alerts, key=lambda x: x['created_at'], reverse=True)[:10]
    }