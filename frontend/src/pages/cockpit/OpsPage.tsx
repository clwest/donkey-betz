import { useNavigate } from 'react-router-dom'
import { useOpsOverview } from '@/hooks/cockpitQueries'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { RUN_STATUS_LABEL, RUN_STATUS_TONE } from '@/components/cockpit/runs/runStatus'
import { formatRelative, formatDateTime, formatDurationMs } from '@/lib/time'
import type { HealthTone, RunStatus } from '@/types/cockpit'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import { Wrench, Activity, AlertTriangle, Play } from 'lucide-react'

const toneMap: Record<HealthTone, Tone> = {
  green: 'green',
  amber: 'amber',
  red: 'red',
  gray: 'gray',
}

export default function CockpitOpsPage() {
  const navigate = useNavigate()
  const { data, isLoading } = useOpsOverview({ hours: 24, limit: 5 })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Ops</h1>
        <div className="card p-6"><SkeletonRows count={8} /></div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Ops</h1>
        <div className="card p-6 text-center text-gray-500">Failed to load ops data</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Wrench size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Ops</h1>
        <StatusPill label={data.health.overall_tone} tone={toneMap[data.health.overall_tone]} />
      </div>

      {/* Health checks grid */}
      <div>
        <h2 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-1.5">
          <Activity size={14} /> Health Checks
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {data.health.checks.map((check) => (
            <div key={check.key} className="card px-4 py-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-200">{check.label}</span>
                <StatusPill label={check.status} tone={toneMap[check.tone as HealthTone] ?? 'gray'} />
              </div>
              <p className="text-xs text-gray-500">{check.detail}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Top failing agents */}
      {data.top_failing_agents.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-1.5">
            <AlertTriangle size={14} /> Top Failing Agents (24h)
          </h2>
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-border text-left text-xs text-gray-500">
                  <th className="px-4 py-2 font-medium">Agent</th>
                  <th className="px-4 py-2 font-medium text-right">Failed</th>
                  <th className="px-4 py-2 font-medium text-right">Total</th>
                  <th className="px-4 py-2 font-medium text-right">Rate</th>
                  <th className="px-4 py-2 font-medium text-right">Last Failure</th>
                </tr>
              </thead>
              <tbody>
                {data.top_failing_agents.map((agent) => (
                  <tr key={agent.agent_name} className="border-b border-dark-border/50">
                    <td className="px-4 py-2 text-gray-200">{agent.agent_name}</td>
                    <td className="px-4 py-2 text-right text-red-400 font-medium tabular-nums">{agent.failed_count}</td>
                    <td className="px-4 py-2 text-right text-gray-500 tabular-nums">{agent.total_count}</td>
                    <td className="px-4 py-2 text-right text-gray-400 tabular-nums">
                      {(agent.failure_rate * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2 text-right text-gray-500" title={agent.last_failed_at ? formatDateTime(agent.last_failed_at) : undefined}>
                      {agent.last_failed_at ? formatRelative(agent.last_failed_at) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top error signatures */}
      {data.top_error_signatures.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-1.5">
            <AlertTriangle size={14} /> Top Error Signatures
          </h2>
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-border text-left text-xs text-gray-500">
                  <th className="px-4 py-2 font-medium">Signature</th>
                  <th className="px-4 py-2 font-medium text-right">Count</th>
                  <th className="px-4 py-2 font-medium text-right">Last Seen</th>
                </tr>
              </thead>
              <tbody>
                {data.top_error_signatures.map((sig, i) => (
                  <tr
                    key={`${sig.signature}-${i}`}
                    className="border-b border-dark-border/50 hover:bg-dark-border/20 cursor-pointer transition-colors"
                    onClick={() => navigate(`/cockpit/errors/${encodeURIComponent(sig.signature)}`)}
                  >
                    <td className="px-4 py-2 text-gray-200 max-w-xs truncate">{sig.signature}</td>
                    <td className="px-4 py-2 text-right text-gray-400 tabular-nums font-medium">{sig.count}</td>
                    <td className="px-4 py-2 text-right text-gray-500" title={sig.last_seen ? formatDateTime(sig.last_seen) : undefined}>
                      {sig.last_seen ? formatRelative(sig.last_seen) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent failed runs */}
      {data.recent_failed_runs.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-1.5">
            <Play size={14} /> Recent Failed Runs
          </h2>
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-border text-left text-xs text-gray-500">
                  <th className="px-4 py-2 font-medium">Task</th>
                  <th className="px-4 py-2 font-medium">Agent</th>
                  <th className="px-4 py-2 font-medium text-right">Duration</th>
                  <th className="px-4 py-2 font-medium text-right">When</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_failed_runs.map((run) => (
                  <tr
                    key={run.id}
                    className="border-b border-dark-border/50 hover:bg-dark-border/20 cursor-pointer transition-colors"
                    onClick={() => navigate(`/cockpit/runs/${run.id}`)}
                  >
                    <td className="px-4 py-2 text-gray-200 max-w-xs truncate">{run.task}</td>
                    <td className="px-4 py-2 text-gray-400 whitespace-nowrap">{run.agent_name}</td>
                    <td className="px-4 py-2 text-right text-gray-500 tabular-nums">
                      {formatDurationMs(run.execution_time_ms)}
                    </td>
                    <td className="px-4 py-2 text-right text-gray-500" title={formatDateTime(run.created_at)}>
                      {formatRelative(run.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* All quiet */}
      {data.top_failing_agents.length === 0 && data.top_error_signatures.length === 0 && data.recent_failed_runs.length === 0 && (
        <div className="card p-8 text-center text-gray-500">
          All systems operational. No failures in the last 24 hours.
        </div>
      )}
    </div>
  )
}
