import React, { useState, useEffect } from 'react';
import { Eye, CheckCircle, XCircle, Clock, User, AlertTriangle, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { workflowAPI } from '@/lib/workflow-api';
import {
  WorkflowInstance,
  WorkflowInstanceStatus,
  WORKFLOW_STATUS_COLORS
} from '@/types/workflow';
import { WorkflowInstanceDetails } from '@/components/workflows/WorkflowInstanceDetails';
import { WorkflowExecutionDialog } from '@/components/workflows/WorkflowExecutionDialog';

const WorkflowInstancesPage: React.FC = () => {
  const [instances, setInstances] = useState<WorkflowInstance[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<WorkflowInstanceStatus | 'all'>('all');
  const [entityFilter, setEntityFilter] = useState<string>('all');
  const [assignedToMeFilter, setAssignedToMeFilter] = useState(false);
  const [selectedInstance, setSelectedInstance] = useState<WorkflowInstance | null>(null);
  const [executionDialogOpen, setExecutionDialogOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadInstances();
  }, [statusFilter, entityFilter, assignedToMeFilter]);

  const loadInstances = async () => {
    try {
      setLoading(true);
      const params: any = {};
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      if (entityFilter !== 'all') {
        params.entity_type = entityFilter;
      }

      if (assignedToMeFilter) {
        params.assigned_to_me = true;
      }

      const data = await workflowAPI.getWorkflowInstances(params);
      setInstances(data);
    } catch (error) {
      console.error('Error loading workflow instances:', error);
      toast({
        title: "Error",
        description: "Failed to load workflow instances",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExecutionComplete = () => {
    setExecutionDialogOpen(false);
    loadInstances();
  };

  const filteredInstances = instances.filter(instance =>
    instance.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    instance.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    instance.entity_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: WorkflowInstanceStatus) => {
    return WORKFLOW_STATUS_COLORS[status] || 'gray';
  };

  const getStatusIcon = (status: WorkflowInstanceStatus) => {
    switch (status) {
      case 'approved':
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'rejected':
      case 'cancelled':
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending_approval':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'in_progress':
        return <User className="h-4 w-4 text-blue-500" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  const getEntityTypeLabel = (entityType: string) => {
    const labels: Record<string, string> = {
      risk: 'Risk',
      task: 'Task',
      assessment: 'Assessment',
      evidence: 'Evidence',
      user_access: 'User Access',
      budget: 'Budget',
      exception: 'Exception'
    };
    return labels[entityType] || entityType;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical':
      case 'urgent':
        return 'text-red-600 bg-red-100';
      case 'high':
        return 'text-orange-600 bg-orange-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const isOverdue = (instance: WorkflowInstance) => {
    if (!instance.due_date) return false;
    return new Date(instance.due_date) < new Date() && 
           !['completed', 'approved', 'rejected', 'cancelled'].includes(instance.status);
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Instances</h1>
          <p className="text-gray-500">
            Monitor and manage active workflow instances
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search instances..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={(value: WorkflowInstanceStatus | 'all') => setStatusFilter(value)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="initiated">Initiated</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="pending_approval">Pending Approval</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>
            <Select value={entityFilter} onValueChange={setEntityFilter}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Filter by entity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Entities</SelectItem>
                <SelectItem value="risk">Risks</SelectItem>
                <SelectItem value="task">Tasks</SelectItem>
                <SelectItem value="assessment">Assessments</SelectItem>
                <SelectItem value="evidence">Evidence</SelectItem>
                <SelectItem value="user_access">User Access</SelectItem>
                <SelectItem value="budget">Budget</SelectItem>
                <SelectItem value="exception">Exceptions</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant={assignedToMeFilter ? "default" : "outline"}
              onClick={() => setAssignedToMeFilter(!assignedToMeFilter)}
              className="whitespace-nowrap"
            >
              Assigned to Me
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Content */}
      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="text-gray-500">Loading workflow instances...</div>
            </div>
          ) : filteredInstances.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-500">No workflow instances found</div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Instance</TableHead>
                  <TableHead>Entity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Assignee</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredInstances.map((instance) => (
                  <TableRow key={instance.id} className={isOverdue(instance) ? 'bg-red-50' : ''}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(instance.status)}
                        <div>
                          <div className="font-semibold">
                            {instance.name || `Workflow #${instance.id}`}
                          </div>
                          {instance.description && (
                            <div className="text-sm text-gray-500 truncate max-w-xs">
                              {instance.description}
                            </div>
                          )}
                        </div>
                        {isOverdue(instance) && (
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <Badge variant="outline">
                          {getEntityTypeLabel(instance.entity_type)}
                        </Badge>
                        <div className="text-sm text-gray-500 mt-1">
                          ID: {instance.entity_id}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={getStatusColor(instance.status) === 'green' ? 'default' : 'secondary'}
                        className={`bg-${getStatusColor(instance.status)}-100 text-${getStatusColor(instance.status)}-800`}
                      >
                        {instance.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={getPriorityColor(instance.priority)}
                      >
                        {instance.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {instance.current_assignee ? (
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
                            <User className="h-3 w-3 text-blue-600" />
                          </div>
                          <span className="text-sm">
                            {instance.current_assignee.full_name || instance.current_assignee.email}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-500">Unassigned</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {instance.due_date ? (
                        <div className={isOverdue(instance) ? 'text-red-600 font-medium' : ''}>
                          {new Date(instance.due_date).toLocaleDateString()}
                        </div>
                      ) : (
                        <span className="text-gray-500">No due date</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ 
                              width: `${
                                instance.status === 'completed' || instance.status === 'approved' ? 100 :
                                instance.status === 'in_progress' || instance.status === 'pending_approval' ? 50 :
                                instance.status === 'initiated' ? 25 : 0
                              }%` 
                            }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">
                          {instance.escalation_level > 0 && `L${instance.escalation_level}`}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedInstance(instance)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                            <DialogHeader>
                              <DialogTitle>
                                Workflow Instance #{instance.id}
                              </DialogTitle>
                              <DialogDescription>
                                {getEntityTypeLabel(instance.entity_type)} workflow instance details
                              </DialogDescription>
                            </DialogHeader>
                            {selectedInstance && (
                              <WorkflowInstanceDetails instance={selectedInstance} />
                            )}
                          </DialogContent>
                        </Dialog>
                        
                        {['pending_approval', 'in_progress'].includes(instance.status) && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedInstance(instance);
                              setExecutionDialogOpen(true);
                            }}
                          >
                            Action
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Execution Dialog */}
      {selectedInstance && (
        <WorkflowExecutionDialog
          instance={selectedInstance}
          open={executionDialogOpen}
          onOpenChange={setExecutionDialogOpen}
          onExecutionComplete={handleExecutionComplete}
        />
      )}
    </div>
  );
};

export default WorkflowInstancesPage;