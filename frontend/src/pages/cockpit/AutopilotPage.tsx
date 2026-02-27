import { useState } from 'react'
import { useAutopilotPolicies, useToggleAutopilotPolicy, useEvaluateAutopilot, useAutopilotHistory } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { AutopilotAction } from '@/types/cockpit'
import { Bot, Play, Zap, Clock, ChevronDown, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/cn'

function RelTime({ iso }: { iso: string | null }) {
  if (!iso) return <span className="text-gray-600">never</span>
  const d = new Date(iso)
  const mins = Math.round((Date.now() - d.getTime()) / 60_000)
  if (mins < 1) return <span className="text-gray-400">just now</span>
  if (mins < 60) return <span className="text-gray-400">{mins}m ago</span>
  const hrs = Math.round(mins / 60)
  if (hrs < 24) return <span className="text-gray-400">{hrs}h ago</span>
  return <span className="text-gray-400">{Math.round(hrs / 24)}d ago</span>
}

function actionTone(action: string): Tone {
  if (action.includes('pause')) return 'amber'
  if (action.includes('alert') || action.includes('incident')) return 'red'
  return 'blue'
}

export default function AutopilotPage() {
  const { data: policiesData, isLoading: policiesLoading } = useAutopilotPolicies()
  const { data: historyData, isLoading: historyLoading } = useAutopilotHistory({ hours: 48, limit: 50 })
  const toggleMut = useToggleAutopilotPolicy()
  const evalMut = useEvaluateAutopilot()
  const [evalResult, setEvalResult] = useState<AutopilotAction[] | null>(null)
  const [evalMode, setEvalMode] = useState<'dry_run' | 'execute'>('dry_run')
  const [expandedPolicy, setExpandedPolicy] = useState<string | null>(null)

  if (policiesLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Autopilot</h1>
        <div className="card p-6"><SkeletonRows count={6} /></div>
      </div>
    )
  }

  const policies = policiesData?.policies ?? []

  const handleEvaluate = async (mode: 'dry_run' | 'execute') => {
    setEvalMode(mode)
    const result = await evalMut.mutateAsync(mode)
    setEvalResult(result.actions)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Bot size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Autopilot</h1>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => handleEvaluate('dry_run')}
            disabled={evalMut.isPending}
            className="btn text-xs flex items-center gap-1.5"
          >
            <Play size={14} />
            {evalMut.isPending && evalMode === 'dry_run' ? 'Running...' : 'Dry Run'}
          </button>
          <button
            onClick={() => handleEvaluate('execute')}
            disabled={evalMut.isPending}
            className="btn-primary text-xs flex items-center gap-1.5"
          >
            <Zap size={14} />
            {evalMut.isPending && evalMode === 'execute' ? 'Executing...' : 'Execute'}
          </button>
        </div>
      </div>

      {/* Eval result banner */}
      {evalResult !== null && (
        <div className={cn(
          'card p-4 border-l-2',
          evalResult.length === 0 ? 'border-l-green-500' : evalMode === 'execute' ? 'border-l-amber-500' : 'border-l-blue-500',
        )}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-200">
              {evalMode === 'dry_run' ? 'Dry Run' : 'Execution'} Result: {evalResult.length} action{evalResult.length !== 1 ? 's' : ''}
            </span>
            <button onClick={() => setEvalResult(null)} className="text-xs text-gray-500 hover:text-gray-300">dismiss</button>
          </div>
          {evalResult.length === 0 && (
            <p className="text-sm text-gray-400">All clear — no policies triggered.</p>
          )}
          {evalResult.map((a, i) => (
            <div key={i} className="flex items-center gap-2 text-sm py-1 border-t border-dark-border/50 first:border-t-0">
              <StatusPill label={a.proposed_action} tone={actionTone(a.proposed_action)} />
              <span className="text-gray-400">{a.target_type}/{a.target_id}</span>
              <span className="text-gray-500 ml-auto text-xs truncate max-w-[40%]">{a.reason}</span>
              {a.executed && <StatusPill label="executed" tone="green" />}
            </div>
          ))}
        </div>
      )}

      {/* Policy cards */}
      <div className="space-y-3">
        <h2 className="text-sm font-medium text-gray-300">Policies</h2>
        {policies.map((p) => {
          const expanded = expandedPolicy === p.id
          return (
            <div key={p.id} className="card">
              <div className="flex items-center gap-3 p-4">
                <button
                  onClick={() => setExpandedPolicy(expanded ? null : p.id)}
                  className="text-gray-500 hover:text-gray-300"
                >
                  {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-200">{p.label}</span>
                    <StatusPill label={p.enabled ? 'enabled' : 'disabled'} tone={p.enabled ? 'green' : 'gray'} />
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5 truncate">{p.description}</p>
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    <RelTime iso={p.last_fired_at} />
                  </span>
                  <button
                    onClick={() => toggleMut.mutate(p.id)}
                    disabled={toggleMut.isPending}
                    className={cn(
                      'relative inline-flex h-5 w-9 items-center rounded-full transition-colors',
                      p.enabled ? 'bg-primary-600' : 'bg-dark-border',
                    )}
                  >
                    <span className={cn(
                      'inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform',
                      p.enabled ? 'translate-x-4.5' : 'translate-x-0.5',
                    )} />
                  </button>
                </div>
              </div>
              {expanded && (
                <div className="border-t border-dark-border px-4 py-3 space-y-2 text-xs">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div>
                      <span className="text-gray-500">Cooldown</span>
                      <div className="text-gray-300">{p.cooldown_minutes}m</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Max Actions/Run</span>
                      <div className="text-gray-300">{p.max_actions_per_run}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Last Evaluated</span>
                      <div><RelTime iso={p.last_evaluated_at} /></div>
                    </div>
                    <div>
                      <span className="text-gray-500">Last Fired</span>
                      <div><RelTime iso={p.last_fired_at} /></div>
                    </div>
                  </div>
                  {Object.keys(p.thresholds).length > 0 && (
                    <div>
                      <span className="text-gray-500">Thresholds</span>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {Object.entries(p.thresholds).map(([k, v]) => (
                          <span key={k} className="px-2 py-0.5 rounded bg-dark-border text-gray-300">
                            {k}: {v}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* History */}
      <div>
        <h2 className="text-sm font-medium text-gray-300 mb-2">Recent Events</h2>
        {historyLoading ? (
          <div className="card p-6"><SkeletonRows count={5} /></div>
        ) : !historyData || historyData.items.length === 0 ? (
          <div className="card p-8 text-center text-gray-500">No autopilot events yet.</div>
        ) : (
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Time</th>
                  <th className="p-3">Policy</th>
                  <th className="p-3">Mode</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">Target</th>
                  <th className="p-3">Reason</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {historyData.items.map((e) => (
                  <tr key={e.id} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-400 whitespace-nowrap">
                      <RelTime iso={e.created_at} />
                    </td>
                    <td className="p-3 text-gray-300">{e.policy_key}</td>
                    <td className="p-3">
                      <StatusPill
                        label={e.mode}
                        tone={e.mode === 'execute' ? 'amber' : 'blue'}
                      />
                    </td>
                    <td className="p-3 text-gray-300">{e.proposed_action}</td>
                    <td className="p-3 text-gray-400">{e.target_type}/{e.target_id}</td>
                    <td className="p-3 text-gray-500 max-w-[200px] truncate">{e.reason}</td>
                    <td className="p-3">
                      <StatusPill
                        label={e.executed ? 'executed' : 'proposed'}
                        tone={e.executed ? 'green' : 'gray'}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
