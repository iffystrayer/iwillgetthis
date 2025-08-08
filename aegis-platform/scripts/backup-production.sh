#!/bin/bash

# Production Backup Script for Aegis Platform
# This script creates comprehensive backups of the production system

set -euo pipefail

# Configuration
COMPOSE_FILE="docker/docker-compose.prod.yml"
BACKUP_ROOT="/var/backups/aegis-platform"
RETENTION_DAYS=30
S3_BUCKET="${BACKUP_S3_BUCKET:-}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Create backup directory
create_backup_dir() {
    log "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
}

# Backup database
backup_database() {
    log "Backing up MySQL database..."
    
    if ! docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
        warn "Database container is not running, skipping database backup"
        return
    fi
    
    local db_backup_file="$BACKUP_DIR/aegis_database_$DATE.sql"
    
    docker-compose -f "$COMPOSE_FILE" exec -T db mysqldump \
        --single-transaction \
        --routines \
        --triggers \
        --all-databases \
        -u"${DB_USER:-aegis_user}" -p"${DB_PASSWORD}" \
        > "$db_backup_file"
    
    gzip "$db_backup_file"
    log "Database backup completed: ${db_backup_file}.gz"
}

# Backup application data
backup_volumes() {
    log "Backing up Docker volumes..."
    
    local volumes=(
        "aegis_platform_uploads"
        "aegis_platform_logs"
        "aegis_platform_reports"
    )
    
    for volume in "${volumes[@]}"; do
        if docker volume ls | grep -q "$volume"; then
            log "Backing up volume: $volume"
            docker run --rm \
                -v "$volume:/source:ro" \
                -v "$BACKUP_DIR:/backup" \
                alpine tar -czf "/backup/${volume}_$DATE.tar.gz" -C /source .
        else
            warn "Volume $volume not found, skipping"
        fi
    done
}

# Backup configuration files
backup_configs() {
    log "Backing up configuration files..."
    
    local config_backup_dir="$BACKUP_DIR/configs"
    mkdir -p "$config_backup_dir"
    
    # Backup docker configurations
    cp -r docker "$config_backup_dir/"
    
    # Backup environment file (without sensitive data)
    if [[ -f ".env.prod" ]]; then
        # Remove sensitive values for security
        sed 's/=.*/=***REDACTED***/g' .env.prod > "$config_backup_dir/env.template"
    fi
    
    # Backup SSL certificates
    if [[ -d "docker/nginx/ssl" ]]; then
        cp -r docker/nginx/ssl "$config_backup_dir/"
    fi
    
    log "Configuration backup completed"
}

# Backup monitoring data
backup_monitoring() {
    log "Backing up monitoring data..."
    
    local monitoring_backup_dir="$BACKUP_DIR/monitoring"
    mkdir -p "$monitoring_backup_dir"
    
    # Backup Grafana dashboards and data
    if docker-compose -f "$COMPOSE_FILE" ps grafana | grep -q "Up"; then
        docker run --rm \
            -v aegis_platform_grafana_data:/source:ro \
            -v "$monitoring_backup_dir:/backup" \
            alpine tar -czf "/backup/grafana_data_$DATE.tar.gz" -C /source .
    fi
    
    # Backup Prometheus data
    if docker-compose -f "$COMPOSE_FILE" ps prometheus | grep -q "Up"; then
        docker run --rm \
            -v aegis_platform_prometheus_data:/source:ro \
            -v "$monitoring_backup_dir:/backup" \
            alpine tar -czf "/backup/prometheus_data_$DATE.tar.gz" -C /source .
    fi
    
    log "Monitoring data backup completed"
}

# Create system information snapshot
create_system_info() {
    log "Creating system information snapshot..."
    
    local info_file="$BACKUP_DIR/system_info.txt"
    {
        echo "Aegis Platform Backup Information"
        echo "Backup Date: $(date)"
        echo "System: $(uname -a)"
        echo "Docker Version: $(docker --version)"
        echo "Docker Compose Version: $(docker-compose --version)"
        echo ""
        echo "Running Services:"
        docker-compose -f "$COMPOSE_FILE" ps
        echo ""
        echo "Docker Images:"
        docker images | grep aegis
        echo ""
        echo "Docker Volumes:"
        docker volume ls | grep aegis
    } > "$info_file"
    
    log "System information saved"
}

# Calculate backup size
calculate_backup_size() {
    local size=$(du -sh "$BACKUP_DIR" | cut -f1)
    log "Backup size: $size"
    echo "$size" > "$BACKUP_DIR/backup_size.txt"
}

# Upload to S3 (if configured)
upload_to_s3() {
    if [[ -z "$S3_BUCKET" ]]; then
        log "S3 backup not configured, skipping cloud upload"
        return
    fi
    
    log "Uploading backup to S3: $S3_BUCKET"
    
    if ! command -v aws &> /dev/null; then
        warn "AWS CLI not found, skipping S3 upload"
        return
    fi
    
    # Create archive
    local archive_name="aegis_backup_$DATE.tar.gz"
    tar -czf "/tmp/$archive_name" -C "$BACKUP_ROOT" "$DATE"
    
    # Upload to S3
    aws s3 cp "/tmp/$archive_name" "s3://$S3_BUCKET/aegis-platform/$archive_name"
    
    # Cleanup local archive
    rm "/tmp/$archive_name"
    
    log "S3 upload completed"
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_ROOT" -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
    
    # Cleanup S3 if configured
    if [[ -n "$S3_BUCKET" ]] && command -v aws &> /dev/null; then
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y%m%d)
        aws s3 ls "s3://$S3_BUCKET/aegis-platform/" | while read -r line; do
            local object_date=$(echo "$line" | awk '{print $4}' | grep -o '[0-9]\{8\}' | head -1)
            if [[ "$object_date" < "$cutoff_date" ]]; then
                local object_name=$(echo "$line" | awk '{print $4}')
                aws s3 rm "s3://$S3_BUCKET/aegis-platform/$object_name"
                log "Deleted old S3 backup: $object_name"
            fi
        done
    fi
    
    log "Cleanup completed"
}

# Send notification (if configured)
send_notification() {
    local status=$1
    local message=$2
    
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Aegis Platform Backup - $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" || warn "Failed to send Slack notification"
    fi
    
    if [[ -n "${EMAIL_RECIPIENT:-}" ]] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "Aegis Platform Backup - $status" "$EMAIL_RECIPIENT" || warn "Failed to send email notification"
    fi
}

# Verify backup integrity
verify_backup() {
    log "Verifying backup integrity..."
    
    local verification_failed=false
    
    # Check if database backup exists and is valid
    local db_backup="$BACKUP_DIR/aegis_database_$DATE.sql.gz"
    if [[ -f "$db_backup" ]]; then
        if zcat "$db_backup" | head -n 10 | grep -q "MySQL dump"; then
            log "Database backup verification passed"
        else
            warn "Database backup verification failed"
            verification_failed=true
        fi
    fi
    
    # Check if volume backups exist
    local volume_count=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f | wc -l)
    if [[ $volume_count -gt 0 ]]; then
        log "Found $volume_count volume backup files"
    else
        warn "No volume backup files found"
        verification_failed=true
    fi
    
    if [[ "$verification_failed" == "true" ]]; then
        error "Backup verification failed"
    fi
    
    log "Backup verification completed successfully"
}

# Main backup function
main() {
    local start_time=$(date +%s)
    
    log "Starting Aegis Platform backup..."
    log "Backup directory: $BACKUP_DIR"
    
    # Ensure backup root exists
    mkdir -p "$BACKUP_ROOT"
    
    # Load environment variables
    if [[ -f ".env.prod" ]]; then
        source .env.prod
    fi
    
    # Run backup steps
    create_backup_dir
    backup_database
    backup_volumes
    backup_configs
    backup_monitoring
    create_system_info
    calculate_backup_size
    verify_backup
    upload_to_s3
    cleanup_old_backups
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local backup_size=$(cat "$BACKUP_DIR/backup_size.txt")
    
    log "✅ Backup completed successfully!"
    log "Duration: ${duration}s"
    log "Backup size: $backup_size"
    log "Location: $BACKUP_DIR"
    
    send_notification "SUCCESS" "Backup completed in ${duration}s, size: $backup_size"
}

# Error handling
trap 'send_notification "FAILED" "Backup failed at line $LINENO"; exit 1' ERR

# Run main function
main "$@"