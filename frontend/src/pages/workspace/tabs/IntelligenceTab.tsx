// Session 825: Intelligence Tab
// Consolidates: Reasoning Engine, Mythology Lab, Collective Intelligence
// Safe approach: Compact views with links to full pages

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Brain,
  Shield,
  Users,
  Loader2,
  ExternalLink,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Network,
  BookOpen,
  Activity,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { reasoningApi, mythologyApi, collectiveApi } from '@/lib/api'

// Sub-tab configuration
type IntelligenceSubTab = 'reasoning' | 'safety' | 'collective'

const subTabs: Array<{ id: IntelligenceSubTab; label: string; icon: typeof Brain; description: string }> = [
  { id: 'reasoning', label: 'Reasoning', icon: Brain, description: 'Gate & decision system' },
  { id: 'safety', label: 'Safety', icon: Shield, description: 'Hallucination detection' },
  { id: 'collective', label: 'Collective', icon: Users, description: 'Shared intelligence' },
]

export function IntelligenceTab() {
  const [activeSubTab, setActiveSubTab] = useState<IntelligenceSubTab>('reasoning')

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
      {activeSubTab === 'reasoning' && <ReasoningSubTab />}
      {activeSubTab === 'safety' && <SafetySubTab />}
      {activeSubTab === 'collective' && <CollectiveSubTab />}
    </div>
  )
}

// ============ Reasoning Engine Sub-Tab ============

function ReasoningSubTab() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['reasoning-dashboard-tab'],
    queryFn: async () => {
      const res = await reasoningApi.dashboard()
      return res.data
    },
  })

  const { data: pendingData } = useQuery({
    queryKey: ['reasoning-pending-tab'],
    queryFn: async () => {
      const res = await reasoningApi.pendingActions()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const dashboard = dashboardData || {
    total_gates: 0,
    approved_gates: 0,
    pending_gates: 0,
    total_thoughts: 0,
  }
  const pending = pendingData?.actions || []

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Reasoning Engine</h3>
        <a href="/reasoning-engine" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Engine
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Gate Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total Gates"
          value={dashboard.total_gates || 0}
          icon={Brain}
          color="text-primary-400"
        />
        <StatCard
          label="Approved"
          value={dashboard.approved_gates || 0}
          icon={CheckCircle}
          color="text-accent-green"
        />
        <StatCard
          label="Pending"
          value={dashboard.pending_gates || 0}
          icon={Clock}
          color="text-accent-amber"
        />
        <StatCard
          label="Thoughts"
          value={dashboard.total_thoughts || 0}
          icon={Zap}
          color="text-accent-purple"
        />
      </div>

      {/* Pending Actions */}
      {pending.length > 0 && (
        <div className="card border-accent-amber/50">
          <div className="flex items-center gap-2 mb-3">
            <Clock size={16} className="text-accent-amber" />
            <h4 className="text-sm font-medium">Pending Actions ({pending.length})</h4>
          </div>
          <div className="space-y-2">
            {pending.slice(0, 3).map((action: any) => (
              <PendingActionRow key={action.id} action={action} />
            ))}
          </div>
          <a href="/reasoning-engine?tab=actions" className="btn btn-secondary text-sm mt-3 w-full">
            View All Pending
          </a>
        </div>
      )}

      {/* Gate Pipeline */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Gate Pipeline</h4>
        <div className="space-y-2">
          <PipelineRow label="Readiness Gates" description="Pre-deployment checks" />
          <PipelineRow label="Safety Gates" description="Risk assessment" />
          <PipelineRow label="Quality Gates" description="Output validation" />
          <PipelineRow label="Auto-Approval" description="AI-powered gate evaluation" />
        </div>
      </div>
    </div>
  )
}

// ============ Safety (Mythology Lab) Sub-Tab ============

function SafetySubTab() {
  const { data: statsData, isLoading } = useQuery({
    queryKey: ['mythology-stats-tab'],
    queryFn: async () => {
      const res = await mythologyApi.stats()
      return res.data
    },
  })

  const { data: eventsData } = useQuery({
    queryKey: ['mythology-events-tab'],
    queryFn: async () => {
      const res = await mythologyApi.recentEvents({ limit: 5 })
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const stats = statsData || {
    total_patterns: 10,
    active_guards: 8,
    flagged_today: 0,
    blocked_rate: 0,
  }
  const events = eventsData?.events || []

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Safety & Mythology Lab</h3>
        <a href="/mythology-lab" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Lab
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Safety Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Myth Patterns"
          value={stats.total_patterns || 10}
          icon={AlertTriangle}
          color="text-accent-amber"
        />
        <StatCard
          label="Active Guards"
          value={stats.active_guards || 8}
          icon={Shield}
          color="text-accent-green"
        />
        <StatCard
          label="Flagged Today"
          value={stats.flagged_today || 0}
          icon={AlertTriangle}
          color="text-red-400"
        />
        <StatCard
          label="Block Rate"
          value={`${stats.blocked_rate || 0}%`}
          icon={CheckCircle}
          color="text-primary-400"
        />
      </div>

      {/* Recent Events */}
      {events.length > 0 && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Events</h4>
          <div className="space-y-2">
            {events.map((event: any) => (
              <EventRow key={event.id} event={event} />
            ))}
          </div>
        </div>
      )}

      {/* Protection Features */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Protection Features</h4>
        <div className="space-y-2">
          <FeatureRow
            label="Hallucination Detection"
            status="active"
            description="Pattern-based myth detection"
          />
          <FeatureRow
            label="Content Guardrails"
            status="active"
            description="8 active mythology guards"
          />
          <FeatureRow
            label="Safety Classification"
            status="active"
            description="Memory safety levels"
          />
          <FeatureRow
            label="Poison Risk Scoring"
            status="active"
            description="Learning content validation"
          />
        </div>
      </div>
    </div>
  )
}

// ============ Collective Intelligence Sub-Tab ============

function CollectiveSubTab() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['collective-dashboard-tab'],
    queryFn: async () => {
      const res = await collectiveApi.dashboard()
      return res.data
    },
  })

  const { data: networkData } = useQuery({
    queryKey: ['collective-network-tab'],
    queryFn: async () => {
      const res = await collectiveApi.network()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const dashboard = dashboardData || {
    total_agents: 74,
    knowledge_items: 0,
    active_collaborations: 0,
  }
  const network = networkData || { connections: 0, clusters: 0 }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Collective Intelligence</h3>
        <a href="/collective-intelligence" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Network
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Network Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Agents"
          value={dashboard.total_agents || 74}
          icon={Users}
          color="text-primary-400"
        />
        <StatCard
          label="Knowledge Items"
          value={dashboard.knowledge_items || 0}
          icon={BookOpen}
          color="text-accent-green"
        />
        <StatCard
          label="Connections"
          value={network.connections || 0}
          icon={Network}
          color="text-accent-purple"
        />
        <StatCard
          label="Clusters"
          value={network.clusters || 0}
          icon={Activity}
          color="text-accent-amber"
        />
      </div>

      {/* Collective Features */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Knowledge Sharing</h4>
        <div className="space-y-2">
          <FeatureRow
            label="Cross-Agent Learning"
            status="active"
            description="Pattern sharing between agents"
          />
          <FeatureRow
            label="Knowledge Gaps"
            status="active"
            description="Identify missing expertise"
          />
          <FeatureRow
            label="Emergent Insights"
            status="active"
            description="Multi-agent synthesis"
          />
          <FeatureRow
            label="Wisdom Injection"
            status="active"
            description="25 advisor personas active"
          />
        </div>
      </div>

      {/* Agent Categories */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Agent Ecosystem</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <CategoryBadge name="Creation" count={4} />
          <CategoryBadge name="Research" count={3} />
          <CategoryBadge name="Strategy" count={8} />
          <CategoryBadge name="Development" count={5} />
          <CategoryBadge name="Analysis" count={6} />
          <CategoryBadge name="Executive" count={4} />
          <CategoryBadge name="Blockchain" count={5} />
          <CategoryBadge name="Other" count={39} />
        </div>
      </div>
    </div>
  )
}

// ============ Helper Components ============

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="animate-spin text-primary-400" size={24} />
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
  icon: typeof Brain
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

function PendingActionRow({ action }: { action: any }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex items-center gap-3">
        <Clock size={14} className="text-accent-amber" />
        <div>
          <span className="text-sm font-medium">{action.action_type || 'Action'}</span>
          <p className="text-xs text-gray-500">
            {action.created_at ? new Date(action.created_at).toLocaleString() : 'Pending'}
          </p>
        </div>
      </div>
      <a
        href={`/reasoning-engine?action=${action.id}`}
        className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30"
      >
        Review
      </a>
    </div>
  )
}

function EventRow({ event }: { event: any }) {
  const severityColors: Record<string, { bg: string; color: string }> = {
    low: { bg: 'bg-gray-500/20', color: 'text-gray-400' },
    medium: { bg: 'bg-accent-amber/20', color: 'text-accent-amber' },
    high: { bg: 'bg-red-500/20', color: 'text-red-400' },
  }
  const style = severityColors[event.severity] || severityColors.low

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex items-center gap-3">
        <AlertTriangle size={14} className={style.color} />
        <div>
          <span className="text-sm">{event.pattern_name || 'Unknown Pattern'}</span>
          <p className="text-xs text-gray-500">{event.agent_name}</p>
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize', style.bg, style.color)}>
        {event.severity}
      </span>
    </div>
  )
}

function PipelineRow({
  label,
  description,
}: {
  label: string
  description: string
}) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
      <CheckCircle size={14} className="text-accent-green" />
      <div>
        <span className="text-sm">{label}</span>
        <p className="text-xs text-gray-500">{description}</p>
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

function CategoryBadge({ name, count }: { name: string; count: number }) {
  return (
    <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-800/50">
      <span className="text-xs text-gray-400">{name}</span>
      <span className="text-xs font-medium">{count}</span>
    </div>
  )
}
