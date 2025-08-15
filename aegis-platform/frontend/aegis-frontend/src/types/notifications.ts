// Notification types and interfaces for the Aegis platform

export type NotificationType = 
  // UI notification types - REQUIRED for toast notifications and UI components
  | 'success'              // Success messages
  | 'error'                // Error messages  
  | 'warning'              // Warning messages
  | 'info'                 // Informational messages
  // Domain-specific notification types
  | 'risk_alert'           // High/Critical risk findings
  | 'task_reminder'        // Task due dates and overdue items
  | 'assessment_complete'  // Assessment completion
  | 'system_update'        // System maintenance, updates
  | 'user_action'          // User invitations, role changes
  | 'asset_change'         // Asset status changes
  | 'compliance_alert'     // Compliance violations or issues
  | 'bulk_operation'       // Bulk operation completion/failure
  | 'ai_analysis'          // AI-powered analysis results
  | 'security_incident';   // Security incidents or breaches

export type NotificationPriority = 'low' | 'medium' | 'high' | 'critical';

export type NotificationStatus = 'unread' | 'read' | 'archived';

export interface Notification {
  id: string;
  type: NotificationType;
  priority: NotificationPriority;
  status: NotificationStatus;
  title: string;
  message?: string;
  timestamp: string;
  createdAt: string;
  isRead: boolean;
  userId?: string;
  category?: string;
  metadata?: {
    resourceId?: string | number;
    resourceType?: 'asset' | 'risk' | 'task' | 'user' | 'assessment';
    actionUrl?: string;
    actionLabel?: string;
    [key: string]: any;
  };
  expiresAt?: string;
  persistent?: boolean; // Whether notification should persist in history
}

export interface NotificationPreferences {
  userId: string;
  emailNotifications: boolean;
  pushNotifications: boolean;
  inAppNotifications: boolean;
  notificationTypes: {
    [K in NotificationType]: {
      enabled: boolean;
      emailEnabled: boolean;
      pushEnabled: boolean;
      minimumPriority: NotificationPriority;
    };
  };
  quietHours?: {
    enabled: boolean;
    startTime: string; // HH:MM format
    endTime: string;
  };
}

export interface NotificationUpdate {
  type: 'new_notification' | 'update_notification' | 'delete_notification';
  notification: Notification;
  timestamp: string;
}

// WebSocket message types for real-time communication
export interface WebSocketMessage {
  type: 'notification_update' | 'bulk_operation_progress' | 'system_status' | 'user_activity';
  payload: any;
  timestamp: string;
}

// Notification context for bulk operations integration
export interface BulkOperationNotification extends Omit<Notification, 'type'> {
  type: 'bulk_operation';
  metadata: {
    operationType: string;
    totalItems: number;
    completedItems: number;
    failedItems: number;
    operationId: string;
  };
}