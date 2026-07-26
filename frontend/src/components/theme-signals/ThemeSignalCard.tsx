/**
 * Session 2978: Theme Signal card — 5-point contract per spec 63ec4d1d.
 *
 * Renders one SignalCluster shaped as a "theme signal":
 *   1. Title (blocked-title-filtered upstream)
 *   2. Why now (Phase A derived template + Phase B tooltip)
 *   3. Evidence (3-7 links)
 *   4. So what (suggested action)
 *   5. Confidence + drivers
 * Investable variant adds:
 *   6. Who benefits / who loses (Coming in Phase B placeholder)
 */

import { ExternalLink } from 'lucide-react'
import { cn } from '@/lib/cn'

export interface ThemeSignalEvidence {
  title: string
  url: string
  source: string
  published?: string | null
}

export interface ThemeSignalCardData {
  id: string
  title: string
  why_now: string
  why_now_note: string
  evidence: ThemeSignalEvidence[]
  so_what: string
  confidence: number
  confidence_drivers: string
  pattern_type: string
  detected_at: string | null
  who_benefits_who_loses?: {
    status: 'coming_in_phase_b'
    message: string
  }
}

const SO_WHAT_STYLE: Record<string, string> = {
  'watch': 'bg-slate-500/20 text-slate-300 border-slate-500/30',
  'research': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  'build': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  'trade': 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  'build/trade': 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30',
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
  const soWhatCls = SO_WHAT_STYLE[card.so_what] ?? SO_WHAT_STYLE['watch']
  const evidence = card.evidence.slice(0, 7)

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-gray-800 bg-gray-900/40 p-4 hover:border-gray-700 transition-colors">
      {/* 1 — Title + so-what badge */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-gray-100 leading-snug break-words min-w-0 flex-1">
          {card.title}
        </h3>
        <span
          className={cn(
            'shrink-0 px-2 py-0.5 text-[10px] uppercase tracking-wide rounded border',
            soWhatCls,
          )}
        >
          {card.so_what}
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
      {evidence.length > 0 && (
        <div className="space-y-1">
          <div className="text-[10px] uppercase tracking-wide text-gray-500">Evidence</div>
          <ul className="space-y-1">
            {evidence.map((item, i) => (
              <li key={`${card.id}-ev-${i}`} className="text-xs">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-start gap-1.5 text-gray-300 hover:text-blue-300 min-w-0"
                >
                  <ExternalLink size={11} className="mt-0.5 shrink-0 opacity-60 group-hover:opacity-100" />
                  <span className="line-clamp-2 break-words min-w-0">{item.title}</span>
                </a>
                <div className="ml-4 text-[10px] text-gray-500 truncate">{item.source}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

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
