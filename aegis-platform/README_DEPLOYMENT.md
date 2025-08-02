# Aegis Risk Management Platform - Deployment Guide

## Overview

The Aegis Risk Management Platform is a comprehensive enterprise cybersecurity risk management solution with advanced AI capabilities. This guide provides step-by-step instructions for deploying the platform in a production environment.

## Architecture

The platform consists of:

- **Frontend**: React + TypeScript + TailwindCSS (Port 3000)
- **Backend**: FastAPI + Python (Port 8000)
- **Database**: PostgreSQL 15 (Port 5432)
- **Cache**: Redis 7 (Port 6379)
- **AI Services**: Multi-provider LLM integration
- **File Storage**: Local filesystem with configurable upload limits

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 20GB free space
- **CPU**: 4+ cores recommended

### Required Software

1. **Docker** (20.10.0 or later)
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   ```

2. **Docker Compose** (2.0.0 or later)
   ```bash
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Git** (for cloning the repository)
   ```bash
   sudo apt update && sudo apt install git
   ```

## Quick Start Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aegis-platform
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section below)
nano .env
```

### 3. Deploy the Platform

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy the complete platform
./deploy.sh
```

The deployment script will:
- Check prerequisites
- Build Docker images
- Start all services
- Initialize the database with seed data
- Show deployment status and access URLs

### 4. Access the Platform

Once deployed, access the platform at:

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. Default Login Credentials

- **Admin**: admin@aegis-platform.com / admin123
- **Analyst**: analyst@aegis-platform.com / analyst123
- **Viewer**: viewer@aegis-platform.com / viewer123

## Configuration

### Core Settings

Edit the `.env` file to configure:

```bash
# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Database
POSTGRES_PASSWORD=secure-database-password

# AI Provider (Optional)
OPENAI_API_KEY=sk-your-openai-api-key
AZURE_OPENAI_API_KEY=your-azure-openai-key
```

### AI/LLM Providers

The platform supports multiple AI providers:

#### OpenAI
```bash
ENABLE_OPENAI=true
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4-turbo-preview
```

#### Azure OpenAI
```bash
ENABLE_AZURE_OPENAI=true
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo
```

#### Local Providers (Ollama)
```bash
ENABLE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### External Integrations

#### OpenVAS (Vulnerability Scanner)
```bash
ENABLE_OPENVAS=true
OPENVAS_HOST=your-openvas-server
OPENVAS_USERNAME=admin
OPENVAS_PASSWORD=your-password
```

#### OpenCTI (Threat Intelligence)
```bash
ENABLE_OPENCTI=true
OPENCTI_URL=http://your-opencti-server:8080
OPENCTI_TOKEN=your-api-token
```

#### Microsoft Entra ID (Azure AD)
```bash
ENABLE_AZURE_AUTH=true
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

## Management Commands

### Service Management

```bash
# View service status
./deploy.sh --status

# View logs
./deploy.sh --logs

# Stop services
./deploy.sh --stop

# Update deployment
./deploy.sh --update

# Complete cleanup
./deploy.sh --cleanup
```

### Database Management

```bash
# Connect to database
docker exec -it aegis-db psql -U aegis_user -d aegis_db

# Backup database
docker exec aegis-db pg_dump -U aegis_user aegis_db > backup.sql

# Restore database
docker exec -i aegis-db psql -U aegis_user -d aegis_db < backup.sql
```

### Logs and Monitoring

```bash
# View all service logs
docker-compose -f docker/docker-compose.yml logs -f

# View specific service logs
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend
docker-compose -f docker/docker-compose.yml logs -f db

# Monitor resource usage
docker stats
```

## Production Hardening

### Security Checklist

1. **Change Default Credentials**
   - Update `SECRET_KEY` and `JWT_SECRET_KEY`
   - Change database passwords
   - Create new admin users and disable defaults

2. **Network Security**
   - Use reverse proxy (Nginx/Apache)
   - Enable HTTPS with SSL certificates
   - Configure firewall rules
   - Restrict database access

3. **File Permissions**
   ```bash
   # Secure configuration files
   chmod 600 .env
   chown root:root .env
   ```

4. **Regular Updates**
   - Keep Docker images updated
   - Monitor security advisories
   - Implement backup procedures

### Reverse Proxy Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :8000
   netstat -tulpn | grep :5432
   
   # Stop conflicting services
   sudo systemctl stop postgresql
   sudo systemctl stop redis-server
   ```

2. **Permission Issues**
   ```bash
   # Fix Docker permissions
   sudo usermod -aG docker $USER
   newgrp docker
   
   # Fix file permissions
   sudo chown -R $USER:$USER ./uploads
   sudo chown -R $USER:$USER ./logs
   ```

3. **Database Connection Issues**
   ```bash
   # Check database logs
   docker logs aegis-db
   
   # Test database connectivity
   docker exec aegis-db pg_isready -U aegis_user -d aegis_db
   ```

4. **Frontend Build Issues**
   ```bash
   # Rebuild frontend with no cache
   cd docker
   docker-compose build --no-cache frontend
   docker-compose up -d frontend
   ```

### Log Analysis

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:3000/

# View backend logs for errors
docker logs aegis-backend | grep ERROR

# Monitor database performance
docker exec aegis-db pg_stat_activity
```

### Recovery Procedures

1. **Complete Reset**
   ```bash
   ./deploy.sh --cleanup
   ./deploy.sh
   ```

2. **Database Recovery**
   ```bash
   # Stop services
   docker-compose -f docker/docker-compose.yml stop
   
   # Remove database volume
   docker volume rm docker_postgres_data
   
   # Restart with fresh database
   ./deploy.sh
   ```

## Performance Optimization

### Resource Allocation

```yaml
# In docker-compose.yml, add resource limits:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Database Tuning

```bash
# Optimize PostgreSQL settings
docker exec -it aegis-db psql -U aegis_user -d aegis_db

-- Increase shared_buffers and work_mem
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET max_connections = '200';
SELECT pg_reload_conf();
```

## Support and Maintenance

### Backup Strategy

1. **Database Backups**
   ```bash
   # Daily backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   docker exec aegis-db pg_dump -U aegis_user aegis_db | gzip > backup_${DATE}.sql.gz
   ```

2. **File Backups**
   ```bash
   # Backup uploads and logs
   tar -czf aegis_files_${DATE}.tar.gz uploads/ logs/
   ```

### Monitoring

1. **Health Checks**
   ```bash
   # Add to crontab for monitoring
   */5 * * * * curl -f http://localhost:8000/health || echo "Aegis backend down" | mail -s "Alert" admin@company.com
   ```

2. **Log Rotation**
   ```bash
   # Configure logrotate
   echo "/var/lib/docker/volumes/aegis_logs_data/_data/*.log {
       daily
       rotate 30
       compress
       delaycompress
       missingok
       notifempty
   }" > /etc/logrotate.d/aegis
   ```

---

For additional support or advanced configuration, refer to the platform documentation or contact the development team.
