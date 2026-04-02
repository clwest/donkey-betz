/**
 * WorkspaceDashboardPage — Per-workspace business dashboard.
 *
 * Shows workspace metrics, pipeline status, and a "Run Pipeline" button.
 * Polls for pipeline progress in real-time.
 */

import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '@/lib/api'
import {
  ArrowLeft, Play, CheckCircle2, XCircle, Clock, Loader2,
  BarChart3, FileText, Bot, Zap, Pause, AlertCircle,
} from 'lucide-react'

interface StageResult {
  stage_index: number
  name: string
  agent: string | null
  auto: boolean
  requires_approval: boolean
  status: string
  started_at: string | null
  finished_at: string | null
  output: Record<string, unknown> | null
  error: string | null
}

interface PipelineRun {
  id: string
  status: string
  progress_pct: number
  current_stage_index: number
  stages: StageResult[]
  started_at: string | null
  finished_at: string | null
  duration_seconds: number | null
  error_message: string
  created_at: string
}

interface DashboardData {
  workspace: {
    id: string
    name: string
    description: string
    template: string
    status: string
    governance_mode: string
    created_at: string
  }
  metrics: {
    deliverables_total: number
    deliverables_saved: number
    by_category: Record<string, number>
    by_type: Record<string, number>
    initiative_count: number
  }
  pipeline: Array<{
    name: string
    agent: string | null
    auto: boolean
    requires_approval: boolean
    deliverable_count: number
    description: string
  }>
  settings: Record<string, unknown>
}

const STAGE_ICONS: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 size={16} className="text-green-400" />,
  failed: <XCircle size={16} className="text-red-400" />,
  running: <Loader2 size={16} className="text-blue-400 animate-spin" />,
  pending: <Clock size={16} className="text-gray-500" />,
  skipped: <Pause size={16} className="text-gray-600" />,
  awaiting_approval: <AlertCircle size={16} className="text-yellow-400" />,
}

export default function WorkspaceDashboardPage() {
  const { workspaceId } = useParams<{ workspaceId: string }>()
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [pipelineRun, setPipelineRun] = useState<PipelineRun | null>(null)
  const [loading, setLoading] = useState(true)
  const [runningPipeline, setRunningPipeline] = useState(false)

  const fetchDashboard = useCallback(async () => {
    if (!workspaceId) return
    try {
      const res = await api.get(`/workspaces/${workspaceId}/dashboard/`)
      if (res.data.success) setDashboard(res.data)
    } catch (err) {
      console.error('Failed to fetch dashboard:', err)
    } finally {
      setLoading(false)
    }
  }, [workspaceId])

  const fetchPipelineStatus = useCallback(async () => {
    if (!workspaceId) return
    try {
      const res = await api.get(`/workspaces/${workspaceId}/pipeline/status/`)
      if (res.data.success && res.data.run) {
        setPipelineRun(res.data.run)
      }
    } catch { /* no runs yet */ }
  }, [workspaceId])

  useEffect(() => {
    fetchDashboard()
    fetchPipelineStatus()
  }, [fetchDashboard, fetchPipelineStatus])

  // Poll pipeline status while running
  useEffect(() => {
    if (!pipelineRun || pipelineRun.status !== 'running') return
    const interval = setInterval(fetchPipelineStatus, 3000)
    return () => clearInterval(interval)
  }, [pipelineRun?.status, fetchPipelineStatus])

  const handleRunPipeline = async () => {
    if (!workspaceId) return
    setRunningPipeline(true)
    try {
      const res = await api.post(`/workspaces/${workspaceId}/pipeline/run/`)
      if (res.data.success) {
        setPipelineRun({
          id: res.data.run_id,
          status: 'pending',
          progress_pct: 0,
          current_stage_index: 0,
          stages: res.data.stages,
          started_at: null,
          finished_at: null,
          duration_seconds: null,
          error_message: '',
          created_at: new Date().toISOString(),
        })
        // Start polling
        setTimeout(fetchPipelineStatus, 2000)
      }
    } catch (err) {
      console.error('Failed to start pipeline:', err)
    } finally {
      setRunningPipeline(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        <Loader2 className="animate-spin mr-2" size={20} /> Loading workspace...
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div className="p-6 text-center text-gray-500">
        Workspace not found.
        <Link to="/workspace" className="text-blue-400 ml-2">Back to workspaces</Link>
      </div>
    )
  }

  const { workspace, metrics, pipeline } = dashboard
  const isPipelineRunning = pipelineRun?.status === 'running' || pipelineRun?.status === 'pending'

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Link to="/workspace" className="text-gray-400 hover:text-white">
              <ArrowLeft size={20} />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white">{workspace.name}</h1>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-sm text-gray-400">{workspace.template}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  workspace.status === 'active' ? 'bg-green-900/30 text-green-300' :
                  workspace.status === 'paused' ? 'bg-yellow-900/30 text-yellow-300' :
                  'bg-gray-800 text-gray-400'
                }`}>{workspace.status}</span>
                <span className="text-xs text-gray-600">
                  Governance: {workspace.governance_mode}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={handleRunPipeline}
            disabled={isPipelineRunning || runningPipeline}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
          >
            {isPipelineRunning ? (
              <><Loader2 size={16} className="animate-spin" /> Running...</>
            ) : (
              <><Play size={16} /> Run Pipeline</>
            )}
          </button>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <FileText size={14} /> Deliverables
            </div>
            <div className="text-2xl font-bold text-white">{metrics.deliverables_total}</div>
            <div className="text-xs text-gray-500">{metrics.deliverables_saved} saved</div>
          </div>
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <Zap size={14} /> Initiatives
            </div>
            <div className="text-2xl font-bold text-white">{metrics.initiative_count}</div>
          </div>
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <Bot size={14} /> Pipeline Stages
            </div>
            <div className="text-2xl font-bold text-white">{pipeline.length}</div>
          </div>
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <BarChart3 size={14} /> Categories
            </div>
            <div className="text-2xl font-bold text-white">
              {Object.keys(metrics.by_category).length}
            </div>
          </div>
        </div>

        {/* Pipeline Status */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Pipeline</h2>
            {pipelineRun && (
              <div className="flex items-center gap-3">
                <div className="w-32 bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${pipelineRun.progress_pct}%` }}
                  />
                </div>
                <span className="text-sm text-gray-400">{pipelineRun.progress_pct}%</span>
              </div>
            )}
          </div>

          <div className="space-y-2">
            {(pipelineRun?.stages || pipeline).map((stage, i) => {
              const isRunResult = 'status' in stage
              const status = isRunResult ? (stage as StageResult).status : 'configured'
              const agentName = isRunResult ? (stage as StageResult).agent : (stage as typeof pipeline[0]).agent
              const stageName = isRunResult ? (stage as StageResult).name : (stage as typeof pipeline[0]).name
              const error = isRunResult ? (stage as StageResult).error : null

              return (
                <div
                  key={i}
                  className={`flex items-center gap-3 p-3 rounded-lg ${
                    status === 'running' ? 'bg-blue-950/30 border border-blue-800/30' :
                    status === 'completed' ? 'bg-green-950/20' :
                    status === 'failed' ? 'bg-red-950/20' :
                    'bg-gray-800/30'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center text-sm font-bold text-gray-400">
                    {STAGE_ICONS[status] || <span>{i + 1}</span>}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{stageName}</div>
                    {agentName && (
                      <div className="text-xs text-gray-500">{agentName}</div>
                    )}
                    {error && (
                      <div className="text-xs text-red-400 mt-0.5">{error}</div>
                    )}
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    status === 'completed' ? 'bg-green-900/30 text-green-300' :
                    status === 'running' ? 'bg-blue-900/30 text-blue-300' :
                    status === 'failed' ? 'bg-red-900/30 text-red-300' :
                    status === 'awaiting_approval' ? 'bg-yellow-900/30 text-yellow-300' :
                    'bg-gray-800 text-gray-500'
                  }`}>
                    {status}
                  </span>
                </div>
              )
            })}
          </div>

          {pipelineRun?.duration_seconds != null && (
            <div className="mt-3 text-xs text-gray-500 text-right">
              Completed in {Math.round(pipelineRun.duration_seconds)}s
            </div>
          )}
        </div>

        {/* Deliverable Categories */}
        {Object.keys(metrics.by_category).length > 0 && (
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Output by Category</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(metrics.by_category).map(([cat, count]) => (
                <div key={cat} className="flex items-center justify-between bg-gray-800/50 rounded-lg px-3 py-2">
                  <span className="text-sm text-gray-300">{cat || 'Uncategorized'}</span>
                  <span className="text-sm font-semibold text-white">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
