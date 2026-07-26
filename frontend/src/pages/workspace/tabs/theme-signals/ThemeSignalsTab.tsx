/**
 * Session 2978: Theme Signals v1 — Workspace sub-tab under Intelligence.
 * Session 2980: Build-only toggle on Buildable + Action chip on cards
 * (spec f3cc9499). Server-side ?build_only=true filter so the visible
 * count is up to `limit` build-classed cards rather than
 * `limit` buildable-then-filtered-to-few.
 *
 * Deliverable 63ec4d1d-9425-468b-815c-b4e571e3fe44 (v1). Combined feed
 * with two sub-tabs (Buildable default / Investable). Strict quality gate.
 * Ships with 7-day default window. Reachable at
 *   /workspace?tab=intelligence&sub=theme-signals
 *
 * Backend: GET /api/theme-signals/?tab={buildable|investable}&days=7&limit=20[&build_only=true]
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Sparkles, TrendingUp, ChevronDown, ChevronUp, Loader2, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/cn'
import { signalsApi } from '@/lib/api'
import { ThemeSignalCard, type ThemeSignalCardData } from '@/components/theme-signals/ThemeSignalCard'

export type ThemeSignalsTabKey = 'buildable' | 'investable'

interface GateReasons {
  title_blocked: number
  evidence_fail: number
  conf_fail: number
  routed_other_tab: number
  build_only_filtered?: number
}

interface ThemeSignalsPayload {
  tab: ThemeSignalsTabKey
  days: number
  limit: number
  build_only?: boolean
  min_confidence_applied: number
  cards: ThemeSignalCardData[]
  total_scanned: number
  total_survived: number
  gate_reasons: GateReasons
}

const SUB_TABS: Array<{ id: ThemeSignalsTabKey; label: string; icon: typeof Sparkles }> = [
  { id: 'buildable', label: 'Buildable', icon: Sparkles },
  { id: 'investable', label: 'Investable', icon: TrendingUp },
]

const WINDOW_DAYS = 7

export function ThemeSignalsTab() {
  const [activeTab, setActiveTab] = useState<ThemeSignalsTabKey>('buildable')
  const [buildOnly, setBuildOnly] = useState<boolean>(false)
  const [debugOpen, setDebugOpen] = useState(false)

  // Build-only is only meaningful on the Buildable tab; Investable is
  // dominated by watch/research so the toggle would filter to ~0 cards.
  const effectiveBuildOnly = activeTab === 'buildable' && buildOnly

  const query = useQuery({
    queryKey: ['theme-signals', activeTab, WINDOW_DAYS, effectiveBuildOnly],
    queryFn: async () => {
      const resp = await signalsApi.themeSignals({
        tab: activeTab,
        days: WINDOW_DAYS,
        limit: 20,
        build_only: effectiveBuildOnly || undefined,
      })
      return resp.data as ThemeSignalsPayload
    },
    staleTime: 60_000,
  })

  const payload = query.data
  const cards = payload?.cards ?? []
  const isLoading = query.isLoading
  const isRefreshing = query.isFetching && !query.isLoading

  return (
    <div className="space-y-4">
      {/* Header — sub-tab switcher */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex gap-2 overflow-x-auto">
            {SUB_TABS.map(tab => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
                    isActive
                      ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                      : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
                  )}
                >
                  <Icon size={14} />
                  {tab.label}
                </button>
              )
            })}
          </div>
          {activeTab === 'buildable' && (
            <div
              className="flex items-center gap-0 rounded-lg border border-gray-800 bg-gray-900/40 overflow-hidden"
              role="group"
              aria-label="Build-only filter"
            >
              <button
                type="button"
                onClick={() => setBuildOnly(false)}
                className={cn(
                  'px-3 py-1.5 text-xs whitespace-nowrap transition-colors',
                  !buildOnly
                    ? 'bg-primary-500/20 text-primary-300'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
                )}
                aria-pressed={!buildOnly}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => setBuildOnly(true)}
                className={cn(
                  'px-3 py-1.5 text-xs whitespace-nowrap border-l border-gray-800 transition-colors',
                  buildOnly
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
                )}
                aria-pressed={buildOnly}
                title="Show only cards whose action is Build"
              >
                Build-only
              </button>
            </div>
          )}
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>Last {WINDOW_DAYS} days · strict quality gate</span>
          <button
            onClick={() => query.refetch()}
            disabled={query.isFetching}
            className="flex items-center gap-1.5 px-2 py-1 rounded-md border border-gray-800 hover:border-gray-700 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw size={12} className={cn(isRefreshing && 'animate-spin')} />
          </button>
        </div>
      </div>

      {/* Card list */}
      {isLoading && (
        <div className="flex items-center justify-center py-16 text-gray-500">
          <Loader2 size={20} className="animate-spin mr-2" />
          Loading {activeTab} signals…
        </div>
      )}

      {!isLoading && cards.length === 0 && (
        <div className="rounded-lg border border-gray-800 bg-gray-900/40 p-8 text-center text-sm text-gray-400">
          <div className="mb-2 font-medium text-gray-300">
            {effectiveBuildOnly
              ? `No Build-classed ${activeTab} signals in the last ${WINDOW_DAYS} days.`
              : `No ${activeTab} signals passed the strict quality gate.`}
          </div>
          <div className="text-xs text-gray-500">
            {effectiveBuildOnly ? (
              <>
                Scanned {payload?.total_scanned ?? 0} clusters; try switching to <button
                  onClick={() => setBuildOnly(false)}
                  className="underline text-gray-400 hover:text-white"
                >All</button> to see Research and Watch cards too.
              </>
            ) : (
              <>
                Scanned {payload?.total_scanned ?? 0} clusters over the last {WINDOW_DAYS} days.
                Try again in 24h once more clusters accumulate.
              </>
            )}
          </div>
        </div>
      )}

      {!isLoading && cards.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {cards.map(card => (
            <ThemeSignalCard key={card.id} card={card} tab={activeTab} />
          ))}
        </div>
      )}

      {/* Gate-reasons debug panel — collapsed by default */}
      {payload && (
        <div className="mt-6 rounded-lg border border-gray-800/60 bg-gray-900/30">
          <button
            onClick={() => setDebugOpen(v => !v)}
            className="w-full flex items-center justify-between px-4 py-2 text-xs text-gray-400 hover:text-gray-200"
          >
            <span>
              Gate stats · scanned {payload.total_scanned} · shown {payload.total_survived} ·
              confidence ≥ {payload.min_confidence_applied.toFixed(2)}
            </span>
            {debugOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {debugOpen && (
            <div className="px-4 pb-3 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <GateStat label="Title blocked" value={payload.gate_reasons.title_blocked} />
              <GateStat label="Evidence fail" value={payload.gate_reasons.evidence_fail} />
              <GateStat label="Confidence fail" value={payload.gate_reasons.conf_fail} />
              <GateStat label="Routed other tab" value={payload.gate_reasons.routed_other_tab} />
              {effectiveBuildOnly && (
                <GateStat
                  label="Build-only filtered"
                  value={payload.gate_reasons.build_only_filtered ?? 0}
                />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function GateStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded border border-gray-800 bg-gray-900/40 px-3 py-2">
      <div className="text-gray-500 text-[10px] uppercase tracking-wide">{label}</div>
      <div className="text-gray-200 font-mono">{value}</div>
    </div>
  )
}
