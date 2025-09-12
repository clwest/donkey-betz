import { apiClient } from './api.config';

// Gallery Types
export interface GalleryItem {
  id: string;
  title: string;
  content_type: 'image' | 'video' | 'text' | 'audio' | 'document';
  file_url?: string;
  content?: string;
  prompt?: string;
  parameters?: Record<string, any>;
  tags: string[];
  category: string;
  is_favorite: boolean;
  is_public: boolean;
  file_size?: number;
  mime_type?: string;
  dimensions?: {
    width: number;
    height: number;
  };
  duration?: number; // for video/audio
  created_at: string;
  updated_at: string;
  metadata?: {
    model?: string;
    style?: string;
    generation_time?: number;
    cost?: number;
    parent_id?: string;
    variation_of?: string;
  };
}

export interface GalleryCollection {
  id: string;
  name: string;
  description: string;
  items: GalleryItem[];
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface GalleryFilters {
  content_type?: string[];
  category?: string[];
  tags?: string[];
  is_favorite?: boolean;
  date_range?: {
    start: string;
    end: string;
  };
  search?: string;
}

export interface GalleryStats {
  total_items: number;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
  total_size: number;
  favorites_count: number;
  recent_activity: Array<{
    action: 'created' | 'updated' | 'favorited' | 'shared';
    item_title: string;
    timestamp: string;
  }>;
}

// Gallery Service
export const galleryService = {
  // Get gallery items with filters and pagination
  async getItems(filters: GalleryFilters = {}, page = 1, limit = 50): Promise<{
    items: GalleryItem[];
    total: number;
    page: number;
    pages: number;
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    // Add filters to params
    if (filters.content_type?.length) {
      params.append('content_type', filters.content_type.join(','));
    }
    if (filters.category?.length) {
      params.append('category', filters.category.join(','));
    }
    if (filters.tags?.length) {
      params.append('tags', filters.tags.join(','));
    }
    if (filters.is_favorite !== undefined) {
      params.append('is_favorite', filters.is_favorite.toString());
    }
    if (filters.search) {
      params.append('search', filters.search);
    }
    if (filters.date_range) {
      params.append('date_start', filters.date_range.start);
      params.append('date_end', filters.date_range.end);
    }

    const { data } = await apiClient.get(`/v1/gallery/list/?${params}`);
    return {
      items: data.images || data.items || [],
      total: data.pagination?.total || 0,
      page: data.pagination?.offset || 0,
      pages: Math.ceil((data.pagination?.total || 0) / limit),
    };
  },

  // Get single gallery item
  async getItem(id: string): Promise<GalleryItem> {
    const { data } = await apiClient.get(`/v1/gallery/${id}/`);
    return data;
  },

  // Save content to gallery
  async saveItem(item: {
    title: string;
    content_type: GalleryItem['content_type'];
    file_url?: string;
    content?: string;
    prompt?: string;
    parameters?: Record<string, any>;
    tags?: string[];
    category?: string;
    metadata?: GalleryItem['metadata'];
  }): Promise<GalleryItem> {
    const { data } = await apiClient.post('/v1/gallery/', item);
    return data;
  },

  // Update gallery item
  async updateItem(id: string, updates: Partial<GalleryItem>): Promise<GalleryItem> {
    const { data } = await apiClient.put(`/v1/gallery/${id}/`, updates);
    return data;
  },

  // Delete gallery item
  async deleteItem(id: string): Promise<void> {
    await apiClient.delete(`/v1/gallery/${id}/`);
  },

  // Batch delete items
  async deleteItems(ids: string[]): Promise<void> {
    await apiClient.post('/v1/gallery/bulk-delete/', { ids });
  },

  // Toggle favorite status
  async toggleFavorite(id: string): Promise<GalleryItem> {
    const { data } = await apiClient.post(`/v1/gallery/${id}/toggle-favorite/`);
    return data;
  },

  // Add/remove tags
  async updateTags(id: string, tags: string[]): Promise<GalleryItem> {
    const { data } = await apiClient.post(`/v1/gallery/${id}/tags/`, { tags });
    return data;
  },

  // Get available categories and tags
  async getMetadata(): Promise<{
    categories: string[];
    tags: string[];
    content_types: Array<{ type: string; count: number }>;
  }> {
    const { data } = await apiClient.get('/v1/gallery/metadata/');
    return data;
  },

  // Get gallery statistics
  async getStats(): Promise<GalleryStats> {
    const { data } = await apiClient.get('/v1/gallery/stats/');
    return data;
  },

  // Search gallery
  async searchItems(query: string, filters: GalleryFilters = {}): Promise<{
    items: GalleryItem[];
    total: number;
    suggestions: string[];
  }> {
    const { data } = await apiClient.get('/v1/gallery/search/', {
      params: { q: query, ...filters },
    });
    return data;
  },

  // Collections
  async getCollections(): Promise<GalleryCollection[]> {
    const { data } = await apiClient.get('/v1/gallery/collections/');
    return data;
  },

  async createCollection(collection: {
    name: string;
    description: string;
    item_ids?: string[];
  }): Promise<GalleryCollection> {
    const { data } = await apiClient.post('/v1/gallery/collections/', collection);
    return data;
  },

  async updateCollection(id: string, updates: Partial<GalleryCollection>): Promise<GalleryCollection> {
    const { data } = await apiClient.put(`/v1/gallery/collections/${id}/`, updates);
    return data;
  },

  async deleteCollection(id: string): Promise<void> {
    await apiClient.delete(`/v1/gallery/collections/${id}/`);
  },

  async addToCollection(collectionId: string, itemIds: string[]): Promise<GalleryCollection> {
    const { data } = await apiClient.post(`/v1/gallery/collections/${collectionId}/add/`, {
      item_ids: itemIds,
    });
    return data;
  },

  async removeFromCollection(collectionId: string, itemIds: string[]): Promise<GalleryCollection> {
    const { data } = await apiClient.post(`/v1/gallery/collections/${collectionId}/remove/`, {
      item_ids: itemIds,
    });
    return data;
  },

  // Export functionality
  async exportItems(itemIds: string[], format: 'zip' | 'pdf'): Promise<Blob> {
    const { data } = await apiClient.post('/v1/gallery/export/', {
      item_ids: itemIds,
      format,
    }, {
      responseType: 'blob',
    });
    return data;
  },

  // Share items
  async shareItems(itemIds: string[], options: {
    expiry_days?: number;
    password?: string;
    allow_download?: boolean;
  }): Promise<{
    share_url: string;
    share_code: string;
    expires_at: string;
  }> {
    const { data } = await apiClient.post('/v1/gallery/share/', {
      item_ids: itemIds,
      ...options,
    });
    return data;
  },

  // Get shared gallery
  async getSharedItems(shareCode: string, password?: string): Promise<{
    items: GalleryItem[];
    collection_name: string;
    expires_at: string;
    allow_download: boolean;
  }> {
    const { data } = await apiClient.get(`/v1/gallery/shared/${shareCode}/`, {
      params: { password },
    });
    return data;
  },

  // Duplicate item
  async duplicateItem(id: string, title?: string): Promise<GalleryItem> {
    const { data } = await apiClient.post(`/v1/gallery/${id}/duplicate/`, { title });
    return data;
  },

  // Generate variations
  async generateVariations(id: string, count = 3): Promise<GalleryItem[]> {
    const { data } = await apiClient.post(`/v1/gallery/${id}/variations/`, { count });
    return data;
  },

  // Image-specific operations
  async cropImage(id: string, cropData: {
    x: number;
    y: number;
    width: number;
    height: number;
  }): Promise<GalleryItem> {
    const { data } = await apiClient.post(`/v1/gallery/${id}/crop/`, cropData);
    return data;
  },

  async resizeImage(id: string, dimensions: {
    width: number;
    height: number;
    maintain_aspect_ratio?: boolean;
  }): Promise<GalleryItem> {
    const { data } = await apiClient.post(`/v1/gallery/${id}/resize/`, dimensions);
    return data;
  },

  // Auto-tagging and categorization
  async autoTag(id: string): Promise<{
    suggested_tags: string[];
    suggested_category: string;
    confidence: number;
  }> {
    const { data } = await apiClient.post(`/v1/gallery/${id}/auto-tag/`);
    return data;
  },
};