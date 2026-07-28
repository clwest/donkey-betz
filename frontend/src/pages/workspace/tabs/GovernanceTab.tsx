// Session 825: Governance Tab
// Session 829: Added Self-Healing Remediation Controls
// Session 830: Live polling with pause toggle, by-agent progress table
// Session 831: Added error handling and success feedback for mutations
// Session 852: Added clickable decision cards with modal
// Extracted from WorkspacePage.tsx for modular architecture
import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  CheckSquare,
  CheckCircle,
  Wrench,
  Play,
  Loader2,
  RefreshCw,
  FileCode,
  Bot,
  Pause,
  Clock,
  Activity,
  XCircle,
  AlertCircle,
  Eye,
  Square,
  Filter,
  ThumbsUp,
  ThumbsDown,
  X as XIcon,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi } from '@/lib/api'
import { EmergencyControls, DecisionDetailModal } from '@/components/platform'
import { ErrorState } from '@/components/ErrorState'

// Session 831: Feedback message type
interface FeedbackMessage {
  type: 'success' | 'error' | 'info'
  message: string
  timestamp: number
}

// Session 3013 (U1): Batch triage — filter values for pending decisions
type UrgencyFilter = 'all' | 'critical' | 'high' | 'medium' | 'low'
type TypeFilter = 'all' | 'decision' | 'alert' | 'opportunity'

export function GovernanceTab() {
  const queryClient = useQueryClient()
  const [remediationLimit, setRemediationLimit] = useState(20)
  const [isPolling, setIsPolling] = useState(true) // Session 830: Polling toggle (default ON)
  const [feedback, setFeedback] = useState<FeedbackMessage | null>(null) // Session 831: User feedback
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null) // Session 852: Decision modal

  // Session 3013 (U1): Batch triage state
  const [selectedItemIds, setSelectedItemIds] = useState<Set<string>>(new Set())
  const [urgencyFilter, setUrgencyFilter] = useState<UrgencyFilter>('all')
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all')
  const [confirmRejectOpen, setConfirmRejectOpen] = useState(false)

  const {
    data: governanceData,
    isLoading: loadingGovernance,
    isError: governanceError,
    error: governanceErrorData,
    refetch: refetchGovernance,
  } = useQuery({
    queryKey: ['platform-governance'],
    queryFn: async () => {
      const res = await platformApi.governance()
      return res.data
    },
  })

  // Session 830: Live self-healing progress with configurable polling
  const {
    data: progressData,
    isLoading: loadingProgress,
    isError: _progressError, // Session 833: Prefixed to suppress warning - error handled at governance level
    refetch: refetchProgress,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ['self-healing-progress'],
    queryFn: async () => {
      const res = await platformApi.selfHealingProgress()
      return res.data
    },
    refetchInterval: isPolling ? 12000 : false, // Poll every 12 seconds when enabled
    staleTime: 5000, // Consider data fresh for 5 seconds
  })

  // Session 829: Remediation status (fallback/additional data)
  const { data: _remediationData, refetch: refetchRemediation } = useQuery({
    queryKey: ['remediation-status'],
    queryFn: async () => {
      const res = await platformApi.remediationStatus()
      return res.data
    },
    refetchInterval: isPolling ? 30000 : false, // Slower refresh for this one
  })

  const emergencyHaltMutation = useMutation({
    mutationFn: () => platformApi.emergencyHalt(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
    },
  })

  const skinLockMutation = useMutation({
    mutationFn: (action: 'lock' | 'unlock' | 'toggle') => platformApi.skinLock(action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
    },
  })

  // Session 829: Run remediation mutation
  // Session 831: Added success/error feedback
  const runRemediationMutation = useMutation({
    mutationFn: (params: { limit?: number; write_files?: boolean }) =>
      platformApi.runRemediation(params),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['self-healing-progress'] })
      queryClient.invalidateQueries({ queryKey: ['remediation-status'] })
      setFeedback({
        type: 'success',
        message: response.data?.message || 'Remediation cycle started successfully',
        timestamp: Date.now(),
      })
    },
    onError: (error: any) => {
      console.error('Remediation error:', error)
      setFeedback({
        type: 'error',
        message: error.response?.data?.error || error.message || 'Failed to start remediation',
        timestamp: Date.now(),
      })
    },
  })

  // Session 829: Run self-audit mutation
  // Session 831: Added success/error feedback
  const runSelfAuditMutation = useMutation({
    mutationFn: () => platformApi.runSelfAudit(),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['self-healing-progress'] })
      queryClient.invalidateQueries({ queryKey: ['remediation-status'] })
      setFeedback({
        type: 'success',
        message: response.data?.message || 'Self-audit started successfully',
        timestamp: Date.now(),
      })
    },
    onError: (error: any) => {
      console.error('Self-audit error:', error)
      setFeedback({
        type: 'error',
        message: error.response?.data?.error || error.message || 'Failed to start self-audit',
        timestamp: Date.now(),
      })
    },
  })

  // Session 3013 (U1): Bulk decide mutation — calls existing BulkAttentionDecideView
  const bulkDecideMutation = useMutation({
    mutationFn: (params: { decision: 'approved' | 'ignored' | 'rejected'; item_ids: string[] }) =>
      platformApi.bulkAttentionDecide(params),
    onSuccess: (response, variables) => {
      const count = response.data?.count ?? 0
      const requested = variables.item_ids.length
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
      setSelectedItemIds(new Set())
      if (response.data?.success === false) {
        setFeedback({
          type: 'error',
          message: response.data?.error || 'Bulk decide failed',
          timestamp: Date.now(),
        })
        return
      }
      const partial = count < requested
      setFeedback({
        type: partial ? 'info' : 'success',
        message: partial
          ? `${count} of ${requested} items ${variables.decision} (${requested - count} skipped — may have changed status)`
          : `${count} items ${variables.decision}`,
        timestamp: Date.now(),
      })
    },
    onError: (error: any) => {
      console.error('Bulk decide error:', error)
      setFeedback({
        type: 'error',
        message: error.response?.data?.error || error.message || 'Failed to bulk decide',
        timestamp: Date.now(),
      })
    },
  })

  // Session 3013 (U1): Filter pending_decisions by urgency + item_type
  const filteredDecisions = useMemo(() => {
    const raw = governanceData?.pending_decisions ?? []
    return raw.filter((d: any) => {
      if (urgencyFilter !== 'all' && d.urgency !== urgencyFilter) return false
      if (typeFilter !== 'all' && d.item_type !== typeFilter) return false
      return true
    })
  }, [governanceData?.pending_decisions, urgencyFilter, typeFilter])

  // Session 3013 (U1): Derived selection state (only counts items still visible under current filters)
  const visibleSelectedIds = useMemo(
    () => filteredDecisions.filter((d: any) => selectedItemIds.has(d.id)).map((d: any) => d.id),
    [filteredDecisions, selectedItemIds]
  )
  const allVisibleSelected = filteredDecisions.length > 0 && visibleSelectedIds.length === filteredDecisions.length

  const toggleItemSelection = (id: string) => {
    setSelectedItemIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const selectAllVisible = () => {
    setSelectedItemIds(new Set(filteredDecisions.map((d: any) => d.id)))
  }

  const clearSelection = () => {
    setSelectedItemIds(new Set())
  }

  const runBulkDecide = (decision: 'approved' | 'ignored' | 'rejected') => {
    if (visibleSelectedIds.length === 0) return
    bulkDecideMutation.mutate({ decision, item_ids: visibleSelectedIds })
  }

  // Format timestamp for display
  const formatLastUpdated = (timestamp: number | undefined) => {
    if (!timestamp) return 'Never'
    const date = new Date(timestamp)
    return date.toLocaleTimeString()
  }

  // Get status color and icon
  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'DONE':
        return { bg: 'bg-accent-green/20', text: 'text-accent-green', icon: CheckCircle }
      case 'RUNNING':
        return { bg: 'bg-accent-amber/20', text: 'text-accent-amber', icon: Activity }
      case 'PENDING':
        return { bg: 'bg-gray-700', text: 'text-gray-400', icon: Clock }
      default:
        return { bg: 'bg-gray-800', text: 'text-gray-500', icon: Pause }
    }
  }

  // Session 833: Show error state if governance query failed
  if (governanceError) {
    return (
      <ErrorState
        error={governanceErrorData as Error}
        onRetry={refetchGovernance}
        message="Failed to load governance data. Please check your connection and try again."
      />
    )
  }

  return (
    <div className="space-y-6">
      <EmergencyControls
        emergency={governanceData?.emergency_controls}
        owner={governanceData?.owner}
        isLoading={loadingGovernance}
        onEmergencyHalt={async () => {
          await emergencyHaltMutation.mutateAsync()
        }}
        onSkinLockToggle={async (action: 'lock' | 'unlock' | 'toggle') => {
          await skinLockMutation.mutateAsync(action)
        }}
      />

      {/* Session 830: Live Self-Healing Progress */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Wrench className="text-primary-400" size={18} />
            <h3 className="text-md font-semibold uppercase">Self-Healing System</h3>
            {isPolling && (
              <span className="flex items-center gap-1 text-xs text-accent-green">
                <span className="w-1.5 h-1.5 bg-accent-green rounded-full animate-pulse" />
                Live
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* Polling Toggle */}
            <button
              onClick={() => setIsPolling(!isPolling)}
              className={cn(
                'flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors',
                isPolling
                  ? 'bg-accent-green/20 text-accent-green'
                  : 'bg-gray-700 text-gray-400'
              )}
              title={isPolling ? 'Pause auto-refresh' : 'Resume auto-refresh'}
            >
              {isPolling ? <Activity size={12} /> : <Pause size={12} />}
              {isPolling ? 'Polling' : 'Paused'}
            </button>
            <button
              onClick={() => {
                refetchProgress()
                refetchRemediation()
              }}
              className="p-1.5 hover:bg-dark-border rounded-lg transition-colors"
              title="Refresh now"
            >
              <RefreshCw size={14} className={loadingProgress ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {loadingProgress && !progressData ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={24} className="animate-spin text-primary-400" />
          </div>
        ) : progressData ? (
          <div className="space-y-4">
            {/* Progress Bar */}
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-400">Overall Progress</span>
                <span className="font-mono text-primary-400">
                  {progressData.completed_tasks}/{progressData.total_tasks}
                  {' '}({progressData.progress_pct?.toFixed(1)}%)
                </span>
              </div>
              <div className="h-3 bg-dark-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-500"
                  style={{ width: `${progressData.progress_pct || 0}%` }}
                />
              </div>
            </div>

            {/* Recent Activity Stats */}
            <div className="grid grid-cols-4 gap-2">
              <div className="p-2 bg-dark-bg rounded-lg text-center">
                <div className="text-lg font-bold text-accent-green">
                  {progressData.completed_tasks}
                </div>
                <div className="text-xs text-gray-400">Completed</div>
              </div>
              <div className="p-2 bg-dark-bg rounded-lg text-center">
                <div className="text-lg font-bold text-accent-amber">
                  {progressData.recent_activity?.in_progress || 0}
                </div>
                <div className="text-xs text-gray-400">In Progress</div>
              </div>
              <div className="p-2 bg-dark-bg rounded-lg text-center">
                <div className="text-lg font-bold text-gray-400">
                  {progressData.recent_activity?.assigned || 0}
                </div>
                <div className="text-xs text-gray-400">Pending</div>
              </div>
              <div className="p-2 bg-dark-bg rounded-lg text-center">
                <div className="text-lg font-bold text-primary-400">
                  {progressData.recent_activity?.completed_last_10m || 0}
                </div>
                <div className="text-xs text-gray-400">Last 10m</div>
              </div>
            </div>

            {/* Agent Progress Table */}
            {progressData.by_agent && progressData.by_agent.length > 0 && (
              <div className="bg-dark-bg rounded-lg overflow-hidden">
                <div className="text-xs text-gray-400 px-3 py-2 border-b border-dark-border flex items-center gap-1.5">
                  <Bot size={12} /> Progress by Agent
                </div>
                <div className="max-h-64 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-dark-border/50 sticky top-0">
                      <tr>
                        <th className="text-left px-3 py-2 text-gray-400 font-medium">Agent</th>
                        <th className="text-right px-3 py-2 text-gray-400 font-medium w-24">Progress</th>
                        <th className="text-right px-3 py-2 text-gray-400 font-medium w-16">%</th>
                        <th className="text-center px-3 py-2 text-gray-400 font-medium w-20">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {progressData.by_agent.map((agent) => {
                        const style = getStatusStyle(agent.status)
                        const StatusIcon = style.icon
                        return (
                          <tr key={agent.agent} className="border-t border-dark-border/50 hover:bg-dark-border/30">
                            <td className="px-3 py-2 truncate max-w-[200px]" title={agent.agent}>
                              {agent.agent}
                            </td>
                            <td className="px-3 py-2 text-right font-mono">
                              {agent.completed}/{agent.total}
                            </td>
                            <td className="px-3 py-2 text-right font-mono text-primary-400">
                              {agent.pct.toFixed(0)}%
                            </td>
                            <td className="px-3 py-2 text-center">
                              <span
                                className={cn(
                                  'inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs',
                                  style.bg,
                                  style.text
                                )}
                              >
                                <StatusIcon size={10} />
                                {agent.status}
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Controls */}
            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <div className="flex items-center gap-2 flex-1">
                <label className="text-sm text-gray-400">Batch size:</label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={remediationLimit}
                  onChange={(e) => setRemediationLimit(Number(e.target.value))}
                  className="w-20 px-2 py-1.5 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
                />
              </div>
              <button
                onClick={() => runRemediationMutation.mutate({ limit: remediationLimit, write_files: true })}
                disabled={runRemediationMutation.isPending}
                className={cn(
                  'flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
                  'bg-primary-500 hover:bg-primary-600 text-white',
                  runRemediationMutation.isPending && 'opacity-50 cursor-not-allowed'
                )}
              >
                {runRemediationMutation.isPending ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Play size={16} />
                )}
                Run Remediation
              </button>
              <button
                onClick={() => runSelfAuditMutation.mutate()}
                disabled={runSelfAuditMutation.isPending}
                className={cn(
                  'flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
                  'bg-dark-border hover:bg-gray-700 text-white',
                  runSelfAuditMutation.isPending && 'opacity-50 cursor-not-allowed'
                )}
              >
                {runSelfAuditMutation.isPending ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <FileCode size={16} />
                )}
                Run Audit
              </button>
            </div>

            {/* Session 831: Feedback Message */}
            {feedback && Date.now() - feedback.timestamp < 30000 && (
              <div
                className={cn(
                  'flex items-center gap-2 p-3 rounded-lg text-sm',
                  feedback.type === 'success' && 'bg-accent-green/10 text-accent-green',
                  feedback.type === 'error' && 'bg-accent-red/10 text-accent-red',
                  feedback.type === 'info' && 'bg-primary-500/10 text-primary-400'
                )}
              >
                {feedback.type === 'success' && <CheckCircle size={16} />}
                {feedback.type === 'error' && <XCircle size={16} />}
                {feedback.type === 'info' && <AlertCircle size={16} />}
                <span>{feedback.message}</span>
                <button
                  onClick={() => setFeedback(null)}
                  className="ml-auto text-current opacity-60 hover:opacity-100"
                >
                  ×
                </button>
              </div>
            )}

            {/* Last Updated Footer */}
            <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-dark-border">
              <span>
                Last updated: {formatLastUpdated(dataUpdatedAt)}
              </span>
              {progressData.recent_activity?.last_completed_at && (
                <span>
                  Last task: {new Date(progressData.recent_activity.last_completed_at).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Wrench className="mx-auto mb-2" size={24} />
            <p>No progress data available</p>
          </div>
        )}
      </div>

      {/* Pending Decisions Full List */}
      {governanceData?.pending_decisions && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <CheckSquare className="text-primary-400" size={18} />
            <h3 className="text-md font-semibold uppercase">
              Pending Decisions ({governanceData.pending_decisions_count})
            </h3>
            {filteredDecisions.length !== governanceData.pending_decisions.length && (
              <span className="text-xs text-gray-500">
                showing {filteredDecisions.length} of {governanceData.pending_decisions.length}
              </span>
            )}
          </div>

          {/* Session 3013 (U1): Filter chips + batch selection controls */}
          {governanceData.pending_decisions.length > 0 && (
            <div className="space-y-3 mb-4">
              {/* Filter chips */}
              <div className="flex flex-wrap items-center gap-3 text-xs">
                <div className="flex items-center gap-1 text-gray-400">
                  <Filter size={12} />
                  Urgency:
                </div>
                {(['all', 'critical', 'high', 'medium', 'low'] as UrgencyFilter[]).map((u) => (
                  <button
                    key={u}
                    onClick={() => setUrgencyFilter(u)}
                    className={cn(
                      'px-2 py-0.5 rounded-md transition-colors',
                      urgencyFilter === u
                        ? 'bg-primary-500 text-white'
                        : 'bg-dark-border text-gray-400 hover:bg-gray-700'
                    )}
                  >
                    {u}
                  </button>
                ))}
                <div className="flex items-center gap-1 text-gray-400 ml-2">Type:</div>
                {(['all', 'decision', 'alert', 'opportunity'] as TypeFilter[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTypeFilter(t)}
                    className={cn(
                      'px-2 py-0.5 rounded-md transition-colors',
                      typeFilter === t
                        ? 'bg-primary-500 text-white'
                        : 'bg-dark-border text-gray-400 hover:bg-gray-700'
                    )}
                  >
                    {t}
                  </button>
                ))}
              </div>

              {/* Select all / clear */}
              {filteredDecisions.length > 0 && (
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => (allVisibleSelected ? clearSelection() : selectAllVisible())}
                      className="flex items-center gap-1 text-gray-400 hover:text-primary-400 transition-colors"
                    >
                      {allVisibleSelected ? (
                        <CheckSquare size={14} className="text-primary-400" />
                      ) : (
                        <Square size={14} />
                      )}
                      {allVisibleSelected ? 'Deselect all' : 'Select all visible'}
                    </button>
                    {selectedItemIds.size > 0 && (
                      <span className="text-primary-400">
                        {visibleSelectedIds.length} selected
                      </span>
                    )}
                  </div>
                  <span className="text-gray-500 italic">
                    Actions apply to Human Attention Items
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Session 3013 (U1): Sticky bulk-action bar when ≥1 selected */}
          {visibleSelectedIds.length > 0 && (
            <div className="sticky top-0 z-10 mb-3 flex flex-wrap items-center gap-2 p-3 bg-dark-bg border border-primary-500/40 rounded-lg shadow-lg">
              <span className="text-sm font-medium text-primary-400">
                {visibleSelectedIds.length} selected
              </span>
              <div className="flex-1" />
              <button
                onClick={() => runBulkDecide('approved')}
                disabled={bulkDecideMutation.isPending}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors',
                  'bg-accent-green/20 text-accent-green hover:bg-accent-green/30',
                  bulkDecideMutation.isPending && 'opacity-50 cursor-not-allowed'
                )}
              >
                {bulkDecideMutation.isPending && bulkDecideMutation.variables?.decision === 'approved' ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <ThumbsUp size={14} />
                )}
                Approve {visibleSelectedIds.length}
              </button>
              <button
                onClick={() => runBulkDecide('ignored')}
                disabled={bulkDecideMutation.isPending}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors',
                  'bg-gray-700 text-gray-300 hover:bg-gray-600',
                  bulkDecideMutation.isPending && 'opacity-50 cursor-not-allowed'
                )}
              >
                {bulkDecideMutation.isPending && bulkDecideMutation.variables?.decision === 'ignored' ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Pause size={14} />
                )}
                Ignore {visibleSelectedIds.length}
              </button>
              <button
                onClick={() => setConfirmRejectOpen(true)}
                disabled={bulkDecideMutation.isPending}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors',
                  'bg-accent-red/20 text-accent-red hover:bg-accent-red/30',
                  bulkDecideMutation.isPending && 'opacity-50 cursor-not-allowed'
                )}
              >
                {bulkDecideMutation.isPending && bulkDecideMutation.variables?.decision === 'rejected' ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <ThumbsDown size={14} />
                )}
                Reject {visibleSelectedIds.length}
              </button>
              <button
                onClick={clearSelection}
                className="p-1.5 hover:bg-dark-border rounded-md transition-colors text-gray-400"
                title="Clear selection"
              >
                <XIcon size={14} />
              </button>
            </div>
          )}

          {filteredDecisions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="mx-auto mb-2" size={24} />
              <p>
                {governanceData.pending_decisions.length === 0
                  ? 'No pending decisions'
                  : 'No decisions match current filters'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredDecisions.map((decision: any) => {
                const isSelected = selectedItemIds.has(decision.id)
                return (
                  <div
                    key={decision.id}
                    onClick={() => setSelectedDecisionId(decision.id)}
                    className={cn(
                      'p-4 bg-gray-800/50 hover:bg-gray-800/80 rounded-lg cursor-pointer transition-colors group flex items-start gap-3',
                      isSelected && 'ring-1 ring-primary-500/60 bg-primary-500/5'
                    )}
                  >
                    {/* Session 3013 (U1): Checkbox — stopPropagation preserves card-click → modal */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleItemSelection(decision.id)
                      }}
                      className="mt-1 text-gray-500 hover:text-primary-400 transition-colors"
                      aria-label={isSelected ? 'Deselect item' : 'Select item'}
                    >
                      {isSelected ? (
                        <CheckSquare size={16} className="text-primary-400" />
                      ) : (
                        <Square size={16} />
                      )}
                    </button>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium group-hover:text-primary-400 transition-colors">
                            {decision.title}
                          </h4>
                          <p className="text-xs text-gray-400 mt-1">
                            {decision.source_agent || decision.source_type}
                            {decision.item_type && (
                              <span className="ml-2 text-gray-500">· {decision.item_type}</span>
                            )}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span
                            className={cn(
                              'text-xs px-2 py-0.5 rounded',
                              decision.urgency === 'critical'
                                ? 'bg-accent-red/20 text-accent-red'
                                : decision.urgency === 'high'
                                ? 'bg-accent-amber/20 text-accent-amber'
                                : 'bg-gray-700 text-gray-400'
                            )}
                          >
                            {decision.urgency}
                          </span>
                          <Eye size={14} className="text-gray-500 group-hover:text-primary-400 transition-colors" />
                        </div>
                      </div>
                      {decision.summary && (
                        <p className="text-sm text-gray-400 line-clamp-2">{decision.summary}</p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Session 3013 (U1): Reject confirm dialog — Rigby A1 SIGN guardrail (prevents fat-finger mass-reject) */}
      {confirmRejectOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
          onClick={() => setConfirmRejectOpen(false)}
        >
          <div
            className="max-w-md w-full mx-4 p-6 bg-dark-bg border border-accent-red/40 rounded-lg shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-2 mb-3">
              <ThumbsDown className="text-accent-red" size={20} />
              <h3 className="text-lg font-semibold">Reject {visibleSelectedIds.length} items?</h3>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              This marks {visibleSelectedIds.length} Human Attention Item{visibleSelectedIds.length === 1 ? '' : 's'} as{' '}
              <span className="text-accent-red font-medium">rejected</span>. This is a terminal action — items
              cannot be re-opened via bulk actions.
            </p>
            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => setConfirmRejectOpen(false)}
                className="px-4 py-2 text-sm rounded-md bg-dark-border hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setConfirmRejectOpen(false)
                  runBulkDecide('rejected')
                }}
                className="flex items-center gap-1.5 px-4 py-2 text-sm rounded-md bg-accent-red/20 text-accent-red hover:bg-accent-red/30 transition-colors"
              >
                <ThumbsDown size={14} />
                Reject {visibleSelectedIds.length}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 852: Decision Detail Modal */}
      {selectedDecisionId && (
        <DecisionDetailModal
          decisionId={selectedDecisionId}
          onClose={() => setSelectedDecisionId(null)}
        />
      )}
    </div>
  )
}
