/**
 * Unified Command & Control Center
 *
 * Combines system monitoring, performance analytics, and monetization management
 * into a single comprehensive dashboard for complete platform oversight.
 */

import React, { useState, useEffect } from 'react';
import {
  Shield,
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  DollarSign,
  Clock,
  Cpu,
  HardDrive,
  Wifi,
  BarChart3,
  LineChart,
  Target,
  Gauge,
  BrainCircuit,
  Zap,
  Rocket,
  RefreshCw,
  Sparkles,
  ChevronDown
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useWebSocket } from '@/hooks/useWebSocket';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart as RechartsLineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface SystemMetric {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'healthy' | 'warning' | 'critical';
}

interface RevenueStream {
  id: string;
  name: string;
  category: string;
  potential: string;
  status: 'active' | 'pending' | 'available';
  earnings?: number;
  progress?: number;
}

interface SystemAlert {
  id: string;
  level: 'info' | 'warning' | 'critical';
  category: string;
  message: string;
  timestamp: string;
}

const UnifiedCommandCenter: React.FC = () => {
  // System Monitoring State
  const [systemMetrics, setSystemMetrics] = useState<SystemMetric[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [systemStatus, setSystemStatus] = useState<'healthy' | 'warning' | 'critical'>('healthy');

  // Monetization State
  const [revenueStreams, setRevenueStreams] = useState<RevenueStream[]>([]);
  const [totalEarnings, setTotalEarnings] = useState(0);
  const [activeStreams, setActiveStreams] = useState(0);
  const [monthlyRecurring, setMonthlyRecurring] = useState(0);

  // Performance State
  const [agentCount, setAgentCount] = useState(149);
  const [advisorCount, setAdvisorCount] = useState(25);
  const [successRate, setSuccessRate] = useState(87.5);
  const [activeWorkflows, setActiveWorkflows] = useState(0);

  const [autoRefresh, setAutoRefresh] = useState(true);

  // WebSocket connection for real-time updates
  const { sendMessage, lastMessage, isConnected } = useWebSocket({
    url: '/ws/control/',
    onMessage: (data) => {
      if (data.type === 'system_metrics') {
        setSystemMetrics(data.metrics);
      } else if (data.type === 'alerts') {
        setAlerts(data.alerts);
      } else if (data.type === 'revenue_update') {
        setTotalEarnings(data.total_revenue);
        setActiveStreams(data.active_streams);
      } else if (data.type === 'performance_update') {
        setSuccessRate(data.success_rate);
        setActiveWorkflows(data.active_workflows);
      }
    },
    onOpen: () => {
      console.log('Command Center connected');
      sendMessage({ type: 'subscribe', channels: ['system', 'revenue', 'performance'] });
    }
  });

  // Initialize with real data
  useEffect(() => {
    fetchSystemStatus();
    fetchRevenueData();

    // Initialize revenue streams
    setRevenueStreams(generateMockStreams());

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchSystemStatus();
        fetchRevenueData();
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchSystemStatus = async () => {
    // System status endpoint doesn't exist yet, use mock data for now
    setSystemMetrics([
      { name: 'CPU Usage', value: 45, unit: '%', trend: 'stable', status: 'healthy' },
      { name: 'Memory', value: 62, unit: '%', trend: 'up', status: 'healthy' },
      { name: 'API Latency', value: 124, unit: 'ms', trend: 'stable', status: 'healthy' },
      { name: 'Queue Size', value: 8, unit: ' tasks', trend: 'down', status: 'healthy' }
    ]);
    setSystemStatus('healthy');
  };

  const fetchRevenueData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/intelligence/revenue/metrics/?days=30');
      if (response.ok) {
        const data = await response.json();
        if (data.metrics) {
          setTotalEarnings(data.metrics.total_revenue || 0);
          setActiveStreams(data.metrics.total_opportunities || 0);
        }
      }
    } catch (error) {
      console.error('Error fetching revenue data:', error);
    }
  };

  const handleActivateStream = async (streamId: string) => {
    sendMessage({ type: 'activate_stream', stream_id: streamId });
    // Update UI optimistically
    setRevenueStreams(prev =>
      prev.map(s => s.id === streamId ? { ...s, status: 'active' as const } : s)
    );
    setActiveStreams(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Unified Command Center</h1>
          <p className="text-muted-foreground">Complete system oversight & monetization control</p>
        </div>
        <div className="flex gap-2">
          <Badge variant={isConnected ? "default" : "secondary"} className="flex items-center gap-1">
            {isConnected ? <Wifi className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
            {isConnected ? 'Live' : 'Disconnected'}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Top Level Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Shield className={`h-4 w-4 ${systemStatus === 'healthy' ? 'text-green-500' : 'text-yellow-500'}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{systemStatus}</div>
            <p className="text-xs text-muted-foreground">All systems operational</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalEarnings.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">+23.5% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <BrainCircuit className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agentCount}</div>
            <p className="text-xs text-muted-foreground">{advisorCount} advisors</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <Target className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{successRate.toFixed(1)}%</div>
            <Progress value={successRate} className="mt-1" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
            <Activity className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeWorkflows}</div>
            <p className="text-xs text-muted-foreground">{activeStreams} revenue streams</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="monetization">Monetization</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="system">System Health</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Revenue Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
                <CardDescription>30-day revenue performance</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={generateMockRevenueData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="revenue" stroke="#8884d8" fill="#8884d8" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* System Performance */}
            <Card>
              <CardHeader>
                <CardTitle>System Performance</CardTitle>
                <CardDescription>Real-time metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">CPU Usage</span>
                      <span className="text-sm">45%</span>
                    </div>
                    <Progress value={45} />
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Memory</span>
                      <span className="text-sm">62%</span>
                    </div>
                    <Progress value={62} />
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">API Latency</span>
                      <span className="text-sm">124ms</span>
                    </div>
                    <Progress value={24} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Queue Size</span>
                      <span className="text-sm">8 tasks</span>
                    </div>
                    <Progress value={16} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Button onClick={() => window.location.href = '/income-builder'}>
                  <Rocket className="mr-2 h-4 w-4" />
                  Launch Income Builder
                </Button>
                <Button variant="outline" onClick={() => window.location.href = '/neural-orchestra'}>
                  <BrainCircuit className="mr-2 h-4 w-4" />
                  Neural Orchestra
                </Button>
                <Button variant="outline" onClick={() => window.location.href = '/decision-command'}>
                  <Target className="mr-2 h-4 w-4" />
                  Decision Command
                </Button>
                <Button variant="outline" onClick={() => sendMessage({ type: 'run_diagnostics' })}>
                  <Activity className="mr-2 h-4 w-4" />
                  Run Diagnostics
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Monetization Tab */}
        <TabsContent value="monetization" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Monthly Recurring</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">${monthlyRecurring.toLocaleString()}</div>
                <p className="text-sm text-muted-foreground">Predictable income</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Pipeline Value</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">$48,500</div>
                <p className="text-sm text-muted-foreground">Potential next 30 days</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Conversion Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">23.8%</div>
                <Progress value={23.8} className="mt-2" />
              </CardContent>
            </Card>
          </div>

          {/* Revenue Streams */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {generateMockStreams().map(stream => (
              <Card key={stream.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{stream.name}</CardTitle>
                      <CardDescription>{stream.category}</CardDescription>
                    </div>
                    <Badge variant={stream.status === 'active' ? 'default' : 'secondary'}>
                      {stream.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Potential:</span>
                      <span className="font-bold">{stream.potential}</span>
                    </div>
                    {stream.earnings && (
                      <div className="flex justify-between text-sm">
                        <span>Earned:</span>
                        <span className="font-bold text-green-600">${stream.earnings}</span>
                      </div>
                    )}
                  </div>

                  {stream.progress && (
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span>Progress</span>
                        <span>{stream.progress}%</span>
                      </div>
                      <Progress value={stream.progress} />
                    </div>
                  )}

                  {stream.status === 'available' && (
                    <Button
                      className="w-full"
                      onClick={() => handleActivateStream(stream.id)}
                    >
                      <Sparkles className="mr-2 h-4 w-4" />
                      Activate
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Agent Performance</CardTitle>
                <CardDescription>Success rates by agent category</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={generateAgentPerformanceData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="success_rate" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* System Health Tab */}
        <TabsContent value="system" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {systemMetrics.map((metric, idx) => (
              <Card key={idx}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">{metric.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">
                      {metric.value}{metric.unit}
                    </span>
                    <Badge variant={
                      metric.status === 'healthy' ? 'default' :
                      metric.status === 'warning' ? 'secondary' : 'destructive'
                    }>
                      {metric.status}
                    </Badge>
                  </div>
                  <div className="flex items-center mt-2 text-sm text-muted-foreground">
                    {metric.trend === 'up' ? <TrendingUp className="h-4 w-4 mr-1" /> :
                     metric.trend === 'down' ? <ChevronDown className="h-4 w-4 mr-1" /> :
                     <Activity className="h-4 w-4 mr-1" />}
                    {metric.trend}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-4">
          {alerts.length === 0 ? (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                No active alerts. All systems operating normally.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-2">
              {alerts.map(alert => (
                <Alert key={alert.id} variant={alert.level === 'critical' ? 'destructive' : 'default'}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="flex justify-between items-start">
                      <div>
                        <Badge className="mr-2">{alert.category}</Badge>
                        {alert.message}
                      </div>
                      <span className="text-xs text-muted-foreground">{alert.timestamp}</span>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Helper functions for mock data
function generateMockRevenueData() {
  const data = [];
  for (let i = 29; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      revenue: Math.floor(Math.random() * 1000) + 500
    });
  }
  return data;
}

function generateMockStreams(): RevenueStream[] {
  return [
    {
      id: 'ai-content',
      name: 'AI Content Creation',
      category: 'Content',
      potential: '$2,000-$5,000',
      status: 'active',
      earnings: 1850,
      progress: 73
    },
    {
      id: 'automation',
      name: 'Workflow Automation',
      category: 'Automation',
      potential: '$3,000-$8,000',
      status: 'active',
      earnings: 3200,
      progress: 45
    },
    {
      id: 'consulting',
      name: 'AI Consulting',
      category: 'Services',
      potential: '$5,000-$15,000',
      status: 'pending',
      progress: 15
    },
    {
      id: 'templates',
      name: 'Template Marketplace',
      category: 'Digital Products',
      potential: '$1,000-$3,000',
      status: 'available'
    },
    {
      id: 'data-analysis',
      name: 'Data Analysis Services',
      category: 'Analytics',
      potential: '$2,500-$7,000',
      status: 'available'
    },
    {
      id: 'trading-bots',
      name: 'Trading Bot Development',
      category: 'Finance',
      potential: '$10,000-$50,000',
      status: 'available'
    }
  ];
}

function generateAgentPerformanceData() {
  return [
    { category: 'Content', success_rate: 92 },
    { category: 'Research', success_rate: 88 },
    { category: 'Analysis', success_rate: 85 },
    { category: 'Trading', success_rate: 78 },
    { category: 'Automation', success_rate: 94 }
  ];
}

export default UnifiedCommandCenter;
export { UnifiedCommandCenter };