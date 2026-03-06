import { useNavigate } from 'react-router-dom'
import type { RunSummary, ImportanceLevel, TriggerType } from '@/types/cockpit'
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

// ── Component ──────────────────────────────────────────────────────────────

interface TodayRunsCardProps {
  runs: RunSummary[]
  isLoading?: boolean
  title?: string
  emptyMessage?: string
  compact?: boolean
  maxRows?: number
}

export default function TodayRunsCard({
  runs,
  isLoading,
  title = 'Recent Runs',
  emptyMessage = 'No runs yet',
  compact = false,
  maxRows = 5,
}: TodayRunsCardProps) {
  const navigate = useNavigate()

  // Compact mode: no header/wrapper (used inside collapsible)
  const rows = runs.slice(0, maxRows)

  const content = isLoading ? (
    <SkeletonRows count={5} />
  ) : rows.length === 0 ? (
    <p className="text-sm text-gray-500 text-center py-6">{emptyMessage}</p>
  ) : (
    <ul className="space-y-1">
      {rows.map((run) => (
        <RunRow key={run.id} run={run} navigate={navigate} />
      ))}
    </ul>
  )

  if (compact) {
    return <div className="px-4 pb-3">{content}</div>
  }

  return (
    <div className="card flex flex-col">
      <div className="flex items-center justify-between border-b border-dark-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
          <Play size={16} className="text-primary-400" />
          {title}
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

function RunRow({ run, navigate }: { run: RunSummary; navigate: ReturnType<typeof useNavigate> }) {
  const enrichment = run.enrichment
  const importance = enrichment?.importance
  const trigger = enrichment?.trigger
  const nextAction = enrichment?.next_action
  const summary = enrichment?.summary

  const impConfig = importance
    ? IMPORTANCE_CONFIG[importance.level]
    : IMPORTANCE_CONFIG.routine

  const TriggerIcon = trigger ? TRIGGER_ICON[trigger.type] ?? HelpCircle : Clock

  return (
    <li
      className="group rounded-lg px-3 py-2.5 hover:bg-dark-border/30 cursor-pointer transition-colors"
      onClick={() => navigate(`/cockpit/runs/${run.id}`)}
    >
      {/* Top line: summary + badges */}
      <div className="flex items-start gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-200 leading-snug">
            {summary || run.task}
          </p>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {/* Importance badge */}
          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${impConfig.tone}`}>
            <impConfig.Icon size={11} />
            {impConfig.label}
          </span>
          <StatusPill
            label={RUN_STATUS_LABEL[run.status]}
            tone={RUN_STATUS_TONE[run.status]}
          />
        </div>
      </div>

      {/* Bottom line: trigger + agent + time + CTA */}
      <div className="flex items-center gap-3 mt-1.5">
        {/* Trigger */}
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

        {/* CTA button */}
        {nextAction && nextAction.type !== 'no_action' && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              navigate(nextAction.href || `/cockpit/runs/${run.id}`)
            }}
            className={`text-[11px] font-medium rounded px-2 py-0.5 transition-colors ${
              nextAction.priority === 'primary'
                ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30'
                : 'bg-dark-border/50 text-gray-400 hover:text-gray-200'
            }`}
          >
            {nextAction.label}
          </button>
        )}
      </div>

      {/* Artifact pills */}
      {enrichment?.artifacts && <ArtifactPills artifacts={enrichment.artifacts} />}
    </li>
  )
}

// ── Artifact pills ─────────────────────────────────────────────────────────

function ArtifactPills({ artifacts }: { artifacts: RunSummary['enrichment'] extends undefined ? never : NonNullable<RunSummary['enrichment']>['artifacts'] }) {
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
