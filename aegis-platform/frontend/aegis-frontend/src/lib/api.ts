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
  import: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiCall('POST', '/assets/import', formData);
  },
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
  upload: async (formData: FormData, title: string, evidenceType: string, description?: string) => {
    try {
      // Backend expects title and evidence_type as query parameters
      const params = new URLSearchParams();
      params.append('title', title);
      params.append('evidence_type', evidenceType);
      if (description) {
        params.append('description', description);
      }

      const response = await api({
        method: 'POST',
        url: `/evidence/upload?${params.toString()}`,
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      console.error('Evidence upload failed:', error);
      throw error;
    }
  },
  download: (id: string) => {
    return api({
      method: 'GET',
      url: `/evidence/${id}/download`,
      responseType: 'blob',
    });
  },
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
  getSystemOwner: () => apiCall('GET', '/dashboards/system-owner-inbox'),
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
  
  // Enhanced enterprise integration endpoints
  getTypes: (category?: string) => apiCall('GET', '/integrations/types', undefined, category ? { category } : undefined),
  createConnector: (data: any) => apiCall('POST', '/integrations/connectors/create', data),
  testConnector: (connectorId: string) => apiCall('POST', `/integrations/connectors/${connectorId}/test`),
  syncConnector: (connectorId: string, options?: any) => apiCall('POST', `/integrations/connectors/${connectorId}/sync`, options),
  getConnectorStatus: (connectorId: string) => apiCall('GET', `/integrations/connectors/${connectorId}/status`),
  getSyncLogs: (connectorId: string, limit?: number) => apiCall('GET', `/integrations/sync-logs/${connectorId}`, undefined, limit ? { limit } : undefined),
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

// AI Analytics API
export const aiAnalyticsApi = {
  // Models
  getModels: (params?: QueryParams) => apiCall('GET', '/ai-analytics/models', undefined, params),
  getModel: (id: number) => apiCall('GET', `/ai-analytics/models/${id}`),
  createModel: (data: any) => apiCall('POST', '/ai-analytics/models', data),
  updateModel: (id: number, data: any) => apiCall('PUT', `/ai-analytics/models/${id}`, data),
  trainModel: (id: number, data: any) => apiCall('POST', `/ai-analytics/models/${id}/train`, data),
  evaluateModel: (id: number, params: any) => apiCall('POST', `/ai-analytics/models/${id}/evaluate`, undefined, params),
  
  // Predictions
  getPredictions: (params?: QueryParams) => apiCall('GET', '/ai-analytics/predictions', undefined, params),
  createPrediction: (data: any) => apiCall('POST', '/ai-analytics/predictions', data),
  createBulkPredictions: (data: any) => apiCall('POST', '/ai-analytics/predictions/bulk', data),
  updatePredictionOutcome: (id: number, outcome: number) => apiCall('PUT', `/ai-analytics/predictions/${id}/outcome`, { actual_outcome: outcome }),
  
  // Anomaly Detection
  detectAnomalies: (data: any) => apiCall('POST', '/ai-analytics/anomalies/detect', data),
  
  // Risk Forecasting
  generateRiskForecast: (data: any) => apiCall('POST', '/ai-analytics/forecasts/risk', data),
  
  // Alerts
  getAlerts: (params?: QueryParams) => apiCall('GET', '/ai-analytics/alerts', undefined, params),
  acknowledgeAlert: (id: number) => apiCall('PUT', `/ai-analytics/alerts/${id}/acknowledge`),
  
  // Insights
  getInsights: (params?: QueryParams) => apiCall('GET', '/ai-analytics/insights', undefined, params),
  
  // Model Comparison
  compareModels: (data: any) => apiCall('POST', '/ai-analytics/models/compare', data),
  
  // Dashboard
  getDashboard: () => apiCall('GET', '/ai-analytics/dashboard'),
};

// Default export
export default api;