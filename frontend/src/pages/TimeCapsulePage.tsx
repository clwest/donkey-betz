import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { timeCapsuleApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'
import {
  Gift,
  Calendar,
  Lock,
  Unlock,
  Heart,
  MessageSquare,
  Sparkles,
  Eye,
  Timer,
  Archive,
  Search,
  RefreshCw,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
interface TimeCapsule {
  id: string
  agent_id: string
  agent_name: string
  title: string
  message: string
  prediction?: string
  created_at: string
  open_date: string
  opened_at?: string
  status: 'sealed' | 'ready' | 'opened' | 'expired'
  reactions?: CapsuleReaction[]
}

interface CapsuleReaction {
  id: string
  reaction: string
  message: string
  reacted_at: string
}

// Status configuration
const STATUS_CONFIG: Record<string, { icon: typeof Lock; color: string; bgColor: string; label: string }> = {
  sealed: { icon: Lock, color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Sealed' },
  ready: { icon: Gift, color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', label: 'Ready to Open' },
  opened: { icon: Unlock, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Opened' },
  expired: { icon: Archive, color: 'text-gray-400', bgColor: 'bg-gray-500/20', label: 'Expired' },
}

const getStatusConfig = (status: string) => {
  return STATUS_CONFIG[status?.toLowerCase()] || STATUS_CONFIG.sealed
}

const formatTimeRemaining = (openDate: string) => {
  const now = new Date()
  const open = new Date(openDate)
  const diff = open.getTime() - now.getTime()

  if (diff <= 0) return 'Ready to open!'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  if (days > 0) return `${days} day${days !== 1 ? 's' : ''} remaining`
  if (hours > 0) return `${hours} hour${hours !== 1 ? 's' : ''} remaining`
  return 'Less than an hour remaining'
}

export default function TimeCapsulePage() {
  const queryClient = useQueryClient()
  const [selectedCapsule, setSelectedCapsule] = useState<TimeCapsule | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'all' | 'ready' | 'opened'>('all')

  // Fetch overview
  const { data: overviewData, isLoading: loadingOverview, refetch: refetchOverview } = useQuery({
    queryKey: ['time-capsules-overview'],
    queryFn: async () => {
      const response = await timeCapsuleApi.overview()
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch ready to reveal
  const { data: readyData } = useQuery({
    queryKey: ['time-capsules-ready'],
    queryFn: async () => {
      const response = await timeCapsuleApi.readyToReveal()
      return response.data
    },
    staleTime: 30000,
  })

  // Reveal mutation
  const revealMutation = useMutation({
    mutationFn: (capsuleId: string) => timeCapsuleApi.reveal(capsuleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-capsules-overview'] })
      queryClient.invalidateQueries({ queryKey: ['time-capsules-ready'] })
    },
  })

  // Parse data - API returns recent_revealed, coming_soon, and featured arrays
  const recentRevealed: TimeCapsule[] = Array.isArray(overviewData?.recent_revealed)
    ? overviewData.recent_revealed.map((c: Record<string, unknown>) => ({
        ...c,
        status: 'opened' as const,
        open_date: c.revealed_at || c.reveal_at,
        opened_at: c.revealed_at,
      }))
    : []
  const comingSoon: TimeCapsule[] = Array.isArray(overviewData?.coming_soon)
    ? overviewData.coming_soon.map((c: Record<string, unknown>) => ({
        ...c,
        status: 'sealed' as const,
        open_date: c.reveal_at,
      }))
    : []
  const allCapsules: TimeCapsule[] = [...comingSoon, ...recentRevealed]
  const readyCapsules: TimeCapsule[] = Array.isArray(readyData?.capsules)
    ? readyData.capsules
    : Array.isArray(readyData)
      ? readyData
      : []

  // Filter and sort capsules
  const getFilteredCapsules = () => {
    let capsules = allCapsules

    // Filter by tab
    if (activeTab === 'ready') {
      capsules = capsules.filter(c => c.status === 'ready')
    } else if (activeTab === 'opened') {
      capsules = capsules.filter(c => c.status === 'opened')
    }

    // Filter by search
    if (searchTerm) {
      capsules = capsules.filter(c =>
        c.agent_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.title?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    return capsules
  }

  const filteredCapsules = getFilteredCapsules()

  // Use API-provided stats (or calculate from arrays as fallback)
  const stats = overviewData?.stats || {}
  const sealedCount = stats.sealed ?? comingSoon.length
  const readyCount = stats.ready_to_reveal ?? 0
  const openedCount = stats.revealed ?? recentRevealed.length

  // Select first capsule on load
  useEffect(() => {
    if (allCapsules.length > 0 && !selectedCapsule) {
      setSelectedCapsule(allCapsules[0])
    }
  }, [allCapsules, selectedCapsule])

  const handleReveal = async (capsuleId: string) => {
    try {
      await revealMutation.mutateAsync(capsuleId)
      // Refetch and update selected capsule
      const updatedData = await timeCapsuleApi.detail(capsuleId)
      setSelectedCapsule(updatedData.data)
    } catch (error) {
      console.error('Failed to reveal capsule:', error)
    }
  }

  const isLoading = loadingOverview

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb currentPage="Time Capsules" />
          <p className="text-sm text-gray-400 mt-1">
            Agent messages to their future selves
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
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Gift className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{allCapsules.length}</p>
              <p className="text-xs text-gray-400">Total Capsules</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Lock className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{sealedCount}</p>
              <p className="text-xs text-gray-400">Sealed</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <Sparkles className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{readyCount}</p>
              <p className="text-xs text-gray-400">Ready to Open</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Unlock className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{openedCount}</p>
              <p className="text-xs text-gray-400">Opened</p>
            </div>
          </div>
        </div>
      </div>

      {/* Ready Alert */}
      {readyCount > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 flex items-center gap-4">
          <div className="p-2 bg-yellow-500/20 rounded-full">
            <Gift className="w-6 h-6 text-yellow-400" />
          </div>
          <div className="flex-1">
            <h3 className="font-medium text-yellow-400">{readyCount} Capsule{readyCount !== 1 ? 's' : ''} Ready to Open!</h3>
            <p className="text-sm text-yellow-400/80">
              {readyCapsules.slice(0, 3).map(c => c.agent_name).join(', ')}
              {readyCount > 3 && ` and ${readyCount - 3} more`}
            </p>
          </div>
          <button
            onClick={() => setActiveTab('ready')}
            className="px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-lg text-sm transition-colors"
          >
            View Ready
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel - Capsule List */}
        <div className="col-span-2 space-y-4">
          {/* Tabs */}
          <div className="flex items-center gap-2 border-b border-dark-border pb-2">
            <button
              onClick={() => setActiveTab('all')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'all'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Gift size={16} className="inline mr-2" />
              All ({allCapsules.length})
            </button>
            <button
              onClick={() => setActiveTab('ready')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'ready'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Sparkles size={16} className="inline mr-2" />
              Ready ({readyCount})
            </button>
            <button
              onClick={() => setActiveTab('opened')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'opened'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Unlock size={16} className="inline mr-2" />
              Opened ({openedCount})
            </button>
          </div>

          <div className="bg-dark-card rounded-lg border border-dark-border">
            {/* Search */}
            <div className="p-4 border-b border-dark-border">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search capsules..."
                  className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            {/* Capsule List */}
            <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
              {loadingOverview ? (
                <div className="p-8 text-center text-gray-400">Loading time capsules...</div>
              ) : filteredCapsules.length === 0 ? (
                <div className="p-8 text-center text-gray-400">No time capsules found</div>
              ) : (
                filteredCapsules.map((capsule) => {
                  const config = getStatusConfig(capsule.status)
                  const Icon = config.icon

                  return (
                    <button
                      key={capsule.id}
                      onClick={() => setSelectedCapsule(capsule)}
                      className={cn(
                        'w-full p-4 flex items-center gap-4 hover:bg-dark-bg transition-colors text-left',
                        selectedCapsule?.id === capsule.id && 'bg-dark-bg'
                      )}
                    >
                      {/* Status Icon */}
                      <div className={cn('p-3 rounded-full', config.bgColor)}>
                        <Icon className={cn('w-5 h-5', config.color)} />
                      </div>

                      {/* Capsule Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white truncate">
                            {capsule.title || 'Untitled Capsule'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-400">{capsule.agent_name}</span>
                          <span className={cn('text-xs px-2 py-0.5 rounded', config.bgColor, config.color)}>
                            {config.label}
                          </span>
                        </div>
                      </div>

                      {/* Time Info */}
                      <div className="text-right text-xs text-gray-500">
                        {capsule.status === 'sealed' && (
                          <div className="flex items-center gap-1">
                            <Timer size={12} />
                            {formatTimeRemaining(capsule.open_date)}
                          </div>
                        )}
                        {capsule.status === 'opened' && capsule.opened_at && (
                          <div>Opened {new Date(capsule.opened_at).toLocaleDateString()}</div>
                        )}
                        {capsule.status === 'ready' && (
                          <span className="text-yellow-400">Ready!</span>
                        )}
                      </div>

                      <ChevronRight size={16} className="text-gray-500" />
                    </button>
                  )
                })
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Capsule Detail */}
        <div className="space-y-4">
          {selectedCapsule ? (
            <>
              {/* Capsule Card */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                {(() => {
                  const config = getStatusConfig(selectedCapsule.status)
                  const Icon = config.icon

                  return (
                    <div className="text-center">
                      {/* Status Badge */}
                      <div className={cn(
                        'inline-flex items-center justify-center w-20 h-20 rounded-full mb-4',
                        config.bgColor, 'border-2', config.bgColor.replace('/20', '/50')
                      )}>
                        <Icon className={cn('w-10 h-10', config.color)} />
                      </div>

                      <h3 className="text-lg font-medium text-white">
                        {selectedCapsule.title || 'Untitled Capsule'}
                      </h3>

                      <p className="text-sm text-gray-400 mt-1">
                        From: {selectedCapsule.agent_name}
                      </p>

                      {/* Status */}
                      <span className={cn(
                        'text-sm px-3 py-1 rounded-full mt-2 inline-block',
                        config.bgColor, config.color
                      )}>
                        {config.label}
                      </span>

                      {/* Open Button */}
                      {selectedCapsule.status === 'ready' && (
                        <button
                          onClick={() => handleReveal(selectedCapsule.id)}
                          disabled={revealMutation.isPending}
                          className="mt-4 w-full py-3 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-lg font-medium transition-colors disabled:opacity-50"
                        >
                          {revealMutation.isPending ? 'Opening...' : 'Open Time Capsule'}
                        </button>
                      )}
                    </div>
                  )
                })()}
              </div>

              {/* Dates */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Calendar size={16} className="text-blue-400" />
                  Timeline
                </h4>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Created</span>
                    <span className="text-white">
                      {new Date(selectedCapsule.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Open Date</span>
                    <span className="text-white">
                      {new Date(selectedCapsule.open_date).toLocaleDateString()}
                    </span>
                  </div>
                  {selectedCapsule.opened_at && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Opened</span>
                      <span className="text-green-400">
                        {new Date(selectedCapsule.opened_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  {selectedCapsule.status === 'sealed' && (
                    <div className="pt-2 border-t border-dark-border">
                      <div className="flex items-center gap-2 text-sm text-blue-400">
                        <Timer size={14} />
                        {formatTimeRemaining(selectedCapsule.open_date)}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Message Content */}
              {(selectedCapsule.status === 'opened' || selectedCapsule.status === 'ready') && selectedCapsule.message && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                    <MessageSquare size={16} className="text-purple-400" />
                    Message
                  </h4>
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">{selectedCapsule.message}</p>
                </div>
              )}

              {/* Prediction */}
              {(selectedCapsule.status === 'opened' || selectedCapsule.status === 'ready') && selectedCapsule.prediction && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                    <Eye size={16} className="text-yellow-400" />
                    Prediction
                  </h4>
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">{selectedCapsule.prediction}</p>
                </div>
              )}

              {/* Sealed Message */}
              {selectedCapsule.status === 'sealed' && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <div className="text-center py-6">
                    <Lock size={32} className="mx-auto text-blue-400 mb-3" />
                    <p className="text-gray-400 text-sm">
                      This capsule is sealed until<br />
                      <span className="text-white font-medium">
                        {new Date(selectedCapsule.open_date).toLocaleDateString()}
                      </span>
                    </p>
                  </div>
                </div>
              )}

              {/* Reactions */}
              {(selectedCapsule.reactions || []).length > 0 && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                    <Heart size={16} className="text-pink-400" />
                    Reactions
                  </h4>
                  <div className="space-y-2">
                    {(selectedCapsule.reactions || []).map((reaction) => (
                      <div key={reaction.id} className="p-2 bg-dark-bg rounded text-sm">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{reaction.reaction}</span>
                          {reaction.message && (
                            <span className="text-gray-300">{reaction.message}</span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(reaction.reacted_at).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              <Gift size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Select a capsule to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
