"""Pydantic schemas for bulk operations"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class BulkImportResponse(BaseModel):
    """Response schema for bulk import operations"""
    success: bool
    total_processed: int
    successful_imports: int
    failed_imports: int
    updated_records: int
    errors: List[str] = []
    imported_ids: List[int] = []

class BulkExportRequest(BaseModel):
    """Request schema for bulk export operations"""
    format_type: str = Field(..., regex="^(xlsx|csv|json)$")
    entity_type: str = Field(..., regex="^(risks|controls)$")
    filters: Optional[Dict[str, Any]] = None

class BulkExportResponse(BaseModel):
    """Response schema for bulk export operations"""
    success: bool
    file_path: str
    total_records: int
    export_format: str
    filters_applied: Optional[Dict[str, Any]] = None

class BulkValidationResponse(BaseModel):
    """Response schema for bulk validation operations"""
    is_valid: bool
    total_records: int
    valid_records: int
    errors: List[str] = []
    warnings: List[str] = []

class BulkTemplateResponse(BaseModel):
    """Response schema for bulk template generation"""
    template_path: str
    format_type: str
    entity_type: str
    fields_included: List[str]

class BulkOperationHistoryItem(BaseModel):
    """Schema for bulk operation history items"""
    id: int
    operation_type: str  # import or export
    entity_type: str     # risks or controls
    description: str
    timestamp: datetime
    status: str          # success or failed
    
class BulkOperationInfoResponse(BaseModel):
    """Response schema for bulk operations system information"""
    supported_formats: Dict[str, List[str]]
    entity_types: List[str]
    max_file_size: str
    max_records_per_import: int
    supported_encodings: List[str]
    template_fields: Dict[str, List[str]]