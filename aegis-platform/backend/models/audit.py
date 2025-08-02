from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # create, update, delete, login, logout, etc.
    entity_type = Column(String(100))  # user, risk, task, assessment, etc.
    entity_id = Column(Integer)  # ID of the affected entity
    
    # User and session
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(255))
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(1000))
    
    # Event description
    action = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Changes tracking
    old_values = Column(JSON)  # Previous state (for updates)
    new_values = Column(JSON)  # New state (for creates/updates)
    
    # Additional context
    source = Column(String(100))  # web_ui, api, system, integration
    correlation_id = Column(String(255))  # For grouping related events
    
    # Risk and compliance
    risk_level = Column(String(20))  # low, medium, high, critical
    compliance_relevant = Column(Boolean, default=False)
    
    # Metadata
    additional_data = Column(JSON)  # Flexible field for extra context
    
    # Immutable timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")