from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class WorkflowType(enum.Enum):
    RISK_APPROVAL = "risk_approval"
    TASK_APPROVAL = "task_approval"
    ASSESSMENT_APPROVAL = "assessment_approval"
    EVIDENCE_APPROVAL = "evidence_approval"
    USER_ACCESS_REQUEST = "user_access_request"
    BUDGET_APPROVAL = "budget_approval"
    EXCEPTION_REQUEST = "exception_request"
    CUSTOM = "custom"


class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class WorkflowStepType(enum.Enum):
    APPROVAL = "approval"
    REVIEW = "review"
    NOTIFICATION = "notification"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    AUTOMATED = "automated"


class WorkflowInstanceStatus(enum.Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ERROR = "error"


class WorkflowStepStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    REJECTED = "rejected"
    ERROR = "error"


class ActionType(enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    COMMENT = "comment"
    REASSIGN = "reassign"
    ESCALATE = "escalate"
    REQUEST_INFORMATION = "request_information"
    CANCEL = "cancel"


class Workflow(Base):
    """
    Defines reusable workflow templates for various approval processes
    """
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Workflow classification
    workflow_type = Column(Enum(WorkflowType), nullable=False)
    category = Column(String(100))  # e.g., "risk_management", "compliance", "security"
    
    # Workflow configuration
    version = Column(String(20), default="1.0")
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    is_default = Column(Boolean, default=False)
    
    # Trigger conditions
    trigger_conditions = Column(Text)  # JSON object defining when workflow is triggered
    auto_trigger = Column(Boolean, default=False)
    
    # Escalation and timeout settings
    default_timeout_hours = Column(Integer, default=72)  # Default step timeout
    escalation_enabled = Column(Boolean, default=True)
    escalation_timeout_hours = Column(Integer, default=24)
    
    # Notification settings
    notification_template_id = Column(Integer, ForeignKey("notification_templates.id"))
    notify_on_start = Column(Boolean, default=True)
    notify_on_completion = Column(Boolean, default=True)
    
    # Metadata
    tags = Column(Text)  # JSON array
    custom_fields = Column(Text)  # JSON object for additional configuration
    
    # Audit fields
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    notification_template = relationship("NotificationTemplate", foreign_keys=[notification_template_id])
    steps = relationship("WorkflowStep", back_populates="workflow", order_by="WorkflowStep.step_order")
    instances = relationship("WorkflowInstance", back_populates="workflow")


class WorkflowStep(Base):
    """
    Defines individual steps within a workflow template
    """
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    
    # Step configuration
    name = Column(String(255), nullable=False)
    description = Column(Text)
    step_type = Column(Enum(WorkflowStepType), nullable=False)
    step_order = Column(Integer, nullable=False)
    
    # Step behavior
    is_required = Column(Boolean, default=True)
    can_skip = Column(Boolean, default=False)
    allow_parallel = Column(Boolean, default=False)
    
    # Assignee configuration
    assignee_type = Column(String(50))  # "user", "role", "group", "auto"
    assignee_id = Column(Integer)  # Can reference users, roles, or groups
    auto_assign_rule = Column(Text)  # JSON rules for automatic assignment
    
    # Approval requirements
    approval_required = Column(Boolean, default=True)
    min_approvals = Column(Integer, default=1)
    unanimous_required = Column(Boolean, default=False)
    
    # Timing and escalation
    timeout_hours = Column(Integer)  # Override workflow default
    reminder_hours = Column(Integer, default=24)  # Send reminder after X hours
    escalation_assignee_id = Column(Integer, ForeignKey("users.id"))
    
    # Conditional logic
    condition_expression = Column(Text)  # JSON expression for conditional steps
    
    # Actions and outcomes
    allowed_actions = Column(Text)  # JSON array of allowed ActionType values
    on_approve_action = Column(Text)  # JSON action configuration
    on_reject_action = Column(Text)  # JSON action configuration
    
    # Metadata
    custom_fields = Column(Text)  # JSON object
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    escalation_assignee = relationship("User", foreign_keys=[escalation_assignee_id])
    step_instances = relationship("WorkflowStepInstance", back_populates="workflow_step")


class WorkflowInstance(Base):
    """
    Represents an active instance of a workflow for a specific entity
    """
    __tablename__ = "workflow_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    
    # Instance identification
    name = Column(String(255))
    description = Column(Text)
    
    # Entity being processed
    entity_type = Column(String(50), nullable=False)  # "risk", "task", "assessment", etc.
    entity_id = Column(Integer, nullable=False)
    
    # Instance status
    status = Column(Enum(WorkflowInstanceStatus), default=WorkflowInstanceStatus.INITIATED)
    current_step_id = Column(Integer, ForeignKey("workflow_steps.id"))
    
    # Workflow context
    context_data = Column(Text)  # JSON object with workflow-specific data
    
    # Participants
    initiated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_assignee_id = Column(Integer, ForeignKey("users.id"))
    
    # Timeline
    initiated_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    
    # Results
    final_outcome = Column(String(50))  # "approved", "rejected", "cancelled"
    outcome_reason = Column(Text)
    
    # Priority and escalation
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    escalation_level = Column(Integer, default=0)
    last_escalated_at = Column(DateTime(timezone=True))
    
    # Metadata
    tags = Column(Text)  # JSON array
    custom_fields = Column(Text)  # JSON object
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="instances")
    current_step = relationship("WorkflowStep", foreign_keys=[current_step_id])
    initiated_by = relationship("User", foreign_keys=[initiated_by_id])
    current_assignee = relationship("User", foreign_keys=[current_assignee_id])
    step_instances = relationship("WorkflowStepInstance", back_populates="workflow_instance")
    actions = relationship("WorkflowAction", back_populates="workflow_instance")


class WorkflowStepInstance(Base):
    """
    Represents the execution of a specific workflow step within an instance
    """
    __tablename__ = "workflow_step_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=False)
    
    # Step execution details
    status = Column(Enum(WorkflowStepStatus), default=WorkflowStepStatus.PENDING)
    step_order = Column(Integer, nullable=False)
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True))
    
    # Timeline
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    
    # Results
    outcome = Column(String(50))  # "approved", "rejected", "completed", "skipped"
    outcome_reason = Column(Text)
    
    # Escalation tracking
    reminder_sent_at = Column(DateTime(timezone=True))
    escalated_at = Column(DateTime(timezone=True))
    escalated_to_id = Column(Integer, ForeignKey("users.id"))
    
    # Step context
    step_data = Column(Text)  # JSON object with step-specific data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="step_instances")
    workflow_step = relationship("WorkflowStep", back_populates="step_instances")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    escalated_to = relationship("User", foreign_keys=[escalated_to_id])
    actions = relationship("WorkflowAction", back_populates="step_instance")


class WorkflowAction(Base):
    """
    Records all actions taken during workflow execution
    """
    __tablename__ = "workflow_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    step_instance_id = Column(Integer, ForeignKey("workflow_step_instances.id"))
    
    # Action details
    action_type = Column(Enum(ActionType), nullable=False)
    action_description = Column(Text)
    
    # Actor information
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    on_behalf_of_id = Column(Integer, ForeignKey("users.id"))  # For delegation
    
    # Action context
    comment = Column(Text)
    attachments = Column(Text)  # JSON array of file references
    
    # Action results
    result_status = Column(String(50))  # "success", "failure", "pending"
    result_data = Column(Text)  # JSON object with action results
    
    # Timeline
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="actions")
    step_instance = relationship("WorkflowStepInstance", back_populates="actions")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
    on_behalf_of = relationship("User", foreign_keys=[on_behalf_of_id])


class WorkflowTemplate(Base):
    """
    Pre-defined workflow templates for common approval processes
    """
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Template classification
    category = Column(String(100))
    workflow_type = Column(Enum(WorkflowType))
    
    # Template definition
    template_data = Column(Text, nullable=False)  # JSON representation of complete workflow
    
    # Template metadata
    version = Column(String(20), default="1.0")
    is_system_template = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    
    # Template settings
    tags = Column(Text)  # JSON array
    
    # Audit
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])


class WorkflowRole(Base):
    """
    Defines roles that can be assigned to workflow steps
    """
    __tablename__ = "workflow_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Role configuration
    is_system_role = Column(Boolean, default=False)
    permissions = Column(Text)  # JSON array of permissions
    
    # Role members
    members = Column(Text)  # JSON array of user IDs
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())