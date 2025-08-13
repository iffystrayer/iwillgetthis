import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { CalendarIcon, Loader2, CheckSquare, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { tasksApi } from '@/lib/api';

interface NewTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskCreated?: () => void;
}

const priorities = [
  { value: 'Low', label: 'Low Priority' },
  { value: 'Medium', label: 'Medium Priority' },
  { value: 'High', label: 'High Priority' },
  { value: 'Critical', label: 'Critical Priority' },
];

const taskTypes = [
  'Security Review',
  'Compliance Task',
  'Risk Assessment',
  'Vulnerability Remediation',
  'Policy Update',
  'Training Task',
  'Audit Task',
  'Incident Response',
  'General Task',
];

export function NewTaskDialog({
  open,
  onOpenChange,
  onTaskCreated,
}: NewTaskDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dueDate, setDueDate] = useState<Date>();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: '',
    type: '',
    assigned_to: '',
    category: '',
  });

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      priority: '',
      type: '',
      assigned_to: '',
      category: '',
    });
    setDueDate(undefined);
    setError(null);
    onOpenChange(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      setError('Task title is required');
      return;
    }
    
    if (!formData.priority) {
      setError('Priority selection is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const taskData = {
        ...formData,
        due_date: dueDate ? format(dueDate, 'yyyy-MM-dd') : null,
        status: 'Open',
        progress: 0,
        created_date: new Date().toISOString(),
      };

      console.log('Creating task with data:', taskData);
      await tasksApi.create(taskData);
      
      console.log('✅ Task created successfully');
      
      if (onTaskCreated) {
        onTaskCreated();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to create task:', err);
      setError(err.response?.data?.message || err.message || 'Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto form-glass border-0">
        <DialogHeader className="text-center space-y-3">
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center justify-center gap-3">
            <CheckSquare className="h-6 w-6 text-indigo-600" />
            ✨ Create New Task
          </DialogTitle>
          <DialogDescription className="text-muted-foreground/80">
            Create a new security or compliance task with our comprehensive task management system
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="glass border-red-200/50 bg-red-50/80 p-4 rounded-xl flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-sm text-red-800 font-medium">{error}</p>
            </div>
          )}
          
          <div className="grid gap-4">
            <div className="space-y-3">
              <Label htmlFor="title" className="text-sm font-semibold text-foreground/90">📋 Task Title *</Label>
              <Input
                id="title"
                placeholder="e.g., Review firewall configuration for Q4"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                required
                className="input-glass h-12 text-base"
              />
            </div>

            <div className="space-y-3">
              <Label htmlFor="description" className="text-sm font-semibold text-foreground/90">📝 Description</Label>
              <Textarea
                id="description"
                placeholder="Describe the task objectives and requirements..."
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                className="input-glass resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <Label htmlFor="priority" className="text-sm font-semibold text-foreground/90">⚡ Priority *</Label>
                <Select 
                  value={formData.priority} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}
                  required
                >
                  <SelectTrigger className="input-glass h-11">
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent className="glass border-0">
                    {priorities.map((priority) => (
                      <SelectItem key={priority.value} value={priority.value} className="hover:bg-primary/10">
                        {priority.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <Label htmlFor="type" className="text-sm font-semibold text-foreground/90">🏷️ Task Type</Label>
                <Select 
                  value={formData.type} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}
                >
                  <SelectTrigger className="input-glass h-11">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent className="glass border-0">
                    {taskTypes.map((type) => (
                      <SelectItem key={type} value={type} className="hover:bg-primary/10">
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <Label htmlFor="assigned_to" className="text-sm font-semibold text-foreground/90">👤 Assigned To</Label>
                <Input
                  id="assigned_to"
                  placeholder="Enter assignee name"
                  value={formData.assigned_to}
                  onChange={(e) => setFormData(prev => ({ ...prev, assigned_to: e.target.value }))}
                  className="input-glass h-11"
                />
              </div>

              <div className="space-y-3">
                <Label className="text-sm font-semibold text-foreground/90">📅 Due Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal input-glass h-11",
                        !dueDate && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dueDate ? format(dueDate, "PPP") : "Select due date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 glass border-0" align="start">
                    <Calendar
                      mode="single"
                      selected={dueDate}
                      onSelect={setDueDate}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </div>

            <div className="space-y-3">
              <Label htmlFor="category" className="text-sm font-semibold text-foreground/90">📂 Category</Label>
              <Input
                id="category"
                placeholder="e.g., Infrastructure, Compliance, Security"
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="input-glass h-12 text-base"
              />
            </div>
          </div>

          <DialogFooter className="flex justify-end space-x-3 pt-6">
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleClose}
              className="glass border-primary/20 hover:border-primary/40 px-6 h-11"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="btn-gradient-primary px-8 h-11 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <CheckSquare className="h-4 w-4 mr-2" />
              Create Task
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}