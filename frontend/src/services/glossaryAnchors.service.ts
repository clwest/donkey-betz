/**
 * API service for Glossary Anchors System
 * Ready for backend API implementation - currently provides mock data structure
 */

import { apiClient } from './api.config';
import type {
  GlossaryAnchor,
  AnchorCluster,
  AnchorPerformanceLog,
  AnchorAnalytics,
  AnchorRecommendation,
  CreateAnchorRequest,
  UpdateAnchorRequest,
  AnchorSearchFilters,
  BulkAnchorOperation,
  AnchorValidationResult,
  MemoryRetrievalTest,
} from '../types/glossaryAnchors.types';

export class GlossaryAnchorsService {
  private readonly baseUrl = '/glossary-anchors'; // Future API endpoint

  /**
   * Get all anchors with filtering and pagination
   */
  async listAnchors(filters?: AnchorSearchFilters): Promise<{
    anchors: GlossaryAnchor[];
    pagination: {
      total: number;
      limit: number;
      offset: number;
      has_next: boolean;
    };
  }> {
    // TODO: Replace with actual API call when backend is ready
    // const response = await apiClient.get(`${this.baseUrl}/`, { params: filters });
    // return response.data;
    
    // Mock implementation for now
    return this.getMockAnchorsData(filters);
  }

  /**
   * Get anchor by ID
   */
  async getAnchor(anchorId: string): Promise<GlossaryAnchor> {
    // TODO: Replace with actual API call
    // const response = await apiClient.get(`${this.baseUrl}/${anchorId}/`);
    // return response.data;
    
    return this.getMockAnchor(anchorId);
  }

  /**
   * Create new anchor
   */
  async createAnchor(anchorData: CreateAnchorRequest): Promise<GlossaryAnchor> {
    // TODO: Replace with actual API call
    // const response = await apiClient.post(`${this.baseUrl}/`, anchorData);
    // return response.data;
    
    return this.getMockCreatedAnchor(anchorData);
  }

  /**
   * Update existing anchor
   */
  async updateAnchor(anchorData: UpdateAnchorRequest): Promise<GlossaryAnchor> {
    // TODO: Replace with actual API call
    // const response = await apiClient.put(`${this.baseUrl}/${anchorData.id}/`, anchorData);
    // return response.data;
    
    return this.getMockUpdatedAnchor(anchorData);
  }

  /**
   * Delete anchor
   */
  async deleteAnchor(anchorId: string): Promise<void> {
    // TODO: Replace with actual API call
    // await apiClient.delete(`${this.baseUrl}/${anchorId}/`);
    
    console.log(`Mock: Deleted anchor ${anchorId}`);
  }

  /**
   * Get anchor analytics and performance data
   */
  async getAnalytics(days: number = 30): Promise<AnchorAnalytics> {
    // TODO: Replace with actual API call
    // const response = await apiClient.get(`${this.baseUrl}/analytics/`, { params: { days } });
    // return response.data;
    
    return this.getMockAnalytics();
  }

  /**
   * Get anchor recommendations based on query patterns
   */
  async getRecommendations(limit: number = 10): Promise<AnchorRecommendation[]> {
    // TODO: Replace with actual API call
    // const response = await apiClient.get(`${this.baseUrl}/recommendations/`, { params: { limit } });
    // return response.data;
    
    return this.getMockRecommendations();
  }

  /**
   * Validate anchor effectiveness
   */
  async validateAnchors(anchorIds: string[]): Promise<AnchorValidationResult[]> {
    // TODO: Replace with actual API call
    // const response = await apiClient.post(`${this.baseUrl}/validate/`, { anchor_ids: anchorIds });
    // return response.data;
    
    return this.getMockValidationResults(anchorIds);
  }

  /**
   * Perform bulk operations on anchors
   */
  async bulkOperation(operation: BulkAnchorOperation): Promise<{
    success_count: number;
    failed_count: number;
    errors: Array<{ anchor_id: string; error: string }>;
  }> {
    // TODO: Replace with actual API call
    // const response = await apiClient.post(`${this.baseUrl}/bulk-operation/`, operation);
    // return response.data;
    
    return {
      success_count: operation.anchor_ids.length,
      failed_count: 0,
      errors: [],
    };
  }

  /**
   * Test memory retrieval with specific anchors
   */
  async testRetrieval(query: string, anchorIds: string[]): Promise<MemoryRetrievalTest> {
    // TODO: Replace with actual API call
    // const response = await apiClient.post(`${this.baseUrl}/test-retrieval/`, { query, anchor_ids: anchorIds });
    // return response.data;
    
    return this.getMockRetrievalTest(query, anchorIds);
  }

  /**
   * Get performance logs for specific anchor
   */
  async getPerformanceLogs(anchorId: string, limit: number = 20): Promise<AnchorPerformanceLog[]> {
    // TODO: Replace with actual API call
    // const response = await apiClient.get(`${this.baseUrl}/${anchorId}/performance/`, { params: { limit } });
    // return response.data;
    
    return this.getMockPerformanceLogs(anchorId);
  }

  /**
   * Get anchor clusters
   */
  async getClusters(): Promise<AnchorCluster[]> {
    // TODO: Replace with actual API call
    // const response = await apiClient.get(`${this.baseUrl}/clusters/`);
    // return response.data;
    
    return this.getMockClusters();
  }

  // Utility methods
  getAnchorTypeColor(type: GlossaryAnchor['anchor_type']): string {
    const colors = {
      technical: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      domain: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      process: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      feature: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      methodology: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      system: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      user_term: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    };
    return colors[type];
  }

  getConfidenceColor(confidence: 'high' | 'medium' | 'low'): string {
    const colors = {
      high: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      low: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return colors[confidence];
  }

  formatEffectivenessScore(score: number): string {
    if (score >= 8) return '🏆 Excellent';
    if (score >= 6) return '✅ Good';
    if (score >= 4) return '⚠️ Needs Improvement';
    return '❌ Poor';
  }

  // Mock data methods (remove when backend API is ready)
  private async getMockAnchorsData(filters?: AnchorSearchFilters): Promise<{
    anchors: GlossaryAnchor[];
    pagination: { total: number; limit: number; offset: number; has_next: boolean };
  }> {
    const mockAnchors: GlossaryAnchor[] = [
      {
        id: '1',
        term: 'machine learning',
        variants: ['ML', 'artificial intelligence', 'AI model'],
        description: 'Computational methods that enable systems to learn from data',
        anchor_type: 'technical',
        domain_context: 'AI/ML',
        source_evidence: {
          documents: ['ml_intro.pdf', 'ai_fundamentals.md'],
          queries: ['how does ML work', 'machine learning basics'],
        },
        confidence: 'high',
        fallback_score: 8.5,
        related_memories: ['mem_1', 'mem_2', 'mem_3'],
        query_matches: 45,
        retrieval_improvements: 12,
        last_matched: '2024-01-15T10:30:00Z',
        is_active: true,
        user: null,
        created_by: 'system',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T10:30:00Z',
        effectiveness_score: 8.5,
      },
      {
        id: '2',
        term: 'prompt engineering',
        variants: ['prompt design', 'prompt optimization'],
        description: 'The practice of designing effective prompts for AI models',
        anchor_type: 'methodology',
        domain_context: 'AI/Prompting',
        source_evidence: {
          queries: ['how to write better prompts', 'prompt engineering tips'],
        },
        confidence: 'high',
        fallback_score: 9.2,
        related_memories: ['mem_4', 'mem_5'],
        query_matches: 23,
        retrieval_improvements: 8,
        last_matched: '2024-01-14T15:20:00Z',
        is_active: true,
        user: 'user_1',
        created_by: 'user',
        created_at: '2024-01-10T12:00:00Z',
        updated_at: '2024-01-14T15:20:00Z',
        effectiveness_score: 9.2,
      },
    ];

    return {
      anchors: mockAnchors,
      pagination: {
        total: mockAnchors.length,
        limit: 20,
        offset: 0,
        has_next: false,
      },
    };
  }

  private async getMockAnchor(id: string): Promise<GlossaryAnchor> {
    const { anchors } = await this.getMockAnchorsData();
    return anchors[0]; // Return first mock anchor
  }

  private async getMockCreatedAnchor(data: CreateAnchorRequest): Promise<GlossaryAnchor> {
    return {
      id: 'new_anchor_' + Date.now(),
      term: data.term,
      variants: data.variants || [],
      description: data.description,
      anchor_type: data.anchor_type,
      domain_context: data.domain_context || '',
      source_evidence: data.source_evidence || {},
      confidence: data.confidence || 'medium',
      fallback_score: 5.0,
      related_memories: [],
      query_matches: 0,
      retrieval_improvements: 0,
      last_matched: null,
      is_active: data.is_active !== false,
      user: 'current_user',
      created_by: 'user',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      effectiveness_score: 5.0,
    };
  }

  private async getMockUpdatedAnchor(data: UpdateAnchorRequest): Promise<GlossaryAnchor> {
    const existing = await this.getMockAnchor(data.id);
    return {
      ...existing,
      ...data,
      updated_at: new Date().toISOString(),
    };
  }

  private async getMockAnalytics(): Promise<AnchorAnalytics> {
    return {
      total_anchors: 24,
      active_anchors: 20,
      user_anchors: 8,
      global_anchors: 16,
      avg_effectiveness_score: 7.2,
      total_query_matches: 145,
      total_improvements: 32,
      anchor_types_breakdown: {
        technical: 8,
        domain: 6,
        methodology: 4,
        feature: 3,
        process: 2,
        system: 1,
      },
      confidence_distribution: {
        high: 12,
        medium: 8,
        low: 4,
      },
      recent_performance: [],
      top_performing_anchors: [],
    };
  }

  private async getMockRecommendations(): Promise<AnchorRecommendation[]> {
    return [
      {
        suggested_term: 'react hooks',
        suggested_variants: ['hooks', 'useEffect', 'useState'],
        confidence: 0.85,
        reasoning: 'Frequent queries about React hooks with low retrieval success',
        source_queries: ['how to use react hooks', 'useEffect tutorial'],
        potential_impact: 'high',
        domain_context: 'Frontend Development',
        anchor_type: 'technical',
      },
    ];
  }

  private async getMockValidationResults(anchorIds: string[]): Promise<AnchorValidationResult[]> {
    return anchorIds.map(id => ({
      anchor_id: id,
      is_valid: true,
      issues: [],
      recommendations: [],
    }));
  }

  private async getMockRetrievalTest(query: string, anchorIds: string[]): Promise<MemoryRetrievalTest> {
    return {
      query,
      expected_memories: ['mem_1', 'mem_2'],
      actual_memories: ['mem_1', 'mem_3'],
      matching_anchors: anchorIds,
      precision_score: 0.75,
      recall_score: 0.65,
      f1_score: 0.70,
      improvement_suggestions: ['Add more specific variants', 'Increase confidence level'],
    };
  }

  private async getMockPerformanceLogs(anchorId: string): Promise<AnchorPerformanceLog[]> {
    return [];
  }

  private async getMockClusters(): Promise<AnchorCluster[]> {
    return [
      {
        id: 'cluster_1',
        name: 'AI/ML Concepts',
        description: 'Machine learning and artificial intelligence terminology',
        anchors: ['1', '2'],
        domain_focus: 'AI/ML',
        semantic_coherence_score: 8.7,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T10:30:00Z',
      },
    ];
  }
}

// Export singleton instance
export const glossaryAnchorsService = new GlossaryAnchorsService();