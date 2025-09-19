import { useState, useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { contentService } from '../../services/content.service';
import { galleryService } from '../../services/gallery.service';
import { apiClient } from '../../services/api.config';
import { BlogViewer } from '../../components/features/blog/BlogViewer';
import { BlogEditor } from '../../components/features/blog/BlogEditor';
import { SocialViewer } from '../../components/features/social';
import { ImageViewer } from '../../components/features/images/ImageViewer';
import { ContentTransformModal } from '../../components/features/content/ContentTransformModal';
import { Logger } from '../../utils/logger';
import { toast } from 'sonner';
import { DocumentTextIcon, PhotoIcon, EyeIcon, TrashIcon, GlobeAltIcon, EyeSlashIcon, HashtagIcon, PlayIcon, ArrowDownTrayIcon, XMarkIcon, MicrophoneIcon, SpeakerWaveIcon, NewspaperIcon, BookOpenIcon, SparklesIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';

// Utility function to strip markdown and return plain text
const stripMarkdown = (markdown: string): string => {
  if (!markdown) return '';
  
  return markdown
    // Remove headers
    .replace(/^#{1,6}\s+/gm, '')
    // Remove bold and italic
    .replace(/\*{1,3}([^*]+)\*{1,3}/g, '$1')
    .replace(/_{1,3}([^_]+)_{1,3}/g, '$1')
    // Remove links but keep text
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    // Remove images
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
    // Remove code blocks
    .replace(/```[^`]*```/g, '')
    // Remove inline code
    .replace(/`([^`]+)`/g, '$1')
    // Remove blockquotes
    .replace(/^>\s+/gm, '')
    // Remove horizontal rules
    .replace(/^---+$/gm, '')
    // Remove lists markers
    .replace(/^[\*\-\+]\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    // Remove HTML tags
    .replace(/<[^>]+>/g, '')
    // Remove extra whitespace
    .replace(/\n{3,}/g, '\n\n')
    .trim();
};

interface BlogPost {
  id: number;
  title: string;
  word_count: number;
  tags: string[];
  tone: string;
  length: string;
  created_at: string;
  preview: string;
  is_live?: boolean;
  is_deleted?: boolean;
}

interface GalleryImage {
  id: number;  // Changed from string to number
  title: string;
  image_url: string;
  saved_at: string;
  tags: string[];
  category?: string;
  description?: string;
}

interface SocialPost {
  id: number;
  topic: string;
  platforms: string[];
  tone: string;
  total_posts: number;
  created_at: string;
  preview: string;
}

interface VideoPost {
  id: number;
  title: string;
  video_url: string;
  thumbnail_url?: string;
  duration: number;
  source_type: 'text_to_video' | 'image_to_video';
  original_prompt: string;
  motion_prompt?: string;
  saved_at: string;
  tags: string[];
  category?: string;
  description?: string;
}

interface VoiceTranscript {
  id: number;
  content_text: string;
  created_at: string;
  metadata?: {
    type?: string;
    duration?: number;
    file_size?: number;
    output_type?: string;
    timestamp?: string;
  };
  tags?: string[];
}

interface PodcastEpisode {
  id: number;
  show_name?: string;
  season?: number;
  episode?: number;
  title: string;
  format?: string;
  duration?: number;
  is_published?: boolean;
  created_at: string;
  content?: any;  // Full content from GeneratedContent
  metadata?: any;  // Metadata from GeneratedContent
}

export function GalleryPage() {
  const navigate = useNavigate();
  const [blogs, setBlogs] = useState<BlogPost[]>([]);
  const [socialPosts, setSocialPosts] = useState<SocialPost[]>([]);
  const [videos, setVideos] = useState<VideoPost[]>([]);
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [voiceTranscripts, setVoiceTranscripts] = useState<VoiceTranscript[]>([]);
  const [podcasts, setPodcasts] = useState<PodcastEpisode[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'blogs' | 'social' | 'videos' | 'images' | 'voice' | 'podcasts'>('blogs');
  const [isCreatingContent, setIsCreatingContent] = useState(false);
  const [expandedTranscripts, setExpandedTranscripts] = useState<Set<number>>(new Set());
  const [selectedBlogId, setSelectedBlogId] = useState<number | null>(null);
  const [selectedSocialId, setSelectedSocialId] = useState<number | null>(null);
  const [selectedPodcastId, setSelectedPodcastId] = useState<number | null>(null);
  const [blogViewerOpen, setBlogViewerOpen] = useState(false);
  const [socialViewerOpen, setSocialViewerOpen] = useState(false);
  const [podcastViewerOpen, setPodcastViewerOpen] = useState(false);
  const [podcastContent, setPodcastContent] = useState<string>('');
  const [editingBlog, setEditingBlog] = useState<BlogPost | null>(null);
  const [blogEditorOpen, setBlogEditorOpen] = useState(false);
  const [transformingBlog, setTransformingBlog] = useState<BlogPost | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState<number>(0);
  const [imageViewerOpen, setImageViewerOpen] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<VideoPost | null>(null);
  const [videoPlayerOpen, setVideoPlayerOpen] = useState(false);
  const [expiredVideoUrls, setExpiredVideoUrls] = useState<Set<number>>(new Set());
  
  // Bulk selection state
  const [selectedItems, setSelectedItems] = useState<Set<number | string>>(new Set());
  const [bulkDeleteMode, setBulkDeleteMode] = useState(false);

  useEffect(() => {
    Logger.component('GalleryPage', 'Loading gallery content');
    loadContent();
  }, []);

  const loadContent = async () => {
    setLoading(true);
    try {
      // Load blogs
      const blogData = await contentService.getBlogList();
      // Get force-deleted IDs from localStorage
      const forceDeletedIds = JSON.parse(localStorage.getItem('forceDeletedBlogIds') || '[]');
      
      const blogs = (blogData.blog_posts || [])
        .filter((blog: BlogPost) => !blog.is_deleted && !forceDeletedIds.includes(blog.id))  // Filter out deleted and force-deleted blogs
        .map((blog: BlogPost) => {
          // Parse embedded title from content if the title is generic
          if (blog.title === 'Generated Blog Post' && blog.preview) {
            const titleMatch = blog.preview.match(/\*\*TITLE:\s*([^\*]+)\*\*/);
            if (titleMatch && titleMatch[1]) {
              return {
                ...blog,
                title: titleMatch[1].trim()
              };
            }
          }
          return blog;
        });
      setBlogs(blogs);
      
      // Load social posts
      const socialData = await contentService.getSocialPostsList();
      setSocialPosts(socialData.social_posts || []);
      
      // Load videos
      try {
        const videoData = await contentService.getVideoGallery({ limit: 50 });
        const videoItems = (videoData.videos || []).map((video: any) => ({
          id: video.id,
          title: video.title,
          video_url: video.video_url,
          thumbnail_url: video.thumbnail_url,
          duration: video.duration,
          source_type: video.source_type,
          original_prompt: video.original_prompt,
          motion_prompt: video.motion_prompt,
          saved_at: video.saved_at,
          tags: video.tags || [],
          category: video.category,
          description: video.description
        }));
        setVideos(videoItems);
        
        // Check for expired video URLs (Runway ML URLs expire after 30 days)
        const expired = new Set<number>();
        const now = new Date();
        videoItems.forEach((video: VideoPost) => {
          const savedDate = new Date(video.saved_at);
          const daysSinceSaved = Math.floor((now.getTime() - savedDate.getTime()) / (1000 * 60 * 60 * 24));
          
          // Mark as expired if it's a Runway ML video older than 30 days
          if ((video.video_url.includes('runwayml.com') || video.video_url.includes('cloudfront.net')) && daysSinceSaved > 30) {
            expired.add(video.id);
          }
        });
        
        if (expired.size > 0) {
          setExpiredVideoUrls(expired);
          Logger.component('GalleryPage', `Found ${expired.size} videos with expired URLs`);
        }
        
        Logger.component('GalleryPage', `Loaded ${videoItems.length} videos`);
      } catch (error) {
        Logger.error('Failed to load videos', error);
        setVideos([]);
      }
      
      // Load images from content list API with type filter
      try {
        const response = await apiClient.get('/v1/content/list/', {
          params: {
            type: 'image',
            limit: 200  // Get up to 200 images
          }
        });
        const allContent = response.data.contents || [];
        
        // Transform to gallery format
        const imageItems = allContent.map((img: any) => ({
          id: img.id || Date.now(),  // Keep as number
          title: img.prompt || 'Untitled Image',
          image_url: img.result?.startsWith('http') 
            ? img.result 
            : `http://localhost:8000${img.result}`,
          saved_at: img.created_at || new Date().toISOString(),
          tags: img.metadata?.style ? [img.metadata.style] : [],
          category: 'Generated',
          description: img.prompt,
          metadata: img.metadata
        }));
        
        setImages(imageItems);
        
        Logger.state('GalleryPage', 'Images loaded from content list', { 
          imageCount: imageItems.length 
        });
      } catch (imgError) {
        Logger.error('GalleryPage.loadImages', imgError);
        // Fallback to empty array if image loading fails
        setImages([]);
      }
      
      // Load voice transcripts
      try {
        const response = await apiClient.get('/v1/voice/history/');
        const rawTranscripts = response.data.history || [];
        
        // Map the API response to match our VoiceTranscript interface
        const transcripts = rawTranscripts.map((item: any) => {
          // Debug logging to understand the API response structure
          console.log('Voice transcript item:', item);
          
          const transcript = {
            id: item.id,
            content_text: item.content || item.content_text || item.transcript || item.text || '',
            created_at: item.timestamp || item.created_at || new Date().toISOString(),
            metadata: item.metadata || {},
            tags: item.tags || []
          };
          
          // Log the mapped result
          console.log('Mapped transcript:', transcript);
          return transcript;
        });
        
        setVoiceTranscripts(transcripts);
        Logger.state('GalleryPage', 'Voice transcripts loaded', { 
          voiceCount: transcripts.length 
        });
      } catch (voiceError) {
        Logger.error('GalleryPage.loadVoiceTranscripts', voiceError);
        setVoiceTranscripts([]);
      }
      
      // Load podcasts from Content Library
      try {
        // First try to get podcasts from the GeneratedContent library
        const libraryResponse = await apiClient.get('/v1/content/library/?type=podcast');
        const podcastItems = libraryResponse.data.results || [];
        
        // Map the GeneratedContent items to PodcastEpisode format
        const mappedPodcasts = podcastItems.map((item: any) => ({
          id: item.id,
          title: item.title,
          created_at: item.created_at,
          content: item.content,
          metadata: item.metadata,
          show_name: item.metadata?.show_name,
          season: item.metadata?.season,
          episode: item.metadata?.episode,
          duration: item.metadata?.duration,
          format: item.metadata?.format
        }));
        
        setPodcasts(mappedPodcasts);
        Logger.state('GalleryPage', 'Podcasts loaded from library', { 
          podcastCount: mappedPodcasts.length 
        });
      } catch (podcastError) {
        Logger.error('GalleryPage.loadPodcasts from library', podcastError);
        // Fallback to old podcast API if needed
        try {
          const podcastData = await contentService.getPodcastList();
          setPodcasts(podcastData || []);
        } catch (error) {
          setPodcasts([]);
        }
      }
      
      Logger.state('GalleryPage', 'Content loaded', { 
        blogCount: blogData.blog_posts?.length || 0,
        socialCount: socialData.social_posts?.length || 0,
        imageCount: images.length,
        voiceCount: voiceTranscripts.length,
        podcastCount: podcasts.length 
      });
    } catch (error: any) {
      Logger.error('GalleryPage.loadContent', error);
      toast.error('Failed to load gallery content');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const viewBlog = (blogId: number) => {
    Logger.component('GalleryPage', `Opening blog viewer for blog ${blogId}`);
    setSelectedBlogId(blogId);
    setBlogViewerOpen(true);
  };

  const closeBlogViewer = () => {
    setBlogViewerOpen(false);
    setSelectedBlogId(null);
  };

  const viewSocialPost = (socialId: number) => {
    Logger.component('GalleryPage', `Opening social viewer for post ${socialId}`);
    setSelectedSocialId(socialId);
    setSocialViewerOpen(true);
  };

  const viewPodcast = async (podcastId: number) => {
    Logger.component('GalleryPage', `Opening podcast viewer for episode ${podcastId}`);
    const podcast = podcasts.find(p => p.id === podcastId);
    if (podcast) {
      // Get the script content from the podcast data
      let scriptContent = '';
      if (podcast.content?.script) {
        scriptContent = podcast.content.script;
      } else if (podcast.content?.content) {
        scriptContent = podcast.content.content;
      } else if (typeof podcast.content === 'string') {
        scriptContent = podcast.content;
      } else {
        // Try to fetch from library API if content not available
        try {
          const response = await apiClient.get(`/v1/content/library/${podcastId}/`);
          if (response.data.content?.script) {
            scriptContent = response.data.content.script;
          } else if (response.data.content?.content) {
            scriptContent = response.data.content.content;
          } else if (typeof response.data.content === 'string') {
            scriptContent = response.data.content;
          }
        } catch (error) {
          Logger.error('Failed to fetch podcast content', error);
        }
      }
      
      setPodcastContent(scriptContent || 'No podcast content available');
      setSelectedPodcastId(podcastId);
      setPodcastViewerOpen(true);
    }
  };

  const closePodcastViewer = () => {
    setPodcastViewerOpen(false);
    setSelectedPodcastId(null);
    setPodcastContent('');
  };

  const closeSocialViewer = () => {
    setSocialViewerOpen(false);
    setSelectedSocialId(null);
  };

  const viewImage = (index: number) => {
    Logger.component('GalleryPage', `Opening image viewer for image at index ${index}`);
    setSelectedImageIndex(index);
    setImageViewerOpen(true);
  };

  const closeImageViewer = () => {
    setImageViewerOpen(false);
  };

  const viewVideo = (video: VideoPost) => {
    Logger.component('GalleryPage', `Opening video player for ${video.title}`);
    setSelectedVideo(video);
    setVideoPlayerOpen(true);
  };

  const closeVideoPlayer = () => {
    setVideoPlayerOpen(false);
    setSelectedVideo(null);
  };

  const deleteImage = async (imageId: number) => {
    if (!confirm('Are you sure you want to delete this image? This action cannot be undone.')) {
      return;
    }

    try {
      Logger.component('GalleryPage', 'Deleting image', { imageId });
      
      // Images are from the Content model, use bulk delete endpoint with single ID
      const response = await apiClient.post('/content/bulk-delete/', {
        content_ids: [imageId]
      });
      
      if (response.data.deleted_count === 0) {
        throw new Error('Failed to delete image - it may not exist');
      }
      
      // Remove from local state
      setImages(prev => prev.filter(img => img.id !== imageId));
      
      toast.success('Image deleted successfully!');
      closeImageViewer();
      
      Logger.state('GalleryPage', 'Image deleted', { imageId });
    } catch (error: any) {
      Logger.error('GalleryPage.deleteImage', error);
      toast.error(error.message || 'Failed to delete image');
    }
  };

  const deleteVideo = async (videoId: number) => {
    if (!confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
      return;
    }

    try {
      Logger.component('GalleryPage', 'Deleting video', { videoId });
      
      // Call the delete API endpoint
      await apiClient.delete(`/v1/gallery/videos/${videoId}/`);
      
      // Remove from local state
      setVideos(prev => prev.filter(v => v.id !== videoId));
      
      toast.success('Video deleted successfully!');
      Logger.state('GalleryPage', 'Video deleted', { videoId });
    } catch (error: any) {
      Logger.error('GalleryPage.deleteVideo', error);
      toast.error('Failed to delete video');
    }
  };

  const editBlog = (blog: any) => {
    Logger.component('GalleryPage', `Opening blog editor for blog ${blog.id}`);
    setEditingBlog(blog);
    setBlogEditorOpen(true);
    closeBlogViewer();
  };

  const toggleBlogLiveStatus = async (blog: BlogPost, event: React.MouseEvent) => {
    event.stopPropagation();
    
    try {
      Logger.component('GalleryPage', 'Toggling blog live status', { blogId: blog.id, currentStatus: blog.is_live });
      const newStatus = !blog.is_live;
      
      await contentService.toggleBlogLiveStatus(blog.id, newStatus);
      
      // Update the local state
      setBlogs(blogs.map(b => b.id === blog.id ? { ...b, is_live: newStatus } : b));
      
      toast.success(`Blog ${newStatus ? 'published' : 'unpublished'} successfully!`);
      Logger.state('GalleryPage', 'Blog live status updated', { blogId: blog.id, newStatus });
    } catch (error: any) {
      Logger.error('GalleryPage.toggleBlogLiveStatus', error);
      toast.error('Failed to update blog status');
    }
  };

  const deleteBlog = async (blog: BlogPost, event: React.MouseEvent) => {
    event.stopPropagation();
    
    if (!confirm(`Are you sure you want to delete "${blog.title}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      Logger.component('GalleryPage', 'Deleting blog', { blogId: blog.id });
      
      await contentService.deleteBlogPost(blog.id);
      
      // Remove from local state
      setBlogs(blogs.filter(b => b.id !== blog.id));
      
      toast.success('Blog deleted successfully!');
      Logger.state('GalleryPage', 'Blog deleted', { blogId: blog.id });
    } catch (error: any) {
      Logger.error('GalleryPage.deleteBlog', error);
      
      // If soft delete fails, offer force delete
      const forceDelete = confirm(
        `Failed to delete blog properly. This blog may have corrupted data.\n\n` +
        `Would you like to force remove it from your library?\n\n` +
        `Note: This will only hide it from your view, but won't delete it from the server.`
      );
      
      if (forceDelete) {
        // Force remove from UI
        setBlogs(blogs.filter(b => b.id !== blog.id));
        
        // Store force-deleted IDs in localStorage to persist hiding
        const forceDeletedIds = JSON.parse(localStorage.getItem('forceDeletedBlogIds') || '[]');
        forceDeletedIds.push(blog.id);
        localStorage.setItem('forceDeletedBlogIds', JSON.stringify(forceDeletedIds));
        
        toast.warning('Blog force removed from view. It may still exist on the server.');
        Logger.state('GalleryPage', 'Blog force deleted from UI', { blogId: blog.id });
      } else {
        toast.error('Failed to delete blog. It may have corrupted data.');
      }
    }
  };

  const closeBlogEditor = () => {
    setBlogEditorOpen(false);
    setEditingBlog(null);
  };

  const publishAllBlogs = async () => {
    const draftBlogs = blogs.filter(blog => !blog.is_live);
    
    if (draftBlogs.length === 0) {
      toast.info('No draft blogs to publish');
      return;
    }

    if (!confirm(`Are you sure you want to publish ${draftBlogs.length} draft blogs? This will make them all visible on the public blog page.`)) {
      return;
    }

    setLoading(true);
    const results = { success: 0, failed: 0, failedIds: [] as number[] };

    try {
      Logger.component('GalleryPage', 'Publishing all draft blogs', { count: draftBlogs.length });
      
      // Process blogs in parallel batches for speed
      const batchSize = 5;
      for (let i = 0; i < draftBlogs.length; i += batchSize) {
        const batch = draftBlogs.slice(i, i + batchSize);
        
        const batchPromises = batch.map(async (blog) => {
          try {
            // Try simple approach first - just update is_live status
            await contentService.updateBlogPost(blog.id, {
              title: blog.title,
              content: blog.preview || '', // Use preview as fallback
              meta_description: '',
              tags: blog.tags || [],
              is_live: true
            });
            results.success++;
            return { success: true, id: blog.id };
          } catch (error: any) {
            // If that fails, try the toggle method
            try {
              await contentService.toggleBlogLiveStatus(blog.id, true);
              results.success++;
              return { success: true, id: blog.id };
            } catch (secondError) {
              Logger.error('GalleryPage.publishAllBlogs', `Failed to publish blog ${blog.id}`, secondError);
              results.failed++;
              results.failedIds.push(blog.id);
              return { success: false, id: blog.id, error: secondError };
            }
          }
        });

        // Wait for batch to complete
        await Promise.all(batchPromises);
        
        // Update UI with progress
        const processed = Math.min(i + batchSize, draftBlogs.length);
        toast.loading(`Publishing blogs... ${processed}/${draftBlogs.length}`, { id: 'bulk-publish' });
      }

      // Reload the blogs to get updated status
      await loadContent();
      
      // Show final result
      toast.dismiss('bulk-publish');
      if (results.failed === 0) {
        toast.success(`Successfully published ${results.success} blogs!`);
      } else {
        toast.warning(
          `Published ${results.success} blogs. ${results.failed} failed (IDs: ${results.failedIds.join(', ')}). ` +
          `These may have missing content - try opening and saving them individually.`
        );
      }
      
      Logger.state('GalleryPage', 'Bulk publish completed', results);
    } catch (error: any) {
      Logger.error('GalleryPage.publishAllBlogs', error);
      toast.error('Failed to complete bulk publish');
    } finally {
      setLoading(false);
      toast.dismiss('bulk-publish');
    }
  };

  const handleBlogSaved = (updatedBlog: BlogPost) => {
    // Update the blog in the list
    setBlogs(prevBlogs => 
      prevBlogs.map(blog => 
        blog.id === updatedBlog.id 
          ? { ...blog, ...updatedBlog }
          : blog
      )
    );
    Logger.state('GalleryPage', 'Blog updated in list', updatedBlog);
  };

  const deleteVoiceTranscript = async (transcriptId: number) => {
    if (!confirm('Are you sure you want to delete this voice transcript? This action cannot be undone.')) {
      return;
    }
    
    try {
      Logger.component('GalleryPage', 'Deleting voice transcript', { transcriptId });
      
      // Voice transcripts are stored as Memory objects
      await apiClient.delete(`/memory/${transcriptId}/`);
      
      // Remove from local state after successful deletion
      setVoiceTranscripts(prev => prev.filter(t => t.id !== transcriptId));
      
      toast.success('Voice transcript deleted successfully!');
      Logger.state('GalleryPage', 'Voice transcript deleted', { transcriptId });
    } catch (error: any) {
      Logger.error('GalleryPage.deleteVoiceTranscript', error);
      toast.error('Failed to delete voice transcript');
    }
  };

  // Bulk selection functions
  const toggleItemSelection = (id: number | string) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const selectAll = () => {
    const allIds = new Set<number | string>();
    
    switch (activeTab) {
      case 'blogs':
        blogs.forEach(blog => allIds.add(blog.id));
        break;
      case 'social':
        socialPosts.forEach(post => allIds.add(post.id));
        break;
      case 'videos':
        videos.forEach(video => allIds.add(video.id));
        break;
      case 'images':
        images.forEach(image => allIds.add(image.id));
        break;
      case 'voice':
        voiceTranscripts.forEach(transcript => allIds.add(transcript.id));
        break;
      case 'podcasts':
        podcasts.forEach(podcast => allIds.add(podcast.id));
        break;
    }
    
    setSelectedItems(allIds);
  };

  const clearSelection = () => {
    setSelectedItems(new Set());
  };

  const handleBulkDelete = async () => {
    if (selectedItems.size === 0) {
      toast.error('No items selected');
      return;
    }

    const confirmDelete = window.confirm(`Are you sure you want to delete ${selectedItems.size} items? This action cannot be undone.`);
    if (!confirmDelete) return;

    try {
      const itemsArray = Array.from(selectedItems);
      Logger.component('GalleryPage', `Starting bulk delete for ${itemsArray.length} items on tab: ${activeTab}`, { items: itemsArray });

      // Handle different content types
      if (activeTab === 'images') {
        // Images are from the Content model, use bulk delete endpoint
        Logger.component('GalleryPage', `Deleting ${itemsArray.length} images`);
        
        const response = await apiClient.post('/content/bulk-delete/', {
          content_ids: itemsArray.map(id => Number(id))
        });
        
        const deletedCount = response.data.deleted_count || 0;
        Logger.component('GalleryPage', `Bulk delete completed`, { deletedCount, requested: itemsArray.length });
        
        if (deletedCount === itemsArray.length) {
          toast.success(`Successfully deleted ${deletedCount} image${deletedCount !== 1 ? 's' : ''}`);
        } else if (deletedCount > 0) {
          toast.warning(`Deleted ${deletedCount} of ${itemsArray.length} images. Some may not exist or you don't have permission.`);
        } else {
          toast.error('Failed to delete images. They may not exist or you don\'t have permission.');
        }
      } else if (activeTab === 'videos') {
        // For videos, use individual delete calls
        const deletePromises = itemsArray.map(id => 
          apiClient.delete(`/v1/gallery/videos/${id}/`)
            .catch(err => {
              Logger.error(`Failed to delete video ${id}`, err);
              return { error: true, id };
            })
        );
        
        const results = await Promise.all(deletePromises);
        const failedDeletes = results.filter(r => r && r.error).length;
        
        if (failedDeletes > 0) {
          toast.warning(`Deleted ${itemsArray.length - failedDeletes} videos. ${failedDeletes} failed to delete.`);
        } else {
          toast.success(`Successfully deleted ${itemsArray.length} video${itemsArray.length !== 1 ? 's' : ''}`);
        }
      } else if (activeTab === 'blogs') {
        // For blogs, use individual delete for now
        const deletePromises = itemsArray.map(id => {
          const blog = blogs.find(b => b.id === id);
          if (blog) {
            return deleteBlogItem(blog);
          }
          return Promise.resolve();
        });
        await Promise.all(deletePromises);
        toast.success(`Successfully deleted ${selectedItems.size} blog${selectedItems.size !== 1 ? 's' : ''}`);
      } else if (activeTab === 'voice') {
        // For voice transcripts, delete locally for now
        itemsArray.forEach(id => {
          setVoiceTranscripts(prev => prev.filter(t => t.id !== id));
        });
        toast.success(`Successfully deleted ${selectedItems.size} transcript${selectedItems.size !== 1 ? 's' : ''}`);
      }
      
      clearSelection();
      setBulkDeleteMode(false);
      await loadContent(); // Reload content
    } catch (error: any) {
      Logger.error('Bulk delete failed', error);
      toast.error(error.response?.data?.error || 'Failed to delete some items');
    }
  };

  // Helper function for deleting blog (extracted from existing logic)
  const deleteBlogItem = async (blog: BlogPost) => {
    try {
      await contentService.deleteBlog(blog.id);
      setBlogs(prev => prev.filter(b => b.id !== blog.id));
    } catch (error) {
      throw error;
    }
  };

  // Helper function for deleting voice transcript
  const deleteVoiceTranscriptItem = async (transcriptId: number) => {
    try {
      await apiClient.delete(`/memory/${transcriptId}/`);
      setVoiceTranscripts(prev => prev.filter(t => t.id !== transcriptId));
    } catch (error) {
      throw error;
    }
  };

  const createContentFromVoice = async (transcript: string, contentType: 'blog' | 'social') => {
    if (!transcript) {
      toast.error('No transcript available');
      return;
    }

    setIsCreatingContent(true);
    
    try {
      let result;
      
      if (contentType === 'blog') {
        // Generate blog from transcript
        toast.loading('Creating blog post from voice transcript...', { id: 'voice-to-blog' });
        result = await contentService.generateBlog({
          topic: transcript, // Use full transcript
          tone: 'professional',
          length: 'medium',
          target_audience: 'general',
          include_outline: true,
          use_memory: true,
        });
        
        if (result.success) {
          toast.dismiss('voice-to-blog');
          toast.success('Blog post created from voice transcript!');
          // Reload blogs and switch to blogs tab
          await loadContent();
          setActiveTab('blogs');
        } else {
          toast.dismiss('voice-to-blog');
        }
      } else if (contentType === 'social') {
        // Generate social posts from transcript
        toast.loading('Creating social posts from voice transcript...', { id: 'voice-to-social' });
        result = await contentService.generateSocialPosts({
          topic: transcript, // Use full transcript
          platforms: ['twitter', 'linkedin', 'instagram'],
          tone: 'casual',
          variations_per_platform: 2,
        });
        
        if (result.success) {
          toast.dismiss('voice-to-social');
          toast.success('Social posts created from voice transcript!');
          // Reload social posts and switch to social tab
          await loadContent();
          setActiveTab('social');
        } else {
          toast.dismiss('voice-to-social');
        }
      }
    } catch (error: any) {
      console.error('Error creating content from voice:', error);
      // Dismiss any loading toasts
      toast.dismiss('voice-to-blog');
      toast.dismiss('voice-to-social');
      
      // Show appropriate error message
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error(`Creating ${contentType} is taking longer than expected. Please try with a shorter transcript or try again later.`);
      } else {
        toast.error(error.userMessage || `Failed to create ${contentType} from voice`);
      }
    } finally {
      setIsCreatingContent(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading your content...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8" style={{ backgroundColor: 'hsl(var(--muted))', minHeight: '100vh' }}>
      {/* Header - Gaming Style */}
      <div className="bg-card p-6">
        <div className="bg-card"></div>
        <div className="relative z-10 flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-black font-mono uppercase tracking-wider" 
                style={{ 
                  color: 'hsl(var(--muted))',
                  textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
                }}>NEURAL CONTENT MATRIX</h1>
            <p className="mt-3 font-mono" style={{ color: 'hsl(var(--muted))' }}>
              NEURAL ARCHIVE • AI-GENERATED CONTENT REPOSITORY
            </p>
          </div>
          {!bulkDeleteMode && (
            <button
              onClick={() => setBulkDeleteMode(true)}
              className="bg-card px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider flex items-center gap-2 transition-all duration-300 hover:scale-105"
              style={{
                background: 'hsl(var(--muted))',
                border: '1px solid hsl(var(--muted))',
                color: 'hsl(var(--muted))'
              }}
            >
              <TrashIcon className="h-4 w-4" />
              BULK DELETE
            </button>
          )}
        </div>
      </div>

      {/* Bulk Actions Bar */}
      {bulkDeleteMode && (
        <div className="bg-card p-4">
          <div className="bg-card"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm font-mono uppercase tracking-wider" style={{ color: 'hsl(var(--muted))' }}>
                  {selectedItems.size} item{selectedItems.size !== 1 ? 's' : ''} selected
                </span>
                <button
                  onClick={selectAll}
                  className="px-4 py-2 text-sm font-mono font-bold uppercase tracking-wider bg-card rounded transition-all duration-200 hover:scale-105"
                  style={{ 
                    background: 'hsl(var(--muted))',
                    border: '1px solid hsl(var(--muted))',
                    color: 'hsl(var(--muted))'
                  }}
                >
                  Select All
                </button>
                <button
                  onClick={clearSelection}
                  className="px-4 py-2 text-sm font-mono font-bold uppercase tracking-wider bg-card rounded transition-all duration-200 hover:scale-105"
                  style={{ 
                    background: 'hsl(var(--muted))',
                    border: '1px solid hsl(var(--muted))',
                    color: 'hsl(var(--muted))'
                  }}
                >
                  Clear Selection
                </button>
              </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  console.log('Delete Selected clicked', { 
                    selectedCount: selectedItems.size, 
                    selectedItems: Array.from(selectedItems),
                    activeTab 
                  });
                  handleBulkDelete();
                }}
                disabled={selectedItems.size === 0}
                className={`px-6 py-2 text-sm font-mono font-bold uppercase tracking-wider rounded-xl transition-all duration-200 flex items-center gap-2 ${
                  selectedItems.size > 0
                    ? 'bg-card hover:scale-105'
                    : 'opacity-50 cursor-not-allowed'
                }`}
                style={selectedItems.size > 0 ? {
                  background: 'linear-gradient(135deg, #dc2626, #991b1b)',
                  border: '1px solid #dc2626',
                  color: 'white',
                  boxShadow: '0 0 20px rgba(220, 38, 38, 0.3)'
                } : {}}
              >
                <TrashIcon className="h-4 w-4" />
                DELETE SELECTED
              </button>
              <button
                onClick={() => {
                  setBulkDeleteMode(false);
                  clearSelection();
                }}
                className="px-6 py-2 text-sm font-mono font-bold uppercase tracking-wider bg-card rounded-xl transition-all duration-200 hover:scale-105"
                style={{
                  background: 'hsl(var(--muted))',
                  border: '1px solid hsl(var(--muted))',
                  color: 'hsl(var(--muted))'
                }}
              >
                CANCEL
              </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Neural Tab Matrix */}
      <div className="bg-card p-6">
        <div className="bg-card"></div>
        <div className="relative z-10">
          <h2 className="text-xl font-bold font-mono uppercase tracking-wider mb-4" 
              style={{ color: 'hsl(var(--muted))' }}>
            CONTENT TYPE SELECTOR
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
            <div
              className={`bg-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
                activeTab === 'blogs' ? 'ring-2' : ''
              }`}
              style={{
                borderColor: activeTab === 'blogs' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                boxShadow: activeTab === 'blogs' ? 'hsl(var(--muted))' : undefined,
                background: activeTab === 'blogs' ? 'hsl(var(--muted))' : undefined
              }}
              onClick={() => setActiveTab('blogs')}
            >
              <div className="bg-card"></div>
              <div className="relative z-10 text-center">
                <DocumentTextIcon className="h-6 w-6 mx-auto mb-2" 
                  style={{ 
                    color: activeTab === 'blogs' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                    filter: activeTab === 'blogs' ? 'drop-shadow(0 0 8px rgba(0, 255, 255, 0.6))' : undefined
                  }} />
                <p className="font-bold font-mono uppercase tracking-wider text-xs" 
                   style={{ color: activeTab === 'blogs' ? 'hsl(var(--muted))' : 'hsl(var(--muted))' }}>
                  BLOGS
                </p>
                <p className="text-xs font-mono" style={{ color: 'hsl(var(--muted))' }}>({blogs.length})</p>
              </div>
            </div>
            <div
              className={`bg-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
                activeTab === 'social' ? 'ring-2' : ''
              }`}
              style={{
                borderColor: activeTab === 'social' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                boxShadow: activeTab === 'social' ? '0 0 20px rgba(157, 78, 221, 0.3)' : undefined,
                background: activeTab === 'social' ? 'hsl(var(--muted))' : undefined
              }}
              onClick={() => setActiveTab('social')}
            >
              <div className="bg-card"></div>
              <div className="relative z-10 text-center">
                <HashtagIcon className="h-6 w-6 mx-auto mb-2" 
                  style={{ 
                    color: activeTab === 'social' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                    filter: activeTab === 'social' ? 'drop-shadow(0 0 8px rgba(157, 78, 221, 0.6))' : undefined
                  }} />
                <p className="font-bold font-mono uppercase tracking-wider text-xs" 
                   style={{ color: activeTab === 'social' ? 'hsl(var(--muted))' : 'hsl(var(--muted))' }}>
                  SOCIAL
                </p>
                <p className="text-xs font-mono" style={{ color: 'hsl(var(--muted))' }}>({socialPosts.length})</p>
              </div>
            </div>

            <div
              className={`bg-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
                activeTab === 'videos' ? 'ring-2' : ''
              }`}
              style={{
                borderColor: activeTab === 'videos' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                boxShadow: activeTab === 'videos' ? '0 0 20px rgba(57, 255, 20, 0.3)' : undefined,
                background: activeTab === 'videos' ? 'hsl(var(--muted))' : undefined
              }}
              onClick={() => setActiveTab('videos')}
            >
              <div className="bg-card"></div>
              <div className="relative z-10 text-center">
                <PlayIcon className="h-6 w-6 mx-auto mb-2" 
                  style={{ 
                    color: activeTab === 'videos' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                    filter: activeTab === 'videos' ? 'drop-shadow(0 0 8px rgba(57, 255, 20, 0.6))' : undefined
                  }} />
                <p className="font-bold font-mono uppercase tracking-wider text-xs" 
                   style={{ color: activeTab === 'videos' ? 'hsl(var(--muted))' : 'hsl(var(--muted))' }}>
                  VIDEOS
                </p>
                <p className="text-xs font-mono" style={{ color: 'hsl(var(--muted))' }}>({videos.length})</p>
              </div>
            </div>

            <div
              className={`bg-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
                activeTab === 'images' ? 'ring-2' : ''
              }`}
              style={{
                borderColor: activeTab === 'images' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                boxShadow: activeTab === 'images' ? '0 0 20px rgba(255, 165, 0, 0.3)' : undefined,
                background: activeTab === 'images' ? 'hsl(var(--muted))' : undefined
              }}
              onClick={() => setActiveTab('images')}
            >
              <div className="bg-card"></div>
              <div className="relative z-10 text-center">
                <PhotoIcon className="h-6 w-6 mx-auto mb-2" 
                  style={{ 
                    color: activeTab === 'images' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                    filter: activeTab === 'images' ? 'drop-shadow(0 0 8px rgba(255, 165, 0, 0.6))' : undefined
                  }} />
                <p className="font-bold font-mono uppercase tracking-wider text-xs" 
                   style={{ color: activeTab === 'images' ? 'hsl(var(--muted))' : 'hsl(var(--muted))' }}>
                  IMAGES
                </p>
                <p className="text-xs font-mono" style={{ color: 'hsl(var(--muted))' }}>({images.length})</p>
              </div>
            </div>

            <div
              className={`bg-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
                activeTab === 'voice' ? 'ring-2' : ''
              }`}
              style={{
                borderColor: activeTab === 'voice' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                boxShadow: activeTab === 'voice' ? '0 0 20px rgba(157, 78, 221, 0.3)' : undefined,
                background: activeTab === 'voice' ? 'hsl(var(--muted))' : undefined
              }}
              onClick={() => setActiveTab('voice')}
            >
              <div className="bg-card"></div>
              <div className="relative z-10 text-center">
                <MicrophoneIcon className="h-6 w-6 mx-auto mb-2" 
                  style={{ 
                    color: activeTab === 'voice' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                    filter: activeTab === 'voice' ? 'drop-shadow(0 0 8px rgba(157, 78, 221, 0.6))' : undefined
                  }} />
                <p className="font-bold font-mono uppercase tracking-wider text-xs" 
                   style={{ color: activeTab === 'voice' ? 'hsl(var(--muted))' : 'hsl(var(--muted))' }}>
                  VOICE
                </p>
                <p className="text-xs font-mono" style={{ color: 'hsl(var(--muted))' }}>({voiceTranscripts.length})</p>
              </div>
            </div>

            <div
              className={`bg-card p-4 cursor-pointer transition-all duration-300 hover:scale-105 ${
                activeTab === 'podcasts' ? 'ring-2' : ''
              }`}
              style={{
                borderColor: activeTab === 'podcasts' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                boxShadow: activeTab === 'podcasts' ? 'hsl(var(--muted))' : undefined,
                background: activeTab === 'podcasts' ? 'hsl(var(--muted))' : undefined
              }}
              onClick={() => setActiveTab('podcasts')}
            >
              <div className="bg-card"></div>
              <div className="relative z-10 text-center">
                <SpeakerWaveIcon className="h-6 w-6 mx-auto mb-2" 
                  style={{ 
                    color: activeTab === 'podcasts' ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                    filter: activeTab === 'podcasts' ? 'drop-shadow(0 0 8px rgba(0, 255, 255, 0.6))' : undefined
                  }} />
                <p className="font-bold font-mono uppercase tracking-wider text-xs" 
                   style={{ color: activeTab === 'podcasts' ? 'hsl(var(--muted))' : 'hsl(var(--muted))' }}>
                  PODCASTS
                </p>
                <p className="text-xs font-mono" style={{ color: 'hsl(var(--muted))' }}>({podcasts.length})</p>
              </div>
            </div>
          </div>

          {/* Bulk Actions - Only show when on blogs tab and there are draft blogs */}
          {activeTab === 'blogs' && blogs.some(blog => !blog.is_live) && (
            <button
              onClick={publishAllBlogs}
              className="px-6 py-3 font-mono font-bold text-sm uppercase tracking-wider rounded-xl transition-all duration-300 hover:scale-105 flex items-center gap-2"
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #16a34a, #15803d)',
                border: '1px solid hsl(var(--muted))',
                color: 'white',
                boxShadow: '0 0 20px rgba(57, 255, 20, 0.3)'
              }}
            >
              <GlobeAltIcon className="h-4 w-4" />
              PUBLISH ALL DRAFTS ({blogs.filter(b => !b.is_live).length})
            </button>
          )}

        {/* Voice Actions - Clear all transcripts */}
        {activeTab === 'voice' && voiceTranscripts.length > 0 && (
          <button
            onClick={async () => {
              if (confirm(`Are you sure you want to delete all ${voiceTranscripts.length} voice transcripts? This action cannot be undone.`)) {
                try {
                  // Delete all voice transcripts from backend
                  const deletePromises = voiceTranscripts.map(transcript => 
                    apiClient.delete(`/memory/${transcript.id}/`)
                      .catch(err => {
                        Logger.error(`Failed to delete transcript ${transcript.id}`, err);
                        return { error: true, id: transcript.id };
                      })
                  );
                  
                  const results = await Promise.all(deletePromises);
                  const failedCount = results.filter(r => r && r.error).length;
                  
                  if (failedCount > 0) {
                    toast.warning(`Cleared ${voiceTranscripts.length - failedCount} transcripts. ${failedCount} failed to delete.`);
                  } else {
                    toast.success('All voice transcripts cleared!');
                  }
                  
                  // Clear local state
                  setVoiceTranscripts([]);
                  
                  // Reload to ensure consistency
                  await loadContent();
                } catch (error) {
                  Logger.error('Failed to clear voice transcripts', error);
                  toast.error('Failed to clear all voice transcripts');
                }
              }
            }}
            className="px-6 py-3 font-mono font-bold text-sm uppercase tracking-wider rounded-xl transition-all duration-300 hover:scale-105 flex items-center gap-2"
            disabled={loading}
            style={{
              background: 'linear-gradient(135deg, #dc2626, #991b1b)',
              border: '1px solid #dc2626',
              color: 'white',
              boxShadow: '0 0 20px rgba(220, 38, 38, 0.3)'
            }}
          >
            <TrashIcon className="h-4 w-4" />
            CLEAR ALL ({voiceTranscripts.length})
          </button>
          )}
        </div>
      </div>

      {/* Content */}
      {activeTab === 'blogs' && (
        <div className="space-y-4">
          {blogs.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-muted-foreground">
                <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No blog posts saved yet.</p>
                <p className="text-sm">Generate and save a blog post to see it here!</p>
              </div>
            </Card>
          ) : (
            blogs.map((blog) => (
              <Card key={blog.id} className={bulkDeleteMode && selectedItems.has(blog.id) ? 'ring-2 ring-primary-500' : ''}>
                <div className="flex justify-between items-start">
                  {bulkDeleteMode && (
                    <div className="mr-4">
                      <input
                        type="checkbox"
                        checked={selectedItems.has(blog.id)}
                        onChange={() => toggleItemSelection(blog.id)}
                        className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 rounded focus:ring-primary-500"
                      />
                    </div>
                  )}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-foreground">
                        {stripMarkdown(blog.title)}
                      </h3>
                      
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        blog.is_live 
                          ? 'bg-green-500/20 text-green-300' 
                          : 'bg-yellow-500/20 text-yellow-300'
                      }`}>
                        {blog.is_live ? 'Published' : 'Draft'}
                      </span>
                    </div>
                    <p className="text-muted-foreground text-sm mb-3 line-clamp-2">
                      {stripMarkdown(blog.preview)}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{blog.word_count} words</span>
                      <span className="capitalize">{blog.tone} tone</span>
                      <span className="capitalize">{blog.length} length</span>
                      <span>{formatDate(blog.created_at)}</span>
                    </div>
                    {blog.tags && blog.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {blog.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 text-xs bg-primary-500/20 text-primary-300 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => viewBlog(blog.id)}
                      className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                      title="View full blog post"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    
                    <button
                      onClick={() => setTransformingBlog(blog)}
                      className="p-2 text-muted-foreground hover:text-primary-400 transition-colors"
                      title="Transform to Social Posts, Podcast, or eBook"
                    >
                      <SparklesIcon className="h-4 w-4" />
                    </button>
                    
                    <button
                      onClick={(e) => toggleBlogLiveStatus(blog, e)}
                      className={`p-2 transition-colors ${
                        blog.is_live 
                          ? 'text-green-500 hover:text-green-300' 
                          : 'text-muted-foreground hover:text-foreground'
                      }`}
                      title={blog.is_live ? 'Published - Click to unpublish' : 'Draft - Click to publish'}
                    >
                      {blog.is_live ? <GlobeAltIcon className="h-4 w-4" /> : <EyeSlashIcon className="h-4 w-4" />}
                    </button>
                    
                    <button
                      onClick={(e) => deleteBlog(blog, e)}
                      className="p-2 text-muted-foreground hover:text-red-500 transition-colors"
                      title="Delete blog post"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {activeTab === 'social' && (
        <div className="space-y-4">
          {socialPosts.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-muted-foreground">
                <HashtagIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No social media posts saved yet.</p>
                <p className="text-sm">Generate social posts to see them here!</p>
              </div>
            </Card>
          ) : (
            socialPosts.map((social) => (
              <Card key={social.id}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                      {social.topic}
                    </h3>
                    <p className="text-muted-foreground text-sm mb-3 line-clamp-2">
                      {social.preview}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="capitalize">{social.tone} tone</span>
                      <span>{social.total_posts} posts</span>
                      <span>{formatDate(social.created_at)}</span>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {social.platforms.map((platform, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-primary-500/20 text-primary-300 rounded capitalize"
                        >
                          {platform}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => viewSocialPost(social.id)}
                      className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                      title="View social posts"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {activeTab === 'videos' && (
        <div className="space-y-4">
          {videos.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-muted-foreground">
                <PlayIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No videos saved yet.</p>
                <p className="text-sm">Generate videos to see them here!</p>
              </div>
            </Card>
          ) : (
            videos.map((video) => (
              <Card key={video.id} className="overflow-hidden">
                <div className="flex flex-col lg:flex-row gap-4">
                  {/* Video Preview */}
                  <div className="lg:w-1/3">
                    {expiredVideoUrls.has(video.id) ? (
                      <div className="relative aspect-video rounded-lg overflow-hidden bg-card flex items-center justify-center">
                        <div className="text-center p-4">
                          <PlayIcon className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                          <p className="text-muted-foreground text-sm">Video expired</p>
                          <p className="text-muted-foreground text-xs mt-1">Runway ML URLs expire after 30 days</p>
                        </div>
                      </div>
                    ) : video.thumbnail_url ? (
                      <div className="relative aspect-video rounded-lg overflow-hidden bg-card">
                        <img
                          src={video.thumbnail_url}
                          alt={video.title}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center bg-black/20 hover:bg-black/40 transition-colors cursor-pointer">
                          <PlayIcon className="h-12 w-12 text-foreground opacity-80" />
                        </div>
                      </div>
                    ) : (
                      <div className="aspect-video rounded-lg bg-gradient-to-br from-blue-900/20 to-purple-900/20 flex items-center justify-center">
                        <PlayIcon className="h-12 w-12 text-muted-foreground" />
                      </div>
                    )}
                  </div>

                  {/* Video Details */}
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-lg font-semibold text-foreground">{video.title}</h3>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-1 bg-primary-500/20 text-primary-300 text-xs rounded-full">
                          {video.duration}s
                        </span>
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full capitalize">
                          {video.source_type.replace('_', ' ')}
                        </span>
                      </div>
                    </div>

                    {video.description && (
                      <p className="text-muted-foreground text-sm mb-3 line-clamp-2">
                        {video.description}
                      </p>
                    )}

                    <div className="space-y-2 mb-4">
                      <div className="text-sm">
                        <span className="text-muted-foreground">Prompt: </span>
                        <span className="text-muted-foreground">{video.original_prompt}</span>
                      </div>
                      {video.motion_prompt && (
                        <div className="text-sm">
                          <span className="text-muted-foreground">Motion: </span>
                          <span className="text-muted-foreground">{video.motion_prompt}</span>
                        </div>
                      )}
                    </div>

                    {video.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {video.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-700 text-muted-foreground text-xs rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        Saved {formatDate(video.saved_at)}
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            if (expiredVideoUrls.has(video.id)) {
                              toast.warning('This video link has expired. Runway ML URLs are only valid for 30 days after generation.');
                            } else {
                              viewVideo(video);
                            }
                          }}
                          disabled={expiredVideoUrls.has(video.id)}
                          className={`px-3 py-2 text-foreground text-sm rounded-lg transition-colors flex items-center gap-1 ${
                            expiredVideoUrls.has(video.id) 
                              ? 'bg-gray-600 cursor-not-allowed opacity-50' 
                              : 'bg-primary-600 hover:bg-primary-700'
                          }`}
                        >
                          <PlayIcon className="h-4 w-4" />
                          {expiredVideoUrls.has(video.id) ? 'Expired' : 'Play'}
                        </button>
                        <button
                          onClick={() => {
                            const link = document.createElement('a');
                            link.href = video.video_url;
                            link.download = `${video.title}.mp4`;
                            link.click();
                          }}
                          className="px-3 py-2 bg-gray-600 hover:bg-gray-700 text-foreground text-sm rounded-lg transition-colors flex items-center gap-1"
                        >
                          <ArrowDownTrayIcon className="h-4 w-4" />
                          Download
                        </button>
                        <button
                          onClick={() => deleteVideo(video.id)}
                          className="px-3 py-2 bg-red-600 hover:bg-red-700 text-foreground text-sm rounded-lg transition-colors flex items-center gap-1"
                          title="Delete video"
                        >
                          <TrashIcon className="h-4 w-4" />
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {activeTab === 'images' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {images.length === 0 ? (
            <div className="col-span-full">
              <Card>
                <div className="text-center py-8 text-muted-foreground">
                  <PhotoIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No images saved yet.</p>
                  <p className="text-sm">Generate and save images to see them here!</p>
                </div>
              </Card>
            </div>
          ) : (
            images.map((image, index) => (
              <Card 
                key={image.id} 
                className={`overflow-hidden ${!bulkDeleteMode ? 'cursor-pointer hover:ring-2 hover:ring-primary-500' : ''} transition-all ${
                  bulkDeleteMode && selectedItems.has(image.id) ? 'ring-2 ring-primary-500' : ''
                }`}
                onClick={() => !bulkDeleteMode && viewImage(index)}
              >
                {bulkDeleteMode && (
                  <div className="p-3 border-b border-gray-700">
                    <input
                      type="checkbox"
                      checked={selectedItems.has(image.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        toggleItemSelection(image.id);
                      }}
                      className="w-4 h-4 text-primary-600 bg-gray-700 border-gray-600 rounded focus:ring-primary-500"
                    />
                  </div>
                )}
                <div className="relative group">
                  <img
                    src={image.image_url}
                    alt={image.title}
                    className="w-full h-48 object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
                    <EyeIcon className="h-5 w-5 text-foreground" />
                  </div>
                </div>
                <div className="p-3">
                  <h3 className="text-sm font-semibold text-foreground truncate">
                    {image.title}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDate(image.saved_at)}
                  </p>
                  {image.tags && image.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {image.tags.slice(0, 3).map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-1 py-0.5 text-xs bg-gray-700 text-muted-foreground rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Voice Content */}
      {activeTab === 'voice' && (
        <div className="space-y-4">
          {voiceTranscripts.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-muted-foreground">
                <MicrophoneIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No voice transcripts yet.</p>
                <p className="text-sm">Record or upload audio to see transcripts here!</p>
              </div>
            </Card>
          ) : (
            voiceTranscripts.map((transcript) => (
              <Card key={transcript.id} className="hover:border-primary-500/50 transition-all">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <SpeakerWaveIcon className="h-5 w-5 text-primary-400" />
                      <span className="text-sm font-medium text-foreground">
                        {transcript.metadata?.output_type === 'conversation' ? 'Conversation' :
                         transcript.metadata?.output_type === 'command' ? 'Voice Command' :
                         'Voice Transcript'}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(transcript.created_at)}
                      </span>
                      {transcript.metadata?.duration && (
                        <span className="text-xs text-muted-foreground">
                          • {Math.round(transcript.metadata.duration / 60)}:{String(transcript.metadata.duration % 60).padStart(2, '0')}
                        </span>
                      )}
                    </div>
                    <div className="relative">
                      <p 
                        id={`transcript-${transcript.id}`} 
                        className={`text-sm ${transcript.content_text ? 'text-muted-foreground' : 'text-muted-foreground italic'} ${expandedTranscripts.has(transcript.id) ? '' : 'line-clamp-3'}`}
                      >
                        {transcript.content_text || 'No transcript content available (empty or failed to load)'}
                      </p>
                      {!expandedTranscripts.has(transcript.id) && transcript.content_text && transcript.content_text.length > 150 && (
                        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-dark-800 to-transparent pointer-events-none" />
                      )}
                    </div>
                    {transcript.tags && transcript.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {transcript.tags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs bg-dark-700 text-muted-foreground rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => createContentFromVoice(transcript.content_text, 'blog')}
                      className={`p-2 hover:bg-dark-700 rounded-lg transition-colors ${isCreatingContent ? 'opacity-50 cursor-not-allowed' : ''}`}
                      title="Create blog post"
                      disabled={isCreatingContent}
                    >
                      {isCreatingContent ? (
                        <div className="h-4 w-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <NewspaperIcon className="h-4 w-4 text-muted-foreground" />
                      )}
                    </button>
                    <button
                      onClick={() => createContentFromVoice(transcript.content_text, 'social')}
                      className={`p-2 hover:bg-dark-700 rounded-lg transition-colors ${isCreatingContent ? 'opacity-50 cursor-not-allowed' : ''}`}
                      title="Create social posts"
                      disabled={isCreatingContent}
                    >
                      {isCreatingContent ? (
                        <div className="h-4 w-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <HashtagIcon className="h-4 w-4 text-muted-foreground" />
                      )}
                    </button>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(transcript.content_text);
                        toast.success('Copied to clipboard');
                      }}
                      className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                      title="Copy transcript"
                    >
                      <DocumentTextIcon className="h-4 w-4 text-muted-foreground" />
                    </button>
                    <button
                      onClick={() => {
                        setExpandedTranscripts(prev => {
                          const newSet = new Set(prev);
                          if (newSet.has(transcript.id)) {
                            newSet.delete(transcript.id);
                          } else {
                            newSet.add(transcript.id);
                          }
                          return newSet;
                        });
                      }}
                      className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                      title={expandedTranscripts.has(transcript.id) ? "Collapse" : "Expand"}
                    >
                      <EyeIcon className={`h-4 w-4 ${expandedTranscripts.has(transcript.id) ? 'text-primary-400' : 'text-muted-foreground'}`} />
                    </button>
                    <button
                      onClick={() => deleteVoiceTranscript(transcript.id)}
                      className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                      title="Delete voice transcript"
                    >
                      <TrashIcon className="h-4 w-4 text-muted-foreground hover:text-red-500" />
                    </button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Podcasts Content */}
      {activeTab === 'podcasts' && (
        <div className="space-y-4">
          {podcasts.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-muted-foreground">
                <SpeakerWaveIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No podcast episodes yet.</p>
                <p className="text-sm">Create podcast scripts to see them here!</p>
              </div>
            </Card>
          ) : (
            podcasts.map((podcast) => (
              <Card key={podcast.id} className="hover:border-primary-500/50 transition-all">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <SpeakerWaveIcon className="h-5 w-5 text-primary-400" />
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-semibold text-foreground">
                          {podcast.title}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          podcast.is_published 
                            ? 'bg-green-500/20 text-green-300' 
                            : 'bg-yellow-500/20 text-yellow-300'
                        }`}>
                          {podcast.is_published ? 'Published' : 'Draft'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="text-sm text-muted-foreground mb-2">
                      <span className="font-medium text-foreground">{podcast.show_name}</span>
                      <span className="mx-2">•</span>
                      <span>S{podcast.season}E{podcast.episode}</span>
                      <span className="mx-2">•</span>
                      <span className="capitalize">{podcast.format}</span>
                      {podcast.duration > 0 && (
                        <>
                          <span className="mx-2">•</span>
                          <span>{Math.floor(podcast.duration / 60)}:{String(podcast.duration % 60).padStart(2, '0')}</span>
                        </>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Created {formatDate(podcast.created_at)}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => viewPodcast(podcast.id)}
                      className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                      title="View podcast details"
                    >
                      <EyeIcon className="h-4 w-4 text-muted-foreground" />
                    </button>
                    <button
                      onClick={async () => {
                        // Copy podcast script to clipboard
                        const currentPodcast = podcast;  // Use the podcast from the map loop
                        if (currentPodcast) {
                          let scriptContent = '';
                          if (currentPodcast.content?.script) {
                            scriptContent = currentPodcast.content.script;
                          } else if (currentPodcast.content?.content) {
                            scriptContent = currentPodcast.content.content;
                          } else if (typeof currentPodcast.content === 'string') {
                            scriptContent = currentPodcast.content;
                          } else {
                            // Try to fetch from library API if content not available
                            try {
                              const response = await apiClient.get(`/v1/content/library/${currentPodcast.id}/`);
                              if (response.data.content?.script) {
                                scriptContent = response.data.content.script;
                              } else if (response.data.content?.content) {
                                scriptContent = response.data.content.content;
                              } else if (typeof response.data.content === 'string') {
                                scriptContent = response.data.content;
                              }
                            } catch (error) {
                              Logger.error('Failed to fetch podcast content for copy', error);
                            }
                          }
                          if (scriptContent) {
                            navigator.clipboard.writeText(scriptContent);
                            toast.success('Podcast script copied to clipboard!');
                          } else {
                            toast.error('No podcast content to copy');
                          }
                        }
                      }}
                      className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                      title="Copy podcast script"
                    >
                      <DocumentDuplicateIcon className="h-4 w-4 text-muted-foreground" />
                    </button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Blog Viewer Modal */}
      {selectedBlogId && (
        <BlogViewer
          blogId={selectedBlogId}
          isOpen={blogViewerOpen}
          onClose={closeBlogViewer}
          onEdit={editBlog}
        />
      )}

      {/* Blog Editor Modal */}
      {editingBlog && (
        <BlogEditor
          blog={editingBlog}
          isOpen={blogEditorOpen}
          onClose={closeBlogEditor}
          onSaved={handleBlogSaved}
        />
      )}

      {/* Social Viewer Modal */}
      {selectedSocialId && (
        <SocialViewer
          socialPostId={selectedSocialId}
          isOpen={socialViewerOpen}
          onClose={closeSocialViewer}
        />
      )}

      {/* Image Viewer Modal */}
      {images.length > 0 && (
        <ImageViewer
          image={images[selectedImageIndex]}
          images={images}
          currentIndex={selectedImageIndex}
          isOpen={imageViewerOpen}
          onClose={closeImageViewer}
          onDelete={deleteImage}
        />
      )}

      {/* Video Player Modal */}
      {selectedVideo && videoPlayerOpen && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-6xl w-full">
            {/* Close Button */}
            <button
              onClick={closeVideoPlayer}
              className="absolute -top-12 right-0 text-foreground/80 hover:text-foreground p-2 z-10"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
            
            {/* Video Title */}
            <div className="text-foreground text-xl font-semibold mb-4 text-center">
              {selectedVideo.title}
            </div>
            
            {/* Video Player */}
            <div className="aspect-video bg-black rounded-lg overflow-hidden">
              <video
                key={selectedVideo.video_url}
                controls
                autoPlay
                className="w-full h-full object-contain"
                onError={(e) => {
                  console.error('Video playback error - URL may have expired');
                  // Check if it's a Runway ML URL with expired token
                  if (selectedVideo.video_url.includes('runwayml.com') || selectedVideo.video_url.includes('cloudfront.net')) {
                    toast.error('This video link has expired. Runway ML video URLs are only valid for a limited time after generation.', {
                      duration: 5000
                    });
                    // Mark this video as having an expired URL
                    setExpiredVideoUrls(prev => new Set(prev).add(selectedVideo.id));
                  } else {
                    toast.error('Failed to load video. The video file may not be available.');
                  }
                }}
              >
                <source src={selectedVideo.video_url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
            
            {/* Video Details */}
            <div className="mt-4 text-foreground space-y-2">
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>Duration: {selectedVideo.duration}s</span>
                <span className="capitalize">{selectedVideo.source_type.replace('_', ' ')}</span>
                <span>Saved {formatDate(selectedVideo.saved_at)}</span>
              </div>
              
              {selectedVideo.description && (
                <p className="text-muted-foreground text-sm">{selectedVideo.description}</p>
              )}
              
              <div className="space-y-1 text-sm">
                <div>
                  <span className="text-muted-foreground">Prompt: </span>
                  <span className="text-foreground">{selectedVideo.original_prompt}</span>
                </div>
                {selectedVideo.motion_prompt && (
                  <div>
                    <span className="text-muted-foreground">Motion: </span>
                    <span className="text-foreground">{selectedVideo.motion_prompt}</span>
                  </div>
                )}
              </div>
              
              {selectedVideo.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {selectedVideo.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-700 text-muted-foreground text-xs rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Podcast Viewer Modal */}
      {podcastViewerOpen && selectedPodcastId && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="bg-card rounded-xl border border-gray-700">
              {/* Header */}
              <div className="flex items-start justify-between p-6 border-b border-gray-700">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-foreground mb-2">
                    {podcasts.find(p => p.id === selectedPodcastId)?.title || 'Podcast Episode'}
                  </h2>
                  {podcasts.find(p => p.id === selectedPodcastId)?.metadata && (
                    <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                      {podcasts.find(p => p.id === selectedPodcastId)?.metadata.show_name && (
                        <span>Show: {podcasts.find(p => p.id === selectedPodcastId)?.metadata.show_name}</span>
                      )}
                      {podcasts.find(p => p.id === selectedPodcastId)?.metadata.duration && (
                        <span>Duration: {Math.round(podcasts.find(p => p.id === selectedPodcastId)?.metadata.duration / 60)} minutes</span>
                      )}
                      {podcasts.find(p => p.id === selectedPodcastId)?.metadata.format && (
                        <span>Format: {podcasts.find(p => p.id === selectedPodcastId)?.metadata.format}</span>
                      )}
                    </div>
                  )}
                </div>
                <button
                  onClick={closePodcastViewer}
                  className="ml-4 p-2 hover:bg-dark-700 rounded-lg transition-colors"
                >
                  <XMarkIcon className="h-5 w-5 text-muted-foreground" />
                </button>
              </div>
              
              {/* Content */}
              <div className="p-6 max-h-[60vh] overflow-y-auto">
                <div className="prose prose-invert max-w-none">
                  <pre className="whitespace-pre-wrap font-sans text-foreground">
                    {podcastContent}
                  </pre>
                </div>
              </div>
              
              {/* Actions */}
              <div className="flex justify-end gap-3 p-6 border-t border-gray-700">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(podcastContent);
                    toast.success('Podcast script copied to clipboard!');
                  }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-foreground rounded-lg transition-colors flex items-center gap-2"
                >
                  <DocumentDuplicateIcon className="h-4 w-4" />
                  Copy Script
                </button>
                <button
                  onClick={() => {
                    const blob = new Blob([podcastContent], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `podcast-${selectedPodcastId}.txt`;
                    a.click();
                    URL.revokeObjectURL(url);
                    toast.success('Podcast script downloaded!');
                  }}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-foreground rounded-lg transition-colors flex items-center gap-2"
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content Transform Modal */}
      {transformingBlog && (
        <ContentTransformModal
          isOpen={!!transformingBlog}
          onClose={() => setTransformingBlog(null)}
          blog={transformingBlog}
          onSuccess={() => {
            // Reload data to show newly created content
            loadContent();
          }}
        />
      )}
    </div>
  );
}