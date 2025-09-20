import { Target, Clock, Zap } from 'lucide-react'

const LiveOpportunities = () => {
  const opportunities = [
    {
      type: 'Sports Arbitrage',
      opportunity: 'Chiefs vs Bills - 2.3% guaranteed profit',
      timeLeft: '4h 23m',
      investment: '$1,000',
      profit: '$23',
      confidence: 'HIGH'
    },
    {
      type: 'Stock Options',
      opportunity: 'NVDA Call $480 - Unusual volume',
      timeLeft: '2 days',
      investment: '$3,250',
      profit: '$500-2000',
      confidence: 'MEDIUM'
    },
    {
      type: 'AI Contract',
      opportunity: 'Healthcare LLM - $75K budget',
      timeLeft: '6 days',
      investment: 'Time',
      profit: '$75,000',
      confidence: 'HIGH'
    },
    {
      type: 'Crypto Signal',
      opportunity: 'ETH Long Setup - Bull flag breakout',
      timeLeft: '12h',
      investment: '$2,000',
      profit: '$400-800',
      confidence: 'MEDIUM'
    }
  ]

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'HIGH': return 'text-green-400 bg-green-500/20'
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-500/20'
      case 'LOW': return 'text-red-400 bg-red-500/20'
      default: return 'text-gray-400 bg-gray-500/20'
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-100 flex items-center space-x-2">
          <Target className="h-6 w-6 text-orange-400" />
          <span>Live Opportunities</span>
        </h3>
        <div className="text-sm text-orange-400">
          {opportunities.length} active
        </div>
      </div>

      <div className="space-y-4">
        {opportunities.map((opp, index) => (
          <div key={index} className="p-4 rounded-lg bg-gray-700 border border-gray-600 hover:bg-gray-600 transition-all">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-sm text-gray-400">{opp.type}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(opp.confidence)}`}>
                    {opp.confidence}
                  </span>
                </div>
                <h4 className="text-gray-100 font-medium">{opp.opportunity}</h4>
              </div>
              <div className="flex items-center space-x-1 text-orange-400">
                <Clock className="h-4 w-4" />
                <span className="text-sm">{opp.timeLeft}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400 mb-1">Investment</p>
                <p className="text-gray-100 font-medium">{opp.investment}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Profit Potential</p>
                <p className="text-green-400 font-medium">{opp.profit}</p>
              </div>
            </div>

            <div className="mt-3 flex space-x-2">
              <button className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 px-4 rounded text-sm font-medium transition-colors">
                View Details
              </button>
              <button className="flex-1 bg-green-600 hover:bg-green-500 text-white py-2 px-4 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1">
                <Zap className="h-4 w-4" />
                <span>Execute</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default LiveOpportunities