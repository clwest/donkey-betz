import { apiClient } from './apiClient';

export interface PromptingSettings {
  enabled: boolean;
  default_level: 'basic' | 'advanced' | 'expert';
  use_memory: boolean;
  auto_enhance: boolean;
  content_preferences: Record<string, boolean>;
}

export interface PromptingStats {
  period: {
    start: string;
    end: string;
    days: number;
  };
  overview: {
    total_content: number;
    enhanced_content: number;
    enhancement_rate: number;
    memory_usage_rate: number;
  };
  by_level: Record<string, number>;
  by_content_type: Record<string, any>;
  techniques_used: Record<string, number>;
}

export interface EnhancementTest {
  original: string;
  enhanced: string;
  level: string;
  metadata: any;
  memory_context: number;
  techniques: string[];
  examples: string[];
}

export interface EnhancementSuggestions {
  content_type: string;
  suggestions: string[];
  pro_tips: string[];
}

class PromptingService {
  async getSettings(): Promise<PromptingSettings> {
    try {
      const response = await apiClient.get('/prompting/settings/');
      return response.data;
    } catch (error) {
      console.error('Failed to get prompting settings:', error);
      // Return default settings
      return {
        enabled: true,
        default_level: 'basic',
        use_memory: true,
        auto_enhance: false,
        content_preferences: {},
      };
    }
  }

  async updateSettings(settings: Partial<PromptingSettings>): Promise<any> {
    try {
      const response = await apiClient.put('/prompting/settings/', settings);
      return response.data;
    } catch (error) {
      console.error('Failed to update prompting settings:', error);
      throw error;
    }
  }

  async getStats(days: number = 30): Promise<PromptingStats> {
    try {
      const response = await apiClient.get(`/prompting/stats/?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get prompting stats:', error);
      // Return empty stats
      return {
        period: { start: '', end: '', days: 0 },
        overview: { total_content: 0, enhanced_content: 0, enhancement_rate: 0, memory_usage_rate: 0 },
        by_level: {},
        by_content_type: {},
        techniques_used: {},
      };
    }
  }

  async testEnhancement(params: {
    prompt: string;
    level: string;
    content_type?: string;
    use_memory?: boolean;
    context?: any;
  }): Promise<EnhancementTest> {
    try {
      const response = await apiClient.post('/prompting/test/', params);
      return response.data;
    } catch (error) {
      console.error('Failed to test enhancement:', error);
      throw error;
    }
  }

  async getSuggestions(contentType: string = 'default'): Promise<EnhancementSuggestions> {
    try {
      const response = await apiClient.get(`/prompting/suggestions/?content_type=${contentType}`);
      // Ensure we always return a valid object
      return response.data || {
        content_type: contentType,
        suggestions: [],
        pro_tips: [],
      };
    } catch (error) {
      console.error('Failed to get suggestions:', error);
      return {
        content_type: contentType,
        suggestions: [],
        pro_tips: [],
      };
    }
  }
}

export const promptingService = new PromptingService();