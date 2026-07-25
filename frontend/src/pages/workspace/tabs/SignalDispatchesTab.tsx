// S2934 A4: Signal Dispatches tab — observability surface for the
// signal-triggered agent auto-dispatch pipeline (S2933 A3 v1).
// Shows recent SignalDispatch rows so operators can see what fired,
// against which cluster, and whether the target agent succeeded.

import { useState, useMemo, useEffect } from 'react'
import { useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query'
import {
  Radio,
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
  Ban,
  Zap,
  Send,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { agentsApi } from '@/lib/api'

interface SignalDispatchRow {
  id: string
  rule_key: string
  pattern_type: string
  agent_name: string
  outcome: string
  error_summary: string
  signal_cluster_id: string | null
  signal_cluster_name: string | null
  agent_execution_id: string | null
  scan_run_id: string
  dispatched_at: string
  completed_at: string | null
  input_payload: Record<string, unknown>
}

interface SignalDispatchListResponse {
  success: boolean
  data: {
    dispatches: SignalDispatchRow[]
    count: number
    total_count: number
    limit: number
    offset: number
    has_more: boolean
  }
}

const PAGE_SIZE = 25

const OUTCOME_META: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  succeeded: { label: 'succeeded', className: 'bg-green-500/15 text-green-400 border-green-500/30', icon: CheckCircle2 },
  failed: { label: 'failed', className: 'bg-red-500/15 text-red-400 border-red-500/30', icon: XCircle },
  queued: { label: 'queued', className: 'bg-slate-500/15 text-slate-300 border-slate-500/30', icon: Clock },
  dispatched: { label: 'dispatched', className: 'bg-blue-500/15 text-blue-400 border-blue-500/30', icon: Loader2 },
  skipped_cap: { label: 'skipped (cap)', className: 'bg-amber-500/15 text-amber-400 border-amber-500/30', icon: Ban },
  skipped_not_actionable: { label: 'skipped (gate)', className: 'bg-amber-500/15 text-amber-400 border-amber-500/30', icon: Ban },
  rejected_agent_missing: { label: 'rejected (agent)', className: 'bg-red-500/15 text-red-400 border-red-500/30', icon: XCircle },
  rejected_unknown_rule: { label: 'rejected (rule)', className: 'bg-red-500/15 text-red-400 border-red-500/30', icon: XCircle },
}

const OUTCOME_FILTER_OPTIONS = ['', 'succeeded', 'failed', 'queued', 'skipped_cap', 'rejected_agent_missing', 'rejected_unknown_rule']

function formatDuration(start: string, end: string | null): string {
  if (!end) return '—'
  const ms = new Date(end).getTime() - new Date(start).getTime()
  if (ms <= 0) return '—'
  if (ms < 1000) return `${ms}ms`
  const s = ms / 1000
  if (s < 60) return `${s.toFixed(1)}s`
  const m = Math.floor(s / 60)
  const rs = Math.round(s - m * 60)
  return `${m}m ${rs}s`
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

function OutcomeBadge({ outcome }: { outcome: string }) {
  const meta = OUTCOME_META[outcome] || { label: outcome, className: 'bg-slate-500/15 text-slate-300 border-slate-500/30', icon: AlertCircle }
  const Icon = meta.icon
  const spin = outcome === 'dispatched'
  return (
    <span className={cn('inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-medium', meta.className)}>
      <Icon size={12} className={cn(spin && 'animate-spin')} />
      {meta.label}
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

// S2947 A8 + S2948 NEW-4: manual-dispatch modal.
// v1 (S2947): paste cluster UUID → inline resolve → rule pick → submit.
// v2 (S2948): searchable cluster picker (Shape B) — no paste needed.

interface EligibleCluster {
  id: string
  name: string
  pattern_type: string
  strength: number
  confidence: number
  status: string
  detected_at: string | null
  matching_rules: { key: string; agent_name: string }[]
  guard_blocked_rules: string[]
}

function ManualDispatchModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<EligibleCluster | null>(null)
  const [ruleKey, setRuleKey] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const { data, isLoading, error, refetch } = useQuery<{ success: boolean; data: { eligible: EligibleCluster[] } }>({
    queryKey: ['signal-dispatches-eligible'],
    queryFn: async () => {
      const r = await agentsApi.signalDispatchesEligible({ limit: 100 })
      return r.data
    },
    staleTime: 30_000,
  })

  const eligible = data?.data?.eligible || []
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return eligible
    return eligible.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.pattern_type.toLowerCase().includes(q) ||
        c.id.toLowerCase().includes(q),
    )
  }, [eligible, search])

  // When a cluster is picked, auto-select rule if there's exactly one.
  useEffect(() => {
    if (!selected) {
      setRuleKey('')
      return
    }
    if (selected.matching_rules.length === 1) {
      setRuleKey(selected.matching_rules[0].key)
    } else {
      setRuleKey('')
    }
  }, [selected])

  const canSubmit =
    selected !== null &&
    selected.matching_rules.length > 0 &&
    ruleKey !== '' &&
    !submitting

  const handleSubmit = async () => {
    if (!canSubmit || !selected) return
    setSubmitting(true)
    setSubmitError(null)
    try {
      await agentsApi.signalDispatchesManual({
        cluster_id: selected.id,
        rule_key: ruleKey,
      })
      onCreated()
      onClose()
    } catch (err: unknown) {
      const errObj = err as { response?: { data?: { error?: string; error_code?: string } } }
      const detail = errObj?.response?.data?.error
      const code = errObj?.response?.data?.error_code
      setSubmitError(detail || `Failed (${code || 'unknown'})`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-2xl rounded-lg border border-slate-700 bg-slate-900 shadow-2xl">
        <header className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <div className="flex items-center gap-2">
            <Send size={16} className="text-amber-400" />
            <h3 className="text-sm font-semibold text-slate-100">Manual dispatch</h3>
            <span className="text-xs text-slate-500">
              · {eligible.length} eligible cluster{eligible.length === 1 ? '' : 's'}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => refetch()}
              disabled={isLoading}
              className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
              aria-label="Refresh cluster list"
              title="Refresh"
            >
              <RefreshCw size={14} className={cn(isLoading && 'animate-spin')} />
            </button>
            <button
              onClick={onClose}
              className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
              aria-label="Close"
            >
              <X size={18} />
            </button>
          </div>
        </header>

        <div className="grid grid-cols-2 divide-x divide-slate-800">
          {/* Left: searchable cluster list */}
          <div className="flex max-h-[26rem] flex-col">
            <div className="border-b border-slate-800 p-3">
              <div className="relative">
                <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter by name, pattern, or ID…"
                  className="w-full rounded border border-slate-700 bg-slate-950 pl-8 pr-3 py-1.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex-1 overflow-auto">
              {isLoading && (
                <div className="flex items-center justify-center py-8 text-slate-400">
                  <Loader2 size={16} className="animate-spin" />
                </div>
              )}
              {!!error && (
                <div className="m-3 rounded border border-red-500/40 bg-red-500/10 p-2 text-xs text-red-300">
                  Failed to load eligible clusters.
                </div>
              )}
              {!isLoading && !error && filtered.length === 0 && (
                <div className="p-4 text-center text-xs text-slate-500">
                  {eligible.length === 0
                    ? 'No active clusters have a matching dispatch rule right now.'
                    : 'No clusters match your filter.'}
                </div>
              )}
              {!isLoading && filtered.length > 0 && (
                <ul className="divide-y divide-slate-800/60">
                  {filtered.map((c) => (
                    <li key={c.id}>
                      <button
                        onClick={() => setSelected(c)}
                        className={cn(
                          'block w-full px-3 py-2 text-left hover:bg-slate-800/40',
                          selected?.id === c.id && 'bg-slate-800/60',
                        )}
                      >
                        <div className="truncate text-sm text-slate-100">{c.name || '(no name)'}</div>
                        <div className="mt-0.5 flex items-center gap-2 text-xs text-slate-500">
                          <span className="font-mono">{c.pattern_type}</span>
                          <span>·</span>
                          <span>str {c.strength.toFixed(2)}</span>
                          <span>·</span>
                          <span>conf {c.confidence.toFixed(2)}</span>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Right: selected cluster preview + rule + submit */}
          <div className="max-h-[26rem] space-y-4 overflow-auto p-4">
            {!selected && (
              <div className="flex h-full flex-col items-center justify-center text-center text-xs text-slate-500">
                <Radio size={24} className="mb-2 opacity-40" />
                Pick a cluster on the left to preview + dispatch.
              </div>
            )}

            {selected && (
              <>
                <div className="rounded border border-slate-800 bg-slate-950/60 p-3">
                  <div className="text-sm font-medium text-slate-100">{selected.name || '(no name)'}</div>
                  <div className="mt-0.5 truncate font-mono text-[10px] text-slate-600">{selected.id}</div>
                  <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-400">
                    <div>
                      <span className="text-slate-500">Pattern:</span>{' '}
                      <span className="font-mono text-slate-200">{selected.pattern_type}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Status:</span>{' '}
                      <span className="font-mono text-green-400">{selected.status}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Strength:</span>{' '}
                      <span className="font-mono text-slate-200">{selected.strength.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Confidence:</span>{' '}
                      <span className="font-mono text-slate-200">{selected.confidence.toFixed(2)}</span>
                    </div>
                  </div>
                  {selected.guard_blocked_rules.length > 0 && (
                    <div className="mt-2 flex items-start gap-1 text-xs text-amber-400">
                      <AlertCircle size={12} className="mt-0.5 flex-shrink-0" />
                      <span>
                        {selected.guard_blocked_rules.length === selected.matching_rules.length
                          ? 'All matching rules guard-blocked (5-min window). Wait or pick another cluster.'
                          : `${selected.guard_blocked_rules.length} of ${selected.matching_rules.length} rules guard-blocked.`}
                      </span>
                    </div>
                  )}
                </div>

                <div>
                  <label htmlFor="rule-select" className="mb-1 block text-xs font-medium text-slate-400">
                    Rule
                  </label>
                  <select
                    id="rule-select"
                    value={ruleKey}
                    onChange={(e) => setRuleKey(e.target.value)}
                    className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-1.5 text-sm text-slate-100 focus:border-blue-500 focus:outline-none"
                  >
                    {selected.matching_rules.length > 1 && (
                      <option value="">Select rule…</option>
                    )}
                    {selected.matching_rules.map((r) => (
                      <option key={r.key} value={r.key}>
                        {r.key} → {r.agent_name}
                      </option>
                    ))}
                  </select>
                </div>

                {submitError && (
                  <div className="rounded border border-red-500/40 bg-red-500/10 p-2 text-xs text-red-300">
                    {submitError}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <footer className="flex items-center justify-end gap-2 border-t border-slate-800 px-4 py-3">
          <button
            onClick={onClose}
            className="rounded border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="inline-flex items-center gap-1.5 rounded border border-amber-500/60 bg-amber-500/20 px-3 py-1.5 text-xs font-medium text-amber-200 hover:bg-amber-500/30 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {submitting ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
            Dispatch
          </button>
        </footer>
      </div>
    </div>
  )
}

function DetailPanel({ row, onClose }: { row: SignalDispatchRow; onClose: () => void }) {
  return (
    <aside className="flex h-full w-full max-w-2xl flex-col border-l border-slate-800 bg-slate-900/95">
      <header className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Radio size={16} className="text-slate-400" />
            <span className="truncate text-sm font-semibold text-slate-100">
              {row.rule_key}
            </span>
            <OutcomeBadge outcome={row.outcome} />
          </div>
          <div className="mt-1 truncate text-xs text-slate-500 font-mono">{row.id}</div>
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
        <section className="grid grid-cols-2 gap-3 text-xs">
          <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
            <div className="text-slate-500 uppercase tracking-wide">Pattern</div>
            <div className="mt-0.5 font-mono text-slate-100">{row.pattern_type}</div>
          </div>
          <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
            <div className="text-slate-500 uppercase tracking-wide">Agent</div>
            <div className="mt-0.5 font-mono text-slate-100">{row.agent_name}</div>
          </div>
          <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
            <div className="text-slate-500 uppercase tracking-wide">Duration</div>
            <div className="mt-0.5 font-mono text-slate-100">{formatDuration(row.dispatched_at, row.completed_at)}</div>
          </div>
          <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
            <div className="text-slate-500 uppercase tracking-wide">Scan Run</div>
            <div className="mt-0.5 font-mono text-slate-100 truncate" title={row.scan_run_id}>
              {row.scan_run_id || '—'}
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
            Triggering cluster
          </h3>
          <div className="rounded border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-200">
            <div className="font-medium">{row.signal_cluster_name || '(no name)'}</div>
            <div className="mt-1 text-xs text-slate-500 font-mono">{row.signal_cluster_id || '—'}</div>
          </div>
        </section>

        {row.agent_execution_id && (
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
              Agent execution
            </h3>
            <div className="rounded border border-slate-800 bg-slate-950/60 p-3 text-xs font-mono text-slate-300 break-all">
              {row.agent_execution_id}
            </div>
          </section>
        )}

        <section>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
            Input payload
          </h3>
          <JsonBlock value={row.input_payload} />
        </section>

        {row.error_summary && (
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-red-400 mb-2">Error</h3>
            <pre className="max-h-96 overflow-auto rounded border border-red-500/40 bg-red-500/10 p-3 text-xs text-red-200 whitespace-pre-wrap break-words">
              {row.error_summary}
            </pre>
          </section>
        )}
      </div>
    </aside>
  )
}

export function SignalDispatchesTab() {
  const [offset, setOffset] = useState(0)
  const [patternFilter, setPatternFilter] = useState('')
  const [patternFilterDraft, setPatternFilterDraft] = useState('')
  const [outcomeFilter, setOutcomeFilter] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [manualOpen, setManualOpen] = useState(false)
  const queryClient = useQueryClient()

  const params = useMemo(
    () => ({
      limit: PAGE_SIZE,
      offset,
      ...(patternFilter ? { pattern_type: patternFilter } : {}),
      ...(outcomeFilter ? { outcome: outcomeFilter } : {}),
    }),
    [offset, patternFilter, outcomeFilter],
  )

  const { data, isLoading, isFetching, error, refetch } = useQuery<SignalDispatchListResponse>({
    queryKey: ['signal-dispatches', params],
    queryFn: async () => {
      const res = await agentsApi.signalDispatches(params)
      return res.data
    },
    placeholderData: keepPreviousData,
    refetchInterval: 30000,
  })

  const rows = data?.data?.dispatches || []
  const totalCount = data?.data?.total_count || 0
  const hasMore = data?.data?.has_more || false
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE))
  const selectedRow = selectedId ? rows.find((r) => r.id === selectedId) || null : null

  const applyPatternFilter = () => {
    setPatternFilter(patternFilterDraft.trim())
    setOffset(0)
  }

  const resetFilters = () => {
    setPatternFilter('')
    setPatternFilterDraft('')
    setOutcomeFilter('')
    setOffset(0)
  }

  return (
    <div className="flex h-full">
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <Radio size={18} className="text-slate-400" />
              Signal Dispatches
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Signal-triggered agent auto-dispatch history (S2933 A3 pipeline) · click any row for cluster + payload detail
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setManualOpen(true)}
              className="inline-flex items-center gap-1.5 rounded border border-amber-500/60 bg-amber-500/15 px-3 py-1.5 text-xs font-medium text-amber-200 hover:bg-amber-500/25"
              title="Manually dispatch a specific cluster (paste UUID)"
            >
              <Send size={12} />
              Dispatch now
            </button>
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="rounded border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800 disabled:opacity-50 flex items-center gap-1.5"
            >
              <RefreshCw size={12} className={cn(isFetching && 'animate-spin')} />
              Refresh
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 px-4 py-2.5">
          <div className="relative flex-1 min-w-64 max-w-md">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={patternFilterDraft}
              onChange={(e) => setPatternFilterDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && applyPatternFilter()}
              placeholder="Filter by pattern_type…"
              className="w-full rounded border border-slate-700 bg-slate-900 pl-8 pr-3 py-1.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <button
            onClick={applyPatternFilter}
            className="rounded border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800"
          >
            Apply
          </button>
          <select
            value={outcomeFilter}
            onChange={(e) => {
              setOutcomeFilter(e.target.value)
              setOffset(0)
            }}
            className="rounded border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-100 focus:border-blue-500 focus:outline-none"
          >
            {OUTCOME_FILTER_OPTIONS.map((s) => (
              <option key={s || 'any'} value={s}>
                {s || 'any outcome'}
              </option>
            ))}
          </select>
          {(patternFilter || outcomeFilter) && (
            <button
              onClick={resetFilters}
              className="rounded px-2 py-1 text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          )}
          <div className="ml-auto text-xs text-slate-500">
            {totalCount.toLocaleString()} dispatch{totalCount === 1 ? '' : 'es'}
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
              Failed to load signal dispatches.
            </div>
          )}
          {!isLoading && !error && rows.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500">
              <Radio size={32} className="mb-2 opacity-40" />
              <div className="text-sm">No signal dispatches yet.</div>
              <div className="text-xs mt-1 opacity-60">
                The scanner runs every 5 min. Use{' '}
                <code className="rounded bg-slate-800 px-1 py-0.5 text-slate-300">
                  python manage.py dispatch_signal --cluster-id X
                </code>{' '}
                to synthesize one.
              </div>
            </div>
          )}
          {!isLoading && rows.length > 0 && (
            <table className="w-full text-sm">
              <thead className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur border-b border-slate-800">
                <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-2 font-medium">When</th>
                  <th className="px-4 py-2 font-medium">Pattern</th>
                  <th className="px-4 py-2 font-medium">Agent</th>
                  <th className="px-4 py-2 font-medium">Outcome</th>
                  <th className="px-4 py-2 font-medium">Cluster</th>
                  <th className="px-4 py-2 font-medium">Scan Run</th>
                  <th className="px-4 py-2 font-medium text-right">Duration</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => setSelectedId(row.id)}
                    className={cn(
                      'cursor-pointer border-b border-slate-800/60 hover:bg-slate-800/40',
                      selectedId === row.id && 'bg-slate-800/60',
                    )}
                  >
                    <td className="px-4 py-2 text-xs text-slate-400 whitespace-nowrap" title={row.dispatched_at}>
                      {formatRelative(row.dispatched_at)}
                    </td>
                    <td className="px-4 py-2 font-mono text-xs text-slate-200 whitespace-nowrap">
                      {row.pattern_type}
                    </td>
                    <td className="px-4 py-2 font-mono text-xs text-slate-200 whitespace-nowrap">
                      {row.agent_name}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      <OutcomeBadge outcome={row.outcome} />
                    </td>
                    <td className="px-4 py-2 text-slate-300 max-w-xs truncate" title={row.signal_cluster_name || ''}>
                      {row.signal_cluster_name || <span className="text-slate-500 italic">—</span>}
                    </td>
                    <td className="px-4 py-2 text-xs text-slate-400 font-mono whitespace-nowrap">
                      {row.scan_run_id === 'manual' ? (
                        <span className="inline-flex items-center gap-1 text-amber-400" title="Manual dispatch via dispatch_signal">
                          <Zap size={10} /> manual
                        </span>
                      ) : (
                        <span className="truncate inline-block max-w-[8ch]" title={row.scan_run_id}>
                          {row.scan_run_id || '—'}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-xs text-slate-300 font-mono text-right whitespace-nowrap">
                      {formatDuration(row.dispatched_at, row.completed_at)}
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
              Page {currentPage} of {totalPages} · showing {rows.length} of {totalCount.toLocaleString()}
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

      {selectedRow && (
        <DetailPanel row={selectedRow} onClose={() => setSelectedId(null)} />
      )}

      {manualOpen && (
        <ManualDispatchModal
          onClose={() => setManualOpen(false)}
          onCreated={() => queryClient.invalidateQueries({ queryKey: ['signal-dispatches'] })}
        />
      )}
    </div>
  )
}

export default SignalDispatchesTab
