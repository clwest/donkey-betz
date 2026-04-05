import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  useIncidentDetail, useUpdateIncident, useAddIncidentEvent,
} from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { HealthTone, IncidentEvent } from '@/types/cockpit'
import {
  ArrowLeft, ShieldAlert, MessageSquare, LinkIcon,
  RefreshCw, Send, CheckCircle2,
} from 'lucide-react'
import { cn } from '@/lib/cn'

const SEVERITY_TONE: Record<string, HealthTone> = {
  critical: 'red', high: 'amber', medium: 'blue', low: 'gray',
}
const STATUS_TONE: Record<string, HealthTone> = {
  open: 'red', mitigating: 'amber', resolved: 'green',
}

function TimeStamp({ iso }: { iso: string }) {
  const d = new Date(iso)
  return (
    <span className="text-xs text-gray-500">
      {d.toLocaleTimeString()} · {d.toLocaleDateString()}
    </span>
  )
}

function EventCard({ event }: { event: IncidentEvent }) {
  const iconMap = {
    note: <MessageSquare size={14} className="text-blue-400" />,
    link: <LinkIcon size={14} className="text-green-400" />,
    status_change: <RefreshCw size={14} className="text-amber-400" />,
  }

  const renderContent = () => {
    const c = event.content as Record<string, unknown>
    if (event.event_type === 'note') {
      return <p className="text-gray-300 text-sm whitespace-pre-wrap">{c.text as string}</p>
    }
    if (event.event_type === 'link') {
      const linkType = c.link_type as string
      const linkId = c.link_id as string
      const label = (c.label as string) || `${linkType}: ${linkId}`
      const linkUrl = linkType === 'run_id' ? `/workspace?tab=system&sub=ops` :
        linkType === 'error_signature_id' ? `/workspace?tab=system&sub=ops` : null
      return (
        <div className="text-sm">
          <span className="text-gray-500 mr-1">{linkType}:</span>
          {linkUrl ? (
            <Link to={linkUrl} className="text-primary-400 hover:underline">{label}</Link>
          ) : (
            <span className="text-gray-300">{label}</span>
          )}
        </div>
      )
    }
    if (event.event_type === 'status_change') {
      const changes = Object.entries(c)
      return (
        <div className="space-y-1">
          {changes.map(([key, val]) => {
            const v = val as Record<string, string> | string
            if (typeof v === 'object' && v !== null && 'from' in v) {
              return (
                <div key={key} className="text-sm text-gray-400">
                  <span className="text-gray-500">{key}:</span>{' '}
                  <span className="text-red-400 line-through">{v.from}</span>{' → '}
                  <span className="text-green-400">{v.to}</span>
                </div>
              )
            }
            return (
              <div key={key} className="text-sm text-gray-400">
                <span className="text-gray-500">{key}:</span> {String(v)}
              </div>
            )
          })}
        </div>
      )
    }
    return null
  }

  return (
    <div className="flex gap-3">
      <div className="mt-1 flex-shrink-0">{iconMap[event.event_type] ?? null}</div>
      <div className="flex-1 card p-3 space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-300">{event.actor}</span>
          <StatusPill label={event.event_type.replace('_', ' ')} tone="blue" />
          <TimeStamp iso={event.created_at} />
        </div>
        {renderContent()}
      </div>
    </div>
  )
}

export default function IncidentDetailPage() {
  const { incidentId } = useParams<{ incidentId: string }>()
  const { data, isLoading } = useIncidentDetail(incidentId ?? '')
  const updateMutation = useUpdateIncident()
  const addEventMutation = useAddIncidentEvent()

  const [noteText, setNoteText] = useState('')
  const [linkType, setLinkType] = useState('run_id')
  const [linkId, setLinkId] = useState('')
  const [linkLabel, setLinkLabel] = useState('')
  const [composerTab, setComposerTab] = useState<'note' | 'link'>('note')

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Incident</h1>
        <div className="card p-6"><SkeletonRows count={6} /></div>
      </div>
    )
  }

  const inc = data.incident
  const events = data.events

  const handleStatusChange = (status: string) => {
    if (!incidentId) return
    updateMutation.mutate({ incidentId, status })
  }

  const handleSeverityChange = (severity: string) => {
    if (!incidentId) return
    updateMutation.mutate({ incidentId, severity })
  }

  const handleAddNote = () => {
    if (!incidentId || !noteText.trim()) return
    addEventMutation.mutate(
      { incidentId, event_type: 'note', text: noteText.trim() },
      { onSuccess: () => setNoteText('') },
    )
  }

  const handleAddLink = () => {
    if (!incidentId || !linkId.trim()) return
    addEventMutation.mutate(
      { incidentId, event_type: 'link', link_type: linkType, link_id: linkId.trim(), label: linkLabel },
      { onSuccess: () => { setLinkId(''); setLinkLabel('') } },
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link to="/workspace?tab=system&sub=incidents" className="text-gray-500 hover:text-gray-300">
          <ArrowLeft size={18} />
        </Link>
        <ShieldAlert size={20} className="text-primary-400" />
        <h1 className="text-xl font-bold text-white flex-1">{inc.title}</h1>
      </div>

      {/* Status bar */}
      <div className="card p-4 flex flex-wrap gap-4 items-center">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Severity</label>
          <select
            value={inc.severity}
            onChange={(e) => handleSeverityChange(e.target.value)}
            className="input text-sm"
            disabled={updateMutation.isPending}
          >
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Status</label>
          <div className="flex gap-1">
            {['open', 'mitigating', 'resolved'].map((s) => (
              <button
                key={s}
                onClick={() => handleStatusChange(s)}
                disabled={updateMutation.isPending}
                className={cn(
                  'px-3 py-1.5 text-xs rounded transition-colors flex items-center gap-1',
                  inc.status === s
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-border text-gray-400 hover:text-gray-200',
                )}
              >
                {s === 'resolved' && <CheckCircle2 size={12} />}
                {s}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Owner</label>
          <span className="text-sm text-gray-300">{inc.owner || 'Unassigned'}</span>
        </div>
        <div className="flex gap-2 ml-auto">
          <StatusPill label={inc.severity} tone={SEVERITY_TONE[inc.severity] ?? 'gray'} />
          <StatusPill label={inc.status} tone={STATUS_TONE[inc.status] ?? 'gray'} />
        </div>
      </div>

      {/* Resolution summary */}
      {inc.resolution_summary && (
        <div className="card p-4 border-l-2 border-l-green-500">
          <span className="text-xs text-gray-500 block mb-1">Resolution</span>
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{inc.resolution_summary}</p>
        </div>
      )}

      {/* Timeline */}
      <div>
        <h2 className="text-sm font-medium text-gray-300 mb-3">
          Timeline ({events.length} events)
        </h2>
        {events.length === 0 ? (
          <div className="card p-8 text-center text-gray-500">
            No events yet. Add a note or link evidence below.
          </div>
        ) : (
          <div className="space-y-3">
            {events.map((ev) => (
              <EventCard key={ev.id} event={ev} />
            ))}
          </div>
        )}
      </div>

      {/* Add event composer */}
      <div className="card p-4 space-y-3">
        <div className="flex gap-2">
          <button
            onClick={() => setComposerTab('note')}
            className={cn(
              'px-3 py-1.5 text-xs rounded transition-colors',
              composerTab === 'note' ? 'bg-primary-600 text-white' : 'bg-dark-border text-gray-400',
            )}
          >
            <MessageSquare size={12} className="inline mr-1" />
            Note
          </button>
          <button
            onClick={() => setComposerTab('link')}
            className={cn(
              'px-3 py-1.5 text-xs rounded transition-colors',
              composerTab === 'link' ? 'bg-primary-600 text-white' : 'bg-dark-border text-gray-400',
            )}
          >
            <LinkIcon size={12} className="inline mr-1" />
            Link Evidence
          </button>
        </div>

        {composerTab === 'note' ? (
          <div className="flex gap-2">
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Add a note..."
              className="input text-sm flex-1 min-h-[60px]"
              onKeyDown={(e) => { if (e.key === 'Enter' && e.metaKey) handleAddNote() }}
            />
            <button
              onClick={handleAddNote}
              disabled={!noteText.trim() || addEventMutation.isPending}
              className="btn-primary text-xs self-end"
            >
              <Send size={14} />
            </button>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2 items-end">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Type</label>
              <select
                value={linkType}
                onChange={(e) => setLinkType(e.target.value)}
                className="input text-sm"
              >
                <option value="run_id">Run</option>
                <option value="error_signature_id">Error Signature</option>
                <option value="alert_id">Alert</option>
                <option value="agent_name">Agent</option>
                <option value="config_change_id">Config Change</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="text-xs text-gray-500 block mb-1">ID</label>
              <input
                value={linkId}
                onChange={(e) => setLinkId(e.target.value)}
                placeholder="ID or reference..."
                className="input text-sm w-full"
              />
            </div>
            <div className="flex-1">
              <label className="text-xs text-gray-500 block mb-1">Label (optional)</label>
              <input
                value={linkLabel}
                onChange={(e) => setLinkLabel(e.target.value)}
                placeholder="Description..."
                className="input text-sm w-full"
              />
            </div>
            <button
              onClick={handleAddLink}
              disabled={!linkId.trim() || addEventMutation.isPending}
              className="btn-primary text-xs"
            >
              <LinkIcon size={14} />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
