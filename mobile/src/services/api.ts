/**
 * API Services for React Native
 * React Native specific implementations with proper mobile optimizations
 */

// Import React Native optimized services
export { apiClient } from './apiClient';
export { authService } from './authService';
export { contentService } from './contentService';
export { galleryService } from './galleryService';
export { voiceService } from './voiceService';
export { dashboardService } from './dashboardService';
export { videoService } from './videoService';
export { styleMemoryService } from './styleMemoryService';
export { promptingService } from './promptingService';
export { assistantService } from './assistantService';

// Add a mock stabilityService for backward compatibility
export const stabilityService = {
  upscale: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/upscale/', { image: imageFile, ...params });
  },
  inpaint: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/inpaint/', { image: imageFile, ...params });
  },
  removeBackground: async (imageFile: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/remove-background/', { image: imageFile });
  },
  outpaint: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/outpaint/', { image: imageFile, ...params });
  },
  generate3D: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/generate-3d/', { image: imageFile, ...params });
  },
  reimagine: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/reimagine/', { image: imageFile, ...params });
  },
  eraseObject: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/erase-object/', { image: imageFile, ...params });
  },
  sketchToImage: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/sketch-to-image/', { image: imageFile, ...params });
  },
  controlToImage: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/control-to-image/', { image: imageFile, ...params });
  },
  replaceObject: async (imageFile: any, params: any) => {
    const { apiClient } = await import('./apiClient');
    return apiClient.post('/stability/replace-object/', { image: imageFile, ...params });
  },
};

// Re-export types
export * from '../types/api';

// Import service instances for convenience
import { authService } from './authService';
import { contentService } from './contentService';
import { galleryService } from './galleryService';
import { voiceService } from './voiceService';
import { dashboardService } from './dashboardService';
import { videoService } from './videoService';
import { styleMemoryService } from './styleMemoryService';
import { promptingService } from './promptingService';
import { assistantService } from './assistantService';

// Legacy API class for backward compatibility during migration
class ApiService {
  // HTTP Methods for backward compatibility
  async get(url: string, config?: any) {
    const { apiClient } = await import('./apiClient');
    return apiClient.get(url, config);
  }

  async post(url: string, data?: any, config?: any) {
    const { apiClient } = await import('./apiClient');
    return apiClient.post(url, data, config);
  }

  async put(url: string, data?: any, config?: any) {
    const { apiClient } = await import('./apiClient');
    return apiClient.put(url, data, config);
  }

  async delete(url: string, config?: any) {
    const { apiClient } = await import('./apiClient');
    return apiClient.delete(url, config);
  }

  // Content generation
  async generateContent(params: any) {
    return contentService.generateContent(params);
  }

  async batchGenerateImages(params: any) {
    return contentService.batchGenerate(params);
  }

  // Blog generation
  async generateBlog(params: any) {
    return contentService.generateBlog(params);
  }

  // Social media
  async generateSocialMedia(params: any) {
    return contentService.generateSocialPost(params);
  }

  // Video generation
  async generateVideo(params: any) {
    if (params.type === 'text_to_video') {
      return videoService.textToVideo(params);
    } else {
      return videoService.imageToVideo(params);
    }
  }

  async checkVideoStatus(taskId: string) {
    return videoService.checkVideoStatus(taskId);
  }

  // Voice
  async transcribeAudio(audioFile: any, outputType?: string) {
    return voiceService.transcribeAudio(audioFile, { output_type: outputType });
  }

  // Gallery
  async getGallery(page?: number, limit?: number, filters?: any) {
    return galleryService.listGalleryItems({ page, limit, ...filters });
  }

  async deleteGalleryItem(id: number) {
    return galleryService.deleteGalleryItem(id);
  }

  // Dashboard
  async getDashboardStats() {
    return dashboardService.getDashboardStats();
  }

  // Auth methods
  async login(email: string, password: string) {
    return authService.login({ username: email, password });
  }

  async logout() {
    return authService.logout();
  }

  async register(email: string, password: string, name: string) {
    return authService.register({
      username: email.split('@')[0],
      email,
      password,
      first_name: name,
    });
  }

  // Profile
  async getCurrentUser() {
    return authService.getCurrentUser();
  }

  async updateProfile(data: any) {
    return authService.updateProfile(data);
  }
}

// Export a singleton instance for backward compatibility
export const api = new ApiService();

// Export default for convenience
export default api;