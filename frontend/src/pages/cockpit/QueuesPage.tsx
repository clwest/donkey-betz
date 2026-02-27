import { useState } from 'react'
import { useQueuesOverview } from '@/hooks/cockpitQueries'
import type { QueueWindow } from '@/lib/cockpitApi'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import { Layers, Server, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/cn'

const WINDOW_OPTIONS: { value: QueueWindow; label: string }[] = [
  { value: '15m', label: '15m' },
  { value: '60m', label: '1h' },
  { value: '2h', label: '2h' },
  { value: '6h', label: '6h' },
  { value: '24h', label: '24h' },
]

function KpiCard({ label, value, sub, tone }: { label: string; value: string | number; sub?: string; tone?: Tone }) {
  return (
    <div className="card p-4">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={cn(
        'text-2xl font-bold',
        tone === 'red' ? 'text-red-400' : tone === 'amber' ? 'text-amber-400' : tone === 'green' ? 'text-green-400' : 'text-white',
      )}>
        {value}
      </div>
      {sub && <div className="text-xs text-gray-500 mt-0.5">{sub}</div>}
    </div>
  )
}

export default function QueuesPage() {
  const [window, setWindow] = useState<QueueWindow>('60m')
  const { data, isLoading } = useQueuesOverview(window)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Queues</h1>
        <div className="card p-6"><SkeletonRows count={8} /></div>
      </div>
    )
  }

  const s = data?.summary

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Layers size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Queues & Workers</h1>
        <div className="flex rounded-lg border border-dark-border overflow-hidden ml-auto">
          {WINDOW_OPTIONS.map((o) => (
            <button
              key={o.value}
              onClick={() => setWindow(o.value)}
              className={cn(
                'px-3 py-1.5 text-xs transition-colors',
                window === o.value
                  ? 'bg-primary-600/20 text-primary-400'
                  : 'text-gray-400 hover:text-white hover:bg-dark-border/50',
              )}
            >
              {o.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI row */}
      {s && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard
            label="Workers Online"
            value={s.workers_online}
            tone={s.workers_online === 0 ? 'red' : s.workers_online < 3 ? 'amber' : 'green'}
          />
          <KpiCard label="Tasks / min" value={s.tasks_per_min} />
          <KpiCard
            label="Failures / min"
            value={s.failures_per_min}
            tone={s.failures_per_min > 1 ? 'red' : s.failures_per_min > 0 ? 'amber' : 'green'}
          />
          <KpiCard
            label="Avg Duration"
            value={s.avg_duration_ms > 1000 ? `${(s.avg_duration_ms / 1000).toFixed(1)}s` : `${s.avg_duration_ms}ms`}
          />
        </div>
      )}

      {/* Workers */}
      {data && data.workers.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-1.5">
            <Server size={14} /> Workers ({data.workers.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {data.workers.map((w) => (
              <div key={w.worker} className="card p-3 flex items-center justify-between">
                <span className="text-sm text-gray-300 truncate">{w.worker}</span>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-gray-500">{w.task_count} tasks</span>
                  {w.failure_count > 0 && (
                    <span className="text-red-400">{w.failure_count} failed</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Queues */}
      {data && data.queues.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-300 mb-2">Queues</h2>
          <div className="flex flex-wrap gap-2">
            {data.queues.map((q) => (
              <div key={q.queue || 'default'} className="card px-3 py-2 flex items-center gap-2">
                <span className="text-sm text-gray-300">{q.queue || 'default'}</span>
                <span className="text-xs text-gray-500">{q.count}</span>
                {q.failures > 0 && (
                  <StatusPill label={`${q.failures} fail`} tone="red" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Tasks */}
      {data && data.top_tasks.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-300 mb-2">Top Tasks</h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Task</th>
                  <th className="p-3 text-right">Count</th>
                  <th className="p-3 text-right">Fail Rate</th>
                  <th className="p-3 text-right">Avg</th>
                </tr>
              </thead>
              <tbody>
                {data.top_tasks.map((t) => (
                  <tr key={t.task_name} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-300 truncate max-w-[200px]" title={t.task_name}>
                      {t.short_name}
                    </td>
                    <td className="p-3 text-right text-gray-400">{t.count}</td>
                    <td className="p-3 text-right">
                      <StatusPill
                        label={`${t.failure_rate}%`}
                        tone={t.failure_rate > 50 ? 'red' : t.failure_rate > 20 ? 'amber' : t.failure_rate > 0 ? 'gray' : 'green'}
                      />
                    </td>
                    <td className="p-3 text-right text-gray-400">
                      {t.avg_ms > 1000 ? `${(t.avg_ms / 1000).toFixed(1)}s` : `${t.avg_ms}ms`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Failures */}
      {data && data.recent_failures.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-1.5">
            <AlertTriangle size={14} className="text-red-400" /> Recent Failures
          </h2>
          <div className="space-y-2">
            {data.recent_failures.map((f) => (
              <div key={f.task_id} className="card p-3 border-l-2 border-l-red-500">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-300">{f.short_name}</span>
                  <span className="text-xs text-gray-600">{f.queue || 'default'}</span>
                  {f.started_at && (
                    <span className="text-xs text-gray-600 ml-auto">
                      {new Date(f.started_at).toLocaleTimeString()}
                    </span>
                  )}
                </div>
                <p className="text-xs text-red-400 truncate">{f.error_type}: {f.error_message?.slice(0, 120)}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
