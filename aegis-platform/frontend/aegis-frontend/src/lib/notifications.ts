// Predefined notification types for common scenarios
import { Notification, NotificationType, NotificationPriority } from '@/types/notifications';

export interface NotificationTemplate {
  type: NotificationType;
  priority: NotificationPriority;
  category?: string;
  title: string;
  message?: string;
}

// System notification templates
export const SystemNotifications = {
  // Authentication & Security
  LOGIN_SUCCESS: {
    type: 'success' as const,
    priority: 'low' as const,
    status: 'unread' as const,
    category: 'security',
    title: 'Successfully logged in',
    message: 'Welcome back to Aegis Platform',
  },
  LOGIN_FAILED: {
    type: 'error' as const,
    priority: 'medium' as const,
    status: 'unread' as const,
    category: 'security',
    title: 'Login failed',
    message: 'Invalid credentials. Please try again.',
  },
  SESSION_EXPIRED: {
    type: 'warning' as const,
    priority: 'high' as const,
    status: 'unread' as const,
    category: 'security',
    title: 'Session expired',
    message: 'Your session has expired. Please log in again.',
  },
  UNAUTHORIZED_ACCESS: {
    type: 'error' as const,
    priority: 'critical' as const,
    status: 'unread' as const,
    category: 'security',
    title: 'Unauthorized access detected',
    message: 'Suspicious activity detected on your account.',
  },

  // Data Operations
  DATA_SAVED: {
    type: 'success' as const,
    priority: 'low' as const,
    status: 'unread' as const,
    category: 'data',
    title: 'Data saved successfully',
  },
  DATA_SAVE_FAILED: {
    type: 'error' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'data',
    title: 'Failed to save data',
    message: 'An error occurred while saving. Please try again.',
  },
  DATA_DELETED: {
    type: 'info' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'data',
    title: 'Data deleted',
  },
  DATA_IMPORTED: {
    type: 'success' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'data',
    title: 'Data imported successfully',
  },
  DATA_EXPORT_READY: {
    type: 'success' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'data',
    title: 'Export ready for download',
    message: 'Your data export has been completed.',
  },

  // Bulk Operations
  BULK_OPERATION_STARTED: {
    type: 'info' as NotificationType,
    priority: 'low' as NotificationPriority,
    category: 'bulk',
    title: 'Bulk operation started',
  },
  BULK_OPERATION_COMPLETED: {
    type: 'success' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'bulk',
    title: 'Bulk operation completed',
  },
  BULK_OPERATION_FAILED: {
    type: 'error' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'bulk',
    title: 'Bulk operation failed',
    message: 'Some items could not be processed.',
  },

  // System Status
  SYSTEM_MAINTENANCE: {
    type: 'warning' as NotificationType,
    priority: 'high' as NotificationPriority,
    category: 'system',
    title: 'Scheduled maintenance',
    message: 'System maintenance will begin shortly.',
  },
  SYSTEM_ERROR: {
    type: 'error' as NotificationType,
    priority: 'high' as NotificationPriority,
    category: 'system',
    title: 'System error',
    message: 'A system error has occurred. Please contact support.',
  },
  CONNECTION_LOST: {
    type: 'warning' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'system',
    title: 'Connection lost',
    message: 'Attempting to reconnect...',
  },
  CONNECTION_RESTORED: {
    type: 'success' as NotificationType,
    priority: 'low' as NotificationPriority,
    category: 'system',
    title: 'Connection restored',
    message: 'You are back online.',
  },

  // Risk Management
  NEW_RISK_DETECTED: {
    type: 'warning' as NotificationType,
    priority: 'high' as NotificationPriority,
    category: 'risk',
    title: 'New risk detected',
    message: 'A new risk has been identified and requires assessment.',
  },
  RISK_ASSESSMENT_DUE: {
    type: 'warning' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'risk',
    title: 'Risk assessment due',
    message: 'A risk assessment is due for review.',
  },
  RISK_MITIGATION_COMPLETED: {
    type: 'success' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'risk',
    title: 'Risk mitigation completed',
    message: 'Risk mitigation actions have been successfully completed.',
  },

  // Task Management
  TASK_ASSIGNED: {
    type: 'info' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'task',
    title: 'New task assigned',
    message: 'You have been assigned a new task.',
  },
  TASK_COMPLETED: {
    type: 'success' as NotificationType,
    priority: 'low' as NotificationPriority,
    category: 'task',
    title: 'Task completed',
  },
  TASK_OVERDUE: {
    type: 'error' as NotificationType,
    priority: 'high' as NotificationPriority,
    category: 'task',
    title: 'Task overdue',
    message: 'A task has passed its due date.',
  },
  TASK_DUE_SOON: {
    type: 'warning' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'task',
    title: 'Task due soon',
    message: 'A task is due within 24 hours.',
  },

  // AI & Analysis
  AI_ANALYSIS_STARTED: {
    type: 'info' as NotificationType,
    priority: 'low' as NotificationPriority,
    category: 'ai',
    title: 'AI analysis started',
    message: 'AI analysis is in progress...',
  },
  AI_ANALYSIS_COMPLETED: {
    type: 'success' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'ai',
    title: 'AI analysis completed',
    message: 'Analysis results are now available.',
  },
  AI_ANALYSIS_FAILED: {
    type: 'error' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'ai',
    title: 'AI analysis failed',
    message: 'Unable to complete AI analysis. Please try again.',
  },

  // Compliance & Audit
  COMPLIANCE_CHECK_PASSED: {
    type: 'success' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'compliance',
    title: 'Compliance check passed',
    message: 'All compliance requirements have been met.',
  },
  COMPLIANCE_CHECK_FAILED: {
    type: 'error' as NotificationType,
    priority: 'high' as NotificationPriority,
    category: 'compliance',
    title: 'Compliance check failed',
    message: 'Compliance issues have been identified.',
  },
  AUDIT_SCHEDULED: {
    type: 'info' as NotificationType,
    priority: 'medium' as NotificationPriority,
    category: 'compliance',
    title: 'Audit scheduled',
    message: 'A new audit has been scheduled.',
  },
} as const;

// Helper function to create notification from template
export const createNotificationFromTemplate = (
  template: NotificationTemplate,
  overrides?: Partial<Omit<Notification, 'id' | 'createdAt' | 'isRead' | 'timestamp' | 'status'>>
): Omit<Notification, 'id' | 'createdAt' | 'isRead' | 'timestamp' | 'status'> => {
  return {
    ...template,
    ...overrides,
  };
};

// Function to get notifications by category
export const getNotificationsByCategory = (category: string) => {
  return Object.entries(SystemNotifications)
    .filter(([_, template]) => template.category === category)
    .map(([key, template]) => ({ key, ...template }));
};

// Function to get high priority notifications
export const getHighPriorityNotifications = () => {
  return Object.entries(SystemNotifications)
    .filter(([_, template]) => template.priority === 'high' || template.priority === 'critical')
    .map(([key, template]) => ({ key, ...template }));
};