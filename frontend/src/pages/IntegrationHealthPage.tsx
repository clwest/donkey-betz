/**
 * Session 758: Integration Health & Observability Dashboard
 *
 * Shows the health status of all 6 integration context sources:
 * - Spider Data (real-time web intelligence)
 * - Learning Patterns (agent learning system)
 * - Advisor System (legendary advisor wisdom)
 * - Feedback Loop (performance tracking)
 * - Sci-Fi Context (mood, evolution, relationships)
 * - Context Injection Rate (delivery success)
 */

import { useQuery } from '@tanstack/react-query'
import { integrationHealthApi } from '@/lib/api'
import {
  Activity,
  AlertTriangle,
  Brain,
  CheckCircle,
  Clock,
  Database,
  Gauge,
  Heart,
  Network,
  RefreshCw,
  Sparkles,
  TrendingUp,
  Users,
  XCircle,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import Breadcrumb from '@/components/Breadcrumb'

// Types for API responses
interface ComponentHealth {
  status: 'healthy' | 'warning' | 'degraded' | 'error'
  total_records?: number
  last_24h?: number
  last_7d?: number
  last_capture?: string
  last_spider?: string
  total_patterns?: number
  active_teaching_agents?: number
  registered_advisors?: number
  agent_mappings?: number
  executions_7d?: number
  success_rate?: number
  active_moods?: number
  evolution_records?: number
  error?: string
}

interface HealthData {
  timestamp: string
  overall_status: 'healthy' | 'warning' | 'degraded' | 'error'
  components: Record<string, ComponentHealth>
  metrics: {
    context_injection_rate: number
    executions_24h: number
    sample_with_context?: number
    error?: string
  }
  issues: string[]
}

interface AlertData {
  timestamp: string
  alert_count: number
  alerts: Array<{
    type: string
    severity: 'warning' | 'error'
    message: string
    details?: Array<{ agent: string; time: string; task: string }>
    last_capture?: string
  }>
}

interface QualityData {
  timestamp: string
  period: string
  with_context: {
    executions: number
    success_rate: number
    avg_execution_time_ms: number
  }
  without_context: {
    executions: number
    success_rate: number
    avg_execution_time_ms: number
  }
  context_benefit: {
    success_rate_improvement: number
    time_difference_ms: number
  }
  agent_breakdown: Array<{
    agent: string
    total: number
    context_rate: number
  }>
}

const statusColors = {
  healthy: 'text-green-500 bg-green-500/10',
  warning: 'text-yellow-500 bg-yellow-500/10',
  degraded: 'text-orange-500 bg-orange-500/10',
  error: 'text-red-500 bg-red-500/10',
}

const statusIcons = {
  healthy: CheckCircle,
  warning: AlertTriangle,
  degraded: AlertTriangle,
  error: XCircle,
}

const componentIcons: Record<string, typeof Brain> = {
  spider_data: Database,
  learning_patterns: Brain,
  advisor_system: Users,
  feedback_loop: TrendingUp,
  scifi_context: Sparkles,
}

const componentLabels: Record<string, string> = {
  spider_data: 'Spider Network',
  learning_patterns: 'Learning Patterns',
  advisor_system: 'Advisor System',
  feedback_loop: 'Feedback Loop',
  scifi_context: 'Sci-Fi Context',
}

export default function IntegrationHealthPage() {
  // Fetch health data
  const { data: healthData, isLoading: healthLoading, refetch: refetchHealth } = useQuery<HealthData>({
    queryKey: ['integration-health'],
    queryFn: async () => {
      const res = await integrationHealthApi.health()
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch alerts
  const { data: alertsData, isLoading: alertsLoading } = useQuery<AlertData>({
    queryKey: ['integration-alerts'],
    queryFn: async () => {
      const res = await integrationHealthApi.alerts()
      return res.data
    },
    refetchInterval: 60000, // Refresh every minute
  })

  // Fetch quality analysis
  const { data: qualityData, isLoading: qualityLoading } = useQuery<QualityData>({
    queryKey: ['integration-quality'],
    queryFn: async () => {
      const res = await integrationHealthApi.quality()
      return res.data
    },
    refetchInterval: 60000,
  })

  const isLoading = healthLoading || alertsLoading || qualityLoading

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <Breadcrumb items={[{ label: 'Integration Health', href: '/integration-health' }]} />

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20">
              <Network className="w-8 h-8 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Integration Health</h1>
              <p className="text-gray-400">Session 758: Observability for 6 context sources</p>
            </div>
          </div>
          <button
            onClick={() => refetchHealth()}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
            Refresh
          </button>
        </div>

        {/* Overall Status Card */}
        {healthData && (
          <div className={cn(
            'p-6 rounded-xl border mb-6',
            healthData.overall_status === 'healthy' ? 'border-green-500/30 bg-green-500/5' :
            healthData.overall_status === 'warning' ? 'border-yellow-500/30 bg-yellow-500/5' :
            'border-red-500/30 bg-red-500/5'
          )}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {healthData.overall_status === 'healthy' ? (
                  <CheckCircle className="w-12 h-12 text-green-500" />
                ) : healthData.overall_status === 'warning' ? (
                  <AlertTriangle className="w-12 h-12 text-yellow-500" />
                ) : (
                  <XCircle className="w-12 h-12 text-red-500" />
                )}
                <div>
                  <h2 className="text-2xl font-bold capitalize">{healthData.overall_status}</h2>
                  <p className="text-gray-400">
                    {healthData.metrics.executions_24h} executions in last 24h
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-cyan-400">
                  {healthData.metrics.context_injection_rate}%
                </div>
                <p className="text-gray-400 text-sm">Context Injection Rate</p>
              </div>
            </div>
          </div>
        )}

        {/* Component Health Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {healthData && Object.entries(healthData.components).map(([name, component]) => {
            const StatusIcon = statusIcons[component.status] || CheckCircle
            const ComponentIcon = componentIcons[name] || Activity
            return (
              <div
                key={name}
                className={cn(
                  'p-4 rounded-xl border bg-gray-800/50',
                  component.status === 'healthy' ? 'border-green-500/30' :
                  component.status === 'warning' ? 'border-yellow-500/30' :
                  'border-red-500/30'
                )}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <ComponentIcon className="w-5 h-5 text-gray-400" />
                    <span className="font-medium">{componentLabels[name] || name}</span>
                  </div>
                  <div className={cn('p-1 rounded', statusColors[component.status])}>
                    <StatusIcon className="w-4 h-4" />
                  </div>
                </div>
                <div className="space-y-1 text-sm text-gray-400">
                  {name === 'spider_data' && (
                    <>
                      <div>Total: {component.total_records?.toLocaleString()} records</div>
                      <div>Last 24h: {component.last_24h?.toLocaleString()}</div>
                      <div>Last spider: {component.last_spider}</div>
                    </>
                  )}
                  {name === 'learning_patterns' && (
                    <>
                      <div>Total: {component.total_patterns?.toLocaleString()} patterns</div>
                      <div>Teaching agents: {component.active_teaching_agents}</div>
                    </>
                  )}
                  {name === 'advisor_system' && (
                    <>
                      <div>Advisors: {component.registered_advisors}</div>
                      <div>Agent mappings: {component.agent_mappings}</div>
                    </>
                  )}
                  {name === 'feedback_loop' && (
                    <>
                      <div>Executions (7d): {component.executions_7d?.toLocaleString()}</div>
                      <div>Success rate: {component.success_rate}%</div>
                    </>
                  )}
                  {name === 'scifi_context' && (
                    <>
                      <div>Active moods: {component.active_moods}</div>
                      <div>Evolution records: {component.evolution_records}</div>
                    </>
                  )}
                  {component.error && (
                    <div className="text-red-400 text-xs mt-2">{component.error}</div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Two-Column Layout: Alerts and Quality */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Alerts Section */}
          <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              <h3 className="text-lg font-semibold">Alerts</h3>
              {alertsData && (
                <span className={cn(
                  'px-2 py-0.5 rounded text-xs',
                  alertsData.alert_count === 0 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                )}>
                  {alertsData.alert_count}
                </span>
              )}
            </div>
            {alertsData?.alerts.length === 0 ? (
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle className="w-4 h-4" />
                <span>No alerts - all systems operational</span>
              </div>
            ) : (
              <div className="space-y-3">
                {alertsData?.alerts.map((alert, i) => (
                  <div
                    key={i}
                    className={cn(
                      'p-3 rounded-lg border',
                      alert.severity === 'error' ? 'border-red-500/30 bg-red-500/5' : 'border-yellow-500/30 bg-yellow-500/5'
                    )}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {alert.severity === 'error' ? (
                        <XCircle className="w-4 h-4 text-red-500" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-yellow-500" />
                      )}
                      <span className="font-medium">{alert.type.replace(/_/g, ' ')}</span>
                    </div>
                    <p className="text-sm text-gray-400">{alert.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Context Quality Analysis */}
          <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Gauge className="w-5 h-5 text-cyan-500" />
              <h3 className="text-lg font-semibold">Context Quality Analysis</h3>
              <span className="text-xs text-gray-500">(7 days)</span>
            </div>
            {qualityData && (
              <>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                    <div className="text-xs text-gray-400 mb-1">WITH Context</div>
                    <div className="text-2xl font-bold text-green-400">
                      {qualityData.with_context.success_rate}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {qualityData.with_context.executions} executions
                    </div>
                  </div>
                  <div className="p-3 bg-gray-700/50 rounded-lg border border-gray-600">
                    <div className="text-xs text-gray-400 mb-1">WITHOUT Context</div>
                    <div className="text-2xl font-bold text-gray-300">
                      {qualityData.without_context.success_rate}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {qualityData.without_context.executions} executions
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-center gap-2 p-3 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
                  <TrendingUp className="w-5 h-5 text-cyan-400" />
                  <span className="text-cyan-400 font-semibold">
                    +{qualityData.context_benefit.success_rate_improvement}% success with context
                  </span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Agent Context Rate Table */}
        {qualityData && qualityData.agent_breakdown.length > 0 && (
          <div className="mt-6 bg-gray-800/50 rounded-xl border border-gray-700 p-6">
            <h3 className="text-lg font-semibold mb-4">Context Rate by Agent</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-2 px-3 text-gray-400">Agent</th>
                    <th className="text-right py-2 px-3 text-gray-400">Executions</th>
                    <th className="text-right py-2 px-3 text-gray-400">Context Rate</th>
                    <th className="text-left py-2 px-3 text-gray-400">Progress</th>
                  </tr>
                </thead>
                <tbody>
                  {qualityData.agent_breakdown.map((agent) => (
                    <tr key={agent.agent} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                      <td className="py-2 px-3 font-medium">{agent.agent}</td>
                      <td className="py-2 px-3 text-right text-gray-400">{agent.total}</td>
                      <td className="py-2 px-3 text-right">
                        <span className={cn(
                          'font-medium',
                          agent.context_rate > 50 ? 'text-green-400' :
                          agent.context_rate > 0 ? 'text-yellow-400' : 'text-gray-500'
                        )}>
                          {agent.context_rate}%
                        </span>
                      </td>
                      <td className="py-2 px-3">
                        <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className={cn(
                              'h-full rounded-full',
                              agent.context_rate > 50 ? 'bg-green-500' :
                              agent.context_rate > 0 ? 'bg-yellow-500' : 'bg-gray-600'
                            )}
                            style={{ width: `${agent.context_rate}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Issues List */}
        {healthData?.issues && healthData.issues.length > 0 && (
          <div className="mt-6 bg-red-500/10 rounded-xl border border-red-500/30 p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <h3 className="text-lg font-semibold text-red-400">Issues Detected</h3>
            </div>
            <ul className="space-y-2">
              {healthData.issues.map((issue, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                  <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
