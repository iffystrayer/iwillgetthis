"""API endpoints for notification management"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.notification import (
    NotificationPreference, NotificationLog, NotificationTemplate,
    NotificationQueue, NotificationSubscription, NotificationChannel
)
from models.audit import AuditLog
from schemas.notification import (
    NotificationPreferenceResponse, NotificationPreferenceCreate, NotificationPreferenceUpdate,
    NotificationLogResponse, NotificationTemplateResponse, NotificationTemplateCreate,
    NotificationSubscriptionResponse, NotificationSubscriptionCreate
)
from auth import get_current_active_user
from services.notification_scheduler import notification_scheduler
from services.email_service import email_service

router = APIRouter()

# Notification Preferences
@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
async def get_user_notification_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's notification preferences"""
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).all()
    
    return preferences

@router.post("/preferences", response_model=NotificationPreferenceResponse)
async def create_notification_preference(
    preference: NotificationPreferenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create or update notification preference"""
    # Check if preference already exists for this type
    existing = db.query(NotificationPreference).filter(
        and_(
            NotificationPreference.user_id == current_user.id,
            NotificationPreference.notification_type == preference.notification_type
        )
    ).first()
    
    if existing:
        # Update existing preference
        for field, value in preference.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new preference
        preference_data = preference.model_dump()
        preference_data["user_id"] = current_user.id
        
        db_preference = NotificationPreference(**preference_data)
        db.add(db_preference)
        db.commit()
        db.refresh(db_preference)
        
        return db_preference

@router.put("/preferences/{preference_id}", response_model=NotificationPreferenceResponse)
async def update_notification_preference(
    preference_id: int,
    preference_update: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update notification preference"""
    preference = db.query(NotificationPreference).filter(
        and_(
            NotificationPreference.id == preference_id,
            NotificationPreference.user_id == current_user.id
        )
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification preference not found"
        )
    
    # Update preference fields
    update_data = preference_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preference, field, value)
    
    db.commit()
    db.refresh(preference)
    
    return preference

@router.delete("/preferences/{preference_id}")
async def delete_notification_preference(
    preference_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete notification preference"""
    preference = db.query(NotificationPreference).filter(
        and_(
            NotificationPreference.id == preference_id,
            NotificationPreference.user_id == current_user.id
        )
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification preference not found"
        )
    
    db.delete(preference)
    db.commit()
    
    return {"message": "Notification preference deleted successfully"}

# Notification Subscriptions
@router.get("/subscriptions", response_model=List[NotificationSubscriptionResponse])
async def get_user_subscriptions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's notification subscriptions"""
    subscriptions = db.query(NotificationSubscription).filter(
        NotificationSubscription.user_id == current_user.id
    ).all()
    
    return subscriptions

@router.post("/subscriptions", response_model=NotificationSubscriptionResponse)
async def create_notification_subscription(
    subscription: NotificationSubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Subscribe to entity notifications"""
    # Check if subscription already exists
    existing = db.query(NotificationSubscription).filter(
        and_(
            NotificationSubscription.user_id == current_user.id,
            NotificationSubscription.entity_type == subscription.entity_type,
            NotificationSubscription.entity_id == subscription.entity_id,
            NotificationSubscription.subscription_type == subscription.subscription_type
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription already exists"
        )
    
    subscription_data = subscription.model_dump()
    subscription_data["user_id"] = current_user.id
    
    db_subscription = NotificationSubscription(**subscription_data)
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription

@router.delete("/subscriptions/{subscription_id}")
async def delete_notification_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe from entity notifications"""
    subscription = db.query(NotificationSubscription).filter(
        and_(
            NotificationSubscription.id == subscription_id,
            NotificationSubscription.user_id == current_user.id
        )
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification subscription not found"
        )
    
    db.delete(subscription)
    db.commit()
    
    return {"message": "Notification subscription deleted successfully"}

# Notification Logs (for admins and users to see their notification history)
@router.get("/logs", response_model=List[NotificationLogResponse])
async def get_notification_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    notification_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification logs (admin can see all, users see only their own)"""
    
    query = db.query(NotificationLog)
    
    # Non-admin users can only see notifications sent to them
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        query = query.filter(NotificationLog.recipients.contains(current_user.email))
    
    # Apply filters
    if notification_type:
        query = query.filter(NotificationLog.notification_type == notification_type)
    
    if entity_type:
        query = query.filter(NotificationLog.entity_type == entity_type)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(NotificationLog.sent_date >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(NotificationLog.sent_date <= end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )
    
    logs = query.order_by(desc(NotificationLog.sent_date)).offset(skip).limit(limit).all()
    return logs

# Test notification endpoint
@router.post("/test")
async def send_test_notification(
    recipient_email: Optional[str] = None,
    notification_type: str = "test",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a test notification"""
    
    # Use current user's email if not specified
    test_email = recipient_email or current_user.email
    
    try:
        # Send test email
        subject = "🧪 Test Notification from Aegis Platform"
        html_content = """
        <html>
        <body>
            <h2>Test Notification</h2>
            <p>Hello,</p>
            <p>This is a test notification from the Aegis Risk Management Platform.</p>
            <p>If you received this email, your notification system is working correctly!</p>
            <ul>
                <li><strong>Sent to:</strong> {email}</li>
                <li><strong>Sent by:</strong> {user}</li>
                <li><strong>Timestamp:</strong> {timestamp}</li>
            </ul>
            <p>Best regards,<br>Aegis Platform Team</p>
        </body>
        </html>
        """.format(
            email=test_email,
            user=current_user.full_name or current_user.username,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        success = await email_service.send_email(
            test_email,
            subject,
            html_content
        )
        
        if success:
            # Log the test notification
            notification_log = NotificationLog(
                entity_type='user',
                entity_id=current_user.id,
                notification_type='test',
                recipients=test_email,
                subject=subject,
                content_summary='Test notification',
                status='sent',
                delivery_method='email'
            )
            db.add(notification_log)
            db.commit()
            
            return {"message": f"Test notification sent successfully to {test_email}"}
        else:
            return {"message": f"Failed to send test notification to {test_email}"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )

# Admin endpoints for managing notification system
@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def get_notification_templates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification templates (admin only)"""
    
    # Check if user is admin
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    templates = db.query(NotificationTemplate).filter(
        NotificationTemplate.is_active == True
    ).all()
    
    return templates

@router.post("/templates", response_model=NotificationTemplateResponse)
async def create_notification_template(
    template: NotificationTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create notification template (admin only)"""
    
    # Check if user is admin
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    template_data = template.model_dump()
    template_data["created_by"] = current_user.id
    
    db_template = NotificationTemplate(**template_data)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template

# Notification statistics
@router.get("/stats")
async def get_notification_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Base query
    query = db.query(NotificationLog).filter(
        NotificationLog.sent_date >= start_date
    )
    
    # Non-admin users see only their stats
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        query = query.filter(NotificationLog.recipients.contains(current_user.email))
    
    # Total notifications
    total_sent = query.filter(NotificationLog.status == 'sent').count()
    total_failed = query.filter(NotificationLog.status == 'failed').count()
    
    # By notification type
    type_stats = {}
    for log in query.all():
        notification_type = log.notification_type
        if notification_type not in type_stats:
            type_stats[notification_type] = {'sent': 0, 'failed': 0}
        type_stats[notification_type][log.status] += 1
    
    # Recent activity (last 7 days)
    recent_query = query.filter(
        NotificationLog.sent_date >= end_date - timedelta(days=7)
    )
    recent_sent = recent_query.filter(NotificationLog.status == 'sent').count()
    
    return {
        "period_days": days,
        "total_sent": total_sent,
        "total_failed": total_failed,
        "success_rate": (total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0,
        "recent_activity": recent_sent,
        "by_type": type_stats
    }

# Manual notification triggers (admin only)
@router.post("/trigger/risk-deadline-check")
async def trigger_risk_deadline_check(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually trigger risk deadline check (admin only)"""
    
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Trigger deadline check in background
    background_tasks.add_task(notification_scheduler._check_risk_deadlines)
    
    # Log admin action
    audit_log = AuditLog(
        event_type="action",
        entity_type="notification",
        entity_id=None,
        user_id=current_user.id,
        action="Manual risk deadline check triggered",
        description="Admin manually triggered risk deadline notification check",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Risk deadline check triggered successfully"}

@router.post("/trigger/weekly-digest")
async def trigger_weekly_digest(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually trigger weekly digest (admin only)"""
    
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Trigger weekly digest in background
    background_tasks.add_task(notification_scheduler._send_weekly_digests)
    
    # Log admin action
    audit_log = AuditLog(
        event_type="action",
        entity_type="notification",
        entity_id=None,
        user_id=current_user.id,
        action="Manual weekly digest triggered",
        description="Admin manually triggered weekly digest notifications",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Weekly digest notifications triggered successfully"}