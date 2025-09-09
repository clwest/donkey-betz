import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// API Configuration
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8001/api',
  default: 'http://10.0.2.2:8001/api', // Android emulator
  // For iOS simulator, use: 'http://localhost:8001/api'
  // For real device, use your computer's IP: 'http://192.168.x.x:8001/api'
});

// Default token for development
const DEFAULT_TOKEN = '993f8273f70877e23b5c7d2f92ed30562a089fe3';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ContentGenerationRequest {
  prompt: string;
  type?: 'text' | 'image';
  content_type?: 'text' | 'image';
  style?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  cfg_scale?: number;
  steps?: number;
  width?: number;
  height?: number;
  negative_prompt?: string;
}

export interface BlogGenerationRequest {
  topic: string;
  tone?: 'professional' | 'casual' | 'technical' | 'marketing';
  length?: 'short' | 'medium' | 'long';
  target_audience?: string;
  keywords?: string[];
  include_meta?: boolean;
  include_images?: boolean;
}

export interface SocialMediaRequest {
  topic: string;
  platforms: ('twitter' | 'linkedin' | 'instagram' | 'facebook')[];
  tone?: string;
  variations_per_platform?: number;
  include_hashtags?: boolean;
  include_emojis?: boolean;
}

export interface BatchGenerationRequest {
  prompt: string;
  variations: number;
  style?: string;
  auto_variations?: boolean;
}

export interface VideoGenerationRequest {
  prompt?: string;
  image_url?: string;
  image_id?: string;
  motion_prompt?: string;
  duration?: 5 | 10;
  resolution?: '720p' | '1080p';
  quality?: 'gen3a_turbo' | 'gen3a';
  use_memory?: boolean;
  enhance_prompt?: boolean;
  enhancement_level?: 'basic' | 'advanced' | 'expert';
  include_voiceover?: boolean;
  voiceover_script?: string;
  voiceover_voice?: string;
  voiceover_style?: string;
}

export interface VideoStatusResponse {
  success: boolean;
  status: 'processing' | 'completed' | 'failed';
  progress?: number;
  task_id: string;
  video_url?: string;
  message?: string;
  raw_status?: string;
}

export interface VideoResponse {
  success: boolean;
  content_id?: number;
  task_id: string;
  error?: string;
}

export interface Video {
  id: number;
  prompt: string;
  video_url: string;
  thumbnail_url?: string;
  duration: number;
  resolution: string;
  status: string;
  created_at: string;
  metadata?: any;
}

class ApiService {
  private token: string | null = null;

  constructor() {
    this.initToken();
  }

  private async initToken() {
    try {
      const storedToken = await AsyncStorage.getItem('auth_token');
      this.token = storedToken || DEFAULT_TOKEN;
    } catch (error) {
      this.token = DEFAULT_TOKEN;
    }
  }

  async setToken(token: string) {
    this.token = token;
    await AsyncStorage.setItem('auth_token', token);
  }

  async clearToken() {
    this.token = null;
    await AsyncStorage.removeItem('auth_token');
  }

  private async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (this.token) {
        headers['Authorization'] = `Token ${this.token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || data.detail || 'Request failed',
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error('API Request Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  // Authentication
  async login(username: string, password: string) {
    return this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async register(username: string, email: string, password: string) {
    return this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
  }

  async logout() {
    await this.clearToken();
    return { success: true };
  }

  // Content Generation
  async generateContent(params: ContentGenerationRequest) {
    // Ensure we use 'content_type' parameter as backend expects
    const requestParams = {
      ...params,
      content_type: params.type || params.content_type
    };
    
    const response = await this.request('/content/create/', {
      method: 'POST',
      body: JSON.stringify(requestParams),
    });
    
    // Map backend response to expected frontend structure
    if (response.success && response.data) {
      if (response.data.type === 'text' && response.data.result) {
        response.data.text = response.data.result;
        response.data.content = response.data.result;
      }
      if (response.data.type === 'image' && response.data.result) {
        response.data.image_url = response.data.result;
      }
    }
    
    return response;
  }

  async generateBlog(params: BlogGenerationRequest) {
    const response = await this.request('/content/blog/generate/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
    
    // Map backend response to expected frontend structure
    if (response.success && response.data && response.data.blog_post) {
      return {
        success: true,
        data: response.data.blog_post
      };
    }
    
    return response;
  }

  async generateSocialMedia(params: SocialMediaRequest) {
    const response = await this.request('/content/social/generate/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
    
    // Map backend response to expected frontend structure
    if (response.success && response.data && response.data.social_posts) {
      return {
        success: true,
        data: response.data.social_posts
      };
    }
    
    return response;
  }

  async generateBatch(params: BatchGenerationRequest) {
    return this.request('/content/batch/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Image Operations
  async img2img(imageData: string, prompt: string, strength: number = 0.75) {
    return this.request('/content/img2img/', {
      method: 'POST',
      body: JSON.stringify({
        image: imageData,
        prompt,
        strength,
      }),
    });
  }

  async upscaleImage(imageData: string, scale: number = 2) {
    return this.request('/stability/upscale/', {
      method: 'POST',
      body: JSON.stringify({
        image: imageData,
        scale,
      }),
    });
  }

  async removeBackground(imageData: string) {
    return this.request('/stability/remove-background/', {
      method: 'POST',
      body: JSON.stringify({
        image: imageData,
      }),
    });
  }

  // Gallery & Content Management
  async getGallery(page: number = 1, limit: number = 20) {
    return this.request(`/content/?page=${page}&limit=${limit}`);
  }

  async getContent(id: string) {
    return this.request(`/content/${id}/`);
  }

  async deleteContent(id: string) {
    return this.request(`/content/${id}/`, {
      method: 'DELETE',
    });
  }

  async saveContent(content: any) {
    return this.request('/content/save/', {
      method: 'POST',
      body: JSON.stringify(content),
    });
  }

  // Video Generation
  async generateTextToVideo(params: {
    prompt: string;
    duration?: number;
    resolution?: string;
    quality?: string;
    style?: string;
    use_memory?: boolean;
    enhance_prompt?: boolean;
  }) {
    return this.request('/video/text-to-video/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async generateImageToVideo(params: {
    image_url?: string;
    image_id?: string;
    motion_prompt: string;
    duration?: number;
  }) {
    return this.request('/video/image-to-video/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getVideoStatus(taskId: string) {
    return this.request(`/video/status/${taskId}/`);
  }

  async getVideoGallery() {
    return this.request('/video/gallery/');
  }

  // Styles
  async getStyles() {
    return this.request('/styles/');
  }

  async getCustomStyles() {
    return this.request('/custom-styles/');
  }

  async createCustomStyle(style: any) {
    return this.request('/custom-styles/', {
      method: 'POST',
      body: JSON.stringify(style),
    });
  }

  // Video Generation
  async generateVideo(prompt: string, duration: number = 5) {
    return this.request('/video/text-to-video/', {
      method: 'POST',
      body: JSON.stringify({
        prompt,
        duration,
      }),
    });
  }

  // Voice Processing
  async transcribeVoice(audioData: string, format: string = 'webm') {
    return this.request('/voice/transcribe/', {
      method: 'POST',
      body: JSON.stringify({
        audio: audioData,
        format,
      }),
    });
  }

  async processVoiceCommand(command: string) {
    return this.request('/voice/command/', {
      method: 'POST',
      body: JSON.stringify({
        command,
      }),
    });
  }

  // Campaigns
  async getCampaigns() {
    return this.request('/campaigns/');
  }

  async createCampaign(campaign: any) {
    return this.request('/campaigns/', {
      method: 'POST',
      body: JSON.stringify(campaign),
    });
  }

  async getCampaignAnalytics(id: string) {
    return this.request(`/campaigns/${id}/analytics/`);
  }

  // AI Editing
  async editContent(contentId: string, instruction: string) {
    return this.request('/content/edit/', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        instruction,
      }),
    });
  }

  async getEditHistory(contentId: string) {
    return this.request(`/content/${contentId}/history/`);
  }

  // Memory System
  async searchMemory(query: string) {
    return this.request('/memory/search/', {
      method: 'POST',
      body: JSON.stringify({
        query,
      }),
    });
  }

  async saveMemory(content: string, tags: string[] = []) {
    return this.request('/memory/save/', {
      method: 'POST',
      body: JSON.stringify({
        content,
        tags,
      }),
    });
  }

  // Video Generation
  async generateTextToVideo(params: VideoGenerationRequest): Promise<ApiResponse<VideoResponse>> {
    return this.request('/video/text-to-video/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async generateImageToVideo(params: VideoGenerationRequest): Promise<ApiResponse<VideoResponse>> {
    return this.request('/video/image-to-video/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getVideoStatus(taskId: string): Promise<ApiResponse<VideoStatusResponse>> {
    return this.request(`/video/status/${taskId}/`);
  }

  async getVideoGallery(): Promise<ApiResponse<{ videos: Video[]; count: number }>> {
    return this.request('/video/gallery/');
  }

  async getVideoDetail(contentId: number): Promise<ApiResponse<{ video: Video }>> {
    return this.request(`/video/${contentId}/`);
  }

  // Gallery API
  async getGalleryImages(params?: {
    category?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<{ images: any[]; pagination: any }>> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append('category', params.category);
    if (params?.search) queryParams.append('search', params.search);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const endpoint = `/gallery/list/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.request(endpoint);
  }

  async saveImageToGallery(imageData: {
    title: string;
    image_url: string;
    original_prompt?: string;
    style_used?: string;
    category?: string;
    description?: string;
    tags?: string[];
    is_public?: boolean;
  }): Promise<ApiResponse<any>> {
    return this.request('/gallery/save/', {
      method: 'POST',
      body: JSON.stringify(imageData),
    });
  }
}

export const api = new ApiService();
export default api;