import { apiClient } from './api.config';

export interface Feedback {
  id?: number;
  content_type: 'text' | 'image' | 'video' | 'blog' | 'social' | 'ebook' | 'voice' | 'research';
  content_id: number;
  overall_rating: number;
  quality_rating?: number;
  accuracy_rating?: number;
  usefulness_rating?: number;
  feedback_type?: string;
  comments?: string;
  suggestions?: string;
  would_recommend?: boolean;
  met_expectations?: boolean;
  saved_time?: boolean;
  tags?: string[];
  generation_params?: Record<string, any>;
  created_at?: string;
  admin_response?: string;
}

export interface FeedbackStats {
  average_rating: number;
  total_feedback: number;
  rating_distribution: Record<number, number>;
  recommendations: number;
  recent_comments: Array<{
    user__username: string;
    comments: string;
    overall_rating: number;
    created_at: string;
  }>;
}

export interface FeedbackAnalytics {
  period: {
    start: string;
    end: string;
    days: number;
  };
  by_content_type: Record<string, {
    total_feedback: number;
    average_rating: number;
    positive: number;
    neutral: number;
    negative: number;
  }>;
  user_contribution: number;
  total_feedback: number;
}

class FeedbackService {
  async submitFeedback(feedback: Feedback): Promise<any> {
    const response = await apiClient.post('/feedback/submit/', feedback);
    return response.data;
  }

  async quickFeedback(
    content_type: string,
    content_id: number,
    is_positive: boolean
  ): Promise<any> {
    const response = await apiClient.post('/feedback/quick/', {
      content_type,
      content_id,
      is_positive,
    });
    return response.data;
  }

  async getContentFeedback(
    content_type: string,
    content_id: number
  ): Promise<{
    user_feedback: Feedback | null;
    stats: FeedbackStats | null;
    recent_feedback: any[];
  }> {
    const response = await apiClient.get(`/feedback/${content_type}/${content_id}/`);
    return response.data;
  }

  async getFeedbackHistory(params?: {
    content_type?: string;
    min_rating?: number;
    page?: number;
    per_page?: number;
  }): Promise<any> {
    const response = await apiClient.get('/feedback/history/', { params });
    return response.data;
  }

  async updateFeedback(feedbackId: number, data: Partial<Feedback>): Promise<any> {
    const response = await apiClient.put(`/feedback/${feedbackId}/`, data);
    return response.data;
  }

  async deleteFeedback(feedbackId: number): Promise<any> {
    const response = await apiClient.delete(`/feedback/${feedbackId}/`);
    return response.data;
  }

  async getAnalytics(days: number = 30, content_type?: string): Promise<FeedbackAnalytics> {
    const params: any = { days };
    if (content_type) params.content_type = content_type;
    const response = await apiClient.get('/feedback/analytics/', { params });
    return response.data;
  }
}

export const feedbackService = new FeedbackService();

// Re-export types for easier importing
export type { Feedback, FeedbackStats, FeedbackAnalytics };