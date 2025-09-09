import { apiClient } from './apiClient';
import { DashboardStats, ActivityItem, ContentBreakdown, PaginatedResponse } from '../types/api';

class DashboardService {
  // === MAIN DASHBOARD STATS ===

  // Get main dashboard statistics
  async getDashboardStats(): Promise<DashboardStats> {
    return await apiClient.get('/dashboard/stats/');
  }

  // Get recent activity feed
  async getRecentActivity(limit?: number): Promise<PaginatedResponse<ActivityItem>> {
    return await apiClient.get('/dashboard/activity/', {
      params: { limit: limit || 20 }
    });
  }

  // Get content breakdown and analytics
  async getContentBreakdown(timeframe?: 'week' | 'month' | 'quarter' | 'year'): Promise<ContentBreakdown> {
    return await apiClient.get('/dashboard/breakdown/', {
      params: { timeframe: timeframe || 'month' }
    });
  }

  // === ANALYTICS AND INSIGHTS ===

  // Get user engagement metrics
  async getEngagementMetrics(period?: string): Promise<{
    daily_active_sessions: number;
    average_session_duration: number;
    content_creation_rate: number;
    feature_usage: Record<string, number>;
    peak_usage_hours: number[];
    engagement_trends: { date: string; value: number }[];
  }> {
    return await apiClient.get('/dashboard/engagement/', {
      params: { period }
    });
  }

  // Get content performance metrics
  async getContentPerformance(): Promise<{
    top_performing_content: any[];
    content_by_category: Record<string, number>;
    success_rates: Record<string, number>;
    user_satisfaction: {
      average_rating: number;
      total_ratings: number;
      rating_distribution: Record<string, number>;
    };
  }> {
    return await apiClient.get('/dashboard/content-performance/');
  }

  // Get usage statistics
  async getUsageStats(timeframe?: string): Promise<{
    api_calls: {
      total: number;
      by_endpoint: Record<string, number>;
      by_day: { date: string; count: number }[];
    };
    storage_usage: {
      total_mb: number;
      by_type: Record<string, number>;
      trend: { date: string; size_mb: number }[];
    };
    feature_adoption: {
      new_features: string[];
      most_used: Record<string, number>;
      adoption_rates: Record<string, number>;
    };
  }> {
    return await apiClient.get('/dashboard/usage/', {
      params: { timeframe }
    });
  }

  // === PERSONALIZED INSIGHTS ===

  // Get personalized recommendations
  async getRecommendations(): Promise<{
    suggested_features: string[];
    content_ideas: string[];
    optimization_tips: string[];
    trending_styles: string[];
    learning_resources: { title: string; url: string; type: string }[];
  }> {
    return await apiClient.get('/dashboard/recommendations/');
  }

  // Get productivity insights
  async getProductivityInsights(): Promise<{
    most_productive_time: string;
    content_creation_patterns: any[];
    efficiency_score: number;
    time_saved: number;
    suggestions: string[];
    weekly_goals: {
      current_streak: number;
      weekly_target: number;
      progress: number;
    };
  }> {
    return await apiClient.get('/dashboard/productivity/');
  }

  // Get style preferences analysis
  async getStylePreferences(): Promise<{
    preferred_styles: string[];
    style_evolution: { date: string; styles: string[] }[];
    success_by_style: Record<string, number>;
    suggested_styles: string[];
  }> {
    return await apiClient.get('/dashboard/style-preferences/');
  }

  // === GOAL TRACKING ===

  // Get user goals and progress
  async getGoals(): Promise<{
    daily_goals: { target: number; current: number; type: string }[];
    weekly_goals: { target: number; current: number; type: string }[];
    monthly_goals: { target: number; current: number; type: string }[];
    achievements: { name: string; date: string; icon: string }[];
    streaks: { type: string; current: number; best: number }[];
  }> {
    return await apiClient.get('/dashboard/goals/');
  }

  // Update user goals
  async updateGoals(goals: {
    daily_content_goal?: number;
    weekly_content_goal?: number;
    quality_threshold?: number;
    focus_areas?: string[];
  }): Promise<void> {
    await apiClient.post('/dashboard/goals/update/', goals);
  }

  // === EXPORT AND REPORTING ===

  // Generate analytics report
  async generateReport(
    type: 'daily' | 'weekly' | 'monthly' | 'custom',
    options?: {
      start_date?: string;
      end_date?: string;
      include_charts?: boolean;
      format?: 'pdf' | 'csv' | 'json';
    }
  ): Promise<{
    report_url: string;
    report_id: string;
    generated_at: string;
    expires_at: string;
  }> {
    return await apiClient.post('/dashboard/generate-report/', {
      type,
      ...options,
    });
  }

  // Get report status
  async getReportStatus(reportId: string): Promise<{
    status: 'pending' | 'completed' | 'failed';
    progress: number;
    download_url?: string;
    error?: string;
  }> {
    return await apiClient.get(`/dashboard/reports/${reportId}/status/`);
  }

  // Export dashboard data
  async exportDashboardData(format: 'json' | 'csv'): Promise<Blob> {
    return await apiClient.get('/dashboard/export/', {
      params: { format },
      responseType: 'blob'
    });
  }

  // === EMBEDDINGS STATS (AI ASSISTANT) ===

  // Get embeddings and AI assistant statistics
  async getEmbeddingsStats(): Promise<{
    total_documents: number;
    total_embeddings: number;
    knowledge_coverage: number;
    recent_queries: number;
    top_topics: string[];
    assistant_usage: {
      total_chats: number;
      average_response_time: number;
      satisfaction_score: number;
    };
  }> {
    return await apiClient.get('/dashboard/embeddings-stats/');
  }

  // === REAL-TIME UPDATES ===

  // Get real-time dashboard updates (for live data)
  async getLiveStats(): Promise<{
    active_generations: number;
    queue_length: number;
    system_status: 'healthy' | 'degraded' | 'down';
    recent_completions: any[];
    current_load: number;
  }> {
    return await apiClient.get('/dashboard/live-stats/');
  }

  // === NOTIFICATION PREFERENCES ===

  // Get dashboard notification settings
  async getNotificationSettings(): Promise<{
    email_notifications: boolean;
    push_notifications: boolean;
    digest_frequency: 'daily' | 'weekly' | 'monthly';
    notification_types: string[];
  }> {
    return await apiClient.get('/dashboard/notification-settings/');
  }

  // Update notification settings
  async updateNotificationSettings(settings: {
    email_notifications?: boolean;
    push_notifications?: boolean;
    digest_frequency?: 'daily' | 'weekly' | 'monthly';
    notification_types?: string[];
  }): Promise<void> {
    await apiClient.post('/dashboard/notification-settings/', settings);
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;