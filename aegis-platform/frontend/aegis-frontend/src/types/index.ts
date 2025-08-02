// Core Types for Aegis Risk Management Platform

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  roles?: Role[];
}

export interface Role {
  id: number;
  name: string;
  description: string;
  permissions: Record<string, string[]>;
  is_active: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
  user: User;
}

export interface Asset {
  id: number;
  name: string;
  description?: string;
  asset_type: string;
  category_id?: number;
  category?: AssetCategory;
  owner_id?: number;
  owner?: User;
  criticality: 'low' | 'medium' | 'high' | 'critical';
  location?: string;
  ip_address?: string;
  hostname?: string;
  operating_system?: string;
  software_version?: string;
  purchase_date?: string;
  warranty_expiry?: string;
  compliance_tags?: string[];
  metadata?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AssetCategory {
  id: number;
  name: string;
  description?: string;
  parent_category_id?: number;
  created_at: string;
  updated_at: string;
}

export interface Framework {
  id: number;
  name: string;
  version: string;
  description?: string;
  framework_type: 'compliance' | 'security' | 'custom';
  is_public: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  controls?: Control[];
}

export interface Control {
  id: number;
  framework_id: number;
  framework?: Framework;
  control_id: string;
  title: string;
  description: string;
  category?: string;
  function?: string;
  control_type: 'mandatory' | 'guidance' | 'enhancement';
  maturity_level: 'basic' | 'intermediate' | 'advanced';
  implementation_guidance?: string;
  testing_procedures?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Assessment {
  id: number;
  name: string;
  description?: string;
  framework_id: number;
  framework?: Framework;
  asset_id?: number;
  asset?: Asset;
  assessor_id: number;
  assessor?: User;
  status: 'draft' | 'in_progress' | 'under_review' | 'completed' | 'approved';
  start_date?: string;
  target_completion_date?: string;
  completion_date?: string;
  overall_score?: number;
  maturity_level?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  controls?: AssessmentControl[];
}

export interface AssessmentControl {
  id: number;
  assessment_id: number;
  assessment?: Assessment;
  control_id: number;
  control?: Control;
  implementation_status: 'implemented' | 'partially_implemented' | 'not_implemented' | 'not_applicable';
  maturity_score?: number;
  control_narrative?: string;
  assessor_notes?: string;
  evidence_required: boolean;
  evidence_provided: boolean;
  testing_date?: string;
  testing_result?: 'pass' | 'fail' | 'partial';
  ai_generated_narrative?: string;
  ai_confidence_score?: number;
  ai_last_updated?: string;
  created_at: string;
  updated_at: string;
}

export interface Risk {
  id: number;
  title: string;
  description?: string;
  category: string;
  asset_id?: number;
  asset?: Asset;
  assessment_id?: number;
  assessment?: Assessment;
  threat_source?: string;
  vulnerability?: string;
  existing_controls?: string;
  business_process?: string;
  likelihood: 'very_low' | 'low' | 'medium' | 'high' | 'very_high';
  impact: 'very_low' | 'low' | 'medium' | 'high' | 'very_high';
  inherent_risk_score?: number;
  residual_risk_score?: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  status: 'identified' | 'assessed' | 'mitigating' | 'monitoring' | 'accepted' | 'closed';
  risk_owner_id?: number;
  risk_owner?: User;
  treatment_strategy: 'mitigate' | 'transfer' | 'avoid' | 'accept';
  due_date?: string;
  ai_generated_statement?: string;
  ai_confidence_score?: number;
  ai_last_updated?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  task_type: 'remediation' | 'mitigation' | 'assessment' | 'review' | 'maintenance';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'awaiting_review' | 'completed' | 'cancelled';
  assigned_to_id?: number;
  assigned_to?: User;
  created_by_id: number;
  created_by?: User;
  risk_id?: number;
  risk?: Risk;
  asset_id?: number;
  asset?: Asset;
  due_date?: string;
  completed_date?: string;
  progress_percentage: number;
  estimated_hours?: number;
  actual_hours?: number;
  requires_approval: boolean;
  approval_status?: 'pending' | 'approved' | 'rejected';
  approved_by_id?: number;
  approved_by?: User;
  approved_at?: string;
  approval_comments?: string;
  ai_generated_plan?: string;
  ai_confidence_score?: number;
  ai_last_updated?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  id: number;
  title: string;
  description?: string;
  evidence_type: 'document' | 'screenshot' | 'configuration' | 'log' | 'certificate' | 'other';
  category?: string;
  file_name?: string;
  file_path?: string;
  file_size?: number;
  file_type?: string;
  file_hash?: string;
  content_summary?: string;
  status: 'draft' | 'under_review' | 'approved' | 'rejected';
  access_level: 'public' | 'internal' | 'confidential' | 'restricted';
  uploaded_by_id: number;
  uploaded_by?: User;
  reviewed_by_id?: number;
  reviewed_by?: User;
  reviewed_at?: string;
  review_comments?: string;
  ai_analysis?: string;
  ai_confidence_score?: number;
  ai_last_analyzed?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardMetrics {
  assets: {
    total: number;
    critical: number;
  };
  risks: {
    total: number;
    high_priority: number;
    open: number;
  };
  tasks: {
    total: number;
    open: number;
    overdue: number;
  };
  assessments: {
    total: number;
    active: number;
    completed: number;
  };
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
  details?: any;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface QueryParams {
  skip?: number;
  limit?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  [key: string]: any;
}

// Theme types
export type Theme = 'light' | 'dark' | 'system';

// Navigation types
export interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
  badge?: number;
  children?: NavigationItem[];
}

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox' | 'date' | 'file';
  placeholder?: string;
  required?: boolean;
  options?: { value: string; label: string }[];
  validation?: any;
}