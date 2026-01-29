// Session 861B: Workspace Triggers Tab
// Exposes the autonomous workspace trigger queue for monitoring and management

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Zap,
  Loader2,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Play,
  RotateCcw,
  ArrowUp,
  Ban,
  Bot,
  Search,
  Filter,
  Activity,
  TrendingUp,
} from 'lucide-react'
import { workspaceTriggersApi } from '@/lib/api'
import { cn } from '@/lib/cn'

// =============================================================================
// Types
// =============================================================================

interface WorkspaceTrigger {
  id: string
  trigger_type: string
  trigger_type_display: string
  title: string
  description?: string
  workspace_name?: string
  target_agent?: string
  target_category?: string
  source_spider?: string
  priority: number
  priority_display: string
  status: string
  is_expired: boolean
  time_until_expiry?: string
  expires_at: string
  created_at: string
  execution_time_ms?: number
  result_summary?: string
  error_message?: string
  context_data?: Record<string, unknown>
}

interface TriggerStats {
  status_counts: {
    pending: number
    queued: number
    in_progress: number
    completed: number
    failed: number
    expired: number
    skipped: number
  }
  by_type_7d: Record<string, number>
  by_priority_pending: Record<number, number>
  last_24h: {
    completed: number
    failed: number
    avg_execution_time_ms: number
  }
  expired_7d: number
  queue_depth: number
}

interface TriggersTabProps {
  showSuccess: (message: string) => void
  showError: (message: string) => void
}

// =============================================================================
// Stats Dashboard
// =============================================================================

function TriggerStatsDashboard({
  stats,
  isLoading,
}: {
  stats?: TriggerStats
  isLoading: boolean
}) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-4">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="p-3 bg-gray-800/50 rounded-lg border border-gray-700 animate-pulse"
          >
            <div className="h-6 w-12 bg-gray-700 rounded mb-1" />
            <div className="h-3 w-16 bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    )
  }

  if (!stats) return null

  const successRate =
    stats.last_24h.completed + stats.last_24h.failed > 0
      ? Math.round(
          (stats.last_24h.completed /
            (stats.last_24h.completed + stats.last_24h.failed)) *
            100
        )
      : 100

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-4">
      {/* Queue Depth */}
      <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <Activity
            className={cn(
              'w-4 h-4',
              stats.queue_depth > 10 ? 'text-amber-400' : 'text-cyan-400'
            )}
          />
          <span className="text-xl font-bold text-white">
            {stats.queue_depth}
          </span>
        </div>
        <div className="text-xs text-gray-400">Queue Depth</div>
      </div>

      {/* Pending */}
      <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <Clock className="w-4 h-4 text-amber-400" />
          <span className="text-xl font-bold text-white">
            {stats.status_counts.pending}
          </span>
        </div>
        <div className="text-xs text-gray-400">Pending</div>
      </div>

      {/* In Progress */}
      <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <Play className="w-4 h-4 text-blue-400" />
          <span className="text-xl font-bold text-white">
            {stats.status_counts.in_progress}
          </span>
        </div>
        <div className="text-xs text-gray-400">In Progress</div>
      </div>

      {/* Completed (24h) */}
      <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <CheckCircle className="w-4 h-4 text-green-400" />
          <span className="text-xl font-bold text-white">
            {stats.last_24h.completed}
          </span>
        </div>
        <div className="text-xs text-gray-400">Completed (24h)</div>
      </div>

      {/* Failed (24h) */}
      <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <XCircle className="w-4 h-4 text-red-400" />
          <span className="text-xl font-bold text-white">
            {stats.last_24h.failed}
          </span>
        </div>
        <div className="text-xs text-gray-400">Failed (24h)</div>
      </div>

      {/* Success Rate */}
      <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp
            className={cn(
              'w-4 h-4',
              successRate >= 90
                ? 'text-green-400'
                : successRate >= 70
                  ? 'text-amber-400'
                  : 'text-red-400'
            )}
          />
          <span className="text-xl font-bold text-white">{successRate}%</span>
        </div>
        <div className="text-xs text-gray-400">Success Rate</div>
      </div>
    </div>
  )
}

// =============================================================================
// Trigger Card
// =============================================================================

function TriggerCard({
  trigger,
  onCancel,
  onRetry,
  onBumpPriority,
  isActioning,
}: {
  trigger: WorkspaceTrigger
  onCancel: () => void
  onRetry: () => void
  onBumpPriority: () => void
  isActioning: boolean
}) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-amber-400 bg-amber-500/20'
      case 'queued':
        return 'text-blue-400 bg-blue-500/20'
      case 'in_progress':
        return 'text-cyan-400 bg-cyan-500/20'
      case 'completed':
        return 'text-green-400 bg-green-500/20'
      case 'failed':
        return 'text-red-400 bg-red-500/20'
      case 'expired':
        return 'text-gray-400 bg-gray-500/20'
      case 'skipped':
        return 'text-gray-400 bg-gray-500/20'
      default:
        return 'text-gray-400 bg-gray-500/20'
    }
  }

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 5:
        return 'text-red-400 bg-red-500/20'
      case 4:
        return 'text-orange-400 bg-orange-500/20'
      case 3:
        return 'text-amber-400 bg-amber-500/20'
      case 2:
        return 'text-blue-400 bg-blue-500/20'
      default:
        return 'text-gray-400 bg-gray-500/20'
    }
  }

  const canCancel = ['pending', 'queued'].includes(trigger.status)
  const canRetry = ['failed', 'expired', 'skipped'].includes(trigger.status)
  const canBump = trigger.status === 'pending' && trigger.priority < 5

  return (
    <div
      className={cn(
        'border rounded-lg overflow-hidden transition-all',
        trigger.is_expired
          ? 'border-gray-600 bg-gray-800/30 opacity-70'
          : 'border-gray-700 bg-gray-800/50'
      )}
    >
      {/* Header Row */}
      <div
        className="p-3 cursor-pointer hover:bg-gray-700/30 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            {/* Expand Icon */}
            <button className="text-gray-400">
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>

            {/* Type Icon */}
            <Zap size={16} className="text-purple-400 flex-shrink-0" />

            {/* Title & Meta */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm text-white truncate">
                  {trigger.title}
                </span>
                <span
                  className={cn(
                    'text-xs px-1.5 py-0.5 rounded',
                    getPriorityColor(trigger.priority)
                  )}
                >
                  P{trigger.priority}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
                <span>{trigger.trigger_type_display}</span>
                {trigger.source_spider && (
                  <>
                    <span>•</span>
                    <span>via {trigger.source_spider}</span>
                  </>
                )}
                {trigger.target_agent && (
                  <>
                    <span>•</span>
                    <Bot size={10} />
                    <span>{trigger.target_agent}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Status & Timing */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {trigger.execution_time_ms && (
              <span className="text-xs text-gray-500">
                {trigger.execution_time_ms}ms
              </span>
            )}
            <span
              className={cn(
                'text-xs px-2 py-1 rounded capitalize',
                getStatusColor(trigger.status)
              )}
            >
              {trigger.status.replace('_', ' ')}
            </span>
            {!trigger.is_expired &&
              trigger.status === 'pending' &&
              trigger.time_until_expiry && (
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Clock size={10} />
                  {trigger.time_until_expiry}
                </span>
              )}
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-700/50 p-3 bg-gray-900/30 space-y-3">
          {/* Description */}
          {trigger.description && (
            <div>
              <label className="text-xs text-gray-500 block mb-1">
                Description
              </label>
              <p className="text-sm text-gray-300">{trigger.description}</p>
            </div>
          )}

          {/* Context Data */}
          {trigger.context_data && Object.keys(trigger.context_data).length > 0 && (
            <div>
              <label className="text-xs text-gray-500 block mb-1">
                Context Data
              </label>
              <pre className="text-xs bg-dark-bg p-2 rounded overflow-x-auto max-h-32 overflow-y-auto font-mono text-gray-300">
                {JSON.stringify(trigger.context_data, null, 2)}
              </pre>
            </div>
          )}

          {/* Result/Error */}
          {trigger.result_summary && (
            <div>
              <label className="text-xs text-gray-500 block mb-1">Result</label>
              <p className="text-sm text-green-400">{trigger.result_summary}</p>
            </div>
          )}
          {trigger.error_message && (
            <div className="flex items-start gap-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-400">
              <XCircle size={14} className="flex-shrink-0 mt-0.5" />
              <span>{trigger.error_message}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 pt-2 border-t border-gray-700/50">
            {canBump && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onBumpPriority()
                }}
                disabled={isActioning}
                className={cn(
                  'text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all',
                  isActioning
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30 border border-amber-500/30'
                )}
              >
                <ArrowUp size={12} />
                Bump Priority
              </button>
            )}
            {canRetry && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onRetry()
                }}
                disabled={isActioning}
                className={cn(
                  'text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all',
                  isActioning
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-500/30'
                )}
              >
                <RotateCcw size={12} />
                Retry
              </button>
            )}
            {canCancel && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onCancel()
                }}
                disabled={isActioning}
                className={cn(
                  'text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all',
                  isActioning
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30'
                )}
              >
                <Ban size={12} />
                Cancel
              </button>
            )}
            <span className="text-xs text-gray-500 ml-auto">
              Created: {new Date(trigger.created_at).toLocaleString()}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Main Component
// =============================================================================

export function TriggersTab({ showSuccess, showError }: TriggersTabProps) {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [actioningId, setActioningId] = useState<string | null>(null)

  // Fetch triggers
  const { data: triggersData, isLoading: loadingTriggers } = useQuery({
    queryKey: ['workspace-triggers', statusFilter],
    queryFn: () =>
      workspaceTriggersApi.list({
        status: statusFilter || undefined,
        show_expired: true,
      }),
    refetchInterval: 15000, // Refresh every 15 seconds
  })

  // Fetch stats
  const { data: statsData, isLoading: loadingStats } = useQuery({
    queryKey: ['workspace-triggers-stats'],
    queryFn: () => workspaceTriggersApi.stats(),
    refetchInterval: 30000,
  })

  const triggers = (triggersData?.data?.results ||
    triggersData?.data ||
    []) as WorkspaceTrigger[]
  const stats = statsData?.data as TriggerStats | undefined

  // Filter by search
  const filteredTriggers = triggers.filter((t) => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      t.title.toLowerCase().includes(query) ||
      t.trigger_type_display.toLowerCase().includes(query) ||
      t.target_agent?.toLowerCase().includes(query) ||
      t.source_spider?.toLowerCase().includes(query)
    )
  })

  // Mutations
  const cancelMutation = useMutation({
    mutationFn: (id: string) => workspaceTriggersApi.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-triggers'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-triggers-stats'] })
      showSuccess('Trigger cancelled')
      setActioningId(null)
    },
    onError: () => {
      showError('Failed to cancel trigger')
      setActioningId(null)
    },
  })

  const retryMutation = useMutation({
    mutationFn: (id: string) => workspaceTriggersApi.retry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-triggers'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-triggers-stats'] })
      showSuccess('Trigger queued for retry')
      setActioningId(null)
    },
    onError: () => {
      showError('Failed to retry trigger')
      setActioningId(null)
    },
  })

  const bumpMutation = useMutation({
    mutationFn: (id: string) => workspaceTriggersApi.bumpPriority(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-triggers'] })
      showSuccess('Priority increased')
      setActioningId(null)
    },
    onError: () => {
      showError('Failed to bump priority')
      setActioningId(null)
    },
  })

  return (
    <div className="space-y-4">
      {/* Stats Dashboard */}
      <TriggerStatsDashboard stats={stats} isLoading={loadingStats} />

      {/* Filters Row */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search triggers..."
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="queued">Queued</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="expired">Expired</option>
          <option value="skipped">Skipped</option>
        </select>

        {/* Refresh Button */}
        <button
          onClick={() => {
            queryClient.invalidateQueries({ queryKey: ['workspace-triggers'] })
            queryClient.invalidateQueries({
              queryKey: ['workspace-triggers-stats'],
            })
          }}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white hover:border-gray-600 flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw size={14} />
          Refresh
        </button>

        {/* Count */}
        <span className="text-sm text-gray-400">
          {filteredTriggers.length} triggers
        </span>
      </div>

      {/* Triggers List */}
      {loadingTriggers ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={24} className="animate-spin text-purple-400" />
        </div>
      ) : filteredTriggers.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="h-16 w-16 rounded-full bg-gray-800 flex items-center justify-center mb-4">
            <Zap size={32} className="text-gray-500" />
          </div>
          <h3 className="font-semibold text-lg">No triggers found</h3>
          <p className="text-sm text-gray-400 mt-1 max-w-sm">
            {statusFilter
              ? `No ${statusFilter} triggers`
              : 'Workspace triggers will appear here when spiders or agents create them'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredTriggers.map((trigger) => (
            <TriggerCard
              key={trigger.id}
              trigger={trigger}
              onCancel={() => {
                setActioningId(trigger.id)
                cancelMutation.mutate(trigger.id)
              }}
              onRetry={() => {
                setActioningId(trigger.id)
                retryMutation.mutate(trigger.id)
              }}
              onBumpPriority={() => {
                setActioningId(trigger.id)
                bumpMutation.mutate(trigger.id)
              }}
              isActioning={actioningId === trigger.id}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default TriggersTab
