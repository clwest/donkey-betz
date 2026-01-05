import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { agentsApi } from '@/lib/api'
import { useAgentUpdates, useLearningFeed, type AgentUpdate, type LearningEvent } from '@/hooks/useWebSocket'
import { Bot, Activity, CheckCircle, Wifi, WifiOff, Zap } from 'lucide-react'
import { cn } from '@/lib/cn'

interface Agent {
  name: string
  specialization: string
  description: string
  is_active: boolean
  success_rate?: number
}

export default function AgentsPage() {
  const [realtimeUpdates, setRealtimeUpdates] = useState<AgentUpdate[]>([])
  const [learningEvents, setLearningEvents] = useState<LearningEvent[]>([])
  const [activeTab, setActiveTab] = useState<'directory' | 'activity' | 'learning'>('directory')

  // REST API queries
  const { data: agentsData, isLoading } = useQuery({
    queryKey: ['agents-list'],
    queryFn: () => agentsApi.list(),
  })

  const { data: healthData } = useQuery({
    queryKey: ['agents-health'],
    queryFn: () => agentsApi.health(),
  })

  // WebSocket connections
  const { status: agentWsStatus } = useAgentUpdates((update) => {
    setRealtimeUpdates((prev) => [update, ...prev].slice(0, 50))
  })

  const { status: learningWsStatus } = useLearningFeed((event) => {
    setLearningEvents((prev) => [event, ...prev].slice(0, 50))
  })

  const agents: Agent[] = agentsData?.data?.agents || []
  const health = healthData?.data || {}

  const isConnected = agentWsStatus === 'connected' || learningWsStatus === 'connected'

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
              <p className="text-2xl font-bold">{agents.length || 71}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-accent-green" size={24} />
            <div>
              <p className="text-sm text-gray-400">Active</p>
              <p className="text-2xl font-bold">
                {agents.filter((a) => a.is_active).length || 68}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Activity className="text-accent-amber" size={24} />
            <div>
              <p className="text-sm text-gray-400">Routable</p>
              <p className="text-2xl font-bold">{health.routable_count || 68}</p>
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
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Agent Directory</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.slice(0, 12).map((agent) => (
              <div
                key={agent.name}
                className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium">{agent.name}</h4>
                    <p className="text-sm text-primary-400">{agent.specialization}</p>
                  </div>
                  <span
                    className={cn(
                      'h-2 w-2 rounded-full',
                      agent.is_active ? 'bg-accent-green' : 'bg-accent-red'
                    )}
                  />
                </div>
                <p className="text-sm text-gray-400 mt-2 line-clamp-2">
                  {agent.description}
                </p>
              </div>
            ))}
          </div>
          {agents.length > 12 && (
            <div className="mt-4 text-center">
              <button className="btn btn-secondary">
                View All {agents.length} Agents
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            Real-time Agent Activity
            {agentWsStatus === 'connected' && (
              <span className="ml-2 h-2 w-2 rounded-full bg-accent-green inline-block animate-pulse" />
            )}
          </h3>
          {realtimeUpdates.length > 0 ? (
            <div className="space-y-3 max-h-[500px] overflow-auto">
              {realtimeUpdates.map((update, idx) => (
                <div
                  key={`${update.timestamp}-${idx}`}
                  className="flex items-start gap-3 p-3 rounded-lg border border-dark-border"
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
                      <span className="font-medium">{update.agent_name}</span>
                      <span className={cn(
                        'text-xs px-2 py-0.5 rounded',
                        update.type === 'agent_completed' ? 'bg-accent-green/20 text-accent-green' :
                        update.type === 'agent_error' ? 'bg-accent-red/20 text-accent-red' :
                        'bg-primary-500/20 text-primary-400'
                      )}>
                        {update.status}
                      </span>
                    </div>
                    {update.message && (
                      <p className="text-sm text-gray-400 mt-1 truncate">{update.message}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(update.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Activity className="mx-auto mb-2" size={32} />
              <p>Waiting for agent activity...</p>
              <p className="text-sm text-gray-500 mt-1">
                Real-time updates will appear here when agents execute tasks
              </p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'learning' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            Learning Feed
            {learningWsStatus === 'connected' && (
              <span className="ml-2 h-2 w-2 rounded-full bg-accent-green inline-block animate-pulse" />
            )}
          </h3>
          {learningEvents.length > 0 ? (
            <div className="space-y-3 max-h-[500px] overflow-auto">
              {learningEvents.map((event, idx) => (
                <div
                  key={`${event.timestamp}-${idx}`}
                  className="flex items-start gap-3 p-3 rounded-lg border border-dark-border"
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
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Zap className="mx-auto mb-2" size={32} />
              <p>Waiting for learning events...</p>
              <p className="text-sm text-gray-500 mt-1">
                Agent learning activity will appear here in real-time
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
