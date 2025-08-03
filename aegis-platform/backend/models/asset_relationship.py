"""
Asset Relationship and Dependency Models
Defines relationships between assets for impact analysis and dependency mapping
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class RelationshipType(enum.Enum):
    """Types of relationships between assets"""
    DEPENDS_ON = "depends_on"              # Asset A depends on Asset B
    PROVIDES_SERVICE_TO = "provides_service_to"  # Asset A provides service to Asset B
    COMMUNICATES_WITH = "communicates_with"      # Asset A communicates with Asset B
    HOSTED_ON = "hosted_on"                      # Asset A is hosted on Asset B
    HOSTS = "hosts"                              # Asset A hosts Asset B
    BACKUP_OF = "backup_of"                      # Asset A is backup of Asset B
    CLUSTER_MEMBER = "cluster_member"            # Asset A is cluster member with Asset B
    LOAD_BALANCED_BY = "load_balanced_by"        # Asset A is load balanced by Asset B
    MONITORS = "monitors"                        # Asset A monitors Asset B
    PROCESSES_DATA_FROM = "processes_data_from"  # Asset A processes data from Asset B


class RelationshipStrength(enum.Enum):
    """Strength of the relationship/dependency"""
    WEAK = "weak"          # Non-critical relationship (degraded performance)
    MODERATE = "moderate"  # Important relationship (service degradation)
    STRONG = "strong"      # Critical relationship (service failure)
    CRITICAL = "critical"  # Essential relationship (complete failure)


class AssetRelationship(Base):
    """Defines relationships and dependencies between assets"""
    __tablename__ = "asset_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    target_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    relationship_type = Column(Enum(RelationshipType), nullable=False)
    relationship_strength = Column(Enum(RelationshipStrength), default=RelationshipStrength.MODERATE)
    
    # Additional metadata
    description = Column(Text)
    port = Column(String(10))  # Network port if applicable
    protocol = Column(String(20))  # Network protocol (TCP, UDP, HTTP, etc.)
    data_flow_direction = Column(String(20))  # bidirectional, source_to_target, target_to_source
    
    # Impact analysis
    impact_percentage = Column(Float)  # Percentage impact if relationship fails (0-100)
    recovery_time_minutes = Column(Integer)  # Time to recover if relationship fails
    
    # Validation and discovery
    is_validated = Column(Boolean, default=False)  # Whether relationship has been verified
    last_validated = Column(DateTime(timezone=True))
    discovered_method = Column(String(50))  # manual, network_scan, config_analysis, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    source_asset = relationship("Asset", foreign_keys=[source_asset_id], back_populates="outgoing_relationships")
    target_asset = relationship("Asset", foreign_keys=[target_asset_id], back_populates="incoming_relationships")
    creator = relationship("User")


class AssetDependencyGraph(Base):
    """Precomputed dependency graph for performance optimization"""
    __tablename__ = "asset_dependency_graphs"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    # Dependency levels (how many hops from root)
    dependency_level = Column(Integer, default=0)
    
    # Impact metrics
    total_dependencies = Column(Integer, default=0)  # Total assets this depends on
    total_dependents = Column(Integer, default=0)   # Total assets that depend on this
    critical_path_length = Column(Integer, default=0)  # Longest critical dependency chain
    
    # Risk metrics
    single_point_of_failure_risk = Column(Float, default=0.0)  # 0-1 scale
    cascade_failure_risk = Column(Float, default=0.0)         # 0-1 scale
    overall_dependency_risk = Column(Float, default=0.0)       # 0-1 scale
    
    # Graph data (JSON)
    dependency_tree = Column(Text)  # JSON representation of dependency tree
    impact_analysis = Column(Text)  # JSON analysis of potential impacts
    
    # Metadata
    last_calculated = Column(DateTime(timezone=True), server_default=func.now())
    calculation_duration_ms = Column(Integer)
    
    # Relationships
    asset = relationship("Asset", back_populates="dependency_graph")


class AssetImpactScenario(Base):
    """Precomputed impact scenarios for different failure modes"""
    __tablename__ = "asset_impact_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    scenario_name = Column(String(100), nullable=False)  # "complete_failure", "partial_degradation", etc.
    
    # Impact metrics
    affected_assets_count = Column(Integer, default=0)
    affected_services_count = Column(Integer, default=0)
    estimated_downtime_minutes = Column(Integer)
    estimated_revenue_impact = Column(Float)  # Monetary impact
    
    # Affected assets and services (JSON arrays)
    affected_assets = Column(Text)  # JSON array of asset IDs and impact levels
    affected_services = Column(Text)  # JSON array of service names and impact levels
    
    # Recovery information
    recovery_steps = Column(Text)  # JSON array of recovery procedures
    estimated_recovery_time = Column(Integer)  # Minutes to full recovery
    
    # Business impact
    business_functions_affected = Column(Text)  # JSON array of affected business functions
    compliance_impact = Column(Text)  # JSON description of compliance implications
    
    # Metadata
    scenario_probability = Column(Float, default=0.1)  # 0-1 probability of occurrence
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="impact_scenarios")