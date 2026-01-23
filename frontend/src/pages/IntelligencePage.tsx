import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
// Session 714: Real-time system events
import { useSystemEvents } from '@/hooks/useWebSocket'
// Session 693: Removed agentsApi - agents tab removed (redundant with main Agents page)
// Session 694: Removed learningApi, activityApi - tabs removed (redundant with main Agents page)
import { intelligenceApi, pilotsApi, experimentsApi, spidersApi, opportunitiesApi, incomeBuilderApi, experimentRecommendationsApi } from '@/lib/api'
import {
  Brain, TrendingUp, AlertTriangle, Zap, CheckCircle, XCircle,
  Play, Pause, RefreshCw, ChevronRight, Loader2,
  Target, BarChart3, Globe, Sparkles, X, ExternalLink,
  Rocket, Ban, DollarSign, Clock, Users, User, Wrench, Lightbulb, FileText, Flag,
  Trash2, Tag, ArrowUp, Eye, Star, FlaskConical, AlertOctagon, Heart
} from 'lucide-react'
import { cn } from '@/lib/cn'
// Session 713: Body governance for pilot blocking
import { useBodyGovernance } from '@/stores/bodyStore'
// Session 713: Cross-page navigation
import EntityLink from '@/components/EntityLink'
import { CompactBreadcrumb } from '@/components/Breadcrumb'

// Session 693: Removed 'agents' tab - redundant with main Agents page
// Session 694: Removed 'learning' and 'activity' tabs - redundant with main Agents page
// Session 734: Added 'income' tab for Income Builder
type TabType = 'gates' | 'pilots' | 'experiments' | 'spiders' | 'predictions' | 'income'

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

// Session 697: Checklist item interface for Gate detail modal
// Session 746: Enhanced with all backend fields
interface GateChecklistItem {
  id: string
  item_type: string
  title: string
  description: string
  status: 'pending' | 'completed'
  is_required: boolean
  generated_content: string | null
  has_content: boolean
  // Session 746: Additional fields from backend
  documentation_url?: string
  documentation_notes?: string
  assigned_to?: string
  completed_by?: string
  completed_at?: string
  completion_notes?: string
}

// Session 746: Pilot execution history interface
interface PilotExecution {
  id: string
  name: string
  status: string
  outcome?: string
  outcome_summary?: string
  kill_switch_triggered?: boolean
  started_at?: string
  completed_at?: string
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

// Session 692: Updated to match actual API response from /api/pilot-experiments/
// Session 693: Extended with all rich data fields
interface Experiment {
  id: string
  name: string
  hypothesis: string
  status: 'running' | 'success' | 'failure' | 'inconclusive'
  kpi_owner: string
  primary_kpi: string
  target_value: string
  current_value: string
  secondary_kpis: string[]
  extracted_metrics?: {
    source: string
    raw_content: string
  }
  started_at: string | null
  ended_at: string | null
  learnings: string | null
  pilot_id: string | null
  decision_topic: string
  decision_id: string | null
  risk_level: string
  is_halted: boolean
  halted_at: string | null
  halted_by: string
  halt_reason: string
  outcome_classification: string
}

// Session 694: Removed LearningEvent and ActivityFeedItem interfaces - tabs moved to Agents page

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
  prediction: string  // Full prediction text
  probability: number
  category: string
  // Agent info
  agent_name: string
  agent_type: string | null
  // Source info
  source_type: string  // dream, analysis, pattern, etc.
  source_reference: { dream_id?: string } | null
  // Legacy field for backwards compat
  source?: string
  // Tags
  tags: string[]
  // Timing
  timeframe: string
  deadline: string | null
  days_remaining: number | null
  created_at: string
  // Status & Verification
  status: string
  is_featured: boolean
  verified_at: string | null
  accuracy_score: number | null
  // Engagement
  upvotes: number
  views: number
}

// Session 734: Income Builder plan interface
interface IncomePlan {
  id: string
  opportunity_title: string
  focus_area: string
  status: 'draft' | 'ready' | 'in_progress' | 'completed' | 'failed'
  created_at: string
  modified_at: string
  has_quickstart: boolean
  step_count: number
  files: string[]
  estimated_value?: number
  progress_percentage?: number
}

// Session 693: Removed Agent interface - agents tab removed (redundant with main Agents page)

// Session 734: Helper to strip HTML tags from scraped content
function stripHtml(html: string | undefined | null): string {
  if (!html) return ''
  // Remove HTML tags and decode common entities
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim()
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
  // Session 697: Expanded checklist items state
  const [expandedChecklistItems, setExpandedChecklistItems] = useState<Set<string>>(new Set())
  // Session 688: Opportunity modal state
  const [selectedOpportunityId, setSelectedOpportunityId] = useState<string | null>(null)
  // Session 689: Pilot detail modal state
  const [selectedPilotId, setSelectedPilotId] = useState<string | null>(null)
  // Session 691: Implementation review modal state
  const [selectedImplementationId, setSelectedImplementationId] = useState<string | null>(null)
  // Session 692: Prediction detail modal state
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null)
  // Session 693: Experiment detail modal state
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null)
  const queryClient = useQueryClient()

  // Session 714: Real-time event handlers - refresh data when events occur
  const handlePilotStarted = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['pilots'] })
    queryClient.invalidateQueries({ queryKey: ['gates'] })
  }, [queryClient])

  const handlePilotCompleted = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['pilots'] })
    queryClient.invalidateQueries({ queryKey: ['gates'] })
    queryClient.invalidateQueries({ queryKey: ['experiments'] })
  }, [queryClient])

  const handleAgentExecution = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['intelligence-status'] })
  }, [queryClient])

  // Session 714: Subscribe to system events
  useSystemEvents({
    onPilotStarted: handlePilotStarted,
    onPilotCompleted: handlePilotCompleted,
    onAgentExecutionComplete: handleAgentExecution,
    onAgentExecutionFailed: handleAgentExecution,
  })

  // Session 713: Body governance check for starting pilots
  const { canStartPilot } = useBodyGovernance()

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

  // Session 745: Experiment recommendations
  const { data: recommendationsData, isLoading: loadingRecommendations } = useQuery({
    queryKey: ['experiment-recommendations'],
    queryFn: () => experimentRecommendationsApi.list(),
    enabled: activeTab === 'experiments',
  })
  const recommendations = recommendationsData?.data?.recommendations || recommendationsData?.data || []

  // Session 694: Removed learning and activity queries - tabs moved to Agents page

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

  // Session 734: Income Builder plans
  const { data: incomePlansData, isLoading: loadingIncomePlans, refetch: refetchIncomePlans } = useQuery({
    queryKey: ['income-plans'],
    queryFn: () => incomeBuilderApi.listPlans(),
    enabled: activeTab === 'income',
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

  // Session 692: Improved error handling for startPilot mutation
  const startPilotMutation = useMutation({
    mutationFn: (gateId: string) => pilotsApi.startPilot(gateId),
    onSuccess: async (response) => {
      // Check response.data.success since API may return 200 with success: false
      if (response.data?.success === false) {
        setActionResult({ type: 'error', message: response.data?.message || 'Failed to start pilot' })
      } else {
        const pilotName = response.data?.pilot?.name?.slice(0, 50) || 'Success'
        setActionResult({ type: 'success', message: `Pilot started: ${pilotName}` })
        // Force immediate refetch to update UI
        await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
        await queryClient.refetchQueries({ queryKey: ['pilots-dashboard'] })
      }
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
  // Session 694: Removed learningEvents and activityFeedItems - tabs moved to Agents page
  const spiders: Spider[] = spidersData?.data?.spiders || []
  const predictions: Prediction[] = predictionsData?.data?.predictions || []
  // Session 734: Income Builder plans
  const incomePlans: IncomePlan[] = incomePlansData?.data?.plans || []

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

  // Session 693: Removed 'agents' tab - redundant with main Agents page (7 tabs now)
  const tabs: { key: TabType; label: string; icon: React.ElementType; count?: number }[] = [
    { key: 'gates', label: 'Gates', icon: Target, count: gates.filter(g => ['not_started', 'in_progress', 'ready'].includes(g.status)).length },
    { key: 'pilots', label: 'Pilots', icon: Play, count: pilots.filter(p => p.status === 'running').length },
    { key: 'experiments', label: 'Experiments', icon: BarChart3, count: experiments.filter(e => e.status === 'running').length },
    { key: 'spiders', label: 'Spiders', icon: Globe, count: spiders.filter(s => s.status === 'active').length },
    { key: 'predictions', label: 'Predictions', icon: Sparkles },
    { key: 'income', label: 'Income Builder', icon: DollarSign, count: incomePlans.length },
    // Session 694: Removed learning and activity tabs - available on Agents page
  ]

  return (
    <div className="space-y-6">
      {/* Session 713: Breadcrumb navigation */}
      <CompactBreadcrumb currentPage="Intelligence" />

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
              <p className="text-sm text-gray-400">Running Experiments</p>
              <p className="text-2xl font-bold">{experiments.filter(e => e.status === 'running').length || 0}</p>
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
                    {/* in_progress with incomplete checklist → Approve All Items */}
                    {/* Session 692: Add button to approve all checklist items at once */}
                    {gate.status === 'in_progress' && gate.checklist_completed < gate.checklist_total && (
                      <button
                        className="btn btn-secondary text-sm flex items-center gap-1"
                        onClick={async (e) => {
                          e.stopPropagation()
                          try {
                            const response = await pilotsApi.approveAllItems(gate.id)
                            if (response.data?.success) {
                              setActionResult({ type: 'success', message: `Approved ${response.data.items_approved} checklist items` })
                              await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                            } else {
                              setActionResult({ type: 'error', message: response.data?.message || 'Failed to approve items' })
                            }
                          } catch {
                            setActionResult({ type: 'error', message: 'Failed to approve checklist items' })
                          }
                        }}
                        disabled={isLoading}
                        title={`Approve all ${gate.checklist_total - gate.checklist_completed} pending checklist items`}
                      >
                        <CheckCircle size={14} />
                        Approve All ({gate.checklist_total - gate.checklist_completed})
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
                    {/* Session 713: Check body governance before allowing pilot start */}
                    {gate.status === 'approved' && !gate.running_pilot && (
                      <div className="flex items-center gap-2">
                        {!canStartPilot.allowed && (
                          <span
                            className="text-xs text-red-400 flex items-center gap-1"
                            title={canStartPilot.reason}
                          >
                            <Heart size={12} className="animate-pulse" />
                            Body Critical
                          </span>
                        )}
                        <button
                          className={cn(
                            "btn text-sm flex items-center gap-1",
                            canStartPilot.allowed ? "btn-primary" : "btn-secondary opacity-50 cursor-not-allowed"
                          )}
                          onClick={(e) => {
                            e.stopPropagation()
                            if (canStartPilot.allowed) {
                              startPilotMutation.mutate(gate.id)
                            } else {
                              setActionResult({ type: 'error', message: canStartPilot.reason || 'Body health critical - cannot start pilot' })
                            }
                          }}
                          disabled={isLoading || !canStartPilot.allowed}
                          title={canStartPilot.allowed ? 'Start pilot' : canStartPilot.reason}
                        >
                          {startPilotMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                          Start Pilot
                        </button>
                      </div>
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
                  <p className="text-2xl font-bold">{(pilotMetrics.success_rate ?? 0).toFixed(0)}%</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Clock className="text-primary-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Avg Duration</p>
                  <p className="text-2xl font-bold">{(pilotMetrics.avg_duration_hours ?? 0).toFixed(1)}h</p>
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
                              <span>{(progressPercent ?? 0).toFixed(0)}% complete</span>
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
                                    {((confidence ?? 0) * 100).toFixed(0)}% confidence
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
        <>
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
              {/* Session 692: Map API fields | Session 693: Rich experiment cards */}
              {experiments.map((experiment) => (
                <div
                  key={experiment.id}
                  className="p-4 rounded-lg border border-dark-border hover:border-primary-500/50 transition-colors cursor-pointer"
                  onClick={() => setSelectedExperiment(experiment)}
                >
                  {/* Header Row */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0',
                        experiment.status === 'running' ? 'bg-primary-500/20' :
                        experiment.status === 'success' ? 'bg-accent-green/20' : 'bg-accent-red/20'
                      )}>
                        <BarChart3 size={20} className={
                          experiment.status === 'running' ? 'text-primary-400' :
                          experiment.status === 'success' ? 'text-accent-green' : 'text-accent-red'
                        } />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium truncate">{experiment.name || experiment.decision_topic}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={cn(
                            'px-2 py-0.5 text-xs rounded',
                            experiment.status === 'running' ? 'bg-primary-500/20 text-primary-400' :
                            experiment.status === 'success' ? 'bg-accent-green/20 text-accent-green' :
                            experiment.status === 'failure' ? 'bg-accent-red/20 text-accent-red' :
                            'bg-accent-amber/20 text-accent-amber'
                          )}>
                            {experiment.status}
                          </span>
                          <span className={cn(
                            'px-2 py-0.5 text-xs rounded',
                            experiment.risk_level === 'high' ? 'bg-accent-red/20 text-accent-red' :
                            experiment.risk_level === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                            'bg-accent-green/20 text-accent-green'
                          )}>
                            {experiment.risk_level} risk
                          </span>
                          {experiment.is_halted && (
                            <span className="px-2 py-0.5 text-xs rounded bg-gray-500/20 text-gray-400">
                              HALTED
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {experiment.status === 'running' && !experiment.is_halted && (
                        <button
                          className="btn btn-secondary text-sm text-accent-red flex items-center gap-1"
                          onClick={(e) => {
                            e.stopPropagation()
                            haltExperimentMutation.mutate(experiment.id)
                          }}
                          disabled={isLoading}
                        >
                          {haltExperimentMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Pause size={14} />}
                          Halt
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Hypothesis */}
                  {experiment.hypothesis && (
                    <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                      <span className="text-gray-500">Hypothesis:</span> {experiment.hypothesis}
                    </p>
                  )}

                  {/* KPI and Metrics Row */}
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-4">
                      <div>
                        <span className="text-gray-500">KPI:</span>{' '}
                        <span className="text-gray-300">{experiment.primary_kpi}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Progress:</span>{' '}
                        <span className="text-accent-cyan">{experiment.current_value || '0'}</span>
                        <span className="text-gray-500"> / </span>
                        <span className="text-gray-300">{experiment.target_value || '100'}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-gray-400">
                      <div className="flex items-center gap-1">
                        <User size={14} />
                        <span>{experiment.kpi_owner}</span>
                      </div>
                      {experiment.started_at && (
                        <div className="flex items-center gap-1">
                          <Clock size={14} />
                          <span>{new Date(experiment.started_at).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <BarChart3 className="mx-auto mb-2" size={32} />
              <p>No experiments yet</p>
              <p className="text-sm text-gray-500 mt-1">Experiments are created when pilots are started</p>
            </div>
          )}
        </div>

        {/* Session 745: Experiment Recommendations */}
        <div className="card mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Lightbulb className="text-accent-amber" size={20} />
              Experiment Recommendations
            </h3>
          </div>
          {loadingRecommendations ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="animate-spin" size={20} />
            </div>
          ) : recommendations.length > 0 ? (
            <div className="space-y-3">
              {recommendations.slice(0, 5).map((rec: { id: string; title: string; description?: string; priority?: string; source?: string }, idx: number) => (
                <div key={rec.id || idx} className="p-3 rounded-lg border border-dark-border hover:border-primary-500/50 transition-colors">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="font-medium text-sm">{rec.title}</p>
                      {rec.description && (
                        <p className="text-xs text-gray-400 mt-1 line-clamp-2">{rec.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {rec.priority && (
                        <span className={cn(
                          'px-2 py-0.5 text-xs rounded',
                          rec.priority === 'high' ? 'bg-accent-red/20 text-accent-red' :
                          rec.priority === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                          'bg-accent-green/20 text-accent-green'
                        )}>
                          {rec.priority}
                        </span>
                      )}
                      {rec.source && (
                        <span className="text-xs text-gray-500">{rec.source}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-400">
              <Lightbulb className="mx-auto mb-2 opacity-50" size={24} />
              <p className="text-sm">No recommendations available</p>
              <p className="text-xs text-gray-500 mt-1">Recommendations will appear based on system analysis</p>
            </div>
          )}
        </div>
        </>
      )}

      {/* Session 694: Removed Learning and Activity tabs - available on Agents page */}

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

      {/* Predictions Tab - Session 692: Rich prediction display with modal */}
      {activeTab === 'predictions' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">AI Predictions</h3>
          {loadingPredictions ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin" size={24} />
            </div>
          ) : predictions.length > 0 ? (
            <div className="space-y-4">
              {predictions.map((pred: Prediction, idx: number) => (
                <div
                  key={pred.id || idx}
                  className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                  onClick={() => setSelectedPrediction(pred)}
                >
                  {/* Header row */}
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-12 w-12 rounded-lg flex items-center justify-center shrink-0',
                        pred.probability >= 70 ? 'bg-accent-green/20' :
                        pred.probability >= 40 ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                      )}>
                        <Sparkles size={24} className={
                          pred.probability >= 70 ? 'text-accent-green' :
                          pred.probability >= 40 ? 'text-accent-amber' : 'text-accent-red'
                        } />
                      </div>
                      <div>
                        <p className="font-semibold text-lg">{pred.title}</p>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                            {pred.category}
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded bg-accent-cyan/20 text-accent-cyan">
                            {pred.source_type || 'analysis'}
                          </span>
                          {pred.is_featured && (
                            <span className="text-xs px-2 py-0.5 rounded bg-accent-amber/20 text-accent-amber">
                              ⭐ Featured
                            </span>
                          )}
                          {pred.status && pred.status !== 'pending' && (
                            <span className={cn(
                              'text-xs px-2 py-0.5 rounded',
                              pred.status === 'verified_true' ? 'bg-accent-green/20 text-accent-green' :
                              pred.status === 'verified_false' ? 'bg-accent-red/20 text-accent-red' :
                              'bg-gray-600/20 text-gray-400'
                            )}>
                              {pred.status.replace('_', ' ')}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <p className={cn(
                        'text-2xl font-bold',
                        pred.probability >= 70 ? 'text-accent-green' :
                        pred.probability >= 40 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {pred.probability}%
                      </p>
                      <p className="text-xs text-gray-500">confidence</p>
                    </div>
                  </div>

                  {/* Prediction text - truncated */}
                  {pred.prediction && (
                    <p className="text-sm text-gray-300 mb-3 line-clamp-2">
                      {pred.prediction}
                    </p>
                  )}

                  {/* Tags */}
                  {pred.tags && pred.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {pred.tags.slice(0, 3).map((tag: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">
                          #{tag.slice(0, 25)}
                        </span>
                      ))}
                      {pred.tags.length > 3 && (
                        <span className="text-xs text-gray-500">+{pred.tags.length - 3} more</span>
                      )}
                    </div>
                  )}

                  {/* Footer row */}
                  <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-dark-border">
                    <div className="flex items-center gap-4">
                      {/* Session 713: EntityLink for agent navigation */}
                      <EntityLink
                        type="agent"
                        id={pred.agent_name || pred.source || ''}
                        label={pred.agent_name || pred.source || 'Unknown'}
                        iconSize={12}
                        className="text-xs"
                      />
                      <span className="flex items-center gap-1">
                        <Clock size={12} />
                        {pred.timeframe || 'quarter'}
                        {pred.days_remaining !== null && pred.days_remaining !== undefined && (
                          <span className={pred.days_remaining < 30 ? 'text-accent-amber' : ''}>
                            ({pred.days_remaining}d)
                          </span>
                        )}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      {(pred.upvotes > 0 || pred.views > 0) && (
                        <>
                          <span>👍 {pred.upvotes}</span>
                          <span>👁 {pred.views}</span>
                        </>
                      )}
                      <span>
                        {pred.created_at ? new Date(pred.created_at).toLocaleDateString() : ''}
                      </span>
                    </div>
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

      {/* Session 693: Removed Agents Tab - redundant with main Agents page */}

      {/* Session 734: Income Builder Tab */}
      {activeTab === 'income' && (
        <div className="space-y-6">
          {/* Income Builder Header */}
          <div className="card bg-gradient-to-r from-accent-green/10 to-accent-amber/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-lg bg-accent-green/20 flex items-center justify-center">
                  <DollarSign size={28} className="text-accent-green" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">Income Builder</h3>
                  <p className="text-gray-400">
                    {incomePlans.length} action plans • Revenue generation strategies
                  </p>
                </div>
              </div>
              <button
                onClick={() => refetchIncomePlans()}
                className="btn btn-secondary flex items-center gap-2"
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>
          </div>

          {/* Plans List */}
          <div className="card">
            <h4 className="text-lg font-semibold mb-4">Action Plans</h4>
            {loadingIncomePlans ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : incomePlans.length > 0 ? (
              <div className="space-y-3">
                {incomePlans.map((plan: IncomePlan) => (
                  <div
                    key={plan.id}
                    className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3 min-w-0 flex-1">
                        <div className={cn(
                          'h-10 w-10 rounded-lg flex items-center justify-center shrink-0',
                          plan.status === 'completed' ? 'bg-accent-green/20' :
                          plan.status === 'in_progress' ? 'bg-accent-cyan/20' :
                          plan.status === 'failed' ? 'bg-accent-red/20' :
                          'bg-accent-amber/20'
                        )}>
                          {plan.status === 'completed' ? <CheckCircle size={20} className="text-accent-green" /> :
                           plan.status === 'in_progress' ? <Play size={20} className="text-accent-cyan" /> :
                           plan.status === 'failed' ? <XCircle size={20} className="text-accent-red" /> :
                           <FileText size={20} className="text-accent-amber" />}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="font-semibold truncate">{plan.opportunity_title}</p>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            <span className={cn(
                              'text-xs px-2 py-0.5 rounded',
                              plan.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                              plan.status === 'in_progress' ? 'bg-accent-cyan/20 text-accent-cyan' :
                              plan.status === 'failed' ? 'bg-accent-red/20 text-accent-red' :
                              'bg-accent-amber/20 text-accent-amber'
                            )}>
                              {plan.status.replace('_', ' ')}
                            </span>
                            {plan.focus_area && (
                              <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                                {plan.focus_area}
                              </span>
                            )}
                            {plan.has_quickstart && (
                              <span className="text-xs px-2 py-0.5 rounded bg-accent-cyan/20 text-accent-cyan">
                                Quick Start
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                            <span>{plan.step_count} steps</span>
                            <span>{plan.files.length} files</span>
                            <span>{new Date(plan.modified_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      {plan.estimated_value && (
                        <div className="text-right shrink-0">
                          <p className="text-lg font-bold text-accent-green">
                            ${plan.estimated_value.toLocaleString()}
                          </p>
                          <p className="text-xs text-gray-500">est. value</p>
                        </div>
                      )}
                    </div>
                    {/* Progress bar if in progress */}
                    {plan.status === 'in_progress' && plan.progress_percentage !== undefined && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-gray-400">Progress</span>
                          <span className="text-accent-cyan">{plan.progress_percentage}%</span>
                        </div>
                        <div className="h-1.5 bg-dark-border rounded-full overflow-hidden">
                          <div
                            className="h-full bg-accent-cyan transition-all"
                            style={{ width: `${plan.progress_percentage}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <DollarSign className="mx-auto mb-3" size={48} />
                <p className="text-lg font-medium">No Action Plans Yet</p>
                <p className="text-sm text-gray-500 mt-1">
                  Action plans are generated when you analyze revenue opportunities
                </p>
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

                    {/* Session 746: Success & Failure Criteria */}
                    {(gate.success_criteria || gate.failure_criteria) && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {gate.success_criteria && (
                          <div className="bg-accent-green/5 border border-accent-green/20 rounded-lg p-3">
                            <h4 className="font-semibold mb-2 flex items-center gap-2 text-accent-green text-sm">
                              <CheckCircle size={16} />
                              Success Criteria
                            </h4>
                            <p className="text-sm text-gray-300">{gate.success_criteria}</p>
                          </div>
                        )}
                        {gate.failure_criteria && (
                          <div className="bg-accent-red/5 border border-accent-red/20 rounded-lg p-3">
                            <h4 className="font-semibold mb-2 flex items-center gap-2 text-accent-red text-sm">
                              <XCircle size={16} />
                              Failure Criteria
                            </h4>
                            <p className="text-sm text-gray-300">{gate.failure_criteria}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Session 746: Risk Factors */}
                    {gate.risk_factors && gate.risk_factors.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <AlertTriangle size={18} className="text-accent-amber" />
                          Risk Factors
                        </h4>
                        <div className="space-y-2">
                          {gate.risk_factors.map((risk: string, idx: number) => (
                            <div key={idx} className="flex items-start gap-2 bg-accent-amber/5 border border-accent-amber/20 rounded-lg p-3">
                              <span className="text-accent-amber text-sm">⚠</span>
                              <p className="text-sm text-gray-300">{risk}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Session 746: Approval Info */}
                    {gate.approved_by && (
                      <div className="bg-accent-green/5 border border-accent-green/20 rounded-lg p-4">
                        <h4 className="font-semibold mb-2 flex items-center gap-2 text-accent-green">
                          <CheckCircle size={18} />
                          Approval Information
                        </h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Approved by:</span>
                            <span className="ml-2 text-gray-300">{gate.approved_by}</span>
                          </div>
                          {gate.approval_notes && (
                            <div className="col-span-2">
                              <span className="text-gray-500">Notes:</span>
                              <p className="text-gray-300 mt-1">{gate.approval_notes}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Session 746: Pilot Execution History */}
                    {gate.executions && gate.executions.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <Play size={18} className="text-accent-cyan" />
                          Pilot Execution History ({gate.executions.length})
                        </h4>
                        <div className="space-y-2">
                          {gate.executions.map((exec: PilotExecution) => (
                            <div
                              key={exec.id}
                              className={cn(
                                'border rounded-lg p-3',
                                exec.status === 'completed' ? 'border-accent-green/30 bg-accent-green/5' :
                                exec.status === 'failed' ? 'border-accent-red/30 bg-accent-red/5' :
                                exec.status === 'running' ? 'border-accent-cyan/30 bg-accent-cyan/5' :
                                'border-dark-border bg-dark-bg'
                              )}
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-medium text-sm">{exec.name}</span>
                                <span className={cn(
                                  'text-xs px-2 py-0.5 rounded',
                                  exec.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                                  exec.status === 'failed' ? 'bg-accent-red/20 text-accent-red' :
                                  exec.status === 'running' ? 'bg-accent-cyan/20 text-accent-cyan' :
                                  'bg-gray-500/20 text-gray-400'
                                )}>
                                  {exec.status}
                                </span>
                              </div>
                              <div className="flex items-center gap-4 text-xs text-gray-400">
                                {exec.started_at && (
                                  <span>Started: {new Date(exec.started_at).toLocaleString()}</span>
                                )}
                                {exec.completed_at && (
                                  <span>Completed: {new Date(exec.completed_at).toLocaleString()}</span>
                                )}
                                {exec.kill_switch_triggered && (
                                  <span className="text-accent-red flex items-center gap-1">
                                    <AlertTriangle size={12} /> Kill switch triggered
                                  </span>
                                )}
                              </div>
                              {exec.outcome && (
                                <div className="mt-2 text-sm">
                                  <span className="text-gray-500">Outcome:</span>
                                  <span className={cn(
                                    'ml-2',
                                    exec.outcome === 'success' ? 'text-accent-green' :
                                    exec.outcome === 'failure' ? 'text-accent-red' : 'text-gray-300'
                                  )}>
                                    {exec.outcome}
                                  </span>
                                </div>
                              )}
                              {exec.outcome_summary && (
                                <p className="mt-1 text-sm text-gray-400">{exec.outcome_summary}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Session 746: Latency Metrics */}
                    {gate.latency && (gate.latency.total_hours || gate.latency.by_stage) && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <Clock size={18} className="text-gray-400" />
                          Latency Metrics
                        </h4>
                        <div className="bg-dark-bg rounded-lg p-3">
                          {gate.latency.total_hours !== undefined && (
                            <div className="flex items-center justify-between text-sm mb-2">
                              <span className="text-gray-400">Total time:</span>
                              <span className="text-gray-300">{(gate.latency?.total_hours ?? 0).toFixed(1)} hours</span>
                            </div>
                          )}
                          {gate.latency.by_stage && Object.keys(gate.latency.by_stage).length > 0 && (
                            <div className="space-y-1 text-xs">
                              {Object.entries(gate.latency.by_stage).map(([stage, hours]) => (
                                <div key={stage} className="flex items-center justify-between">
                                  <span className="text-gray-500">{stage.replace('_', ' ')}:</span>
                                  <span className="text-gray-400">{((hours as number) ?? 0).toFixed(1)}h</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Session 697: Enhanced Checklist with AI-Generated Content */}
                    {gate.checklist_items && gate.checklist_items.length > 0 && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold flex items-center gap-2">
                            <Target size={18} className="text-primary-400" />
                            Checklist Items ({gate.checklist_items.filter((item: GateChecklistItem) => item.status === 'completed').length}/{gate.checklist_items.length})
                          </h4>
                          <div className="flex items-center gap-2">
                            <div className="w-32 h-2 bg-dark-border rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary-500 rounded-full transition-all"
                                style={{ width: `${(gate.checklist_items.filter((item: GateChecklistItem) => item.status === 'completed').length / gate.checklist_items.length) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {gate.checklist_items.map((item: GateChecklistItem) => {
                            const isExpanded = expandedChecklistItems.has(item.id)
                            return (
                              <div
                                key={item.id}
                                className={cn(
                                  'border rounded-lg overflow-hidden transition-colors',
                                  item.status === 'completed' ? 'border-accent-green/30 bg-accent-green/5' : 'border-dark-border bg-dark-bg'
                                )}
                              >
                                {/* Item Header */}
                                <div
                                  className={cn(
                                    'flex items-center justify-between p-3 cursor-pointer hover:bg-dark-hover/50 transition-colors',
                                    item.has_content && 'cursor-pointer'
                                  )}
                                  onClick={() => {
                                    if (item.has_content) {
                                      setExpandedChecklistItems(prev => {
                                        const next = new Set(prev)
                                        if (next.has(item.id)) {
                                          next.delete(item.id)
                                        } else {
                                          next.add(item.id)
                                        }
                                        return next
                                      })
                                    }
                                  }}
                                >
                                  <div className="flex items-center gap-3">
                                    <div className={cn(
                                      'h-6 w-6 rounded flex items-center justify-center flex-shrink-0',
                                      item.status === 'completed' ? 'bg-accent-green/20' : 'bg-dark-card'
                                    )}>
                                      {item.status === 'completed' ? (
                                        <CheckCircle size={14} className="text-accent-green" />
                                      ) : (
                                        <div className="h-3 w-3 rounded-full border-2 border-gray-500" />
                                      )}
                                    </div>
                                    <div>
                                      <p className={cn(
                                        'font-medium text-sm',
                                        item.status === 'completed' && 'text-accent-green'
                                      )}>
                                        {item.title}
                                      </p>
                                      <p className="text-xs text-gray-500">{item.description}</p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    {item.is_required && (
                                      <span className="text-xs px-1.5 py-0.5 rounded bg-accent-amber/20 text-accent-amber">
                                        Required
                                      </span>
                                    )}
                                    {item.has_content && (
                                      <ChevronRight
                                        size={16}
                                        className={cn(
                                          'text-gray-500 transition-transform',
                                          isExpanded && 'rotate-90'
                                        )}
                                      />
                                    )}
                                  </div>
                                </div>
                                {/* AI-Generated Content (Expandable) */}
                                {isExpanded && item.generated_content && (
                                  <div className="border-t border-dark-border p-4 bg-dark-card/50">
                                    <div className="flex items-center gap-2 mb-3 text-xs text-accent-purple">
                                      <Sparkles size={12} />
                                      <span>AI-Generated Content</span>
                                    </div>
                                    <div className="prose prose-invert prose-sm max-w-none">
                                      <pre className="whitespace-pre-wrap text-sm text-gray-300 font-sans leading-relaxed bg-transparent p-0 m-0 overflow-x-auto">
                                        {item.generated_content}
                                      </pre>
                                    </div>
                                  </div>
                                )}
                                {/* Session 746: Show completion details if expanded and completed */}
                                {isExpanded && item.status === 'completed' && (item.completed_by || item.completed_at || item.completion_notes) && (
                                  <div className="border-t border-dark-border p-4 bg-accent-green/5">
                                    <div className="flex items-center gap-2 mb-3 text-xs text-accent-green">
                                      <CheckCircle size={12} />
                                      <span>Completion Details</span>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                      {item.completed_by && (
                                        <div>
                                          <span className="text-gray-500">Completed by:</span>
                                          <span className="ml-2 text-gray-300">{item.completed_by}</span>
                                        </div>
                                      )}
                                      {item.completed_at && (
                                        <div>
                                          <span className="text-gray-500">Completed at:</span>
                                          <span className="ml-2 text-gray-300">
                                            {new Date(item.completed_at).toLocaleString()}
                                          </span>
                                        </div>
                                      )}
                                    </div>
                                    {item.completion_notes && (
                                      <div className="mt-2">
                                        <span className="text-gray-500 text-sm">Notes:</span>
                                        <p className="text-gray-300 text-sm mt-1">{item.completion_notes}</p>
                                      </div>
                                    )}
                                  </div>
                                )}
                                {/* Session 746: Show documentation link if available */}
                                {isExpanded && item.documentation_url && (
                                  <div className="border-t border-dark-border p-3 bg-dark-bg">
                                    <a
                                      href={item.documentation_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="flex items-center gap-2 text-sm text-primary-400 hover:text-primary-300"
                                    >
                                      <ExternalLink size={14} />
                                      <span>View Documentation</span>
                                    </a>
                                    {item.documentation_notes && (
                                      <p className="text-xs text-gray-500 mt-1">{item.documentation_notes}</p>
                                    )}
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                    {/* Fallback: Simple checklist progress if no items */}
                    {gate.checklist && !gate.checklist_items && (
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
                      {/* Session 692: Add Approve All Items button for incomplete checklists */}
                      {gate.status === 'in_progress' && gate.checklist_completed < gate.checklist_total && (
                        <button
                          onClick={async () => {
                            try {
                              const response = await pilotsApi.approveAllItems(gate.id)
                              if (response.data?.success) {
                                setActionResult({ type: 'success', message: `Approved ${response.data.items_approved} checklist items` })
                                await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                                await queryClient.refetchQueries({ queryKey: ['gate-detail', selectedGate] })
                              } else {
                                setActionResult({ type: 'error', message: response.data?.message || 'Failed to approve items' })
                              }
                            } catch {
                              setActionResult({ type: 'error', message: 'Failed to approve checklist items' })
                            }
                          }}
                          className="btn btn-secondary flex items-center gap-2"
                        >
                          <CheckCircle size={16} />
                          Approve All Items ({gate.checklist_total - gate.checklist_completed})
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
                      {/* Session 713: Show body health warning on approve button */}
                      {gate.status === 'ready' && (
                        <div className="flex flex-col items-end gap-2">
                          {!canStartPilot.allowed && (
                            <span className="text-xs text-amber-400 flex items-center gap-1">
                              <Heart size={12} className="animate-pulse" />
                              Warning: Body health may prevent pilot start
                            </span>
                          )}
                          <button
                            onClick={async () => {
                              approveGateMutation.mutate(gate.id)
                              await queryClient.refetchQueries({ queryKey: ['gate-detail', selectedGate] })
                            }}
                            className="btn btn-primary flex items-center gap-2"
                          >
                            <CheckCircle size={16} />
                            Approve Gate
                          </button>
                        </div>
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
                    <p className="text-gray-300">{stripHtml(opp.description)}</p>
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
                                {((learning.confidence ?? 0) * 100).toFixed(0)}% confidence
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
                                <span>{((learning.confidence ?? 0) * 100).toFixed(0)}%</span>
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

      {/* Session 692: Prediction Detail Modal */}
      {selectedPrediction && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-card border border-dark-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border">
              <div className="flex-1 min-w-0 pr-4">
                <h3 className="text-xl font-bold">{selectedPrediction.title}</h3>
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  <span className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400">
                    {selectedPrediction.category}
                  </span>
                  <span className="text-xs px-2 py-1 rounded bg-accent-cyan/20 text-accent-cyan">
                    {selectedPrediction.timeframe}
                  </span>
                  <span className={cn(
                    'text-xs px-2 py-1 rounded',
                    selectedPrediction.status === 'verified' ? 'bg-accent-green/20 text-accent-green' :
                    selectedPrediction.status === 'expired' ? 'bg-gray-500/20 text-gray-400' :
                    'bg-accent-amber/20 text-accent-amber'
                  )}>
                    {selectedPrediction.status}
                  </span>
                  {selectedPrediction.is_featured && (
                    <span className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber flex items-center gap-1">
                      <Star size={12} /> Featured
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => setSelectedPrediction(null)}
                className="p-2 hover:bg-dark-bg rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {/* Probability Gauge */}
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold flex items-center gap-2">
                    <Target size={18} className="text-primary-400" />
                    Confidence Level
                  </h4>
                  <span className={cn(
                    'text-2xl font-bold',
                    selectedPrediction.probability >= 70 ? 'text-accent-green' :
                    selectedPrediction.probability >= 50 ? 'text-accent-amber' : 'text-accent-red'
                  )}>
                    {selectedPrediction.probability}%
                  </span>
                </div>
                <div className="h-3 bg-dark-border rounded-full overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full transition-all',
                      selectedPrediction.probability >= 70 ? 'bg-accent-green' :
                      selectedPrediction.probability >= 50 ? 'bg-accent-amber' : 'bg-accent-red'
                    )}
                    style={{ width: `${selectedPrediction.probability}%` }}
                  />
                </div>
              </div>

              {/* Full Prediction Text */}
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <FileText size={18} className="text-accent-cyan" />
                  Prediction Details
                </h4>
                <div className="bg-dark-bg rounded-lg p-4">
                  <p className="text-gray-300 whitespace-pre-wrap">{selectedPrediction.prediction}</p>
                </div>
              </div>

              {/* Agent Info */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Brain size={18} className="text-primary-400" />
                  <span className="text-sm text-gray-400">Agent:</span>
                  {/* Session 713: EntityLink for agent navigation */}
                  <EntityLink
                    type="agent"
                    id={selectedPrediction.agent_name}
                    label={selectedPrediction.agent_name}
                    showIcon={false}
                    className="font-medium"
                  />
                </div>
                {selectedPrediction.agent_type && (
                  <span className="text-xs px-2 py-1 rounded bg-dark-bg text-gray-400">
                    {selectedPrediction.agent_type}
                  </span>
                )}
              </div>

              {/* Source Info */}
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <Lightbulb size={18} className="text-accent-amber" />
                  Source
                </h4>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber">
                    {selectedPrediction.source_type}
                  </span>
                  {selectedPrediction.source_reference?.dream_id && (
                    <span className="text-sm text-gray-400">
                      Dream ID: {selectedPrediction.source_reference.dream_id}
                    </span>
                  )}
                </div>
              </div>

              {/* Tags */}
              {selectedPrediction.tags && selectedPrediction.tags.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <Tag size={18} className="text-primary-400" />
                    Tags
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedPrediction.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-1 rounded-full bg-primary-600/20 text-primary-400 border border-primary-600/30"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Timing */}
              <div className="grid grid-cols-2 gap-4">
                {selectedPrediction.deadline && (
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <Clock size={18} className="text-accent-cyan" />
                      Deadline
                    </h4>
                    <p className="text-gray-300">{new Date(selectedPrediction.deadline).toLocaleDateString()}</p>
                    {selectedPrediction.days_remaining !== null && selectedPrediction.days_remaining >= 0 && (
                      <p className="text-sm text-gray-400 mt-1">
                        {selectedPrediction.days_remaining} days remaining
                      </p>
                    )}
                  </div>
                )}
                {selectedPrediction.verified_at && (
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <CheckCircle size={18} className="text-accent-green" />
                      Verified
                    </h4>
                    <p className="text-gray-300">{new Date(selectedPrediction.verified_at).toLocaleDateString()}</p>
                    {selectedPrediction.accuracy_score !== null && (
                      <p className="text-sm text-gray-400 mt-1">
                        Accuracy: {((selectedPrediction.accuracy_score ?? 0) * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* Engagement */}
              <div className="flex items-center gap-6 pt-4 border-t border-dark-border">
                <div className="flex items-center gap-2">
                  <ArrowUp size={18} className="text-accent-green" />
                  <span className="font-medium">{selectedPrediction.upvotes}</span>
                  <span className="text-sm text-gray-400">upvotes</span>
                </div>
                <div className="flex items-center gap-2">
                  <Eye size={18} className="text-gray-400" />
                  <span className="font-medium">{selectedPrediction.views}</span>
                  <span className="text-sm text-gray-400">views</span>
                </div>
              </div>

              {/* Created timestamp */}
              <div className="text-sm text-gray-500">
                Created: {new Date(selectedPrediction.created_at).toLocaleString()}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end p-6 border-t border-dark-border bg-dark-bg/50">
              <button
                onClick={() => setSelectedPrediction(null)}
                className="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 693: Experiment Detail Modal */}
      {selectedExperiment && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-card rounded-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <FlaskConical size={20} className="text-primary-400" />
                  <h3 className="text-xl font-bold truncate">{selectedExperiment.name || selectedExperiment.decision_topic}</h3>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className={cn(
                    'px-2 py-0.5 text-xs rounded font-medium',
                    selectedExperiment.status === 'running' ? 'bg-primary-500/20 text-primary-400' :
                    selectedExperiment.status === 'success' ? 'bg-accent-green/20 text-accent-green' :
                    selectedExperiment.status === 'failure' ? 'bg-accent-red/20 text-accent-red' :
                    'bg-accent-amber/20 text-accent-amber'
                  )}>
                    {selectedExperiment.status.toUpperCase()}
                  </span>
                  <span className={cn(
                    'px-2 py-0.5 text-xs rounded font-medium',
                    selectedExperiment.risk_level === 'high' ? 'bg-accent-red/20 text-accent-red' :
                    selectedExperiment.risk_level === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                    'bg-accent-green/20 text-accent-green'
                  )}>
                    {selectedExperiment.risk_level.toUpperCase()} RISK
                  </span>
                  <span className={cn(
                    'px-2 py-0.5 text-xs rounded font-medium',
                    selectedExperiment.outcome_classification === 'pending' ? 'bg-gray-500/20 text-gray-400' :
                    selectedExperiment.outcome_classification === 'positive' ? 'bg-accent-green/20 text-accent-green' :
                    'bg-accent-red/20 text-accent-red'
                  )}>
                    {selectedExperiment.outcome_classification}
                  </span>
                  {selectedExperiment.is_halted && (
                    <span className="px-2 py-0.5 text-xs rounded font-medium bg-accent-red/30 text-accent-red flex items-center gap-1">
                      <AlertOctagon size={12} />
                      HALTED
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => setSelectedExperiment(null)}
                className="p-2 hover:bg-dark-border rounded-lg transition-colors flex-shrink-0"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body - Scrollable */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              {/* Hypothesis Section */}
              {selectedExperiment.hypothesis && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">Hypothesis</h4>
                  <p className="text-gray-300 bg-dark-bg/50 rounded-lg p-4 whitespace-pre-wrap">
                    {selectedExperiment.hypothesis}
                  </p>
                </div>
              )}

              {/* KPI Progress Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-dark-bg/50 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Primary KPI</h4>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg font-medium text-primary-400">{selectedExperiment.primary_kpi}</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-accent-cyan">{selectedExperiment.current_value || '0'}</span>
                    <span className="text-gray-500">/</span>
                    <span className="text-xl text-gray-400">{selectedExperiment.target_value || '100'}</span>
                  </div>
                  {/* Progress bar */}
                  <div className="mt-3 h-2 bg-dark-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary-500 to-accent-cyan rounded-full transition-all"
                      style={{
                        width: `${Math.min(100, (parseFloat(selectedExperiment.current_value || '0') / parseFloat(selectedExperiment.target_value || '100')) * 100)}%`
                      }}
                    />
                  </div>
                </div>

                <div className="bg-dark-bg/50 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Ownership</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <User size={16} className="text-primary-400" />
                      <span className="text-gray-400">KPI Owner:</span>
                      <span className="text-gray-200 font-medium">{selectedExperiment.kpi_owner}</span>
                    </div>
                    {selectedExperiment.pilot_id && (
                      <div className="flex items-center gap-2">
                        <Rocket size={16} className="text-accent-amber" />
                        <span className="text-gray-400">Pilot ID:</span>
                        <span className="text-gray-200 font-mono text-sm">{selectedExperiment.pilot_id.slice(0, 8)}...</span>
                      </div>
                    )}
                    {selectedExperiment.decision_id && (
                      <div className="flex items-center gap-2">
                        <Target size={16} className="text-accent-green" />
                        <span className="text-gray-400">Decision ID:</span>
                        <span className="text-gray-200 font-mono text-sm">{selectedExperiment.decision_id.slice(0, 8)}...</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Timing Section */}
              <div className="bg-dark-bg/50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Timeline</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {selectedExperiment.started_at && (
                    <div>
                      <span className="text-xs text-gray-500 uppercase">Started</span>
                      <p className="text-gray-300">{new Date(selectedExperiment.started_at).toLocaleDateString()}</p>
                      <p className="text-xs text-gray-500">{new Date(selectedExperiment.started_at).toLocaleTimeString()}</p>
                    </div>
                  )}
                  {selectedExperiment.ended_at && (
                    <div>
                      <span className="text-xs text-gray-500 uppercase">Ended</span>
                      <p className="text-gray-300">{new Date(selectedExperiment.ended_at).toLocaleDateString()}</p>
                      <p className="text-xs text-gray-500">{new Date(selectedExperiment.ended_at).toLocaleTimeString()}</p>
                    </div>
                  )}
                  {selectedExperiment.started_at && !selectedExperiment.ended_at && (
                    <div>
                      <span className="text-xs text-gray-500 uppercase">Duration</span>
                      <p className="text-accent-cyan font-medium">
                        {Math.floor((Date.now() - new Date(selectedExperiment.started_at).getTime()) / (1000 * 60 * 60 * 24))} days running
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Halt Information (if halted) */}
              {selectedExperiment.is_halted && (
                <div className="bg-accent-red/10 border border-accent-red/30 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-accent-red uppercase tracking-wide mb-2 flex items-center gap-2">
                    <AlertOctagon size={16} />
                    Experiment Halted
                  </h4>
                  {selectedExperiment.halt_reason && (
                    <p className="text-gray-300 mb-2"><span className="text-gray-500">Reason:</span> {selectedExperiment.halt_reason}</p>
                  )}
                  {selectedExperiment.halted_by && (
                    <p className="text-gray-400 text-sm"><span className="text-gray-500">By:</span> {selectedExperiment.halted_by}</p>
                  )}
                  {selectedExperiment.halted_at && (
                    <p className="text-gray-400 text-sm"><span className="text-gray-500">At:</span> {new Date(selectedExperiment.halted_at).toLocaleString()}</p>
                  )}
                </div>
              )}

              {/* Extracted Metrics (if available) */}
              {selectedExperiment.extracted_metrics?.raw_content && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">
                    Extracted Metrics
                    <span className="ml-2 text-xs font-normal text-gray-500">
                      (Source: {selectedExperiment.extracted_metrics.source})
                    </span>
                  </h4>
                  <div className="bg-dark-bg/50 rounded-lg p-4 max-h-48 overflow-y-auto">
                    <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                      {selectedExperiment.extracted_metrics.raw_content}
                    </pre>
                  </div>
                </div>
              )}

              {/* Learnings (if completed) */}
              {selectedExperiment.learnings && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">Learnings</h4>
                  <p className="text-gray-300 bg-accent-green/10 border border-accent-green/30 rounded-lg p-4 whitespace-pre-wrap">
                    {selectedExperiment.learnings}
                  </p>
                </div>
              )}

              {/* Decision Topic */}
              {selectedExperiment.decision_topic && (
                <div className="pt-4 border-t border-dark-border">
                  <span className="text-xs text-gray-500 uppercase">Decision Topic</span>
                  <p className="text-gray-400 text-sm mt-1">{selectedExperiment.decision_topic}</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-6 border-t border-dark-border bg-dark-bg/50">
              <div className="text-sm text-gray-500">
                ID: <span className="font-mono">{selectedExperiment.id.slice(0, 8)}...</span>
              </div>
              <div className="flex items-center gap-2">
                {selectedExperiment.status === 'running' && !selectedExperiment.is_halted && (
                  <button
                    onClick={() => {
                      haltExperimentMutation.mutate(selectedExperiment.id)
                      setSelectedExperiment(null)
                    }}
                    className="btn btn-secondary text-accent-red flex items-center gap-1"
                    disabled={isLoading}
                  >
                    <Pause size={14} />
                    Halt Experiment
                  </button>
                )}
                <button
                  onClick={() => setSelectedExperiment(null)}
                  className="btn btn-secondary"
                >
                  Close
                </button>
              </div>
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
