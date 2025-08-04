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


class LessonLearned(Base):
    """Lessons learned from incidents and post-incident reviews"""
    __tablename__ = "lessons_learned"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Lesson identification
    lesson_title = Column(String(500), nullable=False)
    lesson_summary = Column(Text, nullable=False)
    lesson_category = Column(String(100))  # process, technology, people, training, etc.
    
    # Source incident/review
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    post_incident_review_id = Column(Integer, ForeignKey("post_incident_reviews.id"))
    
    # Lesson details
    what_happened = Column(Text)  # What went wrong or right
    why_it_happened = Column(Text)  # Root cause analysis
    what_we_learned = Column(Text)  # Key insights gained
    
    # Recommendations and actions
    recommendations = Column(JSON)  # List of recommendations
    preventive_measures = Column(JSON)  # Specific measures to prevent recurrence
    process_improvements = Column(JSON)  # Process improvements identified
    
    # Impact and relevance
    severity_prevented = Column(SQLEnum(IncidentSeverity))  # Potential severity prevented
    cost_savings_estimated = Column(Float)  # Estimated cost savings from lesson
    applicability_scope = Column(String(100))  # organization-wide, department, team, etc.
    affected_systems = Column(JSON)  # Systems this lesson applies to
    
    # Implementation tracking
    implementation_status = Column(String(50), default="identified")  # identified, planned, in_progress, implemented, verified
    implementation_date = Column(DateTime)
    implementation_owner = Column(Integer, ForeignKey("users.id"))
    implementation_cost = Column(Float)
    implementation_effort_hours = Column(Float)
    
    # Knowledge management
    keywords = Column(JSON)  # Keywords for searchability
    related_lessons = Column(JSON)  # IDs of related lessons
    knowledge_base_category = Column(String(100))
    training_material_created = Column(Boolean, default=False)
    
    # Verification and effectiveness
    effectiveness_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    verification_method = Column(Text)
    recurrence_prevented = Column(Boolean)
    
    # Approval and sharing
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    shared_externally = Column(Boolean, default=False)
    sharing_restrictions = Column(Text)
    
    # Metadata
    confidence_level = Column(String(20), default="medium")  # high, medium, low
    evidence_quality = Column(String(20), default="medium")
    tags = Column(JSON)
    
    # Timestamps
    identified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel")
    post_incident_review = relationship("PostIncidentReview")
    implementation_owner_user = relationship("User", foreign_keys=[implementation_owner])
    approver = relationship("User", foreign_keys=[approved_by])


class ActionItem(Base):
    """Action items from post-incident reviews and lessons learned"""
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action item identification
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(100))  # process_improvement, training, technology, policy, etc.
    
    # Source
    post_incident_review_id = Column(Integer, ForeignKey("post_incident_reviews.id"))
    lesson_learned_id = Column(Integer, ForeignKey("lessons_learned.id"))
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    
    # Assignment and ownership
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    responsible_team = Column(String(200))
    
    # Priority and timing
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    due_date = Column(DateTime, nullable=False)
    estimated_effort_hours = Column(Float)
    estimated_cost = Column(Float)
    
    # Status and progress
    status = Column(String(50), default="open")  # open, in_progress, completed, cancelled, on_hold
    progress_percentage = Column(Integer, default=0)
    status_notes = Column(Text)
    
    # Implementation details
    success_criteria = Column(Text)  # How to measure success
    deliverables = Column(JSON)  # Expected deliverables
    dependencies = Column(JSON)  # Dependencies on other items or resources
    risks = Column(Text)  # Risks to implementation
    
    # Results and outcomes
    completion_notes = Column(Text)
    actual_effort_hours = Column(Float)
    actual_cost = Column(Float)
    effectiveness_rating = Column(Integer)  # 1-5 scale
    lessons_from_implementation = Column(Text)
    
    # Verification and closure
    verification_required = Column(Boolean, default=True)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(Text)
    
    # Metadata
    tags = Column(JSON)
    related_action_items = Column(JSON)  # IDs of related action items
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    post_incident_review = relationship("PostIncidentReview")
    lesson_learned = relationship("LessonLearned")
    incident = relationship("IncidentModel")
    assignee = relationship("User", foreign_keys=[assigned_to])
    assigner = relationship("User", foreign_keys=[assigned_by])
    verifier = relationship("User", foreign_keys=[verified_by])


class KnowledgeArticle(Base):
    """Knowledge base articles for incident response knowledge management"""
    __tablename__ = "knowledge_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Article identification
    title = Column(String(500), nullable=False)
    article_type = Column(String(100))  # procedure, guideline, checklist, reference, lesson, etc.
    category = Column(String(100))  # incident_response, forensics, communication, etc.
    subcategory = Column(String(100))
    
    # Content
    summary = Column(Text)
    content = Column(Text, nullable=False)
    content_format = Column(String(20), default="markdown")  # markdown, html, plain_text
    
    # Source and derivation
    derived_from_incident = Column(Integer, ForeignKey("incidents.id"))
    derived_from_lesson = Column(Integer, ForeignKey("lessons_learned.id"))
    source_documents = Column(JSON)  # List of source document references
    
    # Applicability and audience
    target_audience = Column(JSON)  # List of roles/teams this applies to
    skill_level_required = Column(String(20), default="intermediate")  # beginner, intermediate, advanced, expert
    applicable_scenarios = Column(JSON)  # Scenarios where this applies
    
    # Knowledge management
    keywords = Column(JSON)  # Keywords for search
    related_articles = Column(JSON)  # IDs of related articles
    prerequisites = Column(JSON)  # Prerequisite knowledge or articles
    follow_up_reading = Column(JSON)  # Recommended follow-up articles
    
    # Quality and maintenance
    accuracy_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    verified_by = Column(Integer, ForeignKey("users.id"))
    last_reviewed = Column(DateTime)
    review_frequency_days = Column(Integer, default=365)  # How often to review
    
    # Usage and effectiveness
    view_count = Column(Integer, default=0)
    usefulness_rating = Column(Float)  # Average user rating
    usage_feedback = Column(JSON)  # User feedback
    search_ranking = Column(Integer, default=50)  # Search result ranking weight
    
    # Publishing and access
    published = Column(Boolean, default=False)
    publication_date = Column(DateTime)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Access control
    access_level = Column(String(50), default="internal")  # public, internal, restricted, confidential
    allowed_roles = Column(JSON)  # Roles allowed to access
    allowed_teams = Column(JSON)  # Teams allowed to access
    
    # Versioning
    version = Column(String(20), default="1.0")
    previous_version_id = Column(Integer, ForeignKey("knowledge_articles.id"))
    change_log = Column(JSON)  # Log of changes made
    
    # Metadata
    tags = Column(JSON)
    attachments = Column(JSON)  # List of attachment file paths
    external_links = Column(JSON)  # External reference links
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("IncidentModel")
    lesson_learned = relationship("LessonLearned")
    author = relationship("User", foreign_keys=[author_id])
    approver = relationship("User", foreign_keys=[approved_by])
    verifier = relationship("User", foreign_keys=[verified_by])
    previous_version = relationship("KnowledgeArticle", remote_side=[id])


class TrendAnalysis(Base):
    """Trend analysis for incidents and lessons learned"""
    __tablename__ = "trend_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Analysis identification
    analysis_name = Column(String(300), nullable=False)
    analysis_type = Column(String(100))  # incident_trends, lesson_effectiveness, response_performance, etc.
    time_period_start = Column(DateTime, nullable=False)
    time_period_end = Column(DateTime, nullable=False)
    
    # Analysis scope
    incident_categories = Column(JSON)  # Categories included in analysis
    severity_levels = Column(JSON)  # Severity levels included
    teams_included = Column(JSON)  # Teams included in analysis
    
    # Trend findings
    key_trends = Column(JSON)  # List of key trends identified
    emerging_patterns = Column(JSON)  # New patterns detected
    trend_directions = Column(JSON)  # Improving, declining, stable trends
    
    # Statistical analysis
    incident_volume_trend = Column(JSON)  # Volume trend data
    severity_distribution_trend = Column(JSON)  # Severity distribution changes
    response_time_trends = Column(JSON)  # Response time improvements/degradation
    cost_trends = Column(JSON)  # Cost trend analysis
    
    # Predictive insights
    risk_predictions = Column(JSON)  # Predicted risk areas
    resource_needs_forecast = Column(JSON)  # Predicted resource needs
    seasonal_patterns = Column(JSON)  # Seasonal or cyclical patterns
    
    # Recommendations
    strategic_recommendations = Column(JSON)  # High-level strategic recommendations
    tactical_recommendations = Column(JSON)  # Specific tactical improvements
    investment_priorities = Column(JSON)  # Priority areas for investment
    
    # Data quality and methodology
    data_sources = Column(JSON)  # Data sources used
    methodology = Column(Text)  # Analysis methodology
    confidence_level = Column(String(20), default="medium")  # high, medium, low
    limitations = Column(Text)  # Analysis limitations
    
    # Results and impact
    findings_summary = Column(Text)
    business_impact = Column(Text)
    action_items_generated = Column(JSON)  # Action items from analysis
    
    # Approval and distribution
    analyst_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    distribution_list = Column(JSON)
    
    # Metadata
    tags = Column(JSON)
    supporting_charts = Column(JSON)  # Chart/graph file paths
    detailed_report_path = Column(String(500))
    
    # Timestamps
    analysis_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyst = relationship("User", foreign_keys=[analyst_id])
    approver = relationship("User", foreign_keys=[approved_by])