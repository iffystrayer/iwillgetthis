import React from 'react';
import { BaseWidget, BaseWidgetProps, WidgetConfig } from './BaseWidget';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckSquare, Clock, AlertTriangle, User, Calendar } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface TaskItem {
  id: string;
  title: string;
  assignee?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  dueDate?: string;
  description?: string;
}

export interface TasksWidgetProps extends Omit<BaseWidgetProps, 'children'> {
  tasks: TaskItem[];
  showCompleted?: boolean;
  maxItems?: number;
  onTaskClick?: (task: TaskItem) => void;
  onNewTask?: () => void;
}

export function TasksWidget({
  tasks,
  showCompleted = false,
  maxItems = 5,
  onTaskClick,
  onNewTask,
  ...baseProps
}: TasksWidgetProps) {
  const filteredTasks = tasks
    .filter(task => showCompleted || task.status !== 'completed')
    .slice(0, maxItems);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'secondary';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckSquare;
      case 'in_progress': return Clock;
      case 'overdue': return AlertTriangle;
      default: return Clock;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 dark:text-green-400';
      case 'in_progress': return 'text-blue-600 dark:text-blue-400';
      case 'overdue': return 'text-red-600 dark:text-red-400';
      default: return 'text-muted-foreground';
    }
  };

  const renderTask = (task: TaskItem, index: number) => {
    const StatusIcon = getStatusIcon(task.status);
    
    return (
      <div
        key={task.id}
        className={cn(
          "p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors cursor-pointer",
          task.status === 'completed' && "opacity-60"
        )}
        onClick={() => onTaskClick?.(task)}
      >
        <div className="flex items-start gap-3">
          <StatusIcon className={cn("h-4 w-4 mt-0.5", getStatusColor(task.status))} />
          
          <div className="flex-1 min-w-0 space-y-1">
            <div className="flex items-center gap-2">
              <p className={cn(
                "text-sm font-medium truncate",
                task.status === 'completed' && "line-through"
              )}>
                {task.title}
              </p>
              <Badge variant={getPriorityColor(task.priority)} className="text-xs px-1 py-0">
                {task.priority}
              </Badge>
            </div>
            
            {task.description && (
              <p className="text-xs text-muted-foreground line-clamp-2">
                {task.description}
              </p>
            )}
            
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              {task.assignee && (
                <div className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  <span>{task.assignee}</span>
                </div>
              )}
              
              {task.dueDate && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <span>{new Date(task.dueDate).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const taskCounts = {
    total: tasks.length,
    pending: tasks.filter(t => t.status === 'pending').length,
    inProgress: tasks.filter(t => t.status === 'in_progress').length,
    overdue: tasks.filter(t => t.status === 'overdue').length,
    completed: tasks.filter(t => t.status === 'completed').length,
  };

  return (
    <BaseWidget {...baseProps}>
      <div className="space-y-4">
        {/* Task Summary */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="space-y-1">
            <p className="text-muted-foreground">In Progress</p>
            <p className="font-semibold text-blue-600">{taskCounts.inProgress}</p>
          </div>
          <div className="space-y-1">
            <p className="text-muted-foreground">Overdue</p>
            <p className="font-semibold text-red-600">{taskCounts.overdue}</p>
          </div>
        </div>

        {/* Tasks List */}
        <div className="space-y-2">
          {filteredTasks.length > 0 ? (
            filteredTasks.map(renderTask)
          ) : (
            <div className="text-center py-6 text-muted-foreground">
              <CheckSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No tasks to display</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {onNewTask && (
            <Button variant="outline" size="sm" className="flex-1" onClick={onNewTask}>
              New Task
            </Button>
          )}
          <Button variant="outline" size="sm" className="flex-1" asChild>
            <a href="/tasks">View All</a>
          </Button>
        </div>
      </div>
    </BaseWidget>
  );
}

// Preset tasks widget configurations
export const createTasksWidget = (
  id: string,
  title: string,
  tasks: TaskItem[],
  options: Partial<WidgetConfig> = {}
): WidgetConfig => ({
  id,
  title,
  size: { width: 2, height: 3 },
  position: { x: 0, y: 0 },
  customizable: true,
  minimizable: true,
  refreshInterval: 60000, // 1 minute
  ...options,
});