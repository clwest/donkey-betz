// S2831 — RAG Intent-Gate Diagnostics tab
// Thin observability surface for the S2830 DORMANT pointer-intent registry.
// Registry canary: matched_patterns is computed via INTENT_MECHANISMS[*].detect()
// so a Step 2 refactor drift surfaces in the UI before it ships.
//
// Rigby SIGN cycle 1 verdicts baked in:
//   - Q3 DISAGREE: state is ephemeral (URL params + component state; no DB model)
//   - Q4 DISAGREE: drift-WARN not surfaced (scope creep)
//   - Q5 STRENGTHEN: filter_summary rendered under a "debug — not a stable contract" banner

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { Radar, Loader2, Search, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

interface RagDiagnosticResult {
  rank: number
  file_path: string | null
  intent_gate_name: string | null
  intent_gate_fired: boolean | null
  similarity_score: number | null
  chunk_id: number | null
  chunk_index: number | null
  category: string | null
  document_class: string | null
  title: string | null
}

interface RagDiagnosticResponse {
  success: boolean
  schema_version: string
  query: string
  limit: number
  threshold: number
  matched_patterns: string[]
  intent_gates: {
    count_active: boolean
    self_reference_active: boolean
    literal_filename_active: boolean
  }
  results: RagDiagnosticResult[]
  filter_summary: Record<string, unknown>
  notice: string
}

const GATE_LABELS: Record<string, { label: string; hint: string }> = {
  count: { label: 'COUNT', hint: 'Pattern B — "how many …" queries' },
  self_reference: { label: 'SELF_REFERENCE', hint: 'Pattern C — "where do I start" queries' },
  literal_filename: { label: 'LITERAL_FILENAME', hint: 'Pattern D — filename literal queries' },
}

export function RagDiagnosticsTab() {
  const [params, setParams] = useSearchParams()

  const [queryInput, setQueryInput] = useState(params.get('rq') ?? '')
  const [limitInput, setLimitInput] = useState(() => {
    const v = parseInt(params.get('rl') ?? '5', 10)
    return isNaN(v) ? 5 : Math.max(1, Math.min(v, 20))
  })
  const [thresholdInput, setThresholdInput] = useState(() => {
    const v = parseFloat(params.get('rt') ?? '0.4')
    return isNaN(v) ? 0.4 : Math.max(0.0, Math.min(v, 1.0))
  })

  const [activeQuery, setActiveQuery] = useState(params.get('rq') ?? '')
  const [activeLimit, setActiveLimit] = useState(limitInput)
  const [activeThreshold, setActiveThreshold] = useState(thresholdInput)

  const { data, isLoading, isFetching, error, refetch } = useQuery({
    queryKey: ['rag-intent-gate-diagnostics', activeQuery, activeLimit, activeThreshold],
    enabled: activeQuery.trim().length > 0,
    queryFn: async () => {
      const res = await api.get<RagDiagnosticResponse>('/rag/observability/intent-gate/', {
        params: { query: activeQuery, limit: activeLimit, threshold: activeThreshold },
      })
      return res.data
    },
  })

  const runQuery = (e?: React.FormEvent) => {
    e?.preventDefault()
    const q = queryInput.trim()
    if (!q) return
    setActiveQuery(q)
    setActiveLimit(limitInput)
    setActiveThreshold(thresholdInput)
    const next = new URLSearchParams(params)
    next.set('rq', q)
    next.set('rl', String(limitInput))
    next.set('rt', thresholdInput.toFixed(2))
    setParams(next, { replace: true })
  }

  const seedQueries = [
    { label: 'Pattern B (count)', q: 'How many spiders do we have' },
    { label: 'Pattern C (self-ref)', q: 'where do I start' },
    { label: 'Pattern D (filename)', q: 'PLATFORM_INVENTORY' },
    { label: 'No pattern', q: 'celery worker configuration' },
  ]

  const runSeed = (q: string) => {
    setQueryInput(q)
    setActiveQuery(q)
    setActiveLimit(limitInput)
    setActiveThreshold(thresholdInput)
    const next = new URLSearchParams(params)
    next.set('rq', q)
    next.set('rl', String(limitInput))
    next.set('rt', thresholdInput.toFixed(2))
    setParams(next, { replace: true })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-2">
        <Radar size={20} className="text-primary-400" />
        <h3 className="text-lg font-semibold text-white">RAG Intent-Gate Diagnostics</h3>
        <span className="ml-auto text-xs text-gray-500">S2831 · schema v1 · thin/best-effort</span>
      </div>

      <p className="text-xs text-gray-400 leading-relaxed">
        Canary surface for the S2830 pointer-intent registry.
        <code className="mx-1 px-1 py-0.5 rounded bg-gray-800/60 text-gray-300">matched_patterns</code>
        comes from <code className="mx-1 px-1 py-0.5 rounded bg-gray-800/60 text-gray-300">INTENT_MECHANISMS[*].detect()</code> —
        if a Step 2 refactor drifts intent-gate behavior, this tab is where it shows up first.
      </p>

      {/* Query form */}
      <form onSubmit={runQuery} className="space-y-3">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="query, e.g. 'How many spiders' or 'PLATFORM_INVENTORY'"
            className="w-full pl-9 pr-24 py-2 rounded-lg bg-gray-800/50 border border-dark-border text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary-500/50"
          />
          <button
            type="submit"
            disabled={!queryInput.trim() || isFetching}
            className="absolute right-1 top-1/2 -translate-y-1/2 px-3 py-1 rounded-md bg-primary-500/80 text-white text-xs font-medium hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isFetching ? <Loader2 size={12} className="animate-spin" /> : 'Run'}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <label className="flex items-center gap-3 text-xs text-gray-400">
            <span className="w-16">Limit</span>
            <input
              type="range"
              min={1}
              max={20}
              step={1}
              value={limitInput}
              onChange={(e) => setLimitInput(parseInt(e.target.value, 10))}
              className="flex-1"
            />
            <span className="w-6 text-right text-white tabular-nums">{limitInput}</span>
          </label>
          <label className="flex items-center gap-3 text-xs text-gray-400">
            <span className="w-16">Threshold</span>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={thresholdInput}
              onChange={(e) => setThresholdInput(parseFloat(e.target.value))}
              className="flex-1"
            />
            <span className="w-10 text-right text-white tabular-nums">{thresholdInput.toFixed(2)}</span>
          </label>
        </div>

        <div className="flex flex-wrap gap-2">
          {seedQueries.map((s) => (
            <button
              key={s.q}
              type="button"
              onClick={() => runSeed(s.q)}
              className="text-xs px-2 py-1 rounded border border-dark-border text-gray-400 hover:text-white hover:border-primary-500/50"
            >
              {s.label}
            </button>
          ))}
          <button
            type="button"
            onClick={() => refetch()}
            disabled={!activeQuery}
            className="text-xs px-2 py-1 rounded border border-dark-border text-gray-400 hover:text-white hover:border-primary-500/50 disabled:opacity-40 ml-auto"
          >
            Refresh
          </button>
        </div>
      </form>

      {/* Empty state */}
      {!activeQuery && (
        <div className="text-sm text-gray-500 italic border border-dashed border-dark-border rounded-lg p-6 text-center">
          Enter a query above or pick a seed pattern to see intent-gate behavior.
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
          <AlertCircle size={14} className="mt-0.5" />
          <div>
            <div className="font-medium">Diagnostics request failed</div>
            <div className="text-red-400/80 mt-1">{String((error as Error).message)}</div>
          </div>
        </div>
      )}

      {/* Loading */}
      {activeQuery && isLoading && (
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Loader2 size={14} className="animate-spin" />
          Running <code className="text-primary-400">search_embeddings</code>…
        </div>
      )}

      {/* Response */}
      {data && (
        <div className="space-y-5">
          {/* Intent-gate badges */}
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Intent gates</div>
            <div className="flex flex-wrap gap-2">
              {(['count', 'self_reference', 'literal_filename'] as const).map((k) => {
                const active = data.intent_gates[`${k}_active` as keyof typeof data.intent_gates]
                const meta = GATE_LABELS[k]
                return (
                  <div
                    key={k}
                    title={meta.hint}
                    className={cn(
                      'px-2.5 py-1 rounded border text-xs font-mono flex items-center gap-2',
                      active
                        ? 'bg-primary-500/15 border-primary-500/50 text-primary-300'
                        : 'bg-gray-800/30 border-dark-border text-gray-500'
                    )}
                  >
                    <span className={cn('w-1.5 h-1.5 rounded-full', active ? 'bg-primary-400' : 'bg-gray-600')} />
                    {meta.label}
                    <span className="opacity-60">{active ? 'ACTIVE' : 'idle'}</span>
                  </div>
                )
              })}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              matched_patterns:{' '}
              <code className="text-primary-300">
                {data.matched_patterns.length ? JSON.stringify(data.matched_patterns) : '[]'}
              </code>
            </div>
          </div>

          {/* Results table */}
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">
              Results ({data.results.length} · limit {data.limit} · threshold {data.threshold.toFixed(2)})
            </div>
            {data.results.length === 0 ? (
              <div className="text-xs text-gray-500 italic p-3 border border-dashed border-dark-border rounded">
                No results — try lowering the threshold, or the corpus doesn't cover this query.
              </div>
            ) : (
              <div className="border border-dark-border rounded-lg overflow-hidden">
                <table className="w-full text-xs">
                  <thead className="bg-gray-800/40 text-gray-400 uppercase tracking-wide">
                    <tr>
                      <th className="text-left px-2 py-1.5 w-8">#</th>
                      <th className="text-left px-2 py-1.5">file_path</th>
                      <th className="text-left px-2 py-1.5 w-32">intent_gate</th>
                      <th className="text-right px-2 py-1.5 w-20">similarity</th>
                      <th className="text-left px-2 py-1.5 w-24">category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.results.map((r) => (
                      <tr key={`${r.rank}-${r.chunk_id ?? r.chunk_index ?? r.rank}`} className="border-t border-dark-border">
                        <td className="px-2 py-1.5 text-gray-500 tabular-nums">{r.rank}</td>
                        <td className="px-2 py-1.5 text-white font-mono truncate max-w-md" title={r.file_path ?? ''}>
                          {r.file_path ?? <span className="text-gray-500 italic">(no path)</span>}
                        </td>
                        <td className="px-2 py-1.5">
                          {r.intent_gate_name ? (
                            <span className="px-1.5 py-0.5 rounded bg-primary-500/15 text-primary-300 font-mono">
                              {r.intent_gate_name}
                            </span>
                          ) : (
                            <span className="text-gray-600">—</span>
                          )}
                        </td>
                        <td className="px-2 py-1.5 text-right tabular-nums text-gray-300">
                          {r.similarity_score !== null ? r.similarity_score.toFixed(3) : '—'}
                        </td>
                        <td className="px-2 py-1.5 text-gray-500">{r.category ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Debug filter_summary — Rigby Q5 STRENGTHEN */}
          <details className="text-xs">
            <summary className="cursor-pointer text-gray-500 hover:text-gray-300">
              filter_summary (debug — not a stable contract)
            </summary>
            <pre className="mt-2 p-3 rounded bg-gray-900/60 border border-dark-border text-gray-400 overflow-x-auto">
              {JSON.stringify(data.filter_summary, null, 2)}
            </pre>
            <div className="mt-2 text-gray-600 italic">{data.notice}</div>
          </details>
        </div>
      )}
    </div>
  )
}
