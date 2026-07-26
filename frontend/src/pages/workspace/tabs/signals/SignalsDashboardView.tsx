/**
 * S2971: Signals Dashboard view.
 *
 * Three widgets over the shared window (24h/7d/30d):
 *   1) Ingestion Summary — by_data_type + top spiders per type
 *   2) Coverage / Readiness — embedding_text presence buckets
 *   3) Cluster Output Summary — count + top recent clusters
 *
 * CTAs jump to Feed / Cluster views via the parent's setView.
 */

import { useQuery } from '@tanstack/react-query'
import { Rss, Radar, Database, TrendingUp, Loader2, AlertCircle } from 'lucide-react'
import { signalsApi } from '@/lib/api'
import { formatMST, formatNumber, formatConfidence } from './formatters'
import type { SignalsView, SignalsWindow } from './SignalsTab'

const DEFAULT_DATA_TYPES = ['news', 'financial', 'tech', 'ai_ml']

interface Props {
  windowHours: SignalsWindow
  windowDays: number
  onNavigate: (view: SignalsView) => void
}

interface AggregateBucket {
  data_type: string
  actionable_count: number
  total_count: number
  distinct_spiders: number
  top_spiders?: Array<{ spider_name: string; actionable_count: number; total_count: number }>
}

interface AggregateResponse {
  window: { days_back: number; start_ts: string; end_ts: string }
  filters: { data_types: string[] | null; actionable_only: boolean }
  by_data_type: AggregateBucket[]
  totals?: { total_count: number; actionable_count: number; distinct_data_types: number }
}

interface CoverageResponse {
  // S2972 accurate buckets (preferred).
  total: number
  present: number
  pending_eligible: number
  ineligible_empty: number
  embeddable_total: number
  embeddable_coverage_percent: number
  // Legacy fields (kept for backward compat with any older callers).
  total_entries: number
  with_embedding: number
  marked_empty: number
  pending: number
  searchable: number
  coverage_percent: number
  recent_24h: {
    // S2972 additions.
    total: number
    embedded: number
    marked_no_items: number
    still_pending: number
    no_items_rate: number
    // Legacy alias.
    with_embedding: number
  }
}

interface ClusterRow {
  id: string
  name: string
  pattern_type: string
  confidence: number
  signal_count: number
  detected_at: string
  source_breakdown: Record<string, number>
  keywords: string[]
}

export function SignalsDashboardView({ windowHours, windowDays, onNavigate }: Props) {
  const aggregateQ = useQuery({
    queryKey: ['signals-aggregate', windowDays],
    queryFn: async () => {
      const resp = await signalsApi.aggregate({
        days_back: windowDays,
        actionable_only: true,
        data_types: DEFAULT_DATA_TYPES,
        include_top_spiders: true,
      })
      return resp.data as AggregateResponse
    },
    staleTime: 60_000,
  })

  const coverageQ = useQuery({
    queryKey: ['signals-embedding-coverage'],
    queryFn: async () => {
      const resp = await signalsApi.embeddingCoverage()
      return resp.data as CoverageResponse
    },
    staleTime: 60_000,
  })

  const clustersQ = useQuery({
    queryKey: ['signals-cluster-summary', windowHours],
    queryFn: async () => {
      const resp = await signalsApi.clusters({
        window_hours: windowHours,
        page_size: 5,
      })
      // DRF paginated shape: { count, next, previous, results }
      const results = (resp.data?.results ?? []) as ClusterRow[]
      const count = (resp.data?.count ?? results.length) as number
      return { results, count }
    },
    staleTime: 60_000,
  })

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <IngestionSummaryCard query={aggregateQ} onGoToFeed={() => onNavigate('feed')} />
      <CoverageCard query={coverageQ} />
      <ClusterSummaryCard query={clustersQ} onGoToClusters={() => onNavigate('clusters')} />
    </div>
  )
}

// ─────────────────────────────────────────────────────────

function CardShell({
  title,
  icon: Icon,
  children,
  cta,
}: {
  title: string
  icon: typeof Rss
  children: React.ReactNode
  cta?: { label: string; onClick: () => void }
}) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-4 flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon size={16} className="text-primary-400" />
          <h3 className="text-sm font-semibold text-gray-100">{title}</h3>
        </div>
        {cta && (
          <button
            onClick={cta.onClick}
            className="text-xs text-primary-400 hover:text-primary-300"
          >
            {cta.label} →
          </button>
        )}
      </div>
      <div className="flex-1">{children}</div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex items-center gap-2 text-xs text-gray-500 py-4">
      <Loader2 size={14} className="animate-spin" /> Loading…
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 text-xs text-red-400 py-2">
      <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />
      <span>{message}</span>
    </div>
  )
}

// ─────────────────────────────────────────────────────────

function IngestionSummaryCard({
  query,
  onGoToFeed,
}: {
  query: ReturnType<typeof useQuery<AggregateResponse>>
  onGoToFeed: () => void
}) {
  const { data, isLoading, error } = query
  return (
    <CardShell
      title="Ingestion"
      icon={Rss}
      cta={{ label: 'View feed', onClick: onGoToFeed }}
    >
      {isLoading && <LoadingState />}
      {error && <ErrorState message={(error as Error).message || 'Failed to load'} />}
      {data && (
        <div className="space-y-3">
          {data.totals && (
            <div className="flex items-baseline gap-4 pb-2 border-b border-gray-800">
              <div>
                <div className="text-2xl font-bold text-primary-400">
                  {formatNumber(data.totals.actionable_count)}
                </div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wide">actionable</div>
              </div>
              <div>
                <div className="text-lg text-gray-300">{formatNumber(data.totals.total_count)}</div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wide">total rows</div>
              </div>
            </div>
          )}
          {data.by_data_type.length === 0 && (
            <div className="text-xs text-gray-500 py-2">No data in this window.</div>
          )}
          {data.by_data_type.map(bucket => (
            <div key={bucket.data_type} className="text-xs">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-200 capitalize">{bucket.data_type}</span>
                <span className="text-gray-400">
                  {formatNumber(bucket.actionable_count)}
                  <span className="text-gray-600"> / {formatNumber(bucket.total_count)}</span>
                </span>
              </div>
              {bucket.top_spiders && bucket.top_spiders.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {bucket.top_spiders.slice(0, 3).map(sp => (
                    <span
                      key={sp.spider_name}
                      className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800/70 text-gray-400"
                    >
                      {sp.spider_name} · {sp.actionable_count}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </CardShell>
  )
}

function CoverageCard({
  query,
}: {
  query: ReturnType<typeof useQuery<CoverageResponse>>
}) {
  const { data, isLoading, error } = query
  return (
    <CardShell title="Embedding coverage" icon={Database}>
      {isLoading && <LoadingState />}
      {error && <ErrorState message={(error as Error).message || 'Failed to load'} />}
      {data && (
        <div className="space-y-3">
          {/* S2972: primary number is embeddable-coverage (excludes [NO_ITEMS])
              — so a pipeline where every eligible row is embedded reads 100%,
              regardless of how many rollup/metric rows exist. Legacy percent is
              still shown below for cross-reference. */}
          <div>
            <div className="text-3xl font-bold text-primary-400">
              {data.embeddable_coverage_percent.toFixed(1)}%
            </div>
            <div
              className="text-[10px] text-gray-500 uppercase tracking-wide"
              title="Coverage of rows that carry embeddable content. Rollup/metric-only spider rows are excluded."
            >
              coverage (embeddable rows)
            </div>
            <div className="text-[10px] text-gray-500 mt-0.5">
              {formatNumber(data.present)} embedded / {formatNumber(data.embeddable_total)} embeddable · {formatNumber(data.total)} total rows
            </div>
          </div>

          <div className="h-2 bg-gray-800 rounded overflow-hidden">
            <div
              className="h-full bg-primary-500"
              style={{ width: `${Math.min(100, data.embeddable_coverage_percent)}%` }}
            />
          </div>

          <div className="grid grid-cols-3 gap-2 pt-1 text-center">
            <div>
              <div className="text-sm font-semibold text-emerald-400">
                {formatNumber(data.present)}
              </div>
              <div className="text-[10px] text-gray-500 uppercase">embedded</div>
            </div>
            <div>
              <div className="text-sm font-semibold text-yellow-400">
                {formatNumber(data.pending_eligible)}
              </div>
              <div
                className="text-[10px] text-gray-500 uppercase"
                title="Rows waiting for backfill. Backfill Beat runs every 15 min; queue usually drains within one cycle."
              >
                eligible queue
              </div>
            </div>
            <div>
              <div className="text-sm font-semibold text-gray-500">
                {formatNumber(data.ineligible_empty)}
              </div>
              <div
                className="text-[10px] text-gray-500 uppercase"
                title="Rows already visited by backfill and found to have no embeddable content — typically analytics rollups, weather/odds APIs, or extractor misses."
              >
                no items
              </div>
            </div>
          </div>

          {data.recent_24h && (
            <div className="pt-2 border-t border-gray-800 text-xs text-gray-400 space-y-1">
              <div className="flex items-center gap-1">
                <TrendingUp size={12} />
                <span>
                  Last 24h: {formatNumber(data.recent_24h.embedded)} embedded ·{' '}
                  {formatNumber(data.recent_24h.marked_no_items)} no-items ·{' '}
                  {formatNumber(data.recent_24h.still_pending)} queued
                </span>
              </div>
              {data.recent_24h.total > 0 && (
                <div className="text-[10px] text-gray-500">
                  {data.recent_24h.no_items_rate.toFixed(1)}% of new rows marked no-items · {formatNumber(data.recent_24h.total)} new rows total
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </CardShell>
  )
}

function ClusterSummaryCard({
  query,
  onGoToClusters,
}: {
  query: ReturnType<typeof useQuery<{ results: ClusterRow[]; count: number }>>
  onGoToClusters: () => void
}) {
  const { data, isLoading, error } = query
  return (
    <CardShell
      title="Signal clusters"
      icon={Radar}
      cta={{ label: 'View clusters', onClick: onGoToClusters }}
    >
      {isLoading && <LoadingState />}
      {error && <ErrorState message={(error as Error).message || 'Failed to load'} />}
      {data && (
        <div className="space-y-3">
          <div>
            <div className="text-2xl font-bold text-primary-400">{formatNumber(data.count)}</div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wide">clusters in window</div>
          </div>
          {data.results.length === 0 && (
            <div className="text-xs text-gray-500 py-2">No clusters detected in this window.</div>
          )}
          {data.results.map(c => (
            <div key={c.id} className="text-xs border-t border-gray-800/50 pt-2">
              <div className="flex items-start justify-between gap-2">
                <span className="text-gray-200 line-clamp-2 flex-1">{c.name}</span>
                <span className="text-primary-400 flex-shrink-0">
                  {formatConfidence(c.confidence)}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-2 text-[10px] text-gray-500">
                <span className="capitalize">{c.pattern_type.replace(/_/g, ' ')}</span>
                <span>·</span>
                <span>{c.signal_count} signals</span>
                <span>·</span>
                <span>{formatMST(c.detected_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </CardShell>
  )
}
