import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { contentService } from '../../services/content.service';
import { Logger } from '../../utils/logger';
import { toast } from 'sonner';
import { calculateReadingTime } from '../../utils/readingTime';
import { findRelatedPosts, formatSimilarityReasons } from '../../utils/relatedPosts';
import { SEO, extractImageFromContent } from '../../components/SEO/SEO';
import ReactMarkdown from 'react-markdown';
import {
  CalendarIcon,
  TagIcon,
  DocumentTextIcon,
  ArrowLeftIcon,
  ShareIcon,
  HeartIcon,
  EyeIcon,
  ClockIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

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
  author?: string;
  views?: number;
  likes?: number;
  is_liked?: boolean;
  is_live?: boolean;
}

export function PublicBlogPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [blog, setBlog] = useState<BlogPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);
  const [relatedPosts, setRelatedPosts] = useState<any[]>([]);
  const [loadingRelated, setLoadingRelated] = useState(false);

  useEffect(() => {
    if (id) {
      loadBlog(parseInt(id));
    }
  }, [id]);

  const loadBlog = async (blogId: number) => {
    setLoading(true);
    try {
      Logger.component('PublicBlogPage', `Loading public blog ${blogId}`);
      const response = await contentService.getBlogPost(blogId);
      const blogData = response.blog_post || response;
      
      // Parse embedded content like in BlogViewer
      let processedBlog = { ...blogData };
      
      if (blogData.content && typeof blogData.content === 'string') {
        const content = blogData.content;
        
        // Extract title from **TITLE: ...** format
        const titleMatch = content.match(/\*\*TITLE:\s*([^\*]+)\*\*/);
        if (titleMatch && titleMatch[1]) {
          processedBlog.title = titleMatch[1].trim();
        }
        
        // Extract meta description
        const metaMatch = content.match(/\*\*META_DESCRIPTION:\*\*\s*([^\n]+)/);
        if (metaMatch && metaMatch[1]) {
          processedBlog.meta_description = metaMatch[1].trim();
        }
        
        // Extract tags
        const tagsMatch = content.match(/TAGS:\s*(.+)$/);
        if (tagsMatch && tagsMatch[1]) {
          const extractedTags = tagsMatch[1].split(',').map(tag => tag.trim()).filter(tag => tag);
          if (extractedTags.length > 0) {
            processedBlog.tags = [...(processedBlog.tags || []), ...extractedTags];
          }
        }
        
        // Clean content
        let cleanedContent = content
          .replace(/\*\*TITLE:\s*[^\*]+\*\*\n?\n?/, '')
          .replace(/\*\*META_DESCRIPTION:\*\*\s*[^\n]+\n?\n?---\n?\n?/, '')
          .replace(/---\s*\n?\n?TAGS:\s*.+$/, '')
          .trim();
          
        processedBlog.content = cleanedContent;
      }
      
      // Check if blog is live (published)
      if (processedBlog.is_live === false) {
        Logger.warn('PublicBlogPage', 'Attempting to access unpublished blog', { blogId });
        toast.error('This blog post is not published yet');
        navigate('/blog');
        return;
      }
      
      setBlog(processedBlog);
      setLiked(processedBlog.is_liked || false);
      setLikesCount(processedBlog.likes || 0);
      
      // Load related posts after the main blog is loaded
      loadRelatedPosts(processedBlog);
      
      Logger.state('PublicBlogPage', 'Public blog loaded', processedBlog);
    } catch (error: any) {
      Logger.error('PublicBlogPage.loadBlog', error);
      toast.error('Failed to load blog post');
      navigate('/blog');
    } finally {
      setLoading(false);
    }
  };

  const loadRelatedPosts = async (currentBlog: BlogPost) => {
    setLoadingRelated(true);
    try {
      Logger.component('PublicBlogPage', 'Loading related posts');
      const blogData = await contentService.getBlogList();
      const allBlogs = (blogData.blog_posts || []).map((blog: BlogPost) => {
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

      const related = findRelatedPosts(currentBlog, allBlogs, 3);
      setRelatedPosts(related);
      
      Logger.state('PublicBlogPage', 'Related posts loaded', { count: related.length });
    } catch (error: any) {
      Logger.error('PublicBlogPage.loadRelatedPosts', error);
      // Fail silently for related posts
    } finally {
      setLoadingRelated(false);
    }
  };

  const handleLike = async () => {
    if (!blog) return;
    
    try {
      // TODO: Implement like API endpoint
      const newLiked = !liked;
      setLiked(newLiked);
      setLikesCount(prev => newLiked ? prev + 1 : prev - 1);
      
      toast.success(newLiked ? '❤️ Liked!' : 'Like removed');
      Logger.component('PublicBlogPage', 'Blog liked', { blogId: blog.id, liked: newLiked });
    } catch (error: any) {
      Logger.error('PublicBlogPage.handleLike', error);
      toast.error('Failed to update like');
    }
  };

  const handleShare = async () => {
    if (!blog) return;
    
    try {
      const shareUrl = `${window.location.origin}/blog/${blog.id}`;
      await navigator.clipboard.writeText(shareUrl);
      toast.success('Blog link copied to clipboard!');
      Logger.component('PublicBlogPage', 'Blog shared', { url: shareUrl });
    } catch (error) {
      toast.error('Failed to copy link');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };


  if (loading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (!blog) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="text-center text-gray-400">
          <DocumentTextIcon className="h-16 w-16 mx-auto mb-4 opacity-50" />
          <h1 className="text-2xl font-bold mb-2">Blog post not found</h1>
          <p className="mb-4">The blog post you're looking for doesn't exist or has been removed.</p>
          <button
            onClick={() => navigate('/blog')}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Browse All Blogs
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* SEO Meta Tags */}
      {blog && (
        <SEO
          title={`${blog.title} - Donkey Betz Blog`}
          description={blog.meta_description || blog.content.substring(0, 160)}
          keywords={blog.tags}
          image={extractImageFromContent(blog.content) || undefined}
          url={`${window.location.origin}/blog/${blog.id}`}
          type="article"
          publishedTime={blog.created_at}
          author="Donkey Betz"
          siteName="Donkey Betz"
        />
      )}
    
    <div className="min-h-screen bg-dark-900">
      {/* Header */}
      <header className="bg-dark-800 border-b border-dark-700">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/blog')}
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeftIcon className="h-4 w-4" />
                Back to Blogs
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <DocumentTextIcon className="h-4 w-4" />
                Donkey Betz
              </button>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={handleLike}
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 transition-colors"
              >
                {liked ? (
                  <HeartSolidIcon className="h-5 w-5 text-red-500" />
                ) : (
                  <HeartIcon className="h-5 w-5 text-gray-400" />
                )}
                <span className="text-sm text-gray-300">{likesCount}</span>
              </button>
              
              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-3 py-2 text-gray-400 hover:text-white rounded-lg hover:bg-dark-700 transition-colors"
              >
                <ShareIcon className="h-5 w-5" />
                <span className="text-sm">Share</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <article>
          {/* Title and Meta */}
          <header className="mb-8">
            <h1 className="text-4xl font-bold text-white leading-tight mb-4">
              {blog.title}
            </h1>
            
            {blog.meta_description && (
              <p className="text-xl text-gray-300 mb-6 leading-relaxed">
                {blog.meta_description}
              </p>
            )}
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 mb-6">
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
              <div className="flex items-center gap-1">
                <EyeIcon className="h-4 w-4" />
                {blog.views || 0} views
              </div>
            </div>

            {blog.tags && blog.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-6">
                <TagIcon className="h-4 w-4 text-gray-400 mt-1" />
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
          </header>

          {/* Blog Content */}
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
                  <p {...props} className="mb-4 text-gray-100 leading-relaxed" />
                ),
                h1: ({ node, ...props }) => (
                  <h1 {...props} className="text-3xl font-bold mb-4 text-white mt-8" />
                ),
                h2: ({ node, ...props }) => (
                  <h2 {...props} className="text-2xl font-bold mb-3 text-white mt-6" />
                ),
                h3: ({ node, ...props }) => (
                  <h3 {...props} className="text-xl font-semibold mb-2 text-white mt-5" />
                ),
                em: ({ node, ...props }) => (
                  <em {...props} className="italic text-gray-100" />
                ),
                strong: ({ node, ...props }) => (
                  <strong {...props} className="font-bold text-white" />
                ),
              }}
            >
              {blog.content}
            </ReactMarkdown>
          </div>

          {/* Footer */}
          <footer className="mt-12 pt-8 border-t border-dark-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={handleLike}
                  className="flex items-center gap-2 px-4 py-2 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors"
                >
                  {liked ? (
                    <HeartSolidIcon className="h-5 w-5 text-red-500" />
                  ) : (
                    <HeartIcon className="h-5 w-5 text-gray-400" />
                  )}
                  <span className="text-white">{liked ? 'Liked' : 'Like'}</span>
                </button>
                
                <button
                  onClick={handleShare}
                  className="flex items-center gap-2 px-4 py-2 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors"
                >
                  <ShareIcon className="h-5 w-5 text-gray-400" />
                  <span className="text-white">Share</span>
                </button>
              </div>
              
              <div className="text-sm text-gray-400">
                Published on {formatDate(blog.created_at)}
              </div>
            </div>
          </footer>
        </article>

        {/* Related Posts */}
        {relatedPosts.length > 0 && (
          <section className="mt-16 pt-12 border-t border-dark-700">
            <div className="flex items-center gap-2 mb-8">
              <SparklesIcon className="h-6 w-6 text-primary-400" />
              <h2 className="text-2xl font-bold text-white">Related Posts</h2>
            </div>
            
            {loadingRelated ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {relatedPosts.map((post) => (
                  <article
                    key={post.id}
                    onClick={() => navigate(`/blog/${post.id}`)}
                    className="bg-dark-800 rounded-lg overflow-hidden hover:bg-dark-700 transition-all cursor-pointer group border border-dark-700 hover:border-primary-500/50"
                  >
                    <div className="p-6">
                      <h3 className="text-lg font-semibold text-white mb-3 group-hover:text-primary-300 transition-colors line-clamp-2">
                        {post.title}
                      </h3>
                      
                      <p className="text-gray-300 text-sm mb-4 line-clamp-2 leading-relaxed">
                        {post.meta_description || post.preview}
                      </p>

                      <div className="flex items-center gap-3 text-xs text-gray-400 mb-3">
                        <div className="flex items-center gap-1">
                          <ClockIcon className="h-3 w-3" />
                          {calculateReadingTime(post.content || post.preview || '').text}
                        </div>
                        <div className="flex items-center gap-1">
                          <DocumentTextIcon className="h-3 w-3" />
                          {post.word_count} words
                        </div>
                      </div>

                      {post.tags && post.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-3">
                          {post.tags.slice(0, 2).map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 text-xs bg-primary-500/20 text-primary-300 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="text-xs text-gray-500">
                        {formatSimilarityReasons(post.similarity_reasons)}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
    </>
  );
}