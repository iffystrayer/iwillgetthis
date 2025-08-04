# Aegis Platform - Administrator Guide

## 🔧 System Administration Guide

This guide provides comprehensive information for system administrators managing the Aegis Risk Management Platform.

## 📋 Table of Contents

- [Initial Setup](#initial-setup)
- [User Management](#user-management)
- [System Configuration](#system-configuration)
- [Database Management](#database-management)
- [Security Configuration](#security-configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

## 🚀 Initial Setup

### 1. System Requirements

**Minimum Requirements:**
- CPU: 4 cores, 2.5GHz
- RAM: 8GB
- Storage: 100GB SSD
- Network: 1Gbps
- OS: Ubuntu 20.04 LTS or Docker-compatible

**Recommended for Production:**
- CPU: 8 cores, 3.0GHz
- RAM: 16GB
- Storage: 500GB SSD with RAID
- Network: 10Gbps
- Load balancer and redundancy

### 2. Installation

#### Docker Deployment (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd aegis-platform

# Copy and configure environment
cp .env.example .env
nano .env  # Configure your settings

# Start services
docker-compose up -d

# Verify installation
curl http://localhost:8000/health
```

#### Manual Installation
```bash
# Install dependencies
sudo apt update
sudo apt install python3.9 python3-pip postgresql-12

# Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure database
sudo -u postgres createdb aegis_db
sudo -u postgres createuser aegis_user

# Start application
python main.py
```

### 3. Initial Configuration

#### Environment Variables
Create and configure `.env` file:

```bash
# Application Settings
APP_NAME="Aegis Risk Management Platform"
APP_VERSION="1.0.0"
DEBUG=false
LOG_LEVEL="INFO"

# Database Configuration
DATABASE_URL="postgresql://user:password@localhost/aegis_db"

# Security Settings
SECRET_KEY="your-super-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Service Configuration (Optional)
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"

# External Integrations
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# File Storage
UPLOAD_DIRECTORY="/opt/aegis/uploads"
MAX_FILE_SIZE=10485760  # 10MB

# Email Configuration
SMTP_HOST="smtp.yourdomain.com"
SMTP_PORT=587
SMTP_USERNAME="noreply@yourdomain.com"
SMTP_PASSWORD="your-smtp-password"
```

## 👥 User Management

### 1. Creating Admin Users

#### First Admin User
```bash
# Using Python script
cd backend
python -c "
from models.user import User
from database import SessionLocal
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

admin_user = User(
    username='admin',
    email='admin@yourdomain.com',
    full_name='System Administrator',
    hashed_password=pwd_context.hash('ChangeMe123!'),
    is_active=True,
    is_superuser=True,
    role='admin'
)

db.add(admin_user)
db.commit()
print('Admin user created successfully')
"
```

#### Via API
```bash
# Create admin user via API
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@company.com",
    "full_name": "System Administrator",
    "password": "SecurePassword123!",
    "role": "admin",
    "is_active": true
  }'
```

### 2. User Roles and Permissions

#### Role Hierarchy
1. **Super Admin**: Full system access
2. **Admin**: User and system management
3. **Manager**: Department-level access
4. **Analyst**: Risk and compliance analysis
5. **Viewer**: Read-only access

#### Permission Management
```python
# Role-based permissions
ROLE_PERMISSIONS = {
    "super_admin": ["*"],  # All permissions
    "admin": [
        "users:create", "users:read", "users:update", "users:delete",
        "systems:configure", "reports:manage"
    ],
    "manager": [
        "risks:create", "risks:read", "risks:update",
        "assessments:create", "assessments:read", "assessments:update",
        "reports:create", "reports:read"
    ],
    "analyst": [
        "risks:read", "risks:update",
        "assessments:read", "assessments:update",
        "reports:read", "evidence:upload"
    ],
    "viewer": [
        "risks:read", "assessments:read", "reports:read"
    ]
}
```

### 3. User Lifecycle Management

#### Bulk User Import
```bash
# CSV format: username,email,full_name,role,department
# Example: john.doe,john@company.com,John Doe,analyst,IT

python scripts/import_users.py users.csv
```

#### User Deactivation
```bash
# Deactivate user (preserves data)
curl -X PUT "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

## ⚙️ System Configuration

### 1. Application Settings

#### Core Configuration
```python
# config.py settings
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Aegis Risk Management Platform"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # Features
    ENABLE_AI_FEATURES: bool = True
    ENABLE_EXTERNAL_INTEGRATIONS: bool = True
    ENABLE_FILE_UPLOADS: bool = True
    
    # Limits
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_USERS: int = 1000
    RATE_LIMIT_PER_MINUTE: int = 100
```

### 2. Framework Configuration

#### Adding Compliance Frameworks
```bash
# Import NIST CSF framework
curl -X POST "http://localhost:8000/api/v1/frameworks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NIST Cybersecurity Framework",
    "version": "1.1",
    "description": "NIST CSF v1.1 Implementation",
    "framework_type": "cybersecurity",
    "is_active": true
  }'
```

#### Custom Framework Creation
```json
{
  "name": "Custom Security Framework",
  "version": "1.0",
  "description": "Organization-specific security controls",
  "framework_type": "custom",
  "categories": [
    {
      "name": "Access Control",
      "controls": [
        {
          "control_id": "AC-01",
          "title": "Access Control Policy",
          "description": "Develop and maintain access control policies",
          "priority": "high"
        }
      ]
    }
  ]
}
```

### 3. Integration Configuration

#### OpenVAS Integration
```bash
# Configure OpenVAS scanner
export OPENVAS_HOST="scanner.company.com"
export OPENVAS_USERNAME="aegis_user"
export OPENVAS_PASSWORD="scanner_password"

# Test connection
curl -X POST "http://localhost:8000/api/v1/integrations/openvas/test"
```

#### SIEM Integration
```python
# Configure SIEM integration
SIEM_CONFIG = {
    "splunk": {
        "host": "splunk.company.com",
        "port": 8089,
        "username": "aegis_user",
        "password": "secure_password",
        "index": "aegis"
    }
}
```

## 🗄️ Database Management

### 1. Database Maintenance

#### Backup Procedures
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U aegis_user aegis_db > /backups/aegis_backup_$DATE.sql

# Compress and retain for 30 days
gzip /backups/aegis_backup_$DATE.sql
find /backups -name "aegis_backup_*.sql.gz" -mtime +30 -delete
```

#### Database Optimization
```sql
-- Analyze database statistics
ANALYZE;

-- Reindex for performance
REINDEX DATABASE aegis_db;

-- Vacuum to reclaim space
VACUUM (ANALYZE, VERBOSE);

-- Check database size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2. Data Retention Policies

#### Automated Cleanup
```python
# Cleanup script - data_cleanup.py
from datetime import datetime, timedelta
from models import Risk, Assessment, AnalyticsJob

def cleanup_old_data():
    cutoff_date = datetime.utcnow() - timedelta(days=2555)  # 7 years
    
    # Archive old assessments
    old_assessments = db.query(Assessment).filter(
        Assessment.created_at < cutoff_date
    ).all()
    
    # Move to archive table or delete
    for assessment in old_assessments:
        archive_assessment(assessment)
        db.delete(assessment)
    
    db.commit()
```

### 3. Performance Monitoring

#### Database Metrics
```sql
-- Monitor query performance
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 20;

-- Monitor table sizes and bloat
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables
ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC;
```

## 🔒 Security Configuration

### 1. Authentication Security

#### JWT Configuration
```python
# Enhanced security settings
JWT_SETTINGS = {
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "REFRESH_TOKEN_EXPIRE_DAYS": 7,
    "ISSUER": "aegis-platform",
    "AUDIENCE": "aegis-users"
}

# Token validation
def validate_token_security(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_SETTINGS["ALGORITHM"]])
        return payload.get("iss") == JWT_SETTINGS["ISSUER"]
    except jwt.InvalidTokenError:
        return False
```

#### Password Policies
```python
PASSWORD_POLICY = {
    "min_length": 12,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_special_chars": True,
    "max_age_days": 90,
    "history_count": 12,  # Remember last 12 passwords
    "lockout_attempts": 5,
    "lockout_duration_minutes": 30
}
```

### 2. API Security

#### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/api/v1/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request):
    pass
```

#### CORS Configuration
```python
CORS_SETTINGS = {
    "allow_origins": ["https://yourdomain.com"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["Authorization", "Content-Type"],
    "max_age": 3600
}
```

### 3. Audit Logging

#### Security Event Logging
```python
import logging

security_logger = logging.getLogger("security")

def log_security_event(event_type: str, user_id: str, details: dict):
    security_logger.info({
        "event_type": event_type,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": request.client.host,
        "user_agent": request.headers.get("User-Agent"),
        "details": details
    })

# Usage examples
log_security_event("LOGIN_SUCCESS", user.id, {"method": "password"})
log_security_event("LOGIN_FAILED", None, {"username": username, "reason": "invalid_password"})
log_security_event("PRIVILEGE_ESCALATION", user.id, {"from_role": "user", "to_role": "admin"})
```

## 📊 Monitoring & Maintenance

### 1. Health Monitoring

#### System Health Checks
```python
# Custom health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # AI service check
    try:
        ai_status = await enhanced_ai_service.health_check()
        health_status["checks"]["ai_services"] = ai_status
    except Exception as e:
        health_status["checks"]["ai_services"] = {"status": "unhealthy", "error": str(e)}
    
    return health_status
```

#### Metrics Collection
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_users = Gauge('active_users_total', 'Number of active users')
database_connections = Gauge('database_connections_active', 'Active database connections')
```

### 2. Performance Optimization

#### Caching Strategy
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Initialize Redis cache
FastAPICache.init(RedisBackend("redis://localhost:6379"))

# Cache expensive operations
@cache(expire=300)  # 5 minutes
async def get_risk_summary():
    return await calculate_risk_metrics()

# Cache dashboard data
@cache(expire=60)  # 1 minute
async def get_dashboard_data(dashboard_id: str):
    return await generate_dashboard_data(dashboard_id)
```

#### Database Query Optimization
```python
# Use database indexes
CREATE INDEX CONCURRENTLY idx_risks_created_at ON risks(created_at);
CREATE INDEX CONCURRENTLY idx_assets_criticality ON assets(criticality);
CREATE INDEX CONCURRENTLY idx_users_active ON users(is_active) WHERE is_active = true;

# Optimize queries with proper joins
query = db.query(Risk).options(
    joinedload(Risk.asset),
    joinedload(Risk.assigned_user)
).filter(Risk.is_active == True)
```

### 3. Log Management

#### Structured Logging
```python
import structlog

logger = structlog.get_logger()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Usage
logger.info("User login", user_id=user.id, ip_address=request.client.host)
logger.error("Database connection failed", error=str(e), retry_count=3)
```

## 💾 Backup & Recovery

### 1. Backup Strategy

#### Automated Backup Script
```bash
#!/bin/bash
# backup_aegis.sh

BACKUP_DIR="/opt/aegis/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "Starting database backup..."
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# File uploads backup
echo "Backing up uploaded files..."
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz $UPLOAD_DIRECTORY

# Configuration backup
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz /opt/aegis/config

# Cleanup old backups
find $BACKUP_DIR -name "*backup_*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_DIR"
```

#### Backup Verification
```bash
#!/bin/bash
# verify_backup.sh

BACKUP_FILE=$1

# Verify database backup
if [[ $BACKUP_FILE == *"db_backup"* ]]; then
    echo "Verifying database backup..."
    gunzip -t $BACKUP_FILE
    if [ $? -eq 0 ]; then
        echo "✓ Database backup is valid"
    else
        echo "✗ Database backup is corrupted"
        exit 1
    fi
fi

# Verify file backup
if [[ $BACKUP_FILE == *"files_backup"* ]]; then
    echo "Verifying files backup..."
    tar -tzf $BACKUP_FILE > /dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Files backup is valid"
    else
        echo "✗ Files backup is corrupted"
        exit 1
    fi
fi
```

### 2. Disaster Recovery

#### Recovery Procedures
```bash
#!/bin/bash
# disaster_recovery.sh

BACKUP_DATE=$1
BACKUP_DIR="/opt/aegis/backups"

echo "Starting disaster recovery for date: $BACKUP_DATE"

# Stop services
docker-compose down

# Restore database
echo "Restoring database..."
gunzip -c $BACKUP_DIR/db_backup_$BACKUP_DATE.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_NAME

# Restore files
echo "Restoring files..."
tar -xzf $BACKUP_DIR/files_backup_$BACKUP_DATE.tar.gz -C /

# Restore configuration
echo "Restoring configuration..."
tar -xzf $BACKUP_DIR/config_backup_$BACKUP_DATE.tar.gz -C /

# Start services
docker-compose up -d

echo "Disaster recovery completed"
```

## 🔧 Troubleshooting

### 1. Common Issues

#### Database Connection Issues
```bash
# Check database status
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='aegis_db';"

# Reset connections
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='aegis_db';"
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
iostat -x 1

# Check application logs
docker logs aegis-backend
tail -f /var/log/aegis/application.log

# Check database performance
sudo -u postgres psql -d aegis_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### 2. Log Analysis

#### Error Pattern Analysis
```bash
# Most common errors
grep "ERROR" /var/log/aegis/*.log | cut -d' ' -f5- | sort | uniq -c | sort -nr | head -20

# Failed login attempts
grep "LOGIN_FAILED" /var/log/aegis/security.log | wc -l

# Database errors
grep "database" /var/log/aegis/application.log | grep -i error
```

### 3. Recovery Procedures

#### Service Recovery
```bash
# Restart specific service
docker-compose restart aegis-backend

# Full system restart
docker-compose down && docker-compose up -d

# Check service health
curl -f http://localhost:8000/health || echo "Service unhealthy"
```

## 📈 Capacity Planning

### 1. Resource Monitoring

#### System Metrics
- **CPU Usage**: Target < 70% average
- **Memory Usage**: Target < 80% utilization
- **Disk Usage**: Target < 85% capacity
- **Network**: Monitor bandwidth utilization
- **Database**: Connection pool, query performance

#### Growth Planning
```python
# Calculate resource requirements
def calculate_capacity_requirements(users, assessments_per_year, retention_years):
    # Estimate database size
    db_size_per_user = 10  # MB
    db_size_per_assessment = 5  # MB
    
    total_db_size = (users * db_size_per_user) + \
                   (assessments_per_year * retention_years * db_size_per_assessment)
    
    # Estimate file storage
    files_per_assessment = 10
    avg_file_size = 2  # MB
    
    total_file_storage = assessments_per_year * retention_years * \
                        files_per_assessment * avg_file_size
    
    return {
        "database_size_gb": total_db_size / 1024,
        "file_storage_gb": total_file_storage / 1024,
        "recommended_ram_gb": max(16, users / 50),
        "recommended_cpu_cores": max(4, users / 100)
    }
```

---

This administrator guide provides comprehensive information for managing the Aegis Risk Management Platform. For additional support, refer to the troubleshooting section or contact the development team.