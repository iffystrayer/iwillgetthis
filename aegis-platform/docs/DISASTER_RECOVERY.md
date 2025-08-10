# Aegis Platform - Disaster Recovery Plan

## Overview

This document outlines the comprehensive disaster recovery procedures for the Aegis Risk Management Platform. It covers backup strategies, restoration procedures, and business continuity measures to ensure minimal downtime and data loss in the event of system failures.

## Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

| Scenario | RTO | RPO | Priority |
|----------|-----|-----|----------|
| Application Server Failure | 15 minutes | 6 hours | High |
| Database Server Failure | 30 minutes | 6 hours | Critical |
| Complete Infrastructure Loss | 4 hours | 24 hours | Critical |
| Regional Outage | 8 hours | 24 hours | Medium |
| Security Incident | 2 hours | 24 hours | Critical |

## Backup Strategy

### Backup Types and Frequency

#### 1. Database Backups
- **Full backups**: Daily at 2:00 AM UTC
- **Incremental backups**: Every 6 hours
- **Retention**: 30 days local, 90 days offsite
- **Encryption**: AES-256 encryption for all backups
- **Storage**: Local filesystem + AWS S3

#### 2. File System Backups
- **Application files**: Daily at 2:30 AM UTC
- **Configuration files**: Daily at 2:30 AM UTC
- **User uploads**: Daily at 2:30 AM UTC
- **SSL certificates**: Daily at 2:30 AM UTC
- **Retention**: 30 days local, 90 days offsite

#### 3. Monitoring Data Backups
- **Prometheus data**: Weekly on Sundays
- **Grafana dashboards**: Weekly on Sundays
- **Alerting configurations**: Weekly on Sundays
- **Retention**: 14 days local, 60 days offsite

### Backup Locations

#### Primary Backup Location
- **Location**: Local server filesystem (`/var/backups/aegis`)
- **Capacity**: 500GB allocated
- **Security**: Encrypted filesystem, restricted access
- **Monitoring**: Disk usage alerts at 80%

#### Secondary Backup Location (Offsite)
- **Location**: AWS S3 (Standard-IA storage class)
- **Region**: Different from primary infrastructure
- **Security**: Server-side encryption, IAM access controls
- **Versioning**: Enabled with lifecycle policies

## Disaster Recovery Procedures

### 1. Application Server Recovery

#### Scenario: Single application server failure

**Detection:**
- Monitoring alerts on service unavailability
- Health check failures
- Application error rates spike

**Recovery Steps:**
1. **Assess Impact** (2 minutes)
   ```bash
   # Check service status
   docker-compose ps
   systemctl status docker
   
   # Check system resources
   htop
   df -h
   ```

2. **Attempt Service Restart** (3 minutes)
   ```bash
   # Restart application stack
   cd /opt/aegis-platform
   docker-compose restart aegis-backend aegis-frontend
   
   # Check logs for issues
   docker-compose logs --tail=100 aegis-backend
   ```

3. **If restart fails, rebuild containers** (10 minutes)
   ```bash
   # Stop services
   docker-compose down
   
   # Rebuild and start
   docker-compose build --no-cache
   docker-compose up -d
   ```

**Validation:**
- Service health checks pass
- Application accessible via web interface
- Database connectivity confirmed
- Monitor error rates for 30 minutes

### 2. Database Server Recovery

#### Scenario: Database corruption or server failure

**Detection:**
- Database connection failures
- Data corruption alerts
- Backup verification failures

**Recovery Steps:**
1. **Emergency Assessment** (5 minutes)
   ```bash
   # Check database status
   docker-compose exec db psql -U aegis_user -d aegis_production -c "\dt"
   
   # Check database logs
   docker-compose logs db --tail=200
   ```

2. **Stop Application Services** (2 minutes)
   ```bash
   # Prevent further data corruption
   docker-compose stop aegis-backend aegis-frontend
   ```

3. **Database Recovery** (20 minutes)
   ```bash
   # Run restore script
   cd /opt/aegis-platform
   
   # Restore from latest backup
   RESTORE_CONFIRMATION=true ./scripts/restore-system.sh database
   
   # Or restore from specific date
   RESTORE_DATE=20240110 ./scripts/restore-system.sh database
   ```

4. **Restart Services** (3 minutes)
   ```bash
   # Start all services
   docker-compose up -d
   
   # Verify database connectivity
   docker-compose exec backend python -c "
   from database import engine
   from sqlalchemy import text
   with engine.connect() as conn:
       result = conn.execute(text('SELECT COUNT(*) FROM users'))
       print(f'Users in database: {result.scalar()}')
   "
   ```

**Validation:**
- Database queries execute successfully
- Application can read/write data
- No data integrity issues
- Monitor for 1 hour

### 3. Complete Infrastructure Recovery

#### Scenario: Total infrastructure loss (fire, natural disaster, etc.)

**Detection:**
- Complete service unavailability
- Infrastructure monitoring alerts
- No response from any system components

**Recovery Steps:**
1. **Activate DR Site** (30 minutes)
   ```bash
   # Provision new infrastructure (AWS/Cloud)
   # This should be pre-configured as Infrastructure as Code
   
   # Example Terraform deployment
   cd /opt/aegis-platform/terraform
   terraform apply -var="environment=disaster-recovery"
   ```

2. **Restore Data** (2-3 hours)
   ```bash
   # Download latest backups from S3
   AWS_S3_BUCKET=aegis-backups ./scripts/restore-system.sh full
   
   # Verify data integrity
   ./scripts/verify-backups.sh --comprehensive
   ```

3. **Update DNS and Network Configuration** (30 minutes)
   - Update DNS records to point to DR site
   - Configure SSL certificates for new environment
   - Update monitoring endpoints

4. **Validate Full System** (30 minutes)
   - Run comprehensive system tests
   - Verify all integrations work
   - Test user access and functionality

**Communication Plan:**
- Notify users of service disruption (within 15 minutes)
- Provide regular updates every 2 hours
- Announce service restoration

### 4. Security Incident Recovery

#### Scenario: Security breach or compromise

**Detection:**
- Security monitoring alerts
- Unusual activity patterns
- Data access anomalies

**Immediate Response:**
1. **Isolate Systems** (5 minutes)
   ```bash
   # Stop all services immediately
   docker-compose down
   
   # Isolate network (if possible)
   iptables -A INPUT -j DROP
   iptables -A OUTPUT -j DROP
   ```

2. **Assess Compromise** (30 minutes)
   - Review security logs
   - Identify breach scope
   - Determine data exposure

3. **Evidence Preservation** (15 minutes)
   ```bash
   # Create forensic backup
   dd if=/dev/sda of=/mnt/forensic/system-image-$(date +%Y%m%d).img
   
   # Preserve logs
   tar -czf /mnt/forensic/logs-$(date +%Y%m%d).tar.gz /var/log
   ```

**Recovery Steps:**
1. **Clean System Restoration** (2-4 hours)
   - Rebuild infrastructure from clean state
   - Restore data from pre-incident backups
   - Update all secrets and credentials
   - Apply security patches

2. **Security Hardening** (1-2 hours)
   - Review and update security configurations
   - Implement additional monitoring
   - Update access controls

## Recovery Testing

### Monthly Recovery Drills

**Database Recovery Test:**
```bash
# Test database restoration (non-production)
RESTORE_CONFIRMATION=true ./scripts/restore-system.sh database /path/to/test/backup.sql.gz

# Verify data integrity
./scripts/verify-restore.sh --database
```

**File Recovery Test:**
```bash
# Test file restoration
RESTORE_CONFIRMATION=true ./scripts/restore-system.sh files /path/to/test/backup.tar.gz

# Verify file integrity
find /app/uploads -type f -exec sha256sum {} \; > /tmp/restored-files.checksum
```

### Quarterly Full DR Test

**Complete Infrastructure Test:**
1. Deploy to DR environment
2. Restore all data from backups
3. Run full system tests
4. Measure RTO/RPO achievement
5. Document lessons learned

## Backup Verification

### Automated Verification
```bash
# Daily backup verification
./scripts/verify-backups.sh --daily

# Weekly comprehensive verification  
./scripts/verify-backups.sh --comprehensive --restore-test
```

### Verification Checklist
- [ ] Backup files created successfully
- [ ] Backup files encrypted properly
- [ ] Checksums match expected values
- [ ] S3 uploads completed
- [ ] Test restoration works
- [ ] Monitoring alerts configured

## Contact Information

### Emergency Contacts

| Role | Primary | Secondary |
|------|---------|-----------|
| System Administrator | +1-555-0101 | +1-555-0102 |
| Database Administrator | +1-555-0201 | +1-555-0202 |
| Security Team | +1-555-0301 | +1-555-0302 |
| Management | +1-555-0401 | +1-555-0402 |

### Escalation Matrix

| Time Since Incident | Notify |
|---------------------|--------|
| 0-15 minutes | Technical team |
| 15-30 minutes | Team leads |
| 30-60 minutes | Management |
| 60+ minutes | Executive team |

## Recovery Documentation Templates

### Incident Report Template
```
Incident ID: DR-YYYY-MM-DD-###
Date/Time: 
Incident Type: [Hardware/Software/Security/Natural Disaster]
Impact Level: [Low/Medium/High/Critical]

Description:
[Detailed description of incident]

Timeline:
- [Time] - Incident detected
- [Time] - Response initiated
- [Time] - Systems restored
- [Time] - Full service recovery

Root Cause:
[Analysis of what caused the incident]

Recovery Actions:
[Steps taken to resolve the incident]

Lessons Learned:
[What can be improved for future incidents]

Follow-up Actions:
[Preventive measures to implement]
```

### Recovery Checklist
- [ ] Incident detected and assessed
- [ ] Emergency procedures activated
- [ ] Stakeholders notified
- [ ] Data backups verified
- [ ] Systems restored from backup
- [ ] Services validated
- [ ] Performance monitoring resumed
- [ ] Security validated
- [ ] Users notified of resolution
- [ ] Incident documented
- [ ] Post-incident review scheduled

## Maintenance and Updates

### Backup System Maintenance
- **Monthly**: Test backup and restore procedures
- **Quarterly**: Review and update DR plan
- **Annually**: Conduct comprehensive DR exercise
- **As needed**: Update contact information and procedures

### Documentation Updates
- Update this document when infrastructure changes
- Review and validate all procedures quarterly
- Train new team members on DR procedures
- Maintain current emergency contact information

## Compliance and Auditing

### Audit Requirements
- Document all backup activities
- Maintain restoration test records
- Track RTO/RPO measurements
- Record all security incidents

### Compliance Considerations
- Data retention policies
- Encryption requirements
- Access control audits
- Incident reporting requirements

## Automation Scripts

All disaster recovery procedures are supported by automated scripts located in `/opt/aegis-platform/scripts/`:

- `backup-system.sh` - Automated backup creation
- `restore-system.sh` - Automated system restoration
- `verify-backups.sh` - Backup integrity verification
- `setup-monitoring.sh` - Monitoring system deployment
- `disaster-recovery-test.sh` - DR testing automation

Ensure all scripts are tested regularly and updated as the system evolves.