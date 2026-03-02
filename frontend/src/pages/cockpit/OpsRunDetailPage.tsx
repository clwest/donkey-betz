import { useParams, Link } from 'react-router-dom'
import { useOpsRunDetail } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { OpsRunStatus, OpsRunEventType, OpsRunEvent } from '@/types/cockpit'
import {
  ArrowLeft, Activity, CheckCircle2, XCircle, Play, Info, Heart,
} from 'lucide-react'

const STATUS_TONE: Record<OpsRunStatus, Tone> = {
  running: 'blue',
  passed: 'green',
  failed: 'red',
  partial: 'amber',
}

const EVENT_TONE: Record<OpsRunEventType, Tone> = {
  step_start: 'blue',
  step_pass: 'green',
  step_fail: 'red',
  info: 'gray',
  heartbeat: 'gray',
}

const EVENT_ICON: Record<OpsRunEventType, React.ReactNode> = {
  step_start: <Play size={14} className="text-blue-400" />,
  step_pass: <CheckCircle2 size={14} className="text-emerald-400" />,
  step_fail: <XCircle size={14} className="text-red-400" />,
  info: <Info size={14} className="text-gray-400" />,
  heartbeat: <Heart size={14} className="text-gray-400" />,
}

function TimeStamp({ iso }: { iso: string }) {
  const d = new Date(iso)
  return (
    <span className="text-xs text-gray-500">
      {d.toLocaleTimeString()} &middot; {d.toLocaleDateString()}
    </span>
  )
}

function EventCard({ event }: { event: OpsRunEvent }) {
  const detail = event.detail as Record<string, unknown>
  const hasDetail = Object.keys(detail).length > 0

  return (
    <div className="flex gap-3">
      <div className="mt-1 flex-shrink-0">{EVENT_ICON[event.event_type] ?? null}</div>
      <div className="flex-1 card p-3 space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-200">{event.label}</span>
          <StatusPill label={event.event_type.replace('_', ' ')} tone={EVENT_TONE[event.event_type] ?? 'gray'} />
          <TimeStamp iso={event.created_at} />
        </div>
        {hasDetail && (
          <pre className="text-xs text-gray-400 bg-dark-bg/50 rounded p-2 overflow-x-auto max-h-40">
            {JSON.stringify(detail, null, 2)}
          </pre>
        )}
      </div>
    </div>
  )
}

export default function OpsRunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const { data, isLoading } = useOpsRunDetail(runId)

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Ops Run</h1>
        <div className="card p-6"><SkeletonRows count={6} /></div>
      </div>
    )
  }

  const run = data.run
  const events = data.events

  const duration = run.finished_at
    ? ((new Date(run.finished_at).getTime() - new Date(run.started_at).getTime()) / 1000).toFixed(1) + 's'
    : 'running...'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link to="/cockpit/ops-runs" className="text-gray-500 hover:text-gray-300">
          <ArrowLeft size={18} />
        </Link>
        <Activity size={20} className="text-primary-400" />
        <h1 className="text-xl font-bold text-white flex-1">{run.title}</h1>
        <StatusPill label={run.status} tone={STATUS_TONE[run.status] ?? 'gray'} />
      </div>

      {/* Summary card */}
      <div className="card p-4 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Type</label>
          <span className="text-sm text-gray-200">{run.run_type}</span>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Triggered By</label>
          <span className="text-sm text-gray-200">{run.triggered_by}</span>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Duration</label>
          <span className="text-sm text-gray-200">{duration}</span>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Events</label>
          <span className="text-sm text-gray-200">{run.event_count}</span>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Failures</label>
          <span className={`text-sm ${run.fail_count > 0 ? 'text-red-400' : 'text-gray-200'}`}>
            {run.fail_count}
          </span>
        </div>
      </div>

      {/* Summary JSON */}
      {Object.keys(run.summary).length > 0 && (
        <div className="card p-4">
          <label className="text-xs text-gray-500 block mb-2">Summary</label>
          <pre className="text-xs text-gray-400 bg-dark-bg/50 rounded p-3 overflow-x-auto max-h-48">
            {JSON.stringify(run.summary, null, 2)}
          </pre>
        </div>
      )}

      {/* Timeline */}
      <div>
        <h2 className="text-sm font-medium text-gray-300 mb-3">
          Timeline ({events.length} events)
        </h2>
        {events.length === 0 ? (
          <div className="card p-8 text-center text-gray-500">
            No events recorded.
          </div>
        ) : (
          <div className="space-y-3">
            {events.map((ev) => (
              <EventCard key={ev.id} event={ev} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
