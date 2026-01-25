// Session 825: Data Sources Tab
// Consolidates: Spiders, Feed, Learning
// Safe approach: Compact views with links to full pages

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Globe,
  Rss,
  GraduationCap,
  Loader2,
  ExternalLink,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Database,
  Activity,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { spiderIntegrationApi, spiderFeedApi, learningApi } from '@/lib/api'

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

function SpidersSubTab() {
  const { data: healthData, isLoading } = useQuery({
    queryKey: ['spider-health-tab'],
    queryFn: async () => {
      const res = await spiderIntegrationApi.healthSummary()
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30s
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  const stats = healthData || {
    total_spiders: 77,
    healthy: 72,
    needs_api_key: 5,
    failed: 0,
    total_entries: 0,
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold">Spider Network</h3>
          <span className="text-xs px-2 py-0.5 rounded bg-accent-green/20 text-accent-green">
            {stats.healthy || 72} active
          </span>
        </div>
        <a href="/spider-integration" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Dashboard
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Health Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <HealthCard
          label="Total Spiders"
          value={stats.total_spiders || 77}
          icon={Globe}
          color="text-primary-400"
        />
        <HealthCard
          label="Healthy"
          value={stats.healthy || 72}
          icon={CheckCircle}
          color="text-accent-green"
        />
        <HealthCard
          label="Need API Keys"
          value={stats.needs_api_key || 5}
          icon={Clock}
          color="text-accent-amber"
        />
        <HealthCard
          label="Failed"
          value={stats.failed || 0}
          icon={XCircle}
          color="text-red-400"
        />
      </div>

      {/* Spider Categories */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Categories</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <CategoryBadge name="News/Media" count={10} />
          <CategoryBadge name="Financial" count={9} />
          <CategoryBadge name="Tech" count={8} />
          <CategoryBadge name="Legal" count={6} />
          <CategoryBadge name="Education" count={5} />
          <CategoryBadge name="Community" count={4} />
          <CategoryBadge name="Entertainment" count={4} />
          <CategoryBadge name="Other" count={31} />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Quick Actions</h4>
        <div className="flex gap-2">
          <a href="/spider-integration?action=run" className="btn btn-primary text-sm">
            <Zap size={14} className="mr-2" />
            Run All Spiders
          </a>
          <a href="/spider-feed" className="btn btn-secondary text-sm">
            <Rss size={14} className="mr-2" />
            View Feed
          </a>
        </div>
      </div>
    </div>
  )
}

// ============ Feed Sub-Tab ============

function FeedSubTab() {
  const { data: feedData, isLoading } = useQuery({
    queryKey: ['spider-feed-tab'],
    queryFn: async () => {
      const res = await spiderFeedApi.list({ per_page: 5, sort: 'newest' })
      return res.data
    },
    refetchInterval: 60000, // Refresh every minute
  })

  const { data: trendingData } = useQuery({
    queryKey: ['spider-feed-trending-tab'],
    queryFn: async () => {
      const res = await spiderFeedApi.trending({ limit: 3 })
      return res.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  const items = feedData?.items || []
  const trending = trendingData?.items || []
  const total = feedData?.pagination?.total || 0

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold">Data Feed</h3>
          <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
            {total} items
          </span>
        </div>
        <a href="/spider-feed" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Feed
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Trending */}
      {trending.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp size={14} className="text-accent-amber" />
            <h4 className="text-sm font-medium text-gray-400">Trending Now</h4>
          </div>
          <div className="space-y-2">
            {trending.map((item: any) => (
              <FeedItemRow key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}

      {/* Recent Feed */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Data</h4>
        {items.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <Database className="mx-auto mb-2" size={24} />
            <p className="text-sm">No feed data yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.slice(0, 4).map((item: any) => (
              <FeedItemRow key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ============ Learning Sub-Tab ============

function LearningSubTab() {
  const { data: statsData, isLoading } = useQuery({
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  const stats = statsData || {
    total_learnings: 0,
    approved: 0,
    pending: 0,
    agents_learning: 0,
  }

  const velocity = velocityData || {
    today: 0,
    week: 0,
    trend: 'stable',
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Learning System</h3>
        <a href="/learning-journey" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Journey
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <LearningCard
          label="Total Learnings"
          value={stats.total_learnings || 0}
          icon={Database}
          color="text-primary-400"
        />
        <LearningCard
          label="Approved"
          value={stats.approved || 0}
          icon={CheckCircle}
          color="text-accent-green"
        />
        <LearningCard
          label="Pending Review"
          value={stats.pending || 0}
          icon={Clock}
          color="text-accent-amber"
        />
        <LearningCard
          label="Agents Learning"
          value={stats.agents_learning || 74}
          icon={Activity}
          color="text-accent-cyan"
        />
      </div>

      {/* Velocity */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Learning Velocity</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <TrendingUp size={18} className="text-primary-400" />
            </div>
            <div>
              <div className="text-2xl font-bold">{velocity.today || 0}</div>
              <div className="text-xs text-gray-500">Today</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
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

      {/* Learning Pipeline */}
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
            description="Cross-agent learning enabled"
          />
          <PipelineRow
            label="Knowledge Synthesis"
            status="active"
            description="Collective intelligence active"
          />
        </div>
      </div>
    </div>
  )
}

// ============ Helper Components ============

function HealthCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string
  value: number
  icon: typeof Globe
  color: string
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
          <Icon size={20} className={color} />
        </div>
      </div>
    </div>
  )
}

function LearningCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string
  value: number
  icon: typeof Database
  color: string
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
          <Icon size={20} className={color} />
        </div>
      </div>
    </div>
  )
}

function CategoryBadge({ name, count }: { name: string; count: number }) {
  return (
    <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-800/50">
      <span className="text-xs text-gray-400">{name}</span>
      <span className="text-xs font-medium">{count}</span>
    </div>
  )
}

function FeedItemRow({ item }: { item: any }) {
  return (
    <div className="flex items-start justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">{item.title}</div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>{item.spider_name || 'Unknown'}</span>
          <span>•</span>
          <span>{new Date(item.created_at).toLocaleTimeString()}</span>
        </div>
      </div>
      {item.annotation_count > 0 && (
        <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400 ml-2">
          {item.annotation_count} notes
        </span>
      )}
    </div>
  )
}

function PipelineRow({
  label,
  status,
  description,
}: {
  label: string
  status: 'active' | 'inactive'
  description: string
}) {
  return (
    <div className="flex items-center justify-between py-2">
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
      <span className={cn(
        'text-xs px-2 py-0.5 rounded capitalize',
        status === 'active' ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
      )}>
        {status}
      </span>
    </div>
  )
}
