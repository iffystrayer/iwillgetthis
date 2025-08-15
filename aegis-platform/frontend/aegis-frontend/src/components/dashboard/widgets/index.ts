// Widget Components Exports
export { BaseWidget } from './BaseWidget';
export type { WidgetConfig, WidgetSize, BaseWidgetProps } from './BaseWidget';

export { MetricsWidget, createMetricsWidget } from './MetricsWidget';
export type { MetricData, MetricsWidgetProps } from './MetricsWidget';

export { ChartWidget, createChartWidget } from './ChartWidget';
export type { ChartDataPoint, ChartWidgetProps } from './ChartWidget';

export { TasksWidget, createTasksWidget } from './TasksWidget';
export type { TaskItem, TasksWidgetProps } from './TasksWidget';

// Widget Registry
export const WIDGET_TYPES = {
  METRICS: 'metrics',
  CHART: 'chart',
  TASKS: 'tasks',
  ALERTS: 'alerts',
  ACTIVITY: 'activity',
  CALENDAR: 'calendar',
} as const;

export type WidgetType = typeof WIDGET_TYPES[keyof typeof WIDGET_TYPES];

// Default Widget Configurations
export const DEFAULT_WIDGET_CONFIGS = {
  [WIDGET_TYPES.METRICS]: {
    size: { width: 2, height: 2 },
    minimizable: true,
    customizable: true,
  },
  [WIDGET_TYPES.CHART]: {
    size: { width: 2, height: 2 },
    minimizable: true,
    customizable: true,
    refreshInterval: 300000,
  },
  [WIDGET_TYPES.TASKS]: {
    size: { width: 2, height: 3 },
    minimizable: true,
    customizable: true,
    refreshInterval: 60000,
  },
  [WIDGET_TYPES.ALERTS]: {
    size: { width: 2, height: 2 },
    minimizable: true,
    customizable: true,
    refreshInterval: 30000,
  },
  [WIDGET_TYPES.ACTIVITY]: {
    size: { width: 3, height: 2 },
    minimizable: true,
    customizable: true,
    refreshInterval: 60000,
  },
  [WIDGET_TYPES.CALENDAR]: {
    size: { width: 2, height: 3 },
    minimizable: true,
    customizable: true,
  },
} as const;