import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { User, AlertCircle, Loader2 } from 'lucide-react';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { usersApi } from '@/lib/api';

interface EditUserDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user: any | null;
  onUserUpdated?: () => void;
}

interface UserFormData {
  full_name: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  reset_password: boolean;
  new_password?: string;
}

const roles = [
  { value: 'Admin', label: 'Admin - Full system access', description: 'Complete access to all features' },
  { value: 'Analyst', label: 'Security Analyst - Standard access', description: 'Can manage risks, assets, and evidence' },
  { value: 'ReadOnly', label: 'Read-Only User - View only access', description: 'Can view reports and data only' }
];

export function EditUserDialog({ open, onOpenChange, user, onUserUpdated }: EditUserDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resetPassword, setResetPassword] = useState(false);

  const { register, handleSubmit, reset, setValue, formState: { errors }, watch } = useForm<UserFormData>();

  const selectedRole = watch('role');

  useEffect(() => {
    if (user && open) {
      setValue('full_name', user.full_name || '');
      setValue('email', user.email || '');
      setValue('username', user.username || '');
      setValue('role', user.role || 'ReadOnly');
      setValue('is_active', user.is_active !== false);
      setValue('reset_password', false);
      setResetPassword(false);
      setError(null);
    }
  }, [user, open, setValue]);

  const handleClose = () => {
    reset();
    setResetPassword(false);
    setError(null);
    onOpenChange(false);
  };

  const onSubmit = async (data: UserFormData) => {
    if (!user) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const updateData: any = {
        full_name: data.full_name,
        email: data.email,
        username: data.username,
        role: data.role,
        is_active: data.is_active
      };

      if (resetPassword && data.new_password) {
        updateData.password = data.new_password;
        updateData.force_password_change = true;
      }

      console.log('Updating user with data:', updateData);
      await usersApi.update(user.id, updateData);
      
      console.log('✅ User updated successfully');
      
      if (onUserUpdated) {
        onUserUpdated();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to update user:', err);
      setError(err.response?.data?.message || err.message || 'Failed to update user');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!user) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Edit User Account
          </DialogTitle>
          <DialogDescription>
            Update user account details, role, and permissions.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name *</Label>
            <Input
              id="full_name"
              {...register('full_name', { required: 'Full name is required' })}
              placeholder="Enter full name"
            />
            {errors.full_name && (
              <p className="text-sm text-destructive">{errors.full_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email Address *</Label>
            <Input
              id="email"
              type="email"
              {...register('email', { 
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address'
                }
              })}
              placeholder="Enter email address"
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="username">Username *</Label>
            <Input
              id="username"
              {...register('username', { required: 'Username is required' })}
              placeholder="Enter username"
            />
            {errors.username && (
              <p className="text-sm text-destructive">{errors.username.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="role">Role & Permissions *</Label>
            <Select
              value={selectedRole}
              onValueChange={(value) => setValue('role', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select user role" />
              </SelectTrigger>
              <SelectContent>
                {roles.map((role) => (
                  <SelectItem key={role.value} value={role.value}>
                    <div className="flex flex-col">
                      <span className="font-medium">{role.label}</span>
                      <span className="text-sm text-muted-foreground">{role.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.role && (
              <p className="text-sm text-destructive">Role selection is required</p>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="is_active"
              {...register('is_active')}
              defaultChecked={user.is_active !== false}
              onCheckedChange={(checked) => setValue('is_active', checked === true)}
            />
            <Label htmlFor="is_active" className="text-sm">
              Account is active
            </Label>
          </div>

          <div className="border-t pt-4">
            <div className="flex items-center space-x-2 mb-3">
              <Checkbox
                id="reset_password"
                checked={resetPassword}
                onCheckedChange={(checked) => {
                  setResetPassword(checked === true);
                  setValue('reset_password', checked === true);
                }}
              />
              <Label htmlFor="reset_password" className="text-sm">
                Reset user password
              </Label>
            </div>
            
            {resetPassword && (
              <div className="space-y-2">
                <Label htmlFor="new_password">New Temporary Password *</Label>
                <Input
                  id="new_password"
                  type="password"
                  {...register('new_password', { 
                    required: resetPassword ? 'Password is required when resetting' : false,
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters'
                    }
                  })}
                  placeholder="Enter temporary password"
                />
                {errors.new_password && (
                  <p className="text-sm text-destructive">{errors.new_password.message}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  User will be prompted to change password on next login
                </p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Update User
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}