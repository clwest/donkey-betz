/**
 * Documents Page - RAG/Document Embedding System
 *
 * Session 732: Frontend UI for the RAG system with 7,239+ document embeddings
 * using pgvector for semantic search.
 *
 * Features:
 * - Document upload with drag-and-drop
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
  BarChart3,
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
  filename: string
  collection_id?: string
  collection_name?: string
  chunk_count: number
  total_tokens: number
  created_at: string
  file_size: number
  status: 'processing' | 'completed' | 'error'
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
  id: string
  content: string
  similarity: number
  document_id: string
  document_name: string
  chunk_index: number
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
  color?: 'primary' | 'green' | 'blue' | 'yellow' | 'purple'
  subValue?: string
}) {
  const colorClasses = {
    primary: 'text-primary-400',
    green: 'text-green-400',
    blue: 'text-blue-400',
    yellow: 'text-yellow-400',
    purple: 'text-purple-400',
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

// Upload Zone Component
function UploadZone({
  onUpload,
  isUploading,
  collections,
}: {
  onUpload: (file: File, collectionId?: string) => void
  isUploading: boolean
  collections: Collection[]
}) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedCollection, setSelectedCollection] = useState<string>('')
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
        onUpload(files[0], selectedCollection || undefined)
      }
    },
    [onUpload, selectedCollection]
  )

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files?.length) {
        onUpload(files[0], selectedCollection || undefined)
      }
    },
    [onUpload, selectedCollection]
  )

  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-6">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Upload className="h-5 w-5 text-primary-400" />
        Upload Document
      </h2>

      {/* Collection Selection */}
      {collections.length > 0 && (
        <div className="mb-4">
          <label className="block text-sm text-gray-400 mb-2">
            Add to Collection (optional)
          </label>
          <select
            value={selectedCollection}
            onChange={(e) => setSelectedCollection(e.target.value)}
            className="w-full rounded-lg border border-dark-border bg-dark-bg px-3 py-2 text-white text-sm"
          >
            <option value="">No collection</option>
            {collections.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.document_count} docs)
              </option>
            ))}
          </select>
        </div>
      )}

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
          accept=".pdf,.txt,.md,.doc,.docx,.html,.json,.csv"
          onChange={handleFileSelect}
          className="hidden"
        />

        {isUploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="h-10 w-10 text-primary-400 animate-spin mb-3" />
            <span className="text-gray-400">Processing document...</span>
          </div>
        ) : (
          <>
            <FileUp className="h-10 w-10 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-300 mb-1">
              {isDragging ? 'Drop file here' : 'Drag & drop a file or click to browse'}
            </p>
            <p className="text-xs text-gray-500">
              Supports PDF, TXT, MD, DOC, DOCX, HTML, JSON, CSV
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
                key={result.id}
                className="rounded-lg border border-dark-border bg-dark-bg/50 overflow-hidden"
              >
                <div
                  className="p-4 cursor-pointer hover:bg-dark-bg transition-colors"
                  onClick={() =>
                    setExpandedResult(expandedResult === result.id ? null : result.id)
                  }
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-primary-400" />
                      <span className="font-medium text-white text-sm">
                        {result.document_name}
                      </span>
                      <span className="text-xs text-gray-500">
                        Chunk {result.chunk_index + 1}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          result.similarity >= 0.8
                            ? 'bg-green-500/20 text-green-400'
                            : result.similarity >= 0.6
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-gray-500/20 text-gray-400'
                        }`}
                      >
                        {(result.similarity * 100).toFixed(1)}% match
                      </span>
                      {expandedResult === result.id ? (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-400 line-clamp-2">{result.content}</p>
                </div>

                {expandedResult === result.id && (
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

// Document List Component
function DocumentList({
  documents,
  isLoading,
  onDelete,
}: {
  documents: Document[]
  isLoading: boolean
  onDelete: (id: string) => void
}) {
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null)

  const getStatusBadge = (status: Document['status']) => {
    const config = {
      processing: { color: 'bg-yellow-500/20 text-yellow-400', icon: Loader2, animate: true },
      completed: { color: 'bg-green-500/20 text-green-400', icon: CheckCircle2, animate: false },
      error: { color: 'bg-red-500/20 text-red-400', icon: XCircle, animate: false },
    }
    const { color, icon: Icon, animate } = config[status]
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs ${color}`}>
        <Icon className={`h-3 w-3 ${animate ? 'animate-spin' : ''}`} />
        {status}
      </span>
    )
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
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
          Upload your first document to start using semantic search
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
      </div>
      <div className="divide-y divide-dark-border">
        {documents.map((doc) => (
          <div key={doc.id}>
            <div
              className="p-4 hover:bg-dark-bg/30 transition-colors cursor-pointer"
              onClick={() => setExpandedDoc(expandedDoc === doc.id ? null : doc.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 min-w-0">
                  <FileText className="h-5 w-5 text-gray-400 shrink-0" />
                  <div className="min-w-0">
                    <div className="font-medium text-white truncate">{doc.filename}</div>
                    {doc.collection_name && (
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        <Layers className="h-3 w-3" />
                        {doc.collection_name}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(doc.status)}
                  {expandedDoc === doc.id ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </div>
              </div>

              <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                <span>{doc.chunk_count} chunks</span>
                <span>{doc.total_tokens.toLocaleString()} tokens</span>
                <span>{formatFileSize(doc.file_size)}</span>
                <span>{new Date(doc.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {expandedDoc === doc.id && (
              <div className="border-t border-dark-border p-4 bg-dark-bg/30 flex items-center gap-3">
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

  // Fetch stats
  const { data: statsData, isLoading: statsLoading } = useQuery<{ stats: RagStats }>({
    queryKey: ['rag-stats'],
    queryFn: async () => {
      const response = await ragApi.stats()
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch documents
  const { data: documentsData, isLoading: documentsLoading } = useQuery<{ documents: Document[] }>({
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

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ file, collectionId }: { file: File; collectionId?: string }) => {
      const response = await ragApi.uploadDocument(file, { collection_id: collectionId })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
      queryClient.invalidateQueries({ queryKey: ['rag-stats'] })
      queryClient.invalidateQueries({ queryKey: ['rag-collections'] })
    },
  })

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

  const handleUpload = (file: File, collectionId?: string) => {
    uploadMutation.mutate({ file, collectionId })
  }

  const handleSearch = (query: string) => {
    searchMutation.mutate(query)
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id)
    }
  }

  const stats = statsData?.stats
  const documents = documentsData?.documents || []
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

      {/* Stats Grid */}
      {!statsLoading && stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
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
            icon={Layers}
            label="Collections"
            value={stats.total_collections}
            color="purple"
          />
          <StatCard
            icon={BarChart3}
            label="Avg Chunks/Doc"
            value={stats.avg_chunks_per_doc.toFixed(1)}
            color="yellow"
          />
          <StatCard
            icon={Database}
            label="Storage"
            value={`${stats.storage_mb.toFixed(1)} MB`}
            color="green"
            subValue={`${stats.embedding_dimensions} dimensions`}
          />
        </div>
      )}

      {/* Loading State for Stats */}
      {statsLoading && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
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
        {/* Left Column: Upload & Search */}
        <div className="space-y-6">
          <UploadZone
            onUpload={handleUpload}
            isUploading={uploadMutation.isPending}
            collections={collections}
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
              <strong className="text-gray-300">Embedding Model</strong> - OpenAI text-embedding-3-small
              (1536 dimensions)
            </li>
            <li>
              <strong className="text-gray-300">Index Type</strong> - HNSW (Hierarchical Navigable
              Small World) for O(log n) search
            </li>
            <li>
              <strong className="text-gray-300">Similarity</strong> - Cosine distance for semantic
              matching
            </li>
            <li>
              <strong className="text-gray-300">Supported Formats</strong> - PDF, TXT, MD, DOC, DOCX,
              HTML, JSON, CSV
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
