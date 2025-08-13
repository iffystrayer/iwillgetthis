import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Plus, Database, Building, MapPin, Cpu, AlertCircle } from 'lucide-react';

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
import { assetsApi } from '@/lib/api';

interface AddAssetDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAssetAdded?: () => void;
}

interface AssetFormData {
  name: string;
  description: string;
  asset_type: string;
  criticality: string;
  status: string;
  environment: string;
  ip_address: string;
  hostname: string;
  operating_system: string;
  location: string;
  business_unit: string;
}

export function AddAssetDialog({ open, onOpenChange, onAssetAdded }: AddAssetDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<AssetFormData>({
    defaultValues: {
      name: '',
      description: '',
      asset_type: 'server',
      criticality: 'medium',
      status: 'active',
      environment: 'production',
      ip_address: '',
      hostname: '',
      operating_system: '',
      location: '',
      business_unit: '',
    },
  });

  const selectedAssetType = watch('asset_type');
  const selectedCriticality = watch('criticality');
  const selectedEnvironment = watch('environment');

  const handleClose = () => {
    reset();
    setError(null);
    onOpenChange(false);
  };

  const onSubmit = async (data: AssetFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      console.log('Creating asset with data:', data);
      
      // Create asset through API
      await assetsApi.create(data);
      
      console.log('✅ Asset created successfully:', data);
      
      // Show success and refresh parent component
      if (onAssetAdded) {
        onAssetAdded();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to create asset:', err);
      setError(err.message || 'Failed to create asset. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const assetTypeOptions = [
    { value: 'server', label: 'Server', color: 'destructive' as const },
    { value: 'workstation', label: 'Workstation', color: 'default' as const },
    { value: 'network_device', label: 'Network Device', color: 'secondary' as const },
    { value: 'database', label: 'Database', color: 'outline' as const },
    { value: 'application', label: 'Application', color: 'default' as const },
    { value: 'mobile_device', label: 'Mobile Device', color: 'secondary' as const },
    { value: 'iot_device', label: 'IoT Device', color: 'outline' as const },
    { value: 'other', label: 'Other', color: 'secondary' as const },
  ];

  const criticalityOptions = [
    { value: 'critical', label: 'Critical', color: 'destructive' as const },
    { value: 'high', label: 'High', color: 'default' as const },
    { value: 'medium', label: 'Medium', color: 'secondary' as const },
    { value: 'low', label: 'Low', color: 'outline' as const },
  ];

  const environmentOptions = [
    { value: 'production', label: 'Production', color: 'destructive' as const },
    { value: 'staging', label: 'Staging', color: 'default' as const },
    { value: 'development', label: 'Development', color: 'secondary' as const },
    { value: 'testing', label: 'Testing', color: 'outline' as const },
  ];

  const selectedAssetTypeInfo = assetTypeOptions.find(type => type.value === selectedAssetType);
  const selectedCriticalityInfo = criticalityOptions.find(crit => crit.value === selectedCriticality);
  const selectedEnvironmentInfo = environmentOptions.find(env => env.value === selectedEnvironment);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto form-glass border-0">
        <DialogHeader className="text-center space-y-3">
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center justify-center gap-3">
            <Database className="h-6 w-6 text-indigo-600" />
            ✨ Add New Asset
          </DialogTitle>
          <DialogDescription className="text-muted-foreground/80">
            Register a new asset in the asset management system with comprehensive security details
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Asset Name - Glass Input */}
          <div className="space-y-3">
            <Label htmlFor="name" className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <Database className="h-4 w-4" />
              🏢 Asset Name *
            </Label>
            <Input
              id="name"
              placeholder="Enter asset name"
              {...register('name', {
                required: 'Asset name is required',
                minLength: { value: 2, message: 'Name must be at least 2 characters' },
              })}
              className={`input-glass h-12 text-base ${errors.name ? 'border-red-500/50' : ''}`}
            />
            {errors.name && (
              <p className="text-sm text-red-500 font-medium">{errors.name.message}</p>
            )}
          </div>

          {/* Description - Glass Textarea */}
          <div className="space-y-3">
            <Label htmlFor="description" className="text-sm font-semibold text-foreground/90">
              📝 Description *
            </Label>
            <Textarea
              id="description"
              placeholder="Describe the asset's purpose and characteristics"
              rows={3}
              {...register('description', {
                required: 'Asset description is required',
                minLength: { value: 5, message: 'Description must be at least 5 characters' },
              })}
              className={`input-glass resize-none ${errors.description ? 'border-red-500/50' : ''}`}
            />
            {errors.description && (
              <p className="text-sm text-red-500 font-medium">{errors.description.message}</p>
            )}
          </div>

          {/* Asset Type, Criticality, Environment */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                🖥️ Asset Type
              </Label>
              <Select
                value={selectedAssetType}
                onValueChange={(value) => setValue('asset_type', value)}
              >
                <SelectTrigger className="input-glass h-11">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent className="glass border-0">
                  {assetTypeOptions.map((type) => (
                    <SelectItem key={type.value} value={type.value} className="hover:bg-primary/10">
                      <div className="flex items-center gap-2">
                        <Badge variant={type.color} className="text-xs">
                          {type.label}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedAssetTypeInfo && (
                <Badge variant={selectedAssetTypeInfo.color} className="text-xs">
                  {selectedAssetTypeInfo.label}
                </Badge>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-semibold text-foreground/90">⚡ Criticality</Label>
              <Select
                value={selectedCriticality}
                onValueChange={(value) => setValue('criticality', value)}
              >
                <SelectTrigger className="input-glass h-11">
                  <SelectValue placeholder="Select criticality" />
                </SelectTrigger>
                <SelectContent className="glass border-0">
                  {criticalityOptions.map((crit) => (
                    <SelectItem key={crit.value} value={crit.value} className="hover:bg-primary/10">
                      <div className="flex items-center gap-2">
                        <Badge variant={crit.color} className="text-xs">
                          {crit.label}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedCriticalityInfo && (
                <Badge variant={selectedCriticalityInfo.color} className="text-xs">
                  {selectedCriticalityInfo.label}
                </Badge>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-semibold text-foreground/90">🌐 Environment</Label>
              <Select
                value={selectedEnvironment}
                onValueChange={(value) => setValue('environment', value)}
              >
                <SelectTrigger className="input-glass h-11">
                  <SelectValue placeholder="Select environment" />
                </SelectTrigger>
                <SelectContent className="glass border-0">
                  {environmentOptions.map((env) => (
                    <SelectItem key={env.value} value={env.value} className="hover:bg-primary/10">
                      <div className="flex items-center gap-2">
                        <Badge variant={env.color} className="text-xs">
                          {env.label}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedEnvironmentInfo && (
                <Badge variant={selectedEnvironmentInfo.color} className="text-xs">
                  {selectedEnvironmentInfo.label}
                </Badge>
              )}
            </div>
          </div>

          {/* Technical Details - Glass Section */}
          <div className="space-y-4 p-6 glass rounded-xl">
            <h3 className="font-semibold text-lg bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">🔧 Technical Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ip_address" className="text-sm font-medium text-foreground/90">
                  🌐 IP Address
                </Label>
                <Input
                  id="ip_address"
                  placeholder="192.168.1.100"
                  {...register('ip_address')}
                  className="input-glass h-11"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="hostname" className="text-sm font-medium text-foreground/90">
                  💻 Hostname
                </Label>
                <Input
                  id="hostname"
                  placeholder="server01.company.com"
                  {...register('hostname')}
                  className="input-glass h-11"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="operating_system" className="text-sm font-medium text-foreground/90">
                  🖥️ Operating System
                </Label>
                <Input
                  id="operating_system"
                  placeholder="Ubuntu 22.04 LTS"
                  {...register('operating_system')}
                  className="input-glass h-11"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location" className="text-sm font-medium text-foreground/90 flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  📍 Location
                </Label>
                <Input
                  id="location"
                  placeholder="Data Center A, Rack 12"
                  {...register('location')}
                  className="input-glass h-11"
                />
              </div>
            </div>
          </div>

          {/* Business Information - Glass Input */}
          <div className="space-y-3">
            <Label htmlFor="business_unit" className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <Building className="h-4 w-4" />
              🏢 Business Unit
            </Label>
            <Input
              id="business_unit"
              placeholder="IT Department, Finance, etc."
              {...register('business_unit')}
              className="input-glass h-12 text-base"
            />
          </div>

          {/* Error Message - Glass Style */}
          {error && (
            <div className="glass border-red-200/50 bg-red-50/80 p-4 rounded-xl flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-sm text-red-800 font-medium">{error}</p>
            </div>
          )}

          {/* Actions - Gradient Buttons */}
          <DialogFooter className="flex justify-end space-x-3 pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
              className="glass border-primary/20 hover:border-primary/40 px-6 h-11"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="btn-gradient-primary px-8 h-11 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Asset
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}