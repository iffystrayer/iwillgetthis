from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TrainingStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    OVERDUE = "overdue"

class TrainingTypeEnum(str, Enum):
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    CERTIFICATION = "certification"
    AWARENESS = "awareness"
    SKILL_BUILDING = "skill_building"

class TrainingPriorityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class SimulationResultEnum(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    REPORTED = "reported"
    IGNORED = "ignored"
    CLICKED = "clicked"

class CompetencyLevelEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class AssessmentTypeEnum(str, Enum):
    QUIZ = "quiz"
    PRACTICAL = "practical"
    SIMULATION = "simulation"
    CERTIFICATION_EXAM = "certification_exam"

# Training Program Schemas

class TrainingProgramBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    version: str = Field(default="1.0", max_length=20)
    program_type: TrainingTypeEnum
    priority: TrainingPriorityEnum = TrainingPriorityEnum.MEDIUM
    duration_hours: Optional[float] = Field(None, ge=0, le=1000)
    target_roles: List[str] = Field(default_factory=list)
    target_departments: List[str] = Field(default_factory=list)
    prerequisite_programs: List[str] = Field(default_factory=list)
    required_certifications: List[str] = Field(default_factory=list)
    mandatory: bool = Field(default=False)
    recurring: bool = Field(default=False)
    recurrence_months: Optional[int] = Field(None, ge=1, le=60)
    grace_period_days: int = Field(default=30, ge=0, le=365)
    learning_objectives: List[str] = Field(default_factory=list)
    competencies_addressed: List[str] = Field(default_factory=list)
    compliance_frameworks: List[str] = Field(default_factory=list)
    active: bool = Field(default=True)
    auto_enroll: bool = Field(default=False)
    approval_required: bool = Field(default=False)

class TrainingProgramCreate(TrainingProgramBase):
    created_by: str = Field(..., min_length=1, max_length=255)

class TrainingProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=20)
    program_type: Optional[TrainingTypeEnum] = None
    priority: Optional[TrainingPriorityEnum] = None
    duration_hours: Optional[float] = Field(None, ge=0, le=1000)
    target_roles: Optional[List[str]] = None
    target_departments: Optional[List[str]] = None
    prerequisite_programs: Optional[List[str]] = None
    required_certifications: Optional[List[str]] = None
    mandatory: Optional[bool] = None
    recurring: Optional[bool] = None
    recurrence_months: Optional[int] = Field(None, ge=1, le=60)
    grace_period_days: Optional[int] = Field(None, ge=0, le=365)
    learning_objectives: Optional[List[str]] = None
    competencies_addressed: Optional[List[str]] = None
    compliance_frameworks: Optional[List[str]] = None
    active: Optional[bool] = None
    auto_enroll: Optional[bool] = None
    approval_required: Optional[bool] = None
    updated_by: Optional[str] = None

class TrainingProgramResponse(TrainingProgramBase):
    id: int
    program_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

# Training Course Schemas

class TrainingCourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    course_type: Optional[str] = Field(None, max_length=100)
    content_url: Optional[str] = Field(None, max_length=1000)
    content_format: Optional[str] = Field(None, max_length=50)
    duration_minutes: Optional[int] = Field(None, ge=0, le=10080)  # Max 1 week
    difficulty_level: CompetencyLevelEnum = CompetencyLevelEnum.BEGINNER
    sequence_order: int = Field(default=1, ge=1)
    language: str = Field(default="en", max_length=10)
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    attempts_allowed: int = Field(default=3, ge=1, le=10)
    time_limit_minutes: Optional[int] = Field(None, ge=0, le=1440)  # Max 24 hours
    active: bool = Field(default=True)
    published: bool = Field(default=False)

class TrainingCourseCreate(TrainingCourseBase):
    program_id: int = Field(..., gt=0)

class TrainingCourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    course_type: Optional[str] = Field(None, max_length=100)
    content_url: Optional[str] = Field(None, max_length=1000)
    content_format: Optional[str] = Field(None, max_length=50)
    duration_minutes: Optional[int] = Field(None, ge=0, le=10080)
    difficulty_level: Optional[CompetencyLevelEnum] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    language: Optional[str] = Field(None, max_length=10)
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    attempts_allowed: Optional[int] = Field(None, ge=1, le=10)
    time_limit_minutes: Optional[int] = Field(None, ge=0, le=1440)
    active: Optional[bool] = None
    published: Optional[bool] = None

class TrainingCourseResponse(TrainingCourseBase):
    id: int
    course_id: str
    program_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Training Enrollment Schemas

class TrainingEnrollmentBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    user_role: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    enrollment_type: str = Field(default="manual", max_length=50)

class TrainingEnrollmentCreate(TrainingEnrollmentBase):
    program_id: int = Field(..., gt=0)
    assigned_by: str = Field(..., min_length=1, max_length=255)

class TrainingEnrollmentUpdate(BaseModel):
    due_date: Optional[datetime] = None
    status: Optional[TrainingStatusEnum] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    final_score: Optional[float] = Field(None, ge=0, le=100)
    certificate_issued: Optional[bool] = None
    certificate_id: Optional[str] = Field(None, max_length=100)

class TrainingEnrollmentResponse(TrainingEnrollmentBase):
    id: int
    enrollment_id: str
    program_id: int
    enrollment_date: datetime
    assigned_by: str
    status: TrainingStatusEnum
    progress_percentage: float
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    final_score: Optional[float] = None
    certificate_issued: bool
    certificate_id: Optional[str] = None
    attempts_count: int
    compliance_period_start: Optional[datetime] = None
    compliance_period_end: Optional[datetime] = None
    next_due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Course Enrollment Schemas

class CourseEnrollmentBase(BaseModel):
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    feedback_rating: Optional[float] = Field(None, ge=1, le=5)
    feedback_comments: Optional[str] = None
    notes: Optional[str] = None

class CourseEnrollmentCreate(CourseEnrollmentBase):
    training_enrollment_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)

class CourseEnrollmentUpdate(BaseModel):
    status: Optional[TrainingStatusEnum] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    score: Optional[float] = Field(None, ge=0, le=100)
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    bookmarks: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    feedback_rating: Optional[float] = Field(None, ge=1, le=5)
    feedback_comments: Optional[str] = None

class CourseEnrollmentResponse(CourseEnrollmentBase):
    id: int
    enrollment_id: str
    training_enrollment_id: int
    course_id: int
    status: TrainingStatusEnum
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    score: Optional[float] = None
    time_spent_minutes: int
    attempts_count: int
    bookmarks: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Awareness Campaign Schemas

class AwarenessCampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    campaign_type: str = Field(..., max_length=100)
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    target_users: List[str] = Field(default_factory=list)
    target_departments: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    exclude_users: List[str] = Field(default_factory=list)
    template_id: Optional[str] = Field(None, max_length=100)
    subject_line: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    delivery_method: str = Field(default="email", max_length=50)
    send_frequency: str = Field(default="immediate", max_length=50)
    randomize_delivery: bool = Field(default=False)
    delivery_window_hours: Optional[int] = Field(None, ge=1, le=168)
    tags: List[str] = Field(default_factory=list)

    @validator('scheduled_end')
    def validate_end_date(cls, v, values):
        if v and 'scheduled_start' in values and v <= values['scheduled_start']:
            raise ValueError('End date must be after start date')
        return v

class AwarenessCampaignCreate(AwarenessCampaignBase):
    created_by: str = Field(..., min_length=1, max_length=255)

class AwarenessCampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    campaign_type: Optional[str] = Field(None, max_length=100)
    status: Optional[CampaignStatusEnum] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    target_users: Optional[List[str]] = None
    target_departments: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    exclude_users: Optional[List[str]] = None
    template_id: Optional[str] = Field(None, max_length=100)
    subject_line: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    delivery_method: Optional[str] = Field(None, max_length=50)
    send_frequency: Optional[str] = Field(None, max_length=50)
    randomize_delivery: Optional[bool] = None
    delivery_window_hours: Optional[int] = Field(None, ge=1, le=168)
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class AwarenessCampaignResponse(AwarenessCampaignBase):
    id: int
    campaign_id: str
    status: CampaignStatusEnum
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    total_recipients: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    reported_count: int
    failed_count: int
    created_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Phishing Simulation Schemas

class PhishingSimulationBase(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=255)
    difficulty_level: CompetencyLevelEnum = CompetencyLevelEnum.BEGINNER
    attack_vector: str = Field(default="email", max_length=100)
    scenario_description: Optional[str] = None
    sender_email: Optional[str] = Field(None, max_length=255)
    sender_name: Optional[str] = Field(None, max_length=255)
    subject_line: Optional[str] = Field(None, max_length=500)
    email_content: Optional[str] = None
    landing_page_url: Optional[str] = Field(None, max_length=1000)
    attachment_filename: Optional[str] = Field(None, max_length=255)
    track_opens: bool = Field(default=True)
    track_clicks: bool = Field(default=True)
    track_attachments: bool = Field(default=True)
    track_data_entry: bool = Field(default=True)
    industry_relevance: List[str] = Field(default_factory=list)
    threat_types: List[str] = Field(default_factory=list)
    indicators: List[str] = Field(default_factory=list)
    training_materials: List[Dict[str, Any]] = Field(default_factory=list)
    immediate_feedback: Optional[str] = None
    remedial_training: List[int] = Field(default_factory=list)

class PhishingSimulationCreate(PhishingSimulationBase):
    campaign_id: int = Field(..., gt=0)

class PhishingSimulationUpdate(BaseModel):
    template_name: Optional[str] = Field(None, min_length=1, max_length=255)
    difficulty_level: Optional[CompetencyLevelEnum] = None
    attack_vector: Optional[str] = Field(None, max_length=100)
    scenario_description: Optional[str] = None
    sender_email: Optional[str] = Field(None, max_length=255)
    sender_name: Optional[str] = Field(None, max_length=255)
    subject_line: Optional[str] = Field(None, max_length=500)
    email_content: Optional[str] = None
    landing_page_url: Optional[str] = Field(None, max_length=1000)
    attachment_filename: Optional[str] = Field(None, max_length=255)
    track_opens: Optional[bool] = None
    track_clicks: Optional[bool] = None
    track_attachments: Optional[bool] = None
    track_data_entry: Optional[bool] = None
    industry_relevance: Optional[List[str]] = None
    threat_types: Optional[List[str]] = None
    indicators: Optional[List[str]] = None
    training_materials: Optional[List[Dict[str, Any]]] = None
    immediate_feedback: Optional[str] = None
    remedial_training: Optional[List[int]] = None

class PhishingSimulationResponse(PhishingSimulationBase):
    id: int
    simulation_id: str
    campaign_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Simulation Result Schemas

class SimulationResultBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    user_role: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    result: SimulationResultEnum
    delivery_time: Optional[datetime] = None
    interaction_time: Optional[datetime] = None
    response_time_seconds: Optional[int] = Field(None, ge=0)
    email_opened: bool = Field(default=False)
    email_open_time: Optional[datetime] = None
    link_clicked: bool = Field(default=False)
    link_click_time: Optional[datetime] = None
    attachment_opened: bool = Field(default=False)
    attachment_open_time: Optional[datetime] = None
    data_entered: bool = Field(default=False)
    data_entry_time: Optional[datetime] = None
    reported_as_phishing: bool = Field(default=False)
    report_time: Optional[datetime] = None
    forwarded_email: bool = Field(default=False)
    deleted_email: bool = Field(default=False)
    training_assigned: bool = Field(default=False)
    training_completed: bool = Field(default=False)
    follow_up_required: bool = Field(default=False)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=1000)
    geolocation: Optional[Dict[str, Any]] = None

class SimulationResultCreate(SimulationResultBase):
    simulation_id: int = Field(..., gt=0)

class SimulationResultUpdate(BaseModel):
    result: Optional[SimulationResultEnum] = None
    interaction_time: Optional[datetime] = None
    response_time_seconds: Optional[int] = Field(None, ge=0)
    email_opened: Optional[bool] = None
    email_open_time: Optional[datetime] = None
    link_clicked: Optional[bool] = None
    link_click_time: Optional[datetime] = None
    attachment_opened: Optional[bool] = None
    attachment_open_time: Optional[datetime] = None
    data_entered: Optional[bool] = None
    data_entry_time: Optional[datetime] = None
    reported_as_phishing: Optional[bool] = None
    report_time: Optional[datetime] = None
    forwarded_email: Optional[bool] = None
    deleted_email: Optional[bool] = None
    training_assigned: Optional[bool] = None
    training_completed: Optional[bool] = None
    follow_up_required: Optional[bool] = None

class SimulationResultResponse(SimulationResultBase):
    id: int
    result_id: str
    simulation_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Security Competency Schemas

class SecurityCompetencyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    skill_level: CompetencyLevelEnum
    domain: Optional[str] = Field(None, max_length=100)
    framework_reference: Optional[str] = Field(None, max_length=255)
    applicable_roles: List[str] = Field(default_factory=list)
    applicable_departments: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    assessment_methods: List[str] = Field(default_factory=list)
    proficiency_indicators: List[str] = Field(default_factory=list)
    active: bool = Field(default=True)
    version: str = Field(default="1.0", max_length=20)

class SecurityCompetencyCreate(SecurityCompetencyBase):
    pass

class SecurityCompetencyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    skill_level: Optional[CompetencyLevelEnum] = None
    domain: Optional[str] = Field(None, max_length=100)
    framework_reference: Optional[str] = Field(None, max_length=255)
    applicable_roles: Optional[List[str]] = None
    applicable_departments: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    assessment_methods: Optional[List[str]] = None
    proficiency_indicators: Optional[List[str]] = None
    active: Optional[bool] = None
    version: Optional[str] = Field(None, max_length=20)

class SecurityCompetencyResponse(SecurityCompetencyBase):
    id: int
    competency_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Competency Assessment Schemas

class CompetencyAssessmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assessment_type: AssessmentTypeEnum
    time_limit_minutes: Optional[int] = Field(None, ge=0, le=1440)
    passing_score: float = Field(default=70.0, ge=0, le=100)
    attempts_allowed: int = Field(default=3, ge=1, le=10)
    randomize_questions: bool = Field(default=True)
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    scenarios: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    active: bool = Field(default=True)

class CompetencyAssessmentCreate(CompetencyAssessmentBase):
    competency_id: int = Field(..., gt=0)

class CompetencyAssessmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assessment_type: Optional[AssessmentTypeEnum] = None
    time_limit_minutes: Optional[int] = Field(None, ge=0, le=1440)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    attempts_allowed: Optional[int] = Field(None, ge=1, le=10)
    randomize_questions: Optional[bool] = None
    questions: Optional[List[Dict[str, Any]]] = None
    scenarios: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    active: Optional[bool] = None

class CompetencyAssessmentResponse(CompetencyAssessmentBase):
    id: int
    assessment_id: str
    competency_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Assessment Result Schemas

class AssessmentResultBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    score: float = Field(..., ge=0, le=100)
    passed: bool
    attempt_number: int = Field(default=1, ge=1)
    started_at: datetime
    completed_at: datetime
    time_taken_minutes: Optional[int] = Field(None, ge=0)
    answers: Dict[str, Any] = Field(default_factory=dict)
    question_scores: Dict[str, Any] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommended_training: List[str] = Field(default_factory=list)
    next_assessment_date: Optional[datetime] = None

class AssessmentResultCreate(AssessmentResultBase):
    assessment_id: int = Field(..., gt=0)

class AssessmentResultUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    passed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    time_taken_minutes: Optional[int] = Field(None, ge=0)
    answers: Optional[Dict[str, Any]] = None
    question_scores: Optional[Dict[str, Any]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommended_training: Optional[List[str]] = None
    next_assessment_date: Optional[datetime] = None

class AssessmentResultResponse(AssessmentResultBase):
    id: int
    result_id: str
    assessment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Competency Schemas

class UserCompetencyBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    user_role: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    current_level: CompetencyLevelEnum
    target_level: CompetencyLevelEnum
    proficient: bool = Field(default=False)
    last_assessed: Optional[datetime] = None
    last_assessment_score: Optional[float] = Field(None, ge=0, le=100)
    assessment_count: int = Field(default=0, ge=0)
    related_training_completed: List[str] = Field(default_factory=list)
    training_hours: float = Field(default=0.0, ge=0)
    verified_by: Optional[str] = Field(None, max_length=255)
    verification_date: Optional[datetime] = None
    verification_method: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None
    renewal_required: bool = Field(default=False)
    next_assessment_due: Optional[datetime] = None

class UserCompetencyCreate(UserCompetencyBase):
    competency_id: int = Field(..., gt=0)

class UserCompetencyUpdate(BaseModel):
    current_level: Optional[CompetencyLevelEnum] = None
    target_level: Optional[CompetencyLevelEnum] = None
    proficient: Optional[bool] = None
    last_assessed: Optional[datetime] = None
    last_assessment_score: Optional[float] = Field(None, ge=0, le=100)
    assessment_count: Optional[int] = Field(None, ge=0)
    related_training_completed: Optional[List[str]] = None
    training_hours: Optional[float] = Field(None, ge=0)
    verified_by: Optional[str] = Field(None, max_length=255)
    verification_date: Optional[datetime] = None
    verification_method: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None
    renewal_required: Optional[bool] = None
    next_assessment_due: Optional[datetime] = None

class UserCompetencyResponse(UserCompetencyBase):
    id: int
    user_competency_id: str
    competency_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Training Certification Schemas

class TrainingCertificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    issuing_organization: Optional[str] = Field(None, max_length=255)
    certification_type: Optional[str] = Field(None, max_length=100)
    required_training_programs: List[int] = Field(default_factory=list)
    required_competencies: List[int] = Field(default_factory=list)
    prerequisite_certifications: List[int] = Field(default_factory=list)
    validity_period_months: Optional[int] = Field(None, ge=1, le=120)
    renewal_required: bool = Field(default=True)
    renewal_grace_period_days: int = Field(default=30, ge=0, le=365)
    continuing_education_required: bool = Field(default=False)
    compliance_frameworks: List[str] = Field(default_factory=list)
    regulatory_requirements: List[str] = Field(default_factory=list)
    minimum_score: Optional[float] = Field(None, ge=0, le=100)
    assessment_required: bool = Field(default=True)
    practical_demonstration: bool = Field(default=False)
    active: bool = Field(default=True)

class TrainingCertificationCreate(TrainingCertificationBase):
    pass

class TrainingCertificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    issuing_organization: Optional[str] = Field(None, max_length=255)
    certification_type: Optional[str] = Field(None, max_length=100)
    required_training_programs: Optional[List[int]] = None
    required_competencies: Optional[List[int]] = None
    prerequisite_certifications: Optional[List[int]] = None
    validity_period_months: Optional[int] = Field(None, ge=1, le=120)
    renewal_required: Optional[bool] = None
    renewal_grace_period_days: Optional[int] = Field(None, ge=0, le=365)
    continuing_education_required: Optional[bool] = None
    compliance_frameworks: Optional[List[str]] = None
    regulatory_requirements: Optional[List[str]] = None
    minimum_score: Optional[float] = Field(None, ge=0, le=100)
    assessment_required: Optional[bool] = None
    practical_demonstration: Optional[bool] = None
    active: Optional[bool] = None

class TrainingCertificationResponse(TrainingCertificationBase):
    id: int
    certification_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Certification Schemas

class UserCertificationBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    status: TrainingStatusEnum
    earned_date: Optional[datetime] = None
    expires_date: Optional[datetime] = None
    certificate_number: Optional[str] = Field(None, max_length=100)
    digital_badge_url: Optional[str] = Field(None, max_length=1000)
    certificate_file_path: Optional[str] = Field(None, max_length=1000)
    final_score: Optional[float] = Field(None, ge=0, le=100)
    assessment_results: Dict[str, Any] = Field(default_factory=dict)
    renewal_due_date: Optional[datetime] = None
    renewal_reminders_sent: int = Field(default=0, ge=0)
    last_renewal_date: Optional[datetime] = None
    verified: bool = Field(default=False)
    verification_code: Optional[str] = Field(None, max_length=100)
    issued_by: Optional[str] = Field(None, max_length=255)
    compliance_period_start: Optional[datetime] = None
    compliance_period_end: Optional[datetime] = None

class UserCertificationCreate(UserCertificationBase):
    certification_id: int = Field(..., gt=0)

class UserCertificationUpdate(BaseModel):
    status: Optional[TrainingStatusEnum] = None
    earned_date: Optional[datetime] = None
    expires_date: Optional[datetime] = None
    certificate_number: Optional[str] = Field(None, max_length=100)
    digital_badge_url: Optional[str] = Field(None, max_length=1000)
    certificate_file_path: Optional[str] = Field(None, max_length=1000)
    final_score: Optional[float] = Field(None, ge=0, le=100)
    assessment_results: Optional[Dict[str, Any]] = None
    renewal_due_date: Optional[datetime] = None
    renewal_reminders_sent: Optional[int] = Field(None, ge=0)
    last_renewal_date: Optional[datetime] = None
    verified: Optional[bool] = None
    verification_code: Optional[str] = Field(None, max_length=100)
    issued_by: Optional[str] = Field(None, max_length=255)
    compliance_period_start: Optional[datetime] = None
    compliance_period_end: Optional[datetime] = None

class UserCertificationResponse(UserCertificationBase):
    id: int
    user_cert_id: str
    certification_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Training Analytics Schemas

class TrainingAnalyticsResponse(BaseModel):
    program_statistics: Dict[str, Any]
    completion_rates: Dict[str, Any]
    phishing_simulation_results: Dict[str, Any]
    competency_analysis: Dict[str, Any]
    certification_status: Dict[str, Any]
    trends_and_insights: Dict[str, Any]

class UserTrainingDashboardResponse(BaseModel):
    user_id: str
    active_training: List[Dict[str, Any]]
    completed_training: int
    recent_phishing_results: List[Dict[str, Any]]
    competency_summary: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]

# Campaign Interaction Schemas

class CampaignInteractionBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    interaction_type: str = Field(..., max_length=50)
    interaction_time: datetime
    interaction_data: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=1000)
    referrer: Optional[str] = Field(None, max_length=1000)

class CampaignInteractionCreate(CampaignInteractionBase):
    campaign_id: int = Field(..., gt=0)

class CampaignInteractionResponse(CampaignInteractionBase):
    id: int
    interaction_id: str
    campaign_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Request and Response Schemas for Complex Operations

class PhishingInteractionRequest(BaseModel):
    simulation_id: int = Field(..., gt=0)
    user_id: str = Field(..., min_length=1, max_length=255)
    interaction_type: str = Field(..., regex="^(email_opened|link_clicked|attachment_opened|data_entered|reported_phishing|deleted_email)$")
    interaction_data: Optional[Dict[str, Any]] = None

class CertificationEligibilityResponse(BaseModel):
    eligible: bool
    requirements_met: List[str]
    requirements_pending: List[str]
    training_completion: Dict[str, Any]
    competency_status: Dict[str, Any]

class TrainingProgressRequest(BaseModel):
    enrollment_id: int = Field(..., gt=0)
    progress_percentage: float = Field(..., ge=0, le=100)
    last_accessed: Optional[datetime] = None

class AssessmentSubmissionRequest(BaseModel):
    assessment_id: int = Field(..., gt=0)
    user_id: str = Field(..., min_length=1, max_length=255)
    user_email: EmailStr
    answers: Dict[str, Any] = Field(..., min_items=1)

# Filter and Search Schemas

class TrainingProgramFilter(BaseModel):
    program_type: Optional[TrainingTypeEnum] = None
    priority: Optional[TrainingPriorityEnum] = None
    mandatory: Optional[bool] = None
    active: Optional[bool] = None
    target_role: Optional[str] = None
    target_department: Optional[str] = None
    compliance_framework: Optional[str] = None

class TrainingEnrollmentFilter(BaseModel):
    status: Optional[TrainingStatusEnum] = None
    user_role: Optional[str] = None
    department: Optional[str] = None
    overdue: Optional[bool] = None
    completed_after: Optional[datetime] = None
    completed_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None

class CampaignFilter(BaseModel):
    status: Optional[CampaignStatusEnum] = None
    campaign_type: Optional[str] = None
    target_department: Optional[str] = None
    scheduled_after: Optional[datetime] = None
    scheduled_before: Optional[datetime] = None
    created_by: Optional[str] = None

class SimulationResultFilter(BaseModel):
    result: Optional[SimulationResultEnum] = None
    user_role: Optional[str] = None
    department: Optional[str] = None
    difficulty_level: Optional[CompetencyLevelEnum] = None
    interaction_after: Optional[datetime] = None
    interaction_before: Optional[datetime] = None
    training_assigned: Optional[bool] = None