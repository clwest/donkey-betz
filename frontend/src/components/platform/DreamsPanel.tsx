/**
 * Session 834: Dreams Panel for Command Tab
 *
 * Shows recent agent dreams with ability to trigger new dreams and react.
 * Replaces the need for the separate Dreams page.
 *
 * Features:
 * - Time range filter (24h, 7d, 30d)
 * - Dream type filter
 * - Stats overview (total, by type, unread)
 * - Trigger new dreams
 * - React to dreams (love, insightful, like)
 * - Expandable dream content
 */

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Sparkles,
  Cloud,
  ChevronRight,
  ChevronDown,
  Loader2,
  Clock,
  User,
  Heart,
  ThumbsUp,
  Lightbulb,
  RefreshCw,
  Filter,
  Zap,
  Eye,
  Star,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { dreamsApi, type TimeRange } from '@/lib/api'

interface Dream {
  id: string
  title: string
  content: string
  agent_name: string
  agent_id?: string
  dream_type?: string
  dreamed_at: string
  inspiration_source?: string
  shown_to_user?: boolean
  reactions?: Record<string, number>
  rating?: number
}

type DreamTypeFilter = 'all' | 'insight' | 'creative' | 'reflection' | 'synthesis'

export function DreamsPanel() {
  const queryClient = useQueryClient()
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState<TimeRange>('7d')
  const [typeFilter, setTypeFilter] = useState<DreamTypeFilter>('all')

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['dreams-panel', timeRange],
    queryFn: async () => {
      const res = await dreamsApi.list({ limit: 50, timeRange })
      return res.data
    },
    staleTime: 60000,
  })

  const triggerMutation = useMutation({
    mutationFn: () => dreamsApi.trigger(),
    onSuccess: () => {
      // Refetch after a delay to allow dreams to be generated
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['dreams-panel'] })
      }, 2000)
    },
  })

  const allDreams: Dream[] = data?.dreams || []
  const todayCount = data?.today_count || 0
  const unreadCount = data?.unread_count || 0

  // Filter by type
  const dreams = useMemo(() => {
    if (typeFilter === 'all') return allDreams
    return allDreams.filter(d => d.dream_type === typeFilter)
  }, [allDreams, typeFilter])

  // Calculate stats
  const stats = useMemo(() => {
    const byType: Record<string, number> = {}
    allDreams.forEach(d => {
      const type = d.dream_type || 'other'
      byType[type] = (byType[type] || 0) + 1
    })

    const avgRating = allDreams.filter(d => d.rating).length > 0
      ? (allDreams.reduce((sum, d) => sum + (d.rating || 0), 0) / allDreams.filter(d => d.rating).length).toFixed(1)
      : null

    return {
      total: allDreams.length,
      unread: unreadCount,
      today: todayCount,
      byType,
      avgRating,
    }
  }, [allDreams, unreadCount, todayCount])

  if (error) {
    return (
      <div className="card border-accent-red/50">
        <span className="text-accent-red">Failed to load dreams</span>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cloud className="text-accent-purple" size={18} />
          <h3 className="text-md font-semibold uppercase">Agent Dreams</h3>
          {stats.today > 0 && (
            <span className="text-xs px-1.5 py-0.5 bg-accent-purple/20 text-accent-purple rounded">
              {stats.today} today
            </span>
          )}
          {stats.unread > 0 && (
            <span className="text-xs px-1.5 py-0.5 bg-accent-amber/20 text-accent-amber rounded animate-pulse">
              {stats.unread} new
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw size={14} className={isFetching ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={() => triggerMutation.mutate()}
            disabled={triggerMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-accent-purple/20 hover:bg-accent-purple/30 text-accent-purple border border-accent-purple/30 rounded-lg text-sm font-medium transition-colors"
          >
            {triggerMutation.isPending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Sparkles size={16} />
            )}
            Trigger Dreams
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-3">
        <div className="card py-3 text-center">
          <div className="text-xl font-bold text-white">{stats.total}</div>
          <div className="text-xs text-gray-400">Total</div>
        </div>
        <div className="card py-3 text-center">
          <div className="text-xl font-bold text-accent-amber">{stats.unread}</div>
          <div className="text-xs text-gray-400">Unread</div>
        </div>
        <div className="card py-3 text-center">
          <div className="text-xl font-bold text-accent-purple">{stats.today}</div>
          <div className="text-xs text-gray-400">Today</div>
        </div>
        <div className="card py-3 text-center">
          <div className="text-xl font-bold text-accent-green">
            {stats.avgRating || '-'}
          </div>
          <div className="text-xs text-gray-400">Avg Rating</div>
        </div>
      </div>

      {/* Type Distribution */}
      {Object.keys(stats.byType).length > 0 && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(stats.byType).map(([type, count]) => (
            <button
              key={type}
              onClick={() => setTypeFilter(typeFilter === type ? 'all' : type as DreamTypeFilter)}
              className={cn(
                'text-xs px-2 py-1 rounded flex items-center gap-1 transition-colors',
                typeFilter === type
                  ? 'bg-accent-purple/30 text-accent-purple border border-accent-purple/50'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              )}
            >
              {getDreamTypeIcon(type)}
              <span className="capitalize">{type}</span>
              <span className="text-gray-500">{count}</span>
            </button>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          <Filter size={14} className="text-gray-500" />
          <span className="text-xs text-gray-500">Time:</span>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as TimeRange)}
          className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs focus:border-primary-500 focus:outline-none"
        >
          <option value="24h">Last 24h</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="all">All time</option>
        </select>
        <span className="text-xs text-gray-500 ml-auto">
          Showing {dreams.length} of {allDreams.length}
        </span>
      </div>

      {/* Dreams List */}
      {isLoading ? (
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card animate-pulse h-20" />
          ))}
        </div>
      ) : dreams.length === 0 ? (
        <div className="card text-center py-8">
          <Cloud className="mx-auto text-gray-600 mb-3" size={32} />
          <p className="text-gray-400">No dreams found</p>
          <p className="text-xs text-gray-500 mt-1">
            {typeFilter !== 'all' ? 'Try changing the filter or ' : ''}
            Click "Trigger Dreams" to generate agent dreams
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
          {dreams.slice(0, 20).map((dream) => (
            <DreamCard
              key={dream.id}
              dream={dream}
              isExpanded={expandedId === dream.id}
              onToggle={() => setExpandedId(expandedId === dream.id ? null : dream.id)}
            />
          ))}
          {dreams.length > 20 && (
            <div className="text-center py-2 text-xs text-gray-500">
              + {dreams.length - 20} more dreams
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function getDreamTypeIcon(type: string) {
  switch (type) {
    case 'insight':
      return <Lightbulb size={12} className="text-accent-amber" />
    case 'creative':
      return <Sparkles size={12} className="text-accent-purple" />
    case 'reflection':
      return <Eye size={12} className="text-accent-blue" />
    case 'synthesis':
      return <Zap size={12} className="text-accent-green" />
    default:
      return <Cloud size={12} className="text-gray-400" />
  }
}

interface DreamCardProps {
  dream: Dream
  isExpanded: boolean
  onToggle: () => void
}

function DreamCard({ dream, isExpanded, onToggle }: DreamCardProps) {
  const queryClient = useQueryClient()

  const reactMutation = useMutation({
    mutationFn: (reaction: string) => dreamsApi.react(dream.id, reaction),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dreams-panel'] })
    },
  })

  const rateMutation = useMutation({
    mutationFn: (rating: number) => dreamsApi.rate(dream.id, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dreams-panel'] })
    },
  })

  const formatTimeAgo = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  const totalReactions = Object.values(dream.reactions || {}).reduce((sum, n) => sum + n, 0)

  return (
    <div
      className={cn(
        'card cursor-pointer transition-all',
        !dream.shown_to_user && 'border-accent-purple/30 bg-accent-purple/5',
        isExpanded ? 'ring-1 ring-primary-500/50' : 'hover:border-primary-500/50'
      )}
      onClick={onToggle}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            {getDreamTypeIcon(dream.dream_type || 'other')}
            <span className="text-sm font-medium text-white truncate">{dream.title}</span>
            {!dream.shown_to_user && (
              <span className="text-[10px] px-1.5 py-0.5 bg-accent-purple/20 text-accent-purple rounded">NEW</span>
            )}
            {dream.dream_type && (
              <span className="text-[10px] px-1.5 py-0.5 bg-gray-700 text-gray-400 rounded capitalize">
                {dream.dream_type}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <User size={12} />
              {dream.agent_name}
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {formatTimeAgo(dream.dreamed_at)}
            </span>
            {totalReactions > 0 && (
              <span className="flex items-center gap-1 text-accent-red">
                <Heart size={12} />
                {totalReactions}
              </span>
            )}
            {dream.rating && (
              <span className="flex items-center gap-1 text-accent-amber">
                <Star size={12} />
                {dream.rating}
              </span>
            )}
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown size={16} className="text-primary-400 flex-shrink-0" />
        ) : (
          <ChevronRight size={16} className="text-gray-500 flex-shrink-0" />
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-700/50 space-y-3">
          {/* Dream Content */}
          <div>
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Dream Content</h4>
            <p className="text-sm text-gray-300 whitespace-pre-wrap">
              {dream.content?.slice(0, 800)}
              {dream.content && dream.content.length > 800 && '...'}
            </p>
          </div>

          {/* Inspiration */}
          {dream.inspiration_source && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Inspiration</h4>
              <p className="text-sm text-gray-400 italic">{dream.inspiration_source}</p>
            </div>
          )}

          {/* Rating */}
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500">Rate:</span>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  onClick={(e) => {
                    e.stopPropagation()
                    rateMutation.mutate(rating)
                  }}
                  disabled={rateMutation.isPending}
                  className={cn(
                    'p-1 rounded transition-colors',
                    dream.rating && rating <= dream.rating
                      ? 'text-accent-amber'
                      : 'text-gray-600 hover:text-accent-amber'
                  )}
                >
                  <Star size={16} fill={dream.rating && rating <= dream.rating ? 'currentColor' : 'none'} />
                </button>
              ))}
            </div>
          </div>

          {/* Reactions */}
          <div className="flex items-center gap-2 pt-2">
            <span className="text-xs text-gray-500">React:</span>
            <button
              onClick={(e) => {
                e.stopPropagation()
                reactMutation.mutate('love')
              }}
              disabled={reactMutation.isPending}
              className={cn(
                'flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors',
                'bg-gray-800 hover:bg-accent-red/20 hover:text-accent-red'
              )}
            >
              <Heart size={12} />
              {dream.reactions?.love || 0}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                reactMutation.mutate('insightful')
              }}
              disabled={reactMutation.isPending}
              className={cn(
                'flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors',
                'bg-gray-800 hover:bg-accent-amber/20 hover:text-accent-amber'
              )}
            >
              <Lightbulb size={12} />
              {dream.reactions?.insightful || 0}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                reactMutation.mutate('like')
              }}
              disabled={reactMutation.isPending}
              className={cn(
                'flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors',
                'bg-gray-800 hover:bg-accent-blue/20 hover:text-accent-blue'
              )}
            >
              <ThumbsUp size={12} />
              {dream.reactions?.like || 0}
            </button>
          </div>

          {/* Metadata */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>Dreamed: {new Date(dream.dreamed_at).toLocaleString()}</span>
            {dream.agent_id && (
              <a
                href={`/agents?id=${dream.agent_id}`}
                onClick={(e) => e.stopPropagation()}
                className="text-primary-400 hover:text-primary-300"
              >
                View Agent
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
