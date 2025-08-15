import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, Database, CheckSquare, BarChart3, Plus } from 'lucide-react';
import { dashboardApi } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { DashboardGrid, DashboardLayout } from '@/components/dashboard/DashboardGrid';
import { 
  MetricsWidget, 
  ChartWidget, 
  TasksWidget,
  createMetricsWidget,
  createChartWidget,
  createTasksWidget,
  WidgetConfig,
  MetricData,
  ChartDataPoint,
  TaskItem,
  WIDGET_TYPES
} from '@/components/dashboard/widgets';
import { LoadingPage } from '@/components/ui/loading-spinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Sample data for widgets
const sampleMetrics: MetricData[] = [
  {
    label: 'Total Assets',
    value: 45,
    icon: Database,
    status: 'info',
    change: { value: 12, type: 'increase', period: '30d' }
  },
  {
    label: 'Critical Risks',
    value: 8,
    icon: AlertTriangle,
    status: 'error',
    change: { value: -2, type: 'decrease', period: '7d' }
  },
  {
    label: 'Open Tasks',
    value: 23,
    icon: CheckSquare,
    status: 'warning',
    change: { value: 5, type: 'increase', period: '7d' }
  },
  {
    label: 'Compliance Score',
    value: '87%',
    icon: BarChart3,
    status: 'success',
    change: { value: 3, type: 'increase', period: '30d' }
  }
];

const sampleChartData: ChartDataPoint[] = [
  { label: 'Low', value: 15, color: '#10b981' },
  { label: 'Medium', value: 12, color: '#f59e0b' },
  { label: 'High', value: 8, color: '#ef4444' },
  { label: 'Critical', value: 3, color: '#dc2626' }
];

const sampleTasks: TaskItem[] = [
  {
    id: '1',
    title: 'Firewall Configuration Review',
    assignee: 'John Doe',
    priority: 'high',
    status: 'overdue',
    dueDate: '2025-08-10',
    description: 'Review and update firewall rules for web servers'
  },
  {
    id: '2',
    title: 'Security Training Completion',
    assignee: 'Jane Smith',
    priority: 'medium',
    status: 'in_progress',
    dueDate: '2025-08-20',
    description: 'Complete mandatory security awareness training'
  },
  {
    id: '3',
    title: 'Vulnerability Assessment',
    assignee: 'Mike Johnson',
    priority: 'critical',
    status: 'pending',
    dueDate: '2025-08-25',
    description: 'Conduct quarterly vulnerability assessment'
  }
];

// Default dashboard layouts
const defaultLayouts: DashboardLayout[] = [
  {
    id: 'overview',
    name: 'Security Overview',
    description: 'High-level security metrics and KPIs',
    isDefault: true,
    widgets: [
      createMetricsWidget('metrics-1', 'Key Metrics', sampleMetrics, { position: { x: 0, y: 0 } }),
      createChartWidget('chart-1', 'Risk Distribution', 'pie', sampleChartData, { position: { x: 2, y: 0 } }),
      createTasksWidget('tasks-1', 'Priority Tasks', sampleTasks, { position: { x: 0, y: 2 } }),
      {
        id: 'alerts-1',
        title: 'Recent Alerts',
        description: 'Latest security alerts and notifications',
        size: { width: 2, height: 2 },
        position: { x: 2, y: 2 },
        customizable: true,
        minimizable: true,
      }
    ]
  },
  {
    id: 'executive',
    name: 'Executive Dashboard',
    description: 'Strategic overview for leadership',
    widgets: [
      createMetricsWidget('exec-metrics-1', 'Executive KPIs', sampleMetrics.slice(0, 2), { 
        position: { x: 0, y: 0 },
        size: { width: 4, height: 1 }
      }),
      createChartWidget('exec-chart-1', 'Risk Trends', 'line', sampleChartData, { 
        position: { x: 0, y: 1 },
        size: { width: 3, height: 2 }
      })
    ]
  },
  {
    id: 'analyst',
    name: 'Analyst Workbench',
    description: 'Detailed view for security analysts',
    widgets: [
      createTasksWidget('analyst-tasks-1', 'My Tasks', sampleTasks, { position: { x: 0, y: 0 } }),
      createChartWidget('analyst-chart-1', 'Threat Analysis', 'bar', sampleChartData, { position: { x: 2, y: 0 } }),
      createMetricsWidget('analyst-metrics-1', 'Daily Metrics', sampleMetrics, { 
        position: { x: 0, y: 3 },
        size: { width: 4, height: 1 }
      })
    ]
  }
];

export default function AdvancedDashboardPage() {
  const { user } = useAuth();
  const [selectedLayout, setSelectedLayout] = useState<string>('overview');
  const [layouts, setLayouts] = useState<DashboardLayout[]>(defaultLayouts);
  const [isEditing, setIsEditing] = useState(false);

  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'advanced'],
    queryFn: dashboardApi.getOverview,
    retry: 1,
  });

  const currentLayout = layouts.find(l => l.id === selectedLayout) || layouts[0];

  const handleLayoutChange = (updatedLayout: DashboardLayout) => {
    setLayouts(prev => prev.map(layout => 
      layout.id === updatedLayout.id ? updatedLayout : layout
    ));
  };

  const handleWidgetAdd = (widgetType: string) => {
    const newWidget: WidgetConfig = {
      id: `${widgetType}-${Date.now()}`,
      title: `New ${widgetType.charAt(0).toUpperCase() + widgetType.slice(1)} Widget`,
      size: { width: 2, height: 2 },
      position: { x: 0, y: 0 },
      customizable: true,
      minimizable: true,
    };

    const updatedLayout: DashboardLayout = {
      ...currentLayout,
      widgets: [...currentLayout.widgets, newWidget]
    };

    handleLayoutChange(updatedLayout);
  };

  const handleWidgetRemove = (widgetId: string) => {
    const updatedLayout: DashboardLayout = {
      ...currentLayout,
      widgets: currentLayout.widgets.filter(w => w.id !== widgetId)
    };

    handleLayoutChange(updatedLayout);
  };

  const handleWidgetUpdate = (widget: WidgetConfig) => {
    const updatedLayout: DashboardLayout = {
      ...currentLayout,
      widgets: currentLayout.widgets.map(w => w.id === widget.id ? widget : w)
    };

    handleLayoutChange(updatedLayout);
  };

  const renderWidget = (widget: WidgetConfig) => {
    const widgetType = widget.id.split('-')[0];
    
    switch (widgetType) {
      case 'metrics':
        return (
          <MetricsWidget
            key={widget.id}
            config={widget}
            metrics={sampleMetrics}
            onResize={(size) => handleWidgetUpdate({ ...widget, size })}
            onRemove={() => handleWidgetRemove(widget.id)}
          />
        );
      
      case 'chart':
        return (
          <ChartWidget
            key={widget.id}
            config={widget}
            chartType="pie"
            data={sampleChartData}
            onResize={(size) => handleWidgetUpdate({ ...widget, size })}
            onRemove={() => handleWidgetRemove(widget.id)}
          />
        );
      
      case 'tasks':
        return (
          <TasksWidget
            key={widget.id}
            config={widget}
            tasks={sampleTasks}
            onTaskClick={(task) => console.log('Task clicked:', task)}
            onNewTask={() => console.log('New task')}
            onResize={(size) => handleWidgetUpdate({ ...widget, size })}
            onRemove={() => handleWidgetRemove(widget.id)}
          />
        );
      
      default:
        return null;
    }
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Advanced Dashboard</h1>
          <p className="text-muted-foreground text-sm sm:text-base">
            Customizable widgets and personalized views for {user?.full_name || 'User'}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            variant={isEditing ? "default" : "outline"} 
            size="sm"
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? 'Done Editing' : 'Edit Dashboard'}
          </Button>
          
          {isEditing && (
            <Button variant="outline" size="sm" onClick={() => handleWidgetAdd('metrics')}>
              <Plus className="h-4 w-4 mr-2" />
              Add Widget
            </Button>
          )}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Unable to load dashboard data. Using demo data for display.
          </AlertDescription>
        </Alert>
      )}

      {/* Dashboard Tabs */}
      <Tabs value={selectedLayout} onValueChange={setSelectedLayout}>
        <TabsList className="grid w-full grid-cols-3">
          {layouts.map((layout) => (
            <TabsTrigger key={layout.id} value={layout.id} className="text-sm">
              {layout.name}
            </TabsTrigger>
          ))}
        </TabsList>
        
        {layouts.map((layout) => (
          <TabsContent key={layout.id} value={layout.id} className="mt-6">
            <DashboardGrid
              layout={layout}
              isEditing={isEditing}
              onLayoutChange={handleLayoutChange}
              onWidgetAdd={handleWidgetAdd}
              onWidgetRemove={handleWidgetRemove}
              onWidgetUpdate={handleWidgetUpdate}
            >
              {/* Render actual widget components */}
              <div className="hidden">
                {layout.widgets.map(renderWidget)}
              </div>
            </DashboardGrid>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}