import React, { useState, useEffect } from 'react';
import { Plus, Filter, Search, MoreHorizontal, Play, Pause, Archive, Edit } from 'lucide-react';
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { workflowAPI } from '@/lib/workflow-api';
import {
  Workflow,
  WorkflowType,
  WorkflowStatus,
  WORKFLOW_STATUS_COLORS,
  WORKFLOW_TYPE_LABELS
} from '@/types/workflow';

const WorkflowsPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<WorkflowStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<WorkflowType | 'all'>('all');
  const { toast } = useToast();

  useEffect(() => {
    loadWorkflows();
  }, [statusFilter, typeFilter]);

  const loadWorkflows = async () => {
    try {
      setLoading(true);
      const params: any = {};
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      if (typeFilter !== 'all') {
        params.workflow_type = typeFilter;
      }

      const data = await workflowAPI.getWorkflows(params);
      setWorkflows(data);
    } catch (error) {
      console.error('Error loading workflows:', error);
      toast({
        title: "Error",
        description: "Failed to load workflows",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (workflowId: number, newStatus: WorkflowStatus) => {
    try {
      await workflowAPI.updateWorkflow(workflowId, { status: newStatus });
      await loadWorkflows();
      toast({
        title: "Success",
        description: `Workflow status updated to ${newStatus}`,
      });
    } catch (error) {
      console.error('Error updating workflow status:', error);
      toast({
        title: "Error",
        description: "Failed to update workflow status",
        variant: "destructive",
      });
    }
  };

  const handleDeleteWorkflow = async (workflowId: number) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return;

    try {
      await workflowAPI.deleteWorkflow(workflowId);
      await loadWorkflows();
      toast({
        title: "Success",
        description: "Workflow deleted successfully",
      });
    } catch (error) {
      console.error('Error deleting workflow:', error);
      toast({
        title: "Error",
        description: "Failed to delete workflow",
        variant: "destructive",
      });
    }
  };

  const filteredWorkflows = workflows.filter(workflow =>
    workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: WorkflowStatus) => {
    return WORKFLOW_STATUS_COLORS[status] || 'gray';
  };

  const getStatusActions = (workflow: Workflow) => {
    const actions = [];
    
    if (workflow.status === 'draft') {
      actions.push(
        <DropdownMenuItem key="activate" onClick={() => handleStatusChange(workflow.id, 'active')}>
          <Play className="mr-2 h-4 w-4" />
          Activate
        </DropdownMenuItem>
      );
    }
    
    if (workflow.status === 'active') {
      actions.push(
        <DropdownMenuItem key="deactivate" onClick={() => handleStatusChange(workflow.id, 'inactive')}>
          <Pause className="mr-2 h-4 w-4" />
          Deactivate
        </DropdownMenuItem>
      );
    }
    
    if (workflow.status !== 'archived') {
      actions.push(
        <DropdownMenuItem key="archive" onClick={() => handleStatusChange(workflow.id, 'archived')}>
          <Archive className="mr-2 h-4 w-4" />
          Archive
        </DropdownMenuItem>
      );
    }

    return actions;
  };

  const WorkflowTable = ({ workflows }: { workflows: Workflow[] }) => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Category</TableHead>
          <TableHead>Version</TableHead>
          <TableHead>Steps</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {workflows.map((workflow) => (
          <TableRow key={workflow.id}>
            <TableCell className="font-medium">
              <div>
                <div className="font-semibold">{workflow.name}</div>
                {workflow.description && (
                  <div className="text-sm text-gray-500 truncate max-w-xs">
                    {workflow.description}
                  </div>
                )}
              </div>
            </TableCell>
            <TableCell>
              <Badge variant="outline">
                {WORKFLOW_TYPE_LABELS[workflow.workflow_type]}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge 
                variant={getStatusColor(workflow.status) === 'green' ? 'default' : 'secondary'}
                className={`bg-${getStatusColor(workflow.status)}-100 text-${getStatusColor(workflow.status)}-800`}
              >
                {workflow.status}
              </Badge>
            </TableCell>
            <TableCell>{workflow.category || '-'}</TableCell>
            <TableCell>{workflow.version}</TableCell>
            <TableCell>{workflow.steps?.length || 0}</TableCell>
            <TableCell>
              {new Date(workflow.created_at).toLocaleDateString()}
            </TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-8 w-8 p-0">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  {getStatusActions(workflow)}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    className="text-red-600"
                    onClick={() => handleDeleteWorkflow(workflow.id)}
                  >
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );

  const WorkflowCards = ({ workflows }: { workflows: Workflow[] }) => (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {workflows.map((workflow) => (
        <Card key={workflow.id} className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{workflow.name}</CardTitle>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-8 w-8 p-0">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  {getStatusActions(workflow)}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    className="text-red-600"
                    onClick={() => handleDeleteWorkflow(workflow.id)}
                  >
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">
                {WORKFLOW_TYPE_LABELS[workflow.workflow_type]}
              </Badge>
              <Badge 
                variant={getStatusColor(workflow.status) === 'green' ? 'default' : 'secondary'}
                className={`bg-${getStatusColor(workflow.status)}-100 text-${getStatusColor(workflow.status)}-800`}
              >
                {workflow.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {workflow.description && (
              <CardDescription className="mb-3">
                {workflow.description}
              </CardDescription>
            )}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Category:</span>
                <span>{workflow.category || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Version:</span>
                <span>{workflow.version}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Steps:</span>
                <span>{workflow.steps?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Created:</span>
                <span>{new Date(workflow.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Management</h1>
          <p className="text-gray-500">
            Create and manage approval workflows for your organization
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Workflow
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
                <Input
                  placeholder="Search workflows..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={(value: WorkflowStatus | 'all') => setStatusFilter(value)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
            <Select value={typeFilter} onValueChange={(value: WorkflowType | 'all') => setTypeFilter(value)}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {Object.entries(WORKFLOW_TYPE_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Content */}
      <Tabs defaultValue="table" className="w-full">
        <TabsList>
          <TabsTrigger value="table">Table View</TabsTrigger>
          <TabsTrigger value="cards">Card View</TabsTrigger>
        </TabsList>
        
        <TabsContent value="table" className="mt-6">
          <Card>
            <CardContent className="pt-6">
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="text-gray-500">Loading workflows...</div>
                </div>
              ) : filteredWorkflows.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-gray-500 mb-2">No workflows found</div>
                  <Button variant="outline">
                    <Plus className="mr-2 h-4 w-4" />
                    Create your first workflow
                  </Button>
                </div>
              ) : (
                <WorkflowTable workflows={filteredWorkflows} />
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="cards" className="mt-6">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="text-gray-500">Loading workflows...</div>
            </div>
          ) : filteredWorkflows.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-500 mb-2">No workflows found</div>
              <Button variant="outline">
                <Plus className="mr-2 h-4 w-4" />
                Create your first workflow
              </Button>
            </div>
          ) : (
            <WorkflowCards workflows={filteredWorkflows} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WorkflowsPage;