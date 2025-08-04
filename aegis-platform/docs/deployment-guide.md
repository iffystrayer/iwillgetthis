# Aegis Platform - Deployment Guide

## 🚀 Production Deployment Guide

This guide provides comprehensive instructions for deploying the Aegis Risk Management Platform in production environments, including Docker, Kubernetes, and traditional server deployments.

## 📋 Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Infrastructure Requirements](#infrastructure-requirements)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Traditional Server Deployment](#traditional-server-deployment)
- [Database Setup](#database-setup)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Load Balancing](#load-balancing)
- [Monitoring & Logging](#monitoring--logging)
- [Backup Configuration](#backup-configuration)
- [Security Hardening](#security-hardening)

## ✅ Pre-Deployment Checklist

### Infrastructure Planning
- [ ] **Server Sizing**: CPU, RAM, storage requirements calculated
- [ ] **Network Architecture**: Firewall rules, VPC/subnet design
- [ ] **Database Planning**: High availability, backup strategy
- [ ] **SSL Certificates**: Domain validation and certificate acquisition
- [ ] **DNS Configuration**: Domain names and load balancer setup
- [ ] **Monitoring Setup**: Logging, metrics, and alerting systems
- [ ] **Backup Strategy**: Database and file system backup plans
- [ ] **Security Review**: Vulnerability assessment completed

### Application Preparation
- [ ] **Environment Variables**: Production configuration ready
- [ ] **Secrets Management**: API keys and passwords secured
- [ ] **Database Migration**: Schema and initial data prepared
- [ ] **Static Assets**: File storage and CDN configuration
- [ ] **Integration Testing**: External services connectivity verified
- [ ] **Performance Testing**: Load testing completed
- [ ] **Security Scanning**: Container and dependency scanning done
- [ ] **Documentation**: Deployment procedures documented

## 🖥️ Infrastructure Requirements

### Minimum Production Requirements
- **CPU**: 8 cores (3.0GHz)
- **RAM**: 16GB
- **Storage**: 500GB SSD with IOPS > 3000
- **Network**: 1Gbps with low latency
- **OS**: Ubuntu 20.04 LTS or RHEL 8+

### Recommended Production Setup
- **CPU**: 16 cores (3.5GHz)
- **RAM**: 32GB
- **Storage**: 1TB NVMe SSD with RAID 10
- **Network**: 10Gbps with redundancy
- **Database**: Dedicated PostgreSQL cluster
- **Cache**: Redis cluster for session and caching
- **Load Balancer**: HAProxy or AWS ALB
- **CDN**: CloudFlare or AWS CloudFront

### High Availability Architecture
```
┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Load Balancer │
│   (Primary)     │    │   (Secondary)   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
    ┌─────┴──────────────────────┴─────┐
    │                                  │
┌───▼────┐  ┌─────────┐  ┌─────────┐  ┌▼────────┐
│ App 1  │  │  App 2  │  │  App 3  │  │  App N  │
│(Active)│  │(Active) │  │(Active) │  │(Active) │
└───┬────┘  └────┬────┘  └────┬────┘  └─────┬───┘
    └─────┬──────┴──────┬─────┴─────────────┘
          │             │
    ┌─────▼─────┐ ┌─────▼─────┐
    │PostgreSQL │ │   Redis   │
    │ Primary   │ │  Cluster  │
    └─────┬─────┘ └───────────┘
          │
    ┌─────▼─────┐
    │PostgreSQL │
    │Secondary  │
    └───────────┘
```

## 🐳 Docker Deployment

### 1. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  aegis-backend:
    image: aegis-platform/backend:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://aegis:${DB_PASSWORD}@postgres:5432/aegis_prod
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - LOG_LEVEL=INFO
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - aegis_uploads:/app/uploads
      - aegis_logs:/app/logs
    networks:
      - aegis_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:14-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=aegis_prod
      - POSTGRES_USER=aegis
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - aegis_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aegis -d aegis_prod"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - aegis_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - aegis_uploads:/var/www/uploads:ro
    networks:
      - aegis_network
    depends_on:
      - aegis-backend

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  aegis_uploads:
    driver: local
  aegis_logs:
    driver: local

networks:
  aegis_network:
    driver: bridge
```

### 2. Environment Configuration

Create `.env.prod`:

```bash
# Database
DB_PASSWORD=your_secure_database_password
REDIS_PASSWORD=your_secure_redis_password

# Application Security
SECRET_KEY=your_super_secret_key_at_least_32_chars_long
JWT_SECRET_KEY=your_jwt_secret_key_different_from_above

# AI Services (Optional)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Email Configuration
SMTP_HOST=smtp.yourcompany.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourcompany.com
SMTP_PASSWORD=your_smtp_password

# External Services
OPENVAS_HOST=scanner.yourcompany.com
OPENVAS_USERNAME=aegis_scanner
OPENVAS_PASSWORD=scanner_password
```

### 3. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    upstream aegis_backend {
        server aegis-backend:8000;
        keepalive 32;
    }
    
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers on;
        
        # API Proxy
        location /api/ {
            proxy_pass http://aegis_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Health Check
        location /health {
            proxy_pass http://aegis_backend;
            access_log off;
        }
        
        # File Uploads
        location /uploads/ {
            alias /var/www/uploads/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Documentation
        location /docs {
            proxy_pass http://aegis_backend;
        }
        
        # Static Files (if serving frontend)
        location / {
            root /var/www/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }
    }
}
```

### 4. Deployment Commands

```bash
# Set production environment
export COMPOSE_FILE=docker-compose.prod.yml

# Pull latest images
docker-compose pull

# Start services
docker-compose up -d

# Check service health
docker-compose ps
docker-compose logs -f aegis-backend

# Run database migrations (if needed)
docker-compose exec aegis-backend python -c "
from database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Create initial admin user
docker-compose exec aegis-backend python scripts/create_admin.py
```

## ☸️ Kubernetes Deployment

### 1. Namespace and ConfigMap

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aegis-platform
  labels:
    name: aegis-platform
---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aegis-config
  namespace: aegis-platform
data:
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "aegis_prod"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
```

### 2. Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: aegis-secrets
  namespace: aegis-platform
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DB_PASSWORD: <base64-encoded-password>
  REDIS_PASSWORD: <base64-encoded-password>
  OPENAI_API_KEY: <base64-encoded-key>
  ANTHROPIC_API_KEY: <base64-encoded-key>
```

### 3. PostgreSQL Deployment

```yaml
# postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: aegis-platform
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "aegis_prod"
        - name: POSTGRES_USER
          value: "aegis"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: aegis-secrets
              key: DB_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - aegis
            - -d
            - aegis_prod
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - aegis
            - -d
            - aegis_prod
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
      storageClassName: fast-ssd
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: aegis-platform
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

### 4. Aegis Backend Deployment

```yaml
# aegis-backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aegis-backend
  namespace: aegis-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aegis-backend
  template:
    metadata:
      labels:
        app: aegis-backend
    spec:
      containers:
      - name: aegis-backend
        image: aegis-platform/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://aegis:$(DB_PASSWORD)@postgres-service:5432/aegis_prod"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: aegis-secrets
              key: SECRET_KEY
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: aegis-secrets
              key: DB_PASSWORD
        envFrom:
        - configMapRef:
            name: aegis-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: uploads-storage
          mountPath: /app/uploads
      volumes:
      - name: uploads-storage
        persistentVolumeClaim:
          claimName: uploads-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: aegis-backend-service
  namespace: aegis-platform
spec:
  selector:
    app: aegis-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 5. Ingress Configuration

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aegis-ingress
  namespace: aegis-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: aegis-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: aegis-backend-service
            port:
              number: 8000
```

### 6. Kubernetes Deployment Commands

```bash
# Apply all configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
kubectl apply -f aegis-backend.yaml
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get pods -n aegis-platform
kubectl get services -n aegis-platform
kubectl get ingress -n aegis-platform

# View logs
kubectl logs -f deployment/aegis-backend -n aegis-platform

# Scale deployment
kubectl scale deployment aegis-backend --replicas=5 -n aegis-platform
```

## 🗄️ Database Setup

### 1. PostgreSQL Configuration

#### postgresql.conf optimizations:
```conf
# Memory
shared_buffers = 4GB
work_mem = 256MB
maintenance_work_mem = 1GB
effective_cache_size = 12GB

# Connections
max_connections = 200
max_prepared_transactions = 200

# Logging
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000

# Performance
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Replication (if using)
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64
```

#### pg_hba.conf security:
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    aegis_prod      aegis           10.0.0.0/8              md5
```

### 2. Database Initialization Script

```sql
-- init-db.sql
CREATE DATABASE aegis_prod;
CREATE USER aegis WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE aegis_prod TO aegis;

-- Connect to aegis_prod database
\c aegis_prod;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO aegis;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aegis;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aegis;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO aegis;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO aegis;
```

## 🔒 SSL/TLS Configuration

### 1. Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Custom SSL Certificate

```bash
# Generate private key
openssl genrsa -out private.key 2048

# Generate certificate signing request
openssl req -new -key private.key -out certificate.csr

# Install certificate files
sudo cp certificate.crt /etc/ssl/certs/
sudo cp private.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/private.key
```

## ⚖️ Load Balancing

### 1. HAProxy Configuration

```conf
# haproxy.cfg
global
    daemon
    maxconn 4096
    user haproxy
    group haproxy
    
defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog
    option dontlognull
    
frontend aegis_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/aegis.pem
    redirect scheme https if !{ ssl_fc }
    
    # Security headers
    http-response set-header X-Frame-Options DENY
    http-response set-header X-Content-Type-Options nosniff
    
    default_backend aegis_backend
    
backend aegis_backend
    balance roundrobin
    option httpchk GET /health
    
    server app1 10.0.1.10:8000 check
    server app2 10.0.1.11:8000 check
    server app3 10.0.1.12:8000 check
```

### 2. AWS Application Load Balancer

```yaml
# alb-config.yaml
Type: AWS::ElasticLoadBalancingV2::LoadBalancer
Properties:
  Name: aegis-alb
  Scheme: internet-facing
  Type: application
  SecurityGroups:
    - !Ref ALBSecurityGroup
  Subnets:
    - !Ref PublicSubnet1
    - !Ref PublicSubnet2
  Tags:
    - Key: Name
      Value: Aegis Platform ALB

TargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: aegis-targets
    Port: 8000
    Protocol: HTTP
    VpcId: !Ref VPC
    HealthCheckPath: /health
    HealthCheckIntervalSeconds: 30
    HealthyThresholdCount: 2
    UnhealthyThresholdCount: 3
```

## 📊 Monitoring & Logging

### 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aegis-platform'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

rule_files:
  - "aegis_alerts.yml"
```

### 2. Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Aegis Platform Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket{job=\"aegis-platform\"})"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends"
          }
        ]
      }
    ]
  }
}
```

### 3. Log Aggregation with ELK Stack

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/aegis/*.log
  fields:
    service: aegis-platform
  fields_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "aegis-platform-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
```

## 💾 Backup Configuration

### 1. Database Backup Script

```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="aegis_prod"
DB_USER="aegis"
RETENTION_DAYS=30

# Create backup
pg_dump -h localhost -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/aegis_db_$DATE.sql.gz

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/aegis_db_$DATE.sql.gz s3://aegis-backups/database/

# Cleanup old backups
find $BACKUP_DIR -name "aegis_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: aegis_db_$DATE.sql.gz"
```

### 2. File System Backup

```bash
#!/bin/bash
# backup-files.sh

BACKUP_DIR="/opt/backups"
SOURCE_DIR="/opt/aegis/uploads"
DATE=$(date +%Y%m%d_%H%M%S)

# Create compressed archive
tar -czf $BACKUP_DIR/aegis_files_$DATE.tar.gz -C $SOURCE_DIR .

# Upload to S3
aws s3 cp $BACKUP_DIR/aegis_files_$DATE.tar.gz s3://aegis-backups/files/

# Cleanup
find $BACKUP_DIR -name "aegis_files_*.tar.gz" -mtime +30 -delete

echo "File backup completed: aegis_files_$DATE.tar.gz"
```

## 🛡️ Security Hardening

### 1. Firewall Configuration (UFW)

```bash
# Reset firewall
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH access
sudo ufw allow from 10.0.0.0/8 to any port 22

# HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Database (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 5432

# Enable firewall
sudo ufw enable
```

### 2. System Security

```bash
# Disable root login
sudo passwd -l root

# Update system
sudo apt update && sudo apt upgrade -y

# Install security updates automatically
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Install fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Configure fail2ban
sudo cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

sudo systemctl restart fail2ban
```

### 3. Application Security

```bash
# Set file permissions
sudo chown -R aegis:aegis /opt/aegis
sudo chmod 750 /opt/aegis
sudo chmod 640 /opt/aegis/.env

# Secure uploaded files
sudo chmod 750 /opt/aegis/uploads
sudo chown -R www-data:aegis /opt/aegis/uploads

# Log file permissions
sudo chmod 644 /var/log/aegis/*.log
sudo chown syslog:adm /var/log/aegis/*.log
```

This deployment guide provides comprehensive instructions for securely deploying the Aegis Platform in production environments. Follow the security hardening steps and monitoring setup to ensure a robust, secure deployment.