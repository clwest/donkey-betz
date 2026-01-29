/**
 * Session 869: Voice Marketplace Tab
 *
 * Browse, purchase, and manage AI voices for TTS generation.
 * Features:
 * - Browse marketplace voices with filters
 * - Preview voice samples
 * - View and manage my voices
 * - Generate speech with selected voice
 * - Track earnings (for sellers)
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Mic,
  Search,
  Filter,
  Play,
  Pause,
  Star,
  DollarSign,
  Users,
  ShoppingCart,
  Upload,
  TrendingUp,
  RefreshCw,
  Loader2,
  X,
  Volume2,
  Check,
  Clock,
  Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi } from '@/lib/api'

// Types
interface Voice {
  id: string
  name: string
  description: string
  gender: string
  age_range: string
  accent: string
  language: string
  style_tags: string[]
  use_case: string
  price: string
  pricing_model: string
  price_display: string
  sample_url: string
  sample_duration: number
  total_uses: number
  average_rating: number
  rating_count: number
  is_featured: boolean
  is_verified: boolean
  owner: string
}

interface VoiceDetailData extends Voice {
  elevenlabs_voice_id: string
  reviews: Array<{
    id: string
    rating: number
    comment: string
    user: string
    created_at: string
  }>
  is_owned: boolean
}

interface MarketplaceStats {
  total_voices: number
  total_transactions: number
  total_revenue: string
  avg_rating: number
  top_categories: Array<{ category: string; count: number }>
}

// Sub-tabs
type VoiceSubTab = 'browse' | 'my-voices' | 'earnings'

// Audio player hook
function useAudioPlayer() {
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null)

  const play = (id: string, url: string) => {
    if (audio) {
      audio.pause()
    }
    const newAudio = new Audio(url)
    newAudio.onended = () => setPlayingId(null)
    newAudio.play()
    setAudio(newAudio)
    setPlayingId(id)
  }

  const stop = () => {
    if (audio) {
      audio.pause()
      setPlayingId(null)
    }
  }

  return { playingId, play, stop }
}

// Voice Card Component
function VoiceCard({
  voice,
  onSelect,
  playingId,
  onPlay,
  onStop,
}: {
  voice: Voice
  onSelect: () => void
  playingId: string | null
  onPlay: (id: string, url: string) => void
  onStop: () => void
}) {
  const isPlaying = playingId === voice.id

  return (
    <div
      className="bg-dark-card border border-dark-border rounded-xl p-4 hover:border-primary-500/50 transition-all cursor-pointer group"
      onClick={onSelect}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold truncate">{voice.name}</h3>
            {voice.is_featured && (
              <Sparkles size={14} className="text-yellow-400 flex-shrink-0" />
            )}
            {voice.is_verified && (
              <Check size={14} className="text-green-400 flex-shrink-0" />
            )}
          </div>
          <p className="text-sm text-gray-400 mt-1 line-clamp-2">
            {voice.description || `${voice.gender} • ${voice.age_range} • ${voice.accent}`}
          </p>
        </div>
        {voice.sample_url && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              if (isPlaying) {
                onStop()
              } else {
                onPlay(voice.id, voice.sample_url)
              }
            }}
            className={cn(
              'p-2 rounded-full transition-colors flex-shrink-0',
              isPlaying
                ? 'bg-primary-500 text-white'
                : 'bg-dark-bg hover:bg-primary-500/20 text-gray-400 hover:text-primary-400'
            )}
          >
            {isPlaying ? <Pause size={16} /> : <Play size={16} />}
          </button>
        )}
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1 mb-3">
        <span className="px-2 py-0.5 text-xs rounded bg-blue-500/20 text-blue-400 capitalize">
          {voice.gender}
        </span>
        <span className="px-2 py-0.5 text-xs rounded bg-purple-500/20 text-purple-400">
          {voice.accent}
        </span>
        {voice.use_case && (
          <span className="px-2 py-0.5 text-xs rounded bg-green-500/20 text-green-400 capitalize">
            {voice.use_case.replace('_', ' ')}
          </span>
        )}
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-3 text-gray-400">
          <span className="flex items-center gap-1">
            <Star size={14} className="text-yellow-400" />
            {voice.average_rating.toFixed(1)}
          </span>
          <span className="flex items-center gap-1">
            <Users size={14} />
            {voice.total_uses.toLocaleString()}
          </span>
        </div>
        <span className="font-semibold text-primary-400">
          {voice.price_display || (parseFloat(voice.price) === 0 ? 'Free' : `$${voice.price}`)}
        </span>
      </div>
    </div>
  )
}

// Voice Detail Modal
function VoiceDetailModal({
  voiceId,
  onClose,
}: {
  voiceId: string
  onClose: () => void
}) {
  const { playingId, play, stop } = useAudioPlayer()
  const [generateText, setGenerateText] = useState('')
  const queryClient = useQueryClient()

  const { data: voice, isLoading } = useQuery({
    queryKey: ['voice-detail', voiceId],
    queryFn: async () => {
      const res = await platformApi.get(`/api/voice-marketplace/${voiceId}/`)
      return res.data as VoiceDetailData
    },
  })

  const generateMutation = useMutation({
    mutationFn: async (text: string) => {
      const res = await platformApi.post(`/api/voice-marketplace/${voiceId}/generate/`, { text })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voice-detail', voiceId] })
    },
  })

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
        <Loader2 className="animate-spin text-primary-500" size={32} />
      </div>
    )
  }

  if (!voice) return null

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary-500/20">
              <Mic className="text-primary-400" size={20} />
            </div>
            <div>
              <h2 className="font-semibold text-lg">{voice.name}</h2>
              <p className="text-sm text-gray-400">by {voice.owner}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-dark-hover rounded">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Sample Player */}
          {voice.sample_url && (
            <div className="p-4 bg-dark-bg rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Sample Preview</span>
                <span className="text-xs text-gray-500">
                  {voice.sample_duration ? `${Math.round(voice.sample_duration)}s` : ''}
                </span>
              </div>
              <button
                onClick={() =>
                  playingId === voice.id ? stop() : play(voice.id, voice.sample_url)
                }
                className={cn(
                  'w-full py-3 rounded-lg flex items-center justify-center gap-2 transition-colors',
                  playingId === voice.id
                    ? 'bg-primary-500 text-white'
                    : 'bg-dark-border hover:bg-primary-500/20 text-gray-300'
                )}
              >
                {playingId === voice.id ? (
                  <>
                    <Pause size={18} /> Playing...
                  </>
                ) : (
                  <>
                    <Play size={18} /> Play Sample
                  </>
                )}
              </button>
            </div>
          )}

          {/* Description */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Description</h4>
            <p className="text-sm text-gray-400">{voice.description || 'No description'}</p>
          </div>

          {/* Attributes */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-dark-bg rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Gender</p>
              <p className="font-medium capitalize">{voice.gender}</p>
            </div>
            <div className="p-3 bg-dark-bg rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Age Range</p>
              <p className="font-medium capitalize">{voice.age_range}</p>
            </div>
            <div className="p-3 bg-dark-bg rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Accent</p>
              <p className="font-medium">{voice.accent}</p>
            </div>
            <div className="p-3 bg-dark-bg rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Language</p>
              <p className="font-medium">{voice.language}</p>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center justify-between p-4 bg-dark-bg rounded-lg">
            <div className="flex items-center gap-4">
              <div className="text-center">
                <p className="text-xl font-bold text-yellow-400 flex items-center gap-1">
                  <Star size={18} /> {voice.average_rating.toFixed(1)}
                </p>
                <p className="text-xs text-gray-500">{voice.rating_count} reviews</p>
              </div>
              <div className="w-px h-8 bg-dark-border" />
              <div className="text-center">
                <p className="text-xl font-bold text-blue-400">{voice.total_uses.toLocaleString()}</p>
                <p className="text-xs text-gray-500">uses</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary-400">
                {voice.price_display || (parseFloat(voice.price) === 0 ? 'Free' : `$${voice.price}`)}
              </p>
              <p className="text-xs text-gray-500">{voice.pricing_model}</p>
            </div>
          </div>

          {/* Generate Speech */}
          <div className="p-4 bg-dark-bg rounded-lg border border-dashed border-dark-border">
            <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
              <Volume2 size={16} className="text-primary-400" />
              Generate Speech
            </h4>
            <textarea
              value={generateText}
              onChange={(e) => setGenerateText(e.target.value)}
              placeholder="Enter text to convert to speech..."
              className="w-full h-24 bg-dark-card border border-dark-border rounded-lg p-3 text-sm resize-none focus:outline-none focus:border-primary-500"
            />
            <div className="flex items-center justify-between mt-3">
              <span className="text-xs text-gray-500">{generateText.length} characters</span>
              <button
                onClick={() => generateMutation.mutate(generateText)}
                disabled={!generateText.trim() || generateMutation.isPending}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors',
                  generateText.trim()
                    ? 'bg-primary-500 hover:bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                )}
              >
                {generateMutation.isPending ? (
                  <>
                    <Loader2 size={14} className="animate-spin" /> Generating...
                  </>
                ) : (
                  <>
                    <Mic size={14} /> Generate
                  </>
                )}
              </button>
            </div>
            {generateMutation.isSuccess && (
              <div className="mt-3 p-2 bg-green-500/20 border border-green-500/30 rounded text-green-400 text-sm">
                Speech generated successfully!
              </div>
            )}
            {generateMutation.isError && (
              <div className="mt-3 p-2 bg-red-500/20 border border-red-500/30 rounded text-red-400 text-sm">
                Failed to generate speech. Please try again.
              </div>
            )}
          </div>

          {/* Reviews */}
          {voice.reviews && voice.reviews.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-3">Recent Reviews</h4>
              <div className="space-y-2">
                {voice.reviews.map((review) => (
                  <div key={review.id} className="p-3 bg-dark-bg rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">{review.user}</span>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            size={12}
                            className={i < review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-600'}
                          />
                        ))}
                      </div>
                    </div>
                    <p className="text-sm text-gray-400">{review.comment}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Main Component
export function VoiceMarketplaceTab() {
  const [subTab, setSubTab] = useState<VoiceSubTab>('browse')
  const [selectedVoiceId, setSelectedVoiceId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    gender: '',
    age_range: '',
    use_case: '',
    sort: 'rating',
  })
  const { playingId, play, stop } = useAudioPlayer()

  // Browse voices
  const { data: browseData, isLoading: browseLoading, refetch: refetchBrowse } = useQuery({
    queryKey: ['voice-marketplace', 'browse', filters, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters.gender) params.append('gender', filters.gender)
      if (filters.age_range) params.append('age_range', filters.age_range)
      if (filters.use_case) params.append('use_case', filters.use_case)
      if (filters.sort) params.append('sort', filters.sort)
      if (searchQuery) params.append('search', searchQuery)
      params.append('limit', '24')
      const res = await platformApi.get(`/api/voice-marketplace/?${params}`)
      return res.data as { voices: Voice[]; total: number }
    },
    enabled: subTab === 'browse',
  })

  // My voices
  const { data: myVoicesData, isLoading: myVoicesLoading } = useQuery({
    queryKey: ['voice-marketplace', 'my-voices'],
    queryFn: async () => {
      const res = await platformApi.get('/api/voice-marketplace/my-voices/')
      return res.data as { voices: Voice[]; total: number }
    },
    enabled: subTab === 'my-voices',
  })

  // Earnings
  const { data: earningsData, isLoading: earningsLoading } = useQuery({
    queryKey: ['voice-marketplace', 'earnings'],
    queryFn: async () => {
      const res = await platformApi.get('/api/voice-marketplace/earnings/')
      return res.data
    },
    enabled: subTab === 'earnings',
  })

  // Stats
  const { data: statsData } = useQuery({
    queryKey: ['voice-marketplace', 'stats'],
    queryFn: async () => {
      const res = await platformApi.get('/api/voice-marketplace/stats/')
      return res.data as MarketplaceStats
    },
  })

  const subTabs = [
    { id: 'browse' as VoiceSubTab, label: 'Browse', icon: Search },
    { id: 'my-voices' as VoiceSubTab, label: 'My Voices', icon: Mic },
    { id: 'earnings' as VoiceSubTab, label: 'Earnings', icon: DollarSign },
  ]

  return (
    <div className="h-full flex flex-col bg-dark-bg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-dark-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary-500/20">
              <Mic className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Voice Marketplace</h2>
              <p className="text-sm text-gray-400">Browse, purchase, and manage AI voices</p>
            </div>
          </div>
          <button
            onClick={() => subTab === 'browse' ? refetchBrowse() : null}
            className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
          >
            <RefreshCw size={18} className={browseLoading ? 'animate-spin' : ''} />
          </button>
        </div>

        {/* Stats */}
        {statsData && (
          <div className="grid grid-cols-4 gap-3 mb-4">
            <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
              <p className="text-xs text-gray-500">Total Voices</p>
              <p className="text-xl font-bold text-primary-400">{statsData.total_voices}</p>
            </div>
            <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
              <p className="text-xs text-gray-500">Avg Rating</p>
              <p className="text-xl font-bold text-yellow-400 flex items-center gap-1">
                <Star size={16} /> {statsData.avg_rating?.toFixed(1) || '0.0'}
              </p>
            </div>
            <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
              <p className="text-xs text-gray-500">Transactions</p>
              <p className="text-xl font-bold text-blue-400">{statsData.total_transactions}</p>
            </div>
            <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
              <p className="text-xs text-gray-500">Total Revenue</p>
              <p className="text-xl font-bold text-green-400">${statsData.total_revenue || '0'}</p>
            </div>
          </div>
        )}

        {/* Sub-tabs */}
        <div className="flex items-center gap-2">
          {subTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSubTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                subTab === tab.id
                  ? 'bg-primary-500/20 text-primary-400 border border-primary-500/50'
                  : 'text-gray-400 hover:text-white hover:bg-dark-hover'
              )}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Browse Tab */}
        {subTab === 'browse' && (
          <div className="space-y-4">
            {/* Search & Filters */}
            <div className="flex items-center gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search voices..."
                  className="w-full pl-10 pr-4 py-2 bg-dark-card border border-dark-border rounded-lg text-sm focus:outline-none focus:border-primary-500"
                />
              </div>
              <select
                value={filters.gender}
                onChange={(e) => setFilters({ ...filters, gender: e.target.value })}
                className="px-3 py-2 bg-dark-card border border-dark-border rounded-lg text-sm"
              >
                <option value="">All Genders</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="neutral">Neutral</option>
              </select>
              <select
                value={filters.use_case}
                onChange={(e) => setFilters({ ...filters, use_case: e.target.value })}
                className="px-3 py-2 bg-dark-card border border-dark-border rounded-lg text-sm"
              >
                <option value="">All Use Cases</option>
                <option value="narration">Narration</option>
                <option value="podcast">Podcast</option>
                <option value="gaming">Gaming</option>
                <option value="commercial">Commercial</option>
              </select>
              <select
                value={filters.sort}
                onChange={(e) => setFilters({ ...filters, sort: e.target.value })}
                className="px-3 py-2 bg-dark-card border border-dark-border rounded-lg text-sm"
              >
                <option value="rating">Top Rated</option>
                <option value="uses">Most Used</option>
                <option value="price">Price: Low</option>
                <option value="newest">Newest</option>
              </select>
            </div>

            {/* Voice Grid */}
            {browseLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="animate-spin text-primary-500" size={32} />
              </div>
            ) : browseData?.voices.length === 0 ? (
              <div className="text-center py-16">
                <Mic size={48} className="mx-auto mb-4 text-gray-600" />
                <p className="text-gray-400">No voices found</p>
                <p className="text-sm text-gray-500 mt-1">Try adjusting your filters</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {browseData?.voices.map((voice) => (
                  <VoiceCard
                    key={voice.id}
                    voice={voice}
                    onSelect={() => setSelectedVoiceId(voice.id)}
                    playingId={playingId}
                    onPlay={play}
                    onStop={stop}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* My Voices Tab */}
        {subTab === 'my-voices' && (
          <div className="space-y-4">
            {myVoicesLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="animate-spin text-primary-500" size={32} />
              </div>
            ) : myVoicesData?.voices.length === 0 ? (
              <div className="text-center py-16">
                <Mic size={48} className="mx-auto mb-4 text-gray-600" />
                <p className="text-gray-400">You don't have any voices yet</p>
                <p className="text-sm text-gray-500 mt-1">Browse the marketplace to find voices</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {myVoicesData?.voices.map((voice) => (
                  <VoiceCard
                    key={voice.id}
                    voice={voice}
                    onSelect={() => setSelectedVoiceId(voice.id)}
                    playingId={playingId}
                    onPlay={play}
                    onStop={stop}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Earnings Tab */}
        {subTab === 'earnings' && (
          <div className="space-y-4">
            {earningsLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="animate-spin text-primary-500" size={32} />
              </div>
            ) : (
              <>
                {/* Earnings Summary */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                    <p className="text-sm text-gray-400 mb-2">Total Earnings</p>
                    <p className="text-3xl font-bold text-green-400">
                      ${earningsData?.total_earnings || '0.00'}
                    </p>
                  </div>
                  <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                    <p className="text-sm text-gray-400 mb-2">This Month</p>
                    <p className="text-3xl font-bold text-blue-400">
                      ${earningsData?.monthly_earnings || '0.00'}
                    </p>
                  </div>
                  <div className="bg-dark-card border border-dark-border rounded-xl p-6">
                    <p className="text-sm text-gray-400 mb-2">Pending Payout</p>
                    <p className="text-3xl font-bold text-yellow-400">
                      ${earningsData?.pending_payout || '0.00'}
                    </p>
                  </div>
                </div>

                {/* Recent Transactions */}
                <div className="bg-dark-card border border-dark-border rounded-xl p-4">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Clock size={18} className="text-primary-400" />
                    Recent Transactions
                  </h3>
                  {earningsData?.transactions?.length > 0 ? (
                    <div className="space-y-2">
                      {earningsData.transactions.slice(0, 10).map((tx: { id: string; voice_name: string; amount: string; created_at: string }) => (
                        <div
                          key={tx.id}
                          className="flex items-center justify-between p-3 bg-dark-bg rounded-lg"
                        >
                          <div>
                            <p className="font-medium">{tx.voice_name}</p>
                            <p className="text-xs text-gray-500">
                              {new Date(tx.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <span className="text-green-400 font-semibold">+${tx.amount}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center py-8 text-gray-500">No transactions yet</p>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Voice Detail Modal */}
      {selectedVoiceId && (
        <VoiceDetailModal
          voiceId={selectedVoiceId}
          onClose={() => setSelectedVoiceId(null)}
        />
      )}
    </div>
  )
}

export default VoiceMarketplaceTab
