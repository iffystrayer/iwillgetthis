from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReportTypeEnum(str, Enum):
    RISK_REGISTER = "risk_register"
    ASSESSMENT_SUMMARY = "assessment_summary"
    COMPLIANCE_STATUS = "compliance_status"
    EXECUTIVE_SUMMARY = "executive_summary"
    VULNERABILITY_REPORT = "vulnerability_report"
    TASK_STATUS = "task_status"
    CUSTOM = "custom"


class ReportFormatEnum(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"


class ReportStatusEnum(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class ReportTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: ReportTypeEnum
    template_data: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    style_config: Optional[Dict[str, Any]] = None
    default_filters: Optional[Dict[str, Any]] = None
    parameter_schema: Optional[Dict[str, Any]] = None
    is_public: bool = False


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    style_config: Optional[Dict[str, Any]] = None
    default_filters: Optional[Dict[str, Any]] = None
    parameter_schema: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class ReportTemplateResponse(ReportTemplateBase):
    id: int
    is_system_template: bool = False
    usage_count: int = 0
    created_by: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: ReportTypeEnum
    template_id: Optional[int] = None
    format: ReportFormatEnum = ReportFormatEnum.PDF
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    is_scheduled: bool = False
    schedule_config: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None
    distribution_list: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ReportStatusEnum] = None
    format: Optional[ReportFormatEnum] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    is_scheduled: Optional[bool] = None
    schedule_config: Optional[Dict[str, Any]] = None
    next_generation: Optional[datetime] = None
    recipients: Optional[List[str]] = None
    distribution_list: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ReportResponse(ReportBase):
    id: int
    status: ReportStatusEnum
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_insights: Optional[Dict[str, Any]] = None
    ai_confidence_score: Optional[int] = None
    next_generation: Optional[datetime] = None
    generation_started: Optional[datetime] = None
    generation_completed: Optional[datetime] = None
    generation_duration: Optional[int] = None
    error_message: Optional[str] = None
    download_count: int = 0
    last_downloaded: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportGeneration(BaseModel):
    report_id: int
    generate_ai_summary: bool = True
    include_insights: bool = True
    custom_sections: Optional[List[str]] = None


class ReportSchedule(BaseModel):
    cron_expression: str
    timezone: str = "UTC"
    enabled: bool = True
    next_run: Optional[datetime] = None