"""Notification scheduler service for automated email notifications"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from database import get_db
from models.user import User
from models.risk import Risk
from models.assessment import Assessment
from models.audit import AuditLog
from models.notification import NotificationPreference, NotificationLog
from services.email_service import email_service

logger = logging.getLogger(__name__)

class NotificationSchedulerService:
    """Service for scheduling and managing automated notifications"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        # Configure scheduler
        self.scheduler.configure(
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            }
        )
    
    async def start(self):
        """Start the notification scheduler"""
        if self.is_running:
            logger.warning("Notification scheduler is already running")
            return
        
        try:
            # Schedule regular notification checks
            await self._schedule_notification_jobs()
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info("Notification scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start notification scheduler: {e}")
            raise e
    
    async def stop(self):
        """Stop the notification scheduler"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Notification scheduler stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop notification scheduler: {e}")
    
    async def _schedule_notification_jobs(self):
        """Schedule all notification jobs"""
        
        # Risk deadline notifications - check every hour
        self.scheduler.add_job(
            self._check_risk_deadlines,
            trigger=IntervalTrigger(hours=1),
            id='risk_deadline_check',
            name='Check Risk Deadlines',
            replace_existing=True
        )
        
        # Assessment deadline notifications - check every 4 hours
        self.scheduler.add_job(
            self._check_assessment_deadlines,
            trigger=IntervalTrigger(hours=4),
            id='assessment_deadline_check',
            name='Check Assessment Deadlines',
            replace_existing=True
        )
        
        # Weekly digest notifications - send every Monday at 9 AM
        self.scheduler.add_job(
            self._send_weekly_digests,
            trigger=CronTrigger(day_of_week='monday', hour=9, minute=0),
            id='weekly_digest_job',
            name='Send Weekly Risk Digests',
            replace_existing=True
        )
        
        # Daily summary for admins - send every day at 8 AM
        self.scheduler.add_job(
            self._send_daily_summaries,
            trigger=CronTrigger(hour=8, minute=0),
            id='daily_summary_job',
            name='Send Daily Risk Summaries',
            replace_existing=True
        )
        
        # Cleanup old notification logs - run weekly on Sunday at midnight
        self.scheduler.add_job(
            self._cleanup_notification_logs,
            trigger=CronTrigger(day_of_week='sunday', hour=0, minute=0),
            id='cleanup_logs_job',
            name='Cleanup Notification Logs',
            replace_existing=True
        )
        
        logger.info("Notification jobs scheduled successfully")
    
    async def _check_risk_deadlines(self):
        """Check for risks approaching deadlines and send notifications"""
        try:
            db: Session = next(get_db())
            
            # Get risks with upcoming deadlines (1, 3, 7, and 14 days)
            notification_windows = [1, 3, 7, 14]
            current_date = datetime.now().date()
            
            for days_ahead in notification_windows:
                target_date = current_date + timedelta(days=days_ahead)
                
                # Find risks due on target date that are still open
                risks = db.query(Risk).filter(
                    and_(
                        Risk.due_date == target_date,
                        Risk.status.in_(['open', 'in_progress', 'identified'])
                    )
                ).all()
                
                for risk in risks:
                    # Check if we've already sent notification for this window
                    recent_notification = db.query(NotificationLog).filter(
                        and_(
                            NotificationLog.entity_type == 'risk',
                            NotificationLog.entity_id == risk.id,
                            NotificationLog.notification_type == f'deadline_{days_ahead}d',
                            NotificationLog.sent_date >= current_date
                        )
                    ).first()
                    
                    if recent_notification:
                        continue  # Already sent notification today
                    
                    # Get notification recipients
                    recipients = await self._get_risk_notification_recipients(risk, db)
                    
                    if recipients:
                        # Send deadline notification
                        success = await email_service.send_risk_deadline_notification(
                            risk, recipients, days_ahead
                        )
                        
                        if success:
                            # Log the notification
                            notification_log = NotificationLog(
                                entity_type='risk',
                                entity_id=risk.id,
                                notification_type=f'deadline_{days_ahead}d',
                                recipients=', '.join([r.email for r in recipients]),
                                sent_date=datetime.now(),
                                status='sent',
                                content_summary=f'Risk deadline notification for {risk.title}'
                            )
                            db.add(notification_log)
                            
                            # Create audit log
                            audit_log = AuditLog(
                                event_type="notification",
                                entity_type="risk",
                                entity_id=risk.id,
                                user_id=None,  # System generated
                                action="Deadline notification sent",
                                description=f"Deadline notification sent for risk '{risk.title}' ({days_ahead} days)",
                                source="notification_scheduler",
                                risk_level="low"
                            )
                            db.add(audit_log)
            
            db.commit()
            logger.info("Risk deadline notifications check completed")
            
        except Exception as e:
            logger.error(f"Error checking risk deadlines: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _check_assessment_deadlines(self):
        """Check for assessments approaching deadlines"""
        try:
            db: Session = next(get_db())
            
            # Get assessments due in the next 7 days
            current_date = datetime.now().date()
            target_date = current_date + timedelta(days=7)
            
            assessments = db.query(Assessment).filter(
                and_(
                    Assessment.due_date <= target_date,
                    Assessment.due_date >= current_date,
                    Assessment.status.in_(['in_progress', 'not_started'])
                )
            ).all()
            
            for assessment in assessments:
                # Check if notification already sent recently
                recent_notification = db.query(NotificationLog).filter(
                    and_(
                        NotificationLog.entity_type == 'assessment',
                        NotificationLog.entity_id == assessment.id,
                        NotificationLog.notification_type == 'deadline_reminder',
                        NotificationLog.sent_date >= current_date - timedelta(days=2)
                    )
                ).first()
                
                if recent_notification:
                    continue
                
                # Get assessment assignees
                recipients = await self._get_assessment_notification_recipients(assessment, db)
                
                if recipients:
                    success = await email_service.send_assessment_reminder(assessment, recipients)
                    
                    if success:
                        # Log the notification
                        notification_log = NotificationLog(
                            entity_type='assessment',
                            entity_id=assessment.id,
                            notification_type='deadline_reminder',
                            recipients=', '.join([r.email for r in recipients]),
                            sent_date=datetime.now(),
                            status='sent',
                            content_summary=f'Assessment deadline reminder for {assessment.name}'
                        )
                        db.add(notification_log)
            
            db.commit()
            logger.info("Assessment deadline notifications check completed")
            
        except Exception as e:
            logger.error(f"Error checking assessment deadlines: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _send_weekly_digests(self):
        """Send weekly risk digests to subscribed users"""
        try:
            db: Session = next(get_db())
            
            # Get users who have enabled weekly digest notifications
            users = db.query(User).filter(
                User.is_active == True
            ).all()
            
            # Calculate week range
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            for user in users:
                # Check user notification preferences
                preference = db.query(NotificationPreference).filter(
                    and_(
                        NotificationPreference.user_id == user.id,
                        NotificationPreference.notification_type == 'weekly_digest',
                        NotificationPreference.is_enabled == True
                    )
                ).first()
                
                if not preference:
                    continue  # User hasn't enabled weekly digest
                
                # Generate digest data
                digest_data = await self._generate_weekly_digest_data(user, week_start, week_end, db)
                
                # Send digest
                success = await email_service.send_weekly_risk_digest(user, digest_data)
                
                if success:
                    # Log the notification
                    notification_log = NotificationLog(
                        entity_type='user',
                        entity_id=user.id,
                        notification_type='weekly_digest',
                        recipients=user.email,
                        sent_date=datetime.now(),
                        status='sent',
                        content_summary=f'Weekly risk digest for {week_start} to {week_end}'
                    )
                    db.add(notification_log)
            
            db.commit()
            logger.info("Weekly digest notifications sent")
            
        except Exception as e:
            logger.error(f"Error sending weekly digests: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _send_daily_summaries(self):
        """Send daily risk summaries to administrators"""
        try:
            db: Session = next(get_db())
            
            # Get admin users
            admin_users = db.query(User).filter(
                and_(
                    User.is_active == True,
                    User.role == 'admin'
                )
            ).all()
            
            # Generate daily summary data
            summary_data = await self._generate_daily_summary_data(db)
            
            # Send to each admin
            for admin in admin_users:
                # Check if admin wants daily summaries
                preference = db.query(NotificationPreference).filter(
                    and_(
                        NotificationPreference.user_id == admin.id,
                        NotificationPreference.notification_type == 'daily_summary',
                        NotificationPreference.is_enabled == True
                    )
                ).first()
                
                if preference:
                    # Send summary (using simple HTML for now)
                    subject = f"📊 Daily Risk Summary - {datetime.now().strftime('%Y-%m-%d')}"
                    html_content = self._format_daily_summary_html(summary_data)
                    
                    success = await email_service.send_email(
                        admin.email,
                        subject,
                        html_content
                    )
                    
                    if success:
                        notification_log = NotificationLog(
                            entity_type='user',
                            entity_id=admin.id,
                            notification_type='daily_summary',
                            recipients=admin.email,
                            sent_date=datetime.now(),
                            status='sent',
                            content_summary='Daily risk summary'
                        )
                        db.add(notification_log)
            
            db.commit()
            logger.info("Daily summary notifications sent")
            
        except Exception as e:
            logger.error(f"Error sending daily summaries: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _cleanup_notification_logs(self):
        """Clean up old notification logs"""
        try:
            db: Session = next(get_db())
            
            # Delete notification logs older than 90 days
            cutoff_date = datetime.now() - timedelta(days=90)
            
            deleted_count = db.query(NotificationLog).filter(
                NotificationLog.sent_date < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"Cleaned up {deleted_count} old notification logs")
            
        except Exception as e:
            logger.error(f"Error cleaning up notification logs: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _get_risk_notification_recipients(self, risk: Risk, db: Session) -> List[User]:
        """Get list of users who should receive notifications for a risk"""
        recipients = []
        
        # Add risk owner
        if risk.owner:
            owner = db.query(User).filter(User.username == risk.owner).first()
            if owner and owner.is_active:
                recipients.append(owner)
        
        # Add users who have subscribed to risk notifications for this category
        category_subscribers = db.query(User).join(NotificationPreference).filter(
            and_(
                User.is_active == True,
                NotificationPreference.notification_type == 'risk_deadlines',
                NotificationPreference.is_enabled == True,
                or_(
                    NotificationPreference.filters == None,
                    NotificationPreference.filters.contains(risk.category)
                )
            )
        ).all()
        
        recipients.extend(category_subscribers)
        
        # Remove duplicates
        unique_recipients = list({user.id: user for user in recipients}.values())
        
        return unique_recipients
    
    async def _get_assessment_notification_recipients(self, assessment: Assessment, db: Session) -> List[User]:
        """Get list of users who should receive assessment notifications"""
        recipients = []
        
        # Add assessment assignee if specified
        if hasattr(assessment, 'assigned_to') and assessment.assigned_to:
            assignee = db.query(User).filter(User.id == assessment.assigned_to).first()
            if assignee and assignee.is_active:
                recipients.append(assignee)
        
        # Add framework owners or general subscribers
        framework_subscribers = db.query(User).join(NotificationPreference).filter(
            and_(
                User.is_active == True,
                NotificationPreference.notification_type == 'assessment_reminders',
                NotificationPreference.is_enabled == True
            )
        ).all()
        
        recipients.extend(framework_subscribers)
        
        # Remove duplicates
        unique_recipients = list({user.id: user for user in recipients}.values())
        
        return unique_recipients
    
    async def _generate_weekly_digest_data(self, user: User, week_start, week_end, db: Session) -> Dict[str, Any]:
        """Generate data for weekly risk digest"""
        
        # Get risks data for the week
        total_risks = db.query(Risk).count()
        critical_risks = db.query(Risk).filter(Risk.level == 'Critical').count()
        high_risks = db.query(Risk).filter(Risk.level == 'High').count()
        
        # New risks this week
        new_risks = db.query(Risk).filter(
            Risk.created_at >= week_start
        ).count()
        
        # Resolved risks this week
        resolved_risks = db.query(Risk).filter(
            and_(
                Risk.status == 'resolved',
                Risk.updated_at >= week_start
            )
        ).count()
        
        # Upcoming deadlines (next 7 days)
        upcoming_deadline_risks = db.query(Risk).filter(
            and_(
                Risk.due_date >= datetime.now().date(),
                Risk.due_date <= datetime.now().date() + timedelta(days=7),
                Risk.status.in_(['open', 'in_progress'])
            )
        ).limit(5).all()
        
        upcoming_deadlines = []
        for risk in upcoming_deadline_risks:
            upcoming_deadlines.append({
                'title': risk.title,
                'level': risk.level,
                'due_date': risk.due_date.strftime('%Y-%m-%d') if risk.due_date else '',
                'owner': risk.owner
            })
        
        # New risks list
        new_risks_list = []
        new_risks_query = db.query(Risk).filter(
            Risk.created_at >= week_start
        ).limit(5).all()
        
        for risk in new_risks_query:
            new_risks_list.append({
                'title': risk.title,
                'level': risk.level,
                'owner': risk.owner,
                'created_date': risk.created_at.strftime('%Y-%m-%d') if risk.created_at else ''
            })
        
        return {
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d'),
            'total_risks': total_risks,
            'critical_risks': critical_risks,
            'high_risks': high_risks,
            'new_risks': new_risks,
            'resolved_risks': resolved_risks,
            'upcoming_deadlines': upcoming_deadlines,
            'new_risks_list': new_risks_list
        }
    
    async def _generate_daily_summary_data(self, db: Session) -> Dict[str, Any]:
        """Generate daily summary data for administrators"""
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Risk metrics
        total_risks = db.query(Risk).count()
        new_risks_today = db.query(Risk).filter(Risk.created_at >= today).count()
        risks_due_today = db.query(Risk).filter(Risk.due_date == today).count()
        overdue_risks = db.query(Risk).filter(
            and_(
                Risk.due_date < today,
                Risk.status.in_(['open', 'in_progress'])
            )
        ).count()
        
        # Assessment metrics
        assessments_due_today = db.query(Assessment).filter(Assessment.due_date == today).count()
        
        return {
            'date': today.strftime('%Y-%m-%d'),
            'total_risks': total_risks,
            'new_risks_today': new_risks_today,
            'risks_due_today': risks_due_today,
            'overdue_risks': overdue_risks,
            'assessments_due_today': assessments_due_today
        }
    
    def _format_daily_summary_html(self, summary_data: Dict[str, Any]) -> str:
        """Format daily summary data as HTML"""
        
        return f"""
        <html>
        <body>
            <h2>📊 Daily Risk Summary - {summary_data['date']}</h2>
            
            <h3>Risk Metrics</h3>
            <ul>
                <li><strong>Total Active Risks:</strong> {summary_data['total_risks']}</li>
                <li><strong>New Risks Today:</strong> {summary_data['new_risks_today']}</li>
                <li><strong>Risks Due Today:</strong> {summary_data['risks_due_today']}</li>
                <li><strong>Overdue Risks:</strong> {summary_data['overdue_risks']}</li>
            </ul>
            
            <h3>Assessment Metrics</h3>
            <ul>
                <li><strong>Assessments Due Today:</strong> {summary_data['assessments_due_today']}</li>
            </ul>
            
            <p>Best regards,<br>Aegis Risk Management Platform</p>
        </body>
        </html>
        """
    
    async def trigger_risk_status_notification(self, 
                                             risk: Risk, 
                                             old_status: str, 
                                             new_status: str,
                                             updated_by: User,
                                             db: Session):
        """Manually trigger risk status change notification"""
        
        try:
            # Get notification recipients
            recipients = await self._get_risk_notification_recipients(risk, db)
            
            if recipients:
                success = await email_service.send_risk_status_update(
                    risk, old_status, new_status, updated_by, recipients
                )
                
                if success:
                    # Log the notification
                    notification_log = NotificationLog(
                        entity_type='risk',
                        entity_id=risk.id,
                        notification_type='status_update',
                        recipients=', '.join([r.email for r in recipients]),
                        sent_date=datetime.now(),
                        status='sent',
                        content_summary=f'Risk status changed from {old_status} to {new_status}'
                    )
                    db.add(notification_log)
                    db.commit()
                    
                    logger.info(f"Risk status notification sent for risk {risk.id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending risk status notification: {e}")
            return False

# Global service instance
notification_scheduler = NotificationSchedulerService()