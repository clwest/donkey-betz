import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useIncidents, useCreateIncident } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { HealthTone } from '@/types/cockpit'
import { ShieldAlert, Plus, X, Search } from 'lucide-react'
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
                    <Link
                      to={`/cockpit/incidents/${inc.id}`}
                      className="text-gray-200 hover:text-primary-400 transition-colors"
                    >
                      {inc.title}
                    </Link>
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
    </div>
  )
}
