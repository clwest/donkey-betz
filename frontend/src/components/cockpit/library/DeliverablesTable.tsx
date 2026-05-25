import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'
import remarkGfm from 'remark-gfm'
import { ChevronDown, ChevronUp } from 'lucide-react'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import { formatRelative, formatDateTime } from '@/lib/time'
import { api } from '@/lib/api'
import type { DeliverableItem } from '@/types/cockpit'

const STATUS_TONE: Record<string, Tone> = {
  draft: 'gray',
  ready: 'blue',
  published: 'green',
  archived: 'amber',
}

const TYPE_LABELS: Record<string, string> = {
  document: 'Document',
  image: 'Image',
  video: 'Video',
  audio: 'Audio',
  code: 'Code',
  analysis: 'Analysis',
  report: 'Report',
  template: 'Template',
  research: 'Research',
  strategy: 'Strategy',
  plan: 'Plan',
  script: 'Script',
}

interface DeliverablesTableProps {
  items: DeliverableItem[]
  total: number
  offset?: number
  limit?: number
  onPageChange?: (offset: number) => void
}

export default function DeliverablesTable({ items, total, offset = 0, limit = 50, onPageChange }: DeliverablesTableProps) {
  const page = Math.floor(offset / limit) + 1
  const totalPages = Math.ceil(total / limit)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data: expandedDetail } = useQuery({
    queryKey: ['library-deliverable-detail', expandedId],
    queryFn: async () => {
      if (!expandedId) return null
      const res = await api.get(`/deliverables/${expandedId}/`)
      return res.data?.deliverable || res.data
    },
    enabled: !!expandedId,
  })

  if (items.length === 0) {
    return (
      <div className="card p-8 text-center text-gray-500">
        No deliverables found.
      </div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-dark-border text-left text-xs text-gray-500">
            <th className="px-4 py-2 font-medium">Title</th>
            <th className="px-4 py-2 font-medium">Type</th>
            <th className="px-4 py-2 font-medium">Agent</th>
            <th className="px-4 py-2 font-medium text-center">Status</th>
            <th className="px-4 py-2 font-medium text-right">Created</th>
            <th className="px-4 py-2 font-medium w-8"></th>
          </tr>
        </thead>
        <tbody>
          {items.map((d) => {
            const isExpanded = expandedId === d.id
            return (
              <>
                <tr
                  key={d.id}
                  className="border-b border-dark-border/50 cursor-pointer hover:bg-gray-800/30 transition-colors"
                  onClick={() => setExpandedId(isExpanded ? null : d.id)}
                >
                  <td className="px-4 py-2 text-gray-200 max-w-xs truncate" title={d.title}>{d.title}</td>
                  <td className="px-4 py-2 text-gray-400 whitespace-nowrap">{TYPE_LABELS[d.deliverable_type] ?? d.deliverable_type}</td>
                  <td className="px-4 py-2 text-gray-400 whitespace-nowrap">{d.agent_name}</td>
                  <td className="px-4 py-2 text-center">
                    <StatusPill label={d.status} tone={STATUS_TONE[d.status] ?? 'gray'} />
                  </td>
                  <td className="px-4 py-2 text-right text-gray-500" title={formatDateTime(d.created_at)}>
                    {formatRelative(d.created_at)}
                  </td>
                  <td className="px-4 py-2 text-gray-500">
                    {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </td>
                </tr>
                {isExpanded && (
                  <tr key={`${d.id}-detail`}>
                    <td colSpan={6} className="px-6 py-4 bg-gray-900/30 border-b border-dark-border">
                      {expandedDetail?.content ? (
                        <div className="prose prose-invert prose-sm max-w-none">
                          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
                            {expandedDetail.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <div className="text-center py-4 text-gray-500 text-sm">Loading...</div>
                      )}
                    </td>
                  </tr>
                )}
              </>
            )
          })}
        </tbody>
      </table>
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-2 text-xs border-t border-dark-border">
          <span className="text-gray-500">
            {offset + 1}–{Math.min(offset + items.length, total)} of {total}
          </span>
          <div className="flex gap-1">
            <button
              disabled={page <= 1}
              onClick={() => onPageChange?.(Math.max(0, offset - limit))}
              className="px-2 py-1 rounded bg-dark-card text-gray-400 hover:text-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Prev
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange?.(offset + limit)}
              className="px-2 py-1 rounded bg-dark-card text-gray-400 hover:text-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
