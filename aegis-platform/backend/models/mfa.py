"""
Multi-Factor Authentication (MFA) Models for Aegis Risk Management Platform
Supports TOTP, SMS, Email, and Backup codes
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class MFAMethod(Base):
    """MFA authentication methods for users"""
    __tablename__ = "mfa_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    method_type = Column(String(20), nullable=False)  # totp, sms, email, backup_codes
    method_name = Column(String(100))  # User-friendly name like "iPhone Authenticator"
    
    # TOTP specific fields
    secret_key = Column(String(255))  # Encrypted TOTP secret
    qr_code_url = Column(Text)  # QR code data URL for setup
    
    # SMS/Email specific fields
    phone_number = Column(String(20))  # For SMS
    email_address = Column(String(255))  # For email (might differ from main email)
    
    # Backup codes
    backup_codes = Column(JSON)  # Encrypted array of backup codes
    
    # Status and metadata
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary MFA method
    last_used = Column(DateTime(timezone=True))
    verification_attempts = Column(Integer, default=0)
    setup_completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mfa_methods")


class MFASession(Base):
    """Temporary MFA verification sessions"""
    __tablename__ = "mfa_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    
    # Session details
    method_type = Column(String(20), nullable=False)
    method_id = Column(Integer, ForeignKey("mfa_methods.id"))
    challenge_sent_at = Column(DateTime(timezone=True))
    verification_code = Column(String(255))  # Encrypted temporary code
    attempts_remaining = Column(Integer, default=3)
    
    # Security metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    location = Column(String(255))  # Optional geo-location
    
    # Session management
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    mfa_method = relationship("MFAMethod")


class MFABackupCode(Base):
    """Individual backup codes for MFA recovery"""
    __tablename__ = "mfa_backup_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    method_id = Column(Integer, ForeignKey("mfa_methods.id"), nullable=False)
    
    code_hash = Column(String(255), nullable=False)  # Hashed backup code
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True))
    used_ip = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    mfa_method = relationship("MFAMethod")


class MFAAttempt(Base):
    """Log of MFA verification attempts for security monitoring"""
    __tablename__ = "mfa_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("mfa_sessions.id"))
    method_id = Column(Integer, ForeignKey("mfa_methods.id"))
    
    # Attempt details
    method_type = Column(String(20), nullable=False)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255))  # invalid_code, expired, too_many_attempts, etc.
    
    # Security context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    location = Column(String(255))
    
    # Risk assessment
    risk_score = Column(Integer, default=0)  # 0-100 risk score
    anomaly_detected = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    session = relationship("MFASession")
    mfa_method = relationship("MFAMethod")


class TrustedDevice(Base):
    """Trusted devices that can bypass MFA for a period"""
    __tablename__ = "trusted_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Device identification
    device_fingerprint = Column(String(255), nullable=False)  # Hashed device characteristics
    device_name = Column(String(100))  # User-friendly device name
    device_type = Column(String(50))  # mobile, desktop, tablet
    browser = Column(String(100))
    operating_system = Column(String(100))
    
    # Trust management
    is_active = Column(Boolean, default=True)
    trust_expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used = Column(DateTime(timezone=True))
    
    # Security metadata
    first_ip = Column(String(45))  # IP when first trusted
    last_ip = Column(String(45))  # Most recent IP
    location = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trusted_devices")