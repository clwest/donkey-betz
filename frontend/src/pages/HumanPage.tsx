import { useState, useMemo, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { humanApi, agentsApi, bodyApi } from '@/lib/api'
// Session 714: Real-time system events
import { useSystemEvents } from '@/hooks/useWebSocket'
import {
  User,
  Bell,
  Sliders,
  AlertTriangle,
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Pause,
  Play,
  Moon,
  Eye,
  Bot,
  Settings,
  ChevronRight,
  ThumbsUp,
  ThumbsDown,
  Timer,
  TrendingUp,
  Activity,
  Loader2,
  RefreshCw,
  Heart,
  ExternalLink,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
interface AttentionItem {
  id: string
  source_type: string
  source_agent: string
  item_type: string
  title: string
  summary: string
  payload: Record<string, unknown>
  urgency: 'critical' | 'high' | 'medium' | 'low'
  priority_score: number
  ml_confidence: number | null
  ml_recommendation: string | null
  status: 'pending' | 'viewed' | 'acted' | 'deferred' | 'ignored' | 'expired'
  created_at: string
  expires_at: string | null
}

interface AttentionStats {
  pending_count: number
  by_urgency: Record<string, number>
  avg_decision_time_ms: number | null
  ml_agreement_rate: number | null
  total_with_ml_context: number
}

interface SystemState {
  system_paused: boolean
  review_mode: boolean
  quiet_mode: boolean
  quiet_mode_until: string | null
  paused_agents: string[]
  ml_confidence_threshold: number
  auto_approve_threshold: number
}

interface Preferences {
  quiet_hours_start: string | null
  quiet_hours_end: string | null
  min_urgency_to_notify: string
  preferred_channel: string
  review_depth: string
  auto_approve_low_risk: boolean
  require_review_above_confidence: number
  trusted_agents: string[]
  blocked_sources: string[]
  // Learned stats
  topic_weights: Record<string, number>
  avg_decision_time_ms: number | null
  approval_rate: number | null
  total_decisions: number
}

// Urgency config
const URGENCY_CONFIG = {
  critical: { color: 'bg-accent-red', textColor: 'text-accent-red', icon: AlertTriangle },
  high: { color: 'bg-accent-amber', textColor: 'text-accent-amber', icon: AlertCircle },
  medium: { color: 'bg-accent-cyan', textColor: 'text-accent-cyan', icon: Clock },
  low: { color: 'bg-gray-500', textColor: 'text-gray-400', icon: CheckCircle },
}

// Decision Modal
function DecisionModal({
  item,
  onClose,
  onDecide,
  isLoading,
}: {
  item: AttentionItem
  onClose: () => void
  onDecide: (decision: string, feedback: string, confidence: number) => void
  isLoading: boolean
}) {
  const [feedback, setFeedback] = useState('')
  const [confidence, setConfidence] = useState(80)

  const urgencyConfig = URGENCY_CONFIG[item.urgency]
  const UrgencyIcon = urgencyConfig.icon

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-lg', `${urgencyConfig.color}/20`)}>
              <UrgencyIcon className={urgencyConfig.textColor} size={20} />
            </div>
            <div>
              <h3 className="font-semibold">{item.title}</h3>
              <p className="text-sm text-gray-400">{item.source_agent || item.source_type}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">&times;</button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          <div className="prose prose-invert max-w-none">
            <p className="text-gray-300">{item.summary}</p>
          </div>

          {/* ML Recommendation */}
          {item.ml_recommendation && (
            <div className="flex items-center gap-3 p-3 rounded-lg bg-primary-500/10 border border-primary-500/30">
              <Bot className="text-primary-400" size={20} />
              <div>
                <p className="text-sm font-medium text-primary-400">ML Recommendation</p>
                <p className="text-sm text-gray-300">
                  {item.ml_recommendation}
                  {item.ml_confidence && (
                    <span className="ml-2 text-gray-500">
                      ({Math.round(item.ml_confidence * 100)}% confidence)
                    </span>
                  )}
                </p>
              </div>
            </div>
          )}

          {/* Feedback */}
          <div>
            <label className="block text-sm font-medium mb-2">Your Notes (Optional)</label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
              rows={3}
              placeholder="Add any notes about your decision..."
            />
          </div>

          {/* Confidence Slider */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Your Confidence: {confidence}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={confidence}
              onChange={(e) => setConfidence(parseInt(e.target.value))}
              className="w-full accent-primary-500"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2 p-4 border-t border-dark-border">
          <button
            onClick={() => onDecide('approve', feedback, confidence / 100)}
            disabled={isLoading}
            className="btn btn-primary flex items-center gap-2"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <ThumbsUp size={16} />}
            Approve
          </button>
          <button
            onClick={() => onDecide('reject', feedback, confidence / 100)}
            disabled={isLoading}
            className="btn flex items-center gap-2 bg-accent-red/20 text-accent-red hover:bg-accent-red/30"
          >
            <ThumbsDown size={16} />
            Reject
          </button>
          <button
            onClick={() => onDecide('modify', feedback, confidence / 100)}
            disabled={isLoading}
            className="btn btn-secondary"
          >
            Modify
          </button>
          <button
            onClick={() => onDecide('defer', feedback, confidence / 100)}
            disabled={isLoading}
            className="btn btn-secondary"
          >
            Defer
          </button>
          <button
            onClick={() => onDecide('escalate', feedback, confidence / 100)}
            disabled={isLoading}
            className="btn flex items-center gap-2 bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30"
          >
            <AlertTriangle size={16} />
            Escalate
          </button>
        </div>
      </div>
    </div>
  )
}

export default function HumanPage() {
  const [activeTab, setActiveTab] = useState<'attention' | 'control' | 'preferences'>('attention')
  const [selectedItem, setSelectedItem] = useState<AttentionItem | null>(null)
  const [urgencyFilter, setUrgencyFilter] = useState<string[]>([])
  const [localPrefs, setLocalPrefs] = useState<Partial<Preferences>>({})
  const queryClient = useQueryClient()

  // Session 714: Real-time event handlers - refresh data when events occur
  const handleGateBecameCritical = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['human-attention'] })
    queryClient.invalidateQueries({ queryKey: ['human-attention-stats'] })
    queryClient.invalidateQueries({ queryKey: ['human-control'] })
  }, [queryClient])

  const handleBodyStatusChanged = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['body-vitals'] })
  }, [queryClient])

  const handlePilotEvent = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['human-attention'] })
    queryClient.invalidateQueries({ queryKey: ['human-attention-stats'] })
  }, [queryClient])

  // Session 714: Subscribe to system events
  useSystemEvents({
    onGateBecameCritical: handleGateBecameCritical,
    onBodyStatusChanged: handleBodyStatusChanged,
    onPilotStarted: handlePilotEvent,
    onPilotCompleted: handlePilotEvent,
  })

  // REST API queries
  const { data: attentionResponse, isLoading: loadingAttention, refetch: refetchAttention, error: attentionError } = useQuery({
    queryKey: ['human-attention', urgencyFilter],
    queryFn: () => humanApi.attention({ limit: 50, urgency: urgencyFilter.length > 0 ? urgencyFilter : undefined }),
  })

  // Debug: Log API response
  if (attentionError) {
    console.error('Human Attention API Error:', attentionError)
  }
  if (attentionResponse) {
    console.log('Human Attention API Response:', attentionResponse.data)
  }

  const { data: statsResponse, isLoading: loadingStats } = useQuery({
    queryKey: ['human-attention-stats'],
    queryFn: () => humanApi.attentionStats(),
  })

  const { data: controlResponse, isLoading: loadingControl, refetch: refetchControl } = useQuery({
    queryKey: ['human-control'],
    queryFn: () => humanApi.control(),
  })

  const { data: preferencesResponse, isLoading: loadingPreferences } = useQuery({
    queryKey: ['human-preferences'],
    queryFn: () => humanApi.preferences(),
  })

  const { data: agentsResponse } = useQuery({
    queryKey: ['agents-list'],
    queryFn: () => agentsApi.list(),
  })

  // Session 712: Body Health integration - connect consciousness to body
  const { data: bodyVitalsResponse } = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 60000, // Refresh every 60 seconds
  })

  // Mutations
  const decideMutation = useMutation({
    mutationFn: ({ itemId, decision, feedback, confidence }: { itemId: string; decision: string; feedback: string; confidence: number }) =>
      humanApi.decide(itemId, decision, feedback, confidence),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['human-attention'] })
      queryClient.invalidateQueries({ queryKey: ['human-attention-stats'] })
      setSelectedItem(null)
    },
  })

  const pauseAgentMutation = useMutation({
    mutationFn: ({ agent, reason }: { agent: string; reason?: string }) => humanApi.pauseAgent(agent, reason),
    onSuccess: () => refetchControl(),
  })

  const resumeAgentMutation = useMutation({
    mutationFn: ({ agent, reason }: { agent: string; reason?: string }) => humanApi.resumeAgent(agent, reason),
    onSuccess: () => refetchControl(),
  })

  const quietModeMutation = useMutation({
    mutationFn: ({ enabled, duration }: { enabled: boolean; duration?: number }) =>
      humanApi.setQuietMode(enabled, duration),
    onSuccess: () => refetchControl(),
  })

  const reviewModeMutation = useMutation({
    mutationFn: (enabled: boolean) => humanApi.setReviewMode(enabled),
    onSuccess: () => refetchControl(),
  })

  const thresholdMutation = useMutation({
    mutationFn: (threshold: number) => humanApi.adjustThreshold(threshold),
    onSuccess: () => refetchControl(),
  })

  const updatePrefsMutation = useMutation({
    mutationFn: (data: Partial<Preferences>) => humanApi.updatePreferences(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['human-preferences'] })
      setLocalPrefs({})
    },
  })

  // Helper to update a preference
  const updatePref = (key: keyof Preferences, value: unknown) => {
    const newPrefs = { ...localPrefs, [key]: value }
    setLocalPrefs(newPrefs)
    updatePrefsMutation.mutate({ [key]: value })
  }

  // Data extraction
  const attentionItems: AttentionItem[] = attentionResponse?.data?.items || []
  const stats: AttentionStats = statsResponse?.data?.stats || {}
  const systemState: SystemState = controlResponse?.data?.state || {}
  const preferences: Preferences = preferencesResponse?.data?.preferences || {}
  const agentsList = agentsResponse?.data?.agents || []

  // Session 712: Body health data
  const bodyVitals = bodyVitalsResponse?.data || null
  const bodyHealthScore = bodyVitals?.health_score || 0
  const bodyOverallStatus = bodyVitals?.overall_health || 'unknown'
  const bodySystems = bodyVitals?.systems || {}

  // Group items by urgency
  const groupedItems = useMemo(() => {
    const groups: Record<string, AttentionItem[]> = {
      critical: [],
      high: [],
      medium: [],
      low: [],
    }
    attentionItems.forEach((item) => {
      groups[item.urgency]?.push(item)
    })
    return groups
  }, [attentionItems])

  const isLoading = loadingAttention || loadingStats || loadingControl || loadingPreferences

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  // Show error if API call failed
  if (attentionError) {
    return (
      <div className="card text-center py-12">
        <XCircle className="mx-auto mb-4 text-accent-red" size={48} />
        <h3 className="text-lg font-semibold mb-2">Failed to Load Attention Items</h3>
        <p className="text-gray-400 mb-4">
          {(attentionError as Error)?.message || 'Authentication may be required. Please log in again.'}
        </p>
        <button
          onClick={() => refetchAttention()}
          className="btn btn-primary"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-primary-500/20 flex items-center justify-center">
            <User size={24} className="text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Human Interface</h1>
            <p className="text-sm text-gray-400">Your control center for the AI ecosystem</p>
          </div>
        </div>

        {/* System Status Indicators */}
        <div className="flex items-center gap-3">
          {systemState.quiet_mode && (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent-purple/20 text-accent-purple text-sm">
              <Moon size={14} />
              Quiet Mode
            </span>
          )}
          {systemState.review_mode && (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent-amber/20 text-accent-amber text-sm">
              <Eye size={14} />
              Review Mode
            </span>
          )}
          {systemState.system_paused && (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent-red/20 text-accent-red text-sm">
              <Pause size={14} />
              System Paused
            </span>
          )}
        </div>
      </div>

      {/* Session 712: Body Health Card - Consciousness connected to Body */}
      {bodyVitals && (
        <a
          href="/body-health"
          className="card hover:border-primary-500/50 transition-colors group cursor-pointer block"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={cn(
                'h-12 w-12 rounded-full flex items-center justify-center',
                bodyHealthScore >= 80 ? 'bg-accent-green/20' :
                bodyHealthScore >= 60 ? 'bg-accent-amber/20' :
                bodyHealthScore >= 40 ? 'bg-accent-orange/20' : 'bg-accent-red/20'
              )}>
                <Heart className={cn(
                  'animate-pulse',
                  bodyHealthScore >= 80 ? 'text-accent-green' :
                  bodyHealthScore >= 60 ? 'text-accent-amber' :
                  bodyHealthScore >= 40 ? 'text-accent-orange' : 'text-accent-red'
                )} size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-400">Body Health</p>
                <p className="text-2xl font-bold">{Math.round(bodyHealthScore)}%</p>
                <p className={cn(
                  'text-sm capitalize',
                  bodyOverallStatus === 'healthy' ? 'text-accent-green' :
                  bodyOverallStatus === 'degraded' ? 'text-accent-amber' : 'text-accent-red'
                )}>
                  {bodyOverallStatus}
                </p>
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              {/* System emoji strip */}
              <div className="flex gap-1 text-lg">
                {Object.entries(bodySystems).map(([name, system]: [string, any]) => (
                  <span key={name} title={`${name}: ${system.status}`}>
                    {system.emoji || '❓'}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-1 text-sm text-gray-400 group-hover:text-primary-400">
                <span>View Details</span>
                <ExternalLink size={14} />
              </div>
            </div>
          </div>
        </a>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <Bell className="text-accent-amber" size={24} />
            <div>
              <p className="text-sm text-gray-400">Pending</p>
              <p className="text-2xl font-bold">{stats.pending_count || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-accent-red" size={24} />
            <div>
              <p className="text-sm text-gray-400">Urgent</p>
              <p className="text-2xl font-bold">
                {(stats.by_urgency?.critical || 0) + (stats.by_urgency?.high || 0)}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Timer className="text-accent-cyan" size={24} />
            <div>
              <p className="text-sm text-gray-400">Avg Decision Time</p>
              <p className="text-2xl font-bold">
                {stats.avg_decision_time_ms ? `${Math.round(stats.avg_decision_time_ms / 1000)}s` : '--'}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <TrendingUp className="text-accent-green" size={24} />
            <div>
              <p className="text-sm text-gray-400">ML Agreement</p>
              <p className="text-2xl font-bold">
                {stats.ml_agreement_rate ? `${Math.round(stats.ml_agreement_rate * 100)}%` : '--'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-dark-border pb-4">
        {[
          { id: 'attention', label: 'Attention Stream', icon: Bell },
          { id: 'control', label: 'Control Panel', icon: Sliders },
          { id: 'preferences', label: 'Preferences', icon: Settings },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as typeof activeTab)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-card'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'attention' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              {(['critical', 'high', 'medium', 'low'] as const).map((urgency) => {
                const config = URGENCY_CONFIG[urgency]
                const isSelected = urgencyFilter.includes(urgency)
                return (
                  <button
                    key={urgency}
                    onClick={() => {
                      setUrgencyFilter((prev) =>
                        isSelected ? prev.filter((u) => u !== urgency) : [...prev, urgency]
                      )
                    }}
                    className={cn(
                      'px-3 py-1.5 rounded-lg text-sm capitalize transition-colors',
                      isSelected
                        ? `${config.color} text-white`
                        : `${config.color}/20 ${config.textColor} hover:${config.color}/30`
                    )}
                  >
                    {urgency}
                  </button>
                )
              })}
            </div>
            <button
              onClick={() => refetchAttention()}
              className="flex items-center gap-2 text-sm text-gray-400 hover:text-white"
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>

          {/* Attention Items by Urgency */}
          {attentionItems.length === 0 ? (
            <div className="card text-center py-12">
              <CheckCircle className="mx-auto mb-4 text-accent-green" size={48} />
              <h3 className="text-lg font-semibold mb-2">All Clear!</h3>
              <p className="text-gray-400">No items requiring your attention right now.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {Object.entries(groupedItems)
                .filter(([, items]) => items.length > 0)
                .map(([urgency, items]) => {
                  const config = URGENCY_CONFIG[urgency as keyof typeof URGENCY_CONFIG]
                  const UrgencyIcon = config.icon
                  return (
                    <div key={urgency} className="card p-0 overflow-hidden">
                      <div className={cn('flex items-center gap-2 px-4 py-3', `${config.color}/20`)}>
                        <UrgencyIcon className={config.textColor} size={18} />
                        <span className={cn('font-medium capitalize', config.textColor)}>
                          {urgency}
                        </span>
                        <span className="text-sm text-gray-400">({items.length})</span>
                      </div>
                      <div className="divide-y divide-dark-border">
                        {items.map((item) => (
                          <div
                            key={item.id}
                            onClick={() => setSelectedItem(item)}
                            className="flex items-start gap-4 p-4 hover:bg-dark-hover cursor-pointer transition-colors"
                          >
                            <div className={cn('p-2 rounded-lg', `${config.color}/20`)}>
                              <Activity className={config.textColor} size={16} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-medium">{item.title}</h4>
                              <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                                {item.summary}
                              </p>
                              <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                                <span>{item.source_agent || item.source_type}</span>
                                <span>{new Date(item.created_at).toLocaleString()}</span>
                                {item.ml_confidence && (
                                  <span className="px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
                                    ML: {Math.round(item.ml_confidence * 100)}%
                                  </span>
                                )}
                              </div>
                            </div>
                            <ChevronRight className="text-gray-500" size={18} />
                          </div>
                        ))}
                      </div>
                    </div>
                  )
                })}
            </div>
          )}
        </div>
      )}

      {activeTab === 'control' && (
        <div className="space-y-4">
          {/* Global Controls */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">System Controls</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Quiet Mode */}
              <div className="p-4 rounded-lg bg-dark-bg border border-dark-border">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Moon className="text-accent-purple" size={18} />
                    <span className="font-medium">Quiet Mode</span>
                  </div>
                  <button
                    onClick={() => quietModeMutation.mutate({ enabled: !systemState.quiet_mode })}
                    disabled={quietModeMutation.isPending}
                    className={cn(
                      'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                      systemState.quiet_mode
                        ? 'bg-accent-purple text-white'
                        : 'bg-dark-card text-gray-400 hover:bg-dark-hover'
                    )}
                  >
                    {systemState.quiet_mode ? 'ON' : 'OFF'}
                  </button>
                </div>
                <p className="text-xs text-gray-500">Suppress non-critical notifications</p>
              </div>

              {/* Review Mode */}
              <div className="p-4 rounded-lg bg-dark-bg border border-dark-border">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Eye className="text-accent-amber" size={18} />
                    <span className="font-medium">Review Mode</span>
                  </div>
                  <button
                    onClick={() => reviewModeMutation.mutate(!systemState.review_mode)}
                    disabled={reviewModeMutation.isPending}
                    className={cn(
                      'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                      systemState.review_mode
                        ? 'bg-accent-amber text-white'
                        : 'bg-dark-card text-gray-400 hover:bg-dark-hover'
                    )}
                  >
                    {systemState.review_mode ? 'ON' : 'OFF'}
                  </button>
                </div>
                <p className="text-xs text-gray-500">Require approval for all decisions</p>
              </div>

              {/* ML Threshold */}
              <div className="p-4 rounded-lg bg-dark-bg border border-dark-border">
                <div className="flex items-center gap-2 mb-3">
                  <Bot className="text-primary-400" size={18} />
                  <span className="font-medium">ML Threshold</span>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={Math.round((systemState.ml_confidence_threshold || 0.6) * 100)}
                    onChange={(e) => thresholdMutation.mutate(parseInt(e.target.value) / 100)}
                    className="flex-1 accent-primary-500"
                  />
                  <span className="text-sm font-medium w-12">
                    {Math.round((systemState.ml_confidence_threshold || 0.6) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Paused Agents */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Agent Control</h3>
            <div className="space-y-2 max-h-[400px] overflow-auto">
              {agentsList.slice(0, 20).map((agent: { name: string; description?: string }) => {
                const isPaused = systemState.paused_agents?.includes(agent.name)
                return (
                  <div
                    key={agent.name}
                    className="flex items-center justify-between p-3 rounded-lg bg-dark-bg"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-2 w-2 rounded-full',
                        isPaused ? 'bg-accent-red' : 'bg-accent-green'
                      )} />
                      <span>{agent.name}</span>
                    </div>
                    <button
                      onClick={() =>
                        isPaused
                          ? resumeAgentMutation.mutate({ agent: agent.name })
                          : pauseAgentMutation.mutate({ agent: agent.name })
                      }
                      disabled={pauseAgentMutation.isPending || resumeAgentMutation.isPending}
                      className={cn(
                        'flex items-center gap-1 px-3 py-1 rounded text-sm transition-colors',
                        isPaused
                          ? 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30'
                          : 'bg-accent-red/20 text-accent-red hover:bg-accent-red/30'
                      )}
                    >
                      {isPaused ? (
                        <>
                          <Play size={12} /> Resume
                        </>
                      ) : (
                        <>
                          <Pause size={12} /> Pause
                        </>
                      )}
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'preferences' && (
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Notification Preferences</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Minimum Urgency to Notify</label>
                <select
                  value={localPrefs.min_urgency_to_notify ?? preferences.min_urgency_to_notify ?? 'medium'}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  onChange={(e) => updatePref('min_urgency_to_notify', e.target.value)}
                >
                  <option value="critical">Critical Only</option>
                  <option value="high">High and Above</option>
                  <option value="medium">Medium and Above</option>
                  <option value="low">All</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Preferred Channel</label>
                <select
                  value={localPrefs.preferred_channel ?? preferences.preferred_channel ?? 'discord'}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  onChange={(e) => updatePref('preferred_channel', e.target.value)}
                >
                  <option value="discord">Discord</option>
                  <option value="web">Web Dashboard</option>
                  <option value="email">Email</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Review Depth</label>
                <select
                  value={localPrefs.review_depth ?? preferences.review_depth ?? 'standard'}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  onChange={(e) => updatePref('review_depth', e.target.value)}
                >
                  <option value="quick">Quick (&lt; 30s)</option>
                  <option value="standard">Standard (30s-2min)</option>
                  <option value="thorough">Thorough (&gt; 2min)</option>
                </select>
              </div>
              <div className="flex items-center justify-between p-4 rounded-lg bg-dark-bg">
                <span>Auto-approve Low Risk Items</span>
                <button
                  onClick={() => updatePref('auto_approve_low_risk', !preferences.auto_approve_low_risk)}
                  className={cn(
                    'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                    preferences.auto_approve_low_risk
                      ? 'bg-accent-green text-white'
                      : 'bg-dark-card text-gray-400 hover:bg-dark-hover'
                  )}
                >
                  {preferences.auto_approve_low_risk ? 'ON' : 'OFF'}
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Quiet Hours</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Start Time</label>
                <input
                  type="time"
                  value={localPrefs.quiet_hours_start ?? preferences.quiet_hours_start ?? '22:00'}
                  onChange={(e) => updatePref('quiet_hours_start', e.target.value)}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">End Time</label>
                <input
                  type="time"
                  value={localPrefs.quiet_hours_end ?? preferences.quiet_hours_end ?? '08:00'}
                  onChange={(e) => updatePref('quiet_hours_end', e.target.value)}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Your Stats</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 rounded-lg bg-dark-bg">
                <p className="text-2xl font-bold">{preferences.total_decisions || 0}</p>
                <p className="text-sm text-gray-400">Total Decisions</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <p className="text-2xl font-bold">
                  {preferences.avg_decision_time_ms ? `${Math.round(preferences.avg_decision_time_ms / 1000)}s` : '--'}
                </p>
                <p className="text-sm text-gray-400">Avg Decision Time</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <p className="text-2xl font-bold">
                  {preferences.approval_rate ? `${Math.round(preferences.approval_rate * 100)}%` : '--'}
                </p>
                <p className="text-sm text-gray-400">Approval Rate</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Decision Modal */}
      {selectedItem && (
        <DecisionModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
          onDecide={(decision, feedback, confidence) =>
            decideMutation.mutate({
              itemId: selectedItem.id,
              decision,
              feedback,
              confidence,
            })
          }
          isLoading={decideMutation.isPending}
        />
      )}
    </div>
  )
}
