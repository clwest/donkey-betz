import { useState, useEffect } from 'react'
import { Activity, TrendingUp, DollarSign, Zap, Eye, Target, Bot, FileText, Award } from 'lucide-react'
import SpiderDashboard from './components/SpiderDashboard'
import RevenueStream from './components/RevenueStream'
import TrendingContent from './components/TrendingContent'
import LiveOpportunities from './components/LiveOpportunities'
import AgentNetwork from './components/AgentNetwork'
import FreelanceOpportunities from './components/FreelanceOpportunities'
import AgentActivity from './components/AgentActivity'
import RealTimeAgentMonitor from './components/RealTimeAgentMonitor'
import LiveDeliverableViewer from './components/LiveDeliverableViewer'
import CompletedWorkReview from './components/CompletedWorkReview'
import { useWebSocket } from './hooks/useWebSocket'

// Django backend URL
const API_BASE = 'http://localhost:8000'
const WS_BASE = 'ws://localhost:8000'  // Daphne handles both HTTP and WebSocket on same port

function App() {
  const [activeSpiders, setActiveSpiders] = useState(0)
  const [totalRevenue, setTotalRevenue] = useState(0)
  const [activeOpportunities, setActiveOpportunities] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // WebSocket connection for real-time updates
  const { isConnected, lastMessage } = useWebSocket(`${WS_BASE}/ws/spider-updates/`)

  // Process WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.type) {
        case 'spider_update':
          console.log('Spider update:', lastMessage)
          break
        case 'stats_update':
          if (lastMessage.stats) {
            setActiveSpiders(lastMessage.stats.active_spiders || 0)
          }
          break
        case 'revenue_update':
          if (lastMessage.revenue) {
            setTotalRevenue(lastMessage.revenue.total || 0)
          }
          break
        case 'opportunities_update':
          if (lastMessage.opportunities) {
            setActiveOpportunities(lastMessage.opportunities.length || 0)
          }
          break
      }
    }
  }, [lastMessage])

  // Fetch real data from Django backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch spider stats
        const spiderRes = await fetch(`${API_BASE}/api/spider/stats/`)
        if (spiderRes.ok) {
          const spiderData = await spiderRes.json()
          setActiveSpiders(spiderData.active_spiders || 23)
        }

        // Fetch revenue data
        const revenueRes = await fetch(`${API_BASE}/api/revenue/`)
        if (revenueRes.ok) {
          const revenueData = await revenueRes.json()
          setTotalRevenue(revenueData.total_revenue || 0)
        }

        // Fetch opportunities
        const oppRes = await fetch(`${API_BASE}/api/opportunities/live/`)
        if (oppRes.ok) {
          const oppData = await oppRes.json()
          setActiveOpportunities(oppData.count || 0)
        }

        setLoading(false)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to connect to backend')
        // Use fallback data
        setActiveSpiders(23)
        setTotalRevenue(2847.50)
        setActiveOpportunities(7)
        setLoading(false)
      }
    }

    fetchData()

    // Refresh data every 5 seconds
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className="h-8 w-8 text-blue-600 spider-active" />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Spider Army Command Center
                </h1>
              </div>
              <div className="bg-green-900 text-green-400 px-3 py-1 rounded-full text-sm font-medium border border-green-800">
                {activeSpiders} ACTIVE
              </div>
            </div>

            <div className="flex items-center space-x-6">
              {/* WebSocket Status */}
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs ${
                isConnected ? 'bg-green-900 text-green-400 border border-green-700' : 'bg-red-900 text-red-400 border border-red-700'
              }`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
                <span>{isConnected ? 'Live' : 'Disconnected'}</span>
              </div>

              {error && (
                <div className="text-yellow-400 text-sm">
                  ⚠️ {error}
                </div>
              )}
              <div className="text-right">
                <p className="text-sm text-gray-400">Total Revenue</p>
                <p className="text-2xl font-bold text-green-400 revenue-pulse">
                  ${totalRevenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">Active Opportunities</p>
                <p className="text-2xl font-bold text-orange-400">
                  {activeOpportunities}
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <div className="flex items-center space-x-3">
              <Zap className="h-8 w-8 text-yellow-500" />
              <div>
                <p className="text-sm text-gray-400">Sports Betting</p>
                <p className="text-2xl font-bold text-gray-100">7 Spiders</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <div className="flex items-center space-x-3">
              <TrendingUp className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-sm text-gray-400">Trading & Crypto</p>
                <p className="text-2xl font-bold text-gray-100">6 Spiders</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <div className="flex items-center space-x-3">
              <Eye className="h-8 w-8 text-purple-500" />
              <div>
                <p className="text-sm text-gray-400">Content Trends</p>
                <p className="text-2xl font-bold text-gray-100">3 Spiders</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <div className="flex items-center space-x-3">
              <Target className="h-8 w-8 text-blue-500" />
              <div>
                <p className="text-sm text-gray-400">High Value Ops</p>
                <p className="text-2xl font-bold text-gray-100">7 Spiders</p>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SpiderDashboard />
          <RevenueStream />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TrendingContent />
          <LiveOpportunities />
        </div>

        {/* Agent Network Section */}
        <div className="mt-6">
          <AgentNetwork />
        </div>

        {/* Freelance Pipeline Section */}
        <div className="mt-6">
          <FreelanceOpportunities />
        </div>

        {/* Real-Time Agent Monitor - Shows all 152 agents working */}
        <div className="mt-6">
          <div className="bg-gray-800 rounded-lg p-1 border border-gray-700">
            <div className="flex items-center space-x-2 p-4 border-b border-gray-700">
              <Bot className="h-6 w-6 text-blue-500" />
              <h2 className="text-xl font-bold">152 Agent Army - Live Activity Monitor</h2>
              <span className="text-xs bg-green-900 text-green-300 px-2 py-1 rounded">REAL-TIME</span>
            </div>
            <RealTimeAgentMonitor />
          </div>
        </div>

        {/* Live Deliverable Generation Viewer */}
        <div className="mt-6">
          <div className="bg-gray-800 rounded-lg p-1 border border-gray-700">
            <div className="flex items-center space-x-2 p-4 border-b border-gray-700">
              <FileText className="h-6 w-6 text-purple-500" />
              <h2 className="text-xl font-bold">Live Deliverable Generation</h2>
              <span className="text-xs bg-yellow-900 text-yellow-300 px-2 py-1 rounded animate-pulse">GENERATING NOW</span>
            </div>
            <LiveDeliverableViewer />
          </div>
        </div>

        {/* Completed Work Review - Review agent deliverables */}
        <div className="mt-6">
          <div className="bg-gray-800 rounded-lg p-1 border border-gray-700">
            <div className="flex items-center space-x-2 p-4 border-b border-gray-700">
              <Award className="h-6 w-6 text-green-500" />
              <h2 className="text-xl font-bold">Completed Work Review</h2>
              <span className="text-xs bg-green-900 text-green-300 px-2 py-1 rounded">6 PROJECTS COMPLETE</span>
            </div>
            <CompletedWorkReview />
          </div>
        </div>

        {/* Activity Stream */}
        <div className="mt-6">
          <AgentActivity />
        </div>
      </main>
    </div>
  )
}

export default App
