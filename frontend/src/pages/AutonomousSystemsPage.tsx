import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { autonomousApi } from '@/lib/api'
import {
  Cpu, Play, Pause, RefreshCw, Loader2, Power, PowerOff,
  Zap, Clock, Activity, BarChart3, Calendar, TrendingUp,
  CheckCircle, XCircle, ToggleLeft, ToggleRight
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Session 745: Autonomous Systems Dashboard
type TabType = 'overview' | 'situations' | 'triggers' | 'analytics'

interface SystemStatus {
  is_running: boolean
  uptime_seconds?: number
  last_started?: string
  last_paused?: string
  active_situations?: number
  total_triggers?: number
  events_today?: number
}

interface Situation {
  type: string
  name: string
  description: string
  is_enabled: boolean
  schedule?: string
  last_run?: string
  next_run?: string
  run_count?: number
  success_rate?: number
  avg_duration_seconds?: number
}

interface Trigger {
  id: string
  name: string
  trigger_type: string
  condition: string
  action: string
  is_active: boolean
  created_at: string
  last_triggered?: string
  trigger_count?: number
}

interface TriggerEvent {
  id: string
  trigger_id: string
  trigger_name?: string
  triggered_at: string
  status: 'success' | 'failed' | 'pending'
  result?: string
  duration_ms?: number
}

interface AnalyticsSummary {
  total_executions: number
  successful_executions: number
  failed_executions: number
  success_rate: number
  avg_execution_time_ms: number
  executions_today: number
  executions_this_week: number
  most_active_situation?: string
  most_triggered?: string
}

export default function AutonomousSystemsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const queryClient = useQueryClient()

  // Queries
  const { data: statusData, isLoading: loadingStatus } = useQuery({
    queryKey: ['autonomous-status'],
    queryFn: () => autonomousApi.status(),
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  const { data: situationsData, isLoading: loadingSituations } = useQuery({
    queryKey: ['autonomous-situations'],
    queryFn: () => autonomousApi.situations(),
    enabled: activeTab === 'overview' || activeTab === 'situations',
  })

  const { data: triggersData, isLoading: loadingTriggers } = useQuery({
    queryKey: ['autonomous-triggers'],
    queryFn: () => autonomousApi.triggers(),
    enabled: activeTab === 'overview' || activeTab === 'triggers',
  })

  const { data: eventsData, isLoading: loadingEvents } = useQuery({
    queryKey: ['autonomous-events'],
    queryFn: () => autonomousApi.triggerEvents({ limit: 50 }),
    enabled: activeTab === 'triggers',
  })

  const { data: analyticsData, isLoading: loadingAnalytics } = useQuery({
    queryKey: ['autonomous-analytics'],
    queryFn: () => autonomousApi.analyticsSummary(),
    enabled: activeTab === 'overview' || activeTab === 'analytics',
  })

  // Mutations
  const startSystem = useMutation({
    mutationFn: () => autonomousApi.start(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['autonomous-status'] })
    },
  })

  const pauseSystem = useMutation({
    mutationFn: () => autonomousApi.pause(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['autonomous-status'] })
    },
  })

  const toggleSituation = useMutation({
    mutationFn: (type: string) => autonomousApi.toggleSituation(type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['autonomous-situations'] })
    },
  })

  const runSituationNow = useMutation({
    mutationFn: (type: string) => autonomousApi.runSituationNow(type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['autonomous-situations'] })
      queryClient.invalidateQueries({ queryKey: ['autonomous-analytics'] })
    },
  })

  // Data extraction
  const status: SystemStatus = statusData?.data || {}
  const situations: Situation[] = situationsData?.data?.situations || situationsData?.data || []
  const triggers: Trigger[] = triggersData?.data?.triggers || triggersData?.data || []
  const events: TriggerEvent[] = eventsData?.data?.events || eventsData?.data || []
  const analytics: AnalyticsSummary = analyticsData?.data || {}

  const enabledSituations = situations.filter(s => s.is_enabled).length
  const activeTriggers = triggers.filter(t => t.is_active).length

  const tabs = [
    { id: 'overview' as TabType, label: 'Overview', icon: Activity },
    { id: 'situations' as TabType, label: 'Situations', icon: Cpu },
    { id: 'triggers' as TabType, label: 'Triggers', icon: Zap },
    { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
  ]

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '—'
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-accent-green/20 text-accent-green'
      case 'failed': return 'bg-accent-red/20 text-accent-red'
      case 'pending': return 'bg-accent-amber/20 text-accent-amber'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary-500/20">
            <Cpu className="h-6 w-6 text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Autonomous Systems</h1>
            <p className="text-gray-400 text-sm">Manage automated behaviors and triggers</p>
          </div>
        </div>

        {/* System Control */}
        <div className="flex items-center gap-3">
          {loadingStatus ? (
            <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
          ) : (
            <>
              <div className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg',
                status.is_running
                  ? 'bg-accent-green/20 text-accent-green'
                  : 'bg-gray-500/20 text-gray-400'
              )}>
                {status.is_running ? (
                  <Power className="h-4 w-4" />
                ) : (
                  <PowerOff className="h-4 w-4" />
                )}
                <span className="text-sm font-medium">
                  {status.is_running ? 'Running' : 'Paused'}
                </span>
              </div>
              {status.is_running ? (
                <button
                  onClick={() => pauseSystem.mutate()}
                  disabled={pauseSystem.isPending}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30 transition-colors"
                >
                  {pauseSystem.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Pause className="h-4 w-4" />
                  )}
                  Pause
                </button>
              ) : (
                <button
                  onClick={() => startSystem.mutate()}
                  disabled={startSystem.isPending}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent-green/20 text-accent-green hover:bg-accent-green/30 transition-colors"
                >
                  {startSystem.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  Start
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
              activeTab === id
                ? 'bg-primary-500/20 text-primary-400'
                : 'text-gray-400 hover:text-white hover:bg-dark-card'
            )}
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-4">
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Uptime</span>
                <Clock className="h-4 w-4 text-primary-400" />
              </div>
              <p className="text-2xl font-bold">{formatDuration(status.uptime_seconds)}</p>
            </div>
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Active Situations</span>
                <Cpu className="h-4 w-4 text-accent-cyan" />
              </div>
              <p className="text-2xl font-bold">{enabledSituations} / {situations.length}</p>
            </div>
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Active Triggers</span>
                <Zap className="h-4 w-4 text-accent-amber" />
              </div>
              <p className="text-2xl font-bold">{activeTriggers} / {triggers.length}</p>
            </div>
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Events Today</span>
                <Activity className="h-4 w-4 text-accent-green" />
              </div>
              <p className="text-2xl font-bold">{analytics.executions_today || 0}</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-6">
            {/* Recent Situations */}
            <div className="card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Situations</h3>
                <button
                  onClick={() => setActiveTab('situations')}
                  className="text-sm text-primary-400 hover:text-primary-300"
                >
                  View All
                </button>
              </div>
              {loadingSituations ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : situations.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No situations configured</p>
              ) : (
                <div className="space-y-2">
                  {situations.slice(0, 5).map((situation) => (
                    <div
                      key={situation.type}
                      className="flex items-center justify-between p-3 rounded-lg bg-dark-bg"
                    >
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          'w-2 h-2 rounded-full',
                          situation.is_enabled ? 'bg-accent-green' : 'bg-gray-500'
                        )} />
                        <div>
                          <p className="font-medium">{situation.name}</p>
                          <p className="text-xs text-gray-500">{situation.schedule || 'Manual'}</p>
                        </div>
                      </div>
                      <span className="text-sm text-gray-400">
                        {situation.run_count || 0} runs
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Triggers */}
            <div className="card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Recent Triggers</h3>
                <button
                  onClick={() => setActiveTab('triggers')}
                  className="text-sm text-primary-400 hover:text-primary-300"
                >
                  View All
                </button>
              </div>
              {loadingTriggers ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : triggers.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No triggers configured</p>
              ) : (
                <div className="space-y-2">
                  {triggers.slice(0, 5).map((trigger) => (
                    <div
                      key={trigger.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-dark-bg"
                    >
                      <div className="flex items-center gap-3">
                        <Zap className={cn(
                          'h-4 w-4',
                          trigger.is_active ? 'text-accent-amber' : 'text-gray-500'
                        )} />
                        <div>
                          <p className="font-medium">{trigger.name}</p>
                          <p className="text-xs text-gray-500">{trigger.trigger_type}</p>
                        </div>
                      </div>
                      <span className="text-sm text-gray-400">
                        {trigger.trigger_count || 0}x
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Analytics Summary */}
          {!loadingAnalytics && analytics.total_executions > 0 && (
            <div className="card p-4">
              <h3 className="font-semibold mb-4">Performance Summary</h3>
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center p-3 rounded-lg bg-dark-bg">
                  <p className="text-2xl font-bold text-accent-green">
                    {analytics.success_rate?.toFixed(1) || 0}%
                  </p>
                  <p className="text-xs text-gray-500">Success Rate</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-dark-bg">
                  <p className="text-2xl font-bold">{analytics.total_executions}</p>
                  <p className="text-xs text-gray-500">Total Executions</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-dark-bg">
                  <p className="text-2xl font-bold">{analytics.executions_this_week || 0}</p>
                  <p className="text-xs text-gray-500">This Week</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-dark-bg">
                  <p className="text-2xl font-bold">{analytics.avg_execution_time_ms || 0}ms</p>
                  <p className="text-xs text-gray-500">Avg Duration</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Situations Tab */}
      {activeTab === 'situations' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-gray-400">
              {enabledSituations} of {situations.length} situations enabled
            </p>
          </div>

          {loadingSituations ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : situations.length === 0 ? (
            <div className="card p-12 text-center">
              <Cpu className="h-12 w-12 mx-auto mb-4 text-gray-600" />
              <h3 className="text-lg font-medium mb-2">No Situations</h3>
              <p className="text-gray-500">No autonomous situations have been configured yet.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {situations.map((situation) => (
                <div key={situation.type} className="card p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold">{situation.name}</h3>
                        <span className={cn(
                          'px-2 py-0.5 rounded text-xs',
                          situation.is_enabled
                            ? 'bg-accent-green/20 text-accent-green'
                            : 'bg-gray-500/20 text-gray-400'
                        )}>
                          {situation.is_enabled ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mb-3">{situation.description}</p>
                      <div className="flex items-center gap-6 text-sm text-gray-500">
                        {situation.schedule && (
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {situation.schedule}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Activity className="h-3 w-3" />
                          {situation.run_count || 0} runs
                        </span>
                        {situation.success_rate !== undefined && (
                          <span className="flex items-center gap-1">
                            <TrendingUp className="h-3 w-3" />
                            {situation.success_rate.toFixed(1)}% success
                          </span>
                        )}
                        {situation.last_run && (
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Last: {formatDate(situation.last_run)}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => runSituationNow.mutate(situation.type)}
                        disabled={runSituationNow.isPending || !situation.is_enabled}
                        className={cn(
                          'flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors',
                          situation.is_enabled
                            ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30'
                            : 'bg-gray-500/20 text-gray-500 cursor-not-allowed'
                        )}
                      >
                        {runSituationNow.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                        Run Now
                      </button>
                      <button
                        onClick={() => toggleSituation.mutate(situation.type)}
                        disabled={toggleSituation.isPending}
                        className={cn(
                          'p-2 rounded-lg transition-colors',
                          situation.is_enabled
                            ? 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30'
                            : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                        )}
                      >
                        {toggleSituation.isPending ? (
                          <Loader2 className="h-5 w-5 animate-spin" />
                        ) : situation.is_enabled ? (
                          <ToggleRight className="h-5 w-5" />
                        ) : (
                          <ToggleLeft className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Triggers Tab */}
      {activeTab === 'triggers' && (
        <div className="space-y-6">
          {/* Triggers List */}
          <div className="card p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Configured Triggers</h3>
              <span className="text-sm text-gray-400">
                {activeTriggers} of {triggers.length} active
              </span>
            </div>

            {loadingTriggers ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </div>
            ) : triggers.length === 0 ? (
              <div className="text-center py-8">
                <Zap className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                <h3 className="font-medium mb-2">No Triggers</h3>
                <p className="text-gray-500 text-sm">No triggers have been configured yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {triggers.map((trigger) => (
                  <div
                    key={trigger.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-dark-bg"
                  >
                    <div className="flex items-center gap-4">
                      <Zap className={cn(
                        'h-5 w-5',
                        trigger.is_active ? 'text-accent-amber' : 'text-gray-500'
                      )} />
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{trigger.name}</p>
                          <span className={cn(
                            'px-2 py-0.5 rounded text-xs',
                            trigger.is_active
                              ? 'bg-accent-amber/20 text-accent-amber'
                              : 'bg-gray-500/20 text-gray-400'
                          )}>
                            {trigger.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mt-1">
                          <span className="text-gray-500">Type:</span> {trigger.trigger_type} •
                          <span className="text-gray-500 ml-2">Condition:</span> {trigger.condition}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>{trigger.trigger_count || 0} triggers</span>
                      {trigger.last_triggered && (
                        <span>Last: {formatDate(trigger.last_triggered)}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Events */}
          <div className="card p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Recent Trigger Events</h3>
              <button
                onClick={() => queryClient.invalidateQueries({ queryKey: ['autonomous-events'] })}
                className="flex items-center gap-1 text-sm text-gray-400 hover:text-white"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </button>
            </div>

            {loadingEvents ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </div>
            ) : events.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No recent trigger events</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-sm text-gray-500 border-b border-dark-border">
                      <th className="pb-3 font-medium">Trigger</th>
                      <th className="pb-3 font-medium">Time</th>
                      <th className="pb-3 font-medium">Status</th>
                      <th className="pb-3 font-medium">Duration</th>
                      <th className="pb-3 font-medium">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {events.slice(0, 20).map((event) => (
                      <tr key={event.id} className="border-b border-dark-border/50">
                        <td className="py-3">
                          <span className="font-medium">{event.trigger_name || event.trigger_id}</span>
                        </td>
                        <td className="py-3 text-gray-400 text-sm">
                          {formatDate(event.triggered_at)}
                        </td>
                        <td className="py-3">
                          <span className={cn(
                            'px-2 py-0.5 rounded text-xs',
                            getStatusColor(event.status)
                          )}>
                            {event.status}
                          </span>
                        </td>
                        <td className="py-3 text-gray-400 text-sm">
                          {event.duration_ms ? `${event.duration_ms}ms` : '—'}
                        </td>
                        <td className="py-3 text-sm text-gray-400 max-w-xs truncate">
                          {event.result || '—'}
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

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {loadingAnalytics ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : (
            <>
              {/* Stats Overview */}
              <div className="grid grid-cols-4 gap-4">
                <div className="card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">Total Executions</span>
                    <Activity className="h-4 w-4 text-primary-400" />
                  </div>
                  <p className="text-2xl font-bold">{analytics.total_executions || 0}</p>
                </div>
                <div className="card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">Success Rate</span>
                    <CheckCircle className="h-4 w-4 text-accent-green" />
                  </div>
                  <p className="text-2xl font-bold text-accent-green">
                    {analytics.success_rate?.toFixed(1) || 0}%
                  </p>
                </div>
                <div className="card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">Failed</span>
                    <XCircle className="h-4 w-4 text-accent-red" />
                  </div>
                  <p className="text-2xl font-bold text-accent-red">
                    {analytics.failed_executions || 0}
                  </p>
                </div>
                <div className="card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">Avg Duration</span>
                    <Clock className="h-4 w-4 text-accent-cyan" />
                  </div>
                  <p className="text-2xl font-bold">
                    {analytics.avg_execution_time_ms || 0}ms
                  </p>
                </div>
              </div>

              {/* Time-based Stats */}
              <div className="grid grid-cols-2 gap-6">
                <div className="card p-4">
                  <h3 className="font-semibold mb-4">Execution Breakdown</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Successful</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 h-2 rounded-full bg-dark-bg overflow-hidden">
                          <div
                            className="h-full bg-accent-green rounded-full"
                            style={{
                              width: `${analytics.total_executions
                                ? (analytics.successful_executions / analytics.total_executions * 100)
                                : 0}%`
                            }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">
                          {analytics.successful_executions || 0}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Failed</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 h-2 rounded-full bg-dark-bg overflow-hidden">
                          <div
                            className="h-full bg-accent-red rounded-full"
                            style={{
                              width: `${analytics.total_executions
                                ? (analytics.failed_executions / analytics.total_executions * 100)
                                : 0}%`
                            }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">
                          {analytics.failed_executions || 0}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card p-4">
                  <h3 className="font-semibold mb-4">Activity Timeline</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
                      <span className="text-gray-400">Today</span>
                      <span className="font-bold">{analytics.executions_today || 0}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
                      <span className="text-gray-400">This Week</span>
                      <span className="font-bold">{analytics.executions_this_week || 0}</span>
                    </div>
                    {analytics.most_active_situation && (
                      <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
                        <span className="text-gray-400">Most Active</span>
                        <span className="font-medium text-primary-400">
                          {analytics.most_active_situation}
                        </span>
                      </div>
                    )}
                    {analytics.most_triggered && (
                      <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
                        <span className="text-gray-400">Most Triggered</span>
                        <span className="font-medium text-accent-amber">
                          {analytics.most_triggered}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
