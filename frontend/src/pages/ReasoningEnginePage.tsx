import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reasoningApi } from '@/lib/api'
import {
  Brain, Lightbulb, Zap, AlertTriangle, CheckCircle, XCircle,
  Clock, RefreshCw, Loader2, ChevronRight, Play, BarChart3
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Session 745: Reasoning Engine Dashboard - AI Decision Transparency
type TabType = 'dashboard' | 'thoughts' | 'actions' | 'concerns'

interface DashboardStats {
  total_thoughts: number
  active_thoughts: number
  total_actions: number
  pending_actions: number
  completed_actions: number
  total_concerns: number
  unresolved_concerns: number
  avg_reasoning_time_ms: number
  thoughts_today: number
  actions_today: number
}

interface Thought {
  id: string
  prompt: string
  context?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  reasoning_chain?: string[]
  conclusion?: string
  confidence?: number
  created_at: string
  completed_at?: string
  duration_ms?: number
  agent_name?: string
  actions_generated?: number
}

interface Action {
  id: string
  thought_id?: string
  action_type: string
  description: string
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'failed'
  priority: 'low' | 'medium' | 'high' | 'critical'
  created_at: string
  executed_at?: string
  result?: string
  requires_approval?: boolean
  agent_name?: string
}

interface Concern {
  id: string
  title: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  category: string
  status: 'open' | 'investigating' | 'resolved' | 'dismissed'
  created_at: string
  resolved_at?: string
  resolution?: string
  source?: string
  affected_agents?: string[]
}

export default function ReasoningEnginePage() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [selectedThought, setSelectedThought] = useState<Thought | null>(null)
  const queryClient = useQueryClient()

  // Queries
  const { data: dashboardData } = useQuery({
    queryKey: ['reasoning-dashboard'],
    queryFn: () => reasoningApi.dashboard(),
    refetchInterval: 30000,
  })

  const { data: thoughtsData, isLoading: loadingThoughts } = useQuery({
    queryKey: ['reasoning-thoughts'],
    queryFn: () => reasoningApi.thoughts({ limit: 50 }),
    enabled: activeTab === 'dashboard' || activeTab === 'thoughts',
  })

  const { data: actionsData, isLoading: loadingActions, refetch: refetchActions } = useQuery({
    queryKey: ['reasoning-actions'],
    queryFn: () => reasoningApi.actions({ limit: 50 }),
    enabled: activeTab === 'dashboard' || activeTab === 'actions',
  })

  const { data: pendingActionsData } = useQuery({
    queryKey: ['reasoning-pending-actions'],
    queryFn: () => reasoningApi.pendingActions(),
    enabled: activeTab === 'dashboard' || activeTab === 'actions',
    refetchInterval: 15000,
  })

  const { data: concernsData, isLoading: loadingConcerns, refetch: refetchConcerns } = useQuery({
    queryKey: ['reasoning-concerns'],
    queryFn: () => reasoningApi.concerns({ limit: 50 }),
    enabled: activeTab === 'dashboard' || activeTab === 'concerns',
  })

  // Mutations
  const triggerReasoning = useMutation({
    mutationFn: (data: { prompt?: string; context?: string }) => reasoningApi.trigger(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reasoning-thoughts'] })
      queryClient.invalidateQueries({ queryKey: ['reasoning-dashboard'] })
    },
  })

  const approveAction = useMutation({
    mutationFn: (id: string) => reasoningApi.approveAction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reasoning-actions'] })
      queryClient.invalidateQueries({ queryKey: ['reasoning-pending-actions'] })
    },
  })

  const rejectAction = useMutation({
    mutationFn: (id: string) => reasoningApi.rejectAction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reasoning-actions'] })
      queryClient.invalidateQueries({ queryKey: ['reasoning-pending-actions'] })
    },
  })

  const resolveConcern = useMutation({
    mutationFn: ({ id, resolution }: { id: string; resolution?: string }) =>
      reasoningApi.resolveConcern(id, { resolution }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reasoning-concerns'] })
      queryClient.invalidateQueries({ queryKey: ['reasoning-dashboard'] })
    },
  })

  // Data extraction - ensure arrays are actually arrays
  const dashboard: DashboardStats = dashboardData?.data || {}
  const rawThoughts = thoughtsData?.data?.thoughts || thoughtsData?.data?.results || thoughtsData?.data
  const thoughts: Thought[] = Array.isArray(rawThoughts) ? rawThoughts : []
  const rawActions = actionsData?.data?.actions || actionsData?.data?.results || actionsData?.data
  const actions: Action[] = Array.isArray(rawActions) ? rawActions : []
  const rawPendingActions = pendingActionsData?.data?.actions || pendingActionsData?.data?.results || pendingActionsData?.data
  const pendingActions: Action[] = Array.isArray(rawPendingActions) ? rawPendingActions : []
  const rawConcerns = concernsData?.data?.concerns || concernsData?.data?.results || concernsData?.data
  const concerns: Concern[] = Array.isArray(rawConcerns) ? rawConcerns : []

  const unresolvedConcerns = concerns.filter(c => c.status === 'open' || c.status === 'investigating')

  const tabs = [
    { id: 'dashboard' as TabType, label: 'Dashboard', icon: BarChart3 },
    { id: 'thoughts' as TabType, label: 'Thoughts', icon: Lightbulb },
    { id: 'actions' as TabType, label: 'Actions', icon: Zap, badge: pendingActions.length },
    { id: 'concerns' as TabType, label: 'Concerns', icon: AlertTriangle, badge: unresolvedConcerns.length },
  ]

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'approved':
      case 'executed':
      case 'resolved':
        return 'bg-accent-green/20 text-accent-green'
      case 'pending':
      case 'processing':
      case 'investigating':
        return 'bg-accent-amber/20 text-accent-amber'
      case 'failed':
      case 'rejected':
        return 'bg-accent-red/20 text-accent-red'
      case 'open':
        return 'bg-accent-cyan/20 text-accent-cyan'
      default:
        return 'bg-gray-500/20 text-gray-400'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-accent-red/20 text-accent-red border-accent-red/30'
      case 'high': return 'bg-accent-amber/20 text-accent-amber border-accent-amber/30'
      case 'medium': return 'bg-accent-cyan/20 text-accent-cyan border-accent-cyan/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-accent-red'
      case 'high': return 'text-accent-amber'
      case 'medium': return 'text-accent-cyan'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary-500/20">
            <Brain className="h-6 w-6 text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Reasoning Engine</h1>
            <p className="text-gray-400 text-sm">AI decision transparency and thought chains</p>
          </div>
        </div>

        <button
          onClick={() => triggerReasoning.mutate({})}
          disabled={triggerReasoning.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
        >
          {triggerReasoning.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          Trigger Analysis
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {tabs.map(({ id, label, icon: Icon, badge }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors relative',
              activeTab === id
                ? 'bg-primary-500/20 text-primary-400'
                : 'text-gray-400 hover:text-white hover:bg-dark-card'
            )}
          >
            <Icon size={18} />
            {label}
            {badge !== undefined && badge > 0 && (
              <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-accent-red/20 text-accent-red">
                {badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-4">
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Total Thoughts</span>
                <Lightbulb className="h-4 w-4 text-accent-amber" />
              </div>
              <p className="text-2xl font-bold">{dashboard.total_thoughts || 0}</p>
              <p className="text-xs text-gray-500 mt-1">
                {dashboard.thoughts_today || 0} today
              </p>
            </div>
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Pending Actions</span>
                <Zap className="h-4 w-4 text-accent-cyan" />
              </div>
              <p className="text-2xl font-bold">{pendingActions.length}</p>
              <p className="text-xs text-gray-500 mt-1">
                {dashboard.completed_actions || 0} completed
              </p>
            </div>
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Open Concerns</span>
                <AlertTriangle className="h-4 w-4 text-accent-red" />
              </div>
              <p className="text-2xl font-bold">{unresolvedConcerns.length}</p>
              <p className="text-xs text-gray-500 mt-1">
                {dashboard.total_concerns || 0} total
              </p>
            </div>
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Avg Reasoning Time</span>
                <Clock className="h-4 w-4 text-primary-400" />
              </div>
              <p className="text-2xl font-bold">{dashboard.avg_reasoning_time_ms || 0}ms</p>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-2 gap-6">
            {/* Recent Thoughts */}
            <div className="card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Recent Thoughts</h3>
                <button
                  onClick={() => setActiveTab('thoughts')}
                  className="text-sm text-primary-400 hover:text-primary-300"
                >
                  View All
                </button>
              </div>
              {loadingThoughts ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : thoughts.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No thoughts recorded</p>
              ) : (
                <div className="space-y-3">
                  {thoughts.slice(0, 5).map((thought) => (
                    <div
                      key={thought.id}
                      className="p-3 rounded-lg bg-dark-bg cursor-pointer hover:bg-dark-bg/80"
                      onClick={() => setSelectedThought(thought)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{thought.prompt}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={cn(
                              'px-2 py-0.5 rounded text-xs',
                              getStatusColor(thought.status)
                            )}>
                              {thought.status}
                            </span>
                            {thought.confidence && (
                              <span className="text-xs text-gray-500">
                                {(thought.confidence * 100).toFixed(0)}% confidence
                              </span>
                            )}
                          </div>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-500" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Pending Actions */}
            <div className="card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Pending Actions</h3>
                <button
                  onClick={() => setActiveTab('actions')}
                  className="text-sm text-primary-400 hover:text-primary-300"
                >
                  View All
                </button>
              </div>
              {loadingActions ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : pendingActions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No pending actions</p>
              ) : (
                <div className="space-y-3">
                  {pendingActions.slice(0, 5).map((action) => (
                    <div key={action.id} className="p-3 rounded-lg bg-dark-bg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium">{action.description}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={cn('text-xs', getPriorityColor(action.priority))}>
                              {action.priority}
                            </span>
                            <span className="text-xs text-gray-500">{action.action_type}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => approveAction.mutate(action.id)}
                            disabled={approveAction.isPending}
                            className="p-1.5 rounded bg-accent-green/20 text-accent-green hover:bg-accent-green/30"
                          >
                            <CheckCircle className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => rejectAction.mutate(action.id)}
                            disabled={rejectAction.isPending}
                            className="p-1.5 rounded bg-accent-red/20 text-accent-red hover:bg-accent-red/30"
                          >
                            <XCircle className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Active Concerns */}
          {unresolvedConcerns.length > 0 && (
            <div className="card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-accent-red" />
                  Active Concerns
                </h3>
                <button
                  onClick={() => setActiveTab('concerns')}
                  className="text-sm text-primary-400 hover:text-primary-300"
                >
                  View All
                </button>
              </div>
              <div className="space-y-2">
                {unresolvedConcerns.slice(0, 3).map((concern) => (
                  <div
                    key={concern.id}
                    className={cn(
                      'p-3 rounded-lg border',
                      getSeverityColor(concern.severity)
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium">{concern.title}</p>
                        <p className="text-sm opacity-80 mt-1">{concern.description}</p>
                      </div>
                      <span className="text-xs uppercase font-medium">{concern.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Thoughts Tab */}
      {activeTab === 'thoughts' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-gray-400">{thoughts.length} thoughts recorded</p>
            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ['reasoning-thoughts'] })}
              className="flex items-center gap-1 text-sm text-gray-400 hover:text-white"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>

          {loadingThoughts ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : thoughts.length === 0 ? (
            <div className="card p-12 text-center">
              <Lightbulb className="h-12 w-12 mx-auto mb-4 text-gray-600" />
              <h3 className="text-lg font-medium mb-2">No Thoughts</h3>
              <p className="text-gray-500">The reasoning engine hasn't recorded any thoughts yet.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {thoughts.map((thought) => (
                <div
                  key={thought.id}
                  className="card p-4 cursor-pointer hover:border-primary-500/30"
                  onClick={() => setSelectedThought(selectedThought?.id === thought.id ? null : thought)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold">{thought.prompt}</h3>
                      {thought.agent_name && (
                        <span className="text-xs text-gray-500">by {thought.agent_name}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        'px-2 py-0.5 rounded text-xs',
                        getStatusColor(thought.status)
                      )}>
                        {thought.status}
                      </span>
                      {thought.confidence && (
                        <span className="text-xs text-gray-400">
                          {(thought.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Expanded View */}
                  {selectedThought?.id === thought.id && (
                    <div className="mt-4 pt-4 border-t border-dark-border space-y-4">
                      {thought.reasoning_chain && thought.reasoning_chain.length > 0 && (
                        <div>
                          <p className="text-xs text-gray-500 mb-2">Reasoning Chain</p>
                          <div className="space-y-2">
                            {thought.reasoning_chain.map((step, i) => (
                              <div key={i} className="flex items-start gap-2">
                                <span className="text-xs text-primary-400 font-mono">{i + 1}.</span>
                                <p className="text-sm">{step}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {thought.conclusion && (
                        <div>
                          <p className="text-xs text-gray-500 mb-2">Conclusion</p>
                          <p className="text-sm p-3 rounded-lg bg-dark-bg">{thought.conclusion}</p>
                        </div>
                      )}
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>Created: {formatDate(thought.created_at)}</span>
                        {thought.duration_ms && (
                          <span>Duration: {thought.duration_ms}ms</span>
                        )}
                        {thought.actions_generated !== undefined && (
                          <span>Actions: {thought.actions_generated}</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Actions Tab */}
      {activeTab === 'actions' && (
        <div className="space-y-6">
          {/* Pending Actions */}
          {pendingActions.length > 0 && (
            <div className="card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-accent-amber flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Pending Approval ({pendingActions.length})
                </h3>
              </div>
              <div className="space-y-3">
                {pendingActions.map((action) => (
                  <div key={action.id} className="p-4 rounded-lg bg-dark-bg border border-accent-amber/30">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={cn('text-sm font-medium', getPriorityColor(action.priority))}>
                            [{action.priority.toUpperCase()}]
                          </span>
                          <span className="text-sm text-gray-400">{action.action_type}</span>
                        </div>
                        <p className="font-medium">{action.description}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          Created: {formatDate(action.created_at)}
                          {action.agent_name && ` • by ${action.agent_name}`}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => approveAction.mutate(action.id)}
                          disabled={approveAction.isPending}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-accent-green/20 text-accent-green hover:bg-accent-green/30"
                        >
                          {approveAction.isPending ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <CheckCircle className="h-4 w-4" />
                          )}
                          Approve
                        </button>
                        <button
                          onClick={() => rejectAction.mutate(action.id)}
                          disabled={rejectAction.isPending}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-accent-red/20 text-accent-red hover:bg-accent-red/30"
                        >
                          {rejectAction.isPending ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <XCircle className="h-4 w-4" />
                          )}
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* All Actions */}
          <div className="card p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Action History</h3>
              <button
                onClick={() => refetchActions()}
                className="flex items-center gap-1 text-sm text-gray-400 hover:text-white"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </button>
            </div>

            {loadingActions ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </div>
            ) : actions.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No actions recorded</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b border-dark-border">
                      <th className="pb-3 font-medium">Action</th>
                      <th className="pb-3 font-medium">Type</th>
                      <th className="pb-3 font-medium">Priority</th>
                      <th className="pb-3 font-medium">Status</th>
                      <th className="pb-3 font-medium">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {actions.filter(a => a.status !== 'pending').map((action) => (
                      <tr key={action.id} className="border-b border-dark-border/50">
                        <td className="py-3">
                          <span className="font-medium">{action.description}</span>
                        </td>
                        <td className="py-3 text-gray-400 text-sm">{action.action_type}</td>
                        <td className="py-3">
                          <span className={cn('text-sm', getPriorityColor(action.priority))}>
                            {action.priority}
                          </span>
                        </td>
                        <td className="py-3">
                          <span className={cn(
                            'px-2 py-0.5 rounded text-xs',
                            getStatusColor(action.status)
                          )}>
                            {action.status}
                          </span>
                        </td>
                        <td className="py-3 text-gray-400 text-sm">
                          {formatDate(action.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Concerns Tab */}
      {activeTab === 'concerns' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-gray-400">
              {unresolvedConcerns.length} unresolved of {concerns.length} total concerns
            </p>
            <button
              onClick={() => refetchConcerns()}
              className="flex items-center gap-1 text-sm text-gray-400 hover:text-white"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>

          {loadingConcerns ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : concerns.length === 0 ? (
            <div className="card p-12 text-center">
              <CheckCircle className="h-12 w-12 mx-auto mb-4 text-accent-green" />
              <h3 className="text-lg font-medium mb-2">No Concerns</h3>
              <p className="text-gray-500">The system hasn't detected any concerns.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {concerns.map((concern) => (
                <div
                  key={concern.id}
                  className={cn(
                    'card p-4 border',
                    concern.status === 'resolved' || concern.status === 'dismissed'
                      ? 'opacity-60'
                      : getSeverityColor(concern.severity)
                  )}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <AlertTriangle className={cn(
                          'h-4 w-4',
                          concern.severity === 'critical' ? 'text-accent-red' :
                          concern.severity === 'high' ? 'text-accent-amber' : 'text-gray-400'
                        )} />
                        <h3 className="font-semibold">{concern.title}</h3>
                      </div>
                      <p className="text-sm text-gray-400">{concern.description}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs uppercase font-medium">{concern.severity}</span>
                      <span className={cn(
                        'px-2 py-0.5 rounded text-xs',
                        getStatusColor(concern.status)
                      )}>
                        {concern.status}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-4">
                      <span>Category: {concern.category}</span>
                      {concern.source && <span>Source: {concern.source}</span>}
                      <span>Created: {formatDate(concern.created_at)}</span>
                    </div>
                    {(concern.status === 'open' || concern.status === 'investigating') && (
                      <button
                        onClick={() => resolveConcern.mutate({ id: concern.id })}
                        disabled={resolveConcern.isPending}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-accent-green/20 text-accent-green hover:bg-accent-green/30"
                      >
                        {resolveConcern.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle className="h-4 w-4" />
                        )}
                        Resolve
                      </button>
                    )}
                  </div>

                  {concern.resolution && (
                    <div className="mt-3 pt-3 border-t border-dark-border">
                      <p className="text-xs text-gray-500">Resolution:</p>
                      <p className="text-sm mt-1">{concern.resolution}</p>
                    </div>
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
