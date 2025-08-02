// Mock API for development and demo purposes
// This provides the same interface as the real API but with mock data

export const mockApiClient = {
  get: async <T>(url: string, params?: any): Promise<T> => {
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    
    if (url.includes('/auth/me')) {
      return {
        id: 1,
        email: 'admin@aegis-platform.com',
        username: 'admin',
        full_name: 'System Administrator',
        role: 'admin',
        is_active: true,
        permissions: ['read', 'write', 'admin']
      } as T;
    }
    
    if (url.includes('/ai/providers/status')) {
      return {
        openai: {
          enabled: true,
          status: 'healthy',
          requests_count: 1247,
          success_rate: 98.5,
          avg_response_time: 1.2,
          total_cost: 45.67,
          capabilities: {
            supports_streaming: true,
            supports_function_calling: true,
            supports_vision: false,
            supports_embeddings: true,
            max_context_length: 8192,
            supports_json_mode: true,
            supports_system_messages: true
          },
          cost_tracking: {
            daily_cost: 12.34,
            daily_requests: 156,
            last_reset: Date.now() - 86400000
          }
        },
        azure_openai: {
          enabled: false,
          status: 'disabled',
          requests_count: 0,
          success_rate: 0,
          avg_response_time: 0,
          total_cost: 0,
          capabilities: {
            supports_streaming: true,
            supports_function_calling: true,
            supports_vision: true,
            supports_embeddings: true,
            max_context_length: 32768,
            supports_json_mode: true,
            supports_system_messages: true
          },
          cost_tracking: {
            daily_cost: 0,
            daily_requests: 0,
            last_reset: Date.now()
          }
        },
        gemini: {
          enabled: true,
          status: 'degraded',
          requests_count: 89,
          success_rate: 85.2,
          avg_response_time: 2.8,
          total_cost: 8.91,
          capabilities: {
            supports_streaming: true,
            supports_function_calling: true,
            supports_vision: true,
            supports_embeddings: false,
            max_context_length: 32768,
            supports_json_mode: true,
            supports_system_messages: true
          },
          cost_tracking: {
            daily_cost: 3.21,
            daily_requests: 23,
            last_reset: Date.now() - 43200000
          }
        },
        deepseek: {
          enabled: true,
          status: 'healthy',
          requests_count: 567,
          success_rate: 96.8,
          avg_response_time: 0.9,
          total_cost: 2.34,
          capabilities: {
            supports_streaming: true,
            supports_function_calling: false,
            supports_vision: false,
            supports_embeddings: false,
            max_context_length: 16384,
            supports_json_mode: true,
            supports_system_messages: true
          },
          cost_tracking: {
            daily_cost: 0.89,
            daily_requests: 67,
            last_reset: Date.now() - 21600000
          }
        }
      } as T;
    }
    
    if (url.includes('/ai/usage/summary')) {
      return {
        total_requests: 1903,
        total_cost: 56.92,
        average_success_rate: 94.6,
        active_providers: 3,
        provider_breakdown: {
          openai: {
            enabled: true,
            status: 'healthy',
            requests_count: 1247,
            success_rate: 98.5,
            avg_response_time: 1.2,
            total_cost: 45.67
          },
          gemini: {
            enabled: true,
            status: 'degraded',
            requests_count: 89,
            success_rate: 85.2,
            avg_response_time: 2.8,
            total_cost: 8.91
          },
          deepseek: {
            enabled: true,
            status: 'healthy',
            requests_count: 567,
            success_rate: 96.8,
            avg_response_time: 0.9,
            total_cost: 2.34
          }
        }
      } as T;
    }
    
    if (url.includes('/ai/providers/recommended')) {
      return {
        recommended_provider: 'openai',
        reason: 'Best performance for general tasks',
        alternatives: ['deepseek', 'gemini']
      } as T;
    }
    
    if (url.includes('/dashboards/overview')) {
      return {
        assets: {
          total: 45,
          critical: 8
        },
        risks: {
          total: 23,
          high_priority: 8,
          open: 19
        },
        tasks: {
          total: 18,
          open: 13,
          overdue: 4
        },
        assessments: {
          total: 7,
          active: 3,
          completed: 4
        }
      } as T;
    }
    
    if (url.includes('/assets/')) {
      return {
        results: [
          {
            id: 1,
            name: 'Production Web Server',
            type: 'Server',
            category: 'Infrastructure',
            criticality: 'High',
            owner: 'IT Operations',
            last_updated: new Date().toISOString()
          },
          {
            id: 2,
            name: 'Customer Database',
            type: 'Database',
            category: 'Data',
            criticality: 'Critical',
            owner: 'Data Team',
            last_updated: new Date(Date.now() - 86400000).toISOString()
          }
        ],
        total: 247,
        page: 1,
        size: 10
      } as T;
    }
    
    if (url.includes('/risks/')) {
      return {
        results: [
          {
            id: 1,
            title: 'Web Application Vulnerability',
            description: 'SQL injection vulnerability in user login form',
            risk_score: 8.5,
            likelihood: 'High',
            impact: 'High',
            status: 'Open',
            assigned_to: 'security.team@company.com',
            created_at: new Date().toISOString()
          },
          {
            id: 2,
            title: 'Unpatched Operating System',
            description: 'Critical security patches missing on production servers',
            risk_score: 7.2,
            likelihood: 'Medium',
            impact: 'High',
            status: 'In Progress',
            assigned_to: 'it.operations@company.com',
            created_at: new Date(Date.now() - 172800000).toISOString()
          }
        ],
        total: 23,
        page: 1,
        size: 10
      } as T;
    }
    
    // Default response for unhandled URLs
    return { message: 'Mock API response', data: [] } as T;
  },
  
  post: async <T>(url: string, data?: any): Promise<T> => {
    await new Promise(resolve => setTimeout(resolve, 800)); // Simulate network delay
    
    if (url.includes('/auth/login')) {
      return {
        access_token: 'mock-jwt-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        expires_in: 3600
      } as T;
    }
    
    if (url.includes('/ai/providers/test')) {
      const provider = data?.provider_name || 'openai';
      return {
        test_successful: Math.random() > 0.2, // 80% success rate
        provider_used: provider,
        response: 'This is a test response from the AI provider.',
        response_time: Math.random() * 3 + 0.5,
        cost: Math.random() * 0.01,
        timestamp: new Date().toISOString()
      } as T;
    }
    
    if (url.includes('/ai/analyze-evidence')) {
      return {
        summary: 'The evidence contains comprehensive security policies covering data encryption, access controls, and incident response procedures.',
        key_findings: [
          'Strong encryption requirements for data at rest and in transit',
          'Multi-factor authentication mandated for all privileged accounts',
          'Incident response procedures clearly documented with escalation paths',
          'Regular security awareness training requirements specified'
        ],
        control_mappings: ['AC-2', 'AC-3', 'IR-1', 'SC-8', 'SC-13'],
        compliance_assessment: 'The policy adequately addresses the control requirements with specific implementation details.',
        provider_used: 'openai',
        response_time: 2.3,
        cost: 0.0045,
        timestamp: new Date().toISOString()
      } as T;
    }
    
    if (url.includes('/ai/generate-narrative')) {
      return {
        narrative: 'Based on the uploaded evidence and policy documentation, this control is implemented through a comprehensive set of security policies and procedures. The organization has established clear guidelines for access control management, including user account provisioning, regular access reviews, and privileged account management. The documented procedures demonstrate alignment with industry best practices and regulatory requirements.',
        provider_used: 'openai',
        response_time: 1.8,
        cost: 0.0032,
        timestamp: new Date().toISOString()
      } as T;
    }
    
    if (url.includes('/ai/generate-risk')) {
      return {
        risk_statement: 'There is a risk that unauthorized users could gain access to sensitive customer data through the web application due to inadequate input validation and insufficient access controls, potentially resulting in data breach, regulatory non-compliance, and significant reputational damage.',
        risk_factors: [
          'Lack of proper input sanitization in user forms',
          'Insufficient session management controls',
          'Missing web application firewall protection',
          'Inadequate logging and monitoring capabilities'
        ],
        threat_sources: ['External attackers', 'Malicious insiders', 'Automated attack tools'],
        business_impact: 'A successful attack could result in exposure of customer PII, financial losses due to regulatory fines, loss of customer trust, and potential legal liability.',
        risk_score: 8.5,
        provider_used: 'openai',
        response_time: 2.1,
        cost: 0.0078,
        timestamp: new Date().toISOString()
      } as T;
    }
    
    if (url.includes('/ai/generate-remediation')) {
      return {
        remediation_plan: [
          'Implement comprehensive input validation for all user inputs',
          'Deploy and configure a web application firewall (WAF)',
          'Conduct a thorough security code review and penetration testing',
          'Implement proper session management and timeout controls',
          'Enable comprehensive logging and monitoring for security events',
          'Provide security awareness training to development team',
          'Establish regular security testing and vulnerability scanning'
        ],
        provider_used: 'openai',
        response_time: 1.9,
        cost: 0.0056,
        timestamp: new Date().toISOString()
      } as T;
    }
    
    // Dashboard statistics endpoints
    if (url.includes('/dashboard/stats') || url.includes('/dashboard/overview')) {
      return {
        assets: {
          total: 45,
          critical: 8
        },
        risks: {
          total: 23,
          high_priority: 8,
          open: 19
        },
        tasks: {
          total: 18,
          open: 13,
          overdue: 4
        },
        assessments: {
          total: 7,
          active: 3,
          completed: 4
        }
      } as T;
    }
    
    // Assets endpoints
    if (url.includes('/assets')) {
      return {
        total: 45,
        items: [
          {
            id: 1,
            name: 'Web Application Server',
            description: 'Primary web application server hosting customer portal',
            asset_type: 'Server',
            criticality: 'high',
            location: 'Data Center 1',
            owner: 'IT Team',
            is_active: true,
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-07T00:00:00Z'
          },
          {
            id: 2,
            name: 'Database Server',
            description: 'Primary MySQL database server',
            asset_type: 'Database',
            criticality: 'critical',
            location: 'Data Center 1',
            owner: 'Database Team',
            is_active: true,
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-07T00:00:00Z'
          }
        ]
      } as T;
    }
    
    // Risks endpoints
    if (url.includes('/risks')) {
      return {
        total: 23,
        items: [
          {
            id: 1,
            title: 'Unauthorized Access to Database',
            description: 'Risk of unauthorized users gaining access to sensitive customer data',
            likelihood: 4,
            impact: 5,
            risk_score: 20,
            status: 'open',
            owner: 'Security Team',
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-07T00:00:00Z'
          },
          {
            id: 2,
            title: 'Malware Infection on Workstations',
            description: 'Risk of malware infection compromising employee workstations',
            likelihood: 3,
            impact: 3,
            risk_score: 9,
            status: 'open',
            owner: 'IT Security',
            created_at: '2025-01-02T00:00:00Z',
            updated_at: '2025-01-07T00:00:00Z'
          }
        ]
      } as T;
    }
    
    // Tasks endpoints
    if (url.includes('/tasks')) {
      return {
        total: 18,
        items: [
          {
            id: 1,
            title: 'Implement Multi-Factor Authentication',
            description: 'Deploy MFA for all privileged user accounts',
            priority: 'high',
            status: 'in_progress',
            due_date: '2025-02-15T00:00:00Z',
            assigned_to: 'Security Analyst',
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-07T00:00:00Z'
          },
          {
            id: 2,
            title: 'Update Antivirus Definitions',
            description: 'Ensure all workstations have latest antivirus definitions',
            priority: 'medium',
            status: 'pending',
            due_date: '2025-01-14T00:00:00Z',
            assigned_to: 'IT Support',
            created_at: '2025-01-03T00:00:00Z',
            updated_at: '2025-01-07T00:00:00Z'
          }
        ]
      } as T;
    }
    
    // Assessments endpoints  
    if (url.includes('/assessments')) {
      return {
        total: 7,
        items: [
          {
            id: 1,
            name: 'Q1 2025 Security Assessment',
            description: 'Quarterly security assessment for NIST CSF compliance',
            status: 'in_progress',
            start_date: '2025-01-01T00:00:00Z',
            target_completion_date: '2025-01-31T00:00:00Z',
            assessor: 'Security Analyst',
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-07T00:00:00Z'
          }
        ]
      } as T;
    }

    return { message: 'Mock API response', success: true } as T;
  },
  
  put: async <T>(url: string, data?: any): Promise<T> => {
    await new Promise(resolve => setTimeout(resolve, 600));
    return { message: 'Mock update successful', data } as T;
  },
  
  patch: async <T>(url: string, data?: any): Promise<T> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return { message: 'Mock patch successful', data } as T;
  },
  
  delete: async <T>(url: string): Promise<T> => {
    await new Promise(resolve => setTimeout(resolve, 400));
    return { message: 'Mock delete successful' } as T;
  },
  
  upload: async <T>(url: string, formData: FormData): Promise<T> => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return { message: 'Mock upload successful', file_id: Math.floor(Math.random() * 1000) } as T;
  }
};

// Export the same interface as the real API
export default mockApiClient;