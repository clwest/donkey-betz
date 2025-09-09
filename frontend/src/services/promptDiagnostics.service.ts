/**
 * API service for Prompt Diagnostics System
 * Handles communication with Django backend for prompt analysis and optimization
 */

import { apiClient } from './api.config';
import type {
  PromptAnalysisRequest,
  PromptAnalysisResult,
  PromptAnalysisSummary,
  PromptTemplate,
  OptimizationSession,
  DiagnosticsDashboardData,
  QuickAnalysisResult,
  BatchAnalysisRequest,
} from '../types/promptDiagnostics.types';

export class PromptDiagnosticsService {
  private readonly baseUrl = '/prompt-diagnostics';

  /**
   * Perform full prompt analysis and optimization
   */
  async analyzePrompt(request: PromptAnalysisRequest): Promise<PromptAnalysisResult> {
    const response = await apiClient.post(`${this.baseUrl}/analyze/`, request);
    return response.data;
  }

  /**
   * Quick analysis for immediate feedback (no optimization)
   */
  async quickAnalyze(prompt: string): Promise<QuickAnalysisResult> {
    const response = await apiClient.post(`${this.baseUrl}/quick-analyze/`, { prompt });
    return response.data;
  }

  /**
   * Batch analyze multiple prompts
   */
  async batchAnalyze(request: BatchAnalysisRequest): Promise<OptimizationSession> {
    const response = await apiClient.post(`${this.baseUrl}/batch-analyze/`, request);
    return response.data;
  }

  /**
   * Get list of user's analyses with pagination and filtering
   */
  async listAnalyses(params?: {
    status?: 'analyzing' | 'completed' | 'failed';
    prompt_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    analyses: PromptAnalysisSummary[];
    pagination: {
      total: number;
      limit: number;
      offset: number;
      has_next: boolean;
    };
  }> {
    const response = await apiClient.get(`${this.baseUrl}/analyses/`, { params });
    return response.data;
  }

  /**
   * Get detailed analysis by ID
   */
  async getAnalysis(analysisId: string): Promise<PromptAnalysisResult> {
    const response = await apiClient.get(`${this.baseUrl}/analyses/${analysisId}/`);
    return response.data;
  }

  /**
   * Delete an analysis
   */
  async deleteAnalysis(analysisId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/analyses/${analysisId}/`);
  }

  /**
   * Create a template from an analysis or custom text
   */
  async createTemplate(templateData: {
    analysis_id?: string;
    name: string;
    description: string;
    category?: 'general' | 'creative' | 'analytical' | 'technical' | 'conversational' | 'system';
    template_text?: string;
    is_public?: boolean;
  }): Promise<PromptTemplate> {
    const response = await apiClient.post(`${this.baseUrl}/templates/create/`, templateData);
    return response.data;
  }

  /**
   * Get list of available templates
   */
  async listTemplates(params?: {
    category?: string;
    is_public?: boolean;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    templates: PromptTemplate[];
    pagination: {
      total: number;
      limit: number;
      offset: number;
      has_next: boolean;
    };
  }> {
    const response = await apiClient.get(`${this.baseUrl}/templates/`, { params });
    return response.data;
  }

  /**
   * Get diagnostics dashboard data
   */
  async getDashboardData(days: number = 30): Promise<DiagnosticsDashboardData> {
    const response = await apiClient.get(`${this.baseUrl}/dashboard/`, {
      params: { days }
    });
    return response.data;
  }

  /**
   * Utility: Format token count with appropriate units
   */
  formatTokenCount(count: number): string {
    if (count < 1000) return `${count} tokens`;
    if (count < 10000) return `${(count / 1000).toFixed(1)}K tokens`;
    return `${(count / 1000).toFixed(0)}K tokens`;
  }

  /**
   * Utility: Calculate cost estimate based on token count
   */
  calculateCostEstimate(tokens: number, model: string = 'gpt-5-mini'): number {
    const rates = {
      'gpt-5': 0.00125,      // $1.25 per 1K input tokens
      'gpt-5-mini': 0.00025, // $0.25 per 1K input tokens
      'gpt-5-nano': 0.00005, // $0.05 per 1K input tokens
      'gpt-4': 0.00003,      // $0.03 per 1K tokens
      'gpt-4-turbo': 0.00001, // $0.01 per 1K tokens
      'gpt-3.5-turbo': 0.000002, // $0.002 per 1K tokens
    };
    
    const rate = rates[model as keyof typeof rates] || rates['gpt-5-mini'];
    return (tokens / 1000) * rate;
  }

  /**
   * Utility: Get severity color for UI components
   */
  getSeverityColor(severity: 'low' | 'medium' | 'high' | 'critical'): string {
    const colors = {
      low: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      high: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return colors[severity];
  }

  /**
   * Utility: Get priority color for UI components
   */
  getPriorityColor(priority: 'low' | 'medium' | 'high'): string {
    const colors = {
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
      medium: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      high: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    };
    return colors[priority];
  }

  /**
   * Utility: Get complexity rating color
   */
  getComplexityColor(complexity: 'Low' | 'Medium' | 'High'): string {
    const colors = {
      Low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      Medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      High: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return colors[complexity];
  }
}

// Export singleton instance
export const promptDiagnosticsService = new PromptDiagnosticsService();