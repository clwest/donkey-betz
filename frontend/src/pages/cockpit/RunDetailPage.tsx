import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useRunDetail, useRetryRun, useCreateIncidentNote } from '@/hooks/cockpitQueries'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SmartOutputRenderer from '@/components/SmartOutputRenderer'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { RUN_STATUS_LABEL, RUN_STATUS_TONE } from '@/components/cockpit/runs/runStatus'
import { formatDateTime, formatDurationMs } from '@/lib/time'
import { ArrowLeft, RotateCcw, FileText, Activity, Clock, User, GitBranch, Zap, HelpCircle } from 'lucide-react'
import type { RunStatus, TriggerType } from '@/types/cockpit'

const TABS = ['Summary', 'Inputs', 'Outputs', 'Raw JSON'] as const
type Tab = (typeof TABS)[number]

const TRIGGER_ICON: Record<TriggerType, typeof Clock> = {
  scheduled: Clock,
  manual: User,
  workflow: GitBranch,
  autopilot: Zap,
  retry: RotateCcw,
  unknown: HelpCircle,
}

export default function CockpitRunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const navigate = useNavigate()
  const { data: run, isLoading, error } = useRunDetail(runId)
  const retryMutation = useRetryRun()
  const incidentMutation = useCreateIncidentNote()
  const [activeTab, setActiveTab] = useState<Tab>('Summary')

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
                {retryMutation.isPending ? 'Retrying\u2026' : 'Retry Run'}
              </button>
              <button
                onClick={() => incidentMutation.mutate({
                  title: `Failed run: ${run.agent_name} \u2014 ${run.task?.slice(0, 80)}`,
                  detail: run.error_message || '',
                  source_type: 'run',
                  source_id: run.id,
                })}
                disabled={incidentMutation.isPending}
                className="btn text-xs px-3 py-1.5 flex items-center gap-1.5 border border-dark-border text-gray-400 hover:text-gray-200"
              >
                <FileText size={14} />
                {incidentMutation.isPending ? 'Creating\u2026' : 'Incident Note'}
              </button>
              {retryMutation.isSuccess && (
                <span className="text-xs text-green-400">Retry queued (task: {retryMutation.data.new_task_id.slice(0, 8)}\u2026)</span>
              )}
              {retryMutation.isError && (
                <span className="text-xs text-red-400">Retry failed: {(retryMutation.error as Error).message}</span>
              )}
              {incidentMutation.isSuccess && (
                <span className="text-xs text-green-400">Incident note created</span>
              )}
            </div>
          )}

          {/* Metrics row */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: 'Started', value: run.created_at ? formatDateTime(run.created_at) : '\u2014' },
              { label: 'Completed', value: run.completed_at ? formatDateTime(run.completed_at) : '\u2014' },
              { label: 'Duration', value: formatDurationMs(run.execution_time_ms) },
              { label: 'Tokens', value: run.tokens_used > 0 ? run.tokens_used.toLocaleString() : '\u2014' },
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

          {/* Tab bar */}
          <div className="flex gap-1 border-b border-dark-border">
            {TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === tab
                    ? 'text-primary-400 border-primary-400'
                    : 'text-gray-500 border-transparent hover:text-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="min-h-[200px]">
            {activeTab === 'Summary' && <SummaryTab run={run} />}
            {activeTab === 'Inputs' && <InputsTab run={run} />}
            {activeTab === 'Outputs' && <OutputsTab run={run} />}
            {activeTab === 'Raw JSON' && <RawJsonTab run={run} />}
          </div>
        </>
      )}
    </div>
  )
}

// ── Summary tab ────────────────────────────────────────────────────────────

function SummaryTab({ run }: { run: Record<string, any> }) {
  const enrichment = run.enrichment
  const trigger = enrichment?.trigger
  const importance = enrichment?.importance
  const artifacts = enrichment?.artifacts
  const summary = enrichment?.summary

  const TriggerIcon = trigger ? TRIGGER_ICON[trigger.type as TriggerType] ?? HelpCircle : Clock

  return (
    <div className="space-y-4">
      {/* Summary */}
      {summary && (
        <div className="card p-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Summary</p>
          <p className="text-sm text-gray-200">{summary}</p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {/* Trigger */}
        {trigger && (
          <div className="card p-4">
            <p className="text-xs font-medium text-gray-500 mb-2">Trigger</p>
            <div className="flex items-center gap-2 text-sm text-gray-200">
              <TriggerIcon size={14} className="text-gray-400" />
              {trigger.label}
            </div>
          </div>
        )}

        {/* Importance */}
        {importance && (
          <div className="card p-4">
            <p className="text-xs font-medium text-gray-500 mb-2">Importance</p>
            <p className="text-sm text-gray-200 capitalize">{importance.level.replace('_', ' ')}</p>
            {importance.reasons?.length > 0 && (
              <div className="flex gap-1.5 mt-1.5">
                {importance.reasons.map((r: string) => (
                  <span key={r} className="rounded bg-dark-border/50 px-2 py-0.5 text-[11px] text-gray-400">
                    {r.replace('_', ' ')}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Artifacts */}
      {artifacts && (
        <div className="card p-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Artifacts</p>
          <ArtifactList artifacts={artifacts} />
        </div>
      )}

      {/* Output message preview */}
      {run.output_data?.message && (
        <div className="card p-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Output Message</p>
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{run.output_data.message}</p>
        </div>
      )}
    </div>
  )
}

function ArtifactList({ artifacts }: { artifacts: Record<string, any[]> }) {
  const categories = ['deliverables', 'blogs', 'media', 'wagers', 'initiatives'] as const
  const hasAny = categories.some((c) => artifacts[c]?.length > 0)

  if (!hasAny) {
    return <p className="text-sm text-gray-600">No artifacts produced</p>
  }

  return (
    <div className="space-y-2">
      {categories.map((cat) => {
        const items = artifacts[cat] || []
        if (items.length === 0) return null
        return (
          <div key={cat} className="flex items-center gap-2">
            <span className="text-[11px] font-medium text-gray-500 uppercase w-20">{cat}</span>
            <span className="text-sm text-gray-300">{items.length} item{items.length > 1 ? 's' : ''}</span>
          </div>
        )
      })}
    </div>
  )
}

// ── Inputs tab ─────────────────────────────────────────────────────────────

function InputsTab({ run }: { run: Record<string, any> }) {
  const inputData = run.input_data || {}
  const hasInput = Object.keys(inputData).length > 0

  return (
    <div className="card p-4">
      <p className="text-xs font-medium text-gray-500 mb-2">Input Data</p>
      {hasInput ? (
        <pre className="text-xs text-gray-400 whitespace-pre-wrap break-words font-mono max-h-96 overflow-auto">
          {JSON.stringify(inputData, null, 2)}
        </pre>
      ) : (
        <p className="text-sm text-gray-600">No input data</p>
      )}
    </div>
  )
}

// ── Outputs tab ────────────────────────────────────────────────────────────

function OutputsTab({ run }: { run: Record<string, any> }) {
  const outputData = run.output_data || {}
  const hasOutput = Object.keys(outputData).length > 0

  return (
    <div className="card p-4">
      <p className="text-xs font-medium text-gray-500 mb-2">Output</p>
      {hasOutput ? (
        <SmartOutputRenderer
          data={outputData}
          agentName={run.agent_name}
          maxHeight="max-h-[600px]"
          showRawToggle={true}
        />
      ) : (
        <p className="text-sm text-gray-600">No output data</p>
      )}
    </div>
  )
}

// ── Raw JSON tab ───────────────────────────────────────────────────────────

function RawJsonTab({ run }: { run: Record<string, any> }) {
  const [copied, setCopied] = useState(false)
  const raw = JSON.stringify(run, null, 2)

  const handleCopy = () => {
    navigator.clipboard.writeText(raw)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-medium text-gray-500">Full Run Data</p>
        <button
          onClick={handleCopy}
          className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
        >
          {copied ? 'Copied!' : 'Copy JSON'}
        </button>
      </div>
      <pre className="text-xs text-gray-400 whitespace-pre-wrap break-words font-mono max-h-[600px] overflow-auto">
        {raw}
      </pre>
    </div>
  )
}
