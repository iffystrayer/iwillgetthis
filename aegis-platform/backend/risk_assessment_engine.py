"""
Risk Assessment and Scoring Engine
Advanced algorithms for risk evaluation, prioritization, and analysis
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import math
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from models.risk_register import (
    RiskRegister, RiskLikelihood, RiskImpact, RiskPriority, 
    RiskCategory, RiskRegisterMatrix, RiskAssessment, RiskControl
)


class RiskScoringMethod(Enum):
    """Risk scoring methodologies"""
    SIMPLE_MULTIPLICATION = "simple_multiplication"  # Likelihood × Impact
    WEIGHTED_AVERAGE = "weighted_average"            # Weighted factors
    MONTE_CARLO = "monte_carlo"                      # Probabilistic simulation
    EXPERT_JUDGMENT = "expert_judgment"              # Expert-based scoring
    QUANTITATIVE = "quantitative"                    # Financial quantification


@dataclass
class RiskScore:
    """Risk score result"""
    likelihood_score: float
    impact_score: float
    overall_score: float
    priority: str
    confidence_level: float
    methodology_used: str
    calculation_details: Dict[str, Any]


@dataclass
class RiskContext:
    """Context for risk assessment"""
    business_unit: Optional[str] = None
    industry_sector: Optional[str] = None
    regulatory_environment: List[str] = None
    market_conditions: Optional[str] = None
    organizational_maturity: Optional[str] = None
    risk_appetite: Optional[str] = None


class RiskAssessmentEngine:
    """Comprehensive risk assessment and scoring engine"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Default likelihood scale (probability percentages)
        self.likelihood_scale = {
            RiskLikelihood.VERY_LOW: {"min": 0.01, "max": 0.05, "typical": 0.03},
            RiskLikelihood.LOW: {"min": 0.06, "max": 0.25, "typical": 0.15},
            RiskLikelihood.MEDIUM: {"min": 0.26, "max": 0.50, "typical": 0.35},
            RiskLikelihood.HIGH: {"min": 0.51, "max": 0.75, "typical": 0.65},
            RiskLikelihood.VERY_HIGH: {"min": 0.76, "max": 0.95, "typical": 0.85},
            RiskLikelihood.CERTAIN: {"min": 0.96, "max": 1.00, "typical": 0.98}
        }
        
        # Default impact scale (normalized 1-10)
        self.impact_scale = {
            RiskImpact.NEGLIGIBLE: {"min": 1.0, "max": 2.0, "typical": 1.5},
            RiskImpact.MINOR: {"min": 2.1, "max": 4.0, "typical": 3.0},
            RiskImpact.MODERATE: {"min": 4.1, "max": 6.0, "typical": 5.0},
            RiskImpact.MAJOR: {"min": 6.1, "max": 8.0, "typical": 7.0},
            RiskImpact.SEVERE: {"min": 8.1, "max": 10.0, "typical": 9.0}
        }
        
        # Priority thresholds
        self.priority_thresholds = {
            "low": {"min": 0.0, "max": 2.5},
            "medium": {"min": 2.5, "max": 5.0},
            "high": {"min": 5.0, "max": 7.5},
            "critical": {"min": 7.5, "max": 10.0}
        }
        
        # Industry-specific risk factors
        self.industry_factors = {
            "financial": {"regulatory_multiplier": 1.5, "reputation_multiplier": 1.3},
            "healthcare": {"compliance_multiplier": 1.4, "safety_multiplier": 1.6},
            "technology": {"cyber_multiplier": 1.4, "innovation_multiplier": 1.2},
            "manufacturing": {"operational_multiplier": 1.3, "supply_chain_multiplier": 1.4},
            "energy": {"environmental_multiplier": 1.5, "regulatory_multiplier": 1.3}
        }
    
    def assess_risk(
        self, 
        risk: RiskRegister, 
        method: RiskScoringMethod = RiskScoringMethod.SIMPLE_MULTIPLICATION,
        context: Optional[RiskContext] = None,
        custom_matrix: Optional[RiskRegisterMatrix] = None
    ) -> RiskScore:
        """Perform comprehensive risk assessment"""
        
        if method == RiskScoringMethod.SIMPLE_MULTIPLICATION:
            return self._simple_multiplication_method(risk, context, custom_matrix)
        elif method == RiskScoringMethod.WEIGHTED_AVERAGE:
            return self._weighted_average_method(risk, context)
        elif method == RiskScoringMethod.QUANTITATIVE:
            return self._quantitative_method(risk, context)
        elif method == RiskScoringMethod.EXPERT_JUDGMENT:
            return self._expert_judgment_method(risk, context)
        else:
            return self._simple_multiplication_method(risk, context, custom_matrix)
    
    def _simple_multiplication_method(
        self, 
        risk: RiskRegister, 
        context: Optional[RiskContext] = None,
        custom_matrix: Optional[RiskRegisterMatrix] = None
    ) -> RiskScore:
        """Simple likelihood × impact scoring method"""
        
        # Get matrix configuration
        matrix = custom_matrix or self._get_default_matrix()
        
        # Calculate likelihood score
        likelihood_score = self._calculate_likelihood_score(
            risk.inherent_likelihood, context, risk
        )
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(
            risk.inherent_impact, context, risk
        )
        
        # Apply context adjustments
        if context:
            likelihood_score = self._apply_context_adjustments(
                likelihood_score, "likelihood", context, risk
            )
            impact_score = self._apply_context_adjustments(
                impact_score, "impact", context, risk
            )
        
        # Calculate overall score
        overall_score = likelihood_score * impact_score
        
        # Determine priority
        priority = self._determine_priority(overall_score)
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(risk, context)
        
        return RiskScore(
            likelihood_score=likelihood_score,
            impact_score=impact_score,
            overall_score=overall_score,
            priority=priority,
            confidence_level=confidence_level,
            methodology_used="simple_multiplication",
            calculation_details={
                "likelihood_value": risk.inherent_likelihood.value,
                "impact_value": risk.inherent_impact.value,
                "context_applied": context is not None,
                "matrix_used": matrix.name if matrix else "default"
            }
        )
    
    def _weighted_average_method(
        self, 
        risk: RiskRegister, 
        context: Optional[RiskContext] = None
    ) -> RiskScore:
        """Weighted average of multiple risk factors"""
        
        factors = {
            "likelihood": 0.4,
            "financial_impact": 0.25,
            "operational_impact": 0.15,
            "reputational_impact": 0.10,
            "compliance_impact": 0.10
        }
        
        # Calculate base scores
        likelihood_score = self._calculate_likelihood_score(risk.inherent_likelihood, context, risk)
        
        # Calculate impact components
        financial_score = self._calculate_financial_impact_score(risk)
        operational_score = self._calculate_operational_impact_score(risk)
        reputational_score = self._calculate_reputational_impact_score(risk)
        compliance_score = self._calculate_compliance_impact_score(risk)
        
        # Calculate weighted average
        weighted_score = (
            likelihood_score * factors["likelihood"] +
            financial_score * factors["financial_impact"] +
            operational_score * factors["operational_impact"] +
            reputational_score * factors["reputational_impact"] +
            compliance_score * factors["compliance_impact"]
        )
        
        # Determine overall impact score (average of impact components)
        impact_score = (financial_score + operational_score + reputational_score + compliance_score) / 4
        
        priority = self._determine_priority(weighted_score)
        confidence_level = self._calculate_confidence_level(risk, context)
        
        return RiskScore(
            likelihood_score=likelihood_score,
            impact_score=impact_score,
            overall_score=weighted_score,
            priority=priority,
            confidence_level=confidence_level,
            methodology_used="weighted_average",
            calculation_details={
                "factors": factors,
                "component_scores": {
                    "likelihood": likelihood_score,
                    "financial": financial_score,
                    "operational": operational_score,
                    "reputational": reputational_score,
                    "compliance": compliance_score
                }
            }
        )
    
    def _quantitative_method(
        self, 
        risk: RiskRegister, 
        context: Optional[RiskContext] = None
    ) -> RiskScore:
        """Quantitative financial risk assessment"""
        
        # Get financial impact estimates
        min_impact = risk.potential_financial_impact_min or 0
        max_impact = risk.potential_financial_impact_max or min_impact
        
        if max_impact == 0:
            # Fallback to qualitative assessment
            return self._simple_multiplication_method(risk, context)
        
        # Calculate expected financial impact
        likelihood_prob = self.likelihood_scale[risk.inherent_likelihood]["typical"]
        expected_impact = (min_impact + max_impact) / 2
        expected_annual_loss = expected_impact * likelihood_prob
        
        # Normalize to 0-10 scale based on organizational thresholds
        # These should be configurable based on organization size/revenue
        max_acceptable_loss = 10000000  # $10M as example threshold
        
        financial_score = min(10.0, (expected_annual_loss / max_acceptable_loss) * 10)
        likelihood_score = self._calculate_likelihood_score(risk.inherent_likelihood, context, risk)
        
        # Overall score is financial risk adjusted for likelihood
        overall_score = math.sqrt(financial_score * likelihood_score)
        
        priority = self._determine_priority(overall_score)
        confidence_level = self._calculate_confidence_level(risk, context)
        
        return RiskScore(
            likelihood_score=likelihood_score,
            impact_score=financial_score,
            overall_score=overall_score,
            priority=priority,
            confidence_level=confidence_level,
            methodology_used="quantitative",
            calculation_details={
                "min_financial_impact": min_impact,
                "max_financial_impact": max_impact,
                "expected_impact": expected_impact,
                "annual_likelihood": likelihood_prob,
                "expected_annual_loss": expected_annual_loss,
                "max_acceptable_loss": max_acceptable_loss
            }
        )
    
    def _expert_judgment_method(
        self, 
        risk: RiskRegister, 
        context: Optional[RiskContext] = None
    ) -> RiskScore:
        """Expert judgment-based scoring with bias adjustment"""
        
        # Get latest assessment
        latest_assessment = self.db.query(RiskAssessment).filter(
            RiskAssessment.risk_id == risk.id
        ).order_by(RiskAssessment.assessment_date.desc()).first()
        
        if not latest_assessment:
            # Fallback to simple method
            return self._simple_multiplication_method(risk, context)
        
        # Base scores from expert assessment
        likelihood_score = self._calculate_likelihood_score(
            latest_assessment.likelihood_rating, context, risk
        )
        impact_score = self._calculate_impact_score(
            latest_assessment.impact_rating, context, risk
        )
        
        # Apply confidence adjustments
        confidence_adjustment = self._calculate_expert_confidence_adjustment(latest_assessment)
        
        # Adjust scores based on confidence
        adjusted_likelihood = likelihood_score * confidence_adjustment
        adjusted_impact = impact_score * confidence_adjustment
        
        overall_score = adjusted_likelihood * adjusted_impact
        priority = self._determine_priority(overall_score)
        
        return RiskScore(
            likelihood_score=adjusted_likelihood,
            impact_score=adjusted_impact,
            overall_score=overall_score,
            priority=priority,
            confidence_level=latest_assessment.assessment_quality_score or 0.7,
            methodology_used="expert_judgment",
            calculation_details={
                "assessment_id": latest_assessment.assessment_id,
                "assessor_confidence": latest_assessment.assessment_quality_score,
                "confidence_adjustment": confidence_adjustment,
                "original_likelihood": likelihood_score,
                "original_impact": impact_score
            }
        )
    
    def _calculate_likelihood_score(
        self, 
        likelihood: RiskLikelihood, 
        context: Optional[RiskContext], 
        risk: RiskRegister
    ) -> float:
        """Calculate likelihood score with context adjustments"""
        
        base_score = self.likelihood_scale[likelihood]["typical"] * 10
        
        # Apply historical data if available
        historical_adjustment = self._get_historical_likelihood_adjustment(risk)
        
        # Apply trend analysis
        trend_adjustment = self._get_trend_adjustment(risk, "likelihood")
        
        # Combine adjustments
        adjusted_score = base_score * (1 + historical_adjustment + trend_adjustment)
        
        return min(10.0, max(0.1, adjusted_score))
    
    def _calculate_impact_score(
        self, 
        impact: RiskImpact, 
        context: Optional[RiskContext], 
        risk: RiskRegister
    ) -> float:
        """Calculate impact score with context adjustments"""
        
        base_score = self.impact_scale[impact]["typical"]
        
        # Apply business context multipliers
        business_adjustment = self._get_business_context_adjustment(risk, context)
        
        # Apply asset dependency impact
        asset_adjustment = self._get_asset_dependency_impact(risk)
        
        # Combine adjustments
        adjusted_score = base_score * (1 + business_adjustment + asset_adjustment)
        
        return min(10.0, max(0.1, adjusted_score))
    
    def _apply_context_adjustments(
        self, 
        score: float, 
        score_type: str, 
        context: RiskContext, 
        risk: RiskRegister
    ) -> float:
        """Apply contextual adjustments to scores"""
        
        adjustment_factor = 1.0
        
        # Industry-specific adjustments
        if context.industry_sector and context.industry_sector in self.industry_factors:
            industry_factors = self.industry_factors[context.industry_sector]
            
            if risk.category == RiskCategory.COMPLIANCE and "regulatory_multiplier" in industry_factors:
                adjustment_factor *= industry_factors["regulatory_multiplier"]
            elif risk.category == RiskCategory.SECURITY and "cyber_multiplier" in industry_factors:
                adjustment_factor *= industry_factors["cyber_multiplier"]
            elif risk.category == RiskCategory.OPERATIONAL and "operational_multiplier" in industry_factors:
                adjustment_factor *= industry_factors["operational_multiplier"]
        
        # Regulatory environment adjustments
        if context.regulatory_environment:
            regulatory_intensity = len(context.regulatory_environment)
            if regulatory_intensity > 3:  # Highly regulated environment
                adjustment_factor *= 1.2
        
        # Market conditions adjustments
        if context.market_conditions:
            if context.market_conditions.lower() in ["volatile", "declining", "crisis"]:
                adjustment_factor *= 1.3
            elif context.market_conditions.lower() in ["stable", "growing"]:
                adjustment_factor *= 0.9
        
        # Risk appetite adjustments
        if context.risk_appetite:
            if context.risk_appetite.lower() == "low":
                adjustment_factor *= 1.2  # More conservative scoring
            elif context.risk_appetite.lower() == "high":
                adjustment_factor *= 0.8  # More aggressive scoring
        
        return score * adjustment_factor
    
    def _calculate_financial_impact_score(self, risk: RiskRegister) -> float:
        """Calculate financial impact component score"""
        
        if risk.potential_financial_impact_max:
            # Normalize based on impact ranges
            impact = risk.potential_financial_impact_max
            
            if impact < 10000:       # < $10K
                return 2.0
            elif impact < 100000:    # < $100K
                return 4.0
            elif impact < 1000000:   # < $1M
                return 6.0
            elif impact < 10000000:  # < $10M
                return 8.0
            else:                    # >= $10M
                return 10.0
        
        # Fallback to qualitative assessment
        return self.impact_scale[risk.inherent_impact]["typical"]
    
    def _calculate_operational_impact_score(self, risk: RiskRegister) -> float:
        """Calculate operational impact component score"""
        
        base_score = self.impact_scale[risk.inherent_impact]["typical"]
        
        # Adjust based on business unit criticality
        if risk.business_unit:
            critical_units = ["operations", "production", "customer service"]
            if any(unit in risk.business_unit.lower() for unit in critical_units):
                base_score *= 1.3
        
        # Adjust based on process area
        if risk.process_area:
            critical_processes = ["core business", "revenue generation", "customer facing"]
            if any(process in risk.process_area.lower() for process in critical_processes):
                base_score *= 1.2
        
        return min(10.0, base_score)
    
    def _calculate_reputational_impact_score(self, risk: RiskRegister) -> float:
        """Calculate reputational impact component score"""
        
        base_score = self.impact_scale[risk.inherent_impact]["typical"]
        
        # Adjust based on risk category
        high_reputation_categories = [
            RiskCategory.SECURITY, RiskCategory.COMPLIANCE, 
            RiskCategory.ENVIRONMENTAL, RiskCategory.LEGAL
        ]
        
        if risk.category in high_reputation_categories:
            base_score *= 1.4
        
        # Adjust based on geographic scope
        if risk.geographic_scope:
            if "global" in risk.geographic_scope.lower():
                base_score *= 1.3
            elif "national" in risk.geographic_scope.lower():
                base_score *= 1.1
        
        return min(10.0, base_score)
    
    def _calculate_compliance_impact_score(self, risk: RiskRegister) -> float:
        """Calculate compliance impact component score"""
        
        base_score = self.impact_scale[risk.inherent_impact]["typical"]
        
        # Adjust based on regulatory requirements
        if risk.regulatory_requirements:
            reg_count = len(risk.regulatory_requirements)
            if reg_count > 3:
                base_score *= 1.5
            elif reg_count > 1:
                base_score *= 1.2
        
        # Adjust based on compliance category
        if risk.category == RiskCategory.COMPLIANCE:
            base_score *= 1.6
        
        return min(10.0, base_score)
    
    def _get_historical_likelihood_adjustment(self, risk: RiskRegister) -> float:
        """Calculate adjustment based on historical incident data"""
        
        # Get historical incidents for this risk
        historical_incidents = self.db.query(RiskRegister).join(
            "incidents"
        ).filter(
            RiskRegister.category == risk.category,
            RiskRegister.business_unit == risk.business_unit
        ).count()
        
        # More historical incidents = higher likelihood adjustment
        if historical_incidents > 5:
            return 0.3  # 30% increase
        elif historical_incidents > 2:
            return 0.1  # 10% increase
        elif historical_incidents == 0:
            return -0.1  # 10% decrease
        else:
            return 0.0  # No adjustment
    
    def _get_trend_adjustment(self, risk: RiskRegister, score_type: str) -> float:
        """Calculate adjustment based on risk trend analysis"""
        
        # Analyze recent assessments to identify trends
        recent_assessments = self.db.query(RiskAssessment).filter(
            RiskAssessment.risk_id == risk.id,
            RiskAssessment.assessment_date >= datetime.now() - timedelta(days=365)
        ).order_by(RiskAssessment.assessment_date.desc()).limit(3).all()
        
        if len(recent_assessments) < 2:
            return 0.0  # Not enough data for trend analysis
        
        # Simple trend calculation
        if score_type == "likelihood":
            values = [self.likelihood_scale[a.likelihood_rating]["typical"] for a in recent_assessments]
        else:
            values = [self.impact_scale[a.impact_rating]["typical"] for a in recent_assessments]
        
        if len(values) >= 2:
            trend = (values[0] - values[-1]) / len(values)  # Recent vs oldest
            return min(0.2, max(-0.2, trend))  # Cap at ±20%
        
        return 0.0
    
    def _get_business_context_adjustment(
        self, 
        risk: RiskRegister, 
        context: Optional[RiskContext]
    ) -> float:
        """Calculate adjustment based on business context"""
        
        adjustment = 0.0
        
        # Critical business units have higher impact
        if risk.business_unit:
            critical_units = ["finance", "operations", "it", "legal", "compliance"]
            if any(unit in risk.business_unit.lower() for unit in critical_units):
                adjustment += 0.2
        
        # Multiple regulatory requirements increase impact
        if risk.regulatory_requirements and len(risk.regulatory_requirements) > 2:
            adjustment += 0.15
        
        # External dependencies increase impact
        if risk.external_dependencies and len(risk.external_dependencies) > 1:
            adjustment += 0.1
        
        return adjustment
    
    def _get_asset_dependency_impact(self, risk: RiskRegister) -> float:
        """Calculate impact adjustment based on affected assets"""
        
        # Count affected assets
        affected_asset_count = len(risk.affected_assets) if risk.affected_assets else 0
        
        if affected_asset_count == 0:
            return 0.0
        elif affected_asset_count < 3:
            return 0.1
        elif affected_asset_count < 10:
            return 0.2
        else:
            return 0.3
    
    def _calculate_expert_confidence_adjustment(self, assessment: RiskAssessment) -> float:
        """Calculate confidence adjustment for expert judgment"""
        
        base_confidence = assessment.assessment_quality_score or 0.7
        
        # Adjust based on assessment completeness
        completeness_score = 0.0
        
        if assessment.likelihood_rationale:
            completeness_score += 0.2
        if assessment.impact_rationale:
            completeness_score += 0.2
        if assessment.assessment_criteria:
            completeness_score += 0.2
        if assessment.data_sources:
            completeness_score += 0.2
        if assessment.is_validated:
            completeness_score += 0.2
        
        # Combine base confidence with completeness
        final_confidence = (base_confidence + completeness_score) / 2
        
        return min(1.2, max(0.8, final_confidence))  # Cap between 80%-120%
    
    def _determine_priority(self, overall_score: float) -> str:
        """Determine risk priority based on overall score"""
        
        for priority, threshold in self.priority_thresholds.items():
            if threshold["min"] <= overall_score < threshold["max"]:
                return priority
        
        # Handle edge case for maximum score
        if overall_score >= self.priority_thresholds["critical"]["min"]:
            return "critical"
        
        return "low"
    
    def _calculate_confidence_level(
        self, 
        risk: RiskRegister, 
        context: Optional[RiskContext]
    ) -> float:
        """Calculate overall confidence level in the assessment"""
        
        confidence_factors = []
        
        # Data quality factors
        if risk.description and len(risk.description) > 50:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        # Assessment recency
        if risk.last_review_date:
            days_since_review = (datetime.now() - risk.last_review_date).days
            if days_since_review < 90:
                confidence_factors.append(0.9)
            elif days_since_review < 180:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.4)
        
        # Financial impact quantification
        if risk.potential_financial_impact_max:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Control environment
        control_count = len(risk.controls) if risk.controls else 0
        if control_count > 2:
            confidence_factors.append(0.8)
        elif control_count > 0:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # Context availability
        if context:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _get_default_matrix(self) -> Optional[RiskRegisterMatrix]:
        """Get default risk matrix configuration"""
        
        return self.db.query(RiskRegisterMatrix).filter(
            RiskRegisterMatrix.is_default == True,
            RiskRegisterMatrix.is_active == True
        ).first()
    
    def calculate_residual_risk(
        self, 
        risk: RiskRegister, 
        method: RiskScoringMethod = RiskScoringMethod.SIMPLE_MULTIPLICATION
    ) -> RiskScore:
        """Calculate residual risk after controls and treatments"""
        
        if not (risk.residual_likelihood and risk.residual_impact):
            # Use inherent risk if residual not specified
            return self.assess_risk(risk, method)
        
        # Create temporary risk object with residual values
        residual_risk = RiskRegister(
            title=risk.title,
            description=risk.description,
            category=risk.category,
            inherent_likelihood=risk.residual_likelihood,
            inherent_impact=risk.residual_impact,
            business_unit=risk.business_unit,
            process_area=risk.process_area,
            potential_financial_impact_min=risk.potential_financial_impact_min,
            potential_financial_impact_max=risk.potential_financial_impact_max,
            regulatory_requirements=risk.regulatory_requirements,
            external_dependencies=risk.external_dependencies
        )
        
        # Calculate residual score
        residual_score = self.assess_risk(residual_risk, method)
        residual_score.methodology_used = f"residual_{residual_score.methodology_used}"
        
        return residual_score
    
    def compare_risk_scores(
        self, 
        risk1: RiskRegister, 
        risk2: RiskRegister,
        method: RiskScoringMethod = RiskScoringMethod.SIMPLE_MULTIPLICATION
    ) -> Dict[str, Any]:
        """Compare two risks and provide relative analysis"""
        
        score1 = self.assess_risk(risk1, method)
        score2 = self.assess_risk(risk2, method)
        
        return {
            "risk1": {
                "id": risk1.id,
                "title": risk1.title,
                "score": score1.overall_score,
                "priority": score1.priority
            },
            "risk2": {
                "id": risk2.id,
                "title": risk2.title,
                "score": score2.overall_score,
                "priority": score2.priority
            },
            "comparison": {
                "higher_risk": "risk1" if score1.overall_score > score2.overall_score else "risk2",
                "score_difference": abs(score1.overall_score - score2.overall_score),
                "priority_difference": self._compare_priorities(score1.priority, score2.priority)
            }
        }
    
    def _compare_priorities(self, priority1: str, priority2: str) -> str:
        """Compare priority levels"""
        
        priority_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        
        p1_order = priority_order.get(priority1, 1)
        p2_order = priority_order.get(priority2, 1)
        
        if p1_order > p2_order:
            return f"{priority1} > {priority2}"
        elif p2_order > p1_order:
            return f"{priority2} > {priority1}"
        else:
            return f"{priority1} = {priority2}"
    
    def bulk_assess_risks(
        self, 
        risk_ids: List[int], 
        method: RiskScoringMethod = RiskScoringMethod.SIMPLE_MULTIPLICATION
    ) -> Dict[int, RiskScore]:
        """Perform bulk risk assessment for multiple risks"""
        
        risks = self.db.query(RiskRegister).filter(
            RiskRegister.id.in_(risk_ids),
            RiskRegister.is_active == True
        ).all()
        
        results = {}
        for risk in risks:
            try:
                score = self.assess_risk(risk, method)
                results[risk.id] = score
            except Exception as e:
                # Log error and continue with other risks
                results[risk.id] = None
        
        return results