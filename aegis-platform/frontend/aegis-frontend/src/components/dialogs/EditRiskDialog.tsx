import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { AlertTriangle, AlertCircle, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { risksApi } from '@/lib/api';

interface EditRiskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  risk: any | null;
  onRiskUpdated?: () => void;
}

interface RiskFormData {
  title: string;
  description: string;
  category: string;
  probability: string;
  impact: string;
  status: string;
  owner: string;
  mitigation_strategy: string;
  review_date: string;
}

const riskCategories = [
  'Cybersecurity',
  'Operational',
  'Financial', 
  'Compliance',
  'Strategic',
  'Reputational',
  'Technology',
  'Third Party',
  'Physical',
  'Environmental'
];

const probabilityLevels = [
  { value: '1', label: 'Very Low (1)', description: 'Highly unlikely to occur' },
  { value: '2', label: 'Low (2)', description: 'Unlikely to occur' },
  { value: '3', label: 'Medium (3)', description: 'May occur' },
  { value: '4', label: 'High (4)', description: 'Likely to occur' },
  { value: '5', label: 'Very High (5)', description: 'Almost certain to occur' }
];

const impactLevels = [
  { value: '1', label: 'Very Low (1)', description: 'Negligible impact' },
  { value: '2', label: 'Low (2)', description: 'Minor impact' },
  { value: '3', label: 'Medium (3)', description: 'Moderate impact' },
  { value: '4', label: 'High (4)', description: 'Major impact' },
  { value: '5', label: 'Very High (5)', description: 'Catastrophic impact' }
];

const statusOptions = [
  'Open',
  'In Progress',
  'Under Review',
  'Mitigated',
  'Accepted',
  'Closed'
];

export function EditRiskDialog({ open, onOpenChange, risk, onRiskUpdated }: EditRiskDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, reset, setValue, formState: { errors }, watch } = useForm<RiskFormData>();

  const selectedCategory = watch('category');
  const selectedProbability = watch('probability');
  const selectedImpact = watch('impact');
  const selectedStatus = watch('status');

  // Calculate risk score
  const riskScore = selectedProbability && selectedImpact 
    ? parseInt(selectedProbability) * parseInt(selectedImpact)
    : 0;

  const getRiskLevel = (score: number) => {
    if (score >= 20) return { level: 'Critical', color: 'bg-red-100 text-red-800', variant: 'destructive' as const };
    if (score >= 15) return { level: 'High', color: 'bg-orange-100 text-orange-800', variant: 'destructive' as const };
    if (score >= 10) return { level: 'Medium', color: 'bg-yellow-100 text-yellow-800', variant: 'secondary' as const };
    if (score >= 5) return { level: 'Low', color: 'bg-blue-100 text-blue-800', variant: 'secondary' as const };
    return { level: 'Very Low', color: 'bg-green-100 text-green-800', variant: 'outline' as const };
  };

  const riskLevel = getRiskLevel(riskScore);

  useEffect(() => {
    if (risk && open) {
      setValue('title', risk.title || '');
      setValue('description', risk.description || '');
      setValue('category', risk.category || '');
      setValue('probability', risk.probability || '3');
      setValue('impact', risk.impact || '3');
      setValue('status', risk.status || 'Open');
      setValue('owner', risk.owner || '');
      setValue('mitigation_strategy', risk.mitigation_strategy || '');
      setValue('review_date', risk.review_date ? risk.review_date.split('T')[0] : '');
      setError(null);
    }
  }, [risk, open, setValue]);

  const handleClose = () => {
    reset();
    setError(null);
    onOpenChange(false);
  };

  const onSubmit = async (data: RiskFormData) => {
    if (!risk) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const updateData = {
        ...data,
        risk_score: riskScore,
        risk_level: riskLevel.level,
        last_updated: new Date().toISOString(),
        updated_by: 'current_user' // TODO: Get from auth context
      };

      console.log('Updating risk with data:', updateData);
      await risksApi.update(risk.id, updateData);
      
      console.log('✅ Risk updated successfully');
      
      if (onRiskUpdated) {
        onRiskUpdated();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to update risk:', err);
      setError(err.response?.data?.message || err.message || 'Failed to update risk');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!risk) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Edit Risk
          </DialogTitle>
          <DialogDescription>
            Update risk assessment and mitigation details.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Risk Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Risk Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="title">Risk Title *</Label>
              <Input
                id="title"
                {...register('title', { required: 'Risk title is required' })}
                placeholder="e.g., Data breach due to weak authentication"
              />
              {errors.title && (
                <p className="text-sm text-destructive">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Risk Description *</Label>
              <Textarea
                id="description"
                {...register('description', { required: 'Risk description is required' })}
                placeholder="Describe the risk scenario and potential consequences"
                rows={3}
              />
              {errors.description && (
                <p className="text-sm text-destructive">{errors.description.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Risk Category *</Label>
                <Select
                  value={selectedCategory}
                  onValueChange={(value) => setValue('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {riskCategories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.category && (
                  <p className="text-sm text-destructive">Risk category is required</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">Status *</Label>
                <Select
                  value={selectedStatus}
                  onValueChange={(value) => setValue('status', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    {statusOptions.map((status) => (
                      <SelectItem key={status} value={status}>
                        {status}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.status && (
                  <p className="text-sm text-destructive">Status is required</p>
                )}
              </div>
            </div>
          </div>

          {/* Risk Assessment */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Risk Assessment</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="probability">Probability *</Label>
                <Select
                  value={selectedProbability}
                  onValueChange={(value) => setValue('probability', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select probability" />
                  </SelectTrigger>
                  <SelectContent>
                    {probabilityLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        <div className="flex flex-col">
                          <span className="font-medium">{level.label}</span>
                          <span className="text-sm text-muted-foreground">{level.description}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.probability && (
                  <p className="text-sm text-destructive">Probability is required</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="impact">Impact *</Label>
                <Select
                  value={selectedImpact}
                  onValueChange={(value) => setValue('impact', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select impact" />
                  </SelectTrigger>
                  <SelectContent>
                    {impactLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        <div className="flex flex-col">
                          <span className="font-medium">{level.label}</span>
                          <span className="text-sm text-muted-foreground">{level.description}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.impact && (
                  <p className="text-sm text-destructive">Impact is required</p>
                )}
              </div>
            </div>

            {/* Risk Score Display */}
            {selectedProbability && selectedImpact && (
              <div className="bg-muted p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Calculated Risk Score</p>
                    <p className="text-2xl font-bold">{riskScore}</p>
                    <p className="text-sm text-muted-foreground">
                      Probability ({selectedProbability}) × Impact ({selectedImpact})
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium mb-2">Risk Level</p>
                    <Badge variant={riskLevel.variant} className="text-sm">
                      {riskLevel.level}
                    </Badge>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Risk Management */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Risk Management</h3>
            
            <div className="space-y-2">
              <Label htmlFor="owner">Risk Owner</Label>
              <Input
                id="owner"
                {...register('owner')}
                placeholder="Person or team responsible for managing this risk"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="mitigation_strategy">Mitigation Strategy</Label>
              <Textarea
                id="mitigation_strategy"
                {...register('mitigation_strategy')}
                placeholder="Describe the planned or implemented risk mitigation measures"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="review_date">Next Review Date</Label>
              <Input
                id="review_date"
                type="date"
                {...register('review_date')}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Update Risk
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}