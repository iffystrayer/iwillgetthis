from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    integration_type = Column(String(50), nullable=False)  # openvas, opencti, azure_ad, email, splunk, qradar, servicenow
    integration_type_id = Column(Integer, ForeignKey("integration_types.id"))  # Reference to IntegrationType
    
    # Connection details
    endpoint_url = Column(String(500))
    api_key = Column(String(500))  # Encrypted
    username = Column(String(255))
    password = Column(String(500))  # Encrypted
    
    # Enhanced authentication
    auth_method = Column(String(50), default="basic")  # basic, token, oauth, certificate
    auth_config = Column(JSON)  # Method-specific auth configuration
    
    # Configuration
    configuration = Column(JSON)  # Integration-specific settings
    
    # Status
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    last_connection_test = Column(DateTime(timezone=True))
    last_sync = Column(DateTime(timezone=True))
    
    # Enhanced status tracking
    health_status = Column(String(50), default="unknown")  # healthy, warning, error
    sync_status = Column(String(50), default="idle")  # idle, syncing, error
    
    # Error handling
    connection_error = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Performance tracking
    success_rate = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    
    # Metadata
    description = Column(Text)
    tags = Column(JSON)
    version = Column(String(50))  # Integration version
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    integration_type_ref = relationship("IntegrationType", back_populates="integrations")
    connector = relationship("IntegrationConnector", back_populates="integration", uselist=False)
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


class IntegrationType(Base):
    """Integration type definitions for SIEM, GRC, and other enterprise systems"""
    __tablename__ = "integration_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # splunk, qradar, servicenow, etc.
    category = Column(String(50), nullable=False)  # siem, grc, vulnerability, threat_intel
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Configuration schema
    config_schema = Column(JSON)  # JSON schema for configuration validation
    
    # Capabilities
    capabilities = Column(JSON)  # List of supported operations
    auth_methods = Column(JSON)  # Supported authentication methods
    
    # Connection details
    default_port = Column(Integer)
    requires_ssl = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_enterprise = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integrations = relationship("Integration", back_populates="integration_type_ref")


class IntegrationConnector(Base):
    """Base connector implementation for integration types"""
    __tablename__ = "integration_connectors"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    
    # Connector implementation
    connector_class = Column(String(200), nullable=False)  # Python class path
    connector_version = Column(String(50))
    
    # Status tracking
    status = Column(String(50), default="active")  # active, inactive, error, maintenance
    health_status = Column(String(50), default="unknown")  # healthy, warning, error
    last_health_check = Column(DateTime(timezone=True))
    health_details = Column(JSON)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    total_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Data sync tracking
    last_data_sync = Column(DateTime(timezone=True))
    sync_frequency = Column(Integer, default=3600)  # seconds
    auto_sync_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration", back_populates="connector")
    sync_logs = relationship("IntegrationSyncLog", back_populates="connector")


class IntegrationSyncLog(Base):
    """Log entries for integration data synchronization"""
    __tablename__ = "integration_sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    connector_id = Column(Integer, ForeignKey("integration_connectors.id"), nullable=False)
    
    # Sync details
    sync_type = Column(String(50), nullable=False)  # full, incremental, test
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    
    # Results
    status = Column(String(50), nullable=False)  # running, completed, failed, cancelled
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Performance
    duration_seconds = Column(Float)
    
    # Raw sync data
    sync_metadata = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    connector = relationship("IntegrationConnector", back_populates="sync_logs")


class SIEMEventData(Base):
    """SIEM event and log data from integrations"""
    __tablename__ = "siem_event_data"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    
    # Event identification
    event_id = Column(String(255))  # Original event ID from SIEM
    event_type = Column(String(100))  # alert, log, incident
    source_system = Column(String(100))  # Source system that generated the event
    
    # Event details
    title = Column(String(500))
    description = Column(Text)
    severity = Column(String(20))  # critical, high, medium, low, info
    priority = Column(String(20))  # urgent, high, medium, low
    
    # Classification
    category = Column(String(100))  # malware, intrusion, policy_violation, etc.
    subcategory = Column(String(100))
    rule_name = Column(String(255))
    rule_id = Column(String(100))
    
    # Source and destination
    source_ip = Column(String(45))  # IPv4/IPv6
    source_port = Column(Integer)
    source_hostname = Column(String(255))
    destination_ip = Column(String(45))
    destination_port = Column(Integer)
    destination_hostname = Column(String(255))
    
    # User and asset context
    username = Column(String(255))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    
    # Timestamps
    event_time = Column(DateTime(timezone=True))
    first_occurrence = Column(DateTime(timezone=True))
    last_occurrence = Column(DateTime(timezone=True))
    occurrence_count = Column(Integer, default=1)
    
    # Status and workflow
    status = Column(String(50), default="new")  # new, investigating, resolved, false_positive
    assigned_to = Column(Integer, ForeignKey("users.id"))
    investigation_notes = Column(Text)
    
    # Raw data
    raw_event_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration")
    asset = relationship("Asset")
    assigned_user = relationship("User")


class GRCControlData(Base):
    """GRC control and compliance data from integrations"""
    __tablename__ = "grc_control_data"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    
    # Control identification
    control_id = Column(String(100))  # Control ID from GRC system
    control_name = Column(String(500))
    framework = Column(String(100))  # NIST, ISO27001, SOX, etc.
    
    # Control details
    description = Column(Text)
    control_type = Column(String(50))  # preventive, detective, corrective
    control_frequency = Column(String(50))  # annual, quarterly, monthly, daily, continuous
    
    # Implementation
    implementation_status = Column(String(50))  # implemented, not_implemented, partially_implemented
    implementation_description = Column(Text)
    
    # Assessment results
    effectiveness_rating = Column(String(50))  # effective, partially_effective, ineffective
    last_assessment_date = Column(DateTime(timezone=True))
    next_assessment_date = Column(DateTime(timezone=True))
    
    # Risk and compliance
    risk_rating = Column(String(20))  # high, medium, low
    compliance_status = Column(String(50))  # compliant, non_compliant, gap_identified
    
    # Ownership
    control_owner = Column(String(255))
    business_owner = Column(String(255))
    
    # Evidence and documentation
    evidence_collected = Column(Boolean, default=False)
    evidence_links = Column(JSON)  # Links to evidence documents
    
    # Raw data
    raw_control_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration")