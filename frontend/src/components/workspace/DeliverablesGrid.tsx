/**
 * Session 819: Deliverables Marketplace - Grid View
 *
 * Displays deliverables in a responsive grid with:
 * - Filtering by type, category, saved status
 * - Search functionality
 * - Pagination
 * - Stats summary
 */

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Search, Loader2, Package, Bookmark, Layout,
  ChevronLeft, ChevronRight, RefreshCw
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { DeliverableCard, Deliverable } from './DeliverableCard'

interface DeliverableStats {
  total: number
  saved: number
  templates: number
  recent_7d: number
  by_type: Array<{ deliverable_type: string; count: number }>
  by_category: Array<{ category: string; count: number }>
  by_agent: Array<{ agent_name: string; count: number }>
}

interface DeliverablesGridProps {
  onDeliverableClick?: (deliverable: Deliverable) => void
  onTraceClick?: (deliverable: Deliverable) => void
}

// API functions
async function fetchDeliverables(params: {
  page?: number
  per_page?: number
  type?: string
  category?: string
  saved?: boolean
  template?: boolean
  search?: string
}): Promise<{
  deliverables: Deliverable[]
  pagination: {
    page: number
    per_page: number
    total_pages: number
    total_items: number
    has_next: boolean
    has_previous: boolean
  }
}> {
  const queryParams = new URLSearchParams()
  if (params.page) queryParams.append('page', params.page.toString())
  if (params.per_page) queryParams.append('per_page', params.per_page.toString())
  if (params.type) queryParams.append('type', params.type)
  if (params.category) queryParams.append('category', params.category)
  if (params.saved !== undefined) queryParams.append('saved', params.saved.toString())
  if (params.template !== undefined) queryParams.append('template', params.template.toString())
  if (params.search) queryParams.append('search', params.search)

  const response = await fetch(`/api/deliverables/?${queryParams}`, {
    credentials: 'include'
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to fetch deliverables')
  return data
}

async function fetchDeliverableStats(): Promise<DeliverableStats> {
  const response = await fetch('/api/deliverables/stats/', {
    credentials: 'include'
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to fetch stats')
  return data.stats
}

async function saveDeliverable(id: string): Promise<void> {
  const response = await fetch(`/api/deliverables/${id}/save/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to save deliverable')
}

async function unsaveDeliverable(id: string): Promise<void> {
  const response = await fetch(`/api/deliverables/${id}/unsave/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to unsave deliverable')
}

async function cloneDeliverable(id: string): Promise<Deliverable> {
  const response = await fetch(`/api/deliverables/${id}/clone/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to clone deliverable')
  return data.deliverable
}

async function exportDeliverable(id: string, format: string): Promise<Blob> {
  const response = await fetch(`/api/deliverables/${id}/export/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ format })
  })
  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.error || 'Export failed')
  }
  return response.blob()
}

// Deliverable type options
const DELIVERABLE_TYPES = [
  { value: 'document', label: 'Documents' },
  { value: 'image', label: 'Images' },
  { value: 'video', label: 'Videos' },
  { value: 'audio', label: 'Audio' },
  { value: 'code', label: 'Code' },
  { value: 'analysis', label: 'Analysis' },
  { value: 'report', label: 'Reports' },
  { value: 'research', label: 'Research' },
  { value: 'strategy', label: 'Strategy' },
  { value: 'plan', label: 'Plans' },
]

export function DeliverablesGrid({
  onDeliverableClick,
  onTraceClick
}: DeliverablesGridProps) {
  const queryClient = useQueryClient()

  // Filter state
  const [page, setPage] = useState(1)
  const [perPage] = useState(12)
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [savedFilter, setSavedFilter] = useState<boolean | undefined>(undefined)
  const [searchQuery, setSearchQuery] = useState('')

  // Query for deliverables
  const {
    data: deliverablesData,
    isLoading: isLoadingDeliverables,
    refetch: refetchDeliverables
  } = useQuery({
    queryKey: ['deliverables', page, perPage, typeFilter, categoryFilter, savedFilter, searchQuery],
    queryFn: () => fetchDeliverables({
      page,
      per_page: perPage,
      type: typeFilter || undefined,
      category: categoryFilter || undefined,
      saved: savedFilter,
      search: searchQuery || undefined
    })
  })

  // Query for stats
  const { data: stats } = useQuery({
    queryKey: ['deliverables-stats'],
    queryFn: fetchDeliverableStats
  })

  // Mutations
  const saveMutation = useMutation({
    mutationFn: saveDeliverable,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    }
  })

  const unsaveMutation = useMutation({
    mutationFn: unsaveDeliverable,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    }
  })

  const cloneMutation = useMutation({
    mutationFn: cloneDeliverable,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    }
  })

  // Extract unique categories from stats
  const categories = useMemo(() => {
    if (!stats?.by_category) return []
    return stats.by_category.map(c => c.category).filter(Boolean)
  }, [stats])

  const deliverables = deliverablesData?.deliverables || []
  const pagination = deliverablesData?.pagination

  // Handle export
  const handleExport = async (deliverable: Deliverable) => {
    try {
      const blob = await exportDeliverable(deliverable.id, 'html')
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${deliverable.slug}.html`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with Stats */}
      <div className="px-4 py-3 border-b border-zinc-700/50">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4">
            <h3 className="text-lg font-medium text-zinc-100 flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-400" />
              Deliverables
            </h3>
            {stats && (
              <div className="flex items-center gap-3 text-sm text-zinc-400">
                <span>{stats.total} total</span>
                <span className="text-zinc-600">|</span>
                <span className="flex items-center gap-1">
                  <Bookmark className="w-3.5 h-3.5" />
                  {stats.saved} saved
                </span>
                <span className="text-zinc-600">|</span>
                <span className="flex items-center gap-1">
                  <Layout className="w-3.5 h-3.5" />
                  {stats.templates} templates
                </span>
              </div>
            )}
          </div>

          <button
            onClick={() => refetchDeliverables()}
            className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setPage(1)
              }}
              placeholder="Search deliverables..."
              className="w-full pl-9 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value)
              setPage(1)
            }}
            className="px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            {DELIVERABLE_TYPES.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>

          {/* Category Filter */}
          {categories.length > 0 && (
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value)
                setPage(1)
              }}
              className="px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          )}

          {/* Saved Filter */}
          <button
            onClick={() => {
              setSavedFilter(savedFilter === true ? undefined : true)
              setPage(1)
            }}
            className={cn(
              'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors',
              savedFilter === true
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                : 'bg-zinc-800 border border-zinc-700 text-zinc-400 hover:text-zinc-200'
            )}
          >
            <Bookmark className="w-4 h-4" />
            Saved
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-auto p-4">
        {isLoadingDeliverables ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-6 h-6 text-zinc-400 animate-spin" />
          </div>
        ) : deliverables.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-zinc-500">
            <Package className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-lg font-medium">No deliverables found</p>
            <p className="text-sm mt-1">
              {searchQuery || typeFilter || categoryFilter || savedFilter
                ? 'Try adjusting your filters'
                : 'Agent outputs will appear here'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {deliverables.map(deliverable => (
              <DeliverableCard
                key={deliverable.id}
                deliverable={deliverable}
                onClick={() => onDeliverableClick?.(deliverable)}
                onSave={() => {
                  if (deliverable.is_saved) {
                    unsaveMutation.mutate(deliverable.id)
                  } else {
                    saveMutation.mutate(deliverable.id)
                  }
                }}
                onClone={() => cloneMutation.mutate(deliverable.id)}
                onExport={() => handleExport(deliverable)}
                onTrace={() => onTraceClick?.(deliverable)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <div className="px-4 py-3 border-t border-zinc-700/50 flex items-center justify-between">
          <span className="text-sm text-zinc-400">
            Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
            {Math.min(pagination.page * pagination.per_page, pagination.total_items)} of{' '}
            {pagination.total_items}
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={!pagination.has_previous}
              className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <span className="text-sm text-zinc-400">
              Page {pagination.page} of {pagination.total_pages}
            </span>

            <button
              onClick={() => setPage(p => Math.min(pagination.total_pages, p + 1))}
              disabled={!pagination.has_next}
              className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DeliverablesGrid
