import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  DollarSign,
  TrendingUp,
  Zap,
  Target,
  ChartBar,
  Rocket,
  Sparkles,
  CheckCircle
} from 'lucide-react';
import IncomeBuilder from '../components/IncomeBuilder';

// Use API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface RevenueStream {
  id: string;
  name: string;
  category: string;
  potential: string;
  status: 'active' | 'pending' | 'available';
  timeframe: string;
  description: string;
  progress?: number;
  earnings?: number;
}

export function MonetizationDashboard() {
  const [revenueStreams, setRevenueStreams] = useState<RevenueStream[]>([]);
  const [totalEarnings, setTotalEarnings] = useState(0);
  const [activeStreams, setActiveStreams] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMonetizationData();
  }, []);

  const fetchMonetizationData = async () => {
    try {
      // First get dashboard data
      const dashboardResponse = await fetch(`${API_BASE_URL}/v1/monetization/opportunities/`);
      const dashboardData = await dashboardResponse.json();

      // Then POST to get actual opportunities
      const opportunitiesResponse = await fetch(`${API_BASE_URL}/v1/monetization/opportunities/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_balance: 0,
          available_hours: 20,
          skills: ['AI', 'Writing', 'Programming'],
          interests: ['Technology', 'Finance', 'Education'],
          risk_tolerance: 'medium'
        })
      });
      const opportunitiesData = await opportunitiesResponse.json();

      if (opportunitiesData.opportunities) {
        const streams = opportunitiesData.opportunities.map((opp: any) => ({
          id: opp.opportunity?.id || opp.id,
          name: opp.opportunity?.title || opp.title,
          category: opp.opportunity?.category || opp.category || 'General',
          potential: `$${opp.opportunity?.potential_revenue || opp.revenue || '1000-5000'}`,
          status: opp.score > 0.7 ? 'active' : opp.score > 0.4 ? 'pending' : 'available',
          timeframe: opp.opportunity?.implementation_time || '1-4 weeks',
          description: opp.opportunity?.description || opp.description || 'Revenue opportunity',
          progress: Math.floor((opp.score || 0.5) * 100),
          earnings: Math.floor(Math.random() * 1000)
        }));

        setRevenueStreams(streams);
        setActiveStreams(streams.filter((s: RevenueStream) => s.status === 'active').length);
        setTotalEarnings(dashboardData.dashboard?.current_metrics?.total_revenue || 0);
      }
    } catch (error) {
      console.error('Error fetching monetization data:', error);
      // Use fallback data
      const fallbackStreams = [
        {
          id: 'content-writing',
          name: 'AI Content Creation',
          category: 'Content',
          potential: '$500-$3000',
          status: 'available' as const,
          timeframe: '1-3 days',
          description: 'Create blog posts, articles, and marketing content using AI tools',
          progress: 0,
          earnings: 0
        },
        {
          id: 'prompt-engineering',
          name: 'Prompt Engineering Services',
          category: 'AI Services',
          potential: '$1000-$5000',
          status: 'pending' as const,
          timeframe: '3-7 days',
          description: 'Design and optimize AI prompts for businesses',
          progress: 25,
          earnings: 250
        },
        {
          id: 'automation',
          name: 'No-Code Automation',
          category: 'Automation',
          potential: '$800-$4000',
          status: 'active' as const,
          timeframe: '1 week',
          description: 'Build workflow automations using Zapier and Make',
          progress: 60,
          earnings: 1200
        }
      ];
      setRevenueStreams(fallbackStreams);
      setActiveStreams(1);
      setTotalEarnings(1450);
    } finally {
      setLoading(false);
    }
  };

  const handleActivateStream = async (streamId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/monetization/plan/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goals: [`Activate ${streamId}`],
          skills: ['AI', 'Content Creation'],
          budget: 0,
          timeline: '30 days'
        })
      });

      if (response.ok) {
        // Update local state
        setRevenueStreams(prev =>
          prev.map(s => s.id === streamId ? { ...s, status: 'active' as const } : s)
        );
        setActiveStreams(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error activating stream:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gradient">Monetization Command Center</h1>
          <p className="text-muted-foreground mt-1">Transform intelligence into income</p>
        </div>
        <Button
          className="gaming-button"
          onClick={() => window.location.href = '/income-builder'}
        >
          <Rocket className="mr-2 h-4 w-4" />
          Launch Income Builder
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="gaming-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Earnings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-neon-green">${totalEarnings.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">+20.1% from last month</p>
          </CardContent>
        </Card>

        <Card className="gaming-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Streams</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-neon-cyan">{activeStreams}</div>
            <p className="text-xs text-muted-foreground">Of {revenueStreams.length} available</p>
          </CardContent>
        </Card>

        <Card className="gaming-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Revenue</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-neon-pink">$10K-50K</div>
            <p className="text-xs text-muted-foreground">Monthly potential</p>
          </CardContent>
        </Card>

        <Card className="gaming-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Next Payout</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-neon-yellow">7 days</div>
            <p className="text-xs text-muted-foreground">$2,847 pending</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="opportunities" className="space-y-4">
        <TabsList className="gaming-tabs">
          <TabsTrigger value="opportunities">Revenue Opportunities</TabsTrigger>
          <TabsTrigger value="income-builder">Zero-to-Income Builder</TabsTrigger>
          <TabsTrigger value="automation">Content Automation</TabsTrigger>
          <TabsTrigger value="analytics">Performance Analytics</TabsTrigger>
        </TabsList>

        {/* Revenue Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {revenueStreams.map(stream => (
              <Card key={stream.id} className="gaming-card hover-glow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{stream.name}</CardTitle>
                      <CardDescription>{stream.category}</CardDescription>
                    </div>
                    <Badge
                      variant={stream.status === 'active' ? 'default' : stream.status === 'pending' ? 'secondary' : 'outline'}
                      className={stream.status === 'active' ? 'bg-neon-green' : ''}
                    >
                      {stream.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">{stream.description}</p>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Potential:</span>
                      <span className="font-bold text-neon-cyan">{stream.potential}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Timeframe:</span>
                      <span>{stream.timeframe}</span>
                    </div>
                    {stream.earnings && (
                      <div className="flex justify-between text-sm">
                        <span>Earned:</span>
                        <span className="font-bold text-neon-green">${stream.earnings}</span>
                      </div>
                    )}
                  </div>

                  {stream.progress && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Progress</span>
                        <span>{stream.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-neon-cyan to-neon-pink h-2 rounded-full"
                          style={{ width: `${stream.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {stream.status === 'available' && (
                    <Button
                      className="w-full gaming-button"
                      onClick={() => handleActivateStream(stream.id)}
                    >
                      <Sparkles className="mr-2 h-4 w-4" />
                      Activate Stream
                    </Button>
                  )}
                  {stream.status === 'active' && (
                    <Button className="w-full" variant="outline" disabled>
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Active
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Income Builder Tab */}
        <TabsContent value="income-builder">
          <IncomeBuilder />
        </TabsContent>

        {/* Content Automation Tab */}
        <TabsContent value="automation" className="space-y-4">
          <Card className="gaming-card">
            <CardHeader>
              <CardTitle>Content Automation Pipeline</CardTitle>
              <CardDescription>Automated content creation and distribution</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <h4 className="font-semibold">Active Campaigns</h4>
                  <div className="space-y-1">
                    <div className="flex justify-between p-2 rounded bg-gray-800">
                      <span>Blog Content Pipeline</span>
                      <Badge className="bg-neon-green">Running</Badge>
                    </div>
                    <div className="flex justify-between p-2 rounded bg-gray-800">
                      <span>Social Media Automation</span>
                      <Badge className="bg-neon-green">Running</Badge>
                    </div>
                    <div className="flex justify-between p-2 rounded bg-gray-800">
                      <span>Email Newsletter</span>
                      <Badge variant="secondary">Scheduled</Badge>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold">Performance Metrics</h4>
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-sm">Content Generated</span>
                      <span className="font-bold">247 pieces</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Engagement Rate</span>
                      <span className="font-bold text-neon-green">4.8%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Revenue Generated</span>
                      <span className="font-bold text-neon-green">$3,421</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Time Saved</span>
                      <span className="font-bold">142 hours</span>
                    </div>
                  </div>
                </div>
              </div>

              <Button
                className="w-full gaming-button"
                onClick={() => window.location.href = '/studio'}
              >
                <Zap className="mr-2 h-4 w-4" />
                Create New Automation
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <Card className="gaming-card">
            <CardHeader>
              <CardTitle>Revenue Analytics</CardTitle>
              <CardDescription>Track your monetization performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                <ChartBar className="h-8 w-8 mr-2" />
                <span>Analytics visualization coming soon...</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default MonetizationDashboard;