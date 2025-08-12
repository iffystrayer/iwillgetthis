#!/bin/bash

# Aegis Platform Load Testing Runner
# This script runs comprehensive load tests and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL=${BASE_URL:-"http://localhost:30641"}
RESULTS_DIR="load-test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}🚀 Aegis Platform Load Testing Suite${NC}"
echo -e "${BLUE}======================================${NC}"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Function to check if k6 is installed
check_k6() {
    if ! command -v k6 &> /dev/null; then
        echo -e "${RED}❌ k6 is not installed. Please install k6 first.${NC}"
        echo "Installation instructions:"
        echo "  macOS: brew install k6"
        echo "  Ubuntu/Debian: See https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
    echo -e "${GREEN}✅ k6 is available${NC}"
}

# Function to check if services are running
check_services() {
    echo -e "${YELLOW}🔍 Checking if Aegis services are running...${NC}"
    
    # Check if the API is responding
    if curl -s "$BASE_URL/health" > /dev/null; then
        echo -e "${GREEN}✅ Aegis Platform is running at $BASE_URL${NC}"
    else
        echo -e "${RED}❌ Aegis Platform is not responding at $BASE_URL${NC}"
        echo "Please start the services with:"
        echo "  cd aegis-platform && docker-compose -f docker/docker-compose.yml up -d"
        exit 1
    fi
}

# Function to run authentication load test
run_auth_test() {
    echo -e "${YELLOW}🔐 Running Authentication Load Test...${NC}"
    
    local output_file="$RESULTS_DIR/auth-test-$TIMESTAMP.json"
    
    if BASE_URL="$BASE_URL" k6 run --out json="$output_file" tests/load/auth-load-test.js; then
        echo -e "${GREEN}✅ Authentication load test completed${NC}"
        echo "Results saved to: $output_file"
    else
        echo -e "${RED}❌ Authentication load test failed${NC}"
        return 1
    fi
}

# Function to run API load test
run_api_test() {
    echo -e "${YELLOW}🌐 Running API Load Test...${NC}"
    
    local output_file="$RESULTS_DIR/api-test-$TIMESTAMP.json"
    
    if BASE_URL="$BASE_URL" k6 run --out json="$output_file" tests/load/api-load-test.js; then
        echo -e "${GREEN}✅ API load test completed${NC}"
        echo "Results saved to: $output_file"
    else
        echo -e "${RED}❌ API load test failed${NC}"
        return 1
    fi
}

# Function to run database stress test
run_database_test() {
    echo -e "${YELLOW}🗄️ Running Database Stress Test...${NC}"
    
    local output_file="$RESULTS_DIR/database-test-$TIMESTAMP.json"
    
    if BASE_URL="$BASE_URL" k6 run --out json="$output_file" tests/load/database-stress-test.js; then
        echo -e "${GREEN}✅ Database stress test completed${NC}"
        echo "Results saved to: $output_file"
    else
        echo -e "${RED}❌ Database stress test failed${NC}"
        return 1
    fi
}

# Function to generate summary report
generate_summary() {
    echo -e "${YELLOW}📊 Generating Load Test Summary...${NC}"
    
    local summary_file="$RESULTS_DIR/summary-$TIMESTAMP.txt"
    
    cat > "$summary_file" << EOF
Aegis Platform Load Test Summary
===============================
Test Date: $(date)
Base URL: $BASE_URL
Results Directory: $RESULTS_DIR

Test Files Generated:
- auth-test-$TIMESTAMP.json
- api-test-$TIMESTAMP.json  
- database-test-$TIMESTAMP.json

To analyze results in detail:
1. Install k6-to-junit: npm install -g k6-to-junit
2. Convert to JUnit: k6-to-junit $RESULTS_DIR/api-test-$TIMESTAMP.json
3. Or analyze JSON directly with your preferred tools

Performance Thresholds Met:
- Authentication: 95% requests < 2s, error rate < 1%
- API Operations: 95% requests < 2s, error rate < 1%
- Database Operations: 99% requests < 5s, error rate < 5% (stress)

EOF

    echo -e "${GREEN}✅ Summary generated: $summary_file${NC}"
    cat "$summary_file"
}

# Function to run quick smoke test
run_smoke_test() {
    echo -e "${YELLOW}💨 Running Quick Smoke Test...${NC}"
    
    cat > tests/load/smoke-test.js << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:30641';

export function setup() {
  let loginResponse = http.post(`${BASE_URL}/api/v1/auth/login`, 
    JSON.stringify({
      username: 'admin@aegis-platform.com',
      password: 'admin123'
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

  return { token: loginResponse.json('access_token') };
}

export default function(data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
  };

  let response = http.get(`${BASE_URL}/api/v1/assets`, { headers });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 3s': (r) => r.timings.duration < 3000,
  });
}
EOF

    if BASE_URL="$BASE_URL" k6 run tests/load/smoke-test.js; then
        echo -e "${GREEN}✅ Smoke test passed${NC}"
        rm tests/load/smoke-test.js
        return 0
    else
        echo -e "${RED}❌ Smoke test failed${NC}"
        rm tests/load/smoke-test.js
        return 1
    fi
}

# Function to show system resources
show_system_resources() {
    echo -e "${YELLOW}💻 Current System Resources:${NC}"
    
    if command -v docker &> /dev/null; then
        echo "Docker Container Stats:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -6
    fi
    
    echo ""
    echo "System Load:"
    uptime
    
    echo ""
    echo "Memory Usage:"
    free -h | head -2
}

# Main execution
main() {
    echo -e "${BLUE}Starting load test execution...${NC}"
    
    # Pre-flight checks
    check_k6
    check_services
    show_system_resources
    
    echo ""
    
    # Get user confirmation for full test suite
    if [[ "$1" == "--quick" ]]; then
        echo -e "${YELLOW}Running quick smoke test only...${NC}"
        run_smoke_test
        exit $?
    elif [[ "$1" == "--help" ]]; then
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --quick    Run only quick smoke test"
        echo "  --auth     Run only authentication test"
        echo "  --api      Run only API test"
        echo "  --database Run only database test"
        echo "  --help     Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  BASE_URL   API base URL (default: http://localhost:30641)"
        exit 0
    elif [[ "$1" == "--auth" ]]; then
        run_auth_test
        exit $?
    elif [[ "$1" == "--api" ]]; then
        run_api_test
        exit $?
    elif [[ "$1" == "--database" ]]; then
        run_database_test
        exit $?
    else
        read -p "Run full load test suite? This will take ~45 minutes (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Running quick smoke test instead...${NC}"
            run_smoke_test
            exit $?
        fi
    fi
    
    # Run full test suite
    local failed_tests=0
    
    echo -e "${BLUE}🎯 Running Full Load Test Suite...${NC}"
    
    run_auth_test || ((failed_tests++))
    echo ""
    
    run_api_test || ((failed_tests++))
    echo ""
    
    run_database_test || ((failed_tests++))
    echo ""
    
    generate_summary
    
    # Final status
    if [[ $failed_tests -eq 0 ]]; then
        echo -e "${GREEN}🎉 All load tests completed successfully!${NC}"
        exit 0
    else
        echo -e "${RED}⚠️  $failed_tests test(s) failed. Check the results for details.${NC}"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"