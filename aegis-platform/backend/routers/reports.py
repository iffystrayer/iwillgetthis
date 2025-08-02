from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import json

from database import get_db
from models.user import User
from models.report import Report, ReportTemplate
from models.audit import AuditLog
from schemas.report import (
    ReportResponse, ReportCreate, ReportUpdate,
    ReportTemplateResponse, ReportTemplateCreate, ReportTemplateUpdate,
    ReportGeneration, ReportSchedule
)
from auth import get_current_active_user

router = APIRouter()


# Report Templates
@router.get("/templates/", response_model=List[ReportTemplateResponse])
async def get_report_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of report templates."""
    query = db.query(ReportTemplate)
    
    if report_type:
        query = query.filter(ReportTemplate.report_type == report_type)
    
    if is_public is not None:
        query = query.filter(ReportTemplate.is_public == is_public)
    
    # Users can see public templates or their own templates
    query = query.filter(
        (ReportTemplate.is_public == True) |
        (ReportTemplate.created_by == current_user.id)
    )
    
    templates = query.filter(ReportTemplate.is_active == True).offset(skip).limit(limit).all()
    return templates


@router.post("/templates/", response_model=ReportTemplateResponse)
async def create_report_template(
    template: ReportTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new report template."""
    template_data = template.model_dump()
    template_data["created_by"] = current_user.id
    
    db_template = ReportTemplate(**template_data)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get report template by ID."""
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )
    
    # Check access permissions
    if not template.is_public and template.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this template"
        )
    
    return template


# Reports
@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of reports."""
    query = db.query(Report)
    
    if search:
        query = query.filter(
            (Report.name.contains(search)) |
            (Report.description.contains(search))
        )
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    if status:
        query = query.filter(Report.status == status)
    
    # Users can only see their own reports
    query = query.filter(Report.created_by == current_user.id)
    
    reports = query.offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get report by ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check access permissions
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    return report


@router.post("/", response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new report."""
    report_data = report.model_dump()
    report_data["created_by"] = current_user.id
    
    db_report = Report(**report_data)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="report",
        entity_id=db_report.id,
        user_id=current_user.id,
        action="Report created",
        description=f"Report created: {db_report.name}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_report


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_update: ReportUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    # Update report fields
    update_data = report_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    db.delete(report)
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="delete",
        entity_type="report",
        entity_id=report.id,
        user_id=current_user.id,
        action="Report deleted",
        description=f"Report deleted: {report.name}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Report deleted successfully"}


async def generate_report_background(report_id: int, db: Session):
    """Background task to generate report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return
    
    try:
        report.status = "generating"
        report.generation_started = datetime.utcnow()
        db.commit()
        
        # Simulate report generation (replace with actual logic)
        import time
        time.sleep(5)  # Simulate processing time
        
        # Update report with generated file info
        report.status = "completed"
        report.generation_completed = datetime.utcnow()
        report.generation_duration = int((report.generation_completed - report.generation_started).total_seconds())
        report.file_name = f"report_{report.id}_{int(datetime.utcnow().timestamp())}.pdf"
        report.file_path = f"/reports/{report.file_name}"
        report.file_size = 1024 * 1024  # Simulated file size
        
        db.commit()
        
    except Exception as e:
        report.status = "failed"
        report.error_message = str(e)
        db.commit()


@router.post("/{report_id}/generate")
async def generate_report(
    report_id: int,
    background_tasks: BackgroundTasks,
    generation_config: Optional[ReportGeneration] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    if report.status == "generating":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is already being generated"
        )
    
    # Start background task for report generation
    background_tasks.add_task(generate_report_background, report_id, db)
    
    return {"message": "Report generation started", "report_id": report_id}


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download generated report file."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    if report.status != "completed" or not report.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report file is not available"
        )
    
    # Update download tracking
    report.download_count += 1
    report.last_downloaded = datetime.utcnow()
    db.commit()
    
    # In a real implementation, you would return the actual file
    return {
        "message": "Report download would start here",
        "file_name": report.file_name,
        "file_size": report.file_size
    }


@router.post("/{report_id}/schedule")
async def schedule_report(
    report_id: int,
    schedule_config: ReportSchedule,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Schedule report for automatic generation."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    # Update report scheduling
    report.is_scheduled = True
    report.schedule_config = schedule_config.model_dump()
    report.next_generation = schedule_config.next_run
    
    db.commit()
    
    return {"message": "Report scheduled successfully"}


@router.delete("/{report_id}/schedule")
async def unschedule_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove report scheduling."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    # Remove scheduling
    report.is_scheduled = False
    report.schedule_config = None
    report.next_generation = None
    
    db.commit()
    
    return {"message": "Report scheduling removed successfully"}