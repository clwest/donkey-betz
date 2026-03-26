/**
 * Session 1077: Knowledge Tab — Complete Rewrite
 *
 * 7 sub-tabs:
 * 1. Search — Unified semantic search across all knowledge
 * 2. Ingest — URL + file upload with status tracking
 * 3. Documents — Library browser with filters
 * 4. Provenance — Citation tracking + "used by" lookup
 * 5. Playbooks — Curated operational guides
 * 6. Audit Findings — DB-backed findings dashboard
 * 7. RAG Health — Observability dashboard
 */

import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Search, Upload, FileText, GitBranch, BookOpen, Shield, Database,
  Loader2, X, AlertCircle, Calendar, CheckCircle, Clock, XCircle,
  ChevronDown, Zap, Activity, RefreshCw, AlertTriangle, Info,
  Target, Layers, Link, Globe, ExternalLink, Trash2, Tag,
  FileCode, ClipboardList,
} from 'lucide-react'
import { platformApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/cn'

type KnowledgeSubTab = 'search' | 'ingest' | 'documents' | 'provenance' | 'playbooks' | 'audits' | 'rag'

const subTabs: Array<{ id: KnowledgeSubTab; label: string; icon: typeof Search }> = [
  { id: 'search', label: 'Search', icon: Search },
  { id: 'ingest', label: 'Ingest', icon: Upload },
  { id: 'documents', label: 'Documents', icon: FileText },
  { id: 'provenance', label: 'Provenance', icon: GitBranch },
  { id: 'playbooks', label: 'Playbooks', icon: BookOpen },
  { id: 'audits', label: 'Audit Findings', icon: Shield },
  { id: 'rag', label: 'RAG Health', icon: Database },
]

// ============================================================================
// Sub-Tab 1: Search
// ============================================================================
function SearchPanel() {
  const [query, setQuery] = useState('')
  const [threshold, setThreshold] = useState(0.7)

  const searchMutation = useMutation({
    mutationFn: async (q: string) => {
      const r = await fetch('/api/v1/rag/semantic-search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          query: q,
          max_results: 20,
          similarity_threshold: threshold,
        }),
      })
      if (!r.ok) throw new Error(`Search failed: ${r.status}`)
      return r.json()
    },
  })

  const handleSearch = () => {
    if (query.trim()) searchMutation.mutate(query.trim())
  }

  const results = searchMutation.data?.results || []

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search all knowledge — documents, spider data, uploads..."
          className="flex-1 px-4 py-3 bg-gray-800 border border-dark-border rounded-lg text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
        />
        <button
          onClick={handleSearch}
          disabled={searchMutation.isPending || !query.trim()}
          className="px-6 py-3 bg-primary-500 hover:bg-primary-600 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
        >
          {searchMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
          Search
        </button>
      </div>

      <div className="flex items-center gap-3 text-xs text-gray-500">
        <span>Similarity threshold:</span>
        <input
          type="range"
          min={0.3}
          max={0.95}
          step={0.05}
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="w-32"
        />
        <span className="text-primary-400">{threshold.toFixed(2)}</span>
      </div>

      {searchMutation.isPending && (
        <div className="flex justify-center py-8"><Loader2 size={24} className="animate-spin text-primary-400" /></div>
      )}

      {searchMutation.isError && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
          Search failed: {(searchMutation.error as Error).message}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-gray-500">{results.length} results</p>
          {results.map((r: Record<string, string | number>, i: number) => (
            <div key={i} className="p-4 rounded-lg bg-dark-card border border-dark-border hover:border-gray-600 transition-colors">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white">{r.document_title || 'Untitled'}</p>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-3">{r.content || r.chunk_text}</p>
                </div>
                <span className={cn(
                  'px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap',
                  (r.similarity_score as number) >= 0.85 ? 'bg-green-500/20 text-green-400' :
                  (r.similarity_score as number) >= 0.75 ? 'bg-blue-500/20 text-blue-400' :
                  'bg-gray-500/20 text-gray-400'
                )}>
                  {((r.similarity_score as number) * 100).toFixed(0)}%
                </span>
              </div>
              {(r.context_before || r.context_after) && (
                <p className="text-xs text-gray-600 mt-2 italic truncate">
                  ...{r.context_before || ''} [{r.content ? 'match' : ''}] {r.context_after || ''}...
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {searchMutation.isSuccess && results.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Search size={32} className="mx-auto mb-2 opacity-50" />
          <p className="text-sm">No results found. Try a broader query or lower the threshold.</p>
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Sub-Tab 2: Ingest
// ============================================================================
function IngestPanel() {
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const queryClient = useQueryClient()

  const ingestUrlMutation = useMutation({
    mutationFn: async () => {
      const r = await fetch('/api/documents/ingest-url/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          url: url.trim(),
          title: title.trim() || undefined,
          generate_embeddings: true,
        }),
      })
      if (!r.ok) {
        const err = await r.json().catch(() => ({}))
        let message: string
        let code: string | null = err.error_code || null
        if (err.error_code === 'YOUTUBE_TRANSCRIPT_BLOCKED') {
          message = 'YouTube is blocking transcript requests from our server. An admin needs to configure a proxy to resolve this.'
        } else if (r.status === 503 && !err.error) {
          message = 'Server temporarily unavailable. Please wait a moment and try again.'
          code = 'EDGE_UNAVAILABLE'
        } else {
          message = err.error || `Ingest failed: ${r.status}`
        }
        const error = new Error(message)
        ;(error as any).errorCode = code
        ;(error as any).correlationId = err.correlation_id || null
        throw error
      }
      return r.json()
    },
    onSuccess: () => {
      setUrl('')
      setTitle('')
      queryClient.invalidateQueries({ queryKey: ['knowledge-documents'] })
    },
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const r = await fetch('/api/documents/ingest-file/', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      })
      if (!r.ok) {
        const err = await r.json().catch(() => ({}))
        throw new Error(err.error || `Upload failed: ${r.status}`)
      }
      return r.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge-documents'] })
    },
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) uploadMutation.mutate(file)
  }

  return (
    <div className="space-y-6">
      {/* URL Ingest */}
      <div className="p-5 rounded-xl bg-dark-card border border-dark-border">
        <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
          <Globe size={16} className="text-primary-400" />
          Ingest from URL
        </h3>
        <p className="text-xs text-gray-500 mb-3">
          Paste a web page, YouTube video, or PDF URL. Content will be extracted, chunked, and embedded for semantic search.
        </p>
        <div className="space-y-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article or YouTube URL..."
            className="w-full px-3 py-2 bg-gray-800 border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
          />
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title (optional — auto-detected from page)"
            className="w-full px-3 py-2 bg-gray-800 border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
          />
          <button
            onClick={() => ingestUrlMutation.mutate()}
            disabled={ingestUrlMutation.isPending || !url.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
          >
            {ingestUrlMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Link size={14} />}
            Ingest URL
          </button>
        </div>
        {ingestUrlMutation.isSuccess && (
          <div className="mt-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-sm text-green-400">
            <CheckCircle size={14} className="inline mr-1" />
            Ingested successfully — {ingestUrlMutation.data?.chunks_created || 0} chunks created, embeddings generating.
          </div>
        )}
        {ingestUrlMutation.isError && (
          <div className={`mt-3 p-3 rounded-lg text-sm ${
            (ingestUrlMutation.error as any)?.errorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED'
              ? 'bg-orange-500/10 border border-orange-500/20 text-orange-400'
              : (ingestUrlMutation.error as any)?.errorCode === 'EDGE_UNAVAILABLE'
              ? 'bg-yellow-500/10 border border-yellow-500/20 text-yellow-400'
              : 'bg-red-500/10 border border-red-500/20 text-red-400'
          }`}>
            {(ingestUrlMutation.error as Error).message}
            {(ingestUrlMutation.error as any)?.correlationId && (
              <div className="mt-1 text-xs opacity-60 font-mono">
                Correlation ID: {(ingestUrlMutation.error as any).correlationId}
              </div>
            )}
          </div>
        )}
      </div>

      {/* File Upload */}
      <div className="p-5 rounded-xl bg-dark-card border border-dark-border">
        <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
          <Upload size={16} className="text-blue-400" />
          Upload File
        </h3>
        <p className="text-xs text-gray-500 mb-3">
          Upload PDF, text, markdown, or code files. Content will be chunked and embedded automatically.
        </p>
        <label className="flex items-center justify-center gap-2 px-4 py-8 border-2 border-dashed border-dark-border rounded-xl hover:border-primary-500/50 transition-colors cursor-pointer">
          <input type="file" onChange={handleFileSelect} className="hidden" accept=".pdf,.txt,.md,.py,.js,.ts,.json,.csv,.html" />
          {uploadMutation.isPending ? (
            <><Loader2 size={20} className="animate-spin text-primary-400" /> Processing...</>
          ) : (
            <><Upload size={20} className="text-gray-500" /> <span className="text-sm text-gray-400">Click to select a file (PDF, TXT, MD, code files)</span></>
          )}
        </label>
        {uploadMutation.isSuccess && (
          <div className="mt-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-sm text-green-400">
            <CheckCircle size={14} className="inline mr-1" />
            Uploaded — {uploadMutation.data?.title || 'Document'} processed ({uploadMutation.data?.chunks_created || 0} chunks).
          </div>
        )}
        {uploadMutation.isError && (
          <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {(uploadMutation.error as Error).message}
          </div>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// Sub-Tab 3: Documents
// ============================================================================
function DocumentsPanel() {
  const [search, setSearch] = useState('')

  const docsQuery = useQuery({
    queryKey: ['knowledge-documents', search],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '30' })
      if (search) params.set('q', search)
      const r = await fetch(`/api/documents/?${params}`, { credentials: 'include' })
      if (!r.ok) return { documents: [], count: 0 }
      return r.json()
    },
    staleTime: 30000,
  })

  const docs = docsQuery.data?.documents || docsQuery.data?.results || []

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter documents..."
          className="flex-1 px-3 py-2 bg-gray-800 border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none"
        />
      </div>

      {docsQuery.isLoading && (
        <div className="flex justify-center py-8"><Loader2 size={24} className="animate-spin text-primary-400" /></div>
      )}

      <div className="space-y-2">
        {docs.length === 0 && !docsQuery.isLoading && (
          <div className="text-center py-12 text-gray-500">
            <FileText size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No documents yet. Use the Ingest tab to add knowledge.</p>
          </div>
        )}
        {docs.map((doc: Record<string, string | number>) => (
          <div key={doc.id as string} className="p-3 rounded-lg bg-dark-card border border-dark-border hover:border-gray-600 transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <FileText size={14} className="text-primary-400 shrink-0" />
                  <p className="text-sm font-medium text-white truncate">{doc.title || 'Untitled'}</p>
                </div>
                {doc.description && (
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{doc.description}</p>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {doc.document_type && (
                  <span className="px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-300">{doc.document_type}</span>
                )}
                {doc.status && (
                  <span className={cn(
                    'px-2 py-0.5 rounded text-xs',
                    doc.status === 'processed' ? 'bg-green-500/20 text-green-400' :
                    doc.status === 'processing' ? 'bg-blue-500/20 text-blue-400' :
                    doc.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  )}>{doc.status}</span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
              {doc.word_count && <span>{(doc.word_count as number).toLocaleString()} words</span>}
              {doc.source && <><span>&middot;</span><span>{doc.source}</span></>}
              {doc.created_at && <><span>&middot;</span><span>{new Date(doc.created_at as string).toLocaleDateString()}</span></>}
            </div>
          </div>
        ))}
      </div>

      {docsQuery.data?.count > docs.length && (
        <p className="text-xs text-gray-500 text-center">
          Showing {docs.length} of {docsQuery.data.count} documents
        </p>
      )}
    </div>
  )
}

// ============================================================================
// Sub-Tab 4: Provenance
// ============================================================================
function ProvenancePanel() {
  const violationsQuery = useQuery({
    queryKey: ['citation-violations'],
    queryFn: async () => {
      try {
        const r = await fetch('/api/citation-violations/?limit=20&is_resolved=false', { credentials: 'include' })
        if (!r.ok) return { violations: [], count: 0 }
        return r.json()
      } catch { return { violations: [], count: 0 } }
    },
    staleTime: 60000,
  })

  const violations = violationsQuery.data?.violations || violationsQuery.data?.results || []

  return (
    <div className="space-y-4">
      <div className="p-4 rounded-xl bg-dark-card border border-dark-border">
        <h3 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
          <AlertTriangle size={16} className="text-amber-400" />
          Unresolved Citation Violations
        </h3>
        <p className="text-xs text-gray-500 mb-3">
          Agents that produced output without sufficient source citations.
        </p>

        {violationsQuery.isLoading && (
          <div className="flex justify-center py-4"><Loader2 size={20} className="animate-spin text-primary-400" /></div>
        )}

        {violations.length === 0 && !violationsQuery.isLoading && (
          <div className="text-center py-6 text-gray-500">
            <CheckCircle size={24} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No unresolved citation violations.</p>
          </div>
        )}

        <div className="space-y-2">
          {violations.map((v: Record<string, string | number | boolean>) => (
            <div key={v.id as string} className="p-3 rounded-lg bg-gray-800/50 border border-dark-border">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white">{v.agent_name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{v.violation_type}: {v.provided_sources}/{v.required_sources} sources</p>
                  {v.task_description && (
                    <p className="text-xs text-gray-500 mt-1 truncate">{v.task_description}</p>
                  )}
                </div>
                <span className={cn(
                  'px-2 py-0.5 rounded text-xs',
                  v.was_blocked ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                )}>
                  {v.was_blocked ? 'Blocked' : 'Warning'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 rounded-xl bg-dark-card border border-dark-border">
        <h3 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
          <GitBranch size={16} className="text-purple-400" />
          Knowledge Attribution
        </h3>
        <p className="text-xs text-gray-500">
          Track which documents and spider sources are cited in agent outputs.
          This feature is built into the agent execution pipeline — every AgentResult
          includes a KnowledgeAttribution with spider_sources, confidence, and freshness.
        </p>
      </div>
    </div>
  )
}

// ============================================================================
// Sub-Tab 5: Playbooks (from original KnowledgeTab)
// ============================================================================
function PlaybooksPanel() {
  const [selectedDoc, setSelectedDoc] = useState<{ path: string; title: string; category?: string } | null>(null)

  const canonQuery = useQuery({
    queryKey: ['platform-canon'],
    queryFn: () => platformApi.canon().then(r => r.data),
  })

  const playbooksQuery = useQuery({
    queryKey: ['platform-playbooks'],
    queryFn: () => platformApi.playbooks().then(r => r.data),
  })

  const allDocs = [
    ...(canonQuery.data?.documents || []).map((d: Record<string, string>) => ({ ...d, section: 'Canon' })),
    ...(playbooksQuery.data?.playbooks || []).map((d: Record<string, string>) => ({ ...d, section: 'Playbook' })),
  ]

  const isLoading = canonQuery.isLoading || playbooksQuery.isLoading

  return (
    <div className="space-y-4">
      {isLoading ? (
        <div className="flex justify-center py-8"><Loader2 size={24} className="animate-spin text-primary-400" /></div>
      ) : (
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {allDocs.map((doc: Record<string, string>) => (
            <div
              key={doc.path}
              className="p-3 rounded-lg bg-dark-card border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
              onClick={() => setSelectedDoc({ path: doc.path, title: doc.title, category: doc.category })}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {doc.section === 'Canon' ? (
                    <BookOpen size={14} className="text-primary-400 shrink-0" />
                  ) : (
                    <FileCode size={14} className="text-green-400 shrink-0" />
                  )}
                  <span className="text-sm truncate">{doc.title || doc.path}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-400">{doc.section}</span>
                  {doc.category && doc.category !== 'root' && (
                    <span className="text-xs px-2 py-0.5 bg-primary-500/20 text-primary-400 rounded">{doc.category}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedDoc && (
        <DocumentViewerModal doc={selectedDoc} onClose={() => setSelectedDoc(null)} />
      )}
    </div>
  )
}

// ============================================================================
// Sub-Tab 6: Audit Findings (from original KnowledgeTab)
// ============================================================================
function AuditFindingsPanel() {
  const [statusFilter, setStatusFilter] = useState('open')
  const queryClient = useQueryClient()

  const summaryQuery = useQuery({
    queryKey: ['audit-findings-summary'],
    queryFn: () => platformApi.auditFindingsSummary().then(r => r.data),
  })

  const findingsQuery = useQuery({
    queryKey: ['audit-findings', statusFilter],
    queryFn: () => platformApi.auditFindings({
      status: statusFilter === 'all' ? undefined : statusFilter,
      limit: 20,
    }).then(r => r.data),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      platformApi.auditFindingUpdateStatus(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit-findings'] })
      queryClient.invalidateQueries({ queryKey: ['audit-findings-summary'] })
    },
  })

  const summary = summaryQuery.data?.summary
  const findings = findingsQuery.data?.findings || []

  return (
    <div className="space-y-4">
      {/* Stats */}
      {summary && (
        <div className="flex items-center gap-3 text-xs">
          <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded">P0: {summary.by_priority?.P0 || 0}</span>
          <span className="px-2 py-1 bg-orange-500/20 text-orange-400 rounded">P1: {summary.by_priority?.P1 || 0}</span>
          <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded">Open: {summary.by_status?.open || 0}</span>
          <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded">Fixed: {summary.by_status?.fixed || 0}</span>
        </div>
      )}

      {/* Status tabs */}
      <div className="flex gap-1 p-1 bg-gray-800/50 rounded-lg">
        {['open', 'in_progress', 'fixed', 'deferred', 'all'].map(s => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={cn(
              'px-3 py-1.5 rounded text-xs font-medium transition-colors',
              statusFilter === s ? 'bg-primary-500 text-white' : 'text-gray-400 hover:text-white'
            )}
          >
            {s === 'in_progress' ? 'In Progress' : s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {/* Findings */}
      {findingsQuery.isLoading ? (
        <div className="flex justify-center py-8"><Loader2 size={24} className="animate-spin text-primary-400" /></div>
      ) : findings.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircle size={32} className="mx-auto mb-2 opacity-50" />
          <p>No {statusFilter === 'all' ? '' : statusFilter} findings</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {findings.map((f: Record<string, string>) => (
            <div key={f.id} className="p-3 rounded-lg bg-dark-card border border-dark-border">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'text-xs px-1.5 py-0.5 rounded font-medium',
                      f.priority === 'P0' ? 'bg-red-500/20 text-red-400' :
                      f.priority === 'P1' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-gray-500/20 text-gray-400'
                    )}>{f.priority}</span>
                    <span className="text-sm font-medium truncate">{f.title}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{f.description}</p>
                </div>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded shrink-0',
                  f.status === 'open' ? 'bg-blue-500/20 text-blue-400' :
                  f.status === 'fixed' ? 'bg-green-500/20 text-green-400' :
                  'bg-gray-500/20 text-gray-400'
                )}>{f.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Sub-Tab 7: RAG Health (from original KnowledgeTab)
// ============================================================================
function RAGHealthPanel() {
  const queryClient = useQueryClient()

  const ragQuery = useQuery({
    queryKey: ['rag-observability-dashboard'],
    queryFn: () => platformApi.ragDashboard().then(r => r.data),
  })

  const classifyMutation = useMutation({
    mutationFn: (params?: { limit?: number; force?: boolean }) =>
      platformApi.ragRunClassification(params).then(r => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rag-observability-dashboard'] }),
  })

  const data = ragQuery.data

  if (ragQuery.isLoading) {
    return <div className="flex justify-center py-8"><Loader2 size={24} className="animate-spin text-primary-400" /></div>
  }

  if (!data) {
    return <div className="text-center py-8 text-gray-400"><Database size={32} className="mx-auto mb-2 opacity-50" /><p>No RAG data available</p></div>
  }

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
          <div className="text-2xl font-bold text-white">{data.summary?.total_documents || 0}</div>
          <div className="text-xs text-gray-400">Total Documents</div>
        </div>
        <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
          <div className="text-2xl font-bold text-red-400">{data.summary?.critical_documents || 0}</div>
          <div className="text-xs text-gray-400">Critical Docs</div>
        </div>
        <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
          <div className="text-2xl font-bold text-blue-400">{data.summary?.classified_documents || 0}</div>
          <div className="text-xs text-gray-400">Classified</div>
        </div>
        <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
          <div className="text-2xl font-bold text-purple-400">{data.summary?.budget_utilization?.toFixed(1) || 0}%</div>
          <div className="text-xs text-gray-400">Budget Used</div>
        </div>
      </div>

      {/* Health Indicators */}
      {data.health_indicators?.length > 0 && (
        <div className="space-y-2">
          {data.health_indicators.map((ind: Record<string, string>, idx: number) => (
            <div key={idx} className={cn(
              'flex items-start gap-2 p-2 rounded text-sm',
              ind.level === 'success' ? 'bg-green-500/10 text-green-400' :
              ind.level === 'warning' ? 'bg-amber-500/10 text-amber-400' :
              'bg-blue-500/10 text-blue-400'
            )}>
              {ind.level === 'success' ? <CheckCircle size={16} className="shrink-0 mt-0.5" /> :
               ind.level === 'warning' ? <AlertTriangle size={16} className="shrink-0 mt-0.5" /> :
               <Info size={16} className="shrink-0 mt-0.5" />}
              <span>{ind.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Classify button */}
      <button
        onClick={() => classifyMutation.mutate({ limit: 100 })}
        disabled={classifyMutation.isPending}
        className="flex items-center gap-2 px-3 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded text-sm transition-colors disabled:opacity-50"
      >
        {classifyMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
        Run Document Classification
      </button>
    </div>
  )
}

// ============================================================================
// Document Viewer Modal (shared)
// ============================================================================
function DocumentViewerModal({ doc, onClose }: { doc: { path: string; title: string; category?: string }; onClose: () => void }) {
  const docQuery = useQuery({
    queryKey: ['doc-content', doc.path],
    queryFn: () => platformApi.docContent(doc.path).then(r => r.data),
    enabled: !!doc.path,
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[85vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-dark-border shrink-0">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold truncate">{docQuery.data?.metadata?.title || doc.title}</h3>
            <p className="text-xs text-gray-500 truncate mt-1">{doc.path}</p>
          </div>
          <button onClick={onClose} className="ml-4 p-1 text-gray-400 hover:text-white rounded"><X size={20} /></button>
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          {docQuery.isLoading ? (
            <div className="flex justify-center py-12"><Loader2 size={32} className="animate-spin text-primary-400" /></div>
          ) : docQuery.data?.content ? (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{docQuery.data.content}</ReactMarkdown>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400"><FileText size={48} className="mx-auto mb-4 opacity-50" /><p>No content available</p></div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// Main KnowledgeTab
// ============================================================================
export function KnowledgeTab() {
  const [activeSubTab, setActiveSubTab] = useState<KnowledgeSubTab>('search')

  return (
    <div className="space-y-4">
      {/* Sub-tab nav */}
      <div className="flex gap-1 overflow-x-auto pb-1">
        {subTabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
              activeSubTab === tab.id
                ? 'bg-primary-500/20 text-primary-400'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Sub-tab content */}
      {activeSubTab === 'search' && <SearchPanel />}
      {activeSubTab === 'ingest' && <IngestPanel />}
      {activeSubTab === 'documents' && <DocumentsPanel />}
      {activeSubTab === 'provenance' && <ProvenancePanel />}
      {activeSubTab === 'playbooks' && <PlaybooksPanel />}
      {activeSubTab === 'audits' && <AuditFindingsPanel />}
      {activeSubTab === 'rag' && <RAGHealthPanel />}
    </div>
  )
}
