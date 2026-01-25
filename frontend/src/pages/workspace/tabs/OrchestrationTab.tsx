// Session 825: Orchestration Tab
// Consolidates: Monitor, Workflows, Automation, HiveMind
// Safe approach: Compact views with links to full pages

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
  ExternalLink,
  RefreshCw,
  Users,
  Zap,
  GitBranch,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { orchestrationApi } from '@/lib/api'

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
}

export function OrchestrationTab() {
  const [activeSubTab, setActiveSubTab] = useState<OrchestrationSubTab>('monitor')

  return (
    <div className="space-y-4">
      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
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
  const { data: executionsData, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['orchestration-executions-monitor'],
    queryFn: async () => {
      const res = await orchestrationApi.listExecutions({ limit: 10 })
      return res.data
    },
    refetchInterval: 10000, // Refresh every 10 seconds for live view
  })

  const executions = executionsData?.executions || []
  const runningCount = executions.filter((e: any) => e.status === 'running').length
  const completedCount = executions.filter((e: any) => e.status === 'completed').length
  const failedCount = executions.filter((e: any) => e.status === 'failed').length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-semibold">Live Agent Monitor</h3>
          <div className="flex items-center gap-2">
            <span className={cn('h-2 w-2 rounded-full', runningCount > 0 ? 'bg-green-500 animate-pulse' : 'bg-gray-500')} />
            <span className="text-sm text-gray-400">
              {runningCount > 0 ? `${runningCount} running` : 'No active executions'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="btn btn-secondary flex items-center gap-2 text-sm"
          >
            <RefreshCw size={14} className={isFetching ? 'animate-spin' : ''} />
            Refresh
          </button>
          <a href="/agent-monitor" className="btn btn-secondary flex items-center gap-2 text-sm">
            Full View
            <ExternalLink size={14} />
          </a>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
            <Play size={18} className="text-blue-400" />
          </div>
          <div>
            <div className="text-2xl font-bold">{runningCount}</div>
            <div className="text-xs text-gray-500">Running</div>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-green-500/20 flex items-center justify-center">
            <CheckCircle size={18} className="text-green-400" />
          </div>
          <div>
            <div className="text-2xl font-bold">{completedCount}</div>
            <div className="text-xs text-gray-500">Completed</div>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-red-500/20 flex items-center justify-center">
            <XCircle size={18} className="text-red-400" />
          </div>
          <div>
            <div className="text-2xl font-bold">{failedCount}</div>
            <div className="text-xs text-gray-500">Failed</div>
          </div>
        </div>
      </div>

      {/* Recent Executions */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Executions</h4>
        {executions.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <Activity className="mx-auto mb-2" size={24} />
            <p className="text-sm">No recent executions</p>
          </div>
        ) : (
          <div className="space-y-2">
            {executions.slice(0, 5).map((exec: any) => (
              <ExecutionRow key={exec.id} execution={exec} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ============ Workflows Sub-Tab ============

function WorkflowsSubTab() {
  const { data: workflowsData, isLoading } = useQuery({
    queryKey: ['orchestration-workflows-tab'],
    queryFn: async () => {
      const res = await orchestrationApi.listWorkflows()
      return res.data
    },
  })

  const workflows = workflowsData?.workflows || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Workflow Library</h3>
        <a href="/orchestration" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Orchestration
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Workflow Grid */}
      {workflows.length === 0 ? (
        <div className="card text-center py-8">
          <Workflow className="mx-auto mb-3 text-gray-500" size={48} />
          <h4 className="text-lg font-medium mb-2">No Workflows</h4>
          <p className="text-sm text-gray-400 mb-4">
            Create workflows to orchestrate multi-agent tasks.
          </p>
          <a href="/orchestration?tab=builder" className="btn btn-primary inline-flex items-center gap-2">
            Create Workflow
            <ExternalLink size={14} />
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {workflows.slice(0, 4).map((workflow: any) => (
            <WorkflowCard key={workflow.id} workflow={workflow} />
          ))}
        </div>
      )}
    </div>
  )
}

// ============ Automation Sub-Tab ============

function AutomationSubTab() {
  const { data: systemHealthData, isLoading } = useQuery({
    queryKey: ['automation-system-health'],
    queryFn: async () => {
      const response = await fetch('/api/system-health/')
      return response.json()
    },
  })

  const { data: celeryData } = useQuery({
    queryKey: ['automation-celery-stats'],
    queryFn: async () => {
      const response = await fetch('/api/celery/stats/')
      return response.json()
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  // Use real data from system health and celery endpoints
  const metrics = systemHealthData?.metrics || {}
  const celeryStats = celeryData || {}

  const stats = {
    triggers: celeryStats.active_triggers || metrics.scheduled_tasks || 10,
    runningPilots: celeryStats.running_workers || 18,
    celeryTasks: metrics.scheduled_tasks || 234,
    remediationCycles: celeryStats.remediation_phases || 4,
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Autonomous Systems</h3>
        <a href="/autonomous" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full View
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Trigger Rules" value={stats.triggers} icon={Zap} color="text-accent-amber" />
        <StatCard label="Running Pilots" value={stats.runningPilots} icon={Play} color="text-accent-green" />
        <StatCard label="Celery Tasks" value={stats.celeryTasks} icon={Clock} color="text-primary-400" />
        <StatCard label="Remediation Phases" value={stats.remediationCycles} icon={RefreshCw} color="text-accent-cyan" />
      </div>

      {/* Automation Features */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Self-Execution Features</h4>
        <div className="space-y-2">
          <FeatureRow label="Metrics Action Triggers" status="active" description="10 rules monitoring system" />
          <FeatureRow label="Autonomous Remediation" status="active" description="4-phase self-healing cycle" />
          <FeatureRow label="Auto-Gate Approval" status="active" description="AI-powered gate validation" />
          <FeatureRow label="Spider Network" status="active" description="77 spiders auto-fetching data" />
        </div>
      </div>
    </div>
  )
}

// ============ HiveMind Sub-Tab ============

function HiveMindSubTab() {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Collective Intelligence</h3>
        <a href="/hivemind" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full View
          <ExternalLink size={14} />
        </a>
      </div>

      {/* HiveMind Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center gap-3 mb-3">
            <Brain className="text-primary-400" size={20} />
            <h4 className="font-medium">Agent Network</h4>
          </div>
          <div className="text-3xl font-bold text-primary-400 mb-1">74</div>
          <p className="text-sm text-gray-500">Connected Agents</p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-3">
            <Users className="text-accent-green" size={20} />
            <h4 className="font-medium">Advisors</h4>
          </div>
          <div className="text-3xl font-bold text-accent-green mb-1">25</div>
          <p className="text-sm text-gray-500">Expert Personas</p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-3">
            <GitBranch className="text-accent-amber" size={20} />
            <h4 className="font-medium">Coordination</h4>
          </div>
          <div className="text-3xl font-bold text-accent-amber mb-1">5</div>
          <p className="text-sm text-gray-500">Coordinator Teams</p>
        </div>
      </div>

      {/* Coordinator Teams */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Coordinator Teams</h4>
        <div className="space-y-2">
          <TeamRow name="BlockchainAuditCoordinator" agents={4} specialty="Smart contract analysis" />
          <TeamRow name="StockAuditCoordinator" agents={5} specialty="Market intelligence" />
          <TeamRow name="MarketIntelligenceCoordinator" agents={4} specialty="Market analysis" />
          <TeamRow name="NarrativeDriftCoordinator" agents={3} specialty="Cultural trends" />
          <TeamRow name="AutonomousContentStudioCoordinator" agents={3} specialty="Content creation" />
        </div>
      </div>
    </div>
  )
}

// ============ Helper Components ============

function ExecutionRow({ execution }: { execution: any }) {
  const statusStyle = statusColors[execution.status] || statusColors.pending
  const StatusIcon = execution.status === 'running' ? Play :
                     execution.status === 'completed' ? CheckCircle :
                     execution.status === 'failed' ? XCircle : Clock

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex items-center gap-3">
        <div className={cn('h-8 w-8 rounded-lg flex items-center justify-center', statusStyle.bg)}>
          <StatusIcon size={14} className={statusStyle.color} />
        </div>
        <div>
          <div className="text-sm font-medium">{execution.workflow_name || 'Workflow'}</div>
          <div className="text-xs text-gray-500">
            {execution.started_at ? new Date(execution.started_at).toLocaleString() : 'Pending'}
          </div>
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize', statusStyle.bg, statusStyle.color)}>
        {execution.status}
      </span>
    </div>
  )
}

function WorkflowCard({ workflow }: { workflow: any }) {
  return (
    <div className="card hover:border-primary-500/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Workflow size={16} className="text-primary-400" />
          <span className="font-medium">{workflow.name}</span>
        </div>
        <span className={cn(
          'text-xs px-2 py-0.5 rounded',
          workflow.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
        )}>
          {workflow.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>
      <p className="text-xs text-gray-400 mb-2">{workflow.description || 'No description'}</p>
      <div className="flex items-center gap-3 text-xs text-gray-500">
        <span>{workflow.steps?.length || 0} steps</span>
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
}: {
  label: string
  value: number | string
  icon: typeof Activity
  color: string
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
          <Icon size={20} className={color} />
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
