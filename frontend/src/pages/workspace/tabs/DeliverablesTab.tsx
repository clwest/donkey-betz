// Session 1009: Deliverables Library Tab
// Browse, search, and manage agent-produced deliverables

import { useState, useEffect, useRef, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { trackEvent } from '@/hooks/useTelemetryEvent'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'
import remarkGfm from 'remark-gfm'
import {
  Package,
  Bookmark,
  BookmarkCheck,
  Copy,
  Download,
  Search,
  Loader2,
  RefreshCw,
  ArrowLeft,
  FileText,
  Clock,
  ChevronLeft,
  ChevronRight,
  LayoutTemplate,
  Filter,
  X,
  User,
  Bot,
  Zap,
  ListChecks,
  Inbox,
  CheckCircle2,
  MessageSquare,
  Trash2,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { deliverablesApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { usePAStore } from '@/stores/paStore'
import { useAssistantContextStore } from '@/stores/assistantContextStore'

// ============ Types ============

interface Deliverable {
  id: string
  title: string
  slug: string
  deliverable_type: string
  category: string
  tags: string[]
  agent_name: string
  agent_task: string
  preview_content: string
  thumbnail_url: string | null
  quality_score: number
  confidence_score: number
  is_saved: boolean
  is_template: boolean
  is_starred: boolean
  clone_count: number
  is_cloned: boolean
  execution_time_ms: number | null
  llm_cost: string
  word_count: number
  line_count: number
  status: string
  source: 'user' | 'system'
  created_at: string
  updated_at: string
  // Session 1091 — workspace assignment surfacing
  workspace_id?: string | null
  workspace_name?: string | null
  is_orphan?: boolean
  // detail-only fields
  content?: string
  content_format?: string
  tool_calls?: unknown[]
  raw_output?: Record<string, unknown>
  metadata?: Record<string, unknown>
  source_operation?: { id: string; operation_type: string; file_path: string }
}

interface DeliverableStats {
  total: number
  saved: number
  templates: number
  recent_7d: number
  user_count: number
  system_count: number
  by_type: Array<{ deliverable_type: string; count: number }>
  by_category: Array<{ category: string; count: number }>
  by_agent: Array<{ agent_name: string; count: number }>
  // Session 1091 Sprint B — workspace breakdown
  by_workspace?: Array<{
    workspace_id: string | null
    workspace_name: string
    count: number
    is_orphan: boolean
    is_unassigned: boolean
  }>
  orphan_count?: number
  unassigned_count?: number
}

interface DeliverableType {
  value: string
  label: string
}

interface Pagination {
  page: number
  per_page: number
  total_pages: number
  total_items: number
  has_next: boolean
  has_previous: boolean
}

// ============ Helpers ============

const TYPE_COLORS: Record<string, string> = {
  document: 'bg-blue-500/20 text-blue-400',
  image: 'bg-purple-500/20 text-purple-400',
  video: 'bg-red-500/20 text-red-400',
  audio: 'bg-pink-500/20 text-pink-400',
  code: 'bg-green-500/20 text-green-400',
  analysis: 'bg-cyan-500/20 text-cyan-400',
  report: 'bg-orange-500/20 text-orange-400',
  template: 'bg-yellow-500/20 text-yellow-400',
  research: 'bg-indigo-500/20 text-indigo-400',
  strategy: 'bg-emerald-500/20 text-emerald-400',
  plan: 'bg-teal-500/20 text-teal-400',
  script: 'bg-lime-500/20 text-lime-400',
}

const STATUS_COLORS: Record<string, string> = {
  completed: 'bg-green-500/20 text-green-400',
  draft: 'bg-yellow-500/20 text-yellow-400',
  processing: 'bg-blue-500/20 text-blue-400',
  failed: 'bg-red-500/20 text-red-400',
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatTimeShort(iso: string) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit',
  })
}

// Session 1246 — Grouped view helpers. Recency-first (Today / This Week /
// This Month / Older) → category accordions inside. Rigby's design call:
// Chris's framing ("read through what's been done") is fundamentally time-
// oriented, and category is the best semantic chunking inside time.

const RECENCY_BUCKETS = ['today', 'this_week', 'this_month', 'older'] as const
type RecencyBucket = (typeof RECENCY_BUCKETS)[number]

const RECENCY_LABELS: Record<RecencyBucket, string> = {
  today: 'Today',
  this_week: 'This Week',
  this_month: 'This Month',
  older: 'Older',
}

function bucketRecency(iso: string): RecencyBucket {
  const now = new Date()
  const created = new Date(iso)
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  if (created >= startOfToday) return 'today'
  const sevenDaysAgo = new Date(startOfToday.getTime() - 6 * 24 * 60 * 60 * 1000)
  if (created >= sevenDaysAgo) return 'this_week'
  const thirtyDaysAgo = new Date(startOfToday.getTime() - 29 * 24 * 60 * 60 * 1000)
  if (created >= thirtyDaysAgo) return 'this_month'
  return 'older'
}

// Empty/missing category surfaces as a dedicated bucket so we don't
// silently hide items that lack metadata. Rigby's 5th-consideration ask:
// becomes the feedback loop for category discipline.
const UNCATEGORIZED_KEY = '__uncategorized__'
const UNCATEGORIZED_LABEL = 'Uncategorized / Needs metadata'

function categoryKey(d: Deliverable): string {
  const c = (d.category || '').trim()
  return c || UNCATEGORIZED_KEY
}

interface GroupSummary {
  count: number
  latestIso: string
  statusCounts: Record<string, number>
  topTags: { tag: string; count: number }[]
}

function summarizeGroup(items: Deliverable[]): GroupSummary {
  const statusCounts: Record<string, number> = {}
  const tagCounts: Record<string, number> = {}
  let latestIso = items[0]?.created_at ?? ''
  for (const it of items) {
    if (it.status) statusCounts[it.status] = (statusCounts[it.status] ?? 0) + 1
    for (const tag of it.tags ?? []) {
      tagCounts[tag] = (tagCounts[tag] ?? 0) + 1
    }
    if (new Date(it.created_at) > new Date(latestIso)) latestIso = it.created_at
  }
  const topTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(([tag, count]) => ({ tag, count }))
  return { count: items.length, latestIso, statusCounts, topTags }
}

interface GroupedView {
  recency: RecencyBucket
  categories: { key: string; label: string; items: Deliverable[]; summary: GroupSummary }[]
}

function groupDeliverables(items: Deliverable[]): GroupedView[] {
  const byRecency = new Map<RecencyBucket, Map<string, Deliverable[]>>()
  for (const it of items) {
    const r = bucketRecency(it.created_at)
    const c = categoryKey(it)
    let inner = byRecency.get(r)
    if (!inner) {
      inner = new Map()
      byRecency.set(r, inner)
    }
    let bucket = inner.get(c)
    if (!bucket) {
      bucket = []
      inner.set(c, bucket)
    }
    bucket.push(it)
  }
  const out: GroupedView[] = []
  for (const recency of RECENCY_BUCKETS) {
    const inner = byRecency.get(recency)
    if (!inner) continue
    const categories = Array.from(inner.entries()).map(([key, items]) => ({
      key,
      label: key === UNCATEGORIZED_KEY ? UNCATEGORIZED_LABEL : key,
      items: items.slice().sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()),
      summary: summarizeGroup(items),
    }))
    // Surface Uncategorized first inside each recency bucket (Rigby's call —
    // feedback loop for tagging discipline), then alphabetical.
    categories.sort((a, b) => {
      if (a.key === UNCATEGORIZED_KEY) return -1
      if (b.key === UNCATEGORIZED_KEY) return 1
      return a.label.localeCompare(b.label)
    })
    out.push({ recency, categories })
  }
  return out
}

function QualityBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = pct >= 80 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div className={cn('h-full rounded-full', color)} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-400">{pct}%</span>
    </div>
  )
}

// ============ Main Component ============

export function DeliverablesTab() {
  const queryClient = useQueryClient()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<{
    type?: string
    category?: string
    agent?: string
    search?: string
    saved?: boolean
    template?: boolean
    source?: string
  }>({})

  // S2984 PR4: deep-link from Home guided-action "Review Ready Items"
  // uses ?filter=ready to preset a client-side status filter. Keeps the
  // server API + existing filter shape untouched (Rigby T1 REVISE).
  // The library_filter_applied telemetry effect runs LATER in the
  // component (after activeWsId is derived) so we don't race the store.
  const [searchParams] = useSearchParams()
  const statusFilter = searchParams.get('filter') || ''
  const deliverableParam = searchParams.get('deliverable') || ''
  const [searchInput, setSearchInput] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // S2995: deep-link support — `?deliverable=<id>` auto-opens the detail
  // panel for that row on landing. Mirrors the `?filter=` pattern above.
  // `detailQuery` (below) hydrates the panel via ID; the row doesn't need
  // to be in the current list slice.
  useEffect(() => {
    if (deliverableParam) {
      setSelectedId(deliverableParam)
    }
  }, [deliverableParam])

  // Session 1246 — Grouped view (Rigby design: recency → category accordions
  // with cheap aggregation summaries). Default to grouped; persist to
  // localStorage so the toggle survives reloads. Per_page bumps when grouped
  // so all items render in one accordion view (pagination is a flat-mode
  // construct; grouping wants the whole picture).
  const [viewMode, setViewMode] = useState<'grouped' | 'flat'>(() => {
    if (typeof window === 'undefined') return 'grouped'
    const stored = window.localStorage.getItem('deliverables_view_mode')
    return stored === 'flat' ? 'flat' : 'grouped'
  })
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('deliverables_view_mode', viewMode)
    }
  }, [viewMode])
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())

  // ---- Queries ----
  // Workspace-aware: when viewed inside a workspace context, filter by
  // workspace. When on the global /deliverables page, show everything.
  const activeWsId = useWorkspaceStore(s => s.activeWorkspace?.id)

  // S2984 PR4 §5: fire library_filter_applied once per URL-param change
  // (declared here so we can key on the workspace-store value cleanly).
  useEffect(() => {
    if (statusFilter) {
      trackEvent('library_filter_applied', activeWsId, { filter: statusFilter, source: 'url' })
    }
  }, [statusFilter, activeWsId])

  const statsQuery = useQuery({
    queryKey: ['deliverables-stats', activeWsId],
    queryFn: () => deliverablesApi.stats(activeWsId ? { workspace: activeWsId } : undefined).then(r => r.data),
  })

  const typesQuery = useQuery({
    queryKey: ['deliverables-types'],
    queryFn: () => deliverablesApi.types().then(r => r.data),
  })

  // Session 1246 — Grouped mode wants the whole picture rather than a 20-row
  // page slice, so request a larger window. 200 is a tradeoff: large enough
  // to capture the workspace's session-history sweep without paying a full
  // workspace round-trip. If a workspace exceeds 200 items the grouped view
  // still shows the most-recent 200 + the flat-mode toggle remains
  // available for full paginated browse.
  const perPage = viewMode === 'grouped' ? 200 : 20
  const listQuery = useQuery({
    queryKey: ['deliverables-list', page, perPage, filters, activeWsId],
    queryFn: () => deliverablesApi.list({
      ...filters,
      page: viewMode === 'grouped' ? 1 : page,
      per_page: perPage,
      ...(activeWsId ? { workspace: activeWsId } : {}),
    }).then(r => r.data),
  })

  const detailQuery = useQuery({
    queryKey: ['deliverables-detail', selectedId],
    queryFn: () => deliverablesApi.detail(selectedId!).then(r => r.data),
    enabled: !!selectedId,
  })

  // ---- Mutations ----
  const saveMutation = useMutation({
    mutationFn: (id: string) => deliverablesApi.save(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables-list'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-detail'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    },
  })

  const unsaveMutation = useMutation({
    mutationFn: (id: string) => deliverablesApi.unsave(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables-list'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-detail'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deliverablesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables-list'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-detail'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
      setSelectedId(null)
    },
  })

  const cloneMutation = useMutation({
    mutationFn: (id: string) => deliverablesApi.clone(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables-list'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    },
  })

  const templateizeMutation = useMutation({
    mutationFn: (id: string) => deliverablesApi.templateize(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables-list'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-detail'] })
    },
  })

  const exportMutation = useMutation({
    mutationFn: ({ id, format }: { id: string; format: string }) => deliverablesApi.export(id, format),
    onSuccess: (response, { format }) => {
      const blob = new Blob([response.data])
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${detail?.slug || 'export'}.${format === 'markdown' ? 'md' : format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
  })

  const eventMutation = useMutation({
    mutationFn: ({ id, eventType, metadata }: { id: string; eventType: string; metadata?: Record<string, unknown> }) =>
      deliverablesApi.recordEvent(id, eventType, metadata),
  })

  // Fire synthesis_viewed when opening detail view
  const viewedRef = useRef<string | null>(null)
  useEffect(() => {
    if (selectedId && selectedId !== viewedRef.current) {
      viewedRef.current = selectedId
      eventMutation.mutate({ id: selectedId, eventType: 'synthesis_viewed' })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId])

  // ---- Handlers ----
  const handleSearch = () => {
    setFilters(f => ({ ...f, search: searchInput || undefined }))
    setPage(1)
  }

  const handleClearFilters = () => {
    setFilters({})
    setSearchInput('')
    setPage(1)
  }

  // Track locally which today-queue items have been acted on this session
  const [actedIds, setActedIds] = useState<Set<string>>(new Set())

  const handleQuickAction = (id: string, eventType: 'action_taken' | 'task_created') => {
    eventMutation.mutate({ id, eventType, metadata: { source: 'today_queue' } })
    setActedIds(prev => new Set(prev).add(id))
  }

  const stats: DeliverableStats | null = statsQuery.data?.stats ?? null
  const types: DeliverableType[] = typesQuery.data?.types ?? []
  const rawDeliverables: Deliverable[] = listQuery.data?.deliverables ?? []
  // S2984 PR4: apply client-side status filter from URL param
  // (?filter=ready). Kept client-side to avoid touching the server API +
  // existing filters shape for this MVP.
  const deliverables: Deliverable[] = useMemo(() => {
    if (!statusFilter) return rawDeliverables
    return rawDeliverables.filter(d => (d as unknown as { status?: string }).status === statusFilter)
  }, [rawDeliverables, statusFilter])
  const pagination: Pagination | null = listQuery.data?.pagination ?? null
  const detail: Deliverable | null = detailQuery.data?.deliverable ?? null
  const hasActiveFilters = !!(filters.type || filters.category || filters.agent || filters.search || filters.saved || filters.template || filters.source)

  // Today queue: recent deliverables (last 24h) that haven't been acted on
  const recentDeliverables = deliverables.filter(d => {
    const age = Date.now() - new Date(d.created_at).getTime()
    return age < 24 * 60 * 60 * 1000 && !actedIds.has(d.id)
  })

  // Session 1246 — shared card render used by both flat + grouped views.
  // Pulled into a closure so the existing card markup stays the single
  // source of truth instead of being duplicated across two render paths.
  const renderCard = (d: Deliverable) => (
    <button
      key={d.id}
      onClick={() => setSelectedId(d.id)}
      className="text-left bg-dark-card border border-dark-border rounded-lg p-4 hover:border-primary-500/30 transition-colors group"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="text-sm font-medium text-white group-hover:text-primary-400 transition-colors line-clamp-2">
          {d.title}
        </h4>
        <button
          onClick={(e) => {
            e.stopPropagation()
            d.is_saved ? unsaveMutation.mutate(d.id) : saveMutation.mutate(d.id)
          }}
          className="flex-shrink-0 text-gray-500 hover:text-primary-400 transition-colors"
        >
          {d.is_saved ? <BookmarkCheck size={14} className="text-primary-400" /> : <Bookmark size={14} />}
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-2">
        <span className={cn(
          'px-1.5 py-0.5 rounded text-xs inline-flex items-center gap-1',
          d.source === 'user'
            ? 'bg-emerald-500/20 text-emerald-400'
            : 'bg-gray-600/30 text-gray-400'
        )}>
          {d.source === 'user' ? <User size={10} /> : <Bot size={10} />}
          {d.source === 'user' ? 'You' : 'System'}
        </span>
        <span className={cn('px-1.5 py-0.5 rounded text-xs', TYPE_COLORS[d.deliverable_type] || 'bg-gray-700 text-gray-300')}>
          {d.deliverable_type}
        </span>
        {d.agent_name && (
          <span className="px-1.5 py-0.5 rounded text-xs bg-gray-700 text-gray-300 truncate max-w-[120px]">
            {d.agent_name}
          </span>
        )}
        {/* Session 1091 — workspace assignment surfacing.
            Orphans (workspace_id null) shouldn't happen post-fix
            but the badge shouts loudly when one slips through. */}
        {d.is_orphan ? (
          <span
            className="px-1.5 py-0.5 rounded text-xs bg-red-500/20 text-red-300 inline-flex items-center gap-1"
            title="No workspace assigned — needs triage"
          >
            Orphan
          </span>
        ) : d.workspace_name ? (
          <span
            className={cn(
              'px-1.5 py-0.5 rounded text-xs truncate max-w-[140px]',
              d.workspace_name === 'Unassigned'
                ? 'bg-amber-500/20 text-amber-300'
                : 'bg-blue-500/15 text-blue-300'
            )}
            title={
              d.workspace_name === 'Unassigned'
                ? 'Triage bucket — created without workspace; reassign as needed'
                : `Workspace: ${d.workspace_name}`
            }
          >
            {d.workspace_name}
          </span>
        ) : null}
        {d.is_template && (
          <span className="px-1.5 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400">
            template
          </span>
        )}
      </div>

      {d.preview_content && (
        <p className="text-xs text-gray-400 line-clamp-3 mb-2">
          {d.preview_content}
        </p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <Clock size={10} />
          {formatDate(d.created_at)}
        </div>
        {d.quality_score > 0 && <QualityBar score={d.quality_score} />}
      </div>

      {d.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {d.tags.slice(0, 3).map((tag, i) => (
            <span key={i} className="px-1 py-0.5 bg-gray-800 text-gray-500 rounded text-[10px]">{tag}</span>
          ))}
          {d.tags.length > 3 && (
            <span className="text-[10px] text-gray-600">+{d.tags.length - 3}</span>
          )}
        </div>
      )}
    </button>
  )

  // Session 1246 — Grouped view computed eagerly. Computation is O(N log N)
  // for the sort; N ≤ 200 by design (perPage cap above). Memo not needed.
  const groupedView: GroupedView[] = viewMode === 'grouped' ? groupDeliverables(deliverables) : []
  const toggleGroup = (key: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }
  // "View all in this group" — switch to flat view + apply the category
  // filter so the existing pagination + card grid takes it from there. The
  // Uncategorized bucket has no real category to filter on; in that case
  // we just flip to flat view and let the user browse.
  const viewAllInGroup = (categoryName: string) => {
    if (categoryName === UNCATEGORIZED_LABEL || categoryName === UNCATEGORIZED_KEY) {
      setViewMode('flat')
      setPage(1)
      return
    }
    setFilters(f => ({ ...f, category: categoryName }))
    setPage(1)
    setViewMode('flat')
  }

  // ============ Detail View ============
  if (selectedId) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => setSelectedId(null)}
          className="flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft size={14} />
          Back to list
        </button>

        {detailQuery.isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 size={24} className="animate-spin text-primary-400" />
          </div>
        )}

        {detailQuery.error && <ErrorState error={detailQuery.error} />}

        {detail && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Main content */}
            <div className="lg:col-span-2 space-y-4">
              {/* Header */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-2">
                    <h2 className="text-lg font-semibold text-white">{detail.title}</h2>
                    <div className="flex flex-wrap gap-2">
                      <span className={cn('px-2 py-0.5 rounded text-xs', TYPE_COLORS[detail.deliverable_type] || 'bg-gray-700 text-gray-300')}>
                        {detail.deliverable_type}
                      </span>
                      <span className={cn('px-2 py-0.5 rounded text-xs', STATUS_COLORS[detail.status] || 'bg-gray-700 text-gray-300')}>
                        {detail.status}
                      </span>
                      {detail.agent_name && (
                        <span className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">
                          {detail.agent_name}
                        </span>
                      )}
                      <span className={cn(
                        'px-2 py-0.5 rounded text-xs inline-flex items-center gap-1',
                        detail.source === 'user'
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : 'bg-gray-600/30 text-gray-400'
                      )}>
                        {detail.source === 'user' ? <User size={10} /> : <Bot size={10} />}
                        {detail.source === 'user' ? 'You' : 'System'}
                      </span>
                    </div>
                    {detail.quality_score > 0 && <QualityBar score={detail.quality_score} />}
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-4 overflow-auto max-h-[600px]">
                {detail.content_format === 'markdown' ? (
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>{detail.content || ''}</ReactMarkdown>
                  </div>
                ) : detail.content_format === 'html' ? (
                  <div className="prose prose-invert prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: detail.content || '' }} />
                ) : ['python', 'typescript', 'javascript', 'json'].includes(detail.content_format || '') ? (
                  <pre className="text-sm text-gray-300 font-mono whitespace-pre-wrap">{detail.content}</pre>
                ) : (
                  <div className="text-sm text-gray-300 whitespace-pre-wrap">{detail.content}</div>
                )}
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-4">
              {/* Actions */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-4 space-y-2">
                <h3 className="text-sm font-medium text-gray-300 mb-3">Actions</h3>
                <button
                  onClick={() => detail.is_saved ? unsaveMutation.mutate(detail.id) : saveMutation.mutate(detail.id)}
                  className={cn(
                    'w-full flex items-center gap-2 px-3 py-2 rounded text-sm transition-colors',
                    detail.is_saved
                      ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  )}
                >
                  {detail.is_saved ? <BookmarkCheck size={14} /> : <Bookmark size={14} />}
                  {detail.is_saved ? 'Saved' : 'Save to Library'}
                </button>
                <button
                  onClick={() => cloneMutation.mutate(detail.id)}
                  disabled={cloneMutation.isPending}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
                >
                  <Copy size={14} />
                  Clone
                </button>
                <button
                  onClick={() => templateizeMutation.mutate(detail.id)}
                  disabled={templateizeMutation.isPending || detail.is_template}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  <LayoutTemplate size={14} />
                  {detail.is_template ? 'Is Template' : 'Make Template'}
                </button>
                <div className="flex gap-2">
                  {['pdf', 'markdown', 'html', 'json'].map(fmt => (
                    <button
                      key={fmt}
                      onClick={() => exportMutation.mutate({ id: detail.id, format: fmt })}
                      disabled={exportMutation.isPending}
                      className="flex-1 flex items-center justify-center gap-1 px-2 py-2 rounded text-xs bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
                    >
                      <Download size={12} />
                      {fmt.toUpperCase()}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => {
                    if (confirm(`Delete "${detail.title}"? This cannot be undone.`)) {
                      deleteMutation.mutate(detail.id)
                    }
                  }}
                  disabled={deleteMutation.isPending}
                  className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm bg-red-900/20 text-red-400 hover:bg-red-900/40 transition-colors"
                >
                  <Trash2 size={14} />
                  Delete
                </button>

                {/* ATR CTAs — record action events for Stage 3 pilot metrics */}
                <div className="pt-2 border-t border-dark-border space-y-2">
                  <button
                    onClick={() => eventMutation.mutate({ id: detail.id, eventType: 'action_taken', metadata: { source: 'deliverables_tab' } })}
                    disabled={eventMutation.isPending}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 transition-colors"
                  >
                    <Zap size={14} />
                    Mark as Acted On
                  </button>
                  <button
                    onClick={() => eventMutation.mutate({ id: detail.id, eventType: 'task_created', metadata: { source: 'deliverables_tab' } })}
                    disabled={eventMutation.isPending}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition-colors"
                  >
                    <ListChecks size={14} />
                    Create Follow-up Task
                  </button>
                  <button
                    onClick={() => {
                      useAssistantContextStore.getState().setFocusedEntity({
                        type: 'deliverable',
                        id: detail.id,
                        title: detail.title,
                      })
                      usePAStore.getState().setCurrentInput(`Tell me about deliverable "${detail.title}"`)
                      usePAStore.getState().openDock()
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
                  >
                    <MessageSquare size={14} />
                    Ask Rigby
                  </button>
                </div>
              </div>

              {/* Metadata */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-4 space-y-3">
                <h3 className="text-sm font-medium text-gray-300 mb-1">Details</h3>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Created</span>
                    <span className="text-gray-300">{formatDate(detail.created_at)}</span>
                  </div>
                  {detail.word_count > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Words</span>
                      <span className="text-gray-300">{detail.word_count.toLocaleString()}</span>
                    </div>
                  )}
                  {detail.line_count > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Lines</span>
                      <span className="text-gray-300">{detail.line_count.toLocaleString()}</span>
                    </div>
                  )}
                  {detail.execution_time_ms && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Exec time</span>
                      <span className="text-gray-300">{(detail.execution_time_ms / 1000).toFixed(1)}s</span>
                    </div>
                  )}
                  {detail.category && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Category</span>
                      <span className="text-gray-300">{detail.category}</span>
                    </div>
                  )}
                  {detail.clone_count > 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Clones</span>
                      <span className="text-gray-300">{detail.clone_count}</span>
                    </div>
                  )}
                </div>
                {detail.tags.length > 0 && (
                  <div className="pt-2 border-t border-dark-border">
                    <span className="text-xs text-gray-500 block mb-1">Tags</span>
                    <div className="flex flex-wrap gap-1">
                      {detail.tags.map((tag, i) => (
                        <span key={i} className="px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded text-xs">{tag}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  // ============ List View ============
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Package size={20} className="text-primary-400" />
          <h3 className="text-lg font-semibold text-white">Deliverables</h3>
        </div>
        <button
          onClick={() => {
            queryClient.invalidateQueries({ queryKey: ['deliverables-list'] })
            queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
          }}
          className="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-white transition-colors"
        >
          <RefreshCw size={12} className={listQuery.isFetching ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Session 1246 — Layout reorder (Chris ask). The interactive work
          surface (source tabs + search/filters + grouped cards) lives at the
          top of the page so what's been done is the first thing visible.
          Informational panels (Stats / Workspace Breakdown / Today's Queue)
          moved below the cards section — they're still load-bearing for
          hygiene but they're context, not the main read. */}

      {/* Source Tabs */}
      <div className="flex gap-1 border-b border-dark-border pb-2">
        {([
          { key: undefined, label: 'All', count: stats?.total },
          { key: 'user', label: 'Mine', count: stats?.user_count },
          { key: 'system', label: 'System', count: stats?.system_count },
        ] as const).map((tab) => (
          <button
            key={tab.label}
            onClick={() => { setFilters(f => ({ ...f, source: tab.key })); setPage(1) }}
            className={cn(
              'px-3 py-1.5 rounded-t text-sm transition-colors flex items-center gap-1.5',
              filters.source === tab.key
                ? 'bg-primary-500/20 text-primary-400 border-b-2 border-primary-400'
                : 'text-gray-400 hover:text-white'
            )}
          >
            {tab.key === 'user' && <User size={12} />}
            {tab.key === 'system' && <Bot size={12} />}
            {tab.label}
            {tab.count !== undefined && (
              <span className="text-xs text-gray-500">{tab.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Search & Filters */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search deliverables..."
              className="w-full pl-9 pr-3 py-2 bg-gray-800/50 border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          <button
            onClick={handleSearch}
            className="px-3 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors"
          >
            Search
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              'flex items-center gap-1 px-3 py-2 rounded-lg text-sm transition-colors',
              showFilters || hasActiveFilters
                ? 'bg-primary-500/20 text-primary-400'
                : 'bg-gray-800/50 text-gray-400 hover:text-white'
            )}
          >
            <Filter size={14} />
            Filters
            {hasActiveFilters && <span className="ml-1 w-1.5 h-1.5 rounded-full bg-primary-400" />}
          </button>
          {/* Session 1246 — Grouped/Flat view toggle. Grouped is the
              default (Rigby design call: scan-ability for session-spanning
              history). Flat list is the safety valve for raw chronological
              browse + pagination. Persisted to localStorage. */}
          <button
            onClick={() => setViewMode(m => (m === 'grouped' ? 'flat' : 'grouped'))}
            className={cn(
              'flex items-center gap-1 px-3 py-2 rounded-lg text-sm transition-colors',
              viewMode === 'grouped'
                ? 'bg-primary-500/20 text-primary-400'
                : 'bg-gray-800/50 text-gray-400 hover:text-white'
            )}
            title={
              viewMode === 'grouped'
                ? 'Currently grouped by recency → category. Click for flat list.'
                : 'Currently flat list. Click for grouped view.'
            }
          >
            {viewMode === 'grouped' ? 'Grouped' : 'Flat list'}
          </button>
          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white bg-gray-800/50 transition-colors"
            >
              <X size={14} />
              Clear
            </button>
          )}
        </div>

        {showFilters && (
          <div className="flex flex-wrap gap-2 p-3 bg-gray-800/30 rounded-lg border border-dark-border">
            <select
              value={filters.type || ''}
              onChange={(e) => { setFilters(f => ({ ...f, type: e.target.value || undefined })); setPage(1) }}
              className="px-2 py-1.5 bg-gray-800 border border-dark-border rounded text-sm text-gray-300"
            >
              <option value="">All Types</option>
              {types.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <select
              value={filters.category || ''}
              onChange={(e) => { setFilters(f => ({ ...f, category: e.target.value || undefined })); setPage(1) }}
              className="px-2 py-1.5 bg-gray-800 border border-dark-border rounded text-sm text-gray-300"
            >
              <option value="">All Categories</option>
              {(stats?.by_category || []).map((c: { category: string; count: number }) => (
                <option key={c.category} value={c.category}>{c.category} ({c.count})</option>
              ))}
            </select>
            <input
              type="text"
              value={filters.agent || ''}
              onChange={(e) => { setFilters(f => ({ ...f, agent: e.target.value || undefined })); setPage(1) }}
              placeholder="Agent name"
              className="px-2 py-1.5 bg-gray-800 border border-dark-border rounded text-sm text-gray-300 placeholder-gray-500 w-36"
            />
            <button
              onClick={() => { setFilters(f => ({ ...f, saved: f.saved ? undefined : true })); setPage(1) }}
              className={cn(
                'px-2 py-1.5 rounded text-sm transition-colors',
                filters.saved ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' : 'bg-gray-800 text-gray-400 border border-dark-border'
              )}
            >
              Saved only
            </button>
            <button
              onClick={() => { setFilters(f => ({ ...f, template: f.template ? undefined : true })); setPage(1) }}
              className={cn(
                'px-2 py-1.5 rounded text-sm transition-colors',
                filters.template ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : 'bg-gray-800 text-gray-400 border border-dark-border'
              )}
            >
              Templates only
            </button>
          </div>
        )}
      </div>

      {/* Loading / Error */}
      {listQuery.isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={24} className="animate-spin text-primary-400" />
        </div>
      )}
      {listQuery.error && <ErrorState error={listQuery.error} />}

      {/* Cards: flat grid or grouped accordions per viewMode (S1246). */}
      {!listQuery.isLoading && !listQuery.error && (
        <>
          {deliverables.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">{hasActiveFilters ? 'No deliverables match your filters.' : 'No deliverables yet. Agent outputs will appear here.'}</p>
            </div>
          ) : viewMode === 'grouped' ? (
            /* Session 1246 — Grouped view (Rigby design lock): recency
               sections (Today / This Week / This Month / Older) → category
               accordions with cheap aggregation summary headers. */
            <div className="space-y-6">
              {groupedView.map(section => (
                <div key={section.recency} className="space-y-2">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 pl-1">
                    {RECENCY_LABELS[section.recency]}{' '}
                    <span className="text-gray-600 normal-case font-normal">
                      · {section.categories.reduce((s, c) => s + c.summary.count, 0)} items
                    </span>
                  </h3>
                  <div className="space-y-2">
                    {section.categories.map(group => {
                      const groupKey = `${section.recency}:${group.key}`
                      const isOpen = expandedGroups.has(groupKey)
                      const isUncat = group.key === UNCATEGORIZED_KEY
                      return (
                        <div
                          key={groupKey}
                          className={cn(
                            'bg-dark-card border rounded-lg overflow-hidden',
                            isUncat
                              ? 'border-amber-500/30'
                              : 'border-dark-border'
                          )}
                        >
                          {/* Header (click to expand/collapse) */}
                          <button
                            onClick={() => toggleGroup(groupKey)}
                            className="w-full text-left px-4 py-3 hover:bg-dark-border/30 transition-colors"
                          >
                            <div className="flex items-center justify-between gap-3">
                              <div className="flex items-center gap-2 min-w-0 flex-1">
                                <ChevronRight
                                  size={14}
                                  className={cn(
                                    'flex-shrink-0 text-gray-500 transition-transform',
                                    isOpen && 'rotate-90'
                                  )}
                                />
                                <span
                                  className={cn(
                                    'text-sm font-medium truncate',
                                    isUncat ? 'text-amber-300' : 'text-white'
                                  )}
                                >
                                  {group.label}
                                </span>
                                <span className="text-xs text-gray-500 flex-shrink-0">
                                  · {group.summary.count}
                                </span>
                              </div>
                              <div className="flex items-center gap-2 flex-shrink-0">
                                {/* Status mini-badges */}
                                {Object.entries(group.summary.statusCounts)
                                  .sort((a, b) => b[1] - a[1])
                                  .slice(0, 3)
                                  .map(([status, count]) => (
                                    <span
                                      key={status}
                                      className={cn(
                                        'px-1.5 py-0.5 rounded text-[10px]',
                                        STATUS_COLORS[status] || 'bg-gray-700 text-gray-300'
                                      )}
                                      title={`${count} ${status}`}
                                    >
                                      {status} {count}
                                    </span>
                                  ))}
                                <span className="text-xs text-gray-500 hidden sm:inline">
                                  latest {formatTimeShort(group.summary.latestIso)}
                                </span>
                              </div>
                            </div>
                            {/* Top tags + view-all link (only when collapsed
                                for a clean expanded state). */}
                            {!isOpen && (
                              <div className="flex items-center justify-between gap-2 mt-1.5 pl-6">
                                <div className="flex flex-wrap gap-1 min-w-0">
                                  {group.summary.topTags.map(({ tag, count }) => (
                                    <span
                                      key={tag}
                                      className="px-1 py-0.5 bg-gray-800 text-gray-500 rounded text-[10px]"
                                    >
                                      {tag} · {count}
                                    </span>
                                  ))}
                                </div>
                                <span
                                  role="button"
                                  tabIndex={0}
                                  onClick={(e) => { e.stopPropagation(); viewAllInGroup(group.label) }}
                                  onKeyDown={(e) => {
                                    if (e.key === 'Enter' || e.key === ' ') {
                                      e.stopPropagation()
                                      viewAllInGroup(group.label)
                                    }
                                  }}
                                  className="text-[11px] text-primary-400 hover:text-primary-300 transition-colors flex-shrink-0 cursor-pointer"
                                  title={
                                    isUncat
                                      ? 'Flip to flat list (no category filter — these have no category to filter on).'
                                      : `Switch to flat list filtered by category="${group.label}".`
                                  }
                                >
                                  View all →
                                </span>
                              </div>
                            )}
                          </button>
                          {/* Expanded cards. The card grid mirrors the flat
                              view's layout so users don't relearn anything
                              when toggling. */}
                          {isOpen && (
                            <div className="p-3 border-t border-dark-border bg-dark-bg/40">
                              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                                {group.items.map(renderCard)}
                              </div>
                              {!isUncat && (
                                <div className="flex justify-end mt-3">
                                  <span
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => viewAllInGroup(group.label)}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter' || e.key === ' ') viewAllInGroup(group.label)
                                    }}
                                    className="text-xs text-primary-400 hover:text-primary-300 transition-colors cursor-pointer"
                                  >
                                    View all {group.label} in flat list →
                                  </span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              ))}
              {/* Footer note: the perPage cap is honest about what's loaded. */}
              {deliverables.length >= perPage && (
                <p className="text-[11px] text-gray-600 text-center pt-2">
                  Showing the most-recent {perPage} items in grouped view.
                  Switch to Flat list to browse the full history.
                </p>
              )}
            </div>
          ) : (
            /* Flat list — original card grid. */
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
              {deliverables.map(renderCard)}
            </div>
          )}

          {/* Pagination — flat mode only; grouped view shows all loaded items in one window. */}
          {viewMode === 'flat' && pagination && pagination.total_pages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t border-dark-border mt-4">
              <span className="text-xs text-gray-500">
                Page {pagination.page} of {pagination.total_pages} ({pagination.total_items?.toLocaleString()} items)
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(1)}
                  disabled={pagination.page <= 1}
                  className="px-2 py-1 rounded text-xs text-gray-400 hover:text-white hover:bg-dark-border disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  First
                </button>
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={!pagination.has_previous}
                  className="p-1 rounded text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronLeft size={16} />
                </button>
                {/* Page number buttons */}
                {(() => {
                  const current = pagination.page
                  const total = pagination.total_pages
                  const pages: number[] = []
                  const start = Math.max(1, current - 2)
                  const end = Math.min(total, current + 2)
                  for (let i = start; i <= end; i++) pages.push(i)
                  return pages.map(p => (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={cn(
                        'w-7 h-7 rounded text-xs font-medium',
                        p === current
                          ? 'bg-primary-600 text-white'
                          : 'text-gray-400 hover:text-white hover:bg-dark-border'
                      )}
                    >
                      {p}
                    </button>
                  ))
                })()}
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={!pagination.has_next}
                  className="p-1 rounded text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronRight size={16} />
                </button>
                <button
                  onClick={() => setPage(pagination.total_pages)}
                  disabled={pagination.page >= pagination.total_pages}
                  className="px-2 py-1 rounded text-xs text-gray-400 hover:text-white hover:bg-dark-border disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  Last
                </button>
                {/* Jump to page */}
                <div className="flex items-center gap-1 ml-2">
                  <span className="text-xs text-gray-500">Go to</span>
                  <input
                    type="number"
                    min={1}
                    max={pagination.total_pages}
                    className="w-14 px-2 py-1 bg-dark-bg border border-dark-border rounded text-xs text-center"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const val = parseInt((e.target as HTMLInputElement).value)
                        if (val >= 1 && val <= pagination.total_pages) setPage(val)
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Session 1246 — Informational panels (Stats / Workspace Breakdown /
          Today's Queue) moved below the work surface per Chris ask. Still
          load-bearing for hygiene + today's-attention items, but they're
          context, not the headline. */}

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-dark-card border border-dark-border rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-white">{stats.total}</div>
            <div className="text-xs text-gray-400">Total</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-primary-400">{stats.saved}</div>
            <div className="text-xs text-gray-400">Saved</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.templates}</div>
            <div className="text-xs text-gray-400">Templates</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-green-400">{stats.recent_7d}</div>
            <div className="text-xs text-gray-400">Last 7 days</div>
          </div>
        </div>
      )}

      {/* Session 1091 Sprint B — Workspace breakdown card.
          Surfaces per-workspace volume + dedicated orphan/unassigned counts so
          Chris can see hygiene at a glance. orphan_count should always read 0
          post-PR #1965; if it ever rises, the factory's Unassigned-bucket
          fallback has regressed. unassigned_count is informational — it's
          legitimate volume that landed in the triage bucket and may want
          reassignment. */}
      {stats?.by_workspace && stats.by_workspace.length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-200">Workspace Breakdown</h4>
            <div className="flex items-center gap-2 text-xs">
              {typeof stats.orphan_count === 'number' && (
                <span
                  className={cn(
                    'px-1.5 py-0.5 rounded',
                    stats.orphan_count > 0
                      ? 'bg-red-500/20 text-red-300'
                      : 'bg-gray-700 text-gray-400'
                  )}
                  title="Deliverables with no workspace assignment (workspace_id IS NULL). Should always be 0 post-PR #1965; if it rises, the factory fallback regressed."
                >
                  Orphans: {stats.orphan_count}
                </span>
              )}
              {typeof stats.unassigned_count === 'number' && stats.unassigned_count > 0 && (
                <span
                  className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300"
                  title="Deliverables in the per-user 'Unassigned' triage bucket (created without explicit workspace assignment). Reassign as needed."
                >
                  Unassigned: {stats.unassigned_count}
                </span>
              )}
            </div>
          </div>
          <div className="space-y-1.5">
            {stats.by_workspace.slice(0, 10).map((row) => (
              <div
                key={row.workspace_id ?? 'orphan'}
                className="flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span
                    className={cn(
                      'px-1.5 py-0.5 rounded truncate max-w-[200px]',
                      row.is_orphan
                        ? 'bg-red-500/20 text-red-300'
                        : row.is_unassigned
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-blue-500/15 text-blue-300'
                    )}
                  >
                    {row.workspace_name}
                  </span>
                </div>
                <span className="text-gray-400 tabular-nums">{row.count}</span>
              </div>
            ))}
            {stats.by_workspace.length > 10 && (
              <div className="text-xs text-gray-500 pt-1">
                +{stats.by_workspace.length - 10} more workspaces
              </div>
            )}
          </div>
        </div>
      )}

      {/* Today Queue */}
      {recentDeliverables.length > 0 && (
        <div className="bg-gradient-to-r from-emerald-900/20 to-blue-900/20 border border-emerald-500/20 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Inbox size={16} className="text-emerald-400" />
            <h4 className="text-sm font-semibold text-emerald-400">Today's Queue</h4>
            <span className="text-xs text-gray-500">{recentDeliverables.length} items need attention</span>
          </div>
          <div className="space-y-2">
            {recentDeliverables.slice(0, 5).map(d => (
              <div key={d.id} className="flex items-center justify-between gap-3 bg-dark-card/50 rounded-lg px-3 py-2">
                <button
                  onClick={() => setSelectedId(d.id)}
                  className="flex-1 text-left min-w-0"
                >
                  <span className="text-sm text-white truncate block">{d.title}</span>
                  <span className="text-xs text-gray-500">{d.agent_name} &middot; {formatDate(d.created_at)}</span>
                </button>
                <div className="flex gap-1 flex-shrink-0">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleQuickAction(d.id, 'action_taken') }}
                    className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 transition-colors"
                    title="Mark as acted on"
                  >
                    <CheckCircle2 size={12} />
                    Done
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleQuickAction(d.id, 'task_created') }}
                    className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition-colors"
                    title="Create follow-up task"
                  >
                    <ListChecks size={12} />
                    Task
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
