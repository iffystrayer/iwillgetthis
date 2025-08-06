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
import { Badge } from '@/components/ui/badge';
import { Loader2, X, Plus, Mail } from 'lucide-react';
import { usersApi } from '@/lib/api';

interface InviteUsersDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUsersInvited?: () => void;
}

const roles = [
  { value: 'Admin', label: 'Administrator' },
  { value: 'Analyst', label: 'Security Analyst' },
  { value: 'ReadOnly', label: 'Read Only' },
];

export function InviteUsersDialog({
  open,
  onOpenChange,
  onUsersInvited,
}: InviteUsersDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emailInput, setEmailInput] = useState('');
  const [emails, setEmails] = useState<string[]>([]);
  const [selectedRole, setSelectedRole] = useState('');
  const [message, setMessage] = useState('');

  const handleClose = () => {
    setEmailInput('');
    setEmails([]);
    setSelectedRole('');
    setMessage('');
    setError(null);
    onOpenChange(false);
  };

  const addEmail = () => {
    const trimmedEmail = emailInput.trim();
    if (trimmedEmail && isValidEmail(trimmedEmail) && !emails.includes(trimmedEmail)) {
      setEmails([...emails, trimmedEmail]);
      setEmailInput('');
    }
  };

  const removeEmail = (emailToRemove: string) => {
    setEmails(emails.filter(email => email !== emailToRemove));
  };

  const isValidEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addEmail();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (emails.length === 0) {
      setError('At least one email address is required');
      return;
    }
    
    if (!selectedRole) {
      setError('Role selection is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const inviteData = {
        emails,
        role: selectedRole,
        message: message.trim() || 'You have been invited to join the Aegis Risk Management Platform.',
        sent_date: new Date().toISOString(),
      };

      console.log('Sending invitations with data:', inviteData);
      
      // For each email, create an invitation
      const invitePromises = emails.map(email => 
        usersApi.create({
          email,
          role: selectedRole,
          status: 'Invited',
          full_name: '', // Will be filled when they accept
          username: email.split('@')[0], // Generate username from email
          invitation_sent: true,
          invitation_message: message,
        })
      );

      await Promise.all(invitePromises);
      
      console.log('✅ Invitations sent successfully');
      
      if (onUsersInvited) {
        onUsersInvited();
      }
      
      handleClose();
    } catch (err: any) {
      console.error('❌ Failed to send invitations:', err);
      setError(err.response?.data?.message || err.message || 'Failed to send invitations');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Invite Users
          </DialogTitle>
          <DialogDescription>
            Send invitations to new users to join the Aegis Risk Management Platform.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email-input">Email Addresses *</Label>
              <div className="flex gap-2">
                <Input
                  id="email-input"
                  type="email"
                  placeholder="Enter email address and press Enter"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1"
                />
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={addEmail}
                  disabled={!emailInput.trim() || !isValidEmail(emailInput.trim())}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Type email addresses and press Enter or comma to add them
              </p>
              
              {emails.length > 0 && (
                <div className="flex flex-wrap gap-2 p-3 border rounded-md bg-muted/20">
                  {emails.map((email) => (
                    <Badge key={email} variant="secondary" className="gap-1">
                      {email}
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-auto p-0 hover:bg-transparent"
                        onClick={() => removeEmail(email)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Default Role *</Label>
              <Select 
                value={selectedRole} 
                onValueChange={setSelectedRole}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select default role for invited users" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => (
                    <SelectItem key={role.value} value={role.value}>
                      {role.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                All invited users will be assigned this role initially
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">Custom Message (Optional)</Label>
              <Textarea
                id="message"
                placeholder="Add a personal message to the invitation email..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                This message will be included in the invitation email
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <div className="flex items-start gap-2">
                <Mail className="h-4 w-4 text-blue-600 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-blue-900">Invitation Process</p>
                  <p className="text-blue-700 mt-1">
                    Invited users will receive an email with instructions to set up their account. 
                    They will appear in the users list with "Invited" status until they complete registration.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || emails.length === 0}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Send {emails.length > 0 ? `${emails.length} ` : ''}Invitation{emails.length !== 1 ? 's' : ''}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}