// Workflow Engine Types for Aegis Risk Management Platform

import { User } from './index';

export type WorkflowType = 
  | 'risk_approval'
  | 'task_approval' 
  | 'assessment_approval'
  | 'evidence_approval'
  | 'user_access_request'
  | 'budget_approval'
  | 'exception_request'
  | 'custom';

export type WorkflowStatus = 
  | 'draft'
  | 'active'
  | 'inactive'
  | 'archived';

export type WorkflowStepType = 
  | 'approval'
  | 'review'
  | 'notification'
  | 'conditional'
  | 'parallel'
  | 'automated';

export type WorkflowInstanceStatus = 
  | 'initiated'
  | 'in_progress'
  | 'pending_approval'
  | 'approved'
  | 'rejected'
  | 'cancelled'
  | 'completed'
  | 'error';

export type WorkflowStepStatus = 
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'skipped'
  | 'rejected'
  | 'error';

export type ActionType = 
  | 'approve'
  | 'reject'
  | 'comment'
  | 'reassign'
  | 'escalate'
  | 'request_information'
  | 'cancel';

export interface WorkflowStep {
  id: number;
  workflow_id: number;
  name: string;
  description?: string;
  step_type: WorkflowStepType;
  step_order: number;
  is_required: boolean;
  can_skip: boolean;
  allow_parallel: boolean;
  assignee_type?: string; // "user", "role", "group", "auto"
  assignee_id?: number;
  auto_assign_rule?: Record<string, any>;
  approval_required: boolean;
  min_approvals: number;
  unanimous_required: boolean;
  timeout_hours?: number;
  reminder_hours: number;
  escalation_assignee_id?: number;
  condition_expression?: Record<string, any>;
  allowed_actions?: ActionType[];
  on_approve_action?: Record<string, any>;
  on_reject_action?: Record<string, any>;
  custom_fields?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface Workflow {
  id: number;
  name: string;
  description?: string;
  workflow_type: WorkflowType;
  category?: string;
  version: string;
  status: WorkflowStatus;
  is_default: boolean;
  trigger_conditions?: Record<string, any>;
  auto_trigger: boolean;
  default_timeout_hours: number;
  escalation_enabled: boolean;
  escalation_timeout_hours: number;
  notification_template_id?: number;
  notify_on_start: boolean;
  notify_on_completion: boolean;
  tags?: string[];
  custom_fields?: Record<string, any>;
  created_by_id: number;
  created_by?: User;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  steps: WorkflowStep[];
}

export interface WorkflowInstance {
  id: number;
  workflow_id: number;
  workflow?: Workflow;
  name?: string;
  description?: string;
  entity_type: string; // "risk", "task", "assessment", etc.
  entity_id: number;
  status: WorkflowInstanceStatus;
  current_step_id?: number;
  context_data?: Record<string, any>;
  initiated_by_id: number;
  initiated_by?: User;
  current_assignee_id?: number;
  current_assignee?: User;
  initiated_at: string;
  started_at?: string;
  completed_at?: string;
  due_date?: string;
  final_outcome?: string;
  outcome_reason?: string;
  priority: string;
  escalation_level: number;
  last_escalated_at?: string;
  tags?: string[];
  custom_fields?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowStepInstance {
  id: number;
  workflow_instance_id: number;
  workflow_instance?: WorkflowInstance;
  workflow_step_id: number;
  workflow_step?: WorkflowStep;
  status: WorkflowStepStatus;
  step_order: number;
  assigned_to_id?: number;
  assigned_to?: User;
  assigned_at?: string;
  started_at?: string;
  completed_at?: string;
  due_date?: string;
  outcome?: string;
  outcome_reason?: string;
  reminder_sent_at?: string;
  escalated_at?: string;
  escalated_to_id?: number;
  escalated_to?: User;
  step_data?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowAction {
  id: number;
  workflow_instance_id: number;
  workflow_instance?: WorkflowInstance;
  step_instance_id?: number;
  step_instance?: WorkflowStepInstance;
  action_type: ActionType;
  action_description?: string;
  performed_by_id: number;
  performed_by?: User;
  on_behalf_of_id?: number;
  on_behalf_of?: User;
  comment?: string;
  attachments?: string[];
  result_status?: string;
  result_data?: Record<string, any>;
  performed_at: string;
}

export interface WorkflowTemplate {
  id: number;
  name: string;
  description?: string;
  category?: string;
  workflow_type?: WorkflowType;
  template_data: Record<string, any>;
  version: string;
  is_system_template: boolean;
  is_public: boolean;
  usage_count: number;
  tags?: string[];
  created_by_id?: number;
  created_by?: User;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowRole {
  id: number;
  name: string;
  description?: string;
  is_system_role: boolean;
  permissions?: string[];
  members?: number[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowSummary {
  total_workflows: number;
  active_workflows: number;
  pending_instances: number;
  overdue_instances: number;
  completed_today: number;
  approval_rate: number;
  average_completion_time_hours: number;
}

export interface WorkflowDashboard {
  summary: WorkflowSummary;
  my_pending_actions: WorkflowStepInstance[];
  recent_workflows: WorkflowInstance[];
  overdue_workflows: WorkflowInstance[];
}

// Create/Update interfaces
export interface WorkflowCreateData {
  name: string;
  description?: string;
  workflow_type: WorkflowType;
  category?: string;
  version?: string;
  status?: WorkflowStatus;
  is_default?: boolean;
  trigger_conditions?: Record<string, any>;
  auto_trigger?: boolean;
  default_timeout_hours?: number;
  escalation_enabled?: boolean;
  escalation_timeout_hours?: number;
  notification_template_id?: number;
  notify_on_start?: boolean;
  notify_on_completion?: boolean;
  tags?: string[];
  custom_fields?: Record<string, any>;
  steps?: WorkflowStepCreateData[];
}

export interface WorkflowStepCreateData {
  name: string;
  description?: string;
  step_type: WorkflowStepType;
  step_order: number;
  is_required?: boolean;
  can_skip?: boolean;
  allow_parallel?: boolean;
  assignee_type?: string;
  assignee_id?: number;
  auto_assign_rule?: Record<string, any>;
  approval_required?: boolean;
  min_approvals?: number;
  unanimous_required?: boolean;
  timeout_hours?: number;
  reminder_hours?: number;
  escalation_assignee_id?: number;
  condition_expression?: Record<string, any>;
  allowed_actions?: ActionType[];
  on_approve_action?: Record<string, any>;
  on_reject_action?: Record<string, any>;
  custom_fields?: Record<string, any>;
}

export interface WorkflowInstanceCreateData {
  workflow_id: number;
  name?: string;
  description?: string;
  entity_type: string;
  entity_id: number;
  context_data?: Record<string, any>;
  priority?: string;
  tags?: string[];
  custom_fields?: Record<string, any>;
}

export interface WorkflowExecutionRequest {
  action_type: ActionType;
  comment?: string;
  attachments?: string[];
  reassign_to_id?: number; // For reassignment actions
  escalate_to_id?: number; // For escalation actions
}

export interface WorkflowTriggerRequest {
  workflow_id: number;
  entity_type: string;
  entity_id: number;
  context_data?: Record<string, any>;
  priority?: string;
  custom_fields?: Record<string, any>;
}

export interface BulkWorkflowAction {
  workflow_instance_ids: number[];
  action_type: ActionType;
  comment?: string;
}

export interface BulkWorkflowActionResult {
  success_count: number;
  failure_count: number;
  results: Array<{
    instance_id: number;
    status: 'success' | 'failure';
    action_id?: number;
    error?: string;
  }>;
}

// UI-specific interfaces
export interface WorkflowFilters {
  status?: WorkflowInstanceStatus[];
  entity_type?: string[];
  priority?: string[];
  assigned_to_me?: boolean;
  created_by_me?: boolean;
  date_range?: {
    start: string;
    end: string;
  };
}

export interface WorkflowStepConfig {
  step: WorkflowStep;
  users: User[];
  roles: WorkflowRole[];
}

export interface WorkflowBuilder {
  workflow: Partial<WorkflowCreateData>;
  steps: WorkflowStepCreateData[];
  currentStep: number;
  validationErrors: Record<string, string>;
}

// Status color mappings for UI
export const WORKFLOW_STATUS_COLORS = {
  // Workflow statuses
  draft: 'gray',
  active: 'green',
  inactive: 'yellow',
  archived: 'gray',
  
  // Instance statuses
  initiated: 'blue',
  in_progress: 'blue',
  pending_approval: 'yellow',
  approved: 'green',
  rejected: 'red',
  cancelled: 'gray',
  completed: 'green',
  error: 'red',
  
  // Step statuses
  pending: 'gray',
  step_completed: 'green',
  skipped: 'yellow',
} as const;

export const WORKFLOW_TYPE_LABELS = {
  risk_approval: 'Risk Approval',
  task_approval: 'Task Approval',
  assessment_approval: 'Assessment Approval',
  evidence_approval: 'Evidence Approval',
  user_access_request: 'User Access Request',
  budget_approval: 'Budget Approval',
  exception_request: 'Exception Request',
  custom: 'Custom',
} as const;

export const STEP_TYPE_LABELS = {
  approval: 'Approval',
  review: 'Review',
  notification: 'Notification',
  conditional: 'Conditional',
  parallel: 'Parallel',
  automated: 'Automated',
} as const;

export const ACTION_TYPE_LABELS = {
  approve: 'Approve',
  reject: 'Reject',
  comment: 'Comment',
  reassign: 'Reassign',
  escalate: 'Escalate',
  request_information: 'Request Information',
  cancel: 'Cancel',
} as const;