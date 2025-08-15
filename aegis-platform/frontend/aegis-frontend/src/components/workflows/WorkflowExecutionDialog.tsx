import React, { useState } from 'react';
import { CheckCircle, XCircle, MessageSquare, UserPlus, ArrowUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { workflowAPI } from '@/lib/workflow-api';
import {
  WorkflowInstance,
  WorkflowExecutionRequest,
  ActionType,
  ACTION_TYPE_LABELS
} from '@/types/workflow';

interface WorkflowExecutionDialogProps {
  instance: WorkflowInstance;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExecutionComplete: () => void;
}

export const WorkflowExecutionDialog: React.FC<WorkflowExecutionDialogProps> = ({
  instance,
  open,
  onOpenChange,
  onExecutionComplete
}) => {
  const [actionType, setActionType] = useState<ActionType>('approve');
  const [comment, setComment] = useState('');
  const [reassignToId, setReassignToId] = useState<number | undefined>();
  const [escalateToId, setEscalateToId] = useState<number | undefined>();
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const executionRequest: WorkflowExecutionRequest = {
        action_type: actionType,
        comment: comment || undefined,
        reassign_to_id: reassignToId,
        escalate_to_id: escalateToId
      };

      await workflowAPI.executeWorkflowAction(instance.id, executionRequest);
      
      toast({
        title: "Success",
        description: `Action "${ACTION_TYPE_LABELS[actionType]}" executed successfully`,
      });
      
      onExecutionComplete();
    } catch (error) {
      console.error('Error executing workflow action:', error);
      toast({
        title: "Error",
        description: "Failed to execute workflow action",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setActionType('approve');
    setComment('');
    setReassignToId(undefined);
    setEscalateToId(undefined);
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      resetForm();
    }
    onOpenChange(newOpen);
  };

  const getActionIcon = (action: ActionType) => {
    switch (action) {
      case 'approve':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'reject':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'comment':
        return <MessageSquare className="h-4 w-4 text-blue-500" />;
      case 'reassign':
        return <UserPlus className="h-4 w-4 text-orange-500" />;
      case 'escalate':
        return <ArrowUp className="h-4 w-4 text-purple-500" />;
      default:
        return null;
    }
  };

  const getActionDescription = (action: ActionType) => {
    switch (action) {
      case 'approve':
        return 'Approve this workflow step and move to the next step';
      case 'reject':
        return 'Reject this workflow and end the process';
      case 'comment':
        return 'Add a comment without changing the workflow state';
      case 'reassign':
        return 'Reassign this workflow step to another user';
      case 'escalate':
        return 'Escalate this workflow to a higher authority';
      case 'request_information':
        return 'Request additional information from the initiator';
      case 'cancel':
        return 'Cancel this workflow instance';
      default:
        return '';
    }
  };

  const isCommentRequired = () => {
    return ['reject', 'escalate', 'request_information'].includes(actionType);
  };

  const isFormValid = () => {
    if (isCommentRequired() && !comment.trim()) {
      return false;
    }
    if (actionType === 'reassign' && !reassignToId) {
      return false;
    }
    if (actionType === 'escalate' && !escalateToId) {
      return false;
    }
    return true;
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Execute Workflow Action</DialogTitle>
          <DialogDescription>
            Execute an action on workflow instance #{instance.id}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Action Type Selection */}
          <div className="space-y-2">
            <Label htmlFor="action-type">Action Type</Label>
            <Select value={actionType} onValueChange={(value: ActionType) => setActionType(value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select an action" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="approve">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    Approve
                  </div>
                </SelectItem>
                <SelectItem value="reject">
                  <div className="flex items-center gap-2">
                    <XCircle className="h-4 w-4 text-red-500" />
                    Reject
                  </div>
                </SelectItem>
                <SelectItem value="comment">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-blue-500" />
                    Comment
                  </div>
                </SelectItem>
                <SelectItem value="reassign">
                  <div className="flex items-center gap-2">
                    <UserPlus className="h-4 w-4 text-orange-500" />
                    Reassign
                  </div>
                </SelectItem>
                <SelectItem value="escalate">
                  <div className="flex items-center gap-2">
                    <ArrowUp className="h-4 w-4 text-purple-500" />
                    Escalate
                  </div>
                </SelectItem>
                <SelectItem value="request_information">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-yellow-500" />
                    Request Information
                  </div>
                </SelectItem>
                <SelectItem value="cancel">
                  <div className="flex items-center gap-2">
                    <XCircle className="h-4 w-4 text-gray-500" />
                    Cancel
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-gray-500">
              {getActionDescription(actionType)}
            </p>
          </div>

          {/* Reassign User Selection */}
          {actionType === 'reassign' && (
            <div className="space-y-2">
              <Label htmlFor="reassign-to">Reassign To</Label>
              <Select value={reassignToId?.toString()} onValueChange={(value) => setReassignToId(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select user to reassign to" />
                </SelectTrigger>
                <SelectContent>
                  {/* This would be populated with actual users from the API */}
                  <SelectItem value="1">John Doe (john@example.com)</SelectItem>
                  <SelectItem value="2">Jane Smith (jane@example.com)</SelectItem>
                  <SelectItem value="3">Admin User (admin@example.com)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Escalate User Selection */}
          {actionType === 'escalate' && (
            <div className="space-y-2">
              <Label htmlFor="escalate-to">Escalate To</Label>
              <Select value={escalateToId?.toString()} onValueChange={(value) => setEscalateToId(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select user to escalate to" />
                </SelectTrigger>
                <SelectContent>
                  {/* This would be populated with actual escalation targets from the API */}
                  <SelectItem value="1">Manager (manager@example.com)</SelectItem>
                  <SelectItem value="2">Department Head (head@example.com)</SelectItem>
                  <SelectItem value="3">Executive (exec@example.com)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Comment/Reason */}
          <div className="space-y-2">
            <Label htmlFor="comment">
              {isCommentRequired() ? 'Comment (Required)' : 'Comment (Optional)'}
            </Label>
            <Textarea
              id="comment"
              placeholder={
                actionType === 'approve' ? 'Optional approval comment...' :
                actionType === 'reject' ? 'Please provide a reason for rejection...' :
                actionType === 'escalate' ? 'Please provide a reason for escalation...' :
                actionType === 'request_information' ? 'Specify what information is needed...' :
                'Add your comment here...'
              }
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={3}
              className={isCommentRequired() && !comment.trim() ? 'border-red-300' : ''}
            />
            {isCommentRequired() && !comment.trim() && (
              <p className="text-sm text-red-500">Comment is required for this action</p>
            )}
          </div>

          {/* Current Instance Info */}
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="font-medium text-sm mb-2">Current Instance</h4>
            <div className="space-y-1 text-sm text-gray-600">
              <div>Status: <span className="font-medium">{instance.status}</span></div>
              <div>Entity: <span className="font-medium">{instance.entity_type} #{instance.entity_id}</span></div>
              {instance.current_assignee && (
                <div>
                  Assigned to: <span className="font-medium">
                    {instance.current_assignee.full_name || instance.current_assignee.email}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!isFormValid() || loading}
            className="min-w-[100px]"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-foreground" />
                Executing...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                {getActionIcon(actionType)}
                Execute
              </div>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};