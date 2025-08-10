#!/bin/bash
# ==============================================
# Aegis Platform - SSL/TLS Setup Script
# ==============================================
# This script sets up SSL/TLS certificates for production deployment
#
# Options:
# 1. Self-signed certificates (development/testing)
# 2. Let's Encrypt certificates (production)
# 3. Custom certificate installation
# ==============================================

set -e

# Configuration
DOMAIN="yourdomain.com"
SSL_DIR="/etc/ssl"
CERT_DIR="${SSL_DIR}/certs"
KEY_DIR="${SSL_DIR}/private"
CERT_FILE="${CERT_DIR}/aegis-platform.crt"
KEY_FILE="${KEY_DIR}/aegis-platform.key"
CHAIN_FILE="${CERT_DIR}/aegis-platform-chain.crt"
DH_FILE="${CERT_DIR}/dhparam.pem"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

check_requirements() {
    print_header "Checking Requirements"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root"
        exit 1
    fi
    
    # Create SSL directories
    mkdir -p "${CERT_DIR}" "${KEY_DIR}"
    chmod 755 "${CERT_DIR}"
    chmod 700 "${KEY_DIR}"
    
    print_success "SSL directories created"
}

generate_dhparam() {
    print_header "Generating DH Parameters"
    
    if [ ! -f "${DH_FILE}" ]; then
        print_warning "Generating DH parameters (this may take several minutes)..."
        openssl dhparam -out "${DH_FILE}" 2048
        chmod 644 "${DH_FILE}"
        print_success "DH parameters generated"
    else
        print_success "DH parameters already exist"
    fi
}

setup_self_signed() {
    print_header "Setting Up Self-Signed Certificate"
    
    # Generate private key
    openssl genrsa -out "${KEY_FILE}" 2048
    chmod 600 "${KEY_FILE}"
    
    # Generate certificate
    openssl req -new -x509 -key "${KEY_FILE}" -out "${CERT_FILE}" -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}" \
        -addext "subjectAltName=DNS:${DOMAIN},DNS:*.${DOMAIN},DNS:localhost"
    
    chmod 644 "${CERT_FILE}"
    cp "${CERT_FILE}" "${CHAIN_FILE}"
    
    print_success "Self-signed certificate created"
    print_warning "Self-signed certificates should only be used for development/testing"
}

setup_letsencrypt() {
    print_header "Setting Up Let's Encrypt Certificate"
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        print_warning "Installing certbot..."
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            yum install -y certbot
        else
            print_error "Please install certbot manually"
            exit 1
        fi
    fi
    
    # Generate certificate
    print_warning "Generating Let's Encrypt certificate for ${DOMAIN}"
    print_warning "Make sure DNS is pointing to this server and port 80 is accessible"
    
    certbot certonly --standalone -d "${DOMAIN}" -d "www.${DOMAIN}" \
        --agree-tos --non-interactive --email admin@"${DOMAIN}"
    
    # Copy certificates to our location
    cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "${CERT_FILE}"
    cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" "${KEY_FILE}"
    cp "/etc/letsencrypt/live/${DOMAIN}/chain.pem" "${CHAIN_FILE}"
    
    chmod 644 "${CERT_FILE}" "${CHAIN_FILE}"
    chmod 600 "${KEY_FILE}"
    
    print_success "Let's Encrypt certificate installed"
    
    # Setup auto-renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    print_success "Auto-renewal configured"
}

setup_custom() {
    print_header "Custom Certificate Installation"
    
    echo "Please provide the paths to your certificate files:"
    read -p "Certificate file (.crt): " CUSTOM_CERT
    read -p "Private key file (.key): " CUSTOM_KEY
    read -p "Certificate chain file (.crt): " CUSTOM_CHAIN
    
    if [ ! -f "${CUSTOM_CERT}" ] || [ ! -f "${CUSTOM_KEY}" ]; then
        print_error "Certificate or key file not found"
        exit 1
    fi
    
    # Copy certificates
    cp "${CUSTOM_CERT}" "${CERT_FILE}"
    cp "${CUSTOM_KEY}" "${KEY_FILE}"
    
    if [ -f "${CUSTOM_CHAIN}" ]; then
        cp "${CUSTOM_CHAIN}" "${CHAIN_FILE}"
    else
        cp "${CUSTOM_CERT}" "${CHAIN_FILE}"
    fi
    
    chmod 644 "${CERT_FILE}" "${CHAIN_FILE}"
    chmod 600 "${KEY_FILE}"
    
    print_success "Custom certificate installed"
}

verify_certificate() {
    print_header "Verifying Certificate"
    
    if [ -f "${CERT_FILE}" ] && [ -f "${KEY_FILE}" ]; then
        # Check certificate validity
        openssl x509 -in "${CERT_FILE}" -text -noout | grep -E "(Subject:|DNS:|Not After)"
        
        # Verify certificate and key match
        cert_hash=$(openssl x509 -noout -modulus -in "${CERT_FILE}" | openssl md5)
        key_hash=$(openssl rsa -noout -modulus -in "${KEY_FILE}" | openssl md5)
        
        if [ "${cert_hash}" = "${key_hash}" ]; then
            print_success "Certificate and key match"
        else
            print_error "Certificate and key do not match"
            exit 1
        fi
        
        print_success "Certificate verification completed"
    else
        print_error "Certificate or key file missing"
        exit 1
    fi
}

configure_nginx() {
    print_header "Configuring Nginx"
    
    # Update domain in nginx config
    if [ -f "./nginx/nginx-production.conf" ]; then
        sed -i "s/yourdomain\.com/${DOMAIN}/g" ./nginx/nginx-production.conf
        print_success "Nginx configuration updated with domain ${DOMAIN}"
    else
        print_warning "Nginx configuration file not found in ./nginx/nginx-production.conf"
    fi
}

setup_firewall() {
    print_header "Configuring Firewall"
    
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw --force enable
        print_success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        print_success "FirewallD configured"
    else
        print_warning "No supported firewall found. Please configure manually:"
        print_warning "- Allow port 22 (SSH)"
        print_warning "- Allow port 80 (HTTP)"
        print_warning "- Allow port 443 (HTTPS)"
    fi
}

main() {
    print_header "Aegis Platform SSL/TLS Setup"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --domain)
                DOMAIN="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [--domain yourdomain.com]"
                echo "Options:"
                echo "  --domain DOMAIN   Set the domain name (default: yourdomain.com)"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    check_requirements
    generate_dhparam
    
    echo "Select SSL certificate type:"
    echo "1) Self-signed certificate (development/testing only)"
    echo "2) Let's Encrypt certificate (recommended for production)"
    echo "3) Custom certificate (bring your own)"
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            setup_self_signed
            ;;
        2)
            setup_letsencrypt
            ;;
        3)
            setup_custom
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    verify_certificate
    configure_nginx
    setup_firewall
    
    print_header "SSL/TLS Setup Complete"
    print_success "SSL/TLS certificates have been configured successfully"
    print_success "Domain: ${DOMAIN}"
    print_success "Certificate: ${CERT_FILE}"
    print_success "Private Key: ${KEY_FILE}"
    
    echo ""
    print_warning "Next steps:"
    echo "1. Update your DNS to point to this server"
    echo "2. Deploy the nginx configuration"
    echo "3. Test the SSL configuration at: https://www.ssllabs.com/ssltest/"
    echo "4. Consider implementing Certificate Transparency monitoring"
}

main "$@"