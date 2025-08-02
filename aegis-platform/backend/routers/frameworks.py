from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from database import get_db
from models.user import User
from models.framework import Framework, Control, ControlMapping
from models.audit import AuditLog
from schemas.framework import (
    FrameworkResponse, FrameworkCreate, FrameworkUpdate,
    ControlResponse, ControlCreate, ControlUpdate,
    ControlMappingResponse, ControlMappingCreate
)
from auth import get_current_active_user

router = APIRouter()


# Frameworks
@router.get("/", response_model=List[FrameworkResponse])
async def get_frameworks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of frameworks with pagination and filtering."""
    query = db.query(Framework)
    
    if search:
        query = query.filter(
            (Framework.name.contains(search)) |
            (Framework.description.contains(search))
        )
    
    if is_active is not None:
        query = query.filter(Framework.is_active == is_active)
    
    frameworks = query.offset(skip).limit(limit).all()
    return frameworks


@router.get("/{framework_id}", response_model=FrameworkResponse)
async def get_framework(
    framework_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get framework by ID."""
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found"
        )
    return framework


@router.post("/", response_model=FrameworkResponse)
async def create_framework(
    framework: FrameworkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new framework."""
    db_framework = Framework(**framework.model_dump())
    db.add(db_framework)
    db.commit()
    db.refresh(db_framework)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="framework",
        entity_id=db_framework.id,
        user_id=current_user.id,
        action="Framework created",
        description=f"Framework created: {db_framework.name}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_framework


@router.put("/{framework_id}", response_model=FrameworkResponse)
async def update_framework(
    framework_id: int,
    framework_update: FrameworkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update framework."""
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found"
        )
    
    # Update framework fields
    update_data = framework_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(framework, field, value)
    
    db.commit()
    db.refresh(framework)
    
    return framework


# Controls
@router.get("/{framework_id}/controls", response_model=List[ControlResponse])
async def get_framework_controls(
    framework_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=5000),
    search: Optional[str] = None,
    level: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get controls for a specific framework."""
    # Verify framework exists
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found"
        )
    
    query = db.query(Control).filter(Control.framework_id == framework_id)
    
    if search:
        query = query.filter(
            (Control.control_id.contains(search)) |
            (Control.title.contains(search)) |
            (Control.description.contains(search))
        )
    
    if level is not None:
        query = query.filter(Control.level == level)
    
    controls = query.order_by(Control.sort_order, Control.control_id).offset(skip).limit(limit).all()
    return controls


@router.get("/controls/{control_id}", response_model=ControlResponse)
async def get_control(
    control_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get control by ID."""
    control = db.query(Control).filter(Control.id == control_id).first()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found"
        )
    return control


@router.post("/{framework_id}/controls", response_model=ControlResponse)
async def create_control(
    framework_id: int,
    control: ControlCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new control for a framework."""
    # Verify framework exists
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found"
        )
    
    control_data = control.model_dump()
    control_data["framework_id"] = framework_id
    
    db_control = Control(**control_data)
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    
    return db_control


@router.put("/controls/{control_id}", response_model=ControlResponse)
async def update_control(
    control_id: int,
    control_update: ControlUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update control."""
    control = db.query(Control).filter(Control.id == control_id).first()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found"
        )
    
    # Update control fields
    update_data = control_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(control, field, value)
    
    db.commit()
    db.refresh(control)
    
    return control


# Control Mappings
@router.get("/controls/{control_id}/mappings", response_model=List[ControlMappingResponse])
async def get_control_mappings(
    control_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mappings for a specific control."""
    control = db.query(Control).filter(Control.id == control_id).first()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found"
        )
    
    mappings = db.query(ControlMapping).filter(ControlMapping.control_id == control_id).all()
    return mappings


@router.post("/controls/{control_id}/mappings", response_model=ControlMappingResponse)
async def create_control_mapping(
    control_id: int,
    mapping: ControlMappingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new control mapping."""
    control = db.query(Control).filter(Control.id == control_id).first()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found"
        )
    
    mapping_data = mapping.model_dump()
    mapping_data["control_id"] = control_id
    
    db_mapping = ControlMapping(**mapping_data)
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    
    return db_mapping