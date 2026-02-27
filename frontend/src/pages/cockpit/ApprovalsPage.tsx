import { useState } from 'react'
import { useApprovals, useDecideApproval } from '@/hooks/cockpitQueries'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { ApprovalItem } from '@/types/cockpit'
import { formatRelative, formatDateTime } from '@/lib/time'
import { CheckCircle2, XCircle, ShieldCheck, Bot, Gauge } from 'lucide-react'

const URGENCY_TONE: Record<string, Tone> = {
  critical: 'red',
  high: 'amber',
  medium: 'blue',
  low: 'gray',
}

const KIND_LABEL: Record<string, string> = {
  decision: 'Decision',
  gate: 'Gate',
}

const KIND_TONE: Record<string, Tone> = {
  decision: 'blue',
  gate: 'amber',
}

function ApprovalCard({ item, onAction, isPending }: {
  item: ApprovalItem
  onAction: (kind: 'decision' | 'gate', id: string, action: string) => void
  isPending: boolean
}) {
  const [feedback, setFeedback] = useState('')
  const [showFeedback, setShowFeedback] = useState(false)

  return (
    <div className="card p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <StatusPill label={KIND_LABEL[item.kind] ?? item.kind} tone={KIND_TONE[item.kind] ?? 'gray'} />
            <StatusPill label={item.urgency} tone={URGENCY_TONE[item.urgency] ?? 'gray'} />
          </div>
          <h3 className="text-sm font-medium text-gray-200 truncate" title={item.title}>{item.title}</h3>
          {item.summary && (
            <p className="text-xs text-gray-500 mt-1 line-clamp-2">{item.summary}</p>
          )}
        </div>
        <span className="text-xs text-gray-600 whitespace-nowrap" title={formatDateTime(item.created_at)}>
          {formatRelative(item.created_at)}
        </span>
      </div>

      {/* Meta row */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        {item.source_agent && (
          <span className="flex items-center gap-1"><Bot size={12} /> {item.source_agent}</span>
        )}
        {item.ml_recommendation && (
          <span className="flex items-center gap-1"><Gauge size={12} /> ML: {item.ml_recommendation}</span>
        )}
        <span className="text-gray-600">Status: {item.status}</span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 pt-1 border-t border-dark-border/50">
        <button
          onClick={() => {
            if (showFeedback && feedback) {
              onAction(item.kind, item.id, item.kind === 'decision' ? 'approve' : 'approve')
            } else {
              onAction(item.kind, item.id, item.kind === 'decision' ? 'approve' : 'approve')
            }
          }}
          disabled={isPending}
          className="btn btn-primary text-xs px-3 py-1.5 flex items-center gap-1"
        >
          <CheckCircle2 size={14} /> Approve
        </button>
        <button
          onClick={() => {
            if (!showFeedback) {
              setShowFeedback(true)
              return
            }
            onAction(item.kind, item.id, item.kind === 'decision' ? 'reject' : 'block')
          }}
          disabled={isPending}
          className="btn text-xs px-3 py-1.5 flex items-center gap-1 border border-red-500/30 text-red-400 hover:bg-red-500/10"
        >
          <XCircle size={14} /> {item.kind === 'gate' ? 'Block' : 'Reject'}
        </button>
        {showFeedback && (
          <input
            type="text"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder={item.kind === 'gate' ? 'Reason for blocking…' : 'Feedback (optional)'}
            className="input text-xs flex-1"
            autoFocus
          />
        )}
      </div>
    </div>
  )
}

export default function CockpitApprovalsPage() {
  const { data, isLoading } = useApprovals()
  const mutation = useDecideApproval()

  function handleAction(kind: 'decision' | 'gate', id: string, action: string) {
    const payload = kind === 'decision'
      ? { decision: action }
      : { action, notes: '' }
    mutation.mutate({ kind, id, payload })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Approvals</h1>
        <div className="card p-6"><SkeletonRows count={5} /></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <ShieldCheck size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Approvals</h1>
        {data && data.total > 0 && (
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-primary-600/20 text-primary-400">
            {data.total}
          </span>
        )}
      </div>

      {mutation.isError && (
        <div className="card p-3 border border-red-500/30 text-red-400 text-sm">
          Action failed: {(mutation.error as Error)?.message ?? 'Unknown error'}
        </div>
      )}

      {mutation.isSuccess && (
        <div className="card p-3 border border-green-500/30 text-green-400 text-sm">
          Action completed successfully.
        </div>
      )}

      {!data || data.items.length === 0 ? (
        <div className="card p-8 text-center text-gray-500">
          No items awaiting approval. All clear.
        </div>
      ) : (
        <div className="space-y-3">
          {data.items.map((item) => (
            <ApprovalCard
              key={`${item.kind}-${item.id}`}
              item={item}
              onAction={handleAction}
              isPending={mutation.isPending}
            />
          ))}
        </div>
      )}
    </div>
  )
}
