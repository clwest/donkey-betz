import { apiClient } from './apiClient';
import { GalleryItem, PaginatedResponse, ListParams, VideoContent } from '../types/api';

class GalleryService {
  // === IMAGE GALLERY ===

  // Save image to gallery
  async saveImage(imageData: {
    title: string;
    file_url: string;
    tags?: string[];
    metadata?: Record<string, any>;
  }): Promise<GalleryItem> {
    return await apiClient.post('/gallery/save/', imageData);
  }

  // Upload and save image file
  async uploadImage(
    imageFile: any, 
    title: string, 
    tags?: string[],
    onProgress?: (progress: number) => void
  ): Promise<GalleryItem> {
    return await apiClient.uploadFile(
      '/gallery/save/',
      imageFile,
      'image',
      { title, tags: tags?.join(',') || '' },
      onProgress
    );
  }

  // List gallery items
  async listGalleryItems(params?: ListParams): Promise<PaginatedResponse<GalleryItem>> {
    return await apiClient.get('/gallery/list/', { params });
  }

  // Get single gallery item
  async getGalleryItem(id: number): Promise<GalleryItem> {
    return await apiClient.get(`/gallery/${id}/`);
  }

  // Update gallery item
  async updateGalleryItem(id: number, updates: Partial<GalleryItem>): Promise<GalleryItem> {
    return await apiClient.patch(`/gallery/${id}/`, updates);
  }

  // Delete gallery item
  async deleteGalleryItem(id: number): Promise<void> {
    await apiClient.delete(`/gallery/${id}/`);
  }

  // Like/unlike image
  async likeImage(id: number, liked: boolean = true): Promise<void> {
    await apiClient.post(`/gallery/${id}/like/`, { liked });
  }

  // === VIDEO GALLERY ===

  // Save video to gallery
  async saveVideo(videoData: {
    title: string;
    file_url: string;
    thumbnail_url?: string;
    duration?: number;
    tags?: string[];
    metadata?: Record<string, any>;
  }): Promise<VideoContent> {
    return await apiClient.post('/gallery/save-video/', videoData);
  }

  // Upload and save video file
  async uploadVideo(
    videoFile: any,
    title: string,
    tags?: string[],
    onProgress?: (progress: number) => void
  ): Promise<VideoContent> {
    return await apiClient.uploadFile(
      '/gallery/save-video/',
      videoFile,
      'video',
      { title, tags: tags?.join(',') || '' },
      onProgress
    );
  }

  // List video gallery items
  async listVideoGalleryItems(params?: ListParams): Promise<PaginatedResponse<VideoContent>> {
    return await apiClient.get('/gallery/videos/', { params });
  }

  // Get single video gallery item
  async getVideoGalleryItem(id: number): Promise<VideoContent> {
    return await apiClient.get(`/gallery/videos/${id}/`);
  }

  // Update video gallery item
  async updateVideoGalleryItem(id: number, updates: Partial<VideoContent>): Promise<VideoContent> {
    return await apiClient.patch(`/gallery/videos/${id}/`, updates);
  }

  // Delete video gallery item
  async deleteVideoGalleryItem(id: number): Promise<void> {
    await apiClient.delete(`/gallery/videos/${id}/`);
  }

  // === GALLERY STATS AND MANAGEMENT ===

  // Get gallery statistics
  async getGalleryStats(): Promise<{
    total_images: number;
    total_videos: number;
    total_size: number;
    favorite_count: number;
    recent_uploads: number;
    storage_breakdown: Record<string, number>;
  }> {
    return await apiClient.get('/gallery/stats/');
  }

  // Search gallery
  async searchGallery(query: string, filters?: ListParams): Promise<PaginatedResponse<GalleryItem>> {
    return await apiClient.get('/gallery/list/', {
      params: { search: query, ...filters }
    });
  }

  // Get gallery items by tag
  async getGalleryByTag(tag: string, params?: ListParams): Promise<PaginatedResponse<GalleryItem>> {
    return await apiClient.get('/gallery/list/', {
      params: { tags: [tag], ...params }
    });
  }

  // Get favorite gallery items
  async getFavoriteGalleryItems(params?: ListParams): Promise<PaginatedResponse<GalleryItem>> {
    return await apiClient.get('/gallery/list/', {
      params: { is_favorite: true, ...params }
    });
  }

  // Bulk operations
  async bulkDeleteGalleryItems(ids: number[]): Promise<void> {
    await apiClient.post('/gallery/bulk-delete/', { ids });
  }

  async bulkUpdateTags(ids: number[], tags: string[]): Promise<void> {
    await apiClient.post('/gallery/bulk-update-tags/', { ids, tags });
  }

  async bulkToggleFavorite(ids: number[], favorite: boolean): Promise<void> {
    await apiClient.post('/gallery/bulk-favorite/', { ids, favorite });
  }

  // === GALLERY ORGANIZATION ===

  // Get all tags used in gallery
  async getGalleryTags(): Promise<string[]> {
    return await apiClient.get('/gallery/tags/');
  }

  // Get gallery items grouped by date
  async getGalleryByDate(date: string): Promise<PaginatedResponse<GalleryItem>> {
    return await apiClient.get('/gallery/list/', {
      params: { 
        date_from: date,
        date_to: date
      }
    });
  }

  // Get gallery items by content type
  async getGalleryByType(contentType: string, params?: ListParams): Promise<PaginatedResponse<GalleryItem>> {
    return await apiClient.get('/gallery/list/', {
      params: { content_type: contentType, ...params }
    });
  }

  // === SHARING AND EXPORT ===

  // Generate shareable link for gallery item
  async generateShareableLink(id: number, expiresIn?: number): Promise<{ share_url: string; expires_at?: string }> {
    return await apiClient.post(`/gallery/${id}/share/`, { expires_in: expiresIn });
  }

  // Export gallery items
  async exportGalleryItems(ids: number[], format: 'zip' | 'pdf' | 'json'): Promise<Blob> {
    return await apiClient.post('/gallery/export/', { ids, format }, {
      responseType: 'blob'
    });
  }

  // Download gallery item
  async downloadGalleryItem(id: number): Promise<Blob> {
    return await apiClient.get(`/gallery/${id}/download/`, {
      responseType: 'blob'
    });
  }
}

export const galleryService = new GalleryService();
export default galleryService;