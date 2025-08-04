from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM as SQLEnum
from datetime import datetime
import uuid
from enum import Enum

Base = declarative_base()

class TrainingStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    OVERDUE = "overdue"

class TrainingType(Enum):
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    CERTIFICATION = "certification"
    AWARENESS = "awareness"
    SKILL_BUILDING = "skill_building"

class TrainingPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class SimulationResult(Enum):
    PASSED = "passed"
    FAILED = "failed"
    REPORTED = "reported"
    IGNORED = "ignored"
    CLICKED = "clicked"

class CompetencyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class AssessmentType(Enum):
    QUIZ = "quiz"
    PRACTICAL = "practical"
    SIMULATION = "simulation"
    CERTIFICATION_EXAM = "certification_exam"

# Training Program and Course Management

class TrainingProgram(Base):
    __tablename__ = "training_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"PROG-{uuid.uuid4().hex[:8].upper()}")
    name = Column(String(500), nullable=False)
    description = Column(Text)
    version = Column(String(20), nullable=False, default="1.0")
    
    # Program metadata
    program_type = Column(SQLEnum(TrainingType), nullable=False)
    priority = Column(SQLEnum(TrainingPriority), default=TrainingPriority.MEDIUM)
    duration_hours = Column(Float)  # Total program duration
    
    # Target audience and requirements
    target_roles = Column(JSON)  # List of job roles
    target_departments = Column(JSON)  # List of departments
    prerequisite_programs = Column(JSON)  # Required prior training
    required_certifications = Column(JSON)  # Certifications needed
    
    # Compliance and scheduling
    mandatory = Column(Boolean, default=False)
    recurring = Column(Boolean, default=False)
    recurrence_months = Column(Integer)  # How often to retake
    grace_period_days = Column(Integer, default=30)  # Days after due date
    
    # Program objectives and outcomes
    learning_objectives = Column(JSON)  # List of learning goals
    competencies_addressed = Column(JSON)  # Skills/competencies covered
    compliance_frameworks = Column(JSON)  # Related compliance requirements
    
    # Status and lifecycle
    active = Column(Boolean, default=True)
    auto_enroll = Column(Boolean, default=False)
    approval_required = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Relationships
    courses = relationship("TrainingCourse", back_populates="program")
    enrollments = relationship("TrainingEnrollment", back_populates="program")

class TrainingCourse(Base):
    __tablename__ = "training_courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"COURSE-{uuid.uuid4().hex[:8].upper()}")
    program_id = Column(Integer, ForeignKey("training_programs.id"))
    
    # Course details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    course_type = Column(String(100))  # Video, Interactive, Document, Assessment
    content_url = Column(String(1000))  # Link to course content
    content_format = Column(String(50))  # SCORM, Video, PDF, Web, etc.
    
    # Course structure
    duration_minutes = Column(Integer)  # Estimated completion time
    difficulty_level = Column(SQLEnum(CompetencyLevel), default=CompetencyLevel.BEGINNER)
    sequence_order = Column(Integer, default=1)  # Order within program
    
    # Content metadata
    language = Column(String(10), default="en")
    tags = Column(JSON)  # Search tags
    categories = Column(JSON)  # Course categories
    
    # Completion criteria
    passing_score = Column(Float)  # Minimum score to pass (0-100)
    attempts_allowed = Column(Integer, default=3)
    time_limit_minutes = Column(Integer)  # Time limit for completion
    
    # Status and availability
    active = Column(Boolean, default=True)
    published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = relationship("TrainingProgram", back_populates="courses")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    assessments = relationship("TrainingAssessment", back_populates="course")

class TrainingEnrollment(Base):
    __tablename__ = "training_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"ENROLL-{uuid.uuid4().hex[:8].upper()}")
    program_id = Column(Integer, ForeignKey("training_programs.id"))
    
    # User information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_role = Column(String(255))
    department = Column(String(255))
    
    # Enrollment details
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    assigned_by = Column(String(255))
    enrollment_type = Column(String(50))  # auto, manual, self
    
    # Progress tracking
    status = Column(SQLEnum(TrainingStatus), default=TrainingStatus.NOT_STARTED)
    progress_percentage = Column(Float, default=0.0)
    started_date = Column(DateTime)
    completed_date = Column(DateTime)
    last_accessed = Column(DateTime)
    
    # Results
    final_score = Column(Float)  # Overall program score
    certificate_issued = Column(Boolean, default=False)
    certificate_id = Column(String(100))
    attempts_count = Column(Integer, default=0)
    
    # Compliance tracking
    compliance_period_start = Column(DateTime)
    compliance_period_end = Column(DateTime)
    next_due_date = Column(DateTime)  # For recurring training
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = relationship("TrainingProgram", back_populates="enrollments")
    course_enrollments = relationship("CourseEnrollment", back_populates="training_enrollment")

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"CENROLL-{uuid.uuid4().hex[:8].upper()}")
    training_enrollment_id = Column(Integer, ForeignKey("training_enrollments.id"))
    course_id = Column(Integer, ForeignKey("training_courses.id"))
    
    # Progress tracking
    status = Column(SQLEnum(TrainingStatus), default=TrainingStatus.NOT_STARTED)
    progress_percentage = Column(Float, default=0.0)
    started_date = Column(DateTime)
    completed_date = Column(DateTime)
    last_accessed = Column(DateTime)
    
    # Performance metrics
    score = Column(Float)  # Course score (0-100)
    time_spent_minutes = Column(Integer, default=0)
    attempts_count = Column(Integer, default=0)
    
    # Course-specific data
    bookmarks = Column(JSON)  # User bookmarks/progress markers
    notes = Column(Text)  # User notes
    feedback_rating = Column(Float)  # 1-5 star rating
    feedback_comments = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    training_enrollment = relationship("TrainingEnrollment", back_populates="course_enrollments")
    course = relationship("TrainingCourse", back_populates="enrollments")

# Phishing Simulation and Awareness Campaigns

class AwarenessCampaign(Base):
    __tablename__ = "awareness_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"CAMP-{uuid.uuid4().hex[:8].upper()}")
    name = Column(String(500), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(100))  # phishing, awareness, newsletter, alert
    
    # Campaign configuration
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT)
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    
    # Target audience
    target_users = Column(JSON)  # List of user IDs or criteria
    target_departments = Column(JSON)
    target_roles = Column(JSON)
    exclude_users = Column(JSON)  # Users to exclude
    
    # Campaign content
    template_id = Column(String(100))  # Reference to email template
    subject_line = Column(String(500))
    content = Column(Text)  # Campaign content/message
    attachments = Column(JSON)  # File attachments
    
    # Delivery settings
    delivery_method = Column(String(50))  # email, sms, portal, popup
    send_frequency = Column(String(50))  # immediate, scheduled, recurring
    randomize_delivery = Column(Boolean, default=False)
    delivery_window_hours = Column(Integer)  # Spread delivery over hours
    
    # Tracking and analytics
    total_recipients = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Campaign metadata
    created_by = Column(String(255))
    approved_by = Column(String(255))
    approval_date = Column(DateTime)
    tags = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    simulations = relationship("PhishingSimulation", back_populates="campaign")
    interactions = relationship("CampaignInteraction", back_populates="campaign")

class PhishingSimulation(Base):
    __tablename__ = "phishing_simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"PHISH-{uuid.uuid4().hex[:8].upper()}")
    campaign_id = Column(Integer, ForeignKey("awareness_campaigns.id"))
    
    # Simulation details
    template_name = Column(String(255), nullable=False)
    difficulty_level = Column(SQLEnum(CompetencyLevel), default=CompetencyLevel.BEGINNER)
    attack_vector = Column(String(100))  # email, sms, usb, social_engineering
    scenario_description = Column(Text)
    
    # Email-specific fields
    sender_email = Column(String(255))
    sender_name = Column(String(255))
    subject_line = Column(String(500))
    email_content = Column(Text)
    landing_page_url = Column(String(1000))
    attachment_filename = Column(String(255))
    
    # Tracking configuration
    track_opens = Column(Boolean, default=True)
    track_clicks = Column(Boolean, default=True)
    track_attachments = Column(Boolean, default=True)
    track_data_entry = Column(Boolean, default=True)
    
    # Simulation metadata
    industry_relevance = Column(JSON)  # Industries this simulation targets
    threat_types = Column(JSON)  # Types of threats simulated
    indicators = Column(JSON)  # Red flags users should identify
    
    # Educational content
    training_materials = Column(JSON)  # Links to related training
    immediate_feedback = Column(Text)  # Feedback shown immediately
    remedial_training = Column(JSON)  # Additional training for failures
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("AwarenessCampaign", back_populates="simulations")
    results = relationship("SimulationResult", back_populates="simulation")

class SimulationResult(Base):
    __tablename__ = "simulation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"RESULT-{uuid.uuid4().hex[:8].upper()}")
    simulation_id = Column(Integer, ForeignKey("phishing_simulations.id"))
    
    # User information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_role = Column(String(255))
    department = Column(String(255))
    
    # Result details
    result = Column(SQLEnum(SimulationResult), nullable=False)
    delivery_time = Column(DateTime)
    interaction_time = Column(DateTime)
    response_time_seconds = Column(Integer)  # Time to click/report
    
    # Interaction tracking
    email_opened = Column(Boolean, default=False)
    email_open_time = Column(DateTime)
    link_clicked = Column(Boolean, default=False)
    link_click_time = Column(DateTime)
    attachment_opened = Column(Boolean, default=False)
    attachment_open_time = Column(DateTime)
    data_entered = Column(Boolean, default=False)
    data_entry_time = Column(DateTime)
    
    # User actions
    reported_as_phishing = Column(Boolean, default=False)
    report_time = Column(DateTime)
    forwarded_email = Column(Boolean, default=False)
    deleted_email = Column(Boolean, default=False)
    
    # Remedial actions
    training_assigned = Column(Boolean, default=False)
    training_completed = Column(Boolean, default=False)
    follow_up_required = Column(Boolean, default=False)
    
    # Metadata
    ip_address = Column(String(45))  # IPv4/IPv6 address
    user_agent = Column(String(1000))  # Browser/device info
    geolocation = Column(JSON)  # Location data if available
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    simulation = relationship("PhishingSimulation", back_populates="results")

class CampaignInteraction(Base):
    __tablename__ = "campaign_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"INT-{uuid.uuid4().hex[:8].upper()}")
    campaign_id = Column(Integer, ForeignKey("awareness_campaigns.id"))
    
    # User information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    
    # Interaction details
    interaction_type = Column(String(50))  # opened, clicked, downloaded, shared
    interaction_time = Column(DateTime, nullable=False)
    interaction_data = Column(JSON)  # Additional data about interaction
    
    # Technical details
    ip_address = Column(String(45))
    user_agent = Column(String(1000))
    referrer = Column(String(1000))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("AwarenessCampaign", back_populates="interactions")

# Competency Assessment and Skills Management

class SecurityCompetency(Base):
    __tablename__ = "security_competencies"
    
    id = Column(Integer, primary_key=True, index=True)
    competency_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"COMP-{uuid.uuid4().hex[:8].upper()}")
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # technical, procedural, awareness, behavioral
    
    # Competency details
    skill_level = Column(SQLEnum(CompetencyLevel), nullable=False)
    domain = Column(String(100))  # NIST, ISO27001, OWASP, etc.
    framework_reference = Column(String(255))  # Reference to standard
    
    # Requirements
    applicable_roles = Column(JSON)  # Job roles this applies to
    applicable_departments = Column(JSON)
    prerequisites = Column(JSON)  # Required prior competencies
    
    # Assessment criteria
    assessment_methods = Column(JSON)  # How to assess this competency
    proficiency_indicators = Column(JSON)  # What demonstrates proficiency
    
    # Metadata
    active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = relationship("CompetencyAssessment", back_populates="competency")
    user_competencies = relationship("UserCompetency", back_populates="competency")

class CompetencyAssessment(Base):
    __tablename__ = "competency_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"ASSESS-{uuid.uuid4().hex[:8].upper()}")
    competency_id = Column(Integer, ForeignKey("security_competencies.id"))
    
    # Assessment details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    assessment_type = Column(SQLEnum(AssessmentType), nullable=False)
    
    # Configuration
    time_limit_minutes = Column(Integer)
    passing_score = Column(Float)  # Minimum score to pass (0-100)
    attempts_allowed = Column(Integer, default=3)
    randomize_questions = Column(Boolean, default=True)
    
    # Questions and content
    questions = Column(JSON)  # Assessment questions/scenarios
    scenarios = Column(JSON)  # Practical scenarios
    resources = Column(JSON)  # Reference materials
    
    # Validity and scheduling
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competency = relationship("SecurityCompetency", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment")

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"ARESULT-{uuid.uuid4().hex[:8].upper()}")
    assessment_id = Column(Integer, ForeignKey("competency_assessments.id"))
    
    # User information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    
    # Results
    score = Column(Float, nullable=False)  # Score achieved (0-100)
    passed = Column(Boolean, nullable=False)
    attempt_number = Column(Integer, default=1)
    
    # Timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)
    time_taken_minutes = Column(Integer)
    
    # Detailed results
    answers = Column(JSON)  # User answers
    question_scores = Column(JSON)  # Score per question
    strengths = Column(JSON)  # Areas of strength
    weaknesses = Column(JSON)  # Areas needing improvement
    
    # Recommendations
    recommended_training = Column(JSON)  # Suggested training programs
    next_assessment_date = Column(DateTime)  # When to reassess
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("CompetencyAssessment", back_populates="results")

class UserCompetency(Base):
    __tablename__ = "user_competencies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_competency_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"UCOMP-{uuid.uuid4().hex[:8].upper()}")
    competency_id = Column(Integer, ForeignKey("security_competencies.id"))
    
    # User information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_role = Column(String(255))
    department = Column(String(255))
    
    # Competency status
    current_level = Column(SQLEnum(CompetencyLevel), nullable=False)
    target_level = Column(SQLEnum(CompetencyLevel), nullable=False)
    proficient = Column(Boolean, default=False)
    
    # Assessment history
    last_assessed = Column(DateTime)
    last_assessment_score = Column(Float)
    assessment_count = Column(Integer, default=0)
    
    # Training history
    related_training_completed = Column(JSON)  # Training programs completed
    training_hours = Column(Float, default=0.0)
    
    # Verification and validation
    verified_by = Column(String(255))  # Who verified this competency
    verification_date = Column(DateTime)
    verification_method = Column(String(100))  # assessment, observation, certification
    
    # Renewal and maintenance
    expires_at = Column(DateTime)  # When competency expires
    renewal_required = Column(Boolean, default=False)
    next_assessment_due = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competency = relationship("SecurityCompetency", back_populates="user_competencies")

# Certification and Compliance Tracking

class TrainingCertification(Base):
    __tablename__ = "training_certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"CERT-{uuid.uuid4().hex[:8].upper()}")
    
    # Certification details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    issuing_organization = Column(String(255))
    certification_type = Column(String(100))  # internal, external, regulatory
    
    # Requirements
    required_training_programs = Column(JSON)  # Programs that must be completed
    required_competencies = Column(JSON)  # Competencies that must be achieved
    prerequisite_certifications = Column(JSON)  # Other certs required first
    
    # Validity and renewal
    validity_period_months = Column(Integer)  # How long cert is valid
    renewal_required = Column(Boolean, default=True)
    renewal_grace_period_days = Column(Integer, default=30)
    continuing_education_required = Column(Boolean, default=False)
    
    # Compliance mapping
    compliance_frameworks = Column(JSON)  # Which frameworks this satisfies
    regulatory_requirements = Column(JSON)  # Regulatory mandates
    
    # Certification criteria
    minimum_score = Column(Float)  # Minimum score for certification
    assessment_required = Column(Boolean, default=True)
    practical_demonstration = Column(Boolean, default=False)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_certifications = relationship("UserCertification", back_populates="certification")

class UserCertification(Base):
    __tablename__ = "user_certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_cert_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"UCERT-{uuid.uuid4().hex[:8].upper()}")
    certification_id = Column(Integer, ForeignKey("training_certifications.id"))
    
    # User information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    
    # Certification status
    status = Column(SQLEnum(TrainingStatus), nullable=False)
    earned_date = Column(DateTime)
    expires_date = Column(DateTime)
    
    # Certification details
    certificate_number = Column(String(100), unique=True)
    digital_badge_url = Column(String(1000))
    certificate_file_path = Column(String(1000))
    
    # Assessment results
    final_score = Column(Float)  # Final certification score
    assessment_results = Column(JSON)  # Detailed assessment data
    
    # Renewal tracking
    renewal_due_date = Column(DateTime)
    renewal_reminders_sent = Column(Integer, default=0)
    last_renewal_date = Column(DateTime)
    
    # Verification
    verified = Column(Boolean, default=False)
    verification_code = Column(String(100))
    issued_by = Column(String(255))
    
    # Compliance tracking
    compliance_period_start = Column(DateTime)
    compliance_period_end = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    certification = relationship("TrainingCertification", back_populates="user_certifications")

# Training Analytics and Assessment

class TrainingAnalytics(Base):
    __tablename__ = "training_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"ANALYTICS-{uuid.uuid4().hex[:8].upper()}")
    
    # Metric details
    metric_name = Column(String(255), nullable=False)
    metric_type = Column(String(100))  # completion_rate, score_average, time_to_complete
    category = Column(String(100))  # program, course, user, department
    scope = Column(String(100))  # organization, department, role, individual
    
    # Target and measurement
    target_entity_id = Column(String(255))  # ID of what's being measured
    target_entity_type = Column(String(100))  # program, user, department, etc.
    
    # Metric values
    current_value = Column(Float)
    target_value = Column(Float)
    baseline_value = Column(Float)
    trend_direction = Column(String(20))  # improving, declining, stable
    
    # Time period
    measurement_date = Column(DateTime, default=datetime.utcnow)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Historical data
    historical_values = Column(JSON)  # Time series data
    
    # Metadata
    calculation_method = Column(Text)  # How the metric is calculated
    data_sources = Column(JSON)  # What data sources are used
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrainingAssessment(Base):
    __tablename__ = "training_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"TASSESS-{uuid.uuid4().hex[:8].upper()}")
    course_id = Column(Integer, ForeignKey("training_courses.id"))
    
    # Assessment details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    assessment_type = Column(SQLEnum(AssessmentType), nullable=False)
    
    # Configuration
    questions_count = Column(Integer, default=10)
    time_limit_minutes = Column(Integer)
    passing_score = Column(Float, default=70.0)
    attempts_allowed = Column(Integer, default=3)
    randomize_questions = Column(Boolean, default=True)
    show_results_immediately = Column(Boolean, default=True)
    
    # Content
    question_pool = Column(JSON)  # Pool of questions to draw from
    scenarios = Column(JSON)  # Scenario-based questions
    
    # Feedback and remediation
    pass_feedback = Column(Text)  # Feedback for passing
    fail_feedback = Column(Text)  # Feedback for failing
    remedial_resources = Column(JSON)  # Additional resources for failed attempts
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("TrainingCourse", back_populates="assessments")
    responses = relationship("AssessmentResponse", back_populates="assessment")

class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"RESP-{uuid.uuid4().hex[:8].upper()}")
    assessment_id = Column(Integer, ForeignKey("training_assessments.id"))
    
    # User information
    user_id = Column(String(255), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    
    # Response details
    attempt_number = Column(Integer, default=1)
    started_at = Column(DateTime, nullable=False)
    submitted_at = Column(DateTime)
    time_taken_minutes = Column(Integer)
    
    # Results
    score = Column(Float)  # Score achieved (0-100)
    passed = Column(Boolean)
    questions_answered = Column(Integer)
    questions_correct = Column(Integer)
    
    # Response data
    responses = Column(JSON)  # User responses to questions
    question_scores = Column(JSON)  # Score per question
    
    # Status
    completed = Column(Boolean, default=False)
    auto_submitted = Column(Boolean, default=False)  # Due to time limit
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("TrainingAssessment", back_populates="responses")