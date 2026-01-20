/**
 * Session 784: Documentation Index Browser
 *
 * Powered by docs/_index.json - shows all documentation with:
 * - Status badges (active, superseded, deprecated, draft)
 * - Outbound/inbound link counts
 * - Orphan warnings
 * - Full-text search
 * - Detail panel with cross-references
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { docsIndexApi, DocsDetailResponse } from '@/lib/api'
import {
  AlertTriangle,
  ArrowRight,
  Book,
  CheckCircle,
  ChevronRight,
  ExternalLink,
  FileText,
  Filter,
  Link2,
  RefreshCw,
  Search,
  XCircle,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import Breadcrumb from '@/components/Breadcrumb'

// Status badge colors
const statusColors: Record<string, string> = {
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  superseded: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  deprecated: 'bg-red-500/20 text-red-400 border-red-500/30',
  draft: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  unknown: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

// Status icons
const statusIcons: Record<string, typeof CheckCircle> = {
  active: CheckCircle,
  superseded: AlertTriangle,
  deprecated: XCircle,
  draft: FileText,
  unknown: FileText,
}

interface DocDetailsProps {
  docPath: string
  onClose: () => void
}

function DocDetailsPanel({ docPath, onClose }: DocDetailsProps) {
  const { data, isLoading, error } = useQuery<DocsDetailResponse>({
    queryKey: ['docs-detail', docPath],
    queryFn: async () => {
      const res = await docsIndexApi.detail(docPath)
      return res.data
    },
    enabled: !!docPath,
  })

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="p-6 text-red-400">
        <XCircle className="w-6 h-6 mb-2" />
        <p>Failed to load document details</p>
      </div>
    )
  }

  const doc = data.document
  const StatusIcon = statusIcons[doc.status] || FileText

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold truncate" title={doc.path}>
            {doc.title || doc.path.split('/').pop()}
          </h3>
          <p className="text-sm text-gray-400 truncate">{doc.path}</p>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-700 rounded ml-2"
        >
          <XCircle className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Status & Stats */}
        <div className="flex flex-wrap gap-2">
          <span className={cn(
            'inline-flex items-center gap-1 px-2 py-1 text-xs rounded border',
            statusColors[doc.status]
          )}>
            <StatusIcon className="w-3 h-3" />
            {doc.status}
          </span>
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded border border-gray-600 text-gray-400">
            {doc.lines} lines
          </span>
          {doc.type && (
            <span className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded border border-purple-500/30 text-purple-400">
              {doc.type}
            </span>
          )}
          {doc.has_frontmatter && (
            <span className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded border border-cyan-500/30 text-cyan-400">
              frontmatter
            </span>
          )}
        </div>

        {/* Orphan Warning */}
        {data.is_orphan && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
            <div>
              <p className="text-yellow-400 font-medium">Orphan Document</p>
              <p className="text-xs text-gray-400">This document has no inbound or outbound links</p>
            </div>
          </div>
        )}

        {/* Subsystems */}
        {doc.subsystems.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Subsystems</h4>
            <div className="flex flex-wrap gap-1">
              {doc.subsystems.map((sub) => (
                <span
                  key={sub}
                  className="px-2 py-0.5 text-xs rounded bg-gray-700 text-gray-300"
                >
                  {sub}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Outbound Links */}
        <div>
          <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
            <ArrowRight className="w-4 h-4" />
            Outbound Links ({doc.outbound_links.length})
          </h4>
          {doc.outbound_links.length === 0 ? (
            <p className="text-xs text-gray-500">No outbound links</p>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {doc.outbound_links.map((link, i) => (
                <div
                  key={i}
                  className="p-2 bg-gray-800/50 rounded border border-gray-700 hover:border-cyan-500/30 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-cyan-400 truncate" title={link.target}>
                      {link.target}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      {link.occurrences}x
                    </span>
                  </div>
                  {link.snippets.length > 0 && (
                    <p className="text-xs text-gray-500 mt-1 truncate">
                      {link.snippets[0]}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Inbound Links */}
        <div>
          <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
            <Link2 className="w-4 h-4" />
            Inbound Links ({data.inbound_count})
          </h4>
          {data.inbound_links.length === 0 ? (
            <p className="text-xs text-gray-500">No documents link to this one</p>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {data.inbound_links.map((link, i) => (
                <div
                  key={i}
                  className="p-2 bg-gray-800/50 rounded border border-gray-700 hover:border-green-500/30 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-green-400 truncate" title={link.source}>
                      {link.title || link.source}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      {link.occurrences}x
                    </span>
                  </div>
                  {link.snippets.length > 0 && (
                    <p className="text-xs text-gray-500 mt-1 truncate">
                      {link.snippets[0]}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <a
          href={`/docs/${doc.path}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          Open Document
        </a>
      </div>
    </div>
  )
}

export default function DocsIndexPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)

  // Fetch docs index
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['docs-index', statusFilter, typeFilter, searchQuery],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (statusFilter) params.status = statusFilter
      if (typeFilter) params.type = typeFilter
      if (searchQuery) params.search = searchQuery
      const res = await docsIndexApi.index(params)
      return res.data
    },
  })

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ['docs-stats'],
    queryFn: async () => {
      const res = await docsIndexApi.stats()
      return res.data
    },
  })

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="p-6">
        <Breadcrumb currentPage="Documentation Index" />
      </div>

      <div className="flex h-[calc(100vh-120px)]">
        {/* Main Content */}
        <div className={cn(
          'flex-1 flex flex-col min-w-0 transition-all duration-300',
          selectedDoc ? 'pr-0' : 'pr-0'
        )}>
          {/* Header */}
          <div className="px-6 pb-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20">
                  <Book className="w-8 h-8 text-cyan-400" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold">Documentation Index</h1>
                  <p className="text-gray-400">
                    Session 784: Cognitive Build Ledger Browser
                  </p>
                </div>
              </div>
              <button
                onClick={() => refetch()}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
                Refresh
              </button>
            </div>

            {/* Stats Row */}
            {statsData && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
                <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="text-2xl font-bold text-cyan-400">{statsData.total_documents}</div>
                  <div className="text-xs text-gray-400">Total Docs</div>
                </div>
                <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="text-2xl font-bold text-green-400">{statsData.by_status?.active || 0}</div>
                  <div className="text-xs text-gray-400">Active</div>
                </div>
                <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="text-2xl font-bold text-purple-400">{statsData.graph.total_links}</div>
                  <div className="text-xs text-gray-400">Cross-Links</div>
                </div>
                <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="text-2xl font-bold text-red-400">{statsData.graph.broken_links}</div>
                  <div className="text-xs text-gray-400">Broken Links</div>
                </div>
                <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="text-2xl font-bold text-yellow-400">{statsData.graph.orphan_docs}</div>
                  <div className="text-xs text-gray-400">Orphans</div>
                </div>
              </div>
            )}

            {/* Filters */}
            <div className="flex flex-wrap gap-3">
              {/* Search */}
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Status Filter */}
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="pl-10 pr-8 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500 appearance-none cursor-pointer"
                >
                  <option value="">All Statuses</option>
                  {data?.filters.statuses.map((status) => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>

              {/* Type Filter */}
              <div className="relative">
                <FileText className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="pl-10 pr-8 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500 appearance-none cursor-pointer"
                >
                  <option value="">All Types</option>
                  {data?.filters.types.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Results Count */}
          {data && (
            <div className="px-6 py-2 text-sm text-gray-400 border-y border-gray-800">
              Showing {data.filtered_count} of {data.total_count} documents
              {data.version && <span className="ml-2 text-gray-600">• Index v{data.version}</span>}
            </div>
          )}

          {/* Document List */}
          <div className="flex-1 overflow-y-auto px-6 py-2">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-cyan-400" />
              </div>
            ) : data?.documents.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No documents found</p>
              </div>
            ) : (
              <div className="space-y-2">
                {data?.documents.map((doc) => {
                  const StatusIcon = statusIcons[doc.status] || FileText
                  const isOrphan = doc.inbound_links_count === 0 && doc.outbound_links.length === 0
                  return (
                    <button
                      key={doc.path}
                      onClick={() => setSelectedDoc(doc.path)}
                      className={cn(
                        'w-full text-left p-3 rounded-lg border transition-all',
                        selectedDoc === doc.path
                          ? 'bg-cyan-500/10 border-cyan-500/50'
                          : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                      )}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={cn(
                              'inline-flex items-center gap-1 px-1.5 py-0.5 text-xs rounded border',
                              statusColors[doc.status]
                            )}>
                              <StatusIcon className="w-3 h-3" />
                              {doc.status}
                            </span>
                            {doc.type && (
                              <span className="text-xs text-purple-400">{doc.type}</span>
                            )}
                            {isOrphan && (
                              <span className="text-xs text-yellow-500 flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" />
                                orphan
                              </span>
                            )}
                          </div>
                          <h3 className="font-medium truncate" title={doc.title}>
                            {doc.title || doc.path.split('/').pop()}
                          </h3>
                          <p className="text-sm text-gray-500 truncate">{doc.path}</p>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-400 flex-shrink-0">
                          <span className="flex items-center gap-1" title="Outbound links">
                            <ArrowRight className="w-3 h-3" />
                            {doc.outbound_links.length}
                          </span>
                          <span className="flex items-center gap-1" title="Inbound links">
                            <Link2 className="w-3 h-3" />
                            {doc.inbound_links_count}
                          </span>
                          <ChevronRight className="w-4 h-4" />
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Detail Panel */}
        {selectedDoc && (
          <div className="w-96 border-l border-gray-700 bg-gray-800/30 flex-shrink-0">
            <DocDetailsPanel
              docPath={selectedDoc}
              onClose={() => setSelectedDoc(null)}
            />
          </div>
        )}
      </div>
    </div>
  )
}
