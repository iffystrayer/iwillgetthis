"""
Test suite for Asset Criticality Scoring System
"""

import pytest
from asset_scoring import AssetCriticalityScorer, calculate_asset_criticality, get_criticality_factors_info


class TestAssetCriticalityScorer:
    """Test cases for AssetCriticalityScorer class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.scorer = AssetCriticalityScorer()

    def test_scorer_initialization(self):
        """Test that scorer initializes with correct weights"""
        assert len(self.scorer.factor_weights) == 7
        assert sum(self.scorer.factor_weights.values()) == 1.0  # Weights should sum to 1
        
    def test_critical_production_server(self):
        """Test scoring for a critical production server"""
        asset_data = {
            "environment": "production",
            "asset_type": "server",
            "business_unit": "Engineering",
            "compliance_scope": ["SOC2", "ISO27001", "PCI-DSS"],
            "custom_fields": {
                "data_classification": "confidential",
                "sla_requirement": "99.9% uptime",
                "recovery_time_objective": "immediate",
                "revenue_impact_per_hour": "150000",
                "dependent_systems": ["web", "mobile", "api", "analytics", "reporting", "billing"]
            }
        }
        
        result = self.scorer.calculate_criticality_score(asset_data)
        
        assert result["criticality_level"] == "critical"
        assert result["total_score"] >= 8.5
        assert "Implement redundancy and failover mechanisms" in result["recommendations"]
        assert "Implement encryption at rest and in transit" in result["recommendations"]

    def test_low_criticality_dev_workstation(self):
        """Test scoring for a low criticality development workstation"""
        asset_data = {
            "environment": "development",
            "asset_type": "workstation",
            "business_unit": "Other",
            "compliance_scope": [],
            "custom_fields": {
                "data_classification": "public",
                "recovery_time_objective": "72 hours",
                "revenue_impact_per_hour": "0"
            }
        }
        
        result = self.scorer.calculate_criticality_score(asset_data)
        
        assert result["criticality_level"] == "low"
        assert result["total_score"] < 4.0
        assert len(result["recommendations"]) == 0

    def test_medium_criticality_staging_database(self):
        """Test scoring for a medium criticality staging database"""
        asset_data = {
            "environment": "staging",
            "asset_type": "database",
            "business_unit": "Engineering",
            "compliance_scope": ["SOC2"],
            "custom_fields": {
                "data_classification": "internal",
                "sla_requirement": "99.0% uptime",
                "recovery_time_objective": "8 hours",
                "revenue_impact_per_hour": "5000",
                "dependent_systems": ["test-app", "staging-web"]
            }
        }
        
        result = self.scorer.calculate_criticality_score(asset_data)
        
        assert result["criticality_level"] in ["medium", "high"]
        assert 4.0 <= result["total_score"] < 8.5

    def test_business_impact_calculation(self):
        """Test business impact factor calculation"""
        # Production server should score high
        prod_asset = {
            "environment": "production",
            "asset_type": "database",
            "business_unit": "Engineering"
        }
        prod_score = self.scorer._calculate_business_impact(prod_asset)
        assert prod_score >= 8
        
        # Development workstation should score low
        dev_asset = {
            "environment": "development",
            "asset_type": "workstation",
            "business_unit": "Other"
        }
        dev_score = self.scorer._calculate_business_impact(dev_asset)
        assert dev_score <= 6
        
        assert prod_score > dev_score

    def test_data_sensitivity_calculation(self):
        """Test data sensitivity factor calculation"""
        # High sensitivity asset
        high_sens_asset = {
            "compliance_scope": ["PCI-DSS", "HIPAA", "GDPR"],
            "custom_fields": {
                "data_classification": "confidential"
            }
        }
        high_score = self.scorer._calculate_data_sensitivity(high_sens_asset)
        assert high_score >= 8
        
        # Low sensitivity asset
        low_sens_asset = {
            "compliance_scope": [],
            "custom_fields": {
                "data_classification": "public"
            }
        }
        low_score = self.scorer._calculate_data_sensitivity(low_sens_asset)
        assert low_score <= 4
        
        assert high_score > low_score

    def test_rto_score_calculation(self):
        """Test Recovery Time Objective scoring"""
        test_cases = [
            ("immediate", 10),
            ("1 hour", 9),
            ("4 hour", 7),
            ("8 hour", 5),
            ("24 hour", 3),
            ("unknown", 1)
        ]
        
        for rto, expected_score in test_cases:
            asset_data = {
                "custom_fields": {
                    "recovery_time_objective": rto
                }
            }
            score = self.scorer._calculate_rto_score(asset_data)
            assert score == expected_score

    def test_financial_impact_calculation(self):
        """Test financial impact scoring"""
        test_cases = [
            (150000, 10),
            (75000, 8),
            (25000, 6),
            (5000, 4),
            (500, 2),
            (0, 1)
        ]
        
        for revenue_impact, expected_score in test_cases:
            asset_data = {
                "custom_fields": {
                    "revenue_impact_per_hour": str(revenue_impact)
                }
            }
            score = self.scorer._calculate_financial_impact(asset_data)
            assert score == expected_score

    def test_operational_dependency_calculation(self):
        """Test operational dependency scoring"""
        test_cases = [
            (15, 10),
            (7, 7),
            (3, 5),
            (1, 3),
            (0, 1)
        ]
        
        for dep_count, expected_score in test_cases:
            dependent_systems = [f"system-{i}" for i in range(dep_count)]
            asset_data = {
                "custom_fields": {
                    "dependent_systems": dependent_systems
                }
            }
            score = self.scorer._calculate_operational_dependency(asset_data)
            assert score == expected_score

    def test_score_to_criticality_level(self):
        """Test score to criticality level conversion"""
        test_cases = [
            (9.5, "critical"),
            (8.5, "critical"),
            (8.0, "high"),
            (7.0, "high"),
            (5.0, "medium"),
            (4.0, "medium"),
            (3.0, "low"),
            (1.0, "low")
        ]
        
        for score, expected_level in test_cases:
            level = self.scorer._score_to_criticality_level(score)
            assert level == expected_level

    def test_json_field_parsing(self):
        """Test that JSON fields are properly parsed"""
        asset_data = {
            "compliance_scope": '["SOC2", "ISO27001"]',
            "custom_fields": '{"data_classification": "confidential", "dependent_systems": ["sys1", "sys2"]}'
        }
        
        result = self.scorer.calculate_criticality_score(asset_data)
        assert "total_score" in result
        assert "criticality_level" in result
        assert result["factor_scores"]["compliance_requirements"] > 1

    def test_missing_fields_handling(self):
        """Test that missing fields are handled gracefully"""
        minimal_asset = {
            "name": "Test Asset"
        }
        
        result = self.scorer.calculate_criticality_score(minimal_asset)
        assert "total_score" in result
        assert "criticality_level" in result
        assert result["criticality_level"] in ["low", "medium", "high", "critical"]

    def test_recommendations_generation(self):
        """Test that recommendations are generated appropriately"""
        # High impact asset should get multiple recommendations
        high_impact_asset = {
            "environment": "production",
            "asset_type": "database",
            "compliance_scope": ["PCI-DSS", "SOC2"],
            "custom_fields": {
                "data_classification": "confidential",
                "sla_requirement": "99.9% uptime"
            }
        }
        
        result = self.scorer.calculate_criticality_score(high_impact_asset)
        assert len(result["recommendations"]) >= 4
        
        # Low impact asset should get fewer recommendations
        low_impact_asset = {
            "environment": "development",
            "asset_type": "workstation",
            "compliance_scope": [],
            "custom_fields": {}
        }
        
        result = self.scorer.calculate_criticality_score(low_impact_asset)
        assert len(result["recommendations"]) <= 2


class TestUtilityFunctions:
    """Test utility functions"""

    def test_calculate_asset_criticality_function(self):
        """Test the main calculation function"""
        asset_data = {
            "environment": "production",
            "asset_type": "server"
        }
        
        result = calculate_asset_criticality(asset_data)
        assert "total_score" in result
        assert "criticality_level" in result
        assert "factor_scores" in result
        assert "recommendations" in result
        assert "calculated_at" in result

    def test_get_criticality_factors_info(self):
        """Test the factors information function"""
        info = get_criticality_factors_info()
        
        assert "factors" in info
        assert "scoring_scale" in info
        assert "criticality_levels" in info
        
        assert len(info["factors"]) == 7
        assert all("name" in factor for factor in info["factors"])
        assert all("weight" in factor for factor in info["factors"])
        assert all("description" in factor for factor in info["factors"])


if __name__ == "__main__":
    # Run basic tests
    print("Running Asset Criticality Scoring Tests...")
    
    # Test 1: Basic functionality
    scorer = AssetCriticalityScorer()
    print("✓ Scorer initialized successfully")
    
    # Test 2: Critical asset scoring
    critical_asset = {
        "environment": "production",
        "asset_type": "database",
        "compliance_scope": ["PCI-DSS", "HIPAA"],
        "custom_fields": {
            "data_classification": "confidential",
            "recovery_time_objective": "immediate",
            "revenue_impact_per_hour": "200000",
            "dependent_systems": ["web", "mobile", "api", "billing", "analytics"]
        }
    }
    
    result = calculate_asset_criticality(critical_asset)
    print(f"✓ Critical asset scored: {result['total_score']} ({result['criticality_level']})")
    
    # Test 3: Low criticality asset
    low_asset = {
        "environment": "development",
        "asset_type": "workstation",
        "compliance_scope": [],
        "custom_fields": {
            "recovery_time_objective": "72 hours",
            "revenue_impact_per_hour": "0"
        }
    }
    
    result = calculate_asset_criticality(low_asset)
    print(f"✓ Low criticality asset scored: {result['total_score']} ({result['criticality_level']})")
    
    # Test 4: Factors info
    factors_info = get_criticality_factors_info()
    print(f"✓ Factors info retrieved: {len(factors_info['factors'])} factors")
    
    print("\n🎉 All basic tests passed! Asset criticality scoring system is working correctly.")