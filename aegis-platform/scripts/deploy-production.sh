#!/bin/bash

# Production Deployment Script for Aegis Platform
# This script handles the complete production deployment process

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
COMPOSE_FILE="docker/docker-compose.prod.yml"
ENV_FILE=".env.prod"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="./logs/deployment_$(date +%Y%m%d_%H%M%S).log"
DOMAIN="${DOMAIN:-aegis.yourdomain.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} $message" | tee -a "$LOG_FILE"
            ;;
    esac
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Error handler
error_exit() {
    log "ERROR" "$1"
    log "ERROR" "Deployment failed. Check logs at: $LOG_FILE"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        log "WARN" "Running as root is not recommended for security reasons"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "openssl" "curl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error_exit "$cmd is required but not installed"
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error_exit "Docker daemon is not running"
    fi
    
    # Check environment file
    if [[ ! -f "$ENV_FILE" ]]; then
        log "WARN" "Environment file $ENV_FILE not found"
        log "INFO" "Creating from template..."
        if [[ -f ".env.prod.template" ]]; then
            cp .env.prod.template "$ENV_FILE"
            log "WARN" "Please edit $ENV_FILE with your production values before continuing"
            exit 1
        else
            error_exit "Neither $ENV_FILE nor .env.prod.template found"
        fi
    fi
    
    log "INFO" "Prerequisites check completed"
}

# Generate SSL certificates if they don't exist
generate_ssl_certificates() {
    log "INFO" "Checking SSL certificates..."
    
    local ssl_dir="./docker/nginx/ssl"
    local cert_file="$ssl_dir/cert.pem"
    local key_file="$ssl_dir/key.pem"
    
    mkdir -p "$ssl_dir"
    
    if [[ ! -f "$cert_file" || ! -f "$key_file" ]]; then
        log "INFO" "Generating self-signed SSL certificates..."
        log "WARN" "For production, replace with proper SSL certificates from a CA"
        
        openssl req -x509 -newkey rsa:4096 -keyout "$key_file" -out "$cert_file" \
            -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=$DOMAIN"
        
        chmod 600 "$key_file"
        chmod 644 "$cert_file"
        
        log "INFO" "SSL certificates generated"
    else
        log "INFO" "SSL certificates already exist"
    fi
}

# Backup existing data
backup_data() {
    log "INFO" "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if container is running
    if docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
        log "INFO" "Backing up database..."
        docker-compose -f "$COMPOSE_FILE" exec -T db mysqldump \
            -u"${DB_USER:-aegis_user}" -p"${DB_PASSWORD}" "${DB_NAME:-aegis_production}" \
            > "$BACKUP_DIR/database_backup.sql" || log "WARN" "Database backup failed"
    fi
    
    # Backup volumes
    if docker volume ls | grep -q "aegis_platform_uploads"; then
        log "INFO" "Backing up upload volumes..."
        docker run --rm -v aegis_platform_uploads:/source -v "$(pwd)/$BACKUP_DIR":/backup alpine \
            tar -czf /backup/uploads_backup.tar.gz -C /source . || log "WARN" "Uploads backup failed"
    fi
    
    # Backup configuration files
    cp -r docker "$BACKUP_DIR/" || log "WARN" "Config backup failed"
    cp "$ENV_FILE" "$BACKUP_DIR/" || log "WARN" "Environment backup failed"
    
    log "INFO" "Backup completed at: $BACKUP_DIR"
}

# Build and start services
deploy_services() {
    log "INFO" "Starting production deployment..."
    
    # Pull latest images
    log "INFO" "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build custom images
    log "INFO" "Building application images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services
    log "INFO" "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    log "INFO" "Waiting for services to start..."
    sleep 30
    
    # Initialize database
    log "INFO" "Initializing database..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend python init_db_complete.py || {
        log "WARN" "Database initialization failed, continuing..."
    }
}

# Health checks
perform_health_checks() {
    log "INFO" "Performing health checks..."
    
    local max_retries=30
    local retry_count=0
    
    # Check backend health
    while [[ $retry_count -lt $max_retries ]]; do
        if curl -f "http://localhost:8000/health" &> /dev/null; then
            log "INFO" "Backend health check passed"
            break
        fi
        ((retry_count++))
        log "DEBUG" "Backend health check attempt $retry_count/$max_retries"
        sleep 10
    done
    
    if [[ $retry_count -eq $max_retries ]]; then
        error_exit "Backend health check failed after $max_retries attempts"
    fi
    
    # Check database connection
    if docker-compose -f "$COMPOSE_FILE" exec -T db mysql -u"${DB_USER:-aegis_user}" -p"${DB_PASSWORD}" -e "SELECT 1" &> /dev/null; then
        log "INFO" "Database connection check passed"
    else
        error_exit "Database connection check failed"
    fi
    
    # Check Redis connection
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping | grep -q "PONG"; then
        log "INFO" "Redis connection check passed"
    else
        error_exit "Redis connection check failed"
    fi
    
    log "INFO" "All health checks passed"
}

# Setup monitoring
setup_monitoring() {
    log "INFO" "Setting up monitoring..."
    
    # Create Grafana data directory
    mkdir -p ./docker/monitoring/grafana/data
    chmod 777 ./docker/monitoring/grafana/data
    
    # Import Grafana dashboards
    log "INFO" "Monitoring setup completed"
    log "INFO" "Grafana dashboard available at: http://localhost:3001"
    log "INFO" "Prometheus metrics at: http://localhost:9090"
}

# Setup log rotation
setup_log_rotation() {
    log "INFO" "Setting up log rotation..."
    
    # Create logrotate configuration
    sudo tee /etc/logrotate.d/aegis-platform > /dev/null <<EOF
./logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $(whoami) $(whoami)
    postrotate
        docker-compose -f $COMPOSE_FILE restart nginx || true
    endscript
}
EOF
    
    log "INFO" "Log rotation configured"
}

# Final security checks
security_checks() {
    log "INFO" "Performing security checks..."
    
    # Check for default passwords
    if grep -q "your_.*_password" "$ENV_FILE"; then
        error_exit "Default passwords detected in $ENV_FILE. Please update with secure passwords."
    fi
    
    # Check file permissions
    chmod 600 "$ENV_FILE"
    chmod -R 700 ./docker/nginx/ssl/
    
    # Check for exposed ports
    local exposed_ports=$(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Ports}}" | grep -oE '0\.0\.0\.0:[0-9]+' | cut -d: -f2 | sort -u)
    if [[ -n "$exposed_ports" ]]; then
        log "WARN" "Exposed ports detected: $exposed_ports"
        log "WARN" "Ensure firewall is properly configured"
    fi
    
    log "INFO" "Security checks completed"
}

# Main deployment function
main() {
    log "INFO" "Starting Aegis Platform production deployment"
    log "INFO" "Deployment log: $LOG_FILE"
    
    # Create necessary directories
    mkdir -p logs backups
    
    # Run deployment steps
    check_prerequisites
    generate_ssl_certificates
    backup_data
    deploy_services
    perform_health_checks
    setup_monitoring
    setup_log_rotation
    security_checks
    
    log "INFO" "✅ Deployment completed successfully!"
    log "INFO" "🌐 Application available at: https://$DOMAIN"
    log "INFO" "📊 Monitoring dashboard: http://localhost:3001"
    log "INFO" "📈 Metrics endpoint: http://localhost:9090"
    log "INFO" "📝 Logs directory: ./logs/"
    log "INFO" "💾 Backup created at: $BACKUP_DIR"
    
    echo
    echo -e "${GREEN}🎉 Aegis Platform is now running in production mode!${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Update DNS records to point $DOMAIN to this server"
    echo "2. Replace self-signed SSL certificates with proper CA certificates"
    echo "3. Configure firewall rules"
    echo "4. Set up automated backups"
    echo "5. Configure monitoring alerts"
}

# Handle script interruption
trap 'log "ERROR" "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"