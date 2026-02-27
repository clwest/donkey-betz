import { useState } from 'react'
import { useAuditLog } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { AuditLogEntry } from '@/types/cockpit'
import { ScrollText, ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '@/lib/cn'

const ACTION_TONE: Record<string, Tone> = {
  approve: 'green',
  reject: 'red',
  block: 'red',
  retry: 'amber',
  create: 'blue',
}

function toneLookup(action: string): Tone {
  for (const [key, tone] of Object.entries(ACTION_TONE)) {
    if (action.includes(key)) return tone
  }
  return 'gray'
}

function formatAction(action: string) {
  return action.replace(/_/g, ' ')
}

function EntryRow({ entry }: { entry: AuditLogEntry }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="card p-3">
      <button
        className="flex w-full items-center gap-3 text-left"
        onClick={() => setExpanded((e) => !e)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <StatusPill label={formatAction(entry.action)} tone={toneLookup(entry.action)} />
            {entry.target_type && (
              <span className="text-xs text-gray-500">
                {entry.target_type}
                {entry.target_id ? `:${entry.target_id.slice(0, 8)}` : ''}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span>{entry.actor}</span>
            <span>{new Date(entry.created_at).toLocaleString()}</span>
            {entry.ip_address && <span>{entry.ip_address}</span>}
          </div>
        </div>
        {expanded ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
      </button>

      {expanded && (
        <div className="mt-2 pt-2 border-t border-dark-border/50 space-y-2">
          {Object.keys(entry.request_body).length > 0 && (
            <div>
              <span className="text-xs font-medium text-gray-400">Request</span>
              <pre className="mt-0.5 text-xs text-gray-500 bg-dark-bg rounded p-2 overflow-x-auto">
                {JSON.stringify(entry.request_body, null, 2)}
              </pre>
            </div>
          )}
          {Object.keys(entry.response_summary).length > 0 && (
            <div>
              <span className="text-xs font-medium text-gray-400">Response</span>
              <pre className="mt-0.5 text-xs text-gray-500 bg-dark-bg rounded p-2 overflow-x-auto">
                {JSON.stringify(entry.response_summary, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const ACTION_OPTIONS = [
  { value: '', label: 'All actions' },
  { value: 'approve', label: 'Approvals' },
  { value: 'retry', label: 'Retries' },
  { value: 'create', label: 'Creates' },
  { value: 'block', label: 'Blocks' },
]

const RANGE_OPTIONS = [
  { value: 24, label: '24h' },
  { value: 168, label: '7d' },
  { value: 720, label: '30d' },
]

export default function AuditLogPage() {
  const [actionFilter, setActionFilter] = useState('')
  const [hours, setHours] = useState(168)

  const { data, isLoading } = useAuditLog({ hours, action: actionFilter || undefined })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Audit Log</h1>
        <div className="card p-6"><SkeletonRows count={8} /></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <ScrollText size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Audit Log</h1>
        {data && (
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary-600/20 text-primary-400">
            {data.total}
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="input text-sm py-1.5"
        >
          {ACTION_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <div className="flex rounded-lg border border-dark-border overflow-hidden">
          {RANGE_OPTIONS.map((o) => (
            <button
              key={o.value}
              onClick={() => setHours(o.value)}
              className={cn(
                'px-3 py-1.5 text-xs transition-colors',
                hours === o.value
                  ? 'bg-primary-600/20 text-primary-400'
                  : 'text-gray-400 hover:text-white hover:bg-dark-border/50',
              )}
            >
              {o.label}
            </button>
          ))}
        </div>
      </div>

      {/* Entries */}
      {!data || data.items.length === 0 ? (
        <div className="card p-8 text-center text-gray-500">
          No audit entries in this period.
        </div>
      ) : (
        <div className="space-y-2">
          {data.items.map((entry) => (
            <EntryRow key={entry.id} entry={entry} />
          ))}
        </div>
      )}
    </div>
  )
}
