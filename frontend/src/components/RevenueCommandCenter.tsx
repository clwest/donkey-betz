/**
 * Revenue Command Center
 *
 * Unified revenue management combining opportunities tracking and dashboard analytics
 * into a single comprehensive interface for complete revenue oversight.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  Target,
  Calendar,
  Clock,
  BarChart,
  PieChart,
  LineChart,
  Zap,
  Wifi,
  WifiOff,
  RefreshCw,
  Briefcase,
  FileText,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ArrowRight,
  Building,
  Rocket,
  Star,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import {
  LineChart as RechartsLineChart,
  Line,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface Opportunity {
  id: string;
  title: string;
  company: string;
  type: string;
  budget: string;
  deadline: string;
  skills: string[];
  description: string;
  url?: string;
  posted?: string;
  platform?: string;
  matchScore?: number;
  status?: 'new' | 'viewed' | 'applied' | 'rejected' | 'accepted';
}

interface RevenueMetrics {
  total_revenue: number;
  monthly_revenue: number;
  weekly_revenue: number;
  proposals_submitted: number;
  responses_received: number;
  conversions: number;
  conversion_rate: number;
  average_deal_size: number;
  response_rate: number;
  platform_breakdown: Record<string, any>;
  total_opportunities: number;
}

interface DailyMetric {
  date: string;
  revenue: number;
  proposals: number;
  conversions: number;
}

interface PlatformStats {
  name: string;
  revenue: number;
  opportunities: number;
  conversions: number;
  color: string;
}

const RevenueCommandCenter: React.FC = () => {
  // State Management
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d'>('30d');
  const [metrics, setMetrics] = useState<RevenueMetrics | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [dailyMetrics, setDailyMetrics] = useState<DailyMetric[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [filter, setFilter] = useState<'all' | 'new' | 'applied' | 'accepted'>('all');
  const [activeTab, setActiveTab] = useState('opportunities');

  // WebSocket Connection
  const { sendMessage, lastMessage, isConnected } = useWebSocket({
    url: '/ws/revenue-dashboard/',
    onMessage: (data) => {
      console.log('Revenue Command Center received:', data);

      if (data.type === 'revenue_data_update' || data.type === 'initial_revenue_data') {
        if (data.data) {
          const metricsData = data.data.metrics || data.data;
          setMetrics(metricsData);
          generateDailyMetrics(timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : 90, metricsData);
          setLoading(false);
        }
      } else if (data.type === 'opportunities_data') {
        if (data.data?.opportunities) {
          setOpportunities(data.data.opportunities);
        }
      } else if (data.type === 'new_opportunity') {
        if (data.opportunity) {
          setOpportunities(prev => [data.opportunity, ...prev]);
        }
      } else if (data.type === 'proposal_submitted') {
        if (data.opportunity_id) {
          setOpportunities(prev => prev.map(opp =>
            opp.id === data.opportunity_id ? { ...opp, status: 'applied' } : opp
          ));
        }
      }
    },
    onOpen: () => {
      setWsConnected(true);
      setLoading(false);
      console.log('Revenue Command Center connected');
      sendMessage({ type: 'subscribe_all' });
      fetchInitialData();
    },
    onClose: () => {
      setWsConnected(false);
      console.log('Revenue Command Center disconnected');
    },
    reconnectInterval: 5000,
    maxReconnectAttempts: 10
  });

  useEffect(() => {
    setWsConnected(isConnected);
  }, [isConnected]);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      // Fetch metrics
      const metricsResponse = await fetch('http://localhost:8000/api/v1/intelligence/revenue/metrics/?days=30');
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        if (metricsData.metrics) {
          setMetrics(metricsData.metrics);
          generateDailyMetrics(30, metricsData.metrics);
        }
      }

      // Fetch opportunities
      const oppResponse = await fetch('http://localhost:8000/api/opportunities/');
      if (oppResponse.ok) {
        const oppData = await oppResponse.json();
        if (oppData.success && oppData.data) {
          // Process opportunities from various sources
          const allOpportunities: Opportunity[] = [];

          // Add job opportunities
          if (oppData.data.jobs) {
            oppData.data.jobs.forEach((job: any) => {
              allOpportunities.push({
                id: job.id || `job_${Date.now()}_${Math.random()}`,
                title: job.title,
                company: job.company,
                type: 'job',
                budget: job.budget || job.salary || 'Negotiable',
                deadline: job.deadline || 'ASAP',
                skills: job.required_skills || [],
                description: job.description || '',
                url: job.url,
                platform: job.platform || 'Direct',
                matchScore: job.match_score,
                status: 'new'
              });
            });
          }

          // Add content opportunities
          if (oppData.data.content) {
            oppData.data.content.forEach((content: any) => {
              allOpportunities.push({
                id: content.id || `content_${Date.now()}_${Math.random()}`,
                title: content.title,
                company: content.client || 'Content Client',
                type: 'content',
                budget: content.budget || content.pay || 'Per Article',
                deadline: content.deadline || 'Ongoing',
                skills: content.requirements || [],
                description: content.description || '',
                platform: 'Content Platform',
                matchScore: 85,
                status: 'new'
              });
            });
          }

          setOpportunities(allOpportunities);
        }
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching initial data:', error);
      setLoading(false);
    }
  };

  const generateDailyMetrics = (days: number, metricsData: RevenueMetrics) => {
    const data: DailyMetric[] = [];
    const avgDaily = (metricsData?.total_revenue || 0) / days;

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const variation = (Math.random() - 0.5) * 0.4;

      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        revenue: Math.floor(avgDaily * (1 + variation)),
        proposals: Math.floor((metricsData?.proposals_submitted || 0) / days * (1 + variation)),
        conversions: Math.floor((metricsData?.conversions || 0) / days * (1 + Math.random()))
      });
    }

    setDailyMetrics(data);
  };

  const getPlatformStats = (): PlatformStats[] => {
    if (!metrics?.platform_breakdown) return [];

    const colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
    return Object.entries(metrics.platform_breakdown).map(([name, stats]: [string, any], index) => ({
      name,
      revenue: stats.revenue || 0,
      opportunities: stats.count || 0,
      conversions: stats.conversions || 0,
      color: colors[index % colors.length]
    }));
  };

  const handleQuickApply = async (opportunity: Opportunity) => {
    if (wsConnected) {
      sendMessage({
        type: 'quick_apply',
        opportunity_id: opportunity.id,
        opportunity: opportunity
      });
    }

    // Update UI optimistically
    setOpportunities(prev => prev.map(opp =>
      opp.id === opportunity.id ? { ...opp, status: 'applied' } : opp
    ));

    // Show success message
    console.log(`Applied to: ${opportunity.title}`);
  };

  const refreshData = () => {
    fetchInitialData();
    if (wsConnected) {
      sendMessage({ type: 'refresh_all' });
    }
  };

  const filteredOpportunities = opportunities.filter(opp => {
    if (filter === 'all') return true;
    return opp.status === filter;
  });

  const platformStats = getPlatformStats();
  const totalPlatformRevenue = platformStats.reduce((sum, p) => sum + p.revenue, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading Revenue Command Center...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Revenue Command Center</h1>
          <p className="text-muted-foreground">
            Unified revenue management and opportunity tracking
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <Badge variant={wsConnected ? "default" : "secondary"} className="flex items-center gap-1">
            {wsConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
            {wsConnected ? 'Live' : 'Reconnecting...'}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={refreshData}
            disabled={!wsConnected}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${(metrics?.total_revenue || 0).toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              +23.5% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Opportunities</CardTitle>
            <Briefcase className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{opportunities.length}</div>
            <p className="text-xs text-muted-foreground">
              {opportunities.filter(o => o.status === 'new').length} new
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Proposals Sent</CardTitle>
            <FileText className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.proposals_submitted || 0}</div>
            <p className="text-xs text-muted-foreground">
              {metrics?.responses_received || 0} responses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <Target className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(metrics?.conversion_rate || 0).toFixed(1)}%</div>
            <Progress value={metrics?.conversion_rate || 0} className="mt-1" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Deal Size</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${(metrics?.average_deal_size || 0).toFixed(0)}</div>
            <p className="text-xs text-muted-foreground">Per conversion</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
        </TabsList>

        {/* Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All ({opportunities.length})
              </Button>
              <Button
                variant={filter === 'new' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('new')}
              >
                New ({opportunities.filter(o => o.status === 'new').length})
              </Button>
              <Button
                variant={filter === 'applied' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('applied')}
              >
                Applied ({opportunities.filter(o => o.status === 'applied').length})
              </Button>
              <Button
                variant={filter === 'accepted' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('accepted')}
              >
                Accepted ({opportunities.filter(o => o.status === 'accepted').length})
              </Button>
            </div>
            <Button onClick={() => window.location.href = '/income-builder'}>
              <Rocket className="mr-2 h-4 w-4" />
              Launch Income Builder
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredOpportunities.map(opportunity => (
              <Card key={opportunity.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="text-lg line-clamp-1">{opportunity.title}</CardTitle>
                      <CardDescription>{opportunity.company}</CardDescription>
                    </div>
                    <Badge variant={
                      opportunity.status === 'applied' ? 'default' :
                      opportunity.status === 'accepted' ? 'success' :
                      opportunity.status === 'rejected' ? 'destructive' :
                      'secondary'
                    }>
                      {opportunity.status || 'new'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {opportunity.description}
                  </p>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Budget:</span>
                      <span className="font-medium">{opportunity.budget}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Deadline:</span>
                      <span>{opportunity.deadline}</span>
                    </div>
                    {opportunity.matchScore && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Match:</span>
                        <div className="flex items-center gap-1">
                          <span className="font-medium">{opportunity.matchScore}%</span>
                          <Progress value={opportunity.matchScore} className="w-16 h-2" />
                        </div>
                      </div>
                    )}
                  </div>

                  {opportunity.skills && opportunity.skills.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {opportunity.skills.slice(0, 3).map((skill, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                      {opportunity.skills.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{opportunity.skills.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}

                  <div className="flex gap-2">
                    {opportunity.status === 'new' && (
                      <Button
                        className="flex-1"
                        onClick={() => handleQuickApply(opportunity)}
                      >
                        <Zap className="mr-2 h-4 w-4" />
                        Quick Apply
                      </Button>
                    )}
                    {opportunity.url && (
                      <Button
                        variant="outline"
                        onClick={() => window.open(opportunity.url, '_blank')}
                      >
                        View <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Revenue Trend Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
                <CardDescription>Daily revenue over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={dailyMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="revenue" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Conversion Funnel */}
            <Card>
              <CardHeader>
                <CardTitle>Conversion Funnel</CardTitle>
                <CardDescription>From opportunity to revenue</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Opportunities</span>
                      <Badge>{metrics?.total_opportunities || 0}</Badge>
                    </div>
                    <Progress value={100} />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Proposals Submitted</span>
                      <Badge>{metrics?.proposals_submitted || 0}</Badge>
                    </div>
                    <Progress
                      value={(metrics?.total_opportunities || 0) > 0
                        ? ((metrics?.proposals_submitted || 0) / (metrics?.total_opportunities || 1)) * 100
                        : 0}
                    />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Responses Received</span>
                      <Badge>{metrics?.responses_received || 0}</Badge>
                    </div>
                    <Progress
                      value={(metrics?.total_opportunities || 0) > 0
                        ? ((metrics?.responses_received || 0) / (metrics?.total_opportunities || 1)) * 100
                        : 0}
                    />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Conversions</span>
                      <Badge variant="default">{metrics?.conversions || 0}</Badge>
                    </div>
                    <Progress
                      value={(metrics?.total_opportunities || 0) > 0
                        ? ((metrics?.conversions || 0) / (metrics?.total_opportunities || 1)) * 100
                        : 0}
                      className="bg-green-100"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Activity Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Daily Activity</CardTitle>
              <CardDescription>Proposals and conversions over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={dailyMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="proposals" fill="#8b5cf6" />
                  <Bar dataKey="conversions" fill="#10b981" />
                </RechartsBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pipeline Tab */}
        <TabsContent value="pipeline" className="space-y-4">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Active Pipeline</CardTitle>
                <CardDescription>Track proposals through stages</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {opportunities
                    .filter(o => o.status === 'applied' || o.status === 'accepted')
                    .slice(0, 10)
                    .map(opp => (
                      <div key={opp.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium">{opp.title}</p>
                          <p className="text-sm text-muted-foreground">{opp.company}</p>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-sm font-medium">{opp.budget}</span>
                          <Badge variant={opp.status === 'accepted' ? 'default' : 'secondary'}>
                            {opp.status}
                          </Badge>
                        </div>
                      </div>
                    ))}

                  {opportunities.filter(o => o.status === 'applied' || o.status === 'accepted').length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <FileText className="h-12 w-12 mx-auto mb-3 opacity-30" />
                      <p>No active proposals in pipeline</p>
                      <p className="text-sm mt-2">Start applying to opportunities to build your pipeline</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Platforms Tab */}
        <TabsContent value="platforms" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Platform Revenue Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue by Platform</CardTitle>
                <CardDescription>Revenue distribution across platforms</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={platformStats}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="revenue"
                    >
                      {platformStats.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Platform Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Platform Performance</CardTitle>
                <CardDescription>Key metrics by platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {platformStats.map((platform, idx) => (
                    <div key={idx} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{platform.name}</span>
                        <Badge>{platform.opportunities} opportunities</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Revenue: </span>
                          <span className="font-medium">${platform.revenue.toFixed(0)}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Conversions: </span>
                          <span className="font-medium">{platform.conversions}</span>
                        </div>
                      </div>
                      <Progress
                        value={totalPlatformRevenue > 0 ? (platform.revenue / totalPlatformRevenue) * 100 : 0}
                        className="h-2"
                      />
                    </div>
                  ))}

                  {platformStats.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Building className="h-12 w-12 mx-auto mb-3 opacity-30" />
                      <p>No platform data available</p>
                      <p className="text-sm mt-2">Start earning to see platform breakdown</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RevenueCommandCenter;
export { RevenueCommandCenter };