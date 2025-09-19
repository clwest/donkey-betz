import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  User,
  FileText,
  TrendingUp,
  Brain,
  Settings,
  BarChart3,
  PlusCircle,
  Activity,
  DollarSign,
  Clock,
  CheckCircle,
  AlertCircle,
  Sparkles,
  MessageSquare,
  Zap,
  Trophy
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';

interface DashboardData {
  user: {
    name: string;
    email: string;
    avatar?: string;
    plan: 'free' | 'pro' | 'enterprise';
    credits: number;
  };
  stats: {
    articlesGenerated: number;
    betsAnalyzed: number;
    agentsUsed: number;
    totalSavings: number;
  };
  recentActivity: Array<{
    id: string;
    type: 'content' | 'betting' | 'agent';
    title: string;
    status: 'completed' | 'processing' | 'failed';
    timestamp: string;
  }>;
  quickActions: Array<{
    icon: any;
    title: string;
    description: string;
    action: string;
    color: string;
  }>;
}

const UserDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/user/dashboard/');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      // Use mock data as fallback
      setDashboardData(getMockDashboardData());
    } finally {
      setLoading(false);
    }
  };

  const getMockDashboardData = (): DashboardData => ({
    user: {
      name: 'John Doe',
      email: 'john@example.com',
      plan: 'pro',
      credits: 1250
    },
    stats: {
      articlesGenerated: 87,
      betsAnalyzed: 342,
      agentsUsed: 23,
      totalSavings: 4850
    },
    recentActivity: [
      {
        id: '1',
        type: 'content',
        title: 'AI Content Strategy Article Generated',
        status: 'completed',
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        type: 'betting',
        title: 'NBA Odds Analysis - Lakers vs Warriors',
        status: 'processing',
        timestamp: new Date(Date.now() - 300000).toISOString()
      },
      {
        id: '3',
        type: 'agent',
        title: 'Multi-agent research task completed',
        status: 'completed',
        timestamp: new Date(Date.now() - 600000).toISOString()
      }
    ],
    quickActions: [
      {
        icon: FileText,
        title: 'Generate Content',
        description: 'Create articles, blogs, and marketing copy',
        action: '/content/create',
        color: 'text-blue-500'
      },
      {
        icon: TrendingUp,
        title: 'Sports Analysis',
        description: 'Analyze odds and betting opportunities',
        action: '/sports/analyze',
        color: 'text-green-500'
      },
      {
        icon: Brain,
        title: 'AI Agents',
        description: 'Run multi-agent tasks and workflows',
        action: '/agents/orchestrate',
        color: 'text-purple-500'
      },
      {
        icon: MessageSquare,
        title: 'AI Assistant',
        description: 'Chat with your personal AI assistant',
        action: '/assistant/chat',
        color: 'text-orange-500'
      }
    ]
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case 'enterprise':
        return 'bg-purple-600/20 text-purple-400 border-purple-600/50';
      case 'pro':
        return 'bg-blue-600/20 text-blue-500 border-blue-600/50';
      default:
        return 'bg-gray-600/20 text-muted-foreground border-gray-600/50';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-foreground">Loading dashboard...</div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-red-500">Failed to load dashboard</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-background/70 backdrop-blur-lg border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
              <p className="text-muted-foreground">Welcome back, {dashboardData.user.name}</p>
            </div>
            <div className="flex items-center gap-4">
              <Badge className={getPlanBadgeColor(dashboardData.user.plan)}>
                {dashboardData.user.plan.toUpperCase()} Plan
              </Badge>
              <div className="flex items-center gap-2 text-yellow-500">
                <Zap className="h-4 w-4" />
                <span className="font-medium">{dashboardData.user.credits} credits</span>
              </div>
              <Button
                variant="ghost"
                onClick={() => navigate('/settings')}
                className="text-muted-foreground hover:text-foreground"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-card/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Articles Generated</p>
                  <p className="text-3xl font-bold text-foreground">{dashboardData.stats.articlesGenerated}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Bets Analyzed</p>
                  <p className="text-3xl font-bold text-foreground">{dashboardData.stats.betsAnalyzed}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Agents Used</p>
                  <p className="text-3xl font-bold text-foreground">{dashboardData.stats.agentsUsed}</p>
                </div>
                <Brain className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Savings</p>
                  <p className="text-3xl font-bold text-foreground">${dashboardData.stats.totalSavings}</p>
                </div>
                <DollarSign className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <Card className="bg-card/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-foreground flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-500" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="grid md:grid-cols-2 gap-4">
                {dashboardData.quickActions.map((action, index) => (
                  <Card
                    key={index}
                    className="bg-gray-700/50 border-gray-600 hover:bg-gray-700/70 transition-all cursor-pointer group"
                    onClick={() => navigate(action.action)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <action.icon className={`h-8 w-8 ${action.color} group-hover:scale-110 transition-transform`} />
                        <div className="flex-1">
                          <h3 className="font-semibold text-foreground mb-1">{action.title}</h3>
                          <p className="text-sm text-muted-foreground">{action.description}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div>
            <Card className="bg-card/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-foreground flex items-center gap-2">
                  <Activity className="h-5 w-5 text-green-500" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {dashboardData.recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-700/30">
                    {getStatusIcon(activity.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {activity.title}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
                
                <Button
                  variant="outline"
                  className="w-full mt-4 border-gray-600 text-muted-foreground hover:bg-gray-700"
                  onClick={() => navigate('/activity')}
                >
                  View All Activity
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Performance Chart Placeholder */}
        <Card className="mt-8 bg-card/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-foreground flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              Performance Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-gray-700/30 rounded-lg">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-muted-foreground">Performance charts coming soon</p>
                <p className="text-sm text-muted-foreground">Track your usage and success metrics</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Upgrade CTA */}
        {dashboardData.user.plan === 'free' && (
          <Card className="mt-8 bg-gradient-to-r from-purple-900/30 to-pink-900/30 border-purple-700">
            <CardContent className="p-6 text-center">
              <Trophy className="h-12 w-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-foreground mb-2">Unlock More Power</h3>
              <p className="text-muted-foreground mb-4">
                Upgrade to Pro for unlimited agents, priority support, and advanced analytics
              </p>
              <Button
                onClick={() => navigate('/pricing')}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                Upgrade Now
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;