from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssetTypeEnum(str, Enum):
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    APPLICATION = "application"
    DATABASE = "database"
    CLOUD_SERVICE = "cloud_service"
    MOBILE_DEVICE = "mobile_device"
    IOT_DEVICE = "iot_device"
    OTHER = "other"


class AssetCriticalityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class AssetCategoryCreate(AssetCategoryBase):
    pass


class AssetCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class AssetCategoryResponse(AssetCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AssetBase(BaseModel):
    name: str
    description: Optional[str] = None
    asset_type: AssetTypeEnum
    criticality: AssetCriticalityEnum = AssetCriticalityEnum.MEDIUM
    category_id: Optional[int] = None
    owner_id: Optional[int] = None
    
    # Technical details
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    version: Optional[str] = None
    location: Optional[str] = None
    environment: Optional[str] = None
    
    # Business details
    business_unit: Optional[str] = None
    cost_center: Optional[str] = None
    compliance_scope: Optional[str] = None  # JSON array
    
    # Lifecycle
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    
    # Metadata
    tags: Optional[str] = None  # JSON array
    custom_fields: Optional[str] = None  # JSON object


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    asset_type: Optional[AssetTypeEnum] = None
    criticality: Optional[AssetCriticalityEnum] = None
    category_id: Optional[int] = None
    owner_id: Optional[int] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    version: Optional[str] = None
    location: Optional[str] = None
    environment: Optional[str] = None
    business_unit: Optional[str] = None
    cost_center: Optional[str] = None
    compliance_scope: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    tags: Optional[str] = None
    custom_fields: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class AssetResponse(AssetBase):
    id: int
    status: str
    last_scan_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    # Nested objects
    category: Optional[AssetCategoryResponse] = None
    
    class Config:
        from_attributes = True


class AssetImport(BaseModel):
    assets: List[AssetCreate]


class AssetImportResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[str] = []
    imported_assets: List[AssetResponse] = []