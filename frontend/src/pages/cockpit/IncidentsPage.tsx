import { useState } from 'react'
import {
  useIncidents, useCreateIncident,
  useIncidentDetail, useUpdateIncident, useAddIncidentEvent,
} from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { HealthTone, IncidentEvent } from '@/types/cockpit'
import {
  ShieldAlert, Plus, X, Search, ArrowLeft,
  MessageSquare, LinkIcon, RefreshCw, Send, CheckCircle2,
} from 'lucide-react'
import { cn } from '@/lib/cn'

const SEVERITY_TONE: Record<string, HealthTone> = {
  critical: 'red',
  high: 'amber',
  medium: 'blue',
  low: 'gray',
}
const STATUS_TONE: Record<string, HealthTone> = {
  open: 'red',
  mitigating: 'amber',
  resolved: 'green',
}

function RelTime({ iso }: { iso: string | null }) {
  if (!iso) return <span className="text-gray-600">—</span>
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60_000)
  if (mins < 1) return <span className="text-gray-400">just now</span>
  if (mins < 60) return <span className="text-gray-400">{mins}m ago</span>
  const hrs = Math.round(mins / 60)
  if (hrs < 24) return <span className="text-gray-400">{hrs}h ago</span>
  return <span className="text-gray-400">{Math.round(hrs / 24)}d ago</span>
}

export default function IncidentsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [q, setQ] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newSeverity, setNewSeverity] = useState('medium')
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null)

  const { data, isLoading } = useIncidents({
    status: statusFilter || undefined,
    q: q || undefined,
    limit: 50,
  })
  const createMutation = useCreateIncident()

  const handleCreate = () => {
    if (!newTitle.trim()) return
    createMutation.mutate(
      { title: newTitle.trim(), severity: newSeverity },
      {
        onSuccess: () => {
          setShowCreate(false)
          setNewTitle('')
          setNewSeverity('medium')
        },
      },
    )
  }

  const items = data?.items ?? []
  const total = data?.total ?? 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert size={20} className="text-primary-400" />
          <h1 className="text-2xl font-bold text-white">Incidents</h1>
          {total > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-dark-border text-xs text-gray-400">
              {total}
            </span>
          )}
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="btn-primary text-xs flex items-center gap-1.5"
        >
          <Plus size={14} />
          Declare Incident
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <div className="card p-4 space-y-3 border-l-2 border-l-red-500">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-200">New Incident</span>
            <button onClick={() => setShowCreate(false)} className="text-gray-500 hover:text-gray-300">
              <X size={16} />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Incident title..."
              className="input text-sm md:col-span-2"
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
            />
            <select
              value={newSeverity}
              onChange={(e) => setNewSeverity(e.target.value)}
              className="input text-sm"
            >
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <button
            onClick={handleCreate}
            disabled={!newTitle.trim() || createMutation.isPending}
            className="btn-primary text-xs"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Incident'}
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-2.5 text-gray-500" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search incidents..."
            className="input text-sm pl-8 w-56"
          />
        </div>
        <div className="flex gap-1">
          {['', 'open', 'mitigating', 'resolved'].map((s) => (
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
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="card p-6"><SkeletonRows count={6} /></div>
      ) : items.length === 0 ? (
        <div className="card p-12 text-center text-gray-500">
          No incidents found. Click "Declare Incident" to create one.
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                <th className="p-3">Severity</th>
                <th className="p-3">Title</th>
                <th className="p-3">Status</th>
                <th className="p-3">Owner</th>
                <th className="p-3">Events</th>
                <th className="p-3">Links</th>
                <th className="p-3">Last Activity</th>
                <th className="p-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {items.map((inc) => (
                <tr key={inc.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                  <td className="p-3">
                    <StatusPill label={inc.severity} tone={SEVERITY_TONE[inc.severity] ?? 'gray'} />
                  </td>
                  <td className="p-3">
                    <button
                      onClick={() => setSelectedIncidentId(inc.id)}
                      className="text-gray-200 hover:text-primary-400 transition-colors text-left"
                    >
                      {inc.title}
                    </button>
                  </td>
                  <td className="p-3">
                    <StatusPill label={inc.status} tone={STATUS_TONE[inc.status] ?? 'gray'} />
                  </td>
                  <td className="p-3 text-gray-400">{inc.owner || '—'}</td>
                  <td className="p-3 text-gray-400">{inc.event_count}</td>
                  <td className="p-3 text-gray-400">{inc.link_count}</td>
                  <td className="p-3"><RelTime iso={inc.last_activity} /></td>
                  <td className="p-3"><RelTime iso={inc.created_at} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Inline Incident Detail */}
      {selectedIncidentId && (
        <IncidentDetailInline
          incidentId={selectedIncidentId}
          onBack={() => setSelectedIncidentId(null)}
        />
      )}
    </div>
  )
}

/* Inline detail view — replaces the old routed IncidentDetailPage */
function IncidentDetailInline({ incidentId, onBack }: { incidentId: string; onBack: () => void }) {
  const { data, isLoading } = useIncidentDetail(incidentId)
  const updateMutation = useUpdateIncident()
  const addEventMutation = useAddIncidentEvent()
  const [noteText, setNoteText] = useState('')
  const [linkType, setLinkType] = useState('run_id')
  const [linkId, setLinkId] = useState('')
  const [linkLabel, setLinkLabel] = useState('')
  const [composerTab, setComposerTab] = useState<'note' | 'link'>('note')

  if (isLoading || !data) {
    return (
      <div className="card p-6 mt-4 border-l-2 border-l-primary-500">
        <SkeletonRows count={6} />
      </div>
    )
  }

  const inc = data.incident
  const events = (data.events ?? []) as IncidentEvent[]

  return (
    <div className="mt-4 space-y-4 border-t border-dark-border pt-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="text-gray-500 hover:text-gray-300">
          <ArrowLeft size={18} />
        </button>
        <ShieldAlert size={20} className="text-primary-400" />
        <h2 className="text-xl font-bold text-white flex-1">{inc.title}</h2>
      </div>

      {/* Status bar */}
      <div className="card p-4 flex flex-wrap gap-4 items-center">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Severity</label>
          <select
            value={inc.severity}
            onChange={(e) => updateMutation.mutate({ incidentId, severity: e.target.value })}
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
                onClick={() => updateMutation.mutate({ incidentId, status: s })}
                disabled={updateMutation.isPending}
                className={cn(
                  'px-3 py-1.5 text-xs rounded transition-colors flex items-center gap-1',
                  inc.status === s ? 'bg-primary-600 text-white' : 'bg-dark-border text-gray-400 hover:text-gray-200',
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

      {/* Resolution */}
      {inc.resolution_summary && (
        <div className="card p-4 border-l-2 border-l-green-500">
          <span className="text-xs text-gray-500 block mb-1">Resolution</span>
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{inc.resolution_summary}</p>
        </div>
      )}

      {/* Timeline */}
      <div>
        <h3 className="text-sm font-medium text-gray-300 mb-3">Timeline ({events.length} events)</h3>
        {events.length === 0 ? (
          <div className="card p-8 text-center text-gray-500">No events yet.</div>
        ) : (
          <div className="space-y-3">
            {events.map((ev) => (
              <div key={ev.id} className="flex gap-3">
                <div className="mt-1 flex-shrink-0">
                  {ev.event_type === 'note' ? <MessageSquare size={14} className="text-blue-400" /> :
                   ev.event_type === 'link' ? <LinkIcon size={14} className="text-green-400" /> :
                   <RefreshCw size={14} className="text-amber-400" />}
                </div>
                <div className="flex-1 card p-3 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-gray-300">{ev.actor}</span>
                    <StatusPill label={ev.event_type.replace('_', ' ')} tone="blue" />
                    <span className="text-xs text-gray-500">{new Date(ev.created_at).toLocaleString()}</span>
                  </div>
                  {ev.event_type === 'note' && (
                    <p className="text-gray-300 text-sm whitespace-pre-wrap">{(ev.content as Record<string, string>).text}</p>
                  )}
                  {ev.event_type === 'status_change' && (
                    <div className="space-y-1">
                      {Object.entries(ev.content as Record<string, unknown>).map(([key, val]) => {
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
                        return <div key={key} className="text-sm text-gray-400"><span className="text-gray-500">{key}:</span> {String(v)}</div>
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Composer */}
      <div className="card p-4 space-y-3">
        <div className="flex gap-2">
          <button
            onClick={() => setComposerTab('note')}
            className={cn('px-3 py-1.5 text-xs rounded transition-colors', composerTab === 'note' ? 'bg-primary-600 text-white' : 'bg-dark-border text-gray-400')}
          >
            <MessageSquare size={12} className="inline mr-1" /> Note
          </button>
          <button
            onClick={() => setComposerTab('link')}
            className={cn('px-3 py-1.5 text-xs rounded transition-colors', composerTab === 'link' ? 'bg-primary-600 text-white' : 'bg-dark-border text-gray-400')}
          >
            <LinkIcon size={12} className="inline mr-1" /> Link Evidence
          </button>
        </div>
        {composerTab === 'note' ? (
          <div className="flex gap-2">
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Add a note..."
              className="input text-sm flex-1 min-h-[60px]"
              onKeyDown={(e) => { if (e.key === 'Enter' && e.metaKey) { if (noteText.trim()) addEventMutation.mutate({ incidentId, event_type: 'note', text: noteText.trim() }, { onSuccess: () => setNoteText('') }) } }}
            />
            <button
              onClick={() => { if (noteText.trim()) addEventMutation.mutate({ incidentId, event_type: 'note', text: noteText.trim() }, { onSuccess: () => setNoteText('') }) }}
              disabled={!noteText.trim() || addEventMutation.isPending}
              className="btn-primary text-xs self-end"
            >
              <Send size={14} />
            </button>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2 items-end">
            <select value={linkType} onChange={(e) => setLinkType(e.target.value)} className="input text-sm">
              <option value="run_id">Run</option>
              <option value="error_signature_id">Error Signature</option>
              <option value="alert_id">Alert</option>
              <option value="agent_name">Agent</option>
            </select>
            <input value={linkId} onChange={(e) => setLinkId(e.target.value)} placeholder="ID..." className="input text-sm flex-1" />
            <input value={linkLabel} onChange={(e) => setLinkLabel(e.target.value)} placeholder="Label (optional)" className="input text-sm flex-1" />
            <button
              onClick={() => { if (linkId.trim()) addEventMutation.mutate({ incidentId, event_type: 'link', link_type: linkType, link_id: linkId.trim(), label: linkLabel }, { onSuccess: () => { setLinkId(''); setLinkLabel('') } }) }}
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
