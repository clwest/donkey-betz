/**
 * Control Center - Unified Monitoring & Analytics
 *
 * Complete system oversight with real-time monitoring, performance analytics,
 * learning insights, and comprehensive dashboards.
 */

import React, { useState, useEffect } from 'react';
import {
  Shield,
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Cpu,
  HardDrive,
  Wifi,
  BarChart3,
  LineChart,
  PieChart,
  Target,
  Gauge,
  BrainCircuit,
  Lightbulb,
  AlertCircle,
  ChevronUp,
  ChevronDown,
  RefreshCw
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
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

interface SystemMetric {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'healthy' | 'warning' | 'critical';
}

interface Alert {
  id: string;
  level: 'info' | 'warning' | 'critical';
  category: string;
  message: string;
  timestamp: string;
}

interface LearningInsight {
  id: string;
  type: string;
  description: string;
  confidence: number;
  impact: number;
  recommendations: string[];
}

interface PerformanceData {
  timestamp: string;
  agents: number;
  workflows: number;
  success_rate: number;
  response_time: number;
}

const ControlCenter: React.FC = () => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetric[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [insights, setInsights] = useState<LearningInsight[]>([]);
  const [performanceHistory, setPerformanceHistory] = useState<PerformanceData[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<string>('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { sendMessage, lastMessage } = useWebSocket({
    url: '/ws/control/',
    onMessage: (data) => {
      console.log('Control Center received:', data);
      if (data.type === 'monitoring_update') {
        // Update system metrics
        if (data.system) {
          // Update system metrics state
          console.log('System update:', data.system);
        }
        if (data.alerts) {
          setAlerts(data.alerts);
        }
      } else if (data.type === 'insights') {
        setInsights(data.recent_insights || []);
      }
    }
  });

  useEffect(() => {
    // Initialize with mock data
    initializeMockData();

    // Set up auto-refresh
    if (autoRefresh) {
      const interval = setInterval(() => {
        updateMetrics();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const initializeMockData = () => {
    // Mock system metrics
    setSystemMetrics([
      { name: 'CPU Usage', value: 42, unit: '%', trend: 'stable', status: 'healthy' },
      { name: 'Memory', value: 68, unit: '%', trend: 'up', status: 'warning' },
      { name: 'Disk I/O', value: 23, unit: 'MB/s', trend: 'down', status: 'healthy' },
      { name: 'Network', value: 156, unit: 'KB/s', trend: 'up', status: 'healthy' },
      { name: 'Active Agents', value: 87, unit: '', trend: 'up', status: 'healthy' },
      { name: 'Success Rate', value: 94.5, unit: '%', trend: 'stable', status: 'healthy' }
    ]);

    // Mock alerts
    setAlerts([
      {
        id: '1',
        level: 'warning',
        category: 'Performance',
        message: 'Memory usage approaching threshold (68%)',
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        level: 'info',
        category: 'System',
        message: 'Workflow optimization completed successfully',
        timestamp: new Date().toISOString()
      }
    ]);

    // Mock insights
    setInsights([
      {
        id: '1',
        type: 'pattern',
        description: 'Content generation workflows show 23% improvement',
        confidence: 0.92,
        impact: 0.8,
        recommendations: [
          'Increase parallel processing for content tasks',
          'Cache frequently used templates'
        ]
      },
      {
        id: '2',
        type: 'optimization',
        description: 'Agent collaboration efficiency can be improved',
        confidence: 0.85,
        impact: 0.65,
        recommendations: [
          'Implement smart agent routing',
          'Pre-warm frequently used agent pairs'
        ]
      }
    ]);

    // Mock performance history
    const history: PerformanceData[] = [];
    for (let i = 24; i >= 0; i--) {
      const time = new Date();
      time.setHours(time.getHours() - i);
      history.push({
        timestamp: time.toISOString(),
        agents: 80 + Math.random() * 20,
        workflows: 150 + Math.random() * 50,
        success_rate: 90 + Math.random() * 8,
        response_time: 1.0 + Math.random() * 0.5
      });
    }
    setPerformanceHistory(history);
  };

  const updateMetrics = () => {
    // Simulate metric updates
    setSystemMetrics(prev => prev.map(metric => ({
      ...metric,
      value: metric.name === 'CPU Usage' ?
        Math.min(100, Math.max(0, metric.value + (Math.random() - 0.5) * 10)) :
        metric.value + (Math.random() - 0.5) * 5,
      trend: Math.random() > 0.5 ? 'up' : Math.random() > 0.5 ? 'down' : 'stable'
    })));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <ChevronUp className="w-4 h-4 text-green-500" />;
      case 'down': return <ChevronDown className="w-4 h-4 text-red-500" />;
      default: return <div className="w-4 h-4" />;
    }
  };

  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="w-8 h-8 text-green-600" />
            Control Center
          </h1>
          <p className="text-gray-600 mt-1">
            System monitoring, analytics, and insights
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={autoRefresh ? 'default' : 'outline'}>
            {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {systemMetrics.map(metric => (
          <Card key={metric.name} className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-600">{metric.name}</span>
                {getTrendIcon(metric.trend)}
              </div>
              <div className="flex items-baseline gap-1">
                <span className={`text-2xl font-bold ${getStatusColor(metric.status)}`}>
                  {metric.value.toFixed(metric.unit === '%' ? 1 : 0)}
                </span>
                <span className="text-sm text-gray-500">{metric.unit}</span>
              </div>
              {metric.name.includes('Usage') || metric.name.includes('Rate') ? (
                <Progress
                  value={metric.value}
                  className="mt-2 h-1"
                />
              ) : null}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Dashboard */}
      <Tabs defaultValue="monitoring" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="monitoring">
            <Activity className="w-4 h-4 mr-2" />
            Monitoring
          </TabsTrigger>
          <TabsTrigger value="analytics">
            <BarChart3 className="w-4 h-4 mr-2" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="insights">
            <Lightbulb className="w-4 h-4 mr-2" />
            AI Insights
          </TabsTrigger>
          <TabsTrigger value="alerts">
            <AlertCircle className="w-4 h-4 mr-2" />
            Alerts
          </TabsTrigger>
        </TabsList>

        <TabsContent value="monitoring" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Performance Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={performanceHistory.slice(-12)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(value) => new Date(value).getHours() + ':00'}
                    />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="success_rate"
                      stroke="#10b981"
                      fill="#10b98133"
                      name="Success Rate %"
                    />
                    <Area
                      type="monotone"
                      dataKey="agents"
                      stroke="#3b82f6"
                      fill="#3b82f633"
                      name="Active Agents"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Resource Usage */}
            <Card>
              <CardHeader>
                <CardTitle>Resource Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={[
                        { name: 'CPU', value: 42 },
                        { name: 'Memory', value: 68 },
                        { name: 'Disk', value: 23 },
                        { name: 'Network', value: 15 }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {COLORS.map((color, index) => (
                        <Cell key={`cell-${index}`} fill={color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Workflow Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Workflow Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={[
                  { name: 'Completed', value: 145, color: '#10b981' },
                  { name: 'Running', value: 23, color: '#3b82f6' },
                  { name: 'Pending', value: 12, color: '#f59e0b' },
                  { name: 'Failed', value: 3, color: '#ef4444' }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8b5cf6">
                    {[0, 1, 2, 3].map((index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Agent Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Top Performing Agents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { name: 'Content Writer', score: 95, tasks: 234 },
                    { name: 'Market Analyst', score: 92, tasks: 189 },
                    { name: 'Code Generator', score: 88, tasks: 156 },
                    { name: 'Data Processor', score: 85, tasks: 203 },
                    { name: 'Risk Manager', score: 83, tasks: 97 }
                  ].map(agent => (
                    <div key={agent.name} className="space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">{agent.name}</span>
                        <Badge variant="outline">{agent.tasks} tasks</Badge>
                      </div>
                      <Progress value={agent.score} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Income Streams */}
            <Card>
              <CardHeader>
                <CardTitle>Income Stream Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <RechartsPieChart>
                    <Pie
                      data={[
                        { name: 'Content', value: 3500 },
                        { name: 'Freelance', value: 2800 },
                        { name: 'Digital Products', value: 1200 },
                        { name: 'Automation', value: 900 },
                        { name: 'Consulting', value: 600 }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {COLORS.map((color, index) => (
                        <Cell key={`cell-${index}`} fill={color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `$${value}`} />
                  </RechartsPieChart>
                </ResponsiveContainer>
                <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                  {['Content', 'Freelance', 'Digital', 'Automation', 'Consulting'].map((item, i) => (
                    <div key={item} className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded`} style={{ backgroundColor: COLORS[i] }}></div>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Success Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Success Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Task Completion Rate</span>
                      <span className="font-bold">94.5%</span>
                    </div>
                    <Progress value={94.5} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Client Satisfaction</span>
                      <span className="font-bold">4.8/5.0</span>
                    </div>
                    <Progress value={96} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Revenue Growth</span>
                      <span className="font-bold text-green-600">+23%</span>
                    </div>
                    <Progress value={23} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Efficiency Score</span>
                      <span className="font-bold">87%</span>
                    </div>
                    <Progress value={87} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {insights.map(insight => (
              <Card key={insight.id}>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <BrainCircuit className="w-5 h-5 text-purple-600" />
                    {insight.type === 'pattern' ? 'Pattern Detected' : 'Optimization Found'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 mb-3">{insight.description}</p>
                  <div className="flex gap-4 mb-3">
                    <div>
                      <span className="text-xs text-gray-500">Confidence</span>
                      <Progress value={insight.confidence * 100} className="w-20 h-2 mt-1" />
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Impact</span>
                      <Progress value={insight.impact * 100} className="w-20 h-2 mt-1" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium mb-2">Recommendations:</p>
                    <ul className="space-y-1">
                      {insight.recommendations.map((rec, i) => (
                        <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <Button size="sm" className="mt-3">
                    Apply Optimization
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {alerts.map(alert => (
                  <Alert key={alert.id} className={
                    alert.level === 'critical' ? 'border-red-200' :
                    alert.level === 'warning' ? 'border-yellow-200' :
                    'border-blue-200'
                  }>
                    {alert.level === 'critical' ? <XCircle className="w-4 h-4" /> :
                     alert.level === 'warning' ? <AlertTriangle className="w-4 h-4" /> :
                     <AlertCircle className="w-4 h-4" />}
                    <AlertDescription>
                      <div className="flex justify-between items-start">
                        <div>
                          <Badge variant="outline" className="mb-1">
                            {alert.category}
                          </Badge>
                          <p className="text-sm">{alert.message}</p>
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </AlertDescription>
                  </Alert>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ControlCenter;