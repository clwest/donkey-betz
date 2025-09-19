import { useState, useEffect } from 'react';
import { contentService } from '../../../services/content.service';
import { Logger } from '../../../utils/logger';
import { toast } from 'sonner';
import { calculateReadingTime } from '../../../utils/readingTime';
import ReactMarkdown from 'react-markdown';
import { 
  XMarkIcon, 
  PencilIcon, 
  DocumentDuplicateIcon,
  HeartIcon,
  ShareIcon,
  CalendarIcon,
  TagIcon,
  DocumentTextIcon,
  ClockIcon,
  GlobeAltIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { FeedbackWidget } from '../../feedback/FeedbackWidget';

interface BlogPost {
  id: number;
  title: string;
  content: string;
  word_count: number;
  tags: string[];
  tone: string;
  length: string;
  created_at: string;
  meta_description?: string;
  is_live?: boolean;
}

interface BlogViewerProps {
  blogId: number;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: (blog: BlogPost) => void;
}

export function BlogViewer({ blogId, isOpen, onClose, onEdit }: BlogViewerProps) {
  const [blog, setBlog] = useState<BlogPost | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && blogId) {
      loadBlog();
    }
  }, [isOpen, blogId]);

  const loadBlog = async () => {
    setLoading(true);
    try {
      Logger.component('BlogViewer', `Loading blog ${blogId}`);
      const response = await contentService.getBlogPost(blogId);
      const blogData = response.blog_post || response;
      
      // Parse embedded title and content if needed
      let processedBlog = { ...blogData };
      
      if (blogData.content && typeof blogData.content === 'string') {
        const content = blogData.content;
        
        // Extract title from **TITLE: ...** format
        const titleMatch = content.match(/\*\*TITLE:\s*([^\*]+)\*\*/);
        if (titleMatch && titleMatch[1]) {
          processedBlog.title = titleMatch[1].trim();
        }
        
        // Extract meta description from **META_DESCRIPTION:** format
        const metaMatch = content.match(/\*\*META_DESCRIPTION:\*\*\s*([^\n]+)/);
        if (metaMatch && metaMatch[1]) {
          processedBlog.meta_description = metaMatch[1].trim();
        }
        
        // Extract tags from TAGS: at the end
        const tagsMatch = content.match(/TAGS:\s*(.+)$/);
        if (tagsMatch && tagsMatch[1]) {
          const extractedTags = tagsMatch[1].split(',').map(tag => tag.trim()).filter(tag => tag);
          if (extractedTags.length > 0) {
            processedBlog.tags = [...(processedBlog.tags || []), ...extractedTags];
          }
        }
        
        // Clean content by removing metadata sections
        let cleanedContent = content
          .replace(/\*\*TITLE:\s*[^\*]+\*\*\n?\n?/, '')
          .replace(/\*\*META_DESCRIPTION:\*\*\s*[^\n]+\n?\n?---\n?\n?/, '')
          .replace(/---\s*\n?\n?TAGS:\s*.+$/, '')
          .trim();
          
        processedBlog.content = cleanedContent;
      }
      
      setBlog(processedBlog);
      Logger.state('BlogViewer', 'Blog loaded and processed', processedBlog);
    } catch (error: any) {
      Logger.error('BlogViewer.loadBlog', error);
      toast.error('Failed to load blog post');
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Content copied to clipboard!');
    } catch (error) {
      Logger.error('BlogViewer.copyToClipboard', error);
      toast.error('Failed to copy to clipboard');
    }
  };

  const togglePublishStatus = async () => {
    if (!blog) return;
    
    try {
      const newStatus = !blog.is_live;
      Logger.component('BlogViewer', `Toggling blog publish status`, { blogId: blog.id, newStatus });
      
      await contentService.toggleBlogLiveStatus(blog.id, newStatus);
      
      // Update local state
      setBlog({ ...blog, is_live: newStatus });
      
      if (newStatus) {
        toast.success('Blog published successfully! It is now visible on the public blog page.');
      } else {
        toast.success('Blog unpublished. It is now a draft and not visible publicly.');
      }
      
      Logger.state('BlogViewer', 'Blog publish status updated', { blogId: blog.id, newStatus });
    } catch (error: any) {
      Logger.error('BlogViewer.togglePublishStatus', error);
      toast.error('Failed to update publish status');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg w-full max-w-4xl h-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <DocumentTextIcon className="h-6 w-6 text-primary-400" />
            <h2 className="text-xl font-semibold text-foreground">Blog Post</h2>
          </div>
          <div className="flex items-center gap-2">
            {blog && onEdit && (
              <button
                onClick={() => onEdit(blog)}
                className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                title="Edit blog post"
              >
                <PencilIcon className="h-5 w-5" />
              </button>
            )}
            <button
              onClick={() => blog && copyToClipboard(blog.content)}
              className="p-2 text-muted-foreground hover:text-foreground transition-colors"
              title="Copy content"
              disabled={!blog}
            >
              <DocumentDuplicateIcon className="h-5 w-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-muted-foreground hover:text-foreground transition-colors"
              title="Close"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : blog ? (
            <div className="p-6 space-y-6">
              {/* Title */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h1 className="text-3xl font-bold text-foreground leading-tight">
                    {blog.title}
                  </h1>
                  <span className={`px-3 py-1 text-sm rounded-full ${
                    blog.is_live 
                      ? 'bg-green-500/20 text-green-300' 
                      : 'bg-yellow-500/20 text-yellow-300'
                  }`}>
                    {blog.is_live ? '🌍 Published' : '📝 Draft'}
                  </span>
                </div>
                
                {/* Metadata */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
                  <div className="flex items-center gap-1">
                    <CalendarIcon className="h-4 w-4" />
                    {formatDate(blog.created_at)}
                  </div>
                  <div className="flex items-center gap-1">
                    <ClockIcon className="h-4 w-4" />
                    {calculateReadingTime(blog.content).text}
                  </div>
                  <div className="flex items-center gap-1">
                    <DocumentTextIcon className="h-4 w-4" />
                    {blog.word_count} words
                  </div>
                  <span className="capitalize px-2 py-1 bg-primary-500/20 text-primary-300 rounded">
                    {blog.tone} tone
                  </span>
                  <span className="capitalize px-2 py-1 bg-gray-700 text-muted-foreground rounded">
                    {blog.length} length
                  </span>
                </div>

                {/* Tags */}
                {blog.tags && blog.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    <TagIcon className="h-4 w-4 text-muted-foreground mt-1" />
                    {blog.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 text-sm bg-primary-500/20 text-primary-300 rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Meta Description */}
              {blog.meta_description && (
                <Card className="bg-blue-500/10 border-blue-500/20">
                  <div className="p-4">
                    <h3 className="text-sm font-semibold text-blue-300 mb-2">Meta Description</h3>
                    <p className="text-blue-100 text-sm">{blog.meta_description}</p>
                  </div>
                </Card>
              )}

              {/* Content */}
              <div className="prose prose-invert prose-lg max-w-none">
                <ReactMarkdown 
                  components={{
                    img: ({ node, ...props }) => {
                      // Don't render img if src is empty or undefined
                      if (!props.src || props.src.trim() === '') {
                        return null;
                      }
                      return (
                        <img 
                          {...props} 
                          className="rounded-lg max-w-full h-auto my-4" 
                          loading="lazy" 
                        />
                      );
                    },
                    p: ({ node, ...props }) => (
                      <p {...props} className="mb-4 text-foreground" />
                    ),
                    h1: ({ node, ...props }) => (
                      <h1 {...props} className="text-3xl font-bold mb-4 text-foreground" />
                    ),
                    h2: ({ node, ...props }) => (
                      <h2 {...props} className="text-2xl font-bold mb-3 text-foreground" />
                    ),
                    h3: ({ node, ...props }) => (
                      <h3 {...props} className="text-xl font-bold mb-2 text-foreground" />
                    ),
                  }}
                >
                  {blog.content}
                </ReactMarkdown>
              </div>

              {/* Feedback Section */}
              <div className="mt-4">
                <FeedbackWidget
                  contentType="blog"
                  contentId={blog.id}
                  contentTitle={blog.title}
                  inline={true}
                  showStats={true}
                  onFeedbackSubmit={() => {
                    Logger.state('BlogViewer', 'Feedback submitted successfully');
                  }}
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-border">
                <button
                  onClick={togglePublishStatus}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    blog.is_live
                      ? 'bg-yellow-600 text-foreground hover:bg-yellow-700'
                      : 'bg-green-600 text-foreground hover:bg-green-700'
                  }`}
                >
                  {blog.is_live ? (
                    <>
                      <EyeSlashIcon className="h-4 w-4" />
                      Unpublish
                    </>
                  ) : (
                    <>
                      <GlobeAltIcon className="h-4 w-4" />
                      Publish to Blog
                    </>
                  )}
                </button>

                <button
                  onClick={() => copyToClipboard(blog.content)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-foreground rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <DocumentDuplicateIcon className="h-4 w-4" />
                  Copy Full Content
                </button>
                
                {onEdit && (
                  <button
                    onClick={() => onEdit(blog)}
                    className="flex items-center gap-2 px-4 py-2 bg-dark-600 text-foreground rounded-lg hover:bg-dark-500 transition-colors"
                  >
                    <PencilIcon className="h-4 w-4" />
                    Edit Post
                  </button>
                )}

                {blog.is_live && (
                  <button
                    onClick={() => {
                      const publicUrl = `${window.location.origin}/blog/${blog.id}`;
                      navigator.clipboard.writeText(publicUrl);
                      toast.success('Public blog link copied to clipboard!');
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-foreground rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    <ShareIcon className="h-4 w-4" />
                    Share Public Link
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-center text-muted-foreground">
                <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Blog post not found</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}