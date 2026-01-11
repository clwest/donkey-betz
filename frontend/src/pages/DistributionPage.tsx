import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { distributionApi } from '@/lib/api'
import {
  DollarSign, Package, Globe, TrendingUp, Loader2, RefreshCw,
  CheckCircle, XCircle, Clock, Link2, ExternalLink, BarChart3,
  Zap, Calendar, ArrowUpRight, Settings,
  Pause, Trash2, Eye, ShoppingBag, PieChart
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Session 745: Distribution Dashboard for monetization
type TabType = 'overview' | 'platforms' | 'content' | 'revenue' | 'scheduled'

interface Platform {
  id: string
  name: string
  slug: string
  category: string
  is_active: boolean
  icon_url?: string
  description?: string
  features?: string[]
}

interface UserAccount {
  id: string
  platform: string
  platform_name: string
  is_connected: boolean
  connected_at?: string
  username?: string
  store_name?: string
  total_revenue?: number
  item_count?: number
}

interface Distribution {
  id: string
  title: string
  platform: string
  platform_name?: string
  status: 'draft' | 'pending' | 'published' | 'sold' | 'rejected'
  created_at: string
  published_at?: string
  price?: number
  sales_count?: number
  revenue?: number
  thumbnail_url?: string
}

interface RevenueData {
  total_revenue: number
  this_month: number
  last_month: number
  pending: number
  growth_percent?: number
  by_platform?: Record<string, number>
}

interface DistributionStats {
  total_distributions: number
  published: number
  pending: number
  total_sales: number
  total_revenue: number
  connected_platforms: number
}

export default function DistributionPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const queryClient = useQueryClient()

  // Queries
  const { data: statsData } = useQuery({
    queryKey: ['distribution-stats'],
    queryFn: () => distributionApi.stats(),
  })

  const { data: platformsData, isLoading: loadingPlatforms } = useQuery({
    queryKey: ['distribution-platforms'],
    queryFn: () => distributionApi.platforms(),
    enabled: activeTab === 'overview' || activeTab === 'platforms',
  })

  const { data: accountsData, isLoading: loadingAccounts, refetch: refetchAccounts } = useQuery({
    queryKey: ['distribution-accounts'],
    queryFn: () => distributionApi.accounts(),
    enabled: activeTab === 'overview' || activeTab === 'platforms',
  })

  const { data: contentData, isLoading: loadingContent, refetch: refetchContent } = useQuery({
    queryKey: ['distribution-content'],
    queryFn: () => distributionApi.content(),
    enabled: activeTab === 'overview' || activeTab === 'content',
  })

  const { data: revenueData, isLoading: loadingRevenue } = useQuery({
    queryKey: ['distribution-revenue'],
    queryFn: () => distributionApi.revenueDashboard(),
    enabled: activeTab === 'overview' || activeTab === 'revenue',
  })

  const { data: recommendationsData } = useQuery({
    queryKey: ['distribution-recommendations'],
    queryFn: () => distributionApi.recommendations(),
    enabled: activeTab === 'overview',
  })

  const { data: scheduledData, isLoading: loadingScheduled } = useQuery({
    queryKey: ['distribution-scheduled'],
    queryFn: () => distributionApi.scheduled(),
    enabled: activeTab === 'scheduled',
  })

  const { data: compareData } = useQuery({
    queryKey: ['distribution-compare'],
    queryFn: () => distributionApi.comparePlatforms(),
    enabled: activeTab === 'revenue',
  })

  // Mutations
  const syncRevenueMutation = useMutation({
    mutationFn: (platform: string) => distributionApi.syncRevenue(platform),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['distribution-revenue'] })
    },
  })

  // Data extraction
  const stats: DistributionStats = statsData?.data || {
    total_distributions: 0,
    published: 0,
    pending: 0,
    total_sales: 0,
    total_revenue: 0,
    connected_platforms: 0,
  }
  const platforms: Platform[] = platformsData?.data?.platforms || platformsData?.data || []
  const accounts: UserAccount[] = accountsData?.data?.accounts || accountsData?.data || []
  const distributions: Distribution[] = contentData?.data?.distributions || contentData?.data || []
  const revenue: RevenueData = revenueData?.data?.dashboard || revenueData?.data || {}
  const recommendations = recommendationsData?.data?.recommendations || []
  const scheduled = scheduledData?.data?.scheduled || scheduledData?.data || []
  const platformComparison = compareData?.data?.platforms || []

  const connectedAccounts = accounts.filter(a => a.is_connected)

  const tabs = [
    { id: 'overview' as TabType, label: 'Overview', icon: PieChart },
    { id: 'platforms' as TabType, label: 'Platforms', icon: Globe },
    { id: 'content' as TabType, label: 'Content', icon: Package },
    { id: 'revenue' as TabType, label: 'Revenue', icon: DollarSign },
    { id: 'scheduled' as TabType, label: 'Scheduled', icon: Calendar },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-accent-green/20 text-accent-green'
      case 'sold': return 'bg-accent-cyan/20 text-accent-cyan'
      case 'pending': return 'bg-accent-amber/20 text-accent-amber'
      case 'rejected': return 'bg-accent-red/20 text-accent-red'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <DollarSign className="text-accent-green" size={28} />
            Distribution Dashboard
          </h1>
          <p className="text-gray-400">Monetize your content across multiple platforms</p>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={() => {
            refetchAccounts()
            refetchContent()
          }}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-dark-border pb-2 overflow-x-auto">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-bg'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent-green/20 flex items-center justify-center">
                  <DollarSign size={24} className="text-accent-green" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Total Revenue</p>
                  <p className="text-2xl font-bold">${(stats.total_revenue || 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                  <Package size={24} className="text-accent-cyan" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Published Items</p>
                  <p className="text-2xl font-bold">{stats.published || 0}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent-amber/20 flex items-center justify-center">
                  <ShoppingBag size={24} className="text-accent-amber" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Total Sales</p>
                  <p className="text-2xl font-bold">{stats.total_sales || 0}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                  <Globe size={24} className="text-accent-purple" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Connected Platforms</p>
                  <p className="text-2xl font-bold">{connectedAccounts.length}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Connected Platforms */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Link2 size={18} className="text-accent-cyan" />
                  Connected Platforms
                </h3>
                <button
                  className="text-sm text-gray-400 hover:text-white flex items-center gap-1"
                  onClick={() => setActiveTab('platforms')}
                >
                  Manage <ArrowUpRight size={14} />
                </button>
              </div>
              {loadingAccounts ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                </div>
              ) : connectedAccounts.length > 0 ? (
                <div className="space-y-3">
                  {connectedAccounts.slice(0, 5).map((account) => (
                    <div
                      key={account.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-dark-bg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-accent-green/20 flex items-center justify-center">
                          <CheckCircle size={20} className="text-accent-green" />
                        </div>
                        <div>
                          <p className="font-medium">{account.platform_name || account.platform}</p>
                          {account.username && (
                            <p className="text-xs text-gray-400">@{account.username}</p>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-accent-green">
                          ${(account.total_revenue || 0).toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-400">{account.item_count || 0} items</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Globe className="mx-auto mb-2 opacity-50" size={32} />
                  <p>No platforms connected</p>
                  <button
                    className="btn btn-secondary text-sm mt-2"
                    onClick={() => setActiveTab('platforms')}
                  >
                    Connect a Platform
                  </button>
                </div>
              )}
            </div>

            {/* Recent Distributions */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Package size={18} className="text-accent-amber" />
                  Recent Distributions
                </h3>
                <button
                  className="text-sm text-gray-400 hover:text-white flex items-center gap-1"
                  onClick={() => setActiveTab('content')}
                >
                  View All <ArrowUpRight size={14} />
                </button>
              </div>
              {loadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                </div>
              ) : distributions.length > 0 ? (
                <div className="space-y-3">
                  {distributions.slice(0, 5).map((dist) => (
                    <div
                      key={dist.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-dark-bg"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        {dist.thumbnail_url ? (
                          <img
                            src={dist.thumbnail_url}
                            alt={dist.title}
                            className="h-10 w-10 rounded-lg object-cover"
                          />
                        ) : (
                          <div className="h-10 w-10 rounded-lg bg-dark-border flex items-center justify-center">
                            <Package size={20} className="text-gray-500" />
                          </div>
                        )}
                        <div className="min-w-0">
                          <p className="font-medium truncate">{dist.title}</p>
                          <p className="text-xs text-gray-400">{dist.platform_name || dist.platform}</p>
                        </div>
                      </div>
                      <span className={cn('px-2 py-0.5 text-xs rounded', getStatusColor(dist.status))}>
                        {dist.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Package className="mx-auto mb-2 opacity-50" size={32} />
                  <p>No distributions yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Zap size={18} className="text-accent-amber" />
                Recommendations
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.slice(0, 6).map((rec: { id: string; title: string; description?: string; potential_revenue?: number; platform?: string }, idx: number) => (
                  <div
                    key={rec.id || idx}
                    className="p-4 rounded-lg border border-dark-border hover:border-accent-amber/50 transition-colors"
                  >
                    <p className="font-medium text-sm mb-2">{rec.title}</p>
                    {rec.description && (
                      <p className="text-xs text-gray-400 mb-2 line-clamp-2">{rec.description}</p>
                    )}
                    <div className="flex items-center justify-between text-xs">
                      {rec.platform && (
                        <span className="text-gray-500">{rec.platform}</span>
                      )}
                      {rec.potential_revenue && (
                        <span className="text-accent-green">+${rec.potential_revenue}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Platforms Tab */}
      {activeTab === 'platforms' && (
        <div className="space-y-6">
          {/* Connected Accounts */}
          <div className="card">
            <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <CheckCircle size={18} className="text-accent-green" />
              Connected Accounts ({connectedAccounts.length})
            </h3>
            {loadingAccounts ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : connectedAccounts.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {connectedAccounts.map((account) => (
                  <div
                    key={account.id}
                    className="p-4 rounded-lg border border-accent-green/30 bg-accent-green/5"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <CheckCircle size={16} className="text-accent-green" />
                        <span className="font-medium">{account.platform_name || account.platform}</span>
                      </div>
                      <button className="text-gray-400 hover:text-white">
                        <Settings size={16} />
                      </button>
                    </div>
                    {account.username && (
                      <p className="text-sm text-gray-400 mb-2">@{account.username}</p>
                    )}
                    {account.store_name && (
                      <p className="text-sm text-gray-400 mb-2">{account.store_name}</p>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">{account.item_count || 0} items</span>
                      <span className="text-accent-green font-medium">
                        ${(account.total_revenue || 0).toLocaleString()}
                      </span>
                    </div>
                    {account.connected_at && (
                      <p className="text-xs text-gray-500 mt-2">
                        Connected {new Date(account.connected_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Globe className="mx-auto mb-2 opacity-50" size={32} />
                <p>No accounts connected yet</p>
              </div>
            )}
          </div>

          {/* Available Platforms */}
          <div className="card">
            <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <Globe size={18} className="text-primary-400" />
              Available Platforms
            </h3>
            {loadingPlatforms ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : platforms.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {platforms.map((platform) => {
                  const isConnected = accounts.some(
                    a => a.platform === platform.slug && a.is_connected
                  )
                  return (
                    <div
                      key={platform.id}
                      className={cn(
                        'p-4 rounded-lg border transition-colors',
                        isConnected
                          ? 'border-accent-green/30 bg-accent-green/5'
                          : 'border-dark-border hover:border-primary-500/50'
                      )}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{platform.name}</span>
                        {isConnected ? (
                          <CheckCircle size={16} className="text-accent-green" />
                        ) : (
                          <XCircle size={16} className="text-gray-500" />
                        )}
                      </div>
                      <p className="text-xs text-gray-400 mb-3 line-clamp-2">
                        {platform.description || `Sell on ${platform.name}`}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">
                          {platform.category}
                        </span>
                        {!isConnected && (
                          <button className="btn btn-secondary text-xs py-1 px-2">
                            Connect
                          </button>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Globe className="mx-auto mb-2 opacity-50" size={32} />
                <p>No platforms available</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Content Tab */}
      {activeTab === 'content' && (
        <div className="space-y-6">
          {/* Content Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card p-4">
              <p className="text-sm text-gray-400">Total</p>
              <p className="text-2xl font-bold">{stats.total_distributions || 0}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-400">Published</p>
              <p className="text-2xl font-bold text-accent-green">{stats.published || 0}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-400">Pending</p>
              <p className="text-2xl font-bold text-accent-amber">{stats.pending || 0}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-gray-400">Sales</p>
              <p className="text-2xl font-bold text-accent-cyan">{stats.total_sales || 0}</p>
            </div>
          </div>

          {/* Content List */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">All Distributions</h3>
              <button className="btn btn-primary text-sm">
                New Distribution
              </button>
            </div>
            {loadingContent ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : distributions.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-dark-border text-left text-sm text-gray-400">
                      <th className="pb-3 font-medium">Item</th>
                      <th className="pb-3 font-medium">Platform</th>
                      <th className="pb-3 font-medium">Status</th>
                      <th className="pb-3 font-medium">Price</th>
                      <th className="pb-3 font-medium">Sales</th>
                      <th className="pb-3 font-medium">Revenue</th>
                      <th className="pb-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {distributions.map((dist) => (
                      <tr key={dist.id} className="border-b border-dark-border">
                        <td className="py-3">
                          <div className="flex items-center gap-3">
                            {dist.thumbnail_url ? (
                              <img
                                src={dist.thumbnail_url}
                                alt={dist.title}
                                className="h-10 w-10 rounded object-cover"
                              />
                            ) : (
                              <div className="h-10 w-10 rounded bg-dark-bg flex items-center justify-center">
                                <Package size={16} className="text-gray-500" />
                              </div>
                            )}
                            <span className="font-medium truncate max-w-[200px]">{dist.title}</span>
                          </div>
                        </td>
                        <td className="py-3 text-gray-400">{dist.platform_name || dist.platform}</td>
                        <td className="py-3">
                          <span className={cn('px-2 py-0.5 text-xs rounded', getStatusColor(dist.status))}>
                            {dist.status}
                          </span>
                        </td>
                        <td className="py-3">${(dist.price || 0).toFixed(2)}</td>
                        <td className="py-3">{dist.sales_count || 0}</td>
                        <td className="py-3 text-accent-green">${(dist.revenue || 0).toFixed(2)}</td>
                        <td className="py-3">
                          <div className="flex items-center gap-2">
                            <button className="text-gray-400 hover:text-white">
                              <Eye size={16} />
                            </button>
                            <button className="text-gray-400 hover:text-white">
                              <ExternalLink size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Package className="mx-auto mb-2 opacity-50" size={32} />
                <p>No distributions yet</p>
                <p className="text-sm text-gray-500 mt-1">Create your first distribution to start selling</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Revenue Tab */}
      {activeTab === 'revenue' && (
        <div className="space-y-6">
          {/* Revenue Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent-green/20 flex items-center justify-center">
                  <DollarSign size={24} className="text-accent-green" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Total Revenue</p>
                  <p className="text-2xl font-bold">${(revenue.total_revenue || 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                  <TrendingUp size={24} className="text-accent-cyan" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">This Month</p>
                  <p className="text-2xl font-bold">${(revenue.this_month || 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-gray-500/20 flex items-center justify-center">
                  <BarChart3 size={24} className="text-gray-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Last Month</p>
                  <p className="text-2xl font-bold">${(revenue.last_month || 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent-amber/20 flex items-center justify-center">
                  <Clock size={24} className="text-accent-amber" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Pending</p>
                  <p className="text-2xl font-bold">${(revenue.pending || 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Platform Comparison */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <BarChart3 size={18} className="text-primary-400" />
                Revenue by Platform
              </h3>
              <button
                className="btn btn-secondary text-sm flex items-center gap-2"
                onClick={() => connectedAccounts.forEach(a => syncRevenueMutation.mutate(a.platform))}
                disabled={syncRevenueMutation.isPending}
              >
                {syncRevenueMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                Sync All
              </button>
            </div>
            {loadingRevenue ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : platformComparison.length > 0 ? (
              <div className="space-y-4">
                {platformComparison.map((p: { platform: string; revenue: number; growth?: number; item_count?: number }) => {
                  const maxRevenue = Math.max(...platformComparison.map((x: { revenue: number }) => x.revenue))
                  const percentage = maxRevenue > 0 ? (p.revenue / maxRevenue) * 100 : 0
                  return (
                    <div key={p.platform} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{p.platform}</span>
                        <div className="flex items-center gap-4">
                          <span className="text-sm text-gray-400">{p.item_count || 0} items</span>
                          <span className="font-bold text-accent-green">${p.revenue.toLocaleString()}</span>
                          {p.growth !== undefined && (
                            <span className={cn(
                              'text-sm',
                              p.growth >= 0 ? 'text-accent-green' : 'text-accent-red'
                            )}>
                              {p.growth >= 0 ? '+' : ''}{p.growth}%
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-accent-green to-accent-cyan rounded-full transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : revenue.by_platform && Object.keys(revenue.by_platform).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(revenue.by_platform).map(([platform, amount]) => {
                  const maxRevenue = Math.max(...Object.values(revenue.by_platform as Record<string, number>))
                  const percentage = maxRevenue > 0 ? ((amount as number) / maxRevenue) * 100 : 0
                  return (
                    <div key={platform} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{platform}</span>
                        <span className="font-bold text-accent-green">${(amount as number).toLocaleString()}</span>
                      </div>
                      <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-accent-green to-accent-cyan rounded-full transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <BarChart3 className="mx-auto mb-2 opacity-50" size={32} />
                <p>No revenue data available</p>
                <p className="text-sm text-gray-500 mt-1">Connect platforms and make sales to see revenue</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Scheduled Tab */}
      {activeTab === 'scheduled' && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Calendar size={18} className="text-accent-cyan" />
                Scheduled Distributions
              </h3>
              <button className="btn btn-primary text-sm">
                Schedule New
              </button>
            </div>
            {loadingScheduled ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin" size={24} />
              </div>
            ) : scheduled.length > 0 ? (
              <div className="space-y-3">
                {scheduled.map((item: { id: string; title: string; platform: string; scheduled_for: string; status: string }) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-dark-border"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                        <Calendar size={20} className="text-accent-cyan" />
                      </div>
                      <div>
                        <p className="font-medium">{item.title}</p>
                        <p className="text-sm text-gray-400">{item.platform}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-medium">
                          {new Date(item.scheduled_for).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-gray-400">
                          {new Date(item.scheduled_for).toLocaleTimeString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button className="text-gray-400 hover:text-white">
                          <Pause size={16} />
                        </button>
                        <button className="text-gray-400 hover:text-accent-red">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Calendar className="mx-auto mb-2 opacity-50" size={32} />
                <p>No scheduled distributions</p>
                <p className="text-sm text-gray-500 mt-1">Schedule content to be distributed automatically</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
