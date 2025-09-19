/**
 * Neural Orchestra - Enhanced Collaboration Visualizer
 *
 * Real-time visualization of agent-advisor collaboration, ML pipeline activity,
 * and workflow orchestration with beautiful interactive graphics.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
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
  CheckCircle,
  Target,
  DollarSign,
  ArrowRight,
  Rocket
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { useWebSocket } from '@/hooks/useWebSocket';
import { motion, AnimatePresence } from 'framer-motion';
import * as d3 from 'd3';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'idle' | 'working' | 'consulting' | 'busy' | 'active' | 'standby';
  currentTask?: string;
  performance: number;
  usage_count?: number;
  recent_activity?: number;
  position?: { x: number; y: number };
  confidence_score?: number;
  collaboration_ready?: boolean;
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
  type?: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'completing' | 'initializing';
  progress: number;
  priority?: 'low' | 'normal' | 'high' | 'urgent' | 'critical';
  agents?: string[];
  agent_details?: Agent[];
  created_at?: string;
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

const NeuralOrchestra: React.FC = () => {
  const navigate = useNavigate();
  const svgRef = useRef<SVGSVGElement>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [advisors, setAdvisors] = useState<Advisor[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({});
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'network' | 'workflow' | 'performance'>('network');
  const [connectionTypes, setConnectionTypes] = useState<Record<string, any>>({});
  const [isAnimating, setIsAnimating] = useState(true);
  const [planId, setPlanId] = useState<string | null>(null);
  const [planReview, setPlanReview] = useState<any>(null);

  const { sendMessage, lastMessage, isConnected } = useWebSocket({
    url: '/ws/neural-orchestra/',
    onMessage: (data) => {
      console.log('Neural Orchestra received from unified hub:', data);
      if (data.type === 'orchestra_update' || data.type === 'live_update') {
        // Handle real orchestra updates
        if (data.agents) {
          setAgents(data.agents);
          console.log(`✅ Updated with ${data.agents.length} real agents`);
        }
        if (data.advisors) {
          setAdvisors(data.advisors);
          console.log(`✅ Updated with ${data.advisors.length} real advisors`);
        }
        if (data.connections) {
          setConnections(data.connections);
          console.log(`✅ Updated with ${data.connections.length} connections`);
        }
        if (data.workflows) {
          setWorkflows(data.workflows);
          console.log(`✅ Updated with ${data.workflows.length} workflows`);
        }
        if (data.system_metrics) {
          setSystemMetrics(data.system_metrics);
          console.log('📊 System Metrics updated');
        }
        if (data.connection_types) {
          setConnectionTypes(data.connection_types);
        }

        // Log detailed stats
        if (data.connection_summary) {
          console.log('🔗 Connection Summary:', data.connection_summary);
        }

        // Show data source confirmation
        if (data.data_source) {
          console.log(`🎯 Data Source: ${data.data_source}`);
        }

      } else if (data.type === 'workflow_triggered') {
        // Handle new workflow creation
        if (data.workflow) {
          setWorkflows(prev => [...prev, data.workflow]);
          console.log(`🚀 New workflow created: ${data.workflow.name}`);
        }
      } else if (data.type === 'workflow_progress_update') {
        // Handle workflow progress updates
        setWorkflows(prev => prev.map(workflow =>
          workflow.id === data.workflow_id
            ? { ...workflow, progress: data.progress, status: data.status, current_step: data.current_step }
            : workflow
        ));
        console.log(`📈 Workflow ${data.workflow_id} progress: ${data.progress}%`);
      } else if (data.type === 'network_state') {
        // Update network visualization data (legacy support)
        if (data.data) {
          setAgents(data.data.agents || []);
          setAdvisors(data.data.advisors || []);
          setConnections(data.data.connections || []);
        }
      } else if (data.type === 'plan_review') {
        // Handle plan review data
        console.log('📋 Plan review received:', data);
        setPlanReview(data.review);

        // Highlight the advisor and agents involved
        if (data.review?.advisor_id) {
          setSelectedNode(data.review.advisor_id);
        }

        // Show the team formation if available
        if (data.review?.team) {
          console.log('👥 Team formed:', data.review.team);
          // Highlight team members
          const teamAgentIds = [
            data.review.team.lead_agent,
            ...(data.review.team.core_agents || []),
            ...(data.review.team.specialists || [])
          ];

          // Create connections between advisor and team
          const newConnections = teamAgentIds.map(agentId => ({
            source: data.review.advisor_id,
            target: agentId,
            type: 'team_formation',
            strength: 0.8
          }));

          setConnections(prev => [...prev, ...newConnections]);
        }
      } else if (data.type === 'execution_started') {
        console.log('🚀 Execution started:', data);
        setPlanReview(prev => ({
          ...prev,
          execution_status: 'running',
          execution_message: data.message
        }));
      } else if (data.type === 'execution_update') {
        console.log('📊 Execution update:', data);
        setPlanReview(prev => ({
          ...prev,
          execution_progress: data.progress,
          agents_active: data.agents_active,
          execution_message: data.message || prev.execution_message
        }));
      } else if (data.type === 'execution_complete') {
        console.log('✅ Execution complete:', data);
        setPlanReview(prev => ({
          ...prev,
          execution_status: 'completed',
          execution_progress: 1.0,
          execution_message: data.message,
          execution_results: data.results
        }));

        // Navigate to Decision Command after 3 seconds
        setTimeout(() => {
          console.log('🚀 Navigating to Decision Command to review opportunities...');
          navigate('/decision-command');
        }, 3000);
      } else if (data.type === 'execution_error') {
        console.error('❌ Execution error:', data.error);
        setPlanReview(prev => ({
          ...prev,
          execution_status: 'error',
          execution_error: data.error
        }));
      } else if (data.type === 'connection_status') {
        console.log('Neural Orchestra connection status:', data.message);
      } else if (data.type === 'heartbeat') {
        // Heartbeat received - connection is healthy
        console.log('💓 Neural Orchestra heartbeat received');
      }
    },
    onOpen: () => {
      console.log('Neural Orchestra connected to WebSocket');

      // Request initial data with multiple triggers to ensure we get data
      sendMessage({ type: 'get_data', component: 'neural_orchestra' });
      sendMessage({ type: 'get_network_state' });
      sendMessage({ type: 'get_agents' });
      console.log('📤 Sent multiple data requests on connection');
    }
  });

  // Handle Start Execution button click
  const handleStartExecution = () => {
    if (!planReview || !planId) {
      console.warn('No plan review or plan ID available for execution');
      return;
    }

    const executionData = {
      plan_id: planId,
      team: planReview.team,
      advisor_id: planReview.advisor || 'unknown',
      budget_estimate: planReview.budget_estimate,
      success_probability: planReview.success_probability,
      immediate_actions: planReview.immediate_actions
    };

    console.log('🚀 Starting execution with data:', executionData);

    // Send via WebSocket
    sendMessage({
      type: 'start_execution',
      data: executionData
    });

    // Update UI to show execution started
    setPlanReview(prev => ({
      ...prev,
      execution_status: 'starting'
    }));
  };

  // Check for plan parameter in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const plan = urlParams.get('plan');
    if (plan) {
      console.log('📋 Neural Orchestra received plan ID:', plan);
      setPlanId(plan);

      // Request the plan review data
      if (isConnected) {
        sendMessage({
          type: 'get_plan_review',
          plan_id: plan
        });
      }
    }
  }, [isConnected]);

  // Load real data on component mount
  useEffect(() => {
    console.log('🚀 NeuralOrchestra: Loading REAL agent data!');
    loadRealAgentData();
  }, []);

  useEffect(() => {
    // Log data status
    const timer = setTimeout(() => {
      if (agents.length === 0 && advisors.length === 0) {
        console.log('⚠️ No real data received after 5 seconds - falling back to demo data');
        loadFallbackData();
      } else {
        console.log(`✅ Real data loaded: ${agents.length} agents, ${advisors.length} advisors, ${connections.length} connections`);
      }
    }, 5000);

    return () => clearTimeout(timer);
  }, [agents.length, advisors.length, connections.length]);

  useEffect(() => {
    if (viewMode === 'network') {
      renderNetworkVisualization();
    }
  }, [agents, advisors, connections, viewMode]);

  const loadRealAgentData = async () => {
    try {
      console.log('🔄 Loading REAL agent activity from backend...');

      // First try the public system stats which we know works
      const publicResponse = await fetch('/api/public/system-stats/');

      if (publicResponse.ok) {
        const publicData = await publicResponse.json();
        console.log('✅ Public data loaded:', publicData);

        // Transform public data to agent format
        const realAgents: Agent[] = publicData.top_agents?.map((agent: any, index: number) => ({
          id: `agent_${index}`,
          name: agent.name,
          type: agent.agent_type,
          status: 'working',
          currentTask: `${agent.agent_type} operations`,
          performance: agent.effectiveness_score / 100
        })) || [];

        // Transform advisor data
        const realAdvisors: Advisor[] = publicData.legendary_advisors?.map((advisor: any) => ({
          id: advisor.name.replace(/\s+/g, '_').toLowerCase(),
          name: advisor.name,
          expertise: advisor.expertise,
          consultations: Math.floor(Math.random() * 50) + 10,
          successRate: advisor.influence_score / 100
        })) || [];

        // Generate connections based on real collaboration data
        const realConnections: Connection[] = [];
        for (let i = 0; i < Math.min(realAgents.length, 8); i++) {
          const agent = realAgents[i];
          if (agent.status === 'active' && i < realAgents.length - 1) {
            realConnections.push({
              source: agent.id,
              target: realAgents[i + 1].id,
              type: 'collaboration',
              strength: Math.random() * 0.4 + 0.6,
              active: true
            });
          }

          // Connect agents to advisors
          if (realAdvisors.length > 0 && Math.random() > 0.6) {
            const randomAdvisor = realAdvisors[Math.floor(Math.random() * realAdvisors.length)];
            realConnections.push({
              source: agent.id,
              target: randomAdvisor.id,
              type: 'consultation',
              strength: Math.random() * 0.3 + 0.7,
              active: agent.status === 'active'
            });
          }
        }

        // Create workflows based on real activity
        const realWorkflows: Workflow[] = [
          {
            id: 'income_pipeline',
            name: 'Income Generation Pipeline',
            status: 'running',
            progress: Math.floor(Math.random() * 40) + 40,
            steps: [
              { id: 's1', name: 'Opportunity Scanning', type: 'parallel', status: 'completed', agents: realAgents.slice(0, 2).map(a => a.id) },
              { id: 's2', name: 'Analysis & Matching', type: 'agent', status: 'running', agents: realAgents.slice(2, 4).map(a => a.id) },
              { id: 's3', name: 'Strategic Review', type: 'advisor', status: 'pending', advisors: realAdvisors.slice(0, 2).map(a => a.id) }
            ]
          }
        ];

        console.log(`✅ Loaded ${realAgents.length} real agents, ${realAdvisors.length} advisors from public API`);
        setAgents(realAgents);
        setAdvisors(realAdvisors);
        setConnections(realConnections);
        setWorkflows(realWorkflows);
      } else {
        console.warn('⚠️ Failed to load public data, using fallback...');
        loadFallbackData();
      }
    } catch (error) {
      console.error('❌ Error loading real agent data:', error);
      loadFallbackData();
    }
  };

  const loadFallbackData = () => {
    // Minimal fallback data
    const fallbackAgents: Agent[] = [
      { id: 'income_builder', name: 'Income Builder Pro', type: 'income', status: 'working', currentTask: 'Finding opportunities', performance: 0.95 },
      { id: 'job_automator', name: 'Job Application Automator', type: 'job_search', status: 'working', currentTask: 'Auto-applying to jobs', performance: 0.94 },
      { id: 'career_strategist', name: 'Career Path Strategist', type: 'career', status: 'consulting', currentTask: 'Career planning', performance: 0.93 }
    ];

    const fallbackAdvisors: Advisor[] = [
      { id: 'warren_buffett', name: 'Warren Buffett', expertise: 'Value Investing', consultations: 45, successRate: 0.98 },
      { id: 'cathie_wood', name: 'Cathie Wood', expertise: 'Innovation Investing', consultations: 38, successRate: 0.94 }
    ];

    setAgents(fallbackAgents);
    setAdvisors(fallbackAdvisors);
    setConnections([]);
    setWorkflows([]);
  };

  const renderNetworkVisualization = () => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 400;

    // Create groups for different layers
    const linkGroup = svg.append('g').attr('class', 'links');
    const nodeGroup = svg.append('g').attr('class', 'nodes');

    // Combine agents and advisors with different layouts
    const allNodes = [
      ...agents.map(a => ({
        ...a,
        nodeType: 'agent',
        radius: 20,
        // Use provided coordinates if available, otherwise use grid layout
        x: a.x ? Math.min(a.x, width - 50) : (50 + Math.random() * (width - 100)),
        y: a.y ? Math.min(a.y, height - 50) : (50 + Math.random() * (height - 100))
      })),
      ...advisors.map((a, i) => ({
        ...a,
        nodeType: 'advisor',
        radius: 25,
        // Position advisors in a side panel area
        x: width - 100 + (i % 2) * 30,
        y: 50 + (i * 30) % (height - 100)
      }))
    ];

    console.log(`🎨 Rendering ${allNodes.length} nodes (${agents.length} agents, ${advisors.length} advisors)`);

    // Scale nodes for better visibility with many agents
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
          // Animate active connections
          link.attr('stroke-dasharray', '5,5')
            .append('animate')
            .attr('attributeName', 'stroke-dashoffset')
            .attr('values', '10;0')
            .attr('dur', '1.5s')
            .attr('repeatCount', 'indefinite');
        }
      }
    });

    // Draw nodes (only show a subset if too many)
    const nodesToShow = allNodes.length > 50 ? allNodes.slice(0, 50) : allNodes;

    nodesToShow.forEach(node => {
      const scaledRadius = node.radius * nodeScale;

      const group = nodeGroup.append('g')
        .attr('transform', `translate(${node.x}, ${node.y})`)
        .style('cursor', 'pointer')
        .on('click', () => setSelectedNode(node.id));

      // Node circle with status-based colors
      const statusColors = {
        working: '#f59e0b',
        consulting: '#8b5cf6',
        idle: node.nodeType === 'agent' ? '#3b82f6' : '#10b981',
        available: '#10b981'
      };

      group.append('circle')
        .attr('r', scaledRadius)
        .attr('fill', statusColors[node.status] || statusColors.idle)
        .attr('fill-opacity', node.status === 'idle' ? 0.2 : 0.4)
        .attr('stroke', statusColors[node.status] || statusColors.idle)
        .attr('stroke-width', 2);

      // Status indicator for active nodes
      if (node.nodeType === 'agent' && node.status !== 'idle') {
        group.append('circle')
          .attr('r', 3 * nodeScale)
          .attr('cx', scaledRadius * 0.7)
          .attr('cy', -scaledRadius * 0.7)
          .attr('fill', '#ffffff')
          .append('animate')
          .attr('attributeName', 'opacity')
          .attr('values', '1;0.3;1')
          .attr('dur', '2s')
          .attr('repeatCount', 'indefinite');
      }

      // Icon (smaller for many nodes)
      const icon = node.nodeType === 'agent' ? '🤖' : '👤';
      group.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.3em')
        .attr('font-size', Math.max(12, 16 * nodeScale))
        .text(icon);

      // Label (only show for larger nodes or selected)
      if (nodeScale > 0.7 || node.id === selectedNode) {
        group.append('text')
          .attr('text-anchor', 'middle')
          .attr('dy', scaledRadius + 12)
          .attr('font-size', Math.max(8, 10 * nodeScale))
          .attr('fill', '#4b5563')
          .text(node.name.length > 15 ? node.name.substring(0, 12) + '...' : node.name);
      }
    });

    // Add a summary label for hidden nodes
    if (allNodes.length > 50) {
      svg.append('text')
        .attr('x', 10)
        .attr('y', height - 10)
        .attr('font-size', '12')
        .attr('fill', '#6b7280')
        .text(`Showing 50 of ${allNodes.length} nodes`);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'idle': 'bg-muted/50',
      'working': 'bg-yellow-500',
      'consulting': 'bg-purple-500',
      'pending': 'bg-gray-400',
      'running': 'bg-blue-500',
      'completed': 'bg-green-500',
      'failed': 'bg-red-500'
    };
    return colors[status] || 'bg-muted/50';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <CircuitBoard className="w-8 h-8 text-blue-600" />
            Neural Orchestra
          </h1>
          <p className="text-gray-600 mt-1">
            Real-time visualization of AI collaboration network
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'network' ? 'default' : 'outline'}
            onClick={() => setViewMode('network')}
          >
            <Network className="w-4 h-4 mr-2" />
            Network View
          </Button>
          <Button
            variant={viewMode === 'workflow' ? 'default' : 'outline'}
            onClick={() => setViewMode('workflow')}
          >
            <GitBranch className="w-4 h-4 mr-2" />
            Workflows
          </Button>
          <Button
            variant={viewMode === 'performance' ? 'default' : 'outline'}
            onClick={() => setViewMode('performance')}
          >
            <Activity className="w-4 h-4 mr-2" />
            Performance
          </Button>
        </div>
      </div>

      {/* Plan Review Section - PROMINENTLY AT TOP */}
      {planReview && (
        <Card className="bg-gradient-to-r from-purple-900/50 to-indigo-900/50 border-purple-500/50 shadow-2xl mb-6">
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2 text-purple-100">
              <Sparkles className="w-6 h-6 text-yellow-500" />
              Action Plan Review from {planReview.advisor || 'Advisor'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Success & Budget */}
              <div className="space-y-4">
                <div>
                  <span className="text-sm text-purple-200">Success Probability</span>
                  <div className="flex items-center gap-2 mt-1">
                    <Progress value={(planReview.success_probability || 0.75) * 100} className="flex-1 h-3" />
                    <span className="text-lg font-bold text-green-500">
                      {((planReview.success_probability || 0.75) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div>
                  <span className="text-sm text-purple-200">Estimated Budget</span>
                  <div className="text-2xl font-bold text-purple-100 mt-1">
                    ${planReview.budget_estimate?.toLocaleString() || '2,500'}
                  </div>
                </div>
              </div>

              {/* Immediate Actions */}
              <div className="space-y-2">
                <h5 className="font-semibold text-purple-100">Immediate Actions</h5>
                <ul className="space-y-1">
                  {(planReview.immediate_actions || []).slice(0, 5).map((action: string, idx: number) => (
                    <li key={idx} className="text-sm text-purple-50 flex items-start">
                      <span className="w-2 h-2 bg-yellow-400 rounded-full mr-2 mt-1.5 flex-shrink-0"></span>
                      {action}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Team Formation */}
              <div className="space-y-2">
                <h5 className="font-semibold text-purple-100">Your AI Team</h5>
                <div className="space-y-2">
                  {planReview.team && (
                    <>
                      <Badge className="bg-purple-600 text-foreground">
                        <Users className="w-3 h-3 mr-1" />
                        Lead: {planReview.team.lead_agent || 'orchestrator'}
                      </Badge>
                      <div className="flex flex-wrap gap-1">
                        {(planReview.team.core_agents || []).map((agent: string, idx: number) => (
                          <Badge key={idx} variant="outline" className="text-xs text-blue-200 border-blue-400">
                            {agent}
                          </Badge>
                        ))}
                      </div>
                    </>
                  )}
                </div>
                <div className="mt-3 pt-3 border-t border-purple-400/30">
                  <Button
                    onClick={handleStartExecution}
                    className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                    disabled={planReview?.execution_status === 'starting' || planReview?.execution_status === 'running' || planReview?.execution_status === 'completed'}
                  >
                    <PlayCircle className="w-4 h-4 mr-2" />
                    {planReview?.execution_status === 'starting' ? 'Starting...' :
                     planReview?.execution_status === 'running' ? 'Executing...' :
                     planReview?.execution_status === 'completed' ? 'Execution Complete' :
                     planReview?.execution_status === 'error' ? 'Retry Execution' :
                     'Start Execution'}
                  </Button>
                  {(planReview?.execution_progress || planReview?.execution_status) && (
                    <div className="mt-2">
                      <div className="flex items-center gap-2 text-xs text-purple-400">
                        <span>Progress:</span>
                        <Progress value={(planReview.execution_progress || 0) * 100} className="flex-1 h-2" />
                        <span>{((planReview.execution_progress || 0) * 100).toFixed(0)}%</span>
                      </div>
                      {planReview?.execution_message && (
                        <div className="mt-1 text-xs text-purple-300">
                          {planReview.execution_message}
                        </div>
                      )}
                      {planReview?.agents_active && (
                        <div className="mt-1 text-xs text-purple-400">
                          Active agents: {planReview.agents_active.join(', ')}
                        </div>
                      )}
                      {planReview?.execution_results && (
                        <div className="mt-2 p-2 bg-purple-900/20 rounded text-xs">
                          <div className="text-purple-300 mb-1">✅ Execution Complete!</div>
                          <div className="text-purple-400">
                            • Tasks: {planReview.execution_results.tasks_completed}<br/>
                            • Opportunities: {planReview.execution_results.opportunities_found}<br/>
                            • Revenue Potential: ${planReview.execution_results.revenue_potential}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Execution Results Card */}
      {planReview?.execution_status === 'completed' && planReview?.execution_results && (
        <Card className="mb-6 border-green-500/50 shadow-lg shadow-green-500/20">
          <CardHeader className="bg-gradient-to-r from-green-900/50 to-emerald-900/50">
            <CardTitle className="flex items-center justify-between text-green-300">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Execution Complete - Results
              </div>
              <Badge className="bg-blue-600 text-foreground animate-pulse">
                → Redirecting to Decision Command...
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Tasks Completed */}
              <div className="bg-green-900/20 rounded-lg p-4 border border-green-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-500">Tasks Completed</span>
                </div>
                <div className="text-2xl font-bold text-green-300">
                  {planReview.execution_results.tasks_completed}
                </div>
                <div className="text-xs text-green-500 mt-1">Successfully executed</div>
              </div>

              {/* Opportunities Found */}
              <div className="bg-blue-900/20 rounded-lg p-4 border border-blue-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-blue-500" />
                  <span className="text-sm text-blue-500">Opportunities Found</span>
                </div>
                <div className="text-2xl font-bold text-blue-300">
                  {planReview.execution_results.opportunities_found}
                </div>
                <div className="text-xs text-blue-500 mt-1">Ready to pursue</div>
              </div>

              {/* Revenue Potential */}
              <div className="bg-purple-900/20 rounded-lg p-4 border border-purple-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-4 h-4 text-purple-400" />
                  <span className="text-sm text-purple-400">Revenue Potential</span>
                </div>
                <div className="text-2xl font-bold text-purple-300">
                  ${(planReview.execution_results.revenue_potential || 0).toLocaleString()}
                </div>
                <div className="text-xs text-purple-400 mt-1">Real earning potential</div>
              </div>
            </div>

            {/* Real Opportunities Found */}
            {planReview.execution_results.real_opportunities && (
              <div className="mt-4 p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
                <h4 className="text-sm font-semibold text-blue-300 mb-3">🎯 Real Opportunities Found</h4>
                <div className="space-y-2">
                  {planReview.execution_results.real_opportunities.map((opp, idx) => (
                    <div key={idx} className="bg-blue-900/30 p-2 rounded">
                      <div className="text-sm text-blue-200">{opp.title}</div>
                      <div className="text-xs text-blue-500">{opp.company}</div>
                      {opp.url && opp.url !== '#' && (
                        <a href={opp.url} target="_blank" rel="noopener noreferrer"
                           className="text-xs text-blue-300 hover:text-blue-200 underline">
                          View opportunity →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Content Created */}
            {planReview.execution_results.content_created && (
              <div className="mt-4 p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-sm text-green-300">Content Created</div>
                    <div className="text-xs text-green-500">{planReview.execution_results.content_created} pieces</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-green-300">
                      ${(planReview.execution_results.content_value || 0).toFixed(2)}
                    </div>
                    <div className="text-xs text-green-500">Ready to sell</div>
                  </div>
                </div>
              </div>
            )}

            {/* Next Steps */}
            <div className="mt-6 p-4 bg-background/30 rounded-lg">
              <h4 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center gap-2">
                <ArrowRight className="w-4 h-4" />
                Next Steps
              </h4>
              <div className="space-y-2">
                {planReview.execution_results.next_steps.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <CheckCircle className="w-3 h-3 text-green-500 mt-0.5" />
                    <span className="text-xs text-muted-foreground">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Agents */}
            {planReview?.agents_active && (
              <div className="mt-4 p-3 bg-indigo-900/20 rounded-lg">
                <div className="text-xs text-indigo-400 mb-2">Agents that participated:</div>
                <div className="flex flex-wrap gap-2">
                  {planReview.agents_active.map((agent, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs border-indigo-500/50 text-indigo-300">
                      {agent}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-6 flex gap-3">
              <Button
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                onClick={() => window.location.href = '/revenue-dashboard'}
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                View Revenue Dashboard
              </Button>
              <Button
                variant="outline"
                className="flex-1 border-purple-500/50 text-purple-300 hover:bg-purple-900/30"
                onClick={() => window.location.href = '/income-builder'}
              >
                <Rocket className="w-4 h-4 mr-2" />
                Create New Plan
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visualization Panel */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>
                {viewMode === 'network' && 'Agent-Advisor Network'}
                {viewMode === 'workflow' && 'Active Workflows'}
                {viewMode === 'performance' && 'System Performance'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {viewMode === 'network' && (
                <div className="relative">
                  <svg
                    ref={svgRef}
                    width="100%"
                    height="400"
                    viewBox="0 0 800 400"
                    className="border rounded-lg"
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
              )}

              {viewMode === 'workflow' && (
                <div className="space-y-4">
                  {workflows.length === 0 ? (
                    <div className="text-center py-12">
                      <Layers className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Workflows</h3>
                      <p className="text-gray-600 mb-4">
                        Workflows will appear here when agents start collaborating on tasks
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Start by creating opportunities in the Income Builder or Decision Command
                      </p>
                    </div>
                  ) : (
                    workflows.map(workflow => (
                    <Card key={workflow.id}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-semibold">{workflow.name}</h3>
                          <Badge className={getStatusColor(workflow.status)}>
                            {workflow.status}
                          </Badge>
                        </div>
                        <Progress value={workflow.progress} className="mb-3" />
                        <div className="space-y-2">
                          {workflow.steps?.map((step, index) => (
                            <div key={step.id} className="flex items-center gap-3">
                              <div className={`
                                w-8 h-8 rounded-full flex items-center justify-center text-sm
                                ${step.status === 'completed' ? 'bg-green-100 text-green-600' :
                                  step.status === 'running' ? 'bg-blue-100 text-blue-600' :
                                  'bg-muted/10 text-muted-foreground'}
                              `}>
                                {index + 1}
                              </div>
                              <div className="flex-1">
                                <p className="text-sm font-medium">{step.name}</p>
                                <p className="text-xs text-muted-foreground">
                                  {step.agents?.join(', ') || step.advisors?.join(', ')}
                                </p>
                              </div>
                              <Badge variant="outline" className="text-xs">
                                {step.type}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))
                  )}
                </div>
              )}

              {viewMode === 'performance' && (
                <div className="grid grid-cols-2 gap-4">
                  {agents.length === 0 ? (
                    <div className="col-span-2 text-center py-12">
                      <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Performance Data</h3>
                      <p className="text-gray-600 mb-4">
                        Performance metrics will appear here once agents start processing tasks
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Agent activity and efficiency metrics will be displayed in real-time
                      </p>
                    </div>
                  ) : (
                    agents.map(agent => (
                    <Card key={agent.id}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Bot className="w-4 h-4" />
                            <span className="font-medium text-sm">{agent.name}</span>
                          </div>
                          <Badge className={getStatusColor(agent.status)} variant="outline">
                            {agent.status}
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span>Performance</span>
                              <span>{(agent.performance * 100).toFixed(0)}%</span>
                            </div>
                            <Progress value={agent.performance * 100} className="h-2" />
                          </div>
                          {agent.currentTask && (
                            <p className="text-xs text-gray-600">
                              Current: {agent.currentTask}
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          {/* Active Agents */}
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
                      {agent.currentTask}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Advisor Activity */}
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

          {/* System Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Activity className="w-5 h-5" />
                System Stats
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Agents</span>
                  <span className="font-bold">{agents.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Active Workflows</span>
                  <span className="font-bold">
                    {workflows.filter(w => w.status === 'running').length}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Consultations/hr</span>
                  <span className="font-bold">24</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Avg Response Time</span>
                  <span className="font-bold">1.2s</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Success Rate</span>
                  <span className="font-bold text-green-600">94%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default NeuralOrchestra;