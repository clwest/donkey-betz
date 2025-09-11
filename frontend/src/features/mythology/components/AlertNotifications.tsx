/**
 * Alert Notifications Component
 * Real-time notifications for mythology review system with WebSocket integration
 */
import React, { useEffect, useState } from 'react';
import { Bell, X, AlertTriangle, Flag, Clock, Eye } from 'lucide-react';
import { format } from 'date-fns';

import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../../../components/ui/dropdown-menu';

import { 
  useNotifications, 
  useMarkNotificationRead, 
  useMarkAllNotificationsRead,
  type AlertNotification 
} from '../api/mythology';
import { cn } from '../../../lib/utils';

interface AlertNotificationsProps {
  onNotificationClick?: (contentId?: number) => void;
  compact?: boolean;
}

export const AlertNotifications: React.FC<AlertNotificationsProps> = ({ 
  onNotificationClick,
  compact = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [realtimeNotifications, setRealtimeNotifications] = useState<AlertNotification[]>([]);

  // API hooks
  const { data: notifications = [], refetch } = useNotifications({ unread_only: false, limit: 20 });
  const markReadMutation = useMarkNotificationRead();
  const markAllReadMutation = useMarkAllNotificationsRead();

  // Removed WebSocket connection from here since it's already handled in MythologyDashboard parent component
  // This prevents duplicate connections and reconnection issues
  
  // Parent component will refetch notifications when new ones arrive

  useEffect(() => {
    // Update unread count from API data
    const unread = notifications.filter(n => !n.read).length;
    setUnreadCount(unread);
  }, [notifications]);

  // Handle notification click
  const handleNotificationClick = async (notification: AlertNotification) => {
    if (!notification.read) {
      await markReadMutation.mutateAsync(notification.id);
    }
    
    if (notification.content_id) {
      onNotificationClick?.(notification.content_id);
    }
    
    setIsOpen(false);
  };

  // Handle mark all as read
  const handleMarkAllRead = async () => {
    await markAllReadMutation.mutateAsync();
    setUnreadCount(0);
    setRealtimeNotifications([]);
  };

  // Notification type configurations
  const notificationConfig = {
    new_flag: {
      icon: Flag,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50 border-orange-200',
      label: 'New Flag'
    },
    high_priority: {
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50 border-red-200',
      label: 'High Priority'
    },
    urgent_review: {
      icon: Clock,
      color: 'text-red-600',
      bgColor: 'bg-red-50 border-red-200',
      label: 'Urgent Review'
    },
  };

  // Render notification item
  const NotificationItem = ({ notification }: { notification: AlertNotification }) => {
    const config = notificationConfig[notification.type as keyof typeof notificationConfig];
    const Icon = config?.icon || Bell;
    
    return (
      <div
        className={cn(
          'p-3 border rounded-lg cursor-pointer transition-colors hover:bg-muted/50',
          !notification.read && 'bg-blue-50 border-blue-200',
          config?.bgColor && !notification.read && config.bgColor
        )}
        onClick={() => handleNotificationClick(notification)}
      >
        <div className="flex items-start space-x-3">
          <div className={cn('flex-shrink-0 mt-1', config?.color)}>
            <Icon className="h-4 w-4" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900 truncate">
                {notification.title}
              </p>
              {!notification.read && (
                <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 ml-2" />
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {notification.message}
            </p>
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-gray-400">
                {format(new Date(notification.created_at), 'MMM d, HH:mm')}
              </span>
              {config && (
                <Badge variant="outline" className="text-xs">
                  {config.label}
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (compact) {
    // Compact view - just show unread count
    return (
      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsOpen(!isOpen)}
          className="relative"
        >
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Real-time notifications banner */}
      {realtimeNotifications.length > 0 && (
        <Alert className="border-blue-200 bg-blue-50">
          <Bell className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            <div className="flex items-center justify-between">
              <span>
                {realtimeNotifications.length} new notification{realtimeNotifications.length > 1 ? 's' : ''} received
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setRealtimeNotifications([])}
                className="h-6 px-2 text-xs"
              >
                Dismiss
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Notifications dropdown */}
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="relative">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
            {unreadCount > 0 && (
              <Badge 
                variant="destructive" 
                className="ml-2 h-5 w-5 flex items-center justify-center p-0 text-xs"
              >
                {unreadCount > 99 ? '99+' : unreadCount}
              </Badge>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-96 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between p-3 border-b">
            <h3 className="font-semibold text-sm">Notifications</h3>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllRead}
                disabled={markAllReadMutation.isPending}
                className="h-6 px-2 text-xs"
              >
                Mark all read
              </Button>
            )}
          </div>
          
          {notifications.length === 0 ? (
            <div className="p-6 text-center text-muted-foreground">
              <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No notifications yet</p>
            </div>
          ) : (
            <div className="max-h-80 overflow-y-auto">
              {notifications.map((notification) => (
                <DropdownMenuItem
                  key={notification.id}
                  className="p-0 focus:bg-transparent"
                  onSelect={(e) => e.preventDefault()}
                >
                  <NotificationItem notification={notification} />
                </DropdownMenuItem>
              ))}
            </div>
          )}
          
          {notifications.length > 10 && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-center text-sm text-muted-foreground">
                <Eye className="h-4 w-4 mr-2" />
                View all notifications
              </DropdownMenuItem>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};