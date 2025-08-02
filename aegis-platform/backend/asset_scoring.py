"""
Asset Criticality Scoring System
Provides automated scoring algorithms for asset criticality assessment
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json
from datetime import datetime


class CriticalityFactor(Enum):
    """Factors that influence asset criticality"""
    BUSINESS_IMPACT = "business_impact"
    DATA_SENSITIVITY = "data_sensitivity"
    SYSTEM_AVAILABILITY = "system_availability"
    COMPLIANCE_REQUIREMENTS = "compliance_requirements"
    RECOVERY_TIME_OBJECTIVE = "recovery_time_objective"
    FINANCIAL_IMPACT = "financial_impact"
    OPERATIONAL_DEPENDENCY = "operational_dependency"


class AssetCriticalityScorer:
    """Calculate asset criticality scores based on multiple factors"""
    
    def __init__(self):
        self.factor_weights = {
            CriticalityFactor.BUSINESS_IMPACT: 0.25,
            CriticalityFactor.DATA_SENSITIVITY: 0.20,
            CriticalityFactor.SYSTEM_AVAILABILITY: 0.15,
            CriticalityFactor.COMPLIANCE_REQUIREMENTS: 0.15,
            CriticalityFactor.RECOVERY_TIME_OBJECTIVE: 0.10,
            CriticalityFactor.FINANCIAL_IMPACT: 0.10,
            CriticalityFactor.OPERATIONAL_DEPENDENCY: 0.05
        }
    
    def calculate_criticality_score(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive criticality score for an asset"""
        
        # Extract relevant factors from asset data
        scores = {}
        
        # Business Impact Score (1-10)
        business_impact = self._calculate_business_impact(asset_data)
        scores[CriticalityFactor.BUSINESS_IMPACT] = business_impact
        
        # Data Sensitivity Score (1-10)
        data_sensitivity = self._calculate_data_sensitivity(asset_data)
        scores[CriticalityFactor.DATA_SENSITIVITY] = data_sensitivity
        
        # System Availability Score (1-10)
        availability = self._calculate_availability_requirements(asset_data)
        scores[CriticalityFactor.SYSTEM_AVAILABILITY] = availability
        
        # Compliance Requirements Score (1-10)
        compliance = self._calculate_compliance_impact(asset_data)
        scores[CriticalityFactor.COMPLIANCE_REQUIREMENTS] = compliance
        
        # Recovery Time Objective Score (1-10)
        rto = self._calculate_rto_score(asset_data)
        scores[CriticalityFactor.RECOVERY_TIME_OBJECTIVE] = rto
        
        # Financial Impact Score (1-10)
        financial = self._calculate_financial_impact(asset_data)
        scores[CriticalityFactor.FINANCIAL_IMPACT] = financial
        
        # Operational Dependency Score (1-10)
        dependency = self._calculate_operational_dependency(asset_data)
        scores[CriticalityFactor.OPERATIONAL_DEPENDENCY] = dependency
        
        # Calculate weighted total score
        total_score = sum(
            scores[factor] * self.factor_weights[factor]
            for factor in scores
        )
        
        # Convert to criticality level
        criticality_level = self._score_to_criticality_level(total_score)
        
        return {
            "total_score": round(total_score, 2),
            "criticality_level": criticality_level,
            "factor_scores": {factor.value: score for factor, score in scores.items()},
            "recommendations": self._generate_recommendations(scores, asset_data),
            "calculated_at": datetime.now().isoformat()
        }
    
    def _calculate_business_impact(self, asset_data: Dict[str, Any]) -> int:
        """Calculate business impact score (1-10)"""
        environment = asset_data.get("environment", "development").lower()
        asset_type = asset_data.get("asset_type", "other").lower()
        business_unit = asset_data.get("business_unit", "").lower()
        
        score = 5  # Base score
        
        # Environment impact
        if environment == "production":
            score += 3
        elif environment == "staging":
            score += 1
        elif environment == "development":
            score -= 1
        
        # Asset type impact
        if asset_type in ["database", "application", "cloud_service"]:
            score += 2
        elif asset_type in ["server", "network_device"]:
            score += 1
        
        # Business unit criticality
        if "engineering" in business_unit or "operations" in business_unit:
            score += 1
        
        return min(max(score, 1), 10)
    
    def _calculate_data_sensitivity(self, asset_data: Dict[str, Any]) -> int:
        """Calculate data sensitivity score (1-10)"""
        compliance_scope = asset_data.get("compliance_scope", [])
        if isinstance(compliance_scope, str):
            compliance_scope = json.loads(compliance_scope) if compliance_scope else []
        
        custom_fields = asset_data.get("custom_fields", {})
        if isinstance(custom_fields, str):
            custom_fields = json.loads(custom_fields) if custom_fields else {}
        
        score = 3  # Base score
        
        # Compliance framework requirements
        high_sensitivity_frameworks = ["SOX", "HIPAA", "PCI-DSS", "GDPR"]
        medium_sensitivity_frameworks = ["SOC2", "ISO27001", "NIST"]
        
        for framework in compliance_scope:
            if framework in high_sensitivity_frameworks:
                score += 3
            elif framework in medium_sensitivity_frameworks:
                score += 2
        
        # Data classification from custom fields
        data_classification = custom_fields.get("data_classification", "").lower()
        if "confidential" in data_classification or "restricted" in data_classification:
            score += 3
        elif "internal" in data_classification:
            score += 1
        
        return min(max(score, 1), 10)
    
    def _calculate_availability_requirements(self, asset_data: Dict[str, Any]) -> int:
        """Calculate system availability requirements score (1-10)"""
        environment = asset_data.get("environment", "development").lower()
        asset_type = asset_data.get("asset_type", "other").lower()
        
        custom_fields = asset_data.get("custom_fields", {})
        if isinstance(custom_fields, str):
            custom_fields = json.loads(custom_fields) if custom_fields else {}
        
        score = 5  # Base score
        
        # Environment availability requirements
        if environment == "production":
            score += 3
        elif environment == "staging":
            score += 1
        
        # Asset type availability impact
        critical_types = ["database", "network_device", "cloud_service"]
        if asset_type in critical_types:
            score += 2
        
        # SLA requirements from custom fields
        sla_requirement = custom_fields.get("sla_requirement", "").lower()
        if "99.9" in sla_requirement or "four-nines" in sla_requirement:
            score += 2
        elif "99.5" in sla_requirement:
            score += 1
        
        return min(max(score, 1), 10)
    
    def _calculate_compliance_impact(self, asset_data: Dict[str, Any]) -> int:
        """Calculate compliance impact score (1-10)"""
        compliance_scope = asset_data.get("compliance_scope", [])
        if isinstance(compliance_scope, str):
            compliance_scope = json.loads(compliance_scope) if compliance_scope else []
        
        score = len(compliance_scope) * 2 if compliance_scope else 1
        return min(max(score, 1), 10)
    
    def _calculate_rto_score(self, asset_data: Dict[str, Any]) -> int:
        """Calculate Recovery Time Objective score (1-10)"""
        custom_fields = asset_data.get("custom_fields", {})
        if isinstance(custom_fields, str):
            custom_fields = json.loads(custom_fields) if custom_fields else {}
        
        rto = custom_fields.get("recovery_time_objective", "").lower()
        
        if "immediate" in rto or rto == "0":
            return 10
        elif "1 hour" in rto or "< 1" in rto:
            return 9
        elif "24 hour" in rto or "< 24" in rto:
            return 3
        elif "8 hour" in rto or "< 8" in rto:
            return 5
        elif "4 hour" in rto or "< 4" in rto:
            return 7
        else:
            return 1
    
    def _calculate_financial_impact(self, asset_data: Dict[str, Any]) -> int:
        """Calculate financial impact score (1-10)"""
        custom_fields = asset_data.get("custom_fields", {})
        if isinstance(custom_fields, str):
            custom_fields = json.loads(custom_fields) if custom_fields else {}
        
        # Revenue impact from custom fields
        revenue_impact = custom_fields.get("revenue_impact_per_hour", 0)
        if isinstance(revenue_impact, str):
            revenue_impact = float(revenue_impact) if revenue_impact.isdigit() else 0
        
        if revenue_impact >= 100000:
            return 10
        elif revenue_impact >= 50000:
            return 8
        elif revenue_impact >= 10000:
            return 6
        elif revenue_impact >= 1000:
            return 4
        elif revenue_impact > 0:
            return 2
        else:
            return 1
    
    def _calculate_operational_dependency(self, asset_data: Dict[str, Any]) -> int:
        """Calculate operational dependency score (1-10)"""
        custom_fields = asset_data.get("custom_fields", {})
        if isinstance(custom_fields, str):
            custom_fields = json.loads(custom_fields) if custom_fields else {}
        
        dependent_systems = custom_fields.get("dependent_systems", [])
        if isinstance(dependent_systems, str):
            dependent_systems = json.loads(dependent_systems) if dependent_systems else []
        
        # Score based on number of dependent systems
        dependency_count = len(dependent_systems) if dependent_systems else 0
        
        if dependency_count >= 10:
            return 10
        elif dependency_count >= 5:
            return 7
        elif dependency_count >= 2:
            return 5
        elif dependency_count == 1:
            return 3
        else:
            return 1
    
    def _score_to_criticality_level(self, score: float) -> str:
        """Convert numerical score to criticality level"""
        if score >= 8.5:
            return "critical"
        elif score >= 7.0:
            return "high"
        elif score >= 4.0:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, scores: Dict[CriticalityFactor, int], asset_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on criticality scores"""
        recommendations = []
        
        # High business impact recommendations
        if scores[CriticalityFactor.BUSINESS_IMPACT] >= 8:
            recommendations.append("Implement redundancy and failover mechanisms")
            recommendations.append("Establish comprehensive backup and disaster recovery procedures")
        
        # High data sensitivity recommendations
        if scores[CriticalityFactor.DATA_SENSITIVITY] >= 8:
            recommendations.append("Implement encryption at rest and in transit")
            recommendations.append("Establish strict access controls and monitoring")
        
        # High availability requirements
        if scores[CriticalityFactor.SYSTEM_AVAILABILITY] >= 8:
            recommendations.append("Implement high availability clustering")
            recommendations.append("Monitor system health and performance continuously")
        
        # Compliance requirements
        if scores[CriticalityFactor.COMPLIANCE_REQUIREMENTS] >= 7:
            recommendations.append("Regular compliance audits and assessments")
            recommendations.append("Maintain detailed documentation and change logs")
        
        return recommendations


def calculate_asset_criticality(asset_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to calculate asset criticality"""
    scorer = AssetCriticalityScorer()
    return scorer.calculate_criticality_score(asset_data)


def get_criticality_factors_info() -> Dict[str, Any]:
    """Get information about criticality factors and their weights"""
    scorer = AssetCriticalityScorer()
    return {
        "factors": [
            {
                "name": factor.value,
                "weight": weight,
                "description": _get_factor_description(factor)
            }
            for factor, weight in scorer.factor_weights.items()
        ],
        "scoring_scale": {
            "1-3": "Low impact/risk",
            "4-6": "Medium impact/risk", 
            "7-8": "High impact/risk",
            "9-10": "Critical impact/risk"
        },
        "criticality_levels": {
            "low": "0.0 - 3.9",
            "medium": "4.0 - 6.9", 
            "high": "7.0 - 8.4",
            "critical": "8.5 - 10.0"
        }
    }


def _get_factor_description(factor: CriticalityFactor) -> str:
    """Get description for a criticality factor"""
    descriptions = {
        CriticalityFactor.BUSINESS_IMPACT: "Impact on business operations and revenue",
        CriticalityFactor.DATA_SENSITIVITY: "Sensitivity and classification of data stored/processed",
        CriticalityFactor.SYSTEM_AVAILABILITY: "Requirements for system uptime and availability",
        CriticalityFactor.COMPLIANCE_REQUIREMENTS: "Regulatory and compliance framework requirements",
        CriticalityFactor.RECOVERY_TIME_OBJECTIVE: "Required time to restore service after failure",
        CriticalityFactor.FINANCIAL_IMPACT: "Direct financial impact of system downtime",
        CriticalityFactor.OPERATIONAL_DEPENDENCY: "Number of other systems dependent on this asset"
    }
    return descriptions.get(factor, "Unknown factor")