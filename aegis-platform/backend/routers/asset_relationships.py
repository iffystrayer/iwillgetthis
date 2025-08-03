"""
Asset Relationships and Dependencies API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
import json
import time
from datetime import datetime

from database import get_db
from models.user import User
from models.asset import Asset
from models.asset_relationship import AssetRelationship, AssetDependencyGraph, AssetImpactScenario
from models.audit import AuditLog
from schemas.asset_relationship import (
    AssetRelationshipResponse, AssetRelationshipCreate, AssetRelationshipUpdate,
    BulkRelationshipImport, BulkRelationshipImportResponse,
    DependencyGraph, ImpactAnalysis, NetworkDiscoveryRequest, NetworkDiscoveryResponse,
    AssetDependencyGraphResponse, AssetImpactScenarioResponse
)
from auth import get_current_active_user
from asset_dependency_analyzer import AssetDependencyAnalyzer

router = APIRouter()


# Relationship CRUD Operations
@router.get("/", response_model=List[AssetRelationshipResponse])
async def get_asset_relationships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source_asset_id: Optional[int] = None,
    target_asset_id: Optional[int] = None,
    relationship_type: Optional[str] = None,
    relationship_strength: Optional[str] = None,
    is_validated: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get asset relationships with filtering"""
    query = db.query(AssetRelationship).filter(AssetRelationship.is_active == True)
    
    if source_asset_id:
        query = query.filter(AssetRelationship.source_asset_id == source_asset_id)
    
    if target_asset_id:
        query = query.filter(AssetRelationship.target_asset_id == target_asset_id)
    
    if relationship_type:
        query = query.filter(AssetRelationship.relationship_type == relationship_type)
    
    if relationship_strength:
        query = query.filter(AssetRelationship.relationship_strength == relationship_strength)
    
    if is_validated is not None:
        query = query.filter(AssetRelationship.is_validated == is_validated)
    
    relationships = query.offset(skip).limit(limit).all()
    return relationships


@router.post("/", response_model=AssetRelationshipResponse)
async def create_asset_relationship(
    relationship: AssetRelationshipCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new asset relationship"""
    
    # Validate that both assets exist
    source_asset = db.query(Asset).filter(Asset.id == relationship.source_asset_id).first()
    target_asset = db.query(Asset).filter(Asset.id == relationship.target_asset_id).first()
    
    if not source_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source asset {relationship.source_asset_id} not found"
        )
    
    if not target_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target asset {relationship.target_asset_id} not found"
        )
    
    # Check for duplicate relationships
    existing = db.query(AssetRelationship).filter(
        AssetRelationship.source_asset_id == relationship.source_asset_id,
        AssetRelationship.target_asset_id == relationship.target_asset_id,
        AssetRelationship.relationship_type == relationship.relationship_type,
        AssetRelationship.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Relationship already exists"
        )
    
    # Create relationship
    relationship_data = relationship.model_dump()
    relationship_data["created_by"] = current_user.id
    
    db_relationship = AssetRelationship(**relationship_data)
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="create",
        entity_type="asset_relationship",
        entity_id=db_relationship.id,
        user_id=current_user.id,
        action="Asset relationship created",
        description=f"Relationship created: {source_asset.name} -> {target_asset.name}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return db_relationship


@router.get("/{relationship_id}", response_model=AssetRelationshipResponse)
async def get_asset_relationship(
    relationship_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific asset relationship"""
    relationship = db.query(AssetRelationship).filter(AssetRelationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found"
        )
    return relationship


@router.put("/{relationship_id}", response_model=AssetRelationshipResponse)
async def update_asset_relationship(
    relationship_id: int,
    relationship_update: AssetRelationshipUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update asset relationship"""
    relationship = db.query(AssetRelationship).filter(AssetRelationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found"
        )
    
    # Update fields
    update_data = relationship_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relationship, field, value)
    
    # Update validation timestamp if is_validated was set to True
    if update_data.get("is_validated") is True:
        relationship.last_validated = datetime.utcnow()
    
    db.commit()
    db.refresh(relationship)
    
    # Log audit event
    audit_log = AuditLog(
        event_type="update",
        entity_type="asset_relationship",
        entity_id=relationship.id,
        user_id=current_user.id,
        action="Asset relationship updated",
        description=f"Relationship updated: {relationship_id}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return relationship


@router.delete("/{relationship_id}")
async def delete_asset_relationship(
    relationship_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete asset relationship (soft delete)"""
    relationship = db.query(AssetRelationship).filter(AssetRelationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found"
        )
    
    relationship.is_active = False
    db.commit()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="delete",
        entity_type="asset_relationship",
        entity_id=relationship.id,
        user_id=current_user.id,
        action="Asset relationship deleted",
        description=f"Relationship deleted: {relationship_id}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Relationship deleted successfully"}


# Dependency Analysis
@router.get("/{asset_id}/dependency-graph")
async def get_asset_dependency_graph(
    asset_id: int,
    max_depth: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dependency graph for an asset"""
    
    # Verify asset exists
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    analyzer = AssetDependencyAnalyzer(db)
    dependency_graph = analyzer.build_dependency_graph(asset_id, max_depth)
    
    return dependency_graph


@router.get("/{asset_id}/impact-analysis")
async def get_asset_impact_analysis(
    asset_id: int,
    scenario: str = Query("complete_failure", description="Failure scenario to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get impact analysis for asset failure scenarios"""
    
    # Verify asset exists
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    analyzer = AssetDependencyAnalyzer(db)
    impact_analysis = analyzer.analyze_impact_scenario(asset_id, scenario)
    
    return impact_analysis


@router.get("/{asset_id}/risk-metrics")
async def get_asset_risk_metrics(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk metrics for an asset"""
    
    # Verify asset exists
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    analyzer = AssetDependencyAnalyzer(db)
    risk_metrics = analyzer.calculate_risk_metrics(asset_id)
    
    return {
        "asset_id": asset_id,
        "asset_name": asset.name,
        "risk_metrics": risk_metrics,
        "calculated_at": datetime.utcnow().isoformat()
    }


@router.post("/network-map")
async def get_network_map(
    asset_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get network map showing relationships between assets"""
    
    if len(asset_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 assets allowed for network map"
        )
    
    analyzer = AssetDependencyAnalyzer(db)
    network_map = analyzer.get_asset_network_map(asset_ids)
    
    return network_map


# Bulk Operations
@router.post("/bulk-import", response_model=BulkRelationshipImportResponse)
async def bulk_import_relationships(
    import_data: BulkRelationshipImport,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk import asset relationships"""
    
    success_count = 0
    error_count = 0
    errors = []
    created_relationships = []
    
    for i, relationship in enumerate(import_data.relationships):
        try:
            # Validate assets exist if requested
            if import_data.validate_assets:
                source_asset = db.query(Asset).filter(Asset.id == relationship.source_asset_id).first()
                target_asset = db.query(Asset).filter(Asset.id == relationship.target_asset_id).first()
                
                if not source_asset:
                    raise ValueError(f"Source asset {relationship.source_asset_id} not found")
                if not target_asset:
                    raise ValueError(f"Target asset {relationship.target_asset_id} not found")
            
            # Check for duplicates
            existing = db.query(AssetRelationship).filter(
                AssetRelationship.source_asset_id == relationship.source_asset_id,
                AssetRelationship.target_asset_id == relationship.target_asset_id,
                AssetRelationship.relationship_type == relationship.relationship_type,
                AssetRelationship.is_active == True
            ).first()
            
            if existing:
                raise ValueError("Relationship already exists")
            
            # Create relationship
            relationship_data = relationship.model_dump()
            relationship_data["created_by"] = current_user.id
            
            db_relationship = AssetRelationship(**relationship_data)
            db.add(db_relationship)
            db.commit()
            db.refresh(db_relationship)
            
            created_relationships.append(db_relationship)
            success_count += 1
            
            # Create reverse relationship if requested
            if import_data.auto_create_reverse:
                reverse_rel_data = relationship_data.copy()
                reverse_rel_data["source_asset_id"] = relationship.target_asset_id
                reverse_rel_data["target_asset_id"] = relationship.source_asset_id
                
                reverse_relationship = AssetRelationship(**reverse_rel_data)
                db.add(reverse_relationship)
                db.commit()
                db.refresh(reverse_relationship)
                
                created_relationships.append(reverse_relationship)
                success_count += 1
                
        except Exception as e:
            error_count += 1
            errors.append(f"Relationship {i + 1}: {str(e)}")
            db.rollback()
    
    # Log audit event
    audit_log = AuditLog(
        event_type="import",
        entity_type="asset_relationship",
        user_id=current_user.id,
        action="Bulk relationships imported",
        description=f"Imported {success_count} relationships, {error_count} errors",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return BulkRelationshipImportResponse(
        success_count=success_count,
        error_count=error_count,
        errors=errors,
        created_relationships=created_relationships
    )


@router.post("/discover", response_model=NetworkDiscoveryResponse)
async def discover_asset_relationships(
    discovery_request: NetworkDiscoveryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Discover asset relationships automatically (mock implementation)"""
    
    start_time = time.time()
    discovered_relationships = []
    
    # Mock discovery logic - in real implementation, this would:
    # - Scan network connections
    # - Analyze configuration files
    # - Parse log files
    # - Query monitoring systems
    
    for source_asset_id in discovery_request.source_asset_ids:
        # Simulate discovering relationships
        mock_targets = [id + 1 for id in discovery_request.source_asset_ids if id + 1 != source_asset_id]
        
        for target_id in mock_targets[:discovery_request.scan_depth]:
            # Check if assets exist
            source_asset = db.query(Asset).filter(Asset.id == source_asset_id).first()
            target_asset = db.query(Asset).filter(Asset.id == target_id).first()
            
            if source_asset and target_asset:
                # Create mock relationship
                relationship_data = {
                    "source_asset_id": source_asset_id,
                    "target_asset_id": target_id,
                    "relationship_type": "communicates_with",
                    "relationship_strength": "moderate",
                    "description": f"Discovered via {discovery_request.discovery_method}",
                    "discovered_method": discovery_request.discovery_method,
                    "is_validated": discovery_request.auto_validate,
                    "created_by": current_user.id
                }
                
                db_relationship = AssetRelationship(**relationship_data)
                db.add(db_relationship)
                db.commit()
                db.refresh(db_relationship)
                
                discovered_relationships.append(db_relationship)
    
    scan_duration = time.time() - start_time
    
    # Log audit event
    audit_log = AuditLog(
        event_type="discovery",
        entity_type="asset_relationship",
        user_id=current_user.id,
        action="Network discovery performed",
        description=f"Discovered {len(discovered_relationships)} relationships",
        source="automated_discovery",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return NetworkDiscoveryResponse(
        discovered_relationships=discovered_relationships,
        discovery_summary={
            "method": discovery_request.discovery_method,
            "scan_depth": discovery_request.scan_depth,
            "source_assets": len(discovery_request.source_asset_ids)
        },
        scan_duration_seconds=scan_duration,
        assets_scanned=len(discovery_request.source_asset_ids),
        relationships_found=len(discovered_relationships),
        validation_results={
            "auto_validated": discovery_request.auto_validate,
            "validation_rate": 1.0 if discovery_request.auto_validate else 0.0
        }
    )


# Statistics and Summary
@router.get("/statistics/summary")
async def get_relationship_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get relationship statistics and summary"""
    
    total_relationships = db.query(func.count(AssetRelationship.id)).filter(
        AssetRelationship.is_active == True
    ).scalar()
    
    by_type = db.query(
        AssetRelationship.relationship_type,
        func.count(AssetRelationship.id).label('count')
    ).filter(AssetRelationship.is_active == True).group_by(AssetRelationship.relationship_type).all()
    
    by_strength = db.query(
        AssetRelationship.relationship_strength,
        func.count(AssetRelationship.id).label('count')
    ).filter(AssetRelationship.is_active == True).group_by(AssetRelationship.relationship_strength).all()
    
    validated_count = db.query(func.count(AssetRelationship.id)).filter(
        AssetRelationship.is_active == True,
        AssetRelationship.is_validated == True
    ).scalar()
    
    return {
        "total_relationships": total_relationships,
        "validated_relationships": validated_count,
        "validation_rate": validated_count / total_relationships if total_relationships > 0 else 0,
        "by_type": {item.relationship_type.value: item.count for item in by_type},
        "by_strength": {item.relationship_strength.value: item.count for item in by_strength}
    }