import { useState, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ecosystemApi, dashboardApi, spidersApi, activityApi } from '@/lib/api'
import { useWebSocket, useSystemEvents, type WebSocketStatus } from '@/hooks/useWebSocket'
import { Bot, Brain, Zap, Activity, Wifi, WifiOff, Loader2, CheckCircle, XCircle, Users, TrendingUp, Gauge, Lightbulb, Link2, Rocket } from 'lucide-react'
import { cn } from '@/lib/cn'
import HeartWidget from '@/components/HeartWidget'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ElementType
  color: string
  trend?: { value: number; positive: boolean }
}

interface DashboardUpdate {
  type: string
  data: { subtitle?: string; icon?: string; [key: string]: unknown }
  timestamp: string
}

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

function StatCard({ title, value, icon: Icon, color, trend }: StatCardProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {trend && (
            <p className={cn(
              'text-xs mt-1',
              trend.positive ? 'text-accent-green' : 'text-accent-red'
            )}>
              {trend.positive ? '+' : ''}{trend.value}% from last hour
            </p>
          )}
        </div>
        <div
          className="h-12 w-12 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color}20` }}
        >
          <Icon size={24} style={{ color }} />
        </div>
      </div>
    </div>
  )
}

// Session 697: Mini stat card for secondary metrics
interface MiniStatProps {
  title: string
  value: string | number
  icon: React.ElementType
  color: string
}

function MiniStat({ title, value, icon: Icon, color }: MiniStatProps) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-bg">
      <div
        className="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: `${color}15` }}
      >
        <Icon size={18} style={{ color }} />
      </div>
      <div>
        <p className="text-lg font-bold" style={{ color }}>{value}</p>
        <p className="text-xs text-gray-500">{title}</p>
      </div>
    </div>
  )
}

// Session 697: Progress gauge for percentage metrics
interface GaugeStatProps {
  title: string
  value: number
  icon: React.ElementType
  color: string
}

function GaugeStat({ title, value, icon: Icon, color }: GaugeStatProps) {
  return (
    <div className="p-4 rounded-lg bg-dark-bg">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon size={16} style={{ color }} />
          <span className="text-sm text-gray-400">{title}</span>
        </div>
        <span className="text-lg font-bold" style={{ color }}>{value.toFixed(1)}%</span>
      </div>
      <div className="h-2 rounded-full bg-dark-card overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(value, 100)}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

function ConnectionBadge({ status }: { status: WebSocketStatus }) {
  const isConnected = status === 'connected'
  return (
    <div className={cn(
      'flex items-center gap-2 px-3 py-1.5 rounded-full text-xs',
      isConnected ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-amber/10 text-accent-amber'
    )}>
      {isConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
      <span>{isConnected ? 'Live' : 'Connecting...'}</span>
    </div>
  )
}

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

export default function DashboardPage() {
  const [recentActivity, setRecentActivity] = useState<DashboardUpdate[]>([])
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Session 714: Real-time event handlers - refresh data when events occur
  const handleAgentExecution = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['recent-activity'] })
    queryClient.invalidateQueries({ queryKey: ['ecosystem-stats'] })
  }, [queryClient])

  const handleBodyStatusChanged = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['health'] })
  }, [queryClient])

  const handleDreamGenerated = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['recent-activity'] })
  }, [queryClient])

  // Session 714: Subscribe to system events
  useSystemEvents({
    onAgentExecutionComplete: handleAgentExecution,
    onAgentExecutionFailed: handleAgentExecution,
    onBodyStatusChanged: handleBodyStatusChanged,
    onDreamGenerated: handleDreamGenerated,
  })

  // REST API queries
  const { data: ecosystemStats, isLoading: loadingEcosystem } = useQuery({
    queryKey: ['ecosystem-stats'],
    queryFn: () => ecosystemApi.stats(),
  })

  const { data: healthData, isLoading: loadingHealth } = useQuery({
    queryKey: ['health'],
    queryFn: () => dashboardApi.health(),
  })

  // Fetch initial recent activity
  const { data: initialActivity } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => activityApi.recent(20, 24),
  })

  // Initialize recentActivity with fetched data
  useEffect(() => {
    if (initialActivity?.data?.activities) {
      const formatted = initialActivity.data.activities.map((a: { type: string; title: string; subtitle?: string; timestamp: string; icon?: string }) => ({
        type: a.title || a.type,
        timestamp: a.timestamp,
        data: { subtitle: a.subtitle, icon: a.icon },
      }))
      setRecentActivity(formatted)
    }
  }, [initialActivity])

  // Mutations for quick actions
  const agentCycleMutation = useMutation({
    mutationFn: () => dashboardApi.runAgentCycle(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Agent cycle started successfully!' })
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to start agent cycle' })
    },
  })

  const spiderCheckMutation = useMutation({
    mutationFn: () => spidersApi.status(),
    onSuccess: (data) => {
      const d = data?.data || {}
      const spiderCount = d.spider_count || 0
      const last24h = d.last_24h_data || 0
      const totalData = d.total_data_points || 0
      setActionResult({
        type: 'success',
        message: `${spiderCount} spiders | ${last24h} collected (24h) | ${totalData.toLocaleString()} total data points`
      })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to check spider status' })
    },
  })

  const reportMutation = useMutation({
    mutationFn: () => spidersApi.report(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Intelligence report generated!' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate report' })
    },
  })

  // WebSocket for real-time dashboard updates
  const { status: wsStatus } = useWebSocket('/dashboard', {
    onMessage: (data) => {
      const update = data as DashboardUpdate
      setRecentActivity((prev) => [update, ...prev].slice(0, 20))
    },
  })

  const stats = ecosystemStats?.data || {}
  const health = healthData?.data || {}

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  if (loadingEcosystem || loadingHealth) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  const isLoading = agentCycleMutation.isPending || spiderCheckMutation.isPending || reportMutation.isPending

  return (
    <div className="space-y-6">
      {/* Header with connection status */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">System Overview</h1>
        <ConnectionBadge status={wsStatus} />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Agents"
          value={stats.total_agents || 71}
          icon={Bot}
          color="#8b5cf6"
        />
        <StatCard
          title="Active Spiders"
          value={stats.active_spiders || 77}
          icon={Brain}
          color="#22c55e"
        />
        <StatCard
          title="Celery Tasks"
          value={stats.celery_tasks || 127}
          icon={Zap}
          color="#f59e0b"
        />
        <StatCard
          title="System Health"
          value={['ok', 'healthy'].includes(health.status) ? 'Healthy' : (health.status || 'Check')}
          icon={Activity}
          color="#06b6d4"
        />
      </div>

      {/* Session 697: Intelligence Metrics - Previously Hidden Data */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Intelligence Metrics</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Left: Mini stats */}
          <div className="grid grid-cols-2 gap-3">
            <MiniStat
              title="Knowledge Transfers"
              value={(stats.stats?.knowledge_transfers || 0).toLocaleString()}
              icon={Lightbulb}
              color="#a855f7"
            />
            <MiniStat
              title="Collaborations"
              value={(stats.stats?.collaborations || 0).toLocaleString()}
              icon={Users}
              color="#ec4899"
            />
            <MiniStat
              title="Solutions Deployed"
              value={(stats.stats?.solutions_deployed || 0).toLocaleString()}
              icon={Rocket}
              color="#22c55e"
            />
            <MiniStat
              title="Active Connections"
              value={(stats.stats?.active_connections || 0).toLocaleString()}
              icon={Link2}
              color="#06b6d4"
            />
          </div>
          {/* Right: Gauges */}
          <div className="space-y-3">
            <GaugeStat
              title="System Efficiency"
              value={stats.stats?.system_efficiency || 0}
              icon={Gauge}
              color="#22c55e"
            />
            <GaugeStat
              title="Learning Rate"
              value={stats.stats?.learning_rate || 0}
              icon={TrendingUp}
              color="#8b5cf6"
            />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            className="btn btn-primary flex items-center justify-center gap-2"
            onClick={() => agentCycleMutation.mutate()}
            disabled={isLoading}
          >
            {agentCycleMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : null}
            Run Agent Cycle
          </button>
          <button
            className="btn btn-secondary flex items-center justify-center gap-2"
            onClick={() => spiderCheckMutation.mutate()}
            disabled={isLoading}
          >
            {spiderCheckMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : null}
            Check Spiders
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/intelligence')}
          >
            View Pilots
          </button>
          <button
            className="btn btn-secondary flex items-center justify-center gap-2"
            onClick={() => reportMutation.mutate()}
            disabled={isLoading}
          >
            {reportMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : null}
            Intelligence Report
          </button>
        </div>
      </div>

      {/* Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Activity</h3>
            {wsStatus === 'connected' && (
              <span className="h-2 w-2 rounded-full bg-accent-green animate-pulse" />
            )}
          </div>
          {recentActivity.length > 0 ? (
            <div className="space-y-3 max-h-[300px] overflow-auto">
              {recentActivity.map((update, idx) => (
                <div
                  key={`${update.timestamp}-${idx}`}
                  className="flex items-center gap-3 p-2 rounded-lg bg-dark-bg"
                >
                  <div className="h-8 w-8 rounded-full bg-primary-500/20 flex items-center justify-center text-sm">
                    {update.data?.icon || <Activity size={14} className="text-primary-400" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{update.type}</p>
                    {update.data?.subtitle && (
                      <p className="text-xs text-gray-400 truncate">{update.data.subtitle}</p>
                    )}
                    <p className="text-xs text-gray-500">
                      {new Date(update.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-400 text-sm text-center py-8">
              <Activity className="mx-auto mb-2 opacity-50" size={24} />
              <p>No recent activity</p>
            </div>
          )}
        </div>

        {/* HEART Service - System Health (Session 702) */}
        <HeartWidget />
      </div>

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
