import { useParams, useNavigate } from 'react-router-dom'
import { useErrorSummary } from '@/hooks/cockpitQueries'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { ERROR_SOURCE_LABEL, ERROR_SOURCE_TONE } from '@/components/cockpit/errors/errorSource'
import { formatRelative, formatDateTime } from '@/lib/time'
import { ArrowLeft } from 'lucide-react'
import type { FailureSourceType } from '@/types/cockpit'

export default function CockpitErrorDetailPage() {
  const { signatureId } = useParams<{ signatureId: string }>()
  const navigate = useNavigate()
  const decoded = signatureId ? decodeURIComponent(signatureId) : ''

  // Re-use the error summary to find this signature's data
  const { data, isLoading } = useErrorSummary(168) // 7d window for detail
  const sig = data?.signatures.find((s) => s.signature === decoded)

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/cockpit/errors')}
        className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-200 transition-colors"
      >
        <ArrowLeft size={16} />
        Back to Errors
      </button>

      {isLoading ? (
        <div className="card p-6">
          <SkeletonRows count={4} />
        </div>
      ) : !sig ? (
        <div className="card p-6 text-center text-gray-400">
          Signature not found or no occurrences in the last 7 days
        </div>
      ) : (
        <>
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-xl font-bold text-white break-words min-w-0">{sig.signature}</h1>
            <StatusPill
              label={ERROR_SOURCE_LABEL[sig.source as FailureSourceType] ?? sig.source}
              tone={ERROR_SOURCE_TONE[sig.source as FailureSourceType] ?? 'gray'}
            />
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div className="card px-4 py-3">
              <p className="text-xs text-gray-500">Occurrences</p>
              <p className="text-lg font-bold text-red-400 mt-1">{sig.count}</p>
            </div>
            <div className="card px-4 py-3">
              <p className="text-xs text-gray-500">Source</p>
              <p className="text-sm font-medium text-gray-200 mt-1 capitalize">{sig.source}</p>
            </div>
            <div className="card px-4 py-3">
              <p className="text-xs text-gray-500">Last Seen</p>
              <p className="text-sm font-medium text-gray-200 mt-1">
                {sig.last_seen ? formatRelative(sig.last_seen) : '—'}
              </p>
              {sig.last_seen && (
                <p className="text-xs text-gray-500 mt-0.5">{formatDateTime(sig.last_seen)}</p>
              )}
            </div>
          </div>

          {/* Sample error */}
          {sig.sample_error && (
            <div className="card border-red-500/30 p-4">
              <p className="text-xs font-medium text-red-400 mb-2">Sample Error</p>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words font-mono">
                {sig.sample_error}
              </pre>
            </div>
          )}
        </>
      )}
    </div>
  )
}
