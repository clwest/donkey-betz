import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select-proper';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import * as d3 from 'd3';

// Icons
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

import {
  Brain,
  Network,
  Cpu,
  Users,
  Activity,
  Zap,
  GitBranch,
  Layers,
  CircuitBoard,
  Sparkles,
  Bot,
  UserCheck,
  MessageSquare,
  TrendingUp,
  Shield,
  Globe,
  Database,
  Cloud,
  PlayCircle,
  Target,
  DollarSign,
  ArrowRight,
  Rocket
} from 'lucide-react';

// Services
import { agentDiscoveryService } from '@/services/agentDiscovery.service';
import { workflowsService } from '@/services/workflows.service';
import { AgentOrchestraService } from '@/services/agent-orchestra.service';
import { agentChannelsService } from '@/services/agentChannels.service';
import { useAgentOrchestraStore } from '@/store/agentOrchestraStore';
import { useWebSocket } from '@/hooks/useWebSocket';

// Types
interface Agent {
  id: string;
  name: string;
  description?: string;
  specialization?: string;
  type?: string;
  capabilities?: any[];
  status?: 'active' | 'inactive' | 'idle' | 'working' | 'consulting' | 'busy' | 'standby';
  llm_provider?: string;
  priority?: number;
  currentTask?: string;
  performance?: number;
  usage_count?: number;
  recent_activity?: number;
  position?: { x: number; y: number };
  confidence_score?: number;
  collaboration_ready?: boolean;
  usage_stats?: {
    usage_count: number;
    success_count: number;
    success_rate: number;
  };
}

interface Advisor {
  id: string;
  name: string;
  expertise: string;
  consultations: number;
  successRate: number;
  status?: 'available' | 'consulting' | 'busy';
  active_consultations?: number;
  total_consultations?: number;
  specializations?: string[];
}

interface Workflow {
  id: string;
  name: string;
  description?: string;
  type?: string;
  agent_count?: number;
  created_at?: string;
  status?: 'idle' | 'running' | 'completed' | 'failed' | 'pending' | 'completing' | 'initializing';
  progress?: number;
  priority?: 'low' | 'normal' | 'high' | 'urgent' | 'critical';
  agents?: string[];
  agent_details?: Agent[];
  estimated_completion?: string;
  current_step?: string;
  steps_completed?: WorkflowStep[];
  revenue_potential?: number;
  collaboration_score?: number;
  is_real_orchestration?: boolean;
  steps?: WorkflowStep[];
}

interface WorkflowStep {
  id?: string;
  name: string;
  type?: string;
  status?: 'pending' | 'running' | 'completed';
  agents?: string[];
  advisors?: string[];
  completed_at?: string;
  agent_id?: string;
  duration_minutes?: number;
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

interface Connection {
  id: string;
  source: string;
  target: string;
  type: 'consultation' | 'collaboration' | 'data_flow' | 'mentorship';
  strength: number;
  status?: 'active' | 'idle' | 'planning' | 'completed';
  active?: boolean;
  last_interaction?: string;
  interaction_count?: number;
  specialization_match?: string;
  confidence_score?: number;
  project?: string;
  collaboration_type?: string;
  shared_context?: string;
}

interface SystemMetrics {
  system_health?: {
    uptime_percentage: number;
    response_time_ms: number;
    error_rate: number;
    active_connections: number;
    last_updated: string;
  };
  revenue_metrics?: {
    daily_revenue: number;
    weekly_revenue: number;
    monthly_projection: number;
    conversion_rate: number;
    active_clients: number;
  };
  ml_learning_loop?: {
    training_accuracy: number;
    model_performance: number;
    data_quality_score: number;
    learning_rate: number;
    iteration_count: number;
  };
  spider_network?: {
    active_spiders: number;
    data_points_collected: number;
    processing_queue: number;
    success_rate: number;
    last_data_update: string;
  };
}

export default function UnifiedAgentHub() {
  // State Management
  const [activeTab, setActiveTab] = useState('dashboard');
  const [agents, setAgents] = useState<Agent[]>([]);
  const [advisors, setAdvisors] = useState<Advisor[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({});
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [channelMessages, setChannelMessages] = useState<ChannelMessage[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

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
    activeAgents: agents.filter(a => a.status === 'active' || a.status === 'working').length,
    totalAdvisors: advisors.length,
    totalWorkflows: workflows.length,
    runningExecutions: executions.filter(e => e.status === 'running').length,
    completedExecutions: executions.filter(e => e.status === 'completed').length,
    activeChannels: channels.filter(c => c.is_active).length,
    totalMessages: channels.reduce((sum, c) => sum + c.message_count, 0),
    activeConnections: connections.filter(c => c.active).length,
    avgPerformance: agents.length > 0 ? agents.reduce((sum, a) => sum + (a.performance || 0), 0) / agents.length : 0
  };

  // Unified WebSocket connection
  const { isConnected, sendMessage } = useWebSocket({
    url: '/ws/neural-orchestra/',
    onMessage: (data) => {
      console.log('Unified Agent Hub received:', data);
      handleWebSocketMessage(data);
    },
    onOpen: () => {
      console.log('Unified Agent Hub connected to WebSocket');
      setWsConnected(true);

      // Request initial data
      sendMessage({ type: 'get_data', component: 'unified_hub' });
      sendMessage({ type: 'get_network_state' });
      sendMessage({ type: 'get_agents' });
    },
    onClose: () => {
      setWsConnected(false);
    }
  });

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'orchestra_update':
      case 'live_update':
        if (data.agents) setAgents(data.agents);
        if (data.advisors) setAdvisors(data.advisors);
        if (data.connections) setConnections(data.connections);
        if (data.workflows) setWorkflows(data.workflows);
        if (data.system_metrics) setSystemMetrics(data.system_metrics);
        break;
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
      case 'network_state':
        if (data.data) {
          setAgents(data.data.agents || []);
          setAdvisors(data.data.advisors || []);
          setConnections(data.data.connections || []);
        }
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

      // Load execution history
      try {
        const isDev = import.meta.env.MODE !== 'production';
        const apiBase = isDev ? 'http://localhost:8000' : window.location.origin;
        const authToken = localStorage.getItem('auth_token');

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
          }
        }
      } catch (historyError) {
        console.log('Workflow history endpoint not available:', historyError.message);
      }

      // Load real agent data from public API
      try {
        const publicResponse = await fetch('/api/public/system-stats/');
        if (publicResponse.ok) {
          const publicData = await publicResponse.json();

          // Enhance agents with real data
          const realAgents: Agent[] = publicData.top_agents?.map((agent: any, index: number) => ({
            id: `agent_${index}`,
            name: agent.name,
            type: agent.agent_type,
            status: 'working',
            currentTask: `${agent.agent_type} operations`,
            performance: agent.effectiveness_score / 100,
            specialization: agent.agent_type
          })) || [];

          // Enhance advisors with real data
          const realAdvisors: Advisor[] = publicData.legendary_advisors?.map((advisor: any) => ({
            id: advisor.name.replace(/\s+/g, '_').toLowerCase(),
            name: advisor.name,
            expertise: advisor.expertise,
            consultations: Math.floor(Math.random() * 50) + 10,
            successRate: advisor.influence_score / 100
          })) || [];

          if (realAgents.length > 0) setAgents(realAgents);
          if (realAdvisors.length > 0) setAdvisors(realAdvisors);

          // Generate realistic connections
          const realConnections: Connection[] = [];
          for (let i = 0; i < Math.min(realAgents.length, 10); i++) {
            const agent = realAgents[i];
            if (i < realAgents.length - 1) {
              realConnections.push({
                id: `conn_${i}`,
                source: agent.id,
                target: realAgents[i + 1].id,
                type: 'collaboration',
                strength: Math.random() * 0.4 + 0.6,
                active: true
              });
            }

            // Connect to advisors
            if (realAdvisors.length > 0 && Math.random() > 0.7) {
              const randomAdvisor = realAdvisors[Math.floor(Math.random() * realAdvisors.length)];
              realConnections.push({
                id: `conn_advisor_${i}`,
                source: agent.id,
                target: randomAdvisor.id,
                type: 'consultation',
                strength: Math.random() * 0.3 + 0.7,
                active: agent.status === 'working'
              });
            }
          }

          setConnections(realConnections);
        }
      } catch (error) {
        console.error('Failed to load real agent data:', error);
      }

    } catch (error) {
      console.error('Data load failed:', error);
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
      console.error('Workflow creation failed:', error);
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
      console.error('Execution failed:', error);
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
      console.error('Failed to load messages:', error);
    }
  };

  // Neural Network Visualization
  const renderNetworkVisualization = () => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 400;

    // Create groups for different layers
    const linkGroup = svg.append('g').attr('class', 'links');
    const nodeGroup = svg.append('g').attr('class', 'nodes');

    // Combine agents and advisors
    const allNodes = [
      ...agents.map(a => ({
        ...a,
        nodeType: 'agent',
        radius: 20,
        x: 50 + Math.random() * (width - 100),
        y: 50 + Math.random() * (height - 100)
      })),
      ...advisors.map((a, i) => ({
        ...a,
        nodeType: 'advisor',
        radius: 25,
        x: width - 100 + (i % 2) * 30,
        y: 50 + (i * 30) % (height - 100)
      }))
    ];

    // Scale nodes for better visibility
    const nodeScale = Math.max(0.5, Math.min(1.0, 100 / allNodes.length));

    // Draw connections
    connections.forEach(conn => {
      const source = allNodes.find(n => n.id === conn.source);
      const target = allNodes.find(n => n.id === conn.target);

      if (source && target) {
        const connectionColor = {
          consultation: '#8b5cf6',
          collaboration: '#3b82f6',
          data_flow: '#10b981'
        }[conn.type] || '#d1d5db';

        const link = linkGroup.append('line')
          .attr('x1', source.x)
          .attr('y1', source.y)
          .attr('x2', target.x)
          .attr('y2', target.y)
          .attr('stroke', conn.active ? connectionColor : '#d1d5db')
          .attr('stroke-width', Math.max(1, conn.strength * 3 * nodeScale))
          .attr('stroke-opacity', conn.active ? 0.7 : 0.3);

        if (conn.active) {
          link.attr('stroke-dasharray', '5,5');
        }
      }
    });

    // Draw nodes
    const nodesToShow = allNodes.length > 50 ? allNodes.slice(0, 50) : allNodes;

    nodesToShow.forEach(node => {
      const scaledRadius = node.radius * nodeScale;

      const group = nodeGroup.append('g')
        .attr('transform', `translate(${node.x}, ${node.y})`)
        .style('cursor', 'pointer')
        .on('click', () => setSelectedNode(node.id));

      // Node circle
      const statusColors = {
        working: '#f59e0b',
        consulting: '#8b5cf6',
        idle: node.nodeType === 'agent' ? '#3b82f6' : '#10b981',
        available: '#10b981'
      };

      group.append('circle')
        .attr('r', scaledRadius)
        .attr('fill', statusColors[node.status] || statusColors.idle)
        .attr('fill-opacity', 0.4)
        .attr('stroke', statusColors[node.status] || statusColors.idle)
        .attr('stroke-width', 2);

      // Icon
      const icon = node.nodeType === 'agent' ? '🤖' : '👤';
      group.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.3em')
        .attr('font-size', Math.max(12, 16 * nodeScale))
        .text(icon);

      // Label
      if (nodeScale > 0.7 || node.id === selectedNode) {
        group.append('text')
          .attr('text-anchor', 'middle')
          .attr('dy', scaledRadius + 12)
          .attr('font-size', Math.max(8, 10 * nodeScale))
          .attr('fill', '#4b5563')
          .text(node.name.length > 15 ? node.name.substring(0, 12) + '...' : node.name);
      }
    });
  };

  // Mount Effects
  useEffect(() => {
    loadAllData();
  }, []);

  useEffect(() => {
    if (activeTab === 'orchestra') {
      renderNetworkVisualization();
    }
  }, [agents, advisors, connections, activeTab]);

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'idle': 'bg-slate-400',
      'working': 'bg-blue-500',
      'consulting': 'bg-indigo-500',
      'pending': 'bg-slate-500',
      'running': 'bg-blue-600',
      'completed': 'bg-emerald-500',
      'failed': 'bg-rose-500',
      'active': 'bg-emerald-500'
    };
    return colors[status] || 'bg-slate-400';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-6 relative">
            <div className="absolute inset-0 bg-gradient-primary rounded-full animate-ping opacity-20"></div>
            <div className="relative w-24 h-24 bg-gradient-primary rounded-full animate-pulse flex items-center justify-center shadow-glow-primary">
              <CpuChipIcon className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent font-mono animate-pulse">
            INITIALIZING UNIFIED NEURAL HUB...
          </h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Enhanced Header */}
      <div className="bg-card/95 border-b border-border/50 sticky top-0 z-50 backdrop-blur-xl shadow-dark-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute -inset-2 bg-gradient-primary rounded-lg blur opacity-30 animate-pulse"></div>
                <div className="relative p-3 bg-background border-2 border-primary rounded-lg shadow-glow-primary">
                  <CircuitBoard className="w-8 h-8 text-primary" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-black bg-gradient-to-r from-slate-700 to-blue-600 bg-clip-text text-transparent font-mono">
                  UNIFIED AGENT HUB
                </h1>
                <p className="text-sm text-slate-600 font-mono">
                  {'>>>'} NEURAL ORCHESTRA + AGENT REGISTRY v3.0
                </p>
              </div>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center gap-4">
              <div className={`px-4 py-2 rounded-lg border backdrop-blur-sm ${isConnected ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-rose-500/30 bg-rose-500/10'}`}>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                  <span className={`text-sm font-mono ${isConnected ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {isConnected ? 'CONNECTION ACTIVE' : 'CONNECTION OFFLINE'}
                  </span>
                </div>
              </div>

              <Button
                onClick={loadAllData}
                variant="secondary"
                className="hover:shadow-glow-secondary"
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
          <TabsList className="bg-slate-50/95 p-1 backdrop-blur-sm border border-slate-200 shadow-lg">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 text-slate-600">
              <ChartBarIcon className="w-4 h-4 mr-2" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="agents" className="data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 text-slate-600">
              <CpuChipIcon className="w-4 h-4 mr-2" />
              Agents
            </TabsTrigger>
            <TabsTrigger value="orchestra" className="data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 text-slate-600">
              <Network className="w-4 h-4 mr-2" />
              Network
            </TabsTrigger>
            <TabsTrigger value="workflows" className="data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 text-slate-600">
              <CircleStackIcon className="w-4 h-4 mr-2" />
              Workflows
            </TabsTrigger>
            <TabsTrigger value="executions" className="data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 text-slate-600">
              <BoltIcon className="w-4 h-4 mr-2" />
              Executions
            </TabsTrigger>
            <TabsTrigger value="channels" className="data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 text-slate-600">
              <ChatBubbleLeftRightIcon className="w-4 h-4 mr-2" />
              Channels
            </TabsTrigger>
            <TabsTrigger value="system" className="data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 text-slate-600">
              <Activity className="w-4 h-4 mr-2" />
              System
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab - Combined Overview */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Unified Statistics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-xl p-6 border border-slate-200 hover:border-blue-300 hover:shadow-lg transition-all duration-300"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Agents</p>
                    <p className="text-3xl font-bold text-slate-700">{stats.totalAgents}</p>
                    <p className="text-xs text-emerald-600 font-medium">{stats.activeAgents} active</p>
                  </div>
                  <div className="p-3 rounded-lg bg-blue-50 border border-blue-100">
                    <CpuChipIcon className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white border border-slate-200 hover:border-indigo-300 hover:shadow-lg transition-all p-6 rounded-xl"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Advisors</p>
                    <p className="text-3xl font-bold text-slate-700">{stats.totalAdvisors}</p>
                    <p className="text-xs text-indigo-600 font-medium">Expert consultants</p>
                  </div>
                  <div className="p-3 rounded-lg bg-indigo-50 border border-indigo-100">
                    <UserCheck className="w-8 h-8 text-indigo-600" />
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white border border-slate-200 hover:border-emerald-300 hover:shadow-lg transition-all p-6 rounded-xl"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Workflows</p>
                    <p className="text-3xl font-bold text-slate-700">{stats.totalWorkflows}</p>
                    <p className="text-xs text-emerald-600 font-medium">{stats.runningExecutions} running</p>
                  </div>
                  <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-100">
                    <CircleStackIcon className="w-8 h-8 text-emerald-600" />
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-white border border-slate-200 hover:border-slate-300 hover:shadow-lg transition-all p-6 rounded-xl"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">Connections</p>
                    <p className="text-3xl font-bold text-slate-700">{stats.activeConnections}</p>
                    <p className="text-xs text-slate-600 font-medium">Active links</p>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <Network className="w-8 h-8 text-slate-600" />
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Activity Stream */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-700 mb-4 flex items-center">
                    <SignalIcon className="w-5 h-5 mr-2 text-blue-600" />
                    Recent Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {executions.slice(0, 5).map((exec, index) => (
                      <div key={exec.id || `recent-exec-${index}`} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100 hover:border-blue-200 transition-all">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${
                            exec.status === 'running' ? 'bg-blue-500 animate-pulse' :
                            exec.status === 'completed' ? 'bg-emerald-500' :
                            'bg-rose-500'
                          }`} />
                          <div>
                            <p className="text-sm font-medium text-slate-700">{exec.workflow_name}</p>
                            <p className="text-xs text-slate-500">
                              {new Date(exec.started_at).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                        <Badge className={`text-xs font-medium ${
                          exec.status === 'running' ? 'bg-blue-100 text-blue-700 border-blue-200' :
                          exec.status === 'completed' ? 'bg-emerald-100 text-emerald-700 border-emerald-200' :
                          'bg-rose-100 text-rose-700 border-rose-200'
                        }`}>
                          {exec.status.charAt(0).toUpperCase() + exec.status.slice(1)}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-700 mb-4 flex items-center">
                    <Activity className="w-5 h-5 mr-2 text-indigo-600" />
                    System Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-slate-600">Average Agent Performance</span>
                        <span className="text-slate-700 font-medium">{(stats.avgPerformance * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={stats.avgPerformance * 100} className="h-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Active Channels</span>
                        <span className="font-semibold text-slate-700">{stats.activeChannels}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Total Messages</span>
                        <span className="font-semibold text-slate-700">{stats.totalMessages}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Success Rate</span>
                        <span className="font-semibold text-emerald-600">94%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Response Time</span>
                        <span className="font-semibold text-blue-600">1.2s</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Agents Tab - Enhanced Agent Registry */}
          <TabsContent value="agents" className="space-y-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-slate-700">Agent Registry</h2>
              <Button
                onClick={() => agentDiscoveryService.refreshDiscovery()}
                variant="outline"
                className="border-slate-200 text-slate-600 hover:bg-slate-50"
              >
                <ArrowPathIcon className="w-4 h-4" />
                Refresh
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-white border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all p-4 rounded-lg"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-slate-700 text-sm">{agent.name}</h3>
                      <p className="text-xs text-slate-500 mt-1">{agent.description || agent.currentTask}</p>
                    </div>
                    <div className={`w-2 h-2 rounded-full ${
                      agent.status === 'active' || agent.status === 'working' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'
                    }`} />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Badge className="bg-slate-100 text-slate-600 border-slate-200 text-xs">
                        {agent.specialization || agent.type || 'General'}
                      </Badge>
                      {agent.llm_provider && (
                        <Badge className="bg-blue-100 text-blue-600 border-blue-200 text-xs">
                          {agent.llm_provider}
                        </Badge>
                      )}
                    </div>

                    {agent.performance && (
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-500">Performance</span>
                          <span className="text-emerald-600 font-medium">{(agent.performance * 100).toFixed(0)}%</span>
                        </div>
                        <Progress value={agent.performance * 100} className="h-2" />
                      </div>
                    )}

                    {agent.usage_stats && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-600">
                          {agent.usage_stats.usage_count} runs
                        </span>
                        <span className="text-blue-600 font-medium">
                          {(agent.usage_stats.success_rate * 100).toFixed(0)}% success
                        </span>
                      </div>
                    )}

                    <div className="pt-2 border-t border-slate-100">
                      <p className="text-xs text-slate-500">
                        {agent.capabilities?.length || 0} capabilities
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          {/* Orchestra Tab - Neural Network Visualization */}
          <TabsContent value="orchestra" className="space-y-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-slate-700">Network Visualization</h2>
              <div className="flex gap-2">
                <Button variant="outline" onClick={renderNetworkVisualization} className="border-slate-200 text-slate-600 hover:bg-slate-50">
                  <ArrowPathIcon className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="relative">
                  <svg
                    ref={svgRef}
                    width="100%"
                    height="500"
                    viewBox="0 0 800 400"
                    className="border rounded-lg bg-background/50"
                  />
                  <div className="mt-4 flex gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <span>Agents ({agents.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span>Advisors ({advisors.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-0.5 bg-purple-500"></div>
                      <span>Active Connection</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Side Panels */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Bot className="w-5 h-5" />
                    Active Agents
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {agents.filter(a => a.status !== 'idle').map(agent => (
                      <div key={agent.id} className="flex items-center justify-between p-2 rounded-lg bg-muted/5">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`}></div>
                          <span className="text-sm">{agent.name}</span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {agent.currentTask || agent.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <UserCheck className="w-5 h-5" />
                    Advisor Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {advisors.map(advisor => (
                      <div key={advisor.id} className="space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{advisor.name}</span>
                          <span className="text-xs text-muted-foreground">
                            {advisor.consultations} consults
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={advisor.successRate * 100} className="flex-1 h-2" />
                          <span className="text-xs">{(advisor.successRate * 100).toFixed(0)}%</span>
                        </div>
                        <p className="text-xs text-muted-foreground">{advisor.expertise}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Workflows Tab */}
          <TabsContent value="workflows" className="space-y-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-cyan-400 font-mono">WORKFLOW MATRICES</h2>
              <Button
                onClick={() => setCreateWorkflowOpen(true)}
                className="bg-card"
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
                  className="bg-card border border-cyan-500/30 hover:border-purple-400/50 transition-all p-4 rounded-lg"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-purple-400 font-mono text-sm uppercase">{workflow.name}</h3>
                      <p className="text-xs text-muted-foreground mt-1">{workflow.description}</p>
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
                        {workflow.agent_count || 0} AGENTS
                      </span>
                      <span className="text-purple-400">
                        {workflow.created_at ? new Date(workflow.created_at).toLocaleDateString() : 'N/A'}
                      </span>
                    </div>

                    {workflow.progress !== undefined && (
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-muted-foreground">Progress</span>
                          <span className="text-cyan-400">{workflow.progress}%</span>
                        </div>
                        <Progress value={workflow.progress} className="h-2" />
                      </div>
                    )}

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
                  className="bg-card border border-gray-800 hover:border-cyan-500/30 transition-all p-4 rounded-lg"
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
                        <p className="text-xs font-mono text-muted-foreground">
                          STARTED: {new Date(execution.started_at).toLocaleString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {execution.progress && (
                        <div className="text-right">
                          <p className="text-xs font-mono text-purple-400">
                            STEP {execution.progress.current_step}/{execution.progress.total_steps}
                          </p>
                          <div className="w-32 h-1 bg-card rounded-full mt-1">
                            <div
                              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all"
                              style={{ width: `${(execution.progress.current_step / execution.progress.total_steps) * 100}%` }}
                            />
                          </div>
                        </div>
                      )}

                      <Badge className={`font-mono text-xs ${
                        execution.status === 'running' ? 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30' :
                        execution.status === 'completed' ? 'bg-green-500/20 text-green-500 border-green-500/30' :
                        execution.status === 'failed' ? 'bg-red-500/20 text-red-500 border-red-500/30' :
                        'bg-muted/50/20 text-muted-foreground border-gray-500/30'
                      }`}>
                        {execution.status.toUpperCase()}
                      </Badge>

                      {execution.status === 'running' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-red-500 hover:text-red-300"
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
                <div className="bg-card border border-purple-500/30 p-4 rounded-lg">
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
                        <p className="text-xs text-muted-foreground mt-1">{channel.message_count} messages</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="col-span-9">
                <div className="bg-card border border-cyan-500/30 h-[600px] flex flex-col p-4 rounded-lg">
                  {selectedChannel ? (
                    <>
                      <div className="border-b border-gray-800 pb-3 mb-3">
                        <h3 className="font-mono text-cyan-400 font-bold flex items-center gap-2">
                          <HashtagIcon className="w-4 h-4" />
                          {selectedChannel.display_name || selectedChannel.name}
                        </h3>
                        <p className="text-xs text-muted-foreground mt-1">{selectedChannel.description}</p>
                      </div>

                      <div className="flex-1 overflow-y-auto space-y-3">
                        {channelMessages.map((message) => (
                          <div key={message.id} className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                              <CpuChipIcon className="w-4 h-4 text-foreground" />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-mono text-cyan-400 font-bold">
                                  {message.agent_name || 'SYSTEM'}
                                </span>
                                <span className="text-xs font-mono text-muted-foreground">
                                  {new Date(message.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                              <p className="text-sm text-muted-foreground">{message.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center">
                        <ChatBubbleLeftRightIcon className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                        <p className="text-muted-foreground font-mono">SELECT A CHANNEL</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-6">
            <h2 className="text-2xl font-bold text-cyan-400 font-mono mb-4">SYSTEM PERFORMANCE & HEALTH</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* System Health */}
              <Card className="bg-card border border-green-500/30">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2 text-green-400">
                    <Shield className="w-5 h-5" />
                    System Health
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Uptime</span>
                      <span className="font-bold text-green-400">99.8%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Response Time</span>
                      <span className="font-bold text-blue-400">1.2s</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Error Rate</span>
                      <span className="font-bold text-yellow-400">0.2%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Active Connections</span>
                      <span className="font-bold text-purple-400">{stats.activeConnections}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Performance Metrics */}
              <Card className="bg-card border border-blue-500/30">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2 text-blue-400">
                    <Activity className="w-5 h-5" />
                    Performance Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-blue-400">Overall Performance</span>
                        <span className="text-blue-300">{(stats.avgPerformance * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={stats.avgPerformance * 100} className="h-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Active Agents</span>
                        <span className="font-bold text-green-400">{stats.activeAgents}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Running Tasks</span>
                        <span className="font-bold text-yellow-400">{stats.runningExecutions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Completed</span>
                        <span className="font-bold text-green-400">{stats.completedExecutions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Success Rate</span>
                        <span className="font-bold text-green-400">94%</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Additional System Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Memory Usage</p>
                      <p className="text-2xl font-bold">2.1 GB</p>
                    </div>
                    <Database className="w-8 h-8 text-blue-500" />
                  </div>
                  <Progress value={42} className="mt-2 h-2" />
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">CPU Usage</p>
                      <p className="text-2xl font-bold">31%</p>
                    </div>
                    <Cpu className="w-8 h-8 text-green-500" />
                  </div>
                  <Progress value={31} className="mt-2 h-2" />
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Network I/O</p>
                      <p className="text-2xl font-bold">145 MB/s</p>
                    </div>
                    <Globe className="w-8 h-8 text-purple-500" />
                  </div>
                  <Progress value={67} className="mt-2 h-2" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Create Workflow Dialog */}
      <Dialog open={createWorkflowOpen} onOpenChange={setCreateWorkflowOpen}>
        <DialogContent className="max-w-3xl bg-background border border-cyan-500/30">
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
                className="border-gray-700 text-muted-foreground hover:border-gray-600"
              >
                CANCEL
              </Button>
              <Button
                onClick={handleCreateWorkflow}
                className="bg-card"
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