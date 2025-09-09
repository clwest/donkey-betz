// Base Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  name?: string; // Derived from first_name + last_name
  is_premium: boolean;
  avatar?: string;
  date_joined: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// Auth Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name?: string;
}

// Content Types
export interface ContentItem {
  id: number;
  title: string;
  content: string;
  content_type: 'text' | 'image' | 'video' | 'audio';
  prompt?: string;
  style?: string;
  model?: string;
  created_at: string;
  updated_at: string;
  user: number;
  metadata?: Record<string, any>;
  file_url?: string;
  thumbnail_url?: string;
  is_favorite?: boolean;
  tags?: string[];
}

export interface ContentGenerationRequest {
  prompt: string;
  content_type: 'text' | 'image';
  style?: string;
  model?: string;
  parameters?: Record<string, any>;
  enhance_prompt?: boolean;
  use_memory?: boolean;
}

export interface BatchGenerationRequest {
  prompts: string[];
  style?: string;
  model?: string;
  parameters?: Record<string, any>;
  batch_size?: number;
}

// Blog Types
export interface BlogPost {
  id: number;
  title: string;
  content: string;
  excerpt: string;
  slug: string;
  meta_description: string;
  tags: string[];
  featured_image?: string;
  status: 'draft' | 'published' | 'archived';
  publish_date?: string;
  created_at: string;
  updated_at: string;
  user: number;
  word_count: number;
  reading_time: number;
  seo_score?: number;
}

export interface BlogGenerationRequest {
  topic: string;
  style?: string;
  tone?: string;
  target_audience?: string;
  word_count?: number;
  include_images?: boolean;
  seo_keywords?: string[];
  outline_only?: boolean;
}

// Social Media Types
export interface SocialPost {
  id: number;
  platform: string;
  content: string;
  hashtags: string[];
  images?: string[];
  scheduled_time?: string;
  status: 'draft' | 'scheduled' | 'published';
  engagement_score?: number;
  created_at: string;
  updated_at: string;
  user: number;
}

export interface SocialGenerationRequest {
  topic: string;
  platform: 'twitter' | 'facebook' | 'instagram' | 'linkedin' | 'tiktok';
  tone?: string;
  include_hashtags?: boolean;
  include_images?: boolean;
  max_length?: number;
}

// Gallery Types
export interface GalleryItem {
  id: number;
  title: string;
  file_url: string;
  thumbnail_url?: string;
  file_type: string;
  file_size: number;
  metadata?: Record<string, any>;
  tags?: string[];
  is_favorite: boolean;
  created_at: string;
  user: number;
  content_id?: number;
}

// Voice Types
export interface VoiceRecording {
  id: number;
  file_url: string;
  transcript?: string;
  duration: number;
  file_size: number;
  created_at: string;
  user: number;
  processed: boolean;
  speakers?: any[];
}

export interface TranscriptionRequest {
  audio_file: any;
  output_type?: 'summary' | 'blog' | 'social' | 'transcript';
  speaker_diarization?: boolean;
}

export interface TranscriptionResponse {
  id: number;
  transcript: string;
  speakers?: any[];
  summary?: string;
  generated_content?: any;
  confidence_score: number;
}

// Dashboard Types
export interface DashboardStats {
  total_content: number;
  total_content_trend: string;
  images_generated: number;
  images_trend: string;
  text_content: number;
  video_content: number;
  active_workflows: number;
  extended_content: {
    blogs: number;
    social_posts: number;
    campaigns: number;
    ebooks: number;
    podcasts: number;
    pitch_decks: number;
  };
  usage_period: string;
  // Keep legacy fields for backward compatibility
  total_images?: number;
  total_blogs?: number;
  total_social_posts?: number;
  total_videos?: number;
  storage_used?: number;
  api_calls_today?: number;
  api_calls_month?: number;
  premium_features_used?: number;
}

export interface ActivityItem {
  id: number;
  action: string;
  description: string;
  content_type?: string;
  content_id?: number;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ContentBreakdown {
  by_type: Record<string, number>;
  by_date: Record<string, number>;
  by_style: Record<string, number>;
  trends: {
    daily_growth: number;
    weekly_growth: number;
    monthly_growth: number;
  };
}

// Campaign Types
export interface Campaign {
  id: number;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  start_date?: string;
  end_date?: string;
  platforms: string[];
  target_audience: string;
  goals: string[];
  content_types: string[];
  created_at: string;
  updated_at: string;
  user: number;
  analytics?: CampaignAnalytics;
}

export interface CampaignAnalytics {
  total_content: number;
  total_reach: number;
  engagement_rate: number;
  click_through_rate: number;
  conversion_rate: number;
  roi: number;
}

// Video Types
export interface VideoContent {
  id: number;
  title: string;
  description: string;
  video_url?: string;
  thumbnail_url?: string;
  duration?: number;
  status: 'processing' | 'completed' | 'failed';
  task_id?: string;
  created_at: string;
  updated_at: string;
  user: number;
  metadata?: Record<string, any>;
}

export interface VideoGenerationRequest {
  type: 'text_to_video' | 'image_to_video';
  prompt?: string;
  image_url?: string;
  duration?: number;
  style?: string;
  aspect_ratio?: string;
}

// Style Memory Types
export interface StyleInteraction {
  content_id: number;
  rating: number;
  feedback?: string;
  style_elements?: string[];
}

export interface StyleSuggestion {
  style: string;
  confidence: number;
  reason: string;
  example_url?: string;
}

// Character Consistency Types
export interface CharacterProfile {
  id: number;
  name: string;
  description: string;
  appearance: string;
  style_elements: string[];
  reference_images: string[];
  created_at: string;
  user: number;
}

// Feedback Types
export interface FeedbackSubmission {
  content_type: string;
  content_id: number;
  rating: number;
  comment?: string;
  category: string;
  improvement_suggestions?: string[];
}

// Personal Knowledge Types
export interface KnowledgeDocument {
  id: string;
  title: string;
  content: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

// Error Types
export interface ValidationError {
  field: string;
  message: string;
}

export interface ApiError {
  error: string;
  details?: ValidationError[];
  code?: string;
}

// Filtering and Sorting
export interface ListFilters {
  content_type?: string;
  date_from?: string;
  date_to?: string;
  tags?: string[];
  is_favorite?: boolean;
  status?: string;
  search?: string;
}

export interface SortOptions {
  field: string;
  order: 'asc' | 'desc';
}

export interface ListParams extends ListFilters {
  page?: number;
  limit?: number;
  ordering?: string;
}