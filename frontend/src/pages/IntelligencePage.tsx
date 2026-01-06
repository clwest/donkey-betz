import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { intelligenceApi, pilotsApi, experimentsApi, learningApi, spidersApi, agentsApi } from '@/lib/api'
import {
  Brain, TrendingUp, AlertTriangle, Zap, CheckCircle, XCircle,
  Play, Pause, RefreshCw, Eye, ChevronRight, Loader2, Activity,
  BookOpen, Target, BarChart3, Globe, Bot, Sparkles
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
  decision_topic: string
  decision_type: string
  status: string  // running, completed, failed, etc.
  risk_level: string
  hours_running?: number
  auto_complete_in_hours?: number
  outcome?: string
  started_at?: string
  completed_at?: string
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
  })

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

  const status = statusData?.data || {}
  const opportunities = opportunitiesData?.data?.opportunities || []
  const gates: Gate[] = gatesData?.data?.gates || []
  // Pilots API returns running_pilots and completed_pilots separately
  const runningPilots = pilotsData?.data?.running_pilots || []
  const completedPilots = pilotsData?.data?.completed_pilots || []
  const pilots: Pilot[] = [...runningPilots, ...completedPilots]
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
                    {gate.status === 'in_progress' && (
                      <button
                        className="btn btn-secondary text-sm flex items-center gap-1"
                        onClick={async (e) => {
                          e.stopPropagation()
                          try {
                            await pilotsApi.updateGateStatus(gate.id, 'ready')
                            setActionResult({ type: 'success', message: 'Gate marked ready!' })
                            await queryClient.refetchQueries({ queryKey: ['pilot-gates'] })
                          } catch {
                            setActionResult({ type: 'error', message: 'Failed to mark ready' })
                          }
                        }}
                        disabled={isLoading}
                      >
                        <CheckCircle size={14} />
                        Mark Ready
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
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Running Pilots</h3>
          {loadingPilots ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin" size={24} />
            </div>
          ) : pilots.length > 0 ? (
            <div className="space-y-3">
              {pilots.map((pilot) => (
                <div
                  key={pilot.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      'h-10 w-10 rounded-lg flex items-center justify-center',
                      pilot.status === 'running' ? 'bg-accent-green/20' :
                      pilot.status === 'completed' ? 'bg-accent-cyan/20' : 'bg-accent-red/20'
                    )}>
                      {pilot.status === 'running' ? (
                        <Play size={20} className="text-accent-green" />
                      ) : pilot.status === 'completed' ? (
                        <CheckCircle size={20} className="text-accent-cyan" />
                      ) : (
                        <XCircle size={20} className="text-accent-red" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{pilot.decision_topic}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{pilot.decision_type}</span>
                        {pilot.hours_running !== undefined && (
                          <span className="text-xs text-gray-500">{pilot.hours_running}h running</span>
                        )}
                        {pilot.outcome && (
                          <span className={cn(
                            'text-xs px-2 py-0.5 rounded',
                            pilot.outcome === 'success' ? 'bg-accent-green/20 text-accent-green' :
                            pilot.outcome === 'failure' ? 'bg-accent-red/20 text-accent-red' : 'bg-accent-amber/20 text-accent-amber'
                          )}>{pilot.outcome}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'px-2 py-1 text-xs rounded',
                      pilot.status === 'running' ? 'bg-accent-green/20 text-accent-green' :
                      pilot.status === 'completed' ? 'bg-accent-cyan/20 text-accent-cyan' : 'bg-accent-red/20 text-accent-red'
                    )}>
                      {pilot.status}
                    </span>
                    <button className="btn btn-secondary text-sm">
                      <Eye size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Play className="mx-auto mb-2" size={32} />
              <p>No running pilots</p>
              <p className="text-sm text-gray-500 mt-1">Start a pilot from the Gates tab</p>
            </div>
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
                onClick={() => setActionResult({ type: 'success', message: `Viewing opportunity: ${opp.title}` })}
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

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
