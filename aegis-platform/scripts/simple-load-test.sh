#!/bin/bash

# Simple Load Testing Script using curl (no external dependencies)
# This provides basic load testing when k6 is not available

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL=${BASE_URL:-"http://localhost:30641"}
CONCURRENT_USERS=${CONCURRENT_USERS:-10}
REQUESTS_PER_USER=${REQUESTS_PER_USER:-5}
RESULTS_DIR="simple-load-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}🚀 Simple Aegis Platform Load Test${NC}"
echo -e "${BLUE}==================================${NC}"
echo "Base URL: $BASE_URL"
echo "Concurrent Users: $CONCURRENT_USERS"
echo "Requests per User: $REQUESTS_PER_USER"
echo "Timestamp: $TIMESTAMP"
echo ""

# Create results directory
mkdir -p "$RESULTS_DIR"

# Function to check if services are running
check_services() {
    echo -e "${YELLOW}🔍 Checking if Aegis services are running...${NC}"
    
    if curl -s "$BASE_URL/health" > /dev/null; then
        echo -e "${GREEN}✅ Aegis Platform is running at $BASE_URL${NC}"
    else
        echo -e "${RED}❌ Aegis Platform is not responding at $BASE_URL${NC}"
        echo "Please start the services with:"
        echo "  cd aegis-platform && docker-compose -f docker/docker-compose.yml up -d"
        exit 1
    fi
}

# Function to authenticate and get token
authenticate() {
    local token_file="$RESULTS_DIR/auth_token.txt"
    
    echo -e "${YELLOW}🔐 Authenticating...${NC}"
    
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d '{"username":"admin@aegis-platform.com","password":"admin123"}' \
        "$BASE_URL/api/v1/auth/login")
    
    local http_code="${response: -3}"
    local body="${response%???}"
    
    if [[ "$http_code" == "200" ]]; then
        echo "$body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 > "$token_file"
        echo -e "${GREEN}✅ Authentication successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Authentication failed (HTTP $http_code)${NC}"
        return 1
    fi
}

# Function to run single API request
run_single_request() {
    local token="$1"
    local endpoint="$2"
    local user_id="$3"
    local request_id="$4"
    
    local start_time=$(date +%s.%N)
    
    local response=$(curl -s -w "%{http_code}:%{time_total}" \
        -H "Authorization: Bearer $token" \
        "$BASE_URL$endpoint" 2>/dev/null)
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    local http_code=$(echo "$response" | cut -d':' -f1 | tail -1)
    local curl_time=$(echo "$response" | cut -d':' -f2 | tail -1)
    
    echo "$user_id,$request_id,$endpoint,$http_code,$duration,$curl_time" >> "$RESULTS_DIR/requests_$TIMESTAMP.csv"
    
    if [[ "$http_code" == "200" ]]; then
        echo -e "${GREEN}✅ User $user_id Request $request_id: $endpoint ($duration s)${NC}"
    else
        echo -e "${RED}❌ User $user_id Request $request_id: $endpoint HTTP $http_code${NC}"
    fi
}

# Function to simulate single user
simulate_user() {
    local user_id="$1"
    local token="$2"
    
    echo -e "${YELLOW}👤 Starting user $user_id simulation...${NC}"
    
    # Array of endpoints to test
    local endpoints=(
        "/api/v1/assets"
        "/api/v1/risks" 
        "/api/v1/tasks"
        "/api/v1/evidence"
        "/api/v1/frameworks"
        "/api/v1/auth/profile"
    )
    
    for ((i=1; i<=REQUESTS_PER_USER; i++)); do
        # Select random endpoint
        local endpoint=${endpoints[$RANDOM % ${#endpoints[@]}]}
        
        run_single_request "$token" "$endpoint" "$user_id" "$i"
        
        # Think time (0.5 to 2 seconds)
        sleep $(echo "scale=2; $RANDOM/32767 * 1.5 + 0.5" | bc -l)
    done
    
    echo -e "${GREEN}✅ User $user_id completed${NC}"
}

# Function to run load test
run_load_test() {
    local token_file="$RESULTS_DIR/auth_token.txt"
    local token=$(cat "$token_file")
    
    echo -e "${YELLOW}🚀 Starting load test with $CONCURRENT_USERS concurrent users...${NC}"
    
    # Create CSV header
    echo "user_id,request_id,endpoint,http_code,duration,curl_time" > "$RESULTS_DIR/requests_$TIMESTAMP.csv"
    
    # Start concurrent users
    local pids=()
    
    for ((i=1; i<=CONCURRENT_USERS; i++)); do
        simulate_user "$i" "$token" &
        pids+=($!)
    done
    
    # Wait for all users to complete
    echo -e "${YELLOW}⏳ Waiting for all users to complete...${NC}"
    
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    echo -e "${GREEN}✅ All users completed${NC}"
}

# Function to generate results summary
generate_summary() {
    local csv_file="$RESULTS_DIR/requests_$TIMESTAMP.csv"
    local summary_file="$RESULTS_DIR/summary_$TIMESTAMP.txt"
    
    echo -e "${YELLOW}📊 Generating summary...${NC}"
    
    if [[ ! -f "$csv_file" ]]; then
        echo -e "${RED}❌ Results file not found${NC}"
        return 1
    fi
    
    # Calculate statistics using awk
    awk -F',' '
    BEGIN {
        success_count = 0
        total_count = 0
        total_duration = 0
        min_duration = 999999
        max_duration = 0
    }
    NR > 1 {
        total_count++
        duration = $5
        total_duration += duration
        
        if (duration < min_duration) min_duration = duration
        if (duration > max_duration) max_duration = duration
        
        if ($4 == "200") success_count++
    }
    END {
        if (total_count > 0) {
            avg_duration = total_duration / total_count
            success_rate = (success_count / total_count) * 100
            
            print "Simple Load Test Results"
            print "========================"
            print "Total Requests: " total_count
            print "Successful Requests: " success_count
            print "Success Rate: " success_rate "%"
            print "Average Response Time: " avg_duration " seconds"
            print "Min Response Time: " min_duration " seconds"
            print "Max Response Time: " max_duration " seconds"
            print "Requests per Second: " total_count / (max_duration + avg_duration)
        }
    }' "$csv_file" > "$summary_file"
    
    # Display summary
    cat "$summary_file"
    
    # Check if performance is acceptable
    local success_rate=$(awk -F',' 'NR > 1 && $4 == "200" { success++ } NR > 1 { total++ } END { print (success/total)*100 }' "$csv_file")
    local avg_time=$(awk -F',' 'NR > 1 { sum += $5; count++ } END { print sum/count }' "$csv_file")
    
    echo ""
    if (( $(echo "$success_rate >= 95" | bc -l) )) && (( $(echo "$avg_time <= 3" | bc -l) )); then
        echo -e "${GREEN}✅ Performance Acceptable: ${success_rate}% success rate, ${avg_time}s average response time${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Performance Warning: ${success_rate}% success rate, ${avg_time}s average response time${NC}"
        return 1
    fi
}

# Function to show system resources
show_system_resources() {
    echo -e "${YELLOW}💻 Current System Resources:${NC}"
    
    if command -v docker &> /dev/null; then
        echo "Docker Container Stats:"
        timeout 3 docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "Docker stats not available"
    fi
    
    echo ""
    echo "System Load:"
    uptime
    
    echo ""
    echo "Memory Usage:"
    if command -v free &> /dev/null; then
        free -h | head -2
    else
        echo "Memory info not available on this system"
    fi
}

# Main execution
main() {
    # Pre-flight checks
    check_services
    show_system_resources
    
    echo ""
    
    # Authentication
    if ! authenticate; then
        exit 1
    fi
    
    echo ""
    
    # Run load test
    local start_time=$(date +%s)
    run_load_test
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    echo ""
    echo -e "${BLUE}Test completed in ${total_time} seconds${NC}"
    
    # Generate summary
    if generate_summary; then
        echo -e "${GREEN}🎉 Load test completed successfully!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Load test completed with warnings${NC}"
        exit 1
    fi
}

# Check if bc is available (for calculations)
if ! command -v bc &> /dev/null; then
    echo -e "${RED}❌ bc (calculator) is required but not installed${NC}"
    echo "Please install bc: apt-get install bc (Ubuntu) or brew install bc (macOS)"
    exit 1
fi

# Run main function
main "$@"