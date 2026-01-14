import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { evolutionApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'
import {
  Trophy,
  Star,
  Zap,
  TrendingUp,
  Crown,
  Shield,
  Target,
  Award,
  ChevronRight,
  Search,
  RefreshCw,
  Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
interface AgentEvolution {
  id: string
  agent_id: string
  agent_name: string
  level: number
  xp: number
  xp_to_next_level: number
  total_xp: number
  prestige_level: number
  abilities_unlocked: string[]
  created_at: string
  updated_at: string
}

interface XpGain {
  id: string
  agent_name: string
  xp_amount: number
  reason: string
  recorded_at: string
}

interface Ability {
  id?: string
  ability_code?: string
  name?: string
  ability_name?: string
  description: string
  level_required?: number
  unlock_level?: number
  xp_cost?: number
  ability_type?: string
}

// Level tier colors and names
const LEVEL_TIERS = [
  { max: 5, name: 'Novice', color: 'text-gray-400', bgColor: 'bg-gray-500/20', borderColor: 'border-gray-500/50' },
  { max: 10, name: 'Apprentice', color: 'text-green-400', bgColor: 'bg-green-500/20', borderColor: 'border-green-500/50' },
  { max: 20, name: 'Journeyman', color: 'text-blue-400', bgColor: 'bg-blue-500/20', borderColor: 'border-blue-500/50' },
  { max: 35, name: 'Expert', color: 'text-purple-400', bgColor: 'bg-purple-500/20', borderColor: 'border-purple-500/50' },
  { max: 50, name: 'Master', color: 'text-orange-400', bgColor: 'bg-orange-500/20', borderColor: 'border-orange-500/50' },
  { max: 100, name: 'Grandmaster', color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', borderColor: 'border-yellow-500/50' },
  { max: Infinity, name: 'Legendary', color: 'text-red-400', bgColor: 'bg-red-500/20', borderColor: 'border-red-500/50' },
]

const getTier = (level: number) => {
  return LEVEL_TIERS.find(tier => level <= tier.max) || LEVEL_TIERS[LEVEL_TIERS.length - 1]
}

const PRESTIGE_ICONS = [Crown, Shield, Star, Zap, Target]

export default function EvolutionPage() {
  const [selectedAgent, setSelectedAgent] = useState<AgentEvolution | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'leaderboard' | 'abilities' | 'xp-log'>('leaderboard')

  // Fetch evolution overview
  const { isLoading: loadingOverview, refetch: refetchOverview } = useQuery({
    queryKey: ['evolution-overview'],
    queryFn: async () => {
      const response = await evolutionApi.overview()
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch leaderboard
  const { data: leaderboardData, isLoading: loadingLeaderboard } = useQuery({
    queryKey: ['evolution-leaderboard'],
    queryFn: async () => {
      const response = await evolutionApi.leaderboard(100)  // Session 748: Show all agents
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch abilities
  const { data: abilitiesData, isLoading: loadingAbilities } = useQuery({
    queryKey: ['evolution-abilities'],
    queryFn: async () => {
      const response = await evolutionApi.availableAbilities()
      return response.data
    },
    staleTime: 60000,
  })

  // Fetch recent XP gains
  const { data: xpGainsData, isLoading: loadingXpGains } = useQuery({
    queryKey: ['evolution-xp-gains'],
    queryFn: async () => {
      const response = await evolutionApi.recentXpGains(100)
      return response.data
    },
    staleTime: 30000,
  })

  // Parse leaderboard and other data
  const leaderboard: AgentEvolution[] = leaderboardData?.leaderboard || leaderboardData || []
  const abilities: Ability[] = abilitiesData?.abilities || abilitiesData || []
  const xpGains: XpGain[] = xpGainsData?.xp_gains || xpGainsData || []

  // Filter leaderboard by search
  const filteredLeaderboard = leaderboard.filter((agent) =>
    agent.agent_name?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Calculate stats
  const totalAgents = leaderboard.length
  const totalXp = leaderboard.reduce((sum, a) => sum + (a.total_xp || 0), 0)
  const avgLevel = totalAgents > 0 ? Math.round(leaderboard.reduce((sum, a) => sum + (a.level || 1), 0) / totalAgents) : 1
  const prestigeAgents = leaderboard.filter(a => (a.prestige_level || 0) > 0).length

  // Select first agent on load
  useEffect(() => {
    if (leaderboard.length > 0 && !selectedAgent) {
      setSelectedAgent(leaderboard[0])
    }
  }, [leaderboard, selectedAgent])

  const isLoading = loadingOverview || loadingLeaderboard

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb currentPage="Evolution" />
          <p className="text-sm text-gray-400 mt-1">
            Agent XP, Levels, Abilities & Prestige System
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
              <Trophy className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalAgents}</p>
              <p className="text-xs text-gray-400">Evolving Agents</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/20 rounded-lg">
              <Zap className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalXp.toLocaleString()}</p>
              <p className="text-xs text-gray-400">Total XP Earned</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{avgLevel}</p>
              <p className="text-xs text-gray-400">Average Level</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <Crown className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{prestigeAgents}</p>
              <p className="text-xs text-gray-400">Prestige Agents</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel - Leaderboard */}
        <div className="col-span-2 space-y-4">
          {/* Tabs */}
          <div className="flex items-center gap-2 border-b border-dark-border pb-2">
            <button
              onClick={() => setActiveTab('leaderboard')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'leaderboard'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Trophy size={16} className="inline mr-2" />
              Leaderboard
            </button>
            <button
              onClick={() => setActiveTab('abilities')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'abilities'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Sparkles size={16} className="inline mr-2" />
              Abilities ({abilities.length})
            </button>
            <button
              onClick={() => setActiveTab('xp-log')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'xp-log'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Zap size={16} className="inline mr-2" />
              XP Log ({xpGains.length})
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'leaderboard' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              {/* Search */}
              <div className="p-4 border-b border-dark-border">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search agents..."
                    className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Leaderboard List */}
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingLeaderboard ? (
                  <div className="p-8 text-center text-gray-400">Loading leaderboard...</div>
                ) : filteredLeaderboard.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">No agents found</div>
                ) : (
                  filteredLeaderboard.map((agent, index) => {
                    const tier = getTier(agent.level || 1)
                    const progressPercent = agent.xp_to_next_level > 0
                      ? Math.min(100, ((agent.xp || 0) / agent.xp_to_next_level) * 100)
                      : 100

                    return (
                      <button
                        key={agent.id || agent.agent_id}
                        onClick={() => setSelectedAgent(agent)}
                        className={cn(
                          'w-full p-4 flex items-center gap-4 hover:bg-dark-bg transition-colors text-left',
                          selectedAgent?.agent_id === agent.agent_id && 'bg-dark-bg'
                        )}
                      >
                        {/* Rank */}
                        <div className={cn(
                          'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
                          index === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                          index === 1 ? 'bg-gray-400/20 text-gray-300' :
                          index === 2 ? 'bg-orange-500/20 text-orange-400' :
                          'bg-dark-bg text-gray-500'
                        )}>
                          {index + 1}
                        </div>

                        {/* Agent Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white truncate">{agent.agent_name}</span>
                            {(agent.prestige_level || 0) > 0 && (
                              <div className="flex items-center gap-1">
                                {Array.from({ length: Math.min(agent.prestige_level || 0, 5) }).map((_, i) => {
                                  const Icon = PRESTIGE_ICONS[i] || Star
                                  return <Icon key={i} size={12} className="text-yellow-400" />
                                })}
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={cn('text-xs px-2 py-0.5 rounded', tier.bgColor, tier.color)}>
                              {tier.name}
                            </span>
                            <span className="text-xs text-gray-400">
                              Level {agent.level || 1}
                            </span>
                          </div>
                        </div>

                        {/* XP Progress */}
                        <div className="w-32 text-right">
                          <div className="text-sm font-medium text-white">
                            {(agent.total_xp || 0).toLocaleString()} XP
                          </div>
                          <div className="w-full h-1.5 bg-dark-bg rounded-full mt-1">
                            <div
                              className={cn('h-full rounded-full', tier.bgColor.replace('/20', '/60'))}
                              style={{ width: `${progressPercent}%` }}
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

          {activeTab === 'abilities' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="p-4 border-b border-dark-border">
                <h3 className="font-medium text-white">Available Abilities</h3>
                <p className="text-xs text-gray-400 mt-1">Abilities agents can unlock as they level up</p>
              </div>
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingAbilities ? (
                  <div className="p-8 text-center text-gray-400">Loading abilities...</div>
                ) : abilities.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">No abilities defined yet</div>
                ) : (
                  abilities.map((ability, index) => (
                    <div key={ability.id || ability.ability_code || index} className="p-4 hover:bg-dark-bg">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-purple-500/20 rounded-lg">
                          <Sparkles className="w-4 h-4 text-purple-400" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white">{ability.name || ability.ability_name}</span>
                            {ability.ability_type && (
                              <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
                                {ability.ability_type}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 mt-1">{ability.description}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span>Level {ability.level_required || ability.unlock_level} required</span>
                            {ability.xp_cost && <span>{ability.xp_cost} XP cost</span>}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'xp-log' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="p-4 border-b border-dark-border">
                <h3 className="font-medium text-white">Recent XP Gains</h3>
                <p className="text-xs text-gray-400 mt-1">Activity log of XP earned by agents</p>
              </div>
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingXpGains ? (
                  <div className="p-8 text-center text-gray-400">Loading XP log...</div>
                ) : xpGains.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">No XP gains recorded yet</div>
                ) : (
                  xpGains.map((gain) => (
                    <div key={gain.id} className="p-4 hover:bg-dark-bg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-emerald-500/20 rounded-lg">
                            <Zap className="w-4 h-4 text-emerald-400" />
                          </div>
                          <div>
                            <span className="font-medium text-white">{gain.agent_name}</span>
                            <p className="text-sm text-gray-400 mt-0.5">{gain.reason}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-emerald-400 font-medium">+{gain.xp_amount} XP</span>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {new Date(gain.recorded_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Agent Detail */}
        <div className="space-y-4">
          {selectedAgent ? (
            <>
              {/* Agent Card */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                <div className="text-center">
                  {/* Level Badge */}
                  {(() => {
                    const tier = getTier(selectedAgent.level || 1)
                    return (
                      <div className={cn(
                        'inline-flex items-center justify-center w-20 h-20 rounded-full mb-4',
                        tier.bgColor, tier.borderColor, 'border-2'
                      )}>
                        <div className="text-center">
                          <div className={cn('text-2xl font-bold', tier.color)}>
                            {selectedAgent.level || 1}
                          </div>
                          <div className="text-xs text-gray-400">Level</div>
                        </div>
                      </div>
                    )
                  })()}

                  <h3 className="text-lg font-medium text-white">{selectedAgent.agent_name}</h3>

                  {/* Tier Badge */}
                  {(() => {
                    const tier = getTier(selectedAgent.level || 1)
                    return (
                      <span className={cn('text-sm px-3 py-1 rounded-full mt-2 inline-block', tier.bgColor, tier.color)}>
                        {tier.name}
                      </span>
                    )
                  })()}

                  {/* Prestige */}
                  {(selectedAgent.prestige_level || 0) > 0 && (
                    <div className="flex items-center justify-center gap-1 mt-3">
                      <Crown size={14} className="text-yellow-400" />
                      <span className="text-sm text-yellow-400">
                        Prestige {selectedAgent.prestige_level}
                      </span>
                    </div>
                  )}
                </div>

                {/* XP Progress */}
                <div className="mt-6">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">XP Progress</span>
                    <span className="text-white">
                      {(selectedAgent.xp || 0).toLocaleString()} / {(selectedAgent.xp_to_next_level || 100).toLocaleString()}
                    </span>
                  </div>
                  <div className="w-full h-3 bg-dark-bg rounded-full">
                    {(() => {
                      const tier = getTier(selectedAgent.level || 1)
                      const progress = selectedAgent.xp_to_next_level > 0
                        ? Math.min(100, ((selectedAgent.xp || 0) / selectedAgent.xp_to_next_level) * 100)
                        : 100
                      return (
                        <div
                          className={cn('h-full rounded-full transition-all', tier.bgColor.replace('/20', '/60'))}
                          style={{ width: `${progress}%` }}
                        />
                      )
                    })()}
                  </div>
                  <p className="text-xs text-gray-500 mt-2 text-center">
                    Total: {(selectedAgent.total_xp || 0).toLocaleString()} XP earned
                  </p>
                </div>
              </div>

              {/* Unlocked Abilities */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Award size={16} className="text-purple-400" />
                  Unlocked Abilities
                </h4>
                {(selectedAgent.abilities_unlocked || []).length === 0 ? (
                  <p className="text-sm text-gray-400">No abilities unlocked yet</p>
                ) : (
                  <div className="space-y-2">
                    {(selectedAgent.abilities_unlocked || []).map((ability, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <Sparkles size={14} className="text-purple-400" />
                        <span className="text-gray-300">{ability}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Quick Stats */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3">Quick Stats</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedAgent.level || 1}</div>
                    <div className="text-xs text-gray-400">Level</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedAgent.prestige_level || 0}</div>
                    <div className="text-xs text-gray-400">Prestige</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{(selectedAgent.abilities_unlocked || []).length}</div>
                    <div className="text-xs text-gray-400">Abilities</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">
                      {filteredLeaderboard.findIndex(a => a.agent_id === selectedAgent.agent_id) + 1 || '-'}
                    </div>
                    <div className="text-xs text-gray-400">Rank</div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              <Trophy size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Select an agent to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
