"""
Multi-Factor Authentication Service for Aegis Risk Management Platform
Handles TOTP, SMS, Email, and Backup codes with enterprise security features
"""

import secrets
import hashlib
import pyotp
import qrcode
import io
import base64
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json
from cryptography.fernet import Fernet
import smtplib
# Email imports moved to inside function to avoid import issues

from models.user import User
from models.mfa import MFAMethod, MFASession, MFABackupCode, MFAAttempt, TrustedDevice
from models.audit import AuditLog
from config import settings


class MFAService:
    """Comprehensive MFA service with enterprise features"""
    
    def __init__(self):
        # Initialize encryption key for sensitive data
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for MFA secrets"""
        # In production, store this in secure key management
        key_material = settings.SECRET_KEY.encode() + b"mfa_encryption"
        return base64.urlsafe_b64encode(hashlib.sha256(key_material).digest())
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def _generate_device_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Generate device fingerprint for trusted device identification"""
        fingerprint_data = f"{user_agent}:{ip_address}:{secrets.token_hex(16)}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    # TOTP (Time-based One-Time Password) Implementation
    def setup_totp(self, user: User, db: Session, method_name: str = "Authenticator App") -> Dict:
        """Set up TOTP for a user"""
        
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Create TOTP URI for QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=settings.APP_NAME
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Convert QR code to base64 image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_b64}"
        
        # Create MFA method record
        mfa_method = MFAMethod(
            user_id=user.id,
            method_type="totp",
            method_name=method_name,
            secret_key=self._encrypt_data(secret),
            qr_code_url=qr_code_url,
            is_verified=False,
            is_active=True
        )
        
        db.add(mfa_method)
        db.commit()
        db.refresh(mfa_method)
        
        # Log MFA setup
        audit_log = AuditLog(
            event_type="mfa_setup",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            action="TOTP setup initiated",
            description=f"TOTP MFA method setup started for {user.email}",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "method_id": mfa_method.id,
            "secret": secret,  # Return for manual entry
            "qr_code_url": qr_code_url,
            "backup_codes": []  # Generated after verification
        }
    
    def verify_totp_setup(self, user: User, method_id: int, token: str, db: Session) -> Dict:
        """Verify TOTP setup with initial token"""
        
        mfa_method = db.query(MFAMethod).filter(
            MFAMethod.id == method_id,
            MFAMethod.user_id == user.id,
            MFAMethod.method_type == "totp"
        ).first()
        
        if not mfa_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MFA method not found"
            )
        
        # Decrypt secret and verify token
        secret = self._decrypt_data(mfa_method.secret_key)
        totp = pyotp.TOTP(secret)
        
        if not totp.verify(token, valid_window=1):
            # Log failed verification
            attempt = MFAAttempt(
                user_id=user.id,
                method_id=method_id,
                method_type="totp",
                success=False,
                failure_reason="invalid_token"
            )
            db.add(attempt)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        
        # Mark method as verified
        mfa_method.is_verified = True
        mfa_method.setup_completed_at = datetime.utcnow()
        
        # Generate backup codes
        backup_codes = self._generate_backup_codes(user, mfa_method, db)
        
        # Enable MFA for user if this is their first method
        if not user.mfa_enabled:
            user.mfa_enabled = True
        
        # Set as primary if no other primary method exists
        primary_method = db.query(MFAMethod).filter(
            MFAMethod.user_id == user.id,
            MFAMethod.is_primary == True,
            MFAMethod.is_verified == True
        ).first()
        
        if not primary_method:
            mfa_method.is_primary = True
        
        db.commit()
        
        # Log successful setup
        audit_log = AuditLog(
            event_type="mfa_enabled",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            action="TOTP setup completed",
            description=f"TOTP MFA method verified and activated for {user.email}",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "backup_codes": backup_codes,
            "message": "TOTP MFA setup completed successfully"
        }
    
    def verify_totp_code(self, user: User, token: str, db: Session) -> bool:
        """Verify TOTP code for authentication"""
        
        # Get primary TOTP method
        totp_method = db.query(MFAMethod).filter(
            MFAMethod.user_id == user.id,
            MFAMethod.method_type == "totp",
            MFAMethod.is_verified == True,
            MFAMethod.is_active == True
        ).first()
        
        if not totp_method:
            return False
        
        # Decrypt secret and verify
        secret = self._decrypt_data(totp_method.secret_key)
        totp = pyotp.TOTP(secret)
        
        is_valid = totp.verify(token, valid_window=1)
        
        # Log attempt
        attempt = MFAAttempt(
            user_id=user.id,
            method_id=totp_method.id,
            method_type="totp",
            success=is_valid,
            failure_reason=None if is_valid else "invalid_token"
        )
        db.add(attempt)
        
        if is_valid:
            totp_method.last_used = datetime.utcnow()
        
        db.commit()
        
        return is_valid
    
    # SMS Implementation
    def setup_sms_mfa(self, user: User, phone_number: str, db: Session) -> Dict:
        """Set up SMS MFA for a user"""
        
        # Validate phone number format (basic validation)
        if not phone_number.startswith('+') or len(phone_number) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        
        # Create MFA method record
        mfa_method = MFAMethod(
            user_id=user.id,
            method_type="sms",
            method_name=f"SMS to {phone_number[-4:]}",
            phone_number=phone_number,
            is_verified=False,
            is_active=True
        )
        
        db.add(mfa_method)
        db.commit()
        db.refresh(mfa_method)
        
        # Send verification code
        session_data = self._send_sms_verification(user, mfa_method, db)
        
        return {
            "method_id": mfa_method.id,
            "session_token": session_data["session_token"],
            "message": f"Verification code sent to {phone_number}"
        }
    
    def _send_sms_verification(self, user: User, mfa_method: MFAMethod, db: Session) -> Dict:
        """Send SMS verification code"""
        
        # Generate 6-digit code
        verification_code = str(secrets.randbelow(900000) + 100000)
        
        # Create MFA session
        session_token = secrets.token_urlsafe(32)
        session = MFASession(
            user_id=user.id,
            session_token=session_token,
            method_type="sms",
            method_id=mfa_method.id,
            verification_code=self._encrypt_data(verification_code),
            challenge_sent_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            attempts_remaining=3
        )
        
        db.add(session)
        db.commit()
        
        # In production, integrate with SMS provider (Twilio, AWS SNS, etc.)
        # For now, log the code (REMOVE IN PRODUCTION)
        print(f"SMS Verification Code for {user.email}: {verification_code}")
        
        # Log SMS sent
        audit_log = AuditLog(
            event_type="mfa_challenge",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            action="SMS verification sent",
            description=f"SMS verification code sent to {mfa_method.phone_number}",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "session_token": session_token,
            "expires_at": session.expires_at
        }
    
    # Email Implementation
    def setup_email_mfa(self, user: User, email_address: str, db: Session) -> Dict:
        """Set up Email MFA for a user"""
        
        # Create MFA method record
        mfa_method = MFAMethod(
            user_id=user.id,
            method_type="email",
            method_name=f"Email to {email_address}",
            email_address=email_address,
            is_verified=False,
            is_active=True
        )
        
        db.add(mfa_method)
        db.commit()
        db.refresh(mfa_method)
        
        # Send verification email
        session_data = self._send_email_verification(user, mfa_method, db)
        
        return {
            "method_id": mfa_method.id,
            "session_token": session_data["session_token"],
            "message": f"Verification code sent to {email_address}"
        }
    
    def _send_email_verification(self, user: User, mfa_method: MFAMethod, db: Session) -> Dict:
        """Send email verification code"""
        
        # Generate 8-character alphanumeric code
        verification_code = secrets.token_urlsafe(6).upper()
        
        # Create MFA session
        session_token = secrets.token_urlsafe(32)
        session = MFASession(
            user_id=user.id,
            session_token=session_token,
            method_type="email",
            method_id=mfa_method.id,
            verification_code=self._encrypt_data(verification_code),
            challenge_sent_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            attempts_remaining=3
        )
        
        db.add(session)
        db.commit()
        
        # Send email (if SMTP is configured)
        if settings.ENABLE_EMAIL:
            self._send_verification_email(mfa_method.email_address, verification_code, user.full_name)
        else:
            # Log the code for development
            print(f"Email Verification Code for {user.email}: {verification_code}")
        
        return {
            "session_token": session_token,
            "expires_at": session.expires_at
        }
    
    def _send_verification_email(self, email: str, code: str, user_name: str):
        """Send verification email via SMTP"""
        try:
            from email.mime.text import MimeText
            from email.mime.multipart import MimeMultipart
            
            msg = MimeMultipart()
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = email
            msg['Subject'] = f"{settings.APP_NAME} - Verification Code"
            
            body = f"""
            Hello {user_name},
            
            Your verification code for {settings.APP_NAME} is: {code}
            
            This code will expire in 15 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            {settings.APP_NAME} Security Team
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send verification email: {e}")
    
    # Backup Codes Implementation
    def _generate_backup_codes(self, user: User, mfa_method: MFAMethod, db: Session) -> List[str]:
        """Generate backup codes for MFA recovery"""
        
        backup_codes = []
        for _ in range(10):  # Generate 10 backup codes
            code = f"{secrets.token_hex(4)}-{secrets.token_hex(4)}".upper()
            backup_codes.append(code)
            
            # Hash and store backup code
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            backup_code_record = MFABackupCode(
                user_id=user.id,
                method_id=mfa_method.id,
                code_hash=code_hash
            )
            db.add(backup_code_record)
        
        user.mfa_backup_codes_generated = True
        db.commit()
        
        return backup_codes
    
    def verify_backup_code(self, user: User, code: str, db: Session) -> bool:
        """Verify backup code for MFA recovery"""
        
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        backup_code = db.query(MFABackupCode).filter(
            MFABackupCode.user_id == user.id,
            MFABackupCode.code_hash == code_hash,
            MFABackupCode.is_used == False
        ).first()
        
        if backup_code:
            # Mark code as used
            backup_code.is_used = True
            backup_code.used_at = datetime.utcnow()
            db.commit()
            
            # Log backup code usage
            audit_log = AuditLog(
                event_type="mfa_backup_used",
                entity_type="user",
                entity_id=user.id,
                user_id=user.id,
                action="Backup code used",
                description=f"MFA backup code used for {user.email}",
                source="web_ui",
                risk_level="medium"
            )
            db.add(audit_log)
            db.commit()
            
            return True
        
        return False
    
    # Trusted Device Implementation
    def add_trusted_device(self, user: User, device_name: str, user_agent: str, 
                          ip_address: str, db: Session, trust_days: int = 30) -> Dict:
        """Add device to trusted devices list"""
        
        device_fingerprint = self._generate_device_fingerprint(user_agent, ip_address)
        
        # Check if device already exists
        existing_device = db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user.id,
            TrustedDevice.device_fingerprint == device_fingerprint,
            TrustedDevice.is_active == True
        ).first()
        
        if existing_device:
            # Update existing device
            existing_device.trust_expires_at = datetime.utcnow() + timedelta(days=trust_days)
            existing_device.last_used = datetime.utcnow()
            existing_device.last_ip = ip_address
            db.commit()
            return {"device_id": existing_device.id, "message": "Device trust updated"}
        
        # Create new trusted device
        trusted_device = TrustedDevice(
            user_id=user.id,
            device_fingerprint=device_fingerprint,
            device_name=device_name,
            trust_expires_at=datetime.utcnow() + timedelta(days=trust_days),
            first_ip=ip_address,
            last_ip=ip_address,
            last_used=datetime.utcnow()
        )
        
        db.add(trusted_device)
        db.commit()
        db.refresh(trusted_device)
        
        # Log trusted device addition
        audit_log = AuditLog(
            event_type="trusted_device_added",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            action="Trusted device added",
            description=f"Device '{device_name}' added to trusted devices for {user.email}",
            source="web_ui",
            risk_level="low"
        )
        db.add(audit_log)
        db.commit()
        
        return {"device_id": trusted_device.id, "message": "Device added to trusted list"}
    
    def is_trusted_device(self, user: User, user_agent: str, ip_address: str, db: Session) -> bool:
        """Check if device is trusted"""
        
        device_fingerprint = self._generate_device_fingerprint(user_agent, ip_address)
        
        trusted_device = db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user.id,
            TrustedDevice.device_fingerprint == device_fingerprint,
            TrustedDevice.is_active == True,
            TrustedDevice.trust_expires_at > datetime.utcnow()
        ).first()
        
        if trusted_device:
            # Update last used
            trusted_device.last_used = datetime.utcnow()
            trusted_device.last_ip = ip_address
            db.commit()
            return True
        
        return False
    
    # General MFA Management
    def get_user_mfa_methods(self, user: User, db: Session) -> List[Dict]:
        """Get all MFA methods for a user"""
        
        methods = db.query(MFAMethod).filter(
            MFAMethod.user_id == user.id,
            MFAMethod.is_active == True
        ).all()
        
        result = []
        for method in methods:
            method_data = {
                "id": method.id,
                "type": method.method_type,
                "name": method.method_name,
                "is_verified": method.is_verified,
                "is_primary": method.is_primary,
                "last_used": method.last_used,
                "created_at": method.created_at
            }
            
            # Add method-specific details
            if method.method_type == "sms":
                method_data["phone_number"] = method.phone_number
            elif method.method_type == "email":
                method_data["email_address"] = method.email_address
            
            result.append(method_data)
        
        return result
    
    def disable_mfa_method(self, user: User, method_id: int, db: Session) -> Dict:
        """Disable an MFA method"""
        
        method = db.query(MFAMethod).filter(
            MFAMethod.id == method_id,
            MFAMethod.user_id == user.id
        ).first()
        
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MFA method not found"
            )
        
        method.is_active = False
        
        # If this was the primary method, set another verified method as primary
        if method.is_primary:
            method.is_primary = False
            other_method = db.query(MFAMethod).filter(
                MFAMethod.user_id == user.id,
                MFAMethod.id != method_id,
                MFAMethod.is_verified == True,
                MFAMethod.is_active == True
            ).first()
            
            if other_method:
                other_method.is_primary = True
            else:
                # No other methods, disable MFA for user
                user.mfa_enabled = False
        
        db.commit()
        
        # Log MFA method disabled
        audit_log = AuditLog(
            event_type="mfa_disabled",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            action="MFA method disabled",
            description=f"MFA method '{method.method_name}' disabled for {user.email}",
            source="web_ui",
            risk_level="medium"
        )
        db.add(audit_log)
        db.commit()
        
        return {"message": f"MFA method '{method.method_name}' disabled successfully"}


# Global MFA service instance
mfa_service = MFAService()