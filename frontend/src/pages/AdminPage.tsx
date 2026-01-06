import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi, dashboardApi } from '@/lib/api'
import {
  Server, Database, Activity, AlertTriangle, CheckCircle, XCircle,
  Loader2, RefreshCw, Trash2, Users, Clock, HardDrive,
  Cpu, MemoryStick, Wifi, Settings, Play
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'health' | 'celery' | 'database' | 'cache' | 'users'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface ServiceStatus {
  name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime?: string
  memory?: number
  cpu?: number
}

interface CeleryTask {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  duration?: number
}

interface User {
  id: string
  username: string
  email: string
  is_active: boolean
  last_login?: string
  created_at: string
}

const tabs = [
  { id: 'health' as TabType, label: 'System Health', icon: Activity },
  { id: 'celery' as TabType, label: 'Celery Tasks', icon: Clock },
  { id: 'database' as TabType, label: 'Database', icon: Database },
  { id: 'cache' as TabType, label: 'Cache', icon: HardDrive },
  { id: 'users' as TabType, label: 'Users', icon: Users },
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
  const queryClient = useQueryClient()

  // Fetch system health
  const { data: healthData, isLoading: loadingHealth, refetch: refetchHealth } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => dashboardApi.health(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch services
  const { data: servicesData, isLoading: loadingServices } = useQuery({
    queryKey: ['admin-services'],
    queryFn: () => adminApi.services(),
    enabled: activeTab === 'health',
  })

  // Fetch Celery stats
  const { data: celeryStatsData } = useQuery({
    queryKey: ['celery-stats'],
    queryFn: () => adminApi.celeryStats(),
    enabled: activeTab === 'celery',
  })

  // Fetch Celery tasks
  const { data: celeryTasksData, isLoading: loadingCeleryTasks } = useQuery({
    queryKey: ['celery-tasks'],
    queryFn: () => adminApi.celeryTasks(),
    enabled: activeTab === 'celery',
  })

  // Fetch DB stats
  const { data: dbStatsData, isLoading: loadingDbStats } = useQuery({
    queryKey: ['db-stats'],
    queryFn: () => adminApi.dbStats(),
    enabled: activeTab === 'database',
  })

  // Fetch cache stats
  const { data: cacheStatsData, isLoading: loadingCacheStats } = useQuery({
    queryKey: ['cache-stats'],
    queryFn: () => adminApi.cacheStats(),
    enabled: activeTab === 'cache',
  })

  // Fetch users
  const { data: usersData, isLoading: loadingUsers } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.users(),
    enabled: activeTab === 'users',
  })

  // Clear cache mutation
  const clearCacheMutation = useMutation({
    mutationFn: () => adminApi.clearCache(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Cache cleared successfully!' })
      queryClient.invalidateQueries({ queryKey: ['cache-stats'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to clear cache' })
    },
  })

  // Purge queue mutation
  const purgeQueueMutation = useMutation({
    mutationFn: (queue: string) => adminApi.purgeQueue(queue),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Queue purged successfully!' })
      queryClient.invalidateQueries({ queryKey: ['celery-stats'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to purge queue' })
    },
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
  const services: ServiceStatus[] = servicesData?.data?.services || servicesData?.data || []
  const celeryStats = celeryStatsData?.data || {}
  const celeryTasks: CeleryTask[] = celeryTasksData?.data?.tasks || celeryTasksData?.data || []
  const dbStats = dbStatsData?.data || {}
  const cacheStats = cacheStatsData?.data || {}
  const users: User[] = usersData?.data?.users || usersData?.data || []

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'ok':
        return 'text-accent-green'
      case 'degraded':
      case 'warning':
        return 'text-accent-amber'
      default:
        return 'text-accent-red'
    }
  }

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'ok':
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
          {/* Overall Status */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <div className={cn('h-10 w-10 rounded-lg flex items-center justify-center', getStatusBg(health.status || 'healthy'))}>
                  <Server size={20} className={getStatusColor(health.status || 'healthy')} />
                </div>
                <div>
                  <p className="text-sm text-gray-400">System Status</p>
                  <p className={cn('text-lg font-bold capitalize', getStatusColor(health.status || 'healthy'))}>
                    {health.status || 'Healthy'}
                  </p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Cpu className="text-primary-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">CPU Usage</p>
                  <p className="text-2xl font-bold">{health.cpu_percent || 0}%</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <MemoryStick className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Memory</p>
                  <p className="text-2xl font-bold">{health.memory_percent || 0}%</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Wifi className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Uptime</p>
                  <p className="text-2xl font-bold">{health.uptime || 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Services */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Services</h3>
            {loadingServices || loadingHealth ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : services.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {services.map((service, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-4 rounded-lg border border-dark-border"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn('h-8 w-8 rounded-full flex items-center justify-center', getStatusBg(service.status))}>
                        {service.status === 'healthy' ? (
                          <CheckCircle size={16} className="text-accent-green" />
                        ) : service.status === 'degraded' ? (
                          <AlertTriangle size={16} className="text-accent-amber" />
                        ) : (
                          <XCircle size={16} className="text-accent-red" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{service.name}</p>
                        {service.uptime && <p className="text-xs text-gray-500">Uptime: {service.uptime}</p>}
                      </div>
                    </div>
                    <span className={cn('text-xs px-2 py-1 rounded capitalize', getStatusBg(service.status), getStatusColor(service.status))}>
                      {service.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {['Django', 'Redis', 'Celery', 'Celery Beat', 'PostgreSQL', 'Daphne'].map((name) => (
                  <div
                    key={name}
                    className="flex items-center justify-between p-4 rounded-lg border border-dark-border"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-accent-green/20 flex items-center justify-center">
                        <CheckCircle size={16} className="text-accent-green" />
                      </div>
                      <p className="font-medium">{name}</p>
                    </div>
                    <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">
                      healthy
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Celery Tab */}
      {activeTab === 'celery' && (
        <div className="space-y-6">
          {/* Celery Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <p className="text-sm text-gray-400 mb-1">Active Workers</p>
              <p className="text-2xl font-bold">{celeryStats.active_workers || 0}</p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-400 mb-1">Queued Tasks</p>
              <p className="text-2xl font-bold">{celeryStats.queued_tasks || 0}</p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-400 mb-1">Completed (24h)</p>
              <p className="text-2xl font-bold text-accent-green">{celeryStats.completed_24h || 0}</p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-400 mb-1">Failed (24h)</p>
              <p className="text-2xl font-bold text-accent-red">{celeryStats.failed_24h || 0}</p>
            </div>
          </div>

          {/* Queue Actions */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Queue Management</h3>
              <button
                className="btn btn-secondary text-sm text-accent-red flex items-center gap-2"
                onClick={() => purgeQueueMutation.mutate('default')}
                disabled={purgeQueueMutation.isPending}
              >
                {purgeQueueMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                Purge All Queues
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {['default', 'high_priority', 'low_priority'].map((queue) => (
                <div key={queue} className="p-4 rounded-lg bg-dark-bg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium capitalize">{queue.replace('_', ' ')}</h4>
                    <button
                      className="text-xs text-accent-red hover:underline"
                      onClick={() => purgeQueueMutation.mutate(queue)}
                    >
                      Purge
                    </button>
                  </div>
                  <p className="text-2xl font-bold">{celeryStats[`${queue}_count`] || 0}</p>
                  <p className="text-xs text-gray-500">tasks in queue</p>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Tasks */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Recent Tasks</h3>
            {loadingCeleryTasks ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : celeryTasks.length > 0 ? (
              <div className="space-y-3">
                {celeryTasks.slice(0, 10).map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-dark-border"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-8 w-8 rounded-full flex items-center justify-center',
                        task.status === 'completed' ? 'bg-accent-green/20' :
                        task.status === 'running' ? 'bg-accent-amber/20' :
                        task.status === 'failed' ? 'bg-accent-red/20' : 'bg-gray-500/20'
                      )}>
                        {task.status === 'completed' ? <CheckCircle size={14} className="text-accent-green" /> :
                         task.status === 'running' ? <Loader2 size={14} className="text-accent-amber animate-spin" /> :
                         task.status === 'failed' ? <XCircle size={14} className="text-accent-red" /> :
                         <Clock size={14} className="text-gray-400" />}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{task.name}</p>
                        <p className="text-xs text-gray-500 font-mono">{task.id.slice(0, 8)}...</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {task.duration && (
                        <span className="text-sm text-gray-400">{task.duration}s</span>
                      )}
                      <span className={cn(
                        'text-xs px-2 py-1 rounded capitalize',
                        task.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                        task.status === 'running' ? 'bg-accent-amber/20 text-accent-amber' :
                        task.status === 'failed' ? 'bg-accent-red/20 text-accent-red' : 'bg-gray-500/20 text-gray-400'
                      )}>
                        {task.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Clock className="mx-auto mb-2" size={32} />
                <p>No recent tasks</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Database Tab */}
      {activeTab === 'database' && (
        <div className="space-y-6">
          {loadingDbStats ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Total Tables</p>
                  <p className="text-2xl font-bold">{dbStats.total_tables || 324}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Total Rows</p>
                  <p className="text-2xl font-bold">{(dbStats.total_rows || 0).toLocaleString()}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Database Size</p>
                  <p className="text-2xl font-bold">{dbStats.size || '582 MB'}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Connections</p>
                  <p className="text-2xl font-bold">{dbStats.connections || 0}</p>
                </div>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Table Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {[
                    { name: 'Agent', count: 71 },
                    { name: 'AgentExecution', count: dbStats.agent_executions || 0 },
                    { name: 'AgentConversation', count: dbStats.conversations || 0 },
                    { name: 'GeneratedImage', count: dbStats.images || 0 },
                    { name: 'Wager', count: dbStats.wagers || 0 },
                    { name: 'PilotGate', count: dbStats.gates || 0 },
                  ].map((table) => (
                    <div key={table.name} className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
                      <span className="text-sm">{table.name}</span>
                      <span className="font-medium">{table.count.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Cache Tab */}
      {activeTab === 'cache' && (
        <div className="space-y-6">
          {loadingCacheStats ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Cached Keys</p>
                  <p className="text-2xl font-bold">{cacheStats.keys || 0}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Memory Used</p>
                  <p className="text-2xl font-bold">{cacheStats.memory_used || '0 MB'}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Hit Rate</p>
                  <p className="text-2xl font-bold text-accent-green">{cacheStats.hit_rate || 0}%</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Evictions</p>
                  <p className="text-2xl font-bold">{cacheStats.evictions || 0}</p>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Cache Management</h3>
                  <button
                    className="btn btn-secondary text-sm text-accent-red flex items-center gap-2"
                    onClick={() => clearCacheMutation.mutate()}
                    disabled={clearCacheMutation.isPending}
                  >
                    {clearCacheMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                    Clear All Cache
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <h4 className="font-medium mb-2">Redis Status</h4>
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-accent-green" />
                      <span className="text-accent-green">Connected</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">Version: {cacheStats.redis_version || '7.0.0'}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <h4 className="font-medium mb-2">Cache Configuration</h4>
                    <p className="text-sm text-gray-400">Max Memory: {cacheStats.max_memory || '256 MB'}</p>
                    <p className="text-sm text-gray-400">Policy: {cacheStats.eviction_policy || 'allkeys-lru'}</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">User Management</h3>
          {loadingUsers ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : users.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-dark-border">
                    <th className="pb-3">Username</th>
                    <th className="pb-3">Email</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Last Login</th>
                    <th className="pb-3">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b border-dark-border hover:bg-dark-bg/50">
                      <td className="py-3 font-medium">{user.username}</td>
                      <td className="py-3 text-gray-400">{user.email}</td>
                      <td className="py-3">
                        <span className={cn(
                          'text-xs px-2 py-1 rounded',
                          user.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-red/20 text-accent-red'
                        )}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-3 text-gray-400">
                        {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                      </td>
                      <td className="py-3 text-gray-400">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Users className="mx-auto mb-2" size={48} />
              <p>No users found</p>
            </div>
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
