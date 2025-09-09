import { create } from 'zustand';
import { galleryService } from '../services/galleryService';
import { GalleryItem, VideoContent } from '../types/api';

interface GalleryState {
  // Gallery Items
  galleryItems: GalleryItem[];
  videoGalleryItems: VideoContent[];
  isLoading: boolean;
  hasMoreItems: boolean;
  currentPage: number;
  
  // Upload state
  isUploading: boolean;
  uploadProgress: number;
  
  // Filters and search
  filters: {
    contentType?: string;
    tags?: string[];
    dateFrom?: string;
    dateTo?: string;
    isFavorite?: boolean;
    search?: string;
  };
  
  // Current selections
  selectedItems: number[];
  currentItem: GalleryItem | null;
  currentVideo: VideoContent | null;
  
  // Stats
  stats: {
    totalImages: number;
    totalVideos: number;
    totalSize: number;
    favoriteCount: number;
  } | null;
  
  // Error handling
  error: string | null;
  
  // Actions - Gallery Management
  loadGallery: (page?: number, refresh?: boolean) => Promise<void>;
  loadVideoGallery: (page?: number, refresh?: boolean) => Promise<void>;
  uploadImage: (imageFile: any, title: string, tags?: string[]) => Promise<GalleryItem>;
  uploadVideo: (videoFile: any, title: string, tags?: string[]) => Promise<VideoContent>;
  deleteItem: (id: number, isVideo?: boolean) => Promise<void>;
  toggleFavorite: (id: number, isVideo?: boolean) => Promise<void>;
  updateItem: (id: number, updates: Partial<GalleryItem>, isVideo?: boolean) => Promise<void>;
  
  // Actions - Search and Filters
  searchGallery: (query: string) => Promise<void>;
  applyFilters: (filters: any) => void;
  clearFilters: () => void;
  
  // Actions - Selection
  selectItem: (id: number) => void;
  selectMultipleItems: (ids: number[]) => void;
  clearSelection: () => void;
  setCurrentItem: (item: GalleryItem | null) => void;
  setCurrentVideo: (video: VideoContent | null) => void;
  
  // Actions - Bulk Operations
  bulkDeleteItems: (ids: number[]) => Promise<void>;
  bulkUpdateTags: (ids: number[], tags: string[]) => Promise<void>;
  bulkToggleFavorite: (ids: number[], favorite: boolean) => Promise<void>;
  
  // Actions - Stats and Analytics
  loadGalleryStats: () => Promise<void>;
  
  // Actions - Export and Share
  downloadItem: (id: number, isVideo?: boolean) => Promise<void>;
  exportItems: (ids: number[], format: string) => Promise<void>;
  generateShareLink: (id: number, isVideo?: boolean) => Promise<string>;
  
  // Utility actions
  clearError: () => void;
  refreshGallery: () => Promise<void>;
}

export const useGalleryStore = create<GalleryState>((set, get) => ({
  // Initial state
  galleryItems: [],
  videoGalleryItems: [],
  isLoading: false,
  hasMoreItems: true,
  currentPage: 1,
  
  isUploading: false,
  uploadProgress: 0,
  
  filters: {},
  
  selectedItems: [],
  currentItem: null,
  currentVideo: null,
  
  stats: null,
  
  error: null,
  
  // Gallery Management Actions
  loadGallery: async (page = 1, refresh = false) => {
    try {
      set({ isLoading: true, error: null });
      
      if (refresh || page === 1) {
        set({ galleryItems: [], currentPage: 1, hasMoreItems: true });
      }
      
      const { filters } = get();
      const response = await galleryService.listGalleryItems({
        page,
        limit: 20,
        ordering: '-created_at',
        ...filters,
      });
      
      const { galleryItems } = get();
      const newItems = page === 1 ? response.results : [...galleryItems, ...response.results];
      
      set({
        galleryItems: newItems,
        currentPage: page,
        hasMoreItems: !!response.next,
        isLoading: false,
      });
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.userMessage || error.message || 'Failed to load gallery' 
      });
      throw error;
    }
  },

  loadVideoGallery: async (page = 1, refresh = false) => {
    try {
      set({ isLoading: true, error: null });
      
      if (refresh || page === 1) {
        set({ videoGalleryItems: [] });
      }
      
      const { filters } = get();
      const response = await galleryService.listVideoGalleryItems({
        page,
        limit: 20,
        ordering: '-created_at',
        ...filters,
      });
      
      const { videoGalleryItems } = get();
      const newItems = page === 1 ? response.results : [...videoGalleryItems, ...response.results];
      
      set({
        videoGalleryItems: newItems,
        isLoading: false,
      });
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.userMessage || error.message || 'Failed to load video gallery' 
      });
      throw error;
    }
  },

  uploadImage: async (imageFile, title, tags = []) => {
    try {
      set({ isUploading: true, uploadProgress: 0, error: null });
      
      const item = await galleryService.uploadImage(
        imageFile,
        title,
        tags,
        (progress) => set({ uploadProgress: progress })
      );
      
      set(state => ({
        galleryItems: [item, ...state.galleryItems],
        isUploading: false,
        uploadProgress: 100,
      }));
      
      return item;
    } catch (error: any) {
      set({ 
        isUploading: false,
        uploadProgress: 0,
        error: error.userMessage || error.message || 'Upload failed' 
      });
      throw error;
    }
  },

  uploadVideo: async (videoFile, title, tags = []) => {
    try {
      set({ isUploading: true, uploadProgress: 0, error: null });
      
      const video = await galleryService.uploadVideo(
        videoFile,
        title,
        tags,
        (progress) => set({ uploadProgress: progress })
      );
      
      set(state => ({
        videoGalleryItems: [video, ...state.videoGalleryItems],
        isUploading: false,
        uploadProgress: 100,
      }));
      
      return video;
    } catch (error: any) {
      set({ 
        isUploading: false,
        uploadProgress: 0,
        error: error.userMessage || error.message || 'Video upload failed' 
      });
      throw error;
    }
  },

  deleteItem: async (id, isVideo = false) => {
    try {
      if (isVideo) {
        await galleryService.deleteVideoGalleryItem(id);
        set(state => ({
          videoGalleryItems: state.videoGalleryItems.filter(item => item.id !== id),
          currentVideo: state.currentVideo?.id === id ? null : state.currentVideo,
        }));
      } else {
        await galleryService.deleteGalleryItem(id);
        set(state => ({
          galleryItems: state.galleryItems.filter(item => item.id !== id),
          currentItem: state.currentItem?.id === id ? null : state.currentItem,
        }));
      }
      
      // Remove from selection if selected
      set(state => ({
        selectedItems: state.selectedItems.filter(itemId => itemId !== id)
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to delete item' });
      throw error;
    }
  },

  toggleFavorite: async (id, isVideo = false) => {
    try {
      if (isVideo) {
        // For videos, we'll need to implement this in the service
        const video = get().videoGalleryItems.find(v => v.id === id);
        if (video) {
          // Update locally for now
          set(state => ({
            videoGalleryItems: state.videoGalleryItems.map(v => 
              v.id === id ? { ...v, is_favorite: !v.is_favorite } : v
            )
          }));
        }
      } else {
        const item = get().galleryItems.find(i => i.id === id);
        if (item) {
          await galleryService.likeImage(id, !item.is_favorite);
          set(state => ({
            galleryItems: state.galleryItems.map(i => 
              i.id === id ? { ...i, is_favorite: !i.is_favorite } : i
            )
          }));
        }
      }
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to toggle favorite' });
      throw error;
    }
  },

  updateItem: async (id, updates, isVideo = false) => {
    try {
      if (isVideo) {
        const video = await galleryService.updateVideoGalleryItem(id, updates);
        set(state => ({
          videoGalleryItems: state.videoGalleryItems.map(v => v.id === id ? video : v),
          currentVideo: state.currentVideo?.id === id ? video : state.currentVideo,
        }));
      } else {
        const item = await galleryService.updateGalleryItem(id, updates);
        set(state => ({
          galleryItems: state.galleryItems.map(i => i.id === id ? item : i),
          currentItem: state.currentItem?.id === id ? item : state.currentItem,
        }));
      }
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to update item' });
      throw error;
    }
  },

  // Search and Filter Actions
  searchGallery: async (query) => {
    try {
      set({ isLoading: true, error: null, filters: { search: query } });
      
      const response = await galleryService.searchGallery(query);
      
      set({
        galleryItems: response.results,
        isLoading: false,
        hasMoreItems: !!response.next,
        currentPage: 1,
      });
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.userMessage || error.message || 'Search failed' 
      });
      throw error;
    }
  },

  applyFilters: (filters) => {
    set({ filters });
    // Reload gallery with new filters
    get().loadGallery(1, true);
  },

  clearFilters: () => {
    set({ filters: {} });
    get().loadGallery(1, true);
  },

  // Selection Actions
  selectItem: (id) => {
    set(state => {
      const isSelected = state.selectedItems.includes(id);
      return {
        selectedItems: isSelected 
          ? state.selectedItems.filter(itemId => itemId !== id)
          : [...state.selectedItems, id]
      };
    });
  },

  selectMultipleItems: (ids) => {
    set({ selectedItems: ids });
  },

  clearSelection: () => {
    set({ selectedItems: [] });
  },

  setCurrentItem: (item) => {
    set({ currentItem: item });
  },

  setCurrentVideo: (video) => {
    set({ currentVideo: video });
  },

  // Bulk Operations
  bulkDeleteItems: async (ids) => {
    try {
      await galleryService.bulkDeleteGalleryItems(ids);
      
      set(state => ({
        galleryItems: state.galleryItems.filter(item => !ids.includes(item.id)),
        selectedItems: [],
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Bulk delete failed' });
      throw error;
    }
  },

  bulkUpdateTags: async (ids, tags) => {
    try {
      await galleryService.bulkUpdateTags(ids, tags);
      
      set(state => ({
        galleryItems: state.galleryItems.map(item => 
          ids.includes(item.id) ? { ...item, tags } : item
        ),
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Bulk tag update failed' });
      throw error;
    }
  },

  bulkToggleFavorite: async (ids, favorite) => {
    try {
      await galleryService.bulkToggleFavorite(ids, favorite);
      
      set(state => ({
        galleryItems: state.galleryItems.map(item => 
          ids.includes(item.id) ? { ...item, is_favorite: favorite } : item
        ),
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Bulk favorite update failed' });
      throw error;
    }
  },

  // Stats and Analytics
  loadGalleryStats: async () => {
    try {
      const stats = await galleryService.getGalleryStats();
      set({ stats });
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to load stats' });
    }
  },

  // Export and Share
  downloadItem: async (id, isVideo = false) => {
    try {
      const blob = await galleryService.downloadGalleryItem(id);
      
      // Create download link (React Native Web compatible)
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `gallery-item-${id}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Download failed' });
      throw error;
    }
  },

  exportItems: async (ids, format) => {
    try {
      const blob = await galleryService.exportGalleryItems(ids, format as any);
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `gallery-export.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Export failed' });
      throw error;
    }
  },

  generateShareLink: async (id, isVideo = false) => {
    try {
      const response = await galleryService.generateShareableLink(id);
      return response.share_url;
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to generate share link' });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  refreshGallery: async () => {
    await get().loadGallery(1, true);
  },
}));