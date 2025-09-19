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
        <p className="text-red-500 mb-4">{error || 'Failed to load dashboard'}</p>
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
    <div className="space-y-8 animate-fade-in">
      {/* Enhanced Gaming Header */}
      <div className="relative">
        {/* Background gradient accent */}
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-accent/5 rounded-2xl" />

        <div className="relative flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 p-6 rounded-2xl bg-card/40 backdrop-blur-sm border border-border/30">
          <div>
            <h1 className="text-4xl font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Welcome back!
            </h1>
            <p className="mt-2 text-muted-foreground text-lg">
              Here's what's happening with your content in the last {stats.usage_period}.
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => navigate('/studio')}
              className="hover:shadow-glow-secondary"
            >
              <SparklesIcon className="h-4 w-4" />
              Quick Generate
            </Button>
            <Button
              onClick={() => navigate('/opportunities?tab=campaigns')}
              className="hover:shadow-glow-primary"
            >
              <PlusIcon className="h-4 w-4" />
              New Campaign
            </Button>
          </div>
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
              className="cursor-pointer group p-6 border-border/50 hover:border-primary/30 transition-all duration-300"
              onClick={() => stat.route && navigate(stat.route)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
                  <p className="text-3xl font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mt-2 font-mono tracking-tight">
                    {stat.value}
                  </p>
                  {trendData && (
                    <div className={`flex items-center gap-1 text-sm mt-3 ${trendData.color}`}>
                      {trendData.isPositive ? (
                        <ArrowTrendingUpIcon className="h-3 w-3" />
                      ) : (
                        <ArrowTrendingDownIcon className="h-3 w-3" />
                      )}
                      <span className="font-medium">{trendData.value}</span> from last period
                    </div>
                  )}
                </div>
                <div className="p-3 rounded-xl bg-gradient-to-br from-primary/10 to-accent/5 border border-primary/20 group-hover:border-primary/40 group-hover:shadow-glow-subtle transition-all duration-300">
                  <stat.icon className="h-6 w-6 text-primary group-hover:drop-shadow-glow-cyan" />
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
              className="cursor-pointer group p-4 text-center border-border/50 hover:border-secondary/40"
              onClick={() => navigate(stat.route)}
            >
              <div className="space-y-3">
                <div className="p-3 rounded-xl inline-flex bg-gradient-to-br from-secondary/10 to-accent/5 border border-secondary/20 group-hover:border-secondary/40 group-hover:shadow-glow-subtle transition-all duration-300">
                  <stat.icon className="h-5 w-5 text-secondary group-hover:drop-shadow-glow-cyan" />
                </div>
                <p className="text-2xl font-bold text-gradient bg-gradient-to-r from-secondary to-primary bg-clip-text text-transparent font-mono">
                  {stat.value}
                </p>
                <p className="text-xs text-muted-foreground font-medium">{stat.label}</p>
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
        {/* Enhanced Gaming Recent Activity */}
        <Card className="lg:col-span-2 p-6 border-border/50">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Recent Activity
            </h2>
            <button
              className="text-sm text-primary hover:text-accent hover:shadow-glow-subtle transition-all duration-200 px-3 py-1 rounded-lg border border-primary/20 hover:border-primary/40 backdrop-blur-sm"
              onClick={() => navigate('/gallery')}
            >
              View all
            </button>
          </div>
          <div className="space-y-3">
            {activities.length === 0 ? (
              <div className="text-center py-12">
                <div className="mb-4">
                  <SparklesIcon className="h-12 w-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                </div>
                <p className="text-muted-foreground text-lg mb-2">No recent activity</p>
                <p className="text-muted-foreground/70 text-sm mb-6">Start creating content to see your activity here</p>
                <Button
                  variant="primary"
                  className="hover:shadow-glow-primary"
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
                  'image': 'bg-purple-500/10 border-purple-500',
                  'video': 'bg-primary/10 border-primary',
                  'text': 'bg-green-500/10 border-green-500',
                  'workflow': 'bg-orange-500/10 border-orange-500'
                };
                const bgColor = typeColors[activity.type] || 'bg-muted/10 border-border';
                
                return (
                  <div
                    key={activity.id}
                    className={`p-4 rounded-xl border ${bgColor} hover:bg-card/60 hover:border-primary/30 transition-all duration-300 cursor-pointer group backdrop-blur-sm`}
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
                          <div className={`w-2 h-2 rounded-full ${getActivityStatusColor(activity.status)} shadow-glow-subtle`} />
                          <IconComponent className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                              {activity.name}
                            </p>
                            <span className="px-2 py-0.5 text-xs rounded-full bg-background/60 border border-border/40 text-muted-foreground backdrop-blur-sm">
                              {activity.type === 'image' ? '🎨' : activity.type === 'video' ? '🎬' : activity.type === 'text' ? '📝' : '⚙️'} {activity.type}
                            </span>
                          </div>
                          {activity.description && (
                            <p className="text-xs text-muted-foreground line-clamp-2 mt-1 leading-relaxed">
                              {activity.description}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground whitespace-nowrap">
                        <ClockIcon className="h-3 w-3" />
                        <span className="font-medium">{activity.time}</span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* Enhanced Quick Actions & Suggestions */}
        <div className="space-y-6">
          {/* Enhanced Productivity Insights */}
          <Card className="p-6 border-border/50">
            <h2 className="text-lg font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-6">
              Productivity Insights
            </h2>
            <div className="space-y-4">
              {insights.map((insight, index) => (
                <div key={index} className="flex justify-between items-center p-3 rounded-lg bg-background/40 border border-border/30 backdrop-blur-sm">
                  <div>
                    <p className="text-sm font-semibold text-foreground">{insight.value}</p>
                    <p className="text-xs text-muted-foreground mt-1">{insight.description}</p>
                  </div>
                  {insight.trend && (
                    <span className={`text-xs font-medium px-2 py-1 rounded-full bg-background/60 border border-border/40 ${formatTrend(insight.trend).color}`}>
                      {insight.trend}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Enhanced Quick Actions */}
          <Card className="p-6 border-border/50">
            <h2 className="text-lg font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-6">
              Quick Actions
            </h2>
            <div className="space-y-3">
              <Button
                variant="secondary"
                className="w-full justify-start hover:shadow-glow-secondary"
                onClick={() => navigate('/studio')}
              >
                <SparklesIcon className="h-4 w-4" />
                Generate Content
              </Button>
              <Button
                variant="secondary"
                className="w-full justify-start hover:shadow-glow-secondary"
                onClick={() => navigate('/voice')}
              >
                <MicrophoneIcon className="h-4 w-4" />
                Voice Studio
              </Button>
              <Button
                variant="secondary"
                className="w-full justify-start hover:shadow-glow-secondary"
                onClick={() => navigate('/research')}
              >
                <BookOpenIcon className="h-4 w-4" />
                Upload Research
              </Button>
            </div>
          </Card>

          {/* Enhanced AI Suggestions */}
          {suggestions.length > 0 && (
            <Card className="p-6 border-border/50">
              <h2 className="text-lg font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-6">
                Suggested Next Steps
              </h2>
              <div className="space-y-3">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="p-4 border border-border/30 rounded-xl hover:bg-card/60 hover:border-primary/30 cursor-pointer transition-all duration-300 backdrop-blur-sm group"
                    onClick={() => navigate(`/${suggestion.action}`)}
                  >
                    <h3 className="font-semibold text-foreground text-sm mb-1 group-hover:text-primary transition-colors">
                      {suggestion.title}
                    </h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">{suggestion.description}</p>
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