import { useState, useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { 
  SparklesIcon, 
  PhotoIcon, 
  ChartBarIcon, 
  ClockIcon,
  CpuChipIcon,
  PlusIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  BookOpenIcon,
  MegaphoneIcon,
  RocketLaunchIcon,
  MicrophoneIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import EmbeddingsTracker from '../../components/dashboard/EmbeddingsTracker';
// INLINE INTERFACES TO ELIMINATE IMPORT ISSUES
interface DashboardStats {
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

interface RecentActivity {
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

import { 
  dashboardService,
  formatTrend, 
  getActivityStatusColor, 
  getContentTypeIcon, 
  getTotalExtendedContent, 
  getQuickActionSuggestions, 
  getProductivityInsights
} from '../../services/dashboard.service';
import { toast } from 'sonner';

export function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  console.log('🔐 DashboardPage: Component rendered');

  useEffect(() => {
    console.log('🔐 DashboardPage: useEffect - loading dashboard data');
    loadDashboardData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(loadDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      console.log('🔐 DashboardPage: Starting to load dashboard data...');
      setLoading(true);
      setError(null);
      
      const [statsData, activitiesData] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getRecentActivity(8)
      ]);
      
      console.log('🔐 DashboardPage: Data loaded successfully', { statsData, activitiesData });
      setStats(statsData);
      setActivities(activitiesData);
    } catch (err: any) {
      console.error('🔐 DashboardPage: Error loading dashboard:', err);
      console.error('🔐 DashboardPage: Error details:', {
        message: err.message,
        status: err.status,
        userMessage: err.userMessage,
        response: err.response
      });
      
      // Use fallback data instead of showing error
      console.log('🔐 DashboardPage: Using fallback data');
      setStats({
        total_content: 0,
        total_content_trend: '+0%',
        images_generated: 0,
        images_trend: '+0%',
        text_content: 0,
        video_content: 0,
        active_workflows: 0,
        extended_content: {
          blogs: 0,
          social_posts: 0,
          campaigns: 0,
          ebooks: 0,
          podcasts: 0,
          pitch_decks: 0,
        },
        usage_period: 'Last 30 days',
      });
      setActivities([]);
      // Don't show error toast - just use empty data
      // toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getIconComponent = (iconName: string) => {
    switch (iconName) {
      case 'SparklesIcon': return SparklesIcon;
      case 'PhotoIcon': return PhotoIcon;
      case 'DocumentTextIcon': return DocumentTextIcon;
      case 'VideoCameraIcon': return VideoCameraIcon;
      case 'CpuChipIcon': return CpuChipIcon;
      case 'MegaphoneIcon': return MegaphoneIcon;
      case 'EnvelopeIcon': return EnvelopeIcon;
      case 'BookOpenIcon': return BookOpenIcon;
      case 'MicrophoneIcon': return MicrophoneIcon;
      case 'RocketLaunchIcon': return RocketLaunchIcon;
      default: return SparklesIcon;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400 mb-4">{error || 'Failed to load dashboard'}</p>
        <Button onClick={loadDashboardData} variant="secondary">
          Try Again
        </Button>
      </div>
    );
  }

  const mainStats = [
    { 
      label: 'Total Content Created', 
      value: stats.total_content.toLocaleString(), 
      icon: SparklesIcon, 
      trend: stats.total_content_trend,
      route: '/gallery'
    },
    { 
      label: 'Images Generated', 
      value: stats.images_generated.toLocaleString(), 
      icon: PhotoIcon, 
      trend: stats.images_trend,
      route: '/gallery?tab=images'
    },
    { 
      label: 'Active Workflows', 
      value: stats.active_workflows.toString(), 
      icon: CpuChipIcon, 
      trend: null,
      route: '/campaigns'
    },
    { 
      label: 'Extended Content', 
      value: getTotalExtendedContent(stats.extended_content).toString(), 
      icon: ChartBarIcon, 
      trend: null,
      route: '/gallery'
    },
  ];

  const extendedContentStats = [
    { label: 'Blog Posts', value: stats.extended_content.blogs, icon: DocumentTextIcon, route: '/gallery?tab=blogs' },
    { label: 'Social Posts', value: stats.extended_content.social_posts, icon: MegaphoneIcon, route: '/gallery?tab=social' },
    { label: 'eBooks', value: stats.extended_content.ebooks, icon: BookOpenIcon, route: '/ebooks' },
    { label: 'Campaigns', value: stats.extended_content.campaigns, icon: RocketLaunchIcon, route: '/campaigns' },
    { label: 'Podcasts', value: stats.extended_content.podcasts, icon: MicrophoneIcon, route: '/voice' },
  ].filter(stat => stat.value > 0);

  const suggestions = getQuickActionSuggestions(stats);
  const insights = getProductivityInsights(stats);

  return (
    <div className="space-y-8">
      {/* Gaming Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-neon-cyan">Welcome back!</h1>
          <p className="mt-1" style={{ color: 'var(--gaming-text-muted)' }}>
            Here's what's happening with your content in the last {stats.usage_period}.
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={() => navigate('/studio')}>
            <SparklesIcon className="h-4 w-4" />
            Quick Generate
          </Button>
          <Button onClick={() => navigate('/campaigns/new')}>
            <PlusIcon className="h-4 w-4" />
            New Campaign
          </Button>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {mainStats.map((stat) => {
          const trendData = stat.trend ? formatTrend(stat.trend) : null;
          return (
            <Card 
              key={stat.label} 
              hover 
              className="cursor-pointer card-gaming"
              onClick={() => stat.route && navigate(stat.route)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm" style={{ color: 'var(--gaming-text-muted)' }}>{stat.label}</p>
                  <p className="text-2xl font-bold text-neon-cyan mt-1 font-mono">{stat.value}</p>
                  {trendData && (
                    <div className={`flex items-center gap-1 text-sm mt-2 ${trendData.color}`}>
                      {trendData.isPositive ? (
                        <ArrowTrendingUpIcon className="h-3 w-3" />
                      ) : (
                        <ArrowTrendingDownIcon className="h-3 w-3" />
                      )}
                      {trendData.value} from last period
                    </div>
                  )}
                </div>
                <div 
                  className="p-3 rounded-lg"
                  style={{
                    background: 'rgba(0, 255, 255, 0.1)',
                    border: '1px solid var(--gaming-neon-cyan)',
                    boxShadow: 'var(--gaming-glow-subtle)'
                  }}
                >
                  <stat.icon className="h-6 w-6 text-neon-cyan" />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Extended Content Stats */}
      {extendedContentStats.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {extendedContentStats.map((stat) => (
            <Card 
              key={stat.label}
              hover
              className="cursor-pointer card-gaming"
              onClick={() => navigate(stat.route)}
            >
              <div className="text-center">
                <div 
                  className="p-2 rounded-lg inline-flex mb-2"
                  style={{
                    background: 'rgba(157, 78, 221, 0.1)',
                    border: '1px solid var(--gaming-neon-purple)'
                  }}
                >
                  <stat.icon className="h-5 w-5 text-neon-purple" />
                </div>
                <p className="text-lg font-bold text-neon-green font-mono">{stat.value}</p>
                <p className="text-xs" style={{ color: 'var(--gaming-text-muted)' }}>{stat.label}</p>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Embeddings Tracker and System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EmbeddingsTracker />
        {/* Space for another widget if needed */}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gaming Recent Activity */}
        <Card className="lg:col-span-2 card-gaming">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-neon-cyan">Recent Activity</h2>
            <button 
              className="text-sm text-neon-cyan hover:text-neon-purple transition-colors duration-200"
              onClick={() => navigate('/gallery')}
            >
              View all
            </button>
          </div>
          <div className="space-y-3">
            {activities.length === 0 ? (
              <div className="text-center py-8">
                <p style={{ color: 'var(--gaming-text-muted)' }}>No recent activity</p>
                <Button 
                  variant="secondary" 
                  className="mt-4"
                  onClick={() => navigate('/studio')}
                >
                  <SparklesIcon className="h-4 w-4" />
                  Create Your First Content
                </Button>
              </div>
            ) : (
              activities.map((activity) => {
                const IconComponent = getIconComponent(getContentTypeIcon(activity.type));
                const typeColors = {
                  'image': 'rgba(157, 78, 221, 0.1) border-gaming-neon-purple',
                  'video': 'rgba(0, 255, 255, 0.1) border-gaming-neon-cyan',
                  'text': 'rgba(57, 255, 20, 0.1) border-gaming-neon-green',
                  'workflow': 'rgba(255, 107, 0, 0.1) border-gaming-border'
                };
                const bgColor = typeColors[activity.type] || 'rgba(255, 255, 255, 0.05) border-gaming-border';
                
                return (
                  <div 
                    key={activity.id} 
                    className={`p-4 rounded-lg border ${bgColor} hover:bg-white/5 transition-all cursor-pointer group`}
                    onClick={() => {
                      if (activity.nav_route) {
                        navigate(activity.nav_route);
                      } else {
                        navigate('/gallery');
                      }
                    }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="mt-1 flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getActivityStatusColor(activity.status)}`} />
                          <IconComponent className="h-5 w-5 text-gray-300" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-sm font-semibold text-white">{activity.name}</p>
                            <span className="px-2 py-0.5 text-xs rounded-full bg-white/10 text-gray-300">
                              {activity.type === 'image' ? '🎨' : activity.type === 'video' ? '🎬' : activity.type === 'text' ? '📝' : '⚙️'} {activity.type}
                            </span>
                          </div>
                          {activity.description && (
                            <p className="text-xs text-gray-400 line-clamp-2 mt-1">
                              {activity.description}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-gray-500 whitespace-nowrap">
                        <ClockIcon className="h-3 w-3" />
                        {activity.time}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* Quick Actions & Suggestions */}
        <div className="space-y-6">
          {/* Productivity Insights */}
          <Card>
            <h2 className="text-lg font-semibold text-white mb-4">Productivity Insights</h2>
            <div className="space-y-3">
              {insights.map((insight, index) => (
                <div key={index} className="flex justify-between items-center">
                  <div>
                    <p className="text-sm font-medium text-white">{insight.value}</p>
                    <p className="text-xs text-gray-400">{insight.description}</p>
                  </div>
                  {insight.trend && (
                    <span className={`text-xs ${formatTrend(insight.trend).color}`}>
                      {insight.trend}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Quick Actions */}
          <Card>
            <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Button 
                variant="secondary" 
                className="w-full justify-start"
                onClick={() => navigate('/studio')}
              >
                <SparklesIcon className="h-4 w-4" />
                Generate Content
              </Button>
              <Button 
                variant="secondary" 
                className="w-full justify-start"
                onClick={() => navigate('/voice')}
              >
                <MicrophoneIcon className="h-4 w-4" />
                Voice Studio
              </Button>
              <Button 
                variant="secondary" 
                className="w-full justify-start"
                onClick={() => navigate('/research')}
              >
                <BookOpenIcon className="h-4 w-4" />
                Upload Research
              </Button>
            </div>
          </Card>

          {/* AI Suggestions */}
          {suggestions.length > 0 && (
            <Card>
              <h2 className="text-lg font-semibold text-white mb-4">Suggested Next Steps</h2>
              <div className="space-y-3">
                {suggestions.map((suggestion, index) => (
                  <div key={index} className="p-3 border border-white/10 rounded-lg hover:bg-white/5 cursor-pointer transition-colors"
                       onClick={() => navigate(`/${suggestion.action}`)}>
                    <h3 className="font-medium text-white text-sm">{suggestion.title}</h3>
                    <p className="text-xs text-gray-400 mt-1">{suggestion.description}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}