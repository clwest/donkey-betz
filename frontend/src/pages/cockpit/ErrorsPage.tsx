import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useErrorSummary } from '@/hooks/cockpitQueries'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { ERROR_SOURCE_LABEL, ERROR_SOURCE_TONE } from '@/components/cockpit/errors/errorSource'
import { formatRelative, formatDateTime } from '@/lib/time'
import type { FailureSourceType } from '@/types/cockpit'

const HOUR_OPTIONS = [
  { value: 6, label: 'Last 6h' },
  { value: 24, label: 'Last 24h' },
  { value: 72, label: 'Last 3d' },
  { value: 168, label: 'Last 7d' },
]

export default function CockpitErrorsPage() {
  const [hours, setHours] = useState(24)
  const navigate = useNavigate()
  const { data, isLoading } = useErrorSummary(hours)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">
          Errors
          {data && data.total_failures > 0 && (
            <span className="ml-3 text-lg font-normal text-red-400">
              {data.total_failures} total
            </span>
          )}
        </h1>
        <select
          value={hours}
          onChange={(e) => setHours(Number(e.target.value))}
          className="input w-32 text-sm"
        >
          {HOUR_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-4">
            <SkeletonRows count={8} />
          </div>
        ) : !data || data.signatures.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-10">No errors detected in the last {hours}h</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-border text-left text-xs text-gray-500">
                  <th className="px-4 py-3 font-medium">Signature</th>
                  <th className="px-4 py-3 font-medium">Source</th>
                  <th className="px-4 py-3 font-medium text-right">Count</th>
                  <th className="px-4 py-3 font-medium text-right">Last Seen</th>
                </tr>
              </thead>
              <tbody>
                {data.signatures.map((sig, i) => (
                  <tr
                    key={`${sig.signature}-${i}`}
                    className="border-b border-dark-border/50 hover:bg-dark-border/20 cursor-pointer transition-colors"
                    onClick={() => navigate(`/cockpit/errors/${encodeURIComponent(sig.signature)}`)}
                  >
                    <td className="px-4 py-3 max-w-md">
                      <p className="text-gray-200 truncate">{sig.signature}</p>
                      {sig.sample_error && (
                        <p className="text-xs text-gray-500 truncate mt-0.5" title={sig.sample_error}>
                          {sig.sample_error}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <StatusPill
                        label={ERROR_SOURCE_LABEL[sig.source as FailureSourceType] ?? sig.source}
                        tone={ERROR_SOURCE_TONE[sig.source as FailureSourceType] ?? 'gray'}
                      />
                    </td>
                    <td className="px-4 py-3 text-right text-gray-400 tabular-nums font-medium">
                      {sig.count}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500 whitespace-nowrap" title={sig.last_seen ? formatDateTime(sig.last_seen) : undefined}>
                      {sig.last_seen ? formatRelative(sig.last_seen) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
