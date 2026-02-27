import { useNavigate } from 'react-router-dom'
import type { RunSummary } from '@/types/cockpit'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { RUN_STATUS_LABEL, RUN_STATUS_TONE } from '@/components/cockpit/runs/runStatus'
import { formatRelative, formatDurationMs, formatDateTime } from '@/lib/time'
import { Play } from 'lucide-react'

interface TodayRunsCardProps {
  runs: RunSummary[]
  isLoading?: boolean
}

export default function TodayRunsCard({ runs, isLoading }: TodayRunsCardProps) {
  const navigate = useNavigate()

  return (
    <div className="card flex flex-col">
      <div className="flex items-center justify-between border-b border-dark-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
          <Play size={16} className="text-primary-400" />
          Recent Runs
        </div>
        <button
          onClick={() => navigate('/cockpit/runs')}
          className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
        >
          View all
        </button>
      </div>

      <div className="flex-1 p-4">
        {isLoading ? (
          <SkeletonRows count={5} />
        ) : runs.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">No runs yet</p>
        ) : (
          <ul className="space-y-2">
            {runs.slice(0, 5).map((run) => (
              <li
                key={run.id}
                className="flex items-center gap-3 rounded-lg px-2 py-1.5 hover:bg-dark-border/30 cursor-pointer transition-colors"
                onClick={() => navigate(`/cockpit/runs/${run.id}`)}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">{run.task}</p>
                  <p className="text-xs text-gray-500 truncate">{run.agent_name}</p>
                </div>
                <StatusPill
                  label={RUN_STATUS_LABEL[run.status]}
                  tone={RUN_STATUS_TONE[run.status]}
                />
                <span className="text-xs text-gray-500 w-14 text-right" title={formatDateTime(run.created_at)}>
                  {formatRelative(run.created_at)}
                </span>
                {run.execution_time_ms != null && (
                  <span className="text-xs text-gray-600 w-14 text-right">
                    {formatDurationMs(run.execution_time_ms)}
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
