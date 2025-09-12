import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Calendar, 
  User, 
  Clock, 
  ArrowRight, 
  TrendingUp,
  Filter,
  BookOpen,
  Heart,
  MessageCircle,
  Share2
} from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import api from '@/services/api';

interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  author: {
    name: string;
    avatar?: string;
  };
  category: string;
  tags: string[];
  readTime: number;
  likes: number;
  comments: number;
  imageUrl?: string;
  publishedAt: string;
  featured: boolean;
}

const BlogsPage: React.FC = () => {
  const navigate = useNavigate();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [filteredPosts, setFilteredPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    fetchBlogPosts();
  }, []);

  useEffect(() => {
    filterPosts();
  }, [searchQuery, selectedCategory, posts]);

  const fetchBlogPosts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/content/blogs/public/');
      
      // If no real data, use mock data
      const blogPosts = response.data?.results || getMockPosts();
      setPosts(blogPosts);
      
      // Extract unique categories
      const uniqueCategories = [...new Set(blogPosts.map((post: BlogPost) => post.category))];
      setCategories(uniqueCategories);
    } catch (error) {
      console.error('Error fetching blogs:', error);
      // Use mock data as fallback
      const mockPosts = getMockPosts();
      setPosts(mockPosts);
      const uniqueCategories = [...new Set(mockPosts.map(post => post.category))];
      setCategories(uniqueCategories);
    } finally {
      setLoading(false);
    }
  };

  const getMockPosts = (): BlogPost[] => [
    {
      id: '1',
      title: 'Mastering AI Content Generation with GPT-5',
      slug: 'mastering-ai-content-generation-gpt5',
      excerpt: 'Discover the latest techniques for creating high-quality content using GPT-5 and advanced prompt engineering strategies.',
      content: '',
      author: { name: 'Sarah Chen' },
      category: 'AI & Technology',
      tags: ['GPT-5', 'AI', 'Content Creation'],
      readTime: 8,
      likes: 245,
      comments: 32,
      imageUrl: 'https://picsum.photos/seed/1/800/400',
      publishedAt: new Date().toISOString(),
      featured: true
    },
    {
      id: '2',
      title: 'Sports Betting Analytics: The Kelly Criterion Explained',
      slug: 'kelly-criterion-sports-betting',
      excerpt: 'Learn how to optimize your betting strategy using the Kelly Criterion for maximum long-term growth.',
      content: '',
      author: { name: 'Mike Johnson' },
      category: 'Sports Analytics',
      tags: ['Betting', 'Kelly Criterion', 'Analytics'],
      readTime: 12,
      likes: 189,
      comments: 28,
      imageUrl: 'https://picsum.photos/seed/2/800/400',
      publishedAt: new Date(Date.now() - 86400000).toISOString(),
      featured: true
    },
    {
      id: '3',
      title: 'Building Multi-Agent Systems for Complex Tasks',
      slug: 'multi-agent-systems',
      excerpt: 'Explore how orchestrating multiple AI agents can solve complex problems more effectively than single models.',
      content: '',
      author: { name: 'Alex Rivera' },
      category: 'AI & Technology',
      tags: ['Multi-Agent', 'AI Orchestra', 'Automation'],
      readTime: 10,
      likes: 167,
      comments: 19,
      imageUrl: 'https://picsum.photos/seed/3/800/400',
      publishedAt: new Date(Date.now() - 172800000).toISOString(),
      featured: false
    },
    {
      id: '4',
      title: 'Real-Time Odds Analysis with Machine Learning',
      slug: 'real-time-odds-ml',
      excerpt: 'How machine learning models can identify value bets and arbitrage opportunities in real-time.',
      content: '',
      author: { name: 'David Kim' },
      category: 'Sports Analytics',
      tags: ['Machine Learning', 'Odds', 'Real-time'],
      readTime: 15,
      likes: 201,
      comments: 45,
      imageUrl: 'https://picsum.photos/seed/4/800/400',
      publishedAt: new Date(Date.now() - 259200000).toISOString(),
      featured: false
    },
    {
      id: '5',
      title: 'The Future of AI-Powered Research',
      slug: 'future-ai-research',
      excerpt: 'Examining how AI is revolutionizing academic research and knowledge discovery.',
      content: '',
      author: { name: 'Emma Watson' },
      category: 'Research',
      tags: ['Research', 'AI', 'Innovation'],
      readTime: 7,
      likes: 134,
      comments: 22,
      imageUrl: 'https://picsum.photos/seed/5/800/400',
      publishedAt: new Date(Date.now() - 345600000).toISOString(),
      featured: false
    }
  ];

  const filterPosts = () => {
    let filtered = posts;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(post =>
        post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Filter by category
    if (selectedCategory) {
      filtered = filtered.filter(post => post.category === selectedCategory);
    }

    setFilteredPosts(filtered);
  };

  const handleLike = async (postId: string) => {
    try {
      await api.post(`/content/blogs/${postId}/like/`);
      toast.success('Post liked!');
      // Update local state
      setPosts(posts.map(post => 
        post.id === postId ? { ...post, likes: post.likes + 1 } : post
      ));
    } catch (error) {
      toast.error('Please login to like posts');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading blog posts...</div>
      </div>
    );
  }

  const featuredPosts = filteredPosts.filter(post => post.featured);
  const regularPosts = filteredPosts.filter(post => !post.featured);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-gray-900/70 backdrop-blur-lg border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">Blog & Insights</h1>
            <Button 
              onClick={() => navigate('/')}
              variant="ghost"
              className="text-gray-300 hover:text-white"
            >
              Back to Home
            </Button>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Insights from the AI Frontier
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Expert analysis on AI, content generation, sports analytics, and cutting-edge technology
          </p>
          
          {/* Search Bar */}
          <div className="max-w-2xl mx-auto relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <Input
              type="text"
              placeholder="Search articles, topics, or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-3 bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-purple-500"
            />
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap justify-center gap-2 mt-6">
            <Button
              variant={selectedCategory === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(null)}
              className={selectedCategory === null ? 'bg-purple-600' : 'border-gray-600 text-gray-300'}
            >
              All Posts
            </Button>
            {categories.map(category => (
              <Button
                key={category}
                variant={selectedCategory === category ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category)}
                className={selectedCategory === category ? 'bg-purple-600' : 'border-gray-600 text-gray-300'}
              >
                {category}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Posts */}
      {featuredPosts.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="flex items-center mb-6">
            <TrendingUp className="h-6 w-6 text-purple-500 mr-2" />
            <h3 className="text-2xl font-bold text-white">Featured Articles</h3>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            {featuredPosts.map(post => (
              <Card 
                key={post.id}
                className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-all cursor-pointer overflow-hidden group"
                onClick={() => navigate(`/blog/${post.slug}`)}
              >
                {post.imageUrl && (
                  <div className="h-48 overflow-hidden">
                    <img 
                      src={post.imageUrl} 
                      alt={post.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                )}
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Badge className="bg-purple-600/20 text-purple-400 border-purple-600/50">
                      Featured
                    </Badge>
                    <Badge variant="outline" className="border-gray-600 text-gray-400">
                      {post.category}
                    </Badge>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-purple-400 transition-colors">
                    {post.title}
                  </h3>
                  
                  <p className="text-gray-400 mb-4 line-clamp-2">
                    {post.excerpt}
                  </p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        {post.author.name}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {post.readTime} min read
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleLike(post.id);
                        }}
                        className="flex items-center gap-1 hover:text-red-400 transition-colors"
                      >
                        <Heart className="h-4 w-4" />
                        {post.likes}
                      </button>
                      <span className="flex items-center gap-1">
                        <MessageCircle className="h-4 w-4" />
                        {post.comments}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Regular Posts */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h3 className="text-2xl font-bold text-white mb-6">Recent Articles</h3>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {regularPosts.map(post => (
            <Card 
              key={post.id}
              className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-all cursor-pointer group"
              onClick={() => navigate(`/blog/${post.slug}`)}
            >
              {post.imageUrl && (
                <div className="h-40 overflow-hidden">
                  <img 
                    src={post.imageUrl} 
                    alt={post.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
              )}
              <CardContent className="p-5">
                <Badge variant="outline" className="border-gray-600 text-gray-400 mb-3">
                  {post.category}
                </Badge>
                
                <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-purple-400 transition-colors line-clamp-2">
                  {post.title}
                </h3>
                
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  {post.excerpt}
                </p>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {format(new Date(post.publishedAt), 'MMM d, yyyy')}
                  </span>
                  
                  <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1">
                      <Heart className="h-3 w-3" />
                      {post.likes}
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageCircle className="h-3 w-3" />
                      {post.comments}
                    </span>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1 mt-3">
                  {post.tags.slice(0, 3).map((tag, index) => (
                    <Badge 
                      key={index}
                      variant="outline" 
                      className="text-xs border-gray-700 text-gray-500"
                    >
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredPosts.length === 0 && (
          <div className="text-center py-12">
            <BookOpen className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No articles found matching your criteria</p>
          </div>
        )}
      </div>

      {/* Newsletter CTA */}
      <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 py-12 px-4 mt-12">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-2xl font-bold text-white mb-4">
            Stay Updated with AI Insights
          </h3>
          <p className="text-gray-300 mb-6">
            Get weekly updates on AI trends, sports analytics, and platform features
          </p>
          <div className="flex justify-center gap-4">
            <Input
              type="email"
              placeholder="Enter your email..."
              className="max-w-sm bg-gray-800 border-gray-700 text-white"
            />
            <Button className="bg-purple-600 hover:bg-purple-700">
              Subscribe
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogsPage;