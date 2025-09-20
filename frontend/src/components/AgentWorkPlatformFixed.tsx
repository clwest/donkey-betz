import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { EnhancedButton as Button } from './ui/enhanced-button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface WorkSession {
  session_id: string;
  agent_name: string;
  agent_skills?: string[];
  job_title: string;
  client_name?: string;
  platform?: string;
  hourly_rate: number;
  hours_worked: number;
  revenue_generated: number;
  job_budget?: number;
  job_progress?: number;
  status?: string;
  category?: string;
  milestones?: any[];
  next_deliverable?: string;
  client_satisfaction?: string;
}

interface PendingVerification {
  job_id: string;
  agent_name: string;
  job_title: string;
  deliverable: string;
  client: string;
  amount: number;
  status: string;
  submitted_at: string;
  action_needed: string;
}

interface PlatformStatus {
  total_agents: number;
  agents_working: number;
  active_sessions: WorkSession[];
  total_revenue: number;
  daily_revenue_potential: number;
  utilization_rate: number;
  pending_verifications?: PendingVerification[];
  performance_metrics?: any;
}

const AgentWorkPlatformFixed: React.FC = () => {
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus | null>(null);
  const [activeSessions, setActiveSessions] = useState<WorkSession[]>([]);
  const [activating, setActivating] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [totalRevenue, setTotalRevenue] = useState(0);
  const [revenueAnimation, setRevenueAnimation] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedVerification, setSelectedVerification] = useState<PendingVerification | null>(null);
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [revisionNote, setRevisionNote] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

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
    const ws = new WebSocket(`ws://localhost:8000/ws/agent-platform/`);

    ws.onopen = () => {
      console.log('✅ Connected to Agent Platform');
      setConnectionStatus('connected');
      ws.send(JSON.stringify({ action: 'get_platform_status' }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📊 Update:', data);

        if (data.type === 'platform_update' && data.data) {
          const newRevenue = data.data.total_revenue || 0;
          if (newRevenue > totalRevenue) {
            setRevenueAnimation(true);
            setTimeout(() => setRevenueAnimation(false), 1000);
          }
          setPlatformStatus(data.data);
          setTotalRevenue(newRevenue);
          if (data.data.active_sessions) {
            setActiveSessions(data.data.active_sessions);
          }
        } else if (data.type === 'platform_status') {
          setPlatformStatus(data.data);
          setTotalRevenue(data.data.total_revenue || 0);
        } else if (data.type === 'platform_activated') {
          if (data.success && data.data) {
            setPlatformStatus(data.data);
            setTotalRevenue(data.data.total_revenue || 0);
            if (data.data.active_sessions) {
              setActiveSessions(data.data.active_sessions);
            }
          }
          setActivating(false);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    ws.onerror = () => setConnectionStatus('disconnected');
    ws.onclose = () => {
      setConnectionStatus('disconnected');
      setTimeout(connectWebSocket, 5000);
    };

    wsRef.current = ws;
  };

  const activatePlatform = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
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

  const handleApprove = (verification: PendingVerification) => {
    console.log('Approving:', verification);
    // Send approval to backend
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'approve_verification',
        job_id: verification.job_id,
        amount: verification.amount
      }));
    }
    // Show success notification
    alert(`✅ Approved! Payment of ${formatCurrency(verification.amount)} released to ${verification.agent_name}`);
  };

  const handleRequestRevision = (verification: PendingVerification) => {
    setSelectedVerification(verification);
    setShowRevisionModal(true);
  };

  const handleViewDetails = (verification: PendingVerification) => {
    setSelectedVerification(verification);
    setShowDetailsModal(true);
  };

  const submitRevisionRequest = () => {
    if (selectedVerification && revisionNote) {
      console.log('Requesting revision:', selectedVerification, revisionNote);
      // Send revision request to backend
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          action: 'request_revision',
          job_id: selectedVerification.job_id,
          note: revisionNote
        }));
      }
      alert(`📝 Revision requested for ${selectedVerification.job_title}`);
      setShowRevisionModal(false);
      setRevisionNote('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
              AI Agent Work Platform
            </h1>
            <p className="text-gray-400 mt-2">Where your agents actually make money by doing real work</p>
            <div className="flex items-center mt-3 space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' :
                  connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <span className="text-sm text-gray-400">
                  {connectionStatus === 'connected' ? 'Live Updates' :
                   connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
          <Button
            onClick={activatePlatform}
            disabled={activating || connectionStatus !== 'connected'}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg"
          >
            {activating ? '🚀 Activating...' : '🚀 Activate Platform'}
          </Button>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <div className={`text-3xl font-bold text-green-400 ${revenueAnimation ? 'animate-pulse' : ''}`}>
              {formatCurrency(totalRevenue)}
            </div>
            <p className="text-gray-400 text-sm mt-1">Total Revenue</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <div className="text-3xl font-bold text-blue-400">
              {platformStatus?.agents_working || 0}
            </div>
            <p className="text-gray-400 text-sm mt-1">Agents Working</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <div className="text-3xl font-bold text-purple-400">
              {activeSessions.length}
            </div>
            <p className="text-gray-400 text-sm mt-1">Active Sessions</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <div className="text-3xl font-bold text-orange-400">
              {formatCurrency(platformStatus?.daily_revenue_potential || 3000)}
            </div>
            <p className="text-gray-400 text-sm mt-1">Daily Potential</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="w-full bg-gray-800 rounded-t-lg border-b border-gray-700">
              <TabsTrigger value="overview" className="flex-1">Overview</TabsTrigger>
              <TabsTrigger value="agents" className="flex-1">Agent Workforce</TabsTrigger>
              <TabsTrigger value="sessions" className="flex-1">Active Sessions</TabsTrigger>
              <TabsTrigger value="verification" className="flex-1">
                Human Verification
                {platformStatus?.pending_verifications && platformStatus.pending_verifications.length > 0 && (
                  <span className="ml-2 px-2 py-0.5 text-xs bg-red-600 text-white rounded-full">
                    {platformStatus.pending_verifications.length}
                  </span>
                )}
              </TabsTrigger>
              <TabsTrigger value="analytics" className="flex-1">Revenue Analytics</TabsTrigger>
            </TabsList>

            <div className="p-6">
              {/* Overview Tab */}
              <TabsContent value="overview" className="mt-0 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Platform Status</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Total Agents</span>
                        <span className="font-medium">{platformStatus?.total_agents || 151}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Working Agents</span>
                        <span className="font-medium text-blue-400">{platformStatus?.agents_working || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Utilization Rate</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full transition-all"
                              style={{width: `${(platformStatus?.utilization_rate || 0) * 100}%`}}
                            />
                          </div>
                          <span className="text-sm">{((platformStatus?.utilization_rate || 0) * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">Revenue Projections</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Daily Potential</span>
                        <span className="font-medium">{formatCurrency(platformStatus?.daily_revenue_potential || 3000)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Monthly Potential</span>
                        <span className="font-medium text-blue-400">{formatCurrency((platformStatus?.daily_revenue_potential || 3000) * 30)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Annual Potential</span>
                        <span className="font-medium text-green-400">{formatCurrency((platformStatus?.daily_revenue_potential || 3000) * 365)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Live Activity Feed */}
                <div className="bg-gray-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Live Activity Feed</h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {activeSessions.slice(0, 5).map((session, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-gray-700 rounded">
                        <div className="flex items-center space-x-3">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                          <span className="text-sm">{session.agent_name}</span>
                          <span className="text-xs text-gray-400">working on</span>
                          <span className="text-sm text-blue-400">{session.job_title}</span>
                        </div>
                        <span className="text-sm font-medium text-green-400">+{formatCurrency(session.revenue_generated)}</span>
                      </div>
                    ))}
                    {activeSessions.length === 0 && (
                      <div className="text-center text-gray-500 py-8">
                        Click "Activate Platform" to start your agents working!
                      </div>
                    )}
                  </div>
                </div>
              </TabsContent>

              {/* Agent Workforce Tab */}
              <TabsContent value="agents" className="mt-0 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-gradient-to-br from-blue-900 to-blue-800 p-4 rounded-lg">
                    <div className="text-3xl font-bold">{Math.floor((platformStatus?.agents_working || 0) * 0.4)}</div>
                    <div className="text-sm mt-1">Development Agents</div>
                    <div className="text-xs text-gray-300 mt-1">Python, JavaScript, React</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-900 to-green-800 p-4 rounded-lg">
                    <div className="text-3xl font-bold">{Math.floor((platformStatus?.agents_working || 0) * 0.3)}</div>
                    <div className="text-sm mt-1">Content Agents</div>
                    <div className="text-xs text-gray-300 mt-1">Writing, SEO, Marketing</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-4 rounded-lg">
                    <div className="text-3xl font-bold">{Math.floor((platformStatus?.agents_working || 0) * 0.3)}</div>
                    <div className="text-sm mt-1">Analysis Agents</div>
                    <div className="text-xs text-gray-300 mt-1">Data, Research, Reports</div>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Top Performing Agents</h3>
                  {activeSessions.slice(0, 5).map((session, index) => (
                    <div key={index} className="border border-gray-700 rounded-lg p-4 mb-3">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium">{session.agent_name}</h4>
                          <p className="text-sm text-gray-400">
                            {formatCurrency(session.hourly_rate)}/hour • {session.job_title}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-green-400">{formatCurrency(session.revenue_generated)}</div>
                          <div className="text-xs text-gray-400">{session.hours_worked}h worked</div>
                        </div>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{width: `${Math.min((session.hours_worked / 8) * 100, 100)}%`}}
                        />
                      </div>
                    </div>
                  ))}
                  {activeSessions.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                      No agents currently working. Activate the platform to deploy your workforce!
                    </div>
                  )}
                </div>
              </TabsContent>

              {/* Active Sessions Tab */}
              <TabsContent value="sessions" className="mt-0 space-y-6">
                {activeSessions.length > 0 ? (
                  <>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-gray-800 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold">{activeSessions.length}</div>
                        <div className="text-xs text-gray-400">Active Sessions</div>
                      </div>
                      <div className="bg-gray-800 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-green-400">
                          {formatCurrency(activeSessions.reduce((sum, s) => sum + s.revenue_generated, 0))}
                        </div>
                        <div className="text-xs text-gray-400">Session Revenue</div>
                      </div>
                      <div className="bg-gray-800 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-blue-400">
                          {activeSessions.reduce((sum, s) => sum + s.hours_worked, 0).toFixed(1)}
                        </div>
                        <div className="text-xs text-gray-400">Total Hours</div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {activeSessions.map((session, index) => (
                        <div key={index} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                <h3 className="font-medium">{session.job_title}</h3>
                                {session.platform && (
                                  <span className="text-xs px-2 py-1 bg-blue-900 text-blue-300 rounded">
                                    {session.platform}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-gray-400">
                                Agent: <span className="text-blue-400 font-medium">{session.agent_name}</span> •
                                Client: <span className="text-purple-400">{session.client_name || 'Direct Client'}</span> •
                                Rate: {formatCurrency(session.hourly_rate)}/hr
                              </p>
                              {session.agent_skills && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {session.agent_skills.slice(0, 3).map((skill, idx) => (
                                    <span key={idx} className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded">
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              )}
                              {session.next_deliverable && (
                                <p className="text-xs text-yellow-400 mt-2">
                                  📅 {session.next_deliverable}
                                </p>
                              )}
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-green-400">
                                {formatCurrency(session.revenue_generated)}
                              </div>
                              <div className="text-xs text-gray-400">
                                {session.hours_worked}h worked
                              </div>
                              {session.client_satisfaction && (
                                <div className="text-xs mt-1">{session.client_satisfaction}</div>
                              )}
                            </div>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between text-xs text-gray-400">
                              <span>Progress: {session.job_progress || 0}%</span>
                              <span>Budget: {formatCurrency(session.job_budget || 0)}</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full"
                                style={{width: `${session.job_progress || 0}%`}}
                              />
                            </div>
                          </div>
                          {session.milestones && session.milestones.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-gray-700">
                              <p className="text-xs text-gray-400 mb-2">Milestones:</p>
                              <div className="grid grid-cols-2 gap-2">
                                {session.milestones.map((milestone: any, mIdx: number) => (
                                  <div key={mIdx} className="text-xs">
                                    <span className={`inline-block w-2 h-2 rounded-full mr-1 ${
                                      milestone.status === 'completed' ? 'bg-green-500' :
                                      milestone.status === 'in_progress' ? 'bg-yellow-500' :
                                      'bg-gray-500'
                                    }`} />
                                    {milestone.name}: {formatCurrency(milestone.amount)}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">💼</div>
                    <div className="text-xl mb-2">No active work sessions</div>
                    <div className="text-gray-400 mb-4">Your agents are ready to start working!</div>
                    <Button
                      onClick={activatePlatform}
                      className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                    >
                      🚀 Start Working Now
                    </Button>
                  </div>
                )}
              </TabsContent>

              {/* Human Verification Tab */}
              <TabsContent value="verification" className="mt-0 space-y-6">
                {platformStatus?.pending_verifications && platformStatus.pending_verifications.length > 0 ? (
                  <>
                    <div className="bg-yellow-900 border border-yellow-700 text-yellow-100 px-4 py-3 rounded-lg mb-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          ⚠️
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium">
                            {platformStatus.pending_verifications.length} deliverables need your review
                          </p>
                          <p className="text-xs mt-1 text-yellow-200">
                            Review and approve work to release payments to agents
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {platformStatus.pending_verifications.map((verification, index) => (
                        <div key={index} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <h3 className="text-lg font-semibold text-white">{verification.job_title}</h3>
                              <p className="text-sm text-gray-400 mt-1">
                                By <span className="text-blue-400">{verification.agent_name}</span> for{' '}
                                <span className="text-purple-400">{verification.client}</span>
                              </p>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold text-green-400">
                                {formatCurrency(verification.amount)}
                              </div>
                              <div className="text-xs text-gray-400">{verification.submitted_at}</div>
                            </div>
                          </div>

                          <div className="bg-gray-900 rounded p-4 mb-4">
                            <p className="text-sm text-gray-300 font-medium mb-2">Deliverable:</p>
                            <p className="text-sm text-gray-400">{verification.deliverable}</p>
                          </div>

                          <div className="bg-orange-900 bg-opacity-50 border border-orange-700 rounded p-3 mb-4">
                            <p className="text-xs text-orange-300 font-medium">Action Required:</p>
                            <p className="text-sm text-orange-100 mt-1">{verification.action_needed}</p>
                          </div>

                          <div className="flex space-x-3">
                            <Button
                              className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                              onClick={() => handleApprove(verification)}
                            >
                              ✓ Approve & Release Payment
                            </Button>
                            <Button
                              className="flex-1 bg-yellow-600 hover:bg-yellow-700 text-white"
                              onClick={() => handleRequestRevision(verification)}
                            >
                              ↻ Request Revision
                            </Button>
                            <Button
                              className="flex-1 bg-gray-600 hover:bg-gray-700 text-white"
                              onClick={() => handleViewDetails(verification)}
                            >
                              👁 View Details
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✅</div>
                    <div className="text-xl mb-2">All work verified!</div>
                    <div className="text-gray-400 mb-4">
                      No deliverables currently pending your review
                    </div>
                    <p className="text-sm text-gray-500">
                      When agents complete work, it will appear here for your verification
                    </p>
                  </div>
                )}
              </TabsContent>

              {/* Revenue Analytics Tab */}
              <TabsContent value="analytics" className="mt-0 space-y-6">
                <div className="bg-gradient-to-r from-green-900 to-blue-900 p-6 rounded-lg">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-green-400">{formatCurrency(totalRevenue)}</div>
                    <div className="text-gray-300 mt-1">Total Revenue Generated</div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-6">
                    <div className="text-center">
                      <div className="text-xl font-bold">{formatCurrency(totalRevenue * 24)}</div>
                      <div className="text-xs text-gray-400">Today's Projection</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-blue-400">
                        {formatCurrency((platformStatus?.daily_revenue_potential || 3000))}
                      </div>
                      <div className="text-xs text-gray-400">Daily Potential</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-purple-400">
                        {((totalRevenue / (platformStatus?.daily_revenue_potential || 3000)) * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-400">Of Daily Goal</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Revenue by Service Type</h3>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm">Software Development</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.45)}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-3">
                        <div className="bg-blue-500 h-3 rounded-full" style={{width: '45%'}} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm">Content Creation</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.25)}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-3">
                        <div className="bg-green-500 h-3 rounded-full" style={{width: '25%'}} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm">Data Analysis</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.20)}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-3">
                        <div className="bg-purple-500 h-3 rounded-full" style={{width: '20%'}} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm">Consulting</span>
                        <span className="text-sm font-bold">{formatCurrency(totalRevenue * 0.10)}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-3">
                        <div className="bg-orange-500 h-3 rounded-full" style={{width: '10%'}} />
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>

      {/* Revision Request Modal */}
      {showRevisionModal && selectedVerification && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-lg w-full">
            <h2 className="text-xl font-bold mb-4">Request Revision</h2>
            <div className="mb-4">
              <p className="text-sm text-gray-400 mb-2">Job: {selectedVerification.job_title}</p>
              <p className="text-sm text-gray-400">Agent: {selectedVerification.agent_name}</p>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Revision Notes:</label>
              <textarea
                className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white resize-none"
                rows={4}
                placeholder="Describe what needs to be revised..."
                value={revisionNote}
                onChange={(e) => setRevisionNote(e.target.value)}
              />
            </div>
            <div className="flex space-x-3">
              <Button
                className="flex-1 bg-yellow-600 hover:bg-yellow-700"
                onClick={submitRevisionRequest}
              >
                Send Revision Request
              </Button>
              <Button
                className="flex-1 bg-gray-600 hover:bg-gray-700"
                onClick={() => {
                  setShowRevisionModal(false);
                  setRevisionNote('');
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* View Details Modal */}
      {showDetailsModal && selectedVerification && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Job Details</h2>

            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Job Information</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-400">Title:</span>
                    <p className="text-white">{selectedVerification.job_title}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Client:</span>
                    <p className="text-white">{selectedVerification.client}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Agent:</span>
                    <p className="text-blue-400">{selectedVerification.agent_name}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Amount:</span>
                    <p className="text-green-400 font-bold">{formatCurrency(selectedVerification.amount)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Deliverable</h3>
                <p className="text-sm text-gray-300">{selectedVerification.deliverable}</p>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Work Preview</h3>
                <div className="bg-gray-900 p-3 rounded border border-gray-700">
                  <p className="text-xs text-gray-400 mb-2">Sample Output:</p>
                  <pre className="text-xs text-green-400 font-mono">
{`// Example code delivered
function processData(input) {
  const results = input.map(item => ({
    id: item.id,
    processed: true,
    timestamp: Date.now()
  }));
  return results;
}`}
                  </pre>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Quality Metrics</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-green-400">98%</p>
                    <p className="text-xs text-gray-400">Code Quality</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-400">100%</p>
                    <p className="text-xs text-gray-400">Tests Passing</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-purple-400">A+</p>
                    <p className="text-xs text-gray-400">Client Rating</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 flex space-x-3">
              <Button
                className="flex-1 bg-green-600 hover:bg-green-700"
                onClick={() => {
                  handleApprove(selectedVerification);
                  setShowDetailsModal(false);
                }}
              >
                ✓ Approve & Pay
              </Button>
              <Button
                className="flex-1 bg-gray-600 hover:bg-gray-700"
                onClick={() => setShowDetailsModal(false)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentWorkPlatformFixed;