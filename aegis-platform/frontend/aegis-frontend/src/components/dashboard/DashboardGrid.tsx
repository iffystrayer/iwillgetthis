import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger 
} from '@/components/ui/dialog';
import { 
  Settings, 
  Plus, 
  Grid3X3, 
  RotateCcw, 
  Save,
  Eye,
  EyeOff
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { 
  BaseWidget, 
  WidgetConfig, 
  WidgetSize,
  WIDGET_TYPES,
  DEFAULT_WIDGET_CONFIGS
} from './widgets';

export interface DashboardLayout {
  id: string;
  name: string;
  description?: string;
  widgets: WidgetConfig[];
  isDefault?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface DashboardGridProps {
  layout: DashboardLayout;
  isEditing?: boolean;
  className?: string;
  onLayoutChange?: (layout: DashboardLayout) => void;
  onWidgetAdd?: (widgetType: string) => void;
  onWidgetRemove?: (widgetId: string) => void;
  onWidgetUpdate?: (widget: WidgetConfig) => void;
  children?: React.ReactNode;
}

export function DashboardGrid({
  layout,
  isEditing = false,
  className,
  onLayoutChange,
  onWidgetAdd,
  onWidgetRemove,
  onWidgetUpdate,
  children,
}: DashboardGridProps) {
  const [showCustomizeDialog, setShowCustomizeDialog] = useState(false);
  const [minimizedWidgets, setMinimizedWidgets] = useState<Set<string>>(new Set());
  
  const handleWidgetMinimize = useCallback((widgetId: string) => {
    setMinimizedWidgets(prev => new Set([...prev, widgetId]));
  }, []);

  const handleWidgetMaximize = useCallback((widgetId: string) => {
    setMinimizedWidgets(prev => {
      const newSet = new Set(prev);
      newSet.delete(widgetId);
      return newSet;
    });
  }, []);

  const handleWidgetResize = useCallback((widgetId: string, size: WidgetSize) => {
    if (!onWidgetUpdate) return;
    
    const widget = layout.widgets.find(w => w.id === widgetId);
    if (widget) {
      onWidgetUpdate({ ...widget, size });
    }
  }, [layout.widgets, onWidgetUpdate]);

  const handleWidgetMove = useCallback((widgetId: string, position: { x: number; y: number }) => {
    if (!onWidgetUpdate) return;
    
    const widget = layout.widgets.find(w => w.id === widgetId);
    if (widget) {
      onWidgetUpdate({ ...widget, position });
    }
  }, [layout.widgets, onWidgetUpdate]);

  const handleWidgetRemove = useCallback((widgetId: string) => {
    if (onWidgetRemove) {
      onWidgetRemove(widgetId);
    }
  }, [onWidgetRemove]);

  const handleResetLayout = useCallback(() => {
    if (onLayoutChange) {
      // Reset to default positions
      const resetLayout: DashboardLayout = {
        ...layout,
        widgets: layout.widgets.map((widget, index) => ({
          ...widget,
          position: { x: (index % 4) * widget.size.width, y: Math.floor(index / 4) * widget.size.height },
        })),
      };
      onLayoutChange(resetLayout);
    }
  }, [layout, onLayoutChange]);

  const getGridStyle = () => {
    return {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gridAutoRows: '200px',
      gap: '1rem',
      width: '100%',
    };
  };

  const renderCustomizeDialog = () => (
    <Dialog open={showCustomizeDialog} onOpenChange={setShowCustomizeDialog}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Customize Dashboard</DialogTitle>
          <DialogDescription>
            Add, remove, and configure widgets for your dashboard
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Available Widgets */}
          <div>
            <h3 className="text-sm font-medium mb-3">Available Widgets</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(WIDGET_TYPES).map(([key, type]) => (
                <Card key={type} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm capitalize">{type}</CardTitle>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => onWidgetAdd?.(type)}
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <CardDescription className="text-xs">
                      {type === 'metrics' && 'Display key performance indicators'}
                      {type === 'chart' && 'Visualize data with charts and graphs'}
                      {type === 'tasks' && 'Show current tasks and assignments'}
                      {type === 'alerts' && 'Display security alerts and notifications'}
                      {type === 'activity' && 'Show recent system activity'}
                      {type === 'calendar' && 'Display upcoming events and deadlines'}
                    </CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Current Widgets */}
          <div>
            <h3 className="text-sm font-medium mb-3">Current Widgets</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {layout.widgets.map((widget) => (
                <div 
                  key={widget.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      {minimizedWidgets.has(widget.id) ? (
                        <EyeOff className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <Eye className="h-4 w-4 text-green-600" />
                      )}
                      <span className="font-medium text-sm">{widget.title}</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {widget.size.width}×{widget.size.height}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => 
                        minimizedWidgets.has(widget.id) 
                          ? handleWidgetMaximize(widget.id)
                          : handleWidgetMinimize(widget.id)
                      }
                    >
                      {minimizedWidgets.has(widget.id) ? (
                        <Eye className="h-3 w-3" />
                      ) : (
                        <EyeOff className="h-3 w-3" />
                      )}
                    </Button>
                    
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleWidgetRemove(widget.id)}
                      className="text-destructive"
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );

  return (
    <div className={cn("space-y-4", className)}>
      {/* Dashboard Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">{layout.name}</h2>
          {layout.description && (
            <p className="text-sm text-muted-foreground">{layout.description}</p>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleResetLayout}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset Layout
          </Button>
          
          <Button variant="outline" size="sm" onClick={() => setShowCustomizeDialog(true)}>
            <Settings className="h-4 w-4 mr-2" />
            Customize
          </Button>
          
          {isEditing && onLayoutChange && (
            <Button size="sm">
              <Save className="h-4 w-4 mr-2" />
              Save Layout
            </Button>
          )}
        </div>
      </div>

      {/* Widget Grid */}
      <div style={getGridStyle()}>
        {layout.widgets.map((widget) => (
          <BaseWidget
            key={widget.id}
            config={widget}
            isMinimized={minimizedWidgets.has(widget.id)}
            isCustomizable={isEditing}
            onResize={(size) => handleWidgetResize(widget.id, size)}
            onMove={(position) => handleWidgetMove(widget.id, position)}
            onMinimize={() => handleWidgetMinimize(widget.id)}
            onMaximize={() => handleWidgetMaximize(widget.id)}
            onRemove={() => handleWidgetRemove(widget.id)}
          >
            {/* Widget content will be rendered by specific widget components */}
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <Grid3X3 className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">Widget Content</p>
                <p className="text-xs">Type: {widget.id.split('-')[0]}</p>
              </div>
            </div>
          </BaseWidget>
        ))}
        
        {/* Add Widget Placeholder */}
        {isEditing && (
          <Card className="border-dashed border-2 flex items-center justify-center cursor-pointer hover:bg-muted/50 transition-colors">
            <DialogTrigger asChild>
              <Button variant="ghost" className="h-full w-full" onClick={() => setShowCustomizeDialog(true)}>
                <div className="text-center">
                  <Plus className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Add Widget</p>
                </div>
              </Button>
            </DialogTrigger>
          </Card>
        )}
      </div>

      {/* Custom content */}
      {children}

      {/* Customize Dialog */}
      {renderCustomizeDialog()}
    </div>
  );
}