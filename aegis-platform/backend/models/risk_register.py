"""
Risk Register Data Models
Comprehensive risk management system with assessment, treatment, and tracking capabilities
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime


class RiskCategory(enum.Enum):
    """Risk categories for classification"""
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    TECHNOLOGY = "technology"
    REPUTATIONAL = "reputational"
    ENVIRONMENTAL = "environmental"
    SECURITY = "security"
    LEGAL = "legal"
    SUPPLIER = "supplier"


class RiskStatus(enum.Enum):
    """Risk lifecycle status"""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    TREATING = "treating"
    MONITORING = "monitoring"
    CLOSED = "closed"
    ESCALATED = "escalated"


class RiskLikelihood(enum.Enum):
    """Risk likelihood levels"""
    VERY_LOW = "very_low"      # 1-5%
    LOW = "low"                # 6-25%
    MEDIUM = "medium"          # 26-50%
    HIGH = "high"              # 51-75%
    VERY_HIGH = "very_high"    # 76-95%
    CERTAIN = "certain"        # 96-100%


class RiskImpact(enum.Enum):
    """Risk impact levels"""
    NEGLIGIBLE = "negligible"  # Minimal impact
    MINOR = "minor"            # Small impact, easily manageable
    MODERATE = "moderate"      # Noticeable impact, requires attention
    MAJOR = "major"            # Significant impact, serious concern
    SEVERE = "severe"          # Extreme impact, critical concern


class RiskPriority(enum.Enum):
    """Risk priority levels (derived from likelihood x impact)"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TreatmentStrategy(enum.Enum):
    """Risk treatment strategies"""
    AVOID = "avoid"            # Eliminate the risk
    MITIGATE = "mitigate"      # Reduce likelihood or impact
    TRANSFER = "transfer"      # Share or transfer risk (insurance, outsourcing)
    ACCEPT = "accept"          # Accept risk with monitoring
    EXPLOIT = "exploit"        # For positive risks/opportunities


class TreatmentStatus(enum.Enum):
    """Treatment implementation status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class RiskRegister(Base):
    """Main risk register entry"""
    __tablename__ = "risk_register"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String(20), unique=True, nullable=False, index=True)  # RISK-2024-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    category = Column(Enum(RiskCategory), nullable=False)
    subcategory = Column(String(100))
    tags = Column(JSON)  # Array of custom tags
    
    # Risk Assessment
    inherent_likelihood = Column(Enum(RiskLikelihood), nullable=False)
    inherent_impact = Column(Enum(RiskImpact), nullable=False)
    inherent_score = Column(Float)  # Calculated likelihood x impact
    inherent_priority = Column(Enum(RiskPriority))
    
    residual_likelihood = Column(Enum(RiskLikelihood))
    residual_impact = Column(Enum(RiskImpact))
    residual_score = Column(Float)
    residual_priority = Column(Enum(RiskPriority))
    
    # Business Context
    business_unit = Column(String(100))
    process_area = Column(String(100))
    geographic_scope = Column(String(100))
    
    # Financial Impact
    potential_financial_impact_min = Column(Float)  # Minimum financial impact
    potential_financial_impact_max = Column(Float)  # Maximum financial impact
    currency = Column(String(3), default="USD")
    
    # Timeline
    risk_horizon = Column(String(50))  # Short-term, Medium-term, Long-term
    first_identified_date = Column(DateTime(timezone=True), nullable=False)
    last_review_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    
    # Ownership and Responsibility
    risk_owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_manager_id = Column(Integer, ForeignKey("users.id"))
    escalation_contact_id = Column(Integer, ForeignKey("users.id"))
    
    # Status and Lifecycle
    status = Column(Enum(RiskStatus), default=RiskStatus.IDENTIFIED)
    is_active = Column(Boolean, default=True)
    
    # Regulatory and Compliance
    regulatory_requirements = Column(JSON)  # Array of applicable regulations
    compliance_impact = Column(Text)
    
    # External Factors
    external_dependencies = Column(JSON)  # Array of external dependencies
    market_conditions_impact = Column(Text)
    
    # Custom Fields
    custom_fields = Column(JSON)  # Flexible custom data
    
    # Audit Trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    risk_owner = relationship("User", foreign_keys=[risk_owner_id])
    risk_manager = relationship("User", foreign_keys=[risk_manager_id])
    escalation_contact = relationship("User", foreign_keys=[escalation_contact_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    treatments = relationship("RiskTreatment", back_populates="risk", cascade="all, delete-orphan")
    assessments = relationship("RiskAssessment", back_populates="risk", cascade="all, delete-orphan")
    incidents = relationship("RiskIncident", back_populates="risk", cascade="all, delete-orphan")
    controls = relationship("RiskControl", back_populates="risk", cascade="all, delete-orphan")
    reviews = relationship("RiskReview", back_populates="risk", cascade="all, delete-orphan")
    
    # Asset relationships
    affected_assets = relationship("Asset", secondary="risk_asset_mapping", back_populates="risks")


class RiskTreatment(Base):
    """Risk treatment plans and actions"""
    __tablename__ = "risk_treatments"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    treatment_id = Column(String(20), unique=True, nullable=False)  # TREAT-2024-001
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    strategy = Column(Enum(TreatmentStrategy), nullable=False)
    
    # Implementation Details
    action_plan = Column(Text)
    success_criteria = Column(Text)
    resource_requirements = Column(Text)
    
    # Timeline
    planned_start_date = Column(DateTime(timezone=True))
    planned_completion_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Financial
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    currency = Column(String(3), default="USD")
    budget_approval_required = Column(Boolean, default=False)
    budget_approved = Column(Boolean, default=False)
    
    # Ownership
    treatment_owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_team = Column(JSON)  # Array of team member IDs
    
    # Status and Progress
    status = Column(Enum(TreatmentStatus), default=TreatmentStatus.PLANNED)
    progress_percentage = Column(Integer, default=0)
    
    # Effectiveness
    expected_likelihood_reduction = Column(Float)  # Expected reduction in likelihood (0.0-1.0)
    expected_impact_reduction = Column(Float)      # Expected reduction in impact (0.0-1.0)
    actual_likelihood_reduction = Column(Float)    # Measured reduction
    actual_impact_reduction = Column(Float)        # Measured reduction
    
    # Dependencies and Constraints
    dependencies = Column(JSON)  # Array of dependent treatments/tasks
    constraints = Column(Text)
    
    # Monitoring
    monitoring_plan = Column(Text)
    kpis = Column(JSON)  # Key Performance Indicators
    
    # Audit Trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    risk = relationship("RiskRegister", back_populates="treatments")
    treatment_owner = relationship("User", foreign_keys=[treatment_owner_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    milestones = relationship("TreatmentMilestone", back_populates="treatment", cascade="all, delete-orphan")
    updates = relationship("TreatmentUpdate", back_populates="treatment", cascade="all, delete-orphan")


class TreatmentMilestone(Base):
    """Treatment implementation milestones"""
    __tablename__ = "treatment_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    treatment_id = Column(Integer, ForeignKey("risk_treatments.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_date = Column(DateTime(timezone=True), nullable=False)
    actual_date = Column(DateTime(timezone=True))
    
    is_completed = Column(Boolean, default=False)
    completion_notes = Column(Text)
    
    # Dependencies
    depends_on_milestone_ids = Column(JSON)  # Array of prerequisite milestone IDs
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    treatment = relationship("RiskTreatment", back_populates="milestones")


class TreatmentUpdate(Base):
    """Treatment progress updates and notes"""
    __tablename__ = "treatment_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    treatment_id = Column(Integer, ForeignKey("risk_treatments.id"), nullable=False)
    
    update_type = Column(String(50))  # progress, issue, milestone, completion, etc.
    title = Column(String(255))
    description = Column(Text, nullable=False)
    
    progress_percentage = Column(Integer)
    issues_identified = Column(Text)
    actions_taken = Column(Text)
    next_steps = Column(Text)
    
    # Attachments and Evidence
    attachments = Column(JSON)  # Array of file references
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    treatment = relationship("RiskTreatment", back_populates="updates")
    creator = relationship("User")


class RiskAssessment(Base):
    """Risk assessment records and methodology"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    assessment_id = Column(String(20), unique=True, nullable=False)  # ASSESS-2024-001
    
    assessment_type = Column(String(50), nullable=False)  # initial, periodic, triggered, ad_hoc
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Assessment Methodology
    methodology_used = Column(String(100))  # NIST, ISO 31000, COSO, etc.
    assessment_criteria = Column(Text)
    data_sources = Column(JSON)  # Array of data sources used
    
    # Likelihood Assessment
    likelihood_rating = Column(Enum(RiskLikelihood), nullable=False)
    likelihood_rationale = Column(Text)
    likelihood_confidence = Column(String(20))  # high, medium, low
    
    # Impact Assessment
    impact_rating = Column(Enum(RiskImpact), nullable=False)
    impact_rationale = Column(Text)
    impact_confidence = Column(String(20))
    
    # Impact Categories
    financial_impact = Column(Float)
    operational_impact = Column(String(20))    # high, medium, low
    reputational_impact = Column(String(20))
    compliance_impact = Column(String(20))
    strategic_impact = Column(String(20))
    
    # Overall Assessment
    overall_score = Column(Float)
    priority_rating = Column(Enum(RiskPriority))
    
    # Validation and Review
    is_validated = Column(Boolean, default=False)
    validated_by_id = Column(Integer, ForeignKey("users.id"))
    validation_date = Column(DateTime(timezone=True))
    validation_notes = Column(Text)
    
    # Assessment Quality
    assessment_quality_score = Column(Float)  # 0.0-1.0
    quality_comments = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    risk = relationship("RiskRegister", back_populates="assessments")
    assessor = relationship("User", foreign_keys=[assessor_id])
    validator = relationship("User", foreign_keys=[validated_by_id])


class RiskControl(Base):
    """Risk controls and safeguards"""
    __tablename__ = "risk_controls"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    control_id = Column(String(20), unique=True, nullable=False)  # CTRL-2024-001
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    control_type = Column(String(50), nullable=False)  # preventive, detective, corrective, compensating
    
    # Control Implementation
    implementation_status = Column(String(50))  # planned, implemented, tested, operational
    control_owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Effectiveness
    design_effectiveness = Column(String(20))    # effective, partially_effective, ineffective
    operational_effectiveness = Column(String(20))
    last_testing_date = Column(DateTime(timezone=True))
    next_testing_date = Column(DateTime(timezone=True))
    
    # Automation and Frequency
    is_automated = Column(Boolean, default=False)
    frequency = Column(String(50))  # continuous, daily, weekly, monthly, quarterly, annually
    
    # Cost and Resources
    implementation_cost = Column(Float)
    ongoing_cost = Column(Float)
    resource_requirements = Column(Text)
    
    # Monitoring
    monitoring_procedures = Column(Text)
    performance_metrics = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    risk = relationship("RiskRegister", back_populates="controls")
    control_owner = relationship("User", foreign_keys=[control_owner_id])
    creator = relationship("User", foreign_keys=[created_by])


class RiskIncident(Base):
    """Risk materialization incidents"""
    __tablename__ = "risk_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    incident_id = Column(String(20), unique=True, nullable=False)  # INC-2024-001
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Incident Details
    incident_date = Column(DateTime(timezone=True), nullable=False)
    discovery_date = Column(DateTime(timezone=True), nullable=False)
    reported_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Impact Assessment
    actual_financial_impact = Column(Float)
    actual_operational_impact = Column(Text)
    actual_reputational_impact = Column(Text)
    
    # Root Cause
    root_cause_analysis = Column(Text)
    contributing_factors = Column(JSON)
    
    # Response
    immediate_actions_taken = Column(Text)
    incident_response_team = Column(JSON)  # Array of team member IDs
    
    # Resolution
    resolution_date = Column(DateTime(timezone=True))
    final_resolution = Column(Text)
    lessons_learned = Column(Text)
    
    # Follow-up Actions
    corrective_actions = Column(JSON)  # Array of actions to be taken
    preventive_measures = Column(JSON)  # Array of preventive measures
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    risk = relationship("RiskRegister", back_populates="incidents")
    reporter = relationship("User")


class RiskReview(Base):
    """Periodic risk reviews and updates"""
    __tablename__ = "risk_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    review_id = Column(String(20), unique=True, nullable=False)  # REV-2024-001
    
    review_type = Column(String(50), nullable=False)  # scheduled, triggered, annual, quarterly
    review_date = Column(DateTime(timezone=True), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Review Findings
    risk_level_change = Column(String(50))  # increased, decreased, unchanged
    previous_likelihood = Column(Enum(RiskLikelihood))
    previous_impact = Column(Enum(RiskImpact))
    current_likelihood = Column(Enum(RiskLikelihood))
    current_impact = Column(Enum(RiskImpact))
    
    # Treatment Effectiveness
    treatment_effectiveness_assessment = Column(Text)
    control_effectiveness_assessment = Column(Text)
    
    # Environmental Changes
    internal_changes = Column(Text)  # Changes within organization
    external_changes = Column(Text)  # Changes in external environment
    regulatory_changes = Column(Text)
    
    # Recommendations
    recommendations = Column(Text)
    action_items = Column(JSON)  # Array of action items with owners and dates
    
    # Next Review
    next_review_date = Column(DateTime(timezone=True))
    next_review_type = Column(String(50))
    
    # Review Quality
    review_completeness_score = Column(Float)  # 0.0-1.0
    quality_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    risk = relationship("RiskRegister", back_populates="reviews")
    reviewer = relationship("User")


# Junction table for risk-asset relationships
class RiskAssetMapping(Base):
    """Many-to-many relationship between risks and assets"""
    __tablename__ = "risk_asset_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risk_register.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    impact_type = Column(String(50))  # affects, depends_on, hosted_on, etc.
    impact_level = Column(String(20))  # high, medium, low
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))


class RiskRegisterMatrix(Base):
    """Risk register matrix configuration for advanced scoring"""
    __tablename__ = "risk_register_matrices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Matrix Configuration
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Likelihood Scale
    likelihood_scale = Column(JSON, nullable=False)  # Array of likelihood definitions
    
    # Impact Scale
    impact_scale = Column(JSON, nullable=False)      # Array of impact definitions
    
    # Risk Scores Matrix
    risk_scores = Column(JSON, nullable=False)       # 2D array of risk scores
    
    # Priority Thresholds
    priority_thresholds = Column(JSON, nullable=False)  # Thresholds for each priority level
    
    # Applicable Scope
    applicable_categories = Column(JSON)  # Array of risk categories this matrix applies to
    business_units = Column(JSON)         # Array of business units
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User")