import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import { formatRelative, formatDateTime } from '@/lib/time'
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
}

export default function DeliverablesTable({ items, total }: DeliverablesTableProps) {
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
            <th className="px-4 py-2 font-medium text-right">Quality</th>
            <th className="px-4 py-2 font-medium text-right">Created</th>
          </tr>
        </thead>
        <tbody>
          {items.map((d) => (
            <tr key={d.id} className="border-b border-dark-border/50">
              <td className="px-4 py-2 text-gray-200 max-w-xs truncate" title={d.title}>{d.title}</td>
              <td className="px-4 py-2 text-gray-400 whitespace-nowrap">{TYPE_LABELS[d.deliverable_type] ?? d.deliverable_type}</td>
              <td className="px-4 py-2 text-gray-400 whitespace-nowrap">{d.agent_name}</td>
              <td className="px-4 py-2 text-center">
                <StatusPill label={d.status} tone={STATUS_TONE[d.status] ?? 'gray'} />
              </td>
              <td className="px-4 py-2 text-right text-gray-400 tabular-nums">
                {(d.quality_score * 100).toFixed(0)}%
              </td>
              <td className="px-4 py-2 text-right text-gray-500" title={formatDateTime(d.created_at)}>
                {formatRelative(d.created_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {total > items.length && (
        <div className="px-4 py-2 text-xs text-gray-500 border-t border-dark-border">
          Showing {items.length} of {total}
        </div>
      )}
    </div>
  )
}
