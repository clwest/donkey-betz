// Session 865: ConceptForge Dossier Pipeline Tab
// Shows ConceptForge runs with 6 stage tabs: Research | Debate | Feasibility | Risk | Market | Synthesis
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Sparkles,
  RefreshCw,
  Loader2,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  ChevronRight,
  FileText,
  Users,
  Brain,
  Scale,
  TrendingUp,
  Lightbulb,
  BarChart3,
  FlaskConical,
  Eye,
  Copy,
  Download,
  X,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

// Stage configuration
const STAGES = [
  { key: 'research', name: 'Research', icon: FlaskConical, color: 'text-blue-400' },
  { key: 'debate', name: 'Debate', icon: Users, color: 'text-purple-400' },
  { key: 'feasibility', name: 'Feasibility', icon: Brain, color: 'text-cyan-400' },
  { key: 'risk', name: 'Risk', icon: Scale, color: 'text-orange-400' },
  { key: 'market', name: 'Market', icon: TrendingUp, color: 'text-green-400' },
  { key: 'synthesis', name: 'Synthesis', icon: Lightbulb, color: 'text-yellow-400' },
] as const

// Domain lab icons
const DOMAIN_ICONS: Record<string, string> = {
  legal: '⚖️',
  market: '📈',
  tech: '🔧',
  content: '📝',
  startup: '🚀',
  career: '💼',
}

interface StageData {
  id: string
  status: string
  duration_ms: number
  has_output: boolean
  agent_used: string
  advisors_used: string[]
  legendary_advisors_used: string[]
}

interface ConceptForgeRun {
  id: string
  source_type: string
  source_id: string
  source_title: string
  domain: string
  status: string
  current_stage: string
  progress_percentage: number
  quality_score: number
  triggered_by: string
  duration_ms: number
  error: string | null
  stages: Record<string, StageData>
  created_at: string
  started_at: string | null
  completed_at: string | null
}

interface RunDetailStage {
  id: string
  stage_name: string
  stage_order: number
  status: string
  agent_used: string
  advisors_used: string[]
  legendary_advisors_used: string[]
  output_text: string
  output_metadata: Record<string, unknown>
  error: string | null
  duration_ms: number
}

interface RunDetail extends Omit<ConceptForgeRun, 'stages'> {
  advisor_panel_snapshot: Record<string, unknown>
  stages: RunDetailStage[]
  artifacts: Array<{
    id: string
    name: string
    kind: string
    version: number
    is_primary: boolean
    content: string
    created_at: string
  }>
}

interface Stats {
  total_runs: number
  completed_runs: number
  failed_runs: number
  running_runs: number
  pending_runs: number
  runs_last_7_days: number
  success_rate: number
  avg_duration_ms: number
  by_domain: Array<{ domain: string; count: number }>
}

// Session 869: Artifact view modal
interface ArtifactModalProps {
  artifact: {
    id: string
    name: string
    kind: string
    version: number
    is_primary: boolean
    content: string
    created_at: string
  }
  onClose: () => void
}

function ArtifactViewModal({ artifact, onClose }: ArtifactModalProps) {
  const [copied, setCopied] = useState(false)

  // Session 870: Added error handling for clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
      alert('Failed to copy to clipboard. Please try selecting and copying manually.')
    }
  }

  const handleDownload = () => {
    const blob = new Blob([artifact.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${artifact.name.toLowerCase().replace(/\s+/g, '-')}-v${artifact.version}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <FileText size={20} className={artifact.is_primary ? 'text-yellow-400' : 'text-primary-400'} />
            <div>
              <h3 className="font-semibold text-lg">{artifact.name}</h3>
              <p className="text-xs text-gray-400">
                v{artifact.version} • {artifact.kind.toUpperCase()} • {new Date(artifact.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg bg-dark-bg hover:bg-dark-hover transition-colors"
              title="Copy to clipboard"
            >
              <Copy size={14} />
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
              title="Download as markdown"
            >
              <Download size={14} />
              Download
            </button>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-dark-hover rounded-lg transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {artifact.content ? (
            <pre className="whitespace-pre-wrap text-sm font-mono text-gray-300 leading-relaxed">
              {artifact.content}
            </pre>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText size={32} className="mx-auto mb-2 opacity-50" />
              <p>No content available</p>
            </div>
          )}
        </div>

        {/* Footer stats */}
        <div className="flex items-center justify-between p-3 border-t border-dark-border bg-dark-bg/50 text-xs text-gray-400">
          <span>{artifact.content?.length?.toLocaleString() || 0} characters</span>
          <span>{artifact.content?.split(/\s+/).filter(Boolean).length?.toLocaleString() || 0} words</span>
        </div>
      </div>
    </div>
  )
}

// Status badge component
function StatusBadge({ status }: { status: string }) {
  const config = {
    completed: { icon: CheckCircle2, class: 'bg-green-500/20 text-green-400' },
    running: { icon: Loader2, class: 'bg-blue-500/20 text-blue-400' },
    pending: { icon: Clock, class: 'bg-gray-500/20 text-gray-400' },
    failed: { icon: XCircle, class: 'bg-red-500/20 text-red-400' },
    cancelled: { icon: AlertTriangle, class: 'bg-yellow-500/20 text-yellow-400' },
  }[status] || { icon: Clock, class: 'bg-gray-500/20 text-gray-400' }

  const Icon = config.icon

  return (
    <span className={cn('px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1', config.class)}>
      <Icon size={12} className={status === 'running' ? 'animate-spin' : ''} />
      {status}
    </span>
  )
}

// Stage progress indicator
function StageProgress({ run }: { run: ConceptForgeRun }) {
  return (
    <div className="flex items-center gap-1">
      {STAGES.map((stage) => {
        const stageData = run.stages[stage.key]
        const isCompleted = stageData?.status === 'completed'
        const isRunning = stageData?.status === 'running'
        const isFailed = stageData?.status === 'failed'
        const isCurrent = run.current_stage === stage.key

        return (
          <div key={stage.key} className="group relative">
            <div
              className={cn(
                'w-6 h-6 rounded-full flex items-center justify-center transition-all',
                isCompleted && 'bg-green-500/20 text-green-400 ring-2 ring-green-500/30',
                isRunning && 'bg-blue-500/20 text-blue-400 ring-2 ring-blue-500/30 animate-pulse',
                isFailed && 'bg-red-500/20 text-red-400 ring-2 ring-red-500/30',
                !stageData && 'bg-dark-border text-gray-500',
                isCurrent && !isCompleted && !isFailed && 'ring-2 ring-primary-500/50'
              )}
            >
              {isCompleted ? (
                <CheckCircle2 size={14} />
              ) : isFailed ? (
                <XCircle size={12} />
              ) : (
                <stage.icon size={12} />
              )}
            </div>
            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-dark-card border border-dark-border rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              <div className="font-medium">{stage.name}</div>
              <div className="text-gray-400">
                {isCompleted ? 'Completed' : isRunning ? 'Running' : isFailed ? 'Failed' : 'Pending'}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Run card component
function RunCard({ run, onSelect, isSelected }: { run: ConceptForgeRun; onSelect: () => void; isSelected: boolean }) {
  const domainIcon = DOMAIN_ICONS[run.domain] || '📋'

  return (
    <div
      className={cn(
        'bg-dark-card border rounded-lg p-4 hover:border-primary-500/50 transition-colors cursor-pointer',
        isSelected ? 'border-primary-500 ring-1 ring-primary-500/30' : 'border-dark-border'
      )}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{domainIcon}</span>
            <h3 className="font-medium truncate">{run.source_title}</h3>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span className="capitalize">{run.domain}Lab</span>
            <span>•</span>
            <span>Quality: {Math.round(run.quality_score * 100)}%</span>
            <span>•</span>
            <span>{new Date(run.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <StatusBadge status={run.status} />
      </div>

      {/* Progress section */}
      <div className="flex items-center justify-between">
        <StageProgress run={run} />
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>{run.progress_percentage}%</span>
          <ChevronRight size={14} />
        </div>
      </div>
    </div>
  )
}

// Run detail view with stage tabs
// Session 870: Added error state handling
function RunDetailView({ runId }: { runId: string }) {
  const [activeStage, setActiveStage] = useState<string>('research')
  const [selectedArtifact, setSelectedArtifact] = useState<RunDetail['artifacts'][0] | null>(null)
  const [copiedArtifactId, setCopiedArtifactId] = useState<string | null>(null)

  const { data: detail, isLoading, isError, refetch } = useQuery({
    queryKey: ['conceptforge-run', runId],
    queryFn: async () => {
      const response = await api.get(`/api/conceptforge/runs/${runId}/`)
      return response.data as RunDetail
    },
    enabled: !!runId,
  })

  // Session 870: Handler for inline artifact copy with feedback
  const handleArtifactCopy = async (artifact: RunDetail['artifacts'][0]) => {
    try {
      await navigator.clipboard.writeText(artifact.content || '')
      setCopiedArtifactId(artifact.id)
      setTimeout(() => setCopiedArtifactId(null), 2000)
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
      alert('Failed to copy to clipboard')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-primary-500" size={32} />
      </div>
    )
  }

  // Session 870: Show error state instead of null
  if (isError) {
    return (
      <div className="bg-dark-card border border-red-500/30 rounded-lg p-8 text-center">
        <AlertTriangle size={32} className="mx-auto mb-3 text-red-400" />
        <p className="text-gray-400">Failed to load dossier details</p>
        <button
          onClick={() => refetch()}
          className="mt-3 px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (!detail) return null

  // Find active stage data - detail.stages is an array in the detail response
  const stageData = Array.isArray(detail.stages)
    ? detail.stages.find(s => s.stage_name === activeStage)
    : null

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl">{DOMAIN_ICONS[detail.domain] || '📋'}</span>
              <h2 className="text-lg font-semibold">{detail.source_title}</h2>
            </div>
            <p className="text-sm text-gray-400">
              {detail.domain}Lab • Triggered by {detail.triggered_by} • {new Date(detail.created_at).toLocaleString()}
            </p>
          </div>
          <StatusBadge status={detail.status} />
        </div>

        {/* Duration and progress */}
        {detail.duration_ms > 0 && (
          <div className="text-sm text-gray-400">
            Duration: {Math.round(detail.duration_ms / 1000)}s
          </div>
        )}
      </div>

      {/* Stage tabs */}
      <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
        <div className="flex border-b border-dark-border overflow-x-auto">
          {STAGES.map((stage) => {
            const data = Array.isArray(detail.stages)
              ? detail.stages.find(s => s.stage_name === stage.key)
              : null
            const isCompleted = data?.status === 'completed'
            const hasOutput = !!data?.output_text

            return (
              <button
                key={stage.key}
                onClick={() => setActiveStage(stage.key)}
                className={cn(
                  'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap',
                  activeStage === stage.key
                    ? 'bg-primary-500/10 text-primary-400 border-b-2 border-primary-500'
                    : 'text-gray-400 hover:text-white hover:bg-dark-hover'
                )}
              >
                <stage.icon size={16} className={stage.color} />
                {stage.name}
                {isCompleted && <CheckCircle2 size={12} className="text-green-400" />}
                {!hasOutput && !isCompleted && <span className="text-gray-500 text-xs">(pending)</span>}
              </button>
            )
          })}
        </div>

        {/* Stage content */}
        <div className="p-4">
          {stageData ? (
            <div className="space-y-4">
              {/* Stage metadata */}
              <div className="flex flex-wrap gap-4 text-sm">
                {stageData.agent_used && (
                  <div className="flex items-center gap-2">
                    <Brain size={14} className="text-primary-400" />
                    <span className="text-gray-400">Agent:</span>
                    <span>{stageData.agent_used}</span>
                  </div>
                )}
                {stageData.legendary_advisors_used.length > 0 && (
                  <div className="flex items-center gap-2">
                    <Users size={14} className="text-yellow-400" />
                    <span className="text-gray-400">Advisors:</span>
                    <span>{stageData.legendary_advisors_used.join(', ')}</span>
                  </div>
                )}
                {stageData.duration_ms > 0 && (
                  <div className="flex items-center gap-2">
                    <Clock size={14} className="text-gray-400" />
                    <span>{Math.round(stageData.duration_ms / 1000)}s</span>
                  </div>
                )}
              </div>

              {/* Output content */}
              {stageData.output_text ? (
                <div className="bg-dark-bg border border-dark-border rounded-lg p-4 max-h-[500px] overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm font-mono text-gray-300">
                    {stageData.output_text}
                  </pre>
                </div>
              ) : stageData.error ? (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <p className="text-red-400 text-sm">{stageData.error}</p>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Clock size={32} className="mx-auto mb-2 opacity-50" />
                  <p>Stage pending execution</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Clock size={32} className="mx-auto mb-2 opacity-50" />
              <p>No data for this stage yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Artifacts - Session 869: Added interaction buttons */}
      {detail.artifacts.length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="font-medium mb-3 flex items-center gap-2">
            <FileText size={16} className="text-primary-400" />
            Artifacts
            <span className="text-xs bg-dark-bg px-2 py-0.5 rounded text-gray-400">
              {detail.artifacts.length}
            </span>
          </h3>
          <div className="space-y-2">
            {detail.artifacts.map((artifact) => (
              <div
                key={artifact.id}
                className="flex items-center justify-between p-3 bg-dark-bg rounded-lg hover:bg-dark-hover/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <FileText size={16} className={artifact.is_primary ? 'text-yellow-400' : 'text-gray-400'} />
                  <div>
                    <p className="font-medium text-sm">{artifact.name}</p>
                    <p className="text-xs text-gray-400">
                      v{artifact.version} • {artifact.kind.toUpperCase()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {artifact.is_primary && (
                    <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded">
                      Primary
                    </span>
                  )}
                  {/* Session 869: Artifact action buttons */}
                  <button
                    onClick={() => setSelectedArtifact(artifact)}
                    className="p-1.5 hover:bg-dark-border rounded transition-colors text-gray-400 hover:text-white"
                    title="View content"
                  >
                    <Eye size={14} />
                  </button>
                  {/* Session 870: Added copy feedback */}
                  <button
                    onClick={() => handleArtifactCopy(artifact)}
                    className={cn(
                      "p-1.5 hover:bg-dark-border rounded transition-colors",
                      copiedArtifactId === artifact.id
                        ? "text-green-400"
                        : "text-gray-400 hover:text-white"
                    )}
                    title={copiedArtifactId === artifact.id ? "Copied!" : "Copy to clipboard"}
                  >
                    {copiedArtifactId === artifact.id ? (
                      <CheckCircle2 size={14} />
                    ) : (
                      <Copy size={14} />
                    )}
                  </button>
                  <button
                    onClick={() => {
                      if (!artifact.content) return
                      const blob = new Blob([artifact.content], { type: 'text/markdown' })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = `${artifact.name.toLowerCase().replace(/\s+/g, '-')}-v${artifact.version}.md`
                      document.body.appendChild(a)
                      a.click()
                      document.body.removeChild(a)
                      URL.revokeObjectURL(url)
                    }}
                    className="p-1.5 hover:bg-dark-border rounded transition-colors text-gray-400 hover:text-primary-400"
                    title="Download as markdown"
                  >
                    <Download size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Session 869: Artifact view modal */}
      {selectedArtifact && (
        <ArtifactViewModal
          artifact={selectedArtifact}
          onClose={() => setSelectedArtifact(null)}
        />
      )}
    </div>
  )
}

// Stats panel
function StatsPanel({ stats }: { stats: Stats }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div className="bg-dark-card border border-dark-border rounded-lg p-3">
        <div className="text-2xl font-bold text-primary-400">{stats.total_runs}</div>
        <div className="text-xs text-gray-400">Total Runs</div>
      </div>
      <div className="bg-dark-card border border-dark-border rounded-lg p-3">
        <div className="text-2xl font-bold text-green-400">{stats.success_rate}%</div>
        <div className="text-xs text-gray-400">Success Rate</div>
      </div>
      <div className="bg-dark-card border border-dark-border rounded-lg p-3">
        <div className="text-2xl font-bold text-blue-400">{stats.runs_last_7_days}</div>
        <div className="text-xs text-gray-400">Last 7 Days</div>
      </div>
      <div className="bg-dark-card border border-dark-border rounded-lg p-3">
        <div className="text-2xl font-bold text-yellow-400">
          {stats.running_runs + stats.pending_runs}
        </div>
        <div className="text-xs text-gray-400">In Progress</div>
      </div>
    </div>
  )
}

// Main ConceptForge Tab
export function ConceptForgeTab() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')

  // Fetch runs
  // Session 870: Added error state handling
  const { data: runsData, isLoading: runsLoading, isError: runsError, refetch } = useQuery({
    queryKey: ['conceptforge-runs', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter) params.append('status', statusFilter)
      params.append('limit', '50')
      const response = await api.get(`/api/conceptforge/runs/?${params}`)
      return response.data as { runs: ConceptForgeRun[]; total: number }
    },
  })

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['conceptforge-stats'],
    queryFn: async () => {
      const response = await api.get('/api/conceptforge/stats/')
      return response.data as Stats
    },
  })

  const runs = runsData?.runs || []

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-500/20 rounded-lg">
            <Sparkles className="text-primary-400" size={24} />
          </div>
          <div>
            <h2 className="text-lg font-semibold">ConceptForge Dossiers</h2>
            <p className="text-sm text-gray-400">
              Autonomous think tank pipeline: Content → Intelligence → Strategy → Product
            </p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
          title="Refresh"
        >
          <RefreshCw size={18} className={runsLoading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Stats */}
      {stats && <StatsPanel stats={stats} />}

      {/* Filters */}
      <div className="flex items-center gap-2">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-dark-card border border-dark-border rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="">All Status</option>
          <option value="completed">Completed</option>
          <option value="running">Running</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
        <span className="text-sm text-gray-400">
          {runsData?.total || 0} dossiers
        </span>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Runs list */}
        {/* Session 870: Added error state */}
        <div className="space-y-3">
          {runsLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="animate-spin text-primary-500" size={24} />
            </div>
          ) : runsError ? (
            <div className="bg-dark-card border border-red-500/30 rounded-lg p-8 text-center">
              <AlertTriangle size={32} className="mx-auto mb-3 text-red-400" />
              <p className="text-gray-400">Failed to load dossiers</p>
              <button
                onClick={() => refetch()}
                className="mt-3 px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : runs.length === 0 ? (
            <div className="bg-dark-card border border-dark-border rounded-lg p-10 text-center max-w-lg mx-auto">
              <Sparkles size={40} className="mx-auto mb-4 text-amber-400" />
              <h3 className="text-lg font-semibold text-gray-200 mb-2">Automated creative pipelines</h3>
              <p className="text-gray-400 text-sm mb-6">
                ConceptForge runs a 6-stage analysis pipeline on published content — research, debate, feasibility, risk, market analysis, and synthesis — producing comprehensive dossiers.
              </p>
              <div className="text-left space-y-2 mb-4">
                <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">How it works</p>
                <p className="text-sm text-gray-400 flex items-start gap-2"><span className="text-amber-400/80 shrink-0">1.</span> Publish a blog with quality score above 80%</p>
                <p className="text-sm text-gray-400 flex items-start gap-2"><span className="text-amber-400/80 shrink-0">2.</span> The pipeline auto-triggers and runs 6 analysis stages</p>
                <p className="text-sm text-gray-400 flex items-start gap-2"><span className="text-amber-400/80 shrink-0">3.</span> Review the dossier with insights, risks, and market analysis</p>
              </div>
              <p className="text-xs text-gray-500 mt-4">Dossiers will appear here once the pipeline runs on your published content.</p>
            </div>
          ) : (
            runs.map((run) => (
              <RunCard
                key={run.id}
                run={run}
                onSelect={() => setSelectedRunId(run.id)}
                isSelected={selectedRunId === run.id}
              />
            ))
          )}
        </div>

        {/* Detail view */}
        <div>
          {selectedRunId ? (
            <RunDetailView runId={selectedRunId} />
          ) : (
            <div className="bg-dark-card border border-dark-border rounded-lg p-8 text-center h-full flex flex-col items-center justify-center">
              <BarChart3 size={48} className="text-gray-600 mb-3" />
              <p className="text-gray-400">Select a dossier to view details</p>
              <p className="text-sm text-gray-500 mt-1">
                See stage outputs, advisor inputs, and artifacts
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
