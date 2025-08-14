"""Pydantic schemas for audit trail API"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    """Risk level enumeration for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventSource(str, Enum):
    """Source of audit events"""
    WEB_UI = "web_ui"
    API = "api"
    SYSTEM = "system"
    INTEGRATION = "integration"
    SCHEDULED_TASK = "scheduled_task"

class AuditEventCreate(BaseModel):
    """Schema for creating audit events"""
    event_type: str = Field(..., min_length=1, max_length=100)
    entity_type: str = Field(..., min_length=1, max_length=100)
    entity_id: Optional[int] = None
    action: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="", max_length=1000)
    details: Optional[Dict[str, Any]] = None
    source: EventSource = EventSource.SYSTEM
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v is not None:
            import ipaddress
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError('Invalid IP address format')
        return v

class AuditEventBulkCreate(BaseModel):
    """Schema for bulk creating audit events"""
    events: List[AuditEventCreate] = Field(..., min_items=1, max_items=100)

class AuditEventResponse(BaseModel):
    """Schema for audit event response"""
    id: int
    event_type: str
    entity_type: str
    entity_id: Optional[int]
    user_id: Optional[int]
    action: str
    description: str
    source: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    risk_level: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class AuditTrailFilter(BaseModel):
    """Schema for audit trail filtering"""
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    user_id: Optional[int] = None
    event_type: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[EventSource] = None
    include_details: bool = False

class AuditTrailResponse(BaseModel):
    """Schema for audit trail response"""
    total_count: int
    results: List[AuditEventResponse]
    limit: int
    offset: int
    has_more: bool
    filters_applied: Optional[Dict[str, Any]] = None

class UserActivitySummary(BaseModel):
    """Schema for user activity summary"""
    user_id: int
    period_days: int
    total_activities: int
    activity_by_type: Dict[str, int]
    activity_by_entity: Dict[str, int]
    high_risk_events: List[Dict[str, Any]]
    high_risk_event_count: int
    daily_activity: Dict[str, int]
    most_active_day: Optional[str]
    average_daily_activity: float

class SecurityEventSummary(BaseModel):
    """Schema for security event summary"""
    period_days: int
    total_security_events: int
    events_by_type: Dict[str, int]
    events_by_user: Dict[int, int]
    suspicious_ip_addresses: Dict[str, int]
    recent_events: List[Dict[str, Any]]
    summary: Dict[str, int]

class ComplianceReportRequest(BaseModel):
    """Schema for compliance report request"""
    start_date: datetime
    end_date: datetime
    entity_types: Optional[List[str]] = None
    include_user_details: bool = True
    include_data_integrity: bool = True
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('start_date', 'end_date')
    def validate_date_not_future(cls, v):
        if v > datetime.utcnow():
            raise ValueError('Date cannot be in the future')
        return v

class ComplianceReport(BaseModel):
    """Schema for compliance audit report"""
    report_period: Dict[str, Any]
    summary: Dict[str, Any]
    user_activity: Dict[int, Dict[str, int]]
    data_integrity: Dict[str, int]
    compliance_metrics: Dict[str, Any]

class AnomalyDetectionRequest(BaseModel):
    """Schema for anomaly detection request"""
    user_id: int
    analysis_days: int = Field(default=7, ge=1, le=90)

class AnomalyDetectionResponse(BaseModel):
    """Schema for anomaly detection response"""
    user_id: int
    analysis_period: Dict[str, Any]
    activity_summary: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    risk_score: int
    risk_level: str
    requires_investigation: bool

class AuditExportRequest(BaseModel):
    """Schema for audit export request"""
    start_date: datetime
    end_date: datetime
    format: str = Field(default="json", regex="^(json|csv)$")
    entity_types: Optional[List[str]] = None
    include_sensitive_data: bool = False
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class AuditExportResponse(BaseModel):
    """Schema for audit export response"""
    metadata: Dict[str, Any]
    data: List[Dict[str, Any]]

class AuditSearchRequest(BaseModel):
    """Schema for audit search request"""
    query: str = Field(..., min_length=2, max_length=200)
    search_fields: Optional[List[str]] = Field(default=["action", "description", "event_type"])
    filters: Optional[AuditTrailFilter] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

class AuditSearchResponse(BaseModel):
    """Schema for audit search response"""
    query: str
    total_matches: int
    results: List[AuditEventResponse]
    search_fields: List[str]
    search_time_ms: int
    filters_applied: Optional[Dict[str, Any]] = None

class AuditStatistics(BaseModel):
    """Schema for audit statistics"""
    period_days: int
    total_events: int
    events_by_type: Dict[str, int]
    events_by_entity: Dict[str, int]
    events_by_risk_level: Dict[str, int]
    events_by_source: Dict[str, int]
    unique_users: int
    top_users: List[Dict[str, Any]]
    daily_event_counts: Dict[str, int]
    hourly_distribution: Dict[int, int]

class SystemHealthMetrics(BaseModel):
    """Schema for system health metrics derived from audit logs"""
    period_days: int
    system_uptime_percentage: float
    error_rate: float
    security_incident_count: int
    failed_login_attempts: int
    successful_operations: int
    performance_issues: int
    data_integrity_violations: int
    compliance_violations: int
    recommendations: List[str]