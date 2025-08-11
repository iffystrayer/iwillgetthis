# Aegis Platform - Production Nginx with SSL/TLS
FROM nginx:alpine

# Install additional tools for security
RUN apk add --no-cache \
    apache2-utils \
    openssl \
    certbot \
    curl \
    tzdata

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy SSL certificates
COPY ssl/aegis.crt /etc/ssl/certs/aegis.crt
COPY ssl/aegis.key /etc/ssl/private/aegis.key
COPY ssl/dhparam.pem /etc/ssl/certs/dhparam.pem

# Copy basic auth file
COPY .htpasswd /etc/nginx/.htpasswd

# Set proper permissions for SSL files
RUN chown -R nginx:nginx /etc/ssl/certs/ /etc/ssl/private/ && \
    chmod 644 /etc/ssl/certs/aegis.crt /etc/ssl/certs/dhparam.pem && \
    chmod 600 /etc/ssl/private/aegis.key && \
    chmod 644 /etc/nginx/.htpasswd

# Create cache and log directories
RUN mkdir -p /var/cache/nginx /var/log/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f https://localhost/health -k || exit 1

# Expose HTTPS port
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]