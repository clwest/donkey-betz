/**
 * Template Library Component
 * Browse, search, and manage prompt templates
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  DocumentTextIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  StarIcon,
  EyeIcon,
  ClipboardDocumentIcon,
  TagIcon,
  CalendarIcon,
  UserIcon,
  CheckBadgeIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { LoadingSpinner } from '../../common/LoadingSpinner';
import EmptyState from '../../common/EmptyState';
import { promptDiagnosticsService } from '../../../services/promptDiagnostics.service';
import toast from 'react-hot-toast';
import type { PromptTemplate } from '../../../types/promptDiagnostics.types';

export function TemplateLibrary() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [filterPublic, setFilterPublic] = useState<boolean | null>(null);
  const [sortBy, setSortBy] = useState<'effectiveness' | 'usage' | 'recent'>('effectiveness');

  // Fetch templates
  const { data: templatesData, isLoading, error, refetch } = useQuery({
    queryKey: ['prompt-templates', searchQuery, selectedCategory, filterPublic, sortBy],
    queryFn: () => promptDiagnosticsService.listTemplates({
      search: searchQuery || undefined,
      category: selectedCategory || undefined,
      is_public: filterPublic !== null ? filterPublic : undefined,
      limit: 50,
    }),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'general', label: 'General' },
    { value: 'creative', label: 'Creative' },
    { value: 'analytical', label: 'Analytical' },
    { value: 'technical', label: 'Technical' },
    { value: 'conversational', label: 'Conversational' },
    { value: 'system', label: 'System' },
  ];

  const handleCopyTemplate = (template: PromptTemplate) => {
    navigator.clipboard.writeText(template.template_text);
    toast.success(`Template "${template.name}" copied to clipboard!`);
  };

  const handleUseTemplate = (template: PromptTemplate) => {
    // This would navigate to the analyzer with the template pre-filled
    // For now, just copy to clipboard
    handleCopyTemplate(template);
    toast.success('Template ready to use! Paste it in the analyzer.');
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'creative': return '🎨';
      case 'analytical': return '📊';
      case 'technical': return '⚙️';
      case 'conversational': return '💬';
      case 'system': return '🔧';
      default: return '📝';
    }
  };

  const getEffectivenessColor = (rating: number) => {
    if (rating >= 4.0) return 'text-green-600 dark:text-green-500';
    if (rating >= 3.0) return 'text-yellow-600 dark:text-yellow-500';
    return 'text-red-600 dark:text-red-500';
  };

  const templates = templatesData?.templates || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Template Library</h2>
          <p className="text-muted-foreground">
            Browse and use optimized prompt templates from the community
          </p>
        </div>
        <Button className="flex items-center">
          <PlusIcon className="h-4 w-4 mr-2" />
          Create Template
        </Button>
      </div>

      {/* Filters and Search */}
      <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-white/10 rounded-lg focus:ring-primary-500 focus:border-primary-500 bg-card/50 backdrop-blur-sm text-foreground placeholder-gray-400"
              />
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-white/10 rounded-lg focus:ring-primary-500 focus:border-primary-500 bg-card/50 backdrop-blur-sm text-foreground"
            >
              {categories.map((category) => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>
          </div>

          {/* Filter Options */}
          <div className="flex items-center space-x-4">
            <div className="flex space-x-2">
              <Button
                variant={filterPublic === null ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterPublic(null)}
              >
                All
              </Button>
              <Button
                variant={filterPublic === true ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterPublic(true)}
              >
                Public
              </Button>
              <Button
                variant={filterPublic === false ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterPublic(false)}
              >
                Mine
              </Button>
            </div>
          </div>
        </div>

        {/* Sort Options */}
        <div className="flex items-center space-x-4 mt-4 pt-4 border-t border-white/10">
          <span className="text-sm text-muted-foreground">Sort by:</span>
          <div className="flex space-x-2">
            <Button
              variant={sortBy === 'effectiveness' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('effectiveness')}
            >
              <StarIcon className="h-4 w-4 mr-1" />
              Effectiveness
            </Button>
            <Button
              variant={sortBy === 'usage' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('usage')}
            >
              <EyeIcon className="h-4 w-4 mr-1" />
              Most Used
            </Button>
            <Button
              variant={sortBy === 'recent' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('recent')}
            >
              <CalendarIcon className="h-4 w-4 mr-1" />
              Recent
            </Button>
          </div>
        </div>
      </Card>

      {/* Templates Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <DocumentTextIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">
            Failed to load templates
          </h3>
          <p className="text-muted-foreground mb-4">
            Please try refreshing the page
          </p>
          <Button onClick={() => refetch()}>Retry</Button>
        </div>
      ) : templates.length === 0 ? (
        <EmptyState
          icon={DocumentTextIcon}
          title="No templates found"
          description={searchQuery ? "Try adjusting your search or filters" : "Start creating templates from your optimized prompts"}
          action={{
            label: 'Create Your First Template',
            onClick: () => {
              // Navigate to analyzer or template creation
              toast.success('Navigate to the analyzer to create templates from optimized prompts');
            }
          }}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {templates.map((template) => (
            <Card key={template.id} className="p-6 bg-card/50 backdrop-blur-sm hover:bg-dark-700/50 transition-all border border-white/10">
              {/* Template Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">{getCategoryIcon(template.category)}</span>
                    <h3 className="text-lg font-semibold text-foreground truncate">
                      {template.name}
                    </h3>
                    {template.is_verified && (
                      <CheckBadgeIcon className="h-5 w-5 text-blue-500" title="Verified Template" />
                    )}
                    {template.is_public && (
                      <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-300 rounded">
                        Public
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                    {template.description}
                  </p>
                </div>
              </div>

              {/* Template Preview */}
              <div className="mb-4">
                <div className="bg-card/50 backdrop-blur-sm p-3 rounded-lg text-sm font-mono text-muted-foreground max-h-24 overflow-hidden">
                  {template.template_text}
                </div>
                {template.template_text.length > 200 && (
                  <p className="text-xs text-muted-foreground mt-1">Preview truncated...</p>
                )}
              </div>

              {/* Template Variables */}
              {template.variables.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-muted-foreground mb-2">
                    Variables:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {template.variables.slice(0, 3).map((variable) => (
                      <span
                        key={variable}
                        className="px-2 py-1 text-xs font-medium bg-primary-500/20 text-primary-300 rounded"
                      >
                        {'{' + variable + '}'}
                      </span>
                    ))}
                    {template.variables.length > 3 && (
                      <span className="px-2 py-1 text-xs text-muted-foreground">
                        +{template.variables.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Template Metrics */}
              <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                <div>
                  <div className={`text-lg font-bold ${getEffectivenessColor(template.effectiveness_rating)}`}>
                    {template.effectiveness_rating.toFixed(1)}
                  </div>
                  <div className="text-xs text-muted-foreground">Effectiveness</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-foreground">
                    {template.usage_count}
                  </div>
                  <div className="text-xs text-muted-foreground">Uses</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-blue-600 dark:text-blue-500">
                    {promptDiagnosticsService.formatTokenCount(template.token_count)}
                  </div>
                  <div className="text-xs text-muted-foreground">Size</div>
                </div>
              </div>

              {/* Template Meta */}
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                <div className="flex items-center">
                  <UserIcon className="h-3 w-3 mr-1" />
                  {template.is_mine ? 'You' : 'Community'}
                </div>
                <div className="flex items-center">
                  <CalendarIcon className="h-3 w-3 mr-1" />
                  {new Date(template.created_at).toLocaleDateString()}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => handleUseTemplate(template)}
                  className="flex-1"
                >
                  <DocumentTextIcon className="h-4 w-4 mr-1" />
                  Use Template
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopyTemplate(template)}
                >
                  <ClipboardDocumentIcon className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                >
                  <EyeIcon className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Load More */}
      {templates.length > 0 && templatesData?.pagination.has_next && (
        <div className="text-center">
          <Button variant="outline">
            Load More Templates
          </Button>
        </div>
      )}
    </div>
  );
}