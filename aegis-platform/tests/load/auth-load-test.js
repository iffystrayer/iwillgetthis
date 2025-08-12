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