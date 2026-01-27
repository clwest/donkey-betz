/**
 * Session 834: Dreams Panel for Command Tab
 *
 * Shows recent agent dreams with ability to trigger new dreams and react.
 * Replaces the need for the separate Dreams page.
 */

import { useState } from 'react'
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
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { dreamsApi } from '@/lib/api'

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
}

export function DreamsPanel() {
  const queryClient = useQueryClient()
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['dreams-panel'],
    queryFn: async () => {
      const res = await dreamsApi.list({ limit: 10, timeRange: '7d' })
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

  const dreams: Dream[] = data?.dreams || []
  const todayCount = data?.today_count || 0
  const unreadCount = data?.unread_count || 0

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
          {todayCount > 0 && (
            <span className="text-xs px-1.5 py-0.5 bg-accent-purple/20 text-accent-purple rounded">
              {todayCount} today
            </span>
          )}
          {unreadCount > 0 && (
            <span className="text-xs px-1.5 py-0.5 bg-accent-amber/20 text-accent-amber rounded">
              {unreadCount} new
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
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
          <p className="text-gray-400">No recent dreams</p>
          <p className="text-xs text-gray-500 mt-1">Click "Trigger Dreams" to generate agent dreams</p>
        </div>
      ) : (
        <div className="space-y-2">
          {dreams.map((dream) => (
            <DreamCard
              key={dream.id}
              dream={dream}
              isExpanded={expandedId === dream.id}
              onToggle={() => setExpandedId(expandedId === dream.id ? null : dream.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
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

  const getDreamTypeIcon = () => {
    switch (dream.dream_type) {
      case 'insight':
        return <Lightbulb size={14} className="text-accent-amber" />
      case 'creative':
        return <Sparkles size={14} className="text-accent-purple" />
      default:
        return <Cloud size={14} className="text-accent-blue" />
    }
  }

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
          <div className="flex items-center gap-2 mb-1">
            {getDreamTypeIcon()}
            <span className="text-sm font-medium text-white truncate">{dream.title}</span>
            {!dream.shown_to_user && (
              <span className="text-[10px] px-1.5 py-0.5 bg-accent-purple/20 text-accent-purple rounded">NEW</span>
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
            {dream.dream_type && (
              <span className="px-1.5 py-0.5 bg-gray-700 rounded capitalize">
                {dream.dream_type}
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
              {dream.content?.slice(0, 500)}
              {dream.content && dream.content.length > 500 && '...'}
            </p>
          </div>

          {/* Inspiration */}
          {dream.inspiration_source && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Inspiration</h4>
              <p className="text-sm text-gray-400 italic">{dream.inspiration_source}</p>
            </div>
          )}

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

          <a
            href="/agent-social"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
          >
            View All Dreams <ChevronRight size={12} />
          </a>
        </div>
      )}
    </div>
  )
}
