from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(Text)  # JSON string of permissions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Clean relationships
    user_roles = relationship("UserRole")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    profile_picture = Column(String(500))
    department = Column(String(100))
    job_title = Column(String(100))
    phone = Column(String(20))
    # OAuth/SSO Integration Fields
    azure_ad_id = Column(String(255))  # For Azure AD integration
    external_id = Column(String(255))  # For generic OAuth provider IDs
    provider = Column(String(50))  # OAuth provider name (azure_ad, google_workspace, okta)
    created_via_sso = Column(Boolean, default=False)
    preferences = Column(Text)  # JSON string for user preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_roles = relationship("UserRole")
    created_assessments = relationship("Assessment", foreign_keys="Assessment.created_by_id", back_populates="created_by_user")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to")
    created_tasks = relationship("Task", foreign_keys="Task.created_by_id", back_populates="created_by")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Notification relationships
    notification_preferences = relationship("NotificationPreference", back_populates="user")
    notification_subscriptions = relationship("NotificationSubscription", back_populates="user")


class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Clean relationships - no back_populates for now
    user = relationship("User")
    role = relationship("Role")