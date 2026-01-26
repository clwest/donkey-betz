// Session 825: Governance Tab
// Session 829: Added Self-Healing Remediation Controls
// Extracted from WorkspacePage.tsx for modular architecture
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckSquare, CheckCircle, Wrench, Play, Loader2, RefreshCw, FileCode, Bot } from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi } from '@/lib/api'
import { EmergencyControls } from '@/components/platform'

export function GovernanceTab() {
  const queryClient = useQueryClient()
  const [remediationLimit, setRemediationLimit] = useState(20)

  const { data: governanceData, isLoading: loadingGovernance } = useQuery({
    queryKey: ['platform-governance'],
    queryFn: async () => {
      const res = await platformApi.governance()
      return res.data
    },
  })

  // Session 829: Remediation status query
  const { data: remediationData, isLoading: loadingRemediation, refetch: refetchRemediation } = useQuery({
    queryKey: ['remediation-status'],
    queryFn: async () => {
      const res = await platformApi.remediationStatus()
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
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
      queryClient.invalidateQueries({ queryKey: ['remediation-status'] })
    },
  })

  // Session 829: Run self-audit mutation
  const runSelfAuditMutation = useMutation({
    mutationFn: () => platformApi.runSelfAudit(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['remediation-status'] })
    },
  })

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

      {/* Session 829: Self-Healing Remediation Controls */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Wrench className="text-primary-400" size={18} />
            <h3 className="text-md font-semibold uppercase">Self-Healing System</h3>
          </div>
          <button
            onClick={() => refetchRemediation()}
            className="p-1.5 hover:bg-dark-border rounded-lg transition-colors"
            title="Refresh status"
          >
            <RefreshCw size={14} className={loadingRemediation ? 'animate-spin' : ''} />
          </button>
        </div>

        {loadingRemediation ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={24} className="animate-spin text-primary-400" />
          </div>
        ) : remediationData ? (
          <div className="space-y-4">
            {/* Progress Bar */}
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-400">Remediation Progress</span>
                <span className="font-mono text-primary-400">
                  {remediationData.progress?.completed || 0}/{remediationData.progress?.total || 0}
                  {' '}({remediationData.progress?.percentage?.toFixed(1) || 0}%)
                </span>
              </div>
              <div className="h-3 bg-dark-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-500"
                  style={{ width: `${remediationData.progress?.percentage || 0}%` }}
                />
              </div>
            </div>

            {/* Task Status Grid */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 bg-dark-bg rounded-lg">
                <div className="text-2xl font-bold text-accent-green">
                  {remediationData.tasks?.by_status?.completed || 0}
                </div>
                <div className="text-xs text-gray-400">Completed</div>
              </div>
              <div className="p-3 bg-dark-bg rounded-lg">
                <div className="text-2xl font-bold text-accent-amber">
                  {remediationData.tasks?.by_status?.in_progress || 0}
                </div>
                <div className="text-xs text-gray-400">In Progress</div>
              </div>
              <div className="p-3 bg-dark-bg rounded-lg">
                <div className="text-2xl font-bold text-gray-400">
                  {remediationData.tasks?.by_status?.assigned || 0}
                </div>
                <div className="text-xs text-gray-400">Pending</div>
              </div>
            </div>

            {/* Agent Breakdown */}
            {remediationData.tasks?.by_agent && remediationData.tasks.by_agent.length > 0 && (
              <div className="p-3 bg-dark-bg rounded-lg">
                <div className="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
                  <Bot size={12} /> Tasks by Agent
                </div>
                <div className="space-y-1.5">
                  {remediationData.tasks.by_agent.slice(0, 5).map((item: { agent: string; count: number }) => (
                    <div key={item.agent} className="flex items-center justify-between text-sm">
                      <span className="truncate">{item.agent}</span>
                      <span className="font-mono text-primary-400">{item.count}</span>
                    </div>
                  ))}
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

            {/* Recent Activity */}
            {remediationData.recent_tasks && remediationData.recent_tasks.length > 0 && (
              <div className="pt-2">
                <div className="text-xs text-gray-400 mb-2">Recent Tasks</div>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {remediationData.recent_tasks.slice(0, 5).map((task) => (
                    <div
                      key={task.id}
                      className="flex items-center justify-between p-2 bg-dark-bg rounded-lg text-sm"
                    >
                      <div className="flex-1 truncate">
                        <span className="text-gray-300">{task.finding_title}</span>
                        <span className="text-xs text-gray-500 ml-2">{task.agent}</span>
                      </div>
                      <span
                        className={cn(
                          'text-xs px-2 py-0.5 rounded',
                          task.status === 'completed'
                            ? 'bg-accent-green/20 text-accent-green'
                            : task.status === 'in_progress'
                            ? 'bg-accent-amber/20 text-accent-amber'
                            : 'bg-gray-700 text-gray-400'
                        )}
                      >
                        {task.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Wrench className="mx-auto mb-2" size={24} />
            <p>No remediation data available</p>
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
