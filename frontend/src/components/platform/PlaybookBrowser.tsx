/**
 * Session 815: Playbook Browser Component
 *
 * Browse playbooks by category.
 * Part of the Platform Command Center - Knowledge tab.
 */

import { useState } from 'react'
import { FileText, Folder, ChevronRight, Clock, Plus } from 'lucide-react'
import { cn } from '@/lib/cn'

interface Playbook {
  path: string
  name: string
  title: string
  description: string
  category: string
  size_bytes: number
  modified_at: string
}

interface PlaybookData {
  playbooks: Playbook[]
  total: number
  by_category: Record<string, number>
  filtered_count: number
}

interface PlaybookBrowserProps {
  data?: PlaybookData
  isLoading?: boolean
  onSelectPlaybook?: (playbook: Playbook) => void
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

// Category icons/colors
const CATEGORY_COLORS: Record<string, string> = {
  creator: '#22c55e',
  devops: '#06b6d4',
  marketing: '#f59e0b',
  development: '#8b5cf6',
  default: '#64748b',
}

export function PlaybookBrowser({ data, isLoading, onSelectPlaybook }: PlaybookBrowserProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-8 w-24 bg-gray-700 rounded animate-pulse flex-shrink-0"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-700 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!data || data.total === 0) {
    return (
      <div className="card border border-dashed border-gray-700 text-center py-8">
        <FileText className="mx-auto text-gray-500 mb-3" size={32} />
        <p className="text-gray-400">No playbooks created yet</p>
        <p className="text-sm text-gray-500 mt-1">
          Playbooks help standardize processes across the platform
        </p>
        <button className="mt-4 flex items-center gap-2 px-4 py-2 bg-accent-cyan/20 hover:bg-accent-cyan/30 text-accent-cyan rounded-lg mx-auto transition-colors">
          <Plus size={16} />
          Create First Playbook
        </button>
      </div>
    )
  }

  const categories = Object.entries(data.by_category).sort(([a], [b]) => a.localeCompare(b))
  const filteredPlaybooks = selectedCategory
    ? data.playbooks.filter(p => p.category === selectedCategory)
    : data.playbooks

  return (
    <div className="space-y-4">
      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
        <button
          onClick={() => setSelectedCategory(null)}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0',
            selectedCategory === null
              ? 'bg-accent-cyan text-white'
              : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white'
          )}
        >
          <FileText size={14} />
          All ({data.total})
        </button>
        {categories.map(([cat, count]) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0 capitalize',
              selectedCategory === cat
                ? 'bg-accent-cyan text-white'
                : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white'
            )}
          >
            <Folder size={14} />
            {cat} ({count})
          </button>
        ))}
      </div>

      {/* Playbooks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredPlaybooks.map((playbook) => {
          const color = CATEGORY_COLORS[playbook.category] || CATEGORY_COLORS.default

          return (
            <div
              key={playbook.path}
              onClick={() => onSelectPlaybook?.(playbook)}
              className="p-4 bg-gray-800/50 hover:bg-gray-800 rounded-lg border border-gray-700/50 cursor-pointer transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div
                  className="h-10 w-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${color}20` }}
                >
                  <FileText size={20} style={{ color }} />
                </div>
                <span className="text-xs px-2 py-0.5 rounded capitalize" style={{
                  backgroundColor: `${color}20`,
                  color: color,
                }}>
                  {playbook.category}
                </span>
              </div>

              <h4 className="text-sm font-medium text-white group-hover:text-accent-cyan transition-colors mb-1">
                {playbook.title}
              </h4>

              {playbook.description && (
                <p className="text-xs text-gray-500 line-clamp-2 mb-3">
                  {playbook.description}
                </p>
              )}

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <Clock size={12} />
                  {formatDate(playbook.modified_at)}
                </span>
                <ChevronRight
                  size={14}
                  className="text-gray-500 group-hover:text-accent-cyan transition-colors"
                />
              </div>
            </div>
          )
        })}
      </div>

      {filteredPlaybooks.length === 0 && selectedCategory && (
        <div className="text-center py-8 text-gray-500">
          No playbooks in {selectedCategory}
        </div>
      )}
    </div>
  )
}
