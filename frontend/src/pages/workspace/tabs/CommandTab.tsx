// Session 825: Command Tab - Platform Command Center
// Extracted from WorkspacePage.tsx for modular architecture
// Session 832: Enhanced Recent Activity with system activity feed

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Activity,
  Shield,
  Heart,
  BookOpen,
  Zap,
  ChevronRight,
  ChevronDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Hash,
  Wrench,
  X,
  // Session 832: New icons for enhanced activity
  Loader2,
  PlayCircle,
  PauseCircle,
  User,
  FileInput,
  MessageSquare,
  Lightbulb,
  Building2,
  FlaskConical,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi, humanApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'
import {
  MissionCard,
  MetricsGrid,
  LiveMetricsDashboard,
  TriggerRulesPanel,
  ActionsPanel,
} from '@/components/platform'
import type { WorkspaceTab } from '../types'

interface CommandTabProps {
  setActiveTab: (tab: WorkspaceTab) => void
  expandedActivityIds: Set<string>
  toggleActivityExpanded: (id: string) => void
}

export function CommandTab({
  setActiveTab,
  expandedActivityIds,
  toggleActivityExpanded,
}: CommandTabProps) {
  const queryClient = useQueryClient()

  // Queries
  const {
    data: missionData,
    isLoading: loadingMission,
    isError: missionError,
    error: missionErrorData,
    refetch: refetchMission,
  } = useQuery({
    queryKey: ['platform-mission'],
    queryFn: async () => {
      const res = await platformApi.mission()
      return res.data
    },
  })

  const {
    data: metricsData,
    isError: metricsError,
    refetch: refetchMetrics,
  } = useQuery({
    queryKey: ['platform-metrics'],
    queryFn: async () => {
      const res = await platformApi.metrics()
      return res.data
    },
  })

  const {
    data: governanceData,
    isError: governanceError,
    refetch: refetchGovernance,
  } = useQuery({
    queryKey: ['platform-governance'],
    queryFn: async () => {
      const res = await platformApi.governance()
      return res.data
    },
  })

  // Session 833: Combined error state
  const hasError = missionError || metricsError || governanceError
  const handleRetry = () => {
    if (missionError) refetchMission()
    if (metricsError) refetchMetrics()
    if (governanceError) refetchGovernance()
  }

  // Decision mutation
  const decisionMutation = useMutation({
    mutationFn: async ({ itemId, decision }: { itemId: string; decision: string }) => {
      const res = await humanApi.decide(itemId, decision)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
      queryClient.invalidateQueries({ queryKey: ['human-attention'] })
    },
  })

  // Session 833: Show error state if any query failed
  if (hasError) {
    return (
      <ErrorState
        error={missionErrorData as Error}
        onRetry={handleRetry}
        message="Failed to load platform data. Please check your connection and try again."
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Mission Card */}
      <MissionCard mission={missionData?.mission} isLoading={loadingMission} />

      {/* Metrics Grid */}
      <MetricsGrid
        metrics={missionData?.metrics_summary}
        isLoading={loadingMission}
        onRevenueClick={() => (window.location.href = '/human?tab=revenue')}
        onCostClick={() => (window.location.href = '/analytics')}
        onCanonClick={() => setActiveTab('knowledge')}
        onPlaybooksClick={() => setActiveTab('knowledge')}
      />

      {/* Quick Actions */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="text-accent-amber" size={18} />
          <h3 className="text-md font-semibold uppercase">Quick Actions</h3>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setActiveTab('governance')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <Shield size={16} className="text-accent-blue" />
            View Governance
          </button>
          <a
            href="/human"
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <Heart size={16} className="text-accent-red" />
            System Health
          </a>
          <button
            onClick={() => setActiveTab('knowledge')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <BookOpen size={16} className="text-accent-purple" />
            Browse Knowledge
          </button>
        </div>
      </div>

      {/* Live Metrics Dashboard */}
      <LiveMetricsDashboard />

      {/* Trigger Rules Panel */}
      <TriggerRulesPanel />

      {/* Actions Panel */}
      <ActionsPanel />

      {/* Session 832: Enhanced Activity Feed with Tabs */}
      <ActivityFeedSection
        recentActivity={metricsData?.recent_activity || []}
        systemActivity={metricsData?.system_activity || { activities: [], counts: {} }}
        expandedActivityIds={expandedActivityIds}
        toggleActivityExpanded={toggleActivityExpanded}
      />

      {/* Pending Decisions Preview */}
      {governanceData?.pending_decisions &&
        governanceData.pending_decisions.length > 0 && (
          <div className="card border border-accent-amber/30">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="text-accent-amber" size={18} />
                <h3 className="text-md font-semibold uppercase">
                  Pending Decisions ({governanceData.pending_decisions_count})
                </h3>
              </div>
              <a
                href="/human?tab=attention"
                className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
              >
                View All
                <ChevronRight size={12} />
              </a>
            </div>
            <div className="space-y-3">
              {governanceData.pending_decisions.slice(0, 3).map((decision: any) => (
                <DecisionCard
                  key={decision.id}
                  decision={decision}
                  onApprove={() =>
                    decisionMutation.mutate({ itemId: decision.id, decision: 'approve' })
                  }
                  onDismiss={() =>
                    decisionMutation.mutate({ itemId: decision.id, decision: 'dismiss' })
                  }
                  isLoading={decisionMutation.isPending}
                />
              ))}
            </div>
          </div>
        )}
    </div>
  )
}

// Session 832: Enhanced Activity Card with status-aware icons and new fields
interface ActivityCardProps {
  activity: any
  isExpanded: boolean
  onToggle: () => void
}

function ActivityCard({ activity, isExpanded, onToggle }: ActivityCardProps) {
  // Session 832: Status-aware icon and styling
  const getStatusIcon = () => {
    switch (activity.status) {
      case 'in_progress':
        return <Loader2 size={14} className="text-accent-amber animate-spin" />
      case 'pending':
        return <PauseCircle size={14} className="text-gray-400" />
      case 'completed':
        return <CheckCircle size={14} className="text-accent-green" />
      case 'failed':
        return <XCircle size={14} className="text-accent-red" />
      default:
        return <PlayCircle size={14} className="text-gray-400" />
    }
  }

  const getStatusBadge = () => {
    switch (activity.status) {
      case 'in_progress':
        return (
          <span className="text-xs px-1.5 py-0.5 bg-accent-amber/20 text-accent-amber rounded animate-pulse">
            Running
          </span>
        )
      case 'pending':
        return (
          <span className="text-xs px-1.5 py-0.5 bg-gray-600/50 text-gray-400 rounded">
            Pending
          </span>
        )
      default:
        return null
    }
  }

  // Session 832: Format time ago
  const formatTimeAgo = (isoString: string) => {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffSecs < 60) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  return (
    <div
      className={cn(
        'rounded-lg transition-all',
        activity.status === 'in_progress'
          ? 'bg-accent-amber/10 border border-accent-amber/30'
          : isExpanded
          ? 'bg-gray-800'
          : 'bg-gray-800/50 hover:bg-gray-800'
      )}
    >
      {/* Header Row */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 cursor-pointer"
      >
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="text-sm text-white">{activity.agent_name}</span>
              {activity.agent_category && (
                <span className="text-xs px-1.5 py-0.5 bg-primary-500/20 text-primary-400 rounded">
                  {activity.agent_category}
                </span>
              )}
              {getStatusBadge()}
            </div>
            <p className="text-xs text-gray-500 truncate max-w-md">{activity.task}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {activity.execution_time_ms && (
            <span className="text-xs text-gray-500">{activity.execution_time_ms}ms</span>
          )}
          {/* Session 832: Show time since start for in_progress, or completion time */}
          {activity.status === 'in_progress' && activity.created_at ? (
            <span className="text-xs text-accent-amber">
              Started {formatTimeAgo(activity.created_at)}
            </span>
          ) : activity.completed_at ? (
            <span className="text-xs text-gray-500">
              {formatTimeAgo(activity.completed_at)}
            </span>
          ) : activity.created_at ? (
            <span className="text-xs text-gray-500">
              {formatTimeAgo(activity.created_at)}
            </span>
          ) : null}
          {isExpanded ? (
            <ChevronDown size={14} className="text-primary-400" />
          ) : (
            <ChevronRight size={14} className="text-gray-600" />
          )}
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-3 pb-3 space-y-3 border-t border-gray-700/50">
          {/* Full Task */}
          <div className="pt-3">
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Task</h4>
            <p className="text-sm text-gray-300">{activity.task_full || activity.task}</p>
          </div>

          {/* Session 832: Triggered by */}
          {activity.triggered_by && (
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <User size={12} />
              <span>Triggered by:</span>
              <span className="text-white">{activity.triggered_by}</span>
            </div>
          )}

          {/* Timing Row - Session 832: Show both start and end times */}
          <div className="flex flex-wrap gap-4 text-xs">
            {activity.created_at && (
              <div className="flex items-center gap-1">
                <PlayCircle size={12} className="text-gray-500" />
                <span className="text-gray-400">Started:</span>
                <span className="text-white">{new Date(activity.created_at).toLocaleString()}</span>
              </div>
            )}
            {activity.completed_at && (
              <div className="flex items-center gap-1">
                <CheckCircle size={12} className="text-gray-500" />
                <span className="text-gray-400">Completed:</span>
                <span className="text-white">{new Date(activity.completed_at).toLocaleString()}</span>
              </div>
            )}
          </div>

          {/* Metrics Row */}
          <div className="flex flex-wrap gap-4 text-xs">
            {activity.execution_time_ms && (
              <div className="flex items-center gap-1">
                <Clock size={12} className="text-gray-500" />
                <span className="text-gray-400">Duration:</span>
                <span className="text-white">{activity.execution_time_ms}ms</span>
              </div>
            )}
            {activity.tokens_used > 0 && (
              <div className="flex items-center gap-1">
                <Hash size={12} className="text-gray-500" />
                <span className="text-gray-400">Tokens:</span>
                <span className="text-white">{activity.tokens_used.toLocaleString()}</span>
              </div>
            )}
            {activity.cost > 0 && (
              <div className="flex items-center gap-1">
                <span className="text-gray-400">Cost:</span>
                <span className="text-accent-green">${activity.cost.toFixed(4)}</span>
              </div>
            )}
          </div>

          {/* Session 832: Input Data */}
          {activity.input_data && Object.keys(activity.input_data).length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-1">
                <FileInput size={12} />
                Input Parameters
              </h4>
              <div className="bg-gray-900/50 rounded p-2 text-xs font-mono space-y-1">
                {Object.entries(activity.input_data).map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <span className="text-primary-400">{key}:</span>
                    <span className="text-gray-300 truncate">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {activity.error_message && (
            <div className="p-2 bg-accent-red/10 rounded border border-accent-red/30">
              <h4 className="text-xs font-semibold text-accent-red uppercase mb-1">Error</h4>
              <p className="text-xs text-gray-300">{activity.error_message}</p>
            </div>
          )}

          {/* Output Summary */}
          {activity.output_summary && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Output</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">
                {activity.output_summary}
              </p>
            </div>
          )}

          {/* Tool Results */}
          {activity.tool_results && activity.tool_results.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">
                Tools Used
              </h4>
              <div className="flex flex-wrap gap-2">
                {activity.tool_results.map(
                  (tool: string | { name?: string; tool?: string }, idx: number) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded flex items-center gap-1"
                    >
                      <Wrench size={10} />
                      {typeof tool === 'string'
                        ? tool
                        : tool.name || tool.tool || 'Unknown'}
                    </span>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Decision Card sub-component
interface DecisionCardProps {
  decision: any
  onApprove: () => void
  onDismiss: () => void
  isLoading: boolean
}

function DecisionCard({ decision, onApprove, onDismiss, isLoading }: DecisionCardProps) {
  return (
    <div className="p-4 bg-gray-800/50 hover:bg-gray-800/80 rounded-lg transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-white truncate">{decision.title}</h4>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-gray-500">
              {decision.source_agent || decision.source_type}
            </span>
            {decision.ml_recommendation && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400">
                AI: {decision.ml_recommendation}
              </span>
            )}
          </div>
        </div>
        <span
          className={cn(
            'text-xs px-2 py-0.5 rounded flex-shrink-0 ml-2',
            decision.urgency === 'critical'
              ? 'bg-accent-red/20 text-accent-red'
              : decision.urgency === 'high'
              ? 'bg-accent-amber/20 text-accent-amber'
              : 'bg-gray-700 text-gray-400'
          )}
        >
          {decision.urgency}
        </span>
      </div>
      <div className="flex items-center gap-2 mt-3">
        <button
          onClick={onApprove}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-green/20 hover:bg-accent-green/30 text-accent-green rounded text-xs font-medium transition-colors disabled:opacity-50"
        >
          <CheckCircle size={12} />
          Approve
        </button>
        <button
          onClick={onDismiss}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-xs font-medium transition-colors disabled:opacity-50"
        >
          <X size={12} />
          Dismiss
        </button>
        <a
          href={`/human?tab=attention&item=${decision.id}`}
          className="flex items-center gap-1.5 px-3 py-1.5 text-gray-400 hover:text-white text-xs transition-colors ml-auto"
        >
          View Details
          <ChevronRight size={12} />
        </a>
      </div>
    </div>
  )
}

// Session 832: Activity Feed Section with tabs for Agent Executions and System Activity
interface ActivityFeedSectionProps {
  recentActivity: any[]
  systemActivity: { activities: any[]; counts: Record<string, number>; total?: number }
  expandedActivityIds: Set<string>
  toggleActivityExpanded: (id: string) => void
}

function ActivityFeedSection({
  recentActivity,
  systemActivity,
  expandedActivityIds,
  toggleActivityExpanded,
}: ActivityFeedSectionProps) {
  const [activeTab, setActiveTab] = useState<'executions' | 'system'>('executions')

  const hasExecutions = recentActivity && recentActivity.length > 0
  const hasSystemActivity = systemActivity?.activities && systemActivity.activities.length > 0

  if (!hasExecutions && !hasSystemActivity) {
    return null
  }

  // Count in-progress executions for badge
  const inProgressCount = recentActivity.filter((a) => a.status === 'in_progress').length

  return (
    <div className="card">
      {/* Tab Headers */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setActiveTab('executions')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors',
              activeTab === 'executions'
                ? 'bg-primary-500/20 text-primary-400'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            )}
          >
            <Activity size={16} />
            Agent Tasks
            {recentActivity.length > 0 && (
              <span className="text-xs bg-gray-700 px-1.5 py-0.5 rounded">
                {recentActivity.length}
              </span>
            )}
            {inProgressCount > 0 && (
              <span className="text-xs bg-accent-amber/20 text-accent-amber px-1.5 py-0.5 rounded animate-pulse">
                {inProgressCount} running
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors',
              activeTab === 'system'
                ? 'bg-primary-500/20 text-primary-400'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            )}
          >
            <Lightbulb size={16} />
            System Activity
            {systemActivity?.total && systemActivity.total > 0 && (
              <span className="text-xs bg-gray-700 px-1.5 py-0.5 rounded">
                {systemActivity.total}
              </span>
            )}
          </button>
        </div>
        <a
          href="/agents"
          className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
        >
          View All Agents
          <ChevronRight size={12} />
        </a>
      </div>

      {/* Tab Content */}
      {activeTab === 'executions' && (
        <div className="space-y-2">
          {recentActivity.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No recent agent executions</p>
          ) : (
            recentActivity.map((activity: any) => (
              <ActivityCard
                key={activity.id}
                activity={activity}
                isExpanded={expandedActivityIds.has(activity.id)}
                onToggle={() => toggleActivityExpanded(activity.id)}
              />
            ))
          )}
        </div>
      )}

      {activeTab === 'system' && (
        <div className="space-y-2">
          {/* Activity type counts */}
          {systemActivity?.counts && Object.keys(systemActivity.counts).length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3 pb-3 border-b border-gray-700/50">
              {Object.entries(systemActivity.counts).map(([type, count]) => (
                <span
                  key={type}
                  className="text-xs px-2 py-1 bg-gray-800 rounded flex items-center gap-1"
                >
                  {getSystemActivityIcon(type)}
                  <span className="capitalize">{type}s</span>
                  <span className="text-gray-500">{count}</span>
                </span>
              ))}
            </div>
          )}

          {systemActivity?.activities?.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No recent system activity</p>
          ) : (
            systemActivity?.activities?.map((item: any) => (
              <SystemActivityCard key={item.id} item={item} />
            ))
          )}
        </div>
      )}
    </div>
  )
}

// Helper to get icon for system activity type
function getSystemActivityIcon(type: string) {
  switch (type) {
    case 'dream':
      return <Lightbulb size={12} className="text-accent-purple" />
    case 'conversation':
      return <MessageSquare size={12} className="text-accent-blue" />
    case 'decision':
      return <Building2 size={12} className="text-accent-amber" />
    case 'pilot':
      return <FlaskConical size={12} className="text-accent-green" />
    default:
      return <Activity size={12} className="text-gray-400" />
  }
}

// System Activity Card for dreams, conversations, decisions, pilots
interface SystemActivityCardProps {
  item: any
}

function SystemActivityCard({ item }: SystemActivityCardProps) {
  const getTypeStyles = () => {
    switch (item.type) {
      case 'dream':
        return {
          bg: 'bg-accent-purple/10',
          border: 'border-accent-purple/30',
          iconColor: 'text-accent-purple',
        }
      case 'conversation':
        return {
          bg: 'bg-accent-blue/10',
          border: 'border-accent-blue/30',
          iconColor: 'text-accent-blue',
        }
      case 'decision':
        return {
          bg: 'bg-accent-amber/10',
          border: 'border-accent-amber/30',
          iconColor: 'text-accent-amber',
        }
      case 'pilot':
        return {
          bg: 'bg-accent-green/10',
          border: 'border-accent-green/30',
          iconColor: 'text-accent-green',
        }
      default:
        return {
          bg: 'bg-gray-800/50',
          border: 'border-gray-700',
          iconColor: 'text-gray-400',
        }
    }
  }

  const styles = getTypeStyles()

  return (
    <div
      className={cn(
        'p-3 rounded-lg border transition-colors hover:bg-opacity-80',
        styles.bg,
        styles.border
      )}
    >
      <div className="flex items-start gap-3">
        <span className={cn('text-lg', styles.iconColor)}>{item.icon || '📋'}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-white truncate">{item.title}</span>
            <span className="text-xs text-gray-500 capitalize">{item.type}</span>
          </div>
          <p className="text-xs text-gray-400 truncate">{item.subtitle}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            {item.agent_name && (
              <span className="flex items-center gap-1">
                <User size={10} />
                {item.agent_name}
              </span>
            )}
            {item.timestamp_display && (
              <span className="flex items-center gap-1">
                <Clock size={10} />
                {item.timestamp_display}
              </span>
            )}
            {item.status && (
              <span
                className={cn(
                  'px-1.5 py-0.5 rounded',
                  item.status === 'approved' || item.status === 'success'
                    ? 'bg-accent-green/20 text-accent-green'
                    : item.status === 'rejected' || item.status === 'failure'
                    ? 'bg-accent-red/20 text-accent-red'
                    : 'bg-gray-700 text-gray-400'
                )}
              >
                {item.status}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
