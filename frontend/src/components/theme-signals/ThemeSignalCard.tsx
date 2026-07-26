/**
 * Session 2978: Theme Signal card — 5-point contract per spec 63ec4d1d.
 * Session 2979: Evidence-first UX per spec c4602ccd — top-3 default with
 * View all expand, empty-state row, null-url safe rendering.
 * Session 2980: Canonical `action` enum (build/research/watch) per spec
 * f3cc9499 — replaces the prior 5-value `so_what` field; chip and
 * Build-only filter both read from the same field.
 *
 * Renders one SignalCluster shaped as a "theme signal":
 *   1. Title + Action chip (Build / Research / Watch)
 *   2. Why now (Phase A derived template + Phase B tooltip)
 *   3. Evidence (top 3 default; expandable to all; empty state if 0)
 *   4. Confidence + drivers
 * Investable variant adds:
 *   5. Who benefits / who loses (Coming in Phase B placeholder)
 */

import { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/cn'

const DEFAULT_EVIDENCE_VISIBLE = 3

export type ThemeSignalAction = 'build' | 'research' | 'watch'

export interface ThemeSignalEvidence {
  title: string
  // Backend sanitizes to http(s); items that couldn't be sanitized come
  // through with url=null and render as unclickable snippets.
  url: string | null
  source: string
  published?: string | null
}

export interface ThemeSignalCardData {
  id: string
  title: string
  why_now: string
  why_now_note: string
  evidence: ThemeSignalEvidence[]
  action: ThemeSignalAction
  confidence: number
  confidence_drivers: string
  pattern_type: string
  detected_at: string | null
  who_benefits_who_loses?: {
    status: 'coming_in_phase_b'
    message: string
  }
}

const ACTION_STYLE: Record<ThemeSignalAction, string> = {
  build: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  research: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  watch: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
}

function confidenceColor(confidence: number): string {
  if (confidence >= 0.9) return 'text-emerald-400'
  if (confidence >= 0.75) return 'text-blue-400'
  if (confidence >= 0.6) return 'text-amber-400'
  return 'text-gray-400'
}

export function ThemeSignalCard({
  card,
  tab,
}: {
  card: ThemeSignalCardData
  tab: 'buildable' | 'investable'
}) {
  const actionCls = ACTION_STYLE[card.action] ?? ACTION_STYLE.watch
  const [showAll, setShowAll] = useState(false)
  const evidence = card.evidence
  const hiddenCount = Math.max(0, evidence.length - DEFAULT_EVIDENCE_VISIBLE)
  const visible = showAll ? evidence : evidence.slice(0, DEFAULT_EVIDENCE_VISIBLE)

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-gray-800 bg-gray-900/40 p-4 hover:border-gray-700 transition-colors">
      {/* 1 — Title + Action chip (Build / Research / Watch) */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-gray-100 leading-snug break-words min-w-0 flex-1">
          {card.title}
        </h3>
        <span
          className={cn(
            'shrink-0 px-2 py-0.5 text-[10px] uppercase tracking-wide rounded border',
            actionCls,
          )}
        >
          {card.action}
        </span>
      </div>

      {/* 2 — Why now */}
      <div>
        <div className="text-xs text-gray-300 leading-relaxed">{card.why_now}</div>
        <div
          className="mt-1 text-[10px] text-gray-600 italic"
          title="Phase A ships a deterministic template. Phase B replaces the generator with LLM summarization."
        >
          {card.why_now_note}
        </div>
      </div>

      {/* 3 — Evidence */}
      <div className="space-y-1">
        <div className="text-[10px] uppercase tracking-wide text-gray-500">
          Evidence{evidence.length > 0 && ` (top ${Math.min(evidence.length, DEFAULT_EVIDENCE_VISIBLE)})`}
        </div>
        {evidence.length === 0 ? (
          <div className="text-xs text-gray-600 italic">
            No evidence items available yet.
          </div>
        ) : (
          <>
            <ul className="space-y-1">
              {visible.map((item, i) => (
                <li key={`${card.id}-ev-${i}`} className="text-xs">
                  {item.url ? (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group flex items-start gap-1.5 text-gray-300 hover:text-blue-300 min-w-0"
                    >
                      <ExternalLink size={11} className="mt-0.5 shrink-0 opacity-60 group-hover:opacity-100" />
                      <span className="line-clamp-2 break-words min-w-0">{item.title}</span>
                    </a>
                  ) : (
                    <div className="flex items-start gap-1.5 text-gray-400 min-w-0">
                      <span className="mt-0.5 shrink-0 opacity-40 w-[11px] text-center">·</span>
                      <span className="line-clamp-2 break-words min-w-0">{item.title}</span>
                    </div>
                  )}
                  <div className="ml-4 text-[10px] text-gray-500 truncate">{item.source}</div>
                </li>
              ))}
            </ul>
            {hiddenCount > 0 && (
              <button
                type="button"
                onClick={() => setShowAll(v => !v)}
                className="mt-1 flex items-center gap-1 text-[10px] text-gray-500 hover:text-gray-300"
              >
                {showAll ? (
                  <>
                    <ChevronUp size={11} />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDown size={11} />
                    View all {evidence.length}
                  </>
                )}
              </button>
            )}
          </>
        )}
      </div>

      {/* 5 — Confidence + drivers */}
      <div className="flex flex-wrap items-baseline justify-between gap-2 pt-2 border-t border-gray-800/60">
        <div className="text-[10px] text-gray-500">
          confidence <span className={cn('font-mono text-xs ml-1', confidenceColor(card.confidence))}>
            {card.confidence.toFixed(2)}
          </span>
        </div>
        <div className="text-[10px] text-gray-500 truncate max-w-[70%]" title={card.confidence_drivers}>
          {card.confidence_drivers}
        </div>
      </div>

      {/* 6 (Investable only) — Who benefits / who loses */}
      {tab === 'investable' && card.who_benefits_who_loses && (
        <div className="mt-1 rounded border border-dashed border-gray-700 bg-gray-900/60 px-3 py-2 text-[10px]">
          <div className="text-gray-400 uppercase tracking-wide">Who benefits / who loses</div>
          <div className="text-gray-500 italic mt-0.5">{card.who_benefits_who_loses.message}</div>
        </div>
      )}
    </div>
  )
}
