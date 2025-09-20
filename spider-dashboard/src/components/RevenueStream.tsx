import { DollarSign, TrendingUp } from 'lucide-react'

const RevenueStream = () => {
  const revenueStreams = [
    { source: 'Sports Arbitrage', amount: 2340, growth: '+12.5%', status: 'active' },
    { source: 'Crypto Trading', amount: 1890, growth: '+8.7%', status: 'active' },
    { source: 'Options Trading', amount: 3450, growth: '+15.2%', status: 'active' },
    { source: 'AI Contracts', amount: 5200, growth: '+22.1%', status: 'active' },
    { source: 'Content Creation', amount: 450, growth: '+5.3%', status: 'active' },
  ]

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-100 flex items-center space-x-2">
          <DollarSign className="h-6 w-6 text-green-400" />
          <span>Revenue Streams</span>
        </h3>
        <div className="text-sm text-green-400">
          +18.3% overall
        </div>
      </div>

      <div className="space-y-4">
        {revenueStreams.map((stream, index) => (
          <div key={index} className="p-4 rounded-lg bg-gray-700 border border-gray-600">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-gray-100 font-medium">{stream.source}</h4>
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 text-green-400" />
                <span className="text-green-400 text-sm">{stream.growth}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-green-400">
                ${stream.amount.toLocaleString()}
              </span>
              <span className="text-xs text-gray-400">Last 24h</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RevenueStream