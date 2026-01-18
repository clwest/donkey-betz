/**
 * OrchestrationPage - Multi-Agent Workflow Management
 * ====================================================
 *
 * Session 768: Comprehensive UI for orchestration layer management.
 *
 * Features:
 * - Workflow library with templates
 * - Execution history with filtering
 * - Real-time execution monitoring
 * - Step-by-step intelligence drilldown
 * - Visual workflow status
 * - Analytics dashboard
 */

import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  orchestrationApi,
  OrchestrationWorkflow,
  OrchestrationWorkflowStep,
  OrchestrationWorkflowDetail,
  OrchestrationAgent,
  OrchestrationExecution,
  OrchestrationExecutionDetail,
  StepIntelligenceData,
  CreateWorkflowRequest
} from '@/lib/api'
import {
  GitBranch, Play, Pause, Square, RefreshCw, ChevronRight, Loader2,
  Clock, DollarSign, Zap, CheckCircle, XCircle,
  Eye, Layers, Brain, Terminal, FileText, ChevronDown, ChevronUp,
  Workflow, Timer, Users, BarChart3, Activity,
  ArrowRight, RotateCcw, Ban, Plus, Sparkles, History, X,
  Bot, Trash2, Save, Shield, Shuffle
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'workflows' | 'executions' | 'analytics' | 'builder'

// Status colors and icons
const statusConfig: Record<string, { color: string; bgColor: string; icon: typeof CheckCircle }> = {
  pending: { color: 'text-gray-400', bgColor: 'bg-gray-500/20', icon: Clock },
  running: { color: 'text-blue-400', bgColor: 'bg-blue-500/20', icon: Activity },
  paused: { color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', icon: Pause },
  waiting_approval: { color: 'text-amber-400', bgColor: 'bg-amber-500/20', icon: Users },
  completed: { color: 'text-green-400', bgColor: 'bg-green-500/20', icon: CheckCircle },
  failed: { color: 'text-red-400', bgColor: 'bg-red-500/20', icon: XCircle },
  cancelled: { color: 'text-gray-400', bgColor: 'bg-gray-500/20', icon: Ban },
  timed_out: { color: 'text-orange-400', bgColor: 'bg-orange-500/20', icon: Timer },
}

// Execution mode descriptions
const executionModeInfo = {
  sequential: { label: 'Sequential', desc: 'Steps run one after another', icon: ArrowRight },
  parallel: { label: 'Parallel', desc: 'Independent steps run simultaneously', icon: Layers },
  dependency: { label: 'Dependency', desc: 'Steps run based on dependencies', icon: GitBranch },
}

/**
 * Session 770: Smart tool result renderer
 * Formats tool results in a human-readable way instead of raw JSON
 */
function renderToolResult(data: unknown, depth = 0): React.ReactNode {
  if (data === null || data === undefined) {
    return <span className="text-gray-500 italic">No result</span>
  }

  // Handle simple primitives
  if (typeof data === 'string') {
    // Check if it's a long string or multi-line
    if (data.length > 100 || data.includes('\n')) {
      return <p className="text-xs text-gray-300 whitespace-pre-wrap">{data.slice(0, 500)}{data.length > 500 ? '...' : ''}</p>
    }
    return <span className="text-sm text-gray-300">{data}</span>
  }
  if (typeof data === 'number' || typeof data === 'boolean') {
    return <span className="text-sm text-blue-300">{String(data)}</span>
  }

  // Handle arrays
  if (Array.isArray(data)) {
    if (data.length === 0) {
      return <span className="text-xs text-gray-500 italic">Empty</span>
    }

    // Check if it's a topics/counts array (common pattern)
    if (data.length > 0 && typeof data[0] === 'object' && data[0] !== null) {
      const firstItem = data[0] as Record<string, unknown>

      // Topics with counts pattern: [{topic: "ai", count: 150}, ...]
      if ('topic' in firstItem && 'count' in firstItem) {
        return (
          <div className="flex flex-wrap gap-1.5">
            {data.slice(0, 15).map((item, idx) => {
              const t = item as { topic: string; count: number }
              return (
                <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-xs">
                  <span className="font-medium">{t.topic}</span>
                  <span className="text-purple-400/60">({t.count})</span>
                </span>
              )
            })}
            {data.length > 15 && (
              <span className="text-xs text-gray-500">+{data.length - 15} more</span>
            )}
          </div>
        )
      }

      // Items with title/name pattern: [{title: "...", ...}, ...]
      if ('title' in firstItem || 'name' in firstItem || 'headline' in firstItem) {
        return (
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {data.slice(0, 8).map((item, idx) => {
              const i = item as Record<string, unknown>
              const label = (i.title || i.name || i.headline || 'Item') as string
              const subtitle = (i.source || i.author || i.type || i.category || '') as string
              const score = i.score || i.points || i.count
              return (
                <div key={idx} className="flex items-start gap-2 text-xs bg-black/20 rounded px-2 py-1">
                  <span className="text-gray-500 shrink-0">{idx + 1}.</span>
                  <span className="text-gray-300 flex-1 line-clamp-2">{String(label)}</span>
                  {subtitle && <span className="text-gray-500 shrink-0">{String(subtitle)}</span>}
                  {score !== undefined && <span className="text-blue-400 shrink-0">{String(score)}</span>}
                </div>
              )
            })}
            {data.length > 8 && (
              <p className="text-xs text-gray-500">+{data.length - 8} more items</p>
            )}
          </div>
        )
      }

      // URLs or links pattern
      if ('url' in firstItem || 'link' in firstItem) {
        return (
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {data.slice(0, 6).map((item, idx) => {
              const i = item as Record<string, unknown>
              const title = (i.title || i.name || 'Link') as string
              return (
                <div key={idx} className="text-xs text-blue-400 truncate">
                  • {String(title).slice(0, 80)}
                </div>
              )
            })}
            {data.length > 6 && (
              <p className="text-xs text-gray-500">+{data.length - 6} more links</p>
            )}
          </div>
        )
      }
    }

    // Simple array of strings/numbers
    if (data.length > 0 && (typeof data[0] === 'string' || typeof data[0] === 'number')) {
      return (
        <div className="flex flex-wrap gap-1">
          {data.slice(0, 12).map((item, idx) => (
            <span key={idx} className="px-1.5 py-0.5 rounded bg-gray-700/50 text-gray-300 text-xs">
              {String(item).slice(0, 30)}
            </span>
          ))}
          {data.length > 12 && (
            <span className="text-xs text-gray-500">+{data.length - 12} more</span>
          )}
        </div>
      )
    }

    // Fallback: show first few items as mini cards
    return (
      <div className="space-y-1 max-h-32 overflow-y-auto">
        {data.slice(0, 5).map((item, idx) => (
          <div key={idx} className="text-xs bg-black/20 rounded px-2 py-1">
            {typeof item === 'object' ? JSON.stringify(item).slice(0, 100) : String(item)}
          </div>
        ))}
        {data.length > 5 && <p className="text-xs text-gray-500">+{data.length - 5} more</p>}
      </div>
    )
  }

  // Handle objects - drill into nested structures
  if (typeof data === 'object') {
    const obj = data as Record<string, unknown>
    const entries = Object.entries(obj)

    // Filter out empty arrays and nulls for cleaner display
    const meaningfulEntries = entries.filter(([, v]) => {
      if (v === null || v === undefined) return false
      if (Array.isArray(v) && v.length === 0) return false
      return true
    })

    if (meaningfulEntries.length === 0) {
      return <span className="text-xs text-gray-500 italic">No data</span>
    }

    // Render each field with proper formatting
    return (
      <div className="space-y-2">
        {meaningfulEntries.slice(0, 8).map(([key, value]) => (
          <div key={key} className="border-l-2 border-gray-700 pl-2">
            <div className="text-xs text-gray-500 font-medium mb-0.5">
              {key.replace(/_/g, ' ')}
              {Array.isArray(value) && <span className="text-gray-600 ml-1">({value.length})</span>}
            </div>
            <div className="pl-1">
              {depth < 2 ? renderToolResult(value, depth + 1) : (
                <span className="text-xs text-gray-400">
                  {Array.isArray(value) ? `[${value.length} items]` : typeof value === 'object' ? '{...}' : String(value).slice(0, 50)}
                </span>
              )}
            </div>
          </div>
        ))}
        {meaningfulEntries.length > 8 && (
          <p className="text-xs text-gray-500">+{meaningfulEntries.length - 8} more fields</p>
        )}
      </div>
    )
  }

  return <span className="text-gray-500">Unknown data type</span>
}

export default function OrchestrationPage() {
  const [activeTab, setActiveTab] = useState<TabType>('workflows')
  const [selectedExecution, setSelectedExecution] = useState<string | null>(null)
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [selectedStep, setSelectedStep] = useState<number | null>(null)
  const [executionFilter, setExecutionFilter] = useState<string>('')
  const [showExecuteModal, setShowExecuteModal] = useState<string | null>(null)
  const [showBuilder, setShowBuilder] = useState(false)
  const queryClient = useQueryClient()

  // Fetch workflows
  const { data: workflowsData, isLoading: workflowsLoading, refetch: refetchWorkflows } = useQuery({
    queryKey: ['orchestration-workflows'],
    queryFn: () => orchestrationApi.listWorkflows(),
  })

  // Session 768: Fetch workflow detail when selected
  const { data: workflowDetailData, isLoading: workflowDetailLoading } = useQuery({
    queryKey: ['orchestration-workflow-detail', selectedWorkflow],
    queryFn: () => selectedWorkflow ? orchestrationApi.getWorkflowDetail(selectedWorkflow) : null,
    enabled: !!selectedWorkflow,
  })

  // Session 768: Fetch available agents for builder
  const { data: agentsData } = useQuery({
    queryKey: ['orchestration-agents'],
    queryFn: () => orchestrationApi.getAgents(),
    enabled: activeTab === 'builder' || showBuilder,
  })

  // Fetch executions
  const { data: executionsData, isLoading: executionsLoading, refetch: refetchExecutions } = useQuery({
    queryKey: ['orchestration-executions', executionFilter],
    queryFn: () => orchestrationApi.listExecutions({
      status: executionFilter || undefined,
      limit: 50,
      all: true,
    }),
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  // Fetch execution detail when selected
  const { data: executionDetail, isLoading: detailLoading } = useQuery({
    queryKey: ['orchestration-execution-detail', selectedExecution],
    queryFn: () => selectedExecution ? orchestrationApi.getExecution(selectedExecution) : null,
    enabled: !!selectedExecution,
    refetchInterval: selectedExecution ? 5000 : false, // Refresh every 5s when viewing
  })

  // Fetch step intelligence when step selected
  const { data: stepIntelligence, isLoading: intelligenceLoading } = useQuery({
    queryKey: ['orchestration-step-intelligence', selectedExecution, selectedStep],
    queryFn: () => selectedExecution && selectedStep !== null
      ? orchestrationApi.getStepIntelligence(selectedExecution, selectedStep)
      : null,
    enabled: !!selectedExecution && selectedStep !== null,
  })

  // Execute workflow mutation
  const executeMutation = useMutation({
    mutationFn: ({ workflowId, input }: { workflowId: string; input?: Record<string, unknown> }) =>
      orchestrationApi.execute(workflowId, input, true),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['orchestration-executions'] })
      setShowExecuteModal(null)
      // Auto-select the new execution
      if (data.data?.execution_id) {
        setSelectedExecution(data.data.execution_id)
        setActiveTab('executions')
      }
    },
  })

  // Resume execution mutation
  const resumeMutation = useMutation({
    mutationFn: (executionId: string) => orchestrationApi.resume(executionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orchestration-executions'] })
      queryClient.invalidateQueries({ queryKey: ['orchestration-execution-detail'] })
    },
  })

  // Cancel execution mutation
  const cancelMutation = useMutation({
    mutationFn: (executionId: string) => orchestrationApi.cancel(executionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orchestration-executions'] })
      queryClient.invalidateQueries({ queryKey: ['orchestration-execution-detail'] })
    },
  })

  // Session 768: Create workflow mutation
  const createWorkflowMutation = useMutation({
    mutationFn: (data: CreateWorkflowRequest) => orchestrationApi.createWorkflow(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orchestration-workflows'] })
      setShowBuilder(false)
      setActiveTab('workflows')
    },
  })

  const workflows = workflowsData?.data?.workflows || []
  const executions = executionsData?.data?.executions || []
  const availableAgents = agentsData?.data?.agents || []
  const workflowDetail = workflowDetailData?.data
  const workflowSteps = workflowDetailData?.data?.steps || []
  const inputParameters = workflowDetailData?.data?.input_parameters || []

  // Calculate analytics
  const analytics = {
    totalWorkflows: workflows.length,
    totalExecutions: executions.length,
    runningCount: executions.filter(e => e.status === 'running').length,
    completedCount: executions.filter(e => e.status === 'completed').length,
    failedCount: executions.filter(e => e.status === 'failed').length,
    totalCost: executions.reduce((sum, e) => sum + parseFloat(e.total_cost || '0'), 0),
    totalTokens: executions.reduce((sum, e) => sum + (e.total_tokens || 0), 0),
    successRate: executions.length > 0
      ? Math.round((executions.filter(e => e.status === 'completed').length / executions.length) * 100)
      : 0,
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-purple-400">
            <GitBranch className="w-6 h-6" />
            <h1 className="text-2xl font-bold text-white">Orchestration Layer</h1>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => { refetchWorkflows(); refetchExecutions() }}
            className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          icon={Workflow}
          label="Workflows"
          value={analytics.totalWorkflows}
          color="text-purple-400"
        />
        <StatCard
          icon={Activity}
          label="Running"
          value={analytics.runningCount}
          color="text-blue-400"
          pulse={analytics.runningCount > 0}
        />
        <StatCard
          icon={CheckCircle}
          label="Success Rate"
          value={`${analytics.successRate}%`}
          color="text-green-400"
        />
        <StatCard
          icon={DollarSign}
          label="Total Cost"
          value={`$${analytics.totalCost.toFixed(4)}`}
          color="text-yellow-400"
        />
      </div>

      {/* Tabs */}
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <div className="flex gap-2">
          {[
            { id: 'workflows', label: 'Workflows', icon: Workflow },
            { id: 'executions', label: 'Executions', icon: History },
            { id: 'analytics', label: 'Analytics', icon: BarChart3 },
            { id: 'builder', label: 'Builder', icon: Plus },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as TabType)
                if (tab.id !== 'workflows') setSelectedWorkflow(null)
                if (tab.id !== 'executions') setSelectedExecution(null)
              }}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
                activeTab === tab.id
                  ? 'bg-purple-500/20 text-purple-400'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              )}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
        {activeTab === 'workflows' && (
          <button
            onClick={() => setActiveTab('builder')}
            className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg text-white text-sm transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Workflow
          </button>
        )}
      </div>

      {/* Main Content */}
      {activeTab === 'builder' ? (
        <WorkflowBuilder
          agents={availableAgents}
          onSave={(data) => createWorkflowMutation.mutate(data)}
          onCancel={() => setActiveTab('workflows')}
          isSaving={createWorkflowMutation.isPending}
        />
      ) : (
        <div className="grid grid-cols-3 gap-6">
          {/* Left Panel - List */}
          <div className="col-span-1 space-y-4">
            {activeTab === 'workflows' && (
              <WorkflowList
                workflows={workflows}
                loading={workflowsLoading}
                selectedId={selectedWorkflow}
                onSelect={setSelectedWorkflow}
                onExecute={(id) => setShowExecuteModal(id)}
              />
            )}

            {activeTab === 'executions' && (
              <ExecutionList
                executions={executions}
                loading={executionsLoading}
                selectedId={selectedExecution}
                filter={executionFilter}
                onFilterChange={setExecutionFilter}
                onSelect={setSelectedExecution}
              />
            )}

            {activeTab === 'analytics' && (
              <AnalyticsSidebar analytics={analytics} executions={executions} />
            )}
          </div>

          {/* Right Panel - Detail */}
          <div className="col-span-2">
            {activeTab === 'workflows' && selectedWorkflow && workflowDetail ? (
              <WorkflowDetailView
                workflow={workflowDetail.workflow}
                steps={workflowSteps}
                inputParameters={inputParameters}
                loading={workflowDetailLoading}
                isExecuting={executeMutation.isPending}
                onExecute={() => setShowExecuteModal(selectedWorkflow)}
                onClose={() => setSelectedWorkflow(null)}
                onExecuteWithInput={(input) => {
                  if (selectedWorkflow) {
                    executeMutation.mutate({ workflowId: selectedWorkflow, input })
                  }
                }}
              />
            ) : selectedExecution && executionDetail?.data?.execution ? (
              <ExecutionDetail
                detail={executionDetail.data}
                loading={detailLoading}
                selectedStep={selectedStep}
                onSelectStep={setSelectedStep}
                stepIntelligence={stepIntelligence?.data?.intelligence}
                intelligenceLoading={intelligenceLoading}
                onResume={() => resumeMutation.mutate(selectedExecution)}
                onCancel={() => cancelMutation.mutate(selectedExecution)}
                isResuming={resumeMutation.isPending}
                isCancelling={cancelMutation.isPending}
              />
            ) : activeTab === 'analytics' ? (
              <AnalyticsDashboard analytics={analytics} executions={executions} />
            ) : (
              <EmptyDetailPanel />
            )}
          </div>
        </div>
      )}

      {/* Execute Modal */}
      {showExecuteModal && (
        <ExecuteWorkflowModal
          workflowId={showExecuteModal}
          workflow={workflows.find(w => w.id === showExecuteModal)}
          onClose={() => setShowExecuteModal(null)}
          onExecute={(input) => executeMutation.mutate({ workflowId: showExecuteModal, input })}
          isExecuting={executeMutation.isPending}
        />
      )}
    </div>
  )
}

// ============================================================================
// Sub-Components
// ============================================================================

function StatCard({
  icon: Icon,
  label,
  value,
  color,
  pulse = false,
}: {
  icon: typeof CheckCircle
  label: string
  value: string | number
  color: string
  pulse?: boolean
}) {
  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
      <div className="flex items-center justify-between">
        <div className={cn('p-2 rounded-lg bg-white/5', color)}>
          <Icon className={cn('w-5 h-5', pulse && 'animate-pulse')} />
        </div>
        <span className="text-2xl font-bold text-white">{value}</span>
      </div>
      <p className="text-sm text-gray-400 mt-2">{label}</p>
    </div>
  )
}

function WorkflowList({
  workflows,
  loading,
  selectedId,
  onSelect,
  onExecute,
}: {
  workflows: OrchestrationWorkflow[]
  loading: boolean
  selectedId: string | null
  onSelect: (id: string) => void
  onExecute: (id: string) => void
}) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
      </div>
    )
  }

  if (workflows.length === 0) {
    return (
      <div className="bg-white/5 rounded-xl p-6 text-center border border-white/10">
        <Workflow className="w-12 h-12 text-gray-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">No Workflows</h3>
        <p className="text-gray-400 text-sm">
          Create a workflow using the Builder tab to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">
        Available Workflows ({workflows.length})
      </h3>
      {workflows.map(workflow => {
        const modeInfo = executionModeInfo[workflow.execution_mode as keyof typeof executionModeInfo] || executionModeInfo.sequential
        const ModeIcon = modeInfo.icon
        const isSelected = selectedId === workflow.id

        return (
          <div
            key={workflow.id}
            onClick={() => onSelect(workflow.id)}
            className={cn(
              "bg-white/5 rounded-xl p-4 border cursor-pointer transition-colors",
              isSelected
                ? "border-purple-500/50 bg-purple-500/10"
                : "border-white/10 hover:border-purple-500/30"
            )}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-white truncate">{workflow.name}</h4>
                {workflow.description && (
                  <p className="text-sm text-gray-400 mt-1 line-clamp-2">{workflow.description}</p>
                )}
                <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5" />
                    {workflow.step_count} steps
                  </span>
                  <span className="flex items-center gap-1" title={modeInfo.desc}>
                    <ModeIcon className="w-3.5 h-3.5" />
                    {modeInfo.label}
                  </span>
                  {workflow.cost_budget && (
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-3.5 h-3.5" />
                      ${workflow.cost_budget}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); onExecute(workflow.id) }}
                className="p-2 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg text-purple-400 transition-colors"
                title="Execute workflow"
              >
                <Play className="w-4 h-4" />
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ExecutionList({
  executions,
  loading,
  selectedId,
  filter,
  onFilterChange,
  onSelect,
}: {
  executions: OrchestrationExecution[]
  loading: boolean
  selectedId: string | null
  filter: string
  onFilterChange: (filter: string) => void
  onSelect: (id: string) => void
}) {
  const filters = [
    { value: '', label: 'All' },
    { value: 'running', label: 'Running' },
    { value: 'paused', label: 'Paused' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
  ]

  return (
    <div className="space-y-3">
      {/* Filter buttons */}
      <div className="flex flex-wrap gap-2">
        {filters.map(f => (
          <button
            key={f.value}
            onClick={() => onFilterChange(f.value)}
            className={cn(
              'px-3 py-1 text-xs rounded-full transition-colors',
              filter === f.value
                ? 'bg-purple-500/30 text-purple-300'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
        </div>
      ) : executions.length === 0 ? (
        <div className="bg-white/5 rounded-xl p-6 text-center border border-white/10">
          <History className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No Executions</h3>
          <p className="text-gray-400 text-sm">
            Execute a workflow to see history here.
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {executions.map(execution => {
            const config = statusConfig[execution.status] || statusConfig.pending
            const StatusIcon = config.icon

            return (
              <button
                key={execution.id}
                onClick={() => onSelect(execution.id)}
                className={cn(
                  'w-full text-left bg-white/5 rounded-lg p-3 border transition-colors',
                  selectedId === execution.id
                    ? 'border-purple-500/50 bg-purple-500/10'
                    : 'border-white/10 hover:border-white/20'
                )}
              >
                <div className="flex items-center gap-3">
                  <div className={cn('p-1.5 rounded-lg', config.bgColor)}>
                    <StatusIcon className={cn('w-4 h-4', config.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-white truncate">
                      {execution.workflow_name}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-gray-500 mt-0.5">
                      <span>Step {execution.current_step}/{execution.total_steps}</span>
                      <span>•</span>
                      <span>${parseFloat(execution.total_cost).toFixed(4)}</span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

function ExecutionDetail({
  detail,
  loading: _loading,
  selectedStep,
  onSelectStep,
  stepIntelligence,
  intelligenceLoading,
  onResume,
  onCancel,
  isResuming,
  isCancelling,
}: {
  detail: OrchestrationExecutionDetail
  loading: boolean
  selectedStep: number | null
  onSelectStep: (step: number | null) => void
  stepIntelligence?: StepIntelligenceData
  intelligenceLoading: boolean
  onResume: () => void
  onCancel: () => void
  isResuming: boolean
  isCancelling: boolean
}) {
  const { execution, steps, approval_gates } = detail
  const config = statusConfig[execution.status] || statusConfig.pending
  const StatusIcon = config.icon

  const progress = execution.total_steps > 0
    ? Math.round((execution.current_step / execution.total_steps) * 100)
    : 0

  const canResume = ['paused', 'waiting_approval', 'failed'].includes(execution.status)
  const canCancel = ['running', 'paused', 'waiting_approval', 'pending'].includes(execution.status)

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-lg', config.bgColor)}>
              <StatusIcon className={cn('w-5 h-5', config.color)} />
            </div>
            <div>
              <h3 className="font-semibold text-white">{execution.workflow_name}</h3>
              <p className="text-sm text-gray-400">
                {execution.status.replace('_', ' ').toUpperCase()}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {canResume && (
              <button
                onClick={onResume}
                disabled={isResuming}
                className="flex items-center gap-2 px-3 py-1.5 bg-green-500/20 hover:bg-green-500/30 rounded-lg text-green-400 text-sm transition-colors disabled:opacity-50"
              >
                {isResuming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                Resume
              </button>
            )}
            {canCancel && (
              <button
                onClick={onCancel}
                disabled={isCancelling}
                className="flex items-center gap-2 px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-red-400 text-sm transition-colors disabled:opacity-50"
              >
                {isCancelling ? <Loader2 className="w-4 h-4 animate-spin" /> : <Square className="w-4 h-4" />}
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Progress</span>
            <span>{progress}% ({execution.current_step}/{execution.total_steps} steps)</span>
          </div>
          <div className="h-2 bg-white/5 rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all duration-500',
                execution.status === 'completed' ? 'bg-green-500' :
                execution.status === 'failed' ? 'bg-red-500' :
                execution.status === 'running' ? 'bg-blue-500' :
                'bg-yellow-500'
              )}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Quick stats - Session 769: Show external costs */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-4">
          <div className="text-center bg-black/20 rounded-lg p-2">
            <p className="text-lg font-semibold text-green-400">${parseFloat(execution.total_combined_cost || execution.total_cost).toFixed(4)}</p>
            <p className="text-xs text-gray-500">Total Cost</p>
          </div>
          <div className="text-center bg-black/20 rounded-lg p-2">
            <p className="text-sm font-medium text-gray-300">${parseFloat(execution.total_cost).toFixed(4)}</p>
            <p className="text-xs text-gray-500">LLM Cost</p>
          </div>
          <div className="text-center bg-black/20 rounded-lg p-2">
            <p className="text-sm font-medium text-purple-400">${parseFloat(execution.total_external_cost || '0').toFixed(4)}</p>
            <p className="text-xs text-gray-500">External APIs</p>
          </div>
          <div className="text-center bg-black/20 rounded-lg p-2">
            <p className="text-lg font-semibold text-blue-400">{execution.total_tokens.toLocaleString()}</p>
            <p className="text-xs text-gray-500">Tokens</p>
          </div>
          <div className="text-center bg-black/20 rounded-lg p-2">
            <p className="text-lg font-semibold text-white">{steps.length}</p>
            <p className="text-xs text-gray-500">Steps</p>
          </div>
          <div className="text-center bg-black/20 rounded-lg p-2">
            <p className="text-lg font-semibold text-white">{approval_gates.length}</p>
            <p className="text-xs text-gray-500">Approvals</p>
          </div>
        </div>

        {/* External cost breakdown - Session 769 */}
        {execution.external_cost_breakdown && Object.keys(execution.external_cost_breakdown).length > 0 && (
          <div className="mt-3 p-2 bg-purple-500/5 border border-purple-500/20 rounded-lg">
            <p className="text-xs text-purple-400 mb-1">External API Breakdown:</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(execution.external_cost_breakdown).map(([api, cost]) => (
                <span key={api} className="text-xs bg-purple-500/10 px-2 py-0.5 rounded text-purple-300">
                  {api.replace('_', ' ')}: ${cost.toFixed(4)}
                </span>
              ))}
            </div>
          </div>
        )}

        {execution.error_message && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-sm text-red-400">{execution.error_message}</p>
          </div>
        )}
      </div>

      {/* Steps Timeline */}
      <div className="p-4">
        <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-3">
          Execution Steps
        </h4>
        <div className="space-y-2">
          {steps.map((step) => {
            const stepConfig = statusConfig[step.status] || statusConfig.pending
            const StepIcon = stepConfig.icon
            const isSelected = selectedStep === step.step_number

            return (
              <div
                key={step.step_number}
                className={cn(
                  'w-full text-left p-3 rounded-lg border transition-colors',
                  isSelected
                    ? 'bg-purple-500/10 border-purple-500/50'
                    : 'bg-white/5 border-white/10 hover:border-white/20'
                )}
              >
                {/* Clickable header */}
                <button
                  onClick={() => onSelectStep(isSelected ? null : step.step_number)}
                  className="w-full text-left cursor-pointer hover:opacity-80 transition-opacity"
                >
                  <div className="flex items-center gap-3">
                    <div className={cn('p-1.5 rounded-lg', stepConfig.bgColor)}>
                      <StepIcon className={cn('w-4 h-4', stepConfig.color)} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">Step {step.step_number}</span>
                        <span className="font-medium text-white">{step.agent_name}</span>
                      </div>
                      {step.output_preview && (
                        <p className="text-xs text-gray-400 mt-0.5 truncate">
                          {step.output_preview}
                        </p>
                      )}
                      <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
                        <span>${parseFloat(step.cost).toFixed(4)}</span>
                        <span>{step.tokens.toLocaleString()} tokens</span>
                        {step.retry_count > 0 && (
                          <span className="text-yellow-500">{step.retry_count} retries</span>
                        )}
                      </div>
                    </div>
                    {isSelected ? (
                      <ChevronUp className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </button>

                {/* Expanded intelligence view */}
                {isSelected && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    {intelligenceLoading ? (
                      <div className="flex items-center justify-center py-4">
                        <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                      </div>
                    ) : stepIntelligence ? (
                      <StepIntelligencePanel intelligence={stepIntelligence} />
                    ) : (
                      <p className="text-sm text-gray-500 text-center py-4">
                        No intelligence data available
                      </p>
                    )}
                  </div>
                )}
              </div>
            )
          })}

          {steps.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-4">
              No steps executed yet
            </p>
          )}
        </div>
      </div>

      {/* Final Output */}
      {execution.final_output && Object.keys(execution.final_output).length > 0 && (
        <FormattedFinalOutput
          output={execution.final_output}
          executionTotalTokens={execution.total_tokens}
          podcastInfo={detail.podcast_info}
        />
      )}
    </div>
  )
}

/**
 * PodcastAudioPlayer - Audio player with demo/preview functionality
 * Session 770: Enables playing random clips from podcasts
 */
function PodcastAudioPlayer({
  audioUrl,
  durationSeconds,
}: {
  audioUrl: string
  durationSeconds: number | null
}) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [previewMode, setPreviewMode] = useState(false)

  const duration = durationSeconds || 0

  const handlePlayPause = () => {
    if (!audioRef.current) return

    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handlePlayDemo = () => {
    if (!audioRef.current || duration < 30) return

    // Pick a random start position (avoiding last 30 seconds)
    const maxStart = Math.max(0, duration - 30)
    const randomStart = Math.floor(Math.random() * maxStart)

    audioRef.current.currentTime = randomStart
    setCurrentTime(randomStart)
    setPreviewMode(true)
    audioRef.current.play()
    setIsPlaying(true)

    // Stop after 15 seconds
    setTimeout(() => {
      if (audioRef.current && previewMode) {
        audioRef.current.pause()
        setIsPlaying(false)
        setPreviewMode(false)
      }
    }, 15000)
  }

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value)
    if (audioRef.current) {
      audioRef.current.currentTime = newTime
      setCurrentTime(newTime)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="mt-3 bg-black/30 rounded-lg p-3 border border-yellow-500/10">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => {
          setIsPlaying(false)
          setPreviewMode(false)
        }}
        onPause={() => setIsPlaying(false)}
        onPlay={() => setIsPlaying(true)}
      />

      {/* Controls */}
      <div className="flex items-center gap-3 mb-2">
        <button
          onClick={handlePlayPause}
          className="p-2 rounded-full bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 transition-colors"
        >
          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>

        {duration > 30 && (
          <button
            onClick={handlePlayDemo}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 text-xs transition-colors"
            title="Play a random 15-second clip"
          >
            <Shuffle className="w-3 h-3" />
            Demo
          </button>
        )}

        <span className="text-xs text-gray-400 ml-auto">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>

      {/* Progress bar */}
      <input
        type="range"
        min={0}
        max={duration}
        value={currentTime}
        onChange={handleSeek}
        className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-yellow-400"
      />

      {previewMode && (
        <p className="text-xs text-purple-400 mt-1 flex items-center gap-1">
          <Shuffle className="w-3 h-3" />
          Playing random preview...
        </p>
      )}
    </div>
  )
}

/**
 * FormattedFinalOutput - Displays workflow final output in a human-friendly format
 * Session 769: Shows summary stats and step outputs
 * Session 770: Added podcast TTS cost display
 */
function FormattedFinalOutput({
  output,
  executionTotalTokens,
  podcastInfo,
}: {
  output: Record<string, unknown>
  executionTotalTokens?: number
  podcastInfo?: {
    episode_id: string
    title: string
    topic: string
    status: string
    tts_cost: string
    tts_cost_breakdown: Record<string, number>
    audio_url: string
    audio_duration_seconds: number | null
  }
}) {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null)

  const totalCost = output.total_cost as number | undefined
  // Session 769: Extract external costs from final output
  const totalExternalCost = output.total_external_cost as number | undefined
  const totalCombinedCost = output.total_combined_cost as number | undefined
  const externalBreakdown = output.external_cost_breakdown as Record<string, number> | undefined
  // Session 769: Use execution.total_tokens as fallback (calculated from steps by API)
  const totalTokens = (output.total_tokens as number | undefined) || executionTotalTokens
  const completedAt = output.completed_at as string | undefined

  // Session 770: Calculate total cost including TTS
  const ttsCost = podcastInfo ? parseFloat(podcastInfo.tts_cost) : 0
  const grandTotalCost = (totalCombinedCost ?? totalCost ?? 0) + ttsCost
  const stepOutputs = output.step_outputs as Record<string, Record<string, unknown>> | undefined

  return (
    <div className="p-4 border-t border-white/10">
      <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-3 flex items-center gap-2">
        <CheckCircle className="w-4 h-4 text-green-400" />
        Final Output
      </h4>

      {/* Summary Stats - Session 769: Show combined cost breakdown, Session 770: Show TTS cost */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        {(totalCombinedCost !== undefined || totalCost !== undefined || ttsCost > 0) && (
          <div className="bg-black/30 rounded-lg p-3 border border-white/5">
            <p className="text-xs text-gray-500 mb-1">Grand Total</p>
            <p className="text-lg font-semibold text-green-400 flex items-center gap-1">
              <DollarSign className="w-4 h-4" />
              {grandTotalCost.toFixed(4)}
            </p>
          </div>
        )}
        {totalCost !== undefined && (
          <div className="bg-black/30 rounded-lg p-3 border border-white/5">
            <p className="text-xs text-gray-500 mb-1">LLM Cost</p>
            <p className="text-sm font-medium text-gray-300">
              ${totalCost.toFixed(4)}
            </p>
          </div>
        )}
        {totalExternalCost !== undefined && totalExternalCost > 0 && (
          <div className="bg-black/30 rounded-lg p-3 border border-purple-500/20">
            <p className="text-xs text-purple-400 mb-1">External APIs</p>
            <p className="text-sm font-medium text-purple-300">
              ${totalExternalCost.toFixed(4)}
            </p>
          </div>
        )}
        {/* Session 770: Show TTS cost for podcast workflows */}
        {podcastInfo && ttsCost > 0 && (
          <div className="bg-black/30 rounded-lg p-3 border border-yellow-500/20">
            <p className="text-xs text-yellow-400 mb-1">ElevenLabs TTS</p>
            <p className="text-sm font-medium text-yellow-300">
              ${ttsCost.toFixed(4)}
            </p>
          </div>
        )}
        {totalTokens !== undefined && (
          <div className="bg-black/30 rounded-lg p-3 border border-white/5">
            <p className="text-xs text-gray-500 mb-1">Total Tokens</p>
            <p className="text-lg font-semibold text-blue-400 flex items-center gap-1">
              <Zap className="w-4 h-4" />
              {totalTokens.toLocaleString()}
            </p>
          </div>
        )}
      </div>

      {/* External Cost Breakdown - Session 769 */}
      {externalBreakdown && Object.keys(externalBreakdown).length > 0 && (
        <div className="mb-4 p-3 bg-purple-500/5 border border-purple-500/20 rounded-lg">
          <p className="text-xs text-purple-400 mb-2 font-medium">External API Cost Breakdown</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {Object.entries(externalBreakdown).map(([api, cost]) => (
              <div key={api} className="bg-black/20 rounded p-2">
                <p className="text-xs text-gray-400 capitalize">{api.replace(/_/g, ' ')}</p>
                <p className="text-sm font-medium text-purple-300">${cost.toFixed(4)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Session 770: Podcast Episode Info with TTS Cost */}
      {podcastInfo && (
        <div className="mb-4 p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-yellow-400" />
            <p className="text-xs text-yellow-400 font-medium">Podcast Episode</p>
            <span className={cn(
              'ml-auto text-xs px-2 py-0.5 rounded-full',
              podcastInfo.status === 'complete' ? 'bg-green-500/20 text-green-400' :
              podcastInfo.status === 'recording' ? 'bg-yellow-500/20 text-yellow-400' :
              podcastInfo.status === 'failed' ? 'bg-red-500/20 text-red-400' :
              'bg-gray-500/20 text-gray-400'
            )}>
              {podcastInfo.status}
            </span>
          </div>
          <p className="text-sm text-white font-medium mb-2">{podcastInfo.title}</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <div className="bg-black/20 rounded p-2">
              <p className="text-xs text-gray-400">TTS Cost</p>
              <p className="text-sm font-medium text-yellow-300">${parseFloat(podcastInfo.tts_cost).toFixed(4)}</p>
            </div>
            {podcastInfo.audio_duration_seconds && (
              <div className="bg-black/20 rounded p-2">
                <p className="text-xs text-gray-400">Duration</p>
                <p className="text-sm font-medium text-gray-300">
                  {Math.floor(podcastInfo.audio_duration_seconds / 60)}:{String(podcastInfo.audio_duration_seconds % 60).padStart(2, '0')}
                </p>
              </div>
            )}
            {podcastInfo.tts_cost_breakdown.total_characters && (
              <div className="bg-black/20 rounded p-2">
                <p className="text-xs text-gray-400">Characters</p>
                <p className="text-sm font-medium text-gray-300">
                  {podcastInfo.tts_cost_breakdown.total_characters.toLocaleString()}
                </p>
              </div>
            )}
          </div>
          {podcastInfo.audio_url && (
            <PodcastAudioPlayer
              audioUrl={podcastInfo.audio_url}
              durationSeconds={podcastInfo.audio_duration_seconds}
            />
          )}
        </div>
      )}

      {completedAt && (
        <div className="mb-4 text-xs text-gray-500">
          Completed: {new Date(completedAt).toLocaleString()}
        </div>
      )}

      {/* Step Outputs */}
      {stepOutputs && Object.keys(stepOutputs).length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2">Step Outputs ({Object.keys(stepOutputs).length} agents)</p>
          <div className="space-y-2">
            {Object.entries(stepOutputs).map(([agentName, agentOutput]) => {
              const isExpanded = expandedAgent === agentName
              const agentCost = agentOutput.cost as number | undefined
              const agentMessage = agentOutput.message as string | undefined

              return (
                <div key={agentName} className="bg-black/20 rounded-lg border border-white/5 overflow-hidden">
                  {/* Agent header - clickable */}
                  <button
                    onClick={() => setExpandedAgent(isExpanded ? null : agentName)}
                    className="w-full flex items-center justify-between p-3 hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Bot className="w-4 h-4 text-purple-400" />
                      <span className="text-sm font-medium text-white">{agentName}</span>
                      {agentCost !== undefined && (
                        <span className="text-xs text-gray-500">${agentCost.toFixed(4)}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {agentMessage && (
                        <span className="text-xs text-gray-400 max-w-xs truncate">
                          {agentMessage.slice(0, 50)}...
                        </span>
                      )}
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </button>

                  {/* Expanded content */}
                  {isExpanded && (
                    <div className="p-3 border-t border-white/5">
                      <FormattedOutputData data={agentOutput} agentName={agentName} />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * FormattedOutputData - Intelligent output rendering based on agent type
 * Session 769: Shows structured data instead of raw JSON
 */
function FormattedOutputData({ data, agentName }: { data: Record<string, unknown>; agentName: string }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const message = data.message as string | undefined
  const cost = data.cost as number | undefined
  const tokensUsed = data.tokens_used as number | undefined
  const executionTimeMs = data.execution_time_ms as number | undefined
  const innerData = data.data as Record<string, unknown> | undefined

  // Helper to render expandable text
  const TRUNCATE_LIMIT = 600
  const renderExpandableText = (text: string, customLimit?: number) => {
    const limit = customLimit || TRUNCATE_LIMIT
    const needsTruncation = text.length > limit
    const displayText = (!isExpanded && needsTruncation) ? text.slice(0, limit) + '...' : text

    return (
      <>
        <p className="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">{displayText}</p>
        {needsTruncation && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-purple-400 hover:text-purple-300 mt-2 flex items-center gap-1"
          >
            {isExpanded ? (
              <>Show less</>
            ) : (
              <>Show full output ({text.length.toLocaleString()} chars)</>
            )}
          </button>
        )}
      </>
    )
  }

  // Common footer with cost/tokens/time
  const CostFooter = () => (
    (cost !== undefined || tokensUsed !== undefined || executionTimeMs !== undefined) ? (
      <div className="flex items-center gap-4 text-xs text-gray-500 pt-2 border-t border-white/10 mt-3">
        {cost !== undefined && (
          <span className="flex items-center gap-1">
            <DollarSign className="w-3 h-3" />
            ${cost.toFixed(4)}
          </span>
        )}
        {tokensUsed !== undefined && (
          <span className="flex items-center gap-1">
            <Zap className="w-3 h-3" />
            {tokensUsed.toLocaleString()} tokens
          </span>
        )}
        {executionTimeMs !== undefined && (
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {(executionTimeMs / 1000).toFixed(1)}s
          </span>
        )}
      </div>
    ) : null
  )

  // ResearchAgent output formatting
  if (agentName === 'ResearchAgent' || agentName.toLowerCase().includes('research')) {
    // Extract nested data from results structure
    const nestedData = (innerData as { results?: Array<{ data?: Record<string, unknown> }> })?.results?.[0]?.data
    const actualData = nestedData || innerData || data

    // Topics can be string[] or {count, topic}[] format
    const rawTopics = actualData?.topics as (string[] | Array<{ count: number; topic: string }>) | undefined
    const topics = rawTopics?.map(t => typeof t === 'string' ? t : t.topic)
    const topicCounts = rawTopics?.reduce((acc, t) => {
      if (typeof t !== 'string' && t.topic) acc[t.topic] = t.count
      return acc
    }, {} as Record<string, number>)

    // Discussions
    const rawDiscussions = actualData?.discussions as Array<{
      title?: string
      source?: string
      url?: string
      excerpt?: string
      description?: string
      relevance?: number
      score?: number
    }> | undefined
    const discussions = rawDiscussions?.map(d => ({
      ...d,
      excerpt: d.excerpt || d.description,
      originalScore: d.score,
      relevance: d.relevance ?? (d.score ? Math.min(d.score / 500, 1) : undefined)
    }))

    // Sources
    const rawSources = actualData?.sources as (string[] | Record<string, number>) | undefined
    const sources = Array.isArray(rawSources) ? rawSources : rawSources ? Object.keys(rawSources) : undefined
    const sourceCounts = !Array.isArray(rawSources) ? rawSources : undefined

    return (
      <div className="space-y-4">
        {/* Summary message */}
        {message && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
            <p className="text-sm text-green-300">{message}</p>
          </div>
        )}

        {/* Topics */}
        {topics && topics.length > 0 && (
          <div>
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Topics ({topics.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {topics.map((topic, idx) => (
                <span key={idx} className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/30 flex items-center gap-1">
                  {topic}
                  {topicCounts?.[topic] !== undefined && (
                    <span className="bg-purple-500/30 px-1 rounded text-purple-200">{topicCounts[topic]}</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Discussions */}
        {discussions && discussions.length > 0 && (
          <div>
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Discussions ({discussions.length})
            </h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {discussions.slice(0, 5).map((disc, idx) => (
                <div key={idx} className="bg-black/30 rounded-lg p-3 border border-white/5">
                  <div className="flex items-start justify-between gap-2">
                    <h5 className="text-sm font-medium text-white line-clamp-1">{disc.title || 'Untitled'}</h5>
                    {disc.originalScore !== undefined && (
                      <span className={cn('text-xs px-1.5 py-0.5 rounded shrink-0',
                        disc.originalScore >= 200 ? 'bg-green-500/20 text-green-400' :
                        disc.originalScore >= 50 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-500/20 text-gray-400'
                      )}>{disc.originalScore} pts</span>
                    )}
                  </div>
                  {disc.source && <p className="text-xs text-blue-400 mt-1">{disc.source}</p>}
                  {disc.excerpt && <p className="text-xs text-gray-400 mt-2 line-clamp-2">{disc.excerpt}</p>}
                  {disc.url && (
                    <a href={disc.url} target="_blank" rel="noopener noreferrer"
                       className="text-xs text-purple-400 hover:text-purple-300 mt-2 inline-block">
                      View source →
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sources */}
        {sources && sources.length > 0 && (
          <div>
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Sources ({sources.length})</h4>
            <div className="flex flex-wrap gap-1">
              {sources.map((source, idx) => (
                <span key={idx} className="px-2 py-0.5 text-xs bg-blue-500/10 text-blue-300 rounded border border-blue-500/20 flex items-center gap-1">
                  {source}
                  {sourceCounts?.[source] !== undefined && (
                    <span className="bg-blue-500/20 px-1 rounded text-blue-200">{sourceCounts[source]}</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}

        <CostFooter />
      </div>
    )
  }

  // Debate agents (Advocate, Skeptic) and Moderator
  if (agentName.includes('Advocate') || agentName.includes('Skeptic') || agentName.includes('Moderator')) {
    const role = innerData?.role as string | undefined
    const voiceId = innerData?.voice_id as string | undefined

    const roleConfig: Record<string, { color: string; bgColor: string; label: string }> = {
      'ADVOCATE': { color: 'text-green-400', bgColor: 'bg-green-500/20', label: '👍 Advocate' },
      'SKEPTIC': { color: 'text-red-400', bgColor: 'bg-red-500/20', label: '🤔 Skeptic' },
      'HOST': { color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: '🎙️ Host' },
    }
    const config = roleConfig[role || ''] || { color: 'text-gray-400', bgColor: 'bg-gray-500/20', label: role || 'Speaker' }

    return (
      <div className="space-y-3">
        {/* Role badge and voice */}
        <div className="flex items-center gap-3">
          <span className={cn('px-3 py-1 text-sm font-medium rounded-full', config.bgColor, config.color)}>
            {config.label}
          </span>
          {voiceId && (
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <Activity className="w-3 h-3" /> Voice: {voiceId}
            </span>
          )}
        </div>

        {/* Message content - Session 770: Now expandable */}
        {message && (
          <div className="bg-black/30 rounded-lg p-4 border border-white/5">
            {renderExpandableText(message)}
          </div>
        )}

        <CostFooter />
      </div>
    )
  }

  // PodcastCoordinatorAgent
  if (agentName.includes('PodcastCoordinator')) {
    const toolResults = innerData?.tool_results as Array<{
      topic?: string
      format?: Record<string, string>
      participants?: Array<{ role: string; voice_id: string; perspective: string }>
      key_questions?: string[]
    }> | undefined
    const result = toolResults?.[0]

    return (
      <div className="space-y-4">
        {/* Summary */}
        {message && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <p className="text-sm text-green-300">{message}</p>
            </div>
          </div>
        )}

        {/* Topic */}
        {result?.topic && (
          <div>
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Episode Topic</h4>
            <p className="text-sm text-white font-medium">{result.topic}</p>
          </div>
        )}

        {/* Participants */}
        {result?.participants && result.participants.length > 0 && (
          <div>
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Participants ({result.participants.length})
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {result.participants.map((p, idx) => (
                <div key={idx} className="bg-black/30 rounded-lg p-2 border border-white/5">
                  <div className="flex items-center gap-2">
                    <span className={cn('text-xs px-2 py-0.5 rounded-full font-medium',
                      p.role === 'host' ? 'bg-blue-500/20 text-blue-300' :
                      p.role === 'advocate' ? 'bg-green-500/20 text-green-300' :
                      p.role === 'skeptic' ? 'bg-red-500/20 text-red-300' :
                      'bg-purple-500/20 text-purple-300'
                    )}>{p.role}</span>
                    <span className="text-xs text-gray-500">{p.voice_id}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{p.perspective}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Format structure */}
        {result?.format && (
          <div>
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Episode Format</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(result.format).map(([key, value]) => (
                <div key={key} className="bg-black/30 rounded px-2 py-1 border border-white/5">
                  <span className="text-xs text-purple-400 font-medium">{key.replace(/_/g, ' ')}</span>
                  <span className="text-xs text-gray-500 ml-1">({value})</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Key questions */}
        {result?.key_questions && result.key_questions.length > 0 && (
          <div>
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Key Questions</h4>
            <ul className="space-y-1">
              {result.key_questions.slice(0, 3).map((q, idx) => (
                <li key={idx} className="text-xs text-gray-300 flex items-start gap-2">
                  <span className="text-purple-400 shrink-0">•</span>
                  <span className="line-clamp-2">{q}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <CostFooter />
      </div>
    )
  }

  // ContentWriterAgent, ContentStrategyAgent, etc. - Session 770: Now expandable
  if (agentName.includes('Content') || agentName.includes('Writer') || agentName.includes('Strategy')) {
    return (
      <div className="space-y-3">
        {message && (
          <div className="bg-black/30 rounded-lg p-4 border border-white/5">
            {renderExpandableText(message)}
          </div>
        )}
        {innerData && Object.keys(innerData).length > 0 && (
          <div className="bg-black/20 rounded-lg p-3">
            <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Additional Data</h4>
            <pre className="text-xs text-gray-300 overflow-x-auto">{JSON.stringify(innerData, null, 2)}</pre>
          </div>
        )}
        <CostFooter />
      </div>
    )
  }

  // Default: Show message prominently + formatted data - Session 770: Now expandable
  return (
    <div className="space-y-3">
      {/* Message */}
      {message && (
        <div className="bg-black/30 rounded-lg p-4 border border-white/5">
          {renderExpandableText(message)}
        </div>
      )}

      {/* Data summary */}
      {innerData && Object.keys(innerData).length > 0 && (
        <div className="bg-black/20 rounded-lg p-3">
          <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">Output Data</h4>
          <pre className="text-xs text-gray-300 overflow-x-auto max-h-48">
            {JSON.stringify(innerData, null, 2)}
          </pre>
        </div>
      )}

      <CostFooter />
    </div>
  )
}

function StepIntelligencePanel({ intelligence }: { intelligence: StepIntelligenceData }) {
  const { step_info, agent_execution, memories_created, context_injected, tool_calls } = intelligence
  const [expandedSection, setExpandedSection] = useState<string | null>('output')

  const sections = [
    { id: 'output', label: 'Output Data', icon: FileText, count: step_info.output_data ? 1 : 0 },
    { id: 'context', label: 'Injected Context', icon: Brain, count: Object.keys(context_injected || {}).length },
    { id: 'tools', label: 'Tool Calls', icon: Terminal, count: tool_calls?.length || 0 },
    { id: 'memories', label: 'Memories Created', icon: Sparkles, count: memories_created?.length || 0 },
  ]

  return (
    <div className="space-y-3">
      {/* Section tabs */}
      <div className="flex flex-wrap gap-2">
        {sections.map(section => (
          <button
            key={section.id}
            onClick={() => setExpandedSection(expandedSection === section.id ? null : section.id)}
            className={cn(
              'flex items-center gap-1.5 px-2 py-1 text-xs rounded transition-colors',
              expandedSection === section.id
                ? 'bg-purple-500/30 text-purple-300'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            )}
          >
            <section.icon className="w-3.5 h-3.5" />
            {section.label}
            {section.count > 0 && (
              <span className="bg-white/10 px-1.5 rounded-full">{section.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Section content */}
      {expandedSection === 'output' && step_info.output_data && (
        <FormattedOutputData data={step_info.output_data} agentName={step_info.agent_name} />
      )}

      {expandedSection === 'context' && context_injected && Object.keys(context_injected).length > 0 && (
        <div className="space-y-3">
          {Object.entries(context_injected).map(([key, rawValue]) => {
            // Format the key nicely
            const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

            // Render based on type
            const renderValue = () => {
              if (typeof rawValue === 'string') {
                const strVal = rawValue as string
                return (
                  <p className="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">
                    {strVal.length > 500 ? strVal.slice(0, 500) + '...' : strVal}
                  </p>
                )
              }
              if (typeof rawValue === 'boolean') {
                return (
                  <span className={cn('text-xs px-2 py-0.5 rounded',
                    rawValue ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  )}>
                    {rawValue ? '✓ Enabled' : '✗ Disabled'}
                  </span>
                )
              }
              if (typeof rawValue === 'number') {
                return <span className="text-sm text-blue-300 font-medium">{rawValue}</span>
              }
              if (Array.isArray(rawValue)) {
                const arrVal = rawValue as unknown[]
                return (
                  <div className="flex flex-wrap gap-2">
                    {arrVal.slice(0, 10).map((item, idx) => (
                      <span key={idx} className="text-xs bg-purple-500/10 text-purple-300 px-2 py-0.5 rounded">
                        {String(item)}
                      </span>
                    ))}
                    {arrVal.length > 10 && (
                      <span className="text-xs text-gray-500">+{arrVal.length - 10} more</span>
                    )}
                  </div>
                )
              }
              if (rawValue !== null && typeof rawValue === 'object') {
                const jsonStr = JSON.stringify(rawValue, null, 2)
                return (
                  <div className="bg-black/20 rounded p-2 max-h-32 overflow-y-auto">
                    <pre className="text-xs text-gray-300">
                      {jsonStr.slice(0, 400)}
                      {jsonStr.length > 400 && '...'}
                    </pre>
                  </div>
                )
              }
              return null
            }

            return (
              <div key={key} className="bg-black/30 rounded-lg p-3 border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <p className="text-sm font-medium text-purple-400">{formattedKey}</p>
                </div>
                {renderValue()}
              </div>
            )
          })}
        </div>
      )}

      {expandedSection === 'tools' && tool_calls && tool_calls.length > 0 && (
        <div className="space-y-3">
          {tool_calls.map((tool, index) => {
            // Handle different tool call formats: {tool, arguments, result} or {name, function, arguments}
            const toolName = tool.tool || tool.name || tool.function || 'Unknown Tool'
            const args = tool.arguments || {}
            const result = tool.result as { success?: boolean; data?: Record<string, unknown> } | undefined

            return (
              <div key={index} className="bg-black/30 rounded-lg p-3 border border-white/5">
                {/* Tool header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-green-400" />
                    <span className="text-sm font-medium text-green-400">{toolName}</span>
                  </div>
                  {result?.success !== undefined && (
                    <span className={cn('text-xs px-2 py-0.5 rounded-full',
                      result.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    )}>
                      {result.success ? '✓ Success' : '✗ Failed'}
                    </span>
                  )}
                </div>

                {/* Arguments */}
                {Object.keys(args).length > 0 && (
                  <div className="mb-2">
                    <p className="text-xs text-gray-500 mb-1">Arguments:</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(args).map(([key, value]) => (
                        <span key={key} className="text-xs bg-blue-500/10 text-blue-300 px-2 py-0.5 rounded">
                          {key}: <span className="text-blue-200">{String(value)}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Result summary - Session 770: Smart formatting */}
                {result?.data && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Result:</p>
                    <div className="bg-black/20 rounded p-2 max-h-48 overflow-y-auto">
                      {renderToolResult(result.data)}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {expandedSection === 'memories' && memories_created && memories_created.length > 0 && (
        <div className="space-y-3">
          {memories_created.map((memory) => (
            <div key={memory.id} className="bg-black/30 rounded-lg p-3 border border-white/5">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded-full font-medium',
                    memory.valence === 'positive' ? 'bg-green-500/20 text-green-400' :
                    memory.valence === 'negative' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  )}>
                    {memory.memory_type?.replace(/_/g, ' ') || 'Memory'}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span className={cn(
                    'px-1.5 py-0.5 rounded',
                    memory.importance_score >= 0.7 ? 'bg-amber-500/20 text-amber-400' :
                    memory.importance_score >= 0.4 ? 'bg-blue-500/20 text-blue-400' :
                    'bg-gray-500/20 text-gray-400'
                  )}>
                    {(memory.importance_score * 100).toFixed(0)}% importance
                  </span>
                </div>
              </div>
              {memory.title && (
                <p className="text-sm font-medium text-white mb-1">{memory.title}</p>
              )}
              <p className="text-sm text-gray-300 leading-relaxed">
                {memory.content.length > 300 ? memory.content.slice(0, 300) + '...' : memory.content}
              </p>
              {memory.created_at && (
                <p className="text-xs text-gray-500 mt-2">
                  Created: {new Date(memory.created_at).toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Agent execution link */}
      {agent_execution && (
        <div className="text-xs text-gray-500 border-t border-white/10 pt-2 mt-2">
          <span className="text-gray-400">Execution ID:</span>{' '}
          <code className="bg-black/30 px-1 py-0.5 rounded">{agent_execution.id}</code>
        </div>
      )}
    </div>
  )
}

function AnalyticsSidebar({
  analytics,
  executions
}: {
  analytics: {
    totalWorkflows: number
    totalExecutions: number
    runningCount: number
    completedCount: number
    failedCount: number
    totalCost: number
    totalTokens: number
    successRate: number
  }
  executions: OrchestrationExecution[]
}) {
  // Group executions by status
  const byStatus = executions.reduce((acc, ex) => {
    acc[ex.status] = (acc[ex.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">
        Analytics Overview
      </h3>

      <div className="space-y-2">
        {Object.entries(byStatus).map(([status, count]) => {
          const config = statusConfig[status] || statusConfig.pending
          const StatusIcon = config.icon

          return (
            <div key={status} className="flex items-center justify-between bg-white/5 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <div className={cn('p-1.5 rounded-lg', config.bgColor)}>
                  <StatusIcon className={cn('w-4 h-4', config.color)} />
                </div>
                <span className="text-sm text-gray-300 capitalize">
                  {status.replace('_', ' ')}
                </span>
              </div>
              <span className="text-lg font-semibold text-white">{count}</span>
            </div>
          )
        })}
      </div>

      <div className="bg-white/5 rounded-lg p-4 border border-white/10">
        <h4 className="text-sm font-medium text-white mb-3">Cost Breakdown</h4>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm text-gray-400">Total Cost</span>
            <span className="text-sm text-white">${analytics.totalCost.toFixed(4)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-400">Total Tokens</span>
            <span className="text-sm text-white">{analytics.totalTokens.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-400">Avg. Cost/Execution</span>
            <span className="text-sm text-white">
              ${analytics.totalExecutions > 0
                ? (analytics.totalCost / analytics.totalExecutions).toFixed(4)
                : '0.0000'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

function AnalyticsDashboard({
  analytics,
  executions
}: {
  analytics: {
    totalWorkflows: number
    totalExecutions: number
    runningCount: number
    completedCount: number
    failedCount: number
    totalCost: number
    totalTokens: number
    successRate: number
  }
  executions: OrchestrationExecution[]
}) {
  // Get top workflows by execution count
  const workflowCounts = executions.reduce((acc, ex) => {
    acc[ex.workflow_name] = (acc[ex.workflow_name] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const topWorkflows = Object.entries(workflowCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  // Recent activity
  const recentExecutions = executions.slice(0, 10)

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-6">
      <h3 className="text-lg font-semibold text-white mb-6">Orchestration Analytics</h3>

      <div className="grid grid-cols-2 gap-6">
        {/* Success Rate */}
        <div className="bg-white/5 rounded-xl p-4">
          <h4 className="text-sm text-gray-400 mb-2">Success Rate</h4>
          <div className="flex items-end gap-2">
            <span className="text-4xl font-bold text-green-400">{analytics.successRate}%</span>
            <span className="text-sm text-gray-500 mb-1">
              ({analytics.completedCount}/{analytics.totalExecutions})
            </span>
          </div>
          <div className="h-2 bg-white/5 rounded-full mt-3 overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full"
              style={{ width: `${analytics.successRate}%` }}
            />
          </div>
        </div>

        {/* Cost Analysis */}
        <div className="bg-white/5 rounded-xl p-4">
          <h4 className="text-sm text-gray-400 mb-2">Cost Analysis</h4>
          <div className="text-4xl font-bold text-yellow-400">${analytics.totalCost.toFixed(2)}</div>
          <p className="text-sm text-gray-500 mt-1">
            {analytics.totalTokens.toLocaleString()} tokens used
          </p>
        </div>
      </div>

      {/* Top Workflows */}
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-3">
          Most Executed Workflows
        </h4>
        <div className="space-y-2">
          {topWorkflows.map(([name, count], index) => (
            <div key={name} className="flex items-center gap-3 bg-white/5 rounded-lg p-3">
              <span className="text-lg font-bold text-purple-400">#{index + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{name}</p>
              </div>
              <span className="text-sm text-gray-400">{count} runs</span>
            </div>
          ))}
          {topWorkflows.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-4">
              No execution data yet
            </p>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-3">
          Recent Activity
        </h4>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {recentExecutions.map((ex) => {
            const config = statusConfig[ex.status] || statusConfig.pending
            const StatusIcon = config.icon

            return (
              <div key={ex.id} className="flex items-center gap-3 bg-white/5 rounded-lg p-2">
                <div className={cn('p-1 rounded', config.bgColor)}>
                  <StatusIcon className={cn('w-3.5 h-3.5', config.color)} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-white truncate">{ex.workflow_name}</p>
                  <p className="text-xs text-gray-500">
                    {ex.started_at && new Date(ex.started_at).toLocaleString()}
                  </p>
                </div>
                <span className="text-xs text-gray-400">${parseFloat(ex.total_cost).toFixed(4)}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function EmptyDetailPanel() {
  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-12 text-center">
      <Eye className="w-16 h-16 text-gray-600 mx-auto mb-4" />
      <h3 className="text-xl font-semibold text-white mb-2">Select an Execution</h3>
      <p className="text-gray-400 max-w-sm mx-auto">
        Choose an execution from the list to view its details, step-by-step progress, and intelligence data.
      </p>
    </div>
  )
}

// Session 768: Workflow Detail View with step visualization and inline execution
function WorkflowDetailView({
  workflow,
  steps,
  inputParameters,
  loading,
  onExecute,
  onClose,
  onExecuteWithInput,
  isExecuting = false,
}: {
  workflow: OrchestrationWorkflowDetail
  steps: OrchestrationWorkflowStep[]
  inputParameters: string[]
  loading: boolean
  onExecute: () => void
  onClose: () => void
  onExecuteWithInput?: (input: Record<string, string>) => void
  isExecuting?: boolean
}) {
  const [expandedStep, setExpandedStep] = useState<number | null>(null)
  const [inputValues, setInputValues] = useState<Record<string, string>>({})
  const modeInfo = executionModeInfo[workflow.execution_mode as keyof typeof executionModeInfo] || executionModeInfo.sequential

  // Handle inline execution
  const handleQuickExecute = () => {
    if (onExecuteWithInput) {
      onExecuteWithInput(inputValues)
    } else {
      onExecute()
    }
  }

  if (loading) {
    return (
      <div className="bg-white/5 rounded-xl border border-white/10 p-12 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
      </div>
    )
  }

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 overflow-hidden max-h-[calc(100vh-280px)] overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-white/10 sticky top-0 bg-gray-900/95 backdrop-blur z-10">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Workflow className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">{workflow.name}</h3>
              {workflow.description && (
                <p className="text-sm text-gray-400 mt-0.5">{workflow.description}</p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg text-gray-400 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {workflow.is_template && (
          <div className="mt-2 flex items-center gap-2 text-xs text-purple-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>System Template - Ready to use</span>
          </div>
        )}
      </div>

      {/* Quick Execute Section - Most prominent */}
      {inputParameters.length > 0 && (
        <div className="p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-b border-white/10">
          <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            Quick Execute
          </h4>
          <div className="space-y-3">
            {inputParameters.map(param => (
              <div key={param}>
                <label className="block text-sm text-gray-300 mb-1.5 capitalize">
                  {param.replace(/_/g, ' ')}
                  <span className="text-gray-500 ml-1 font-normal">*</span>
                </label>
                <input
                  type="text"
                  value={inputValues[param] || ''}
                  onChange={(e) => setInputValues(prev => ({ ...prev, [param]: e.target.value }))}
                  className="w-full bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white text-base placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder={
                    param === 'topic'
                      ? 'e.g., "The future of AI in healthcare" or "Climate change solutions"'
                      : `Enter ${param}...`
                  }
                />
              </div>
            ))}
            <button
              onClick={handleQuickExecute}
              disabled={isExecuting || inputParameters.some(p => !inputValues[p]?.trim())}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors mt-2"
            >
              {isExecuting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Starting Workflow...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Run {workflow.name}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* No inputs - Simple execute */}
      {inputParameters.length === 0 && (
        <div className="p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-b border-white/10">
          <button
            onClick={onExecute}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-500 hover:bg-purple-600 rounded-lg text-white font-medium transition-colors"
          >
            <Play className="w-5 h-5" />
            Run {workflow.name}
          </button>
        </div>
      )}

      {/* Workflow metadata */}
      <div className="p-4 border-b border-white/10">
        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Configuration</h4>
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-white/5 rounded-lg p-2.5 text-center">
            <div className="flex items-center justify-center gap-1 text-purple-400">
              <modeInfo.icon className="w-3.5 h-3.5" />
              <span className="text-xs font-medium">{modeInfo.label}</span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">Mode</p>
          </div>
          <div className="bg-white/5 rounded-lg p-2.5 text-center">
            <p className="text-base font-semibold text-white">{steps.length}</p>
            <p className="text-xs text-gray-500">Steps</p>
          </div>
          <div className="bg-white/5 rounded-lg p-2.5 text-center">
            <p className="text-base font-semibold text-white">
              {Math.round(workflow.timeout_seconds / 60)}m
            </p>
            <p className="text-xs text-gray-500">Timeout</p>
          </div>
          <div className="bg-white/5 rounded-lg p-2.5 text-center">
            <p className="text-base font-semibold text-white">
              {workflow.cost_budget ? `$${workflow.cost_budget}` : '∞'}
            </p>
            <p className="text-xs text-gray-500">Budget</p>
          </div>
        </div>
      </div>

      {/* Steps pipeline visualization */}
      <div className="p-4">
        <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">
          Workflow Steps
        </h4>
        <div className="space-y-3">
          {steps.map((step, index) => {
            const isExpanded = expandedStep === step.order
            const hasDependencies = step.depends_on_steps.length > 0

            return (
              <div key={step.id} className="relative">
                {/* Connection line */}
                {index > 0 && (
                  <div className="absolute left-6 -top-3 w-0.5 h-3 bg-gray-700" />
                )}

                <button
                  onClick={() => setExpandedStep(isExpanded ? null : step.order)}
                  className={cn(
                    "w-full text-left bg-white/5 rounded-lg border transition-colors",
                    isExpanded
                      ? "border-purple-500/50 bg-purple-500/5"
                      : "border-white/10 hover:border-white/20"
                  )}
                >
                  <div className="p-4">
                    <div className="flex items-center gap-4">
                      {/* Step number */}
                      <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                        <span className="text-lg font-bold text-purple-400">{step.order}</span>
                      </div>

                      {/* Step info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h5 className="font-semibold text-white">{step.name}</h5>
                          {step.requires_approval && (
                            <span className="px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded-full flex items-center gap-1">
                              <Shield className="w-3 h-3" />
                              Approval
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <Bot className="w-4 h-4" />
                            {step.agent}
                          </span>
                          <span className="text-gray-600">•</span>
                          <span>{step.timeout_seconds}s timeout</span>
                          {step.retry_count > 0 && (
                            <>
                              <span className="text-gray-600">•</span>
                              <span>{step.retry_count} retries</span>
                            </>
                          )}
                        </div>
                        {hasDependencies && (
                          <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                            <ArrowRight className="w-3 h-3" />
                            Depends on: Step {step.depends_on_steps.join(', ')}
                          </div>
                        )}
                      </div>

                      {/* Expand icon */}
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </div>

                    {/* Expanded content */}
                    {isExpanded && (
                      <div className="mt-4 pt-4 border-t border-white/10 space-y-4">
                        {step.description && (
                          <div>
                            <label className="text-xs text-gray-500 uppercase tracking-wide">Description</label>
                            <p className="text-sm text-gray-300 mt-1">{step.description}</p>
                          </div>
                        )}

                        {step.prompt_template && (
                          <div>
                            <label className="text-xs text-gray-500 uppercase tracking-wide">Prompt Template</label>
                            <pre className="mt-1 p-3 bg-black/30 rounded-lg text-xs text-gray-300 font-mono overflow-x-auto whitespace-pre-wrap">
                              {step.prompt_template}
                            </pre>
                          </div>
                        )}

                        {step.input_params.length > 0 && (
                          <div>
                            <label className="text-xs text-gray-500 uppercase tracking-wide">Input Parameters</label>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {step.input_params.map(param => (
                                <span key={param} className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs font-mono">
                                  {'{' + param + '}'}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <label className="text-xs text-gray-500 uppercase tracking-wide">Timeout</label>
                            <p className="text-sm text-white mt-1">{step.timeout_seconds} seconds</p>
                          </div>
                          <div>
                            <label className="text-xs text-gray-500 uppercase tracking-wide">Retries</label>
                            <p className="text-sm text-white mt-1">{step.retry_count}</p>
                          </div>
                          <div>
                            <label className="text-xs text-gray-500 uppercase tracking-wide">Required</label>
                            <p className="text-sm text-white mt-1">{step.is_required ? 'Yes' : 'No'}</p>
                          </div>
                        </div>

                        {step.rollback_step && (
                          <div className="p-2 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                            <div className="flex items-center gap-2 text-sm text-orange-400">
                              <RotateCcw className="w-4 h-4" />
                              <span>On failure, rollback to Step {step.rollback_step}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// Session 768: Workflow Builder for creating new workflows
function WorkflowBuilder({
  agents,
  onSave,
  onCancel,
  isSaving,
}: {
  agents: OrchestrationAgent[]
  onSave: (data: CreateWorkflowRequest) => void
  onCancel: () => void
  isSaving: boolean
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [executionMode, setExecutionMode] = useState<'sequential' | 'parallel' | 'dependency'>('sequential')
  const [maxRetries, setMaxRetries] = useState(3)
  const [timeoutSeconds, setTimeoutSeconds] = useState(3600)
  const [costBudget, setCostBudget] = useState('')
  const [steps, setSteps] = useState<Array<{
    name: string
    description: string
    agent: string
    prompt_template: string
    timeout_seconds: number
    requires_approval: boolean
    depends_on_steps: number[]
  }>>([
    {
      name: 'Step 1',
      description: '',
      agent: 'PersonalAssistantAgent',
      prompt_template: '',
      timeout_seconds: 300,
      requires_approval: false,
      depends_on_steps: [],
    }
  ])

  const addStep = () => {
    setSteps([...steps, {
      name: `Step ${steps.length + 1}`,
      description: '',
      agent: 'PersonalAssistantAgent',
      prompt_template: '',
      timeout_seconds: 300,
      requires_approval: false,
      depends_on_steps: [],
    }])
  }

  const removeStep = (index: number) => {
    if (steps.length > 1) {
      setSteps(steps.filter((_, i) => i !== index))
    }
  }

  const updateStep = (index: number, updates: Partial<typeof steps[0]>) => {
    const newSteps = [...steps]
    newSteps[index] = { ...newSteps[index], ...updates }
    setSteps(newSteps)
  }

  const handleSave = () => {
    if (!name.trim()) return

    onSave({
      name: name.trim(),
      description: description.trim(),
      execution_mode: executionMode,
      max_retries: maxRetries,
      timeout_seconds: timeoutSeconds,
      cost_budget: costBudget || undefined,
      steps: steps.map((step, index) => ({
        order: index + 1,
        name: step.name,
        description: step.description,
        agent: step.agent,
        prompt_template: step.prompt_template,
        timeout_seconds: step.timeout_seconds,
        requires_approval: step.requires_approval,
        depends_on_steps: step.depends_on_steps,
      })),
    })
  }

  // Group agents by category
  const agentsByCategory = agents.reduce((acc, agent) => {
    if (!acc[agent.category]) acc[agent.category] = []
    acc[agent.category].push(agent)
    return acc
  }, {} as Record<string, OrchestrationAgent[]>)

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Plus className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Create New Workflow</h3>
              <p className="text-sm text-gray-400">Design a multi-agent workflow pipeline</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!name.trim() || isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white text-sm transition-colors"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Workflow
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Basic info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Workflow Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
              placeholder="e.g., Research to Blog Post"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Execution Mode</label>
            <select
              value={executionMode}
              onChange={(e) => setExecutionMode(e.target.value as typeof executionMode)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
            >
              <option value="sequential">Sequential (one after another)</option>
              <option value="parallel">Parallel (independent steps run together)</option>
              <option value="dependency">Dependency (based on depends_on)</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-purple-500 h-20 resize-none"
            placeholder="Describe what this workflow does..."
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Max Retries</label>
            <input
              type="number"
              value={maxRetries}
              onChange={(e) => setMaxRetries(parseInt(e.target.value) || 0)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Timeout (seconds)</label>
            <input
              type="number"
              value={timeoutSeconds}
              onChange={(e) => setTimeoutSeconds(parseInt(e.target.value) || 300)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Cost Budget ($)</label>
            <input
              type="text"
              value={costBudget}
              onChange={(e) => setCostBudget(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
              placeholder="Optional"
            />
          </div>
        </div>

        {/* Steps */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wide">
              Workflow Steps ({steps.length})
            </h4>
            <button
              onClick={addStep}
              className="flex items-center gap-1 px-3 py-1.5 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg text-purple-400 text-sm transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Step
            </button>
          </div>

          <div className="space-y-4">
            {steps.map((step, index) => (
              <div
                key={index}
                className="bg-black/20 rounded-lg border border-white/10 p-4"
              >
                <div className="flex items-start gap-4">
                  {/* Step number */}
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <span className="text-lg font-bold text-purple-400">{index + 1}</span>
                  </div>

                  <div className="flex-1 space-y-4">
                    {/* Step header */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Step Name</label>
                        <input
                          type="text"
                          value={step.name}
                          onChange={(e) => updateStep(index, { name: e.target.value })}
                          className="w-full bg-black/30 border border-white/10 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Agent</label>
                        <select
                          value={step.agent}
                          onChange={(e) => updateStep(index, { agent: e.target.value })}
                          className="w-full bg-black/30 border border-white/10 rounded px-2 py-1.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                        >
                          {Object.entries(agentsByCategory).map(([category, categoryAgents]) => (
                            <optgroup key={category} label={category}>
                              {categoryAgents.map(agent => (
                                <option key={agent.key} value={agent.key}>
                                  {agent.name}
                                </option>
                              ))}
                            </optgroup>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Prompt template */}
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">
                        Prompt Template
                        <span className="text-gray-600 ml-2">
                          Use {'{variable}'} for inputs, {'{step_N}'} for previous step outputs
                        </span>
                      </label>
                      <textarea
                        value={step.prompt_template}
                        onChange={(e) => updateStep(index, { prompt_template: e.target.value })}
                        className="w-full bg-black/30 border border-white/10 rounded px-2 py-1.5 text-sm text-white font-mono focus:outline-none focus:ring-1 focus:ring-purple-500 h-20 resize-none"
                        placeholder="e.g., Research {topic} and provide a comprehensive summary"
                      />
                    </div>

                    {/* Step options */}
                    <div className="flex items-center gap-6">
                      <label className="flex items-center gap-2 text-sm text-gray-400">
                        <input
                          type="checkbox"
                          checked={step.requires_approval}
                          onChange={(e) => updateStep(index, { requires_approval: e.target.checked })}
                          className="w-4 h-4 rounded bg-black/30 border-white/10 text-purple-500 focus:ring-purple-500"
                        />
                        Requires Approval
                      </label>
                      <div className="flex items-center gap-2">
                        <label className="text-sm text-gray-400">Timeout:</label>
                        <input
                          type="number"
                          value={step.timeout_seconds}
                          onChange={(e) => updateStep(index, { timeout_seconds: parseInt(e.target.value) || 300 })}
                          className="w-20 bg-black/30 border border-white/10 rounded px-2 py-1 text-sm text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                        />
                        <span className="text-sm text-gray-500">sec</span>
                      </div>
                    </div>
                  </div>

                  {/* Delete button */}
                  {steps.length > 1 && (
                    <button
                      onClick={() => removeStep(index)}
                      className="p-1.5 hover:bg-red-500/20 rounded text-gray-500 hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Session 768: Enhanced execute modal with dynamic input fields
function ExecuteWorkflowModal({
  workflowId,
  workflow,
  onClose,
  onExecute,
  isExecuting,
}: {
  workflowId: string
  workflow?: OrchestrationWorkflow
  onClose: () => void
  onExecute: (input?: Record<string, unknown>) => void
  isExecuting: boolean
}) {
  const [inputValues, setInputValues] = useState<Record<string, string>>({})
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [advancedJson, setAdvancedJson] = useState('{}')
  const [error, setError] = useState<string | null>(null)

  // Fetch workflow detail to get input parameters
  const { data: detailData, isLoading: detailLoading } = useQuery({
    queryKey: ['orchestration-workflow-detail', workflowId],
    queryFn: () => orchestrationApi.getWorkflowDetail(workflowId),
    enabled: !!workflowId,
  })

  const inputParameters = detailData?.data?.input_parameters || []
  const steps = detailData?.data?.steps || []

  const handleExecute = () => {
    try {
      let input: Record<string, unknown>

      if (showAdvanced) {
        input = JSON.parse(advancedJson)
      } else {
        // Build input from dynamic fields
        input = { ...inputValues }
      }

      setError(null)
      onExecute(input)
    } catch (e) {
      setError('Invalid JSON input')
    }
  }

  // Update input value
  const updateInputValue = (param: string, value: string) => {
    setInputValues(prev => ({ ...prev, [param]: value }))
  }

  if (!workflow) return null

  const modeInfo = executionModeInfo[workflow.execution_mode as keyof typeof executionModeInfo] || executionModeInfo.sequential

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-xl border border-white/10 w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Play className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Execute Workflow</h3>
              <p className="text-sm text-gray-400">{workflow.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <div className="p-4 space-y-4 overflow-y-auto flex-1">
          {/* Workflow info */}
          <div className="bg-white/5 rounded-lg p-3">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-lg font-semibold text-white">{workflow.step_count}</p>
                <p className="text-xs text-gray-500">Steps</p>
              </div>
              <div>
                <p className="text-sm font-medium text-white">{modeInfo.label}</p>
                <p className="text-xs text-gray-500">Mode</p>
              </div>
              <div>
                <p className="text-lg font-semibold text-white">{Math.round(workflow.timeout_seconds / 60)}m</p>
                <p className="text-xs text-gray-500">Timeout</p>
              </div>
              <div>
                <p className="text-lg font-semibold text-white">{workflow.cost_budget ? `$${workflow.cost_budget}` : '∞'}</p>
                <p className="text-xs text-gray-500">Budget</p>
              </div>
            </div>
          </div>

          {/* Dynamic input fields */}
          {detailLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
            </div>
          ) : inputParameters.length > 0 && !showAdvanced ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-400">Required Inputs</h4>
                <button
                  onClick={() => setShowAdvanced(true)}
                  className="text-xs text-purple-400 hover:text-purple-300"
                >
                  Switch to JSON
                </button>
              </div>
              {inputParameters.map(param => (
                <div key={param}>
                  <label className="block text-sm text-gray-400 mb-2 font-mono">
                    {'{' + param + '}'}
                  </label>
                  <input
                    type="text"
                    value={inputValues[param] || ''}
                    onChange={(e) => updateInputValue(param, e.target.value)}
                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                    placeholder={`Enter ${param}...`}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-gray-400">Input Data (JSON)</label>
                {inputParameters.length > 0 && (
                  <button
                    onClick={() => setShowAdvanced(false)}
                    className="text-xs text-purple-400 hover:text-purple-300"
                  >
                    Switch to Form
                  </button>
                )}
              </div>
              <textarea
                value={advancedJson}
                onChange={(e) => setAdvancedJson(e.target.value)}
                className="w-full h-32 bg-black/30 rounded-lg border border-white/10 p-3 text-sm text-white font-mono resize-none focus:outline-none focus:ring-1 focus:ring-purple-500"
                placeholder={inputParameters.length > 0
                  ? `{\n  "${inputParameters[0]}": "your value here"\n}`
                  : '{"key": "value"}'}
              />
              {error && (
                <p className="text-xs text-red-400 mt-1">{error}</p>
              )}
            </div>
          )}

          {/* Steps preview */}
          {steps.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Workflow Steps</h4>
              <div className="space-y-2">
                {steps.map((step, index) => (
                  <div key={step.id} className="flex items-center gap-3 bg-black/20 rounded-lg p-2">
                    <div className="w-6 h-6 rounded bg-purple-500/20 flex items-center justify-center">
                      <span className="text-xs font-bold text-purple-400">{index + 1}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white truncate">{step.name}</p>
                      <p className="text-xs text-gray-500">{step.agent}</p>
                    </div>
                    {step.requires_approval && (
                      <span className="px-1.5 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded">
                        Approval
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-3 p-4 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleExecute}
            disabled={isExecuting}
            className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg text-white text-sm transition-colors disabled:opacity-50"
          >
            {isExecuting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Execute Workflow
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
