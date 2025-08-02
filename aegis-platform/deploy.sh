#!/bin/bash

# Aegis Risk Management Platform - Production Deployment Script
# This script deploys the complete Aegis platform using Docker Compose

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning "No .env file found. Copying from .env.example"
            cp .env.example .env
            print_warning "Please edit .env file with your configuration before proceeding"
            print_warning "Press any key to continue after editing .env file..."
            read -n 1 -s
        else
            print_error "No .env.example file found. Cannot setup environment."
            exit 1
        fi
    fi
    
    # Source environment variables
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
        print_success "Environment variables loaded"
    fi
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    cd docker
    
    # Build images with no cache for clean build
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
    
    cd ..
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    cd docker
    
    # Start services in detached mode
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
    
    cd ..
}

# Function to wait for services
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker exec aegis-db pg_isready -U aegis_user -d aegis_db >/dev/null 2>&1; then
            print_success "Database is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Database failed to start within timeout"
        exit 1
    fi
    
    # Wait for backend
    print_status "Waiting for backend API..."
    timeout=120
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend API is ready"
            break
        fi
        sleep 3
        timeout=$((timeout - 3))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Backend API failed to start within timeout"
        exit 1
    fi
    
    # Wait for frontend
    print_status "Waiting for frontend..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Frontend failed to start within timeout"
        exit 1
    fi
}

# Function to initialize database
init_database() {
    print_status "Initializing database with seed data..."
    
    # Run database initialization script
    docker exec aegis-backend python init_db_complete.py
    
    if [ $? -eq 0 ]; then
        print_success "Database initialized successfully"
    else
        print_warning "Database initialization may have failed. Check logs."
    fi
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status:"
    
    cd docker
    docker-compose ps
    cd ..
    
    echo
    print_success "🎉 Aegis Risk Management Platform deployed successfully!"
    echo
    print_status "📊 Access URLs:"
    echo "   • Frontend (Web UI):  http://localhost:3000"
    echo "   • Backend API:        http://localhost:8000"
    echo "   • API Documentation:  http://localhost:8000/docs"
    echo "   • Health Check:       http://localhost:8000/health"
    echo
    print_status "🔐 Default Login Credentials:"
    echo "   • Admin:    admin@aegis-platform.com / admin123"
    echo "   • Analyst:  analyst@aegis-platform.com / analyst123"
    echo "   • Viewer:   viewer@aegis-platform.com / viewer123"
    echo
    print_status "📋 Management Commands:"
    echo "   • View logs:       docker-compose -f docker/docker-compose.yml logs -f"
    echo "   • Stop services:   docker-compose -f docker/docker-compose.yml down"
    echo "   • Restart:         docker-compose -f docker/docker-compose.yml restart"
    echo "   • Update:          ./deploy.sh --update"
    echo
}

# Function to update deployment
update_deployment() {
    print_status "Updating deployment..."
    
    cd docker
    
    # Pull latest images and rebuild
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    cd ..
    
    wait_for_services
    print_success "Deployment updated successfully"
}

# Function to show logs
show_logs() {
    cd docker
    docker-compose logs -f
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    cd docker
    docker-compose down
    
    print_success "Services stopped"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    cd docker
    docker-compose down -v --remove-orphans
    docker system prune -f
    
    print_success "Cleanup completed"
}

# Main deployment function
main_deploy() {
    echo "🚀 Aegis Risk Management Platform - Production Deployment"
    echo "========================================================"
    echo
    
    check_prerequisites
    setup_environment
    build_images
    start_services
    wait_for_services
    init_database
    show_status
}

# Parse command line arguments
case "${1:-}" in
    --update)
        update_deployment
        ;;
    --logs)
        show_logs
        ;;
    --stop)
        stop_services
        ;;
    --cleanup)
        cleanup
        ;;
    --status)
        cd docker
        docker-compose ps
        ;;
    --help)
        echo "Usage: $0 [OPTION]"
        echo "Deploy and manage Aegis Risk Management Platform"
        echo
        echo "Options:"
        echo "  (no args)    Deploy the platform"
        echo "  --update     Update existing deployment"
        echo "  --logs       Show service logs"
        echo "  --stop       Stop all services"
        echo "  --status     Show service status"
        echo "  --cleanup    Stop services and clean up"
        echo "  --help       Show this help message"
        ;;
    "")
        main_deploy
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
