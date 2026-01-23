/**
 * Spider Integration Page
 *
 * Session 718: Visualizes the spider network - 77 data-gathering spiders
 * across 20+ categories providing real-time intelligence feeds.
 *
 * Features:
 * - Spider registry with search/filter
 * - Health monitoring (success rates, errors)
 * - Execution controls (run individual spiders)
 * - Data feed preview
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Bug,
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Play,
  Search,
  TrendingUp,
  Database,
  Clock,
  RefreshCw,
  Filter,
  ChevronDown,
  ChevronUp,
  Zap,
  Globe,
  Info,
} from 'lucide-react'
import { spiderIntegrationApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

// Types
interface Spider {
  id: number
  name: string
  displayName: string
  icon: string
  category: string
  status: 'Active' | 'Idle' | 'Error'
  dataCollected: number
  lastActivity: string
  successRate: number
  targets: string[]
}

interface NetworkData {
  totalSpiders: number
  activeSpiders: number
  opportunitiesFound: number
  dataCollected: number
  successRate: number
  spiders: Spider[]
  lastUpdated: string
}

interface HealthSummary {
  summary: {
    executions_24h: number
    errors_24h: number
    success_rate_24h: number
    data_collected_24h: number
    data_collected_7d: number
    embedding_coverage: number
  }
  recent_errors: Array<{
    id: string
    spider_name: string
    error_message: string
    started_at: string
  }>
  top_error_spiders: Array<{
    spider_name: string
    error_count: number
  }>
}

interface ActivityItem {
  timestamp: string
  spider: string
  action: string
  details: string
  status: 'success' | 'error' | 'warning'
}

// Status Badge Component
function StatusBadge({ status }: { status: 'Active' | 'Idle' | 'Error' }) {
  const config = {
    Active: { color: 'bg-green-500/20 text-green-400', icon: CheckCircle2 },
    Idle: { color: 'bg-gray-500/20 text-gray-400', icon: Clock },
    Error: { color: 'bg-red-500/20 text-red-400', icon: XCircle },
  }
  const { color, icon: Icon } = config[status]
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs ${color}`}>
      <Icon className="h-3 w-3" />
      {status}
    </span>
  )
}

// Spider Card Component
function SpiderCard({
  spider,
  onRun,
  isRunning,
}: {
  spider: Spider
  onRun: () => void
  isRunning: boolean
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-lg border border-dark-border bg-dark-card overflow-hidden">
      <div
        className="p-4 cursor-pointer hover:bg-dark-bg/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{spider.icon}</span>
            <div>
              <h3 className="font-medium text-white">{spider.displayName}</h3>
              <span className="text-xs text-gray-400">{spider.category}</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={spider.status} />
            {expanded ? (
              <ChevronUp className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            )}
          </div>
        </div>

        <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-400">Data Collected</div>
            <div className="text-white font-medium">{spider.dataCollected.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-gray-400">Success Rate</div>
            <div className={`font-medium ${spider.successRate >= 80 ? 'text-green-400' : spider.successRate >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
              {spider.successRate}%
            </div>
          </div>
          <div>
            <div className="text-gray-400">Last Activity</div>
            <div className="text-white text-xs">
              {new Date(spider.lastActivity).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-dark-border p-4 bg-dark-bg/30">
          <div className="mb-3">
            <div className="text-sm text-gray-400 mb-2">Data Sources:</div>
            <div className="flex flex-wrap gap-2">
              {spider.targets.map((target, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-2 py-1 rounded bg-dark-bg text-xs text-gray-300"
                >
                  <Globe className="h-3 w-3" />
                  {target}
                </span>
              ))}
            </div>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onRun()
            }}
            disabled={isRunning || spider.status !== 'Active'}
            className={`w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isRunning || spider.status !== 'Active'
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {isRunning ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Run Spider
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

// Activity Feed Item
function ActivityFeedItem({ item }: { item: ActivityItem }) {
  return (
    <div className="flex items-start gap-3 py-3 border-b border-dark-border last:border-0">
      <div
        className={`p-1.5 rounded-full ${
          item.status === 'success'
            ? 'bg-green-500/20'
            : item.status === 'error'
              ? 'bg-red-500/20'
              : 'bg-yellow-500/20'
        }`}
      >
        {item.status === 'success' ? (
          <CheckCircle2 className="h-4 w-4 text-green-400" />
        ) : item.status === 'error' ? (
          <XCircle className="h-4 w-4 text-red-400" />
        ) : (
          <AlertTriangle className="h-4 w-4 text-yellow-400" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className="font-medium text-white text-sm">{item.spider}</span>
          <span className="text-xs text-gray-500">
            {new Date(item.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <div className="text-sm text-gray-400">{item.action}</div>
        {item.details && (
          <div className="text-xs text-gray-500 truncate mt-1">{item.details}</div>
        )}
      </div>
    </div>
  )
}

// Main Page Component
export default function SpiderIntegrationPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [runningSpider, setRunningSpider] = useState<string | null>(null)

  const queryClient = useQueryClient()

  // Fetch network data
  const { data: networkData, isLoading: networkLoading } = useQuery<NetworkData>({
    queryKey: ['spider-network'],
    queryFn: async () => {
      const response = await spiderIntegrationApi.network()
      return response.data
    },
    staleTime: 30000,
    refetchInterval: 60000,
  })

  // Fetch health summary
  const { data: healthData, isLoading: healthLoading } = useQuery<HealthSummary>({
    queryKey: ['spider-health-summary'],
    queryFn: async () => {
      const response = await spiderIntegrationApi.healthSummary()
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch activity feed
  const { data: activityData } = useQuery<{ activities: ActivityItem[] }>({
    queryKey: ['spider-activity'],
    queryFn: async () => {
      const response = await spiderIntegrationApi.activityFeed()
      return response.data
    },
    staleTime: 15000,
    refetchInterval: 30000,
  })

  // Run spider mutation
  const runSpiderMutation = useMutation({
    mutationFn: async (spiderName: string) => {
      setRunningSpider(spiderName)
      const response = await spiderIntegrationApi.runSpider(spiderName)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spider-network'] })
      queryClient.invalidateQueries({ queryKey: ['spider-activity'] })
    },
    onSettled: () => {
      setTimeout(() => setRunningSpider(null), 2000)
    },
  })

  // Get unique categories
  const categories = networkData
    ? [...new Set(networkData.spiders.map((s) => s.category))].sort()
    : []

  // Filter spiders
  const filteredSpiders = networkData?.spiders.filter((spider) => {
    const matchesSearch =
      searchQuery === '' ||
      spider.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      spider.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      spider.category.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesCategory =
      categoryFilter === 'all' || spider.category === categoryFilter

    const matchesStatus =
      statusFilter === 'all' || spider.status === statusFilter

    return matchesSearch && matchesCategory && matchesStatus
  }) || []

  if (networkLoading || healthLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading spider network...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <Breadcrumb currentPage="Spider Integration" />

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Bug className="h-7 w-7 text-primary-400" />
          Spider Integration
        </h1>
        <p className="text-gray-400 mt-1">
          77 data-gathering spiders across 20+ categories
        </p>
      </div>

      {/* Overview Stats */}
      {networkData && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="flex items-center gap-2 text-primary-400 mb-1">
              <Bug className="h-4 w-4" />
              <span className="text-sm text-gray-400">Total Spiders</span>
            </div>
            <div className="text-2xl font-bold text-white">{networkData.totalSpiders}</div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="flex items-center gap-2 text-green-400 mb-1">
              <Activity className="h-4 w-4" />
              <span className="text-sm text-gray-400">Active</span>
            </div>
            <div className="text-2xl font-bold text-white">{networkData.activeSpiders}</div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="flex items-center gap-2 text-blue-400 mb-1">
              <Database className="h-4 w-4" />
              <span className="text-sm text-gray-400">Data Collected</span>
            </div>
            <div className="text-2xl font-bold text-white">
              {networkData.dataCollected.toLocaleString()}
            </div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="flex items-center gap-2 text-yellow-400 mb-1">
              <Zap className="h-4 w-4" />
              <span className="text-sm text-gray-400">Opportunities</span>
            </div>
            <div className="text-2xl font-bold text-white">
              {networkData.opportunitiesFound.toLocaleString()}
            </div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="flex items-center gap-2 text-green-400 mb-1">
              <TrendingUp className="h-4 w-4" />
              <span className="text-sm text-gray-400">Success Rate</span>
            </div>
            <div className="text-2xl font-bold text-white">{networkData.successRate}%</div>
          </div>
        </div>
      )}

      {/* Health Monitoring */}
      {healthData && (
        <div className="grid md:grid-cols-2 gap-4">
          {/* Health Stats */}
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary-400" />
              Health (24h)
            </h2>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-gray-400">Executions</div>
                <div className="text-xl font-bold text-white">
                  {healthData.summary.executions_24h}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Errors</div>
                <div className={`text-xl font-bold ${healthData.summary.errors_24h > 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {healthData.summary.errors_24h}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Success Rate</div>
                <div className={`text-xl font-bold ${healthData.summary.success_rate_24h >= 80 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {(healthData.summary.success_rate_24h ?? 0).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Embedding Coverage */}
            <div className="mt-4 pt-4 border-t border-dark-border">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Embedding Coverage</span>
                <span className="text-sm font-medium text-white">
                  {(healthData.summary.embedding_coverage ?? 0).toFixed(0)}%
                </span>
              </div>
              <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 rounded-full transition-all"
                  style={{ width: `${healthData.summary.embedding_coverage}%` }}
                />
              </div>
            </div>

            {/* Recent Errors */}
            {healthData.recent_errors.length > 0 && (
              <div className="mt-4 pt-4 border-t border-dark-border">
                <div className="text-sm text-gray-400 mb-2">Recent Errors</div>
                <div className="space-y-2">
                  {healthData.recent_errors.slice(0, 3).map((error) => (
                    <div
                      key={error.id}
                      className="flex items-start gap-2 p-2 rounded bg-red-500/10 border border-red-500/20"
                    >
                      <AlertTriangle className="h-4 w-4 text-red-400 shrink-0 mt-0.5" />
                      <div className="min-w-0">
                        <div className="text-sm font-medium text-red-300">
                          {error.spider_name}
                        </div>
                        <div className="text-xs text-red-400/70 truncate">
                          {error.error_message}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Activity Feed */}
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <RefreshCw className="h-5 w-5 text-primary-400" />
              Activity Feed
            </h2>
            <div className="max-h-80 overflow-y-auto">
              {activityData?.activities && activityData.activities.length > 0 ? (
                activityData.activities.slice(0, 10).map((item, i) => (
                  <ActivityFeedItem key={i} item={item} />
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  No recent activity
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Spider Registry */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Bug className="h-5 w-5 text-primary-400" />
            Spider Registry ({filteredSpiders.length})
          </h2>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-wrap gap-3 mb-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search spiders..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-dark-border bg-dark-card text-white placeholder-gray-400"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="rounded-lg border border-dark-border bg-dark-card px-3 py-2 text-white text-sm"
            >
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-lg border border-dark-border bg-dark-card px-3 py-2 text-white text-sm"
            >
              <option value="all">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Idle">Idle</option>
              <option value="Error">Error</option>
            </select>
          </div>
        </div>

        {/* Spider Grid */}
        {filteredSpiders.length === 0 ? (
          <div className="rounded-lg border border-dark-border bg-dark-card p-8 text-center">
            <Bug className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">No spiders match your search criteria</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSpiders.map((spider) => (
              <SpiderCard
                key={spider.id}
                spider={spider}
                onRun={() => runSpiderMutation.mutate(spider.name)}
                isRunning={runningSpider === spider.name}
              />
            ))}
          </div>
        )}
      </div>

      {/* Info Section */}
      <div className="rounded-lg border border-dark-border bg-dark-card p-4">
        <h3 className="flex items-center gap-2 text-white font-medium mb-3">
          <Info className="h-5 w-5 text-primary-400" />
          About the Spider Network
        </h3>
        <div className="text-sm text-gray-400 space-y-2">
          <p>
            The Spider Network is a distributed intelligence gathering system that collects
            real-time data from 77 sources across 20+ categories including finance, tech news,
            legal databases, job markets, and more.
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>
              <strong className="text-gray-300">Data Methods</strong> - REST API (32), RSS (30),
              Web Scraping (10), Playwright (2), JSON (3)
            </li>
            <li>
              <strong className="text-gray-300">Categories</strong> - Financial, Tech, News, Legal,
              Design, Jobs, Social, Entertainment, Education, and more
            </li>
            <li>
              <strong className="text-gray-300">Integration</strong> - Spider data feeds into 72
              specialized agents for analysis and action
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
