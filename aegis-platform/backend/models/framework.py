from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Framework(Base):
    __tablename__ = "frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50))
    description = Column(Text)
    source_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    controls = relationship("Control", back_populates="framework")
    assessments = relationship("Assessment", back_populates="framework")


class Control(Base):
    __tablename__ = "controls"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id"), nullable=False)
    control_id = Column(String(50), nullable=False)  # e.g., "AC-1", "CIS-1.1"
    title = Column(String(500), nullable=False)
    description = Column(Text)
    guidance = Column(Text)
    
    # Hierarchical structure
    parent_id = Column(Integer, ForeignKey("controls.id"))
    level = Column(Integer, default=1)  # 1 = top level, 2 = sub-control, etc.
    sort_order = Column(Float, default=0)
    
    # Control properties
    control_type = Column(String(50))  # preventive, detective, corrective
    implementation_status = Column(String(50))  # manual, automated, hybrid
    testing_frequency = Column(String(50))  # annual, semi-annual, quarterly, monthly
    
    # Risk and compliance
    risk_level = Column(String(20))  # low, medium, high, critical
    compliance_references = Column(Text)  # JSON array of compliance mappings
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    framework = relationship("Framework", back_populates="controls")
    parent = relationship("Control", remote_side=[id])
    children = relationship("Control")
    assessment_controls = relationship("AssessmentControl", back_populates="control")
    control_mappings = relationship("ControlMapping", back_populates="control")
    evidence_controls = relationship("EvidenceControl", back_populates="control")


class ControlMapping(Base):
    __tablename__ = "control_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(Integer, ForeignKey("controls.id"), nullable=False)
    mapped_framework = Column(String(100))  # Target framework name
    mapped_control_id = Column(String(50))  # Target control ID
    mapping_type = Column(String(50))  # equivalent, related, derived
    confidence_level = Column(String(20))  # high, medium, low
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    control = relationship("Control", back_populates="control_mappings")