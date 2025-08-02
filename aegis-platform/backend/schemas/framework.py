from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FrameworkBase(BaseModel):
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None


class FrameworkCreate(FrameworkBase):
    pass


class FrameworkUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class FrameworkResponse(FrameworkBase):
    id: int
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ControlBase(BaseModel):
    framework_id: int
    control_id: str
    title: str
    description: Optional[str] = None
    guidance: Optional[str] = None
    parent_id: Optional[int] = None
    level: int = 1
    sort_order: float = 0
    control_type: Optional[str] = None
    implementation_status: Optional[str] = None
    testing_frequency: Optional[str] = None
    risk_level: Optional[str] = None
    compliance_references: Optional[str] = None  # JSON array


class ControlCreate(ControlBase):
    pass


class ControlUpdate(BaseModel):
    control_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    guidance: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    sort_order: Optional[float] = None
    control_type: Optional[str] = None
    implementation_status: Optional[str] = None
    testing_frequency: Optional[str] = None
    risk_level: Optional[str] = None
    compliance_references: Optional[str] = None
    is_active: Optional[bool] = None


class ControlResponse(ControlBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested objects
    framework: Optional[FrameworkResponse] = None
    parent: Optional['ControlResponse'] = None
    children: Optional[List['ControlResponse']] = []
    
    class Config:
        from_attributes = True


class ControlMappingBase(BaseModel):
    control_id: int
    mapped_framework: str
    mapped_control_id: str
    mapping_type: str
    confidence_level: str
    notes: Optional[str] = None


class ControlMappingCreate(ControlMappingBase):
    pass


class ControlMappingResponse(ControlMappingBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Update forward references
ControlResponse.model_rebuild()