"""Database models for notification system"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)  # 'risk_deadlines', 'status_updates', 'weekly_digest', etc.
    is_enabled = Column(Boolean, default=True, nullable=False)
    delivery_method = Column(String(20), default='email', nullable=False)  # 'email', 'sms', 'in_app'
    frequency = Column(String(20), default='immediate')  # 'immediate', 'daily', 'weekly'
    filters = Column(JSON, nullable=True)  # JSON filters like risk categories, levels, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

class NotificationLog(Base):
    """Log of all sent notifications"""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # 'risk', 'assessment', 'user', etc.
    entity_id = Column(Integer, nullable=True)  # ID of the related entity
    notification_type = Column(String(50), nullable=False)  # Type of notification sent
    recipients = Column(Text, nullable=False)  # Comma-separated list of recipient emails
    subject = Column(String(255), nullable=True)  # Email subject
    content_summary = Column(Text, nullable=True)  # Brief summary of notification content
    status = Column(String(20), default='sent', nullable=False)  # 'sent', 'failed', 'pending'
    error_message = Column(Text, nullable=True)  # Error details if failed
    sent_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional metadata
    delivery_method = Column(String(20), default='email', nullable=False)
    template_used = Column(String(100), nullable=True)  # Template name used
    context_data = Column(JSON, nullable=True)  # JSON context data used in template

class NotificationTemplate(Base):
    """Email/notification templates"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # Template identifier
    display_name = Column(String(255), nullable=False)  # Human readable name
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)  # 'email', 'sms', 'in_app'
    subject_template = Column(String(255), nullable=True)  # Email subject template
    html_content = Column(Text, nullable=True)  # HTML email content
    text_content = Column(Text, nullable=True)  # Plain text content
    variables = Column(JSON, nullable=True)  # Expected template variables
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System templates cannot be deleted
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

class NotificationQueue(Base):
    """Queue for scheduled/delayed notifications"""
    __tablename__ = "notification_queue"

    id = Column(Integer, primary_key=True, index=True)
    notification_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    recipients = Column(Text, nullable=False)  # JSON array of recipient info
    template_name = Column(String(100), nullable=False)
    context_data = Column(JSON, nullable=False)  # Template context
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher number = higher priority
    status = Column(String(20), default='pending', nullable=False)  # 'pending', 'processing', 'sent', 'failed'
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    last_attempt = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

class NotificationSubscription(Base):
    """User subscriptions to specific entities or topics"""
    __tablename__ = "notification_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'risk', 'assessment', 'framework', etc.
    entity_id = Column(Integer, nullable=True)  # Specific entity ID, null for category subscription
    category = Column(String(100), nullable=True)  # Category name for broader subscriptions
    subscription_type = Column(String(50), nullable=False)  # 'updates', 'deadlines', 'all'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notification_subscriptions")

class NotificationChannel(Base):
    """Different notification channels (email, SMS, webhooks, etc.)"""
    __tablename__ = "notification_channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    channel_type = Column(String(50), nullable=False)  # 'email', 'sms', 'webhook', 'slack'
    configuration = Column(JSON, nullable=False)  # Channel-specific config (SMTP settings, API keys, etc.)
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships  
    creator = relationship("User", foreign_keys=[created_by])