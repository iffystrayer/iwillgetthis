from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
import hashlib
import aiofiles
from pathlib import Path

from database import get_db
from models.user import User
from models.evidence import Evidence, EvidenceControl
from models.audit import AuditLog
from schemas.evidence import (
    EvidenceResponse, EvidenceCreate, EvidenceUpdate, EvidenceUpload,
    EvidenceControlResponse, EvidenceControlCreate
)
from auth import get_current_active_user
from config import settings

router = APIRouter()


@router.get("/", response_model=List[EvidenceResponse])
async def get_evidence(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    evidence_type: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of evidence with pagination and filtering."""
    query = db.query(Evidence)
    
    if search:
        query = query.filter(
            (Evidence.title.contains(search)) |
            (Evidence.description.contains(search)) |
            (Evidence.file_name.contains(search))
        )
    
    if evidence_type:
        query = query.filter(Evidence.evidence_type == evidence_type)
    
    if status:
        query = query.filter(Evidence.status == status)
    
    if category:
        query = query.filter(Evidence.category == category)
    
    evidence = query.filter(Evidence.is_active == True).offset(skip).limit(limit).all()
    return evidence


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence_item(
    evidence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get evidence item by ID."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    return evidence


@router.post("/", response_model=EvidenceResponse)
async def create_evidence(
    evidence: EvidenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new evidence record."""
    evidence_data = evidence.model_dump()
    evidence_data["uploaded_by_id"] = current_user.id
    
    db_evidence = Evidence(**evidence_data)
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="evidence",
        entity_id=db_evidence.id,
        user_id=current_user.id,
        action="Evidence created",
        description=f"Evidence created: {db_evidence.title}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_evidence


@router.post("/upload", response_model=EvidenceResponse)
async def upload_evidence(
    file: UploadFile = File(...),
    title: str = Query(...),
    description: Optional[str] = Query(None),
    evidence_type: str = Query(...),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload evidence file."""
    # Validate file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path(settings.uploads_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{current_user.id}_{int(datetime.now().timestamp())}_{file.filename}"
    file_path = upload_dir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Calculate file hash
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Create evidence record
    evidence_data = {
        "title": title,
        "description": description,
        "evidence_type": evidence_type,
        "category": category,
        "file_name": file.filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "file_type": file.content_type,
        "file_hash": file_hash,
        "uploaded_by_id": current_user.id
    }
    
    db_evidence = Evidence(**evidence_data)
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="upload",
        entity_type="evidence",
        entity_id=db_evidence.id,
        user_id=current_user.id,
        action="Evidence uploaded",
        description=f"Evidence file uploaded: {file.filename}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_evidence


@router.put("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: int,
    evidence_update: EvidenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update evidence record."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    # Store old values for audit
    old_values = {
        "title": evidence.title,
        "status": evidence.status,
        "access_level": evidence.access_level
    }
    
    # Update evidence fields
    update_data = evidence_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evidence, field, value)
    
    db.commit()
    db.refresh(evidence)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="update",
        entity_type="evidence",
        entity_id=evidence.id,
        user_id=current_user.id,
        action="Evidence updated",
        description=f"Evidence updated: {evidence.title}",
        old_values=old_values,
        new_values=update_data,
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return evidence


@router.delete("/{evidence_id}")
async def delete_evidence(
    evidence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete evidence (set is_active=False)."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    evidence.is_active = False
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="delete",
        entity_type="evidence",
        entity_id=evidence.id,
        user_id=current_user.id,
        action="Evidence deleted",
        description=f"Evidence deleted: {evidence.title}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Evidence deleted successfully"}


@router.post("/{evidence_id}/review")
async def review_evidence(
    evidence_id: int,
    approved: bool,
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Review and approve/reject evidence."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    evidence.status = "approved" if approved else "rejected"
    evidence.reviewed_by_id = current_user.id
    evidence.reviewed_at = datetime.utcnow()
    evidence.review_comments = comments
    
    db.commit()
    
    # Log audit event
    action = "Evidence approved" if approved else "Evidence rejected"
    audit_log = AuditLog(
        event_type="review",
        entity_type="evidence",
        entity_id=evidence.id,
        user_id=current_user.id,
        action=action,
        description=f"{action}: {evidence.title}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": f"Evidence {evidence.status} successfully"}


# Evidence-Control Links
@router.get("/{evidence_id}/controls", response_model=List[EvidenceControlResponse])
async def get_evidence_controls(
    evidence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get controls linked to evidence."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    controls = db.query(EvidenceControl).filter(
        EvidenceControl.evidence_id == evidence_id
    ).all()
    
    return controls


@router.post("/{evidence_id}/controls", response_model=EvidenceControlResponse)
async def link_evidence_control(
    evidence_id: int,
    control_link: EvidenceControlCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Link evidence to a control."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    link_data = control_link.model_dump()
    link_data["evidence_id"] = evidence_id
    link_data["created_by"] = current_user.id
    
    db_link = EvidenceControl(**link_data)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    
    return db_link


@router.delete("/{evidence_id}/controls/{control_link_id}")
async def unlink_evidence_control(
    evidence_id: int,
    control_link_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlink evidence from a control."""
    link = db.query(EvidenceControl).filter(
        EvidenceControl.id == control_link_id,
        EvidenceControl.evidence_id == evidence_id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence-control link not found"
        )
    
    db.delete(link)
    db.commit()
    
    return {"message": "Evidence-control link removed successfully"}