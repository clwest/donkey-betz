/**
 * Documents Page - RAG/Document Embedding System
 *
 * Session 732: Frontend UI for the RAG system with 7,239+ document embeddings
 * using pgvector for semantic search.
 *
 * Features:
 * - Document upload with drag-and-drop (PDF, DOCX, CSV, TXT, MD)
 * - URL ingestion (web pages)
 * - YouTube video transcription ingestion
 * - Semantic search interface
 * - Embedding statistics display
 * - Document management
 * - Collection organization
 */

import { useState, useCallback, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  FileText,
  Upload,
  Search,
  Database,
  Trash2,
  Sparkles,
  CheckCircle2,
  XCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Loader2,
  FileUp,
  Layers,
  Info,
  Zap,
  Link,
  Youtube,
  Globe,
  AlertTriangle,
  Mic,
} from 'lucide-react'
import { ragApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

// Types
interface RagStats {
  total_embeddings: number
  total_documents: number
  total_collections: number
  embedding_dimensions: number
  models: Array<{
    name: string
    count: number
    percentage: number
  }>
  storage_mb: number
  avg_chunks_per_doc: number
}

interface Document {
  id: string
  title: string
  filename?: string
  document_type: string
  source_url?: string
  collection_id?: string
  collection_name?: string
  embedding_count: number
  word_count: number
  created_at: string
  status: string
}

interface DocumentStats {
  total: number
  youtube: number
  urls: number
  pdfs: number
  processed: number
}

interface Collection {
  id: string
  name: string
  description?: string
  document_count: number
  embedding_count: number
  created_at: string
}

interface SearchResult {
  chunk_id: string
  content: string
  similarity_score: number
  document_id: string
  document_title: string
  metadata?: Record<string, unknown>
}

// Stat Card Component
function StatCard({
  icon: Icon,
  label,
  value,
  color = 'primary',
  subValue,
}: {
  icon: React.ElementType
  label: string
  value: string | number
  color?: 'primary' | 'green' | 'blue' | 'yellow' | 'purple' | 'red'
  subValue?: string
}) {
  const colorClasses = {
    primary: 'text-primary-400',
    green: 'text-green-400',
    blue: 'text-blue-400',
    yellow: 'text-yellow-400',
    purple: 'text-purple-400',
    red: 'text-red-400',
  }

  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-4">
      <div className={`flex items-center gap-2 ${colorClasses[color]} mb-1`}>
        <Icon className="h-4 w-4" />
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {subValue && <div className="text-xs text-gray-500 mt-1">{subValue}</div>}
    </div>
  )
}

// URL Ingestion Component
// Session 733: Crawl options interface
interface CrawlOptions {
  crawl_site?: boolean
  max_pages?: number
  max_depth?: number
  url_pattern?: string
}

function URLIngestZone({
  onIngestUrl,
  onWhisperFallback,
  isIngesting,
  isWhisperRunning,
}: {
  onIngestUrl: (url: string, title?: string, crawlOptions?: CrawlOptions) => void
  onWhisperFallback?: (url: string, title?: string) => void
  isIngesting: boolean
  isWhisperRunning?: boolean
}) {
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')

  // Session 733: Multi-page crawling settings
  const [crawlEnabled, setCrawlEnabled] = useState(false)
  const [maxPages, setMaxPages] = useState(10)
  const [maxDepth, setMaxDepth] = useState(2)
  const [urlPattern, setUrlPattern] = useState('')

  const isYouTube = url.includes('youtube.com') || url.includes('youtu.be')
  const isValidUrl = url.trim().startsWith('http://') || url.trim().startsWith('https://')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim() && isValidUrl) {
      const crawlOptions: CrawlOptions | undefined = crawlEnabled && !isYouTube ? {
        crawl_site: true,
        max_pages: maxPages,
        max_depth: maxDepth,
        url_pattern: urlPattern.trim() || undefined,
      } : undefined

      onIngestUrl(url.trim(), title.trim() || undefined, crawlOptions)
      setUrl('')
      setTitle('')
      setCrawlEnabled(false)
      setUrlPattern('')
    }
  }

  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-6">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Link className="h-5 w-5 text-primary-400" />
        Import from URL
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* URL Input */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            URL (Web Page or YouTube Video)
          </label>
          <div className="relative">
            {isYouTube ? (
              <Youtube className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-red-400" />
            ) : (
              <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            )}
            <input
              type="url"
              placeholder="https://example.com or https://youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-dark-border bg-dark-bg text-white placeholder-gray-500"
            />
          </div>
          {isYouTube && (
            <p className="text-xs text-red-400 mt-1 flex items-center gap-1">
              <Youtube className="h-3 w-3" />
              YouTube video detected - will extract transcript
            </p>
          )}
        </div>

        {/* Optional Title */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">
            Custom Title (optional)
          </label>
          <input
            type="text"
            placeholder="Leave empty to auto-detect"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-dark-border bg-dark-bg text-white placeholder-gray-500"
          />
        </div>

        {/* Session 733: Multi-Page Crawl Settings */}
        {!isYouTube && isValidUrl && (
          <div className="p-3 rounded-lg bg-dark-bg/50 border border-dark-border space-y-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={crawlEnabled}
                onChange={(e) => setCrawlEnabled(e.target.checked)}
                className="rounded border-dark-border bg-dark-bg text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-300">
                Crawl multiple pages (for documentation sites)
              </span>
            </label>

            {crawlEnabled && (
              <div className="space-y-3 pt-2 border-t border-dark-border">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Max Pages</label>
                    <select
                      value={maxPages}
                      onChange={(e) => setMaxPages(Number(e.target.value))}
                      className="w-full px-2 py-1 rounded border border-dark-border bg-dark-bg text-white text-sm"
                    >
                      <option value={5}>5 pages</option>
                      <option value={10}>10 pages</option>
                      <option value={20}>20 pages</option>
                      <option value={30}>30 pages</option>
                      <option value={50}>50 pages</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Max Depth</label>
                    <select
                      value={maxDepth}
                      onChange={(e) => setMaxDepth(Number(e.target.value))}
                      className="w-full px-2 py-1 rounded border border-dark-border bg-dark-bg text-white text-sm"
                    >
                      <option value={1}>1 level</option>
                      <option value={2}>2 levels</option>
                      <option value={3}>3 levels</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">
                    URL Pattern Filter (optional regex)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., /tutorial/ or /docs/api/"
                    value={urlPattern}
                    onChange={(e) => setUrlPattern(e.target.value)}
                    className="w-full px-2 py-1 rounded border border-dark-border bg-dark-bg text-white text-sm placeholder-gray-600"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Only crawl URLs matching this pattern
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isIngesting || !url.trim() || !isValidUrl}
          className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            isIngesting || !url.trim() || !isValidUrl
              ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
              : isYouTube
                ? 'bg-red-600 text-white hover:bg-red-700'
                : crawlEnabled
                  ? 'bg-green-600 text-white hover:bg-green-700'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
          }`}
        >
          {isIngesting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              {crawlEnabled ? 'Crawling...' : 'Importing...'}
            </>
          ) : isYouTube ? (
            <>
              <Youtube className="h-4 w-4" />
              Import YouTube Video
            </>
          ) : crawlEnabled ? (
            <>
              <Layers className="h-4 w-4" />
              Crawl Site ({maxPages} pages max)
            </>
          ) : (
            <>
              <Globe className="h-4 w-4" />
              Import Single Page
            </>
          )}
        </button>

        {/* Whisper Fallback Button — shown for YouTube URLs */}
        {isYouTube && onWhisperFallback && (
          <button
            type="button"
            onClick={() => {
              if (url.trim() && isValidUrl) {
                onWhisperFallback(url.trim(), title.trim() || undefined)
                setUrl('')
                setTitle('')
              }
            }}
            disabled={isWhisperRunning || isIngesting || !url.trim() || !isValidUrl}
            className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isWhisperRunning || isIngesting || !url.trim() || !isValidUrl
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-gray-700 border border-gray-600 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {isWhisperRunning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Transcribing with Whisper...
              </>
            ) : (
              <>
                <Mic className="h-4 w-4" />
                Transcribe with Whisper (fallback)
              </>
            )}
          </button>
        )}
      </form>

      {/* Help Text */}
      <div className="mt-4 p-3 rounded-lg bg-dark-bg/50 border border-dark-border">
        <div className="flex items-start gap-2">
          <Info className="h-4 w-4 text-gray-500 mt-0.5 shrink-0" />
          <div className="text-xs text-gray-500">
            <p className="mb-1">
              <strong className="text-gray-400">Single Page:</strong> Extracts text content from one URL
            </p>
            <p className="mb-1">
              <strong className="text-gray-400">Multi-Page Crawl:</strong> Follows links to crawl entire documentation sites
            </p>
            <p>
              <strong className="text-gray-400">YouTube:</strong> Extracts video transcript for semantic search
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Upload Zone Component
function UploadZone({
  onUpload,
  isUploading,
}: {
  onUpload: (file: File) => void
  isUploading: boolean
}) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer?.items?.length) {
      setIsDragging(true)
    }
  }, [])

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = e.dataTransfer?.files
      if (files?.length) {
        onUpload(files[0])
      }
    },
    [onUpload]
  )

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files?.length) {
        onUpload(files[0])
        // Reset input so same file can be selected again
        e.target.value = ''
      }
    },
    [onUpload]
  )

  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-6">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Upload className="h-5 w-5 text-primary-400" />
        Upload File
      </h2>

      {/* Drop Zone */}
      <div
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-primary-400 bg-primary-400/10'
            : 'border-dark-border hover:border-gray-500 hover:bg-dark-bg/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md,.docx,.csv"
          onChange={handleFileSelect}
          className="hidden"
        />

        {isUploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="h-10 w-10 text-primary-400 animate-spin mb-3" />
            <span className="text-gray-400">Processing file...</span>
          </div>
        ) : (
          <>
            <FileUp className="h-10 w-10 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-300 mb-1">
              {isDragging ? 'Drop file here' : 'Drag & drop a file or click to browse'}
            </p>
            <p className="text-xs text-gray-500">
              Supports PDF, DOCX, CSV, TXT, MD files (max 5MB)
            </p>
          </>
        )}
      </div>
    </div>
  )
}

// Search Interface Component
function SearchInterface({
  onSearch,
  isSearching,
  results,
}: {
  onSearch: (query: string) => void
  isSearching: boolean
  results: SearchResult[] | null
}) {
  const [query, setQuery] = useState('')
  const [expandedResult, setExpandedResult] = useState<string | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-6">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Search className="h-5 w-5 text-primary-400" />
        Semantic Search
      </h2>

      <form onSubmit={handleSubmit} className="mb-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search your documents semantically..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-dark-border bg-dark-bg text-white placeholder-gray-400"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              isSearching || !query.trim()
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {isSearching ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Search
              </>
            )}
          </button>
        </div>
      </form>

      {/* Search Results */}
      {results !== null && (
        <div className="space-y-3">
          <div className="text-sm text-gray-400">
            {results.length} result{results.length !== 1 ? 's' : ''} found
          </div>
          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
              No matching documents found
            </div>
          ) : (
            results.map((result) => (
              <div
                key={result.chunk_id}
                className="rounded-lg border border-dark-border bg-dark-bg/50 overflow-hidden"
              >
                <div
                  className="p-4 cursor-pointer hover:bg-dark-bg transition-colors"
                  onClick={() =>
                    setExpandedResult(expandedResult === result.chunk_id ? null : result.chunk_id)
                  }
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-primary-400" />
                      <span className="font-medium text-white text-sm">
                        {result.document_title}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          result.similarity_score >= 0.8
                            ? 'bg-green-500/20 text-green-400'
                            : result.similarity_score >= 0.6
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-gray-500/20 text-gray-400'
                        }`}
                      >
                        {((result.similarity_score ?? 0) * 100).toFixed(1)}% match
                      </span>
                      {expandedResult === result.chunk_id ? (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-400 line-clamp-2">{result.content}</p>
                </div>

                {expandedResult === result.chunk_id && (
                  <div className="border-t border-dark-border p-4 bg-dark-bg/30">
                    <div className="text-sm text-gray-300 whitespace-pre-wrap">
                      {result.content}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

// Document Type Badge
function DocumentTypeBadge({ type }: { type: string }) {
  const config: Record<string, { color: string; icon: React.ElementType; label: string }> = {
    youtube: { color: 'bg-red-500/20 text-red-400', icon: Youtube, label: 'YouTube' },
    url: { color: 'bg-blue-500/20 text-blue-400', icon: Globe, label: 'Web Page' },
    pdf: { color: 'bg-orange-500/20 text-orange-400', icon: FileText, label: 'PDF' },
    docx: { color: 'bg-indigo-500/20 text-indigo-400', icon: FileText, label: 'Word' },
    csv: { color: 'bg-emerald-500/20 text-emerald-400', icon: FileText, label: 'CSV' },
    text: { color: 'bg-gray-500/20 text-gray-400', icon: FileText, label: 'Text' },
    markdown: { color: 'bg-purple-500/20 text-purple-400', icon: FileText, label: 'Markdown' },
  }

  const { color, icon: Icon, label } = config[type.toLowerCase()] || config.text

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs ${color}`}>
      <Icon className="h-3 w-3" />
      {label}
    </span>
  )
}

// Document List Component
function DocumentList({
  documents,
  stats,
  isLoading,
  onDelete,
}: {
  documents: Document[]
  stats?: DocumentStats
  isLoading: boolean
  onDelete: (id: string) => void
}) {
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null)

  const getStatusBadge = (status: string) => {
    const config: Record<string, { color: string; icon: React.ElementType; animate: boolean }> = {
      embedding: { color: 'bg-yellow-500/20 text-yellow-400', icon: Loader2, animate: true },
      processed: { color: 'bg-green-500/20 text-green-400', icon: CheckCircle2, animate: false },
      failed: { color: 'bg-red-500/20 text-red-400', icon: XCircle, animate: false },
      pending: { color: 'bg-gray-500/20 text-gray-400', icon: Loader2, animate: true },
    }
    const { color, icon: Icon, animate } = config[status] || config.pending
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs ${color}`}>
        <Icon className={`h-3 w-3 ${animate ? 'animate-spin' : ''}`} />
        {status}
      </span>
    )
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border border-dark-border bg-dark-card p-8 text-center">
        <Loader2 className="h-8 w-8 text-primary-400 animate-spin mx-auto mb-2" />
        <span className="text-gray-400">Loading documents...</span>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="rounded-lg border border-dark-border bg-dark-card p-8 text-center">
        <FileText className="h-12 w-12 text-gray-500 mx-auto mb-4" />
        <p className="text-gray-400">No documents uploaded yet</p>
        <p className="text-sm text-gray-500 mt-1">
          Upload files or import URLs to start using semantic search
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-dark-border bg-dark-card overflow-hidden">
      <div className="p-4 border-b border-dark-border">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary-400" />
          Documents ({documents.length})
        </h2>
        {stats && (
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            {stats.youtube > 0 && (
              <span className="flex items-center gap-1">
                <Youtube className="h-3 w-3 text-red-400" />
                {stats.youtube} videos
              </span>
            )}
            {stats.urls > 0 && (
              <span className="flex items-center gap-1">
                <Globe className="h-3 w-3 text-blue-400" />
                {stats.urls} web pages
              </span>
            )}
            {stats.pdfs > 0 && (
              <span className="flex items-center gap-1">
                <FileText className="h-3 w-3 text-orange-400" />
                {stats.pdfs} PDFs
              </span>
            )}
          </div>
        )}
      </div>
      <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
        {documents.map((doc) => (
          <div key={doc.id}>
            <div
              className="p-4 hover:bg-dark-bg/30 transition-colors cursor-pointer"
              onClick={() => setExpandedDoc(expandedDoc === doc.id ? null : doc.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 min-w-0">
                  {doc.document_type === 'youtube' ? (
                    <Youtube className="h-5 w-5 text-red-400 shrink-0" />
                  ) : doc.document_type === 'url' ? (
                    <Globe className="h-5 w-5 text-blue-400 shrink-0" />
                  ) : (
                    <FileText className="h-5 w-5 text-gray-400 shrink-0" />
                  )}
                  <div className="min-w-0">
                    <div className="font-medium text-white truncate">{doc.title}</div>
                    {doc.source_url && (
                      <div className="text-xs text-gray-500 truncate max-w-[300px]">
                        {doc.source_url}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <DocumentTypeBadge type={doc.document_type} />
                  {getStatusBadge(doc.status)}
                  {expandedDoc === doc.id ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </div>
              </div>

              <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                <span>{doc.embedding_count} embeddings</span>
                <span>{doc.word_count.toLocaleString()} words</span>
                <span>{new Date(doc.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {expandedDoc === doc.id && (
              <div className="border-t border-dark-border p-4 bg-dark-bg/30 flex items-center gap-3">
                {doc.source_url && (
                  <a
                    href={doc.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 text-sm transition-colors"
                  >
                    <Link className="h-4 w-4" />
                    Open Source
                  </a>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(doc.id)
                  }}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 text-sm transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Main Page Component
export default function DocumentsPage() {
  const queryClient = useQueryClient()
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null)
  const [ingestError, setIngestError] = useState<string | null>(null)
  const [ingestErrorCode, setIngestErrorCode] = useState<string | null>(null)
  const [ingestErrorDetails, setIngestErrorDetails] = useState<string | null>(null)
  const [showErrorDetails, setShowErrorDetails] = useState(false)
  const [ingestWarning, setIngestWarning] = useState<string | null>(null)

  // Fetch stats
  const { data: statsData, isLoading: statsLoading } = useQuery<{
    embeddings_stats: RagStats
    rag_performance: { total_knowledge_bases: number }
  }>({
    queryKey: ['rag-stats'],
    queryFn: async () => {
      const response = await ragApi.stats()
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch documents
  const { data: documentsData, isLoading: documentsLoading } = useQuery<{
    documents: Document[]
    stats: DocumentStats
  }>({
    queryKey: ['rag-documents'],
    queryFn: async () => {
      const response = await ragApi.listDocuments({ limit: 100 })
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch collections
  const { data: collectionsData } = useQuery<{ collections: Collection[] }>({
    queryKey: ['rag-collections'],
    queryFn: async () => {
      const response = await ragApi.listCollections()
      return response.data
    },
    staleTime: 30000,
  })

  // File upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const response = await ragApi.ingestFile(file, { generate_embeddings: true })
      return response.data
    },
    onSuccess: () => {
      setIngestError(null)
      setIngestErrorCode(null)
      setIngestErrorDetails(null)
      setIngestWarning(null)
      queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
      queryClient.invalidateQueries({ queryKey: ['rag-stats'] })
    },
    onError: (error: Error) => {
      setIngestErrorCode(null)
      setIngestErrorDetails(null)
      setIngestError(error.message || 'Failed to upload file')
    },
  })

  // URL ingestion mutation - Session 733: Added crawl options support
  const ingestUrlMutation = useMutation({
    mutationFn: async ({ url, title, crawlOptions }: {
      url: string;
      title?: string;
      crawlOptions?: CrawlOptions;
    }) => {
      const response = await ragApi.ingestUrl(url, {
        title,
        generate_embeddings: true,
        ...crawlOptions,
      })
      return response.data
    },
    onSuccess: (data) => {
      setIngestError(null)
      setIngestErrorCode(null)
      setIngestErrorDetails(null)
      if (data.warning) {
        setIngestWarning(data.warning)
      } else if (data.crawl_stats) {
        // Session 733: Show crawl success message
        setIngestWarning(`Crawled ${data.crawl_stats.pages_crawled} pages, ${data.crawl_stats.total_words.toLocaleString()} words extracted`)
      } else {
        setIngestWarning(null)
      }
      queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
      queryClient.invalidateQueries({ queryKey: ['rag-stats'] })
    },
    onError: (error: any) => {
      const status = error?.response?.status
      const responseData = error?.response?.data
      const errorCode = responseData?.error_code || null
      const correlationId = responseData?.correlation_id || null
      const errorMessage = responseData?.error || error.message || 'Failed to import URL'

      setShowErrorDetails(false)

      if (errorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED') {
        setIngestErrorCode(errorCode)
        setIngestError('YouTube is blocking transcript requests from our server. An admin needs to configure a proxy to resolve this.')
        setIngestErrorDetails(
          [correlationId ? `Correlation ID: ${correlationId}` : '', 'Fix: set YOUTUBE_PROXY_URL env var on Railway with a residential proxy URL.'].filter(Boolean).join('\n')
        )
      } else if (status === 503 && !responseData?.error) {
        setIngestErrorCode('EDGE_UNAVAILABLE')
        setIngestError('Server temporarily unavailable. Please wait a moment and try again.')
        setIngestErrorDetails(`Status: 503 | ${new Date().toLocaleTimeString()}`)
      } else {
        setIngestErrorCode(null)
        setIngestError(errorMessage)
        setIngestErrorDetails(correlationId ? `Correlation ID: ${correlationId}` : null)
      }
    },
  })

  // YouTube Whisper fallback mutation (async — returns job_id, polls for status)
  const [whisperJobId, setWhisperJobId] = useState<string | null>(null)
  const whisperPollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const whisperMutation = useMutation({
    mutationFn: async ({ url, title }: { url: string; title?: string }) => {
      const response = await ragApi.ingestYoutubeWhisper(url, { title })
      return response.data
    },
    onSuccess: (data) => {
      setIngestError(null)
      setIngestErrorCode(null)
      setIngestErrorDetails(null)
      setWhisperJobId(data.job_id)
      setIngestWarning('Whisper transcription started — downloading audio and transcribing. This may take a few minutes...')

      // Poll for completion
      if (whisperPollRef.current) clearInterval(whisperPollRef.current)
      whisperPollRef.current = setInterval(async () => {
        try {
          const statusResp = await ragApi.ingestStatus(data.job_id)
          const status = statusResp.data
          if (status.status === 'completed' || status.status === 'success') {
            if (whisperPollRef.current) clearInterval(whisperPollRef.current)
            setWhisperJobId(null)
            setIngestWarning(`Whisper transcription complete — ${status.word_count || 0} words, ${status.segment_count || 0} segments`)
            queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
            queryClient.invalidateQueries({ queryKey: ['rag-stats'] })
          } else if (status.status === 'failed') {
            if (whisperPollRef.current) clearInterval(whisperPollRef.current)
            setWhisperJobId(null)
            setIngestWarning(null)
            setIngestError(status.error || 'Whisper transcription failed')
            setIngestErrorCode(null)
          }
        } catch {
          // Polling error — keep trying
        }
      }, 5000)
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.error || error.message || 'Failed to start Whisper transcription'
      setIngestError(errorMessage)
      setIngestErrorCode(null)
      setIngestErrorDetails(null)
    },
  })

  const handleWhisperFallback = (url: string, title?: string) => {
    setIngestError(null)
    whisperMutation.mutate({ url, title })
  }

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: async (query: string) => {
      const response = await ragApi.semanticSearch(query, { limit: 10, similarity_threshold: 0.3 })
      return response.data
    },
    onSuccess: (data) => {
      setSearchResults(data.results || [])
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await ragApi.deleteDocument(id)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
      queryClient.invalidateQueries({ queryKey: ['rag-stats'] })
    },
  })

  // Optimize mutation
  const optimizeMutation = useMutation({
    mutationFn: async () => {
      const response = await ragApi.optimize()
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rag-stats'] })
    },
  })

  const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

  const handleUpload = (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      setIngestError(`File too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Maximum size is 5MB.`)
      return
    }
    setIngestError(null)
    uploadMutation.mutate(file)
  }

  // Session 733: Updated to accept crawl options
  const handleIngestUrl = (url: string, title?: string, crawlOptions?: CrawlOptions) => {
    ingestUrlMutation.mutate({ url, title, crawlOptions })
  }

  const handleSearch = (query: string) => {
    searchMutation.mutate(query)
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id)
    }
  }

  const stats = statsData?.embeddings_stats
  const documents = documentsData?.documents || []
  const documentStats = documentsData?.stats
  const collections = collectionsData?.collections || []

  return (
    <div className="space-y-6 p-6">
      <Breadcrumb currentPage="Documents" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Database className="h-7 w-7 text-primary-400" />
            Documents & RAG
          </h1>
          <p className="text-gray-400 mt-1">
            Semantic search powered by pgvector embeddings
          </p>
        </div>
        <button
          onClick={() => optimizeMutation.mutate()}
          disabled={optimizeMutation.isPending}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            optimizeMutation.isPending
              ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
              : 'bg-dark-card border border-dark-border text-gray-300 hover:bg-dark-bg'
          }`}
        >
          {optimizeMutation.isPending ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Zap className="h-4 w-4" />
          )}
          Optimize
        </button>
      </div>

      {/* Error/Warning Banners */}
      {ingestError && (
        <div className={`rounded-lg p-4 flex items-start gap-3 ${
          ingestErrorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED'
            ? 'bg-orange-500/10 border border-orange-500/30'
            : ingestErrorCode === 'EDGE_UNAVAILABLE'
            ? 'bg-yellow-500/10 border border-yellow-500/30'
            : 'bg-red-500/10 border border-red-500/30'
        }`}>
          <XCircle className={`h-5 w-5 shrink-0 mt-0.5 ${
            ingestErrorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED' ? 'text-orange-400'
            : ingestErrorCode === 'EDGE_UNAVAILABLE' ? 'text-yellow-400'
            : 'text-red-400'
          }`} />
          <div className="flex-1">
            <div className={`font-medium ${
              ingestErrorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED' ? 'text-orange-400'
              : ingestErrorCode === 'EDGE_UNAVAILABLE' ? 'text-yellow-400'
              : 'text-red-400'
            }`}>
              {ingestErrorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED' ? 'YouTube Transcript Blocked'
                : ingestErrorCode === 'EDGE_UNAVAILABLE' ? 'Temporary Server Issue'
                : 'Import Error'}
            </div>
            <div className={`text-sm ${
              ingestErrorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED' ? 'text-orange-300/80'
              : ingestErrorCode === 'EDGE_UNAVAILABLE' ? 'text-yellow-300/80'
              : 'text-red-300/80'
            }`}>{ingestError}</div>
            {ingestErrorDetails && (
              <div className="mt-2">
                <button
                  onClick={() => setShowErrorDetails(!showErrorDetails)}
                  className="text-xs text-zinc-500 hover:text-zinc-400 underline"
                >
                  {showErrorDetails ? 'Hide details' : 'Show details'}
                </button>
                {showErrorDetails && (
                  <div className="mt-1 text-xs text-zinc-500 font-mono">{ingestErrorDetails}</div>
                )}
              </div>
            )}
          </div>
          <button
            onClick={() => { setIngestError(null); setIngestErrorCode(null); setIngestErrorDetails(null); }}
            className={`ml-auto ${
              ingestErrorCode === 'YOUTUBE_TRANSCRIPT_BLOCKED' ? 'text-orange-400 hover:text-orange-300' : 'text-red-400 hover:text-red-300'
            }`}
          >
            <XCircle className="h-4 w-4" />
          </button>
        </div>
      )}

      {ingestWarning && (
        <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/30 p-4 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-yellow-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-medium text-yellow-400">Import Warning</div>
            <div className="text-sm text-yellow-300/80">{ingestWarning}</div>
          </div>
          <button
            onClick={() => setIngestWarning(null)}
            className="ml-auto text-yellow-400 hover:text-yellow-300"
          >
            <XCircle className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Stats Grid */}
      {!statsLoading && stats && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <StatCard
            icon={Database}
            label="Total Embeddings"
            value={stats.total_embeddings}
            color="primary"
          />
          <StatCard
            icon={FileText}
            label="Documents"
            value={stats.total_documents}
            color="blue"
          />
          <StatCard
            icon={Youtube}
            label="YouTube"
            value={documentStats?.youtube || 0}
            color="red"
          />
          <StatCard
            icon={Globe}
            label="Web Pages"
            value={documentStats?.urls || 0}
            color="blue"
          />
          <StatCard
            icon={Layers}
            label="Collections"
            value={collections.length}
            color="purple"
          />
          <StatCard
            icon={Database}
            label="Dimensions"
            value={stats.embedding_dimensions || 1536}
            color="green"
          />
        </div>
      )}

      {/* Loading State for Stats */}
      {statsLoading && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="rounded-lg border border-dark-border bg-dark-card p-4 animate-pulse"
            >
              <div className="h-4 bg-dark-bg rounded w-20 mb-2"></div>
              <div className="h-8 bg-dark-bg rounded w-16"></div>
            </div>
          ))}
        </div>
      )}

      {/* Main Content */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column: Upload, URL Import & Search */}
        <div className="space-y-6">
          <URLIngestZone
            onIngestUrl={handleIngestUrl}
            onWhisperFallback={handleWhisperFallback}
            isIngesting={ingestUrlMutation.isPending}
            isWhisperRunning={whisperMutation.isPending || !!whisperJobId}
          />
          <UploadZone
            onUpload={handleUpload}
            isUploading={uploadMutation.isPending}
          />
          <SearchInterface
            onSearch={handleSearch}
            isSearching={searchMutation.isPending}
            results={searchResults}
          />
        </div>

        {/* Right Column: Documents List */}
        <div>
          <DocumentList
            documents={documents}
            stats={documentStats}
            isLoading={documentsLoading}
            onDelete={handleDelete}
          />
        </div>
      </div>

      {/* Info Section */}
      <div className="rounded-lg border border-dark-border bg-dark-card p-4">
        <h3 className="flex items-center gap-2 text-white font-medium mb-3">
          <Info className="h-5 w-5 text-primary-400" />
          About the RAG System
        </h3>
        <div className="text-sm text-gray-400 space-y-2">
          <p>
            The RAG (Retrieval-Augmented Generation) system uses pgvector to store and search
            document embeddings. Documents are chunked, embedded using OpenAI's text-embedding-3-small
            model, and indexed with HNSW for fast similarity search.
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>
              <strong className="text-gray-300">Files</strong> - Upload PDF, DOCX, CSV, TXT, or Markdown files
            </li>
            <li>
              <strong className="text-gray-300">Web Pages</strong> - Import any public URL
            </li>
            <li>
              <strong className="text-gray-300">YouTube</strong> - Extract video transcripts for search
            </li>
            <li>
              <strong className="text-gray-300">Index</strong> - HNSW for O(log n) similarity search
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
