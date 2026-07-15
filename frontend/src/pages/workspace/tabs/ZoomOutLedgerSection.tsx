/**
 * S2780 N22 v3: Zoom-Out Ledger section for GovernanceTab.
 *
 * Chris-facing read of logs/zoom_out_classifications.jsonl (the Rigby
 * SIGN zoom-out concern ledger, constitutional at Playbook v0.7.0 via
 * PLAYBOOK-6.10.8). Rigby's read path is `zoom_out_tool.list` (PA-tool
 * surface, S2780); this component consumes the parallel REST endpoint
 * `/api/governance/zoom-out-ledger/`.
 *
 * Design constraints from S2780 T1 SIGN V5 fold:
 * - Advisory posture rendered PROMINENTLY (banner) and REPEATED (badge
 *   next to counts). Advisory→gate drift is the primary risk.
 * - Inline "what is this?" tooltip on the section header for context-
 *   collapse mitigation (Chris may open the tab weeks apart).
 * - Classification badge color-coded per enum, but non-severity palette
 *   (no red/orange for "actionable" — those read as alerts).
 */
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Info, Filter, Loader2, ScrollText, X, Copy, Check } from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

interface ZoomOutRow {
  ts: string
  schema_version: number
  session: number
  arc: string
  classification: 'same_pr_actionable' | 'same_pr_mitigatable' | 'future_trigger'
  concern_text: string
  evidence_ref: string | null
  backfilled: boolean
  entered_by: string
}

interface ZoomOutAggregations {
  top_arcs_by_count: Array<{ arc: string; count: number }>
  future_trigger_rule_targets: Array<{ rule_id: string; count: number }>
  sessions_covered: number[]
  is_gate: boolean
  semantics: string
}

interface ZoomOutLedgerResponse {
  action: 'list'
  log_exists: boolean
  log_path: string
  advisory: string
  is_gate: boolean
  semantics: string
  total_rows: number
  counts_by_classification: Record<string, number>
  items: ZoomOutRow[]
  count: number
  limit: number
  malformed_lines_skipped: number
  session_filter?: number
  classification_filter?: string
  arc_filter?: string
  note?: string
  aggregations?: ZoomOutAggregations
}

type ClassificationFilter = '' | 'same_pr_actionable' | 'same_pr_mitigatable' | 'future_trigger'

// Non-severity palette per S2780 T1 SIGN V5 fold — advisory pattern
// evidence, not alerts. Amber = deferred; slate = mitigated; indigo =
// actionable. All muted; none red/orange.
const CLASSIFICATION_STYLES: Record<string, { label: string; badge: string }> = {
  same_pr_actionable: {
    label: 'Same PR — actionable',
    badge: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
  },
  same_pr_mitigatable: {
    label: 'Same PR — mitigatable',
    badge: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
  },
  future_trigger: {
    label: 'Future trigger',
    badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  },
}

function buildQueryString(filters: {
  session: string
  classification: ClassificationFilter
  arc: string
  limit: number
}): string {
  // S2791: always request aggregations so the chip strip stays populated
  // even when a filter is applied (aggregations are computed over ALL
  // rows server-side per test_zoom_out_aggregations_2791 contract 1).
  const parts: string[] = [`limit=${filters.limit}`, 'include=aggregations']
  if (filters.session) parts.push(`session=${encodeURIComponent(filters.session)}`)
  if (filters.classification) parts.push(`classification=${filters.classification}`)
  if (filters.arc) parts.push(`arc=${encodeURIComponent(filters.arc)}`)
  return parts.join('&')
}

export function ZoomOutLedgerSection() {
  const [session, setSession] = useState('')
  const [classification, setClassification] = useState<ClassificationFilter>('')
  const [arc, setArc] = useState('')
  const [limit, setLimit] = useState(20)
  const [helpOpen, setHelpOpen] = useState(false)
  const [detailRow, setDetailRow] = useState<ZoomOutRow | null>(null)

  const queryString = buildQueryString({ session, classification, arc, limit })

  const { data, isLoading, isError } = useQuery<ZoomOutLedgerResponse | null>({
    queryKey: ['governance-zoom-out-ledger', queryString],
    queryFn: async () => {
      try {
        const r = await api.get<ZoomOutLedgerResponse>(
          `/governance/zoom-out-ledger/?${queryString}`,
        )
        return r.data
      } catch {
        return null
      }
    },
    staleTime: 30_000,
  })

  const hasFilters = Boolean(session || classification || arc)
  const filteredCount = data?.count ?? 0
  const totalRows = data?.total_rows ?? 0

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <ScrollText className="text-primary-400" size={18} />
          <h3 className="text-md font-semibold uppercase">Zoom-Out Ledger</h3>
          <button
            type="button"
            onClick={() => setHelpOpen((v) => !v)}
            className="p-1 rounded text-gray-500 hover:text-gray-300 hover:bg-dark-bg transition-colors"
            aria-label={helpOpen ? 'Hide help' : 'Show help'}
          >
            <Info size={13} />
          </button>
        </div>
        <div className="text-xs text-gray-500">
          {totalRows} total {totalRows === 1 ? 'row' : 'rows'}
          {hasFilters && (
            <span className="ml-2">
              · {filteredCount} matching
            </span>
          )}
        </div>
      </div>

      {/* Advisory banner — PROMINENT + REPEATED per S2780 V5 fold. */}
      <div className="mb-3 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
        <div className="flex items-start gap-2">
          <Info size={14} className="text-amber-400 shrink-0 mt-0.5" aria-hidden />
          <div className="text-xs text-amber-200/90">
            <span className="font-semibold">Advisory pattern evidence — not gates.</span>{' '}
            Rows are longitudinal signal that inform SIGN loops. Any Playbook
            codification decision requires its own ratification.
          </div>
        </div>
      </div>

      {helpOpen && (
        <div className="mb-3 p-3 rounded-lg bg-dark-bg border border-dark-border text-xs text-gray-400 space-y-2">
          <p>
            The zoom-out ledger records the folds Rigby surfaces at the
            mandatory V-slot ("what would you push back on if I asked
            fresh?") during joint SIGN loops, per PLAYBOOK-6.10.7 +
            PLAYBOOK-6.10.8 (constitutional at Playbook v0.7.0).
          </p>
          <p>
            Each row carries a classification:
          </p>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              <span className="text-indigo-300">Same PR — actionable</span>:
              must be incorporated in the same PR before ship.
            </li>
            <li>
              <span className="text-slate-300">Same PR — mitigatable</span>:
              risk can be reduced same-PR without expanding scope.
            </li>
            <li>
              <span className="text-amber-300">Future trigger</span>:
              deferred to a named trigger condition.
            </li>
          </ul>
        </div>
      )}

      {/* Filters */}
      <div className="mb-3 flex flex-wrap items-center gap-2 text-xs">
        <Filter size={12} className="text-gray-500" aria-hidden />
        <input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          placeholder="session #"
          value={session}
          onChange={(e) => setSession(e.target.value.replace(/\D/g, ''))}
          className="w-24 px-2 py-1 rounded bg-dark-bg border border-dark-border text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-primary-500/40"
          aria-label="Filter by session number"
        />
        <select
          value={classification}
          onChange={(e) => setClassification(e.target.value as ClassificationFilter)}
          className="px-2 py-1 rounded bg-dark-bg border border-dark-border text-gray-200 focus:outline-none focus:border-primary-500/40"
          aria-label="Filter by classification"
        >
          <option value="">any classification</option>
          <option value="same_pr_actionable">same_pr_actionable</option>
          <option value="same_pr_mitigatable">same_pr_mitigatable</option>
          <option value="future_trigger">future_trigger</option>
        </select>
        <input
          type="text"
          placeholder="arc substring"
          value={arc}
          onChange={(e) => setArc(e.target.value)}
          className="w-40 px-2 py-1 rounded bg-dark-bg border border-dark-border text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-primary-500/40"
          aria-label="Filter by arc slug substring"
        />
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="px-2 py-1 rounded bg-dark-bg border border-dark-border text-gray-200 focus:outline-none focus:border-primary-500/40"
          aria-label="Limit"
        >
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
        {hasFilters && (
          <button
            type="button"
            onClick={() => {
              setSession('')
              setClassification('')
              setArc('')
            }}
            className="px-2 py-1 rounded bg-dark-bg border border-dark-border text-gray-400 hover:text-gray-200 transition-colors"
          >
            clear
          </button>
        )}
      </div>

      {/* Aggregate counts — advisory framing repeated in "not gates" copy */}
      {data && data.log_exists && (
        <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-gray-500">
          <span>Counts (pattern evidence, not gates):</span>
          {Object.entries(data.counts_by_classification).map(([k, v]) => {
            const style = CLASSIFICATION_STYLES[k]?.badge ??
              'bg-dark-bg text-gray-400 border-dark-border'
            return (
              <span
                key={k}
                className={cn('px-1.5 py-0.5 rounded border font-mono', style)}
              >
                {k}: {v}
              </span>
            )
          })}
        </div>
      )}

      {/* S2791: Aggregation chips strip. Two rows — top arcs (click to
          filter) + future_trigger rule targets (informational, showing
          which PLAYBOOK amendments have accumulated future_trigger
          evidence). Advisory posture stays intact — chips only set the
          existing arc filter, no gating side-effect. */}
      {data && data.log_exists && data.aggregations && (
        <div className="mb-3 space-y-2">
          {data.aggregations.top_arcs_by_count.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 text-xs">
              <span className="text-gray-500">Top arcs:</span>
              {data.aggregations.top_arcs_by_count.slice(0, 8).map((entry) => {
                const isActive = arc === entry.arc
                return (
                  <button
                    key={entry.arc}
                    type="button"
                    onClick={() => setArc(isActive ? '' : entry.arc)}
                    className={cn(
                      'px-1.5 py-0.5 rounded border font-mono transition-colors',
                      isActive
                        ? 'bg-primary-500/20 text-primary-300 border-primary-500/40'
                        : 'bg-dark-bg text-gray-400 border-dark-border hover:text-gray-200 hover:border-gray-600',
                    )}
                    title={`Filter to arc=${entry.arc}`}
                  >
                    {entry.arc}
                    <span className="ml-1 text-gray-500">{entry.count}</span>
                  </button>
                )
              })}
            </div>
          )}
          {data.aggregations.future_trigger_rule_targets.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 text-xs">
              <span className="text-gray-500">Future-trigger rule targets:</span>
              {data.aggregations.future_trigger_rule_targets.map((entry) => (
                <span
                  key={entry.rule_id}
                  className="px-1.5 py-0.5 rounded border font-mono bg-amber-500/10 text-amber-300 border-amber-500/30"
                  title="Advisory evidence — codification requires ratification."
                >
                  {entry.rule_id}
                  <span className="ml-1 text-amber-200/70">{entry.count}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Items list */}
      {isLoading && (
        <div className="py-8 flex items-center justify-center text-gray-500">
          <Loader2 className="animate-spin" size={16} />
        </div>
      )}
      {isError && (
        <div className="py-4 text-sm text-red-400/80">
          Failed to load zoom-out ledger. Retry on next refresh.
        </div>
      )}
      {data && !data.log_exists && (
        <div className="py-4 text-sm text-gray-500">
          {data.note ?? 'Ledger empty — no zoom-out folds recorded yet.'}
        </div>
      )}
      {data && data.log_exists && data.items.length === 0 && (
        <div className="py-4 text-sm text-gray-500">
          No rows match the current filters.
        </div>
      )}
      {data && data.log_exists && data.items.length > 0 && (
        <div className="space-y-2">
          {data.items.slice().reverse().map((row, i) => {
            const style = CLASSIFICATION_STYLES[row.classification]
            const label = style?.label ?? row.classification
            const badge = style?.badge ?? 'bg-dark-bg text-gray-400 border-dark-border'
            const ts = row.ts.replace('T', ' ').split('.')[0].replace('+00:00', 'Z')
            return (
              <button
                key={`${row.session}-${row.ts}-${i}`}
                type="button"
                onClick={() => setDetailRow(row)}
                className="w-full text-left p-3 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/40 hover:bg-dark-card/80 transition-colors"
                aria-label={`Open detail for S${row.session} ${row.arc}`}
              >
                <div className="flex items-center gap-3 mb-2 text-xs">
                  <span className="font-mono font-medium text-primary-400">
                    S{row.session}
                  </span>
                  <span className="text-gray-400 truncate">{row.arc}</span>
                  <span className={cn('px-1.5 py-0.5 rounded border font-medium', badge)}>
                    {label}
                  </span>
                  {row.backfilled && (
                    <span className="px-1.5 py-0.5 rounded bg-dark-bg border border-dark-border text-gray-500">
                      backfilled
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-200 mb-2 line-clamp-2">{row.concern_text}</p>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{ts}</span>
                  {row.evidence_ref && (
                    <>
                      <span className="text-gray-600">·</span>
                      <span className="font-mono">{row.evidence_ref}</span>
                    </>
                  )}
                  <span className="text-gray-600">·</span>
                  <span>by {row.entered_by}</span>
                </div>
              </button>
            )
          })}
        </div>
      )}

      {detailRow && (
        <ZoomOutRowDetailModal
          row={detailRow}
          allRows={data?.items ?? []}
          onClose={() => setDetailRow(null)}
          onOpenSister={(next) => setDetailRow(next)}
        />
      )}
    </div>
  )
}

interface ZoomOutRowDetailModalProps {
  row: ZoomOutRow
  allRows: ZoomOutRow[]
  onClose: () => void
  onOpenSister: (row: ZoomOutRow) => void
}

function ZoomOutRowDetailModal({
  row,
  allRows,
  onClose,
  onOpenSister,
}: ZoomOutRowDetailModalProps) {
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const style = CLASSIFICATION_STYLES[row.classification]
  const label = style?.label ?? row.classification
  const badge = style?.badge ?? 'bg-dark-bg text-gray-400 border-dark-border'
  const ts = row.ts.replace('T', ' ').split('.')[0].replace('+00:00', 'Z')

  // Sister rows share arc, exclude self by (session, ts) identity —
  // helpful when reviewing the shape of a specific arc's fold history.
  const sisters = allRows.filter(
    (r) => r.arc === row.arc && !(r.session === row.session && r.ts === row.ts),
  )

  const copyEvidence = async () => {
    if (!row.evidence_ref) return
    try {
      await navigator.clipboard.writeText(row.evidence_ref)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1200)
    } catch {
      // Clipboard rejected (permissions, insecure context). Non-fatal.
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={`Zoom-out fold detail — S${row.session} ${row.arc}`}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header — advisory posture REPEATED here per S2780 V5 fold. */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border bg-gradient-to-r from-amber-500/5 to-transparent">
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2 rounded-lg bg-amber-500/10 shrink-0">
              <ScrollText size={18} className="text-amber-400" />
            </div>
            <div className="min-w-0">
              <h2 className="text-base font-semibold">Zoom-Out Fold Detail</h2>
              <p className="text-xs text-amber-200/80 truncate">
                Advisory pattern evidence — not a gate.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-dark-border transition-colors shrink-0"
            aria-label="Close detail"
          >
            <X size={18} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Meta strip */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="font-mono font-medium text-primary-400">
              S{row.session}
            </span>
            <span className={cn('px-1.5 py-0.5 rounded border font-medium', badge)}>
              {label}
            </span>
            <span className="text-gray-500">{ts}</span>
            {row.backfilled && (
              <span className="px-1.5 py-0.5 rounded bg-dark-bg border border-dark-border text-gray-500">
                backfilled
              </span>
            )}
            <span className="text-gray-500">by {row.entered_by}</span>
          </div>

          {/* Arc */}
          <div>
            <div className="text-xs text-gray-500 mb-1">Arc</div>
            <div className="font-mono text-sm text-gray-200 break-all">
              {row.arc}
            </div>
          </div>

          {/* Full concern_text — this is the primary content the modal
              exists to expose (list view truncates via line-clamp-2). */}
          <div>
            <div className="text-xs text-gray-500 mb-1">Concern</div>
            <p className="text-sm text-gray-200 whitespace-pre-wrap">
              {row.concern_text}
            </p>
          </div>

          {/* Evidence ref with click-to-copy */}
          {row.evidence_ref && (
            <div>
              <div className="text-xs text-gray-500 mb-1">Evidence</div>
              <div className="flex items-center gap-2">
                <code className="flex-1 font-mono text-xs text-gray-300 bg-dark-bg border border-dark-border rounded px-2 py-1.5 break-all">
                  {row.evidence_ref}
                </code>
                <button
                  type="button"
                  onClick={copyEvidence}
                  className="p-1.5 rounded bg-dark-bg border border-dark-border text-gray-400 hover:text-gray-200 hover:border-gray-600 transition-colors"
                  aria-label="Copy evidence reference"
                  title="Copy evidence reference"
                >
                  {copied ? (
                    <Check size={14} className="text-green-400" />
                  ) : (
                    <Copy size={14} />
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Sister rows — rows in the same arc, click to pivot */}
          {sisters.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-2">
                Sister rows in this arc ({sisters.length})
              </div>
              <div className="space-y-2">
                {sisters.map((s, i) => {
                  const sStyle = CLASSIFICATION_STYLES[s.classification]
                  const sBadge =
                    sStyle?.badge ??
                    'bg-dark-bg text-gray-400 border-dark-border'
                  const sTs = s.ts.replace('T', ' ').split('.')[0].replace(
                    '+00:00',
                    'Z',
                  )
                  return (
                    <button
                      key={`${s.session}-${s.ts}-${i}`}
                      type="button"
                      onClick={() => onOpenSister(s)}
                      className="w-full text-left p-2 rounded bg-dark-bg border border-dark-border hover:border-primary-500/40 transition-colors"
                    >
                      <div className="flex items-center gap-2 text-xs mb-1">
                        <span className="font-mono font-medium text-primary-400">
                          S{s.session}
                        </span>
                        <span
                          className={cn(
                            'px-1.5 py-0.5 rounded border font-medium',
                            sBadge,
                          )}
                        >
                          {sStyle?.label ?? s.classification}
                        </span>
                        <span className="text-gray-500">{sTs}</span>
                      </div>
                      <p className="text-xs text-gray-300 line-clamp-2">
                        {s.concern_text}
                      </p>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer — third repetition of advisory posture. */}
        <div className="px-4 py-2 border-t border-dark-border bg-dark-bg/50 text-xs text-gray-500">
          Rows are longitudinal signal. Any Playbook codification requires
          its own ratification.
        </div>
      </div>
    </div>
  )
}
