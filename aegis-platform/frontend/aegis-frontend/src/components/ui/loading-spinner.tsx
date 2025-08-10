import { cn } from '@/lib/utils';
import { Loader2, AlertCircle, Wifi, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12',
};

export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  return (
    <Loader2 
      className={cn(
        'animate-spin',
        sizeClasses[size],
        className
      )} 
    />
  );
}

export function LoadingPage({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mb-4" />
        <p className="text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

// Enhanced loading state for specific sections
export function LoadingCard({ title, message }: { title?: string; message?: string }) {
  return (
    <Card className="animate-pulse">
      <CardContent className="p-6">
        <div className="flex items-center space-x-3">
          <LoadingSpinner size="sm" />
          <div>
            {title && <h3 className="font-medium text-sm">{title}</h3>}
            <p className="text-xs text-muted-foreground">{message || 'Loading...'}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Skeleton loader for data tables
export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="h-9 w-[250px] bg-muted animate-pulse rounded-md" />
        <div className="h-9 w-[100px] bg-muted animate-pulse rounded-md" />
      </div>
      <div className="border rounded-md">
        <div className="h-12 border-b bg-muted/50" />
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-14 border-b last:border-b-0 bg-muted/20 animate-pulse flex items-center space-x-4 px-4">
            {Array.from({ length: columns }).map((_, j) => (
              <div key={j} className="h-4 bg-muted/60 rounded flex-1" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// Loading overlay for components
export function LoadingOverlay({ show, message }: { show: boolean; message?: string }) {
  if (!show) return null;
  
  return (
    <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mb-2" />
        <p className="text-sm text-muted-foreground">{message || 'Loading...'}</p>
      </div>
    </div>
  );
}

// Connection status indicator
export function ConnectionStatus({ isOnline = true }: { isOnline?: boolean }) {
  return (
    <div className={cn(
      "flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium",
      isOnline 
        ? "bg-green-100 text-green-800" 
        : "bg-red-100 text-red-800"
    )}>
      {isOnline ? (
        <>
          <Wifi className="h-3 w-3" />
          <span>Connected</span>
        </>
      ) : (
        <>
          <WifiOff className="h-3 w-3" />
          <span>Offline</span>
        </>
      )}
    </div>
  );
}