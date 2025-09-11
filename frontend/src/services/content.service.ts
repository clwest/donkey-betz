import { apiClient, createFormData } from './api.config';

// Content Generation Types
export interface ContentGenerationRequest {
  prompt: string;
  model?: string;
  max_tokens?: number;
  temperature?: number;
  type?: 'blog' | 'social' | 'email' | 'general';
  tone?: 'professional' | 'casual' | 'technical' | 'marketing';
  // GPT-5 specific parameters
  verbosity?: 'low' | 'medium' | 'high';
  reasoning_effort?: 'minimal' | 'standard' | 'maximum';
}

export interface ImageGenerationRequest {
  prompt: string;
  style?: string;
  cfg_scale?: number;
  steps?: number;
  width?: number;
  height?: number;
  model?: string;
  negative_prompt?: string;
  seed?: number;
  batch_size?: number;
}

export interface VideoGenerationRequest {
  type: 'text_to_video' | 'image_to_video';
  prompt?: string;
  image_url?: string;
  image_id?: string;
  motion_prompt?: string;
  duration?: 5 | 10;
  resolution?: '720p' | '1080p';
  quality?: 'gen3a_turbo' | 'gen3a';
  style?: string;
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

export interface StabilityEditRequest {
  image: File;
  operation: 'upscale' | 'inpaint' | 'outpaint' | 'remove_background' | 'search_replace' | 'erase';
  prompt?: string;
  mask?: File;
  creativity?: number;
  upscale_factor?: 2 | 4;
}

// Content Service
export const contentService = {
  // Text Generation
  async generateText(request: ContentGenerationRequest) {
    const { data } = await apiClient.post('/api/v1/content/create/', {
      content_type: 'text',
      ...request,
    });
    return data;
  },

  // Image Generation
  async generateImage(request: ImageGenerationRequest) {
    // Convert width/height to size format expected by backend
    const size = request.width && request.height 
      ? `${request.width}x${request.height}`
      : '1024x1024';
    
    const { data } = await apiClient.post('/api/v1/content/create/', {
      content_type: 'image',
      ...request,
      size,
    });
    return data;
  },

  // Batch Image Generation
  async generateImageBatch(request: ImageGenerationRequest & { variations: number }) {
    const { data } = await apiClient.post('/api/v1/content/batch/', request);
    return data;
  },

  // Image-to-Image
  async imageToImage(baseImage: File, request: Omit<ImageGenerationRequest, 'prompt'> & { prompt?: string }) {
    const formData = createFormData({
      image: baseImage,
      ...request,
    });
    
    const { data } = await apiClient.post('/api/v1/content/img2img/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Video Generation (Runway ML)
  async generateVideo(endpoint: string, formData: FormData) {
    const { data } = await apiClient.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Generate text-to-video
  async generateTextToVideo(request: VideoGenerationRequest): Promise<VideoResponse> {
    const { data } = await apiClient.post('/api/v1/video/text-to-video/', request);
    return data;
  },

  // Generate image-to-video
  async generateImageToVideo(request: VideoGenerationRequest): Promise<VideoResponse> {
    const { data } = await apiClient.post('/api/v1/video/image-to-video/', request);
    return data;
  },

  // Get video generation status
  async getVideoStatus(taskId: string): Promise<VideoStatusResponse> {
    const { data } = await apiClient.get(`/api/v1/video/status/${taskId}/`);
    return data;
  },


  // Get video detail
  async getVideoDetail(contentId: number): Promise<{ video: any }> {
    const { data } = await apiClient.get(`/api/v1/video/${contentId}/`);
    return data;
  },

  // Stability AI Features
  async upscaleImage(image: File, factor: 2 | 4 = 2, creativity: 'conservative' | 'creative' = 'conservative') {
    const formData = createFormData({
      image,
      upscale_factor: factor,
      creativity,
    });
    
    const { data } = await apiClient.post('/api/v1/stability/upscale/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async removeBackground(image: File) {
    const formData = createFormData({ image });
    
    const { data } = await apiClient.post('/api/v1/stability/remove-background/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async inpaintImage(image: File, mask: File, prompt: string) {
    const formData = createFormData({
      image,
      mask,
      prompt,
    });
    
    const { data } = await apiClient.post('/api/v1/stability/inpaint/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async outpaintImage(image: File, direction: 'up' | 'down' | 'left' | 'right' | 'all', prompt?: string) {
    const formData = createFormData({
      image,
      direction,
      prompt,
    });
    
    const { data } = await apiClient.post('/api/v1/stability/outpaint/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async searchAndReplace(image: File, searchPrompt: string, replacePrompt: string) {
    const formData = createFormData({
      image,
      search_prompt: searchPrompt,
      replace_prompt: replacePrompt,
    });
    
    const { data } = await apiClient.post('/api/v1/stability/search-replace/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async eraseObject(image: File, mask: File) {
    const formData = createFormData({
      image,
      mask,
    });
    
    const { data } = await apiClient.post('/api/v1/stability/erase/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async sketchToImage(image: File, prompt: string) {
    const formData = createFormData({
      sketch: image,  // Backend expects 'sketch' key, not 'image'
      prompt,
    });
    
    const { data } = await apiClient.post('/api/v1/stability/sketch/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async generate3D(image: File) {
    const formData = createFormData({ image });
    
    const { data } = await apiClient.post('/api/v1/stability/3d/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Voice Studio
  async transcribeAudio(audioFile: File, outputType = 'transcript') {
    const formData = createFormData({
      audio: audioFile,
      output_type: outputType,  // Backend expects output_type, not format
    });
    
    const { data } = await apiClient.post('/api/v1/voice/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async formatConversation(transcriptId: string, speakers?: string[]) {
    const { data } = await apiClient.post('/api/v1/voice/format-conversation/', {
      transcript_id: transcriptId,
      speakers,
    });
    return data;
  },

  // Blog Generation
  async generateBlog(request: {
    topic: string;
    tone?: string;
    length?: 'short' | 'medium' | 'long';
    outline_mode?: boolean;
    target_audience?: string;
    keywords?: string[];
  }) {
    const { data } = await apiClient.post('/api/v1/content/blog/generate/', request, {
      timeout: 90000, // 90 seconds for blog generation
    });
    return data;
  },

  // Social Media Generation
  async generateSocialPosts(request: {
    topic: string;
    platforms: string[];
    tone?: string;
    variations?: number;
    hashtags?: boolean;
  }) {
    const { data } = await apiClient.post('/api/v1/content/social/generate/', request, {
      timeout: 90000, // 90 seconds for social generation
    });
    return data;
  },

  // Get saved social media posts
  async getSocialPostsList() {
    const { data } = await apiClient.get('/api/v1/content/social/list/');
    return data;
  },

  // Get specific social post details
  async getSocialPost(id: number) {
    const { data } = await apiClient.get(`/api/v1/content/social/${id}/`);
    return data;
  },

  // Custom Styles
  async getStyles() {
    const { data } = await apiClient.get('/api/v1/styles/');
    return data;
  },

  async getCustomStyles() {
    const { data } = await apiClient.get('/api/v1/custom-styles/');
    return data;
  },

  async createCustomStyle(style: {
    name: string;
    description: string;
    prompt_additions: string;
    negative_prompts?: string;
    cfg_scale?: number;
    steps?: number;
    is_public?: boolean;
  }) {
    const { data } = await apiClient.post('/api/v1/custom-styles/', style);
    return data;
  },

  // Gallery
  async getGalleryItems(limit = 50, content_type?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (content_type) params.append('content_type', content_type);
    
    const { data } = await apiClient.get(`/api/v1/gallery/?${params}`);
    return data;
  },

  async saveToGallery(contentId: string, title?: string, tags?: string[]) {
    const { data } = await apiClient.post('/api/v1/gallery/save/', {
      content_id: contentId,
      title,
      tags,
    });
    return data;
  },

  async saveImageToGallery(params: {
    image_url: string;
    title?: string;
    description?: string;
    category?: string;
    tags?: string[];
    original_prompt?: string;
    style_used?: string;
    is_public?: boolean;
  }) {
    const { data } = await apiClient.post('/api/v1/gallery/save/', params);
    return data;
  },

  async saveVideoToGallery(params: {
    video_url: string;
    title?: string;
    description?: string;
    category?: string;
    tags?: string[];
    original_prompt?: string;
    motion_prompt?: string;
    duration?: number;
    source_type?: 'text_to_video' | 'image_to_video';
    thumbnail_url?: string;
    metadata?: Record<string, any>;
    is_public?: boolean;
  }) {
    const { data } = await apiClient.post('/api/v1/gallery/save-video/', params);
    return data;
  },

  async getVideoGallery(params?: {
    category?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.append('category', params.category);
    if (params?.search) queryParams.append('search', params.search);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    
    const { data } = await apiClient.get(`/gallery/videos/?${queryParams}`);
    return data;
  },

  // Podcast Methods
  async createPodcast(podcastData: {
    show_name: string;
    episode_number: number;
    title: string;
    format: string;
    tone: string;
    target_duration: number;
    topic: string;
    description: string;
    keywords: string[];
  }) {
    const { data } = await apiClient.post('/api/v1/podcasts/', podcastData);
    return data;
  },

  async generatePodcast(podcastData: {
    topic: string;
    title?: string;
    format?: string;
    tone?: string;
    duration?: number;
    enhance_prompt?: boolean;
    use_memory?: boolean;
  }) {
    const { data } = await apiClient.post('/api/v1/podcasts/generate/', podcastData);
    return data;
  },

  async generatePodcastScript(episodeId: number) {
    const { data } = await apiClient.post(`/api/v1/podcasts/${episodeId}/generate-full/`);
    return data;
  },

  async getPodcastList() {
    const { data } = await apiClient.get('/api/v1/podcasts/');
    return data;
  },

  // Save blog posts to content library
  async saveBlogPost(blogData: {
    title: string;
    content: string;
    meta_description?: string;
    tags?: string[];
    is_live?: boolean;
  }) {
    // Default to draft status if not specified
    const dataToSave = {
      ...blogData,
      is_live: blogData.is_live ?? false
    };
    const { data } = await apiClient.post('/api/v1/content/blog/save/', dataToSave);
    return data;
  },

  // Get saved blog posts
  async getBlogList() {
    const { data } = await apiClient.get('/api/v1/content/blog/list/');
    return data;
  },

  // Get specific blog post
  async getBlogPost(id: number) {
    const { data } = await apiClient.get(`/api/v1/content/blog/${id}/`);
    return data;
  },

  // Update blog post
  async updateBlogPost(id: number, blogData: {
    title: string;
    content: string;
    meta_description?: string;
    tags?: string[];
    is_live?: boolean;
    is_deleted?: boolean;
  }) {
    const { data } = await apiClient.put(`/api/v1/content/blog/${id}/`, blogData);
    return data;
  },

  // Submit blog feedback
  async submitBlogFeedback(id: number, feedbackData: {
    rating: number;
    comments?: string;
    helpful?: boolean;
    feedback_type?: string;
  }) {
    const { data } = await apiClient.post(`/api/v1/content/blog/${id}/feedback/`, feedbackData);
    return data;
  },

  // Delete blog post (mark as deleted using PUT since DELETE is not supported)
  async deleteBlogPost(id: number) {
    // Get the current blog data first
    const response = await this.getBlogPost(id);
    const currentBlog = response.blog_post || response;
    
    // Mark as deleted and unpublished using PUT
    const { data } = await apiClient.put(`/api/v1/content/blog/${id}/`, {
      title: currentBlog.title,
      content: currentBlog.content,
      meta_description: currentBlog.meta_description,
      tags: currentBlog.tags,
      is_live: false,
      is_deleted: true  // Mark as deleted
    });
    return data;
  },

  // Toggle blog live status
  async toggleBlogLiveStatus(id: number, isLive: boolean) {
    // Get the current blog data first
    const response = await this.getBlogPost(id);
    const currentBlog = response.blog_post || response;
    
    // Update with the new is_live status using PUT with all required fields
    const { data } = await apiClient.put(`/api/v1/content/blog/${id}/`, {
      title: currentBlog.title,
      content: currentBlog.content,
      meta_description: currentBlog.meta_description,
      tags: currentBlog.tags,
      is_live: isLive
    });
    return data;
  },

  // Export
  async exportContent(contentId: string, format: 'png' | 'jpg' | 'pdf' | 'docx') {
    const { data } = await apiClient.post(`/api/v1/export/${contentId}/`, {
      format,
    }, {
      responseType: 'blob',
    });
    return data;
  },

  // Content Transformation Methods
  async generateSocialFromBlog(request: {
    blogContent: string;
    topic: string;
    tone: string;
    platforms: string[];
  }) {
    const { data } = await apiClient.post('/api/v1/content/social/generate/', {
      topic: request.topic,
      platforms: request.platforms,
      tone: request.tone,
      target_audience: `Readers interested in: ${request.topic}`,
      call_to_action: 'Share your thoughts in the comments',
      include_hashtags: true,
      variations_per_platform: 2,
      use_memory: true,
      enhance_prompt: true
    });
    return data;
  },

  async generatePodcastFromBlog(request: {
    blogContent: string;
    title: string;
    tone: string;
    duration: string;
  }) {
    const { data } = await apiClient.post('/api/v1/podcasts/generate/', {
      topic: request.title,
      title: `Podcast: ${request.title}`,
      format: 'interview',
      tone: request.tone,
      duration: request.duration === 'medium' ? 15 : 30,
      enhance_prompt: true,
      use_memory: true
    }, {
      timeout: 120000, // 2 minutes timeout for podcast generation
    });
    return data;
  },

  async generateEbookFromBlog(request: {
    blogContent: string;
    title: string;
    tone: string;
    targetWordCount: number;
  }) {
    const { data } = await apiClient.post('/api/v1/ebooks/', {
      title: `${request.title} - eBook`,
      description: `Comprehensive eBook expanded from: ${request.title}`,
      genre: 'business',
      target_audience: 'professional',
      author: 'AI Content Studio',
      chapter_count: 3,
      words_per_chapter: Math.floor(request.targetWordCount / 3),
      tone: request.tone
    });
    return data;
  },
};