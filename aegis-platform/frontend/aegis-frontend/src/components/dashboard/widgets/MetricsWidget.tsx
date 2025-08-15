import React from 'react';
import { BaseWidget, BaseWidgetProps, WidgetConfig } from './BaseWidget';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MetricData {
  label: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease' | 'neutral';
    period: string;
  };
  status?: 'success' | 'warning' | 'error' | 'info';
  icon?: React.ComponentType<{ className?: string }>;
}

export interface MetricsWidgetProps extends Omit<BaseWidgetProps, 'children'> {
  metrics: MetricData[];
  layout?: 'grid' | 'list';
}

export function MetricsWidget({
  metrics,
  layout = 'grid',
  ...baseProps
}: MetricsWidgetProps) {
  const renderMetric = (metric: MetricData, index: number) => {
    const Icon = metric.icon;
    
    const getStatusColor = (status?: string) => {
      switch (status) {
        case 'success': return 'text-green-600 dark:text-green-400';
        case 'warning': return 'text-orange-600 dark:text-orange-400';
        case 'error': return 'text-red-600 dark:text-red-400';
        case 'info': return 'text-blue-600 dark:text-blue-400';
        default: return 'text-foreground';
      }
    };

    const getTrendIcon = (type: string) => {
      switch (type) {
        case 'increase': return TrendingUp;
        case 'decrease': return TrendingDown;
        default: return Minus;
      }
    };

    const getTrendColor = (type: string) => {
      switch (type) {
        case 'increase': return 'text-green-600 dark:text-green-400';
        case 'decrease': return 'text-red-600 dark:text-red-400';
        default: return 'text-muted-foreground';
      }
    };

    return (
      <div
        key={index}
        className={cn(
          "space-y-2 p-3 rounded-lg border bg-card",
          layout === 'list' && "flex items-center justify-between space-y-0"
        )}
      >
        <div className={cn(
          "flex items-center gap-2",
          layout === 'list' && "flex-1"
        )}>
          {Icon && (
            <Icon className={cn("h-4 w-4", getStatusColor(metric.status))} />
          )}
          <div>
            <p className="text-xs text-muted-foreground">{metric.label}</p>
            <p className={cn(
              "text-xl font-bold",
              getStatusColor(metric.status),
              layout === 'list' && "text-lg"
            )}>
              {metric.value}
            </p>
          </div>
        </div>
        
        {metric.change && (
          <div className="flex items-center gap-1">
            {React.createElement(getTrendIcon(metric.change.type), {
              className: cn("h-3 w-3", getTrendColor(metric.change.type))
            })}
            <span className={cn(
              "text-xs font-medium",
              getTrendColor(metric.change.type)
            )}>
              {metric.change.value > 0 ? '+' : ''}{metric.change.value}%
            </span>
            <span className="text-xs text-muted-foreground">
              {metric.change.period}
            </span>
          </div>
        )}
      </div>
    );
  };

  return (
    <BaseWidget {...baseProps}>
      <div className={cn(
        layout === 'grid' 
          ? "grid grid-cols-1 sm:grid-cols-2 gap-3"
          : "space-y-3"
      )}>
        {metrics.map(renderMetric)}
      </div>
    </BaseWidget>
  );
}

// Preset metric widget configurations
export const createMetricsWidget = (
  id: string,
  title: string,
  metrics: MetricData[],
  options: Partial<WidgetConfig> = {}
): WidgetConfig => ({
  id,
  title,
  size: { width: 2, height: 2 },
  position: { x: 0, y: 0 },
  customizable: true,
  minimizable: true,
  ...options,
});