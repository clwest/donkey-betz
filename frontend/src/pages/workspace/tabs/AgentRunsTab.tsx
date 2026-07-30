// S2930: Agent Runs tab — persistent view of AgentExecution history.
// Fixes visibility gap: dispatching an agent via Rigby returns an execution_id
// but there was no UI to find that run later without hitting the ORM.

import { useState, useMemo } from 'react'
import { useQuery, keepPreviousData } from '@tanstack/react-query'
import {
  Bot,
  Loader2,
  RefreshCw,
  Search,
  XCircle,
  ChevronLeft,
  ChevronRight,
  X,
  AlertCircle,
  CheckCircle2,
  Clock,
  PauseCircle,
  DollarSign,
  Copy,
  GitBranch,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { agentsApi } from '@/lib/api'

interface AgentRunSummary {
  id: string
  agent_name: string
  task: string | null
  task_summary: string
  status: string
  output_data: unknown
  error_message: string | null
  tokens_used: number | null
  cost: number
  execution_time_ms: number | null
  created_at: string
  completed_at: string | null
  last_heartbeat_at: string | null
}

interface AgentRunsResponse {
  success: boolean
  data: {
    executions: AgentRunSummary[]
    count: number
    total_count: number
    limit: number
    offset: number
    has_more: boolean
  }
}

interface AgentRunChild {
  execution_id: string
  agent_name: string | null
  status: string
  created_at: string | null
  completed_at: string | null
  duration_ms: number | null
}

interface AgentRunDetailResponse {
  success: boolean
  data: {
    execution: AgentRunSummary & {
      agent_display_name: string | null
      input_data: unknown
      parent_execution_id: string | null
      root_execution_id: string | null
      child_count: number
      subtree_count: number
      children: AgentRunChild[]
      children_truncated: boolean
      fanout_available: boolean
    }
    related_memory: {
      id: string
      title: string
      content: string
      valence: string
      memory_type: string
      importance_score: number
    } | null
  }
}

const PAGE_SIZE = 25

const STATUS_META: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  completed: { label: 'completed', className: 'bg-green-500/15 text-green-400 border-green-500/30', icon: CheckCircle2 },
  failed: { label: 'failed', className: 'bg-red-500/15 text-red-400 border-red-500/30', icon: XCircle },
  running: { label: 'running', className: 'bg-blue-500/15 text-blue-400 border-blue-500/30', icon: Loader2 },
  in_progress: { label: 'in progress', className: 'bg-blue-500/15 text-blue-400 border-blue-500/30', icon: Loader2 },
  pending: { label: 'pending', className: 'bg-slate-500/15 text-slate-300 border-slate-500/30', icon: Clock },
  cancelled: { label: 'cancelled', className: 'bg-slate-500/15 text-slate-400 border-slate-500/30', icon: PauseCircle },
  paused: { label: 'paused', className: 'bg-amber-500/15 text-amber-400 border-amber-500/30', icon: PauseCircle },
}

const STATUS_FILTER_OPTIONS = ['', 'completed', 'failed', 'running', 'pending', 'cancelled']

function formatDuration(ms: number | null): string {
  if (!ms || ms <= 0) return '—'
  if (ms < 1000) return `${ms}ms`
  const s = ms / 1000
  if (s < 60) return `${s.toFixed(1)}s`
  const m = Math.floor(s / 60)
  const rs = Math.round(s - m * 60)
  return `${m}m ${rs}s`
}

function formatCost(cost: number): string {
  if (!cost) return '—'
  if (cost < 0.01) return `<$0.01`
  return `$${cost.toFixed(2)}`
}

function formatRelative(iso: string): string {
  const d = new Date(iso)
  const diff = Date.now() - d.getTime()
  const s = Math.floor(diff / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const days = Math.floor(h / 24)
  if (days < 30) return `${days}d ago`
  return d.toLocaleDateString()
}

function StatusBadge({ status }: { status: string }) {
  const meta = STATUS_META[status] || { label: status, className: 'bg-slate-500/15 text-slate-300 border-slate-500/30', icon: AlertCircle }
  const Icon = meta.icon
  const spin = status === 'running' || status === 'in_progress'
  return (
    <span className={cn('inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-medium', meta.className)}>
      <Icon size={12} className={cn(spin && 'animate-spin')} />
      {meta.label}
    </span>
  )
}

function shortId(id: string): string {
  return id.length > 14 ? `${id.slice(0, 8)}…${id.slice(-4)}` : id
}

function IdChip({
  id,
  onSelect,
  clickable = true,
}: {
  id: string
  onSelect: (id: string) => void
  clickable?: boolean
}) {
  return (
    <span className="inline-flex items-center gap-1 font-mono text-xs">
      {clickable ? (
        <button
          onClick={() => onSelect(id)}
          className="text-slate-100 hover:text-blue-300 hover:underline"
          title={`Navigate to ${id}`}
        >
          {shortId(id)}
        </button>
      ) : (
        <span className="text-slate-100" title={id}>{shortId(id)}</span>
      )}
      <button
        onClick={(e) => {
          e.stopPropagation()
          navigator.clipboard?.writeText(id)
        }}
        className="rounded p-0.5 text-slate-500 hover:bg-slate-800 hover:text-slate-200"
        title="Copy full ID"
        aria-label="Copy full execution ID"
      >
        <Copy size={10} />
      </button>
    </span>
  )
}

function JsonBlock({ value }: { value: unknown }) {
  if (value === null || value === undefined) return <span className="text-slate-500 italic">null</span>
  const text = typeof value === 'string' ? value : JSON.stringify(value, null, 2)
  return (
    <pre className="max-h-96 overflow-auto rounded bg-slate-950/60 p-3 text-xs text-slate-200 whitespace-pre-wrap break-words border border-slate-800">
      {text}
    </pre>
  )
}

function DetailPanel({
  executionId,
  onClose,
  onSelectExecution,
}: {
  executionId: string
  onClose: () => void
  onSelectExecution: (id: string) => void
}) {
  const { data, isLoading, error } = useQuery<AgentRunDetailResponse>({
    queryKey: ['agent-execution-detail', executionId],
    queryFn: async () => {
      const res = await agentsApi.executionDetail(executionId)
      return res.data
    },
  })

  const ex = data?.data?.execution
  const mem = data?.data?.related_memory

  return (
    <aside className="flex h-full w-full max-w-2xl flex-col border-l border-slate-800 bg-slate-900/95">
      <header className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Bot size={16} className="text-slate-400" />
            <span className="truncate text-sm font-semibold text-slate-100">
              {ex?.agent_name || 'Loading…'}
            </span>
            {ex && <StatusBadge status={ex.status} />}
          </div>
          <div className="mt-1 truncate text-xs text-slate-500 font-mono">{executionId}</div>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
          aria-label="Close detail panel"
        >
          <X size={18} />
        </button>
      </header>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        {isLoading && (
          <div className="flex items-center justify-center py-12 text-slate-400">
            <Loader2 size={20} className="animate-spin" />
          </div>
        )}
        {!!error && (
          <div className="rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
            Failed to load execution detail.
          </div>
        )}
        {ex && (
          <>
            <section>
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">Task</h3>
              <div className="rounded border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-200 whitespace-pre-wrap">
                {ex.task || <span className="text-slate-500 italic">no task recorded</span>}
              </div>
            </section>

            <section className="grid grid-cols-3 gap-3 text-xs">
              <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                <div className="text-slate-500 uppercase tracking-wide">Duration</div>
                <div className="mt-0.5 font-mono text-slate-100">{formatDuration(ex.execution_time_ms)}</div>
              </div>
              <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                <div className="text-slate-500 uppercase tracking-wide">Tokens</div>
                <div className="mt-0.5 font-mono text-slate-100">{ex.tokens_used?.toLocaleString() ?? '—'}</div>
              </div>
              <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                <div className="text-slate-500 uppercase tracking-wide">Cost</div>
                <div className="mt-0.5 font-mono text-slate-100">{formatCost(ex.cost)}</div>
              </div>
            </section>

            {ex.fanout_available && (
              <section>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2 flex items-center gap-1.5">
                  <GitBranch size={12} />
                  Lineage &amp; Fanout
                </h3>

                {(ex.parent_execution_id || ex.root_execution_id) && (
                  <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                    <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                      <div className="text-slate-500 uppercase tracking-wide mb-1">Parent</div>
                      {ex.parent_execution_id ? (
                        <IdChip id={ex.parent_execution_id} onSelect={onSelectExecution} />
                      ) : (
                        <span className="text-slate-500 italic text-xs">root execution</span>
                      )}
                    </div>
                    <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                      <div className="text-slate-500 uppercase tracking-wide mb-1">Root</div>
                      {ex.root_execution_id && ex.root_execution_id !== ex.id ? (
                        <IdChip id={ex.root_execution_id} onSelect={onSelectExecution} />
                      ) : (
                        <span className="text-slate-500 italic text-xs">this run</span>
                      )}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                  <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                    <div className="text-slate-500 uppercase tracking-wide">Direct children</div>
                    <div className="mt-0.5 font-mono text-slate-100">{ex.child_count}</div>
                  </div>
                  <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                    <div className="text-slate-500 uppercase tracking-wide">Subtree size</div>
                    <div className="mt-0.5 font-mono text-slate-100">{ex.subtree_count}</div>
                  </div>
                </div>

                {ex.child_count === 0 ? (
                  <div className="rounded border border-slate-800 bg-slate-950/40 p-3 text-xs text-slate-500 italic">
                    No sub-executions.
                  </div>
                ) : (
                  <div className="rounded border border-slate-800 bg-slate-950/40 divide-y divide-slate-800/60">
                    {ex.children.map((child) => (
                      <button
                        key={child.execution_id}
                        onClick={() => onSelectExecution(child.execution_id)}
                        className="flex w-full items-center gap-2 px-2.5 py-1.5 text-left hover:bg-slate-800/40"
                      >
                        <span className="font-mono text-xs text-slate-200 truncate max-w-[10rem]">
                          {child.agent_name || 'unknown'}
                        </span>
                        <StatusBadge status={child.status} />
                        <span className="ml-auto flex items-center gap-2 text-xs text-slate-400">
                          <span className="font-mono">{formatDuration(child.duration_ms)}</span>
                          {child.created_at && <span>{formatRelative(child.created_at)}</span>}
                        </span>
                      </button>
                    ))}
                    {ex.children_truncated && (
                      <div className="px-2.5 py-1.5 text-xs text-slate-500 italic">
                        + {ex.child_count - ex.children.length} more (showing first {ex.children.length})
                      </div>
                    )}
                  </div>
                )}
              </section>
            )}

            <section>
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">Input</h3>
              <JsonBlock value={ex.input_data} />
            </section>

            <section>
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">Output</h3>
              <JsonBlock value={ex.output_data} />
            </section>

            {ex.error_message && (
              <section>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-red-400 mb-2">Error</h3>
                <pre className="max-h-96 overflow-auto rounded border border-red-500/40 bg-red-500/10 p-3 text-xs text-red-200 whitespace-pre-wrap break-words">
                  {ex.error_message}
                </pre>
              </section>
            )}

            {mem && (
              <section>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                  Related memory · {mem.memory_type} · {mem.valence}
                </h3>
                <div className="rounded border border-slate-800 bg-slate-950/60 p-3 text-sm">
                  <div className="font-medium text-slate-200">{mem.title}</div>
                  <div className="mt-1 text-slate-300 whitespace-pre-wrap">{mem.content}</div>
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </aside>
  )
}

export function AgentRunsTab() {
  const [offset, setOffset] = useState(0)
  const [agentFilter, setAgentFilter] = useState('')
  const [agentFilterDraft, setAgentFilterDraft] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const params = useMemo(
    () => ({
      limit: PAGE_SIZE,
      offset,
      ...(agentFilter ? { agent_name: agentFilter } : {}),
      ...(statusFilter ? { status: statusFilter } : {}),
    }),
    [offset, agentFilter, statusFilter],
  )

  const { data, isLoading, isFetching, error, refetch } = useQuery<AgentRunsResponse>({
    queryKey: ['agent-runs', params],
    queryFn: async () => {
      const res = await agentsApi.unifiedExecutions(params)
      return res.data
    },
    placeholderData: keepPreviousData,
    refetchInterval: 30000,
  })

  const runs = data?.data?.executions || []
  const totalCount = data?.data?.total_count || 0
  const hasMore = data?.data?.has_more || false
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE))

  const applyAgentFilter = () => {
    setAgentFilter(agentFilterDraft.trim())
    setOffset(0)
  }

  const resetFilters = () => {
    setAgentFilter('')
    setAgentFilterDraft('')
    setStatusFilter('')
    setOffset(0)
  }

  return (
    <div className="flex h-full">
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <Bot size={18} className="text-slate-400" />
              Agent Runs
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Recent AgentExecution history · click any row for full input/output
            </p>
          </div>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="rounded border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800 disabled:opacity-50 flex items-center gap-1.5"
          >
            <RefreshCw size={12} className={cn(isFetching && 'animate-spin')} />
            Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 px-4 py-2.5">
          <div className="relative flex-1 min-w-64 max-w-md">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={agentFilterDraft}
              onChange={(e) => setAgentFilterDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && applyAgentFilter()}
              placeholder="Filter by agent name…"
              className="w-full rounded border border-slate-700 bg-slate-900 pl-8 pr-3 py-1.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <button
            onClick={applyAgentFilter}
            className="rounded border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800"
          >
            Apply
          </button>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setOffset(0)
            }}
            className="rounded border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-100 focus:border-blue-500 focus:outline-none"
          >
            {STATUS_FILTER_OPTIONS.map((s) => (
              <option key={s || 'any'} value={s}>
                {s || 'any status'}
              </option>
            ))}
          </select>
          {(agentFilter || statusFilter) && (
            <button
              onClick={resetFilters}
              className="rounded px-2 py-1 text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          )}
          <div className="ml-auto text-xs text-slate-500">
            {totalCount.toLocaleString()} run{totalCount === 1 ? '' : 's'}
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          {isLoading && (
            <div className="flex items-center justify-center py-16 text-slate-400">
              <Loader2 size={20} className="animate-spin" />
            </div>
          )}
          {!!error && (
            <div className="m-4 rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
              Failed to load agent runs.
            </div>
          )}
          {!isLoading && !error && runs.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500">
              <Bot size={32} className="mb-2 opacity-40" />
              <div className="text-sm">No agent runs match these filters.</div>
            </div>
          )}
          {!isLoading && runs.length > 0 && (
            <table className="w-full text-sm">
              <thead className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur border-b border-slate-800">
                <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-2 font-medium">Agent</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Task</th>
                  <th className="px-4 py-2 font-medium">When</th>
                  <th className="px-4 py-2 font-medium text-right">Duration</th>
                  <th className="px-4 py-2 font-medium text-right">Cost</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr
                    key={run.id}
                    onClick={() => setSelectedId(run.id)}
                    className={cn(
                      'cursor-pointer border-b border-slate-800/60 hover:bg-slate-800/40',
                      selectedId === run.id && 'bg-slate-800/60',
                    )}
                  >
                    <td className="px-4 py-2 font-mono text-xs text-slate-200 whitespace-nowrap">
                      {run.agent_name}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="px-4 py-2 text-slate-300 max-w-md truncate">
                      {run.task_summary}
                    </td>
                    <td className="px-4 py-2 text-xs text-slate-400 whitespace-nowrap" title={run.created_at}>
                      {formatRelative(run.created_at)}
                    </td>
                    <td className="px-4 py-2 text-xs text-slate-300 font-mono text-right whitespace-nowrap">
                      {formatDuration(run.execution_time_ms)}
                    </td>
                    <td className="px-4 py-2 text-xs text-slate-300 font-mono text-right whitespace-nowrap">
                      {run.cost > 0 && <DollarSign size={10} className="inline mr-0.5 text-slate-500" />}
                      {formatCost(run.cost)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {totalCount > PAGE_SIZE && (
          <div className="flex items-center justify-between border-t border-slate-800 px-4 py-2">
            <div className="text-xs text-slate-500">
              Page {currentPage} of {totalPages} · showing {runs.length} of {totalCount.toLocaleString()}
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                disabled={offset === 0}
                className="rounded border border-slate-700 bg-slate-800/50 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={14} />
              </button>
              <button
                onClick={() => setOffset(offset + PAGE_SIZE)}
                disabled={!hasMore}
                className="rounded border border-slate-700 bg-slate-800/50 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {selectedId && (
        <DetailPanel
          executionId={selectedId}
          onClose={() => setSelectedId(null)}
          onSelectExecution={setSelectedId}
        />
      )}
    </div>
  )
}

export default AgentRunsTab
