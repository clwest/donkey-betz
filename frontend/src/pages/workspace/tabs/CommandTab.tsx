// Session 825: Command Tab - Platform Command Center
// Extracted from WorkspacePage.tsx for modular architecture
// Session 832: Enhanced Recent Activity with system activity feed
// Session 834: Clickable System Activity cards with expanded details

import React, { useState, useMemo } from 'react'
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
  // Session 849: Help icon for "Needs Input" badge
  HelpCircle,
  // Session 850: Inbox view icons
  Inbox,
  FolderOpen,
  Link2,
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
  ConversationsPanel,
  DreamsPanel,
  AdvisorsPanel,
  ConversationDetailModal,
  DreamDetailModal,
  DecisionDetailModal,
} from '@/components/platform'
// Session 1035: CommandTab is used by PlatformPage — setActiveTab accepts string (platform tab IDs)

interface CommandTabProps {
  setActiveTab: (tab: string) => void
  expandedActivityIds: Set<string>
  toggleActivityExpanded: (id: string) => void
}

export function CommandTab({
  setActiveTab,
  expandedActivityIds,
  toggleActivityExpanded,
}: CommandTabProps) {
  const queryClient = useQueryClient()

  // Session 834: Modal state for viewing conversations and dreams inline
  // Session 843: Added decision modal state
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [selectedDreamId, setSelectedDreamId] = useState<string | null>(null)
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null)
  // Session 848: Decision error feedback
  const [decisionError, setDecisionError] = useState<string | null>(null)
  // Session 855: Toggle to show all decisions inline
  const [showAllDecisions, setShowAllDecisions] = useState(false)

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
  // Session 848: Added error handling to surface failures to user
  const decisionMutation = useMutation({
    mutationFn: async ({ itemId, decision }: { itemId: string; decision: string }) => {
      const res = await humanApi.decide(itemId, decision)
      return res.data
    },
    onSuccess: () => {
      setDecisionError(null)
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
      queryClient.invalidateQueries({ queryKey: ['human-attention'] })
    },
    onError: (error: any) => {
      // Session 848: Show error feedback when decision fails
      const message = error?.response?.data?.error || error?.message || 'Failed to record decision'
      setDecisionError(message)
      console.error('Decision error:', error)
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

      {/* Metrics Grid - Session 857: Removed external navigation, cards are informational or navigate within workspace */}
      <MetricsGrid
        metrics={missionData?.metrics_summary}
        isLoading={loadingMission}
        onRevenueClick={() => setActiveTab('governance')}
        onCostClick={() => setActiveTab('infrastructure')}
        onCanonClick={() => setActiveTab('knowledge')}
        onPlaybooksClick={() => setActiveTab('knowledge')}
      />

      {/* Quick Actions - Session 857: All actions navigate within workspace */}
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
          <button
            onClick={() => setActiveTab('infrastructure')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <Heart size={16} className="text-accent-red" />
            System Health
          </button>
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

      {/* Session 834: Conversations, Dreams & Advisors Panels */}
      <ConversationsPanel />
      <DreamsPanel />
      <AdvisorsPanel />

      {/* Session 832: Enhanced Activity Feed with Tabs */}
      <ActivityFeedSection
        recentActivity={metricsData?.recent_activity || []}
        systemActivity={metricsData?.system_activity || { activities: [], counts: {} }}
        expandedActivityIds={expandedActivityIds}
        toggleActivityExpanded={toggleActivityExpanded}
        onViewConversation={(id) => setSelectedConversationId(id)}
        onViewDream={(id) => setSelectedDreamId(id)}
        onViewDecision={(id) => setSelectedDecisionId(id)}
        setActiveTab={setActiveTab}
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
              <div className="flex items-center gap-3">
                {/* Session 855: Toggle to show all inline */}
                {governanceData.pending_decisions.length > 3 && (
                  <button
                    onClick={() => setShowAllDecisions(!showAllDecisions)}
                    className="text-xs text-gray-400 hover:text-white flex items-center gap-1 cursor-pointer"
                  >
                    {showAllDecisions ? 'Show Less' : `Show All ${governanceData.pending_decisions.length}`}
                    {showAllDecisions ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                  </button>
                )}
                {/* Session 857: Navigate to governance tab instead of external page */}
                <button
                  onClick={() => setActiveTab('governance')}
                  className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1 cursor-pointer"
                >
                  View in Governance
                  <ChevronRight size={12} />
                </button>
              </div>
            </div>
            {/* Session 855: Scrollable area when showing all */}
            <div className={cn(
              "space-y-3",
              showAllDecisions && governanceData.pending_decisions.length > 5 && "max-h-96 overflow-y-auto pr-2"
            )}>
              {(showAllDecisions
                ? governanceData.pending_decisions
                : governanceData.pending_decisions.slice(0, 3)
              ).map((decision: any) => (
                <DecisionCard
                  key={decision.id}
                  decision={decision}
                  onApprove={() =>
                    decisionMutation.mutate({ itemId: decision.id, decision: 'approve' })
                  }
                  onDismiss={() =>
                    decisionMutation.mutate({ itemId: decision.id, decision: 'dismiss' })
                  }
                  // Session 845: View details in modal instead of navigating
                  onViewDetails={() => setSelectedDecisionId(decision.id)}
                  isLoading={decisionMutation.isPending}
                />
              ))}
            </div>
            {/* Session 848: Show error feedback when decision fails */}
            {decisionError && (
              <div className="mt-3 flex items-center gap-2 p-3 bg-accent-red/10 border border-accent-red/30 rounded-lg text-sm text-accent-red">
                <XCircle size={16} />
                <span>{decisionError}</span>
                <button
                  onClick={() => setDecisionError(null)}
                  className="ml-auto text-current opacity-60 hover:opacity-100"
                >
                  <X size={14} />
                </button>
              </div>
            )}
          </div>
        )}

      {/* Session 834: Detail Modals for inline viewing */}
      {selectedConversationId && (
        <ConversationDetailModal
          conversationId={selectedConversationId}
          onClose={() => setSelectedConversationId(null)}
        />
      )}
      {selectedDreamId && (
        <DreamDetailModal
          dreamId={selectedDreamId}
          onClose={() => setSelectedDreamId(null)}
        />
      )}
      {/* Session 843: Decision detail modal for inline viewing */}
      {selectedDecisionId && (
        <DecisionDetailModal
          decisionId={selectedDecisionId}
          onClose={() => setSelectedDecisionId(null)}
        />
      )}
    </div>
  )
}

// Session 851: Helper component for rendering input parameter values cleanly
// Avoids raw JSON display by formatting objects into readable key-value pairs
// Session 910: Expandable InputParamRow with full data display
function InputParamRow({ name, value }: { name: string; value: unknown }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const MAX_STRING_LENGTH = 200
  const MAX_INITIAL_FIELDS = 5

  // Handle null/undefined
  if (value === null || value === undefined) {
    return (
      <div className="flex items-start gap-2">
        <span className="text-primary-400 font-medium font-mono">{name}:</span>
        <span className="text-gray-500 italic">null</span>
      </div>
    )
  }

  // Handle arrays
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return (
        <div className="flex items-start gap-2">
          <span className="text-primary-400 font-medium font-mono">{name}:</span>
          <span className="text-gray-500 italic">empty array</span>
        </div>
      )
    }
    // Simple array of primitives
    if (value.every(v => typeof v !== 'object' || v === null)) {
      const displayItems = isExpanded ? value : value.slice(0, 10)
      return (
        <div className="flex flex-col gap-1">
          <span className="text-primary-400 font-medium font-mono">{name}:</span>
          <div className="pl-3 flex flex-wrap gap-1">
            {displayItems.map((item, idx) => (
              <span key={idx} className="px-1.5 py-0.5 bg-gray-800 rounded text-gray-300">
                {String(item)}
              </span>
            ))}
            {value.length > 10 && !isExpanded && (
              <button
                onClick={() => setIsExpanded(true)}
                className="px-1.5 py-0.5 text-primary-400 hover:text-primary-300 text-xs"
              >
                +{value.length - 10} more
              </button>
            )}
          </div>
        </div>
      )
    }
    // Array of objects - show count with expandable detail
    return (
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="text-primary-400 font-medium font-mono">{name}:</span>
          <span className="text-gray-400">{value.length} item{value.length !== 1 ? 's' : ''}</span>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-primary-400 hover:text-primary-300 text-xs"
          >
            {isExpanded ? 'collapse' : 'expand'}
          </button>
        </div>
        {isExpanded && (
          <pre className="pl-3 text-xs text-gray-300 bg-gray-900 rounded p-2 overflow-auto max-h-48">
            {JSON.stringify(value, null, 2)}
          </pre>
        )}
      </div>
    )
  }

  // Handle objects
  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
    if (entries.length === 0) {
      return (
        <div className="flex items-start gap-2">
          <span className="text-primary-400 font-medium font-mono">{name}:</span>
          <span className="text-gray-500 italic">empty object</span>
        </div>
      )
    }
    // Session 910: Show all fields with expand/collapse for large objects
    const displayEntries = isExpanded ? entries : entries.slice(0, MAX_INITIAL_FIELDS)
    const hasMore = entries.length > MAX_INITIAL_FIELDS
    return (
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="text-primary-400 font-medium font-mono">{name}:</span>
          {hasMore && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-primary-400 hover:text-primary-300 text-xs"
            >
              {isExpanded ? `collapse (${entries.length} fields)` : `expand all (${entries.length} fields)`}
            </button>
          )}
        </div>
        <div className="pl-3 space-y-1">
          {displayEntries.map(([k, v]) => (
            <div key={k} className="flex items-start gap-2 text-gray-300">
              <span className="text-gray-500 shrink-0">{k}:</span>
              <span className={typeof v === 'boolean' ? (v ? 'text-accent-green' : 'text-accent-red') : 'break-words'}>
                {typeof v === 'object' && v !== null
                  ? Array.isArray(v)
                    ? `[${v.length} items]`
                    : `{${Object.keys(v).length} fields}`
                  : typeof v === 'boolean'
                    ? v ? 'true' : 'false'
                    : String(v)}
              </span>
            </div>
          ))}
          {hasMore && !isExpanded && (
            <button
              onClick={() => setIsExpanded(true)}
              className="text-gray-500 hover:text-gray-300 text-[10px]"
            >
              +{entries.length - MAX_INITIAL_FIELDS} more fields
            </button>
          )}
        </div>
      </div>
    )
  }

  // Handle booleans
  if (typeof value === 'boolean') {
    return (
      <div className="flex items-start gap-2">
        <span className="text-primary-400 font-medium font-mono">{name}:</span>
        <span className={value ? 'text-accent-green' : 'text-accent-red'}>
          {value ? 'true' : 'false'}
        </span>
      </div>
    )
  }

  // Handle primitives (string, number)
  // Session 910: Make long strings expandable
  const stringValue = String(value)
  const isLongString = stringValue.length > MAX_STRING_LENGTH

  if (isLongString && !isExpanded) {
    return (
      <div className="flex flex-col gap-1">
        <span className="text-primary-400 font-medium font-mono">{name}:</span>
        <div className="pl-3">
          <span className="text-gray-300 break-words whitespace-pre-wrap">
            {stringValue.slice(0, MAX_STRING_LENGTH)}...
          </span>
          <button
            onClick={() => setIsExpanded(true)}
            className="ml-2 text-primary-400 hover:text-primary-300 text-xs"
          >
            show more ({stringValue.length} chars)
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <span className="text-primary-400 font-medium font-mono">{name}:</span>
        {isLongString && (
          <button
            onClick={() => setIsExpanded(false)}
            className="text-primary-400 hover:text-primary-300 text-xs"
          >
            collapse
          </button>
        )}
      </div>
      <pre className={cn(
        "text-gray-300 whitespace-pre-wrap break-words",
        isLongString ? "pl-3 bg-gray-900 rounded p-2 text-xs max-h-96 overflow-auto" : ""
      )}>
        {stringValue}
      </pre>
    </div>
  )
}

// Session 832: Enhanced Activity Card with status-aware icons and new fields
interface ActivityCardProps {
  activity: any
  isExpanded: boolean
  onToggle: () => void
}

// Session 839: Helper to check if activity is in running state
// Backend uses 'running', some legacy code uses 'in_progress'
const isRunningStatus = (status: string) => status === 'running' || status === 'in_progress'

function ActivityCard({ activity, isExpanded, onToggle }: ActivityCardProps) {
  // Session 832: Status-aware icon and styling
  // Session 839: Handle both 'running' (backend) and 'in_progress' (legacy)
  const getStatusIcon = () => {
    switch (activity.status) {
      case 'in_progress':
      case 'running':
        return <Loader2 size={14} className="text-accent-amber animate-spin" />
      case 'pending':
      case 'initializing':
        return <PauseCircle size={14} className="text-gray-400" />
      case 'completed':
        return <CheckCircle size={14} className="text-accent-green" />
      case 'failed':
      case 'cancelled':
        return <XCircle size={14} className="text-accent-red" />
      default:
        return <PlayCircle size={14} className="text-gray-400" />
    }
  }

  const getStatusBadge = () => {
    switch (activity.status) {
      case 'in_progress':
      case 'running':
        return (
          <span className="text-xs px-1.5 py-0.5 bg-accent-amber/20 text-accent-amber rounded animate-pulse">
            Running
          </span>
        )
      case 'pending':
      case 'initializing':
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
        // Session 839: Handle both 'running' (backend) and 'in_progress' (legacy)
        isRunningStatus(activity.status)
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
          {/* Session 832: Show time since start for running, or completion time */}
          {/* Session 839: Handle both 'running' and 'in_progress' */}
          {isRunningStatus(activity.status) && activity.created_at ? (
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

          {/* Session 832: Input Data - Session 834: Fixed truncation, show full values */}
          {/* Session 851: Improved object value rendering to avoid raw JSON display */}
          {activity.input_data && Object.keys(activity.input_data).length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-1">
                <FileInput size={12} />
                Input Parameters
              </h4>
              <div className="bg-gray-900/50 rounded p-2 text-xs space-y-2 max-h-64 overflow-y-auto">
                {Object.entries(activity.input_data).map(([key, value]) => (
                  <InputParamRow key={key} name={key} value={value} />
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

// Session 849: Helper to detect if a decision needs human input (contains questions)
function needsHumanDecision(decision: any): boolean {
  // Check title, summary, and key_insights for question marks
  const title = decision.title || ''
  const summary = decision.summary || ''
  const keyInsights = decision.key_insights || []

  if (title.includes('?') || summary.includes('?')) {
    return true
  }

  // Check key_insights array for questions
  if (Array.isArray(keyInsights)) {
    return keyInsights.some((insight: string) => insight.includes('?'))
  }

  return false
}

// Decision Card sub-component
// Session 845: Added onViewDetails for inline modal viewing
// Session 849: Added "Needs Decision" badge for items with questions
interface DecisionCardProps {
  decision: any
  onApprove: () => void
  onDismiss: () => void
  onViewDetails?: () => void
  isLoading: boolean
}

function DecisionCard({ decision, onApprove, onDismiss, onViewDetails, isLoading }: DecisionCardProps) {
  const needsInput = needsHumanDecision(decision)

  return (
    <div className="p-4 bg-gray-800/50 hover:bg-gray-800/80 rounded-lg transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium text-white truncate">{decision.title}</h4>
            {/* Session 849: "Needs Decision" badge for items with questions */}
            {needsInput && (
              <span className="flex items-center gap-1 text-xs px-1.5 py-0.5 rounded bg-accent-purple/20 text-accent-purple flex-shrink-0">
                <HelpCircle size={10} />
                Needs Input
              </span>
            )}
          </div>
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
      {/* Session 845: Show summary preview if available */}
      {decision.summary && (
        <p className="text-xs text-gray-400 mt-2 line-clamp-2">{decision.summary}</p>
      )}
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
        {/* Session 845: View details opens modal instead of navigating */}
        <button
          onClick={onViewDetails}
          className="flex items-center gap-1.5 px-3 py-1.5 text-gray-400 hover:text-white text-xs transition-colors ml-auto"
        >
          View Details
          <ChevronRight size={12} />
        </button>
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
  // Session 834: Callbacks for viewing details in modals
  // Session 843: Added onViewDecision for inline decision viewing
  onViewConversation?: (id: string) => void
  onViewDream?: (id: string) => void
  onViewDecision?: (id: string) => void
  // Session 857: Navigate within workspace instead of external navigation
  setActiveTab?: (tab: string) => void
}

function ActivityFeedSection({
  recentActivity,
  systemActivity,
  expandedActivityIds,
  toggleActivityExpanded,
  onViewConversation,
  onViewDream,
  onViewDecision,
  setActiveTab,
}: ActivityFeedSectionProps) {
  const [feedTab, setFeedTab] = useState<'executions' | 'system'>('executions')
  // Session 850: Sub-view for system activity - chronological or inbox (grouped by initiative)
  const [systemView, setSystemView] = useState<'chrono' | 'inbox'>('chrono')
  // Session 850: Track expanded initiative groups in inbox view
  const [expandedInitiatives, setExpandedInitiatives] = useState<Set<string>>(new Set())

  const hasExecutions = recentActivity && recentActivity.length > 0
  const hasSystemActivity = systemActivity?.activities && systemActivity.activities.length > 0

  // Count in-progress executions for badge
  // Session 839: Handle both 'running' (backend) and 'in_progress' (legacy)
  const inProgressCount = recentActivity.filter((a) => isRunningStatus(a.status)).length

  // Session 850: Group activities by initiative for inbox view
  // Session 851: Moved useMemo BEFORE early return to avoid React hook order violation
  const groupedByInitiative = useMemo(() => {
    if (!systemActivity?.activities) return { linked: {}, unlinked: [] }

    const linked: Record<string, { name: string; items: any[] }> = {}
    const unlinked: any[] = []

    for (const item of systemActivity.activities) {
      if (item.initiative_id && item.initiative_name) {
        if (!linked[item.initiative_id]) {
          linked[item.initiative_id] = { name: item.initiative_name, items: [] }
        }
        linked[item.initiative_id].items.push(item)
      } else {
        unlinked.push(item)
      }
    }

    return { linked, unlinked }
  }, [systemActivity?.activities])

  // Session 850: Count initiatives with items
  const initiativeCount = Object.keys(groupedByInitiative.linked).length

  // Session 851: Early return moved AFTER all hooks to satisfy React rules
  if (!hasExecutions && !hasSystemActivity) {
    return null
  }

  const toggleInitiativeExpanded = (id: string) => {
    setExpandedInitiatives((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  return (
    <div className="card">
      {/* Tab Headers */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setFeedTab('executions')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors',
              feedTab === 'executions'
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
            onClick={() => setFeedTab('system')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors',
              feedTab === 'system'
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
        {/* Session 857: Navigate to intelligence tab instead of external page */}
        {setActiveTab && (
          <button
            onClick={() => setActiveTab('intelligence')}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            View All Agents
            <ChevronRight size={12} />
          </button>
        )}
      </div>

      {/* Tab Content */}
      {feedTab === 'executions' && (
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

      {feedTab === 'system' && (
        <div className="space-y-2">
          {/* Session 850: View toggle - Chronological vs Inbox */}
          <div className="flex items-center justify-between mb-3 pb-3 border-b border-gray-700/50">
            {/* Activity type counts */}
            <div className="flex flex-wrap gap-2">
              {systemActivity?.counts && Object.keys(systemActivity.counts).length > 0 &&
                Object.entries(systemActivity.counts).map(([type, count]) => (
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
            {/* View toggle */}
            <div className="flex items-center gap-1 bg-gray-800/50 rounded-lg p-0.5">
              <button
                onClick={() => setSystemView('chrono')}
                className={cn(
                  'flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors',
                  systemView === 'chrono'
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:text-white'
                )}
                title="Chronological view"
              >
                <Clock size={12} />
                Recent
              </button>
              <button
                onClick={() => setSystemView('inbox')}
                className={cn(
                  'flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors',
                  systemView === 'inbox'
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:text-white'
                )}
                title="Inbox view - grouped by initiative"
              >
                <Inbox size={12} />
                Inbox
                {initiativeCount > 0 && (
                  <span className="text-[10px] bg-primary-500/30 text-primary-400 px-1 rounded">
                    {initiativeCount}
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Chronological View */}
          {systemView === 'chrono' && (
            <>
              {systemActivity?.activities?.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">No recent system activity</p>
              ) : (
                systemActivity?.activities?.map((item: any) => (
                  <SystemActivityCard
                    key={item.id}
                    item={item}
                    onViewConversation={onViewConversation}
                    onViewDream={onViewDream}
                    onViewDecision={onViewDecision}
                  />
                ))
              )}
            </>
          )}

          {/* Session 850: Inbox View - Grouped by Initiative */}
          {systemView === 'inbox' && (
            <div className="space-y-3">
              {/* Linked to Initiatives */}
              {Object.entries(groupedByInitiative.linked).map(([initId, group]) => (
                <div key={initId} className="rounded-lg border border-primary-500/30 bg-primary-500/5 overflow-hidden">
                  <button
                    onClick={() => toggleInitiativeExpanded(initId)}
                    className="w-full flex items-center justify-between p-3 hover:bg-primary-500/10 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <FolderOpen size={16} className="text-primary-400" />
                      <span className="text-sm font-medium text-white">{group.name}</span>
                      <span className="text-xs bg-primary-500/20 text-primary-400 px-1.5 py-0.5 rounded">
                        {group.items.length} item{group.items.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    {expandedInitiatives.has(initId) ? (
                      <ChevronDown size={16} className="text-gray-400" />
                    ) : (
                      <ChevronRight size={16} className="text-gray-400" />
                    )}
                  </button>
                  {expandedInitiatives.has(initId) && (
                    <div className="border-t border-primary-500/20 p-2 space-y-2">
                      {group.items.map((item: any) => (
                        <SystemActivityCard
                          key={item.id}
                          item={item}
                          onViewConversation={onViewConversation}
                          onViewDream={onViewDream}
                          onViewDecision={onViewDecision}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {/* Unlinked Items */}
              {groupedByInitiative.unlinked.length > 0 && (
                <div className="rounded-lg border border-gray-700 bg-gray-800/30 overflow-hidden">
                  <button
                    onClick={() => toggleInitiativeExpanded('__unlinked__')}
                    className="w-full flex items-center justify-between p-3 hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <Link2 size={16} className="text-gray-500" />
                      <span className="text-sm font-medium text-gray-400">Unlinked Items</span>
                      <span className="text-xs bg-gray-700 text-gray-400 px-1.5 py-0.5 rounded">
                        {groupedByInitiative.unlinked.length}
                      </span>
                    </div>
                    {expandedInitiatives.has('__unlinked__') ? (
                      <ChevronDown size={16} className="text-gray-500" />
                    ) : (
                      <ChevronRight size={16} className="text-gray-500" />
                    )}
                  </button>
                  {expandedInitiatives.has('__unlinked__') && (
                    <div className="border-t border-gray-700/50 p-2 space-y-2">
                      {groupedByInitiative.unlinked.map((item: any) => (
                        <SystemActivityCard
                          key={item.id}
                          item={item}
                          onViewConversation={onViewConversation}
                          onViewDream={onViewDream}
                          onViewDecision={onViewDecision}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Empty state */}
              {Object.keys(groupedByInitiative.linked).length === 0 &&
                groupedByInitiative.unlinked.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">No system activity</p>
                )}
            </div>
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
  // Session 834: Callbacks for viewing details in modals
  // Session 843: Added onViewDecision for inline decision viewing
  onViewConversation?: (id: string) => void
  onViewDream?: (id: string) => void
  onViewDecision?: (id: string) => void
}

function SystemActivityCard({ item, onViewConversation, onViewDream, onViewDecision }: SystemActivityCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Session 842: Handle card click - open modal for dreams/conversations, expand for others
  // Session 843: Added decision modal support
  const handleCardClick = () => {
    if (item.type === 'dream' && onViewDream) {
      onViewDream(item.id)
    } else if (item.type === 'conversation' && onViewConversation) {
      onViewConversation(item.id)
    } else if (item.type === 'decision' && onViewDecision) {
      onViewDecision(item.id)
    } else {
      setIsExpanded(!isExpanded)
    }
  }

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
        'rounded-lg border transition-all cursor-pointer',
        styles.bg,
        styles.border,
        isExpanded ? 'ring-1 ring-primary-500/50' : 'hover:border-primary-500/50 hover:bg-white/5'
      )}
      onClick={handleCardClick}
    >
      {/* Clickable Header - Session 842: Opens modal for dreams/conversations */}
      <div className="w-full p-3 text-left">
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
          <ChevronRight
            size={16}
            className={cn(
              'text-gray-500 transition-transform flex-shrink-0',
              isExpanded && 'rotate-90'
            )}
          />
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-3 pb-3 pt-0 space-y-3 border-t border-gray-700/50 mt-1">
          {/* Full Title */}
          {item.title && item.title.length > 40 && (
            <div className="pt-3">
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Full Title</h4>
              <p className="text-sm text-white">{item.title}</p>
            </div>
          )}

          {/* Full Subtitle/Description */}
          {item.subtitle && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Description</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{item.subtitle}</p>
            </div>
          )}

          {/* Content/Details */}
          {item.content && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Content</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{item.content}</p>
            </div>
          )}

          {/* Metadata */}
          <div className="flex flex-wrap gap-4 text-xs">
            {item.agent_name && (
              <div className="flex items-center gap-1">
                <User size={12} className="text-gray-500" />
                <span className="text-gray-400">Agent:</span>
                <span className="text-white">{item.agent_name}</span>
              </div>
            )}
            {item.created_at && (
              <div className="flex items-center gap-1">
                <Clock size={12} className="text-gray-500" />
                <span className="text-gray-400">Created:</span>
                <span className="text-white">{new Date(item.created_at).toLocaleString()}</span>
              </div>
            )}
            {item.id && (
              <div className="flex items-center gap-1">
                <Hash size={12} className="text-gray-500" />
                <span className="text-gray-400">ID:</span>
                <span className="text-white font-mono text-xs">{item.id.slice(0, 8)}</span>
              </div>
            )}
          </div>

          {/* Session 834: View Details - Modal for dreams/conversations, links for others */}
          {item.type === 'dream' && onViewDream && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onViewDream(item.id)
              }}
              className="inline-flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
            >
              View Full Dream <ChevronRight size={12} />
            </button>
          )}
          {item.type === 'conversation' && onViewConversation && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onViewConversation(item.id)
              }}
              className="inline-flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
            >
              View Full Conversation <ChevronRight size={12} />
            </button>
          )}
          {/* Session 843: Decision now opens inline modal instead of redirecting */}
          {item.type === 'decision' && onViewDecision && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onViewDecision(item.id)
              }}
              className="inline-flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
            >
              View Decision Details <ChevronRight size={12} />
            </button>
          )}
          {/* Session 857: Removed external link - pilot details shown inline */}
          {item.type === 'pilot' && (
            <span className="inline-flex items-center gap-1 text-xs text-gray-400">
              Pilot Experiment
            </span>
          )}
        </div>
      )}
    </div>
  )
}
