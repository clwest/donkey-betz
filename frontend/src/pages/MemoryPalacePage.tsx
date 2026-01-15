/**
 * Session 716: Memory Palace Page
 * Session 718: Added Clusters tab for semantic memory grouping
 *
 * A visual interface for exploring and managing agent memories.
 * Memories are organized into "rooms" like a palace, with connections
 * between related memories.
 *
 * Features:
 * - Overview of all agents with memories
 * - Agent memory palace with rooms
 * - Memory search functionality
 * - Memory detail view with connections
 * - Create and connect memories
 * - Session 718: Memory Clusters - semantic grouping via embedding clustering
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Brain,
  Search,
  Home,
  BookOpen,
  Lightbulb,
  MessageSquare,
  Star,
  Link2,
  ChevronRight,
  ArrowLeft,
  Trash2,
  RefreshCw,
  Filter,
  Eye,
  Layers,
  Sparkles,
  Network,
  Play,
  CheckCircle,
  XCircle,
  Clock,
  ArrowUpDown,
  GitBranch,
  // Session 754: Phase 2 - Evolution Timeline icons
  Plus,
  GitMerge,
  TrendingUp,
  TrendingDown,
  History,
  // Session 754: Phase 2 - Connection Graph icons
  ArrowRight,
} from 'lucide-react'
import { memoryPalaceApi, memoryClustersApi } from '@/lib/api'
// Session 754: Phase 3 - Force-directed graph for cluster visualization
import ForceGraph2D from 'react-force-graph-2d'
import { cn } from '@/lib/cn'
import { CompactBreadcrumb } from '@/components/Breadcrumb'

// Types
interface Agent {
  id: string
  name: string
  memory_count: number
  avg_importance: number
}

interface Memory {
  id: string
  title: string
  content: string
  memory_type: string
  valence: string
  importance_score: number
  access_count?: number
  created_at: string
  source_type?: string
  // Session 753: Added fields for enhanced display
  memory_outcome?: 'success' | 'failure' | 'partial' | 'unknown'
  last_accessed_at?: string
  tags?: string[]
}

interface Room {
  id: string
  name: string
  room_type: string
  description: string
  color: string
  icon: string
  memory_count: number
  // Session 754: Phase 3 - Position for visual map
  position_x?: number
  position_y?: number
}

// Session 757: Execution data with full content from agent runs
interface ExecutionData {
  output_data: {
    result_preview?: string
    message?: string
    data?: {
      content?: string | Record<string, unknown>
      content_type?: string
      metadata?: Record<string, unknown>
      [key: string]: unknown
    }
  }
  status: string
  execution_time_ms?: number
  tokens_used?: number
  cost?: number
}

interface MemoryDetail extends Memory {
  agent_id: string
  agent_name: string
  context: string
  source_id?: string
  last_accessed_at?: string
  connected_memories: Array<{
    id: string
    title: string
    memory_type: string
  }>
  // Session 757: Include execution data with full content
  execution_data?: ExecutionData | null
}

interface Overview {
  total_memories: number
  agents_with_memories: number
  memory_types: Array<{ memory_type: string; count: number }>
}

// Session 718: Cluster types
// Session 753: Added parent_cluster field
interface Cluster {
  id: string
  name: string
  description: string
  keywords: string[]
  color: string
  icon: string
  coherence_score: number
  stability_score: number
  memory_count: number
  cluster_method: string
  version: number
  last_clustered_at: string | null
  created_at: string
  cluster_type?: string
  parent_cluster?: { id: string; name: string } | null
  top_memories?: Array<{
    id: string
    title: string
    memory_type: string
    similarity: number
    is_core: boolean
  }>
}

// Session 753: Related and sub cluster types
interface RelatedCluster {
  id: string
  name: string
  color: string
}

interface SubCluster extends RelatedCluster {
  memory_count: number
}

// Session 754: Phase 2 - Cluster Evolution types
interface ClusterEvolutionEvent {
  id: string
  event_type: 'created' | 'merged' | 'split' | 'grown' | 'shrunk' | 'dissolved'
  cluster_name: string | null
  details: Record<string, unknown>
  memories_before: number
  memories_after: number
  coherence_before: number
  coherence_after: number
  created_at: string
}

// Session 754: Phase 2 - Memory Connection types
interface MemoryConnection {
  id: string
  target_id?: string
  source_id?: string
  target_title?: string
  source_title?: string
  type: 'causal' | 'similar' | 'contrast' | 'elaborates' | 'temporal'
  strength: number
}

interface ClusterOverview {
  stats: {
    total_clusters: number
    agents_with_clusters: number
  }
  clusters_by_agent: Record<string, Cluster[]>
  // Session 746: Easy lookup for agent IDs by name
  agents_with_clusters_list?: Array<{
    id: string
    name: string
  }>
  agents_needing_clusters: Array<{
    id: string
    name: string
    memory_count: number
  }>
}

// Memory type icons and colors
const MEMORY_TYPE_CONFIG: Record<string, { icon: typeof Brain; color: string; bgColor: string }> = {
  interaction: { icon: MessageSquare, color: 'text-blue-400', bgColor: 'bg-blue-500/20' },
  learning: { icon: Lightbulb, color: 'text-yellow-400', bgColor: 'bg-yellow-500/20' },
  skill: { icon: Star, color: 'text-purple-400', bgColor: 'bg-purple-500/20' },
  knowledge: { icon: BookOpen, color: 'text-green-400', bgColor: 'bg-green-500/20' },
  experience: { icon: Brain, color: 'text-pink-400', bgColor: 'bg-pink-500/20' },
  success: { icon: Star, color: 'text-emerald-400', bgColor: 'bg-emerald-500/20' },
  failure: { icon: Brain, color: 'text-red-400', bgColor: 'bg-red-500/20' },
  insight: { icon: Lightbulb, color: 'text-amber-400', bgColor: 'bg-amber-500/20' },
  preference: { icon: MessageSquare, color: 'text-cyan-400', bgColor: 'bg-cyan-500/20' },
  default: { icon: Brain, color: 'text-gray-400', bgColor: 'bg-gray-500/20' },
}

// Valence colors
const VALENCE_COLORS: Record<string, string> = {
  positive: 'border-l-green-500',
  negative: 'border-l-red-500',
  neutral: 'border-l-gray-500',
}

// Room icons
const ROOM_ICONS: Record<string, typeof Home> = {
  library: BookOpen,
  workshop: Star,
  garden: Lightbulb,
  vault: Brain,
  default: Home,
}

export default function MemoryPalacePage() {
  const queryClient = useQueryClient()
  // Session 718: Tab state for Palace vs Clusters view
  const [activeTab, setActiveTab] = useState<'palace' | 'clusters'>('palace')
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)
  const [selectedMemory, setSelectedMemory] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<Memory[]>([])
  const [filterType, setFilterType] = useState<string>('')
  // Session 753: Outcome filter and sort options
  const [filterOutcome, setFilterOutcome] = useState<string>('')
  const [sortBy, setSortBy] = useState<string>('importance')
  // Session 754: Phase 2 - Tag filter
  const [filterTag, setFilterTag] = useState<string>('')
  // Session 718: Clusters state
  const [selectedClusterAgent, setSelectedClusterAgent] = useState<string | null>(null)
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null)
  // Session 754: Phase 2 & 3 - Clusters sub-tabs for Evolution Timeline and Visualization
  // Session 755: Phase 3 - Added 'find-similar' sub-tab
  const [clustersSubTab, setClustersSubTab] = useState<'clusters' | 'evolution' | 'visualization' | 'find-similar'>('clusters')
  // Session 755: Phase 3 - Find Similar Clusters state
  const [similarQuery, setSimilarQuery] = useState('')
  const [similarResults, setSimilarResults] = useState<Array<{
    id: string
    name: string
    description: string
    color: string
    similarity: number
    agent: string
    memory_count: number
  }>>([])
  const [isSearchingSimilar, setIsSearchingSimilar] = useState(false)
  // Session 754: Phase 3 - Room view mode (list or map)
  const [roomViewMode, setRoomViewMode] = useState<'list' | 'map'>('list')

  // Fetch overview
  const { data: overviewData, isLoading: loadingOverview } = useQuery({
    queryKey: ['memory-palace-overview'],
    queryFn: async () => {
      const res = await memoryPalaceApi.overview()
      return res.data as { success: boolean; overview: Overview; agents: Agent[] }
    },
    staleTime: 30000,
  })

  // Fetch agent rooms when agent selected
  const { data: roomsData, isLoading: loadingRooms } = useQuery({
    queryKey: ['memory-palace-rooms', selectedAgent?.id],
    queryFn: async () => {
      if (!selectedAgent) return null
      const res = await memoryPalaceApi.agentRooms(selectedAgent.id)
      return res.data as { success: boolean; rooms: Room[] }
    },
    enabled: !!selectedAgent,
  })

  // Fetch agent memories (all or filtered)
  // Session 753: Added outcome and sort_by parameters to query
  // Session 754: Added tag filter to query
  const { data: memoriesData, isLoading: loadingMemories } = useQuery({
    queryKey: ['memory-palace-memories', selectedAgent?.id, filterType, filterOutcome, sortBy, filterTag],
    queryFn: async () => {
      if (!selectedAgent) return null
      const params: { type?: string; outcome?: string; sort_by?: string; tag?: string; limit?: number } = { limit: 100 }
      if (filterType) params.type = filterType
      if (filterOutcome) params.outcome = filterOutcome
      if (sortBy) params.sort_by = sortBy
      if (filterTag) params.tag = filterTag
      const res = await memoryPalaceApi.agentMemories(selectedAgent.id, params)
      return res.data as { success: boolean; memories: Memory[] }
    },
    enabled: !!selectedAgent && !selectedRoom,
  })

  // Fetch room memories
  const { data: roomMemoriesData, isLoading: loadingRoomMemories } = useQuery({
    queryKey: ['memory-palace-room-memories', selectedRoom?.id],
    queryFn: async () => {
      if (!selectedRoom) return null
      const res = await memoryPalaceApi.roomMemories(selectedRoom.id)
      return res.data as { success: boolean; memories: Memory[] }
    },
    enabled: !!selectedRoom,
  })

  // Fetch memory detail
  const { data: memoryDetailData } = useQuery({
    queryKey: ['memory-palace-detail', selectedMemory],
    queryFn: async () => {
      if (!selectedMemory) return null
      const res = await memoryPalaceApi.memoryDetail(selectedMemory)
      return res.data as { success: boolean; memory: MemoryDetail }
    },
    enabled: !!selectedMemory,
  })

  // Session 754: Phase 2 - Fetch memory connections with types and strengths
  const { data: connectionsData, isLoading: loadingConnections } = useQuery<{
    success: boolean
    outgoing: MemoryConnection[]
    incoming: MemoryConnection[]
  } | null>({
    queryKey: ['memory-palace-connections', selectedMemory],
    queryFn: async () => {
      if (!selectedMemory) return null
      const res = await memoryPalaceApi.memoryConnections(selectedMemory)
      return res.data
    },
    enabled: !!selectedMemory,
  })

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: async (query: string) => {
      if (!selectedAgent || !query.trim()) return []
      const res = await memoryPalaceApi.searchMemories({
        agent_id: selectedAgent.id,
        query,
        limit: 20,
      })
      return res.data.memories as Memory[]
    },
    onSuccess: (data) => {
      setSearchResults(data)
      setIsSearching(false)
    },
  })

  // Delete memory mutation
  const deleteMutation = useMutation({
    mutationFn: async (memoryId: string) => {
      await memoryPalaceApi.deleteMemory(memoryId)
    },
    onSuccess: () => {
      setSelectedMemory(null)
      queryClient.invalidateQueries({ queryKey: ['memory-palace'] })
    },
  })

  // Session 718: Clusters queries
  const { data: clustersOverviewData, isLoading: loadingClustersOverview } = useQuery<{ success: boolean } & ClusterOverview>({
    queryKey: ['memory-clusters-overview'],
    queryFn: async () => {
      const res = await memoryClustersApi.overview()
      return res.data
    },
    enabled: activeTab === 'clusters',
    staleTime: 30000,
  })

  const { data: agentClustersData, isLoading: loadingAgentClusters } = useQuery<{ success: boolean; agent: { id: string; name: string }; clusters: Cluster[] }>({
    queryKey: ['memory-clusters-agent', selectedClusterAgent],
    queryFn: async () => {
      if (!selectedClusterAgent) return null
      const res = await memoryClustersApi.agentClusters(selectedClusterAgent)
      return res.data
    },
    enabled: activeTab === 'clusters' && !!selectedClusterAgent,
  })

  // Session 753: Enhanced cluster detail type with related/sub clusters
  interface ClusterDetailResponse {
    success: boolean
    cluster: Cluster & {
      agent: { id: string; name: string }
    }
    memories: Array<{
      id: string
      title: string
      content: string
      memory_type: string
      valence: string
      importance_score: number
      similarity_to_centroid: number
      is_core_member: boolean
      position_x: number
      position_y: number
      created_at: string
      memory_outcome?: string
    }>
    related_clusters: RelatedCluster[]
    sub_clusters: SubCluster[]
  }

  const { data: clusterDetailData, isLoading: loadingClusterDetail } = useQuery<ClusterDetailResponse | null>({
    queryKey: ['memory-cluster-detail', selectedCluster],
    queryFn: async () => {
      if (!selectedCluster) return null
      const res = await memoryClustersApi.detail(selectedCluster)
      return res.data as ClusterDetailResponse
    },
    enabled: activeTab === 'clusters' && !!selectedCluster,
  })

  // Session 754: Phase 2 - Cluster Evolution query
  const { data: evolutionData, isLoading: loadingEvolution } = useQuery<{
    success: boolean
    agent: { id: string; name: string }
    events: ClusterEvolutionEvent[]
  } | null>({
    queryKey: ['memory-cluster-evolution', selectedClusterAgent],
    queryFn: async () => {
      if (!selectedClusterAgent) return null
      const res = await memoryClustersApi.evolution(selectedClusterAgent)
      return res.data
    },
    enabled: activeTab === 'clusters' && !!selectedClusterAgent && clustersSubTab === 'evolution',
  })

  // Session 754: Phase 3 - Cluster Visualization query
  const { data: visualizationData, isLoading: loadingVisualization } = useQuery<{
    success: boolean
    nodes: Array<{
      id: string
      type: 'cluster' | 'memory'
      name: string
      color: string
      size: number
      coherence?: number
      memory_type?: string
      similarity?: number
      is_core?: boolean
    }>
    links: Array<{
      source: string
      target: string
      strength: number
      type?: string
    }>
  } | null>({
    queryKey: ['memory-cluster-visualization', selectedClusterAgent],
    queryFn: async () => {
      if (!selectedClusterAgent) return null
      const res = await memoryClustersApi.visualization(selectedClusterAgent)
      return res.data
    },
    enabled: activeTab === 'clusters' && !!selectedClusterAgent && clustersSubTab === 'visualization',
  })

  // Generate clusters mutation
  const generateClustersMutation = useMutation({
    mutationFn: async (agentId: string) => {
      const res = await memoryClustersApi.generateClusters(agentId)
      return res.data
    },
    onSuccess: () => {
      // Session 746: Invalidate all cluster-related queries to refresh UI
      queryClient.invalidateQueries({ queryKey: ['memory-clusters'] })
      queryClient.invalidateQueries({ queryKey: ['memory-clusters-overview'] })
      queryClient.invalidateQueries({ queryKey: ['memory-clusters-agent'] })
    },
  })

  // Session 755: Phase 3 - Find similar clusters mutation
  const findSimilarMutation = useMutation({
    mutationFn: async (query: string) => {
      const res = await memoryClustersApi.findSimilar({ query, limit: 10 })
      return res.data
    },
    onSuccess: (data) => {
      setSimilarResults(data.similar_clusters || [])
      setIsSearchingSimilar(false)
    },
    onError: () => {
      setIsSearchingSimilar(false)
    },
  })

  const handleFindSimilar = () => {
    if (similarQuery.trim()) {
      setIsSearchingSimilar(true)
      findSimilarMutation.mutate(similarQuery)
    }
  }

  const handleSearch = () => {
    if (searchQuery.trim() && selectedAgent) {
      setIsSearching(true)
      searchMutation.mutate(searchQuery)
    }
  }

  const handleBack = () => {
    if (selectedMemory) {
      setSelectedMemory(null)
    } else if (selectedRoom) {
      setSelectedRoom(null)
    } else if (selectedAgent) {
      setSelectedAgent(null)
      setSearchResults([])
      setSearchQuery('')
      setFilterType('')
      // Session 753: Reset new filters
      setFilterOutcome('')
      setSortBy('importance')
      // Session 754: Reset tag filter
      setFilterTag('')
    }
  }

  const getMemoryTypeConfig = (type: string) => {
    return MEMORY_TYPE_CONFIG[type] || MEMORY_TYPE_CONFIG.default
  }

  const getRoomIcon = (type: string) => {
    return ROOM_ICONS[type] || ROOM_ICONS.default
  }

  // Current memories to display
  const displayMemories = searchResults.length > 0
    ? searchResults
    : selectedRoom
      ? roomMemoriesData?.memories || []
      : memoriesData?.memories || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {activeTab === 'palace' && (selectedAgent || selectedRoom || selectedMemory) && (
            <button
              onClick={handleBack}
              className="p-2 hover:bg-dark-border rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-400" />
            </button>
          )}
          {activeTab === 'clusters' && (selectedClusterAgent || selectedCluster) && (
            <button
              onClick={() => {
                if (selectedCluster) setSelectedCluster(null)
                else if (selectedClusterAgent) setSelectedClusterAgent(null)
              }}
              className="p-2 hover:bg-dark-border rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-400" />
            </button>
          )}
          <div>
            <CompactBreadcrumb currentPage="Memory Palace" />
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Brain className="h-7 w-7 text-purple-400" />
              Memory Palace
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              {activeTab === 'palace'
                ? selectedMemory
                  ? 'Memory Detail'
                  : selectedRoom
                    ? `${selectedRoom.name} - ${selectedAgent?.name}`
                    : selectedAgent
                      ? `${selectedAgent.name}'s Memory Palace`
                      : 'Explore agent memories and knowledge'
                : selectedCluster
                  ? 'Cluster Detail'
                  : selectedClusterAgent
                    ? `${agentClustersData?.agent?.name || ''} Clusters`
                    : 'Semantic memory clustering'}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {selectedAgent && !selectedMemory && (
            <>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search memories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="pl-9 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm w-64 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={isSearching || !searchQuery.trim()}
                className="px-3 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50"
              >
                {isSearching ? <RefreshCw className="h-4 w-4 animate-spin" /> : 'Search'}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Session 718: Tab Navigation */}
      <div className="flex gap-2 border-b border-dark-border pb-4">
        <button
          onClick={() => {
            setActiveTab('palace')
            setSelectedClusterAgent(null)
            setSelectedCluster(null)
          }}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'palace'
              ? 'bg-purple-600 text-white'
              : 'text-gray-400 hover:bg-dark-bg hover:text-white'
          )}
        >
          <Home className="h-4 w-4" />
          Palace
        </button>
        <button
          onClick={() => {
            setActiveTab('clusters')
            setSelectedAgent(null)
            setSelectedRoom(null)
            setSelectedMemory(null)
            setSearchResults([])
          }}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'clusters'
              ? 'bg-purple-600 text-white'
              : 'text-gray-400 hover:bg-dark-bg hover:text-white'
          )}
        >
          <Layers className="h-4 w-4" />
          Clusters
        </button>
      </div>

      {/* Palace Tab Content */}
      {activeTab === 'palace' && (
        <>
          {/* Overview Stats */}
          {!selectedAgent && overviewData?.overview && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
            <div className="text-3xl font-bold text-purple-400">
              {overviewData.overview.total_memories.toLocaleString()}
            </div>
            <div className="text-sm text-gray-400">Total Memories</div>
          </div>
          <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
            <div className="text-3xl font-bold text-blue-400">
              {overviewData.overview.agents_with_memories}
            </div>
            <div className="text-sm text-gray-400">Agents with Memories</div>
          </div>
          <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
            <div className="text-3xl font-bold text-green-400">
              {overviewData.overview.memory_types.length}
            </div>
            <div className="text-sm text-gray-400">Memory Types</div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-12 gap-6">
        {/* Agent List / Room List Sidebar */}
        <div className="col-span-3">
          <div className="bg-dark-card rounded-lg border border-dark-border">
            <div className="p-4 border-b border-dark-border">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-white">
                  {selectedAgent ? 'Rooms' : 'Agents'}
                </h2>
                {/* Session 754: Phase 3 - Room view toggle */}
                {selectedAgent && (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setRoomViewMode('list')}
                      className={cn(
                        'p-1.5 rounded transition-colors',
                        roomViewMode === 'list'
                          ? 'bg-purple-600 text-white'
                          : 'text-gray-400 hover:bg-dark-bg'
                      )}
                      title="List view"
                    >
                      <Layers className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setRoomViewMode('map')}
                      className={cn(
                        'p-1.5 rounded transition-colors',
                        roomViewMode === 'map'
                          ? 'bg-purple-600 text-white'
                          : 'text-gray-400 hover:bg-dark-bg'
                      )}
                      title="Map view"
                    >
                      <Network className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
            <div className="max-h-[600px] overflow-y-auto">
              {!selectedAgent ? (
                // Agent list
                loadingOverview ? (
                  <div className="p-4 text-center text-gray-400">Loading agents...</div>
                ) : overviewData?.agents?.length === 0 ? (
                  <div className="p-4 text-center text-gray-400">No agents with memories</div>
                ) : (
                  overviewData?.agents?.map((agent) => (
                    <button
                      key={agent.id}
                      onClick={() => setSelectedAgent(agent)}
                      className="w-full p-4 text-left hover:bg-dark-bg border-b border-dark-border last:border-b-0 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-white">{agent.name}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            {agent.memory_count} memories
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="text-xs text-purple-400 bg-purple-500/20 px-2 py-1 rounded">
                            {agent.avg_importance.toFixed(1)}
                          </div>
                          <ChevronRight className="h-4 w-4 text-gray-500" />
                        </div>
                      </div>
                    </button>
                  ))
                )
              ) : (
                // Room list or map
                loadingRooms ? (
                  <div className="p-4 text-center text-gray-400">Loading rooms...</div>
                ) : roomViewMode === 'map' ? (
                  // Session 754: Phase 3 - Palace Room Map View
                  <PalaceRoomMap
                    rooms={roomsData?.rooms || []}
                    selectedRoom={selectedRoom}
                    onRoomClick={(room) => setSelectedRoom(room)}
                    getRoomIcon={getRoomIcon}
                  />
                ) : (
                  <>
                    {/* All Memories option */}
                    <button
                      onClick={() => setSelectedRoom(null)}
                      className={cn(
                        'w-full p-4 text-left hover:bg-dark-bg border-b border-dark-border transition-colors',
                        !selectedRoom && 'bg-purple-500/10'
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-purple-500/20 rounded-lg">
                          <Brain className="h-5 w-5 text-purple-400" />
                        </div>
                        <div>
                          <div className="font-medium text-white">All Memories</div>
                          <div className="text-xs text-gray-400">
                            {selectedAgent?.memory_count} total
                          </div>
                        </div>
                      </div>
                    </button>

                    {/* Room list */}
                    {roomsData?.rooms?.map((room) => {
                      const RoomIcon = getRoomIcon(room.room_type)
                      return (
                        <button
                          key={room.id}
                          onClick={() => setSelectedRoom(room)}
                          className={cn(
                            'w-full p-4 text-left hover:bg-dark-bg border-b border-dark-border last:border-b-0 transition-colors',
                            selectedRoom?.id === room.id && 'bg-purple-500/10'
                          )}
                        >
                          <div className="flex items-center gap-3">
                            <div
                              className="p-2 rounded-lg"
                              style={{ backgroundColor: room.color + '20' }}
                            >
                              <RoomIcon className="h-5 w-5" style={{ color: room.color }} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-white truncate">{room.name}</div>
                              <div className="text-xs text-gray-400">
                                {room.memory_count} memories
                              </div>
                            </div>
                            <ChevronRight className="h-4 w-4 text-gray-500 flex-shrink-0" />
                          </div>
                        </button>
                      )
                    })}
                  </>
                )
              )}
            </div>
          </div>

          {/* Filter by Type */}
          {selectedAgent && !selectedRoom && !selectedMemory && (
            <div className="mt-4 bg-dark-card rounded-lg border border-dark-border p-4 space-y-4">
              {/* Filter by Type */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Filter className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-300">Filter by Type</span>
                </div>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm text-white"
                >
                  <option value="">All Types</option>
                  <option value="success">Success</option>
                  <option value="failure">Failure</option>
                  <option value="insight">Insight</option>
                  <option value="preference">Preference</option>
                  <option value="interaction">Interaction</option>
                  <option value="learning">Learning</option>
                  <option value="skill">Skill</option>
                  <option value="knowledge">Knowledge</option>
                  <option value="experience">Experience</option>
                </select>
              </div>

              {/* Session 753: Filter by Outcome */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-300">Filter by Outcome</span>
                </div>
                <select
                  value={filterOutcome}
                  onChange={(e) => setFilterOutcome(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm text-white"
                >
                  <option value="">All Outcomes</option>
                  <option value="success">Success</option>
                  <option value="failure">Failure</option>
                  <option value="partial">Partial</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>

              {/* Session 753: Sort By */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <ArrowUpDown className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-300">Sort By</span>
                </div>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm text-white"
                >
                  <option value="importance">Importance</option>
                  <option value="recent">Most Recent</option>
                  <option value="accessed">Last Accessed</option>
                  <option value="access_count">Most Accessed</option>
                </select>
              </div>

              {/* Session 754: Phase 2 - Tag Filter */}
              <TagFilterSection
                memories={memoriesData?.memories || []}
                filterTag={filterTag}
                setFilterTag={setFilterTag}
              />
            </div>
          )}
        </div>

        {/* Memory List / Detail */}
        <div className="col-span-9">
          {selectedMemory && memoryDetailData?.memory ? (
            // Memory Detail View
            <MemoryDetailCard
              memory={memoryDetailData.memory}
              onDelete={() => deleteMutation.mutate(selectedMemory)}
              onViewConnected={(id) => setSelectedMemory(id)}
              isDeleting={deleteMutation.isPending}
              // Session 754: Phase 2 - Pass connections data
              connectionsData={connectionsData}
              loadingConnections={loadingConnections}
            />
          ) : selectedAgent ? (
            // Memory List View
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="p-4 border-b border-dark-border flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-white">
                    {searchResults.length > 0
                      ? `Search Results (${searchResults.length})`
                      : selectedRoom
                        ? `${selectedRoom.name}`
                        : 'All Memories'}
                  </h2>
                  {searchResults.length > 0 && (
                    <button
                      onClick={() => {
                        setSearchResults([])
                        setSearchQuery('')
                      }}
                      className="text-xs text-purple-400 hover:underline mt-1"
                    >
                      Clear search
                    </button>
                  )}
                </div>
                <div className="text-sm text-gray-400">
                  {displayMemories.length} memories
                </div>
              </div>

              {loadingMemories || loadingRoomMemories ? (
                <div className="p-8 text-center text-gray-400">
                  <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
                  Loading memories...
                </div>
              ) : displayMemories.length === 0 ? (
                <div className="p-8 text-center text-gray-400">
                  <Brain className="h-12 w-12 mx-auto mb-3 text-gray-600" />
                  <p>No memories found</p>
                  {searchQuery && (
                    <p className="text-sm mt-1">Try a different search term</p>
                  )}
                </div>
              ) : (
                <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                  {displayMemories.map((memory) => (
                    <MemoryCard
                      key={memory.id}
                      memory={memory}
                      onClick={() => setSelectedMemory(memory.id)}
                      // Session 754: Phase 2 - Tag click handler
                      onTagClick={(tag) => setFilterTag(tag)}
                    />
                  ))}
                </div>
              )}
            </div>
          ) : (
            // Welcome / Overview
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              <Brain className="h-16 w-16 mx-auto mb-4 text-purple-400/50" />
              <h2 className="text-xl font-semibold text-white mb-2">
                Welcome to the Memory Palace
              </h2>
              <p className="text-gray-400 max-w-md mx-auto">
                Select an agent from the list to explore their memories.
                Memories are organized into rooms based on type and can be
                searched semantically.
              </p>

              {overviewData?.overview?.memory_types && (
                <div className="mt-8">
                  <h3 className="text-sm font-medium text-gray-300 mb-4">
                    Memory Types Distribution
                  </h3>
                  <div className="flex flex-wrap justify-center gap-3">
                    {overviewData.overview.memory_types.map((type) => {
                      const config = getMemoryTypeConfig(type.memory_type)
                      const Icon = config.icon
                      return (
                        <div
                          key={type.memory_type}
                          className={cn(
                            'px-4 py-2 rounded-lg flex items-center gap-2',
                            config.bgColor
                          )}
                        >
                          <Icon className={cn('h-4 w-4', config.color)} />
                          <span className="text-sm font-medium text-white capitalize">
                            {type.memory_type}
                          </span>
                          <span className="text-xs text-gray-400">
                            ({type.count})
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
        </>
      )}

      {/* Session 718: Clusters Tab Content */}
      {activeTab === 'clusters' && (
        <ClustersTabContent
          clustersOverviewData={clustersOverviewData}
          loadingClustersOverview={loadingClustersOverview}
          agentClustersData={agentClustersData}
          loadingAgentClusters={loadingAgentClusters}
          clusterDetailData={clusterDetailData}
          loadingClusterDetail={loadingClusterDetail}
          selectedClusterAgent={selectedClusterAgent}
          setSelectedClusterAgent={setSelectedClusterAgent}
          selectedCluster={selectedCluster}
          setSelectedCluster={setSelectedCluster}
          generateClustersMutation={generateClustersMutation}
          getMemoryTypeConfig={getMemoryTypeConfig}
          // Session 754: Phase 2 - Evolution Timeline props
          clustersSubTab={clustersSubTab}
          setClustersSubTab={setClustersSubTab}
          evolutionData={evolutionData}
          loadingEvolution={loadingEvolution}
          // Session 754: Phase 3 - Visualization props
          visualizationData={visualizationData}
          loadingVisualization={loadingVisualization}
          // Session 755: Phase 3 - Find Similar props
          similarQuery={similarQuery}
          setSimilarQuery={setSimilarQuery}
          handleFindSimilar={handleFindSimilar}
          isSearchingSimilar={isSearchingSimilar}
          similarResults={similarResults}
        />
      )}
    </div>
  )
}

// Session 718: Clusters Tab Content Component
function ClustersTabContent({
  clustersOverviewData,
  loadingClustersOverview,
  agentClustersData,
  loadingAgentClusters,
  clusterDetailData,
  loadingClusterDetail,
  selectedClusterAgent,
  setSelectedClusterAgent,
  selectedCluster,
  setSelectedCluster,
  generateClustersMutation,
  getMemoryTypeConfig,
  // Session 754: Phase 2 - Evolution Timeline props
  clustersSubTab,
  setClustersSubTab,
  evolutionData,
  loadingEvolution,
  // Session 754: Phase 3 - Visualization props
  visualizationData,
  loadingVisualization,
  // Session 755: Phase 3 - Find Similar props
  similarQuery,
  setSimilarQuery,
  handleFindSimilar,
  isSearchingSimilar,
  similarResults,
}: {
  clustersOverviewData: ({ success: boolean } & ClusterOverview) | undefined
  loadingClustersOverview: boolean
  agentClustersData: { success: boolean; agent: { id: string; name: string }; clusters: Cluster[] } | undefined | null
  loadingAgentClusters: boolean
  // Session 753: Added related_clusters and sub_clusters
  clusterDetailData: {
    success: boolean
    cluster: Cluster & { agent: { id: string; name: string } }
    memories: Array<{
      id: string; title: string; content: string; memory_type: string
      valence: string; importance_score: number; similarity_to_centroid: number
      is_core_member: boolean; position_x: number; position_y: number
      created_at: string; memory_outcome?: string
    }>
    related_clusters?: RelatedCluster[]
    sub_clusters?: SubCluster[]
  } | undefined | null
  loadingClusterDetail: boolean
  selectedClusterAgent: string | null
  setSelectedClusterAgent: (id: string | null) => void
  selectedCluster: string | null
  setSelectedCluster: (id: string | null) => void
  generateClustersMutation: { mutate: (agentId: string) => void; isPending: boolean }
  getMemoryTypeConfig: (type: string) => { icon: typeof Brain; color: string; bgColor: string }
  // Session 754: Phase 2 - Evolution Timeline props
  // Session 755: Phase 3 - Added 'find-similar' to clustersSubTab
  clustersSubTab: 'clusters' | 'evolution' | 'visualization' | 'find-similar'
  setClustersSubTab: (tab: 'clusters' | 'evolution' | 'visualization' | 'find-similar') => void
  evolutionData: { success: boolean; agent: { id: string; name: string }; events: ClusterEvolutionEvent[] } | undefined | null
  loadingEvolution: boolean
  // Session 754: Phase 3 - Visualization props
  visualizationData?: {
    success: boolean
    nodes: Array<{
      id: string
      type: 'cluster' | 'memory'
      name: string
      color: string
      size: number
      coherence?: number
      memory_type?: string
      similarity?: number
      is_core?: boolean
    }>
    links: Array<{
      source: string
      target: string
      strength: number
      type?: string
    }>
  } | null
  loadingVisualization?: boolean
  // Session 755: Phase 3 - Find Similar props
  similarQuery: string
  setSimilarQuery: (query: string) => void
  handleFindSimilar: () => void
  isSearchingSimilar: boolean
  similarResults: Array<{
    id: string
    name: string
    description: string
    color: string
    similarity: number
    agent: string
    memory_count: number
  }>
}) {
  // Session 746: Filter state for memory outcomes
  const [outcomeFilter, setOutcomeFilter] = useState<'all' | 'failure' | 'success'>('all')

  if (loadingClustersOverview) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-purple-400" />
        <span className="ml-2 text-gray-400">Loading clusters...</span>
      </div>
    )
  }

  // Session 746: Loading state for cluster detail
  if (selectedCluster && loadingClusterDetail) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-purple-400" />
        <span className="ml-2 text-gray-400">Loading cluster details...</span>
      </div>
    )
  }

  // Cluster Detail View
  if (selectedCluster && clusterDetailData?.cluster) {
    const cluster = clusterDetailData.cluster
    const memories = clusterDetailData.memories || []
    // Session 753: Extract related and sub clusters
    const relatedClusters = clusterDetailData.related_clusters || []
    const subClusters = clusterDetailData.sub_clusters || []

    return (
      <div className="space-y-6">
        {/* Cluster Info Card */}
        <div className="bg-dark-card rounded-lg border border-dark-border p-6">
          <div className="flex items-start gap-4">
            <div
              className="p-4 rounded-xl"
              style={{ backgroundColor: cluster.color + '30' }}
            >
              <Network className="h-8 w-8" style={{ color: cluster.color }} />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-white">{cluster.name}</h2>
                {/* Session 746: Cluster type badge */}
                {cluster.cluster_type && cluster.cluster_type !== 'general' && (
                  <span className={cn(
                    'px-2 py-0.5 text-xs rounded font-medium',
                    cluster.cluster_type === 'failure_pattern' && 'bg-red-500/20 text-red-300',
                    cluster.cluster_type === 'success_pattern' && 'bg-green-500/20 text-green-300',
                    cluster.cluster_type === 'learning_pattern' && 'bg-blue-500/20 text-blue-300',
                    cluster.cluster_type === 'error_recovery' && 'bg-yellow-500/20 text-yellow-300',
                  )}>
                    {cluster.cluster_type.replace('_', ' ')}
                  </span>
                )}
              </div>
              <p className="text-gray-400 mt-1">{cluster.description}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                {cluster.keywords?.map((kw, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 bg-dark-bg rounded text-xs text-gray-300"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
            {/* Session 753: Coherence and Stability scores side by side */}
            <div className="flex items-center gap-6">
              <div className="text-right">
                <div className="text-2xl font-bold text-purple-400">
                  {(cluster.coherence_score * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-400">Coherence</div>
              </div>
              {cluster.stability_score > 0 && (
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-400">
                    {(cluster.stability_score * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-400">Stability</div>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4 mt-6 pt-4 border-t border-dark-border">
            <div>
              <div className="text-sm text-gray-400">Memories</div>
              <div className="text-lg font-semibold text-white">{memories.length}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Method</div>
              <div className="text-lg font-semibold text-white capitalize">{cluster.cluster_method}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Version</div>
              <div className="text-lg font-semibold text-white">v{cluster.version}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Agent</div>
              <div className="text-lg font-semibold text-white">{cluster.agent?.name || 'Cross-Agent'}</div>
            </div>
          </div>

          {/* Session 753: Parent cluster breadcrumb */}
          {cluster.parent_cluster && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <div className="flex items-center gap-2 text-sm">
                <GitBranch className="h-4 w-4 text-gray-400" />
                <span className="text-gray-400">Parent Cluster:</span>
                <button
                  onClick={() => setSelectedCluster(cluster.parent_cluster!.id)}
                  className="text-purple-400 hover:underline"
                >
                  {cluster.parent_cluster.name}
                </button>
              </div>
            </div>
          )}

          {/* Session 753: Sub-clusters section */}
          {subClusters.length > 0 && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <GitBranch className="h-4 w-4" />
                Sub-Clusters ({subClusters.length})
              </h4>
              <div className="grid grid-cols-3 gap-2">
                {subClusters.map(sub => (
                  <button
                    key={sub.id}
                    onClick={() => setSelectedCluster(sub.id)}
                    className="p-3 bg-dark-bg rounded-lg hover:bg-dark-border transition-colors text-left"
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: sub.color }}
                      />
                      <span className="text-sm font-medium text-white truncate">{sub.name}</span>
                    </div>
                    <span className="text-xs text-gray-500 mt-1">{sub.memory_count} memories</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Session 753: Related clusters section */}
          {relatedClusters.length > 0 && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <Link2 className="h-4 w-4" />
                Related Clusters ({relatedClusters.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {relatedClusters.map(rel => (
                  <button
                    key={rel.id}
                    onClick={() => setSelectedCluster(rel.id)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-dark-bg rounded-lg hover:bg-dark-border transition-colors"
                  >
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: rel.color }}
                    />
                    <span className="text-sm text-white">{rel.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Cluster Memories */}
        <div className="bg-dark-card rounded-lg border border-dark-border">
          <div className="p-4 border-b border-dark-border flex items-center justify-between">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-400" />
              Cluster Memories ({memories.length})
            </h3>
            <div className="flex items-center gap-4 text-sm">
              {/* Session 746: Outcome filter toggle */}
              <div className="flex items-center gap-1 bg-dark-bg rounded-lg p-0.5">
                <button
                  onClick={() => setOutcomeFilter('all')}
                  className={cn(
                    'px-2 py-1 rounded text-xs transition-colors',
                    outcomeFilter === 'all' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
                  )}
                >
                  All
                </button>
                <button
                  onClick={() => setOutcomeFilter('failure')}
                  className={cn(
                    'px-2 py-1 rounded text-xs transition-colors',
                    outcomeFilter === 'failure' ? 'bg-red-600 text-white' : 'text-gray-400 hover:text-white'
                  )}
                >
                  Failures
                </button>
                <button
                  onClick={() => setOutcomeFilter('success')}
                  className={cn(
                    'px-2 py-1 rounded text-xs transition-colors',
                    outcomeFilter === 'success' ? 'bg-green-600 text-white' : 'text-gray-400 hover:text-white'
                  )}
                >
                  Successes
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Core members:</span>
                <span className="text-purple-400 font-medium">
                  {memories.filter(m => m.is_core_member).length}
                </span>
              </div>
            </div>
          </div>
          <div className="divide-y divide-dark-border max-h-[500px] overflow-y-auto">
            {memories
              .filter(m => outcomeFilter === 'all' || m.memory_outcome === outcomeFilter)
              .map((memory) => {
              const config = getMemoryTypeConfig(memory.memory_type)
              const Icon = config.icon
              return (
                <div
                  key={memory.id}
                  className={cn(
                    'p-4 border-l-4',
                    memory.valence === 'positive' ? 'border-l-green-500' : memory.valence === 'negative' ? 'border-l-red-500' : 'border-l-gray-500'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className={cn('p-2 rounded-lg', config.bgColor)}>
                      <Icon className={cn('h-4 w-4', config.color)} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-white truncate">{memory.title}</h4>
                        {memory.is_core_member && (
                          <span className="px-1.5 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded">
                            Core
                          </span>
                        )}
                        {/* Session 746: Memory outcome badge */}
                        {memory.memory_outcome && memory.memory_outcome !== 'unknown' && (
                          <span className={cn(
                            'px-1.5 py-0.5 text-xs rounded',
                            memory.memory_outcome === 'failure' && 'bg-red-500/20 text-red-300',
                            memory.memory_outcome === 'success' && 'bg-green-500/20 text-green-300',
                            memory.memory_outcome === 'partial' && 'bg-yellow-500/20 text-yellow-300',
                          )}>
                            {memory.memory_outcome}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-400 mt-1 line-clamp-2">{memory.content}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span className="capitalize">{memory.memory_type}</span>
                        <span>Similarity: {(memory.similarity_to_centroid * 100).toFixed(0)}%</span>
                        <span>Importance: {(memory.importance_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    )
  }

  // Agent Clusters View
  if (selectedClusterAgent && agentClustersData) {
    const clusters = agentClustersData.clusters || []

    return (
      <div className="space-y-6">
        {/* Agent Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">{agentClustersData.agent.name}</h2>
            <p className="text-gray-400">{clusters.length} clusters</p>
          </div>
          <button
            onClick={() => generateClustersMutation.mutate(selectedClusterAgent)}
            disabled={generateClustersMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50"
          >
            {generateClustersMutation.isPending ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            Regenerate Clusters
          </button>
        </div>

        {/* Session 754: Phase 2 - Sub-tabs for Clusters and Evolution */}
        <div className="flex gap-2 border-b border-dark-border pb-3">
          <button
            onClick={() => setClustersSubTab('clusters')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              clustersSubTab === 'clusters'
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:bg-dark-bg hover:text-white'
            )}
          >
            <Network className="h-4 w-4" />
            Clusters
          </button>
          <button
            onClick={() => setClustersSubTab('evolution')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              clustersSubTab === 'evolution'
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:bg-dark-bg hover:text-white'
            )}
          >
            <History className="h-4 w-4" />
            Evolution
          </button>
          {/* Session 754: Phase 3 - Visualization tab */}
          <button
            onClick={() => setClustersSubTab('visualization')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              clustersSubTab === 'visualization'
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:bg-dark-bg hover:text-white'
            )}
          >
            <Sparkles className="h-4 w-4" />
            Visualization
          </button>
          {/* Session 755: Phase 3 - Find Similar tab */}
          <button
            onClick={() => setClustersSubTab('find-similar')}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              clustersSubTab === 'find-similar'
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:bg-dark-bg hover:text-white'
            )}
          >
            <Search className="h-4 w-4" />
            Find Similar
          </button>
        </div>

        {/* Session 754: Phase 2 - Evolution Timeline View */}
        {clustersSubTab === 'evolution' && (
          <EvolutionTimeline
            evolutionData={evolutionData}
            loadingEvolution={loadingEvolution}
          />
        )}

        {/* Session 754: Phase 3 - Visualization View */}
        {clustersSubTab === 'visualization' && (
          <ClusterVisualizationGraph
            visualizationData={visualizationData}
            loadingVisualization={loadingVisualization}
            onNodeClick={(nodeId) => {
              // Navigate to cluster or memory detail
              if (nodeId.startsWith('cluster_')) {
                const clusterId = nodeId.replace('cluster_', '')
                setSelectedCluster(clusterId)
                setClustersSubTab('clusters')
              }
            }}
          />
        )}

        {/* Session 755: Phase 3 - Find Similar View */}
        {clustersSubTab === 'find-similar' && (
          <FindSimilarClusters
            similarQuery={similarQuery}
            setSimilarQuery={setSimilarQuery}
            handleFindSimilar={handleFindSimilar}
            isSearchingSimilar={isSearchingSimilar}
            similarResults={similarResults}
            onClusterClick={(clusterId) => {
              setSelectedCluster(clusterId)
              setClustersSubTab('clusters')
            }}
          />
        )}

        {/* Clusters View */}
        {clustersSubTab === 'clusters' && (loadingAgentClusters ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-6 w-6 animate-spin text-purple-400" />
          </div>
        ) : clusters.length === 0 ? (
          <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
            <Layers className="h-12 w-12 mx-auto mb-4 text-gray-500" />
            <h3 className="text-lg font-medium text-white mb-2">No Clusters Yet</h3>
            <p className="text-gray-400 mb-4">
              Click "Regenerate Clusters" to create semantic clusters from this agent's memories.
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clusters.map((cluster) => (
              <button
                key={cluster.id}
                onClick={() => setSelectedCluster(cluster.id)}
                className="bg-dark-card rounded-lg border border-dark-border p-4 text-left hover:bg-dark-bg transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div
                    className="p-2 rounded-lg"
                    style={{ backgroundColor: cluster.color + '30' }}
                  >
                    <Network className="h-5 w-5" style={{ color: cluster.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-white truncate">{cluster.name}</h3>
                    <p className="text-xs text-gray-400 mt-1 line-clamp-2">{cluster.description}</p>
                  </div>
                </div>
                {/* Session 753: Enhanced cluster metrics with stability score */}
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-dark-border">
                  <span className="text-sm text-gray-400">{cluster.memory_count} memories</span>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-purple-400">
                      {(cluster.coherence_score * 100).toFixed(0)}% coherent
                    </span>
                    {cluster.stability_score > 0 && (
                      <span className="text-sm text-blue-400">
                        {(cluster.stability_score * 100).toFixed(0)}% stable
                      </span>
                    )}
                  </div>
                </div>
                {cluster.keywords && cluster.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {cluster.keywords.slice(0, 3).map((kw, i) => (
                      <span
                        key={i}
                        className="px-1.5 py-0.5 bg-dark-bg rounded text-xs text-gray-400"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                )}
              </button>
            ))}
          </div>
        ))}
      </div>
    )
  }

  // Overview View
  return (
    <div className="space-y-6">
      {/* Stats */}
      {clustersOverviewData?.stats && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
            <div className="text-3xl font-bold text-purple-400">
              {clustersOverviewData.stats.total_clusters}
            </div>
            <div className="text-sm text-gray-400">Total Clusters</div>
          </div>
          <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
            <div className="text-3xl font-bold text-blue-400">
              {clustersOverviewData.stats.agents_with_clusters}
            </div>
            <div className="text-sm text-gray-400">Agents with Clusters</div>
          </div>
        </div>
      )}

      {/* Agents with Clusters */}
      {clustersOverviewData?.clusters_by_agent && (
        <div className="bg-dark-card rounded-lg border border-dark-border">
          <div className="p-4 border-b border-dark-border">
            <h2 className="font-semibold text-white flex items-center gap-2">
              <Layers className="h-5 w-5 text-purple-400" />
              Agents with Clusters
            </h2>
          </div>
          <div className="divide-y divide-dark-border max-h-[400px] overflow-y-auto">
            {Object.entries(clustersOverviewData.clusters_by_agent).map(([agentName, clusters]) => (
              <button
                key={agentName}
                onClick={() => {
                  // Session 746: Look up agent ID from agents_with_clusters_list
                  const agentInfo = clustersOverviewData.agents_with_clusters_list?.find(a => a.name === agentName)
                  if (agentInfo?.id) {
                    setSelectedClusterAgent(agentInfo.id)
                  } else {
                    // Fallback to agent_id in cluster data
                    const firstCluster = clusters[0] as Cluster & { agent_id?: string }
                    if (firstCluster?.agent_id) {
                      setSelectedClusterAgent(firstCluster.agent_id)
                    } else {
                      console.warn('Could not find agent_id for:', agentName)
                    }
                  }
                }}
                className="w-full p-4 text-left hover:bg-dark-bg transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-white">{agentName}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {clusters.length} clusters, {clusters.reduce((sum, c) => sum + c.memory_count, 0)} memories
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex -space-x-1">
                      {clusters.slice(0, 4).map((cluster) => (
                        <div
                          key={cluster.id}
                          className="w-6 h-6 rounded-full border-2 border-dark-card"
                          style={{ backgroundColor: cluster.color }}
                          title={cluster.name}
                        />
                      ))}
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-500" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Agents Needing Clusters */}
      {clustersOverviewData?.agents_needing_clusters && clustersOverviewData.agents_needing_clusters.length > 0 && (
        <div className="bg-dark-card rounded-lg border border-dark-border">
          <div className="p-4 border-b border-dark-border">
            <h2 className="font-semibold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-yellow-400" />
              Ready for Clustering
            </h2>
            <p className="text-xs text-gray-400 mt-1">
              Agents with 5+ memories that don't have clusters yet
            </p>
          </div>
          <div className="divide-y divide-dark-border">
            {clustersOverviewData.agents_needing_clusters.map((agent) => (
              <div
                key={agent.id}
                className="p-4 flex items-center justify-between"
              >
                <div>
                  <div className="font-medium text-white">{agent.name}</div>
                  <div className="text-xs text-gray-400">{agent.memory_count} memories</div>
                </div>
                <button
                  onClick={() => generateClustersMutation.mutate(agent.id)}
                  disabled={generateClustersMutation.isPending}
                  className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50"
                >
                  {generateClustersMutation.isPending ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  Generate
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info */}
      <div className="bg-dark-card rounded-lg border border-dark-border p-4">
        <h3 className="font-medium text-white flex items-center gap-2 mb-2">
          <Brain className="h-5 w-5 text-purple-400" />
          About Memory Clusters
        </h3>
        <p className="text-sm text-gray-400">
          Memory Clusters use embedding-based semantic clustering to automatically discover
          related memories. Unlike manual room organization, clusters emerge from the
          content similarity of memories, revealing hidden patterns and connections.
        </p>
      </div>
    </div>
  )
}

// Memory Card Component
// Session 754: Added onTagClick prop for clickable tags
function MemoryCard({ memory, onClick, onTagClick }: { memory: Memory; onClick: () => void; onTagClick?: (tag: string) => void }) {
  const config = MEMORY_TYPE_CONFIG[memory.memory_type] || MEMORY_TYPE_CONFIG.default
  const Icon = config.icon
  const valenceColor = VALENCE_COLORS[memory.valence] || VALENCE_COLORS.neutral

  // Session 753: Outcome badge configuration
  const getOutcomeBadge = (outcome?: string) => {
    if (!outcome || outcome === 'unknown') return null
    const config: Record<string, { icon: typeof CheckCircle; color: string; bg: string; label: string }> = {
      success: { icon: CheckCircle, color: 'text-green-300', bg: 'bg-green-500/20', label: 'Success' },
      failure: { icon: XCircle, color: 'text-red-300', bg: 'bg-red-500/20', label: 'Failure' },
      partial: { icon: Clock, color: 'text-yellow-300', bg: 'bg-yellow-500/20', label: 'Partial' },
    }
    return config[outcome]
  }

  const outcomeBadge = getOutcomeBadge(memory.memory_outcome)

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      className={cn(
        'w-full p-4 text-left hover:bg-dark-bg transition-colors border-l-4 cursor-pointer',
        valenceColor
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn('p-2 rounded-lg flex-shrink-0', config.bgColor)}>
          <Icon className={cn('h-4 w-4', config.color)} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <h3 className="font-medium text-white truncate">{memory.title}</h3>
              {/* Session 753: Outcome badge */}
              {outcomeBadge && (
                <span className={cn('px-1.5 py-0.5 text-xs rounded flex items-center gap-1 flex-shrink-0', outcomeBadge.bg)}>
                  <outcomeBadge.icon className={cn('h-3 w-3', outcomeBadge.color)} />
                  <span className={outcomeBadge.color}>{outcomeBadge.label}</span>
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className="text-xs text-purple-400 bg-purple-500/20 px-2 py-0.5 rounded">
                {(memory.importance_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-1 line-clamp-2">{memory.content}</p>
          {/* Session 753: Tags display - Session 754: Made clickable */}
          {memory.tags && memory.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {memory.tags.slice(0, 3).map((tag, i) => (
                <button
                  key={i}
                  onClick={(e) => {
                    e.stopPropagation()
                    onTagClick?.(tag)
                  }}
                  className="px-1.5 py-0.5 bg-dark-bg rounded text-xs text-gray-400 hover:bg-purple-600/30 hover:text-purple-300 transition-colors"
                >
                  #{tag}
                </button>
              ))}
              {memory.tags.length > 3 && (
                <span className="text-xs text-gray-500">+{memory.tags.length - 3}</span>
              )}
            </div>
          )}
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            <span className="capitalize">{memory.memory_type}</span>
            <span>{new Date(memory.created_at).toLocaleDateString()}</span>
            {memory.access_count !== undefined && (
              <span className="flex items-center gap-1">
                <Eye className="h-3 w-3" />
                {memory.access_count}
              </span>
            )}
            {/* Session 753: Last accessed display */}
            {memory.last_accessed_at && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {new Date(memory.last_accessed_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-gray-600 flex-shrink-0 mt-1" />
      </div>
    </div>
  )
}

// Session 757: Component to display execution content (blog posts, generated content, etc.)
function ExecutionContentDisplay({ executionData }: { executionData: ExecutionData }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const data = executionData.output_data?.data

  if (!data) return null

  // Handle different content types
  const contentType = data.content_type || 'unknown'
  const content = data.content
  // Session 757: Handle new conversation format with 'response' field
  const response = (data as Record<string, unknown>).response as string | undefined
  const query = (data as Record<string, unknown>).query as string | undefined

  // Render content based on type
  const renderContent = () => {
    // Session 757: Handle conversation responses (response field instead of content)
    if (response) {
      return (
        <div className="space-y-4">
          {query ? (
            <div className="mb-3 pb-3 border-b border-dark-border">
              <h4 className="text-xs font-medium text-gray-500 uppercase mb-1">Query</h4>
              <p className="text-gray-400 text-sm">{query}</p>
            </div>
          ) : null}
          <div>
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-1">Response</h4>
            <div className="text-gray-300 whitespace-pre-wrap">{response}</div>
          </div>
        </div>
      )
    }

    if (!content) return <p className="text-gray-400 italic">No content available</p>

    // If content is a string, display it directly
    if (typeof content === 'string') {
      return <p className="text-gray-300 whitespace-pre-wrap">{content}</p>
    }

    // If content is an object (like a blog post with structure)
    if (typeof content === 'object') {
      const contentObj = content as Record<string, unknown>
      const hasIntro = 'intro' in contentObj && contentObj.intro
      const hasBody = 'body' in contentObj && contentObj.body
      const hasConclusion = 'conclusion' in contentObj && contentObj.conclusion
      const hasTags = 'tags' in contentObj && Array.isArray(contentObj.tags)

      return (
        <div className="space-y-4">
          {/* Blog-style content with intro, body, etc. */}
          {hasIntro ? (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-1">Introduction</h4>
              <p className="text-gray-300">{String(contentObj.intro)}</p>
            </div>
          ) : null}
          {hasBody ? (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-1">Body</h4>
              <div className="text-gray-300 whitespace-pre-wrap">{String(contentObj.body)}</div>
            </div>
          ) : null}
          {hasConclusion ? (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-1">Conclusion</h4>
              <p className="text-gray-300">{String(contentObj.conclusion)}</p>
            </div>
          ) : null}
          {/* Tags */}
          {hasTags ? (
            <div className="flex flex-wrap gap-2">
              {(contentObj.tags as string[]).slice(0, 10).map((tag, i) => (
                <span key={i} className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                  {tag}
                </span>
              ))}
            </div>
          ) : null}
          {/* Fallback: show raw JSON for other structured content */}
          {!hasIntro && !hasBody ? (
            <pre className="text-xs text-gray-400 bg-dark-bg p-3 rounded overflow-x-auto max-h-96">
              {JSON.stringify(content, null, 2)}
            </pre>
          ) : null}
        </div>
      )
    }

    return <p className="text-gray-400">Unable to display content</p>
  }

  return (
    <div className="mb-4 border border-green-500/30 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 bg-green-500/10 hover:bg-green-500/20 transition-colors"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-green-400" />
          <span className="font-medium text-green-400">Generated Content</span>
          <span className="text-sm text-gray-400 capitalize">({contentType})</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-gray-400">
          {executionData.tokens_used && (
            <span>{executionData.tokens_used.toLocaleString()} tokens</span>
          )}
          {executionData.cost && (
            <span>${executionData.cost.toFixed(4)}</span>
          )}
          <ChevronRight className={cn('h-5 w-5 transition-transform', isExpanded && 'rotate-90')} />
        </div>
      </button>
      {isExpanded && (
        <div className="p-4 bg-dark-bg border-t border-green-500/30">
          {renderContent()}
          {/* Metadata section */}
          {data.metadata && Object.keys(data.metadata).length > 0 && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <h4 className="text-sm font-medium text-gray-400 mb-2">Metadata</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {Object.entries(data.metadata).map(([key, value]) => (
                  <div key={key}>
                    <span className="text-gray-500">{key}: </span>
                    <span className="text-gray-300">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Memory Detail Card Component
function MemoryDetailCard({
  memory,
  onDelete,
  onViewConnected,
  isDeleting,
  // Session 754: Phase 2 - Connection Graph props
  connectionsData,
  loadingConnections,
}: {
  memory: MemoryDetail
  onDelete: () => void
  onViewConnected: (id: string) => void
  isDeleting: boolean
  // Session 754: Phase 2 - Connection Graph props
  connectionsData?: { success: boolean; outgoing: MemoryConnection[]; incoming: MemoryConnection[] } | null
  loadingConnections?: boolean
}) {
  const config = MEMORY_TYPE_CONFIG[memory.memory_type] || MEMORY_TYPE_CONFIG.default
  const Icon = config.icon
  const valenceColor = VALENCE_COLORS[memory.valence] || VALENCE_COLORS.neutral

  return (
    <div className="space-y-4">
      {/* Main Card */}
      <div className={cn('bg-dark-card rounded-lg border border-dark-border border-l-4', valenceColor)}>
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={cn('p-3 rounded-lg', config.bgColor)}>
                <Icon className={cn('h-6 w-6', config.color)} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">{memory.title}</h2>
                <div className="flex items-center gap-2 mt-1 text-sm text-gray-400">
                  <span className="capitalize">{memory.memory_type}</span>
                  <span>from {memory.agent_name}</span>
                </div>
              </div>
            </div>
            <button
              onClick={onDelete}
              disabled={isDeleting}
              className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors disabled:opacity-50"
              title="Delete memory"
            >
              {isDeleting ? (
                <RefreshCw className="h-5 w-5 animate-spin" />
              ) : (
                <Trash2 className="h-5 w-5" />
              )}
            </button>
          </div>

          {/* Content */}
          <div className="bg-dark-bg rounded-lg p-4 mb-4">
            <p className="text-gray-300 whitespace-pre-wrap">{memory.content}</p>
          </div>

          {/* Session 757: Generated Content from Execution */}
          {memory.execution_data?.output_data?.data && (
            <ExecutionContentDisplay executionData={memory.execution_data} />
          )}

          {/* Context */}
          {memory.context && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-300 mb-2">Context</h3>
              <p className="text-sm text-gray-400">{memory.context}</p>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-dark-border">
            <div>
              <div className="text-xs text-gray-500 uppercase">Importance</div>
              <div className="text-lg font-semibold text-purple-400">
                {(memory.importance_score * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase">Valence</div>
              <div className="text-lg font-semibold text-white capitalize">{memory.valence}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase">Access Count</div>
              <div className="text-lg font-semibold text-white">{memory.access_count}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase">Created</div>
              <div className="text-sm font-medium text-white">
                {new Date(memory.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Source Info */}
          {memory.source_type && (
            <div className="mt-4 pt-4 border-t border-dark-border">
              <div className="text-xs text-gray-500">
                Source: {memory.source_type}
                {memory.source_id && ` (${memory.source_id})`}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Session 754: Phase 2 - Enhanced Memory Connection Graph */}
      <MemoryConnectionGraph
        connectionsData={connectionsData}
        loadingConnections={loadingConnections}
        fallbackConnections={memory.connected_memories}
        onViewConnected={onViewConnected}
      />
    </div>
  )
}

// Session 754: Phase 2 - Memory Connection Graph Component
function MemoryConnectionGraph({
  connectionsData,
  loadingConnections,
  fallbackConnections,
  onViewConnected,
}: {
  connectionsData?: { success: boolean; outgoing: MemoryConnection[]; incoming: MemoryConnection[] } | null
  loadingConnections?: boolean
  fallbackConnections?: Array<{ id: string; title: string; memory_type: string }>
  onViewConnected: (id: string) => void
}) {
  // Connection type configuration
  const getConnectionTypeConfig = (type: string) => {
    const configs: Record<string, { color: string; bgColor: string; label: string; description: string }> = {
      causal: { color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Caused', description: 'This memory caused or led to' },
      similar: { color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Similar', description: 'Similar in content or context' },
      contrast: { color: 'text-red-400', bgColor: 'bg-red-500/20', label: 'Contrasts', description: 'Contrasting or opposing view' },
      elaborates: { color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Expands', description: 'Elaborates or expands on' },
      temporal: { color: 'text-gray-400', bgColor: 'bg-gray-500/20', label: 'Follows', description: 'Happened after in time' },
    }
    return configs[type] || configs.similar
  }

  // Get strength label
  const getStrengthLabel = (strength: number) => {
    if (strength >= 0.7) return { label: 'Strong', color: 'text-green-400' }
    if (strength >= 0.4) return { label: 'Moderate', color: 'text-yellow-400' }
    return { label: 'Weak', color: 'text-gray-400' }
  }

  // Use enhanced connections if available, otherwise use fallback
  const hasEnhancedConnections = connectionsData?.success && (connectionsData.outgoing?.length > 0 || connectionsData.incoming?.length > 0)
  const hasFallbackConnections = fallbackConnections && fallbackConnections.length > 0

  if (loadingConnections) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-4">
        <div className="flex items-center justify-center py-4">
          <RefreshCw className="h-5 w-5 animate-spin text-purple-400" />
          <span className="ml-2 text-gray-400">Loading connections...</span>
        </div>
      </div>
    )
  }

  if (!hasEnhancedConnections && !hasFallbackConnections) {
    return null
  }

  // If we have enhanced connection data
  if (hasEnhancedConnections && connectionsData) {
    const outgoing = connectionsData.outgoing || []
    const incoming = connectionsData.incoming || []
    const totalConnections = outgoing.length + incoming.length

    return (
      <div className="bg-dark-card rounded-lg border border-dark-border">
        <div className="p-4 border-b border-dark-border">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Link2 className="h-5 w-5 text-purple-400" />
            Memory Connections ({totalConnections})
          </h3>
        </div>

        <div className="grid md:grid-cols-2 gap-4 p-4">
          {/* Outgoing Connections */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 flex items-center gap-2 mb-3">
              <ArrowRight className="h-4 w-4" />
              Leads To ({outgoing.length})
            </h4>
            {outgoing.length === 0 ? (
              <p className="text-xs text-gray-500 italic">No outgoing connections</p>
            ) : (
              <div className="space-y-2">
                {outgoing.map((conn) => {
                  const typeConfig = getConnectionTypeConfig(conn.type)
                  const strengthConfig = getStrengthLabel(conn.strength)

                  return (
                    <button
                      key={conn.id}
                      onClick={() => conn.target_id && onViewConnected(conn.target_id)}
                      className="w-full p-3 text-left hover:bg-dark-bg rounded-lg border border-dark-border transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-white text-sm truncate flex-1">
                          {conn.target_title}
                        </span>
                        <ChevronRight className="h-4 w-4 text-gray-500 ml-2 flex-shrink-0" />
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={cn('px-1.5 py-0.5 rounded text-xs', typeConfig.bgColor, typeConfig.color)}>
                          {typeConfig.label}
                        </span>
                        <div className="flex items-center gap-1">
                          <div className="w-16 h-1.5 bg-dark-border rounded-full overflow-hidden">
                            <div
                              className="h-full bg-purple-500 rounded-full"
                              style={{ width: `${conn.strength * 100}%` }}
                            />
                          </div>
                          <span className={cn('text-xs', strengthConfig.color)}>
                            {strengthConfig.label}
                          </span>
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          {/* Incoming Connections */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 flex items-center gap-2 mb-3">
              <ArrowLeft className="h-4 w-4" />
              Comes From ({incoming.length})
            </h4>
            {incoming.length === 0 ? (
              <p className="text-xs text-gray-500 italic">No incoming connections</p>
            ) : (
              <div className="space-y-2">
                {incoming.map((conn) => {
                  const typeConfig = getConnectionTypeConfig(conn.type)
                  const strengthConfig = getStrengthLabel(conn.strength)

                  return (
                    <button
                      key={conn.id}
                      onClick={() => conn.source_id && onViewConnected(conn.source_id)}
                      className="w-full p-3 text-left hover:bg-dark-bg rounded-lg border border-dark-border transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-white text-sm truncate flex-1">
                          {conn.source_title}
                        </span>
                        <ChevronRight className="h-4 w-4 text-gray-500 ml-2 flex-shrink-0" />
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={cn('px-1.5 py-0.5 rounded text-xs', typeConfig.bgColor, typeConfig.color)}>
                          {typeConfig.label}
                        </span>
                        <div className="flex items-center gap-1">
                          <div className="w-16 h-1.5 bg-dark-border rounded-full overflow-hidden">
                            <div
                              className="h-full bg-purple-500 rounded-full"
                              style={{ width: `${conn.strength * 100}%` }}
                            />
                          </div>
                          <span className={cn('text-xs', strengthConfig.color)}>
                            {strengthConfig.label}
                          </span>
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Connection Type Legend */}
        <div className="px-4 pb-4 pt-2 border-t border-dark-border">
          <div className="text-xs text-gray-500 mb-2">Connection Types:</div>
          <div className="flex flex-wrap gap-2">
            {['causal', 'similar', 'contrast', 'elaborates', 'temporal'].map((type) => {
              const config = getConnectionTypeConfig(type)
              return (
                <span key={type} className={cn('px-2 py-1 rounded text-xs', config.bgColor, config.color)}>
                  {config.label}
                </span>
              )
            })}
          </div>
        </div>
      </div>
    )
  }

  // Fallback to simple connected memories list
  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
        <Link2 className="h-5 w-5 text-purple-400" />
        Connected Memories ({fallbackConnections?.length || 0})
      </h3>
      <div className="space-y-2">
        {fallbackConnections?.map((connected) => {
          const connConfig = MEMORY_TYPE_CONFIG[connected.memory_type] || MEMORY_TYPE_CONFIG.default
          const ConnIcon = connConfig.icon
          return (
            <button
              key={connected.id}
              onClick={() => onViewConnected(connected.id)}
              className="w-full p-3 text-left hover:bg-dark-bg rounded-lg border border-dark-border transition-colors flex items-center gap-3"
            >
              <div className={cn('p-2 rounded-lg', connConfig.bgColor)}>
                <ConnIcon className={cn('h-4 w-4', connConfig.color)} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-white truncate">{connected.title}</div>
                <div className="text-xs text-gray-500 capitalize">{connected.memory_type}</div>
              </div>
              <ChevronRight className="h-4 w-4 text-gray-500" />
            </button>
          )
        })}
      </div>
    </div>
  )
}

// Session 754: Phase 2 - Evolution Timeline Component
function EvolutionTimeline({
  evolutionData,
  loadingEvolution,
}: {
  evolutionData: { success: boolean; agent: { id: string; name: string }; events: ClusterEvolutionEvent[] } | undefined | null
  loadingEvolution: boolean
}) {
  // Event type configuration with icons and colors
  const getEventConfig = (eventType: string) => {
    const configs: Record<string, { icon: typeof Plus; color: string; bgColor: string; label: string }> = {
      created: { icon: Plus, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Created' },
      merged: { icon: GitMerge, color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Merged' },
      split: { icon: GitBranch, color: 'text-purple-400', bgColor: 'bg-purple-500/20', label: 'Split' },
      grown: { icon: TrendingUp, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Grown' },
      shrunk: { icon: TrendingDown, color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Shrunk' },
      dissolved: { icon: Trash2, color: 'text-red-400', bgColor: 'bg-red-500/20', label: 'Dissolved' },
    }
    return configs[eventType] || configs.created
  }

  // Format relative time
  const formatRelativeTime = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return date.toLocaleDateString()
  }

  if (loadingEvolution) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-purple-400" />
        <span className="ml-2 text-gray-400">Loading evolution history...</span>
      </div>
    )
  }

  const events = evolutionData?.events || []

  if (events.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
        <History className="h-12 w-12 mx-auto mb-4 text-gray-500" />
        <h3 className="text-lg font-medium text-white mb-2">No Evolution History</h3>
        <p className="text-gray-400">
          Cluster evolution events will appear here as clusters are created, merged, split, or dissolved.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border">
      <div className="p-4 border-b border-dark-border">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <History className="h-5 w-5 text-purple-400" />
          Cluster Evolution Timeline ({events.length} events)
        </h3>
      </div>
      <div className="p-4 max-h-[500px] overflow-y-auto">
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-dark-border" />

          {/* Events */}
          <div className="space-y-4">
            {events.map((event) => {
              const config = getEventConfig(event.event_type)
              const EventIcon = config.icon
              const memoriesDiff = event.memories_after - event.memories_before
              const coherenceDiff = event.coherence_after - event.coherence_before

              return (
                <div key={event.id} className="relative flex items-start gap-4 pl-2">
                  {/* Event icon */}
                  <div className={cn('relative z-10 p-2 rounded-lg', config.bgColor)}>
                    <EventIcon className={cn('h-4 w-4', config.color)} />
                  </div>

                  {/* Event content */}
                  <div className="flex-1 bg-dark-bg rounded-lg p-4 border border-dark-border">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={cn('text-sm font-medium', config.color)}>
                            {config.label}
                          </span>
                          {event.cluster_name && (
                            <span className="text-white font-medium">
                              {event.cluster_name}
                            </span>
                          )}
                        </div>

                        {/* Metrics */}
                        <div className="flex items-center gap-4 mt-2 text-xs">
                          <span className="text-gray-400">
                            Memories: {event.memories_before} → {event.memories_after}
                            {memoriesDiff !== 0 && (
                              <span className={memoriesDiff > 0 ? 'text-green-400 ml-1' : 'text-red-400 ml-1'}>
                                ({memoriesDiff > 0 ? '+' : ''}{memoriesDiff})
                              </span>
                            )}
                          </span>
                          <span className="text-gray-400">
                            Coherence: {(event.coherence_before * 100).toFixed(0)}% → {(event.coherence_after * 100).toFixed(0)}%
                            {coherenceDiff !== 0 && (
                              <span className={coherenceDiff > 0 ? 'text-green-400 ml-1' : 'text-red-400 ml-1'}>
                                ({coherenceDiff > 0 ? '+' : ''}{(coherenceDiff * 100).toFixed(0)}%)
                              </span>
                            )}
                          </span>
                        </div>

                        {/* Details */}
                        {event.details && Object.keys(event.details).length > 0 && (
                          <div className="mt-2 text-xs text-gray-500">
                            {Object.entries(event.details).map(([key, value]) => (
                              <span key={key} className="mr-3">
                                {key}: {String(value)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Timestamp */}
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatRelativeTime(event.created_at)}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

// Session 754: Phase 2 - Tag Filter Section Component
function TagFilterSection({
  memories,
  filterTag,
  setFilterTag,
}: {
  memories: Memory[]
  filterTag: string
  setFilterTag: (tag: string) => void
}) {
  // Extract all unique tags from memories
  const allTags = memories.reduce((tags: string[], memory) => {
    if (memory.tags && Array.isArray(memory.tags)) {
      memory.tags.forEach((tag) => {
        if (!tags.includes(tag)) {
          tags.push(tag)
        }
      })
    }
    return tags
  }, [])

  // Sort tags alphabetically
  allTags.sort()

  if (allTags.length === 0) {
    return null
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-300">Filter by Tag</span>
        </div>
        {filterTag && (
          <button
            onClick={() => setFilterTag('')}
            className="text-xs text-purple-400 hover:underline"
          >
            Clear
          </button>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto">
        {allTags.map((tag) => (
          <button
            key={tag}
            onClick={() => setFilterTag(filterTag === tag ? '' : tag)}
            className={cn(
              'px-2 py-1 text-xs rounded-lg border transition-colors',
              filterTag === tag
                ? 'bg-purple-600 border-purple-500 text-white'
                : 'bg-dark-bg border-dark-border text-gray-400 hover:border-purple-500 hover:text-purple-400'
            )}
          >
            #{tag}
          </button>
        ))}
      </div>
    </div>
  )
}

// Session 754: Phase 3 - Cluster Visualization Graph Component
function ClusterVisualizationGraph({
  visualizationData,
  loadingVisualization,
  onNodeClick,
}: {
  visualizationData?: {
    success: boolean
    nodes: Array<{
      id: string
      type: 'cluster' | 'memory'
      name: string
      color: string
      size: number
      coherence?: number
      memory_type?: string
      similarity?: number
      is_core?: boolean
    }>
    links: Array<{
      source: string
      target: string
      strength: number
      type?: string
    }>
  } | null
  loadingVisualization?: boolean
  onNodeClick?: (nodeId: string) => void
}) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)

  if (loadingVisualization) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-8">
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-6 w-6 animate-spin text-purple-400" />
          <span className="ml-2 text-gray-400">Loading visualization...</span>
        </div>
      </div>
    )
  }

  const nodes = visualizationData?.nodes || []
  const links = visualizationData?.links || []

  if (nodes.length === 0) {
    return (
      <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
        <Sparkles className="h-12 w-12 mx-auto mb-4 text-gray-500" />
        <h3 className="text-lg font-medium text-white mb-2">No Visualization Data</h3>
        <p className="text-gray-400">
          Generate clusters first to see the visualization graph.
        </p>
      </div>
    )
  }

  // Get node info for tooltip
  const hoveredNodeInfo = nodes.find(n => n.id === hoveredNode)

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border overflow-hidden">
      <div className="p-4 border-b border-dark-border flex items-center justify-between">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-400" />
          Cluster Visualization Graph
        </h3>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            Clusters ({nodes.filter(n => n.type === 'cluster').length})
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            Memories ({nodes.filter(n => n.type === 'memory').length})
          </span>
        </div>
      </div>

      <div className="relative" style={{ height: '500px' }}>
        <ForceGraph2D
          graphData={{ nodes, links }}
          nodeLabel={(node) => node.name}
          nodeColor={(node) => node.color}
          nodeVal={(node) => node.size}
          linkWidth={(link) => (link.strength || 0.5) * 3}
          linkColor={() => '#4b5563'}
          backgroundColor="#0f172a"
          onNodeClick={(node) => {
            if (onNodeClick && node.id) {
              onNodeClick(node.id as string)
            }
          }}
          onNodeHover={(node) => {
            setHoveredNode(node?.id as string || null)
          }}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name as string
            const fontSize = Math.max(10 / globalScale, 2)
            const nodeSize = (node.size as number) || 5

            // Draw node
            ctx.beginPath()
            ctx.arc(node.x!, node.y!, nodeSize, 0, 2 * Math.PI)
            ctx.fillStyle = node.color as string
            ctx.fill()

            // Draw label for clusters or hovered nodes
            if ((node.type === 'cluster' || node.id === hoveredNode) && globalScale > 0.5) {
              ctx.font = `${fontSize}px Sans-Serif`
              ctx.textAlign = 'center'
              ctx.textBaseline = 'middle'
              ctx.fillStyle = '#e2e8f0'
              ctx.fillText(label?.substring(0, 20) || '', node.x!, node.y! + nodeSize + fontSize)
            }
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            const nodeSize = (node.size as number) || 5
            ctx.beginPath()
            ctx.arc(node.x!, node.y!, nodeSize + 2, 0, 2 * Math.PI)
            ctx.fillStyle = color
            ctx.fill()
          }}
        />

        {/* Tooltip */}
        {hoveredNodeInfo && (
          <div className="absolute top-4 right-4 bg-dark-bg border border-dark-border rounded-lg p-3 max-w-xs">
            <div className="flex items-center gap-2 mb-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: hoveredNodeInfo.color }}
              />
              <span className="font-medium text-white text-sm">
                {hoveredNodeInfo.name}
              </span>
            </div>
            <div className="text-xs text-gray-400 space-y-1">
              <p>Type: {hoveredNodeInfo.type}</p>
              {hoveredNodeInfo.coherence !== undefined && (
                <p>Coherence: {(hoveredNodeInfo.coherence * 100).toFixed(0)}%</p>
              )}
              {hoveredNodeInfo.memory_type && (
                <p>Memory Type: {hoveredNodeInfo.memory_type}</p>
              )}
              {hoveredNodeInfo.similarity !== undefined && (
                <p>Similarity: {(hoveredNodeInfo.similarity * 100).toFixed(0)}%</p>
              )}
              {hoveredNodeInfo.is_core && (
                <p className="text-purple-400">Core Member</p>
              )}
            </div>
            {hoveredNodeInfo.type === 'cluster' && (
              <p className="text-xs text-purple-400 mt-2">Click to view details</p>
            )}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="px-4 py-3 border-t border-dark-border bg-dark-bg/50">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Drag to pan, scroll to zoom, click clusters for details</span>
          <span>{nodes.length} nodes, {links.length} connections</span>
        </div>
      </div>
    </div>
  )
}

// Session 755: Phase 3 - Find Similar Clusters Component
function FindSimilarClusters({
  similarQuery,
  setSimilarQuery,
  handleFindSimilar,
  isSearchingSimilar,
  similarResults,
  onClusterClick,
}: {
  similarQuery: string
  setSimilarQuery: (query: string) => void
  handleFindSimilar: () => void
  isSearchingSimilar: boolean
  similarResults: Array<{
    id: string
    name: string
    description: string
    color: string
    similarity: number
    agent: string
    memory_count: number
  }>
  onClusterClick: (clusterId: string) => void
}) {
  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="bg-dark-card rounded-lg border border-dark-border p-4">
        <h3 className="text-sm font-medium text-white mb-3">Semantic Cluster Search</h3>
        <p className="text-xs text-gray-400 mb-4">
          Enter a concept, topic, or description to find semantically similar clusters across all agents.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={similarQuery}
            onChange={(e) => setSimilarQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleFindSimilar()}
            placeholder="e.g., user authentication, data processing, error handling..."
            className="flex-1 bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={handleFindSimilar}
            disabled={isSearchingSimilar || !similarQuery.trim()}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            {isSearchingSimilar ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="h-4 w-4" />
                Search
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {similarResults.length > 0 ? (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-400">
            Found {similarResults.length} similar clusters
          </h3>
          <div className="grid md:grid-cols-2 gap-3">
            {similarResults.map((result) => (
              <button
                key={result.id}
                onClick={() => onClusterClick(result.id)}
                className="bg-dark-card rounded-lg border border-dark-border p-4 text-left hover:bg-dark-bg transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div
                    className="p-2 rounded-lg flex-shrink-0"
                    style={{ backgroundColor: result.color + '30' }}
                  >
                    <Network className="h-5 w-5" style={{ color: result.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="font-medium text-white truncate">{result.name}</h4>
                      <span
                        className={cn(
                          'text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0',
                          result.similarity >= 0.8
                            ? 'bg-green-500/20 text-green-400'
                            : result.similarity >= 0.6
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-gray-500/20 text-gray-400'
                        )}
                      >
                        {(result.similarity * 100).toFixed(0)}% match
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1 line-clamp-2">{result.description}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Brain className="h-3 w-3" />
                        {result.agent}
                      </span>
                      <span>{result.memory_count} memories</span>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      ) : similarQuery && !isSearchingSimilar ? (
        <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
          <Search className="h-12 w-12 mx-auto mb-4 text-gray-500" />
          <h3 className="text-lg font-medium text-white mb-2">No Results Yet</h3>
          <p className="text-gray-400">
            Press Search to find clusters similar to your query.
          </p>
        </div>
      ) : (
        <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
          <Search className="h-12 w-12 mx-auto mb-4 text-gray-500" />
          <h3 className="text-lg font-medium text-white mb-2">Semantic Search</h3>
          <p className="text-gray-400">
            Enter a concept or topic above to find related memory clusters.
            <br />
            This uses embedding similarity to find semantically related clusters.
          </p>
        </div>
      )}
    </div>
  )
}

// Session 754: Phase 3 - Palace Room Map Component
function PalaceRoomMap({
  rooms,
  selectedRoom,
  onRoomClick,
  getRoomIcon,
}: {
  rooms: Room[]
  selectedRoom: Room | null
  onRoomClick: (room: Room) => void
  getRoomIcon: (type: string) => typeof Brain
}) {
  // Calculate grid positions if position_x/y not set
  const roomsWithPositions = rooms.map((room, index) => {
    // Use provided positions or calculate grid positions
    const col = room.position_x !== undefined ? room.position_x : (index % 3)
    const row = room.position_y !== undefined ? room.position_y : Math.floor(index / 3)
    return { ...room, gridCol: col, gridRow: row }
  })

  // Find the grid dimensions
  const maxCol = Math.max(...roomsWithPositions.map(r => r.gridCol), 2)
  const maxRow = Math.max(...roomsWithPositions.map(r => r.gridRow), 0)

  // Create grid cells
  const gridCells: Array<{ room: Room | null; col: number; row: number }> = []
  for (let row = 0; row <= maxRow; row++) {
    for (let col = 0; col <= maxCol; col++) {
      const room = roomsWithPositions.find(r => r.gridCol === col && r.gridRow === row)
      gridCells.push({ room: room || null, col, row })
    }
  }

  if (rooms.length === 0) {
    return (
      <div className="p-4 text-center text-gray-400">
        <Home className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No rooms yet</p>
      </div>
    )
  }

  return (
    <div className="p-4">
      {/* Palace Map Grid */}
      <div
        className="grid gap-2"
        style={{
          gridTemplateColumns: `repeat(${maxCol + 1}, 1fr)`,
        }}
      >
        {gridCells.map(({ room, col, row }) => {
          if (!room) {
            return (
              <div
                key={`empty-${col}-${row}`}
                className="aspect-square rounded-lg border border-dashed border-dark-border/50 bg-dark-bg/30"
              />
            )
          }

          const RoomIcon = getRoomIcon(room.room_type)
          const isSelected = selectedRoom?.id === room.id

          return (
            <button
              key={room.id}
              onClick={() => onRoomClick(room)}
              className={cn(
                'aspect-square rounded-lg p-2 flex flex-col items-center justify-center transition-all',
                'border-2 hover:scale-105',
                isSelected
                  ? 'border-purple-500 ring-2 ring-purple-500/30'
                  : 'border-dark-border hover:border-gray-500'
              )}
              style={{
                backgroundColor: room.color + '20',
              }}
              title={`${room.name}\n${room.memory_count} memories\n${room.description || ''}`}
            >
              <RoomIcon
                className="h-6 w-6 mb-1"
                style={{ color: room.color }}
              />
              <span
                className="text-xs font-medium text-center line-clamp-2 leading-tight"
                style={{ color: room.color }}
              >
                {room.name}
              </span>
              <span className="text-xs text-gray-500 mt-0.5">
                {room.memory_count}
              </span>
            </button>
          )
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-dark-border">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Click a room to view its memories</span>
          <span>{rooms.length} rooms</span>
        </div>
      </div>
    </div>
  )
}
