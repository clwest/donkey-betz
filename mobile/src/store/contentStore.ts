import { create } from 'zustand';
import { contentService } from '../services/contentService';
import { ContentItem, BlogPost, SocialPost, PaginatedResponse } from '../types/api';

interface ContentState {
  // Content Generation
  isGenerating: boolean;
  generatedContent: ContentItem | null;
  generationProgress: number;
  
  // Content Library
  contentItems: ContentItem[];
  isLoadingContent: boolean;
  hasMoreContent: boolean;
  currentPage: number;
  
  // Blog Posts
  blogPosts: BlogPost[];
  currentBlog: BlogPost | null;
  isGeneratingBlog: boolean;
  
  // Social Posts
  socialPosts: SocialPost[];
  currentSocial: SocialPost | null;
  isGeneratingSocial: boolean;
  
  // Error handling
  error: string | null;
  
  // Actions - Content Generation
  generateContent: (request: any) => Promise<ContentItem>;
  batchGenerateContent: (requests: any) => Promise<ContentItem[]>;
  clearGeneratedContent: () => void;
  
  // Actions - Content Library
  loadContent: (page?: number, refresh?: boolean) => Promise<void>;
  deleteContent: (id: number) => Promise<void>;
  starContent: (id: number, starred: boolean) => Promise<void>;
  duplicateContent: (id: number) => Promise<ContentItem>;
  
  // Actions - Blog Generation
  generateBlog: (request: any) => Promise<BlogPost>;
  loadBlogPosts: (refresh?: boolean) => Promise<void>;
  saveBlogPost: (blog: Partial<BlogPost>) => Promise<BlogPost>;
  updateBlogPost: (id: number, updates: Partial<BlogPost>) => Promise<BlogPost>;
  deleteBlogPost: (id: number) => Promise<void>;
  setBlogAsCurrent: (blog: BlogPost) => void;
  
  // Actions - Social Media
  generateSocialPost: (request: any) => Promise<SocialPost>;
  loadSocialPosts: (refresh?: boolean) => Promise<void>;
  saveSocialPost: (post: Partial<SocialPost>) => Promise<SocialPost>;
  updateSocialPost: (id: number, updates: Partial<SocialPost>) => Promise<SocialPost>;
  deleteSocialPost: (id: number) => Promise<void>;
  setSocialAsCurrent: (post: SocialPost) => void;
  
  // Utility actions
  clearError: () => void;
}

export const useContentStore = create<ContentState>((set, get) => ({
  // Initial state
  isGenerating: false,
  generatedContent: null,
  generationProgress: 0,
  
  contentItems: [],
  isLoadingContent: false,
  hasMoreContent: true,
  currentPage: 1,
  
  blogPosts: [],
  currentBlog: null,
  isGeneratingBlog: false,
  
  socialPosts: [],
  currentSocial: null,
  isGeneratingSocial: false,
  
  error: null,
  
  // Content Generation Actions
  generateContent: async (request) => {
    try {
      set({ isGenerating: true, error: null, generationProgress: 0 });
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        set(state => ({
          generationProgress: Math.min(state.generationProgress + 10, 90)
        }));
      }, 500);
      
      const content = await contentService.generateContent(request);
      
      clearInterval(progressInterval);
      set({
        generatedContent: content,
        isGenerating: false,
        generationProgress: 100,
      });
      
      // Add to content list if it's the first page
      const { currentPage } = get();
      if (currentPage === 1) {
        set(state => ({
          contentItems: [content, ...state.contentItems]
        }));
      }
      
      return content;
    } catch (error: any) {
      set({ 
        isGenerating: false, 
        generationProgress: 0,
        error: error.userMessage || error.message || 'Content generation failed' 
      });
      throw error;
    }
  },

  batchGenerateContent: async (requests) => {
    try {
      set({ isGenerating: true, error: null, generationProgress: 0 });
      
      const content = await contentService.batchGenerate(requests);
      
      set({
        isGenerating: false,
        generationProgress: 100,
      });
      
      // Add to content list
      const { currentPage } = get();
      if (currentPage === 1) {
        set(state => ({
          contentItems: [...content, ...state.contentItems]
        }));
      }
      
      return content;
    } catch (error: any) {
      set({ 
        isGenerating: false, 
        generationProgress: 0,
        error: error.userMessage || error.message || 'Batch generation failed' 
      });
      throw error;
    }
  },

  clearGeneratedContent: () => {
    set({ generatedContent: null, generationProgress: 0 });
  },

  // Content Library Actions
  loadContent: async (page = 1, refresh = false) => {
    try {
      set({ isLoadingContent: true, error: null });
      
      if (refresh || page === 1) {
        set({ contentItems: [], currentPage: 1, hasMoreContent: true });
      }
      
      const response = await contentService.listContent({ 
        page, 
        limit: 20,
        ordering: '-created_at' 
      });
      
      const { contentItems } = get();
      const newItems = page === 1 ? response.results : [...contentItems, ...response.results];
      
      set({
        contentItems: newItems,
        currentPage: page,
        hasMoreContent: !!response.next,
        isLoadingContent: false,
      });
    } catch (error: any) {
      set({ 
        isLoadingContent: false,
        error: error.userMessage || error.message || 'Failed to load content' 
      });
      throw error;
    }
  },

  deleteContent: async (id) => {
    try {
      await contentService.deleteContent(id);
      
      set(state => ({
        contentItems: state.contentItems.filter(item => item.id !== id)
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to delete content' });
      throw error;
    }
  },

  starContent: async (id, starred) => {
    try {
      await contentService.starContent(id, starred);
      
      set(state => ({
        contentItems: state.contentItems.map(item => 
          item.id === id ? { ...item, is_favorite: starred } : item
        )
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to update favorite status' });
      throw error;
    }
  },

  duplicateContent: async (id) => {
    try {
      const duplicate = await contentService.duplicateContent(id);
      
      set(state => ({
        contentItems: [duplicate, ...state.contentItems]
      }));
      
      return duplicate;
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to duplicate content' });
      throw error;
    }
  },

  // Blog Actions
  generateBlog: async (request) => {
    try {
      set({ isGeneratingBlog: true, error: null });
      
      const blog = await contentService.generateBlog(request);
      
      set({
        currentBlog: blog,
        isGeneratingBlog: false,
        blogPosts: [blog, ...get().blogPosts]
      });
      
      return blog;
    } catch (error: any) {
      set({ 
        isGeneratingBlog: false,
        error: error.userMessage || error.message || 'Blog generation failed' 
      });
      throw error;
    }
  },

  loadBlogPosts: async (refresh = false) => {
    try {
      set({ isLoadingContent: true, error: null });
      
      const response = await contentService.listBlogPosts({ 
        ordering: '-created_at',
        limit: 50 
      });
      
      set({
        blogPosts: response.results,
        isLoadingContent: false,
      });
    } catch (error: any) {
      set({ 
        isLoadingContent: false,
        error: error.userMessage || error.message || 'Failed to load blog posts' 
      });
      throw error;
    }
  },

  saveBlogPost: async (blogData) => {
    try {
      const blog = await contentService.saveBlogPost(blogData);
      
      set(state => ({
        blogPosts: [blog, ...state.blogPosts.filter(b => b.id !== blog.id)]
      }));
      
      return blog;
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to save blog post' });
      throw error;
    }
  },

  updateBlogPost: async (id, updates) => {
    try {
      const blog = await contentService.updateBlogPost(id, updates);
      
      set(state => ({
        blogPosts: state.blogPosts.map(b => b.id === id ? blog : b),
        currentBlog: state.currentBlog?.id === id ? blog : state.currentBlog
      }));
      
      return blog;
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to update blog post' });
      throw error;
    }
  },

  deleteBlogPost: async (id) => {
    try {
      await contentService.deleteBlogPost(id);
      
      set(state => ({
        blogPosts: state.blogPosts.filter(b => b.id !== id),
        currentBlog: state.currentBlog?.id === id ? null : state.currentBlog
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to delete blog post' });
      throw error;
    }
  },

  setBlogAsCurrent: (blog) => {
    set({ currentBlog: blog });
  },

  // Social Media Actions
  generateSocialPost: async (request) => {
    try {
      set({ isGeneratingSocial: true, error: null });
      
      const post = await contentService.generateSocialPost(request);
      
      set({
        currentSocial: post,
        isGeneratingSocial: false,
        socialPosts: [post, ...get().socialPosts]
      });
      
      return post;
    } catch (error: any) {
      set({ 
        isGeneratingSocial: false,
        error: error.userMessage || error.message || 'Social post generation failed' 
      });
      throw error;
    }
  },

  loadSocialPosts: async (refresh = false) => {
    try {
      set({ isLoadingContent: true, error: null });
      
      const response = await contentService.listSocialPosts({ 
        ordering: '-created_at',
        limit: 50 
      });
      
      set({
        socialPosts: response.results,
        isLoadingContent: false,
      });
    } catch (error: any) {
      set({ 
        isLoadingContent: false,
        error: error.userMessage || error.message || 'Failed to load social posts' 
      });
      throw error;
    }
  },

  saveSocialPost: async (postData) => {
    try {
      const post = await contentService.saveSocialPost(postData);
      
      set(state => ({
        socialPosts: [post, ...state.socialPosts.filter(p => p.id !== post.id)]
      }));
      
      return post;
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to save social post' });
      throw error;
    }
  },

  updateSocialPost: async (id, updates) => {
    try {
      const post = await contentService.updateSocialPost(id, updates);
      
      set(state => ({
        socialPosts: state.socialPosts.map(p => p.id === id ? post : p),
        currentSocial: state.currentSocial?.id === id ? post : state.currentSocial
      }));
      
      return post;
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to update social post' });
      throw error;
    }
  },

  deleteSocialPost: async (id) => {
    try {
      await contentService.deleteSocialPost(id);
      
      set(state => ({
        socialPosts: state.socialPosts.filter(p => p.id !== id),
        currentSocial: state.currentSocial?.id === id ? null : state.currentSocial
      }));
    } catch (error: any) {
      set({ error: error.userMessage || error.message || 'Failed to delete social post' });
      throw error;
    }
  },

  setSocialAsCurrent: (post) => {
    set({ currentSocial: post });
  },

  clearError: () => {
    set({ error: null });
  },
}));