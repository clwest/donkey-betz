import { useState, useEffect } from 'react'
import { Activity, Zap, TrendingUp, DollarSign, Bot, Clock, AlertCircle } from 'lucide-react'

interface ActivityItem {
  id: string
  type: 'spider' | 'agent' | 'execution' | 'revenue' | 'alert'
  title: string
  description: string
  timestamp: string
  icon: string
  color: string
  metadata?: {
    spider_name?: string
    agent_name?: string
    amount?: number
    confidence?: number
    action?: string
  }
}

const AgentActivity = () => {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [wsConnected, setWsConnected] = useState(false)
  const [filter, setFilter] = useState<'all' | 'spider' | 'agent' | 'revenue'>('all')

  useEffect(() => {
    // Initialize WebSocket connection for real-time updates
    let ws: WebSocket | null = null

    const connectWebSocket = () => {
      ws = new WebSocket('ws://localhost:8000/ws/activity/')

      ws.onopen = () => {
        console.log('Activity WebSocket connected')
        setWsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleActivityUpdate(data)
        } catch (e) {
          console.error('Error parsing activity data:', e)
        }
      }

      ws.onerror = (error) => {
        console.error('Activity WebSocket error:', error)
        setWsConnected(false)
      }

      ws.onclose = () => {
        console.log('Activity WebSocket disconnected')
        setWsConnected(false)
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000)
      }
    }

    const handleActivityUpdate = (data: any) => {
      const newActivity: ActivityItem = {
        id: `activity-${Date.now()}-${Math.random()}`,
        type: data.type || 'agent',
        title: data.title || 'Activity Update',
        description: data.description || '',
        timestamp: new Date().toLocaleTimeString(),
        icon: getActivityIcon(data.type),
        color: getActivityColor(data.type),
        metadata: data.metadata || {}
      }

      setActivities(prev => [newActivity, ...prev].slice(0, 50)) // Keep last 50 activities
    }

    // Load initial activities
    loadInitialActivities()

    // Connect WebSocket
    connectWebSocket()

    // Generate mock activities for demonstration
    const mockInterval = setInterval(() => {
      generateMockActivity()
    }, 5000)

    return () => {
      if (ws) ws.close()
      clearInterval(mockInterval)
    }
  }, [])

  const loadInitialActivities = async () => {
    try {
      // In production, this would fetch from API
      setLoading(false)

      // Add some initial mock activities
      const initialActivities: ActivityItem[] = [
        {
          id: 'init-1',
          type: 'spider',
          title: 'Sports Odds Spider Active',
          description: 'Collected 5 arbitrage opportunities with 2.3% profit margin',
          timestamp: new Date().toLocaleTimeString(),
          icon: '🕷️',
          color: 'text-blue-400',
          metadata: {
            spider_name: 'sports_odds_1',
            confidence: 0.85
          }
        },
        {
          id: 'init-2',
          type: 'agent',
          title: 'Income Builder Analyzed Opportunity',
          description: 'Senior Developer role at TechCorp - $150k remote',
          timestamp: new Date().toLocaleTimeString(),
          icon: '🤖',
          color: 'text-cyan-400',
          metadata: {
            agent_name: 'income_builder_agent',
            action: 'analyze'
          }
        },
        {
          id: 'init-3',
          type: 'revenue',
          title: 'Revenue Generated',
          description: 'Content creation task completed - $125 earned',
          timestamp: new Date().toLocaleTimeString(),
          icon: '💰',
          color: 'text-green-400',
          metadata: {
            amount: 125
          }
        }
      ]
      setActivities(initialActivities)
    } catch (error) {
      console.error('Error loading activities:', error)
      setLoading(false)
    }
  }

  const generateMockActivity = () => {
    const mockActivities = [
      {
        type: 'spider' as const,
        title: 'Crypto Arbitrage Found',
        description: 'BTC/USDT arbitrage opportunity - 0.8% profit',
        metadata: { spider_name: 'crypto_intel_1', confidence: 0.72 }
      },
      {
        type: 'agent' as const,
        title: 'Content Created',
        description: 'AI Tools productivity guide - trending topic',
        metadata: { agent_name: 'content_creator_agent' }
      },
      {
        type: 'execution' as const,
        title: 'Agent Execution Started',
        description: 'Sports analytics agent processing betting data',
        metadata: { agent_name: 'sports_analytics_agent' }
      },
      {
        type: 'revenue' as const,
        title: 'Quick Apply Success',
        description: 'Application submitted for Data Analyst position',
        metadata: { action: 'quick_apply' }
      }
    ]

    const randomActivity = mockActivities[Math.floor(Math.random() * mockActivities.length)]

    const newActivity: ActivityItem = {
      id: `mock-${Date.now()}`,
      type: randomActivity.type,
      title: randomActivity.title,
      description: randomActivity.description,
      timestamp: new Date().toLocaleTimeString(),
      icon: getActivityIcon(randomActivity.type),
      color: getActivityColor(randomActivity.type),
      metadata: randomActivity.metadata
    }

    setActivities(prev => [newActivity, ...prev].slice(0, 50))
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'spider': return '🕷️'
      case 'agent': return '🤖'
      case 'execution': return '⚡'
      case 'revenue': return '💰'
      case 'alert': return '🚨'
      default: return '📊'
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'spider': return 'text-blue-400'
      case 'agent': return 'text-cyan-400'
      case 'execution': return 'text-yellow-400'
      case 'revenue': return 'text-green-400'
      case 'alert': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const filteredActivities = filter === 'all'
    ? activities
    : activities.filter(a => a.type === filter)

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading activity stream...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-100 flex items-center space-x-2">
          <Activity className="h-6 w-6 text-purple-400" />
          <span>Live Activity Stream</span>
          {wsConnected && (
            <span className="flex items-center space-x-1 text-xs text-green-400 ml-2">
              <Zap className="h-3 w-3" />
              <span>Connected</span>
            </span>
          )}
        </h3>

        {/* Filter Tabs */}
        <div className="flex space-x-2">
          {(['all', 'spider', 'agent', 'revenue'] as const).map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                filter === type
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Activity Feed */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredActivities.map((activity) => (
          <div
            key={activity.id}
            className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-all border border-gray-600"
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{activity.icon}</span>
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className={`font-medium ${activity.color}`}>
                      {activity.title}
                    </h4>
                    <p className="text-sm text-gray-300 mt-1">
                      {activity.description}
                    </p>

                    {/* Metadata badges */}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {activity.metadata?.spider_name && (
                        <span className="text-xs bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded">
                          {activity.metadata.spider_name}
                        </span>
                      )}
                      {activity.metadata?.agent_name && (
                        <span className="text-xs bg-cyan-900/50 text-cyan-400 px-2 py-0.5 rounded">
                          {activity.metadata.agent_name}
                        </span>
                      )}
                      {activity.metadata?.confidence && (
                        <span className="text-xs bg-purple-900/50 text-purple-400 px-2 py-0.5 rounded">
                          {(activity.metadata.confidence * 100).toFixed(0)}% confidence
                        </span>
                      )}
                      {activity.metadata?.amount && (
                        <span className="text-xs bg-green-900/50 text-green-400 px-2 py-0.5 rounded font-medium">
                          ${activity.metadata.amount}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-gray-400 flex items-center">
                    <Clock className="h-3 w-3 mr-1" />
                    {activity.timestamp}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}

        {filteredActivities.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <AlertCircle className="h-8 w-8 mx-auto mb-2" />
            <p>No activities to display</p>
          </div>
        )}
      </div>

      {/* Activity Summary */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-4 gap-3">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {activities.filter(a => a.type === 'spider').length}
            </div>
            <div className="text-xs text-gray-400">Spider Updates</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-cyan-400">
              {activities.filter(a => a.type === 'agent').length}
            </div>
            <div className="text-xs text-gray-400">Agent Actions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">
              {activities.filter(a => a.type === 'execution').length}
            </div>
            <div className="text-xs text-gray-400">Executions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {activities.filter(a => a.type === 'revenue').length}
            </div>
            <div className="text-xs text-gray-400">Revenue Events</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentActivity