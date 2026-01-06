import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { agentsApi, activityApi } from '@/lib/api'
import { useAgentUpdates, useLearningFeed, type AgentUpdate, type LearningEvent } from '@/hooks/useWebSocket'
import { Bot, Activity, CheckCircle, Wifi, WifiOff, Zap, Search, ChevronDown, ChevronRight, Layers, MessageSquare, Brain, Sparkles, Users, Clock, RefreshCw, Trophy, ThumbsUp, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/cn'

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

                              {/* Expanded Agent Details */}
                              {selectedAgent?.name === agent.name && (
                                <div className="mt-3 pt-3 border-t border-dark-border space-y-2">
                                  {agent.keywords.length > 0 && (
                                    <div>
                                      <p className="text-xs text-gray-500 mb-1">Keywords</p>
                                      <div className="flex flex-wrap gap-1">
                                        {agent.keywords.map((keyword) => (
                                          <span
                                            key={keyword}
                                            className="text-xs px-2 py-0.5 rounded bg-dark-card text-gray-400"
                                          >
                                            {keyword}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  {agent.examples.length > 0 && (
                                    <div>
                                      <p className="text-xs text-gray-500 mb-1">Example prompts</p>
                                      <ul className="text-xs text-gray-400 space-y-1">
                                        {agent.examples.map((example, i) => (
                                          <li key={i} className="truncate">"{example}"</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  <div className="flex items-center gap-4 text-xs text-gray-500">
                                    <span>Priority: {agent.priority}</span>
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

            {/* Activity Type Legend */}
            <div className="flex flex-wrap gap-3 mb-4 pb-4 border-b border-dark-border">
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
            </div>

            {recentActivities.length > 0 ? (
              <div className="space-y-3 max-h-[500px] overflow-auto">
                {recentActivities.map((activity, idx) => (
                  <div
                    key={`activity-${activity.id || activity.timestamp}-${idx}`}
                    className="flex items-start gap-3 p-4 rounded-lg border border-dark-border hover:border-primary-500/50 transition-colors"
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
                ))}
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
                      className={cn(
                        "p-4 rounded-lg border transition-colors",
                        transfer.was_useful
                          ? "border-accent-green/30 bg-accent-green/5 hover:border-accent-green/50"
                          : "border-dark-border hover:border-accent-cyan/50"
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
    </div>
  )
}
