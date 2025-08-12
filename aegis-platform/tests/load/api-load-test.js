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