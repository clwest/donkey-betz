// Session 1067: Full-page Governance — elevated from workspace tab
// Health banner, KPI cards, four tabs, emergency controls, self-healing, live polling
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ShieldCheck,
  CheckCircle,
  XCircle,
  Wrench,
  Play,
  Loader2,
  RefreshCw,
  FileCode,
  Bot,
  Pause,
  Clock,
  Activity,
  AlertCircle,
  Eye,
  AlertTriangle,
  Shield,
  Zap,
  ListChecks,
  ScrollText,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi } from '@/lib/api'
import { EmergencyControls, DecisionDetailModal } from '@/components/platform'
import { ErrorState } from '@/components/ErrorState'

type GovernanceTab = 'alerts' | 'gates' | 'decisions' | 'activity'

interface FeedbackMessage {
  type: 'success' | 'error' | 'info'
  message: string
  timestamp: number
}

export default function GovernancePage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<GovernanceTab>('alerts')
  const [isPolling, setIsPolling] = useState(true)
  const [remediationLimit, setRemediationLimit] = useState(20)
  const [feedback, setFeedback] = useState<FeedbackMessage | null>(null)
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null)

  // Governance data
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
    refetchInterval: isPolling ? 12000 : false,
  })

  // Self-healing progress
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
    refetchInterval: isPolling ? 12000 : false,
    staleTime: 5000,
  })

  // Remediation status
  const { refetch: refetchRemediation } = useQuery({
    queryKey: ['remediation-status'],
    queryFn: async () => {
      const res = await platformApi.remediationStatus()
      return res.data
    },
    refetchInterval: isPolling ? 30000 : false,
  })

  // Mutations
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
      setFeedback({
        type: 'error',
        message: error.response?.data?.error || error.message || 'Failed to start remediation',
        timestamp: Date.now(),
      })
    },
  })

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
      setFeedback({
        type: 'error',
        message: error.response?.data?.error || error.message || 'Failed to start self-audit',
        timestamp: Date.now(),
      })
    },
  })

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

  const formatLastUpdated = (timestamp: number | undefined) => {
    if (!timestamp) return 'Never'
    return new Date(timestamp).toLocaleTimeString()
  }

  // Overall health status
  const healthStatus = governanceData?.emergency_controls?.all_clear !== false ? 'healthy' : 'alert'
  const pendingDecisionsCount = governanceData?.pending_decisions_count ?? 0

  if (governanceError) {
    return (
      <div className="flex-1 p-6">
        <ErrorState
          error={governanceErrorData as Error}
          onRetry={refetchGovernance}
          message="Failed to load governance data. Please check your connection and try again."
        />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-hidden flex flex-col">
      {/* Health Banner */}
      <div className={cn(
        'px-6 py-3 flex items-center gap-3',
        healthStatus === 'healthy'
          ? 'bg-green-500/10 border-b border-green-500/20'
          : 'bg-red-500/10 border-b border-red-500/20'
      )}>
        <div className={cn(
          'w-3 h-3 rounded-full',
          healthStatus === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500 animate-pulse'
        )} />
        <span className={cn(
          'text-sm font-medium',
          healthStatus === 'healthy' ? 'text-green-400' : 'text-red-400'
        )}>
          {healthStatus === 'healthy' ? 'All Systems Operational' : 'System Alert Active'}
        </span>
        {isPolling && (
          <span className="flex items-center gap-1 text-xs text-gray-500 ml-auto">
            <Activity size={12} /> Live polling (12s)
          </span>
        )}
      </div>

      {/* Page Header */}
      <div className="px-6 py-4 border-b border-dark-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldCheck className="text-primary-400" size={24} />
            <div>
              <h1 className="text-xl font-bold">Governance</h1>
              <p className="text-sm text-gray-500">System control panel and self-healing oversight</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPolling(!isPolling)}
              className={cn(
                'flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-colors',
                isPolling
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-dark-border text-gray-400'
              )}
            >
              {isPolling ? <Activity size={14} /> : <Pause size={14} />}
              {isPolling ? 'Live' : 'Paused'}
            </button>
            <button
              onClick={() => { refetchGovernance(); refetchProgress(); refetchRemediation() }}
              className="flex items-center gap-2 px-3 py-2 bg-dark-border rounded-lg hover:bg-gray-700 transition-colors text-sm"
            >
              <RefreshCw size={14} className={loadingGovernance || loadingProgress ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="px-6 py-4 border-b border-dark-border">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Bot size={14} /> Active Agents
            </div>
            <div className="text-2xl font-bold text-white">
              {progressData?.by_agent?.length ?? '--'}
            </div>
          </div>
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Activity size={14} /> System Health
            </div>
            <div className={cn(
              "text-2xl font-bold",
              healthStatus === 'healthy' ? 'text-green-400' : 'text-red-400'
            )}>
              {progressData?.progress_pct != null ? `${progressData.progress_pct.toFixed(0)}%` : '--'}
            </div>
          </div>
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Shield size={14} /> Open Gates
            </div>
            <div className="text-2xl font-bold text-amber-400">
              {pendingDecisionsCount}
            </div>
          </div>
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Wrench size={14} /> Remediations
            </div>
            <div className="text-2xl font-bold text-primary-400">
              {progressData?.recent_activity?.in_progress ?? 0}
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="px-6 border-b border-dark-border flex items-center gap-1">
        {([
          { key: 'alerts' as GovernanceTab, label: 'Alerts', icon: AlertTriangle },
          { key: 'gates' as GovernanceTab, label: 'Gates', icon: Shield },
          { key: 'decisions' as GovernanceTab, label: 'Decisions', icon: ListChecks },
          { key: 'activity' as GovernanceTab, label: 'Activity', icon: ScrollText },
        ]).map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              'flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2',
              activeTab === tab.key
                ? 'text-primary-400 border-primary-500'
                : 'text-gray-400 border-transparent hover:text-white'
            )}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {/* Emergency Controls - always visible at top */}
        <div className="px-6 pt-4">
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
        </div>

        {/* Feedback Message */}
        {feedback && Date.now() - feedback.timestamp < 30000 && (
          <div className="px-6 pt-3">
            <div className={cn(
              'flex items-center gap-2 p-3 rounded-lg text-sm',
              feedback.type === 'success' && 'bg-accent-green/10 text-accent-green',
              feedback.type === 'error' && 'bg-accent-red/10 text-accent-red',
              feedback.type === 'info' && 'bg-primary-500/10 text-primary-400'
            )}>
              {feedback.type === 'success' && <CheckCircle size={16} />}
              {feedback.type === 'error' && <XCircle size={16} />}
              {feedback.type === 'info' && <AlertCircle size={16} />}
              <span>{feedback.message}</span>
              <button onClick={() => setFeedback(null)} className="ml-auto text-current opacity-60 hover:opacity-100">
                x
              </button>
            </div>
          </div>
        )}

        {/* Tab Content */}
        <div className="p-6">
          {/* Alerts Tab */}
          {activeTab === 'alerts' && (
            <div className="space-y-4">
              <h3 className="text-md font-semibold text-gray-300 uppercase flex items-center gap-2">
                <AlertTriangle size={16} className="text-amber-400" />
                Active Alerts
              </h3>
              {governanceData?.emergency_controls?.all_clear === false ? (
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <div className="flex items-center gap-2 text-red-400 font-medium">
                    <AlertTriangle size={16} />
                    Emergency halt is active
                  </div>
                  <p className="text-sm text-gray-400 mt-1">
                    System operations are paused. Review and clear the emergency state to resume.
                  </p>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <CheckCircle className="mx-auto mb-3" size={36} />
                  <p className="text-lg">No active alerts</p>
                  <p className="text-sm mt-1">All systems are running normally</p>
                </div>
              )}
            </div>
          )}

          {/* Gates Tab */}
          {activeTab === 'gates' && (
            <div className="space-y-4">
              <h3 className="text-md font-semibold text-gray-300 uppercase flex items-center gap-2">
                <Shield size={16} className="text-primary-400" />
                Pending Decisions ({pendingDecisionsCount})
              </h3>
              {governanceData?.pending_decisions && governanceData.pending_decisions.length > 0 ? (
                <div className="space-y-3">
                  {governanceData.pending_decisions.map((decision: any) => (
                    <div
                      key={decision.id}
                      onClick={() => setSelectedDecisionId(decision.id)}
                      className="p-4 bg-dark-card border border-dark-border rounded-lg cursor-pointer hover:border-gray-600 transition-colors group"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium group-hover:text-primary-400 transition-colors">
                            {decision.title}
                          </h4>
                          <p className="text-xs text-gray-400 mt-1">
                            {decision.source_agent || decision.source_type}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={cn(
                            'text-xs px-2 py-0.5 rounded',
                            decision.urgency === 'critical'
                              ? 'bg-red-500/20 text-red-400'
                              : decision.urgency === 'high'
                              ? 'bg-amber-500/20 text-amber-400'
                              : 'bg-gray-700 text-gray-400'
                          )}>
                            {decision.urgency}
                          </span>
                          <Eye size={14} className="text-gray-500 group-hover:text-primary-400 transition-colors" />
                        </div>
                      </div>
                      {decision.description && (
                        <p className="text-sm text-gray-400 line-clamp-2">{decision.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <CheckCircle className="mx-auto mb-3" size={36} />
                  <p className="text-lg">No pending decisions</p>
                </div>
              )}
            </div>
          )}

          {/* Decisions (Self-Healing) Tab */}
          {activeTab === 'decisions' && (
            <div className="space-y-6">
              {/* Self-Healing Progress */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-md font-semibold text-gray-300 uppercase flex items-center gap-2">
                    <Wrench size={16} className="text-primary-400" />
                    Self-Healing System
                  </h3>
                  <span className="text-xs text-gray-500">
                    Updated: {formatLastUpdated(dataUpdatedAt)}
                  </span>
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

                    {/* Stats Grid */}
                    <div className="grid grid-cols-4 gap-3">
                      <div className="p-3 bg-dark-bg rounded-lg text-center">
                        <div className="text-xl font-bold text-green-400">{progressData.completed_tasks}</div>
                        <div className="text-xs text-gray-400">Completed</div>
                      </div>
                      <div className="p-3 bg-dark-bg rounded-lg text-center">
                        <div className="text-xl font-bold text-amber-400">{progressData.recent_activity?.in_progress || 0}</div>
                        <div className="text-xs text-gray-400">In Progress</div>
                      </div>
                      <div className="p-3 bg-dark-bg rounded-lg text-center">
                        <div className="text-xl font-bold text-gray-400">{progressData.recent_activity?.assigned || 0}</div>
                        <div className="text-xs text-gray-400">Pending</div>
                      </div>
                      <div className="p-3 bg-dark-bg rounded-lg text-center">
                        <div className="text-xl font-bold text-primary-400">{progressData.recent_activity?.completed_last_10m || 0}</div>
                        <div className="text-xs text-gray-400">Last 10m</div>
                      </div>
                    </div>

                    {/* Agent Progress Table */}
                    {progressData.by_agent && progressData.by_agent.length > 0 && (
                      <div className="bg-dark-bg rounded-lg overflow-hidden">
                        <div className="text-xs text-gray-400 px-3 py-2 border-b border-dark-border flex items-center gap-1.5">
                          <Bot size={12} /> Progress by Agent
                        </div>
                        <div className="max-h-80 overflow-y-auto">
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
                              {progressData.by_agent.map((agent: any) => {
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
                                      <span className={cn(
                                        'inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs',
                                        style.bg, style.text
                                      )}>
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
                        {runRemediationMutation.isPending
                          ? <Loader2 size={16} className="animate-spin" />
                          : <Play size={16} />}
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
                        {runSelfAuditMutation.isPending
                          ? <Loader2 size={16} className="animate-spin" />
                          : <FileCode size={16} />}
                        Run Audit
                      </button>
                    </div>

                    {/* Last updated */}
                    {progressData.recent_activity?.last_completed_at && (
                      <div className="text-xs text-gray-500 pt-2 border-t border-dark-border">
                        Last completed task: {new Date(progressData.recent_activity.last_completed_at).toLocaleTimeString()}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Wrench className="mx-auto mb-2" size={24} />
                    <p>No progress data available</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Activity Tab */}
          {activeTab === 'activity' && (
            <div className="space-y-4">
              <h3 className="text-md font-semibold text-gray-300 uppercase flex items-center gap-2">
                <ScrollText size={16} className="text-primary-400" />
                System Activity
              </h3>

              {/* Authority escalation path */}
              {governanceData?.authority_escalation_path && governanceData.authority_escalation_path.length > 0 && (
                <div className="card">
                  <h4 className="text-sm font-medium text-gray-400 mb-3">Authority Escalation Path</h4>
                  <div className="space-y-2">
                    {governanceData.authority_escalation_path.map((level: any, idx: number) => (
                      <div key={idx} className="flex items-center gap-3 p-2 bg-dark-bg rounded">
                        <span className="text-xs font-mono text-primary-400 w-8 shrink-0">L{level.level}</span>
                        <span className="text-sm text-gray-300 font-medium">{level.entity}</span>
                        <span className="text-xs text-gray-500 ml-auto">{level.scope}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent remediation activity */}
              {progressData?.by_agent && progressData.by_agent.length > 0 ? (
                <div className="card">
                  <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Agent Activity</h4>
                  <div className="space-y-2">
                    {progressData.by_agent
                      .filter((a: any) => a.status === 'RUNNING' || a.status === 'DONE')
                      .slice(0, 10)
                      .map((agent: any, idx: number) => {
                        const style = getStatusStyle(agent.status)
                        const StatusIcon = style.icon
                        return (
                          <div key={idx} className="flex items-center gap-3 p-2 bg-dark-bg rounded">
                            <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs shrink-0', style.bg, style.text)}>
                              <StatusIcon size={10} />
                              {agent.status}
                            </span>
                            <span className="text-sm text-gray-300 truncate">{agent.agent}</span>
                            <span className="text-xs text-gray-500 ml-auto font-mono">
                              {agent.completed}/{agent.total}
                            </span>
                          </div>
                        )
                      })}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <ScrollText className="mx-auto mb-3" size={36} />
                  <p className="text-lg">No recent activity</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Decision Detail Modal */}
      {selectedDecisionId && (
        <DecisionDetailModal
          decisionId={selectedDecisionId}
          onClose={() => setSelectedDecisionId(null)}
        />
      )}
    </div>
  )
}
