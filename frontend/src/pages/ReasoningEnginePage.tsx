import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reasoningApi } from '@/lib/api'
import {
  Brain, Lightbulb, Zap, AlertTriangle, CheckCircle, XCircle,
  Clock, RefreshCw, Loader2, ChevronRight, Play, BarChart3,
  TrendingUp, Target, Eye, Activity
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

// Session 782: Full thought detail from API
interface ThoughtDetail {
  id: string
  cycle_number: number
  cycle_type: string
  context_summary: string
  context_data: Record<string, unknown>
  reflection: string
  insights: Array<{ insight: string; confidence: number; category: string }>
  patterns: Array<{ pattern: string; evidence: string; strength: number }>
  opportunities: Array<{ opportunity: string; potential_impact: string; urgency: string }>
  concerns: Array<{ concern: string; severity: string; recommendation: string }>
  decisions: Array<{
    action_type: string
    action_name: string
    reasoning: string
    params: Record<string, unknown>
    priority: string
    expected_outcome: string
  }>
  actions_planned: unknown[]
  actions_executed: Array<{ action_id: string; type: string; name: string; success: boolean }>
  priority_score: number
  execution_status: string
  thinking_duration_seconds: number
  model_used: string
  token_usage: Record<string, unknown>
  started_at: string
  completed_at: string | null
}

interface ThoughtAction {
  id: string
  action_type: string
  action_name: string
  reasoning: string
  priority: string
  status: string
  result_summary: string
  error_message: string
  created_at: string
}

// Session 782: Pending action notification from API
interface PendingNotification {
  id: string
  title: string
  message: string
  priority: string
  category: string
  severity: string
  concern_id: string | null
  quick_actions: Array<{
    label: string
    style: string
    action: string
  }>
  created_at: string
  is_read: boolean
}

// Session 782: Full concern detail from API
interface ConcernDetail {
  id: string
  concern_text: string
  category: string
  severity: string
  status: string
  times_detected: number
  days_active: number
  first_seen_cycle: number | null
  last_seen_cycle: number | null
  actions_taken: Array<{
    id: string
    action_type: string
    action_name: string
    status: string
    created_at: string
  }>
  verification_metric: string | null
  last_verification: Record<string, unknown> | null
  last_verified_at: string | null
  resolution_notes: string | null
  created_at: string
  resolved_at: string | null
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
  const [selectedConcern, setSelectedConcern] = useState<Concern | null>(null)
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

  // Session 782: Fetch full thought detail when a thought is selected
  const { data: thoughtDetailData, isLoading: loadingThoughtDetail } = useQuery({
    queryKey: ['reasoning-thought-detail', selectedThought?.id],
    queryFn: () => selectedThought ? reasoningApi.thoughtDetail(selectedThought.id) : null,
    enabled: !!selectedThought?.id,
  })

  const thoughtDetail: ThoughtDetail | null = thoughtDetailData?.data?.thought || null
  const thoughtActions: ThoughtAction[] = thoughtDetailData?.data?.actions || []

  // Session 782: Fetch full concern detail when a concern is selected
  const { data: concernDetailData, isLoading: loadingConcernDetail } = useQuery({
    queryKey: ['reasoning-concern-detail', selectedConcern?.id],
    queryFn: () => selectedConcern ? reasoningApi.concernDetail(selectedConcern.id) : null,
    enabled: !!selectedConcern?.id,
  })

  const concernDetail: ConcernDetail | null = concernDetailData?.data?.concern || null

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

  const deferAction = useMutation({
    mutationFn: (id: string) => reasoningApi.deferAction(id),
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

  // Helper functions - defined before data extraction that uses them
  function mapThoughtStatus(status: string): 'pending' | 'processing' | 'completed' | 'failed' {
    switch (status) {
      case 'completed': return 'completed'
      case 'failed': return 'failed'
      case 'thinking':
      case 'deciding':
      case 'executing': return 'processing'
      default: return 'pending'
    }
  }

  function mapActionStatus(status: string): 'pending' | 'approved' | 'rejected' | 'executed' | 'failed' {
    switch (status) {
      case 'completed':
      case 'executed': return 'executed'
      case 'approved':
      case 'queued': return 'approved'
      case 'rejected':
      case 'cancelled': return 'rejected'
      case 'failed': return 'failed'
      default: return 'pending'
    }
  }

  function mapPriority(priority: string): 'low' | 'medium' | 'high' | 'critical' {
    switch (priority) {
      case 'critical': return 'critical'
      case 'high': return 'high'
      case 'low':
      case 'background': return 'low'
      default: return 'medium'
    }
  }

  function mapSeverity(severity: string): 'low' | 'medium' | 'high' | 'critical' {
    switch (severity) {
      case 'critical': return 'critical'
      case 'high': return 'high'
      case 'low': return 'low'
      default: return 'medium'
    }
  }

  function mapConcernStatus(status: string): 'open' | 'investigating' | 'resolved' | 'dismissed' {
    switch (status) {
      case 'resolved': return 'resolved'
      case 'accepted': return 'dismissed'
      case 'in_progress':
      case 'monitoring': return 'investigating'
      default: return 'open'
    }
  }

  // Data extraction - map API response to expected interface
  // Session 782: Handle actual API structure from views_autonomous_reasoning.py
  const rawDashboard = dashboardData?.data || {}
  const dashboard: DashboardStats = {
    total_thoughts: rawDashboard.thought_stats?.total || 0,
    active_thoughts: rawDashboard.thought_stats?.last_24h || 0,
    total_actions: rawDashboard.action_stats?.total || 0,
    pending_actions: rawDashboard.action_stats?.total - rawDashboard.action_stats?.completed || 0,
    completed_actions: rawDashboard.action_stats?.completed || 0,
    total_concerns: 0, // Will be set from concerns data
    unresolved_concerns: 0,
    avg_reasoning_time_ms: 0,
    thoughts_today: rawDashboard.thought_stats?.last_24h || 0,
    actions_today: rawDashboard.action_stats?.last_24h || 0,
  }

  // Map thoughts from API format to frontend format
  const rawThoughts = thoughtsData?.data?.thoughts || thoughtsData?.data?.results || []
  const thoughts: Thought[] = Array.isArray(rawThoughts) ? rawThoughts.map((t: Record<string, unknown>) => ({
    id: t.id as string,
    prompt: (t.context_summary as string) || `Thinking Cycle #${t.cycle_number}`,
    context: t.context_summary as string,
    status: mapThoughtStatus(t.execution_status as string),
    reasoning_chain: t.insights as string[] || [],
    conclusion: t.reflection as string,
    confidence: t.priority_score ? (t.priority_score as number) / 10 : undefined,
    created_at: t.started_at as string,
    completed_at: t.completed_at as string,
    duration_ms: t.thinking_duration_seconds ? (t.thinking_duration_seconds as number) * 1000 : undefined,
    agent_name: 'ThinkingAgent',
    actions_generated: t.actions_executed_count as number || 0,
  })) : []

  // Map actions from API format
  const rawActions = actionsData?.data?.actions || actionsData?.data?.results || []
  const actions: Action[] = Array.isArray(rawActions) ? rawActions.map((a: Record<string, unknown>) => ({
    id: a.id as string,
    thought_id: a.thought_record_id as string,
    action_type: a.action_type as string,
    description: (a.action_name as string) || (a.description as string) || 'Unknown action',
    status: mapActionStatus(a.status as string),
    priority: mapPriority(a.priority as string),
    created_at: a.created_at as string,
    executed_at: a.completed_at as string,
    result: a.result_summary as string,
    requires_approval: a.priority === 'critical' || a.priority === 'high',
    agent_name: 'ThinkingAgent',
  })) : []

  // Map pending actions (different API structure - uses notifications)
  // Session 782: Use full notification structure for better detail display
  const rawPendingNotifications = pendingActionsData?.data?.notifications || []
  const pendingNotifications: PendingNotification[] = Array.isArray(rawPendingNotifications)
    ? rawPendingNotifications.map((n: Record<string, unknown>) => ({
        id: n.id as string,
        title: n.title as string || 'Action Required',
        message: n.message as string || '',
        priority: n.priority as string || 'medium',
        category: n.category as string || 'general',
        severity: n.severity as string || 'medium',
        concern_id: n.concern_id as string | null,
        quick_actions: (n.quick_actions as PendingNotification['quick_actions']) || [],
        created_at: n.created_at as string,
        is_read: n.is_read as boolean || false,
      }))
    : []

  // Legacy format for backwards compatibility
  const pendingActions: Action[] = pendingNotifications.map((n) => ({
    id: n.id,
    action_type: n.category,
    description: n.message,
    status: 'pending' as const,
    priority: mapPriority(n.priority),
    created_at: n.created_at,
    requires_approval: true,
    agent_name: 'ThinkingAgent',
  }))

  // Map concerns from API format
  const rawConcerns = concernsData?.data?.recent || concernsData?.data?.concerns || []
  const concerns: Concern[] = Array.isArray(rawConcerns) ? rawConcerns.map((c: Record<string, unknown>) => ({
    id: c.id as string,
    title: ((c.text as string) || (c.concern_text as string) || 'Unknown concern').slice(0, 100),
    description: (c.text as string) || (c.concern_text as string) || '',
    severity: mapSeverity(c.severity as string),
    category: (c.category as string) || 'general',
    status: mapConcernStatus(c.status as string),
    created_at: c.created_at as string,
    resolved_at: c.resolved_at as string,
    resolution: c.resolution_notes as string,
    source: 'ThinkingAgent',
    affected_agents: [],
  })) : []

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
                      className="p-3 rounded-lg bg-dark-bg cursor-pointer hover:bg-dark-bg/80 hover:ring-1 hover:ring-primary-500/30 transition-all"
                      onClick={() => {
                        setSelectedThought(thought)
                        setActiveTab('thoughts')
                      }}
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
                                {((thought.confidence ?? 0) * 100).toFixed(0)}% confidence
                              </span>
                            )}
                            {thought.actions_generated !== undefined && thought.actions_generated > 0 && (
                              <span className="text-xs text-gray-500">
                                {thought.actions_generated} actions
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
                          {((thought.confidence ?? 0) * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Session 782: Rich Expanded Detail View */}
                  {selectedThought?.id === thought.id && (
                    <div className="mt-4 pt-4 border-t border-dark-border space-y-4">
                      {loadingThoughtDetail ? (
                        <div className="flex justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                        </div>
                      ) : thoughtDetail ? (
                        <>
                          {/* Reflection */}
                          {thoughtDetail.reflection && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <Brain className="h-3 w-3" /> Reflection
                              </p>
                              <p className="text-sm p-3 rounded-lg bg-dark-bg whitespace-pre-wrap">
                                {thoughtDetail.reflection}
                              </p>
                            </div>
                          )}

                          {/* Insights */}
                          {thoughtDetail.insights && thoughtDetail.insights.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <Lightbulb className="h-3 w-3" /> Insights ({thoughtDetail.insights.length})
                              </p>
                              <div className="space-y-2">
                                {thoughtDetail.insights.map((insight, i) => (
                                  <div key={i} className="p-2 rounded-lg bg-dark-bg flex items-start gap-2">
                                    <span className={cn(
                                      'px-1.5 py-0.5 rounded text-xs shrink-0',
                                      insight.category === 'opportunity' ? 'bg-accent-green/20 text-accent-green' :
                                      insight.category === 'concern' ? 'bg-accent-red/20 text-accent-red' :
                                      insight.category === 'pattern' ? 'bg-accent-cyan/20 text-accent-cyan' :
                                      'bg-accent-amber/20 text-accent-amber'
                                    )}>
                                      {insight.category}
                                    </span>
                                    <p className="text-sm flex-1">{insight.insight}</p>
                                    <span className="text-xs text-gray-500 shrink-0">
                                      {((insight.confidence ?? 0) * 100).toFixed(0)}%
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Patterns */}
                          {thoughtDetail.patterns && thoughtDetail.patterns.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <Activity className="h-3 w-3" /> Patterns ({thoughtDetail.patterns.length})
                              </p>
                              <div className="space-y-2">
                                {thoughtDetail.patterns.map((pattern, i) => (
                                  <div key={i} className="p-2 rounded-lg bg-dark-bg">
                                    <div className="flex items-center justify-between mb-1">
                                      <p className="text-sm font-medium">{pattern.pattern}</p>
                                      <span className="text-xs text-gray-500">
                                        {((pattern.strength ?? 0) * 100).toFixed(0)}% strength
                                      </span>
                                    </div>
                                    <p className="text-xs text-gray-400">{pattern.evidence}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Opportunities */}
                          {thoughtDetail.opportunities && thoughtDetail.opportunities.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <TrendingUp className="h-3 w-3" /> Opportunities ({thoughtDetail.opportunities.length})
                              </p>
                              <div className="space-y-2">
                                {thoughtDetail.opportunities.map((opp, i) => (
                                  <div key={i} className="p-2 rounded-lg bg-dark-bg flex items-start gap-2">
                                    <Target className={cn(
                                      'h-4 w-4 shrink-0 mt-0.5',
                                      opp.potential_impact === 'high' ? 'text-accent-green' :
                                      opp.potential_impact === 'medium' ? 'text-accent-amber' : 'text-gray-400'
                                    )} />
                                    <div className="flex-1">
                                      <p className="text-sm">{opp.opportunity}</p>
                                      <div className="flex gap-2 mt-1">
                                        <span className="text-xs text-gray-500">Impact: {opp.potential_impact}</span>
                                        <span className="text-xs text-gray-500">Urgency: {opp.urgency}</span>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Concerns */}
                          {thoughtDetail.concerns && thoughtDetail.concerns.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <AlertTriangle className="h-3 w-3" /> Concerns ({thoughtDetail.concerns.length})
                              </p>
                              <div className="space-y-2">
                                {thoughtDetail.concerns.map((concern, i) => (
                                  <div key={i} className={cn(
                                    'p-2 rounded-lg border',
                                    concern.severity === 'high' ? 'bg-accent-red/10 border-accent-red/30' :
                                    concern.severity === 'medium' ? 'bg-accent-amber/10 border-accent-amber/30' :
                                    'bg-dark-bg border-dark-border'
                                  )}>
                                    <div className="flex items-start gap-2">
                                      <span className={cn(
                                        'text-xs uppercase font-medium shrink-0',
                                        concern.severity === 'high' ? 'text-accent-red' :
                                        concern.severity === 'medium' ? 'text-accent-amber' : 'text-gray-400'
                                      )}>
                                        {concern.severity}
                                      </span>
                                      <div className="flex-1">
                                        <p className="text-sm">{concern.concern}</p>
                                        <p className="text-xs text-gray-400 mt-1">
                                          Recommendation: {concern.recommendation}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Decisions / Actions Planned */}
                          {thoughtDetail.decisions && thoughtDetail.decisions.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <Zap className="h-3 w-3" /> Decisions ({thoughtDetail.decisions.length})
                              </p>
                              <div className="space-y-2">
                                {thoughtDetail.decisions.map((decision, i) => (
                                  <div key={i} className="p-2 rounded-lg bg-dark-bg border border-primary-500/20">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className={cn(
                                        'px-1.5 py-0.5 rounded text-xs',
                                        decision.priority === 'critical' ? 'bg-accent-red/20 text-accent-red' :
                                        decision.priority === 'high' ? 'bg-accent-amber/20 text-accent-amber' :
                                        'bg-primary-500/20 text-primary-400'
                                      )}>
                                        {decision.priority}
                                      </span>
                                      <span className="text-xs text-gray-500">{decision.action_type}</span>
                                    </div>
                                    <p className="text-sm font-medium">{decision.action_name}</p>
                                    <p className="text-xs text-gray-400 mt-1">{decision.reasoning}</p>
                                    {decision.expected_outcome && (
                                      <p className="text-xs text-gray-500 mt-1">
                                        Expected: {decision.expected_outcome}
                                      </p>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Actions Executed */}
                          {thoughtActions.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <CheckCircle className="h-3 w-3" /> Actions Executed ({thoughtActions.length})
                              </p>
                              <div className="space-y-2">
                                {thoughtActions.map((action) => (
                                  <div key={action.id} className="p-2 rounded-lg bg-dark-bg flex items-start gap-2">
                                    {action.status === 'completed' ? (
                                      <CheckCircle className="h-4 w-4 text-accent-green shrink-0 mt-0.5" />
                                    ) : (
                                      <XCircle className="h-4 w-4 text-accent-red shrink-0 mt-0.5" />
                                    )}
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm font-medium">{action.action_name}</p>
                                      <p className="text-xs text-gray-400">{action.action_type}</p>
                                      {action.result_summary && (
                                        <p className="text-xs text-gray-500 mt-1 truncate">
                                          Result: {action.result_summary}
                                        </p>
                                      )}
                                      {action.error_message && (
                                        <p className="text-xs text-accent-red mt-1">
                                          Error: {action.error_message}
                                        </p>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Metadata */}
                          <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 pt-2 border-t border-dark-border">
                            <span>Cycle #{thoughtDetail.cycle_number}</span>
                            <span>Started: {formatDate(thoughtDetail.started_at)}</span>
                            {thoughtDetail.thinking_duration_seconds > 0 && (
                              <span>Duration: {(thoughtDetail.thinking_duration_seconds ?? 0).toFixed(1)}s</span>
                            )}
                            {thoughtDetail.priority_score > 0 && (
                              <span>Priority: {(thoughtDetail.priority_score ?? 0).toFixed(1)}/10</span>
                            )}
                          </div>
                        </>
                      ) : (
                        <p className="text-gray-500 text-center py-4">No details available</p>
                      )}
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
          {/* Session 782: Enhanced Pending Actions with full notification details */}
          {pendingNotifications.length > 0 && (
            <div className="card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-accent-amber flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Pending Approval ({pendingNotifications.length})
                </h3>
              </div>
              <div className="space-y-4">
                {pendingNotifications.map((notification) => (
                  <div key={notification.id} className={cn(
                    'p-4 rounded-lg border',
                    notification.severity === 'high' ? 'bg-accent-red/10 border-accent-red/30' :
                    notification.severity === 'medium' ? 'bg-accent-amber/10 border-accent-amber/30' :
                    'bg-dark-bg border-dark-border'
                  )}>
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className={cn(
                          'h-5 w-5',
                          notification.severity === 'high' ? 'text-accent-red' :
                          notification.severity === 'medium' ? 'text-accent-amber' : 'text-gray-400'
                        )} />
                        <div>
                          <h4 className="font-semibold">{notification.title}</h4>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className={cn(
                              'px-1.5 py-0.5 rounded text-xs',
                              notification.severity === 'high' ? 'bg-accent-red/20 text-accent-red' :
                              notification.severity === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                              'bg-gray-500/20 text-gray-400'
                            )}>
                              {notification.severity}
                            </span>
                            <span className="text-xs text-gray-500">{notification.category}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Full Message */}
                    <div className="mb-4">
                      <p className="text-sm p-3 rounded-lg bg-dark-bg/50 whitespace-pre-wrap">
                        {notification.message}
                      </p>
                    </div>

                    {/* What happens section */}
                    <div className="mb-4 p-3 rounded-lg bg-primary-500/10 border border-primary-500/20">
                      <p className="text-xs text-primary-400 font-medium mb-1">What happens when you respond:</p>
                      <ul className="text-xs text-gray-400 space-y-1">
                        <li>• <span className="text-accent-green">Accept Risk</span>: Acknowledge the concern and continue with current approach</li>
                        <li>• <span className="text-accent-red">Reject</span>: Flag this as a problem that needs immediate attention</li>
                        <li>• <span className="text-gray-400">Defer</span>: Postpone the decision for later review</li>
                      </ul>
                    </div>

                    {/* Metadata */}
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                      <span>Created: {formatDate(notification.created_at)}</span>
                      {notification.concern_id && (
                        <span>Linked to concern</span>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-2 pt-3 border-t border-dark-border">
                      <button
                        onClick={() => approveAction.mutate(notification.id)}
                        disabled={approveAction.isPending || rejectAction.isPending || deferAction.isPending}
                        className="flex items-center gap-1 px-4 py-2 rounded-lg bg-accent-green/20 text-accent-green hover:bg-accent-green/30 transition-colors"
                      >
                        {approveAction.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle className="h-4 w-4" />
                        )}
                        Accept Risk
                      </button>
                      <button
                        onClick={() => rejectAction.mutate(notification.id)}
                        disabled={approveAction.isPending || rejectAction.isPending || deferAction.isPending}
                        className="flex items-center gap-1 px-4 py-2 rounded-lg bg-accent-red/20 text-accent-red hover:bg-accent-red/30 transition-colors"
                      >
                        {rejectAction.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <XCircle className="h-4 w-4" />
                        )}
                        Reject
                      </button>
                      <button
                        onClick={() => deferAction.mutate(notification.id)}
                        disabled={approveAction.isPending || rejectAction.isPending || deferAction.isPending}
                        className="flex items-center gap-1 px-4 py-2 rounded-lg bg-gray-500/20 text-gray-400 hover:bg-gray-500/30 transition-colors"
                      >
                        {deferAction.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Clock className="h-4 w-4" />
                        )}
                        Defer
                      </button>
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
                    'card p-4 border cursor-pointer hover:border-primary-500/30 transition-all',
                    concern.status === 'resolved' || concern.status === 'dismissed'
                      ? 'opacity-60'
                      : getSeverityColor(concern.severity)
                  )}
                  onClick={() => setSelectedConcern(selectedConcern?.id === concern.id ? null : concern)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
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
                      <ChevronRight className={cn(
                        'h-4 w-4 text-gray-500 transition-transform',
                        selectedConcern?.id === concern.id && 'rotate-90'
                      )} />
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
                        onClick={(e) => {
                          e.stopPropagation()
                          resolveConcern.mutate({ id: concern.id })
                        }}
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

                  {/* Session 782: Rich Expanded Concern Detail View */}
                  {selectedConcern?.id === concern.id && (
                    <div className="mt-4 pt-4 border-t border-dark-border space-y-4" onClick={(e) => e.stopPropagation()}>
                      {loadingConcernDetail ? (
                        <div className="flex justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                        </div>
                      ) : concernDetail ? (
                        <>
                          {/* Full Concern Text */}
                          <div>
                            <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                              <AlertTriangle className="h-3 w-3" /> Full Description
                            </p>
                            <p className="text-sm p-3 rounded-lg bg-dark-bg whitespace-pre-wrap">
                              {concernDetail.concern_text}
                            </p>
                          </div>

                          {/* Detection Info */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <div className="p-2 rounded-lg bg-dark-bg">
                              <p className="text-xs text-gray-500">Times Detected</p>
                              <p className="text-lg font-semibold">{concernDetail.times_detected}</p>
                            </div>
                            <div className="p-2 rounded-lg bg-dark-bg">
                              <p className="text-xs text-gray-500">Days Active</p>
                              <p className="text-lg font-semibold">{concernDetail.days_active}</p>
                            </div>
                            <div className="p-2 rounded-lg bg-dark-bg">
                              <p className="text-xs text-gray-500">First Seen</p>
                              <p className="text-sm font-medium">
                                {concernDetail.first_seen_cycle ? `Cycle #${concernDetail.first_seen_cycle}` : '—'}
                              </p>
                            </div>
                            <div className="p-2 rounded-lg bg-dark-bg">
                              <p className="text-xs text-gray-500">Last Seen</p>
                              <p className="text-sm font-medium">
                                {concernDetail.last_seen_cycle ? `Cycle #${concernDetail.last_seen_cycle}` : '—'}
                              </p>
                            </div>
                          </div>

                          {/* Actions Taken */}
                          {concernDetail.actions_taken && concernDetail.actions_taken.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <Zap className="h-3 w-3" /> Actions Taken ({concernDetail.actions_taken.length})
                              </p>
                              <div className="space-y-2">
                                {concernDetail.actions_taken.map((action) => (
                                  <div key={action.id} className="p-2 rounded-lg bg-dark-bg flex items-center gap-2">
                                    {action.status === 'completed' ? (
                                      <CheckCircle className="h-4 w-4 text-accent-green shrink-0" />
                                    ) : action.status === 'failed' ? (
                                      <XCircle className="h-4 w-4 text-accent-red shrink-0" />
                                    ) : (
                                      <Clock className="h-4 w-4 text-accent-amber shrink-0" />
                                    )}
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm font-medium truncate">{action.action_name}</p>
                                      <p className="text-xs text-gray-500">{action.action_type}</p>
                                    </div>
                                    <span className={cn(
                                      'px-2 py-0.5 rounded text-xs shrink-0',
                                      getStatusColor(action.status)
                                    )}>
                                      {action.status}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Verification Info */}
                          {concernDetail.verification_metric && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <Eye className="h-3 w-3" /> Verification
                              </p>
                              <div className="p-3 rounded-lg bg-dark-bg">
                                <p className="text-sm mb-1">
                                  <span className="text-gray-500">Metric:</span> {concernDetail.verification_metric}
                                </p>
                                {concernDetail.last_verified_at && (
                                  <p className="text-xs text-gray-500">
                                    Last verified: {formatDate(concernDetail.last_verified_at)}
                                  </p>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Resolution Notes */}
                          {concernDetail.resolution_notes && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                <CheckCircle className="h-3 w-3" /> Resolution Notes
                              </p>
                              <p className="text-sm p-3 rounded-lg bg-accent-green/10 border border-accent-green/20">
                                {concernDetail.resolution_notes}
                              </p>
                            </div>
                          )}

                          {/* Metadata */}
                          <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 pt-2 border-t border-dark-border">
                            <span>Created: {formatDate(concernDetail.created_at)}</span>
                            {concernDetail.resolved_at && (
                              <span>Resolved: {formatDate(concernDetail.resolved_at)}</span>
                            )}
                          </div>
                        </>
                      ) : (
                        <p className="text-gray-500 text-center py-4">No details available</p>
                      )}
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
