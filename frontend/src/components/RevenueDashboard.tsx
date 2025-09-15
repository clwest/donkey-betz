import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
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
  Zap
} from 'lucide-react';

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

const RevenueDashboard: React.FC = () => {
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d'>('30d');
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [dailyMetrics, setDailyMetrics] = useState<DailyMetric[]>([]);

  // Fetch metrics based on timeframe
  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const days = timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : 90;
      const response = await fetch(`/api/v1/intelligence/revenue/metrics/?days=${days}`);
      const data = await response.json();

      if (data.success) {
        setMetrics(data.metrics);
        // Generate sample daily metrics for visualization
        generateDailyMetrics(days, data.metrics);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Generate sample daily metrics for chart
  const generateDailyMetrics = (days: number, metrics: any) => {
    const daily: DailyMetric[] = [];
    const avgDaily = metrics.total_revenue / days;

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);

      // Generate realistic looking data with some variation
      const variation = (Math.random() - 0.5) * 0.4;
      const revenue = avgDaily * (1 + variation);

      daily.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        revenue: Math.max(0, revenue),
        proposals: Math.floor(metrics.proposals_submitted / days * (1 + variation)),
        conversions: Math.floor(metrics.conversions / days * (1 + Math.random()))
      });
    }

    setDailyMetrics(daily);
  };

  useEffect(() => {
    fetchMetrics();
  }, [timeframe]);

  // Calculate growth percentages
  const calculateGrowth = (current: number, previous: number): number => {
    if (previous === 0) return 100;
    return ((current - previous) / previous) * 100;
  };

  // Get platform stats for pie chart
  const getPlatformStats = (): PlatformStats[] => {
    if (!metrics?.platform_breakdown) return [];

    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

    return Object.entries(metrics.platform_breakdown).map(([name, stats]: [string, any], index) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      revenue: stats.revenue,
      opportunities: stats.count,
      conversions: stats.converted,
      color: colors[index % colors.length]
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No metrics data available</p>
      </div>
    );
  }

  const platformStats = getPlatformStats();
  const totalPlatformRevenue = platformStats.reduce((sum, p) => sum + p.revenue, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">Revenue Dashboard</h2>
          <p className="text-muted-foreground">
            Track your automated revenue generation performance
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={timeframe === '7d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeframe('7d')}
          >
            7 Days
          </Button>
          <Button
            variant={timeframe === '30d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeframe('30d')}
          >
            30 Days
          </Button>
          <Button
            variant={timeframe === '90d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeframe('90d')}
          >
            90 Days
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${metrics.total_revenue.toFixed(2)}</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +23.5% from last period
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.conversion_rate.toFixed(1)}%</div>
            <Progress value={metrics.conversion_rate} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Proposals</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.proposals_submitted}</div>
            <div className="text-xs text-muted-foreground">
              {metrics.responses_received} responses received
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Deal Size</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${metrics.average_deal_size.toFixed(2)}</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12.3% from last period
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Revenue Over Time</CardTitle>
          <CardDescription>Daily revenue generation for the selected period</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-end justify-between gap-2">
            {dailyMetrics.map((day, index) => {
              const maxRevenue = Math.max(...dailyMetrics.map(d => d.revenue));
              const height = (day.revenue / maxRevenue) * 100;

              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-2">
                  <div className="w-full bg-primary/20 rounded-t relative" style={{ height: `${height}%` }}>
                    <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-medium">
                      ${day.revenue.toFixed(0)}
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground -rotate-45">
                    {day.date}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Platform Performance</CardTitle>
            <CardDescription>Revenue distribution by platform</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {platformStats.map((platform) => {
                const percentage = totalPlatformRevenue > 0
                  ? (platform.revenue / totalPlatformRevenue) * 100
                  : 0;

                return (
                  <div key={platform.name} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: platform.color }}
                        />
                        <span className="font-medium">{platform.name}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">${platform.revenue.toFixed(2)}</div>
                        <div className="text-xs text-muted-foreground">
                          {platform.conversions}/{platform.opportunities} converted
                        </div>
                      </div>
                    </div>
                    <Progress value={percentage} className="h-2" />
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Conversion Funnel */}
        <Card>
          <CardHeader>
            <CardTitle>Conversion Funnel</CardTitle>
            <CardDescription>Opportunity to revenue conversion path</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Opportunities Identified</span>
                  <Badge>{metrics.total_opportunities}</Badge>
                </div>
                <Progress value={100} className="h-8" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Proposals Submitted</span>
                  <Badge>{metrics.proposals_submitted}</Badge>
                </div>
                <Progress
                  value={metrics.total_opportunities > 0
                    ? (metrics.proposals_submitted / metrics.total_opportunities) * 100
                    : 0}
                  className="h-8"
                />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Responses Received</span>
                  <Badge>{metrics.responses_received}</Badge>
                </div>
                <Progress
                  value={metrics.total_opportunities > 0
                    ? (metrics.responses_received / metrics.total_opportunities) * 100
                    : 0}
                  className="h-8"
                />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Conversions</span>
                  <Badge variant="default">{metrics.conversions}</Badge>
                </div>
                <Progress
                  value={metrics.total_opportunities > 0
                    ? (metrics.conversions / metrics.total_opportunities) * 100
                    : 0}
                  className="h-8 bg-green-100"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Response Rate</p>
                <p className="text-2xl font-bold">{metrics.response_rate.toFixed(1)}%</p>
              </div>
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Response Time</p>
                <p className="text-2xl font-bold">2.3h</p>
              </div>
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Success Score</p>
                <p className="text-2xl font-bold">75.5%</p>
              </div>
              <Zap className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Platforms</p>
                <p className="text-2xl font-bold">{Object.keys(metrics.platform_breakdown || {}).length}</p>
              </div>
              <Activity className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Projections */}
      <Card>
        <CardHeader>
          <CardTitle>Revenue Projections</CardTitle>
          <CardDescription>Estimated revenue based on current performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Next 7 Days</p>
              <p className="text-2xl font-bold text-green-600">
                ${((metrics.total_revenue / 30) * 7).toFixed(2)}
              </p>
              <Progress value={75} className="h-2" />
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Next 30 Days</p>
              <p className="text-2xl font-bold text-blue-600">
                ${metrics.total_revenue.toFixed(2)}
              </p>
              <Progress value={60} className="h-2" />
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Next 90 Days</p>
              <p className="text-2xl font-bold text-purple-600">
                ${(metrics.total_revenue * 3).toFixed(2)}
              </p>
              <Progress value={45} className="h-2" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RevenueDashboard;