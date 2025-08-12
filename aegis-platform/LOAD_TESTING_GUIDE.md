# Load Testing Guide for Aegis Risk Management Platform

## Overview
This guide provides comprehensive load testing procedures to validate the Aegis Platform's performance under production-level load conditions. Load testing ensures the system can handle expected user volumes and traffic patterns without performance degradation.

## Load Testing Strategy

### Performance Requirements
- **Concurrent Users**: 50-100 simultaneous users
- **Response Time**: < 2 seconds for 95% of requests
- **Throughput**: 500+ requests per minute
- **Error Rate**: < 1% under normal load
- **Database Performance**: < 500ms query response time
- **Memory Usage**: < 2GB RAM per service
- **CPU Usage**: < 80% under peak load

## Load Testing Tools

### 1. K6 Load Testing (Primary)
K6 is recommended for comprehensive API and workflow testing.

**Installation:**
```bash
# macOS
brew install k6

# Ubuntu/Debian
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Docker
docker pull grafana/k6
```

### 2. Artillery (Alternative)
Lightweight HTTP load testing tool.

**Installation:**
```bash
npm install -g artillery
```

### 3. JMeter (GUI Option)
For visual test planning and execution.

## Load Testing Scripts

### K6 Test Scripts

#### 1. Authentication Load Test
```javascript
// tests/load/auth-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Maintain 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Maintain 20 users
    { duration: '2m', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% requests under 2s
    errors: ['rate<0.01'], // Error rate under 1%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:30641';

export default function() {
  // Login request
  let loginPayload = JSON.stringify({
    username: 'admin@aegis-platform.com',
    password: 'admin123'
  });

  let loginParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let loginResponse = http.post(`${BASE_URL}/api/v1/auth/login`, loginPayload, loginParams);
  
  let loginSuccess = check(loginResponse, {
    'login status is 200': (r) => r.status === 200,
    'login response time < 2s': (r) => r.timings.duration < 2000,
    'received access token': (r) => r.json('access_token') !== undefined,
  });

  errorRate.add(!loginSuccess);
  
  if (loginSuccess) {
    let token = loginResponse.json('access_token');
    
    // Profile request with authentication
    let profileParams = {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    };
    
    let profileResponse = http.get(`${BASE_URL}/api/v1/auth/profile`, profileParams);
    
    let profileSuccess = check(profileResponse, {
      'profile status is 200': (r) => r.status === 200,
      'profile response time < 1s': (r) => r.timings.duration < 1000,
    });
    
    errorRate.add(!profileSuccess);
  }
  
  sleep(1);
}
```

#### 2. Core API Load Test
```javascript
// tests/load/api-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '3m', target: 25 }, // Ramp up to 25 users
    { duration: '10m', target: 25 }, // Maintain 25 users
    { duration: '3m', target: 50 }, // Ramp up to 50 users
    { duration: '10m', target: 50 }, // Maintain 50 users
    { duration: '3m', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:30641';
let authToken = '';

export function setup() {
  // Authenticate once for all virtual users
  let loginPayload = JSON.stringify({
    username: 'admin@aegis-platform.com',
    password: 'admin123'
  });

  let loginResponse = http.post(`${BASE_URL}/api/v1/auth/login`, loginPayload, {
    headers: { 'Content-Type': 'application/json' },
  });

  if (loginResponse.status === 200) {
    return { token: loginResponse.json('access_token') };
  }
  
  throw new Error('Authentication failed during setup');
}

export default function(data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  // Test various API endpoints
  const endpoints = [
    '/api/v1/assets',
    '/api/v1/risks',
    '/api/v1/tasks',
    '/api/v1/evidence',
    '/api/v1/frameworks',
    '/api/v1/assessments',
    '/api/v1/dashboards/overview',
  ];

  // Random endpoint selection for realistic load distribution
  let endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  
  let response = http.get(`${BASE_URL}${endpoint}`, { headers });
  
  let success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
    'response has data': (r) => r.body.length > 0,
  });

  errorRate.add(!success);
  
  // Simulate user think time
  sleep(Math.random() * 3 + 1); // 1-4 seconds
}
```

#### 3. Database Stress Test
```javascript
// tests/load/database-stress-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 50 },  // Rapid ramp up
    { duration: '15m', target: 50 }, // Sustained load
    { duration: '2m', target: 100 }, // Stress test
    { duration: '5m', target: 100 }, // Peak load
    { duration: '3m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<5000'], // 99% under 5s (stress conditions)
    http_req_failed: ['rate<0.05'], // Allow 5% failures under stress
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
    'Content-Type': 'application/json',
  };

  // Database-heavy operations
  const operations = [
    () => http.get(`${BASE_URL}/api/v1/analytics/trends`, { headers }),
    () => http.get(`${BASE_URL}/api/v1/reports/generate`, { headers }),
    () => http.get(`${BASE_URL}/api/v1/dashboards/risk-metrics`, { headers }),
    () => http.post(`${BASE_URL}/api/v1/ai/analyze-risk`, 
      JSON.stringify({ description: 'Test risk for load testing' }), 
      { headers }),
  ];

  // Execute random database-heavy operation
  let operation = operations[Math.floor(Math.random() * operations.length)];
  let response = operation();
  
  check(response, {
    'status is 200 or 202': (r) => [200, 202].includes(r.status),
    'response time acceptable': (r) => r.timings.duration < 10000,
  });

  sleep(0.5); // Aggressive load
}
```

### Artillery Test Configuration

#### Basic Load Test
```yaml
# tests/load/artillery-basic.yml
config:
  target: 'http://localhost:30641'
  phases:
    - duration: 300
      arrivalRate: 5
      name: "Warm up"
    - duration: 600
      arrivalRate: 10
      name: "Sustained load"
    - duration: 300
      arrivalRate: 20
      name: "Peak load"
  processor: "./auth-processor.js"

scenarios:
  - name: "API Load Test"
    weight: 100
    flow:
      - post:
          url: "/api/v1/auth/login"
          json:
            username: "admin@aegis-platform.com"
            password: "admin123"
          capture:
            - json: "$.access_token"
              as: "authToken"
      - get:
          url: "/api/v1/assets"
          headers:
            Authorization: "Bearer {{ authToken }}"
      - get:
          url: "/api/v1/risks"
          headers:
            Authorization: "Bearer {{ authToken }}"
      - think: 2
```

## Load Testing Execution

### Environment Setup
```bash
# Navigate to aegis platform directory
cd aegis-platform

# Ensure services are running
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to be ready
sleep 30

# Create load testing directory
mkdir -p tests/load
```

### Running K6 Tests
```bash
# Basic authentication load test
k6 run tests/load/auth-load-test.js

# API load test with custom base URL
BASE_URL=http://localhost:30641 k6 run tests/load/api-load-test.js

# Database stress test
k6 run tests/load/database-stress-test.js

# Combined test with custom thresholds
k6 run --out json=load-test-results.json tests/load/api-load-test.js
```

### Running Artillery Tests
```bash
# Basic load test
artillery run tests/load/artillery-basic.yml

# Custom load test with reporting
artillery run --output load-report.json tests/load/artillery-basic.yml
artillery report load-report.json
```

## Performance Monitoring

### System Metrics Collection
```bash
# Monitor Docker container resources
docker stats

# Monitor database performance
docker-compose exec db mysql -u root -p -e "SHOW PROCESSLIST;"

# Monitor Redis performance  
docker-compose exec redis redis-cli info stats

# System resource monitoring
htop
iostat -x 1
```

### Application Metrics
```bash
# FastAPI metrics endpoint (if implemented)
curl http://localhost:30641/metrics

# Health check monitoring
curl http://localhost:30641/health

# Database connection pool status
curl -H "Authorization: Bearer $TOKEN" http://localhost:30641/api/v1/health/detailed
```

## Performance Baselines

### Expected Performance Metrics

#### Response Times (95th percentile)
- Authentication: < 500ms
- Asset listing: < 1s
- Risk queries: < 1.5s
- Report generation: < 5s
- AI analysis: < 10s

#### Throughput Targets
- Login requests: 50/minute
- API reads: 200/minute  
- API writes: 100/minute
- Complex queries: 20/minute

#### Resource Utilization
- CPU: < 70% under normal load
- Memory: < 1.5GB per service
- Database connections: < 50% of pool
- Disk I/O: < 80% utilization

## Load Testing Scenarios

### 1. Normal Business Load
- 25 concurrent users
- 60% read operations, 40% write operations
- 30-minute duration
- Realistic user behavior patterns

### 2. Peak Business Load  
- 50 concurrent users
- 70% read operations, 30% write operations
- 45-minute duration
- Higher frequency of complex operations

### 3. Stress Test
- 100 concurrent users
- 80% read operations, 20% write operations
- 20-minute duration
- Identify breaking points

### 4. Endurance Test
- 30 concurrent users
- Normal operation mix
- 4-hour duration
- Check for memory leaks and degradation

## Results Analysis

### K6 Results Interpretation
```bash
# Generate HTML report from JSON results
k6 run --out json=results.json tests/load/api-load-test.js
# Use k6-reporter to generate HTML report
npm install -g k6-to-junit
k6-to-junit results.json
```

### Performance Regression Detection
```bash
# Compare current results with baseline
# Store baseline metrics in version control
cp load-test-results.json baseline/$(date +%Y%m%d)-baseline.json

# Automated comparison script
python3 tools/compare-performance.py baseline/latest.json load-test-results.json
```

## Troubleshooting Performance Issues

### Common Issues and Solutions

#### High Response Times
1. **Database Query Optimization**
   - Add indexes for frequently queried columns
   - Optimize complex JOIN operations
   - Implement query result caching

2. **Connection Pool Tuning**
   - Increase database connection pool size
   - Optimize connection timeout settings
   - Monitor connection utilization

3. **Memory Issues**
   - Implement Redis caching for frequent queries
   - Optimize object serialization
   - Add memory limits to containers

#### High Error Rates
1. **Database Connection Errors**
   - Check connection pool exhaustion
   - Verify database server capacity
   - Implement retry logic

2. **Timeout Errors**
   - Increase request timeout settings
   - Optimize slow database queries
   - Implement asynchronous processing

### Performance Optimization Checklist

- [ ] Database indexes optimized
- [ ] Redis caching implemented
- [ ] Connection pooling configured
- [ ] Static file caching enabled
- [ ] Gzip compression active
- [ ] Background task processing
- [ ] Database query optimization
- [ ] Memory usage monitoring
- [ ] Error rate tracking
- [ ] Performance regression testing

## Continuous Performance Testing

### CI/CD Integration
```yaml
# .github/workflows/performance-test.yml
name: Performance Tests
on:
  schedule:
    - cron: '0 2 * * *' # Daily at 2 AM
  push:
    branches: [main]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose -f docker/docker-compose.yml up -d
      - name: Wait for services
        run: sleep 60
      - name: Install k6
        run: |
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      - name: Run performance tests
        run: |
          k6 run --out json=performance-results.json tests/load/api-load-test.js
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: performance-results.json
```

## Production Load Testing

### Pre-Production Testing
- Test against staging environment identical to production
- Use production data volumes (anonymized)
- Include third-party service integration testing
- Validate monitoring and alerting systems

### Production Testing Considerations
- Schedule testing during low-traffic periods
- Use synthetic test data
- Implement circuit breakers and rate limiting
- Monitor real user impact during testing
- Have rollback procedures ready

## Success Criteria

### Performance Acceptance Criteria
✅ **Response Time**: 95% of requests complete under 2 seconds  
✅ **Throughput**: System handles 500+ requests per minute  
✅ **Error Rate**: Less than 1% error rate under normal load  
✅ **Resource Usage**: CPU and memory within acceptable limits  
✅ **Database Performance**: Query response times under 500ms  
✅ **Scalability**: Linear performance scaling with load increase  
✅ **Recovery**: System recovers gracefully from peak load  

Load testing validates that the Aegis Platform can handle production workloads reliably and efficiently.