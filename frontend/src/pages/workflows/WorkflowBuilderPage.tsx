import { useCallback, useState, useEffect } from 'react';
import { Logger } from '../../utils/logger';
import ReactFlow, {
  type Node,
  type Edge,
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Connection,
  MarkerType,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { WorkflowNodeLibrary } from '../../components/features/workflow-builder/WorkflowNodeLibrary';
import { WorkflowPropertiesPanel } from '../../components/features/workflow-builder/WorkflowPropertiesPanel';
import { WorkflowExecutionPanel } from '../../components/features/workflow-builder/WorkflowExecutionPanel';
import { WorkflowCustomNode } from '../../components/features/workflow-builder/WorkflowCustomNode';
import { Button } from '../../components/common/Button';
import { useWorkflowStore } from '../../store/workflowStore';
import { 
  PlayIcon, 
  DocumentArrowDownIcon, 
  ArrowLeftIcon,
  DocumentDuplicateIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const nodeTypes = {
  custom: WorkflowCustomNode,
};

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'custom',
    position: { x: 250, y: 100 },
    data: { 
      label: 'Research Input',
      type: 'research-input',
      category: 'input',
      config: {},
    },
  },
  {
    id: '2',
    type: 'custom',
    position: { x: 250, y: 250 },
    data: { 
      label: 'Content Generation',
      type: 'content-generation',
      category: 'process',
      config: {},
    },
  },
  {
    id: '3',
    type: 'custom',
    position: { x: 250, y: 400 },
    data: { 
      label: 'Blog Publishing',
      type: 'blog-publishing',
      category: 'output',
      config: {},
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
    animated: true,
    style: { stroke: '#8b5cf6' },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: '#8b5cf6',
    },
  },
  {
    id: 'e2-3',
    source: '2',
    target: '3',
    animated: true,
    style: { stroke: '#8b5cf6' },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: '#8b5cf6',
    },
  },
];

export function WorkflowBuilderPage() {
  const navigate = useNavigate();
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const { currentWorkflow, isDirty } = useWorkflowStore();

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge({
        ...params,
        animated: true,
        style: { stroke: '#8b5cf6' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#8b5cf6',
        },
      }, eds));
    },
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const onNodeDrop = useCallback(
    (event: React.DragEvent, nodeType: any) => {
      event.preventDefault();

      const reactFlowBounds = event.currentTarget.getBoundingClientRect();
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };

      const newNode: Node = {
        id: `node-${Date.now()}`,
        type: 'custom',
        position,
        data: {
          label: nodeType.name,
          type: nodeType.type,
          category: nodeType.category,
          config: {},
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  const handleSave = () => {
    // TODO: Implement save workflow
    Logger.workflow('Save Workflow', '', { nodes: nodes.length, edges: edges.length });
    Logger.state('WorkflowStore', 'Saving workflow', { nodes, edges });
    toast.success('Workflow saved successfully');
  };

  const handleExecute = () => {
    Logger.workflow('Execute Workflow', '', { nodes: nodes.length, edges: edges.length });
    Logger.group('Workflow Execution');
    Logger.workflow('Starting execution', '', { nodes, edges });
    
    setIsExecuting(true);
    // TODO: Implement workflow execution
    setTimeout(() => {
      Logger.workflow('Execution Complete', '', { duration: '3000ms' });
      Logger.groupEnd();
      setIsExecuting(false);
      toast.success('Workflow executed successfully');
    }, 3000);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] -mx-6 -my-8">
      {/* Node Library */}
      <WorkflowNodeLibrary />

      {/* Canvas */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-background"
        >
          <Background color="#374151" gap={16} />
          <Controls className="!bg-background !border-border" />
          <MiniMap 
            className="!bg-background !border-border"
            nodeColor="#8b5cf6"
            maskColor="rgba(0, 0, 0, 0.8)"
          />
          
          {/* Top toolbar */}
          <Panel position="top-left" className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => navigate('/workflows')}>
              <ArrowLeftIcon className="h-4 w-4" />
              Back
            </Button>
            <div className="h-6 w-px bg-dark-700" />
            <span className="text-foreground font-medium">
              {currentWorkflow?.name || 'New Workflow'}
            </span>
            {isDirty && (
              <span className="px-2 py-0.5 text-xs bg-yellow-500/20 text-yellow-500 rounded-full">
                Unsaved changes
              </span>
            )}
          </Panel>

          {/* Bottom toolbar */}
          <Panel position="bottom-center" className="flex items-center gap-2">
            <Button variant="secondary" size="sm">
              <DocumentDuplicateIcon className="h-4 w-4" />
              Duplicate
            </Button>
            <Button variant="secondary" size="sm">
              <TrashIcon className="h-4 w-4" />
              Clear
            </Button>
            <div className="h-6 w-px bg-dark-700" />
            <Button 
              variant="secondary" 
              size="sm"
              onClick={handleSave}
              disabled={!isDirty}
            >
              <DocumentArrowDownIcon className="h-4 w-4" />
              Save
            </Button>
            <Button 
              size="sm"
              onClick={handleExecute}
              loading={isExecuting}
            >
              <PlayIcon className="h-4 w-4" />
              Execute
            </Button>
          </Panel>
        </ReactFlow>
      </div>

      {/* Properties Panel */}
      <WorkflowPropertiesPanel node={selectedNode} />

      {/* Execution Panel */}
      {isExecuting && <WorkflowExecutionPanel />}
    </div>
  );
}