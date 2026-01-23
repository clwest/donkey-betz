/**
 * AgentCollaborationPage - Production Agent Collaboration Monitor
 * ================================================================
 *
 * Session 794: Real-time monitoring of agent collaborations for all 213 agents
 * (74 core Python + 139 persona) + 25 advisors.
 *
 * Features:
 * - Live collaboration feed (WebSocket)
 * - Agent status indicators (idle/active/collaborating)
 * - Active collaboration cards with progress
 * - Message flow visualization
 * - Statistics dashboard
 * - Agent roster with filtering
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  agentCollaborationApi,
  AgentInfo,
  CollaborationSession,
  InterAgentMessage,
} from '@/lib/api'
import {
  Users, Activity, MessageSquare, Zap, CheckCircle,
  RefreshCw, Search,
  Bot, Crown, ChevronRight, ChevronDown, BarChart3,
  MessageCircle, Wifi, WifiOff, Loader2,
  ArrowRight, User
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'monitor' | 'agents' | 'messages' | 'stats'

// Status colors
const statusColors: Record<string, { bg: string; text: string; dot: string }> = {
  idle: { bg: 'bg-gray-500/20', text: 'text-gray-400', dot: 'bg-gray-400' },
  active: { bg: 'bg-blue-500/20', text: 'text-blue-400', dot: 'bg-blue-400' },
  collaborating: { bg: 'bg-green-500/20', text: 'text-green-400', dot: 'bg-green-400 animate-pulse' },
  available: { bg: 'bg-purple-500/20', text: 'text-purple-400', dot: 'bg-purple-400' },
  pending: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', dot: 'bg-yellow-400' },
  completed: { bg: 'bg-green-500/20', text: 'text-green-400', dot: 'bg-green-400' },
  failed: { bg: 'bg-red-500/20', text: 'text-red-400', dot: 'bg-red-400' },
}

// Agent type icons and colors
const agentTypeConfig: Record<string, { icon: typeof Bot; color: string }> = {
  core: { icon: Bot, color: 'text-blue-400' },
  persona: { icon: User, color: 'text-purple-400' },
  advisor: { icon: Crown, color: 'text-yellow-400' },
}

export default function AgentCollaborationPage() {
  const [activeTab, setActiveTab] = useState<TabType>('monitor')
  const [wsConnected, setWsConnected] = useState(false)
  const [agentFilter, setAgentFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [expandedCollab, setExpandedCollab] = useState<string | null>(null)
  const [liveEvents, setLiveEvents] = useState<Array<{
    type: string
    data: unknown
    timestamp: string
  }>>([])

  const wsRef = useRef<WebSocket | null>(null)
  const queryClient = useQueryClient()

  // Fetch agents
  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ['agent-collab-agents'],
    queryFn: () => agentCollaborationApi.agents(),
    refetchInterval: 30000,
  })

  // Fetch active collaborations
  const { data: activeData, isLoading: activeLoading } = useQuery({
    queryKey: ['agent-collab-active'],
    queryFn: () => agentCollaborationApi.activeCollaborations(),
    refetchInterval: 10000,
  })

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ['agent-collab-stats'],
    queryFn: () => agentCollaborationApi.stats(24),
    refetchInterval: 30000,
  })

  // Fetch recent messages
  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['agent-collab-messages'],
    queryFn: () => agentCollaborationApi.recentMessages(50),
    refetchInterval: 15000,
  })

  // WebSocket connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/agent-collaboration/`

    const connect = () => {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setWsConnected(true)
        console.log('Connected to agent collaboration monitor')
      }

      ws.onclose = () => {
        setWsConnected(false)
        // Reconnect after 5 seconds
        setTimeout(connect, 5000)
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWsMessage(data)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const handleWsMessage = useCallback((data: { type: string; [key: string]: unknown }) => {
    // Add to live events
    setLiveEvents(prev => [{
      type: data.type,
      data,
      timestamp: new Date().toISOString()
    }, ...prev.slice(0, 49)])

    // Invalidate relevant queries based on event type
    if (data.type.startsWith('collaboration:')) {
      queryClient.invalidateQueries({ queryKey: ['agent-collab-active'] })
      queryClient.invalidateQueries({ queryKey: ['agent-collab-stats'] })
    }
    if (data.type === 'message:sent') {
      queryClient.invalidateQueries({ queryKey: ['agent-collab-messages'] })
    }
    if (data.type === 'agent:status_changed') {
      queryClient.invalidateQueries({ queryKey: ['agent-collab-agents'] })
    }
  }, [queryClient])

  // Filter agents
  const filteredAgents = (agentsData?.data?.agents || []).filter(agent => {
    if (agentFilter && !agent.name.toLowerCase().includes(agentFilter.toLowerCase())) {
      return false
    }
    if (typeFilter !== 'all' && agent.type !== typeFilter) {
      return false
    }
    if (statusFilter !== 'all' && agent.status !== statusFilter) {
      return false
    }
    return true
  })

  const counts = agentsData?.data?.counts || { total: 0, core: 0, persona: 0, advisors: 0 }
  const stats = statsData?.data?.stats
  const activeCollabs = activeData?.data?.collaborations || []
  const messages = messagesData?.data?.messages || []

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Users className="w-7 h-7 text-blue-400" />
              Production Agent Collaboration
            </h1>
            <p className="text-gray-400 mt-1">
              Real-time monitoring of {counts.total} agents + {counts.advisors} advisors
            </p>
          </div>
          <div className="flex items-center gap-4">
            {/* WebSocket Status */}
            <div className={cn(
              "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm",
              wsConnected ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
            )}>
              {wsConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              {wsConnected ? 'Live' : 'Reconnecting...'}
            </div>
            {/* Refresh */}
            <button
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['agent-collab-agents'] })
                queryClient.invalidateQueries({ queryKey: ['agent-collab-active'] })
                queryClient.invalidateQueries({ queryKey: ['agent-collab-stats'] })
                queryClient.invalidateQueries({ queryKey: ['agent-collab-messages'] })
              }}
              className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard
          icon={<Users className="w-5 h-5 text-blue-400" />}
          label="Total Agents"
          value={counts.total}
          subtext={`${counts.core} core / ${counts.persona} persona`}
        />
        <StatCard
          icon={<Activity className="w-5 h-5 text-green-400" />}
          label="Active Collaborations"
          value={activeCollabs.length}
          subtext={stats ? `${stats.completed} completed today` : 'Loading...'}
        />
        <StatCard
          icon={<BarChart3 className="w-5 h-5 text-purple-400" />}
          label="Success Rate"
          value={stats ? `${stats.success_rate.toFixed(1)}%` : '-'}
          subtext={stats ? `${stats.total_collaborations} total (24h)` : 'Loading...'}
        />
        <StatCard
          icon={<MessageCircle className="w-5 h-5 text-yellow-400" />}
          label="Messages"
          value={stats?.total_messages || 0}
          subtext="Inter-agent messages (24h)"
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-900/50 p-1 rounded-lg w-fit">
        {(['monitor', 'agents', 'messages', 'stats'] as TabType[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize",
              activeTab === tab
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-800"
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'monitor' && (
        <div className="grid grid-cols-3 gap-6">
          {/* Active Collaborations */}
          <div className="col-span-2">
            <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Active Collaborations
                {activeLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              </h2>
              {activeCollabs.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No active collaborations right now
                </div>
              ) : (
                <div className="space-y-3">
                  {activeCollabs.map(collab => (
                    <CollaborationCard
                      key={collab.id}
                      collab={collab}
                      expanded={expandedCollab === collab.id}
                      onToggle={() => setExpandedCollab(
                        expandedCollab === collab.id ? null : collab.id
                      )}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Live Events Feed */}
          <div>
            <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-400" />
                Live Events
                <span className="text-xs text-gray-500">({liveEvents.length})</span>
              </h2>
              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {liveEvents.length === 0 ? (
                  <div className="text-center py-4 text-gray-500 text-sm">
                    Waiting for events...
                  </div>
                ) : (
                  liveEvents.slice(0, 20).map((event, idx) => (
                    <div
                      key={idx}
                      className="text-xs p-2 rounded bg-gray-800/50 border border-gray-700"
                    >
                      <div className="flex items-center gap-2">
                        <span className={cn(
                          "px-1.5 py-0.5 rounded text-[10px] font-medium",
                          event.type.includes('completed') ? 'bg-green-500/20 text-green-400' :
                          event.type.includes('failed') ? 'bg-red-500/20 text-red-400' :
                          event.type.includes('started') ? 'bg-blue-500/20 text-blue-400' :
                          'bg-gray-500/20 text-gray-400'
                        )}>
                          {event.type.split(':')[1] || event.type}
                        </span>
                        <span className="text-gray-500">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'agents' && (
        <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
          {/* Filters */}
          <div className="flex items-center gap-4 mb-4">
            <div className="relative flex-1 max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search agents..."
                value={agentFilter}
                onChange={(e) => setAgentFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Types</option>
              <option value="core">Core ({counts.core})</option>
              <option value="persona">Persona ({counts.persona})</option>
              <option value="advisor">Advisors ({counts.advisors})</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="idle">Idle</option>
              <option value="active">Active</option>
              <option value="collaborating">Collaborating</option>
            </select>
            <div className="text-sm text-gray-400">
              Showing {filteredAgents.length} of {counts.total}
            </div>
          </div>

          {/* Agent Grid */}
          {agentsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
          ) : (
            <div className="grid grid-cols-4 gap-3 max-h-[600px] overflow-y-auto">
              {filteredAgents.map(agent => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'messages' && (
        <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-400" />
            Recent Inter-Agent Messages
            {messagesLoading && <Loader2 className="w-4 h-4 animate-spin" />}
          </h2>
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {messages.map(msg => (
              <MessageCard key={msg.id} message={msg} />
            ))}
            {messages.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No messages yet
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'stats' && stats && (
        <div className="grid grid-cols-2 gap-6">
          {/* Collaboration Types */}
          <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
            <h2 className="text-lg font-semibold mb-4">By Collaboration Type</h2>
            <div className="space-y-3">
              {Object.entries(stats.by_type || {}).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-gray-300 capitalize">{type}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${(count as number / stats.total_collaborations) * 100}%` }}
                      />
                    </div>
                    <span className="text-gray-400 text-sm w-8 text-right">{count as number}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Most Active Agents */}
          <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
            <h2 className="text-lg font-semibold mb-4">Most Active Agents (24h)</h2>
            <div className="space-y-2">
              {stats.most_active_agents.map((agent, idx) => (
                <div key={agent.name} className="flex items-center gap-3 p-2 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-500 w-6">{idx + 1}.</span>
                  <Bot className="w-4 h-4 text-blue-400" />
                  <span className="flex-1 text-gray-300">{agent.name}</span>
                  <span className="text-blue-400 font-medium">{agent.count} collabs</span>
                </div>
              ))}
              {stats.most_active_agents.length === 0 && (
                <div className="text-center py-4 text-gray-500">
                  No activity in the last 24 hours
                </div>
              )}
            </div>
          </div>

          {/* Summary Stats */}
          <div className="col-span-2 bg-gray-900/50 rounded-xl border border-gray-800 p-4">
            <h2 className="text-lg font-semibold mb-4">24-Hour Summary</h2>
            <div className="grid grid-cols-5 gap-4">
              <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                <div className="text-3xl font-bold text-white">{stats.total_collaborations}</div>
                <div className="text-sm text-gray-400">Total</div>
              </div>
              <div className="text-center p-4 bg-green-500/10 rounded-lg">
                <div className="text-3xl font-bold text-green-400">{stats.completed}</div>
                <div className="text-sm text-gray-400">Completed</div>
              </div>
              <div className="text-center p-4 bg-red-500/10 rounded-lg">
                <div className="text-3xl font-bold text-red-400">{stats.failed}</div>
                <div className="text-sm text-gray-400">Failed</div>
              </div>
              <div className="text-center p-4 bg-yellow-500/10 rounded-lg">
                <div className="text-3xl font-bold text-yellow-400">{stats.active}</div>
                <div className="text-sm text-gray-400">Active</div>
              </div>
              <div className="text-center p-4 bg-purple-500/10 rounded-lg">
                <div className="text-3xl font-bold text-purple-400">{stats.average_quality_score.toFixed(1)}</div>
                <div className="text-sm text-gray-400">Avg Quality</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Sub-components

function StatCard({ icon, label, value, subtext }: {
  icon: React.ReactNode
  label: string
  value: string | number
  subtext: string
}) {
  return (
    <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="text-gray-400 text-sm">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-xs text-gray-500 mt-1">{subtext}</div>
    </div>
  )
}

function AgentCard({ agent }: { agent: AgentInfo }) {
  const config = agentTypeConfig[agent.type] || agentTypeConfig.core
  const status = statusColors[agent.status] || statusColors.idle
  const Icon = config.icon

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 hover:border-gray-600 transition-colors">
      <div className="flex items-start gap-2">
        <Icon className={cn("w-4 h-4 mt-0.5", config.color)} />
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm text-gray-200 truncate">{agent.name}</div>
          <div className="text-xs text-gray-500 truncate">{agent.category}</div>
        </div>
        <div className={cn("w-2 h-2 rounded-full", status.dot)} />
      </div>
      <div className="mt-2 flex items-center justify-between">
        <span className={cn("text-xs px-1.5 py-0.5 rounded", status.bg, status.text)}>
          {agent.status}
        </span>
        <span className="text-xs text-gray-500">
          {agent.effectiveness_score}%
        </span>
      </div>
    </div>
  )
}

function CollaborationCard({ collab, expanded, onToggle }: {
  collab: CollaborationSession
  expanded: boolean
  onToggle: () => void
}) {
  const status = statusColors[collab.status] || statusColors.pending

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full p-3 flex items-center gap-3 hover:bg-gray-800/80 transition-colors"
      >
        <div className={cn("w-2 h-2 rounded-full", status.dot)} />
        <div className="flex-1 text-left">
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-200">{collab.requester_agent}</span>
            <ArrowRight className="w-3 h-3 text-gray-500" />
            <span className="text-gray-400 text-sm">
              {collab.participating_agents.join(', ') || 'No participants'}
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1 truncate">
            {collab.task_description}
          </div>
        </div>
        <span className={cn("text-xs px-2 py-1 rounded", status.bg, status.text)}>
          {collab.collaboration_type}
        </span>
        {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>
      {expanded && (
        <div className="px-3 pb-3 border-t border-gray-700 pt-3">
          <div className="text-xs space-y-1">
            <div className="flex justify-between">
              <span className="text-gray-500">Started:</span>
              <span className="text-gray-300">{new Date(collab.started_at).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Status:</span>
              <span className={status.text}>{collab.status}</span>
            </div>
            {collab.quality_score !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-500">Quality:</span>
                <span className="text-gray-300">{collab.quality_score.toFixed(1)}%</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function MessageCard({ message }: { message: InterAgentMessage }) {
  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <Bot className="w-4 h-4 text-blue-400" />
        <span className="font-medium text-gray-200">{message.from_agent}</span>
        <ArrowRight className="w-3 h-3 text-gray-500" />
        <span className="text-gray-400">{message.to_agent}</span>
        <span className="ml-auto text-xs text-gray-500">
          {new Date(message.created_at).toLocaleTimeString()}
        </span>
      </div>
      <div className="text-sm text-gray-300 truncate">
        {message.content_preview || '(no content)'}
      </div>
      <div className="flex items-center gap-2 mt-2">
        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-400">
          {message.message_type}
        </span>
        <span className="text-xs text-gray-500">Priority: {message.priority}</span>
        {message.is_read && <CheckCircle className="w-3 h-3 text-green-400" />}
      </div>
    </div>
  )
}
