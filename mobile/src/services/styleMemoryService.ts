import { apiClient } from './apiClient';

export interface StyleSuggestion {
  style: string;
  confidence: number;
  reason: string;
  basedOn?: string[];
}

export interface StyleInsights {
  total_interactions: number;
  style_preferences: { [key: string]: number };
  top_styles: string[];
  confidence_trends: any;
}

export interface InteractionType {
  LOVE: 'love';
  LIKE: 'like';
  DISLIKE: 'dislike';
  HATE: 'hate';
  SIMILAR: 'similar';
  RECIPE: 'recipe';
}

export const styleMemoryService = {
  // Get AI-powered suggestions
  async getSuggestions(): Promise<StyleSuggestion[]> {
    try {
      const response = await apiClient.get('/style-memory/suggestions/');
      return response.data || [];
    } catch (error) {
      console.error('Failed to get style suggestions:', error);
      return [];
    }
  },

  // Get comprehensive style insights and analytics
  async getInsights(): Promise<StyleInsights | null> {
    try {
      const response = await apiClient.get('/style-memory/insights/');
      return response.data;
    } catch (error) {
      console.error('Failed to get style insights:', error);
      return null;
    }
  },

  // Capture user interactions with generated content
  async captureInteraction(
    contentId: string,
    interactionType: string,
    parentContentId?: string,
    notes?: string
  ) {
    try {
      const response = await apiClient.post('/style-memory/', {
        content_id: contentId,
        interaction_type: interactionType,
        parent_content_id: parentContentId,
        notes,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to capture interaction:', error);
      throw error;
    }
  },

  // Generate variations based on style preferences
  async generateSimilar(request: any) {
    try {
      const response = await apiClient.post('/style-memory/generate-similar/', request);
      return response.data;
    } catch (error) {
      console.error('Failed to generate similar content:', error);
      throw error;
    }
  },

  // Get the family tree of an image
  async getLineage(contentId: string) {
    try {
      const response = await apiClient.get(`/style-memory/lineage/${contentId}/`);
      return response.data;
    } catch (error) {
      console.error('Failed to get lineage:', error);
      return null;
    }
  },

  // Respond to a suggestion (use it or dismiss it)
  async respondToSuggestion(suggestionId: string, response: 'used' | 'dismissed') {
    try {
      const result = await apiClient.post(`/style-memory/suggestions/${suggestionId}/respond/`, {
        response,
      });
      return result.data;
    } catch (error) {
      console.error('Failed to respond to suggestion:', error);
      throw error;
    }
  },

  // Get style memories for a specific user
  async getStyleMemories(limit = 50) {
    try {
      const response = await apiClient.get(`/style-memory/?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get style memories:', error);
      return [];
    }
  },

  // Extract style recipe from a successful generation
  async extractRecipe(contentId: string) {
    try {
      const response = await apiClient.get(`/style-memory/recipe/${contentId}/`);
      return response.data;
    } catch (error) {
      console.error('Failed to extract recipe:', error);
      return null;
    }
  },

  // Search similar styles using semantic search
  async searchSimilarStyles(query: string, limit = 10) {
    try {
      const response = await apiClient.post('/style-memory/search/', {
        query,
        limit,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to search similar styles:', error);
      return [];
    }
  },
};