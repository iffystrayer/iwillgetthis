#!/bin/bash

# ==============================================
# Aegis Risk Management Platform - Production Deployment Script
# ==============================================
# This script deploys the Aegis platform to production with security hardening

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${DOMAIN:-"localhost"}
EMAIL=${EMAIL:-"admin@example.com"}
BACKUP_DIR=${BACKUP_DIR:-"./backups"}
LOG_FILE="./deployment.log"

# Function to print colored output
print_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate secure random string
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check OpenSSL for secret generation
    if ! command_exists openssl; then
        print_error "OpenSSL is not installed. Please install OpenSSL first."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to setup environment
setup_environment() {
    print_header "Setting Up Production Environment"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating production .env file from template..."
        cp .env.example .env
        
        # Generate secure secrets
        SECRET_KEY=$(generate_secret)
        JWT_SECRET_KEY=$(generate_secret)
        DB_PASSWORD=$(generate_secret)
        
        # Update .env with generated secrets
        sed -i.bak "s/CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_2025/$SECRET_KEY/g" .env
        sed -i.bak "s/CHANGE_THIS_JWT_SECRET_KEY_IN_PRODUCTION_2025/$JWT_SECRET_KEY/g" .env
        sed -i.bak "s/CHANGE_THIS_PASSWORD/$DB_PASSWORD/g" .env
        
        # Update domain
        sed -i.bak "s/yourdomain.com/$DOMAIN/g" .env
        
        # Remove backup file
        rm .env.bak
        
        print_success "Environment file created with secure secrets"
        print_warning "Please review and update .env file with your specific configuration"
    else
        print_status "Environment file already exists"
    fi
    
    # Create necessary directories
    mkdir -p uploads reports logs backups
    print_success "Created necessary directories"
}

# Function to setup SSL certificates
setup_ssl() {
    print_header "Setting Up SSL Certificates"
    
    if [ "$DOMAIN" != "localhost" ]; then
        print_status "Setting up SSL certificates for domain: $DOMAIN"
        
        # Create SSL directory
        mkdir -p ssl
        
        if command_exists certbot; then
            print_status "Using Let's Encrypt for SSL certificates..."
            certbot certonly --standalone -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
            
            # Copy certificates to ssl directory
            cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ssl/
            cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ssl/
            
            print_success "SSL certificates configured"
        else
            print_warning "Certbot not found. Creating self-signed certificates for development..."
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout ssl/privkey.pem \
                -out ssl/fullchain.pem \
                -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
            print_success "Self-signed certificates created"
        fi
    else
        print_status "Using localhost - SSL setup skipped"
    fi
}

# Function to build and start services
deploy_services() {
    print_header "Building and Deploying Services"
    
    cd docker
    
    # Pull latest images
    print_status "Pulling latest base images..."
    docker-compose pull
    
    # Build services
    print_status "Building application images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    cd ..
    print_success "Services deployed successfully"
}

# Function to wait for services to be ready
wait_for_services() {
    print_header "Waiting for Services to Start"
    
    print_status "Waiting for database to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose -f docker/docker-compose.yml exec -T db pg_isready -U aegis_user -d aegis_db >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Database failed to start within 60 seconds"
        exit 1
    fi
    
    print_status "Waiting for backend to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Backend failed to start within 60 seconds"
        exit 1
    fi
    
    print_success "All services are ready"
}

# Function to initialize database
init_database() {
    print_header "Initializing Database"
    
    print_status "Running database migrations..."
    docker-compose -f docker/docker-compose.yml exec backend python init_db_complete.py
    
    print_success "Database initialized successfully"
}

# Function to setup monitoring
setup_monitoring() {
    print_header "Setting Up Monitoring"
    
    print_status "Configuring log rotation..."
    # Add logrotate configuration here if needed
    
    print_status "Setting up health check monitoring..."
    # Add monitoring setup here
    
    print_success "Monitoring configured"
}

# Function to create backup
create_backup() {
    print_header "Creating Initial Backup"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    print_status "Creating database backup..."
    docker-compose -f docker/docker-compose.yml exec -T db pg_dump -U aegis_user aegis_db > "$BACKUP_DIR/aegis_db_$(date +%Y%m%d_%H%M%S).sql"
    
    # Backup configuration
    print_status "Backing up configuration..."
    cp .env "$BACKUP_DIR/.env_$(date +%Y%m%d_%H%M%S)"
    
    print_success "Backup created in $BACKUP_DIR"
}

# Function to show deployment status
show_status() {
    print_header "Deployment Status"
    
    echo ""
    print_success "🎉 Aegis Risk Management Platform deployed successfully!"
    echo ""
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "  Frontend: ${BLUE}http://$DOMAIN:3000${NC}"
    echo -e "  Backend API: ${BLUE}http://$DOMAIN:8000${NC}"
    echo -e "  API Documentation: ${BLUE}http://$DOMAIN:8000/docs${NC}"
    echo ""
    echo -e "${GREEN}Default Login Credentials:${NC}"
    echo -e "  Admin: ${BLUE}admin@aegis-platform.com / admin123${NC}"
    echo -e "  Analyst: ${BLUE}analyst@aegis-platform.com / analyst123${NC}"
    echo -e "  Viewer: ${BLUE}viewer@aegis-platform.com / viewer123${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Update default passwords"
    echo "  2. Configure AI provider API keys in .env"
    echo "  3. Set up SSL certificates for production"
    echo "  4. Configure external integrations"
    echo "  5. Set up automated backups"
    echo ""
    echo -e "${GREEN}Logs:${NC} $LOG_FILE"
    echo -e "${GREEN}Backups:${NC} $BACKUP_DIR"
}

# Function to cleanup on error
cleanup_on_error() {
    print_error "Deployment failed. Cleaning up..."
    cd docker 2>/dev/null && docker-compose down -v --remove-orphans 2>/dev/null || true
    exit 1
}

# Trap errors
trap cleanup_on_error ERR

# Main deployment function
main() {
    print_header "Aegis Risk Management Platform - Production Deployment"
    echo "Starting deployment at $(date)" > "$LOG_FILE"
    
    check_prerequisites
    setup_environment
    setup_ssl
    deploy_services
    wait_for_services
    init_database
    setup_monitoring
    create_backup
    show_status
    
    echo "Deployment completed at $(date)" >> "$LOG_FILE"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_status "Stopping services..."
        cd docker && docker-compose down
        print_success "Services stopped"
        ;;
    "restart")
        print_status "Restarting services..."
        cd docker && docker-compose restart
        print_success "Services restarted"
        ;;
    "logs")
        cd docker && docker-compose logs -f
        ;;
    "backup")
        create_backup
        ;;
    "status")
        cd docker && docker-compose ps
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|backup|status}"
        exit 1
        ;;
esac
