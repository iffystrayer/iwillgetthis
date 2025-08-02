// AI API Response Types

export interface ProviderCapabilities {
  supports_streaming: boolean;
  supports_function_calling: boolean;
  supports_vision: boolean;
  supports_embeddings: boolean;
  max_context_length: number;
  supports_json_mode: boolean;
  supports_system_messages: boolean;
}

export interface CostTracking {
  daily_cost: number;
  daily_requests: number;
  last_reset: number;
}

export interface ProviderStatus {
  enabled: boolean;
  status: string;
  requests_count: number;
  success_rate: number;
  avg_response_time: number;
  total_cost: number;
  capabilities: ProviderCapabilities;
  cost_tracking: CostTracking;
}

export interface ProvidersStatus {
  [key: string]: ProviderStatus;
}

export interface UsageSummary {
  total_requests: number;
  total_cost: number;
  average_success_rate: number;
  active_providers: number;
  provider_breakdown: {
    [key: string]: {
      enabled: boolean;
      status: string;
      requests_count: number;
      success_rate: number;
      avg_response_time: number;
      total_cost: number;
    };
  };
}

export interface EvidenceAnalysisResponse {
  summary: string;
  key_findings: string[];
  control_mappings: string[];
  compliance_assessment: string;
  provider_used: string;
  response_time: number;
  cost: number;
  timestamp: string;
  generated_narrative?: string;
  narrative_provider?: string;
}

export interface NarrativeResponse {
  narrative: string;
  provider_used: string;
  response_time: number;
  cost: number;
  timestamp: string;
}

export interface RiskGenerationResponse {
  risk_statement: string;
  risk_factors: string[];
  threat_sources: string[];
  business_impact: string;
  risk_score: number;
  asset_context?: string;
  provider_used: string;
  response_time: number;
  cost: number;
  timestamp: string;
  remediation_plan?: string[] | string;
  remediation_provider?: string;
}

export interface RemediationResponse {
  remediation_plan: string[] | string;
  provider_used: string;
  response_time: number;
  cost: number;
  timestamp: string;
}

export interface ProviderTestResponse {
  test_successful: boolean;
  provider_used: string;
  response: string;
  response_time: number;
  cost: number;
  timestamp: string;
  error?: string;
}

export interface RecommendedProviderResponse {
  recommended_provider: string;
  reason: string;
  alternatives: string[];
}
