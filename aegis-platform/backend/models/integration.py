from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    integration_type = Column(String(50), nullable=False)  # openvas, opencti, azure_ad, email
    
    # Connection details
    endpoint_url = Column(String(500))
    api_key = Column(String(500))  # Encrypted
    username = Column(String(255))
    password = Column(String(500))  # Encrypted
    
    # Configuration
    configuration = Column(JSON)  # Integration-specific settings
    
    # Status
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    last_connection_test = Column(DateTime(timezone=True))
    last_sync = Column(DateTime(timezone=True))
    
    # Error handling
    connection_error = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    description = Column(Text)
    tags = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    vulnerability_data = relationship("VulnerabilityData", back_populates="integration")
    threat_intel_data = relationship("ThreatIntelData", back_populates="integration")


class VulnerabilityData(Base):
    __tablename__ = "vulnerability_data"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    
    # Vulnerability details
    vulnerability_id = Column(String(100))  # CVE, plugin ID, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Severity and scoring
    severity = Column(String(20))  # critical, high, medium, low, info
    cvss_score = Column(Float)
    cvss_vector = Column(String(200))
    
    # Technical details
    port = Column(String(20))
    protocol = Column(String(20))
    service = Column(String(100))
    
    # Scan details
    scan_id = Column(String(100))
    scan_date = Column(DateTime(timezone=True))
    scanner_name = Column(String(100))
    
    # Status
    status = Column(String(50), default="open")  # open, confirmed, fixed, false_positive
    first_detected = Column(DateTime(timezone=True))
    last_detected = Column(DateTime(timezone=True))
    
    # Remediation
    solution = Column(Text)
    workaround = Column(Text)
    
    # Risk assessment
    risk_score = Column(Float)
    business_impact = Column(Text)
    
    # Raw data
    raw_data = Column(JSON)  # Original scanner output
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration", back_populates="vulnerability_data")
    asset = relationship("Asset", back_populates="vulnerability_data")


class ThreatIntelData(Base):
    __tablename__ = "threat_intel_data"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    
    # Threat intelligence details
    intel_type = Column(String(50))  # ioc, malware, campaign, actor, technique
    indicator_type = Column(String(50))  # ip, domain, url, hash, email
    indicator_value = Column(String(1000))
    
    # Threat details
    threat_name = Column(String(255))
    description = Column(Text)
    
    # Attribution
    threat_actor = Column(String(255))
    campaign = Column(String(255))
    malware_family = Column(String(255))
    
    # Confidence and scoring
    confidence_level = Column(String(20))  # high, medium, low
    severity = Column(String(20))  # critical, high, medium, low
    
    # Timeline
    first_seen = Column(DateTime(timezone=True))
    last_seen = Column(DateTime(timezone=True))
    
    # Context
    tags = Column(JSON)
    tlp = Column(String(20))  # Traffic Light Protocol
    
    # Raw data
    raw_data = Column(JSON)  # Original CTI platform data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration", back_populates="threat_intel_data")