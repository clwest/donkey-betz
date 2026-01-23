import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { voiceMarketplaceApi } from '@/lib/api'
import { cn } from '@/lib/cn'
import {
  Mic,
  Search,
  Star,
  Play,
  Pause,
  DollarSign,
  Download,
  Upload,
  ShoppingCart,
  TrendingUp,
  Users,
  Clock,
  Grid,
  List,
  Plus,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  Loader2,
  CheckCircle,
  XCircle,
  ArrowUpRight,
  Volume2,
} from 'lucide-react'

// Types
interface Voice {
  id: string
  name: string
  description?: string
  creator?: string
  creator_name?: string
  category?: string
  tags?: string[]
  price?: number
  currency?: string
  license_type?: string
  sample_url?: string
  preview_url?: string
  rating?: number
  review_count?: number
  download_count?: number
  purchase_count?: number
  status?: 'draft' | 'published' | 'unpublished' | 'pending'
  is_featured?: boolean
  created_at?: string
  updated_at?: string
}

interface Transaction {
  id: string
  type: 'sale' | 'purchase' | 'withdrawal' | 'refund'
  voice_id?: string
  voice_name?: string
  amount: number
  currency?: string
  status?: string
  buyer_name?: string
  created_at?: string
}

interface Earnings {
  total_earnings: number
  pending_earnings: number
  available_balance: number
  total_sales: number
  this_month: number
  last_month: number
  currency?: string
}

interface Stats {
  total_voices: number
  published_voices: number
  total_downloads: number
  total_purchases: number
  average_rating: number
  total_reviews: number
}

type TabType = 'browse' | 'my-voices' | 'purchases' | 'earnings'

export default function VoiceMarketplacePage() {
  const [activeTab, setActiveTab] = useState<TabType>('browse')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [playingVoiceId, setPlayingVoiceId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Queries
  const { data: browseData, isLoading: loadingBrowse } = useQuery({
    queryKey: ['voice-marketplace-browse', searchQuery, selectedCategory],
    queryFn: () => voiceMarketplaceApi.browse({ search: searchQuery, category: selectedCategory }),
    enabled: activeTab === 'browse',
  })

  const { data: categoriesData } = useQuery({
    queryKey: ['voice-marketplace-categories'],
    queryFn: () => voiceMarketplaceApi.categories(),
    enabled: activeTab === 'browse',
  })

  const { data: myVoicesData, isLoading: loadingMyVoices } = useQuery({
    queryKey: ['voice-marketplace-my-voices'],
    queryFn: () => voiceMarketplaceApi.myVoices(),
    enabled: activeTab === 'my-voices',
  })

  const { data: purchasesData, isLoading: loadingPurchases } = useQuery({
    queryKey: ['voice-marketplace-purchases'],
    queryFn: () => voiceMarketplaceApi.myPurchases(),
    enabled: activeTab === 'purchases',
  })

  const { data: earningsData, isLoading: loadingEarnings } = useQuery({
    queryKey: ['voice-marketplace-earnings'],
    queryFn: () => voiceMarketplaceApi.earnings(),
    enabled: activeTab === 'earnings',
  })

  const { data: transactionsData, isLoading: loadingTransactions } = useQuery({
    queryKey: ['voice-marketplace-transactions'],
    queryFn: () => voiceMarketplaceApi.transactions({ limit: 50 }),
    enabled: activeTab === 'earnings',
  })

  const { data: statsData } = useQuery({
    queryKey: ['voice-marketplace-stats'],
    queryFn: () => voiceMarketplaceApi.stats(),
  })

  // Mutations
  const publishVoice = useMutation({
    mutationFn: (id: string) => voiceMarketplaceApi.publishVoice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voice-marketplace-my-voices'] })
    },
  })

  const unpublishVoice = useMutation({
    mutationFn: (id: string) => voiceMarketplaceApi.unpublishVoice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voice-marketplace-my-voices'] })
    },
  })

  const deleteVoice = useMutation({
    mutationFn: (id: string) => voiceMarketplaceApi.deleteVoice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voice-marketplace-my-voices'] })
    },
  })

  const purchaseVoice = useMutation({
    mutationFn: (id: string) => voiceMarketplaceApi.purchase(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voice-marketplace-purchases'] })
      queryClient.invalidateQueries({ queryKey: ['voice-marketplace-browse'] })
    },
  })

  // Data extraction
  const rawBrowse = browseData?.data?.voices || browseData?.data?.results || browseData?.data
  const voices: Voice[] = Array.isArray(rawBrowse) ? rawBrowse : []
  const rawCategories = categoriesData?.data?.categories || categoriesData?.data
  const categories: string[] = Array.isArray(rawCategories) ? rawCategories : []
  const rawMyVoices = myVoicesData?.data?.voices || myVoicesData?.data?.results || myVoicesData?.data
  const myVoices: Voice[] = Array.isArray(rawMyVoices) ? rawMyVoices : []
  const rawPurchases = purchasesData?.data?.purchases || purchasesData?.data?.results || purchasesData?.data
  const purchases: Voice[] = Array.isArray(rawPurchases) ? rawPurchases : []
  const earnings: Earnings = earningsData?.data || {}
  const rawTransactions = transactionsData?.data?.transactions || transactionsData?.data?.results || transactionsData?.data
  const transactions: Transaction[] = Array.isArray(rawTransactions) ? rawTransactions : []
  const stats: Stats = statsData?.data || {}

  const tabs = [
    { id: 'browse' as TabType, label: 'Browse', icon: Search },
    { id: 'my-voices' as TabType, label: 'My Voices', icon: Mic, badge: myVoices.length },
    { id: 'purchases' as TabType, label: 'Purchases', icon: ShoppingCart },
    { id: 'earnings' as TabType, label: 'Earnings', icon: DollarSign },
  ]

  const formatCurrency = (amount?: number, currency = 'USD') => {
    if (amount === undefined || amount === null) return '$0.00'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount)
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString()
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'published':
        return 'text-accent-green'
      case 'draft':
        return 'text-yellow-400'
      case 'pending':
        return 'text-blue-400'
      case 'unpublished':
        return 'text-gray-400'
      default:
        return 'text-gray-500'
    }
  }

  const getTransactionColor = (type?: string) => {
    switch (type) {
      case 'sale':
        return 'text-accent-green'
      case 'purchase':
        return 'text-blue-400'
      case 'withdrawal':
        return 'text-yellow-400'
      case 'refund':
        return 'text-red-400'
      default:
        return 'text-gray-500'
    }
  }

  const handlePlayPreview = (voiceId: string) => {
    if (playingVoiceId === voiceId) {
      setPlayingVoiceId(null)
    } else {
      setPlayingVoiceId(voiceId)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-purple-500/20">
            <Mic className="h-6 w-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Voice Marketplace</h1>
            <p className="text-gray-400">Browse, create, and sell AI voice clones</p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-xs text-gray-500">Total Voices</p>
            <p className="text-lg font-bold">{stats.total_voices || voices.length}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">Your Earnings</p>
            <p className="text-lg font-bold text-accent-green">
              {formatCurrency(earnings.total_earnings)}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors',
                activeTab === tab.id
                  ? 'bg-dark-card text-white border-b-2 border-primary-500'
                  : 'text-gray-400 hover:text-white hover:bg-dark-card/50'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
              {tab.badge !== undefined && tab.badge > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-primary-600">
                  {tab.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div className="space-y-4">
            {/* Search & Filters */}
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search voices..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-dark-card border border-dark-border rounded-lg focus:outline-none focus:border-primary-500"
                />
              </div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 bg-dark-card border border-dark-border rounded-lg"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              <div className="flex items-center gap-1 bg-dark-card border border-dark-border rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={cn('p-1.5 rounded', viewMode === 'grid' && 'bg-primary-600')}
                >
                  <Grid className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={cn('p-1.5 rounded', viewMode === 'list' && 'bg-primary-600')}
                >
                  <List className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Voice Grid/List */}
            {loadingBrowse ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : voices.length === 0 ? (
              <div className="text-center py-12">
                <Mic className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No voices found</p>
                <p className="text-sm text-gray-500">Try adjusting your search or filters</p>
              </div>
            ) : viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {voices.map((voice) => (
                  <div key={voice.id} className="card p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium truncate">{voice.name}</h3>
                        <p className="text-xs text-gray-500">{voice.creator_name || 'Unknown'}</p>
                      </div>
                      {voice.is_featured && (
                        <span className="px-2 py-0.5 text-xs rounded bg-yellow-500/20 text-yellow-400">
                          Featured
                        </span>
                      )}
                    </div>

                    {voice.description && (
                      <p className="text-sm text-gray-400 line-clamp-2">{voice.description}</p>
                    )}

                    <div className="flex items-center gap-2">
                      {voice.category && (
                        <span className="px-2 py-0.5 text-xs rounded bg-dark-bg text-gray-400">
                          {voice.category}
                        </span>
                      )}
                      {voice.rating && (
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-yellow-400 fill-yellow-400" />
                          <span className="text-xs">{(voice.rating ?? 0).toFixed(1)}</span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-dark-border">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handlePlayPreview(voice.id)}
                          className="p-2 rounded-full bg-primary-600/20 text-primary-400 hover:bg-primary-600/30"
                        >
                          {playingVoiceId === voice.id ? (
                            <Pause className="h-4 w-4" />
                          ) : (
                            <Play className="h-4 w-4" />
                          )}
                        </button>
                        <span className="text-lg font-bold">
                          {formatCurrency(voice.price)}
                        </span>
                      </div>
                      <button
                        onClick={() => purchaseVoice.mutate(voice.id)}
                        disabled={purchaseVoice.isPending}
                        className="px-3 py-1.5 text-sm rounded bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                      >
                        Buy
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {voices.map((voice) => (
                  <div key={voice.id} className="card p-4 flex items-center gap-4">
                    <button
                      onClick={() => handlePlayPreview(voice.id)}
                      className="p-3 rounded-full bg-primary-600/20 text-primary-400 hover:bg-primary-600/30"
                    >
                      {playingVoiceId === voice.id ? (
                        <Pause className="h-5 w-5" />
                      ) : (
                        <Play className="h-5 w-5" />
                      )}
                    </button>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium">{voice.name}</h3>
                        {voice.is_featured && (
                          <span className="px-2 py-0.5 text-xs rounded bg-yellow-500/20 text-yellow-400">
                            Featured
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-400">
                        {voice.creator_name || 'Unknown'} • {voice.category}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                      <span>{voice.rating?.toFixed(1) || '—'}</span>
                    </div>
                    <span className="text-lg font-bold">{formatCurrency(voice.price)}</span>
                    <button
                      onClick={() => purchaseVoice.mutate(voice.id)}
                      disabled={purchaseVoice.isPending}
                      className="px-4 py-2 rounded bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                    >
                      Buy Now
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* My Voices Tab */}
        {activeTab === 'my-voices' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Your Voice Clones</h2>
              <button className="btn-primary flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Create New Voice
              </button>
            </div>

            {loadingMyVoices ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : myVoices.length === 0 ? (
              <div className="text-center py-12">
                <Upload className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">You haven't created any voices yet</p>
                <p className="text-sm text-gray-500 mb-4">Upload audio samples to create your first voice clone</p>
                <button className="btn-primary">Create Your First Voice</button>
              </div>
            ) : (
              <div className="space-y-3">
                {myVoices.map((voice) => (
                  <div key={voice.id} className="card p-4 flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-purple-500/20">
                      <Mic className="h-6 w-6 text-purple-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium">{voice.name}</h3>
                        <span className={cn('text-xs', getStatusColor(voice.status))}>
                          {voice.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400">
                        {voice.category} • {formatCurrency(voice.price)} • {voice.purchase_count || 0} sales
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {voice.rating && (
                        <div className="flex items-center gap-1 px-2 py-1 rounded bg-dark-bg">
                          <Star className="h-3 w-3 text-yellow-400 fill-yellow-400" />
                          <span className="text-sm">{(voice.rating ?? 0).toFixed(1)}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handlePlayPreview(voice.id)}
                        className="p-2 rounded hover:bg-dark-bg"
                        title="Preview"
                      >
                        <Volume2 className="h-4 w-4" />
                      </button>
                      <button className="p-2 rounded hover:bg-dark-bg" title="Edit">
                        <Edit className="h-4 w-4" />
                      </button>
                      {voice.status === 'published' ? (
                        <button
                          onClick={() => unpublishVoice.mutate(voice.id)}
                          disabled={unpublishVoice.isPending}
                          className="p-2 rounded hover:bg-dark-bg text-gray-400"
                          title="Unpublish"
                        >
                          <EyeOff className="h-4 w-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => publishVoice.mutate(voice.id)}
                          disabled={publishVoice.isPending}
                          className="p-2 rounded hover:bg-dark-bg text-accent-green"
                          title="Publish"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => deleteVoice.mutate(voice.id)}
                        disabled={deleteVoice.isPending}
                        className="p-2 rounded hover:bg-dark-bg text-red-400"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Purchases Tab */}
        {activeTab === 'purchases' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Your Purchased Voices</h2>

            {loadingPurchases ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : purchases.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingCart className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No purchases yet</p>
                <p className="text-sm text-gray-500 mb-4">Browse the marketplace to find voices</p>
                <button
                  onClick={() => setActiveTab('browse')}
                  className="btn-primary"
                >
                  Browse Marketplace
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {purchases.map((voice) => (
                  <div key={voice.id} className="card p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium">{voice.name}</h3>
                        <p className="text-xs text-gray-500">{voice.creator_name}</p>
                      </div>
                      <CheckCircle className="h-5 w-5 text-accent-green" />
                    </div>

                    <p className="text-sm text-gray-400">{voice.category}</p>

                    <div className="flex items-center gap-2 pt-2 border-t border-dark-border">
                      <button className="flex-1 btn-secondary flex items-center justify-center gap-2">
                        <Download className="h-4 w-4" />
                        Download
                      </button>
                      <button className="btn-primary flex items-center justify-center gap-2">
                        <Play className="h-4 w-4" />
                        Use
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Earnings Tab */}
        {activeTab === 'earnings' && (
          <div className="space-y-6">
            {/* Earnings Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-accent-green/20">
                    <DollarSign className="h-5 w-5 text-accent-green" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Total Earnings</p>
                    <p className="text-xl font-bold text-accent-green">
                      {formatCurrency(earnings.total_earnings)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-blue-500/20">
                    <Clock className="h-5 w-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Pending</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(earnings.pending_earnings)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-purple-500/20">
                    <TrendingUp className="h-5 w-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">This Month</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(earnings.this_month)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-yellow-500/20">
                    <Users className="h-5 w-5 text-yellow-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Total Sales</p>
                    <p className="text-xl font-bold">{earnings.total_sales || 0}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Available Balance & Withdraw */}
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400">Available for Withdrawal</p>
                  <p className="text-3xl font-bold text-accent-green">
                    {formatCurrency(earnings.available_balance)}
                  </p>
                </div>
                <button
                  className="btn-primary flex items-center gap-2"
                  disabled={!earnings.available_balance || earnings.available_balance <= 0}
                >
                  <ArrowUpRight className="h-4 w-4" />
                  Withdraw
                </button>
              </div>
            </div>

            {/* Transactions */}
            <div className="card">
              <div className="p-4 border-b border-dark-border">
                <h3 className="font-semibold">Recent Transactions</h3>
              </div>

              {loadingEarnings || loadingTransactions ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : transactions.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">No transactions yet</p>
                </div>
              ) : (
                <div className="divide-y divide-dark-border">
                  {transactions.map((tx) => (
                    <div key={tx.id} className="p-4 flex items-center gap-4">
                      <div className={cn(
                        'p-2 rounded-lg',
                        tx.type === 'sale' ? 'bg-accent-green/20' :
                        tx.type === 'purchase' ? 'bg-blue-500/20' :
                        tx.type === 'withdrawal' ? 'bg-yellow-500/20' :
                        'bg-red-500/20'
                      )}>
                        {tx.type === 'sale' ? <TrendingUp className="h-4 w-4 text-accent-green" /> :
                         tx.type === 'purchase' ? <ShoppingCart className="h-4 w-4 text-blue-400" /> :
                         tx.type === 'withdrawal' ? <ArrowUpRight className="h-4 w-4 text-yellow-400" /> :
                         <XCircle className="h-4 w-4 text-red-400" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium capitalize">{tx.type}</p>
                        <p className="text-sm text-gray-400">
                          {tx.voice_name || tx.buyer_name || '—'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={cn('font-medium', getTransactionColor(tx.type))}>
                          {tx.type === 'sale' ? '+' : tx.type === 'refund' ? '-' : ''}
                          {formatCurrency(tx.amount)}
                        </p>
                        <p className="text-xs text-gray-500">{formatDate(tx.created_at)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
