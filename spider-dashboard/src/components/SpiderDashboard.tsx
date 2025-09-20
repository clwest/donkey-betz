import { useState, useEffect } from 'react'
import { Activity, AlertCircle, CheckCircle2, Clock } from 'lucide-react'

interface SpiderStatus {
  name: string
  type: string
  status: 'active' | 'idle' | 'error'
  lastUpdate: string
  dataPoints: number
  revenue: number
}

const SpiderDashboard = () => {
  const [spiders, setSpiders] = useState<SpiderStatus[]>([
    { name: 'sports_odds_1', type: 'sports', status: 'active', lastUpdate: '2s ago', dataPoints: 245, revenue: 1250 },
    { name: 'live_betting_1', type: 'betting', status: 'active', lastUpdate: '5s ago', dataPoints: 189, revenue: 890 },
    { name: 'crypto_intel_1', type: 'crypto', status: 'active', lastUpdate: '1s ago', dataPoints: 156, revenue: 2340 },
    { name: 'trending_content_1', type: 'content', status: 'active', lastUpdate: '3s ago', dataPoints: 78, revenue: 450 },
    { name: 'forex_crypto_1', type: 'trading', status: 'active', lastUpdate: '8s ago', dataPoints: 203, revenue: 1680 },
    { name: 'ai_startup_1', type: 'opportunities', status: 'active', lastUpdate: '12s ago', dataPoints: 34, revenue: 5200 },
    { name: 'prop_betting_1', type: 'betting', status: 'idle', lastUpdate: '45s ago', dataPoints: 67, revenue: 230 },
    { name: 'stock_options_1', type: 'trading', status: 'active', lastUpdate: '6s ago', dataPoints: 123, revenue: 3450 },
  ])

  const [selectedSpider, setSelectedSpider] = useState<SpiderStatus | null>(null)

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSpiders(prev => prev.map(spider => ({
        ...spider,
        dataPoints: spider.dataPoints + Math.floor(Math.random() * 5),
        revenue: spider.revenue + Math.random() * 100,
        lastUpdate: Math.random() > 0.7 ? 'just now' : spider.lastUpdate
      })))
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400'
      case 'idle': return 'text-yellow-400'
      case 'error': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle2 className="h-4 w-4" />
      case 'idle': return <Clock className="h-4 w-4" />
      case 'error': return <AlertCircle className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-100 flex items-center space-x-2">
          <Activity className="h-6 w-6 text-blue-400" />
          <span>Spider Network Status</span>
        </h3>
        <div className="text-sm text-gray-400">
          {spiders.filter(s => s.status === 'active').length} / {spiders.length} active
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {spiders.map((spider, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border transition-all cursor-pointer ${
              selectedSpider?.name === spider.name
                ? 'border-blue-500 bg-blue-900/30'
                : 'border-gray-600 bg-gray-700 hover:bg-gray-600'
            }`}
            onClick={() => setSelectedSpider(spider)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`${getStatusColor(spider.status)} spider-active`}>
                  {getStatusIcon(spider.status)}
                </div>
                <div>
                  <p className="text-gray-100 font-medium">{spider.name}</p>
                  <p className="text-sm text-gray-400 capitalize">{spider.type}</p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-green-400 font-medium">
                  ${spider.revenue.toLocaleString()}
                </p>
                <p className="text-sm text-gray-400">
                  {spider.dataPoints} points
                </p>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between text-sm">
              <span className="text-gray-400">Last update: {spider.lastUpdate}</span>
              <div className="flex space-x-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  spider.status === 'active' ? 'bg-green-900 text-green-400' :
                  spider.status === 'idle' ? 'bg-yellow-900 text-yellow-400' :
                  'bg-red-900 text-red-400'
                }`}>
                  {spider.status.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Progress bar for activity */}
            <div className="mt-2 w-full bg-gray-600 rounded-full h-1">
              <div
                className={`h-1 rounded-full transition-all duration-500 ${
                  spider.status === 'active' ? 'bg-green-500' :
                  spider.status === 'idle' ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${Math.min(100, spider.dataPoints / 3)}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {selectedSpider && (
        <div className="mt-4 p-4 bg-blue-900/30 rounded-lg border border-blue-700">
          <h4 className="text-lg font-medium text-gray-100 mb-2">
            {selectedSpider.name} Details
          </h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-400">Type</p>
              <p className="text-gray-100 capitalize">{selectedSpider.type}</p>
            </div>
            <div>
              <p className="text-gray-400">Revenue</p>
              <p className="text-green-400">${selectedSpider.revenue.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-gray-400">Data Points</p>
              <p className="text-gray-100">{selectedSpider.dataPoints}</p>
            </div>
            <div>
              <p className="text-gray-400">Status</p>
              <p className={getStatusColor(selectedSpider.status)}>
                {selectedSpider.status.toUpperCase()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SpiderDashboard