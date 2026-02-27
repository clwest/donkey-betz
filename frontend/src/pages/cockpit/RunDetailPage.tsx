import { useParams, useNavigate } from 'react-router-dom'
import { useRunDetail, useRetryRun, useCreateIncidentNote } from '@/hooks/cockpitQueries'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { RUN_STATUS_LABEL, RUN_STATUS_TONE } from '@/components/cockpit/runs/runStatus'
import { formatDateTime, formatDurationMs } from '@/lib/time'
import { ArrowLeft, RotateCcw, FileText, Activity } from 'lucide-react'
import type { RunStatus } from '@/types/cockpit'

export default function CockpitRunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const navigate = useNavigate()
  const { data: run, isLoading, error } = useRunDetail(runId)
  const retryMutation = useRetryRun()
  const incidentMutation = useCreateIncidentNote()

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/cockpit/runs')}
        className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-200 transition-colors"
      >
        <ArrowLeft size={16} />
        Back to Runs
      </button>

      {isLoading ? (
        <div className="card p-6">
          <SkeletonRows count={6} />
        </div>
      ) : error || !run ? (
        <div className="card p-6 text-center text-gray-400">
          {error ? `Failed to load run: ${(error as Error).message}` : 'Run not found'}
        </div>
      ) : (
        <>
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <h1 className="text-xl font-bold text-white truncate">{run.task}</h1>
              <p className="text-sm text-gray-400 mt-1">{run.agent_name}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate(`/cockpit/runs/${runId}/trace`)}
                className="btn text-xs px-3 py-1.5 flex items-center gap-1.5"
              >
                <Activity size={14} />
                View Trace
              </button>
              <StatusPill
                label={RUN_STATUS_LABEL[run.status as RunStatus] ?? run.status}
                tone={RUN_STATUS_TONE[run.status as RunStatus] ?? 'gray'}
              />
            </div>
          </div>

          {/* Action bar for failed runs */}
          {run.status === 'failed' && (
            <div className="flex items-center gap-3">
              <button
                onClick={() => retryMutation.mutate(run.id)}
                disabled={retryMutation.isPending}
                className="btn btn-primary text-xs px-3 py-1.5 flex items-center gap-1.5"
              >
                <RotateCcw size={14} />
                {retryMutation.isPending ? 'Retrying…' : 'Retry Run'}
              </button>
              <button
                onClick={() => incidentMutation.mutate({
                  title: `Failed run: ${run.agent_name} — ${run.task?.slice(0, 80)}`,
                  detail: run.error_message || '',
                  source_type: 'run',
                  source_id: run.id,
                })}
                disabled={incidentMutation.isPending}
                className="btn text-xs px-3 py-1.5 flex items-center gap-1.5 border border-dark-border text-gray-400 hover:text-gray-200"
              >
                <FileText size={14} />
                {incidentMutation.isPending ? 'Creating…' : 'Incident Note'}
              </button>
              {retryMutation.isSuccess && (
                <span className="text-xs text-green-400">Retry queued (task: {retryMutation.data.new_task_id.slice(0, 8)}…)</span>
              )}
              {retryMutation.isError && (
                <span className="text-xs text-red-400">Retry failed: {(retryMutation.error as Error).message}</span>
              )}
              {incidentMutation.isSuccess && (
                <span className="text-xs text-green-400">Incident note created</span>
              )}
            </div>
          )}

          {/* Metrics */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: 'Started', value: run.created_at ? formatDateTime(run.created_at) : '—' },
              { label: 'Completed', value: run.completed_at ? formatDateTime(run.completed_at) : '—' },
              { label: 'Duration', value: formatDurationMs(run.execution_time_ms) },
              { label: 'Tokens', value: run.tokens_used > 0 ? run.tokens_used.toLocaleString() : '—' },
            ].map((m) => (
              <div key={m.label} className="card px-4 py-3">
                <p className="text-xs text-gray-500">{m.label}</p>
                <p className="text-sm font-medium text-gray-200 mt-1">{m.value}</p>
              </div>
            ))}
          </div>

          {/* Error message */}
          {run.error_message && (
            <div className="card border-red-500/30 p-4">
              <p className="text-xs font-medium text-red-400 mb-1">Error</p>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words font-mono">
                {run.error_message}
              </pre>
            </div>
          )}

          {/* Input / Output panels */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="card p-4">
              <p className="text-xs font-medium text-gray-500 mb-2">Input</p>
              {run.input_data && Object.keys(run.input_data).length > 0 ? (
                <pre className="text-xs text-gray-400 whitespace-pre-wrap break-words font-mono max-h-64 overflow-auto">
                  {JSON.stringify(run.input_data, null, 2)}
                </pre>
              ) : (
                <p className="text-sm text-gray-600">No input data</p>
              )}
            </div>
            <div className="card p-4">
              <p className="text-xs font-medium text-gray-500 mb-2">Output</p>
              {run.output_data && Object.keys(run.output_data).length > 0 ? (
                <pre className="text-xs text-gray-400 whitespace-pre-wrap break-words font-mono max-h-64 overflow-auto">
                  {JSON.stringify(run.output_data, null, 2)}
                </pre>
              ) : (
                <p className="text-sm text-gray-600">No output data</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
