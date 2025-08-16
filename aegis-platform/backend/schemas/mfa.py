"""
MFA (Multi-Factor Authentication) Schemas for Aegis Risk Management Platform
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Base schemas
class MFAMethodBase(BaseModel):
    method_type: str = Field(..., description="Type of MFA method (totp, sms, email)")
    method_name: Optional[str] = Field(None, description="User-friendly name for the method")


class MFAMethodCreate(MFAMethodBase):
    phone_number: Optional[str] = Field(None, description="Phone number for SMS")
    email_address: Optional[str] = Field(None, description="Email address for email MFA")


class MFAMethodResponse(MFAMethodBase):
    id: int
    is_verified: bool
    is_active: bool
    is_primary: bool
    last_used: Optional[datetime]
    created_at: datetime
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    
    class Config:
        from_attributes = True


# TOTP Setup schemas
class TOTPSetupRequest(BaseModel):
    method_name: Optional[str] = Field("Authenticator App", description="Name for this TOTP method")


class TOTPSetupResponse(BaseModel):
    method_id: int
    secret: str = Field(..., description="TOTP secret for manual entry")
    qr_code_url: str = Field(..., description="QR code data URL")
    backup_codes: List[str] = Field([], description="Backup codes (empty until verified)")


class TOTPVerifyRequest(BaseModel):
    method_id: int
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")


class TOTPVerifyResponse(BaseModel):
    success: bool
    backup_codes: List[str] = Field(..., description="Generated backup codes")
    message: str


# SMS MFA schemas
class SMSSetupRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number in international format (+1234567890)")
    method_name: Optional[str] = Field(None, description="Optional name for this SMS method")


class SMSSetupResponse(BaseModel):
    method_id: int
    session_token: str
    message: str


# Email MFA schemas
class EmailSetupRequest(BaseModel):
    email_address: str = Field(..., description="Email address for MFA codes")
    method_name: Optional[str] = Field(None, description="Optional name for this email method")


class EmailSetupResponse(BaseModel):
    method_id: int
    session_token: str
    message: str


# Verification schemas
class MFAVerifyRequest(BaseModel):
    method_type: str = Field(..., description="Type of MFA method (totp, sms, email, backup)")
    code: str = Field(..., description="Verification code")
    session_token: Optional[str] = Field(None, description="Session token for SMS/Email")
    trust_device: Optional[bool] = Field(False, description="Add device to trusted list")
    device_name: Optional[str] = Field(None, description="Name for trusted device")


class MFAVerifyResponse(BaseModel):
    success: bool
    message: str
    device_trusted: Optional[bool] = Field(None, description="Whether device was added to trusted list")


# Session management schemas
class MFASessionRequest(BaseModel):
    method_type: str = Field(..., description="Type of MFA challenge to send")
    method_id: Optional[int] = Field(None, description="Specific method ID (optional)")


class MFASessionResponse(BaseModel):
    session_token: str
    method_type: str
    expires_at: datetime
    attempts_remaining: int
    message: str


# Backup codes schemas
class BackupCodeRequest(BaseModel):
    code: str = Field(..., description="Backup recovery code")


class BackupCodeResponse(BaseModel):
    success: bool
    message: str
    remaining_codes: int = Field(..., description="Number of remaining backup codes")


class BackupCodesRegenerateResponse(BaseModel):
    backup_codes: List[str] = Field(..., description="New backup codes")
    message: str


# Trusted device schemas
class TrustedDeviceCreate(BaseModel):
    device_name: str = Field(..., description="User-friendly device name")
    trust_days: Optional[int] = Field(30, description="Number of days to trust device")


class TrustedDeviceResponse(BaseModel):
    id: int
    device_name: str
    device_type: Optional[str]
    browser: Optional[str]
    operating_system: Optional[str]
    is_active: bool
    trust_expires_at: datetime
    last_used: Optional[datetime]
    first_ip: str
    last_ip: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Admin management schemas
class MFAStatusResponse(BaseModel):
    user_id: int
    mfa_enabled: bool
    mfa_enforced: bool
    methods_count: int
    verified_methods_count: int
    primary_method: Optional[str]
    backup_codes_generated: bool
    trusted_devices_count: int


class MFAEnforcementRequest(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs to enforce MFA")
    enforce: bool = Field(..., description="Whether to enforce or remove enforcement")
    grace_period_days: Optional[int] = Field(7, description="Grace period for compliance")


class MFAEnforcementResponse(BaseModel):
    success: bool
    affected_users: int
    message: str


# Statistics and analytics schemas
class MFAStatistics(BaseModel):
    total_users: int
    mfa_enabled_users: int
    mfa_adoption_rate: float
    totp_users: int
    sms_users: int
    email_users: int
    backup_codes_generated: int
    trusted_devices: int
    recent_attempts: int
    success_rate: float


class MFASecurityEvent(BaseModel):
    event_id: int
    user_id: Optional[int]
    event_type: str
    method_type: str
    success: bool
    ip_address: Optional[str]
    user_agent: Optional[str]
    risk_score: int
    anomaly_detected: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Comprehensive user MFA status
class UserMFAStatus(BaseModel):
    mfa_enabled: bool
    mfa_enforced: bool
    methods: List[MFAMethodResponse]
    backup_codes_generated: bool
    backup_codes_remaining: int
    trusted_devices: List[TrustedDeviceResponse]
    recent_attempts: int
    last_successful_auth: Optional[datetime]


# Error response schemas
class MFAError(BaseModel):
    error: str
    detail: str
    error_code: Optional[str] = None


# Admin bulk operations
class BulkMFAOperation(BaseModel):
    operation: str = Field(..., description="Operation type (enforce, disable, reset)")
    user_ids: List[int] = Field(..., description="List of user IDs")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation-specific parameters")


class BulkMFAOperationResponse(BaseModel):
    operation: str
    total_users: int
    successful: int
    failed: int
    errors: List[Dict[str, str]] = Field([], description="List of errors for failed operations")
    results: List[Dict[str, Any]] = Field(..., description="Detailed results per user")