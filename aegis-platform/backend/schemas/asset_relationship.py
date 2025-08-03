"""
Pydantic schemas for Asset Relationships and Dependencies
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RelationshipTypeEnum(str, Enum):
    DEPENDS_ON = "depends_on"
    PROVIDES_SERVICE_TO = "provides_service_to"
    COMMUNICATES_WITH = "communicates_with"
    HOSTED_ON = "hosted_on"
    HOSTS = "hosts"
    BACKUP_OF = "backup_of"
    CLUSTER_MEMBER = "cluster_member"
    LOAD_BALANCED_BY = "load_balanced_by"
    MONITORS = "monitors"
    PROCESSES_DATA_FROM = "processes_data_from"


class RelationshipStrengthEnum(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    CRITICAL = "critical"


class DataFlowDirectionEnum(str, Enum):
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"


class AssetRelationshipBase(BaseModel):
    source_asset_id: int
    target_asset_id: int
    relationship_type: RelationshipTypeEnum
    relationship_strength: RelationshipStrengthEnum = RelationshipStrengthEnum.MODERATE
    description: Optional[str] = None
    port: Optional[str] = None
    protocol: Optional[str] = None
    data_flow_direction: Optional[DataFlowDirectionEnum] = DataFlowDirectionEnum.BIDIRECTIONAL
    impact_percentage: Optional[float] = Field(None, ge=0, le=100)
    recovery_time_minutes: Optional[int] = Field(None, ge=0)
    discovered_method: Optional[str] = "manual"
    
    @validator('source_asset_id', 'target_asset_id')
    def validate_asset_ids(cls, v):
        if v <= 0:
            raise ValueError('Asset ID must be positive')
        return v
    
    @validator('target_asset_id')
    def validate_different_assets(cls, v, values):
        if 'source_asset_id' in values and v == values['source_asset_id']:
            raise ValueError('Source and target assets cannot be the same')
        return v


class AssetRelationshipCreate(AssetRelationshipBase):
    pass


class AssetRelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipTypeEnum] = None
    relationship_strength: Optional[RelationshipStrengthEnum] = None
    description: Optional[str] = None
    port: Optional[str] = None
    protocol: Optional[str] = None
    data_flow_direction: Optional[DataFlowDirectionEnum] = None
    impact_percentage: Optional[float] = Field(None, ge=0, le=100)
    recovery_time_minutes: Optional[int] = Field(None, ge=0)
    is_validated: Optional[bool] = None
    is_active: Optional[bool] = None


class AssetSummary(BaseModel):
    """Lightweight asset summary for relationship display"""
    id: int
    name: str
    asset_type: str
    criticality: str
    environment: Optional[str] = None


class AssetRelationshipResponse(AssetRelationshipBase):
    id: int
    is_validated: bool
    last_validated: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    # Include asset summaries
    source_asset: Optional[AssetSummary] = None
    target_asset: Optional[AssetSummary] = None
    
    class Config:
        from_attributes = True


class DependencyNode(BaseModel):
    """Node in a dependency graph"""
    asset_id: int
    asset_name: str
    asset_type: str
    criticality: str
    environment: str
    level: int = 0  # Depth in dependency tree
    relationship_type: Optional[str] = None
    relationship_strength: Optional[str] = None
    impact_percentage: Optional[float] = None


class DependencyGraph(BaseModel):
    """Complete dependency graph for an asset"""
    root_asset_id: int
    root_asset_name: str
    dependencies: List[DependencyNode] = []  # Assets this depends on
    dependents: List[DependencyNode] = []    # Assets that depend on this
    max_depth: int = 0
    total_dependencies: int = 0
    total_dependents: int = 0
    critical_path_assets: List[int] = []  # Assets in critical dependency path


class ImpactAnalysis(BaseModel):
    """Impact analysis for asset failure scenarios"""
    asset_id: int
    asset_name: str
    scenario_name: str
    affected_assets: List[Dict[str, Any]] = []
    affected_services: List[Dict[str, Any]] = []
    estimated_downtime_minutes: Optional[int] = None
    estimated_revenue_impact: Optional[float] = None
    business_functions_affected: List[str] = []
    recovery_steps: List[str] = []
    estimated_recovery_time: Optional[int] = None
    scenario_probability: float = Field(0.1, ge=0, le=1)


class AssetDependencyGraphResponse(BaseModel):
    """Response model for asset dependency graph"""
    id: int
    asset_id: int
    dependency_level: int
    total_dependencies: int
    total_dependents: int
    critical_path_length: int
    single_point_of_failure_risk: float
    cascade_failure_risk: float
    overall_dependency_risk: float
    last_calculated: datetime
    calculation_duration_ms: Optional[int] = None
    
    class Config:
        from_attributes = True


class AssetImpactScenarioResponse(BaseModel):
    """Response model for impact scenarios"""
    id: int
    asset_id: int
    scenario_name: str
    affected_assets_count: int
    affected_services_count: int
    estimated_downtime_minutes: Optional[int] = None
    estimated_revenue_impact: Optional[float] = None
    estimated_recovery_time: Optional[int] = None
    scenario_probability: float
    last_updated: datetime
    
    class Config:
        from_attributes = True


class BulkRelationshipImport(BaseModel):
    """Bulk import model for relationships"""
    relationships: List[AssetRelationshipCreate]
    validate_assets: bool = True
    auto_create_reverse: bool = False  # Automatically create reverse relationships


class BulkRelationshipImportResponse(BaseModel):
    """Response for bulk import"""
    success_count: int
    error_count: int
    errors: List[str] = []
    created_relationships: List[AssetRelationshipResponse] = []


class NetworkDiscoveryRequest(BaseModel):
    """Request for automated network discovery"""
    source_asset_ids: List[int]
    discovery_method: str = "network_scan"  # network_scan, config_analysis, log_analysis
    scan_depth: int = Field(2, ge=1, le=5)  # How many hops to discover
    include_weak_relationships: bool = False
    auto_validate: bool = True


class NetworkDiscoveryResponse(BaseModel):
    """Response for network discovery"""
    discovered_relationships: List[AssetRelationshipResponse] = []
    discovery_summary: Dict[str, Any] = {}
    scan_duration_seconds: float
    assets_scanned: int
    relationships_found: int
    validation_results: Dict[str, Any] = {}