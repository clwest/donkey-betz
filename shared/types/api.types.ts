/**
 * Shared TypeScript Types for API
 * Common types used across both platforms
 */

// Base response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T = any> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
  page: number;
  total_pages: number;
}

// User and Auth types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  avatar?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access: string;
  refresh?: string;
}

export interface LoginResponse {
  user: User;
  token: string;
  tokens?: AuthTokens;
}

// Content types
export interface ContentItem {
  id: number;
  title?: string;
  content?: string;
  type: 'text' | 'image' | 'video' | 'audio';
  media_url?: string;
  thumbnail_url?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  user?: number;
  tags?: string[];
  status?: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface ImageGenerationParams {
  prompt: string;
  negative_prompt?: string;
  style?: string;
  model?: string;
  width?: number;
  height?: number;
  steps?: number;
  cfg_scale?: number;
  seed?: number;
  batch_size?: number;
  variations?: boolean;
}

export interface ImageGenerationResponse {
  id: number;
  images: Array<{
    id: number;
    url: string;
    thumbnail_url?: string;
    metadata?: Record<string, any>;
  }>;
  prompt: string;
  style?: string;
  created_at: string;
}

// Blog types
export interface BlogPost {
  id: number;
  title: string;
  content: string;
  summary?: string;
  slug?: string;
  author?: User;
  featured_image?: string;
  tags?: string[];
  categories?: string[];
  status: 'draft' | 'published' | 'archived';
  published_at?: string;
  created_at: string;
  updated_at: string;
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string[];
}

export interface BlogGenerationParams {
  topic: string;
  tone?: string;
  length?: 'short' | 'medium' | 'long';
  keywords?: string[];
  target_audience?: string;
  include_images?: boolean;
  seo_optimized?: boolean;
}

// Social Media types
export interface SocialPost {
  id: number;
  platform: 'twitter' | 'facebook' | 'instagram' | 'linkedin' | 'tiktok';
  content: string;
  media?: string[];
  hashtags?: string[];
  scheduled_at?: string;
  published_at?: string;
  status: 'draft' | 'scheduled' | 'published';
  engagement?: {
    likes: number;
    shares: number;
    comments: number;
  };
  created_at: string;
  updated_at: string;
}

export interface SocialGenerationParams {
  platform: string;
  topic: string;
  tone?: string;
  include_hashtags?: boolean;
  include_emojis?: boolean;
  character_limit?: number;
}

// Video types
export interface VideoGenerationParams {
  prompt?: string;
  image_url?: string;
  duration?: number;
  fps?: number;
  resolution?: string;
  style?: string;
  motion_intensity?: number;
}

export interface VideoGenerationResponse {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  video_url?: string;
  thumbnail_url?: string;
  created_at: string;
  estimated_completion?: string;
  progress?: number;
  error?: string;
}

// Voice types
export interface VoiceTranscriptionParams {
  audio_file?: File | any;
  audio_url?: string;
  language?: string;
  speaker_diarization?: boolean;
  format?: 'text' | 'srt' | 'vtt';
}

export interface VoiceTranscriptionResponse {
  id: number;
  text: string;
  segments?: Array<{
    start: number;
    end: number;
    text: string;
    speaker?: string;
  }>;
  language?: string;
  duration?: number;
  created_at: string;
}

export interface TTSParams {
  text: string;
  voice?: string;
  language?: string;
  speed?: number;
  pitch?: number;
}

// Style Memory types
export interface StyleMemoryEntry {
  id: number;
  image_id: number;
  style_attributes: Record<string, any>;
  rating: number;
  learned_at: string;
  user_feedback?: string;
}

export interface StyleSuggestion {
  style: string;
  confidence: number;
  reason: string;
  examples?: string[];
}

// Dashboard types
export interface DashboardStats {
  total_content: number;
  content_by_type: Record<string, number>;
  recent_activity: Array<{
    action: string;
    timestamp: string;
    details?: any;
  }>;
  usage_metrics: {
    api_calls: number;
    storage_used: number;
    credits_remaining?: number;
  };
  popular_styles?: string[];
  trending_topics?: string[];
}

// Campaign types
export interface Campaign {
  id: number;
  name: string;
  description?: string;
  type: 'social' | 'email' | 'blog' | 'multi-channel';
  status: 'draft' | 'active' | 'paused' | 'completed';
  start_date?: string;
  end_date?: string;
  targets?: Record<string, any>;
  content?: ContentItem[];
  analytics?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Workflow types
export interface Workflow {
  id: number;
  name: string;
  description?: string;
  steps: WorkflowStep[];
  triggers?: WorkflowTrigger[];
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
}

export interface WorkflowStep {
  id: string;
  type: string;
  config: Record<string, any>;
  next_steps?: string[];
}

export interface WorkflowTrigger {
  type: 'schedule' | 'webhook' | 'event';
  config: Record<string, any>;
}

// Feedback types
export interface Feedback {
  id: number;
  content_id: number;
  rating: number;
  comment?: string;
  tags?: string[];
  created_at: string;
  user?: User;
}

// Error types
export interface ApiError {
  message: string;
  code: string;
  details?: any;
  field_errors?: Record<string, string[]>;
}

// Gallery types
export interface GalleryItem extends ContentItem {
  downloads?: number;
  views?: number;
  likes?: number;
  is_public?: boolean;
  collections?: string[];
}

export interface GalleryFilters {
  type?: string;
  date_from?: string;
  date_to?: string;
  tags?: string[];
  search?: string;
  sort_by?: 'created' | 'updated' | 'likes' | 'views';
  order?: 'asc' | 'desc';
}

// Stability AI types
export interface StabilityOperation {
  operation: 'upscale' | 'inpaint' | 'remove-background' | '3d' | 'outpaint';
  image_url?: string;
  image_file?: File | any;
  mask_url?: string;
  mask_file?: File | any;
  params?: Record<string, any>;
}

export interface StabilityResponse {
  id: number;
  operation: string;
  result_url: string;
  original_url?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

// Character types
export interface Character {
  id: number;
  name: string;
  description?: string;
  personality?: string;
  avatar?: string;
  voice?: string;
  backstory?: string;
  traits?: string[];
  created_at: string;
  updated_at: string;
}

// Research/eBook types
export interface ResearchBook {
  id: number;
  title: string;
  author?: string;
  description?: string;
  chapters: Chapter[];
  cover_image?: string;
  status: 'draft' | 'in-progress' | 'completed' | 'published';
  word_count?: number;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface Chapter {
  id: number;
  title: string;
  content: string;
  order: number;
  word_count?: number;
  status: 'draft' | 'completed';
  created_at: string;
  updated_at: string;
}

// Prompting types
export interface PromptEnhancement {
  original_prompt: string;
  enhanced_prompt: string;
  level: 'basic' | 'advanced' | 'expert';
  improvements?: string[];
  suggestions?: string[];
}

export interface PromptTemplate {
  id: number;
  name: string;
  category: string;
  template: string;
  variables?: string[];
  examples?: string[];
  created_at: string;
}

// Export all types
export * from './api.types';