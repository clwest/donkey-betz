/**
 * Session 816: Audits Browser Component
 *
 * Browse system audits by type.
 * Part of the Platform Command Center - Knowledge tab.
 */

import { useState } from 'react'
import { FileSearch, Folder, ChevronRight, Clock, ExternalLink, AlertTriangle, Database, RefreshCw, Archive, FileText } from 'lucide-react'
import { cn } from '@/lib/cn'

interface Audit {
  path: string
  name: string
  title: string
  summary: string
  audit_type: string
  size_bytes: number
  modified_at: string
}

interface AuditData {
  audits: Audit[]
  total: number
  by_type: Record<string, number>
  filtered_count: number
}

interface AuditsBrowserProps {
  data?: AuditData
  isLoading?: boolean
  onSelectAudit?: (audit: Audit) => void
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// Audit type styling
const AUDIT_TYPE_CONFIG: Record<string, { color: string; icon: typeof FileSearch; label: string }> = {
  session: { color: '#22c55e', icon: RefreshCw, label: 'Session' },
  system: { color: '#06b6d4', icon: FileSearch, label: 'System' },
  integration: { color: '#f59e0b', icon: AlertTriangle, label: 'Integration' },
  database: { color: '#8b5cf6', icon: Database, label: 'Database' },
  archive: { color: '#64748b', icon: Archive, label: 'Archive' },
  other: { color: '#94a3b8', icon: FileText, label: 'Other' },
}

function getAuditTypeConfig(type: string) {
  return AUDIT_TYPE_CONFIG[type] || AUDIT_TYPE_CONFIG.other
}

export function AuditsBrowser({ data, isLoading, onSelectAudit }: AuditsBrowserProps) {
  const [selectedType, setSelectedType] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-8 w-24 bg-gray-700 rounded animate-pulse flex-shrink-0"></div>
          ))}
        </div>
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-700 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!data || data.total === 0) {
    return (
      <div className="card border border-dashed border-gray-700 text-center py-8">
        <FileSearch className="mx-auto text-gray-500 mb-3" size={32} />
        <p className="text-gray-400">No audits found</p>
        <p className="text-sm text-gray-500 mt-1">
          System audits will appear here as they're generated
        </p>
      </div>
    )
  }

  const types = Object.entries(data.by_type).sort(([,a], [,b]) => b - a)
  const filteredAudits = selectedType
    ? data.audits.filter(a => a.audit_type === selectedType)
    : data.audits

  return (
    <div className="space-y-4">
      {/* Type Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
        <button
          onClick={() => setSelectedType(null)}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0',
            selectedType === null
              ? 'bg-accent-cyan text-white'
              : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white'
          )}
        >
          <FileSearch size={14} />
          All ({data.total})
        </button>
        {types.map(([type, count]) => {
          const config = getAuditTypeConfig(type)
          const Icon = config.icon
          return (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0',
                selectedType === type
                  ? 'bg-accent-cyan text-white'
                  : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white'
              )}
            >
              <Icon size={14} />
              {config.label} ({count})
            </button>
          )
        })}
      </div>

      {/* Audits List */}
      <div className="space-y-2">
        {filteredAudits.map((audit) => {
          const config = getAuditTypeConfig(audit.audit_type)
          const Icon = config.icon

          return (
            <div
              key={audit.path}
              onClick={() => onSelectAudit?.(audit)}
              className="p-4 bg-gray-800/50 hover:bg-gray-800 rounded-lg border border-gray-700/50 cursor-pointer transition-colors group"
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div
                  className="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: `${config.color}20` }}
                >
                  <Icon size={20} style={{ color: config.color }} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-medium text-white group-hover:text-accent-cyan transition-colors truncate">
                      {audit.title}
                    </h4>
                    <span
                      className="text-xs px-2 py-0.5 rounded flex-shrink-0"
                      style={{
                        backgroundColor: `${config.color}20`,
                        color: config.color,
                      }}
                    >
                      {config.label}
                    </span>
                  </div>

                  {audit.summary && (
                    <p className="text-xs text-gray-500 line-clamp-2 mb-2">
                      {audit.summary}
                    </p>
                  )}

                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock size={12} />
                      {formatDate(audit.modified_at)}
                    </span>
                    <span>{formatSize(audit.size_bytes)}</span>
                    <span className="text-gray-600 truncate max-w-[200px]">{audit.name}</span>
                  </div>
                </div>

                {/* Arrow */}
                <ChevronRight
                  size={16}
                  className="text-gray-500 group-hover:text-accent-cyan transition-colors flex-shrink-0"
                />
              </div>
            </div>
          )
        })}
      </div>

      {filteredAudits.length === 0 && selectedType && (
        <div className="text-center py-8 text-gray-500">
          No {getAuditTypeConfig(selectedType).label.toLowerCase()} audits found
        </div>
      )}

      {/* Summary Stats */}
      <div className="pt-4 border-t border-gray-700/50">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            Showing {filteredAudits.length} of {data.total} audits
          </span>
          <a
            href="/docs-index?folder=audits"
            className="flex items-center gap-1 text-accent-cyan hover:text-accent-cyan/80 transition-colors"
          >
            View in Docs Index
            <ExternalLink size={12} />
          </a>
        </div>
      </div>
    </div>
  )
}
