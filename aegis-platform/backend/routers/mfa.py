"""
Multi-Factor Authentication (MFA) Router for Aegis Risk Management Platform
Provides comprehensive MFA endpoints for enterprise security
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from database import get_db
from auth import get_current_active_user
from models.user import User
from models.mfa import MFAMethod, MFASession, MFABackupCode, TrustedDevice, MFAAttempt
from models.audit import AuditLog
from services.mfa_service import mfa_service
from schemas.mfa import (
    TOTPSetupRequest, TOTPSetupResponse, TOTPVerifyRequest, TOTPVerifyResponse,
    SMSSetupRequest, SMSSetupResponse, EmailSetupRequest, EmailSetupResponse,
    MFAVerifyRequest, MFAVerifyResponse, MFASessionRequest, MFASessionResponse,
    BackupCodeRequest, BackupCodeResponse, BackupCodesRegenerateResponse,
    TrustedDeviceCreate, TrustedDeviceResponse, MFAStatusResponse,
    UserMFAStatus, MFAMethodResponse, MFAStatistics, MFASecurityEvent,
    MFAEnforcementRequest, MFAEnforcementResponse, BulkMFAOperation, BulkMFAOperationResponse
)

router = APIRouter()


def get_client_info(request: Request, user_agent: Optional[str] = Header(None)):
    """Extract client information from request"""
    client_ip = request.client.host if request.client else "unknown"
    return {
        "ip_address": client_ip,
        "user_agent": user_agent or "unknown"
    }


# TOTP Endpoints
@router.post("/totp/setup", response_model=TOTPSetupResponse)
async def setup_totp(
    request: TOTPSetupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set up TOTP (Time-based One-Time Password) authentication"""
    
    # Check if user already has a verified TOTP method
    existing_totp = db.query(MFAMethod).filter(
        MFAMethod.user_id == current_user.id,
        MFAMethod.method_type == "totp",
        MFAMethod.is_verified == True,
        MFAMethod.is_active == True
    ).first()
    
    if existing_totp:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="TOTP is already configured for this user"
        )
    
    result = mfa_service.setup_totp(current_user, db, request.method_name)
    return result


@router.post("/totp/verify", response_model=TOTPVerifyResponse)
async def verify_totp_setup(
    request: TOTPVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify TOTP setup with initial token"""
    
    result = mfa_service.verify_totp_setup(current_user, request.method_id, request.token, db)
    return result


# SMS MFA Endpoints
@router.post("/sms/setup", response_model=SMSSetupResponse)
async def setup_sms_mfa(
    request: SMSSetupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set up SMS-based MFA"""
    
    result = mfa_service.setup_sms_mfa(current_user, request.phone_number, db)
    return result


@router.post("/sms/send")
async def send_sms_code(
    method_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send SMS verification code"""
    
    mfa_method = db.query(MFAMethod).filter(
        MFAMethod.id == method_id,
        MFAMethod.user_id == current_user.id,
        MFAMethod.method_type == "sms",
        MFAMethod.is_active == True
    ).first()
    
    if not mfa_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS MFA method not found"
        )
    
    session_data = mfa_service._send_sms_verification(current_user, mfa_method, db)
    return {"session_token": session_data["session_token"], "message": "SMS code sent"}


# Email MFA Endpoints
@router.post("/email/setup", response_model=EmailSetupResponse)
async def setup_email_mfa(
    request: EmailSetupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set up Email-based MFA"""
    
    result = mfa_service.setup_email_mfa(current_user, request.email_address, db)
    return result


@router.post("/email/send")
async def send_email_code(
    method_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send email verification code"""
    
    mfa_method = db.query(MFAMethod).filter(
        MFAMethod.id == method_id,
        MFAMethod.user_id == current_user.id,
        MFAMethod.method_type == "email",
        MFAMethod.is_active == True
    ).first()
    
    if not mfa_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email MFA method not found"
        )
    
    session_data = mfa_service._send_email_verification(current_user, mfa_method, db)
    return {"session_token": session_data["session_token"], "message": "Email code sent"}


# General MFA Verification
@router.post("/verify", response_model=MFAVerifyResponse)
async def verify_mfa_code(
    request: MFAVerifyRequest,
    req: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(None)
):
    """Verify MFA code for authentication"""
    
    client_info = get_client_info(req, user_agent)
    success = False
    message = "Invalid verification code"
    device_trusted = False
    
    if request.method_type == "totp":
        success = mfa_service.verify_totp_code(current_user, request.code, db)
        if success:
            message = "TOTP verification successful"
    
    elif request.method_type == "backup":
        success = mfa_service.verify_backup_code(current_user, request.code, db)
        if success:
            message = "Backup code verification successful"
    
    elif request.method_type in ["sms", "email"]:
        if not request.session_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session token required for SMS/Email verification"
            )
        
        # Verify session-based code
        session = db.query(MFASession).filter(
            MFASession.session_token == request.session_token,
            MFASession.user_id == current_user.id,
            MFASession.method_type == request.method_type,
            MFASession.expires_at > datetime.utcnow(),
            MFASession.is_verified == False
        ).first()
        
        if not session or session.attempts_remaining <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired session"
            )
        
        # Decrypt and verify code
        stored_code = mfa_service._decrypt_data(session.verification_code)
        if request.code == stored_code:
            success = True
            session.is_verified = True
            session.verified_at = datetime.utcnow()
            message = f"{request.method_type.upper()} verification successful"
        else:
            session.attempts_remaining -= 1
            message = f"Invalid code. {session.attempts_remaining} attempts remaining"
        
        db.commit()
    
    # Handle trusted device
    if success and request.trust_device:
        device_name = request.device_name or f"Device - {datetime.utcnow().strftime('%Y-%m-%d')}"
        result = mfa_service.add_trusted_device(
            current_user, device_name, client_info["user_agent"], client_info["ip_address"], db
        )
        device_trusted = True
        message += f" Device '{device_name}' added to trusted list."
    
    # Log verification attempt
    attempt = MFAAttempt(
        user_id=current_user.id,
        method_type=request.method_type,
        success=success,
        failure_reason=None if success else "invalid_code",
        ip_address=client_info["ip_address"],
        user_agent=client_info["user_agent"]
    )
    db.add(attempt)
    db.commit()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return MFAVerifyResponse(
        success=success,
        message=message,
        device_trusted=device_trusted
    )


# Backup Codes Management
@router.post("/backup-codes/verify", response_model=BackupCodeResponse)
async def verify_backup_code(
    request: BackupCodeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify backup recovery code"""
    
    success = mfa_service.verify_backup_code(current_user, request.code, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid backup code"
        )
    
    # Count remaining backup codes
    remaining = db.query(MFABackupCode).filter(
        MFABackupCode.user_id == current_user.id,
        MFABackupCode.is_used == False
    ).count()
    
    return BackupCodeResponse(
        success=True,
        message="Backup code verified successfully",
        remaining_codes=remaining
    )


@router.post("/backup-codes/regenerate", response_model=BackupCodesRegenerateResponse)
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate backup codes for user"""
    
    # Check if user has verified MFA methods
    verified_method = db.query(MFAMethod).filter(
        MFAMethod.user_id == current_user.id,
        MFAMethod.is_verified == True,
        MFAMethod.is_active == True
    ).first()
    
    if not verified_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verified MFA methods found"
        )
    
    # Mark existing backup codes as used
    existing_codes = db.query(MFABackupCode).filter(
        MFABackupCode.user_id == current_user.id,
        MFABackupCode.is_used == False
    ).all()
    
    for code in existing_codes:
        code.is_used = True
    
    # Generate new backup codes
    backup_codes = mfa_service._generate_backup_codes(current_user, verified_method, db)
    
    # Log backup codes regeneration
    audit_log = AuditLog(
        event_type="mfa_backup_regenerated",
        entity_type="user",
        entity_id=current_user.id,
        user_id=current_user.id,
        action="Backup codes regenerated",
        description=f"MFA backup codes regenerated for {current_user.email}",
        source="web_ui",
        risk_level="medium"
    )
    db.add(audit_log)
    db.commit()
    
    return BackupCodesRegenerateResponse(
        backup_codes=backup_codes,
        message="New backup codes generated successfully"
    )


# Trusted Devices Management
@router.get("/trusted-devices", response_model=List[TrustedDeviceResponse])
async def get_trusted_devices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's trusted devices"""
    
    devices = db.query(TrustedDevice).filter(
        TrustedDevice.user_id == current_user.id,
        TrustedDevice.is_active == True
    ).all()
    
    return devices


@router.delete("/trusted-devices/{device_id}")
async def remove_trusted_device(
    device_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a trusted device"""
    
    device = db.query(TrustedDevice).filter(
        TrustedDevice.id == device_id,
        TrustedDevice.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trusted device not found"
        )
    
    device.is_active = False
    db.commit()
    
    # Log device removal
    audit_log = AuditLog(
        event_type="trusted_device_removed",
        entity_type="user",
        entity_id=current_user.id,
        user_id=current_user.id,
        action="Trusted device removed",
        description=f"Trusted device '{device.device_name}' removed for {current_user.email}",
        source="web_ui",
        risk_level="low"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Trusted device removed successfully"}


# MFA Methods Management
@router.get("/methods", response_model=List[MFAMethodResponse])
async def get_mfa_methods(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's MFA methods"""
    
    methods = mfa_service.get_user_mfa_methods(current_user, db)
    return methods


@router.delete("/methods/{method_id}")
async def disable_mfa_method(
    method_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable an MFA method"""
    
    result = mfa_service.disable_mfa_method(current_user, method_id, db)
    return result


@router.put("/methods/{method_id}/primary")
async def set_primary_method(
    method_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set an MFA method as primary"""
    
    method = db.query(MFAMethod).filter(
        MFAMethod.id == method_id,
        MFAMethod.user_id == current_user.id,
        MFAMethod.is_verified == True,
        MFAMethod.is_active == True
    ).first()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MFA method not found or not verified"
        )
    
    # Remove primary flag from other methods
    db.query(MFAMethod).filter(
        MFAMethod.user_id == current_user.id,
        MFAMethod.is_primary == True
    ).update({"is_primary": False})
    
    # Set this method as primary
    method.is_primary = True
    db.commit()
    
    return {"message": f"'{method.method_name}' set as primary MFA method"}


# User MFA Status
@router.get("/status", response_model=UserMFAStatus)
async def get_mfa_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive MFA status for current user"""
    
    methods = mfa_service.get_user_mfa_methods(current_user, db)
    
    # Get trusted devices
    trusted_devices = db.query(TrustedDevice).filter(
        TrustedDevice.user_id == current_user.id,
        TrustedDevice.is_active == True
    ).all()
    
    # Get backup codes count
    backup_codes_remaining = db.query(MFABackupCode).filter(
        MFABackupCode.user_id == current_user.id,
        MFABackupCode.is_used == False
    ).count()
    
    # Get recent attempts count
    recent_attempts = db.query(MFAAttempt).filter(
        MFAAttempt.user_id == current_user.id,
        MFAAttempt.created_at > datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Get last successful authentication
    last_success = db.query(MFAAttempt).filter(
        MFAAttempt.user_id == current_user.id,
        MFAAttempt.success == True
    ).order_by(MFAAttempt.created_at.desc()).first()
    
    return UserMFAStatus(
        mfa_enabled=current_user.mfa_enabled,
        mfa_enforced=current_user.mfa_enforced,
        methods=methods,
        backup_codes_generated=current_user.mfa_backup_codes_generated,
        backup_codes_remaining=backup_codes_remaining,
        trusted_devices=trusted_devices,
        recent_attempts=recent_attempts,
        last_successful_auth=last_success.created_at if last_success else None
    )


# Check device trust status
@router.get("/device-status")
async def check_device_trust(
    req: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(None)
):
    """Check if current device is trusted"""
    
    client_info = get_client_info(req, user_agent)
    is_trusted = mfa_service.is_trusted_device(
        current_user, client_info["user_agent"], client_info["ip_address"], db
    )
    
    return {
        "is_trusted": is_trusted,
        "requires_mfa": current_user.mfa_enabled and not is_trusted
    }


# Admin endpoints (require appropriate permissions)
@router.get("/admin/statistics", response_model=MFAStatistics)
async def get_mfa_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get MFA adoption and usage statistics (Admin only)"""
    
    # Check admin permissions (implement based on your RBAC system)
    # For now, just check if user has admin role
    admin_role = any(role.name == "Admin" for role in current_user.roles if hasattr(current_user, 'roles'))
    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Calculate statistics
    total_users = db.query(User).filter(User.is_active == True).count()
    mfa_enabled_users = db.query(User).filter(User.mfa_enabled == True).count()
    
    totp_users = db.query(MFAMethod).filter(
        MFAMethod.method_type == "totp",
        MFAMethod.is_verified == True,
        MFAMethod.is_active == True
    ).count()
    
    sms_users = db.query(MFAMethod).filter(
        MFAMethod.method_type == "sms",
        MFAMethod.is_verified == True,
        MFAMethod.is_active == True
    ).count()
    
    email_users = db.query(MFAMethod).filter(
        MFAMethod.method_type == "email",
        MFAMethod.is_verified == True,
        MFAMethod.is_active == True
    ).count()
    
    backup_codes_generated = db.query(User).filter(User.mfa_backup_codes_generated == True).count()
    trusted_devices = db.query(TrustedDevice).filter(TrustedDevice.is_active == True).count()
    
    recent_attempts = db.query(MFAAttempt).filter(
        MFAAttempt.created_at > datetime.utcnow() - timedelta(days=7)
    ).count()
    
    successful_attempts = db.query(MFAAttempt).filter(
        MFAAttempt.created_at > datetime.utcnow() - timedelta(days=7),
        MFAAttempt.success == True
    ).count()
    
    success_rate = (successful_attempts / recent_attempts * 100) if recent_attempts > 0 else 0
    adoption_rate = (mfa_enabled_users / total_users * 100) if total_users > 0 else 0
    
    return MFAStatistics(
        total_users=total_users,
        mfa_enabled_users=mfa_enabled_users,
        mfa_adoption_rate=round(adoption_rate, 2),
        totp_users=totp_users,
        sms_users=sms_users,
        email_users=email_users,
        backup_codes_generated=backup_codes_generated,
        trusted_devices=trusted_devices,
        recent_attempts=recent_attempts,
        success_rate=round(success_rate, 2)
    )


@router.post("/admin/enforce", response_model=MFAEnforcementResponse)
async def enforce_mfa(
    request: MFAEnforcementRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enforce or remove MFA enforcement for specified users (Admin only)"""
    
    # Check admin permissions
    admin_role = any(role.name == "Admin" for role in current_user.roles if hasattr(current_user, 'roles'))
    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    affected_users = 0
    for user_id in request.user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.mfa_enforced = request.enforce
            affected_users += 1
            
            # Log enforcement change
            audit_log = AuditLog(
                event_type="mfa_enforcement_changed",
                entity_type="user",
                entity_id=user.id,
                user_id=current_user.id,
                action=f"MFA enforcement {'enabled' if request.enforce else 'disabled'}",
                description=f"MFA enforcement {'enabled' if request.enforce else 'disabled'} for {user.email} by admin",
                source="admin_ui",
                risk_level="medium"
            )
            db.add(audit_log)
    
    db.commit()
    
    return MFAEnforcementResponse(
        success=True,
        affected_users=affected_users,
        message=f"MFA enforcement {'enabled' if request.enforce else 'disabled'} for {affected_users} users"
    )