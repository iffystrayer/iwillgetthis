"""
Compliance Assessment and Management Engine
Advanced compliance framework assessment, gap analysis, and continuous monitoring
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import math
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from models.compliance import (
    ComplianceFrameworkModel, ComplianceControl, ComplianceRequirement,
    ComplianceAssessment, ControlAssessment, RequirementAssessment,
    ComplianceFinding, ComplianceEvidence, ComplianceException,
    ComplianceMetric, ComplianceFramework, ComplianceStatus,
    ControlType, TestingFrequency, EvidenceType
)


class AssessmentMethodology(Enum):
    """Compliance assessment methodologies"""
    NIST_SP_800_53A = "nist_sp_800_53a"
    ISO_27001_AUDIT = "iso_27001_audit"
    SOC_2_EXAMINATION = "soc_2_examination"
    PCI_DSS_ASSESSMENT = "pci_dss_assessment"
    CUSTOM_METHODOLOGY = "custom_methodology"
    AUTOMATED_SCANNING = "automated_scanning"
    CONTINUOUS_MONITORING = "continuous_monitoring"


class MaturityLevel(Enum):
    """Control maturity levels"""
    INITIAL = 1          # Ad hoc, reactive
    DEVELOPING = 2       # Documented, some implementation
    DEFINED = 3          # Standardized, consistent implementation
    MANAGED = 4          # Measured, monitored
    OPTIMIZED = 5        # Continuous improvement


@dataclass
class AssessmentContext:
    """Context for compliance assessment"""
    framework_id: int
    assessment_scope: List[str]
    methodology: AssessmentMethodology
    assessment_period: Tuple[datetime, datetime]
    business_context: Optional[Dict[str, Any]] = None
    risk_tolerance: str = "medium"
    automated_testing_enabled: bool = True
    continuous_monitoring: bool = False


@dataclass
class ControlAssessmentResult:
    """Individual control assessment result"""
    control_id: int
    compliance_status: ComplianceStatus
    effectiveness_rating: str
    maturity_level: int
    compliance_score: float
    implementation_percentage: float
    confidence_level: str
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    evidence_collected: List[str]
    assessment_details: Dict[str, Any]


@dataclass
class ComplianceGapAnalysis:
    """Compliance gap analysis results"""
    framework_id: int
    overall_compliance_percentage: float
    compliant_controls: int
    non_compliant_controls: int
    partially_compliant_controls: int
    not_assessed_controls: int
    critical_gaps: List[Dict[str, Any]]
    high_priority_gaps: List[Dict[str, Any]]
    remediation_roadmap: List[Dict[str, Any]]
    estimated_remediation_effort: Dict[str, Any]


@dataclass
class ComplianceScorecard:
    """Comprehensive compliance scorecard"""
    framework_id: int
    assessment_id: int
    overall_score: float
    maturity_score: float
    effectiveness_score: float
    implementation_score: float
    control_family_scores: Dict[str, float]
    trend_analysis: Dict[str, Any]
    benchmark_comparison: Dict[str, Any]
    executive_summary: str


class ComplianceEngine:
    """Comprehensive compliance assessment and management engine"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Assessment scoring weights
        self.scoring_weights = {
            "implementation": 0.4,
            "effectiveness": 0.3,
            "documentation": 0.2,
            "testing": 0.1
        }
        
        # Maturity level criteria
        self.maturity_criteria = {
            1: {"implementation": 0.2, "documentation": 0.1, "testing": 0.0},
            2: {"implementation": 0.4, "documentation": 0.3, "testing": 0.1},
            3: {"implementation": 0.6, "documentation": 0.5, "testing": 0.3},
            4: {"implementation": 0.8, "documentation": 0.7, "testing": 0.6},
            5: {"implementation": 0.95, "documentation": 0.9, "testing": 0.8}
        }
        
        # Control family mappings for different frameworks
        self.control_families = {
            ComplianceFramework.NIST_800_53: {
                "AC": "Access Control",
                "AT": "Awareness and Training",
                "AU": "Audit and Accountability",
                "CA": "Assessment, Authorization, and Monitoring",
                "CM": "Configuration Management",
                "CP": "Contingency Planning",
                "IA": "Identification and Authentication",
                "IR": "Incident Response",
                "MA": "Maintenance",
                "MP": "Media Protection",
                "PE": "Physical and Environmental Protection",
                "PL": "Planning",
                "PS": "Personnel Security",
                "RA": "Risk Assessment",
                "SA": "System and Services Acquisition",
                "SC": "System and Communications Protection",
                "SI": "System and Information Integrity"
            },
            ComplianceFramework.ISO_27001: {
                "A.5": "Information Security Policies",
                "A.6": "Organization of Information Security",
                "A.7": "Human Resource Security",
                "A.8": "Asset Management",
                "A.9": "Access Control",
                "A.10": "Cryptography",
                "A.11": "Physical and Environmental Security",
                "A.12": "Operations Security",
                "A.13": "Communications Security",
                "A.14": "System Acquisition, Development and Maintenance",
                "A.15": "Supplier Relationships",
                "A.16": "Information Security Incident Management",
                "A.17": "Information Security Aspects of Business Continuity Management",
                "A.18": "Compliance"
            }
        }
        
        # Risk scoring thresholds
        self.risk_thresholds = {
            "critical": {"min": 9.0, "max": 10.0},
            "high": {"min": 7.0, "max": 8.9},
            "medium": {"min": 4.0, "max": 6.9},
            "low": {"min": 0.1, "max": 3.9}
        }
    
    def conduct_compliance_assessment(
        self,
        context: AssessmentContext,
        assessment_name: str,
        assessor_id: int
    ) -> ComplianceAssessment:
        """Conduct comprehensive compliance assessment"""
        
        # Create assessment record
        assessment = ComplianceAssessment(
            assessment_id=f"ASSESS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            framework_id=context.framework_id,
            assessment_name=assessment_name,
            assessment_type="comprehensive",
            assessment_scope=json.dumps(context.assessment_scope),
            start_date=context.assessment_period[0],
            planned_completion_date=context.assessment_period[1],
            lead_assessor=assessor_id,
            status="in_progress",
            assessment_methodology=context.methodology.value
        )
        
        self.db.add(assessment)
        self.db.commit()
        
        # Get framework and controls
        framework = self.db.query(ComplianceFrameworkModel).filter(
            ComplianceFrameworkModel.id == context.framework_id
        ).first()
        
        if not framework:
            raise ValueError(f"Framework {context.framework_id} not found")
        
        controls = self.db.query(ComplianceControl).filter(
            ComplianceControl.framework_id == context.framework_id,
            ComplianceControl.active == True
        ).all()
        
        # Assess each control
        control_results = []
        for control in controls:
            if self._is_control_in_scope(control, context.assessment_scope):
                result = self._assess_control(control, context, assessment.id)
                control_results.append(result)
        
        # Calculate overall assessment results
        self._calculate_assessment_summary(assessment, control_results)
        
        # Generate findings and recommendations
        self._generate_assessment_findings(assessment, control_results)
        
        # Update assessment status
        assessment.status = "completed"
        assessment.end_date = datetime.now()
        assessment.progress_percentage = 100
        
        self.db.commit()
        
        return assessment
    
    def _assess_control(
        self,
        control: ComplianceControl,
        context: AssessmentContext,
        assessment_id: int
    ) -> ControlAssessmentResult:
        """Assess individual compliance control"""
        
        # Determine assessment method based on control type and automation capability
        assessment_method = self._determine_assessment_method(control, context)
        
        # Collect and analyze evidence
        evidence_analysis = self._analyze_control_evidence(control, context)
        
        # Calculate implementation percentage
        implementation_percentage = self._calculate_implementation_percentage(
            control, evidence_analysis
        )
        
        # Determine compliance status
        compliance_status = self._determine_compliance_status(
            implementation_percentage, evidence_analysis
        )
        
        # Calculate effectiveness rating
        effectiveness_rating = self._calculate_effectiveness_rating(
            control, evidence_analysis, implementation_percentage
        )
        
        # Determine maturity level
        maturity_level = self._determine_maturity_level(
            control, implementation_percentage, evidence_analysis
        )
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            implementation_percentage, effectiveness_rating, maturity_level
        )
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(
            evidence_analysis, assessment_method
        )
        
        # Identify findings and recommendations
        findings = self._identify_control_findings(
            control, compliance_status, evidence_analysis
        )
        recommendations = self._generate_control_recommendations(
            control, findings, maturity_level
        )
        
        # Create control assessment record
        control_assessment = ControlAssessment(
            assessment_id=assessment_id,
            control_id=control.id,
            assessment_date=datetime.now(),
            assessor=context.business_context.get("assessor_id") if context.business_context else None,
            assessment_method=assessment_method,
            compliance_status=compliance_status,
            effectiveness_rating=effectiveness_rating,
            confidence_level=confidence_level,
            compliance_score=compliance_score,
            maturity_level=maturity_level,
            implementation_percentage=implementation_percentage,
            testing_performed=evidence_analysis.get("testing_summary", ""),
            evidence_reviewed=evidence_analysis.get("evidence_summary", ""),
            assessment_notes=evidence_analysis.get("assessment_notes", ""),
            deficiencies_identified=json.dumps([f["description"] for f in findings]),
            recommendations=json.dumps(recommendations)
        )
        
        self.db.add(control_assessment)
        
        return ControlAssessmentResult(
            control_id=control.id,
            compliance_status=compliance_status,
            effectiveness_rating=effectiveness_rating,
            maturity_level=maturity_level,
            compliance_score=compliance_score,
            implementation_percentage=implementation_percentage,
            confidence_level=confidence_level,
            findings=findings,
            recommendations=recommendations,
            evidence_collected=evidence_analysis.get("evidence_list", []),
            assessment_details={
                "assessment_method": assessment_method,
                "testing_performed": evidence_analysis.get("testing_summary", ""),
                "limitations": evidence_analysis.get("limitations", "")
            }
        )
    
    def _determine_assessment_method(
        self,
        control: ComplianceControl,
        context: AssessmentContext
    ) -> str:
        """Determine appropriate assessment method for control"""
        
        if context.automated_testing_enabled and control.automated_testing:
            return "automated_testing"
        elif control.control_type == ControlType.TECHNICAL:
            return "technical_testing"
        elif control.control_type == ControlType.ADMINISTRATIVE:
            return "document_review"
        elif control.control_type == ControlType.PHYSICAL:
            return "physical_inspection"
        else:
            return "interview_and_observation"
    
    def _analyze_control_evidence(
        self,
        control: ComplianceControl,
        context: AssessmentContext
    ) -> Dict[str, Any]:
        """Analyze available evidence for control"""
        
        # Get existing evidence
        evidence = self.db.query(ComplianceEvidence).filter(
            ComplianceEvidence.control_id == control.id,
            ComplianceEvidence.active == True
        ).all()
        
        evidence_analysis = {
            "evidence_list": [],
            "evidence_quality_score": 0.0,
            "documentation_completeness": 0.0,
            "testing_evidence_available": False,
            "implementation_evidence": [],
            "testing_summary": "",
            "evidence_summary": "",
            "assessment_notes": "",
            "limitations": []
        }
        
        if not evidence:
            evidence_analysis["limitations"].append("No evidence available for review")
            evidence_analysis["evidence_quality_score"] = 0.1
            return evidence_analysis
        
        # Analyze evidence quality and completeness
        for ev in evidence:
            evidence_analysis["evidence_list"].append({
                "type": ev.evidence_type.value,
                "name": ev.evidence_name,
                "collection_date": ev.collection_date.isoformat(),
                "validated": ev.validated
            })
            
            if ev.evidence_type in [EvidenceType.DOCUMENT, EvidenceType.POLICY]:
                evidence_analysis["documentation_completeness"] += 0.2
            elif ev.evidence_type in [EvidenceType.TEST_RESULT, EvidenceType.AUDIT_REPORT]:
                evidence_analysis["testing_evidence_available"] = True
                evidence_analysis["documentation_completeness"] += 0.3
            elif ev.evidence_type in [EvidenceType.CONFIGURATION, EvidenceType.LOG_FILE]:
                evidence_analysis["implementation_evidence"].append(ev.evidence_name)
                evidence_analysis["documentation_completeness"] += 0.25
        
        # Cap documentation completeness at 1.0
        evidence_analysis["documentation_completeness"] = min(1.0, evidence_analysis["documentation_completeness"])
        
        # Calculate overall evidence quality score
        quality_factors = [
            evidence_analysis["documentation_completeness"],
            1.0 if evidence_analysis["testing_evidence_available"] else 0.5,
            min(1.0, len(evidence_analysis["implementation_evidence"]) * 0.3)
        ]
        
        evidence_analysis["evidence_quality_score"] = sum(quality_factors) / len(quality_factors)
        
        # Generate summaries
        evidence_analysis["evidence_summary"] = f"Reviewed {len(evidence)} pieces of evidence"
        evidence_analysis["testing_summary"] = "Testing evidence available" if evidence_analysis["testing_evidence_available"] else "No testing evidence"
        
        return evidence_analysis
    
    def _calculate_implementation_percentage(
        self,
        control: ComplianceControl,
        evidence_analysis: Dict[str, Any]
    ) -> float:
        """Calculate control implementation percentage"""
        
        base_implementation = 0.0
        
        # Base implementation from control status
        if control.implementation_status == ComplianceStatus.COMPLIANT:
            base_implementation = 0.9
        elif control.implementation_status == ComplianceStatus.PARTIALLY_COMPLIANT:
            base_implementation = 0.6
        elif control.implementation_status == ComplianceStatus.NON_COMPLIANT:
            base_implementation = 0.2
        else:
            base_implementation = 0.4  # Not assessed
        
        # Adjust based on evidence quality
        evidence_multiplier = evidence_analysis["evidence_quality_score"]
        
        # Adjust based on documentation completeness
        documentation_multiplier = evidence_analysis["documentation_completeness"]
        
        # Calculate weighted implementation percentage
        implementation_percentage = (
            base_implementation * 0.5 +
            evidence_multiplier * 0.3 +
            documentation_multiplier * 0.2
        ) * 100
        
        return min(100.0, max(0.0, implementation_percentage))
    
    def _determine_compliance_status(
        self,
        implementation_percentage: float,
        evidence_analysis: Dict[str, Any]
    ) -> ComplianceStatus:
        """Determine compliance status based on implementation and evidence"""
        
        if implementation_percentage >= 85 and evidence_analysis["evidence_quality_score"] >= 0.7:
            return ComplianceStatus.COMPLIANT
        elif implementation_percentage >= 60:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        elif implementation_percentage < 30:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.REQUIRES_REVIEW
    
    def _calculate_effectiveness_rating(
        self,
        control: ComplianceControl,
        evidence_analysis: Dict[str, Any],
        implementation_percentage: float
    ) -> str:
        """Calculate control effectiveness rating"""
        
        effectiveness_score = 0.0
        
        # Base effectiveness from implementation
        effectiveness_score += (implementation_percentage / 100) * 0.4
        
        # Testing evidence bonus
        if evidence_analysis["testing_evidence_available"]:
            effectiveness_score += 0.3
        
        # Documentation quality
        effectiveness_score += evidence_analysis["documentation_completeness"] * 0.2
        
        # Control type considerations
        if control.control_type == ControlType.PREVENTIVE:
            effectiveness_score += 0.1  # Preventive controls get bonus
        
        if effectiveness_score >= 0.8:
            return "effective"
        elif effectiveness_score >= 0.6:
            return "partially_effective"
        else:
            return "ineffective"
    
    def _determine_maturity_level(
        self,
        control: ComplianceControl,
        implementation_percentage: float,
        evidence_analysis: Dict[str, Any]
    ) -> int:
        """Determine control maturity level (1-5)"""
        
        implementation_score = implementation_percentage / 100
        documentation_score = evidence_analysis["documentation_completeness"]
        testing_score = 1.0 if evidence_analysis["testing_evidence_available"] else 0.0
        
        # Compare against maturity criteria
        for level in range(5, 0, -1):
            criteria = self.maturity_criteria[level]
            if (implementation_score >= criteria["implementation"] and
                documentation_score >= criteria["documentation"] and
                testing_score >= criteria["testing"]):
                return level
        
        return 1  # Default to initial level
    
    def _calculate_compliance_score(
        self,
        implementation_percentage: float,
        effectiveness_rating: str,
        maturity_level: int
    ) -> float:
        """Calculate overall compliance score for control"""
        
        implementation_score = implementation_percentage / 100
        
        effectiveness_scores = {
            "effective": 1.0,
            "partially_effective": 0.7,
            "ineffective": 0.3
        }
        effectiveness_score = effectiveness_scores.get(effectiveness_rating, 0.5)
        
        maturity_score = maturity_level / 5.0
        
        # Weighted combination
        compliance_score = (
            implementation_score * self.scoring_weights["implementation"] +
            effectiveness_score * self.scoring_weights["effectiveness"] +
            maturity_score * 0.2 +
            0.8 * 0.1  # Documentation base score
        )
        
        return round(compliance_score * 10, 1)  # Scale to 0-10
    
    def _calculate_confidence_level(
        self,
        evidence_analysis: Dict[str, Any],
        assessment_method: str
    ) -> str:
        """Calculate confidence level in assessment"""
        
        confidence_score = 0.0
        
        # Evidence quality contribution
        confidence_score += evidence_analysis["evidence_quality_score"] * 0.4
        
        # Assessment method contribution
        method_scores = {
            "automated_testing": 0.9,
            "technical_testing": 0.8,
            "document_review": 0.6,
            "physical_inspection": 0.7,
            "interview_and_observation": 0.5
        }
        confidence_score += method_scores.get(assessment_method, 0.5) * 0.4
        
        # Documentation completeness
        confidence_score += evidence_analysis["documentation_completeness"] * 0.2
        
        if confidence_score >= 0.8:
            return "high"
        elif confidence_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _identify_control_findings(
        self,
        control: ComplianceControl,
        compliance_status: ComplianceStatus,
        evidence_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify findings for control assessment"""
        
        findings = []
        
        if compliance_status == ComplianceStatus.NON_COMPLIANT:
            findings.append({
                "type": "deficiency",
                "severity": "high",
                "description": f"Control {control.control_id} is not compliant",
                "impact": "High risk of control failure",
                "recommendation": "Implement missing control components"
            })
        
        if evidence_analysis["evidence_quality_score"] < 0.5:
            findings.append({
                "type": "observation",
                "severity": "medium",
                "description": "Insufficient evidence to support control implementation",
                "impact": "Cannot verify control effectiveness",
                "recommendation": "Collect additional supporting evidence"
            })
        
        if not evidence_analysis["testing_evidence_available"]:
            findings.append({
                "type": "recommendation",
                "severity": "medium",
                "description": "No testing evidence available for control validation",
                "impact": "Control effectiveness cannot be verified through testing",
                "recommendation": "Implement regular testing procedures"
            })
        
        return findings
    
    def _generate_control_recommendations(
        self,
        control: ComplianceControl,
        findings: List[Dict[str, Any]],
        maturity_level: int
    ) -> List[str]:
        """Generate recommendations for control improvement"""
        
        recommendations = []
        
        # Maturity-based recommendations
        if maturity_level < 3:
            recommendations.append("Standardize control implementation procedures")
            recommendations.append("Develop comprehensive documentation")
        
        if maturity_level < 4:
            recommendations.append("Implement control monitoring and measurement")
            recommendations.append("Establish regular testing procedures")
        
        if maturity_level < 5:
            recommendations.append("Implement continuous improvement processes")
        
        # Finding-based recommendations
        for finding in findings:
            if finding["recommendation"] not in recommendations:
                recommendations.append(finding["recommendation"])
        
        # Control-specific recommendations
        if control.automated_testing and not control.automation_tool:
            recommendations.append("Implement automated testing tools")
        
        if not control.testing_methodology:
            recommendations.append("Define control testing methodology")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _is_control_in_scope(
        self,
        control: ComplianceControl,
        assessment_scope: List[str]
    ) -> bool:
        """Check if control is within assessment scope"""
        
        if not assessment_scope:
            return True  # No scope limitation
        
        # Check control family
        control_family = control.control_family
        if control_family in assessment_scope:
            return True
        
        # Check control ID
        if control.control_id in assessment_scope:
            return True
        
        # Check control type
        if control.control_type.value in assessment_scope:
            return True
        
        return False
    
    def _calculate_assessment_summary(
        self,
        assessment: ComplianceAssessment,
        control_results: List[ControlAssessmentResult]
    ):
        """Calculate assessment summary statistics"""
        
        if not control_results:
            return
        
        # Count by compliance status
        status_counts = {
            ComplianceStatus.COMPLIANT: 0,
            ComplianceStatus.NON_COMPLIANT: 0,
            ComplianceStatus.PARTIALLY_COMPLIANT: 0,
            ComplianceStatus.NOT_ASSESSED: 0
        }
        
        total_score = 0.0
        finding_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for result in control_results:
            status_counts[result.compliance_status] += 1
            total_score += result.compliance_score
            
            # Count findings by severity
            for finding in result.findings:
                severity = finding.get("severity", "low")
                if severity in finding_counts:
                    finding_counts[severity] += 1
        
        # Update assessment with summary data
        assessment.overall_compliance_score = total_score / len(control_results)
        assessment.compliant_controls = status_counts[ComplianceStatus.COMPLIANT]
        assessment.non_compliant_controls = status_counts[ComplianceStatus.NON_COMPLIANT]
        assessment.partially_compliant_controls = status_counts[ComplianceStatus.PARTIALLY_COMPLIANT]
        assessment.not_assessed_controls = status_counts[ComplianceStatus.NOT_ASSESSED]
        
        assessment.total_findings = sum(finding_counts.values())
        assessment.critical_findings = finding_counts["critical"]
        assessment.high_findings = finding_counts["high"]
        assessment.medium_findings = finding_counts["medium"]
        assessment.low_findings = finding_counts["low"]
    
    def _generate_assessment_findings(
        self,
        assessment: ComplianceAssessment,
        control_results: List[ControlAssessmentResult]
    ):
        """Generate assessment-level findings"""
        
        for result in control_results:
            for finding_data in result.findings:
                finding = ComplianceFinding(
                    finding_id=f"FIND-{assessment.assessment_id}-{result.control_id}-{datetime.now().strftime('%H%M%S')}",
                    assessment_id=assessment.id,
                    control_id=result.control_id,
                    finding_title=finding_data["description"],
                    finding_description=finding_data["description"],
                    finding_type=finding_data["type"],
                    severity=finding_data["severity"],
                    business_impact=finding_data.get("impact", ""),
                    remediation_plan=finding_data.get("recommendation", ""),
                    identified_date=datetime.now()
                )
                
                self.db.add(finding)
    
    def conduct_gap_analysis(
        self,
        framework_id: int,
        target_maturity_level: int = 3
    ) -> ComplianceGapAnalysis:
        """Conduct compliance gap analysis"""
        
        # Get latest assessment for framework
        latest_assessment = self.db.query(ComplianceAssessment).filter(
            ComplianceAssessment.framework_id == framework_id
        ).order_by(ComplianceAssessment.created_at.desc()).first()
        
        if not latest_assessment:
            raise ValueError("No assessment found for framework")
        
        # Get control assessments
        control_assessments = self.db.query(ControlAssessment).filter(
            ControlAssessment.assessment_id == latest_assessment.id
        ).all()
        
        # Calculate gap analysis
        total_controls = len(control_assessments)
        compliant_controls = sum(1 for ca in control_assessments 
                                if ca.compliance_status == ComplianceStatus.COMPLIANT)
        
        overall_compliance_percentage = (compliant_controls / total_controls * 100) if total_controls > 0 else 0
        
        # Identify gaps
        critical_gaps = []
        high_priority_gaps = []
        
        for ca in control_assessments:
            if ca.compliance_status == ComplianceStatus.NON_COMPLIANT:
                gap = {
                    "control_id": ca.control_id,
                    "control_title": ca.control.control_title,
                    "current_maturity": ca.maturity_level,
                    "target_maturity": target_maturity_level,
                    "gap_size": target_maturity_level - ca.maturity_level,
                    "remediation_effort": self._estimate_remediation_effort(ca, target_maturity_level)
                }
                
                if ca.control.priority == "critical" or gap["gap_size"] >= 3:
                    critical_gaps.append(gap)
                elif gap["gap_size"] >= 2:
                    high_priority_gaps.append(gap)
        
        # Generate remediation roadmap
        remediation_roadmap = self._generate_remediation_roadmap(
            critical_gaps + high_priority_gaps
        )
        
        return ComplianceGapAnalysis(
            framework_id=framework_id,
            overall_compliance_percentage=overall_compliance_percentage,
            compliant_controls=compliant_controls,
            non_compliant_controls=sum(1 for ca in control_assessments 
                                     if ca.compliance_status == ComplianceStatus.NON_COMPLIANT),
            partially_compliant_controls=sum(1 for ca in control_assessments 
                                           if ca.compliance_status == ComplianceStatus.PARTIALLY_COMPLIANT),
            not_assessed_controls=sum(1 for ca in control_assessments 
                                    if ca.compliance_status == ComplianceStatus.NOT_ASSESSED),
            critical_gaps=critical_gaps,
            high_priority_gaps=high_priority_gaps,
            remediation_roadmap=remediation_roadmap,
            estimated_remediation_effort=self._calculate_total_remediation_effort(remediation_roadmap)
        )
    
    def _estimate_remediation_effort(
        self,
        control_assessment: ControlAssessment,
        target_maturity: int
    ) -> Dict[str, Any]:
        """Estimate effort required to remediate control"""
        
        gap_size = target_maturity - control_assessment.maturity_level
        base_effort_days = gap_size * 5  # Base 5 days per maturity level
        
        # Adjust based on control complexity
        if control_assessment.control.control_type == ControlType.TECHNICAL:
            base_effort_days *= 1.5
        elif control_assessment.control.control_type == ControlType.ADMINISTRATIVE:
            base_effort_days *= 1.2
        
        return {
            "estimated_days": base_effort_days,
            "estimated_cost": base_effort_days * 800,  # $800/day rate
            "complexity": "high" if gap_size >= 3 else "medium" if gap_size >= 2 else "low",
            "dependencies": []
        }
    
    def _generate_remediation_roadmap(
        self,
        gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized remediation roadmap"""
        
        # Sort gaps by priority (gap size and control priority)
        sorted_gaps = sorted(gaps, key=lambda x: (x["gap_size"], x["control_id"]), reverse=True)
        
        roadmap = []
        current_quarter = 1
        current_effort = 0
        max_quarterly_effort = 120  # Max 120 days per quarter
        
        for gap in sorted_gaps:
            effort = gap["remediation_effort"]["estimated_days"]
            
            if current_effort + effort > max_quarterly_effort:
                current_quarter += 1
                current_effort = 0
            
            roadmap_item = {
                "control_id": gap["control_id"],
                "control_title": gap["control_title"],
                "priority": gap["gap_size"],
                "quarter": f"Q{current_quarter}",
                "effort_days": effort,
                "estimated_cost": gap["remediation_effort"]["estimated_cost"],
                "dependencies": gap["remediation_effort"]["dependencies"]
            }
            
            roadmap.append(roadmap_item)
            current_effort += effort
        
        return roadmap
    
    def _calculate_total_remediation_effort(
        self,
        roadmap: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate total remediation effort and cost"""
        
        total_days = sum(item["effort_days"] for item in roadmap)
        total_cost = sum(item["estimated_cost"] for item in roadmap)
        
        quarters = set(item["quarter"] for item in roadmap)
        
        return {
            "total_effort_days": total_days,
            "total_estimated_cost": total_cost,
            "estimated_duration_quarters": len(quarters),
            "average_quarterly_effort": total_days / len(quarters) if quarters else 0
        }
    
    def generate_compliance_scorecard(
        self,
        framework_id: int,
        assessment_id: int
    ) -> ComplianceScorecard:
        """Generate comprehensive compliance scorecard"""
        
        assessment = self.db.query(ComplianceAssessment).filter(
            ComplianceAssessment.id == assessment_id
        ).first()
        
        if not assessment:
            raise ValueError("Assessment not found")
        
        control_assessments = self.db.query(ControlAssessment).filter(
            ControlAssessment.assessment_id == assessment_id
        ).all()
        
        # Calculate overall scores
        overall_score = assessment.overall_compliance_score
        
        maturity_scores = [ca.maturity_level for ca in control_assessments]
        maturity_score = sum(maturity_scores) / len(maturity_scores) if maturity_scores else 0
        
        implementation_scores = [ca.implementation_percentage for ca in control_assessments]
        implementation_score = sum(implementation_scores) / len(implementation_scores) if implementation_scores else 0
        
        effectiveness_ratings = [ca.effectiveness_rating for ca in control_assessments]
        effectiveness_score = sum(1 for rating in effectiveness_ratings if rating == "effective") / len(effectiveness_ratings) * 100 if effectiveness_ratings else 0
        
        # Calculate control family scores
        control_family_scores = self._calculate_control_family_scores(control_assessments)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            overall_score, assessment.total_findings, len(control_assessments)
        )
        
        return ComplianceScorecard(
            framework_id=framework_id,
            assessment_id=assessment_id,
            overall_score=overall_score,
            maturity_score=maturity_score,
            effectiveness_score=effectiveness_score,
            implementation_score=implementation_score,
            control_family_scores=control_family_scores,
            trend_analysis={},  # Could be implemented with historical data
            benchmark_comparison={},  # Could be implemented with industry benchmarks
            executive_summary=executive_summary
        )
    
    def _calculate_control_family_scores(
        self,
        control_assessments: List[ControlAssessment]
    ) -> Dict[str, float]:
        """Calculate scores by control family"""
        
        family_scores = {}
        family_counts = {}
        
        for ca in control_assessments:
            family = ca.control.control_family
            if family not in family_scores:
                family_scores[family] = 0.0
                family_counts[family] = 0
            
            family_scores[family] += ca.compliance_score
            family_counts[family] += 1
        
        # Calculate averages
        for family in family_scores:
            family_scores[family] = family_scores[family] / family_counts[family]
        
        return family_scores
    
    def _generate_executive_summary(
        self,
        overall_score: float,
        total_findings: int,
        total_controls: int
    ) -> str:
        """Generate executive summary for scorecard"""
        
        compliance_level = "Strong" if overall_score >= 8.0 else "Moderate" if overall_score >= 6.0 else "Weak"
        
        summary = f"""
        Compliance Assessment Executive Summary
        
        Overall Compliance Score: {overall_score:.1f}/10.0 ({compliance_level})
        
        Assessment Results:
        - Total Controls Assessed: {total_controls}
        - Total Findings Identified: {total_findings}
        - Compliance Level: {compliance_level}
        
        Key Observations:
        - {"Strong compliance posture with minor gaps" if overall_score >= 8.0 else 
           "Moderate compliance with several areas for improvement" if overall_score >= 6.0 else
           "Significant compliance gaps requiring immediate attention"}
        """
        
        return summary.strip()