/**
 * Canonical Briefing view — S2985.
 *
 * Renders the response of POST /api/repo/canonical-briefing/ as a stack of
 * section cards. Each bullet exposes an "Evidence" toggle that reveals the
 * retrieved chunk citations. Bullets with zero citations render as the
 * literal "Insufficient support in canonical docs" placeholder (Z1
 * no-hallucination invariant enforced server-side).
 *
 * On error, the parent (DocumentViewer) receives an onFallback callback so
 * the user can drop back to the Raw markdown tab (Z2 UI isolation).
 */

import { useEffect, useMemo, useState } from 'react'
import {
  AlertTriangle,
  Check,
  ChevronDown,
  ChevronRight,
  FileText,
  Loader2,
  RefreshCw,
  Send,
} from 'lucide-react'
import { api } from '@/lib/api'

interface Citation {
  document_id: string
  chunk_id: string
  path: string
  snippet: string
}

interface Bullet {
  text: string
  citations: Citation[]
  original_text?: string
}

interface Section {
  key: string
  title: string
  bullets: Bullet[]
}

interface BriefingResponse {
  anchor_path: string
  scope: { root: string }
  generated_at: string
  prompt_version: string
  sections: Section[]
  cache: { hit: boolean; ttl_seconds: number }
  retrieval?: {
    total_unique_chunks: number
    per_section_counts: Record<string, number>
  }
  empty_reason?: string
}

interface CanonicalBriefingProps {
  anchorPath: string
  onFallbackToRaw: () => void
}

interface SendState {
  status: 'idle' | 'sending' | 'sent' | 'error'
  deliverableId?: string
  workspaceId?: string
  error?: string
}

const INSUFFICIENT_SUPPORT_MSG = 'Insufficient support in canonical docs'

function CitationList({ citations }: { citations: Citation[] }) {
  const [open, setOpen] = useState(false)
  if (citations.length === 0) return null
  return (
    <div className="mt-1">
      <button
        onClick={() => setOpen(!open)}
        className="text-xs text-gray-400 hover:text-primary-400 flex items-center gap-1 transition-colors"
      >
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        Evidence ({citations.length})
      </button>
      {open && (
        <ul className="mt-1 ml-4 space-y-2 border-l border-gray-700 pl-3">
          {citations.map((c, idx) => (
            <li key={`${c.chunk_id}-${idx}`} className="text-xs text-gray-400">
              <div className="flex items-center gap-1 text-gray-500">
                <FileText size={11} />
                <code className="text-gray-400 break-all">{c.path}</code>
              </div>
              <p className="mt-1 whitespace-pre-wrap text-gray-500">{c.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function SendToRigbyButton({
  anchorPath,
  section,
  bullet,
}: {
  anchorPath: string
  section: Section
  bullet: Bullet
}) {
  const [state, setState] = useState<SendState>({ status: 'idle' })

  const handleSend = async () => {
    setState({ status: 'sending' })
    try {
      const resp = await api.post('/repo/canonical-briefing/send-to-rigby/', {
        anchor_path: anchorPath,
        section_key: section.key,
        section_title: section.title,
        bullet_text: bullet.text,
        citations: bullet.citations,
      })
      setState({
        status: 'sent',
        deliverableId: resp.data?.deliverable_id,
        workspaceId: resp.data?.workspace_id,
      })
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.error ||
        err.message ||
        'Failed to send'
      setState({ status: 'error', error: errorMsg })
    }
  }

  if (state.status === 'sent') {
    return (
      <span className="mt-1 inline-flex items-center gap-1 text-xs text-primary-400">
        <Check size={12} />
        Sent — deliverable{' '}
        {state.deliverableId && state.workspaceId ? (
          <a
            href={`/workspace?tab=deliverables&workspace=${state.workspaceId}`}
            className="underline hover:text-primary-300"
            target="_blank"
            rel="noreferrer"
          >
            {state.deliverableId.slice(0, 8)}
          </a>
        ) : (
          'created'
        )}
      </span>
    )
  }

  if (state.status === 'error') {
    return (
      <button
        onClick={handleSend}
        className="mt-1 inline-flex items-center gap-1 text-xs text-accent-red hover:text-red-300"
        title={state.error}
      >
        <AlertTriangle size={12} />
        Send failed — retry
      </button>
    )
  }

  return (
    <button
      onClick={handleSend}
      disabled={state.status === 'sending'}
      className="mt-1 inline-flex items-center gap-1 text-xs text-gray-500 hover:text-primary-400 disabled:opacity-50 transition-colors"
      title="Create a workspace deliverable in Donkey Betz so Claude can pick it up"
    >
      {state.status === 'sending' ? (
        <Loader2 size={12} className="animate-spin" />
      ) : (
        <Send size={12} />
      )}
      {state.status === 'sending' ? 'Sending…' : 'Send to Rigby'}
    </button>
  )
}

function BulletItem({
  bullet,
  section,
  anchorPath,
}: {
  bullet: Bullet
  section: Section
  anchorPath: string
}) {
  const isInsufficient = bullet.text === INSUFFICIENT_SUPPORT_MSG
  return (
    <li className="text-sm">
      <span className={isInsufficient ? 'italic text-gray-500' : 'text-gray-200'}>
        {bullet.text}
      </span>
      <div className="flex items-center gap-3">
        <CitationList citations={bullet.citations} />
        {!isInsufficient && (
          <SendToRigbyButton
            anchorPath={anchorPath}
            section={section}
            bullet={bullet}
          />
        )}
      </div>
    </li>
  )
}

function SectionCard({
  section,
  anchorPath,
}: {
  section: Section
  anchorPath: string
}) {
  return (
    <div className="rounded-lg border border-gray-700 bg-gray-800/40 p-4">
      <h3 className="text-sm font-semibold text-white mb-2">{section.title}</h3>
      {section.bullets.length === 0 ? (
        <p className="text-xs text-gray-500 italic">No supporting content in scope.</p>
      ) : (
        <ul className="space-y-2 list-disc list-outside ml-4">
          {section.bullets.map((b, idx) => (
            <BulletItem
              key={idx}
              bullet={b}
              section={section}
              anchorPath={anchorPath}
            />
          ))}
        </ul>
      )}
    </div>
  )
}

export function CanonicalBriefing({ anchorPath, onFallbackToRaw }: CanonicalBriefingProps) {
  const [data, setData] = useState<BriefingResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [refreshTick, setRefreshTick] = useState(0)
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    if (!anchorPath) return

    let cancelled = false
    const fetchBriefing = async () => {
      setIsLoading(!data)
      setIsRefreshing(!!data)
      setError(null)
      try {
        const response = await api.post('/repo/canonical-briefing/', {
          anchor_path: anchorPath,
          force_refresh: refreshTick > 0,
        })
        if (cancelled) return
        const payload = response.data
        if (!payload || !Array.isArray(payload.sections)) {
          throw new Error('Invalid briefing response (missing sections)')
        }
        setData(payload)
      } catch (err: any) {
        if (cancelled) return
        const errorMsg = err.response?.data?.error
        setError(typeof errorMsg === 'string' ? errorMsg : err.message || 'Failed to load briefing')
      } finally {
        if (!cancelled) {
          setIsLoading(false)
          setIsRefreshing(false)
        }
      }
    }

    fetchBriefing()
    return () => {
      cancelled = true
    }
  }, [anchorPath, refreshTick])

  const generatedAt = useMemo(() => {
    if (!data?.generated_at) return null
    try {
      return new Date(data.generated_at).toLocaleString()
    } catch {
      return data.generated_at
    }
  }, [data])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="animate-spin text-primary-400" size={24} />
          <span className="text-sm text-gray-400">Generating briefing…</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-lg border border-accent-red/40 bg-accent-red/10 p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={16} className="text-accent-red" />
            <span className="text-sm font-semibold text-accent-red">Briefing unavailable</span>
          </div>
          <p className="text-xs text-gray-400 mb-3">{error}</p>
          <button
            onClick={onFallbackToRaw}
            className="text-xs px-3 py-1.5 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-200 transition-colors"
          >
            Show raw markdown instead
          </button>
        </div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-3 min-w-0">
          <span>Scope: <code className="text-gray-400">{data.scope.root}</code></span>
          {data.retrieval && (
            <span>{data.retrieval.total_unique_chunks} chunks retrieved</span>
          )}
          {generatedAt && <span>Generated {generatedAt}</span>}
          {data.cache?.hit && (
            <span className="text-primary-400">cache hit</span>
          )}
        </div>
        <button
          onClick={() => setRefreshTick(refreshTick + 1)}
          disabled={isRefreshing}
          className="flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-800 text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
          title="Regenerate briefing (bypasses cache)"
        >
          <RefreshCw size={12} className={isRefreshing ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>
      {data.empty_reason === 'no_chunks_in_scope' && (
        <div className="rounded-lg border border-yellow-700/40 bg-yellow-900/10 p-3 text-xs text-yellow-300">
          No embedded content found in this scope. Try the Raw tab or check that
          the containing folder has been indexed.
        </div>
      )}
      <div className="space-y-3">
        {data.sections.map((section) => (
          <SectionCard
            key={section.key}
            section={section}
            anchorPath={anchorPath}
          />
        ))}
      </div>
    </div>
  )
}
