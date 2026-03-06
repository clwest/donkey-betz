import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { RunSummary, ImportanceLevel, TriggerType, NextActionType } from '@/types/cockpit'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { RUN_STATUS_LABEL, RUN_STATUS_TONE } from '@/components/cockpit/runs/runStatus'
import { formatRelative, formatDateTime } from '@/lib/time'
import {
  Play,
  Clock,
  User,
  GitBranch,
  Zap,
  RotateCcw,
  HelpCircle,
  AlertCircle,
  ArrowUpRight,
  Info,
  Minus,
  AlertTriangle,
  Eye,
  ChevronDown,
  ChevronUp,
  ShieldAlert,
  Settings,
  Timer,
  Image,
} from 'lucide-react'

// ── Badge configs ──────────────────────────────────────────────────────────

const IMPORTANCE_CONFIG: Record<ImportanceLevel, { label: string; tone: string; Icon: typeof AlertCircle }> = {
  action_required: { label: 'Action', tone: 'bg-red-500/20 text-red-400', Icon: AlertCircle },
  high_impact: { label: 'Impact', tone: 'bg-amber-500/20 text-amber-400', Icon: ArrowUpRight },
  fyi: { label: 'FYI', tone: 'bg-blue-500/20 text-blue-400', Icon: Info },
  routine: { label: 'Routine', tone: 'bg-gray-500/20 text-gray-500', Icon: Minus },
}

const TRIGGER_ICON: Record<TriggerType, typeof Clock> = {
  scheduled: Clock,
  manual: User,
  workflow: GitBranch,
  autopilot: Zap,
  retry: RotateCcw,
  unknown: HelpCircle,
}

const CTA_CONFIG: Partial<Record<NextActionType, { label: string; Icon: typeof Eye; tone: string }>> = {
  investigate_failure: { label: 'Investigate', Icon: AlertTriangle, tone: 'bg-red-500/20 text-red-400 hover:bg-red-500/30' },
  retry_timeout: { label: 'Retry', Icon: RotateCcw, tone: 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30' },
  fix_config: { label: 'Fix configuration', Icon: Settings, tone: 'bg-red-500/20 text-red-400 hover:bg-red-500/30' },
  rate_limited: { label: 'View rate limit', Icon: Timer, tone: 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/30' },
  review_deliverable: { label: 'Review deliverable', Icon: Eye, tone: 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30' },
  approve_content: { label: 'Review content', Icon: Eye, tone: 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30' },
  preview_media: { label: 'Preview media', Icon: Image, tone: 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30' },
  view_artifacts: { label: 'View output', Icon: Eye, tone: 'bg-dark-border/50 text-gray-400 hover:text-gray-200' },
}

const SECTION_ICON: Record<string, typeof AlertCircle> = {
  attention: ShieldAlert,
  review: Eye,
  routine: Minus,
}

const SECTION_ICON_TONE: Record<string, string> = {
  attention: 'text-red-400',
  review: 'text-primary-400',
  routine: 'text-gray-500',
}

// ── Display title ──────────────────────────────────────────────────────────

function displayTitle(run: RunSummary): string {
  const summary = run.enrichment?.summary
  if (summary && summary.length <= 80) return summary
  if (summary) return summary.slice(0, 77) + '...'

  const task = run.task || ''
  if (task.length <= 80) return task
  return task.slice(0, 77) + '...'
}

function fullTitle(run: RunSummary): string {
  return run.enrichment?.summary || run.task || ''
}

// ── Component ──────────────────────────────────────────────────────────────

export type SectionType = 'attention' | 'review' | 'routine'

interface TodayRunsCardProps {
  runs: RunSummary[]
  isLoading?: boolean
  title?: string
  emptyMessage?: string
  compact?: boolean
  maxRows?: number
  section?: SectionType
}

export default function TodayRunsCard({
  runs,
  isLoading,
  title = 'Recent Runs',
  emptyMessage = 'No runs yet',
  compact = false,
  maxRows = 5,
  section = 'routine',
}: TodayRunsCardProps) {
  const navigate = useNavigate()

  const rows = runs.slice(0, maxRows)

  const content = isLoading ? (
    <SkeletonRows count={5} />
  ) : rows.length === 0 ? (
    <p className="text-sm text-gray-500 text-center py-6">{emptyMessage}</p>
  ) : (
    <ul className="space-y-1">
      {rows.map((run) => (
        <RunRow key={run.id} run={run} navigate={navigate} section={section} />
      ))}
    </ul>
  )

  if (compact) {
    return <div className="px-4 pb-3">{content}</div>
  }

  const SectionIcon = SECTION_ICON[section] || Play
  const iconTone = SECTION_ICON_TONE[section] || 'text-primary-400'

  return (
    <div className="card flex flex-col">
      <div className="flex items-center justify-between border-b border-dark-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
          <SectionIcon size={16} className={iconTone} />
          {title}
          {runs.length > 0 && (
            <span className="text-xs font-normal text-gray-500">({runs.length})</span>
          )}
        </div>
        <button
          onClick={() => navigate('/cockpit/runs')}
          className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
        >
          View all
        </button>
      </div>
      <div className="flex-1 p-4">{content}</div>
    </div>
  )
}

// ── Run row ────────────────────────────────────────────────────────────────

function RunRow({
  run,
  navigate,
  section,
}: {
  run: RunSummary
  navigate: ReturnType<typeof useNavigate>
  section: SectionType
}) {
  const [expanded, setExpanded] = useState(false)
  const enrichment = run.enrichment
  const importance = enrichment?.importance
  const trigger = enrichment?.trigger
  const nextAction = enrichment?.next_action

  const impConfig = importance
    ? IMPORTANCE_CONFIG[importance.level]
    : IMPORTANCE_CONFIG.routine

  const TriggerIcon = trigger ? TRIGGER_ICON[trigger.type] ?? HelpCircle : Clock

  const title = displayTitle(run)
  const full = fullTitle(run)
  const isTruncated = full.length > 80

  const ctaConfig = nextAction?.type ? CTA_CONFIG[nextAction.type] : undefined

  return (
    <li
      className="group rounded-lg px-3 py-2.5 hover:bg-dark-border/30 cursor-pointer transition-colors"
      onClick={() => navigate(`/cockpit/runs/${run.id}`)}
    >
      {/* Top line: title + badges */}
      <div className="flex items-start gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-200 leading-snug">
            {title}
          </p>
          {/* Expandable full title */}
          {isTruncated && expanded && (
            <p className="text-xs text-gray-400 mt-1 whitespace-pre-wrap">{full}</p>
          )}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {/* Expand toggle for truncated titles */}
          {isTruncated && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                setExpanded(!expanded)
              }}
              className="text-gray-600 hover:text-gray-400 transition-colors"
              title={expanded ? 'Collapse' : 'Show full details'}
            >
              {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            </button>
          )}
          {/* Importance badge (skip in routine section) */}
          {section !== 'routine' && (
            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${impConfig.tone}`}>
              <impConfig.Icon size={11} />
              {impConfig.label}
            </span>
          )}
          <StatusPill
            label={RUN_STATUS_LABEL[run.status]}
            tone={RUN_STATUS_TONE[run.status]}
          />
        </div>
      </div>

      {/* Bottom line: trigger + agent + time + CTA */}
      <div className="flex items-center gap-3 mt-1.5">
        {trigger && (
          <span className="inline-flex items-center gap-1 text-[11px] text-gray-500" title={trigger.label}>
            <TriggerIcon size={11} />
            {trigger.label}
          </span>
        )}

        <span className="text-[11px] text-gray-600">{run.agent_name}</span>

        <span className="text-[11px] text-gray-600 ml-auto" title={run.created_at ? formatDateTime(run.created_at) : ''}>
          {run.created_at ? formatRelative(run.created_at) : ''}
        </span>

        {/* CTA button — specific to action type */}
        {ctaConfig && nextAction && nextAction.type !== 'no_action' && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              navigate(nextAction.href || `/cockpit/runs/${run.id}`)
            }}
            className={`inline-flex items-center gap-1 text-[11px] font-medium rounded px-2 py-0.5 transition-colors ${ctaConfig.tone}`}
          >
            <ctaConfig.Icon size={11} />
            {ctaConfig.label}
          </button>
        )}
      </div>

      {/* Artifact pills */}
      {enrichment?.artifacts && <ArtifactPills artifacts={enrichment.artifacts} />}
    </li>
  )
}

// ── Artifact pills ─────────────────────────────────────────────────────────

function ArtifactPills({ artifacts }: { artifacts: NonNullable<RunSummary['enrichment']>['artifacts'] }) {
  const pills: { label: string; count: number }[] = []
  if (artifacts.deliverables.length) pills.push({ label: 'Deliverable', count: artifacts.deliverables.length })
  if (artifacts.blogs.length) pills.push({ label: 'Blog', count: artifacts.blogs.length })
  if (artifacts.media.length) pills.push({ label: 'Media', count: artifacts.media.length })
  if (artifacts.wagers.length) pills.push({ label: 'Wager', count: artifacts.wagers.length })
  if (artifacts.initiatives.length) pills.push({ label: 'Initiative', count: artifacts.initiatives.length })

  if (pills.length === 0) return null

  return (
    <div className="flex items-center gap-1.5 mt-1.5">
      {pills.map((p) => (
        <span
          key={p.label}
          className="inline-flex items-center gap-1 rounded bg-dark-border/40 px-1.5 py-0.5 text-[10px] text-gray-400"
        >
          {p.count > 1 ? `${p.count} ${p.label}s` : p.label}
        </span>
      ))}
    </div>
  )
}
