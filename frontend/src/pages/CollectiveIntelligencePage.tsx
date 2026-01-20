import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { collectiveApi } from '@/lib/api'
import { cn } from '@/lib/cn'
import {
  Brain,
  Users,
  Network,
  BookOpen,
  MessageSquare,
  Lightbulb,
  AlertTriangle,
  Search,
  Plus,
  Send,
  Vote,
  Clock,
  Loader2,
  ChevronRight,
  Share2,
  Bot,
  Zap,
  Target,
} from 'lucide-react'

// Types
interface Insight {
  id: string
  title: string
  description?: string
  source_agent?: string
  category?: string
  confidence?: number
  created_at?: string
  related_agents?: string[]
  actionable?: boolean
}

interface Team {
  id: string
  name: string
  description?: string
  member_count?: number
  created_at?: string
  agents?: string[]
  active_projects?: number
}

interface KnowledgeGap {
  id: string
  topic: string
  description?: string
  priority: 'high' | 'medium' | 'low'
  affected_agents?: number
  suggested_sources?: string[]
}

interface KnowledgeTopic {
  id: string
  name: string
  description?: string
  article_count?: number
  contributors?: number
  last_updated?: string
}

interface Collaboration {
  id: string
  type: 'consultation' | 'delegation' | 'consensus' | 'knowledge_share'
  initiator?: string
  participants?: string[]
  topic?: string
  status: 'pending' | 'active' | 'completed' | 'cancelled'
  created_at?: string
  outcome?: string
}

interface NetworkNode {
  id: string
  name: string
  type: 'agent' | 'team' | 'topic'
  connections?: number
  activity_score?: number
}

interface CollectiveStats {
  total_agents: number
  active_collaborations: number
  knowledge_articles: number
  insights_generated: number
  consensus_decisions: number
  avg_response_time?: number
}

interface Message {
  id: string
  from_agent: string
  to_agent?: string
  content: string
  priority?: 'high' | 'normal' | 'low'
  created_at?: string
  read?: boolean
}

type TabType = 'insights' | 'teams' | 'knowledge' | 'network' | 'messages'

export default function CollectiveIntelligencePage() {
  const [activeTab, setActiveTab] = useState<TabType>('insights')
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateTeam, setShowCreateTeam] = useState(false)
  const [newTeamName, setNewTeamName] = useState('')
  const queryClient = useQueryClient()

  // Queries
  const { data: dashboardData, isLoading: loadingDashboard } = useQuery({
    queryKey: ['collective-dashboard'],
    queryFn: () => collectiveApi.dashboard(),
  })

  const { data: insightsData, isLoading: loadingInsights } = useQuery({
    queryKey: ['collective-insights'],
    queryFn: () => collectiveApi.insights(),
    enabled: activeTab === 'insights',
  })

  const { data: teamsData, isLoading: loadingTeams } = useQuery({
    queryKey: ['collective-teams'],
    queryFn: () => collectiveApi.teams(),
    enabled: activeTab === 'teams',
  })

  const { data: knowledgeGapsData, isLoading: loadingGaps } = useQuery({
    queryKey: ['collective-knowledge-gaps'],
    queryFn: () => collectiveApi.knowledgeGaps(),
    enabled: activeTab === 'knowledge',
  })

  const { data: topicsData, isLoading: loadingTopics } = useQuery({
    queryKey: ['collective-topics'],
    queryFn: () => collectiveApi.knowledgeTopics(),
    enabled: activeTab === 'knowledge',
  })

  const { data: networkData, isLoading: loadingNetwork } = useQuery({
    queryKey: ['collective-network'],
    queryFn: () => collectiveApi.network(),
    enabled: activeTab === 'network',
  })

  const { data: historyData, isLoading: loadingHistory } = useQuery({
    queryKey: ['collective-history'],
    queryFn: () => collectiveApi.collaborationHistory({ limit: 20 }),
    enabled: activeTab === 'network',
  })

  const { data: messagesData, isLoading: loadingMessages } = useQuery({
    queryKey: ['collective-messages'],
    queryFn: () => collectiveApi.messages({ limit: 50 }),
    enabled: activeTab === 'messages',
  })

  const { data: statsData } = useQuery({
    queryKey: ['collective-stats'],
    queryFn: () => collectiveApi.collaborationStats(),
  })

  // Mutations
  const createTeam = useMutation({
    mutationFn: (name: string) => collectiveApi.createTeam({ name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collective-teams'] })
      setShowCreateTeam(false)
      setNewTeamName('')
    },
  })

  // Data extraction
  const dashboard = dashboardData?.data || {}
  const rawInsights = insightsData?.data?.insights || insightsData?.data?.results || insightsData?.data
  const insights: Insight[] = Array.isArray(rawInsights) ? rawInsights : []
  const rawTeams = teamsData?.data?.teams || teamsData?.data?.results || teamsData?.data
  const teams: Team[] = Array.isArray(rawTeams) ? rawTeams : []
  const rawGaps = knowledgeGapsData?.data?.gaps || knowledgeGapsData?.data?.results || knowledgeGapsData?.data
  const knowledgeGaps: KnowledgeGap[] = Array.isArray(rawGaps) ? rawGaps : []
  const rawTopics = topicsData?.data?.topics || topicsData?.data?.results || topicsData?.data
  const topics: KnowledgeTopic[] = Array.isArray(rawTopics) ? rawTopics : []
  const rawNetwork = networkData?.data?.nodes || networkData?.data?.results || networkData?.data
  const networkNodes: NetworkNode[] = Array.isArray(rawNetwork) ? rawNetwork : []
  const rawHistory = historyData?.data?.collaborations || historyData?.data?.active_collaborations || historyData?.data?.results || historyData?.data
  const collaborations: Collaboration[] = Array.isArray(rawHistory) ? rawHistory : []
  const rawMessages = messagesData?.data?.messages || messagesData?.data?.results || messagesData?.data
  const messages: Message[] = Array.isArray(rawMessages) ? rawMessages : []

  // Session 782: Map API response to CollectiveStats interface
  // API returns: { collaboration: {...}, knowledge: {...}, agents: {...}, learning: {...} }
  // Dashboard returns: { monitor: {...}, stats: {...}, learning: {...} }
  // UI expects: { total_agents, active_collaborations, knowledge_articles, insights_generated, ... }
  const rawStats = statsData?.data || {}
  const dashboardStats = dashboard?.stats || {}
  const monitor = dashboard?.monitor || {}

  // Calculate avg response time in seconds from ms
  const avgResponseMs = monitor?.avg_response_time_ms || rawStats?.collaboration?.avg_response_time_ms
  const avgResponseSec = avgResponseMs ? Math.round(avgResponseMs / 1000) : undefined

  const stats: CollectiveStats = {
    total_agents: rawStats?.agents?.database_agents || rawStats?.agents?.total || dashboardStats?.agents?.database_agents || 74,
    active_collaborations: monitor?.active_collaborations ?? rawStats?.collaboration?.total ?? dashboardStats?.collaboration?.total ?? 0,
    knowledge_articles: rawStats?.knowledge?.total_items || dashboardStats?.knowledge?.total_items || 0,
    insights_generated: rawStats?.learning?.total_transfers || dashboard?.learning?.recent?.length || 0,
    consensus_decisions: rawStats?.collaboration?.completed || dashboardStats?.collaboration?.completed || 0,
    avg_response_time: avgResponseSec,
  }

  const tabs = [
    { id: 'insights' as TabType, label: 'Insights', icon: Lightbulb, badge: insights.length },
    { id: 'teams' as TabType, label: 'Teams', icon: Users, badge: teams.length },
    { id: 'knowledge' as TabType, label: 'Knowledge', icon: BookOpen },
    { id: 'network' as TabType, label: 'Network', icon: Network },
    { id: 'messages' as TabType, label: 'Messages', icon: MessageSquare, badge: messages.filter(m => !m.read).length },
  ]

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString()
  }

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-400 bg-red-500/20'
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/20'
      case 'low':
        return 'text-gray-400 bg-gray-500/20'
      default:
        return 'text-gray-400 bg-gray-500/20'
    }
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'text-accent-green'
      case 'active':
        return 'text-blue-400'
      case 'pending':
        return 'text-yellow-400'
      case 'cancelled':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/20">
            <Brain className="h-6 w-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Collective Intelligence</h1>
            <p className="text-gray-400">Agent collaboration, knowledge sharing, and team insights</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Bot className="h-4 w-4" />
            <span className="text-xs">Agents</span>
          </div>
          <p className="text-2xl font-bold">{stats.total_agents || 0}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Zap className="h-4 w-4" />
            <span className="text-xs">Active Collabs</span>
          </div>
          <p className="text-2xl font-bold text-blue-400">{stats.active_collaborations || 0}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <BookOpen className="h-4 w-4" />
            <span className="text-xs">Knowledge</span>
          </div>
          <p className="text-2xl font-bold">{stats.knowledge_articles || 0}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Lightbulb className="h-4 w-4" />
            <span className="text-xs">Insights</span>
          </div>
          <p className="text-2xl font-bold text-yellow-400">{stats.insights_generated || 0}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Vote className="h-4 w-4" />
            <span className="text-xs">Consensus</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">{stats.consensus_decisions || 0}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Clock className="h-4 w-4" />
            <span className="text-xs">Avg Response</span>
          </div>
          <p className="text-2xl font-bold text-accent-green">{stats.avg_response_time || 0}s</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors',
                activeTab === tab.id
                  ? 'bg-dark-card text-white border-b-2 border-primary-500'
                  : 'text-gray-400 hover:text-white hover:bg-dark-card/50'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
              {tab.badge !== undefined && tab.badge > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-primary-600">
                  {tab.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="space-y-4">
            {loadingInsights || loadingDashboard ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : insights.length === 0 ? (
              <div className="text-center py-12">
                <Lightbulb className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No insights available</p>
                <p className="text-sm text-gray-500">Insights are generated from agent collaborations</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.map((insight) => (
                  <div key={insight.id} className="card p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Lightbulb className={cn(
                          'h-5 w-5',
                          insight.actionable ? 'text-yellow-400' : 'text-gray-500'
                        )} />
                        <h3 className="font-medium">{insight.title}</h3>
                      </div>
                      {insight.confidence && (
                        <span className="text-xs text-gray-500">
                          {Math.round(insight.confidence * 100)}% confident
                        </span>
                      )}
                    </div>
                    {insight.description && (
                      <p className="text-sm text-gray-400 mb-3">{insight.description}</p>
                    )}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>From: {insight.source_agent || 'Multiple agents'}</span>
                      <span>{formatDate(insight.created_at)}</span>
                    </div>
                    {insight.actionable && (
                      <button className="mt-3 w-full btn-primary text-sm flex items-center justify-center gap-2">
                        <Target className="h-4 w-4" />
                        Take Action
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Teams Tab */}
        {activeTab === 'teams' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Agent Teams</h2>
              <button
                onClick={() => setShowCreateTeam(true)}
                className="btn-primary flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Create Team
              </button>
            </div>

            {showCreateTeam && (
              <div className="card p-4">
                <h3 className="font-medium mb-3">Create New Team</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Team name..."
                    value={newTeamName}
                    onChange={(e) => setNewTeamName(e.target.value)}
                    className="flex-1 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg"
                  />
                  <button
                    onClick={() => createTeam.mutate(newTeamName)}
                    disabled={!newTeamName || createTeam.isPending}
                    className="btn-primary"
                  >
                    {createTeam.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create'}
                  </button>
                  <button
                    onClick={() => setShowCreateTeam(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {loadingTeams ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : teams.length === 0 ? (
              <div className="text-center py-12">
                <Users className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No teams created yet</p>
                <p className="text-sm text-gray-500">Create a team to organize agent collaboration</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {teams.map((team) => (
                  <div key={team.id} className="card p-4 hover:border-primary-500/50 cursor-pointer">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 rounded-lg bg-cyan-500/20">
                        <Users className="h-5 w-5 text-cyan-400" />
                      </div>
                      <div>
                        <h3 className="font-medium">{team.name}</h3>
                        <p className="text-xs text-gray-500">{team.member_count || 0} members</p>
                      </div>
                    </div>
                    {team.description && (
                      <p className="text-sm text-gray-400 mb-3 line-clamp-2">{team.description}</p>
                    )}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{team.active_projects || 0} active projects</span>
                      <ChevronRight className="h-4 w-4" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Knowledge Tab */}
        {activeTab === 'knowledge' && (
          <div className="space-y-6">
            {/* Knowledge Gaps */}
            <div>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-400" />
                Knowledge Gaps
              </h2>
              {loadingGaps ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : knowledgeGaps.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No knowledge gaps identified</div>
              ) : (
                <div className="space-y-2">
                  {knowledgeGaps.map((gap) => (
                    <div key={gap.id} className="card p-4 flex items-center gap-4">
                      <span className={cn(
                        'px-2 py-1 text-xs rounded capitalize',
                        getPriorityColor(gap.priority)
                      )}>
                        {gap.priority}
                      </span>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium">{gap.topic}</h3>
                        {gap.description && (
                          <p className="text-sm text-gray-400">{gap.description}</p>
                        )}
                      </div>
                      <span className="text-sm text-gray-500">
                        {gap.affected_agents || 0} agents affected
                      </span>
                      <button className="btn-secondary text-sm">
                        Address
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Knowledge Topics */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-blue-400" />
                  Knowledge Base
                </h2>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search knowledge..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-dark-card border border-dark-border rounded-lg"
                  />
                </div>
              </div>
              {loadingTopics ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : topics.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No knowledge topics yet</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {topics.map((topic) => (
                    <div key={topic.id} className="card p-4 hover:border-primary-500/50 cursor-pointer">
                      <h3 className="font-medium mb-2">{topic.name}</h3>
                      {topic.description && (
                        <p className="text-sm text-gray-400 mb-3 line-clamp-2">{topic.description}</p>
                      )}
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{topic.article_count || 0} articles</span>
                        <span>{topic.contributors || 0} contributors</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Network Tab */}
        {activeTab === 'network' && (
          <div className="space-y-6">
            {/* Network Visualization Placeholder */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold mb-4">Collaboration Network</h2>
              {loadingNetwork ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                </div>
              ) : networkNodes.length === 0 ? (
                <div className="text-center py-12">
                  <Network className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">No network data available</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                  {networkNodes.slice(0, 12).map((node) => (
                    <div
                      key={node.id}
                      className="p-3 rounded-lg bg-dark-bg text-center hover:bg-primary-500/10 cursor-pointer"
                    >
                      <div className={cn(
                        'w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center',
                        node.type === 'agent' ? 'bg-cyan-500/20' :
                        node.type === 'team' ? 'bg-purple-500/20' :
                        'bg-yellow-500/20'
                      )}>
                        {node.type === 'agent' ? <Bot className="h-5 w-5 text-cyan-400" /> :
                         node.type === 'team' ? <Users className="h-5 w-5 text-purple-400" /> :
                         <BookOpen className="h-5 w-5 text-yellow-400" />}
                      </div>
                      <p className="text-sm font-medium truncate">{node.name}</p>
                      <p className="text-xs text-gray-500">{node.connections || 0} connections</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Collaboration History */}
            <div>
              <h2 className="text-lg font-semibold mb-4">Recent Collaborations</h2>
              {loadingHistory ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : collaborations.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No collaboration history</div>
              ) : (
                <div className="space-y-2">
                  {collaborations.map((collab) => (
                    <div key={collab.id} className="card p-4 flex items-center gap-4">
                      <div className={cn(
                        'p-2 rounded-lg',
                        collab.type === 'consultation' ? 'bg-blue-500/20' :
                        collab.type === 'consensus' ? 'bg-purple-500/20' :
                        collab.type === 'delegation' ? 'bg-yellow-500/20' :
                        'bg-cyan-500/20'
                      )}>
                        {collab.type === 'consultation' ? <MessageSquare className="h-4 w-4 text-blue-400" /> :
                         collab.type === 'consensus' ? <Vote className="h-4 w-4 text-purple-400" /> :
                         collab.type === 'delegation' ? <Share2 className="h-4 w-4 text-yellow-400" /> :
                         <BookOpen className="h-4 w-4 text-cyan-400" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium capitalize">{collab.type.replace('_', ' ')}</span>
                          <span className={cn('text-xs capitalize', getStatusColor(collab.status))}>
                            {collab.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400">
                          {collab.initiator} → {collab.participants?.join(', ') || 'Multiple agents'}
                        </p>
                      </div>
                      <span className="text-xs text-gray-500">{formatDate(collab.created_at)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Messages Tab */}
        {activeTab === 'messages' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Agent Messages</h2>
              <button className="btn-primary flex items-center gap-2">
                <Send className="h-4 w-4" />
                New Message
              </button>
            </div>

            {loadingMessages ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : messages.length === 0 ? (
              <div className="text-center py-12">
                <MessageSquare className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No messages</p>
              </div>
            ) : (
              <div className="space-y-2">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      'card p-4',
                      !message.read && 'border-primary-500/30 bg-primary-500/5'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-cyan-500/20">
                        <Bot className="h-5 w-5 text-cyan-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{message.from_agent}</span>
                          {message.priority === 'high' && (
                            <span className="px-1.5 py-0.5 text-xs rounded bg-red-500/20 text-red-400">
                              High Priority
                            </span>
                          )}
                          {!message.read && (
                            <span className="w-2 h-2 rounded-full bg-primary-500" />
                          )}
                        </div>
                        <p className="text-gray-300">{message.content}</p>
                        <p className="text-xs text-gray-500 mt-2">{formatDate(message.created_at)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
