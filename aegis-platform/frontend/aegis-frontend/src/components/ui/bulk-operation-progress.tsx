import React, { useState, useEffect } from 'react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertCircle, Loader2, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface BulkOperationItem {
  id: string | number;
  name?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
}

export interface BulkOperationProgressProps {
  isOpen: boolean;
  onClose: () => void;
  operation: string;
  items: BulkOperationItem[];
  onCancel?: () => void;
  canCancel?: boolean;
  showDetails?: boolean;
}

export function BulkOperationProgress({
  isOpen,
  onClose,
  operation,
  items,
  onCancel,
  canCancel = false,
  showDetails = true,
}: BulkOperationProgressProps) {
  const [startTime] = useState(Date.now());
  const [elapsed, setElapsed] = useState(0);

  // Update elapsed time
  useEffect(() => {
    if (!isOpen) return;
    
    const interval = setInterval(() => {
      setElapsed(Date.now() - startTime);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isOpen, startTime]);

  if (!isOpen) return null;

  const totalItems = items.length;
  const completedItems = items.filter(item => item.status === 'completed').length;
  const failedItems = items.filter(item => item.status === 'failed').length;
  const processingItems = items.filter(item => item.status === 'processing').length;
  const pendingItems = items.filter(item => item.status === 'pending').length;
  
  const progress = totalItems > 0 ? ((completedItems + failedItems) / totalItems) * 100 : 0;
  const isComplete = completedItems + failedItems === totalItems;
  const hasErrors = failedItems > 0;

  const formatElapsedTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusIcon = (status: BulkOperationItem['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: BulkOperationItem['status']) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'processing':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Processing</Badge>;
      default:
        return <Badge variant="outline">Pending</Badge>;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[80vh] overflow-hidden">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                {!isComplete ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : hasErrors ? (
                  <AlertCircle className="h-5 w-5 text-orange-600" />
                ) : (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                )}
                {operation}
              </CardTitle>
              <CardDescription>
                {isComplete
                  ? hasErrors
                    ? `Completed with ${failedItems} error${failedItems !== 1 ? 's' : ''}`
                    : 'Operation completed successfully'
                  : `Processing ${totalItems} item${totalItems !== 1 ? 's' : ''}...`
                }
              </CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">{completedItems}</div>
              <div className="text-muted-foreground">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-red-600">{failedItems}</div>
              <div className="text-muted-foreground">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-600">{processingItems}</div>
              <div className="text-muted-foreground">Processing</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-500">{pendingItems}</div>
              <div className="text-muted-foreground">Pending</div>
            </div>
          </div>

          {/* Timing Info */}
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Elapsed: {formatElapsedTime(elapsed)}</span>
            {!isComplete && totalItems > 0 && (
              <span>
                ETA: {Math.round((elapsed / (completedItems + failedItems)) * pendingItems / 1000)}s
              </span>
            )}
          </div>

          {/* Detailed Items List */}
          {showDetails && (
            <div className="space-y-2">
              <div className="text-sm font-medium">Item Details</div>
              <div className="max-h-40 overflow-y-auto space-y-1">
                {items.map((item) => (
                  <div
                    key={item.id}
                    className={cn(
                      "flex items-center justify-between p-2 rounded-md text-sm",
                      item.status === 'completed' && "bg-green-50",
                      item.status === 'failed' && "bg-red-50",
                      item.status === 'processing' && "bg-blue-50"
                    )}
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      {getStatusIcon(item.status)}
                      <span className="truncate">
                        {item.name || `Item ${item.id}`}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(item.status)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Details */}
          {hasErrors && showDetails && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-red-600">Errors</div>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {items
                  .filter(item => item.status === 'failed' && item.error)
                  .map((item) => (
                    <div key={item.id} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                      <div className="font-medium">{item.name || `Item ${item.id}`}</div>
                      <div className="text-xs text-red-500">{item.error}</div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-2">
            {!isComplete && canCancel && (
              <Button variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
            {isComplete && (
              <Button onClick={onClose}>
                {hasErrors ? 'Close' : 'Done'}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Hook for managing bulk operation progress
export function useBulkOperationProgress() {
  const [isOpen, setIsOpen] = useState(false);
  const [operation, setOperation] = useState('');
  const [items, setItems] = useState<BulkOperationItem[]>([]);
  const [canCancel, setCanCancel] = useState(false);

  const startOperation = (
    operationName: string,
    operationItems: (string | number | { id: string | number; name?: string })[],
    cancelable = false
  ) => {
    const formattedItems: BulkOperationItem[] = operationItems.map(item => ({
      id: typeof item === 'object' ? item.id : item,
      name: typeof item === 'object' ? item.name : undefined,
      status: 'pending'
    }));

    setOperation(operationName);
    setItems(formattedItems);
    setCanCancel(cancelable);
    setIsOpen(true);
  };

  const updateItemStatus = (
    itemId: string | number,
    status: BulkOperationItem['status'],
    error?: string
  ) => {
    setItems(prevItems =>
      prevItems.map(item =>
        item.id === itemId ? { ...item, status, error } : item
      )
    );
  };

  const closeProgress = () => {
    setIsOpen(false);
    // Clear state after animation
    setTimeout(() => {
      setItems([]);
      setOperation('');
      setCanCancel(false);
    }, 300);
  };

  return {
    isOpen,
    operation,
    items,
    canCancel,
    startOperation,
    updateItemStatus,
    closeProgress,
  };
}