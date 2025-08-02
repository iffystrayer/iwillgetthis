"""Report generation service for PDF exports and custom reports"""

import io
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from jinja2 import Template

from config import settings
from integration_services import email_service

logger = logging.getLogger(__name__)

class ReportService:
    """Service for generating and managing reports"""
    
    def __init__(self):
        self.reports_dir = Path(settings.UPLOADS_DIR) / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Report templates
        self.templates = {
            "risk_register": self._create_risk_register_template(),
            "assessment_summary": self._create_assessment_summary_template(),
            "executive_summary": self._create_executive_summary_template(),
            "compliance_status": self._create_compliance_status_template()
        }
    
    def _create_risk_register_template(self) -> str:
        """Create risk register report template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Risk Register Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .summary { margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .risk-critical { background-color: #ffebee; }
        .risk-high { background-color: #fff3e0; }
        .risk-medium { background-color: #fffde7; }
        .risk-low { background-color: #e8f5e8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Risk Register Report</h1>
        <p>Generated on {{ report_date }}</p>
        <p>Organization: {{ organization }}</p>
    </div>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>Total Risks: {{ total_risks }}</p>
        <p>Critical Risks: {{ critical_risks }}</p>
        <p>High Risks: {{ high_risks }}</p>
        <p>Medium Risks: {{ medium_risks }}</p>
        <p>Low Risks: {{ low_risks }}</p>
    </div>
    
    <h2>Risk Details</h2>
    <table>
        <thead>
            <tr>
                <th>Risk ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Level</th>
                <th>Score</th>
                <th>Status</th>
                <th>Owner</th>
                <th>Due Date</th>
            </tr>
        </thead>
        <tbody>
            {% for risk in risks %}
            <tr class="risk-{{ risk.level.lower() }}">
                <td>{{ risk.id }}</td>
                <td>{{ risk.title }}</td>
                <td>{{ risk.category }}</td>
                <td>{{ risk.level }}</td>
                <td>{{ risk.score }}</td>
                <td>{{ risk.status }}</td>
                <td>{{ risk.owner }}</td>
                <td>{{ risk.due_date }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
        """
    
    def _create_assessment_summary_template(self) -> str:
        """Create assessment summary report template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Assessment Summary Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .control-implemented { background-color: #e8f5e8; }
        .control-partial { background-color: #fffde7; }
        .control-not-implemented { background-color: #ffebee; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Assessment Summary Report</h1>
        <p>Assessment: {{ assessment_name }}</p>
        <p>Framework: {{ framework_name }}</p>
        <p>Completed on: {{ completion_date }}</p>
    </div>
    
    <div class="section">
        <h2>Assessment Overview</h2>
        <p>Total Controls: {{ total_controls }}</p>
        <p>Implemented: {{ implemented_controls }} ({{ implementation_percentage }}%)</p>
        <p>Partially Implemented: {{ partial_controls }}</p>
        <p>Not Implemented: {{ not_implemented_controls }}</p>
        <p>Overall Maturity Score: {{ maturity_score }}%</p>
    </div>
    
    <div class="section">
        <h2>Control Implementation Status</h2>
        <table>
            <thead>
                <tr>
                    <th>Control ID</th>
                    <th>Control Name</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Evidence</th>
                    <th>Comments</th>
                </tr>
            </thead>
            <tbody>
                {% for control in controls %}
                <tr class="control-{{ control.status.lower().replace(' ', '-') }}">
                    <td>{{ control.control_id }}</td>
                    <td>{{ control.name }}</td>
                    <td>{{ control.category }}</td>
                    <td>{{ control.status }}</td>
                    <td>{{ control.evidence_count }} files</td>
                    <td>{{ control.comments or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
        """
    
    def _create_executive_summary_template(self) -> str:
        """Create executive summary report template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Executive Security Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .metric-box { display: inline-block; margin: 10px; padding: 20px; border: 1px solid #ddd; text-align: center; }
        .critical { color: #d32f2f; }
        .high { color: #f57c00; }
        .medium { color: #fbc02d; }
        .low { color: #388e3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Executive Security Summary</h1>
        <p>Reporting Period: {{ reporting_period }}</p>
        <p>Generated on: {{ report_date }}</p>
    </div>
    
    <h2>Key Security Metrics</h2>
    <div class="metric-box">
        <h3>Overall Risk Level</h3>
        <p class="{{ overall_risk_class }}">{{ overall_risk_level }}</p>
    </div>
    
    <div class="metric-box">
        <h3>Active Risks</h3>
        <p>{{ total_active_risks }}</p>
    </div>
    
    <div class="metric-box">
        <h3>Compliance Score</h3>
        <p>{{ compliance_percentage }}%</p>
    </div>
    
    <div class="metric-box">
        <h3>Open Tasks</h3>
        <p>{{ open_tasks }}</p>
    </div>
    
    <h2>Executive Summary</h2>
    <div>{{ executive_narrative }}</div>
    
    <h2>Top Risks Requiring Executive Attention</h2>
    <ol>
        {% for risk in top_risks %}
        <li><strong>{{ risk.title }}</strong> - {{ risk.description }}</li>
        {% endfor %}
    </ol>
    
    <h2>Recommended Actions</h2>
    <ul>
        {% for action in recommended_actions %}
        <li>{{ action }}</li>
        {% endfor %}
    </ul>
</body>
</html>
        """
    
    def _create_compliance_status_template(self) -> str:
        """Create compliance status report template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Status Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .framework-section { margin-bottom: 40px; }
        .progress-bar { width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background-color: #4caf50; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Compliance Status Report</h1>
        <p>As of: {{ report_date }}</p>
    </div>
    
    {% for framework in frameworks %}
    <div class="framework-section">
        <h2>{{ framework.name }}</h2>
        <p>Overall Compliance: {{ framework.compliance_percentage }}%</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ framework.compliance_percentage }}%;"></div>
        </div>
        
        <h3>Category Breakdown</h3>
        <ul>
            {% for category in framework.categories %}
            <li>{{ category.name }}: {{ category.compliance_percentage }}% ({{ category.implemented }}/{{ category.total }} controls)</li>
            {% endfor %}
        </ul>
        
        <h3>Areas for Improvement</h3>
        <ul>
            {% for gap in framework.gaps %}
            <li>{{ gap }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}
</body>
</html>
        """
    
    async def generate_risk_register_report(self, risks_data: List[Dict[str, Any]], 
                                          organization: str = "Organization") -> str:
        """Generate risk register PDF report"""
        try:
            # Prepare data for template
            template_data = {
                "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "organization": organization,
                "total_risks": len(risks_data),
                "critical_risks": len([r for r in risks_data if r.get("level", "").lower() == "critical"]),
                "high_risks": len([r for r in risks_data if r.get("level", "").lower() == "high"]),
                "medium_risks": len([r for r in risks_data if r.get("level", "").lower() == "medium"]),
                "low_risks": len([r for r in risks_data if r.get("level", "").lower() == "low"]),
                "risks": risks_data
            }
            
            # Generate HTML from template
            template = Template(self.templates["risk_register"])
            html_content = template.render(**template_data)
            
            # Generate PDF
            pdf_filename = f"risk_register_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = self.reports_dir / pdf_filename
            
            # For now, save as HTML (PDF generation would require additional setup)
            html_path = pdf_path.with_suffix('.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Risk register report generated: {html_path}")
            return str(html_path)
            
        except Exception as e:
            logger.error(f"Failed to generate risk register report: {e}")
            raise e
    
    async def generate_assessment_summary_report(self, assessment_data: Dict[str, Any]) -> str:
        """Generate assessment summary PDF report"""
        try:
            template_data = {
                "assessment_name": assessment_data.get("name", "Assessment"),
                "framework_name": assessment_data.get("framework", "Framework"),
                "completion_date": datetime.now().strftime("%Y-%m-%d"),
                "total_controls": assessment_data.get("total_controls", 0),
                "implemented_controls": assessment_data.get("implemented_controls", 0),
                "partial_controls": assessment_data.get("partial_controls", 0),
                "not_implemented_controls": assessment_data.get("not_implemented_controls", 0),
                "implementation_percentage": assessment_data.get("implementation_percentage", 0),
                "maturity_score": assessment_data.get("maturity_score", 0),
                "controls": assessment_data.get("controls", [])
            }
            
            template = Template(self.templates["assessment_summary"])
            html_content = template.render(**template_data)
            
            pdf_filename = f"assessment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            html_path = self.reports_dir / pdf_filename.replace('.pdf', '.html')
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Assessment summary report generated: {html_path}")
            return str(html_path)
            
        except Exception as e:
            logger.error(f"Failed to generate assessment summary report: {e}")
            raise e
    
    async def generate_executive_summary_report(self, dashboard_data: Dict[str, Any], 
                                              ai_narrative: str = None) -> str:
        """Generate executive summary PDF report"""
        try:
            template_data = {
                "reporting_period": "Last 30 days",
                "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "overall_risk_level": dashboard_data.get("overall_risk_level", "Medium"),
                "overall_risk_class": dashboard_data.get("overall_risk_level", "medium").lower(),
                "total_active_risks": dashboard_data.get("risks", {}).get("total", 0),
                "compliance_percentage": dashboard_data.get("compliance_percentage", 75),
                "open_tasks": dashboard_data.get("tasks", {}).get("open", 0),
                "executive_narrative": ai_narrative or "Executive summary content would be generated here using AI analysis of current security metrics and trends.",
                "top_risks": dashboard_data.get("top_risks", []),
                "recommended_actions": dashboard_data.get("recommended_actions", [
                    "Continue monitoring critical infrastructure",
                    "Complete pending security assessments",
                    "Review and update incident response procedures"
                ])
            }
            
            template = Template(self.templates["executive_summary"])
            html_content = template.render(**template_data)
            
            pdf_filename = f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            html_path = self.reports_dir / pdf_filename.replace('.pdf', '.html')
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Executive summary report generated: {html_path}")
            return str(html_path)
            
        except Exception as e:
            logger.error(f"Failed to generate executive summary report: {e}")
            raise e
    
    async def schedule_report(self, report_type: str, schedule: str, 
                            recipients: List[str], report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a report for automatic generation and distribution"""
        try:
            # This would integrate with a task scheduler like Celery or APScheduler
            # For now, return a mock response
            
            schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "schedule_id": schedule_id,
                "report_type": report_type,
                "schedule": schedule,
                "recipients": recipients,
                "status": "scheduled",
                "next_run": datetime.now() + timedelta(days=1),
                "created_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule report: {e}")
            raise e
    
    async def email_report(self, report_path: str, recipients: List[str], 
                         subject: str = None) -> Dict[str, Any]:
        """Email a generated report to recipients"""
        try:
            if not email_service.is_enabled():
                return {"status": "disabled", "message": "Email service not configured"}
            
            default_subject = f"Aegis Security Report - {datetime.now().strftime('%Y-%m-%d')}"
            email_subject = subject or default_subject
            
            body = f"""
            Please find attached the requested security report.
            
            Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            For any questions, please contact the security team.
            
            Best regards,
            Aegis Risk Management Platform
            """
            
            # Send email to each recipient
            results = []
            for recipient in recipients:
                result = await email_service.send_notification(
                    to_email=recipient,
                    subject=email_subject,
                    body=body
                )
                results.append(result)
            
            return {
                "status": "sent",
                "recipients": len(recipients),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to email report: {e}")
            return {"status": "error", "message": str(e)}

# Global report service instance
report_service = ReportService()