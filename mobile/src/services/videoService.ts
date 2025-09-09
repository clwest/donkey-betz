import { apiClient } from './apiClient';
import { VideoContent, VideoGenerationRequest, PaginatedResponse, ListParams } from '../types/api';

class VideoService {
  // === VIDEO GENERATION (RUNWAY ML) ===

  // Generate text-to-video
  async textToVideo(request: {
    prompt: string;
    duration?: number;
    aspect_ratio?: '16:9' | '9:16' | '1:1';
    style?: string;
    camera_movement?: string;
    seed?: number;
  }): Promise<{
    task_id: string;
    status: string;
    estimated_time: number;
  }> {
    return await apiClient.post('/video/text-to-video/', request);
  }

  // Generate image-to-video
  async imageToVideo(request: {
    image_url?: string;
    image_file?: any;
    prompt?: string;
    duration?: number;
    camera_movement?: string;
    seed?: number;
  }): Promise<{
    task_id: string;
    status: string;
    estimated_time: number;
  }> {
    if (request.image_file) {
      return await apiClient.uploadFile(
        '/video/image-to-video/',
        request.image_file,
        'image',
        {
          prompt: request.prompt,
          duration: request.duration,
          camera_movement: request.camera_movement,
          seed: request.seed,
        }
      );
    } else {
      return await apiClient.post('/video/image-to-video/', request);
    }
  }

  // Check video generation status
  async checkVideoStatus(taskId: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress: number;
    video_url?: string;
    thumbnail_url?: string;
    duration?: number;
    error?: string;
    estimated_remaining: number;
  }> {
    return await apiClient.get(`/video/status/${taskId}/`);
  }

  // Get video detail
  async getVideoDetail(contentId: number): Promise<VideoContent> {
    return await apiClient.get(`/video/${contentId}/`);
  }

  // List video gallery
  async getVideoGallery(params?: ListParams): Promise<PaginatedResponse<VideoContent>> {
    return await apiClient.get('/video/gallery/', { params });
  }

  // === ENHANCED VIDEO GENERATION WITH NARRATION ===

  // Generate video with narration
  async generateVideoWithNarration(request: {
    video_prompt: string;
    narration_script: string;
    voice_id: string;
    video_options?: {
      duration?: number;
      aspect_ratio?: string;
      style?: string;
    };
    narration_options?: {
      stability?: number;
      similarity_boost?: number;
      background_music?: boolean;
    };
  }): Promise<{
    task_id: string;
    video_task_id: string;
    narration_task_id: string;
    estimated_time: number;
  }> {
    return await apiClient.post('/video/generate-with-narration/', request);
  }

  // Add narration to existing video
  async addNarrationToVideo(request: {
    video_id: number;
    narration_script: string;
    voice_id: string;
    sync_options?: {
      auto_sync?: boolean;
      manual_timings?: { text: string; start_time: number }[];
    };
    audio_options?: {
      background_music_volume?: number;
      narration_volume?: number;
      fade_in_out?: boolean;
    };
  }): Promise<{
    task_id: string;
    estimated_time: number;
  }> {
    return await apiClient.post('/video/add-narration/', request);
  }

  // Get narration voices for video
  async getNarrationVoices(): Promise<{
    id: string;
    name: string;
    description: string;
    category: string;
    preview_url?: string;
    suitable_for: string[];
  }[]> {
    return await apiClient.get('/video/narration-voices/');
  }

  // Check enhanced video status (video + narration)
  async checkEnhancedVideoStatus(taskId: string): Promise<{
    status: 'pending' | 'processing_video' | 'processing_narration' | 'combining' | 'completed' | 'failed';
    progress: number;
    video_progress: number;
    narration_progress: number;
    final_video_url?: string;
    video_only_url?: string;
    narration_only_url?: string;
    error?: string;
    estimated_remaining: number;
  }> {
    return await apiClient.get(`/video/enhanced-status/${taskId}/`);
  }

  // === VIDEO MANAGEMENT ===

  // Update video metadata
  async updateVideo(id: number, updates: {
    title?: string;
    description?: string;
    tags?: string[];
    thumbnail_url?: string;
  }): Promise<VideoContent> {
    return await apiClient.patch(`/video/${id}/`, updates);
  }

  // Delete video
  async deleteVideo(id: number): Promise<void> {
    await apiClient.delete(`/video/${id}/`);
  }

  // === VIDEO PROCESSING ===

  // Extract thumbnail from video
  async extractThumbnail(videoId: number, timestamp?: number): Promise<{
    thumbnail_url: string;
  }> {
    return await apiClient.post(`/video/${videoId}/extract-thumbnail/`, {
      timestamp: timestamp || 0
    });
  }

  // Get video analytics
  async getVideoAnalytics(videoId: number): Promise<{
    duration: number;
    file_size: number;
    resolution: string;
    bitrate: number;
    frame_rate: number;
    codec: string;
    audio_info?: {
      channels: number;
      sample_rate: number;
      duration: number;
    };
  }> {
    return await apiClient.get(`/video/${videoId}/analytics/`);
  }

  // === BATCH VIDEO OPERATIONS ===

  // Batch generate videos
  async batchGenerateVideos(requests: {
    prompt: string;
    type: 'text_to_video' | 'image_to_video';
    image_url?: string;
    options?: any;
  }[]): Promise<{
    batch_id: string;
    task_ids: string[];
    estimated_total_time: number;
  }> {
    return await apiClient.post('/video/batch-generate/', { requests });
  }

  // Check batch status
  async checkBatchStatus(batchId: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed';
    completed_count: number;
    total_count: number;
    failed_count: number;
    results: {
      task_id: string;
      status: string;
      video_url?: string;
      error?: string;
    }[];
  }> {
    return await apiClient.get(`/video/batch-status/${batchId}/`);
  }

  // === VIDEO EXPORT AND SHARING ===

  // Export video in different formats
  async exportVideo(videoId: number, format: 'mp4' | 'mov' | 'avi' | 'gif', quality?: 'low' | 'medium' | 'high'): Promise<{
    export_url: string;
    file_size: number;
    format: string;
    expires_at: string;
  }> {
    return await apiClient.post(`/video/${videoId}/export/`, {
      format,
      quality: quality || 'medium'
    });
  }

  // Generate shareable link
  async generateShareableLink(videoId: number, options?: {
    expires_in?: number;
    password?: string;
    download_allowed?: boolean;
  }): Promise<{
    share_url: string;
    expires_at?: string;
    share_id: string;
  }> {
    return await apiClient.post(`/video/${videoId}/share/`, options);
  }

  // Download video
  async downloadVideo(videoId: number): Promise<Blob> {
    return await apiClient.get(`/video/${videoId}/download/`, {
      responseType: 'blob'
    });
  }

  // === VIDEO TEMPLATES AND PRESETS ===

  // Get video templates
  async getVideoTemplates(): Promise<{
    id: string;
    name: string;
    description: string;
    thumbnail: string;
    category: string;
    duration: number;
    aspect_ratio: string;
    style: string;
  }[]> {
    return await apiClient.get('/video/templates/');
  }

  // Create video from template
  async createVideoFromTemplate(templateId: string, customizations: {
    prompt?: string;
    duration?: number;
    style_modifications?: Record<string, any>;
  }): Promise<{
    task_id: string;
    estimated_time: number;
  }> {
    return await apiClient.post('/video/from-template/', {
      template_id: templateId,
      ...customizations
    });
  }
}

export const videoService = new VideoService();
export default videoService;