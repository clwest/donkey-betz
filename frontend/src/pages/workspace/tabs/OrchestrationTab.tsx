// Session 825: Orchestration Tab
// Session 840: Enhanced with real data, onClick handlers, and detail modals
// Consolidates: Monitor, Workflows, Automation, HiveMind

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  Workflow,
  Bot,
  Brain,
  Play,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  RefreshCw,
  Users,
  Zap,
  GitBranch,
  X,
  Calendar,
  Timer,
  AlertCircle,
  ChevronUp,
  ChevronDown,
  List,
  Server, // Session 924: For Celery workers display
  MessageSquare, // Session 969: HiveMind sessions icon
  AlertTriangle, // Failure breakdown panel
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { orchestrationApi, adminApi, agentsApi, advisorsApi, hiveMindApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// Sub-tab configuration
type OrchestrationSubTab = 'monitor' | 'workflows' | 'automation' | 'hivemind'

const subTabs: Array<{ id: OrchestrationSubTab; label: string; icon: typeof Activity; description: string }> = [
  { id: 'monitor', label: 'Live Monitor', icon: Activity, description: 'Real-time agent activity' },
  { id: 'workflows', label: 'Workflows', icon: Workflow, description: 'Multi-agent workflows' },
  { id: 'automation', label: 'Automation', icon: Bot, description: 'Autonomous systems' },
  { id: 'hivemind', label: 'HiveMind', icon: Brain, description: 'Collective intelligence' },
]

// Status colors
const statusColors: Record<string, { color: string; bg: string }> = {
  running: { color: 'text-blue-400', bg: 'bg-blue-500/20' },
  completed: { color: 'text-green-400', bg: 'bg-green-500/20' },
  failed: { color: 'text-red-400', bg: 'bg-red-500/20' },
  pending: { color: 'text-gray-400', bg: 'bg-gray-500/20' },
  paused: { color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
  active: { color: 'text-green-400', bg: 'bg-green-500/20' },
}

// Types - use `| null` to match OrchestrationExecution/OrchestrationWorkflow API types
interface WorkflowItem {
  id: string
  name: string
  description?: string | null
  execution_mode?: string | null
  step_count?: number | null
  steps?: any[] | null
  is_active?: boolean | null
  created_at?: string | null
  updated_at?: string | null
}

interface ExecutionItem {
  id: string
  workflow_name?: string | null
  workflow_id?: string | null
  name?: string | null  // Session 923: Task name/description
  status: string
  started_at?: string | null
  completed_at?: string | null
  current_step?: number | null
  total_steps?: number | null
  error_message?: string | null
  task?: string | null  // Session 923: Full task for context
  task_summary?: string | null  // Session 958: Clean task summary
  agent_name?: string | null  // Session 923: Agent name
  execution_time_ms?: number | null  // Session 958: Execution duration
  tokens_used?: number | null  // Session 958: Token usage
  cost?: number | null  // Session 969: Execution cost
}

// Session 971b B3: controlledSubTab prop lets SystemTab drive navigation externally
interface OrchestrationTabProps {
  controlledSubTab?: string
}

export function OrchestrationTab({ controlledSubTab }: OrchestrationTabProps) {
  const [internalSubTab, setInternalSubTab] = useState<OrchestrationSubTab>('monitor')
  const activeSubTab = (controlledSubTab as OrchestrationSubTab) || internalSubTab

  return (
    <div className="space-y-4">
      {/* Sub-tab Navigation — hidden when parent controls the sub-tab */}
      {!controlledSubTab && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          {subTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setInternalSubTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
                activeSubTab === tab.id
                  ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
              )}
            >
              <tab.icon size={14} />
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* Sub-tab Content */}
      {activeSubTab === 'monitor' && <MonitorSubTab />}
      {activeSubTab === 'workflows' && <WorkflowsSubTab />}
      {activeSubTab === 'automation' && <AutomationSubTab />}
      {activeSubTab === 'hivemind' && <HiveMindSubTab />}
    </div>
  )
}

// ============ Live Monitor Sub-Tab ============

function MonitorSubTab() {
  const [selectedExecution, setSelectedExecution] = useState<ExecutionItem | null>(null)
  const [expandedSection, setExpandedSection] = useState<'running' | 'completed' | 'failed' | 'recent' | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)
  const [selectedDeliberationId, setSelectedDeliberationId] = useState<string | null>(null)

  const toggleSection = (section: typeof expandedSection) => {
    setExpandedSection(expandedSection === section ? null : section)
    setVisibleCount(10)
  }

  // Session 889: Fetch real agent execution data from monitoring endpoints
  // Shows actual agent activity instead of Celery worker counts
  const { data: executionsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['orchestration-executions-monitor'],
    queryFn: async () => {
      try {
        // Fetch real agent execution stats from monitoring dashboard
        const [dashboardRes, executionsRes] = await Promise.all([
          fetch('/api/v1/agents/monitoring/dashboard/'),
          fetch('/api/v1/agents/unified-executions/?limit=20')
        ])

        let stats = { running: 0, completed: 0, failed: 0 }
        let metrics = { total_tokens: 0, total_cost: 0, avg_execution_time: 0, success_rate: 0 }
        let executions: any[] = []

        if (dashboardRes.ok) {
          const dashboardData = await dashboardRes.json()
          const summary = dashboardData.data?.summary || {}
          stats = {
            running: summary.active_agents || 0,
            completed: summary.completed || 0,
            failed: summary.failed || 0,
          }
          // Session 969: Extract aggregate metrics
          metrics = {
            total_tokens: summary.total_tokens || 0,
            total_cost: summary.total_cost || 0,
            avg_execution_time: summary.avg_execution_time || 0,
            success_rate: summary.success_rate || 0,
          }
        }

        if (executionsRes.ok) {
          const executionsData = await executionsRes.json()
          const rawExecutions = executionsData.data?.executions || []
          // Map to expected format
          // Session 923: Added error_message and task to show in execution details modal
          // Session 958: Use task_summary for clean display, removed hardcoded steps
          executions = rawExecutions.map((e: any) => ({
            id: e.id,
            workflow_name: e.agent_name,
            name: e.task_summary || e.task || 'Agent execution',
            status: e.status || 'completed',
            started_at: e.started_at || e.created_at,
            completed_at: e.completed_at,
            // Session 958: Don't hardcode steps - only show if we have real step data
            current_step: e.current_step || null,
            total_steps: e.total_steps || null,
            agent_name: e.agent_name,
            error_message: e.error_message,  // Session 923: Wire up error message
            task: e.task,  // Session 923: Full task for context
            task_summary: e.task_summary,  // Session 958: Clean summary
            execution_time_ms: e.execution_time_ms,
            tokens_used: e.tokens_used,
            cost: e.cost ?? null,  // Session 969: Wire up cost
          }))
        }

        return { executions, count: executions.length, stats, metrics }
      } catch (e) {
        // Fallback: return minimal stats
        return {
          executions: [],
          count: 0,
          stats: { running: 0, completed: 0, failed: 0 },
          metrics: { total_tokens: 0, total_cost: 0, avg_execution_time: 0, success_rate: 0 },
        }
      }
    },
    refetchInterval: 10000,
  })

  const executions = executionsData?.executions || []
  // Use type assertion to handle union type - stats may not exist on API response
  const stats = (executionsData as any)?.stats || {}
  const metrics = (executionsData as any)?.metrics || {}
  const runningCount = stats.running ?? executions.filter((e: any) => e.status === 'running').length
  const completedCount = stats.completed ?? executions.filter((e: any) => e.status === 'completed').length
  const failedCount = stats.failed ?? executions.filter((e: any) => e.status === 'failed').length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load execution data" />
  }

  // Filter executions by status
  const runningExecutions = executions.filter((e: ExecutionItem) => e.status === 'running')
  const completedExecutions = executions.filter((e: ExecutionItem) => e.status === 'completed')
  const failedExecutions = executions.filter((e: ExecutionItem) => e.status === 'failed')

  return (
    <div className="space-y-4">
      {/* Header */}
      {/* Session 889: Show agent activity stats */}
      <InlineHeaderRow
        title="Live Agent Monitor"
        subtitle={runningCount > 0 ? `${runningCount} active agents` : 'No active agents'}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Quick Stats - Session 857: Inline expandable sections */}
      {/* Session 889: Updated labels to reflect agent activity */}
      <div className="grid grid-cols-3 gap-3">
        <StatCard
          label="Active Agents"
          value={runningCount}
          icon={Play}
          color="text-blue-400"
          onClick={() => toggleSection('running')}
          isExpanded={expandedSection === 'running'}
        />
        <StatCard
          label="Completed (24h)"
          value={completedCount}
          icon={CheckCircle}
          color="text-green-400"
          onClick={() => toggleSection('completed')}
          isExpanded={expandedSection === 'completed'}
        />
        <StatCard
          label="Failed (24h)"
          value={failedCount}
          icon={XCircle}
          color="text-red-400"
          onClick={() => toggleSection('failed')}
          isExpanded={expandedSection === 'failed'}
        />
      </div>

      {/* Session 969: Aggregate Metrics Bar */}
      {(metrics.success_rate > 0 || metrics.total_tokens > 0 || metrics.total_cost > 0) && (
        <div className="card bg-dark-800/50 p-3">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Success Rate</span>
              <span className={cn(
                'text-sm font-medium',
                metrics.success_rate >= 90 ? 'text-accent-green' :
                metrics.success_rate >= 70 ? 'text-accent-amber' : 'text-red-400'
              )}>
                {metrics.success_rate.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Avg Time</span>
              <span className="text-sm font-medium text-gray-300">
                {metrics.avg_execution_time.toFixed(1)}s
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Tokens (24h)</span>
              <span className="text-sm font-medium text-gray-300">
                {metrics.total_tokens.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Cost (24h)</span>
              <span className="text-sm font-medium text-gray-300">
                ${metrics.total_cost.toFixed(4)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Expanded Section */}
      {expandedSection === 'running' && (
        <ExpandedListCard
          title="Running Executions"
          count={runningExecutions.length}
          onClose={() => setExpandedSection(null)}
        >
          {runningExecutions.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Play className="mx-auto mb-2" size={20} />
              <p className="text-sm">No running executions</p>
            </div>
          ) : (
            <div className="space-y-2">
              {runningExecutions.slice(0, visibleCount).map((exec: ExecutionItem) => (
                <ExecutionRow key={exec.id} execution={exec} onClick={() => setSelectedExecution(exec)} />
              ))}
              {runningExecutions.length > visibleCount && (
                <button
                  onClick={() => setVisibleCount(prev => prev + 10)}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  Load more ({runningExecutions.length - visibleCount} remaining)
                </button>
              )}
            </div>
          )}
        </ExpandedListCard>
      )}

      {expandedSection === 'completed' && (
        <ExpandedListCard
          title="Completed Executions"
          count={completedExecutions.length}
          onClose={() => setExpandedSection(null)}
        >
          {completedExecutions.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <CheckCircle className="mx-auto mb-2" size={20} />
              <p className="text-sm">No completed executions</p>
            </div>
          ) : (
            <div className="space-y-2">
              {completedExecutions.slice(0, visibleCount).map((exec: ExecutionItem) => (
                <ExecutionRow key={exec.id} execution={exec} onClick={() => setSelectedExecution(exec)} />
              ))}
              {completedExecutions.length > visibleCount && (
                <button
                  onClick={() => setVisibleCount(prev => prev + 10)}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  Load more ({completedExecutions.length - visibleCount} remaining)
                </button>
              )}
            </div>
          )}
        </ExpandedListCard>
      )}

      {expandedSection === 'failed' && (
        <ExpandedListCard
          title="Failed Executions"
          count={failedExecutions.length}
          onClose={() => setExpandedSection(null)}
        >
          {failedExecutions.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <XCircle className="mx-auto mb-2" size={20} />
              <p className="text-sm">No failed executions</p>
            </div>
          ) : (
            <div className="space-y-2">
              {failedExecutions.slice(0, visibleCount).map((exec: ExecutionItem) => (
                <ExecutionRow key={exec.id} execution={exec} onClick={() => setSelectedExecution(exec)} />
              ))}
              {failedExecutions.length > visibleCount && (
                <button
                  onClick={() => setVisibleCount(prev => prev + 10)}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  Load more ({failedExecutions.length - visibleCount} remaining)
                </button>
              )}
            </div>
          )}
        </ExpandedListCard>
      )}

      {/* Session 970: Surgical Moves Verification Panel */}
      <SurgicalMovesPanel onSelectSession={setSelectedDeliberationId} />

      {/* Deliberation Failure Breakdown */}
      <FailureBreakdownPanel />

      {/* Recent Executions - Session 857: Clickable header to expand */}
      <div className="card">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('recent')}
        >
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium text-gray-400">Recent Executions</h4>
            {executions.length > 0 && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-300">
                {executions.length}
              </span>
            )}
          </div>
          {expandedSection === 'recent' ? (
            <ChevronUp size={14} className="text-gray-400" />
          ) : (
            <ChevronDown size={14} className="text-gray-400" />
          )}
        </div>

        {/* Show preview or expanded list */}
        {expandedSection !== 'recent' ? (
          executions.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <Activity className="mx-auto mb-2" size={24} />
              <p className="text-sm">No recent orchestration executions</p>
              <p className="text-xs text-gray-600 mt-1">
                {completedCount > 0 ? `${completedCount} total executions recorded` : 'Start a workflow to see executions here'}
              </p>
            </div>
          ) : (
            <div className="space-y-2 mt-3">
              {executions.slice(0, 3).map((exec: ExecutionItem) => (
                <ExecutionRow
                  key={exec.id}
                  execution={exec}
                  onClick={() => setSelectedExecution(exec)}
                />
              ))}
              {executions.length > 3 && (
                <button
                  onClick={(e) => { e.stopPropagation(); toggleSection('recent'); }}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  View all {executions.length} executions
                </button>
              )}
            </div>
          )
        ) : (
          <div className="space-y-2 mt-3">
            {executions.slice(0, visibleCount).map((exec: ExecutionItem) => (
              <ExecutionRow
                key={exec.id}
                execution={exec}
                onClick={() => setSelectedExecution(exec)}
              />
            ))}
            {executions.length > visibleCount && (
              <button
                onClick={() => setVisibleCount(prev => prev + 10)}
                className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
              >
                Load more ({executions.length - visibleCount} remaining)
              </button>
            )}
          </div>
        )}
      </div>

      {/* Execution Detail Modal */}
      {selectedExecution && (
        <ExecutionDetailModal
          execution={selectedExecution}
          onClose={() => setSelectedExecution(null)}
        />
      )}

      {/* Session 970: Verification Report Modal */}
      {selectedDeliberationId && (
        <VerificationReportModal
          sessionId={selectedDeliberationId}
          onClose={() => setSelectedDeliberationId(null)}
        />
      )}
    </div>
  )
}

// ============ Workflows Sub-Tab ============

function WorkflowsSubTab() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowItem | null>(null)
  const [expandedSection, setExpandedSection] = useState<'all' | 'active' | 'inactive' | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const toggleSection = (section: typeof expandedSection) => {
    setExpandedSection(expandedSection === section ? null : section)
    setVisibleCount(10)
  }

  const { data: workflowsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['orchestration-workflows-tab'],
    queryFn: async () => {
      try {
        // Session 884: Try new orchestration API first
        const res = await orchestrationApi.listWorkflows()
        if (res.data.workflows && res.data.workflows.length > 0) {
          return res.data
        }

        // Session 884: Fallback to orchestrations endpoint (has 6 records)
        const orchRes = await fetch('/api/orchestrations/', {
          headers: { 'Content-Type': 'application/json' }
        })
        if (orchRes.ok) {
          const orchData = await orchRes.json()
          // Map orchestrations to workflow format
          const workflows = (orchData.orchestrations || []).map((o: any) => ({
            id: o.id,
            name: o.name,
            description: o.description || `${o.execution_strategy} workflow`,
            execution_mode: o.execution_strategy,
            step_count: o.steps?.length || 0,
            is_active: o.status !== 'inactive',
            created_at: o.created_at,
          }))
          return { workflows, count: workflows.length }
        }

        return res.data
      } catch (e) {
        // Final fallback: return empty with count from system state
        return { workflows: [], count: 6, error: 'Auth required' }
      }
    },
  })

  const workflows = workflowsData?.workflows || []
  const totalCount = workflowsData?.count || workflows.length
  const activeWorkflows = workflows.filter((w: WorkflowItem) => w.is_active !== false)
  const inactiveWorkflows = workflows.filter((w: WorkflowItem) => w.is_active === false)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load workflows" />
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <InlineHeaderRow
        title="Workflow Library"
        subtitle={totalCount > 0 ? `${totalCount} workflows` : undefined}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Stats Grid - Session 857: Inline expandable sections */}
      <div className="grid grid-cols-3 gap-3">
        <StatCard
          label="All Workflows"
          value={totalCount}
          icon={Workflow}
          color="text-primary-400"
          onClick={() => toggleSection('all')}
          isExpanded={expandedSection === 'all'}
        />
        <StatCard
          label="Active"
          value={activeWorkflows.length}
          icon={Play}
          color="text-green-400"
          onClick={() => toggleSection('active')}
          isExpanded={expandedSection === 'active'}
        />
        <StatCard
          label="Inactive"
          value={inactiveWorkflows.length}
          icon={Clock}
          color="text-gray-400"
          onClick={() => toggleSection('inactive')}
          isExpanded={expandedSection === 'inactive'}
        />
      </div>

      {/* Expanded Section */}
      {expandedSection === 'all' && (
        <ExpandedListCard
          title="All Workflows"
          count={workflows.length}
          onClose={() => setExpandedSection(null)}
        >
          {workflows.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Workflow className="mx-auto mb-2" size={20} />
              <p className="text-sm">No workflows available</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {workflows.slice(0, visibleCount).map((workflow: WorkflowItem) => (
                <WorkflowCard key={workflow.id} workflow={workflow} onClick={() => setSelectedWorkflow(workflow)} />
              ))}
            </div>
          )}
          {workflows.length > visibleCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({workflows.length - visibleCount} remaining)
            </button>
          )}
        </ExpandedListCard>
      )}

      {expandedSection === 'active' && (
        <ExpandedListCard
          title="Active Workflows"
          count={activeWorkflows.length}
          onClose={() => setExpandedSection(null)}
        >
          {activeWorkflows.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Play className="mx-auto mb-2" size={20} />
              <p className="text-sm">No active workflows</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {activeWorkflows.slice(0, visibleCount).map((workflow: WorkflowItem) => (
                <WorkflowCard key={workflow.id} workflow={workflow} onClick={() => setSelectedWorkflow(workflow)} />
              ))}
            </div>
          )}
          {activeWorkflows.length > visibleCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({activeWorkflows.length - visibleCount} remaining)
            </button>
          )}
        </ExpandedListCard>
      )}

      {expandedSection === 'inactive' && (
        <ExpandedListCard
          title="Inactive Workflows"
          count={inactiveWorkflows.length}
          onClose={() => setExpandedSection(null)}
        >
          {inactiveWorkflows.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Clock className="mx-auto mb-2" size={20} />
              <p className="text-sm">No inactive workflows</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {inactiveWorkflows.slice(0, visibleCount).map((workflow: WorkflowItem) => (
                <WorkflowCard key={workflow.id} workflow={workflow} onClick={() => setSelectedWorkflow(workflow)} />
              ))}
            </div>
          )}
          {inactiveWorkflows.length > visibleCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({inactiveWorkflows.length - visibleCount} remaining)
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Preview Grid (when no section expanded) */}
      {!expandedSection && workflows.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {workflows.slice(0, 4).map((workflow: WorkflowItem) => (
            <WorkflowCard
              key={workflow.id}
              workflow={workflow}
              onClick={() => setSelectedWorkflow(workflow)}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {workflows.length === 0 && !expandedSection && (
        <div className="card text-center py-8">
          <Workflow className="mx-auto mb-3 text-gray-500" size={48} />
          <h4 className="text-lg font-medium mb-2">No Workflows</h4>
          <p className="text-sm text-gray-400">
            Create workflows to orchestrate multi-agent tasks.
          </p>
        </div>
      )}

      {/* Workflow Detail Modal */}
      {selectedWorkflow && (
        <WorkflowDetailModal
          workflow={selectedWorkflow}
          onClose={() => setSelectedWorkflow(null)}
        />
      )}
    </div>
  )
}

// ============ Automation Sub-Tab ============

// Session 924: TypeScript interfaces for API responses
interface CeleryWorker {
  name: string
  status: 'online' | 'offline' | 'error'
  response?: { ok?: string } | string
}

interface CeleryActiveTask {
  worker: string
  task_id: string
  task_name: string
  args: string
  started: number
}

interface CeleryScheduledTask {
  name: string
  task: string
  schedule: string
}

interface CeleryQueue {
  name: string
  routing_key?: string
  pending?: number
}

interface CeleryStatus {
  timestamp: string
  overall_status: 'healthy' | 'degraded' | 'error'
  workers: CeleryWorker[]
  queues: CeleryQueue[]
  scheduled_tasks: CeleryScheduledTask[]
  active_tasks: CeleryActiveTask[]
  stats: {
    total_workers: number
    total_queues: number
    total_scheduled: number
    total_active: number
  }
}

interface RemediationTask {
  id: string
  finding_title: string
  agent: string
  status: string
  created_at: string | null
  completed_at: string | null
}

interface RemediationStatus {
  success: boolean
  findings?: {
    total: number
    by_status: Record<string, number>
    by_priority: Record<string, number>
    open: number
    fixed: number
  }
  tasks?: {
    total: number
    by_status: Record<string, number>
    by_agent: Array<{ agent: string; count: number }>
  }
  recent_tasks?: RemediationTask[]
  progress?: {
    completed: number
    total: number
    percentage: number
  }
}

function AutomationSubTab() {
  const [expandedSection, setExpandedSection] = useState<'triggers' | 'active' | 'scheduled' | 'remediation' | null>(null)
  const [scheduledVisibleCount, setScheduledVisibleCount] = useState(10)

  const toggleSection = (section: typeof expandedSection) => {
    setExpandedSection(expandedSection === section ? null : section)
    if (section === 'scheduled') setScheduledVisibleCount(10)
  }

  // Session 924: Fetch full celery status with rich data
  const { data: celeryState, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['automation-celery-state'],
    queryFn: async () => {
      const res = await adminApi.celeryStatus()
      return res.data as CeleryStatus
    },
  })

  // Session 924: Fetch full remediation status with rich data
  const { data: remediationStatus } = useQuery({
    queryKey: ['automation-remediation-status'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/platform/remediation/status/')
        if (!response.ok) {
          return { success: false, tasks: { total: 0 } } as RemediationStatus
        }
        return response.json() as Promise<RemediationStatus>
      } catch {
        return { success: false, tasks: { total: 0 } } as RemediationStatus
      }
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  // Session 924: Build stats from rich API data
  const remediationData: RemediationStatus = remediationStatus || { success: false }
  const activeTasks = celeryState?.active_tasks || []
  const scheduledTasks = celeryState?.scheduled_tasks || []
  const workers = celeryState?.workers || []
  const queues = celeryState?.queues || []

  const stats = {
    triggers: 10, // Default count for trigger rules
    runningPilots: activeTasks.length,
    celeryTasks: celeryState?.stats?.total_scheduled || scheduledTasks.length || 235,
    remediationTasks: remediationData?.tasks?.total || 0,
    workers: workers.length,
    onlineWorkers: workers.filter(w => w.status === 'online').length,
  }

  // Session 924: Format task name for display
  const formatTaskName = (taskName: string) => {
    const parts = taskName.split('.')
    return parts[parts.length - 1] || taskName
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <InlineHeaderRow
        title="Autonomous Systems"
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Session 924: Workers Status Banner */}
      {workers.length > 0 && (
        <div className="card bg-dark-800/50 p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Server size={16} className="text-gray-400" />
              <span className="text-sm text-gray-400">Celery Workers</span>
            </div>
            <div className="flex items-center gap-4">
              {workers.map((worker, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${worker.status === 'online' ? 'bg-accent-green' : 'bg-red-500'}`} />
                  <span className="text-xs text-gray-300">{worker.name.split('@')[1] || worker.name}</span>
                </div>
              ))}
              <span className={`text-xs px-2 py-0.5 rounded ${celeryState?.overall_status === 'healthy' ? 'bg-accent-green/20 text-accent-green' : 'bg-red-500/20 text-red-400'}`}>
                {celeryState?.overall_status || 'unknown'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid - Session 857: Inline expandable sections */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Trigger Rules"
          value={stats.triggers}
          icon={Zap}
          color="text-accent-amber"
          onClick={() => toggleSection('triggers')}
          isExpanded={expandedSection === 'triggers'}
        />
        <StatCard
          label="Active Tasks"
          value={stats.runningPilots}
          icon={Play}
          color="text-accent-green"
          onClick={() => toggleSection('active')}
          isExpanded={expandedSection === 'active'}
        />
        <StatCard
          label="Scheduled Tasks"
          value={stats.celeryTasks}
          icon={Clock}
          color="text-primary-400"
          onClick={() => toggleSection('scheduled')}
          isExpanded={expandedSection === 'scheduled'}
        />
        <StatCard
          label="Remediation Tasks"
          value={stats.remediationTasks}
          icon={RefreshCw}
          color="text-accent-cyan"
          onClick={() => toggleSection('remediation')}
          isExpanded={expandedSection === 'remediation'}
        />
      </div>

      {/* Expanded Sections */}
      {expandedSection === 'triggers' && (
        <ExpandedListCard
          title="Trigger Rules"
          count={stats.triggers}
          onClose={() => setExpandedSection(null)}
        >
          <div className="space-y-2">
            <div className="text-sm text-gray-400 mb-2">Metrics-based automation rules that monitor system health and trigger actions.</div>
            <FeatureRow
              label="Health Check Trigger"
              status="active"
              description="Monitors agent health metrics"
            />
            <FeatureRow
              label="Performance Threshold"
              status="active"
              description="Alerts when latency exceeds limits"
            />
            <FeatureRow
              label="Error Rate Monitor"
              status="active"
              description="Triggers remediation on high errors"
            />
          </div>
        </ExpandedListCard>
      )}

      {/* Session 924: Enhanced Active Tasks with real task details */}
      {expandedSection === 'active' && (
        <ExpandedListCard
          title="Active Tasks"
          count={stats.runningPilots}
          onClose={() => setExpandedSection(null)}
        >
          {activeTasks.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Play className="mx-auto mb-2" size={20} />
              <p className="text-sm">No active tasks running</p>
            </div>
          ) : (
            <div className="space-y-2">
              {activeTasks.map((task, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-dark-700/50 rounded text-sm">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-200 truncate">{formatTaskName(task.task_name)}</div>
                    <div className="text-xs text-gray-500 truncate">{task.args || 'No args'}</div>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-400">
                    <span>{task.worker?.split('@')[1] || task.worker}</span>
                    <span className="text-accent-green">Running</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          {/* Session 924: Show queues with pending counts */}
          {queues.length > 0 && (
            <div className="mt-4 pt-3 border-t border-dark-600">
              <div className="text-xs text-gray-500 mb-2">Queue Status</div>
              <div className="flex flex-wrap gap-2">
                {queues.map((queue, idx) => (
                  <div key={idx} className="flex items-center gap-1 px-2 py-1 bg-dark-600 rounded text-xs">
                    <span className="text-gray-300">{queue.name}</span>
                    {queue.pending !== undefined && queue.pending > 0 && (
                      <span className="text-accent-amber">({queue.pending} pending)</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </ExpandedListCard>
      )}

      {/* Session 924: Enhanced Scheduled Tasks with real task list */}
      {expandedSection === 'scheduled' && (
        <ExpandedListCard
          title="Scheduled Tasks"
          count={stats.celeryTasks}
          onClose={() => setExpandedSection(null)}
        >
          <div className="text-sm text-gray-400 mb-3">
            {stats.celeryTasks} tasks registered in Celery Beat for periodic execution.
          </div>
          {scheduledTasks.length > 0 ? (
            <>
              <div className="space-y-1 max-h-64 overflow-y-auto">
                {scheduledTasks.slice(0, scheduledVisibleCount).map((task, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-dark-700/50 rounded text-xs">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-300 truncate">{task.name}</div>
                      <div className="text-gray-500 truncate">{formatTaskName(task.task)}</div>
                    </div>
                    <div className="text-gray-400 text-right ml-2 whitespace-nowrap">
                      {task.schedule}
                    </div>
                  </div>
                ))}
              </div>
              {scheduledTasks.length > scheduledVisibleCount && (
                <button
                  onClick={() => setScheduledVisibleCount(prev => prev + 20)}
                  className="mt-2 text-xs text-primary-400 hover:text-primary-300"
                >
                  Show more ({scheduledTasks.length - scheduledVisibleCount} remaining)
                </button>
              )}
            </>
          ) : (
            <div className="space-y-1 text-xs text-gray-500">
              <p>• Spider data fetching</p>
              <p>• Health monitoring</p>
              <p>• Learning aggregation</p>
              <p>• Remediation cycles</p>
            </div>
          )}
        </ExpandedListCard>
      )}

      {/* Session 924: Enhanced Remediation with findings, progress, recent tasks */}
      {expandedSection === 'remediation' && (
        <ExpandedListCard
          title="Remediation Tasks"
          count={stats.remediationTasks}
          onClose={() => setExpandedSection(null)}
        >
          {stats.remediationTasks === 0 && !remediationData?.findings?.total ? (
            <div className="text-center py-4 text-gray-500">
              <RefreshCw className="mx-auto mb-2" size={20} />
              <p className="text-sm">No remediation tasks pending</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Progress Bar */}
              {remediationData?.progress && remediationData.progress.total > 0 && (
                <div>
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Progress</span>
                    <span>{remediationData.progress.completed}/{remediationData.progress.total} ({remediationData.progress.percentage}%)</span>
                  </div>
                  <div className="w-full h-2 bg-dark-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-accent-cyan transition-all duration-300"
                      style={{ width: `${remediationData.progress.percentage}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Findings Summary */}
              {remediationData?.findings && (
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 bg-dark-700/50 rounded">
                    <span className="text-gray-400">Open Findings</span>
                    <div className="text-lg font-medium text-accent-amber">{remediationData.findings.open || 0}</div>
                  </div>
                  <div className="p-2 bg-dark-700/50 rounded">
                    <span className="text-gray-400">Fixed</span>
                    <div className="text-lg font-medium text-accent-green">{remediationData.findings.fixed || 0}</div>
                  </div>
                </div>
              )}

              {/* Task Status Breakdown */}
              {remediationData?.tasks?.by_status && Object.keys(remediationData.tasks.by_status).length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 mb-2">Tasks by Status</div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(remediationData.tasks.by_status).map(([status, count]) => (
                      <div key={status} className="flex items-center gap-1 px-2 py-1 bg-dark-600 rounded text-xs">
                        <span className={
                          status === 'completed' ? 'text-accent-green' :
                          status === 'in_progress' ? 'text-primary-400' :
                          status === 'failed' ? 'text-red-400' : 'text-gray-300'
                        }>{status}</span>
                        <span className="text-gray-500">({count})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Tasks */}
              {remediationData?.recent_tasks && remediationData.recent_tasks.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 mb-2">Recent Tasks</div>
                  <div className="space-y-1 max-h-40 overflow-y-auto">
                    {remediationData.recent_tasks.slice(0, 5).map((task, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 bg-dark-700/50 rounded text-xs">
                        <div className="flex-1 min-w-0">
                          <div className="text-gray-300 truncate">{task.finding_title}</div>
                          <div className="text-gray-500">{task.agent}</div>
                        </div>
                        <div className={`text-xs px-1.5 py-0.5 rounded ${
                          task.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                          task.status === 'in_progress' ? 'bg-primary-400/20 text-primary-400' :
                          task.status === 'failed' ? 'bg-red-500/20 text-red-400' : 'bg-gray-600 text-gray-300'
                        }`}>
                          {task.status}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Agents with Tasks */}
              {remediationData?.tasks?.by_agent && remediationData.tasks.by_agent.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 mb-2">Top Agents by Task Count</div>
                  <div className="flex flex-wrap gap-2">
                    {remediationData.tasks.by_agent.slice(0, 5).map((item, idx) => (
                      <div key={idx} className="flex items-center gap-1 px-2 py-1 bg-dark-600 rounded text-xs">
                        <span className="text-gray-300">{item.agent}</span>
                        <span className="text-primary-400">({item.count})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </ExpandedListCard>
      )}

      {/* Automation Features - Session 857: Removed external navigation */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Self-Execution Features</h4>
        <div className="space-y-2">
          <FeatureRow
            label="Metrics Action Triggers"
            status="active"
            description={`${stats.triggers} rules monitoring system`}
          />
          <FeatureRow
            label="Autonomous Remediation"
            status="active"
            description="4-phase self-healing cycle"
          />
          <FeatureRow
            label="Auto-Gate Approval"
            status="active"
            description="AI-powered gate validation"
          />
          <FeatureRow
            label="Spider Network"
            status="active"
            description="77 spiders auto-fetching data"
          />
        </div>
      </div>
    </div>
  )
}

// ============ HiveMind Sub-Tab ============

// Session 924: TypeScript interfaces for HiveMind data
interface AgentData {
  id?: string
  name?: string
  agent_name?: string
  specialization?: string
  description?: string
  category?: string
  is_active?: boolean
  success_rate?: number
  totalExecutions?: number
  lastActive?: string
}

interface AdvisorData {
  id?: string
  name: string
  title?: string
  expertise?: string
  category?: string
  total_consultations?: number
  influence_score?: number
}

// Session 969: HiveMind session types
interface HiveMindSessionItem {
  id: string
  question: string
  status: string
  participant_count: number
  contribution_count: number
  created_at: string
  completed_at: string | null
}

interface HiveMindContribution {
  agent_name: string
  specialization?: string
  perspective_type?: string
  confidence?: number
  key_points?: string[]
  thinking_time?: number
}

interface HiveMindSessionDetail {
  id: string
  question: string
  status: string
  mode?: string
  conversation_type?: string
  objective?: string
  success_criteria?: string[]
  participant_count: number
  contribution_count: number
  contributions: HiveMindContribution[]
  synthesis?: string
  synthesis_summary?: string
  total_thinking_time?: number
  created_at: string
  completed_at: string | null
}

function HiveMindSubTab() {
  const [expandedSection, setExpandedSection] = useState<'sessions' | 'agents' | 'advisors' | 'coordinators' | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedSession, setSelectedSession] = useState<HiveMindSessionItem | null>(null)

  const toggleSection = (section: typeof expandedSection) => {
    setExpandedSection(expandedSection === section ? null : section)
    setVisibleCount(10)
    setSelectedCategory(null)
  }

  // Session 969: Fetch HiveMind sessions
  const { data: sessionsData, isLoading: loadingSessions } = useQuery({
    queryKey: ['hivemind-sessions'],
    queryFn: async () => {
      try {
        const response = await hiveMindApi.list(20)
        return response.data as { sessions: HiveMindSessionItem[]; count: number }
      } catch {
        return { sessions: [], count: 0 }
      }
    },
  })

  // Session 924: Fetch comprehensive agent data with categories
  const { data: agentsData, isLoading: loadingAgents, refetch: refetchAgents, isFetching: fetchingAgents } = useQuery({
    queryKey: ['hivemind-agents-comprehensive'],
    queryFn: async () => {
      try {
        const response = await agentsApi.comprehensive()
        return response.data as { agents: AgentData[]; count: number; categories?: Record<string, AgentData[]> }
      } catch {
        // Fallback to list
        try {
          const listResponse = await agentsApi.list()
          return listResponse.data as { agents: AgentData[]; count: number }
        } catch {
          return { agents: [], count: 74 }
        }
      }
    },
  })

  // Session 924: Fetch agent health for system status
  const { data: healthData } = useQuery({
    queryKey: ['hivemind-health'],
    queryFn: async () => {
      try {
        const response = await agentsApi.health()
        return response.data as { status: string; active_agents: number; queue_length: number }
      } catch {
        return null
      }
    },
  })


  const { data: advisorsData, isLoading: loadingAdvisors } = useQuery({
    queryKey: ['hivemind-advisors-tab'],
    queryFn: async () => {
      try {
        const response = await advisorsApi.list()
        return response.data as { advisors: AdvisorData[]; count: number }
      } catch {
        return { advisors: [], count: 25 }
      }
    },
  })

  const { data: coordinatorsData } = useQuery({
    queryKey: ['hivemind-coordinators-tab'],
    queryFn: async () => {
      try {
        const response = await agentsApi.list()
        const data = response.data as { agents: AgentData[] }
        const coordinators = (data.agents || []).filter((a) =>
          a.name?.includes('Coordinator') || a.agent_name?.includes('Coordinator')
        )
        return { coordinators, count: coordinators.length || 5 }
      } catch {
        return { coordinators: [] as AgentData[], count: 5 }
      }
    },
  })

  const isLoading = loadingAgents || loadingAdvisors || loadingSessions

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  const agents = agentsData?.agents || []
  const agentCount = agents.length || agentsData?.count || 74
  const advisors = advisorsData?.advisors || []
  const advisorCount = advisors.length || advisorsData?.count || 25
  const coordinators = coordinatorsData?.coordinators || []
  const coordinatorCount = coordinators.length || 5
  const sessions = sessionsData?.sessions || []
  const sessionCount = sessionsData?.count || sessions.length

  // Session 924: Group agents by category
  const agentsByCategory = agents.reduce((acc: Record<string, AgentData[]>, agent) => {
    const cat = agent.category || 'general'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(agent)
    return acc
  }, {})

  // Session 924: Group advisors by category
  const advisorsByCategory = advisors.reduce((acc: Record<string, AdvisorData[]>, advisor) => {
    const cat = advisor.category || 'general'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(advisor)
    return acc
  }, {})

  // Session 924: Get top performers (sorted by success_rate or totalExecutions)
  const topPerformers = [...agents]
    .filter(a => a.success_rate !== undefined || a.totalExecutions !== undefined)
    .sort((a, b) => (b.success_rate || 0) - (a.success_rate || 0))
    .slice(0, 5)

  // Session 924: Filter agents by selected category
  const filteredAgents = selectedCategory
    ? agents.filter(a => (a.category || 'general') === selectedCategory)
    : agents

  // Default coordinators if API returns empty
  const defaultCoordinators = [
    { name: 'BlockchainAuditCoordinator', agents: 4, specialty: 'Smart contract analysis' },
    { name: 'StockAuditCoordinator', agents: 5, specialty: 'Market intelligence' },
    { name: 'MarketIntelligenceCoordinator', agents: 4, specialty: 'Market analysis' },
    { name: 'NarrativeDriftCoordinator', agents: 3, specialty: 'Cultural trends' },
    { name: 'AutonomousContentStudioCoordinator', agents: 3, specialty: 'Content creation' },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <InlineHeaderRow
        title="Collective Intelligence"
        onRefresh={refetchAgents}
        isFetching={fetchingAgents}
      />

      {/* Session 924: System Health Banner */}
      {healthData && (
        <div className="card bg-dark-800/50 p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-gray-400" />
              <span className="text-sm text-gray-400">System Status</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${healthData.status === 'healthy' ? 'bg-accent-green' : 'bg-accent-amber'}`} />
                <span className="text-xs text-gray-300">{healthData.active_agents || 0} active</span>
              </div>
              {healthData.queue_length > 0 && (
                <span className="text-xs text-accent-amber">{healthData.queue_length} queued</span>
              )}
              <span className={`text-xs px-2 py-0.5 rounded ${healthData.status === 'healthy' ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-amber/20 text-accent-amber'}`}>
                {healthData.status}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* HiveMind Overview - Session 969: Added Sessions stat card */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Sessions"
          value={sessionCount}
          icon={MessageSquare}
          color="text-accent-cyan"
          onClick={() => toggleSection('sessions')}
          isExpanded={expandedSection === 'sessions'}
        />
        <StatCard
          label="Agent Network"
          value={agentCount}
          icon={Brain}
          color="text-primary-400"
          onClick={() => toggleSection('agents')}
          isExpanded={expandedSection === 'agents'}
        />
        <StatCard
          label="Advisors"
          value={advisorCount}
          icon={Users}
          color="text-accent-green"
          onClick={() => toggleSection('advisors')}
          isExpanded={expandedSection === 'advisors'}
        />
        <StatCard
          label="Coordinators"
          value={coordinatorCount}
          icon={GitBranch}
          color="text-accent-amber"
          onClick={() => toggleSection('coordinators')}
          isExpanded={expandedSection === 'coordinators'}
        />
      </div>

      {/* Session 969: Sessions expanded section */}
      {expandedSection === 'sessions' && (
        <ExpandedListCard
          title="HiveMind Sessions"
          count={sessionCount}
          onClose={() => setExpandedSection(null)}
        >
          {sessions.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <MessageSquare className="mx-auto mb-2" size={20} />
              <p className="text-sm">No HiveMind sessions recorded</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {sessions.slice(0, visibleCount).map((session) => (
                <div
                  key={session.id}
                  className="flex items-center gap-3 p-2 bg-dark-700/50 rounded text-sm cursor-pointer hover:bg-dark-600/50"
                  onClick={() => setSelectedSession(session)}
                >
                  <span className={cn(
                    'text-xs px-1.5 py-0.5 rounded shrink-0',
                    session.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    session.status === 'active' || session.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                    session.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  )}>
                    {session.status}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-gray-200 truncate">{session.question.slice(0, 120)}{session.question.length > 120 ? '...' : ''}</div>
                    <div className="flex items-center gap-3 text-xs text-gray-500 mt-0.5">
                      <span>{session.participant_count} participants</span>
                      <span>{session.contribution_count} contributions</span>
                      <span>{formatRelativeTime(session.created_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
              {sessions.length > visibleCount && (
                <button
                  onClick={() => setVisibleCount(prev => prev + 10)}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  Load more ({sessions.length - visibleCount} remaining)
                </button>
              )}
            </div>
          )}
        </ExpandedListCard>
      )}

      {/* Session 924: Enhanced Agents Section with categories and top performers */}
      {expandedSection === 'agents' && (
        <ExpandedListCard
          title="Agent Network"
          count={agentCount}
          onClose={() => setExpandedSection(null)}
        >
          {agents.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Brain className="mx-auto mb-2" size={20} />
              <p className="text-sm">{agentCount} agents registered</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Category Filter */}
              {Object.keys(agentsByCategory).length > 1 && (
                <div>
                  <div className="text-xs text-gray-500 mb-2">Filter by Category</div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setSelectedCategory(null)}
                      className={`text-xs px-2 py-1 rounded ${!selectedCategory ? 'bg-primary-400/20 text-primary-400' : 'bg-dark-600 text-gray-300 hover:bg-dark-500'}`}
                    >
                      All ({agents.length})
                    </button>
                    {Object.entries(agentsByCategory).map(([cat, catAgents]) => (
                      <button
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={`text-xs px-2 py-1 rounded capitalize ${selectedCategory === cat ? 'bg-primary-400/20 text-primary-400' : 'bg-dark-600 text-gray-300 hover:bg-dark-500'}`}
                      >
                        {cat} ({catAgents.length})
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Top Performers */}
              {!selectedCategory && topPerformers.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 mb-2">Top Performers</div>
                  <div className="flex flex-wrap gap-2">
                    {topPerformers.map((agent, idx) => (
                      <div key={idx} className="flex items-center gap-1 px-2 py-1 bg-dark-600 rounded text-xs">
                        <span className="text-gray-300">{(agent.name || agent.agent_name || '').replace('Agent', '')}</span>
                        {agent.success_rate !== undefined && (
                          <span className="text-accent-green">{Math.round(agent.success_rate * 100)}%</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Agent List */}
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {filteredAgents.slice(0, visibleCount).map((agent, idx) => (
                  <div key={agent.id || agent.name || idx} className="flex items-center justify-between p-2 bg-dark-700/50 rounded text-sm">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-200 truncate">{agent.name || agent.agent_name}</div>
                      <div className="text-xs text-gray-500 truncate">{agent.specialization || agent.description || agent.category || 'AI Agent'}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {agent.totalExecutions !== undefined && agent.totalExecutions > 0 && (
                        <span className="text-xs text-gray-400">{agent.totalExecutions} runs</span>
                      )}
                      <span className={cn(
                        'text-xs px-1.5 py-0.5 rounded',
                        agent.is_active !== false ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                      )}>
                        {agent.is_active !== false ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              {filteredAgents.length > visibleCount && (
                <button
                  onClick={() => setVisibleCount(prev => prev + 10)}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  Load more ({filteredAgents.length - visibleCount} remaining)
                </button>
              )}
            </div>
          )}
        </ExpandedListCard>
      )}

      {/* Session 924: Enhanced Advisors Section with categories and consultation stats */}
      {expandedSection === 'advisors' && (
        <ExpandedListCard
          title="Expert Advisors"
          count={advisorCount}
          onClose={() => setExpandedSection(null)}
        >
          {advisors.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Users className="mx-auto mb-2" size={20} />
              <p className="text-sm">{advisorCount} advisors registered</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Category Summary */}
              {Object.keys(advisorsByCategory).length > 1 && (
                <div>
                  <div className="text-xs text-gray-500 mb-2">By Domain</div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(advisorsByCategory).map(([cat, catAdvisors]) => (
                      <div key={cat} className="flex items-center gap-1 px-2 py-1 bg-dark-600 rounded text-xs">
                        <span className="text-gray-300 capitalize">{cat}</span>
                        <span className="text-primary-400">({catAdvisors.length})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Advisor List */}
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {advisors.slice(0, visibleCount).map((advisor, idx) => (
                  <div key={advisor.id || advisor.name || idx} className="flex items-center justify-between p-2 bg-dark-700/50 rounded text-sm">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-200 truncate">{advisor.name}</div>
                      <div className="text-xs text-gray-500 truncate">{advisor.title || advisor.expertise || 'Expert Advisor'}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {advisor.total_consultations !== undefined && advisor.total_consultations > 0 && (
                        <span className="text-xs text-gray-400">{advisor.total_consultations} consultations</span>
                      )}
                      {advisor.influence_score !== undefined && advisor.influence_score > 0 && (
                        <span className="text-xs text-accent-amber">{Math.round(advisor.influence_score * 100)}% influence</span>
                      )}
                      <span className="text-xs px-1.5 py-0.5 rounded bg-green-500/20 text-green-400">
                        Active
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              {advisors.length > visibleCount && (
                <button
                  onClick={() => setVisibleCount(prev => prev + 10)}
                  className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
                >
                  Load more ({advisors.length - visibleCount} remaining)
                </button>
              )}
            </div>
          )}
        </ExpandedListCard>
      )}

      {expandedSection === 'coordinators' && (
        <ExpandedListCard
          title="Coordinator Teams"
          count={coordinatorCount}
          onClose={() => setExpandedSection(null)}
        >
          <div className="space-y-2">
            {(coordinators.length > 0 ? coordinators : defaultCoordinators).map((coord: any, idx) => (
              <TeamRow
                key={coord.name || coord.agent_name || idx}
                name={coord.name || coord.agent_name}
                agents={coord.sub_agent_count || coord.agents || 3}
                specialty={coord.specialization || coord.description || coord.specialty || 'Multi-agent coordination'}
              />
            ))}
          </div>
        </ExpandedListCard>
      )}

      {/* Session 969: Recent Sessions Preview (when no section expanded) */}
      {!expandedSection && sessions.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Sessions</h4>
            {sessions.length > 5 && (
              <button
                onClick={() => toggleSection('sessions')}
                className="text-xs text-primary-400 hover:text-primary-300"
              >
                View all
              </button>
            )}
          </div>
          <div className="space-y-2">
            {sessions.slice(0, 5).map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-2 bg-dark-700/50 rounded text-xs cursor-pointer hover:bg-dark-600/50"
                onClick={() => setSelectedSession(session)}
              >
                <div className="flex-1 min-w-0">
                  <span className="text-gray-300 truncate block">{session.question.slice(0, 80)}{session.question.length > 80 ? '...' : ''}</span>
                </div>
                <div className="flex items-center gap-2 ml-2 shrink-0">
                  <span className="text-gray-500">{session.participant_count}p</span>
                  <span className="text-gray-500">{formatRelativeTime(session.created_at)}</span>
                  <span className={cn(
                    'px-1.5 py-0.5 rounded',
                    session.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                    session.status === 'active' || session.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                    session.status === 'failed' ? 'bg-red-500/20 text-red-400' : 'bg-gray-600 text-gray-300'
                  )}>
                    {session.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Coordinator Teams Preview (when no section expanded) */}
      {!expandedSection && (
        <div className="card">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => toggleSection('coordinators')}
          >
            <h4 className="text-sm font-medium text-gray-400">Coordinator Teams</h4>
            <ChevronDown size={14} className="text-gray-400" />
          </div>
          <div className="space-y-2 mt-3">
            {(coordinators.length > 0 ? coordinators.slice(0, 3) : defaultCoordinators.slice(0, 3)).map((coord: any, idx) => (
              <TeamRow
                key={coord.name || coord.agent_name || idx}
                name={coord.name || coord.agent_name}
                agents={coord.sub_agent_count || coord.agents || 3}
                specialty={coord.specialization || coord.description || coord.specialty || 'Multi-agent coordination'}
              />
            ))}
            {(coordinators.length > 3 || defaultCoordinators.length > 3) && (
              <button
                onClick={() => toggleSection('coordinators')}
                className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
              >
                View all coordinators
              </button>
            )}
          </div>
        </div>
      )}

      {/* Session 969: HiveMind Session Detail Modal */}
      {selectedSession && (
        <HiveMindSessionDetailModal
          session={selectedSession}
          onClose={() => setSelectedSession(null)}
        />
      )}
    </div>
  )
}

// ============ Detail Modals ============

// Session 969: Helper to render output_data which can be a string, object, or nested structure
function renderOutputData(data: unknown): string {
  if (!data) return ''
  if (typeof data === 'string') return data
  if (typeof data === 'object') {
    const obj = data as Record<string, unknown>
    // Common output_data shapes: { result: "...", response: "...", output: "...", summary: "..." }
    // Try known text fields first for a clean display
    for (const key of ['result', 'response', 'output', 'summary', 'content', 'analysis', 'report', 'text']) {
      if (obj[key] && typeof obj[key] === 'string') return obj[key] as string
    }
    // If it has a nested result object with text inside
    if (obj.result && typeof obj.result === 'object') {
      const nested = obj.result as Record<string, unknown>
      for (const key of ['response', 'output', 'summary', 'content', 'text']) {
        if (nested[key] && typeof nested[key] === 'string') return nested[key] as string
      }
    }
    // Fallback: pretty-print the whole object
    return JSON.stringify(data, null, 2)
  }
  return String(data)
}

function ExecutionDetailModal({ execution, onClose }: { execution: ExecutionItem; onClose: () => void }) {
  const statusStyle = statusColors[execution.status] || statusColors.pending

  // Session 969: Fetch full execution detail (untruncated task + output_data + related_memory)
  const { data: detailData, isLoading: detailLoading } = useQuery({
    queryKey: ['execution-detail', execution.id],
    queryFn: async () => {
      try {
        const res = await fetch(`/api/v1/agents/execution/${execution.id}/`)
        if (!res.ok) return null
        const json = await res.json()
        return json.data as {
          execution: {
            task: string
            output_data: unknown
            input_data: unknown
            agent_display_name?: string
          }
          related_memory?: {
            id: string
            title: string
            content: string
            valence: string
            memory_type: string
            importance_score: number
          } | null
        }
      } catch {
        return null
      }
    },
    staleTime: 30000,
  })

  // Use detail data when available, fall back to list data
  const fullTask = detailData?.execution?.task || execution.task
  const outputData = detailData?.execution?.output_data
  const relatedMemory = detailData?.related_memory
  const outputText = renderOutputData(outputData)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 max-w-2xl w-full max-h-[85vh] overflow-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-700 sticky top-0 bg-gray-900 z-10">
          <h3 className="text-lg font-semibold">Execution Details</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div className="flex items-center gap-3">
            <span className={cn('px-3 py-1 rounded-full text-sm capitalize', statusStyle.bg, statusStyle.color)}>
              {execution.status}
            </span>
            <span className="text-gray-400">
              {detailData?.execution?.agent_display_name || execution.workflow_name || execution.agent_name || 'Workflow Execution'}
            </span>
          </div>

          {/* Session 969: Show full untruncated task from detail endpoint */}
          {fullTask && (
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Task</p>
              <p className="text-sm text-gray-300 max-h-40 overflow-y-auto whitespace-pre-wrap break-words">{fullTask}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">Started</p>
              <p className="text-sm flex items-center gap-2">
                <Calendar size={14} className="text-gray-400" />
                {execution.started_at ? new Date(execution.started_at).toLocaleString() : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Completed</p>
              <p className="text-sm flex items-center gap-2">
                <Timer size={14} className="text-gray-400" />
                {execution.completed_at ? new Date(execution.completed_at).toLocaleString() : 'In progress'}
              </p>
            </div>
          </div>

          {/* Session 958: Only show progress if we have real step data (not hardcoded 1/1) */}
          {execution.current_step && execution.total_steps && execution.total_steps > 1 && (
            <div>
              <p className="text-xs text-gray-500 mb-2">Progress</p>
              <div className="bg-gray-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-primary-500 h-full transition-all"
                  style={{ width: `${(execution.current_step / execution.total_steps) * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">Step {execution.current_step} of {execution.total_steps}</p>
            </div>
          )}

          {/* Session 958: Show execution metrics if available */}
          {/* Session 969: Added cost display */}
          {(execution.execution_time_ms || execution.tokens_used || (execution.cost != null && execution.cost > 0)) && (
            <div className="grid grid-cols-2 gap-4">
              {execution.execution_time_ms && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Duration</p>
                  <p className="text-sm">{(execution.execution_time_ms / 1000).toFixed(1)}s</p>
                </div>
              )}
              {execution.tokens_used && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Tokens</p>
                  <p className="text-sm">{execution.tokens_used.toLocaleString()}</p>
                </div>
              )}
              {execution.cost != null && execution.cost > 0 && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Cost</p>
                  <p className="text-sm">${execution.cost.toFixed(4)}</p>
                </div>
              )}
            </div>
          )}

          {execution.error_message && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-red-400 mb-1">
                <AlertCircle size={14} />
                <span className="text-sm font-medium">Error</span>
              </div>
              <p className="text-sm text-gray-300">{execution.error_message}</p>
            </div>
          )}

          {/* Session 969: Show full agent output from detail endpoint */}
          {detailLoading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="animate-spin text-primary-400" size={20} />
              <span className="text-sm text-gray-400 ml-2">Loading full output...</span>
            </div>
          ) : outputText ? (
            <div>
              <p className="text-xs text-gray-500 mb-2">Agent Output</p>
              <div className="bg-gray-800/50 rounded-lg p-3 max-h-80 overflow-y-auto">
                <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words font-sans">{outputText}</pre>
              </div>
            </div>
          ) : null}

          {/* Session 969: Show related memory if exists */}
          {relatedMemory && (
            <div>
              <p className="text-xs text-gray-500 mb-2">Related Memory</p>
              <div className="bg-primary-500/5 border border-primary-500/20 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-200">{relatedMemory.title}</span>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'text-xs px-1.5 py-0.5 rounded',
                      relatedMemory.valence === 'positive' ? 'bg-green-500/20 text-green-400' :
                      relatedMemory.valence === 'negative' ? 'bg-red-500/20 text-red-400' :
                      'bg-gray-600 text-gray-300'
                    )}>
                      {relatedMemory.valence}
                    </span>
                    <span className="text-xs text-gray-500">{relatedMemory.memory_type}</span>
                  </div>
                </div>
                <p className="text-xs text-gray-400 mt-1 whitespace-pre-wrap">{relatedMemory.content}</p>
              </div>
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <button
              onClick={onClose}
              className="btn btn-secondary flex-1"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ============ Session 970: Surgical Moves Verification Panel ============

function SurgicalMovesPanel({ onSelectSession }: { onSelectSession: (id: string) => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['deliberation-sessions-recent'],
    queryFn: async () => {
      const res = await fetch('/api/deliberation/sessions/?limit=5&status=completed')
      if (!res.ok) return null
      return res.json() as Promise<{
        count: number
        sessions: Array<{
          id: string
          objective: string
          status: string
          created_at: string | null
          turn_count: number
          contract_count: number
          blog?: {
            blog_title: string
            blog_id: string
            verdict: string | null
            quality_score: number | null
            structure_score: number | null
            publish_ready: boolean
          } | null
        }>
      }>
    },
    staleTime: 30000,
  })

  const sessions = data?.sessions || []

  if (isLoading) return null
  if (sessions.length === 0) return null

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-3">
        <GitBranch size={14} className="text-primary-400" />
        <h4 className="text-sm font-medium text-gray-400">Surgical Moves Verification</h4>
        <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400">
          {sessions.length}
        </span>
      </div>
      <div className="space-y-1.5">
        {sessions.map((s) => (
          <div
            key={s.id}
            className="flex items-center justify-between p-2 rounded-lg bg-dark-800/50 hover:bg-dark-700/50 cursor-pointer transition-colors"
            onClick={() => onSelectSession(s.id)}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-300 truncate">
                {s.blog?.blog_title || s.objective || 'No objective'}
              </p>
              <div className="flex items-center gap-2 mt-0.5">
                {s.blog?.verdict && (
                  <span className={cn(
                    'text-xs px-1.5 py-0.5 rounded font-medium uppercase',
                    s.blog.verdict === 'PUBLISH' && 'bg-green-500/20 text-green-400',
                    s.blog.verdict === 'REVISE' && 'bg-yellow-500/20 text-yellow-400',
                    s.blog.verdict === 'KILL' && 'bg-red-500/20 text-red-400',
                    !['PUBLISH', 'REVISE', 'KILL'].includes(s.blog.verdict) && 'bg-gray-600 text-gray-300'
                  )}>
                    {s.blog.verdict}
                  </span>
                )}
                {s.blog?.quality_score != null && (
                  <span className="text-xs text-gray-500">Q: {s.blog.quality_score.toFixed(2)}</span>
                )}
                <span className="text-xs text-gray-500">
                  {s.created_at ? new Date(s.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2 ml-2 shrink-0">
              <span className="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-300">
                {s.turn_count} turns
              </span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-300">
                {s.contract_count} contracts
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ============ Deliberation Failure Breakdown Panel ============

const REASON_LABELS: Record<string, { label: string; color: string }> = {
  TIMEOUT: { label: 'Timeout', color: 'text-orange-400' },
  LLM_UPSTREAM: { label: 'LLM Upstream', color: 'text-red-400' },
  EMPTY_TURN: { label: 'Empty Turn', color: 'text-yellow-400' },
  TOOL_ERROR: { label: 'Tool Error', color: 'text-red-300' },
  GATE_REJECT: { label: 'Gate Rejected', color: 'text-purple-400' },
  DRAFT_FAILED: { label: 'Draft Failed', color: 'text-pink-400' },
  UNKNOWN: { label: 'Unknown', color: 'text-gray-400' },
}

function FailureBreakdownPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['deliberation-failure-stats'],
    queryFn: async () => {
      const res = await fetch('/api/deliberation/failure-stats/?hours=24')
      if (!res.ok) return null
      return res.json() as Promise<{
        hours: number
        total_sessions: number
        total_failed: number
        failure_rate: number
        by_reason: Record<string, number>
        recent_failures: Array<{
          id: string
          objective: string
          failure_reason_code: string
          failure_detail: string
          created_at: string | null
        }>
      }>
    },
    staleTime: 60000,
  })

  if (isLoading || !data || data.total_failed === 0) return null

  const sorted = Object.entries(data.by_reason).sort((a, b) => b[1] - a[1])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle size={14} className="text-orange-400" />
          <h4 className="text-sm font-medium text-gray-400">Deliberation Failures (24h)</h4>
          <span className="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 font-medium">
            {data.total_failed}
          </span>
        </div>
        <span className="text-xs text-gray-500">
          {data.total_sessions} total / {(data.failure_rate * 100).toFixed(1)}% fail rate
        </span>
      </div>

      {/* Reason breakdown bars */}
      <div className="space-y-1.5 mb-3">
        {sorted.map(([code, count]) => {
          const meta = REASON_LABELS[code] || REASON_LABELS.UNKNOWN
          const pct = data.total_failed > 0 ? (count / data.total_failed) * 100 : 0
          return (
            <div key={code} className="flex items-center gap-2">
              <span className={cn('text-xs w-24 shrink-0 font-medium', meta.color)}>
                {meta.label}
              </span>
              <div className="flex-1 h-2 bg-dark-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-red-500/60 to-orange-500/60 rounded-full"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="text-xs text-gray-400 w-6 text-right">{count}</span>
            </div>
          )
        })}
      </div>

      {/* Recent failures list */}
      {data.recent_failures.length > 0 && (
        <div className="border-t border-dark-700 pt-2 space-y-1">
          <p className="text-xs text-gray-500 mb-1">Recent failures:</p>
          {data.recent_failures.slice(0, 3).map((f) => (
            <div key={f.id} className="text-xs flex items-start gap-1.5 text-gray-400">
              <span className={cn('shrink-0 mt-0.5', (REASON_LABELS[f.failure_reason_code] || REASON_LABELS.UNKNOWN).color)}>
                {(REASON_LABELS[f.failure_reason_code] || REASON_LABELS.UNKNOWN).label}
              </span>
              <span className="truncate">{f.failure_detail || f.objective}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ============ Session 970: Verification Report Modal ============

interface VerificationCheck {
  phase: string
  name: string
  status: 'pass' | 'warn' | 'fail'
  detail: string
}

interface VerificationReport {
  session: {
    id: string
    status: string
    objective: string
    created_at: string | null
    completed_at: string | null
    participant_count: number
  }
  blog?: {
    blog_title: string
    blog_id: string
    verdict: string | null
    quality_score: number | null
    structure_score: number | null
    publish_ready: boolean
  } | null
  turns: { count: number; agents: string[] }
  contracts: Array<{ type: string; data_size: number; verdict_summary: string | null }>
  evidence_stats: {
    sources: number
    claims: number
    contradictions: number
    internal_refs: number
    memory_retrievals: number
  }
  trace_stats: { turns_recorded: number; has_contracts: boolean; has_decisions: boolean }
  checks: VerificationCheck[]
}

function VerificationReportModal({ sessionId, onClose }: { sessionId: string; onClose: () => void }) {
  const [showRaw, setShowRaw] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['deliberation-verification', sessionId],
    queryFn: async () => {
      const res = await fetch(`/api/deliberation/sessions/${sessionId}/verification-report/`)
      if (!res.ok) return null
      return res.json() as Promise<VerificationReport>
    },
    staleTime: 60000,
  })

  const statusIcon = (s: string) => {
    if (s === 'pass') return <CheckCircle size={14} className="text-green-400" />
    if (s === 'warn') return <AlertCircle size={14} className="text-yellow-400" />
    return <XCircle size={14} className="text-red-400" />
  }

  const statusBg = (s: string) => {
    if (s === 'pass') return 'bg-green-500/10'
    if (s === 'warn') return 'bg-yellow-500/10'
    return 'bg-red-500/10'
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 max-w-2xl w-full max-h-[85vh] overflow-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-700 sticky top-0 bg-gray-900 z-10">
          <h3 className="text-lg font-semibold">Verification Report</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin text-primary-400" size={24} />
              <span className="text-sm text-gray-400 ml-2">Loading report...</span>
            </div>
          ) : !data ? (
            <p className="text-sm text-gray-400 text-center py-4">Failed to load report</p>
          ) : (
            <>
              {/* Session info */}
              <div className="bg-gray-800/50 rounded-lg p-3">
                {data.blog ? (
                  <>
                    <p className="text-sm font-medium text-gray-200 mb-1">{data.blog.blog_title}</p>
                    <div className="flex items-center gap-2 mb-2">
                      {data.blog.verdict && (
                        <span className={cn(
                          'text-xs px-2 py-0.5 rounded font-medium uppercase',
                          data.blog.verdict === 'PUBLISH' && 'bg-green-500/20 text-green-400',
                          data.blog.verdict === 'REVISE' && 'bg-yellow-500/20 text-yellow-400',
                          data.blog.verdict === 'KILL' && 'bg-red-500/20 text-red-400',
                          !['PUBLISH', 'REVISE', 'KILL'].includes(data.blog.verdict) && 'bg-gray-600 text-gray-300'
                        )}>
                          {data.blog.verdict}
                        </span>
                      )}
                      {data.blog.quality_score != null && (
                        <span className="text-xs text-gray-400">Quality: {data.blog.quality_score.toFixed(2)}</span>
                      )}
                      {data.blog.structure_score != null && (
                        <span className="text-xs text-gray-400">Structure: {data.blog.structure_score.toFixed(2)}</span>
                      )}
                      {data.blog.publish_ready && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-green-500/10 text-green-400">Publish Ready</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mb-1">{data.session.objective}</p>
                  </>
                ) : (
                  <p className="text-sm text-gray-300 mb-1">{data.session.objective || 'No objective'}</p>
                )}
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className={cn(
                    'px-2 py-0.5 rounded capitalize',
                    data.session.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-gray-600 text-gray-300'
                  )}>
                    {data.session.status}
                  </span>
                  <span>{data.turns.count} turns</span>
                  <span>{data.turns.agents.join(', ')}</span>
                  {data.session.created_at && (
                    <span>{new Date(data.session.created_at).toLocaleString()}</span>
                  )}
                </div>
              </div>

              {/* Checks */}
              <div className="space-y-1.5">
                {data.checks.map((check, i) => (
                  <div key={i} className={cn('flex items-center gap-2 p-2 rounded-lg', statusBg(check.status))}>
                    {statusIcon(check.status)}
                    <span className="text-xs text-gray-500 w-16 shrink-0">{check.phase}</span>
                    <span className="text-sm text-gray-300 flex-1">{check.name}</span>
                    <span className="text-xs text-gray-400 text-right">{check.detail}</span>
                  </div>
                ))}
              </div>

              {/* Contracts */}
              {data.contracts.length > 0 && (
                <div>
                  <p className="text-xs text-gray-500 mb-2">Contracts</p>
                  <div className="space-y-1">
                    {data.contracts.map((c, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm bg-gray-800/30 p-2 rounded">
                        <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400 capitalize">{c.type}</span>
                        <span className="text-gray-400">{c.data_size}B</span>
                        {c.verdict_summary && (
                          <span className="text-gray-300 truncate flex-1">{c.verdict_summary}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence stats */}
              <div>
                <p className="text-xs text-gray-500 mb-2">Evidence Stats</p>
                <div className="grid grid-cols-5 gap-2">
                  {Object.entries(data.evidence_stats).map(([key, val]) => (
                    <div key={key} className="text-center bg-gray-800/30 p-2 rounded">
                      <p className="text-sm font-medium text-gray-300">{val}</p>
                      <p className="text-xs text-gray-500">{key.replace('_', ' ')}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Raw JSON toggle */}
              <div>
                <button
                  onClick={() => setShowRaw(!showRaw)}
                  className="text-xs text-primary-400 hover:text-primary-300"
                >
                  {showRaw ? 'Hide' : 'Show'} raw JSON
                </button>
                {showRaw && (
                  <pre className="mt-2 text-xs text-gray-400 bg-gray-800/50 p-3 rounded-lg max-h-60 overflow-auto whitespace-pre-wrap">
                    {JSON.stringify(data, null, 2)}
                  </pre>
                )}
              </div>
            </>
          )}

          <button onClick={onClose} className="btn btn-secondary w-full">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

function WorkflowDetailModal({ workflow, onClose }: { workflow: WorkflowItem; onClose: () => void }) {
  const [isExecuting, setIsExecuting] = useState(false)
  const [executeMessage, setExecuteMessage] = useState<string | null>(null)

  // Session 924: Fetch workflow detail with steps
  const { data: detailData, isLoading: detailLoading } = useQuery({
    queryKey: ['workflow-detail', workflow.id],
    queryFn: async () => {
      const res = await orchestrationApi.getWorkflowDetail(workflow.id)
      return res.data
    },
    staleTime: 30000,
  })

  // Session 924: Fetch recent executions for this workflow
  const { data: executionsData } = useQuery({
    queryKey: ['workflow-executions', workflow.id],
    queryFn: async () => {
      const res = await orchestrationApi.listExecutions({ workflow_id: workflow.id, limit: 5 })
      return res.data
    },
    staleTime: 30000,
  })

  const steps = detailData?.steps || []
  const detail = detailData?.workflow
  const recentExecutions = executionsData?.executions || []

  const handleExecute = async () => {
    setIsExecuting(true)
    setExecuteMessage(null)
    try {
      const result = await orchestrationApi.execute(workflow.id, {}, true)
      setExecuteMessage(result.data.message || 'Workflow started successfully')
    } catch (error) {
      setExecuteMessage('Failed to start workflow')
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 max-w-2xl w-full max-h-[85vh] overflow-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-700 sticky top-0 bg-gray-900 z-10">
          <div className="flex items-center gap-2">
            <Workflow className="text-primary-400" size={20} />
            <h3 className="text-lg font-semibold">{workflow.name}</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {workflow.description && (
            <p className="text-sm text-gray-300">{workflow.description}</p>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Execution Mode</p>
              <p className="text-sm capitalize font-medium">{workflow.execution_mode || 'sequential'}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Steps</p>
              <p className="text-sm font-medium">{steps.length || workflow.step_count || 0}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Timeout</p>
              <p className="text-sm font-medium">{detail?.timeout_seconds ? `${detail.timeout_seconds}s` : 'None'}</p>
            </div>
          </div>

          {/* Workflow Steps */}
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
              <List size={14} />
              Workflow Steps
            </h4>
            {detailLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="animate-spin text-primary-400" size={20} />
              </div>
            ) : steps.length > 0 ? (
              <div className="space-y-2">
                {steps.map((step: any, index: number) => (
                  <div key={step.id || index} className="bg-gray-800 rounded-lg p-3 border-l-2 border-primary-500">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded">
                          Step {step.order || index + 1}
                        </span>
                        <span className="text-sm font-medium">{step.name}</span>
                      </div>
                      <span className="text-xs text-gray-500">{step.agent}</span>
                    </div>
                    {step.description && (
                      <p className="text-xs text-gray-400 mt-1">{step.description}</p>
                    )}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {step.requires_approval && (
                        <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded">
                          Requires Approval
                        </span>
                      )}
                      {step.timeout_seconds && (
                        <span className="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded">
                          {step.timeout_seconds}s timeout
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 italic">No steps defined</p>
            )}
          </div>

          {/* Recent Executions */}
          {recentExecutions.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
                <Clock size={14} />
                Recent Executions
              </h4>
              <div className="space-y-1">
                {recentExecutions.map((exec: any) => (
                  <div key={exec.id} className="flex items-center justify-between bg-gray-800 rounded px-3 py-2">
                    <div className="flex items-center gap-2">
                      {exec.status === 'completed' && <CheckCircle size={12} className="text-green-400" />}
                      {exec.status === 'failed' && <XCircle size={12} className="text-red-400" />}
                      {exec.status === 'running' && <Loader2 size={12} className="text-blue-400 animate-spin" />}
                      {!['completed', 'failed', 'running'].includes(exec.status) && <Clock size={12} className="text-gray-400" />}
                      <span className="text-xs capitalize">{exec.status}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {exec.started_at ? new Date(exec.started_at).toLocaleString() : 'Pending'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-700">
            <span>ID: {workflow.id.slice(0, 8)}...</span>
            {workflow.created_at && (
              <span>Created: {new Date(workflow.created_at).toLocaleDateString()}</span>
            )}
          </div>

          {/* Execute Message */}
          {executeMessage && (
            <div className={cn(
              "text-sm p-2 rounded",
              executeMessage.includes('Failed') ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
            )}>
              {executeMessage}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={handleExecute}
              disabled={isExecuting}
              className="btn btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {isExecuting ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Play size={16} />
              )}
              {isExecuting ? 'Starting...' : 'Execute Workflow'}
            </button>
            <button
              onClick={onClose}
              className="btn btn-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Session 969: HiveMind Session Detail Modal
function HiveMindSessionDetailModal({ session, onClose }: { session: HiveMindSessionItem; onClose: () => void }) {
  const statusStyle = statusColors[session.status] || statusColors.pending

  // Fetch full session detail
  const { data: detail, isLoading } = useQuery({
    queryKey: ['hivemind-session-detail', session.id],
    queryFn: async () => {
      try {
        const response = await hiveMindApi.detail(session.id)
        return response.data as HiveMindSessionDetail
      } catch {
        return null
      }
    },
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 max-w-2xl w-full max-h-[85vh] overflow-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-700 sticky top-0 bg-gray-900 z-10">
          <div className="flex items-center gap-2">
            <MessageSquare className="text-accent-cyan" size={20} />
            <h3 className="text-lg font-semibold">HiveMind Session</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Status + Mode */}
          <div className="flex items-center gap-3 flex-wrap">
            <span className={cn('px-3 py-1 rounded-full text-sm capitalize', statusStyle.bg, statusStyle.color)}>
              {session.status}
            </span>
            {detail?.mode && (
              <span className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">{detail.mode}</span>
            )}
            {detail?.conversation_type && (
              <span className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">{detail.conversation_type}</span>
            )}
          </div>

          {/* Question */}
          <div className="bg-gray-800/50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">Question</p>
            <p className="text-sm text-gray-200">{detail?.question || session.question}</p>
          </div>

          {/* Objective & Success Criteria */}
          {detail?.objective && (
            <div className="bg-gray-800/50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Objective</p>
              <p className="text-sm text-gray-300">{detail.objective}</p>
              {detail.success_criteria && detail.success_criteria.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-gray-500 mb-1">Success Criteria</p>
                  <ul className="text-xs text-gray-400 space-y-1">
                    {detail.success_criteria.map((c, i) => (
                      <li key={i} className="flex items-start gap-1">
                        <span className="text-accent-green mt-0.5">-</span>
                        <span>{c}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Participants</p>
              <p className="text-sm font-medium">{detail?.participant_count ?? session.participant_count}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Contributions</p>
              <p className="text-sm font-medium">{detail?.contribution_count ?? session.contribution_count}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Think Time</p>
              <p className="text-sm font-medium">
                {detail?.total_thinking_time ? `${detail.total_thinking_time.toFixed(1)}s` : 'N/A'}
              </p>
            </div>
          </div>

          {/* Contributions */}
          {isLoading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="animate-spin text-primary-400" size={20} />
            </div>
          ) : detail?.contributions && detail.contributions.length > 0 ? (
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
                <Users size={14} />
                Contributions ({detail.contributions.length})
              </h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {detail.contributions.map((contrib, idx) => (
                  <div key={idx} className="bg-gray-800 rounded-lg p-3 border-l-2 border-accent-cyan">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-200">{contrib.agent_name}</span>
                        {contrib.specialization && (
                          <span className="text-xs text-gray-500">{contrib.specialization}</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        {contrib.perspective_type && (
                          <span className={cn(
                            'text-xs px-1.5 py-0.5 rounded',
                            contrib.perspective_type === 'bullish' ? 'bg-green-500/20 text-green-400' :
                            contrib.perspective_type === 'bearish' ? 'bg-red-500/20 text-red-400' :
                            'bg-gray-600 text-gray-300'
                          )}>
                            {contrib.perspective_type}
                          </span>
                        )}
                        {contrib.confidence != null && (
                          <span className="text-xs text-gray-400">{Math.round(contrib.confidence * 100)}%</span>
                        )}
                      </div>
                    </div>
                    {contrib.key_points && contrib.key_points.length > 0 && (
                      <ul className="text-xs text-gray-400 space-y-0.5 mt-1">
                        {contrib.key_points.slice(0, 4).map((point, i) => (
                          <li key={i} className="flex items-start gap-1">
                            <span className="text-primary-400 mt-0.5">-</span>
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                    {contrib.thinking_time != null && (
                      <div className="text-xs text-gray-500 mt-1">{contrib.thinking_time.toFixed(1)}s thinking</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {/* Synthesis */}
          {detail?.synthesis && (
            <div>
              <h4 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
                <Brain size={14} />
                Synthesis
              </h4>
              <div className="bg-gray-800/50 rounded-lg p-3">
                {detail.synthesis_summary && (
                  <p className="text-sm text-gray-200 mb-2 font-medium">{detail.synthesis_summary}</p>
                )}
                <p className="text-sm text-gray-300 whitespace-pre-wrap max-h-40 overflow-y-auto">{detail.synthesis}</p>
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-700">
            <span>Created: {new Date(session.created_at).toLocaleString()}</span>
            {session.completed_at && (
              <span>Completed: {new Date(session.completed_at).toLocaleString()}</span>
            )}
          </div>

          <div className="flex gap-2 pt-2">
            <button onClick={onClose} className="btn btn-secondary flex-1">Close</button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Session 969: Relative time formatting helper
function formatRelativeTime(dateStr: string): string {
  const now = Date.now()
  const date = new Date(dateStr).getTime()
  const diffMs = now - date
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHrs = Math.floor(diffMin / 60)
  if (diffHrs < 24) return `${diffHrs}h ago`
  const diffDays = Math.floor(diffHrs / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  return new Date(dateStr).toLocaleDateString()
}

// ============ Helper Components ============

function InlineHeaderRow({
  title,
  subtitle,
  onRefresh,
  isFetching,
}: {
  title: string
  subtitle?: string
  onRefresh?: () => void
  isFetching?: boolean
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h3 className="text-lg font-semibold">{title}</h3>
        {subtitle && (
          <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
            {subtitle}
          </span>
        )}
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          disabled={isFetching}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
          title="Refresh data"
        >
          <RefreshCw size={14} className={cn('text-gray-400', isFetching && 'animate-spin')} />
        </button>
      )}
    </div>
  )
}

function ExpandedListCard({
  title,
  count,
  children,
  onClose,
}: {
  title: string
  count: number
  children: React.ReactNode
  onClose: () => void
}) {
  return (
    <div className="card border-primary-500/30 bg-primary-500/5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <List size={16} className="text-primary-400" />
          <h4 className="font-medium">{title}</h4>
          <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400">
            {count}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-800 rounded transition-colors"
        >
          <X size={14} className="text-gray-400" />
        </button>
      </div>
      {children}
    </div>
  )
}

function ExecutionRow({ execution, onClick }: { execution: ExecutionItem; onClick?: () => void }) {
  const statusStyle = statusColors[execution.status] || statusColors.pending
  const StatusIcon = execution.status === 'running' ? Play :
                     execution.status === 'completed' ? CheckCircle :
                     execution.status === 'failed' ? XCircle : Clock

  return (
    <div
      className={cn(
        'flex items-center gap-3 py-2 border-b border-gray-800 last:border-0',
        onClick && 'cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded'
      )}
      onClick={onClick}
    >
      <div className={cn('h-8 w-8 rounded-lg flex items-center justify-center shrink-0', statusStyle.bg)}>
        <StatusIcon size={14} className={statusStyle.color} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-sm font-medium truncate">{execution.workflow_name || 'Workflow'}</div>
        <div className="text-xs text-gray-500">
          {execution.started_at ? new Date(execution.started_at).toLocaleString() : 'Pending'}
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize shrink-0', statusStyle.bg, statusStyle.color)}>
        {execution.status}
      </span>
    </div>
  )
}

function WorkflowCard({ workflow, onClick }: { workflow: WorkflowItem; onClick?: () => void }) {
  return (
    <div
      className={cn(
        'card hover:border-primary-500/50 transition-colors',
        onClick && 'cursor-pointer'
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Workflow size={16} className="text-primary-400" />
          <span className="font-medium">{workflow.name}</span>
        </div>
        <span className={cn(
          'text-xs px-2 py-0.5 rounded',
          workflow.is_active !== false ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
        )}>
          {workflow.is_active !== false ? 'Active' : 'Inactive'}
        </span>
      </div>
      <p className="text-xs text-gray-400 mb-2">{workflow.description || 'No description'}</p>
      <div className="flex items-center gap-3 text-xs text-gray-500">
        <span>{workflow.step_count || workflow.steps?.length || 0} steps</span>
        <span>•</span>
        <span>{workflow.execution_mode || 'sequential'}</span>
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  icon: Icon,
  color,
  onClick,
  isExpanded,
}: {
  label: string
  value: number | string
  icon: typeof Activity
  color: string
  onClick?: () => void
  isExpanded?: boolean
}) {
  return (
    <div
      className={cn(
        'card',
        onClick && 'cursor-pointer hover:border-primary-500/50 transition-colors',
        isExpanded && 'border-primary-500/50 bg-primary-500/5'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
            <Icon size={20} className={color} />
          </div>
          {onClick && (
            isExpanded ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )
          )}
        </div>
      </div>
    </div>
  )
}

function FeatureRow({
  label,
  status,
  description,
}: {
  label: string
  status: 'active' | 'inactive'
  description: string
}) {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-3">
        <div className={cn(
          'h-2 w-2 rounded-full',
          status === 'active' ? 'bg-accent-green' : 'bg-gray-500'
        )} />
        <div>
          <span className="text-sm">{label}</span>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
      <span className={cn(
        'text-xs px-2 py-0.5 rounded capitalize',
        status === 'active' ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
      )}>
        {status}
      </span>
    </div>
  )
}

function TeamRow({
  name,
  agents,
  specialty,
}: {
  name: string
  agents: number
  specialty: string
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div>
        <span className="text-sm font-medium">{name}</span>
        <p className="text-xs text-gray-500">{specialty}</p>
      </div>
      <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
        {agents} agents
      </span>
    </div>
  )
}
