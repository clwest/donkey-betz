/**
 * Content Service
 * Handles all content generation operations
 */

import { BaseService } from './base.service';
import { apiHelpers } from '../api/client';
import { ENDPOINTS } from '../api/config';
import { 
  ContentItem, 
  ImageGenerationParams, 
  ImageGenerationResponse,
  BlogPost,
  BlogGenerationParams,
  SocialPost,
  SocialGenerationParams,
  VideoGenerationParams,
  VideoGenerationResponse,
  VoiceTranscriptionParams,
  VoiceTranscriptionResponse,
  StabilityOperation,
  StabilityResponse,
  PaginatedResponse
} from '../types/api.types';

class ContentService extends BaseService {
  constructor() {
    super(ENDPOINTS.CONTENT.CREATE);
  }

  /**
   * Generate images using Stable Diffusion
   */
  async generateImage(params: ImageGenerationParams): Promise<ImageGenerationResponse> {
    return this.post<ImageGenerationResponse>('', params);
  }

  /**
   * Batch generate images
   */
  async batchGenerate(params: ImageGenerationParams & { batch_size?: number }): Promise<ImageGenerationResponse> {
    return this.post<ImageGenerationResponse>(
      ENDPOINTS.CONTENT.BATCH.replace(ENDPOINTS.CONTENT.CREATE, ''),
      params
    );
  }

  /**
   * Generate blog post
   */
  async generateBlog(params: BlogGenerationParams): Promise<BlogPost> {
    return this.post<BlogPost>(
      ENDPOINTS.CONTENT.BLOG_GENERATE.replace(ENDPOINTS.CONTENT.CREATE, ''),
      params,
      { timeout: 90000 } // 90 seconds for blog generation
    );
  }

  /**
   * Generate social media posts
   */
  async generateSocialPosts(params: SocialGenerationParams & {
    platforms: string[];
    variations?: number;
    hashtags?: boolean;
    emojis?: boolean;
  }): Promise<SocialPost[]> {
    return this.post<SocialPost[]>(
      ENDPOINTS.CONTENT.SOCIAL_GENERATE.replace(ENDPOINTS.CONTENT.CREATE, ''),
      params,
      { timeout: 60000 } // 60 seconds for social generation
    );
  }

  /**
   * Generate text content
   */
  async generateText(params: {
    prompt: string;
    model?: string;
    max_tokens?: number;
    temperature?: number;
    type?: 'blog' | 'social' | 'email' | 'general';
    tone?: 'professional' | 'casual' | 'technical' | 'marketing';
  }): Promise<ContentItem> {
    return this.post<ContentItem>('/text/', params);
  }

  /**
   * Get content gallery
   */
  async getGallery(
    page: number = 1,
    limit: number = 20,
    filters?: {
      type?: string;
      date_from?: string;
      date_to?: string;
      tags?: string[];
    }
  ): Promise<PaginatedResponse<ContentItem>> {
    return this.getPaginated<ContentItem>(
      ENDPOINTS.CONTENT.GALLERY.replace(ENDPOINTS.CONTENT.CREATE, ''),
      page,
      limit,
      filters
    );
  }

  /**
   * Delete content item
   */
  async deleteContent(id: number): Promise<void> {
    return this.delete(`/${id}/`);
  }
}

class VideoService extends BaseService {
  constructor() {
    super(ENDPOINTS.VIDEO.TEXT_TO_VIDEO);
  }

  /**
   * Generate video from text
   */
  async textToVideo(params: VideoGenerationParams): Promise<VideoGenerationResponse> {
    return this.post<VideoGenerationResponse>('', params, {
      timeout: 120000 // 2 minutes for video generation
    });
  }

  /**
   * Generate video from image
   */
  async imageToVideo(params: VideoGenerationParams): Promise<VideoGenerationResponse> {
    return this.post<VideoGenerationResponse>(
      ENDPOINTS.VIDEO.IMAGE_TO_VIDEO.replace(ENDPOINTS.VIDEO.TEXT_TO_VIDEO, ''),
      params,
      { timeout: 120000 }
    );
  }

  /**
   * Check video generation status
   */
  async checkStatus(taskId: string): Promise<VideoGenerationResponse> {
    return this.get<VideoGenerationResponse>(
      `${ENDPOINTS.VIDEO.STATUS.replace(ENDPOINTS.VIDEO.TEXT_TO_VIDEO, '')}${taskId}/`
    );
  }

  /**
   * Cancel video generation
   */
  async cancelGeneration(taskId: string): Promise<void> {
    return this.delete(`/${taskId}/`);
  }
}

class VoiceService extends BaseService {
  constructor() {
    super(ENDPOINTS.VOICE.TRANSCRIBE);
  }

  /**
   * Transcribe audio file
   */
  async transcribeAudio(
    audioFile: File | any,
    outputType: 'transcript' | 'blog' | 'summary' = 'transcript'
  ): Promise<VoiceTranscriptionResponse> {
    const formData = apiHelpers.createFormData({
      audio: audioFile,
      output_type: outputType,
    });
    
    return this.post<VoiceTranscriptionResponse>('', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  /**
   * Format conversation from transcript
   */
  async formatConversation(
    transcriptId: string,
    speakers?: string[]
  ): Promise<any> {
    return this.post('/format-conversation/', {
      transcript_id: transcriptId,
      speakers,
    });
  }

  /**
   * Generate TTS audio
   */
  async textToSpeech(params: {
    text: string;
    voice?: string;
    language?: string;
    speed?: number;
  }): Promise<{ audio_url: string }> {
    return this.post<{ audio_url: string }>(
      ENDPOINTS.VOICE.TTS.replace(ENDPOINTS.VOICE.TRANSCRIBE, ''),
      params
    );
  }
}

class StabilityService extends BaseService {
  constructor() {
    super('/api/stability');
  }

  /**
   * Upscale image
   */
  async upscale(imageFile: File | any, scale?: number): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
      scale: scale || 2,
    });
    
    return this.post<StabilityResponse>(
      ENDPOINTS.STABILITY.UPSCALE.replace('/api/stability', ''),
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Inpaint image
   */
  async inpaint(
    imageFile: File | any,
    maskFile: File | any,
    prompt: string
  ): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
      mask: maskFile,
      prompt,
    });
    
    return this.post<StabilityResponse>(
      ENDPOINTS.STABILITY.INPAINT.replace('/api/stability', ''),
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Remove background from image
   */
  async removeBackground(imageFile: File | any): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
    });
    
    return this.post<StabilityResponse>(
      ENDPOINTS.STABILITY.REMOVE_BACKGROUND.replace('/api/stability', ''),
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Generate 3D model from image
   */
  async generate3D(imageFile: File | any): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
    });
    
    return this.post<StabilityResponse>(
      ENDPOINTS.STABILITY.THREE_D.replace('/api/stability', ''),
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Outpaint image
   */
  async outpaint(
    imageFile: File | any,
    prompt: string,
    direction: 'left' | 'right' | 'top' | 'bottom'
  ): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
      prompt,
      direction,
    });
    
    return this.post<StabilityResponse>(
      '/outpaint/',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Control-to-image generation
   */
  async controlToImage(
    controlImage: File | any,
    prompt: string,
    controlType: 'canny' | 'depth' | 'pose'
  ): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      control_image: controlImage,
      prompt,
      control_type: controlType,
    });
    
    return this.post<StabilityResponse>(
      '/control-to-image/',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Sketch-to-image generation
   */
  async sketchToImage(
    sketchFile: File | any,
    prompt: string
  ): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      sketch: sketchFile,
      prompt,
    });
    
    return this.post<StabilityResponse>(
      '/sketch-to-image/',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Replace object in image
   */
  async replaceObject(
    imageFile: File | any,
    maskFile: File | any,
    searchPrompt: string,
    replacePrompt: string
  ): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
      mask: maskFile,
      search_prompt: searchPrompt,
      replace_prompt: replacePrompt,
    });
    
    return this.post<StabilityResponse>(
      '/replace-object/',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Reimagine image with new style
   */
  async reimagine(
    imageFile: File | any,
    prompt?: string,
    strength?: number
  ): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
      prompt,
      strength: strength || 0.5,
    });
    
    return this.post<StabilityResponse>(
      '/reimagine/',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }

  /**
   * Erase object from image
   */
  async eraseObject(
    imageFile: File | any,
    maskFile: File | any
  ): Promise<StabilityResponse> {
    const formData = apiHelpers.createFormData({
      image: imageFile,
      mask: maskFile,
    });
    
    return this.post<StabilityResponse>(
      '/erase/',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  }
}

// Export service instances
export const contentService = new ContentService();
export const videoService = new VideoService();
export const voiceService = new VoiceService();
export const stabilityService = new StabilityService();

// Export classes for extension if needed
export { ContentService, VideoService, VoiceService, StabilityService };