import axios, { AxiosResponse, AxiosError } from 'axios';
import Cookies from 'js-cookie';
import { ApiResponse, AuthTokens, QueryParams } from '@/types';

// Create axios instance - ALWAYS use real backend
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:30641/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
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
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper function for API calls
const apiCall = async <T = any>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  endpoint: string,
  data?: any,
  params?: QueryParams
): Promise<T> => {
  try {
    const response = await api({
      method,
      url: endpoint,
      data,
      params,
    });
    return response.data;
  } catch (error: any) {
    console.error(`API ${method} ${endpoint} failed:`, error);
    throw error;
  }
};

// Authentication API
export const authApi = {
  login: async (email: string, password: string) => {
    return apiCall<{ access_token: string; refresh_token: string; user: any }>('POST', '/auth/login', {
      username: email,
      password,
    });
  },

  register: async (userData: any) => {
    return apiCall('POST', '/auth/register', userData);
  },

  logout: async () => {
    return apiCall('POST', '/auth/logout');
  },

  getCurrentUser: async () => {
    return apiCall('GET', '/auth/me');
  },

  refreshToken: async (refreshToken: string) => {
    return apiCall<AuthTokens>('POST', '/auth/refresh', { refresh_token: refreshToken });
  },
};

// Assets API
export const assetsApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/assets', undefined, params),
  getById: (id: string) => apiCall('GET', `/assets/${id}`),
  create: (data: any) => apiCall('POST', '/assets', data),
  update: (id: string, data: any) => apiCall('PUT', `/assets/${id}`, data),
  delete: (id: string) => apiCall('DELETE', `/assets/${id}`),
};

// Risks API
export const risksApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/risks', undefined, params),
  getById: (id: string) => apiCall('GET', `/risks/${id}`),
  create: (data: any) => apiCall('POST', '/risks', data),
  update: (id: string, data: any) => apiCall('PUT', `/risks/${id}`, data),
  delete: (id: string) => apiCall('DELETE', `/risks/${id}`),
};

// Tasks API
export const tasksApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/tasks', undefined, params),
  getById: (id: string) => apiCall('GET', `/tasks/${id}`),
  create: (data: any) => apiCall('POST', '/tasks', data),
  update: (id: string, data: any) => apiCall('PUT', `/tasks/${id}`, data),
  delete: (id: string) => apiCall('DELETE', `/tasks/${id}`),
};

// Assessments API
export const assessmentsApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/assessments', undefined, params),
  getById: (id: string) => apiCall('GET', `/assessments/${id}`),
  create: (data: any) => apiCall('POST', '/assessments', data),
  update: (id: string, data: any) => apiCall('PUT', `/assessments/${id}`, data),
  delete: (id: string) => apiCall('DELETE', `/assessments/${id}`),
};

// Evidence API
export const evidenceApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/evidence', undefined, params),
  getById: (id: string) => apiCall('GET', `/evidence/${id}`),
  create: (data: any) => apiCall('POST', '/evidence', data),
  update: (id: string, data: any) => apiCall('PUT', `/evidence/${id}`, data),
  delete: (id: string) => apiCall('DELETE', `/evidence/${id}`),
};

// Reports API
export const reportsApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/reports', undefined, params),
  getById: (id: string) => apiCall('GET', `/reports/${id}`),
  generate: (data: any) => apiCall('POST', '/reports/generate', data),
};

// Dashboard API
export const dashboardApi = {
  getOverview: () => apiCall('GET', '/dashboards/overview'),
  getMetrics: () => apiCall('GET', '/dashboards/metrics'),
  getRecentActivity: () => apiCall('GET', '/dashboards/recent-activity'),
  getCisoCockpit: () => apiCall('GET', '/dashboards/ciso-cockpit'),
  getAnalystWorkbench: () => apiCall('GET', '/dashboards/analyst-workbench'),
  getSystemOwner: () => apiCall('GET', '/dashboards/system-owner'),
};

// Users API
export const usersApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/users', undefined, params),
  getById: (id: string) => apiCall('GET', `/users/${id}`),
  create: (data: any) => apiCall('POST', '/users', data),
  update: (id: string, data: any) => apiCall('PUT', `/users/${id}`, data),
  delete: (id: string) => apiCall('DELETE', `/users/${id}`),
};

// Integrations API
export const integrationsApi = {
  getAll: (params?: QueryParams) => apiCall('GET', '/integrations', undefined, params),
  getById: (id: string) => apiCall('GET', `/integrations/${id}`),
  create: (data: any) => apiCall('POST', '/integrations', data),
  update: (id: string, data: any) => apiCall('PUT', `/integrations/${id}`, data),
  delete: (id: string) => apiCall('DELETE', `/integrations/${id}`),
  sync: (id: string) => apiCall('POST', `/integrations/${id}/sync`),
  test: (id: string) => apiCall('POST', `/integrations/${id}/test`),
};

// AI API
export const aiApi = {
  getProviders: () => apiCall('GET', '/ai/providers'),
  getProviderStatus: (providerId: string) => apiCall('GET', `/ai/providers/${providerId}/status`),
  getProvidersStatus: () => apiCall('GET', '/ai/providers/status'),
  getRecommendedProvider: (taskType?: string) => apiCall('GET', '/ai/providers/recommended', undefined, { task_type: taskType }),
  analyzeEvidence: (data: any) => apiCall('POST', '/ai/analyze-evidence', data),
  analyzeEvidenceEnhanced: (data: any) => apiCall('POST', '/ai/analyze-evidence-enhanced', data),
  generateRisk: (data: any) => apiCall('POST', '/ai/generate-risk', data),
  generateRemediation: (data: any) => apiCall('POST', '/ai/generate-remediation', data),
  generateNarrativeEnhanced: (data: any) => apiCall('POST', '/ai/generate-narrative-enhanced', data),
  testProvider: (providerId: string, message?: string) => apiCall('POST', `/ai/providers/${providerId}/test`, { message }),
  getAnalytics: () => apiCall('GET', '/ai/analytics'),
  getUsageSummary: () => apiCall('GET', '/ai/usage-summary'),
};

// Default export
export default api;