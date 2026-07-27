/**
 * Session 818: Document Viewer Component
 *
 * Inline document viewer for reading Canon, Playbooks, and Audits
 * directly in the Knowledge tab without navigating away.
 */

import { useState, useEffect, useMemo } from 'react'
import { X, ExternalLink, Clock, FileText, Copy, Check, ChevronLeft, Maximize2, Minimize2, Sparkles, Code2 } from 'lucide-react'
import { cn } from '@/lib/cn'
// S2984 PR5 hotfix: use shared `api` axios instance (withCredentials:true +
// CSRF interceptor) so Django session cookies flow. Raw `axios` was used
// pre-PR3 when this endpoint was in PUBLIC_PATHS whitelist and didn't need
// auth; PR3 hardening exposed the wrapper mismatch.
import { api } from '@/lib/api'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'
import remarkGfm from 'remark-gfm'
import { CanonicalBriefing } from '@/components/platform/CanonicalBriefing'

// S2985: Briefing tab is only meaningful for canonical summary docs under
// docs/research/domains/. Detect via a conservative regex so we don't show a
// broken Briefing button on canon/, playbooks/, or audits/ pages.
const BRIEFING_ELIGIBLE_PATTERN = /docs\/research\/domains\/.+canonical_summary.*\.md$/i
type ViewerMode = 'briefing' | 'raw'

interface DocumentMetadata {
  path: string
  name: string
  title: string
  lines: number
  size_bytes: number
  modified_at: string
}

interface DocumentViewerProps {
  /** Path to the document (e.g., 'docs/canon/example.md') */
  documentPath: string | null
  /** Title to display in header */
  title?: string
  /** Category/type badge */
  category?: string
  /** Color for category badge */
  categoryColor?: string
  /** Called when viewer should close */
  onClose: () => void
  /** Whether the viewer is open */
  isOpen: boolean
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
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Session 943: Removed custom renderMarkdown in favor of ReactMarkdown with unified prose-dark styling

export function DocumentViewer({
  documentPath,
  title,
  category,
  categoryColor = '#8b5cf6',
  onClose,
  isOpen
}: DocumentViewerProps) {
  const [content, setContent] = useState<string | null>(null)
  const [metadata, setMetadata] = useState<DocumentMetadata | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // S2985: Briefing tab (spec deliverable 6f6c4122). Default to Briefing when
  // the doc is a canonical-summary path; otherwise Raw only.
  const briefingEligible = useMemo(
    () => Boolean(documentPath && BRIEFING_ELIGIBLE_PATTERN.test(documentPath)),
    [documentPath],
  )
  const [viewerMode, setViewerMode] = useState<ViewerMode>(
    briefingEligible ? 'briefing' : 'raw',
  )
  useEffect(() => {
    setViewerMode(briefingEligible ? 'briefing' : 'raw')
  }, [briefingEligible, documentPath])

  // Fetch document content when path changes
  useEffect(() => {
    if (!documentPath || !isOpen) {
      setContent(null)
      setMetadata(null)
      setError(null)
      return
    }

    const fetchDocument = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const response = await api.get('/platform/doc-content/', {
          params: { path: documentPath }
        })
        // S2984 PR4 hotfix: shape-guard the response body. Belt-and-
        // suspenders in case the backend ever regresses to returning a
        // 302 HTML redirect (which axios would surface as a 200 with an
        // HTML body — content becomes undefined, viewer renders blank).
        if (typeof response.data?.content !== 'string') {
          throw new Error('Invalid doc-content response (missing content string)')
        }
        setContent(response.data.content)
        setMetadata(response.data.metadata)
      } catch (err: any) {
        console.error('Error fetching document:', err)
        // Ensure error is always a string, not an object
        const errorMsg = err.response?.data?.error
        setError(typeof errorMsg === 'string' ? errorMsg : err.message || 'Failed to load document')
      } finally {
        setIsLoading(false)
      }
    }

    fetchDocument()
  }, [documentPath, isOpen])

  const handleCopy = () => {
    if (content) {
      navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleOpenExternal = () => {
    if (documentPath) {
      window.open(`/docs-index?search=${encodeURIComponent(documentPath)}`, '_blank')
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          'fixed inset-0 bg-black/60 transition-opacity z-40',
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
      />

      {/* Slide-out Panel */}
      <div
        className={cn(
          'fixed top-0 right-0 h-full bg-gray-900 border-l border-gray-700 shadow-2xl z-50 flex flex-col transition-all duration-300',
          isFullscreen ? 'w-full' : 'w-full max-w-3xl',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800/50 flex-shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
            >
              <ChevronLeft size={20} />
            </button>
            <div className="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${categoryColor}20` }}>
              <FileText size={16} style={{ color: categoryColor }} />
            </div>
            <div className="min-w-0">
              <h2 className="text-lg font-semibold text-white truncate">
                {title || metadata?.title || 'Document'}
              </h2>
              {metadata && (
                <p className="text-xs text-gray-500 truncate">{metadata.path}</p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {category && (
              <span
                className="text-xs px-2 py-1 rounded capitalize"
                style={{ backgroundColor: `${categoryColor}20`, color: categoryColor }}
              >
                {category}
              </span>
            )}
            <button
              onClick={handleCopy}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
              title="Copy content"
            >
              {copied ? <Check size={16} className="text-accent-green" /> : <Copy size={16} />}
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
              title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            >
              {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </button>
            <button
              onClick={handleOpenExternal}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
              title="Open in Docs Index"
            >
              <ExternalLink size={16} />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Metadata Bar */}
        {metadata && (
          <div className="flex items-center gap-4 px-4 py-2 bg-gray-800/30 border-b border-gray-700/50 text-xs text-gray-500 flex-shrink-0">
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {formatDate(metadata.modified_at)}
            </span>
            <span>{metadata.lines.toLocaleString()} lines</span>
            <span>{formatBytes(metadata.size_bytes)}</span>
          </div>
        )}

        {/* S2985: Briefing | Raw tab strip — only rendered when the doc is
            eligible for an LLM briefing (canonical summary under
            docs/research/domains/). Non-canonical docs skip the strip
            entirely so nothing changes for existing viewers. */}
        {briefingEligible && (
          <div className="flex items-center gap-1 px-4 py-2 bg-gray-800/20 border-b border-gray-700/50 flex-shrink-0">
            <button
              onClick={() => setViewerMode('briefing')}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-colors',
                viewerMode === 'briefing'
                  ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700',
              )}
            >
              <Sparkles size={13} />
              Briefing
            </button>
            <button
              onClick={() => setViewerMode('raw')}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-colors',
                viewerMode === 'raw'
                  ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700',
              )}
            >
              <Code2 size={13} />
              Raw
            </button>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {briefingEligible && viewerMode === 'briefing' && documentPath ? (
            <CanonicalBriefing
              anchorPath={documentPath}
              onFallbackToRaw={() => setViewerMode('raw')}
            />
          ) : isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="flex flex-col items-center gap-3">
                <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-400 text-sm">Loading document...</span>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="text-red-400 mb-2">Failed to load document</div>
                <div className="text-sm text-gray-500">{error}</div>
                <button
                  onClick={() => documentPath && window.open(`/docs-index?search=${encodeURIComponent(documentPath)}`, '_blank')}
                  className="mt-4 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
                >
                  Try opening in Docs Index
                </button>
              </div>
            </div>
          ) : content ? (
            /* Session 943: Unified prose styling with ReactMarkdown */
            <div className="p-6">
              <article className="prose prose-invert prose-dark prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
                  {content}
                </ReactMarkdown>
              </article>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No content to display
            </div>
          )}
        </div>
      </div>
    </>
  )
}
