/**
 * S2971: Signal Cluster Explorer.
 *
 * Backend:
 *   GET /api/v1/signal-clusters/  (extended filters: window_hours, min_confidence,
 *                                  source_spider, query)
 *   GET /api/v1/signal-clusters/<uuid>/ (detail)
 */

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2, X, ChevronLeft, ChevronRight, Rocket, CheckCircle2, AlertTriangle } from 'lucide-react'
import { signalsApi } from '@/lib/api'
import { formatMST, formatNumber, formatConfidence } from './formatters'
import type { SignalsWindow } from './SignalsTab'

const PAGE_SIZE = 25

const PATTERN_TYPES = [
  'demand_spike', 'trend_emergence', 'sentiment_shift',
  'opportunity_window', 'knowledge_gap', 'competitive_signal',
  'market_movement', 'skill_demand', 'content_gap', 'user_need',
]

interface ClusterRow {
  id: string
  name: string
  pattern_type: string
  strength: number
  novelty: number
  confidence: number
  urgency: number
  status: string
  detected_at: string
  signal_count: number
  total_signals: number
  source_breakdown: Record<string, number>
  keywords: string[]
}

interface ClustersResponse {
  count: number
  next: string | null
  previous: string | null
  results: ClusterRow[]
}

interface ClusterDetail extends ClusterRow {
  spider_data_ids: string[]
  trigger_event_ids: string[]
  sample_signals: Array<{ source?: string; text?: string }>
  signal_window_start: string | null
  signal_window_end: string | null
  confirmed_at: string | null
  expires_at: string | null
  decay_rate: number
}

interface Props {
  windowHours: SignalsWindow
}

export function SignalsClustersView({ windowHours }: Props) {
  const [query, setQuery] = useState('')
  const [patternType, setPatternType] = useState<string>('')
  const [minConfidence, setMinConfidence] = useState<number>(0)
  const [sourceSpiders, setSourceSpiders] = useState<string>('')  // comma-separated
  const [page, setPage] = useState(1)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const clustersQ = useQuery({
    queryKey: ['signals-clusters', query, patternType, minConfidence, sourceSpiders, windowHours, page],
    queryFn: async () => {
      const spiderList = sourceSpiders
        .split(',')
        .map(s => s.trim())
        .filter(Boolean)
      const resp = await signalsApi.clusters({
        query: query || undefined,
        pattern_type: patternType || undefined,
        min_confidence: minConfidence > 0 ? minConfidence : undefined,
        source_spider: spiderList.length > 0 ? spiderList : undefined,
        window_hours: windowHours,
        page,
        page_size: PAGE_SIZE,
      })
      return resp.data as ClustersResponse
    },
    staleTime: 15_000,
  })

  const detailQ = useQuery({
    queryKey: ['signals-cluster-detail', selectedId],
    queryFn: async () => {
      if (!selectedId) return null
      const resp = await signalsApi.clusterDetail(selectedId)
      return resp.data as ClusterDetail
    },
    enabled: !!selectedId,
    staleTime: 60_000,
  })

  const total = clustersQ.data?.count ?? 0
  const pageStart = total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1
  const pageEnd = Math.min(page * PAGE_SIZE, total)

  return (
    <div className="relative">
      {/* Filters */}
      <div className="mb-4 space-y-3 rounded-lg border border-gray-800 bg-gray-900/40 p-3">
        <div className="flex flex-wrap gap-2 items-center">
          <input
            type="text"
            value={query}
            onChange={e => { setQuery(e.target.value); setPage(1) }}
            placeholder="Search name / keywords…"
            className="flex-1 min-w-[200px] px-3 py-1.5 rounded bg-gray-950 border border-gray-800 text-sm text-white placeholder-gray-500"
          />
          <input
            type="text"
            value={sourceSpiders}
            onChange={e => { setSourceSpiders(e.target.value); setPage(1) }}
            placeholder="Source spider(s), comma-separated…"
            className="w-[240px] px-3 py-1.5 rounded bg-gray-950 border border-gray-800 text-sm text-white placeholder-gray-500"
          />
        </div>

        <div className="flex flex-wrap gap-3 items-center text-xs">
          <label className="flex items-center gap-2 text-gray-400">
            Pattern type
            <select
              value={patternType}
              onChange={e => { setPatternType(e.target.value); setPage(1) }}
              className="px-2 py-1 rounded bg-gray-950 border border-gray-800 text-gray-200"
            >
              <option value="">All</option>
              {PATTERN_TYPES.map(pt => (
                <option key={pt} value={pt}>{pt.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </label>

          <label className="flex items-center gap-2 text-gray-400">
            Min confidence
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={minConfidence}
              onChange={e => { setMinConfidence(parseFloat(e.target.value)); setPage(1) }}
              className="accent-primary-500"
            />
            <span className="text-primary-400 w-10 text-right">
              {minConfidence === 0 ? 'any' : `${Math.round(minConfidence * 100)}%`}
            </span>
          </label>
        </div>
      </div>

      {/* Results header */}
      <div className="flex items-center justify-between mb-2 text-xs text-gray-500">
        <div>
          {clustersQ.isLoading ? 'Loading…' : `${formatNumber(pageStart)}-${formatNumber(pageEnd)} of ${formatNumber(total)}`}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="p-1 rounded hover:bg-gray-800 disabled:opacity-30"
          >
            <ChevronLeft size={14} />
          </button>
          <button
            onClick={() => setPage(page + 1)}
            disabled={!clustersQ.data?.next}
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
              <th className="text-left px-3 py-2">Name</th>
              <th className="text-left px-3 py-2">Pattern</th>
              <th className="text-left px-3 py-2">Conf.</th>
              <th className="text-left px-3 py-2">Signals</th>
              <th className="text-left px-3 py-2">Sources</th>
            </tr>
          </thead>
          <tbody>
            {clustersQ.isLoading && (
              <tr><td colSpan={6} className="px-3 py-6 text-center text-gray-500">
                <Loader2 size={14} className="inline animate-spin mr-2" />Loading clusters…
              </td></tr>
            )}
            {clustersQ.error && (
              <tr><td colSpan={6} className="px-3 py-6 text-center text-red-400">
                {(clustersQ.error as Error).message || 'Failed to load'}
              </td></tr>
            )}
            {clustersQ.data && clustersQ.data.results.length === 0 && (
              <tr><td colSpan={6} className="px-3 py-6 text-center text-gray-500">
                No clusters match the current filters.
              </td></tr>
            )}
            {clustersQ.data?.results.map(row => (
              <tr
                key={row.id}
                onClick={() => setSelectedId(row.id)}
                className="border-t border-gray-800/60 hover:bg-gray-800/40 cursor-pointer"
              >
                <td className="px-3 py-2 whitespace-nowrap text-gray-400">{formatMST(row.detected_at)}</td>
                <td className="px-3 py-2 text-gray-200 max-w-[260px]">
                  <div className="truncate" title={row.name}>{row.name}</div>
                  {row.keywords && row.keywords.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {row.keywords.slice(0, 3).map(kw => (
                        <span key={kw} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800/70 text-gray-500">
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td className="px-3 py-2 text-gray-300 capitalize">{row.pattern_type.replace(/_/g, ' ')}</td>
                <td className="px-3 py-2 text-primary-400">{formatConfidence(row.confidence)}</td>
                <td className="px-3 py-2 text-gray-300">{formatNumber(row.signal_count)}</td>
                <td className="px-3 py-2">
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(row.source_breakdown ?? {}).slice(0, 4).map(([source, count]) => (
                      <span
                        key={source}
                        className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800/70 text-gray-400"
                      >
                        {source}·{count}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedId && (
        <ClusterDrawer
          detail={detailQ.data ?? null}
          isLoading={detailQ.isLoading}
          error={detailQ.error as Error | null}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  )
}

function ClusterDrawer({
  detail,
  isLoading,
  error,
  onClose,
}: {
  detail: ClusterDetail | null
  isLoading: boolean
  error: Error | null
  onClose: () => void
}) {
  const evidenceCount = detail
    ? (detail.spider_data_ids?.length || 0) + (detail.trigger_event_ids?.length || 0)
    : 0

  // Session 3014 (U2): Create initiative modal state
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [createResult, setCreateResult] = useState<{
    initiativeId: string
    initiativeName: string
    deliverableId: string | null
    deliverableTitle: string | null
    deliverableError?: string
  } | null>(null)

  return (
    <div
      role="dialog"
      className="fixed inset-y-0 right-0 z-40 w-full max-w-2xl bg-gray-950 border-l border-gray-800 shadow-2xl overflow-y-auto"
    >
      <div className="sticky top-0 z-10 flex items-center justify-between p-3 border-b border-gray-800 bg-gray-950">
        <h3 className="text-sm font-semibold text-gray-100">Cluster detail</h3>
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
        {error && <div className="text-red-400">{error.message}</div>}
        {detail && (
          <>
            <div>
              <div className="text-[10px] uppercase tracking-wide text-gray-500">Cluster</div>
              <div className="text-gray-100 mt-1 text-base">{detail.name}</div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Metric label="Confidence" value={formatConfidence(detail.confidence)} />
              <Metric label="Strength" value={formatConfidence(detail.strength)} />
              <Metric label="Novelty" value={formatConfidence(detail.novelty)} />
              <Metric label="Urgency" value={formatConfidence(detail.urgency)} />
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs text-gray-400">
              <div>
                <div className="text-[10px] uppercase text-gray-500">Pattern</div>
                <div className="mt-0.5 text-gray-200 capitalize">{detail.pattern_type.replace(/_/g, ' ')}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase text-gray-500">Status</div>
                <div className="mt-0.5 text-gray-200 capitalize">{detail.status}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase text-gray-500">Detected</div>
                <div className="mt-0.5 text-gray-200">{formatMST(detail.detected_at)}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase text-gray-500">Signal window</div>
                <div className="mt-0.5 text-gray-200">
                  {formatMST(detail.signal_window_start)} → {formatMST(detail.signal_window_end)}
                </div>
              </div>
            </div>

            {detail.keywords && detail.keywords.length > 0 && (
              <div>
                <div className="text-[10px] uppercase tracking-wide text-gray-500 mb-1">Keywords</div>
                <div className="flex flex-wrap gap-1">
                  {detail.keywords.map(kw => (
                    <span key={kw} className="text-xs px-2 py-0.5 rounded bg-primary-500/10 text-primary-300 border border-primary-500/20">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div>
              <div className="text-[10px] uppercase tracking-wide text-gray-500 mb-1">Source breakdown</div>
              <div className="flex flex-wrap gap-1">
                {Object.entries(detail.source_breakdown ?? {}).map(([source, count]) => (
                  <span key={source} className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                    {source} · {count}
                  </span>
                ))}
              </div>
            </div>

            {detail.sample_signals && detail.sample_signals.length > 0 && (
              <div>
                <div className="text-[10px] uppercase tracking-wide text-gray-500 mb-1">
                  Sample signals ({detail.sample_signals.length})
                </div>
                <div className="space-y-2">
                  {detail.sample_signals.slice(0, 5).map((s, i) => (
                    <div key={i} className="p-2 rounded bg-gray-900/60 border border-gray-800 text-xs">
                      {s.source && <div className="text-[10px] text-gray-500 uppercase">{s.source}</div>}
                      <div className="text-gray-300 mt-0.5">{s.text || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {evidenceCount > 0 ? (
              <div className="text-xs text-gray-500">
                Evidence: {detail.spider_data_ids?.length ?? 0} spider rows · {detail.trigger_event_ids?.length ?? 0} trigger events
              </div>
            ) : (
              <div className="text-xs text-gray-600 italic">
                Evidence linkage not available in v1.
              </div>
            )}

            {/* Session 3014 (U2): Create initiative bridge */}
            <div className="pt-3 border-t border-gray-800">
              {createResult ? (
                <div className="rounded-lg border border-accent-green/30 bg-accent-green/5 p-3 space-y-2">
                  <div className="flex items-center gap-2 text-accent-green text-sm">
                    <CheckCircle2 size={14} />
                    <span className="font-medium">Initiative created</span>
                  </div>
                  <div className="text-xs text-gray-300">{createResult.initiativeName}</div>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <a
                      href={`/workspace?tab=initiatives&id=${createResult.initiativeId}`}
                      className="px-2 py-1 rounded bg-primary-500/20 text-primary-300 hover:bg-primary-500/30"
                    >
                      Open initiative
                    </a>
                    {createResult.deliverableId && (
                      <a
                        href={`/workspace?tab=deliverables&id=${createResult.deliverableId}`}
                        className="px-2 py-1 rounded bg-primary-500/20 text-primary-300 hover:bg-primary-500/30"
                      >
                        View brief
                      </a>
                    )}
                    {createResult.deliverableError && (
                      <span className="flex items-center gap-1 text-accent-amber">
                        <AlertTriangle size={12} />
                        Brief skipped: {createResult.deliverableError}
                      </span>
                    )}
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setCreateModalOpen(true)}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm bg-primary-500/20 text-primary-300 hover:bg-primary-500/30 transition-colors"
                >
                  <Rocket size={14} />
                  Create initiative from this cluster
                </button>
              )}
            </div>
          </>
        )}
      </div>

      {createModalOpen && detail && (
        <CreateInitiativeModal
          cluster={detail}
          onClose={() => setCreateModalOpen(false)}
          onCreated={(res) => {
            setCreateResult(res)
            setCreateModalOpen(false)
          }}
        />
      )}
    </div>
  )
}

// Session 3014 (U2): Confirm-and-submit modal for signal-cluster → initiative bridge
function CreateInitiativeModal({
  cluster,
  onClose,
  onCreated,
}: {
  cluster: ClusterDetail
  onClose: () => void
  onCreated: (result: {
    initiativeId: string
    initiativeName: string
    deliverableId: string | null
    deliverableTitle: string | null
    deliverableError?: string
  }) => void
}) {
  const queryClient = useQueryClient()
  const defaultName = `${cluster.pattern_type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}: ${cluster.name}`.slice(0, 200)
  const [name, setName] = useState(defaultName)
  const [generateBrief, setGenerateBrief] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () =>
      signalsApi.createInitiativeFromCluster(cluster.id, {
        name: name.trim() && name.trim() !== defaultName ? name.trim() : undefined,
        generate_brief: generateBrief,
      }),
    onSuccess: (resp) => {
      const body = resp.data
      if (!body.success || !body.initiative) {
        setErrorMsg(body.error || 'Initiative creation failed')
        return
      }
      queryClient.invalidateQueries({ queryKey: ['initiatives'] })
      onCreated({
        initiativeId: body.initiative.id,
        initiativeName: body.initiative.name,
        deliverableId: body.deliverable?.id ?? null,
        deliverableTitle: body.deliverable?.title ?? null,
        deliverableError: body.deliverable_error,
      })
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || err?.message || 'Request failed'
      setErrorMsg(msg)
    },
  })

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={onClose}
    >
      <div
        className="max-w-md w-full mx-4 p-5 bg-gray-950 border border-primary-500/30 rounded-lg shadow-2xl space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2">
          <Rocket className="text-primary-400" size={18} />
          <h3 className="text-base font-semibold text-gray-100">Create initiative from cluster</h3>
        </div>

        <div className="space-y-3 text-sm">
          <div>
            <label className="block text-xs uppercase tracking-wide text-gray-500 mb-1">Initiative name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={200}
              className="w-full px-3 py-2 rounded bg-gray-900 border border-gray-800 text-sm text-white focus:border-primary-500 focus:outline-none"
            />
            <div className="text-[10px] text-gray-500 mt-1">{name.length}/200 characters</div>
          </div>

          <label className="flex items-center gap-2 text-sm text-gray-300">
            <input
              type="checkbox"
              checked={generateBrief}
              onChange={(e) => setGenerateBrief(e.target.checked)}
              className="accent-primary-500"
            />
            Generate Signal Brief deliverable
          </label>

          {errorMsg && (
            <div className="flex items-start gap-2 p-2 rounded bg-accent-red/10 text-accent-red text-xs">
              <AlertTriangle size={12} className="mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-800">
          <button
            onClick={onClose}
            disabled={mutation.isPending}
            className="px-3 py-1.5 text-sm rounded-md bg-gray-800 hover:bg-gray-700 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !name.trim()}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md bg-primary-500/20 text-primary-300 hover:bg-primary-500/30 disabled:opacity-50"
          >
            {mutation.isPending ? (
              <>
                <Loader2 size={14} className="animate-spin" /> Creating…
              </>
            ) : (
              <>
                <Rocket size={14} /> Create
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-gray-800 bg-gray-900/40 p-2">
      <div className="text-[10px] uppercase text-gray-500">{label}</div>
      <div className="text-primary-400 font-semibold text-lg mt-0.5">{value}</div>
    </div>
  )
}
