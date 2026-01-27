/**
 * Session 824: Trigger Rules Panel
 *
 * Displays and manages self-execution trigger rules from the MetricsActionTrigger.
 * Shows rule status, allows toggling, and manual execution.
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Zap,
  Play,
  ToggleLeft,
  ToggleRight,
  Clock,
  Loader2,
  CheckCircle,
  AlertTriangle,
  X,
  ChevronRight,
  Target,
  Activity,
  Settings,
  History,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

interface TriggerRule {
  name: string
  description: string
  metric: string
  threshold: string
  priority: string
  action: string
  action_type: string
  enabled: boolean
  in_cooldown: boolean
  cooldown_minutes?: number
  last_triggered?: string
  trigger_count?: number
  condition?: string
}

interface TriggerRunResult {
  rules_evaluated: number
  conditions_met: number
  actions_triggered: number
  actions_skipped_cooldown: number
  actions: Array<{
    rule: string
    priority: string
    success: boolean
    message: string
  }>
}

// Session 830: Use api instance to include auth token
async function fetchTriggers(): Promise<{ rules: TriggerRule[]; total: number }> {
  const response = await api.get('/platform/triggers/')
  return response.data
}

async function runTriggersNow(): Promise<{ result: TriggerRunResult }> {
  const response = await api.post('/platform/triggers/run-now/')
  return { result: response.data.result }
}

function PriorityBadge({ priority }: { priority: string }) {
  const colorMap: Record<string, string> = {
    CRITICAL: 'bg-accent-red text-white',
    HIGH: 'bg-accent-amber text-black',
    MEDIUM: 'bg-primary-600 text-white',
    LOW: 'bg-gray-600 text-gray-200',
  }

  return (
    <span className={cn('px-2 py-0.5 rounded text-xs font-medium', colorMap[priority] || colorMap.LOW)}>
      {priority}
    </span>
  )
}

export function TriggerRulesPanel() {
  const queryClient = useQueryClient()
  const [lastRunResult, setLastRunResult] = useState<TriggerRunResult | null>(null)
  const [showResults, setShowResults] = useState(false)
  const [selectedRule, setSelectedRule] = useState<TriggerRule | null>(null)

  const { data, isLoading, error } = useQuery({
    queryKey: ['trigger-rules'],
    queryFn: fetchTriggers,
    staleTime: 60000,
  })

  const runMutation = useMutation({
    mutationFn: runTriggersNow,
    onSuccess: (response) => {
      setLastRunResult(response.result)
      setShowResults(true)
      queryClient.invalidateQueries({ queryKey: ['trigger-rules'] })
      queryClient.invalidateQueries({ queryKey: ['live-metrics'] })
    },
  })

  if (error) {
    return (
      <div className="card border-accent-red/50">
        <span className="text-accent-red">Failed to load trigger rules</span>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="text-accent-amber" size={18} />
          <h3 className="text-md font-semibold uppercase">Self-Execution Triggers</h3>
          {data && (
            <span className="text-xs text-gray-500">
              ({data.rules.filter((r) => r.enabled).length}/{data.total} enabled)
            </span>
          )}
        </div>
        <button
          onClick={() => runMutation.mutate()}
          disabled={runMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
        >
          {runMutation.isPending ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Play size={16} />
          )}
          Run Check Now
        </button>
      </div>

      {/* Last Run Results */}
      {showResults && lastRunResult && (
        <div className="card bg-gray-800/80 border-primary-500/50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <CheckCircle className="text-accent-green" size={16} />
              <span className="text-sm font-medium">Check Complete</span>
            </div>
            <button
              onClick={() => setShowResults(false)}
              className="text-xs text-gray-400 hover:text-white"
            >
              Dismiss
            </button>
          </div>
          <div className="grid grid-cols-4 gap-4 text-center mb-4">
            <div>
              <div className="text-2xl font-bold">{lastRunResult.rules_evaluated}</div>
              <div className="text-xs text-gray-400">Evaluated</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-accent-amber">{lastRunResult.conditions_met}</div>
              <div className="text-xs text-gray-400">Conditions Met</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-accent-green">{lastRunResult.actions_triggered}</div>
              <div className="text-xs text-gray-400">Actions Triggered</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-500">{lastRunResult.actions_skipped_cooldown}</div>
              <div className="text-xs text-gray-400">Skipped (Cooldown)</div>
            </div>
          </div>
          {lastRunResult.actions.length > 0 && (
            <div className="space-y-2">
              {lastRunResult.actions.map((action, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  {action.success ? (
                    <CheckCircle size={14} className="text-accent-green" />
                  ) : (
                    <AlertTriangle size={14} className="text-accent-red" />
                  )}
                  <PriorityBadge priority={action.priority} />
                  <span className="text-gray-300">{action.rule}:</span>
                  <span className="text-gray-400">{action.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Rules List */}
      {isLoading ? (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card animate-pulse h-16" />
          ))}
        </div>
      ) : data ? (
        <div className="space-y-2">
          {data.rules.map((rule) => (
            <button
              key={rule.name}
              onClick={() => setSelectedRule(rule)}
              className={cn(
                'card flex items-center justify-between py-3 w-full text-left cursor-pointer hover:bg-gray-800/80 transition-colors',
                !rule.enabled && 'opacity-60',
                rule.in_cooldown && 'border-accent-amber/30'
              )}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-white">{rule.name}</span>
                  <PriorityBadge priority={rule.priority} />
                  {rule.in_cooldown && (
                    <span className="flex items-center gap-1 text-xs text-accent-amber">
                      <Clock size={12} /> Cooldown
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-400">{rule.description}</p>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                  <span>Metric: {rule.metric}</span>
                  <span>Threshold: {rule.threshold}</span>
                  <span>Action: {rule.action}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 pl-4">
                {rule.enabled ? (
                  <ToggleRight size={24} className="text-accent-green" />
                ) : (
                  <ToggleLeft size={24} className="text-gray-500" />
                )}
                <ChevronRight size={16} className="text-gray-500" />
              </div>
            </button>
          ))}
        </div>
      ) : null}

      {/* Session 834: Trigger Detail Modal */}
      {selectedRule && (
        <TriggerDetailModal rule={selectedRule} onClose={() => setSelectedRule(null)} />
      )}
    </div>
  )
}

// Session 834: Trigger Detail Modal Component
interface TriggerDetailModalProps {
  rule: TriggerRule
  onClose: () => void
}

function TriggerDetailModal({ rule, onClose }: TriggerDetailModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-2xl w-full max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <Zap className="text-accent-amber" size={20} />
            <div>
              <h2 className="text-lg font-semibold text-white">{rule.name}</h2>
              <div className="flex items-center gap-2 mt-1">
                <PriorityBadge priority={rule.priority} />
                {rule.enabled ? (
                  <span className="text-xs px-2 py-0.5 bg-accent-green/20 text-accent-green rounded">
                    Enabled
                  </span>
                ) : (
                  <span className="text-xs px-2 py-0.5 bg-gray-600 text-gray-400 rounded">
                    Disabled
                  </span>
                )}
                {rule.in_cooldown && (
                  <span className="text-xs px-2 py-0.5 bg-accent-amber/20 text-accent-amber rounded flex items-center gap-1">
                    <Clock size={10} /> In Cooldown
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4 overflow-y-auto max-h-[calc(85vh-80px)]">
          {/* Description */}
          <div className="card bg-gray-800/50">
            <p className="text-sm text-gray-300">{rule.description}</p>
          </div>

          {/* Trigger Condition */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3 flex items-center gap-2">
              <Target size={14} />
              Trigger Condition
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-gray-500">Metric</span>
                <p className="text-sm text-white font-mono bg-gray-800 px-2 py-1 rounded mt-1">
                  {rule.metric}
                </p>
              </div>
              <div>
                <span className="text-xs text-gray-500">Threshold</span>
                <p className="text-sm text-accent-amber font-mono bg-gray-800 px-2 py-1 rounded mt-1">
                  {rule.threshold}
                </p>
              </div>
            </div>
            {rule.condition && (
              <div className="mt-3">
                <span className="text-xs text-gray-500">Full Condition</span>
                <p className="text-xs text-gray-300 font-mono bg-gray-800 px-2 py-1 rounded mt-1">
                  {rule.condition}
                </p>
              </div>
            )}
          </div>

          {/* Action Details */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3 flex items-center gap-2">
              <Activity size={14} />
              Action
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-gray-500">Action Name</span>
                <p className="text-sm text-white">{rule.action}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500">Action Type</span>
                <p className="text-sm text-primary-400">{rule.action_type}</p>
              </div>
            </div>
          </div>

          {/* Settings */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3 flex items-center gap-2">
              <Settings size={14} />
              Settings
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-gray-500">Cooldown Period</span>
                <p className="text-sm text-white">{rule.cooldown_minutes || 60} minutes</p>
              </div>
              <div>
                <span className="text-xs text-gray-500">Priority</span>
                <p className="text-sm text-white">{rule.priority}</p>
              </div>
            </div>
          </div>

          {/* History (if available) */}
          {(rule.last_triggered || rule.trigger_count !== undefined) && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3 flex items-center gap-2">
                <History size={14} />
                History
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {rule.last_triggered && (
                  <div>
                    <span className="text-xs text-gray-500">Last Triggered</span>
                    <p className="text-sm text-white">
                      {new Date(rule.last_triggered).toLocaleString()}
                    </p>
                  </div>
                )}
                {rule.trigger_count !== undefined && (
                  <div>
                    <span className="text-xs text-gray-500">Total Triggers</span>
                    <p className="text-sm text-white">{rule.trigger_count} times</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* How It Works */}
          <div className="card bg-primary-500/10 border-primary-500/30">
            <h3 className="text-sm font-semibold text-primary-400 mb-2">How This Trigger Works</h3>
            <p className="text-xs text-gray-400">
              When <span className="text-white font-mono">{rule.metric}</span> meets the threshold{' '}
              <span className="text-accent-amber font-mono">{rule.threshold}</span>, the system
              automatically executes <span className="text-primary-400">{rule.action}</span>.
              After triggering, a cooldown period prevents repeated execution.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
