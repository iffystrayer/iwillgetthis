import { test, expect } from '@playwright/test';

// Test configuration
const LOGIN_CREDENTIALS = {
  email: 'admin@aegis-platform.com',
  password: 'admin123'
};

const BACKEND_URL = 'https://localhost/api';

test.describe('API Endpoints E2E Tests', () => {
  
  let authToken: string;
  
  test.beforeAll(async ({ request }) => {
    // Get authentication token for API tests
    const loginResponse = await request.post(`${BACKEND_URL}/api/v1/auth/login`, {
      data: {
        username: LOGIN_CREDENTIALS.email,
        password: LOGIN_CREDENTIALS.password
      }
    });
    
    expect(loginResponse.ok()).toBeTruthy();
    const loginData = await loginResponse.json();
    authToken = loginData.access_token;
    expect(authToken).toBeTruthy();
  });

  test.describe('User Management API', () => {
    
    test('GET /api/v1/users - should list users', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/users`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
      expect(data.items.length).toBeGreaterThan(0);
      
      // Verify user structure
      const user = data.items[0];
      expect(user).toHaveProperty('id');
      expect(user).toHaveProperty('email');
      expect(user).toHaveProperty('full_name');
      expect(user).not.toHaveProperty('hashed_password'); // Should not expose password
    });
    
    test('GET /api/v1/users/me - should return current user', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/users/me`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.email).toBe(LOGIN_CREDENTIALS.email);
    });
    
    test('POST /api/v1/users - should create new user', async ({ request }) => {
      const newUser = {
        email: `test${Date.now()}@example.com`,
        username: `testuser${Date.now()}`,
        full_name: 'Test User',
        password: 'testpass123',
        department: 'IT',
        job_title: 'Analyst'
      };
      
      const response = await request.post(`${BACKEND_URL}/api/v1/users`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: newUser
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.email).toBe(newUser.email);
      expect(data.username).toBe(newUser.username);
      
      // Clean up - delete the created user
      const userId = data.id;
      await request.delete(`${BACKEND_URL}/api/v1/users/${userId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
    });
  });

  test.describe('Asset Management API', () => {
    
    let createdAssetId: number;
    
    test('GET /api/v1/assets - should list assets', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/assets`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
    
    test('POST /api/v1/assets - should create new asset', async ({ request }) => {
      const newAsset = {
        name: `Test Asset ${Date.now()}`,
        description: 'Test asset created by E2E test',
        asset_type: 'server',
        criticality: 'high',
        ip_address: '192.168.1.100',
        hostname: 'test-server.company.com',
        operating_system: 'Ubuntu 22.04 LTS',
        environment: 'testing'
      };
      
      const response = await request.post(`${BACKEND_URL}/api/v1/assets`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: newAsset
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.name).toBe(newAsset.name);
      expect(data.asset_type).toBe(newAsset.asset_type);
      
      createdAssetId = data.id;
    });
    
    test('GET /api/v1/assets/{id} - should get specific asset', async ({ request }) => {
      if (!createdAssetId) {
        test.skip('No asset created to test with');
      }
      
      const response = await request.get(`${BACKEND_URL}/api/v1/assets/${createdAssetId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.id).toBe(createdAssetId);
    });
    
    test('PUT /api/v1/assets/{id} - should update asset', async ({ request }) => {
      if (!createdAssetId) {
        test.skip('No asset created to test with');
      }
      
      const updateData = {
        name: `Updated Asset ${Date.now()}`,
        description: 'Updated description',
        criticality: 'critical'
      };
      
      const response = await request.put(`${BACKEND_URL}/api/v1/assets/${createdAssetId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: updateData
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.name).toBe(updateData.name);
      expect(data.criticality).toBe(updateData.criticality);
    });
    
    test('DELETE /api/v1/assets/{id} - should delete asset', async ({ request }) => {
      if (!createdAssetId) {
        test.skip('No asset created to test with');
      }
      
      const response = await request.delete(`${BACKEND_URL}/api/v1/assets/${createdAssetId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(204);
      
      // Verify asset is deleted
      const getResponse = await request.get(`${BACKEND_URL}/api/v1/assets/${createdAssetId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      expect(getResponse.status()).toBe(404);
    });
  });

  test.describe('Risk Management API', () => {
    
    let createdRiskId: number;
    let testAssetId: number;
    
    test.beforeAll(async ({ request }) => {
      // Create a test asset for risk association
      const assetResponse = await request.post(`${BACKEND_URL}/api/v1/assets`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: {
          name: `Risk Test Asset ${Date.now()}`,
          asset_type: 'server',
          criticality: 'high'
        }
      });
      
      const assetData = await assetResponse.json();
      testAssetId = assetData.id;
    });
    
    test('GET /api/v1/risks - should list risks', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/risks`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
    
    test('POST /api/v1/risks - should create new risk', async ({ request }) => {
      const newRisk = {
        title: `Test Risk ${Date.now()}`,
        description: 'Test risk created by E2E test',
        category: 'technical',
        asset_id: testAssetId,
        inherent_likelihood: 4,
        inherent_impact: 5,
        status: 'identified'
      };
      
      const response = await request.post(`${BACKEND_URL}/api/v1/risks`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: newRisk
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.title).toBe(newRisk.title);
      expect(data.category).toBe(newRisk.category);
      
      createdRiskId = data.id;
    });
    
    test('GET /api/v1/risks/{id} - should get specific risk', async ({ request }) => {
      if (!createdRiskId) {
        test.skip('No risk created to test with');
      }
      
      const response = await request.get(`${BACKEND_URL}/api/v1/risks/${createdRiskId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.id).toBe(createdRiskId);
    });
    
    test.afterAll(async ({ request }) => {
      // Clean up test data
      if (createdRiskId) {
        await request.delete(`${BACKEND_URL}/api/v1/risks/${createdRiskId}`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
      }
      if (testAssetId) {
        await request.delete(`${BACKEND_URL}/api/v1/assets/${testAssetId}`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
      }
    });
  });

  test.describe('Task Management API', () => {
    
    let createdTaskId: number;
    
    test('GET /api/v1/tasks - should list tasks', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/tasks`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
    
    test('POST /api/v1/tasks - should create new task', async ({ request }) => {
      const newTask = {
        title: `Test Task ${Date.now()}`,
        description: 'Test task created by E2E test',
        task_type: 'remediation',
        priority: 'high',
        status: 'open',
        due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days from now
      };
      
      const response = await request.post(`${BACKEND_URL}/api/v1/tasks`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: newTask
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.title).toBe(newTask.title);
      expect(data.priority).toBe(newTask.priority);
      
      createdTaskId = data.id;
    });
    
    test('PATCH /api/v1/tasks/{id} - should update task progress', async ({ request }) => {
      if (!createdTaskId) {
        test.skip('No task created to test with');
      }
      
      const updateData = {
        progress_percentage: 50,
        status: 'in_progress'
      };
      
      const response = await request.patch(`${BACKEND_URL}/api/v1/tasks/${createdTaskId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: updateData
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.progress_percentage).toBe(50);
      expect(data.status).toBe('in_progress');
    });
    
    test.afterAll(async ({ request }) => {
      if (createdTaskId) {
        await request.delete(`${BACKEND_URL}/api/v1/tasks/${createdTaskId}`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
      }
    });
  });

  test.describe('Assessment API', () => {
    
    test('GET /api/v1/assessments - should list assessments', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/assessments`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
  });

  test.describe('Evidence Management API', () => {
    
    test('GET /api/v1/evidence - should list evidence', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/evidence`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
  });

  test.describe('Framework API', () => {
    
    test('GET /api/v1/frameworks - should list frameworks', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/frameworks`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
      
      // Should have NIST CSF and CIS Controls from initialization
      expect(data.items.length).toBeGreaterThanOrEqual(2);
    });
    
    test('GET /api/v1/frameworks/{id}/controls - should list controls for framework', async ({ request }) => {
      // First get frameworks to get an ID
      const frameworksResponse = await request.get(`${BACKEND_URL}/api/v1/frameworks`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      const frameworksData = await frameworksResponse.json();
      if (frameworksData.items.length === 0) {
        test.skip('No frameworks available to test with');
      }
      
      const frameworkId = frameworksData.items[0].id;
      
      const response = await request.get(`${BACKEND_URL}/api/v1/frameworks/${frameworkId}/controls`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
  });

  test.describe('Dashboard API', () => {
    
    test('GET /api/v1/dashboards/overview - should get dashboard overview', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/dashboards/overview`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data).toHaveProperty('total_assets');
      expect(data).toHaveProperty('total_risks');
      expect(data).toHaveProperty('total_tasks');
    });
  });

  test.describe('Reports API', () => {
    
    test('GET /api/v1/reports - should list reports', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/reports`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
    
    test('GET /api/v1/reports/templates - should list report templates', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/reports/templates`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(Array.isArray(data.items)).toBeTruthy();
    });
  });

  test.describe('API Error Handling', () => {
    
    test('should handle unauthorized requests', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/users`);
      expect(response.status()).toBe(401);
    });
    
    test('should handle invalid endpoints', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/nonexistent`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      expect(response.status()).toBe(404);
    });
    
    test('should handle invalid data in POST requests', async ({ request }) => {
      const response = await request.post(`${BACKEND_URL}/api/v1/assets`, {
        headers: { 'Authorization': `Bearer ${authToken}` },
        data: {
          name: '', // Invalid: empty name
          asset_type: 'invalid_type', // Invalid: bad enum
          criticality: 'invalid_criticality' // Invalid: bad enum
        }
      });
      
      expect(response.status()).toBe(422);
      const data = await response.json();
      expect(data.detail).toBeDefined(); // FastAPI validation errors use 'detail'
    });
  });

  test.describe('API Pagination', () => {
    
    test('should handle pagination parameters', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/assets?page=1&per_page=5`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      expect(data.page).toBe(1);
      expect(data.limit).toBe(5);
    });
  });

  test.describe('API Filtering and Search', () => {
    
    test('should handle asset filtering by type', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/assets?asset_type=server`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      // All returned assets should be of type 'server'
      if (data.items.length > 0) {
        data.items.forEach((asset: any) => {
          expect(asset.asset_type).toBe('server');
        });
      }
    });
    
    test('should handle risk filtering by status', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/api/v1/risks?status=identified`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      expect(response.status()).toBe(200);
      const data = await response.json();
      
      if (data.items.length > 0) {
        data.items.forEach((risk: any) => {
          expect(risk.status).toBe('identified');
        });
      }
    });
  });
});