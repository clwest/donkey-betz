import { apiClient } from './api.config';

// Dashboard Types
export interface DashboardStats {
  total_content: number;
  total_content_trend: string;
  images_generated: number;
  images_trend: string;
  text_content: number;
  video_content: number;
  active_workflows: number;
  extended_content: {
    blogs: number;
    social_posts: number;
    campaigns: number;
    ebooks: number;
    podcasts: number;
    pitch_decks: number;
  };
  usage_period: string;
}

export interface RecentActivity {
  id: number;
  type: string;
  name: string;
  description?: string;
  time: string;
  status: 'completed' | 'running' | 'failed';
  content_type: string;
  created_at: string;
  nav_route?: string;
  gallery_id?: number;
}

export interface ContentBreakdown {
  content_breakdown: Array<{
    type: string;
    count: number;
  }>;
  extended_breakdown: Array<{
    type: string;
    count: number;
  }>;
}

// Dashboard API Functions
export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const response = await apiClient.get('/v1/dashboard/stats/');
    return response.data;
  },

  async getRecentActivity(limit: number = 10): Promise<RecentActivity[]> {
    const response = await apiClient.get(`/v1/dashboard/activity/?limit=${limit}`);
    return response.data;
  },

  async getContentBreakdown(): Promise<ContentBreakdown> {
    const response = await apiClient.get('/v1/dashboard/breakdown/');
    return response.data;
  },
};

// Utility Functions
export const formatTrend = (trend: string) => {
  const isPositive = trend.startsWith('+');
  const value = trend;
  const color = isPositive ? 'text-green-400' : trend === '0%' ? 'text-gray-400' : 'text-red-400';
  
  return { value, isPositive, color };
};

export const getActivityStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'bg-green-400';
    case 'running':
      return 'bg-yellow-400 animate-pulse';
    case 'failed':
      return 'bg-red-400';
    default:
      return 'bg-gray-400';
  }
};

export const getContentTypeIcon = (type: string): string => {
  // Map detailed content types to appropriate icons
  const lowerType = type.toLowerCase();
  
  if (lowerType.includes('blog')) return 'DocumentTextIcon';
  if (lowerType.includes('social')) return 'MegaphoneIcon';
  if (lowerType.includes('email')) return 'EnvelopeIcon';
  if (lowerType.includes('ebook')) return 'BookOpenIcon';
  if (lowerType.includes('podcast')) return 'MicrophoneIcon';
  if (lowerType.includes('campaign')) return 'RocketLaunchIcon';
  
  // Default type mappings
  switch (type) {
    case 'image':
      return 'PhotoIcon';
    case 'video':
      return 'VideoCameraIcon';
    case 'text':
      return 'DocumentTextIcon';
    case 'workflow':
      return 'CpuChipIcon';
    default:
      return 'SparklesIcon';
  }
};

export const getTotalExtendedContent = (extendedContent: DashboardStats['extended_content']): number => {
  return Object.values(extendedContent).reduce((sum, count) => sum + count, 0);
};

export const getQuickActionSuggestions = (stats: DashboardStats) => {
  const suggestions = [];

  // Suggest creating first eBook if user has blog content but no eBooks
  if (stats.extended_content.blogs > 5 && stats.extended_content.ebooks === 0) {
    suggestions.push({
      title: 'Create Your First eBook',
      description: `Turn your ${stats.extended_content.blogs} blog posts into a comprehensive eBook`,
      action: 'ebooks',
      priority: 1
    });
  }

  // Suggest social media if they have text but low social posts
  if (stats.text_content > 10 && stats.extended_content.social_posts < 5) {
    suggestions.push({
      title: 'Boost Social Presence',
      description: 'Convert your content into engaging social media posts',
      action: 'studio?tab=social',
      priority: 2
    });
  }

  // Suggest campaigns if they have diverse content
  if (getTotalExtendedContent(stats.extended_content) > 10 && stats.extended_content.campaigns < 3) {
    suggestions.push({
      title: 'Launch a Campaign',
      description: 'Organize your content into targeted campaigns',
      action: 'campaigns',
      priority: 3
    });
  }

  return suggestions.sort((a, b) => a.priority - b.priority).slice(0, 3);
};

export const getProductivityInsights = (stats: DashboardStats) => {
  const insights = [];

  // Content velocity
  const contentVelocity = stats.total_content / 30; // per day average
  insights.push({
    title: 'Daily Content Average',
    value: contentVelocity.toFixed(1),
    description: 'pieces of content per day',
    trend: stats.total_content_trend
  });

  // Content diversity
  const contentTypes = [
    stats.text_content,
    stats.images_generated, 
    stats.video_content
  ].filter(count => count > 0).length;
  
  insights.push({
    title: 'Content Diversity',
    value: `${contentTypes}/3`,
    description: 'content types actively used'
  });

  // Workflow efficiency
  const workflowEfficiency = stats.active_workflows > 0 ? 
    (getTotalExtendedContent(stats.extended_content) / Math.max(stats.active_workflows, 1)) : 0;
  
  insights.push({
    title: 'Workflow Efficiency',
    value: workflowEfficiency.toFixed(1),
    description: 'content pieces per active workflow'
  });

  return insights;
};