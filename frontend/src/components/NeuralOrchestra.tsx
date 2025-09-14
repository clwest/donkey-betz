/**
 * Neural Orchestra - Enhanced Collaboration Visualizer
 *
 * Real-time visualization of agent-advisor collaboration, ML pipeline activity,
 * and workflow orchestration with beautiful interactive graphics.
 */

import React, { useState, useEffect, useRef } from 'react';
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
  Cloud
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
  status: 'idle' | 'working' | 'consulting';
  currentTask?: string;
  performance: number;
}

interface Advisor {
  id: string;
  name: string;
  expertise: string;
  consultations: number;
  successRate: number;
}

interface Workflow {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  steps: WorkflowStep[];
}

interface WorkflowStep {
  id: string;
  name: string;
  type: string;
  status: 'pending' | 'running' | 'completed';
  agents?: string[];
  advisors?: string[];
}

interface Connection {
  source: string;
  target: string;
  type: 'consultation' | 'collaboration' | 'data_flow';
  strength: number;
  active: boolean;
}

const NeuralOrchestra: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [advisors, setAdvisors] = useState<Advisor[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'network' | 'workflow' | 'performance'>('network');

  const { sendMessage, lastMessage } = useWebSocket({
    url: '/ws/orchestra/',
    onMessage: (data) => {
      console.log('Neural Orchestra received:', data);
      if (data.type === 'orchestra_update') {
        // Handle orchestra updates
        console.log('Active workflows:', data.active_workflows);
      } else if (data.type === 'network_state') {
        // Update network visualization data
        if (data.data) {
          setAgents(data.data.agents || []);
          setAdvisors(data.data.advisors || []);
          setConnections(data.data.connections || []);
        }
      }
    }
  });

  useEffect(() => {
    // Initialize with mock data for demonstration
    initializeMockData();
  }, []);

  useEffect(() => {
    if (viewMode === 'network') {
      renderNetworkVisualization();
    }
  }, [agents, advisors, connections, viewMode]);

  const initializeMockData = () => {
    // Mock agents
    const mockAgents: Agent[] = [
      { id: 'agent1', name: 'Content Writer', type: 'content', status: 'working', currentTask: 'Writing article', performance: 0.85 },
      { id: 'agent2', name: 'Market Analyst', type: 'analysis', status: 'consulting', currentTask: 'Analyzing trends', performance: 0.92 },
      { id: 'agent3', name: 'Code Generator', type: 'development', status: 'idle', performance: 0.78 },
      { id: 'agent4', name: 'Data Processor', type: 'data', status: 'working', currentTask: 'Processing dataset', performance: 0.88 },
      { id: 'agent5', name: 'Risk Manager', type: 'finance', status: 'consulting', currentTask: 'Risk assessment', performance: 0.95 }
    ];

    // Mock advisors
    const mockAdvisors: Advisor[] = [
      { id: 'advisor1', name: 'Warren Buffett', expertise: 'Value Investing', consultations: 45, successRate: 0.89 },
      { id: 'advisor2', name: 'Cathie Wood', expertise: 'Innovation', consultations: 38, successRate: 0.82 },
      { id: 'advisor3', name: 'Ray Dalio', expertise: 'Macro Economics', consultations: 52, successRate: 0.91 }
    ];

    // Mock connections
    const mockConnections: Connection[] = [
      { source: 'agent1', target: 'agent2', type: 'collaboration', strength: 0.8, active: true },
      { source: 'agent2', target: 'advisor1', type: 'consultation', strength: 0.9, active: true },
      { source: 'agent4', target: 'agent5', type: 'data_flow', strength: 0.7, active: false },
      { source: 'agent5', target: 'advisor3', type: 'consultation', strength: 0.85, active: true }
    ];

    // Mock workflows
    const mockWorkflows: Workflow[] = [
      {
        id: 'wf1',
        name: 'Content Generation Pipeline',
        status: 'running',
        progress: 65,
        steps: [
          { id: 's1', name: 'Research', type: 'parallel', status: 'completed', agents: ['agent2'] },
          { id: 's2', name: 'Writing', type: 'agent', status: 'running', agents: ['agent1'] },
          { id: 's3', name: 'Review', type: 'advisor', status: 'pending', advisors: ['advisor1'] }
        ]
      }
    ];

    setAgents(mockAgents);
    setAdvisors(mockAdvisors);
    setConnections(mockConnections);
    setWorkflows(mockWorkflows);
  };

  const renderNetworkVisualization = () => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 400;
    const centerX = width / 2;
    const centerY = height / 2;

    // Create groups for different layers
    const linkGroup = svg.append('g').attr('class', 'links');
    const nodeGroup = svg.append('g').attr('class', 'nodes');

    // Position nodes in a circular layout
    const allNodes = [
      ...agents.map(a => ({ ...a, nodeType: 'agent', radius: 30 })),
      ...advisors.map(a => ({ ...a, nodeType: 'advisor', radius: 35 }))
    ];

    const angleStep = (2 * Math.PI) / allNodes.length;
    allNodes.forEach((node, i) => {
      const angle = i * angleStep;
      node.x = centerX + Math.cos(angle) * 150;
      node.y = centerY + Math.sin(angle) * 150;
    });

    // Draw connections
    connections.forEach(conn => {
      const source = allNodes.find(n => n.id === conn.source);
      const target = allNodes.find(n => n.id === conn.target);

      if (source && target) {
        const link = linkGroup.append('line')
          .attr('x1', source.x)
          .attr('y1', source.y)
          .attr('x2', target.x)
          .attr('y2', target.y)
          .attr('stroke', conn.active ? '#8b5cf6' : '#d1d5db')
          .attr('stroke-width', conn.strength * 3)
          .attr('stroke-opacity', conn.active ? 0.6 : 0.3);

        if (conn.active) {
          // Animate active connections
          link.attr('stroke-dasharray', '5,5')
            .append('animate')
            .attr('attributeName', 'stroke-dashoffset')
            .attr('values', '10;0')
            .attr('dur', '1s')
            .attr('repeatCount', 'indefinite');
        }
      }
    });

    // Draw nodes
    allNodes.forEach(node => {
      const group = nodeGroup.append('g')
        .attr('transform', `translate(${node.x}, ${node.y})`)
        .style('cursor', 'pointer')
        .on('click', () => setSelectedNode(node.id));

      // Node circle
      group.append('circle')
        .attr('r', node.radius)
        .attr('fill', node.nodeType === 'agent' ? '#3b82f6' : '#10b981')
        .attr('fill-opacity', 0.2)
        .attr('stroke', node.nodeType === 'agent' ? '#3b82f6' : '#10b981')
        .attr('stroke-width', 2);

      // Status indicator for agents
      if (node.nodeType === 'agent' && node.status !== 'idle') {
        group.append('circle')
          .attr('r', 5)
          .attr('cx', node.radius * 0.7)
          .attr('cy', -node.radius * 0.7)
          .attr('fill', node.status === 'working' ? '#f59e0b' : '#8b5cf6')
          .append('animate')
          .attr('attributeName', 'opacity')
          .attr('values', '1;0.3;1')
          .attr('dur', '2s')
          .attr('repeatCount', 'indefinite');
      }

      // Icon
      const icon = node.nodeType === 'agent' ? '🤖' : '👤';
      group.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.3em')
        .attr('font-size', '20')
        .text(icon);

      // Label
      group.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', node.radius + 15)
        .attr('font-size', '12')
        .attr('fill', '#4b5563')
        .text(node.name);
    });
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'idle': 'bg-gray-500',
      'working': 'bg-yellow-500',
      'consulting': 'bg-purple-500',
      'pending': 'bg-gray-400',
      'running': 'bg-blue-500',
      'completed': 'bg-green-500',
      'failed': 'bg-red-500'
    };
    return colors[status] || 'bg-gray-500';
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
                  {workflows.map(workflow => (
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
                          {workflow.steps.map((step, index) => (
                            <div key={step.id} className="flex items-center gap-3">
                              <div className={`
                                w-8 h-8 rounded-full flex items-center justify-center text-sm
                                ${step.status === 'completed' ? 'bg-green-100 text-green-600' :
                                  step.status === 'running' ? 'bg-blue-100 text-blue-600' :
                                  'bg-gray-100 text-gray-400'}
                              `}>
                                {index + 1}
                              </div>
                              <div className="flex-1">
                                <p className="text-sm font-medium">{step.name}</p>
                                <p className="text-xs text-gray-500">
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
                  ))}
                </div>
              )}

              {viewMode === 'performance' && (
                <div className="grid grid-cols-2 gap-4">
                  {agents.map(agent => (
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
                  ))}
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
                  <div key={agent.id} className="flex items-center justify-between p-2 rounded-lg bg-gray-50">
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
                      <span className="text-xs text-gray-500">
                        {advisor.consultations} consults
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress value={advisor.successRate * 100} className="flex-1 h-2" />
                      <span className="text-xs">{(advisor.successRate * 100).toFixed(0)}%</span>
                    </div>
                    <p className="text-xs text-gray-500">{advisor.expertise}</p>
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