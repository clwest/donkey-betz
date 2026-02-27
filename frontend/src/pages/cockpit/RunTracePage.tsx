import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useRunTrace } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { TraceTimelineEvent } from '@/types/cockpit'
import { ArrowLeft, Activity, Cpu, Brain, ScrollText, Clock, DollarSign, Zap } from 'lucide-react'
import { cn } from '@/lib/cn'

function fmtTs(iso: string | null) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function fmtDur(ms: number | null) {
  if (!ms) return '—'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function fmtTokens(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

const EVENT_COLORS: Record<string, { bg: string; border: string; icon: React.ElementType }> = {
  run: { bg: 'bg-primary-600/20', border: 'border-primary-500', icon: Zap },
  celery: { bg: 'bg-amber-600/20', border: 'border-amber-500', icon: Cpu },
  llm: { bg: 'bg-blue-600/20', border: 'border-blue-500', icon: Brain },
  audit: { bg: 'bg-gray-600/20', border: 'border-gray-500', icon: ScrollText },
}

function timelineTone(ev: TraceTimelineEvent): Tone {
  if (ev.subtype === 'failed' || ev.subtype === 'error' || ev.subtype === 'FAILURE') return 'red'
  if (ev.subtype === 'completed' || ev.subtype === 'success' || ev.subtype === 'SUCCESS') return 'green'
  if (ev.subtype === 'started' || ev.subtype === 'STARTED') return 'blue'
  return 'gray'
}

type Tab = 'timeline' | 'llm' | 'celery' | 'audit'

export default function RunTracePage() {
  const { runId } = useParams<{ runId: string }>()
  const navigate = useNavigate()
  const { data, isLoading, error } = useRunTrace(runId)
  const [tab, setTab] = useState<Tab>('timeline')

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Run Trace</h1>
        <div className="card p-6"><SkeletonRows count={10} /></div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-200">
          <ArrowLeft size={16} /> Back
        </button>
        <div className="card p-6 text-center text-gray-400">
          {error ? `Failed to load trace: ${(error as Error).message}` : 'Trace not found'}
        </div>
      </div>
    )
  }

  const { run, llm_summary, timeline, celery_events, llm_calls, audit_entries } = data

  const tabs: { id: Tab; label: string; count: number }[] = [
    { id: 'timeline', label: 'Timeline', count: timeline.length },
    { id: 'llm', label: 'LLM Calls', count: llm_calls.length },
    { id: 'celery', label: 'Celery Tasks', count: celery_events.length },
    { id: 'audit', label: 'Audit', count: audit_entries.length },
  ]

  return (
    <div className="space-y-6">
      {/* Back + header */}
      <button
        onClick={() => navigate(`/cockpit/runs/${runId}`)}
        className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-200 transition-colors"
      >
        <ArrowLeft size={16} /> Back to Run Detail
      </button>

      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Activity size={20} className="text-primary-400" />
            <h1 className="text-xl font-bold text-white truncate">Trace: {run.agent_name}</h1>
          </div>
          <p className="text-sm text-gray-400 mt-1 truncate">{run.task}</p>
        </div>
        <StatusPill
          label={run.status}
          tone={run.status === 'completed' ? 'green' : run.status === 'failed' ? 'red' : 'blue'}
        />
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="card p-3">
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-1"><Clock size={12} /> Duration</div>
          <div className="text-lg font-bold text-gray-200">{fmtDur(run.execution_time_ms)}</div>
        </div>
        <div className="card p-3">
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-1"><Brain size={12} /> LLM Calls</div>
          <div className="text-lg font-bold text-gray-200">{llm_summary.total_calls}</div>
        </div>
        <div className="card p-3">
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-1"><Zap size={12} /> Tokens</div>
          <div className="text-lg font-bold text-gray-200">{fmtTokens(llm_summary.total_tokens)}</div>
        </div>
        <div className="card p-3">
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-1"><DollarSign size={12} /> LLM Cost</div>
          <div className="text-lg font-bold text-gray-200">${llm_summary.total_cost.toFixed(4)}</div>
        </div>
        <div className="card p-3">
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-1"><Cpu size={12} /> Celery Tasks</div>
          <div className="text-lg font-bold text-gray-200">{celery_events.length}</div>
        </div>
      </div>

      {/* Error banner */}
      {run.error_message && (
        <div className="card border-l-2 border-l-red-500 p-4">
          <p className="text-xs font-medium text-red-400 mb-1">Error</p>
          <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words font-mono max-h-32 overflow-auto">
            {run.error_message}
          </pre>
        </div>
      )}

      {/* Tab bar */}
      <div className="flex border-b border-dark-border">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'px-4 py-2 text-sm border-b-2 transition-colors',
              tab === t.id
                ? 'border-primary-500 text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-300',
            )}
          >
            {t.label}
            {t.count > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-dark-border text-xs text-gray-400">
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Timeline tab */}
      {tab === 'timeline' && (
        <div className="space-y-2">
          {timeline.length === 0 ? (
            <div className="card p-8 text-center text-gray-500">No events in trace.</div>
          ) : (
            timeline.map((ev, i) => {
              const cfg = EVENT_COLORS[ev.type] || EVENT_COLORS.audit
              const Icon = cfg.icon
              return (
                <div key={i} className={cn('card p-3 flex items-start gap-3 border-l-2', cfg.border)}>
                  <div className={cn('p-1.5 rounded', cfg.bg)}>
                    <Icon size={14} className="text-gray-300" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-200">{ev.summary}</span>
                      <StatusPill label={ev.subtype} tone={timelineTone(ev)} />
                    </div>
                    {ev.detail && (
                      <p className="text-xs text-gray-500 mt-0.5 truncate">{ev.detail}</p>
                    )}
                  </div>
                  <span className="text-xs text-gray-600 whitespace-nowrap">{fmtTs(ev.timestamp)}</span>
                </div>
              )
            })
          )}
        </div>
      )}

      {/* LLM Calls tab */}
      {tab === 'llm' && (
        <div className="card overflow-x-auto">
          {llm_calls.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No LLM calls recorded.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Time</th>
                  <th className="p-3">Provider</th>
                  <th className="p-3">Model</th>
                  <th className="p-3 text-right">Tokens</th>
                  <th className="p-3 text-right">Cost</th>
                  <th className="p-3 text-right">Latency</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {llm_calls.map((c) => (
                  <tr key={c.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-400 whitespace-nowrap">{fmtTs(c.created_at)}</td>
                    <td className="p-3 text-gray-300 capitalize">{c.provider}</td>
                    <td className="p-3 text-gray-300">{c.model_id}</td>
                    <td className="p-3 text-right text-gray-400">{c.total_tokens.toLocaleString()}</td>
                    <td className="p-3 text-right text-gray-200 font-medium">${parseFloat(c.cost).toFixed(4)}</td>
                    <td className="p-3 text-right text-gray-400">{c.latency_ms}ms</td>
                    <td className="p-3">
                      <StatusPill label={c.success ? 'ok' : 'error'} tone={c.success ? 'green' : 'red'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Celery Tasks tab */}
      {tab === 'celery' && (
        <div className="card overflow-x-auto">
          {celery_events.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No Celery task events.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Time</th>
                  <th className="p-3">Task</th>
                  <th className="p-3">Queue</th>
                  <th className="p-3">Worker</th>
                  <th className="p-3 text-right">Duration</th>
                  <th className="p-3 text-right">RSS Delta</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {celery_events.map((ev) => (
                  <tr key={ev.task_id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-400 whitespace-nowrap">{fmtTs(ev.started_at)}</td>
                    <td className="p-3 text-gray-300">{ev.short_name}</td>
                    <td className="p-3 text-gray-400">{ev.queue}</td>
                    <td className="p-3 text-gray-400">{ev.worker}</td>
                    <td className="p-3 text-right text-gray-400">{ev.duration_seconds != null ? `${ev.duration_seconds.toFixed(1)}s` : '—'}</td>
                    <td className="p-3 text-right text-gray-400">{ev.rss_delta_mb != null ? `${ev.rss_delta_mb.toFixed(1)}MB` : '—'}</td>
                    <td className="p-3">
                      <StatusPill
                        label={ev.status}
                        tone={ev.status === 'SUCCESS' ? 'green' : ev.status === 'FAILURE' ? 'red' : 'blue'}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Audit tab */}
      {tab === 'audit' && (
        <div className="card overflow-x-auto">
          {audit_entries.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No audit entries for this run.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Time</th>
                  <th className="p-3">Actor</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">Target</th>
                </tr>
              </thead>
              <tbody>
                {audit_entries.map((a) => (
                  <tr key={a.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-400 whitespace-nowrap">{fmtTs(a.created_at)}</td>
                    <td className="p-3 text-gray-300">{a.actor}</td>
                    <td className="p-3 text-gray-300">{a.action}</td>
                    <td className="p-3 text-gray-400">{a.target_type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}
