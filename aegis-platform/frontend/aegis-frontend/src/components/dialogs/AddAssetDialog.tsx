import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Plus, Database, Building, MapPin, Cpu } from 'lucide-react';

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
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Add New Asset
          </DialogTitle>
          <DialogDescription>
            Register a new asset in the asset management system with detailed information.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Asset Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              Asset Name
            </Label>
            <Input
              id="name"
              placeholder="Enter asset name"
              {...register('name', {
                required: 'Asset name is required',
                minLength: { value: 2, message: 'Name must be at least 2 characters' },
              })}
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && (
              <p className="text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">
              Description
            </Label>
            <Textarea
              id="description"
              placeholder="Describe the asset's purpose and characteristics"
              rows={3}
              {...register('description', {
                required: 'Asset description is required',
                minLength: { value: 5, message: 'Description must be at least 5 characters' },
              })}
              className={errors.description ? 'border-red-500' : ''}
            />
            {errors.description && (
              <p className="text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          {/* Asset Type, Criticality, Environment */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                Asset Type
              </Label>
              <Select
                value={selectedAssetType}
                onValueChange={(value) => setValue('asset_type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  {assetTypeOptions.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
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
              <Label>Criticality</Label>
              <Select
                value={selectedCriticality}
                onValueChange={(value) => setValue('criticality', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select criticality" />
                </SelectTrigger>
                <SelectContent>
                  {criticalityOptions.map((crit) => (
                    <SelectItem key={crit.value} value={crit.value}>
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
              <Label>Environment</Label>
              <Select
                value={selectedEnvironment}
                onValueChange={(value) => setValue('environment', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select environment" />
                </SelectTrigger>
                <SelectContent>
                  {environmentOptions.map((env) => (
                    <SelectItem key={env.value} value={env.value}>
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

          {/* Technical Details */}
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium">Technical Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ip_address">
                  IP Address
                </Label>
                <Input
                  id="ip_address"
                  placeholder="192.168.1.100"
                  {...register('ip_address')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="hostname">
                  Hostname
                </Label>
                <Input
                  id="hostname"
                  placeholder="server01.company.com"
                  {...register('hostname')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="operating_system">
                  Operating System
                </Label>
                <Input
                  id="operating_system"
                  placeholder="Ubuntu 22.04 LTS"
                  {...register('operating_system')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location" className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Location
                </Label>
                <Input
                  id="location"
                  placeholder="Data Center A, Rack 12"
                  {...register('location')}
                />
              </div>
            </div>
          </div>

          {/* Business Information */}
          <div className="space-y-2">
            <Label htmlFor="business_unit" className="flex items-center gap-2">
              <Building className="h-4 w-4" />
              Business Unit
            </Label>
            <Input
              id="business_unit"
              placeholder="IT Department, Finance, etc."
              {...register('business_unit')}
            />
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