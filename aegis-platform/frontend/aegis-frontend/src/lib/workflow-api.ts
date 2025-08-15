// Workflow API Client for Aegis Risk Management Platform

import api from './api';
import {
  Workflow,
  WorkflowCreateData,
  WorkflowStep,
  WorkflowStepCreateData,
  WorkflowInstance,
  WorkflowInstanceCreateData,
  WorkflowStepInstance,
  WorkflowAction,
  WorkflowTemplate,
  WorkflowRole,
  WorkflowSummary,
  WorkflowDashboard,
  WorkflowExecutionRequest,
  WorkflowTriggerRequest,
  BulkWorkflowAction,
  BulkWorkflowActionResult,
  WorkflowType,
  WorkflowInstanceStatus
} from '../types/workflow';

export class WorkflowAPI {
  private baseUrl = '/workflows';

  // Workflow CRUD operations
  async createWorkflow(workflowData: WorkflowCreateData): Promise<Workflow> {
    const response = await api.post(`${this.baseUrl}/`, workflowData);
    return response.data;
  }

  async getWorkflows(params?: {
    skip?: number;
    limit?: number;
    workflow_type?: WorkflowType;
    status?: string;
    category?: string;
  }): Promise<Workflow[]> {
    const response = await api.get(`${this.baseUrl}/`, { params });
    return response.data;
  }

  async getWorkflow(workflowId: number): Promise<Workflow> {
    const response = await api.get(`${this.baseUrl}/${workflowId}`);
    return response.data;
  }

  async updateWorkflow(workflowId: number, updateData: Partial<WorkflowCreateData>): Promise<Workflow> {
    const response = await api.put(`${this.baseUrl}/${workflowId}`, updateData);
    return response.data;
  }

  async deleteWorkflow(workflowId: number): Promise<void> {
    await api.delete(`${this.baseUrl}/${workflowId}`);
  }

  // Workflow Step operations
  async createWorkflowStep(workflowId: number, stepData: WorkflowStepCreateData): Promise<WorkflowStep> {
    const response = await api.post(`${this.baseUrl}/${workflowId}/steps`, stepData);
    return response.data;
  }

  async getWorkflowSteps(workflowId: number): Promise<WorkflowStep[]> {
    const response = await api.get(`${this.baseUrl}/${workflowId}/steps`);
    return response.data;
  }

  async updateWorkflowStep(stepId: number, updateData: Partial<WorkflowStepCreateData>): Promise<WorkflowStep> {
    const response = await api.put(`${this.baseUrl}/steps/${stepId}`, updateData);
    return response.data;
  }

  async deleteWorkflowStep(stepId: number): Promise<void> {
    await api.delete(`${this.baseUrl}/steps/${stepId}`);
  }

  // Workflow Instance operations
  async createWorkflowInstance(instanceData: WorkflowInstanceCreateData): Promise<WorkflowInstance> {
    const response = await api.post(`${this.baseUrl}/instances`, instanceData);
    return response.data;
  }

  async triggerWorkflow(triggerData: WorkflowTriggerRequest): Promise<WorkflowInstance> {
    const response = await api.post(`${this.baseUrl}/trigger`, triggerData);
    return response.data;
  }

  async getWorkflowInstances(params?: {
    skip?: number;
    limit?: number;
    status?: WorkflowInstanceStatus;
    entity_type?: string;
    assigned_to_me?: boolean;
  }): Promise<WorkflowInstance[]> {
    const response = await api.get(`${this.baseUrl}/instances`, { params });
    return response.data;
  }

  async getWorkflowInstance(instanceId: number): Promise<WorkflowInstance> {
    const response = await api.get(`${this.baseUrl}/instances/${instanceId}`);
    return response.data;
  }

  async updateWorkflowInstance(instanceId: number, updateData: Partial<WorkflowInstanceCreateData>): Promise<WorkflowInstance> {
    const response = await api.put(`${this.baseUrl}/instances/${instanceId}`, updateData);
    return response.data;
  }

  // Workflow execution
  async executeWorkflowAction(instanceId: number, actionData: WorkflowExecutionRequest): Promise<WorkflowAction> {
    const response = await api.post(`${this.baseUrl}/instances/${instanceId}/execute`, actionData);
    return response.data;
  }

  async getWorkflowActions(instanceId: number): Promise<WorkflowAction[]> {
    const response = await api.get(`${this.baseUrl}/instances/${instanceId}/actions`);
    return response.data;
  }

  async getWorkflowStepInstances(instanceId: number): Promise<WorkflowStepInstance[]> {
    const response = await api.get(`${this.baseUrl}/instances/${instanceId}/steps`);
    return response.data;
  }

  // Dashboard and summary
  async getWorkflowSummary(): Promise<WorkflowSummary> {
    const response = await api.get(`${this.baseUrl}/dashboard/summary`);
    return response.data;
  }

  async getMyWorkflowTasks(): Promise<WorkflowStepInstance[]> {
    const response = await api.get(`${this.baseUrl}/dashboard/my-tasks`);
    return response.data;
  }

  async getOverdueWorkflows(): Promise<WorkflowInstance[]> {
    const response = await api.get(`${this.baseUrl}/dashboard/overdue`);
    return response.data;
  }

  // Workflow Templates
  async createWorkflowTemplate(templateData: any): Promise<WorkflowTemplate> {
    const response = await api.post(`${this.baseUrl}/templates`, templateData);
    return response.data;
  }

  async getWorkflowTemplates(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    workflow_type?: WorkflowType;
  }): Promise<WorkflowTemplate[]> {
    const response = await api.get(`${this.baseUrl}/templates`, { params });
    return response.data;
  }

  async getWorkflowTemplate(templateId: number): Promise<WorkflowTemplate> {
    const response = await api.get(`${this.baseUrl}/templates/${templateId}`);
    return response.data;
  }

  async applyWorkflowTemplate(templateId: number): Promise<Workflow> {
    const response = await api.post(`${this.baseUrl}/templates/${templateId}/apply`);
    return response.data;
  }

  // Workflow Roles
  async createWorkflowRole(roleData: any): Promise<WorkflowRole> {
    const response = await api.post(`${this.baseUrl}/roles`, roleData);
    return response.data;
  }

  async getWorkflowRoles(): Promise<WorkflowRole[]> {
    const response = await api.get(`${this.baseUrl}/roles`);
    return response.data;
  }

  // Bulk operations
  async executeBulkWorkflowAction(bulkAction: BulkWorkflowAction): Promise<BulkWorkflowActionResult> {
    const response = await api.post(`${this.baseUrl}/instances/bulk-action`, bulkAction);
    return response.data;
  }

  // Entity-specific workflow triggers
  async triggerRiskWorkflow(riskId: number, workflowType: WorkflowType = 'risk_approval'): Promise<WorkflowInstance> {
    const response = await api.post(`${this.baseUrl}/trigger/risk/${riskId}`, { workflow_type: workflowType });
    return response.data;
  }

  async triggerTaskWorkflow(taskId: number, workflowType: WorkflowType = 'task_approval'): Promise<WorkflowInstance> {
    const response = await api.post(`${this.baseUrl}/trigger/task/${taskId}`, { workflow_type: workflowType });
    return response.data;
  }

  async triggerAssessmentWorkflow(assessmentId: number, workflowType: WorkflowType = 'assessment_approval'): Promise<WorkflowInstance> {
    const response = await api.post(`${this.baseUrl}/trigger/assessment/${assessmentId}`, { workflow_type: workflowType });
    return response.data;
  }

  // Workflow instance filtering and searching
  async searchWorkflowInstances(searchParams: {
    query?: string;
    status?: WorkflowInstanceStatus[];
    entity_type?: string[];
    priority?: string[];
    assigned_to?: number[];
    date_range?: {
      start: string;
      end: string;
    };
    skip?: number;
    limit?: number;
  }): Promise<WorkflowInstance[]> {
    const response = await api.get(`${this.baseUrl}/instances/search`, { params: searchParams });
    return response.data;
  }

  // Workflow analytics
  async getWorkflowAnalytics(params?: {
    workflow_type?: WorkflowType;
    date_range?: {
      start: string;
      end: string;
    };
  }): Promise<{
    completion_rate: number;
    average_completion_time: number;
    bottlenecks: Array<{
      step_name: string;
      average_time: number;
      count: number;
    }>;
    trending_workflows: Array<{
      workflow_name: string;
      instance_count: number;
    }>;
  }> {
    const response = await api.get(`${this.baseUrl}/analytics`, { params });
    return response.data;
  }

  // Workflow step assignment helpers
  async getAvailableAssignees(stepId: number): Promise<{
    users: Array<{
      id: number;
      name: string;
      email: string;
      role: string;
    }>;
    roles: Array<{
      id: number;
      name: string;
      member_count: number;
    }>;
  }> {
    const response = await api.get(`${this.baseUrl}/steps/${stepId}/assignees`);
    return response.data;
  }

  // Workflow notification preferences
  async updateNotificationPreferences(preferences: {
    email_notifications: boolean;
    sms_notifications: boolean;
    in_app_notifications: boolean;
    digest_frequency: 'immediate' | 'daily' | 'weekly' | 'none';
  }): Promise<void> {
    await api.put(`${this.baseUrl}/notifications/preferences`, preferences);
  }

  async getNotificationPreferences(): Promise<{
    email_notifications: boolean;
    sms_notifications: boolean;
    in_app_notifications: boolean;
    digest_frequency: 'immediate' | 'daily' | 'weekly' | 'none';
  }> {
    const response = await api.get(`${this.baseUrl}/notifications/preferences`);
    return response.data;
  }
}

// Export a singleton instance
export const workflowAPI = new WorkflowAPI();