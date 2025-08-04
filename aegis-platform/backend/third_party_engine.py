from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import logging
from enum import Enum

from models.third_party import (
    Vendor, VendorRiskAssessment, VendorContract, VendorMonitoring,
    VendorIncident, VendorActionItem, VendorAlert, SLAMonitoring,
    SupplyChainNode, VendorDueDiligence,
    VendorStatus, VendorTier, RiskLevel, AssessmentStatus, ContractStatus,
    MonitoringStatus, ComplianceStatus
)

logger = logging.getLogger(__name__)

class RiskCategory(Enum):
    INFORMATION_SECURITY = "information_security"
    DATA_PROTECTION = "data_protection"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    BUSINESS_CONTINUITY = "business_continuity"
    REPUTATIONAL = "reputational"

@dataclass
class RiskAssessmentCriteria:
    category: str
    weight: float
    questions: List[Dict[str, Any]]
    scoring_rules: Dict[str, Any]
    thresholds: Dict[str, float]

@dataclass
class VendorRiskProfile:
    vendor_id: str
    overall_risk_score: float
    risk_level: RiskLevel
    category_scores: Dict[str, float]
    risk_factors: List[str]
    mitigation_recommendations: List[str]
    confidence_score: float
    last_updated: datetime

@dataclass
class AssessmentResult:
    vendor_id: str
    assessment_id: str
    scores: Dict[str, float]
    overall_score: float
    risk_level: RiskLevel
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    action_items: List[Dict[str, Any]]

class ThirdPartyRiskEngine:
    def __init__(self, db_session):
        self.db = db_session
        self.risk_criteria = self._initialize_risk_criteria()
        self.scoring_weights = self._initialize_scoring_weights()
        
    def _initialize_risk_criteria(self) -> Dict[str, RiskAssessmentCriteria]:
        """Initialize risk assessment criteria for different categories"""
        return {
            RiskCategory.INFORMATION_SECURITY.value: RiskAssessmentCriteria(
                category="Information Security",
                weight=0.25,
                questions=[
                    {
                        "id": "sec_001",
                        "question": "Does the vendor have ISO 27001 certification?",
                        "type": "boolean",
                        "weight": 20,
                        "risk_impact": "high"
                    },
                    {
                        "id": "sec_002", 
                        "question": "Has the vendor experienced a security breach in the last 2 years?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "critical"
                    },
                    {
                        "id": "sec_003",
                        "question": "Does the vendor conduct regular penetration testing?",
                        "type": "frequency",
                        "weight": 15,
                        "options": ["never", "annually", "semi-annually", "quarterly"]
                    },
                    {
                        "id": "sec_004",
                        "question": "What is the vendor's security awareness training frequency?",
                        "type": "frequency",
                        "weight": 10,
                        "options": ["none", "annually", "semi-annually", "quarterly", "monthly"]
                    },
                    {
                        "id": "sec_005",
                        "question": "Does the vendor have a dedicated CISO?",
                        "type": "boolean",
                        "weight": 15,
                        "risk_impact": "medium"
                    }
                ],
                scoring_rules={
                    "boolean": {"yes": 100, "no": 0},
                    "frequency": {
                        "never": 0, "annually": 25, "semi-annually": 50,
                        "quarterly": 75, "monthly": 100
                    }
                },
                thresholds={"excellent": 90, "good": 75, "acceptable": 60, "poor": 40}
            ),
            
            RiskCategory.DATA_PROTECTION.value: RiskAssessmentCriteria(
                category="Data Protection",
                weight=0.20,
                questions=[
                    {
                        "id": "dp_001",
                        "question": "Is the vendor GDPR compliant?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "critical"
                    },
                    {
                        "id": "dp_002",
                        "question": "Does the vendor have data encryption at rest?",
                        "type": "boolean",
                        "weight": 20,
                        "risk_impact": "high"
                    },
                    {
                        "id": "dp_003",
                        "question": "Does the vendor have data encryption in transit?",
                        "type": "boolean",
                        "weight": 20,
                        "risk_impact": "high"
                    },
                    {
                        "id": "dp_004",
                        "question": "What is the vendor's data retention policy?",
                        "type": "scale",
                        "weight": 15,
                        "scale": "1-5"
                    },
                    {
                        "id": "dp_005",
                        "question": "Does the vendor have a Data Protection Officer?",
                        "type": "boolean",
                        "weight": 20,
                        "risk_impact": "medium"
                    }
                ],
                scoring_rules={
                    "boolean": {"yes": 100, "no": 0},
                    "scale": {"1": 0, "2": 25, "3": 50, "4": 75, "5": 100}
                },
                thresholds={"excellent": 90, "good": 75, "acceptable": 60, "poor": 40}
            ),
            
            RiskCategory.FINANCIAL.value: RiskAssessmentCriteria(
                category="Financial",
                weight=0.15,
                questions=[
                    {
                        "id": "fin_001",
                        "question": "What is the vendor's credit rating?",
                        "type": "rating",
                        "weight": 30,
                        "options": ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]
                    },
                    {
                        "id": "fin_002",
                        "question": "Has the vendor filed for bankruptcy in the last 5 years?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "critical"
                    },
                    {
                        "id": "fin_003",
                        "question": "What is the vendor's annual revenue growth rate?",
                        "type": "percentage",
                        "weight": 20
                    },
                    {
                        "id": "fin_004",
                        "question": "Does the vendor maintain adequate insurance coverage?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "high"
                    }
                ],
                scoring_rules={
                    "boolean": {"yes": 100, "no": 0},
                    "rating": {
                        "AAA": 100, "AA": 90, "A": 80, "BBB": 70,
                        "BB": 60, "B": 50, "CCC": 40, "CC": 30, "C": 20, "D": 0
                    }
                },
                thresholds={"excellent": 85, "good": 70, "acceptable": 55, "poor": 40}
            ),
            
            RiskCategory.OPERATIONAL.value: RiskAssessmentCriteria(
                category="Operational",
                weight=0.15,
                questions=[
                    {
                        "id": "op_001",
                        "question": "What is the vendor's service availability SLA?",
                        "type": "percentage",
                        "weight": 25
                    },
                    {
                        "id": "op_002",
                        "question": "Does the vendor have 24/7 support coverage?",
                        "type": "boolean",
                        "weight": 20,
                        "risk_impact": "medium"
                    },
                    {
                        "id": "op_003",
                        "question": "What is the vendor's incident response time SLA?",
                        "type": "time",
                        "weight": 20,
                        "options": ["<1h", "1-4h", "4-8h", "8-24h", ">24h"]
                    },
                    {
                        "id": "op_004",
                        "question": "Does the vendor have documented change management processes?",
                        "type": "boolean",
                        "weight": 15,
                        "risk_impact": "medium"
                    },
                    {
                        "id": "op_005",
                        "question": "What is the vendor's staff turnover rate?",
                        "type": "percentage",
                        "weight": 20
                    }
                ],
                scoring_rules={
                    "boolean": {"yes": 100, "no": 0},
                    "time": {"<1h": 100, "1-4h": 80, "4-8h": 60, "8-24h": 40, ">24h": 20}
                },
                thresholds={"excellent": 90, "good": 75, "acceptable": 60, "poor": 45}
            ),
            
            RiskCategory.COMPLIANCE.value: RiskAssessmentCriteria(
                category="Compliance",
                weight=0.15,
                questions=[
                    {
                        "id": "comp_001",
                        "question": "Does the vendor have SOC 2 Type II certification?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "high"
                    },
                    {
                        "id": "comp_002",
                        "question": "Is the vendor compliant with industry-specific regulations?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "critical"
                    },
                    {
                        "id": "comp_003",
                        "question": "Does the vendor conduct regular compliance audits?",
                        "type": "frequency",
                        "weight": 20,
                        "options": ["never", "annually", "semi-annually", "quarterly"]
                    },
                    {
                        "id": "comp_004",
                        "question": "Has the vendor received regulatory fines in the last 3 years?",
                        "type": "boolean",
                        "weight": 30,
                        "risk_impact": "critical"
                    }
                ],
                scoring_rules={
                    "boolean": {"yes": 100, "no": 0},
                    "frequency": {
                        "never": 0, "annually": 60, "semi-annually": 80, "quarterly": 100
                    }
                },
                thresholds={"excellent": 90, "good": 75, "acceptable": 60, "poor": 40}
            ),
            
            RiskCategory.BUSINESS_CONTINUITY.value: RiskAssessmentCriteria(
                category="Business Continuity",
                weight=0.10,
                questions=[
                    {
                        "id": "bc_001",
                        "question": "Does the vendor have a documented BCP?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "high"
                    },
                    {
                        "id": "bc_002",
                        "question": "How frequently is the BCP tested?",
                        "type": "frequency",
                        "weight": 25,
                        "options": ["never", "annually", "semi-annually", "quarterly"]
                    },
                    {
                        "id": "bc_003",
                        "question": "What is the vendor's RTO for critical services?",
                        "type": "time",
                        "weight": 25,
                        "options": ["<1h", "1-4h", "4-8h", "8-24h", ">24h"]
                    },
                    {
                        "id": "bc_004",
                        "question": "Does the vendor have geographically distributed infrastructure?",
                        "type": "boolean",
                        "weight": 25,
                        "risk_impact": "medium"
                    }
                ],
                scoring_rules={
                    "boolean": {"yes": 100, "no": 0},
                    "frequency": {
                        "never": 0, "annually": 60, "semi-annually": 80, "quarterly": 100
                    },
                    "time": {"<1h": 100, "1-4h": 80, "4-8h": 60, "8-24h": 40, ">24h": 20}
                },
                thresholds={"excellent": 90, "good": 75, "acceptable": 60, "poor": 45}
            )
        }
    
    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """Initialize scoring weights for different vendor tiers"""
        return {
            VendorTier.CRITICAL.value: {
                "information_security": 0.30,
                "data_protection": 0.25,
                "operational": 0.20,
                "compliance": 0.15,
                "business_continuity": 0.10
            },
            VendorTier.HIGH.value: {
                "information_security": 0.25,
                "data_protection": 0.20,
                "operational": 0.20,
                "financial": 0.15,
                "compliance": 0.12,
                "business_continuity": 0.08
            },
            VendorTier.MEDIUM.value: {
                "information_security": 0.22,
                "data_protection": 0.18,
                "operational": 0.18,
                "financial": 0.18,
                "compliance": 0.12,
                "business_continuity": 0.12
            },
            VendorTier.LOW.value: {
                "information_security": 0.20,
                "data_protection": 0.15,
                "operational": 0.15,
                "financial": 0.20,
                "compliance": 0.15,
                "business_continuity": 0.15
            }
        }
    
    def conduct_risk_assessment(
        self,
        vendor_id: int,
        assessment_data: Dict[str, Any],
        assessment_type: str = "periodic"
    ) -> AssessmentResult:
        """Conduct comprehensive vendor risk assessment"""
        
        try:
            vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
            if not vendor:
                raise ValueError(f"Vendor with ID {vendor_id} not found")
            
            # Calculate category scores
            category_scores = {}
            detailed_findings = []
            
            for category, criteria in self.risk_criteria.items():
                score, findings = self._assess_category(
                    category, criteria, assessment_data.get(category, {})
                )
                category_scores[category] = score
                detailed_findings.extend(findings)
            
            # Calculate overall risk score
            weights = self.scoring_weights.get(
                vendor.tier.value, 
                self.scoring_weights[VendorTier.MEDIUM.value]
            )
            
            overall_score = sum(
                category_scores.get(category, 0) * weight
                for category, weight in weights.items()
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                category_scores, detailed_findings
            )
            
            # Create action items
            action_items = self._generate_action_items(
                category_scores, detailed_findings, vendor.tier
            )
            
            # Create assessment record
            assessment = VendorRiskAssessment(
                vendor_id=vendor_id,
                assessment_name=f"{assessment_type.title()} Risk Assessment",
                assessment_type=assessment_type,
                assessment_start_date=datetime.utcnow(),
                status=AssessmentStatus.COMPLETED,
                information_security_score=category_scores.get("information_security", 0),
                data_protection_score=category_scores.get("data_protection", 0),
                operational_risk_score=category_scores.get("operational", 0),
                financial_risk_score=category_scores.get("financial", 0),
                compliance_risk_score=category_scores.get("compliance", 0),
                business_continuity_score=category_scores.get("business_continuity", 0),
                reputational_risk_score=category_scores.get("reputational", 0),
                overall_risk_score=overall_score,
                overall_risk_level=risk_level,
                questionnaire_responses=assessment_data,
                strengths=[f["strength"] for f in detailed_findings if f.get("strength")],
                weaknesses=[f["weakness"] for f in detailed_findings if f.get("weakness")],
                recommendations=recommendations,
                assessment_end_date=datetime.utcnow(),
                next_assessment_due=datetime.utcnow() + timedelta(days=365)
            )
            
            self.db.add(assessment)
            self.db.flush()
            
            # Update vendor risk score
            vendor.overall_risk_score = overall_score
            vendor.last_risk_assessment = datetime.utcnow()
            vendor.next_assessment_due = assessment.next_assessment_due
            
            # Create action items
            for item_data in action_items:
                action_item = VendorActionItem(
                    assessment_id=assessment.id,
                    title=item_data["title"],
                    description=item_data["description"],
                    category=item_data["category"],
                    priority=item_data["priority"],
                    due_date=item_data["due_date"]
                )
                self.db.add(action_item)
            
            self.db.commit()
            
            return AssessmentResult(
                vendor_id=vendor.vendor_id,
                assessment_id=assessment.assessment_id,
                scores=category_scores,
                overall_score=overall_score,
                risk_level=risk_level,
                findings=detailed_findings,
                recommendations=recommendations,
                action_items=action_items
            )
            
        except Exception as e:
            logger.error(f"Error conducting risk assessment: {str(e)}")
            self.db.rollback()
            raise
    
    def _assess_category(
        self,
        category: str,
        criteria: RiskAssessmentCriteria,
        responses: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Assess a specific risk category"""
        
        total_score = 0
        total_weight = 0
        findings = []
        
        for question in criteria.questions:
            question_id = question["id"]
            weight = question["weight"]
            response = responses.get(question_id)
            
            if response is None:
                findings.append({
                    "question_id": question_id,
                    "category": category,
                    "finding": "No response provided",
                    "impact": "Unknown"
                })
                continue
            
            # Calculate question score
            question_score = self._score_response(
                question, response, criteria.scoring_rules
            )
            
            total_score += question_score * (weight / 100)
            total_weight += weight / 100
            
            # Generate findings
            if question_score < 50:
                findings.append({
                    "question_id": question_id,
                    "category": category,
                    "weakness": question["question"],
                    "score": question_score,
                    "impact": question.get("risk_impact", "medium")
                })
            elif question_score > 80:
                findings.append({
                    "question_id": question_id,
                    "category": category,
                    "strength": question["question"],
                    "score": question_score
                })
        
        category_score = (total_score / total_weight) if total_weight > 0 else 0
        
        return category_score, findings
    
    def _score_response(
        self,
        question: Dict[str, Any],
        response: Any,
        scoring_rules: Dict[str, Any]
    ) -> float:
        """Score an individual question response"""
        
        question_type = question["type"]
        
        if question_type == "boolean":
            response_key = "yes" if response else "no"
            return scoring_rules["boolean"].get(response_key, 0)
        
        elif question_type == "frequency":
            return scoring_rules["frequency"].get(response, 0)
        
        elif question_type == "scale":
            return scoring_rules["scale"].get(str(response), 0)
        
        elif question_type == "rating":
            return scoring_rules["rating"].get(response, 0)
        
        elif question_type == "percentage":
            # Convert percentage to score (assuming higher is better)
            try:
                pct = float(response)
                return min(100, max(0, pct))
            except (ValueError, TypeError):
                return 0
        
        elif question_type == "time":
            return scoring_rules["time"].get(response, 0)
        
        else:
            return 0
    
    def _determine_risk_level(self, overall_score: float) -> RiskLevel:
        """Determine risk level based on overall score"""
        if overall_score >= 80:
            return RiskLevel.LOW
        elif overall_score >= 60:
            return RiskLevel.MEDIUM
        elif overall_score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_recommendations(
        self,
        category_scores: Dict[str, float],
        findings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on assessment results"""
        
        recommendations = []
        
        # Category-specific recommendations
        for category, score in category_scores.items():
            if score < 60:
                recommendations.extend(
                    self._get_category_recommendations(category, score)
                )
        
        # Finding-specific recommendations
        critical_findings = [
            f for f in findings 
            if f.get("impact") == "critical" and f.get("score", 100) < 50
        ]
        
        for finding in critical_findings:
            recommendations.append(
                f"Address critical issue: {finding.get('weakness', 'Unknown issue')}"
            )
        
        return list(set(recommendations))  # Remove duplicates
    
    def _get_category_recommendations(self, category: str, score: float) -> List[str]:
        """Get recommendations for specific category"""
        
        recommendations = {
            "information_security": [
                "Implement ISO 27001 certification process",
                "Conduct regular security audits and penetration testing",
                "Establish incident response procedures",
                "Implement multi-factor authentication",
                "Enhance security awareness training"
            ],
            "data_protection": [
                "Achieve GDPR compliance",
                "Implement data encryption at rest and in transit",
                "Establish data retention and deletion policies",
                "Appoint Data Protection Officer",
                "Conduct privacy impact assessments"
            ],
            "financial": [
                "Obtain credit rating improvement",
                "Provide financial statements and audits",
                "Secure adequate insurance coverage",
                "Establish financial monitoring procedures"
            ],
            "operational": [
                "Improve service level agreements",
                "Implement 24/7 support coverage",
                "Establish change management processes",
                "Reduce staff turnover through retention programs",
                "Implement service monitoring and alerting"
            ],
            "compliance": [
                "Obtain SOC 2 Type II certification",
                "Ensure regulatory compliance",
                "Conduct regular compliance audits",
                "Establish compliance monitoring procedures"
            ],
            "business_continuity": [
                "Develop comprehensive business continuity plan",
                "Conduct regular BCP testing",
                "Implement disaster recovery procedures",
                "Establish redundant infrastructure",
                "Define and test recovery time objectives"
            ]
        }
        
        return recommendations.get(category, [])
    
    def _generate_action_items(
        self,
        category_scores: Dict[str, float],
        findings: List[Dict[str, Any]],
        vendor_tier: VendorTier
    ) -> List[Dict[str, Any]]:
        """Generate action items based on assessment results"""
        
        action_items = []
        
        # High priority items for critical/high findings
        critical_findings = [
            f for f in findings 
            if f.get("impact") in ["critical", "high"] and f.get("score", 100) < 40
        ]
        
        for finding in critical_findings:
            due_date = datetime.utcnow() + timedelta(days=30)
            if vendor_tier in [VendorTier.CRITICAL, VendorTier.HIGH]:
                due_date = datetime.utcnow() + timedelta(days=14)
            
            action_items.append({
                "title": f"Address {finding['category']} Issue",
                "description": finding.get("weakness", "Critical finding requiring attention"),
                "category": finding["category"],
                "priority": RiskLevel.CRITICAL if finding.get("impact") == "critical" else RiskLevel.HIGH,
                "due_date": due_date
            })
        
        # Medium priority items for low-scoring categories
        for category, score in category_scores.items():
            if score < 60:
                due_date = datetime.utcnow() + timedelta(days=90)
                action_items.append({
                    "title": f"Improve {category.replace('_', ' ').title()}",
                    "description": f"Category scored {score:.1f}% - improvement needed",
                    "category": category,
                    "priority": RiskLevel.MEDIUM,
                    "due_date": due_date
                })
        
        return action_items
    
    def monitor_vendor_performance(self, vendor_id: int) -> Dict[str, Any]:
        """Monitor ongoing vendor performance and compliance"""
        
        try:
            vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
            if not vendor:
                raise ValueError(f"Vendor with ID {vendor_id} not found")
            
            monitoring = self.db.query(VendorMonitoring).filter(
                VendorMonitoring.vendor_id == vendor_id
            ).first()
            
            if not monitoring:
                # Create new monitoring record
                monitoring = VendorMonitoring(
                    vendor_id=vendor_id,
                    monitoring_type="comprehensive",
                    monitoring_frequency="daily",
                    status=MonitoringStatus.ACTIVE
                )
                self.db.add(monitoring)
            
            # Perform monitoring checks
            monitoring_results = {
                "vendor_id": vendor.vendor_id,
                "monitoring_timestamp": datetime.utcnow(),
                "checks_performed": []
            }
            
            # Security monitoring
            security_check = self._check_security_posture(vendor)
            monitoring.security_posture_score = security_check["score"]
            monitoring_results["checks_performed"].append(security_check)
            
            # Availability monitoring
            availability_check = self._check_service_availability(vendor)
            monitoring.service_availability = availability_check["availability"]
            monitoring_results["checks_performed"].append(availability_check)
            
            # Compliance monitoring
            compliance_check = self._check_compliance_status(vendor)
            monitoring.compliance_status = compliance_check["status"]
            monitoring_results["checks_performed"].append(compliance_check)
            
            # Financial monitoring
            financial_check = self._check_financial_health(vendor)
            monitoring.financial_health_score = financial_check["score"]
            monitoring.credit_rating = financial_check.get("credit_rating")
            monitoring_results["checks_performed"].append(financial_check)
            
            # News sentiment monitoring
            news_check = self._check_news_sentiment(vendor)
            monitoring.news_sentiment = news_check["sentiment"]
            monitoring_results["checks_performed"].append(news_check)
            
            # Update monitoring record
            monitoring.last_check_date = datetime.utcnow()
            monitoring.next_check_date = datetime.utcnow() + timedelta(days=1)
            
            # Generate alerts if necessary
            alerts = self._generate_monitoring_alerts(monitoring, monitoring_results)
            monitoring_results["alerts_generated"] = len(alerts)
            
            self.db.commit()
            
            return monitoring_results
            
        except Exception as e:
            logger.error(f"Error monitoring vendor performance: {str(e)}")
            self.db.rollback()
            raise
    
    def _check_security_posture(self, vendor: Vendor) -> Dict[str, Any]:
        """Check vendor security posture"""
        
        # Simulate security posture check
        # In real implementation, this would integrate with security scanning tools
        
        security_score = 85.0  # Placeholder
        
        return {
            "check_type": "security_posture",
            "score": security_score,
            "status": "good" if security_score > 70 else "needs_attention",
            "details": {
                "certificate_status": "valid",
                "vulnerability_scan": "passed",
                "compliance_check": "compliant"
            }
        }
    
    def _check_service_availability(self, vendor: Vendor) -> Dict[str, Any]:
        """Check service availability"""
        
        # Simulate availability check
        availability = 99.5  # Placeholder
        
        return {
            "check_type": "availability",
            "availability": availability,
            "status": "excellent" if availability > 99 else "good",
            "details": {
                "uptime_percentage": availability,
                "response_time_ms": 250,
                "last_incident": None
            }
        }
    
    def _check_compliance_status(self, vendor: Vendor) -> Dict[str, Any]:
        """Check compliance status"""
        
        # Simulate compliance check
        status = ComplianceStatus.COMPLIANT
        
        return {
            "check_type": "compliance",
            "status": status,
            "details": {
                "certifications_valid": True,
                "audit_findings": [],
                "regulatory_changes": []
            }
        }
    
    def _check_financial_health(self, vendor: Vendor) -> Dict[str, Any]:
        """Check financial health"""
        
        # Simulate financial health check
        score = 80.0
        
        return {
            "check_type": "financial_health",
            "score": score,
            "credit_rating": "A-",
            "status": "stable",
            "details": {
                "payment_history": "good",
                "financial_trends": "positive",
                "bankruptcy_risk": "low"
            }
        }
    
    def _check_news_sentiment(self, vendor: Vendor) -> Dict[str, Any]:
        """Check news sentiment"""
        
        # Simulate news sentiment analysis
        sentiment = 0.2  # Slightly positive
        
        return {
            "check_type": "news_sentiment",
            "sentiment": sentiment,
            "status": "positive" if sentiment > 0 else "negative",
            "details": {
                "articles_analyzed": 15,
                "positive_mentions": 8,
                "negative_mentions": 2,
                "neutral_mentions": 5
            }
        }
    
    def _generate_monitoring_alerts(
        self,
        monitoring: VendorMonitoring,
        results: Dict[str, Any]
    ) -> List[VendorAlert]:
        """Generate alerts based on monitoring results"""
        
        alerts = []
        
        # Check for threshold breaches
        if monitoring.security_posture_score and monitoring.security_posture_score < 70:
            alert = VendorAlert(
                monitoring_id=monitoring.id,
                alert_type="security_threshold",
                severity=RiskLevel.HIGH,
                title="Security Posture Below Threshold",
                description=f"Security score: {monitoring.security_posture_score}%",
                current_value=monitoring.security_posture_score,
                threshold_value=70.0
            )
            self.db.add(alert)
            alerts.append(alert)
        
        if monitoring.service_availability and monitoring.service_availability < 99:
            alert = VendorAlert(
                monitoring_id=monitoring.id,
                alert_type="availability_threshold",
                severity=RiskLevel.MEDIUM,
                title="Service Availability Below SLA",
                description=f"Availability: {monitoring.service_availability}%",
                current_value=monitoring.service_availability,
                threshold_value=99.0
            )
            self.db.add(alert)
            alerts.append(alert)
        
        if monitoring.news_sentiment and monitoring.news_sentiment < -0.5:
            alert = VendorAlert(
                monitoring_id=monitoring.id,
                alert_type="reputation_risk",
                severity=RiskLevel.MEDIUM,
                title="Negative News Sentiment",
                description=f"News sentiment: {monitoring.news_sentiment}",
                current_value=monitoring.news_sentiment,
                threshold_value=-0.5
            )
            self.db.add(alert)
            alerts.append(alert)
        
        return alerts
    
    def calculate_portfolio_risk(self) -> Dict[str, Any]:
        """Calculate overall third-party risk portfolio metrics"""
        
        try:
            vendors = self.db.query(Vendor).filter(Vendor.status == VendorStatus.ACTIVE).all()
            
            if not vendors:
                return {"error": "No active vendors found"}
            
            # Calculate portfolio metrics
            total_vendors = len(vendors)
            total_contract_value = sum(v.contract_value_annual or 0 for v in vendors)
            avg_risk_score = sum(v.overall_risk_score or 0 for v in vendors) / total_vendors
            
            # Risk distribution
            risk_distribution = {
                "critical": len([v for v in vendors if (v.overall_risk_score or 0) >= 80]),
                "high": len([v for v in vendors if 60 <= (v.overall_risk_score or 0) < 80]),
                "medium": len([v for v in vendors if 40 <= (v.overall_risk_score or 0) < 60]),
                "low": len([v for v in vendors if (v.overall_risk_score or 0) < 40])
            }
            
            # Tier distribution
            tier_distribution = {}
            for tier in VendorTier:
                tier_distribution[tier.value] = len([v for v in vendors if v.tier == tier])
            
            # Concentration risk (top 10 vendors by contract value)
            top_vendors = sorted(vendors, key=lambda x: x.contract_value_annual or 0, reverse=True)[:10]
            concentration_value = sum(v.contract_value_annual or 0 for v in top_vendors)
            concentration_percentage = (concentration_value / total_contract_value * 100) if total_contract_value > 0 else 0
            
            # Overdue assessments
            overdue_assessments = self.db.query(Vendor).filter(
                Vendor.next_assessment_due < datetime.utcnow(),
                Vendor.status == VendorStatus.ACTIVE
            ).count()
            
            return {
                "portfolio_summary": {
                    "total_vendors": total_vendors,
                    "total_contract_value": total_contract_value,
                    "average_risk_score": round(avg_risk_score, 2),
                    "concentration_risk_percentage": round(concentration_percentage, 2)
                },
                "risk_distribution": risk_distribution,
                "tier_distribution": tier_distribution,
                "key_metrics": {
                    "overdue_assessments": overdue_assessments,
                    "high_risk_vendors": risk_distribution["critical"] + risk_distribution["high"],
                    "critical_vendors": len([v for v in vendors if v.tier == VendorTier.CRITICAL])
                },
                "top_risk_vendors": [
                    {
                        "vendor_id": v.vendor_id,
                        "name": v.name,
                        "risk_score": v.overall_risk_score,
                        "tier": v.tier.value,
                        "contract_value": v.contract_value_annual
                    }
                    for v in sorted(vendors, key=lambda x: x.overall_risk_score or 0, reverse=True)[:10]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {str(e)}")
            raise