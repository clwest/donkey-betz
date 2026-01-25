/**
 * Session 824: Live Metrics Dashboard
 *
 * Real-time display of system metrics from the self-awareness engine.
 * Shows component counts, body system health, activity, and remediation status.
 */

import { useState, useEffect } from 'react'
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
} from 'lucide-react'
import { cn } from '@/lib/cn'

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
            />
            <MetricCard
              icon={Bug}
              label="Spiders"
              value={data.components.spiders_registered ?? 0}
              subtext="registered"
              color="text-accent-amber"
            />
            <MetricCard
              icon={Server}
              label="Celery Tasks"
              value={data.components.celery_tasks ?? 0}
              subtext="enabled"
              color="text-accent-cyan"
            />
            <MetricCard
              icon={Database}
              label="Spider Data (24h)"
              value={data.activity.spider_entries_24h ?? 0}
              subtext="entries"
              color={data.activity.spider_entries_24h === 0 ? 'text-accent-red' : 'text-accent-green'}
              alert={data.activity.spider_entries_24h === 0}
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
            />
            <MetricCard
              icon={Brain}
              label="LLM Calls"
              value={data.activity.llm_calls_24h ?? 0}
              subtext={`$${(data.activity.llm_cost_24h ?? 0).toFixed(2)} cost`}
              color="text-accent-blue"
            />
            <MetricCard
              icon={DollarSign}
              label="Revenue (7d)"
              value={`$${(data.revenue.last_7_days ?? 0).toFixed(2)}`}
              subtext={`$${(data.revenue.total_amount ?? 0).toFixed(2)} total`}
              color={data.revenue.last_7_days === 0 ? 'text-accent-red' : 'text-accent-green'}
              alert={data.revenue.last_7_days === 0}
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
            />
          </div>

          {/* Body Systems Health */}
          <div className="card">
            <h4 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Body Systems Health
            </h4>
            <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
              {Object.entries(data.health).map(([system, health]) => (
                <div
                  key={system}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-800/50 rounded-lg"
                >
                  <BodySystemIcon system={system} />
                  <span className="text-xs text-gray-300 capitalize">{system}</span>
                  <div className="ml-auto">
                    <HealthIcon status={health.status} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Timestamp */}
          <div className="text-xs text-gray-500 text-right">
            Last updated: {new Date(data.timestamp).toLocaleString()}
          </div>
        </>
      ) : null}
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
}

function MetricCard({ icon: Icon, label, value, subtext, color, alert }: MetricCardProps) {
  return (
    <div
      className={cn(
        'card transition-all',
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
    </div>
  )
}
