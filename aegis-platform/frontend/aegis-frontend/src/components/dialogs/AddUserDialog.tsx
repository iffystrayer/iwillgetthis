import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Plus, User, Mail, Key, Shield, AlertCircle } from 'lucide-react';

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
      
      // Create user through API
      await usersApi.create(data);
      
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
      <DialogContent className="sm:max-w-[500px] form-glass border-0">
        <DialogHeader className="text-center space-y-3">
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center justify-center gap-3">
            <User className="h-6 w-6 text-indigo-600" />
            ✨ Add New User
          </DialogTitle>
          <DialogDescription className="text-muted-foreground/80">
            Create a new user account with appropriate roles and permissions using our secure platform
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Full Name - Glass Input */}
          <div className="space-y-3">
            <Label htmlFor="full_name" className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <User className="h-4 w-4" />
              👤 Full Name *
            </Label>
            <Input
              id="full_name"
              placeholder="Enter full name"
              {...register('full_name', {
                required: 'Full name is required',
                minLength: { value: 2, message: 'Name must be at least 2 characters' },
              })}
              className={`input-glass h-12 text-base ${errors.full_name ? 'border-red-500/50' : ''}`}
            />
            {errors.full_name && (
              <p className="text-sm text-red-500 font-medium">{errors.full_name.message}</p>
            )}
          </div>

          {/* Email - Glass Input */}
          <div className="space-y-3">
            <Label htmlFor="email" className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <Mail className="h-4 w-4" />
              📧 Email Address *
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
              className={`input-glass h-12 text-base ${errors.email ? 'border-red-500/50' : ''}`}
            />
            {errors.email && (
              <p className="text-sm text-red-500 font-medium">{errors.email.message}</p>
            )}
          </div>

          {/* Username - Glass Input */}
          <div className="space-y-3">
            <Label htmlFor="username" className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <User className="h-4 w-4" />
              🔤 Username *
            </Label>
            <Input
              id="username"
              placeholder="Auto-generated from email"
              {...register('username', {
                required: 'Username is required',
                minLength: { value: 3, message: 'Username must be at least 3 characters' },
              })}
              className={`input-glass h-12 text-base ${errors.username ? 'border-red-500/50' : ''}`}
            />
            {errors.username && (
              <p className="text-sm text-red-500 font-medium">{errors.username.message}</p>
            )}
          </div>

          {/* Password - Glass Input */}
          <div className="space-y-3">
            <Label htmlFor="password" className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <Key className="h-4 w-4" />
              🔐 Temporary Password *
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter temporary password"
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 8, message: 'Password must be at least 8 characters' },
              })}
              className={`input-glass h-12 text-base ${errors.password ? 'border-red-500/50' : ''}`}
            />
            {errors.password && (
              <p className="text-sm text-red-500 font-medium">{errors.password.message}</p>
            )}
            <p className="text-xs text-muted-foreground/70">
              User will be prompted to change password on first login
            </p>
          </div>

          {/* Role Selection - Glass Select */}
          <div className="space-y-3">
            <Label className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
              <Shield className="h-4 w-4" />
              🛡️ Role & Permissions *
            </Label>
            <Select
              value={selectedRole}
              onValueChange={(value) => setValue('role', value)}
            >
              <SelectTrigger className="input-glass h-12">
                <SelectValue placeholder="Select user role" />
              </SelectTrigger>
              <SelectContent className="glass border-0">
                {roleOptions.map((role) => (
                  <SelectItem key={role.value} value={role.value} className="hover:bg-primary/10">
                    <div className="flex items-center gap-2">
                      <Badge variant={role.color} className="text-xs">
                        {role.label}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {role.description}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedRoleInfo && (
              <div className="flex items-center gap-2 p-3 glass rounded-lg">
                <Badge variant={selectedRoleInfo.color}>
                  {selectedRoleInfo.label}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {selectedRoleInfo.description}
                </span>
              </div>
            )}
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