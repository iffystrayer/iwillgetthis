from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class EvidenceType(enum.Enum):
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    CONFIGURATION = "configuration"
    POLICY = "policy"
    PROCEDURE = "procedure"
    CERTIFICATE = "certificate"
    SCAN_RESULT = "scan_result"
    REPORT = "report"
    OTHER = "other"


class EvidenceStatus(enum.Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # File details
    file_name = Column(String(255))
    file_path = Column(String(1000))
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(100))  # MIME type
    file_hash = Column(String(64))  # SHA-256 hash
    
    # Evidence classification
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    
    # Content analysis
    content_summary = Column(Text)
    ai_analysis = Column(Text)  # AI-generated analysis
    ai_confidence_score = Column(Integer)  # 0-100
    ai_last_analyzed = Column(DateTime(timezone=True))
    
    # Version control
    version = Column(String(20), default="1.0")
    previous_version_id = Column(Integer, ForeignKey("evidence.id"))
    is_current_version = Column(Boolean, default=True)
    
    # Status and lifecycle
    status = Column(Enum(EvidenceStatus), default=EvidenceStatus.DRAFT)
    
    # Ownership and access
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    access_level = Column(String(50), default="private")  # private, team, organization, public
    
    # Validity and compliance
    effective_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    review_date = Column(DateTime(timezone=True))
    compliance_scope = Column(Text)  # JSON array of applicable frameworks
    
    # Review and approval
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    review_comments = Column(Text)
    
    # Metadata
    tags = Column(Text)  # JSON array
    custom_fields = Column(Text)  # JSON object
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    owner = relationship("User", foreign_keys=[owner_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    previous_version = relationship("Evidence", remote_side=[id])
    evidence_controls = relationship("EvidenceControl", back_populates="evidence")


class EvidenceControl(Base):
    __tablename__ = "evidence_controls"
    
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=False)
    
    relationship_type = Column(String(50), default="supporting")  # supporting, implementing, testing
    relevance_score = Column(Integer)  # 0-100
    description = Column(Text)
    
    # AI analysis
    ai_relevance_analysis = Column(Text)
    ai_confidence_score = Column(Integer)  # 0-100
    ai_last_analyzed = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    evidence = relationship("Evidence", back_populates="evidence_controls")
    control = relationship("Control", back_populates="evidence_controls")
    creator = relationship("User", foreign_keys=[created_by])