"""Pydantic schemas for notification models"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class NotificationTypeEnum(str, Enum):
    """Notification types"""
    RISK_DEADLINES = "risk_deadlines"
    RISK_STATUS_UPDATES = "risk_status_updates"
    ASSESSMENT_REMINDERS = "assessment_reminders"
    WEEKLY_DIGEST = "weekly_digest"
    DAILY_SUMMARY = "daily_summary"
    COMPLIANCE_ALERTS = "compliance_alerts"
    FRAMEWORK_UPDATES = "framework_updates"
    EVIDENCE_EXPIRY = "evidence_expiry"
    TASK_ASSIGNMENTS = "task_assignments"
    SYSTEM_MAINTENANCE = "system_maintenance"

class DeliveryMethodEnum(str, Enum):
    """Delivery methods"""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"

class FrequencyEnum(str, Enum):
    """Notification frequency"""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class NotificationStatusEnum(str, Enum):
    """Notification status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Notification Preference Schemas
class NotificationPreferenceBase(BaseModel):
    """Base schema for notification preferences"""
    notification_type: NotificationTypeEnum
    is_enabled: bool = True
    delivery_method: DeliveryMethodEnum = DeliveryMethodEnum.EMAIL
    frequency: FrequencyEnum = FrequencyEnum.IMMEDIATE
    filters: Optional[Dict[str, Any]] = None

class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences"""
    pass

class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences"""
    is_enabled: Optional[bool] = None
    delivery_method: Optional[DeliveryMethodEnum] = None
    frequency: Optional[FrequencyEnum] = None
    filters: Optional[Dict[str, Any]] = None

class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema for notification preference responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Notification Log Schemas
class NotificationLogBase(BaseModel):
    """Base schema for notification logs"""
    entity_type: str
    entity_id: Optional[int] = None
    notification_type: str
    recipients: str
    subject: Optional[str] = None
    content_summary: Optional[str] = None
    status: NotificationStatusEnum = NotificationStatusEnum.SENT
    error_message: Optional[str] = None
    delivery_method: DeliveryMethodEnum = DeliveryMethodEnum.EMAIL
    template_used: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class NotificationLogResponse(NotificationLogBase):
    """Schema for notification log responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sent_date: datetime

# Notification Template Schemas
class NotificationTemplateBase(BaseModel):
    """Base schema for notification templates"""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_type: DeliveryMethodEnum
    subject_template: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema for creating notification templates"""
    pass

class NotificationTemplateUpdate(BaseModel):
    """Schema for updating notification templates"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    subject_template: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None

class NotificationTemplateResponse(NotificationTemplateBase):
    """Schema for notification template responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_system: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Notification Subscription Schemas
class NotificationSubscriptionBase(BaseModel):
    """Base schema for notification subscriptions"""
    entity_type: str = Field(..., min_length=1, max_length=50)
    entity_id: Optional[int] = None
    category: Optional[str] = None
    subscription_type: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True

class NotificationSubscriptionCreate(NotificationSubscriptionBase):
    """Schema for creating notification subscriptions"""
    pass

class NotificationSubscriptionUpdate(BaseModel):
    """Schema for updating notification subscriptions"""
    subscription_type: Optional[str] = None
    is_active: Optional[bool] = None

class NotificationSubscriptionResponse(NotificationSubscriptionBase):
    """Schema for notification subscription responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Notification Queue Schemas
class NotificationQueueBase(BaseModel):
    """Base schema for notification queue"""
    notification_type: str
    entity_type: str
    entity_id: Optional[int] = None
    recipients: str  # JSON string
    template_name: str
    context_data: Dict[str, Any]
    scheduled_for: datetime
    priority: int = 0
    max_attempts: int = 3

class NotificationQueueCreate(NotificationQueueBase):
    """Schema for creating queued notifications"""
    pass

class NotificationQueueResponse(NotificationQueueBase):
    """Schema for notification queue responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: NotificationStatusEnum
    attempts: int
    last_attempt: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

# Notification Channel Schemas
class NotificationChannelBase(BaseModel):
    """Base schema for notification channels"""
    name: str = Field(..., min_length=1, max_length=100)
    channel_type: DeliveryMethodEnum
    configuration: Dict[str, Any]
    is_enabled: bool = True
    is_default: bool = False

class NotificationChannelCreate(NotificationChannelBase):
    """Schema for creating notification channels"""
    pass

class NotificationChannelUpdate(BaseModel):
    """Schema for updating notification channels"""
    configuration: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None

class NotificationChannelResponse(NotificationChannelBase):
    """Schema for notification channel responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Test Notification Schema
class TestNotificationRequest(BaseModel):
    """Schema for test notification requests"""
    recipient_email: Optional[str] = None
    notification_type: str = "test"
    message: Optional[str] = None

# Notification Statistics Schema
class NotificationStatsResponse(BaseModel):
    """Schema for notification statistics"""
    period_days: int
    total_sent: int
    total_failed: int
    success_rate: float
    recent_activity: int
    by_type: Dict[str, Dict[str, int]]

# Batch Notification Schema
class BatchNotificationRequest(BaseModel):
    """Schema for batch notification requests"""
    notification_type: NotificationTypeEnum
    recipients: List[str]  # List of email addresses
    template_name: str
    context_data: Dict[str, Any]
    priority: int = 0
    scheduled_for: Optional[datetime] = None

class BatchNotificationResponse(BaseModel):
    """Schema for batch notification responses"""
    queued_count: int
    failed_count: int
    batch_id: Optional[str] = None
    estimated_delivery: Optional[datetime] = None

# Notification Settings Schema
class NotificationSettingsResponse(BaseModel):
    """Schema for notification system settings"""
    email_enabled: bool
    sms_enabled: bool
    webhook_enabled: bool
    default_frequency: FrequencyEnum
    max_daily_notifications: int
    retry_attempts: int
    queue_processing_enabled: bool

class NotificationSettingsUpdate(BaseModel):
    """Schema for updating notification settings"""
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    default_frequency: Optional[FrequencyEnum] = None
    max_daily_notifications: Optional[int] = None
    retry_attempts: Optional[int] = None
    queue_processing_enabled: Optional[bool] = None