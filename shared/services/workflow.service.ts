import { apiClient } from './api.config';
import type { Workflow, WorkflowExecution, WorkflowTemplate } from '../types/workflow.types';

export const workflowService = {
  // Workflow CRUD operations
  async getWorkflows() {
    const { data } = await apiClient.get<Workflow[]>('/workflows/');
    return data;
  },

  async getWorkflow(id: string) {
    const { data } = await apiClient.get<Workflow>(`/workflows/${id}/`);
    return data;
  },

  async createWorkflow(workflow: Partial<Workflow>) {
    const { data } = await apiClient.post<Workflow>('/workflows/', workflow);
    return data;
  },

  async updateWorkflow(id: string, workflow: Partial<Workflow>) {
    const { data } = await apiClient.put<Workflow>(`/workflows/${id}/`, workflow);
    return data;
  },

  async deleteWorkflow(id: string) {
    await apiClient.delete(`/workflows/${id}/`);
  },

  async duplicateWorkflow(id: string) {
    const { data } = await apiClient.post<Workflow>(`/workflows/${id}/duplicate/`);
    return data;
  },

  // Workflow execution
  async executeWorkflow(id: string, params?: Record<string, any>) {
    const { data } = await apiClient.post<WorkflowExecution>(
      `/workflows/${id}/execute/`,
      params
    );
    return data;
  },

  async getExecutions(workflowId: string) {
    const { data } = await apiClient.get<WorkflowExecution[]>(
      `/workflows/${workflowId}/executions/`
    );
    return data;
  },

  async getExecution(workflowId: string, executionId: string) {
    const { data } = await apiClient.get<WorkflowExecution>(
      `/workflows/executions/${executionId}/`
    );
    return data;
  },

  // Workflow scheduling
  async scheduleWorkflow(id: string, schedule: any) {
    const { data } = await apiClient.post(`/workflows/${id}/schedule/`, schedule);
    return data;
  },

  async removeSchedule(id: string) {
    await apiClient.delete(`/workflows/${id}/schedule/`);
  },

  // Templates
  async getTemplates() {
    const { data } = await apiClient.get<WorkflowTemplate[]>('/workflows/templates/');
    return data;
  },

  async createFromTemplate(templateId: string, name: string) {
    const { data } = await apiClient.post<Workflow>('/workflows/from-template/', {
      templateId,
      name,
    });
    return data;
  },

  // Node registry
  async getAvailableNodes() {
    const { data } = await apiClient.get('/workflow-nodes/');
    return data;
  },

  async getNodeConfig(nodeType: string) {
    const { data } = await apiClient.get(`/workflow-nodes/${nodeType}/config/`);
    return data;
  },
};