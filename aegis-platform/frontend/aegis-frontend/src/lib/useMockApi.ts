// Hook to toggle between real API and mock API for development
import { useState, useEffect } from 'react';

// Check if we should use mock API based on environment or API availability
const shouldUseMockApi = () => {
  // Use mock API if VITE_USE_MOCK_API is set to true
  if (import.meta.env.VITE_USE_MOCK_API === 'true') {
    return true;
  }
  
  // Use mock API if we're in development and no API URL is configured
  if (import.meta.env.DEV && !import.meta.env.VITE_API_URL) {
    return true;
  }
  
  return false;
};

export const useMockApi = () => {
  const [useMock, setUseMock] = useState(shouldUseMockApi());
  
  // Test API connectivity and fall back to mock if needed
  useEffect(() => {
    const testApiConnectivity = async () => {
      if (!shouldUseMockApi() && import.meta.env.VITE_API_URL) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 3000);
          
          const response = await fetch(import.meta.env.VITE_API_URL.replace('/api/v1', '/health'), {
            signal: controller.signal,
            method: 'GET'
          });
          
          clearTimeout(timeoutId);
          
          if (!response.ok) {
            console.warn('API health check failed, falling back to mock API');
            setUseMock(true);
          }
        } catch (error) {
          console.warn('API connectivity test failed, using mock API:', error);
          setUseMock(true);
        }
      }
    };
    
    testApiConnectivity();
  }, []);
  
  return { useMock, setUseMock };
};

export const getApiClient = () => {
  const { useMock } = useMockApi();
  
  if (useMock) {
    return import('./mockApi').then(module => module.default);
  } else {
    return import('./api').then(module => module.default);
  }
};
