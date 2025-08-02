from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class AssetType(enum.Enum):
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    APPLICATION = "application"
    DATABASE = "database"
    CLOUD_SERVICE = "cloud_service"
    MOBILE_DEVICE = "mobile_device"
    IOT_DEVICE = "iot_device"
    OTHER = "other"


class AssetCriticality(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetCategory(Base):
    __tablename__ = "asset_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assets = relationship("Asset", back_populates="category")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    asset_type = Column(Enum(AssetType), nullable=False)
    criticality = Column(Enum(AssetCriticality), default=AssetCriticality.MEDIUM)
    category_id = Column(Integer, ForeignKey("asset_categories.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Technical details
    ip_address = Column(String(45))  # IPv4 or IPv6
    hostname = Column(String(255))
    operating_system = Column(String(100))
    version = Column(String(50))
    location = Column(String(255))
    environment = Column(String(50))  # Production, Staging, Development
    
    # Business details
    business_unit = Column(String(100))
    cost_center = Column(String(50))
    compliance_scope = Column(Text)  # JSON array of compliance frameworks
    
    # Status and lifecycle
    status = Column(String(50), default="active")  # active, inactive, decommissioned
    purchase_date = Column(DateTime(timezone=True))
    warranty_expiry = Column(DateTime(timezone=True))
    last_scan_date = Column(DateTime(timezone=True))
    
    # Metadata
    tags = Column(Text)  # JSON array of tags
    custom_fields = Column(Text)  # JSON object for custom fields
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    category = relationship("AssetCategory", back_populates="assets")
    owner = relationship("User", foreign_keys=[owner_id])
    creator = relationship("User", foreign_keys=[created_by])
    assessments = relationship("Assessment", back_populates="asset")
    risks = relationship("Risk", back_populates="asset")
    vulnerability_data = relationship("VulnerabilityData", back_populates="asset")