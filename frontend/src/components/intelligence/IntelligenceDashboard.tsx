import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Brain, Target, Activity, TrendingUp, Zap, Shield,
  BarChart3, Globe, Sparkles, Eye, RefreshCw, Settings,
  AlertTriangle, CheckCircle, Clock, DollarSign
} from 'lucide-react';

// Import our new intelligence components
import { RealTimeIntelligencePanel } from './RealTimeIntelligencePanel';
import { LiveOpportunityStream } from './LiveOpportunityStream';
import { IntelligencePanel } from './IntelligencePanel';

interface DashboardMetrics {
  totalOpportunities: number;
  activePredictions: number;
  successRate: number;
  totalProfit: number;
  avgEdge: number;
  agentCount: number;
}

interface SystemHealth {
  skynet: 'ONLINE' | 'OFFLINE' | 'INITIALIZING';
  intelligence_engine: 'ACTIVE' | 'INACTIVE';
  websocket: 'CONNECTED' | 'DISCONNECTED';
  api: 'AVAILABLE' | 'UNAVAILABLE';
}

export function IntelligenceDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalOpportunities: 0,
    activePredictions: 0,
    successRate: 0,
    totalProfit: 0,
    avgEdge: 0,
    agentCount: 102
  });
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    skynet: 'INITIALIZING',
    intelligence_engine: 'INACTIVE',
    websocket: 'DISCONNECTED',
    api: 'UNAVAILABLE'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize dashboard with system check
    const initializeDashboard = async () => {
      try {
        // Check Skynet status
        const skynetResponse = await fetch('/api/v1/intelligence/skynet/status/');
        if (skynetResponse.ok) {
          const skynetData = await skynetResponse.json();
          setSystemHealth(prev => ({
            ...prev,
            skynet: skynetData.skynet_status || 'OFFLINE',
            intelligence_engine: skynetData.intelligence_engine || 'INACTIVE',
            api: 'AVAILABLE'
          }));

          setMetrics(prev => ({
            ...prev,
            totalOpportunities: skynetData.live_opportunities || 0,
            activePredictions: skynetData.live_predictions || 0
          }));
        }

        // Check opportunities
        const oppResponse = await fetch('/api/v1/intelligence/opportunities/');
        if (oppResponse.ok) {
          const oppData = await oppResponse.json();
          if (oppData.opportunities) {
            setMetrics(prev => ({
              ...prev,
              totalOpportunities: oppData.count || 0
            }));
          }
        }

        // Check predictions
        const predResponse = await fetch('/api/v1/intelligence/predictions/');
        if (predResponse.ok) {
          const predData = await predResponse.json();
          if (predData.predictions) {
            setMetrics(prev => ({
              ...prev,
              activePredictions: predData.count || 0
            }));
          }
        }

        setLoading(false);
      } catch (error) {
        console.error('Failed to initialize intelligence dashboard:', error);
        setSystemHealth(prev => ({
          ...prev,
          api: 'UNAVAILABLE'
        }));
        setLoading(false);
      }
    };

    initializeDashboard();
  }, []);

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'ONLINE':
      case 'ACTIVE':
      case 'CONNECTED':
      case 'AVAILABLE':
        return 'text-green-500';
      case 'INITIALIZING':
        return 'text-yellow-500';
      case 'OFFLINE':
      case 'INACTIVE':
      case 'DISCONNECTED':
      case 'UNAVAILABLE':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'ONLINE':
      case 'ACTIVE':
      case 'CONNECTED':
      case 'AVAILABLE':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'INITIALIZING':
        return <RefreshCw className="h-4 w-4 text-yellow-500 animate-spin" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center space-y-4">
            <Brain className="h-16 w-16 mx-auto text-blue-500 animate-pulse" />
            <h2 className="text-2xl font-bold">Initializing Intelligence Dashboard</h2>
            <p className="text-gray-400">Connecting to Skynet Intelligence Engine...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
              Intelligence Dashboard
            </h1>
            <p className="text-gray-400 mt-2">
              Real-time AI intelligence and market opportunity detection
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Configure
            </Button>
            <Button size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh All
            </Button>
          </div>
        </div>

        {/* Quick Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
          <Card className="gaming-card">
            <CardContent className="p-4 text-center">
              <Target className="h-6 w-6 mx-auto mb-2 text-green-500" />
              <p className="text-2xl font-bold text-green-500">{metrics.totalOpportunities}</p>
              <p className="text-sm text-gray-400">Live Opportunities</p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4 text-center">
              <Sparkles className="h-6 w-6 mx-auto mb-2 text-purple-500" />
              <p className="text-2xl font-bold text-purple-500">{metrics.activePredictions}</p>
              <p className="text-sm text-gray-400">Active Predictions</p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4 text-center">
              <TrendingUp className="h-6 w-6 mx-auto mb-2 text-blue-500" />
              <p className="text-2xl font-bold text-blue-500">{metrics.avgEdge.toFixed(1)}%</p>
              <p className="text-sm text-gray-400">Avg Edge</p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4 text-center">
              <DollarSign className="h-6 w-6 mx-auto mb-2 text-green-500" />
              <p className="text-2xl font-bold text-green-500">
                ${metrics.totalProfit.toLocaleString()}
              </p>
              <p className="text-sm text-gray-400">Profit Potential</p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4 text-center">
              <BarChart3 className="h-6 w-6 mx-auto mb-2 text-yellow-500" />
              <p className="text-2xl font-bold text-yellow-500">{metrics.successRate}%</p>
              <p className="text-sm text-gray-400">Success Rate</p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4 text-center">
              <Activity className="h-6 w-6 mx-auto mb-2 text-blue-500" />
              <p className="text-2xl font-bold text-blue-500">{metrics.agentCount}</p>
              <p className="text-sm text-gray-400">Active Agents</p>
            </CardContent>
          </Card>
        </div>

        {/* System Health */}
        <Card className="gaming-card mb-6 border-blue-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-500" />
              System Health Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center justify-between p-3 rounded border border-gray-700/50">
                <div>
                  <p className="font-medium">Skynet Engine</p>
                  <p className={`text-sm ${getHealthColor(systemHealth.skynet)}`}>
                    {systemHealth.skynet}
                  </p>
                </div>
                {getHealthIcon(systemHealth.skynet)}
              </div>

              <div className="flex items-center justify-between p-3 rounded border border-gray-700/50">
                <div>
                  <p className="font-medium">Intelligence Core</p>
                  <p className={`text-sm ${getHealthColor(systemHealth.intelligence_engine)}`}>
                    {systemHealth.intelligence_engine}
                  </p>
                </div>
                {getHealthIcon(systemHealth.intelligence_engine)}
              </div>

              <div className="flex items-center justify-between p-3 rounded border border-gray-700/50">
                <div>
                  <p className="font-medium">WebSocket</p>
                  <p className={`text-sm ${getHealthColor(systemHealth.websocket)}`}>
                    {systemHealth.websocket}
                  </p>
                </div>
                {getHealthIcon(systemHealth.websocket)}
              </div>

              <div className="flex items-center justify-between p-3 rounded border border-gray-700/50">
                <div>
                  <p className="font-medium">API Services</p>
                  <p className={`text-sm ${getHealthColor(systemHealth.api)}`}>
                    {systemHealth.api}
                  </p>
                </div>
                {getHealthIcon(systemHealth.api)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid grid-cols-4 w-full max-w-2xl">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="opportunities">Live Stream</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <RealTimeIntelligencePanel />
        </TabsContent>

        {/* Live Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-6">
          <LiveOpportunityStream />
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions" className="space-y-6">
          <Card className="gaming-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
                AI Prediction Engine
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Brain className="h-16 w-16 mx-auto mb-4 text-purple-500 opacity-50" />
                <h3 className="text-xl font-bold mb-2">Advanced Predictions Coming Soon</h3>
                <p className="text-gray-400 mb-4">
                  Multi-domain predictive analytics with cross-market pattern recognition
                </p>
                <Button>
                  <Eye className="h-4 w-4 mr-2" />
                  View Prediction Models
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <Card className="gaming-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-500" />
                Intelligence Analytics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <BarChart3 className="h-16 w-16 mx-auto mb-4 text-blue-500 opacity-50" />
                <h3 className="text-xl font-bold mb-2">Advanced Analytics Dashboard</h3>
                <p className="text-gray-400 mb-4">
                  Performance metrics, success rates, and profitability analysis
                </p>
                <Button>
                  <TrendingUp className="h-4 w-4 mr-2" />
                  View Analytics
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* System Alerts */}
      {systemHealth.api === 'UNAVAILABLE' && (
        <Alert variant="destructive" className="mt-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Intelligence API is unavailable. Some features may not work correctly.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}