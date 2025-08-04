from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM as SQLEnum
from datetime import datetime
import uuid
from enum import Enum

Base = declarative_base()

class ContinuityPlanStatus(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    OUTDATED = "outdated"
    ARCHIVED = "archived"

class BusinessImpactLevel(Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"

class RecoveryPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"

class ContinuityTestStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ActivationStatus(Enum):
    INACTIVE = "inactive"
    STANDBY = "standby"
    PARTIAL_ACTIVATION = "partial_activation"
    FULL_ACTIVATION = "full_activation"
    RECOVERY_MODE = "recovery_mode"

class BusinessContinuityPlan(Base):
    __tablename__ = "business_continuity_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"BCP-{uuid.uuid4().hex[:8].upper()}")
    name = Column(String(500), nullable=False)
    description = Column(Text)
    version = Column(String(20), nullable=False, default="1.0")
    
    # Plan metadata
    status = Column(SQLEnum(ContinuityPlanStatus), default=ContinuityPlanStatus.DRAFT)
    scope = Column(Text)  # Departments, processes, systems covered
    business_units = Column(JSON)  # List of business units covered
    geographic_scope = Column(JSON)  # Locations covered
    
    # Plan details
    objectives = Column(Text)
    assumptions = Column(Text)
    dependencies = Column(JSON)  # System/service dependencies
    
    # Approval and review
    approved_by = Column(String(255))
    approved_date = Column(DateTime)
    next_review_date = Column(DateTime)
    review_frequency_months = Column(Integer, default=12)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Relationships
    business_impacts = relationship("BusinessImpactAnalysis", back_populates="continuity_plan")
    recovery_procedures = relationship("DisasterRecoveryProcedure", back_populates="continuity_plan")
    tests = relationship("ContinuityTest", back_populates="continuity_plan")
    activations = relationship("PlanActivation", back_populates="continuity_plan")

class BusinessImpactAnalysis(Base):
    __tablename__ = "business_impact_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"BIA-{uuid.uuid4().hex[:8].upper()}")
    continuity_plan_id = Column(Integer, ForeignKey("business_continuity_plans.id"))
    
    # Business process details
    business_process = Column(String(500), nullable=False)
    process_owner = Column(String(255))
    department = Column(String(255))
    
    # Impact assessment
    impact_level = Column(SQLEnum(BusinessImpactLevel), nullable=False)
    financial_impact_hourly = Column(Float)  # Financial loss per hour
    financial_impact_daily = Column(Float)  # Financial loss per day
    operational_impact = Column(Text)
    regulatory_impact = Column(Text)
    reputational_impact = Column(Text)
    
    # Recovery objectives
    rto_hours = Column(Float, nullable=False)  # Recovery Time Objective in hours
    rpo_hours = Column(Float, nullable=False)  # Recovery Point Objective in hours
    minimum_service_level = Column(Float)  # Percentage of normal capacity
    
    # Dependencies
    critical_dependencies = Column(JSON)  # Systems, suppliers, etc.
    required_resources = Column(JSON)  # Personnel, equipment, facilities
    
    # Peak periods and seasonality
    peak_periods = Column(JSON)
    seasonal_considerations = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    continuity_plan = relationship("BusinessContinuityPlan", back_populates="business_impacts")

class DisasterRecoveryProcedure(Base):
    __tablename__ = "disaster_recovery_procedures"
    
    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"DRP-{uuid.uuid4().hex[:8].upper()}")
    continuity_plan_id = Column(Integer, ForeignKey("business_continuity_plans.id"))
    
    # Procedure details
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(255))  # e.g., IT Systems, Facilities, Communications
    priority = Column(SQLEnum(RecoveryPriority), nullable=False)
    
    # Recovery specifications
    target_rto_hours = Column(Float, nullable=False)
    target_rpo_hours = Column(Float, nullable=False)
    estimated_recovery_time = Column(Float)  # Actual estimated time
    
    # Procedure steps
    preparation_steps = Column(JSON)  # Pre-disaster preparation
    activation_triggers = Column(JSON)  # Conditions that trigger this procedure
    recovery_steps = Column(JSON)  # Step-by-step recovery process
    validation_steps = Column(JSON)  # How to verify successful recovery
    
    # Resources and requirements
    required_personnel = Column(JSON)
    required_equipment = Column(JSON)
    required_facilities = Column(JSON)
    estimated_cost = Column(Float)
    
    # Testing and validation
    last_tested = Column(DateTime)
    test_frequency_months = Column(Integer, default=6)
    test_success_rate = Column(Float)  # Percentage of successful tests
    
    # Automation
    automated = Column(Boolean, default=False)
    automation_script = Column(Text)  # Path to automation script
    manual_intervention_required = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    continuity_plan = relationship("BusinessContinuityPlan", back_populates="recovery_procedures")
    executions = relationship("ProcedureExecution", back_populates="procedure")

class ContinuityTest(Base):
    __tablename__ = "continuity_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"CT-{uuid.uuid4().hex[:8].upper()}")
    continuity_plan_id = Column(Integer, ForeignKey("business_continuity_plans.id"))
    
    # Test details
    name = Column(String(500), nullable=False)
    description = Column(Text)
    test_type = Column(String(100))  # Tabletop, Walkthrough, Simulation, Full Test
    scope = Column(Text)  # What's being tested
    
    # Test status and scheduling
    status = Column(SQLEnum(ContinuityTestStatus), default=ContinuityTestStatus.PLANNED)
    scheduled_date = Column(DateTime)
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    
    # Test participants
    test_coordinator = Column(String(255))
    participants = Column(JSON)  # List of participants
    observers = Column(JSON)  # List of observers
    
    # Test objectives and scenarios
    objectives = Column(JSON)  # What the test aims to achieve
    scenarios = Column(JSON)  # Test scenarios
    success_criteria = Column(JSON)  # How success is measured
    
    # Test results
    overall_success = Column(Boolean)
    rto_achieved = Column(Float)  # Actual RTO achieved during test
    rpo_achieved = Column(Float)  # Actual RPO achieved during test
    issues_identified = Column(JSON)  # Problems found during test
    recommendations = Column(JSON)  # Improvement recommendations
    
    # Test documentation
    test_report = Column(Text)
    lessons_learned = Column(Text)
    action_items = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    continuity_plan = relationship("BusinessContinuityPlan", back_populates="tests")

class PlanActivation(Base):
    __tablename__ = "plan_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    activation_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"PA-{uuid.uuid4().hex[:8].upper()}")
    continuity_plan_id = Column(Integer, ForeignKey("business_continuity_plans.id"))
    
    # Activation details
    trigger_event = Column(String(500))  # What triggered the activation
    activation_level = Column(SQLEnum(ActivationStatus), nullable=False)
    activated_by = Column(String(255))
    activation_reason = Column(Text)
    
    # Timing
    activation_time = Column(DateTime, nullable=False)
    expected_duration = Column(Float)  # Expected duration in hours
    actual_end_time = Column(DateTime)
    
    # Scope of activation
    affected_business_units = Column(JSON)
    activated_procedures = Column(JSON)  # Which procedures were activated
    personnel_notified = Column(JSON)
    
    # Status tracking
    current_status = Column(String(100))
    completion_percentage = Column(Float, default=0.0)
    
    # Communication
    stakeholder_notifications = Column(JSON)
    communication_log = Column(JSON)
    
    # Results and metrics
    success_metrics = Column(JSON)
    actual_rto = Column(Float)  # Actual recovery time achieved
    actual_rpo = Column(Float)  # Actual recovery point achieved
    lessons_learned = Column(Text)
    
    # Deactivation
    deactivated_by = Column(String(255))
    deactivation_time = Column(DateTime)
    deactivation_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    continuity_plan = relationship("BusinessContinuityPlan", back_populates="activations")
    procedure_executions = relationship("ProcedureExecution", back_populates="activation")

class ProcedureExecution(Base):
    __tablename__ = "procedure_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"PE-{uuid.uuid4().hex[:8].upper()}")
    procedure_id = Column(Integer, ForeignKey("disaster_recovery_procedures.id"))
    activation_id = Column(Integer, ForeignKey("plan_activations.id"), nullable=True)
    
    # Execution details
    executed_by = Column(String(255))
    execution_context = Column(String(100))  # Test, Drill, Actual Incident
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Float)
    
    # Execution status
    status = Column(String(50))  # Started, In Progress, Completed, Failed, Aborted
    completion_percentage = Column(Float, default=0.0)
    
    # Results
    successful = Column(Boolean)
    rto_met = Column(Boolean)
    rpo_met = Column(Boolean)
    issues_encountered = Column(JSON)
    deviations_from_plan = Column(Text)
    
    # Documentation
    execution_log = Column(JSON)  # Step-by-step execution log
    notes = Column(Text)
    evidence_collected = Column(JSON)  # Screenshots, logs, etc.
    
    # Metrics
    actual_recovery_time = Column(Float)  # In hours
    actual_data_loss = Column(Float)  # In hours (RPO)
    resource_utilization = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    procedure = relationship("DisasterRecoveryProcedure", back_populates="executions")
    activation = relationship("PlanActivation", back_populates="procedure_executions")

class ContinuityMetrics(Base):
    __tablename__ = "continuity_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"CM-{uuid.uuid4().hex[:8].upper()}")
    
    # Metric details
    metric_name = Column(String(255), nullable=False)
    metric_type = Column(String(100))  # RTO, RPO, Test Success Rate, etc.
    category = Column(String(100))  # Business Process, System, Department
    target_name = Column(String(255))  # What this metric measures
    
    # Target values
    target_value = Column(Float)
    tolerance_threshold = Column(Float)  # Acceptable deviation
    
    # Current performance
    current_value = Column(Float)
    measurement_date = Column(DateTime, default=datetime.utcnow)
    trend = Column(String(50))  # Improving, Stable, Degrading
    
    # Historical tracking
    historical_values = Column(JSON)  # Time series data
    last_test_value = Column(Float)
    last_incident_value = Column(Float)
    
    # Status
    status = Column(String(50))  # Meeting Target, At Risk, Below Target
    action_required = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContinuityResource(Base):
    __tablename__ = "continuity_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: f"CR-{uuid.uuid4().hex[:8].upper()}")
    
    # Resource details
    name = Column(String(500), nullable=False)
    resource_type = Column(String(100))  # Personnel, Equipment, Facility, Service
    category = Column(String(100))
    description = Column(Text)
    
    # Availability and capacity
    available = Column(Boolean, default=True)
    capacity = Column(Float)  # Maximum capacity
    current_utilization = Column(Float)  # Current usage percentage
    
    # Location and contact
    location = Column(String(500))
    contact_information = Column(JSON)
    
    # Resource specifications
    specifications = Column(JSON)
    capabilities = Column(JSON)
    limitations = Column(JSON)
    
    # Maintenance and lifecycle
    maintenance_schedule = Column(JSON)
    last_maintenance = Column(DateTime)
    next_maintenance = Column(DateTime)
    replacement_date = Column(DateTime)
    
    # Cost information
    acquisition_cost = Column(Float)
    maintenance_cost_annual = Column(Float)
    replacement_cost = Column(Float)
    
    # Criticality and dependencies
    criticality_level = Column(String(50))  # Critical, Important, Standard
    dependencies = Column(JSON)  # What this resource depends on
    dependents = Column(JSON)  # What depends on this resource
    
    # Backup and alternatives
    backup_resources = Column(JSON)
    alternative_sources = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)