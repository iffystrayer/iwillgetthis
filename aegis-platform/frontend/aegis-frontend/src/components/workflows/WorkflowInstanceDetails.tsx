import React, { useState, useEffect } from 'react';
import { User, Clock, CheckCircle, XCircle, AlertCircle, MessageSquare } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { workflowAPI } from '@/lib/workflow-api';
import {
  WorkflowInstance,
  WorkflowStepInstance,
  WorkflowAction,
  WORKFLOW_STATUS_COLORS,
  ACTION_TYPE_LABELS
} from '@/types/workflow';

interface WorkflowInstanceDetailsProps {
  instance: WorkflowInstance;
}

export const WorkflowInstanceDetails: React.FC<WorkflowInstanceDetailsProps> = ({ instance }) => {
  const [stepInstances, setStepInstances] = useState<WorkflowStepInstance[]>([]);
  const [actions, setActions] = useState<WorkflowAction[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadInstanceDetails();
  }, [instance.id]);

  const loadInstanceDetails = async () => {
    try {
      setLoading(true);
      const [stepsData, actionsData] = await Promise.all([
        workflowAPI.getWorkflowStepInstances(instance.id),
        workflowAPI.getWorkflowActions(instance.id)
      ]);
      setStepInstances(stepsData);
      setActions(actionsData);
    } catch (error) {
      console.error('Error loading instance details:', error);
      toast({
        title: "Error",
        description: "Failed to load workflow details",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'rejected':
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'in_progress':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case 'approve':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'reject':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'comment':
        return <MessageSquare className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatDuration = (start: string, end?: string) => {
    const startDate = new Date(start);
    const endDate = end ? new Date(end) : new Date();
    const duration = endDate.getTime() - startDate.getTime();
    
    const hours = Math.floor(duration / (1000 * 60 * 60));
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="text-gray-500">Loading workflow details...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Instance Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Instance Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <div className="flex items-center gap-2 mt-1">
                <Badge 
                  variant={WORKFLOW_STATUS_COLORS[instance.status] === 'green' ? 'default' : 'secondary'}
                  className={`bg-${WORKFLOW_STATUS_COLORS[instance.status]}-100 text-${WORKFLOW_STATUS_COLORS[instance.status]}-800`}
                >
                  {instance.status.replace('_', ' ')}
                </Badge>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Priority</label>
              <div className="mt-1">
                <Badge variant="outline" className={
                  instance.priority === 'critical' || instance.priority === 'urgent' ? 'text-red-600 bg-red-100' :
                  instance.priority === 'high' ? 'text-orange-600 bg-orange-100' :
                  instance.priority === 'medium' ? 'text-yellow-600 bg-yellow-100' :
                  'text-green-600 bg-green-100'
                }>
                  {instance.priority}
                </Badge>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Entity Type</label>
              <div className="mt-1">{instance.entity_type}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Entity ID</label>
              <div className="mt-1">{instance.entity_id}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Initiated By</label>
              <div className="flex items-center gap-2 mt-1">
                <User className="h-4 w-4 text-gray-400" />
                <span>{instance.initiated_by?.full_name || instance.initiated_by?.email || 'Unknown'}</span>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Current Assignee</label>
              <div className="flex items-center gap-2 mt-1">
                {instance.current_assignee ? (
                  <>
                    <User className="h-4 w-4 text-gray-400" />
                    <span>{instance.current_assignee.full_name || instance.current_assignee.email}</span>
                  </>
                ) : (
                  <span className="text-gray-500">Unassigned</span>
                )}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Initiated At</label>
              <div className="mt-1">{new Date(instance.initiated_at).toLocaleString()}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Due Date</label>
              <div className="mt-1">
                {instance.due_date ? new Date(instance.due_date).toLocaleString() : 'No due date'}
              </div>
            </div>
          </div>
          
          {instance.description && (
            <div>
              <label className="text-sm font-medium text-gray-500">Description</label>
              <div className="mt-1 text-gray-700">{instance.description}</div>
            </div>
          )}

          {instance.escalation_level > 0 && (
            <div>
              <label className="text-sm font-medium text-gray-500">Escalation Level</label>
              <div className="mt-1">
                <Badge variant="outline" className="text-orange-600 bg-orange-100">
                  Level {instance.escalation_level}
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="steps" className="w-full">
        <TabsList>
          <TabsTrigger value="steps">Workflow Steps</TabsTrigger>
          <TabsTrigger value="actions">Action History</TabsTrigger>
          <TabsTrigger value="context">Context Data</TabsTrigger>
        </TabsList>
        
        <TabsContent value="steps" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Progress</CardTitle>
              <CardDescription>
                Steps in this workflow instance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stepInstances.map((step, index) => (
                  <div key={step.id} className="flex items-start gap-4">
                    <div className="flex flex-col items-center">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full border-2 border-gray-200 bg-white">
                        {getStepStatusIcon(step.status)}
                      </div>
                      {index < stepInstances.length - 1 && (
                        <div className="w-px h-8 bg-gray-200 mt-2" />
                      )}
                    </div>
                    
                    <div className="flex-1 pb-8">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">
                            Step {step.step_order}: {step.workflow_step?.name || 'Unknown Step'}
                          </h4>
                          <p className="text-sm text-gray-500">
                            {step.workflow_step?.description}
                          </p>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline" className={
                            step.status === 'completed' ? 'text-green-600 bg-green-100' :
                            step.status === 'in_progress' ? 'text-blue-600 bg-blue-100' :
                            step.status === 'rejected' || step.status === 'error' ? 'text-red-600 bg-red-100' :
                            'text-gray-600 bg-gray-100'
                          }>
                            {step.status.replace('_', ' ')}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="mt-2 space-y-2">
                        {step.assigned_to && (
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <User className="h-3 w-3" />
                            <span>Assigned to: {step.assigned_to.full_name || step.assigned_to.email}</span>
                          </div>
                        )}
                        
                        {step.started_at && (
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <Clock className="h-3 w-3" />
                            <span>
                              Started: {new Date(step.started_at).toLocaleString()}
                              {step.completed_at && (
                                <span className="ml-2">
                                  (Duration: {formatDuration(step.started_at, step.completed_at)})
                                </span>
                              )}
                            </span>
                          </div>
                        )}
                        
                        {step.due_date && (
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <AlertCircle className="h-3 w-3" />
                            <span>Due: {new Date(step.due_date).toLocaleString()}</span>
                          </div>
                        )}
                        
                        {step.outcome_reason && (
                          <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                            <strong>Outcome:</strong> {step.outcome_reason}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="actions" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Action History</CardTitle>
              <CardDescription>
                All actions performed on this workflow instance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {actions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No actions recorded yet
                  </div>
                ) : (
                  actions.map((action) => (
                    <div key={action.id} className="flex items-start gap-4 p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100">
                        {getActionIcon(action.action_type)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="font-medium">
                              {ACTION_TYPE_LABELS[action.action_type] || action.action_type}
                            </h4>
                            <p className="text-sm text-gray-500">
                              by {action.performed_by?.full_name || action.performed_by?.email || 'Unknown'}
                            </p>
                          </div>
                          <div className="text-sm text-gray-500">
                            {new Date(action.performed_at).toLocaleString()}
                          </div>
                        </div>
                        
                        {action.comment && (
                          <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                            {action.comment}
                          </div>
                        )}
                        
                        {action.action_description && (
                          <div className="mt-2 text-sm text-gray-600">
                            {action.action_description}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="context" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Context Data</CardTitle>
              <CardDescription>
                Additional data associated with this workflow instance
              </CardDescription>
            </CardHeader>
            <CardContent>
              {instance.context_data ? (
                <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto">
                  {JSON.stringify(instance.context_data, null, 2)}
                </pre>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No context data available
                </div>
              )}
              
              {instance.custom_fields && Object.keys(instance.custom_fields).length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium mb-3">Custom Fields</h4>
                  <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto">
                    {JSON.stringify(instance.custom_fields, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};