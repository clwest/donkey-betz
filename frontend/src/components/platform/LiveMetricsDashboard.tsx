/**
 * Session 824: Live Metrics Dashboard
 *
 * Real-time display of system metrics from the self-awareness engine.
 * Shows component counts, body system health, activity, and remediation status.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  Bot,
  Bug,
  Database,
  Heart,
  RefreshCw,
  Server,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  Brain,
  Wind,
  Cog,
  X,
  TrendingUp,
  Clock,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Session 834: Types for detail modals
interface MetricDetail {
  label: string
  value: number | string
  subtext: string
  icon: React.ElementType
  color: string
  type: 'agents' | 'spiders' | 'tasks' | 'data' | 'executions' | 'llm' | 'revenue' | 'findings'
}

interface BodySystemDetail {
  system: string
  status: string
  health_score?: number
  error?: string
}

interface LiveMetrics {
  timestamp: string
  components: {
    agents_in_db?: number
    active_agents?: number
    spiders_registered?: number
    celery_tasks?: number
    advisors?: number
    agents_error?: string
    spiders_error?: string
    celery_tasks_error?: string
  }
  health: {
    [key: string]: {
      status: string
      health_score?: number
      error?: string
    }
  }
  activity: {
    agent_executions_24h?: number
    successful_executions_24h?: number
    failed_executions_24h?: number
    spider_entries_24h?: number
    workspace_operations_24h?: number
    llm_calls_24h?: number
    llm_cost_24h?: number
    memories_created_24h?: number
  }
  errors: {
    top_failing_agents?: Array<{ agent_name: string; count: number }>
  }
  revenue: {
    total_amount?: number
    last_7_days?: number
  }
  remediation: {
    open_findings?: number
    fixed_findings?: number
    findings_by_status?: Record<string, number>
    tasks_by_status?: Record<string, number>
  }
}

async function fetchLiveMetrics(): Promise<LiveMetrics> {
  const response = await fetch('/api/platform/live-metrics/', {
    credentials: 'include',
  })
  if (!response.ok) throw new Error('Failed to fetch metrics')
  const data = await response.json()
  return data.metrics
}

function HealthIcon({ status }: { status: string }) {
  const color =
    status === 'healthy' || status === 'focused'
      ? 'text-accent-green'
      : status === 'error' || status === 'damaged'
        ? 'text-accent-red'
        : status === 'unknown' || status === 'not_checked'
          ? 'text-gray-500'
          : 'text-accent-amber'

  const Icon =
    status === 'healthy' || status === 'focused'
      ? CheckCircle
      : status === 'error' || status === 'damaged'
        ? XCircle
        : AlertTriangle

  return <Icon size={14} className={color} />
}

function BodySystemIcon({ system }: { system: string }) {
  const iconMap: Record<string, React.ElementType> = {
    heart: Heart,
    lungs: Wind,
    brain: Brain,
    skin: Cog,
    spine: Server,
    immune: Bug,
    digestive: Database,
    muscular: Activity,
    circulatory: RefreshCw,
  }
  const Icon = iconMap[system] || Activity
  return <Icon size={14} />
}

export function LiveMetricsDashboard() {
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState<MetricDetail | null>(null)
  const [selectedBodySystem, setSelectedBodySystem] = useState<BodySystemDetail | null>(null)

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['live-metrics'],
    queryFn: fetchLiveMetrics,
    refetchInterval: autoRefresh ? 60000 : false, // 60 seconds
    staleTime: 30000,
  })

  if (error) {
    return (
      <div className="card border-accent-red/50">
        <div className="flex items-center gap-2 text-accent-red">
          <XCircle size={18} />
          <span>Failed to load live metrics</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="text-primary-400" size={18} />
          <h3 className="text-md font-semibold uppercase">Live System Metrics</h3>
          {isFetching && <Loader2 size={14} className="animate-spin text-gray-500" />}
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-600 bg-gray-800 text-primary-500 focus:ring-primary-500"
            />
            Auto-refresh (60s)
          </label>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-1.5 hover:bg-gray-700 rounded transition-colors disabled:opacity-50"
          >
            <RefreshCw size={14} className={cn(isFetching && 'animate-spin')} />
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-700 rounded w-1/2 mb-2" />
              <div className="h-8 bg-gray-700 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : data ? (
        <>
          {/* Components Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard
              icon={Bot}
              label="Agents"
              value={data.components.active_agents ?? 0}
              subtext={`of ${data.components.agents_in_db ?? 0} total`}
              color="text-primary-400"
              onClick={() => setSelectedMetric({
                label: 'Agents',
                value: data.components.active_agents ?? 0,
                subtext: `${data.components.agents_in_db ?? 0} total in database`,
                icon: Bot,
                color: 'text-primary-400',
                type: 'agents'
              })}
            />
            <MetricCard
              icon={Bug}
              label="Spiders"
              value={data.components.spiders_registered ?? 0}
              subtext="registered"
              color="text-accent-amber"
              onClick={() => setSelectedMetric({
                label: 'Spiders',
                value: data.components.spiders_registered ?? 0,
                subtext: 'Data collection spiders registered',
                icon: Bug,
                color: 'text-accent-amber',
                type: 'spiders'
              })}
            />
            <MetricCard
              icon={Server}
              label="Celery Tasks"
              value={data.components.celery_tasks ?? 0}
              subtext="enabled"
              color="text-accent-cyan"
              onClick={() => setSelectedMetric({
                label: 'Celery Tasks',
                value: data.components.celery_tasks ?? 0,
                subtext: 'Background tasks enabled',
                icon: Server,
                color: 'text-accent-cyan',
                type: 'tasks'
              })}
            />
            <MetricCard
              icon={Database}
              label="Spider Data (24h)"
              value={data.activity.spider_entries_24h ?? 0}
              subtext="entries"
              color={data.activity.spider_entries_24h === 0 ? 'text-accent-red' : 'text-accent-green'}
              alert={data.activity.spider_entries_24h === 0}
              onClick={() => setSelectedMetric({
                label: 'Spider Data (24h)',
                value: data.activity.spider_entries_24h ?? 0,
                subtext: 'Data entries collected in last 24 hours',
                icon: Database,
                color: data.activity.spider_entries_24h === 0 ? 'text-accent-red' : 'text-accent-green',
                type: 'data'
              })}
            />
          </div>

          {/* Activity Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard
              icon={Activity}
              label="Agent Executions"
              value={data.activity.agent_executions_24h ?? 0}
              subtext={`${data.activity.successful_executions_24h ?? 0} success / ${data.activity.failed_executions_24h ?? 0} failed`}
              color="text-accent-purple"
              onClick={() => setSelectedMetric({
                label: 'Agent Executions (24h)',
                value: data.activity.agent_executions_24h ?? 0,
                subtext: `${data.activity.successful_executions_24h ?? 0} successful, ${data.activity.failed_executions_24h ?? 0} failed`,
                icon: Activity,
                color: 'text-accent-purple',
                type: 'executions'
              })}
            />
            <MetricCard
              icon={Brain}
              label="LLM Calls"
              value={data.activity.llm_calls_24h ?? 0}
              subtext={`$${(data.activity.llm_cost_24h ?? 0).toFixed(2)} cost`}
              color="text-accent-blue"
              onClick={() => setSelectedMetric({
                label: 'LLM Calls (24h)',
                value: data.activity.llm_calls_24h ?? 0,
                subtext: `$${(data.activity.llm_cost_24h ?? 0).toFixed(2)} total cost`,
                icon: Brain,
                color: 'text-accent-blue',
                type: 'llm'
              })}
            />
            <MetricCard
              icon={DollarSign}
              label="Revenue (7d)"
              value={`$${(data.revenue.last_7_days ?? 0).toFixed(2)}`}
              subtext={`$${(data.revenue.total_amount ?? 0).toFixed(2)} total`}
              color={data.revenue.last_7_days === 0 ? 'text-accent-red' : 'text-accent-green'}
              alert={data.revenue.last_7_days === 0}
              onClick={() => setSelectedMetric({
                label: 'Revenue',
                value: `$${(data.revenue.last_7_days ?? 0).toFixed(2)}`,
                subtext: `$${(data.revenue.total_amount ?? 0).toFixed(2)} total revenue`,
                icon: DollarSign,
                color: data.revenue.last_7_days === 0 ? 'text-accent-red' : 'text-accent-green',
                type: 'revenue'
              })}
            />
            <MetricCard
              icon={AlertTriangle}
              label="Open Findings"
              value={data.remediation.open_findings ?? 0}
              subtext={`${data.remediation.fixed_findings ?? 0} fixed`}
              color={
                (data.remediation.open_findings ?? 0) > 100
                  ? 'text-accent-red'
                  : 'text-accent-amber'
              }
              alert={(data.remediation.open_findings ?? 0) > 100}
              onClick={() => setSelectedMetric({
                label: 'Audit Findings',
                value: data.remediation.open_findings ?? 0,
                subtext: `${data.remediation.fixed_findings ?? 0} findings fixed`,
                icon: AlertTriangle,
                color: (data.remediation.open_findings ?? 0) > 100 ? 'text-accent-red' : 'text-accent-amber',
                type: 'findings'
              })}
            />
          </div>

          {/* Body Systems Health */}
          <div className="card">
            <h4 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Body Systems Health
            </h4>
            <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
              {Object.entries(data.health).map(([system, health]) => (
                <button
                  key={system}
                  onClick={() => setSelectedBodySystem({ system, ...health })}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer"
                >
                  <BodySystemIcon system={system} />
                  <span className="text-xs text-gray-300 capitalize">{system}</span>
                  <div className="ml-auto">
                    <HealthIcon status={health.status} />
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Timestamp */}
          <div className="text-xs text-gray-500 text-right">
            Last updated: {new Date(data.timestamp).toLocaleString()}
          </div>
        </>
      ) : null}

      {/* Session 834: Metric Detail Modal */}
      {selectedMetric && (
        <MetricDetailModal metric={selectedMetric} onClose={() => setSelectedMetric(null)} />
      )}

      {/* Session 834: Body System Detail Modal */}
      {selectedBodySystem && (
        <BodySystemModal system={selectedBodySystem} onClose={() => setSelectedBodySystem(null)} />
      )}
    </div>
  )
}

interface MetricCardProps {
  icon: React.ElementType
  label: string
  value: number | string
  subtext: string
  color: string
  alert?: boolean
  onClick?: () => void
}

function MetricCard({ icon: Icon, label, value, subtext, color, alert, onClick }: MetricCardProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'card transition-all cursor-pointer hover:bg-gray-800/80 text-left w-full',
        alert && 'border-accent-red/50 bg-accent-red/5'
      )}
    >
      <div className="flex items-center gap-2 mb-1">
        <Icon size={14} className={color} />
        <span className="text-xs text-gray-400">{label}</span>
        {alert && <AlertTriangle size={12} className="text-accent-red" />}
      </div>
      <div className="text-xl font-bold text-white">{value}</div>
      <div className="text-xs text-gray-500">{subtext}</div>
    </button>
  )
}

// Session 834: Metric Detail Modal
interface MetricDetailModalProps {
  metric: MetricDetail
  onClose: () => void
}

function MetricDetailModal({ metric, onClose }: MetricDetailModalProps) {
  const Icon = metric.icon

  const getTypeDescription = () => {
    switch (metric.type) {
      case 'agents':
        return 'AI agents that perform automated tasks like analysis, content creation, and data processing.'
      case 'spiders':
        return 'Data collection crawlers that gather information from various sources like news, financial data, and tech sites.'
      case 'tasks':
        return 'Background Celery tasks that handle async operations like notifications, data processing, and scheduled jobs.'
      case 'data':
        return 'Raw data entries collected by spiders in the last 24 hours. Zero entries may indicate spider network issues.'
      case 'executions':
        return 'Number of times agents were invoked to perform tasks. High failure rates may indicate system issues.'
      case 'llm':
        return 'API calls to language models (GPT, Claude, etc.) for AI-powered features. Costs accumulate based on token usage.'
      case 'revenue':
        return 'Revenue generated through the platform from various monetization sources.'
      case 'findings':
        return 'Audit findings from self-audits that identify issues needing remediation. High numbers indicate technical debt.'
      default:
        return 'System metric tracking platform health and performance.'
    }
  }

  const getActionLink = () => {
    switch (metric.type) {
      case 'agents':
        return { href: '/agents', label: 'View All Agents' }
      case 'spiders':
        return { href: '/workspace?tab=dataintel', label: 'View Spider Network' }
      case 'findings':
        return { href: '/workspace?tab=governance', label: 'View Governance' }
      case 'revenue':
        return { href: '/human?tab=revenue', label: 'View Revenue Details' }
      default:
        return null
    }
  }

  const actionLink = getActionLink()

  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-lg', metric.color.replace('text-', 'bg-') + '/20')}>
              <Icon size={20} className={metric.color} />
            </div>
            <h2 className="text-lg font-semibold text-white">{metric.label}</h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Value Display */}
          <div className="text-center py-4 bg-gray-800/50 rounded-lg">
            <div className={cn('text-4xl font-bold', metric.color)}>{metric.value}</div>
            <div className="text-sm text-gray-400 mt-1">{metric.subtext}</div>
          </div>

          {/* Description */}
          <div className="card bg-gray-800/50">
            <p className="text-sm text-gray-300">{getTypeDescription()}</p>
          </div>

          {/* Action Link */}
          {actionLink && (
            <a
              href={actionLink.href}
              className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-primary-600 hover:bg-primary-500 rounded-lg text-sm font-medium transition-colors"
            >
              <TrendingUp size={16} />
              {actionLink.label}
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

// Session 834: Body System Detail Modal
interface BodySystemModalProps {
  system: BodySystemDetail
  onClose: () => void
}

function BodySystemModal({ system, onClose }: BodySystemModalProps) {
  const getSystemDescription = () => {
    const descriptions: Record<string, string> = {
      heart: 'The HEART system monitors core platform vitals including database connections, API health, and critical service availability.',
      lungs: 'The LUNGS system handles data ingestion and processing, breathing in new information from spiders and external sources.',
      brain: 'The BRAIN system manages AI orchestration, agent coordination, and intelligent decision-making processes.',
      skin: 'The SKIN system is the execution layer that writes files, runs code, and interfaces with external systems.',
      spine: 'The SPINE system provides the core infrastructure backbone including task queues, messaging, and service communication.',
      immune: 'The IMMUNE system handles security, audit findings, and self-healing remediation to protect platform health.',
      digestive: 'The DIGESTIVE system processes and transforms raw data into usable knowledge and insights.',
      muscular: 'The MUSCULAR system handles heavy lifting operations like batch processing, migrations, and intensive computations.',
      circulatory: 'The CIRCULATORY system manages data flow between components, ensuring information reaches where it needs to go.',
    }
    return descriptions[system.system] || 'System component monitoring platform health.'
  }

  const getStatusColor = () => {
    switch (system.status) {
      case 'healthy':
      case 'focused':
        return 'text-accent-green'
      case 'error':
      case 'damaged':
        return 'text-accent-red'
      case 'unknown':
      case 'not_checked':
        return 'text-gray-500'
      default:
        return 'text-accent-amber'
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <BodySystemIcon system={system.system} />
            <h2 className="text-lg font-semibold text-white capitalize">{system.system} System</h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Status Display */}
          <div className="text-center py-4 bg-gray-800/50 rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <HealthIcon status={system.status} />
              <span className={cn('text-xl font-bold capitalize', getStatusColor())}>
                {system.status.replace('_', ' ')}
              </span>
            </div>
            {system.health_score !== undefined && (
              <div className="text-sm text-gray-400">
                Health Score: <span className="text-white font-medium">{(system.health_score ?? 0).toFixed(1)}%</span>
              </div>
            )}
          </div>

          {/* Description */}
          <div className="card bg-gray-800/50">
            <p className="text-sm text-gray-300">{getSystemDescription()}</p>
          </div>

          {/* Error Message */}
          {system.error && (
            <div className="card bg-accent-red/10 border-accent-red/30">
              <h4 className="text-xs font-semibold text-accent-red uppercase mb-1">Error</h4>
              <p className="text-sm text-gray-300">{system.error}</p>
            </div>
          )}

          {/* Action Link */}
          <a
            href="/human"
            className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors"
          >
            <Heart size={16} />
            View Full System Health
          </a>
        </div>
      </div>
    </div>
  )
}
