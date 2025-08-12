from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, case
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.user import User
from models.assessment import Assessment, AssessmentControl
from models.framework import Framework, Control
from models.risk import Risk
from models.audit import AuditLog
from schemas.assessment import (
    AssessmentResponse, AssessmentCreate, AssessmentUpdate, AssessmentSummary,
    AssessmentControlResponse, AssessmentControlCreate, AssessmentControlUpdate
)
from auth import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    framework_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of assessments with pagination and filtering."""
    query = db.query(Assessment).options(
        joinedload(Assessment.framework),
        joinedload(Assessment.asset),
        joinedload(Assessment.created_by_user),
        joinedload(Assessment.lead_assessor),
        selectinload(Assessment.assessment_controls)
    )
    
    if search:
        query = query.filter(
            (Assessment.name.contains(search)) |
            (Assessment.description.contains(search))
        )
    
    if status:
        query = query.filter(Assessment.status == status)
    
    if framework_id:
        query = query.filter(Assessment.framework_id == framework_id)
    
    # Get total count for pagination
    total = query.filter(Assessment.is_active == True).count()
    assessments = query.filter(Assessment.is_active == True).offset(skip).limit(limit).all()
    
    # Return paginated response structure expected by frontend
    return {
        "items": [AssessmentResponse.model_validate(assessment) for assessment in assessments],
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get assessment by ID."""
    assessment = db.query(Assessment).options(
        joinedload(Assessment.framework),
        joinedload(Assessment.asset),
        joinedload(Assessment.created_by_user),
        joinedload(Assessment.lead_assessor),
        selectinload(Assessment.assessment_controls)
    ).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    return assessment


@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment: AssessmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new assessment."""
    # Verify framework exists
    framework = db.query(Framework).filter(Framework.id == assessment.framework_id).first()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found"
        )
    
    assessment_data = assessment.model_dump()
    assessment_data["created_by_id"] = current_user.id
    
    db_assessment = Assessment(**assessment_data)
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    
    # Create assessment controls for all controls in the framework
    controls = db.query(Control).filter(Control.framework_id == assessment.framework_id).all()
    for control in controls:
        assessment_control = AssessmentControl(
            assessment_id=db_assessment.id,
            control_id=control.id,
            implementation_status="not_implemented"  # Default status
        )
        db.add(assessment_control)
    
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="assessment",
        entity_id=db_assessment.id,
        user_id=current_user.id,
        action="Assessment created",
        description=f"Assessment created: {db_assessment.name}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_assessment


@router.put("/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment(
    assessment_id: int,
    assessment_update: AssessmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update assessment."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Update assessment fields
    update_data = assessment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment, field, value)
    
    db.commit()
    db.refresh(assessment)
    
    return assessment


@router.get("/{assessment_id}/summary", response_model=AssessmentSummary)
async def get_assessment_summary(
    assessment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get assessment summary statistics."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Get control status counts in a single query using CASE WHEN
    status_counts = db.query(
        func.count(AssessmentControl.id).label('total_controls'),
        func.count(case((AssessmentControl.implementation_status == "implemented", 1))).label('implemented'),
        func.count(case((AssessmentControl.implementation_status == "not_implemented", 1))).label('not_implemented'),
        func.count(case((AssessmentControl.implementation_status == "partially_implemented", 1))).label('partially_implemented'),
        func.count(case((AssessmentControl.implementation_status == "not_applicable", 1))).label('not_applicable'),
        func.count(case((AssessmentControl.implementation_status == "planned", 1))).label('planned')
    ).filter(
        AssessmentControl.assessment_id == assessment_id
    ).first()
    
    total_controls = status_counts.total_controls
    implemented = status_counts.implemented
    not_implemented = status_counts.not_implemented
    partially_implemented = status_counts.partially_implemented
    not_applicable = status_counts.not_applicable
    planned = status_counts.planned
    
    completion_percentage = 0
    if total_controls > 0:
        completed_controls = implemented + not_applicable
        completion_percentage = (completed_controls / total_controls) * 100
    
    return AssessmentSummary(
        total_controls=total_controls,
        implemented=implemented,
        not_implemented=not_implemented,
        partially_implemented=partially_implemented,
        not_applicable=not_applicable,
        planned=planned,
        completion_percentage=completion_percentage,
        overall_score=assessment.overall_score,
        maturity_level=assessment.maturity_level
    )


# Assessment Controls
@router.get("/{assessment_id}/controls", response_model=List[AssessmentControlResponse])
async def get_assessment_controls(
    assessment_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=5000),
    implementation_status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get controls for a specific assessment."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    query = db.query(AssessmentControl).options(
        joinedload(AssessmentControl.assessment),
        joinedload(AssessmentControl.control),
        joinedload(AssessmentControl.reviewed_by)
    ).filter(AssessmentControl.assessment_id == assessment_id)
    
    if implementation_status:
        query = query.filter(AssessmentControl.implementation_status == implementation_status)
    
    controls = query.offset(skip).limit(limit).all()
    return controls


@router.put("/controls/{control_id}", response_model=AssessmentControlResponse)
async def update_assessment_control(
    control_id: int,
    control_update: AssessmentControlUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update assessment control."""
    assessment_control = db.query(AssessmentControl).filter(
        AssessmentControl.id == control_id
    ).first()
    
    if not assessment_control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment control not found"
        )
    
    # Store old status for risk creation logic
    old_status = assessment_control.implementation_status
    
    # Update control fields
    update_data = control_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment_control, field, value)
    
    db.commit()
    db.refresh(assessment_control)
    
    # Auto-create risk if control is marked as "not_implemented"
    if (assessment_control.implementation_status == "not_implemented" and 
        old_status != "not_implemented"):
        
        # Get control details
        control = db.query(Control).filter(Control.id == assessment_control.control_id).first()
        assessment = db.query(Assessment).filter(
            Assessment.id == assessment_control.assessment_id
        ).first()
        
        if control and assessment:
            # Create risk
            risk = Risk(
                title=f"Control not implemented: {control.control_id} - {control.title}",
                description=f"Control {control.control_id} is not implemented for assessment {assessment.name}",
                category="compliance",
                risk_type="compliance_gap",
                source="assessment",
                source_reference=f"assessment_{assessment.id}_control_{control.id}",
                asset_id=assessment.asset_id,
                inherent_likelihood=3,  # Default medium likelihood
                inherent_impact=3,  # Default medium impact
                status="IDENTIFIED",
                created_by=current_user.id
            )
            db.add(risk)
            db.commit()
            
            # Log risk creation
            audit_log = AuditLog(
                event_type="create",
                entity_type="risk",
                entity_id=risk.id,
                user_id=current_user.id,
                action="Risk auto-created from assessment",
                description=f"Risk auto-created for non-implemented control: {control.control_id}",
                source="system",
                risk_level="medium"
            )
            db.add(audit_log)
            db.commit()
    
    return assessment_control


@router.post("/{assessment_id}/complete")
async def complete_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark assessment as completed."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    assessment.status = "completed"
    assessment.actual_completion_date = datetime.utcnow()
    
    # Calculate overall score using a single query
    control_counts = db.query(
        func.count(AssessmentControl.id).label('total_controls'),
        func.count(case((AssessmentControl.implementation_status.in_(["implemented", "not_applicable"]), 1))).label('implemented_controls')
    ).filter(
        AssessmentControl.assessment_id == assessment_id
    ).first()
    
    total_controls = control_counts.total_controls
    implemented_controls = control_counts.implemented_controls
    
    if total_controls > 0:
        assessment.overall_score = int((implemented_controls / total_controls) * 100)
    
    db.commit()
    
    return {"message": "Assessment completed successfully", "overall_score": assessment.overall_score}