import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contentService } from '../../services/content.service';
import { Logger } from '../../utils/logger';
import { toast } from 'sonner';
import { getReadingTimeFromWordCount } from '../../utils/readingTime';
import { categorizeContent, getCategoryById, getPopularCategories } from '../../utils/blogCategories';
import type { Category } from '../../utils/blogCategories';
import { SEO } from '../../components/SEO/SEO';
import {
  CalendarIcon,
  TagIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  HeartIcon,
  ClockIcon,
  FunnelIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

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
  meta_description?: string;
  views?: number;
  likes?: number;
  category?: string;
  is_live?: boolean;
  is_deleted?: boolean;
}

export function PublicBlogListPage() {
  const navigate = useNavigate();
  const [blogs, setBlogs] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'popular'>('newest');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadBlogs();
  }, []);

  const loadBlogs = async () => {
    setLoading(true);
    try {
      Logger.component('PublicBlogListPage', 'Loading public blogs');
      const blogData = await contentService.getBlogList();
      const blogs = (blogData.blog_posts || []).map((blog: BlogPost) => {
        // Parse embedded title from content if the title is generic
        let processedBlog = { ...blog };
        if (blog.title === 'Generated Blog Post' && blog.preview) {
          const titleMatch = blog.preview.match(/\*\*TITLE:\s*([^\*]+)\*\*/);
          if (titleMatch && titleMatch[1]) {
            processedBlog.title = titleMatch[1].trim();
          }
        }
        
        // Auto-categorize the blog based on content
        const detectedCategory = categorizeContent(
          processedBlog.title, 
          processedBlog.tags || [], 
          processedBlog.tone || ''
        );
        if (detectedCategory) {
          processedBlog.category = detectedCategory;
        }
        
        return processedBlog;
      });
      
      // Only show published blogs (is_live = true) and not deleted
      const liveBlogs = blogs.filter(blog => blog.is_live !== false && !blog.is_deleted);
      setBlogs(liveBlogs);
      
      Logger.state('PublicBlogListPage', 'Public blogs loaded', { count: blogs.length });
    } catch (error: any) {
      Logger.error('PublicBlogListPage.loadBlogs', error);
      toast.error('Failed to load blog posts');
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

  const getAllTags = () => {
    const tagSet = new Set<string>();
    blogs.forEach(blog => {
      blog.tags?.forEach(tag => tagSet.add(tag));
    });
    return Array.from(tagSet).sort();
  };

  const filteredAndSortedBlogs = (() => {
    let filtered = blogs.filter(blog => {
      const matchesSearch = searchQuery === '' || 
        blog.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        blog.preview.toLowerCase().includes(searchQuery.toLowerCase()) ||
        blog.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      
      const matchesTag = selectedTag === null || blog.tags?.includes(selectedTag);
      const matchesCategory = selectedCategory === null || blog.category === selectedCategory;
      
      return matchesSearch && matchesTag && matchesCategory;
    });

    // Sort the filtered results
    switch (sortBy) {
      case 'oldest':
        return filtered.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      case 'popular':
        return filtered.sort((a, b) => ((b.views || 0) + (b.likes || 0)) - ((a.views || 0) + (a.likes || 0)));
      case 'newest':
      default:
        return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }
  })();

  const handleBlogClick = (blogId: number) => {
    navigate(`/blog/${blogId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // Generate dynamic SEO based on current filters
  const generateSEOData = () => {
    let title = 'Donkey Betz - Blog';
    let description = 'Discover insights, stories, and AI-powered content from Donkey Betz';
    let keywords = ['AI', 'content', 'blog', 'artificial intelligence', 'writing'];

    if (selectedCategory) {
      const category = getCategoryById(selectedCategory);
      if (category) {
        title = `${category.name} Articles - Donkey Betz Blog`;
        description = `${category.description} - Browse our collection of ${category.name.toLowerCase()} articles and insights`;
        keywords.push(category.name.toLowerCase());
      }
    }

    if (selectedTag) {
      title = `#${selectedTag} - Donkey Betz Blog`;
      description = `Articles tagged with #${selectedTag} - Explore related content and insights`;
      keywords.push(selectedTag);
    }

    if (searchQuery) {
      title = `Search: "${searchQuery}" - Donkey Betz Blog`;
      description = `Search results for "${searchQuery}" on our blog`;
    }

    return { title, description, keywords };
  };

  const seoData = generateSEOData();

  return (
    <>
      {/* SEO Meta Tags */}
      <SEO
        title={seoData.title}
        description={seoData.description}
        keywords={seoData.keywords}
        url={`${window.location.origin}/blog`}
        type="website"
        siteName="Donkey Betz"
      />
      
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-4xl font-bold text-foreground">Our Blog</h1>
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-foreground rounded-lg hover:bg-primary-700 transition-colors"
              >
                <DocumentTextIcon className="h-4 w-4" />
                Donkey Betz
              </button>
            </div>
            <p className="text-xl text-muted-foreground">
              Discover insights, stories, and knowledge from our content creators
            </p>
          </div>

          {/* Search and Filters */}
          <div className="space-y-4">
            {/* Main Search Bar */}
            <div className="flex flex-col md:flex-row gap-4 items-center justify-center">
              <div className="relative flex-1 max-w-lg">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search blogs..."
                  className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div className="flex gap-2">
                {/* Sort Dropdown */}
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'newest' | 'oldest' | 'popular')}
                  className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="popular">Most Popular</option>
                </select>

                {/* Advanced Filters Toggle */}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    showFilters || selectedCategory || selectedTag
                      ? 'bg-primary-500 text-foreground'
                      : 'bg-dark-700 text-muted-foreground hover:bg-dark-600'
                  }`}
                >
                  <FunnelIcon className="h-4 w-4" />
                  Filters
                  {(selectedCategory || selectedTag) && (
                    <span className="bg-white/20 rounded-full px-1.5 py-0.5 text-xs">
                      {(selectedCategory ? 1 : 0) + (selectedTag ? 1 : 0)}
                    </span>
                  )}
                </button>
              </div>
            </div>

            {/* Advanced Filters Panel */}
            {showFilters && (
              <div className="bg-card/50 rounded-lg p-4 border border-border">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-foreground">Advanced Filters</h3>
                  <button
                    onClick={() => {
                      setSelectedCategory(null);
                      setSelectedTag(null);
                      setShowFilters(false);
                    }}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>

                <div className="space-y-4">
                  {/* Categories */}
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Categories</h4>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => setSelectedCategory(null)}
                        className={`px-3 py-1 text-sm rounded-full transition-colors ${
                          selectedCategory === null
                            ? 'bg-primary-500 text-foreground'
                            : 'bg-dark-700 text-muted-foreground hover:bg-dark-600'
                        }`}
                      >
                        All Categories
                      </button>
                      {getPopularCategories(blogs).map(({ category, count }) => (
                        <button
                          key={category.id}
                          onClick={() => setSelectedCategory(selectedCategory === category.id ? null : category.id)}
                          className={`flex items-center gap-1 px-3 py-1 text-sm rounded-full transition-colors ${
                            selectedCategory === category.id
                              ? `${category.bgColor} ${category.color} ring-1 ring-current`
                              : 'bg-dark-700 text-muted-foreground hover:bg-dark-600'
                          }`}
                        >
                          <span>{category.icon}</span>
                          {category.name}
                          <span className="text-xs opacity-75">({count})</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Tags */}
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Popular Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => setSelectedTag(null)}
                        className={`px-3 py-1 text-sm rounded-full transition-colors ${
                          selectedTag === null
                            ? 'bg-primary-500 text-foreground'
                            : 'bg-dark-700 text-muted-foreground hover:bg-dark-600'
                        }`}
                      >
                        All Tags
                      </button>
                      {getAllTags().slice(0, 10).map(tag => (
                        <button
                          key={tag}
                          onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
                          className={`px-3 py-1 text-sm rounded-full transition-colors ${
                            selectedTag === tag
                              ? 'bg-primary-500 text-foreground'
                              : 'bg-dark-700 text-muted-foreground hover:bg-dark-600'
                          }`}
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Active Filters Display */}
            {(selectedCategory || selectedTag) && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Active filters:</span>
                {selectedCategory && (
                  <span className="flex items-center gap-1 px-2 py-1 bg-primary-500/20 text-primary-300 rounded-full">
                    {getCategoryById(selectedCategory)?.icon} {getCategoryById(selectedCategory)?.name}
                    <button onClick={() => setSelectedCategory(null)} className="hover:text-foreground">
                      <XMarkIcon className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {selectedTag && (
                  <span className="flex items-center gap-1 px-2 py-1 bg-primary-500/20 text-primary-300 rounded-full">
                    #{selectedTag}
                    <button onClick={() => setSelectedTag(null)} className="hover:text-foreground">
                      <XMarkIcon className="h-3 w-3" />
                    </button>
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Blog Grid */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {filteredAndSortedBlogs.length === 0 ? (
          <div className="text-center py-16">
            <DocumentTextIcon className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-muted-foreground mb-2">
              {searchQuery || selectedTag || selectedCategory ? 'No blogs found' : 'No blogs published yet'}
            </h2>
            <p className="text-muted-foreground">
              {searchQuery || selectedTag || selectedCategory
                ? 'Try adjusting your search or filter criteria' 
                : 'Check back soon for new content!'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedBlogs.map((blog) => (
              <article
                key={blog.id}
                onClick={() => handleBlogClick(blog.id)}
                className="bg-card rounded-lg overflow-hidden hover:bg-dark-700 transition-all cursor-pointer group border border-border hover:border-primary-500/50"
              >
                <div className="p-6">
                  {/* Category Badge */}
                  {blog.category && (
                    <div className="mb-3">
                      {(() => {
                        const category = getCategoryById(blog.category);
                        return category ? (
                          <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full ${category.bgColor} ${category.color}`}>
                            {category.icon} {category.name}
                          </span>
                        ) : null;
                      })()}
                    </div>
                  )}

                  <h2 className="text-xl font-semibold text-foreground mb-3 group-hover:text-primary-300 transition-colors line-clamp-2">
                    {stripMarkdown(blog.title)}
                  </h2>
                  
                  <p className="text-muted-foreground text-sm mb-4 line-clamp-3 leading-relaxed">
                    {stripMarkdown(blog.meta_description || blog.preview)}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                    <div className="flex items-center gap-1">
                      <CalendarIcon className="h-3 w-3" />
                      {formatDate(blog.created_at)}
                    </div>
                    <div className="flex items-center gap-1">
                      <ClockIcon className="h-3 w-3" />
                      {getReadingTimeFromWordCount(blog.word_count).text}
                    </div>
                    <div className="flex items-center gap-1">
                      <DocumentTextIcon className="h-3 w-3" />
                      {blog.word_count} words
                    </div>
                    <div className="flex items-center gap-1">
                      <EyeIcon className="h-3 w-3" />
                      {blog.views || 0}
                    </div>
                    <div className="flex items-center gap-1">
                      <HeartIcon className="h-3 w-3" />
                      {blog.likes || 0}
                    </div>
                  </div>

                  {blog.tags && blog.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {blog.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-primary-500/20 text-primary-300 rounded"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedTag(tag);
                          }}
                        >
                          {tag}
                        </span>
                      ))}
                      {blog.tags.length > 3 && (
                        <span className="px-2 py-1 text-xs bg-gray-700 text-muted-foreground rounded">
                          +{blog.tags.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div className="px-6 py-3 bg-background/50 border-t border-border">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground capitalize">
                      {blog.tone} • {blog.length}
                    </span>
                    <span className="text-xs text-primary-400 group-hover:text-primary-300">
                      Read more →
                    </span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}

        {/* Stats */}
        {filteredAndSortedBlogs.length > 0 && (
          <div className="mt-12 text-center text-muted-foreground text-sm">
            Showing {filteredAndSortedBlogs.length} of {blogs.length} blog posts
          </div>
        )}
      </main>
    </div>
    </>
  );
}