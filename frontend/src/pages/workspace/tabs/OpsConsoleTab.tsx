/**
 * Session 1077: Ops Console Tab (#7)
 * Surfaces SLO breaches, failure signatures, blocked agents, queue depth.
 * Replaces the generic System tab with actionable ops data.
 */

import { useEffect, useRef, useState, Suspense, lazy } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle, CheckCircle, XCircle, Loader2, Shield,
  Clock, Zap, Activity, Ban, TrendingDown, Layers, Copy, Check, RotateCw,
  FileText, ScrollText, ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

// S2767 N4: DocumentViewer lazy-loaded so the drawer chunk is only paid when
// the operator actually opens a ledger doc — keeps OpsConsole route bundle lean.
const LazyDocumentViewer = lazy(() =>
  import('@/components/platform/DocumentViewer').then((m) => ({ default: m.DocumentViewer })),
)

// S2767 N4: doc-content response shape from /api/platform/doc-content/ (public
// read-only, guarded to docs/** with traversal check — see auth_middleware.py:436).
interface DocContentResponse {
  content: string
  metadata: {
    path: string
    name: string
    title: string
    lines: number
    size_bytes: number
    modified_at: string
  }
}

const PREVIEW_LINE_LIMIT = 10
const HOVER_DEBOUNCE_MS = 150
const PREVIEW_STALE_TIME_MS = 5 * 60 * 1000

interface OpsHealthSummary {
  window: string
  // S2770 N11: new PARTIAL_RECYCLE verdict fires when base is STALE_* AND
  // the newest recycle event has partial_recycle=true (N7 evidence). Amber
  // in the UI — between green FRESH and red STALE.
  verdict: 'FRESH' | 'STALE_DAPHNE' | 'STALE_CELERY' | 'STALE_BOTH' | 'PARTIAL_RECYCLE' | 'UNKNOWN'
  head_commit_sha_short: string
  tenant_boundary_violations: {
    total: number
    by_task_name: Record<string, number>
    by_failure_kind: Record<string, number>
  }
  staleness_warnings: {
    total: number
    by_verdict: Record<string, number>
  }
  slo_status: {
    total: number
    breach_count: number
    healthy_count: number
    worst_breach: {
      key: string | null
      name: string | null
      current: number
      target: number
    } | null
  }
  // S2770 N11: populated only when verdict === 'PARTIAL_RECYCLE'.
  partial_recycle_details?: {
    surviving_processes: string[]
    recycle_sha_short: string
  }
}

interface CloseCeremonyItem {
  session_number: number
  title: string
  date: string | null
  handoff_path: string
  envelope_path: string | null
  envelope_exists: boolean
  // S2771 N14: present only when the ledger query included a text search;
  // number of times the term appears in the handoff body.
  text_match_count?: number
}

interface CloseCeremonyLedger {
  items: CloseCeremonyItem[]
  count: number
  limit: number
  // S2769 N8: pre-limit filter-matching count. Optional for backward-compat
  // if the client hits an older backend, but the S2769 view always returns it.
  total_available?: number
}

// S2769 N8: ledger filter state — all fields optional; empty string means
// "no filter for this dimension." Session inputs are string-typed so an empty
// input is representable; parsed to int server-side.
// S2771 N14: `text` full-body substring search added to same interface.
interface LedgerFilters {
  sessionMin: string
  sessionMax: string
  envelopeOnly: boolean
  dateFrom: string
  dateTo: string
  text: string
}

const LEDGER_LIMIT_DEFAULT = 10
const LEDGER_LIMIT_EXPANDED = 50
// S2771 N14: keystroke storm shield — text state updates every keypress
// but the query fires only after this quiet period. 200ms is Rigby-signed
// (Q3 discussion) — long enough to skip typos, short enough to feel live.
const TEXT_SEARCH_DEBOUNCE_MS = 200

function hasActiveFilters(f: LedgerFilters): boolean {
  return (
    f.sessionMin !== '' ||
    f.sessionMax !== '' ||
    f.envelopeOnly ||
    f.dateFrom !== '' ||
    f.dateTo !== '' ||
    f.text !== ''
  )
}

function buildLedgerQueryString(f: LedgerFilters, limit: number): string {
  const parts: string[] = [`limit=${limit}`]
  if (f.sessionMin) parts.push(`session_min=${encodeURIComponent(f.sessionMin)}`)
  if (f.sessionMax) parts.push(`session_max=${encodeURIComponent(f.sessionMax)}`)
  if (f.envelopeOnly) parts.push('envelope_only=true')
  if (f.dateFrom) parts.push(`date_from=${encodeURIComponent(f.dateFrom)}`)
  if (f.dateTo) parts.push(`date_to=${encodeURIComponent(f.dateTo)}`)
  if (f.text) parts.push(`text=${encodeURIComponent(f.text)}`)
  return parts.join('&')
}

interface RecycleEvent {
  timestamp: string | null
  sha: string
  sha_short: string
  label: string
  seconds_ago: number | null
}

interface RecentRecyclesResponse {
  items: RecycleEvent[]
  count: number
  limit: number
  log_exists: boolean
  note?: string
}

function formatAgo(seconds: number): string {
  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}

// S2767 N4: single close-ceremony row with hover-preview + click-to-open.
// Hover a stable 150ms → fetch first PREVIEW_LINE_LIMIT lines and render as
// plain text in a tooltip. Click the row header → parent opens DocumentViewer.
// Focus/blur mirror hover for keyboard users; react-query caches per-path 5min.
interface LedgerRowProps {
  item: CloseCeremonyItem
  onOpen: (path: string, title: string) => void
  onCopy: (path: string) => void
  copiedPath: string | null
}

function LedgerRow({ item, onOpen, onCopy, copiedPath }: LedgerRowProps) {
  const [previewOpen, setPreviewOpen] = useState(false)
  const hoverTimer = useRef<number | null>(null)

  const previewQuery = useQuery<DocContentResponse | null>({
    queryKey: ['doc-preview', item.handoff_path],
    queryFn: async () => {
      try {
        const r = await api.get<DocContentResponse>('/platform/doc-content/', {
          params: { path: item.handoff_path },
        })
        return r.data
      } catch { return null }
    },
    enabled: previewOpen,
    staleTime: PREVIEW_STALE_TIME_MS,
  })

  const startHover = () => {
    if (hoverTimer.current) window.clearTimeout(hoverTimer.current)
    hoverTimer.current = window.setTimeout(() => setPreviewOpen(true), HOVER_DEBOUNCE_MS)
  }

  const stopHover = () => {
    if (hoverTimer.current) {
      window.clearTimeout(hoverTimer.current)
      hoverTimer.current = null
    }
    setPreviewOpen(false)
  }

  const previewLines = previewQuery.data?.content?.split('\n').slice(0, PREVIEW_LINE_LIMIT) ?? []
  const totalLines = previewQuery.data?.metadata.lines ?? 0
  const remainingLines = Math.max(0, totalLines - previewLines.length)

  return (
    <div
      className="relative p-3 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/40 transition-colors"
      onMouseEnter={startHover}
      onMouseLeave={stopHover}
    >
      <button
        type="button"
        className="w-full text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/40 rounded"
        onClick={() => onOpen(item.handoff_path, item.title)}
        onFocus={startHover}
        onBlur={stopHover}
        aria-label={`Open handoff ${item.handoff_path}`}
      >
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-medium text-primary-400 shrink-0">
            S{item.session_number}
          </span>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-white truncate">{item.title}</p>
            <div className="flex items-center gap-2 mt-0.5 text-xs">
              {item.date && <span className="text-gray-500">{item.date}</span>}
              <span
                className={cn(
                  'px-1.5 py-0.5 rounded font-medium',
                  item.envelope_exists
                    ? 'bg-green-500/10 text-green-400'
                    : 'bg-gray-500/10 text-gray-400',
                )}
              >
                {item.envelope_exists ? 'envelope' : 'handoff-only'}
              </span>
              {/* S2771 N14: match-count badge — only present when text search is active. */}
              {typeof item.text_match_count === 'number' && (
                <span className="px-1.5 py-0.5 rounded font-medium bg-primary-500/10 text-primary-300">
                  {item.text_match_count} {item.text_match_count === 1 ? 'match' : 'matches'}
                </span>
              )}
            </div>
          </div>
          <FileText size={13} className="text-gray-500 shrink-0" aria-hidden />
        </div>
      </button>

      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <button
          type="button"
          onClick={() => onCopy(item.handoff_path)}
          className="flex items-center gap-1 px-2 py-1 rounded bg-dark-bg hover:bg-dark-border text-gray-500 hover:text-gray-300 transition-colors"
          title="Copy handoff path"
        >
          {copiedPath === item.handoff_path ? (
            <Check size={11} className="text-green-400" />
          ) : (
            <Copy size={11} />
          )}
          <span>handoff path</span>
        </button>
        {item.envelope_path && (
          <>
            <button
              type="button"
              onClick={() => onOpen(item.envelope_path!, `${item.title} (envelope)`)}
              className="flex items-center gap-1 px-2 py-1 rounded bg-dark-bg hover:bg-dark-border text-gray-500 hover:text-gray-300 transition-colors"
              title="Open envelope in viewer"
            >
              <FileText size={11} />
              <span>envelope</span>
            </button>
            <button
              type="button"
              onClick={() => onCopy(item.envelope_path!)}
              className="flex items-center gap-1 px-2 py-1 rounded bg-dark-bg hover:bg-dark-border text-gray-500 hover:text-gray-300 transition-colors"
              title="Copy envelope path"
            >
              {copiedPath === item.envelope_path ? (
                <Check size={11} className="text-green-400" />
              ) : (
                <Copy size={11} />
              )}
              <span>copy envelope</span>
            </button>
          </>
        )}
      </div>

      {previewOpen && (
        <div
          role="tooltip"
          className="absolute left-0 right-0 top-full mt-1 z-20 p-3 rounded-lg bg-dark-bg border border-primary-500/30 shadow-lg pointer-events-none"
        >
          {previewQuery.isLoading && (
            <div className="text-xs text-gray-500 flex items-center gap-2">
              <Loader2 size={11} className="animate-spin" />
              Loading preview…
            </div>
          )}
          {previewQuery.data && (
            <>
              <div className="text-xs text-gray-500 mb-1">
                First {previewLines.length} lines · {item.handoff_path.split('/').pop()}
              </div>
              <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono max-h-40 overflow-hidden">
                {previewLines.join('\n')}
              </pre>
              {remainingLines > 0 && (
                <div className="text-xs text-gray-500 mt-1">
                  … {remainingLines} more lines — click to open
                </div>
              )}
            </>
          )}
          {previewQuery.isError && (
            <div className="text-xs text-red-400">Preview unavailable</div>
          )}
        </div>
      )}
    </div>
  )
}

export function OpsConsoleTab() {
  // S2761: unified health summary — freshness verdict + I-0303 tenant
  // boundary violation counts + S2759 staleness warning counts. Wraps the
  // three S2755→S2760 diagnostic surfaces into one always-visible tile.
  // S2762: sibling SLO/failure/blocked queries below now share this
  // `api.get` pattern (raw fetch omitted the Authorization token → 401).
  const healthQuery = useQuery<OpsHealthSummary | null>({
    queryKey: ['ops-health-summary'],
    queryFn: async () => {
      try {
        const r = await api.get<OpsHealthSummary>('/ops/health-summary/')
        return r.data
      } catch { return null }
    },
    refetchInterval: 30000,
  })

  const sloQuery = useQuery({
    queryKey: ['ops-slo'],
    queryFn: async () => {
      try {
        const r = await api.get('/ops/slo-status/')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })

  const sigQuery = useQuery({
    queryKey: ['ops-signatures'],
    queryFn: async () => {
      try {
        const r = await api.get('/ops/failure-signatures/?window=24h&limit=10')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })

  const blockedQuery = useQuery({
    queryKey: ['ops-blocked'],
    queryFn: async () => {
      try {
        const r = await api.get('/ops/blocked-agents/')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })

  // S2763: close-ceremony ledger — last 10 handoffs paired with envelopes.
  // Filesystem-backed (docs/handoffs/ + docs/research/implementation/), no
  // data model. Read-only operator surface for fast context re-load.
  // S2769 N8: filters (session range / envelope-only / date range) applied
  // server-side; total_available surfaces the pre-limit matching count so
  // the operator can expand to the S2769 hard cap of 50.
  const [ledgerFilters, setLedgerFilters] = useState<LedgerFilters>({
    sessionMin: '',
    sessionMax: '',
    envelopeOnly: false,
    dateFrom: '',
    dateTo: '',
    text: '',
  })
  // S2771 N14: text is debounced separately from the other filters so
  // rapid typing doesn't spam the backend text-scan (~30ms per char is
  // fine; ~5ms full-scan per keystroke on the 961-handoff corpus is not).
  // The text input updates ledgerFilters.text every keypress for UX
  // responsiveness; debouncedText syncs 200ms later and feeds the query.
  const [debouncedText, setDebouncedText] = useState<string>('')
  useEffect(() => {
    const t = window.setTimeout(() => setDebouncedText(ledgerFilters.text), TEXT_SEARCH_DEBOUNCE_MS)
    return () => window.clearTimeout(t)
  }, [ledgerFilters.text])
  const debouncedFilters = { ...ledgerFilters, text: debouncedText }
  const [ledgerLimit, setLedgerLimit] = useState<number>(LEDGER_LIMIT_DEFAULT)
  const ledgerQueryString = buildLedgerQueryString(debouncedFilters, ledgerLimit)
  const ledgerFiltersActive = hasActiveFilters(debouncedFilters)
  const ledgerQuery = useQuery<CloseCeremonyLedger | null>({
    queryKey: ['ops-close-ceremony-ledger', ledgerQueryString],
    queryFn: async () => {
      try {
        const r = await api.get<CloseCeremonyLedger>(`/ops/close-ceremony-ledger/?${ledgerQueryString}`)
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })
  const resetLedgerFilters = () => {
    setLedgerFilters({ sessionMin: '', sessionMax: '', envelopeOnly: false, dateFrom: '', dateTo: '', text: '' })
    setLedgerLimit(LEDGER_LIMIT_DEFAULT)
  }

  // S2765: recent recycle events — JSONL-backed (logs/recycle_events.jsonl,
  // emitted by `make recycle-all` post-restart). Answers "when did we last
  // recycle?" without a Rigby round-trip.
  const recyclesQuery = useQuery<RecentRecyclesResponse | null>({
    queryKey: ['ops-recent-recycles'],
    queryFn: async () => {
      try {
        const r = await api.get<RecentRecyclesResponse>('/ops/recent-recycles/?limit=10')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })

  // S2780 N22 v3: lightweight preview of the zoom-out ledger for
  // discoverability. Canonical home is system.sign-ledger (dedicated
  // sub-tab per Rigby S2780 V3 fold — semantic boundary preserved).
  // Fetches limit=1 to keep the payload small; we only need the counts.
  const zoomOutPreviewQuery = useQuery<{
    total_rows: number
    counts_by_classification: Record<string, number>
    log_exists: boolean
  } | null>({
    queryKey: ['governance-zoom-out-preview'],
    queryFn: async () => {
      try {
        const r = await api.get<{
          total_rows: number
          counts_by_classification: Record<string, number>
          log_exists: boolean
        }>('/governance/zoom-out-ledger/?limit=1')
        return r.data
      } catch { return null }
    },
    staleTime: 120_000,
  })
  const [, setSearchParams] = useSearchParams()
  const goToSignLedger = () => {
    setSearchParams({ tab: 'system', sub: 'sign-ledger' }, { replace: false })
  }
  const [copiedPath, setCopiedPath] = useState<string | null>(null)
  const copyPath = async (path: string) => {
    try {
      await navigator.clipboard.writeText(path)
      setCopiedPath(path)
      setTimeout(() => setCopiedPath(null), 1500)
    } catch { /* clipboard unavailable — no-op */ }
  }

  // S2767 N4: docs viewer drawer state — populated when the operator clicks
  // a ledger row (handoff or envelope). Cleared on close.
  const [viewerDoc, setViewerDoc] = useState<{ path: string; title: string } | null>(null)
  const openViewer = (path: string, title: string) => setViewerDoc({ path, title })
  const closeViewer = () => setViewerDoc(null)

  const slos = sloQuery.data?.slos || []
  const breaches = slos.filter((s: Record<string, boolean>) => s.breach)
  const signatures = sigQuery.data?.signatures || []
  const blocked = blockedQuery.data?.blocked || []
  const isLoading = sloQuery.isLoading

  const opsHealth = healthQuery.data

  return (
    <div className="space-y-6">
      {/* S2761: Ops Health tile — verdict + I-0303 + S2759 counts */}
      {opsHealth && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Activity size={14} />
            Ops Health (24h)
            <span
              className={cn(
                'ml-2 h-1.5 w-1.5 rounded-full',
                opsHealth.verdict === 'FRESH' && 'bg-green-400',
                opsHealth.verdict === 'UNKNOWN' && 'bg-gray-500',
                // S2770 N11: PARTIAL_RECYCLE lands amber — distinct from FRESH green and STALE red.
                opsHealth.verdict === 'PARTIAL_RECYCLE' && 'bg-amber-400',
                opsHealth.verdict !== 'FRESH' &&
                  opsHealth.verdict !== 'UNKNOWN' &&
                  opsHealth.verdict !== 'PARTIAL_RECYCLE' &&
                  'bg-red-400',
              )}
            />
            <span className={cn(
              'text-xs font-medium',
              opsHealth.verdict === 'FRESH' ? 'text-green-400' :
              opsHealth.verdict === 'UNKNOWN' ? 'text-gray-400' :
              opsHealth.verdict === 'PARTIAL_RECYCLE' ? 'text-amber-400' :
              'text-red-400'
            )}>{opsHealth.verdict}</span>
            {opsHealth.head_commit_sha_short && (
              <code className="text-xs text-gray-500 ml-1">{opsHealth.head_commit_sha_short.slice(0, 7)}</code>
            )}
          </h3>
          {/* S2770 N11: surviving-processes row appears only on PARTIAL_RECYCLE verdict.
              Names come from the newest recycle event's surviving_processes list. */}
          {opsHealth.verdict === 'PARTIAL_RECYCLE' && opsHealth.partial_recycle_details && (
            <div className="mb-3 -mt-1 p-2 rounded-lg border border-amber-500/30 bg-amber-500/5 text-xs">
              <span className="text-amber-400 font-medium">Partial recycle detected</span>
              <span className="text-gray-400"> · surviving:</span>{' '}
              {opsHealth.partial_recycle_details.surviving_processes.length > 0 ? (
                <span className="text-amber-300 font-mono">
                  {opsHealth.partial_recycle_details.surviving_processes.join(', ')}
                </span>
              ) : (
                <span className="text-gray-500 italic">none listed</span>
              )}
              {opsHealth.partial_recycle_details.recycle_sha_short && (
                <>
                  <span className="text-gray-500"> · recycle sha </span>
                  <code className="text-gray-400">{opsHealth.partial_recycle_details.recycle_sha_short.slice(0, 7)}</code>
                </>
              )}
              <span className="text-gray-500"> · run </span>
              <code className="text-gray-400">make recycle-all</code>
              <span className="text-gray-500"> to fix.</span>
            </div>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className={cn(
              'p-3 rounded-lg border',
              opsHealth.tenant_boundary_violations.total > 0
                ? 'border-amber-500/30 bg-amber-500/5'
                : 'border-dark-border bg-dark-card'
            )}>
              <div className="flex items-center gap-2 mb-1">
                <Shield size={14} className={opsHealth.tenant_boundary_violations.total > 0 ? 'text-amber-400' : 'text-green-400'} />
                <span className="text-xs text-gray-400">Tenant Boundary Violations</span>
              </div>
              <p className={cn(
                'text-lg font-bold',
                opsHealth.tenant_boundary_violations.total > 0 ? 'text-amber-400' : 'text-green-400'
              )}>
                {opsHealth.tenant_boundary_violations.total}
              </p>
              {opsHealth.tenant_boundary_violations.total > 0 && (
                <div className="mt-2 space-y-0.5">
                  {Object.entries(opsHealth.tenant_boundary_violations.by_failure_kind).slice(0, 4).map(([kind, count]) => (
                    <div key={kind} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500 truncate">{kind}</span>
                      <span className="text-gray-400 ml-2">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className={cn(
              'p-3 rounded-lg border',
              opsHealth.staleness_warnings.total > 0
                ? 'border-red-500/30 bg-red-500/5'
                : 'border-dark-border bg-dark-card'
            )}>
              <div className="flex items-center gap-2 mb-1">
                <Clock size={14} className={opsHealth.staleness_warnings.total > 0 ? 'text-red-400' : 'text-green-400'} />
                <span className="text-xs text-gray-400">Staleness Warnings</span>
              </div>
              <p className={cn(
                'text-lg font-bold',
                opsHealth.staleness_warnings.total > 0 ? 'text-red-400' : 'text-green-400'
              )}>
                {opsHealth.staleness_warnings.total}
              </p>
              {opsHealth.staleness_warnings.total > 0 && (
                <div className="mt-2 space-y-0.5">
                  {Object.entries(opsHealth.staleness_warnings.by_verdict).slice(0, 4).map(([v, count]) => (
                    <div key={v} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500 truncate">{v}</span>
                      <span className="text-gray-400 ml-2">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* S2764: SLO Status tile card — 3rd tile per N1 */}
            <div className={cn(
              'p-3 rounded-lg border',
              opsHealth.slo_status.breach_count > 0
                ? 'border-red-500/30 bg-red-500/5'
                : 'border-dark-border bg-dark-card'
            )}>
              <div className="flex items-center gap-2 mb-1">
                <Zap size={14} className={opsHealth.slo_status.breach_count > 0 ? 'text-red-400' : 'text-green-400'} />
                <span className="text-xs text-gray-400">SLO Breaches</span>
              </div>
              <p className={cn(
                'text-lg font-bold',
                opsHealth.slo_status.breach_count > 0 ? 'text-red-400' : 'text-green-400'
              )}>
                {opsHealth.slo_status.breach_count}
                <span className="text-sm font-normal text-gray-500 ml-1">/ {opsHealth.slo_status.total}</span>
              </p>
              {opsHealth.slo_status.worst_breach && (
                <div className="mt-2 space-y-0.5">
                  <div className="text-xs text-gray-400 truncate" title={opsHealth.slo_status.worst_breach.name ?? ''}>
                    {opsHealth.slo_status.worst_breach.name}
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">current</span>
                    <span className="text-red-400 font-mono">
                      {opsHealth.slo_status.worst_breach.current < 1
                        ? `${(opsHealth.slo_status.worst_breach.current * 100).toFixed(2)}%`
                        : opsHealth.slo_status.worst_breach.current.toFixed(0)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">target</span>
                    <span className="text-gray-400 font-mono">
                      {opsHealth.slo_status.worst_breach.target < 1
                        ? `${(opsHealth.slo_status.worst_breach.target * 100).toFixed(2)}%`
                        : opsHealth.slo_status.worst_breach.target.toFixed(0)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SLO Overview */}
      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
          <Activity size={14} />
          SLO Status (24h)
        </h3>
        {isLoading ? (
          <div className="flex justify-center py-8"><Loader2 size={20} className="animate-spin text-primary-400" /></div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {slos.map((slo: Record<string, string | number | boolean>) => (
              <div
                key={slo.key as string}
                className={cn(
                  'p-3 rounded-lg border',
                  slo.breach ? 'border-red-500/30 bg-red-500/5' : 'border-dark-border bg-dark-card'
                )}
              >
                <div className="flex items-center gap-2 mb-1">
                  {slo.breach ? <XCircle size={14} className="text-red-400" /> : <CheckCircle size={14} className="text-green-400" />}
                  <span className="text-xs text-gray-400 truncate">{slo.name as string}</span>
                </div>
                <p className={cn('text-lg font-bold', slo.breach ? 'text-red-400' : 'text-green-400')}>
                  {typeof slo.current === 'number' ? (slo.current as number > 1 ? (slo.current as number).toFixed(0) : `${((slo.current as number) * 100).toFixed(1)}%`) : slo.current}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Breaches */}
      {breaches.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-red-400 mb-3 flex items-center gap-2">
            <AlertTriangle size={14} />
            SLO Breaches ({breaches.length})
          </h3>
          <div className="space-y-2">
            {breaches.map((b: Record<string, string | number>) => (
              <div key={b.key as string} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                <p className="text-sm text-white">{b.name as string}</p>
                <p className="text-xs text-red-300 mt-1">
                  Current: {typeof b.current === 'number' && (b.current as number) < 1 ? `${((b.current as number) * 100).toFixed(2)}%` : b.current}
                  {b.target !== undefined && ` (target: ${typeof b.target === 'number' && (b.target as number) < 1 ? `${((b.target as number) * 100).toFixed(1)}%` : b.target})`}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Failure Signatures */}
      {signatures.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <TrendingDown size={14} />
            Failure Signatures (24h)
          </h3>
          <div className="space-y-2">
            {signatures.map((sig: Record<string, string | number>, i: number) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-dark-card border border-dark-border">
                <AlertTriangle size={14} className="text-orange-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{sig.signature as string}</p>
                  <p className="text-xs text-gray-500">{sig.description as string}</p>
                </div>
                <span className="text-xs text-gray-400">x{sig.total_count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Blocked Agents */}
      {blocked.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Ban size={14} />
            Blocked Agents ({blocked.length})
          </h3>
          <div className="space-y-2">
            {blocked.map((agent: Record<string, string>, i: number) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-dark-card border border-dark-border">
                <Shield size={14} className="text-red-400" />
                <div className="flex-1">
                  <p className="text-sm text-white">{agent.agent_name}</p>
                  <p className="text-xs text-gray-500">{agent.reason}</p>
                </div>
                {agent.ttl_hours && (
                  <span className="text-xs text-gray-400">{agent.ttl_hours}h TTL</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {!isLoading && breaches.length === 0 && signatures.length === 0 && blocked.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <CheckCircle size={32} className="mx-auto mb-2 opacity-50" />
          <p className="text-sm">All systems healthy. No breaches, failures, or blocked agents.</p>
        </div>
      )}

      {/* S2765: Recent Recycles */}
      {recyclesQuery.data && recyclesQuery.data.log_exists && recyclesQuery.data.items.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <RotateCw size={14} />
            Recent Recycles (last {recyclesQuery.data.count})
          </h3>
          <div className="space-y-1.5">
            {recyclesQuery.data.items.map((evt, i) => (
              <div key={`${evt.timestamp}-${i}`} className="flex items-center gap-3 p-2 rounded bg-dark-card border border-dark-border">
                <RotateCw size={12} className="text-green-400 shrink-0" />
                <code className="text-xs text-primary-400 font-mono shrink-0">
                  {evt.sha_short || 'unknown'}
                </code>
                <span className="text-xs text-gray-500 truncate flex-1">
                  {evt.timestamp}
                </span>
                {evt.seconds_ago !== null && (
                  <span className="text-xs text-gray-400 shrink-0">
                    {formatAgo(evt.seconds_ago)}
                  </span>
                )}
                <span className="text-xs text-gray-600 shrink-0">{evt.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* S2780 N22 v3: Zoom-Out Ledger preview — discoverability card
          pointing at the canonical home under system.sign-ledger. Full
          filtering, help, and content live on the dedicated sub-tab per
          Rigby S2780 V3 fold (semantic boundary — governance ledger
          does not co-locate with ops observability). */}
      {zoomOutPreviewQuery.data && zoomOutPreviewQuery.data.log_exists && (
        <button
          type="button"
          onClick={goToSignLedger}
          className="w-full text-left p-3 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/40 transition-colors flex items-center gap-3 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/40"
          aria-label="Open SIGN Ledger sub-tab"
        >
          <ScrollText size={14} className="text-primary-400 shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="text-sm text-gray-200">
              SIGN Ledger — {zoomOutPreviewQuery.data.total_rows} zoom-out{' '}
              {zoomOutPreviewQuery.data.total_rows === 1 ? 'fold' : 'folds'} on record
            </div>
            <div className="text-xs text-gray-500 mt-0.5 flex flex-wrap gap-x-2">
              <span>Advisory pattern evidence — not gates.</span>
              {Object.entries(zoomOutPreviewQuery.data.counts_by_classification).map(([k, v]) => (
                <span key={k} className="font-mono">
                  {k}: {v}
                </span>
              ))}
            </div>
          </div>
          <ChevronRight size={14} className="text-gray-500 shrink-0" aria-hidden />
        </button>
      )}

      {/* S2763: Close-Ceremony Ledger */}
      {ledgerQuery.data && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Layers size={14} />
            Recent Close-Ceremonies
            {ledgerFiltersActive && ledgerQuery.data.total_available !== undefined ? (
              <span className="text-xs text-gray-500">
                (showing {ledgerQuery.data.count} of {ledgerQuery.data.total_available} matches)
              </span>
            ) : (
              <span className="text-xs text-gray-500">
                (last {ledgerQuery.data.count})
              </span>
            )}
          </h3>

          {/* S2769 N8: compact filter row — session range + envelope-only + date range */}
          <div className="mb-3 p-2 rounded-lg bg-dark-card/50 border border-dark-border flex flex-wrap items-center gap-2 text-xs">
            <span className="text-gray-500">Session</span>
            <input
              type="number"
              inputMode="numeric"
              placeholder="min"
              value={ledgerFilters.sessionMin}
              onChange={(e) => setLedgerFilters((f) => ({ ...f, sessionMin: e.target.value }))}
              className="w-16 px-2 py-1 bg-dark-bg border border-dark-border rounded text-gray-300 placeholder:text-gray-600 focus:outline-none focus:border-primary-500/40"
              aria-label="Minimum session number"
            />
            <span className="text-gray-600">–</span>
            <input
              type="number"
              inputMode="numeric"
              placeholder="max"
              value={ledgerFilters.sessionMax}
              onChange={(e) => setLedgerFilters((f) => ({ ...f, sessionMax: e.target.value }))}
              className="w-16 px-2 py-1 bg-dark-bg border border-dark-border rounded text-gray-300 placeholder:text-gray-600 focus:outline-none focus:border-primary-500/40"
              aria-label="Maximum session number"
            />
            <label className="flex items-center gap-1.5 ml-2 cursor-pointer">
              <input
                type="checkbox"
                checked={ledgerFilters.envelopeOnly}
                onChange={(e) => setLedgerFilters((f) => ({ ...f, envelopeOnly: e.target.checked }))}
                className="accent-primary-500"
              />
              <span className="text-gray-400">envelope only</span>
            </label>
            <span className="text-gray-500 ml-2">Date</span>
            <input
              type="date"
              value={ledgerFilters.dateFrom}
              onChange={(e) => setLedgerFilters((f) => ({ ...f, dateFrom: e.target.value }))}
              className="px-2 py-1 bg-dark-bg border border-dark-border rounded text-gray-300 focus:outline-none focus:border-primary-500/40"
              aria-label="Date from"
            />
            <span className="text-gray-600">–</span>
            <input
              type="date"
              value={ledgerFilters.dateTo}
              onChange={(e) => setLedgerFilters((f) => ({ ...f, dateTo: e.target.value }))}
              className="px-2 py-1 bg-dark-bg border border-dark-border rounded text-gray-300 focus:outline-none focus:border-primary-500/40"
              aria-label="Date to"
            />
            {/* S2771 N14: text search input — debounced 200ms; case-insensitive
                substring match against the full handoff body server-side. */}
            <input
              type="search"
              placeholder="search text…"
              value={ledgerFilters.text}
              onChange={(e) => setLedgerFilters((f) => ({ ...f, text: e.target.value }))}
              className="ml-2 flex-1 min-w-[8rem] max-w-[18rem] px-2 py-1 bg-dark-bg border border-dark-border rounded text-gray-300 placeholder:text-gray-600 focus:outline-none focus:border-primary-500/40"
              aria-label="Search handoff body text"
            />
            {ledgerFiltersActive && (
              <button
                type="button"
                onClick={resetLedgerFilters}
                className="ml-auto px-2 py-1 rounded text-gray-500 hover:text-gray-300 hover:bg-dark-border transition-colors"
              >
                clear
              </button>
            )}
          </div>

          {ledgerQuery.data.items.length > 0 ? (
            <>
              <div className="space-y-2">
                {ledgerQuery.data.items.map((item) => (
                  <LedgerRow
                    key={item.session_number}
                    item={item}
                    onOpen={openViewer}
                    onCopy={copyPath}
                    copiedPath={copiedPath}
                  />
                ))}
              </div>
              {ledgerQuery.data.total_available !== undefined &&
                ledgerQuery.data.total_available > ledgerQuery.data.count &&
                ledgerLimit < LEDGER_LIMIT_EXPANDED && (
                  <button
                    type="button"
                    onClick={() => setLedgerLimit(LEDGER_LIMIT_EXPANDED)}
                    className="mt-2 w-full py-2 text-xs text-primary-400 hover:text-primary-300 rounded-lg border border-dark-border hover:border-primary-500/40 transition-colors"
                  >
                    Show up to {LEDGER_LIMIT_EXPANDED} (currently {ledgerQuery.data.count} of {ledgerQuery.data.total_available})
                  </button>
                )}
            </>
          ) : (
            <div className="p-4 text-center text-xs text-gray-500 border border-dashed border-dark-border rounded-lg">
              No close-ceremonies match the current filters.
            </div>
          )}
        </div>
      )}

      {/* S2767 N4: DocumentViewer drawer — mounted only when a doc is selected;
          Suspense catches the lazy chunk load. Fallback is null since drawer
          renders its own loading state once mounted. */}
      <Suspense fallback={null}>
        {viewerDoc && (
          <LazyDocumentViewer
            documentPath={viewerDoc.path}
            title={viewerDoc.title}
            category="handoff"
            categoryColor="#22d3ee"
            isOpen={true}
            onClose={closeViewer}
          />
        )}
      </Suspense>
    </div>
  )
}
