import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Server, AlertCircle, Loader2 } from 'lucide-react';
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
import { Checkbox } from '@/components/ui/checkbox';
import { assetsApi } from '@/lib/api';

interface EditAssetDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  asset: any | null;
  onAssetUpdated?: () => void;
}

interface AssetFormData {
  name: string;
  description: string;
  type: string;
  criticality: string;
  owner: string;
  location: string;
  ip_address: string;
  hostname: string;
  operating_system: string;
  business_unit: string;
  cost_center: string;
  data_classification: string;
  is_active: boolean;
  requires_encryption: boolean;
  internet_accessible: boolean;
}

const assetTypes = [
  'Server',
  'Database',
  'Network Device',
  'Workstation', 
  'Mobile Device',
  'IoT Device',
  'Cloud Service',
  'Web Application',
  'Software',
  'Data Store',
  'Other'
];

const criticalityLevels = [
  { value: 'Low', label: 'Low Impact', color: 'text-green-600' },
  { value: 'Medium', label: 'Medium Impact', color: 'text-yellow-600' },
  { value: 'High', label: 'High Impact', color: 'text-orange-600' },
  { value: 'Critical', label: 'Critical Impact', color: 'text-red-600' }
];

const dataClassifications = [
  'Public',
  'Internal',
  'Confidential',
  'Restricted'
];

export function EditAssetDialog({ open, onOpenChange, asset, onAssetUpdated }: EditAssetDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, reset, setValue, formState: { errors }, watch } = useForm<AssetFormData>();

  const selectedType = watch('type');
  const selectedCriticality = watch('criticality');
  const selectedClassification = watch('data_classification');

  useEffect(() => {
    if (asset && open) {
      setValue('name', asset.name || '');
      setValue('description', asset.description || '');
      setValue('type', asset.type || '');
      setValue('criticality', asset.criticality || 'Medium');
      setValue('owner', asset.owner || '');
      setValue('location', asset.location || '');
      setValue('ip_address', asset.ip_address || '');
      setValue('hostname', asset.hostname || '');
      setValue('operating_system', asset.operating_system || '');
      setValue('business_unit', asset.business_unit || '');
      setValue('cost_center', asset.cost_center || '');
      setValue('data_classification', asset.data_classification || 'Internal');
      setValue('is_active', asset.is_active !== false);
      setValue('requires_encryption', asset.requires_encryption === true);
      setValue('internet_accessible', asset.internet_accessible === true);
      setError(null);
    }
  }, [asset, open, setValue]);

  const handleClose = () => {
    reset();
    setError(null);
    onOpenChange(false);
  };

  const onSubmit = async (data: AssetFormData) => {
    if (!asset) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const updateData = {
        ...data,
        last_updated: new Date().toISOString(),
        updated_by: 'current_user' // TODO: Get from auth context
      };

      console.log('Updating asset with data:', updateData);
      await assetsApi.update(asset.id, updateData);
      
      console.log('✅ Asset updated successfully');
      
      if (onAssetUpdated) {
        onAssetUpdated();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to update asset:', err);
      setError(err.response?.data?.message || err.message || 'Failed to update asset');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!asset) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Edit Asset
          </DialogTitle>
          <DialogDescription>
            Update asset information and configuration details.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Basic Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Asset Name *</Label>
                <Input
                  id="name"
                  {...register('name', { required: 'Asset name is required' })}
                  placeholder="e.g., Web Server 01"
                />
                {errors.name && (
                  <p className="text-sm text-destructive">{errors.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="type">Asset Type *</Label>
                <Select
                  value={selectedType}
                  onValueChange={(value) => setValue('type', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select asset type" />
                  </SelectTrigger>
                  <SelectContent>
                    {assetTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.type && (
                  <p className="text-sm text-destructive">Asset type is required</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                {...register('description')}
                placeholder="Describe the asset's purpose and function"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="criticality">Business Criticality *</Label>
                <Select
                  value={selectedCriticality}
                  onValueChange={(value) => setValue('criticality', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select criticality" />
                  </SelectTrigger>
                  <SelectContent>
                    {criticalityLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        <div className="flex items-center gap-2">
                          <span className={`font-medium ${level.color}`}>
                            {level.label}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.criticality && (
                  <p className="text-sm text-destructive">Criticality is required</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="data_classification">Data Classification *</Label>
                <Select
                  value={selectedClassification}
                  onValueChange={(value) => setValue('data_classification', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select classification" />
                  </SelectTrigger>
                  <SelectContent>
                    {dataClassifications.map((classification) => (
                      <SelectItem key={classification} value={classification}>
                        {classification}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.data_classification && (
                  <p className="text-sm text-destructive">Data classification is required</p>
                )}
              </div>
            </div>
          </div>

          {/* Technical Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Technical Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ip_address">IP Address</Label>
                <Input
                  id="ip_address"
                  {...register('ip_address', {
                    pattern: {
                      value: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
                      message: 'Please enter a valid IP address'
                    }
                  })}
                  placeholder="192.168.1.100"
                />
                {errors.ip_address && (
                  <p className="text-sm text-destructive">{errors.ip_address.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="hostname">Hostname</Label>
                <Input
                  id="hostname"
                  {...register('hostname')}
                  placeholder="server01.company.com"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="operating_system">Operating System</Label>
              <Input
                id="operating_system"
                {...register('operating_system')}
                placeholder="e.g., Ubuntu 22.04, Windows Server 2019"
              />
            </div>
          </div>

          {/* Organizational Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Organizational Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="owner">Asset Owner</Label>
                <Input
                  id="owner"
                  {...register('owner')}
                  placeholder="IT Department"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  {...register('location')}
                  placeholder="Data Center - Rack A1"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="business_unit">Business Unit</Label>
                <Input
                  id="business_unit"
                  {...register('business_unit')}
                  placeholder="Information Technology"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cost_center">Cost Center</Label>
                <Input
                  id="cost_center"
                  {...register('cost_center')}
                  placeholder="CC-IT-001"
                />
              </div>
            </div>
          </div>

          {/* Configuration Flags */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Configuration</h3>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_active"
                  {...register('is_active')}
                  defaultChecked={asset.is_active !== false}
                  onCheckedChange={(checked) => setValue('is_active', checked === true)}
                />
                <Label htmlFor="is_active" className="text-sm">
                  Asset is active and in use
                </Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="requires_encryption"
                  {...register('requires_encryption')}
                  defaultChecked={asset.requires_encryption === true}
                  onCheckedChange={(checked) => setValue('requires_encryption', checked === true)}
                />
                <Label htmlFor="requires_encryption" className="text-sm">
                  Requires data encryption
                </Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="internet_accessible"
                  {...register('internet_accessible')}
                  defaultChecked={asset.internet_accessible === true}
                  onCheckedChange={(checked) => setValue('internet_accessible', checked === true)}
                />
                <Label htmlFor="internet_accessible" className="text-sm">
                  Accessible from internet
                </Label>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Update Asset
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}