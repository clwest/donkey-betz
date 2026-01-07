import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { relationshipsApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'
import {
  Users,
  Heart,
  Swords,
  Link2,
  Shield,
  Crown,
  Target,
  RefreshCw,
  ChevronRight,
  Sparkles,
  Zap,
  Award,
  UserPlus,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
interface AgentRef {
  id: string
  name: string
}

interface Relationship {
  id: string
  agent_from: AgentRef
  agent_to: AgentRef
  relationship_type: string
  emoji?: string
  strength: number
  trust_level: number
  respect_level: number
  total_interactions: number
  competition_wins: number
  competition_losses: number
  successful_collaborations: number
  failed_collaborations: number
}

interface Alliance {
  id: string
  name: string
  emoji?: string
  purpose: string
  member_count: number
  members: AgentRef[]
  leader?: AgentRef
  combined_strength: number
  success_rate: number
}

interface Rivalry {
  id: string
  challenger_name: string
  defender_name: string
  rivalry_type: string
  intensity: number
  challenger_wins: number
  defender_wins: number
  active_since: string
  current_leader?: string
}

// Relationship type configuration
const RELATIONSHIP_TYPE_CONFIG: Record<string, { icon: typeof Heart; color: string; bgColor: string; label: string }> = {
  ally: { icon: Heart, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Ally' },
  mentor: { icon: Award, color: 'text-purple-400', bgColor: 'bg-purple-500/20', label: 'Mentor' },
  student: { icon: UserPlus, color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Student' },
  collaborator: { icon: Link2, color: 'text-cyan-400', bgColor: 'bg-cyan-500/20', label: 'Collaborator' },
  rival: { icon: Swords, color: 'text-red-400', bgColor: 'bg-red-500/20', label: 'Rival' },
  competitor: { icon: Target, color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Competitor' },
  neutral: { icon: Users, color: 'text-gray-400', bgColor: 'bg-gray-500/20', label: 'Neutral' },
}

const getRelationshipConfig = (type: string) => {
  return RELATIONSHIP_TYPE_CONFIG[type?.toLowerCase()] || RELATIONSHIP_TYPE_CONFIG.neutral
}

// Get initials for avatar
const getInitials = (name: string) => {
  return name.split(/(?=[A-Z])/).map(w => w[0]).join('').substring(0, 2).toUpperCase()
}

export default function RelationshipsPage() {
  const [activeTab, setActiveTab] = useState<'relationships' | 'alliances' | 'rivalries'>('relationships')
  const [selectedRelationship, setSelectedRelationship] = useState<Relationship | null>(null)
  const [selectedAlliance, setSelectedAlliance] = useState<Alliance | null>(null)
  const queryClient = useQueryClient()

  // Fetch relationships overview
  const { data: overviewData, isLoading, refetch } = useQuery({
    queryKey: ['agent-relationships'],
    queryFn: async () => {
      const response = await relationshipsApi.overview()
      return response.data
    },
    staleTime: 30000,
  })

  // Auto-generate mutation
  const autoGenerateMutation = useMutation({
    mutationFn: () => relationshipsApi.autoGenerate(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-relationships'] })
    },
  })

  // Parse data
  const relationships: Relationship[] = Array.isArray(overviewData?.relationships)
    ? overviewData.relationships
    : []
  const alliances: Alliance[] = Array.isArray(overviewData?.alliances)
    ? overviewData.alliances
    : []
  const rivalries: Rivalry[] = Array.isArray(overviewData?.rivalries)
    ? overviewData.rivalries
    : []
  const distribution = overviewData?.relationship_distribution || {}

  // Stats
  const totalRelationships = relationships.length
  const totalAlliances = alliances.length
  const totalRivalries = rivalries.length
  const allyCount = distribution['ally'] || 0
  const rivalCount = distribution['rival'] || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb currentPage="Agent Relationships" />
          <p className="text-sm text-gray-400 mt-1">
            Rivalries, alliances, and bonds between agents
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => autoGenerateMutation.mutate()}
            disabled={autoGenerateMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm transition-colors disabled:opacity-50"
          >
            <Sparkles size={16} className={autoGenerateMutation.isPending ? 'animate-spin' : ''} />
            Generate Relationships
          </button>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:text-white hover:bg-dark-bg transition-colors"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Users className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalRelationships}</p>
              <p className="text-xs text-gray-400">Relationships</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Heart className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{allyCount}</p>
              <p className="text-xs text-gray-400">Allies</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <Swords className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{rivalCount}</p>
              <p className="text-xs text-gray-400">Rivals</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Shield className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalAlliances}</p>
              <p className="text-xs text-gray-400">Alliances</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Zap className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalRivalries}</p>
              <p className="text-xs text-gray-400">Active Rivalries</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel - Lists */}
        <div className="col-span-2 space-y-4">
          {/* Tabs */}
          <div className="flex items-center gap-2 border-b border-dark-border pb-2">
            <button
              onClick={() => {
                setActiveTab('relationships')
                setSelectedRelationship(null)
                setSelectedAlliance(null)
              }}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'relationships'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Link2 size={16} className="inline mr-2" />
              Relationships ({relationships.length})
            </button>
            <button
              onClick={() => {
                setActiveTab('alliances')
                setSelectedRelationship(null)
                setSelectedAlliance(null)
              }}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'alliances'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Shield size={16} className="inline mr-2" />
              Alliances ({alliances.length})
            </button>
            <button
              onClick={() => {
                setActiveTab('rivalries')
                setSelectedRelationship(null)
                setSelectedAlliance(null)
              }}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'rivalries'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Swords size={16} className="inline mr-2" />
              Rivalries ({rivalries.length})
            </button>
          </div>

          {/* Relationships Tab */}
          {activeTab === 'relationships' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {isLoading ? (
                  <div className="p-8 text-center text-gray-400">Loading relationships...</div>
                ) : relationships.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Users size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No relationships found</p>
                    <p className="text-xs mt-2">Click "Generate Relationships" to create agent bonds</p>
                  </div>
                ) : (
                  relationships.map((rel) => {
                    const config = getRelationshipConfig(rel.relationship_type)
                    const Icon = config.icon

                    return (
                      <button
                        key={rel.id}
                        onClick={() => {
                          setSelectedRelationship(rel)
                          setSelectedAlliance(null)
                        }}
                        className={cn(
                          'w-full p-4 flex items-center gap-4 hover:bg-dark-bg transition-colors text-left',
                          selectedRelationship?.id === rel.id && 'bg-dark-bg'
                        )}
                      >
                        {/* Avatars */}
                        <div className="flex -space-x-2">
                          <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center text-sm font-medium text-purple-400 border-2 border-dark-card">
                            {getInitials(rel.agent_from.name)}
                          </div>
                          <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center text-sm font-medium text-blue-400 border-2 border-dark-card">
                            {getInitials(rel.agent_to.name)}
                          </div>
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white truncate">
                              {rel.agent_from.name}
                            </span>
                            <Icon size={14} className={config.color} />
                            <span className="font-medium text-white truncate">
                              {rel.agent_to.name}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                            <span className={cn('px-2 py-0.5 rounded', config.bgColor, config.color)}>
                              {rel.emoji || ''} {config.label}
                            </span>
                            <span>Strength: {rel.strength}%</span>
                            <span>{rel.total_interactions} interactions</span>
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

          {/* Alliances Tab */}
          {activeTab === 'alliances' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {isLoading ? (
                  <div className="p-8 text-center text-gray-400">Loading alliances...</div>
                ) : alliances.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Shield size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No alliances found</p>
                  </div>
                ) : (
                  alliances.map((alliance) => (
                    <button
                      key={alliance.id}
                      onClick={() => {
                        setSelectedAlliance(alliance)
                        setSelectedRelationship(null)
                      }}
                      className={cn(
                        'w-full p-4 flex items-center gap-4 hover:bg-dark-bg transition-colors text-left',
                        selectedAlliance?.id === alliance.id && 'bg-dark-bg'
                      )}
                    >
                      <div className="p-3 rounded-full bg-blue-500/20">
                        <Shield className="w-6 h-6 text-blue-400" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white">{alliance.emoji} {alliance.name}</span>
                          {alliance.leader && (
                            <span className="text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 flex items-center gap-1">
                              <Crown size={10} />
                              {alliance.leader.name}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-400 truncate mt-1">{alliance.purpose}</p>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                          <span>{alliance.member_count} members</span>
                          <span>Strength: {alliance.combined_strength}</span>
                          <span>Success: {Math.round(alliance.success_rate)}%</span>
                        </div>
                      </div>

                      <ChevronRight size={16} className="text-gray-500" />
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Rivalries Tab */}
          {activeTab === 'rivalries' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {isLoading ? (
                  <div className="p-8 text-center text-gray-400">Loading rivalries...</div>
                ) : rivalries.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Swords size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No active rivalries</p>
                  </div>
                ) : (
                  rivalries.map((rivalry) => (
                    <div
                      key={rivalry.id}
                      className="p-4 flex items-center gap-4"
                    >
                      <div className="p-3 rounded-full bg-red-500/20">
                        <Swords className="w-6 h-6 text-red-400" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white">{rivalry.challenger_name}</span>
                          <span className="text-red-400">vs</span>
                          <span className="font-medium text-white">{rivalry.defender_name}</span>
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                          <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400">
                            {rivalry.rivalry_type}
                          </span>
                          <span>Intensity: {rivalry.intensity}%</span>
                          <span>Score: {rivalry.challenger_wins} - {rivalry.defender_wins}</span>
                        </div>
                      </div>

                      {rivalry.current_leader && (
                        <span className="text-xs px-2 py-1 rounded bg-yellow-500/20 text-yellow-400 flex items-center gap-1">
                          <Crown size={12} />
                          Leading
                        </span>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Detail */}
        <div className="space-y-4">
          {selectedRelationship ? (
            <>
              {/* Relationship Detail */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                <div className="text-center">
                  {/* Agent Avatars */}
                  <div className="flex justify-center items-center gap-4 mb-4">
                    <div className="text-center">
                      <div className="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center text-lg font-bold text-purple-400 mx-auto">
                        {getInitials(selectedRelationship.agent_from.name)}
                      </div>
                      <p className="text-sm text-white mt-2">{selectedRelationship.agent_from.name}</p>
                    </div>

                    {(() => {
                      const config = getRelationshipConfig(selectedRelationship.relationship_type)
                      return (
                        <div className={cn('px-3 py-1 rounded-full', config.bgColor)}>
                          <config.icon className={cn('w-5 h-5', config.color)} />
                        </div>
                      )
                    })()}

                    <div className="text-center">
                      <div className="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center text-lg font-bold text-blue-400 mx-auto">
                        {getInitials(selectedRelationship.agent_to.name)}
                      </div>
                      <p className="text-sm text-white mt-2">{selectedRelationship.agent_to.name}</p>
                    </div>
                  </div>

                  <span className={cn(
                    'text-sm px-3 py-1 rounded',
                    getRelationshipConfig(selectedRelationship.relationship_type).bgColor,
                    getRelationshipConfig(selectedRelationship.relationship_type).color
                  )}>
                    {selectedRelationship.emoji} {getRelationshipConfig(selectedRelationship.relationship_type).label}
                  </span>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-3 mt-6">
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedRelationship.strength}%</div>
                    <div className="text-xs text-gray-400">Strength</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedRelationship.trust_level}%</div>
                    <div className="text-xs text-gray-400">Trust</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedRelationship.respect_level}%</div>
                    <div className="text-xs text-gray-400">Respect</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedRelationship.total_interactions}</div>
                    <div className="text-xs text-gray-400">Interactions</div>
                  </div>
                </div>
              </div>

              {/* Competition Stats */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Target size={16} className="text-orange-400" />
                  Competition History
                </h4>
                <div className="flex justify-between items-center">
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-400">{selectedRelationship.competition_wins}</div>
                    <div className="text-xs text-gray-400">Wins</div>
                  </div>
                  <div className="text-2xl text-gray-600">vs</div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-red-400">{selectedRelationship.competition_losses}</div>
                    <div className="text-xs text-gray-400">Losses</div>
                  </div>
                </div>
              </div>

              {/* Collaboration Stats */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Link2 size={16} className="text-green-400" />
                  Collaboration History
                </h4>
                <div className="flex justify-between items-center">
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-400">{selectedRelationship.successful_collaborations}</div>
                    <div className="text-xs text-gray-400">Successful</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-red-400">{selectedRelationship.failed_collaborations}</div>
                    <div className="text-xs text-gray-400">Failed</div>
                  </div>
                </div>
              </div>
            </>
          ) : selectedAlliance ? (
            <>
              {/* Alliance Detail */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/20 mb-4">
                    <Shield className="w-8 h-8 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-medium text-white">{selectedAlliance.emoji} {selectedAlliance.name}</h3>
                  {selectedAlliance.leader && (
                    <p className="text-sm text-yellow-400 mt-1 flex items-center justify-center gap-1">
                      <Crown size={14} />
                      Led by {selectedAlliance.leader.name}
                    </p>
                  )}
                  <p className="text-sm text-gray-400 mt-2">{selectedAlliance.purpose}</p>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-3 mt-6">
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedAlliance.member_count}</div>
                    <div className="text-xs text-gray-400">Members</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{selectedAlliance.combined_strength}</div>
                    <div className="text-xs text-gray-400">Strength</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{Math.round(selectedAlliance.success_rate)}%</div>
                    <div className="text-xs text-gray-400">Success</div>
                  </div>
                </div>
              </div>

              {/* Members */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3">Members</h4>
                <div className="space-y-2">
                  {selectedAlliance.members.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center gap-3 p-2 bg-dark-bg rounded-lg"
                    >
                      <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-xs font-medium text-blue-400">
                        {getInitials(member.name)}
                      </div>
                      <span className="text-sm text-white">{member.name}</span>
                      {selectedAlliance.leader?.id === member.id && (
                        <Crown size={12} className="text-yellow-400 ml-auto" />
                      )}
                    </div>
                  ))}
                  {selectedAlliance.member_count > selectedAlliance.members.length && (
                    <p className="text-xs text-gray-500 text-center">
                      +{selectedAlliance.member_count - selectedAlliance.members.length} more members
                    </p>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              <Users size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Select a relationship or alliance to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
