import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Plus, AlertTriangle, Building, Calendar, User } from 'lucide-react';

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
import { Badge } from '@/components/ui/badge';
import { risksApi } from '@/lib/api';

interface AddRiskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onRiskAdded?: () => void;
}

interface RiskFormData {
  title: string;
  description: string;
  category: string;
  level: string;
  probability: number;
  impact: number;
  owner: string;
  due_date: string;
  tags: string[];
}

export function AddRiskDialog({ open, onOpenChange, onRiskAdded }: AddRiskDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<RiskFormData>({
    defaultValues: {
      title: '',
      description: '',
      category: 'Technical',
      level: 'medium',
      probability: 5,
      impact: 5,
      owner: '',
      due_date: '',
      tags: [],
    },
  });

  const selectedCategory = watch('category');
  const selectedLevel = watch('level');
  const probability = watch('probability');
  const impact = watch('impact');

  const calculateRiskScore = () => {
    return ((probability * impact) / 2).toFixed(1);
  };

  const handleClose = () => {
    reset();
    setError(null);
    onOpenChange(false);
  };

  const onSubmit = async (data: RiskFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      console.log('Creating risk with data:', data);
      
      // Calculate risk score
      const riskScore = (data.probability * data.impact) / 2;
      
      // Create risk through API
      await risksApi.create({
        ...data,
        score: riskScore,
        status: 'identified',
      });
      
      console.log('✅ Risk created successfully:', data);
      
      // Show success and refresh parent component
      if (onRiskAdded) {
        onRiskAdded();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to create risk:', err);
      setError(err.message || 'Failed to create risk. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const categoryOptions = [
    { value: 'Technical', color: 'destructive' as const },
    { value: 'Operational', color: 'default' as const },
    { value: 'Financial', color: 'secondary' as const },
    { value: 'Strategic', color: 'outline' as const },
    { value: 'Compliance', color: 'secondary' as const },
    { value: 'Human Factor', color: 'default' as const },
  ];

  const levelOptions = [
    { value: 'critical', label: 'Critical', color: 'destructive' as const },
    { value: 'high', label: 'High', color: 'default' as const },
    { value: 'medium', label: 'Medium', color: 'secondary' as const },
    { value: 'low', label: 'Low', color: 'outline' as const },
  ];

  const selectedCategoryInfo = categoryOptions.find(cat => cat.value === selectedCategory);
  const selectedLevelInfo = levelOptions.find(level => level.value === selectedLevel);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Add New Risk
          </DialogTitle>
          <DialogDescription>
            Document a new risk to the risk register with appropriate categorization and scoring.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Risk Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Risk Title
            </Label>
            <Input
              id="title"
              placeholder="Enter a clear, concise risk title"
              {...register('title', {
                required: 'Risk title is required',
                minLength: { value: 5, message: 'Title must be at least 5 characters' },
              })}
              className={errors.title ? 'border-red-500' : ''}
            />
            {errors.title && (
              <p className="text-sm text-red-600">{errors.title.message}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">
              Description
            </Label>
            <Textarea
              id="description"
              placeholder="Describe the risk, its potential causes, and consequences"
              rows={3}
              {...register('description', {
                required: 'Risk description is required',
                minLength: { value: 10, message: 'Description must be at least 10 characters' },
              })}
              className={errors.description ? 'border-red-500' : ''}
            />
            {errors.description && (
              <p className="text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          {/* Category and Level Row */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Building className="h-4 w-4" />
                Category
              </Label>
              <Select
                value={selectedCategory}
                onValueChange={(value) => setValue('category', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categoryOptions.map((category) => (
                    <SelectItem key={category.value} value={category.value}>
                      <div className="flex items-center gap-2">
                        <Badge variant={category.color} className="text-xs">
                          {category.value}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedCategoryInfo && (
                <Badge variant={selectedCategoryInfo.color} className="text-xs">
                  {selectedCategoryInfo.value}
                </Badge>
              )}
            </div>

            <div className="space-y-2">
              <Label>Risk Level</Label>
              <Select
                value={selectedLevel}
                onValueChange={(value) => setValue('level', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select level" />
                </SelectTrigger>
                <SelectContent>
                  {levelOptions.map((level) => (
                    <SelectItem key={level.value} value={level.value}>
                      <div className="flex items-center gap-2">
                        <Badge variant={level.color} className="text-xs">
                          {level.label}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedLevelInfo && (
                <Badge variant={selectedLevelInfo.color} className="text-xs">
                  {selectedLevelInfo.label}
                </Badge>
              )}
            </div>
          </div>

          {/* Risk Scoring */}
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium">Risk Assessment</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="probability">
                  Probability (1-10)
                </Label>
                <Input
                  id="probability"
                  type="number"
                  min="1"
                  max="10"
                  {...register('probability', {
                    required: 'Probability is required',
                    min: { value: 1, message: 'Minimum value is 1' },
                    max: { value: 10, message: 'Maximum value is 10' },
                    valueAsNumber: true,
                  })}
                  className={errors.probability ? 'border-red-500' : ''}
                />
                {errors.probability && (
                  <p className="text-sm text-red-600">{errors.probability.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="impact">
                  Impact (1-10)
                </Label>
                <Input
                  id="impact"
                  type="number"
                  min="1"
                  max="10"
                  {...register('impact', {
                    required: 'Impact is required',
                    min: { value: 1, message: 'Minimum value is 1' },
                    max: { value: 10, message: 'Maximum value is 10' },
                    valueAsNumber: true,
                  })}
                  className={errors.impact ? 'border-red-500' : ''}
                />
                {errors.impact && (
                  <p className="text-sm text-red-600">{errors.impact.message}</p>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between p-2 bg-white rounded border">
              <span className="text-sm font-medium">Calculated Risk Score:</span>
              <Badge variant="outline" className="font-mono">
                {calculateRiskScore()}
              </Badge>
            </div>
          </div>

          {/* Owner and Due Date */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="owner" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Risk Owner
              </Label>
              <Input
                id="owner"
                placeholder="Risk owner/responsible party"
                {...register('owner', {
                  required: 'Risk owner is required',
                })}
                className={errors.owner ? 'border-red-500' : ''}
              />
              {errors.owner && (
                <p className="text-sm text-red-600">{errors.owner.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="due_date" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Target Date
              </Label>
              <Input
                id="due_date"
                type="date"
                {...register('due_date', {
                  required: 'Target date is required',
                })}
                className={errors.due_date ? 'border-red-500' : ''}
              />
              {errors.due_date && (
                <p className="text-sm text-red-600">{errors.due_date.message}</p>
              )}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Risk
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}