import { apiClient, API_BASE_URL, DEFAULT_AUTH_TOKEN } from './api.config';

export interface CreateWorkflowRequest {
  name: string;
  description: string;
  agents: Array<{
    name: string;
    order: number;
    params?: Record<string, any>;
    input_from?: string | string[];
  }>;
  flow_config: {
    type: 'sequential' | 'parallel';
    error_handling?: 'stop' | 'continue';
    save_intermediate?: boolean;
    feedback_loops?: boolean;
    max_iterations?: number;
    merge_strategy?: 'combine' | 'latest';
  };
}

export interface ExecuteWorkflowRequest {
  workflow_name: string;
  prompt: string;
  params?: Record<string, any>;
}

export interface WorkflowExecutionResult {
  success: boolean;
  conversation_id: number;
  execution_result: {
    type: string;
    results: Array<{
      agent: string;
      success: boolean;
      content?: string;
      error?: string;
    }>;
    final_output: string;
  };
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  agent_count: number;
  created_at: string;
  version: string;
}

export interface WorkflowTemplate {
  name: string;
  description: string;
  agents: Array<{
    name: string;
    order: number;
    params?: Record<string, any>;
    input_from?: string | string[];
  }>;
  flow_config: {
    type: string;
    error_handling?: string;
    save_intermediate?: boolean;
    feedback_loops?: boolean;
    max_iterations?: number;
    merge_strategy?: string;
  };
}

export interface WorkflowStatus {
  workflow_id: string;
  workflow_name: string;
  status: 'running' | 'completed' | 'failed';
  message_count: number;
  start_time: string;
  messages: Array<{
    id: number;
    role: string;
    content: string;
    created_at: string;
    agent: string;
  }>;
}

class WorkflowsService {
  async createWorkflow(workflowData: CreateWorkflowRequest): Promise<{success: boolean; workflow: any}> {
    try {
      const response = await apiClient.post('/api/v1/workflows/create/', workflowData);
      return response.data;
    } catch (error) {
      console.error('Error creating workflow:', error);
      throw error;
    }
  }

  async executeWorkflow(executeData: ExecuteWorkflowRequest): Promise<WorkflowExecutionResult> {
    try {
      const response = await apiClient.post('/api/v1/workflows/execute/', executeData);
      return response.data;
    } catch (error) {
      console.error('Error executing workflow:', error);
      throw error;
    }
  }

  async listWorkflows(): Promise<{workflows: Workflow[]}> {
    try {
      const response = await apiClient.get('/api/v1/workflows/list/');
      return response.data;
    } catch (error) {
      console.error('Error listing workflows:', error);
      throw error;
    }
  }

  async getWorkflowTemplates(): Promise<{templates: WorkflowTemplate[]}> {
    try {
      const response = await apiClient.get('/api/v1/workflows/templates/');
      return response.data;
    } catch (error) {
      console.error('Error getting workflow templates:', error);
      throw error;
    }
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    try {
      const response = await apiClient.get(`/api/v1/workflows/status/${workflowId}/`);
      return response.data;
    } catch (error) {
      console.error('Error getting workflow status:', error);
      throw error;
    }
  }

  // Utility methods for workflow management
  async validateWorkflow(workflowData: CreateWorkflowRequest): Promise<{valid: boolean; errors: string[]}> {
    const errors: string[] = [];

    // Basic validation
    if (!workflowData.name) {
      errors.push('Workflow name is required');
    }

    if (!workflowData.agents || workflowData.agents.length === 0) {
      errors.push('At least one agent is required');
    }

    // Validate agent order
    const orders = workflowData.agents.map(a => a.order);
    const uniqueOrders = new Set(orders);
    if (workflowData.flow_config.type === 'sequential' && uniqueOrders.size !== orders.length) {
      errors.push('Sequential workflows require unique order values');
    }

    // Validate input dependencies
    const agentNames = workflowData.agents.map(a => a.name);
    for (const agent of workflowData.agents) {
      if (agent.input_from) {
        const dependencies = Array.isArray(agent.input_from) ? agent.input_from : [agent.input_from];
        for (const dep of dependencies) {
          if (!agentNames.includes(dep)) {
            errors.push(`Agent ${agent.name} depends on non-existent agent: ${dep}`);
          }
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  async duplicateWorkflow(workflowId: string, newName: string): Promise<{success: boolean; workflow: any}> {
    try {
      // Get existing workflow data
      const workflows = await this.listWorkflows();
      const workflow = workflows.workflows.find(w => w.id === workflowId);
      
      if (!workflow) {
        throw new Error('Workflow not found');
      }

      // Create duplicate with new name
      const duplicateData: CreateWorkflowRequest = {
        name: newName,
        description: `Copy of ${workflow.name}`,
        agents: [], // Would need to get full workflow data
        flow_config: {
          type: 'sequential',
          error_handling: 'stop',
          save_intermediate: true
        }
      };

      return await this.createWorkflow(duplicateData);
    } catch (error) {
      console.error('Error duplicating workflow:', error);
      throw error;
    }
  }

  // Real-time status monitoring
  async monitorWorkflowExecution(workflowId: string, onStatusUpdate: (status: WorkflowStatus) => void): Promise<void> {
    const pollInterval = 2000; // 2 seconds
    let polling = true;

    const poll = async () => {
      if (!polling) return;

      try {
        const status = await this.getWorkflowStatus(workflowId);
        onStatusUpdate(status);

        if (status.status === 'completed' || status.status === 'failed') {
          polling = false;
          return;
        }

        setTimeout(poll, pollInterval);
      } catch (error) {
        console.error('Error polling workflow status:', error);
        polling = false;
      }
    };

    poll();
  }
}

export const workflowsService = new WorkflowsService();