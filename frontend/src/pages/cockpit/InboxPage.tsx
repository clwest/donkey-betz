import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useInbox } from '@/hooks/cockpitQueries'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import {
  INBOX_TYPE_LABEL,
  INBOX_TYPE_TONE,
  INBOX_SEVERITY_LABEL,
  INBOX_SEVERITY_TONE,
} from '@/components/cockpit/inbox/inboxMaps'
import { formatRelative, formatDateTime } from '@/lib/time'
import type { InboxItemType, InboxSeverity } from '@/types/cockpit'
import { Inbox, AlertTriangle, Shield, Play, Bug } from 'lucide-react'

const TYPE_ICON: Record<InboxItemType, React.ElementType> = {
  decision: Shield,
  gate: AlertTriangle,
  error_signature: Bug,
  failed_run: Play,
}

const TYPE_FILTERS: Array<{ value: string; label: string }> = [
  { value: '', label: 'All types' },
  { value: 'decision', label: 'Decisions' },
  { value: 'gate', label: 'Gates' },
  { value: 'error_signature', label: 'Errors' },
  { value: 'failed_run', label: 'Failed Runs' },
]

export default function CockpitInboxPage() {
  const [typeFilter, setTypeFilter] = useState('')
  const navigate = useNavigate()
  const wsId = useWorkspaceStore((s) => s.activeWorkspace?.id)
  const { data, isLoading } = useInbox({ hours: 24, limit: 50, ...(wsId ? { workspace: wsId } : {}) })

  const items = data?.items ?? []
  const filtered = typeFilter ? items.filter((i) => i.type === typeFilter) : items
  const counts = data?.counts

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-white">Inbox</h1>
          {counts && counts.total > 0 && (
            <span className="rounded-full bg-primary-600/20 px-2.5 py-0.5 text-sm font-medium text-primary-400">
              {counts.total}
            </span>
          )}
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="input w-40 text-sm"
        >
          {TYPE_FILTERS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Count chips */}
      {counts && counts.total > 0 && (
        <div className="flex flex-wrap gap-2">
          {counts.decisions > 0 && (
            <button
              onClick={() => setTypeFilter(typeFilter === 'decision' ? '' : 'decision')}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${typeFilter === 'decision' ? 'bg-blue-500/30 text-blue-300' : 'bg-dark-border text-gray-400 hover:text-gray-200'}`}
            >
              Decisions: {counts.decisions}
            </button>
          )}
          {counts.gates > 0 && (
            <button
              onClick={() => setTypeFilter(typeFilter === 'gate' ? '' : 'gate')}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${typeFilter === 'gate' ? 'bg-amber-500/30 text-amber-300' : 'bg-dark-border text-gray-400 hover:text-gray-200'}`}
            >
              Gates: {counts.gates}
            </button>
          )}
          {counts.errors > 0 && (
            <button
              onClick={() => setTypeFilter(typeFilter === 'error_signature' ? '' : 'error_signature')}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${typeFilter === 'error_signature' ? 'bg-red-500/30 text-red-300' : 'bg-dark-border text-gray-400 hover:text-gray-200'}`}
            >
              Errors: {counts.errors}
            </button>
          )}
          {counts.failed_runs > 0 && (
            <button
              onClick={() => setTypeFilter(typeFilter === 'failed_run' ? '' : 'failed_run')}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${typeFilter === 'failed_run' ? 'bg-red-500/30 text-red-300' : 'bg-dark-border text-gray-400 hover:text-gray-200'}`}
            >
              Failed Runs: {counts.failed_runs}
            </button>
          )}
        </div>
      )}

      {/* Items */}
      <div className="space-y-2">
        {isLoading ? (
          <div className="card p-4">
            <SkeletonRows count={8} />
          </div>
        ) : filtered.length === 0 ? (
          <div className="card p-10 text-center">
            <Inbox size={32} className="mx-auto mb-3 text-gray-600" />
            <p className="text-sm text-gray-500">
              {items.length === 0 ? 'Nothing needs attention right now' : 'No items match this filter'}
            </p>
          </div>
        ) : (
          filtered.map((item) => {
            const TypeIcon = TYPE_ICON[item.type] ?? AlertTriangle
            return (
              <div
                key={item.id}
                className="card flex items-start gap-4 px-4 py-3 hover:bg-dark-border/20 cursor-pointer transition-colors"
                onClick={() => navigate(item.cta.route)}
              >
                <div className="mt-0.5 flex-shrink-0">
                  <TypeIcon size={18} className="text-gray-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <StatusPill
                      label={INBOX_SEVERITY_LABEL[item.severity as InboxSeverity]}
                      tone={INBOX_SEVERITY_TONE[item.severity as InboxSeverity] ?? 'gray'}
                    />
                    <StatusPill
                      label={INBOX_TYPE_LABEL[item.type as InboxItemType]}
                      tone={INBOX_TYPE_TONE[item.type as InboxItemType] ?? 'gray'}
                    />
                  </div>
                  <p className="text-sm font-medium text-gray-200 truncate">{item.title}</p>
                  {item.subtitle && (
                    <p className="text-xs text-gray-500 mt-0.5">{item.subtitle}</p>
                  )}
                  {item.preview?.text && (
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">{item.preview.text}</p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <span className="text-xs text-gray-500" title={formatDateTime(item.timestamp)}>
                    {formatRelative(item.timestamp)}
                  </span>
                  <span className="text-[10px] text-primary-400 hover:text-primary-300">
                    {item.cta.label}
                  </span>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
