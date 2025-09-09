import { apiClient } from './api.config';

// Campaign Types
export interface Campaign {
  id: string;
  title: string;
  description: string;
  campaign_type: CampaignType;
  status: 'draft' | 'active' | 'paused' | 'completed';
  target_audience: string;
  budget?: number;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
  content: CampaignContent[];
  analytics?: CampaignAnalytics;
}

export type CampaignType = 'email' | 'sms' | 'social' | 'ppc' | 'display' | 'content';

export interface CampaignContent {
  id: string;
  content_type: 'email' | 'sms' | 'social_post' | 'ad_copy' | 'landing_page' | 'blog_post';
  title: string;
  content: string;
  subject_line?: string;
  call_to_action?: string;
  platform?: string;
  status: 'draft' | 'active' | 'paused';
  performance_metrics?: ContentMetrics;
  created_at: string;
}

export interface ContentMetrics {
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number;
  conversion_rate: number;
  cost_per_click?: number;
  revenue?: number;
}

export interface CampaignAnalytics {
  total_impressions: number;
  total_clicks: number;
  total_conversions: number;
  overall_ctr: number;
  overall_conversion_rate: number;
  total_cost: number;
  total_revenue: number;
  roi: number;
  top_performing_content: CampaignContent[];
}

export interface CampaignTemplate {
  id: string;
  name: string;
  description: string;
  campaign_type: CampaignType;
  template_content: {
    email_templates: Array<{ subject: string; content: string }>;
    sms_templates: Array<{ content: string }>;
    social_templates: Array<{ platform: string; content: string }>;
  };
}

export interface ABTest {
  id: string;
  campaign_id: string;
  name: string;
  variant_a: CampaignContent;
  variant_b: CampaignContent;
  traffic_split: number;
  status: 'draft' | 'running' | 'completed';
  winner?: 'a' | 'b' | 'tie';
  confidence_level?: number;
  created_at: string;
}

// Campaign Service
export const campaignService = {
  // Get all campaigns
  async getCampaigns(): Promise<Campaign[]> {
    const { data } = await apiClient.get('/campaigns/');
    // API returns { success: true, campaigns: [...] }
    return data.campaigns || data;
  },

  // Get single campaign
  async getCampaign(id: string): Promise<Campaign> {
    const { data } = await apiClient.get(`/campaigns/${id}/`);
    // API returns { success: true, campaign: {...} }
    return data.campaign || data;
  },

  // Create campaign
  async createCampaign(campaign: {
    title: string;
    description: string;
    campaign_type: CampaignType;
    target_audience: string;
    budget?: number;
  }): Promise<Campaign> {
    // Backend expects 'name' not 'title'
    const payload = {
      name: campaign.title,
      description: campaign.description,
      campaign_type: campaign.campaign_type,
      target_audience: campaign.target_audience,
      budget: campaign.budget,
    };
    const { data } = await apiClient.post('/campaigns/', payload);
    // API returns { success: true, campaign: {...} }
    return data.campaign || data;
  },

  // Update campaign
  async updateCampaign(id: string, updates: Partial<Campaign>): Promise<Campaign> {
    const { data } = await apiClient.put(`/campaigns/${id}/`, updates);
    return data;
  },

  // Delete campaign
  async deleteCampaign(id: string): Promise<void> {
    await apiClient.delete(`/campaigns/${id}/`);
  },

  // Generate campaign content
  async generateCampaignContent(campaignId: string, contentType: CampaignContent['content_type'], prompt?: string): Promise<any> {
    // Use simple generator for now as it's more reliable
    const { data } = await apiClient.post(`/campaigns/${campaignId}/simple-generate/`, {
      content_type: contentType,
      prompt,
    });
    return data;
  },

  // Batch generate campaign content
  async batchGenerateContent(campaignId: string, contentTypes: CampaignContent['content_type'][], prompt: string): Promise<CampaignContent[]> {
    const { data } = await apiClient.post(`/campaigns/${campaignId}/batch-generate/`, {
      content_types: contentTypes,
      prompt,
    });
    return data;
  },

  // Get campaign templates
  async getTemplates(): Promise<CampaignTemplate[]> {
    const { data } = await apiClient.get('/campaigns/templates/');
    // API returns { success: true, templates: [...] }
    return data.templates || data;
  },

  // Create campaign from template
  async createFromTemplate(templateId: string, customizations: {
    title: string;
    target_audience: string;
    budget?: number;
  }): Promise<Campaign> {
    const { data } = await apiClient.post('/campaigns/from-template/', {
      template_name: templateId, // API expects template_name, not template_id
      customizations: {
        name: customizations.title,
        target_audience: {
          description: customizations.target_audience // API expects object with description
        },
        budget: customizations.budget,
      }
    });
    return data.campaign || data;
  },

  // Get campaign analytics
  async getCampaignAnalytics(id: string): Promise<CampaignAnalytics> {
    const { data } = await apiClient.get(`/campaigns/${id}/analytics/`);
    return data;
  },

  // Get dashboard data
  async getDashboard(): Promise<{
    total_campaigns: number;
    active_campaigns: number;
    total_impressions: number;
    total_clicks: number;
    average_ctr: number;
    total_revenue: number;
    top_campaigns: Campaign[];
    recent_activity: Array<{
      type: string;
      campaign: string;
      timestamp: string;
      details: string;
    }>;
  }> {
    const { data } = await apiClient.get('/campaigns/dashboard/');
    return data;
  },

  // A/B Testing
  async createABTest(test: {
    campaign_id: string;
    name: string;
    variant_a: Partial<CampaignContent>;
    variant_b: Partial<CampaignContent>;
    traffic_split: number;
  }): Promise<ABTest> {
    const { data } = await apiClient.post('/campaigns/ab-tests/', test);
    return data;
  },

  async getABTests(campaignId: string): Promise<ABTest[]> {
    const { data } = await apiClient.get(`/campaigns/${campaignId}/ab-tests/`);
    return data;
  },

  async getABTestResults(testId: string): Promise<ABTest> {
    const { data } = await apiClient.get(`/campaigns/ab-tests/${testId}/results/`);
    return data;
  },

  // Campaign optimization
  async getOptimizationSuggestions(campaignId: string): Promise<{
    suggestions: Array<{
      type: 'budget' | 'targeting' | 'content' | 'timing';
      title: string;
      description: string;
      impact: 'low' | 'medium' | 'high';
      effort: 'low' | 'medium' | 'high';
    }>;
  }> {
    const { data } = await apiClient.get(`/campaigns/${campaignId}/optimize/`);
    return data;
  },

  // Content performance
  async getContentPerformance(campaignId: string): Promise<{
    top_performing: CampaignContent[];
    underperforming: CampaignContent[];
    recommendations: string[];
  }> {
    const { data } = await apiClient.get(`/campaigns/${campaignId}/content-performance/`);
    return data;
  },

  // Export campaign data
  async exportCampaign(campaignId: string, format: 'csv' | 'xlsx' | 'pdf'): Promise<Blob> {
    const { data } = await apiClient.post(`/campaigns/${campaignId}/export/`, {
      format,
    }, {
      responseType: 'blob',
    });
    return data;
  },

  // Launch campaign
  async launchCampaign(campaignId: string): Promise<Campaign> {
    const { data } = await apiClient.post(`/campaigns/${campaignId}/launch/`);
    return data;
  },

  // Pause/Resume campaign
  async pauseCampaign(campaignId: string): Promise<Campaign> {
    const { data } = await apiClient.post(`/campaigns/${campaignId}/pause/`);
    return data;
  },

  async resumeCampaign(campaignId: string): Promise<Campaign> {
    const { data } = await apiClient.post(`/campaigns/${campaignId}/resume/`);
    return data;
  },
};