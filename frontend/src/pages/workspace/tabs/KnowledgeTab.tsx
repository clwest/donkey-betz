// Session 825: Knowledge Tab
// Extracted from WorkspacePage.tsx for modular architecture

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, FileText, ClipboardList, ExternalLink, Loader2 } from 'lucide-react'
import { platformApi } from '@/lib/api'

interface Document {
  path: string
  title: string
  category?: string
  status?: string
}

export function KnowledgeTab() {
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)

  const { data: canonData, isLoading: loadingCanon } = useQuery({
    queryKey: ['platform-canon'],
    queryFn: async () => {
      const res = await platformApi.canon()
      return res.data
    },
  })

  const { data: playbooksData, isLoading: loadingPlaybooks } = useQuery({
    queryKey: ['platform-playbooks'],
    queryFn: async () => {
      const res = await platformApi.playbooks()
      return res.data
    },
  })

  const { data: auditsData, isLoading: loadingAudits } = useQuery({
    queryKey: ['platform-audits'],
    queryFn: async () => {
      const res = await platformApi.audits()
      return res.data
    },
  })

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
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setSelectedDoc(null)}
        >
          <div
            className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b border-dark-border">
              <h3 className="font-semibold">{selectedDoc.title || selectedDoc.path}</h3>
              <button
                onClick={() => setSelectedDoc(null)}
                className="text-gray-400 hover:text-white"
              >
                &times;
              </button>
            </div>
            <div className="p-4">
              <p className="text-sm text-gray-400">
                Document viewer will be implemented here.
              </p>
              <p className="text-xs text-gray-500 mt-2">Path: {selectedDoc.path}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
