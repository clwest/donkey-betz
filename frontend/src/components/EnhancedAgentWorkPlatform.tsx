import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { EnhancedButton as Button } from './ui/enhanced-button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';

interface AgentWorker {
  name: string;
  skills: string[];
  hourly_rate: number;
  current_workload: number;
  max_concurrent: number;
  total_earned?: number;
}

interface WorkSession {
  session_id: string;
  agent_name: string;
  job_title: string;
  hourly_rate: number;
  hours_worked: number;
  revenue_generated: number;
}

interface PlatformStatus {
  total_agents: number;
  agents_working: number;
  active_sessions: WorkSession[];
  total_revenue: number;
  daily_revenue_potential: number;
  utilization_rate: number;
  agent_breakdown?: AgentWorker[];
}

const EnhancedAgentWorkPlatform: React.FC = () => {
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus | null>(null);
  const [activeSessions, setActiveSessions] = useState<WorkSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [activating, setActivating] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [totalRevenue, setTotalRevenue] = useState(0);
  const [revenueAnimation, setRevenueAnimation] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    setConnectionStatus('connecting');
    const backendHost = 'localhost:8000';
    const ws = new WebSocket(`ws://${backendHost}/ws/agent-platform/`);

    ws.onopen = () => {
      console.log('✅ WebSocket connected to Agent Platform');
      setConnectionStatus('connected');
      ws.send(JSON.stringify({ action: 'get_platform_status' }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📊 Platform update:', data);
        setLastUpdate(new Date().toLocaleTimeString());

        switch (data.type) {
          case 'platform_update':
            if (data.data) {
              const newRevenue = data.data.total_revenue || 0;
              if (newRevenue > totalRevenue) {
                setRevenueAnimation(true);
                setTimeout(() => setRevenueAnimation(false), 1000);
              }
              const updatedStatus = {
                ...data.data,
                agent_breakdown: data.data.agent_breakdown || []
              };
              setPlatformStatus(updatedStatus);
              setTotalRevenue(newRevenue);

              if (data.data.active_sessions) {
                setActiveSessions(data.data.active_sessions);
              }
            }
            break;

          case 'platform_status':
            setPlatformStatus(data.data);
            setTotalRevenue(data.data.total_revenue || 0);
            break;

          case 'platform_activated':
            if (data.success && data.data) {
              console.log('✅ Platform activated via WebSocket!');
              const activatedStatus = {
                ...data.data,
                agent_breakdown: data.data.agent_breakdown || []
              };
              setPlatformStatus(activatedStatus);
              setTotalRevenue(data.data.total_revenue || 0);
              if (data.data.active_sessions) {
                setActiveSessions(data.data.active_sessions);
              }
            }
            setActivating(false);
            break;

          case 'activation_error':
            console.error('❌ Activation error:', data.message);
            setActivating(false);
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setConnectionStatus('disconnected');
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnectionStatus('disconnected');
      setTimeout(connectWebSocket, 5000);
    };

    wsRef.current = ws;
  };

  const activatePlatform = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    setActivating(true);
    wsRef.current.send(JSON.stringify({ action: 'activate_platform' }));
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">AI Agent Work Platform</h1>
          <p className="text-gray-600">Where your agents actually make money by doing real work</p>
          <div className="flex items-center mt-2 space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500' :
                connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                {connectionStatus === 'connected' ? '🔄 Live Updates' :
                 connectionStatus === 'connecting' ? '⏳ Connecting...' : '❌ Disconnected'}
              </span>
            </div>
            {lastUpdate && (
              <span className="text-xs text-gray-500">
                Last update: {lastUpdate}
              </span>
            )}
          </div>
        </div>
        <div className="flex space-x-2">
          <Button
            onClick={activatePlatform}
            disabled={activating || connectionStatus !== 'connected'}
            className="bg-green-600 hover:bg-green-700"
          >
            {activating ? '🚀 Activating...' : '🚀 Activate Platform'}
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className={`text-2xl font-bold text-green-600 transition-all duration-500 ${
              revenueAnimation ? 'scale-110 text-green-400' : ''
            }`}>
              {formatCurrency(totalRevenue)}
              {revenueAnimation && <span className="ml-2 text-sm">💰 +</span>}
            </div>
            <p className="text-sm text-gray-600">Total Revenue Earned</p>
            {connectionStatus === 'connected' && (
              <p className="text-xs text-green-600 mt-1">🔄 Live Updates</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">
              {platformStatus?.agents_working || 0}
            </div>
            <p className="text-sm text-gray-600">Agents Working</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-purple-600">
              {activeSessions.length}
            </div>
            <p className="text-sm text-gray-600">Active Work Sessions</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-orange-600">
              {formatCurrency(platformStatus?.daily_revenue_potential || 3000)}
            </div>
            <p className="text-sm text-gray-600">Daily Potential</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="agents">Agent Workforce</TabsTrigger>
          <TabsTrigger value="sessions">Active Sessions</TabsTrigger>
          <TabsTrigger value="analytics">Revenue Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Platform Status */}
            <Card>
              <CardHeader>
                <CardTitle>Platform Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Agents</span>
                    <span className="font-medium">{platformStatus?.total_agents || 151}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Working Agents</span>
                    <span className="font-medium text-blue-600">{platformStatus?.agents_working || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Utilization Rate</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{width: `${platformStatus?.utilization_rate ? platformStatus.utilization_rate * 100 : 0}%`}}
                        />
                      </div>
                      <span className="font-medium">
                        {platformStatus?.utilization_rate ? `${(platformStatus.utilization_rate * 100).toFixed(1)}%` : '0%'}
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Revenue Today</span>
                    <span className="font-medium text-green-600">{formatCurrency(totalRevenue)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Sessions</span>
                    <span className="font-medium text-purple-600">{activeSessions.length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Revenue Projections */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue Projections</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Hourly Rate</span>
                    <span className="font-medium text-orange-600">
                      {totalRevenue > 0 ? formatCurrency(totalRevenue / Math.max((platformStatus?.agents_working || 1) * 0.5, 1)) : '$0'}/hr
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Daily Potential</span>
                    <span className="font-medium">{formatCurrency(platformStatus?.daily_revenue_potential || 3000)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly Potential</span>
                    <span className="font-medium text-blue-600">{formatCurrency((platformStatus?.daily_revenue_potential || 3000) * 30)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Annual Potential</span>
                    <span className="font-medium text-green-600">{formatCurrency((platformStatus?.daily_revenue_potential || 3000) * 365)}</span>
                  </div>
                  <div className="pt-2 border-t">
                    <div className="text-center text-sm text-gray-600">At current rate, you'll earn</div>
                    <div className="text-center text-2xl font-bold text-green-600">
                      {formatCurrency(totalRevenue * 24)} today
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Live Activity Feed */}
          <Card>
            <CardHeader>
              <CardTitle>Live Activity Feed</CardTitle>
              <CardDescription>Real-time agent actions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {activeSessions.slice(0, 5).map((session, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-sm font-medium">{session.agent_name}</span>
                      <span className="text-xs text-gray-500">is working on</span>
                      <span className="text-sm">{session.job_title}</span>
                    </div>
                    <span className="text-sm font-medium text-green-600">+{formatCurrency(session.revenue_generated)}</span>
                  </div>
                ))}
                {activeSessions.length === 0 && (
                  <div className="text-center text-gray-500 py-4">
                    Click "Activate Platform" to start your agents working!
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agent Workforce Tab */}
        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Workforce</CardTitle>
              <CardDescription>Your AI agents organized by specialization</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Agent Categories */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {Math.floor((platformStatus?.agents_working || 0) * 0.4)}
                  </div>
                  <div className="text-sm text-gray-600">Development Agents</div>
                  <div className="text-xs text-gray-500">Python, JavaScript, React</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {Math.floor((platformStatus?.agents_working || 0) * 0.3)}
                  </div>
                  <div className="text-sm text-gray-600">Content Agents</div>
                  <div className="text-xs text-gray-500">Writing, SEO, Marketing</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {Math.floor((platformStatus?.agents_working || 0) * 0.3)}
                  </div>
                  <div className="text-sm text-gray-600">Analysis Agents</div>
                  <div className="text-xs text-gray-500">Data, Research, Reports</div>
                </div>
              </div>

              {/* Top Performing Agents */}
              <div className="space-y-4">
                <h3 className="font-medium text-gray-700">Top Performing Agents</h3>
                {activeSessions.slice(0, 5).map((session, index) => (
                  <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-medium">{session.agent_name}</h3>
                        <p className="text-sm text-gray-600">
                          {formatCurrency(session.hourly_rate)}/hour • Working on: {session.job_title}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-600">
                          {formatCurrency(session.revenue_generated)}
                        </div>
                        <div className="text-xs text-gray-600">
                          {session.hours_worked} hours worked
                        </div>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{width: `${Math.min((session.hours_worked / 8) * 100, 100)}%`}}
                      />
                    </div>
                  </div>
                ))}
                {activeSessions.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    <div className="text-lg mb-2">No agents currently working</div>
                    <div className="text-sm">Activate the platform to deploy your workforce!</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Active Sessions Tab */}
        <TabsContent value="sessions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Work Sessions</CardTitle>
              <CardDescription>Real-time view of ongoing projects and their progress</CardDescription>
            </CardHeader>
            <CardContent>
              {activeSessions.length > 0 ? (
                <div className="space-y-4">
                  {/* Session Stats */}
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <div className="text-2xl font-bold">{activeSessions.length}</div>
                      <div className="text-xs text-gray-600">Active Sessions</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <div className="text-2xl font-bold text-green-600">
                        {formatCurrency(activeSessions.reduce((sum, s) => sum + s.revenue_generated, 0))}
                      </div>
                      <div className="text-xs text-gray-600">Session Revenue</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <div className="text-2xl font-bold text-blue-600">
                        {activeSessions.reduce((sum, s) => sum + s.hours_worked, 0).toFixed(1)}
                      </div>
                      <div className="text-xs text-gray-600">Total Hours</div>
                    </div>
                  </div>

                  {/* Session List */}
                  {activeSessions.map((session, index) => (
                    <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            <h3 className="font-medium">{session.job_title}</h3>
                          </div>
                          <p className="text-sm text-gray-600">
                            Agent: {session.agent_name} • Rate: {formatCurrency(session.hourly_rate)}/hr
                          </p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>Started: {new Date(Date.now() - session.hours_worked * 3600000).toLocaleTimeString()}</span>
                            <span>Duration: {session.hours_worked}h</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-green-600">
                            {formatCurrency(session.revenue_generated)}
                          </div>
                          <div className="text-xs text-gray-600">
                            {((session.revenue_generated / session.hourly_rate) * 100).toFixed(0)}% complete
                          </div>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs text-gray-600">
                          <span>Progress</span>
                          <span>{((session.hours_worked / 8) * 100).toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                            style={{width: `${Math.min((session.hours_worked / 8) * 100, 100)}%`}}
                          />
                        </div>
                      </div>

                      {/* Session Actions */}
                      <div className="mt-3 flex items-center justify-between">
                        <div className="text-xs text-gray-600">
                          Session ID: {session.session_id}
                        </div>
                        <div className="flex space-x-2">
                          <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Active</span>
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                            {session.job_title.includes('Python') ? 'Development' :
                             session.job_title.includes('Content') ? 'Writing' : 'Analysis'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-12">
                  <div className="text-6xl mb-4">💼</div>
                  <div className="text-lg mb-2">No active work sessions</div>
                  <div className="text-sm mb-4">Your agents are ready to start working!</div>
                  <Button
                    onClick={activatePlatform}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    🚀 Start Working Now
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Revenue Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Revenue Analytics</CardTitle>
              <CardDescription>Comprehensive revenue insights and projections</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Revenue Chart */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
                  <div className="text-center mb-4">
                    <div className="text-4xl font-bold text-green-600">{formatCurrency(totalRevenue)}</div>
                    <div className="text-sm text-gray-600">Total Revenue Generated</div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-xl font-bold">
                        {formatCurrency(totalRevenue / Math.max(1, 1))}
                      </div>
                      <div className="text-xs text-gray-600">Per Hour</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-blue-600">
                        {formatCurrency(platformStatus?.daily_revenue_potential || 3000)}
                      </div>
                      <div className="text-xs text-gray-600">Daily Potential</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-purple-600">
                        {((totalRevenue / (platformStatus?.daily_revenue_potential || 3000)) * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-600">Of Daily Goal</div>
                    </div>
                  </div>
                </div>

                {/* Revenue by Category */}
                <div>
                  <h3 className="font-medium mb-3">Revenue by Service Type</h3>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium">Software Development</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.45)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div className="bg-blue-600 h-3 rounded-full flex items-center" style={{width: '45%'}}>
                          <span className="text-xs text-white px-2">45%</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium">Content Creation</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.25)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div className="bg-green-600 h-3 rounded-full flex items-center" style={{width: '25%'}}>
                          <span className="text-xs text-white px-2">25%</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium">Data Analysis</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.20)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div className="bg-purple-600 h-3 rounded-full flex items-center" style={{width: '20%'}}>
                          <span className="text-xs text-white px-2">20%</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium">Consulting</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.10)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div className="bg-orange-600 h-3 rounded-full flex items-center" style={{width: '10%'}}>
                          <span className="text-xs text-white px-2">10%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div>
                  <h3 className="font-medium mb-3">Key Performance Indicators</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3 bg-gray-50 rounded text-center">
                      <div className="text-xl font-bold text-blue-600">
                        {platformStatus?.agents_working || 0}
                      </div>
                      <div className="text-xs text-gray-600">Active Agents</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded text-center">
                      <div className="text-xl font-bold text-green-600">
                        {formatCurrency(totalRevenue / Math.max(platformStatus?.agents_working || 1, 1))}
                      </div>
                      <div className="text-xs text-gray-600">Per Agent</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded text-center">
                      <div className="text-xl font-bold text-purple-600">
                        {activeSessions.length}
                      </div>
                      <div className="text-xs text-gray-600">Active Jobs</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded text-center">
                      <div className="text-xl font-bold text-orange-600">
                        {((platformStatus?.utilization_rate || 0) * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-gray-600">Utilization</div>
                    </div>
                  </div>
                </div>

                {/* Projection */}
                <div className="border-t pt-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-2">If you maintain this rate 24/7</div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <div className="text-lg font-bold">{formatCurrency(totalRevenue * 24)}</div>
                        <div className="text-xs text-gray-500">Today</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-blue-600">{formatCurrency(totalRevenue * 24 * 30)}</div>
                        <div className="text-xs text-gray-500">This Month</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-green-600">{formatCurrency(totalRevenue * 24 * 365)}</div>
                        <div className="text-xs text-gray-500">This Year</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EnhancedAgentWorkPlatform;