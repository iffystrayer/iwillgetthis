#!/bin/bash
# ==============================================
# Aegis Platform - Deployment Script
# ==============================================
# Automated deployment script for different environments
# Supports staging, production, and development deployments
# ==============================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEFAULT_ENVIRONMENT="staging"
ENVIRONMENT="${ENVIRONMENT:-$DEFAULT_ENVIRONMENT}"
DRY_RUN="${DRY_RUN:-false}"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-true}"

# Container registry
REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
BACKEND_IMAGE="${REGISTRY}/${GITHUB_REPOSITORY:-aegis}/aegis-backend:${IMAGE_TAG}"
FRONTEND_IMAGE="${REGISTRY}/${GITHUB_REPOSITORY:-aegis}/aegis-frontend:${IMAGE_TAG}"

# Environment-specific configurations
declare -A ENV_CONFIGS
ENV_CONFIGS[development]="docker/docker-compose.yml"
ENV_CONFIGS[staging]="docker/docker-compose.staging.yml"
ENV_CONFIGS[production]="docker/docker-compose.production.yml"

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${PROJECT_ROOT}/deployment.log"
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy Aegis Platform to specified environment.

OPTIONS:
    -e, --environment ENV    Target environment (development|staging|production)
    -t, --tag TAG           Container image tag (default: latest)
    -d, --dry-run           Show what would be deployed without making changes
    -b, --no-backup         Skip backup before deployment
    -r, --no-rollback       Don't rollback on deployment failure
    -c, --config FILE       Custom docker-compose file
    -h, --help              Show this help message

ENVIRONMENT VARIABLES:
    ENVIRONMENT             Target environment (overridden by -e)
    IMAGE_TAG               Container image tag (overridden by -t)
    REGISTRY                Container registry URL
    DRY_RUN                 Set to 'true' for dry run (overridden by -d)
    BACKUP_BEFORE_DEPLOY    Set to 'false' to skip backup (overridden by -b)
    ROLLBACK_ON_FAILURE     Set to 'false' to skip rollback (overridden by -r)

EXAMPLES:
    $0                                      # Deploy to staging with default settings
    $0 -e production -t v1.2.3             # Deploy specific version to production
    $0 -e staging --dry-run                # Show what would be deployed to staging
    $0 -e production -b -r                 # Deploy to production without backup or rollback

EOF
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                BACKEND_IMAGE="${REGISTRY}/${GITHUB_REPOSITORY:-aegis}/aegis-backend:${IMAGE_TAG}"
                FRONTEND_IMAGE="${REGISTRY}/${GITHUB_REPOSITORY:-aegis}/aegis-frontend:${IMAGE_TAG}"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -b|--no-backup)
                BACKUP_BEFORE_DEPLOY="false"
                shift
                ;;
            -r|--no-rollback)
                ROLLBACK_ON_FAILURE="false"
                shift
                ;;
            -c|--config)
                CUSTOM_COMPOSE_FILE="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

validate_environment() {
    print_header "Validating Deployment Environment"
    
    if [[ ! " development staging production " =~ " $ENVIRONMENT " ]]; then
        print_error "Invalid environment: $ENVIRONMENT"
        print_error "Valid environments: development, staging, production"
        exit 1
    fi
    
    # Check if compose file exists
    local compose_file="${CUSTOM_COMPOSE_FILE:-${ENV_CONFIGS[$ENVIRONMENT]}}"
    if [ ! -f "${PROJECT_ROOT}/$compose_file" ]; then
        print_error "Docker compose file not found: $compose_file"
        exit 1
    fi
    
    print_success "Environment validation passed: $ENVIRONMENT"
    log_message "Deployment environment: $ENVIRONMENT"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check required tools
    local required_tools=("docker" "docker-compose" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is required but not installed"
            exit 1
        fi
        print_success "$tool is available"
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    print_success "Docker daemon is running"
    
    # Check environment file
    local env_file="${PROJECT_ROOT}/.env.${ENVIRONMENT}"
    if [ ! -f "$env_file" ]; then
        env_file="${PROJECT_ROOT}/.env"
        if [ ! -f "$env_file" ]; then
            print_error "Environment file not found: .env.${ENVIRONMENT} or .env"
            exit 1
        fi
        print_warning "Using default .env file (consider creating .env.${ENVIRONMENT})"
    else
        print_success "Environment file found: .env.${ENVIRONMENT}"
    fi
    
    # Check container images (for staging/production)
    if [ "$ENVIRONMENT" != "development" ]; then
        print_info "Checking container image availability..."
        if ! docker manifest inspect "$BACKEND_IMAGE" &> /dev/null; then
            print_error "Backend image not found: $BACKEND_IMAGE"
            exit 1
        fi
        if ! docker manifest inspect "$FRONTEND_IMAGE" &> /dev/null; then
            print_error "Frontend image not found: $FRONTEND_IMAGE"
            exit 1
        fi
        print_success "Container images are available"
    fi
    
    log_message "Prerequisites check completed successfully"
}

create_backup() {
    if [ "$BACKUP_BEFORE_DEPLOY" != "true" ]; then
        print_info "Skipping backup (disabled by configuration)"
        return 0
    fi
    
    print_header "Creating Pre-Deployment Backup"
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="${PROJECT_ROOT}/backups/deployment_${backup_timestamp}"
    
    mkdir -p "$backup_dir"
    
    # Backup current environment file
    local current_env="${PROJECT_ROOT}/.env.${ENVIRONMENT}"
    if [ -f "$current_env" ]; then
        cp "$current_env" "$backup_dir/"
        print_success "Environment file backed up"
    fi
    
    # Run application backup script if available
    if [ -f "${PROJECT_ROOT}/scripts/backup-system.sh" ]; then
        print_info "Running comprehensive system backup..."
        if ! BACKUP_BASE_DIR="$backup_dir" "${PROJECT_ROOT}/scripts/backup-system.sh"; then
            print_warning "System backup failed - continuing with deployment"
        else
            print_success "System backup completed"
        fi
    fi
    
    # Store backup information
    echo "BACKUP_DIR=$backup_dir" > "${PROJECT_ROOT}/.last_backup_info"
    echo "BACKUP_TIMESTAMP=$backup_timestamp" >> "${PROJECT_ROOT}/.last_backup_info"
    
    log_message "Pre-deployment backup created: $backup_dir"
    export BACKUP_DIR="$backup_dir"
}

pull_images() {
    if [ "$ENVIRONMENT" = "development" ]; then
        print_info "Skipping image pull for development environment"
        return 0
    fi
    
    print_header "Pulling Container Images"
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "[DRY RUN] Would pull: $BACKEND_IMAGE"
        print_info "[DRY RUN] Would pull: $FRONTEND_IMAGE"
        return 0
    fi
    
    print_info "Pulling backend image: $BACKEND_IMAGE"
    if docker pull "$BACKEND_IMAGE"; then
        print_success "Backend image pulled successfully"
    else
        print_error "Failed to pull backend image"
        exit 1
    fi
    
    print_info "Pulling frontend image: $FRONTEND_IMAGE"
    if docker pull "$FRONTEND_IMAGE"; then
        print_success "Frontend image pulled successfully"
    else
        print_error "Failed to pull frontend image"
        exit 1
    fi
    
    log_message "Container images pulled successfully"
}

deploy_application() {
    print_header "Deploying Application"
    
    local compose_file="${CUSTOM_COMPOSE_FILE:-${ENV_CONFIGS[$ENVIRONMENT]}}"
    local env_file=".env.${ENVIRONMENT}"
    
    if [ ! -f "${PROJECT_ROOT}/$env_file" ]; then
        env_file=".env"
    fi
    
    cd "$PROJECT_ROOT"
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "[DRY RUN] Would deploy with:"
        print_info "[DRY RUN]   Compose file: $compose_file"
        print_info "[DRY RUN]   Environment file: $env_file"
        print_info "[DRY RUN]   Backend image: $BACKEND_IMAGE"
        print_info "[DRY RUN]   Frontend image: $FRONTEND_IMAGE"
        
        print_info "[DRY RUN] Validating compose configuration..."
        docker-compose -f "$compose_file" --env-file "$env_file" config > /dev/null
        print_success "[DRY RUN] Compose configuration is valid"
        return 0
    fi
    
    # Stop existing services gracefully
    print_info "Stopping existing services..."
    docker-compose -f "$compose_file" --env-file "$env_file" down --remove-orphans || true
    
    # Remove old images (except for production)
    if [ "$ENVIRONMENT" != "production" ]; then
        print_info "Cleaning up old images..."
        docker image prune -f || true
    fi
    
    # Start new services
    print_info "Starting new services..."
    export BACKEND_IMAGE FRONTEND_IMAGE
    
    if docker-compose -f "$compose_file" --env-file "$env_file" up -d; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        if [ "$ROLLBACK_ON_FAILURE" = "true" ]; then
            rollback_deployment
        fi
        exit 1
    fi
    
    log_message "Application deployment completed"
}

wait_for_services() {
    print_header "Waiting for Services to be Ready"
    
    local health_endpoints=(
        "http://localhost:${BACKEND_PORT:-30641}/health"
        "http://localhost:${FRONTEND_PORT:-58533}"
    )
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "[DRY RUN] Would wait for services to be ready"
        return 0
    fi
    
    local max_attempts=30
    local attempt=0
    
    for endpoint in "${health_endpoints[@]}"; do
        print_info "Waiting for $endpoint to be ready..."
        
        while [ $attempt -lt $max_attempts ]; do
            if curl -f -s --max-time 5 "$endpoint" > /dev/null 2>&1; then
                print_success "$endpoint is ready"
                break
            fi
            
            attempt=$((attempt + 1))
            print_info "Attempt $attempt/$max_attempts - waiting 10 seconds..."
            sleep 10
        done
        
        if [ $attempt -ge $max_attempts ]; then
            print_error "Service at $endpoint failed to become ready"
            if [ "$ROLLBACK_ON_FAILURE" = "true" ]; then
                rollback_deployment
            fi
            exit 1
        fi
        
        attempt=0
    done
    
    log_message "All services are ready"
}

run_smoke_tests() {
    print_header "Running Smoke Tests"
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "[DRY RUN] Would run smoke tests"
        return 0
    fi
    
    local backend_url="http://localhost:${BACKEND_PORT:-30641}"
    local frontend_url="http://localhost:${FRONTEND_PORT:-58533}"
    
    # Test backend health
    if curl -f -s "$backend_url/health" | grep -q "healthy"; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Test API endpoints
    if curl -f -s "$backend_url/api" > /dev/null; then
        print_success "API endpoint test passed"
    else
        print_error "API endpoint test failed"
        return 1
    fi
    
    # Test frontend
    if curl -f -s "$frontend_url" > /dev/null; then
        print_success "Frontend test passed"
    else
        print_error "Frontend test failed"
        return 1
    fi
    
    # Test database connection (if possible)
    local compose_file="${CUSTOM_COMPOSE_FILE:-${ENV_CONFIGS[$ENVIRONMENT]}}"
    if docker-compose -f "$compose_file" exec -T backend python -c "
from database import engine
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_success "Database connection test passed"
    else
        print_warning "Database connection test failed or skipped"
    fi
    
    log_message "Smoke tests completed successfully"
    return 0
}

rollback_deployment() {
    print_header "Rolling Back Deployment"
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "[DRY RUN] Would rollback deployment"
        return 0
    fi
    
    print_warning "Rolling back to previous version..."
    
    # Load backup information
    if [ -f "${PROJECT_ROOT}/.last_backup_info" ]; then
        source "${PROJECT_ROOT}/.last_backup_info"
        
        if [ -d "$BACKUP_DIR" ]; then
            print_info "Restoring from backup: $BACKUP_DIR"
            
            # Restore environment file
            local backup_env="$BACKUP_DIR/.env.${ENVIRONMENT}"
            if [ -f "$backup_env" ]; then
                cp "$backup_env" "${PROJECT_ROOT}/.env.${ENVIRONMENT}"
                print_success "Environment file restored"
            fi
            
            # Run system restore if backup script is available
            if [ -f "${PROJECT_ROOT}/scripts/restore-system.sh" ]; then
                print_info "Running system restore..."
                RESTORE_CONFIRMATION=true "${PROJECT_ROOT}/scripts/restore-system.sh" || true
            fi
        else
            print_warning "Backup directory not found - cannot restore"
        fi
    else
        print_warning "No backup information found - cannot rollback"
    fi
    
    log_message "Rollback attempt completed"
}

update_monitoring() {
    print_header "Updating Monitoring Systems"
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "[DRY RUN] Would update monitoring systems"
        return 0
    fi
    
    # Update deployment status in monitoring
    local deployment_event=$(cat << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "$ENVIRONMENT",
  "version": "$IMAGE_TAG",
  "status": "deployed",
  "backend_image": "$BACKEND_IMAGE",
  "frontend_image": "$FRONTEND_IMAGE"
}
EOF
)
    
    # Log deployment event
    echo "$deployment_event" >> "${PROJECT_ROOT}/deployments.log"
    
    # Send to monitoring webhook if configured
    if [ -n "$MONITORING_WEBHOOK_URL" ]; then
        curl -s -X POST "$MONITORING_WEBHOOK_URL" \
             -H "Content-Type: application/json" \
             -d "$deployment_event" || true
        print_success "Monitoring systems updated"
    else
        print_info "No monitoring webhook configured"
    fi
    
    log_message "Monitoring systems updated"
}

cleanup_deployment() {
    print_header "Cleaning Up"
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "[DRY RUN] Would clean up deployment artifacts"
        return 0
    fi
    
    # Clean up old containers
    docker system prune -f --volumes=false || true
    
    # Clean up old images (except for production)
    if [ "$ENVIRONMENT" != "production" ]; then
        docker image prune -a -f || true
    fi
    
    print_success "Cleanup completed"
    log_message "Deployment cleanup completed"
}

show_deployment_summary() {
    print_header "Deployment Summary"
    
    cat << EOF
🚀 Deployment Summary
=====================
Environment:     $ENVIRONMENT
Image Tag:       $IMAGE_TAG
Backend Image:   $BACKEND_IMAGE
Frontend Image:  $FRONTEND_IMAGE
Compose File:    ${CUSTOM_COMPOSE_FILE:-${ENV_CONFIGS[$ENVIRONMENT]}}
Backup Created:  $([ "$BACKUP_BEFORE_DEPLOY" = "true" ] && echo "Yes" || echo "No")
Dry Run:         $([ "$DRY_RUN" = "true" ] && echo "Yes" || echo "No")
Deployed At:     $(date)

Service URLs:
- Frontend:      http://localhost:${FRONTEND_PORT:-58533}
- Backend:       http://localhost:${BACKEND_PORT:-30641}
- API Docs:      http://localhost:${BACKEND_PORT:-30641}/docs
- Health Check:  http://localhost:${BACKEND_PORT:-30641}/health

Next Steps:
1. Verify application functionality
2. Run comprehensive tests
3. Monitor application logs
4. Check monitoring dashboards
5. Notify stakeholders of deployment

EOF
    
    log_message "Deployment completed successfully for environment: $ENVIRONMENT"
}

main() {
    print_header "Aegis Platform Deployment"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Main deployment workflow
    validate_environment
    check_prerequisites
    create_backup
    pull_images
    deploy_application
    wait_for_services
    
    # Run tests and validation
    if ! run_smoke_tests; then
        print_error "Smoke tests failed"
        if [ "$ROLLBACK_ON_FAILURE" = "true" ]; then
            rollback_deployment
        fi
        exit 1
    fi
    
    # Post-deployment tasks
    update_monitoring
    cleanup_deployment
    show_deployment_summary
    
    print_header "Deployment Complete"
    print_success "Aegis Platform has been successfully deployed to $ENVIRONMENT"
    
    if [ "$DRY_RUN" = "true" ]; then
        print_info "This was a dry run - no actual changes were made"
    fi
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"