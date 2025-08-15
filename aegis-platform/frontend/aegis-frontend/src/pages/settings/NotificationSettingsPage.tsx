import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';

interface NotificationPreference {
  id?: string;
  notification_type: string;
  is_enabled: boolean;
  delivery_method: string;
  frequency: string;
}

interface NotificationCategory {
  name: string;
  description: string;
  types: {
    type: string;
    label: string;
    description: string;
  }[];
}

const notificationCategories: NotificationCategory[] = [
  {
    name: 'Security',
    description: 'Critical security alerts and notifications',
    types: [
      { type: 'new_risk_detected', label: 'New Risk Detected', description: 'Alert when new security risks are identified' },
      { type: 'risk_assessment_due', label: 'Risk Assessment Due', description: 'Reminder for pending risk assessments' },
      { type: 'security_incident', label: 'Security Incidents', description: 'Immediate alerts for security incidents' },
    ]
  },
  {
    name: 'Tasks',
    description: 'Task and workflow notifications',
    types: [
      { type: 'task_assigned', label: 'Task Assigned', description: 'Notification when tasks are assigned to you' },
      { type: 'task_due_soon', label: 'Task Due Soon', description: 'Reminder for tasks due within 24 hours' },
      { type: 'task_overdue', label: 'Task Overdue', description: 'Alert for overdue tasks' },
    ]
  },
  {
    name: 'System',
    description: 'System and platform notifications',
    types: [
      { type: 'system_maintenance', label: 'System Maintenance', description: 'Scheduled maintenance notifications' },
      { type: 'data_export_ready', label: 'Data Export Ready', description: 'Notification when exports are completed' },
      { type: 'bulk_operation_completed', label: 'Bulk Operations', description: 'Status updates for bulk operations' },
    ]
  },
  {
    name: 'Compliance',
    description: 'Compliance and audit notifications',
    types: [
      { type: 'compliance_check_failed', label: 'Compliance Issues', description: 'Alert for compliance violations' },
      { type: 'audit_scheduled', label: 'Audit Scheduled', description: 'Notification for scheduled audits' },
    ]
  }
];

const NotificationSettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<Record<string, NotificationPreference>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await api.get('/notifications/preferences');
      const prefs: Record<string, NotificationPreference> = {};
      
      response.data.forEach((pref: NotificationPreference) => {
        prefs[pref.notification_type] = pref;
      });
      
      setPreferences(prefs);
    } catch (error) {
      console.error('Failed to load notification preferences:', error);
      toast.error('Failed to load notification preferences');
    } finally {
      setLoading(false);
    }
  };

  const updatePreference = async (type: string, updates: Partial<NotificationPreference>) => {
    try {
      setSaving(true);
      const existing = preferences[type];
      
      if (existing?.id) {
        // Update existing preference
        await api.put(`/notifications/preferences/${existing.id}`, updates);
      } else {
        // Create new preference
        await api.post('/notifications/preferences', {
          notification_type: type,
          is_enabled: true,
          delivery_method: 'email',
          frequency: 'immediate',
          ...updates
        });
      }
      
      setPreferences(prev => ({
        ...prev,
        [type]: {
          ...prev[type],
          notification_type: type,
          ...updates
        }
      }));
      
      toast.success('Notification preference updated');
    } catch (error) {
      console.error('Failed to update preference:', error);
      toast.error('Failed to update notification preference');
    } finally {
      setSaving(false);
    }
  };

  const getPreference = (type: string): NotificationPreference => {
    return preferences[type] || {
      notification_type: type,
      is_enabled: false,
      delivery_method: 'email',
      frequency: 'immediate'
    };
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Notification Settings</h1>
          <p className="text-muted-foreground">Configure your notification preferences</p>
        </div>
        <Badge variant="outline">{user?.email}</Badge>
      </div>

      <div className="space-y-6">
        {notificationCategories.map((category) => (
          <Card key={category.name}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {category.name}
                <Badge variant="secondary">{category.types.length}</Badge>
              </CardTitle>
              <CardDescription>{category.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {category.types.map((notificationType) => {
                const pref = getPreference(notificationType.type);
                
                return (
                  <div key={notificationType.type} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <Label htmlFor={notificationType.type} className="font-medium">
                          {notificationType.label}
                        </Label>
                        <Switch
                          id={notificationType.type}
                          checked={pref.is_enabled}
                          onCheckedChange={(checked) => 
                            updatePreference(notificationType.type, { is_enabled: checked })
                          }
                          disabled={saving}
                        />
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {notificationType.description}
                      </p>
                    </div>
                    
                    {pref.is_enabled && (
                      <div className="flex items-center gap-2 ml-4">
                        <Select
                          value={pref.delivery_method}
                          onValueChange={(value) => 
                            updatePreference(notificationType.type, { delivery_method: value })
                          }
                          disabled={saving}
                        >
                          <SelectTrigger className="w-28">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="email">Email</SelectItem>
                            <SelectItem value="in_app">In-App</SelectItem>
                          </SelectContent>
                        </Select>
                        
                        <Select
                          value={pref.frequency}
                          onValueChange={(value) => 
                            updatePreference(notificationType.type, { frequency: value })
                          }
                          disabled={saving}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="immediate">Immediate</SelectItem>
                            <SelectItem value="daily">Daily</SelectItem>
                            <SelectItem value="weekly">Weekly</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </div>
                );
              })}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Global Settings</CardTitle>
          <CardDescription>
            Global notification settings that apply to all notification types
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Quiet Hours</Label>
              <p className="text-sm text-muted-foreground">
                Disable non-critical notifications during specified hours
              </p>
            </div>
            <Switch disabled />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Email Digest</Label>
              <p className="text-sm text-muted-foreground">
                Receive a daily summary of all notifications
              </p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NotificationSettingsPage;