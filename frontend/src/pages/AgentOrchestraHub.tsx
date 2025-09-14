import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select-proper';
import { Checkbox } from '@/components/ui/checkbox';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { 
  CpuChipIcon,
  BoltIcon,
  UserGroupIcon,
  CommandLineIcon,
  CircleStackIcon,
  ArrowPathIcon,
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  ChartBarIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  HashtagIcon,
  ChatBubbleLeftRightIcon,
  SignalIcon,
  ClockIcon,
  EyeIcon,
  PlusIcon,
  BeakerIcon,
  ServerStackIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

// Services
import { agentDiscoveryService } from '@/services/agentDiscovery.service';
import { workflowsService } from '@/services/workflows.service';
import { AgentOrchestraService } from '@/services/agent-orchestra.service';
import { agentChannelsService } from '@/services/agentChannels.service';
import { useAgentOrchestraStore } from '@/store/agentOrchestraStore';

// Styles
import '../styles/gaming-theme.css';

// Types
interface Agent {
  id: string;
  name: string;
  description: string;
  specialization: string;
  capabilities: any[];
  status?: 'active' | 'inactive';
  llm_provider?: string;
  priority?: number;
  usage_stats?: {
    usage_count: number;
    success_count: number;
    success_rate: number;
  };
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  agent_count: number;
  created_at: string;
  status?: 'idle' | 'running' | 'completed' | 'failed';
}

interface Execution {
  id: string;
  workflow_name: string;
  status: 'running' | 'completed' | 'failed' | 'stopped';
  started_at: string;
  completed_at?: string;
  progress?: {
    current_step: number;
    total_steps: number;
    message: string;
  };
}

interface Channel {
  id: string;
  name: string;
  display_name?: string;
  description?: string;
  is_active: boolean;
  message_count: number;
  member_count?: number;
}

interface ChannelMessage {
  id: string;
  content: string;
  agent_name?: string;
  message_type: string;
  timestamp: string;
  channel?: string;
}

export default function AgentOrchestraHub() {
  // State Management
  const [activeTab, setActiveTab] = useState('dashboard');
  const [agents, setAgents] = useState<Agent[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [channelMessages, setChannelMessages] = useState<ChannelMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  
  // Dialog States
  const [createWorkflowOpen, setCreateWorkflowOpen] = useState(false);
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
  const [workflowForm, setWorkflowForm] = useState({
    name: '',
    description: '',
    coordination_strategy: 'parallel' as 'sequential' | 'parallel' | 'adaptive',
    agents: [] as string[]
  });

  // Statistics
  const stats = {
    totalAgents: agents.length,
    activeAgents: agents.filter(a => a.status === 'active').length,
    totalWorkflows: workflows.length,
    runningExecutions: executions.filter(e => e.status === 'running').length,
    completedExecutions: executions.filter(e => e.status === 'completed').length,
    activeChannels: channels.filter(c => c.is_active).length,
    totalMessages: channels.reduce((sum, c) => sum + c.message_count, 0)
  };

  // WebSocket Management
  const connectWebSocket = useCallback(() => {
    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    try {
      // Use dynamic API base URL from environment
      const isDev = import.meta.env.MODE !== 'production';
      const wsBase = isDev ? 'ws://localhost:8000' :
        (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host;
      const wsUrl = `${wsBase}/ws/channels/`;

      console.log('[NEURAL LINK] Connecting to:', wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setWsConnected(true);
        console.log('[NEURAL LINK] Connection established');
        toast.success('Neural Link Online', {
          description: 'Real-time connection established',
          icon: '🔗'
        });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('[NEURAL LINK] Message parse error:', error);
        }
      };

      ws.onclose = (event) => {
        setWsConnected(false);
        console.log('[NEURAL LINK] Connection terminated, code:', event.code);

        // Only attempt reconnection for unexpected closures (not normal close = 1000)
        if (event.code !== 1000 && event.code !== 1001) {
          console.log('[NEURAL LINK] Scheduling reconnection...');
          setTimeout(() => {
            if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
              connectWebSocket();
            }
          }, 3000);
        }
      };

      ws.onerror = (error) => {
        console.error('[NEURAL LINK] Connection error:', error);
        setWsConnected(false);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('[NEURAL LINK] Failed to establish connection:', error);
      setWsConnected(false);
    }
  }, []);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'agent_message':
      case 'channel_message':
        if (selectedChannel && (data.channel === selectedChannel.id || data.channel_id === selectedChannel.id)) {
          setChannelMessages(prev => [...prev, data]);
        }
        break;
      case 'execution_update':
        setExecutions(prev => prev.map(exec => 
          exec.id === data.execution_id ? { ...exec, ...data } : exec
        ));
        break;
      case 'workflow_status':
        setWorkflows(prev => prev.map(wf => 
          wf.id === data.workflow_id ? { ...wf, status: data.status } : wf
        ));
        break;
    }
  };

  // Data Loading
  const loadAllData = async () => {
    setLoading(true);
    try {
      const [agentsData, workflowsData, channelsData] = await Promise.all([
        agentDiscoveryService.discoverAllAgents(),
        workflowsService.listWorkflows(),
        agentChannelsService.channels.listChannels({ is_active: true })
      ]);

      setAgents(agentsData?.agents || []);
      setWorkflows(workflowsData?.workflows || []);
      setChannels(channelsData?.results || []);

      // Load execution history - handle if endpoint doesn't exist
      try {
        const isDev = import.meta.env.MODE !== 'production';
        const apiBase = isDev ? 'http://localhost:8000' : window.location.origin;
        const authToken = localStorage.getItem('auth_token');

        // Only try to fetch history if we have a valid auth token
        if (authToken) {
          const historyResponse = await fetch(`${apiBase}/api/v1/workflows/history/`, {
            headers: {
              'Authorization': `Token ${authToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            setExecutions(historyData.executions || []);
          } else if (historyResponse.status === 401) {
            console.log('[NEURAL MATRIX] Authentication required for workflow history');
          }
        } else {
          console.log('[NEURAL MATRIX] No auth token available for history');
        }
      } catch (historyError) {
        console.log('[NEURAL MATRIX] Workflow history endpoint not available:', historyError.message);
        // Continue without history - not critical
      }
    } catch (error) {
      console.error('[NEURAL MATRIX] Data load failed:', error);
      toast.error('Failed to load neural matrix data');
    } finally {
      setLoading(false);
    }
  };

  // Workflow Creation
  const handleCreateWorkflow = async () => {
    if (!workflowForm.name || selectedAgents.size === 0) {
      toast.error('Workflow requires name and agents');
      return;
    }

    try {
      const agentsList = Array.from(selectedAgents);
      const workflowData = {
        name: workflowForm.name,
        description: workflowForm.description,
        agents: agentsList.map((agentId, index) => ({
          name: agents.find(a => a.id === agentId)?.name || agentId,
          agent_id: agentId,
          order: index + 1
        })),
        flow_config: {
          type: workflowForm.coordination_strategy,
          save_intermediate: true,
          error_handling: 'continue'
        }
      };

      await workflowsService.createWorkflow(workflowData);
      toast.success('Neural workflow matrix created');
      setCreateWorkflowOpen(false);
      setSelectedAgents(new Set());
      setWorkflowForm({
        name: '',
        description: '',
        coordination_strategy: 'parallel',
        agents: []
      });
      loadAllData();
    } catch (error) {
      console.error('[NEURAL MATRIX] Workflow creation failed:', error);
      toast.error('Failed to create workflow matrix');
    }
  };

  // Execute Workflow
  const executeWorkflow = async (workflow: Workflow) => {
    try {
      const result = await workflowsService.executeWorkflow({
        workflow_name: workflow.name,
        prompt: 'Execute neural protocol',
        params: {}
      });
      
      toast.success(`Neural matrix "${workflow.name}" activated`);
      loadAllData();
    } catch (error) {
      console.error('[NEURAL MATRIX] Execution failed:', error);
      toast.error('Failed to execute neural matrix');
    }
  };

  // Load Channel Messages
  const loadChannelMessages = async (channel: Channel) => {
    try {
      const response = await agentChannelsService.channels.getChannelMessages(channel.id, {
        page_size: 50
      });
      setChannelMessages(response.results.reverse());
      setSelectedChannel(channel);
    } catch (error) {
      console.error('[NEURAL CHANNEL] Failed to load messages:', error);
    }
  };

  // Mount Effects
  useEffect(() => {
    document.body.classList.add('gaming-theme');
    loadAllData();
    connectWebSocket();

    return () => {
      document.body.classList.remove('gaming-theme');
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
    };
  }, []); // Empty dependency array to run only on mount/unmount

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-6 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full animate-ping opacity-20"></div>
            <div className="relative w-24 h-24 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full animate-pulse flex items-center justify-center">
              <CpuChipIcon className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-cyan-400 font-mono animate-pulse">INITIALIZING NEURAL MATRIX...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Cyberpunk Header */}
      <div className="gaming-card border-b border-cyan-500/30 sticky top-0 z-50 backdrop-blur-xl bg-black/80">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute -inset-2 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg blur opacity-30 animate-pulse"></div>
                <div className="relative p-3 bg-black border-2 border-cyan-500 rounded-lg">
                  <CpuChipIcon className="w-8 h-8 text-cyan-400" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 font-mono">
                  NEURAL ORCHESTRA MATRIX
                </h1>
                <p className="text-sm text-cyan-400/80 font-mono">
                  {'>>>'} UNIFIED AGENT COMMAND CENTER v2.0
                </p>
              </div>
            </div>
            
            {/* Status Indicators */}
            <div className="flex items-center gap-4">
              <div className={`px-4 py-2 rounded-lg border ${wsConnected ? 'border-green-500 bg-green-500/10' : 'border-red-500 bg-red-500/10'}`}>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                  <span className={`text-sm font-mono ${wsConnected ? 'text-green-400' : 'text-red-400'}`}>
                    {wsConnected ? 'NEURAL LINK ACTIVE' : 'NEURAL LINK OFFLINE'}
                  </span>
                </div>
              </div>
              
              <Button
                onClick={loadAllData}
                className="gaming-btn-active"
              >
                <ArrowPathIcon className="w-4 h-4" />
                SYNC
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="gaming-card p-1 bg-gray-900/80 border border-cyan-500/30">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <ChartBarIcon className="w-4 h-4 mr-2" />
              DASHBOARD
            </TabsTrigger>
            <TabsTrigger value="agents" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <CpuChipIcon className="w-4 h-4 mr-2" />
              AGENTS
            </TabsTrigger>
            <TabsTrigger value="workflows" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <CircleStackIcon className="w-4 h-4 mr-2" />
              WORKFLOWS
            </TabsTrigger>
            <TabsTrigger value="executions" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <BoltIcon className="w-4 h-4 mr-2" />
              EXECUTIONS
            </TabsTrigger>
            <TabsTrigger value="channels" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              <ChatBubbleLeftRightIcon className="w-4 h-4 mr-2" />
              CHANNELS
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Statistics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="gaming-card border border-cyan-500/30 hover:border-cyan-400/50 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-purple-400 font-mono uppercase">NEURAL AGENTS</p>
                    <p className="text-3xl font-black text-cyan-400 font-mono">{stats.totalAgents}</p>
                    <p className="text-xs text-green-400 font-mono">{stats.activeAgents} ACTIVE</p>
                  </div>
                  <CpuChipIcon className="w-10 h-10 text-cyan-400/50" />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="gaming-card border border-purple-500/30 hover:border-purple-400/50 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-purple-400 font-mono uppercase">WORKFLOW MATRICES</p>
                    <p className="text-3xl font-black text-purple-400 font-mono">{stats.totalWorkflows}</p>
                    <p className="text-xs text-cyan-400 font-mono">{stats.runningExecutions} RUNNING</p>
                  </div>
                  <CircleStackIcon className="w-10 h-10 text-purple-400/50" />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="gaming-card border border-green-500/30 hover:border-green-400/50 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-purple-400 font-mono uppercase">EXECUTIONS</p>
                    <p className="text-3xl font-black text-green-400 font-mono">{stats.completedExecutions}</p>
                    <p className="text-xs text-yellow-400 font-mono">{stats.runningExecutions} ACTIVE</p>
                  </div>
                  <BoltIcon className="w-10 h-10 text-green-400/50" />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="gaming-card border border-orange-500/30 hover:border-orange-400/50 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-purple-400 font-mono uppercase">NEURAL CHANNELS</p>
                    <p className="text-3xl font-black text-orange-400 font-mono">{stats.activeChannels}</p>
                    <p className="text-xs text-cyan-400 font-mono">{stats.totalMessages} MESSAGES</p>
                  </div>
                  <ChatBubbleLeftRightIcon className="w-10 h-10 text-orange-400/50" />
                </div>
              </motion.div>
            </div>

            {/* Recent Activity */}
            <div className="gaming-card border border-cyan-500/30">
              <h3 className="text-xl font-bold text-cyan-400 mb-4 font-mono flex items-center">
                <SignalIcon className="w-5 h-5 mr-2" />
                NEURAL ACTIVITY STREAM
              </h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {executions.slice(0, 5).map((exec, index) => (
                  <div key={exec.id || `recent-exec-${index}`} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg border border-gray-800 hover:border-cyan-500/30 transition-all">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${
                        exec.status === 'running' ? 'bg-yellow-400 animate-pulse' :
                        exec.status === 'completed' ? 'bg-green-400' :
                        'bg-red-400'
                      }`} />
                      <div>
                        <p className="text-sm font-mono text-cyan-400">{exec.workflow_name}</p>
                        <p className="text-xs font-mono text-gray-500">
                          ID: {exec.id ? exec.id.slice(0, 8) + '...' : 'N/A'} | {exec.started_at ? new Date(exec.started_at).toLocaleTimeString() : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <Badge className={`font-mono text-xs ${
                      exec.status === 'running' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                      exec.status === 'completed' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                      'bg-red-500/20 text-red-400 border-red-500/30'
                    }`}>
                      {exec.status.toUpperCase()}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Agents Tab */}
          <TabsContent value="agents" className="space-y-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-cyan-400 font-mono">NEURAL AGENT REGISTRY</h2>
              <Button
                onClick={() => agentDiscoveryService.refreshDiscovery()}
                className="gaming-btn-active"
              >
                <ArrowPathIcon className="w-4 h-4" />
                SCAN AGENTS
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="gaming-card border border-purple-500/30 hover:border-cyan-400/50 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-cyan-400 font-mono text-sm uppercase">{agent.name}</h3>
                      <p className="text-xs text-gray-400 mt-1">{agent.description}</p>
                    </div>
                    <div className={`w-2 h-2 rounded-full ${
                      agent.status === 'active' ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
                    }`} />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs font-mono">
                        {agent.specialization?.toUpperCase() || 'GENERAL'}
                      </Badge>
                      {agent.llm_provider && (
                        <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30 text-xs font-mono">
                          {agent.llm_provider.toUpperCase()}
                        </Badge>
                      )}
                    </div>
                    
                    {agent.usage_stats && (
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-green-400">
                          {agent.usage_stats.usage_count} RUNS
                        </span>
                        <span className="text-cyan-400">
                          {(agent.usage_stats.success_rate * 100).toFixed(0)}% SUCCESS
                        </span>
                      </div>
                    )}
                    
                    <div className="pt-2 border-t border-gray-800">
                      <p className="text-xs text-purple-400 font-mono">
                        {agent.capabilities?.length || 0} CAPABILITIES
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          {/* Workflows Tab */}
          <TabsContent value="workflows" className="space-y-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-cyan-400 font-mono">WORKFLOW MATRICES</h2>
              <Button
                onClick={() => setCreateWorkflowOpen(true)}
                className="gaming-btn-active"
              >
                <PlusIcon className="w-4 h-4" />
                CREATE MATRIX
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {workflows.map((workflow) => (
                <motion.div
                  key={workflow.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="gaming-card border border-cyan-500/30 hover:border-purple-400/50 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-purple-400 font-mono text-sm uppercase">{workflow.name}</h3>
                      <p className="text-xs text-gray-400 mt-1">{workflow.description}</p>
                    </div>
                    {workflow.status && (
                      <div className={`w-2 h-2 rounded-full ${
                        workflow.status === 'running' ? 'bg-yellow-400 animate-pulse' :
                        workflow.status === 'completed' ? 'bg-green-400' :
                        workflow.status === 'failed' ? 'bg-red-400' :
                        'bg-gray-400'
                      }`} />
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-cyan-400">
                        {workflow.agent_count} AGENTS
                      </span>
                      <span className="text-purple-400">
                        {new Date(workflow.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <div className="flex gap-2 pt-2 border-t border-gray-800">
                      <Button
                        size="sm"
                        onClick={() => executeWorkflow(workflow)}
                        className="flex-1 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30"
                      >
                        <PlayIcon className="w-3 h-3" />
                        EXECUTE
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-purple-400 hover:text-purple-300"
                      >
                        <EyeIcon className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          {/* Executions Tab */}
          <TabsContent value="executions" className="space-y-6">
            <h2 className="text-2xl font-bold text-cyan-400 font-mono mb-4">EXECUTION MONITOR</h2>
            
            <div className="space-y-3">
              {executions.map((execution, index) => (
                <motion.div
                  key={execution.id || `execution-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="gaming-card border border-gray-800 hover:border-cyan-500/30 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${
                        execution.status === 'running' ? 'bg-yellow-400 animate-pulse' :
                        execution.status === 'completed' ? 'bg-green-400' :
                        execution.status === 'failed' ? 'bg-red-400' :
                        'bg-gray-400'
                      }`} />
                      <div>
                        <p className="font-mono text-cyan-400 font-bold">{execution.workflow_name}</p>
                        <p className="text-xs font-mono text-gray-500">
                          MATRIX_ID: {execution.id ? execution.id.slice(0, 8) + '...' : 'N/A'} | INITIATED: {execution.started_at ? new Date(execution.started_at).toLocaleString() : 'N/A'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {execution.progress && (
                        <div className="text-right">
                          <p className="text-xs font-mono text-purple-400">
                            STEP {execution.progress.current_step}/{execution.progress.total_steps}
                          </p>
                          <div className="w-32 h-1 bg-gray-800 rounded-full mt-1">
                            <div 
                              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all"
                              style={{ width: `${(execution.progress.current_step / execution.progress.total_steps) * 100}%` }}
                            />
                          </div>
                        </div>
                      )}
                      
                      <Badge className={`font-mono text-xs ${
                        execution.status === 'running' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                        execution.status === 'completed' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                        execution.status === 'failed' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                        'bg-gray-500/20 text-gray-400 border-gray-500/30'
                      }`}>
                        {execution.status.toUpperCase()}
                      </Badge>
                      
                      {execution.status === 'running' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-red-400 hover:text-red-300"
                        >
                          <XCircleIcon className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  {execution.progress && (
                    <div className="mt-3 pt-3 border-t border-gray-800">
                      <p className="text-xs font-mono text-cyan-400">{execution.progress.message}</p>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </TabsContent>

          {/* Channels Tab */}
          <TabsContent value="channels" className="space-y-6">
            <h2 className="text-2xl font-bold text-cyan-400 font-mono mb-4">NEURAL COMMUNICATION CHANNELS</h2>
            
            <div className="grid grid-cols-12 gap-6">
              {/* Channel List */}
              <div className="col-span-3">
                <div className="gaming-card border border-purple-500/30">
                  <h3 className="text-sm font-mono text-purple-400 uppercase mb-3">ACTIVE CHANNELS</h3>
                  <div className="space-y-2">
                    {channels.map((channel) => (
                      <div
                        key={channel.id}
                        onClick={() => loadChannelMessages(channel)}
                        className={`p-2 rounded-lg border cursor-pointer transition-all ${
                          selectedChannel?.id === channel.id
                            ? 'border-cyan-400 bg-cyan-500/10'
                            : 'border-gray-800 hover:border-purple-500/50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <HashtagIcon className="w-3 h-3 text-cyan-400" />
                            <span className="text-xs font-mono text-cyan-400">
                              {channel.display_name || channel.name}
                            </span>
                          </div>
                          {channel.is_active && (
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{channel.message_count} messages</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Messages */}
              <div className="col-span-9">
                <div className="gaming-card border border-cyan-500/30 h-[600px] flex flex-col">
                  {selectedChannel ? (
                    <>
                      <div className="border-b border-gray-800 pb-3 mb-3">
                        <h3 className="font-mono text-cyan-400 font-bold flex items-center gap-2">
                          <HashtagIcon className="w-4 h-4" />
                          {selectedChannel.display_name || selectedChannel.name}
                        </h3>
                        <p className="text-xs text-gray-500 mt-1">{selectedChannel.description}</p>
                      </div>
                      
                      <div className="flex-1 overflow-y-auto space-y-3">
                        {channelMessages.map((message) => (
                          <div key={message.id} className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                              <CpuChipIcon className="w-4 h-4 text-white" />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-mono text-cyan-400 font-bold">
                                  {message.agent_name || 'SYSTEM'}
                                </span>
                                <span className="text-xs font-mono text-gray-500">
                                  {new Date(message.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                              <p className="text-sm text-gray-300">{message.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center">
                        <ChatBubbleLeftRightIcon className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                        <p className="text-gray-500 font-mono">SELECT A CHANNEL</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Create Workflow Dialog */}
      <Dialog open={createWorkflowOpen} onOpenChange={setCreateWorkflowOpen}>
        <DialogContent className="max-w-3xl bg-gray-900 border border-cyan-500/30">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-cyan-400 font-mono">
              CREATE NEURAL WORKFLOW MATRIX
            </DialogTitle>
            <DialogDescription className="text-purple-400 font-mono">
              Configure multi-agent collaboration protocol
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 mt-4">
            <div>
              <Label className="text-cyan-400 font-mono text-sm">MATRIX NAME</Label>
              <input
                type="text"
                value={workflowForm.name}
                onChange={(e) => setWorkflowForm(prev => ({ ...prev, name: e.target.value }))}
                className="w-full mt-1 px-3 py-2 bg-black border border-cyan-500/30 rounded-lg text-cyan-400 font-mono focus:border-cyan-400 focus:outline-none"
                placeholder="Enter workflow name..."
              />
            </div>
            
            <div>
              <Label className="text-cyan-400 font-mono text-sm">DESCRIPTION</Label>
              <textarea
                value={workflowForm.description}
                onChange={(e) => setWorkflowForm(prev => ({ ...prev, description: e.target.value }))}
                className="w-full mt-1 px-3 py-2 bg-black border border-cyan-500/30 rounded-lg text-cyan-400 font-mono focus:border-cyan-400 focus:outline-none"
                rows={3}
                placeholder="Describe workflow purpose..."
              />
            </div>
            
            <div>
              <Label className="text-cyan-400 font-mono text-sm">COORDINATION STRATEGY</Label>
              <Select
                value={workflowForm.coordination_strategy}
                onValueChange={(value: any) => setWorkflowForm(prev => ({ ...prev, coordination_strategy: value }))}
              >
                <SelectTrigger className="w-full mt-1 bg-black border-cyan-500/30 text-cyan-400 font-mono">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sequential">SEQUENTIAL</SelectItem>
                  <SelectItem value="parallel">PARALLEL</SelectItem>
                  <SelectItem value="adaptive">ADAPTIVE</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-cyan-400 font-mono text-sm mb-3 block">
                SELECT AGENTS ({selectedAgents.size} SELECTED)
              </Label>
              <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                {agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center space-x-2 p-2 bg-black border border-gray-800 rounded-lg hover:border-cyan-500/30 transition-all"
                  >
                    <Checkbox
                      id={agent.id}
                      checked={selectedAgents.has(agent.id)}
                      onCheckedChange={(checked) => {
                        const newSelection = new Set(selectedAgents);
                        if (checked) {
                          newSelection.add(agent.id);
                        } else {
                          newSelection.delete(agent.id);
                        }
                        setSelectedAgents(newSelection);
                      }}
                      className="border-cyan-500/50 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500"
                    />
                    <label
                      htmlFor={agent.id}
                      className="text-xs font-mono text-cyan-400 cursor-pointer flex-1"
                    >
                      {agent.name}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-800">
              <Button
                variant="outline"
                onClick={() => setCreateWorkflowOpen(false)}
                className="border-gray-700 text-gray-400 hover:border-gray-600"
              >
                CANCEL
              </Button>
              <Button
                onClick={handleCreateWorkflow}
                className="gaming-btn-active"
              >
                <PlusIcon className="w-4 h-4" />
                CREATE MATRIX
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}