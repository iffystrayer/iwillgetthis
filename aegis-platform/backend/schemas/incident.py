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
    reputation_impact: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
    
    # Detection and source
    detection_method: Optional[str] = Field(None, max_length=100)
    detection_source: Optional[str] = Field(None, max_length=200)
    
    # Classification and handling
    confidentiality_level: str = Field("internal", regex="^(public|internal|confidential|restricted)$")
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
    reputation_impact: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
    
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
    confidentiality_level: Optional[str] = Field(None, regex="^(public|internal|confidential|restricted)$")
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
    experience_level: str = Field("intermediate", regex="^(junior|intermediate|senior|expert)$")
    
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
    experience_level: Optional[str] = Field(None, regex="^(junior|intermediate|senior|expert)$")
    
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
    priority: str = Field("medium", regex="^(low|medium|high|critical)$")
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
    
    priority: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
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
    analysis_status: str = Field("pending", regex="^(pending|in_progress|completed)$")
    analysis_results: Optional[str] = None
    analysis_tools_used: Optional[List[str]] = []
    
    # Legal and compliance
    legal_hold: bool = False
    retention_period_days: int = Field(2555, gt=0)
    confidentiality_level: str = Field("internal", regex="^(public|internal|confidential|restricted)$")
    
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
    analysis_status: Optional[str] = Field(None, regex="^(pending|in_progress|completed)$")
    analysis_results: Optional[str] = None
    analysis_tools_used: Optional[List[str]] = None
    
    legal_hold: Optional[bool] = None
    retention_period_days: Optional[int] = Field(None, gt=0)
    confidentiality_level: Optional[str] = Field(None, regex="^(public|internal|confidential|restricted)$")
    
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
    urgency: str = Field("normal", regex="^(low|normal|high|urgent)$")
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
    
    urgency: Optional[str] = Field(None, regex="^(low|normal|high|urgent)$")
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
    priority: str = Field("medium", regex="^(low|medium|high|critical)$")
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
    
    priority: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, gt=0)
    actual_hours: Optional[float] = Field(None, gt=0)
    
    status: Optional[str] = Field(None, regex="^(assigned|in_progress|completed|cancelled|blocked)$")
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
    confidence_level: str = Field("medium", regex="^(low|medium|high)$")
    verified: bool = False
    
    # Categorization
    phase: Optional[ResponsePhaseEnum] = None
    actor: Optional[str] = Field(None, max_length=200)
    target: Optional[str] = Field(None, max_length=200)
    technique: Optional[str] = Field(None, max_length=200)
    
    # Impact and severity
    impact_level: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
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
    confidence_level: Optional[str] = Field(None, regex="^(low|medium|high)$")
    verified: Optional[bool] = None
    verified_by: Optional[int] = None
    
    phase: Optional[ResponsePhaseEnum] = None
    actor: Optional[str] = None
    target: Optional[str] = None
    technique: Optional[str] = None
    
    impact_level: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
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
    response_effectiveness: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
    communication_effectiveness: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
    coordination_effectiveness: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
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
    confidentiality_level: str = Field("internal", regex="^(public|internal|confidential|restricted)$")


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
    
    response_effectiveness: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
    communication_effectiveness: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
    coordination_effectiveness: Optional[str] = Field(None, regex="^(excellent|good|fair|poor)$")
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
    confidentiality_level: Optional[str] = Field(None, regex="^(public|internal|confidential|restricted)$")


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