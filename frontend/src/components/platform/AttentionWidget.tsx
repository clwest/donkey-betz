/**
 * Session 933: Unified Attention Widget
 *
 * Displays unified attention from both sources:
 * - System Attention: Platform health metrics (17 items typically)
 * - Human Attention: User notifications, decisions, alerts (600+ items)
 *
 * Features:
 * - Quick stats view (default)
 * - Filter by urgency
 * - Click to expand full list
 * - Color-coded urgency indicators
 */

import { useQuery } from '@tanstack/react-query'
import { assistantApi } from '@/lib/api'
import {
  Bell,
  AlertTriangle,
  AlertCircle,
  Info,
  ChevronRight,
  RefreshCw,
  Server,
  User,
  Filter,
  X,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useState } from 'react'

// Types for unified attention response
interface AttentionItem {
  id: string
  source: 'system' | 'human'
  category: string
  urgency: 'critical' | 'high' | 'medium' | 'low'
  title: string
  summary: string
  created_at: string
  action_url?: string
  source_agent?: string
  item_type?: string
}

interface AttentionSource {
  count: number
  items: AttentionItem[]
  source: string
  description: string
  error?: string
}

interface UnifiedAttentionResponse {
  system_attention: AttentionSource | null
  human_attention: AttentionSource | null
  combined_urgent: number
  total_count: number
  by_urgency: {
    critical: number
    high: number
    medium: number
    low: number
  }
  timestamp: string
}

interface AttentionStats {
  human_attention: {
    pending: number
    total: number
    by_urgency: Record<string, number>
  }
  system_attention: {
    count: number
    by_urgency: Record<string, number>
  }
  combined: {
    pending: number
    urgent: number
  }
  timestamp: string
}

// Urgency configuration
const URGENCY_CONFIG = {
  critical: {
    icon: AlertCircle,
    color: 'text-red-500',
    bg: 'bg-red-500/20',
    border: 'border-red-500/50',
    label: 'Critical',
  },
  high: {
    icon: AlertTriangle,
    color: 'text-orange-500',
    bg: 'bg-orange-500/20',
    border: 'border-orange-500/50',
    label: 'High',
  },
  medium: {
    icon: Bell,
    color: 'text-yellow-500',
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/50',
    label: 'Medium',
  },
  low: {
    icon: Info,
    color: 'text-blue-500',
    bg: 'bg-blue-500/20',
    border: 'border-blue-500/50',
    label: 'Low',
  },
} as const

type UrgencyLevel = keyof typeof URGENCY_CONFIG

interface AttentionWidgetProps {
  compact?: boolean
  showRefresh?: boolean
  onItemClick?: (item: AttentionItem) => void
  className?: string
}

function UrgencyBadge({ urgency, count }: { urgency: UrgencyLevel; count: number }) {
  const config = URGENCY_CONFIG[urgency]
  const Icon = config.icon

  if (count === 0) return null

  return (
    <div
      className={cn(
        'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium',
        config.bg,
        config.color
      )}
    >
      <Icon size={12} />
      <span>{count}</span>
    </div>
  )
}

function AttentionItemRow({
  item,
  onClick,
}: {
  item: AttentionItem
  onClick?: () => void
}) {
  const config = URGENCY_CONFIG[item.urgency]
  const Icon = config.icon

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-start gap-3 p-3 rounded-lg border transition-colors text-left',
        'hover:bg-dark-card/50',
        config.border,
        'bg-dark-bg/50'
      )}
    >
      <div className={cn('mt-0.5', config.color)}>
        <Icon size={16} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white truncate">
            {item.title}
          </span>
          <span
            className={cn(
              'px-1.5 py-0.5 rounded text-xs',
              item.source === 'system' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'
            )}
          >
            {item.source === 'system' ? 'System' : 'User'}
          </span>
        </div>
        <p className="text-xs text-gray-400 truncate mt-0.5">{item.summary}</p>
        {item.source_agent && (
          <p className="text-xs text-gray-500 mt-1">From: {item.source_agent}</p>
        )}
      </div>
      <ChevronRight size={16} className="text-gray-500 mt-1 flex-shrink-0" />
    </button>
  )
}

export function AttentionWidget({
  compact = false,
  showRefresh = true,
  onItemClick,
  className,
}: AttentionWidgetProps) {
  const [expanded, setExpanded] = useState(false)
  const [urgencyFilter, setUrgencyFilter] = useState<UrgencyLevel[]>([])
  const [sourceFilter, setSourceFilter] = useState<'all' | 'system' | 'human'>('all')

  // Fetch stats for compact view
  const {
    data: stats,
    isLoading: statsLoading,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ['attention-stats'],
    queryFn: async () => {
      const response = await assistantApi.getAttentionStats()
      return response.data as AttentionStats
    },
    refetchInterval: 60000, // Refresh every minute
  })

  // Fetch full data when expanded
  const {
    data: fullData,
    isLoading: fullLoading,
    refetch: refetchFull,
  } = useQuery({
    queryKey: ['attention-unified', urgencyFilter, sourceFilter],
    queryFn: async () => {
      const response = await assistantApi.getUnifiedAttention({
        include_system: sourceFilter === 'all' || sourceFilter === 'system',
        include_human: sourceFilter === 'all' || sourceFilter === 'human',
        urgency: urgencyFilter.length > 0 ? urgencyFilter : undefined,
        limit: 50,
      })
      return response.data as UnifiedAttentionResponse
    },
    enabled: expanded,
    refetchInterval: expanded ? 30000 : false, // Refresh every 30s when expanded
  })

  const handleRefresh = () => {
    refetchStats()
    if (expanded) refetchFull()
  }

  const toggleUrgencyFilter = (level: UrgencyLevel) => {
    setUrgencyFilter(prev =>
      prev.includes(level)
        ? prev.filter(u => u !== level)
        : [...prev, level]
    )
  }

  // Combine items from both sources
  const allItems: AttentionItem[] = []
  if (fullData?.system_attention?.items) {
    allItems.push(...fullData.system_attention.items)
  }
  if (fullData?.human_attention?.items) {
    allItems.push(...fullData.human_attention.items)
  }
  // Sort by urgency priority
  const urgencyOrder = { critical: 0, high: 1, medium: 2, low: 3 }
  allItems.sort((a, b) => urgencyOrder[a.urgency] - urgencyOrder[b.urgency])

  // Calculate totals from stats
  const systemCount = stats?.system_attention?.count ?? 0
  const humanCount = stats?.human_attention?.pending ?? 0
  const urgentCount = stats?.combined?.urgent ?? 0
  const totalCount = systemCount + humanCount

  // Compact view
  if (compact && !expanded) {
    return (
      <div
        className={cn(
          'bg-dark-card rounded-xl border border-dark-border p-4',
          className
        )}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Bell className="text-accent-cyan" size={20} />
            <h3 className="text-sm font-semibold text-white">Attention</h3>
          </div>
          {showRefresh && (
            <button
              onClick={handleRefresh}
              className="p-1 hover:bg-dark-border rounded transition-colors"
              disabled={statsLoading}
            >
              <RefreshCw
                size={14}
                className={cn('text-gray-400', statsLoading && 'animate-spin')}
              />
            </button>
          )}
        </div>

        {statsLoading ? (
          <div className="flex items-center justify-center py-4">
            <RefreshCw size={20} className="text-gray-400 animate-spin" />
          </div>
        ) : (
          <>
            {/* Urgency badges row */}
            <div className="flex flex-wrap gap-2 mb-3">
              <UrgencyBadge urgency="critical" count={stats?.combined?.urgent ? Math.min(stats.combined.urgent, stats?.system_attention?.by_urgency?.critical ?? 0 + (stats?.human_attention?.by_urgency?.critical ?? 0)) : 0} />
              {stats?.human_attention?.by_urgency && (
                <>
                  <UrgencyBadge urgency="critical" count={stats.human_attention.by_urgency.critical ?? 0} />
                  <UrgencyBadge urgency="high" count={stats.human_attention.by_urgency.high ?? 0} />
                  <UrgencyBadge urgency="medium" count={stats.human_attention.by_urgency.medium ?? 0} />
                </>
              )}
            </div>

            {/* Source breakdown */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div className="flex items-center gap-2 p-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
                <Server size={14} className="text-purple-400" />
                <div>
                  <p className="text-xs text-gray-400">System</p>
                  <p className="text-lg font-bold text-purple-400">{systemCount}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <User size={14} className="text-blue-400" />
                <div>
                  <p className="text-xs text-gray-400">User</p>
                  <p className="text-lg font-bold text-blue-400">{humanCount}</p>
                </div>
              </div>
            </div>

            {/* Expand button */}
            <button
              onClick={() => setExpanded(true)}
              className="w-full flex items-center justify-center gap-2 py-2 text-sm text-accent-cyan hover:text-accent-cyan/80 transition-colors"
            >
              View {totalCount} items
              <ChevronRight size={16} />
            </button>
          </>
        )}
      </div>
    )
  }

  // Full expanded view
  return (
    <div
      className={cn(
        'bg-dark-card rounded-xl border border-dark-border',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-border">
        <div className="flex items-center gap-2">
          <Bell className="text-accent-cyan" size={20} />
          <h3 className="text-lg font-semibold text-white">Unified Attention</h3>
          {urgentCount > 0 && (
            <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded-full">
              {urgentCount} urgent
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {showRefresh && (
            <button
              onClick={handleRefresh}
              className="p-2 hover:bg-dark-border rounded-lg transition-colors"
              disabled={fullLoading}
            >
              <RefreshCw
                size={16}
                className={cn('text-gray-400', fullLoading && 'animate-spin')}
              />
            </button>
          )}
          {compact && (
            <button
              onClick={() => setExpanded(false)}
              className="p-2 hover:bg-dark-border rounded-lg transition-colors"
            >
              <X size={16} className="text-gray-400" />
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-dark-border space-y-3">
        {/* Source filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 w-16">Source:</span>
          <div className="flex gap-1">
            {(['all', 'system', 'human'] as const).map(source => (
              <button
                key={source}
                onClick={() => setSourceFilter(source)}
                className={cn(
                  'px-3 py-1 rounded-full text-xs font-medium transition-colors',
                  sourceFilter === source
                    ? 'bg-accent-cyan/20 text-accent-cyan'
                    : 'bg-dark-border text-gray-400 hover:text-white'
                )}
              >
                {source === 'all' ? 'All' : source === 'system' ? 'System' : 'User'}
              </button>
            ))}
          </div>
        </div>

        {/* Urgency filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 w-16">Urgency:</span>
          <div className="flex gap-1">
            {(Object.keys(URGENCY_CONFIG) as UrgencyLevel[]).map(level => {
              const config = URGENCY_CONFIG[level]
              const isActive = urgencyFilter.includes(level)
              return (
                <button
                  key={level}
                  onClick={() => toggleUrgencyFilter(level)}
                  className={cn(
                    'px-3 py-1 rounded-full text-xs font-medium transition-colors',
                    isActive
                      ? cn(config.bg, config.color)
                      : 'bg-dark-border text-gray-400 hover:text-white'
                  )}
                >
                  {config.label}
                </button>
              )
            })}
            {urgencyFilter.length > 0 && (
              <button
                onClick={() => setUrgencyFilter([])}
                className="px-2 py-1 text-xs text-gray-400 hover:text-white"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats bar */}
      {fullData && (
        <div className="px-4 py-2 bg-dark-bg/50 border-b border-dark-border">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">
              Showing {allItems.length} of {fullData.total_count} items
            </span>
            <div className="flex gap-3">
              <span className="text-purple-400">
                <Server size={12} className="inline mr-1" />
                {fullData.system_attention?.count ?? 0} system
              </span>
              <span className="text-blue-400">
                <User size={12} className="inline mr-1" />
                {fullData.human_attention?.count ?? 0} user
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Items list */}
      <div className="p-4 max-h-96 overflow-y-auto space-y-2">
        {fullLoading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw size={24} className="text-gray-400 animate-spin" />
          </div>
        ) : allItems.length === 0 ? (
          <div className="text-center py-8">
            <Bell size={32} className="text-gray-600 mx-auto mb-2" />
            <p className="text-gray-400">No attention items</p>
            <p className="text-xs text-gray-500 mt-1">
              {urgencyFilter.length > 0 ? 'Try clearing filters' : 'All clear!'}
            </p>
          </div>
        ) : (
          allItems.map(item => (
            <AttentionItemRow
              key={`${item.source}-${item.id}`}
              item={item}
              onClick={() => {
                if (onItemClick) {
                  onItemClick(item)
                } else if (item.action_url) {
                  window.location.href = item.action_url
                }
              }}
            />
          ))
        )}
      </div>

      {/* Footer with urgency summary */}
      {fullData?.by_urgency && (
        <div className="px-4 py-3 border-t border-dark-border bg-dark-bg/30">
          <div className="flex items-center justify-center gap-4">
            {(Object.entries(fullData.by_urgency) as [UrgencyLevel, number][]).map(
              ([level, count]) => {
                const config = URGENCY_CONFIG[level]
                return (
                  <div key={level} className="flex items-center gap-1 text-xs">
                    <span className={config.color}>{count}</span>
                    <span className="text-gray-500">{config.label}</span>
                  </div>
                )
              }
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Export a minimal stats-only version for use in headers/navbars
export function AttentionBadge({ className }: { className?: string }) {
  const { data: stats } = useQuery({
    queryKey: ['attention-stats'],
    queryFn: async () => {
      const response = await assistantApi.getAttentionStats()
      return response.data as AttentionStats
    },
    refetchInterval: 60000,
  })

  const urgentCount = stats?.combined?.urgent ?? 0

  if (urgentCount === 0) return null

  return (
    <div
      className={cn(
        'flex items-center gap-1 px-2 py-1 rounded-full bg-red-500/20 text-red-400 text-xs font-medium',
        className
      )}
    >
      <AlertCircle size={12} />
      <span>{urgentCount}</span>
    </div>
  )
}
