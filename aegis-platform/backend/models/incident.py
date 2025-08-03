"""
Database models for Incident Response and Crisis Management
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum

from .base import Base


# Enums
class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class IncidentStatus(Enum):
    """Incident lifecycle status"""
    REPORTED = "reported"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    CONTAINING = "containing"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class IncidentCategory(Enum):
    """Incident categories"""
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


class EscalationLevel(Enum):
    """Incident escalation levels"""
    L1_BASIC = "l1_basic"
    L2_STANDARD = "l2_standard"
    L3_ADVANCED = "l3_advanced"
    L4_EXPERT = "l4_expert"
    EXECUTIVE = "executive"
    EXTERNAL = "external"


class ResponsePhase(Enum):
    """Incident response phases"""
    PREPARATION = "preparation"
    IDENTIFICATION = "identification"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    LESSONS_LEARNED = "lessons_learned"


class CommunicationChannel(Enum):
    """Communication channels for incident response"""
    EMAIL = "email"
    PHONE = "phone"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    PAGER = "pager"
    IN_PERSON = "in_person"
    VIDEO_CONFERENCE = "video_conference"


class ArtifactType(Enum):
    """Types of incident artifacts"""
    LOG_FILE = "log_file"
    SCREENSHOT = "screenshot"
    NETWORK_CAPTURE = "network_capture"
    MEMORY_DUMP = "memory_dump"
    DISK_IMAGE = "disk_image"
    EMAIL = "email"
    DOCUMENT = "document"
    FORENSIC_REPORT = "forensic_report"
    TIMELINE = "timeline"
    IOC = "ioc"  # Indicators of Compromise


# Main Models
class IncidentModel(Base):
    """Core incident model"""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic incident information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(SQLEnum(IncidentCategory), nullable=False)
    severity = Column(SQLEnum(IncidentSeverity), nullable=False)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.REPORTED)
    
    # Timeline
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    detected_at = Column(DateTime)
    occurred_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Impact assessment
    business_impact = Column(Text)
    affected_systems = Column(JSON)  # List of affected systems/services
    affected_users_count = Column(Integer, default=0)
    financial_impact = Column(Float)
    reputation_impact = Column(String(20))  # low, medium, high, critical
    
    # Response team assignment
    primary_responder_id = Column(Integer, ForeignKey("users.id"))
    incident_commander_id = Column(Integer, ForeignKey("users.id"))
    assigned_team_id = Column(Integer, ForeignKey("incident_response_teams.id"))
    
    # Escalation
    escalation_level = Column(SQLEnum(EscalationLevel), default=EscalationLevel.L1_BASIC)
    escalated_at = Column(DateTime)
    escalated_by = Column(Integer, ForeignKey("users.id"))
    escalation_reason = Column(Text)
    
    # External reporting
    requires_regulatory_reporting = Column(Boolean, default=False)
    regulatory_bodies_notified = Column(JSON)  # List of regulatory bodies
    regulatory_notification_deadline = Column(DateTime)
    
    # Classification and handling
    confidentiality_level = Column(String(20), default="internal")  # public, internal, confidential, restricted
    handling_instructions = Column(Text)
    legal_hold_required = Column(Boolean, default=False)
    
    # Source and detection
    reported_by = Column(Integer, ForeignKey("users.id"))
    detection_method = Column(String(100))  # manual, automated, third_party, etc.
    detection_source = Column(String(200))  # specific tool or person
    
    # Metadata
    tags = Column(JSON)  # Flexible tagging system
    custom_fields = Column(JSON)  # Organization-specific fields
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    primary_responder = relationship("User", foreign_keys=[primary_responder_id])
    incident_commander = relationship("User", foreign_keys=[incident_commander_id])
    reporter = relationship("User", foreign_keys=[reported_by])
    escalated_by_user = relationship("User", foreign_keys=[escalated_by])
    assigned_team = relationship("IncidentResponseTeam", back_populates="incidents")
    
    activities = relationship("IncidentActivity", back_populates="incident", cascade="all, delete-orphan")
    artifacts = relationship("IncidentArtifact", back_populates="incident", cascade="all, delete-orphan")
    communications = relationship("IncidentCommunication", back_populates="incident", cascade="all, delete-orphan")
    tasks = relationship("IncidentTask", back_populates="incident", cascade="all, delete-orphan")
    timeline_entries = relationship("IncidentTimelineEntry", back_populates="incident", cascade="all, delete-orphan")
    post_incident_review = relationship("PostIncidentReview", back_populates="incident", uselist=False)


class IncidentResponseTeam(Base):
    """Incident response team model"""
    __tablename__ = "incident_response_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Team composition
    team_lead_id = Column(Integer, ForeignKey("users.id"))
    escalation_contact_id = Column(Integer, ForeignKey("users.id"))
    
    # Availability and scheduling
    on_call_schedule = Column(JSON)  # Schedule configuration
    time_zone = Column(String(50), default="UTC")
    availability_hours = Column(JSON)  # Business hours, 24/7, etc.
    
    # Team capabilities
    specializations = Column(JSON)  # List of specializations
    max_concurrent_incidents = Column(Integer, default=5)
    escalation_criteria = Column(JSON)  # When to escalate
    
    # Contact information
    primary_contact_method = Column(SQLEnum(CommunicationChannel), default=CommunicationChannel.EMAIL)
    contact_details = Column(JSON)  # Email, phone, Slack channel, etc.
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team_lead = relationship("User", foreign_keys=[team_lead_id])
    escalation_contact = relationship("User", foreign_keys=[escalation_contact_id])
    members = relationship("IncidentTeamMember", back_populates="team", cascade="all, delete-orphan")
    incidents = relationship("IncidentModel", back_populates="assigned_team")


class IncidentTeamMember(Base):
    """Team member model with roles and availability"""
    __tablename__ = "incident_team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("incident_response_teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Role and permissions
    role = Column(String(100), nullable=False)  # analyst, lead, commander, specialist
    permissions = Column(JSON)  # Specific permissions within incident response
    
    # Availability
    on_call_priority = Column(Integer, default=1)  # 1 = primary, 2 = secondary, etc.
    available = Column(Boolean, default=True)
    availability_schedule = Column(JSON)  # Personal schedule overrides
    
    # Skills and certifications
    skills = Column(JSON)  # Technical and soft skills
    certifications = Column(JSON)  # Relevant certifications
    experience_level = Column(String(20), default="intermediate")  # junior, intermediate, senior, expert
    
    # Contact preferences
    preferred_contact_method = Column(SQLEnum(CommunicationChannel))
    contact_details = Column(JSON)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("IncidentResponseTeam", back_populates="members")
    user = relationship("User")


class IncidentActivity(Base):
    """Activity log for incident response actions"""
    __tablename__ = "incident_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Activity details
    activity_type = Column(String(100), nullable=False)  # investigation, containment, communication, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Execution details
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_minutes = Column(Integer)
    
    # Response phase
    response_phase = Column(SQLEnum(ResponsePhase))
    
    # Results and outcomes
    outcome = Column(Text)
    success = Column(Boolean)
    next_actions = Column(Text)
    
    # Associated data
    artifacts_created = Column(JSON)  # List of artifact IDs created
    systems_affected = Column(JSON)  # Systems touched during activity
    tools_used = Column(JSON)  # Tools and techniques used
    
    # Metadata
    priority = Column(String(20), default="medium")
    tags = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel", back_populates="activities")
    performer = relationship("User")


class IncidentArtifact(Base):
    """Digital artifacts and evidence collected during incident response"""
    __tablename__ = "incident_artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Artifact identification
    artifact_name = Column(String(300), nullable=False)
    artifact_type = Column(SQLEnum(ArtifactType), nullable=False)
    description = Column(Text)
    
    # File information
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    file_hash_md5 = Column(String(32))
    file_hash_sha256 = Column(String(64))
    
    # Collection details
    collected_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    collection_method = Column(String(200))
    source_system = Column(String(200))
    
    # Chain of custody
    custody_log = Column(JSON)  # Chain of custody tracking
    integrity_verified = Column(Boolean, default=False)
    verification_method = Column(String(100))
    
    # Analysis and relevance
    relevance_score = Column(Float)  # 0.0 to 1.0
    analysis_status = Column(String(50), default="pending")  # pending, in_progress, completed
    analysis_results = Column(Text)
    analysis_tools_used = Column(JSON)
    
    # Legal and compliance
    legal_hold = Column(Boolean, default=False)
    retention_period_days = Column(Integer, default=2555)  # 7 years default
    confidentiality_level = Column(String(20), default="internal")
    
    # Metadata
    tags = Column(JSON)
    ioc_indicators = Column(JSON)  # Indicators of Compromise extracted
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel", back_populates="artifacts")
    collector = relationship("User")


class IncidentCommunication(Base):
    """Communication log for incident response"""
    __tablename__ = "incident_communications"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Communication details
    communication_type = Column(String(100), nullable=False)  # status_update, escalation, notification, etc.
    channel = Column(SQLEnum(CommunicationChannel), nullable=False)
    subject = Column(String(500))
    message = Column(Text, nullable=False)
    
    # Participants
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipients = Column(JSON)  # List of recipient IDs and/or external contacts
    cc_recipients = Column(JSON)
    bcc_recipients = Column(JSON)
    
    # Timing and urgency
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    urgency = Column(String(20), default="normal")  # low, normal, high, urgent
    read_receipt_required = Column(Boolean, default=False)
    
    # External communication
    external_recipients = Column(JSON)  # External parties (customers, vendors, media, etc.)
    regulatory_notification = Column(Boolean, default=False)
    public_communication = Column(Boolean, default=False)
    
    # Response tracking
    responses_received = Column(JSON)  # Track responses to communications
    acknowledgments = Column(JSON)  # Track message acknowledgments
    
    # Templates and approvals
    template_used = Column(String(200))
    approval_required = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Metadata
    communication_id = Column(String(100))  # External message ID if applicable
    thread_id = Column(String(100))  # For tracking conversation threads
    attachments = Column(JSON)  # List of attachment file paths
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel", back_populates="communications")
    sender = relationship("User", foreign_keys=[sender_id])
    approver = relationship("User", foreign_keys=[approved_by])


class IncidentTask(Base):
    """Tasks and action items during incident response"""
    __tablename__ = "incident_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Task details
    task_name = Column(String(500), nullable=False)
    description = Column(Text)
    task_type = Column(String(100))  # investigation, containment, communication, documentation, etc.
    
    # Assignment and ownership
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Priority and timing
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    due_date = Column(DateTime)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    
    # Status and progress
    status = Column(String(50), default="assigned")  # assigned, in_progress, completed, cancelled, blocked
    progress_percentage = Column(Integer, default=0)
    completion_notes = Column(Text)
    
    # Dependencies and relationships
    depends_on_tasks = Column(JSON)  # Task IDs this task depends on
    blocking_tasks = Column(JSON)  # Tasks this task is blocking
    parent_task_id = Column(Integer, ForeignKey("incident_tasks.id"))
    
    # Results and outcomes
    outcome = Column(Text)
    deliverables = Column(JSON)  # List of deliverable artifacts
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to])
    assigner = relationship("User", foreign_keys=[assigned_by])
    parent_task = relationship("IncidentTask", remote_side=[id])
    subtasks = relationship("IncidentTask", back_populates="parent_task")


class IncidentTimelineEntry(Base):
    """Timeline entries for incident reconstruction"""
    __tablename__ = "incident_timeline_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Timeline entry details
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String(100), nullable=False)  # attack_action, response_action, system_event, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Source and verification
    source = Column(String(200))  # log file, witness account, forensic analysis, etc.
    confidence_level = Column(String(20), default="medium")  # low, medium, high
    verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"))
    
    # Categorization
    phase = Column(SQLEnum(ResponsePhase))
    actor = Column(String(200))  # who/what performed the action
    target = Column(String(200))  # what was affected
    technique = Column(String(200))  # MITRE ATT&CK technique or similar
    
    # Impact and severity
    impact_level = Column(String(20))  # low, medium, high, critical
    business_impact = Column(Text)
    technical_impact = Column(Text)
    
    # Evidence and artifacts
    supporting_artifacts = Column(JSON)  # List of artifact IDs
    indicators = Column(JSON)  # IOCs or other indicators
    
    # Metadata
    tags = Column(JSON)
    coordinates = Column(JSON)  # For mapping/visualization
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel", back_populates="timeline_entries")
    verifier = relationship("User")


class PostIncidentReview(Base):
    """Post-incident review and lessons learned"""
    __tablename__ = "post_incident_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, unique=True)
    
    # Review details
    review_name = Column(String(300), nullable=False)
    review_date = Column(DateTime, nullable=False)
    facilitator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    participants = Column(JSON)  # List of participant IDs
    
    # Timeline analysis
    detection_time_minutes = Column(Integer)  # Time from occurrence to detection
    response_time_minutes = Column(Integer)  # Time from detection to response start
    containment_time_minutes = Column(Integer)  # Time to contain the incident
    resolution_time_minutes = Column(Integer)  # Time to full resolution
    
    # Effectiveness assessment
    response_effectiveness = Column(String(20))  # excellent, good, fair, poor
    communication_effectiveness = Column(String(20))
    coordination_effectiveness = Column(String(20))
    tool_effectiveness = Column(JSON)  # Effectiveness of tools used
    
    # Root cause analysis
    root_cause = Column(Text)
    contributing_factors = Column(JSON)  # List of contributing factors
    attack_vectors = Column(JSON)  # How the incident occurred
    vulnerabilities_exploited = Column(JSON)  # Vulnerabilities that enabled the incident
    
    # Impact assessment
    total_impact_cost = Column(Float)
    business_downtime_hours = Column(Float)
    data_compromised = Column(Boolean, default=False)
    data_compromised_records = Column(Integer)
    regulatory_fines = Column(Float)
    reputation_impact_assessment = Column(Text)
    
    # What went well
    successes = Column(JSON)  # List of things that went well
    effective_controls = Column(JSON)  # Controls that worked effectively
    good_decisions = Column(JSON)  # Good decisions made during response
    
    # Areas for improvement
    gaps_identified = Column(JSON)  # Gaps in response capability
    improvement_opportunities = Column(JSON)  # Areas for improvement
    ineffective_controls = Column(JSON)  # Controls that didn't work
    
    # Recommendations and action items
    recommendations = Column(JSON)  # List of recommendations
    action_items = Column(JSON)  # Specific action items with owners and due dates
    preventive_measures = Column(JSON)  # Measures to prevent recurrence
    detection_improvements = Column(JSON)  # Improvements to detection capabilities
    
    # Follow-up tracking
    follow_up_required = Column(Boolean, default=True)
    next_review_date = Column(DateTime)
    action_items_status = Column(JSON)  # Status tracking for action items
    
    # Documentation
    executive_summary = Column(Text)
    detailed_report_path = Column(String(500))
    supporting_documents = Column(JSON)  # List of supporting document paths
    
    # Approval and distribution
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    distribution_list = Column(JSON)  # Who should receive the review
    confidentiality_level = Column(String(20), default="internal")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel", back_populates="post_incident_review")
    facilitator = relationship("User", foreign_keys=[facilitator_id])
    approver = relationship("User", foreign_keys=[approved_by])


class IncidentPlaybook(Base):
    """Incident response playbooks and procedures"""
    __tablename__ = "incident_playbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Playbook identification
    playbook_name = Column(String(300), nullable=False)
    playbook_id = Column(String(100), unique=True, nullable=False)
    version = Column(String(20), default="1.0")
    description = Column(Text)
    
    # Applicability
    incident_categories = Column(JSON)  # Categories this playbook applies to
    severity_levels = Column(JSON)  # Severity levels this applies to
    triggers = Column(JSON)  # Conditions that trigger this playbook
    
    # Playbook content
    procedures = Column(JSON)  # Step-by-step procedures
    checklists = Column(JSON)  # Checklists for each phase
    decision_trees = Column(JSON)  # Decision trees for complex scenarios
    escalation_criteria = Column(JSON)  # When and how to escalate
    
    # Resources and contacts
    required_skills = Column(JSON)  # Skills required to execute
    required_tools = Column(JSON)  # Tools needed
    contact_lists = Column(JSON)  # Relevant contacts
    reference_materials = Column(JSON)  # Supporting documentation
    
    # Automation and integration
    automated_actions = Column(JSON)  # Actions that can be automated
    integration_points = Column(JSON)  # System integrations
    notification_templates = Column(JSON)  # Communication templates
    
    # Effectiveness and maintenance
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)  # Success rate when used
    average_resolution_time = Column(Integer)  # Average time to resolution
    last_used = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Approval and ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    review_due_date = Column(DateTime)
    
    # Status
    active = Column(Boolean, default=True)
    draft = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    approver = relationship("User", foreign_keys=[approved_by])


class IncidentMetric(Base):
    """Incident response metrics and KPIs"""
    __tablename__ = "incident_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metric identification
    metric_name = Column(String(200), nullable=False)
    metric_type = Column(String(100), nullable=False)  # time, count, percentage, cost, etc.
    category = Column(String(100))  # response_time, cost, effectiveness, etc.
    
    # Time period
    measurement_period_start = Column(DateTime, nullable=False)
    measurement_period_end = Column(DateTime, nullable=False)
    
    # Metric values
    value = Column(Float)
    unit = Column(String(50))  # minutes, hours, dollars, percentage, etc.
    target_value = Column(Float)  # Target or SLA value
    benchmark_value = Column(Float)  # Industry benchmark
    
    # Breakdown and context
    incident_count = Column(Integer)  # Number of incidents in calculation
    severity_breakdown = Column(JSON)  # Breakdown by severity
    category_breakdown = Column(JSON)  # Breakdown by category
    team_breakdown = Column(JSON)  # Breakdown by team
    
    # Trend information
    previous_period_value = Column(Float)
    trend_direction = Column(String(20))  # improving, declining, stable
    trend_percentage = Column(Float)  # Percentage change
    
    # Data quality
    confidence_level = Column(String(20), default="high")  # high, medium, low
    data_completeness = Column(Float)  # Percentage of complete data
    calculation_method = Column(Text)  # How the metric was calculated
    
    # Metadata
    notes = Column(Text)
    tags = Column(JSON)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)