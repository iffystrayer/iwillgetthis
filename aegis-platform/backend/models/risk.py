from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class RiskCategory(enum.Enum):
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"


class RiskStatus(enum.Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class RiskMatrix(Base):
    __tablename__ = "risk_matrices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Matrix configuration (JSON)
    likelihood_levels = Column(Text)  # JSON array of likelihood levels
    impact_levels = Column(Text)  # JSON array of impact levels
    risk_scores = Column(Text)  # JSON matrix of risk scores
    risk_levels = Column(Text)  # JSON mapping of scores to levels (low, medium, high, critical)
    
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    risks = relationship("Risk", back_populates="risk_matrix")


class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Risk classification
    category = Column(Enum(RiskCategory), nullable=False)
    subcategory = Column(String(100))
    risk_type = Column(String(100))  # vulnerability, threat, compliance_gap, etc.
    
    # Risk source
    source = Column(String(100))  # assessment, vulnerability_scan, threat_intel, manual
    source_reference = Column(String(255))  # Reference to source (assessment ID, CVE, etc.)
    
    # Asset and scope
    asset_id = Column(Integer, ForeignKey("assets.id"))
    affected_systems = Column(Text)  # JSON array of affected systems
    business_process = Column(String(255))
    
    # Risk scoring
    risk_matrix_id = Column(Integer, ForeignKey("risk_matrices.id"))
    inherent_likelihood = Column(Integer)  # 1-5 scale
    inherent_impact = Column(Integer)  # 1-5 scale
    inherent_risk_score = Column(Float)
    residual_likelihood = Column(Integer)
    residual_impact = Column(Integer)
    residual_risk_score = Column(Float)
    risk_level = Column(String(20))  # low, medium, high, critical
    
    # Risk details
    threat_source = Column(String(255))
    vulnerability = Column(Text)
    existing_controls = Column(Text)
    control_effectiveness = Column(String(50))  # ineffective, limited, moderate, strong
    
    # AI-generated content
    ai_generated_statement = Column(Text)
    ai_risk_assessment = Column(Text)
    ai_confidence_score = Column(Integer)  # 0-100
    ai_last_updated = Column(DateTime(timezone=True))
    
    # Risk treatment
    treatment_strategy = Column(String(50))  # accept, mitigate, transfer, avoid
    treatment_rationale = Column(Text)
    
    # Status and ownership
    status = Column(Enum(RiskStatus), default=RiskStatus.IDENTIFIED)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Timeline
    identified_date = Column(DateTime(timezone=True), server_default=func.now())
    target_resolution_date = Column(DateTime(timezone=True))
    actual_resolution_date = Column(DateTime(timezone=True))
    last_review_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    
    # Metadata
    tags = Column(Text)  # JSON array
    custom_fields = Column(Text)  # JSON object
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    risk_matrix = relationship("RiskMatrix", back_populates="risks")
    asset = relationship("Asset", back_populates="risks")
    owner = relationship("User", foreign_keys=[owner_id])
    creator = relationship("User", foreign_keys=[created_by])
    tasks = relationship("Task", back_populates="risk")
    risk_scores = relationship("RiskScore", back_populates="risk")


class RiskScore(Base):
    __tablename__ = "risk_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False)
    
    # Scoring details
    likelihood_score = Column(Integer)
    impact_score = Column(Integer)
    total_score = Column(Float)
    risk_level = Column(String(20))
    score_type = Column(String(20))  # inherent, residual
    
    # Scoring rationale
    likelihood_rationale = Column(Text)
    impact_rationale = Column(Text)
    scoring_methodology = Column(String(100))
    
    # Metadata
    scored_by = Column(Integer, ForeignKey("users.id"))
    scored_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    risk = relationship("Risk", back_populates="risk_scores")
    scorer = relationship("User", foreign_keys=[scored_by])