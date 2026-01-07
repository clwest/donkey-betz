import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { adminApi, dashboardApi, heartApi, lungsApi, circulatoryApi, spineApi, immuneApi } from '@/lib/api'
import {
  Server, Activity, CheckCircle, XCircle,
  Loader2, RefreshCw, Settings, Play, Bug, Bot, Clock, Globe,
  Heart, Brain, Zap, Users, Eye, Hand, Database, Wind, DollarSign, TrendingUp, GitBranch, AlertTriangle, Bone, Route, Shield, ShieldAlert, ShieldCheck, Ban
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'heart' | 'lungs' | 'circulatory' | 'spine' | 'immune' | 'health' | 'celery' | 'spiders' | 'agents'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

const tabs = [
  { id: 'heart' as TabType, label: 'HEART', icon: Heart },
  { id: 'lungs' as TabType, label: 'LUNGS', icon: Wind },
  { id: 'circulatory' as TabType, label: 'CIRCULATORY', icon: GitBranch },
  { id: 'spine' as TabType, label: 'SPINE', icon: Bone },
  { id: 'immune' as TabType, label: 'IMMUNE', icon: Shield },
  { id: 'health' as TabType, label: 'Services', icon: Activity },
  { id: 'celery' as TabType, label: 'Celery', icon: Clock },
  { id: 'spiders' as TabType, label: 'Spiders', icon: Bug },
  { id: 'agents' as TabType, label: 'Agents', icon: Bot },
]

// Body part icons for HEART service
const BODY_PARTS = {
  brain: { icon: Brain, label: 'Brain', description: 'ThinkingAgent - autonomous reasoning' },
  nervous_system: { icon: Zap, label: 'Nervous System', description: 'LLM/ML Routers - signal routing' },
  organs: { icon: Users, label: 'Organs', description: '72 Agents - work execution' },
  sensory: { icon: Eye, label: 'Sensory', description: '77 Spiders - data gathering' },
  skin: { icon: Hand, label: 'Skin', description: 'Workspace Manager - reality interface' },
  memory: { icon: Database, label: 'Memory', description: 'Database & Redis - persistence' },
} as const

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
  const { data: heartStatusData, isLoading: loadingHeart, refetch: refetchHeart } = useQuery({
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

  // LUNGS Service queries (Session 703)
  const { data: lungsStatusData, isLoading: loadingLungs, refetch: refetchLungs } = useQuery({
    queryKey: ['lungs-status'],
    queryFn: () => lungsApi.status(),
    refetchInterval: 30000,
    enabled: activeTab === 'lungs',
  })

  const { data: lungsBudgetsData } = useQuery({
    queryKey: ['lungs-budgets'],
    queryFn: () => lungsApi.budgets(),
    enabled: activeTab === 'lungs',
  })

  const { data: lungsForecastData } = useQuery({
    queryKey: ['lungs-forecast'],
    queryFn: () => lungsApi.forecast(),
    enabled: activeTab === 'lungs',
  })

  // CIRCULATORY Service queries (Session 703)
  // Use /circulate/ endpoint which returns full data with correct field names
  const { data: circulatoryStatusData, isLoading: loadingCirculatory, refetch: refetchCirculatory } = useQuery({
    queryKey: ['circulatory-circulate'],
    queryFn: () => circulatoryApi.circulate(),
    refetchInterval: 30000,
    enabled: activeTab === 'circulatory',
  })

  // Routes are now fetched from /circulate/ endpoint, not needed separately
  // const { data: circulatoryRoutesData } = useQuery({
  //   queryKey: ['circulatory-routes'],
  //   queryFn: () => circulatoryApi.routes(),
  //   enabled: activeTab === 'circulatory',
  // })

  const { data: circulatoryBottlenecksData } = useQuery({
    queryKey: ['circulatory-bottlenecks'],
    queryFn: () => circulatoryApi.bottlenecks(),
    enabled: activeTab === 'circulatory',
  })

  const { data: circulatoryHistoryData } = useQuery({
    queryKey: ['circulatory-history'],
    queryFn: () => circulatoryApi.history(24, 50),
    enabled: activeTab === 'circulatory',
  })

  // SPINE Service queries (Session 704)
  const { data: spineAlignData, isLoading: loadingSpine, refetch: refetchSpine } = useQuery({
    queryKey: ['spine-align'],
    queryFn: () => spineApi.align(),
    refetchInterval: 30000,
    enabled: activeTab === 'spine',
  })

  const { data: spineCategoriesData } = useQuery({
    queryKey: ['spine-categories'],
    queryFn: () => spineApi.categories(),
    enabled: activeTab === 'spine',
  })

  // History query available for future use
  // const { data: spineHistoryData } = useQuery({
  //   queryKey: ['spine-history'],
  //   queryFn: () => spineApi.history(24, 50),
  //   enabled: activeTab === 'spine',
  // })

  // IMMUNE System queries (Session 705)
  const { data: immuneScanData, isLoading: loadingImmune, refetch: refetchImmune } = useQuery({
    queryKey: ['immune-scan'],
    queryFn: () => immuneApi.scan(),
    refetchInterval: 30000,
    enabled: activeTab === 'immune',
  })

  const { data: immunePatternsData } = useQuery({
    queryKey: ['immune-patterns'],
    queryFn: () => immuneApi.patterns(),
    enabled: activeTab === 'immune',
  })

  const { data: immuneThreatsData } = useQuery({
    queryKey: ['immune-threats'],
    queryFn: () => immuneApi.threats({ hours: 24, limit: 50 }),
    enabled: activeTab === 'immune',
  })

  const { data: immuneQuarantineData } = useQuery({
    queryKey: ['immune-quarantine'],
    queryFn: () => immuneApi.quarantine(),
    enabled: activeTab === 'immune',
  })

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

  // LUNGS data (Session 703)
  const lungsStatus = lungsStatusData?.data || {}
  const lungsBudgets = lungsBudgetsData?.data?.budgets || []
  const lungsForecasts = lungsForecastData?.data?.forecasts || []
  const lungsProviders = lungsStatus.providers || {}

  // CIRCULATORY data (Session 703)
  const circulatoryStatus = circulatoryStatusData?.data || {}
  // Convert routes object to array format from /circulate/ endpoint
  const circulatoryRoutesObj = circulatoryStatus.routes || {}
  interface CirculatoryRoute {
    id: string
    name: string
    display_name?: string
    status: string
    is_healthy: boolean
    health_score: number
    current_depth?: number
    throughput?: number
    latency_ms?: number
    active_workers?: number
    active_tasks?: number
    bottleneck?: boolean
  }
  const circulatoryRoutes: CirculatoryRoute[] = Object.entries(circulatoryRoutesObj).map(([name, data]) => ({
    id: name,
    name,
    status: 'unknown',
    is_healthy: false,
    health_score: 0,
    ...(data as Partial<CirculatoryRoute>),
  }))
  const circulatoryBottlenecks = circulatoryStatus.bottlenecks || circulatoryBottlenecksData?.data?.bottlenecks || []
  const circulatoryHistory = circulatoryHistoryData?.data?.history || []

  // SPINE data (Session 704)
  const spineStatus = spineAlignData?.data || {}
  const spinePatterns = spineStatus.patterns || {}
  const spinePatternsArray = Object.entries(spinePatterns).map(([pattern, data]) => ({
    pattern,
    ...(data as Record<string, unknown>),
  }))
  const spineCategories = spineCategoriesData?.data?.categories || {}
  // const spineHistory = spineHistoryData?.data?.history || []  // Available for future use
  const spineIntegrations = spineStatus.integrations || {}

  // IMMUNE data (Session 705)
  const immuneStatus = immuneScanData?.data || {}
  const immunePatterns = immunePatternsData?.data?.patterns || []
  const immuneThreats = immuneThreatsData?.data?.threats || []
  const immuneQuarantine = immuneQuarantineData?.data?.quarantine || []
  // Available for future use:
  // const immuneThreatsByCategory = immuneStatus.threats_by_category || {}
  // const immuneThreatsBySeverity = immuneStatus.threats_by_severity || {}

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

              {/* Body Parts Grid */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Body Part Status</h3>
                  <button
                    onClick={() => refetchHeart()}
                    className="btn btn-secondary btn-sm flex items-center gap-2"
                  >
                    <RefreshCw size={14} />
                    Refresh
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {(Object.keys(BODY_PARTS) as Array<keyof typeof BODY_PARTS>).map((partKey) => {
                    const part = BODY_PARTS[partKey]
                    const status = heartComponents[partKey] || {}
                    const Icon = part.icon
                    const isHealthy = status.is_healthy
                    const partStatus = status.status || 'unknown'

                    return (
                      <div
                        key={partKey}
                        className={cn(
                          'p-4 rounded-lg border transition-colors',
                          getStatusBg(partStatus),
                          isHealthy ? 'border-accent-green/30' : isHealthy === false ? 'border-accent-red/30' : 'border-dark-border'
                        )}
                      >
                        <div className="flex items-start gap-3">
                          <div className={cn('h-12 w-12 rounded-lg flex items-center justify-center flex-shrink-0', getStatusBg(partStatus))}>
                            <Icon size={24} className={getStatusColor(partStatus)} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="font-semibold">{part.label}</p>
                              {isHealthy === true && <CheckCircle size={14} className="text-accent-green" />}
                              {isHealthy === false && <XCircle size={14} className="text-accent-red" />}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">{part.description}</p>
                            {status.response_time_ms && (
                              <p className="text-xs text-gray-400 mt-1">Response: {status.response_time_ms}ms</p>
                            )}
                            {status.details && (
                              <div className="mt-2 text-xs text-gray-400">
                                {Object.entries(status.details).slice(0, 3).map(([key, value]) => (
                                  <p key={key} className="truncate">
                                    {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                  </p>
                                ))}
                              </div>
                            )}
                            {status.last_error && (
                              <p className="text-xs text-accent-red mt-2 truncate" title={status.last_error}>
                                {status.last_error}
                              </p>
                            )}
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
                              {beat.health_score.toFixed(0)}% - {beat.components_healthy}/{beat.components_checked} healthy
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

              {/* Human Body Architecture */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Human Body Architecture</h3>
                <p className="text-sm text-gray-400 mb-4">
                  The platform uses the human body as an architectural metaphor. Each body part has specific responsibilities:
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-dark-border">
                        <th className="text-left py-2 px-3 text-gray-400">Body Part</th>
                        <th className="text-left py-2 px-3 text-gray-400">Component</th>
                        <th className="text-left py-2 px-3 text-gray-400">Purpose</th>
                        <th className="text-center py-2 px-3 text-gray-400">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-dark-border/50">
                        <td className="py-2 px-3 font-medium">Consciousness</td>
                        <td className="py-2 px-3 text-gray-400">Human Operator</td>
                        <td className="py-2 px-3 text-gray-400">Final decisions & approvals</td>
                        <td className="py-2 px-3 text-center"><span className="text-accent-green">Active</span></td>
                      </tr>
                      {(Object.keys(BODY_PARTS) as Array<keyof typeof BODY_PARTS>).map((partKey) => {
                        const part = BODY_PARTS[partKey]
                        const status = heartComponents[partKey] || {}
                        return (
                          <tr key={partKey} className="border-b border-dark-border/50">
                            <td className="py-2 px-3 font-medium">{part.label}</td>
                            <td className="py-2 px-3 text-gray-400">{status.display_name || partKey}</td>
                            <td className="py-2 px-3 text-gray-400">{part.description}</td>
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

      {/* LUNGS Tab - Session 703 */}
      {activeTab === 'lungs' && (
        <div className="space-y-6">
          {loadingLungs ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Overall Oxygen Status */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      'h-12 w-12 rounded-lg flex items-center justify-center',
                      (lungsStatus.system_oxygen || 100) >= 80 ? 'bg-accent-green/20' :
                      (lungsStatus.system_oxygen || 100) >= 50 ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                    )}>
                      <Wind size={24} className={cn(
                        (lungsStatus.system_oxygen || 100) >= 80 ? 'text-accent-green' :
                        (lungsStatus.system_oxygen || 100) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Oxygen Level</p>
                      <p className={cn(
                        'text-2xl font-bold',
                        (lungsStatus.system_oxygen || 100) >= 80 ? 'text-accent-green' :
                        (lungsStatus.system_oxygen || 100) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {(lungsStatus.system_oxygen || 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <DollarSign className="text-accent-cyan" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Cost Today</p>
                      <p className="text-2xl font-bold">${(lungsStatus.total_cost_today || 0).toFixed(4)}</p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Activity className="text-primary-400" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">API Calls Today</p>
                      <p className="text-2xl font-bold">{lungsStatus.total_calls_today || 0}</p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="text-accent-green" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Status</p>
                      <p className={cn(
                        'text-lg font-bold capitalize',
                        lungsStatus.system_status === 'normal' ? 'text-accent-green' :
                        lungsStatus.system_status === 'warning' ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {lungsStatus.system_status || 'Unknown'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Provider Oxygen Levels */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Provider Oxygen Levels</h3>
                  <button
                    onClick={() => refetchLungs()}
                    className="btn btn-secondary btn-sm flex items-center gap-2"
                  >
                    <RefreshCw size={14} />
                    Refresh
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(lungsProviders).map(([provider, data]) => {
                    const providerData = data as { oxygen_level: number; status: string; cost_today: number; calls_today: number }
                    const oxygenLevel = providerData.oxygen_level || 100
                    const status = providerData.status || 'normal'

                    return (
                      <div
                        key={provider}
                        className={cn(
                          'p-4 rounded-lg border transition-colors',
                          oxygenLevel >= 80 ? 'bg-accent-green/10 border-accent-green/30' :
                          oxygenLevel >= 50 ? 'bg-accent-amber/10 border-accent-amber/30' : 'bg-accent-red/10 border-accent-red/30'
                        )}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <p className="font-semibold capitalize">{provider.replace('_', ' ')}</p>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded capitalize',
                            status === 'normal' ? 'bg-accent-green/20 text-accent-green' :
                            status === 'warning' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-accent-red/20 text-accent-red'
                          )}>
                            {status}
                          </span>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Oxygen</span>
                            <span className={cn(
                              'font-bold',
                              oxygenLevel >= 80 ? 'text-accent-green' :
                              oxygenLevel >= 50 ? 'text-accent-amber' : 'text-accent-red'
                            )}>
                              {oxygenLevel.toFixed(1)}%
                            </span>
                          </div>
                          <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                            <div
                              className={cn(
                                'h-full rounded-full transition-all',
                                oxygenLevel >= 80 ? 'bg-accent-green' :
                                oxygenLevel >= 50 ? 'bg-accent-amber' : 'bg-accent-red'
                              )}
                              style={{ width: `${oxygenLevel}%` }}
                            />
                          </div>
                          <div className="flex justify-between text-xs text-gray-500 mt-2">
                            <span>${(providerData.cost_today || 0).toFixed(4)}</span>
                            <span>{providerData.calls_today || 0} calls</span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Budget Overview */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Budget Configuration</h3>
                {lungsBudgets.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-dark-border">
                          <th className="text-left py-2 px-3 text-gray-400">Budget Name</th>
                          <th className="text-left py-2 px-3 text-gray-400">Scope</th>
                          <th className="text-left py-2 px-3 text-gray-400">Period</th>
                          <th className="text-right py-2 px-3 text-gray-400">Limit</th>
                          <th className="text-center py-2 px-3 text-gray-400">Warning</th>
                          <th className="text-center py-2 px-3 text-gray-400">Critical</th>
                          <th className="text-center py-2 px-3 text-gray-400">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {lungsBudgets.map((budget: {
                          id: string
                          name: string
                          scope: string
                          scope_identifier: string
                          period: string
                          cost_limit: number
                          warning_threshold: number
                          critical_threshold: number
                          is_active: boolean
                        }) => (
                          <tr key={budget.id} className="border-b border-dark-border/50 hover:bg-dark-bg/50">
                            <td className="py-2 px-3 font-medium">{budget.name}</td>
                            <td className="py-2 px-3 text-gray-400 capitalize">
                              {budget.scope === 'provider' ? budget.scope_identifier.replace('_', ' ') : budget.scope}
                            </td>
                            <td className="py-2 px-3 text-gray-400 capitalize">{budget.period}</td>
                            <td className="py-2 px-3 text-right font-mono">${budget.cost_limit?.toFixed(2) || '0.00'}</td>
                            <td className="py-2 px-3 text-center text-accent-amber">{((budget.warning_threshold || 0.8) * 100).toFixed(0)}%</td>
                            <td className="py-2 px-3 text-center text-accent-red">{((budget.critical_threshold || 0.95) * 100).toFixed(0)}%</td>
                            <td className="py-2 px-3 text-center">
                              <span className={cn(
                                'text-xs px-2 py-1 rounded',
                                budget.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                              )}>
                                {budget.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <DollarSign className="mx-auto mb-2" size={32} />
                    <p>No budgets configured</p>
                  </div>
                )}
              </div>

              {/* Spending Forecast */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Spending Forecast</h3>
                {lungsForecasts.length > 0 ? (
                  <div className="space-y-3">
                    {lungsForecasts.map((forecast: {
                      budget_name: string
                      scope: string
                      period: string
                      limit: number
                      projected_cost: number
                      on_pace_to_exceed: boolean
                      confidence: number
                      period_elapsed_percent: number
                    }) => (
                      <div
                        key={forecast.budget_name}
                        className={cn(
                          'p-4 rounded-lg border transition-colors',
                          forecast.on_pace_to_exceed ? 'bg-accent-red/10 border-accent-red/30' : 'border-dark-border'
                        )}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="font-medium">{forecast.budget_name}</p>
                            <p className="text-xs text-gray-500">{forecast.scope} • {forecast.period}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            {forecast.on_pace_to_exceed && (
                              <span className="text-xs px-2 py-1 rounded bg-accent-red/20 text-accent-red flex items-center gap-1">
                                <TrendingUp size={12} />
                                Exceeding
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-400">Limit</p>
                            <p className="font-mono font-bold">${forecast.limit.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-gray-400">Projected</p>
                            <p className={cn(
                              'font-mono font-bold',
                              forecast.on_pace_to_exceed ? 'text-accent-red' : 'text-accent-green'
                            )}>
                              ${forecast.projected_cost.toFixed(4)}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-400">Period Elapsed</p>
                            <p className="font-mono">{forecast.period_elapsed_percent.toFixed(1)}%</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <TrendingUp className="mx-auto mb-2" size={32} />
                    <p>No forecast data available</p>
                  </div>
                )}
              </div>

              {/* LUNGS Architecture */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">LUNGS Architecture</h3>
                <p className="text-sm text-gray-400 mb-4">
                  The LUNGS (Limits, Usage, Notifications, Governance, Spending) service manages resource consumption and budget enforcement across all AI providers.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-cyan mb-1">Oxygen = Budget Remaining</p>
                    <p className="text-xs text-gray-400">100% = No spending, 0% = Budget exhausted</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-amber mb-1">Warning Threshold</p>
                    <p className="text-xs text-gray-400">Default 80% - alerts when budget usage reaches this level</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-red mb-1">Critical Threshold</p>
                    <p className="text-xs text-gray-400">Default 95% - urgent alerts, may block new calls</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-green mb-1">Budget Periods</p>
                    <p className="text-xs text-gray-400">Daily and Monthly limits per provider and system-wide</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* CIRCULATORY Tab - Session 703 */}
      {activeTab === 'circulatory' && (
        <div className="space-y-6">
          {loadingCirculatory ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Overall Flow Status */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      'h-12 w-12 rounded-lg flex items-center justify-center',
                      (circulatoryStatus.flow_score || 0) >= 80 ? 'bg-accent-green/20' :
                      (circulatoryStatus.flow_score || 0) >= 50 ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                    )}>
                      <GitBranch size={24} className={cn(
                        (circulatoryStatus.flow_score || 0) >= 80 ? 'text-accent-green' :
                        (circulatoryStatus.flow_score || 0) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Flow Score</p>
                      <p className={cn(
                        'text-2xl font-bold',
                        (circulatoryStatus.flow_score || 0) >= 80 ? 'text-accent-green' :
                        (circulatoryStatus.flow_score || 0) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {(circulatoryStatus.flow_score || 0).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Activity className="text-accent-cyan" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Overall Status</p>
                      <p className={cn(
                        'text-lg font-bold capitalize',
                        circulatoryStatus.overall_status === 'flowing' ? 'text-accent-green' :
                        circulatoryStatus.overall_status === 'slow' ? 'text-accent-amber' :
                        circulatoryStatus.overall_status === 'congested' ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {circulatoryStatus.overall_status || 'Unknown'}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="text-accent-green" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Routes</p>
                      <p className="text-2xl font-bold">
                        {circulatoryStatus.routes_healthy ?? circulatoryRoutes.filter((r: { is_healthy?: boolean }) => r.is_healthy).length}/
                        {circulatoryStatus.routes_checked ?? circulatoryRoutes.length}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className={cn(
                      (circulatoryStatus.bottleneck_count || circulatoryBottlenecks.length) > 0 ? 'text-accent-amber' : 'text-gray-500'
                    )} size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Bottlenecks</p>
                      <p className={cn(
                        'text-2xl font-bold',
                        (circulatoryStatus.bottleneck_count || circulatoryBottlenecks.length) > 0 ? 'text-accent-amber' : 'text-accent-green'
                      )}>
                        {circulatoryStatus.bottleneck_count ?? circulatoryBottlenecks.length}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Flow Routes */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Flow Routes</h3>
                  <button
                    onClick={() => refetchCirculatory()}
                    className="btn btn-secondary btn-sm flex items-center gap-2"
                  >
                    <RefreshCw size={14} />
                    Refresh
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {circulatoryRoutes.map((route: {
                    id: string
                    name: string
                    display_name?: string
                    status: string
                    is_healthy: boolean
                    health_score: number
                    current_depth?: number
                    throughput?: number
                    latency_ms?: number
                    active_workers?: number
                    active_tasks?: number
                    bottleneck?: boolean
                  }) => {
                    // Data is flat from /circulate/ endpoint, not nested in current_status
                    const isHealthy = route.is_healthy
                    const statusStr = route.status || 'unknown'
                    const healthScore = route.health_score || 0

                    // Format route name for display
                    const displayName = route.display_name || route.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

                    return (
                      <div
                        key={route.id}
                        className={cn(
                          'p-4 rounded-lg border transition-colors',
                          isHealthy ? 'bg-accent-green/10 border-accent-green/30' :
                          statusStr === 'slow' || statusStr === 'congested' ? 'bg-accent-amber/10 border-accent-amber/30' : 'bg-accent-red/10 border-accent-red/30'
                        )}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <p className="font-semibold">{displayName}</p>
                            {route.bottleneck && (
                              <span className="text-xs px-1.5 py-0.5 rounded bg-accent-amber/20 text-accent-amber">Bottleneck</span>
                            )}
                          </div>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded capitalize',
                            isHealthy ? 'bg-accent-green/20 text-accent-green' :
                            statusStr === 'slow' || statusStr === 'congested' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-accent-red/20 text-accent-red'
                          )}>
                            {statusStr}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div>
                            <p className="text-gray-500">Health</p>
                            <p className={cn(
                              'font-bold',
                              healthScore >= 80 ? 'text-accent-green' :
                              healthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
                            )}>
                              {healthScore.toFixed(0)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500">Depth</p>
                            <p className="font-medium">{route.current_depth ?? '-'}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Latency</p>
                            <p className="font-medium">{route.latency_ms ? `${route.latency_ms.toFixed(1)}ms` : '-'}</p>
                          </div>
                        </div>
                        {(route.active_workers !== undefined || route.active_tasks !== undefined) && (
                          <div className="flex gap-4 text-xs text-gray-500 mt-2">
                            {route.active_workers !== undefined && <span>Workers: {route.active_workers}</span>}
                            {route.active_tasks !== undefined && <span>Tasks: {route.active_tasks}</span>}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
                {circulatoryRoutes.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    <GitBranch className="mx-auto mb-2" size={32} />
                    <p>No flow routes configured</p>
                  </div>
                )}
              </div>

              {/* Bottlenecks */}
              {circulatoryBottlenecks.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <AlertTriangle className="text-accent-amber" size={20} />
                    Active Bottlenecks
                  </h3>
                  <div className="space-y-3">
                    {circulatoryBottlenecks.map((bottleneck: {
                      route_name: string
                      severity: string
                      issue: string
                      metric?: string
                      current_value?: number
                      threshold?: number
                    }, idx: number) => (
                      <div
                        key={idx}
                        className={cn(
                          'p-4 rounded-lg border',
                          bottleneck.severity === 'critical' ? 'bg-accent-red/10 border-accent-red/30' :
                          bottleneck.severity === 'warning' ? 'bg-accent-amber/10 border-accent-amber/30' : 'border-dark-border'
                        )}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-medium">{bottleneck.route_name}</p>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded capitalize',
                            bottleneck.severity === 'critical' ? 'bg-accent-red/20 text-accent-red' :
                            bottleneck.severity === 'warning' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                          )}>
                            {bottleneck.severity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-300">{bottleneck.issue}</p>
                        {bottleneck.metric && (
                          <p className="text-xs text-gray-500 mt-2">
                            {bottleneck.metric}: {bottleneck.current_value} (threshold: {bottleneck.threshold})
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Circulation History */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Circulation Pulse History (24h)</h3>
                {circulatoryHistory.length > 0 ? (
                  <div className="space-y-2 max-h-[400px] overflow-y-auto">
                    {circulatoryHistory.slice(0, 20).map((pulse: {
                      id: string
                      flow_score: number
                      overall_status: string
                      recorded_at: string
                      check_duration_ms?: number
                      routes_healthy: number
                      routes_checked: number
                    }, idx: number) => (
                      <div
                        key={pulse.id || idx}
                        className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            'h-8 w-8 rounded-full flex items-center justify-center',
                            pulse.overall_status === 'flowing' ? 'bg-accent-green/20' :
                            pulse.overall_status === 'slow' || pulse.overall_status === 'congested' ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                          )}>
                            <GitBranch size={14} className={cn(
                              pulse.overall_status === 'flowing' ? 'text-accent-green' :
                              pulse.overall_status === 'slow' || pulse.overall_status === 'congested' ? 'text-accent-amber' : 'text-accent-red'
                            )} />
                          </div>
                          <div>
                            <p className="font-medium text-sm">
                              {pulse.flow_score.toFixed(0)}% - {pulse.routes_healthy}/{pulse.routes_checked} healthy
                            </p>
                            <p className="text-xs text-gray-500">
                              {new Date(pulse.recorded_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {pulse.check_duration_ms && (
                            <span className="text-xs text-gray-400">{pulse.check_duration_ms}ms</span>
                          )}
                          <span className={cn(
                            'text-xs px-2 py-1 rounded capitalize',
                            pulse.overall_status === 'flowing' ? 'bg-accent-green/20 text-accent-green' :
                            pulse.overall_status === 'slow' || pulse.overall_status === 'congested' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-accent-red/20 text-accent-red'
                          )}>
                            {pulse.overall_status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <GitBranch className="mx-auto mb-2" size={32} />
                    <p>No circulation history yet</p>
                    <p className="text-sm text-gray-500 mt-1">Run a circulation check to see data flow status</p>
                  </div>
                )}
              </div>

              {/* Circulatory Architecture */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Circulatory System Architecture</h3>
                <p className="text-sm text-gray-400 mb-4">
                  The CIRCULATORY system monitors data flow health across all queues, channels, and streams - the blood circulation of the AI body.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-red mb-1">Blood = Data</p>
                    <p className="text-xs text-gray-400">Messages, tasks, events flowing through the system</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-cyan mb-1">Arteries = Outbound</p>
                    <p className="text-xs text-gray-400">WebSocket broadcasts, API responses, notifications</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-primary-400 mb-1">Veins = Inbound</p>
                    <p className="text-xs text-gray-400">Spider data, user inputs, external webhooks</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-amber mb-1">Blood Pressure = Queue Depth</p>
                    <p className="text-xs text-gray-400">High pressure indicates congestion, low indicates idle</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* SPINE Tab - Session 704 */}
      {activeTab === 'spine' && (
        <div className="space-y-6">
          {loadingSpine ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Overall Spine Status */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      'h-12 w-12 rounded-lg flex items-center justify-center',
                      (spineStatus.health_score || 0) >= 80 ? 'bg-accent-green/20' :
                      (spineStatus.health_score || 0) >= 50 ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                    )}>
                      <Bone size={24} className={cn(
                        (spineStatus.health_score || 0) >= 80 ? 'text-accent-green' :
                        (spineStatus.health_score || 0) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Health Score</p>
                      <p className={cn(
                        'text-2xl font-bold',
                        (spineStatus.health_score || 0) >= 80 ? 'text-accent-green' :
                        (spineStatus.health_score || 0) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {(spineStatus.health_score || 0).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Activity className="text-accent-cyan" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Status</p>
                      <p className={cn(
                        'text-lg font-bold capitalize',
                        spineStatus.overall_status === 'aligned' ? 'text-accent-green' :
                        spineStatus.overall_status === 'strained' ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {spineStatus.overall_status || 'Unknown'}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Route className="text-primary-400" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Patterns</p>
                      <p className="text-2xl font-bold">
                        {spineStatus.healthy_patterns || 0}/{spineStatus.total_patterns || 0}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className={cn(
                      (spineStatus.routing?.routes_blocked || 0) > 0 ? 'text-accent-red' : 'text-gray-500'
                    )} size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Blocked Routes</p>
                      <p className={cn(
                        'text-2xl font-bold',
                        (spineStatus.routing?.routes_blocked || 0) > 0 ? 'text-accent-red' : 'text-accent-green'
                      )}>
                        {spineStatus.routing?.routes_blocked || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Integration Status */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Integration Status</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {['heart', 'lungs', 'circulatory'].map((system) => {
                    const integration = spineIntegrations[system] || {}
                    const isHealthy = integration.is_healthy || integration.is_flowing
                    const score = integration.health_score || integration.capacity_score || integration.flow_score || 0

                    return (
                      <div
                        key={system}
                        className={cn(
                          'p-4 rounded-lg border',
                          isHealthy ? 'bg-accent-green/10 border-accent-green/30' : 'bg-accent-amber/10 border-accent-amber/30'
                        )}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-semibold capitalize">{system}</p>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded capitalize',
                            isHealthy ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-amber/20 text-accent-amber'
                          )}>
                            {integration.status || 'unknown'}
                          </span>
                        </div>
                        <p className={cn(
                          'text-2xl font-bold',
                          score >= 80 ? 'text-accent-green' : score >= 50 ? 'text-accent-amber' : 'text-accent-red'
                        )}>
                          {score.toFixed(0)}%
                        </p>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Route Patterns */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Route Patterns ({spinePatternsArray.length})</h3>
                  <button
                    onClick={() => refetchSpine()}
                    className="btn btn-secondary btn-sm flex items-center gap-2"
                  >
                    <RefreshCw size={14} />
                    Refresh
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {spinePatternsArray.map((route: {
                    pattern: string
                    display_name?: string
                    category?: string
                    priority?: string
                    is_healthy?: boolean
                    health_score?: number
                    can_route?: boolean
                    route_reason?: string
                    total_requests?: number
                    avg_latency_ms?: number
                  }) => (
                    <div
                      key={route.pattern}
                      className={cn(
                        'p-3 rounded-lg border transition-colors',
                        route.is_healthy ? 'bg-accent-green/5 border-accent-green/30' :
                        route.can_route === false ? 'bg-accent-red/10 border-accent-red/30' : 'bg-accent-amber/10 border-accent-amber/30'
                      )}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-sm truncate" title={route.pattern}>
                          {route.display_name || route.pattern}
                        </p>
                        {route.priority === 'critical' && (
                          <span className="text-xs px-1 py-0.5 rounded bg-accent-red/20 text-accent-red">Critical</span>
                        )}
                        {route.priority === 'high' && (
                          <span className="text-xs px-1 py-0.5 rounded bg-accent-amber/20 text-accent-amber">High</span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mb-2 capitalize">{route.category || 'other'}</p>
                      <div className="flex items-center justify-between text-xs">
                        <span className={cn(
                          route.can_route ? 'text-accent-green' : 'text-accent-red'
                        )}>
                          {route.can_route ? '✓ Routable' : '✗ Blocked'}
                        </span>
                        <span className={cn(
                          'font-medium',
                          (route.health_score || 0) >= 80 ? 'text-accent-green' :
                          (route.health_score || 0) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                        )}>
                          {(route.health_score || 0).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                {spinePatternsArray.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    <Bone className="mx-auto mb-2" size={32} />
                    <p>No route patterns configured</p>
                  </div>
                )}
              </div>

              {/* Category Health */}
              {Object.keys(spineCategories).length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Category Health</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(spineCategories).map(([category, data]: [string, unknown]) => {
                      const catData = data as { health_score?: number; pattern_count?: number; healthy_count?: number }
                      const score = catData.health_score || 0

                      return (
                        <div
                          key={category}
                          className={cn(
                            'p-3 rounded-lg border',
                            score >= 80 ? 'bg-accent-green/10 border-accent-green/30' :
                            score >= 50 ? 'bg-accent-amber/10 border-accent-amber/30' : 'bg-accent-red/10 border-accent-red/30'
                          )}
                        >
                          <p className="text-sm font-medium capitalize mb-1">{category.replace('_', ' ')}</p>
                          <div className="flex items-center justify-between">
                            <span className={cn(
                              'text-xl font-bold',
                              score >= 80 ? 'text-accent-green' : score >= 50 ? 'text-accent-amber' : 'text-accent-red'
                            )}>
                              {score.toFixed(0)}%
                            </span>
                            <span className="text-xs text-gray-500">
                              {catData.healthy_count || 0}/{catData.pattern_count || 0}
                            </span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Spine Architecture */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Spine Architecture</h3>
                <p className="text-sm text-gray-400 mb-4">
                  The SPINE is the backbone of the AI body - central API routing and coordination.
                  It tracks route health, manages request flow, and coordinates with HEART, LUNGS, and CIRCULATORY.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-primary-400 mb-1">Aligned = Healthy</p>
                    <p className="text-xs text-gray-400">All routes operational, no issues</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-amber mb-1">Strained = Degraded</p>
                    <p className="text-xs text-gray-400">Some routes showing stress, monitoring closely</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-cyan mb-1">Compressed = High Load</p>
                    <p className="text-xs text-gray-400">Heavy traffic, routing slowed to protect system</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-red mb-1">Injured = Critical</p>
                    <p className="text-xs text-gray-400">Critical routes failing, immediate attention needed</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* IMMUNE Tab - Session 705 */}
      {activeTab === 'immune' && (
        <div className="space-y-6">
          {loadingImmune ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Overall Immune Status */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      'h-12 w-12 rounded-lg flex items-center justify-center',
                      (immuneStatus.health_score || 0) >= 80 ? 'bg-accent-green/20' :
                      (immuneStatus.health_score || 0) >= 50 ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                    )}>
                      <Shield size={24} className={cn(
                        (immuneStatus.health_score || 0) >= 80 ? 'text-accent-green' :
                        (immuneStatus.health_score || 0) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )} />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Health Score</p>
                      <p className={cn(
                        'text-2xl font-bold',
                        (immuneStatus.health_score || 0) >= 80 ? 'text-accent-green' :
                        (immuneStatus.health_score || 0) >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {(immuneStatus.health_score || 0).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <ShieldAlert className={cn(
                      immuneStatus.threat_level === 'none' ? 'text-accent-green' :
                      immuneStatus.threat_level === 'low' ? 'text-accent-cyan' :
                      immuneStatus.threat_level === 'medium' ? 'text-accent-amber' : 'text-accent-red'
                    )} size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Threat Level</p>
                      <p className={cn(
                        'text-lg font-bold capitalize',
                        immuneStatus.threat_level === 'none' ? 'text-accent-green' :
                        immuneStatus.threat_level === 'low' ? 'text-accent-cyan' :
                        immuneStatus.threat_level === 'medium' ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {immuneStatus.threat_level || 'None'}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <ShieldCheck className="text-primary-400" size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Active Patterns</p>
                      <p className="text-2xl font-bold">
                        {immuneStatus.patterns?.active || immunePatterns.length || 0}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <Ban className={cn(
                      (immuneQuarantine.length || 0) > 0 ? 'text-accent-red' : 'text-gray-500'
                    )} size={24} />
                    <div>
                      <p className="text-sm text-gray-400">Quarantined</p>
                      <p className={cn(
                        'text-2xl font-bold',
                        (immuneQuarantine.length || 0) > 0 ? 'text-accent-red' : 'text-accent-green'
                      )}>
                        {immuneQuarantine.length || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Threat Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Threats (24h)</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">Detected</p>
                      <p className="text-xl font-bold text-accent-amber">
                        {immuneStatus.threats?.detected_24h || 0}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">Blocked</p>
                      <p className="text-xl font-bold text-accent-red">
                        {immuneStatus.threats?.blocked_24h || 0}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">Active</p>
                      <p className="text-xl font-bold text-accent-cyan">
                        {immuneStatus.threats?.active || 0}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">False Positives</p>
                      <p className="text-xl font-bold text-gray-400">
                        {immuneStatus.threats?.false_positives_24h || 0}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Responses (24h)</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">Auto Responses</p>
                      <p className="text-xl font-bold text-accent-green">
                        {immuneStatus.responses?.auto_24h || 0}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">Manual Reviews</p>
                      <p className="text-xl font-bold text-primary-400">
                        {immuneStatus.responses?.manual_24h || 0}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">Quarantined IPs</p>
                      <p className="text-xl font-bold text-accent-red">
                        {immuneStatus.quarantine?.ips || 0}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400">Quarantined Users</p>
                      <p className="text-xl font-bold text-accent-amber">
                        {immuneStatus.quarantine?.users || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Threat Patterns */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Threat Patterns ({immunePatterns.length})</h3>
                  <button
                    onClick={() => refetchImmune()}
                    className="btn btn-secondary btn-sm flex items-center gap-2"
                  >
                    <RefreshCw size={14} />
                    Refresh
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {immunePatterns.map((pattern: {
                    id: string
                    name: string
                    display_name?: string
                    category?: string
                    severity?: string
                    detection_type?: string
                    is_active?: boolean
                    auto_respond?: boolean
                    total_detections?: number
                    last_detection?: string
                  }) => (
                    <div
                      key={pattern.id || pattern.name}
                      className={cn(
                        'p-3 rounded-lg border transition-colors',
                        pattern.is_active ? 'bg-accent-green/5 border-accent-green/30' : 'bg-gray-500/10 border-gray-500/30'
                      )}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-sm truncate" title={pattern.name}>
                          {pattern.display_name || pattern.name}
                        </p>
                        <span className={cn(
                          'text-xs px-1 py-0.5 rounded capitalize',
                          pattern.severity === 'critical' ? 'bg-accent-red/20 text-accent-red' :
                          pattern.severity === 'high' ? 'bg-accent-amber/20 text-accent-amber' :
                          pattern.severity === 'medium' ? 'bg-accent-cyan/20 text-accent-cyan' : 'bg-gray-500/20 text-gray-400'
                        )}>
                          {pattern.severity || 'low'}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mb-2 capitalize">{pattern.category?.replace('_', ' ') || 'other'}</p>
                      <div className="flex items-center justify-between text-xs">
                        <span className={cn(
                          pattern.auto_respond ? 'text-accent-green' : 'text-gray-500'
                        )}>
                          {pattern.auto_respond ? '⚡ Auto-respond' : '👁 Monitor only'}
                        </span>
                        <span className="text-gray-400">
                          {pattern.total_detections || 0} hits
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                {immunePatterns.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    <Shield className="mx-auto mb-2" size={32} />
                    <p>No threat patterns configured</p>
                  </div>
                )}
              </div>

              {/* Recent Threats */}
              {immuneThreats.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Recent Threats ({immuneThreats.length})</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {immuneThreats.slice(0, 10).map((threat: {
                      id: string
                      severity?: string
                      category?: string
                      source_ip?: string
                      source_path?: string
                      status?: string
                      detected_at?: string
                    }, idx: number) => (
                      <div
                        key={threat.id || idx}
                        className={cn(
                          'p-3 rounded-lg border',
                          threat.severity === 'critical' ? 'bg-accent-red/10 border-accent-red/30' :
                          threat.severity === 'high' ? 'bg-accent-amber/10 border-accent-amber/30' : 'bg-dark-bg border-dark-border'
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className={cn(
                              'text-xs px-2 py-0.5 rounded capitalize',
                              threat.severity === 'critical' ? 'bg-accent-red/20 text-accent-red' :
                              threat.severity === 'high' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                            )}>
                              {threat.severity || 'low'}
                            </span>
                            <span className="text-sm font-medium capitalize">{threat.category?.replace('_', ' ') || 'Unknown'}</span>
                          </div>
                          <span className="text-xs text-gray-500">
                            {threat.detected_at ? new Date(threat.detected_at).toLocaleString() : 'Unknown'}
                          </span>
                        </div>
                        <div className="mt-1 text-xs text-gray-400">
                          {threat.source_ip && <span>IP: {threat.source_ip}</span>}
                          {threat.source_path && <span className="ml-2">Path: {threat.source_path}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quarantine List */}
              {immuneQuarantine.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Quarantine ({immuneQuarantine.length})</h3>
                  <div className="space-y-2">
                    {immuneQuarantine.map((entry: {
                      id: string
                      entity_type?: string
                      entity_value?: string
                      reason?: string
                      is_permanent?: boolean
                      expires_at?: string
                      created_at?: string
                    }, idx: number) => (
                      <div
                        key={entry.id || idx}
                        className="flex items-center justify-between p-3 rounded-lg bg-accent-red/10 border border-accent-red/30"
                      >
                        <div>
                          <p className="font-medium text-sm">
                            <span className="text-gray-400 capitalize">{entry.entity_type}: </span>
                            {entry.entity_value}
                          </p>
                          <p className="text-xs text-gray-500">{entry.reason || 'No reason specified'}</p>
                        </div>
                        <span className={cn(
                          'text-xs px-2 py-1 rounded',
                          entry.is_permanent ? 'bg-accent-red/20 text-accent-red' : 'bg-accent-amber/20 text-accent-amber'
                        )}>
                          {entry.is_permanent ? 'Permanent' : `Expires: ${entry.expires_at ? new Date(entry.expires_at).toLocaleString() : 'Unknown'}`}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Immune Architecture */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Immune System Architecture</h3>
                <p className="text-sm text-gray-400 mb-4">
                  The IMMUNE system is the defense layer of the AI body - detecting and responding to threats,
                  suspicious patterns, and malicious activity. Like biological immunity, it learns from threats
                  and adapts its responses.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-green mb-1">Healthy = No Threats</p>
                    <p className="text-xs text-gray-400">System clear, all patterns monitoring normally</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-cyan mb-1">Alert = Low Activity</p>
                    <p className="text-xs text-gray-400">Minor suspicious activity detected, monitoring</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-amber mb-1">Elevated = Active Threats</p>
                    <p className="text-xs text-gray-400">Threats detected, auto-responses engaged</p>
                  </div>
                  <div className="p-3 rounded-lg bg-dark-bg">
                    <p className="font-medium text-accent-red mb-1">Compromised = Critical</p>
                    <p className="text-xs text-gray-400">Severe threats, manual intervention required</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

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
                              <p className="text-xs text-gray-500">{exec.duration_seconds.toFixed(1)}s</p>
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
                          {activity.duration && <span className="text-gray-500">{activity.duration.toFixed(1)}s</span>}
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

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
