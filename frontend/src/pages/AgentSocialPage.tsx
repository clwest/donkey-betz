import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { dreamsApi, conversationsApi, type TimeRange } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'
import {
  Cloud,
  MessageCircle,
  Sparkles,
  Star,
  Heart,
  ThumbsUp,
  Lightbulb,
  Users,
  Clock,
  RefreshCw,
  Play,
  Eye,
  Zap,
  Brain,
  Palette,
  Search,
  ChevronRight,
  ChevronDown,
  Loader2,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Time range options
const TIME_RANGE_OPTIONS: { value: TimeRange; label: string }[] = [
  { value: '24h', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
  { value: 'all', label: 'All Time' },
]

// Types
interface Dream {
  id: string
  agent_id: string
  agent_name: string
  title: string
  content: string
  dream_type: string
  inspiration: string
  related_topics: string[]
  vividness: number
  creativity: number
  shown_to_user: boolean
  user_reaction?: string
  dreamed_at: string
}

// Session 751: Fixed participant type to match API response
interface Participant {
  name: string
  emoji: string
}

interface Conversation {
  id: string
  agent_names?: string[]
  topic: string
  status: string
  messages_count?: number
  message_count?: number  // API returns this field name
  started_at: string  // Session 751: API returns started_at, not created_at
  ended_at?: string | null
  participants?: Participant[]  // API returns {name, emoji} objects
  conclusion?: string
  insights?: string[]
}

// Dream type configuration
const DREAM_TYPE_CONFIG: Record<string, { icon: typeof Cloud; color: string; bgColor: string; label: string }> = {
  creative: { icon: Palette, color: 'text-purple-400', bgColor: 'bg-purple-500/20', label: 'Creative' },
  analytical: { icon: Brain, color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Analytical' },
  predictive: { icon: Zap, color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', label: 'Predictive' },
  reflective: { icon: Eye, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Reflective' },
  exploratory: { icon: Search, color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Exploratory' },
}

const getDreamConfig = (type: string) => {
  return DREAM_TYPE_CONFIG[type?.toLowerCase()] || DREAM_TYPE_CONFIG.creative
}

// Reaction options
const REACTIONS = [
  { value: 'love', icon: Heart, label: 'Love it', color: 'text-red-400' },
  { value: 'insightful', icon: Lightbulb, label: 'Insightful', color: 'text-yellow-400' },
  { value: 'interesting', icon: Star, label: 'Interesting', color: 'text-blue-400' },
  { value: 'like', icon: ThumbsUp, label: 'Like', color: 'text-green-400' },
]

export default function AgentSocialPage() {
  const [activeTab, setActiveTab] = useState<'dreams' | 'conversations'>('dreams')
  const [selectedDream, setSelectedDream] = useState<Dream | null>(null)
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const queryClient = useQueryClient()

  // Dreams pagination state
  const [dreamsTimeRange, setDreamsTimeRange] = useState<TimeRange>('7d')
  const [dreams, setDreams] = useState<Dream[]>([])
  const [dreamsOffset, setDreamsOffset] = useState(0)
  const [loadingMoreDreams, setLoadingMoreDreams] = useState(false)

  // Conversations pagination state
  const [conversationsTimeRange, setConversationsTimeRange] = useState<TimeRange>('7d')
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [conversationsOffset, setConversationsOffset] = useState(0)
  const [loadingMoreConversations, setLoadingMoreConversations] = useState(false)

  const ITEMS_PER_PAGE = 25

  // Fetch dreams with pagination
  const { data: dreamsData, isLoading: loadingDreams, refetch: refetchDreams } = useQuery({
    queryKey: ['agent-dreams', dreamsTimeRange],
    queryFn: async () => {
      const response = await dreamsApi.list({
        limit: ITEMS_PER_PAGE,
        offset: 0,
        timeRange: dreamsTimeRange,
      })
      setDreams(response.data.dreams || [])
      setDreamsOffset(ITEMS_PER_PAGE)
      return response.data
    },
    staleTime: 30000,
  })

  // Load more dreams handler
  const loadMoreDreams = async () => {
    setLoadingMoreDreams(true)
    try {
      const response = await dreamsApi.list({
        limit: ITEMS_PER_PAGE,
        offset: dreamsOffset,
        timeRange: dreamsTimeRange,
      })
      const newDreams = response.data.dreams || []
      setDreams(prev => [...prev, ...newDreams])
      setDreamsOffset(prev => prev + ITEMS_PER_PAGE)
    } finally {
      setLoadingMoreDreams(false)
    }
  }

  // Handle dreams time range change
  const handleDreamsTimeRangeChange = (newRange: TimeRange) => {
    setDreamsTimeRange(newRange)
    setDreams([])
    setDreamsOffset(0)
  }

  // Fetch conversations with pagination
  const { data: conversationsData, isLoading: loadingConversations, refetch: refetchConversations } = useQuery({
    queryKey: ['agent-conversations', conversationsTimeRange],
    queryFn: async () => {
      const response = await conversationsApi.list({
        limit: ITEMS_PER_PAGE,
        offset: 0,
        timeRange: conversationsTimeRange,
      })
      setConversations(response.data.conversations || [])
      setConversationsOffset(ITEMS_PER_PAGE)
      return response.data
    },
    staleTime: 30000,
  })

  // Load more conversations handler
  const loadMoreConversations = async () => {
    setLoadingMoreConversations(true)
    try {
      const response = await conversationsApi.list({
        limit: ITEMS_PER_PAGE,
        offset: conversationsOffset,
        timeRange: conversationsTimeRange,
      })
      const newConversations = response.data.conversations || []
      setConversations(prev => [...prev, ...newConversations])
      setConversationsOffset(prev => prev + ITEMS_PER_PAGE)
    } finally {
      setLoadingMoreConversations(false)
    }
  }

  // Handle conversations time range change
  const handleConversationsTimeRangeChange = (newRange: TimeRange) => {
    setConversationsTimeRange(newRange)
    setConversations([])
    setConversationsOffset(0)
  }

  // Trigger dreams mutation
  const triggerDreamsMutation = useMutation({
    mutationFn: () => dreamsApi.trigger(),
    onSuccess: () => {
      setTimeout(() => refetchDreams(), 2000)
    },
  })

  // Trigger conversation mutation
  const triggerConversationMutation = useMutation({
    mutationFn: () => conversationsApi.trigger(),
    onSuccess: () => {
      setTimeout(() => refetchConversations(), 2000)
    },
  })

  // React to dream mutation
  const reactToDreamMutation = useMutation({
    mutationFn: ({ dreamId, reaction }: { dreamId: string; reaction: string }) =>
      dreamsApi.react(dreamId, reaction),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-dreams'] })
    },
  })

  // Stats - use pagination info from API
  const totalDreams = dreamsData?.total_count || dreams.length
  const unreadDreams = dreamsData?.unread_count || dreams.filter(d => !d.shown_to_user).length
  const hasMoreDreams = dreamsData?.pagination?.has_more || false

  const totalConversations = conversationsData?.total_count || conversations.length
  const activeConversations = conversations.filter(c => c.status === 'active').length
  const hasMoreConversations = conversationsData?.pagination?.has_more || false

  const isLoading = activeTab === 'dreams' ? loadingDreams : loadingConversations

  const handleRefresh = () => {
    if (activeTab === 'dreams') {
      refetchDreams()
    } else {
      refetchConversations()
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb currentPage="Agent Social" />
          <p className="text-sm text-gray-400 mt-1">
            Dreams, conversations, and creative expressions from agents
          </p>
        </div>
        <div className="flex items-center gap-2">
          {activeTab === 'dreams' ? (
            <button
              onClick={() => triggerDreamsMutation.mutate()}
              disabled={triggerDreamsMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm transition-colors disabled:opacity-50"
            >
              <Sparkles size={16} className={triggerDreamsMutation.isPending ? 'animate-spin' : ''} />
              Trigger Dreams
            </button>
          ) : (
            <button
              onClick={() => triggerConversationMutation.mutate()}
              disabled={triggerConversationMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm transition-colors disabled:opacity-50"
            >
              <MessageCircle size={16} className={triggerConversationMutation.isPending ? 'animate-spin' : ''} />
              Start Conversation
            </button>
          )}
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:text-white hover:bg-dark-bg transition-colors"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Cloud className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalDreams.toLocaleString()}</p>
              <p className="text-xs text-gray-400">
                {dreamsTimeRange === '24h' ? 'Dreams Today' :
                 dreamsTimeRange === '7d' ? 'Dreams (7 Days)' :
                 dreamsTimeRange === '30d' ? 'Dreams (30 Days)' :
                 'Total Dreams'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <Sparkles className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{unreadDreams}</p>
              <p className="text-xs text-gray-400">New Dreams</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Play className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{activeConversations}</p>
              <p className="text-xs text-gray-400">Active Conversations</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <MessageCircle className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalConversations.toLocaleString()}</p>
              <p className="text-xs text-gray-400">
                {conversationsTimeRange === '24h' ? 'Conversations Today' :
                 conversationsTimeRange === '7d' ? 'Conversations (7 Days)' :
                 conversationsTimeRange === '30d' ? 'Conversations (30 Days)' :
                 'Total Conversations'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel - List */}
        <div className="col-span-2 space-y-4">
          {/* Tabs with Time Range Selector */}
          <div className="flex items-center justify-between border-b border-dark-border pb-2">
            <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setActiveTab('dreams')
                setSelectedDream(null)
                setSelectedConversation(null)
              }}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'dreams'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Cloud size={16} className="inline mr-2" />
              Dreams ({dreams.length}{totalDreams > dreams.length ? ` of ${totalDreams}` : ''})
            </button>
            <button
              onClick={() => {
                setActiveTab('conversations')
                setSelectedDream(null)
                setSelectedConversation(null)
              }}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'conversations'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <MessageCircle size={16} className="inline mr-2" />
              Conversations ({conversations.length}{totalConversations > conversations.length ? ` of ${totalConversations}` : ''})
            </button>
            </div>

            {/* Time Range Selector - show for both tabs */}
            <div className="relative">
              <select
                value={activeTab === 'dreams' ? dreamsTimeRange : conversationsTimeRange}
                onChange={(e) => activeTab === 'dreams'
                  ? handleDreamsTimeRangeChange(e.target.value as TimeRange)
                  : handleConversationsTimeRangeChange(e.target.value as TimeRange)
                }
                className="appearance-none bg-dark-bg border border-dark-border rounded-lg px-3 py-1.5 pr-8 text-sm text-gray-300 hover:border-gray-500 focus:outline-none focus:border-purple-500 cursor-pointer"
              >
                {TIME_RANGE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <ChevronDown size={14} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {activeTab === 'dreams' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingDreams ? (
                  <div className="p-8 text-center text-gray-400">Loading dreams...</div>
                ) : dreams.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Cloud size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No dreams recorded yet</p>
                    <p className="text-xs mt-2">Click "Trigger Dreams" to generate agent dreams</p>
                  </div>
                ) : (
                  dreams.map((dream) => {
                    const config = getDreamConfig(dream.dream_type)
                    const Icon = config.icon

                    return (
                      <button
                        key={dream.id}
                        onClick={() => {
                          setSelectedDream(dream)
                          setSelectedConversation(null)
                        }}
                        className={cn(
                          'w-full p-4 flex items-start gap-4 hover:bg-dark-bg transition-colors text-left',
                          selectedDream?.id === dream.id && 'bg-dark-bg'
                        )}
                      >
                        <div className={cn('p-3 rounded-full', config.bgColor)}>
                          <Icon className={cn('w-5 h-5', config.color)} />
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white truncate">{dream.title}</span>
                            {!dream.shown_to_user && (
                              <span className="text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400">
                                New
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mt-0.5">by {dream.agent_name}</p>
                          <p className="text-sm text-gray-400 truncate mt-1">
                            {dream.content.substring(0, 100)}...
                          </p>
                          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                            <span className={cn('px-2 py-0.5 rounded', config.bgColor, config.color)}>
                              {config.label}
                            </span>
                            <span className="flex items-center gap-1">
                              <Sparkles size={12} />
                              {Math.round((dream.creativity || 0) * 100)}% creative
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock size={12} />
                              {new Date(dream.dreamed_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>

                        <ChevronRight size={16} className="text-gray-500 mt-2" />
                      </button>
                    )
                  })
                )}
              </div>
              {/* Load More Button */}
              {hasMoreDreams && !loadingDreams && (
                <div className="p-4 border-t border-dark-border">
                  <button
                    onClick={loadMoreDreams}
                    disabled={loadingMoreDreams}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-bg hover:bg-dark-border rounded-lg text-gray-300 hover:text-white transition-colors disabled:opacity-50"
                  >
                    {loadingMoreDreams ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        Loading more...
                      </>
                    ) : (
                      <>
                        <ChevronDown size={16} />
                        Load More Dreams ({totalDreams - dreams.length} remaining)
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'conversations' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingConversations ? (
                  <div className="p-8 text-center text-gray-400">Loading conversations...</div>
                ) : conversations.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <MessageCircle size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No conversations recorded yet</p>
                    <p className="text-xs mt-2">Click "Start Conversation" to trigger agent discussions</p>
                  </div>
                ) : (
                  conversations.map((conversation) => (
                    <button
                      key={conversation.id}
                      onClick={() => {
                        setSelectedConversation(conversation)
                        setSelectedDream(null)
                      }}
                      className={cn(
                        'w-full p-4 flex items-start gap-4 hover:bg-dark-bg transition-colors text-left',
                        selectedConversation?.id === conversation.id && 'bg-dark-bg'
                      )}
                    >
                      <div className={cn(
                        'p-3 rounded-full',
                        conversation.status === 'active' ? 'bg-green-500/20' :
                        conversation.status === 'concluded' ? 'bg-blue-500/20' : 'bg-gray-500/20'
                      )}>
                        <Users className={cn(
                          'w-5 h-5',
                          conversation.status === 'active' ? 'text-green-400' :
                          conversation.status === 'concluded' ? 'text-blue-400' : 'text-gray-400'
                        )} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white truncate">{conversation.topic}</span>
                          {conversation.status === 'active' && (
                            <span className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400">
                              Active
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {/* Session 751: Handle both object {name,emoji} and string participants */}
                          {(conversation.participants || [])
                            .slice(0, 3)
                            .map(p => typeof p === 'string' ? p : p.name)
                            .join(', ') || (conversation.agent_names || []).slice(0, 3).join(', ')}
                          {(conversation.participants || conversation.agent_names || []).length > 3 && ' +more'}
                        </p>
                        {conversation.conclusion && (
                          <p className="text-sm text-gray-400 truncate mt-1">
                            {conversation.conclusion}
                          </p>
                        )}
                        <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                          {(conversation.message_count || conversation.messages_count) && (
                            <span className="flex items-center gap-1">
                              <MessageCircle size={12} />
                              {conversation.message_count || conversation.messages_count} messages
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Clock size={12} />
                            {new Date(conversation.started_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      <ChevronRight size={16} className="text-gray-500 mt-2" />
                    </button>
                  ))
                )}
              </div>
              {/* Load More Button for Conversations */}
              {hasMoreConversations && !loadingConversations && (
                <div className="p-4 border-t border-dark-border">
                  <button
                    onClick={loadMoreConversations}
                    disabled={loadingMoreConversations}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-bg hover:bg-dark-border rounded-lg text-gray-300 hover:text-white transition-colors disabled:opacity-50"
                  >
                    {loadingMoreConversations ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        Loading more...
                      </>
                    ) : (
                      <>
                        <ChevronDown size={16} />
                        Load More Conversations ({totalConversations - conversations.length} remaining)
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Panel - Detail */}
        <div className="space-y-4">
          {selectedDream ? (
            <>
              {/* Dream Detail */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                <div className="text-center">
                  {(() => {
                    const config = getDreamConfig(selectedDream.dream_type)
                    const Icon = config.icon
                    return (
                      <div className={cn('inline-flex items-center justify-center w-16 h-16 rounded-full mb-4', config.bgColor)}>
                        <Icon className={cn('w-8 h-8', config.color)} />
                      </div>
                    )
                  })()}

                  <h3 className="text-lg font-medium text-white">{selectedDream.title}</h3>
                  <p className="text-sm text-gray-400 mt-1">Dreamed by {selectedDream.agent_name}</p>

                  <div className="flex items-center justify-center gap-2 mt-3">
                    <span className={cn(
                      'text-xs px-2 py-0.5 rounded',
                      getDreamConfig(selectedDream.dream_type).bgColor,
                      getDreamConfig(selectedDream.dream_type).color
                    )}>
                      {getDreamConfig(selectedDream.dream_type).label}
                    </span>
                  </div>
                </div>

                {/* Dream Stats */}
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">
                      {Math.round((selectedDream.vividness || 0) * 100)}%
                    </div>
                    <div className="text-xs text-gray-400">Vividness</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">
                      {Math.round((selectedDream.creativity || 0) * 100)}%
                    </div>
                    <div className="text-xs text-gray-400">Creativity</div>
                  </div>
                </div>
              </div>

              {/* Dream Content */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3">Dream Content</h4>
                <p className="text-sm text-gray-300 whitespace-pre-wrap">{selectedDream.content}</p>
              </div>

              {/* Inspiration */}
              {selectedDream.inspiration && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-2 flex items-center gap-2">
                    <Lightbulb size={16} className="text-yellow-400" />
                    Inspiration
                  </h4>
                  <p className="text-sm text-gray-300">{selectedDream.inspiration}</p>
                </div>
              )}

              {/* Related Topics */}
              {(selectedDream.related_topics || []).length > 0 && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-2">Related Topics</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedDream.related_topics.map((topic, i) => (
                      <span key={i} className="text-xs px-2 py-1 rounded bg-dark-bg text-gray-300">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* React to Dream */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3">React to this Dream</h4>
                <div className="grid grid-cols-2 gap-2">
                  {REACTIONS.map((reaction) => (
                    <button
                      key={reaction.value}
                      onClick={() => reactToDreamMutation.mutate({ dreamId: selectedDream.id, reaction: reaction.value })}
                      disabled={reactToDreamMutation.isPending}
                      className={cn(
                        'flex items-center justify-center gap-2 p-2 rounded-lg text-sm transition-colors',
                        selectedDream.user_reaction === reaction.value
                          ? 'bg-purple-500/20 border border-purple-500/50 text-purple-400'
                          : 'bg-dark-bg hover:bg-dark-border/50 text-gray-300'
                      )}
                    >
                      <reaction.icon size={16} className={reaction.color} />
                      {reaction.label}
                    </button>
                  ))}
                </div>
              </div>
            </>
          ) : selectedConversation ? (
            <>
              {/* Conversation Detail */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                <div className="text-center">
                  <div className={cn(
                    'inline-flex items-center justify-center w-16 h-16 rounded-full mb-4',
                    selectedConversation.status === 'active' ? 'bg-green-500/20' : 'bg-blue-500/20'
                  )}>
                    <Users className={cn(
                      'w-8 h-8',
                      selectedConversation.status === 'active' ? 'text-green-400' : 'text-blue-400'
                    )} />
                  </div>

                  <h3 className="text-lg font-medium text-white">{selectedConversation.topic}</h3>

                  <div className="flex items-center justify-center gap-2 mt-2">
                    <span className={cn(
                      'text-xs px-2 py-0.5 rounded',
                      selectedConversation.status === 'active'
                        ? 'bg-green-500/20 text-green-400'
                        : selectedConversation.status === 'concluded'
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'bg-gray-500/20 text-gray-400'
                    )}>
                      {selectedConversation.status}
                    </span>
                  </div>

                  <p className="text-sm text-gray-400 mt-3">
                    {new Date(selectedConversation.started_at).toLocaleString()}
                  </p>
                </div>

                {/* Participants */}
                <div className="mt-6">
                  <h4 className="font-medium text-white mb-2">Participants</h4>
                  <div className="flex flex-wrap gap-2">
                    {/* Session 751: Handle both object {name,emoji} and string participants */}
                    {(selectedConversation.participants || []).map((p, i) => (
                      <span key={i} className="text-xs px-2 py-1 rounded bg-dark-bg text-gray-300">
                        {typeof p === 'string' ? p : `${p.emoji} ${p.name}`}
                      </span>
                    ))}
                    {!selectedConversation.participants?.length && selectedConversation.agent_names?.map((name, i) => (
                      <span key={i} className="text-xs px-2 py-1 rounded bg-dark-bg text-gray-300">
                        {name}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Conclusion */}
              {selectedConversation.conclusion && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-2">Conclusion</h4>
                  <p className="text-sm text-gray-300">{selectedConversation.conclusion}</p>
                </div>
              )}

              {/* Insights */}
              {(selectedConversation.insights || []).length > 0 && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-2 flex items-center gap-2">
                    <Lightbulb size={16} className="text-yellow-400" />
                    Key Insights
                  </h4>
                  <ul className="space-y-2">
                    {selectedConversation.insights?.map((insight, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                        <Star size={14} className="text-yellow-400 mt-0.5 flex-shrink-0" />
                        {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              {activeTab === 'dreams' ? (
                <>
                  <Cloud size={48} className="mx-auto text-gray-600 mb-4" />
                  <p className="text-gray-400">Select a dream to view details</p>
                </>
              ) : (
                <>
                  <MessageCircle size={48} className="mx-auto text-gray-600 mb-4" />
                  <p className="text-gray-400">Select a conversation to view details</p>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
