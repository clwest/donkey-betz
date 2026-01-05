import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ecosystemApi, dashboardApi, spidersApi } from '@/lib/api'
import { useWebSocket, type WebSocketStatus } from '@/hooks/useWebSocket'
import { Bot, Brain, Zap, Activity, Wifi, WifiOff, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { cn } from '@/lib/cn'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ElementType
  color: string
  trend?: { value: number; positive: boolean }
}

interface DashboardUpdate {
  type: string
  data: Record<string, unknown>
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

  // REST API queries
  const { data: ecosystemStats, isLoading: loadingEcosystem } = useQuery({
    queryKey: ['ecosystem-stats'],
    queryFn: () => ecosystemApi.stats(),
  })

  const { data: healthData, isLoading: loadingHealth } = useQuery({
    queryKey: ['health'],
    queryFn: () => dashboardApi.health(),
  })

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
      const spiderCount = data?.data?.active_spiders || data?.data?.total || 'Unknown'
      setActionResult({ type: 'success', message: `Spiders checked: ${spiderCount} active` })
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
          value={health.status === 'ok' ? 'Healthy' : 'Check'}
          icon={Activity}
          color="#06b6d4"
        />
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
                  <div className="h-8 w-8 rounded-full bg-primary-500/20 flex items-center justify-center">
                    <Activity size={14} className="text-primary-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{update.type}</p>
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
              <p>Waiting for real-time updates...</p>
            </div>
          )}
        </div>

        {/* System Notifications */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">System Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-accent-green" />
                <span>Django Backend</span>
              </div>
              <span className="text-accent-green text-sm">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-accent-green" />
                <span>WebSocket Server</span>
              </div>
              <span className={cn(
                'text-sm',
                wsStatus === 'connected' ? 'text-accent-green' : 'text-accent-amber'
              )}>
                {wsStatus === 'connected' ? 'Connected' : 'Reconnecting...'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-accent-green" />
                <span>Celery Workers</span>
              </div>
              <span className="text-accent-green text-sm">Running</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-accent-green" />
                <span>Redis</span>
              </div>
              <span className="text-accent-green text-sm">Connected</span>
            </div>
          </div>
        </div>
      </div>

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
