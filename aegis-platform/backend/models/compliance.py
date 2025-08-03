"""
Compliance Management Data Models
Enterprise-grade compliance framework tracking, assessment, and reporting
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum

Base = declarative_base()


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""
    SOX = "sox"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST_800_53 = "nist_800_53"
    NIST_CSF = "nist_csf"
    CIS_CONTROLS = "cis_controls"
    COBIT = "cobit"
    FFIEC = "ffiec"
    FISMA = "fisma"
    FedRAMP = "fedramp"
    SOC_2 = "soc_2"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    CUSTOM = "custom"


class ComplianceStatus(str, Enum):
    """Compliance assessment status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"
    IN_PROGRESS = "in_progress"
    REQUIRES_REVIEW = "requires_review"
    EXEMPTED = "exempted"
    NOT_APPLICABLE = "not_applicable"


class ControlType(str, Enum):
    """Types of compliance controls"""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATING = "compensating"
    DIRECTIVE = "directive"
    ADMINISTRATIVE = "administrative"
    TECHNICAL = "technical"
    PHYSICAL = "physical"


class TestingFrequency(str, Enum):
    """Frequency for compliance testing"""
    CONTINUOUS = "continuous"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    AD_HOC = "ad_hoc"


class EvidenceType(str, Enum):
    """Types of compliance evidence"""
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    CONFIGURATION = "configuration"
    AUDIT_REPORT = "audit_report"
    TEST_RESULT = "test_result"
    CERTIFICATE = "certificate"
    POLICY = "policy"
    PROCEDURE = "procedure"
    INTERVIEW = "interview"
    OBSERVATION = "observation"


class ComplianceFrameworkModel(Base):
    """Compliance framework definitions and metadata"""
    __tablename__ = "compliance_frameworks"

    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    framework_type = Column(SQLEnum(ComplianceFramework), nullable=False)
    
    description = Column(Text)
    version = Column(String(50))
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    
    # Framework metadata
    authority = Column(String(200))  # Regulatory authority
    scope = Column(Text)  # Framework scope
    industry_focus = Column(String(100))
    geographic_scope = Column(String(100))
    
    # Framework structure
    total_controls = Column(Integer, default=0)
    control_families = Column(JSON)  # Organized control structure
    framework_hierarchy = Column(JSON)  # Framework organization
    
    # Configuration
    active = Column(Boolean, default=True)
    mandatory = Column(Boolean, default=False)
    custom_framework = Column(Boolean, default=False)
    
    # Automation
    automated_assessment = Column(Boolean, default=False)
    assessment_frequency = Column(SQLEnum(TestingFrequency), default=TestingFrequency.QUARTERLY)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    controls = relationship("ComplianceControl", back_populates="framework", cascade="all, delete-orphan")
    assessments = relationship("ComplianceAssessment", back_populates="framework")
    requirements = relationship("ComplianceRequirement", back_populates="framework")


class ComplianceControl(Base):
    """Individual compliance controls within frameworks"""
    __tablename__ = "compliance_controls"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(100), nullable=False, index=True)  # e.g., AC-1, PCI-3.4
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id"), nullable=False)
    
    # Control identification
    control_number = Column(String(50))
    control_family = Column(String(100))
    control_title = Column(String(500), nullable=False)
    control_objective = Column(Text)
    
    # Control details
    description = Column(Text, nullable=False)
    implementation_guidance = Column(Text)
    assessment_procedures = Column(Text)
    
    # Control classification
    control_type = Column(SQLEnum(ControlType), nullable=False)
    control_class = Column(String(50))  # Low, Moderate, High
    priority = Column(String(20), default="medium")
    
    # Control properties
    baseline_impact = Column(String(20))  # Low, Moderate, High
    privacy_control = Column(Boolean, default=False)
    security_control = Column(Boolean, default=True)
    operational_control = Column(Boolean, default=False)
    
    # Implementation
    implementation_status = Column(SQLEnum(ComplianceStatus), default=ComplianceStatus.NOT_ASSESSED)
    implementation_notes = Column(Text)
    compensating_controls = Column(JSON)  # List of compensating control IDs
    
    # Testing and validation
    testing_frequency = Column(SQLEnum(TestingFrequency), default=TestingFrequency.ANNUALLY)
    testing_methodology = Column(Text)
    last_test_date = Column(DateTime)
    next_test_date = Column(DateTime)
    
    # Automation
    automated_testing = Column(Boolean, default=False)
    automation_tool = Column(String(100))
    automation_script = Column(Text)
    
    # Dependencies
    parent_control_id = Column(Integer, ForeignKey("compliance_controls.id"))
    dependent_controls = Column(JSON)  # List of dependent control IDs
    related_controls = Column(JSON)  # Related control mappings
    
    # Metadata
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    framework = relationship("ComplianceFrameworkModel", back_populates="controls")
    parent_control = relationship("ComplianceControl", remote_side=[id])
    assessments = relationship("ControlAssessment", back_populates="control")
    evidence = relationship("ComplianceEvidence", back_populates="control")
    findings = relationship("ComplianceFinding", back_populates="control")


class ComplianceRequirement(Base):
    """Specific compliance requirements mapped to business processes"""
    __tablename__ = "compliance_requirements"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(String(100), unique=True, nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id"), nullable=False)
    
    # Requirement details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    requirement_text = Column(Text)
    
    # Business mapping
    business_process = Column(String(200))
    process_owner = Column(Integer, ForeignKey("users.id"))
    responsible_parties = Column(JSON)  # List of responsible user/team IDs
    
    # Implementation
    implementation_approach = Column(Text)
    implementation_deadline = Column(DateTime)
    implementation_status = Column(SQLEnum(ComplianceStatus), default=ComplianceStatus.NOT_ASSESSED)
    
    # Risk and impact
    risk_level = Column(String(20), default="medium")
    business_impact = Column(String(20))
    compliance_impact = Column(Text)
    
    # Validation
    validation_method = Column(String(100))
    validation_frequency = Column(SQLEnum(TestingFrequency), default=TestingFrequency.ANNUALLY)
    last_validation_date = Column(DateTime)
    next_validation_date = Column(DateTime)
    
    # Control mapping
    mapped_controls = Column(JSON)  # List of control IDs that satisfy this requirement
    
    # Metadata
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    framework = relationship("ComplianceFrameworkModel", back_populates="requirements")
    assessments = relationship("RequirementAssessment", back_populates="requirement")


class ComplianceAssessment(Base):
    """Compliance assessments and audits"""
    __tablename__ = "compliance_assessments"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(100), unique=True, nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id"), nullable=False)
    
    # Assessment details
    assessment_name = Column(String(300), nullable=False)
    assessment_type = Column(String(50))  # internal, external, self, third_party
    assessment_scope = Column(Text)
    
    # Timing
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    planned_completion_date = Column(DateTime)
    
    # Assessment team
    lead_assessor = Column(Integer, ForeignKey("users.id"))
    assessment_team = Column(JSON)  # List of assessor user IDs
    external_auditor = Column(String(200))
    
    # Status and progress
    status = Column(String(50), default="planned")
    progress_percentage = Column(Integer, default=0)
    
    # Results summary
    overall_compliance_score = Column(Float)
    compliant_controls = Column(Integer, default=0)
    non_compliant_controls = Column(Integer, default=0)
    partially_compliant_controls = Column(Integer, default=0)
    not_assessed_controls = Column(Integer, default=0)
    
    # Findings summary
    total_findings = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    
    # Documentation
    assessment_methodology = Column(Text)
    assessment_criteria = Column(Text)
    executive_summary = Column(Text)
    detailed_report_path = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    framework = relationship("ComplianceFrameworkModel", back_populates="assessments")
    control_assessments = relationship("ControlAssessment", back_populates="assessment")
    requirement_assessments = relationship("RequirementAssessment", back_populates="assessment")
    findings = relationship("ComplianceFinding", back_populates="assessment")


class ControlAssessment(Base):
    """Individual control assessment results"""
    __tablename__ = "control_assessments"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("compliance_assessments.id"), nullable=False)
    control_id = Column(Integer, ForeignKey("compliance_controls.id"), nullable=False)
    
    # Assessment details
    assessment_date = Column(DateTime, nullable=False)
    assessor = Column(Integer, ForeignKey("users.id"))
    assessment_method = Column(String(100))  # interview, observation, testing, review
    
    # Results
    compliance_status = Column(SQLEnum(ComplianceStatus), nullable=False)
    effectiveness_rating = Column(String(20))  # effective, partially_effective, ineffective
    confidence_level = Column(String(20), default="medium")
    
    # Scoring
    compliance_score = Column(Float)  # 0-100
    maturity_level = Column(Integer)  # 1-5
    implementation_percentage = Column(Float)  # 0-100
    
    # Assessment details
    testing_performed = Column(Text)
    evidence_reviewed = Column(Text)
    assessment_notes = Column(Text)
    limitations = Column(Text)
    
    # Findings
    deficiencies_identified = Column(Text)
    compensating_controls_evaluated = Column(Text)
    recommendations = Column(Text)
    
    # Follow-up
    requires_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    assessment = relationship("ComplianceAssessment", back_populates="control_assessments")
    control = relationship("ComplianceControl", back_populates="assessments")
    evidence = relationship("ComplianceEvidence", back_populates="control_assessment")


class RequirementAssessment(Base):
    """Assessment of compliance requirements"""
    __tablename__ = "requirement_assessments"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("compliance_assessments.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.id"), nullable=False)
    
    # Assessment results
    compliance_status = Column(SQLEnum(ComplianceStatus), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    assessor = Column(Integer, ForeignKey("users.id"))
    
    # Details
    implementation_details = Column(Text)
    gaps_identified = Column(Text)
    improvement_recommendations = Column(Text)
    
    # Scoring
    compliance_percentage = Column(Float)  # 0-100
    risk_rating = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    assessment = relationship("ComplianceAssessment", back_populates="requirement_assessments")
    requirement = relationship("ComplianceRequirement", back_populates="assessments")


class ComplianceFinding(Base):
    """Compliance findings and deficiencies"""
    __tablename__ = "compliance_findings"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(String(100), unique=True, nullable=False, index=True)
    assessment_id = Column(Integer, ForeignKey("compliance_assessments.id"), nullable=False)
    control_id = Column(Integer, ForeignKey("compliance_controls.id"))
    
    # Finding details
    finding_title = Column(String(500), nullable=False)
    finding_description = Column(Text, nullable=False)
    finding_type = Column(String(50))  # deficiency, observation, recommendation
    
    # Severity and impact
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    risk_level = Column(String(20))
    business_impact = Column(Text)
    compliance_impact = Column(Text)
    
    # Root cause analysis
    root_cause = Column(Text)
    contributing_factors = Column(JSON)
    
    # Remediation
    remediation_plan = Column(Text)
    remediation_owner = Column(Integer, ForeignKey("users.id"))
    remediation_deadline = Column(DateTime)
    remediation_status = Column(String(50), default="open")
    remediation_notes = Column(Text)
    
    # Validation
    validation_required = Column(Boolean, default=True)
    validation_method = Column(String(100))
    validated_date = Column(DateTime)
    validated_by = Column(Integer, ForeignKey("users.id"))
    
    # Status tracking
    status = Column(String(50), default="open")  # open, in_progress, resolved, closed
    resolution_date = Column(DateTime)
    resolution_notes = Column(Text)
    
    # References
    related_findings = Column(JSON)  # List of related finding IDs
    external_references = Column(JSON)
    
    # Metadata
    identified_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    assessment = relationship("ComplianceAssessment", back_populates="findings")
    control = relationship("ComplianceControl", back_populates="findings")
    evidence = relationship("ComplianceEvidence", back_populates="finding")


class ComplianceEvidence(Base):
    """Evidence collected for compliance assessments"""
    __tablename__ = "compliance_evidence"

    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String(100), unique=True, nullable=False, index=True)
    control_assessment_id = Column(Integer, ForeignKey("control_assessments.id"))
    control_id = Column(Integer, ForeignKey("compliance_controls.id"))
    finding_id = Column(Integer, ForeignKey("compliance_findings.id"))
    
    # Evidence details
    evidence_name = Column(String(300), nullable=False)
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    description = Column(Text)
    
    # File information
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    file_hash = Column(String(64))  # SHA-256 hash
    
    # Evidence metadata
    collection_date = Column(DateTime, nullable=False)
    collected_by = Column(Integer, ForeignKey("users.id"))
    collection_method = Column(String(100))
    
    # Validation
    validated = Column(Boolean, default=False)
    validation_date = Column(DateTime)
    validation_notes = Column(Text)
    
    # Chain of custody
    custody_log = Column(JSON)  # Chain of custody tracking
    
    # Classification
    confidentiality_level = Column(String(20), default="internal")
    retention_period_days = Column(Integer, default=2555)  # 7 years default
    
    # Metadata
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    control_assessment = relationship("ControlAssessment", back_populates="evidence")
    control = relationship("ComplianceControl", back_populates="evidence")
    finding = relationship("ComplianceFinding", back_populates="evidence")


class ComplianceException(Base):
    """Compliance exceptions and waivers"""
    __tablename__ = "compliance_exceptions"

    id = Column(Integer, primary_key=True, index=True)
    exception_id = Column(String(100), unique=True, nullable=False, index=True)
    control_id = Column(Integer, ForeignKey("compliance_controls.id"), nullable=False)
    
    # Exception details
    exception_title = Column(String(300), nullable=False)
    exception_reason = Column(Text, nullable=False)
    business_justification = Column(Text, nullable=False)
    
    # Exception type
    exception_type = Column(String(50))  # permanent, temporary, conditional
    
    # Risk assessment
    residual_risk = Column(String(20))
    risk_mitigation = Column(Text)
    compensating_controls = Column(JSON)
    
    # Approval
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime)
    approval_conditions = Column(Text)
    
    # Validity
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime)
    review_frequency = Column(SQLEnum(TestingFrequency), default=TestingFrequency.ANNUALLY)
    next_review_date = Column(DateTime)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, denied, expired, revoked
    
    # Monitoring
    monitoring_requirements = Column(Text)
    last_review_date = Column(DateTime)
    review_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ComplianceMetric(Base):
    """Compliance metrics and KPIs"""
    __tablename__ = "compliance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id"))
    
    # Metric definition
    metric_name = Column(String(200), nullable=False)
    metric_description = Column(Text)
    metric_type = Column(String(50))  # percentage, count, ratio, score
    
    # Calculation
    calculation_method = Column(Text)
    data_source = Column(String(100))
    measurement_frequency = Column(SQLEnum(TestingFrequency), default=TestingFrequency.MONTHLY)
    
    # Targets and thresholds
    target_value = Column(Float)
    threshold_values = Column(JSON)  # Green, yellow, red thresholds
    
    # Current values
    current_value = Column(Float)
    previous_value = Column(Float)
    trend_direction = Column(String(20))  # improving, declining, stable
    
    # Measurement period
    measurement_date = Column(DateTime)
    measurement_period_start = Column(DateTime)
    measurement_period_end = Column(DateTime)
    
    # Metadata
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())