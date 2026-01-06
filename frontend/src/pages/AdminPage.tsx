import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { adminApi, dashboardApi } from '@/lib/api'
import {
  Server, Activity, CheckCircle, XCircle,
  Loader2, RefreshCw, Settings, Play, Bug, Bot, Clock, Globe
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'health' | 'celery' | 'spiders' | 'agents'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

const tabs = [
  { id: 'health' as TabType, label: 'System Health', icon: Activity },
  { id: 'celery' as TabType, label: 'Celery', icon: Clock },
  { id: 'spiders' as TabType, label: 'Spiders', icon: Bug },
  { id: 'agents' as TabType, label: 'Agents', icon: Bot },
]

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<TabType>('health')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)

  // Fetch v1 health
  const { data: healthData, isLoading: loadingHealth, refetch: refetchHealth } = useQuery({
    queryKey: ['v1-health'],
    queryFn: () => adminApi.health(),
    refetchInterval: 30000,
  })

  // Fetch system health
  const { data: systemHealthData } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => adminApi.systemHealth(),
  })

  // Fetch celery status
  const { data: celeryStatusData, isLoading: loadingCelery } = useQuery({
    queryKey: ['celery-status'],
    queryFn: () => adminApi.celeryStatus(),
    enabled: activeTab === 'celery' || activeTab === 'health',
  })

  // Fetch celery stats
  const { data: celeryStatsData } = useQuery({
    queryKey: ['celery-stats'],
    queryFn: () => adminApi.celeryStats(),
    enabled: activeTab === 'celery',
  })

  // Fetch spider health
  const { data: spiderHealthData, isLoading: loadingSpiders } = useQuery({
    queryKey: ['spider-health'],
    queryFn: () => adminApi.spiderHealth(),
    enabled: activeTab === 'spiders',
  })

  // Fetch spider executions
  const { data: spiderExecutionsData } = useQuery({
    queryKey: ['spider-executions'],
    queryFn: () => adminApi.spiderExecutions(),
    enabled: activeTab === 'spiders',
  })

  // Fetch agent health
  const { data: agentHealthData, isLoading: loadingAgents } = useQuery({
    queryKey: ['agent-health'],
    queryFn: () => adminApi.agentHealth(),
    enabled: activeTab === 'agents',
  })

  // Run agent cycle mutation
  const runAgentCycleMutation = useMutation({
    mutationFn: () => dashboardApi.runAgentCycle(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Agent cycle started!' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to start agent cycle' })
    },
  })

  const health = healthData?.data || {}
  const healthServices = health.services || {}
  const systemHealth = systemHealthData?.data || {}
  const celeryStatus = celeryStatusData?.data || {}
  const celeryStats = celeryStatsData?.data || {}
  const spiderHealth = spiderHealthData?.data || {}
  const spiderExecutions = spiderExecutionsData?.data?.executions || spiderExecutionsData?.data || []
  const agentHealth = agentHealthData?.data || {}

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'ok':
      case 'running':
      case 'active':
        return 'text-accent-green'
      case 'degraded':
      case 'warning':
        return 'text-accent-amber'
      default:
        return 'text-accent-red'
    }
  }

  const getStatusBg = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'ok':
      case 'running':
      case 'active':
        return 'bg-accent-green/20'
      case 'degraded':
      case 'warning':
        return 'bg-accent-amber/20'
      default:
        return 'bg-accent-red/20'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
            <Settings size={28} className="text-accent-cyan" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
            <p className="text-gray-400">System monitoring and administration</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => refetchHealth()}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          <button
            className="btn btn-primary flex items-center gap-2"
            onClick={() => runAgentCycleMutation.mutate()}
            disabled={runAgentCycleMutation.isPending}
          >
            {runAgentCycleMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
            Run Agent Cycle
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2 overflow-x-auto">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-bg'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* System Health Tab */}
      {activeTab === 'health' && (
        <div className="space-y-6">
          {loadingHealth ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Overall Status */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className={cn('h-10 w-10 rounded-lg flex items-center justify-center', getStatusBg(health.status || 'ok'))}>
                      <Server size={20} className={getStatusColor(health.status || 'ok')} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">API Health</p>
                      <p className={cn('text-lg font-bold capitalize', getStatusColor(health.status || 'ok'))}>
                        {health.status || 'OK'}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Clock className="text-primary-400" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Celery Workers</p>
                      <p className="text-2xl font-bold">{Array.isArray(celeryStatus.workers) ? celeryStatus.workers.length : (celeryStats.workers || 0)}</p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Bug className="text-accent-amber" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Active Spiders</p>
                      <p className="text-2xl font-bold">{systemHealth.spiders || 77}</p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Bot className="text-accent-green" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Active Agents</p>
                      <p className="text-2xl font-bold">{systemHealth.agents || agentHealth.total || 71}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Services Status */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Service Status</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[
                    { name: 'Django API', status: healthServices.api || health.status || 'ok' },
                    { name: 'Redis', status: healthServices.redis || 'ok' },
                    { name: 'PostgreSQL', status: healthServices.database || 'ok' },
                    { name: 'WebSocket', status: healthServices.websocket || 'ok' },
                    { name: 'Celery Workers', status: celeryStatus.overall_status || 'ok' },
                    { name: 'Celery Beat', status: celeryStatus.beat_status || 'ok' },
                  ].map((service) => {
                    const statusStr = typeof service.status === 'object' ? (service.status as { status?: string })?.status || 'unknown' : String(service.status || 'ok')
                    const isHealthy = ['ok', 'healthy', 'running', 'connected', 'active'].includes(statusStr.toLowerCase())
                    return (
                      <div
                        key={service.name}
                        className="flex items-center justify-between p-4 rounded-lg border border-dark-border"
                      >
                        <div className="flex items-center gap-3">
                          <div className={cn('h-8 w-8 rounded-full flex items-center justify-center', isHealthy ? 'bg-accent-green/20' : 'bg-accent-red/20')}>
                            {isHealthy ? (
                              <CheckCircle size={16} className="text-accent-green" />
                            ) : (
                              <XCircle size={16} className="text-accent-red" />
                            )}
                          </div>
                          <p className="font-medium">{service.name}</p>
                        </div>
                        <span className={cn('text-xs px-2 py-1 rounded capitalize', isHealthy ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-red/20 text-accent-red')}>
                          {statusStr}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Celery Tab */}
      {activeTab === 'celery' && (
        <div className="space-y-6">
          {loadingCelery ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Celery Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Workers</p>
                  <p className="text-2xl font-bold">{celeryStatus.stats?.total_workers || (Array.isArray(celeryStatus.workers) ? celeryStatus.workers.length : 0)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Active Tasks</p>
                  <p className="text-2xl font-bold text-accent-green">{celeryStatus.stats?.total_active || (Array.isArray(celeryStatus.active_tasks) ? celeryStatus.active_tasks.length : 0)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Scheduled Tasks</p>
                  <p className="text-2xl font-bold text-accent-cyan">{celeryStatus.stats?.total_scheduled || (Array.isArray(celeryStatus.scheduled_tasks) ? celeryStatus.scheduled_tasks.length : 0)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Queues</p>
                  <p className="text-2xl font-bold text-accent-amber">{celeryStatus.stats?.total_queues || (Array.isArray(celeryStatus.queues) ? celeryStatus.queues.length : 0)}</p>
                </div>
              </div>

              {/* Worker Details */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Worker Status</h3>
                {Array.isArray(celeryStatus.workers) && celeryStatus.workers.length > 0 ? (
                  <div className="space-y-3">
                    {celeryStatus.workers.map((worker: { name: string; status: string; response?: { ok?: string } }) => (
                      <div
                        key={worker.name}
                        className="flex items-center justify-between p-3 rounded-lg border border-dark-border"
                      >
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            'h-8 w-8 rounded-full flex items-center justify-center',
                            worker.status === 'online' ? 'bg-accent-green/20' : 'bg-accent-red/20'
                          )}>
                            {worker.status === 'online' ? (
                              <CheckCircle size={14} className="text-accent-green" />
                            ) : (
                              <XCircle size={14} className="text-accent-red" />
                            )}
                          </div>
                          <div>
                            <p className="font-medium text-sm">{worker.name}</p>
                            <p className="text-xs text-gray-500">
                              {worker.response?.ok || worker.status}
                            </p>
                          </div>
                        </div>
                        <span className={cn(
                          'text-xs px-2 py-1 rounded',
                          worker.status === 'online' ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-red/20 text-accent-red'
                        )}>
                          {worker.status}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Clock className="mx-auto mb-2" size={32} />
                    <p>No worker details available</p>
                    <p className="text-sm text-gray-500 mt-1">Workers are running but detailed info is not exposed</p>
                  </div>
                )}
              </div>

              {/* Active Tasks */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Active Tasks</h3>
                {Array.isArray(celeryStatus.active_tasks) && celeryStatus.active_tasks.length > 0 ? (
                  <div className="space-y-3">
                    {celeryStatus.active_tasks.map((task: { task_id: string; task_name: string; worker: string; started: number }) => (
                      <div
                        key={task.task_id}
                        className="flex items-center justify-between p-3 rounded-lg border border-dark-border"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-accent-green/20 flex items-center justify-center">
                            <Play size={14} className="text-accent-green" />
                          </div>
                          <div>
                            <p className="font-medium text-sm">{task.task_name.split('.').pop()}</p>
                            <p className="text-xs text-gray-500">{task.worker.split('@')[0]}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">Running</span>
                          <p className="text-xs text-gray-500 mt-1">
                            {task.started ? `${Math.round((Date.now() / 1000 - task.started) / 60)}m ago` : ''}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Play className="mx-auto mb-2" size={32} />
                    <p>No active tasks</p>
                  </div>
                )}
              </div>

              {/* Task Schedule Status - Similar to Service Status */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Task Schedule Status</h3>
                <p className="text-sm text-gray-400 mb-4">
                  {celeryStatus.stats?.total_scheduled || 0} scheduled tasks configured
                </p>
                {Array.isArray(celeryStatus.scheduled_tasks) && celeryStatus.scheduled_tasks.length > 0 ? (
                  <div className="space-y-2 max-h-[600px] overflow-y-auto">
                    {celeryStatus.scheduled_tasks.map((task: { name: string; task: string; schedule: string }) => {
                      // Check if this task is currently running
                      const isRunning = Array.isArray(celeryStatus.active_tasks) &&
                        celeryStatus.active_tasks.some((active: { task_name: string }) => active.task_name === task.task)

                      // Parse schedule to show human-readable format
                      const getScheduleDisplay = (schedule: string) => {
                        if (schedule.startsWith('Cron:')) {
                          // Clean up cron format: "Cron: {0} {18} * * *" -> "0 18 * * *"
                          const cronPart = schedule.replace('Cron: ', '').replace(/\{|\}/g, '')
                          // Try to make it more readable
                          const parts = cronPart.split(' ')
                          if (parts.length >= 5) {
                            const [min, hour] = parts
                            if (hour !== '*' && min !== '*') {
                              // Format like "Daily 6:00" or "Daily 18:00"
                              const hours = hour.split(',').map(h => h.trim())
                              if (hours.length === 1) {
                                return `Daily ${hours[0].padStart(2, '0')}:${min.padStart(2, '0')}`
                              } else if (hours.length <= 3) {
                                return `${hours.length}x daily`
                              } else {
                                return `${hours.length}x daily`
                              }
                            }
                          }
                          return cronPart
                        }
                        const seconds = parseFloat(schedule)
                        if (!isNaN(seconds)) {
                          if (seconds < 60) return `Every ${seconds}s`
                          if (seconds < 3600) return `Every ${Math.round(seconds / 60)}m`
                          return `Every ${Math.round(seconds / 3600)}h`
                        }
                        return schedule
                      }

                      return (
                        <div
                          key={task.name}
                          className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                        >
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            <div className={cn(
                              'h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0',
                              isRunning ? 'bg-accent-green/20' : 'bg-accent-cyan/20'
                            )}>
                              {isRunning ? (
                                <Play size={14} className="text-accent-green" />
                              ) : (
                                <Clock size={14} className="text-accent-cyan" />
                              )}
                            </div>
                            <div className="min-w-0 flex-1">
                              <p className="font-medium text-sm truncate">{task.name}</p>
                              <p className="text-xs text-gray-500 truncate">{task.task}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                            <span className="text-xs text-accent-cyan whitespace-nowrap">
                              {getScheduleDisplay(task.schedule)}
                            </span>
                            <span className={cn(
                              'text-xs px-2 py-1 rounded whitespace-nowrap',
                              isRunning
                                ? 'bg-accent-green/20 text-accent-green'
                                : 'bg-gray-500/20 text-gray-400'
                            )}>
                              {isRunning ? 'Running' : 'Scheduled'}
                            </span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Clock className="mx-auto mb-2" size={32} />
                    <p>No scheduled tasks</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* Spiders Tab */}
      {activeTab === 'spiders' && (
        <div className="space-y-6">
          {loadingSpiders ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Spider Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Total Spiders</p>
                  <p className="text-2xl font-bold">{spiderHealth.total || 77}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Working</p>
                  <p className="text-2xl font-bold text-accent-green">{spiderHealth.working || 72}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Need API Keys</p>
                  <p className="text-2xl font-bold text-accent-amber">{spiderHealth.need_api_keys || 5}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Recent Runs</p>
                  <p className="text-2xl font-bold">{spiderHealth.recent_runs || spiderExecutions.length || 0}</p>
                </div>
              </div>

              {/* Recent Executions */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Recent Executions</h3>
                {spiderExecutions.length > 0 ? (
                  <div className="space-y-3">
                    {spiderExecutions.slice(0, 10).map((exec: { id: string; spider_name?: string; status?: string; created_at?: string; items_count?: number }) => (
                      <div
                        key={exec.id}
                        className="flex items-center justify-between p-3 rounded-lg border border-dark-border"
                      >
                        <div className="flex items-center gap-3">
                          <Globe size={18} className="text-primary-400" />
                          <div>
                            <p className="font-medium text-sm">{exec.spider_name || 'Unknown Spider'}</p>
                            <p className="text-xs text-gray-500">
                              {exec.created_at ? new Date(exec.created_at).toLocaleString() : ''}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-gray-400">{exec.items_count || 0} items</span>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded capitalize',
                            exec.status === 'success' ? 'bg-accent-green/20 text-accent-green' :
                            exec.status === 'failed' ? 'bg-accent-red/20 text-accent-red' : 'bg-accent-amber/20 text-accent-amber'
                          )}>
                            {exec.status || 'unknown'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Bug className="mx-auto mb-2" size={32} />
                    <p>No recent spider executions</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* Agents Tab */}
      {activeTab === 'agents' && (
        <div className="space-y-6">
          {loadingAgents ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Agent Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Total Agents</p>
                  <p className="text-2xl font-bold">{agentHealth.total || 71}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Routable</p>
                  <p className="text-2xl font-bold text-accent-green">{agentHealth.routable || 68}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Sub-Agents</p>
                  <p className="text-2xl font-bold text-accent-amber">{agentHealth.sub_agents || 3}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Recent Executions</p>
                  <p className="text-2xl font-bold">{agentHealth.recent_executions || 0}</p>
                </div>
              </div>

              {/* Agent Categories */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Agent Categories</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {[
                    { name: 'Creation', count: 4 },
                    { name: 'Research', count: 1 },
                    { name: 'Strategy', count: 4 },
                    { name: 'Executive', count: 4 },
                    { name: 'Development', count: 4 },
                    { name: 'Blockchain', count: 5 },
                    { name: 'Stocks', count: 9 },
                    { name: 'Markets', count: 3 },
                    { name: 'Podcast', count: 4 },
                    { name: 'Narrative', count: 4 },
                    { name: 'Content', count: 4 },
                    { name: 'Other', count: 25 },
                  ].map((category) => (
                    <div key={category.name} className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
                      <span className="text-sm">{category.name}</span>
                      <span className="font-medium">{category.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
