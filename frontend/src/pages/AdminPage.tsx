import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
// Session 712: Removed unused body system APIs (lungsApi, circulatoryApi, spineApi, immuneApi, digestiveApi, muscularApi)
import { adminApi, dashboardApi, heartApi, bodyApi } from '@/lib/api'
// Session 712: Cleaned up unused icon imports after removing body system tabs
import {
  Server, Activity, CheckCircle, XCircle,
  Loader2, RefreshCw, Settings, Play, Bug, Bot, Clock, Globe,
  Heart, Wind, Bone, Shield, Utensils, Dumbbell, Droplets, ExternalLink,
  CreditCard, BarChart3
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Session 712: Simplified tab types after removing redundant body system tabs
// Session 1007: Added billing + analytics tabs
type TabType = 'heart' | 'health' | 'celery' | 'spiders' | 'agents' | 'billing' | 'analytics'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

// Session 712: Removed redundant body system tabs (LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR)
// These are now shown in the unified Body Systems Status on the HEART tab and the Body Health page
const tabs = [
  { id: 'heart' as TabType, label: 'Body Health', icon: Heart },
  { id: 'health' as TabType, label: 'Services', icon: Activity },
  { id: 'celery' as TabType, label: 'Celery', icon: Clock },
  { id: 'spiders' as TabType, label: 'Spiders', icon: Bug },
  { id: 'agents' as TabType, label: 'Agents', icon: Bot },
  { id: 'billing' as TabType, label: 'Billing', icon: CreditCard },
  { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
]

// Session 712: Updated to actual 7 body systems
const BODY_SYSTEMS = {
  heart: { icon: Heart, label: 'HEART', description: 'Health monitoring & heartbeat', emoji: '❤️' },
  lungs: { icon: Wind, label: 'LUNGS', description: 'Resource & budget management', emoji: '🫁' },
  circulatory: { icon: Droplets, label: 'CIRCULATORY', description: 'Data flow & pipelines', emoji: '🩸' },
  spine: { icon: Bone, label: 'SPINE', description: 'Central API routing', emoji: '🦴' },
  immune: { icon: Shield, label: 'IMMUNE', description: 'Security & threat detection', emoji: '🛡️' },
  digestive: { icon: Utensils, label: 'DIGESTIVE', description: 'Data ingestion & processing', emoji: '🍽️' },
  muscular: { icon: Dumbbell, label: 'MUSCULAR', description: 'Agent work execution', emoji: '💪' },
} as const

// Session 712: Healthy status values for each system
const HEALTHY_STATUSES: Record<string, string[]> = {
  heart: ['healthy'],
  lungs: ['healthy', 'normal', 'optimal'],
  circulatory: ['flowing', 'healthy'],
  spine: ['aligned', 'healthy'],
  immune: ['healthy', 'protected'],
  digestive: ['healthy', 'processing', 'digesting'],
  muscular: ['strong', 'fit', 'healthy'],
}

// Helper to determine if a system is healthy
function isSystemHealthy(system: string, status?: { status?: string; score?: number }): boolean {
  if (!status) return false
  const healthyStatuses = HEALTHY_STATUSES[system] || ['healthy']
  return healthyStatuses.includes(status.status || '') || (status.score !== undefined && status.score >= 80)
}

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
  const [activeTab, setActiveTab] = useState<TabType>('heart')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)

  // HEART Service queries (Session 702)
  const { data: heartStatusData, isLoading: loadingHeart } = useQuery({
    queryKey: ['heart-status'],
    queryFn: () => heartApi.status(),
    refetchInterval: 30000,
    enabled: activeTab === 'heart',
  })

  const { data: heartHistoryData } = useQuery({
    queryKey: ['heart-history'],
    queryFn: () => heartApi.history(24, 50),
    enabled: activeTab === 'heart',
  })

  // Session 712: Body vitals query for unified body systems view
  const { data: bodyVitalsData, refetch: refetchBodyVitals } = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 30000,
    enabled: activeTab === 'heart',
  })

  // Session 712: Removed redundant body system queries (LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR)
  // These are now handled by the unified bodyApi.vitals() query above
  // Individual system details are available on the Body Health page (/body-health)

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

  // Fetch agent stats (detailed)
  const { data: agentStatsData } = useQuery({
    queryKey: ['agent-stats'],
    queryFn: () => adminApi.agentStats(),
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

  // HEART data (Session 702)
  const heartStatus = heartStatusData?.data || {}
  const heartHistory = heartHistoryData?.data?.heartbeats || []
  const heartComponents = heartStatus.components || {}

  // Session 712: Body vitals data for unified view
  const bodyVitals = bodyVitalsData?.data || { systems: {}, health_score: 0, overall_health: 'unknown' }
  const bodySystems = bodyVitals.systems || {}

  // Session 712: Removed data extraction for LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE
  // These are now accessed via the unified bodyVitals query above
  // Individual system details are available on the Body Health page (/body-health)

  const health = healthData?.data || {}
  const healthServices = health.services || {}
  const systemHealth = systemHealthData?.data || {}
  const celeryStatus = celeryStatusData?.data || {}
  const celeryStats = celeryStatsData?.data || {}
  const spiderHealth = spiderHealthData?.data || {}
  const spiderExecutions = spiderExecutionsData?.data?.logs || spiderExecutionsData?.data?.executions || spiderExecutionsData?.data || []
  const spiderStatusSummary = spiderExecutionsData?.data?.status_summary || {}
  const agentHealth = agentHealthData?.data || {}
  const agentStats = agentStatsData?.data || {}
  const coreAgents = agentStats.core_agents || []
  const agentCategories = agentStats.by_category || {}
  const recentAgentActivity = agentStats.recent_activity || []

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  // Session 712: Updated to handle all body system status values
  const HEALTHY_STATUS_VALUES = ['healthy', 'ok', 'running', 'active', 'normal', 'optimal', 'flowing', 'aligned', 'protected', 'strong', 'fit', 'processing', 'digesting']
  const DEGRADED_STATUS_VALUES = ['degraded', 'warning', 'sluggish', 'slow', 'depleted', 'fatigued']

  const getStatusColor = (status: string) => {
    const s = status?.toLowerCase() || ''
    if (HEALTHY_STATUS_VALUES.includes(s)) return 'text-accent-green'
    if (DEGRADED_STATUS_VALUES.includes(s)) return 'text-accent-amber'
    return 'text-accent-red'
  }

  const getStatusBg = (status: string) => {
    const s = status?.toLowerCase() || ''
    if (HEALTHY_STATUS_VALUES.includes(s)) return 'bg-accent-green/20'
    if (DEGRADED_STATUS_VALUES.includes(s)) return 'bg-accent-amber/20'
    return 'bg-accent-red/20'
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

      {/* HEART Tab - Session 702 */}
      {activeTab === 'heart' && (
        <div className="space-y-6">
          {loadingHeart ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Overall Health Status */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className={cn('h-12 w-12 rounded-lg flex items-center justify-center', getStatusBg(heartStatus.overall_status || 'unknown'))}>
                      <Heart size={24} className={cn(getStatusColor(heartStatus.overall_status || 'unknown'), 'animate-pulse')} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Health Score</p>
                      <p className={cn('text-2xl font-bold', getStatusColor(heartStatus.overall_status || 'unknown'))}>
                        {(heartStatus.health_score || 0).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Activity className="text-accent-cyan" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Status</p>
                      <p className={cn('text-lg font-bold capitalize', getStatusColor(heartStatus.overall_status || 'unknown'))}>
                        {heartStatus.overall_status || 'Unknown'}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="text-accent-green" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Components</p>
                      <p className="text-2xl font-bold">
                        {Object.values(heartComponents as Record<string, { is_healthy?: boolean }>).filter((c) => c?.is_healthy).length}/
                        {Object.keys(heartComponents).length}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Clock className="text-accent-amber" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Last Check</p>
                      <p className="text-sm font-medium">
                        {heartStatus.last_check ? new Date(heartStatus.last_check).toLocaleTimeString() : 'Never'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Session 712: Body Systems Grid - Updated to use 7 real body systems */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">Body Systems Status</h3>
                    <span className={cn(
                      'text-sm font-bold px-2 py-0.5 rounded',
                      bodyVitals.health_score >= 80 ? 'bg-accent-green/20 text-accent-green' :
                      bodyVitals.health_score >= 50 ? 'bg-accent-amber/20 text-accent-amber' :
                      'bg-accent-red/20 text-accent-red'
                    )}>
                      {(bodyVitals.health_score || 0).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <a
                      href="/workspace?tab=system"
                      className="btn btn-secondary btn-sm flex items-center gap-2"
                    >
                      <ExternalLink size={14} />
                      Full Details
                    </a>
                    <button
                      onClick={() => refetchBodyVitals()}
                      className="btn btn-secondary btn-sm flex items-center gap-2"
                    >
                      <RefreshCw size={14} />
                      Refresh
                    </button>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {(Object.keys(BODY_SYSTEMS) as Array<keyof typeof BODY_SYSTEMS>).map((systemKey) => {
                    const system = BODY_SYSTEMS[systemKey]
                    const status = bodySystems[systemKey] || {}
                    const Icon = system.icon
                    const isHealthy = isSystemHealthy(systemKey, status)
                    const systemStatus = status.status || 'unknown'
                    const score = status.score || 0

                    return (
                      <div
                        key={systemKey}
                        className={cn(
                          'p-4 rounded-lg border transition-colors',
                          getStatusBg(systemStatus),
                          isHealthy ? 'border-accent-green/30' : 'border-accent-red/30'
                        )}
                      >
                        <div className="flex items-start gap-3">
                          <div className={cn('h-12 w-12 rounded-lg flex items-center justify-center flex-shrink-0', getStatusBg(systemStatus))}>
                            <Icon size={24} className={getStatusColor(systemStatus)} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-lg">{system.emoji}</span>
                              <p className="font-semibold">{system.label}</p>
                              {isHealthy && <CheckCircle size={14} className="text-accent-green" />}
                              {!isHealthy && <XCircle size={14} className="text-accent-red" />}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">{system.description}</p>
                            <div className="flex items-center justify-between mt-2">
                              <span className={cn('text-sm font-medium capitalize', getStatusColor(systemStatus))}>
                                {systemStatus}
                              </span>
                              <span className={cn('text-sm font-bold', getStatusColor(systemStatus))}>
                                {(score ?? 0).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Heartbeat History */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Heartbeat History (24h)</h3>
                {heartHistory.length > 0 ? (
                  <div className="space-y-2 max-h-[400px] overflow-y-auto">
                    {heartHistory.slice(0, 20).map((beat: { id: string; health_score: number; overall_status: string; recorded_at: string; check_duration_ms: number; components_healthy: number; components_checked: number }, idx: number) => (
                      <div
                        key={beat.id || idx}
                        className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className={cn('h-8 w-8 rounded-full flex items-center justify-center', getStatusBg(beat.overall_status))}>
                            <Heart size={14} className={getStatusColor(beat.overall_status)} />
                          </div>
                          <div>
                            <p className="font-medium text-sm">
                              {(beat.health_score ?? 0).toFixed(0)}% - {beat.components_healthy}/{beat.components_checked} healthy
                            </p>
                            <p className="text-xs text-gray-500">
                              {new Date(beat.recorded_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">{beat.check_duration_ms}ms</span>
                          <span className={cn('text-xs px-2 py-1 rounded capitalize', getStatusBg(beat.overall_status), getStatusColor(beat.overall_status))}>
                            {beat.overall_status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Heart className="mx-auto mb-2" size={32} />
                    <p>No heartbeat history yet</p>
                    <p className="text-sm text-gray-500 mt-1">Heartbeats are recorded every 60 seconds</p>
                  </div>
                )}
              </div>

              {/* Session 712: Human Body Architecture - Updated to 7 real systems */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Human Body Architecture</h3>
                <p className="text-sm text-gray-400 mb-4">
                  The platform uses the human body as an architectural metaphor. Each body system has specific responsibilities:
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-dark-border">
                        <th className="text-left py-2 px-3 text-gray-400">System</th>
                        <th className="text-left py-2 px-3 text-gray-400">Purpose</th>
                        <th className="text-center py-2 px-3 text-gray-400">Score</th>
                        <th className="text-center py-2 px-3 text-gray-400">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-dark-border/50">
                        <td className="py-2 px-3 font-medium">🧠 Consciousness</td>
                        <td className="py-2 px-3 text-gray-400">Human Operator - Final decisions & approvals</td>
                        <td className="py-2 px-3 text-center">—</td>
                        <td className="py-2 px-3 text-center"><span className="text-accent-green">Active</span></td>
                      </tr>
                      {(Object.keys(BODY_SYSTEMS) as Array<keyof typeof BODY_SYSTEMS>).map((systemKey) => {
                        const system = BODY_SYSTEMS[systemKey]
                        const status = bodySystems[systemKey] || {}
                        const isHealthy = isSystemHealthy(systemKey, status)
                        return (
                          <tr key={systemKey} className="border-b border-dark-border/50">
                            <td className="py-2 px-3 font-medium">{system.emoji} {system.label}</td>
                            <td className="py-2 px-3 text-gray-400">{system.description}</td>
                            <td className="py-2 px-3 text-center">
                              <span className={cn(
                                'font-medium',
                                isHealthy ? 'text-accent-green' : 'text-accent-amber'
                              )}>
                                {(status.score || 0).toFixed(0)}%
                              </span>
                            </td>
                            <td className="py-2 px-3 text-center">
                              <span className={cn('px-2 py-0.5 rounded text-xs capitalize', getStatusBg(status.status || 'unknown'), getStatusColor(status.status || 'unknown'))}>
                                {status.status || 'unknown'}
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Session 712: Removed redundant body system tabs (LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR)
          These are now shown in the unified Body Systems Status on the HEART/Body Health tab above.
          For detailed system views, use the Body Health page (/body-health) */}

      {/* Services Tab (was System Health Tab) */}
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
                    {celeryStatus.active_tasks.map((task: { task_id: string; task_name: string | object; worker: string | object; started: number; args?: unknown }) => {
                      // Safely extract string values - API may return objects
                      const taskName = typeof task.task_name === 'string' ? task.task_name : String(task.task_name || 'Unknown')
                      const workerName = typeof task.worker === 'string' ? task.worker : String(task.worker || 'Unknown')
                      return (
                        <div
                          key={task.task_id}
                          className="flex items-center justify-between p-3 rounded-lg border border-dark-border"
                        >
                          <div className="flex items-center gap-3">
                            <div className="h-8 w-8 rounded-full bg-accent-green/20 flex items-center justify-center">
                              <Play size={14} className="text-accent-green" />
                            </div>
                            <div>
                              <p className="font-medium text-sm">{taskName.split('.').pop()}</p>
                              <p className="text-xs text-gray-500">{workerName.split('@')[0]}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">Running</span>
                            <p className="text-xs text-gray-500 mt-1">
                              {task.started ? `${Math.round((Date.now() / 1000 - task.started) / 60)}m ago` : ''}
                            </p>
                          </div>
                        </div>
                      )
                    })}
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
                    {celeryStatus.scheduled_tasks.map((task: { name: string | object; task: string | object; schedule: string | object }) => {
                      // Safely extract string values - API may return objects
                      const taskName = typeof task.name === 'string' ? task.name : String(task.name || 'Unknown')
                      const taskPath = typeof task.task === 'string' ? task.task : String(task.task || 'Unknown')
                      const taskSchedule = typeof task.schedule === 'string' ? task.schedule : String(task.schedule || '')

                      // Check if this task is currently running
                      const isRunning = Array.isArray(celeryStatus.active_tasks) &&
                        celeryStatus.active_tasks.some((active: { task_name: string | object }) => {
                          const activeName = typeof active.task_name === 'string' ? active.task_name : String(active.task_name || '')
                          return activeName === taskPath
                        })

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
                          key={taskName}
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
                              <p className="font-medium text-sm truncate">{taskName}</p>
                              <p className="text-xs text-gray-500 truncate">{taskPath}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                            <span className="text-xs text-accent-cyan whitespace-nowrap">
                              {getScheduleDisplay(taskSchedule)}
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
              {/* Spider Stats - Using real API data from /api/spider-health/summary/ */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Executions (24h)</p>
                  <p className="text-2xl font-bold">{spiderHealth.summary?.executions_24h || spiderHealth.executions_24h || 0}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Success Rate</p>
                  <p className="text-2xl font-bold text-accent-green">{(spiderHealth.summary?.success_rate_24h || spiderHealth.success_rate_24h || 0).toFixed(1)}%</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Data Collected (24h)</p>
                  <p className="text-2xl font-bold text-accent-cyan">{spiderHealth.summary?.data_collected_24h || spiderHealth.data_collected_24h || 0}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Embedding Coverage</p>
                  <p className="text-2xl font-bold text-accent-amber">{(spiderHealth.summary?.embedding_coverage || spiderHealth.embedding_coverage || 0).toFixed(1)}%</p>
                </div>
              </div>

              {/* Error Stats */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Errors (24h)</p>
                  <p className="text-2xl font-bold text-accent-red">{spiderHealth.summary?.errors_24h || spiderHealth.errors_24h || 0}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Data Collected (7d)</p>
                  <p className="text-2xl font-bold">{spiderHealth.summary?.data_collected_7d || spiderHealth.data_collected_7d || 0}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Total Spiders</p>
                  <p className="text-2xl font-bold">77</p>
                </div>
              </div>

              {/* Status Summary */}
              {Object.keys(spiderStatusSummary).length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Execution Status (24h)</h3>
                  <div className="flex flex-wrap gap-3">
                    {Object.entries(spiderStatusSummary).map(([status, count]) => (
                      <div key={status} className={cn(
                        'px-4 py-2 rounded-lg',
                        status === 'success' ? 'bg-accent-green/20' :
                        status === 'partial' ? 'bg-accent-amber/20' :
                        status === 'failed' || status === 'error' ? 'bg-accent-red/20' : 'bg-gray-500/20'
                      )}>
                        <p className={cn(
                          'text-xl font-bold',
                          status === 'success' ? 'text-accent-green' :
                          status === 'partial' ? 'text-accent-amber' :
                          status === 'failed' || status === 'error' ? 'text-accent-red' : 'text-gray-400'
                        )}>{count as number}</p>
                        <p className="text-xs text-gray-400 capitalize">{status}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Executions */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Recent Executions</h3>
                {spiderExecutions.length > 0 ? (
                  <div className="space-y-3 max-h-[500px] overflow-y-auto">
                    {spiderExecutions.slice(0, 15).map((exec: { id: string; spider_name?: string; category?: string; status?: string; started_at?: string; completed_at?: string; items_collected?: number; duration_seconds?: number; triggered_by?: string }) => (
                      <div
                        key={exec.id}
                        className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <Globe size={18} className="text-primary-400 flex-shrink-0" />
                          <div className="min-w-0">
                            <p className="font-medium text-sm truncate">{exec.spider_name || 'Unknown Spider'}</p>
                            <p className="text-xs text-gray-500">
                              {exec.category && <span className="text-accent-cyan">{exec.category}</span>}
                              {exec.category && exec.started_at && ' • '}
                              {exec.started_at ? new Date(exec.started_at).toLocaleString() : ''}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 flex-shrink-0">
                          <div className="text-right">
                            <p className="text-sm font-medium">{exec.items_collected || 0} items</p>
                            {exec.duration_seconds && (
                              <p className="text-xs text-gray-500">{(exec.duration_seconds ?? 0).toFixed(1)}s</p>
                            )}
                          </div>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded capitalize whitespace-nowrap',
                            exec.status === 'success' ? 'bg-accent-green/20 text-accent-green' :
                            exec.status === 'partial' ? 'bg-accent-amber/20 text-accent-amber' :
                            exec.status === 'failed' || exec.status === 'error' ? 'bg-accent-red/20 text-accent-red' : 'bg-gray-500/20 text-gray-400'
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
                  <p className="text-2xl font-bold">{agentStats.total_agents || 72}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Active</p>
                  <p className="text-2xl font-bold text-accent-green">
                    {coreAgents.filter((a: { is_active?: boolean }) => a.is_active).length || agentHealth.active_agents || 0}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Total Executions</p>
                  <p className="text-2xl font-bold text-accent-cyan">
                    {coreAgents.reduce((sum: number, a: { total_executions?: number }) => sum + (a.total_executions || 0), 0)}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Avg Success Rate</p>
                  <p className="text-2xl font-bold text-accent-amber">
                    {coreAgents.length > 0
                      ? (coreAgents.filter((a: { total_executions?: number }) => a.total_executions && a.total_executions > 0)
                          .reduce((sum: number, a: { success_rate?: number }) => sum + (a.success_rate || 0), 0) /
                        (coreAgents.filter((a: { total_executions?: number }) => a.total_executions && a.total_executions > 0).length || 1)).toFixed(0)
                      : 0}%
                  </p>
                </div>
              </div>

              {/* Agent Categories from API */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Agent Categories</h3>
                {Object.keys(agentCategories).length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {Object.entries(agentCategories)
                      .sort((a, b) => (Array.isArray(b[1]) ? b[1].length : 0) - (Array.isArray(a[1]) ? a[1].length : 0))
                      .map(([category, agents]) => (
                        <div key={category} className="flex items-center justify-between p-3 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors">
                          <span className="text-sm capitalize">{category || 'Other'}</span>
                          <span className="font-medium text-primary-400">{Array.isArray(agents) ? agents.length : 0}</span>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {(() => {
                      // Group by type from coreAgents
                      const typeGroups: Record<string, number> = {}
                      coreAgents.forEach((a: { type?: string }) => {
                        const type = a.type || 'other'
                        typeGroups[type] = (typeGroups[type] || 0) + 1
                      })
                      return Object.entries(typeGroups)
                        .sort((a, b) => b[1] - a[1])
                        .map(([type, count]) => (
                          <div key={type} className="flex items-center justify-between p-3 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors">
                            <span className="text-sm capitalize">{type || 'Other'}</span>
                            <span className="font-medium text-primary-400">{count}</span>
                          </div>
                        ))
                    })()}
                  </div>
                )}
              </div>

              {/* Top Performing Agents */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Top Performing Agents</h3>
                {coreAgents.length > 0 ? (
                  <div className="space-y-3 max-h-[400px] overflow-y-auto">
                    {coreAgents
                      .filter((a: { total_executions?: number }) => a.total_executions && a.total_executions > 0)
                      .sort((a: { effectiveness_score?: number }, b: { effectiveness_score?: number }) =>
                        (b.effectiveness_score || 0) - (a.effectiveness_score || 0))
                      .slice(0, 10)
                      .map((agent: {
                        id: string
                        name: string
                        type?: string
                        effectiveness_score?: number
                        total_executions?: number
                        success_rate?: number
                        knowledge_count?: number
                      }) => (
                        <div
                          key={agent.id}
                          className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                        >
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            <div className={cn(
                              'h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0',
                              (agent.effectiveness_score || 0) >= 80 ? 'bg-accent-green/20' :
                              (agent.effectiveness_score || 0) >= 60 ? 'bg-accent-amber/20' : 'bg-gray-500/20'
                            )}>
                              <Bot size={18} className={cn(
                                (agent.effectiveness_score || 0) >= 80 ? 'text-accent-green' :
                                (agent.effectiveness_score || 0) >= 60 ? 'text-accent-amber' : 'text-gray-400'
                              )} />
                            </div>
                            <div className="min-w-0">
                              <p className="font-medium text-sm truncate">{agent.name}</p>
                              <p className="text-xs text-gray-500">
                                <span className="text-accent-cyan capitalize">{agent.type || 'agent'}</span>
                                {agent.knowledge_count ? ` • ${agent.knowledge_count} knowledge` : ''}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 flex-shrink-0">
                            <div className="text-right">
                              <p className="text-sm font-medium">{agent.total_executions} runs</p>
                              <p className="text-xs text-gray-500">{(agent.success_rate || 0).toFixed(0)}% success</p>
                            </div>
                            <div className={cn(
                              'px-2 py-1 rounded text-sm font-bold',
                              (agent.effectiveness_score || 0) >= 80 ? 'bg-accent-green/20 text-accent-green' :
                              (agent.effectiveness_score || 0) >= 60 ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                            )}>
                              {agent.effectiveness_score || 0}%
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Bot className="mx-auto mb-2" size={32} />
                    <p>No agent execution data available</p>
                  </div>
                )}
              </div>

              {/* Recent Agent Activity */}
              {recentAgentActivity.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {recentAgentActivity.slice(0, 10).map((activity: {
                      agent?: string
                      task?: string
                      completed?: string
                      duration?: number
                      success?: boolean
                    }, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2 rounded-lg bg-dark-bg"
                      >
                        <div className="flex items-center gap-2">
                          <div className={cn(
                            'h-6 w-6 rounded-full flex items-center justify-center',
                            activity.success !== false ? 'bg-accent-green/20' : 'bg-accent-red/20'
                          )}>
                            {activity.success !== false ? (
                              <CheckCircle size={12} className="text-accent-green" />
                            ) : (
                              <XCircle size={12} className="text-accent-red" />
                            )}
                          </div>
                          <span className="text-sm font-medium">{activity.agent || 'Unknown'}</span>
                          <span className="text-xs text-gray-500 truncate max-w-[200px]" title={activity.task}>
                            {activity.task || 'executed'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          <span className={cn(
                            'px-1.5 py-0.5 rounded',
                            activity.success !== false ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-red/20 text-accent-red'
                          )}>
                            {activity.success !== false ? 'Success' : 'Failed'}
                          </span>
                          {activity.duration && <span className="text-gray-500">{(activity.duration ?? 0).toFixed(1)}s</span>}
                          {activity.completed && <span className="text-gray-500">{new Date(activity.completed).toLocaleTimeString()}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Session 1007: Billing Tab — link to standalone page */}
      {activeTab === 'billing' && (
        <div className="space-y-6">
          <div className="card text-center py-12">
            <CreditCard className="mx-auto mb-4 text-primary-400" size={48} />
            <h3 className="text-xl font-semibold mb-2">Billing & Subscriptions</h3>
            <p className="text-gray-400 mb-6">Manage API keys, subscription tiers, and usage limits.</p>
            <a href="/billing" className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-500 rounded-lg font-medium transition-colors">
              Open Billing Dashboard <ExternalLink size={16} />
            </a>
          </div>
        </div>
      )}

      {/* Session 1007: Analytics Tab — link to standalone page */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <div className="card text-center py-12">
            <BarChart3 className="mx-auto mb-4 text-accent-cyan" size={48} />
            <h3 className="text-xl font-semibold mb-2">Analytics Dashboard</h3>
            <p className="text-gray-400 mb-6">View platform metrics, agent performance, and usage analytics.</p>
            <a href="/analytics" className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-500 rounded-lg font-medium transition-colors">
              Open Analytics Dashboard <ExternalLink size={16} />
            </a>
          </div>
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
