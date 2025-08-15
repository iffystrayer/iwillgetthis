"""API endpoints for bulk operations (import/export)"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Path as PathParam, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import os
import logging

from database import get_db
from models.user import User
from models.audit import AuditLog
from auth import get_current_active_user
from services.bulk_operations import bulk_operations_service
from schemas.bulk_operations import (
    BulkImportResponse, BulkExportRequest, BulkExportResponse,
    BulkValidationResponse, BulkTemplateResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Template Generation Endpoints
@router.get("/templates/risks/{format_type}", response_class=FileResponse)
async def download_risk_template(
    format_type: str = PathParam(..., pattern="^(xlsx|csv)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Download risk import template"""
    try:
        template_path = bulk_operations_service.generate_risk_template(format_type)
        
        # Get filename for download
        filename = Path(template_path).name
        
        return FileResponse(
            path=template_path,
            filename=filename,
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Failed to generate risk template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate template: {str(e)}"
        )

@router.get("/templates/controls/{format_type}", response_class=FileResponse)
async def download_control_template(
    format_type: str = PathParam(..., pattern="^(xlsx|csv)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Download control import template"""
    try:
        template_path = bulk_operations_service.generate_control_template(format_type)
        
        # Get filename for download
        filename = Path(template_path).name
        
        return FileResponse(
            path=template_path,
            filename=filename,
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Failed to generate control template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate template: {str(e)}"
        )

# Import Validation Endpoint
@router.post("/validate", response_model=BulkValidationResponse)
async def validate_import_file(
    entity_type: str = Query(..., pattern="^(risks|controls)$"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Validate import file without importing"""
    
    # Check file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.csv', '.xlsx', '.xls', '.json']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Use CSV, Excel, or JSON"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Parse and validate file
        data, parse_errors = bulk_operations_service.parse_import_file(temp_file_path, entity_type)
        validation_errors = bulk_operations_service.validate_import_data(data, entity_type)
        
        all_errors = parse_errors + validation_errors
        
        return BulkValidationResponse(
            is_valid=len(all_errors) == 0,
            total_records=len(data),
            valid_records=len(data) - len([e for e in all_errors if "Row" in e]),
            errors=all_errors[:50],  # Limit to first 50 errors
            warnings=[]
        )
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

# Import Endpoints
@router.post("/import/risks", response_model=BulkImportResponse)
async def import_risks(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    update_existing: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Import risks from file"""
    
    # Check file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.csv', '.xlsx', '.xls', '.json']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Use CSV, Excel, or JSON"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Parse file
        data, parse_errors = bulk_operations_service.parse_import_file(temp_file_path, "risks")
        
        if parse_errors:
            return BulkImportResponse(
                success=False,
                total_processed=0,
                successful_imports=0,
                failed_imports=0,
                updated_records=0,
                errors=parse_errors,
                imported_ids=[]
            )
        
        # Validate data
        validation_errors = bulk_operations_service.validate_import_data(data, "risks")
        if validation_errors:
            return BulkImportResponse(
                success=False,
                total_processed=len(data),
                successful_imports=0,
                failed_imports=len(data),
                updated_records=0,
                errors=validation_errors,
                imported_ids=[]
            )
        
        # Import risks
        results = bulk_operations_service.import_risks(data, current_user, db, update_existing)
        
        # Log bulk import
        audit_log = AuditLog(
            event_type="bulk_import",
            entity_type="risk",
            entity_id=None,
            user_id=current_user.id,
            action="Bulk risk import",
            description=f"Imported {results['successful_imports']} risks, updated {results['updated_records']} risks from file {file.filename}",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return BulkImportResponse(
            success=results['failed_imports'] == 0,
            total_processed=results['total_processed'],
            successful_imports=results['successful_imports'],
            failed_imports=results['failed_imports'],
            updated_records=results['updated_records'],
            errors=results['errors'],
            imported_ids=results['imported_ids']
        )
        
    except Exception as e:
        logger.error(f"Risk import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

# Export Endpoints
@router.post("/export/risks", response_class=FileResponse)
async def export_risks(
    format_type: str = Query("xlsx", pattern="^(xlsx|csv|json)$"),
    category: Optional[str] = None,
    level: Optional[str] = None,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export risks to file"""
    
    try:
        # Build filters
        filters = {}
        if category:
            filters['category'] = category
        if level:
            filters['level'] = level
        if status:
            filters['status'] = status
        if owner:
            filters['owner'] = owner
        
        # Export risks
        export_path = bulk_operations_service.export_risks(db, format_type, filters)
        
        # Get filename for download
        filename = Path(export_path).name
        
        # Log export
        audit_log = AuditLog(
            event_type="bulk_export",
            entity_type="risk",
            entity_id=None,
            user_id=current_user.id,
            action="Bulk risk export",
            description=f"Exported risks to {format_type} format with filters: {filters}",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return FileResponse(
            path=export_path,
            filename=filename,
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Risk export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )

# Bulk Operations Status and History
@router.get("/history")
async def get_bulk_operations_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    operation_type: Optional[str] = Query(None, pattern="^(import|export)$"),
    entity_type: Optional[str] = Query(None, pattern="^(risk|control)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get bulk operations history"""
    
    query = db.query(AuditLog).filter(
        AuditLog.user_id == current_user.id,
        AuditLog.event_type.in_(["bulk_import", "bulk_export"])
    )
    
    if operation_type:
        if operation_type == "import":
            query = query.filter(AuditLog.event_type == "bulk_import")
        else:
            query = query.filter(AuditLog.event_type == "bulk_export")
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    history = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "operation_type": "import" if log.event_type == "bulk_import" else "export",
            "entity_type": log.entity_type,
            "description": log.description,
            "timestamp": log.timestamp,
            "status": "success" if log.risk_level == "low" else "failed"
        }
        for log in history
    ]

# System Information
@router.get("/info")
async def get_bulk_operations_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get bulk operations system information"""
    
    return {
        "supported_formats": {
            "import": ["csv", "xlsx", "xls", "json"],
            "export": ["csv", "xlsx", "json"]
        },
        "entity_types": ["risks", "controls"],
        "max_file_size": "50MB",
        "max_records_per_import": 1000,
        "supported_encodings": ["utf-8", "utf-8-sig"],
        "template_fields": {
            "risks": [
                "title", "description", "category", "level", "risk_score",
                "impact", "likelihood", "status", "owner", "due_date",
                "mitigation_strategy", "residual_risk", "controls", "tags"
            ],
            "controls": [
                "control_id", "name", "description", "category", "control_type",
                "implementation_status", "effectiveness", "test_frequency",
                "last_tested", "next_test_date", "owner", "evidence_required",
                "framework_id"
            ]
        }
    }