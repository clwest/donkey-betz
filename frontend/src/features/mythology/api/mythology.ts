/**
 * Mythology API Service
 * API client for mythology review and content flagging system
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../services/api.config';
import { Logger } from '../../../utils/logger';

// Types
export interface FlaggedContent {
  id: number;
  content_type: string;
  content_id: number;
  flag_type: 'misinformation' | 'harmful' | 'inappropriate' | 'spam' | 'other';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'reviewing' | 'resolved' | 'dismissed';
  content_preview: string;
  reason: string;
  flagged_by: {
    id: number;
    username: string;
    email: string;
  };
  flagged_at: string;
  reviewed_by?: {
    id: number;
    username: string;
    email: string;
  };
  reviewed_at?: string;
  review_notes?: string;
  metadata?: Record<string, any>;
}

export interface ReviewAction {
  content_id: number;
  action: 'approve' | 'remove' | 'edit' | 'flag_false_positive';
  notes?: string;
  edit_content?: string;
}

export interface ReportContent {
  content_type: string;
  content_id: number;
  flag_type: string;
  reason: string;
  additional_info?: string;
}

export interface MythologyStats {
  total_flagged: number;
  pending_review: number;
  high_priority: number;
  resolved_today: number;
  false_positive_rate: number;
  avg_review_time: number;
}

export interface AlertNotification {
  id: number;
  type: 'new_flag' | 'high_priority' | 'urgent_review';
  title: string;
  message: string;
  content_id?: number;
  priority: string;
  created_at: string;
  read: boolean;
}

// API Query Keys
export const mythologyKeys = {
  all: ['mythology'] as const,
  stats: () => [...mythologyKeys.all, 'stats'] as const,
  flaggedContent: (filters?: any) => [...mythologyKeys.all, 'flagged', filters] as const,
  notifications: () => [...mythologyKeys.all, 'notifications'] as const,
  contentDetail: (id: number) => [...mythologyKeys.all, 'content', id] as const,
};

// API Functions
const mythologyAPI = {
  // Get mythology dashboard stats
  getStats: async (): Promise<MythologyStats> => {
    Logger.api('GET', '/api/v1/mythology/stats/', {});
    const response = await apiClient.get('/api/v1/mythology/stats/');
    return response.data;
  },

  // Get flagged content with filtering and pagination
  getFlaggedContent: async (params?: {
    status?: string;
    priority?: string;
    flag_type?: string;
    page?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<{
    results: FlaggedContent[];
    count: number;
    next?: string;
    previous?: string;
  }> => {
    Logger.api('GET', '/api/v1/mythology/flagged-content/', { params });
    const response = await apiClient.get('/api/v1/mythology/flagged-content/', { params });
    return response.data;
  },

  // Get specific flagged content details
  getFlaggedContentDetail: async (id: number): Promise<FlaggedContent> => {
    Logger.api('GET', `/api/v1/mythology/flagged-content/${id}/`, {});
    const response = await apiClient.get(`/api/v1/mythology/flagged-content/${id}/`);
    return response.data;
  },

  // Submit review action
  submitReview: async (data: ReviewAction): Promise<{ success: boolean; message: string }> => {
    Logger.api('POST', '/api/v1/mythology/review/', { data });
    const response = await apiClient.post('/api/v1/mythology/review/', data);
    return response.data;
  },

  // Report content for review
  reportContent: async (data: ReportContent): Promise<{ success: boolean; message: string; flag_id: number }> => {
    Logger.api('POST', '/api/v1/mythology/report/', { data });
    const response = await apiClient.post('/api/v1/mythology/report/', data);
    return response.data;
  },

  // Get notifications
  getNotifications: async (params?: {
    unread_only?: boolean;
    limit?: number;
  }): Promise<AlertNotification[]> => {
    Logger.api('GET', '/api/v1/mythology/notifications/', { params });
    const response = await apiClient.get('/api/v1/mythology/notifications/', { params });
    return response.data;
  },

  // Mark notification as read
  markNotificationRead: async (id: number): Promise<{ success: boolean }> => {
    Logger.api('PATCH', `/api/v1/mythology/notifications/${id}/read/`, {});
    const response = await apiClient.patch(`/api/v1/mythology/notifications/${id}/read/`);
    return response.data;
  },

  // Mark all notifications as read
  markAllNotificationsRead: async (): Promise<{ success: boolean }> => {
    Logger.api('POST', '/api/v1/mythology/notifications/mark-all-read/', {});
    const response = await apiClient.post('/api/v1/mythology/notifications/mark-all-read/');
    return response.data;
  },
};

// React Query Hooks
export const useMythologyStats = () => {
  return useQuery({
    queryKey: mythologyKeys.stats(),
    queryFn: mythologyAPI.getStats,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
  });
};

export const useFlaggedContent = (params?: Parameters<typeof mythologyAPI.getFlaggedContent>[0]) => {
  return useQuery({
    queryKey: mythologyKeys.flaggedContent(params),
    queryFn: () => mythologyAPI.getFlaggedContent(params),
    staleTime: 10 * 1000, // 10 seconds
  });
};

export const useFlaggedContentDetail = (id: number) => {
  return useQuery({
    queryKey: mythologyKeys.contentDetail(id),
    queryFn: () => mythologyAPI.getFlaggedContentDetail(id),
    enabled: !!id,
  });
};

export const useNotifications = (params?: Parameters<typeof mythologyAPI.getNotifications>[0]) => {
  return useQuery({
    queryKey: mythologyKeys.notifications(),
    queryFn: () => mythologyAPI.getNotifications(params),
    staleTime: 5 * 1000, // 5 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  });
};

export const useSubmitReview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: mythologyAPI.submitReview,
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: mythologyKeys.stats() });
      queryClient.invalidateQueries({ queryKey: mythologyKeys.flaggedContent() });
      Logger.component('Mythology Review', 'Review submitted successfully');
    },
    onError: (error) => {
      Logger.error('Mythology Review', 'Failed to submit review', error);
    },
  });
};

export const useReportContent = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: mythologyAPI.reportContent,
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: mythologyKeys.stats() });
      queryClient.invalidateQueries({ queryKey: mythologyKeys.flaggedContent() });
      Logger.component('Mythology Report', 'Content reported successfully');
    },
    onError: (error) => {
      Logger.error('Mythology Report', 'Failed to report content', error);
    },
  });
};

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: mythologyAPI.markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mythologyKeys.notifications() });
    },
  });
};

export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: mythologyAPI.markAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mythologyKeys.notifications() });
    },
  });
};

// WebSocket Hook for Real-time Notifications
export const useMythologyWebSocket = (onNewNotification?: (notification: AlertNotification) => void) => {
  const queryClient = useQueryClient();
  let reconnectTimeout: NodeJS.Timeout | null = null;
  let isConnecting = false;

  // WebSocket connection for real-time updates
  const connectWebSocket = () => {
    if (isConnecting) {
      return null; // Prevent multiple connections
    }
    
    isConnecting = true;
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/ws/mythology/`);

    ws.onopen = () => {
      isConnecting = false;
      Logger.component('Mythology WebSocket', 'Connected to real-time notifications');
      
      // Clear any pending reconnect timeout
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'mythology_notification') {
          const notification: AlertNotification = data.notification;
          
          // Update notifications query
          queryClient.invalidateQueries({ queryKey: mythologyKeys.notifications() });
          
          // Update stats if it's a new flag
          if (notification.type === 'new_flag') {
            queryClient.invalidateQueries({ queryKey: mythologyKeys.stats() });
          }
          
          // Call callback
          onNewNotification?.(notification);
          
          Logger.event('Mythology WebSocket', 'New notification received', notification);
        } else if (data.type === 'connection_established') {
          Logger.component('Mythology WebSocket', 'Connection established');
        }
      } catch (error) {
        Logger.error('Mythology WebSocket', 'Failed to parse message', error);
      }
    };

    ws.onclose = (event) => {
      isConnecting = false;
      
      // Only reconnect if it wasn't a manual close (code 1000) and not a connection failure
      if (event.code !== 1000 && event.code !== 1006 && !reconnectTimeout) {
        Logger.warn('Mythology WebSocket', 'Connection closed unexpectedly, attempting to reconnect in 5s');
        reconnectTimeout = setTimeout(() => {
          reconnectTimeout = null;
          connectWebSocket();
        }, 5000);
      } else {
        Logger.component('Mythology WebSocket', 'Connection closed or failed to connect - not reconnecting');
      }
    };

    ws.onerror = (error) => {
      isConnecting = false;
      Logger.error('Mythology WebSocket', 'Connection error - server may be down', error);
      // Don't attempt reconnection on initial connection errors
    };

    return ws;
  };

  return { connectWebSocket };
};

export default mythologyAPI;