/**
 * Session 1224 P1 — Outreach Inbox tab.
 *
 * Browser surface for OutreachDraft approval. Backed by:
 *   GET  /api/cockpit/outreach/inbox/
 *   POST /api/cockpit/outreach/<id>/approve/
 *   POST /api/cockpit/outreach/<id>/reject/
 *   POST /api/cockpit/outreach/generate/
 *
 * Tracking deliverable: 329165f4-d5c1-420c-a6ea-d5393ec3e343
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Mail, Loader2, CheckCircle, X, ChevronDown, ChevronRight,
  Send, Sparkles, AlertCircle,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

interface OutreachDraft {
  id: string
  lead_title: string
  lead_source: string
  lead_url: string
  lead_score: number
  offer_key: string
  subject_line: string
  body_text: string
  channel: string
  touch_number: number
  created_at: string
}

interface InboxResponse {
  drafts: OutreachDraft[]
  total_pending: number
  total_approved: number
  total_sent: number
  total_replied: number
  today_approved: number
  daily_cap: number
  remaining_approvals: number
  error?: string
}

interface GenerateResponse {
  created: number
  skipped_uncontactable: number
  candidates_walked: number
  daily_cap: number
  remaining_before: number
  note?: string
  drafts: Array<{ id: string; opportunity_id: string; offer_key: string; subject: string; fallback?: boolean }>
}

const offerBadgeColors: Record<string, string> = {
  ai_automation: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  content_engine: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  consulting: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
}

function formatAge(iso: string): string {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return 'just now'
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export function OutreachInboxTab() {
  const queryClient = useQueryClient()
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [editedText, setEditedText] = useState<Record<string, string>>({})
  const [generateBanner, setGenerateBanner] = useState<string | null>(null)

  const inboxQuery = useQuery<InboxResponse>({
    queryKey: ['outreach-inbox'],
    queryFn: () => api.get<InboxResponse>('/cockpit/outreach/inbox/').then(r => r.data),
    staleTime: 15000,
  })

  const approveMutation = useMutation({
    mutationFn: (vars: { id: string; edited_text?: string }) =>
      api.post(`/cockpit/outreach/${vars.id}/approve/`, { edited_text: vars.edited_text || '' }).then(r => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['outreach-inbox'] })
      setExpandedId(null)
    },
  })

  const rejectMutation = useMutation({
    mutationFn: (vars: { id: string; reason?: string }) =>
      api.post(`/cockpit/outreach/${vars.id}/reject/`, { reason: vars.reason || '' }).then(r => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['outreach-inbox'] })
      setExpandedId(null)
    },
  })

  const generateMutation = useMutation({
    mutationFn: () =>
      api.post<GenerateResponse>('/cockpit/outreach/generate/', {}).then(r => r.data),
    onSuccess: (data) => {
      const note = data.note || `Generated ${data.created} new draft${data.created === 1 ? '' : 's'} (walked ${data.candidates_walked}, skipped ${data.skipped_uncontactable} uncontactable)`
      setGenerateBanner(note)
      queryClient.invalidateQueries({ queryKey: ['outreach-inbox'] })
    },
    onError: (err: unknown) => {
      const msg = err instanceof Error ? err.message : 'Generate failed'
      setGenerateBanner(`Error: ${msg}`)
    },
  })

  const inbox = inboxQuery.data
  const drafts = inbox?.drafts || []

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Mail className="text-blue-400" size={22} />
          <div>
            <h2 className="text-xl font-semibold text-white">Outreach Inbox</h2>
            <p className="text-sm text-gray-400">
              Email drafts generated from Opportunity rows — approve to send
            </p>
          </div>
        </div>
        <button
          onClick={() => { setGenerateBanner(null); generateMutation.mutate() }}
          disabled={generateMutation.isPending}
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium',
            'bg-purple-600 hover:bg-purple-500 text-white border border-purple-500/50',
            'disabled:opacity-50 disabled:cursor-not-allowed',
          )}
        >
          {generateMutation.isPending ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Sparkles size={16} />
          )}
          Generate Now
        </button>
      </div>

      {/* Generate banner */}
      {generateBanner && (
        <div className="flex items-start gap-2 p-3 rounded-md bg-blue-500/10 border border-blue-500/30 text-blue-200 text-sm">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <span className="flex-1">{generateBanner}</span>
          <button onClick={() => setGenerateBanner(null)} className="text-blue-300 hover:text-blue-100">
            <X size={14} />
          </button>
        </div>
      )}

      {/* Counts strip */}
      {inbox && !inbox.error && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {[
            { label: 'Pending', value: inbox.total_pending, color: 'text-yellow-400' },
            { label: 'Approved today', value: inbox.today_approved, color: 'text-green-400' },
            { label: 'Remaining approvals', value: inbox.remaining_approvals, color: 'text-blue-400' },
            { label: 'Sent', value: inbox.total_sent, color: 'text-gray-300' },
            { label: 'Replied', value: inbox.total_replied, color: 'text-purple-400' },
          ].map(({ label, value, color }) => (
            <div key={label} className="p-2 rounded-md bg-gray-800/60 border border-gray-700">
              <div className="text-xs text-gray-400">{label}</div>
              <div className={cn('text-lg font-semibold', color)}>{value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Drafts list */}
      {inboxQuery.isLoading && (
        <div className="flex items-center justify-center py-8 text-gray-400">
          <Loader2 className="animate-spin mr-2" size={18} /> Loading drafts…
        </div>
      )}

      {inboxQuery.isError && (
        <div className="p-4 rounded-md bg-red-500/10 border border-red-500/30 text-red-200">
          Failed to load outreach inbox. Check the worker logs.
        </div>
      )}

      {inbox?.error && (
        <div className="p-4 rounded-md bg-red-500/10 border border-red-500/30 text-red-200">
          {inbox.error}
        </div>
      )}

      {!inboxQuery.isLoading && drafts.length === 0 && (
        <div className="p-8 text-center text-gray-400 border border-dashed border-gray-700 rounded-md">
          <Mail className="mx-auto mb-2 opacity-50" size={28} />
          <div>No pending drafts.</div>
          <div className="text-sm mt-1">Click <span className="text-purple-300">Generate Now</span> to create drafts from your top Opportunities.</div>
        </div>
      )}

      <div className="space-y-2">
        {drafts.map(draft => {
          const isExpanded = expandedId === draft.id
          const edited = editedText[draft.id] ?? draft.body_text
          return (
            <div
              key={draft.id}
              className="rounded-md border border-gray-700 bg-gray-800/40 overflow-hidden"
            >
              <button
                onClick={() => setExpandedId(isExpanded ? null : draft.id)}
                className="w-full px-3 py-3 flex items-center gap-3 hover:bg-gray-800/80 text-left"
              >
                {isExpanded ? (
                  <ChevronDown size={16} className="text-gray-400 shrink-0" />
                ) : (
                  <ChevronRight size={16} className="text-gray-400 shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-medium text-white truncate">
                      {draft.subject_line || '(no subject)'}
                    </span>
                    {draft.offer_key && (
                      <span
                        className={cn(
                          'text-[10px] px-1.5 py-0.5 rounded border uppercase tracking-wide shrink-0',
                          offerBadgeColors[draft.offer_key] || 'bg-gray-500/20 text-gray-300 border-gray-500/30',
                        )}
                      >
                        {draft.offer_key.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-400">
                    <span className="truncate">{draft.lead_title}</span>
                    {draft.lead_url && (
                      <span className="truncate opacity-70">{draft.lead_url}</span>
                    )}
                    <span className="shrink-0">{formatAge(draft.created_at)}</span>
                  </div>
                </div>
                {draft.lead_score > 0 && (
                  <div className="text-xs text-gray-300 shrink-0">
                    score {draft.lead_score}
                  </div>
                )}
              </button>

              {isExpanded && (
                <div className="px-4 pb-4 pt-2 border-t border-gray-700/60 space-y-3">
                  <div>
                    <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Subject</div>
                    <div className="text-sm text-white">{draft.subject_line || '(no subject)'}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Body</div>
                    <textarea
                      value={edited}
                      onChange={(e) => setEditedText(prev => ({ ...prev, [draft.id]: e.target.value }))}
                      rows={Math.min(14, Math.max(6, edited.split('\n').length))}
                      className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm text-gray-100 font-mono whitespace-pre-wrap focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  <div className="flex items-center gap-2 pt-1">
                    <button
                      onClick={() => approveMutation.mutate({ id: draft.id, edited_text: edited !== draft.body_text ? edited : '' })}
                      disabled={approveMutation.isPending}
                      className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-green-600 hover:bg-green-500 text-white text-sm font-medium disabled:opacity-50"
                    >
                      {approveMutation.isPending && approveMutation.variables?.id === draft.id ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <CheckCircle size={14} />
                      )}
                      Approve
                    </button>
                    <button
                      onClick={() => rejectMutation.mutate({ id: draft.id, reason: '' })}
                      disabled={rejectMutation.isPending}
                      className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-gray-700 hover:bg-gray-600 text-gray-200 text-sm disabled:opacity-50"
                    >
                      {rejectMutation.isPending && rejectMutation.variables?.id === draft.id ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <X size={14} />
                      )}
                      Reject
                    </button>
                    {draft.lead_url && (
                      <a
                        href={draft.lead_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-gray-700/60 hover:bg-gray-700 text-gray-300 text-sm ml-auto"
                      >
                        <Send size={14} /> View source
                      </a>
                    )}
                  </div>

                  {approveMutation.isError && approveMutation.variables?.id === draft.id && (
                    <div className="text-xs text-red-300">Approve failed — see console.</div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default OutreachInboxTab
