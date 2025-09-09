import { apiClient } from './api.config';
import type {
  StyleMemory,
  StyleInsights,
  VariationRequest,
  VariationResponse,
  LineageTree,
  InteractionType,
  StyleSuggestion,
} from '../types/style-memory.types';

export const styleMemoryService = {
  // Capture user interactions with generated content
  async captureInteraction(contentId: string, interactionType: InteractionType, parentContentId?: string, notes?: string) {
    const { data } = await apiClient.post<{
      success: boolean;
      style_memory_id: string;
      recipe: any;
      patterns_detected: number;
      new_suggestions: number;
    }>('/style-memory/', {
      content_id: contentId,
      interaction_type: interactionType,
      parent_content_id: parentContentId,
      notes,
    });
    return data;
  },

  // Get comprehensive style insights and analytics
  async getInsights() {
    const { data } = await apiClient.get<StyleInsights>('/style-memory/insights/');
    return data;
  },

  // Generate variations based on style preferences
  async generateSimilar(request: VariationRequest) {
    const { data } = await apiClient.post<VariationResponse>('/style-memory/generate-similar/', request);
    return data;
  },

  // Get the family tree of an image
  async getLineage(contentId: string) {
    const { data } = await apiClient.get<LineageTree>(`/style-memory/lineage/${contentId}/`);
    return data;
  },

  // Get AI-powered suggestions
  async getSuggestions() {
    const { data } = await apiClient.get<StyleSuggestion[]>('/style-memory/suggestions/');
    return data;
  },

  // Respond to a suggestion (use it or dismiss it)
  async respondToSuggestion(suggestionId: string, response: 'used' | 'dismissed') {
    const { data } = await apiClient.post(`/style-memory/suggestions/${suggestionId}/respond/`, {
      response,
    });
    return data;
  },

  // Get style memories for a specific user
  async getStyleMemories(limit = 50) {
    const { data } = await apiClient.get<StyleMemory[]>(`/style-memory/?limit=${limit}`);
    return data;
  },

  // Extract style recipe from a successful generation
  async extractRecipe(contentId: string) {
    const { data } = await apiClient.get(`/style-memory/recipe/${contentId}/`);
    return data;
  },

  // Search similar styles using semantic search
  async searchSimilarStyles(query: string, limit = 10) {
    const { data } = await apiClient.post('/style-memory/search/', {
      query,
      limit,
    });
    return data;
  },

  // Batch operations for bulk interactions
  async batchInteractions(interactions: Array<{
    content_id: string;
    interaction_type: InteractionType;
    notes?: string;
  }>) {
    const { data } = await apiClient.post('/style-memory/batch/', {
      interactions,
    });
    return data;
  },

  // Get evolution timeline of user's style preferences
  async getEvolutionTimeline(timeRange = '30d') {
    const { data } = await apiClient.get(`/style-memory/evolution/?range=${timeRange}`);
    return data;
  },
};