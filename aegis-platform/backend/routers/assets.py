from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
import io
import json

from database import get_db
from models.user import User
from models.asset import Asset, AssetCategory
from models.audit import AuditLog
from schemas.asset import (
    AssetResponse, AssetCreate, AssetUpdate, AssetImportResponse,
    AssetCategoryResponse, AssetCategoryCreate, AssetCategoryUpdate
)
from auth import get_current_active_user

router = APIRouter()


# Asset Categories
@router.get("/categories/", response_model=List[AssetCategoryResponse])
async def get_asset_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all asset categories."""
    categories = db.query(AssetCategory).filter(AssetCategory.is_active == True).all()
    return categories


@router.post("/categories/", response_model=AssetCategoryResponse)
async def create_asset_category(
    category: AssetCategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new asset category."""
    db_category = AssetCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# Assets
@router.get("/")
async def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    asset_type: Optional[str] = None,
    criticality: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of assets with pagination and filtering."""
    query = db.query(Asset).options(
        joinedload(Asset.category),
        joinedload(Asset.owner),
        joinedload(Asset.creator),
        selectinload(Asset.assessments),
        selectinload(Asset.risks),
        selectinload(Asset.vulnerability_data)
    )
    
    if search:
        query = query.filter(
            (Asset.name.contains(search)) |
            (Asset.hostname.contains(search)) |
            (Asset.ip_address.contains(search))
        )
    
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    
    if criticality:
        query = query.filter(Asset.criticality == criticality)
    
    if category_id:
        query = query.filter(Asset.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(Asset.is_active == is_active)
    
    # Get total count for pagination
    total = query.count()
    assets = query.offset(skip).limit(limit).all()
    
    # Return paginated response structure expected by frontend
    return {
        "items": [AssetResponse.model_validate(asset) for asset in assets],
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/count")
async def get_assets_count(
    search: Optional[str] = None,
    asset_type: Optional[str] = None,
    criticality: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get total count of assets matching filters."""
    query = db.query(func.count(Asset.id))
    
    if search:
        query = query.filter(
            (Asset.name.contains(search)) |
            (Asset.hostname.contains(search)) |
            (Asset.ip_address.contains(search))
        )
    
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    
    if criticality:
        query = query.filter(Asset.criticality == criticality)
    
    if category_id:
        query = query.filter(Asset.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(Asset.is_active == is_active)
    
    count = query.scalar()
    return {"count": count}


@router.get("/summary")
async def get_assets_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get asset summary statistics."""
    total_assets = db.query(func.count(Asset.id)).filter(Asset.is_active == True).scalar()
    
    by_type = db.query(
        Asset.asset_type,
        func.count(Asset.id).label('count')
    ).filter(Asset.is_active == True).group_by(Asset.asset_type).all()
    
    by_criticality = db.query(
        Asset.criticality,
        func.count(Asset.id).label('count')
    ).filter(Asset.is_active == True).group_by(Asset.criticality).all()
    
    return {
        "total_assets": total_assets,
        "by_type": {item.asset_type: item.count for item in by_type},
        "by_criticality": {item.criticality: item.count for item in by_criticality}
    }


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get asset by ID."""
    asset = db.query(Asset).options(
        joinedload(Asset.category),
        joinedload(Asset.owner),
        joinedload(Asset.creator),
        selectinload(Asset.assessments),
        selectinload(Asset.risks),
        selectinload(Asset.vulnerability_data)
    ).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@router.post("/", response_model=AssetResponse)
async def create_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new asset."""
    asset_data = asset.model_dump()
    asset_data["created_by"] = current_user.id
    
    # Convert Pydantic enum values (lowercase) to database enum values (uppercase)
    if "asset_type" in asset_data and asset_data["asset_type"]:
        # Extract the string value from enum object and convert to uppercase
        asset_data["asset_type"] = str(asset_data["asset_type"].value).upper()
    if "criticality" in asset_data and asset_data["criticality"]:
        # Extract the string value from enum object and convert to uppercase
        asset_data["criticality"] = str(asset_data["criticality"].value).upper()
    
    db_asset = Asset(**asset_data)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="asset",
        entity_id=db_asset.id,
        user_id=current_user.id,
        action="Asset created",
        description=f"Asset created: {db_asset.name}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Store old values for audit
    old_values = {
        "name": asset.name,
        "asset_type": asset.asset_type,
        "criticality": asset.criticality,
        "status": asset.status
    }
    
    # Update asset fields
    update_data = asset_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    db.commit()
    db.refresh(asset)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="update",
        entity_type="asset",
        entity_id=asset.id,
        user_id=current_user.id,
        action="Asset updated",
        description=f"Asset updated: {asset.name}",
        old_values=old_values,
        new_values=update_data,
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete asset (set is_active=False)."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    asset.is_active = False
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="delete",
        entity_type="asset",
        entity_id=asset.id,
        user_id=current_user.id,
        action="Asset deleted",
        description=f"Asset deleted: {asset.name}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Asset deleted successfully"}


@router.post("/import", response_model=AssetImportResponse)
async def import_assets(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Import assets from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        success_count = 0
        error_count = 0
        errors = []
        imported_assets = []
        
        for index, row in df.iterrows():
            try:
                # Map CSV columns to asset fields
                asset_data = {
                    "name": row.get("name", ""),
                    "description": row.get("description", ""),
                    "asset_type": row.get("asset_type", "other"),
                    "criticality": row.get("criticality", "medium"),
                    "ip_address": row.get("ip_address", ""),
                    "hostname": row.get("hostname", ""),
                    "operating_system": row.get("operating_system", ""),
                    "location": row.get("location", ""),
                    "environment": row.get("environment", ""),
                    "business_unit": row.get("business_unit", ""),
                    "created_by": current_user.id
                }
                
                # Create asset
                db_asset = Asset(**asset_data)
                db.add(db_asset)
                db.commit()
                db.refresh(db_asset)
                
                imported_assets.append(db_asset)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 1}: {str(e)}")
                db.rollback()
        
        # Log audit event
        audit_log = AuditLog(
            event_type="import",
            entity_type="asset",
            user_id=current_user.id,
            action="Assets imported",
            description=f"Imported {success_count} assets, {error_count} errors",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return AssetImportResponse(
            success_count=success_count,
            error_count=error_count,
            errors=errors,
            imported_assets=imported_assets
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV file: {str(e)}"
        )