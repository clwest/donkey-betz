// Session 825: Command Tab - Platform Command Center
// Extracted from WorkspacePage.tsx for modular architecture

// Session 825: Command Tab - Platform Command Center
// Extracted from WorkspacePage.tsx for modular architecture
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Activity,
  Shield,
  Heart,
  BookOpen,
  Zap,
  ChevronRight,
  ChevronDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Hash,
  Wrench,
  X,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi, humanApi } from '@/lib/api'
import {
  MissionCard,
  MetricsGrid,
  LiveMetricsDashboard,
  TriggerRulesPanel,
  ActionsPanel,
} from '@/components/platform'
import type { WorkspaceTab } from '../types'

interface CommandTabProps {
  setActiveTab: (tab: WorkspaceTab) => void
  expandedActivityIds: Set<string>
  toggleActivityExpanded: (id: string) => void
}

export function CommandTab({
  setActiveTab,
  expandedActivityIds,
  toggleActivityExpanded,
}: CommandTabProps) {
  const queryClient = useQueryClient()

  // Queries
  const { data: missionData, isLoading: loadingMission } = useQuery({
    queryKey: ['platform-mission'],
    queryFn: async () => {
      const res = await platformApi.mission()
      return res.data
    },
  })

  const { data: metricsData } = useQuery({
    queryKey: ['platform-metrics'],
    queryFn: async () => {
      const res = await platformApi.metrics()
      return res.data
    },
  })

  const { data: governanceData } = useQuery({
    queryKey: ['platform-governance'],
    queryFn: async () => {
      const res = await platformApi.governance()
      return res.data
    },
  })

  // Decision mutation
  const decisionMutation = useMutation({
    mutationFn: async ({ itemId, decision }: { itemId: string; decision: string }) => {
      const res = await humanApi.decide(itemId, decision)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
      queryClient.invalidateQueries({ queryKey: ['human-attention'] })
    },
  })

  return (
    <div className="space-y-6">
      {/* Mission Card */}
      <MissionCard mission={missionData?.mission} isLoading={loadingMission} />

      {/* Metrics Grid */}
      <MetricsGrid
        metrics={missionData?.metrics_summary}
        isLoading={loadingMission}
        onRevenueClick={() => (window.location.href = '/human?tab=revenue')}
        onCostClick={() => (window.location.href = '/analytics')}
        onCanonClick={() => setActiveTab('knowledge')}
        onPlaybooksClick={() => setActiveTab('knowledge')}
      />

      {/* Quick Actions */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="text-accent-amber" size={18} />
          <h3 className="text-md font-semibold uppercase">Quick Actions</h3>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setActiveTab('governance')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <Shield size={16} className="text-accent-blue" />
            View Governance
          </button>
          <a
            href="/human"
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <Heart size={16} className="text-accent-red" />
            System Health
          </a>
          <button
            onClick={() => setActiveTab('knowledge')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <BookOpen size={16} className="text-accent-purple" />
            Browse Knowledge
          </button>
        </div>
      </div>

      {/* Live Metrics Dashboard */}
      <LiveMetricsDashboard />

      {/* Trigger Rules Panel */}
      <TriggerRulesPanel />

      {/* Actions Panel */}
      <ActionsPanel />

      {/* Recent Activity Feed */}
      {metricsData?.recent_activity && metricsData.recent_activity.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="text-primary-400" size={18} />
              <h3 className="text-md font-semibold uppercase">Recent Activity</h3>
              <span className="text-xs text-gray-500">
                ({metricsData.recent_activity.length})
              </span>
            </div>
            <a
              href="/agents"
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              View All Agents
              <ChevronRight size={12} />
            </a>
          </div>
          <div className="space-y-2">
            {metricsData.recent_activity.map((activity: any) => (
              <ActivityCard
                key={activity.id}
                activity={activity}
                isExpanded={expandedActivityIds.has(activity.id)}
                onToggle={() => toggleActivityExpanded(activity.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Pending Decisions Preview */}
      {governanceData?.pending_decisions &&
        governanceData.pending_decisions.length > 0 && (
          <div className="card border border-accent-amber/30">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="text-accent-amber" size={18} />
                <h3 className="text-md font-semibold uppercase">
                  Pending Decisions ({governanceData.pending_decisions_count})
                </h3>
              </div>
              <a
                href="/human?tab=attention"
                className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
              >
                View All
                <ChevronRight size={12} />
              </a>
            </div>
            <div className="space-y-3">
              {governanceData.pending_decisions.slice(0, 3).map((decision: any) => (
                <DecisionCard
                  key={decision.id}
                  decision={decision}
                  onApprove={() =>
                    decisionMutation.mutate({ itemId: decision.id, decision: 'approve' })
                  }
                  onDismiss={() =>
                    decisionMutation.mutate({ itemId: decision.id, decision: 'dismiss' })
                  }
                  isLoading={decisionMutation.isPending}
                />
              ))}
            </div>
          </div>
        )}
    </div>
  )
}

// Activity Card sub-component
interface ActivityCardProps {
  activity: any
  isExpanded: boolean
  onToggle: () => void
}

function ActivityCard({ activity, isExpanded, onToggle }: ActivityCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg transition-all',
        isExpanded ? 'bg-gray-800' : 'bg-gray-800/50 hover:bg-gray-800'
      )}
    >
      {/* Header Row */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 cursor-pointer"
      >
        <div className="flex items-center gap-3">
          {activity.success ? (
            <CheckCircle size={14} className="text-accent-green" />
          ) : (
            <XCircle size={14} className="text-accent-red" />
          )}
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="text-sm text-white">{activity.agent_name}</span>
              {activity.agent_category && (
                <span className="text-xs px-1.5 py-0.5 bg-primary-500/20 text-primary-400 rounded">
                  {activity.agent_category}
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500 truncate max-w-md">{activity.task}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {activity.execution_time_ms && (
            <span className="text-xs text-gray-500">{activity.execution_time_ms}ms</span>
          )}
          {activity.completed_at && (
            <span className="text-xs text-gray-500">
              {new Date(activity.completed_at).toLocaleString()}
            </span>
          )}
          {isExpanded ? (
            <ChevronDown size={14} className="text-primary-400" />
          ) : (
            <ChevronRight size={14} className="text-gray-600" />
          )}
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-3 pb-3 space-y-3 border-t border-gray-700/50">
          {/* Full Task */}
          <div className="pt-3">
            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Task</h4>
            <p className="text-sm text-gray-300">{activity.task_full || activity.task}</p>
          </div>

          {/* Metrics Row */}
          <div className="flex flex-wrap gap-4 text-xs">
            {activity.execution_time_ms && (
              <div className="flex items-center gap-1">
                <Clock size={12} className="text-gray-500" />
                <span className="text-gray-400">Duration:</span>
                <span className="text-white">{activity.execution_time_ms}ms</span>
              </div>
            )}
            {activity.tokens_used > 0 && (
              <div className="flex items-center gap-1">
                <Hash size={12} className="text-gray-500" />
                <span className="text-gray-400">Tokens:</span>
                <span className="text-white">{activity.tokens_used.toLocaleString()}</span>
              </div>
            )}
            {activity.cost > 0 && (
              <div className="flex items-center gap-1">
                <span className="text-gray-400">Cost:</span>
                <span className="text-accent-green">${activity.cost.toFixed(4)}</span>
              </div>
            )}
          </div>

          {/* Error Message */}
          {activity.error_message && (
            <div className="p-2 bg-accent-red/10 rounded border border-accent-red/30">
              <h4 className="text-xs font-semibold text-accent-red uppercase mb-1">Error</h4>
              <p className="text-xs text-gray-300">{activity.error_message}</p>
            </div>
          )}

          {/* Output Summary */}
          {activity.output_summary && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Output</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">
                {activity.output_summary}
              </p>
            </div>
          )}

          {/* Tool Results */}
          {activity.tool_results && activity.tool_results.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">
                Tools Used
              </h4>
              <div className="flex flex-wrap gap-2">
                {activity.tool_results.map(
                  (tool: string | { name?: string; tool?: string }, idx: number) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded flex items-center gap-1"
                    >
                      <Wrench size={10} />
                      {typeof tool === 'string'
                        ? tool
                        : tool.name || tool.tool || 'Unknown'}
                    </span>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Decision Card sub-component
interface DecisionCardProps {
  decision: any
  onApprove: () => void
  onDismiss: () => void
  isLoading: boolean
}

function DecisionCard({ decision, onApprove, onDismiss, isLoading }: DecisionCardProps) {
  return (
    <div className="p-4 bg-gray-800/50 hover:bg-gray-800/80 rounded-lg transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-white truncate">{decision.title}</h4>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-gray-500">
              {decision.source_agent || decision.source_type}
            </span>
            {decision.ml_recommendation && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400">
                AI: {decision.ml_recommendation}
              </span>
            )}
          </div>
        </div>
        <span
          className={cn(
            'text-xs px-2 py-0.5 rounded flex-shrink-0 ml-2',
            decision.urgency === 'critical'
              ? 'bg-accent-red/20 text-accent-red'
              : decision.urgency === 'high'
              ? 'bg-accent-amber/20 text-accent-amber'
              : 'bg-gray-700 text-gray-400'
          )}
        >
          {decision.urgency}
        </span>
      </div>
      <div className="flex items-center gap-2 mt-3">
        <button
          onClick={onApprove}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-green/20 hover:bg-accent-green/30 text-accent-green rounded text-xs font-medium transition-colors disabled:opacity-50"
        >
          <CheckCircle size={12} />
          Approve
        </button>
        <button
          onClick={onDismiss}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-xs font-medium transition-colors disabled:opacity-50"
        >
          <X size={12} />
          Dismiss
        </button>
        <a
          href={`/human?tab=attention&item=${decision.id}`}
          className="flex items-center gap-1.5 px-3 py-1.5 text-gray-400 hover:text-white text-xs transition-colors ml-auto"
        >
          View Details
          <ChevronRight size={12} />
        </a>
      </div>
    </div>
  )
}
