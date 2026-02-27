import { useState } from 'react'
import { useAgentFleet, useAgentRunNow, useAgentPause, useAgentResume } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { AgentFleetItem } from '@/types/cockpit'
import { Bot, Search, Play, Pause, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '@/lib/cn'

const RANGE_OPTIONS = [
  { value: 6, label: '6h' },
  { value: 24, label: '24h' },
  { value: 168, label: '7d' },
]

function healthTone(agent: AgentFleetItem): Tone {
  if (!agent.cockpit_enabled) return 'gray'
  if (agent.recent_failed > 0 && agent.recent_total > 0) {
    const rate = agent.recent_failed / agent.recent_total
    if (rate > 0.5) return 'red'
    if (rate > 0.2) return 'amber'
  }
  if (agent.recent_total === 0) return 'gray'
  return 'green'
}

function healthLabel(agent: AgentFleetItem): string {
  if (!agent.cockpit_enabled) return 'paused'
  if (agent.recent_total === 0) return 'idle'
  const rate = agent.recent_total > 0 ? Math.round((agent.recent_completed / agent.recent_total) * 100) : 0
  return `${rate}%`
}

function AgentRow({ agent }: { agent: AgentFleetItem }) {
  const [expanded, setExpanded] = useState(false)
  const [pauseReason, setPauseReason] = useState('')
  const runNow = useAgentRunNow()
  const pause = useAgentPause()
  const resume = useAgentResume()

  return (
    <div className={cn('card p-3', !agent.cockpit_enabled && 'opacity-60')}>
      <button
        className="flex w-full items-center gap-3 text-left"
        onClick={() => setExpanded((e) => !e)}
      >
        <Bot size={16} className="text-gray-500 shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-200 truncate">{agent.name}</span>
            <StatusPill label={healthLabel(agent)} tone={healthTone(agent)} />
            {agent.category && (
              <span className="text-xs text-gray-600 hidden sm:inline">{agent.category}</span>
            )}
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-500 mt-0.5">
            <span>{agent.specialization || agent.agent_type}</span>
            <span>{agent.recent_completed}/{agent.recent_total} runs</span>
            {agent.recent_failed > 0 && (
              <span className="text-red-400">{agent.recent_failed} failed</span>
            )}
            {agent.last_run_at && (
              <span className="hidden md:inline">{new Date(agent.last_run_at).toLocaleString()}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {agent.cockpit_enabled ? (
            <span className="text-xs text-gray-600">eff {agent.effectiveness_score}%</span>
          ) : (
            <span className="text-xs text-amber-400">paused</span>
          )}
          {expanded ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
        </div>
      </button>

      {expanded && (
        <div className="mt-3 pt-2 border-t border-dark-border/50 space-y-3">
          {/* Pause reason */}
          {!agent.cockpit_enabled && agent.paused_reason && (
            <p className="text-xs text-amber-400">Paused: {agent.paused_reason}</p>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 flex-wrap">
            {agent.cockpit_enabled ? (
              <>
                <button
                  onClick={() => runNow.mutate({ agentName: agent.name })}
                  disabled={runNow.isPending}
                  className="btn text-xs py-1 px-2 flex items-center gap-1"
                >
                  <Play size={12} />
                  {runNow.isPending ? 'Queuing...' : 'Run Now'}
                </button>
                <div className="flex items-center gap-1">
                  <input
                    type="text"
                    value={pauseReason}
                    onChange={(e) => setPauseReason(e.target.value)}
                    placeholder="Reason (optional)"
                    className="input text-xs py-1 px-2 w-40"
                    onClick={(e) => e.stopPropagation()}
                  />
                  <button
                    onClick={() => {
                      pause.mutate({ agentName: agent.name, reason: pauseReason })
                      setPauseReason('')
                    }}
                    disabled={pause.isPending}
                    className="btn text-xs py-1 px-2 flex items-center gap-1 text-amber-400 hover:text-amber-300"
                  >
                    <Pause size={12} />
                    {pause.isPending ? 'Pausing...' : 'Pause'}
                  </button>
                </div>
              </>
            ) : (
              <button
                onClick={() => resume.mutate(agent.name)}
                disabled={resume.isPending}
                className="btn text-xs py-1 px-2 flex items-center gap-1 text-green-400 hover:text-green-300"
              >
                <RotateCcw size={12} />
                {resume.isPending ? 'Resuming...' : 'Resume'}
              </button>
            )}
          </div>

          {/* Mutation feedback */}
          {runNow.isSuccess && (
            <p className="text-xs text-green-400">Queued: task {runNow.data.task_id?.slice(0, 8)}</p>
          )}
          {runNow.isError && (
            <p className="text-xs text-red-400">Failed to queue run</p>
          )}
        </div>
      )}
    </div>
  )
}

export default function AgentsPage() {
  const [search, setSearch] = useState('')
  const [hours, setHours] = useState(24)

  const { data, isLoading } = useAgentFleet({ q: search || undefined, hours })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Agent Fleet</h1>
        <div className="card p-6"><SkeletonRows count={10} /></div>
      </div>
    )
  }

  const paused = data?.items.filter((a) => !a.cockpit_enabled).length ?? 0
  const failing = data?.items.filter((a) => a.recent_failed > 0).length ?? 0

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Bot size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Agent Fleet</h1>
        {data && (
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary-600/20 text-primary-400">
            {data.total}
          </span>
        )}
        {paused > 0 && (
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-amber-600/20 text-amber-400">
            {paused} paused
          </span>
        )}
        {failing > 0 && (
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-600/20 text-red-400">
            {failing} failing
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search agents..."
            className="input text-sm py-1.5 pl-8 w-full"
          />
        </div>

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

      {/* Agent list */}
      {!data || data.items.length === 0 ? (
        <div className="card p-8 text-center text-gray-500">
          No agents found.
        </div>
      ) : (
        <div className="space-y-2">
          {data.items.map((agent) => (
            <AgentRow key={agent.id} agent={agent} />
          ))}
        </div>
      )}
    </div>
  )
}
