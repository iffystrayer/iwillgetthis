"""API endpoints for comprehensive audit trail functionality"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from auth import get_current_active_user
from services.audit_service import audit_service
from schemas.audit import (
    AuditEventCreate, AuditEventBulkCreate, AuditEventResponse,
    AuditTrailFilter, AuditTrailResponse, UserActivitySummary,
    SecurityEventSummary, ComplianceReportRequest, ComplianceReport,
    AnomalyDetectionRequest, AnomalyDetectionResponse,
    AuditExportRequest, AuditExportResponse, AuditSearchRequest,
    AuditSearchResponse, AuditStatistics, SystemHealthMetrics
)

router = APIRouter()

@router.post("/events", response_model=AuditEventResponse)
async def create_audit_event(
    event: AuditEventCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new audit event"""
    
    try:
        # Extract client information
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Create audit event
        audit_log = audit_service.log_event(
            db=db,
            event_type=event.event_type,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            user_id=current_user.id,
            action=event.action,
            description=event.description,
            details=event.details,
            source=event.source.value,
            ip_address=event.ip_address or client_ip,
            user_agent=event.user_agent or user_agent,
            risk_level=event.risk_level.value
        )
        
        return AuditEventResponse(
            id=audit_log.id,
            event_type=audit_log.event_type,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            user_id=audit_log.user_id,
            action=audit_log.action,
            description=audit_log.description,
            source=audit_log.source,
            ip_address=audit_log.ip_address,
            user_agent=audit_log.user_agent,
            risk_level=audit_log.risk_level,
            timestamp=audit_log.timestamp
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit event: {str(e)}"
        )

@router.post("/events/bulk", response_model=List[AuditEventResponse])
async def create_audit_events_bulk(
    bulk_events: AuditEventBulkCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create multiple audit events in bulk"""
    
    try:
        # Extract client information
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Prepare events for bulk creation
        events_data = []
        for event in bulk_events.events:
            events_data.append({
                'event_type': event.event_type,
                'entity_type': event.entity_type,
                'entity_id': event.entity_id,
                'user_id': current_user.id,
                'action': event.action,
                'description': event.description,
                'details': event.details,
                'source': event.source.value,
                'ip_address': event.ip_address or client_ip,
                'user_agent': event.user_agent or user_agent,
                'risk_level': event.risk_level.value
            })
        
        # Create events in bulk
        audit_logs = audit_service.bulk_log_events(db=db, events=events_data)
        
        # Format response
        return [
            AuditEventResponse(
                id=log.id,
                event_type=log.event_type,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                user_id=log.user_id,
                action=log.action,
                description=log.description,
                source=log.source,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                risk_level=log.risk_level,
                timestamp=log.timestamp
            )
            for log in audit_logs
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bulk audit events: {str(e)}"
        )

@router.get("/trail", response_model=AuditTrailResponse)
async def get_audit_trail(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (ISO format)"),
    include_details: bool = Query(False, description="Include event details"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve audit trail with filtering and pagination"""
    
    try:
        # Get audit trail
        result = audit_service.get_audit_trail(
            db=db,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            event_type=event_type,
            risk_level=risk_level,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            include_details=include_details
        )
        
        # Format response
        events = [
            AuditEventResponse(**event_data)
            for event_data in result['results']
        ]
        
        return AuditTrailResponse(
            total_count=result['total_count'],
            results=events,
            limit=result['limit'],
            offset=result['offset'],
            has_more=result['has_more'],
            filters_applied={
                'entity_type': entity_type,
                'entity_id': entity_id,
                'user_id': user_id,
                'event_type': event_type,
                'risk_level': risk_level,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit trail: {str(e)}"
        )

@router.get("/user/{user_id}/activity", response_model=UserActivitySummary)
async def get_user_activity_summary(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user activity summary"""
    
    # Check if user can access this data (admin or own data)
    if current_user.role not in ["admin", "system_admin"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's activity"
        )
    
    try:
        summary = audit_service.get_user_activity_summary(
            db=db,
            user_id=user_id,
            days=days
        )
        
        return UserActivitySummary(**summary)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user activity summary: {str(e)}"
        )

@router.get("/security-events", response_model=SecurityEventSummary)
async def get_security_events(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    risk_level: str = Query("high", regex="^(low|medium|high|critical)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get security-related events for monitoring"""
    
    # Only admin users can access security events
    if current_user.role not in ["admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view security events"
        )
    
    try:
        security_events = audit_service.get_security_events(
            db=db,
            days=days,
            risk_level=risk_level
        )
        
        return SecurityEventSummary(**security_events)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security events: {str(e)}"
        )

@router.post("/compliance-report", response_model=ComplianceReport)
async def generate_compliance_report(
    report_request: ComplianceReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate compliance audit report for regulatory requirements"""
    
    # Only admin users can generate compliance reports
    if current_user.role not in ["admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to generate compliance reports"
        )
    
    try:
        report = audit_service.generate_compliance_report(
            db=db,
            start_date=report_request.start_date,
            end_date=report_request.end_date,
            entity_types=report_request.entity_types
        )
        
        return ComplianceReport(**report)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compliance report: {str(e)}"
        )

@router.post("/anomaly-detection", response_model=AnomalyDetectionResponse)
async def detect_anomalous_activity(
    detection_request: AnomalyDetectionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Detect potentially anomalous user activity patterns"""
    
    # Check if user can access this data (admin or own data)
    if current_user.role not in ["admin", "system_admin"] and current_user.id != detection_request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this user's activity"
        )
    
    try:
        anomalies = audit_service.detect_anomalous_activity(
            db=db,
            user_id=detection_request.user_id,
            days=detection_request.analysis_days
        )
        
        return AnomalyDetectionResponse(**anomalies)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect anomalous activity: {str(e)}"
        )

@router.post("/export", response_model=AuditExportResponse)
async def export_audit_trail(
    export_request: AuditExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export audit trail data for external analysis or compliance"""
    
    # Only admin users can export audit data
    if current_user.role not in ["admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export audit data"
        )
    
    try:
        export_data = audit_service.export_audit_trail(
            db=db,
            start_date=export_request.start_date,
            end_date=export_request.end_date,
            format=export_request.format,
            entity_types=export_request.entity_types
        )
        
        return AuditExportResponse(**export_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export audit trail: {str(e)}"
        )

@router.post("/search", response_model=AuditSearchResponse)
async def search_audit_trail(
    search_request: AuditSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search audit trail with text-based queries"""
    
    from sqlalchemy import or_, and_
    from models.audit import AuditLog
    import time
    
    try:
        start_time = time.time()
        
        # Build base query
        query = db.query(AuditLog)
        
        # Apply filters if provided
        if search_request.filters:
            filters = []
            if search_request.filters.entity_type:
                filters.append(AuditLog.entity_type == search_request.filters.entity_type)
            if search_request.filters.entity_id is not None:
                filters.append(AuditLog.entity_id == search_request.filters.entity_id)
            if search_request.filters.user_id is not None:
                filters.append(AuditLog.user_id == search_request.filters.user_id)
            if search_request.filters.event_type:
                filters.append(AuditLog.event_type == search_request.filters.event_type)
            if search_request.filters.risk_level:
                filters.append(AuditLog.risk_level == search_request.filters.risk_level.value)
            if search_request.filters.start_date:
                filters.append(AuditLog.timestamp >= search_request.filters.start_date)
            if search_request.filters.end_date:
                filters.append(AuditLog.timestamp <= search_request.filters.end_date)
            if search_request.filters.source:
                filters.append(AuditLog.source == search_request.filters.source.value)
            
            if filters:
                query = query.filter(and_(*filters))
        
        # Apply text search
        search_conditions = []
        for field in search_request.search_fields:
            if field == "action" and hasattr(AuditLog, 'action'):
                search_conditions.append(AuditLog.action.ilike(f"%{search_request.query}%"))
            elif field == "description" and hasattr(AuditLog, 'description'):
                search_conditions.append(AuditLog.description.ilike(f"%{search_request.query}%"))
            elif field == "event_type" and hasattr(AuditLog, 'event_type'):
                search_conditions.append(AuditLog.event_type.ilike(f"%{search_request.query}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        results = query.order_by(AuditLog.timestamp.desc()).offset(search_request.offset).limit(search_request.limit).all()
        
        # Format results
        events = []
        for log in results:
            event_data = {
                'id': log.id,
                'event_type': log.event_type,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'user_id': log.user_id,
                'action': log.action,
                'description': log.description,
                'source': log.source,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'risk_level': log.risk_level,
                'timestamp': log.timestamp
            }
            
            # Include details if requested
            if search_request.filters and search_request.filters.include_details and log.details:
                import json
                try:
                    event_data['details'] = json.loads(log.details)
                except json.JSONDecodeError:
                    event_data['details'] = None
            
            events.append(AuditEventResponse(**event_data))
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        return AuditSearchResponse(
            query=search_request.query,
            total_matches=total_count,
            results=events,
            search_fields=search_request.search_fields,
            search_time_ms=search_time_ms,
            filters_applied=search_request.filters.dict() if search_request.filters else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search audit trail: {str(e)}"
        )

@router.get("/statistics", response_model=AuditStatistics)
async def get_audit_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive audit trail statistics"""
    
    # Only admin users can access full statistics
    if current_user.role not in ["admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view audit statistics"
        )
    
    try:
        from models.audit import AuditLog
        from sqlalchemy import func
        from collections import Counter
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all logs in the period
        logs = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
        ).all()
        
        total_events = len(logs)
        
        # Count by event type
        events_by_type = Counter(log.event_type for log in logs)
        
        # Count by entity type
        events_by_entity = Counter(log.entity_type for log in logs)
        
        # Count by risk level
        events_by_risk_level = Counter(log.risk_level for log in logs)
        
        # Count by source
        events_by_source = Counter(log.source for log in logs)
        
        # Count unique users
        unique_users = len(set(log.user_id for log in logs if log.user_id))
        
        # Top users by activity
        user_activity = Counter(log.user_id for log in logs if log.user_id)
        top_users = [{"user_id": user_id, "event_count": count} for user_id, count in user_activity.most_common(10)]
        
        # Daily event counts
        daily_counts = Counter(log.timestamp.date().isoformat() for log in logs)
        
        # Hourly distribution
        hourly_distribution = Counter(log.timestamp.hour for log in logs)
        
        return AuditStatistics(
            period_days=days,
            total_events=total_events,
            events_by_type=dict(events_by_type),
            events_by_entity=dict(events_by_entity),
            events_by_risk_level=dict(events_by_risk_level),
            events_by_source=dict(events_by_source),
            unique_users=unique_users,
            top_users=top_users,
            daily_event_counts=dict(daily_counts),
            hourly_distribution=dict(hourly_distribution)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit statistics: {str(e)}"
        )

@router.get("/system-health", response_model=SystemHealthMetrics)
async def get_system_health_metrics(
    days: int = Query(7, ge=1, le=90, description="Number of days for analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get system health metrics derived from audit logs"""
    
    # Only admin users can access system health metrics
    if current_user.role not in ["admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view system health metrics"
        )
    
    try:
        from models.audit import AuditLog
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all logs in the period
        logs = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
        ).all()
        
        total_events = len(logs)
        
        # Calculate metrics
        error_events = len([log for log in logs if 'error' in log.event_type.lower() or 'fail' in log.event_type.lower()])
        security_incidents = len([log for log in logs if log.event_type in ['security_breach', 'unauthorized_access', 'suspicious_activity']])
        failed_logins = len([log for log in logs if log.event_type == 'failed_login_attempt'])
        successful_operations = len([log for log in logs if 'success' in log.event_type.lower() or log.event_type in ['create', 'update', 'read', 'delete']])
        performance_issues = len([log for log in logs if 'timeout' in log.description.lower() or 'slow' in log.description.lower()])
        data_integrity_violations = len([log for log in logs if 'integrity' in log.description.lower() or 'corruption' in log.description.lower()])
        compliance_violations = len([log for log in logs if 'compliance' in log.description.lower() or 'violation' in log.description.lower()])
        
        # Calculate rates
        error_rate = (error_events / max(1, total_events)) * 100
        system_uptime_percentage = max(0, 100 - error_rate)  # Simplified calculation
        
        # Generate recommendations
        recommendations = []
        if error_rate > 5:
            recommendations.append(f"High error rate detected ({error_rate:.1f}%) - investigate system stability")
        if security_incidents > 0:
            recommendations.append(f"{security_incidents} security incidents detected - review security measures")
        if failed_logins > 10:
            recommendations.append(f"High number of failed login attempts ({failed_logins}) - consider implementing rate limiting")
        if performance_issues > 0:
            recommendations.append(f"{performance_issues} performance issues detected - review system resources")
        if data_integrity_violations > 0:
            recommendations.append(f"{data_integrity_violations} data integrity violations - perform data validation")
        
        if not recommendations:
            recommendations.append("System appears to be operating normally")
        
        return SystemHealthMetrics(
            period_days=days,
            system_uptime_percentage=round(system_uptime_percentage, 2),
            error_rate=round(error_rate, 2),
            security_incident_count=security_incidents,
            failed_login_attempts=failed_logins,
            successful_operations=successful_operations,
            performance_issues=performance_issues,
            data_integrity_violations=data_integrity_violations,
            compliance_violations=compliance_violations,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health metrics: {str(e)}"
        )