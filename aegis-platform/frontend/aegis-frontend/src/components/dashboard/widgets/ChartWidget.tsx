import React from 'react';
import { BaseWidget, BaseWidgetProps, WidgetConfig } from './BaseWidget';
import { BarChart3, LineChart, PieChart } from 'lucide-react';

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface ChartWidgetProps extends Omit<BaseWidgetProps, 'children'> {
  chartType: 'bar' | 'line' | 'pie' | 'area';
  data: ChartDataPoint[];
  showLegend?: boolean;
  showGrid?: boolean;
  height?: number;
}

export function ChartWidget({
  chartType,
  data,
  showLegend = true,
  showGrid = true,
  height = 200,
  ...baseProps
}: ChartWidgetProps) {
  const getChartIcon = () => {
    switch (chartType) {
      case 'bar': return BarChart3;
      case 'line': return LineChart;
      case 'pie': return PieChart;
      default: return BarChart3;
    }
  };

  const renderPlaceholderChart = () => {
    const Icon = getChartIcon();
    
    return (
      <div 
        className="flex items-center justify-center border-2 border-dashed border-muted rounded-lg"
        style={{ height: `${height}px` }}
      >
        <div className="text-center space-y-2">
          <Icon className="h-12 w-12 mx-auto text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart
          </p>
          <p className="text-xs text-muted-foreground">
            Chart library integration needed
          </p>
        </div>
      </div>
    );
  };

  const renderDataSummary = () => {
    if (!data || data.length === 0) return null;

    const total = data.reduce((sum, point) => sum + point.value, 0);
    const max = Math.max(...data.map(point => point.value));
    const maxPoint = data.find(point => point.value === max);

    return (
      <div className="mt-4 p-3 bg-muted/50 rounded-lg">
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <p className="text-muted-foreground">Total</p>
            <p className="font-semibold">{total.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Highest</p>
            <p className="font-semibold">{maxPoint?.label}: {max.toLocaleString()}</p>
          </div>
        </div>
        
        {showLegend && data.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {data.map((point, index) => (
              <div key={index} className="flex items-center gap-1">
                <div 
                  className="w-2 h-2 rounded-full"
                  style={{ 
                    backgroundColor: point.color || `hsl(${index * 360 / data.length}, 70%, 50%)` 
                  }}
                />
                <span className="text-xs">{point.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <BaseWidget {...baseProps}>
      <div className="space-y-4">
        {renderPlaceholderChart()}
        {renderDataSummary()}
      </div>
    </BaseWidget>
  );
}

// Preset chart widget configurations
export const createChartWidget = (
  id: string,
  title: string,
  chartType: 'bar' | 'line' | 'pie' | 'area',
  data: ChartDataPoint[],
  options: Partial<WidgetConfig> = {}
): WidgetConfig => ({
  id,
  title,
  size: { width: 2, height: 2 },
  position: { x: 0, y: 0 },
  customizable: true,
  minimizable: true,
  refreshInterval: 300000, // 5 minutes
  ...options,
});