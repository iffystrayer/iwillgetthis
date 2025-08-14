"""API endpoints for advanced search functionality"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from database import get_db
from models.user import User
from models.audit import AuditLog
from auth import get_current_active_user
from services.search_service import search_service
from schemas.search import (
    GlobalSearchResponse, SearchSuggestionResponse, AdvancedSearchRequest,
    AdvancedSearchResponse, SearchStatsResponse
)

router = APIRouter()

@router.get("/global", response_model=GlobalSearchResponse)
async def global_search(
    q: str = Query(..., min_length=2, description="Search query"),
    entities: Optional[str] = Query(None, description="Comma-separated list of entities to search"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per entity"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Perform global search across all platform data"""
    
    # Parse entities filter
    entity_list = None
    if entities:
        entity_list = [e.strip() for e in entities.split(',') if e.strip()]
        
        # Validate entity types
        valid_entities = ['risks', 'assets', 'assessments', 'evidence', 'tasks', 'frameworks', 'controls']
        invalid_entities = [e for e in entity_list if e not in valid_entities]
        if invalid_entities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity types: {invalid_entities}. Valid types: {valid_entities}"
            )
    
    try:
        # Perform search
        results = search_service.global_search(
            db=db,
            query=q,
            entities=entity_list,
            limit=limit,
            offset=offset,
            user=current_user
        )
        
        # Log search activity (optional, for analytics)
        if results['total_results'] > 0:
            audit_log = AuditLog(
                event_type="search",
                entity_type="global",
                entity_id=None,
                user_id=current_user.id,
                action="Global search performed",
                description=f"Search query: '{q}', Results: {results['total_results']}",
                source="web_ui",
                risk_level="low"
            )
            db.add(audit_log)
            db.commit()
        
        return GlobalSearchResponse(**results)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get search suggestions based on partial query"""
    
    try:
        suggestions = search_service.search_suggestions(
            db=db,
            partial_query=q,
            limit=limit
        )
        
        return SearchSuggestionResponse(
            query=q,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )

@router.post("/advanced", response_model=AdvancedSearchResponse)
async def advanced_search(
    search_request: AdvancedSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Perform advanced search with specific filters"""
    
    # Validate entity type
    valid_entities = ['risks', 'assets', 'assessments', 'evidence', 'tasks', 'frameworks', 'controls']
    if search_request.entity_type not in valid_entities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {search_request.entity_type}. Valid types: {valid_entities}"
        )
    
    try:
        # Perform advanced search
        results = search_service.advanced_search(
            db=db,
            entity_type=search_request.entity_type,
            filters=search_request.filters,
            user=current_user
        )
        
        # Log search activity
        if results:
            audit_log = AuditLog(
                event_type="search",
                entity_type=search_request.entity_type,
                entity_id=None,
                user_id=current_user.id,
                action="Advanced search performed",
                description=f"Advanced search on {search_request.entity_type}, filters: {search_request.filters}, Results: {len(results)}",
                source="web_ui",
                risk_level="low"
            )
            db.add(audit_log)
            db.commit()
        
        return AdvancedSearchResponse(
            entity_type=search_request.entity_type,
            filters=search_request.filters,
            total_results=len(results),
            results=results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advanced search failed: {str(e)}"
        )

@router.get("/entities")
async def get_searchable_entities(
    current_user: User = Depends(get_current_active_user)
):
    """Get information about searchable entities"""
    
    return {
        "entities": {
            "risks": {
                "name": "Risks",
                "description": "Security risks and threats",
                "searchable_fields": ["title", "description", "category", "mitigation_strategy", "owner"],
                "filterable_fields": ["category", "level", "status", "owner", "due_date"]
            },
            "assets": {
                "name": "Assets",
                "description": "Organizational assets",
                "searchable_fields": ["name", "description", "asset_type", "location", "owner"],
                "filterable_fields": ["asset_type", "criticality", "owner", "location"]
            },
            "assessments": {
                "name": "Assessments",
                "description": "Security assessments",
                "searchable_fields": ["name", "description", "scope", "methodology"],
                "filterable_fields": ["status", "assessment_type", "start_date", "end_date"]
            },
            "evidence": {
                "name": "Evidence",
                "description": "Supporting evidence and documents",
                "searchable_fields": ["name", "description", "file_name", "content_summary"],
                "filterable_fields": ["evidence_type", "file_type", "upload_date"]
            },
            "tasks": {
                "name": "Tasks",
                "description": "Risk management tasks",
                "searchable_fields": ["title", "description", "assigned_to"],
                "filterable_fields": ["status", "priority", "assigned_to", "due_date"]
            },
            "frameworks": {
                "name": "Frameworks",
                "description": "Compliance frameworks",
                "searchable_fields": ["name", "description", "version"],
                "filterable_fields": ["framework_type", "version", "is_active"]
            },
            "controls": {
                "name": "Controls",
                "description": "Security controls",
                "searchable_fields": ["control_id", "name", "description", "guidance"],
                "filterable_fields": ["category", "control_family", "implementation_status"]
            }
        },
        "total_entities": 7
    }

@router.get("/stats", response_model=SearchStatsResponse)
async def get_search_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get search usage statistics"""
    
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        # Get search logs from audit table
        search_logs = db.query(AuditLog).filter(
            and_(
                AuditLog.event_type == "search",
                AuditLog.timestamp >= start_date,
                AuditLog.user_id == current_user.id
            )
        ).all()
        
        total_searches = len(search_logs)
        
        # Count by entity type
        entity_counts = {}
        query_terms = []
        
        for log in search_logs:
            entity_type = log.entity_type or "global"
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            # Extract query terms from description
            if log.description and "query:" in log.description.lower():
                try:
                    query_part = log.description.split("query:")[1].split(",")[0].strip().strip("'\"")
                    if query_part and len(query_part) > 2:
                        query_terms.append(query_part.lower())
                except:
                    pass
        
        # Find most common search terms
        from collections import Counter
        term_counter = Counter(query_terms)
        popular_terms = [{"term": term, "count": count} for term, count in term_counter.most_common(10)]
        
        return SearchStatsResponse(
            period_days=days,
            total_searches=total_searches,
            searches_by_entity=entity_counts,
            popular_search_terms=popular_terms,
            average_daily_searches=round(total_searches / days, 1) if days > 0 else 0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search statistics: {str(e)}"
        )