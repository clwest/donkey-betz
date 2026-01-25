/**
 * Session 819: Deliverables Marketplace - Library Panel
 *
 * Shows saved deliverables and templates:
 * - Saved deliverables list
 * - Templates section
 * - Quick filters by type/category
 * - Remove from library action
 */

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Bookmark, Layout, Search, Loader2, FolderOpen,
  FileText, Image, Video, Music, Code, BarChart3,
  BookmarkX
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { Deliverable } from './DeliverableCard'

interface LibraryPanelProps {
  onDeliverableClick?: (deliverable: Deliverable) => void
}

// API functions
async function fetchSavedDeliverables(): Promise<Deliverable[]> {
  const response = await fetch('/api/deliverables/?saved=true&per_page=100', {
    credentials: 'include'
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to fetch saved deliverables')
  return data.deliverables
}

async function fetchTemplates(): Promise<Deliverable[]> {
  const response = await fetch('/api/deliverables/?template=true&per_page=100', {
    credentials: 'include'
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to fetch templates')
  return data.deliverables
}

async function unsaveDeliverable(id: string): Promise<void> {
  const response = await fetch(`/api/deliverables/${id}/unsave/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to unsave')
}

const TYPE_ICONS: Record<string, React.ElementType> = {
  document: FileText,
  image: Image,
  video: Video,
  audio: Music,
  code: Code,
  analysis: BarChart3,
}

export function LibraryPanel({ onDeliverableClick }: LibraryPanelProps) {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'saved' | 'templates'>('saved')
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('')

  // Queries
  const { data: savedDeliverables = [], isLoading: isLoadingSaved } = useQuery({
    queryKey: ['library-saved'],
    queryFn: fetchSavedDeliverables
  })

  const { data: templates = [], isLoading: isLoadingTemplates } = useQuery({
    queryKey: ['library-templates'],
    queryFn: fetchTemplates
  })

  // Mutation
  const unsaveMutation = useMutation({
    mutationFn: unsaveDeliverable,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['library-saved'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    }
  })

  // Filter items based on search and type
  const filterItems = (items: Deliverable[]) => {
    return items.filter(item => {
      const matchesSearch = !searchQuery ||
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.agent_name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesType = !typeFilter || item.deliverable_type === typeFilter
      return matchesSearch && matchesType
    })
  }

  const displayItems = activeTab === 'saved'
    ? filterItems(savedDeliverables)
    : filterItems(templates)

  const isLoading = activeTab === 'saved' ? isLoadingSaved : isLoadingTemplates

  // Get unique types for filter
  const allItems = [...savedDeliverables, ...templates]
  const types = [...new Set(allItems.map(d => d.deliverable_type))]

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-zinc-700/50">
        <div className="flex items-center gap-3 mb-3">
          <FolderOpen className="w-5 h-5 text-amber-400" />
          <h3 className="text-lg font-medium text-zinc-100">Library</h3>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 mb-3">
          <button
            onClick={() => setActiveTab('saved')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'saved'
                ? 'bg-blue-500/20 text-blue-400'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50'
            )}
          >
            <Bookmark className="w-4 h-4" />
            Saved
            <span className="px-1.5 py-0.5 text-xs bg-zinc-700 rounded-full">
              {savedDeliverables.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('templates')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              activeTab === 'templates'
                ? 'bg-indigo-500/20 text-indigo-400'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50'
            )}
          >
            <Layout className="w-4 h-4" />
            Templates
            <span className="px-1.5 py-0.5 text-xs bg-zinc-700 rounded-full">
              {templates.length}
            </span>
          </button>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search library..."
              className="w-full pl-9 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {types.length > 1 && (
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              {types.map(type => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-48">
            <Loader2 className="w-6 h-6 text-zinc-400 animate-spin" />
          </div>
        ) : displayItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-zinc-500">
            {activeTab === 'saved' ? (
              <>
                <Bookmark className="w-12 h-12 mb-3 opacity-50" />
                <p className="text-lg font-medium">No saved items</p>
                <p className="text-sm mt-1">
                  {searchQuery ? 'Try a different search' : 'Save deliverables to access them here'}
                </p>
              </>
            ) : (
              <>
                <Layout className="w-12 h-12 mb-3 opacity-50" />
                <p className="text-lg font-medium">No templates</p>
                <p className="text-sm mt-1">
                  {searchQuery ? 'Try a different search' : 'Convert deliverables to templates'}
                </p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {displayItems.map(item => (
              <LibraryItem
                key={item.id}
                deliverable={item}
                onClick={() => onDeliverableClick?.(item)}
                onRemove={activeTab === 'saved'
                  ? () => unsaveMutation.mutate(item.id)
                  : undefined}
                isRemoving={unsaveMutation.isPending}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function LibraryItem({
  deliverable,
  onClick,
  onRemove,
  isRemoving
}: {
  deliverable: Deliverable
  onClick: () => void
  onRemove?: () => void
  isRemoving?: boolean
}) {
  const TypeIcon = TYPE_ICONS[deliverable.deliverable_type] || FileText

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 bg-zinc-800/50 rounded-lg',
        'hover:bg-zinc-800 transition-colors cursor-pointer group'
      )}
      onClick={onClick}
    >
      <div className="p-2 bg-zinc-700/50 rounded-lg text-zinc-400">
        <TypeIcon className="w-4 h-4" />
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-medium text-zinc-200 truncate">
          {deliverable.title}
        </h4>
        <div className="flex items-center gap-2 text-xs text-zinc-500 mt-0.5">
          <span>{deliverable.agent_name}</span>
          {deliverable.category && (
            <>
              <span>|</span>
              <span>{deliverable.category}</span>
            </>
          )}
        </div>
      </div>

      {/* Quality indicator */}
      <div className="flex items-center gap-2">
        <div
          className={cn(
            'w-2 h-2 rounded-full',
            deliverable.quality_score >= 0.7 ? 'bg-green-400' :
            deliverable.quality_score >= 0.4 ? 'bg-yellow-400' : 'bg-red-400'
          )}
          title={`Quality: ${Math.round(deliverable.quality_score * 100)}%`}
        />

        {onRemove && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onRemove()
            }}
            disabled={isRemoving}
            className="p-1.5 text-zinc-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
            title="Remove from library"
          >
            <BookmarkX className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}

export default LibraryPanel
