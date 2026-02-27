import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useRuns } from '@/hooks/cockpitQueries'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { RUN_STATUS_LABEL, RUN_STATUS_TONE } from '@/components/cockpit/runs/runStatus'
import { formatRelative, formatDurationMs, formatDateTime } from '@/lib/time'
import type { RunStatus } from '@/types/cockpit'

const STATUS_OPTIONS: Array<{ value: string; label: string }> = [
  { value: '', label: 'All statuses' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'in_progress', label: 'Running' },
  { value: 'pending', label: 'Pending' },
]

export default function CockpitRunsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [agentFilter, setAgentFilter] = useState('')
  const navigate = useNavigate()

  const { data: runs = [], isLoading } = useRuns({
    hours: 24,
    limit: 50,
    status: statusFilter || undefined,
    agent: agentFilter || undefined,
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Runs</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input w-40 text-sm"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Filter by agent..."
          value={agentFilter}
          onChange={(e) => setAgentFilter(e.target.value)}
          className="input w-48 text-sm"
        />
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-4">
            <SkeletonRows count={8} />
          </div>
        ) : runs.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-10">No runs found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-border text-left text-xs text-gray-500">
                  <th className="px-4 py-3 font-medium">Task</th>
                  <th className="px-4 py-3 font-medium">Agent</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium text-right">Duration</th>
                  <th className="px-4 py-3 font-medium text-right">Tokens</th>
                  <th className="px-4 py-3 font-medium text-right">When</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr
                    key={run.id}
                    className="border-b border-dark-border/50 hover:bg-dark-border/20 cursor-pointer transition-colors"
                    onClick={() => navigate(`/cockpit/runs/${run.id}`)}
                  >
                    <td className="px-4 py-3 max-w-xs truncate text-gray-200">{run.task}</td>
                    <td className="px-4 py-3 text-gray-400 whitespace-nowrap">{run.agent_name}</td>
                    <td className="px-4 py-3">
                      <StatusPill
                        label={RUN_STATUS_LABEL[run.status as RunStatus] ?? run.status}
                        tone={RUN_STATUS_TONE[run.status as RunStatus] ?? 'gray'}
                      />
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500 tabular-nums">
                      {formatDurationMs(run.execution_time_ms)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500 tabular-nums">
                      {run.tokens_used > 0 ? run.tokens_used.toLocaleString() : '—'}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500 whitespace-nowrap" title={formatDateTime(run.created_at)}>
                      {formatRelative(run.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
