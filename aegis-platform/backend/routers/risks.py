from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from typing import List, Optional
import json

from database import get_db
from models.user import User
from models.risk import Risk, RiskMatrix, RiskScore
from models.audit import AuditLog
from schemas.risk import (
    RiskResponse, RiskCreate, RiskUpdate, RiskSummary,
    RiskMatrixResponse, RiskMatrixCreate, RiskMatrixUpdate,
    RiskScoreResponse, RiskScoreCreate
)
from auth import get_current_active_user

router = APIRouter()


# Risk Matrices
@router.get("/matrices/", response_model=List[RiskMatrixResponse])
async def get_risk_matrices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all risk matrices."""
    matrices = db.query(RiskMatrix).filter(RiskMatrix.is_active == True).all()
    return matrices


@router.post("/matrices/", response_model=RiskMatrixResponse)
async def create_risk_matrix(
    matrix: RiskMatrixCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new risk matrix."""
    db_matrix = RiskMatrix(**matrix.model_dump())
    db.add(db_matrix)
    db.commit()
    db.refresh(db_matrix)
    return db_matrix


@router.get("/matrices/default", response_model=RiskMatrixResponse)
async def get_default_risk_matrix(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the default risk matrix."""
    matrix = db.query(RiskMatrix).filter(RiskMatrix.is_default == True).first()
    if not matrix:
        # Create default matrix if it doesn't exist
        default_matrix = RiskMatrix(
            name="Default Risk Matrix",
            description="Standard 5x5 risk matrix",
            likelihood_levels=json.dumps([
                {"level": 1, "name": "Very Low", "description": "Very unlikely to occur"},
                {"level": 2, "name": "Low", "description": "Unlikely to occur"},
                {"level": 3, "name": "Medium", "description": "May occur"},
                {"level": 4, "name": "High", "description": "Likely to occur"},
                {"level": 5, "name": "Very High", "description": "Very likely to occur"}
            ]),
            impact_levels=json.dumps([
                {"level": 1, "name": "Very Low", "description": "Minimal impact"},
                {"level": 2, "name": "Low", "description": "Minor impact"},
                {"level": 3, "name": "Medium", "description": "Moderate impact"},
                {"level": 4, "name": "High", "description": "Major impact"},
                {"level": 5, "name": "Very High", "description": "Severe impact"}
            ]),
            risk_scores=json.dumps([
                [1, 2, 3, 4, 5],
                [2, 4, 6, 8, 10],
                [3, 6, 9, 12, 15],
                [4, 8, 12, 16, 20],
                [5, 10, 15, 20, 25]
            ]),
            risk_levels=json.dumps({
                "1-5": "low",
                "6-10": "medium",
                "11-15": "high",
                "16-25": "critical"
            }),
            is_default=True
        )
        db.add(default_matrix)
        db.commit()
        db.refresh(default_matrix)
        matrix = default_matrix
    
    return matrix


# Risks
@router.get("/")
async def get_risks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    asset_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of risks with pagination and filtering."""
    query = db.query(Risk).options(
        joinedload(Risk.risk_matrix),
        joinedload(Risk.asset),
        joinedload(Risk.owner),
        joinedload(Risk.creator),
        selectinload(Risk.tasks),
        selectinload(Risk.risk_scores)
    )
    
    if search:
        query = query.filter(
            (Risk.title.contains(search)) |
            (Risk.description.contains(search))
        )
    
    if category:
        query = query.filter(Risk.category == category)
    
    if status:
        query = query.filter(Risk.status == status)
    
    if risk_level:
        query = query.filter(Risk.risk_level == risk_level)
    
    if asset_id:
        query = query.filter(Risk.asset_id == asset_id)
    
    # Get total count for pagination
    total = query.filter(Risk.is_active == True).count()
    risks = query.filter(Risk.is_active == True).offset(skip).limit(limit).all()
    
    # Return paginated response structure expected by frontend
    return {
        "items": [RiskResponse.model_validate(risk) for risk in risks],
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/summary", response_model=RiskSummary)
async def get_risks_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk summary statistics."""
    total_risks = db.query(func.count(Risk.id)).filter(Risk.is_active == True).scalar()
    
    # Count by status
    by_status = {}
    status_counts = db.query(
        Risk.status,
        func.count(Risk.id).label('count')
    ).filter(Risk.is_active == True).group_by(Risk.status).all()
    
    for item in status_counts:
        by_status[item.status] = item.count
    
    # Count by category
    by_category = {}
    category_counts = db.query(
        Risk.category,
        func.count(Risk.id).label('count')
    ).filter(Risk.is_active == True).group_by(Risk.category).all()
    
    for item in category_counts:
        by_category[item.category] = item.count
    
    # Count by risk level
    by_risk_level = {}
    level_counts = db.query(
        Risk.risk_level,
        func.count(Risk.id).label('count')
    ).filter(Risk.is_active == True, Risk.risk_level.isnot(None)).group_by(Risk.risk_level).all()
    
    for item in level_counts:
        by_risk_level[item.risk_level] = item.count
    
    # High priority count (high and critical)
    high_priority_count = db.query(func.count(Risk.id)).filter(
        Risk.is_active == True,
        Risk.risk_level.in_(["HIGH", "CRITICAL"])
    ).scalar()
    
    # Overdue count (past target resolution date)
    from datetime import datetime
    overdue_count = db.query(func.count(Risk.id)).filter(
        Risk.is_active == True,
        Risk.target_resolution_date < datetime.utcnow(),
        Risk.status.in_(["IDENTIFIED", "ASSESSED", "MITIGATING"])
    ).scalar()
    
    return RiskSummary(
        total_risks=total_risks,
        by_status=by_status,
        by_category=by_category,
        by_risk_level=by_risk_level,
        high_priority_count=high_priority_count,
        overdue_count=overdue_count
    )


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk by ID."""
    risk = db.query(Risk).options(
        joinedload(Risk.risk_matrix),
        joinedload(Risk.asset),
        joinedload(Risk.owner),
        joinedload(Risk.creator),
        selectinload(Risk.tasks),
        selectinload(Risk.risk_scores)
    ).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    return risk


@router.post("/", response_model=RiskResponse)
async def create_risk(
    risk: RiskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new risk."""
    risk_data = risk.model_dump()
    risk_data["created_by"] = current_user.id
    
    # Convert Pydantic enum values (lowercase) to database enum values (uppercase)
    if "category" in risk_data and risk_data["category"]:
        # Extract the string value from enum object and convert to uppercase
        risk_data["category"] = str(risk_data["category"].value).upper()
    if "status" in risk_data and risk_data["status"]:
        # Extract the string value from enum object and convert to uppercase
        risk_data["status"] = str(risk_data["status"].value).upper()
    
    # Calculate risk score if likelihood and impact are provided
    if risk_data.get("inherent_likelihood") and risk_data.get("inherent_impact"):
        likelihood = risk_data["inherent_likelihood"]
        impact = risk_data["inherent_impact"]
        risk_data["inherent_risk_score"] = likelihood * impact
        
        # Determine risk level
        score = risk_data["inherent_risk_score"]
        if score <= 5:
            risk_data["risk_level"] = "LOW"
        elif score <= 10:
            risk_data["risk_level"] = "MEDIUM"
        elif score <= 15:
            risk_data["risk_level"] = "HIGH"
        else:
            risk_data["risk_level"] = "CRITICAL"
    
    db_risk = Risk(**risk_data)
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="risk",
        entity_id=db_risk.id,
        user_id=current_user.id,
        action="Risk created",
        description=f"Risk created: {db_risk.title}",
        source="web_ui",
        risk_level="medium"
    )
    db.add(audit_log)
    db.commit()
    
    return db_risk


@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: int,
    risk_update: RiskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update risk."""
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    
    # Store old values for audit
    old_values = {
        "title": risk.title,
        "status": risk.status,
        "risk_level": risk.risk_level
    }
    
    # Update risk fields
    update_data = risk_update.model_dump(exclude_unset=True)
    
    # Recalculate risk score if likelihood or impact changed
    if ("inherent_likelihood" in update_data or "inherent_impact" in update_data or
        "residual_likelihood" in update_data or "residual_impact" in update_data):
        
        # Update inherent risk score
        likelihood = update_data.get("inherent_likelihood", risk.inherent_likelihood)
        impact = update_data.get("inherent_impact", risk.inherent_impact)
        if likelihood and impact:
            update_data["inherent_risk_score"] = likelihood * impact
        
        # Update residual risk score
        res_likelihood = update_data.get("residual_likelihood", risk.residual_likelihood)
        res_impact = update_data.get("residual_impact", risk.residual_impact)
        if res_likelihood and res_impact:
            update_data["residual_risk_score"] = res_likelihood * res_impact
            
            # Use residual score for risk level determination
            score = update_data["residual_risk_score"]
        else:
            score = update_data.get("inherent_risk_score", risk.inherent_risk_score)
        
        # Determine risk level
        if score:
            if score <= 5:
                update_data["risk_level"] = "LOW"
            elif score <= 10:
                update_data["risk_level"] = "MEDIUM"
            elif score <= 15:
                update_data["risk_level"] = "HIGH"
            else:
                update_data["risk_level"] = "CRITICAL"
    
    for field, value in update_data.items():
        setattr(risk, field, value)
    
    db.commit()
    db.refresh(risk)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="update",
        entity_type="risk",
        entity_id=risk.id,
        user_id=current_user.id,
        action="Risk updated",
        description=f"Risk updated: {risk.title}",
        old_values=old_values,
        new_values=update_data,
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return risk


@router.delete("/{risk_id}")
async def delete_risk(
    risk_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete risk (set is_active=False)."""
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    
    risk.is_active = False
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="delete",
        entity_type="risk",
        entity_id=risk.id,
        user_id=current_user.id,
        action="Risk deleted",
        description=f"Risk deleted: {risk.title}",
        source="web_ui",
        risk_level="medium"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Risk deleted successfully"}


# Risk Scoring
@router.post("/{risk_id}/scores", response_model=RiskScoreResponse)
async def create_risk_score(
    risk_id: int,
    score: RiskScoreCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new risk score."""
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    
    score_data = score.model_dump()
    score_data["risk_id"] = risk_id
    score_data["scored_by"] = current_user.id
    
    # Calculate total score
    if score_data.get("likelihood_score") and score_data.get("impact_score"):
        score_data["total_score"] = score_data["likelihood_score"] * score_data["impact_score"]
    
    db_score = RiskScore(**score_data)
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    
    return db_score


@router.get("/{risk_id}/scores", response_model=List[RiskScoreResponse])
async def get_risk_scores(
    risk_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all scores for a risk."""
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )
    
    scores = db.query(RiskScore).options(
        joinedload(RiskScore.risk),
        joinedload(RiskScore.scorer)
    ).filter(RiskScore.risk_id == risk_id).all()
    return scores