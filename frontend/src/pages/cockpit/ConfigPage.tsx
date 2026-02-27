import { useState } from 'react'
import {
  useConfigOverview, useToggleConfigProvider, useUpsertConfigFlag,
  useDeleteConfigFlag, useConfigChanges,
} from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import { Settings, Server, Flag, History, Plus, Trash2, Check } from 'lucide-react'
import { cn } from '@/lib/cn'

type Tab = 'providers' | 'flags' | 'changes'

function RelTime({ iso }: { iso: string | null }) {
  if (!iso) return <span className="text-gray-600">never</span>
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60_000)
  if (mins < 1) return <span className="text-gray-400">just now</span>
  if (mins < 60) return <span className="text-gray-400">{mins}m ago</span>
  const hrs = Math.round(mins / 60)
  if (hrs < 24) return <span className="text-gray-400">{hrs}h ago</span>
  return <span className="text-gray-400">{Math.round(hrs / 24)}d ago</span>
}

export default function ConfigPage() {
  const { data, isLoading } = useConfigOverview()
  const { data: changesData } = useConfigChanges({ hours: 48, limit: 50 })
  const toggleProvider = useToggleConfigProvider()
  const upsertFlag = useUpsertConfigFlag()
  const deleteFlag = useDeleteConfigFlag()
  const [tab, setTab] = useState<Tab>('providers')

  // New flag form
  const [showAddFlag, setShowAddFlag] = useState(false)
  const [newKey, setNewKey] = useState('')
  const [newValue, setNewValue] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [newCat, setNewCat] = useState('general')

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Configuration</h1>
        <div className="card p-6"><SkeletonRows count={8} /></div>
      </div>
    )
  }

  const providers = data?.providers ?? []
  const models = data?.models ?? []
  const flags = data?.flags ?? []
  const env = data?.env
  const changes = changesData?.items ?? []

  const tabs: { id: Tab; label: string; count: number }[] = [
    { id: 'providers', label: 'LLM Providers', count: providers.length },
    { id: 'flags', label: 'Feature Flags', count: flags.length },
    { id: 'changes', label: 'Change Log', count: changes.length },
  ]

  const handleAddFlag = () => {
    if (!newKey.trim()) return
    let parsedValue: unknown = newValue
    try { parsedValue = JSON.parse(newValue) } catch { /* keep as string */ }
    upsertFlag.mutate(
      { key: newKey.trim(), value: parsedValue, description: newDesc, category: newCat },
      {
        onSuccess: () => {
          setShowAddFlag(false)
          setNewKey('')
          setNewValue('')
          setNewDesc('')
          setNewCat('general')
        },
      },
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Settings size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Configuration</h1>
      </div>

      {/* Env summary */}
      {env && (
        <div className="flex flex-wrap gap-2">
          <StatusPill label={env.debug ? 'DEBUG' : 'PROD'} tone={env.debug ? 'amber' : 'green'} />
          <StatusPill label={env.database} tone="green" />
          <StatusPill label={env.redis ? 'Redis' : 'No Redis'} tone={env.redis ? 'green' : 'red'} />
          <StatusPill label={env.celery_broker ? 'Celery' : 'No Celery'} tone={env.celery_broker ? 'green' : 'red'} />
          {env.railway && <StatusPill label="Railway" tone="blue" />}
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

      {/* Providers tab */}
      {tab === 'providers' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {providers.map((p) => (
              <div key={p.id} className="card p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Server size={16} className="text-gray-400" />
                    <span className="text-sm font-medium text-gray-200 capitalize">{p.display_name}</span>
                  </div>
                  <button
                    onClick={() => toggleProvider.mutate(p.id)}
                    disabled={toggleProvider.isPending}
                    className={cn(
                      'relative inline-flex h-5 w-9 items-center rounded-full transition-colors',
                      p.is_active ? 'bg-primary-600' : 'bg-dark-border',
                    )}
                  >
                    <span className={cn(
                      'inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform',
                      p.is_active ? 'translate-x-4.5' : 'translate-x-0.5',
                    )} />
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 text-xs">
                  <StatusPill label={p.is_active ? 'active' : 'disabled'} tone={p.is_active ? 'green' : 'gray'} />
                  <StatusPill label={`${p.model_count} models`} tone="blue" />
                  {p.supports_tools && <span className="px-1.5 py-0.5 rounded bg-dark-border text-gray-400">tools</span>}
                  {p.supports_vision && <span className="px-1.5 py-0.5 rounded bg-dark-border text-gray-400">vision</span>}
                  {p.supports_streaming && <span className="px-1.5 py-0.5 rounded bg-dark-border text-gray-400">stream</span>}
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  Health: <RelTime iso={p.last_health_check} />
                </div>
              </div>
            ))}
          </div>

          {/* Models table */}
          {models.length > 0 && (
            <div>
              <h2 className="text-sm font-medium text-gray-300 mb-2">Registered Models ({models.length})</h2>
              <div className="card overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                      <th className="p-3">Model ID</th>
                      <th className="p-3">Provider</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {models.map((m) => (
                      <tr key={m.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                        <td className="p-3 text-gray-300">{m.model_id}</td>
                        <td className="p-3 text-gray-400 capitalize">{m.provider}</td>
                        <td className="p-3">
                          <StatusPill label={m.is_active ? 'active' : 'disabled'} tone={m.is_active ? 'green' : 'gray'} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Flags tab */}
      {tab === 'flags' && (
        <div className="space-y-3">
          <div className="flex justify-end">
            <button
              onClick={() => setShowAddFlag(!showAddFlag)}
              className="btn text-xs flex items-center gap-1.5"
            >
              <Plus size={14} />
              Add Flag
            </button>
          </div>

          {showAddFlag && (
            <div className="card p-4 space-y-3 border-l-2 border-l-primary-500">
              <div className="grid grid-cols-2 gap-3">
                <input
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                  placeholder="key (e.g. enable_auto_blog)"
                  className="input text-sm"
                />
                <input
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  placeholder='value (e.g. true, 42, "text")'
                  className="input text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <input
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Description (optional)"
                  className="input text-sm"
                />
                <select
                  value={newCat}
                  onChange={(e) => setNewCat(e.target.value)}
                  className="input text-sm"
                >
                  <option value="general">general</option>
                  <option value="feature">feature</option>
                  <option value="limit">limit</option>
                  <option value="routing">routing</option>
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleAddFlag}
                  disabled={!newKey.trim() || upsertFlag.isPending}
                  className="btn-primary text-xs flex items-center gap-1.5"
                >
                  <Check size={14} />
                  {upsertFlag.isPending ? 'Saving...' : 'Save Flag'}
                </button>
                <button onClick={() => setShowAddFlag(false)} className="btn text-xs">Cancel</button>
              </div>
            </div>
          )}

          {flags.length === 0 ? (
            <div className="card p-8 text-center text-gray-500">
              No feature flags configured. Click "Add Flag" to create one.
            </div>
          ) : (
            <div className="card overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                    <th className="p-3">Key</th>
                    <th className="p-3">Value</th>
                    <th className="p-3">Category</th>
                    <th className="p-3">Description</th>
                    <th className="p-3">Updated</th>
                    <th className="p-3 w-10"></th>
                  </tr>
                </thead>
                <tbody>
                  {flags.map((f) => (
                    <tr key={f.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                      <td className="p-3 text-gray-300 font-mono text-xs">{f.key}</td>
                      <td className="p-3 text-gray-200 font-mono text-xs">
                        {f.is_sensitive ? '***' : JSON.stringify(f.value)}
                      </td>
                      <td className="p-3">
                        <StatusPill label={f.category} tone="blue" />
                      </td>
                      <td className="p-3 text-gray-500 max-w-[200px] truncate">{f.description}</td>
                      <td className="p-3"><RelTime iso={f.updated_at} /></td>
                      <td className="p-3">
                        <button
                          onClick={() => deleteFlag.mutate(f.id)}
                          disabled={deleteFlag.isPending}
                          className="text-gray-500 hover:text-red-400 transition-colors"
                          title="Delete flag"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Changes tab */}
      {tab === 'changes' && (
        <div className="card overflow-x-auto">
          {changes.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No config changes recorded.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Time</th>
                  <th className="p-3">Actor</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">Target</th>
                  <th className="p-3">Details</th>
                </tr>
              </thead>
              <tbody>
                {changes.map((c) => (
                  <tr key={c.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-400 whitespace-nowrap"><RelTime iso={c.created_at} /></td>
                    <td className="p-3 text-gray-300">{c.actor}</td>
                    <td className="p-3"><StatusPill label={c.action.replace('config.', '')} tone="blue" /></td>
                    <td className="p-3 text-gray-400">{c.target_type}</td>
                    <td className="p-3 text-gray-500 text-xs font-mono max-w-[300px] truncate">
                      {JSON.stringify(c.request_body)}
                    </td>
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
