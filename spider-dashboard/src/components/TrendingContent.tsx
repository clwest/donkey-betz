import { useState, useEffect } from 'react'
import { TrendingUp, Eye, Heart, Share2, DollarSign } from 'lucide-react'

interface TrendingTopic {
  topic: string
  platform: string
  engagement: string
  viralPotential: 'HIGH' | 'MEDIUM' | 'LOW'
  reach: string
  suggestion: string
  hashtags: string[]
}

const TrendingContent = () => {
  const [trends, setTrends] = useState<TrendingTopic[]>([
    {
      topic: "AI beats humans at creative writing",
      platform: "TikTok",
      engagement: "12.5%",
      viralPotential: "HIGH",
      reach: "500K-2M",
      suggestion: "Demo our AI agents creating content in real-time",
      hashtags: ["#AIwriting", "#creativity", "#future"]
    },
    {
      topic: "Make money while you sleep",
      platform: "YouTube Shorts",
      engagement: "8.9%",
      viralPotential: "MEDIUM",
      reach: "200K-800K",
      suggestion: "Demo our spider system finding opportunities",
      hashtags: ["#passiveincome", "#automation", "#makemoney"]
    },
    {
      topic: "Sports betting secrets pros don't want you to know",
      platform: "TikTok",
      engagement: "15.2%",
      viralPotential: "HIGH",
      reach: "1M-5M",
      suggestion: "Show live arbitrage finds from our spiders",
      hashtags: ["#sportsbetting", "#gambling", "#moneymaking"]
    }
  ])

  const [selectedTrend, setSelectedTrend] = useState<TrendingTopic | null>(null)

  // Simulate trending updates
  useEffect(() => {
    const interval = setInterval(() => {
      setTrends(prev => prev.map(trend => ({
        ...trend,
        engagement: `${(Math.random() * 20 + 5).toFixed(1)}%`
      })))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getPotentialColor = (potential: string) => {
    switch (potential) {
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
          <TrendingUp className="h-6 w-6 text-purple-400" />
          <span>Viral Content Opportunities</span>
        </h3>
        <div className="text-sm text-gray-400">
          Live trends • Updated now
        </div>
      </div>

      <div className="space-y-4">
        {trends.map((trend, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border transition-all cursor-pointer ${
              selectedTrend?.topic === trend.topic
                ? 'border-purple-500 bg-purple-900/30'
                : 'border-gray-300 bg-gray-700 hover:bg-gray-600'
            }`}
            onClick={() => setSelectedTrend(trend)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h4 className="text-gray-100 font-medium mb-1 line-clamp-2">
                  {trend.topic}
                </h4>
                <p className="text-sm text-gray-400 mb-2">
                  Platform: {trend.platform}
                </p>
              </div>

              <span className={`px-2 py-1 rounded text-xs font-medium ${getPotentialColor(trend.viralPotential)}`}>
                {trend.viralPotential}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-3">
              <div className="flex items-center space-x-2">
                <Eye className="h-4 w-4 text-blue-400" />
                <span className="text-sm text-gray-100">{trend.reach}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Heart className="h-4 w-4 text-red-400" />
                <span className="text-sm text-gray-100">{trend.engagement}</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-1 mb-3">
              {trend.hashtags.map((tag, tagIndex) => (
                <span
                  key={tagIndex}
                  className="text-xs bg-blue-900 text-blue-400 px-2 py-1 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>

            <div className="text-sm text-gray-700 bg-gray-100 p-2 rounded">
              <strong>💡 Content Idea:</strong> {trend.suggestion}
            </div>
          </div>
        ))}
      </div>

      {selectedTrend && (
        <div className="mt-6 p-4 bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-lg border border-purple-500/30">
          <h4 className="text-lg font-medium text-gray-100 mb-3 flex items-center space-x-2">
            <Share2 className="h-5 w-5 text-purple-400" />
            <span>Ready-to-Create Content</span>
          </h4>

          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-400 mb-1">Video Title:</p>
              <p className="text-gray-100 font-medium">
                "I Built an AI Army That Finds Me Money 24/7"
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-400 mb-1">Hook:</p>
              <p className="text-gray-100">
                "POV: You discover arbitrage betting with AI"
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-400 mb-1">Call to Action:</p>
              <p className="text-gray-100">
                "Link to waitlist in bio 👆"
              </p>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-gray-300">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-4 w-4 text-green-400" />
                <span className="text-sm text-green-400">User Acquisition Potential: VERY HIGH</span>
              </div>
              <span className="text-sm text-gray-400">Viral Score: 9.2/10</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TrendingContent