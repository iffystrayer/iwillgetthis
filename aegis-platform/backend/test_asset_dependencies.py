"""
Test suite for Asset Dependencies and Relationships System
"""

import pytest
from unittest.mock import Mock, MagicMock
from asset_dependency_analyzer import AssetDependencyAnalyzer
from models.asset_relationship import RelationshipType, RelationshipStrength


class TestAssetDependencyAnalyzer:
    """Test cases for AssetDependencyAnalyzer class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.analyzer = AssetDependencyAnalyzer(self.mock_db)

    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        assert self.analyzer.db == self.mock_db
        assert len(self.analyzer.relationship_weights) == 4
        assert self.analyzer.relationship_weights[RelationshipStrength.CRITICAL] == 1.0
        assert self.analyzer.relationship_weights[RelationshipStrength.WEAK] == 0.25

    def test_calculate_risk_metrics(self):
        """Test risk metrics calculation"""
        # Mock relationships
        mock_incoming_rels = [
            Mock(relationship_strength=RelationshipStrength.CRITICAL),
            Mock(relationship_strength=RelationshipStrength.STRONG),
        ]
        mock_outgoing_rels = [
            Mock(relationship_strength=RelationshipStrength.MODERATE),
            Mock(relationship_strength=RelationshipStrength.WEAK),
        ]
        
        # Mock database queries
        self.mock_db.query.return_value.filter.return_value.all.side_effect = [
            mock_incoming_rels, mock_outgoing_rels
        ]
        
        result = self.analyzer.calculate_risk_metrics(1)
        
        assert "single_point_of_failure_risk" in result
        assert "cascade_failure_risk" in result
        assert "overall_dependency_risk" in result
        assert 0 <= result["single_point_of_failure_risk"] <= 1
        assert 0 <= result["cascade_failure_risk"] <= 1
        assert 0 <= result["overall_dependency_risk"] <= 1

    def test_spof_risk_calculation(self):
        """Test single point of failure risk calculation"""
        # No dependencies = low risk
        result = self.analyzer._calculate_spof_risk(1, [])
        assert result == 0.0
        
        # Critical dependencies = high risk
        critical_rels = [
            Mock(relationship_strength=RelationshipStrength.CRITICAL, relationship_type=RelationshipType.DEPENDS_ON),
            Mock(relationship_strength=RelationshipStrength.CRITICAL, relationship_type=RelationshipType.DEPENDS_ON),
        ]
        result = self.analyzer._calculate_spof_risk(1, critical_rels)
        assert result > 0.3  # Should be significant risk

    def test_cascade_risk_calculation(self):
        """Test cascade failure risk calculation"""
        # No outgoing relationships = no cascade risk
        result = self.analyzer._calculate_cascade_risk(1, [])
        assert result == 0.0
        
        # Multiple strong relationships = higher cascade risk
        strong_rels = [
            Mock(relationship_strength=RelationshipStrength.STRONG),
            Mock(relationship_strength=RelationshipStrength.CRITICAL),
        ]
        result = self.analyzer._calculate_cascade_risk(1, strong_rels)
        assert result > 0.05  # Should have some risk

    def test_determine_impact_level(self):
        """Test impact level determination logic"""
        # Complete failure scenarios
        assert self.analyzer._determine_impact_level("critical", "complete_failure") == "severe"
        assert self.analyzer._determine_impact_level("strong", "complete_failure") == "severe"
        assert self.analyzer._determine_impact_level("moderate", "complete_failure") == "moderate"
        assert self.analyzer._determine_impact_level("weak", "complete_failure") == "minor"
        
        # Partial degradation scenarios
        assert self.analyzer._determine_impact_level("critical", "partial_degradation") == "moderate"
        assert self.analyzer._determine_impact_level("moderate", "partial_degradation") == "minor"

    def test_estimate_downtime(self):
        """Test downtime estimation logic"""
        # Create mock dependent node
        dependent = Mock()
        dependent.criticality = "critical"
        
        # Severe impact should result in significant downtime
        downtime = self.analyzer._estimate_downtime(dependent, "severe")
        assert downtime > 100  # Should be more than 100 minutes
        
        # Critical assets should recover faster
        dependent.criticality = "critical"
        critical_downtime = self.analyzer._estimate_downtime(dependent, "severe")
        
        dependent.criticality = "low"
        low_downtime = self.analyzer._estimate_downtime(dependent, "severe")
        
        assert critical_downtime < low_downtime  # Critical assets recover faster

    def test_estimate_revenue_impact(self):
        """Test revenue impact estimation"""
        # Create mock dependent node
        dependent = Mock()
        dependent.asset_type = "database"
        dependent.criticality = "critical"
        
        # Database with critical rating should have high impact
        impact = self.analyzer._estimate_revenue_impact(dependent, 120)  # 2 hours
        assert impact > 10000  # Should be significant revenue impact
        
        # Lower criticality should have lower impact
        dependent.criticality = "low"
        low_impact = self.analyzer._estimate_revenue_impact(dependent, 120)
        assert low_impact < impact

    def test_generate_recovery_steps(self):
        """Test recovery steps generation"""
        mock_asset = Mock()
        mock_asset.name = "Test Server"
        
        mock_dep_graph = Mock()
        mock_dep_graph.total_dependents = 3
        
        steps = self.analyzer._generate_recovery_steps(mock_asset, "complete_failure", mock_dep_graph)
        
        assert len(steps) >= 6  # Should have multiple steps
        assert "Test Server" in steps[0]  # Should mention asset name
        assert any("backup" in step.lower() for step in steps)  # Should mention backups
        assert any("dependent" in step.lower() for step in steps)  # Should mention dependents

    def test_estimate_recovery_time(self):
        """Test recovery time estimation"""
        mock_asset = Mock()
        mock_asset.asset_type.value = "database"
        
        # Database should take longer than basic server
        db_time = self.analyzer._estimate_recovery_time(mock_asset, "complete_failure", 5)
        
        mock_asset.asset_type.value = "workstation"
        ws_time = self.analyzer._estimate_recovery_time(mock_asset, "complete_failure", 5)
        
        assert db_time > ws_time  # Database should take longer
        
        # Complete failure should take longer than partial
        complete_time = self.analyzer._estimate_recovery_time(mock_asset, "complete_failure", 1)
        partial_time = self.analyzer._estimate_recovery_time(mock_asset, "partial_degradation", 1)
        
        assert complete_time > partial_time

    def test_identify_business_functions(self):
        """Test business function identification"""
        mock_asset = Mock()
        mock_asset.business_unit = "Engineering"
        mock_asset.environment = "production"
        
        affected_assets = [
            {"asset_name": "database-server", "impact_level": "severe"},
            {"asset_name": "web-frontend", "impact_level": "moderate"}
        ]
        
        functions = self.analyzer._identify_business_functions(mock_asset, affected_assets)
        
        assert "Engineering Operations" in functions
        assert "Customer Services" in functions  # Production environment
        assert "Data Management" in functions    # Database asset affected
        assert "Web Services" in functions       # Web asset affected

    def test_calculate_scenario_probability(self):
        """Test scenario probability calculation"""
        mock_asset = Mock()
        mock_asset.environment = "production"
        
        # Production should have lower probability than development
        prod_prob = self.analyzer._calculate_scenario_probability(mock_asset, "complete_failure")
        
        mock_asset.environment = "development"
        dev_prob = self.analyzer._calculate_scenario_probability(mock_asset, "complete_failure")
        
        assert prod_prob < dev_prob  # Production should be more stable
        assert 0 <= prod_prob <= 1   # Should be valid probability
        assert 0 <= dev_prob <= 1    # Should be valid probability

    def test_get_asset_network_map_structure(self):
        """Test network map structure and format"""
        # Mock assets
        mock_assets = [
            Mock(id=1, name="Server 1", asset_type=Mock(value="server"), 
                 criticality=Mock(value="high"), environment="production", business_unit="IT"),
            Mock(id=2, name="Database 1", asset_type=Mock(value="database"), 
                 criticality=Mock(value="critical"), environment="production", business_unit="IT")
        ]
        
        # Mock relationships
        mock_rels = [
            Mock(source_asset_id=1, target_asset_id=2, 
                 relationship_type=Mock(value="depends_on"),
                 relationship_strength=Mock(value="critical"),
                 description="Database connection")
        ]
        
        # Setup mock database queries
        self.mock_db.query.return_value.filter.return_value.all.side_effect = [
            mock_assets, mock_rels
        ]
        
        result = self.analyzer.get_asset_network_map([1, 2])
        
        # Verify structure
        assert "nodes" in result
        assert "edges" in result
        assert "statistics" in result
        
        # Verify nodes
        assert len(result["nodes"]) == 2
        node = result["nodes"][0]
        assert all(key in node for key in ["id", "name", "type", "criticality", "environment", "group"])
        
        # Verify edges
        assert len(result["edges"]) == 1
        edge = result["edges"][0]
        assert all(key in edge for key in ["source", "target", "type", "strength"])
        
        # Verify statistics
        stats = result["statistics"]
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "network_density" in stats


class TestAssetRelationshipModels:
    """Test the relationship data models and validation"""

    def test_relationship_type_enum(self):
        """Test relationship type enumeration"""
        assert RelationshipType.DEPENDS_ON.value == "depends_on"
        assert RelationshipType.HOSTS.value == "hosts"
        assert RelationshipType.COMMUNICATES_WITH.value == "communicates_with"

    def test_relationship_strength_enum(self):
        """Test relationship strength enumeration"""
        assert RelationshipStrength.WEAK.value == "weak"
        assert RelationshipStrength.MODERATE.value == "moderate"
        assert RelationshipStrength.STRONG.value == "strong"
        assert RelationshipStrength.CRITICAL.value == "critical"


class TestImpactAnalysisIntegration:
    """Integration tests for impact analysis functionality"""

    def setup_method(self):
        """Set up integration test fixtures"""
        self.mock_db = Mock()
        self.analyzer = AssetDependencyAnalyzer(self.mock_db)

    def test_analyze_impact_scenario_integration(self):
        """Test complete impact analysis scenario"""
        # Mock asset
        mock_asset = Mock()
        mock_asset.id = 1
        mock_asset.name = "Critical Server"
        mock_asset.asset_type.value = "server"
        mock_asset.environment = "production"
        mock_asset.business_unit = "Engineering"
        
        # Mock the database query for the asset
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_asset
        
        # Mock dependency graph (simplified)
        mock_dep_graph = Mock()
        mock_dep_graph.dependents = [
            Mock(asset_id=2, asset_name="Dependent App", asset_type="application",
                 criticality="high", environment="production", 
                 relationship_strength="critical", impact_percentage=80.0)
        ]
        mock_dep_graph.total_dependents = 1
        
        # Mock the build_dependency_graph method
        self.analyzer.build_dependency_graph = Mock(return_value=mock_dep_graph)
        
        # Run impact analysis
        result = self.analyzer.analyze_impact_scenario(1, "complete_failure")
        
        # Verify results
        assert result.asset_id == 1
        assert result.asset_name == "Critical Server"
        assert result.scenario_name == "complete_failure"
        assert len(result.affected_assets) == 1
        assert result.estimated_downtime_minutes > 0
        assert result.estimated_revenue_impact > 0
        assert len(result.recovery_steps) > 0
        assert 0 <= result.scenario_probability <= 1


if __name__ == "__main__":
    # Run basic functionality tests
    print("Running Asset Dependencies and Relationships Tests...")
    
    # Test 1: Analyzer initialization
    mock_db = Mock()
    analyzer = AssetDependencyAnalyzer(mock_db)
    print("✓ AssetDependencyAnalyzer initialized successfully")
    
    # Test 2: Risk calculation structure
    mock_db.query.return_value.filter.return_value.all.return_value = []
    risk_metrics = analyzer.calculate_risk_metrics(1)
    assert all(key in risk_metrics for key in ["single_point_of_failure_risk", "cascade_failure_risk", "overall_dependency_risk"])
    print("✓ Risk metrics calculation structure correct")
    
    # Test 3: Impact level determination
    impact_severe = analyzer._determine_impact_level("critical", "complete_failure")
    impact_minor = analyzer._determine_impact_level("weak", "complete_failure")
    assert impact_severe == "severe"
    assert impact_minor == "minor"
    print("✓ Impact level determination working correctly")
    
    # Test 4: Recovery time estimation
    mock_asset = Mock()
    mock_asset.asset_type.value = "database"
    recovery_time = analyzer._estimate_recovery_time(mock_asset, "complete_failure", 3)
    assert recovery_time > 0
    print(f"✓ Recovery time estimation: {recovery_time} minutes")
    
    # Test 5: Business function identification
    mock_asset.business_unit = "Engineering"
    mock_asset.environment = "production"
    affected = [{"asset_name": "database-server", "impact_level": "severe"}]
    functions = analyzer._identify_business_functions(mock_asset, affected)
    assert len(functions) > 0
    print(f"✓ Business functions identified: {len(functions)} functions")
    
    print("\n🎉 All basic tests passed! Asset dependency system is working correctly.")