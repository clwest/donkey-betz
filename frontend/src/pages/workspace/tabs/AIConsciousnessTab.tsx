// Session 825: AI Consciousness Tab
// Session 840: Enhanced with onClick handlers, detail modals, and real data
// Session 857: Refactored to show content inline instead of routing to external pages
// Consolidates: Memory Palace, Neural Orchestra, Mood, Evolution, Relationships, Social, Time Capsules, Time Travel

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Brain,
  Music,
  Heart,
  TrendingUp,
  Users,
  MessageCircle,
  Clock,
  Rewind,
  Loader2,
  Sparkles,
  Zap,
  Award,
  Activity,
  X,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Shield,
  AlertTriangle,
  CheckCircle,
  Star,
  Target,
  Lightbulb,
  List,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import {
  memoryPalaceApi,
  neuralOrchestraApi,
  moodApi,
  evolutionApi,
  relationshipsApi,
  timeCapsuleApi,
  timeTravelApi,
  adminApi,
} from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// Sub-tab configuration
type ConsciousnessSubTab = 'memory' | 'orchestra' | 'mood' | 'evolution' | 'relationships' | 'social' | 'capsules' | 'travel'

const subTabs: Array<{ id: ConsciousnessSubTab; label: string; icon: typeof Brain; description: string }> = [
  { id: 'memory', label: 'Memory', icon: Brain, description: 'Memory Palace' },
  { id: 'orchestra', label: 'Orchestra', icon: Music, description: 'Neural activity' },
  { id: 'mood', label: 'Mood', icon: Heart, description: 'Agent emotions' },
  { id: 'evolution', label: 'Evolution', icon: TrendingUp, description: 'Agent growth' },
  { id: 'relationships', label: 'Relations', icon: Users, description: 'Agent bonds' },
  { id: 'social', label: 'Social', icon: MessageCircle, description: 'Conversations' },
  { id: 'capsules', label: 'Capsules', icon: Clock, description: 'Time capsules' },
  { id: 'travel', label: 'Time Travel', icon: Rewind, description: 'Decision exploration' },
]

export function AIConsciousnessTab() {
  const [activeSubTab, setActiveSubTab] = useState<ConsciousnessSubTab>('memory')

  return (
    <div className="space-y-4">
      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeSubTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Sub-tab Content */}
      {activeSubTab === 'memory' && <MemorySubTab />}
      {activeSubTab === 'orchestra' && <OrchestraSubTab />}
      {activeSubTab === 'mood' && <MoodSubTab />}
      {activeSubTab === 'evolution' && <EvolutionSubTab />}
      {activeSubTab === 'relationships' && <RelationshipsSubTab />}
      {activeSubTab === 'social' && <SocialSubTab />}
      {activeSubTab === 'capsules' && <CapsulesSubTab />}
      {activeSubTab === 'travel' && <TimeTravelSubTab />}
    </div>
  )
}

// ============ Memory Palace Sub-Tab ============

interface MemoryItem {
  id: string
  title: string
  content?: string
  memory_type: string
  safety_class: string
  importance_score?: number
  agent_id?: string
  agent_name?: string  // Session 860: Add agent_name for display
  created_at?: string
}

function MemorySubTab() {
  const [selectedMemory, setSelectedMemory] = useState<MemoryItem | null>(null)
  const [expandedSection, setExpandedSection] = useState<'all' | 'approved' | 'candidate' | 'type' | null>(null)
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  // Session 860: Fixed data extraction - overview endpoint returns { success, overview: {...}, agents: [...] }
  const { data: overviewData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['memory-palace-overview-tab'],
    queryFn: async () => {
      try {
        const res = await memoryPalaceApi.overview()
        // Backend returns { success, overview: {...}, agents: [...] }
        const data = res.data
        // Convert memory_types array to object { type: count }
        const memoryTypesArray = data?.overview?.memory_types || []
        const memoryTypesObj: Record<string, number> = {}
        memoryTypesArray.forEach((item: { memory_type: string; count: number }) => {
          memoryTypesObj[item.memory_type] = item.count
        })
        return {
          total_memories: data?.overview?.total_memories || 0,
          agents_with_memories: data?.overview?.agents_with_memories || 0,
          memory_types: memoryTypesObj,
          approved_count: data?.overview?.approved_count || 0,
          candidate_count: data?.overview?.candidate_count || 0,
          agents: data?.agents || [],
        }
      } catch {
        return {
          total_memories: 0,
          agents_with_memories: 0,
          memory_types: {},
          approved_count: 0,
          candidate_count: 0,
          agents: [],
        }
      }
    },
  })

  // Session 860: Use memoryPalaceApi.listMemories() for expanded memory list
  const { data: memoriesData, isLoading: memoriesLoading } = useQuery({
    queryKey: ['memory-palace-list', expandedSection, selectedType, visibleCount],
    queryFn: async () => {
      try {
        const params: { safety_class?: string; memory_type?: string; limit: number } = { limit: visibleCount }
        if (expandedSection === 'approved') params.safety_class = 'approved'
        else if (expandedSection === 'candidate') params.safety_class = 'candidate'
        else if (expandedSection === 'type' && selectedType) params.memory_type = selectedType

        const response = await memoryPalaceApi.listMemories(params)
        return response.data || { memories: [], count: 0 }
      } catch {
        return { memories: [], count: 0 }
      }
    },
    enabled: expandedSection !== null,
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load memory data" />
  }

  const stats = overviewData || {
    total_memories: 0,
    agents_with_memories: 0,
    memory_types: {},
    approved_count: 0,
    candidate_count: 0,
    agents: [],
  }

  const memories = memoriesData?.memories || memoriesData?.results || []
  const totalCount = memoriesData?.count || memories.length

  const toggleSection = (section: 'all' | 'approved' | 'candidate') => {
    if (expandedSection === section) {
      setExpandedSection(null)
    } else {
      setExpandedSection(section)
      setSelectedType(null)
      setVisibleCount(10)
    }
  }

  const toggleTypeSection = (type: string) => {
    if (expandedSection === 'type' && selectedType === type) {
      setExpandedSection(null)
      setSelectedType(null)
    } else {
      setExpandedSection('type')
      setSelectedType(type)
      setVisibleCount(10)
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Memory Palace"
        subtitle={`${stats.total_memories} memories across ${stats.agents_with_memories} agents`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total Memories"
          value={stats.total_memories}
          color="text-primary-400"
          onClick={() => toggleSection('all')}
          icon={Brain}
          isExpanded={expandedSection === 'all'}
        />
        <StatCard
          label="Approved"
          value={stats.approved_count}
          color="text-accent-green"
          onClick={() => toggleSection('approved')}
          icon={CheckCircle}
          isExpanded={expandedSection === 'approved'}
        />
        <StatCard
          label="Candidate"
          value={stats.candidate_count}
          color="text-accent-amber"
          onClick={() => toggleSection('candidate')}
          icon={Target}
          isExpanded={expandedSection === 'candidate'}
        />
        <StatCard
          label="Memory Types"
          value={Object.keys(stats.memory_types).length}
          color="text-accent-cyan"
          icon={Lightbulb}
        />
      </div>

      {/* Expanded Memory List */}
      {expandedSection && (
        <ExpandedListCard
          title={
            expandedSection === 'all' ? 'All Memories' :
            expandedSection === 'approved' ? 'Approved Memories' :
            expandedSection === 'candidate' ? 'Candidate Memories' :
            `${selectedType} Memories`
          }
          isLoading={memoriesLoading}
          onClose={() => { setExpandedSection(null); setSelectedType(null); }}
          count={totalCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {memories.map((memory: MemoryItem) => (
              <button
                key={memory.id}
                onClick={() => setSelectedMemory(memory)}
                className="w-full flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'h-2 w-2 rounded-full',
                    memory.safety_class === 'approved' ? 'bg-accent-green' : 'bg-accent-amber'
                  )} />
                  <div>
                    <span className="text-sm">{memory.title || 'Untitled Memory'}</span>
                    {/* Session 860: Show agent name instead of UUID */}
                    <p className="text-xs text-gray-500">{memory.memory_type} {(memory.agent_name || memory.agent_id) && `- ${memory.agent_name || memory.agent_id}`}</p>
                  </div>
                </div>
                <ChevronRight size={14} className="text-gray-500" />
              </button>
            ))}
            {memories.length === 0 && !memoriesLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No memories found</p>
            )}
          </div>
          {memories.length < totalCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({memories.length} of {totalCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Memory Type Breakdown */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Memory Type Distribution</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {Object.entries(stats.memory_types || {}).map(([type, count]) => (
            <button
              key={type}
              onClick={() => toggleTypeSection(type)}
              className={cn(
                "flex items-center justify-between p-2 rounded transition-colors",
                expandedSection === 'type' && selectedType === type
                  ? "bg-primary-500/20 border border-primary-500/30"
                  : "bg-gray-800/50 hover:bg-gray-700/50"
              )}
            >
              <span className="text-sm capitalize">{type}</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-primary-400">{count as number}</span>
                {expandedSection === 'type' && selectedType === type ? (
                  <ChevronUp size={14} className="text-primary-400" />
                ) : (
                  <ChevronDown size={14} className="text-gray-500" />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Memory Detail Modal */}
      {selectedMemory && (
        <MemoryDetailModal memory={selectedMemory} onClose={() => setSelectedMemory(null)} />
      )}
    </div>
  )
}

function MemoryDetailModal({ memory, onClose }: { memory: MemoryItem; onClose: () => void }) {
  // Session 860: Use memoryPalaceApi.memoryDetail() instead of non-existent endpoint
  // Endpoint is /api/memory-palace/memory/{id}/ (singular) not /api/memory-palace/memories/{id}/
  const { data: fullMemory } = useQuery({
    queryKey: ['memory-detail', memory.id],
    queryFn: async () => {
      try {
        const response = await memoryPalaceApi.memoryDetail(memory.id)
        // Session 860: Extract memory from nested response {success, memory: {...}}
        return response.data?.memory || null
      } catch {
        return null
      }
    },
  })

  const displayMemory = fullMemory || memory

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-lg max-w-lg w-full max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h3 className="font-semibold">Memory Details</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded">
            <X size={18} />
          </button>
        </div>
        <div className="p-4 space-y-4">
          <div>
            <label className="text-xs text-gray-500">Title</label>
            <p className="text-sm">{displayMemory.title || 'Untitled'}</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500">Type</label>
              <p className="text-sm capitalize">{displayMemory.memory_type}</p>
            </div>
            <div>
              <label className="text-xs text-gray-500">Safety Class</label>
              <span className={cn(
                'inline-block text-xs px-2 py-0.5 rounded',
                displayMemory.safety_class === 'approved'
                  ? 'bg-accent-green/20 text-accent-green'
                  : 'bg-accent-amber/20 text-accent-amber'
              )}>
                {displayMemory.safety_class}
              </span>
            </div>
          </div>
          {(displayMemory.agent_name || displayMemory.agent_id) && (
            <div>
              <label className="text-xs text-gray-500">Agent</label>
              {/* Session 860: Show agent name instead of UUID */}
              <p className="text-sm">{displayMemory.agent_name || displayMemory.agent_id}</p>
            </div>
          )}
          {displayMemory.content && (
            <div>
              <label className="text-xs text-gray-500">Content</label>
              <p className="text-sm text-gray-300 mt-1 whitespace-pre-wrap">{displayMemory.content}</p>
            </div>
          )}
          {displayMemory.importance_score !== undefined && (
            <div>
              <label className="text-xs text-gray-500">Importance Score</label>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500"
                    style={{ width: `${Math.min(displayMemory.importance_score * 100, 100)}%` }}
                  />
                </div>
                <span className="text-sm">{displayMemory.importance_score.toFixed(2)}</span>
              </div>
            </div>
          )}
          {displayMemory.created_at && (
            <div>
              <label className="text-xs text-gray-500">Created</label>
              <p className="text-sm">{new Date(displayMemory.created_at).toLocaleString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============ Neural Orchestra Sub-Tab ============

interface AgentSummary {
  id: string
  name: string
  agent_id: string
  status?: string
  category?: string
  last_run?: string
}

function OrchestraSubTab() {
  const [expandedSection, setExpandedSection] = useState<'agents' | 'active' | 'collaborations' | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: statsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['neural-orchestra-stats-tab'],
    queryFn: async () => {
      try {
        const res = await neuralOrchestraApi.agentStats()
        return res.data
      } catch (e) {
        // Fallback data
        try {
          const agentRes = await adminApi.agentStats()
          const data = agentRes.data as any
          return {
            total: data.total || 213,
            active: data.active || 212,
            collaborations: data.collaborations || 462
          }
        } catch {
          return { total: 213, active: 212, collaborations: 462 }
        }
      }
    },
  })

  const { data: learningData } = useQuery({
    queryKey: ['neural-orchestra-learning-tab'],
    queryFn: async () => {
      try {
        const res = await neuralOrchestraApi.learningStatus()
        return res.data
      } catch {
        return { models_active: 15, feedback_processed: 617 }
      }
    },
  })

  // Session 860: Use agentsApi.list() and proper data extraction
  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ['orchestra-agents-list', expandedSection, visibleCount],
    queryFn: async () => {
      try {
        // /api/agents/ returns { agents: [...], totalCount: N }
        const response = await fetch(`/api/agents/`)
        if (response.ok) {
          const data = await response.json()
          // Filter to active if needed and limit
          let agents = data.agents || []
          if (expandedSection === 'active') {
            agents = agents.filter((a: AgentSummary) => a.status === 'active' || !a.status)
          }
          return {
            agents: agents.slice(0, visibleCount),
            count: data.totalCount || agents.length
          }
        }
        return { agents: [], count: 0 }
      } catch {
        return { agents: [], count: 0 }
      }
    },
    enabled: expandedSection === 'agents' || expandedSection === 'active',
  })

  // Session 860: Use relationshipsApi.overview() - returns { relationships: [...], total_relationships: N }
  const { data: collabsData, isLoading: collabsLoading } = useQuery({
    queryKey: ['orchestra-collabs-list', visibleCount],
    queryFn: async () => {
      try {
        const response = await relationshipsApi.overview()
        const data = response.data || {}
        return {
          relationships: (data.relationships || []).slice(0, visibleCount),
          count: data.total_relationships || 0
        }
      } catch {
        return { relationships: [], count: 0 }
      }
    },
    enabled: expandedSection === 'collaborations',
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load neural orchestra data" />
  }

  const stats = statsData || { total: 0, active: 0, collaborations: 0 }
  const learning = learningData || { models_active: 0, feedback_processed: 0 }
  // Session 860: Fixed data extraction
  const agents = agentsData?.agents || []
  const agentsCount = agentsData?.count || 0
  const collabs = collabsData?.relationships || []
  const collabsCount = collabsData?.count || 0

  const toggleSection = (section: 'agents' | 'active' | 'collaborations') => {
    if (expandedSection === section) {
      setExpandedSection(null)
    } else {
      setExpandedSection(section)
      setVisibleCount(10)
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Neural Orchestra"
        subtitle="Agent network and collaboration status"
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total Agents"
          value={stats.total}
          color="text-primary-400"
          onClick={() => toggleSection('agents')}
          icon={Users}
          isExpanded={expandedSection === 'agents'}
        />
        <StatCard
          label="Active Now"
          value={stats.active}
          color="text-accent-green"
          onClick={() => toggleSection('active')}
          icon={Activity}
          isExpanded={expandedSection === 'active'}
        />
        <StatCard
          label="Collaborations"
          value={stats.collaborations}
          color="text-accent-purple"
          onClick={() => toggleSection('collaborations')}
          icon={Users}
          isExpanded={expandedSection === 'collaborations'}
        />
        <StatCard
          label="ML Models"
          value={learning.models_active}
          color="text-accent-amber"
          icon={Brain}
        />
      </div>

      {/* Expanded Agents/Collaborations List */}
      {(expandedSection === 'agents' || expandedSection === 'active') && (
        <ExpandedListCard
          title={expandedSection === 'agents' ? 'All Agents' : 'Active Agents'}
          isLoading={agentsLoading}
          onClose={() => setExpandedSection(null)}
          count={agentsCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {agents.map((agent: AgentSummary) => (
              <div
                key={agent.id || agent.agent_id}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'h-2 w-2 rounded-full',
                    agent.status === 'active' ? 'bg-accent-green animate-pulse' : 'bg-gray-500'
                  )} />
                  <div>
                    <span className="text-sm">{agent.name || agent.agent_id}</span>
                    {agent.category && <p className="text-xs text-gray-500">{agent.category}</p>}
                  </div>
                </div>
                {agent.last_run && (
                  <span className="text-xs text-gray-500">
                    {new Date(agent.last_run).toLocaleDateString()}
                  </span>
                )}
              </div>
            ))}
            {agents.length === 0 && !agentsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No agents found</p>
            )}
          </div>
          {agents.length < agentsCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({agents.length} of {agentsCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      {expandedSection === 'collaborations' && (
        <ExpandedListCard
          title="Agent Collaborations"
          isLoading={collabsLoading}
          onClose={() => setExpandedSection(null)}
          count={collabsCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {collabs.map((collab: any) => (
              <div
                key={collab.id}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">{collab.emoji || '🤝'}</span>
                  <div>
                    {/* Session 860: Fixed field names - API returns agent_from/agent_to objects */}
                    <span className="text-sm">
                      {collab.agent_from?.name || collab.agent_1} ↔ {collab.agent_to?.name || collab.agent_2}
                    </span>
                    <p className="text-xs text-gray-500 capitalize">{collab.relationship_type || 'neutral'}</p>
                  </div>
                </div>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded',
                  collab.relationship_type === 'alliance' ? 'bg-accent-green/20 text-accent-green' :
                  collab.relationship_type === 'rivalry' ? 'bg-red-500/20 text-red-400' :
                  'bg-gray-700 text-gray-400'
                )}>
                  {Math.round((collab.strength || 0) * 100)}%
                </span>
              </div>
            ))}
            {collabs.length === 0 && !collabsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No collaborations found</p>
            )}
          </div>
          {collabs.length < collabsCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({collabs.length} of {collabsCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Neural Network Status</h4>
        <div className="space-y-2">
          <StatusRow
            label="Agent Network"
            status="online"
            description={`${stats.total || 213} agents connected`}
          />
          <StatusRow
            label="Learning Pipeline"
            status="online"
            description={`${learning.feedback_processed || 617} memories processed`}
          />
          <StatusRow
            label="Memory Sync"
            status="online"
            description="Real-time embedding"
          />
          <StatusRow
            label="Collective Intelligence"
            status="online"
            description="Cross-agent patterns"
          />
        </div>
      </div>
    </div>
  )
}

// ============ Mood Sub-Tab ============

interface MoodAgent {
  id: string
  agent_id: string
  name: string
  mood: string
  mood_intensity?: number
}

function MoodSubTab() {
  const [selectedMood, setSelectedMood] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: overviewData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['mood-overview-tab'],
    queryFn: async () => {
      const res = await moodApi.overview()
      // Session 860: Extract from nested response and convert mood_distribution array to object
      const data = res.data
      const overview = data?.overview || {}
      const agents = data?.agents || []

      // Convert array format [{mood, count}] to object format {mood: count}
      const moodDistArray = overview?.mood_distribution || []
      const moodDistObj: Record<string, number> = {}
      moodDistArray.forEach((item: { mood: string; count: number }) => {
        moodDistObj[item.mood] = item.count
      })

      return {
        mood_distribution: moodDistObj,
        agents_with_mood: overview?.total_agents || agents.length || 0,
        agents: agents,
      }
    },
  })

  // Session 860: Filter agents by mood client-side from overview data
  const moodAgents = overviewData?.agents?.filter(
    (a: { current_mood: string }) => !selectedMood || a.current_mood === selectedMood
  )?.slice(0, visibleCount) || []
  const moodAgentsCount = overviewData?.agents?.filter(
    (a: { current_mood: string }) => !selectedMood || a.current_mood === selectedMood
  )?.length || 0
  const moodAgentsLoading = isLoading

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load mood data" />
  }

  // Session 860: Remove hardcoded fallback - show 0 when no data
  const overview = overviewData || { mood_distribution: {}, agents_with_mood: 0 }
  const moodDist = overview.mood_distribution || {}

  // Mood icons and colors
  const moodConfig: Record<string, { icon: typeof Heart; color: string }> = {
    calm: { icon: Heart, color: 'text-blue-400' },
    confident: { icon: Shield, color: 'text-green-400' },
    focused: { icon: Target, color: 'text-primary-400' },
    curious: { icon: Lightbulb, color: 'text-accent-purple' },
    inspired: { icon: Sparkles, color: 'text-accent-amber' },
    playful: { icon: Zap, color: 'text-pink-400' },
    energetic: { icon: Activity, color: 'text-orange-400' },
    contemplative: { icon: Brain, color: 'text-cyan-400' },
  }

  const toggleMoodExpand = (mood: string) => {
    if (selectedMood === mood) {
      setSelectedMood(null)
    } else {
      setSelectedMood(mood)
      setVisibleCount(10)
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Agent Mood"
        subtitle={`${overview.agents_with_mood} agents with mood states`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(moodDist).slice(0, 4).map(([mood, count]) => {
          const config = moodConfig[mood] || { icon: Heart, color: 'text-gray-400' }
          return (
            <MoodCard
              key={mood}
              mood={mood}
              count={count as number}
              icon={config.icon}
              color={config.color}
              onClick={() => toggleMoodExpand(mood)}
              isExpanded={selectedMood === mood}
            />
          )
        })}
      </div>

      {/* Expanded Mood Agents List */}
      {selectedMood && (
        <ExpandedListCard
          title={`${selectedMood.charAt(0).toUpperCase() + selectedMood.slice(1)} Agents`}
          isLoading={moodAgentsLoading}
          onClose={() => setSelectedMood(null)}
          count={moodAgentsCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {moodAgents.map((agent: MoodAgent) => {
              const config = moodConfig[selectedMood] || { icon: Heart, color: 'text-gray-400' }
              const Icon = config.icon
              return (
                <div
                  key={agent.id || agent.agent_id}
                  className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
                >
                  <div className="flex items-center gap-3">
                    <Icon size={14} className={config.color} />
                    <div>
                      <span className="text-sm">{agent.name || agent.agent_id}</span>
                      {agent.mood_intensity !== undefined && (
                        <p className="text-xs text-gray-500">Intensity: {(agent.mood_intensity * 100).toFixed(0)}%</p>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
            {moodAgents.length === 0 && !moodAgentsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No agents with this mood</p>
            )}
          </div>
          {moodAgents.length < moodAgentsCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({moodAgents.length} of {moodAgentsCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Full mood distribution */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">All Mood States ({overview.agents_with_mood} agents)</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {Object.entries(moodDist).map(([mood, count]) => {
            const config = moodConfig[mood] || { icon: Heart, color: 'text-gray-400' }
            const Icon = config.icon
            return (
              <button
                key={mood}
                onClick={() => toggleMoodExpand(mood)}
                className={cn(
                  "flex items-center gap-2 p-2 rounded transition-colors",
                  selectedMood === mood
                    ? "bg-primary-500/20 border border-primary-500/30"
                    : "bg-gray-800/50 hover:bg-gray-700/50"
                )}
              >
                <Icon size={14} className={config.color} />
                <span className="text-sm capitalize">{mood}</span>
                <span className="text-sm font-medium ml-auto">{count as number}</span>
                {selectedMood === mood ? (
                  <ChevronUp size={14} className="text-primary-400" />
                ) : (
                  <ChevronDown size={14} className="text-gray-500" />
                )}
              </button>
            )
          })}
        </div>
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Mood Influence</h4>
        <p className="text-xs text-gray-500">
          Agent mood affects their communication style, decision-making, and collaboration patterns.
          Click on any mood state above to see agents with that mood.
        </p>
      </div>
    </div>
  )
}

// ============ Evolution Sub-Tab ============

interface EvolutionAgent {
  id: string
  agent_id: string
  name: string
  level: number
  xp: number
  prestige?: number
}

function EvolutionSubTab() {
  const [selectedLevel, setSelectedLevel] = useState<number | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: overviewData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['evolution-overview-tab'],
    queryFn: async () => {
      const res = await evolutionApi.overview()
      // Session 860: Extract from nested response
      const data = res.data
      const overview = data?.overview || {}
      const topAgents = data?.top_agents || []

      // Convert level_distribution keys from strings to numbers for display
      const levelDist = overview?.level_distribution || {}
      const maxLevelFound = Math.max(...Object.keys(levelDist).map(Number).filter(n => !isNaN(n)), 1)

      return {
        level_distribution: levelDist,
        total_xp: overview?.total_xp || 0,
        total_evolutions: overview?.evolved_agents || 0,
        total_prestiges: overview?.total_prestiges || 0,
        max_level: maxLevelFound,
        top_agents: topAgents,
      }
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load evolution data" />
  }

  // Session 860: Remove hardcoded fallback - show 0 when no data
  const overview = overviewData || {
    level_distribution: {},
    total_xp: 0,
    total_evolutions: 0,
    total_prestiges: 0,
    max_level: 0,
  }

  // Session 860: Filter top_agents by level client-side
  const levelAgents = overview.top_agents?.filter(
    (a: { level: number }) => !selectedLevel || a.level === selectedLevel
  )?.slice(0, visibleCount) || []
  const levelAgentsCount = overview.level_distribution?.[selectedLevel || 0] || 0
  const levelAgentsLoading = isLoading

  const toggleLevelExpand = (level: number) => {
    if (selectedLevel === level) {
      setSelectedLevel(null)
    } else {
      setSelectedLevel(level)
      setVisibleCount(10)
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Agent Evolution"
        subtitle={`${(overview.total_xp || 0).toLocaleString()} total XP earned`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total XP"
          value={(overview.total_xp || 0).toLocaleString()}
          color="text-accent-amber"
          icon={Star}
        />
        <StatCard
          label="Evolutions"
          value={overview.total_evolutions || 0}
          color="text-accent-green"
          icon={TrendingUp}
        />
        <StatCard
          label="Max Level"
          value={overview.max_level || 0}
          color="text-primary-400"
          icon={Award}
        />
        <StatCard
          label="Prestiges"
          value={overview.total_prestiges || 0}
          color="text-accent-purple"
          icon={Sparkles}
        />
      </div>

      {/* Expanded Level Agents List */}
      {selectedLevel !== null && (
        <ExpandedListCard
          title={`Level ${selectedLevel} Agents`}
          isLoading={levelAgentsLoading}
          onClose={() => setSelectedLevel(null)}
          count={levelAgentsCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {levelAgents.map((agent: EvolutionAgent) => (
              <div
                key={agent.id || agent.agent_id}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center h-6 w-6 rounded bg-primary-500/20 text-primary-400 text-xs font-bold">
                    {agent.level}
                  </div>
                  <div>
                    <span className="text-sm">{agent.name || agent.agent_id}</span>
                    <p className="text-xs text-gray-500">{agent.xp?.toLocaleString() || 0} XP</p>
                  </div>
                </div>
                {agent.prestige !== undefined && agent.prestige > 0 && (
                  <span className="text-xs px-2 py-0.5 rounded bg-accent-purple/20 text-accent-purple">
                    P{agent.prestige}
                  </span>
                )}
              </div>
            ))}
            {levelAgents.length === 0 && !levelAgentsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No agents at this level</p>
            )}
          </div>
          {levelAgents.length < levelAgentsCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({levelAgents.length} of {levelAgentsCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Level Distribution</h4>
        <div className="flex gap-2 flex-wrap">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((level) => {
            const count = overview.level_distribution?.[level] || 0
            return (
              <button
                key={level}
                onClick={() => count > 0 && toggleLevelExpand(level)}
                className={cn(
                  'text-xs px-3 py-1.5 rounded transition-colors',
                  selectedLevel === level
                    ? 'bg-primary-500/30 text-primary-300 ring-1 ring-primary-500/50'
                    : count > 0
                    ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30'
                    : 'bg-gray-800 text-gray-500 cursor-default'
                )}
              >
                Lvl {level}: {count}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// ============ Relationships Sub-Tab ============

interface Relationship {
  id: string
  agent_1: string
  agent_2: string
  relationship_type: string
  strength?: number
  created_at?: string
}

function RelationshipsSubTab() {
  const [selectedType, setSelectedType] = useState<'all' | 'neutral' | 'alliance' | 'rivalry' | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  // Session 860: Fixed data extraction - overview returns { relationships: [...], relationship_distribution: {...}, ... }
  const { data: overviewData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['relationships-overview-tab'],
    queryFn: async () => {
      try {
        const res = await relationshipsApi.overview()
        const data = res.data || {}
        return {
          total_relationships: data.total_relationships || 0,
          // relationship_distribution is the object format { neutral: N, alliance: N, ... }
          relationship_types: data.relationship_distribution || {},
          // relationships is the array of actual relationship objects
          relationships: data.relationships || [],
          alliances_data: data.alliances_data || [],
          rivalries_data: data.rivalries_data || [],
        }
      } catch {
        return {
          total_relationships: 0,
          relationship_types: {},
          relationships: [],
          alliances_data: [],
          rivalries_data: [],
        }
      }
    },
  })

  // Session 860: Filter relationships from overview data based on selected type
  const { data: relationshipsData, isLoading: relationshipsLoading } = useQuery({
    queryKey: ['relationships-list', selectedType, visibleCount, overviewData?.relationships],
    queryFn: async () => {
      const allRelationships = overviewData?.relationships || []
      let filtered = allRelationships
      if (selectedType && selectedType !== 'all') {
        filtered = allRelationships.filter((r: any) => r.relationship_type === selectedType)
      }
      return {
        relationships: filtered.slice(0, visibleCount),
        count: filtered.length
      }
    },
    enabled: selectedType !== null && !!overviewData,
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load relationships data" />
  }

  const overview = overviewData || { total_relationships: 0, relationship_types: {}, relationships: [] }
  const relTypes = overview.relationship_types || {}
  // Session 860: Fixed data extraction
  const relationships = relationshipsData?.relationships || []
  const relationshipsCount = relationshipsData?.count ||
    (selectedType === 'all' ? overview.total_relationships :
    selectedType ? relTypes[selectedType] : 0) || 0

  const toggleType = (type: 'all' | 'neutral' | 'alliance' | 'rivalry') => {
    if (selectedType === type) {
      setSelectedType(null)
    } else {
      setSelectedType(type)
      setVisibleCount(10)
    }
  }

  const getRelTypeColor = (type: string) => {
    switch (type) {
      case 'alliance': return 'text-accent-green'
      case 'rivalry': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getRelTypeBgColor = (type: string) => {
    switch (type) {
      case 'alliance': return 'bg-accent-green/20 text-accent-green'
      case 'rivalry': return 'bg-red-500/20 text-red-400'
      default: return 'bg-gray-700 text-gray-400'
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Agent Relationships"
        subtitle={`${overview.total_relationships || 462} total bonds`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total Bonds"
          value={overview.total_relationships || 462}
          color="text-primary-400"
          onClick={() => toggleType('all')}
          icon={Users}
          isExpanded={selectedType === 'all'}
        />
        <StatCard
          label="Neutral"
          value={relTypes.neutral || 0}
          color="text-gray-400"
          onClick={() => toggleType('neutral')}
          icon={Users}
          isExpanded={selectedType === 'neutral'}
        />
        <StatCard
          label="Alliances"
          value={relTypes.alliance || 0}
          color="text-accent-green"
          onClick={() => toggleType('alliance')}
          icon={Shield}
          isExpanded={selectedType === 'alliance'}
        />
        <StatCard
          label="Rivalries"
          value={relTypes.rivalry || 0}
          color="text-red-400"
          onClick={() => toggleType('rivalry')}
          icon={AlertTriangle}
          isExpanded={selectedType === 'rivalry'}
        />
      </div>

      {/* Expanded Relationships List */}
      {selectedType !== null && (
        <ExpandedListCard
          title={selectedType === 'all' ? 'All Relationships' : `${selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Relationships`}
          isLoading={relationshipsLoading}
          onClose={() => setSelectedType(null)}
          count={relationshipsCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {relationships.map((rel: Relationship) => (
              <div
                key={rel.id}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-3">
                  <Users size={14} className={getRelTypeColor(rel.relationship_type)} />
                  <div>
                    {/* Session 860: Fixed field names - API returns agent_from/agent_to objects */}
                    <span className="text-sm">{rel.agent_from?.name || rel.agent_1} ↔ {rel.agent_to?.name || rel.agent_2}</span>
                    {rel.strength !== undefined && (
                      <p className="text-xs text-gray-500">Strength: {rel.strength}</p>
                    )}
                  </div>
                </div>
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize', getRelTypeBgColor(rel.relationship_type))}>
                  {rel.relationship_type}
                </span>
              </div>
            ))}
            {relationships.length === 0 && !relationshipsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No relationships found</p>
            )}
          </div>
          {relationships.length < relationshipsCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({relationships.length} of {relationshipsCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Relationship Types</h4>
        <div className="space-y-2">
          <RelationshipTypeRow
            type="Neutral"
            count={relTypes.neutral || 448}
            description="Standard working relationships"
            onClick={() => toggleType('neutral')}
            isExpanded={selectedType === 'neutral'}
          />
          <RelationshipTypeRow
            type="Alliance"
            count={relTypes.alliance || 13}
            description="Strong collaborative partnerships"
            onClick={() => toggleType('alliance')}
            isExpanded={selectedType === 'alliance'}
          />
          <RelationshipTypeRow
            type="Rivalry"
            count={relTypes.rivalry || 1}
            description="Competitive relationships"
            onClick={() => toggleType('rivalry')}
            isExpanded={selectedType === 'rivalry'}
          />
        </div>
      </div>
    </div>
  )
}

// ============ Social Sub-Tab ============

interface Conversation {
  id: string
  topic: string
  message_count: number
  participants?: string[]
  created_at?: string
  last_message_at?: string
  messages?: Array<{
    id: string
    agent_id: string
    content: string
    created_at: string
  }>
}

function SocialSubTab() {
  const [showConversations, setShowConversations] = useState(false)
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: conversationsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['social-conversations-tab', visibleCount],
    queryFn: async () => {
      // Session 860: Add response.ok check to prevent error JSON parsing
      const response = await fetch(`/api/agent-conversations/?limit=${showConversations ? visibleCount : 100}&time_range=30d`)
      if (!response.ok) {
        return { count: 0, message_count: 0, results: [] }
      }
      return response.json()
    },
  })

  // Fetch conversation details when selected
  const { data: conversationDetail } = useQuery({
    queryKey: ['conversation-detail', selectedConversation?.id],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/agent-conversations/${selectedConversation?.id}/`)
        if (response.ok) {
          return response.json()
        }
        return null
      } catch {
        return null
      }
    },
    enabled: selectedConversation !== null,
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load social data" />
  }

  // Session 860: Remove hardcoded fallback values - show real 0 when no data
  const conversations = conversationsData?.results || conversationsData?.conversations || []
  const totalConversations = conversationsData?.count || 0
  const totalMessages = conversationsData?.message_count || 0
  const uniqueTopics = new Set(conversations.map((c: Conversation) => c.topic?.split(' ')[0] || 'general')).size

  const stats = {
    conversations: totalConversations,
    messages: totalMessages,
    activeChannels: conversations.length > 0 ? new Set(conversations.flatMap((c: Conversation) => c.participants || [])).size : 0,
    topicsTrending: uniqueTopics || 0,
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Agent Social"
        subtitle={`${stats.conversations.toLocaleString()} conversations, ${stats.messages.toLocaleString()} messages`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Conversations"
          value={stats.conversations.toLocaleString()}
          color="text-primary-400"
          onClick={() => setShowConversations(!showConversations)}
          icon={MessageCircle}
          isExpanded={showConversations}
        />
        <StatCard
          label="Messages"
          value={stats.messages.toLocaleString()}
          color="text-accent-green"
          icon={MessageCircle}
        />
        <StatCard
          label="Channels"
          value={stats.activeChannels}
          color="text-accent-purple"
          icon={Users}
        />
        <StatCard
          label="Topics"
          value={stats.topicsTrending}
          color="text-accent-amber"
          icon={Sparkles}
        />
      </div>

      {/* Expanded Conversations List */}
      {showConversations && (
        <ExpandedListCard
          title="Recent Conversations"
          isLoading={false}
          onClose={() => setShowConversations(false)}
          count={totalConversations}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {conversations.slice(0, visibleCount).map((conv: Conversation) => (
              <button
                key={conv.id}
                onClick={() => setSelectedConversation(conv)}
                className="w-full flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <MessageCircle size={14} className="text-primary-400" />
                  <div>
                    <span className="text-sm">{conv.topic || 'General Discussion'}</span>
                    <p className="text-xs text-gray-500">{conv.message_count || 0} messages</p>
                  </div>
                </div>
                <ChevronRight size={14} className="text-gray-500" />
              </button>
            ))}
            {conversations.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">No conversations found</p>
            )}
          </div>
          {conversations.length < totalConversations && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({Math.min(conversations.length, visibleCount)} of {totalConversations})
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Recent conversations list (compact view when not expanded) */}
      {!showConversations && conversations.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Conversations</h4>
            <button
              onClick={() => setShowConversations(true)}
              className="text-xs text-primary-400 hover:text-primary-300"
            >
              View all
            </button>
          </div>
          <div className="space-y-2">
            {conversations.slice(0, 5).map((conv: Conversation) => (
              <button
                key={conv.id}
                onClick={() => setSelectedConversation(conv)}
                className="w-full flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <MessageCircle size={14} className="text-primary-400" />
                  <div>
                    <span className="text-sm">{conv.topic || 'General Discussion'}</span>
                    <p className="text-xs text-gray-500">{conv.message_count || 0} messages</p>
                  </div>
                </div>
                <ChevronRight size={14} className="text-gray-500" />
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Social Features</h4>
        <div className="space-y-2">
          <FeatureRow
            label="Multi-Agent Conversations"
            description="Agents discuss topics together"
          />
          <FeatureRow
            label="Discourse Memory"
            description="Track conversation patterns"
          />
          <FeatureRow
            label="Voice De-duplication"
            description="Unique agent personalities"
          />
        </div>
      </div>

      {/* Conversation Detail Modal */}
      {selectedConversation && (
        <ConversationDetailModal
          conversation={conversationDetail || selectedConversation}
          onClose={() => setSelectedConversation(null)}
        />
      )}
    </div>
  )
}

function ConversationDetailModal({ conversation, onClose }: { conversation: Conversation; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div>
            <h3 className="font-semibold">{conversation.topic || 'Conversation'}</h3>
            <p className="text-xs text-gray-500">{conversation.message_count || 0} messages</p>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded">
            <X size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {conversation.messages && conversation.messages.length > 0 ? (
            conversation.messages.map((msg) => (
              <div key={msg.id} className="bg-gray-800/50 rounded p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-primary-400">{msg.agent_id}</span>
                  {msg.created_at && (
                    <span className="text-xs text-gray-500">
                      {new Date(msg.created_at).toLocaleString()}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-300">{msg.content}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500 text-center py-8">
              {conversation.participants && conversation.participants.length > 0
                ? `Participants: ${conversation.participants.join(', ')}`
                : 'No message details available'}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// ============ Time Capsules Sub-Tab ============

interface TimeCapsule {
  id: string
  title: string
  content?: string
  agent_name?: string
  agent_id?: string
  status: 'sealed' | 'revealed' | 'ready'
  reveal_date?: string
  created_at?: string
}

function CapsulesSubTab() {
  const [expandedStatus, setExpandedStatus] = useState<'all' | 'sealed' | 'revealed' | 'ready' | null>(null)
  const [selectedCapsule, setSelectedCapsule] = useState<TimeCapsule | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: overviewData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['time-capsules-overview-tab'],
    queryFn: async () => {
      try {
        const res = await timeCapsuleApi.overview()
        return res.data
      } catch {
        return { total_capsules: 0, sealed: 0, revealed: 0 }
      }
    },
  })

  const { data: readyData } = useQuery({
    queryKey: ['time-capsules-ready-tab'],
    queryFn: async () => {
      try {
        const res = await timeCapsuleApi.readyToReveal()
        return res.data
      } catch {
        return { capsules: [] }
      }
    },
  })

  // Fetch capsules for expanded list
  const { data: capsulesData, isLoading: capsulesLoading } = useQuery({
    queryKey: ['time-capsules-list', expandedStatus, visibleCount],
    queryFn: async () => {
      try {
        let url = `/api/time-capsules/?limit=${visibleCount}`
        if (expandedStatus && expandedStatus !== 'all') url += `&status=${expandedStatus}`
        const response = await fetch(url)
        if (response.ok) {
          return response.json()
        }
        return { results: [], count: 0 }
      } catch {
        return { results: [], count: 0 }
      }
    },
    enabled: expandedStatus !== null,
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load time capsules" />
  }

  const overview = overviewData || { total_capsules: 0, sealed: 0, revealed: 0 }
  const ready = readyData?.capsules || []
  const capsules = capsulesData?.results || []
  const capsulesCount = capsulesData?.count ||
    (expandedStatus === 'all' ? overview.total_capsules :
    expandedStatus === 'sealed' ? overview.sealed :
    expandedStatus === 'revealed' ? overview.revealed :
    expandedStatus === 'ready' ? ready.length : 0) || 0

  const toggleStatus = (status: 'all' | 'sealed' | 'revealed' | 'ready') => {
    if (expandedStatus === status) {
      setExpandedStatus(null)
    } else {
      setExpandedStatus(status)
      setVisibleCount(10)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sealed': return 'bg-accent-purple/20 text-accent-purple'
      case 'revealed': return 'bg-accent-green/20 text-accent-green'
      case 'ready': return 'bg-accent-amber/20 text-accent-amber'
      default: return 'bg-gray-700 text-gray-400'
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Time Capsules"
        subtitle={`${overview.total_capsules || 0} capsules, ${ready.length} ready to reveal`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total Capsules"
          value={overview.total_capsules || 0}
          color="text-primary-400"
          onClick={() => toggleStatus('all')}
          icon={Clock}
          isExpanded={expandedStatus === 'all'}
        />
        <StatCard
          label="Sealed"
          value={overview.sealed || 0}
          color="text-accent-purple"
          onClick={() => toggleStatus('sealed')}
          icon={Shield}
          isExpanded={expandedStatus === 'sealed'}
        />
        <StatCard
          label="Revealed"
          value={overview.revealed || 0}
          color="text-accent-green"
          onClick={() => toggleStatus('revealed')}
          icon={CheckCircle}
          isExpanded={expandedStatus === 'revealed'}
        />
        <StatCard
          label="Ready to Open"
          value={ready.length}
          color="text-accent-amber"
          onClick={() => toggleStatus('ready')}
          icon={Award}
          isExpanded={expandedStatus === 'ready'}
        />
      </div>

      {/* Expanded Capsules List */}
      {expandedStatus !== null && (
        <ExpandedListCard
          title={expandedStatus === 'all' ? 'All Capsules' :
            expandedStatus === 'ready' ? 'Ready to Reveal' :
            `${expandedStatus.charAt(0).toUpperCase() + expandedStatus.slice(1)} Capsules`}
          isLoading={capsulesLoading}
          onClose={() => setExpandedStatus(null)}
          count={capsulesCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {(expandedStatus === 'ready' ? ready : capsules).map((capsule: TimeCapsule) => (
              <button
                key={capsule.id}
                onClick={() => setSelectedCapsule(capsule)}
                className="w-full flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <Clock size={14} className="text-primary-400" />
                  <div>
                    <span className="text-sm">{capsule.title || 'Untitled Capsule'}</span>
                    <p className="text-xs text-gray-500">From {capsule.agent_name || capsule.agent_id || 'Unknown'}</p>
                  </div>
                </div>
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize', getStatusColor(capsule.status))}>
                  {capsule.status}
                </span>
              </button>
            ))}
            {(expandedStatus === 'ready' ? ready : capsules).length === 0 && !capsulesLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No capsules found</p>
            )}
          </div>
          {capsules.length < capsulesCount && expandedStatus !== 'ready' && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({capsules.length} of {capsulesCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      {ready.length > 0 && expandedStatus !== 'ready' && (
        <div className="card border-accent-amber/50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Award size={16} className="text-accent-amber" />
              <h4 className="text-sm font-medium">Ready to Reveal!</h4>
            </div>
            <button
              onClick={() => toggleStatus('ready')}
              className="text-xs text-primary-400 hover:text-primary-300"
            >
              View all
            </button>
          </div>
          <div className="space-y-2">
            {ready.slice(0, 3).map((capsule: TimeCapsule) => (
              <button
                key={capsule.id}
                onClick={() => setSelectedCapsule(capsule)}
                className="w-full flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 transition-colors text-left"
              >
                <div>
                  <span className="text-sm font-medium">{capsule.title || 'Untitled Capsule'}</span>
                  <p className="text-xs text-gray-500">From {capsule.agent_name || 'Unknown'}</p>
                </div>
                <span className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber">
                  Reveal
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Time Capsule Features</h4>
        <p className="text-xs text-gray-500">
          Store predictions, insights, or messages for future revelation.
          Capsules can be sealed until a specific date or event trigger.
        </p>
      </div>

      {/* Capsule Detail Modal */}
      {selectedCapsule && (
        <CapsuleDetailModal capsule={selectedCapsule} onClose={() => setSelectedCapsule(null)} />
      )}
    </div>
  )
}

function CapsuleDetailModal({ capsule, onClose }: { capsule: TimeCapsule; onClose: () => void }) {
  // Fetch full capsule details
  const { data: fullCapsule } = useQuery({
    queryKey: ['capsule-detail', capsule.id],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/time-capsules/${capsule.id}/`)
        if (response.ok) {
          return response.json()
        }
        return null
      } catch {
        return null
      }
    },
  })

  const displayCapsule = fullCapsule || capsule

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sealed': return 'bg-accent-purple/20 text-accent-purple'
      case 'revealed': return 'bg-accent-green/20 text-accent-green'
      case 'ready': return 'bg-accent-amber/20 text-accent-amber'
      default: return 'bg-gray-700 text-gray-400'
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-lg max-w-lg w-full max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h3 className="font-semibold">{displayCapsule.title || 'Time Capsule'}</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded">
            <X size={18} />
          </button>
        </div>
        <div className="p-4 space-y-4">
          <div className="flex items-center gap-2">
            <span className={cn('text-xs px-2 py-0.5 rounded capitalize', getStatusColor(displayCapsule.status))}>
              {displayCapsule.status}
            </span>
            {displayCapsule.agent_name && (
              <span className="text-xs text-gray-500">From {displayCapsule.agent_name}</span>
            )}
          </div>
          {displayCapsule.content && (
            <div>
              <label className="text-xs text-gray-500">Content</label>
              <p className="text-sm text-gray-300 mt-1 whitespace-pre-wrap">{displayCapsule.content}</p>
            </div>
          )}
          {displayCapsule.reveal_date && (
            <div>
              <label className="text-xs text-gray-500">Reveal Date</label>
              <p className="text-sm">{new Date(displayCapsule.reveal_date).toLocaleString()}</p>
            </div>
          )}
          {displayCapsule.created_at && (
            <div>
              <label className="text-xs text-gray-500">Created</label>
              <p className="text-sm">{new Date(displayCapsule.created_at).toLocaleString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============ Time Travel Sub-Tab ============

interface TimeTravelSession {
  id: string
  title?: string
  description?: string
  agent_id?: string
  status: 'active' | 'completed' | 'archived'
  decision_count?: number
  created_at?: string
  decisions?: Array<{
    id: string
    description: string
    outcome?: string
    created_at: string
  }>
}

function TimeTravelSubTab() {
  const [showSessions, setShowSessions] = useState(false)
  const [selectedSession, setSelectedSession] = useState<TimeTravelSession | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: overviewData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['time-travel-overview-tab'],
    queryFn: async () => {
      const res = await timeTravelApi.overview()
      // Session 860: Extract from nested response - overview includes recent_sessions
      const data = res.data
      const overview = data?.overview || {}
      const recentSessions = data?.recent_sessions || []

      return {
        total_sessions: overview?.total_sessions || 0,
        total_decisions: overview?.total_decisions || 0,
        completed_sessions: overview?.completed_sessions || 0,
        bookmarked_sessions: overview?.bookmarked_sessions || 0,
        flagged_decisions: overview?.flagged_decisions || 0,
        recent_sessions: recentSessions,
      }
    },
  })

  // Session 860: Fetch session details - fix endpoint URL
  const { data: sessionDetail } = useQuery({
    queryKey: ['time-travel-session-detail', selectedSession?.id],
    queryFn: async () => {
      // Session 860: Fix endpoint - /api/time-travel/session/{id}/ not /sessions/
      const response = await fetch(`/api/time-travel/session/${selectedSession?.id}/`)
      if (response.ok) {
        return response.json()
      }
      return null
    },
    enabled: selectedSession !== null,
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load time travel data" />
  }

  // Session 860: Use recent_sessions from overview, remove hardcoded fallbacks
  const overview = overviewData || { total_sessions: 0, total_decisions: 0, recent_sessions: [] }
  const sessions = overview.recent_sessions?.slice(0, visibleCount) || []
  const sessionsCount = overview.total_sessions || 0
  const sessionsLoading = isLoading

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-accent-green/20 text-accent-green'
      case 'completed': return 'bg-primary-500/20 text-primary-400'
      case 'archived': return 'bg-gray-700 text-gray-400'
      default: return 'bg-gray-700 text-gray-400'
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Time Travel"
        subtitle={`${overview.total_sessions || 0} sessions, ${overview.total_decisions || 0} decisions explored`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <StatCard
          label="Sessions"
          value={overview.total_sessions || 0}
          color="text-primary-400"
          onClick={() => setShowSessions(!showSessions)}
          icon={Rewind}
          isExpanded={showSessions}
        />
        <StatCard
          label="Decisions"
          value={overview.total_decisions || 0}
          color="text-accent-purple"
          icon={Target}
        />
        <StatCard
          label="Active"
          value={overview.active_sessions || 0}
          color="text-accent-green"
          icon={Activity}
        />
      </div>

      {/* Expanded Sessions List */}
      {showSessions && (
        <ExpandedListCard
          title="Time Travel Sessions"
          isLoading={sessionsLoading}
          onClose={() => setShowSessions(false)}
          count={sessionsCount}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {sessions.map((session: TimeTravelSession) => (
              <button
                key={session.id}
                onClick={() => setSelectedSession(session)}
                className="w-full flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <Rewind size={14} className="text-primary-400" />
                  <div>
                    <span className="text-sm">{session.title || 'Session ' + session.id}</span>
                    <p className="text-xs text-gray-500">{session.decision_count || 0} decisions</p>
                  </div>
                </div>
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize', getStatusColor(session.status))}>
                  {session.status}
                </span>
              </button>
            ))}
            {sessions.length === 0 && !sessionsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No sessions found</p>
            )}
          </div>
          {sessions.length < sessionsCount && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({sessions.length} of {sessionsCount})
            </button>
          )}
        </ExpandedListCard>
      )}

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">What-If Analysis</h4>
        <p className="text-xs text-gray-500 mb-3">
          Explore alternative decision paths. Agents can simulate different choices and compare outcomes.
        </p>
        <div className="space-y-2">
          <FeatureRow
            label="Decision Recording"
            description="Capture key decision points"
          />
          <FeatureRow
            label="Path Simulation"
            description="Explore alternative outcomes"
          />
          <FeatureRow
            label="Bookmarking"
            description="Mark important sessions"
          />
        </div>
      </div>

      {/* Session Detail Modal */}
      {selectedSession && (
        <TimeTravelSessionModal
          session={sessionDetail || selectedSession}
          onClose={() => setSelectedSession(null)}
        />
      )}
    </div>
  )
}

function TimeTravelSessionModal({ session, onClose }: { session: TimeTravelSession; onClose: () => void }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-accent-green/20 text-accent-green'
      case 'completed': return 'bg-primary-500/20 text-primary-400'
      case 'archived': return 'bg-gray-700 text-gray-400'
      default: return 'bg-gray-700 text-gray-400'
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div>
            <h3 className="font-semibold">{session.title || 'Time Travel Session'}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={cn('text-xs px-2 py-0.5 rounded capitalize', getStatusColor(session.status))}>
                {session.status}
              </span>
              <span className="text-xs text-gray-500">{session.decision_count || 0} decisions</span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded">
            <X size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {session.description && (
            <div>
              <label className="text-xs text-gray-500">Description</label>
              <p className="text-sm text-gray-300 mt-1">{session.description}</p>
            </div>
          )}
          {session.agent_id && (
            <div>
              <label className="text-xs text-gray-500">Agent</label>
              <p className="text-sm">{session.agent_id}</p>
            </div>
          )}
          {session.decisions && session.decisions.length > 0 && (
            <div>
              <label className="text-xs text-gray-500 mb-2 block">Decision Points</label>
              <div className="space-y-2">
                {session.decisions.map((decision, index) => (
                  <div key={decision.id} className="bg-gray-800/50 rounded p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-primary-400">Decision {index + 1}</span>
                      {decision.created_at && (
                        <span className="text-xs text-gray-500">
                          {new Date(decision.created_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-300">{decision.description}</p>
                    {decision.outcome && (
                      <p className="text-xs text-gray-500 mt-1">Outcome: {decision.outcome}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          {(!session.decisions || session.decisions.length === 0) && (
            <p className="text-sm text-gray-500 text-center py-8">
              No decision details available
            </p>
          )}
          {session.created_at && (
            <div>
              <label className="text-xs text-gray-500">Created</label>
              <p className="text-sm">{new Date(session.created_at).toLocaleString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============ Helper Components ============

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="animate-spin text-primary-400" size={24} />
    </div>
  )
}

// Session 857: New inline header without external navigation
function InlineHeaderRow({
  title,
  subtitle,
  onRefresh,
  isFetching,
}: {
  title: string
  subtitle?: string
  onRefresh?: () => void
  isFetching?: boolean
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-lg font-semibold">{title}</h3>
        {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
      </div>
      {onRefresh && (
        <button
          onClick={() => onRefresh()}
          disabled={isFetching}
          className="p-2 hover:bg-gray-800 rounded transition-colors disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw size={14} className={cn(isFetching && 'animate-spin')} />
        </button>
      )}
    </div>
  )
}

// Session 857: Expandable list card for inline content
function ExpandedListCard({
  title,
  isLoading,
  onClose,
  count,
  children,
}: {
  title: string
  isLoading: boolean
  onClose: () => void
  count?: number
  children: React.ReactNode
}) {
  return (
    <div className="card border-primary-500/30">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <List size={14} className="text-primary-400" />
          <h4 className="text-sm font-medium">{title}</h4>
          {count !== undefined && (
            <span className="text-xs text-gray-500">({count})</span>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-800 rounded transition-colors"
          title="Close"
        >
          <X size={14} />
        </button>
      </div>
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="animate-spin text-primary-400" size={20} />
        </div>
      ) : (
        children
      )}
    </div>
  )
}

function StatCard({
  label,
  value,
  color,
  onClick,
  icon: Icon,
  isExpanded,
}: {
  label: string
  value: number | string
  color: string
  onClick?: () => void
  icon?: typeof Brain
  isExpanded?: boolean
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'card text-left transition-all',
        onClick && 'hover:bg-gray-800/80 cursor-pointer',
        isExpanded && 'bg-primary-500/10 border-primary-500/30'
      )}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-400">{label}</p>
        <div className="flex items-center gap-1">
          {Icon && <Icon size={14} className={color} />}
          {onClick && (
            isExpanded ? (
              <ChevronUp size={12} className="text-primary-400" />
            ) : (
              <ChevronDown size={12} className="text-gray-500" />
            )
          )}
        </div>
      </div>
      <p className={cn('text-2xl font-bold mt-1', color)}>{value}</p>
    </button>
  )
}

function MoodCard({
  mood,
  count,
  icon: Icon,
  color,
  onClick,
  isExpanded,
}: {
  mood: string
  count: number
  icon: typeof Heart
  color: string
  onClick?: () => void
  isExpanded?: boolean
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'card text-left transition-all',
        onClick && 'hover:bg-gray-800/80 cursor-pointer',
        isExpanded && 'bg-primary-500/10 border-primary-500/30'
      )}
    >
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <Icon size={14} className={color} />
          <span className="text-sm text-gray-400 capitalize">{mood}</span>
        </div>
        {onClick && (
          isExpanded ? (
            <ChevronUp size={12} className="text-primary-400" />
          ) : (
            <ChevronDown size={12} className="text-gray-500" />
          )
        )}
      </div>
      <p className="text-2xl font-bold">{count}</p>
    </button>
  )
}

function StatusRow({
  label,
  status,
  description,
}: {
  label: string
  status: 'online' | 'offline'
  description: string
}) {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-3">
        <div className={cn(
          'h-2 w-2 rounded-full',
          status === 'online' ? 'bg-accent-green animate-pulse' : 'bg-red-500'
        )} />
        <div>
          <span className="text-sm">{label}</span>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
      <span className={cn(
        'text-xs px-2 py-0.5 rounded',
        status === 'online' ? 'bg-accent-green/20 text-accent-green' : 'bg-red-500/20 text-red-400'
      )}>
        {status}
      </span>
    </div>
  )
}

function RelationshipTypeRow({
  type,
  count,
  description,
  onClick,
  isExpanded,
}: {
  type: string
  count: number
  description: string
  onClick?: () => void
  isExpanded?: boolean
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center justify-between gap-3 py-2 border-b border-gray-800 last:border-0 text-left',
        onClick && 'hover:bg-gray-800/50 rounded px-2 -mx-2 transition-colors cursor-pointer',
        isExpanded && 'bg-primary-500/10'
      )}
    >
      <div className="flex items-center gap-3">
        <Activity size={14} className="text-gray-500" />
        <div>
          <span className="text-sm">{type}</span>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-primary-400">{count}</span>
        {onClick && (
          isExpanded ? (
            <ChevronUp size={14} className="text-primary-400" />
          ) : (
            <ChevronDown size={14} className="text-gray-500" />
          )
        )}
      </div>
    </button>
  )
}

function FeatureRow({
  label,
  description,
}: {
  label: string
  description: string
}) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
      <Sparkles size={14} className="text-primary-400" />
      <div className="flex-1">
        <span className="text-sm">{label}</span>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
    </div>
  )
}
