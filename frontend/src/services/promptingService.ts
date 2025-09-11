import { apiClient } from './api.config';

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
    const response = await apiClient.get('/api/v1/prompting/settings/');
    return response.data;
  }

  async updateSettings(settings: Partial<PromptingSettings>): Promise<any> {
    const response = await apiClient.put('/api/v1/prompting/settings/', settings);
    return response.data;
  }

  async getStats(days: number = 30): Promise<PromptingStats> {
    const response = await apiClient.get(`/api/v1/prompting/stats/?days=${days}`);
    return response.data;
  }

  async testEnhancement(params: {
    prompt: string;
    level: string;
    content_type?: string;
    use_memory?: boolean;
    context?: any;
  }): Promise<EnhancementTest> {
    const response = await apiClient.post('/api/v1/prompting/test/', params);
    return response.data;
  }

  async getSuggestions(contentType: string = 'default'): Promise<EnhancementSuggestions> {
    const response = await apiClient.get(`/api/v1/prompting/suggestions/?content_type=${contentType}`);
    return response.data;
  }
}

export const promptingService = new PromptingService();