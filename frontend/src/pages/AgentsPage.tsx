import { useState, useMemo, useCallback } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { agentsApi, activityApi, dreamsApi, conversationsApi, decisionsApi, experimentsApi } from '@/lib/api'
import { useAgentUpdates, useLearningFeed, useSystemEvents, type AgentUpdate, type LearningEvent } from '@/hooks/useWebSocket'
import { Bot, Activity, CheckCircle, Wifi, WifiOff, Zap, Search, ChevronDown, ChevronRight, Layers, MessageSquare, Brain, Sparkles, Users, Clock, RefreshCw, Trophy, ThumbsUp, TrendingUp, X, Eye, Lightbulb } from 'lucide-react'
import { cn } from '@/lib/cn'
// Session 713: Cross-page navigation
import { CompactBreadcrumb } from '@/components/Breadcrumb'

// Session 688: Safe date formatter to handle invalid/missing timestamps
const formatTimestamp = (timestamp: string | number | undefined | null, format: 'time' | 'full' = 'time'): string => {
  if (!timestamp) return 'Just now'
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) return 'Just now'
  return format === 'time' ? date.toLocaleTimeString() : date.toLocaleString()
}

// Session 688: Extract timestamp from WebSocket update (may be nested in data)
const getUpdateTimestamp = (update: AgentUpdate): string | undefined => {
  // Try direct timestamp first, then nested in data
  return update.timestamp || (update.data as Record<string, unknown>)?.timestamp as string
}

// Session 688: Extract agent name from WebSocket update (may be nested)
const getUpdateAgentName = (update: AgentUpdate): string => {
  return update.agent_name || (update.data as Record<string, unknown>)?.agent_type as string || 'Agent'
}

// Session 688: Extract message from WebSocket update (may be nested)
const getUpdateMessage = (update: AgentUpdate): string | undefined => {
  return update.message || (update.data as Record<string, unknown>)?.message as string
}

// Session 688: Extract status from WebSocket update (may be nested)
const getUpdateStatus = (update: AgentUpdate): string => {
  return update.status || (update.data as Record<string, unknown>)?.stage as string || 'active'
}

// Session 694: Learning feed item with rich data
interface LearningFeedItem {
  id?: string
  timestamp: string
  type: string
  source: string
  description: string
  teacher?: string
  student?: string
  knowledge?: string
  knowledge_full?: {
    title: string
    summary: string
    key_insights: string[]
    knowledge_type: string
    confidence: number
  }
  key_points?: string[]
  was_useful?: boolean
  usefulness_score?: number
  effectiveness_gain?: number
}

// Session 694: Top learner from API
interface TopLearner {
  name: string
  knowledge_count: number
  effectiveness: number
  teaches: number
  learns_from: number
}

// Activity item from the recent-activity API
interface RecentActivity {
  id?: string
  type: 'dream' | 'conversation' | 'decision' | 'pilot' | 'knowledge'
  icon: string
  title: string
  subtitle: string
  timestamp: string
  timestamp_display?: string  // Session 694: Friendly format like "20m ago"
  agent_name?: string
  agents?: string[]  // Session 694: List of participating agents
  data?: Record<string, unknown>
}

// Session 695: Dream interface for Dream Gallery Modal
interface Dream {
  id: string
  agent_id: string
  agent_name: string
  title: string
  content: string
  dream_type: 'observation' | 'prediction' | 'insight' | 'reflection'
  inspiration: string
  related_topics: string[]
  vividness: number
  creativity: number
  shown_to_user: boolean
  user_reaction: string
  dreamed_at: string
}

// Session 695: Conversation interface for Conversation Thread Viewer
interface ConversationMessage {
  id: string
  agent: string
  agent_emoji: string
  content: string
  type: 'question' | 'answer' | 'synthesis' | 'opening' | 'response'
  sequence: number
  relevance: number
  created_at: string
}

interface ConversationParticipant {
  name: string
  emoji: string
}

interface Conversation {
  id: string
  topic: string
  type: string
  type_display: string
  trigger: string
  status: 'active' | 'concluded' | 'abandoned'
  initiator: string
  initiator_emoji: string
  participants: ConversationParticipant[]
  message_count: number
  quality_score: number
  conclusion: string
  insights: string[]
  started_at: string
  ended_at: string | null
  messages: ConversationMessage[]
}

// Session 696: Decision interface for Decision Insights Panel
interface Decision {
  id: string
  topic: string
  decision_type: 'experiment' | 'pipeline' | 'guideline' | 'feature' | 'process'
  decision_type_display: string
  impact_area: string
  impact_area_display: string
  key_insights: string[]
  recommended_stance: string
  suggested_feature: string
  rationale: string
  participants: string[]
  status: 'draft' | 'approved' | 'rejected' | 'implemented'
  is_canonical: boolean
  promoted_at: string | null
  promoted_by: string | null
  source_type: string
  source_id: string | null
  source_topic: string | null
  created_at: string
}

// Session 696: Experiment interface for Pilot Activity Modal
interface Experiment {
  id: string
  name: string
  hypothesis: string
  status: 'running' | 'success' | 'failure' | 'halted'
  kpi_owner: string
  primary_kpi: string
  target_value: string
  current_value: string
  secondary_kpis: string[]
  extracted_metrics: {
    raw_content: string
    source: string
  } | null
  started_at: string
  ended_at: string | null
  learnings: string | null
  pilot_id: string
  decision_topic: string
  decision_id: string
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  is_halted: boolean
  halted_at: string | null
  halted_by: string
  halt_reason: string
  outcome_classification: 'pending' | 'success' | 'failure'
}

interface Agent {
  name: string
  category: string
  description: string
  keywords: string[]
  examples: string[]
  is_routable: boolean
  is_active: boolean
  priority: number
}

interface AgentsResponse {
  success: boolean
  data: {
    agents: Agent[]
    categories: Record<string, Agent[]>
    stats: {
      total: number
      routable: number
      categories_count: number
    }
  }
}

// Category display names and colors
const CATEGORY_CONFIG: Record<string, { name: string; color: string }> = {
  creation: { name: 'Creation', color: 'bg-accent-purple' },
  editing: { name: 'Editing', color: 'bg-accent-pink' },
  research: { name: 'Research', color: 'bg-accent-cyan' },
  analysis: { name: 'Analysis', color: 'bg-accent-blue' },
  strategy: { name: 'Strategy', color: 'bg-accent-green' },
  executive: { name: 'Executive', color: 'bg-accent-amber' },
  development: { name: 'Development', color: 'bg-primary-500' },
  security: { name: 'Security', color: 'bg-accent-red' },
  training: { name: 'Training', color: 'bg-accent-teal' },
  legal: { name: 'Legal', color: 'bg-gray-500' },
  orchestration: { name: 'Orchestration', color: 'bg-indigo-500' },
  audit: { name: 'Audit', color: 'bg-orange-500' },
  system: { name: 'System', color: 'bg-emerald-500' },
  content_creation: { name: 'Content', color: 'bg-violet-500' },
  general: { name: 'Specialized', color: 'bg-slate-500' },
}

export default function AgentsPage() {
  const [realtimeUpdates, setRealtimeUpdates] = useState<AgentUpdate[]>([])
  const [learningEvents, setLearningEvents] = useState<LearningEvent[]>([])
  const [activeTab, setActiveTab] = useState<'directory' | 'activity' | 'learning'>('directory')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['creation', 'research', 'strategy']))
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  // Session 695: Dream Gallery Modal state
  const [selectedDream, setSelectedDream] = useState<Dream | null>(null)
  // Session 695: Conversation Thread Viewer state
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  // Session 696: Decision Insights Panel state
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null)
  // Session 696: Experiment Modal state (for "pilot" activities)
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null)
  // Session 697: Knowledge Transfer Modal state
  const [selectedTransfer, setSelectedTransfer] = useState<LearningFeedItem | null>(null)

  const queryClient = useQueryClient()

  // Session 714: Real-time event handlers - refresh data when events occur
  const handleDreamGenerated = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['agent-dreams'] })
    queryClient.invalidateQueries({ queryKey: ['recent-activity'] })
  }, [queryClient])

  const handleLevelUp = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['agents-comprehensive'] })
    queryClient.invalidateQueries({ queryKey: ['recent-activity'] })
  }, [queryClient])

  const handleAgentExecution = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['recent-activity'] })
    queryClient.invalidateQueries({ queryKey: ['learning-activity'] })
  }, [queryClient])

  // Session 714: Subscribe to system events
  useSystemEvents({
    onDreamGenerated: handleDreamGenerated,
    onLevelUp: handleLevelUp,
    onAgentExecutionComplete: handleAgentExecution,
    onAgentExecutionFailed: handleAgentExecution,
  })

  // REST API queries - use comprehensive endpoint
  const { data: agentsResponse, isLoading } = useQuery<{ data: AgentsResponse }>({
    queryKey: ['agents-comprehensive'],
    queryFn: () => agentsApi.comprehensive(),
  })

  // Recent activity from REST API
  const { data: recentActivityResponse, refetch: refetchActivity, isRefetching: isRefetchingActivity } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => activityApi.recent(30, 72),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Learning activity from REST API
  const { data: learningActivityResponse, refetch: refetchLearning, isRefetching: isRefetchingLearning } = useQuery({
    queryKey: ['learning-activity'],
    queryFn: () => activityApi.learning(30),
    refetchInterval: 30000,
  })

  // Session 695: Dreams for Dream Gallery Modal
  const { data: dreamsResponse } = useQuery({
    queryKey: ['agent-dreams'],
    queryFn: () => dreamsApi.list(50),
    refetchInterval: 60000, // Refresh every minute
  })
  const dreams: Dream[] = dreamsResponse?.data?.dreams || []
  const dreamStats = {
    todayCount: dreamsResponse?.data?.today_count || 0,
    unreadCount: dreamsResponse?.data?.unread_count || 0,
  }

  // Session 695: Conversations for Conversation Thread Viewer
  const { data: conversationsResponse } = useQuery({
    queryKey: ['agent-conversations'],
    queryFn: () => conversationsApi.list(50),
    refetchInterval: 60000,
  })
  const conversations: Conversation[] = conversationsResponse?.data?.conversations || []

  // Session 696: Decisions for Decision Insights Panel
  const { data: decisionsResponse } = useQuery({
    queryKey: ['boardroom-decisions'],
    queryFn: () => decisionsApi.list(50),
    refetchInterval: 60000,
  })
  const decisions: Decision[] = decisionsResponse?.data?.decisions || []

  // Session 696: Experiments for Pilot Activity Modal (pilot activities are experiments)
  const { data: experimentsResponse } = useQuery({
    queryKey: ['pilot-experiments'],
    queryFn: () => experimentsApi.list(),
    refetchInterval: 60000,
  })
  const experiments: Experiment[] = experimentsResponse?.data?.experiments || []

  // WebSocket connections
  const { status: agentWsStatus } = useAgentUpdates((update) => {
    // Session 688: Filter out connection messages - only show real agent activity
    // Cast to string for runtime check since WebSocket may send types not in the union
    const msgType = update.type as string
    if (msgType === 'connection_established' || msgType === 'pong') {
      return
    }
    setRealtimeUpdates((prev) => [update, ...prev].slice(0, 50))
  })

  const { status: learningWsStatus } = useLearningFeed((event) => {
    // Session 688: Filter out connection messages - only show real learning events
    // Cast to string for runtime check since WebSocket may send types not in the union
    const msgType = event.type as string
    if (msgType === 'connection_established' || msgType === 'pong') {
      return
    }
    setLearningEvents((prev) => [event, ...prev].slice(0, 50))
  })

  const agentsData = agentsResponse?.data?.data
  const categories = agentsData?.categories || {}
  const stats = agentsData?.stats || { total: 72, routable: 69, categories_count: 15 }

  // Parse activity data
  const recentActivities: RecentActivity[] = recentActivityResponse?.data?.activities || []
  const learningActivity = learningActivityResponse?.data || {}
  // Session 688: API returns feed_items, not feed
  // Session 694: Properly typed with rich data
  const learningFeed: LearningFeedItem[] = learningActivity?.feed_items || learningActivity?.feed || []
  const learningStats = learningActivity?.stats || {}
  const topLearners: TopLearner[] = learningActivity?.top_learners || []

  const isConnected = agentWsStatus === 'connected' || learningWsStatus === 'connected'

  // Get activity icon based on type
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'dream': return <Brain size={16} className="text-accent-purple" />
      case 'conversation': return <MessageSquare size={16} className="text-accent-cyan" />
      case 'decision': return <Sparkles size={16} className="text-accent-amber" />
      case 'pilot': return <Activity size={16} className="text-accent-green" />
      case 'knowledge': return <Zap size={16} className="text-accent-pink" />
      default: return <Bot size={16} className="text-primary-400" />
    }
  }

  // Get activity color based on type
  const getActivityColor = (type: string) => {
    switch (type) {
      case 'dream': return 'bg-accent-purple/20'
      case 'conversation': return 'bg-accent-cyan/20'
      case 'decision': return 'bg-accent-amber/20'
      case 'pilot': return 'bg-accent-green/20'
      case 'knowledge': return 'bg-accent-pink/20'
      default: return 'bg-primary-500/20'
    }
  }

  // Filter agents based on search query
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return categories

    const query = searchQuery.toLowerCase()
    const filtered: Record<string, Agent[]> = {}

    Object.entries(categories).forEach(([cat, agentList]) => {
      const matchingAgents = agentList.filter((agent) =>
        agent.name.toLowerCase().includes(query) ||
        agent.description.toLowerCase().includes(query) ||
        agent.keywords.some((k) => k.toLowerCase().includes(query))
      )
      if (matchingAgents.length > 0) {
        filtered[cat] = matchingAgents
      }
    })

    return filtered
  }, [categories, searchQuery])

  const toggleCategory = (category: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Session 713: Breadcrumb navigation */}
      <CompactBreadcrumb currentPage="Agents" />

      {/* Connection Status Banner */}
      <div className={cn(
        'flex items-center gap-2 px-4 py-2 rounded-lg text-sm',
        isConnected ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-amber/10 text-accent-amber'
      )}>
        {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
        <span>
          {isConnected
            ? 'Real-time updates connected'
            : 'Connecting to real-time updates...'}
        </span>
        <span className="text-xs opacity-70 ml-auto">
          Agent WS: {agentWsStatus} | Learning WS: {learningWsStatus}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <Bot className="text-primary-400" size={24} />
            <div>
              <p className="text-sm text-gray-400">Total Agents</p>
              <p className="text-2xl font-bold">{stats.total}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-accent-green" size={24} />
            <div>
              <p className="text-sm text-gray-400">Routable</p>
              <p className="text-2xl font-bold">{stats.routable}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Layers className="text-accent-amber" size={24} />
            <div>
              <p className="text-sm text-gray-400">Categories</p>
              <p className="text-2xl font-bold">{stats.categories_count}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Zap className="text-accent-cyan" size={24} />
            <div>
              <p className="text-sm text-gray-400">Live Updates</p>
              <p className="text-2xl font-bold">{realtimeUpdates.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-dark-border pb-4">
        {(['directory', 'activity', 'learning'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize',
              activeTab === tab
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-card'
            )}
          >
            {tab === 'activity' && realtimeUpdates.length > 0 && (
              <span className="mr-2 h-2 w-2 rounded-full bg-accent-green inline-block animate-pulse" />
            )}
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'directory' && (
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search agents by name, description, or keywords..."
              className="w-full pl-10 pr-4 py-3 bg-dark-card border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
            />
          </div>

          {/* Categories */}
          <div className="space-y-2">
            {Object.entries(filteredCategories)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([category, agentList]) => {
                const config = CATEGORY_CONFIG[category] || CATEGORY_CONFIG.general
                const isExpanded = expandedCategories.has(category)

                return (
                  <div key={category} className="card p-0 overflow-hidden">
                    {/* Category Header */}
                    <button
                      onClick={() => toggleCategory(category)}
                      className="w-full flex items-center justify-between p-4 hover:bg-dark-hover transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className={cn('h-3 w-3 rounded-full', config.color)} />
                        <span className="font-medium">{config.name}</span>
                        <span className="text-sm text-gray-400">({agentList.length} agents)</span>
                      </div>
                      {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                    </button>

                    {/* Agent List */}
                    {isExpanded && (
                      <div className="border-t border-dark-border">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0">
                          {agentList.map((agent) => (
                            <div
                              key={agent.name}
                              onClick={() => setSelectedAgent(selectedAgent?.name === agent.name ? null : agent)}
                              className={cn(
                                'p-4 border-b border-r border-dark-border hover:bg-dark-hover transition-colors cursor-pointer',
                                selectedAgent?.name === agent.name && 'bg-primary-500/10 border-primary-500'
                              )}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                  <h4 className="font-medium truncate">{agent.name.replace('Agent', '')}</h4>
                                  <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                                    {agent.description || 'No description available'}
                                  </p>
                                  {/* Session 697: Always-visible keywords preview */}
                                  {agent.keywords.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-2">
                                      {agent.keywords.slice(0, 3).map((keyword) => (
                                        <span
                                          key={keyword}
                                          className="text-xs px-1.5 py-0.5 rounded bg-accent-purple/10 text-accent-purple border border-accent-purple/20"
                                        >
                                          {keyword}
                                        </span>
                                      ))}
                                      {agent.keywords.length > 3 && (
                                        <span className="text-xs px-1.5 py-0.5 text-gray-500">
                                          +{agent.keywords.length - 3} more
                                        </span>
                                      )}
                                    </div>
                                  )}
                                  {/* Session 697: Examples indicator */}
                                  {agent.examples.length > 0 && (
                                    <div className="flex items-center gap-1 mt-1.5 text-xs text-accent-cyan">
                                      <MessageSquare size={10} />
                                      <span>{agent.examples.length} example{agent.examples.length > 1 ? 's' : ''}</span>
                                    </div>
                                  )}
                                </div>
                                <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                                  {agent.is_routable && (
                                    <span className="text-xs px-2 py-0.5 rounded bg-accent-green/20 text-accent-green">
                                      routable
                                    </span>
                                  )}
                                  <span
                                    className={cn(
                                      'h-2 w-2 rounded-full',
                                      agent.is_active ? 'bg-accent-green' : 'bg-accent-red'
                                    )}
                                  />
                                </div>
                              </div>

                              {/* Expanded Agent Details - Session 697: Improved styling */}
                              {selectedAgent?.name === agent.name && (
                                <div className="mt-3 pt-3 border-t border-dark-border space-y-3">
                                  {/* All Keywords */}
                                  {agent.keywords.length > 0 && (
                                    <div>
                                      <p className="text-xs text-gray-500 mb-1.5 flex items-center gap-1">
                                        <span className="h-1 w-1 rounded-full bg-accent-purple"></span>
                                        All Keywords
                                      </p>
                                      <div className="flex flex-wrap gap-1">
                                        {agent.keywords.map((keyword) => (
                                          <span
                                            key={keyword}
                                            className="text-xs px-2 py-0.5 rounded bg-accent-purple/10 text-accent-purple border border-accent-purple/20"
                                          >
                                            {keyword}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  {/* Example Prompts */}
                                  {agent.examples.length > 0 && (
                                    <div>
                                      <p className="text-xs text-gray-500 mb-1.5 flex items-center gap-1">
                                        <span className="h-1 w-1 rounded-full bg-accent-cyan"></span>
                                        Example Prompts
                                      </p>
                                      <div className="space-y-1.5">
                                        {agent.examples.map((example, i) => (
                                          <div
                                            key={i}
                                            className="text-xs p-2 rounded bg-accent-cyan/5 border border-accent-cyan/20 text-gray-300"
                                          >
                                            <span className="text-accent-cyan mr-1">→</span>
                                            "{example}"
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  {/* Agent Meta */}
                                  <div className="flex items-center gap-3 pt-2 text-xs text-gray-500 border-t border-dark-border/50">
                                    <span className="flex items-center gap-1">
                                      <span className="h-1.5 w-1.5 rounded-full bg-accent-amber"></span>
                                      Priority: {agent.priority}
                                    </span>
                                    <span className="flex items-center gap-1">
                                      <span className={cn(
                                        'h-1.5 w-1.5 rounded-full',
                                        agent.is_active ? 'bg-accent-green' : 'bg-accent-red'
                                      )}></span>
                                      {agent.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                    {agent.is_routable && (
                                      <span className="flex items-center gap-1">
                                        <span className="h-1.5 w-1.5 rounded-full bg-accent-green"></span>
                                        Routable
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
          </div>

          {Object.keys(filteredCategories).length === 0 && searchQuery && (
            <div className="text-center py-8 text-gray-400">
              <Search className="mx-auto mb-2" size={32} />
              <p>No agents found matching "{searchQuery}"</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-4">
          {/* Real-time Updates Section */}
          {realtimeUpdates.length > 0 && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-accent-green animate-pulse" />
                  Live Updates
                </h3>
                <span className="text-xs text-gray-500">{realtimeUpdates.length} events</span>
              </div>
              <div className="space-y-3 max-h-[300px] overflow-auto">
                {realtimeUpdates.slice(0, 10).map((update, idx) => {
                  const agentName = getUpdateAgentName(update)
                  const status = getUpdateStatus(update)
                  const message = getUpdateMessage(update)
                  const timestamp = getUpdateTimestamp(update)
                  return (
                  <div
                    key={`rt-${timestamp}-${idx}`}
                    className="flex items-start gap-3 p-3 rounded-lg border border-dark-border bg-dark-hover/50"
                  >
                    <div className={cn(
                      'h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0',
                      update.type === 'agent_completed' ? 'bg-accent-green/20' :
                      update.type === 'agent_error' ? 'bg-accent-red/20' :
                      'bg-primary-500/20'
                    )}>
                      <Bot size={16} className={
                        update.type === 'agent_completed' ? 'text-accent-green' :
                        update.type === 'agent_error' ? 'text-accent-red' :
                        'text-primary-400'
                      } />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{agentName}</span>
                        <span className={cn(
                          'text-xs px-2 py-0.5 rounded',
                          update.type === 'agent_completed' ? 'bg-accent-green/20 text-accent-green' :
                          update.type === 'agent_error' ? 'bg-accent-red/20 text-accent-red' :
                          'bg-primary-500/20 text-primary-400'
                        )}>
                          {status}
                        </span>
                      </div>
                      {message && (
                        <p className="text-sm text-gray-400 mt-1 truncate">{message}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {formatTimestamp(timestamp)}
                      </p>
                    </div>
                  </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Recent System Activity */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Recent Activity</h3>
              <button
                onClick={() => refetchActivity()}
                disabled={isRefetchingActivity}
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <RefreshCw size={14} className={cn(isRefetchingActivity && 'animate-spin')} />
                Refresh
              </button>
            </div>

            {/* Activity Type Legend + Dream Stats */}
            <div className="flex flex-wrap items-center gap-3 mb-4 pb-4 border-b border-dark-border">
              {[
                { type: 'dream', label: 'Dreams', icon: <Brain size={14} /> },
                { type: 'conversation', label: 'Conversations', icon: <MessageSquare size={14} /> },
                { type: 'decision', label: 'Decisions', icon: <Sparkles size={14} /> },
                { type: 'pilot', label: 'Pilots', icon: <Activity size={14} /> },
                { type: 'knowledge', label: 'Knowledge', icon: <Zap size={14} /> },
              ].map(({ type, label, icon }) => (
                <div key={type} className="flex items-center gap-1.5 text-xs text-gray-400">
                  <span className={cn('p-1 rounded', getActivityColor(type))}>{icon}</span>
                  {label}
                </div>
              ))}
              {/* Session 695: Dream stats */}
              {dreamStats.todayCount > 0 && (
                <div className="ml-auto flex items-center gap-2 text-xs">
                  <span className="text-accent-purple font-medium">{dreamStats.todayCount} dreams today</span>
                  {dreamStats.unreadCount > 0 && (
                    <span className="px-2 py-0.5 rounded-full bg-accent-purple/20 text-accent-purple">
                      {dreamStats.unreadCount} unread
                    </span>
                  )}
                </div>
              )}
            </div>

            {recentActivities.length > 0 ? (
              <div className="space-y-3 max-h-[500px] overflow-auto">
                {recentActivities.map((activity, idx) => {
                  // Session 695: Find matching dream for click handler
                  const matchingDream = activity.type === 'dream' && activity.id
                    ? dreams.find(d => d.id === activity.id)
                    : null
                  const isDreamClickable = activity.type === 'dream' && matchingDream

                  // Session 695: Find matching conversation for click handler
                  const matchingConversation = activity.type === 'conversation' && activity.id
                    ? conversations.find(c => c.id === activity.id)
                    : null
                  const isConversationClickable = activity.type === 'conversation' && matchingConversation

                  // Session 696: Find matching decision for click handler
                  const matchingDecision = activity.type === 'decision' && activity.id
                    ? decisions.find(d => d.id === activity.id)
                    : null
                  const isDecisionClickable = activity.type === 'decision' && matchingDecision

                  // Session 696: Find matching experiment for click handler (pilot activities are experiments)
                  const matchingExperiment = activity.type === 'pilot' && activity.id
                    ? experiments.find(e => e.id === activity.id)
                    : null
                  const isPilotClickable = activity.type === 'pilot' && matchingExperiment

                  return (
                  <div
                    key={`activity-${activity.id || activity.timestamp}-${idx}`}
                    onClick={
                      isDreamClickable ? () => setSelectedDream(matchingDream) :
                      isConversationClickable ? () => setSelectedConversation(matchingConversation) :
                      isDecisionClickable ? () => setSelectedDecision(matchingDecision) :
                      isPilotClickable ? () => setSelectedExperiment(matchingExperiment) :
                      undefined
                    }
                    className={cn(
                      "flex items-start gap-3 p-4 rounded-lg border border-dark-border transition-colors",
                      isDreamClickable
                        ? "hover:border-accent-purple/50 cursor-pointer hover:bg-accent-purple/5"
                        : isConversationClickable
                        ? "hover:border-accent-cyan/50 cursor-pointer hover:bg-accent-cyan/5"
                        : isDecisionClickable
                        ? "hover:border-accent-amber/50 cursor-pointer hover:bg-accent-amber/5"
                        : isPilotClickable
                        ? "hover:border-accent-green/50 cursor-pointer hover:bg-accent-green/5"
                        : "hover:border-primary-500/50"
                    )}
                  >
                    {/* Session 694: Show emoji icon if available, otherwise use icon component */}
                    <div className={cn(
                      'h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0 text-lg',
                      getActivityColor(activity.type)
                    )}>
                      {typeof activity.icon === 'string' ? activity.icon : getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={cn(
                          'text-xs px-2 py-0.5 rounded capitalize',
                          activity.type === 'dream' ? 'bg-accent-purple/20 text-accent-purple' :
                          activity.type === 'conversation' ? 'bg-accent-cyan/20 text-accent-cyan' :
                          activity.type === 'decision' ? 'bg-accent-amber/20 text-accent-amber' :
                          activity.type === 'pilot' ? 'bg-accent-green/20 text-accent-green' :
                          'bg-accent-pink/20 text-accent-pink'
                        )}>
                          {activity.type}
                        </span>
                        {/* Session 695: Show "Click to view" hint for clickable items */}
                        {isDreamClickable && (
                          <span className="text-xs text-accent-purple/60 flex items-center gap-1">
                            <Eye size={10} />
                            Click to view
                          </span>
                        )}
                        {isConversationClickable && (
                          <span className="text-xs text-accent-cyan/60 flex items-center gap-1">
                            <Eye size={10} />
                            Click to view thread
                          </span>
                        )}
                        {isDecisionClickable && (
                          <span className="text-xs text-accent-amber/60 flex items-center gap-1">
                            <Eye size={10} />
                            Click for insights
                          </span>
                        )}
                        {isPilotClickable && (
                          <span className="text-xs text-accent-green/60 flex items-center gap-1">
                            <Eye size={10} />
                            Click for details
                          </span>
                        )}
                        {/* Session 694: Show friendly timestamp */}
                        {activity.timestamp_display && (
                          <span className="text-xs text-gray-500">{activity.timestamp_display}</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-200 mt-1 font-medium">{activity.title}</p>
                      <p className="text-sm text-gray-400 mt-0.5">{activity.subtitle}</p>
                      {/* Session 694: Show participating agents */}
                      {activity.agents && activity.agents.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {activity.agents.map((agent, agentIdx) => (
                            <span key={agentIdx} className="text-xs px-2 py-0.5 rounded bg-dark-card text-gray-400 flex items-center gap-1">
                              <Bot size={10} />
                              {agent}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          {formatTimestamp(activity.timestamp, 'full')}
                        </span>
                        {activity.agent_name && (
                          <span className="flex items-center gap-1">
                            <Bot size={12} />
                            {activity.agent_name}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Activity className="mx-auto mb-2" size={32} />
                <p>No recent activity</p>
                <p className="text-sm text-gray-500 mt-1">
                  Agent dreams, conversations, and decisions will appear here
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'learning' && (
        <div className="space-y-4">
          {/* Learning Stats */}
          {Object.keys(learningStats).length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="card p-4">
                <div className="flex items-center gap-2 text-accent-cyan mb-1">
                  <Brain size={16} />
                  <span className="text-xs text-gray-400">Total Knowledge</span>
                </div>
                <p className="text-xl font-bold">{learningStats.total_knowledge || 0}</p>
              </div>
              <div className="card p-4">
                <div className="flex items-center gap-2 text-accent-green mb-1">
                  <Users size={16} />
                  <span className="text-xs text-gray-400">Connections</span>
                </div>
                <p className="text-xl font-bold">{learningStats.total_connections || 0}</p>
              </div>
              <div className="card p-4">
                <div className="flex items-center gap-2 text-accent-amber mb-1">
                  <Zap size={16} />
                  <span className="text-xs text-gray-400">Transfers (24h)</span>
                </div>
                <p className="text-xl font-bold">{learningStats.transfers_last_day || 0}</p>
              </div>
              <div className="card p-4">
                <div className="flex items-center gap-2 text-accent-purple mb-1">
                  <Activity size={16} />
                  <span className="text-xs text-gray-400">Active Learners</span>
                </div>
                <p className="text-xl font-bold">{learningStats.active_learners || 0}</p>
              </div>
            </div>
          )}

          {/* Session 694: Top Learners Section */}
          {topLearners.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Trophy size={18} className="text-accent-amber" />
                Top Learners
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {topLearners.slice(0, 6).map((learner, idx) => (
                  <div
                    key={learner.name}
                    className={cn(
                      "p-3 rounded-lg border transition-colors",
                      idx === 0 ? "border-accent-amber/50 bg-accent-amber/5" :
                      idx === 1 ? "border-gray-400/50 bg-gray-400/5" :
                      idx === 2 ? "border-orange-600/50 bg-orange-600/5" :
                      "border-dark-border"
                    )}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {idx < 3 && (
                        <span className={cn(
                          "text-sm font-bold",
                          idx === 0 ? "text-accent-amber" :
                          idx === 1 ? "text-gray-400" :
                          "text-orange-600"
                        )}>
                          #{idx + 1}
                        </span>
                      )}
                      <span className="font-medium truncate">{learner.name.replace('Agent', '')}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1 text-gray-400">
                        <Brain size={12} className="text-accent-cyan" />
                        <span>{learner.knowledge_count} knowledge</span>
                      </div>
                      <div className="flex items-center gap-1 text-gray-400">
                        <TrendingUp size={12} className="text-accent-green" />
                        <span>{learner.effectiveness}% effective</span>
                      </div>
                      <div className="flex items-center gap-1 text-gray-400">
                        <Users size={12} className="text-accent-purple" />
                        <span>Teaches {learner.teaches}</span>
                      </div>
                      <div className="flex items-center gap-1 text-gray-400">
                        <Zap size={12} className="text-accent-pink" />
                        <span>Learns from {learner.learns_from}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Real-time Learning Events */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <span className={cn(
                  "h-2 w-2 rounded-full",
                  learningEvents.length > 0 ? "bg-accent-cyan animate-pulse" : "bg-gray-500"
                )} />
                Live Learning
              </h3>
              <span className="text-xs text-gray-500">
                {learningWsStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {learningEvents.length > 0 ? (
              <div className="space-y-3 max-h-[200px] overflow-auto">
                {learningEvents.slice(0, 5).map((event, idx) => (
                  <div
                    key={`live-${event.timestamp}-${idx}`}
                    className="flex items-start gap-3 p-3 rounded-lg border border-dark-border bg-accent-cyan/5"
                  >
                    <div className="h-8 w-8 rounded-full bg-accent-cyan/20 flex items-center justify-center flex-shrink-0">
                      <Zap size={16} className="text-accent-cyan" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{event.agent_name}</span>
                        <span className="text-xs px-2 py-0.5 rounded bg-accent-cyan/20 text-accent-cyan">
                          {event.event_type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">{event.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 text-gray-400">
                <Zap size={24} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">Waiting for real-time learning events...</p>
                <p className="text-xs mt-1">Events appear here as agents learn and share knowledge</p>
              </div>
            )}
          </div>

          {/* Session 694: Enhanced Knowledge Transfers with rich data */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Knowledge Transfers</h3>
              <button
                onClick={() => refetchLearning()}
                disabled={isRefetchingLearning}
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <RefreshCw size={14} className={cn(isRefetchingLearning && 'animate-spin')} />
                Refresh
              </button>
            </div>

            {learningFeed.length > 0 ? (
              <div className="space-y-3 max-h-[500px] overflow-auto">
                {learningFeed.map((transfer, idx) => {
                  const fromAgent = transfer.teacher || 'Unknown'
                  const toAgent = transfer.student || 'Unknown'
                  const title = transfer.knowledge_full?.title?.replace(/^\[Learned\]\s*/g, '') || 'Knowledge shared'
                  const transferType = transfer.type || 'transfer'
                  const confidence = transfer.knowledge_full?.confidence
                  const keyInsights = transfer.knowledge_full?.key_insights || transfer.key_points || []
                  const knowledgeType = transfer.knowledge_full?.knowledge_type

                  return (
                    <div
                      key={`transfer-${transfer.id || idx}`}
                      onClick={() => setSelectedTransfer(transfer)}
                      className={cn(
                        "p-4 rounded-lg border transition-colors cursor-pointer group",
                        transfer.was_useful
                          ? "border-accent-green/30 bg-accent-green/5 hover:border-accent-green/50 hover:bg-accent-green/10"
                          : "border-dark-border hover:border-accent-cyan/50 hover:bg-accent-cyan/5"
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div className={cn(
                          "h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0",
                          transfer.was_useful ? "bg-accent-green/20" : "bg-accent-cyan/20"
                        )}>
                          <Brain size={18} className={transfer.was_useful ? "text-accent-green" : "text-accent-cyan"} />
                        </div>
                        <div className="flex-1 min-w-0">
                          {/* Header with agents and badges */}
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-medium text-accent-cyan">{fromAgent.replace('Agent', '')}</span>
                            <span className="text-gray-500">→</span>
                            <span className="font-medium text-accent-green">{toAgent.replace('Agent', '')}</span>
                            {transfer.was_useful !== undefined && (
                              <span className={cn(
                                "text-xs px-2 py-0.5 rounded flex items-center gap-1",
                                transfer.was_useful
                                  ? "bg-accent-green/20 text-accent-green"
                                  : "bg-gray-500/20 text-gray-400"
                              )}>
                                <ThumbsUp size={10} />
                                {transfer.was_useful ? 'Useful' : 'Low Impact'}
                              </span>
                            )}
                            {knowledgeType && (
                              <span className="text-xs px-2 py-0.5 rounded bg-accent-purple/20 text-accent-purple capitalize">
                                {knowledgeType}
                              </span>
                            )}
                          </div>

                          {/* Title */}
                          <p className="text-sm text-gray-200 mt-1 font-medium">{title}</p>

                          {/* Key Insights - Session 694: Filter for strings only (some may be objects) */}
                          {keyInsights.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {keyInsights.slice(0, 3).map((insight, insightIdx) => {
                                // Handle both string insights and object insights
                                const displayText = typeof insight === 'string'
                                  ? insight
                                  : String((insight as Record<string, unknown>)?.type || 'Insight')
                                return (
                                  <span key={insightIdx} className="text-xs px-2 py-0.5 rounded bg-dark-card text-gray-400">
                                    {displayText}
                                  </span>
                                )
                              })}
                            </div>
                          )}

                          {/* Metrics row */}
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span className="px-2 py-0.5 rounded bg-dark-card capitalize">{transferType.replace('_', ' ')}</span>
                            {confidence !== undefined && (
                              <span className="flex items-center gap-1">
                                <TrendingUp size={12} className="text-accent-amber" />
                                {(confidence * 100).toFixed(0)}% confidence
                              </span>
                            )}
                            {transfer.usefulness_score !== undefined && (
                              <span className="flex items-center gap-1">
                                <ThumbsUp size={12} />
                                {(transfer.usefulness_score * 100).toFixed(0)}% score
                              </span>
                            )}
                            <span className="flex items-center gap-1">
                              <Clock size={12} />
                              {formatTimestamp(transfer.timestamp, 'full')}
                            </span>
                            <span className="flex items-center gap-1 ml-auto text-accent-cyan opacity-60 group-hover:opacity-100">
                              <Eye size={12} />
                              Details
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Zap className="mx-auto mb-2" size={32} />
                <p>No knowledge transfers yet</p>
                <p className="text-sm text-gray-500 mt-1">
                  Agent learning activity will appear here
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Session 695: Dream Gallery Modal */}
      {selectedDream && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-purple/10 to-accent-pink/10">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">💭</span>
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded capitalize',
                    selectedDream.dream_type === 'prediction' ? 'bg-accent-amber/20 text-accent-amber' :
                    selectedDream.dream_type === 'observation' ? 'bg-accent-cyan/20 text-accent-cyan' :
                    selectedDream.dream_type === 'insight' ? 'bg-accent-green/20 text-accent-green' :
                    'bg-accent-purple/20 text-accent-purple'
                  )}>
                    {selectedDream.dream_type}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-white">{selectedDream.title}</h2>
                <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                  <Bot size={14} />
                  <span>{selectedDream.agent_name}</span>
                  <span className="text-gray-600">•</span>
                  <Clock size={14} />
                  <span>{formatTimestamp(selectedDream.dreamed_at, 'full')}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedDream(null)}
                className="p-2 rounded-lg hover:bg-dark-hover transition-colors text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[60vh] space-y-6">
              {/* Dream Content */}
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                  <MessageSquare size={14} />
                  Dream Content
                </h3>
                <div className="bg-dark-hover rounded-lg p-4 text-gray-200 leading-relaxed whitespace-pre-wrap">
                  {selectedDream.content}
                </div>
              </div>

              {/* Inspiration */}
              {selectedDream.inspiration && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Lightbulb size={14} />
                    Inspiration
                  </h3>
                  <div className="bg-accent-amber/5 border border-accent-amber/20 rounded-lg p-4 text-gray-300 text-sm">
                    {selectedDream.inspiration}
                  </div>
                </div>
              )}

              {/* Creativity Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-dark-hover rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400 flex items-center gap-2">
                      <Eye size={14} />
                      Vividness
                    </span>
                    <span className="text-sm font-medium text-accent-purple">
                      {Math.round(selectedDream.vividness * 100)}%
                    </span>
                  </div>
                  <div className="h-2 bg-dark-card rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-accent-purple to-accent-pink transition-all"
                      style={{ width: `${selectedDream.vividness * 100}%` }}
                    />
                  </div>
                </div>
                <div className="bg-dark-hover rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400 flex items-center gap-2">
                      <Sparkles size={14} />
                      Creativity
                    </span>
                    <span className="text-sm font-medium text-accent-cyan">
                      {Math.round(selectedDream.creativity * 100)}%
                    </span>
                  </div>
                  <div className="h-2 bg-dark-card rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-accent-cyan to-accent-green transition-all"
                      style={{ width: `${selectedDream.creativity * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Related Topics */}
              {selectedDream.related_topics && selectedDream.related_topics.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Layers size={14} />
                    Related Topics
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedDream.related_topics.map((topic, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-3 py-1.5 rounded-full bg-dark-hover text-gray-300 border border-dark-border"
                      >
                        {typeof topic === 'string' ? topic.slice(0, 50) : 'Topic'}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>Dream ID: {selectedDream.id.slice(0, 8)}...</span>
                {selectedDream.shown_to_user && (
                  <span className="flex items-center gap-1 text-accent-green">
                    <CheckCircle size={12} />
                    Viewed
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {/* Reaction buttons */}
                {['✨', '🔥', '💡', '🤔'].map((emoji) => (
                  <button
                    key={emoji}
                    onClick={() => {
                      // TODO: Call dreamsApi.react when implemented
                      console.log('React to dream:', selectedDream.id, emoji)
                    }}
                    className={cn(
                      'text-xl p-2 rounded-lg transition-all hover:bg-dark-card hover:scale-110',
                      selectedDream.user_reaction === emoji && 'bg-accent-purple/20 ring-2 ring-accent-purple'
                    )}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Session 695: Conversation Thread Viewer Modal */}
      {selectedConversation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-cyan/10 to-accent-blue/10">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🗣️</span>
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded capitalize',
                    selectedConversation.status === 'concluded' ? 'bg-accent-green/20 text-accent-green' :
                    selectedConversation.status === 'active' ? 'bg-accent-cyan/20 text-accent-cyan' :
                    'bg-gray-500/20 text-gray-400'
                  )}>
                    {selectedConversation.status}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-accent-blue/20 text-accent-blue capitalize">
                    {selectedConversation.type_display || selectedConversation.type.replace('_', ' ')}
                  </span>
                  {selectedConversation.quality_score > 0 && (
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-amber/20 text-accent-amber flex items-center gap-1">
                      <Sparkles size={10} />
                      {Math.round(selectedConversation.quality_score * 100)}% quality
                    </span>
                  )}
                </div>
                <h2 className="text-xl font-bold text-white">{selectedConversation.topic}</h2>
                <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                  <Users size={14} />
                  <span>{selectedConversation.participants.length} participants</span>
                  <span className="text-gray-600">•</span>
                  <MessageSquare size={14} />
                  <span>{selectedConversation.message_count} messages</span>
                  <span className="text-gray-600">•</span>
                  <Clock size={14} />
                  <span>{formatTimestamp(selectedConversation.started_at, 'full')}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedConversation(null)}
                className="p-2 rounded-lg hover:bg-dark-hover transition-colors text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Participants Strip */}
            <div className="px-6 py-3 border-b border-dark-border bg-dark-hover/30 flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-500">Participants:</span>
              {selectedConversation.participants.map((participant, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-1 rounded-full bg-dark-card text-gray-300 flex items-center gap-1"
                >
                  <span>{participant.emoji || '🤖'}</span>
                  {participant.name}
                </span>
              ))}
            </div>

            {/* Message Thread */}
            <div className="p-6 overflow-y-auto max-h-[50vh] space-y-4">
              {selectedConversation.messages && selectedConversation.messages.length > 0 ? (
                selectedConversation.messages.map((msg, idx) => (
                  <div
                    key={msg.id || idx}
                    className={cn(
                      "flex gap-3",
                      msg.type === 'synthesis' && "bg-accent-green/5 rounded-lg p-3 border border-accent-green/20"
                    )}
                  >
                    <div className={cn(
                      "h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 text-lg",
                      msg.type === 'synthesis' ? "bg-accent-green/20" :
                      msg.type === 'question' ? "bg-accent-cyan/20" :
                      "bg-dark-hover"
                    )}>
                      {msg.agent_emoji || '🤖'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">{msg.agent}</span>
                        <span className={cn(
                          "text-xs px-1.5 py-0.5 rounded",
                          msg.type === 'synthesis' ? "bg-accent-green/20 text-accent-green" :
                          msg.type === 'question' ? "bg-accent-cyan/20 text-accent-cyan" :
                          msg.type === 'answer' ? "bg-accent-amber/20 text-accent-amber" :
                          "bg-dark-card text-gray-400"
                        )}>
                          {msg.type}
                        </span>
                        {msg.relevance > 0 && (
                          <span className="text-xs text-gray-500">
                            {Math.round(msg.relevance * 100)}% relevance
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
                        {msg.content}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {formatTimestamp(msg.created_at)}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No messages available</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Message thread was not captured for this conversation
                  </p>
                </div>
              )}
            </div>

            {/* Conclusion Section */}
            {selectedConversation.conclusion && (
              <div className="px-6 py-4 border-t border-dark-border bg-accent-green/5">
                <h3 className="text-sm font-medium text-accent-green mb-2 flex items-center gap-2">
                  <CheckCircle size={14} />
                  Conclusion
                </h3>
                <p className="text-sm text-gray-200 leading-relaxed">
                  {selectedConversation.conclusion}
                </p>
              </div>
            )}

            {/* Insights Section */}
            {selectedConversation.insights && selectedConversation.insights.length > 0 && (
              <div className="px-6 py-4 border-t border-dark-border">
                <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                  <Lightbulb size={14} />
                  Insights Generated
                </h3>
                <div className="flex flex-wrap gap-2">
                  {selectedConversation.insights.map((insight, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-3 py-1.5 rounded-lg bg-dark-hover text-gray-300 border border-dark-border"
                    >
                      {typeof insight === 'string' ? insight : 'Insight'}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>ID: {selectedConversation.id.slice(0, 8)}...</span>
                <span className="text-gray-600">•</span>
                <span>Trigger: {selectedConversation.trigger}</span>
                {selectedConversation.ended_at && (
                  <>
                    <span className="text-gray-600">•</span>
                    <span>Ended: {formatTimestamp(selectedConversation.ended_at, 'full')}</span>
                  </>
                )}
              </div>
              <button
                onClick={() => setSelectedConversation(null)}
                className="px-4 py-2 text-sm bg-dark-card hover:bg-dark-hover rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 696: Decision Insights Panel Modal */}
      {selectedDecision && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-amber/10 to-accent-green/10">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="text-2xl">🏛️</span>
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded capitalize',
                    selectedDecision.status === 'approved' ? 'bg-accent-green/20 text-accent-green' :
                    selectedDecision.status === 'rejected' ? 'bg-accent-red/20 text-accent-red' :
                    selectedDecision.status === 'implemented' ? 'bg-accent-cyan/20 text-accent-cyan' :
                    'bg-gray-500/20 text-gray-400'
                  )}>
                    {selectedDecision.status}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-accent-amber/20 text-accent-amber capitalize">
                    {selectedDecision.decision_type_display || selectedDecision.decision_type}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-accent-blue/20 text-accent-blue capitalize">
                    {selectedDecision.impact_area_display || selectedDecision.impact_area}
                  </span>
                  {selectedDecision.is_canonical && (
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-purple/20 text-accent-purple flex items-center gap-1">
                      <Sparkles size={10} />
                      Canon
                    </span>
                  )}
                </div>
                <h2 className="text-xl font-bold text-white">{selectedDecision.topic}</h2>
                <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                  <Users size={14} />
                  <span>{selectedDecision.participants.length} participants</span>
                  <span className="text-gray-600">•</span>
                  <Clock size={14} />
                  <span>{formatTimestamp(selectedDecision.created_at, 'full')}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedDecision(null)}
                className="p-2 rounded-lg hover:bg-dark-hover transition-colors text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Participants Strip */}
            <div className="px-6 py-3 border-b border-dark-border bg-dark-hover/30 flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-500">Participants:</span>
              {selectedDecision.participants.map((participant, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-1 rounded-full bg-dark-card text-gray-300 flex items-center gap-1"
                >
                  <Bot size={10} />
                  {participant}
                </span>
              ))}
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[55vh] space-y-6">
              {/* Key Insights */}
              {selectedDecision.key_insights && selectedDecision.key_insights.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-accent-amber mb-3 flex items-center gap-2">
                    <Lightbulb size={14} />
                    Key Insights
                  </h3>
                  <ul className="space-y-2">
                    {selectedDecision.key_insights.map((insight, idx) => (
                      <li
                        key={idx}
                        className="flex items-start gap-2 text-sm text-gray-200 bg-dark-hover rounded-lg p-3"
                      >
                        <span className="text-accent-amber mt-0.5">•</span>
                        <span>{typeof insight === 'string' ? insight : 'Insight'}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommended Stance */}
              {selectedDecision.recommended_stance && (
                <div>
                  <h3 className="text-sm font-medium text-accent-green mb-2 flex items-center gap-2">
                    <TrendingUp size={14} />
                    Recommended Stance
                  </h3>
                  <div className="bg-accent-green/5 border border-accent-green/20 rounded-lg p-4 text-gray-200 text-sm leading-relaxed">
                    {selectedDecision.recommended_stance}
                  </div>
                </div>
              )}

              {/* Suggested Feature */}
              {selectedDecision.suggested_feature && (
                <div>
                  <h3 className="text-sm font-medium text-accent-cyan mb-2 flex items-center gap-2">
                    <Sparkles size={14} />
                    Suggested Feature
                  </h3>
                  <div className="bg-accent-cyan/5 border border-accent-cyan/20 rounded-lg p-4 text-gray-200 text-sm leading-relaxed">
                    {selectedDecision.suggested_feature}
                  </div>
                </div>
              )}

              {/* Rationale */}
              {selectedDecision.rationale && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Brain size={14} />
                    Rationale
                  </h3>
                  <div className="bg-dark-hover rounded-lg p-4 text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
                    {selectedDecision.rationale}
                  </div>
                </div>
              )}

              {/* Source Link */}
              {selectedDecision.source_topic && (
                <div className="text-xs text-gray-500 flex items-center gap-2">
                  <span>Source:</span>
                  <span className="text-gray-400">{selectedDecision.source_type}</span>
                  <span className="text-gray-600">•</span>
                  <span className="text-gray-400">{selectedDecision.source_topic}</span>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>ID: {selectedDecision.id.slice(0, 8)}...</span>
                {selectedDecision.is_canonical && selectedDecision.promoted_at && (
                  <>
                    <span className="text-gray-600">•</span>
                    <span className="text-accent-purple">
                      Promoted: {formatTimestamp(selectedDecision.promoted_at, 'full')}
                    </span>
                  </>
                )}
              </div>
              <button
                onClick={() => setSelectedDecision(null)}
                className="px-4 py-2 text-sm bg-dark-card hover:bg-dark-hover rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 696: Experiment Modal (for "pilot" activities) */}
      {selectedExperiment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-green/10 to-accent-cyan/10">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="text-2xl">🧪</span>
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded capitalize',
                    selectedExperiment.status === 'success' ? 'bg-accent-green/20 text-accent-green' :
                    selectedExperiment.status === 'running' ? 'bg-accent-cyan/20 text-accent-cyan' :
                    selectedExperiment.status === 'failure' ? 'bg-accent-red/20 text-accent-red' :
                    selectedExperiment.status === 'halted' ? 'bg-accent-amber/20 text-accent-amber' :
                    'bg-gray-500/20 text-gray-400'
                  )}>
                    {selectedExperiment.status}
                  </span>
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded capitalize',
                    selectedExperiment.risk_level === 'low' ? 'bg-accent-green/20 text-accent-green' :
                    selectedExperiment.risk_level === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                    selectedExperiment.risk_level === 'high' ? 'bg-orange-500/20 text-orange-500' :
                    'bg-accent-red/20 text-accent-red'
                  )}>
                    {selectedExperiment.risk_level} risk
                  </span>
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded capitalize',
                    selectedExperiment.outcome_classification === 'success' ? 'bg-accent-green/20 text-accent-green' :
                    selectedExperiment.outcome_classification === 'failure' ? 'bg-accent-red/20 text-accent-red' :
                    'bg-gray-500/20 text-gray-400'
                  )}>
                    {selectedExperiment.outcome_classification}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-white">{selectedExperiment.name}</h2>
                <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                  <Clock size={14} />
                  <span>Started: {formatTimestamp(selectedExperiment.started_at, 'full')}</span>
                  {selectedExperiment.kpi_owner && (
                    <>
                      <span className="text-gray-600">•</span>
                      <span>Owner: {selectedExperiment.kpi_owner}</span>
                    </>
                  )}
                </div>
              </div>
              <button
                onClick={() => setSelectedExperiment(null)}
                className="p-2 rounded-lg hover:bg-dark-hover transition-colors text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* KPI Progress */}
            <div className="px-6 py-4 border-b border-dark-border bg-dark-hover/30">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">Primary KPI</div>
                  <div className="text-sm font-medium text-accent-cyan">{selectedExperiment.primary_kpi || 'Not set'}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">Target</div>
                  <div className="text-sm font-medium text-accent-green">{selectedExperiment.target_value || '-'}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">Current</div>
                  <div className="text-sm font-medium text-accent-amber">{selectedExperiment.current_value || '-'}</div>
                </div>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[50vh] space-y-6">
              {/* Hypothesis */}
              {selectedExperiment.hypothesis && (
                <div>
                  <h3 className="text-sm font-medium text-accent-cyan mb-2 flex items-center gap-2">
                    <Lightbulb size={14} />
                    Hypothesis
                  </h3>
                  <div className="bg-accent-cyan/5 border border-accent-cyan/20 rounded-lg p-4 text-gray-200 text-sm leading-relaxed">
                    {selectedExperiment.hypothesis}
                  </div>
                </div>
              )}

              {/* Decision Topic */}
              {selectedExperiment.decision_topic && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <MessageSquare size={14} />
                    Source Decision
                  </h3>
                  <div className="bg-dark-hover rounded-lg p-4 text-gray-200 text-sm leading-relaxed">
                    {selectedExperiment.decision_topic}
                  </div>
                </div>
              )}

              {/* Halt Info */}
              {selectedExperiment.is_halted && (
                <div className="bg-accent-red/5 border border-accent-red/20 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-accent-red mb-2 flex items-center gap-2">
                    <Activity size={14} />
                    Experiment Halted
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {selectedExperiment.halted_by && (
                      <div>
                        <span className="text-gray-500">Halted by:</span>
                        <span className="ml-2 text-gray-200">{selectedExperiment.halted_by}</span>
                      </div>
                    )}
                    {selectedExperiment.halted_at && (
                      <div>
                        <span className="text-gray-500">Halted at:</span>
                        <span className="ml-2 text-gray-200">{formatTimestamp(selectedExperiment.halted_at, 'full')}</span>
                      </div>
                    )}
                    {selectedExperiment.halt_reason && (
                      <div className="col-span-2">
                        <span className="text-gray-500">Reason:</span>
                        <span className="ml-2 text-gray-200">{selectedExperiment.halt_reason}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Learnings */}
              {selectedExperiment.learnings && (
                <div>
                  <h3 className="text-sm font-medium text-accent-green mb-2 flex items-center gap-2">
                    <Brain size={14} />
                    Learnings
                  </h3>
                  <div className="bg-accent-green/5 border border-accent-green/20 rounded-lg p-4 text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">
                    {selectedExperiment.learnings}
                  </div>
                </div>
              )}

              {/* AI-Generated Metrics */}
              {selectedExperiment.extracted_metrics?.raw_content && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <TrendingUp size={14} />
                    AI-Generated Success Metrics
                  </h3>
                  <details>
                    <summary className="text-xs text-accent-cyan cursor-pointer hover:text-accent-cyan/80 mb-2">
                      View full metrics document
                    </summary>
                    <div className="bg-dark-hover rounded-lg p-4 text-gray-300 text-xs leading-relaxed whitespace-pre-wrap max-h-60 overflow-auto">
                      {selectedExperiment.extracted_metrics.raw_content}
                    </div>
                  </details>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>Experiment ID: {selectedExperiment.id.slice(0, 8)}...</span>
                {selectedExperiment.ended_at && (
                  <>
                    <span className="text-gray-600">•</span>
                    <span>Ended: {formatTimestamp(selectedExperiment.ended_at, 'full')}</span>
                  </>
                )}
              </div>
              <button
                onClick={() => setSelectedExperiment(null)}
                className="px-4 py-2 text-sm bg-dark-card hover:bg-dark-hover rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 697: Knowledge Transfer Modal */}
      {selectedTransfer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className={cn(
              "flex items-start justify-between p-6 border-b border-dark-border",
              selectedTransfer.was_useful
                ? "bg-gradient-to-r from-accent-green/10 to-accent-cyan/10"
                : "bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10"
            )}>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="text-2xl">🧠</span>
                  {selectedTransfer.was_useful !== undefined && (
                    <span className={cn(
                      'text-xs px-2 py-0.5 rounded flex items-center gap-1',
                      selectedTransfer.was_useful
                        ? 'bg-accent-green/20 text-accent-green'
                        : 'bg-gray-500/20 text-gray-400'
                    )}>
                      <ThumbsUp size={10} />
                      {selectedTransfer.was_useful ? 'Useful Transfer' : 'Low Impact'}
                    </span>
                  )}
                  {selectedTransfer.knowledge_full?.knowledge_type && (
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-purple/20 text-accent-purple capitalize">
                      {selectedTransfer.knowledge_full.knowledge_type}
                    </span>
                  )}
                  {selectedTransfer.effectiveness_gain !== undefined && selectedTransfer.effectiveness_gain > 0 && (
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-amber/20 text-accent-amber flex items-center gap-1">
                      <TrendingUp size={10} />
                      +{(selectedTransfer.effectiveness_gain * 100).toFixed(1)}% effectiveness
                    </span>
                  )}
                </div>
                <h2 className="text-xl font-bold text-white">
                  {selectedTransfer.knowledge_full?.title?.replace(/^\[Learned\]\s*/g, '') || 'Knowledge Transfer'}
                </h2>
                <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                  <Clock size={14} />
                  <span>{formatTimestamp(selectedTransfer.timestamp, 'full')}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedTransfer(null)}
                className="p-2 rounded-lg hover:bg-dark-hover transition-colors text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto max-h-[60vh] space-y-6">
              {/* Transfer Direction */}
              <div className="flex items-center justify-center gap-4 p-4 rounded-lg bg-dark-hover/50">
                <div className="text-center">
                  <div className="h-12 w-12 rounded-full bg-accent-cyan/20 flex items-center justify-center mx-auto mb-2">
                    <Bot size={20} className="text-accent-cyan" />
                  </div>
                  <div className="font-medium text-accent-cyan">{selectedTransfer.teacher?.replace('Agent', '') || 'Unknown'}</div>
                  <div className="text-xs text-gray-500">Teacher</div>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <div className="h-0.5 w-16 bg-gradient-to-r from-accent-cyan to-accent-green"></div>
                  <Brain size={16} className="text-gray-400" />
                  <div className="h-0.5 w-16 bg-gradient-to-r from-accent-cyan to-accent-green"></div>
                </div>
                <div className="text-center">
                  <div className="h-12 w-12 rounded-full bg-accent-green/20 flex items-center justify-center mx-auto mb-2">
                    <Bot size={20} className="text-accent-green" />
                  </div>
                  <div className="font-medium text-accent-green">{selectedTransfer.student?.replace('Agent', '') || 'Unknown'}</div>
                  <div className="text-xs text-gray-500">Student</div>
                </div>
              </div>

              {/* Metrics Row */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 rounded-lg bg-dark-hover/50 text-center">
                  <div className="text-xs text-gray-500 mb-1">Confidence</div>
                  <div className="text-lg font-bold text-accent-amber">
                    {selectedTransfer.knowledge_full?.confidence
                      ? `${(selectedTransfer.knowledge_full.confidence * 100).toFixed(0)}%`
                      : '-'}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-dark-hover/50 text-center">
                  <div className="text-xs text-gray-500 mb-1">Usefulness Score</div>
                  <div className="text-lg font-bold text-accent-cyan">
                    {selectedTransfer.usefulness_score !== undefined
                      ? `${(selectedTransfer.usefulness_score * 100).toFixed(0)}%`
                      : '-'}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-dark-hover/50 text-center">
                  <div className="text-xs text-gray-500 mb-1">Effectiveness Gain</div>
                  <div className={cn(
                    "text-lg font-bold",
                    selectedTransfer.effectiveness_gain && selectedTransfer.effectiveness_gain > 0
                      ? "text-accent-green"
                      : "text-gray-500"
                  )}>
                    {selectedTransfer.effectiveness_gain !== undefined
                      ? selectedTransfer.effectiveness_gain > 0
                        ? `+${(selectedTransfer.effectiveness_gain * 100).toFixed(1)}%`
                        : '0%'
                      : '-'}
                  </div>
                </div>
              </div>

              {/* Description */}
              {selectedTransfer.description && (
                <div className="p-4 rounded-lg bg-dark-hover/30 border border-dark-border">
                  <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                    <MessageSquare size={14} className="text-accent-cyan" />
                    Description
                  </h3>
                  <p className="text-gray-200">{selectedTransfer.description}</p>
                </div>
              )}

              {/* Full Summary */}
              {selectedTransfer.knowledge_full?.summary && (
                <div className="p-4 rounded-lg bg-dark-hover/30 border border-dark-border">
                  <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                    <Lightbulb size={14} className="text-accent-amber" />
                    Summary
                  </h3>
                  <p className="text-gray-200 whitespace-pre-wrap">{selectedTransfer.knowledge_full.summary}</p>
                </div>
              )}

              {/* Full Knowledge Text */}
              {selectedTransfer.knowledge && selectedTransfer.knowledge !== selectedTransfer.knowledge_full?.summary && (
                <details className="p-4 rounded-lg bg-dark-hover/30 border border-dark-border">
                  <summary className="text-sm font-medium text-gray-300 cursor-pointer flex items-center gap-2">
                    <Brain size={14} className="text-accent-purple" />
                    Full Knowledge Content
                  </summary>
                  <p className="text-gray-200 whitespace-pre-wrap mt-3 pt-3 border-t border-dark-border">
                    {selectedTransfer.knowledge}
                  </p>
                </details>
              )}

              {/* Key Insights */}
              {(selectedTransfer.knowledge_full?.key_insights?.length || selectedTransfer.key_points?.length) && (
                <div className="p-4 rounded-lg bg-dark-hover/30 border border-dark-border">
                  <h3 className="text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                    <Sparkles size={14} className="text-accent-green" />
                    Key Insights
                  </h3>
                  <div className="space-y-2">
                    {(selectedTransfer.knowledge_full?.key_insights || selectedTransfer.key_points || []).map((insight, idx) => {
                      const displayText = typeof insight === 'string'
                        ? insight
                        : String((insight as Record<string, unknown>)?.type || (insight as Record<string, unknown>)?.insight || 'Insight')
                      return (
                        <div key={idx} className="flex items-start gap-2">
                          <div className="h-1.5 w-1.5 rounded-full bg-accent-green mt-2 flex-shrink-0"></div>
                          <span className="text-gray-200">{displayText}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span className="capitalize">{selectedTransfer.type?.replace('_', ' ') || 'Transfer'}</span>
                {selectedTransfer.source && (
                  <>
                    <span className="text-gray-600">•</span>
                    <span>{selectedTransfer.source}</span>
                  </>
                )}
              </div>
              <button
                onClick={() => setSelectedTransfer(null)}
                className="px-4 py-2 text-sm bg-dark-card hover:bg-dark-hover rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
