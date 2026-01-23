import { useState, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ecosystemApi, dashboardApi, spidersApi, activityApi, portfolioApi, learningApi, researchApi } from '@/lib/api'
import { useWebSocket, useSystemEvents, type WebSocketStatus } from '@/hooks/useWebSocket'
import { Bot, Brain, Zap, Activity, Wifi, WifiOff, Loader2, CheckCircle, XCircle, Users, TrendingUp, Gauge, Lightbulb, Link2, Rocket, DollarSign, ArrowUpRight, GitBranch } from 'lucide-react'
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
        <span className="text-lg font-bold" style={{ color }}>{(value ?? 0).toFixed(1)}%</span>
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

  // Session 745: Revenue dashboard widget
  const { data: revenueData } = useQuery({
    queryKey: ['dashboard-revenue'],
    queryFn: () => portfolioApi.revenueDashboard(),
  })

  // Session 745: Learning velocity widget
  const { data: velocityData } = useQuery({
    queryKey: ['dashboard-velocity'],
    queryFn: () => learningApi.velocity(),
  })

  // Session 745: Network graph data
  const { data: networkData, isLoading: networkLoading } = useQuery({
    queryKey: ['dashboard-network-graph'],
    queryFn: () => researchApi.networkGraph(),
    staleTime: 60000, // Cache for 1 minute
  })

  // Session 774: Personalized greeting + "While You Were Away"
  const { data: summaryData } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => dashboardApi.summary(),
    staleTime: 300000, // Cache for 5 minutes
  })

  // Session 780: Connect previously unused dashboard endpoints
  const { data: dashboardStatsData } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.stats(),
    staleTime: 60000, // Cache for 1 minute
  })

  const { data: liveAgentData } = useQuery({
    queryKey: ['dashboard-live-agents'],
    queryFn: () => dashboardApi.liveAgentActivity(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: advisorInsightsData } = useQuery({
    queryKey: ['dashboard-advisor-insights'],
    queryFn: () => dashboardApi.advisorInsights(),
    staleTime: 120000, // Cache for 2 minutes
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
  // Session 774: Personalized summary data
  const summary = summaryData?.data || {}
  const whileAway = summary.while_away || {}
  // Session 780: Extended dashboard stats (previously unused endpoint)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const dashboardStats = (dashboardStatsData as any)?.data || (dashboardStatsData as any) || {}
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const liveAgents = (liveAgentData as any)?.data?.agents || (liveAgentData as any)?.agents || []
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const advisorInsights = (advisorInsightsData as any)?.data?.insights || (advisorInsightsData as any)?.insights || []
  // Session 745: Revenue and velocity data
  const revenue = revenueData?.data?.dashboard || revenueData?.data || {}
  // Session 745: Transform velocity API response to expected format
  const velocityDashboard = velocityData?.data?.dashboard || {}
  const velocity = {
    rate: velocityDashboard.overall_health?.score || 0,
    today: velocityDashboard.daily_velocity?.[0]?.total_weight || 0,
    this_week: velocityDashboard.weekly_summary?.[0]?.total_weight || 0,
    trend: velocityDashboard.velocity_trend?.rate || 0,
    status: velocityDashboard.overall_health?.status || 'unknown',
  }
  // Session 745: Network graph summary
  const networkNodes = networkData?.data?.nodes || []
  const networkEdges = networkData?.data?.edges || []
  const activeNodes = networkNodes.filter((n: { is_recently_active?: boolean }) => n.is_recently_active).length
  const topCategories = networkNodes.reduce((acc: Record<string, number>, n: { category?: string }) => {
    const cat = n.category || 'Other'
    acc[cat] = (acc[cat] || 0) + 1
    return acc
  }, {} as Record<string, number>)

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

  // Session 774: Calculate if any activity happened while away
  const hasAwayActivity = Object.values(whileAway).some((v) => typeof v === 'number' && v > 0)

  return (
    <div className="space-y-6">
      {/* Session 774: Personalized Greeting + While You Were Away */}
      {summary.user_name && (
        <div className="card bg-gradient-to-r from-primary-500/10 to-accent-purple/10 border-primary-500/30">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold">
                Welcome back, {summary.user_name}!
              </h1>
              {hasAwayActivity && (
                <p className="text-gray-400 mt-1">Here's what happened while you were away:</p>
              )}
            </div>
            <ConnectionBadge status={wsStatus} />
          </div>
          {hasAwayActivity && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">
              {whileAway.new_spider_data > 0 && (
                <div className="flex items-center gap-2 bg-dark-bg rounded-lg px-3 py-2">
                  <Brain size={16} className="text-accent-green" />
                  <span className="text-sm"><strong>{whileAway.new_spider_data}</strong> spider data points</span>
                </div>
              )}
              {whileAway.agent_dreams > 0 && (
                <div className="flex items-center gap-2 bg-dark-bg rounded-lg px-3 py-2">
                  <Lightbulb size={16} className="text-accent-purple" />
                  <span className="text-sm"><strong>{whileAway.agent_dreams}</strong> agent dreams</span>
                </div>
              )}
              {whileAway.agent_conversations > 0 && (
                <div className="flex items-center gap-2 bg-dark-bg rounded-lg px-3 py-2">
                  <Users size={16} className="text-accent-cyan" />
                  <span className="text-sm"><strong>{whileAway.agent_conversations}</strong> conversations</span>
                </div>
              )}
              {whileAway.new_opportunities > 0 && (
                <div className="flex items-center gap-2 bg-dark-bg rounded-lg px-3 py-2">
                  <TrendingUp size={16} className="text-accent-gold" />
                  <span className="text-sm"><strong>{whileAway.new_opportunities}</strong> opportunities</span>
                </div>
              )}
              {whileAway.images_created > 0 && (
                <div className="flex items-center gap-2 bg-dark-bg rounded-lg px-3 py-2">
                  <Zap size={16} className="text-accent-pink" />
                  <span className="text-sm"><strong>{whileAway.images_created}</strong> images created</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Header with connection status (fallback if no summary) */}
      {!summary.user_name && (
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">System Overview</h1>
          <ConnectionBadge status={wsStatus} />
        </div>
      )}

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

      {/* Session 745: Revenue & Learning Velocity Widgets */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Revenue Widget */}
        <div
          className="card cursor-pointer hover:border-accent-green/50 transition-colors"
          onClick={() => navigate('/portfolio')}
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <DollarSign className="text-accent-green" size={20} />
              Revenue
            </h3>
            <ArrowUpRight size={16} className="text-gray-400" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-2xl font-bold text-accent-green">
                ${((revenue.total || 0) / 1000).toFixed(1)}k
              </p>
              <p className="text-xs text-gray-400">Total</p>
            </div>
            <div>
              <p className="text-xl font-bold">
                ${((revenue.this_month || 0) / 1000).toFixed(1)}k
              </p>
              <p className="text-xs text-gray-400">This Month</p>
            </div>
            <div>
              <p className="text-xl font-bold text-accent-amber">
                ${((revenue.pending || 0) / 1000).toFixed(1)}k
              </p>
              <p className="text-xs text-gray-400">Pending</p>
            </div>
          </div>
          {revenue.growth_percent !== undefined && (
            <div className="mt-3 flex items-center gap-2">
              <TrendingUp size={14} className={revenue.growth_percent >= 0 ? 'text-accent-green' : 'text-accent-red'} />
              <span className={cn(
                'text-sm',
                revenue.growth_percent >= 0 ? 'text-accent-green' : 'text-accent-red'
              )}>
                {revenue.growth_percent >= 0 ? '+' : ''}{revenue.growth_percent}% vs last month
              </span>
            </div>
          )}
        </div>

        {/* Learning Velocity Widget */}
        <div
          className="card cursor-pointer hover:border-primary-500/50 transition-colors"
          onClick={() => navigate('/agents')}
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <TrendingUp className="text-primary-400" size={20} />
              Learning Velocity
            </h3>
            <ArrowUpRight size={16} className="text-gray-400" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-2xl font-bold text-primary-400">
                {velocity.rate?.toFixed(1) || '0.0'}
              </p>
              <p className="text-xs text-gray-400">Learn/Hour</p>
            </div>
            <div>
              <p className="text-xl font-bold">
                {velocity.today || 0}
              </p>
              <p className="text-xs text-gray-400">Today</p>
            </div>
            <div>
              <p className="text-xl font-bold">
                {velocity.this_week || 0}
              </p>
              <p className="text-xs text-gray-400">This Week</p>
            </div>
          </div>
          {velocity.trend !== undefined && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                <span>Trend</span>
                <span className={velocity.trend >= 0 ? 'text-accent-green' : 'text-accent-red'}>
                  {velocity.trend >= 0 ? '+' : ''}{velocity.trend}%
                </span>
              </div>
              <div className="h-1.5 bg-dark-bg rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary-500 to-accent-cyan rounded-full transition-all"
                  style={{ width: `${Math.min(Math.max((velocity.rate || 0) * 10, 5), 100)}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Session 780: Extended Dashboard Stats - Previously Unused Data */}
      {dashboardStats.total_revenue !== undefined && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="text-accent-gold" size={20} />
            Performance Overview
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <MiniStat
              title="Total Revenue"
              value={`$${((dashboardStats.total_revenue || 0) / 1000).toFixed(1)}k`}
              icon={DollarSign}
              color="#22c55e"
            />
            <MiniStat
              title="Active Opportunities"
              value={dashboardStats.active_opportunities || 0}
              icon={TrendingUp}
              color="#f59e0b"
            />
            <MiniStat
              title="Success Rate"
              value={`${dashboardStats.success_rate || 0}%`}
              icon={CheckCircle}
              color="#8b5cf6"
            />
            <MiniStat
              title="Executions (24h)"
              value={dashboardStats.agent_executions_24h || 0}
              icon={Zap}
              color="#06b6d4"
            />
            <MiniStat
              title="Spider Data (24h)"
              value={(dashboardStats.spider_data_points || 0).toLocaleString()}
              icon={Brain}
              color="#22c55e"
            />
            <MiniStat
              title="Collaborations (7d)"
              value={dashboardStats.recent_collaborations || 0}
              icon={Users}
              color="#ec4899"
            />
          </div>
          {/* AI Usage Stats */}
          {(dashboardStats.token_usage_24h > 0 || dashboardStats.ai_cost_24h > 0) && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <h4 className="text-sm text-gray-400 mb-2">AI Usage (24h)</h4>
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <Zap size={14} className="text-accent-amber" />
                  <span className="text-sm">{(dashboardStats.token_usage_24h || 0).toLocaleString()} tokens</span>
                </div>
                <div className="flex items-center gap-2">
                  <DollarSign size={14} className="text-accent-green" />
                  <span className="text-sm">${(dashboardStats.ai_cost_24h || 0).toFixed(2)} cost</span>
                </div>
              </div>
            </div>
          )}
          {/* Top Agents */}
          {dashboardStats.top_agents?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <h4 className="text-sm text-gray-400 mb-2">Top Performing Agents</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {dashboardStats.top_agents.slice(0, 6).map((agent: { name: string; type: string; executions: number; success_rate: number }, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded bg-dark-bg">
                    <div className="flex items-center gap-2">
                      <Bot size={14} className="text-primary-400" />
                      <span className="text-sm truncate max-w-[120px]">{agent.name.replace('Agent', '')}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-gray-400">{agent.executions}</span>
                      <span className="text-accent-green">{(agent.success_rate ?? 0).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Session 780: Live Agent Activity - Previously Unused Endpoint */}
      {liveAgents.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Activity className="text-accent-cyan" size={20} />
              Live Agent Activity
              <span className="h-2 w-2 rounded-full bg-accent-green animate-pulse" />
            </h3>
            <span className="text-xs text-gray-400">{liveAgents.length} agents</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {liveAgents.slice(0, 9).map((agent: { id: number; name: string; type: string; status: string; current_task?: string; collaborating_with?: string[]; metrics?: { tasks_completed?: number; success_rate?: number } }) => (
              <div
                key={agent.id}
                className={cn(
                  'p-3 rounded-lg border',
                  agent.status === 'active'
                    ? 'bg-accent-green/5 border-accent-green/30'
                    : 'bg-dark-bg border-dark-border'
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Bot size={16} className={agent.status === 'active' ? 'text-accent-green' : 'text-gray-400'} />
                    <span className="font-medium text-sm truncate max-w-[120px]">{agent.name.replace('Agent', '')}</span>
                  </div>
                  <span className={cn(
                    'px-2 py-0.5 text-xs rounded-full',
                    agent.status === 'active' ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                  )}>
                    {agent.status}
                  </span>
                </div>
                {agent.current_task && (
                  <p className="text-xs text-gray-400 truncate mb-1">{agent.current_task}</p>
                )}
                {agent.collaborating_with && agent.collaborating_with.length > 0 && (
                  <div className="flex items-center gap-1 text-xs text-accent-cyan">
                    <Users size={10} />
                    <span>with {agent.collaborating_with.join(', ')}</span>
                  </div>
                )}
                {agent.metrics && (
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span>{agent.metrics.tasks_completed || 0} tasks</span>
                    <span>{(agent.metrics.success_rate || 0).toFixed(0)}% success</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Session 780: Advisor Insights - Previously Unused Endpoint */}
      {advisorInsights.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Lightbulb className="text-accent-gold" size={20} />
              Advisor Insights
            </h3>
            <button
              className="text-sm text-gray-400 hover:text-white flex items-center gap-1"
              onClick={() => navigate('/advisors')}
            >
              View All <ArrowUpRight size={14} />
            </button>
          </div>
          <div className="space-y-3">
            {advisorInsights.slice(0, 4).map((insight: { advisor: { name: string; title: string; expertise: string; avatar?: string }; insight: string; confidence: number; category: string; actionable: boolean; created_at: string }, idx: number) => (
              <div key={idx} className="p-3 rounded-lg bg-dark-bg border-l-2 border-accent-gold/50">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {insight.advisor.avatar ? (
                      <img src={insight.advisor.avatar} alt="" className="w-8 h-8 rounded-full" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-accent-gold/20 flex items-center justify-center">
                        <Users size={14} className="text-accent-gold" />
                      </div>
                    )}
                    <div>
                      <p className="font-medium text-sm">{insight.advisor.name}</p>
                      <p className="text-xs text-gray-500">{insight.advisor.title}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {insight.actionable && (
                      <span className="px-2 py-0.5 text-xs rounded-full bg-accent-green/20 text-accent-green">
                        Actionable
                      </span>
                    )}
                    <span className="text-xs text-gray-500">{((insight.confidence ?? 0) * 100).toFixed(0)}% conf</span>
                  </div>
                </div>
                <p className="text-sm text-gray-300">{insight.insight}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="px-2 py-0.5 text-xs rounded-full bg-dark-card text-gray-400">{insight.category}</span>
                  <span className="text-xs text-gray-500">{new Date(insight.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Session 746: Enhanced Agent Network Widget with Mini Visualization */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <GitBranch className="text-accent-purple" size={20} />
            Agent Network
          </h3>
          <button
            className="text-sm text-gray-400 hover:text-white flex items-center gap-1"
            onClick={() => navigate('/agents')}
          >
            View All <ArrowUpRight size={14} />
          </button>
        </div>
        {networkLoading ? (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="animate-spin" size={20} />
          </div>
        ) : (
          <>
            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center p-3 bg-dark-bg rounded-lg">
                <p className="text-2xl font-bold text-accent-purple">{networkNodes.length}</p>
                <p className="text-xs text-gray-400">Total Agents</p>
              </div>
              <div className="text-center p-3 bg-dark-bg rounded-lg">
                <p className="text-2xl font-bold text-accent-green">{activeNodes}</p>
                <p className="text-xs text-gray-400">Active (24h)</p>
              </div>
              <div className="text-center p-3 bg-dark-bg rounded-lg">
                <p className="text-2xl font-bold text-accent-cyan">{networkEdges.length}</p>
                <p className="text-xs text-gray-400">Connections</p>
              </div>
              <div className="text-center p-3 bg-dark-bg rounded-lg">
                <p className="text-2xl font-bold text-accent-amber">{Object.keys(topCategories).length}</p>
                <p className="text-xs text-gray-400">Categories</p>
              </div>
            </div>

            {/* Mini Network Visualization */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              {/* Top Active Agents */}
              <div className="bg-dark-bg rounded-lg p-3">
                <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                  <Zap size={14} className="text-accent-amber" />
                  Top Active Agents
                </h4>
                <div className="space-y-2">
                  {networkNodes
                    .filter((n: { is_recently_active?: boolean; total_executions?: number }) => n.is_recently_active)
                    .sort((a: { total_executions?: number }, b: { total_executions?: number }) => (b.total_executions || 0) - (a.total_executions || 0))
                    .slice(0, 5)
                    .map((node: { id: string; name: string; category?: string; color?: string; total_executions?: number; effectiveness?: number }) => (
                      <div key={node.id} className="flex items-center justify-between p-2 rounded bg-dark-card">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: node.color || '#6366f1' }}
                          />
                          <span className="text-sm truncate max-w-[140px]">{node.name.replace('Agent', '')}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-gray-400">{node.total_executions || 0} runs</span>
                          {(node.effectiveness || 0) > 0 && (
                            <span className="text-accent-green">{((node.effectiveness || 0) * 100).toFixed(0)}%</span>
                          )}
                        </div>
                      </div>
                    ))}
                  {networkNodes.filter((n: { is_recently_active?: boolean }) => n.is_recently_active).length === 0 && (
                    <p className="text-xs text-gray-500 text-center py-2">No recently active agents</p>
                  )}
                </div>
              </div>

              {/* Recent Connections */}
              <div className="bg-dark-bg rounded-lg p-3">
                <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                  <Link2 size={14} className="text-accent-cyan" />
                  Active Connections
                </h4>
                <div className="space-y-2">
                  {networkEdges
                    .filter((e: { has_recent_transfer?: boolean; total_transfers?: number }) => e.has_recent_transfer || (e.total_transfers || 0) > 0)
                    .sort((a: { total_transfers?: number }, b: { total_transfers?: number }) => (b.total_transfers || 0) - (a.total_transfers || 0))
                    .slice(0, 5)
                    .map((edge: { source: string; target: string; strength?: number; learning_type?: string; total_transfers?: number; has_recent_transfer?: boolean }, idx: number) => {
                      const sourceNode = networkNodes.find((n: { id: string }) => n.id === edge.source)
                      const targetNode = networkNodes.find((n: { id: string }) => n.id === edge.target)
                      return (
                        <div key={`${edge.source}-${edge.target}-${idx}`} className="flex items-center justify-between p-2 rounded bg-dark-card">
                          <div className="flex items-center gap-1 flex-1 min-w-0">
                            <span className="text-xs truncate max-w-[80px]" title={sourceNode?.name}>
                              {sourceNode?.name?.replace('Agent', '') || 'Unknown'}
                            </span>
                            <span className="text-accent-cyan">→</span>
                            <span className="text-xs truncate max-w-[80px]" title={targetNode?.name}>
                              {targetNode?.name?.replace('Agent', '') || 'Unknown'}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {edge.has_recent_transfer && (
                              <span className="h-1.5 w-1.5 rounded-full bg-accent-green animate-pulse" />
                            )}
                            <span className="text-xs text-gray-400">{edge.total_transfers || 0}x</span>
                            {/* Connection strength bar */}
                            <div className="w-12 h-1.5 bg-dark-border rounded overflow-hidden">
                              <div
                                className="h-full bg-accent-cyan"
                                style={{ width: `${Math.min((edge.strength || 0.5) * 100, 100)}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  {networkEdges.filter((e: { total_transfers?: number }) => (e.total_transfers || 0) > 0).length === 0 && (
                    <p className="text-xs text-gray-500 text-center py-2">No active knowledge transfers</p>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
        {/* Category Tags */}
        {!networkLoading && Object.keys(topCategories).length > 0 && (
          <div className="flex flex-wrap gap-2">
            {(Object.entries(topCategories) as [string, number][])
              .sort((a, b) => b[1] - a[1])
              .slice(0, 8)
              .map(([category, count]) => (
                <span
                  key={category}
                  className="px-2 py-1 text-xs rounded-full bg-dark-bg text-gray-300"
                >
                  {category}: {count}
                </span>
              ))}
          </div>
        )}
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
