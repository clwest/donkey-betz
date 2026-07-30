// S3047 slice 2: Rigby Tool Gap Ledger — operator dashboard for the
// engineering_backlog deliverables stored in the Donkey Betz workspace.
// Reuses deliverablesApi.list — no new backend needed.
//
// Hard-scoped to the Donkey Betz workspace because the ledger is a
// platform-wide concern (Rigby logs gaps here regardless of the workspace
// context that surfaced them). If a second workspace ever hosts a ledger,
// update TOOL_GAP_LEDGER_WORKSPACE_ID (single point of edit).

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'
import remarkGfm from 'remark-gfm'
import {
  ClipboardList,
  Loader2,
  RefreshCw,
  X,
  CheckCircle2,
  Clock,
  AlertCircle,
  PauseCircle,
  Copy,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { deliverablesApi } from '@/lib/api'

// Rigby Tool Gap Ledger lives in the Donkey Betz workspace. Single edit
// point if this ever moves — the entire tab reads through this constant.
const TOOL_GAP_LEDGER_WORKSPACE_ID = 'b4503364-2573-4401-9e28-61a739e0ce50'
const TOOL_GAP_LEDGER_WORKSPACE_NAME = 'Donkey Betz'

interface LedgerRow {
  id: string
  title: string
  deliverable_type: string
  category: string
  agent_name: string
  status: string
  created_at: string
  updated_at: string
  workspace_id?: string | null
  workspace_name?: string | null
  quality_score?: number | null
  is_saved?: boolean
}

interface LedgerListResponse {
  success?: boolean
  deliverables?: LedgerRow[]
  count?: number
  total?: number
  pagination?: { total?: number; count?: number; page?: number }
}

interface LedgerDetailRow extends LedgerRow {
  content?: string
  content_format?: string
}

interface LedgerDetailResponse {
  success?: boolean
  deliverable?: LedgerDetailRow
  [k: string]: unknown
}

const STATUS_META: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  ready: { label: 'ready', className: 'bg-amber-500/15 text-amber-300 border-amber-500/30', icon: Clock },
  in_progress: { label: 'in progress', className: 'bg-blue-500/15 text-blue-300 border-blue-500/30', icon: Loader2 },
  completed: { label: 'completed', className: 'bg-green-500/15 text-green-300 border-green-500/30', icon: CheckCircle2 },
  deferred: { label: 'deferred', className: 'bg-slate-500/15 text-slate-300 border-slate-500/30', icon: PauseCircle },
  draft: { label: 'draft', className: 'bg-slate-500/15 text-slate-400 border-slate-500/30', icon: Clock },
}

// Preferred rendering order — buckets Chris cares about first.
const STATUS_ORDER = ['ready', 'in_progress', 'draft', 'deferred', 'completed']

function StatusBadge({ status }: { status: string }) {
  const meta = STATUS_META[status] || {
    label: status,
    className: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
    icon: AlertCircle,
  }
  const Icon = meta.icon
  const spin = status === 'in_progress'
  return (
    <span className={cn('inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-medium', meta.className)}>
      <Icon size={12} className={cn(spin && 'animate-spin')} />
      {meta.label}
    </span>
  )
}

function CategoryBadge({ category }: { category: string }) {
  if (!category) return null
  return (
    <span className="inline-flex items-center rounded border border-slate-700 bg-slate-800/60 px-1.5 py-0.5 text-[10px] font-mono text-slate-300">
      {category}
    </span>
  )
}

function formatRelative(iso: string): string {
  const d = new Date(iso)
  const diff = Date.now() - d.getTime()
  const s = Math.floor(diff / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const days = Math.floor(h / 24)
  if (days < 30) return `${days}d ago`
  return d.toLocaleDateString()
}

function DetailDrawer({ id, onClose }: { id: string; onClose: () => void }) {
  const { data, isLoading, error } = useQuery<LedgerDetailResponse>({
    queryKey: ['tool-gap-ledger-detail', id],
    queryFn: async () => {
      const res = await deliverablesApi.detail(id)
      return res.data
    },
  })

  const row: LedgerDetailRow | undefined = data?.deliverable

  return (
    <aside className="flex h-full w-full max-w-2xl flex-col border-l border-slate-800 bg-slate-900/95">
      <header className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div className="min-w-0 flex-1 pr-3">
          <div className="flex items-center gap-2">
            <ClipboardList size={16} className="text-slate-400 flex-shrink-0" />
            <span className="truncate text-sm font-semibold text-slate-100">
              {row?.title || 'Loading…'}
            </span>
          </div>
          <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
            <span className="font-mono">{id.slice(0, 8)}…{id.slice(-4)}</span>
            <button
              onClick={() => navigator.clipboard?.writeText(id)}
              className="rounded p-0.5 text-slate-500 hover:bg-slate-800 hover:text-slate-200"
              title="Copy full ID"
              aria-label="Copy ledger row ID"
            >
              <Copy size={10} />
            </button>
            {row && <StatusBadge status={row.status} />}
            {row?.category && <CategoryBadge category={row.category} />}
          </div>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
          aria-label="Close ledger detail"
        >
          <X size={18} />
        </button>
      </header>

      <div className="flex-1 overflow-auto p-4">
        {isLoading && (
          <div className="flex items-center justify-center py-12 text-slate-400">
            <Loader2 size={20} className="animate-spin" />
          </div>
        )}
        {!!error && (
          <div className="rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
            Failed to load ledger row.
          </div>
        )}
        {row && (
          <>
            <div className="grid grid-cols-2 gap-2 text-xs mb-4">
              <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                <div className="text-slate-500 uppercase tracking-wide">Created</div>
                <div className="mt-0.5 font-mono text-slate-100">{formatRelative(row.created_at)}</div>
              </div>
              <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
                <div className="text-slate-500 uppercase tracking-wide">Updated</div>
                <div className="mt-0.5 font-mono text-slate-100">{formatRelative(row.updated_at)}</div>
              </div>
            </div>

            {row.content ? (
              <article className="prose prose-invert prose-sm max-w-none prose-pre:bg-slate-950/60 prose-pre:border prose-pre:border-slate-800">
                <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
                  {row.content}
                </ReactMarkdown>
              </article>
            ) : (
              <div className="rounded border border-slate-800 bg-slate-950/40 p-3 text-sm text-slate-500 italic">
                No content body.
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  )
}

export function ToolGapLedgerTab() {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { data, isLoading, isFetching, error, refetch } = useQuery<LedgerListResponse>({
    queryKey: ['tool-gap-ledger', TOOL_GAP_LEDGER_WORKSPACE_ID],
    queryFn: async () => {
      const res = await deliverablesApi.list({
        type: 'engineering_backlog',
        workspace: TOOL_GAP_LEDGER_WORKSPACE_ID,
        per_page: 100,
      })
      return res.data
    },
    refetchInterval: 30000,
  })

  const rows: LedgerRow[] = data?.deliverables || []
  const totalCount = data?.pagination?.total ?? data?.total ?? data?.count ?? rows.length

  const grouped = useMemo(() => {
    const buckets: Record<string, LedgerRow[]> = {}
    for (const r of rows) {
      const key = r.status || 'unknown'
      if (!buckets[key]) buckets[key] = []
      buckets[key].push(r)
    }
    return buckets
  }, [rows])

  const statusesInOrder = useMemo(() => {
    const seen = Object.keys(grouped)
    const ordered = STATUS_ORDER.filter((s) => seen.includes(s))
    const extras = seen.filter((s) => !STATUS_ORDER.includes(s))
    return [...ordered, ...extras]
  }, [grouped])

  return (
    <div className="flex h-full">
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <ClipboardList size={18} className="text-slate-400" />
              Tool Gap Ledger
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Rigby-authored engineering backlog · stored in the{' '}
              <span className="font-mono text-slate-400">{TOOL_GAP_LEDGER_WORKSPACE_NAME}</span> workspace ·
              click any row for full content
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">{totalCount} row{totalCount === 1 ? '' : 's'}</span>
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="rounded border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800 disabled:opacity-50 flex items-center gap-1.5"
            >
              <RefreshCw size={12} className={cn(isFetching && 'animate-spin')} />
              Refresh
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto">
          {isLoading && (
            <div className="flex items-center justify-center py-16 text-slate-400">
              <Loader2 size={20} className="animate-spin" />
            </div>
          )}
          {!!error && (
            <div className="m-4 rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
              Failed to load ledger.
            </div>
          )}
          {!isLoading && !error && rows.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500">
              <ClipboardList size={32} className="mb-2 opacity-40" />
              <div className="text-sm">No ledger rows.</div>
            </div>
          )}
          {!isLoading && rows.length > 0 && (
            <div className="p-4 space-y-6">
              {statusesInOrder.map((status) => (
                <section key={status}>
                  <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                    <StatusBadge status={status} />
                    <span className="text-slate-500">·</span>
                    <span>{grouped[status].length} row{grouped[status].length === 1 ? '' : 's'}</span>
                  </h3>
                  <div className="rounded border border-slate-800 bg-slate-950/40 divide-y divide-slate-800/60">
                    {grouped[status].map((row) => (
                      <button
                        key={row.id}
                        onClick={() => setSelectedId(row.id)}
                        className={cn(
                          'flex w-full flex-col gap-1 px-4 py-2.5 text-left hover:bg-slate-800/40',
                          selectedId === row.id && 'bg-slate-800/60',
                        )}
                      >
                        <div className="flex items-start gap-2 min-w-0">
                          <span className="text-sm text-slate-100 truncate flex-1">{row.title}</span>
                          <CategoryBadge category={row.category} />
                        </div>
                        <div className="flex items-center gap-3 text-xs text-slate-500">
                          <span title={row.created_at}>created {formatRelative(row.created_at)}</span>
                          {row.updated_at !== row.created_at && (
                            <span title={row.updated_at}>· updated {formatRelative(row.updated_at)}</span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </section>
              ))}
            </div>
          )}
        </div>
      </div>

      {selectedId && (
        <DetailDrawer id={selectedId} onClose={() => setSelectedId(null)} />
      )}
    </div>
  )
}

export default ToolGapLedgerTab
