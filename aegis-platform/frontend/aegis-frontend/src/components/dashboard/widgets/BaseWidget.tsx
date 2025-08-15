import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Maximize2, Minimize2, RefreshCw, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface WidgetSize {
  width: 1 | 2 | 3 | 4;
  height: 1 | 2 | 3 | 4;
}

export interface WidgetConfig {
  id: string;
  title: string;
  description?: string;
  size: WidgetSize;
  position: { x: number; y: number };
  refreshInterval?: number;
  customizable?: boolean;
  minimizable?: boolean;
}

export interface BaseWidgetProps {
  config: WidgetConfig;
  isMinimized?: boolean;
  isCustomizable?: boolean;
  onResize?: (size: WidgetSize) => void;
  onMove?: (position: { x: number; y: number }) => void;
  onMinimize?: () => void;
  onMaximize?: () => void;
  onRefresh?: () => void;
  onConfigure?: () => void;
  onRemove?: () => void;
  children: React.ReactNode;
  className?: string;
}

export function BaseWidget({
  config,
  isMinimized = false,
  isCustomizable = true,
  onResize,
  onMove,
  onMinimize,
  onMaximize,
  onRefresh,
  onConfigure,
  onRemove,
  children,
  className,
}: BaseWidgetProps) {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleRefresh = async () => {
    if (onRefresh) {
      setIsLoading(true);
      try {
        await onRefresh();
      } finally {
        setIsLoading(false);
      }
    }
  };

  const getSizeClasses = (size: WidgetSize) => {
    const widthClass = {
      1: 'col-span-1',
      2: 'col-span-2', 
      3: 'col-span-3',
      4: 'col-span-4',
    }[size.width] || 'col-span-1';

    const heightClass = {
      1: 'row-span-1',
      2: 'row-span-2',
      3: 'row-span-3', 
      4: 'row-span-4',
    }[size.height] || 'row-span-1';

    return `${widthClass} ${heightClass}`;
  };

  return (
    <Card 
      className={cn(
        "widget-container transition-all duration-200 hover:shadow-md",
        getSizeClasses(config.size),
        isMinimized && "row-span-1",
        className
      )}
      data-widget-id={config.id}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex-1 min-w-0">
          <CardTitle className="text-sm font-medium truncate">
            {config.title}
          </CardTitle>
          {config.description && !isMinimized && (
            <CardDescription className="text-xs truncate">
              {config.description}
            </CardDescription>
          )}
        </div>
        
        {isCustomizable && (
          <div className="flex items-center gap-1">
            {onRefresh && (
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw className={cn("h-3 w-3", isLoading && "animate-spin")} />
              </Button>
            )}
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-6 w-6">
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {isMinimized ? (
                  <DropdownMenuItem onClick={onMaximize}>
                    <Maximize2 className="h-4 w-4 mr-2" />
                    Expand
                  </DropdownMenuItem>
                ) : (
                  config.minimizable && (
                    <DropdownMenuItem onClick={onMinimize}>
                      <Minimize2 className="h-4 w-4 mr-2" />
                      Minimize
                    </DropdownMenuItem>
                  )
                )}
                
                {onConfigure && (
                  <DropdownMenuItem onClick={onConfigure}>
                    <Settings className="h-4 w-4 mr-2" />
                    Configure
                  </DropdownMenuItem>
                )}
                
                {onRemove && (
                  <DropdownMenuItem onClick={onRemove} className="text-destructive">
                    Remove Widget
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </CardHeader>
      
      {!isMinimized && (
        <CardContent className="flex-1">
          {children}
        </CardContent>
      )}
    </Card>
  );
}