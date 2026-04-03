/**
 * DemoPipelineCard — "First Win" onboarding component.
 *
 * One button, one outcome: run a quick demo pipeline that produces
 * a real deliverable in ~60 seconds. Shows progress in real-time.
 *
 * The moment where a new user goes from "I don't understand this system"
 * to "Oh — this actually does something."
 */

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import { Rocket, Loader2, CheckCircle2, XCircle, FileText, ArrowRight } from 'lucide-react'

interface DemoStage {
  name: string
  status: string
}

interface DemoState {
  status: string
  topic: string
  stages: DemoStage[]
  progress_pct: number
  deliverable_id: string | null
  message: string
  error?: string
}

export default function DemoPipelineCard() {
  const [demoState, setDemoState] = useState<DemoState | null>(null)
  const [running, setRunning] = useState(false)
  const [dismissed, setDismissed] = useState(() => {
    return localStorage.getItem('demo-pipeline-dismissed') === 'true'
  })
  const [runId, setRunId] = useState<string | null>(null)
  const [customTopic, setCustomTopic] = useState('')

  const startDemo = async () => {
    setRunning(true)
    try {
      const res = await api.post('/demo-pipeline/run/', {
        topic: customTopic.trim() || undefined,
      })
      if (res.data.success) {
        setRunId(res.data.run_id)
        setDemoState({
          status: 'running',
          topic: res.data.topic,
          stages: [
            { name: 'Quick Research', status: 'pending' },
            { name: 'Quality Check', status: 'pending' },
            { name: 'Create Deliverable', status: 'pending' },
          ],
          progress_pct: 0,
          deliverable_id: null,
          message: res.data.message,
        })
      }
    } catch (err) {
      console.error('Failed to start demo:', err)
      setRunning(false)
    }
  }

  const pollStatus = useCallback(async () => {
    if (!runId) return
    try {
      const res = await api.get(`/demo-pipeline/status/${runId}/`)
      if (res.data.success) {
        setDemoState(res.data)
        if (res.data.status === 'completed' || res.data.status === 'failed') {
          setRunning(false)
        }
      }
    } catch { /* ignore */ }
  }, [runId])

  useEffect(() => {
    if (!runId || !running) return
    const interval = setInterval(pollStatus, 2000)
    return () => clearInterval(interval)
  }, [runId, running, pollStatus])

  const dismiss = () => {
    setDismissed(true)
    localStorage.setItem('demo-pipeline-dismissed', 'true')
  }

  if (dismissed) return null

  // Not started yet — show the CTA
  if (!demoState) {
    return (
      <div className="bg-gradient-to-r from-blue-950/40 to-purple-950/30 rounded-xl border border-blue-800/30 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-blue-600/20">
            <Rocket size={24} className="text-blue-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-1">See it in action</h3>
            <p className="text-sm text-gray-400 mb-4">
              Want to see this actually work? I can run a quick research pipeline and
              produce a real deliverable in about 60 seconds.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 mb-3">
              <input
                type="text"
                value={customTopic}
                onChange={e => setCustomTopic(e.target.value)}
                placeholder="Enter a topic (or leave blank for a sample)"
                className="flex-1 bg-gray-900/50 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={startDemo}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <Rocket size={16} /> Run demo pipeline
              </button>
              <button
                onClick={dismiss}
                className="text-xs text-gray-500 hover:text-gray-400 px-3 py-2"
              >
                Not now
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Running or completed — show progress
  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Rocket size={18} className="text-blue-400" />
          <h3 className="text-sm font-semibold text-white">Demo Pipeline: {demoState.topic}</h3>
        </div>
        {demoState.status === 'completed' && (
          <button onClick={dismiss} className="text-xs text-gray-500 hover:text-gray-400">Dismiss</button>
        )}
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-800 rounded-full h-2 mb-4">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            demoState.status === 'failed' ? 'bg-red-500' :
            demoState.status === 'completed' ? 'bg-green-500' :
            'bg-blue-500'
          }`}
          style={{ width: `${demoState.progress_pct}%` }}
        />
      </div>

      {/* Stages */}
      <div className="space-y-2 mb-4">
        {demoState.stages.map((stage, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            {stage.status === 'completed' ? (
              <CheckCircle2 size={16} className="text-green-400" />
            ) : stage.status === 'running' ? (
              <Loader2 size={16} className="text-blue-400 animate-spin" />
            ) : stage.status === 'failed' ? (
              <XCircle size={16} className="text-red-400" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-gray-600" />
            )}
            <span className={stage.status === 'running' ? 'text-blue-300' : 'text-gray-400'}>
              {stage.name}
            </span>
          </div>
        ))}
      </div>

      {/* Success state */}
      {demoState.status === 'completed' && demoState.deliverable_id && (
        <div className="bg-green-950/30 border border-green-800/30 rounded-lg p-4">
          <div className="flex items-center gap-2 text-green-300 font-medium text-sm mb-2">
            <CheckCircle2 size={16} /> Your first deliverable is ready!
          </div>
          <p className="text-xs text-gray-400 mb-3">
            Rigby just researched "{demoState.topic}" and created a summary with sources.
          </p>
          <div className="flex gap-2">
            <a
              href={`/workspace?tab=deliverables`}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white text-xs rounded-lg transition-colors"
            >
              <FileText size={14} /> Open deliverable
            </a>
            <a
              href="/workspace/new"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded-lg transition-colors"
            >
              <ArrowRight size={14} /> Create a full workspace
            </a>
          </div>
        </div>
      )}

      {/* Failure state */}
      {demoState.status === 'failed' && (
        <div className="bg-red-950/30 border border-red-800/30 rounded-lg p-3">
          <p className="text-xs text-red-400 mb-2">
            {demoState.error || 'Demo ran into an issue. This happens sometimes with new topics.'}
          </p>
          <button
            onClick={() => { setDemoState(null); setRunId(null); setRunning(false) }}
            className="text-xs px-3 py-1.5 bg-red-900/50 hover:bg-red-900/70 text-red-300 rounded-lg"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  )
}
