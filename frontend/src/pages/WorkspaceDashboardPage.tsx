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
  Save, MessageSquare, PenLine,
} from 'lucide-react'
import { usePAStore } from '@/stores/paStore'

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

  // Workspace brief state
  const [brief, setBrief] = useState<Record<string, string | string[]>>({
    topic: '', audience: '', tone: '', focus_areas: [], notes: '',
  })
  const [briefDirty, setBriefDirty] = useState(false)
  const [savingBrief, setSavingBrief] = useState(false)

  const fetchDashboard = useCallback(async () => {
    if (!workspaceId) return
    try {
      const res = await api.get(`/workspaces/${workspaceId}/biz-dashboard/`)
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

  // Load brief from config on first load
  const fetchConfig = useCallback(async () => {
    if (!workspaceId) return
    try {
      const res = await api.get(`/workspaces/${workspaceId}/config/`)
      if (res.data.success && res.data.config?.workspace_brief) {
        setBrief(res.data.config.workspace_brief)
      }
    } catch { /* no config */ }
  }, [workspaceId])

  const saveBrief = async () => {
    if (!workspaceId) return
    setSavingBrief(true)
    try {
      await api.patch(`/workspaces/${workspaceId}/config/`, { workspace_brief: brief })
      setBriefDirty(false)
    } catch (err) {
      console.error('Failed to save brief:', err)
    } finally {
      setSavingBrief(false)
    }
  }

  const updateBrief = (field: string, value: string | string[]) => {
    setBrief(prev => ({ ...prev, [field]: value }))
    setBriefDirty(true)
  }

  useEffect(() => {
    fetchDashboard()
    fetchPipelineStatus()
    fetchConfig()
  }, [fetchDashboard, fetchPipelineStatus, fetchConfig])

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
  const isPipelineFailed = pipelineRun?.status === 'failed'
  const isPipelineDone = pipelineRun?.status === 'completed'

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

          <div className="flex items-center gap-3">
            {isPipelineFailed && (
              <span className="text-xs text-red-400 bg-red-900/20 px-2 py-1 rounded">
                Last run had failures
              </span>
            )}
            {isPipelineDone && !isPipelineFailed && (
              <span className="text-xs text-green-400 bg-green-900/20 px-2 py-1 rounded">
                Pipeline complete
              </span>
            )}
            <button
              onClick={handleRunPipeline}
              disabled={isPipelineRunning || runningPipeline}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
            >
              {isPipelineRunning ? (
                <><Loader2 size={16} className="animate-spin" /> Running...</>
              ) : isPipelineFailed ? (
                <><Play size={16} /> Retry Pipeline</>
              ) : (
                <><Play size={16} /> Run Pipeline</>
              )}
            </button>
          </div>
        </div>

        {/* Workspace Brief — tells agents what to do */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <PenLine className="text-blue-400" size={18} />
              <h2 className="text-lg font-semibold text-white">Workspace Brief</h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  const msg = `I'm working in the "${workspace.name}" workspace (${workspace.template}). Topic: ${brief.topic || 'not set'}. Help me configure this workspace and decide what to focus on.`
                  usePAStore.getState().setCurrentInput(msg)
                  usePAStore.getState().openDock()
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-900/30 border border-purple-800/30 hover:bg-purple-900/50 text-purple-300 text-sm transition-colors"
              >
                <MessageSquare size={14} /> Ask Rigby
              </button>
              {briefDirty && (
                <button
                  onClick={saveBrief}
                  disabled={savingBrief}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 text-white text-sm rounded-lg transition-colors"
                >
                  <Save size={14} /> {savingBrief ? 'Saving...' : 'Save'}
                </button>
              )}
            </div>
          </div>
          <p className="text-xs text-gray-500 mb-4">
            This brief tells agents what to research, write about, and who the audience is when running the pipeline.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Topic / Focus</label>
              <input
                type="text"
                value={(brief.topic as string) || ''}
                onChange={e => updateBrief('topic', e.target.value)}
                placeholder="e.g., AI trends in enterprise SaaS"
                className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Target Audience</label>
              <input
                type="text"
                value={(brief.audience as string) || ''}
                onChange={e => updateBrief('audience', e.target.value)}
                placeholder="e.g., CTOs and engineering leaders"
                className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Tone</label>
              <input
                type="text"
                value={(brief.tone as string) || ''}
                onChange={e => updateBrief('tone', e.target.value)}
                placeholder="e.g., Professional but approachable"
                className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Focus Areas (comma-separated)</label>
              <input
                type="text"
                value={Array.isArray(brief.focus_areas) ? (brief.focus_areas as string[]).join(', ') : ''}
                onChange={e => updateBrief('focus_areas', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                placeholder="e.g., LLMs, DevOps, Cloud"
                className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="text-xs text-gray-500 mb-1 block">Additional Notes</label>
            <textarea
              value={(brief.notes as string) || ''}
              onChange={e => updateBrief('notes', e.target.value)}
              placeholder="Any specific instructions, preferred sources, things to avoid..."
              rows={2}
              className="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 resize-none"
            />
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Link
            to={`/workspace?tab=deliverables&workspace=${workspaceId}`}
            className="bg-gray-900 rounded-xl border border-gray-800 p-4 hover:border-blue-800/50 transition-colors"
          >
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <FileText size={14} /> Deliverables
            </div>
            <div className="text-2xl font-bold text-white">{metrics.deliverables_total}</div>
            <div className="text-xs text-blue-400">{metrics.deliverables_saved} saved — click to view</div>
          </Link>
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
              const output = isRunResult ? (stage as StageResult).output : null
              const deliverableId = output?.deliverable_id as string | undefined
              // Check if stage is part of a parallel group (from pipeline snapshot)
              const snapshotStage = dashboard.pipeline[i] || {} as Record<string, unknown>
              const parallelGroup = (stage as Record<string, unknown>).parallel_group || (snapshotStage as Record<string, unknown>).parallel_group

              return (
                <div
                  key={i}
                  className={`flex items-center gap-3 p-3 rounded-lg ${
                    status === 'running' ? 'bg-blue-950/30 border border-blue-800/30' :
                    status === 'completed' ? 'bg-green-950/20' :
                    status === 'failed' ? 'bg-red-950/20' :
                    status === 'awaiting_approval' ? 'bg-yellow-950/20 border border-yellow-800/30' :
                    'bg-gray-800/30'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center text-sm font-bold text-gray-400">
                    {STAGE_ICONS[status] || <span>{i + 1}</span>}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white">{stageName}</span>
                      {parallelGroup && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-900/30 text-indigo-300 border border-indigo-800/30">
                          parallel
                        </span>
                      )}
                    </div>
                    {agentName && (
                      <div className="text-xs text-gray-500">{agentName}</div>
                    )}
                    {error && (
                      <div className="text-xs text-red-400 mt-0.5">{error}</div>
                    )}
                    {output?.message && status === 'completed' && (
                      <div className="text-xs text-gray-400 mt-0.5 truncate max-w-md">
                        {(output.message as string).slice(0, 100)}...
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {/* View deliverable link for completed stages */}
                    {deliverableId && (
                      <Link
                        to={`/workspace?tab=deliverables&workspace=${workspaceId}`}
                        className="text-xs px-2 py-1 rounded bg-blue-900/30 text-blue-300 hover:bg-blue-900/50 transition-colors"
                      >
                        View
                      </Link>
                    )}
                    {/* Approve button for review stages */}
                    {status === 'awaiting_approval' && (
                      <button
                        onClick={() => {
                          // Mark as approved by navigating to deliverables to review
                          window.location.href = `/workspace?tab=deliverables&workspace=${workspaceId}`
                        }}
                        className="text-xs px-3 py-1 rounded bg-green-600 hover:bg-green-500 text-white transition-colors"
                      >
                        Review & Approve
                      </button>
                    )}
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      status === 'completed' ? 'bg-green-900/30 text-green-300' :
                      status === 'running' ? 'bg-blue-900/30 text-blue-300' :
                      status === 'failed' ? 'bg-red-900/30 text-red-300' :
                      status === 'awaiting_approval' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-gray-800 text-gray-500'
                    }`}>
                      {status === 'awaiting_approval' ? 'needs review' : status}
                    </span>
                  </div>
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
