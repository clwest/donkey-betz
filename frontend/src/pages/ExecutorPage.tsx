/**
 * Executor Page - Execution Runs List + Detail + Approval Controls
 *
 * Session 1076: PR D — Minimal UI for the executor subsystem.
 * Shows list of execution runs, detail view with logs/diff, and approval controls.
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  ChevronRight,
  ArrowLeft,
  ShieldCheck,
  Ban,
  FileCode,
  Terminal,
  GitBranch,
  AlertTriangle,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { executorApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

// ── Types ────────────────────────────────────────────────────────────────────

interface ExecutionRun {
  id: string
  status: string
  plan_summary: string
  repo: { id: string; name: string; repo_url: string } | null
  repo_url: string
  base_branch: string
  working_branch: string
  steps_completed: number
  steps_total: number
  current_step: string
  current_step_index: number
  awaiting_approval_step_id: string
  error_message: string
  execution_time_seconds: number | null
  changed_files: string[]
  conversation_id: string
  created_at: string
  started_at: string | null
  completed_at: string | null
}

interface RunDetail extends ExecutionRun {
  plan_json: {
    version: string
    title: string
    steps: Array<{
      id: string
      type: string
      description: string
      cmd?: string
      patch?: string
      requires_approval?: boolean
      network?: string
    }>
  }
  test_summary: Record<string, unknown>
  blocked_steps: number[]
  approval_required_steps: number[]
  approved_steps: string[]
}

// ── Status helpers ───────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<string, { icon: typeof Play; color: string; bg: string }> = {
  queued: { icon: Clock, color: 'text-amber-400', bg: 'bg-amber-400/10' },
  running: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-400/10' },
  awaiting_approval: { icon: ShieldCheck, color: 'text-purple-400', bg: 'bg-purple-400/10' },
  succeeded: { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-400/10' },
  failed: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-400/10' },
  canceled: { icon: Ban, color: 'text-gray-400', bg: 'bg-gray-400/10' },
}

function StatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.queued
  const Icon = config.icon
  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium', config.bg, config.color)}>
      <Icon className={cn('w-3.5 h-3.5', status === 'running' && 'animate-spin')} />
      {status.replace('_', ' ')}
    </span>
  )
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

// ── Run List View ────────────────────────────────────────────────────────────

function RunListView({ onSelect }: { onSelect: (id: string) => void }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['executor-runs'],
    queryFn: async () => {
      const res = await executorApi.list()
      return res.data.runs as ExecutionRun[]
    },
    refetchInterval: 5000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        Loading runs...
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400">
        <AlertTriangle className="w-5 h-5 mr-2" />
        Failed to load runs
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <Terminal className="w-10 h-10 mb-3 opacity-50" />
        <p className="text-sm">No execution runs yet</p>
        <p className="text-xs mt-1 opacity-60">Runs are created by the PA via the collaboration protocol</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {data.map((run) => (
        <button
          key={run.id}
          onClick={() => onSelect(run.id)}
          className="w-full p-4 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/50 transition-colors text-left"
        >
          <div className="flex items-center justify-between mb-2">
            <StatusBadge status={run.status} />
            <span className="text-xs text-gray-500">{timeAgo(run.created_at)}</span>
          </div>
          <p className="text-sm text-gray-200 font-medium truncate">{run.plan_summary || 'Untitled run'}</p>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Terminal className="w-3 h-3" />
              {run.steps_completed}/{run.steps_total} steps
            </span>
            {run.working_branch && (
              <span className="flex items-center gap-1">
                <GitBranch className="w-3 h-3" />
                {run.working_branch}
              </span>
            )}
            {run.changed_files && run.changed_files.length > 0 && (
              <span className="flex items-center gap-1">
                <FileCode className="w-3 h-3" />
                {run.changed_files.length} files
              </span>
            )}
            {run.execution_time_seconds && (
              <span>{run.execution_time_seconds.toFixed(1)}s</span>
            )}
            <ChevronRight className="w-3.5 h-3.5 ml-auto" />
          </div>
        </button>
      ))}
    </div>
  )
}

// ── Run Detail View ──────────────────────────────────────────────────────────

function RunDetailView({ runId, onBack }: { runId: string; onBack: () => void }) {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'plan' | 'logs' | 'diff'>('plan')

  const { data: run, isLoading } = useQuery({
    queryKey: ['executor-run', runId],
    queryFn: async () => {
      const res = await executorApi.detail(runId)
      return res.data.run as RunDetail
    },
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'running' || status === 'queued' ? 3000 : false
    },
  })

  const { data: logsData } = useQuery({
    queryKey: ['executor-run-logs', runId],
    queryFn: async () => {
      const res = await executorApi.logs(runId)
      return res.data.log as string
    },
    enabled: activeTab === 'logs',
    refetchInterval: () => {
      return run?.status === 'running' ? 3000 : false
    },
  })

  const { data: diffData } = useQuery({
    queryKey: ['executor-run-diff', runId],
    queryFn: async () => {
      const res = await executorApi.diff(runId)
      return { diff: res.data.diff as string, files: res.data.changed_files as string[] }
    },
    enabled: activeTab === 'diff' && run?.status === 'succeeded',
  })

  const cancelMutation = useMutation({
    mutationFn: () => executorApi.cancel(runId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['executor-run', runId] })
      queryClient.invalidateQueries({ queryKey: ['executor-runs'] })
    },
  })

  const approveStepMutation = useMutation({
    mutationFn: (stepId: string) => executorApi.approveStep(runId, stepId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['executor-run', runId] })
      queryClient.invalidateQueries({ queryKey: ['executor-runs'] })
    },
  })

  const approveAllMutation = useMutation({
    mutationFn: () => executorApi.approve(runId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['executor-run', runId] })
      queryClient.invalidateQueries({ queryKey: ['executor-runs'] })
    },
  })

  if (isLoading || !run) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        Loading run...
      </div>
    )
  }

  const steps = run.plan_json?.steps || []
  const approvedSet = new Set(run.approved_steps || [])

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-1.5 rounded-lg hover:bg-dark-border transition-colors">
          <ArrowLeft className="w-4 h-4 text-gray-400" />
        </button>
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-gray-100 truncate">
            {run.plan_summary || 'Untitled run'}
          </h2>
          <p className="text-xs text-gray-500 font-mono">{run.id}</p>
        </div>
        <StatusBadge status={run.status} />
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetaCard label="Steps" value={`${run.steps_completed}/${run.steps_total}`} />
        <MetaCard label="Branch" value={run.working_branch || '-'} />
        <MetaCard label="Changed Files" value={String(run.changed_files?.length || 0)} />
        <MetaCard label="Duration" value={run.execution_time_seconds ? `${run.execution_time_seconds.toFixed(1)}s` : '-'} />
      </div>

      {/* Error banner */}
      {run.status === 'failed' && run.error_message && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
          <span className="font-medium">Error:</span> {run.error_message}
        </div>
      )}

      {/* Awaiting approval banner */}
      {run.status === 'awaiting_approval' && (
        <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-300 font-medium text-sm">Approval Required</p>
              <p className="text-purple-400/70 text-xs mt-0.5">
                Step <span className="font-mono">{run.awaiting_approval_step_id}</span> needs approval to continue
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => approveStepMutation.mutate(run.awaiting_approval_step_id)}
                disabled={approveStepMutation.isPending}
                className="px-3 py-1.5 rounded-lg bg-purple-500 hover:bg-purple-400 text-white text-sm font-medium transition-colors disabled:opacity-50"
              >
                {approveStepMutation.isPending ? 'Approving...' : 'Approve Step'}
              </button>
              <button
                onClick={() => approveAllMutation.mutate()}
                disabled={approveAllMutation.isPending}
                className="px-3 py-1.5 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-sm font-medium transition-colors border border-purple-500/40 disabled:opacity-50"
              >
                Approve All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      {(run.status === 'queued' || run.status === 'running') && (
        <div className="flex gap-2">
          <button
            onClick={() => cancelMutation.mutate()}
            disabled={cancelMutation.isPending}
            className="px-3 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-300 text-sm font-medium transition-colors border border-red-500/30 disabled:opacity-50"
          >
            {cancelMutation.isPending ? 'Canceling...' : 'Cancel Run'}
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-dark-border">
        {(['plan', 'logs', 'diff'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              'px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px',
              activeTab === tab
                ? 'text-primary-400 border-primary-500'
                : 'text-gray-500 border-transparent hover:text-gray-300'
            )}
          >
            {tab === 'plan' ? 'Plan' : tab === 'logs' ? 'Logs' : 'Diff'}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'plan' && (
        <div className="space-y-2">
          {steps.length === 0 ? (
            <p className="text-sm text-gray-500">No steps in plan</p>
          ) : (
            steps.map((step, i) => {
              const isCompleted = i < run.steps_completed
              const isCurrent = i === run.current_step_index && run.status === 'running'
              const isAwaiting = step.id === run.awaiting_approval_step_id && run.status === 'awaiting_approval'
              const isApproved = approvedSet.has(step.id)

              return (
                <div
                  key={step.id}
                  className={cn(
                    'p-3 rounded-lg border text-sm',
                    isCompleted && 'bg-green-500/5 border-green-500/20',
                    isCurrent && 'bg-blue-500/10 border-blue-500/30',
                    isAwaiting && 'bg-purple-500/10 border-purple-500/30',
                    !isCompleted && !isCurrent && !isAwaiting && 'bg-dark-bg border-dark-border'
                  )}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-gray-500">{step.id}</span>
                    <span className={cn(
                      'text-xs px-1.5 py-0.5 rounded',
                      step.type === 'shell' ? 'bg-cyan-500/10 text-cyan-400' : 'bg-amber-500/10 text-amber-400'
                    )}>
                      {step.type}
                    </span>
                    {step.requires_approval && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400">approval</span>
                    )}
                    {step.network === 'on' && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400">network</span>
                    )}
                    {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-green-400 ml-auto" />}
                    {isCurrent && <Loader2 className="w-3.5 h-3.5 text-blue-400 ml-auto animate-spin" />}
                    {isAwaiting && <ShieldCheck className="w-3.5 h-3.5 text-purple-400 ml-auto" />}
                    {isApproved && !isCompleted && (
                      <span className="text-xs text-green-400 ml-auto">approved</span>
                    )}
                  </div>
                  <p className="text-gray-300">{step.description}</p>
                  {step.cmd && (
                    <pre className="mt-1.5 text-xs bg-dark-bg p-2 rounded font-mono text-gray-400 overflow-x-auto">
                      {step.cmd}
                    </pre>
                  )}
                </div>
              )
            })
          )}
        </div>
      )}

      {activeTab === 'logs' && (
        <pre className="p-4 rounded-lg bg-dark-bg border border-dark-border text-xs font-mono text-gray-300 overflow-auto max-h-[500px] whitespace-pre-wrap">
          {logsData || 'No logs available'}
        </pre>
      )}

      {activeTab === 'diff' && (
        <div>
          {run.status !== 'succeeded' ? (
            <p className="text-sm text-gray-500">Diff available after run succeeds</p>
          ) : diffData?.diff ? (
            <>
              {diffData.files && diffData.files.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-1.5">
                  {diffData.files.map((f) => (
                    <span key={f} className="text-xs px-2 py-0.5 rounded bg-dark-bg border border-dark-border text-gray-400 font-mono">
                      {f}
                    </span>
                  ))}
                </div>
              )}
              <pre className="p-4 rounded-lg bg-dark-bg border border-dark-border text-xs font-mono text-gray-300 overflow-auto max-h-[500px] whitespace-pre-wrap">
                {diffData.diff}
              </pre>
            </>
          ) : (
            <p className="text-sm text-gray-500">No changes produced</p>
          )}
        </div>
      )}
    </div>
  )
}

function MetaCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 rounded-lg bg-dark-card border border-dark-border">
      <p className="text-xs text-gray-500 mb-0.5">{label}</p>
      <p className="text-sm text-gray-200 font-medium truncate">{value}</p>
    </div>
  )
}

// ── Main Page ────────────────────────────────────────────────────────────────

export default function ExecutorPage() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Breadcrumb currentPage="Executor" />

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Executor</h1>
          <p className="text-sm text-gray-500 mt-1">Plan-based code execution runs</p>
        </div>
      </div>

      {selectedRunId ? (
        <RunDetailView runId={selectedRunId} onBack={() => setSelectedRunId(null)} />
      ) : (
        <RunListView onSelect={setSelectedRunId} />
      )}
    </div>
  )
}
