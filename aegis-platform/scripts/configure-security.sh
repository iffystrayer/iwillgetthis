#!/bin/bash
# ==============================================
# Aegis Platform - Security Configuration Script
# ==============================================
# Configure and manage security settings for the platform
# ==============================================

set -e

# Configuration
CONFIG_DIR="$(pwd)"
SECURITY_CONFIG_FILE="${CONFIG_DIR}/security-config.json"
NGINX_CONFIG_FILE="${CONFIG_DIR}/nginx/nginx-production.conf"
BACKEND_CONFIG_FILE="${CONFIG_DIR}/backend/config.py"

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

check_requirements() {
    print_header "Checking Security Configuration Requirements"
    
    # Check if configuration files exist
    local required_files=("$NGINX_CONFIG_FILE" "$BACKEND_CONFIG_FILE")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    # Check if running with appropriate permissions
    if [ "$(id -u)" -eq 0 ]; then
        print_warning "Running as root - ensure proper file permissions after configuration"
    fi
    
    print_success "Requirements check passed"
}

create_security_config() {
    print_header "Creating Security Configuration"
    
    cat > "$SECURITY_CONFIG_FILE" << 'EOF'
{
  "rate_limiting": {
    "enabled": true,
    "global": {
      "requests_per_minute": 200,
      "requests_per_hour": 2000,
      "requests_per_day": 20000,
      "burst_size": 100
    },
    "auth_endpoints": {
      "requests_per_minute": 10,
      "requests_per_hour": 50,
      "requests_per_day": 200,
      "burst_size": 5
    },
    "api_endpoints": {
      "requests_per_minute": 100,
      "requests_per_hour": 1000,
      "requests_per_day": 10000,
      "burst_size": 50
    },
    "admin_endpoints": {
      "requests_per_minute": 20,
      "requests_per_hour": 100,
      "requests_per_day": 500,
      "burst_size": 10
    }
  },
  "security_headers": {
    "x_frame_options": "DENY",
    "x_content_type_options": "nosniff",
    "x_xss_protection": "1; mode=block",
    "referrer_policy": "strict-origin-when-cross-origin",
    "content_security_policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    "strict_transport_security": "max-age=31536000; includeSubDomains; preload",
    "permissions_policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), speaker=(), vibrate=(), fullscreen=(self), sync-xhr=()"
  },
  "ip_filtering": {
    "enabled": false,
    "allowlist": [],
    "blocklist": [],
    "auto_block_threshold": 10,
    "suspicious_pattern_threshold": 5
  },
  "request_limits": {
    "max_request_size": 52428800,
    "max_header_size": 8192,
    "max_query_params": 100,
    "timeout_seconds": 30
  },
  "logging": {
    "log_security_events": true,
    "log_failed_requests": true,
    "log_suspicious_patterns": true,
    "log_rate_limit_hits": true
  },
  "alerts": {
    "email_notifications": true,
    "slack_notifications": false,
    "pagerduty_notifications": false,
    "webhook_notifications": false
  }
}
EOF
    
    print_success "Security configuration created: $SECURITY_CONFIG_FILE"
}

configure_rate_limiting() {
    print_header "Configuring Rate Limiting"
    
    local rate_config=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
rate_config = config['rate_limiting']
print(f\"Global: {rate_config['global']['requests_per_minute']}/min\")
print(f\"Auth: {rate_config['auth_endpoints']['requests_per_minute']}/min\")
print(f\"API: {rate_config['api_endpoints']['requests_per_minute']}/min\")
print(f\"Admin: {rate_config['admin_endpoints']['requests_per_minute']}/min\")
")
    
    echo "Rate limiting configuration:"
    echo "$rate_config"
    
    # Update nginx rate limiting zones
    local temp_file=$(mktemp)
    
    # Extract rate limits from config
    local global_rate=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(config['rate_limiting']['global']['requests_per_minute'])
")
    
    local auth_rate=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(config['rate_limiting']['auth_endpoints']['requests_per_minute'])
")
    
    local api_rate=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(config['rate_limiting']['api_endpoints']['requests_per_minute'])
")
    
    # Update nginx configuration
    sed "s/rate=5r\/m/rate=${auth_rate}r\/m/g; s/rate=100r\/m/rate=${api_rate}r\/m/g; s/rate=200r\/m/rate=${global_rate}r\/m/g" \
        "$NGINX_CONFIG_FILE" > "$temp_file"
    
    cp "$temp_file" "$NGINX_CONFIG_FILE"
    rm "$temp_file"
    
    print_success "Rate limiting configured in nginx"
}

configure_security_headers() {
    print_header "Configuring Security Headers"
    
    # Extract security headers from config
    local csp_policy=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(config['security_headers']['content_security_policy'])
")
    
    local hsts_header=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(config['security_headers']['strict_transport_security'])
")
    
    echo "Configured security headers:"
    echo "  Content-Security-Policy: $csp_policy"
    echo "  Strict-Transport-Security: $hsts_header"
    
    print_success "Security headers configured"
}

configure_ip_filtering() {
    print_header "Configuring IP Filtering"
    
    local ip_filtering_enabled=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(config['ip_filtering']['enabled'])
")
    
    if [ "$ip_filtering_enabled" = "True" ]; then
        echo "IP filtering is enabled"
        
        # Get allowlist and blocklist
        local allowlist=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
allowlist = config['ip_filtering']['allowlist']
if allowlist:
    for ip in allowlist:
        print(f'allow {ip};')
else:
    print('# No IP allowlist configured')
")
        
        local blocklist=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
blocklist = config['ip_filtering']['blocklist']
if blocklist:
    for ip in blocklist:
        print(f'deny {ip};')
else:
    print('# No IP blocklist configured')
")
        
        echo "IP Allowlist rules:"
        echo "$allowlist"
        echo
        echo "IP Blocklist rules:"
        echo "$blocklist"
        
        print_success "IP filtering configured"
    else
        echo "IP filtering is disabled"
        print_warning "Consider enabling IP filtering for production environments"
    fi
}

configure_request_limits() {
    print_header "Configuring Request Limits"
    
    local max_size=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
size_mb = config['request_limits']['max_request_size'] // 1048576
print(f'{size_mb}M')
")
    
    local timeout=$(cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(f\"{config['request_limits']['timeout_seconds']}s\")
")
    
    echo "Request limits:"
    echo "  Max request size: $max_size"
    echo "  Request timeout: $timeout"
    
    # Update nginx configuration
    local temp_file=$(mktemp)
    sed "s/client_max_body_size [^;]*/client_max_body_size $max_size/g; s/client_body_timeout [^;]*/client_body_timeout $timeout/g" \
        "$NGINX_CONFIG_FILE" > "$temp_file"
    
    cp "$temp_file" "$NGINX_CONFIG_FILE"
    rm "$temp_file"
    
    print_success "Request limits configured"
}

setup_logging() {
    print_header "Setting Up Security Logging"
    
    # Create log directory
    mkdir -p "${CONFIG_DIR}/logs/security"
    
    # Create logrotate configuration
    cat > "/etc/logrotate.d/aegis-security" << EOF
${CONFIG_DIR}/logs/security/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
        docker-compose restart aegis-backend > /dev/null 2>&1 || true
    endscript
}
EOF
    
    # Create security monitoring script
    cat > "${CONFIG_DIR}/scripts/security-monitor.sh" << 'EOF'
#!/bin/bash
# Security monitoring script
LOG_DIR="$(dirname "$0")/../logs/security"
DATE=$(date '+%Y-%m-%d')

# Monitor failed login attempts
failed_logins=$(grep "401" "${LOG_DIR}/access-${DATE}.log" 2>/dev/null | grep "/api/v1/auth/" | wc -l)
if [ "$failed_logins" -gt 50 ]; then
    echo "High number of failed login attempts detected: $failed_logins"
fi

# Monitor suspicious patterns
suspicious_requests=$(grep -E "(union select|script>|\.\.\/)" "${LOG_DIR}/access-${DATE}.log" 2>/dev/null | wc -l)
if [ "$suspicious_requests" -gt 0 ]; then
    echo "Suspicious request patterns detected: $suspicious_requests"
fi

# Monitor rate limit hits
rate_limit_hits=$(grep "429" "${LOG_DIR}/access-${DATE}.log" 2>/dev/null | wc -l)
if [ "$rate_limit_hits" -gt 100 ]; then
    echo "High number of rate limit hits: $rate_limit_hits"
fi
EOF
    
    chmod +x "${CONFIG_DIR}/scripts/security-monitor.sh"
    
    print_success "Security logging configured"
}

create_security_dashboard() {
    print_header "Creating Security Dashboard"
    
    cat > "${CONFIG_DIR}/scripts/security-dashboard.py" << 'EOF'
#!/usr/bin/env python3
"""
Security Dashboard - Real-time security metrics and alerts
"""
import json
import time
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
import re

def parse_log_file(log_file_path):
    """Parse nginx access log file"""
    entries = []
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                # Parse nginx log format
                # This is a simplified parser - adjust for your log format
                entries.append(line.strip())
    except FileNotFoundError:
        print(f"Log file not found: {log_file_path}")
    return entries

def analyze_security_events(log_entries):
    """Analyze security events from log entries"""
    events = {
        'failed_auth': 0,
        'rate_limits': 0,
        'suspicious_patterns': 0,
        'error_4xx': 0,
        'error_5xx': 0,
        'top_ips': defaultdict(int),
        'attack_patterns': []
    }
    
    suspicious_patterns = [
        r'union\s+select', r'script>', r'\.\./', r'<script',
        r'javascript:', r'onload\s*=', r'onerror\s*='
    ]
    
    for entry in log_entries:
        # Count different types of events
        if '401' in entry and '/api/v1/auth/' in entry:
            events['failed_auth'] += 1
        elif '429' in entry:
            events['rate_limits'] += 1
        elif any(re.search(pattern, entry, re.IGNORECASE) for pattern in suspicious_patterns):
            events['suspicious_patterns'] += 1
            events['attack_patterns'].append(entry)
        elif ' 4' in entry and entry.split()[8].startswith('4'):
            events['error_4xx'] += 1
        elif ' 5' in entry and entry.split()[8].startswith('5'):
            events['error_5xx'] += 1
        
        # Extract IP addresses (simplified)
        try:
            ip = entry.split()[0]
            events['top_ips'][ip] += 1
        except IndexError:
            pass
    
    return events

def display_dashboard(events):
    """Display security dashboard"""
    print("\n" + "="*60)
    print("  AEGIS SECURITY DASHBOARD")
    print("="*60)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Security metrics
    print("SECURITY METRICS:")
    print("-" * 30)
    print(f"Failed Authentication Attempts: {events['failed_auth']}")
    print(f"Rate Limit Violations:          {events['rate_limits']}")
    print(f"Suspicious Pattern Matches:     {events['suspicious_patterns']}")
    print(f"4xx Client Errors:              {events['error_4xx']}")
    print(f"5xx Server Errors:              {events['error_5xx']}")
    print()
    
    # Top IPs
    print("TOP CLIENT IPs:")
    print("-" * 30)
    top_ips = sorted(events['top_ips'].items(), key=lambda x: x[1], reverse=True)[:10]
    for ip, count in top_ips:
        print(f"{ip:<20} {count:>6} requests")
    print()
    
    # Alerts
    alerts = []
    if events['failed_auth'] > 50:
        alerts.append(f"HIGH: {events['failed_auth']} failed authentication attempts")
    if events['suspicious_patterns'] > 10:
        alerts.append(f"HIGH: {events['suspicious_patterns']} suspicious patterns detected")
    if events['rate_limits'] > 100:
        alerts.append(f"MEDIUM: {events['rate_limits']} rate limit violations")
    
    if alerts:
        print("🚨 SECURITY ALERTS:")
        print("-" * 30)
        for alert in alerts:
            print(f"  {alert}")
        print()
    else:
        print("✅ No active security alerts")
        print()

def main():
    parser = argparse.ArgumentParser(description='Aegis Security Dashboard')
    parser.add_argument('--log-file', default='../logs/security/access.log',
                       help='Path to nginx access log file')
    parser.add_argument('--watch', action='store_true',
                       help='Continuously monitor and update dashboard')
    parser.add_argument('--interval', type=int, default=30,
                       help='Update interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    if args.watch:
        print("Starting security dashboard monitoring...")
        print("Press Ctrl+C to stop")
        try:
            while True:
                log_entries = parse_log_file(args.log_file)
                events = analyze_security_events(log_entries)
                
                # Clear screen
                print("\033[2J\033[H", end="")
                display_dashboard(events)
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    else:
        log_entries = parse_log_file(args.log_file)
        events = analyze_security_events(log_entries)
        display_dashboard(events)

if __name__ == '__main__':
    main()
EOF
    
    chmod +x "${CONFIG_DIR}/scripts/security-dashboard.py"
    
    print_success "Security dashboard created"
}

test_security_configuration() {
    print_header "Testing Security Configuration"
    
    echo "Running security configuration tests..."
    
    # Test 1: Check nginx configuration syntax
    if command -v nginx &> /dev/null; then
        if nginx -t -c "$NGINX_CONFIG_FILE" 2>/dev/null; then
            print_success "Nginx configuration syntax is valid"
        else
            print_error "Nginx configuration syntax error"
            nginx -t -c "$NGINX_CONFIG_FILE"
        fi
    else
        print_warning "Nginx not installed - skipping configuration test"
    fi
    
    # Test 2: Validate JSON configuration
    if python3 -m json.tool "$SECURITY_CONFIG_FILE" > /dev/null 2>&1; then
        print_success "Security configuration JSON is valid"
    else
        print_error "Security configuration JSON is invalid"
    fi
    
    # Test 3: Check required directories
    local required_dirs=("${CONFIG_DIR}/logs/security" "${CONFIG_DIR}/scripts")
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_success "Directory exists: $dir"
        else
            print_error "Directory missing: $dir"
        fi
    done
    
    print_success "Security configuration tests completed"
}

show_security_status() {
    print_header "Security Configuration Status"
    
    echo "Configuration files:"
    echo "  Security config: $SECURITY_CONFIG_FILE"
    echo "  Nginx config: $NGINX_CONFIG_FILE"
    echo "  Backend config: $BACKEND_CONFIG_FILE"
    echo
    
    if [ -f "$SECURITY_CONFIG_FILE" ]; then
        echo "Security features status:"
        cat "$SECURITY_CONFIG_FILE" | python3 -c "
import json, sys
config = json.load(sys.stdin)
print(f\"  Rate limiting: {'Enabled' if config['rate_limiting']['enabled'] else 'Disabled'}\")
print(f\"  IP filtering: {'Enabled' if config['ip_filtering']['enabled'] else 'Disabled'}\")
print(f\"  Security logging: {'Enabled' if config['logging']['log_security_events'] else 'Disabled'}\")
print(f\"  Email alerts: {'Enabled' if config['alerts']['email_notifications'] else 'Disabled'}\")
"
    else
        print_warning "Security configuration file not found"
    fi
    
    echo
    echo "Security scripts:"
    echo "  Monitor: ${CONFIG_DIR}/scripts/security-monitor.sh"
    echo "  Dashboard: ${CONFIG_DIR}/scripts/security-dashboard.py"
    echo
    echo "Log directory: ${CONFIG_DIR}/logs/security"
}

main() {
    print_header "Aegis Platform Security Configuration"
    
    case "${1:-configure}" in
        configure)
            check_requirements
            create_security_config
            configure_rate_limiting
            configure_security_headers
            configure_ip_filtering
            configure_request_limits
            setup_logging
            create_security_dashboard
            test_security_configuration
            show_security_status
            print_success "Security configuration completed successfully"
            ;;
        test)
            test_security_configuration
            ;;
        status)
            show_security_status
            ;;
        dashboard)
            exec python3 "${CONFIG_DIR}/scripts/security-dashboard.py" "${@:2}"
            ;;
        monitor)
            exec "${CONFIG_DIR}/scripts/security-monitor.sh"
            ;;
        --help)
            echo "Usage: $0 [configure|test|status|dashboard|monitor]"
            echo ""
            echo "Commands:"
            echo "  configure    Configure all security settings (default)"
            echo "  test         Test security configuration"
            echo "  status       Show security configuration status"
            echo "  dashboard    Launch security dashboard"
            echo "  monitor      Run security monitoring check"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

main "$@"
EOF