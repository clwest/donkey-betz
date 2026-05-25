import { useState, useMemo, useCallback } from 'react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { agentsApi, activityApi, dreamsApi, decisionsApi, experimentsApi, agentChannelsApi, agentMonitoringApi, agentToolsApi, agentTemplatesApi, collectiveApi } from '@/lib/api'
import { useNavigate } from 'react-router-dom'
import { useAgentUpdates, useLearningFeed, useSystemEvents, type AgentUpdate, type LearningEvent } from '@/hooks/useWebSocket'
import { Bot, Activity, CheckCircle, Wifi, WifiOff, Zap, Search, ChevronDown, ChevronRight, Layers, MessageSquare, Brain, Sparkles, Users, Clock, RefreshCw, Trophy, ThumbsUp, TrendingUp, X, Eye, Lightbulb, Hash, Send, BarChart3, AlertTriangle, Cpu, Database, Loader2, Wrench, Power, ExternalLink, Plus, Edit2, Trash2, FileText, Star, Globe, Lock, Shield, Calendar, DollarSign, XCircle } from 'lucide-react'
import { cn } from '@/lib/cn'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'
import remarkGfm from 'remark-gfm'
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
  full_title?: string  // Session 761: Full title for modal display
  subtitle: string
  full_subtitle?: string  // Session 761: Full inspiration/description for modal
  content?: string  // Session 761: Content preview for dreams
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

// Session 782: Conversation interfaces removed - consolidated to ConversationContractPage

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

// Session 760: Agent Execution interface for Output Detail Modal
// Session 760: Output data sub-types for type-safe rendering
interface ImageOutput {
  image_url?: string
  image_id?: string
  file_path?: string
  batch_index?: number
}

interface ToolResultOutput {
  tool?: string
  result?: Record<string, unknown>
}

interface ResearchResultOutput {
  source?: string
  data?: Record<string, unknown>
  title?: string
  summary?: string
}

interface RecommendationOutput {
  title?: string
  description?: string
  priority?: 'high' | 'medium' | 'low'
}

interface SignalOutput {
  type?: string
  strength?: 'strong' | 'moderate' | 'weak'
  description?: string
  market?: string
  confidence?: number
}

interface AnalysisOutput {
  summary?: string
  key_insights?: string[]
  [key: string]: unknown
}

interface ThinkingResultOutput {
  conclusion?: string
  reasoning?: string
  confidence?: number
}

interface WorkflowStepOutput {
  step?: string
  agent?: string
  description?: string
}

interface ContentOutput {
  title?: string
  body?: string
  [key: string]: unknown
}

interface DebateResultOutput {
  topic?: string
  winner?: string
  summary?: string
}

interface OutputDataPayload {
  // Image agents
  images?: ImageOutput[]
  // Tool usage
  tool_results?: ToolResultOutput[]
  // Research agents
  results?: ResearchResultOutput[]
  query?: string
  // ContentWriterAgent
  content?: ContentOutput | string
  metadata?: Record<string, unknown>
  content_type?: string
  // ContentStrategyAgent
  task?: string
  recommendations?: (string | RecommendationOutput)[]
  // PredictionMarketAnalyst, SportsOddsAnalyst
  signals?: SignalOutput[]
  analysis?: AnalysisOutput
  categories?: Record<string, unknown>
  total_volume?: number
  markets_analyzed?: number
  sports?: Record<string, unknown>
  upcoming_24h?: number
  events_analyzed?: number
  // ThinkingAgent
  context?: Record<string, unknown>
  thinking_result?: ThinkingResultOutput
  // WorkflowAgent
  workflow_type?: string
  suggested_workflow?: (string | WorkflowStepOutput)[]
  note?: string
  // Debate agents
  role?: string
  voice_id?: string
  // AutonomousContentStudioCoordinator
  debate_result?: DebateResultOutput
  // SystemIntelligenceAgent
  info_count?: number
  items_count?: number
  warning_count?: number
  critical_count?: number
  execution_time?: number
  // Generic fallback
  type?: string
  response?: string
  [key: string]: unknown
}

interface AgentExecutionDetail {
  id: string
  agent_name: string
  agent_display_name?: string
  task: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  output_data: {
    data?: OutputDataPayload
    message?: string
    result_preview?: string
  } | null
  input_data?: {
    task?: string
    context_injected?: Record<string, unknown>
  } | null
  error_message?: string
  tokens_used?: number
  cost?: number
  execution_time_ms?: number
  created_at: string
  completed_at?: string
}

interface RelatedMemory {
  id: string
  title: string
  content: string
  valence: 'positive' | 'negative' | 'neutral'
  memory_type: string
  importance_score: number
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

// =============================================================================
// Session 734: Channels Tab Component - "Slack for AI Agents"
// =============================================================================

interface Channel {
  id: string
  name: string
  display_name?: string
  description: string
  channel_type: string
  topic?: string
  is_public: boolean
  is_archived: boolean
  member_count: number
  message_count: number
  last_activity?: string
  created_at: string
}

interface ChannelMessage {
  id: string
  channel: string
  content: string
  message_type: string
  sender_agent?: { id: string; name: string }
  sender_user?: { id: string; username: string }
  created_at: string
  reactions?: Record<string, number>
}

interface ChannelMembership {
  id: string
  agent?: { id: string; name: string }
  role: string
  is_active: boolean
  presence_status: string
  joined_at: string
}

function ChannelsTab() {
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const queryClient = useQueryClient()

  // Fetch channels
  const { data: channelsData, isLoading: channelsLoading } = useQuery({
    queryKey: ['agent-channels'],
    queryFn: async () => {
      const response = await agentChannelsApi.list()
      return response.data
    },
  })

  // Fetch messages for selected channel
  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['channel-messages', selectedChannel?.id],
    queryFn: async () => {
      if (!selectedChannel) return { results: [] }
      const response = await agentChannelsApi.messages(selectedChannel.id, { limit: 50 })
      return response.data
    },
    enabled: !!selectedChannel,
  })

  // Fetch memberships for selected channel
  const { data: membershipsData } = useQuery({
    queryKey: ['channel-memberships', selectedChannel?.id],
    queryFn: async () => {
      if (!selectedChannel) return { results: [] }
      const response = await agentChannelsApi.memberships(selectedChannel.id)
      return response.data
    },
    enabled: !!selectedChannel,
  })

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!selectedChannel) throw new Error('No channel selected')
      return agentChannelsApi.sendMessage({
        channel: selectedChannel.id,
        content,
        message_type: 'text',
      })
    },
    onSuccess: () => {
      setNewMessage('')
      queryClient.invalidateQueries({ queryKey: ['channel-messages', selectedChannel?.id] })
    },
  })

  const channels: Channel[] = channelsData?.results || channelsData || []
  const messages: ChannelMessage[] = messagesData?.results || messagesData || []
  const memberships: ChannelMembership[] = membershipsData?.results || membershipsData || []

  const handleSendMessage = () => {
    if (newMessage.trim() && selectedChannel) {
      sendMessageMutation.mutate(newMessage.trim())
    }
  }

  const getChannelTypeColor = (type: string) => {
    switch (type) {
      case 'project': return 'bg-accent-purple/20 text-accent-purple'
      case 'topic': return 'bg-accent-cyan/20 text-accent-cyan'
      case 'team': return 'bg-accent-green/20 text-accent-green'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 h-[calc(100vh-300px)] min-h-[500px]">
      {/* Channel List */}
      <div className="lg:col-span-1 card overflow-hidden flex flex-col">
        <div className="p-4 border-b border-dark-border">
          <h3 className="font-semibold flex items-center gap-2">
            <Hash size={18} className="text-accent-cyan" />
            Channels
            <span className="text-xs text-gray-500 ml-auto">{channels.length}</span>
          </h3>
        </div>
        <div className="flex-1 overflow-y-auto">
          {channelsLoading ? (
            <div className="p-4 text-center text-gray-400">Loading channels...</div>
          ) : channels.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <Hash size={32} className="mx-auto mb-2 opacity-50" />
              <p>No channels yet</p>
              <p className="text-xs text-gray-500 mt-1">Channels will appear here when agents collaborate</p>
            </div>
          ) : (
            <div className="divide-y divide-dark-border">
              {channels.map((channel) => (
                <button
                  key={channel.id}
                  onClick={() => setSelectedChannel(channel)}
                  className={cn(
                    'w-full p-3 text-left hover:bg-dark-bg/50 transition-colors',
                    selectedChannel?.id === channel.id && 'bg-primary-600/20 border-l-2 border-primary-500'
                  )}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Hash size={14} className="text-gray-400" />
                    <span className="font-medium text-white truncate">
                      {channel.display_name || channel.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className={cn('px-1.5 py-0.5 rounded', getChannelTypeColor(channel.channel_type))}>
                      {channel.channel_type}
                    </span>
                    <span className="text-gray-500">{channel.member_count} members</span>
                  </div>
                  {channel.description && (
                    <p className="text-xs text-gray-500 mt-1 line-clamp-1">{channel.description}</p>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Message Thread */}
      <div className="lg:col-span-2 card overflow-hidden flex flex-col">
        {selectedChannel ? (
          <>
            {/* Channel Header */}
            <div className="p-4 border-b border-dark-border">
              <div className="flex items-center gap-2">
                <Hash size={20} className="text-accent-cyan" />
                <h3 className="font-semibold text-white">
                  {selectedChannel.display_name || selectedChannel.name}
                </h3>
                <span className={cn('text-xs px-2 py-0.5 rounded', getChannelTypeColor(selectedChannel.channel_type))}>
                  {selectedChannel.channel_type}
                </span>
              </div>
              {selectedChannel.topic && (
                <p className="text-sm text-gray-400 mt-1">{selectedChannel.topic}</p>
              )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messagesLoading ? (
                <div className="text-center text-gray-400">Loading messages...</div>
              ) : messages.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No messages yet</p>
                  <p className="text-xs text-gray-500 mt-1">Be the first to send a message!</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div key={message.id} className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary-600/30 flex items-center justify-center flex-shrink-0">
                      <Bot size={16} className="text-primary-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-white text-sm">
                          {message.sender_agent?.name || message.sender_user?.username || 'System'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(message.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">{message.content}</p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-dark-border">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={`Message #${selectedChannel.display_name || selectedChannel.name}`}
                  className="flex-1 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim() || sendMessageMutation.isPending}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Hash size={48} className="mx-auto mb-3 opacity-30" />
              <p className="text-lg">Select a channel</p>
              <p className="text-sm text-gray-500 mt-1">Choose a channel from the list to view messages</p>
            </div>
          </div>
        )}
      </div>

      {/* Members Panel */}
      <div className="lg:col-span-1 card overflow-hidden flex flex-col">
        <div className="p-4 border-b border-dark-border">
          <h3 className="font-semibold flex items-center gap-2">
            <Users size={18} className="text-accent-green" />
            Members
            {selectedChannel && (
              <span className="text-xs text-gray-500 ml-auto">{memberships.length}</span>
            )}
          </h3>
        </div>
        <div className="flex-1 overflow-y-auto">
          {!selectedChannel ? (
            <div className="p-4 text-center text-gray-500 text-sm">
              Select a channel to see members
            </div>
          ) : memberships.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <Users size={24} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">No members yet</p>
            </div>
          ) : (
            <div className="divide-y divide-dark-border">
              {memberships.map((membership) => (
                <div key={membership.id} className="p-3 flex items-center gap-3">
                  <div className="relative">
                    <div className="w-8 h-8 rounded-full bg-primary-600/30 flex items-center justify-center">
                      <Bot size={14} className="text-primary-400" />
                    </div>
                    <span
                      className={cn(
                        'absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-dark-card',
                        membership.presence_status === 'online' ? 'bg-accent-green' :
                        membership.presence_status === 'busy' ? 'bg-accent-amber' :
                        'bg-gray-500'
                      )}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">
                      {membership.agent?.name || 'Unknown Agent'}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">{membership.role}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AgentsPage() {
  const [realtimeUpdates, setRealtimeUpdates] = useState<AgentUpdate[]>([])
  const [learningEvents, setLearningEvents] = useState<LearningEvent[]>([])
  // Session 734: Added 'monitoring', 'tools', 'templates' tabs (orchestrations moved to dedicated OrchestrationPage)
  const [activeTab, setActiveTab] = useState<'directory' | 'activity' | 'learning' | 'channels' | 'monitoring' | 'tools' | 'templates'>('directory')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['creation', 'research', 'strategy']))
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  // Session 695: Dream Gallery Modal state
  const [selectedDream, setSelectedDream] = useState<Dream | null>(null)
  // Session 782: Conversation viewer removed - consolidated to ConversationContractPage
  const navigate = useNavigate()
  // Session 696: Decision Insights Panel state
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null)
  // Session 696: Experiment Modal state (for "pilot" activities)
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null)
  // Session 697: Knowledge Transfer Modal state
  const [selectedTransfer, setSelectedTransfer] = useState<LearningFeedItem | null>(null)
  // Session 760: Agent Execution Output Detail Modal state
  const [selectedExecution, setSelectedExecution] = useState<AgentExecutionDetail | null>(null)
  const [relatedMemory, setRelatedMemory] = useState<RelatedMemory | null>(null)
  const [executionDetailLoading, setExecutionDetailLoading] = useState(false)
  // Session 761: Generic Activity Detail Modal for items without matching entities
  const [selectedActivity, setSelectedActivity] = useState<RecentActivity | null>(null)

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

  // Session 745: Knowledge gaps for learning tab
  const { data: knowledgeGapsResponse, isLoading: loadingKnowledgeGaps } = useQuery({
    queryKey: ['knowledge-gaps'],
    queryFn: () => collectiveApi.knowledgeGaps(),
    enabled: activeTab === 'learning',
  })
  const knowledgeGaps = knowledgeGapsResponse?.data?.gaps || knowledgeGapsResponse?.data || []

  // Session 695: Dreams for Dream Gallery Modal
  const { data: dreamsResponse } = useQuery({
    queryKey: ['agent-dreams'],
    queryFn: () => dreamsApi.list({ limit: 50, timeRange: '7d' }),
    refetchInterval: 60000, // Refresh every minute
  })
  const dreams: Dream[] = dreamsResponse?.data?.dreams || []
  const dreamStats = {
    todayCount: dreamsResponse?.data?.today_count || 0,
    unreadCount: dreamsResponse?.data?.unread_count || 0,
  }

  // Session 782: Conversations query removed - consolidated to ConversationContractPage

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

  // Session 760: Unified executions for Output Detail Modal
  const { data: executionsResponse, refetch: refetchExecutions, isRefetching: isRefetchingExecutions } = useQuery({
    queryKey: ['unified-executions'],
    queryFn: () => agentsApi.unifiedExecutions({ limit: 30 }),
    refetchInterval: 30000,
    enabled: activeTab === 'activity',
  })
  const unifiedExecutions: AgentExecutionDetail[] = executionsResponse?.data?.data?.executions || []

  // Session 760: Function to load execution detail and open modal
  const handleExecutionClick = async (executionId: string) => {
    setExecutionDetailLoading(true)
    try {
      const response = await agentsApi.executionDetail(executionId)
      if (response.data?.success) {
        setSelectedExecution(response.data.data.execution)
        setRelatedMemory(response.data.data.related_memory)
      }
    } catch (error) {
      console.error('Failed to load execution detail:', error)
    } finally {
      setExecutionDetailLoading(false)
    }
  }

  // Session 734: Monitoring dashboard state and queries
  const [monitoringPeriod, setMonitoringPeriod] = useState<'1h' | '24h' | '7d' | '30d'>('24h')
  const { data: monitoringData, isLoading: monitoringLoading, refetch: refetchMonitoring } = useQuery({
    queryKey: ['agent-monitoring', monitoringPeriod],
    queryFn: async () => {
      const response = await agentMonitoringApi.dashboard(monitoringPeriod)
      // API returns { success: true, data: { summary: {...}, system: {...} } }
      return response.data?.data || response.data
    },
    enabled: activeTab === 'monitoring',
  })

  const { data: alertsData } = useQuery({
    queryKey: ['agent-alerts'],
    queryFn: async () => {
      const response = await agentMonitoringApi.alerts()
      // API returns { success: true, data: { alerts: [...] } }
      return response.data?.data || response.data
    },
    enabled: activeTab === 'monitoring',
  })

  // Session 734: Agent Tools query
  const [toolTypeFilter, setToolTypeFilter] = useState<string>('')
  const [toolSearch, setToolSearch] = useState<string>('')  // Session 761: Tool search
  const [selectedTool, setSelectedTool] = useState<{
    id: string
    name: string
    display_name: string
    description: string
    tool_type: string
    is_active: boolean
    usage_count: number
    success_rate: number
    avg_response_time_ms: number
    tool_version: string
    endpoint_url?: string
    supported_operations?: string[]
    required_permissions?: string[]
    compatible_agent_count?: number
    created_at?: string
    updated_at?: string
  } | null>(null)  // Session 761: Tool detail modal
  const { data: toolsData, isLoading: toolsLoading, refetch: refetchTools } = useQuery({
    queryKey: ['agent-tools', toolTypeFilter],
    queryFn: async () => {
      const params = toolTypeFilter ? { tool_type: toolTypeFilter } : undefined
      const response = await agentToolsApi.list(params)
      return response.data?.results || response.data?.data?.results || response.data || []
    },
    enabled: activeTab === 'tools',
  })

  // Session 734: Agent Templates CRUD
  const [templateSpecFilter, setTemplateSpecFilter] = useState<string>('')
  const [templateSearch, setTemplateSearch] = useState<string>('')
  const [templateModalOpen, setTemplateModalOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<{
    id: string
    name: string
    display_name: string
    description: string
    specialization: string
    capabilities: string
    system_prompt: string
    personality_traits: string
    llm_provider: string
    llm_model: string
    routing_keywords: string
    is_public: boolean
    learning_enabled: boolean
  } | null>(null)
  const [templateForm, setTemplateForm] = useState({
    name: '',
    display_name: '',
    description: '',
    specialization: '',
    capabilities: '',
    system_prompt: '',
    personality_traits: '',
    llm_provider: '',
    llm_model: '',
    routing_keywords: '',
    is_public: false,
    learning_enabled: true,
  })

  const { data: templatesData, isLoading: templatesLoading, refetch: refetchTemplates } = useQuery({
    queryKey: ['agent-templates', templateSpecFilter, templateSearch],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (templateSpecFilter) params.specialization = templateSpecFilter
      if (templateSearch) params.search = templateSearch
      const response = await agentTemplatesApi.list(params)
      return response.data?.results || response.data?.data?.results || response.data || []
    },
    enabled: activeTab === 'templates',
  })

  const createTemplateMutation = useMutation({
    mutationFn: (data: typeof templateForm) => agentTemplatesApi.create(data),
    onSuccess: () => {
      refetchTemplates()
      setTemplateModalOpen(false)
      setTemplateForm({
        name: '', display_name: '', description: '', specialization: '',
        capabilities: '', system_prompt: '', personality_traits: '',
        llm_provider: '', llm_model: '', routing_keywords: '',
        is_public: false, learning_enabled: true,
      })
    },
  })

  const updateTemplateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      agentTemplatesApi.update(id, data),
    onSuccess: () => {
      refetchTemplates()
      setTemplateModalOpen(false)
      setEditingTemplate(null)
    },
  })

  const deleteTemplateMutation = useMutation({
    mutationFn: (id: string) => agentTemplatesApi.delete(id),
    onSuccess: () => refetchTemplates(),
  })

  // Session 774: Orchestration functionality moved to dedicated OrchestrationPage
  // See /orchestration for workflow management

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
    if (msgType === 'connection_established' || msgType === 'connected' || msgType === 'pong') {
      return
    }

    // Session 746: Handle 'learning_activity' bulk messages from backend
    // Backend sends { type: 'learning_activity', feed_items: [...], stats: {...} }
    if (msgType === 'learning_activity') {
      const data = event as unknown as { feed_items?: Array<{
        timestamp: string
        type: string
        description: string
        teacher?: string
        student?: string
        knowledge?: string
      }> }
      if (data.feed_items && Array.isArray(data.feed_items)) {
        // Convert feed_items to LearningEvent format
        const convertedEvents = data.feed_items.map(item => ({
          type: 'learning_event' as const,
          agent_name: item.teacher || 'System',
          event_type: item.type === 'knowledge_transfer' ? 'Knowledge Transfer' :
                      item.type === 'self_learning' ? 'Self Learning' : item.type,
          description: item.description || item.knowledge || 'Learning activity',
          timestamp: item.timestamp,
          data: { teacher: item.teacher, student: item.student }
        }))
        setLearningEvents((prev) => [...convertedEvents, ...prev].slice(0, 50))
      }
      return
    }

    // Handle individual learning_event messages
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
        {(['directory', 'activity', 'learning', 'channels', 'monitoring', 'tools', 'templates'] as const).map((tab) => (
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

                  // Session 782: Conversations now link to unified Conversations page
                  const isConversationClickable = activity.type === 'conversation'

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
                      isConversationClickable ? () => navigate('/conversation-contract') :
                      isDecisionClickable ? () => setSelectedDecision(matchingDecision) :
                      isPilotClickable ? () => setSelectedExperiment(matchingExperiment) :
                      // Session 761: Show generic activity modal for items without matching entities
                      () => setSelectedActivity(activity)
                    }
                    className={cn(
                      "flex items-start gap-3 p-4 rounded-lg border border-dark-border transition-colors cursor-pointer",
                      isDreamClickable
                        ? "hover:border-accent-purple/50 hover:bg-accent-purple/5"
                        : isConversationClickable
                        ? "hover:border-accent-cyan/50 hover:bg-accent-cyan/5"
                        : isDecisionClickable
                        ? "hover:border-accent-amber/50 hover:bg-accent-amber/5"
                        : isPilotClickable
                        ? "hover:border-accent-green/50 hover:bg-accent-green/5"
                        // Session 761: Make non-matched items also clickable
                        : "hover:border-primary-500/50 hover:bg-primary-500/5"
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
                            View in Conversations
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

          {/* Session 760: Agent Executions Section with Output Detail */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Cpu size={18} className="text-accent-cyan" />
                Agent Executions
              </h3>
              <button
                onClick={() => refetchExecutions()}
                disabled={isRefetchingExecutions}
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <RefreshCw size={14} className={cn(isRefetchingExecutions && 'animate-spin')} />
                Refresh
              </button>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Click on any execution to view full output details
            </p>
            {unifiedExecutions.length > 0 ? (
              <div className="space-y-3 max-h-[400px] overflow-auto">
                {unifiedExecutions.map((execution) => (
                  <div
                    key={execution.id}
                    onClick={() => handleExecutionClick(execution.id)}
                    className={cn(
                      "p-4 rounded-lg border border-dark-border hover:border-accent-cyan/50 cursor-pointer transition-colors bg-dark-hover/30 hover:bg-accent-cyan/5",
                      executionDetailLoading && "opacity-50 pointer-events-none"
                    )}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Bot size={16} className="text-accent-cyan" />
                        <span className="font-medium text-white">{execution.agent_name}</span>
                        <span className={cn(
                          'text-xs px-2 py-0.5 rounded',
                          execution.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                          execution.status === 'failed' ? 'bg-accent-red/20 text-accent-red' :
                          execution.status === 'running' ? 'bg-accent-amber/20 text-accent-amber' :
                          'bg-gray-500/20 text-gray-400'
                        )}>
                          {execution.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        {execution.execution_time_ms && execution.execution_time_ms > 0 && (
                          <span className="flex items-center gap-1">
                            <Clock size={12} />
                            {((execution.execution_time_ms ?? 0) / 1000).toFixed(1)}s
                          </span>
                        )}
                        {execution.tokens_used && execution.tokens_used > 0 && (
                          <span>{execution.tokens_used.toLocaleString()} tokens</span>
                        )}
                        {execution.cost && execution.cost > 0 && (
                          <span>${(execution.cost ?? 0).toFixed(4)}</span>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-gray-300 truncate">
                      {execution.task || 'No task description'}
                    </p>
                    {execution.output_data?.message && (
                      <p className="text-sm text-gray-500 mt-1 truncate">
                        {execution.output_data.message}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <Clock size={12} />
                      {formatTimestamp(execution.created_at, 'full')}
                      <span className="text-accent-cyan/60 flex items-center gap-1 ml-auto">
                        <Eye size={10} />
                        Click to view output
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Cpu className="mx-auto mb-2" size={32} />
                <p>No recent executions</p>
                <p className="text-sm text-gray-500 mt-1">
                  Agent executions will appear here
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
                                {((confidence ?? 0) * 100).toFixed(0)}% confidence
                              </span>
                            )}
                            {transfer.usefulness_score !== undefined && (
                              <span className="flex items-center gap-1">
                                <ThumbsUp size={12} />
                                {((transfer.usefulness_score ?? 0) * 100).toFixed(0)}% score
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

          {/* Session 745: Knowledge Gaps */}
          <div className="card">
            <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <AlertTriangle size={18} className="text-accent-amber" />
              Knowledge Gaps
            </h3>
            {loadingKnowledgeGaps ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="animate-spin" size={20} />
              </div>
            ) : knowledgeGaps.length > 0 ? (
              <div className="space-y-3">
                {knowledgeGaps.slice(0, 5).map((gap: { id?: string; topic: string; description?: string; priority?: string; affected_agents?: string[] }, idx: number) => (
                  <div key={gap.id || idx} className="p-3 rounded-lg border border-dark-border hover:border-accent-amber/50 transition-colors">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium text-sm">{gap.topic}</p>
                        {gap.description && (
                          <p className="text-xs text-gray-400 mt-1 line-clamp-2">{gap.description}</p>
                        )}
                        {gap.affected_agents && gap.affected_agents.length > 0 && (
                          <div className="flex items-center gap-1 mt-2">
                            <Users size={12} className="text-gray-500" />
                            <span className="text-xs text-gray-500">{gap.affected_agents.length} agents affected</span>
                          </div>
                        )}
                      </div>
                      {gap.priority && (
                        <span className={cn(
                          'px-2 py-0.5 text-xs rounded flex-shrink-0',
                          gap.priority === 'high' ? 'bg-accent-red/20 text-accent-red' :
                          gap.priority === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                          'bg-accent-green/20 text-accent-green'
                        )}>
                          {gap.priority}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-400">
                <CheckCircle className="mx-auto mb-2 opacity-50" size={24} />
                <p className="text-sm">No knowledge gaps identified</p>
                <p className="text-xs text-gray-500 mt-1">The system has comprehensive knowledge coverage</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Session 734: Channels Tab - Slack for AI Agents */}
      {activeTab === 'channels' && (
        <ChannelsTab />
      )}

      {/* Session 734: Monitoring Tab - Agent Performance Dashboard */}
      {activeTab === 'monitoring' && (
        <div className="space-y-6">
          {/* Monitoring Header */}
          <div className="card bg-gradient-to-r from-accent-cyan/10 to-accent-blue/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                  <BarChart3 size={28} className="text-accent-cyan" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">Agent Monitoring</h3>
                  <p className="text-gray-400">
                    Performance metrics and system health
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {/* Period Selector */}
                <select
                  value={monitoringPeriod}
                  onChange={(e) => setMonitoringPeriod(e.target.value as '1h' | '24h' | '7d' | '30d')}
                  className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="1h">Last Hour</option>
                  <option value="24h">Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                </select>
                <button
                  onClick={() => refetchMonitoring()}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <RefreshCw size={16} />
                  Refresh
                </button>
              </div>
            </div>
          </div>

          {monitoringLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : monitoringData ? (
            <>
              {/* Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-accent-green/20 flex items-center justify-center">
                      <CheckCircle size={20} className="text-accent-green" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Success Rate</p>
                      <p className="text-2xl font-bold">
                        {(monitoringData.summary?.success_rate || 0).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                      <Activity size={20} className="text-accent-cyan" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Executions (24h)</p>
                      <p className="text-2xl font-bold">
                        {(monitoringData.summary?.total_executions_24h || 0).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-accent-amber/20 flex items-center justify-center">
                      <Clock size={20} className="text-accent-amber" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Avg Execution Time</p>
                      <p className="text-2xl font-bold">
                        {(monitoringData.summary?.average_execution_time || 0).toFixed(2)}s
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
                      <Bot size={20} className="text-primary-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Active Agents</p>
                      <p className="text-2xl font-bold">
                        {monitoringData.summary?.active_agents || '0'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Session 773: AI Usage & Execution Breakdown - Previously Hidden Data */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                      <Zap size={20} className="text-accent-purple" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Tokens Used</p>
                      <p className="text-2xl font-bold">
                        {(monitoringData.summary?.total_tokens || 0).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-accent-green/20 flex items-center justify-center">
                      <DollarSign size={20} className="text-accent-green" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">AI Cost</p>
                      <p className="text-2xl font-bold">
                        ${(monitoringData.summary?.total_cost || 0).toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                      <CheckCircle size={20} className="text-accent-cyan" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Completed</p>
                      <p className="text-2xl font-bold text-accent-green">
                        {(monitoringData.summary?.completed || 0).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-accent-red/20 flex items-center justify-center">
                      <XCircle size={20} className="text-accent-red" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Failed</p>
                      <p className="text-2xl font-bold text-accent-red">
                        {(monitoringData.summary?.failed || 0).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* System & Cache Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* System Metrics */}
                <div className="card">
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Cpu size={18} className="text-accent-cyan" />
                    System Metrics
                  </h4>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-400">CPU Usage</span>
                        <span className="text-sm font-medium">
                          {monitoringData.system?.cpu_percent?.toFixed(1) || '0'}%
                        </span>
                      </div>
                      <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                        <div
                          className={cn(
                            "h-full transition-all",
                            (monitoringData.system?.cpu_percent || 0) > 80 ? "bg-accent-red" :
                            (monitoringData.system?.cpu_percent || 0) > 60 ? "bg-accent-amber" : "bg-accent-green"
                          )}
                          style={{ width: `${monitoringData.system?.cpu_percent || 0}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-400">Memory Usage</span>
                        <span className="text-sm font-medium">
                          {monitoringData.system?.memory_percent?.toFixed(1) || '0'}%
                        </span>
                      </div>
                      <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                        <div
                          className={cn(
                            "h-full transition-all",
                            (monitoringData.system?.memory_percent || 0) > 80 ? "bg-accent-red" :
                            (monitoringData.system?.memory_percent || 0) > 60 ? "bg-accent-amber" : "bg-accent-cyan"
                          )}
                          style={{ width: `${monitoringData.system?.memory_percent || 0}%` }}
                        />
                      </div>
                    </div>
                    <div className="pt-2 border-t border-dark-border">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Uptime</span>
                        <span className="text-gray-200">{monitoringData.system?.uptime || 'N/A'}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Cache Metrics */}
                <div className="card">
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Database size={18} className="text-accent-purple" />
                    Cache Performance
                  </h4>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-400">Hit Rate</span>
                        <span className="text-sm font-medium text-accent-green">
                          {monitoringData.cache?.hit_rate?.toFixed(1) || '0'}%
                        </span>
                      </div>
                      <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                        <div
                          className="h-full bg-accent-green transition-all"
                          style={{ width: `${monitoringData.cache?.hit_rate || 0}%` }}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 pt-2">
                      <div className="bg-dark-hover rounded-lg p-3">
                        <p className="text-xs text-gray-400">Cache Hits</p>
                        <p className="text-lg font-semibold text-accent-green">
                          {monitoringData.cache?.hits?.toLocaleString() || '0'}
                        </p>
                      </div>
                      <div className="bg-dark-hover rounded-lg p-3">
                        <p className="text-xs text-gray-400">Cache Misses</p>
                        <p className="text-lg font-semibold text-accent-red">
                          {monitoringData.cache?.misses?.toLocaleString() || '0'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Alerts Section */}
              {alertsData?.alerts && alertsData.alerts.length > 0 && (
                <div className="card border-accent-amber/30">
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <AlertTriangle size={18} className="text-accent-amber" />
                    Active Alerts
                    <span className="text-xs px-2 py-0.5 rounded-full bg-accent-amber/20 text-accent-amber">
                      {alertsData.alerts.length}
                    </span>
                  </h4>
                  <div className="space-y-2">
                    {alertsData.alerts.slice(0, 5).map((alert: { id: string; level: string; message: string; timestamp: string }, idx: number) => (
                      <div
                        key={alert.id || idx}
                        className={cn(
                          "p-3 rounded-lg border",
                          alert.level === 'critical' ? 'bg-accent-red/10 border-accent-red/30' :
                          alert.level === 'warning' ? 'bg-accent-amber/10 border-accent-amber/30' :
                          'bg-dark-hover border-dark-border'
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm">{alert.message}</span>
                          <span className="text-xs text-gray-400">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Agent Performance Table */}
              {monitoringData.agents && Object.keys(monitoringData.agents).length > 0 && (
                <div className="card">
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Bot size={18} className="text-primary-400" />
                    Agent Performance
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-dark-border text-left">
                          <th className="pb-3 text-sm font-medium text-gray-400">Agent</th>
                          <th className="pb-3 text-sm font-medium text-gray-400">Executions</th>
                          <th className="pb-3 text-sm font-medium text-gray-400">Success Rate</th>
                          <th className="pb-3 text-sm font-medium text-gray-400">Avg Time</th>
                          <th className="pb-3 text-sm font-medium text-gray-400">Tokens</th>
                          <th className="pb-3 text-sm font-medium text-gray-400">Cost</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-dark-border">
                        {Object.entries(monitoringData.agents).slice(0, 10).map(([name, stats]: [string, unknown]) => {
                          const agentStats = stats as { total_executions?: number; success_rate?: number; avg_execution_time?: number; total_tokens?: number; total_cost?: number }
                          const successRate = (agentStats.success_rate || 0) * 100
                          return (
                            <tr key={name} className="hover:bg-dark-hover/50">
                              <td className="py-3">
                                <span className="font-medium">{name}</span>
                              </td>
                              <td className="py-3 text-gray-300">
                                {(agentStats.total_executions || 0).toLocaleString()}
                              </td>
                              <td className="py-3">
                                <span className={cn(
                                  "text-sm",
                                  successRate >= 90 ? "text-accent-green" :
                                  successRate >= 70 ? "text-accent-amber" : "text-accent-red"
                                )}>
                                  {(successRate ?? 0).toFixed(1)}%
                                </span>
                              </td>
                              <td className="py-3 text-gray-300">
                                {(agentStats.avg_execution_time || 0).toFixed(2)}s
                              </td>
                              <td className="py-3 text-gray-300">
                                {(agentStats.total_tokens || 0).toLocaleString()}
                              </td>
                              <td className="py-3 text-accent-green">
                                ${(agentStats.total_cost || 0).toFixed(2)}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Session 774: Execution Timeline - Previously Hidden Data */}
              {monitoringData.timeline && monitoringData.timeline.length > 0 && (
                <div className="card">
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <TrendingUp size={18} className="text-accent-cyan" />
                    Execution Timeline
                  </h4>
                  <div className="h-48">
                    {/* Simple bar chart visualization */}
                    <div className="flex items-end justify-between h-full gap-1">
                      {monitoringData.timeline.map((point: { timestamp: string; executions: number; successful: number }, idx: number) => {
                        const maxExec = Math.max(...monitoringData.timeline.map((p: { executions: number }) => p.executions), 1)
                        const height = (point.executions / maxExec) * 100
                        const successHeight = (point.successful / maxExec) * 100
                        const timeLabel = point.timestamp ? new Date(point.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''
                        return (
                          <div key={idx} className="flex-1 flex flex-col items-center gap-1 group">
                            <div className="relative w-full h-40 flex items-end">
                              {/* Total executions bar */}
                              <div
                                className="w-full bg-accent-cyan/30 rounded-t transition-all group-hover:bg-accent-cyan/50"
                                style={{ height: `${height}%` }}
                              >
                                {/* Successful overlay */}
                                <div
                                  className="w-full bg-accent-green rounded-t absolute bottom-0"
                                  style={{ height: `${successHeight}%` }}
                                />
                              </div>
                              {/* Tooltip on hover */}
                              <div className="absolute -top-8 left-1/2 -translate-x-1/2 hidden group-hover:block bg-dark-card border border-dark-border rounded px-2 py-1 text-xs whitespace-nowrap z-10">
                                {point.executions} total, {point.successful} successful
                              </div>
                            </div>
                            {idx % Math.ceil(monitoringData.timeline.length / 6) === 0 && (
                              <span className="text-xs text-gray-500 truncate max-w-full">{timeLabel}</span>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                  <div className="flex items-center justify-center gap-6 mt-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-accent-cyan/30" />
                      <span className="text-gray-400">Total Executions</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-accent-green" />
                      <span className="text-gray-400">Successful</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Session 774: Recent Executions Feed - Previously Hidden Data */}
              {monitoringData.recent_executions && monitoringData.recent_executions.length > 0 && (
                <div className="card">
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Activity size={18} className="text-accent-purple" />
                    Recent Executions
                    <span className="text-xs px-2 py-0.5 rounded-full bg-accent-purple/20 text-accent-purple">
                      {monitoringData.recent_executions.length}
                    </span>
                  </h4>
                  <div className="space-y-2">
                    {monitoringData.recent_executions.map((exec: { id: string; agent_name: string; status: string; execution_time_ms: number; tokens_used: number; created_at: string }) => (
                      <div
                        key={exec.id}
                        className={cn(
                          "flex items-center justify-between p-3 rounded-lg border",
                          exec.status === 'completed' ? 'bg-accent-green/5 border-accent-green/20' :
                          exec.status === 'failed' ? 'bg-accent-red/5 border-accent-red/20' :
                          'bg-dark-hover border-dark-border'
                        )}
                      >
                        <div className="flex items-center gap-3">
                          {exec.status === 'completed' ? (
                            <CheckCircle size={16} className="text-accent-green" />
                          ) : exec.status === 'failed' ? (
                            <XCircle size={16} className="text-accent-red" />
                          ) : (
                            <Clock size={16} className="text-accent-amber animate-pulse" />
                          )}
                          <div>
                            <p className="font-medium text-sm">{exec.agent_name}</p>
                            <p className="text-xs text-gray-500">
                              {new Date(exec.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-400">
                            {exec.execution_time_ms ? `${((exec.execution_time_ms ?? 0) / 1000).toFixed(2)}s` : '—'}
                          </span>
                          <span className="text-gray-400">
                            {exec.tokens_used?.toLocaleString() || '0'} tokens
                          </span>
                          <span className={cn(
                            "px-2 py-0.5 rounded text-xs",
                            exec.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                            exec.status === 'failed' ? 'bg-accent-red/20 text-accent-red' :
                            'bg-accent-amber/20 text-accent-amber'
                          )}>
                            {exec.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="card text-center py-12 text-gray-400">
              <BarChart3 className="mx-auto mb-3" size={48} />
              <p className="text-lg font-medium">No Monitoring Data</p>
              <p className="text-sm text-gray-500 mt-1">
                Monitoring metrics will appear as agents execute tasks
              </p>
            </div>
          )}
        </div>
      )}

      {/* Session 734: Tools Tab - Agent Tool Registry */}
      {activeTab === 'tools' && (
        <div className="space-y-6">
          {/* Tools Header */}
          <div className="card bg-gradient-to-r from-accent-amber/10 to-accent-purple/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-lg bg-accent-amber/20 flex items-center justify-center">
                  <Wrench size={28} className="text-accent-amber" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">PA Utility Tools</h3>
                  <p className="text-gray-400">
                    Utility functions available to the Personal Assistant
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {/* Session 761: Tool Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                  <input
                    type="text"
                    value={toolSearch}
                    onChange={(e) => setToolSearch(e.target.value)}
                    placeholder="Search tools..."
                    className="pl-9 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm w-48"
                  />
                </div>
                {/* Tool Type Filter */}
                <select
                  value={toolTypeFilter}
                  onChange={(e) => setToolTypeFilter(e.target.value)}
                  className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">All Types</option>
                  <option value="api">API Integration</option>
                  <option value="computation">Computation</option>
                  <option value="data_processing">Data Processing</option>
                  <option value="communication">Communication</option>
                  <option value="content_generation">Content Generation</option>
                  <option value="analysis">Analysis</option>
                  <option value="monitoring">Monitoring</option>
                  <option value="integration">System Integration</option>
                </select>
                <button
                  onClick={() => refetchTools()}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <RefreshCw size={16} />
                  Refresh
                </button>
              </div>
            </div>
          </div>

          {toolsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : Array.isArray(toolsData) && toolsData.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {toolsData
                .filter((tool: { display_name: string; name: string; description: string }) =>
                  !toolSearch ||
                  tool.display_name.toLowerCase().includes(toolSearch.toLowerCase()) ||
                  tool.name.toLowerCase().includes(toolSearch.toLowerCase()) ||
                  tool.description.toLowerCase().includes(toolSearch.toLowerCase())
                )
                .map((tool: {
                id: string
                name: string
                display_name: string
                description: string
                tool_type: string
                is_active: boolean
                usage_count: number
                success_rate: number
                avg_response_time_ms: number
                tool_version: string
                endpoint_url?: string
                supported_operations?: string[]
                required_permissions?: string[]
                compatible_agent_count?: number
                created_at?: string
                updated_at?: string
              }) => (
                <div
                  key={tool.id}
                  onClick={() => setSelectedTool(tool)}
                  className={cn(
                    "card hover:border-primary-500/50 transition-colors cursor-pointer",
                    !tool.is_active && "opacity-60"
                  )}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "h-10 w-10 rounded-lg flex items-center justify-center",
                        tool.tool_type === 'api' ? 'bg-accent-cyan/20' :
                        tool.tool_type === 'computation' ? 'bg-accent-purple/20' :
                        tool.tool_type === 'data_processing' ? 'bg-accent-blue/20' :
                        tool.tool_type === 'communication' ? 'bg-accent-green/20' :
                        tool.tool_type === 'content_generation' ? 'bg-accent-pink/20' :
                        tool.tool_type === 'analysis' ? 'bg-accent-amber/20' :
                        'bg-gray-500/20'
                      )}>
                        {tool.tool_type === 'api' ? <ExternalLink size={20} className="text-accent-cyan" /> :
                         tool.tool_type === 'computation' ? <Cpu size={20} className="text-accent-purple" /> :
                         tool.tool_type === 'data_processing' ? <Database size={20} className="text-accent-blue" /> :
                         tool.tool_type === 'communication' ? <MessageSquare size={20} className="text-accent-green" /> :
                         tool.tool_type === 'content_generation' ? <Sparkles size={20} className="text-accent-pink" /> :
                         tool.tool_type === 'analysis' ? <BarChart3 size={20} className="text-accent-amber" /> :
                         <Wrench size={20} className="text-gray-400" />}
                      </div>
                      <div>
                        <h4 className="font-semibold text-white">{tool.display_name}</h4>
                        <span className="text-xs text-gray-500 capitalize">{tool.tool_type.replace('_', ' ')}</span>
                      </div>
                    </div>
                    <div className={cn(
                      "flex items-center gap-1 text-xs px-2 py-1 rounded",
                      tool.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                    )}>
                      <Power size={12} />
                      {tool.is_active ? 'Active' : 'Inactive'}
                    </div>
                  </div>

                  <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                    {tool.description}
                  </p>

                  <div className="grid grid-cols-3 gap-2 text-center border-t border-dark-border pt-3">
                    <div>
                      <p className="text-lg font-semibold text-white">{tool.usage_count.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">Uses</p>
                    </div>
                    <div>
                      <p className={cn(
                        "text-lg font-semibold",
                        tool.success_rate >= 0.9 ? 'text-accent-green' :
                        tool.success_rate >= 0.7 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {((tool.success_rate ?? 0) * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500">Success</p>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-white">{(tool.avg_response_time_ms ?? 0).toFixed(0)}ms</p>
                      <p className="text-xs text-gray-500">Avg Time</p>
                    </div>
                  </div>

                  {tool.endpoint_url && (
                    <div className="mt-3 pt-3 border-t border-dark-border">
                      <p className="text-xs text-gray-500 truncate flex items-center gap-1">
                        <ExternalLink size={12} />
                        {tool.endpoint_url}
                      </p>
                    </div>
                  )}

                  <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                    <span>v{tool.tool_version}</span>
                    <div className="flex items-center gap-3">
                      {/* Session 761: Show compatible agent count */}
                      {tool.compatible_agent_count !== undefined && tool.compatible_agent_count > 0 && (
                        <span className="flex items-center gap-1">
                          <Users size={12} />
                          {tool.compatible_agent_count} agents
                        </span>
                      )}
                      {tool.supported_operations && tool.supported_operations.length > 0 && (
                        <span>{tool.supported_operations.length} operations</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card text-center py-12 text-gray-400">
              <Wrench className="mx-auto mb-3 opacity-50" size={48} />
              <p className="text-lg font-medium">No Utility Tools Registered</p>
              <p className="text-sm text-gray-500 mt-1">
                Run `python manage.py sync_agent_tools` to populate
              </p>
            </div>
          )}
        </div>
      )}

      {/* Session 734: Templates Tab - Agent Templates CRUD */}
      {activeTab === 'templates' && (
        <div className="space-y-6">
          {/* Templates Header */}
          <div className="card bg-gradient-to-r from-accent-cyan/10 to-accent-blue/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                  <FileText size={28} className="text-accent-cyan" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">Agent Templates</h3>
                  <p className="text-gray-400">
                    Create and manage reusable agent configurations
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                  <input
                    type="text"
                    value={templateSearch}
                    onChange={(e) => setTemplateSearch(e.target.value)}
                    placeholder="Search templates..."
                    className="pl-9 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm w-48"
                  />
                </div>
                {/* Specialization Filter */}
                <select
                  value={templateSpecFilter}
                  onChange={(e) => setTemplateSpecFilter(e.target.value)}
                  className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">All Specializations</option>
                  <option value="creation">Creation</option>
                  <option value="research">Research</option>
                  <option value="strategy">Strategy</option>
                  <option value="analysis">Analysis</option>
                  <option value="development">Development</option>
                  <option value="executive">Executive</option>
                  <option value="content">Content</option>
                  <option value="security">Security</option>
                </select>
                <button
                  onClick={() => refetchTemplates()}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <RefreshCw size={16} />
                  Refresh
                </button>
                <button
                  onClick={() => {
                    setEditingTemplate(null)
                    setTemplateForm({
                      name: '', display_name: '', description: '', specialization: '',
                      capabilities: '', system_prompt: '', personality_traits: '',
                      llm_provider: '', llm_model: '', routing_keywords: '',
                      is_public: false, learning_enabled: true,
                    })
                    setTemplateModalOpen(true)
                  }}
                  className="btn btn-primary flex items-center gap-2"
                >
                  <Plus size={16} />
                  Create Template
                </button>
              </div>
            </div>
          </div>

          {templatesLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : Array.isArray(templatesData) && templatesData.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templatesData.map((template: {
                id: string
                name: string
                display_name: string
                description?: string
                specialization: string
                confidence_score: number
                success_rate: number
                usage_count: number
                avg_user_rating: number
                is_public: boolean
                is_verified: boolean
                llm_provider: string
                llm_model: string
                creator_name?: string
                created_at: string
                is_active: boolean
                capabilities?: string
                system_prompt?: string
                personality_traits?: string
                routing_keywords?: string
                learning_enabled?: boolean
              }) => (
                <div
                  key={template.id}
                  className={cn(
                    "card hover:border-primary-500/50 transition-colors",
                    !template.is_active && "opacity-60"
                  )}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "h-10 w-10 rounded-lg flex items-center justify-center",
                        template.specialization === 'creation' ? 'bg-accent-pink/20' :
                        template.specialization === 'research' ? 'bg-accent-cyan/20' :
                        template.specialization === 'strategy' ? 'bg-accent-amber/20' :
                        template.specialization === 'analysis' ? 'bg-accent-purple/20' :
                        template.specialization === 'development' ? 'bg-accent-green/20' :
                        template.specialization === 'executive' ? 'bg-accent-blue/20' :
                        'bg-gray-500/20'
                      )}>
                        <Bot size={20} className={cn(
                          template.specialization === 'creation' ? 'text-accent-pink' :
                          template.specialization === 'research' ? 'text-accent-cyan' :
                          template.specialization === 'strategy' ? 'text-accent-amber' :
                          template.specialization === 'analysis' ? 'text-accent-purple' :
                          template.specialization === 'development' ? 'text-accent-green' :
                          template.specialization === 'executive' ? 'text-accent-blue' :
                          'text-gray-400'
                        )} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-white">{template.display_name || template.name}</h4>
                        <span className="text-xs text-gray-500 capitalize">{template.specialization || 'General'}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {template.is_verified && (
                        <span className="text-accent-blue" title="Verified">
                          <CheckCircle size={16} />
                        </span>
                      )}
                      {template.is_public ? (
                        <span title="Public"><Globe size={14} className="text-gray-400" /></span>
                      ) : (
                        <span title="Private"><Lock size={14} className="text-gray-400" /></span>
                      )}
                    </div>
                  </div>

                  <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                    {template.description || 'No description provided'}
                  </p>

                  <div className="grid grid-cols-3 gap-2 text-center border-t border-dark-border pt-3">
                    <div>
                      <p className="text-lg font-semibold text-white">{template.usage_count.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">Uses</p>
                    </div>
                    <div>
                      <p className={cn(
                        "text-lg font-semibold",
                        template.success_rate >= 0.9 ? 'text-accent-green' :
                        template.success_rate >= 0.7 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {((template.success_rate ?? 0) * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500">Success</p>
                    </div>
                    <div className="flex items-center justify-center gap-1">
                      <Star size={14} className="text-accent-amber" />
                      <p className="text-lg font-semibold text-white">
                        {template.avg_user_rating?.toFixed(1) || '—'}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-dark-border flex items-center justify-between">
                    <div className="text-xs text-gray-500">
                      <span className="text-accent-cyan">{template.llm_provider}</span>
                      {template.llm_model && <span> / {template.llm_model}</span>}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setEditingTemplate({
                            id: template.id,
                            name: template.name,
                            display_name: template.display_name || '',
                            description: template.description || '',
                            specialization: template.specialization || '',
                            capabilities: template.capabilities || '',
                            system_prompt: template.system_prompt || '',
                            personality_traits: template.personality_traits || '',
                            llm_provider: template.llm_provider || '',
                            llm_model: template.llm_model || '',
                            routing_keywords: template.routing_keywords || '',
                            is_public: template.is_public,
                            learning_enabled: template.learning_enabled ?? true,
                          })
                          setTemplateForm({
                            name: template.name,
                            display_name: template.display_name || '',
                            description: template.description || '',
                            specialization: template.specialization || '',
                            capabilities: template.capabilities || '',
                            system_prompt: template.system_prompt || '',
                            personality_traits: template.personality_traits || '',
                            llm_provider: template.llm_provider || '',
                            llm_model: template.llm_model || '',
                            routing_keywords: template.routing_keywords || '',
                            is_public: template.is_public,
                            learning_enabled: template.learning_enabled ?? true,
                          })
                          setTemplateModalOpen(true)
                        }}
                        className="p-1.5 rounded hover:bg-dark-border transition-colors text-gray-400 hover:text-accent-cyan"
                        title="Edit template"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm(`Delete template "${template.display_name || template.name}"?`)) {
                            deleteTemplateMutation.mutate(template.id)
                          }
                        }}
                        className="p-1.5 rounded hover:bg-dark-border transition-colors text-gray-400 hover:text-accent-red"
                        title="Delete template"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  {template.creator_name && (
                    <div className="mt-2 text-xs text-gray-500">
                      Created by {template.creator_name}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="card text-center py-12 text-gray-400">
              <FileText className="mx-auto mb-3 opacity-50" size={48} />
              <p className="text-lg font-medium">No Templates Found</p>
              <p className="text-sm text-gray-500 mt-1">
                {templateSearch || templateSpecFilter
                  ? 'Try adjusting your search or filter'
                  : 'Create your first agent template to get started'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Session 734: Template Create/Edit Modal */}
      {templateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between p-6 border-b border-dark-border">
              <h2 className="text-xl font-bold">
                {editingTemplate ? 'Edit Template' : 'Create New Template'}
              </h2>
              <button
                onClick={() => {
                  setTemplateModalOpen(false)
                  setEditingTemplate(null)
                }}
                className="p-2 rounded-lg hover:bg-dark-border transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[calc(90vh-150px)] space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name (slug)</label>
                  <input
                    type="text"
                    value={templateForm.name}
                    onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                    placeholder="my-agent-template"
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Display Name</label>
                  <input
                    type="text"
                    value={templateForm.display_name}
                    onChange={(e) => setTemplateForm({ ...templateForm, display_name: e.target.value })}
                    placeholder="My Agent Template"
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={templateForm.description}
                  onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
                  placeholder="Describe what this agent does..."
                  rows={3}
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Specialization</label>
                  <select
                    value={templateForm.specialization}
                    onChange={(e) => setTemplateForm({ ...templateForm, specialization: e.target.value })}
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                  >
                    <option value="">Select...</option>
                    <option value="creation">Creation</option>
                    <option value="research">Research</option>
                    <option value="strategy">Strategy</option>
                    <option value="analysis">Analysis</option>
                    <option value="development">Development</option>
                    <option value="executive">Executive</option>
                    <option value="content">Content</option>
                    <option value="security">Security</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">LLM Provider</label>
                  <select
                    value={templateForm.llm_provider}
                    onChange={(e) => setTemplateForm({ ...templateForm, llm_provider: e.target.value })}
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                  >
                    <option value="">Select...</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="together">Together AI</option>
                    <option value="ollama">Ollama</option>
                    <option value="deepseek">DeepSeek</option>
                    <option value="gemini">Gemini</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">LLM Model</label>
                <input
                  type="text"
                  value={templateForm.llm_model}
                  onChange={(e) => setTemplateForm({ ...templateForm, llm_model: e.target.value })}
                  placeholder="gpt-4, claude-3-opus, etc."
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Capabilities</label>
                <textarea
                  value={templateForm.capabilities}
                  onChange={(e) => setTemplateForm({ ...templateForm, capabilities: e.target.value })}
                  placeholder="List agent capabilities..."
                  rows={2}
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">System Prompt</label>
                <textarea
                  value={templateForm.system_prompt}
                  onChange={(e) => setTemplateForm({ ...templateForm, system_prompt: e.target.value })}
                  placeholder="Enter system prompt for the agent..."
                  rows={4}
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg resize-none font-mono text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Personality Traits</label>
                <input
                  type="text"
                  value={templateForm.personality_traits}
                  onChange={(e) => setTemplateForm({ ...templateForm, personality_traits: e.target.value })}
                  placeholder="analytical, friendly, detail-oriented"
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Routing Keywords</label>
                <input
                  type="text"
                  value={templateForm.routing_keywords}
                  onChange={(e) => setTemplateForm({ ...templateForm, routing_keywords: e.target.value })}
                  placeholder="research, analyze, investigate"
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                />
              </div>

              <div className="flex gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={templateForm.is_public}
                    onChange={(e) => setTemplateForm({ ...templateForm, is_public: e.target.checked })}
                    className="rounded border-dark-border"
                  />
                  <span className="text-sm">Public Template</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={templateForm.learning_enabled}
                    onChange={(e) => setTemplateForm({ ...templateForm, learning_enabled: e.target.checked })}
                    className="rounded border-dark-border"
                  />
                  <span className="text-sm">Learning Enabled</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end gap-3 p-6 border-t border-dark-border">
              <button
                onClick={() => {
                  setTemplateModalOpen(false)
                  setEditingTemplate(null)
                }}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (editingTemplate) {
                    updateTemplateMutation.mutate({
                      id: editingTemplate.id,
                      data: templateForm,
                    })
                  } else {
                    createTemplateMutation.mutate(templateForm)
                  }
                }}
                disabled={!templateForm.name || !templateForm.display_name || createTemplateMutation.isPending || updateTemplateMutation.isPending}
                className="btn btn-primary flex items-center gap-2"
              >
                {(createTemplateMutation.isPending || updateTemplateMutation.isPending) && (
                  <Loader2 size={16} className="animate-spin" />
                )}
                {editingTemplate ? 'Save Changes' : 'Create Template'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 774: Orchestration functionality moved to dedicated OrchestrationPage at /orchestration */}
      {/* Session 695: Dream Gallery Modal */}
      {selectedDream && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header - Session 761: flex-shrink-0 */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-purple/10 to-accent-pink/10 flex-shrink-0">
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

            {/* Modal Content - Session 761: flex-1 for proper scrolling */}
            <div className="p-6 overflow-y-auto flex-1 min-h-0 space-y-6">
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

              {/* Inspiration - Session 761: Full text with proper wrapping */}
              {selectedDream.inspiration && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Lightbulb size={14} className="text-accent-amber" />
                    Inspiration
                  </h3>
                  <div className="bg-accent-amber/5 border border-accent-amber/20 rounded-lg p-4 text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">
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

              {/* Related Topics - Session 761: Show full text, not truncated */}
              {selectedDream.related_topics && selectedDream.related_topics.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Layers size={14} />
                    Related Topics
                  </h3>
                  <div className="space-y-2">
                    {selectedDream.related_topics.map((topic, idx) => (
                      <div
                        key={idx}
                        className="text-sm px-4 py-2 rounded-lg bg-dark-hover text-gray-300 border border-dark-border whitespace-pre-wrap"
                      >
                        {typeof topic === 'string' ? topic : 'Topic'}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer - Session 761: flex-shrink-0 to always show */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50 flex-shrink-0">
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
                      dreamsApi.react(selectedDream.id, emoji).catch(() => {})
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

      {/* Session 782: Conversation Thread Viewer Modal removed - consolidated to ConversationContractPage */}

      {/* Session 696: Decision Insights Panel Modal */}
      {selectedDecision && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header - Session 761: flex-shrink-0 */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-amber/10 to-accent-green/10 flex-shrink-0">
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

            {/* Participants Strip - Session 761: flex-shrink-0 */}
            <div className="px-6 py-3 border-b border-dark-border bg-dark-hover/30 flex items-center gap-2 flex-wrap flex-shrink-0">
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

            {/* Modal Content - Session 761: flex-1 for proper scrolling */}
            <div className="p-6 overflow-y-auto flex-1 min-h-0 space-y-6">
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

            {/* Modal Footer - Session 761: flex-shrink-0 to always show */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50 flex-shrink-0">
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
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header - Session 761: flex-shrink-0 */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-green/10 to-accent-cyan/10 flex-shrink-0">
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

            {/* KPI Progress - Session 761: flex-shrink-0 */}
            <div className="px-6 py-4 border-b border-dark-border bg-dark-hover/30 flex-shrink-0">
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

            {/* Modal Content - Session 761: flex-1 for proper scrolling */}
            <div className="p-6 overflow-y-auto flex-1 min-h-0 space-y-6">
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

            {/* Modal Footer - Session 761: flex-shrink-0 to always show */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50 flex-shrink-0">
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
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className={cn(
              "flex items-start justify-between p-6 border-b border-dark-border flex-shrink-0",
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
                      +{((selectedTransfer.effectiveness_gain ?? 0) * 100).toFixed(1)}% effectiveness
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

            {/* Modal Body - Session 761: Use flex-1 for proper scrolling */}
            <div className="p-6 overflow-y-auto flex-1 min-h-0 space-y-6">
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
                      ? `${((selectedTransfer.knowledge_full?.confidence ?? 0) * 100).toFixed(0)}%`
                      : '-'}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-dark-hover/50 text-center">
                  <div className="text-xs text-gray-500 mb-1">Usefulness Score</div>
                  <div className="text-lg font-bold text-accent-cyan">
                    {selectedTransfer.usefulness_score !== undefined
                      ? `${((selectedTransfer.usefulness_score ?? 0) * 100).toFixed(0)}%`
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
                        ? `+${((selectedTransfer.effectiveness_gain ?? 0) * 100).toFixed(1)}%`
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

            {/* Modal Footer - Session 761: flex-shrink-0 to always show */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50 flex-shrink-0">
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

      {/* Session 760: Agent Execution Output Detail Modal */}
      {selectedExecution && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header - Session 761: flex-shrink-0 */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border bg-gradient-to-r from-accent-cyan/10 to-accent-green/10 flex-shrink-0">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Bot size={24} className="text-accent-cyan" />
                  <h2 className="text-xl font-bold text-white">{selectedExecution.agent_display_name || selectedExecution.agent_name}</h2>
                  <span className={cn(
                    'text-xs px-2 py-1 rounded',
                    selectedExecution.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                    selectedExecution.status === 'failed' ? 'bg-accent-red/20 text-accent-red' :
                    'bg-accent-amber/20 text-accent-amber'
                  )}>
                    {selectedExecution.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span className="flex items-center gap-1">
                    <Clock size={14} />
                    {formatTimestamp(selectedExecution.created_at, 'full')}
                  </span>
                  {selectedExecution.execution_time_ms && selectedExecution.execution_time_ms > 0 && (
                    <span>Duration: {((selectedExecution.execution_time_ms ?? 0) / 1000).toFixed(2)}s</span>
                  )}
                  {selectedExecution.tokens_used && selectedExecution.tokens_used > 0 && (
                    <span>{selectedExecution.tokens_used.toLocaleString()} tokens</span>
                  )}
                  {selectedExecution.cost && selectedExecution.cost > 0 && (
                    <span className="text-accent-amber">Cost: ${(selectedExecution.cost ?? 0).toFixed(4)}</span>
                  )}
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedExecution(null)
                  setRelatedMemory(null)
                }}
                className="p-2 rounded-lg hover:bg-dark-border transition-colors text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content - Session 761: flex-1 for proper scrolling */}
            <div className="p-6 overflow-y-auto flex-1 min-h-0 space-y-6">
              {/* Task Section */}
              <div>
                <h3 className="text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                  <FileText size={14} />
                  Task
                </h3>
                <div className="bg-dark-lighter rounded-lg p-4 border border-dark-border">
                  <p className="text-gray-200 whitespace-pre-wrap">{selectedExecution.task || 'No task description'}</p>
                </div>
              </div>

              {/* Error Section (if failed) */}
              {selectedExecution.status === 'failed' && selectedExecution.error_message && (
                <div>
                  <h3 className="text-sm font-semibold text-accent-red mb-2 flex items-center gap-2">
                    <AlertTriangle size={14} />
                    Error
                  </h3>
                  <div className="bg-accent-red/10 rounded-lg p-4 border border-accent-red/30">
                    <p className="text-accent-red whitespace-pre-wrap font-mono text-sm">{selectedExecution.error_message}</p>
                  </div>
                </div>
              )}

              {/* Output Section */}
              {selectedExecution.output_data && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                    <Database size={14} />
                    Output Data
                  </h3>

                  {/* Message */}
                  {selectedExecution.output_data.message && (
                    <div className="bg-dark-lighter rounded-lg p-4 border border-dark-border mb-4">
                      <h4 className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Message</h4>
                      <div className="text-gray-200 whitespace-pre-wrap">
                        {(() => {
                          const msg = selectedExecution.output_data.message
                          // Format code blocks
                          if (msg.includes('```')) {
                            return msg.split(/(```[\s\S]*?```)/g).map((part, idx) => {
                              if (part.startsWith('```')) {
                                const code = part.replace(/```\w*\n?/g, '').replace(/```$/g, '')
                                return (
                                  <pre key={idx} className="bg-dark-card p-3 rounded-lg font-mono text-sm text-accent-cyan overflow-x-auto my-2">
                                    {code}
                                  </pre>
                                )
                              }
                              return <span key={idx}>{part}</span>
                            })
                          }
                          return msg
                        })()}
                      </div>
                    </div>
                  )}

                  {/* Data Object */}
                  {selectedExecution.output_data.data && Object.keys(selectedExecution.output_data.data).length > 0 && (
                    <div className="bg-dark-lighter rounded-lg p-4 border border-dark-border">
                      <h4 className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Structured Data</h4>

                      {/* Special handling for images */}
                      {selectedExecution.output_data.data.images && selectedExecution.output_data.data.images.length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-purple mb-2">Generated Images ({selectedExecution.output_data.data.images.length})</h5>
                          <div className="grid grid-cols-2 gap-3">
                            {selectedExecution.output_data.data.images.map((img: { image_url?: string; image_id?: string }, idx: number) => (
                              <div key={idx} className="bg-dark-card rounded-lg p-2 border border-dark-border">
                                {img.image_url && (
                                  <a href={img.image_url} target="_blank" rel="noopener noreferrer" className="text-accent-cyan hover:underline text-sm">
                                    View Image {idx + 1}
                                  </a>
                                )}
                                {img.image_id && (
                                  <p className="text-xs text-gray-500 mt-1 font-mono truncate">ID: {img.image_id}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Special handling for tool_results */}
                      {selectedExecution.output_data.data.tool_results && selectedExecution.output_data.data.tool_results.length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-amber mb-2">Tool Results</h5>
                          <div className="space-y-2">
                            {selectedExecution.output_data.data.tool_results.map((tr, idx) => (
                              <div key={idx} className="bg-dark-card rounded-lg p-3 border border-dark-border">
                                <div className="flex items-center gap-2 mb-2">
                                  <Wrench size={14} className="text-accent-amber" />
                                  <span className="font-medium text-white">{tr.tool || `Tool ${idx + 1}`}</span>
                                </div>
                                {tr.result && (
                                  <pre className="text-xs text-gray-400 overflow-x-auto max-h-32">
                                    {JSON.stringify(tr.result, null, 2)}
                                  </pre>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Special handling for research results */}
                      {selectedExecution.output_data.data.results && selectedExecution.output_data.data.results.length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-cyan mb-2">Research Results ({selectedExecution.output_data.data.results.length})</h5>
                          <div className="space-y-2">
                            {selectedExecution.output_data.data.results.slice(0, 5).map((result, idx) => (
                              <div key={idx} className="bg-dark-card rounded-lg p-3 border border-dark-border">
                                {result.source && (
                                  <span className="text-xs text-accent-green">{result.source}</span>
                                )}
                                {result.title && (
                                  <p className="text-sm text-white font-medium mt-1">{result.title}</p>
                                )}
                                {result.summary && (
                                  <p className="text-xs text-gray-400 mt-1">{result.summary}</p>
                                )}
                                {result.data && !result.summary && (
                                  <pre className="text-xs text-gray-400 mt-1 overflow-x-auto max-h-24">
                                    {JSON.stringify(result.data, null, 2)}
                                  </pre>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Special handling for ContentWriterAgent content */}
                      {selectedExecution.output_data.data.content && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-green mb-2">Generated Content</h5>
                          <div className="bg-dark-card rounded-lg p-3 border border-dark-border">
                            {selectedExecution.output_data.data.content_type && (
                              <span className="inline-block px-2 py-0.5 text-xs bg-accent-green/20 text-accent-green rounded mb-2">
                                {selectedExecution.output_data.data.content_type}
                              </span>
                            )}
                            {typeof selectedExecution.output_data.data.content === 'object' ? (
                              <>
                                {(selectedExecution.output_data.data.content as { title?: string }).title && (
                                  <h6 className="text-white font-medium mb-2">{(selectedExecution.output_data.data.content as { title: string }).title}</h6>
                                )}
                                {(selectedExecution.output_data.data.content as { body?: string }).body && (
                                  <p className="text-gray-300 text-sm whitespace-pre-wrap">{(selectedExecution.output_data.data.content as { body: string }).body}</p>
                                )}
                                {!(selectedExecution.output_data.data.content as { body?: string }).body && (
                                  <pre className="text-xs text-gray-400 overflow-x-auto">
                                    {JSON.stringify(selectedExecution.output_data.data.content, null, 2)}
                                  </pre>
                                )}
                              </>
                            ) : (
                              <p className="text-gray-300 text-sm whitespace-pre-wrap">{String(selectedExecution.output_data.data.content)}</p>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Special handling for recommendations */}
                      {selectedExecution.output_data.data.recommendations && Array.isArray(selectedExecution.output_data.data.recommendations) && selectedExecution.output_data.data.recommendations.length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-purple mb-2">Recommendations ({selectedExecution.output_data.data.recommendations.length})</h5>
                          <div className="space-y-2">
                            {selectedExecution.output_data.data.recommendations.map((rec: string | { title?: string; description?: string; priority?: string }, idx: number) => (
                              <div key={idx} className="bg-dark-card rounded-lg p-3 border border-dark-border flex items-start gap-2">
                                <span className="text-accent-purple font-mono text-xs mt-0.5">{idx + 1}.</span>
                                {typeof rec === 'string' ? (
                                  <p className="text-gray-300 text-sm">{rec}</p>
                                ) : (
                                  <div>
                                    {rec.title && <p className="text-white font-medium text-sm">{rec.title}</p>}
                                    {rec.description && <p className="text-gray-400 text-xs mt-1">{rec.description}</p>}
                                    {rec.priority && (
                                      <span className={`inline-block mt-1 px-1.5 py-0.5 text-xs rounded ${
                                        rec.priority === 'high' ? 'bg-accent-red/20 text-accent-red' :
                                        rec.priority === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                                        'bg-gray-600/20 text-gray-400'
                                      }`}>{rec.priority}</span>
                                    )}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Special handling for signals (PredictionMarketAnalyst, SportsOddsAnalyst) */}
                      {selectedExecution.output_data.data.signals && Array.isArray(selectedExecution.output_data.data.signals) && selectedExecution.output_data.data.signals.length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-cyan mb-2">Signals ({selectedExecution.output_data.data.signals.length})</h5>
                          <div className="space-y-2">
                            {selectedExecution.output_data.data.signals.slice(0, 10).map((signal: { type?: string; strength?: string; description?: string; market?: string; confidence?: number }, idx: number) => (
                              <div key={idx} className="bg-dark-card rounded-lg p-3 border border-dark-border">
                                <div className="flex items-center justify-between">
                                  <span className="text-white font-medium text-sm">{signal.type || signal.market || `Signal ${idx + 1}`}</span>
                                  {signal.strength && (
                                    <span className={`px-2 py-0.5 text-xs rounded ${
                                      signal.strength === 'strong' ? 'bg-accent-green/20 text-accent-green' :
                                      signal.strength === 'moderate' ? 'bg-accent-amber/20 text-accent-amber' :
                                      'bg-gray-600/20 text-gray-400'
                                    }`}>{signal.strength}</span>
                                  )}
                                  {signal.confidence !== undefined && (
                                    <span className="text-xs text-gray-500">{((signal.confidence ?? 0) * 100).toFixed(0)}% confidence</span>
                                  )}
                                </div>
                                {signal.description && (
                                  <p className="text-gray-400 text-xs mt-1">{signal.description}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Special handling for analysis object */}
                      {selectedExecution.output_data.data.analysis && typeof selectedExecution.output_data.data.analysis === 'object' && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-amber mb-2">Analysis</h5>
                          <div className="bg-dark-card rounded-lg p-3 border border-dark-border">
                            {(selectedExecution.output_data.data.analysis as { summary?: string }).summary && (
                              <p className="text-gray-300 text-sm mb-2">{(selectedExecution.output_data.data.analysis as { summary: string }).summary}</p>
                            )}
                            {(selectedExecution.output_data.data.analysis as { key_insights?: string[] }).key_insights && (
                              <div className="mt-2">
                                <span className="text-xs text-gray-500 uppercase">Key Insights:</span>
                                <ul className="mt-1 space-y-1">
                                  {((selectedExecution.output_data.data.analysis as { key_insights: string[] }).key_insights).map((insight: string, idx: number) => (
                                    <li key={idx} className="text-xs text-gray-400 flex items-start gap-2">
                                      <span className="text-accent-amber">•</span>
                                      {insight}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {!(selectedExecution.output_data.data.analysis as { summary?: string }).summary && !(selectedExecution.output_data.data.analysis as { key_insights?: string[] }).key_insights && (
                              <pre className="text-xs text-gray-400 overflow-x-auto">
                                {JSON.stringify(selectedExecution.output_data.data.analysis, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Special handling for analysis as string (CompetitorAnalysisAgent, etc.) */}
                      {selectedExecution.output_data.data.analysis && typeof selectedExecution.output_data.data.analysis === 'string' && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-amber mb-2">Analysis</h5>
                          <div className="bg-dark-card rounded-lg p-3 border border-dark-border prose prose-invert prose-sm max-w-none prose-table:text-xs prose-th:text-accent-amber prose-td:border-dark-border">
                            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>{selectedExecution.output_data.data.analysis}</ReactMarkdown>
                          </div>
                        </div>
                      )}

                      {/* Special handling for query string */}
                      {selectedExecution.output_data.data.query && typeof selectedExecution.output_data.data.query === 'string' && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-gray-500 mb-1">Query</h5>
                          <p className="text-gray-300 text-sm bg-dark-card rounded-lg px-3 py-2 border border-dark-border">{selectedExecution.output_data.data.query}</p>
                        </div>
                      )}

                      {/* Special handling for raw_data array (source cards) */}
                      {selectedExecution.output_data.data.raw_data && Array.isArray(selectedExecution.output_data.data.raw_data) && selectedExecution.output_data.data.raw_data.length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-cyan mb-2">Sources ({selectedExecution.output_data.data.raw_data.length})</h5>
                          <div className="space-y-2">
                            {selectedExecution.output_data.data.raw_data.slice(0, 10).map((item: { title?: string; source?: string; url?: string; description?: string; snippet?: string }, idx: number) => (
                              <div key={idx} className="bg-dark-card rounded-lg p-3 border border-dark-border">
                                <div className="flex items-center gap-2 mb-1">
                                  {item.source && (
                                    <span className="text-xs px-1.5 py-0.5 bg-accent-cyan/20 text-accent-cyan rounded">{item.source}</span>
                                  )}
                                  {item.title && (
                                    item.url ? (
                                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-sm text-white font-medium hover:text-accent-cyan truncate">
                                        {item.title}
                                      </a>
                                    ) : (
                                      <span className="text-sm text-white font-medium truncate">{item.title}</span>
                                    )
                                  )}
                                </div>
                                {(item.description || item.snippet) && (
                                  <p className="text-xs text-gray-400 line-clamp-2">{item.description || item.snippet}</p>
                                )}
                                {item.url && !item.title && (
                                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-xs text-accent-cyan hover:underline truncate block">
                                    {item.url}
                                  </a>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Special handling for ThinkingAgent thinking_result */}
                      {selectedExecution.output_data.data.thinking_result && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-purple mb-2">Thinking Process</h5>
                          <div className="bg-dark-card rounded-lg p-3 border border-dark-border">
                            {(selectedExecution.output_data.data.thinking_result as { conclusion?: string }).conclusion && (
                              <p className="text-white font-medium mb-2">{(selectedExecution.output_data.data.thinking_result as { conclusion: string }).conclusion}</p>
                            )}
                            {(selectedExecution.output_data.data.thinking_result as { reasoning?: string }).reasoning && (
                              <p className="text-gray-400 text-sm whitespace-pre-wrap">{(selectedExecution.output_data.data.thinking_result as { reasoning: string }).reasoning}</p>
                            )}
                            {(selectedExecution.output_data.data.thinking_result as { confidence?: number }).confidence !== undefined && (
                              <div className="mt-2 flex items-center gap-2">
                                <span className="text-xs text-gray-500">Confidence:</span>
                                <div className="flex-1 bg-dark-border rounded-full h-2">
                                  <div
                                    className="bg-accent-purple h-2 rounded-full"
                                    style={{ width: `${((selectedExecution.output_data.data.thinking_result as { confidence: number }).confidence) * 100}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-400">
                                  {(((selectedExecution.output_data.data.thinking_result as { confidence: number }).confidence) * 100).toFixed(0)}%
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Special handling for WorkflowAgent suggested_workflow */}
                      {selectedExecution.output_data.data.suggested_workflow && Array.isArray(selectedExecution.output_data.data.suggested_workflow) && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-cyan mb-2">
                            Suggested Workflow
                            {selectedExecution.output_data.data.workflow_type && (
                              <span className="ml-2 px-2 py-0.5 text-xs bg-accent-cyan/20 rounded">{selectedExecution.output_data.data.workflow_type}</span>
                            )}
                          </h5>
                          <div className="space-y-2">
                            {selectedExecution.output_data.data.suggested_workflow.map((step: string | { step?: string; agent?: string; description?: string }, idx: number) => (
                              <div key={idx} className="bg-dark-card rounded-lg p-3 border border-dark-border flex items-start gap-3">
                                <div className="w-6 h-6 rounded-full bg-accent-cyan/20 flex items-center justify-center flex-shrink-0">
                                  <span className="text-accent-cyan text-xs font-medium">{idx + 1}</span>
                                </div>
                                {typeof step === 'string' ? (
                                  <p className="text-gray-300 text-sm">{step}</p>
                                ) : (
                                  <div>
                                    {step.step && <p className="text-white font-medium text-sm">{step.step}</p>}
                                    {step.agent && <span className="text-xs text-accent-purple">{step.agent}</span>}
                                    {step.description && <p className="text-gray-400 text-xs mt-1">{step.description}</p>}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Special handling for debate agents (role, voice_id) */}
                      {selectedExecution.output_data.data.role && selectedExecution.output_data.data.voice_id && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-amber mb-2">Debate Role</h5>
                          <div className="bg-dark-card rounded-lg p-3 border border-dark-border">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-accent-amber/20 flex items-center justify-center">
                                <MessageSquare size={18} className="text-accent-amber" />
                              </div>
                              <div>
                                <p className="text-white font-medium capitalize">{selectedExecution.output_data.data.role}</p>
                                <p className="text-xs text-gray-500">Voice: {selectedExecution.output_data.data.voice_id}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Special handling for SystemIntelligenceAgent stats */}
                      {(selectedExecution.output_data.data.info_count !== undefined ||
                        selectedExecution.output_data.data.warning_count !== undefined ||
                        selectedExecution.output_data.data.critical_count !== undefined) && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-cyan mb-2">System Intelligence Summary</h5>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            {selectedExecution.output_data.data.items_count !== undefined && (
                              <div className="bg-dark-card rounded-lg p-3 border border-dark-border text-center">
                                <p className="text-2xl font-bold text-white">{selectedExecution.output_data.data.items_count}</p>
                                <p className="text-xs text-gray-500">Total Items</p>
                              </div>
                            )}
                            {selectedExecution.output_data.data.info_count !== undefined && (
                              <div className="bg-dark-card rounded-lg p-3 border border-accent-cyan/30 text-center">
                                <p className="text-2xl font-bold text-accent-cyan">{selectedExecution.output_data.data.info_count}</p>
                                <p className="text-xs text-gray-500">Info</p>
                              </div>
                            )}
                            {selectedExecution.output_data.data.warning_count !== undefined && (
                              <div className="bg-dark-card rounded-lg p-3 border border-accent-amber/30 text-center">
                                <p className="text-2xl font-bold text-accent-amber">{selectedExecution.output_data.data.warning_count}</p>
                                <p className="text-xs text-gray-500">Warnings</p>
                              </div>
                            )}
                            {selectedExecution.output_data.data.critical_count !== undefined && (
                              <div className="bg-dark-card rounded-lg p-3 border border-accent-red/30 text-center">
                                <p className="text-2xl font-bold text-accent-red">{selectedExecution.output_data.data.critical_count}</p>
                                <p className="text-xs text-gray-500">Critical</p>
                              </div>
                            )}
                          </div>
                          {selectedExecution.output_data.data.execution_time !== undefined && (
                            <p className="text-xs text-gray-500 mt-2 text-right">
                              Execution time: {(selectedExecution.output_data?.data?.execution_time ?? 0).toFixed(2)}s
                            </p>
                          )}
                        </div>
                      )}

                      {/* Special handling for debate_result from AutonomousContentStudioCoordinator */}
                      {selectedExecution.output_data.data.debate_result && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium text-accent-purple mb-2">Debate Result</h5>
                          <div className="bg-dark-card rounded-lg p-3 border border-dark-border">
                            {(selectedExecution.output_data.data.debate_result as { topic?: string }).topic && (
                              <p className="text-white font-medium mb-2">{(selectedExecution.output_data.data.debate_result as { topic: string }).topic}</p>
                            )}
                            {(selectedExecution.output_data.data.debate_result as { winner?: string }).winner && (
                              <p className="text-accent-green text-sm">Winner: {(selectedExecution.output_data.data.debate_result as { winner: string }).winner}</p>
                            )}
                            {(selectedExecution.output_data.data.debate_result as { summary?: string }).summary && (
                              <p className="text-gray-400 text-sm mt-2">{(selectedExecution.output_data.data.debate_result as { summary: string }).summary}</p>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Raw JSON for remaining data - collapsed by default */}
                      <details className="mt-4">
                        <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-300">View Raw JSON</summary>
                        <pre className="mt-2 text-xs text-gray-400 overflow-x-auto max-h-64 bg-dark-card p-3 rounded-lg">
                          {JSON.stringify(selectedExecution.output_data.data, null, 2)}
                        </pre>
                      </details>
                    </div>
                  )}
                </div>
              )}

              {/* Context Injected Section */}
              {selectedExecution.input_data?.context_injected && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                    <Zap size={14} />
                    Context Injected
                  </h3>
                  <div className="bg-dark-lighter rounded-lg p-4 border border-dark-border">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {Object.entries(selectedExecution.input_data.context_injected).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between text-sm">
                          <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}</span>
                          {typeof value === 'boolean' ? (
                            value ? (
                              <CheckCircle size={16} className="text-accent-green" />
                            ) : (
                              <X size={16} className="text-gray-600" />
                            )
                          ) : (
                            <span className="text-gray-200">{String(value)}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Related Memory Section */}
              {relatedMemory && (
                <div>
                  <h3 className="text-sm font-semibold text-accent-purple mb-2 flex items-center gap-2">
                    <Brain size={14} />
                    Related Memory
                  </h3>
                  <div className="bg-accent-purple/10 rounded-lg p-4 border border-accent-purple/30">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-white">{relatedMemory.title}</span>
                      <span className={cn(
                        'text-xs px-2 py-0.5 rounded',
                        relatedMemory.valence === 'positive' ? 'bg-accent-green/20 text-accent-green' :
                        relatedMemory.valence === 'negative' ? 'bg-accent-red/20 text-accent-red' :
                        'bg-gray-500/20 text-gray-400'
                      )}>
                        {relatedMemory.valence}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 whitespace-pre-wrap">{relatedMemory.content}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                      <span>Type: {relatedMemory.memory_type}</span>
                      <span>Importance: {((relatedMemory.importance_score ?? 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer - Session 761: flex-shrink-0 to always show */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50 flex-shrink-0">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>Execution ID: {selectedExecution.id.substring(0, 8)}...</span>
                {selectedExecution.completed_at && (
                  <span>Completed: {formatTimestamp(selectedExecution.completed_at, 'full')}</span>
                )}
              </div>
              <button
                onClick={() => {
                  setSelectedExecution(null)
                  setRelatedMemory(null)
                }}
                className="px-4 py-2 text-sm bg-dark-card hover:bg-dark-hover rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 761: Generic Activity Detail Modal for items without matching entities */}
      {selectedActivity && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
            {/* Modal Header - flex-shrink-0 */}
            <div className={cn(
              "flex items-start justify-between p-6 border-b border-dark-border flex-shrink-0",
              selectedActivity.type === 'dream' ? "bg-gradient-to-r from-accent-purple/10 to-accent-pink/10" :
              selectedActivity.type === 'conversation' ? "bg-gradient-to-r from-accent-cyan/10 to-accent-blue/10" :
              selectedActivity.type === 'decision' ? "bg-gradient-to-r from-accent-amber/10 to-accent-green/10" :
              selectedActivity.type === 'pilot' ? "bg-gradient-to-r from-accent-green/10 to-accent-cyan/10" :
              "bg-gradient-to-r from-primary-500/10 to-accent-pink/10"
            )}>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{selectedActivity.icon}</span>
                  <span className={cn(
                    'text-xs px-2 py-0.5 rounded capitalize',
                    selectedActivity.type === 'dream' ? 'bg-accent-purple/20 text-accent-purple' :
                    selectedActivity.type === 'conversation' ? 'bg-accent-cyan/20 text-accent-cyan' :
                    selectedActivity.type === 'decision' ? 'bg-accent-amber/20 text-accent-amber' :
                    selectedActivity.type === 'pilot' ? 'bg-accent-green/20 text-accent-green' :
                    'bg-primary-500/20 text-primary-400'
                  )}>
                    {selectedActivity.type}
                  </span>
                </div>
                {/* Session 761: Use full_title if available */}
                <h2 className="text-xl font-bold text-white">{selectedActivity.full_title || selectedActivity.title}</h2>
                <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                  <Clock size={14} />
                  <span>{formatTimestamp(selectedActivity.timestamp, 'full')}</span>
                  {selectedActivity.timestamp_display && (
                    <>
                      <span className="text-gray-600">•</span>
                      <span>{selectedActivity.timestamp_display}</span>
                    </>
                  )}
                </div>
              </div>
              <button
                onClick={() => setSelectedActivity(null)}
                className="p-2 rounded-lg hover:bg-dark-hover transition-colors text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content - flex-1 for proper scrolling */}
            <div className="p-6 overflow-y-auto flex-1 min-h-0 space-y-6">
              {/* Session 761: Full inspiration/subtitle - use full_subtitle if available */}
              {(selectedActivity.full_subtitle || selectedActivity.subtitle) && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Lightbulb size={14} className="text-accent-amber" />
                    {selectedActivity.type === 'dream' ? 'Inspiration' : 'Description'}
                  </h3>
                  <div className="bg-accent-amber/5 border border-accent-amber/20 rounded-lg p-4 text-gray-200 leading-relaxed whitespace-pre-wrap">
                    {selectedActivity.full_subtitle || selectedActivity.subtitle}
                  </div>
                </div>
              )}

              {/* Session 761: Dream content preview */}
              {selectedActivity.type === 'dream' && selectedActivity.content && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <MessageSquare size={14} />
                    Dream Content
                  </h3>
                  <div className="bg-dark-hover rounded-lg p-4 text-gray-200 leading-relaxed whitespace-pre-wrap">
                    {selectedActivity.content}
                  </div>
                </div>
              )}

              {/* Participating Agents */}
              {selectedActivity.agents && selectedActivity.agents.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Users size={14} />
                    Participating Agents
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedActivity.agents.map((agent, idx) => (
                      <span
                        key={idx}
                        className="text-sm px-3 py-1.5 rounded-lg bg-dark-hover text-gray-300 border border-dark-border flex items-center gap-2"
                      >
                        <Bot size={14} className="text-accent-cyan" />
                        {agent}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Single Agent */}
              {selectedActivity.agent_name && !selectedActivity.agents?.length && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Bot size={14} />
                    Agent
                  </h3>
                  <span className="text-sm px-3 py-1.5 rounded-lg bg-dark-hover text-gray-300 border border-dark-border inline-flex items-center gap-2">
                    <Bot size={14} className="text-accent-cyan" />
                    {selectedActivity.agent_name}
                  </span>
                </div>
              )}

              {/* Additional Data */}
              {selectedActivity.data && Object.keys(selectedActivity.data).length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Zap size={14} />
                    Additional Details
                  </h3>
                  <div className="bg-dark-hover rounded-lg p-4">
                    <pre className="text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(selectedActivity.data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Info Note */}
              <div className="p-4 rounded-lg bg-accent-amber/5 border border-accent-amber/20">
                <p className="text-sm text-gray-400">
                  <span className="text-accent-amber font-medium">Note:</span> This activity&apos;s full details were not loaded.
                  The detailed data may have been archived or created before the current session.
                </p>
              </div>
            </div>

            {/* Modal Footer - flex-shrink-0 to always show */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50 flex-shrink-0">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                {selectedActivity.id && (
                  <span>ID: {selectedActivity.id.slice(0, 8)}...</span>
                )}
                <span className="capitalize">{selectedActivity.type}</span>
              </div>
              <button
                onClick={() => setSelectedActivity(null)}
                className="px-4 py-2 text-sm bg-dark-card hover:bg-dark-hover rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session 761: Tool Detail Modal */}
      {selectedTool && (
        <div
          className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedTool(null)}
        >
          <div
            className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header - flex-shrink-0 to always show */}
            <div className="flex items-start justify-between p-6 border-b border-dark-border flex-shrink-0">
              <div className="flex items-center gap-4">
                <div className={cn(
                  "h-14 w-14 rounded-xl flex items-center justify-center",
                  selectedTool.tool_type === 'api' ? 'bg-accent-cyan/20' :
                  selectedTool.tool_type === 'computation' ? 'bg-accent-purple/20' :
                  selectedTool.tool_type === 'data_processing' ? 'bg-accent-blue/20' :
                  selectedTool.tool_type === 'communication' ? 'bg-accent-green/20' :
                  selectedTool.tool_type === 'content_generation' ? 'bg-accent-pink/20' :
                  selectedTool.tool_type === 'analysis' ? 'bg-accent-amber/20' :
                  'bg-gray-500/20'
                )}>
                  {selectedTool.tool_type === 'api' ? <ExternalLink size={28} className="text-accent-cyan" /> :
                   selectedTool.tool_type === 'computation' ? <Cpu size={28} className="text-accent-purple" /> :
                   selectedTool.tool_type === 'data_processing' ? <Database size={28} className="text-accent-blue" /> :
                   selectedTool.tool_type === 'communication' ? <MessageSquare size={28} className="text-accent-green" /> :
                   selectedTool.tool_type === 'content_generation' ? <Sparkles size={28} className="text-accent-pink" /> :
                   selectedTool.tool_type === 'analysis' ? <BarChart3 size={28} className="text-accent-amber" /> :
                   <Wrench size={28} className="text-gray-400" />}
                </div>
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold text-white">{selectedTool.display_name}</h2>
                    <div className={cn(
                      "flex items-center gap-1 text-xs px-2 py-1 rounded",
                      selectedTool.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                    )}>
                      <Power size={12} />
                      {selectedTool.is_active ? 'Active' : 'Inactive'}
                    </div>
                  </div>
                  <p className="text-gray-400 capitalize">{selectedTool.tool_type.replace('_', ' ')} · v{selectedTool.tool_version}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedTool(null)}
                className="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-dark-hover transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body - flex-1 min-h-0 for proper scrolling */}
            <div className="p-6 space-y-6 overflow-y-auto flex-1 min-h-0">
              {/* Description */}
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2">Description</h3>
                <p className="text-gray-300 whitespace-pre-wrap">{selectedTool.description}</p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-dark-hover rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-white">{selectedTool.usage_count.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">Total Uses</p>
                </div>
                <div className="bg-dark-hover rounded-lg p-4 text-center">
                  <p className={cn(
                    "text-2xl font-bold",
                    selectedTool.success_rate >= 0.9 ? 'text-accent-green' :
                    selectedTool.success_rate >= 0.7 ? 'text-accent-amber' : 'text-accent-red'
                  )}>
                    {((selectedTool.success_rate ?? 0) * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500">Success Rate</p>
                </div>
                <div className="bg-dark-hover rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-white">{(selectedTool.avg_response_time_ms ?? 0).toFixed(0)}ms</p>
                  <p className="text-xs text-gray-500">Avg Response Time</p>
                </div>
              </div>

              {/* Endpoint URL */}
              {selectedTool.endpoint_url && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <ExternalLink size={14} />
                    Endpoint URL
                  </h3>
                  <div className="bg-dark-hover rounded-lg p-3">
                    <code className="text-sm text-accent-cyan break-all">{selectedTool.endpoint_url}</code>
                  </div>
                </div>
              )}

              {/* Supported Operations */}
              {selectedTool.supported_operations && selectedTool.supported_operations.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Zap size={14} />
                    Supported Operations ({selectedTool.supported_operations.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedTool.supported_operations.map((op, idx) => (
                      <span key={idx} className="px-3 py-1.5 rounded-lg bg-dark-hover text-gray-300 text-sm border border-dark-border">
                        {op}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Required Permissions */}
              {selectedTool.required_permissions && selectedTool.required_permissions.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Shield size={14} />
                    Required Permissions ({selectedTool.required_permissions.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedTool.required_permissions.map((perm, idx) => (
                      <span key={idx} className="px-3 py-1.5 rounded-lg bg-accent-amber/10 text-accent-amber text-sm border border-accent-amber/20">
                        {perm}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Compatible Agents */}
              {selectedTool.compatible_agent_count !== undefined && selectedTool.compatible_agent_count > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Users size={14} />
                    Compatible Agents
                  </h3>
                  <p className="text-gray-300">{selectedTool.compatible_agent_count} agents can use this tool</p>
                </div>
              )}

              {/* Timestamps */}
              <div className="grid grid-cols-2 gap-4">
                {selectedTool.created_at && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-400 mb-1 flex items-center gap-2">
                      <Calendar size={14} />
                      Created
                    </h3>
                    <p className="text-gray-300 text-sm">{new Date(selectedTool.created_at).toLocaleDateString()}</p>
                  </div>
                )}
                {selectedTool.updated_at && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-400 mb-1 flex items-center gap-2">
                      <RefreshCw size={14} />
                      Last Updated
                    </h3>
                    <p className="text-gray-300 text-sm">{new Date(selectedTool.updated_at).toLocaleDateString()}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer - flex-shrink-0 to always show */}
            <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-hover/50 flex-shrink-0">
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>ID: {selectedTool.id.slice(0, 8)}...</span>
                <span>Name: {selectedTool.name}</span>
              </div>
              <button
                onClick={() => setSelectedTool(null)}
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
