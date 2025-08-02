from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class TaskStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(enum.Enum):
    REMEDIATION = "remediation"
    MITIGATION = "mitigation"
    ASSESSMENT = "assessment"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    COMPLIANCE = "compliance"
    OTHER = "other"


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Task classification
    task_type = Column(Enum(TaskType), default=TaskType.REMEDIATION)
    category = Column(String(100))
    subcategory = Column(String(100))
    
    # Task details
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN)
    
    # Relationships
    risk_id = Column(Integer, ForeignKey("risks.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timeline
    start_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    completed_date = Column(DateTime(timezone=True))
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    milestone_description = Column(Text)
    
    # AI-generated content
    ai_generated_plan = Column(Text)
    ai_suggested_actions = Column(Text)
    ai_confidence_score = Column(Integer)  # 0-100
    ai_last_updated = Column(DateTime(timezone=True))
    
    # Review and approval
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(50))  # pending, approved, rejected
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    approval_comments = Column(Text)
    
    # Cost and effort
    estimated_cost = Column(String(50))
    actual_cost = Column(String(50))
    cost_center = Column(String(50))
    
    # Dependencies
    depends_on_tasks = Column(Text)  # JSON array of task IDs
    blocks_tasks = Column(Text)  # JSON array of task IDs
    
    # Metadata
    tags = Column(Text)  # JSON array
    custom_fields = Column(Text)  # JSON object
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    risk = relationship("Risk", back_populates="tasks")
    asset = relationship("Asset")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    comments = relationship("TaskComment", back_populates="task")
    evidence = relationship("TaskEvidence", back_populates="task")


class TaskComment(Base):
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    comment = Column(Text, nullable=False)
    comment_type = Column(String(50), default="general")  # general, status_update, approval, rejection
    
    # Metadata
    is_internal = Column(Boolean, default=False)
    is_system_generated = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User")


class TaskEvidence(Base):
    __tablename__ = "task_evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    
    relationship_type = Column(String(50), default="supporting")  # supporting, deliverable, reference
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="evidence")
    evidence_item = relationship("Evidence")