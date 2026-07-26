/**
 * S2971: Signals Feed Explorer.
 *
 * Table of LegacySpiderData rows + filters + row-detail drawer.
 * Backend: GET /api/signals/feed/, GET /api/signals/feed/<uuid>/
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Loader2, X, ExternalLink, ChevronLeft, ChevronRight } from 'lucide-react'
import { signalsApi } from '@/lib/api'
import { cn } from '@/lib/cn'
import { formatMST, formatNumber } from './formatters'
import type { SignalsWindow } from './SignalsTab'

const DEFAULT_DATA_TYPES = ['news', 'financial', 'tech', 'ai_ml']
const ALL_DATA_TYPES = [...DEFAULT_DATA_TYPES, 'design', 'crypto', 'sports', 'legal', 'health']
const PAGE_SIZE = 25

type EmbeddingFilter = 'all' | 'present' | 'missing' | 'marked_empty'

interface FeedItem {
  id: string
  spider_name: string
  data_type: string
  source_url: string
  is_actionable: boolean
  embedding_status: 'present' | 'empty' | 'missing' | 'marked_empty'
  embedding_text: string
  preview: string
  created_at: string
}

interface FeedResponse {
  items: FeedItem[]
  total: number
  offset: number
  limit: number
  has_more: boolean
}

interface FeedDetailResponse extends FeedItem {
  raw_data: unknown
  processed_data: unknown
}

interface Props {
  windowHours: SignalsWindow
}

export function SignalsFeedView({ windowHours }: Props) {
  const [query, setQuery] = useState('')
  const [dataTypes, setDataTypes] = useState<string[]>(DEFAULT_DATA_TYPES)
  const [spiderName, setSpiderName] = useState('')
  const [actionableOnly, setActionableOnly] = useState(true)
  const [embeddingFilter, setEmbeddingFilter] = useState<EmbeddingFilter>('all')
  const [offset, setOffset] = useState(0)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const feedQ = useQuery({
    queryKey: [
      'signals-feed',
      query, dataTypes.join(','), spiderName, actionableOnly, embeddingFilter, windowHours, offset,
    ],
    queryFn: async () => {
      const resp = await signalsApi.feed({
        query: query || undefined,
        data_types: dataTypes.length > 0 ? dataTypes : undefined,
        spider_name: spiderName || undefined,
        actionable_only: actionableOnly,
        embedding_status: embeddingFilter,
        window_hours: windowHours,
        limit: PAGE_SIZE,
        offset,
      })
      return resp.data as FeedResponse
    },
    staleTime: 15_000,
  })

  const detailQ = useQuery({
    queryKey: ['signals-feed-detail', selectedId],
    queryFn: async () => {
      if (!selectedId) return null
      const resp = await signalsApi.feedDetail(selectedId)
      return resp.data as FeedDetailResponse
    },
    enabled: !!selectedId,
    staleTime: 60_000,
  })

  function toggleDataType(dt: string) {
    setOffset(0)
    setDataTypes(prev =>
      prev.includes(dt) ? prev.filter(x => x !== dt) : [...prev, dt]
    )
  }

  const total = feedQ.data?.total ?? 0
  const pageStart = offset + 1
  const pageEnd = Math.min(offset + PAGE_SIZE, total)

  return (
    <div className="relative">
      {/* Filters */}
      <div className="mb-4 space-y-3 rounded-lg border border-gray-800 bg-gray-900/40 p-3">
        <div className="flex flex-wrap gap-2 items-center">
          <input
            type="text"
            value={query}
            onChange={e => { setQuery(e.target.value); setOffset(0) }}
            placeholder="Search embedding_text or source_url…"
            className="flex-1 min-w-[200px] px-3 py-1.5 rounded bg-gray-950 border border-gray-800 text-sm text-white placeholder-gray-500"
          />
          <input
            type="text"
            value={spiderName}
            onChange={e => { setSpiderName(e.target.value); setOffset(0) }}
            placeholder="Spider name…"
            className="w-[180px] px-3 py-1.5 rounded bg-gray-950 border border-gray-800 text-sm text-white placeholder-gray-500"
          />
        </div>

        <div className="flex flex-wrap gap-2 items-center text-xs">
          <span className="text-gray-500">Types:</span>
          {ALL_DATA_TYPES.map(dt => (
            <button
              key={dt}
              onClick={() => toggleDataType(dt)}
              className={cn(
                'px-2 py-1 rounded border',
                dataTypes.includes(dt)
                  ? 'bg-primary-500/20 border-primary-500/40 text-primary-300'
                  : 'bg-gray-950 border-gray-800 text-gray-500 hover:text-gray-300',
              )}
            >
              {dt}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-4 items-center text-xs">
          <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={actionableOnly}
              onChange={e => { setActionableOnly(e.target.checked); setOffset(0) }}
              className="accent-primary-500"
            />
            Actionable only
          </label>

          <div className="flex items-center gap-2">
            <span className="text-gray-500">Embedding:</span>
            {(['all', 'present', 'missing', 'marked_empty'] as EmbeddingFilter[]).map(v => (
              <button
                key={v}
                onClick={() => { setEmbeddingFilter(v); setOffset(0) }}
                className={cn(
                  'px-2 py-1 rounded border capitalize',
                  embeddingFilter === v
                    ? 'bg-primary-500/20 border-primary-500/40 text-primary-300'
                    : 'bg-gray-950 border-gray-800 text-gray-500 hover:text-gray-300',
                )}
              >
                {v.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results header */}
      <div className="flex items-center justify-between mb-2 text-xs text-gray-500">
        <div>
          {feedQ.isLoading ? 'Loading…' : `${formatNumber(pageStart)}-${formatNumber(pageEnd)} of ${formatNumber(total)}`}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            disabled={offset === 0}
            className="p-1 rounded hover:bg-gray-800 disabled:opacity-30"
          >
            <ChevronLeft size={14} />
          </button>
          <button
            onClick={() => setOffset(offset + PAGE_SIZE)}
            disabled={!feedQ.data?.has_more}
            className="p-1 rounded hover:bg-gray-800 disabled:opacity-30"
          >
            <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-gray-800 overflow-hidden">
        <table className="w-full text-xs">
          <thead className="bg-gray-900/60 text-gray-400 uppercase text-[10px]">
            <tr>
              <th className="text-left px-3 py-2">Detected</th>
              <th className="text-left px-3 py-2">Type</th>
              <th className="text-left px-3 py-2">Spider</th>
              <th className="text-left px-3 py-2">Preview</th>
              <th className="text-left px-3 py-2">Emb.</th>
              <th className="text-left px-3 py-2">Actionable</th>
              <th className="text-left px-3 py-2">URL</th>
            </tr>
          </thead>
          <tbody>
            {feedQ.isLoading && (
              <tr><td colSpan={7} className="px-3 py-6 text-center text-gray-500">
                <Loader2 size={14} className="inline animate-spin mr-2" />Loading rows…
              </td></tr>
            )}
            {feedQ.error && (
              <tr><td colSpan={7} className="px-3 py-6 text-center text-red-400">
                {(feedQ.error as Error).message || 'Failed to load'}
              </td></tr>
            )}
            {feedQ.data && feedQ.data.items.length === 0 && (
              <tr><td colSpan={7} className="px-3 py-6 text-center text-gray-500">
                No rows match the current filters.
              </td></tr>
            )}
            {feedQ.data?.items.map(row => (
              <tr
                key={row.id}
                onClick={() => setSelectedId(row.id)}
                className="border-t border-gray-800/60 hover:bg-gray-800/40 cursor-pointer"
              >
                <td className="px-3 py-2 whitespace-nowrap text-gray-400">{formatMST(row.created_at)}</td>
                <td className="px-3 py-2 text-gray-300 capitalize">{row.data_type || '—'}</td>
                <td className="px-3 py-2 text-gray-300">{row.spider_name || '—'}</td>
                <td className="px-3 py-2 text-gray-200 max-w-[280px] truncate" title={row.preview}>
                  {row.preview || <span className="text-gray-600">—</span>}
                </td>
                <td className="px-3 py-2">
                  <EmbeddingBadge status={row.embedding_status} />
                </td>
                <td className="px-3 py-2">
                  {row.is_actionable ? (
                    <span className="text-emerald-400">✓</span>
                  ) : (
                    <span className="text-gray-600">—</span>
                  )}
                </td>
                <td className="px-3 py-2 max-w-[200px] truncate">
                  {row.source_url ? (
                    <a
                      href={row.source_url}
                      target="_blank"
                      rel="noreferrer"
                      onClick={e => e.stopPropagation()}
                      className="text-primary-400 hover:text-primary-300 inline-flex items-center gap-1"
                    >
                      link <ExternalLink size={10} />
                    </a>
                  ) : <span className="text-gray-600">—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedId && (
        <RowDrawer
          detail={detailQ.data ?? null}
          isLoading={detailQ.isLoading}
          error={detailQ.error as Error | null}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  )
}

function EmbeddingBadge({ status }: { status: FeedItem['embedding_status'] }) {
  const map: Record<FeedItem['embedding_status'], { label: string; cls: string }> = {
    present: { label: 'present', cls: 'bg-emerald-500/20 text-emerald-300' },
    missing: { label: 'missing', cls: 'bg-yellow-500/20 text-yellow-300' },
    empty: { label: 'empty', cls: 'bg-yellow-500/20 text-yellow-300' },
    marked_empty: { label: 'empty·flag', cls: 'bg-gray-700 text-gray-400' },
  }
  const b = map[status] ?? map.missing
  return (
    <span className={cn('text-[10px] px-1.5 py-0.5 rounded uppercase tracking-wide', b.cls)}>
      {b.label}
    </span>
  )
}

function RowDrawer({
  detail,
  isLoading,
  error,
  onClose,
}: {
  detail: FeedDetailResponse | null
  isLoading: boolean
  error: Error | null
  onClose: () => void
}) {
  return (
    <div
      role="dialog"
      className="fixed inset-y-0 right-0 z-40 w-full max-w-2xl bg-gray-950 border-l border-gray-800 shadow-2xl overflow-y-auto"
    >
      <div className="sticky top-0 z-10 flex items-center justify-between p-3 border-b border-gray-800 bg-gray-950">
        <h3 className="text-sm font-semibold text-gray-100">Row detail</h3>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-gray-800 text-gray-400"
          aria-label="Close drawer"
        >
          <X size={16} />
        </button>
      </div>

      <div className="p-4 space-y-4 text-sm">
        {isLoading && (
          <div className="text-gray-500 flex items-center gap-2">
            <Loader2 size={14} className="animate-spin" /> Loading…
          </div>
        )}
        {error && (
          <div className="text-red-400">{error.message}</div>
        )}
        {detail && (
          <>
            <DetailField label="Spider">{detail.spider_name}</DetailField>
            <DetailField label="Type">{detail.data_type}</DetailField>
            <DetailField label="Detected">{formatMST(detail.created_at)}</DetailField>
            <DetailField label="Source URL">
              {detail.source_url ? (
                <a href={detail.source_url} target="_blank" rel="noreferrer" className="text-primary-400 hover:text-primary-300 break-all">
                  {detail.source_url}
                </a>
              ) : '—'}
            </DetailField>
            <DetailField label="Actionable">{detail.is_actionable ? 'yes' : 'no'}</DetailField>
            <DetailField label="Embedding">
              <EmbeddingBadge status={detail.embedding_status} />
            </DetailField>

            <CollapsibleJson label="embedding_text" value={detail.embedding_text} />
            <CollapsibleJson label="raw_data" value={detail.raw_data} />
            <CollapsibleJson label="processed_data" value={detail.processed_data} />
          </>
        )}
      </div>
    </div>
  )
}

function DetailField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wide text-gray-500">{label}</div>
      <div className="text-gray-200 mt-0.5">{children}</div>
    </div>
  )
}

function CollapsibleJson({ label, value }: { label: string; value: unknown }) {
  const [open, setOpen] = useState(false)
  const text = typeof value === 'string' ? value : JSON.stringify(value, null, 2)
  const truncated = text.length > 600
  const displayText = open || !truncated ? text : `${text.slice(0, 600)}…`
  return (
    <div className="border-t border-gray-800/60 pt-3">
      <div className="flex items-center justify-between mb-1">
        <div className="text-[10px] uppercase tracking-wide text-gray-500">{label}</div>
        {truncated && (
          <button
            onClick={() => setOpen(o => !o)}
            className="text-[10px] text-primary-400 hover:text-primary-300"
          >
            {open ? 'collapse' : 'expand'}
          </button>
        )}
      </div>
      <pre className="text-[11px] bg-gray-900/60 p-2 rounded overflow-x-auto text-gray-300 whitespace-pre-wrap break-words">
        {displayText || <span className="text-gray-600">— empty —</span>}
      </pre>
    </div>
  )
}
