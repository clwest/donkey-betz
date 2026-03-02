import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useOpsRuns } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { OpsRunStatus, OpsRunType } from '@/types/cockpit'
import { Activity } from 'lucide-react'
import { cn } from '@/lib/cn'

const STATUS_TONE: Record<OpsRunStatus, Tone> = {
  running: 'blue',
  passed: 'green',
  failed: 'red',
  partial: 'amber',
}

const TYPE_LABEL: Record<OpsRunType, string> = {
  ops_loop: 'Ops Loop',
  smoke_test: 'Smoke Test',
  deploy_verify: 'Deploy Verify',
  manual: 'Manual',
}

function RelTime({ iso }: { iso: string | null }) {
  if (!iso) return <span className="text-gray-600">&mdash;</span>
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60_000)
  if (mins < 1) return <span className="text-gray-400">just now</span>
  if (mins < 60) return <span className="text-gray-400">{mins}m ago</span>
  const hrs = Math.round(mins / 60)
  if (hrs < 24) return <span className="text-gray-400">{hrs}h ago</span>
  return <span className="text-gray-400">{Math.round(hrs / 24)}d ago</span>
}

function Duration({ start, end }: { start: string; end: string | null }) {
  if (!end) return <span className="text-blue-400 text-xs">running...</span>
  const ms = new Date(end).getTime() - new Date(start).getTime()
  if (ms < 1000) return <span className="text-gray-400">{ms}ms</span>
  return <span className="text-gray-400">{(ms / 1000).toFixed(1)}s</span>
}

export default function OpsRunsPage() {
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data, isLoading } = useOpsRuns({
    run_type: typeFilter || undefined,
    status: statusFilter || undefined,
    hours: 72,
    limit: 100,
  })

  const items = data?.items ?? []
  const total = data?.total ?? 0

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Activity size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Ops Runs</h1>
        {total > 0 && (
          <span className="px-2 py-0.5 rounded-full bg-dark-border text-xs text-gray-400">
            {total}
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex gap-1">
          {(['', 'ops_loop', 'smoke_test', 'deploy_verify', 'manual'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={cn(
                'px-3 py-1.5 text-xs rounded transition-colors',
                typeFilter === t
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-border text-gray-400 hover:text-gray-200',
              )}
            >
              {t ? TYPE_LABEL[t] : 'All Types'}
            </button>
          ))}
        </div>
        <div className="flex gap-1">
          {(['', 'running', 'passed', 'failed', 'partial'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={cn(
                'px-3 py-1.5 text-xs rounded transition-colors',
                statusFilter === s
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-border text-gray-400 hover:text-gray-200',
              )}
            >
              {s || 'All Status'}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="card p-6"><SkeletonRows count={6} /></div>
      ) : items.length === 0 ? (
        <div className="card p-12 text-center text-gray-500">
          No ops runs found in the last 72 hours.
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                <th className="p-3">Status</th>
                <th className="p-3">Title</th>
                <th className="p-3">Type</th>
                <th className="p-3">Triggered By</th>
                <th className="p-3">Events</th>
                <th className="p-3">Fails</th>
                <th className="p-3">Duration</th>
                <th className="p-3">Started</th>
              </tr>
            </thead>
            <tbody>
              {items.map((run) => (
                <tr key={run.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                  <td className="p-3">
                    <StatusPill label={run.status} tone={STATUS_TONE[run.status] ?? 'gray'} />
                  </td>
                  <td className="p-3">
                    <Link
                      to={`/cockpit/ops-runs/${run.id}`}
                      className="text-gray-200 hover:text-primary-400 transition-colors"
                    >
                      {run.title}
                    </Link>
                  </td>
                  <td className="p-3 text-gray-400">{TYPE_LABEL[run.run_type] ?? run.run_type}</td>
                  <td className="p-3 text-gray-400">{run.triggered_by}</td>
                  <td className="p-3 text-gray-400">{run.event_count}</td>
                  <td className="p-3">
                    {run.fail_count > 0 ? (
                      <span className="text-red-400">{run.fail_count}</span>
                    ) : (
                      <span className="text-gray-600">0</span>
                    )}
                  </td>
                  <td className="p-3">
                    <Duration start={run.started_at} end={run.finished_at} />
                  </td>
                  <td className="p-3"><RelTime iso={run.started_at} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
