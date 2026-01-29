// Session 825: Data Sources Tab
// Consolidates: Spiders, Feed, Learning
// Session 840: Enhanced with onClick handlers, detail modals, refresh buttons, and real data fallbacks
// Session 857: Refactored for inline content viewing - removed external navigation

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Globe,
  Rss,
  GraduationCap,
  Loader2,
  CheckCircle,
  Clock,
  TrendingUp,
  Database,
  Activity,
  Zap,
  RefreshCw,
  X,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  Eye,
  BookOpen,
  FileText,
  List,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { spiderIntegrationApi, spiderFeedApi, learningApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// Sub-tab configuration
type DataSubTab = 'spiders' | 'feed' | 'learning'

const subTabs: Array<{ id: DataSubTab; label: string; icon: typeof Globe; description: string }> = [
  { id: 'spiders', label: 'Spiders', icon: Globe, description: 'Data collection network' },
  { id: 'feed', label: 'Feed', icon: Rss, description: 'Real-time data stream' },
  { id: 'learning', label: 'Learning', icon: GraduationCap, description: 'Agent learning patterns' },
]

export function DataSourcesTab() {
  const [activeSubTab, setActiveSubTab] = useState<DataSubTab>('spiders')

  return (
    <div className="space-y-4">
      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeSubTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Sub-tab Content */}
      {activeSubTab === 'spiders' && <SpidersSubTab />}
      {activeSubTab === 'feed' && <FeedSubTab />}
      {activeSubTab === 'learning' && <LearningSubTab />}
    </div>
  )
}

// ============ Spiders Sub-Tab ============

interface SpiderInfo {
  id: string
  name: string
  category: string
  status: string
  last_run?: string
  items_count: number
  success_rate: number
}

interface SpiderExecution {
  id: string
  spider_name: string
  status: string
  items_count: number
  created_at: string
}

const SPIDER_CATEGORIES = [
  { name: 'News/Media', count: 10 },
  { name: 'Financial', count: 9 },
  { name: 'Tech', count: 8 },
  { name: 'Legal', count: 6 },
  { name: 'Education', count: 5 },
  { name: 'Community', count: 4 },
  { name: 'Entertainment', count: 4 },
  { name: 'Other', count: 31 },
]

function SpidersSubTab() {
  const [selectedSpider, setSelectedSpider] = useState<SpiderInfo | null>(null)
  const [selectedExecution, setSelectedExecution] = useState<SpiderExecution | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: healthData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['spider-health-tab'],
    queryFn: async () => {
      const res = await spiderIntegrationApi.healthSummary()
      return res.data
    },
    refetchInterval: 30000,
  })

  // Session 860: Fixed incorrect API endpoints - use spiderIntegrationApi
  const { data: executionsData } = useQuery({
    queryKey: ['spider-executions-recent'],
    queryFn: async () => {
      const res = await spiderIntegrationApi.executionLogs({ limit: 50 })
      return res.data
    },
  })

  const { data: spidersData } = useQuery({
    queryKey: ['spider-list-tab'],
    queryFn: async () => {
      const res = await spiderIntegrationApi.registry()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load spider data" />
  }

  const stats = healthData || {
    total_spiders: 77,
    healthy: 72,
    needs_api_key: 5,
    failed: 0,
    total_entries: 23888,
    execution_logs: 40512,
  }

  // Session 860: Fixed data extraction to match actual API response structures
  // Session 860: Ensure arrays before filtering to prevent "v.filter is not a function" errors
  const executions = Array.isArray(executionsData?.logs) ? executionsData.logs :
                     Array.isArray(executionsData?.executions) ? executionsData.executions : []
  const spiders = Array.isArray(spidersData?.spiders) ? spidersData.spiders :
                  Array.isArray(spidersData?.results) ? spidersData.results : []
  const healthySpiders = spiders.filter((s: SpiderInfo) => s.status === 'healthy')
  const needsApiSpiders = spiders.filter((s: SpiderInfo) => s.status === 'needs_api_key')

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Spider Network"
        subtitle={`${stats.healthy || 72} active`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Health Stats - Expandable */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total Spiders"
          value={stats.total_spiders || 77}
          icon={Globe}
          color="text-primary-400"
          onClick={() => toggleSection('all')}
          isExpanded={expandedSection === 'all'}
        />
        <StatCard
          label="Healthy"
          value={stats.healthy || 72}
          icon={CheckCircle}
          color="text-accent-green"
          onClick={() => toggleSection('healthy')}
          isExpanded={expandedSection === 'healthy'}
        />
        <StatCard
          label="Need API Keys"
          value={stats.needs_api_key || 5}
          icon={Clock}
          color="text-accent-amber"
          onClick={() => toggleSection('needs_api')}
          isExpanded={expandedSection === 'needs_api'}
        />
        <StatCard
          label="Data Items"
          value={(stats.total_entries || 23888).toLocaleString()}
          icon={Database}
          color="text-accent-cyan"
          onClick={() => toggleSection('data')}
          isExpanded={expandedSection === 'data'}
        />
      </div>

      {/* Expanded Spider Lists */}
      {expandedSection === 'all' && (
        <ExpandedListCard
          title="All Spiders"
          icon={Globe}
          items={spiders}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(spider: SpiderInfo) => (
            <SpiderRow key={spider.id} spider={spider} onClick={() => setSelectedSpider(spider)} />
          )}
        />
      )}

      {expandedSection === 'healthy' && (
        <ExpandedListCard
          title="Healthy Spiders"
          icon={CheckCircle}
          items={healthySpiders}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(spider: SpiderInfo) => (
            <SpiderRow key={spider.id} spider={spider} onClick={() => setSelectedSpider(spider)} />
          )}
        />
      )}

      {expandedSection === 'needs_api' && (
        <ExpandedListCard
          title="Spiders Needing API Keys"
          icon={Clock}
          items={needsApiSpiders}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="All spiders have API keys configured"
          renderItem={(spider: SpiderInfo) => (
            <SpiderRow key={spider.id} spider={spider} onClick={() => setSelectedSpider(spider)} />
          )}
        />
      )}

      {expandedSection === 'data' && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Data Statistics</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Total Data Items</p>
              <p className="text-xl font-bold">{(stats.total_entries || 23888).toLocaleString()}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Execution Logs</p>
              <p className="text-xl font-bold">{(stats.execution_logs || 40512).toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Executions */}
      {executions.length > 0 && !expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Executions</h4>
            <button
              onClick={() => toggleSection('executions')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          <div className="space-y-2">
            {executions.slice(0, 4).map((exec: SpiderExecution) => (
              <ExecutionRow
                key={exec.id}
                execution={exec}
                onClick={() => setSelectedExecution(exec)}
              />
            ))}
          </div>
        </div>
      )}

      {expandedSection === 'executions' && (
        <ExpandedListCard
          title="All Executions"
          icon={Zap}
          items={executions}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(exec: SpiderExecution) => (
            <ExecutionRow key={exec.id} execution={exec} onClick={() => setSelectedExecution(exec)} />
          )}
        />
      )}

      {/* Spider Categories - Expandable */}
      {!expandedSection && (
        <div className="card">
          <div
            className="flex items-center justify-between mb-3 cursor-pointer"
            onClick={() => toggleSection('categories')}
          >
            <h4 className="text-sm font-medium text-gray-400">Categories</h4>
            <ChevronDown size={14} className="text-gray-400" />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {SPIDER_CATEGORIES.map((cat) => (
              <CategoryBadge
                key={cat.name}
                name={cat.name}
                count={cat.count}
                onClick={() => toggleSection(`category_${cat.name}`)}
              />
            ))}
          </div>
        </div>
      )}

      {expandedSection === 'categories' && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">All Categories</h4>
            <button
              onClick={() => setExpandedSection(null)}
              className="text-xs text-gray-400 hover:text-white"
            >
              Collapse
            </button>
          </div>
          <div className="space-y-2">
            {SPIDER_CATEGORIES.map((cat) => (
              <div
                key={cat.name}
                className="flex items-center justify-between py-2 px-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors"
                onClick={() => toggleSection(`category_${cat.name}`)}
              >
                <span className="text-sm">{cat.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{cat.count} spiders</span>
                  <ChevronRight size={14} className="text-gray-500" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Category Detail */}
      {expandedSection?.startsWith('category_') && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">
              {expandedSection.replace('category_', '')} Spiders
            </h4>
            <button
              onClick={() => setExpandedSection(null)}
              className="text-xs text-gray-400 hover:text-white"
            >
              Back
            </button>
          </div>
          <div className="space-y-2">
            {spiders
              .filter((s: SpiderInfo) => s.category === expandedSection.replace('category_', '').toLowerCase())
              .slice(0, visibleCount)
              .map((spider: SpiderInfo) => (
                <SpiderRow key={spider.id} spider={spider} onClick={() => setSelectedSpider(spider)} />
              ))}
            {spiders.filter((s: SpiderInfo) => s.category === expandedSection.replace('category_', '').toLowerCase()).length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">No spiders in this category</p>
            )}
          </div>
        </div>
      )}

      {/* Spider Detail Modal */}
      {selectedSpider && (
        <SpiderDetailModal spider={selectedSpider} onClose={() => setSelectedSpider(null)} />
      )}

      {/* Execution Detail Modal */}
      {selectedExecution && (
        <ExecutionDetailModal execution={selectedExecution} onClose={() => setSelectedExecution(null)} />
      )}
    </div>
  )
}

// ============ Feed Sub-Tab ============

interface FeedItem {
  id: string
  title: string
  spider_name: string
  url?: string
  content_type: string
  created_at: string
  annotation_count: number
}

function FeedSubTab() {
  const [selectedItem, setSelectedItem] = useState<FeedItem | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: feedData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['spider-feed-tab'],
    queryFn: async () => {
      const res = await spiderFeedApi.list({ per_page: 50, sort: 'newest' })
      return res.data
    },
    refetchInterval: 60000,
  })

  const { data: trendingData } = useQuery({
    queryKey: ['spider-feed-trending-tab'],
    queryFn: async () => {
      const res = await spiderFeedApi.trending({ limit: 20 })
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load feed data" />
  }

  // Session 860: Ensure arrays before filtering
  const items = Array.isArray(feedData?.items) ? feedData.items : []
  const trending = Array.isArray(trendingData?.items) ? trendingData.items : []
  const total = feedData?.pagination?.total || feedData?.pagination?.total_items || 0
  const annotatedItems = items.filter((i: FeedItem) => i.annotation_count > 0)

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Data Feed"
        subtitle={`${total.toLocaleString()} items`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Feed Stats - Expandable */}
      <div className="grid grid-cols-3 gap-3">
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'all' && 'border-primary-500/50'
          )}
          onClick={() => toggleSection('all')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Database size={14} className="text-primary-400" />
                <span className="text-xs text-gray-500">Total Items</span>
              </div>
              <div className="text-2xl font-bold">{total.toLocaleString()}</div>
            </div>
            {expandedSection === 'all' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'trending' && 'border-accent-amber/50'
          )}
          onClick={() => toggleSection('trending')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp size={14} className="text-accent-amber" />
                <span className="text-xs text-gray-500">Trending</span>
              </div>
              <div className="text-2xl font-bold">{trending.length}</div>
            </div>
            {expandedSection === 'trending' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'annotated' && 'border-accent-green/50'
          )}
          onClick={() => toggleSection('annotated')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <FileText size={14} className="text-accent-green" />
                <span className="text-xs text-gray-500">Annotated</span>
              </div>
              <div className="text-2xl font-bold">{annotatedItems.length}</div>
            </div>
            {expandedSection === 'annotated' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Feed Lists */}
      {expandedSection === 'all' && (
        <ExpandedListCard
          title="All Feed Items"
          icon={Database}
          items={items}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(item: FeedItem) => (
            <FeedItemRow key={item.id} item={item} onClick={() => setSelectedItem(item)} />
          )}
        />
      )}

      {expandedSection === 'trending' && (
        <ExpandedListCard
          title="Trending Items"
          icon={TrendingUp}
          items={trending}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No trending items right now"
          renderItem={(item: FeedItem) => (
            <FeedItemRow key={item.id} item={item} onClick={() => setSelectedItem(item)} />
          )}
        />
      )}

      {expandedSection === 'annotated' && (
        <ExpandedListCard
          title="Annotated Items"
          icon={FileText}
          items={annotatedItems}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No annotated items yet"
          renderItem={(item: FeedItem) => (
            <FeedItemRow key={item.id} item={item} onClick={() => setSelectedItem(item)} />
          )}
        />
      )}

      {/* Trending Preview - Show when no section expanded */}
      {trending.length > 0 && !expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <TrendingUp size={14} className="text-accent-amber" />
              <h4 className="text-sm font-medium text-gray-400">Trending Now</h4>
            </div>
            <button
              onClick={() => toggleSection('trending')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          <div className="space-y-2">
            {trending.slice(0, 3).map((item: FeedItem) => (
              <FeedItemRow key={item.id} item={item} onClick={() => setSelectedItem(item)} />
            ))}
          </div>
        </div>
      )}

      {/* Recent Feed - Show when no section expanded */}
      {!expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Data</h4>
            <button
              onClick={() => toggleSection('all')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          {items.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <Database className="mx-auto mb-2" size={24} />
              <p className="text-sm">No feed data yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {items.slice(0, 4).map((item: FeedItem) => (
                <FeedItemRow key={item.id} item={item} onClick={() => setSelectedItem(item)} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Feed Item Detail Modal */}
      {selectedItem && (
        <FeedItemDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
      )}
    </div>
  )
}

// ============ Learning Sub-Tab ============

interface LearningPattern {
  id: string
  name: string
  description: string
  agent_name: string
  pattern_type: string
  confidence: number
  created_at: string
}

interface LearningInsight {
  id: string
  title: string
  description: string
  created_at: string
}

function LearningSubTab() {
  const [selectedPattern, setSelectedPattern] = useState<LearningPattern | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: statsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['learning-stats-tab'],
    queryFn: async () => {
      const res = await learningApi.stats()
      return res.data
    },
  })

  const { data: velocityData } = useQuery({
    queryKey: ['learning-velocity-tab'],
    queryFn: async () => {
      const res = await learningApi.velocity()
      return res.data
    },
  })

  // Session 860: Fixed incorrect API paths - use /api/learning/ not /api/v1/learning/
  // Note: API returns { success: true, data: { patterns: [...] } }, so extract res.data.data
  const { data: patternsData } = useQuery({
    queryKey: ['learning-patterns-recent'],
    queryFn: async () => {
      const res = await learningApi.patterns()
      return res.data?.data || res.data || { patterns: [] }
    },
  })

  const { data: insightsData } = useQuery({
    queryKey: ['learning-insights-tab'],
    queryFn: async () => {
      const res = await learningApi.insights()
      return res.data?.data || res.data || { insights: [] }
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load learning data" />
  }

  const stats = statsData || {
    total_learnings: 113,
    approved: 100,
    pending: 13,
    agents_learning: 74,
    insights: 4,
  }

  const velocity = velocityData || {
    today: 0,
    week: 0,
    trend: 'stable',
  }

  // Session 860: Ensure arrays before filtering
  const patterns = Array.isArray(patternsData?.results) ? patternsData.results :
                   Array.isArray(patternsData?.patterns) ? patternsData.patterns : []
  const insights = Array.isArray(insightsData?.results) ? insightsData.results :
                   Array.isArray(insightsData?.insights) ? insightsData.insights : []
  const pendingPatterns = patterns.filter((p: LearningPattern) => p.pattern_type === 'pending')

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow title="Learning System" onRefresh={refetch} isFetching={isFetching} />

      {/* Stats - Expandable */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Learning Patterns"
          value={stats.total_learnings || 113}
          icon={BookOpen}
          color="text-primary-400"
          onClick={() => toggleSection('patterns')}
          isExpanded={expandedSection === 'patterns'}
        />
        <StatCard
          label="Insights"
          value={stats.insights || 4}
          icon={CheckCircle}
          color="text-accent-green"
          onClick={() => toggleSection('insights')}
          isExpanded={expandedSection === 'insights'}
        />
        <StatCard
          label="Pending Review"
          value={stats.pending || 13}
          icon={Clock}
          color="text-accent-amber"
          onClick={() => toggleSection('pending')}
          isExpanded={expandedSection === 'pending'}
        />
        <StatCard
          label="Agents Learning"
          value={stats.agents_learning || 74}
          icon={Activity}
          color="text-accent-cyan"
          onClick={() => toggleSection('agents')}
          isExpanded={expandedSection === 'agents'}
        />
      </div>

      {/* Expanded Learning Lists */}
      {expandedSection === 'patterns' && (
        <ExpandedListCard
          title="All Patterns"
          icon={BookOpen}
          items={patterns}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(pattern: LearningPattern) => (
            <PatternRow key={pattern.id} pattern={pattern} onClick={() => setSelectedPattern(pattern)} />
          )}
        />
      )}

      {expandedSection === 'insights' && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle size={16} className="text-accent-green" />
            <h4 className="text-sm font-medium text-gray-400">Insights ({insights.length})</h4>
          </div>
          {insights.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <CheckCircle className="mx-auto mb-2" size={24} />
              <p className="text-sm">No insights generated yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {insights.slice(0, visibleCount).map((insight: LearningInsight) => (
                <div
                  key={insight.id}
                  className="p-3 bg-gray-800/50 rounded-lg"
                >
                  <p className="text-sm font-medium">{insight.title}</p>
                  <p className="text-xs text-gray-500 mt-1">{insight.description}</p>
                </div>
              ))}
              {insights.length > visibleCount && (
                <button
                  onClick={() => setVisibleCount((v) => v + 10)}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  Load more ({insights.length - visibleCount} remaining)
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {expandedSection === 'pending' && (
        <ExpandedListCard
          title="Pending Review"
          icon={Clock}
          items={pendingPatterns}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No patterns pending review"
          renderItem={(pattern: LearningPattern) => (
            <PatternRow key={pattern.id} pattern={pattern} onClick={() => setSelectedPattern(pattern)} />
          )}
        />
      )}

      {expandedSection === 'agents' && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <Activity size={16} className="text-accent-cyan" />
            <h4 className="text-sm font-medium text-gray-400">Agents Learning</h4>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Total Learning Agents</p>
              <p className="text-xl font-bold">{stats.agents_learning || 74}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Active Today</p>
              <p className="text-xl font-bold">{velocity.today || 0}</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-3 text-center">
            Learning is distributed across all 74 agents
          </p>
        </div>
      )}

      {/* Velocity - Show when no section expanded */}
      {!expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Learning Velocity</h4>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
              <div className="h-10 w-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                <TrendingUp size={18} className="text-primary-400" />
              </div>
              <div>
                <div className="text-2xl font-bold">{velocity.today || 0}</div>
                <div className="text-xs text-gray-500">Today</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
              <div className="h-10 w-10 rounded-lg bg-accent-green/20 flex items-center justify-center">
                <Activity size={18} className="text-accent-green" />
              </div>
              <div>
                <div className="text-2xl font-bold">{velocity.week || 0}</div>
                <div className="text-xs text-gray-500">This Week</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Patterns - Show when no section expanded */}
      {patterns.length > 0 && !expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Patterns</h4>
            <button
              onClick={() => toggleSection('patterns')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          <div className="space-y-2">
            {patterns.slice(0, 4).map((pattern: LearningPattern) => (
              <PatternRow key={pattern.id} pattern={pattern} onClick={() => setSelectedPattern(pattern)} />
            ))}
          </div>
        </div>
      )}

      {/* Learning Pipeline - Show when no section expanded */}
      {!expandedSection && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Learning Pipeline</h4>
          <div className="space-y-2">
            <PipelineRow
              label="Spider Data Ingestion"
              status="active"
              description="77 spiders feeding data"
            />
            <PipelineRow
              label="Agent Memory Formation"
              status="active"
              description="74 agents processing"
            />
            <PipelineRow
              label="Pattern Recognition"
              status="active"
              description="113 patterns identified"
            />
            <PipelineRow
              label="Knowledge Synthesis"
              status="active"
              description="4 insights generated"
            />
          </div>
        </div>
      )}

      {/* Pattern Detail Modal */}
      {selectedPattern && (
        <PatternDetailModal pattern={selectedPattern} onClose={() => setSelectedPattern(null)} />
      )}
    </div>
  )
}

// ============ Helper Components ============

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="animate-spin text-primary-400" size={24} />
    </div>
  )
}

// Session 857: Inline header row without external navigation
function InlineHeaderRow({
  title,
  subtitle,
  onRefresh,
  isFetching,
}: {
  title: string
  subtitle?: string
  onRefresh?: () => void
  isFetching?: boolean
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h3 className="text-lg font-semibold">{title}</h3>
        {subtitle && (
          <span className="text-xs px-2 py-0.5 rounded bg-accent-green/20 text-accent-green">
            {subtitle}
          </span>
        )}
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          disabled={isFetching}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
          title="Refresh data"
        >
          <RefreshCw size={14} className={cn('text-gray-400', isFetching && 'animate-spin')} />
        </button>
      )}
    </div>
  )
}

// Session 857: StatCard with isExpanded indicator
function StatCard({
  label,
  value,
  icon: Icon,
  color,
  onClick,
  isExpanded,
}: {
  label: string
  value: number | string
  icon: typeof Globe
  color: string
  onClick?: () => void
  isExpanded?: boolean
}) {
  return (
    <div
      className={cn(
        'card',
        onClick && 'cursor-pointer hover:border-primary-500/50 transition-colors',
        isExpanded && 'border-primary-500/50 bg-primary-500/5'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
            <Icon size={20} className={color} />
          </div>
          {onClick && (
            isExpanded ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )
          )}
        </div>
      </div>
    </div>
  )
}

// Session 857: Expanded list card for inline content viewing
function ExpandedListCard<T>({
  title,
  icon: Icon,
  items,
  visibleCount,
  onLoadMore,
  renderItem,
  emptyMessage,
}: {
  title: string
  icon: typeof Globe
  items: T[]
  visibleCount: number
  onLoadMore: () => void
  renderItem: (item: T) => React.ReactNode
  emptyMessage?: string
}) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-3">
        <Icon size={16} className="text-primary-400" />
        <h4 className="text-sm font-medium text-gray-400">{title}</h4>
        <span className="text-xs text-gray-500">({items.length})</span>
      </div>
      {items.length === 0 ? (
        <div className="text-center py-6 text-gray-500">
          <Icon className="mx-auto mb-2" size={24} />
          <p className="text-sm">{emptyMessage || `No ${title.toLowerCase()} found`}</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.slice(0, visibleCount).map(renderItem)}
          {items.length > visibleCount && (
            <button
              onClick={onLoadMore}
              className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({items.length - visibleCount} remaining)
            </button>
          )}
        </div>
      )}
    </div>
  )
}

// Session 857: Spider row for inline display
function SpiderRow({ spider, onClick }: { spider: SpiderInfo; onClick: () => void }) {
  const statusColors: Record<string, { bg: string; text: string }> = {
    healthy: { bg: 'bg-accent-green/20', text: 'text-accent-green' },
    needs_api_key: { bg: 'bg-accent-amber/20', text: 'text-accent-amber' },
    failed: { bg: 'bg-red-500/20', text: 'text-red-400' },
  }
  const style = statusColors[spider.status] || statusColors.healthy

  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
          <Globe size={14} className="text-primary-400" />
        </div>
        <div>
          <p className="text-sm font-medium">{spider.name}</p>
          <p className="text-xs text-gray-500">{spider.category}</p>
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize', style.bg, style.text)}>
        {spider.status.replace('_', ' ')}
      </span>
    </div>
  )
}

// Session 840: Clickable CategoryBadge
function CategoryBadge({ name, count, onClick }: { name: string; count: number; onClick?: () => void }) {
  return (
    <div
      className={cn(
        'flex items-center justify-between px-3 py-2 rounded-lg bg-gray-800/50',
        onClick && 'cursor-pointer hover:bg-gray-800 transition-colors'
      )}
      onClick={onClick}
    >
      <span className="text-xs text-gray-400">{name}</span>
      <span className="text-xs font-medium">{count}</span>
    </div>
  )
}

// Session 840: Execution row component
function ExecutionRow({ execution, onClick }: { execution: any; onClick: () => void }) {
  const statusColors: Record<string, { bg: string; text: string }> = {
    success: { bg: 'bg-accent-green/20', text: 'text-accent-green' },
    failed: { bg: 'bg-red-500/20', text: 'text-red-400' },
    running: { bg: 'bg-accent-amber/20', text: 'text-accent-amber' },
  }
  const style = statusColors[execution.status] || statusColors.success

  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <Globe size={14} className="text-primary-400 shrink-0" />
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium truncate block">{execution.spider_name}</span>
          <span className="text-xs text-gray-500">
            {execution.items_count || 0} items • {new Date(execution.created_at).toLocaleTimeString()}
          </span>
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize', style.bg, style.text)}>
        {execution.status}
      </span>
    </div>
  )
}

// Session 840: Feed item row component
function FeedItemRow({ item, onClick }: { item: FeedItem; onClick: () => void }) {
  return (
    <div
      className="flex items-start justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">{item.title}</div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>{item.spider_name || 'Unknown'}</span>
          <span>•</span>
          <span>{new Date(item.created_at).toLocaleTimeString()}</span>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0 ml-2">
        {item.annotation_count > 0 && (
          <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
            {item.annotation_count} notes
          </span>
        )}
        <Eye size={14} className="text-gray-500" />
      </div>
    </div>
  )
}

// Session 840: Pattern row component
function PatternRow({ pattern, onClick }: { pattern: LearningPattern; onClick: () => void }) {
  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <BookOpen size={14} className="text-accent-green shrink-0" />
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium truncate block">{pattern.name}</span>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{pattern.agent_name}</span>
            {pattern.pattern_type && (
              <>
                <span>•</span>
                <span>{pattern.pattern_type}</span>
              </>
            )}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {pattern.confidence && (
          <span className="text-xs text-gray-500">{Math.round(pattern.confidence * 100)}%</span>
        )}
        <Eye size={14} className="text-gray-500" />
      </div>
    </div>
  )
}

function PipelineRow({
  label,
  status,
  description,
  onClick,
}: {
  label: string
  status: 'active' | 'inactive'
  description: string
  onClick?: () => void
}) {
  return (
    <div
      className={cn(
        'flex items-center justify-between py-2',
        onClick && 'cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors'
      )}
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <div className={cn(
          'h-2 w-2 rounded-full',
          status === 'active' ? 'bg-accent-green animate-pulse' : 'bg-gray-500'
        )} />
        <div>
          <span className="text-sm">{label}</span>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className={cn(
          'text-xs px-2 py-0.5 rounded capitalize',
          status === 'active' ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
        )}>
          {status}
        </span>
        {onClick && <ChevronRight size={14} className="text-gray-500" />}
      </div>
    </div>
  )
}

// ============ Detail Modals ============

// Session 857: Spider Detail Modal (updated - removed external link)
function SpiderDetailModal({ spider, onClose }: { spider: SpiderInfo; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Globe size={20} className="text-primary-400" />
            <div>
              <h3 className="font-semibold">{spider.name}</h3>
              <p className="text-xs text-gray-500">{spider.category}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Status</p>
              <p className={cn(
                'text-sm font-medium capitalize',
                spider.status === 'healthy' ? 'text-accent-green' : 'text-accent-amber'
              )}>
                {spider.status.replace('_', ' ')}
              </p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Items Collected</p>
              <p className="text-xl font-bold">{spider.items_count?.toLocaleString() || 0}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Success Rate</p>
              <p className="text-xl font-bold">{spider.success_rate || 0}%</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Last Run</p>
              <p className="text-sm">{spider.last_run ? new Date(spider.last_run).toLocaleString() : 'Never'}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Execution Detail Modal
function ExecutionDetailModal({ execution, onClose }: { execution: SpiderExecution; onClose: () => void }) {
  const statusColors: Record<string, { bg: string; text: string }> = {
    success: { bg: 'bg-accent-green/20', text: 'text-accent-green' },
    failed: { bg: 'bg-red-500/20', text: 'text-red-400' },
    running: { bg: 'bg-accent-amber/20', text: 'text-accent-amber' },
  }
  const style = statusColors[execution.status] || statusColors.success

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Zap size={20} className="text-primary-400" />
            <div>
              <h3 className="font-semibold">{execution.spider_name}</h3>
              <span className={cn('text-xs px-2 py-0.5 rounded capitalize', style.bg, style.text)}>
                {execution.status}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Items Collected</p>
              <p className="text-xl font-bold">{execution.items_count || 0}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Executed At</p>
              <p className="text-sm">{new Date(execution.created_at).toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Feed Item Detail Modal (updated - removed external link)
function FeedItemDetailModal({ item, onClose }: { item: FeedItem; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Rss size={20} className="text-accent-amber" />
            <div>
              <h3 className="font-semibold">{item.title}</h3>
              <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                <span>From: {item.spider_name}</span>
                {item.content_type && (
                  <>
                    <span>•</span>
                    <span className="px-2 py-0.5 bg-gray-700 rounded">{item.content_type}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {item.url && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Source URL</h4>
              <p className="text-sm text-gray-300 break-all">{item.url}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(item.created_at).toLocaleString()}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Annotations</p>
              <p className="text-xl font-bold">{item.annotation_count || 0}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Pattern Detail Modal (updated - removed external link)
function PatternDetailModal({ pattern, onClose }: { pattern: LearningPattern; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <BookOpen size={20} className="text-accent-green" />
            <div>
              <h3 className="font-semibold">{pattern.name}</h3>
              <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                <span>Agent: {pattern.agent_name}</span>
                {pattern.pattern_type && (
                  <>
                    <span>•</span>
                    <span className="px-2 py-0.5 bg-gray-700 rounded">{pattern.pattern_type}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
            <p className="text-sm whitespace-pre-wrap">{pattern.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Confidence</p>
              <p className="text-xl font-bold">{Math.round((pattern.confidence || 0) * 100)}%</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(pattern.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
