"""Email notification service for risk management platform"""

import asyncio
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, Template

from config import settings
from models.user import User
from models.risk import Risk
from models.assessment import Assessment
from models.audit import AuditLog

logger = logging.getLogger(__name__)

class EmailTemplateService:
    """Service for managing email templates"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "email_templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default email templates"""
        
        # Risk deadline notification template
        risk_deadline_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Risk Deadline Notification</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #6366f1; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .risk-details { background: #f8f9fa; padding: 15px; border-left: 4px solid #6366f1; margin: 15px 0; }
        .urgent { border-left-color: #ef4444; }
        .warning { border-left-color: #f59e0b; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }
        .btn { display: inline-block; padding: 10px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Risk Deadline Notification</h1>
        <p>Aegis Risk Management Platform</p>
    </div>
    
    <div class="content">
        <p>Hello {{ recipient_name }},</p>
        
        <p>This is a reminder that the following risk requires your attention:</p>
        
        <div class="risk-details {{ urgency_class }}">
            <h3>{{ risk_title }}</h3>
            <p><strong>Risk ID:</strong> {{ risk_id }}</p>
            <p><strong>Risk Level:</strong> {{ risk_level }}</p>
            <p><strong>Due Date:</strong> {{ due_date }}</p>
            <p><strong>Days Remaining:</strong> {{ days_remaining }}</p>
            <p><strong>Owner:</strong> {{ risk_owner }}</p>
            {% if mitigation_strategy %}
            <p><strong>Mitigation Strategy:</strong> {{ mitigation_strategy }}</p>
            {% endif %}
        </div>
        
        <p>Please review this risk and take appropriate action before the deadline.</p>
        
        <p>
            <a href="{{ platform_url }}/risks/{{ risk_id }}" class="btn">View Risk Details</a>
        </p>
        
        <p>Best regards,<br>Aegis Risk Management Team</p>
    </div>
    
    <div class="footer">
        <p>This is an automated notification from the Aegis Risk Management Platform</p>
        <p>Generated on {{ generated_date }}</p>
    </div>
</body>
</html>
        """
        
        # Risk status change template
        risk_status_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Risk Status Update</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #6366f1; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .status-change { background: #f8f9fa; padding: 15px; border-left: 4px solid #10b981; margin: 15px 0; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }
        .btn { display: inline-block; padding: 10px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📝 Risk Status Update</h1>
        <p>Aegis Risk Management Platform</p>
    </div>
    
    <div class="content">
        <p>Hello {{ recipient_name }},</p>
        
        <p>A risk status has been updated:</p>
        
        <div class="status-change">
            <h3>{{ risk_title }}</h3>
            <p><strong>Risk ID:</strong> {{ risk_id }}</p>
            <p><strong>Previous Status:</strong> {{ old_status }}</p>
            <p><strong>New Status:</strong> {{ new_status }}</p>
            <p><strong>Updated By:</strong> {{ updated_by }}</p>
            <p><strong>Update Date:</strong> {{ update_date }}</p>
            {% if comments %}
            <p><strong>Comments:</strong> {{ comments }}</p>
            {% endif %}
        </div>
        
        <p>
            <a href="{{ platform_url }}/risks/{{ risk_id }}" class="btn">View Risk Details</a>
        </p>
        
        <p>Best regards,<br>Aegis Risk Management Team</p>
    </div>
    
    <div class="footer">
        <p>This is an automated notification from the Aegis Risk Management Platform</p>
        <p>Generated on {{ generated_date }}</p>
    </div>
</body>
</html>
        """
        
        # Weekly risk digest template
        weekly_digest_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Weekly Risk Digest</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #6366f1; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .summary-box { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .metric { display: inline-block; margin: 10px 15px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #6366f1; }
        .risk-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .critical { color: #ef4444; }
        .high { color: #f59e0b; }
        .medium { color: #8b5cf6; }
        .low { color: #10b981; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }
        .btn { display: inline-block; padding: 10px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Weekly Risk Digest</h1>
        <p>Aegis Risk Management Platform</p>
        <p>{{ week_start }} - {{ week_end }}</p>
    </div>
    
    <div class="content">
        <p>Hello {{ recipient_name }},</p>
        
        <p>Here's your weekly risk management summary:</p>
        
        <div class="summary-box">
            <h3>Risk Summary</h3>
            <div class="metric">
                <div class="metric-value">{{ total_risks }}</div>
                <div>Total Risks</div>
            </div>
            <div class="metric">
                <div class="metric-value critical">{{ critical_risks }}</div>
                <div>Critical</div>
            </div>
            <div class="metric">
                <div class="metric-value high">{{ high_risks }}</div>
                <div>High</div>
            </div>
            <div class="metric">
                <div class="metric-value">{{ new_risks }}</div>
                <div>New This Week</div>
            </div>
            <div class="metric">
                <div class="metric-value">{{ resolved_risks }}</div>
                <div>Resolved</div>
            </div>
        </div>
        
        {% if upcoming_deadlines %}
        <h3>⏰ Upcoming Deadlines</h3>
        {% for risk in upcoming_deadlines %}
        <div class="risk-item">
            <strong class="{{ risk.level|lower }}">{{ risk.title }}</strong>
            <span style="float: right;">Due: {{ risk.due_date }}</span>
            <br><small>Owner: {{ risk.owner }}</small>
        </div>
        {% endfor %}
        {% endif %}
        
        {% if new_risks_list %}
        <h3>🆕 New Risks This Week</h3>
        {% for risk in new_risks_list %}
        <div class="risk-item">
            <strong class="{{ risk.level|lower }}">{{ risk.title }}</strong>
            <span style="float: right;">{{ risk.level }}</span>
            <br><small>Created: {{ risk.created_date }} | Owner: {{ risk.owner }}</small>
        </div>
        {% endfor %}
        {% endif %}
        
        <p>
            <a href="{{ platform_url }}/dashboard" class="btn">View Full Dashboard</a>
        </p>
        
        <p>Best regards,<br>Aegis Risk Management Team</p>
    </div>
    
    <div class="footer">
        <p>This is an automated weekly digest from the Aegis Risk Management Platform</p>
        <p>Generated on {{ generated_date }}</p>
    </div>
</body>
</html>
        """
        
        # Save templates to files
        templates = {
            "risk_deadline_notification.html": risk_deadline_template,
            "risk_status_update.html": risk_status_template,
            "weekly_risk_digest.html": weekly_digest_template
        }
        
        for template_name, content in templates.items():
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                template_path.write_text(content.strip())
                logger.info(f"Created email template: {template_name}")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise e

class EmailNotificationService:
    """Email notification service for risk management events"""
    
    def __init__(self):
        self.template_service = EmailTemplateService()
        
        # Email configuration from settings
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@aegis-platform.com')
        self.platform_url = getattr(settings, 'PLATFORM_URL', 'http://localhost:3000')
        
        # Notification preferences
        self.enabled = getattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED', True)
        
    async def send_email(self, 
                        to_emails: Union[str, List[str]], 
                        subject: str, 
                        html_content: str,
                        text_content: str = None,
                        attachments: List[str] = None) -> bool:
        """Send email notification"""
        
        if not self.enabled:
            logger.info("Email notifications are disabled")
            return False
            
        try:
            # Prepare email
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['Subject'] = subject
            
            # Handle single email or list
            if isinstance(to_emails, str):
                to_emails = [to_emails]
            
            msg['To'] = ', '.join(to_emails)
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment_path in attachments:
                    if Path(attachment_path).exists():
                        with open(attachment_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {Path(attachment_path).name}'
                            )
                            msg.attach(part)
            
            # Send email using aiosmtplib for async operation
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls
            )
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_emails}: {e}")
            return False
    
    async def send_risk_deadline_notification(self, 
                                            risk: Risk, 
                                            recipients: List[User],
                                            days_until_deadline: int) -> bool:
        """Send risk deadline notification"""
        
        try:
            # Determine urgency
            if days_until_deadline <= 1:
                urgency_class = "urgent"
                subject_prefix = "🚨 URGENT"
            elif days_until_deadline <= 3:
                urgency_class = "warning"
                subject_prefix = "⚠️ WARNING"
            else:
                urgency_class = ""
                subject_prefix = "📅 REMINDER"
            
            subject = f"{subject_prefix}: Risk '{risk.title}' due in {days_until_deadline} days"
            
            # Prepare context for template
            context = {
                'risk_id': risk.id,
                'risk_title': risk.title,
                'risk_level': risk.level,
                'risk_owner': risk.owner,
                'due_date': risk.due_date.strftime('%Y-%m-%d') if risk.due_date else 'Not set',
                'days_remaining': days_until_deadline,
                'mitigation_strategy': risk.mitigation_strategy,
                'urgency_class': urgency_class,
                'platform_url': self.platform_url,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Send to each recipient
            success_count = 0
            for recipient in recipients:
                context['recipient_name'] = recipient.full_name or recipient.username
                
                html_content = self.template_service.render_template(
                    'risk_deadline_notification.html', 
                    context
                )
                
                success = await self.send_email(
                    recipient.email,
                    subject,
                    html_content
                )
                
                if success:
                    success_count += 1
            
            logger.info(f"Risk deadline notification sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send risk deadline notification: {e}")
            return False
    
    async def send_risk_status_update(self, 
                                    risk: Risk, 
                                    old_status: str,
                                    new_status: str,
                                    updated_by_user: User,
                                    recipients: List[User],
                                    comments: str = None) -> bool:
        """Send risk status change notification"""
        
        try:
            subject = f"📝 Risk Status Updated: '{risk.title}' - {old_status} → {new_status}"
            
            # Prepare context for template
            context = {
                'risk_id': risk.id,
                'risk_title': risk.title,
                'old_status': old_status,
                'new_status': new_status,
                'updated_by': updated_by_user.full_name or updated_by_user.username,
                'update_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'comments': comments,
                'platform_url': self.platform_url,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Send to each recipient
            success_count = 0
            for recipient in recipients:
                context['recipient_name'] = recipient.full_name or recipient.username
                
                html_content = self.template_service.render_template(
                    'risk_status_update.html', 
                    context
                )
                
                success = await self.send_email(
                    recipient.email,
                    subject,
                    html_content
                )
                
                if success:
                    success_count += 1
            
            logger.info(f"Risk status update notification sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send risk status update notification: {e}")
            return False
    
    async def send_weekly_risk_digest(self, 
                                    recipient: User,
                                    digest_data: Dict[str, Any]) -> bool:
        """Send weekly risk digest to user"""
        
        try:
            week_start = digest_data.get('week_start', '')
            week_end = digest_data.get('week_end', '')
            
            subject = f"📊 Weekly Risk Digest - {week_start} to {week_end}"
            
            # Prepare context for template
            context = {
                'recipient_name': recipient.full_name or recipient.username,
                'week_start': week_start,
                'week_end': week_end,
                'total_risks': digest_data.get('total_risks', 0),
                'critical_risks': digest_data.get('critical_risks', 0),
                'high_risks': digest_data.get('high_risks', 0),
                'new_risks': digest_data.get('new_risks', 0),
                'resolved_risks': digest_data.get('resolved_risks', 0),
                'upcoming_deadlines': digest_data.get('upcoming_deadlines', []),
                'new_risks_list': digest_data.get('new_risks_list', []),
                'platform_url': self.platform_url,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            html_content = self.template_service.render_template(
                'weekly_risk_digest.html', 
                context
            )
            
            success = await self.send_email(
                recipient.email,
                subject,
                html_content
            )
            
            if success:
                logger.info(f"Weekly digest sent to {recipient.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send weekly digest to {recipient.email}: {e}")
            return False
    
    async def send_assessment_reminder(self, 
                                     assessment: Assessment,
                                     recipients: List[User]) -> bool:
        """Send assessment deadline reminder"""
        
        try:
            subject = f"📋 Assessment Reminder: '{assessment.name}'"
            
            # Simple HTML content for assessment reminder
            html_content = f"""
            <html>
            <body>
                <h2>Assessment Reminder</h2>
                <p>Hello,</p>
                <p>This is a reminder that the following assessment requires attention:</p>
                <ul>
                    <li><strong>Assessment:</strong> {assessment.name}</li>
                    <li><strong>Status:</strong> {assessment.status}</li>
                    <li><strong>Due Date:</strong> {assessment.due_date if assessment.due_date else 'Not set'}</li>
                </ul>
                <p>Please complete this assessment at your earliest convenience.</p>
                <p><a href="{self.platform_url}/assessments/{assessment.id}">View Assessment</a></p>
                <p>Best regards,<br>Aegis Risk Management Team</p>
            </body>
            </html>
            """
            
            # Send to each recipient
            success_count = 0
            for recipient in recipients:
                success = await self.send_email(
                    recipient.email,
                    subject,
                    html_content
                )
                
                if success:
                    success_count += 1
            
            logger.info(f"Assessment reminder sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send assessment reminder: {e}")
            return False

# Global service instance
email_service = EmailNotificationService()