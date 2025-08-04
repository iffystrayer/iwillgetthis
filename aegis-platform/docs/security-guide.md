# Aegis Platform - Security Guide

## 🛡️ Comprehensive Security Configuration Guide

This guide provides detailed security configuration and hardening instructions for the Aegis Risk Management Platform, covering authentication, authorization, data protection, and compliance requirements.

## 📋 Table of Contents

- [Security Architecture](#security-architecture)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [Application Security](#application-security)
- [Infrastructure Security](#infrastructure-security)
- [Compliance Requirements](#compliance-requirements)
- [Security Monitoring](#security-monitoring)
- [Incident Response](#incident-response)
- [Security Testing](#security-testing)

## 🏗️ Security Architecture

### Security by Design Principles

The Aegis Platform implements security-by-design with multiple layers of protection:

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
├─────────────────────────────────────────────────────────┤
│           Authentication & Authorization Layer          │
├─────────────────────────────────────────────────────────┤
│              API Gateway & Rate Limiting                │
├─────────────────────────────────────────────────────────┤
│              Application Logic & Validation             │
├─────────────────────────────────────────────────────────┤
│                Data Access Layer (ORM)                  │
├─────────────────────────────────────────────────────────┤
│              Database Encryption & Access               │
├─────────────────────────────────────────────────────────┤
│              Infrastructure & Network Security          │
└─────────────────────────────────────────────────────────┘
```

### Security Domains

1. **Identity & Access Management (IAM)**
2. **Data Protection & Privacy**
3. **Network & Infrastructure Security**
4. **Application Security**
5. **Audit & Compliance**
6. **Incident Response & Recovery**

## 🔐 Authentication & Authorization

### 1. Multi-Factor Authentication (MFA)

#### TOTP Implementation
```python
# MFA configuration in auth.py
from pyotp import TOTP
import qrcode
from io import BytesIO
import base64

class MFAManager:
    def __init__(self):
        self.issuer_name = "Aegis Platform"
    
    def generate_secret(self, user_email: str) -> str:
        """Generate TOTP secret for user"""
        secret = pyotp.random_base32()
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = TOTP(secret)
        return totp.verify(token, valid_window=1)

# Integration with authentication
async def login_with_mfa(username: str, password: str, mfa_token: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    if user.mfa_enabled:
        mfa_manager = MFAManager()
        if not mfa_manager.verify_token(user.mfa_secret, mfa_token):
            raise HTTPException(401, "Invalid MFA token")
    
    return generate_tokens(user)
```

#### MFA Enforcement Policy
```python
# MFA policy configuration
MFA_POLICY = {
    "enforce_for_roles": ["admin", "super_admin"],
    "grace_period_days": 30,
    "backup_codes_count": 10,
    "remember_device_days": 30
}

def enforce_mfa_policy(user: User) -> bool:
    """Check if MFA is required for user"""
    if user.role in MFA_POLICY["enforce_for_roles"]:
        return True
    
    if user.last_mfa_setup is None:
        grace_period = timedelta(days=MFA_POLICY["grace_period_days"])
        if datetime.utcnow() - user.created_at > grace_period:
            return True
    
    return False
```

### 2. Role-Based Access Control (RBAC)

#### Permission System
```python
# permissions.py
from enum import Enum
from typing import List, Dict, Set

class Permission(Enum):
    # User management
    USERS_CREATE = "users:create"
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    
    # Risk management
    RISKS_CREATE = "risks:create"
    RISKS_READ = "risks:read"
    RISKS_UPDATE = "risks:update"
    RISKS_DELETE = "risks:delete"
    RISKS_APPROVE = "risks:approve"
    
    # Assessment management
    ASSESSMENTS_CREATE = "assessments:create"
    ASSESSMENTS_READ = "assessments:read"
    ASSESSMENTS_UPDATE = "assessments:update"
    ASSESSMENTS_DELETE = "assessments:delete"
    ASSESSMENTS_APPROVE = "assessments:approve"
    
    # System administration
    SYSTEM_CONFIG = "system:configure"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_LOGS = "system:logs"
    
    # Reporting
    REPORTS_CREATE = "reports:create"
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"
    REPORTS_SCHEDULE = "reports:schedule"

# Role definitions
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    "super_admin": {
        # All permissions
        Permission.USERS_CREATE, Permission.USERS_READ, 
        Permission.USERS_UPDATE, Permission.USERS_DELETE,
        Permission.RISKS_CREATE, Permission.RISKS_READ,
        Permission.RISKS_UPDATE, Permission.RISKS_DELETE, Permission.RISKS_APPROVE,
        Permission.ASSESSMENTS_CREATE, Permission.ASSESSMENTS_READ,
        Permission.ASSESSMENTS_UPDATE, Permission.ASSESSMENTS_DELETE, Permission.ASSESSMENTS_APPROVE,
        Permission.SYSTEM_CONFIG, Permission.SYSTEM_BACKUP, Permission.SYSTEM_LOGS,
        Permission.REPORTS_CREATE, Permission.REPORTS_READ,
        Permission.REPORTS_EXPORT, Permission.REPORTS_SCHEDULE
    },
    "admin": {
        Permission.USERS_CREATE, Permission.USERS_READ, Permission.USERS_UPDATE,
        Permission.RISKS_CREATE, Permission.RISKS_READ, Permission.RISKS_UPDATE, Permission.RISKS_APPROVE,
        Permission.ASSESSMENTS_CREATE, Permission.ASSESSMENTS_READ,
        Permission.ASSESSMENTS_UPDATE, Permission.ASSESSMENTS_APPROVE,
        Permission.REPORTS_CREATE, Permission.REPORTS_READ, Permission.REPORTS_EXPORT
    },
    "manager": {
        Permission.RISKS_CREATE, Permission.RISKS_READ, Permission.RISKS_UPDATE,
        Permission.ASSESSMENTS_CREATE, Permission.ASSESSMENTS_READ, Permission.ASSESSMENTS_UPDATE,
        Permission.REPORTS_CREATE, Permission.REPORTS_READ, Permission.REPORTS_EXPORT
    },
    "analyst": {
        Permission.RISKS_READ, Permission.RISKS_UPDATE,
        Permission.ASSESSMENTS_READ, Permission.ASSESSMENTS_UPDATE,
        Permission.REPORTS_READ
    },
    "viewer": {
        Permission.RISKS_READ,
        Permission.ASSESSMENTS_READ,
        Permission.REPORTS_READ
    }
}

def has_permission(user: User, permission: Permission) -> bool:
    """Check if user has specific permission"""
    user_permissions = ROLE_PERMISSIONS.get(user.role, set())
    return permission in user_permissions

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission required: {permission.value}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. JWT Security Configuration

#### Enhanced JWT Implementation
```python
# jwt_manager.py
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=30)
        self.refresh_token_expire = timedelta(days=7)
        self.issuer = "aegis-platform"
        self.audience = "aegis-users"
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token with enhanced claims"""
        now = datetime.utcnow()
        payload = {
            "sub": str(user_data["user_id"]),
            "username": user_data["username"],
            "role": user_data["role"],
            "permissions": user_data.get("permissions", []),
            "iat": now,
            "exp": now + self.access_token_expire,
            "iss": self.issuer,
            "aud": self.audience,
            "jti": secrets.token_urlsafe(16),  # JWT ID for revocation
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.refresh_token_expire,
            "iss": self.issuer,
            "aud": self.audience,
            "jti": secrets.token_urlsafe(16),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience
            )
            
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")
            
            # Check if token is revoked
            if self.is_token_revoked(payload.get("jti")):
                raise jwt.InvalidTokenError("Token has been revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(401, f"Invalid token: {str(e)}")
    
    def is_token_revoked(self, jti: str) -> bool:
        """Check if token is in revocation list (implement with Redis)"""
        # Implementation depends on your caching solution
        return False
    
    def revoke_token(self, jti: str, exp: datetime):
        """Add token to revocation list"""
        # Store in Redis with expiration
        pass
```

## 🔒 Data Protection

### 1. Encryption at Rest

#### Database Encryption
```sql
-- PostgreSQL encryption setup
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create encrypted columns
ALTER TABLE users ADD COLUMN encrypted_data bytea;

-- Encrypt sensitive data
UPDATE users SET encrypted_data = pgp_sym_encrypt(sensitive_field, 'encryption_key');

-- Decrypt data
SELECT pgp_sym_decrypt(encrypted_data, 'encryption_key') FROM users;
```

#### File System Encryption
```python
# file_encryption.py
from cryptography.fernet import Fernet
import os
import base64

class FileEncryption:
    def __init__(self, key: bytes = None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher_suite = Fernet(key)
        self.key = key
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """Encrypt file and return encrypted file path"""
        if output_path is None:
            output_path = f"{file_path}.encrypted"
        
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = self.cipher_suite.encrypt(file_data)
        
        with open(output_path, 'wb') as file:
            file.write(encrypted_data)
        
        return output_path
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> str:
        """Decrypt file and return decrypted file path"""
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)
        
        return output_path
    
    def get_key_string(self) -> str:
        """Get base64 encoded key for storage"""
        return base64.b64encode(self.key).decode()

# Usage in file upload handler
@router.post("/evidence/upload")
async def upload_evidence(
    file: UploadFile,
    encrypt: bool = True,
    current_user: User = Depends(get_current_user)
):
    file_path = f"/secure/uploads/{file.filename}"
    
    # Save original file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    if encrypt:
        encryption = FileEncryption()
        encrypted_path = encryption.encrypt_file(file_path)
        
        # Store encryption key securely
        store_encryption_key(file.filename, encryption.get_key_string())
        
        # Remove original file
        os.remove(file_path)
        file_path = encrypted_path
    
    return {"message": "File uploaded successfully", "path": file_path}
```

### 2. Data Loss Prevention (DLP)

#### Sensitive Data Detection
```python
# dlp.py
import re
from typing import List, Dict, Any
from enum import Enum

class SensitiveDataType(Enum):
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    EMAIL = "email"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"

class DLPScanner:
    def __init__(self):
        self.patterns = {
            SensitiveDataType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
            SensitiveDataType.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            SensitiveDataType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            SensitiveDataType.PHONE: r'\b\d{3}-\d{3}-\d{4}\b',
            SensitiveDataType.IP_ADDRESS: r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            SensitiveDataType.API_KEY: r'\b[A-Za-z0-9]{32,}\b'
        }
    
    def scan_text(self, text: str) -> Dict[SensitiveDataType, List[str]]:
        """Scan text for sensitive data patterns"""
        findings = {}
        
        for data_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[data_type] = matches
        
        return findings
    
    def mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text"""
        masked_text = text
        
        for data_type, pattern in self.patterns.items():
            if data_type == SensitiveDataType.EMAIL:
                masked_text = re.sub(pattern, 'EMAIL_REDACTED', masked_text)
            elif data_type == SensitiveDataType.SSN:
                masked_text = re.sub(pattern, 'XXX-XX-XXXX', masked_text)
            elif data_type == SensitiveDataType.CREDIT_CARD:
                masked_text = re.sub(pattern, 'XXXX-XXXX-XXXX-XXXX', masked_text)
            else:
                masked_text = re.sub(pattern, '[REDACTED]', masked_text)
        
        return masked_text

# Integration with file upload
async def scan_uploaded_file(file_path: str) -> Dict[str, Any]:
    """Scan uploaded file for sensitive data"""
    scanner = DLPScanner()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        findings = scanner.scan_text(content)
        
        if findings:
            # Log security event
            log_security_event(
                "SENSITIVE_DATA_DETECTED",
                {"file": file_path, "findings": findings}
            )
            
            # Quarantine file if high-risk data found
            high_risk_types = [SensitiveDataType.SSN, SensitiveDataType.CREDIT_CARD]
            if any(data_type in findings for data_type in high_risk_types):
                quarantine_file(file_path)
        
        return {"sensitive_data_found": bool(findings), "findings": findings}
        
    except UnicodeDecodeError:
        # Handle binary files
        return {"sensitive_data_found": False, "error": "Binary file - cannot scan"}
```

### 3. Data Retention and Purging

#### Automated Data Lifecycle Management
```python
# data_lifecycle.py
from datetime import datetime, timedelta
from typing import List
import asyncio

class DataRetentionPolicy:
    def __init__(self):
        self.policies = {
            "audit_logs": timedelta(days=2555),  # 7 years
            "user_sessions": timedelta(days=30),
            "temporary_files": timedelta(days=7),
            "assessment_drafts": timedelta(days=90),
            "system_logs": timedelta(days=365),
            "backup_files": timedelta(days=90)
        }
    
    async def apply_retention_policies(self):
        """Apply all retention policies"""
        for data_type, retention_period in self.policies.items():
            cutoff_date = datetime.utcnow() - retention_period
            await self.purge_data(data_type, cutoff_date)
    
    async def purge_data(self, data_type: str, cutoff_date: datetime):
        """Purge data older than cutoff date"""
        if data_type == "audit_logs":
            await self.purge_audit_logs(cutoff_date)
        elif data_type == "user_sessions":
            await self.purge_user_sessions(cutoff_date)
        elif data_type == "temporary_files":
            await self.purge_temporary_files(cutoff_date)
        # Add more data types as needed
    
    async def purge_audit_logs(self, cutoff_date: datetime):
        """Purge old audit logs with archival"""
        # Archive before purging
        old_logs = db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).all()
        
        if old_logs:
            # Export to archive storage
            await self.archive_logs(old_logs)
            
            # Delete from active database
            db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).delete()
            
            db.commit()
            
            log_security_event(
                "DATA_PURGED",
                {"type": "audit_logs", "count": len(old_logs), "cutoff": cutoff_date.isoformat()}
            )

# Scheduled task for data lifecycle management
from celery import Celery

app = Celery('data_lifecycle')

@app.task
def run_data_retention():
    """Scheduled task to run data retention policies"""
    policy = DataRetentionPolicy()
    asyncio.run(policy.apply_retention_policies())
```

## 🌐 Network Security

### 1. Network Segmentation

#### Security Groups Configuration (AWS)
```yaml
# security-groups.yaml
SecurityGroupWeb:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Web tier security group
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0
        Description: HTTPS from internet
      - IpProtocol: tcp
        FromPort: 80
        ToPort: 80
        CidrIp: 0.0.0.0/0
        Description: HTTP redirect to HTTPS
    SecurityGroupEgress:
      - IpProtocol: tcp
        FromPort: 8000
        ToPort: 8000
        DestinationSecurityGroupId: !Ref SecurityGroupApp
        Description: To application tier

SecurityGroupApp:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Application tier security group
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 8000
        ToPort: 8000
        SourceSecurityGroupId: !Ref SecurityGroupWeb
        Description: From web tier
    SecurityGroupEgress:
      - IpProtocol: tcp
        FromPort: 5432
        ToPort: 5432
        DestinationSecurityGroupId: !Ref SecurityGroupDB
        Description: To database tier

SecurityGroupDB:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Database tier security group
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 5432
        ToPort: 5432
        SourceSecurityGroupId: !Ref SecurityGroupApp
        Description: From application tier
```

### 2. Web Application Firewall (WAF)

#### WAF Rules Configuration
```yaml
# waf-config.yaml
WebACL:
  Type: AWS::WAFv2::WebACL
  Properties:
    Name: AegisWebACL
    Scope: REGIONAL
    DefaultAction:
      Allow: {}
    Rules:
      - Name: AWSManagedRulesCommonRuleSet
        Priority: 1
        OverrideAction:
          None: {}
        Statement:
          ManagedRuleGroupStatement:
            VendorName: AWS
            Name: AWSManagedRulesCommonRuleSet
        VisibilityConfig:
          SampledRequestsEnabled: true
          CloudWatchMetricsEnabled: true
          MetricName: CommonRuleSetMetric
      
      - Name: RateLimitRule
        Priority: 2
        Action:
          Block: {}
        Statement:
          RateBasedStatement:
            Limit: 2000
            AggregateKeyType: IP
        VisibilityConfig:
          SampledRequestsEnabled: true
          CloudWatchMetricsEnabled: true
          MetricName: RateLimitMetric
      
      - Name: SQLInjectionRule
        Priority: 3
        OverrideAction:
          None: {}
        Statement:
          ManagedRuleGroupStatement:
            VendorName: AWS
            Name: AWSManagedRulesSQLiRuleSet
        VisibilityConfig:
          SampledRequestsEnabled: true
          CloudWatchMetricsEnabled: true
          MetricName: SQLInjectionMetric
```

### 3. API Rate Limiting

#### Advanced Rate Limiting
```python
# rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from datetime import datetime, timedelta

class AdvancedRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.limits = {
            "login": {"requests": 5, "window": 300},  # 5 attempts per 5 minutes
            "api_general": {"requests": 100, "window": 60},  # 100 requests per minute
            "api_upload": {"requests": 10, "window": 60},  # 10 uploads per minute
            "api_export": {"requests": 5, "window": 300},  # 5 exports per 5 minutes
        }
    
    def is_rate_limited(self, key: str, limit_type: str, identifier: str) -> bool:
        """Check if request should be rate limited"""
        limit_config = self.limits.get(limit_type)
        if not limit_config:
            return False
        
        redis_key = f"rate_limit:{limit_type}:{identifier}"
        current_count = self.redis.get(redis_key)
        
        if current_count is None:
            # First request in window
            self.redis.setex(redis_key, limit_config["window"], 1)
            return False
        
        if int(current_count) >= limit_config["requests"]:
            return True
        
        # Increment counter
        self.redis.incr(redis_key)
        return False
    
    def get_reset_time(self, limit_type: str, identifier: str) -> datetime:
        """Get when rate limit resets"""
        redis_key = f"rate_limit:{limit_type}:{identifier}"
        ttl = self.redis.ttl(redis_key)
        
        if ttl > 0:
            return datetime.utcnow() + timedelta(seconds=ttl)
        
        return datetime.utcnow()

# Custom rate limiting decorator
def rate_limit(limit_type: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            rate_limiter = AdvancedRateLimiter(redis_client)
            
            # Use API key if available, otherwise IP address
            identifier = request.headers.get("X-API-Key", get_remote_address(request))
            
            if rate_limiter.is_rate_limited("rate_limit", limit_type, identifier):
                reset_time = rate_limiter.get_reset_time(limit_type, identifier)
                
                # Log rate limit violation
                log_security_event(
                    "RATE_LIMIT_EXCEEDED",
                    {
                        "identifier": identifier,
                        "limit_type": limit_type,
                        "reset_time": reset_time.isoformat()
                    }
                )
                
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again at {reset_time.isoformat()}",
                    headers={"Retry-After": str(int((reset_time - datetime.utcnow()).total_seconds()))}
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/auth/login")
@rate_limit("login")
async def login(request: Request, user_data: UserLogin):
    # Login logic here
    pass
```

## 🔍 Security Monitoring

### 1. Security Event Logging

#### Comprehensive Security Logger
```python
# security_logger.py
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class SecurityEventType(Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    MFA_ENABLED = "MFA_ENABLED"
    MFA_DISABLED = "MFA_DISABLED"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DATA_EXPORT = "DATA_EXPORT"
    DATA_IMPORT = "DATA_IMPORT"
    CONFIGURATION_CHANGED = "CONFIGURATION_CHANGED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        # Create handler for security logs
        handler = logging.FileHandler("/var/log/aegis/security.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        risk_level: str = "medium"
    ):
        """Log security event with structured data"""
        event_data = {
            "event_type": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "risk_level": risk_level,
            "details": details or {}
        }
        
        # Add to database for querying
        security_event = SecurityEvent(**event_data)
        db.add(security_event)
        db.commit()
        
        # Log to file
        self.logger.info(json.dumps(event_data))
        
        # Send alert for high-risk events
        if risk_level == "high":
            self.send_security_alert(event_data)
    
    def send_security_alert(self, event_data: Dict[str, Any]):
        """Send immediate alert for high-risk security events"""
        # Implementation depends on alerting system (email, Slack, PagerDuty, etc.)
        pass

# Usage throughout the application
security_logger = SecurityLogger()

def log_security_event(event_type: str, details: Dict[str, Any], request: Request = None):
    """Helper function to log security events"""
    security_logger.log_event(
        SecurityEventType(event_type),
        user_id=getattr(request.state, 'current_user_id', None),
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("User-Agent") if request else None,
        details=details
    )
```

### 2. Anomaly Detection

#### Behavioral Analysis
```python
# anomaly_detection.py
from typing import List, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.baseline_period_days = 30
    
    def train_user_behavior_model(self, user_id: str):
        """Train anomaly detection model for user behavior"""
        # Get user's historical behavior
        features = self.extract_user_features(user_id)
        
        if len(features) < 10:  # Need minimum data
            return False
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Train isolation forest
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(scaled_features)
        
        # Store model and scaler
        self.models[user_id] = model
        self.scalers[user_id] = scaler
        
        return True
    
    def extract_user_features(self, user_id: str) -> List[List[float]]:
        """Extract behavioral features for user"""
        # Get user activity from last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=self.baseline_period_days)
        
        activities = db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id,
            SecurityEvent.timestamp >= cutoff_date
        ).all()
        
        features = []
        
        # Group by day and extract features
        daily_activities = {}
        for activity in activities:
            day = activity.timestamp.date()
            if day not in daily_activities:
                daily_activities[day] = []
            daily_activities[day].append(activity)
        
        for day, day_activities in daily_activities.items():
            feature_vector = [
                len(day_activities),  # Number of activities
                len(set(a.ip_address for a in day_activities)),  # Unique IP addresses
                len(set(a.event_type for a in day_activities)),  # Event type diversity
                self.extract_time_features(day_activities),  # Time-based features
                self.extract_location_features(day_activities)  # Location-based features
            ]
            features.append(feature_vector)
        
        return features
    
    def detect_anomaly(self, user_id: str, current_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if current activity is anomalous"""
        if user_id not in self.models:
            # Train model if not exists
            if not self.train_user_behavior_model(user_id):
                return {"anomaly_detected": False, "reason": "insufficient_data"}
        
        model = self.models[user_id]
        scaler = self.scalers[user_id]
        
        # Extract features for current activity
        current_features = self.extract_current_features(current_activity)
        scaled_features = scaler.transform([current_features])
        
        # Predict anomaly
        anomaly_score = model.decision_function(scaled_features)[0]
        is_anomaly = model.predict(scaled_features)[0] == -1
        
        result = {
            "anomaly_detected": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "risk_level": self.calculate_risk_level(anomaly_score)
        }
        
        if is_anomaly:
            result["recommendations"] = self.get_anomaly_recommendations(current_activity)
        
        return result
    
    def calculate_risk_level(self, anomaly_score: float) -> str:
        """Calculate risk level based on anomaly score"""
        if anomaly_score < -0.5:
            return "high"
        elif anomaly_score < -0.2:
            return "medium"
        else:
            return "low"

# Integration with authentication
async def check_login_anomaly(user_id: str, login_details: Dict[str, Any]):
    """Check for login anomalies"""
    detector = AnomalyDetector()
    anomaly_result = detector.detect_anomaly(user_id, login_details)
    
    if anomaly_result["anomaly_detected"]:
        # Log security event
        log_security_event(
            "ANOMALOUS_LOGIN",
            {
                "anomaly_score": anomaly_result["anomaly_score"],
                "risk_level": anomaly_result["risk_level"],
                "login_details": login_details
            }
        )
        
        # Take action based on risk level
        if anomaly_result["risk_level"] == "high":
            # Require additional verification
            return {"require_additional_auth": True, "reason": "anomalous_behavior"}
    
    return {"require_additional_auth": False}
```

## 🚨 Incident Response

### 1. Automated Response System

#### Incident Response Automation
```python
# incident_response.py
from enum import Enum
from typing import Dict, Any, List
import asyncio

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(Enum):
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    SYSTEM_COMPROMISE = "system_compromise"
    MALWARE_DETECTED = "malware_detected"
    DDOS_ATTACK = "ddos_attack"
    INSIDER_THREAT = "insider_threat"

class IncidentResponseSystem:
    def __init__(self):
        self.response_playbooks = {
            IncidentType.UNAUTHORIZED_ACCESS: self.handle_unauthorized_access,
            IncidentType.DATA_BREACH: self.handle_data_breach,
            IncidentType.SYSTEM_COMPROMISE: self.handle_system_compromise,
            IncidentType.MALWARE_DETECTED: self.handle_malware_detection,
            IncidentType.DDOS_ATTACK: self.handle_ddos_attack,
            IncidentType.INSIDER_THREAT: self.handle_insider_threat
        }
    
    async def trigger_incident_response(
        self,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        details: Dict[str, Any]
    ) -> str:
        """Trigger automated incident response"""
        incident_id = self.create_incident(incident_type, severity, details)
        
        # Execute response playbook
        if incident_type in self.response_playbooks:
            await self.response_playbooks[incident_type](incident_id, severity, details)
        
        # Notify security team
        await self.notify_security_team(incident_id, incident_type, severity, details)
        
        return incident_id
    
    async def handle_unauthorized_access(
        self,
        incident_id: str,
        severity: IncidentSeverity,
        details: Dict[str, Any]
    ):
        """Handle unauthorized access incident"""
        user_id = details.get("user_id")
        ip_address = details.get("ip_address")
        
        # Immediate actions
        if severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            if user_id:
                await self.disable_user_account(user_id)
            
            if ip_address:
                await self.block_ip_address(ip_address)
        
        # Force password reset for affected user
        if user_id:
            await self.force_password_reset(user_id)
        
        # Audit user's recent activities
        await self.audit_user_activities(user_id, days=7)
        
        # Update incident log
        self.update_incident(incident_id, "Automated response completed")
    
    async def handle_data_breach(
        self,
        incident_id: str,
        severity: IncidentSeverity,
        details: Dict[str, Any]
    ):
        """Handle data breach incident"""
        affected_data = details.get("affected_data", [])
        
        # Immediate containment
        await self.isolate_affected_systems(details.get("systems", []))
        
        # Data protection measures
        for data_source in affected_data:
            await self.encrypt_data_source(data_source)
            await self.backup_affected_data(data_source)
        
        # Compliance notifications
        if severity == IncidentSeverity.CRITICAL:
            await self.trigger_compliance_notifications(incident_id, details)
        
        # Forensic preservation
        await self.preserve_forensic_evidence(incident_id, details)
    
    async def disable_user_account(self, user_id: str):
        """Disable user account immediately"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            user.account_locked = True
            user.locked_at = datetime.utcnow()
            user.locked_reason = "Security incident - automated lockout"
            db.commit()
            
            # Revoke all active sessions
            await self.revoke_user_sessions(user_id)
    
    async def block_ip_address(self, ip_address: str):
        """Block IP address at firewall level"""
        # Implementation depends on firewall system
        # Could integrate with AWS WAF, CloudFlare, etc.
        pass
    
    async def notify_security_team(
        self,
        incident_id: str,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        details: Dict[str, Any]
    ):
        """Notify security team of incident"""
        notification = {
            "incident_id": incident_id,
            "type": incident_type.value,
            "severity": severity.value,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        # Send to multiple channels based on severity
        if severity == IncidentSeverity.CRITICAL:
            await self.send_pager_alert(notification)
            await self.send_email_alert(notification)
            await self.send_slack_alert(notification)
        elif severity == IncidentSeverity.HIGH:
            await self.send_email_alert(notification)
            await self.send_slack_alert(notification)
        else:
            await self.send_slack_alert(notification)

# Integration with security monitoring
async def security_event_handler(event: SecurityEvent):
    """Handle security events and trigger incident response if needed"""
    incident_response = IncidentResponseSystem()
    
    # Analyze event for incident triggers
    if event.event_type == "MULTIPLE_FAILED_LOGINS":
        if event.details.get("attempt_count", 0) > 10:
            await incident_response.trigger_incident_response(
                IncidentType.UNAUTHORIZED_ACCESS,
                IncidentSeverity.HIGH,
                event.details
            )
    
    elif event.event_type == "SUSPICIOUS_DATA_ACCESS":
        await incident_response.trigger_incident_response(
            IncidentType.INSIDER_THREAT,
            IncidentSeverity.MEDIUM,
            event.details
        )
```

This comprehensive security guide provides detailed implementation guidance for securing the Aegis Risk Management Platform. Continue implementing these security measures progressively, starting with the highest priority items for your deployment environment.