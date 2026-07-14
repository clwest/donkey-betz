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
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Info, Filter, Loader2, ScrollText } from 'lucide-react'
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
  const parts: string[] = [`limit=${filters.limit}`]
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
              <div
                key={`${row.session}-${row.ts}-${i}`}
                className="p-3 rounded-lg bg-dark-card border border-dark-border"
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
                <p className="text-sm text-gray-200 mb-2">{row.concern_text}</p>
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
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
