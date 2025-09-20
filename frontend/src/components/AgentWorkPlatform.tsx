import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { EnhancedButton as Button } from './ui/enhanced-button';
import { Badge } from './common/Badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';

interface AgentWorker {
  name: string;
  capabilities: string[];
  hourly_rate: number;
  current_workload: number;
  max_concurrent: number;
  availability_hours: number;
}

interface WorkSession {
  session_id: string;
  agent_id: string;
  agent_name?: string;
  job_id: string;
  task_description?: string;
  progress: number;
  status: string;
  revenue_earned: number;
  estimated_completion: string;
  started_at: string;
  agent_specialization?: string;
}

interface ExecutableJob {
  opportunity_id: string;
  title: string;
  description: string;
  required_capabilities: string[];
  estimated_hours: number;
  client_budget: number;
  complexity_level: string;
  revenue_potential: number;
  status: string;
}

interface PlatformStatus {
  total_agents: number;
  agents_working: number;
  active_work_sessions: number;
  completed_jobs: number;
  total_revenue: number;
  agent_utilization_rate: number;
  daily_revenue_potential: number;
  agent_breakdown: AgentWorker[];
}

interface RevenueAnalytics {
  current_revenue: number;
  potential_revenue: number;
  revenue_in_progress: number;
  average_job_value: number;
  highest_value_job: number;
  revenue_by_complexity: {
    beginner: number;
    intermediate: number;
    advanced: number;
  };
  jobs_by_status: {
    available: number;
    assigned: number;
    in_progress: number;
    completed: number;
  };
}

const AgentWorkPlatform: React.FC = () => {
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus | null>(null);
  const [activeSessions, setActiveSessions] = useState<WorkSession[]>([]);
  const [executableJobs, setExecutableJobs] = useState<ExecutableJob[]>([]);
  const [revenueAnalytics, setRevenueAnalytics] = useState<RevenueAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [activating, setActivating] = useState(false);
  const [totalRevenue, setTotalRevenue] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [revenueAnimation, setRevenueAnimation] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);

  const connectWebSocket = () => {
    try {
      // Create WebSocket connection to agent platform backend
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const backendHost = 'localhost:8000'; // Backend WebSocket server
      const wsUrl = `${protocol}//${backendHost}/ws/agent-platform/`;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('💰 Agent Work Platform WebSocket connected!');
        setConnectionStatus('connected');

        // Request initial data
        wsRef.current?.send(JSON.stringify({ action: 'get_platform_status' }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📊 Real-time platform update:', data.type);

          setLastUpdate(new Date().toLocaleTimeString());

          switch (data.type) {
            case 'platform_update':
              // Complete real-time update with all data
              if (data.data) {
                const newRevenue = data.data.total_revenue || 0;
                if (newRevenue > totalRevenue) {
                  // Animate revenue increase
                  setRevenueAnimation(true);
                  setTimeout(() => setRevenueAnimation(false), 1000);
                }
                // Ensure agent_breakdown exists
                const updatedStatus = {
                  ...data.data,
                  agent_breakdown: data.data.agent_breakdown || []
                };
                setPlatformStatus(updatedStatus);
                setTotalRevenue(newRevenue);

                // Update active sessions if present
                if (data.data.active_sessions) {
                  setActiveSessions(data.data.active_sessions);
                }
              }
              if (data.revenue_analytics) {
                setRevenueAnalytics(data.revenue_analytics);
              }
              if (data.executable_jobs) {
                setExecutableJobs(data.executable_jobs);
              }
              break;

            case 'platform_status':
              setPlatformStatus(data.data);
              setTotalRevenue(data.data.total_revenue || 0);
              break;

            case 'active_sessions':
              setActiveSessions(data.sessions);
              break;

            case 'revenue_metrics':
              setRevenueAnalytics(data.analytics);
              break;

            case 'platform_activated':
              if (data.success && data.data) {
                console.log('✅ Platform activated via WebSocket!');
                // Update platform status with activation data
                const activatedStatus = {
                  ...data.data,
                  agent_breakdown: data.data.agent_breakdown || []
                };
                setPlatformStatus(activatedStatus);
                setTotalRevenue(data.data.total_revenue || 0);

                // Update active sessions if present
                if (data.data.active_sessions) {
                  setActiveSessions(data.data.active_sessions);
                }
              }
              setActivating(false);
              break;

            case 'activation_error':
              console.error('❌ Platform activation failed:', data.error);
              setActivating(false);
              break;

            case 'error':
              console.error('WebSocket error:', data.message);
              break;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('Agent Work Platform WebSocket disconnected');
        setConnectionStatus('disconnected');

        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  };

  const activatePlatform = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      setActivating(true);
      wsRef.current.send(JSON.stringify({ action: 'activate_platform' }));
    } else {
      console.error('WebSocket not connected');
    }
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
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
              {formatCurrency(revenueAnalytics?.potential_revenue || 0)}
            </div>
            <p className="text-sm text-gray-600">Potential Revenue</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="agents">Agent Workforce</TabsTrigger>
          <TabsTrigger value="sessions">Active Sessions</TabsTrigger>
          <TabsTrigger value="analytics">Revenue Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Platform Utilization */}
            <Card>
              <CardHeader>
                <CardTitle>Platform Utilization</CardTitle>
                <CardDescription>How efficiently your agents are being used</CardDescription>
              </CardHeader>
              <CardContent>
                {platformStatus && (
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm">
                        <span>Agent Utilization</span>
                        <span>{(platformStatus.agent_utilization_rate * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={platformStatus.agent_utilization_rate * 100} className="mt-2" />
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="font-medium">Total Agents</div>
                        <div className="text-2xl font-bold">{platformStatus.total_agents}</div>
                      </div>
                      <div>
                        <div className="font-medium">Daily Potential</div>
                        <div className="text-2xl font-bold">{formatCurrency(platformStatus.daily_revenue_potential)}</div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Revenue Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue Breakdown</CardTitle>
                <CardDescription>Revenue distribution by complexity</CardDescription>
              </CardHeader>
              <CardContent>
                {revenueAnalytics && (
                  <div className="space-y-3">
                    {Object.entries(revenueAnalytics.revenue_by_complexity).map(([complexity, revenue]) => (
                      <div key={complexity} className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                          <Badge className={getComplexityColor(complexity)}>
                            {complexity}
                          </Badge>
                        </div>
                        <div className="font-medium">{formatCurrency(revenue)}</div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Workforce</CardTitle>
              <CardDescription>Your AI agents and their capabilities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {(platformStatus?.agent_breakdown || []).map((agent, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-medium">{agent.name}</h3>
                        <p className="text-sm text-gray-600">{formatCurrency(agent.hourly_rate)}/hour</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">
                          {agent.current_workload}/{agent.max_concurrent} jobs
                        </div>
                        <div className="text-xs text-gray-600">
                          {agent.availability_hours}h/day available
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1 mb-2">
                      {agent.capabilities.map((capability, capIndex) => (
                        <Badge key={capIndex} variant="secondary" className="text-xs">
                          {capability}
                        </Badge>
                      ))}
                    </div>

                    <Progress
                      value={(agent.current_workload / agent.max_concurrent) * 100}
                      className="h-2"
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sessions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Work Sessions</CardTitle>
              <CardDescription>Agents currently working on jobs</CardDescription>
            </CardHeader>
            <CardContent>
              {activeSessions.length > 0 ? (
                <div className="space-y-4">
                  {activeSessions.map((session, index) => (
                    <div key={session.session_id || index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-medium">{session.agent_name || session.agent_id}</h3>
                          <p className="text-sm text-gray-600">{session.task_description || `Session ${session.session_id}`}</p>
                          {session.agent_specialization && (
                            <Badge variant="outline" className="text-xs mt-1">
                              {session.agent_specialization}
                            </Badge>
                          )}
                        </div>
                        <div className="text-right">
                          <Badge className={`${getStatusColor(session.status)} text-white`}>
                            {session.status === 'working' ? '🔄 Working' : session.status}
                          </Badge>
                          <div className="text-sm font-medium mt-1 text-green-600">
                            {formatCurrency(session.revenue_earned)}
                          </div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Progress</span>
                          <span>{(session.progress * 100).toFixed(1)}%</span>
                        </div>
                        <Progress
                          value={session.progress * 100}
                          className={`h-2 ${session.status === 'working' ? 'animate-pulse' : ''}`}
                        />

                        <div className="flex justify-between text-xs text-gray-600">
                          <span>Started: {new Date(session.started_at).toLocaleTimeString()}</span>
                          <span>Est. completion: {new Date(session.estimated_completion).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <Alert>
                  <AlertDescription>
                    No active work sessions. Click "Activate Platform" to start assigning jobs to agents.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                {revenueAnalytics && (
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Current Revenue</span>
                      <span className="font-medium">{formatCurrency(revenueAnalytics.current_revenue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Revenue in Progress</span>
                      <span className="font-medium">{formatCurrency(revenueAnalytics.revenue_in_progress)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Average Job Value</span>
                      <span className="font-medium">{formatCurrency(revenueAnalytics.average_job_value)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Highest Value Job</span>
                      <span className="font-medium">{formatCurrency(revenueAnalytics.highest_value_job)}</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Job Status Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                {revenueAnalytics && (
                  <div className="space-y-3">
                    {Object.entries(revenueAnalytics.jobs_by_status).map(([status, count]) => (
                      <div key={status} className="flex justify-between items-center">
                        <span className="capitalize">{status.replace('_', ' ')}</span>
                        <Badge variant="outline">{count}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AgentWorkPlatform;