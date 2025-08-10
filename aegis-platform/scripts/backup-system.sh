#!/bin/bash
# ==============================================
# Aegis Platform - Comprehensive Backup System
# ==============================================
# Automated backup solution for:
# - Database backups (PostgreSQL)
# - File system backups (uploads, configs)
# - Application data backups
# - Monitoring data backups
# - Encrypted offsite storage
# ==============================================

set -e

# Configuration
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/var/backups/aegis}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
BACKUP_ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"
AWS_S3_BUCKET="${AWS_S3_BUCKET:-}"
BACKUP_NOTIFICATION_EMAIL="${BACKUP_NOTIFICATION_EMAIL:-}"

# Database configuration
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-aegis_production}"
DB_USER="${POSTGRES_USER:-aegis_user}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${BACKUP_BASE_DIR}/backup.log"
}

check_requirements() {
    print_header "Checking Backup Requirements"
    
    # Check if running as appropriate user
    if [ "$(id -u)" -eq 0 ]; then
        print_warning "Running as root - ensure proper permissions are set"
    fi
    
    # Check required tools
    local required_tools=("pg_dump" "tar" "gzip")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check optional tools
    if command -v gpg &> /dev/null; then
        print_success "GPG available for encryption"
    else
        print_warning "GPG not available - backups will not be encrypted"
    fi
    
    if command -v aws &> /dev/null; then
        print_success "AWS CLI available for S3 uploads"
    else
        print_warning "AWS CLI not available - no S3 uploads"
    fi
    
    # Create backup directories
    mkdir -p "${BACKUP_BASE_DIR}"/{database,files,monitoring,temp}
    mkdir -p "${BACKUP_BASE_DIR}/logs"
    
    print_success "Requirements check completed"
}

backup_database() {
    print_header "Database Backup"
    log_message "Starting database backup"
    
    local backup_date=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_BASE_DIR}/database/aegis_db_${backup_date}.sql"
    local compressed_backup="${backup_file}.gz"
    
    # Set PostgreSQL password
    export PGPASSWORD="$DB_PASSWORD"
    
    # Create database dump
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
               --verbose --clean --create --format=plain \
               --file="$backup_file" 2>> "${BACKUP_BASE_DIR}/backup.log"; then
        print_success "Database dump created: $(basename "$backup_file")"
        log_message "Database backup completed successfully"
    else
        print_error "Database backup failed"
        log_message "ERROR: Database backup failed"
        return 1
    fi
    
    # Compress backup
    if gzip "$backup_file"; then
        print_success "Database backup compressed"
        backup_file="$compressed_backup"
    else
        print_warning "Compression failed, keeping uncompressed backup"
    fi
    
    # Encrypt if key is provided
    if [ -n "$BACKUP_ENCRYPTION_KEY" ] && command -v gpg &> /dev/null; then
        local encrypted_backup="${backup_file}.gpg"
        if echo "$BACKUP_ENCRYPTION_KEY" | gpg --batch --yes --passphrase-fd 0 \
           --cipher-algo AES256 --compress-algo 1 --symmetric \
           --output "$encrypted_backup" "$backup_file"; then
            rm "$backup_file"
            backup_file="$encrypted_backup"
            print_success "Database backup encrypted"
            log_message "Database backup encrypted successfully"
        else
            print_error "Encryption failed"
            log_message "WARNING: Database backup encryption failed"
        fi
    fi
    
    # Calculate backup size and checksum
    local backup_size=$(du -h "$backup_file" | cut -f1)
    local backup_checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
    
    log_message "Database backup details: File=${backup_file}, Size=${backup_size}, SHA256=${backup_checksum}"
    
    # Store backup metadata
    cat > "${backup_file}.meta" << EOF
backup_type=database
backup_date=$backup_date
backup_file=$(basename "$backup_file")
backup_size=$backup_size
backup_checksum=$backup_checksum
database_name=$DB_NAME
database_host=$DB_HOST
EOF
    
    echo "$backup_file"
}

backup_files() {
    print_header "File System Backup"
    log_message "Starting file system backup"
    
    local backup_date=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_BASE_DIR}/files/aegis_files_${backup_date}.tar.gz"
    
    # Define directories to backup
    local backup_dirs=(
        "/app/uploads"
        "/app/logs"
        "/app/config"
        "/etc/nginx/sites-available"
        "/etc/ssl/certs/aegis-*"
        "/etc/ssl/private/aegis-*"
    )
    
    # Create file list for existing directories
    local existing_dirs=()
    for dir in "${backup_dirs[@]}"; do
        if [ -e "$dir" ]; then
            existing_dirs+=("$dir")
        else
            print_warning "Skipping non-existent directory: $dir"
        fi
    done
    
    if [ ${#existing_dirs[@]} -eq 0 ]; then
        print_warning "No directories to backup"
        return 0
    fi
    
    # Create tar backup
    if tar -czf "$backup_file" "${existing_dirs[@]}" 2>> "${BACKUP_BASE_DIR}/backup.log"; then
        print_success "File system backup created: $(basename "$backup_file")"
        log_message "File system backup completed successfully"
    else
        print_error "File system backup failed"
        log_message "ERROR: File system backup failed"
        return 1
    fi
    
    # Encrypt if key is provided
    if [ -n "$BACKUP_ENCRYPTION_KEY" ] && command -v gpg &> /dev/null; then
        local encrypted_backup="${backup_file}.gpg"
        if echo "$BACKUP_ENCRYPTION_KEY" | gpg --batch --yes --passphrase-fd 0 \
           --cipher-algo AES256 --compress-algo 1 --symmetric \
           --output "$encrypted_backup" "$backup_file"; then
            rm "$backup_file"
            backup_file="$encrypted_backup"
            print_success "File system backup encrypted"
            log_message "File system backup encrypted successfully"
        fi
    fi
    
    # Calculate backup size and checksum
    local backup_size=$(du -h "$backup_file" | cut -f1)
    local backup_checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
    
    log_message "File system backup details: File=${backup_file}, Size=${backup_size}, SHA256=${backup_checksum}"
    
    # Store backup metadata
    cat > "${backup_file}.meta" << EOF
backup_type=files
backup_date=$backup_date
backup_file=$(basename "$backup_file")
backup_size=$backup_size
backup_checksum=$backup_checksum
directories_backed_up=$(printf '%s,' "${existing_dirs[@]}")
EOF
    
    echo "$backup_file"
}

backup_monitoring_data() {
    print_header "Monitoring Data Backup"
    log_message "Starting monitoring data backup"
    
    local backup_date=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_BASE_DIR}/monitoring/aegis_monitoring_${backup_date}.tar.gz"
    
    # Define monitoring directories to backup
    local monitoring_dirs=(
        "/var/lib/prometheus"
        "/var/lib/grafana"
        "/var/lib/alertmanager"
        "./monitoring"
    )
    
    # Create file list for existing directories
    local existing_dirs=()
    for dir in "${monitoring_dirs[@]}"; do
        if [ -e "$dir" ]; then
            existing_dirs+=("$dir")
        fi
    done
    
    if [ ${#existing_dirs[@]} -eq 0 ]; then
        print_warning "No monitoring directories to backup"
        return 0
    fi
    
    # Create monitoring backup
    if tar -czf "$backup_file" "${existing_dirs[@]}" 2>> "${BACKUP_BASE_DIR}/backup.log"; then
        print_success "Monitoring backup created: $(basename "$backup_file")"
        log_message "Monitoring backup completed successfully"
    else
        print_warning "Monitoring backup failed"
        log_message "WARNING: Monitoring backup failed"
        return 0
    fi
    
    # Calculate backup details
    local backup_size=$(du -h "$backup_file" | cut -f1)
    local backup_checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
    
    log_message "Monitoring backup details: File=${backup_file}, Size=${backup_size}, SHA256=${backup_checksum}"
    
    echo "$backup_file"
}

upload_to_s3() {
    local backup_file="$1"
    
    if [ -z "$AWS_S3_BUCKET" ] || ! command -v aws &> /dev/null; then
        return 0
    fi
    
    print_header "Uploading to S3"
    log_message "Starting S3 upload: $(basename "$backup_file")"
    
    local s3_key="aegis-backups/$(date '+%Y/%m/%d')/$(basename "$backup_file")"
    
    if aws s3 cp "$backup_file" "s3://$AWS_S3_BUCKET/$s3_key" \
       --storage-class STANDARD_IA \
       --server-side-encryption AES256 2>> "${BACKUP_BASE_DIR}/backup.log"; then
        print_success "Uploaded to S3: s3://$AWS_S3_BUCKET/$s3_key"
        log_message "S3 upload completed: $s3_key"
        
        # Upload metadata
        local meta_file="${backup_file}.meta"
        if [ -f "$meta_file" ]; then
            aws s3 cp "$meta_file" "s3://$AWS_S3_BUCKET/${s3_key}.meta"
        fi
    else
        print_error "S3 upload failed"
        log_message "ERROR: S3 upload failed for $(basename "$backup_file")"
        return 1
    fi
}

cleanup_old_backups() {
    print_header "Cleaning Up Old Backups"
    log_message "Starting cleanup of backups older than $BACKUP_RETENTION_DAYS days"
    
    local cleanup_dirs=("${BACKUP_BASE_DIR}/database" "${BACKUP_BASE_DIR}/files" "${BACKUP_BASE_DIR}/monitoring")
    
    for dir in "${cleanup_dirs[@]}"; do
        if [ -d "$dir" ]; then
            local deleted_count=$(find "$dir" -type f -mtime +$BACKUP_RETENTION_DAYS -delete -print | wc -l)
            if [ "$deleted_count" -gt 0 ]; then
                print_success "Deleted $deleted_count old backup files from $(basename "$dir")"
                log_message "Cleanup: Deleted $deleted_count files from $(basename "$dir")"
            fi
        fi
    done
    
    # Clean up old log files
    if [ -f "${BACKUP_BASE_DIR}/backup.log" ]; then
        # Keep last 1000 lines
        tail -n 1000 "${BACKUP_BASE_DIR}/backup.log" > "${BACKUP_BASE_DIR}/backup.log.tmp"
        mv "${BACKUP_BASE_DIR}/backup.log.tmp" "${BACKUP_BASE_DIR}/backup.log"
    fi
}

send_notification() {
    local status="$1"
    local details="$2"
    
    if [ -z "$BACKUP_NOTIFICATION_EMAIL" ]; then
        return 0
    fi
    
    local subject="Aegis Backup Report - $status"
    local body="Aegis Platform Backup Report
    
Date: $(date)
Status: $status
Server: $(hostname)

$details

Log Location: ${BACKUP_BASE_DIR}/backup.log
"
    
    # Try to send email notification
    if command -v mail &> /dev/null; then
        echo "$body" | mail -s "$subject" "$BACKUP_NOTIFICATION_EMAIL"
        print_success "Notification sent to $BACKUP_NOTIFICATION_EMAIL"
    elif command -v sendmail &> /dev/null; then
        {
            echo "Subject: $subject"
            echo "To: $BACKUP_NOTIFICATION_EMAIL"
            echo ""
            echo "$body"
        } | sendmail "$BACKUP_NOTIFICATION_EMAIL"
        print_success "Notification sent via sendmail"
    else
        print_warning "No email system available for notifications"
    fi
}

create_backup_report() {
    local backup_files=("$@")
    local total_size=0
    local report=""
    
    report+="Backup Summary:\\n"
    report+="=============\\n\\n"
    
    for backup_file in "${backup_files[@]}"; do
        if [ -f "$backup_file" ]; then
            local size=$(du -h "$backup_file" | cut -f1)
            local type=$(basename "$(dirname "$backup_file")")
            report+="- $type: $(basename "$backup_file") ($size)\\n"
            
            # Add checksum if metadata exists
            local meta_file="${backup_file}.meta"
            if [ -f "$meta_file" ]; then
                local checksum=$(grep "backup_checksum" "$meta_file" | cut -d'=' -f2)
                report+="  Checksum: $checksum\\n"
            fi
        fi
    done
    
    echo -e "$report"
}

main() {
    print_header "Aegis Platform Backup System"
    log_message "Starting backup process"
    
    local backup_start_time=$(date +%s)
    local backup_files=()
    local backup_status="SUCCESS"
    local error_details=""
    
    # Check requirements
    check_requirements
    
    # Perform backups
    set +e  # Don't exit on error, collect all errors
    
    # Database backup
    if db_backup=$(backup_database); then
        backup_files+=("$db_backup")
    else
        backup_status="PARTIAL_FAILURE"
        error_details+="Database backup failed. "
    fi
    
    # File system backup
    if files_backup=$(backup_files); then
        backup_files+=("$files_backup")
    else
        backup_status="PARTIAL_FAILURE" 
        error_details+="File system backup failed. "
    fi
    
    # Monitoring data backup
    if monitoring_backup=$(backup_monitoring_data); then
        backup_files+=("$monitoring_backup")
    else
        print_warning "Monitoring backup failed (non-critical)"
    fi
    
    set -e
    
    # Upload to S3 if configured
    for backup_file in "${backup_files[@]}"; do
        upload_to_s3 "$backup_file" || {
            backup_status="PARTIAL_FAILURE"
            error_details+="S3 upload failed for $(basename "$backup_file"). "
        }
    done
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Calculate backup duration
    local backup_end_time=$(date +%s)
    local backup_duration=$((backup_end_time - backup_start_time))
    
    # Create and display report
    local report=$(create_backup_report "${backup_files[@]}")
    report+="\\nBackup Duration: ${backup_duration} seconds\\n"
    report+="Status: $backup_status\\n"
    
    if [ -n "$error_details" ]; then
        report+="Errors: $error_details\\n"
    fi
    
    echo -e "$report"
    log_message "Backup process completed with status: $backup_status"
    log_message "Backup duration: ${backup_duration} seconds"
    
    # Send notification
    send_notification "$backup_status" "$report"
    
    print_header "Backup Process Complete"
    
    if [ "$backup_status" = "SUCCESS" ]; then
        print_success "All backups completed successfully"
        exit 0
    else
        print_warning "Some backups failed - check logs for details"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --database-only)
        backup_database
        exit 0
        ;;
    --files-only)
        backup_files
        exit 0
        ;;
    --monitoring-only)
        backup_monitoring_data
        exit 0
        ;;
    --cleanup-only)
        cleanup_old_backups
        exit 0
        ;;
    --help)
        echo "Usage: $0 [--database-only|--files-only|--monitoring-only|--cleanup-only]"
        echo ""
        echo "Environment Variables:"
        echo "  BACKUP_BASE_DIR           Base directory for backups (default: /var/backups/aegis)"
        echo "  BACKUP_RETENTION_DAYS     Days to keep backups (default: 30)"
        echo "  BACKUP_ENCRYPTION_KEY     Key for encrypting backups"
        echo "  AWS_S3_BUCKET            S3 bucket for offsite backups"
        echo "  BACKUP_NOTIFICATION_EMAIL Email for backup notifications"
        echo ""
        echo "Database Environment Variables:"
        echo "  POSTGRES_HOST            Database host"
        echo "  POSTGRES_PORT            Database port"
        echo "  POSTGRES_DB              Database name"
        echo "  POSTGRES_USER            Database user"
        echo "  POSTGRES_PASSWORD        Database password"
        exit 0
        ;;
    *)
        main
        ;;
esac