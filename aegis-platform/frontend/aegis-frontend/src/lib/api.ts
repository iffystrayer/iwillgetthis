import axios, { AxiosResponse, AxiosError } from 'axios';
import Cookies from 'js-cookie';
import { ApiResponse, AuthTokens, QueryParams } from '@/types';
import { mockApiClient } from './mockApi';

// Check if we should use mock API
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true' || !import.meta.env.VITE_API_URL;

// API availability tracker
let apiAvailable = !USE_MOCK_API;

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Set up request interceptor for the main API instance
if (!USE_MOCK_API) {
  api.interceptors.request.use(
    (config) => {
      const token = Cookies.get('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling and token refresh
  api.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config;
      
      if (error.response?.status === 401 && originalRequest) {
        // Try to refresh token
        const refreshToken = Cookies.get('refresh_token');
        if (refreshToken) {
          try {
            const response = await axios.post(
              `${api.defaults.baseURL}/auth/refresh`,
              { refresh_token: refreshToken }
            );
            
            const tokens: AuthTokens = response.data;
            Cookies.set('access_token', tokens.access_token, { expires: 1 });
            Cookies.set('refresh_token', tokens.refresh_token, { expires: 7 });
            
            // Retry original request with new token
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
            }
            return api(originalRequest);
          } catch (refreshError) {
            // Refresh failed, redirect to login
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        } else {
          // No refresh token, redirect to login
          window.location.href = '/login';
        }
      }
      
      return Promise.reject(error);
    }
  );
}

// Generic API functions with fallback to mock
export const apiClient = {
  get: async <T>(url: string, params?: QueryParams): Promise<T> => {
    if (USE_MOCK_API || !apiAvailable) {
      return mockApiClient.get<T>(url, params);
    }
    
    try {
      const response = await api.get(url, { params });
      return response.data;
    } catch (error) {
      console.warn('API request failed, falling back to mock:', error);
      apiAvailable = false;
      return mockApiClient.get<T>(url, params);
    }
  },
  
  post: async <T>(url: string, data?: any): Promise<T> => {
    if (USE_MOCK_API || !apiAvailable) {
      return mockApiClient.post<T>(url, data);
    }
    
    try {
      const response = await api.post(url, data);
      return response.data;
    } catch (error) {
      console.warn('API request failed, falling back to mock:', error);
      apiAvailable = false;
      return mockApiClient.post<T>(url, data);
    }
  },
  
  put: async <T>(url: string, data?: any): Promise<T> => {
    if (USE_MOCK_API || !apiAvailable) {
      return mockApiClient.put<T>(url, data);
    }
    
    try {
      const response = await api.put(url, data);
      return response.data;
    } catch (error) {
      console.warn('API request failed, falling back to mock:', error);
      apiAvailable = false;
      return mockApiClient.put<T>(url, data);
    }
  },
  
  patch: async <T>(url: string, data?: any): Promise<T> => {
    if (USE_MOCK_API || !apiAvailable) {
      return mockApiClient.patch<T>(url, data);
    }
    
    try {
      const response = await api.patch(url, data);
      return response.data;
    } catch (error) {
      console.warn('API request failed, falling back to mock:', error);
      apiAvailable = false;
      return mockApiClient.patch<T>(url, data);
    }
  },
  
  delete: async <T>(url: string): Promise<T> => {
    if (USE_MOCK_API || !apiAvailable) {
      return mockApiClient.delete<T>(url);
    }
    
    try {
      const response = await api.delete(url);
      return response.data;
    } catch (error) {
      console.warn('API request failed, falling back to mock:', error);
      apiAvailable = false;
      return mockApiClient.delete<T>(url);
    }
  },
  
  upload: async <T>(url: string, formData: FormData): Promise<T> => {
    if (USE_MOCK_API || !apiAvailable) {
      return mockApiClient.upload<T>(url, formData);
    }
    
    try {
      const response = await api.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.warn('API request failed, falling back to mock:', error);
      apiAvailable = false;
      return mockApiClient.upload<T>(url, formData);
    }
  },
};

// Authentication API
export const authApi = {
  login: async (email: string, password: string): Promise<AuthTokens> => {
    if (USE_MOCK_API || !apiAvailable) {
      return mockApiClient.post('/auth/login', { username: email, password });
    }
    
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    } catch (error) {
      console.warn('Login API failed, falling back to mock:', error);
      apiAvailable = false;
      return mockApiClient.post('/auth/login', { username: email, password });
    }
  },
  
  register: async (userData: {
    email: string;
    username: string;
    full_name: string;
    password: string;
  }) => {
    return apiClient.post('/auth/register', userData);
  },
  
  getCurrentUser: () => {
    return apiClient.get('/auth/me');
  },
  
  logout: () => {
    return apiClient.post('/auth/logout');
  },
  
  refreshToken: (refreshToken: string) => {
    return apiClient.post('/auth/refresh', { refresh_token: refreshToken });
  },
};

// Assets API
export const assetsApi = {
  getAssets: (params?: QueryParams) => {
    return apiClient.get('/assets/', params);
  },
  
  getAsset: (id: number) => {
    return apiClient.get(`/assets/${id}`);
  },
  
  createAsset: (data: any) => {
    return apiClient.post('/assets/', data);
  },
  
  updateAsset: (id: number, data: any) => {
    return apiClient.put(`/assets/${id}`, data);
  },
  
  deleteAsset: (id: number) => {
    return apiClient.delete(`/assets/${id}`);
  },
  
  importAssets: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload('/assets/import', formData);
  },
  
  getAssetCategories: () => {
    return apiClient.get('/assets/categories/');
  },
  
  getAssetsSummary: () => {
    return apiClient.get('/assets/summary');
  },
};

// Risks API
export const risksApi = {
  getRisks: (params?: QueryParams) => {
    return apiClient.get('/risks/', params);
  },
  
  getRisk: (id: number) => {
    return apiClient.get(`/risks/${id}`);
  },
  
  createRisk: (data: any) => {
    return apiClient.post('/risks/', data);
  },
  
  updateRisk: (id: number, data: any) => {
    return apiClient.put(`/risks/${id}`, data);
  },
  
  deleteRisk: (id: number) => {
    return apiClient.delete(`/risks/${id}`);
  },
  
  getRiskSummary: () => {
    return apiClient.get('/risks/summary');
  },
  
  getRiskMatrices: () => {
    return apiClient.get('/risks/matrices/');
  },
};

// Tasks API
export const tasksApi = {
  getTasks: (params?: QueryParams) => {
    return apiClient.get('/tasks/', params);
  },
  
  getMyTasks: (status?: string) => {
    return apiClient.get('/tasks/my-tasks', { status });
  },
  
  getTask: (id: number) => {
    return apiClient.get(`/tasks/${id}`);
  },
  
  createTask: (data: any) => {
    return apiClient.post('/tasks/', data);
  },
  
  updateTask: (id: number, data: any) => {
    return apiClient.put(`/tasks/${id}`, data);
  },
  
  approveTask: (id: number, comments?: string) => {
    return apiClient.post(`/tasks/${id}/approve`, { approval_comments: comments });
  },
  
  rejectTask: (id: number, comments: string) => {
    return apiClient.post(`/tasks/${id}/reject`, { rejection_comments: comments });
  },
  
  getTasksSummary: () => {
    return apiClient.get('/tasks/summary');
  },
};

// Assessments API
export const assessmentsApi = {
  getAssessments: (params?: QueryParams) => {
    return apiClient.get('/assessments/', params);
  },
  
  getAssessment: (id: number) => {
    return apiClient.get(`/assessments/${id}`);
  },
  
  createAssessment: (data: any) => {
    return apiClient.post('/assessments/', data);
  },
  
  updateAssessment: (id: number, data: any) => {
    return apiClient.put(`/assessments/${id}`, data);
  },
  
  getAssessmentControls: (assessmentId: number) => {
    return apiClient.get(`/assessments/${assessmentId}/controls`);
  },
  
  updateAssessmentControl: (assessmentId: number, controlId: number, data: any) => {
    return apiClient.put(`/assessments/${assessmentId}/controls/${controlId}`, data);
  },
  
  getAssessmentSummary: (assessmentId: number) => {
    return apiClient.get(`/assessments/${assessmentId}/summary`);
  },
};

// Frameworks API
export const frameworksApi = {
  getFrameworks: (params?: QueryParams) => {
    return apiClient.get('/frameworks/', params);
  },
  
  getFramework: (id: number) => {
    return apiClient.get(`/frameworks/${id}`);
  },
  
  getFrameworkControls: (frameworkId: number, params?: QueryParams) => {
    return apiClient.get(`/frameworks/${frameworkId}/controls`, params);
  },
};

// Dashboard API
export const dashboardApi = {
  getOverview: () => {
    return apiClient.get('/dashboards/overview');
  },
  
  getCisoCockpit: () => {
    return apiClient.get('/dashboards/ciso-cockpit');
  },
  
  getAnalystWorkbench: () => {
    return apiClient.get('/dashboards/analyst-workbench');
  },
  
  getSystemOwnerInbox: () => {
    return apiClient.get('/dashboards/system-owner-inbox');
  },
};

// Evidence API
export const evidenceApi = {
  getEvidence: (params?: QueryParams) => {
    return apiClient.get('/evidence/', params);
  },
  
  getEvidenceItem: (id: number) => {
    return apiClient.get(`/evidence/${id}`);
  },
  
  uploadEvidence: (file: File, metadata: any) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.entries(metadata).forEach(([key, value]) => {
      formData.append(key, value as string);
    });
    return apiClient.upload('/evidence/upload', formData);
  },
  
  updateEvidence: (id: number, data: any) => {
    return apiClient.put(`/evidence/${id}`, data);
  },
  
  reviewEvidence: (id: number, approved: boolean, comments?: string) => {
    return apiClient.post(`/evidence/${id}/review`, { approved, comments });
  },
};

// AI Services API
export const aiApi = {
  analyzeEvidence: (evidenceId: number) => {
    return apiClient.post(`/ai/analyze-evidence`, { evidence_id: evidenceId });
  },
  
  generateNarrative: (assessmentControlId: number) => {
    return apiClient.post(`/ai/generate-narrative`, { assessment_control_id: assessmentControlId });
  },
  
  generateRiskStatement: (riskId: number) => {
    return apiClient.post(`/ai/generate-risk-statement`, { risk_id: riskId });
  },
  
  suggestRemediation: (taskId: number) => {
    return apiClient.post(`/ai/suggest-remediation`, { task_id: taskId });
  },
  
  generateExecutiveSummary: () => {
    return apiClient.post('/ai/generate-executive-summary');
  },
  
  getServiceStatus: () => {
    return apiClient.get('/ai/service-status');
  },
  
  // AI Provider Management
  getProvidersStatus: () => {
    return apiClient.get('/ai/providers/status');
  },
  
  testProvider: (providerName: string, testMessage: string) => {
    return apiClient.post('/ai/providers/test', { provider_name: providerName, test_message: testMessage });
  },
  
  getRecommendedProvider: (taskType: string) => {
    return apiClient.get(`/ai/providers/recommended?task_type=${taskType}`);
  },
  
  getUsageSummary: () => {
    return apiClient.get('/ai/usage/summary');
  },
  
  // Enhanced AI Functions
  analyzeEvidenceEnhanced: (data: any) => {
    return apiClient.post('/ai/analyze-evidence', data);
  },
  
  generateNarrativeEnhanced: (data: any) => {
    return apiClient.post('/ai/generate-narrative', data);
  },
  
  generateRisk: (data: any) => {
    return apiClient.post('/ai/generate-risk', data);
  },
  
  generateRemediation: (data: any) => {
    return apiClient.post('/ai/generate-remediation', data);
  },
};

// Integrations API
export const integrationsApi = {
  getIntegrations: () => {
    return apiClient.get('/integrations/');
  },
  
  configureOpenVas: (config: any) => {
    return apiClient.post('/integrations/openvas/configure', config);
  },
  
  configureOpenCti: (config: any) => {
    return apiClient.post('/integrations/opencti/configure', config);
  },
  
  testConnection: (integrationId: number) => {
    return apiClient.post(`/integrations/test-connection/${integrationId}`);
  },
  
  syncData: (integrationId: number) => {
    return apiClient.post(`/integrations/sync/${integrationId}`);
  },
  
  getVulnerabilities: (params?: QueryParams) => {
    return apiClient.get('/integrations/vulnerabilities', params);
  },
  
  getThreatIntelligence: (params?: QueryParams) => {
    return apiClient.get('/integrations/threat-intelligence', params);
  },
};

export default apiClient;
