/**
 * Session 716: Memory Palace Page
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
} from 'lucide-react'
import { memoryPalaceApi } from '@/lib/api'
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
}

interface Room {
  id: string
  name: string
  room_type: string
  description: string
  color: string
  icon: string
  memory_count: number
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
}

interface Overview {
  total_memories: number
  agents_with_memories: number
  memory_types: Array<{ memory_type: string; count: number }>
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
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)
  const [selectedMemory, setSelectedMemory] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<Memory[]>([])
  const [filterType, setFilterType] = useState<string>('')

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
  const { data: memoriesData, isLoading: loadingMemories } = useQuery({
    queryKey: ['memory-palace-memories', selectedAgent?.id, filterType],
    queryFn: async () => {
      if (!selectedAgent) return null
      const params: { type?: string; limit?: number } = { limit: 100 }
      if (filterType) params.type = filterType
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
          {(selectedAgent || selectedRoom || selectedMemory) && (
            <button
              onClick={handleBack}
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
              {selectedMemory
                ? 'Memory Detail'
                : selectedRoom
                  ? `${selectedRoom.name} - ${selectedAgent?.name}`
                  : selectedAgent
                    ? `${selectedAgent.name}'s Memory Palace`
                    : 'Explore agent memories and knowledge'}
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
              <h2 className="font-semibold text-white">
                {selectedAgent ? 'Rooms' : 'Agents'}
              </h2>
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
                // Room list
                loadingRooms ? (
                  <div className="p-4 text-center text-gray-400">Loading rooms...</div>
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
            <div className="mt-4 bg-dark-card rounded-lg border border-dark-border p-4">
              <div className="flex items-center gap-2 mb-3">
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
    </div>
  )
}

// Memory Card Component
function MemoryCard({ memory, onClick }: { memory: Memory; onClick: () => void }) {
  const config = MEMORY_TYPE_CONFIG[memory.memory_type] || MEMORY_TYPE_CONFIG.default
  const Icon = config.icon
  const valenceColor = VALENCE_COLORS[memory.valence] || VALENCE_COLORS.neutral

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full p-4 text-left hover:bg-dark-bg transition-colors border-l-4',
        valenceColor
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn('p-2 rounded-lg flex-shrink-0', config.bgColor)}>
          <Icon className={cn('h-4 w-4', config.color)} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-medium text-white truncate">{memory.title}</h3>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className="text-xs text-purple-400 bg-purple-500/20 px-2 py-0.5 rounded">
                {(memory.importance_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-1 line-clamp-2">{memory.content}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            <span className="capitalize">{memory.memory_type}</span>
            <span>{new Date(memory.created_at).toLocaleDateString()}</span>
            {memory.access_count !== undefined && (
              <span className="flex items-center gap-1">
                <Eye className="h-3 w-3" />
                {memory.access_count}
              </span>
            )}
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-gray-600 flex-shrink-0 mt-1" />
      </div>
    </button>
  )
}

// Memory Detail Card Component
function MemoryDetailCard({
  memory,
  onDelete,
  onViewConnected,
  isDeleting,
}: {
  memory: MemoryDetail
  onDelete: () => void
  onViewConnected: (id: string) => void
  isDeleting: boolean
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

      {/* Connected Memories */}
      {memory.connected_memories && memory.connected_memories.length > 0 && (
        <div className="bg-dark-card rounded-lg border border-dark-border p-4">
          <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
            <Link2 className="h-5 w-5 text-purple-400" />
            Connected Memories ({memory.connected_memories.length})
          </h3>
          <div className="space-y-2">
            {memory.connected_memories.map((connected) => {
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
      )}
    </div>
  )
}
