/**
 * Session 819: Deliverables Marketplace - Jobs Panel
 *
 * Execution tracking panel showing:
 * - Running jobs with progress
 * - Queued jobs
 * - Recently completed jobs
 * - Cancel/retry actions
 */

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Play, Clock, CheckCircle, XCircle, RefreshCw,
  Loader2, AlertTriangle, Bot, ChevronDown, ChevronRight,
  StopCircle, RotateCcw, Zap
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { workspaceOperationsApi } from '@/lib/api'

interface Job {
  id: string
  agent_name: string
  task: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  started_at?: string
  completed_at?: string
  error?: string
  output_preview?: string
  deliverable_id?: string
}

interface JobsPanelProps {
  onJobClick?: (job: Job) => void
  onDeliverableClick?: (deliverableId: string) => void
}

// API functions
async function fetchJobs(): Promise<{
  running: Job[]
  queued: Job[]
  completed: Job[]
}> {
  // Session 860: Fixed to use correct endpoint /api/workspace-operations/
  const response = await workspaceOperationsApi.list({
    status: 'pending,running,completed,failed',
    limit: 50
  })
  const data = response.data

  // Transform operations into jobs format
  const operations = data.operations || []
  const running: Job[] = []
  const queued: Job[] = []
  const completed: Job[] = []

  operations.forEach((op: any) => {
    const job: Job = {
      id: op.id,
      agent_name: op.agent_name || 'Unknown Agent',
      task: op.description || op.command || 'Processing...',
      status: op.status,
      progress: op.status === 'running' ? 50 : op.status === 'completed' ? 100 : 0,
      started_at: op.started_at || op.created_at,
      completed_at: op.completed_at,
      error: op.error_message,
      output_preview: op.output_data?.preview,
      deliverable_id: op.deliverable_id
    }

    if (op.status === 'running') {
      running.push(job)
    } else if (op.status === 'pending') {
      queued.push(job)
    } else {
      completed.push(job)
    }
  })

  return { running, queued, completed }
}

async function cancelJob(jobId: string): Promise<void> {
  const response = await fetch(`/api/workspace/operations/${jobId}/cancel/`, {
    method: 'POST',
    credentials: 'include'
  })
  if (!response.ok) {
    throw new Error('Failed to cancel job')
  }
}

async function retryJob(jobId: string): Promise<void> {
  const response = await fetch(`/api/workspace/operations/${jobId}/retry/`, {
    method: 'POST',
    credentials: 'include'
  })
  if (!response.ok) {
    throw new Error('Failed to retry job')
  }
}

export function JobsPanel({ onJobClick, onDeliverableClick }: JobsPanelProps) {
  const queryClient = useQueryClient()
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['running', 'queued'])
  )

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    refetchInterval: 5000 // Poll every 5 seconds for running jobs
  })

  const cancelMutation = useMutation({
    mutationFn: cancelJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    }
  })

  const retryMutation = useMutation({
    mutationFn: retryJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    }
  })

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const runningJobs = data?.running || []
  const queuedJobs = data?.queued || []
  const completedJobs = data?.completed || []

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-zinc-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-yellow-400" />
            <h3 className="text-lg font-medium text-zinc-100">Jobs</h3>
            {runningJobs.length > 0 && (
              <span className="px-2 py-0.5 text-xs font-medium bg-green-500/20 text-green-400 rounded-full">
                {runningJobs.length} running
              </span>
            )}
          </div>

          <button
            onClick={() => refetch()}
            className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-48">
            <Loader2 className="w-6 h-6 text-zinc-400 animate-spin" />
          </div>
        ) : (
          <>
            {/* Running Jobs */}
            <JobSection
              title="Running"
              icon={<Play className="w-4 h-4 text-green-400" />}
              jobs={runningJobs}
              isExpanded={expandedSections.has('running')}
              onToggle={() => toggleSection('running')}
              onCancel={(id) => cancelMutation.mutate(id)}
              onJobClick={onJobClick}
              onDeliverableClick={onDeliverableClick}
                          />

            {/* Queued Jobs */}
            <JobSection
              title="Queued"
              icon={<Clock className="w-4 h-4 text-amber-400" />}
              jobs={queuedJobs}
              isExpanded={expandedSections.has('queued')}
              onToggle={() => toggleSection('queued')}
              onCancel={(id) => cancelMutation.mutate(id)}
              onJobClick={onJobClick}
              onDeliverableClick={onDeliverableClick}
                          />

            {/* Completed Jobs */}
            <JobSection
              title="Recent"
              icon={<CheckCircle className="w-4 h-4 text-zinc-400" />}
              jobs={completedJobs.slice(0, 20)}
              isExpanded={expandedSections.has('completed')}
              onToggle={() => toggleSection('completed')}
              onRetry={(id) => retryMutation.mutate(id)}
              onJobClick={onJobClick}
              onDeliverableClick={onDeliverableClick}
                          />
          </>
        )}

        {/* Empty state */}
        {!isLoading && runningJobs.length === 0 && queuedJobs.length === 0 && completedJobs.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-zinc-500">
            <Zap className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-lg font-medium">No jobs</p>
            <p className="text-sm mt-1">Agent executions will appear here</p>
          </div>
        )}
      </div>
    </div>
  )
}

function JobSection({
  title,
  icon,
  jobs,
  isExpanded,
  onToggle,
  onCancel,
  onRetry,
  onJobClick,
  onDeliverableClick
}: {
  title: string
  icon: React.ReactNode
  jobs: Job[]
  isExpanded: boolean
  onToggle: () => void
  onCancel?: (id: string) => void
  onRetry?: (id: string) => void
  onJobClick?: (job: Job) => void
  onDeliverableClick?: (deliverableId: string) => void
}) {
  if (jobs.length === 0) return null

  return (
    <div>
      <button
        onClick={onToggle}
        className="flex items-center gap-2 w-full p-2 hover:bg-zinc-800/50 rounded-lg transition-colors"
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-zinc-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-zinc-400" />
        )}
        {icon}
        <span className="text-sm font-medium text-zinc-300">{title}</span>
        <span className="px-1.5 py-0.5 text-xs bg-zinc-700 text-zinc-400 rounded-full">
          {jobs.length}
        </span>
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-2 pl-6">
          {jobs.map(job => (
            <JobCard
              key={job.id}
              job={job}
              onCancel={onCancel}
              onRetry={onRetry}
              onClick={() => onJobClick?.(job)}
              onDeliverableClick={onDeliverableClick}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function JobCard({
  job,
  onCancel,
  onRetry,
  onClick,
  onDeliverableClick
}: {
  job: Job
  onCancel?: (id: string) => void
  onRetry?: (id: string) => void
  onClick?: () => void
  onDeliverableClick?: (deliverableId: string) => void
}) {
  const statusConfig: Record<string, { icon: React.ElementType; color: string }> = {
    pending: { icon: Clock, color: 'text-amber-400' },
    running: { icon: Loader2, color: 'text-green-400' },
    completed: { icon: CheckCircle, color: 'text-green-400' },
    failed: { icon: XCircle, color: 'text-red-400' },
    cancelled: { icon: StopCircle, color: 'text-zinc-400' }
  }

  const config = statusConfig[job.status] || statusConfig.pending
  const StatusIcon = config.icon

  // Format time
  const formatTime = (dateStr?: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-zinc-800/50 rounded-lg p-3 cursor-pointer',
        'hover:bg-zinc-800 transition-colors'
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className={cn('mt-0.5', config.color)}>
            <StatusIcon className={cn(
              'w-4 h-4',
              job.status === 'running' && 'animate-spin'
            )} />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-zinc-200 truncate">
                {job.agent_name}
              </span>
              {job.status === 'running' && (
                <span className="text-xs text-green-400">
                  {job.progress}%
                </span>
              )}
            </div>

            <p className="text-xs text-zinc-400 truncate mt-0.5">
              {job.task}
            </p>

            {job.error && (
              <p className="text-xs text-red-400 mt-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                {job.error}
              </p>
            )}

            <div className="flex items-center gap-3 mt-2 text-xs text-zinc-500">
              {job.started_at && (
                <span>Started: {formatTime(job.started_at)}</span>
              )}
              {job.completed_at && (
                <span>Completed: {formatTime(job.completed_at)}</span>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 ml-2">
          {(job.status === 'pending' || job.status === 'running') && onCancel && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onCancel(job.id)
              }}
              className="p-1.5 text-zinc-500 hover:text-red-400 transition-colors"
              title="Cancel"
            >
              <StopCircle className="w-4 h-4" />
            </button>
          )}

          {job.status === 'failed' && onRetry && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onRetry(job.id)
              }}
              className="p-1.5 text-zinc-500 hover:text-green-400 transition-colors"
              title="Retry"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          )}

          {job.deliverable_id && onDeliverableClick && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDeliverableClick(job.deliverable_id!)
              }}
              className="p-1.5 text-zinc-500 hover:text-blue-400 transition-colors"
              title="View Deliverable"
            >
              <Bot className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Progress bar for running jobs */}
      {job.status === 'running' && (
        <div className="mt-3 h-1 bg-zinc-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 transition-all duration-300"
            style={{ width: `${job.progress}%` }}
          />
        </div>
      )}
    </div>
  )
}

export default JobsPanel
