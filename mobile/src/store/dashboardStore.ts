import { create } from 'zustand';
import { dashboardService } from '../services/dashboardService';
import { DashboardStats, ActivityItem, ContentBreakdown } from '../types/api';

interface DashboardState {
  // Main Stats
  stats: DashboardStats | null;
  isLoadingStats: boolean;
  
  // Activity Feed
  activities: ActivityItem[];
  isLoadingActivities: boolean;
  
  // Content Breakdown
  contentBreakdown: ContentBreakdown | null;
  isLoadingBreakdown: boolean;
  
  // Analytics
  engagementMetrics: any | null;
  contentPerformance: any | null;
  usageStats: any | null;
  
  // Insights and Recommendations
  recommendations: any | null;
  productivityInsights: any | null;
  stylePreferences: any | null;
  
  // Goals and Progress
  goals: any | null;
  
  // Notifications
  notificationSettings: any | null;
  
  // Live Stats
  liveStats: any | null;
  
  // Error handling
  error: string | null;
  
  // Actions - Main Dashboard
  loadDashboardStats: () => Promise<void>;
  loadRecentActivity: (limit?: number) => Promise<void>;
  loadContentBreakdown: (timeframe?: string) => Promise<void>;
  refreshDashboard: () => Promise<void>;
  
  // Actions - Analytics
  loadEngagementMetrics: (period?: string) => Promise<void>;
  loadContentPerformance: () => Promise<void>;
  loadUsageStats: (timeframe?: string) => Promise<void>;
  
  // Actions - Insights
  loadRecommendations: () => Promise<void>;
  loadProductivityInsights: () => Promise<void>;
  loadStylePreferences: () => Promise<void>;
  
  // Actions - Goals
  loadGoals: () => Promise<void>;
  updateGoals: (goals: any) => Promise<void>;
  
  // Actions - Reports
  generateReport: (type: string, options?: any) => Promise<string>;
  checkReportStatus: (reportId: string) => Promise<any>;
  exportDashboardData: (format: string) => Promise<void>;
  
  // Actions - Notifications
  loadNotificationSettings: () => Promise<void>;
  updateNotificationSettings: (settings: any) => Promise<void>;
  
  // Actions - Live Data
  loadLiveStats: () => Promise<void>;
  startLiveUpdates: () => void;
  stopLiveUpdates: () => void;
  
  // Utility actions
  clearError: () => void;
}

export const useDashboardStore = create<DashboardState>((set, get) => {
  let liveUpdateInterval: NodeJS.Timeout | null = null;
  
  return {
    // Initial state
    stats: null,
    isLoadingStats: false,
    
    activities: [],
    isLoadingActivities: false,
    
    contentBreakdown: null,
    isLoadingBreakdown: false,
    
    engagementMetrics: null,
    contentPerformance: null,
    usageStats: null,
    
    recommendations: null,
    productivityInsights: null,
    stylePreferences: null,
    
    goals: null,
    
    notificationSettings: null,
    
    liveStats: null,
    
    error: null,
    
    // Main Dashboard Actions
    loadDashboardStats: async () => {
      try {
        set({ isLoadingStats: true, error: null });
        
        const stats = await dashboardService.getDashboardStats();
        
        set({
          stats,
          isLoadingStats: false,
        });
      } catch (error: any) {
        set({ 
          isLoadingStats: false,
          error: error.userMessage || error.message || 'Failed to load dashboard stats' 
        });
        throw error;
      }
    },

    loadRecentActivity: async (limit = 20) => {
      try {
        set({ isLoadingActivities: true, error: null });
        
        const response = await dashboardService.getRecentActivity(limit);
        
        set({
          activities: response.results,
          isLoadingActivities: false,
        });
      } catch (error: any) {
        set({ 
          isLoadingActivities: false,
          error: error.userMessage || error.message || 'Failed to load recent activity' 
        });
        throw error;
      }
    },

    loadContentBreakdown: async (timeframe = 'month') => {
      try {
        set({ isLoadingBreakdown: true, error: null });
        
        const breakdown = await dashboardService.getContentBreakdown(timeframe as any);
        
        set({
          contentBreakdown: breakdown,
          isLoadingBreakdown: false,
        });
      } catch (error: any) {
        set({ 
          isLoadingBreakdown: false,
          error: error.userMessage || error.message || 'Failed to load content breakdown' 
        });
        throw error;
      }
    },

    refreshDashboard: async () => {
      const promises = [
        get().loadDashboardStats(),
        get().loadRecentActivity(),
        get().loadContentBreakdown(),
      ];
      
      try {
        await Promise.allSettled(promises);
      } catch (error) {
        console.error('Error refreshing dashboard:', error);
      }
    },

    // Analytics Actions
    loadEngagementMetrics: async (period = 'month') => {
      try {
        const metrics = await dashboardService.getEngagementMetrics(period);
        set({ engagementMetrics: metrics });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load engagement metrics' });
      }
    },

    loadContentPerformance: async () => {
      try {
        const performance = await dashboardService.getContentPerformance();
        set({ contentPerformance: performance });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load content performance' });
      }
    },

    loadUsageStats: async (timeframe = 'month') => {
      try {
        const usage = await dashboardService.getUsageStats(timeframe);
        set({ usageStats: usage });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load usage stats' });
      }
    },

    // Insights Actions
    loadRecommendations: async () => {
      try {
        const recommendations = await dashboardService.getRecommendations();
        set({ recommendations });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load recommendations' });
      }
    },

    loadProductivityInsights: async () => {
      try {
        const insights = await dashboardService.getProductivityInsights();
        set({ productivityInsights: insights });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load productivity insights' });
      }
    },

    loadStylePreferences: async () => {
      try {
        const preferences = await dashboardService.getStylePreferences();
        set({ stylePreferences: preferences });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load style preferences' });
      }
    },

    // Goals Actions
    loadGoals: async () => {
      try {
        const goals = await dashboardService.getGoals();
        set({ goals });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load goals' });
      }
    },

    updateGoals: async (goalData) => {
      try {
        await dashboardService.updateGoals(goalData);
        // Reload goals to get updated data
        await get().loadGoals();
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to update goals' });
        throw error;
      }
    },

    // Reports Actions
    generateReport: async (type, options = {}) => {
      try {
        const response = await dashboardService.generateReport(type as any, options);
        return response.report_id;
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to generate report' });
        throw error;
      }
    },

    checkReportStatus: async (reportId) => {
      try {
        return await dashboardService.getReportStatus(reportId);
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to check report status' });
        throw error;
      }
    },

    exportDashboardData: async (format) => {
      try {
        const blob = await dashboardService.exportDashboardData(format as any);
        
        // Create download link (React Native Web compatible)
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `dashboard-data.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Export failed' });
        throw error;
      }
    },

    // Notifications Actions
    loadNotificationSettings: async () => {
      try {
        const settings = await dashboardService.getNotificationSettings();
        set({ notificationSettings: settings });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load notification settings' });
      }
    },

    updateNotificationSettings: async (settings) => {
      try {
        await dashboardService.updateNotificationSettings(settings);
        set({ notificationSettings: { ...get().notificationSettings, ...settings } });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to update notification settings' });
        throw error;
      }
    },

    // Live Data Actions
    loadLiveStats: async () => {
      try {
        const liveStats = await dashboardService.getLiveStats();
        set({ liveStats });
      } catch (error: any) {
        set({ error: error.userMessage || error.message || 'Failed to load live stats' });
      }
    },

    startLiveUpdates: () => {
      if (liveUpdateInterval) {
        clearInterval(liveUpdateInterval);
      }
      
      // Update live stats every 30 seconds
      liveUpdateInterval = setInterval(() => {
        get().loadLiveStats().catch(console.error);
      }, 30000);
      
      // Load initial data
      get().loadLiveStats().catch(console.error);
    },

    stopLiveUpdates: () => {
      if (liveUpdateInterval) {
        clearInterval(liveUpdateInterval);
        liveUpdateInterval = null;
      }
    },

    clearError: () => {
      set({ error: null });
    },
  };
});