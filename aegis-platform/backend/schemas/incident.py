"""
Pydantic schemas for Incident Response and Crisis Management system
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class IncidentSeverityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class IncidentStatusEnum(str, Enum):
    REPORTED = "reported"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    CONTAINING = "containing"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class IncidentCategoryEnum(str, Enum):
    SECURITY_BREACH = "security_breach"
    DATA_BREACH = "data_breach"
    SYSTEM_OUTAGE = "system_outage"
    DENIAL_OF_SERVICE = "denial_of_service"
    MALWARE = "malware"
    PHISHING = "phishing"
    INSIDER_THREAT = "insider_threat"
    COMPLIANCE_VIOLATION = "compliance_violation"
    OPERATIONAL_ISSUE = "operational_issue"
    THIRD_PARTY_INCIDENT = "third_party_incident"
    NATURAL_DISASTER = "natural_disaster"
    OTHER = "other"


class EscalationLevelEnum(str, Enum):
    L1_BASIC = "l1_basic"
    L2_STANDARD = "l2_standard"
    L3_ADVANCED = "l3_advanced"
    L4_EXPERT = "l4_expert"
    EXECUTIVE = "executive"
    EXTERNAL = "external"


class ResponsePhaseEnum(str, Enum):
    PREPARATION = "preparation"
    IDENTIFICATION = "identification"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    LESSONS_LEARNED = "lessons_learned"


class CommunicationChannelEnum(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    PAGER = "pager"
    IN_PERSON = "in_person"
    VIDEO_CONFERENCE = "video_conference"


class ArtifactTypeEnum(str, Enum):
    LOG_FILE = "log_file"
    SCREENSHOT = "screenshot"
    NETWORK_CAPTURE = "network_capture"
    MEMORY_DUMP = "memory_dump"
    DISK_IMAGE = "disk_image"
    EMAIL = "email"
    DOCUMENT = "document"
    FORENSIC_REPORT = "forensic_report"
    TIMELINE = "timeline"
    IOC = "ioc"


# Base Schemas
class UserSummary(BaseModel):
    """Lightweight user summary for incident display"""
    id: int
    email: str
    full_name: Optional[str] = None


# Incident Schemas
class IncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: IncidentCategoryEnum
    severity: IncidentSeverityEnum
    
    # Timeline
    detected_at: Optional[datetime] = None
    occurred_at: Optional[datetime] = None
    
    # Impact assessment
    business_impact: Optional[str] = None
    affected_systems: Optional[List[str]] = []
    affected_users_count: int = Field(0, ge=0)
    financial_impact: Optional[float] = Field(None, ge=0)
    reputation_impact: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    
    # Detection and source
    detection_method: Optional[str] = Field(None, max_length=100)
    detection_source: Optional[str] = Field(None, max_length=200)
    
    # Classification and handling
    confidentiality_level: str = Field("internal", pattern="^(public|internal|confidential|restricted)$")
    handling_instructions: Optional[str] = None
    legal_hold_required: bool = False
    
    # External reporting
    requires_regulatory_reporting: bool = False
    regulatory_bodies_notified: Optional[List[str]] = []
    regulatory_notification_deadline: Optional[datetime] = None
    
    # Metadata
    tags: Optional[List[str]] = []
    custom_fields: Optional[Dict[str, Any]] = {}


class IncidentCreate(IncidentBase):
    reported_by: int


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[IncidentCategoryEnum] = None
    severity: Optional[IncidentSeverityEnum] = None
    status: Optional[IncidentStatusEnum] = None
    
    # Timeline updates
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Impact updates
    business_impact: Optional[str] = None
    affected_systems: Optional[List[str]] = None
    affected_users_count: Optional[int] = Field(None, ge=0)
    financial_impact: Optional[float] = Field(None, ge=0)
    reputation_impact: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    
    # Assignment updates
    primary_responder_id: Optional[int] = None
    incident_commander_id: Optional[int] = None
    assigned_team_id: Optional[int] = None
    
    # Escalation updates
    escalation_level: Optional[EscalationLevelEnum] = None
    escalation_reason: Optional[str] = None
    
    # External reporting updates
    requires_regulatory_reporting: Optional[bool] = None
    regulatory_bodies_notified: Optional[List[str]] = None
    regulatory_notification_deadline: Optional[datetime] = None
    
    # Handling updates
    confidentiality_level: Optional[str] = Field(None, pattern="^(public|internal|confidential|restricted)$")
    handling_instructions: Optional[str] = None
    legal_hold_required: Optional[bool] = None
    
    # Metadata updates
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class IncidentResponse(IncidentBase):
    id: int
    incident_id: str
    status: IncidentStatusEnum = IncidentStatusEnum.REPORTED
    
    # Timeline
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Assignment
    primary_responder_id: Optional[int] = None
    incident_commander_id: Optional[int] = None
    assigned_team_id: Optional[int] = None
    
    # Escalation
    escalation_level: EscalationLevelEnum = EscalationLevelEnum.L1_BASIC
    escalated_at: Optional[datetime] = None
    escalated_by: Optional[int] = None
    escalation_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    reported_by_user: Optional[UserSummary] = None
    primary_responder: Optional[UserSummary] = None
    incident_commander: Optional[UserSummary] = None
    escalated_by_user: Optional[UserSummary] = None
    assigned_team: Optional[Dict[str, Any]] = None
    
    # Aggregated data
    activity_count: Optional[int] = 0
    artifact_count: Optional[int] = 0
    communication_count: Optional[int] = 0
    task_count: Optional[int] = 0
    timeline_entry_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Response Team Schemas
class IncidentResponseTeamBase(BaseModel):
    team_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    
    # Team composition
    team_lead_id: Optional[int] = None
    escalation_contact_id: Optional[int] = None
    
    # Availability and scheduling
    on_call_schedule: Optional[Dict[str, Any]] = {}
    time_zone: str = Field("UTC", max_length=50)
    availability_hours: Optional[Dict[str, Any]] = {}
    
    # Team capabilities
    specializations: Optional[List[str]] = []
    max_concurrent_incidents: int = Field(5, gt=0)
    escalation_criteria: Optional[Dict[str, Any]] = {}
    
    # Contact information
    primary_contact_method: CommunicationChannelEnum = CommunicationChannelEnum.EMAIL
    contact_details: Optional[Dict[str, Any]] = {}
    
    # Status
    active: bool = True


class IncidentResponseTeamCreate(IncidentResponseTeamBase):
    pass


class IncidentResponseTeamUpdate(BaseModel):
    team_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    team_lead_id: Optional[int] = None
    escalation_contact_id: Optional[int] = None
    
    on_call_schedule: Optional[Dict[str, Any]] = None
    time_zone: Optional[str] = None
    availability_hours: Optional[Dict[str, Any]] = None
    
    specializations: Optional[List[str]] = None
    max_concurrent_incidents: Optional[int] = Field(None, gt=0)
    escalation_criteria: Optional[Dict[str, Any]] = None
    
    primary_contact_method: Optional[CommunicationChannelEnum] = None
    contact_details: Optional[Dict[str, Any]] = None
    
    active: Optional[bool] = None


class IncidentResponseTeamResponse(IncidentResponseTeamBase):
    id: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    team_lead: Optional[UserSummary] = None
    escalation_contact: Optional[UserSummary] = None
    member_count: Optional[int] = 0
    
    # Current status
    current_incidents: Optional[int] = 0
    available_capacity: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Team Member Schemas
class IncidentTeamMemberBase(BaseModel):
    team_id: int
    user_id: int
    
    # Role and permissions
    role: str = Field(..., min_length=1, max_length=100)
    permissions: Optional[Dict[str, Any]] = {}
    
    # Availability
    on_call_priority: int = Field(1, gt=0)
    available: bool = True
    availability_schedule: Optional[Dict[str, Any]] = {}
    
    # Skills and certifications
    skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    experience_level: str = Field("intermediate", pattern="^(junior|intermediate|senior|expert)$")
    
    # Contact preferences
    preferred_contact_method: Optional[CommunicationChannelEnum] = None
    contact_details: Optional[Dict[str, Any]] = {}


class IncidentTeamMemberCreate(IncidentTeamMemberBase):
    pass


class IncidentTeamMemberUpdate(BaseModel):
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    permissions: Optional[Dict[str, Any]] = None
    
    on_call_priority: Optional[int] = Field(None, gt=0)
    available: Optional[bool] = None
    availability_schedule: Optional[Dict[str, Any]] = None
    
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    experience_level: Optional[str] = Field(None, pattern="^(junior|intermediate|senior|expert)$")
    
    preferred_contact_method: Optional[CommunicationChannelEnum] = None
    contact_details: Optional[Dict[str, Any]] = None


class IncidentTeamMemberResponse(IncidentTeamMemberBase):
    id: int
    
    # Timestamps
    joined_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    team: Optional[Dict[str, Any]] = None
    user: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Activity Schemas
class IncidentActivityBase(BaseModel):
    activity_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    
    # Execution details
    duration_minutes: Optional[int] = Field(None, gt=0)
    response_phase: Optional[ResponsePhaseEnum] = None
    
    # Results and outcomes
    outcome: Optional[str] = None
    success: Optional[bool] = None
    next_actions: Optional[str] = None
    
    # Associated data
    artifacts_created: Optional[List[str]] = []
    systems_affected: Optional[List[str]] = []
    tools_used: Optional[List[str]] = []
    
    # Metadata
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    tags: Optional[List[str]] = []


class IncidentActivityCreate(IncidentActivityBase):
    incident_id: int
    performed_by: int


class IncidentActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    
    duration_minutes: Optional[int] = Field(None, gt=0)
    outcome: Optional[str] = None
    success: Optional[bool] = None
    next_actions: Optional[str] = None
    
    artifacts_created: Optional[List[str]] = None
    systems_affected: Optional[List[str]] = None
    tools_used: Optional[List[str]] = None
    
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    tags: Optional[List[str]] = None


class IncidentActivityResponse(IncidentActivityBase):
    id: int
    incident_id: int
    
    # Execution details
    performed_by: int
    performed_at: datetime
    
    # Timestamps
    created_at: datetime
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    performer: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Artifact Schemas
class IncidentArtifactBase(BaseModel):
    artifact_name: str = Field(..., min_length=1, max_length=300)
    artifact_type: ArtifactTypeEnum
    description: Optional[str] = None
    
    # File information
    file_path: Optional[str] = Field(None, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, gt=0)
    file_hash_md5: Optional[str] = Field(None, min_length=32, max_length=32)
    file_hash_sha256: Optional[str] = Field(None, min_length=64, max_length=64)
    
    # Collection details
    collection_method: Optional[str] = Field(None, max_length=200)
    source_system: Optional[str] = Field(None, max_length=200)
    
    # Chain of custody
    custody_log: Optional[List[Dict[str, Any]]] = []
    integrity_verified: bool = False
    verification_method: Optional[str] = Field(None, max_length=100)
    
    # Analysis and relevance
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    analysis_status: str = Field("pending", pattern="^(pending|in_progress|completed)$")
    analysis_results: Optional[str] = None
    analysis_tools_used: Optional[List[str]] = []
    
    # Legal and compliance
    legal_hold: bool = False
    retention_period_days: int = Field(2555, gt=0)
    confidentiality_level: str = Field("internal", pattern="^(public|internal|confidential|restricted)$")
    
    # Metadata
    tags: Optional[List[str]] = []
    ioc_indicators: Optional[List[str]] = []


class IncidentArtifactCreate(IncidentArtifactBase):
    incident_id: int
    collected_by: int


class IncidentArtifactUpdate(BaseModel):
    artifact_name: Optional[str] = Field(None, min_length=1, max_length=300)
    artifact_type: Optional[ArtifactTypeEnum] = None
    description: Optional[str] = None
    
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = Field(None, gt=0)
    file_hash_md5: Optional[str] = Field(None, min_length=32, max_length=32)
    file_hash_sha256: Optional[str] = Field(None, min_length=64, max_length=64)
    
    collection_method: Optional[str] = None
    source_system: Optional[str] = None
    
    custody_log: Optional[List[Dict[str, Any]]] = None
    integrity_verified: Optional[bool] = None
    verification_method: Optional[str] = None
    
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    analysis_status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    analysis_results: Optional[str] = None
    analysis_tools_used: Optional[List[str]] = None
    
    legal_hold: Optional[bool] = None
    retention_period_days: Optional[int] = Field(None, gt=0)
    confidentiality_level: Optional[str] = Field(None, pattern="^(public|internal|confidential|restricted)$")
    
    tags: Optional[List[str]] = None
    ioc_indicators: Optional[List[str]] = None


class IncidentArtifactResponse(IncidentArtifactBase):
    id: int
    incident_id: int
    
    # Collection details
    collected_by: int
    collected_at: datetime
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    collector: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Communication Schemas
class IncidentCommunicationBase(BaseModel):
    communication_type: str = Field(..., min_length=1, max_length=100)
    channel: CommunicationChannelEnum
    subject: Optional[str] = Field(None, max_length=500)
    message: str = Field(..., min_length=1)
    
    # Participants
    recipients: Optional[List[int]] = []
    cc_recipients: Optional[List[int]] = []
    bcc_recipients: Optional[List[int]] = []
    
    # Timing and urgency
    urgency: str = Field("normal", pattern="^(low|normal|high|urgent)$")
    read_receipt_required: bool = False
    
    # External communication
    external_recipients: Optional[List[str]] = []
    regulatory_notification: bool = False
    public_communication: bool = False
    
    # Templates and approvals
    template_used: Optional[str] = Field(None, max_length=200)
    approval_required: bool = False
    
    # Metadata
    communication_id: Optional[str] = Field(None, max_length=100)
    thread_id: Optional[str] = Field(None, max_length=100)
    attachments: Optional[List[str]] = []


class IncidentCommunicationCreate(IncidentCommunicationBase):
    incident_id: int
    sender_id: int


class IncidentCommunicationUpdate(BaseModel):
    subject: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = Field(None, min_length=1)
    
    recipients: Optional[List[int]] = None
    cc_recipients: Optional[List[int]] = None
    bcc_recipients: Optional[List[int]] = None
    
    urgency: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    read_receipt_required: Optional[bool] = None
    
    external_recipients: Optional[List[str]] = None
    regulatory_notification: Optional[bool] = None
    public_communication: Optional[bool] = None
    
    approval_required: Optional[bool] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    communication_id: Optional[str] = None
    thread_id: Optional[str] = None
    attachments: Optional[List[str]] = None


class IncidentCommunicationResponse(IncidentCommunicationBase):
    id: int
    incident_id: int
    
    # Sender and timing
    sender_id: int
    sent_at: datetime
    
    # Approval tracking
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    # Response tracking
    responses_received: Optional[List[Dict[str, Any]]] = []
    acknowledgments: Optional[List[Dict[str, Any]]] = []
    
    # Timestamps
    created_at: datetime
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    sender: Optional[UserSummary] = None
    approver: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Task Schemas
class IncidentTaskBase(BaseModel):
    task_name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    task_type: Optional[str] = Field(None, max_length=100)
    
    # Priority and timing
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, gt=0)
    
    # Dependencies and relationships
    depends_on_tasks: Optional[List[int]] = []
    parent_task_id: Optional[int] = None
    
    # Results and outcomes
    deliverables: Optional[List[str]] = []
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None


class IncidentTaskCreate(IncidentTaskBase):
    incident_id: int
    assigned_to: int
    assigned_by: int


class IncidentTaskUpdate(BaseModel):
    task_name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    task_type: Optional[str] = None
    
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, gt=0)
    actual_hours: Optional[float] = Field(None, gt=0)
    
    status: Optional[str] = Field(None, pattern="^(assigned|in_progress|completed|cancelled|blocked)$")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    completion_notes: Optional[str] = None
    
    depends_on_tasks: Optional[List[int]] = None
    parent_task_id: Optional[int] = None
    
    outcome: Optional[str] = None
    deliverables: Optional[List[str]] = None
    follow_up_required: Optional[bool] = None
    follow_up_notes: Optional[str] = None
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class IncidentTaskResponse(IncidentTaskBase):
    id: int
    incident_id: int
    
    # Assignment and ownership
    assigned_to: int
    assigned_by: int
    assigned_at: datetime
    
    # Status and progress
    status: str = "assigned"
    progress_percentage: int = 0
    completion_notes: Optional[str] = None
    actual_hours: Optional[float] = None
    
    # Dependencies
    blocking_tasks: Optional[List[int]] = []
    
    # Results
    outcome: Optional[str] = None
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    assignee: Optional[UserSummary] = None
    assigner: Optional[UserSummary] = None
    parent_task: Optional[Dict[str, Any]] = None
    subtask_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Timeline Entry Schemas
class IncidentTimelineEntryBase(BaseModel):
    timestamp: datetime
    event_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    
    # Source and verification
    source: Optional[str] = Field(None, max_length=200)
    confidence_level: str = Field("medium", pattern="^(low|medium|high)$")
    verified: bool = False
    
    # Categorization
    phase: Optional[ResponsePhaseEnum] = None
    actor: Optional[str] = Field(None, max_length=200)
    target: Optional[str] = Field(None, max_length=200)
    technique: Optional[str] = Field(None, max_length=200)
    
    # Impact and severity
    impact_level: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    business_impact: Optional[str] = None
    technical_impact: Optional[str] = None
    
    # Evidence and artifacts
    supporting_artifacts: Optional[List[int]] = []
    indicators: Optional[List[str]] = []
    
    # Metadata
    tags: Optional[List[str]] = []
    coordinates: Optional[Dict[str, Any]] = {}


class IncidentTimelineEntryCreate(IncidentTimelineEntryBase):
    incident_id: int


class IncidentTimelineEntryUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    event_type: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    
    source: Optional[str] = None
    confidence_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    verified: Optional[bool] = None
    verified_by: Optional[int] = None
    
    phase: Optional[ResponsePhaseEnum] = None
    actor: Optional[str] = None
    target: Optional[str] = None
    technique: Optional[str] = None
    
    impact_level: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    business_impact: Optional[str] = None
    technical_impact: Optional[str] = None
    
    supporting_artifacts: Optional[List[int]] = None
    indicators: Optional[List[str]] = None
    
    tags: Optional[List[str]] = None
    coordinates: Optional[Dict[str, Any]] = None


class IncidentTimelineEntryResponse(IncidentTimelineEntryBase):
    id: int
    incident_id: int
    
    # Verification
    verified_by: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    verifier: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Post-Incident Review Schemas
class PostIncidentReviewBase(BaseModel):
    review_name: str = Field(..., min_length=1, max_length=300)
    review_date: datetime
    participants: Optional[List[int]] = []
    
    # Timeline analysis
    detection_time_minutes: Optional[int] = Field(None, gt=0)
    response_time_minutes: Optional[int] = Field(None, gt=0)
    containment_time_minutes: Optional[int] = Field(None, gt=0)
    resolution_time_minutes: Optional[int] = Field(None, gt=0)
    
    # Effectiveness assessment
    response_effectiveness: Optional[str] = Field(None, pattern="^(excellent|good|fair|poor)$")
    communication_effectiveness: Optional[str] = Field(None, pattern="^(excellent|good|fair|poor)$")
    coordination_effectiveness: Optional[str] = Field(None, pattern="^(excellent|good|fair|poor)$")
    tool_effectiveness: Optional[Dict[str, str]] = {}
    
    # Root cause analysis
    root_cause: Optional[str] = None
    contributing_factors: Optional[List[str]] = []
    attack_vectors: Optional[List[str]] = []
    vulnerabilities_exploited: Optional[List[str]] = []
    
    # Impact assessment
    total_impact_cost: Optional[float] = Field(None, ge=0)
    business_downtime_hours: Optional[float] = Field(None, ge=0)
    data_compromised: bool = False
    data_compromised_records: Optional[int] = Field(None, ge=0)
    regulatory_fines: Optional[float] = Field(None, ge=0)
    reputation_impact_assessment: Optional[str] = None
    
    # What went well
    successes: Optional[List[str]] = []
    effective_controls: Optional[List[str]] = []
    good_decisions: Optional[List[str]] = []
    
    # Areas for improvement
    gaps_identified: Optional[List[str]] = []
    improvement_opportunities: Optional[List[str]] = []
    ineffective_controls: Optional[List[str]] = []
    
    # Recommendations and action items
    recommendations: Optional[List[str]] = []
    action_items: Optional[List[Dict[str, Any]]] = []
    preventive_measures: Optional[List[str]] = []
    detection_improvements: Optional[List[str]] = []
    
    # Follow-up tracking
    follow_up_required: bool = True
    next_review_date: Optional[datetime] = None
    action_items_status: Optional[Dict[str, str]] = {}
    
    # Documentation
    executive_summary: Optional[str] = None
    detailed_report_path: Optional[str] = Field(None, max_length=500)
    supporting_documents: Optional[List[str]] = []
    
    # Approval and distribution
    distribution_list: Optional[List[str]] = []
    confidentiality_level: str = Field("internal", pattern="^(public|internal|confidential|restricted)$")


class PostIncidentReviewCreate(PostIncidentReviewBase):
    incident_id: int
    facilitator_id: int


class PostIncidentReviewUpdate(BaseModel):
    review_name: Optional[str] = Field(None, min_length=1, max_length=300)
    review_date: Optional[datetime] = None
    participants: Optional[List[int]] = None
    
    detection_time_minutes: Optional[int] = Field(None, gt=0)
    response_time_minutes: Optional[int] = Field(None, gt=0)
    containment_time_minutes: Optional[int] = Field(None, gt=0)
    resolution_time_minutes: Optional[int] = Field(None, gt=0)
    
    response_effectiveness: Optional[str] = Field(None, pattern="^(excellent|good|fair|poor)$")
    communication_effectiveness: Optional[str] = Field(None, pattern="^(excellent|good|fair|poor)$")
    coordination_effectiveness: Optional[str] = Field(None, pattern="^(excellent|good|fair|poor)$")
    tool_effectiveness: Optional[Dict[str, str]] = None
    
    root_cause: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    attack_vectors: Optional[List[str]] = None
    vulnerabilities_exploited: Optional[List[str]] = None
    
    total_impact_cost: Optional[float] = Field(None, ge=0)
    business_downtime_hours: Optional[float] = Field(None, ge=0)
    data_compromised: Optional[bool] = None
    data_compromised_records: Optional[int] = Field(None, ge=0)
    regulatory_fines: Optional[float] = Field(None, ge=0)
    reputation_impact_assessment: Optional[str] = None
    
    successes: Optional[List[str]] = None
    effective_controls: Optional[List[str]] = None
    good_decisions: Optional[List[str]] = None
    
    gaps_identified: Optional[List[str]] = None
    improvement_opportunities: Optional[List[str]] = None
    ineffective_controls: Optional[List[str]] = None
    
    recommendations: Optional[List[str]] = None
    action_items: Optional[List[Dict[str, Any]]] = None
    preventive_measures: Optional[List[str]] = None
    detection_improvements: Optional[List[str]] = None
    
    follow_up_required: Optional[bool] = None
    next_review_date: Optional[datetime] = None
    action_items_status: Optional[Dict[str, str]] = None
    
    executive_summary: Optional[str] = None
    detailed_report_path: Optional[str] = None
    supporting_documents: Optional[List[str]] = None
    
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    distribution_list: Optional[List[str]] = None
    confidentiality_level: Optional[str] = Field(None, pattern="^(public|internal|confidential|restricted)$")


class PostIncidentReviewResponse(PostIncidentReviewBase):
    id: int
    incident_id: int
    facilitator_id: int
    
    # Approval tracking
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    facilitator: Optional[UserSummary] = None
    approver: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Dashboard and Analytics Schemas
class IncidentDashboardData(BaseModel):
    """Incident response dashboard summary data"""
    total_incidents: int
    open_incidents: int
    incidents_this_month: int
    avg_resolution_time_hours: float
    
    incidents_by_severity: Dict[str, int]
    incidents_by_category: Dict[str, int]
    incidents_by_status: Dict[str, int]
    incidents_by_team: Dict[str, int]
    
    overdue_incidents: int
    escalated_incidents: int
    regulatory_incidents: int
    
    response_time_trend: Dict[str, Any]
    recent_incidents: List[Dict[str, Any]]
    critical_incidents: List[Dict[str, Any]]


class IncidentMetricsData(BaseModel):
    """Incident response metrics and KPIs"""
    measurement_period: Dict[str, datetime]
    
    # Response time metrics
    mean_time_to_detect_hours: float
    mean_time_to_respond_hours: float
    mean_time_to_contain_hours: float
    mean_time_to_resolve_hours: float
    
    # Volume metrics
    incident_volume_trend: Dict[str, int]
    severity_distribution: Dict[str, float]
    category_distribution: Dict[str, float]
    
    # Effectiveness metrics
    first_call_resolution_rate: float
    escalation_rate: float
    customer_satisfaction_score: Optional[float]
    regulatory_compliance_rate: float
    
    # Cost metrics
    average_incident_cost: float
    total_business_impact: float
    prevention_vs_response_cost_ratio: float


class IncidentFilter(BaseModel):
    """Filters for incident queries"""
    severity_levels: Optional[List[IncidentSeverityEnum]] = None
    categories: Optional[List[IncidentCategoryEnum]] = None
    statuses: Optional[List[IncidentStatusEnum]] = None
    assigned_teams: Optional[List[int]] = None
    assigned_responders: Optional[List[int]] = None
    escalation_levels: Optional[List[EscalationLevelEnum]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    text_search: Optional[str] = None
    regulatory_reporting_required: Optional[bool] = None
    min_affected_users: Optional[int] = Field(None, ge=0)
    max_affected_users: Optional[int] = Field(None, ge=0)
    min_financial_impact: Optional[float] = Field(None, ge=0)
    max_financial_impact: Optional[float] = Field(None, ge=0)


class BulkIncidentOperation(BaseModel):
    """Bulk operations on incidents"""
    operation: str  # update_status, assign_team, escalate, close, etc.
    incident_ids: List[int]
    operation_data: Dict[str, Any]
    reason: Optional[str] = None


class BulkIncidentOperationResponse(BaseModel):
    """Response for bulk incident operations"""
    success: bool
    operation: str
    processed_count: int
    success_count: int
    error_count: int
    errors: List[str] = []
    updated_incidents: List[int] = []


# Specialized Schemas
class IncidentClassificationRequest(BaseModel):
    """Request for incident classification"""
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    affected_systems: Optional[List[str]] = []
    affected_users_count: int = Field(0, ge=0)
    financial_impact: Optional[float] = Field(None, ge=0)
    detection_method: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = {}


class IncidentClassificationResponse(BaseModel):
    """Response from incident classification"""
    category: IncidentCategoryEnum
    severity: IncidentSeverityEnum
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    escalation_level: EscalationLevelEnum
    required_response_time_minutes: int
    required_team: Optional[str] = None
    regulatory_reporting_required: bool
    auto_actions: List[Dict[str, Any]] = []
    reasoning: str


class IncidentEscalationCheck(BaseModel):
    """Escalation check result"""
    incident_id: int
    should_escalate: bool
    current_escalation_level: EscalationLevelEnum
    recommended_escalation_level: EscalationLevelEnum
    escalation_reason: str
    time_elapsed_minutes: int
    escalation_criteria_met: List[str]


class IncidentPlaybookExecution(BaseModel):
    """Playbook execution request"""
    incident_id: int
    playbook_id: str
    execution_parameters: Optional[Dict[str, Any]] = {}
    auto_execute: bool = False


class IncidentPlaybookExecutionResponse(BaseModel):
    """Playbook execution response"""
    execution_id: str
    incident_id: int
    playbook_id: str
    status: str  # initiated, in_progress, completed, failed
    steps_completed: int
    total_steps: int
    next_action: Optional[str] = None
    estimated_completion_time: Optional[datetime] = None
    errors: List[str] = []


# Post-Incident Analysis Schemas

# Lessons Learned Schemas
class LessonLearnedBase(BaseModel):
    """Base schema for lessons learned"""
    lesson_title: str = Field(..., min_length=1, max_length=500)
    lesson_summary: str = Field(..., min_length=1)
    lesson_category: Optional[str] = Field(None, max_length=100)
    
    # Lesson details
    what_happened: Optional[str] = None
    why_it_happened: Optional[str] = None
    what_we_learned: Optional[str] = None
    
    # Recommendations and actions
    recommendations: Optional[List[str]] = []
    preventive_measures: Optional[List[str]] = []
    process_improvements: Optional[List[str]] = []
    
    # Impact and relevance
    severity_prevented: Optional[IncidentSeverityEnum] = None
    cost_savings_estimated: Optional[float] = Field(None, ge=0)
    applicability_scope: Optional[str] = Field(None, max_length=100)
    affected_systems: Optional[List[str]] = []
    
    # Implementation tracking
    implementation_status: str = Field("identified", pattern="^(identified|planned|in_progress|implemented|verified)$")
    implementation_date: Optional[datetime] = None
    implementation_cost: Optional[float] = Field(None, ge=0)
    implementation_effort_hours: Optional[float] = Field(None, ge=0)
    
    # Knowledge management
    keywords: Optional[List[str]] = []
    related_lessons: Optional[List[int]] = []
    knowledge_base_category: Optional[str] = Field(None, max_length=100)
    training_material_created: bool = False
    
    # Verification and effectiveness
    effectiveness_verified: bool = False
    verification_date: Optional[datetime] = None
    verification_method: Optional[str] = None
    recurrence_prevented: Optional[bool] = None
    
    # Approval and sharing
    shared_externally: bool = False
    sharing_restrictions: Optional[str] = None
    
    # Metadata
    confidence_level: str = Field("medium", pattern="^(high|medium|low)$")
    evidence_quality: str = Field("medium", pattern="^(high|medium|low)$")
    tags: Optional[List[str]] = []


class LessonLearnedCreate(LessonLearnedBase):
    """Create schema for lessons learned"""
    incident_id: Optional[int] = None
    post_incident_review_id: Optional[int] = None
    implementation_owner: Optional[int] = None


class LessonLearnedUpdate(BaseModel):
    """Update schema for lessons learned"""
    lesson_title: Optional[str] = Field(None, min_length=1, max_length=500)
    lesson_summary: Optional[str] = Field(None, min_length=1)
    lesson_category: Optional[str] = None
    
    what_happened: Optional[str] = None
    why_it_happened: Optional[str] = None
    what_we_learned: Optional[str] = None
    
    recommendations: Optional[List[str]] = None
    preventive_measures: Optional[List[str]] = None
    process_improvements: Optional[List[str]] = None
    
    severity_prevented: Optional[IncidentSeverityEnum] = None
    cost_savings_estimated: Optional[float] = Field(None, ge=0)
    applicability_scope: Optional[str] = None
    affected_systems: Optional[List[str]] = None
    
    implementation_status: Optional[str] = Field(None, pattern="^(identified|planned|in_progress|implemented|verified)$")
    implementation_date: Optional[datetime] = None
    implementation_owner: Optional[int] = None
    implementation_cost: Optional[float] = Field(None, ge=0)
    implementation_effort_hours: Optional[float] = Field(None, ge=0)
    
    keywords: Optional[List[str]] = None
    related_lessons: Optional[List[int]] = None
    knowledge_base_category: Optional[str] = None
    training_material_created: Optional[bool] = None
    
    effectiveness_verified: Optional[bool] = None
    verification_date: Optional[datetime] = None
    verification_method: Optional[str] = None
    recurrence_prevented: Optional[bool] = None
    
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    shared_externally: Optional[bool] = None
    sharing_restrictions: Optional[str] = None
    
    confidence_level: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    evidence_quality: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    tags: Optional[List[str]] = None


class LessonLearnedResponse(LessonLearnedBase):
    """Response schema for lessons learned"""
    id: int
    
    # Source relationships
    incident_id: Optional[int] = None
    post_incident_review_id: Optional[int] = None
    implementation_owner: Optional[int] = None
    
    # Approval tracking
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    # Timestamps
    identified_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    post_incident_review: Optional[Dict[str, Any]] = None
    implementation_owner_user: Optional[UserSummary] = None
    approver: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Action Item Schemas
class ActionItemBase(BaseModel):
    """Base schema for action items"""
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    action_type: Optional[str] = Field(None, max_length=100)
    
    # Assignment and ownership
    responsible_team: Optional[str] = Field(None, max_length=200)
    
    # Priority and timing
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    due_date: datetime
    estimated_effort_hours: Optional[float] = Field(None, ge=0)
    estimated_cost: Optional[float] = Field(None, ge=0)
    
    # Implementation details
    success_criteria: Optional[str] = None
    deliverables: Optional[List[str]] = []
    dependencies: Optional[List[str]] = []
    risks: Optional[str] = None
    
    # Follow-up
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    
    # Metadata
    tags: Optional[List[str]] = []
    related_action_items: Optional[List[int]] = []


class ActionItemCreate(ActionItemBase):
    """Create schema for action items"""
    assigned_to: int
    assigned_by: int
    post_incident_review_id: Optional[int] = None
    lesson_learned_id: Optional[int] = None
    incident_id: Optional[int] = None


class ActionItemUpdate(BaseModel):
    """Update schema for action items"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    action_type: Optional[str] = None
    
    responsible_team: Optional[str] = None
    
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    due_date: Optional[datetime] = None
    estimated_effort_hours: Optional[float] = Field(None, ge=0)
    estimated_cost: Optional[float] = Field(None, ge=0)
    
    status: Optional[str] = Field(None, pattern="^(open|in_progress|completed|cancelled|on_hold)$")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    status_notes: Optional[str] = None
    
    success_criteria: Optional[str] = None
    deliverables: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    risks: Optional[str] = None
    
    completion_notes: Optional[str] = None
    actual_effort_hours: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    lessons_from_implementation: Optional[str] = None
    
    verification_required: Optional[bool] = None
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    
    tags: Optional[List[str]] = None
    related_action_items: Optional[List[int]] = None
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ActionItemResponse(ActionItemBase):
    """Response schema for action items"""
    id: int
    
    # Source relationships
    post_incident_review_id: Optional[int] = None
    lesson_learned_id: Optional[int] = None
    incident_id: Optional[int] = None
    
    # Assignment
    assigned_to: int
    assigned_by: int
    
    # Status and progress
    status: str = "open"
    progress_percentage: int = 0
    status_notes: Optional[str] = None
    
    # Results and outcomes
    completion_notes: Optional[str] = None
    actual_effort_hours: Optional[float] = None
    actual_cost: Optional[float] = None
    effectiveness_rating: Optional[int] = None
    lessons_from_implementation: Optional[str] = None
    
    # Verification and closure
    verification_required: bool = True
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Relationships
    post_incident_review: Optional[Dict[str, Any]] = None
    lesson_learned: Optional[Dict[str, Any]] = None
    incident: Optional[Dict[str, Any]] = None
    assignee: Optional[UserSummary] = None
    assigner: Optional[UserSummary] = None
    verifier: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Knowledge Article Schemas
class KnowledgeArticleBase(BaseModel):
    """Base schema for knowledge articles"""
    title: str = Field(..., min_length=1, max_length=500)
    article_type: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    
    # Content
    summary: Optional[str] = None
    content: str = Field(..., min_length=1)
    content_format: str = Field("markdown", pattern="^(markdown|html|plain_text)$")
    
    # Source and derivation
    source_documents: Optional[List[str]] = []
    
    # Applicability and audience
    target_audience: Optional[List[str]] = []
    skill_level_required: str = Field("intermediate", pattern="^(beginner|intermediate|advanced|expert)$")
    applicable_scenarios: Optional[List[str]] = []
    
    # Knowledge management
    keywords: Optional[List[str]] = []
    related_articles: Optional[List[int]] = []
    prerequisites: Optional[List[str]] = []
    follow_up_reading: Optional[List[str]] = []
    
    # Quality and maintenance
    review_frequency_days: int = Field(365, gt=0)
    
    # Access control
    access_level: str = Field("internal", pattern="^(public|internal|restricted|confidential)$")
    allowed_roles: Optional[List[str]] = []
    allowed_teams: Optional[List[str]] = []
    
    # Versioning
    version: str = Field("1.0", max_length=20)
    change_log: Optional[List[Dict[str, Any]]] = []
    
    # Metadata
    tags: Optional[List[str]] = []
    attachments: Optional[List[str]] = []
    external_links: Optional[List[str]] = []


class KnowledgeArticleCreate(KnowledgeArticleBase):
    """Create schema for knowledge articles"""
    author_id: int
    derived_from_incident: Optional[int] = None
    derived_from_lesson: Optional[int] = None


class KnowledgeArticleUpdate(BaseModel):
    """Update schema for knowledge articles"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    article_type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    
    summary: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    content_format: Optional[str] = Field(None, pattern="^(markdown|html|plain_text)$")
    
    source_documents: Optional[List[str]] = None
    
    target_audience: Optional[List[str]] = None
    skill_level_required: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced|expert)$")
    applicable_scenarios: Optional[List[str]] = None
    
    keywords: Optional[List[str]] = None
    related_articles: Optional[List[int]] = None
    prerequisites: Optional[List[str]] = None
    follow_up_reading: Optional[List[str]] = None
    
    accuracy_verified: Optional[bool] = None
    verification_date: Optional[datetime] = None
    verified_by: Optional[int] = None
    last_reviewed: Optional[datetime] = None
    review_frequency_days: Optional[int] = Field(None, gt=0)
    
    usefulness_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    usage_feedback: Optional[List[Dict[str, Any]]] = None
    search_ranking: Optional[int] = Field(None, ge=1, le=100)
    
    published: Optional[bool] = None
    publication_date: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    access_level: Optional[str] = Field(None, pattern="^(public|internal|restricted|confidential)$")
    allowed_roles: Optional[List[str]] = None
    allowed_teams: Optional[List[str]] = None
    
    version: Optional[str] = None
    change_log: Optional[List[Dict[str, Any]]] = None
    
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    external_links: Optional[List[str]] = None


class KnowledgeArticleResponse(KnowledgeArticleBase):
    """Response schema for knowledge articles"""
    id: int
    
    # Source relationships
    derived_from_incident: Optional[int] = None
    derived_from_lesson: Optional[int] = None
    author_id: int
    
    # Quality and maintenance
    accuracy_verified: bool = False
    verification_date: Optional[datetime] = None
    verified_by: Optional[int] = None
    last_reviewed: Optional[datetime] = None
    
    # Usage and effectiveness
    view_count: int = 0
    usefulness_rating: Optional[float] = None
    usage_feedback: Optional[List[Dict[str, Any]]] = []
    search_ranking: int = 50
    
    # Publishing and access
    published: bool = False
    publication_date: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    # Versioning
    previous_version_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    incident: Optional[Dict[str, Any]] = None
    lesson_learned: Optional[Dict[str, Any]] = None
    author: Optional[UserSummary] = None
    approver: Optional[UserSummary] = None
    verifier: Optional[UserSummary] = None
    previous_version: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# Trend Analysis Schemas
class TrendAnalysisBase(BaseModel):
    """Base schema for trend analysis"""
    analysis_name: str = Field(..., min_length=1, max_length=300)
    analysis_type: Optional[str] = Field(None, max_length=100)
    time_period_start: datetime
    time_period_end: datetime
    
    # Analysis scope
    incident_categories: Optional[List[str]] = []
    severity_levels: Optional[List[str]] = []
    teams_included: Optional[List[str]] = []
    
    # Trend findings
    key_trends: Optional[List[str]] = []
    emerging_patterns: Optional[List[str]] = []
    trend_directions: Optional[Dict[str, str]] = {}
    
    # Statistical analysis
    incident_volume_trend: Optional[Dict[str, Any]] = {}
    severity_distribution_trend: Optional[Dict[str, Any]] = {}
    response_time_trends: Optional[Dict[str, Any]] = {}
    cost_trends: Optional[Dict[str, Any]] = {}
    
    # Predictive insights
    risk_predictions: Optional[List[str]] = []
    resource_needs_forecast: Optional[Dict[str, Any]] = {}
    seasonal_patterns: Optional[Dict[str, Any]] = {}
    
    # Recommendations
    strategic_recommendations: Optional[List[str]] = []
    tactical_recommendations: Optional[List[str]] = []
    investment_priorities: Optional[List[str]] = []
    
    # Data quality and methodology
    data_sources: Optional[List[str]] = []
    methodology: Optional[str] = None
    confidence_level: str = Field("medium", pattern="^(high|medium|low)$")
    limitations: Optional[str] = None
    
    # Results and impact
    findings_summary: Optional[str] = None
    business_impact: Optional[str] = None
    action_items_generated: Optional[List[Dict[str, Any]]] = []
    
    # Approval and distribution
    distribution_list: Optional[List[str]] = []
    
    # Metadata
    tags: Optional[List[str]] = []
    supporting_charts: Optional[List[str]] = []
    detailed_report_path: Optional[str] = Field(None, max_length=500)


class TrendAnalysisCreate(TrendAnalysisBase):
    """Create schema for trend analysis"""
    analyst_id: int


class TrendAnalysisUpdate(BaseModel):
    """Update schema for trend analysis"""
    analysis_name: Optional[str] = Field(None, min_length=1, max_length=300)
    analysis_type: Optional[str] = None
    time_period_start: Optional[datetime] = None
    time_period_end: Optional[datetime] = None
    
    incident_categories: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    teams_included: Optional[List[str]] = None
    
    key_trends: Optional[List[str]] = None
    emerging_patterns: Optional[List[str]] = None
    trend_directions: Optional[Dict[str, str]] = None
    
    incident_volume_trend: Optional[Dict[str, Any]] = None
    severity_distribution_trend: Optional[Dict[str, Any]] = None
    response_time_trends: Optional[Dict[str, Any]] = None
    cost_trends: Optional[Dict[str, Any]] = None
    
    risk_predictions: Optional[List[str]] = None
    resource_needs_forecast: Optional[Dict[str, Any]] = None
    seasonal_patterns: Optional[Dict[str, Any]] = None
    
    strategic_recommendations: Optional[List[str]] = None
    tactical_recommendations: Optional[List[str]] = None
    investment_priorities: Optional[List[str]] = None
    
    data_sources: Optional[List[str]] = None
    methodology: Optional[str] = None
    confidence_level: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    limitations: Optional[str] = None
    
    findings_summary: Optional[str] = None
    business_impact: Optional[str] = None
    action_items_generated: Optional[List[Dict[str, Any]]] = None
    
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    distribution_list: Optional[List[str]] = None
    
    tags: Optional[List[str]] = None
    supporting_charts: Optional[List[str]] = None
    detailed_report_path: Optional[str] = None


class TrendAnalysisResponse(TrendAnalysisBase):
    """Response schema for trend analysis"""
    id: int
    analyst_id: int
    
    # Approval tracking
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    # Timestamps
    analysis_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    analyst: Optional[UserSummary] = None
    approver: Optional[UserSummary] = None
    
    class Config:
        from_attributes = True


# Knowledge Base Dashboard Schemas
class LessonsLearnedDashboardData(BaseModel):
    """Dashboard data for lessons learned"""
    total_lessons: int
    lessons_this_quarter: int
    implemented_lessons: int
    verified_effectiveness: int
    
    lessons_by_category: Dict[str, int]
    lessons_by_implementation_status: Dict[str, int]
    cost_savings_total: float
    recurrence_prevention_rate: float
    
    recent_lessons: List[Dict[str, Any]]
    high_impact_lessons: List[Dict[str, Any]]
    implementation_backlog: List[Dict[str, Any]]


class KnowledgeBaseDashboardData(BaseModel):
    """Dashboard data for knowledge base"""
    total_articles: int
    published_articles: int
    articles_this_month: int
    pending_review_articles: int
    
    articles_by_category: Dict[str, int]
    articles_by_type: Dict[str, int]
    most_viewed_articles: List[Dict[str, Any]]
    highest_rated_articles: List[Dict[str, Any]]
    
    search_activity: Dict[str, Any]
    user_feedback_summary: Dict[str, Any]


class PostIncidentAnalyticsDashboard(BaseModel):
    """Comprehensive post-incident analytics dashboard"""
    lessons_learned_data: LessonsLearnedDashboardData
    knowledge_base_data: KnowledgeBaseDashboardData
    
    action_items_summary: Dict[str, Any]
    trend_analysis_summary: Dict[str, Any]
    improvement_metrics: Dict[str, Any]
    
    recent_reviews: List[Dict[str, Any]]
    pending_action_items: List[Dict[str, Any]]
    effectiveness_trends: Dict[str, Any]


class KnowledgeSearchRequest(BaseModel):
    """Knowledge base search request"""
    query: str = Field(..., min_length=1)
    categories: Optional[List[str]] = None
    article_types: Optional[List[str]] = None
    skill_levels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    access_level: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class KnowledgeSearchResponse(BaseModel):
    """Knowledge base search response"""
    total_results: int
    results: List[Dict[str, Any]]
    search_suggestions: List[str]
    related_searches: List[str]
    facets: Dict[str, List[Dict[str, Any]]]