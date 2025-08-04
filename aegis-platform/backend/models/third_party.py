from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM as SQLEnum
from datetime import datetime
import uuid
from enum import Enum

Base = declarative_base()

class VendorStatus(Enum):
    PROSPECT = "prospect"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"

class VendorTier(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class AssessmentStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_UPDATE = "requires_update"

class ContractStatus(Enum):
    DRAFT = "draft"
    UNDER_NEGOTIATION = "under_negotiation"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"

class MonitoringStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ALERT = "alert"
    CRITICAL = "critical"
    OFFLINE = "offline"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    PENDING_REVIEW = "pending_review"
    EXCEPTION_GRANTED = "exception_granted"

# Vendor Management

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VEN-{uuid.uuid4().hex[:8].upper()}")
    
    # Basic information
    name = Column(String(500), nullable=False, index=True)
    legal_name = Column(String(500))
    business_name = Column(String(500))
    vendor_type = Column(String(100))  # software, hardware, service, consulting, outsourcing
    
    # Contact information
    primary_contact_name = Column(String(255))
    primary_contact_email = Column(String(255))
    primary_contact_phone = Column(String(50))
    website = Column(String(500))
    
    # Business details
    industry = Column(String(255))
    business_model = Column(String(255))
    number_of_employees = Column(Integer)
    annual_revenue = Column(Float)
    founding_year = Column(Integer)
    
    # Address information
    headquarters_address = Column(JSON)  # Full address structure
    operating_locations = Column(JSON)  # List of operating locations
    data_processing_locations = Column(JSON)  # Where data is processed
    
    # Vendor classification
    tier = Column(SQLEnum(VendorTier), nullable=False, default=VendorTier.LOW)
    status = Column(SQLEnum(VendorStatus), default=VendorStatus.PROSPECT)
    criticality = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    
    # Services and products
    services_provided = Column(JSON)  # List of services/products
    service_categories = Column(JSON)  # Categories of services
    data_types_accessed = Column(JSON)  # Types of data vendor accesses
    systems_accessed = Column(JSON)  # Systems vendor has access to
    
    # Financial information
    contract_value_annual = Column(Float)
    contract_value_total = Column(Float)
    payment_terms = Column(String(255))
    
    # Risk and compliance
    overall_risk_score = Column(Float, default=0.0)
    last_risk_assessment = Column(DateTime)
    next_assessment_due = Column(DateTime)
    
    # Certifications and standards
    certifications = Column(JSON)  # ISO27001, SOC2, etc.
    compliance_frameworks = Column(JSON)  # Frameworks they comply with
    security_attestations = Column(JSON)  # Security certifications
    
    # Relationship management
    relationship_manager = Column(String(255))  # Internal relationship manager
    vendor_account_manager = Column(String(255))  # Vendor's account manager
    escalation_contacts = Column(JSON)  # Emergency/escalation contacts
    
    # Business continuity
    backup_vendors = Column(JSON)  # Alternative vendors
    dependency_level = Column(String(100))  # How dependent we are on this vendor
    replacement_difficulty = Column(String(100))  # How hard to replace
    
    # Onboarding and lifecycle
    onboarding_date = Column(DateTime)
    contract_start_date = Column(DateTime)
    contract_end_date = Column(DateTime)
    termination_notice_period = Column(Integer)  # Days notice required
    
    # Notes and tags
    notes = Column(Text)
    tags = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Relationships
    assessments = relationship("VendorRiskAssessment", back_populates="vendor")
    contracts = relationship("VendorContract", back_populates="vendor")
    monitoring = relationship("VendorMonitoring", back_populates="vendor")
    incidents = relationship("VendorIncident", back_populates="vendor")

class VendorRiskAssessment(Base):
    __tablename__ = "vendor_risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VRA-{uuid.uuid4().hex[:8].upper()}")
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    
    # Assessment metadata
    assessment_name = Column(String(500), nullable=False)
    assessment_type = Column(String(100))  # initial, periodic, triggered, renewal
    assessment_methodology = Column(String(255))  # questionnaire, audit, review
    
    # Scope and timeline
    scope_description = Column(Text)
    assessment_start_date = Column(DateTime, nullable=False)
    assessment_end_date = Column(DateTime)
    due_date = Column(DateTime)
    
    # Status and progress
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.NOT_STARTED)
    progress_percentage = Column(Float, default=0.0)
    
    # Risk categories and scores
    information_security_score = Column(Float, default=0.0)
    data_protection_score = Column(Float, default=0.0)
    operational_risk_score = Column(Float, default=0.0)
    financial_risk_score = Column(Float, default=0.0)
    compliance_risk_score = Column(Float, default=0.0)
    business_continuity_score = Column(Float, default=0.0)
    reputational_risk_score = Column(Float, default=0.0)
    
    # Overall assessment results
    overall_risk_score = Column(Float, default=0.0)
    overall_risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    previous_risk_score = Column(Float)
    risk_trend = Column(String(20))  # improving, stable, deteriorating
    
    # Detailed findings
    strengths = Column(JSON)  # Areas where vendor excels
    weaknesses = Column(JSON)  # Areas of concern
    gaps = Column(JSON)  # Compliance/security gaps
    recommendations = Column(JSON)  # Recommendations for improvement
    
    # Risk factors
    inherent_risks = Column(JSON)  # Risks inherent to the vendor/service
    residual_risks = Column(JSON)  # Risks after controls
    mitigating_controls = Column(JSON)  # Controls in place
    
    # Assessment details
    questionnaire_responses = Column(JSON)  # Vendor's responses
    supporting_documents = Column(JSON)  # Documents provided
    site_visit_conducted = Column(Boolean, default=False)
    site_visit_findings = Column(JSON)
    
    # Review and approval
    reviewed_by = Column(String(255))
    review_date = Column(DateTime)
    approved_by = Column(String(255))
    approval_date = Column(DateTime)
    approval_comments = Column(Text)
    
    # Next assessment
    next_assessment_due = Column(DateTime)
    assessment_frequency_months = Column(Integer, default=12)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="assessments")
    action_items = relationship("VendorActionItem", back_populates="assessment")

class VendorContract(Base):
    __tablename__ = "vendor_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VCT-{uuid.uuid4().hex[:8].upper()}")
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    
    # Contract basics
    contract_name = Column(String(500), nullable=False)
    contract_type = Column(String(100))  # MSA, SOW, SLA, DPA, etc.
    contract_number = Column(String(255))
    parent_contract_id = Column(Integer, ForeignKey("vendor_contracts.id"))
    
    # Contract terms
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    auto_renewal = Column(Boolean, default=False)
    renewal_notice_days = Column(Integer, default=90)
    termination_notice_days = Column(Integer, default=30)
    
    # Financial terms
    contract_value = Column(Float)
    currency = Column(String(10), default="USD")
    payment_terms = Column(String(255))
    payment_schedule = Column(String(100))  # monthly, quarterly, annually
    penalty_clauses = Column(JSON)
    
    # Service levels and requirements
    service_levels = Column(JSON)  # SLA requirements
    performance_metrics = Column(JSON)  # KPIs and metrics
    security_requirements = Column(JSON)  # Security obligations
    compliance_requirements = Column(JSON)  # Compliance obligations
    data_handling_requirements = Column(JSON)  # Data protection requirements
    
    # Risk and liability
    liability_cap = Column(Float)
    insurance_requirements = Column(JSON)
    indemnification_terms = Column(JSON)
    force_majeure_clauses = Column(JSON)
    
    # Contract management
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT)
    contract_owner = Column(String(255))  # Internal contract owner
    business_owner = Column(String(255))  # Business stakeholder
    legal_reviewer = Column(String(255))
    
    # Documents and amendments
    contract_document_path = Column(String(1000))
    amendments = Column(JSON)  # Contract amendments
    related_documents = Column(JSON)  # Related documents
    
    # Renewal and termination
    renewal_date = Column(DateTime)
    renewal_status = Column(String(100))
    termination_date = Column(DateTime)
    termination_reason = Column(Text)
    
    # Compliance tracking
    regulatory_approvals = Column(JSON)  # Required approvals
    privacy_impact_assessment = Column(Boolean, default=False)
    security_review_completed = Column(Boolean, default=False)
    
    # Notifications and alerts
    renewal_alerts_sent = Column(Integer, default=0)
    compliance_alerts_sent = Column(Integer, default=0)
    last_alert_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="contracts")
    parent_contract = relationship("VendorContract", remote_side=[id])
    sla_monitoring = relationship("SLAMonitoring", back_populates="contract")

class VendorMonitoring(Base):
    __tablename__ = "vendor_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    monitoring_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VMN-{uuid.uuid4().hex[:8].upper()}")
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    
    # Monitoring configuration
    monitoring_type = Column(String(100))  # security, performance, compliance, financial
    monitoring_frequency = Column(String(50))  # continuous, daily, weekly, monthly
    automated_monitoring = Column(Boolean, default=True)
    
    # Security monitoring
    security_posture_score = Column(Float)
    vulnerability_scan_results = Column(JSON)
    security_incidents = Column(JSON)
    certificate_status = Column(JSON)  # SSL/TLS certificate monitoring
    
    # Performance monitoring
    service_availability = Column(Float)  # % uptime
    response_time_ms = Column(Integer)
    throughput_metrics = Column(JSON)
    error_rates = Column(JSON)
    
    # Compliance monitoring
    compliance_status = Column(SQLEnum(ComplianceStatus), default=ComplianceStatus.PENDING_REVIEW)
    regulatory_changes = Column(JSON)  # Changes affecting vendor
    audit_findings = Column(JSON)
    corrective_actions = Column(JSON)
    
    # Financial monitoring
    financial_health_score = Column(Float)
    credit_rating = Column(String(10))
    financial_alerts = Column(JSON)
    payment_history = Column(JSON)
    
    # News and intelligence
    news_sentiment = Column(Float)  # Sentiment analysis of news
    negative_news_alerts = Column(JSON)
    regulatory_actions = Column(JSON)
    breach_notifications = Column(JSON)
    
    # Risk indicators
    risk_indicators = Column(JSON)  # Early warning indicators
    threshold_breaches = Column(JSON)  # SLA/KPI breaches
    escalation_triggers = Column(JSON)
    
    # Monitoring status
    status = Column(SQLEnum(MonitoringStatus), default=MonitoringStatus.ACTIVE)
    last_check_date = Column(DateTime)
    next_check_date = Column(DateTime)
    
    # Alert configuration
    alert_thresholds = Column(JSON)
    notification_recipients = Column(JSON)
    escalation_rules = Column(JSON)
    
    # Data sources
    monitoring_tools = Column(JSON)  # Tools used for monitoring
    data_sources = Column(JSON)  # Sources of monitoring data
    api_endpoints = Column(JSON)  # Endpoints for automated checks
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="monitoring")
    alerts = relationship("VendorAlert", back_populates="monitoring")

class VendorIncident(Base):
    __tablename__ = "vendor_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VIN-{uuid.uuid4().hex[:8].upper()}")
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    
    # Incident details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    incident_type = Column(String(100))  # security, operational, compliance, financial
    severity = Column(SQLEnum(RiskLevel), nullable=False)
    
    # Impact assessment
    business_impact = Column(String(100))  # high, medium, low
    affected_services = Column(JSON)
    affected_users = Column(Integer)
    financial_impact = Column(Float)
    regulatory_impact = Column(Boolean, default=False)
    
    # Timeline
    discovered_date = Column(DateTime, nullable=False)
    reported_date = Column(DateTime)
    acknowledged_date = Column(DateTime)
    resolved_date = Column(DateTime)
    verified_date = Column(DateTime)
    
    # Response details
    immediate_actions = Column(JSON)
    containment_actions = Column(JSON)
    remediation_actions = Column(JSON)
    
    # Root cause analysis
    root_cause = Column(Text)
    contributing_factors = Column(JSON)
    lessons_learned = Column(Text)
    
    # Communication
    internal_notification_sent = Column(Boolean, default=False)
    customer_notification_required = Column(Boolean, default=False)
    regulatory_notification_required = Column(Boolean, default=False)
    communication_log = Column(JSON)
    
    # Resolution
    resolution_summary = Column(Text)
    preventive_measures = Column(JSON)
    follow_up_actions = Column(JSON)
    
    # Incident management
    incident_manager = Column(String(255))
    status = Column(String(100))  # open, investigating, resolved, closed
    priority = Column(String(20))  # critical, high, medium, low
    
    # External references
    vendor_incident_id = Column(String(255))  # Vendor's incident ID
    external_references = Column(JSON)  # Links to external reports
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="incidents")

class VendorActionItem(Base):
    __tablename__ = "vendor_action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VAC-{uuid.uuid4().hex[:8].upper()}")
    assessment_id = Column(Integer, ForeignKey("vendor_risk_assessments.id"))
    
    # Action item details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # security, compliance, operational, contractual
    priority = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM)
    
    # Assignment and ownership
    assigned_to = Column(String(255))  # Internal owner
    vendor_contact = Column(String(255))  # Vendor contact responsible
    
    # Timeline
    due_date = Column(DateTime)
    estimated_effort_hours = Column(Float)
    
    # Status tracking
    status = Column(String(100), default="open")  # open, in_progress, completed, overdue, cancelled
    progress_percentage = Column(Float, default=0.0)
    completed_date = Column(DateTime)
    
    # Implementation details
    implementation_plan = Column(Text)
    acceptance_criteria = Column(JSON)
    verification_method = Column(String(255))
    
    # Progress tracking
    progress_updates = Column(JSON)  # Timeline of updates
    obstacles = Column(JSON)  # Blockers or challenges
    dependencies = Column(JSON)  # Other actions this depends on
    
    # Impact and justification
    risk_reduction_expected = Column(Float)
    business_justification = Column(Text)
    cost_estimate = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relationships
    assessment = relationship("VendorRiskAssessment", back_populates="action_items")

class VendorAlert(Base):
    __tablename__ = "vendor_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VAL-{uuid.uuid4().hex[:8].upper()}")
    monitoring_id = Column(Integer, ForeignKey("vendor_monitoring.id"))
    
    # Alert details
    alert_type = Column(String(100))  # threshold_breach, anomaly, compliance, security
    severity = Column(SQLEnum(RiskLevel), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Alert data
    metric_name = Column(String(255))
    current_value = Column(Float)
    threshold_value = Column(Float)
    alert_data = Column(JSON)  # Additional alert context
    
    # Status and resolution
    status = Column(String(100), default="open")  # open, acknowledged, investigating, resolved
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime)
    resolved_by = Column(String(255))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Notification tracking
    notifications_sent = Column(JSON)  # Who was notified and when
    escalation_level = Column(Integer, default=0)
    auto_resolved = Column(Boolean, default=False)
    
    # Timestamps
    triggered_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    monitoring = relationship("VendorMonitoring", back_populates="alerts")

class SLAMonitoring(Base):
    __tablename__ = "sla_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    sla_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"SLA-{uuid.uuid4().hex[:8].upper()}")
    contract_id = Column(Integer, ForeignKey("vendor_contracts.id"))
    
    # SLA definition
    sla_name = Column(String(255), nullable=False)
    sla_description = Column(Text)
    metric_name = Column(String(255), nullable=False)
    metric_unit = Column(String(50))  # %, seconds, count, etc.
    
    # Thresholds and targets
    target_value = Column(Float, nullable=False)
    warning_threshold = Column(Float)
    critical_threshold = Column(Float)
    measurement_period = Column(String(50))  # monthly, quarterly, annually
    
    # Current performance
    current_value = Column(Float)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    
    # Performance history
    historical_performance = Column(JSON)  # Time series data
    trend_direction = Column(String(20))  # improving, stable, declining
    
    # Breach tracking
    breach_count = Column(Integer, default=0)
    last_breach_date = Column(DateTime)
    consecutive_breaches = Column(Integer, default=0)
    
    # Penalties and credits
    penalty_rate = Column(Float)  # % of contract value
    service_credits_earned = Column(Float)
    penalties_applied = Column(Float)
    
    # Reporting
    reporting_frequency = Column(String(50))  # weekly, monthly, quarterly
    last_report_date = Column(DateTime)
    next_report_due = Column(DateTime)
    
    # Status
    status = Column(String(100), default="active")  # active, breached, suspended
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contract = relationship("VendorContract", back_populates="sla_monitoring")

class SupplyChainNode(Base):
    __tablename__ = "supply_chain_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"SCN-{uuid.uuid4().hex[:8].upper()}")
    
    # Node identification
    name = Column(String(500), nullable=False)
    node_type = Column(String(100))  # vendor, subcontractor, supplier, partner
    tier_level = Column(Integer, default=1)  # 1st tier, 2nd tier, etc.
    
    # Relationship mapping
    parent_node_id = Column(Integer, ForeignKey("supply_chain_nodes.id"))
    primary_vendor_id = Column(Integer, ForeignKey("vendors.id"))
    
    # Node details
    services_provided = Column(JSON)
    criticality_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    geographic_location = Column(JSON)
    
    # Risk assessment
    inherent_risk_score = Column(Float, default=0.0)
    residual_risk_score = Column(Float, default=0.0)
    concentration_risk = Column(Float, default=0.0)  # Risk from over-dependence
    
    # Dependencies
    dependent_services = Column(JSON)  # Services that depend on this node
    dependency_level = Column(String(100))  # critical, important, nice-to-have
    single_point_of_failure = Column(Boolean, default=False)
    
    # Alternative options
    backup_options = Column(JSON)  # Alternative suppliers/vendors
    replacement_time_days = Column(Integer)  # Time to replace if needed
    switching_cost = Column(Float)
    
    # Monitoring and visibility
    visibility_level = Column(String(100))  # full, partial, limited, none
    monitoring_capabilities = Column(JSON)
    data_sharing_agreements = Column(JSON)
    
    # Status
    operational_status = Column(String(100), default="active")
    last_assessment_date = Column(DateTime)
    next_assessment_due = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_node = relationship("SupplyChainNode", remote_side=[id])
    vendor = relationship("Vendor")

class VendorDueDiligence(Base):
    __tablename__ = "vendor_due_diligence"
    
    id = Column(Integer, primary_key=True, index=True)
    due_diligence_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"VDD-{uuid.uuid4().hex[:8].upper()}")
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    
    # Due diligence scope
    due_diligence_type = Column(String(100))  # initial, annual, triggered, acquisition
    scope_areas = Column(JSON)  # security, financial, legal, operational
    
    # Financial due diligence
    financial_statements_reviewed = Column(Boolean, default=False)
    credit_check_completed = Column(Boolean, default=False)
    financial_stability_rating = Column(String(10))
    bankruptcy_risk_score = Column(Float)
    
    # Legal and regulatory
    legal_entity_verification = Column(Boolean, default=False)
    regulatory_compliance_check = Column(Boolean, default=False)
    sanctions_screening = Column(Boolean, default=False)
    litigation_history = Column(JSON)
    
    # Security and privacy
    security_assessment_completed = Column(Boolean, default=False)
    privacy_assessment_completed = Column(Boolean, default=False)
    penetration_testing_results = Column(JSON)
    security_certifications_verified = Column(JSON)
    
    # Operational due diligence
    business_continuity_plan_reviewed = Column(Boolean, default=False)
    disaster_recovery_tested = Column(Boolean, default=False)
    operational_resilience_score = Column(Float)
    key_personnel_background_checks = Column(Boolean, default=False)
    
    # References and reputation
    reference_checks_completed = Column(Boolean, default=False)
    customer_references = Column(JSON)
    industry_reputation_score = Column(Float)
    negative_media_screening = Column(JSON)
    
    # Technology and infrastructure
    technology_stack_review = Column(Boolean, default=False)
    infrastructure_assessment = Column(JSON)
    data_handling_practices = Column(JSON)
    cybersecurity_maturity_level = Column(String(50))
    
    # Results and recommendations
    overall_rating = Column(String(50))  # approved, conditional, rejected
    risk_factors_identified = Column(JSON)
    mitigation_requirements = Column(JSON)
    approval_conditions = Column(JSON)
    
    # Review and approval
    reviewed_by = Column(String(255))
    review_date = Column(DateTime)
    approved_by = Column(String(255))
    approval_date = Column(DateTime)
    
    # Validity and renewal
    valid_until = Column(DateTime)
    renewal_required = Column(Boolean, default=True)
    next_review_due = Column(DateTime)
    
    # Documentation
    supporting_documents = Column(JSON)
    assessment_reports = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))