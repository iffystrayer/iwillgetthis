# Production Deployment Guide - Aegis Risk Management Platform

**Target Environment:** Production  
**Platform Version:** 1.0.0  
**Deployment Type:** Docker Compose with Production Hardening  

---

## 🎯 Pre-Deployment Checklist

### Infrastructure Requirements ✅
- [ ] **Server Specifications**: Minimum 4 CPU cores, 8GB RAM, 100GB storage
- [ ] **Operating System**: Ubuntu 22.04 LTS or equivalent
- [ ] **Docker**: Version 24.0+ installed
- [ ] **Docker Compose**: Version 2.0+ installed
- [ ] **Domain & DNS**: Production domain configured with SSL certificates
- [ ] **Database**: PostgreSQL 15+ (managed service recommended)
- [ ] **Redis**: Managed Redis service (AWS ElastiCache, Azure Cache, etc.)
- [ ] **Load Balancer**: If scaling beyond single server

### Security Requirements ✅
- [ ] **SSL Certificates**: Valid SSL certificates for your domain
- [ ] **Firewall**: Properly configured firewall rules
- [ ] **Secret Management**: Production secrets generated and secured
- [ ] **Backup Strategy**: Automated backup system in place
- [ ] **Monitoring**: Logging and monitoring systems configured

---

## 🚀 Production Deployment Steps

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/aegis-platform
sudo chown $USER:$USER /opt/aegis-platform
```

### Step 2: Application Deployment

```bash
# Clone/copy application files to server
cd /opt/aegis-platform

# Copy production environment file
cp .env.production .env

# Edit production configuration
nano .env
# Update the following critical values:
# - VITE_API_URL=https://api.yourdomain.com/api/v1
# - CORS_ORIGINS with your actual domains
# - DATABASE_URL with your managed database
# - REDIS_URL with your managed Redis
# - All SECRET_KEY values with actual production secrets
# - SSL certificate paths
# - Email SMTP settings
# - External API keys (OpenAI, etc.)

# Set secure file permissions
chmod 600 .env
```

### Step 3: SSL Certificate Setup

```bash
# If using Let's Encrypt
sudo apt install certbot nginx
sudo certbot certonly --nginx -d yourdomain.com -d api.yourdomain.com

# Copy certificates to expected location
sudo mkdir -p /etc/ssl/certs /etc/ssl/private
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /etc/ssl/certs/aegis-platform.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /etc/ssl/private/aegis-platform.key
sudo chmod 644 /etc/ssl/certs/aegis-platform.crt
sudo chmod 600 /etc/ssl/private/aegis-platform.key
```

### Step 4: Database Setup (External)

```bash
# For AWS RDS PostgreSQL
aws rds create-db-instance \\
  --db-instance-identifier aegis-production \\
  --db-instance-class db.t3.medium \\
  --engine postgres \\
  --engine-version 15.4 \\
  --master-username aegis_user \\
  --master-user-password "YOUR_SECURE_PASSWORD" \\
  --allocated-storage 100 \\
  --storage-type gp2 \\
  --backup-retention-period 7 \\
  --multi-az \\
  --storage-encrypted

# Update DATABASE_URL in .env with actual connection string
```

### Step 5: Launch Production Stack

```bash
# Build and start production services
docker-compose -f docker/docker-compose.prod.yml up --build -d

# Verify all services are healthy
docker-compose -f docker/docker-compose.prod.yml ps

# Check logs for any errors
docker-compose -f docker/docker-compose.prod.yml logs -f
```

### Step 6: Post-Deployment Verification

```bash
# Run health checks
curl -k https://yourdomain.com/health
curl -k https://api.yourdomain.com/health

# Run production test suite
docker-compose -f docker/docker-compose.prod.yml exec backend python test_integration_e2e_fixed.py

# Verify SSL configuration
curl -I https://yourdomain.com
```

---

## 🔒 Security Hardening

### System Level Security
```bash
# Configure firewall (UFW example)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Install fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Application Security
- **Environment Variables**: All sensitive data in environment variables, never in code
- **Rate Limiting**: Implemented in production configuration
- **CORS**: Restricted to production domains only
- **Security Headers**: HSTS, CSP, and other security headers configured
- **JWT Tokens**: Short-lived access tokens with secure refresh mechanism

---

## 📊 Monitoring & Logging

### Health Monitoring
```bash
# Set up automated health checks (example with systemd timer)
sudo tee /etc/systemd/system/aegis-health-check.service << EOF
[Unit]
Description=Aegis Platform Health Check

[Service]
Type=oneshot
ExecStart=/opt/aegis-platform/scripts/health-check.sh
EOF

sudo tee /etc/systemd/system/aegis-health-check.timer << EOF
[Unit]
Description=Run Aegis health check every 5 minutes

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl enable aegis-health-check.timer
sudo systemctl start aegis-health-check.timer
```

### Log Management
- **Application Logs**: JSON format for structured logging
- **Access Logs**: Nginx access logs for traffic analysis
- **Error Logs**: Centralized error logging with Sentry (optional)
- **Audit Logs**: All user actions logged for compliance

---

## 🔄 Backup & Recovery

### Automated Backup Script
```bash
#!/bin/bash
# /opt/aegis-platform/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/aegis-platform/backups"
S3_BUCKET="aegis-production-backups"

# Database backup
pg_dump $DATABASE_URL > $BACKUP_DIR/db_backup_$DATE.sql

# Application data backup
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz /opt/aegis-platform/uploads

# Upload to S3
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql s3://$S3_BUCKET/
aws s3 cp $BACKUP_DIR/app_data_$DATE.tar.gz s3://$S3_BUCKET/

# Clean up local backups older than 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Crontab Setup
```bash
# Add to crontab (crontab -e)
0 2 * * * /opt/aegis-platform/scripts/backup.sh >> /var/log/aegis-backup.log 2>&1
```

---

## 🎯 Performance Optimization

### Database Optimization
- **Connection Pooling**: Configured with appropriate pool sizes
- **Indexing**: Ensure proper database indexes are in place
- **Query Optimization**: Monitor slow queries and optimize

### Application Optimization
- **Caching**: Redis caching for API responses
- **CDN**: Use CDN for static assets
- **Compression**: Gzip compression enabled

### Infrastructure Optimization
- **Load Balancing**: If multiple instances needed
- **Auto Scaling**: Configure auto-scaling based on CPU/memory usage
- **Database Scaling**: Use read replicas for read-heavy workloads

---

## 🔧 Maintenance Procedures

### Regular Maintenance Tasks
- **Weekly**: Review security logs and system updates
- **Monthly**: Database performance analysis and optimization
- **Quarterly**: Security vulnerability assessment
- **Annually**: SSL certificate renewal (if not automated)

### Emergency Procedures
- **Service Restart**: `docker-compose restart <service>`
- **Full System Restart**: `docker-compose down && docker-compose up -d`
- **Database Recovery**: Restore from latest backup
- **Rollback**: Keep previous version images for quick rollback

---

## 📞 Support & Troubleshooting

### Common Issues & Solutions

#### Service Won't Start
```bash
# Check logs
docker-compose logs <service_name>

# Check disk space
df -h

# Check memory usage
free -h

# Restart specific service
docker-compose restart <service_name>
```

#### SSL Certificate Issues
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/aegis-platform.crt -text -noout | grep "Not After"

# Renew Let's Encrypt certificate
sudo certbot renew
```

#### Database Connection Issues
```bash
# Test database connection
docker-compose exec backend python -c "from database import engine; print('DB Connected:', engine.execute('SELECT 1').scalar())"
```

### Support Contacts
- **System Administrator**: [Your contact info]
- **Development Team**: [Your contact info]
- **Emergency Contact**: [24/7 contact info]

---

## ✅ Production Deployment Complete

After completing all steps above, your Aegis Risk Management Platform will be:

- ✅ **Secure**: Production-grade security hardening
- ✅ **Scalable**: Ready for enterprise load
- ✅ **Monitored**: Comprehensive logging and health checks
- ✅ **Backed Up**: Automated backup and recovery
- ✅ **Compliant**: Ready for audit and compliance requirements

**Next Steps**: Proceed to User Acceptance Testing (UAT) with production-like environment.