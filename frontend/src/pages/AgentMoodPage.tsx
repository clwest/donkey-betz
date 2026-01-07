import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { moodApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'
import {
  Smile,
  Meh,
  Frown,
  Zap,
  Heart,
  ThumbsUp,
  AlertCircle,
  Coffee,
  Sparkles,
  Brain,
  Search,
  RefreshCw,
  ChevronRight,
  Clock,
  ListFilter,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
interface AgentMood {
  id: string
  agent_id: string
  agent_name: string
  current_mood: string
  intensity: number
  last_updated: string
  mood_streak: number
  personality_traits?: string[]
}

interface MoodHistoryItem {
  id: string
  mood: string
  intensity: number
  reason: string
  recorded_at: string
}

interface MoodRule {
  id: string
  trigger_type: string
  trigger_value: string
  mood_change: string
  intensity_change: number
  description: string
  is_active: boolean
}

// Mood configuration with icons and colors
const MOOD_CONFIG: Record<string, { icon: typeof Smile; color: string; bgColor: string; label: string }> = {
  happy: { icon: Smile, color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', label: 'Happy' },
  excited: { icon: Zap, color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Excited' },
  content: { icon: ThumbsUp, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Content' },
  neutral: { icon: Meh, color: 'text-gray-400', bgColor: 'bg-gray-500/20', label: 'Neutral' },
  focused: { icon: Brain, color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Focused' },
  tired: { icon: Coffee, color: 'text-amber-400', bgColor: 'bg-amber-500/20', label: 'Tired' },
  frustrated: { icon: AlertCircle, color: 'text-red-400', bgColor: 'bg-red-500/20', label: 'Frustrated' },
  sad: { icon: Frown, color: 'text-indigo-400', bgColor: 'bg-indigo-500/20', label: 'Sad' },
  inspired: { icon: Sparkles, color: 'text-purple-400', bgColor: 'bg-purple-500/20', label: 'Inspired' },
  loving: { icon: Heart, color: 'text-pink-400', bgColor: 'bg-pink-500/20', label: 'Loving' },
}

const getMoodConfig = (mood: string) => {
  return MOOD_CONFIG[mood?.toLowerCase()] || MOOD_CONFIG.neutral
}

const getIntensityLabel = (intensity: number) => {
  if (intensity >= 80) return 'Very Strong'
  if (intensity >= 60) return 'Strong'
  if (intensity >= 40) return 'Moderate'
  if (intensity >= 20) return 'Mild'
  return 'Weak'
}

export default function AgentMoodPage() {
  const [selectedAgent, setSelectedAgent] = useState<AgentMood | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'agents' | 'rules'>('agents')
  const [moodFilter, setMoodFilter] = useState<string>('all')

  // Fetch mood overview
  const { data: overviewData, isLoading: loadingOverview, refetch: refetchOverview } = useQuery({
    queryKey: ['mood-overview'],
    queryFn: async () => {
      const response = await moodApi.overview()
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch mood rules
  const { data: rulesData, isLoading: loadingRules } = useQuery({
    queryKey: ['mood-rules'],
    queryFn: async () => {
      const response = await moodApi.rules()
      return response.data
    },
    staleTime: 60000,
  })

  
  // Fetch selected agent's mood history
  const { data: historyData, isLoading: loadingHistory } = useQuery({
    queryKey: ['mood-history', selectedAgent?.agent_id],
    queryFn: async () => {
      if (!selectedAgent?.agent_id) return null
      const response = await moodApi.moodHistory(selectedAgent.agent_id, 50)
      return response.data
    },
    enabled: !!selectedAgent?.agent_id,
    staleTime: 30000,
  })

  // Parse data
  const agentMoods: AgentMood[] = overviewData?.moods || overviewData?.agents || overviewData || []
  const moodRules: MoodRule[] = rulesData?.rules || rulesData || []
  const moodHistory: MoodHistoryItem[] = historyData?.history || historyData || []

  // Get unique moods for filter
  const uniqueMoods = [...new Set(agentMoods.map(a => a.current_mood?.toLowerCase()))]
    .filter(Boolean)
    .sort()

  // Filter agents
  const filteredAgents = agentMoods.filter(agent => {
    const matchesSearch = agent.agent_name?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesMood = moodFilter === 'all' || agent.current_mood?.toLowerCase() === moodFilter
    return matchesSearch && matchesMood
  })

  // Calculate mood stats
  const moodCounts = agentMoods.reduce((acc, agent) => {
    const mood = agent.current_mood?.toLowerCase() || 'neutral'
    acc[mood] = (acc[mood] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const mostCommonMood = Object.entries(moodCounts)
    .sort((a, b) => b[1] - a[1])[0]?.[0] || 'neutral'

  // Select first agent on load
  useEffect(() => {
    if (agentMoods.length > 0 && !selectedAgent) {
      setSelectedAgent(agentMoods[0])
    }
  }, [agentMoods, selectedAgent])

  const isLoading = loadingOverview

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb currentPage="Agent Mood" />
          <p className="text-sm text-gray-400 mt-1">
            Agent emotional states, personality and mood rules
          </p>
        </div>
        <button
          onClick={() => refetchOverview()}
          className="flex items-center gap-2 px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:text-white hover:bg-dark-bg transition-colors"
        >
          <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Brain className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{agentMoods.length}</p>
              <p className="text-xs text-gray-400">Agents with Moods</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            {(() => {
              const config = getMoodConfig(mostCommonMood)
              const Icon = config.icon
              return (
                <>
                  <div className={cn('p-2 rounded-lg', config.bgColor)}>
                    <Icon className={cn('w-5 h-5', config.color)} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white capitalize">{mostCommonMood}</p>
                    <p className="text-xs text-gray-400">Most Common Mood</p>
                  </div>
                </>
              )
            })()}
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <ThumbsUp className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {agentMoods.filter(a => ['happy', 'excited', 'content', 'inspired'].includes(a.current_mood?.toLowerCase())).length}
              </p>
              <p className="text-xs text-gray-400">Positive Moods</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <ListFilter className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{moodRules.length}</p>
              <p className="text-xs text-gray-400">Mood Rules</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel - Agent List / Rules */}
        <div className="col-span-2 space-y-4">
          {/* Tabs */}
          <div className="flex items-center gap-2 border-b border-dark-border pb-2">
            <button
              onClick={() => setActiveTab('agents')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'agents'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Brain size={16} className="inline mr-2" />
              Agent Moods ({agentMoods.length})
            </button>
            <button
              onClick={() => setActiveTab('rules')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'rules'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <ListFilter size={16} className="inline mr-2" />
              Mood Rules ({moodRules.length})
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'agents' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              {/* Filters */}
              <div className="p-4 border-b border-dark-border flex gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search agents..."
                    className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <select
                  value={moodFilter}
                  onChange={(e) => setMoodFilter(e.target.value)}
                  className="px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="all">All Moods</option>
                  {uniqueMoods.map(mood => (
                    <option key={mood} value={mood} className="capitalize">
                      {getMoodConfig(mood).label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Agent List */}
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingOverview ? (
                  <div className="p-8 text-center text-gray-400">Loading agent moods...</div>
                ) : filteredAgents.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">No agents found</div>
                ) : (
                  filteredAgents.map((agent) => {
                    const config = getMoodConfig(agent.current_mood)
                    const Icon = config.icon

                    return (
                      <button
                        key={agent.id || agent.agent_id}
                        onClick={() => setSelectedAgent(agent)}
                        className={cn(
                          'w-full p-4 flex items-center gap-4 hover:bg-dark-bg transition-colors text-left',
                          selectedAgent?.agent_id === agent.agent_id && 'bg-dark-bg'
                        )}
                      >
                        {/* Mood Icon */}
                        <div className={cn('p-3 rounded-full', config.bgColor)}>
                          <Icon className={cn('w-5 h-5', config.color)} />
                        </div>

                        {/* Agent Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white truncate">{agent.agent_name}</span>
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={cn('text-xs px-2 py-0.5 rounded capitalize', config.bgColor, config.color)}>
                              {config.label}
                            </span>
                            <span className="text-xs text-gray-500">
                              {getIntensityLabel(agent.intensity || 50)} ({agent.intensity || 50}%)
                            </span>
                          </div>
                        </div>

                        {/* Intensity Bar */}
                        <div className="w-24">
                          <div className="w-full h-2 bg-dark-bg rounded-full">
                            <div
                              className={cn('h-full rounded-full', config.bgColor.replace('/20', '/60'))}
                              style={{ width: `${agent.intensity || 50}%` }}
                            />
                          </div>
                        </div>

                        <ChevronRight size={16} className="text-gray-500" />
                      </button>
                    )
                  })
                )}
              </div>
            </div>
          )}

          {activeTab === 'rules' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="p-4 border-b border-dark-border">
                <h3 className="font-medium text-white">Mood Trigger Rules</h3>
                <p className="text-xs text-gray-400 mt-1">Rules that automatically adjust agent moods based on events</p>
              </div>
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingRules ? (
                  <div className="p-8 text-center text-gray-400">Loading mood rules...</div>
                ) : moodRules.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">No mood rules defined yet</div>
                ) : (
                  moodRules.map((rule) => {
                    const moodConfig = getMoodConfig(rule.mood_change)

                    return (
                      <div key={rule.id} className="p-4 hover:bg-dark-bg">
                        <div className="flex items-start gap-3">
                          <div className={cn('p-2 rounded-lg', moodConfig.bgColor)}>
                            {React.createElement(moodConfig.icon, { className: cn('w-4 h-4', moodConfig.color) })}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-white capitalize">
                                {rule.trigger_type}: {rule.trigger_value}
                              </span>
                              {!rule.is_active && (
                                <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400">
                                  Inactive
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-400 mt-1">{rule.description}</p>
                            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                              <span className={cn('capitalize', moodConfig.color)}>
                                → {moodConfig.label}
                              </span>
                              <span>
                                Intensity: {rule.intensity_change > 0 ? '+' : ''}{rule.intensity_change}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Agent Detail */}
        <div className="space-y-4">
          {selectedAgent ? (
            <>
              {/* Agent Mood Card */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                {(() => {
                  const config = getMoodConfig(selectedAgent.current_mood)
                  const Icon = config.icon

                  return (
                    <div className="text-center">
                      {/* Mood Badge */}
                      <div className={cn(
                        'inline-flex items-center justify-center w-20 h-20 rounded-full mb-4',
                        config.bgColor, 'border-2', config.bgColor.replace('/20', '/50')
                      )}>
                        <Icon className={cn('w-10 h-10', config.color)} />
                      </div>

                      <h3 className="text-lg font-medium text-white">{selectedAgent.agent_name}</h3>

                      {/* Current Mood */}
                      <span className={cn(
                        'text-sm px-3 py-1 rounded-full mt-2 inline-block capitalize',
                        config.bgColor, config.color
                      )}>
                        {config.label}
                      </span>

                      {/* Intensity */}
                      <div className="mt-4">
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-gray-400">Intensity</span>
                          <span className="text-white">
                            {getIntensityLabel(selectedAgent.intensity || 50)} ({selectedAgent.intensity || 50}%)
                          </span>
                        </div>
                        <div className="w-full h-3 bg-dark-bg rounded-full">
                          <div
                            className={cn('h-full rounded-full transition-all', config.bgColor.replace('/20', '/60'))}
                            style={{ width: `${selectedAgent.intensity || 50}%` }}
                          />
                        </div>
                      </div>

                      {/* Last Updated */}
                      {selectedAgent.last_updated && (
                        <p className="text-xs text-gray-500 mt-4 flex items-center justify-center gap-1">
                          <Clock size={12} />
                          Updated {new Date(selectedAgent.last_updated).toLocaleString()}
                        </p>
                      )}
                    </div>
                  )
                })()}
              </div>

              {/* Personality Traits */}
              {(selectedAgent.personality_traits || []).length > 0 && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                    <Sparkles size={16} className="text-purple-400" />
                    Personality Traits
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {(selectedAgent.personality_traits || []).map((trait, i) => (
                      <span key={i} className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded">
                        {trait}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Mood History */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Clock size={16} className="text-blue-400" />
                  Mood History
                </h4>
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {loadingHistory ? (
                    <p className="text-sm text-gray-400">Loading history...</p>
                  ) : moodHistory.length === 0 ? (
                    <p className="text-sm text-gray-400">No mood history yet</p>
                  ) : (
                    moodHistory.slice(0, 10).map((item) => {
                      const config = getMoodConfig(item.mood)
                      const Icon = config.icon

                      return (
                        <div key={item.id} className="flex items-center gap-3 p-2 rounded hover:bg-dark-bg">
                          <div className={cn('p-1.5 rounded', config.bgColor)}>
                            <Icon className={cn('w-3 h-3', config.color)} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className={cn('text-xs capitalize', config.color)}>
                                {config.label}
                              </span>
                              <span className="text-xs text-gray-500">
                                {item.intensity}%
                              </span>
                            </div>
                            {item.reason && (
                              <p className="text-xs text-gray-400 truncate">{item.reason}</p>
                            )}
                          </div>
                          <span className="text-xs text-gray-600">
                            {new Date(item.recorded_at).toLocaleDateString()}
                          </span>
                        </div>
                      )
                    })
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              <Brain size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Select an agent to view mood details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
