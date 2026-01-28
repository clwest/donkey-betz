// Session 825: Knowledge Tab
// Extracted from WorkspacePage.tsx for modular architecture
// Session 833: Document viewer with markdown rendering
// Session 840: Enhanced cards with metadata and onClick handlers for all sections
// Session 840: Replaced static audits with Audit Dashboard showing actionable findings

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { BookOpen, FileText, ClipboardList, Loader2, X, AlertCircle, Calendar, FileCode, Shield, CheckCircle, Clock, XCircle, ChevronDown } from 'lucide-react'
import { platformApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Session 840: Extended interfaces for full API response data
interface Document {
  path: string
  name?: string
  title: string
  category?: string
  description?: string
  summary?: string
  audit_type?: string
  size_bytes?: number
  modified_at?: string
  lines?: number
  status?: string
}

interface Playbook {
  path: string
  name: string
  title: string
  description?: string
  category: string
  size_bytes: number
  modified_at: string
}

// Session 840: Audit Finding interface from database
interface AuditFinding {
  id: string
  title: string
  description: string
  priority: string
  category: string
  status: string
  impact: string
  audit_report: {
    id: string
    title: string
  }
  recommendation: string
  assigned_agent: string
  fixed_by: string
  created_at: string
  updated_at: string
}

export function KnowledgeTab() {
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const [selectedFinding, setSelectedFinding] = useState<AuditFinding | null>(null)
  const [auditStatusFilter, setAuditStatusFilter] = useState<string>('open')
  const queryClient = useQueryClient()

  const {
    data: canonData,
    isLoading: loadingCanon,
    isError: canonError,
    error: canonErrorData,
    refetch: refetchCanon,
  } = useQuery({
    queryKey: ['platform-canon'],
    queryFn: async () => {
      const res = await platformApi.canon()
      return res.data
    },
  })

  const {
    data: playbooksData,
    isLoading: loadingPlaybooks,
    isError: playbooksError,
    refetch: refetchPlaybooks,
  } = useQuery({
    queryKey: ['platform-playbooks'],
    queryFn: async () => {
      const res = await platformApi.playbooks()
      return res.data
    },
  })

  // Session 840: Audit findings from database (replaces static files)
  const {
    data: auditSummary,
    isLoading: loadingAuditSummary,
  } = useQuery({
    queryKey: ['audit-findings-summary'],
    queryFn: async () => {
      const res = await platformApi.auditFindingsSummary()
      return res.data
    },
  })

  const {
    data: auditFindings,
    isLoading: loadingFindings,
    isError: findingsError,
    refetch: refetchFindings,
  } = useQuery({
    queryKey: ['audit-findings', auditStatusFilter],
    queryFn: async () => {
      const res = await platformApi.auditFindings({
        status: auditStatusFilter === 'all' ? undefined : auditStatusFilter,
        limit: 20
      })
      return res.data
    },
  })

  // Session 840: Mutation to update finding status
  const updateStatusMutation = useMutation({
    mutationFn: async ({ findingId, status, notes }: { findingId: string, status: string, notes?: string }) => {
      const res = await platformApi.auditFindingUpdateStatus(findingId, { status, notes })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit-findings'] })
      queryClient.invalidateQueries({ queryKey: ['audit-findings-summary'] })
      setSelectedFinding(null)
    },
  })

  // Session 833: Combined error handling
  const hasError = canonError || playbooksError || findingsError
  const handleRetry = () => {
    if (canonError) refetchCanon()
    if (playbooksError) refetchPlaybooks()
    if (findingsError) refetchFindings()
  }

  if (hasError) {
    return (
      <ErrorState
        error={canonErrorData as Error}
        onRetry={handleRetry}
        message="Failed to load knowledge data. Please check your connection and try again."
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Canon Documents */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="text-primary-400" size={18} />
          <h3 className="text-md font-semibold uppercase">Canon Documents</h3>
          {canonData?.documents && (
            <span className="text-xs text-gray-500">({canonData.documents.length})</span>
          )}
        </div>
        {loadingCanon ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary-400" size={24} />
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {(canonData?.documents || []).slice(0, 10).map((doc: Document) => (
              <div
                key={doc.path}
                className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer"
                onClick={() => setSelectedDoc(doc)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <FileText size={14} className="text-primary-400 shrink-0" />
                      <span className="text-sm truncate">{doc.title || doc.path}</span>
                    </div>
                  </div>
                  {doc.category && doc.category !== 'root' && (
                    <span className="text-xs px-2 py-0.5 bg-primary-500/20 text-primary-400 rounded ml-2 shrink-0">
                      {doc.category}
                    </span>
                  )}
                </div>
                {/* Metadata row */}
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  {doc.lines && <span>{doc.lines} lines</span>}
                  {doc.size_bytes && (
                    <>
                      {doc.lines && <span>•</span>}
                      <span>{(doc.size_bytes / 1024).toFixed(1)} KB</span>
                    </>
                  )}
                  {doc.modified_at && (
                    <>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Calendar size={10} />
                        {new Date(doc.modified_at).toLocaleDateString()}
                      </span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Playbooks */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <ClipboardList className="text-accent-green" size={18} />
          <h3 className="text-md font-semibold uppercase">Playbooks</h3>
          {playbooksData?.playbooks && (
            <span className="text-xs text-gray-500">({playbooksData.playbooks.length})</span>
          )}
        </div>
        {loadingPlaybooks ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary-400" size={24} />
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {(playbooksData?.playbooks || []).slice(0, 10).map((playbook: Playbook) => (
              <div
                key={playbook.path}
                className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer"
                onClick={() => setSelectedDoc({ path: playbook.path, title: playbook.title, category: playbook.category })}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <FileCode size={14} className="text-accent-green shrink-0" />
                      <h4 className="font-medium text-sm truncate">{playbook.title}</h4>
                    </div>
                    {playbook.description && (
                      <p className="text-xs text-gray-400 mt-1 line-clamp-2">{playbook.description}</p>
                    )}
                  </div>
                  {playbook.category && playbook.category !== 'root' && (
                    <span className="text-xs px-2 py-0.5 bg-accent-green/20 text-accent-green rounded ml-2 shrink-0">
                      {playbook.category}
                    </span>
                  )}
                </div>
                {/* Metadata row */}
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <span>{(playbook.size_bytes / 1024).toFixed(1)} KB</span>
                  {playbook.modified_at && (
                    <>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Calendar size={10} />
                        {new Date(playbook.modified_at).toLocaleDateString()}
                      </span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Session 840: Audit Dashboard - Actionable Findings from Database */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Shield className="text-accent-amber" size={18} />
            <h3 className="text-md font-semibold uppercase">Audit Findings</h3>
          </div>
          {/* Summary Stats */}
          {auditSummary?.summary && (
            <div className="flex items-center gap-3 text-xs">
              <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded">
                P0: {auditSummary.summary.by_priority?.P0 || 0}
              </span>
              <span className="px-2 py-1 bg-orange-500/20 text-orange-400 rounded">
                P1: {auditSummary.summary.by_priority?.P1 || 0}
              </span>
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                Open: {auditSummary.summary.by_status?.open || 0}
              </span>
              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded">
                Fixed: {auditSummary.summary.by_status?.fixed || 0}
              </span>
            </div>
          )}
        </div>

        {/* Status Filter Tabs */}
        <div className="flex gap-1 mb-4 p-1 bg-gray-800/50 rounded-lg">
          {[
            { value: 'open', label: 'Open', icon: AlertCircle },
            { value: 'in_progress', label: 'In Progress', icon: Clock },
            { value: 'fixed', label: 'Fixed', icon: CheckCircle },
            { value: 'deferred', label: 'Deferred', icon: XCircle },
            { value: 'all', label: 'All', icon: ClipboardList },
          ].map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              onClick={() => setAuditStatusFilter(value)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                auditStatusFilter === value
                  ? 'bg-primary-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon size={12} />
              {label}
            </button>
          ))}
        </div>

        {/* Findings List */}
        {loadingFindings || loadingAuditSummary ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary-400" size={24} />
          </div>
        ) : (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {auditFindings?.findings?.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle size={32} className="mx-auto mb-2 opacity-50" />
                <p>No {auditStatusFilter === 'all' ? '' : auditStatusFilter} findings</p>
              </div>
            ) : (
              auditFindings?.findings?.map((finding: AuditFinding) => (
                <div
                  key={finding.id}
                  className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer"
                  onClick={() => setSelectedFinding(finding)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                          finding.priority === 'P0' ? 'bg-red-500/20 text-red-400' :
                          finding.priority === 'P1' ? 'bg-orange-500/20 text-orange-400' :
                          finding.priority === 'P2' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {finding.priority}
                        </span>
                        <span className="text-sm font-medium truncate">{finding.title}</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1 line-clamp-2">{finding.description}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1 shrink-0">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        finding.status === 'open' ? 'bg-blue-500/20 text-blue-400' :
                        finding.status === 'fixed' ? 'bg-green-500/20 text-green-400' :
                        finding.status === 'in_progress' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {finding.status}
                      </span>
                      <span className="text-xs text-gray-500">{finding.category}</span>
                    </div>
                  </div>
                  {/* Source audit */}
                  <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                    <span>From: {finding.audit_report?.title || 'Unknown audit'}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Total count */}
        {auditFindings?.count && (
          <div className="mt-3 pt-3 border-t border-dark-border text-xs text-gray-500 text-center">
            Showing {auditFindings.findings?.length || 0} of {auditFindings.count} findings
          </div>
        )}
      </div>

      {/* Session 857: Documentation info shown inline instead of external link */}
      <div className="card">
        <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
          <div>
            <h4 className="font-medium">Documentation Index</h4>
            <p className="text-sm text-gray-400 mt-1">
              1,500+ documentation files available in canon and playbooks above
            </p>
          </div>
          <BookOpen size={20} className="text-primary-400" />
        </div>
      </div>

      {/* Document Preview Modal */}
      {selectedDoc && (
        <DocumentViewerModal
          doc={selectedDoc}
          onClose={() => setSelectedDoc(null)}
        />
      )}

      {/* Session 840: Finding Detail Modal */}
      {selectedFinding && (
        <FindingDetailModal
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
          onUpdateStatus={(status, notes) => {
            updateStatusMutation.mutate({
              findingId: selectedFinding.id,
              status,
              notes,
            })
          }}
          isUpdating={updateStatusMutation.isPending}
        />
      )}
    </div>
  )
}

// Session 833: Document Viewer Modal Component
function DocumentViewerModal({ doc, onClose }: { doc: Document; onClose: () => void }) {
  const {
    data: docData,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['doc-content', doc.path],
    queryFn: async () => {
      const res = await platformApi.docContent(doc.path)
      return res.data
    },
    enabled: !!doc.path,
  })

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border shrink-0">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold truncate">{docData?.metadata?.title || doc.title || doc.path}</h3>
            <p className="text-xs text-gray-500 truncate mt-1">{doc.path}</p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-primary-400" size={32} />
              <span className="ml-3 text-gray-400">Loading document...</span>
            </div>
          ) : isError ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="h-12 w-12 rounded-full bg-red-500/20 flex items-center justify-center mb-4">
                <AlertCircle className="text-red-400" size={24} />
              </div>
              <h4 className="text-lg font-medium text-white mb-2">Failed to Load Document</h4>
              <p className="text-sm text-gray-400 max-w-md">
                {(error as Error)?.message || 'An error occurred while loading the document'}
              </p>
            </div>
          ) : docData?.content ? (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {docData.content}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <FileText size={48} className="mx-auto mb-4 opacity-50" />
              <p>No content available</p>
            </div>
          )}
        </div>

        {/* Footer with metadata */}
        {docData?.metadata && (
          <div className="flex items-center gap-4 px-4 py-2 border-t border-dark-border bg-gray-900/50 text-xs text-gray-500 shrink-0">
            <span>{docData.metadata.lines} lines</span>
            <span>•</span>
            <span>{(docData.metadata.size_bytes / 1024).toFixed(1)} KB</span>
            {docData.metadata.modified_at && (
              <>
                <span>•</span>
                <span>Modified: {new Date(docData.metadata.modified_at).toLocaleDateString()}</span>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Session 840: Finding Detail Modal Component
function FindingDetailModal({
  finding,
  onClose,
  onUpdateStatus,
  isUpdating,
}: {
  finding: AuditFinding
  onClose: () => void
  onUpdateStatus: (status: string, notes?: string) => void
  isUpdating: boolean
}) {
  const [showStatusMenu, setShowStatusMenu] = useState(false)

  const statusActions = [
    { value: 'in_progress', label: 'Mark In Progress', color: 'text-yellow-400' },
    { value: 'fixed', label: 'Mark as Fixed', color: 'text-green-400' },
    { value: 'deferred', label: 'Defer', color: 'text-gray-400' },
    { value: 'wontfix', label: "Won't Fix", color: 'text-red-400' },
  ]

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-4 border-b border-dark-border shrink-0">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-xs px-2 py-1 rounded font-medium ${
                finding.priority === 'P0' ? 'bg-red-500/20 text-red-400' :
                finding.priority === 'P1' ? 'bg-orange-500/20 text-orange-400' :
                finding.priority === 'P2' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-gray-500/20 text-gray-400'
              }`}>
                {finding.priority}
              </span>
              <span className={`text-xs px-2 py-1 rounded ${
                finding.status === 'open' ? 'bg-blue-500/20 text-blue-400' :
                finding.status === 'fixed' ? 'bg-green-500/20 text-green-400' :
                finding.status === 'in_progress' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-gray-500/20 text-gray-400'
              }`}>
                {finding.status}
              </span>
              <span className="text-xs px-2 py-1 bg-gray-700 rounded text-gray-300">
                {finding.category}
              </span>
            </div>
            <h3 className="font-semibold text-lg">{finding.title}</h3>
            <p className="text-xs text-gray-500 mt-1">
              From: {finding.audit_report?.title || 'Unknown audit'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Description */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Description</h4>
            <p className="text-sm text-gray-400">{finding.description}</p>
          </div>

          {/* Recommendation */}
          {finding.recommendation && (
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-2">Recommendation</h4>
              <p className="text-sm text-gray-400">{finding.recommendation}</p>
            </div>
          )}

          {/* Impact */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Impact</h4>
            <span className={`text-xs px-2 py-1 rounded ${
              finding.impact === 'critical' ? 'bg-red-500/20 text-red-400' :
              finding.impact === 'high' ? 'bg-orange-500/20 text-orange-400' :
              finding.impact === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-gray-500/20 text-gray-400'
            }`}>
              {finding.impact}
            </span>
          </div>

          {/* Assignment info */}
          {(finding.assigned_agent || finding.fixed_by) && (
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-2">Assignment</h4>
              <div className="text-sm text-gray-400 space-y-1">
                {finding.assigned_agent && <p>Assigned to: {finding.assigned_agent}</p>}
                {finding.fixed_by && <p>Fixed by: {finding.fixed_by}</p>}
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="text-xs text-gray-500 pt-4 border-t border-dark-border">
            <p>Created: {new Date(finding.created_at).toLocaleString()}</p>
            <p>Updated: {new Date(finding.updated_at).toLocaleString()}</p>
          </div>
        </div>

        {/* Footer with actions */}
        <div className="flex items-center justify-between p-4 border-t border-dark-border bg-gray-900/50 shrink-0">
          <div className="relative">
            <button
              onClick={() => setShowStatusMenu(!showStatusMenu)}
              disabled={isUpdating}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
            >
              {isUpdating ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <ChevronDown size={16} />
              )}
              Update Status
            </button>

            {showStatusMenu && (
              <div className="absolute bottom-full left-0 mb-2 bg-dark-card border border-dark-border rounded-lg shadow-xl overflow-hidden min-w-[160px]">
                {statusActions.map(({ value, label, color }) => (
                  <button
                    key={value}
                    onClick={() => {
                      onUpdateStatus(value)
                      setShowStatusMenu(false)
                    }}
                    className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-700 transition-colors ${color}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
