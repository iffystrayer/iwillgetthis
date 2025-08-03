"""
Asset Dependency Analyzer
Provides dependency mapping, impact analysis, and risk assessment for asset relationships
"""

from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, deque
import json
import time
from datetime import datetime
from sqlalchemy.orm import Session

from models.asset import Asset
from models.asset_relationship import AssetRelationship, RelationshipType, RelationshipStrength
from schemas.asset_relationship import DependencyGraph, DependencyNode, ImpactAnalysis


class AssetDependencyAnalyzer:
    """Analyzes asset dependencies and calculates impact scenarios"""
    
    def __init__(self, db: Session):
        self.db = db
        self.relationship_weights = {
            RelationshipStrength.WEAK: 0.25,
            RelationshipStrength.MODERATE: 0.5,
            RelationshipStrength.STRONG: 0.75,
            RelationshipStrength.CRITICAL: 1.0
        }
    
    def build_dependency_graph(self, asset_id: int, max_depth: int = 5) -> DependencyGraph:
        """Build complete dependency graph for an asset"""
        
        # Get the root asset
        root_asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not root_asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        # Build dependencies (what this asset depends on)
        dependencies = self._traverse_dependencies(asset_id, max_depth, direction="dependencies")
        
        # Build dependents (what depends on this asset)
        dependents = self._traverse_dependencies(asset_id, max_depth, direction="dependents")
        
        # Find critical path
        critical_path_assets = self._find_critical_path(asset_id)
        
        return DependencyGraph(
            root_asset_id=asset_id,
            root_asset_name=root_asset.name,
            dependencies=dependencies,
            dependents=dependents,
            max_depth=max(len(dependencies), len(dependents)),
            total_dependencies=len(dependencies),
            total_dependents=len(dependents),
            critical_path_assets=critical_path_assets
        )
    
    def _traverse_dependencies(self, asset_id: int, max_depth: int, direction: str) -> List[DependencyNode]:
        """Traverse dependency tree using BFS"""
        visited = set()
        queue = deque([(asset_id, 0)])  # (asset_id, depth)
        nodes = []
        
        while queue:
            current_asset_id, depth = queue.popleft()
            
            if depth >= max_depth or current_asset_id in visited:
                continue
            
            visited.add(current_asset_id)
            
            # Get relationships based on direction
            if direction == "dependencies":
                # What this asset depends on (outgoing relationships where this is source)
                relationships = self.db.query(AssetRelationship).filter(
                    AssetRelationship.source_asset_id == current_asset_id,
                    AssetRelationship.is_active == True,
                    AssetRelationship.relationship_type.in_([
                        RelationshipType.DEPENDS_ON,
                        RelationshipType.HOSTED_ON,
                        RelationshipType.LOAD_BALANCED_BY,
                        RelationshipType.PROCESSES_DATA_FROM
                    ])
                ).all()
                
                for rel in relationships:
                    target_asset = rel.target_asset
                    if target_asset and target_asset.id not in visited:
                        nodes.append(DependencyNode(
                            asset_id=target_asset.id,
                            asset_name=target_asset.name,
                            asset_type=target_asset.asset_type.value,
                            criticality=target_asset.criticality.value,
                            environment=target_asset.environment or "unknown",
                            level=depth + 1,
                            relationship_type=rel.relationship_type.value,
                            relationship_strength=rel.relationship_strength.value,
                            impact_percentage=rel.impact_percentage
                        ))
                        queue.append((target_asset.id, depth + 1))
                        
            else:  # dependents
                # What depends on this asset (incoming relationships where this is target)
                relationships = self.db.query(AssetRelationship).filter(
                    AssetRelationship.target_asset_id == current_asset_id,
                    AssetRelationship.is_active == True,
                    AssetRelationship.relationship_type.in_([
                        RelationshipType.DEPENDS_ON,
                        RelationshipType.HOSTED_ON,
                        RelationshipType.LOAD_BALANCED_BY,
                        RelationshipType.PROCESSES_DATA_FROM
                    ])
                ).all()
                
                for rel in relationships:
                    source_asset = rel.source_asset
                    if source_asset and source_asset.id not in visited:
                        nodes.append(DependencyNode(
                            asset_id=source_asset.id,
                            asset_name=source_asset.name,
                            asset_type=source_asset.asset_type.value,
                            criticality=source_asset.criticality.value,
                            environment=source_asset.environment or "unknown",
                            level=depth + 1,
                            relationship_type=rel.relationship_type.value,
                            relationship_strength=rel.relationship_strength.value,
                            impact_percentage=rel.impact_percentage
                        ))
                        queue.append((source_asset.id, depth + 1))
        
        return nodes
    
    def _find_critical_path(self, asset_id: int) -> List[int]:
        """Find the critical dependency path (longest chain of critical relationships)"""
        critical_relationships = self.db.query(AssetRelationship).filter(
            AssetRelationship.relationship_strength == RelationshipStrength.CRITICAL,
            AssetRelationship.is_active == True
        ).all()
        
        # Build adjacency list for critical relationships
        graph = defaultdict(list)
        for rel in critical_relationships:
            graph[rel.source_asset_id].append(rel.target_asset_id)
        
        # Find longest path from asset_id
        def dfs_longest_path(node: int, visited: Set[int], path: List[int]) -> List[int]:
            visited.add(node)
            longest = path.copy()
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    candidate = dfs_longest_path(neighbor, visited.copy(), path + [neighbor])
                    if len(candidate) > len(longest):
                        longest = candidate
            
            return longest
        
        return dfs_longest_path(asset_id, set(), [asset_id])
    
    def calculate_risk_metrics(self, asset_id: int) -> Dict[str, float]:
        """Calculate various risk metrics for an asset"""
        
        # Get all relationships for this asset
        incoming_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.target_asset_id == asset_id,
            AssetRelationship.is_active == True
        ).all()
        
        outgoing_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.source_asset_id == asset_id,
            AssetRelationship.is_active == True
        ).all()
        
        # Single Point of Failure Risk
        spof_risk = self._calculate_spof_risk(asset_id, incoming_rels)
        
        # Cascade Failure Risk
        cascade_risk = self._calculate_cascade_risk(asset_id, outgoing_rels)
        
        # Overall Dependency Risk
        overall_risk = (spof_risk + cascade_risk) / 2
        
        return {
            "single_point_of_failure_risk": spof_risk,
            "cascade_failure_risk": cascade_risk,
            "overall_dependency_risk": overall_risk
        }
    
    def _calculate_spof_risk(self, asset_id: int, incoming_relationships: List[AssetRelationship]) -> float:
        """Calculate single point of failure risk"""
        if not incoming_relationships:
            return 0.0
        
        # Count critical dependencies
        critical_deps = sum(1 for rel in incoming_relationships 
                          if rel.relationship_strength == RelationshipStrength.CRITICAL)
        
        # Risk increases with number of critical dependencies
        base_risk = min(critical_deps * 0.2, 1.0)
        
        # Adjust for redundancy
        dependency_types = set(rel.relationship_type for rel in incoming_relationships)
        redundancy_factor = len(dependency_types) / len(incoming_relationships) if incoming_relationships else 1
        
        return base_risk * (2 - redundancy_factor)  # Less redundancy = higher risk
    
    def _calculate_cascade_risk(self, asset_id: int, outgoing_relationships: List[AssetRelationship]) -> float:
        """Calculate cascade failure risk"""
        if not outgoing_relationships:
            return 0.0
        
        # Risk based on number of dependent assets and relationship strength
        risk_score = 0.0
        for rel in outgoing_relationships:
            weight = self.relationship_weights[rel.relationship_strength]
            risk_score += weight * 0.1  # Each relationship adds risk
        
        return min(risk_score, 1.0)
    
    def analyze_impact_scenario(self, asset_id: int, scenario_name: str = "complete_failure") -> ImpactAnalysis:
        """Analyze the impact of an asset failure scenario"""
        
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        # Get dependency graph
        dep_graph = self.build_dependency_graph(asset_id)
        
        # Analyze affected assets
        affected_assets = []
        total_downtime = 0
        total_revenue_impact = 0.0
        
        for dependent in dep_graph.dependents:
            impact_level = self._determine_impact_level(dependent.relationship_strength, scenario_name)
            downtime = self._estimate_downtime(dependent, impact_level)
            revenue_impact = self._estimate_revenue_impact(dependent, downtime)
            
            affected_assets.append({
                "asset_id": dependent.asset_id,
                "asset_name": dependent.asset_name,
                "impact_level": impact_level,
                "estimated_downtime_minutes": downtime,
                "estimated_revenue_impact": revenue_impact
            })
            
            total_downtime = max(total_downtime, downtime)  # Use max as parallel failures
            total_revenue_impact += revenue_impact
        
        # Analyze affected services
        affected_services = self._identify_affected_services(dep_graph.dependents)
        
        # Generate recovery steps
        recovery_steps = self._generate_recovery_steps(asset, scenario_name, dep_graph)
        
        # Estimate recovery time
        recovery_time = self._estimate_recovery_time(asset, scenario_name, len(affected_assets))
        
        # Identify affected business functions
        business_functions = self._identify_business_functions(asset, affected_assets)
        
        return ImpactAnalysis(
            asset_id=asset_id,
            asset_name=asset.name,
            scenario_name=scenario_name,
            affected_assets=affected_assets,
            affected_services=affected_services,
            estimated_downtime_minutes=total_downtime,
            estimated_revenue_impact=total_revenue_impact,
            business_functions_affected=business_functions,
            recovery_steps=recovery_steps,
            estimated_recovery_time=recovery_time,
            scenario_probability=self._calculate_scenario_probability(asset, scenario_name)
        )
    
    def _determine_impact_level(self, relationship_strength: str, scenario_name: str) -> str:
        """Determine impact level based on relationship strength and scenario"""
        if scenario_name == "complete_failure":
            if relationship_strength in ["critical", "strong"]:
                return "severe"
            elif relationship_strength == "moderate":
                return "moderate"
            else:
                return "minor"
        elif scenario_name == "partial_degradation":
            if relationship_strength == "critical":
                return "moderate"
            elif relationship_strength in ["strong", "moderate"]:
                return "minor"
            else:
                return "negligible"
        else:
            return "unknown"
    
    def _estimate_downtime(self, dependent: DependencyNode, impact_level: str) -> int:
        """Estimate downtime in minutes based on asset and impact level"""
        base_downtime = {
            "severe": 240,    # 4 hours
            "moderate": 120,  # 2 hours  
            "minor": 30,      # 30 minutes
            "negligible": 5   # 5 minutes
        }
        
        downtime = base_downtime.get(impact_level, 60)
        
        # Adjust based on asset criticality
        if dependent.criticality == "critical":
            downtime *= 0.5  # Critical assets recover faster
        elif dependent.criticality == "low":
            downtime *= 2.0  # Low priority assets take longer
        
        return int(downtime)
    
    def _estimate_revenue_impact(self, dependent: DependencyNode, downtime_minutes: int) -> float:
        """Estimate revenue impact based on asset and downtime"""
        # Base revenue impact per hour by asset type
        hourly_impact = {
            "server": 10000,
            "database": 25000,
            "application": 15000,
            "cloud_service": 20000,
            "network_device": 5000
        }
        
        base_impact = hourly_impact.get(dependent.asset_type, 5000)
        
        # Adjust for criticality
        criticality_multiplier = {
            "critical": 3.0,
            "high": 2.0,
            "medium": 1.0,
            "low": 0.5
        }
        
        multiplier = criticality_multiplier.get(dependent.criticality, 1.0)
        
        return (base_impact * multiplier * downtime_minutes) / 60
    
    def _identify_affected_services(self, dependents: List[DependencyNode]) -> List[Dict[str, Any]]:
        """Identify services affected by dependent asset failures"""
        services = []
        
        for dependent in dependents:
            if dependent.asset_type in ["application", "cloud_service"]:
                services.append({
                    "service_name": f"{dependent.asset_name}_service",
                    "impact_level": "high" if dependent.criticality in ["critical", "high"] else "medium",
                    "affected_users": 1000 if dependent.criticality == "critical" else 100
                })
        
        return services
    
    def _generate_recovery_steps(self, asset: Asset, scenario_name: str, dep_graph: DependencyGraph) -> List[str]:
        """Generate recovery procedure steps"""
        steps = []
        
        if scenario_name == "complete_failure":
            steps.append(f"1. Isolate failed asset: {asset.name}")
            steps.append("2. Assess root cause of failure")
            steps.append("3. Activate backup systems if available")
            
            if dep_graph.total_dependents > 0:
                steps.append("4. Notify stakeholders of dependent service impacts")
                steps.append("5. Implement temporary workarounds for critical dependents")
            
            steps.append("6. Begin primary recovery procedures")
            steps.append("7. Test functionality before bringing back online")
            steps.append("8. Gradually restore dependent services")
            steps.append("9. Conduct post-incident review")
        
        return steps
    
    def _estimate_recovery_time(self, asset: Asset, scenario_name: str, affected_count: int) -> int:
        """Estimate total recovery time in minutes"""
        base_recovery = {
            "server": 120,      # 2 hours
            "database": 180,    # 3 hours
            "application": 60,  # 1 hour
            "cloud_service": 90, # 1.5 hours
            "network_device": 45 # 45 minutes
        }
        
        recovery_time = base_recovery.get(asset.asset_type.value, 90)
        
        # Add time for each affected asset
        recovery_time += affected_count * 15
        
        # Multiply for complete failure
        if scenario_name == "complete_failure":
            recovery_time *= 1.5
        
        return int(recovery_time)
    
    def _identify_business_functions(self, asset: Asset, affected_assets: List[Dict[str, Any]]) -> List[str]:
        """Identify affected business functions"""
        functions = set()
        
        # Based on asset business unit
        if asset.business_unit:
            functions.add(f"{asset.business_unit} Operations")
        
        # Based on environment
        if asset.environment == "production":
            functions.add("Customer Services")
            functions.add("Revenue Generation")
        
        # Based on affected assets
        for affected in affected_assets:
            if affected["impact_level"] in ["severe", "moderate"]:
                functions.add("IT Operations")
                if "database" in affected["asset_name"].lower():
                    functions.add("Data Management")
                if "web" in affected["asset_name"].lower():
                    functions.add("Web Services")
        
        return list(functions)
    
    def _calculate_scenario_probability(self, asset: Asset, scenario_name: str) -> float:
        """Calculate probability of scenario occurrence"""
        base_probability = {
            "complete_failure": 0.05,      # 5% annual probability
            "partial_degradation": 0.15,   # 15% annual probability
            "performance_impact": 0.30     # 30% annual probability
        }
        
        prob = base_probability.get(scenario_name, 0.10)
        
        # Adjust based on asset age and environment
        if asset.environment == "production":
            prob *= 0.8  # Production assets are better maintained
        elif asset.environment == "development":
            prob *= 1.5  # Development assets are less stable
        
        return min(prob, 1.0)
    
    def get_asset_network_map(self, asset_ids: List[int]) -> Dict[str, Any]:
        """Generate network map showing relationships between multiple assets"""
        
        nodes = []
        edges = []
        
        # Get all assets
        assets = self.db.query(Asset).filter(Asset.id.in_(asset_ids)).all()
        asset_map = {asset.id: asset for asset in assets}
        
        # Add nodes
        for asset in assets:
            nodes.append({
                "id": asset.id,
                "name": asset.name,
                "type": asset.asset_type.value,
                "criticality": asset.criticality.value,
                "environment": asset.environment,
                "group": asset.business_unit or "Unknown"
            })
        
        # Get relationships between these assets
        relationships = self.db.query(AssetRelationship).filter(
            AssetRelationship.source_asset_id.in_(asset_ids),
            AssetRelationship.target_asset_id.in_(asset_ids),
            AssetRelationship.is_active == True
        ).all()
        
        # Add edges
        for rel in relationships:
            edges.append({
                "source": rel.source_asset_id,
                "target": rel.target_asset_id,
                "type": rel.relationship_type.value,
                "strength": rel.relationship_strength.value,
                "description": rel.description or ""
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "network_density": len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
            }
        }