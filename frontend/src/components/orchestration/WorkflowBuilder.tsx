import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  ReactFlowProvider,
  MarkerType,
} from 'reactflow';
import type {
  Node,
  Edge,
  Connection,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PlayIcon,
  PlusIcon,
  TrashIcon,
  Cog6ToothIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  UserGroupIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { useAgentOrchestraStore, useAgentOrchestraSelectors } from '../../store/agentOrchestraStore';
import type { Agent, AgentOrchestration } from '../../services/agent-orchestra.service';
import { toast } from 'sonner';

// Custom Node Component
const AgentNode = ({ data, selected }: { data: any; selected: boolean }) => {
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-500 bg-green-50';
      case 'processing':
        return 'border-yellow-500 bg-yellow-50';
      case 'failed':
        return 'border-red-500 bg-red-50';
      default:
        return 'border-blue-500 bg-blue-50';
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <ClockIcon className="h-4 w-4 text-yellow-500 animate-spin" />;
      case 'failed':
        return <XCircleIcon className="h-4 w-4 text-red-500" />;
      default:
        return <UserGroupIcon className="h-4 w-4 text-blue-500" />;
    }
  };

  return (
    <div
      className={`px-4 py-3 shadow-md rounded-lg border-2 min-w-48 ${getStatusColor(data.status)} ${
        selected ? 'ring-2 ring-blue-300' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {getStatusIcon(data.status)}
          <span className="font-semibold text-sm text-gray-900">
            {data.agent?.name || 'Agent'}
          </span>
        </div>
        {data.status && (
          <span className="text-xs px-2 py-1 rounded-full bg-white border">
            {data.status}
          </span>
        )}
      </div>
      
      <div className="text-xs text-gray-600 mb-2">
        {data.agent?.specialization || 'General'}
      </div>
      
      {data.task && (
        <div className="text-xs text-gray-700 bg-white p-2 rounded border">
          {data.task.length > 60 ? `${data.task.substring(0, 60)}...` : data.task}
        </div>
      )}
      
      {data.result && (
        <div className="mt-2 text-xs text-gray-600 bg-green-50 p-2 rounded border">
          <DocumentTextIcon className="h-3 w-3 inline mr-1" />
          Result available
        </div>
      )}
    </div>
  );
};

const nodeTypes: NodeTypes = {
  agentNode: AgentNode,
};

interface WorkflowBuilderProps {
  className?: string;
}

export const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({ className }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [showAgentPanel, setShowAgentPanel] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [autoRoute, setAutoRoute] = useState(true);

  const {
    agents,
    orchestrations,
    selectedOrchestration,
    agentsLoading,
    fetchAgents,
    orchestrateTask,
    selectOrchestration,
    connectWebSocket,
    wsConnected
  } = useAgentOrchestraStore();

  const {
    activeOrchestrations,
    completedOrchestrations
  } = useAgentOrchestraSelectors();

  useEffect(() => {
    if (agents.length === 0) {
      fetchAgents();
    }
    if (!wsConnected) {
      connectWebSocket();
    }
  }, []);

  // Load existing orchestration if selected
  useEffect(() => {
    if (selectedOrchestration) {
      loadOrchestrationToWorkflow(selectedOrchestration);
    }
  }, [selectedOrchestration]);

  const loadOrchestrationToWorkflow = (orchestration: AgentOrchestration) => {
    const workflowNodes: Node[] = [];
    const workflowEdges: Edge[] = [];

    orchestration.agent_sequence.forEach((agent, index) => {
      const nodeId = `agent-${index}`;
      workflowNodes.push({
        id: nodeId,
        type: 'agentNode',
        position: { x: 100 + (index * 300), y: 100 },
        data: {
          agent,
          task: orchestration.task_description,
          status: index < orchestration.current_step ? 'completed' : 
                 index === orchestration.current_step ? 'processing' : 'pending',
          result: index < orchestration.current_step ? orchestration.results[index] : null
        },
      });

      if (index > 0) {
        workflowEdges.push({
          id: `edge-${index - 1}-${index}`,
          source: `agent-${index - 1}`,
          target: nodeId,
          markerEnd: {
            type: MarkerType.ArrowClosed,
          },
        });
      }
    });

    setNodes(workflowNodes);
    setEdges(workflowEdges);
    setWorkflowDescription(orchestration.task_description);
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addAgent = (agent: Agent) => {
    const nodeId = `agent-${Date.now()}`;
    const newNode: Node = {
      id: nodeId,
      type: 'agentNode',
      position: {
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 100,
      },
      data: {
        agent,
        task: '',
        status: 'pending'
      },
    };

    setNodes((nds) => [...nds, newNode]);
    setShowAgentPanel(false);
    toast.success(`Added ${agent.name} to workflow`);
  };

  const removeNode = (nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
  };

  const updateNodeTask = (nodeId: string, task: string) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, task } }
          : node
      )
    );
  };

  const executeWorkflow = async () => {
    if (nodes.length === 0) {
      toast.error('Please add at least one agent to the workflow');
      return;
    }

    if (!workflowDescription.trim()) {
      toast.error('Please provide a workflow description');
      return;
    }

    setIsBuilding(true);
    try {
      const agentTypes = nodes.map(node => node.data.agent.specialization);
      const orchestration = await orchestrateTask(
        workflowDescription,
        autoRoute ? undefined : agentTypes,
        autoRoute
      );

      toast.success('Workflow orchestration started!');
      selectOrchestration(orchestration);
      
      // Update nodes to show they're processing
      setNodes((nds) =>
        nds.map((node, index) => ({
          ...node,
          data: {
            ...node.data,
            status: index === 0 ? 'processing' : 'pending'
          }
        }))
      );
    } catch (error) {
      console.error('Workflow execution failed:', error);
    } finally {
      setIsBuilding(false);
    }
  };

  const clearWorkflow = () => {
    setNodes([]);
    setEdges([]);
    setWorkflowDescription('');
    setSelectedNodeId(null);
    selectOrchestration(null);
    toast.success('Workflow cleared');
  };

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-border p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <UserGroupIcon className="h-8 w-8 mr-3 text-purple-600" />
            Multi-Agent Workflow Builder
          </h1>
          <div className="flex items-center space-x-2">
            {wsConnected ? (
              <div className="flex items-center text-green-600">
                <div className="h-2 w-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                <span className="text-sm">Live Updates</span>
              </div>
            ) : (
              <div className="flex items-center text-red-600">
                <div className="h-2 w-2 bg-red-500 rounded-full mr-2" />
                <span className="text-sm">Disconnected</span>
              </div>
            )}
          </div>
        </div>

        {/* Workflow Controls */}
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Describe your workflow objective..."
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRoute}
              onChange={(e) => setAutoRoute(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Auto Route</span>
          </label>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowAgentPanel(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-foreground rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Agent
          </button>

          <button
            onClick={executeWorkflow}
            disabled={isBuilding || nodes.length === 0}
            className="flex items-center px-4 py-2 bg-green-600 text-foreground rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isBuilding ? (
              <>
                <ClockIcon className="h-5 w-5 mr-2 animate-spin" />
                Orchestrating...
              </>
            ) : (
              <>
                <PlayIcon className="h-5 w-5 mr-2" />
                Execute Workflow
              </>
            )}
          </button>

          <button
            onClick={clearWorkflow}
            className="flex items-center px-4 py-2 bg-gray-600 text-foreground rounded-lg hover:bg-gray-700 transition-colors"
          >
            <TrashIcon className="h-5 w-5 mr-2" />
            Clear
          </button>
        </div>
      </div>

      {/* Workflow Canvas */}
      <div className="flex-1 relative">
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            className="bg-muted/5"
            onNodeClick={(event, node) => setSelectedNodeId(node.id)}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background />
          </ReactFlow>
        </ReactFlowProvider>

        {/* Agent Panel */}
        <AnimatePresence>
          {showAgentPanel && (
            <motion.div
              initial={{ opacity: 0, x: -300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -300 }}
              className="absolute left-4 top-4 bottom-4 w-80 bg-white rounded-lg shadow-lg border border-border z-10 overflow-hidden"
            >
              <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Available Agents
                  </h3>
                  <button
                    onClick={() => setShowAgentPanel(false)}
                    className="text-muted-foreground hover:text-gray-600"
                  >
                    <XCircleIcon className="h-6 w-6" />
                  </button>
                </div>
              </div>
              
              <div className="p-4 overflow-y-auto max-h-full">
                {agentsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <ClockIcon className="h-8 w-8 text-muted-foreground animate-spin" />
                  </div>
                ) : (
                  <div className="space-y-3">
                    {agents.map((agent) => (
                      <div
                        key={agent.id}
                        onClick={() => addAgent(agent)}
                        className="p-3 border border-border rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">
                            {agent.name}
                          </h4>
                          <span className="text-xs px-2 py-1 bg-muted/10 text-gray-600 rounded-full">
                            {agent.specialization}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {agent.description}
                        </p>
                        <div className="mt-2 flex flex-wrap gap-1">
                          {agent.capabilities.slice(0, 3).map((capability, idx) => (
                            <span
                              key={idx}
                              className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded"
                            >
                              {capability}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Node Configuration Panel */}
        <AnimatePresence>
          {selectedNodeId && (
            <motion.div
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              className="absolute right-4 top-4 bottom-4 w-80 bg-white rounded-lg shadow-lg border border-border z-10 overflow-hidden"
            >
              <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Agent Configuration
                  </h3>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => removeNode(selectedNodeId)}
                      className="text-red-500 hover:text-red-600"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => setSelectedNodeId(null)}
                      className="text-muted-foreground hover:text-gray-600"
                    >
                      <XCircleIcon className="h-6 w-6" />
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="p-4 overflow-y-auto">
                {(() => {
                  const node = nodes.find(n => n.id === selectedNodeId);
                  if (!node) return null;
                  
                  return (
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">
                          {node.data.agent.name}
                        </h4>
                        <p className="text-sm text-gray-600 mb-4">
                          {node.data.agent.description}
                        </p>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Specific Task (Optional)
                        </label>
                        <textarea
                          value={node.data.task || ''}
                          onChange={(e) => updateNodeTask(selectedNodeId, e.target.value)}
                          placeholder="Specific instructions for this agent..."
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 resize-none"
                          rows={3}
                        />
                      </div>
                      
                      <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">
                          Capabilities
                        </h5>
                        <div className="flex flex-wrap gap-1">
                          {node.data.agent.capabilities.map((capability: string, idx: number) => (
                            <span
                              key={idx}
                              className="text-xs px-2 py-1 bg-muted/10 text-gray-600 rounded"
                            >
                              {capability}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      {node.data.result && (
                        <div>
                          <h5 className="text-sm font-medium text-gray-700 mb-2">
                            Result
                          </h5>
                          <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
                            {typeof node.data.result === 'string' 
                              ? node.data.result 
                              : JSON.stringify(node.data.result, null, 2)
                            }
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Status Bar */}
      <div className="bg-muted/10 border-t border-border px-4 py-3">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Agents: {nodes.length}</span>
            <span>Connections: {edges.length}</span>
            {selectedOrchestration && (
              <span>
                Progress: {selectedOrchestration.current_step}/{selectedOrchestration.total_steps}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-4">
            <span>Active Orchestrations: {activeOrchestrations.length}</span>
            <span>Completed: {completedOrchestrations.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};