// Session 825: Governance Tab
// Session 829: Added Self-Healing Remediation Controls
// Session 830: Live polling with pause toggle, by-agent progress table
// Extracted from WorkspacePage.tsx for modular architecture
import { useState, useEffect } from 'react'
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
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi } from '@/lib/api'
import { EmergencyControls } from '@/components/platform'

export function GovernanceTab() {
  const queryClient = useQueryClient()
  const [remediationLimit, setRemediationLimit] = useState(20)
  const [isPolling, setIsPolling] = useState(true) // Session 830: Polling toggle (default ON)

  const { data: governanceData, isLoading: loadingGovernance } = useQuery({
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
  const { data: remediationData, refetch: refetchRemediation } = useQuery({
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
  const runRemediationMutation = useMutation({
    mutationFn: (params: { limit?: number; write_files?: boolean }) =>
      platformApi.runRemediation(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['self-healing-progress'] })
      queryClient.invalidateQueries({ queryKey: ['remediation-status'] })
    },
  })

  // Session 829: Run self-audit mutation
  const runSelfAuditMutation = useMutation({
    mutationFn: () => platformApi.runSelfAudit(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['self-healing-progress'] })
      queryClient.invalidateQueries({ queryKey: ['remediation-status'] })
    },
  })

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
          </div>
          {governanceData.pending_decisions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="mx-auto mb-2" size={24} />
              <p>No pending decisions</p>
            </div>
          ) : (
            <div className="space-y-3">
              {governanceData.pending_decisions.map((decision: any) => (
                <div
                  key={decision.id}
                  className="p-4 bg-gray-800/50 rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium">{decision.title}</h4>
                      <p className="text-xs text-gray-400 mt-1">
                        {decision.source_agent || decision.source_type}
                      </p>
                    </div>
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
                  </div>
                  {decision.description && (
                    <p className="text-sm text-gray-400">{decision.description}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
