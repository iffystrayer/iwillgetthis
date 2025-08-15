import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  X, 
  ChevronDown, 
  Download, 
  Upload, 
  Trash2, 
  Edit, 
  Copy, 
  Archive,
  CheckSquare,
  AlertTriangle,
  Shield
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface BulkAction {
  id: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
  variant?: 'default' | 'destructive' | 'secondary' | 'outline';
  disabled?: boolean;
  onClick: () => void;
  requiresConfirmation?: boolean;
  confirmationMessage?: string;
}

export interface BulkActionsToolbarProps {
  selectedCount: number;
  totalCount: number;
  onClearSelection: () => void;
  actions: BulkAction[];
  className?: string;
  maxVisibleActions?: number;
}

export function BulkActionsToolbar({
  selectedCount,
  totalCount,
  onClearSelection,
  actions,
  className,
  maxVisibleActions = 3,
}: BulkActionsToolbarProps) {
  if (selectedCount === 0) {
    return null;
  }

  const visibleActions = actions.slice(0, maxVisibleActions);
  const hiddenActions = actions.slice(maxVisibleActions);

  return (
    <div className={cn(
      "flex items-center gap-3 px-4 py-3 bg-muted/50 border rounded-lg",
      className
    )}>
      {/* Selection Summary */}
      <div className="flex items-center gap-2">
        <Badge variant="secondary">
          {selectedCount} of {totalCount} selected
        </Badge>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearSelection}
          className="h-6 w-6 p-0"
        >
          <X className="h-3 w-3" />
        </Button>
      </div>

      <Separator orientation="vertical" className="h-6" />

      {/* Visible Actions */}
      <div className="flex items-center gap-2">
        {visibleActions.map((action) => {
          const Icon = action.icon;
          
          return (
            <Button
              key={action.id}
              variant={action.variant || 'outline'}
              size="sm"
              onClick={action.onClick}
              disabled={action.disabled}
              className="h-8"
            >
              {Icon && <Icon className="h-3 w-3 mr-1" />}
              {action.label}
            </Button>
          );
        })}
      </div>

      {/* Hidden Actions Dropdown */}
      {hiddenActions.length > 0 && (
        <>
          <Separator orientation="vertical" className="h-6" />
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-8">
                More
                <ChevronDown className="h-3 w-3 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {hiddenActions.map((action, index) => {
                const Icon = action.icon;
                
                return (
                  <React.Fragment key={action.id}>
                    {index > 0 && action.variant === 'destructive' && (
                      <DropdownMenuSeparator />
                    )}
                    <DropdownMenuItem
                      onClick={action.onClick}
                      disabled={action.disabled}
                      className={cn(
                        action.variant === 'destructive' && 'text-destructive focus:text-destructive'
                      )}
                    >
                      {Icon && <Icon className="h-4 w-4 mr-2" />}
                      {action.label}
                    </DropdownMenuItem>
                  </React.Fragment>
                );
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        </>
      )}
    </div>
  );
}

// Preset bulk actions for common use cases
export const createCommonBulkActions = (
  selectedItems: any[],
  callbacks: {
    onEdit?: () => void;
    onDelete?: () => void;
    onExport?: () => void;
    onArchive?: () => void;
    onDuplicate?: () => void;
    onAssign?: () => void;
    onUpdateStatus?: () => void;
  }
): BulkAction[] => {
  const actions: BulkAction[] = [];

  if (callbacks.onEdit) {
    actions.push({
      id: 'edit',
      label: 'Edit',
      icon: Edit,
      variant: 'outline',
      onClick: callbacks.onEdit,
    });
  }

  if (callbacks.onAssign) {
    actions.push({
      id: 'assign',
      label: 'Assign',
      icon: CheckSquare,
      variant: 'outline',
      onClick: callbacks.onAssign,
    });
  }

  if (callbacks.onUpdateStatus) {
    actions.push({
      id: 'status',
      label: 'Update Status',
      icon: AlertTriangle,
      variant: 'outline',
      onClick: callbacks.onUpdateStatus,
    });
  }

  if (callbacks.onDuplicate) {
    actions.push({
      id: 'duplicate',
      label: 'Duplicate',
      icon: Copy,
      variant: 'outline',
      onClick: callbacks.onDuplicate,
    });
  }

  if (callbacks.onExport) {
    actions.push({
      id: 'export',
      label: 'Export',
      icon: Download,
      variant: 'outline',
      onClick: callbacks.onExport,
    });
  }

  if (callbacks.onArchive) {
    actions.push({
      id: 'archive',
      label: 'Archive',
      icon: Archive,
      variant: 'secondary',
      onClick: callbacks.onArchive,
    });
  }

  if (callbacks.onDelete) {
    actions.push({
      id: 'delete',
      label: 'Delete',
      icon: Trash2,
      variant: 'destructive',
      onClick: callbacks.onDelete,
      requiresConfirmation: true,
      confirmationMessage: `Are you sure you want to delete ${selectedItems.length} items? This action cannot be undone.`,
    });
  }

  return actions;
};