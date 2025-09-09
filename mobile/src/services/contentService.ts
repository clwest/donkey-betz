import { apiClient } from './apiClient';
import { 
  ContentItem, 
  ContentGenerationRequest, 
  BatchGenerationRequest, 
  PaginatedResponse,
  ListParams,
  BlogPost,
  BlogGenerationRequest,
  SocialPost,
  SocialGenerationRequest 
} from '../types/api';

class ContentService {
  // Generate single content item
  async generateContent(request: ContentGenerationRequest): Promise<ContentItem> {
    return await apiClient.post('/content/create/', request);
  }

  // Batch generate images
  async batchGenerate(request: BatchGenerationRequest): Promise<ContentItem[]> {
    return await apiClient.post('/content/batch/', request);
  }

  // Quick batch generation
  async quickBatchGenerate(prompts: string[], style?: string): Promise<ContentItem[]> {
    return await apiClient.post('/content/batch/quick/', {
      prompts,
      style,
    });
  }

  // List content with pagination and filters
  async listContent(params?: ListParams): Promise<PaginatedResponse<ContentItem>> {
    return await apiClient.get('/content/list/', { params });
  }

  // Get single content item
  async getContent(id: number): Promise<ContentItem> {
    return await apiClient.get(`/content/${id}/`);
  }

  // Delete content
  async deleteContent(id: number): Promise<void> {
    await apiClient.delete(`/content/${id}/`);
  }

  // Bulk delete content
  async bulkDeleteContent(ids: number[]): Promise<void> {
    await apiClient.post('/content/bulk-delete/', { ids });
  }

  // Create variation of existing content
  async createVariation(contentId: number, variations: Partial<ContentGenerationRequest>): Promise<ContentItem> {
    return await apiClient.post(`/content/${contentId}/create-variation/`, variations);
  }

  // Save content to gallery
  async saveToGallery(contentId: number): Promise<void> {
    await apiClient.post(`/content/${contentId}/save-to-gallery/`);
  }

  // Batch save to gallery
  async batchSaveToGallery(contentIds: number[]): Promise<void> {
    await apiClient.post('/content/batch-save-to-gallery/', { content_ids: contentIds });
  }

  // Get unified image history
  async getImageHistory(params?: ListParams): Promise<PaginatedResponse<ContentItem>> {
    return await apiClient.get('/images/history/', { params });
  }

  // Image editing operations
  async imageToImage(imageFile: any, prompt: string, strength?: number): Promise<ContentItem> {
    return await apiClient.uploadFile('/content/img2img/', imageFile, 'image', {
      prompt,
      strength: strength || 0.8,
    });
  }

  async createImageVariations(imageFile: any, count?: number): Promise<ContentItem[]> {
    return await apiClient.uploadFile('/content/variations/', imageFile, 'image', {
      count: count || 4,
    });
  }

  // === BLOG GENERATION ===
  
  // Generate blog post
  async generateBlog(request: BlogGenerationRequest): Promise<BlogPost> {
    return await apiClient.post('/content/blog/generate/', request);
  }

  // Generate blog outline only
  async generateBlogOutline(topic: string, options?: Partial<BlogGenerationRequest>): Promise<{ outline: string }> {
    return await apiClient.post('/content/blog/outline/', { topic, ...options });
  }

  // Get blog templates
  async getBlogTemplates(): Promise<any[]> {
    return await apiClient.get('/content/blog/templates/');
  }

  // Save blog post
  async saveBlogPost(blogData: Partial<BlogPost>): Promise<BlogPost> {
    return await apiClient.post('/content/blog/save/', blogData);
  }

  // List user blog posts
  async listBlogPosts(params?: ListParams): Promise<PaginatedResponse<BlogPost>> {
    return await apiClient.get('/content/blog/list/', { params });
  }

  // Get blog post detail
  async getBlogPost(id: number): Promise<BlogPost> {
    return await apiClient.get(`/content/blog/${id}/`);
  }

  // Update blog post
  async updateBlogPost(id: number, updates: Partial<BlogPost>): Promise<BlogPost> {
    return await apiClient.put(`/content/blog/${id}/update/`, updates);
  }

  // Delete blog post
  async deleteBlogPost(id: number): Promise<void> {
    await apiClient.delete(`/content/blog/${id}/delete/`);
  }

  // Submit blog feedback
  async submitBlogFeedback(postId: number, feedback: any): Promise<void> {
    await apiClient.post(`/content/blog/${postId}/feedback/`, feedback);
  }

  // === SOCIAL MEDIA GENERATION ===

  // Generate social media post
  async generateSocialPost(request: SocialGenerationRequest): Promise<SocialPost> {
    return await apiClient.post('/content/social/generate/', request);
  }

  // Get available social platforms
  async getSocialPlatforms(): Promise<string[]> {
    return await apiClient.get('/content/social/platforms/');
  }

  // Generate hashtags
  async generateHashtags(topic: string, platform?: string, count?: number): Promise<string[]> {
    return await apiClient.post('/content/social/hashtags/', { topic, platform, count });
  }

  // Get social templates
  async getSocialTemplates(): Promise<any[]> {
    return await apiClient.get('/content/social/templates/');
  }

  // Save social post
  async saveSocialPost(postData: Partial<SocialPost>): Promise<SocialPost> {
    return await apiClient.post('/content/social/save/', postData);
  }

  // List social posts
  async listSocialPosts(params?: ListParams): Promise<PaginatedResponse<SocialPost>> {
    return await apiClient.get('/content/social/list/', { params });
  }

  // Get social post detail
  async getSocialPost(id: number): Promise<SocialPost> {
    return await apiClient.get(`/content/social/${id}/`);
  }

  // Update social post
  async updateSocialPost(id: number, updates: Partial<SocialPost>): Promise<SocialPost> {
    return await apiClient.put(`/content/social/${id}/update/`, updates);
  }

  // Delete social post
  async deleteSocialPost(id: number): Promise<void> {
    await apiClient.delete(`/content/social/${id}/delete/`);
  }

  // === CONTENT LIBRARY ===

  // Get content library
  async getContentLibrary(params?: ListParams): Promise<PaginatedResponse<ContentItem>> {
    return await apiClient.get('/content/library/', { params });
  }

  // Get content detail
  async getContentDetail(id: number): Promise<ContentItem> {
    return await apiClient.get(`/content/library/${id}/`);
  }

  // Star/unstar content
  async starContent(id: number, starred: boolean = true): Promise<void> {
    await apiClient.post(`/content/library/${id}/star/`, { starred });
  }

  // Duplicate content
  async duplicateContent(id: number): Promise<ContentItem> {
    return await apiClient.post(`/content/library/${id}/duplicate/`);
  }

  // Export content
  async exportContent(id: number, format: string): Promise<Blob> {
    return await apiClient.get(`/content/${id}/export/`, { 
      params: { format },
      responseType: 'blob' 
    });
  }

  // Get export formats
  async getExportFormats(id: number): Promise<string[]> {
    return await apiClient.get(`/content/${id}/export-formats/`);
  }

  // Bulk export
  async bulkExport(ids: number[], format: string): Promise<Blob> {
    return await apiClient.post('/content/bulk-export/', { ids, format }, {
      responseType: 'blob'
    });
  }

  // Bulk operations
  async bulkOperation(operation: string, ids: number[], data?: any): Promise<any> {
    return await apiClient.post('/content/bulk-operation/', {
      operation,
      ids,
      data,
    });
  }

  // Get content stats
  async getContentStats(): Promise<any> {
    return await apiClient.get('/content/stats/');
  }

  // Get content projects
  async getContentProjects(): Promise<any[]> {
    return await apiClient.get('/content/projects/');
  }
}

export const contentService = new ContentService();
export default contentService;