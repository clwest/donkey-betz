import { useNavigate } from 'react-router-dom'
import type { ErrorSummaryResponse } from '@/types/cockpit'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { ERROR_SOURCE_LABEL, ERROR_SOURCE_TONE } from '@/components/cockpit/errors/errorSource'
import { formatRelative, formatDateTime } from '@/lib/time'
import { AlertTriangle } from 'lucide-react'

interface TodayErrorsCardProps {
  data?: ErrorSummaryResponse
  isLoading?: boolean
}

export default function TodayErrorsCard({ data, isLoading }: TodayErrorsCardProps) {
  const navigate = useNavigate()

  return (
    <div className="card flex flex-col">
      <div className="flex items-center justify-between border-b border-dark-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
          <AlertTriangle size={16} className="text-amber-400" />
          Errors
          {data && data.total_failures > 0 && (
            <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-[11px] font-medium text-red-400">
              {data.total_failures}
            </span>
          )}
        </div>
        <button
          onClick={() => navigate('/cockpit/errors')}
          className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
        >
          View all
        </button>
      </div>

      <div className="flex-1 p-4">
        {isLoading ? (
          <SkeletonRows count={5} />
        ) : !data || data.signatures.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">No errors detected</p>
        ) : (
          <ul className="space-y-2">
            {data.signatures.slice(0, 5).map((sig, i) => (
              <li
                key={`${sig.signature}-${i}`}
                className="flex items-center gap-3 rounded-lg px-2 py-1.5 hover:bg-dark-border/30 cursor-pointer transition-colors"
                onClick={() => navigate(`/cockpit/errors/${encodeURIComponent(sig.signature)}`)}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate" title={sig.sample_error}>
                    {sig.signature}
                  </p>
                </div>
                <StatusPill
                  label={ERROR_SOURCE_LABEL[sig.source]}
                  tone={ERROR_SOURCE_TONE[sig.source]}
                />
                <span className="text-xs text-gray-500 tabular-nums w-8 text-right">
                  {sig.count}x
                </span>
                {sig.last_seen && (
                  <span className="text-xs text-gray-600 w-14 text-right" title={formatDateTime(sig.last_seen)}>
                    {formatRelative(sig.last_seen)}
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
