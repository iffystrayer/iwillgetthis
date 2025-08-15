import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, CheckSquare, Calendar, User, Eye, Edit, MoreHorizontal, Trash2, Archive, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { tasksApi } from '@/lib/api';
import { DataTable, StatusBadge } from '@/components/ui/data-table';
import { createCommonBulkActions } from '@/components/ui/bulk-actions-toolbar';
import { ColumnDef } from '@tanstack/react-table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { NewTaskDialog } from '@/components/dialogs/NewTaskDialog';

// Task interface for type safety
interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_to?: string;
  due_date?: string;
  created_at?: string;
  updated_at?: string;
}

export default function TasksPage() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewTaskDialog, setShowNewTaskDialog] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<Task[]>([]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await tasksApi.getAll();
      setTasks(response.items || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch tasks');
      console.error('Error fetching tasks:', err);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // Define columns for the data table
  const columns = useMemo<ColumnDef<Task>[]>(
    () => [
      {
        accessorKey: 'title',
        header: 'Task Title',
        cell: ({ row }) => {
          const task = row.original;
          return (
            <div className="flex flex-col max-w-[300px]">
              <span className="font-medium">{task.title}</span>
              {task.description && (
                <span className="text-sm text-muted-foreground truncate">
                  {task.description}
                </span>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ getValue }) => {
          const status = getValue() as string;
          const getVariant = () => {
            switch (status?.toLowerCase()) {
              case 'open': return 'destructive';
              case 'in progress': return 'secondary';
              case 'completed': return 'default';
              default: return 'outline';
            }
          };
          return <StatusBadge status={status} variant={getVariant()} />;
        },
      },
      {
        accessorKey: 'priority',
        header: 'Priority',
        cell: ({ getValue }) => {
          const priority = getValue() as string;
          const getVariant = () => {
            switch (priority?.toLowerCase()) {
              case 'high': return 'destructive';
              case 'medium': return 'secondary';
              case 'low': return 'outline';
              default: return 'secondary';
            }
          };
          return <Badge variant={getVariant()} className="capitalize">
            {priority || 'Unknown'}
          </Badge>;
        },
      },
      {
        accessorKey: 'assigned_to',
        header: 'Assigned To',
        cell: ({ getValue }) => {
          const assignee = getValue() as string;
          return (
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">{assignee || 'Unassigned'}</span>
            </div>
          );
        },
      },
      {
        accessorKey: 'due_date',
        header: 'Due Date',
        cell: ({ getValue }) => {
          const date = getValue() as string;
          if (!date) return <span className="text-sm text-muted-foreground">No due date</span>;
          const dueDate = new Date(date);
          const isOverdue = dueDate < new Date();
          return (
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className={`text-sm ${
                isOverdue ? 'text-red-600 font-semibold' : 'text-muted-foreground'
              }`}>
                {dueDate.toLocaleDateString()}
              </span>
            </div>
          );
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Created',
        cell: ({ getValue }) => {
          const date = getValue() as string;
          return date ? (
            <span className="text-sm text-muted-foreground">
              {new Date(date).toLocaleDateString()}
            </span>
          ) : (
            <span className="text-sm text-muted-foreground">N/A</span>
          );
        },
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => {
          const task = row.original;
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Open menu</span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => handleViewDetails(task.id)}>
                  <Eye className="mr-2 h-4 w-4" />
                  View Details
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Task
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          );
        },
      },
    ],
    []
  );


  const handleNewTask = () => {
    console.log('New Task clicked - Opening task creation dialog');
    setShowNewTaskDialog(true);
  };

  const handleTaskCreated = () => {
    console.log('Task created successfully - refreshing tasks list');
    fetchTasks();
  };


  const handleViewCalendar = () => {
    console.log('View Calendar clicked - Opening calendar view');
    // TODO: Implement calendar view functionality
  };

  const handleViewDetails = (taskId: number) => {
    console.log('View Details clicked for task:', taskId);
    navigate(`/tasks/${taskId}`);
  };

  // Bulk operations handlers
  const handleBulkDelete = async () => {
    console.log('Bulk delete tasks:', selectedTasks.map(t => t.id));
    // TODO: Implement bulk delete API call
    alert(`Would delete ${selectedTasks.length} tasks`);
  };

  const handleBulkUpdateStatus = async () => {
    console.log('Bulk update status for tasks:', selectedTasks.map(t => t.id));
    // TODO: Implement bulk status update dialog
    alert(`Would update status for ${selectedTasks.length} tasks`);
  };

  const handleBulkAssign = async () => {
    console.log('Bulk assign tasks:', selectedTasks.map(t => t.id));
    // TODO: Implement bulk assignment dialog
    alert(`Would assign ${selectedTasks.length} tasks`);
  };

  const handleBulkExport = () => {
    console.log('Bulk export selected tasks:', selectedTasks.map(t => t.id));
    
    // Generate CSV from selected tasks
    const csvHeaders = 'Title,Description,Status,Priority,Assigned To,Due Date,Created\n';
    const csvContent = selectedTasks.map(task => 
      `"${task.title || ''}","${task.description || ''}","${task.status || ''}","${task.priority || ''}","${task.assigned_to || ''}","${task.due_date || ''}","${task.created_at || ''}"`
    ).join('\n');
    
    const csvData = csvHeaders + csvContent;
    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `selected_tasks_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log(`✅ Exported ${selectedTasks.length} selected tasks to CSV`);
  };

  // Create bulk actions for tasks
  const bulkActions = useMemo(() => {
    return createCommonBulkActions(selectedTasks, {
      onExport: handleBulkExport,
      onUpdateStatus: handleBulkUpdateStatus,
      onAssign: handleBulkAssign,
      onDelete: handleBulkDelete,
    });
  }, [selectedTasks]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <CheckSquare className="h-8 w-8" />
            Task Management
          </h1>
          <p className="text-muted-foreground">
            Track and manage security and compliance tasks
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleViewCalendar}>
            <Calendar className="h-4 w-4 mr-2" />
            View Calendar
          </Button>
          <Button onClick={handleNewTask}>
            <Plus className="h-4 w-4 mr-2" />
            New Task
          </Button>
        </div>
      </div>


      {/* Error Message */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Error: {error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Showing demo data while backend is unavailable.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.length}</div>
            <p className="text-xs text-muted-foreground">
              Active tasks in system
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Tasks</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter(t => t.status?.toLowerCase() === 'open').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Require attention
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter(t => t.status?.toLowerCase() === 'in progress').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently being worked on
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter(t => t.status?.toLowerCase() === 'completed').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Successfully finished
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Tasks ({tasks.length})</CardTitle>
          <CardDescription>
            Comprehensive view of all security and compliance tasks with advanced filtering and search
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={columns}
            data={tasks}
            loading={loading}
            searchPlaceholder="Search tasks by title, description, or assignee..."
            emptyStateTitle="No tasks found"
            emptyStateDescription="Get started by creating your first security or compliance task"
            emptyStateAction={
              <Button onClick={handleNewTask}>
                <Plus className="h-4 w-4 mr-2" />
                Create First Task
              </Button>
            }
            showSearch={true}
            showColumnToggle={true}
            showPagination={true}
            pageSize={10}
            onRowClick={(task) => {
              handleViewDetails(task.id);
            }}
            rowClassName={(task) => {
              // Highlight overdue or high priority tasks
              const isOverdue = task.due_date && new Date(task.due_date) < new Date();
              const isHighPriority = task.priority?.toLowerCase() === 'high';
              if (isOverdue && isHighPriority) return 'bg-red-50 hover:bg-red-100';
              if (isOverdue) return 'bg-orange-50 hover:bg-orange-100';
              if (isHighPriority) return 'bg-yellow-50 hover:bg-yellow-100';
              return '';
            }}
            enableBulkSelect={true}
            bulkActions={bulkActions}
            onBulkSelectionChange={setSelectedTasks}
            getRowId={(row) => row.id.toString()}
          />
        </CardContent>
      </Card>

      {/* New Task Dialog */}
      <NewTaskDialog
        open={showNewTaskDialog}
        onOpenChange={setShowNewTaskDialog}
        onTaskCreated={handleTaskCreated}
      />
    </div>
  );
}