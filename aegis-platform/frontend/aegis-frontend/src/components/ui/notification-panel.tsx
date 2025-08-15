import React, { useState } from 'react';
import { Bell, X, Check, CheckCheck, Trash2, Filter, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Notification, NotificationType, NotificationPriority } from '@/types/notifications';
import { useNotifications } from '@/hooks/useNotifications';
import { cn } from '@/lib/utils';

interface NotificationPanelProps {
  className?: string;
}

const getNotificationIcon = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'error':
      return <XCircle className="h-4 w-4 text-red-500" />;
    case 'warning':
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    case 'info':
    default:
      return <Info className="h-4 w-4 text-blue-500" />;
  }
};

const getPriorityColor = (priority: NotificationPriority) => {
  switch (priority) {
    case 'critical':
      return 'border-l-red-500 bg-red-50 dark:bg-red-950';
    case 'high':
      return 'border-l-orange-500 bg-orange-50 dark:bg-orange-950';
    case 'medium':
      return 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-950';
    case 'low':
    default:
      return 'border-l-blue-500 bg-blue-50 dark:bg-blue-950';
  }
};

const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return `${Math.floor(diff / 86400000)}d ago`;
};

export const NotificationPanel: React.FC<NotificationPanelProps> = ({ className }) => {
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    clearAll,
  } = useNotifications();

  const [filterType, setFilterType] = useState<NotificationType | 'all'>('all');
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);

  const filteredNotifications = notifications.filter(notification => {
    if (filterType !== 'all' && notification.type !== filterType) return false;
    if (showUnreadOnly && notification.isRead) return false;
    return true;
  });

  return (
    <div className={cn("w-80 border-l bg-background", className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          <h2 className="font-semibold">Notifications</h2>
          {unreadCount > 0 && (
            <Badge variant="secondary" className="ml-2">
              {unreadCount}
            </Badge>
          )}
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <Filter className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={() => setFilterType('all')}
              className={filterType === 'all' ? 'bg-accent' : ''}
            >
              All Types
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => setFilterType('info')}
              className={filterType === 'info' ? 'bg-accent' : ''}
            >
              <Info className="h-4 w-4 mr-2" />
              Info
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => setFilterType('success')}
              className={filterType === 'success' ? 'bg-accent' : ''}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Success
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => setFilterType('warning')}
              className={filterType === 'warning' ? 'bg-accent' : ''}
            >
              <AlertTriangle className="h-4 w-4 mr-2" />
              Warning
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => setFilterType('error')}
              className={filterType === 'error' ? 'bg-accent' : ''}
            >
              <XCircle className="h-4 w-4 mr-2" />
              Error
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => setShowUnreadOnly(!showUnreadOnly)}
              className={showUnreadOnly ? 'bg-accent' : ''}
            >
              {showUnreadOnly ? 'Show All' : 'Unread Only'}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 p-2 border-b">
        <Button
          variant="ghost"
          size="sm"
          onClick={markAllAsRead}
          disabled={unreadCount === 0}
          className="flex-1"
        >
          <CheckCheck className="h-4 w-4 mr-2" />
          Mark All Read
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={clearAll}
          disabled={notifications.length === 0}
          className="flex-1"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Clear All
        </Button>
      </div>

      {/* Notifications List */}
      <ScrollArea className="flex-1 h-[500px]">
        {filteredNotifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
            <Bell className="h-12 w-12 mb-4 opacity-50" />
            <p className="text-sm">
              {showUnreadOnly ? 'No unread notifications' : 'No notifications'}
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={cn(
                  "group relative p-3 rounded-lg border-l-4 transition-colors hover:bg-accent/50 cursor-pointer",
                  getPriorityColor(notification.priority),
                  !notification.isRead && "ring-1 ring-primary/20"
                )}
                onClick={() => markAsRead(notification.id)}
              >
                <div className="flex items-start gap-3">
                  {getNotificationIcon(notification.type)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-medium truncate">
                        {notification.title}
                      </h4>
                      {!notification.isRead && (
                        <div className="w-2 h-2 bg-primary rounded-full" />
                      )}
                    </div>
                    {notification.message && (
                      <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                        {notification.message}
                      </p>
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        {formatTime(notification.createdAt)}
                      </span>
                      {notification.category && (
                        <Badge variant="outline" className="text-xs">
                          {notification.category}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => {
                      e.stopPropagation();
                      dismissNotification(notification.id);
                    }}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};