from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ReportType(enum.Enum):
    RISK_REGISTER = "risk_register"
    ASSESSMENT_SUMMARY = "assessment_summary"
    COMPLIANCE_STATUS = "compliance_status"
    EXECUTIVE_SUMMARY = "executive_summary"
    VULNERABILITY_REPORT = "vulnerability_report"
    TASK_STATUS = "task_status"
    CUSTOM = "custom"


class ReportFormat(enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"


class ReportStatus(enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class ReportTemplate(Base):
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Template details
    report_type = Column(Enum(ReportType), nullable=False)
    template_data = Column(JSON)  # Template configuration
    
    # Design and layout
    layout_config = Column(JSON)  # Layout configuration
    style_config = Column(JSON)  # Styling configuration
    
    # Filters and parameters
    default_filters = Column(JSON)  # Default filter values
    parameter_schema = Column(JSON)  # Parameter definitions
    
    # Access and usage
    is_public = Column(Boolean, default=False)
    is_system_template = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    reports = relationship("Report", back_populates="template")


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Report details
    report_type = Column(Enum(ReportType), nullable=False)
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    
    # Generation details
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT)
    format = Column(Enum(ReportFormat), default=ReportFormat.PDF)
    
    # Parameters and filters
    parameters = Column(JSON)  # Report parameters
    filters = Column(JSON)  # Applied filters
    
    # File details
    file_name = Column(String(255))
    file_path = Column(String(1000))
    file_size = Column(Integer)  # in bytes
    
    # AI-generated content
    ai_summary = Column(Text)  # AI-generated executive summary
    ai_insights = Column(JSON)  # AI-generated insights
    ai_confidence_score = Column(Integer)  # 0-100
    
    # Scheduling
    is_scheduled = Column(Boolean, default=False)
    schedule_config = Column(JSON)  # Cron-like schedule configuration
    next_generation = Column(DateTime(timezone=True))
    
    # Distribution
    recipients = Column(JSON)  # Email recipients
    distribution_list = Column(String(500))
    
    # Generation metadata
    generation_started = Column(DateTime(timezone=True))
    generation_completed = Column(DateTime(timezone=True))
    generation_duration = Column(Integer)  # in seconds
    error_message = Column(Text)
    
    # Access tracking
    download_count = Column(Integer, default=0)
    last_downloaded = Column(DateTime(timezone=True))
    
    # Metadata
    tags = Column(JSON)
    custom_fields = Column(JSON)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="reports")
    creator = relationship("User", foreign_keys=[created_by])