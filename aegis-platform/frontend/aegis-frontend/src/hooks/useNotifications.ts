import { useState, useEffect, useCallback } from 'react';
import { Notification, NotificationType, NotificationPriority } from '@/types/notifications';
import { webSocketService } from '@/lib/websocket';
import { toast } from 'sonner';

export interface NotificationContextValue {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  dismissNotification: (id: string) => void;
  clearAll: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'isRead' | 'timestamp' | 'status'>) => void;
}

export const useNotifications = (): NotificationContextValue => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Add notification helper
  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'createdAt' | 'isRead' | 'timestamp' | 'status'>) => {
    const now = new Date().toISOString();
    const notification: Notification = {
      ...notificationData,
      id: crypto.randomUUID(),
      timestamp: now,
      createdAt: now,
      isRead: false,
      status: 'unread' as const,
    };

    setNotifications(prev => [notification, ...prev]);

    // Show toast based on priority and type
    const toastMessage = notification.title + (notification.message ? `: ${notification.message}` : '');
    
    switch (notification.priority) {
      case 'critical':
        toast.error(toastMessage, {
          duration: 0, // Never auto-dismiss critical notifications
          action: {
            label: 'Dismiss',
            onClick: () => {},
          },
        });
        break;
      case 'high':
        toast.error(toastMessage, { duration: 10000 });
        break;
      case 'medium':
        if (notification.type === 'success') {
          toast.success(toastMessage, { duration: 5000 });
        } else if (notification.type === 'warning') {
          toast.warning(toastMessage, { duration: 7000 });
        } else {
          toast.info(toastMessage, { duration: 5000 });
        }
        break;
      case 'low':
        toast.info(toastMessage, { duration: 3000 });
        break;
    }

    return notification.id;
  }, []);

  // Handle WebSocket notifications
  useEffect(() => {
    const unsubscribe = webSocketService.subscribe('notification', (data) => {
      if (data && typeof data === 'object') {
        addNotification(data);
      }
    });

    // Handle bulk operation updates
    const unsubscribeBulk = webSocketService.subscribe('bulk_operation', (data) => {
      if (data && data.progress !== undefined) {
        addNotification({
          type: 'info',
          title: 'Bulk Operation Progress',
          message: `${data.operation}: ${data.progress}% complete`,
          priority: 'low',
          category: 'system',
          metadata: data,
        });
      }
    });

    // Handle system status updates
    const unsubscribeSystem = webSocketService.subscribe('system_status', (data) => {
      if (data && data.type && data.type !== 'ping') {
        addNotification({
          type: data.level === 'error' ? 'error' : 'info',
          title: 'System Status',
          message: data.message || 'System status update',
          priority: data.level === 'error' ? 'high' : 'low',
          category: 'system',
          metadata: data,
        });
      }
    });

    // Handle WebSocket errors
    const unsubscribeError = webSocketService.subscribe('error', (data) => {
      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: data.error || 'WebSocket connection issue',
        priority: 'medium',
        category: 'system',
        metadata: data,
      });
    });

    return () => {
      unsubscribe();
      unsubscribeBulk();
      unsubscribeSystem();
      unsubscribeError();
    };
  }, [addNotification]);

  // Mark notification as read
  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id
          ? { ...notification, isRead: true }
          : notification
      )
    );
  }, []);

  // Mark all notifications as read
  const markAllAsRead = useCallback(() => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, isRead: true }))
    );
  }, []);

  // Dismiss notification
  const dismissNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // Clear all notifications
  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  // Calculate unread count
  const unreadCount = notifications.filter(n => !n.isRead).length;

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    clearAll,
    addNotification,
  };
};