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