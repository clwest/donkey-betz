import { useState, useEffect } from 'react'
import { Activity, Zap, TrendingUp, DollarSign, Bot, Clock, AlertCircle, X, ChevronRight, Play, Eye, Send } from 'lucide-react'

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
  const [selectedActivity, setSelectedActivity] = useState<ActivityItem | null>(null)

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
          title: '🏀 NBA Arbitrage Alert: 5 Live Opportunities',
          description: 'Lakers/Celtics: +2.3% | Warriors/Nets: +1.8% | Total potential: $1,247 profit | Books: DraftKings↔FanDuel | Act fast!',
          timestamp: new Date().toLocaleTimeString(),
          icon: '🕷️',
          color: 'text-blue-400',
          metadata: {
            spider_name: 'sports_arbitrage_scanner',
            confidence: 0.85,
            total_profit: 1247,
            opportunities: 5,
            best_spread: '2.3%',
            books: 'DraftKings, FanDuel, BetMGM'
          }
        },
        {
          id: 'init-2',
          type: 'agent',
          title: '💼 Perfect Job Match: Senior Python Developer @ AI Unicorn',
          description: 'Remote | $180K + equity | 95% skill match | Company: OpenAI competitor | Applied automatically | Interview request likely',
          timestamp: new Date().toLocaleTimeString(),
          icon: '🤖',
          color: 'text-cyan-400',
          metadata: {
            agent_name: 'income_builder_agent',
            action: 'auto_applied',
            salary: 180000,
            match_score: 0.95,
            company_valuation: '$2.3B',
            response_probability: 0.78
          }
        },
        {
          id: 'init-3',
          type: 'revenue',
          title: '💵 Milestone Payment: E-commerce Dashboard Project',
          description: 'Phase 2 complete: $3,750 received | Client approved all deliverables | Phase 3 approved: $5,000 | Total project: $15K',
          timestamp: new Date().toLocaleTimeString(),
          icon: '💰',
          color: 'text-green-400',
          metadata: {
            amount: 3750,
            project_total: 15000,
            completion: '50%',
            next_milestone: 5000,
            client_satisfaction: '5/5'
          }
        },
        {
          id: 'init-4',
          type: 'execution',
          title: '⚡ Algorithmic Trade: ETH Long Position Opened',
          description: 'Entry: $2,347 | Size: 10 ETH | Stop: $2,285 | Target: $2,520 | Risk/Reward: 1:3 | Confidence: 84%',
          timestamp: new Date().toLocaleTimeString(),
          icon: '⚡',
          color: 'text-yellow-400',
          metadata: {
            agent_name: 'crypto_trading_agent',
            asset: 'ETH/USDT',
            position_size: 23470,
            potential_profit: 1730,
            risk_amount: 620,
            confidence: 0.84
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
        title: '💹 Crypto Arbitrage: BTC/USDT',
        description: 'Binance: $43,521 → Coinbase: $43,867 | Spread: $346 (0.8%) | Volume: $2.3M available | Execute within 3 mins',
        metadata: {
          spider_name: 'crypto_arbitrage_scanner',
          confidence: 0.92,
          profit_potential: 346,
          time_window: '3 mins',
          exchanges: 'Binance → Coinbase',
          volume: '$2.3M'
        }
      },
      {
        type: 'agent' as const,
        title: '📝 Blog Post Generated: "10 AI Tools That Doubled My Productivity"',
        description: '2,500 words | SEO Score: 94/100 | Keywords: 15/15 matched | Est. traffic: 5K visits/month | Ready for client review',
        metadata: {
          agent_name: 'content_creator_agent',
          word_count: 2500,
          seo_score: 94,
          estimated_value: 125,
          client: 'TechStartup Inc.',
          deadline: '2 days remaining'
        }
      },
      {
        type: 'execution' as const,
        title: '⚽ Live Bet Opportunity: Lakers vs Warriors',
        description: 'Q3 Over/Under shifted from 54.5 to 52.5 | Current pace: 58 pts | Win probability: 78% | Recommended stake: $250',
        metadata: {
          agent_name: 'sports_analytics_agent',
          game: 'LAL vs GSW',
          bet_type: 'Over 52.5 Q3',
          confidence: 0.78,
          recommended_stake: 250,
          expected_return: 475
        }
      },
      {
        type: 'revenue' as const,
        title: '💰 Payment Received: Freelance Project #FV-2847',
        description: 'Data Analysis Dashboard - $1,250 received via Stripe | Client: DataCorp | Rating: ⭐⭐⭐⭐⭐ | Follow-up project available',
        metadata: {
          amount: 1250,
          project_id: 'FV-2847',
          client: 'DataCorp',
          payment_method: 'Stripe',
          rating: 5,
          follow_up_value: 3500
        }
      },
      {
        type: 'spider' as const,
        title: '🎯 High-Value Job Alert: Senior Python Developer',
        description: 'Remote | $150K-180K | Match: 94% | Your skills: 12/14 requirements met | 3 applicants so far | Expires in 48 hours',
        metadata: {
          spider_name: 'job_opportunity_hunter',
          salary_range: '$150K-180K',
          match_score: 0.94,
          company: 'AI Startup (Series B)',
          urgency: 'Apply within 48h',
          competition: '3 applicants'
        }
      },
      {
        type: 'agent' as const,
        title: '🎨 NFT Collection Analyzed: "Cosmic Cats"',
        description: 'Floor price trend: +12% (7d) | Volume: 234 ETH | Holders: 1.2K growing | Rarity score identified: #142 undervalued by 40%',
        metadata: {
          agent_name: 'nft_analyzer_agent',
          collection: 'Cosmic Cats',
          floor_change: '+12%',
          volume_eth: 234,
          opportunity: 'Buy #142 - undervalued',
          potential_profit: '40% upside'
        }
      },
      {
        type: 'execution' as const,
        title: '🤖 Automated Trade Executed: TSLA Options',
        description: 'Sold 5x TSLA 250C exp 9/27 @ $4.20 | Collected premium: $2,100 | Delta neutral maintained | P&L today: +$847',
        metadata: {
          agent_name: 'options_trading_agent',
          trade: 'Sold 5x TSLA 250C',
          premium_collected: 2100,
          expiry: '9/27',
          daily_pnl: 847,
          position_delta: 0.02
        }
      },
      {
        type: 'revenue' as const,
        title: '🎓 Course Sale: "Master Python in 30 Days"',
        description: '3 new students enrolled | Revenue: $597 | Total students: 147 | Rating: 4.8★ | Passive income this month: $4,821',
        metadata: {
          amount: 597,
          product: 'Master Python Course',
          total_students: 147,
          monthly_passive: 4821,
          rating: 4.8,
          platform: 'Teachable'
        }
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
            className="bg-gray-700 rounded-lg p-3 hover:bg-gray-600 transition-all border border-gray-600 cursor-pointer"
            onClick={() => setSelectedActivity(activity)}
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

                    {/* Enhanced Metadata Display */}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {/* Primary value indicators */}
                      {activity.metadata?.amount && (
                        <span className="text-xs bg-green-900/50 text-green-400 px-2 py-0.5 rounded font-medium">
                          💰 ${activity.metadata.amount.toLocaleString()}
                        </span>
                      )}
                      {activity.metadata?.profit_potential && (
                        <span className="text-xs bg-emerald-900/50 text-emerald-400 px-2 py-0.5 rounded font-medium">
                          📈 +${activity.metadata.profit_potential}
                        </span>
                      )}
                      {activity.metadata?.salary && (
                        <span className="text-xs bg-indigo-900/50 text-indigo-400 px-2 py-0.5 rounded font-medium">
                          💼 ${(activity.metadata.salary/1000)}K
                        </span>
                      )}
                      {activity.metadata?.daily_pnl && (
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                          activity.metadata.daily_pnl > 0
                            ? 'bg-green-900/50 text-green-400'
                            : 'bg-red-900/50 text-red-400'
                        }`}>
                          {activity.metadata.daily_pnl > 0 ? '📈' : '📉'} ${Math.abs(activity.metadata.daily_pnl)}
                        </span>
                      )}

                      {/* Confidence/Match scores */}
                      {activity.metadata?.confidence && (
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          activity.metadata.confidence > 0.8
                            ? 'bg-green-900/50 text-green-400'
                            : activity.metadata.confidence > 0.6
                            ? 'bg-yellow-900/50 text-yellow-400'
                            : 'bg-orange-900/50 text-orange-400'
                        }`}>
                          🎯 {(activity.metadata.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      {activity.metadata?.match_score && (
                        <span className="text-xs bg-purple-900/50 text-purple-400 px-2 py-0.5 rounded">
                          ✅ {(activity.metadata.match_score * 100).toFixed(0)}% match
                        </span>
                      )}

                      {/* Urgency indicators */}
                      {activity.metadata?.urgency && (
                        <span className="text-xs bg-red-900/50 text-red-400 px-2 py-0.5 rounded animate-pulse">
                          ⏰ {activity.metadata.urgency}
                        </span>
                      )}
                      {activity.metadata?.time_window && (
                        <span className="text-xs bg-orange-900/50 text-orange-400 px-2 py-0.5 rounded">
                          ⏱️ {activity.metadata.time_window}
                        </span>
                      )}

                      {/* Source/Platform badges */}
                      {activity.metadata?.spider_name && (
                        <span className="text-xs bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded">
                          🕷️ {activity.metadata.spider_name}
                        </span>
                      )}
                      {activity.metadata?.agent_name && (
                        <span className="text-xs bg-cyan-900/50 text-cyan-400 px-2 py-0.5 rounded">
                          🤖 {activity.metadata.agent_name}
                        </span>
                      )}
                      {activity.metadata?.platform && (
                        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">
                          {activity.metadata.platform}
                        </span>
                      )}

                      {/* Status indicators */}
                      {activity.metadata?.rating && (
                        <span className="text-xs bg-yellow-900/50 text-yellow-400 px-2 py-0.5 rounded">
                          ⭐ {activity.metadata.rating}/5
                        </span>
                      )}
                      {activity.metadata?.completion && (
                        <span className="text-xs bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded">
                          📊 {activity.metadata.completion}
                        </span>
                      )}
                    </div>

                    {/* Quick Actions */}
                    <div className="flex items-center space-x-2 mt-3">
                      {activity.type === 'spider' && activity.metadata?.profit_potential && (
                        <button className="text-xs bg-green-600/20 hover:bg-green-600/30 text-green-400 px-3 py-1 rounded flex items-center space-x-1 transition-colors">
                          <Play className="h-3 w-3" />
                          <span>Execute Trade</span>
                        </button>
                      )}
                      {activity.type === 'agent' && activity.metadata?.action === 'auto_applied' && (
                        <button className="text-xs bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 px-3 py-1 rounded flex items-center space-x-1 transition-colors">
                          <Eye className="h-3 w-3" />
                          <span>View Application</span>
                        </button>
                      )}
                      {activity.type === 'revenue' && (
                        <button className="text-xs bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 px-3 py-1 rounded flex items-center space-x-1 transition-colors">
                          <Send className="h-3 w-3" />
                          <span>Send Invoice</span>
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedActivity(activity)
                        }}
                        className="text-xs bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 px-3 py-1 rounded flex items-center space-x-1 transition-colors ml-auto"
                      >
                        <span>Details</span>
                        <ChevronRight className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <span className="text-xs text-gray-400 flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {activity.timestamp}
                    </span>
                    {/* Priority Indicator */}
                    {(activity.metadata?.urgency || activity.metadata?.time_window ||
                      (activity.metadata?.confidence && activity.metadata.confidence > 0.85)) && (
                      <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                      </span>
                    )}
                  </div>
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

      {/* Activity Details Modal */}
      {selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg border border-gray-600 p-6 max-w-lg w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-100 flex items-center space-x-2">
                <span className="text-2xl">{selectedActivity.icon}</span>
                <span>Activity Details</span>
              </h3>
              <button
                onClick={() => setSelectedActivity(null)}
                className="text-gray-400 hover:text-gray-100 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400">Title</label>
                <p className={`font-medium ${selectedActivity.color}`}>
                  {selectedActivity.title}
                </p>
              </div>

              <div>
                <label className="text-xs text-gray-400">Description</label>
                <p className="text-gray-300">{selectedActivity.description}</p>
              </div>

              <div>
                <label className="text-xs text-gray-400">Type</label>
                <p className="text-gray-300 capitalize">{selectedActivity.type}</p>
              </div>

              <div>
                <label className="text-xs text-gray-400">Timestamp</label>
                <p className="text-gray-300">{selectedActivity.timestamp}</p>
              </div>

              {selectedActivity.metadata && Object.keys(selectedActivity.metadata).length > 0 && (
                <div>
                  <label className="text-xs text-gray-400">Metadata</label>
                  <div className="mt-2 space-y-2">
                    {Object.entries(selectedActivity.metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-400 capitalize">{key.replace('_', ' ')}:</span>
                        <span className="text-gray-300">
                          {typeof value === 'number' && key === 'amount'
                            ? `$${value}`
                            : typeof value === 'number' && key === 'confidence'
                            ? `${(value * 100).toFixed(0)}%`
                            : value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-4">
                {selectedActivity.type === 'agent' && (
                  <button className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white py-2 px-4 rounded transition-colors">
                    View Agent
                  </button>
                )}
                {selectedActivity.type === 'spider' && (
                  <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors">
                    View Spider Data
                  </button>
                )}
                {selectedActivity.type === 'revenue' && (
                  <button className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors">
                    View Transaction
                  </button>
                )}
                <button
                  onClick={() => setSelectedActivity(null)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 text-gray-300 py-2 px-4 rounded transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentActivity