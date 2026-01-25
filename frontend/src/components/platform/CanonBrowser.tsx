/**
 * Session 815: Canon Browser Component
 *
 * Browse canon documents by category.
 * Part of the Platform Command Center - Knowledge tab.
 */

import { useState } from 'react'
import { BookOpen, Folder, FileText, Clock, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/cn'

interface CanonDocument {
  path: string
  name: string
  title: string
  category: string
  size_bytes: number
  modified_at: string
  lines: number
}

interface CanonData {
  documents: CanonDocument[]
  total: number
  by_category: Record<string, number>
  filtered_count: number
}

interface CanonBrowserProps {
  data?: CanonData
  isLoading?: boolean
  onSelectDocument?: (doc: CanonDocument) => void
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

export function CanonBrowser({ data, isLoading, onSelectDocument }: CanonBrowserProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-8 w-24 bg-gray-700 rounded animate-pulse flex-shrink-0"></div>
          ))}
        </div>
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-700 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!data || data.total === 0) {
    return (
      <div className="card border border-dashed border-gray-700 text-center py-8">
        <BookOpen className="mx-auto text-gray-500 mb-3" size={32} />
        <p className="text-gray-400">No canon documents yet</p>
        <p className="text-sm text-gray-500 mt-1">
          Promote valuable docs to canon via the Knowledge Pipeline
        </p>
      </div>
    )
  }

  const categories = Object.entries(data.by_category).sort(([a], [b]) => a.localeCompare(b))
  const filteredDocs = selectedCategory
    ? data.documents.filter(d => d.category === selectedCategory)
    : data.documents

  return (
    <div className="space-y-4">
      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
        <button
          onClick={() => setSelectedCategory(null)}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0',
            selectedCategory === null
              ? 'bg-accent-purple text-white'
              : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white'
          )}
        >
          <BookOpen size={14} />
          All ({data.total})
        </button>
        {categories.map(([cat, count]) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0 capitalize',
              selectedCategory === cat
                ? 'bg-accent-purple text-white'
                : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white'
            )}
          >
            <Folder size={14} />
            {cat} ({count})
          </button>
        ))}
      </div>

      {/* Documents List */}
      <div className="space-y-2">
        {filteredDocs.map((doc) => (
          <div
            key={doc.path}
            onClick={() => onSelectDocument?.(doc)}
            className={cn(
              'p-4 bg-gray-800/50 hover:bg-gray-800 rounded-lg border border-gray-700/50 cursor-pointer transition-colors group'
            )}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 min-w-0">
                <div className="h-8 w-8 rounded bg-accent-purple/20 flex items-center justify-center flex-shrink-0">
                  <FileText className="text-accent-purple" size={16} />
                </div>
                <div className="min-w-0">
                  <h4 className="text-sm font-medium text-white truncate group-hover:text-accent-purple transition-colors">
                    {doc.title}
                  </h4>
                  <p className="text-xs text-gray-500 truncate">{doc.path}</p>
                </div>
              </div>
              <ChevronRight
                size={16}
                className="text-gray-500 group-hover:text-accent-purple transition-colors flex-shrink-0 mt-1"
              />
            </div>

            <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Clock size={12} />
                {formatDate(doc.modified_at)}
              </span>
              <span>{formatBytes(doc.size_bytes)}</span>
              <span>{doc.lines.toLocaleString()} lines</span>
              {doc.category !== 'root' && (
                <span className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-400 capitalize">
                  {doc.category}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredDocs.length === 0 && selectedCategory && (
        <div className="text-center py-8 text-gray-500">
          No documents in {selectedCategory}
        </div>
      )}
    </div>
  )
}
