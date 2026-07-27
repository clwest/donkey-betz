/**
 * Session 2983 — Workspace Home Tab (Legibility Overhaul v1)
 *
 * Full redesign per ENGINEERING SPEC — Workspace Home v1 (deliverable
 * `5e1c702f-c09e-4f10-b513-888f0784a81a`, initiative `1b9ef2c4-…`).
 *
 * Layout: single screen with four primary modules (2×2 desktop, stacked
 * mobile):
 *   1. NOW           — what changed in the last 24h
 *   2. ACTIVE WORK   — initiatives / action items / needs review
 *   3. LIBRARY       — pinned + recent (filters ship in PR3)
 *   4. GUIDED ACTIONS— safe next-step buttons (wired in PR4; stub here)
 *
 * Data sources:
 *   - `/api/workspaces/<id>/home/` — the workspace snapshot (PR1, S2983)
 *   - `/api/home/boot/`            — greeting + since-last-visit only
 *
 * Design decision (S2983 PR2, Claude+Rigby joint agreement): the prior
 * Session 1078 HomeTab was a global platform dashboard (vitals/celery/
 * attention). Chris confirmed he wasn't using it yet, so we replaced it
 * outright with the workspace-legibility shape the spec asked for and
 * kept only the greeting band + a "hours since visit" chip (orthogonal
 * value the spec doesn't cover).
 */

import { useMemo, useState, lazy, Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity, AlertTriangle, ArrowRight, BookOpen, ChevronDown, ChevronRight,
  ClipboardList, Clock, FileText, GitBranch, Layers, Loader2, Package,
  Plus, Sparkles, Star, Target, XCircle,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

// S2984 PR3: DocumentViewer lazy-loaded — arc entrypoints open in the
// in-app viewer per spec §Frontend / Chris directive #3 (no GitHub links).
const LazyDocumentViewer = lazy(() =>
  import('@/components/platform/DocumentViewer').then((m) => ({ default: m.DocumentViewer })),
)

interface HomeTabProps {
  activeWorkspace: { id: string; name: string } | null
  onNavigateTab: (tab: string) => void
}

// --------------------------------------------------------------------- //
// Types matching the backend response (spec §3.1)
// --------------------------------------------------------------------- //

interface TimelineEntry {
  kind: 'deliverable_created' | 'deliverable_updated' | 'agent_run_failed'
  id: string
  title?: string
  agent?: string
  at: string | null
}

interface NowSection {
  window_hours: number
  runs_count: number
  failures_count: number
  new_deliverables_count: number
  updated_deliverables_count: number
  timeline: TimelineEntry[]
}

interface InitiativeCard {
  id: string
  name: string
  status: string
  stage: number
  updated_at: string | null
  next_action: string
  action_items_count: number
}

interface ActionItemCard {
  id: string
  title: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  status: 'pending' | 'in_progress'
  initiative_id: string
  initiative_name: string
}

interface DeliverableCard {
  id: string
  title: string
  type: string
  status: string
  is_pinned: boolean
  updated_at: string | null
  initiative_id: string | null
}

interface ActiveWorkSection {
  initiatives: InitiativeCard[]
  action_items: ActionItemCard[]
  needs_review: {
    ready_deliverables: DeliverableCard[]
    pending_decisions: unknown[]
  }
}

interface LibrarySection {
  pinned: DeliverableCard[]
  recent: DeliverableCard[]
}

interface HomeSnapshot {
  workspace: { id: string; name: string }
  now: NowSection
  active_work: ActiveWorkSection
  library: LibrarySection
}

// --------------------------------------------------------------------- //
// Helpers
// --------------------------------------------------------------------- //

function relativeTime(iso: string | null): string {
  if (!iso) return '—'
  const diffMs = Date.now() - new Date(iso).getTime()
  if (diffMs < 60_000) return 'just now'
  const mins = Math.floor(diffMs / 60_000)
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

const PRIORITY_STYLES: Record<ActionItemCard['priority'], { chip: string; label: string }> = {
  critical: { chip: 'bg-accent-red/20 text-accent-red border-accent-red/30', label: 'Critical' },
  high:     { chip: 'bg-accent-amber/20 text-accent-amber border-accent-amber/30', label: 'High' },
  medium:   { chip: 'bg-primary-500/20 text-primary-400 border-primary-500/30', label: 'Medium' },
  low:      { chip: 'bg-gray-500/20 text-gray-400 border-gray-500/30', label: 'Low' },
}

const STATUS_STYLES: Record<string, string> = {
  ready: 'bg-accent-green/20 text-accent-green border-accent-green/30',
  draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  published: 'bg-primary-500/20 text-primary-400 border-primary-500/30',
  archived: 'bg-gray-700/40 text-gray-500 border-gray-700/40',
  completed: 'bg-accent-green/20 text-accent-green border-accent-green/30',
}

function statusChipClass(status: string) {
  return STATUS_STYLES[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'
}

// --------------------------------------------------------------------- //
// Section: NOW
// --------------------------------------------------------------------- //

function NowModule({ data }: { data: NowSection }) {
  const chips = [
    { label: 'Runs', value: data.runs_count, icon: Activity, tone: 'text-primary-400' },
    { label: 'Failures', value: data.failures_count, icon: XCircle, tone: data.failures_count > 0 ? 'text-accent-red' : 'text-gray-400' },
    { label: 'New', value: data.new_deliverables_count, icon: Plus, tone: 'text-accent-green' },
    { label: 'Updated', value: data.updated_deliverables_count, icon: FileText, tone: 'text-primary-400' },
  ]

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-primary-400" />
          <h2 className="text-lg font-semibold">Now</h2>
          <span className="text-xs text-gray-500">last {data.window_hours}h</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {chips.map((c) => (
          <div key={c.label} className="rounded-lg bg-dark-bg/60 border border-dark-border p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{c.label}</span>
              <c.icon size={14} className={c.tone} />
            </div>
            <div className={cn('text-2xl font-semibold mt-1', c.tone)}>{c.value}</div>
          </div>
        ))}
      </div>

      <div>
        <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-2">Timeline</h3>
        {data.timeline.length === 0 ? (
          <p className="text-sm text-gray-500 italic">Nothing has happened here in the last {data.window_hours} hours.</p>
        ) : (
          <ul className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
            {data.timeline.map((entry) => {
              const Icon = entry.kind === 'agent_run_failed' ? XCircle
                : entry.kind === 'deliverable_created' ? Plus
                : FileText
              const tone = entry.kind === 'agent_run_failed' ? 'text-accent-red' : 'text-gray-400'
              return (
                <li key={`${entry.kind}-${entry.id}`} className="flex items-start gap-2 text-sm">
                  <Icon size={14} className={cn('mt-0.5 flex-shrink-0', tone)} />
                  <div className="flex-1 min-w-0">
                    <div className="truncate">
                      {entry.title || entry.agent || 'Untitled'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {entry.kind.replace(/_/g, ' ')} · {relativeTime(entry.at)}
                    </div>
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </div>
  )
}

// --------------------------------------------------------------------- //
// Section: ACTIVE WORK
// --------------------------------------------------------------------- //

function ActiveWorkModule({
  data,
  onNavigateTab,
}: {
  data: ActiveWorkSection
  onNavigateTab: (tab: string) => void
}) {
  return (
    <div className="card space-y-5">
      <div className="flex items-center gap-2">
        <Target size={18} className="text-primary-400" />
        <h2 className="text-lg font-semibold">Active Work</h2>
      </div>

      {/* Active initiatives */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs uppercase tracking-wide text-gray-500">Active Initiatives</h3>
          <button
            onClick={() => onNavigateTab('initiatives')}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            View all <ArrowRight size={12} />
          </button>
        </div>
        {data.initiatives.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No initiatives in this workspace yet.</p>
        ) : (
          <ul className="space-y-2">
            {data.initiatives.slice(0, 5).map((init) => (
              <li key={init.id} className="rounded-md bg-dark-bg/60 border border-dark-border p-3 hover:border-primary-500/50 transition-colors">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-medium truncate">{init.name}</span>
                      <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400 border border-primary-500/30">
                        {init.status}
                      </span>
                    </div>
                    {init.next_action && (
                      <p className="text-xs text-gray-400 truncate">Next: {init.next_action}</p>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-xs text-gray-500">Stage {init.stage}</div>
                    <div className="text-xs text-gray-500">{init.action_items_count} action{init.action_items_count === 1 ? '' : 's'}</div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Next actions */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs uppercase tracking-wide text-gray-500">My Next Actions</h3>
        </div>
        {data.action_items.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No pending action items.</p>
        ) : (
          <ul className="space-y-1.5">
            {data.action_items.slice(0, 5).map((item) => {
              const prio = PRIORITY_STYLES[item.priority]
              return (
                <li key={item.id} className="flex items-start gap-2 text-sm">
                  <span className={cn('text-xs px-1.5 py-0.5 rounded border mt-0.5 flex-shrink-0', prio.chip)}>
                    {prio.label}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate">{item.title}</div>
                    <div className="text-xs text-gray-500 truncate">{item.initiative_name}</div>
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </section>

      {/* Needs review */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs uppercase tracking-wide text-gray-500 flex items-center gap-1.5">
            <AlertTriangle size={12} className="text-accent-amber" />
            Needs Review
          </h3>
        </div>
        {data.needs_review.ready_deliverables.length === 0 ? (
          <p className="text-sm text-gray-500 italic">Nothing waiting on review.</p>
        ) : (
          <ul className="space-y-1.5">
            {data.needs_review.ready_deliverables.slice(0, 5).map((d) => (
              <li key={d.id} className="flex items-start gap-2 text-sm">
                <FileText size={14} className="text-accent-amber mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="truncate">{d.title}</div>
                  <div className="text-xs text-gray-500">
                    {d.type} · {relativeTime(d.updated_at)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

// --------------------------------------------------------------------- //
// Section: LIBRARY
// --------------------------------------------------------------------- //

function LibraryModule({
  data,
  onNavigateTab,
}: {
  data: LibrarySection
  onNavigateTab: (tab: string) => void
}) {
  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen size={18} className="text-primary-400" />
          <h2 className="text-lg font-semibold">Library</h2>
        </div>
        <button
          onClick={() => onNavigateTab('deliverables')}
          className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
        >
          Browse all <ArrowRight size={12} />
        </button>
      </div>

      <section>
        <div className="flex items-center gap-1.5 mb-2">
          <Star size={12} className="text-accent-amber" />
          <h3 className="text-xs uppercase tracking-wide text-gray-500">Pinned</h3>
        </div>
        {data.pinned.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No pinned deliverables — pin work you want to return to.</p>
        ) : (
          <ul className="space-y-1.5">
            {data.pinned.slice(0, 5).map((d) => (
              <li key={d.id} className="flex items-start gap-2 text-sm">
                <Star size={14} className="text-accent-amber mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="truncate">{d.title}</div>
                  <div className="text-xs text-gray-500 flex items-center gap-1.5">
                    <span>{d.type}</span>
                    <span className={cn('text-xs px-1 py-0 rounded border', statusChipClass(d.status))}>{d.status}</span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <div className="flex items-center gap-1.5 mb-2">
          <Clock size={12} className="text-gray-400" />
          <h3 className="text-xs uppercase tracking-wide text-gray-500">Recently Updated</h3>
        </div>
        {data.recent.length === 0 ? (
          <p className="text-sm text-gray-500 italic">No other deliverables in this workspace yet.</p>
        ) : (
          <ul className="space-y-1.5">
            {data.recent.slice(0, 5).map((d) => (
              <li key={d.id} className="flex items-start gap-2 text-sm">
                <Package size={14} className="text-gray-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="truncate">{d.title}</div>
                  <div className="text-xs text-gray-500">
                    {d.type} · {relativeTime(d.updated_at)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="text-xs text-gray-500 italic border-t border-dark-border pt-3">
        Filters + Canonical view ship in the next round.
      </p>
    </div>
  )
}

// --------------------------------------------------------------------- //
// Section: RESEARCH ARCS (S2984 PR3) — repo docs/research/domains/*
// --------------------------------------------------------------------- //

interface ArcEntrypoint {
  label: string
  path: string
}

interface ResearchArc {
  arc_id: string
  title: string
  path: string
  status: 'active' | 'hanging' | 'done' | 'stale'
  last_touched_at: string | null
  days_since_touched: number | null
  entrypoints: ArcEntrypoint[]
  signals: {
    has_canonical_summary: boolean
    open_questions_markers: number
    todo_hits: number
  }
}

interface ResearchArcsResponse {
  generated_at: string
  root: string
  active_days: number
  stale_days: number
  arcs: ResearchArc[]
}

const STATUS_GROUPS: Array<{
  key: ResearchArc['status']
  label: string
  chip: string
  hint: string
}> = [
  {
    key: 'active',
    label: 'Active',
    chip: 'bg-accent-green/20 text-accent-green border-accent-green/30',
    hint: 'Touched in the last 14 days.',
  },
  {
    key: 'hanging',
    label: 'Hanging',
    chip: 'bg-accent-amber/20 text-accent-amber border-accent-amber/30',
    hint: 'Open questions / TODOs, or no canonical summary.',
  },
  {
    key: 'done',
    label: 'Done',
    chip: 'bg-primary-500/20 text-primary-400 border-primary-500/30',
    hint: 'Canonical summary present, no open questions, not stale.',
  },
  {
    key: 'stale',
    label: 'Stale',
    chip: 'bg-gray-500/20 text-gray-500 border-gray-500/30',
    hint: 'Not touched in 60+ days (or no timestamp available).',
  },
]

function touchedLabel(arc: ResearchArc): string {
  if (arc.days_since_touched === null) return 'Never touched'
  if (arc.days_since_touched === 0) return 'Touched today'
  if (arc.days_since_touched === 1) return 'Touched 1 day ago'
  return `Touched ${arc.days_since_touched} days ago`
}

function ArcRow({
  arc,
  onOpenPath,
}: {
  arc: ResearchArc
  onOpenPath: (path: string, label: string) => void
}) {
  return (
    <li className="rounded-md bg-dark-bg/60 border border-dark-border p-2.5 hover:border-primary-500/40 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate" title={arc.arc_id}>{arc.title}</div>
          <div className="text-xs text-gray-500 mt-0.5">{touchedLabel(arc)}</div>
        </div>
        {arc.signals.open_questions_markers > 0 && (
          <span
            className="text-[10px] px-1.5 py-0.5 rounded bg-accent-amber/15 text-accent-amber border border-accent-amber/30 flex-shrink-0"
            title={`${arc.signals.open_questions_markers} TODO/TBD/WIP hits across arc`}
          >
            {arc.signals.open_questions_markers}
          </span>
        )}
      </div>
      {arc.entrypoints.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {arc.entrypoints.map((entry) => (
            <button
              key={entry.path}
              type="button"
              onClick={() => onOpenPath(entry.path, `${arc.title} — ${entry.label}`)}
              className="text-[11px] px-1.5 py-0.5 rounded border border-dark-border text-gray-300 hover:text-primary-300 hover:border-primary-500/40 transition-colors flex items-center gap-1"
              title={entry.path}
            >
              <FileText size={10} />
              {entry.label}
            </button>
          ))}
        </div>
      )}
    </li>
  )
}

function ArcStatusColumn({
  group,
  arcs,
  onOpenPath,
}: {
  group: (typeof STATUS_GROUPS)[number]
  arcs: ResearchArc[]
  onOpenPath: (path: string, label: string) => void
}) {
  const TOP_N = 5
  const [expanded, setExpanded] = useState(false)
  const visible = expanded ? arcs : arcs.slice(0, TOP_N)

  return (
    <div className="rounded-lg border border-dark-border bg-dark-bg/40 p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={cn('text-xs px-1.5 py-0.5 rounded border', group.chip)}>
            {group.label}
          </span>
          <span className="text-xs text-gray-500">{arcs.length}</span>
        </div>
        {arcs.length > TOP_N && (
          <button
            type="button"
            onClick={() => setExpanded((e) => !e)}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-0.5"
          >
            {expanded ? (<><ChevronDown size={12} /> Less</>) : (<><ChevronRight size={12} /> All</>)}
          </button>
        )}
      </div>
      {arcs.length === 0 ? (
        <p className="text-xs text-gray-500 italic py-1">None.</p>
      ) : (
        <ul className="space-y-1.5">
          {visible.map((arc) => (
            <ArcRow key={arc.arc_id} arc={arc} onOpenPath={onOpenPath} />
          ))}
        </ul>
      )}
    </div>
  )
}

function ResearchArcsModule({
  onOpenPath,
}: {
  onOpenPath: (path: string, label: string) => void
}) {
  const arcsQuery = useQuery<ResearchArcsResponse>({
    queryKey: ['repo-research-arcs'],
    queryFn: async () => {
      const res = await api.get('/repo/research/arcs/')
      return res.data as ResearchArcsResponse
    },
    // Backend caches 30s; refetch on a slightly longer interval so a
    // second tab-open shares the same warm entry.
    refetchInterval: 60_000,
    retry: false,
  })

  // Group arcs by status — sorted within each group by recency (already
  // deterministic on the backend by arc_id, so we re-sort here by
  // last_touched_at DESC per spec §Frontend "Sort within group").
  const grouped = useMemo(() => {
    const out: Record<ResearchArc['status'], ResearchArc[]> = {
      active: [], hanging: [], done: [], stale: [],
    }
    for (const arc of arcsQuery.data?.arcs ?? []) {
      out[arc.status].push(arc)
    }
    for (const status of Object.keys(out) as ResearchArc['status'][]) {
      out[status].sort((a, b) => {
        const at = a.last_touched_at ?? ''
        const bt = b.last_touched_at ?? ''
        return bt.localeCompare(at)
      })
    }
    return out
  }, [arcsQuery.data])

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitBranch size={18} className="text-primary-400" />
          <h2 className="text-lg font-semibold">Research Arcs (Repo)</h2>
        </div>
        <span className="text-xs text-gray-500">
          Auto-detected from <code className="font-mono">docs/research/domains</code>
        </span>
      </div>

      {arcsQuery.isLoading ? (
        <div className="flex items-center justify-center py-6">
          <Loader2 className="animate-spin text-primary-400" size={20} />
        </div>
      ) : arcsQuery.isError || !arcsQuery.data ? (
        <p className="text-sm text-gray-500 italic py-2">
          Couldn't load research arcs — the doc tree may be unreachable in this environment.
        </p>
      ) : arcsQuery.data.arcs.length === 0 ? (
        <p className="text-sm text-gray-500 italic py-2">
          No research arcs found under <code className="font-mono">docs/research/domains</code>.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {STATUS_GROUPS.map((group) => (
            <ArcStatusColumn
              key={group.key}
              group={group}
              arcs={grouped[group.key]}
              onOpenPath={onOpenPath}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// --------------------------------------------------------------------- //
// Section: GUIDED ACTIONS (stub — PR4 wires the buttons)
// --------------------------------------------------------------------- //

const GUIDED_ACTIONS = [
  { id: 'create-spec', label: 'Create Engineering Spec', icon: FileText, hint: 'Draft a new spec deliverable with a template' },
  { id: 'review-ready', label: 'Review Ready Items', icon: ClipboardList, hint: 'Filter deliverables where status = ready' },
  { id: 'start-initiative', label: 'Start Initiative from Spec', icon: Target, hint: 'Wizard: pick a spec → create initiative → link' },
  { id: 'shift-brief', label: 'Run Shift Brief', icon: Sparkles, hint: 'Rigby-generated summary of the workspace right now' },
]

function GuidedActionsModule() {
  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2">
        <Layers size={18} className="text-primary-400" />
        <h2 className="text-lg font-semibold">Guided Actions</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {GUIDED_ACTIONS.map((action) => (
          <button
            key={action.id}
            type="button"
            disabled
            title={`${action.hint} (available in PR4)`}
            className="flex items-start gap-2 text-left rounded-md border border-dark-border bg-dark-bg/40 p-3 opacity-60 cursor-not-allowed"
          >
            <action.icon size={16} className="text-primary-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{action.label}</div>
              <div className="text-xs text-gray-500 truncate">{action.hint}</div>
            </div>
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-500 italic">
        These will light up in an upcoming round.
      </p>
    </div>
  )
}

// --------------------------------------------------------------------- //
// Greeting band (kept from prior HomeTab per Rigby A-prime+ agreement)
// --------------------------------------------------------------------- //

interface BootData {
  greeting?: { time_of_day?: string; user_name?: string; message?: string }
  while_away?: { hours_since_visit?: number }
}

function GreetingBand({ workspaceName, boot }: { workspaceName: string; boot: BootData | undefined }) {
  const greetingText = useMemo(() => {
    const tod = boot?.greeting?.time_of_day || 'day'
    const name = boot?.greeting?.user_name
    const base = `Good ${tod}${name ? `, ${name}` : ''}`
    return base
  }, [boot])

  const hoursSince = boot?.while_away?.hours_since_visit
  const sinceLabel = typeof hoursSince === 'number' && hoursSince >= 1
    ? `${hoursSince < 24 ? `${Math.round(hoursSince)}h` : `${Math.round(hoursSince / 24)}d`} since your last visit`
    : null

  return (
    <div className="rounded-xl border border-dark-border bg-gradient-to-r from-primary-500/10 via-dark-card to-dark-card p-4 md:p-5">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold">{greetingText}</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            You're in <span className="text-primary-400 font-medium">{workspaceName}</span>.
          </p>
        </div>
        {sinceLabel && (
          <span className="text-xs px-2 py-1 rounded bg-dark-bg border border-dark-border text-gray-400 flex items-center gap-1.5">
            <Clock size={12} />
            {sinceLabel}
          </span>
        )}
      </div>
    </div>
  )
}

// --------------------------------------------------------------------- //
// Root component
// --------------------------------------------------------------------- //

export default function HomeTab({ activeWorkspace, onNavigateTab }: HomeTabProps) {
  const wsId = activeWorkspace?.id

  // S2984 PR3: doc viewer slide-out state — arc entrypoint clicks feed here.
  const [docViewer, setDocViewer] = useState<{ path: string; title: string } | null>(null)
  const openArcDoc = (path: string, title: string) => setDocViewer({ path, title })

  const snapshotQuery = useQuery<HomeSnapshot>({
    queryKey: ['workspace-home-snapshot', wsId],
    queryFn: async () => {
      const res = await api.get(`/workspaces/${wsId}/home/`)
      return res.data as HomeSnapshot
    },
    enabled: !!wsId,
    refetchInterval: 60_000,
    retry: false,
  })

  // Greeting-only fetch — kept from prior HomeTab per Rigby A-prime+ agreement.
  const bootQuery = useQuery<BootData>({
    queryKey: ['home-boot-greeting', wsId],
    queryFn: async () => {
      const res = await api.get('/home/boot/', { params: wsId ? { workspace: wsId } : undefined })
      return res.data as BootData
    },
    refetchInterval: 5 * 60_000,
    retry: false,
  })

  if (!activeWorkspace) {
    return (
      <div className="card text-center py-12">
        <BookOpen size={32} className="mx-auto text-gray-500 mb-3" />
        <p className="text-sm text-gray-400">Select a workspace to see its Home view.</p>
      </div>
    )
  }

  if (snapshotQuery.isLoading) {
    return (
      <div className="card flex items-center justify-center py-16">
        <Loader2 className="animate-spin text-primary-400" size={28} />
      </div>
    )
  }

  if (snapshotQuery.isError || !snapshotQuery.data) {
    return (
      <div className="card border border-accent-red/30 p-6">
        <div className="flex items-center gap-2 mb-2">
          <XCircle size={18} className="text-accent-red" />
          <h2 className="text-lg font-semibold">Home snapshot unavailable</h2>
        </div>
        <p className="text-sm text-gray-400">
          Couldn't load the workspace snapshot. Try refreshing; the underlying data may still be reachable via
          the individual tabs (Deliverables, Initiatives, Operations).
        </p>
      </div>
    )
  }

  const snapshot = snapshotQuery.data

  return (
    <div className="space-y-5">
      <GreetingBand workspaceName={snapshot.workspace.name} boot={bootQuery.data} />

      {/* S2984 PR3: research arcs — full-width, above the 2×2 grid per
          spec §Frontend "near the top of Home". */}
      <ResearchArcsModule onOpenPath={openArcDoc} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <NowModule data={snapshot.now} />
        <ActiveWorkModule data={snapshot.active_work} onNavigateTab={onNavigateTab} />
        <LibraryModule data={snapshot.library} onNavigateTab={onNavigateTab} />
        <GuidedActionsModule />
      </div>

      {/* S2984 PR3: in-app doc viewer for arc entrypoints. Lazy-loaded so
          the DocumentViewer bundle only downloads when an arc is clicked. */}
      <Suspense fallback={null}>
        <LazyDocumentViewer
          documentPath={docViewer?.path ?? null}
          title={docViewer?.title}
          isOpen={docViewer !== null}
          onClose={() => setDocViewer(null)}
        />
      </Suspense>
    </div>
  )
}
