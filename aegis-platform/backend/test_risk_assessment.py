"""
Test suite for Risk Assessment Engine
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from risk_assessment_engine import RiskAssessmentEngine, RiskScoringMethod, RiskScore, RiskContext
from models.risk_register import RiskRegister, RiskLikelihood, RiskImpact, RiskCategory


class TestRiskAssessmentEngine:
    """Test cases for RiskAssessmentEngine class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.engine = RiskAssessmentEngine(self.mock_db)

    def test_engine_initialization(self):
        """Test that engine initializes correctly"""
        assert self.engine.db == self.mock_db
        assert len(self.engine.likelihood_scale) == 6
        assert len(self.engine.impact_scale) == 5
        assert len(self.engine.priority_thresholds) == 4
        assert "financial" in self.engine.industry_factors

    def test_simple_multiplication_method(self):
        """Test simple multiplication risk scoring method"""
        # Create mock risk
        mock_risk = Mock()
        mock_risk.id = 1
        mock_risk.inherent_likelihood = RiskLikelihood.MEDIUM
        mock_risk.inherent_impact = RiskImpact.MAJOR
        mock_risk.category = RiskCategory.SECURITY
        mock_risk.business_unit = "IT Security"
        mock_risk.process_area = "Security Operations"
        mock_risk.potential_financial_impact_max = None
        mock_risk.regulatory_requirements = ["GDPR", "SOX"]
        mock_risk.external_dependencies = []
        mock_risk.affected_assets = []
        mock_risk.controls = []
        mock_risk.last_review_date = datetime.now() - timedelta(days=30)
        mock_risk.description = "Test risk description for cybersecurity threats"
        
        # Mock database queries for historical data
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 1
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.engine.assess_risk(mock_risk, RiskScoringMethod.SIMPLE_MULTIPLICATION)
        
        assert isinstance(result, RiskScore)
        assert result.likelihood_score > 0
        assert result.impact_score > 0
        assert result.overall_score > 0
        assert result.priority in ["low", "medium", "high", "critical"]
        assert 0 <= result.confidence_level <= 1
        assert result.methodology_used == "simple_multiplication"

    def test_weighted_average_method(self):
        """Test weighted average risk scoring method"""
        mock_risk = Mock()
        mock_risk.id = 1
        mock_risk.inherent_likelihood = RiskLikelihood.HIGH
        mock_risk.inherent_impact = RiskImpact.SEVERE
        mock_risk.category = RiskCategory.OPERATIONAL
        mock_risk.business_unit = "Operations"
        mock_risk.process_area = "Core Business"
        mock_risk.potential_financial_impact_max = 1000000
        mock_risk.regulatory_requirements = ["SOX", "SOC2"]
        mock_risk.external_dependencies = ["Supplier A", "Supplier B"]
        mock_risk.affected_assets = [Mock(), Mock(), Mock()]  # 3 affected assets
        mock_risk.controls = [Mock()]
        mock_risk.last_review_date = datetime.now() - timedelta(days=15)
        mock_risk.description = "Major operational risk affecting core business processes"
        
        # Mock database queries
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        result = self.engine.assess_risk(mock_risk, RiskScoringMethod.WEIGHTED_AVERAGE)
        
        assert isinstance(result, RiskScore)
        assert result.overall_score > 5.0  # Should be high due to high likelihood and severe impact
        assert result.priority in ["high", "critical"]
        assert result.methodology_used == "weighted_average"
        assert "component_scores" in result.calculation_details

    def test_quantitative_method(self):
        """Test quantitative financial risk assessment method"""
        mock_risk = Mock()
        mock_risk.id = 1
        mock_risk.inherent_likelihood = RiskLikelihood.MEDIUM
        mock_risk.inherent_impact = RiskImpact.MAJOR
        mock_risk.category = RiskCategory.FINANCIAL
        mock_risk.potential_financial_impact_min = 500000
        mock_risk.potential_financial_impact_max = 2000000
        mock_risk.business_unit = "Finance"
        mock_risk.regulatory_requirements = []
        mock_risk.external_dependencies = []
        mock_risk.affected_assets = []
        mock_risk.controls = []
        mock_risk.last_review_date = datetime.now() - timedelta(days=45)
        mock_risk.description = "Financial risk with quantified impact"
        
        # Mock database queries
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        result = self.engine.assess_risk(mock_risk, RiskScoringMethod.QUANTITATIVE)
        
        assert isinstance(result, RiskScore)
        assert result.methodology_used == "quantitative"
        assert "expected_annual_loss" in result.calculation_details
        assert "max_acceptable_loss" in result.calculation_details
        assert result.calculation_details["min_financial_impact"] == 500000
        assert result.calculation_details["max_financial_impact"] == 2000000

    def test_expert_judgment_method(self):
        """Test expert judgment-based scoring method"""
        mock_risk = Mock()
        mock_risk.id = 1
        mock_risk.inherent_likelihood = RiskLikelihood.HIGH
        mock_risk.inherent_impact = RiskImpact.MODERATE
        mock_risk.category = RiskCategory.COMPLIANCE
        mock_risk.business_unit = "Legal"
        mock_risk.regulatory_requirements = ["GDPR", "CCPA", "SOX"]
        mock_risk.external_dependencies = []
        mock_risk.affected_assets = []
        mock_risk.controls = []
        mock_risk.last_review_date = datetime.now() - timedelta(days=60)
        mock_risk.description = "Compliance risk requiring expert assessment"
        
        # Mock latest assessment
        mock_assessment = Mock()
        mock_assessment.assessment_id = "ASSESS-2024-001"
        mock_assessment.likelihood_rating = RiskLikelihood.HIGH
        mock_assessment.impact_rating = RiskImpact.MODERATE
        mock_assessment.assessment_quality_score = 0.9
        mock_assessment.likelihood_rationale = "Strong rationale"
        mock_assessment.impact_rationale = "Strong rationale"
        mock_assessment.assessment_criteria = "ISO 31000"
        mock_assessment.data_sources = ["Historical data", "Expert opinion"]
        mock_assessment.is_validated = True
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_assessment
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        result = self.engine.assess_risk(mock_risk, RiskScoringMethod.EXPERT_JUDGMENT)
        
        assert isinstance(result, RiskScore)
        assert result.methodology_used == "expert_judgment"
        assert "assessment_id" in result.calculation_details
        assert result.calculation_details["assessment_id"] == "ASSESS-2024-001"
        assert "confidence_adjustment" in result.calculation_details

    def test_context_adjustments(self):
        """Test risk context adjustments"""
        mock_risk = Mock()
        mock_risk.category = RiskCategory.SECURITY
        mock_risk.business_unit = "IT Security"
        mock_risk.regulatory_requirements = ["GDPR", "SOX", "HIPAA", "PCI-DSS"]
        mock_risk.external_dependencies = ["Cloud Provider", "Security Vendor"]
        
        context = RiskContext(
            industry_sector="financial",
            regulatory_environment=["SEC", "FINRA", "OCC", "FDIC"],
            market_conditions="volatile",
            risk_appetite="low"
        )
        
        base_score = 5.0
        adjusted_score = self.engine._apply_context_adjustments(
            base_score, "likelihood", context, mock_risk
        )
        
        # Should be higher due to financial sector, high regulatory environment,
        # volatile market conditions, and low risk appetite
        assert adjusted_score > base_score

    def test_likelihood_score_calculation(self):
        """Test likelihood score calculation with adjustments"""
        mock_risk = Mock()
        mock_risk.category = RiskCategory.OPERATIONAL
        mock_risk.business_unit = "Operations"
        
        # Mock historical data
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 3
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        score = self.engine._calculate_likelihood_score(
            RiskLikelihood.MEDIUM, None, mock_risk
        )
        
        assert 0.1 <= score <= 10.0
        assert isinstance(score, float)

    def test_impact_score_calculation(self):
        """Test impact score calculation with adjustments"""
        mock_risk = Mock()
        mock_risk.category = RiskCategory.SECURITY
        mock_risk.business_unit = "Operations"
        mock_risk.process_area = "Core Business"
        mock_risk.affected_assets = [Mock(), Mock()]  # 2 affected assets
        
        context = RiskContext(business_unit="Operations")
        
        score = self.engine._calculate_impact_score(
            RiskImpact.MAJOR, context, mock_risk
        )
        
        assert 0.1 <= score <= 10.0
        assert isinstance(score, float)

    def test_financial_impact_scoring(self):
        """Test financial impact component scoring"""
        # Test different financial impact ranges
        test_cases = [
            (5000, 2.0),      # < $10K
            (50000, 4.0),     # < $100K
            (500000, 6.0),    # < $1M
            (5000000, 8.0),   # < $10M
            (50000000, 10.0)  # >= $10M
        ]
        
        for impact_amount, expected_score in test_cases:
            mock_risk = Mock()
            mock_risk.potential_financial_impact_max = impact_amount
            mock_risk.inherent_impact = RiskImpact.MODERATE
            
            score = self.engine._calculate_financial_impact_score(mock_risk)
            assert score == expected_score

    def test_operational_impact_scoring(self):
        """Test operational impact component scoring"""
        mock_risk = Mock()
        mock_risk.inherent_impact = RiskImpact.MAJOR
        mock_risk.business_unit = "Operations"  # Critical unit
        mock_risk.process_area = "Core Business"  # Critical process
        
        score = self.engine._calculate_operational_impact_score(mock_risk)
        
        # Should be higher than base due to critical business unit and process
        base_score = self.engine.impact_scale[RiskImpact.MAJOR]["typical"]
        assert score > base_score

    def test_reputational_impact_scoring(self):
        """Test reputational impact component scoring"""
        mock_risk = Mock()
        mock_risk.inherent_impact = RiskImpact.MAJOR
        mock_risk.category = RiskCategory.SECURITY  # High reputation impact category
        mock_risk.geographic_scope = "Global"  # Global scope increases impact
        
        score = self.engine._calculate_reputational_impact_score(mock_risk)
        
        # Should be higher than base due to security category and global scope
        base_score = self.engine.impact_scale[RiskImpact.MAJOR]["typical"]
        assert score > base_score

    def test_compliance_impact_scoring(self):
        """Test compliance impact component scoring"""
        mock_risk = Mock()
        mock_risk.inherent_impact = RiskImpact.MODERATE
        mock_risk.category = RiskCategory.COMPLIANCE
        mock_risk.regulatory_requirements = ["GDPR", "SOX", "HIPAA", "PCI-DSS"]  # 4 requirements
        
        score = self.engine._calculate_compliance_impact_score(mock_risk)
        
        # Should be significantly higher due to compliance category and multiple regulations
        base_score = self.engine.impact_scale[RiskImpact.MODERATE]["typical"]
        assert score > base_score * 1.5

    def test_priority_determination(self):
        """Test priority level determination from scores"""
        test_cases = [
            (1.0, "low"),
            (3.0, "medium"),
            (6.0, "high"),
            (8.5, "critical"),
            (10.0, "critical")
        ]
        
        for score, expected_priority in test_cases:
            priority = self.engine._determine_priority(score)
            assert priority == expected_priority

    def test_confidence_level_calculation(self):
        """Test confidence level calculation"""
        mock_risk = Mock()
        mock_risk.description = "This is a detailed description with more than fifty characters to meet the requirement"
        mock_risk.last_review_date = datetime.now() - timedelta(days=60)  # Within 90 days
        mock_risk.potential_financial_impact_max = 1000000
        mock_risk.controls = [Mock(), Mock(), Mock()]  # 3 controls
        
        context = RiskContext(industry_sector="financial")
        
        confidence = self.engine._calculate_confidence_level(mock_risk, context)
        
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)

    def test_residual_risk_calculation(self):
        """Test residual risk calculation"""
        mock_risk = Mock()
        mock_risk.id = 1
        mock_risk.title = "Test Risk"
        mock_risk.description = "Test Description"
        mock_risk.category = RiskCategory.OPERATIONAL
        mock_risk.inherent_likelihood = RiskLikelihood.HIGH
        mock_risk.inherent_impact = RiskImpact.MAJOR
        mock_risk.residual_likelihood = RiskLikelihood.MEDIUM
        mock_risk.residual_impact = RiskImpact.MODERATE
        mock_risk.business_unit = "Operations"
        mock_risk.process_area = None
        mock_risk.potential_financial_impact_min = None
        mock_risk.potential_financial_impact_max = None
        mock_risk.regulatory_requirements = []
        mock_risk.external_dependencies = []
        
        # Mock database queries
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        result = self.engine.calculate_residual_risk(mock_risk)
        
        assert isinstance(result, RiskScore)
        assert "residual_" in result.methodology_used

    def test_risk_comparison(self):
        """Test risk comparison functionality"""
        mock_risk1 = Mock()
        mock_risk1.id = 1
        mock_risk1.title = "High Risk"
        mock_risk1.inherent_likelihood = RiskLikelihood.HIGH
        mock_risk1.inherent_impact = RiskImpact.SEVERE
        mock_risk1.category = RiskCategory.SECURITY
        mock_risk1.business_unit = "IT"
        mock_risk1.process_area = None
        mock_risk1.potential_financial_impact_max = None
        mock_risk1.regulatory_requirements = []
        mock_risk1.external_dependencies = []
        mock_risk1.affected_assets = []
        mock_risk1.controls = []
        mock_risk1.last_review_date = datetime.now()
        mock_risk1.description = "High severity security risk"
        
        mock_risk2 = Mock()
        mock_risk2.id = 2
        mock_risk2.title = "Medium Risk"
        mock_risk2.inherent_likelihood = RiskLikelihood.MEDIUM
        mock_risk2.inherent_impact = RiskImpact.MODERATE
        mock_risk2.category = RiskCategory.OPERATIONAL
        mock_risk2.business_unit = "Operations"
        mock_risk2.process_area = None
        mock_risk2.potential_financial_impact_max = None
        mock_risk2.regulatory_requirements = []
        mock_risk2.external_dependencies = []
        mock_risk2.affected_assets = []
        mock_risk2.controls = []
        mock_risk2.last_review_date = datetime.now()
        mock_risk2.description = "Moderate operational risk"
        
        # Mock database queries
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        comparison = self.engine.compare_risk_scores(mock_risk1, mock_risk2)
        
        assert "risk1" in comparison
        assert "risk2" in comparison
        assert "comparison" in comparison
        assert comparison["comparison"]["higher_risk"] == "risk1"  # High/Severe should be higher than Medium/Moderate

    def test_bulk_risk_assessment(self):
        """Test bulk risk assessment functionality"""
        # Mock risks
        mock_risks = [
            Mock(
                id=1, inherent_likelihood=RiskLikelihood.HIGH, inherent_impact=RiskImpact.MAJOR,
                category=RiskCategory.SECURITY, business_unit="IT", process_area=None,
                potential_financial_impact_max=None, regulatory_requirements=[],
                external_dependencies=[], affected_assets=[], controls=[],
                last_review_date=datetime.now(), description="Security risk 1"
            ),
            Mock(
                id=2, inherent_likelihood=RiskLikelihood.MEDIUM, inherent_impact=RiskImpact.MODERATE,
                category=RiskCategory.OPERATIONAL, business_unit="Ops", process_area=None,
                potential_financial_impact_max=None, regulatory_requirements=[],
                external_dependencies=[], affected_assets=[], controls=[],
                last_review_date=datetime.now(), description="Operational risk 2"
            )
        ]
        
        # Mock database queries
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_risks
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        results = self.engine.bulk_assess_risks([1, 2])
        
        assert len(results) == 2
        assert 1 in results
        assert 2 in results
        assert isinstance(results[1], RiskScore)
        assert isinstance(results[2], RiskScore)

    def test_historical_likelihood_adjustment(self):
        """Test historical likelihood adjustment calculation"""
        mock_risk = Mock()
        mock_risk.category = RiskCategory.SECURITY
        mock_risk.business_unit = "IT Security"
        
        # Test case: many historical incidents
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 6
        adjustment = self.engine._get_historical_likelihood_adjustment(mock_risk)
        assert adjustment == 0.3  # 30% increase
        
        # Test case: no historical incidents
        self.mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        adjustment = self.engine._get_historical_likelihood_adjustment(mock_risk)
        assert adjustment == -0.1  # 10% decrease

    def test_trend_adjustment(self):
        """Test trend adjustment calculation"""
        mock_risk = Mock()
        mock_risk.id = 1
        
        # Test with insufficient data
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        adjustment = self.engine._get_trend_adjustment(mock_risk, "likelihood")
        assert adjustment == 0.0
        
        # Test with trend data (would need more complex mocking for full test)
        mock_assessments = [
            Mock(likelihood_rating=RiskLikelihood.HIGH),
            Mock(likelihood_rating=RiskLikelihood.MEDIUM)
        ]
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_assessments
        adjustment = self.engine._get_trend_adjustment(mock_risk, "likelihood")
        assert -0.2 <= adjustment <= 0.2  # Within expected range

    def test_priority_comparison(self):
        """Test priority comparison utility"""
        comparison = self.engine._compare_priorities("high", "medium")
        assert "high > medium" in comparison
        
        comparison = self.engine._compare_priorities("low", "critical")
        assert "critical > low" in comparison
        
        comparison = self.engine._compare_priorities("medium", "medium")
        assert "medium = medium" in comparison


if __name__ == "__main__":
    # Run basic functionality tests
    print("Running Risk Assessment Engine Tests...")
    
    # Test 1: Engine initialization
    mock_db = Mock()
    engine = RiskAssessmentEngine(mock_db)
    print("✓ RiskAssessmentEngine initialized successfully")
    
    # Test 2: Basic risk assessment
    mock_risk = Mock()
    mock_risk.id = 1
    mock_risk.inherent_likelihood = RiskLikelihood.MEDIUM
    mock_risk.inherent_impact = RiskImpact.MAJOR
    mock_risk.category = RiskCategory.SECURITY
    mock_risk.business_unit = "IT"
    mock_risk.process_area = None
    mock_risk.potential_financial_impact_max = None
    mock_risk.regulatory_requirements = []
    mock_risk.external_dependencies = []
    mock_risk.affected_assets = []
    mock_risk.controls = []
    mock_risk.last_review_date = datetime.now()
    mock_risk.description = "Test risk for basic assessment"
    
    # Mock database queries
    mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 1
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    result = engine.assess_risk(mock_risk, RiskScoringMethod.SIMPLE_MULTIPLICATION)
    assert isinstance(result, RiskScore)
    print("✓ Basic risk assessment working correctly")
    
    # Test 3: Priority determination
    priority = engine._determine_priority(7.5)
    assert priority == "high"
    print("✓ Priority determination working correctly")
    
    # Test 4: Context adjustments
    context = RiskContext(industry_sector="financial")
    adjusted_score = engine._apply_context_adjustments(5.0, "likelihood", context, mock_risk)
    assert adjusted_score >= 5.0  # Should be adjusted upward for financial sector
    print("✓ Context adjustments working correctly")
    
    # Test 5: Financial impact scoring
    mock_risk.potential_financial_impact_max = 1000000
    score = engine._calculate_financial_impact_score(mock_risk)
    assert score == 6.0  # Should be 6.0 for $1M impact
    print("✓ Financial impact scoring working correctly")
    
    print("\n🎉 All basic tests passed! Risk assessment engine is working correctly.")