"""Enhanced dashboard analytics service with comprehensive reporting and visualization data generation"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from collections import defaultdict

from models.user import User
from models.asset import Asset, AssetCriticality, AssetType
from models.risk import Risk, RiskStatus, RiskLevel
from models.task import Task, TaskStatus, TaskPriority
from models.assessment import Assessment, AssessmentControl, AssessmentStatus, ControlImplementationStatus
from models.framework import Framework
from models.evidence import Evidence, EvidenceStatus
from models.analytics import MetricValue, MetricDefinition
from enhanced_ai_service import enhanced_ai_service

logger = logging.getLogger(__name__)

class DashboardAnalyticsService:
    """Service for generating enhanced dashboard analytics and reporting data"""
    
    def __init__(self):
        self.metric_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        self.last_cache_update = {}
    
    async def generate_executive_dashboard(self, db: Session, time_range: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive executive dashboard with AI-powered insights"""
        
        try:
            # Calculate date range
            days = self._parse_time_range(time_range)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Core metrics
            core_metrics = await self._get_core_metrics(db, start_date)
            
            # Risk analytics
            risk_analytics = await self._get_risk_analytics(db, start_date)
            
            # Compliance posture
            compliance_posture = await self._get_compliance_posture(db)
            
            # Performance trends
            performance_trends = await self._get_performance_trends(db, start_date)
            
            # AI-powered insights
            ai_insights = await self._generate_ai_insights(db, core_metrics, risk_analytics)
            
            # Executive summary
            executive_summary = await self._generate_executive_summary(db, core_metrics, risk_analytics)
            
            # Critical alerts
            critical_alerts = await self._get_critical_alerts(db, start_date)
            
            return {
                "dashboard_type": "executive",
                "generated_at": datetime.utcnow().isoformat(),
                "time_range": time_range,
                "core_metrics": core_metrics,
                "risk_analytics": risk_analytics,
                "compliance_posture": compliance_posture,
                "performance_trends": performance_trends,
                "ai_insights": ai_insights,
                "executive_summary": executive_summary,
                "critical_alerts": critical_alerts,
                "recommendations": await self._get_executive_recommendations(db, risk_analytics)
            }
            
        except Exception as e:
            logger.error(f"Executive dashboard generation failed: {e}")
            raise
    
    async def generate_operational_dashboard(self, db: Session, user_id: int, time_range: str = "7d") -> Dict[str, Any]:
        """Generate operational dashboard for analysts and system owners"""
        
        try:
            days = self._parse_time_range(time_range)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # User-specific metrics
            user_metrics = await self._get_user_metrics(db, user_id, start_date)
            
            # Workload analytics
            workload_analytics = await self._get_workload_analytics(db, user_id)
            
            # Task performance
            task_performance = await self._get_task_performance(db, user_id, start_date)
            
            # Evidence analytics
            evidence_analytics = await self._get_evidence_analytics(db, start_date)
            
            # Assessment progress
            assessment_progress = await self._get_assessment_progress(db, start_date)
            
            # Team performance
            team_performance = await self._get_team_performance(db, start_date)
            
            return {
                "dashboard_type": "operational",
                "generated_at": datetime.utcnow().isoformat(),
                "time_range": time_range,
                "user_id": user_id,
                "user_metrics": user_metrics,
                "workload_analytics": workload_analytics,
                "task_performance": task_performance,
                "evidence_analytics": evidence_analytics,
                "assessment_progress": assessment_progress,
                "team_performance": team_performance,
                "productivity_insights": await self._generate_productivity_insights(db, user_id, task_performance)
            }
            
        except Exception as e:
            logger.error(f"Operational dashboard generation failed: {e}")
            raise
    
    async def generate_risk_dashboard(self, db: Session, time_range: str = "90d") -> Dict[str, Any]:
        """Generate comprehensive risk management dashboard"""
        
        try:
            days = self._parse_time_range(time_range)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Risk portfolio analytics
            risk_portfolio = await self._get_risk_portfolio_analytics(db, start_date)
            
            # Risk heat map
            risk_heat_map = await self._generate_risk_heat_map(db)
            
            # Risk velocity
            risk_velocity = await self._get_risk_velocity(db, start_date)
            
            # Risk treatment effectiveness
            treatment_effectiveness = await self._get_risk_treatment_effectiveness(db, start_date)
            
            # Risk forecasting
            risk_forecast = await self._generate_risk_forecast(db, start_date)
            
            # Top risk scenarios
            top_risk_scenarios = await self._get_top_risk_scenarios(db)
            
            # Risk maturity assessment
            risk_maturity = await self._assess_risk_maturity(db)
            
            return {
                "dashboard_type": "risk",
                "generated_at": datetime.utcnow().isoformat(),
                "time_range": time_range,
                "risk_portfolio": risk_portfolio,
                "risk_heat_map": risk_heat_map,
                "risk_velocity": risk_velocity,
                "treatment_effectiveness": treatment_effectiveness,
                "risk_forecast": risk_forecast,
                "top_risk_scenarios": top_risk_scenarios,
                "risk_maturity": risk_maturity,
                "risk_appetite_analysis": await self._analyze_risk_appetite(db, risk_portfolio)
            }
            
        except Exception as e:
            logger.error(f"Risk dashboard generation failed: {e}")
            raise
    
    async def generate_compliance_dashboard(self, db: Session, framework_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate comprehensive compliance dashboard"""
        
        try:
            # Compliance posture
            compliance_posture = await self._get_detailed_compliance_posture(db, framework_id)
            
            # Control effectiveness
            control_effectiveness = await self._get_control_effectiveness(db, framework_id)
            
            # Compliance trends
            compliance_trends = await self._get_compliance_trends(db, framework_id)
            
            # Gap analysis
            gap_analysis = await self._perform_compliance_gap_analysis(db, framework_id)
            
            # Evidence coverage
            evidence_coverage = await self._get_evidence_coverage(db, framework_id)
            
            # Regulatory changes impact
            regulatory_impact = await self._assess_regulatory_impact(db)
            
            # Compliance forecast
            compliance_forecast = await self._forecast_compliance_readiness(db, framework_id)
            
            return {
                "dashboard_type": "compliance",
                "generated_at": datetime.utcnow().isoformat(),
                "framework_id": framework_id,
                "compliance_posture": compliance_posture,
                "control_effectiveness": control_effectiveness,
                "compliance_trends": compliance_trends,
                "gap_analysis": gap_analysis,
                "evidence_coverage": evidence_coverage,
                "regulatory_impact": regulatory_impact,
                "compliance_forecast": compliance_forecast,
                "remediation_roadmap": await self._generate_remediation_roadmap(db, gap_analysis)
            }
            
        except Exception as e:
            logger.error(f"Compliance dashboard generation failed: {e}")
            raise
    
    async def generate_security_metrics_dashboard(self, db: Session, time_range: str = "30d") -> Dict[str, Any]:
        """Generate security metrics and KPI dashboard"""
        
        try:
            days = self._parse_time_range(time_range)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Security metrics
            security_metrics = await self._get_security_metrics(db, start_date)
            
            # Incident response metrics
            incident_metrics = await self._get_incident_response_metrics(db, start_date)
            
            # Vulnerability management
            vulnerability_metrics = await self._get_vulnerability_metrics(db, start_date)
            
            # Security awareness metrics
            awareness_metrics = await self._get_security_awareness_metrics(db, start_date)
            
            # MTTR/MTTD analytics
            response_time_analytics = await self._get_response_time_analytics(db, start_date)
            
            # Security ROI
            security_roi = await self._calculate_security_roi(db, start_date)
            
            # Threat landscape
            threat_landscape = await self._analyze_threat_landscape(db, start_date)
            
            return {
                "dashboard_type": "security_metrics",
                "generated_at": datetime.utcnow().isoformat(),
                "time_range": time_range,
                "security_metrics": security_metrics,
                "incident_metrics": incident_metrics,
                "vulnerability_metrics": vulnerability_metrics,
                "awareness_metrics": awareness_metrics,
                "response_time_analytics": response_time_analytics,
                "security_roi": security_roi,
                "threat_landscape": threat_landscape,
                "security_posture_score": await self._calculate_security_posture_score(db, security_metrics)
            }
            
        except Exception as e:
            logger.error(f"Security metrics dashboard generation failed: {e}")
            raise
    
    # Core metric calculations
    async def _get_core_metrics(self, db: Session, start_date: datetime) -> Dict[str, Any]:
        """Get core organizational metrics"""
        
        # Asset metrics
        total_assets = db.query(func.count(Asset.id)).filter(Asset.is_active == True).scalar() or 0
        critical_assets = db.query(func.count(Asset.id)).filter(
            Asset.is_active == True,
            Asset.criticality == AssetCriticality.CRITICAL
        ).scalar() or 0
        
        # Risk metrics
        total_risks = db.query(func.count(Risk.id)).filter(Risk.is_active == True).scalar() or 0
        open_risks = db.query(func.count(Risk.id)).filter(
            Risk.is_active == True,
            Risk.status.in_([RiskStatus.IDENTIFIED, RiskStatus.ASSESSED, RiskStatus.MITIGATING])
        ).scalar() or 0
        
        high_risks = db.query(func.count(Risk.id)).filter(
            Risk.is_active == True,
            Risk.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).scalar() or 0
        
        # Task metrics
        total_tasks = db.query(func.count(Task.id)).filter(Task.is_active == True).scalar() or 0
        open_tasks = db.query(func.count(Task.id)).filter(
            Task.is_active == True,
            Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
        ).scalar() or 0
        
        overdue_tasks = db.query(func.count(Task.id)).filter(
            Task.is_active == True,
            Task.due_date < datetime.utcnow(),
            Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
        ).scalar() or 0
        
        # Assessment metrics
        total_assessments = db.query(func.count(Assessment.id)).filter(
            Assessment.is_active == True
        ).scalar() or 0
        
        completed_assessments = db.query(func.count(Assessment.id)).filter(
            Assessment.is_active == True,
            Assessment.status == AssessmentStatus.COMPLETED
        ).scalar() or 0
        
        # Calculate percentages
        critical_asset_percentage = (critical_assets / total_assets * 100) if total_assets > 0 else 0
        high_risk_percentage = (high_risks / total_risks * 100) if total_risks > 0 else 0
        overdue_task_percentage = (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0
        assessment_completion_rate = (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0
        
        # Recent activity
        new_risks_this_period = db.query(func.count(Risk.id)).filter(
            Risk.created_at >= start_date,
            Risk.is_active == True
        ).scalar() or 0
        
        tasks_completed_this_period = db.query(func.count(Task.id)).filter(
            Task.completed_at >= start_date,
            Task.status == TaskStatus.COMPLETED
        ).scalar() or 0
        
        return {
            "assets": {
                "total": total_assets,
                "critical": critical_assets,
                "critical_percentage": round(critical_asset_percentage, 1)
            },
            "risks": {
                "total": total_risks,
                "open": open_risks,
                "high_priority": high_risks,
                "high_priority_percentage": round(high_risk_percentage, 1),
                "new_this_period": new_risks_this_period
            },
            "tasks": {
                "total": total_tasks,
                "open": open_tasks,
                "overdue": overdue_tasks,
                "overdue_percentage": round(overdue_task_percentage, 1),
                "completed_this_period": tasks_completed_this_period
            },
            "assessments": {
                "total": total_assessments,
                "completed": completed_assessments,
                "completion_rate": round(assessment_completion_rate, 1)
            },
            "health_indicators": {
                "risk_health": "good" if high_risk_percentage < 10 else "warning" if high_risk_percentage < 20 else "critical",
                "task_health": "good" if overdue_task_percentage < 5 else "warning" if overdue_task_percentage < 15 else "critical",
                "compliance_health": "good" if assessment_completion_rate > 80 else "warning" if assessment_completion_rate > 60 else "critical"
            }
        }
    
    async def _get_risk_analytics(self, db: Session, start_date: datetime) -> Dict[str, Any]:
        """Get detailed risk analytics"""
        
        # Risk level distribution
        risk_distribution = db.query(
            Risk.risk_level,
            func.count(Risk.id).label('count')
        ).filter(
            Risk.is_active == True
        ).group_by(Risk.risk_level).all()
        
        # Risk trend over time (monthly)
        risk_trend = db.query(
            func.date_trunc('month', Risk.created_at).label('month'),
            func.count(Risk.id).label('count'),
            Risk.risk_level
        ).filter(
            Risk.created_at >= start_date,
            Risk.is_active == True
        ).group_by(
            func.date_trunc('month', Risk.created_at),
            Risk.risk_level
        ).all()
        
        # Risk by category
        risk_by_category = db.query(
            Risk.category,
            func.count(Risk.id).label('count'),
            func.avg(Risk.inherent_risk_score).label('avg_score')
        ).filter(
            Risk.is_active == True
        ).group_by(Risk.category).all()
        
        # Risk closure rate
        closed_risks = db.query(func.count(Risk.id)).filter(
            Risk.status == RiskStatus.CLOSED,
            Risk.closed_date >= start_date
        ).scalar() or 0
        
        total_risks_in_period = db.query(func.count(Risk.id)).filter(
            Risk.created_at >= start_date
        ).scalar() or 0
        
        closure_rate = (closed_risks / total_risks_in_period * 100) if total_risks_in_period > 0 else 0
        
        # Average risk resolution time
        avg_resolution_time = db.query(
            func.avg(
                func.extract('epoch', Risk.closed_date - Risk.created_at) / 86400
            )
        ).filter(
            Risk.status == RiskStatus.CLOSED,
            Risk.closed_date >= start_date
        ).scalar() or 0
        
        return {
            "distribution": [
                {"level": item.risk_level, "count": item.count}
                for item in risk_distribution
            ],
            "trend": [
                {
                    "month": item.month.strftime('%Y-%m'),
                    "count": item.count,
                    "risk_level": item.risk_level
                }
                for item in risk_trend
            ],
            "by_category": [
                {
                    "category": item.category,
                    "count": item.count,
                    "avg_score": round(float(item.avg_score or 0), 2)
                }
                for item in risk_by_category
            ],
            "closure_metrics": {
                "closure_rate": round(closure_rate, 1),
                "avg_resolution_days": round(float(avg_resolution_time or 0), 1),
                "closed_this_period": closed_risks
            }
        }
    
    async def _get_compliance_posture(self, db: Session) -> Dict[str, Any]:
        """Get overall compliance posture"""
        
        # Framework-wise compliance
        frameworks = db.query(Framework).filter(Framework.is_active == True).all()
        framework_compliance = []
        
        for framework in frameworks:
            total_controls = db.query(func.count(AssessmentControl.id)).join(Assessment).filter(
                Assessment.framework_id == framework.id,
                Assessment.is_active == True
            ).scalar() or 0
            
            implemented_controls = db.query(func.count(AssessmentControl.id)).join(Assessment).filter(
                Assessment.framework_id == framework.id,
                Assessment.is_active == True,
                AssessmentControl.implementation_status == ControlImplementationStatus.IMPLEMENTED
            ).scalar() or 0
            
            compliance_percentage = (implemented_controls / total_controls * 100) if total_controls > 0 else 0
            
            framework_compliance.append({
                "framework_id": framework.id,
                "framework_name": framework.name,
                "total_controls": total_controls,
                "implemented_controls": implemented_controls,
                "compliance_percentage": round(compliance_percentage, 1),
                "status": "compliant" if compliance_percentage >= 90 else "partially_compliant" if compliance_percentage >= 70 else "non_compliant"
            })
        
        # Overall compliance score
        total_controls_all = sum(f["total_controls"] for f in framework_compliance)
        total_implemented_all = sum(f["implemented_controls"] for f in framework_compliance)
        overall_compliance = (total_implemented_all / total_controls_all * 100) if total_controls_all > 0 else 0
        
        return {
            "overall_score": round(overall_compliance, 1),
            "frameworks": framework_compliance,
            "compliance_trend": await self._get_compliance_trend(db),
            "gaps_summary": await self._get_compliance_gaps_summary(db)
        }
    
    async def _get_performance_trends(self, db: Session, start_date: datetime) -> Dict[str, Any]:
        """Get performance trends over time"""
        
        # Calculate weekly performance metrics
        weeks = []
        current_date = start_date
        
        while current_date < datetime.utcnow():
            week_end = current_date + timedelta(days=7)
            
            # Tasks completed this week
            tasks_completed = db.query(func.count(Task.id)).filter(
                Task.completed_at >= current_date,
                Task.completed_at < week_end,
                Task.status == TaskStatus.COMPLETED
            ).scalar() or 0
            
            # New risks this week
            new_risks = db.query(func.count(Risk.id)).filter(
                Risk.created_at >= current_date,
                Risk.created_at < week_end,
                Risk.is_active == True
            ).scalar() or 0
            
            # Risks mitigated this week
            mitigated_risks = db.query(func.count(Risk.id)).filter(
                Risk.closed_date >= current_date,
                Risk.closed_date < week_end,
                Risk.status == RiskStatus.CLOSED
            ).scalar() or 0
            
            weeks.append({
                "week_start": current_date.strftime('%Y-%m-%d'),
                "tasks_completed": tasks_completed,
                "new_risks": new_risks,
                "mitigated_risks": mitigated_risks,
                "net_risk_reduction": mitigated_risks - new_risks
            })
            
            current_date = week_end
        
        return {
            "weekly_trends": weeks,
            "summary": {
                "avg_weekly_task_completion": sum(w["tasks_completed"] for w in weeks) / len(weeks) if weeks else 0,
                "total_risk_reduction": sum(w["net_risk_reduction"] for w in weeks),
                "trend_direction": "improving" if weeks and weeks[-1]["net_risk_reduction"] > 0 else "stable" if weeks and weeks[-1]["net_risk_reduction"] == 0 else "declining"
            }
        }
    
    async def _generate_ai_insights(self, db: Session, core_metrics: Dict[str, Any], risk_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights from the data"""
        
        insights = []
        
        try:
            # Prepare data for AI analysis
            metrics_summary = {
                "total_assets": core_metrics["assets"]["total"],
                "critical_assets": core_metrics["assets"]["critical"],
                "high_priority_risks": core_metrics["risks"]["high_priority"],
                "overdue_tasks": core_metrics["tasks"]["overdue"],
                "risk_closure_rate": risk_analytics["closure_metrics"]["closure_rate"],
                "avg_resolution_days": risk_analytics["closure_metrics"]["avg_resolution_days"]
            }
            
            # Generate insights using AI service
            ai_response = await enhanced_ai_service.generate_executive_summary(metrics_summary)
            
            if ai_response and isinstance(ai_response, dict):
                if "overview" in ai_response:
                    insights.append({
                        "type": "overview",
                        "priority": "high",
                        "title": "Current Risk Posture",
                        "description": ai_response["overview"],
                        "generated_at": datetime.utcnow().isoformat()
                    })
                
                if "concerns" in ai_response:
                    insights.append({
                        "type": "alert",
                        "priority": "critical",
                        "title": "Areas of Concern",
                        "description": ai_response["concerns"],
                        "generated_at": datetime.utcnow().isoformat()
                    })
                
                if "recommendations" in ai_response:
                    insights.append({
                        "type": "recommendation",
                        "priority": "medium",
                        "title": "Recommended Actions",
                        "description": ai_response["recommendations"],
                        "generated_at": datetime.utcnow().isoformat()
                    })
                    
        except Exception as e:
            logger.warning(f"AI insight generation failed: {e}")
            # Fallback to rule-based insights
            insights.extend(await self._generate_rule_based_insights(core_metrics, risk_analytics))
        
        return insights
    
    async def _generate_rule_based_insights(self, core_metrics: Dict[str, Any], risk_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate rule-based insights as fallback"""
        
        insights = []
        
        # High risk percentage insight
        if core_metrics["risks"]["high_priority_percentage"] > 20:
            insights.append({
                "type": "alert",
                "priority": "critical",
                "title": "High Risk Exposure",
                "description": f"High-priority risks represent {core_metrics['risks']['high_priority_percentage']:.1f}% of total risks, which exceeds the recommended threshold of 20%.",
                "generated_at": datetime.utcnow().isoformat()
            })
        
        # Overdue task insight
        if core_metrics["tasks"]["overdue_percentage"] > 10:
            insights.append({
                "type": "alert",
                "priority": "high",
                "title": "Task Management Issue",
                "description": f"{core_metrics['tasks']['overdue_percentage']:.1f}% of tasks are overdue, indicating potential resource constraints or process inefficiencies.",
                "generated_at": datetime.utcnow().isoformat()
            })
        
        # Risk closure rate insight
        if risk_analytics["closure_metrics"]["closure_rate"] < 50:
            insights.append({
                "type": "recommendation",
                "priority": "medium",
                "title": "Risk Closure Efficiency",
                "description": f"Risk closure rate of {risk_analytics['closure_metrics']['closure_rate']:.1f}% is below optimal levels. Consider reviewing risk treatment strategies.",
                "generated_at": datetime.utcnow().isoformat()
            })
        
        return insights
    
    async def _generate_executive_summary(self, db: Session, core_metrics: Dict[str, Any], risk_analytics: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        
        try:
            # Use AI service for intelligent summary
            summary_data = {
                "total_risks": core_metrics["risks"]["total"],
                "high_risks": core_metrics["risks"]["high_priority"],
                "overdue_tasks": core_metrics["tasks"]["overdue"],
                "closure_rate": risk_analytics["closure_metrics"]["closure_rate"],
                "new_risks": core_metrics["risks"]["new_this_period"]
            }
            
            ai_summary = await enhanced_ai_service.generate_executive_summary(summary_data)
            if ai_summary and isinstance(ai_summary, dict) and "overview" in ai_summary:
                return ai_summary["overview"]
                
        except Exception as e:
            logger.warning(f"AI summary generation failed: {e}")
        
        # Fallback summary
        return f"""Current cybersecurity posture shows {core_metrics['risks']['total']} total risks with {core_metrics['risks']['high_priority']} high-priority items requiring immediate attention. 
        Task management performance indicates {core_metrics['tasks']['overdue']} overdue items ({core_metrics['tasks']['overdue_percentage']:.1f}% of total). 
        Risk closure efficiency stands at {risk_analytics['closure_metrics']['closure_rate']:.1f}% with an average resolution time of {risk_analytics['closure_metrics']['avg_resolution_days']:.1f} days."""
    
    async def _get_critical_alerts(self, db: Session, start_date: datetime) -> List[Dict[str, Any]]:
        """Get critical alerts and notifications"""
        
        alerts = []
        
        # Critical risks created recently
        critical_risks = db.query(Risk).filter(
            Risk.risk_level == RiskLevel.CRITICAL,
            Risk.created_at >= start_date,
            Risk.is_active == True
        ).limit(5).all()
        
        for risk in critical_risks:
            alerts.append({
                "type": "critical_risk",
                "priority": "critical",
                "title": f"Critical Risk Identified: {risk.title}",
                "description": risk.description[:200] + "..." if len(risk.description) > 200 else risk.description,
                "created_at": risk.created_at.isoformat(),
                "entity_id": risk.id,
                "entity_type": "risk"
            })
        
        # Overdue high-priority tasks
        overdue_critical_tasks = db.query(Task).filter(
            Task.priority.in_([TaskPriority.HIGH, TaskPriority.CRITICAL]),
            Task.due_date < datetime.utcnow(),
            Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
        ).limit(5).all()
        
        for task in overdue_critical_tasks:
            days_overdue = (datetime.utcnow() - task.due_date).days
            alerts.append({
                "type": "overdue_task",
                "priority": "high",
                "title": f"High-Priority Task Overdue: {task.title}",
                "description": f"Task has been overdue for {days_overdue} days",
                "created_at": task.due_date.isoformat(),
                "entity_id": task.id,
                "entity_type": "task"
            })
        
        # Failed assessments
        failed_assessments = db.query(Assessment).filter(
            Assessment.status == AssessmentStatus.FAILED,
            Assessment.updated_at >= start_date
        ).limit(3).all()
        
        for assessment in failed_assessments:
            alerts.append({
                "type": "failed_assessment",
                "priority": "high",
                "title": f"Assessment Failed: {assessment.name}",
                "description": "Assessment has failed and requires immediate attention",
                "created_at": assessment.updated_at.isoformat(),
                "entity_id": assessment.id,
                "entity_type": "assessment"
            })
        
        return sorted(alerts, key=lambda x: x["created_at"], reverse=True)
    
    async def _get_executive_recommendations(self, db: Session, risk_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate executive-level recommendations"""
        
        recommendations = []
        
        # Risk-based recommendations
        if risk_analytics["closure_metrics"]["closure_rate"] < 60:
            recommendations.append({
                "category": "risk_management",
                "priority": "high",
                "title": "Improve Risk Closure Efficiency",
                "description": "Current risk closure rate is below optimal levels. Consider implementing automated risk tracking and escalation procedures.",
                "estimated_effort": "medium",
                "expected_impact": "high"
            })
        
        if risk_analytics["closure_metrics"]["avg_resolution_days"] > 30:
            recommendations.append({
                "category": "process_improvement",
                "priority": "medium",
                "title": "Accelerate Risk Resolution",
                "description": f"Average risk resolution time of {risk_analytics['closure_metrics']['avg_resolution_days']:.1f} days exceeds best practice targets. Review resource allocation and risk treatment processes.",
                "estimated_effort": "high",
                "expected_impact": "high"
            })
        
        # Add strategic recommendations
        recommendations.append({
            "category": "strategic",
            "priority": "medium",
            "title": "Enhance Risk Monitoring",
            "description": "Implement continuous risk monitoring capabilities to improve detection and response times.",
            "estimated_effort": "high",
            "expected_impact": "very_high"
        })
        
        return recommendations
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to number of days"""
        
        if time_range.endswith('d'):
            return int(time_range[:-1])
        elif time_range.endswith('w'):
            return int(time_range[:-1]) * 7
        elif time_range.endswith('m'):
            return int(time_range[:-1]) * 30
        elif time_range.endswith('y'):
            return int(time_range[:-1]) * 365
        else:
            return 30  # Default to 30 days
    
    # Additional helper methods would be implemented here for the other dashboard types
    # This is a comprehensive foundation that can be extended with more specific analytics
    
    async def _get_user_metrics(self, db: Session, user_id: int, start_date: datetime) -> Dict[str, Any]:
        """Get user-specific metrics for operational dashboard"""
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # User task metrics
        my_total_tasks = db.query(func.count(Task.id)).filter(
            Task.assigned_to_id == user_id,
            Task.is_active == True
        ).scalar() or 0
        
        my_completed_tasks = db.query(func.count(Task.id)).filter(
            Task.assigned_to_id == user_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= start_date
        ).scalar() or 0
        
        my_overdue_tasks = db.query(func.count(Task.id)).filter(
            Task.assigned_to_id == user_id,
            Task.due_date < datetime.utcnow(),
            Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
        ).scalar() or 0
        
        # User owned assets
        my_assets = db.query(func.count(Asset.id)).filter(
            Asset.owner_id == user_id,
            Asset.is_active == True
        ).scalar() or 0
        
        return {
            "user_name": user.full_name or user.username,
            "tasks": {
                "total_assigned": my_total_tasks,
                "completed_this_period": my_completed_tasks,
                "overdue": my_overdue_tasks
            },
            "assets_owned": my_assets,
            "productivity_score": self._calculate_productivity_score(my_total_tasks, my_completed_tasks, my_overdue_tasks)
        }
    
    def _calculate_productivity_score(self, total_tasks: int, completed_tasks: int, overdue_tasks: int) -> float:
        """Calculate user productivity score"""
        
        if total_tasks == 0:
            return 100.0
        
        completion_rate = (completed_tasks / total_tasks) * 100
        overdue_penalty = (overdue_tasks / total_tasks) * 20
        
        score = max(0, completion_rate - overdue_penalty)
        return round(score, 1)
    
    async def _get_workload_analytics(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get workload analytics for user"""
        
        # Task distribution by priority
        task_priority_dist = db.query(
            Task.priority,
            func.count(Task.id).label('count')
        ).filter(
            Task.assigned_to_id == user_id,
            Task.is_active == True,
            Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
        ).group_by(Task.priority).all()
        
        # Upcoming deadlines (next 7 days)
        upcoming_deadlines = db.query(func.count(Task.id)).filter(
            Task.assigned_to_id == user_id,
            Task.due_date >= datetime.utcnow(),
            Task.due_date <= datetime.utcnow() + timedelta(days=7),
            Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
        ).scalar() or 0
        
        return {
            "priority_distribution": [
                {"priority": item.priority, "count": item.count}
                for item in task_priority_dist
            ],
            "upcoming_deadlines": upcoming_deadlines,
            "workload_status": "overloaded" if upcoming_deadlines > 10 else "busy" if upcoming_deadlines > 5 else "normal"
        }
    
    # Additional methods for other dashboard components would continue here...
    # This provides a solid foundation for the enhanced dashboard analytics service

# Global service instance
dashboard_analytics_service = DashboardAnalyticsService()