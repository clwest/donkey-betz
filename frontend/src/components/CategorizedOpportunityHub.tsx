import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Filter, TrendingUp, Clock, CheckCircle, XCircle,
  DollarSign, Briefcase, Target, BarChart3, Send, Sparkles,
  Brain, Zap, Activity, Database, Loader2, ChevronRight,
  Calendar, Award, AlertCircle, RefreshCw, Eye, Star,
  FileText, MapPin, Building, Users, Play, Pause, Grid,
  List, SortAsc, SortDesc, Filter as FilterIcon
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { apiClient } from '../services/api.config';
import { toast } from 'sonner';

interface CategorizedOpportunity {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  url: string;
  source: string;
  category: {
    main: string;
    display_name: string;
    icon: string;
    color: string;
    subcategory: string;
    confidence: number;
  };
  financial: {
    budget_min?: number;
    budget_max?: number;
    currency: string;
    payment_type: string;
    payment_frequency: string;
  };
  quality: {
    budget_attractiveness: number;
    description_quality: number;
    overall_score: number;
  };
  enrichment: {
    tags: string[];
    difficulty_level: string;
    time_commitment: string;
    skill_requirements: string[];
  };
}

interface CategorySummary {
  total_opportunities: number;
  categories: {
    [key: string]: {
      count: number;
      display_name: string;
      icon: string;
      subcategories: { [key: string]: number };
    };
  };
  quality_distribution: {
    high: number;
    medium: number;
    low: number;
  };
}

const CategorizedOpportunityHub: React.FC = () => {
  const [opportunities, setOpportunities] = useState<CategorizedOpportunity[]>([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState<CategorizedOpportunity[]>([]);
  const [categorySummary, setCategorySummary] = useState<CategorySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedSubcategory, setSelectedSubcategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'quality' | 'budget' | 'date' | 'confidence'>('quality');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [qualityFilter, setQualityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    loadCategorizedOpportunities();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [opportunities, selectedCategory, selectedSubcategory, searchTerm, qualityFilter, sortBy, sortOrder]);

  const loadCategorizedOpportunities = async () => {
    setLoading(true);
    try {
      // Load opportunities from the spider system
      const response = await apiClient.get('/api/categorized-opportunities/');

      if (response.data.opportunities) {
        setOpportunities(response.data.opportunities);
        setCategorySummary(response.data.summary);
      } else {
        // Mock data for development
        generateMockCategorizedOpportunities();
      }
    } catch (error) {
      console.warn('Could not load live data, using mock opportunities');
      generateMockCategorizedOpportunities();
    } finally {
      setLoading(false);
    }
  };

  const generateMockCategorizedOpportunities = () => {
    const mockOpportunities: CategorizedOpportunity[] = [
      {
        id: '1',
        title: 'Senior Python Developer - AI/ML Focus',
        company: 'TechCorp AI',
        location: 'Remote',
        description: 'Looking for an experienced Python developer to work on cutting-edge AI and machine learning projects.',
        url: 'https://example.com/job/1',
        source: 'Remote OK',
        category: {
          main: 'full_time_jobs',
          display_name: 'Full-Time Jobs',
          icon: '🏢',
          color: '#10B981',
          subcategory: 'tech',
          confidence: 0.95
        },
        financial: {
          budget_min: 120000,
          budget_max: 180000,
          currency: 'USD',
          payment_type: 'salary',
          payment_frequency: 'annually'
        },
        quality: {
          budget_attractiveness: 0.9,
          description_quality: 0.8,
          overall_score: 0.85
        },
        enrichment: {
          tags: ['Python', 'AI', 'Machine Learning', 'Remote', 'Senior'],
          difficulty_level: 'advanced',
          time_commitment: 'full_time',
          skill_requirements: ['Python', 'TensorFlow', 'PyTorch', 'SQL']
        }
      },
      {
        id: '2',
        title: 'Content Writer for Tech Blog',
        company: 'AI Content Studio',
        location: 'Remote',
        description: 'Create engaging technical content about AI, machine learning, and software development.',
        url: 'https://example.com/job/2',
        source: 'Upwork',
        category: {
          main: 'freelance_work',
          display_name: 'Freelance & Contract',
          icon: '💼',
          color: '#3B82F6',
          subcategory: 'writing',
          confidence: 0.88
        },
        financial: {
          budget_min: 50,
          budget_max: 80,
          currency: 'USD',
          payment_type: 'hourly',
          payment_frequency: 'weekly'
        },
        quality: {
          budget_attractiveness: 0.7,
          description_quality: 0.9,
          overall_score: 0.8
        },
        enrichment: {
          tags: ['Content Writing', 'Tech', 'Blog', 'AI', 'Remote'],
          difficulty_level: 'intermediate',
          time_commitment: 'part_time',
          skill_requirements: ['Writing', 'SEO', 'Tech Knowledge']
        }
      },
      {
        id: '3',
        title: 'Amazon FBA Product Research Opportunity',
        company: 'E-commerce Ventures',
        location: 'USA',
        description: 'Profitable kitchen gadget niche with high demand and low competition. Estimated 30% profit margin.',
        url: 'https://example.com/opportunity/3',
        source: 'Amazon Research',
        category: {
          main: 'e_commerce',
          display_name: 'E-Commerce & Selling',
          icon: '🛒',
          color: '#F59E0B',
          subcategory: 'amazon_fba',
          confidence: 0.92
        },
        financial: {
          budget_min: 5000,
          budget_max: 15000,
          currency: 'USD',
          payment_type: 'investment',
          payment_frequency: 'once'
        },
        quality: {
          budget_attractiveness: 0.8,
          description_quality: 0.7,
          overall_score: 0.75
        },
        enrichment: {
          tags: ['Amazon FBA', 'E-commerce', 'Product Research', 'Kitchen', 'Profitable'],
          difficulty_level: 'intermediate',
          time_commitment: 'project_based',
          skill_requirements: ['Product Research', 'Amazon Seller Central', 'Marketing']
        }
      },
      {
        id: '4',
        title: 'Online Business Coaching Program',
        company: 'Success Mentors',
        location: 'Remote',
        description: 'Launch your own business coaching practice. Complete certification and client acquisition system included.',
        url: 'https://example.com/opportunity/4',
        source: 'Coaching Institute',
        category: {
          main: 'digital_services',
          display_name: 'Digital Services',
          icon: '💻',
          color: '#8B5CF6',
          subcategory: 'coaching',
          confidence: 0.85
        },
        financial: {
          budget_min: 2000,
          budget_max: 10000,
          currency: 'USD',
          payment_type: 'monthly',
          payment_frequency: 'monthly'
        },
        quality: {
          budget_attractiveness: 0.9,
          description_quality: 0.8,
          overall_score: 0.85
        },
        enrichment: {
          tags: ['Coaching', 'Business', 'Certification', 'Remote', 'Mentoring'],
          difficulty_level: 'intermediate',
          time_commitment: 'flexible',
          skill_requirements: ['Communication', 'Business Knowledge', 'Coaching Skills']
        }
      },
      {
        id: '5',
        title: 'Rental Property Investment - Kansas City',
        company: 'Real Estate Investments',
        location: 'Kansas City, MO',
        description: 'Turnkey rental property with 8.5% cap rate and $400/month cash flow. Fully renovated.',
        url: 'https://example.com/property/5',
        source: 'Real Estate Platform',
        category: {
          main: 'real_estate',
          display_name: 'Real Estate',
          icon: '🏠',
          color: '#EF4444',
          subcategory: 'rental_property',
          confidence: 0.93
        },
        financial: {
          budget_min: 45000,
          budget_max: 45000,
          currency: 'USD',
          payment_type: 'investment',
          payment_frequency: 'once'
        },
        quality: {
          budget_attractiveness: 0.9,
          description_quality: 0.9,
          overall_score: 0.9
        },
        enrichment: {
          tags: ['Real Estate', 'Rental Property', 'Cash Flow', 'Investment', 'Turnkey'],
          difficulty_level: 'advanced',
          time_commitment: 'project_based',
          skill_requirements: ['Real Estate Knowledge', 'Property Management', 'Financing']
        }
      }
    ];

    setOpportunities(mockOpportunities);

    // Generate mock summary
    const mockSummary: CategorySummary = {
      total_opportunities: mockOpportunities.length,
      categories: {
        full_time_jobs: { count: 1, display_name: 'Full-Time Jobs', icon: '🏢', subcategories: { tech: 1 } },
        freelance_work: { count: 1, display_name: 'Freelance & Contract', icon: '💼', subcategories: { writing: 1 } },
        e_commerce: { count: 1, display_name: 'E-Commerce & Selling', icon: '🛒', subcategories: { amazon_fba: 1 } },
        digital_services: { count: 1, display_name: 'Digital Services', icon: '💻', subcategories: { coaching: 1 } },
        real_estate: { count: 1, display_name: 'Real Estate', icon: '🏠', subcategories: { rental_property: 1 } }
      },
      quality_distribution: { high: 3, medium: 2, low: 0 }
    };

    setCategorySummary(mockSummary);
  };

  const applyFilters = () => {
    let filtered = [...opportunities];

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(opp => opp.category.main === selectedCategory);
    }

    // Subcategory filter
    if (selectedSubcategory !== 'all') {
      filtered = filtered.filter(opp => opp.category.subcategory === selectedSubcategory);
    }

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(opp =>
        opp.title.toLowerCase().includes(searchLower) ||
        opp.company.toLowerCase().includes(searchLower) ||
        opp.description.toLowerCase().includes(searchLower) ||
        opp.enrichment.tags.some(tag => tag.toLowerCase().includes(searchLower))
      );
    }

    // Quality filter
    if (qualityFilter !== 'all') {
      filtered = filtered.filter(opp => {
        const score = opp.quality.overall_score;
        switch (qualityFilter) {
          case 'high': return score >= 0.7;
          case 'medium': return score >= 0.4 && score < 0.7;
          case 'low': return score < 0.4;
          default: return true;
        }
      });
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue, bValue;

      switch (sortBy) {
        case 'quality':
          aValue = a.quality.overall_score;
          bValue = b.quality.overall_score;
          break;
        case 'budget':
          aValue = a.financial.budget_max || a.financial.budget_min || 0;
          bValue = b.financial.budget_max || b.financial.budget_min || 0;
          break;
        case 'confidence':
          aValue = a.category.confidence;
          bValue = b.category.confidence;
          break;
        default:
          aValue = parseInt(a.id);
          bValue = parseInt(b.id);
      }

      return sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
    });

    setFilteredOpportunities(filtered);
  };

  const handleSelectOpportunity = async (opportunity: CategorizedOpportunity) => {
    try {
      await apiClient.post('/api/select-opportunity/', {
        opportunity_id: opportunity.id,
        category: opportunity.category.main,
        action: 'apply'
      });

      toast.success(`Selected "${opportunity.title}" for application!`);
    } catch (error) {
      toast.error('Failed to select opportunity');
    }
  };

  const formatBudget = (financial: CategorizedOpportunity['financial']) => {
    const { budget_min, budget_max, currency, payment_type, payment_frequency } = financial;

    if (!budget_min && !budget_max) return 'Budget not specified';

    let budgetStr = '';
    if (budget_min && budget_max && budget_min !== budget_max) {
      budgetStr = `${currency} ${budget_min.toLocaleString()} - ${budget_max.toLocaleString()}`;
    } else {
      const amount = budget_max || budget_min || 0;
      budgetStr = `${currency} ${amount.toLocaleString()}`;
    }

    if (payment_type === 'hourly') budgetStr += '/hr';
    if (payment_type === 'salary' && payment_frequency === 'annually') budgetStr += '/year';
    if (payment_type === 'monthly') budgetStr += '/month';

    return budgetStr;
  };

  const getQualityBadgeColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-100 text-green-800';
    if (score >= 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getQualityLabel = (score: number) => {
    if (score >= 0.7) return 'High Quality';
    if (score >= 0.4) return 'Medium Quality';
    return 'Low Quality';
  };

  const OpportunityCard = ({ opportunity }: { opportunity: CategorizedOpportunity }) => (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ y: -5 }}
      className="h-full"
    >
      <Card className="h-full bg-gradient-to-br from-white to-gray-50 border-l-4 hover:shadow-lg transition-all duration-200"
            style={{ borderLeftColor: opportunity.category.color }}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">{opportunity.category.icon}</span>
              <div>
                <CardTitle className="text-lg line-clamp-2">{opportunity.title}</CardTitle>
                <CardDescription className="flex items-center space-x-2">
                  <span>{opportunity.company}</span>
                  <span>•</span>
                  <span>{opportunity.location}</span>
                </CardDescription>
              </div>
            </div>
            <Badge className={getQualityBadgeColor(opportunity.quality.overall_score)}>
              {getQualityLabel(opportunity.quality.overall_score)}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <p className="text-sm text-gray-600 line-clamp-3">{opportunity.description}</p>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-green-600">{formatBudget(opportunity.financial)}</span>
              <Badge variant="outline" style={{ color: opportunity.category.color }}>
                {opportunity.category.display_name}
              </Badge>
            </div>

            <div className="flex flex-wrap gap-1">
              {opportunity.enrichment.tags.slice(0, 4).map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {opportunity.enrichment.tags.length > 4 && (
                <Badge variant="secondary" className="text-xs">
                  +{opportunity.enrichment.tags.length - 4} more
                </Badge>
              )}
            </div>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Confidence: {(opportunity.category.confidence * 100).toFixed(0)}%</span>
              <span>{opportunity.enrichment.difficulty_level} • {opportunity.enrichment.time_commitment}</span>
            </div>
          </div>

          <div className="flex space-x-2 pt-2">
            <Button
              onClick={() => handleSelectOpportunity(opportunity)}
              className="flex-1"
              style={{ backgroundColor: opportunity.category.color }}
            >
              <Send className="w-4 h-4 mr-2" />
              Apply Now
            </Button>
            <Button variant="outline" size="sm" asChild>
              <a href={opportunity.url} target="_blank" rel="noopener noreferrer">
                <Eye className="w-4 h-4" />
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const CategorySummaryCard = ({ categoryKey, categoryData }: { categoryKey: string, categoryData: any }) => (
    <Card
      className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
        selectedCategory === categoryKey ? 'ring-2 ring-blue-500' : ''
      }`}
      onClick={() => setSelectedCategory(selectedCategory === categoryKey ? 'all' : categoryKey)}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{categoryData.icon}</span>
            <div>
              <h3 className="font-medium">{categoryData.display_name}</h3>
              <p className="text-sm text-gray-500">{categoryData.count} opportunities</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            🎯 Categorized Opportunities
          </h1>
          <p className="text-gray-600">
            AI-powered opportunity discovery and categorization across all income streams
          </p>
        </div>

        {/* Summary Stats */}
        {categorySummary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{categorySummary.total_opportunities}</div>
                <div className="text-sm text-gray-500">Total Opportunities</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{categorySummary.quality_distribution.high}</div>
                <div className="text-sm text-gray-500">High Quality</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">{categorySummary.quality_distribution.medium}</div>
                <div className="text-sm text-gray-500">Medium Quality</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">{Object.keys(categorySummary.categories).length}</div>
                <div className="text-sm text-gray-500">Categories</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Category Overview */}
        {categorySummary && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Browse by Category</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(categorySummary.categories).map(([key, data]) => (
                <CategorySummaryCard key={key} categoryKey={key} categoryData={data} />
              ))}
            </div>
          </div>
        )}

        {/* Filters and Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
            <div className="flex-1">
              <Input
                placeholder="Search opportunities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>

            <div className="flex flex-wrap gap-2">
              <Select value={qualityFilter} onValueChange={(value: any) => setQualityFilter(value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Quality" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Quality</SelectItem>
                  <SelectItem value="high">High Quality</SelectItem>
                  <SelectItem value="medium">Medium Quality</SelectItem>
                  <SelectItem value="low">Low Quality</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="quality">Quality</SelectItem>
                  <SelectItem value="budget">Budget</SelectItem>
                  <SelectItem value="confidence">Confidence</SelectItem>
                  <SelectItem value="date">Date</SelectItem>
                </SelectContent>
              </Select>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              >
                {viewMode === 'grid' ? <List className="w-4 h-4" /> : <Grid className="w-4 h-4" />}
              </Button>

              <Button onClick={loadCategorizedOpportunities} disabled={loading}>
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>

        {/* Opportunities Grid */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">
              {selectedCategory === 'all' ? 'All Opportunities' :
               categorySummary?.categories[selectedCategory]?.display_name || 'Opportunities'}
            </h2>
            <span className="text-gray-500">{filteredOpportunities.length} opportunities</span>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Loading opportunities...</span>
            </div>
          ) : (
            <AnimatePresence>
              <div className={`grid gap-6 ${
                viewMode === 'grid'
                  ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                  : 'grid-cols-1'
              }`}>
                {filteredOpportunities.map((opportunity) => (
                  <OpportunityCard key={opportunity.id} opportunity={opportunity} />
                ))}
              </div>
            </AnimatePresence>
          )}

          {!loading && filteredOpportunities.length === 0 && (
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-600 mb-2">No opportunities found</h3>
              <p className="text-gray-500">Try adjusting your filters or search criteria</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CategorizedOpportunityHub;