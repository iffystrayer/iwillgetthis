import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Plus, User, Mail, Key, Shield } from 'lucide-react';

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
import { Badge } from '@/components/ui/badge';
import { usersApi } from '@/lib/api';

interface AddUserDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUserAdded?: () => void;
}

interface UserFormData {
  full_name: string;
  email: string;
  username: string;
  password: string;
  role: string;
  is_active: boolean;
}

export function AddUserDialog({ open, onOpenChange, onUserAdded }: AddUserDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<UserFormData>({
    defaultValues: {
      full_name: '',
      email: '',
      username: '',
      password: '',
      role: 'Read-Only User',
      is_active: true,
    },
  });

  const selectedRole = watch('role');

  const handleClose = () => {
    reset();
    setError(null);
    onOpenChange(false);
  };

  const onSubmit = async (data: UserFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      console.log('Creating user with data:', data);
      
      // For now, simulate API call with timeout
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // TODO: Replace with actual API call when backend is ready
      // await usersApi.create(data);
      
      console.log('✅ User created successfully:', data);
      
      // Show success and refresh parent component
      if (onUserAdded) {
        onUserAdded();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to create user:', err);
      setError(err.message || 'Failed to create user. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const generateUsername = (email: string) => {
    if (email) {
      const username = email.split('@')[0];
      setValue('username', username);
    }
  };

  const roleOptions = [
    { value: 'Admin', label: 'Admin', description: 'Full system access', color: 'destructive' as const },
    { value: 'Security Analyst', label: 'Security Analyst', description: 'Security operations', color: 'default' as const },
    { value: 'Risk Manager', label: 'Risk Manager', description: 'Risk management tasks', color: 'secondary' as const },
    { value: 'Compliance Officer', label: 'Compliance Officer', description: 'Compliance activities', color: 'outline' as const },
    { value: 'Read-Only User', label: 'Read-Only User', description: 'View only access', color: 'secondary' as const },
  ];

  const selectedRoleInfo = roleOptions.find(role => role.value === selectedRole);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Add New User
          </DialogTitle>
          <DialogDescription>
            Create a new user account with appropriate roles and permissions.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Full Name */}
          <div className="space-y-2">
            <Label htmlFor="full_name" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Full Name
            </Label>
            <Input
              id="full_name"
              placeholder="Enter full name"
              {...register('full_name', {
                required: 'Full name is required',
                minLength: { value: 2, message: 'Name must be at least 2 characters' },
              })}
              className={errors.full_name ? 'border-red-500' : ''}
            />
            {errors.full_name && (
              <p className="text-sm text-red-600">{errors.full_name.message}</p>
            )}
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email" className="flex items-center gap-2">
              <Mail className="h-4 w-4" />
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="user@company.com"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
                onChange: (e) => generateUsername(e.target.value),
              })}
              className={errors.email ? 'border-red-500' : ''}
            />
            {errors.email && (
              <p className="text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          {/* Username */}
          <div className="space-y-2">
            <Label htmlFor="username" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Username
            </Label>
            <Input
              id="username"
              placeholder="Auto-generated from email"
              {...register('username', {
                required: 'Username is required',
                minLength: { value: 3, message: 'Username must be at least 3 characters' },
              })}
              className={errors.username ? 'border-red-500' : ''}
            />
            {errors.username && (
              <p className="text-sm text-red-600">{errors.username.message}</p>
            )}
          </div>

          {/* Password */}
          <div className="space-y-2">
            <Label htmlFor="password" className="flex items-center gap-2">
              <Key className="h-4 w-4" />
              Temporary Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter temporary password"
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 8, message: 'Password must be at least 8 characters' },
              })}
              className={errors.password ? 'border-red-500' : ''}
            />
            {errors.password && (
              <p className="text-sm text-red-600">{errors.password.message}</p>
            )}
            <p className="text-xs text-gray-500">
              User will be prompted to change password on first login
            </p>
          </div>

          {/* Role Selection */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Role & Permissions
            </Label>
            <Select
              value={selectedRole}
              onValueChange={(value) => setValue('role', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select user role" />
              </SelectTrigger>
              <SelectContent>
                {roleOptions.map((role) => (
                  <SelectItem key={role.value} value={role.value}>
                    <div className="flex items-center gap-2">
                      <Badge variant={role.color} className="text-xs">
                        {role.label}
                      </Badge>
                      <span className="text-sm text-gray-600">
                        {role.description}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedRoleInfo && (
              <div className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                <Badge variant={selectedRoleInfo.color}>
                  {selectedRoleInfo.label}
                </Badge>
                <span className="text-sm text-gray-600">
                  {selectedRoleInfo.description}
                </span>
              </div>
            )}
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
                  Create User
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}