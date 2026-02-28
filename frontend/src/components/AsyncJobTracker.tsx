/**
 * Session 1075: Inline async job tracker for PA chat.
 * Polls Celery task status and shows progress for image generation, etc.
 */

import { useState, useEffect, useRef } from 'react'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'
import { getJobStatus } from '@/lib/cockpitApi'

interface AsyncJob {
  task_id: string
  agent: string
  status: 'pending' | 'started' | 'success' | 'failed'
  duration_ms?: number
}

interface Props {
  jobs: AsyncJob[]
}

const AGENT_LABELS: Record<string, string> = {
  ImageAgent: 'Generating image',
  ContentWriterAgent: 'Writing content',
  ResearchAgent: 'Researching',
  LegalDocDrafterAgent: 'Drafting document',
}

export default function AsyncJobTracker({ jobs }: Props) {
  const [trackedJobs, setTrackedJobs] = useState<AsyncJob[]>(jobs)
  const pollRefs = useRef<Record<string, ReturnType<typeof setInterval>>>({})

  useEffect(() => {
    trackedJobs.forEach((job) => {
      if ((job.status === 'pending' || job.status === 'started') && !pollRefs.current[job.task_id]) {
        pollRefs.current[job.task_id] = setInterval(async () => {
          try {
            const data = await getJobStatus(job.task_id)
            const newStatus = data.status === 'completed' ? 'success'
              : data.status === 'failed' ? 'failed'
              : data.status === 'processing' ? 'started'
              : 'pending'

            setTrackedJobs((prev) =>
              prev.map((j) =>
                j.task_id !== job.task_id ? j : { ...j, status: newStatus }
              )
            )

            if (newStatus === 'success' || newStatus === 'failed') {
              clearInterval(pollRefs.current[job.task_id])
              delete pollRefs.current[job.task_id]
            }
          } catch {
            // Keep polling on transient errors
          }
        }, 3000)
      }
    })

    return () => {
      Object.values(pollRefs.current).forEach(clearInterval)
      pollRefs.current = {}
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (trackedJobs.length === 0) return null

  return (
    <div className="mt-3 space-y-2">
      {trackedJobs.map((job) => (
        <div
          key={job.task_id}
          className={`flex items-center gap-3 px-3 py-2 rounded-lg border text-sm ${
            job.status === 'success'
              ? 'border-green-500/30 bg-green-500/5'
              : job.status === 'failed'
              ? 'border-red-500/30 bg-red-500/5'
              : 'border-primary-500/30 bg-primary-500/5'
          }`}
        >
          {job.status === 'success' ? (
            <CheckCircle size={16} className="text-green-400 shrink-0" />
          ) : job.status === 'failed' ? (
            <XCircle size={16} className="text-red-400 shrink-0" />
          ) : (
            <Loader2 size={16} className="text-primary-400 animate-spin shrink-0" />
          )}

          <span className="text-gray-300">
            {AGENT_LABELS[job.agent] || job.agent}
          </span>

          {(job.status === 'pending' || job.status === 'started') && (
            <ElapsedTimer />
          )}

          {job.status === 'success' && (
            <span className="text-xs text-green-400 ml-auto">Done</span>
          )}
          {job.status === 'failed' && (
            <span className="text-xs text-red-400 ml-auto">Failed</span>
          )}
        </div>
      ))}
    </div>
  )
}

function ElapsedTimer() {
  const [elapsed, setElapsed] = useState(0)
  const startRef = useRef(Date.now())

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startRef.current) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <span className="text-xs text-gray-500 font-mono ml-auto">
      {elapsed}s
    </span>
  )
}
