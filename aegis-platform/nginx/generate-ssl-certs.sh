#!/bin/bash

# Aegis Platform - SSL Certificate Generation Script
# This script generates self-signed certificates for development
# For production, replace with certificates from a trusted CA like Let's Encrypt

set -e

CERT_DIR="/Users/ifiokmoses/code/iwillgetthis/aegis-platform/nginx/ssl"
DOMAIN="localhost"
DAYS=365

echo "🔐 Generating SSL certificates for Aegis Platform..."

# Create SSL directory
mkdir -p "$CERT_DIR"

# Generate private key
echo "Generating private key..."
openssl genrsa -out "$CERT_DIR/aegis.key" 2048

# Generate certificate signing request
echo "Generating certificate signing request..."
openssl req -new -key "$CERT_DIR/aegis.key" -out "$CERT_DIR/aegis.csr" -subj "/C=US/ST=State/L=City/O=Aegis/OU=Security/CN=$DOMAIN"

# Generate self-signed certificate
echo "Generating self-signed certificate..."
openssl x509 -req -in "$CERT_DIR/aegis.csr" -signkey "$CERT_DIR/aegis.key" -out "$CERT_DIR/aegis.crt" -days $DAYS

# Generate DH parameters for enhanced security
echo "Generating DH parameters (this may take a few minutes)..."
openssl dhparam -out "$CERT_DIR/dhparam.pem" 2048

# Set appropriate permissions
chmod 600 "$CERT_DIR/aegis.key"
chmod 644 "$CERT_DIR/aegis.crt"
chmod 644 "$CERT_DIR/dhparam.pem"

# Clean up CSR
rm "$CERT_DIR/aegis.csr"

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificates location: $CERT_DIR"
echo ""
echo "📋 Files created:"
echo "  • aegis.crt - SSL certificate"
echo "  • aegis.key - Private key"
echo "  • dhparam.pem - Diffie-Hellman parameters"
echo ""
echo "⚠️  PRODUCTION NOTE:"
echo "   Replace self-signed certificates with trusted CA certificates"
echo "   Consider using Let's Encrypt for free, trusted certificates"
echo ""
echo "🔧 Next steps:"
echo "   1. Update docker-compose.yml to include nginx service"
echo "   2. Start the stack: docker-compose up -d"
echo "   3. Access via: https://localhost"