/**
 * Findings Tab — S2989 Phase B.
 *
 * Surfaces docs/research/ audit + canonical-summary + IDBT-debt findings
 * indexed by `python manage.py index_doc_research_findings`. Chris can:
 *   - filter by status / domain / source_type / confidence / text
 *   - mark fixed / dismissed / reopen
 *   - send to Rigby (spec-shape Deliverable via Phase A generator)
 *
 * Findings are the single source of truth for status; the source doc is
 * evidence, never authority.
 */
import { useEffect, useMemo, useState } from 'react'
import {
  AlertTriangle,
  Check,
  ChevronDown,
  ChevronRight,
  Circle,
  Loader2,
  Search,
  Send,
  X,
} from 'lucide-react'
import { api } from '@/lib/api'

type FindingStatus = 'open' | 'fixed' | 'dismissed'
type Confidence = 'high' | 'medium' | 'low'
type SourceType = 'audit' | 'canonical_summary' | 'implementation_debt'

interface Finding {
  id: string
  doc_path: string
  domain_slug: string
  source_type: SourceType
  source_heading: string
  text: string
  confidence: Confidence
  tags: string[]
  status: FindingStatus
  resolved_at: string | null
  resolved_by: string | null
  resolution_note: string
  deliverable_id: string | null
  first_seen_at: string | null
  last_seen_at: string | null
  metadata: Record<string, unknown>
}

interface ListResponse {
  total: number
  page: number
  page_size: number
  findings: Finding[]
}

const DONKEY_BETZ_WORKSPACE_ID = 'b4503364-2573-4401-9e28-61a739e0ce50'

const STATUS_LABELS: Record<FindingStatus, string> = {
  open: 'Open',
  fixed: 'Fixed',
  dismissed: 'Dismissed',
}

const CONFIDENCE_ORDER: Record<Confidence, number> = { high: 0, medium: 1, low: 2 }

function ConfidenceBadge({ c }: { c: Confidence }) {
  const color =
    c === 'high'
      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
      : c === 'medium'
        ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
        : 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  return (
    <span className={`px-1.5 py-0.5 rounded border text-[10px] uppercase tracking-wide ${color}`}>
      {c}
    </span>
  )
}

function StatusBadge({ s }: { s: FindingStatus }) {
  const color =
    s === 'open'
      ? 'bg-blue-500/20 text-blue-300 border-blue-500/30'
      : s === 'fixed'
        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
        : 'bg-gray-500/20 text-gray-500 border-gray-500/30'
  return (
    <span className={`px-1.5 py-0.5 rounded border text-[10px] uppercase tracking-wide ${color}`}>
      {STATUS_LABELS[s]}
    </span>
  )
}

function FindingRow({
  finding,
  onMark,
  onSend,
  sending,
  markingStatus,
}: {
  finding: Finding
  onMark: (status: FindingStatus) => void
  onSend: () => void
  sending: boolean
  markingStatus: FindingStatus | null
}) {
  const [open, setOpen] = useState(false)
  const isFixed = finding.status === 'fixed'
  const isDismissed = finding.status === 'dismissed'

  return (
    <div
      className={`border rounded-lg px-3 py-2 text-sm ${
        isFixed
          ? 'border-emerald-500/20 bg-emerald-500/5'
          : isDismissed
            ? 'border-gray-700/50 bg-gray-800/20 opacity-60'
            : 'border-gray-700 bg-gray-800/50'
      }`}
    >
      <div className="flex items-start gap-2">
        <button
          onClick={() => setOpen(v => !v)}
          className="mt-0.5 text-gray-500 hover:text-gray-300"
          aria-label={open ? 'collapse' : 'expand'}
        >
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap text-[11px] text-gray-400 mb-1">
            <StatusBadge s={finding.status} />
            <ConfidenceBadge c={finding.confidence} />
            <span className="px-1.5 py-0.5 rounded bg-gray-700/50 border border-gray-600 text-gray-300">
              {finding.domain_slug || '(no domain)'}
            </span>
            <span className="text-gray-500 truncate max-w-[26rem]" title={finding.doc_path}>
              {finding.doc_path.replace(/^docs\/research\//, '')}
            </span>
          </div>
          <div className="text-gray-200 leading-snug">{finding.text}</div>
          {open && (
            <div className="mt-2 space-y-2 text-xs text-gray-400 border-t border-gray-700 pt-2">
              <div>
                <span className="font-medium text-gray-300">Section:</span>{' '}
                {finding.source_heading || '(none)'}
              </div>
              {finding.tags.length > 0 && (
                <div>
                  <span className="font-medium text-gray-300">Tags:</span>{' '}
                  {finding.tags.join(', ')}
                </div>
              )}
              {finding.resolution_note && (
                <div>
                  <span className="font-medium text-gray-300">Resolution note:</span>{' '}
                  {finding.resolution_note}
                </div>
              )}
              {finding.deliverable_id && (
                <div>
                  <span className="font-medium text-gray-300">Deliverable:</span>{' '}
                  <a
                    href={`/workspace?tab=work&sub=deliverables&workspace=${DONKEY_BETZ_WORKSPACE_ID}`}
                    className="text-primary-400 underline hover:text-primary-300"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {finding.deliverable_id.slice(0, 8)}
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex flex-col gap-1 items-end shrink-0">
          {finding.status === 'open' && (
            <>
              <button
                onClick={onSend}
                disabled={sending}
                className="px-2 py-1 text-xs rounded border border-primary-500/40 bg-primary-500/10 text-primary-300 hover:bg-primary-500/20 disabled:opacity-50 flex items-center gap-1"
                title="Create spec-shape Deliverable in Donkey Betz workspace"
              >
                {sending ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
                Send to Rigby
              </button>
              <button
                onClick={() => onMark('fixed')}
                disabled={markingStatus !== null}
                className="px-2 py-1 text-xs rounded border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20 disabled:opacity-50 flex items-center gap-1"
              >
                {markingStatus === 'fixed' ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <Check size={12} />
                )}
                Mark fixed
              </button>
              <button
                onClick={() => onMark('dismissed')}
                disabled={markingStatus !== null}
                className="px-2 py-1 text-xs rounded border border-gray-500/40 bg-gray-500/10 text-gray-400 hover:bg-gray-500/20 disabled:opacity-50 flex items-center gap-1"
              >
                {markingStatus === 'dismissed' ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <X size={12} />
                )}
                Dismiss
              </button>
            </>
          )}
          {finding.status !== 'open' && (
            <button
              onClick={() => onMark('open')}
              disabled={markingStatus !== null}
              className="px-2 py-1 text-xs rounded border border-blue-500/40 bg-blue-500/10 text-blue-300 hover:bg-blue-500/20 disabled:opacity-50 flex items-center gap-1"
            >
              {markingStatus === 'open' ? (
                <Loader2 size={12} className="animate-spin" />
              ) : (
                <Circle size={12} />
              )}
              Reopen
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export function FindingsTab() {
  const [status, setStatus] = useState<'open' | 'fixed' | 'dismissed' | 'all'>('open')
  const [domainSlug, setDomainSlug] = useState('')
  const [sourceType, setSourceType] = useState<'' | SourceType>('')
  const [minConfidence, setMinConfidence] = useState<'' | 'high' | 'medium'>('medium')
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize] = useState(25)
  const [findings, setFindings] = useState<Finding[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sendingId, setSendingId] = useState<string | null>(null)
  const [markingId, setMarkingId] = useState<string | null>(null)
  const [markingStatusOn, setMarkingStatusOn] = useState<FindingStatus | null>(null)
  const [toast, setToast] = useState<{ kind: 'ok' | 'err'; text: string } | null>(null)

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search.trim()), 300)
    return () => clearTimeout(t)
  }, [search])

  useEffect(() => {
    let cancelled = false
    const fetch = async () => {
      setLoading(true)
      setError(null)
      try {
        const params: Record<string, string | number> = {
          status,
          page,
          page_size: pageSize,
        }
        if (domainSlug) params.domain_slug = domainSlug
        if (sourceType) params.source_type = sourceType
        if (minConfidence) params.min_confidence = minConfidence
        if (debouncedSearch) params.search = debouncedSearch
        const resp = await api.get<ListResponse>('/repo/doc-research-findings/', { params })
        if (cancelled) return
        setFindings(resp.data.findings)
        setTotal(resp.data.total)
      } catch (err: any) {
        if (cancelled) return
        setError(err?.response?.data?.error || err?.message || 'Failed to load findings')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void fetch()
    return () => {
      cancelled = true
    }
  }, [status, domainSlug, sourceType, minConfidence, debouncedSearch, page, pageSize])

  const handleMark = async (finding: Finding, next: FindingStatus) => {
    setMarkingId(finding.id)
    setMarkingStatusOn(next)
    try {
      const resp = await api.post<{ finding: Finding }>(
        `/repo/doc-research-findings/${finding.id}/mark/`,
        { status: next },
      )
      setFindings(prev =>
        prev.map(f => (f.id === finding.id ? resp.data.finding : f)),
      )
      setToast({ kind: 'ok', text: `Marked ${STATUS_LABELS[next].toLowerCase()}` })
    } catch (err: any) {
      setToast({
        kind: 'err',
        text: err?.response?.data?.error || 'Mark failed',
      })
    } finally {
      setMarkingId(null)
      setMarkingStatusOn(null)
    }
  }

  const handleSend = async (finding: Finding) => {
    setSendingId(finding.id)
    try {
      const resp = await api.post<{ finding: Finding; deliverable_id: string }>(
        `/repo/doc-research-findings/${finding.id}/send-to-rigby/`,
        {},
      )
      setFindings(prev =>
        prev.map(f => (f.id === finding.id ? resp.data.finding : f)),
      )
      setToast({
        kind: 'ok',
        text: `Deliverable created (${resp.data.deliverable_id.slice(0, 8)})`,
      })
    } catch (err: any) {
      setToast({
        kind: 'err',
        text: err?.response?.data?.error || 'Send failed',
      })
    } finally {
      setSendingId(null)
    }
  }

  const sortedFindings = useMemo(
    () =>
      [...findings].sort((a, b) => {
        const dc = CONFIDENCE_ORDER[a.confidence] - CONFIDENCE_ORDER[b.confidence]
        if (dc !== 0) return dc
        return a.doc_path.localeCompare(b.doc_path)
      }),
    [findings],
  )

  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), 3500)
    return () => clearTimeout(t)
  }, [toast])

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h2 className="text-lg font-semibold text-white">Audit Findings</h2>
          <p className="text-xs text-gray-400 mt-1">
            Actionable bullets extracted from{' '}
            <code className="text-gray-300">docs/research/</code> audits + canonical
            summaries + <code className="text-gray-300">IMPLEMENTATION_DEBT.md</code>.
            Send any open finding to Rigby to package as an execution-ready spec.
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 items-center bg-gray-800/40 border border-gray-700 rounded-lg p-3">
        <select
          value={status}
          onChange={e => {
            setStatus(e.target.value as any)
            setPage(1)
          }}
          className="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-200"
        >
          <option value="open">Status: Open</option>
          <option value="fixed">Status: Fixed</option>
          <option value="dismissed">Status: Dismissed</option>
          <option value="all">Status: All</option>
        </select>
        <select
          value={sourceType}
          onChange={e => {
            setSourceType(e.target.value as any)
            setPage(1)
          }}
          className="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-200"
        >
          <option value="">Source: Any</option>
          <option value="audit">Source: Audit</option>
          <option value="canonical_summary">Source: Canonical Summary</option>
          <option value="implementation_debt">Source: Implementation Debt</option>
        </select>
        <select
          value={minConfidence}
          onChange={e => {
            setMinConfidence(e.target.value as any)
            setPage(1)
          }}
          className="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-200"
        >
          <option value="">Min confidence: Any</option>
          <option value="medium">Min confidence: Medium+</option>
          <option value="high">Min confidence: High only</option>
        </select>
        <input
          type="text"
          value={domainSlug}
          onChange={e => {
            setDomainSlug(e.target.value)
            setPage(1)
          }}
          placeholder="Domain slug (e.g. pa)"
          className="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-200 w-40"
        />
        <div className="relative flex-1 min-w-[16rem]">
          <Search
            size={12}
            className="absolute left-2 top-1/2 -translate-y-1/2 text-gray-500"
          />
          <input
            type="text"
            value={search}
            onChange={e => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="Search text…"
            className="w-full text-xs bg-gray-900 border border-gray-700 rounded pl-6 pr-2 py-1 text-gray-200"
          />
        </div>
        <div className="text-xs text-gray-400 ml-auto">
          {loading ? 'Loading…' : `${total} finding${total === 1 ? '' : 's'}`}
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-300 bg-red-500/10 border border-red-500/30 rounded p-3 text-sm">
          <AlertTriangle size={14} />
          {error}
        </div>
      )}

      {/* Results */}
      <div className="space-y-2">
        {sortedFindings.map(f => (
          <FindingRow
            key={f.id}
            finding={f}
            onMark={next => void handleMark(f, next)}
            onSend={() => void handleSend(f)}
            sending={sendingId === f.id}
            markingStatus={markingId === f.id ? markingStatusOn : null}
          />
        ))}
        {!loading && sortedFindings.length === 0 && (
          <div className="text-sm text-gray-500 text-center py-8 border border-dashed border-gray-700 rounded">
            No findings match the current filters.
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="px-2 py-1 rounded border border-gray-700 disabled:opacity-40 hover:bg-gray-800"
          >
            Prev
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="px-2 py-1 rounded border border-gray-700 disabled:opacity-40 hover:bg-gray-800"
          >
            Next
          </button>
        </div>
      )}

      {toast && (
        <div
          className={`fixed bottom-4 right-4 px-3 py-2 rounded shadow-lg text-sm border ${
            toast.kind === 'ok'
              ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-200'
              : 'bg-red-500/20 border-red-500/40 text-red-200'
          }`}
        >
          {toast.text}
        </div>
      )}
    </div>
  )
}
