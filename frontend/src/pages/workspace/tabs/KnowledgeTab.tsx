// Session 825: Knowledge Tab
// Extracted from WorkspacePage.tsx for modular architecture
// Session 833: Document viewer with markdown rendering

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, FileText, ClipboardList, ExternalLink, Loader2, X, AlertCircle } from 'lucide-react'
import { platformApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Document {
  path: string
  title: string
  category?: string
  status?: string
}

export function KnowledgeTab() {
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)

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

  const {
    data: auditsData,
    isLoading: loadingAudits,
    isError: auditsError,
    refetch: refetchAudits,
  } = useQuery({
    queryKey: ['platform-audits'],
    queryFn: async () => {
      const res = await platformApi.audits()
      return res.data
    },
  })

  // Session 833: Combined error handling
  const hasError = canonError || playbooksError || auditsError
  const handleRetry = () => {
    if (canonError) refetchCanon()
    if (playbooksError) refetchPlaybooks()
    if (auditsError) refetchAudits()
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
        </div>
        {loadingCanon ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary-400" size={24} />
          </div>
        ) : (
          <div className="space-y-2">
            {(canonData?.documents || []).slice(0, 10).map((doc: Document) => (
              <div
                key={doc.path}
                className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer"
                onClick={() => setSelectedDoc(doc)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText size={14} className="text-gray-400" />
                    <span className="text-sm">{doc.title || doc.path}</span>
                  </div>
                  {doc.category && (
                    <span className="text-xs px-2 py-0.5 bg-primary-500/20 text-primary-400 rounded">
                      {doc.category}
                    </span>
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
        </div>
        {loadingPlaybooks ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary-400" size={24} />
          </div>
        ) : (
          <div className="grid gap-2">
            {(playbooksData?.playbooks || []).map((playbook: { name: string; path: string; description?: string }) => (
              <div
                key={playbook.path}
                className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors"
              >
                <h4 className="font-medium text-sm">{playbook.name}</h4>
                {playbook.description && (
                  <p className="text-xs text-gray-400 mt-1">{playbook.description}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* System Audits */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <ClipboardList className="text-accent-amber" size={18} />
          <h3 className="text-md font-semibold uppercase">System Audits</h3>
          {auditsData?.audits && (
            <span className="text-xs text-gray-500">({auditsData.audits.length})</span>
          )}
        </div>
        {loadingAudits ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary-400" size={24} />
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {(auditsData?.audits || []).slice(0, 10).map((audit: { path: string; title: string; audit_type?: string }) => (
              <div
                key={audit.path}
                className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm">{audit.title}</span>
                  {audit.audit_type && (
                    <span className="text-xs px-2 py-0.5 bg-accent-amber/20 text-accent-amber rounded">
                      {audit.audit_type}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Full Documentation Index Link */}
      <div className="card">
        <a
          href="/docs-index"
          className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors"
        >
          <div>
            <h4 className="font-medium">Full Documentation Index</h4>
            <p className="text-sm text-gray-400 mt-1">
              Browse all 1,500+ documentation files with cross-reference graph
            </p>
          </div>
          <ExternalLink size={20} className="text-primary-400" />
        </a>
      </div>

      {/* Document Preview Modal */}
      {selectedDoc && (
        <DocumentViewerModal
          doc={selectedDoc}
          onClose={() => setSelectedDoc(null)}
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
