from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class AssessmentStatus(enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ControlImplementationStatus(enum.Enum):
    IMPLEMENTED = "implemented"
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    NOT_APPLICABLE = "not_applicable"
    PLANNED = "planned"


class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Assessment scope
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    scope_description = Column(Text)
    
    # Assessment details
    assessment_type = Column(String(50), default="control_assessment")  # control_assessment, risk_assessment, compliance_audit
    methodology = Column(String(100))  # self_assessment, independent_review, third_party
    
    # Status and timeline
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.DRAFT)
    start_date = Column(DateTime(timezone=True))
    target_completion_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Assessment team
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_assessor_id = Column(Integer, ForeignKey("users.id"))
    
    # Results and scoring
    overall_score = Column(Integer)  # 0-100
    maturity_level = Column(String(20))  # initial, developing, defined, managed, optimizing
    
    # Metadata
    tags = Column(Text)  # JSON array
    custom_fields = Column(Text)  # JSON object
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    framework = relationship("Framework", back_populates="assessments")
    asset = relationship("Asset", back_populates="assessments")
    created_by_user = relationship("User", foreign_keys=[created_by_id], back_populates="created_assessments")
    lead_assessor = relationship("User", foreign_keys=[lead_assessor_id])
    assessment_controls = relationship("AssessmentControl", back_populates="assessment")


class AssessmentControl(Base):
    __tablename__ = "assessment_controls"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=False)
    
    # Control assessment results
    implementation_status = Column(Enum(ControlImplementationStatus), nullable=False)
    implementation_score = Column(Integer)  # 0-100
    effectiveness_rating = Column(String(20))  # ineffective, needs_improvement, adequate, effective
    
    # Evidence and documentation
    control_narrative = Column(Text)
    testing_procedures = Column(Text)
    evidence_summary = Column(Text)
    
    # AI-generated content
    ai_generated_narrative = Column(Text)
    ai_confidence_score = Column(Integer)  # 0-100
    ai_last_updated = Column(DateTime(timezone=True))
    
    # Assessment details
    assessor_notes = Column(Text)
    testing_date = Column(DateTime(timezone=True))
    next_testing_date = Column(DateTime(timezone=True))
    
    # Review and approval
    review_status = Column(String(50), default="pending")  # pending, under_review, approved, rejected
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    review_comments = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="assessment_controls")
    control = relationship("Control", back_populates="assessment_controls")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])