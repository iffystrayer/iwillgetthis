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
import { CalendarIcon, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { assessmentsApi } from '@/lib/api';

interface NewAssessmentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAssessmentCreated?: () => void;
}

const frameworks = [
  'NIST Cybersecurity Framework',
  'ISO 27001',
  'SOC 2',
  'PCI DSS',
  'HIPAA',
  'GDPR',
  'COBIT',
  'COSO',
  'Custom Framework',
];

const assessmentTypes = [
  'Internal Security Assessment',
  'External Security Assessment', 
  'Compliance Assessment',
  'Risk Assessment',
  'Penetration Testing',
  'Vulnerability Assessment',
  'Third-Party Assessment',
];

export function NewAssessmentDialog({
  open,
  onOpenChange,
  onAssessmentCreated,
}: NewAssessmentDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dueDate, setDueDate] = useState<Date>();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    framework: '',
    type: '',
    assessor: '',
    scope: '',
  });

  const handleClose = () => {
    setFormData({
      name: '',
      description: '',
      framework: '',
      type: '',
      assessor: '',
      scope: '',
    });
    setDueDate(undefined);
    setError(null);
    onOpenChange(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Assessment name is required');
      return;
    }
    
    if (!formData.framework) {
      setError('Framework selection is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const assessmentData = {
        ...formData,
        due_date: dueDate ? format(dueDate, 'yyyy-MM-dd') : null,
        status: 'Planning',
        progress: 0,
        created_date: new Date().toISOString(),
      };

      console.log('Creating assessment with data:', assessmentData);
      await assessmentsApi.create(assessmentData);
      
      console.log('✅ Assessment created successfully');
      
      if (onAssessmentCreated) {
        onAssessmentCreated();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to create assessment:', err);
      setError(err.response?.data?.message || err.message || 'Failed to create assessment');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Assessment</DialogTitle>
          <DialogDescription>
            Set up a new security or compliance assessment. Fill in the details below to get started.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md">
              {error}
            </div>
          )}
          
          <div className="grid gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Assessment Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Q4 2024 SOC 2 Assessment"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe the assessment objectives and scope..."
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="framework">Framework *</Label>
                <Select 
                  value={formData.framework} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, framework: value }))}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select framework" />
                  </SelectTrigger>
                  <SelectContent>
                    {frameworks.map((framework) => (
                      <SelectItem key={framework} value={framework}>
                        {framework}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="type">Assessment Type</Label>
                <Select 
                  value={formData.type} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {assessmentTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="assessor">Lead Assessor</Label>
                <Input
                  id="assessor"
                  placeholder="Enter assessor name"
                  value={formData.assessor}
                  onChange={(e) => setFormData(prev => ({ ...prev, assessor: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label>Due Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !dueDate && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dueDate ? format(dueDate, "PPP") : "Select due date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
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

            <div className="space-y-2">
              <Label htmlFor="scope">Scope</Label>
              <Textarea
                id="scope"
                placeholder="Define what systems, processes, or areas will be assessed..."
                value={formData.scope}
                onChange={(e) => setFormData(prev => ({ ...prev, scope: e.target.value }))}
                rows={2}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Assessment
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}