// Session 1009: Deliverables Library Tab
// Browse, search, and manage agent-produced deliverables

import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
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
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { deliverablesApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'
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
  const [searchInput, setSearchInput] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // ---- Queries ----
  // Note: workspace filter removed — PA-created and system deliverables have
  // workspace_id=None, so filtering by workspace hides them from the list.

  const statsQuery = useQuery({
    queryKey: ['deliverables-stats'],
    queryFn: () => deliverablesApi.stats().then(r => r.data),
  })

  const typesQuery = useQuery({
    queryKey: ['deliverables-types'],
    queryFn: () => deliverablesApi.types().then(r => r.data),
  })

  const listQuery = useQuery({
    queryKey: ['deliverables-list', page, filters],
    queryFn: () => deliverablesApi.list({
      ...filters,
      page,
      per_page: 20,
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
  const deliverables: Deliverable[] = listQuery.data?.deliverables ?? []
  const pagination: Pagination | null = listQuery.data?.pagination ?? null
  const detail: Deliverable | null = detailQuery.data?.deliverable ?? null
  const hasActiveFilters = !!(filters.type || filters.category || filters.agent || filters.search || filters.saved || filters.template || filters.source)

  // Today queue: recent deliverables (last 24h) that haven't been acted on
  const recentDeliverables = deliverables.filter(d => {
    const age = Date.now() - new Date(d.created_at).getTime()
    return age < 24 * 60 * 60 * 1000 && !actedIds.has(d.id)
  })

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
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{detail.content || ''}</ReactMarkdown>
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

      {/* Cards Grid */}
      {!listQuery.isLoading && !listQuery.error && (
        <>
          {deliverables.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">{hasActiveFilters ? 'No deliverables match your filters.' : 'No deliverables yet. Agent outputs will appear here.'}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
              {deliverables.map((d) => (
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
              ))}
            </div>
          )}

          {/* Pagination */}
          {pagination && pagination.total_pages > 1 && (
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
    </div>
  )
}
