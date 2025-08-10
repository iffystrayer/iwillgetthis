#!/bin/bash
# ==============================================
# Aegis Platform - Comprehensive Restore System
# ==============================================
# Disaster recovery and restore capabilities for:
# - Database restoration (PostgreSQL)
# - File system restoration (uploads, configs)
# - Point-in-time recovery
# - System state restoration
# ==============================================

set -e

# Configuration
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/var/backups/aegis}"
RESTORE_DATE="${RESTORE_DATE:-latest}"
BACKUP_ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"
AWS_S3_BUCKET="${AWS_S3_BUCKET:-}"
RESTORE_CONFIRMATION="${RESTORE_CONFIRMATION:-false}"

# Database configuration
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-aegis_production}"
DB_USER="${POSTGRES_USER:-aegis_user}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"
DB_SUPERUSER="${POSTGRES_SUPERUSER:-postgres}"
DB_SUPERUSER_PASSWORD="${POSTGRES_SUPERUSER_PASSWORD:-}"

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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${BACKUP_BASE_DIR}/restore.log"
}

confirm_restore() {
    local restore_type="$1"
    local backup_file="$2"
    
    if [ "$RESTORE_CONFIRMATION" != "true" ]; then
        print_warning "This will restore $restore_type from backup: $(basename "$backup_file")"
        print_warning "This operation will OVERWRITE existing data!"
        echo ""
        read -p "Are you sure you want to continue? (yes/no): " confirm
        
        if [ "$confirm" != "yes" ]; then
            print_error "Restore cancelled by user"
            exit 1
        fi
    fi
    
    log_message "Restore confirmed for $restore_type: $(basename "$backup_file")"
}

check_requirements() {
    print_header "Checking Restore Requirements"
    
    # Check required tools
    local required_tools=("psql" "pg_restore" "tar" "gzip")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check optional tools
    if command -v gpg &> /dev/null; then
        print_success "GPG available for decryption"
    else
        print_warning "GPG not available - encrypted backups cannot be restored"
    fi
    
    if command -v aws &> /dev/null; then
        print_success "AWS CLI available for S3 downloads"
    else
        print_warning "AWS CLI not available - cannot download from S3"
    fi
    
    # Create restore working directory
    mkdir -p "${BACKUP_BASE_DIR}/temp"
    
    print_success "Requirements check completed"
}

list_available_backups() {
    local backup_type="$1"
    
    print_header "Available $backup_type Backups"
    
    local backup_dir="${BACKUP_BASE_DIR}/$backup_type"
    
    if [ ! -d "$backup_dir" ]; then
        print_warning "No local $backup_type backups found"
        return 1
    fi
    
    echo "Local backups:"
    local count=0
    for backup in "$backup_dir"/*; do
        if [ -f "$backup" ] && [[ "$backup" != *.meta ]] && [[ "$backup" != *.log ]]; then
            count=$((count + 1))
            local backup_name=$(basename "$backup")
            local backup_date=$(echo "$backup_name" | grep -o '[0-9]\{8\}_[0-9]\{6\}' || echo "unknown")
            local backup_size=$(du -h "$backup" | cut -f1)
            
            echo "  $count) $backup_name (Date: $backup_date, Size: $backup_size)"
            
            # Show metadata if available
            local meta_file="${backup}.meta"
            if [ -f "$meta_file" ]; then
                local checksum=$(grep "backup_checksum" "$meta_file" 2>/dev/null | cut -d'=' -f2 || echo "N/A")
                echo "     Checksum: $checksum"
            fi
        fi
    done
    
    if [ $count -eq 0 ]; then
        print_warning "No $backup_type backup files found"
        return 1
    fi
    
    return 0
}

find_backup_file() {
    local backup_type="$1"
    local date_pattern="$2"
    
    local backup_dir="${BACKUP_BASE_DIR}/$backup_type"
    
    if [ "$date_pattern" = "latest" ]; then
        # Find the most recent backup
        local latest_backup=$(find "$backup_dir" -type f -name "*.sql.gz*" -o -name "*.tar.gz*" | \
                            grep -v "\.meta$" | sort -r | head -n 1)
        
        if [ -n "$latest_backup" ] && [ -f "$latest_backup" ]; then
            echo "$latest_backup"
            return 0
        fi
    else
        # Find backup matching date pattern
        local matching_backup=$(find "$backup_dir" -type f -name "*${date_pattern}*" | \
                              grep -v "\.meta$" | head -n 1)
        
        if [ -n "$matching_backup" ] && [ -f "$matching_backup" ]; then
            echo "$matching_backup"
            return 0
        fi
    fi
    
    return 1
}

download_from_s3() {
    local backup_type="$1"
    local date_pattern="$2"
    
    if [ -z "$AWS_S3_BUCKET" ] || ! command -v aws &> /dev/null; then
        return 1
    fi
    
    print_header "Searching S3 for Backups"
    log_message "Searching S3 bucket: $AWS_S3_BUCKET"
    
    # List available backups in S3
    local s3_backups=$(aws s3 ls "s3://$AWS_S3_BUCKET/aegis-backups/" --recursive | \
                      grep "$backup_type" | grep -v "\.meta$" | sort -r)
    
    if [ -z "$s3_backups" ]; then
        print_warning "No $backup_type backups found in S3"
        return 1
    fi
    
    echo "Available S3 backups:"
    echo "$s3_backups"
    
    # Find appropriate backup
    local s3_key=""
    if [ "$date_pattern" = "latest" ]; then
        s3_key=$(echo "$s3_backups" | head -n 1 | awk '{print $4}')
    else
        s3_key=$(echo "$s3_backups" | grep "$date_pattern" | head -n 1 | awk '{print $4}')
    fi
    
    if [ -z "$s3_key" ]; then
        print_error "No matching backup found in S3"
        return 1
    fi
    
    # Download backup
    local local_file="${BACKUP_BASE_DIR}/temp/$(basename "$s3_key")"
    print_warning "Downloading from S3: $s3_key"
    
    if aws s3 cp "s3://$AWS_S3_BUCKET/$s3_key" "$local_file"; then
        print_success "Downloaded: $(basename "$local_file")"
        log_message "S3 download completed: $s3_key"
        echo "$local_file"
        return 0
    else
        print_error "S3 download failed"
        return 1
    fi
}

decrypt_backup() {
    local encrypted_file="$1"
    
    if [[ "$encrypted_file" != *.gpg ]]; then
        echo "$encrypted_file"
        return 0
    fi
    
    if [ -z "$BACKUP_ENCRYPTION_KEY" ]; then
        print_error "Backup is encrypted but no decryption key provided"
        print_error "Set BACKUP_ENCRYPTION_KEY environment variable"
        exit 1
    fi
    
    if ! command -v gpg &> /dev/null; then
        print_error "GPG not available for decryption"
        exit 1
    fi
    
    print_warning "Decrypting backup file"
    local decrypted_file="${encrypted_file%.gpg}"
    
    if echo "$BACKUP_ENCRYPTION_KEY" | gpg --batch --yes --passphrase-fd 0 \
       --decrypt --output "$decrypted_file" "$encrypted_file"; then
        print_success "Backup decrypted successfully"
        echo "$decrypted_file"
        return 0
    else
        print_error "Decryption failed"
        exit 1
    fi
}

decompress_backup() {
    local compressed_file="$1"
    
    if [[ "$compressed_file" != *.gz ]]; then
        echo "$compressed_file"
        return 0
    fi
    
    print_warning "Decompressing backup file"
    
    if gzip -dc "$compressed_file" > "${compressed_file%.gz}"; then
        print_success "Backup decompressed successfully"
        echo "${compressed_file%.gz}"
        return 0
    else
        print_error "Decompression failed"
        exit 1
    fi
}

verify_backup_integrity() {
    local backup_file="$1"
    local meta_file="${backup_file}.meta"
    
    if [ ! -f "$meta_file" ]; then
        print_warning "No metadata file found - skipping integrity check"
        return 0
    fi
    
    print_warning "Verifying backup integrity"
    
    local expected_checksum=$(grep "backup_checksum" "$meta_file" | cut -d'=' -f2)
    if [ -z "$expected_checksum" ]; then
        print_warning "No checksum in metadata - skipping verification"
        return 0
    fi
    
    local actual_checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
    
    if [ "$expected_checksum" = "$actual_checksum" ]; then
        print_success "Backup integrity verified"
        return 0
    else
        print_error "Backup integrity check failed!"
        print_error "Expected: $expected_checksum"
        print_error "Actual:   $actual_checksum"
        return 1
    fi
}

restore_database() {
    local backup_file="$1"
    
    print_header "Database Restoration"
    confirm_restore "database" "$backup_file"
    
    # Find or download backup
    if [ ! -f "$backup_file" ]; then
        print_warning "Backup file not found locally, checking S3..."
        if ! backup_file=$(download_from_s3 "database" "$RESTORE_DATE"); then
            print_error "Could not find database backup"
            exit 1
        fi
    fi
    
    # Decrypt if needed
    backup_file=$(decrypt_backup "$backup_file")
    
    # Verify integrity
    if ! verify_backup_integrity "$backup_file"; then
        print_error "Backup integrity verification failed"
        exit 1
    fi
    
    # Decompress if needed
    local sql_file=$(decompress_backup "$backup_file")
    
    # Set PostgreSQL passwords
    export PGPASSWORD="$DB_SUPERUSER_PASSWORD"
    
    # Stop application services to prevent connections
    print_warning "Stopping application services"
    docker-compose down aegis-backend || print_warning "Backend service not running"
    
    # Terminate existing connections
    print_warning "Terminating existing database connections"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" || true
    
    # Drop and recreate database
    print_warning "Recreating database"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    
    # Restore database
    print_warning "Restoring database from backup"
    log_message "Starting database restoration from: $(basename "$sql_file")"
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_SUPERUSER" -d "$DB_NAME" -f "$sql_file" \
       2>> "${BACKUP_BASE_DIR}/restore.log"; then
        print_success "Database restored successfully"
        log_message "Database restoration completed successfully"
    else
        print_error "Database restoration failed"
        log_message "ERROR: Database restoration failed"
        exit 1
    fi
    
    # Update database statistics
    print_warning "Updating database statistics"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "ANALYZE;" || true
    
    # Start application services
    print_warning "Starting application services"
    docker-compose up -d aegis-backend
    
    # Cleanup temporary files
    rm -f "$sql_file"
    if [ "$backup_file" != "$1" ]; then
        rm -f "$backup_file"
    fi
    
    print_success "Database restoration completed"
}

restore_files() {
    local backup_file="$1"
    local restore_path="${2:-/}"
    
    print_header "File System Restoration"
    confirm_restore "files" "$backup_file"
    
    # Find or download backup
    if [ ! -f "$backup_file" ]; then
        print_warning "Backup file not found locally, checking S3..."
        if ! backup_file=$(download_from_s3 "files" "$RESTORE_DATE"); then
            print_error "Could not find file system backup"
            exit 1
        fi
    fi
    
    # Decrypt if needed
    backup_file=$(decrypt_backup "$backup_file")
    
    # Verify integrity
    if ! verify_backup_integrity "$backup_file"; then
        print_error "Backup integrity verification failed"
        exit 1
    fi
    
    # Stop services that might be using files
    print_warning "Stopping services for file restoration"
    docker-compose down || print_warning "Services not running"
    
    # Create backup of current files
    local current_backup="/tmp/current_files_$(date +%Y%m%d_%H%M%S).tar.gz"
    print_warning "Creating backup of current files to: $current_backup"
    tar -czf "$current_backup" /app/uploads /app/logs /app/config 2>/dev/null || true
    
    # Restore files
    print_warning "Restoring files from backup"
    log_message "Starting file restoration from: $(basename "$backup_file")"
    
    if tar -xzf "$backup_file" -C "$restore_path" 2>> "${BACKUP_BASE_DIR}/restore.log"; then
        print_success "Files restored successfully"
        log_message "File restoration completed successfully"
    else
        print_error "File restoration failed"
        log_message "ERROR: File restoration failed"
        
        # Restore from current backup
        print_warning "Restoring previous files"
        tar -xzf "$current_backup" -C "$restore_path" || true
        exit 1
    fi
    
    # Fix permissions
    print_warning "Fixing file permissions"
    chown -R 1000:1000 /app/uploads 2>/dev/null || true
    chown -R 1000:1000 /app/logs 2>/dev/null || true
    
    # Start services
    print_warning "Starting services"
    docker-compose up -d
    
    # Cleanup
    if [ "$backup_file" != "$1" ]; then
        rm -f "$backup_file"
    fi
    
    print_success "File system restoration completed"
    print_warning "Previous files backed up to: $current_backup"
}

restore_monitoring() {
    local backup_file="$1"
    
    print_header "Monitoring Data Restoration"
    confirm_restore "monitoring data" "$backup_file"
    
    # Find or download backup
    if [ ! -f "$backup_file" ]; then
        print_warning "Backup file not found locally, checking S3..."
        if ! backup_file=$(download_from_s3 "monitoring" "$RESTORE_DATE"); then
            print_error "Could not find monitoring backup"
            exit 1
        fi
    fi
    
    # Decrypt if needed
    backup_file=$(decrypt_backup "$backup_file")
    
    # Stop monitoring services
    print_warning "Stopping monitoring services"
    docker-compose -f monitoring/docker-compose.monitoring.yml down || true
    
    # Restore monitoring data
    print_warning "Restoring monitoring data"
    log_message "Starting monitoring restoration from: $(basename "$backup_file")"
    
    if tar -xzf "$backup_file" -C / 2>> "${BACKUP_BASE_DIR}/restore.log"; then
        print_success "Monitoring data restored successfully"
        log_message "Monitoring restoration completed successfully"
    else
        print_error "Monitoring restoration failed"
        log_message "ERROR: Monitoring restoration failed"
        exit 1
    fi
    
    # Start monitoring services
    print_warning "Starting monitoring services"
    docker-compose -f monitoring/docker-compose.monitoring.yml up -d
    
    # Cleanup
    if [ "$backup_file" != "$1" ]; then
        rm -f "$backup_file"
    fi
    
    print_success "Monitoring restoration completed"
}

show_restore_status() {
    print_header "Restore Status Summary"
    
    echo "Restore completed at: $(date)"
    echo "Restore logs: ${BACKUP_BASE_DIR}/restore.log"
    
    # Check service status
    print_warning "Checking service status..."
    docker-compose ps
    
    # Check database connectivity
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt" &>/dev/null; then
        print_success "Database is accessible"
    else
        print_error "Database connection failed"
    fi
    
    # Check web service
    if curl -f -s http://localhost:8000/health &>/dev/null; then
        print_success "Web service is responding"
    else
        print_warning "Web service may not be ready yet"
    fi
}

main() {
    print_header "Aegis Platform Restore System"
    log_message "Starting restore process for: $RESTORE_DATE"
    
    check_requirements
    
    case "${1:-full}" in
        database)
            local backup_file="${2:-}"
            if [ -z "$backup_file" ]; then
                if ! backup_file=$(find_backup_file "database" "$RESTORE_DATE"); then
                    list_available_backups "database" || exit 1
                    echo
                    read -p "Enter backup number or filename: " selection
                    # Handle user selection logic here
                    exit 1
                fi
            fi
            restore_database "$backup_file"
            ;;
            
        files)
            local backup_file="${2:-}"
            if [ -z "$backup_file" ]; then
                if ! backup_file=$(find_backup_file "files" "$RESTORE_DATE"); then
                    list_available_backups "files" || exit 1
                    exit 1
                fi
            fi
            restore_files "$backup_file"
            ;;
            
        monitoring)
            local backup_file="${2:-}"
            if [ -z "$backup_file" ]; then
                if ! backup_file=$(find_backup_file "monitoring" "$RESTORE_DATE"); then
                    list_available_backups "monitoring" || exit 1
                    exit 1
                fi
            fi
            restore_monitoring "$backup_file"
            ;;
            
        list)
            list_available_backups "database"
            list_available_backups "files"
            list_available_backups "monitoring"
            ;;
            
        full|*)
            print_warning "Performing full system restore"
            
            # Restore database
            if db_backup=$(find_backup_file "database" "$RESTORE_DATE"); then
                restore_database "$db_backup"
            else
                print_error "No database backup found for restore date: $RESTORE_DATE"
                exit 1
            fi
            
            # Restore files
            if files_backup=$(find_backup_file "files" "$RESTORE_DATE"); then
                restore_files "$files_backup"
            else
                print_warning "No file backup found for restore date: $RESTORE_DATE"
            fi
            
            # Restore monitoring (optional)
            if monitoring_backup=$(find_backup_file "monitoring" "$RESTORE_DATE"); then
                restore_monitoring "$monitoring_backup"
            else
                print_warning "No monitoring backup found for restore date: $RESTORE_DATE"
            fi
            ;;
    esac
    
    show_restore_status
    
    print_header "Restore Process Complete"
    print_success "System restore completed successfully"
    log_message "Restore process completed successfully"
}

# Handle command line arguments
case "${1:-}" in
    --help)
        echo "Usage: $0 [database|files|monitoring|full|list] [backup_file]"
        echo ""
        echo "Commands:"
        echo "  database     Restore database only"
        echo "  files        Restore file system only"
        echo "  monitoring   Restore monitoring data only"
        echo "  full         Full system restore (default)"
        echo "  list         List available backups"
        echo ""
        echo "Environment Variables:"
        echo "  RESTORE_DATE              Date pattern or 'latest' (default: latest)"
        echo "  BACKUP_BASE_DIR           Base directory for backups"
        echo "  BACKUP_ENCRYPTION_KEY     Key for decrypting backups"
        echo "  AWS_S3_BUCKET            S3 bucket for backups"
        echo "  RESTORE_CONFIRMATION      Skip confirmation prompts (true/false)"
        echo ""
        echo "Database Environment Variables:"
        echo "  POSTGRES_HOST            Database host"
        echo "  POSTGRES_PORT            Database port"
        echo "  POSTGRES_DB              Database name"
        echo "  POSTGRES_USER            Database user"
        echo "  POSTGRES_PASSWORD        Database password"
        echo "  POSTGRES_SUPERUSER       Database superuser"
        echo "  POSTGRES_SUPERUSER_PASSWORD Database superuser password"
        echo ""
        echo "Examples:"
        echo "  $0 database                              # Restore latest database backup"
        echo "  $0 files /path/to/backup.tar.gz         # Restore specific file backup"
        echo "  RESTORE_DATE=20240110 $0 full            # Restore from specific date"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac