/**
 * Spider News Feed Page
 *
 * Session 783: Human-facing news feed for spider data with agent annotations.
 * Similar to Reddit/Yahoo News - browse, filter, search, and vote on items.
 *
 * Features:
 * - Feed statistics summary cards
 * - Trending items carousel
 * - Filterable feed (source, category, annotation type, search)
 * - Annotation badges (Breaking News, Profitable, etc.)
 * - Upvote/downvote functionality
 * - Item detail modal
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Newspaper,
  TrendingUp,
  Search,
  ThumbsUp,
  ThumbsDown,
  Clock,
  Tag,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  X,
  Bot,
  AlertTriangle,
  Zap,
  DollarSign,
  Mic,
  Bell,
  Eye,
  Activity,
} from 'lucide-react'
import { spiderFeedApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

// Simple time ago function
function timeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  const intervals = [
    { label: 'year', seconds: 31536000 },
    { label: 'month', seconds: 2592000 },
    { label: 'day', seconds: 86400 },
    { label: 'hour', seconds: 3600 },
    { label: 'minute', seconds: 60 },
  ]

  for (const interval of intervals) {
    const count = Math.floor(seconds / interval.seconds)
    if (count >= 1) {
      return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`
    }
  }
  return 'just now'
}

// Types
interface Annotation {
  type: string
  agent: string
  confidence: number
  note: string
  upvotes: number
  downvotes: number
  created_at: string
}

interface FeedItem {
  id: string
  spider_name: string
  data_type: string
  title: string
  preview: string
  source_url: string
  created_at: string
  relevance_score: number
  is_actionable: boolean
  annotations: Annotation[]
  score: number
  badges: string[]
  annotation_count: number
  raw_data?: Record<string, unknown>
  processed_data?: Record<string, unknown>
  insights?: unknown[]
}

interface FeedResponse {
  status: string
  items: FeedItem[]
  pagination: {
    page: number
    per_page: number
    total_items: number
    total_pages: number
    has_next: boolean
    has_previous: boolean
  }
}

interface StatsResponse {
  status: string
  stats: {
    total_annotated_items: number
    total_annotations: number
    annotations_24h: number
    annotations_7d: number
    top_sources: { spider_name: string; count: number }[]
    type_distribution: { annotation_type: string; count: number }[]
    top_agents: { agent_name: string; count: number }[]
  }
}

// Badge configuration
const BADGE_CONFIG: Record<string, { color: string; icon: React.ElementType; label: string }> = {
  breaking_news: { color: 'bg-red-500/20 text-red-400 border-red-500/30', icon: Zap, label: 'Breaking News' },
  profitable: { color: 'bg-green-500/20 text-green-400 border-green-500/30', icon: DollarSign, label: 'Profitable' },
  podcast_worthy: { color: 'bg-purple-500/20 text-purple-400 border-purple-500/30', icon: Mic, label: 'Podcast Worthy' },
  warning: { color: 'bg-orange-500/20 text-orange-400 border-orange-500/30', icon: AlertTriangle, label: 'Warning' },
  useful: { color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: ThumbsUp, label: 'Useful' },
  trending: { color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30', icon: TrendingUp, label: 'Trending' },
  investment_opportunity: { color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: DollarSign, label: 'Investment' },
  action_required: { color: 'bg-amber-500/20 text-amber-400 border-amber-500/30', icon: Bell, label: 'Action Required' },
}

// Annotation Badge Component
function AnnotationBadge({ type }: { type: string }) {
  const config = BADGE_CONFIG[type] || { color: 'bg-gray-500/20 text-gray-400 border-gray-500/30', icon: Tag, label: type }
  const Icon = config.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  )
}

// Stats Card Component
function StatsCard({ title, value, subtitle, icon: Icon }: { title: string; value: string | number; subtitle?: string; icon: React.ElementType }) {
  return (
    <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-500/20 rounded-lg">
          <Icon className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          <p className="text-xs text-gray-400">{title}</p>
          <p className="text-xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
      </div>
    </div>
  )
}

// Feed Item Card Component
function FeedItemCard({
  item,
  onVote,
  onClick,
}: {
  item: FeedItem
  onVote: (annotationId: string, direction: 'up' | 'down') => void
  onClick: () => void
}) {
  return (
    <div
      className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4 hover:bg-gray-800/70 transition-colors cursor-pointer"
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-gray-700/50 rounded text-xs text-gray-400 font-mono">
            {item.spider_name}
          </span>
          <span className="text-xs text-gray-500">{item.data_type}</span>
        </div>
        <span className="text-xs text-gray-500">
          {item.created_at && timeAgo(item.created_at)}
        </span>
      </div>

      {/* Title & Preview */}
      <h3 className="text-white font-medium mb-1 line-clamp-2">{item.title || 'Untitled'}</h3>
      {item.preview && <p className="text-sm text-gray-400 mb-3 line-clamp-2">{item.preview}</p>}

      {/* Badges */}
      {item.badges.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {item.badges.map((badge) => (
            <AnnotationBadge key={badge} type={badge} />
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        {/* Agent Avatars */}
        <div className="flex items-center gap-1">
          <Bot className="w-4 h-4 text-gray-500" />
          <span className="text-xs text-gray-500">
            {item.annotation_count} annotation{item.annotation_count !== 1 ? 's' : ''}
          </span>
        </div>

        {/* Score & Actions */}
        <div className="flex items-center gap-3" onClick={(e) => e.stopPropagation()}>
          <div className="flex items-center gap-1 text-sm">
            <button
              onClick={() => item.annotations[0] && onVote(item.annotations[0].type, 'up')}
              className="p-1 hover:bg-green-500/20 rounded transition-colors"
            >
              <ThumbsUp className="w-4 h-4 text-gray-400 hover:text-green-400" />
            </button>
            <span className={`font-medium ${item.score > 0 ? 'text-green-400' : item.score < 0 ? 'text-red-400' : 'text-gray-400'}`}>
              {item.score}
            </span>
            <button
              onClick={() => item.annotations[0] && onVote(item.annotations[0].type, 'down')}
              className="p-1 hover:bg-red-500/20 rounded transition-colors"
            >
              <ThumbsDown className="w-4 h-4 text-gray-400 hover:text-red-400" />
            </button>
          </div>
          {item.source_url && (
            <a
              href={item.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1 hover:bg-blue-500/20 rounded transition-colors"
            >
              <ExternalLink className="w-4 h-4 text-gray-400 hover:text-blue-400" />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

// Item Detail Modal Component
function ItemDetailModal({ item, onClose }: { item: FeedItem; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-gray-900 border border-gray-700 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 bg-gray-700/50 rounded text-sm text-gray-400 font-mono">
              {item.spider_name}
            </span>
            <span className="text-sm text-gray-500">{item.data_type}</span>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          <h2 className="text-xl font-bold text-white">{item.title || 'Untitled'}</h2>

          {/* Badges */}
          {item.badges.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {item.badges.map((badge) => (
                <AnnotationBadge key={badge} type={badge} />
              ))}
            </div>
          )}

          {/* Preview */}
          {item.preview && <p className="text-gray-400">{item.preview}</p>}

          {/* Annotations */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-300">Agent Annotations</h3>
            {item.annotations.map((annotation, idx) => (
              <div key={idx} className="bg-gray-800/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AnnotationBadge type={annotation.type} />
                    <span className="text-sm text-gray-400">by {annotation.agent}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {Math.round(annotation.confidence * 100)}% confident
                  </span>
                </div>
                {annotation.note && <p className="text-sm text-gray-400">{annotation.note}</p>}
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <ThumbsUp className="w-3 h-3" /> {annotation.upvotes}
                  </span>
                  <span className="flex items-center gap-1">
                    <ThumbsDown className="w-3 h-3" /> {annotation.downvotes}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Relevance Score:</span>
              <span className="ml-2 text-white">{item.relevance_score}%</span>
            </div>
            <div>
              <span className="text-gray-500">Created:</span>
              <span className="ml-2 text-white">
                {item.created_at && timeAgo(item.created_at)}
              </span>
            </div>
          </div>

          {/* Source Link */}
          {item.source_url && (
            <a
              href={item.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300"
            >
              <ExternalLink className="w-4 h-4" />
              View Source
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

// Main Page Component
export default function SpiderFeedPage() {
  const queryClient = useQueryClient()

  // State
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [source, setSource] = useState<string>('')
  const [annotationType, setAnnotationType] = useState<string>('')
  const [sort, setSort] = useState<'newest' | 'popular' | 'trending'>('newest')
  const [selectedItem, setSelectedItem] = useState<FeedItem | null>(null)

  // Queries
  const { data: statsData } = useQuery({
    queryKey: ['spider-feed-stats'],
    queryFn: async () => {
      const response = await spiderFeedApi.stats()
      return response.data as StatsResponse
    },
  })

  const { data: trendingData } = useQuery({
    queryKey: ['spider-feed-trending'],
    queryFn: async () => {
      const response = await spiderFeedApi.trending({ hours: 24, limit: 6 })
      return response.data as { items: FeedItem[] }
    },
  })

  const { data: feedData, isLoading } = useQuery({
    queryKey: ['spider-feed', page, search, source, annotationType, sort],
    queryFn: async () => {
      const response = await spiderFeedApi.list({
        page,
        per_page: 20,
        search: search || undefined,
        source: source || undefined,
        annotation_type: annotationType || undefined,
        sort,
      })
      return response.data as FeedResponse
    },
  })

  // Mutations
  const voteMutation = useMutation({
    mutationFn: async ({ itemId, annotationId, direction }: { itemId: string; annotationId: string; direction: 'up' | 'down' }) => {
      return spiderFeedApi.vote(itemId, annotationId, direction)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spider-feed'] })
      queryClient.invalidateQueries({ queryKey: ['spider-feed-trending'] })
    },
  })

  const stats = statsData?.stats
  const trending = trendingData?.items || []
  const feed = feedData?.items || []
  const pagination = feedData?.pagination

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      {/* Header */}
      <div className="mb-6">
        <Breadcrumb currentPage="Spider Feed" />
        <div className="flex items-center gap-3 mt-4">
          <Newspaper className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Spider News Feed</h1>
            <p className="text-sm text-gray-400">Agent-annotated intelligence from 77 spiders</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatsCard
            title="Annotated Items"
            value={stats.total_annotated_items}
            icon={Newspaper}
          />
          <StatsCard
            title="Total Annotations"
            value={stats.total_annotations}
            icon={Tag}
          />
          <StatsCard
            title="Last 24 Hours"
            value={stats.annotations_24h}
            subtitle="new annotations"
            icon={Clock}
          />
          <StatsCard
            title="Last 7 Days"
            value={stats.annotations_7d}
            subtitle="annotations"
            icon={Activity}
          />
        </div>
      )}

      {/* Trending Section */}
      {trending.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-5 h-5 text-orange-400" />
            <h2 className="text-lg font-semibold text-white">Trending Now</h2>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {trending.slice(0, 3).map((item) => (
              <FeedItemCard
                key={item.id}
                item={item}
                onVote={(annotationId, direction) =>
                  voteMutation.mutate({ itemId: item.id, annotationId, direction })
                }
                onClick={() => setSelectedItem(item)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-4 flex-wrap">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search feed..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              className="w-full pl-10 pr-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Source Filter */}
          <select
            value={source}
            onChange={(e) => {
              setSource(e.target.value)
              setPage(1)
            }}
            className="px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="">All Sources</option>
            {stats?.top_sources?.map((s) => (
              <option key={s.spider_name} value={s.spider_name}>
                {s.spider_name} ({s.count})
              </option>
            ))}
          </select>

          {/* Annotation Type Filter */}
          <select
            value={annotationType}
            onChange={(e) => {
              setAnnotationType(e.target.value)
              setPage(1)
            }}
            className="px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="">All Types</option>
            {Object.entries(BADGE_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>
                {config.label}
              </option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={sort}
            onChange={(e) => {
              setSort(e.target.value as 'newest' | 'popular' | 'trending')
              setPage(1)
            }}
            className="px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="newest">Newest</option>
            <option value="popular">Most Popular</option>
            <option value="trending">Trending</option>
          </select>
        </div>
      </div>

      {/* Feed */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-12 text-gray-400">Loading feed...</div>
        ) : feed.length === 0 ? (
          <div className="text-center py-12">
            <Eye className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No annotated items found</p>
            <p className="text-sm text-gray-500">Agents will annotate interesting spider data as it comes in</p>
          </div>
        ) : (
          feed.map((item) => (
            <FeedItemCard
              key={item.id}
              item={item}
              onVote={(annotationId, direction) =>
                voteMutation.mutate({ itemId: item.id, annotationId, direction })
              }
              onClick={() => setSelectedItem(item)}
            />
          ))
        )}
      </div>

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={!pagination.has_previous}
            className="p-2 bg-gray-800 border border-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
          >
            <ChevronLeft className="w-5 h-5 text-white" />
          </button>
          <span className="text-gray-400">
            Page {pagination.page} of {pagination.total_pages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
            disabled={!pagination.has_next}
            className="p-2 bg-gray-800 border border-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
          >
            <ChevronRight className="w-5 h-5 text-white" />
          </button>
        </div>
      )}

      {/* Detail Modal */}
      {selectedItem && <ItemDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />}
    </div>
  )
}
