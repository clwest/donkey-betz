import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import type { Workflow, WorkflowNode, WorkflowConnection, WorkflowExecution } from '../types/workflow.types';
import { Logger } from '../utils/logger';

interface WorkflowState {
  // Current workflow being edited
  currentWorkflow: Workflow | null;
  isDirty: boolean;
  
  // Workflow list
  workflows: Workflow[];
  
  // Execution state
  currentExecution: WorkflowExecution | null;
  executionLogs: string[];
  
  // UI State
  selectedNode: string | null;
  selectedConnection: string | null;
  isExecuting: boolean;
  
  // Actions - Workflow Management
  setCurrentWorkflow: (workflow: Workflow) => void;
  updateWorkflow: (updates: Partial<Workflow>) => void;
  clearCurrentWorkflow: () => void;
  
  // Actions - Node Management
  addNode: (node: WorkflowNode) => void;
  updateNode: (nodeId: string, updates: Partial<WorkflowNode>) => void;
  deleteNode: (nodeId: string) => void;
  selectNode: (nodeId: string | null) => void;
  
  // Actions - Connection Management
  addConnection: (connection: WorkflowConnection) => void;
  deleteConnection: (connectionId: string) => void;
  selectConnection: (connectionId: string | null) => void;
  
  // Actions - Execution
  startExecution: () => void;
  updateExecution: (execution: WorkflowExecution) => void;
  addExecutionLog: (log: string) => void;
  clearExecution: () => void;
  
  // Actions - Workflow List
  setWorkflows: (workflows: Workflow[]) => void;
  markDirty: (isDirty: boolean) => void;
}

export const useWorkflowStore = create<WorkflowState>()(
  immer((set) => ({
    currentWorkflow: null,
    isDirty: false,
    workflows: [],
    currentExecution: null,
    executionLogs: [],
    selectedNode: null,
    selectedConnection: null,
    isExecuting: false,
    
    setCurrentWorkflow: (workflow) => set((state) => {
      Logger.state('WorkflowStore', 'Set current workflow', { workflowId: workflow.id, name: workflow.name });
      state.currentWorkflow = workflow;
      state.isDirty = false;
    }),
    
    updateWorkflow: (updates) => set((state) => {
      if (state.currentWorkflow) {
        Logger.state('WorkflowStore', 'Update workflow', { workflowId: state.currentWorkflow.id, updates });
        Object.assign(state.currentWorkflow, updates);
        state.isDirty = true;
      }
    }),
    
    clearCurrentWorkflow: () => set((state) => {
      state.currentWorkflow = null;
      state.isDirty = false;
      state.selectedNode = null;
      state.selectedConnection = null;
    }),
    
    addNode: (node) => set((state) => {
      if (state.currentWorkflow) {
        Logger.workflow('Add node', node.id, { type: node.type, position: node.position });
        state.currentWorkflow.nodes.push(node);
        state.isDirty = true;
      }
    }),
    
    updateNode: (nodeId, updates) => set((state) => {
      if (state.currentWorkflow) {
        const node = state.currentWorkflow.nodes.find(n => n.id === nodeId);
        if (node) {
          Logger.workflow('Update node', nodeId, updates);
          Object.assign(node, updates);
          state.isDirty = true;
        }
      }
    }),
    
    deleteNode: (nodeId) => set((state) => {
      if (state.currentWorkflow) {
        Logger.workflow('Delete node', nodeId);
        state.currentWorkflow.nodes = state.currentWorkflow.nodes.filter(n => n.id !== nodeId);
        state.currentWorkflow.connections = state.currentWorkflow.connections.filter(
          c => c.source !== nodeId && c.target !== nodeId
        );
        state.isDirty = true;
        if (state.selectedNode === nodeId) {
          state.selectedNode = null;
        }
      }
    }),
    
    selectNode: (nodeId) => set((state) => {
      Logger.workflow('Select node', nodeId || 'none');
      state.selectedNode = nodeId;
      state.selectedConnection = null;
    }),
    
    addConnection: (connection) => set((state) => {
      if (state.currentWorkflow) {
        Logger.workflow('Add connection', connection.id, { source: connection.source, target: connection.target });
        state.currentWorkflow.connections.push(connection);
        state.isDirty = true;
      }
    }),
    
    deleteConnection: (connectionId) => set((state) => {
      if (state.currentWorkflow) {
        state.currentWorkflow.connections = state.currentWorkflow.connections.filter(
          c => c.id !== connectionId
        );
        state.isDirty = true;
        if (state.selectedConnection === connectionId) {
          state.selectedConnection = null;
        }
      }
    }),
    
    selectConnection: (connectionId) => set((state) => {
      state.selectedConnection = connectionId;
      state.selectedNode = null;
    }),
    
    startExecution: () => set((state) => {
      Logger.workflow('Start execution', state.currentWorkflow?.id);
      state.isExecuting = true;
      state.executionLogs = [];
    }),
    
    updateExecution: (execution) => set((state) => {
      Logger.workflow('Update execution', execution.id, { status: execution.status });
      state.currentExecution = execution;
      if (execution.status === 'completed' || execution.status === 'failed') {
        state.isExecuting = false;
      }
    }),
    
    addExecutionLog: (log) => set((state) => {
      state.executionLogs.push(log);
    }),
    
    clearExecution: () => set((state) => {
      state.currentExecution = null;
      state.executionLogs = [];
      state.isExecuting = false;
    }),
    
    setWorkflows: (workflows) => set((state) => {
      state.workflows = workflows;
    }),
    
    markDirty: (isDirty) => set((state) => {
      state.isDirty = isDirty;
    }),
  }))
);