import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { intelligenceApi, pilotsApi, experimentsApi, learningApi, spidersApi, agentsApi, opportunitiesApi } from '@/lib/api'
import {
  Brain, TrendingUp, AlertTriangle, Zap, CheckCircle, XCircle,
  Play, Pause, RefreshCw, ChevronRight, Loader2, Activity,
  BookOpen, Target, BarChart3, Globe, Bot, Sparkles, X, ExternalLink,
  Rocket, Ban, DollarSign, Clock, Users, Wrench, Lightbulb, FileText, Flag,
  Trash2
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'gates' | 'pilots' | 'experiments' | 'learning' | 'activity' | 'spiders' | 'predictions' | 'agents'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface Gate {
  id: string
  decision_topic: string
  summary: string
  status: string  // not_started, in_progress, ready, approved, blocked, waived
  status_display: string
  risk_level: string
  checklist_percentage: number
  checklist_total: number
  checklist_completed: number
  created_at?: string
  running_pilot?: {
    id: string
    name: string
    status: string
    hours_running: number
    started_at: string
  } | null
}

interface Pilot {
  id: string
  gate_id: string
  decision_topic: string
  decision_type: string
  status: string  // running, completed, failed, etc.
  risk_level: string
  hours_running?: number
  auto_complete_in_hours?: number
  outcome?: string
  started_at?: string
  completed_at?: string
  duration_hours?: number
  kill_switch_triggered?: boolean
  thinking_agent_evaluation?: string | null
  learnings?: Array<{
    type: string
    outcome: string
    confidence: number
    impact_area: string
    decision_type: string
    hours_running: number
  }>
  // Session 690: Implementation status
  implementation?: {
    id: string
    status: string  // pending, in_progress, completed, failed, requires_human
    type: string    // agent_update, code_generation, workflow_update, etc.
    executed_by?: string
    completed_at?: string
  } | null
}

// Session 691: Full implementation details for review modal
interface ImplementationDetail {
  id: string
  pilot_id: string
  type: string
  status: string
  target_description: string
  plan: {
    steps?: string[]
    rationale?: string
    impact_area?: string
    key_insights?: string[]
    decision_type?: string
    suggested_feature?: string
    recommended_action?: string
  }
  executed_by: string
  result: {
    requires_human_reason?: string
    success?: boolean
    summary?: string
    actions?: Array<{
      type: string
      description: string
      success: boolean
    }>
  }
  artifacts: string[]
  error: string
  created_at: string
  started_at: string | null
  completed_at: string | null
}

interface PilotMetrics {
  total_pilots: number
  running_count: number
  completed_count: number
  success_count: number
  failure_count: number
  partial_count: number
  success_rate: number
  avg_duration_hours: number
}

interface Experiment {
  id: string
  name: string
  status: 'active' | 'completed' | 'halted'
  kpi_current: number
  kpi_target: number
  pilot_name: string
}

interface LearningEvent {
  id?: string
  agent_name: string  // Mapped from source or teacher
  event_type: string  // Mapped from type
  description: string
  timestamp: string
  // Session 688: Additional fields from API
  teacher?: string
  student?: string
  source?: string
  type?: string
}

interface Spider {
  name: string
  status: 'active' | 'inactive' | 'error'
  last_run: string
  items_collected: number
  category: string
}

interface Prediction {
  id: string
  title: string
  probability: number
  category: string
  source: string
  created_at: string
}

interface Agent {
  name: string
  display_name: string
  status: 'healthy' | 'degraded' | 'offline'
  executions_today: number
  last_execution: string
}

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

export default function IntelligencePage() {
  const [activeTab, setActiveTab] = useState<TabType>('gates')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [selectedGate, setSelectedGate] = useState<string | null>(null)
  // Session 688: Opportunity modal state
  const [selectedOpportunityId, setSelectedOpportunityId] = useState<string | null>(null)
  // Session 689: Pilot detail modal state
  const [selectedPilotId, setSelectedPilotId] = useState<string | null>(null)
  // Session 691: Implementation review modal state
  const [selectedImplementationId, setSelectedImplementationId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Core queries
  const { data: statusData, isLoading: loadingStatus } = useQuery({
    queryKey: ['intelligence-status'],
    queryFn: () => intelligenceApi.status(),
  })

  const { data: opportunitiesData } = useQuery({
    queryKey: ['intelligence-opportunities'],
    queryFn: () => intelligenceApi.opportunities(),
  })

  // Session 688: Fetch opportunity detail when selected
  const { data: opportunityDetailData, isLoading: loadingOpportunityDetail } = useQuery({
    queryKey: ['opportunity-detail', selectedOpportunityId],
    queryFn: () => opportunitiesApi.detail(selectedOpportunityId!),
    enabled: !!selectedOpportunityId,
  })

  // Session 689: Fetch gate detail when selected (for modal)
  const { data: gateDetailData, isLoading: loadingGateDetail } = useQuery({
    queryKey: ['gate-detail', selectedGate],
    queryFn: () => pilotsApi.gateDetail(selectedGate!),
    enabled: !!selectedGate,
  })

  // Tab-specific queries
  const { data: gatesData, isLoading: loadingGates } = useQuery({
    queryKey: ['pilot-gates'],
    queryFn: () => pilotsApi.gates(),
    enabled: activeTab === 'gates',
  })

  const { data: pilotsData, isLoading: loadingPilots } = useQuery({
    queryKey: ['pilots-dashboard'],
    queryFn: () => pilotsApi.dashboard(),
    enabled: activeTab === 'pilots',
    staleTime: 0,  // Session 692: Always fetch fresh data
    refetchOnMount: 'always',  // Session 692: Refetch when tab becomes active
  })

  // Session 689: Fetch gate detail for pilot modal (to get rich decision context)
  const selectedPilot = selectedPilotId ? [...(pilotsData?.data?.running_pilots || []).map((p: Pilot) => ({ ...p, status: 'running' })), ...(pilotsData?.data?.completed_pilots || []).map((p: Pilot) => ({ ...p, status: 'completed' }))].find(p => p.id === selectedPilotId) : null
  const { data: pilotGateDetailData, isLoading: loadingPilotGateDetail } = useQuery({
    queryKey: ['pilot-gate-detail', selectedPilot?.gate_id],
    queryFn: () => pilotsApi.gateDetail(selectedPilot!.gate_id),
    enabled: !!selectedPilot?.gate_id,
  })

  // Session 691: Fetch implementation details for review modal
  const { data: implementationDetailData, isLoading: loadingImplementation } = useQuery({
    queryKey: ['implementation-detail', selectedImplementationId],
    queryFn: () => pilotsApi.implementationDetail(selectedImplementationId!),
    enabled: !!selectedImplementationId,
  })
  const implementationDetail: ImplementationDetail | null = implementationDetailData?.data?.implementation || null

  const { data: experimentsData, isLoading: loadingExperiments } = useQuery({
    queryKey: ['experiments-list'],
    queryFn: () => experimentsApi.list(),
    enabled: activeTab === 'experiments',
  })

  const { data: learningData, isLoading: loadingLearning } = useQuery({
    queryKey: ['learning-activity'],
    queryFn: () => learningApi.activity(),
    enabled: activeTab === 'learning' || activeTab === 'activity',
  })

  // Spider Network
  const { data: spidersData, isLoading: loadingSpiders } = useQuery({
    queryKey: ['spider-status'],
    queryFn: () => spidersApi.status(),
    enabled: activeTab === 'spiders',
  })

  // Predictions
  const { data: predictionsData, isLoading: loadingPredictions } = useQuery({
    queryKey: ['predictions'],
    queryFn: () => intelligenceApi.predictions(),
    enabled: activeTab === 'predictions',
  })

  // Session 688: Use agents list endpoint instead of health (which returns system stats, not agent array)
  const { data: agentsListData, isLoading: loadingAgents } = useQuery({
    queryKey: ['agents-list'],
    queryFn: () => agentsApi.list(),
    enabled: activeTab === 'agents',
  })

  // Mutations
  const approveGateMutation = useMutation({
    mutationFn: (gateId: string) => pilotsApi.updateGateStatus(gateId, 'approve', 'Approved via UI'),
    onSuccess: async () => {
      setActionResult({ type: 'success', message: 'Gate approved! Ready to start pilot.' })
      // Force immediate refetch to update UI with new status
      await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to approve gate' })
    },
  })

  const startPilotMutation = useMutation({
    mutationFn: (gateId: string) => pilotsApi.startPilot(gateId),
    onSuccess: async () => {
      setActionResult({ type: 'success', message: 'Pilot started successfully!' })
      // Force immediate refetch to update UI
      await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
      await queryClient.refetchQueries({ queryKey: ['pilots-dashboard'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to start pilot' })
    },
  })

  const haltExperimentMutation = useMutation({
    mutationFn: (experimentId: string) => experimentsApi.halt(experimentId, 'Manual halt from Command Center'),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Experiment halted' })
      queryClient.invalidateQueries({ queryKey: ['experiments-list'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to halt experiment' })
    },
  })

  const triggerKpiUpdateMutation = useMutation({
    mutationFn: () => experimentsApi.triggerKpiUpdate(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'KPI update triggered for all experiments' })
      queryClient.invalidateQueries({ queryKey: ['experiments-list'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to trigger KPI update' })
    },
  })

  // Session 688: Opportunity action mutations
  const actOnOpportunityMutation = useMutation({
    mutationFn: (id: string) => opportunitiesApi.act(id),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Opportunity marked as in-progress!' })
      setSelectedOpportunityId(null)
      queryClient.invalidateQueries({ queryKey: ['intelligence-opportunities'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to update opportunity' })
    },
  })

  const dismissOpportunityMutation = useMutation({
    mutationFn: (id: string) => opportunitiesApi.dismiss(id, 'Dismissed from UI'),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Opportunity dismissed' })
      setSelectedOpportunityId(null)
      queryClient.invalidateQueries({ queryKey: ['intelligence-opportunities'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to dismiss opportunity' })
    },
  })

  const status = statusData?.data || {}
  const opportunities = opportunitiesData?.data?.opportunities || []
  const gates: Gate[] = gatesData?.data?.gates || []
  // Pilots API returns running_pilots, completed_pilots, and metrics separately
  const runningPilots: Pilot[] = (pilotsData?.data?.running_pilots || []).map((p: Pilot) => ({ ...p, status: 'running' }))
  const completedPilots: Pilot[] = (pilotsData?.data?.completed_pilots || []).map((p: Pilot) => ({ ...p, status: 'completed' }))
  const pilots: Pilot[] = [...runningPilots, ...completedPilots]
  const pilotMetrics: PilotMetrics = pilotsData?.data?.metrics || {
    total_pilots: 0, running_count: 0, completed_count: 0,
    success_count: 0, failure_count: 0, partial_count: 0,
    success_rate: 0, avg_duration_hours: 0
  }
  // Session 689: Get gate decision data for pilot modal
  const pilotGateDecision = pilotGateDetailData?.data?.gate?.decision || null
  const experiments: Experiment[] = experimentsData?.data?.experiments || []
  // Session 688: API returns feed_items with different field names - map them
  const rawLearningEvents = learningData?.data?.feed_items || learningData?.data?.events || []
  const learningEvents: LearningEvent[] = rawLearningEvents.map((e: { timestamp: string; type?: string; source?: string; teacher?: string; description?: string }, idx: number) => ({
    ...e,
    id: `learning-${idx}`,
    agent_name: e.source || e.teacher || 'Unknown Agent',
    event_type: e.type || 'activity',
    description: e.description || '',
    timestamp: e.timestamp,
  }))
  const spiders: Spider[] = spidersData?.data?.spiders || []
  const predictions: Prediction[] = predictionsData?.data?.predictions || []
  // Session 688: Use list API and map to expected format
  const agentsRaw = agentsListData?.data?.agents || []
  const agents: Agent[] = agentsRaw.map((a: { name: string; isActive: boolean; totalExecutions: number; lastActive: string }) => ({
    name: a.name,
    display_name: a.name.replace(/Agent$/, '').replace(/([A-Z])/g, ' $1').trim(),
    status: a.isActive ? 'healthy' : 'offline',
    executions_today: a.totalExecutions,
    last_execution: a.lastActive,
  }))

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const isLoading = approveGateMutation.isPending || startPilotMutation.isPending ||
                    haltExperimentMutation.isPending || triggerKpiUpdateMutation.isPending

  if (loadingStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  const tabs: { key: TabType; label: string; icon: React.ElementType; count?: number }[] = [
    { key: 'gates', label: 'Gates', icon: Target, count: gates.filter(g => ['not_started', 'in_progress', 'ready'].includes(g.status)).length },
    { key: 'pilots', label: 'Pilots', icon: Play, count: pilots.filter(p => p.status === 'running').length },
    { key: 'experiments', label: 'Experiments', icon: BarChart3, count: experiments.filter(e => e.status === 'active').length },
    { key: 'spiders', label: 'Spiders', icon: Globe, count: spiders.filter(s => s.status === 'active').length },
    { key: 'predictions', label: 'Predictions', icon: Sparkles },
    { key: 'agents', label: 'Agents', icon: Bot },
    { key: 'learning', label: 'Learning', icon: BookOpen },
    { key: 'activity', label: 'Activity', icon: Activity },
  ]

  return (
    <div className="space-y-6">
      {/* Command Center Header */}
      <div className="card bg-gradient-to-r from-primary-900/50 to-primary-800/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-lg bg-primary-600/20 flex items-center justify-center">
              <Brain size={32} className="text-primary-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Intelligence Command Center</h2>
              <p className="text-gray-400">
                Real-time intelligence from {status.spider_count || 77} spiders
              </p>
            </div>
          </div>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => {
              queryClient.invalidateQueries()
              setActionResult({ type: 'success', message: 'Refreshing all data...' })
            }}
          >
            <RefreshCw size={16} />
            Refresh All
          </button>
        </div>
      </div>

      {/* Sub-tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-4">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === tab.key
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-card'
            )}
          >
            <tab.icon size={16} />
            {tab.label}
            {tab.count !== undefined && tab.count > 0 && (
              <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-accent-amber/20 text-accent-amber">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <TrendingUp className="text-accent-green" size={24} />
            <div>
              <p className="text-sm text-gray-400">Opportunities</p>
              <p className="text-2xl font-bold">{opportunities.length || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Target className="text-accent-cyan" size={24} />
            <div>
              <p className="text-sm text-gray-400">Pending Gates</p>
              <p className="text-2xl font-bold">{gates.filter(g => ['not_started', 'in_progress', 'ready'].includes(g.status)).length || status.pending_gates || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Zap className="text-accent-amber" size={24} />
            <div>
              <p className="text-sm text-gray-400">Running Pilots</p>
              <p className="text-2xl font-bold">{pilots.filter(p => p.status === 'running').length || status.running_pilots || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <BarChart3 className="text-primary-400" size={24} />
            <div>
              <p className="text-sm text-gray-400">Active Experiments</p>
              <p className="text-2xl font-bold">{experiments.filter(e => e.status === 'active').length || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'gates' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Pilot Readiness Gates</h3>
          </div>
          {loadingGates ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin" size={24} />
            </div>
          ) : gates.length > 0 ? (
            <div className="space-y-3">
              {gates.map((gate) => (
                <div
                  key={gate.id}
                  className={cn(
                    'flex items-center justify-between p-4 rounded-lg border transition-colors cursor-pointer',
                    selectedGate === gate.id ? 'border-primary-500 bg-primary-500/10' : 'border-dark-border hover:border-gray-600'
                  )}
                  onClick={() => setSelectedGate(selectedGate === gate.id ? null : gate.id)}
                >
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      'h-10 w-10 rounded-lg flex items-center justify-center',
                      gate.status === 'approved' || gate.status === 'waived' ? 'bg-accent-green/20' :
                      gate.status === 'blocked' ? 'bg-accent-red/20' : 'bg-accent-amber/20'
                    )}>
                      {gate.status === 'approved' || gate.status === 'waived' ? (
                        <CheckCircle size={20} className="text-accent-green" />
                      ) : gate.status === 'blocked' ? (
                        <AlertTriangle size={20} className="text-accent-red" />
                      ) : (
                        <Target size={20} className="text-accent-amber" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{gate.decision_topic || gate.summary}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{gate.status_display || gate.status}</span>
                        <div className="w-24 h-1.5 bg-dark-bg rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-500 rounded-full"
                            style={{ width: `${gate.checklist_percentage || 0}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">{gate.checklist_completed}/{gate.checklist_total}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {/* not_started → Start Gate */}
                    {gate.status === 'not_started' && (
                      <button
                        className="btn btn-secondary text-sm flex items-center gap-1"
                        onClick={async (e) => {
                          e.stopPropagation()
                          try {
                            await pilotsApi.updateGateStatus(gate.id, 'start')
                            setActionResult({ type: 'success', message: 'Gate started!' })
                            await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                          } catch {
                            setActionResult({ type: 'error', message: 'Failed to start gate' })
                          }
                        }}
                        disabled={isLoading}
                      >
                        <Play size={14} />
                        Start Gate
                      </button>
                    )}
                    {/* in_progress → Mark Ready */}
                    {/* Session 692: Show Mark Ready only when checklist is reasonably complete */}
                    {gate.status === 'in_progress' && (
                      <button
                        className={cn(
                          "btn text-sm flex items-center gap-1",
                          gate.checklist_percentage >= 50 ? "btn-secondary" : "btn-secondary opacity-50"
                        )}
                        onClick={async (e) => {
                          e.stopPropagation()
                          try {
                            const response = await pilotsApi.updateGateStatus(gate.id, 'ready')
                            // Session 692: Check response.data.success since API returns 200 even on failure
                            if (response.data?.success === false) {
                              setActionResult({ type: 'error', message: response.data?.message || 'Checklist incomplete' })
                            } else {
                              setActionResult({ type: 'success', message: 'Gate marked ready!' })
                              await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                            }
                          } catch {
                            setActionResult({ type: 'error', message: 'Failed to mark ready' })
                          }
                        }}
                        disabled={isLoading}
                        title={gate.checklist_percentage < 50 ? `Checklist ${gate.checklist_percentage}% complete - needs more items` : 'Mark gate as ready for approval'}
                      >
                        <CheckCircle size={14} />
                        Mark Ready {gate.checklist_percentage < 100 && `(${Math.round(gate.checklist_percentage)}%)`}
                      </button>
                    )}
                    {/* ready → Approve */}
                    {gate.status === 'ready' && (
                      <button
                        className="btn btn-secondary text-sm flex items-center gap-1"
                        onClick={(e) => {
                          e.stopPropagation()
                          approveGateMutation.mutate(gate.id)
                        }}
                        disabled={isLoading}
                      >
                        {approveGateMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle size={14} />}
                        Approve
                      </button>
                    )}
                    {/* approved + no running pilot → Start Pilot */}
                    {gate.status === 'approved' && !gate.running_pilot && (
                      <button
                        className="btn btn-primary text-sm flex items-center gap-1"
                        onClick={(e) => {
                          e.stopPropagation()
                          startPilotMutation.mutate(gate.id)
                        }}
                        disabled={isLoading}
                      >
                        {startPilotMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                        Start Pilot
                      </button>
                    )}
                    {/* approved + running pilot → Show pilot status */}
                    {gate.status === 'approved' && gate.running_pilot && (
                      <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green flex items-center gap-1">
                        <Play size={12} />
                        Pilot Running ({gate.running_pilot.hours_running}h)
                      </span>
                    )}
                    <ChevronRight size={16} className="text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Target className="mx-auto mb-2" size={32} />
              <p>No pending gates</p>
              <p className="text-sm text-gray-500 mt-1">Gates will appear when decisions need validation</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'pilots' && (
        <div className="space-y-6">
          {/* Pilots Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <Play className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Running</p>
                  <p className="text-2xl font-bold">{pilotMetrics.running_count}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <CheckCircle className="text-accent-cyan" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Completed</p>
                  <p className="text-2xl font-bold">{pilotMetrics.completed_count}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <TrendingUp className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Success Rate</p>
                  <p className="text-2xl font-bold">{pilotMetrics.success_rate.toFixed(0)}%</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Clock className="text-primary-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Avg Duration</p>
                  <p className="text-2xl font-bold">{pilotMetrics.avg_duration_hours.toFixed(1)}h</p>
                </div>
              </div>
            </div>
          </div>

          {loadingPilots ? (
            <div className="card">
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            </div>
          ) : (
            <>
              {/* Running Pilots Section */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Play size={20} className="text-accent-green" />
                  Running Pilots ({runningPilots.length})
                </h3>
                {runningPilots.length > 0 ? (
                  <div className="space-y-3">
                    {runningPilots.map((pilot) => {
                      const progressPercent = pilot.auto_complete_in_hours && pilot.hours_running !== undefined
                        ? Math.min(100, (pilot.hours_running / (pilot.hours_running + pilot.auto_complete_in_hours)) * 100)
                        : 0
                      return (
                        <div
                          key={pilot.id}
                          className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                          onClick={() => setSelectedPilotId(pilot.id)}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <p className="font-medium">{pilot.decision_topic}</p>
                              <div className="flex items-center gap-2 mt-2 flex-wrap">
                                <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
                                  {pilot.decision_type}
                                </span>
                                <span className={cn(
                                  'text-xs px-2 py-0.5 rounded',
                                  pilot.risk_level === 'high' || pilot.risk_level === 'critical'
                                    ? 'bg-accent-red/20 text-accent-red'
                                    : pilot.risk_level === 'medium'
                                    ? 'bg-accent-amber/20 text-accent-amber'
                                    : 'bg-accent-green/20 text-accent-green'
                                )}>
                                  {pilot.risk_level} risk
                                </span>
                                {pilot.kill_switch_triggered && (
                                  <span className="text-xs px-2 py-0.5 rounded bg-accent-red/20 text-accent-red flex items-center gap-1">
                                    <AlertTriangle size={12} /> Kill Switch
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium text-accent-green">
                                {pilot.hours_running?.toFixed(1)}h running
                              </p>
                              <p className="text-xs text-gray-500">
                                {pilot.auto_complete_in_hours?.toFixed(1)}h remaining
                              </p>
                            </div>
                          </div>
                          {/* Progress Bar */}
                          <div className="mt-3">
                            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                              <span>Started {pilot.started_at ? new Date(pilot.started_at).toLocaleString() : 'Unknown'}</span>
                              <span>{progressPercent.toFixed(0)}% complete</span>
                            </div>
                            <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                              <div
                                className="h-full bg-accent-green rounded-full transition-all"
                                style={{ width: `${progressPercent}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-400">
                    <Play className="mx-auto mb-2" size={24} />
                    <p>No running pilots</p>
                    <p className="text-sm text-gray-500 mt-1">Start a pilot from the Gates tab</p>
                  </div>
                )}
              </div>

              {/* Completed Pilots Section */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <CheckCircle size={20} className="text-accent-cyan" />
                  Completed Pilots ({completedPilots.length})
                </h3>
                {completedPilots.length > 0 ? (
                  <div className="space-y-3">
                    {completedPilots.slice(0, 10).map((pilot) => {
                      const confidence = pilot.learnings?.[0]?.confidence
                      const impl = pilot.implementation
                      return (
                        <div
                          key={pilot.id}
                          className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                          onClick={() => setSelectedPilotId(pilot.id)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="font-medium">{pilot.decision_topic}</p>
                              <div className="flex items-center gap-2 mt-2 flex-wrap">
                                <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
                                  {pilot.decision_type}
                                </span>
                                <span className={cn(
                                  'text-xs px-2 py-0.5 rounded',
                                  pilot.outcome === 'success' ? 'bg-accent-green/20 text-accent-green' :
                                  pilot.outcome === 'failure' ? 'bg-accent-red/20 text-accent-red' :
                                  'bg-accent-amber/20 text-accent-amber'
                                )}>
                                  {pilot.outcome}
                                </span>
                                {confidence !== undefined && (
                                  <span className="text-xs px-2 py-0.5 rounded bg-accent-cyan/20 text-accent-cyan">
                                    {(confidence * 100).toFixed(0)}% confidence
                                  </span>
                                )}
                                {/* Session 690/691: Implementation status badge - clickable for review */}
                                {impl ? (
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      if (impl.status === 'requires_human' || impl.status === 'completed' || impl.status === 'failed') {
                                        setSelectedImplementationId(pilot.id)
                                      }
                                    }}
                                    className={cn(
                                      'text-xs px-2 py-0.5 rounded flex items-center gap-1 transition-colors',
                                      impl.status === 'completed' ? 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30' :
                                      impl.status === 'requires_human' ? 'bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30 cursor-pointer' :
                                      impl.status === 'failed' ? 'bg-accent-red/20 text-accent-red hover:bg-accent-red/30' :
                                      impl.status === 'in_progress' ? 'bg-primary-500/20 text-primary-400' :
                                      'bg-gray-500/20 text-gray-400'
                                    )}
                                    title={impl.status === 'requires_human' ? 'Click to review implementation details' : undefined}
                                  >
                                    <Wrench size={10} />
                                    {impl.status === 'completed' ? 'Implemented' :
                                     impl.status === 'requires_human' ? 'Needs Review' :
                                     impl.status === 'failed' ? 'Failed' :
                                     impl.status === 'in_progress' ? 'Implementing...' :
                                     'Pending'}
                                  </button>
                                ) : pilot.outcome === 'success' ? (
                                  <span className="text-xs px-2 py-0.5 rounded bg-gray-500/20 text-gray-400 flex items-center gap-1">
                                    <Wrench size={10} />
                                    Not Implemented
                                  </span>
                                ) : null}
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm text-gray-400">
                                {pilot.duration_hours?.toFixed(1)}h duration
                              </p>
                              <p className="text-xs text-gray-500">
                                {pilot.completed_at ? new Date(pilot.completed_at).toLocaleDateString() : ''}
                              </p>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                    {completedPilots.length > 10 && (
                      <p className="text-sm text-gray-500 text-center">
                        + {completedPilots.length - 10} more completed pilots
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-400">
                    <CheckCircle className="mx-auto mb-2" size={24} />
                    <p>No completed pilots yet</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'experiments' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Active Experiments</h3>
            <button
              className="btn btn-secondary text-sm flex items-center gap-1"
              onClick={() => triggerKpiUpdateMutation.mutate()}
              disabled={isLoading}
            >
              {triggerKpiUpdateMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
              Update All KPIs
            </button>
          </div>
          {loadingExperiments ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin" size={24} />
            </div>
          ) : experiments.length > 0 ? (
            <div className="space-y-3">
              {experiments.map((experiment) => (
                <div
                  key={experiment.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      'h-10 w-10 rounded-lg flex items-center justify-center',
                      experiment.status === 'active' ? 'bg-primary-500/20' :
                      experiment.status === 'completed' ? 'bg-accent-green/20' : 'bg-accent-red/20'
                    )}>
                      <BarChart3 size={20} className={
                        experiment.status === 'active' ? 'text-primary-400' :
                        experiment.status === 'completed' ? 'text-accent-green' : 'text-accent-red'
                      } />
                    </div>
                    <div>
                      <p className="font-medium">{experiment.name || experiment.pilot_name}</p>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-sm text-gray-400">
                          KPI: <span className={experiment.kpi_current >= experiment.kpi_target ? 'text-accent-green' : 'text-accent-amber'}>
                            {experiment.kpi_current || 0}
                          </span> / {experiment.kpi_target || 100}
                        </span>
                        <div className="w-20 h-1.5 bg-dark-bg rounded-full overflow-hidden">
                          <div
                            className={cn(
                              'h-full rounded-full',
                              experiment.kpi_current >= experiment.kpi_target ? 'bg-accent-green' : 'bg-primary-500'
                            )}
                            style={{ width: `${Math.min((experiment.kpi_current / experiment.kpi_target) * 100, 100) || 0}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'px-2 py-1 text-xs rounded',
                      experiment.status === 'active' ? 'bg-primary-500/20 text-primary-400' :
                      experiment.status === 'completed' ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-red/20 text-accent-red'
                    )}>
                      {experiment.status}
                    </span>
                    {experiment.status === 'active' && (
                      <button
                        className="btn btn-secondary text-sm text-accent-red flex items-center gap-1"
                        onClick={() => haltExperimentMutation.mutate(experiment.id)}
                        disabled={isLoading}
                      >
                        {haltExperimentMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Pause size={14} />}
                        Halt
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <BarChart3 className="mx-auto mb-2" size={32} />
              <p>No active experiments</p>
              <p className="text-sm text-gray-500 mt-1">Experiments are created when pilots complete successfully</p>
            </div>
          )}
        </div>
      )}

      {(activeTab === 'learning' || activeTab === 'activity') && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            {activeTab === 'learning' ? 'Agent Learning Feed' : 'Recent Activity'}
          </h3>
          {loadingLearning ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin" size={24} />
            </div>
          ) : learningEvents.length > 0 ? (
            <div className="space-y-3 max-h-[500px] overflow-auto">
              {learningEvents.map((event, idx) => (
                <div
                  key={event.id || idx}
                  className="flex items-start gap-3 p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                >
                  <div className="h-8 w-8 rounded-full bg-accent-cyan/20 flex items-center justify-center flex-shrink-0">
                    <BookOpen size={14} className="text-accent-cyan" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{event.agent_name}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-accent-cyan/20 text-accent-cyan">
                        {event.event_type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mt-1">{event.description}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(event.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <BookOpen className="mx-auto mb-2" size={32} />
              <p>No learning events yet</p>
              <p className="text-sm text-gray-500 mt-1">Agent learning activity will appear here</p>
            </div>
          )}
        </div>
      )}

      {/* Spiders Tab */}
      {activeTab === 'spiders' && (
        <div className="space-y-6">
          {/* Spider Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <Globe className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Active Spiders</p>
                  <p className="text-2xl font-bold">{spiders.filter(s => s.status === 'active').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <AlertTriangle className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Inactive</p>
                  <p className="text-2xl font-bold">{spiders.filter(s => s.status === 'inactive').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <XCircle className="text-accent-red" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Errors</p>
                  <p className="text-2xl font-bold">{spiders.filter(s => s.status === 'error').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <TrendingUp className="text-primary-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Items Collected</p>
                  <p className="text-2xl font-bold">{spiders.reduce((acc, s) => acc + (s.items_collected || 0), 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Spider Grid */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Spider Network</h3>
            {loadingSpiders ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : spiders.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {spiders.map((spider, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-8 w-8 rounded-full flex items-center justify-center',
                        spider.status === 'active' ? 'bg-accent-green/20' :
                        spider.status === 'error' ? 'bg-accent-red/20' : 'bg-gray-500/20'
                      )}>
                        <Globe size={14} className={
                          spider.status === 'active' ? 'text-accent-green' :
                          spider.status === 'error' ? 'text-accent-red' : 'text-gray-400'
                        } />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{spider.name}</p>
                        <p className="text-xs text-gray-500">{spider.category}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{spider.items_collected || 0}</p>
                      <p className="text-xs text-gray-500">items</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Globe className="mx-auto mb-2" size={32} />
                <p>No spiders configured</p>
                <p className="text-sm text-gray-500 mt-1">Spider network data will appear here</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Predictions Tab */}
      {activeTab === 'predictions' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">AI Predictions</h3>
          {loadingPredictions ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin" size={24} />
            </div>
          ) : predictions.length > 0 ? (
            <div className="space-y-3">
              {predictions.map((pred, idx) => (
                <div
                  key={pred.id || idx}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      'h-10 w-10 rounded-lg flex items-center justify-center',
                      pred.probability >= 70 ? 'bg-accent-green/20' :
                      pred.probability >= 40 ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                    )}>
                      <Sparkles size={20} className={
                        pred.probability >= 70 ? 'text-accent-green' :
                        pred.probability >= 40 ? 'text-accent-amber' : 'text-accent-red'
                      } />
                    </div>
                    <div>
                      <p className="font-medium">{pred.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                          {pred.category}
                        </span>
                        <span className="text-xs text-gray-500">{pred.source}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={cn(
                      'text-xl font-bold',
                      pred.probability >= 70 ? 'text-accent-green' :
                      pred.probability >= 40 ? 'text-accent-amber' : 'text-accent-red'
                    )}>
                      {pred.probability}%
                    </p>
                    <p className="text-xs text-gray-500">probability</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Sparkles className="mx-auto mb-2" size={32} />
              <p>No predictions available</p>
              <p className="text-sm text-gray-500 mt-1">AI predictions will appear here</p>
            </div>
          )}
        </div>
      )}

      {/* Agents Tab */}
      {activeTab === 'agents' && (
        <div className="space-y-6">
          {/* Agent Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <Bot className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Healthy</p>
                  <p className="text-2xl font-bold">{agents.filter(a => a.status === 'healthy').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <AlertTriangle className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Degraded</p>
                  <p className="text-2xl font-bold">{agents.filter(a => a.status === 'degraded').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <XCircle className="text-accent-red" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Offline</p>
                  <p className="text-2xl font-bold">{agents.filter(a => a.status === 'offline').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Activity className="text-primary-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Executions Today</p>
                  <p className="text-2xl font-bold">{agents.reduce((acc, a) => acc + (a.executions_today || 0), 0)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Agent Grid */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Agent Fleet</h3>
            {loadingAgents ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : agents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {agents.map((agent, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-8 w-8 rounded-full flex items-center justify-center',
                        agent.status === 'healthy' ? 'bg-accent-green/20' :
                        agent.status === 'degraded' ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                      )}>
                        <Bot size={14} className={
                          agent.status === 'healthy' ? 'text-accent-green' :
                          agent.status === 'degraded' ? 'text-accent-amber' : 'text-accent-red'
                        } />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{agent.display_name || agent.name}</p>
                        <p className="text-xs text-gray-500">{agent.executions_today || 0} runs today</p>
                      </div>
                    </div>
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      agent.status === 'healthy' ? 'bg-accent-green/20 text-accent-green' :
                      agent.status === 'degraded' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-accent-red/20 text-accent-red'
                    )}>
                      {agent.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Bot className="mx-auto mb-2" size={32} />
                <p>No agent data available</p>
                <p className="text-sm text-gray-500 mt-1">Agent health will appear here</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Opportunities Section (always visible at bottom) */}
      {opportunities.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Latest Opportunities</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {opportunities.slice(0, 6).map((opp: { id: string; title: string; score: number; source: string }) => (
              <div
                key={opp.id}
                className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                onClick={() => setSelectedOpportunityId(opp.id)}
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium truncate">{opp.title}</p>
                  <p className="text-sm text-gray-400">{opp.source}</p>
                </div>
                <div className="text-right ml-3">
                  <p className="text-accent-green font-medium">{opp.score}%</p>
                  <p className="text-xs text-gray-500">Score</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Session 689: Gate Detail Modal */}
      {selectedGate && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-dark-card rounded-lg border border-dark-border max-w-3xl w-full max-h-[90vh] overflow-auto">
            {(() => {
              const gate = gateDetailData?.data?.gate

              if (loadingGateDetail) {
                return (
                  <div className="flex items-center justify-center py-16">
                    <Loader2 className="animate-spin" size={32} />
                  </div>
                )
              }

              if (!gate) {
                return (
                  <div className="p-6 text-center text-gray-400">
                    <AlertTriangle className="mx-auto mb-2" size={32} />
                    <p>Failed to load gate details</p>
                    <button
                      onClick={() => setSelectedGate(null)}
                      className="btn btn-secondary mt-4"
                    >
                      Close
                    </button>
                  </div>
                )
              }

              const decision = gate.decision || {}

              return (
                <>
                  {/* Modal Header */}
                  <div className="flex items-start justify-between p-6 border-b border-dark-border">
                    <div className="flex-1 min-w-0 pr-4">
                      <h3 className="text-xl font-bold">{decision.topic || gate.summary}</h3>
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        <span className={cn(
                          'text-xs px-2 py-1 rounded',
                          gate.status === 'approved' || gate.status === 'waived' ? 'bg-accent-green/20 text-accent-green' :
                          gate.status === 'blocked' ? 'bg-accent-red/20 text-accent-red' :
                          gate.status === 'in_progress' ? 'bg-accent-cyan/20 text-accent-cyan' :
                          gate.status === 'ready' ? 'bg-accent-amber/20 text-accent-amber' :
                          'bg-gray-500/20 text-gray-400'
                        )}>
                          {gate.status.replace('_', ' ')}
                        </span>
                        <span className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400">
                          {decision.decision_type || 'general'}
                        </span>
                        <span className="text-xs px-2 py-1 rounded bg-accent-cyan/20 text-accent-cyan">
                          {decision.impact_area || 'product'}
                        </span>
                        <span className={cn(
                          'text-xs px-2 py-1 rounded',
                          gate.risk_level === 'high' ? 'bg-accent-red/20 text-accent-red' :
                          gate.risk_level === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                          'bg-accent-green/20 text-accent-green'
                        )}>
                          {gate.risk_level} risk
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedGate(null)}
                      className="p-2 hover:bg-dark-bg rounded-lg transition-colors"
                    >
                      <X size={20} />
                    </button>
                  </div>

                  {/* Modal Body */}
                  <div className="p-6 space-y-6">
                    {/* Recommended Stance */}
                    {decision.recommended_stance && (
                      <div className="bg-primary-600/10 border border-primary-600/30 rounded-lg p-4">
                        <h4 className="font-semibold mb-2 flex items-center gap-2 text-primary-400">
                          <Flag size={18} />
                          Recommended Action
                        </h4>
                        <p className="text-gray-300">{decision.recommended_stance}</p>
                      </div>
                    )}

                    {/* Rationale */}
                    {decision.rationale && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <FileText size={18} className="text-accent-cyan" />
                          Rationale
                        </h4>
                        <p className="text-gray-300 text-sm">{decision.rationale}</p>
                      </div>
                    )}

                    {/* Key Insights */}
                    {decision.key_insights && decision.key_insights.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-3 flex items-center gap-2">
                          <Lightbulb size={18} className="text-accent-amber" />
                          Key Insights
                        </h4>
                        <div className="space-y-2">
                          {decision.key_insights.map((insight: string, idx: number) => (
                            <div key={idx} className="flex items-start gap-3 bg-dark-bg rounded-lg p-3">
                              <span className="text-accent-amber font-bold">{idx + 1}.</span>
                              <p className="text-gray-300 text-sm">{insight}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Suggested Feature */}
                    {decision.suggested_feature && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <Rocket size={18} className="text-accent-green" />
                          Suggested Feature
                        </h4>
                        <p className="text-gray-300 text-sm bg-dark-bg rounded-lg p-3">{decision.suggested_feature}</p>
                      </div>
                    )}

                    {/* Participants */}
                    {decision.participants && decision.participants.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <Users size={18} className="text-primary-400" />
                          Participants
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {decision.participants.map((agent: string, idx: number) => (
                            <span key={idx} className="text-xs px-2 py-1 rounded-full bg-dark-bg text-gray-400 border border-dark-border">
                              {agent}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Checklist Progress */}
                    {gate.checklist && (
                      <div className="bg-dark-bg rounded-lg p-4">
                        <h4 className="font-semibold mb-3 flex items-center gap-2">
                          <Target size={18} className="text-primary-400" />
                          Checklist Progress
                        </h4>
                        <div className="flex items-center gap-4">
                          <div className="flex-1">
                            <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary-500 rounded-full"
                                style={{ width: `${gate.checklist.percentage || 0}%` }}
                              />
                            </div>
                          </div>
                          <span className="text-sm font-medium">
                            {gate.checklist.completed}/{gate.checklist.total} complete
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Created timestamp */}
                    <div className="text-sm text-gray-500">
                      Created: {new Date(gate.created_at).toLocaleString()}
                    </div>
                  </div>

                  {/* Modal Footer - Action Buttons */}
                  <div className="flex items-center justify-between p-6 border-t border-dark-border bg-dark-bg/50">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setSelectedGate(null)}
                        className="btn btn-secondary"
                      >
                        Close
                      </button>
                      {/* Session 689: Decline button to permanently dismiss unwanted gates */}
                      {!['approved', 'declined', 'waived'].includes(gate.status) && (
                        <button
                          onClick={async () => {
                            if (confirm('Are you sure you want to decline this pilot? This cannot be undone.')) {
                              try {
                                await pilotsApi.updateGateStatus(gate.id, 'decline', 'Declined by user')
                                setActionResult({ type: 'success', message: 'Pilot declined and removed!' })
                                setSelectedGate(null)
                                await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                              } catch {
                                setActionResult({ type: 'error', message: 'Failed to decline gate' })
                              }
                            }
                          }}
                          className="btn btn-secondary text-accent-red hover:bg-accent-red/20 flex items-center gap-2"
                          title="Permanently decline this pilot"
                        >
                          <Trash2 size={16} />
                          Decline
                        </button>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      {gate.status === 'not_started' && (
                        <button
                          onClick={async () => {
                            try {
                              await pilotsApi.updateGateStatus(gate.id, 'start')
                              setActionResult({ type: 'success', message: 'Gate started!' })
                              await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                              await queryClient.refetchQueries({ queryKey: ['gate-detail', selectedGate] })
                            } catch {
                              setActionResult({ type: 'error', message: 'Failed to start gate' })
                            }
                          }}
                          className="btn btn-primary flex items-center gap-2"
                        >
                          <Play size={16} />
                          Start Gate
                        </button>
                      )}
                      {/* Session 692: Check response.success and show checklist % */}
                      {gate.status === 'in_progress' && (
                        <button
                          onClick={async () => {
                            try {
                              const response = await pilotsApi.updateGateStatus(gate.id, 'ready')
                              if (response.data?.success === false) {
                                setActionResult({ type: 'error', message: response.data?.message || 'Checklist incomplete' })
                              } else {
                                setActionResult({ type: 'success', message: 'Gate marked ready!' })
                                await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                                await queryClient.refetchQueries({ queryKey: ['gate-detail', selectedGate] })
                              }
                            } catch {
                              setActionResult({ type: 'error', message: 'Failed to mark ready' })
                            }
                          }}
                          className={cn(
                            "btn flex items-center gap-2",
                            gate.checklist_percentage >= 50 ? "btn-primary" : "btn-primary opacity-50"
                          )}
                          title={gate.checklist_percentage < 50 ? `Checklist ${gate.checklist_percentage}% complete` : ''}
                        >
                          <CheckCircle size={16} />
                          Mark Ready {gate.checklist_percentage < 100 && `(${Math.round(gate.checklist_percentage)}%)`}
                        </button>
                      )}
                      {gate.status === 'ready' && (
                        <button
                          onClick={async () => {
                            approveGateMutation.mutate(gate.id)
                            await queryClient.refetchQueries({ queryKey: ['gate-detail', selectedGate] })
                          }}
                          className="btn btn-primary flex items-center gap-2"
                        >
                          <CheckCircle size={16} />
                          Approve & Start Pilot
                        </button>
                      )}
                    </div>
                  </div>
                </>
              )
            })()}
          </div>
        </div>
      )}

      {/* Session 688: Opportunity Detail Modal */}
      {selectedOpportunityId && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-dark-card rounded-lg border border-dark-border max-w-2xl w-full max-h-[90vh] overflow-auto">
            {(() => {
              // Session 688: Extract opportunity from response
              const opp = opportunityDetailData?.data?.opportunity

              if (loadingOpportunityDetail) {
                return (
                  <div className="flex items-center justify-center py-16">
                    <Loader2 className="animate-spin" size={32} />
                  </div>
                )
              }

              if (!opp) {
                return (
                  <div className="p-6 text-center text-gray-400">
                    <AlertTriangle className="mx-auto mb-2" size={32} />
                    <p>Failed to load opportunity details</p>
                    <button
                      onClick={() => setSelectedOpportunityId(null)}
                      className="btn btn-secondary mt-4"
                    >
                      Close
                    </button>
                  </div>
                )
              }

              return (
              <>
                {/* Modal Header */}
                <div className="flex items-start justify-between p-6 border-b border-dark-border">
                  <div className="flex-1 min-w-0 pr-4">
                    <h3 className="text-xl font-bold">{opp.title}</h3>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400">
                        {opp.category || 'General'}
                      </span>
                      <span className="text-xs px-2 py-1 rounded bg-accent-cyan/20 text-accent-cyan">
                        {opp.source_type || 'System'}
                      </span>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        opp.status === 'active' ? 'bg-accent-green/20 text-accent-green' :
                        opp.status === 'acted_on' ? 'bg-accent-amber/20 text-accent-amber' :
                        'bg-gray-500/20 text-gray-400'
                      )}>
                        {opp.status || 'active'}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedOpportunityId(null)}
                    className="p-2 hover:bg-dark-bg rounded-lg transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Modal Body */}
                <div className="p-6 space-y-6">
                  {/* Description */}
                  <div>
                    <p className="text-gray-300">{opp.description}</p>
                  </div>

                  {/* Score Section - Show breakdown only if detailed scores exist */}
                  {(() => {
                    const hasDetailedScores = opp.scores?.profit_potential || opp.scores?.competition_level ||
                                              opp.scores?.effort_required || opp.scores?.time_sensitivity
                    const overallScore = opp.scores?.overall_score || 0

                    return (
                      <div className="bg-dark-bg rounded-lg p-4">
                        <h4 className="font-semibold mb-4 flex items-center gap-2">
                          <Target size={18} className="text-primary-400" />
                          {hasDetailedScores ? 'Score Breakdown' : 'Opportunity Score'}
                        </h4>

                        {hasDetailedScores ? (
                          <>
                            <div className="grid grid-cols-2 gap-4">
                              <div className="space-y-3">
                                <div>
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm text-gray-400 flex items-center gap-1">
                                      <DollarSign size={14} /> Profit Potential (35%)
                                    </span>
                                    <span className="text-sm font-medium">{opp.scores?.profit_potential || 0}%</span>
                                  </div>
                                  <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                                    <div className="h-full bg-accent-green rounded-full" style={{ width: `${opp.scores?.profit_potential || 0}%` }} />
                                  </div>
                                </div>
                                <div>
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm text-gray-400 flex items-center gap-1">
                                      <Users size={14} /> Competition (35%)
                                    </span>
                                    <span className="text-sm font-medium">{opp.scores?.competition_level || 0}%</span>
                                  </div>
                                  <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                                    <div className="h-full bg-accent-amber rounded-full" style={{ width: `${opp.scores?.competition_level || 0}%` }} />
                                  </div>
                                </div>
                              </div>
                              <div className="space-y-3">
                                <div>
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm text-gray-400 flex items-center gap-1">
                                      <Wrench size={14} /> Effort Required (20%)
                                    </span>
                                    <span className="text-sm font-medium">{opp.scores?.effort_required || 0}%</span>
                                  </div>
                                  <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                                    <div className="h-full bg-accent-cyan rounded-full" style={{ width: `${opp.scores?.effort_required || 0}%` }} />
                                  </div>
                                </div>
                                <div>
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm text-gray-400 flex items-center gap-1">
                                      <Clock size={14} /> Time Sensitivity (10%)
                                    </span>
                                    <span className="text-sm font-medium">{opp.scores?.time_sensitivity || 0}%</span>
                                  </div>
                                  <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                                    <div className="h-full bg-primary-500 rounded-full" style={{ width: `${opp.scores?.time_sensitivity || 0}%` }} />
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="mt-4 pt-4 border-t border-dark-border flex items-center justify-between">
                              <span className="text-lg font-semibold">Overall Score</span>
                              <span className={cn(
                                'text-2xl font-bold',
                                overallScore >= 70 ? 'text-accent-green' :
                                overallScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
                              )}>
                                {overallScore}%
                              </span>
                            </div>
                          </>
                        ) : (
                          /* Simple score display when no detailed breakdown */
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-gray-400 text-sm">AI-calculated relevance score</p>
                              <p className="text-xs text-gray-500 mt-1">
                                {overallScore >= 70 ? 'High potential opportunity' :
                                 overallScore >= 50 ? 'Moderate potential' : 'Lower priority'}
                              </p>
                            </div>
                            <div className="text-center">
                              <span className={cn(
                                'text-4xl font-bold',
                                overallScore >= 70 ? 'text-accent-green' :
                                overallScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
                              )}>
                                {overallScore}%
                              </span>
                              <div className="w-24 h-2 bg-dark-border rounded-full overflow-hidden mt-2">
                                <div
                                  className={cn(
                                    'h-full rounded-full',
                                    overallScore >= 70 ? 'bg-accent-green' :
                                    overallScore >= 50 ? 'bg-accent-amber' : 'bg-accent-red'
                                  )}
                                  style={{ width: `${overallScore}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })()}

                  {/* Keywords */}
                  {opp.keywords && opp.keywords.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Keywords</h4>
                      <div className="flex flex-wrap gap-2">
                        {opp.keywords.map((kw: string, idx: number) => (
                          <span key={idx} className="text-xs px-2 py-1 rounded-full bg-dark-bg text-gray-400 border border-dark-border">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Source URL */}
                  {opp.url && (
                    <div>
                      <h4 className="font-semibold mb-2">Source</h4>
                      <a
                        href={opp.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 transition-colors"
                      >
                        <ExternalLink size={16} />
                        View Source
                      </a>
                    </div>
                  )}

                  {/* Created At */}
                  <div className="text-sm text-gray-500">
                    Discovered: {new Date(opp.created_at).toLocaleString()}
                  </div>
                </div>

                {/* Modal Footer - Action Buttons */}
                <div className="flex items-center justify-between p-6 border-t border-dark-border bg-dark-bg/50">
                  <button
                    onClick={() => dismissOpportunityMutation.mutate(selectedOpportunityId)}
                    disabled={dismissOpportunityMutation.isPending}
                    className="btn btn-secondary text-accent-red flex items-center gap-2"
                  >
                    {dismissOpportunityMutation.isPending ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Ban size={16} />
                    )}
                    Dismiss
                  </button>
                  <div className="flex items-center gap-3">
                    {opp.url && (
                      <a
                        href={opp.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary flex items-center gap-2"
                      >
                        <ExternalLink size={16} />
                        View Source
                      </a>
                    )}
                    <button
                      onClick={() => actOnOpportunityMutation.mutate(selectedOpportunityId)}
                      disabled={actOnOpportunityMutation.isPending || opp.status === 'acted_on' || opp.status === 'creating'}
                      className="btn btn-primary flex items-center gap-2"
                      title="Mark this opportunity as in-progress"
                    >
                      {actOnOpportunityMutation.isPending ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <Rocket size={16} />
                      )}
                      {opp.status === 'acted_on' || opp.status === 'creating' ? 'In Progress' : 'Mark Working'}
                    </button>
                  </div>
                </div>
              </>
              )
            })()}
          </div>
        </div>
      )}

      {/* Session 689: Pilot Detail Modal */}
      {selectedPilot && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-card border border-dark-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border">
              <div className="flex-1">
                <h3 className="text-lg font-semibold">{selectedPilot.decision_topic}</h3>
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  <span className={cn(
                    'text-xs px-2 py-1 rounded',
                    selectedPilot.status === 'running' ? 'bg-accent-green/20 text-accent-green' :
                    selectedPilot.outcome === 'success' ? 'bg-accent-green/20 text-accent-green' :
                    selectedPilot.outcome === 'failure' ? 'bg-accent-red/20 text-accent-red' :
                    'bg-accent-amber/20 text-accent-amber'
                  )}>
                    {selectedPilot.status === 'running' ? 'Running' : selectedPilot.outcome || 'Completed'}
                  </span>
                  <span className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400">
                    {selectedPilot.decision_type}
                  </span>
                  <span className={cn(
                    'text-xs px-2 py-1 rounded',
                    selectedPilot.risk_level === 'high' || selectedPilot.risk_level === 'critical'
                      ? 'bg-accent-red/20 text-accent-red'
                      : selectedPilot.risk_level === 'medium'
                      ? 'bg-accent-amber/20 text-accent-amber'
                      : 'bg-accent-green/20 text-accent-green'
                  )}>
                    {selectedPilot.risk_level} risk
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedPilotId(null)}
                className="p-2 hover:bg-dark-bg rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {/* Status Section - Different for Running vs Completed */}
              {selectedPilot.status === 'running' ? (
                <>
                  {/* Running Pilot: Progress */}
                  <div className="bg-accent-green/10 border border-accent-green/30 rounded-lg p-4">
                    <h4 className="font-semibold mb-3 flex items-center gap-2 text-accent-green">
                      <Play size={18} />
                      Pilot In Progress
                    </h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400">Time Running</p>
                        <p className="text-xl font-bold text-accent-green">{selectedPilot.hours_running?.toFixed(1)}h</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Time Remaining</p>
                        <p className="text-xl font-bold">{selectedPilot.auto_complete_in_hours?.toFixed(1)}h</p>
                      </div>
                    </div>
                    {/* Progress Bar */}
                    {selectedPilot.auto_complete_in_hours !== undefined && selectedPilot.hours_running !== undefined && (
                      <div className="mt-4">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                          <span>Progress</span>
                          <span>
                            {((selectedPilot.hours_running / (selectedPilot.hours_running + selectedPilot.auto_complete_in_hours)) * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                          <div
                            className="h-full bg-accent-green rounded-full transition-all"
                            style={{
                              width: `${Math.min(100, (selectedPilot.hours_running / (selectedPilot.hours_running + selectedPilot.auto_complete_in_hours)) * 100)}%`
                            }}
                          />
                        </div>
                      </div>
                    )}
                    {selectedPilot.kill_switch_triggered && (
                      <div className="mt-4 flex items-center gap-2 text-accent-red">
                        <AlertTriangle size={16} />
                        <span className="font-semibold">Kill Switch Triggered!</span>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  {/* Completed Pilot: Outcome */}
                  <div className={cn(
                    'rounded-lg p-4 border',
                    selectedPilot.outcome === 'success' ? 'bg-accent-green/10 border-accent-green/30' :
                    selectedPilot.outcome === 'failure' ? 'bg-accent-red/10 border-accent-red/30' :
                    'bg-accent-amber/10 border-accent-amber/30'
                  )}>
                    <h4 className={cn(
                      'font-semibold mb-3 flex items-center gap-2',
                      selectedPilot.outcome === 'success' ? 'text-accent-green' :
                      selectedPilot.outcome === 'failure' ? 'text-accent-red' :
                      'text-accent-amber'
                    )}>
                      {selectedPilot.outcome === 'success' ? <CheckCircle size={18} /> :
                       selectedPilot.outcome === 'failure' ? <XCircle size={18} /> :
                       <AlertTriangle size={18} />}
                      Pilot {selectedPilot.outcome === 'success' ? 'Succeeded' :
                             selectedPilot.outcome === 'failure' ? 'Failed' : 'Partially Completed'}
                    </h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400">Duration</p>
                        <p className="text-xl font-bold">{selectedPilot.duration_hours?.toFixed(1)}h</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Completed</p>
                        <p className="text-lg">{selectedPilot.completed_at ? new Date(selectedPilot.completed_at).toLocaleDateString() : 'Unknown'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Learnings Section */}
                  {selectedPilot.learnings && selectedPilot.learnings.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Lightbulb size={18} className="text-accent-amber" />
                        AI Evaluation & Learnings
                      </h4>
                      <div className="space-y-3">
                        {selectedPilot.learnings.map((learning: { type: string; outcome: string; confidence: number; impact_area: string; decision_type: string; hours_running: number }, idx: number) => (
                          <div key={idx} className="bg-dark-bg rounded-lg p-4 border border-dark-border">
                            <div className="flex items-center justify-between mb-2">
                              <span className={cn(
                                'text-xs px-2 py-1 rounded font-medium',
                                learning.outcome === 'success' ? 'bg-accent-green/20 text-accent-green' :
                                learning.outcome === 'failure' ? 'bg-accent-red/20 text-accent-red' :
                                'bg-accent-amber/20 text-accent-amber'
                              )}>
                                {learning.outcome}
                              </span>
                              <span className="text-xs px-2 py-1 rounded bg-accent-cyan/20 text-accent-cyan">
                                {(learning.confidence * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>
                                <span className="text-gray-400">Impact Area:</span>{' '}
                                <span className="text-gray-200">{learning.impact_area}</span>
                              </div>
                              <div>
                                <span className="text-gray-400">Type:</span>{' '}
                                <span className="text-gray-200">{learning.decision_type}</span>
                              </div>
                            </div>
                            {/* Confidence Bar */}
                            <div className="mt-3">
                              <div className="flex justify-between text-xs text-gray-500 mb-1">
                                <span>Confidence Score</span>
                                <span>{(learning.confidence * 100).toFixed(0)}%</span>
                              </div>
                              <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                                <div
                                  className={cn(
                                    'h-full rounded-full transition-all',
                                    learning.confidence >= 0.8 ? 'bg-accent-green' :
                                    learning.confidence >= 0.6 ? 'bg-accent-amber' :
                                    'bg-accent-red'
                                  )}
                                  style={{ width: `${learning.confidence * 100}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Session 690/691: Implementation Status with Review Button */}
                  {selectedPilot.outcome === 'success' && (
                    <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Wrench size={18} className="text-primary-400" />
                        Implementation Status
                      </h4>
                      {selectedPilot.implementation ? (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <span className={cn(
                              'text-sm px-3 py-1 rounded-full font-medium',
                              selectedPilot.implementation.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                              selectedPilot.implementation.status === 'requires_human' ? 'bg-accent-amber/20 text-accent-amber' :
                              selectedPilot.implementation.status === 'failed' ? 'bg-accent-red/20 text-accent-red' :
                              selectedPilot.implementation.status === 'in_progress' ? 'bg-accent-cyan/20 text-accent-cyan' :
                              'bg-gray-600/20 text-gray-400'
                            )}>
                              {selectedPilot.implementation.status === 'completed' ? '✓ Implemented' :
                               selectedPilot.implementation.status === 'requires_human' ? '⚠ Needs Review' :
                               selectedPilot.implementation.status === 'failed' ? '✗ Failed' :
                               selectedPilot.implementation.status === 'in_progress' ? '⟳ In Progress' :
                               '○ Pending'}
                            </span>
                            <span className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400">
                              {selectedPilot.implementation.type.replace(/_/g, ' ')}
                            </span>
                          </div>
                          {selectedPilot.implementation.executed_by && (
                            <div className="text-sm">
                              <span className="text-gray-400">Executed by:</span>{' '}
                              <span className="text-gray-200">{selectedPilot.implementation.executed_by}</span>
                            </div>
                          )}
                          {selectedPilot.implementation.completed_at && (
                            <div className="text-sm">
                              <span className="text-gray-400">Completed:</span>{' '}
                              <span className="text-gray-200">
                                {new Date(selectedPilot.implementation.completed_at).toLocaleString()}
                              </span>
                            </div>
                          )}
                          {/* Session 691: View Details button for review */}
                          {(selectedPilot.implementation.status === 'requires_human' ||
                            selectedPilot.implementation.status === 'completed' ||
                            selectedPilot.implementation.status === 'failed') && (
                            <button
                              onClick={() => setSelectedImplementationId(selectedPilot.id)}
                              className={cn(
                                'w-full mt-2 px-4 py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-colors',
                                selectedPilot.implementation.status === 'requires_human'
                                  ? 'bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30 border border-accent-amber/30'
                                  : 'bg-dark-card text-gray-300 hover:bg-dark-border border border-dark-border'
                              )}
                            >
                              <FileText size={16} />
                              {selectedPilot.implementation.status === 'requires_human'
                                ? 'Review Implementation Plan'
                                : 'View Implementation Details'}
                            </button>
                          )}
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-gray-400">
                          <Clock size={16} />
                          <span className="text-sm">No implementation yet - awaiting pipeline execution</span>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}

              {/* Decision Context from Gate */}
              {loadingPilotGateDetail ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="animate-spin" size={20} />
                  <span className="ml-2 text-gray-400">Loading decision context...</span>
                </div>
              ) : pilotGateDecision && (
                <>
                  {/* Recommended Action */}
                  {pilotGateDecision.recommended_stance && (
                    <div className="bg-primary-600/10 border border-primary-600/30 rounded-lg p-4">
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-primary-400">
                        <Flag size={18} />
                        Recommended Action
                      </h4>
                      <p className="text-gray-300 text-sm">{pilotGateDecision.recommended_stance}</p>
                    </div>
                  )}

                  {/* Rationale */}
                  {pilotGateDecision.rationale && (
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <FileText size={18} className="text-accent-cyan" />
                        Rationale
                      </h4>
                      <p className="text-gray-300 text-sm">{pilotGateDecision.rationale}</p>
                    </div>
                  )}

                  {/* Key Insights */}
                  {pilotGateDecision.key_insights && pilotGateDecision.key_insights.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Lightbulb size={18} className="text-accent-amber" />
                        Key Insights
                      </h4>
                      <div className="space-y-2">
                        {pilotGateDecision.key_insights.map((insight: string, idx: number) => (
                          <div key={idx} className="flex items-start gap-3 bg-dark-bg rounded-lg p-3">
                            <span className="text-accent-amber font-bold">{idx + 1}.</span>
                            <p className="text-gray-300 text-sm">{insight}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Suggested Feature */}
                  {pilotGateDecision.suggested_feature && (
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Wrench size={18} className="text-accent-green" />
                        Suggested Feature
                      </h4>
                      <p className="text-gray-300 text-sm">{pilotGateDecision.suggested_feature}</p>
                    </div>
                  )}

                  {/* Participants */}
                  {pilotGateDecision.participants && pilotGateDecision.participants.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Users size={18} className="text-primary-400" />
                        Participants
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {pilotGateDecision.participants.map((participant: string, idx: number) => (
                          <span key={idx} className="text-xs px-2 py-1 rounded-full bg-primary-600/20 text-primary-400 border border-primary-600/30">
                            {participant}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Timeline */}
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Clock size={18} className="text-primary-400" />
                  Timeline
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Started</span>
                    <span>{selectedPilot.started_at ? new Date(selectedPilot.started_at).toLocaleString() : 'Unknown'}</span>
                  </div>
                  {selectedPilot.completed_at && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Completed</span>
                      <span>{new Date(selectedPilot.completed_at).toLocaleString()}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* IDs for Debug/Reference */}
              <div className="text-xs text-gray-500 pt-4 border-t border-dark-border">
                <p>Pilot ID: {selectedPilot.id}</p>
                <p>Gate ID: {selectedPilot.gate_id}</p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end p-6 border-t border-dark-border bg-dark-bg/50">
              <button
                onClick={() => setSelectedPilotId(null)}
                className="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 691: Implementation Review Modal */}
      {selectedImplementationId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4">
          <div className="bg-dark-card border border-dark-border rounded-xl max-w-3xl w-full max-h-[90vh] overflow-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border">
              <div className="flex-1">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Wrench size={20} className="text-primary-400" />
                  Implementation Review
                </h3>
                {implementationDetail && (
                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      implementationDetail.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                      implementationDetail.status === 'requires_human' ? 'bg-accent-amber/20 text-accent-amber' :
                      implementationDetail.status === 'failed' ? 'bg-accent-red/20 text-accent-red' :
                      'bg-gray-500/20 text-gray-400'
                    )}>
                      {implementationDetail.status === 'completed' ? '✓ Completed' :
                       implementationDetail.status === 'requires_human' ? '⚠ Needs Human Review' :
                       implementationDetail.status === 'failed' ? '✗ Failed' :
                       implementationDetail.status}
                    </span>
                    <span className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400">
                      {implementationDetail.type.replace(/_/g, ' ')}
                    </span>
                  </div>
                )}
              </div>
              <button
                onClick={() => setSelectedImplementationId(null)}
                className="p-2 hover:bg-dark-bg rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {loadingImplementation ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                  <span className="ml-2 text-gray-400">Loading implementation details...</span>
                </div>
              ) : implementationDetail ? (
                <>
                  {/* Why it needs review */}
                  {implementationDetail.result?.requires_human_reason && (
                    <div className="bg-accent-amber/10 border border-accent-amber/30 rounded-lg p-4">
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-accent-amber">
                        <AlertTriangle size={18} />
                        Why This Needs Review
                      </h4>
                      <p className="text-gray-300 text-sm">{implementationDetail.result.requires_human_reason}</p>
                    </div>
                  )}

                  {/* Target Description - Session 692: Status-aware labels */}
                  {implementationDetail.target_description && (
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Target size={18} className="text-accent-cyan" />
                        {implementationDetail.status === 'completed' ? 'What Was Built' :
                         implementationDetail.status === 'failed' ? 'What Failed to Build' :
                         'What Needs to Be Built'}
                      </h4>
                      <p className="text-gray-300 text-sm bg-dark-bg p-4 rounded-lg border border-dark-border">
                        {implementationDetail.target_description}
                      </p>
                    </div>
                  )}

                  {/* Recommended Action - Session 692: Status-aware labels */}
                  {implementationDetail.plan?.recommended_action && (
                    <div className={cn(
                      "rounded-lg p-4",
                      implementationDetail.status === 'completed'
                        ? "bg-accent-green/10 border border-accent-green/30"
                        : "bg-primary-600/10 border border-primary-600/30"
                    )}>
                      <h4 className={cn(
                        "font-semibold mb-2 flex items-center gap-2",
                        implementationDetail.status === 'completed' ? "text-accent-green" : "text-primary-400"
                      )}>
                        <Flag size={18} />
                        {implementationDetail.status === 'completed' ? 'Action Taken' :
                         implementationDetail.status === 'requires_human' ? 'Action Required' :
                         'Recommended Action'}
                      </h4>
                      <p className="text-gray-300 text-sm">{implementationDetail.plan.recommended_action}</p>
                    </div>
                  )}

                  {/* Key Insights - Session 692: Status-aware labels */}
                  {implementationDetail.plan?.key_insights && implementationDetail.plan.key_insights.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <Lightbulb size={18} className={implementationDetail.status === 'completed' ? "text-accent-green" : "text-accent-amber"} />
                        {implementationDetail.status === 'completed'
                          ? `Insights Applied (${implementationDetail.plan.key_insights.length})`
                          : `Key Insights (${implementationDetail.plan.key_insights.length})`}
                      </h4>
                      <div className="space-y-2">
                        {implementationDetail.plan.key_insights.map((insight, idx) => (
                          <div key={idx} className="flex items-start gap-3 bg-dark-bg rounded-lg p-3 border border-dark-border">
                            <span className={cn(
                              "font-bold text-sm",
                              implementationDetail.status === 'completed' ? "text-accent-green" : "text-accent-amber"
                            )}>{implementationDetail.status === 'completed' ? '✓' : `${idx + 1}.`}</span>
                            <p className="text-gray-300 text-sm">{insight}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Implementation Steps - Session 692: Status-aware labels */}
                  {implementationDetail.plan?.steps && implementationDetail.plan.steps.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <CheckCircle size={18} className={implementationDetail.status === 'completed' ? "text-accent-green" : "text-gray-400"} />
                        {implementationDetail.status === 'completed' ? 'Completed Steps' : 'Implementation Steps'}
                      </h4>
                      <div className="space-y-2">
                        {implementationDetail.plan.steps.map((step, idx) => (
                          <div key={idx} className="flex items-center gap-3 text-sm">
                            <span className={cn(
                              "w-6 h-6 rounded-full flex items-center justify-center text-xs",
                              implementationDetail.status === 'completed'
                                ? "bg-accent-green/20 text-accent-green"
                                : "bg-dark-border text-gray-400"
                            )}>
                              {implementationDetail.status === 'completed' ? '✓' : idx + 1}
                            </span>
                            <span className="text-gray-300">{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Rationale */}
                  {implementationDetail.plan?.rationale && (
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <FileText size={18} className="text-gray-400" />
                        Rationale
                      </h4>
                      <p className="text-gray-400 text-sm">{implementationDetail.plan.rationale}</p>
                    </div>
                  )}

                  {/* Execution Result (for completed/failed) */}
                  {implementationDetail.result?.success !== undefined && (
                    <div className={cn(
                      'rounded-lg p-4 border',
                      implementationDetail.result.success
                        ? 'bg-accent-green/10 border-accent-green/30'
                        : 'bg-accent-red/10 border-accent-red/30'
                    )}>
                      <h4 className={cn(
                        'font-semibold mb-2 flex items-center gap-2',
                        implementationDetail.result.success ? 'text-accent-green' : 'text-accent-red'
                      )}>
                        {implementationDetail.result.success ? <CheckCircle size={18} /> : <XCircle size={18} />}
                        Execution Result
                      </h4>
                      {implementationDetail.result.summary && (
                        <p className="text-gray-300 text-sm mb-2">{implementationDetail.result.summary}</p>
                      )}
                      {implementationDetail.result.actions && implementationDetail.result.actions.length > 0 && (
                        <div className="space-y-1 mt-3">
                          {implementationDetail.result.actions.map((action, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-sm">
                              {action.success ? (
                                <CheckCircle size={14} className="text-accent-green" />
                              ) : (
                                <XCircle size={14} className="text-accent-red" />
                              )}
                              <span className="text-gray-300">{action.description}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Error (if failed) */}
                  {implementationDetail.error && (
                    <div className="bg-accent-red/10 border border-accent-red/30 rounded-lg p-4">
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-accent-red">
                        <XCircle size={18} />
                        Error
                      </h4>
                      <p className="text-gray-300 text-sm font-mono">{implementationDetail.error}</p>
                    </div>
                  )}

                  {/* Timestamps */}
                  <div className="text-xs text-gray-500 pt-4 border-t border-dark-border">
                    <p>Created: {new Date(implementationDetail.created_at).toLocaleString()}</p>
                    {implementationDetail.started_at && (
                      <p>Started: {new Date(implementationDetail.started_at).toLocaleString()}</p>
                    )}
                    {implementationDetail.completed_at && (
                      <p>Completed: {new Date(implementationDetail.completed_at).toLocaleString()}</p>
                    )}
                    <p className="mt-2">Implementation ID: {implementationDetail.id}</p>
                  </div>
                </>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <AlertTriangle size={32} className="mx-auto mb-2" />
                  <p>No implementation details found</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-dark-border bg-dark-bg/50">
              <button
                onClick={() => setSelectedImplementationId(null)}
                className="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
