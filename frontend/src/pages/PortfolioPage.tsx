import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { portfolioApi } from '@/lib/api'
import {
  DollarSign, BarChart3, PieChart,
  Loader2, CheckCircle, XCircle,
  Globe, ChevronRight, Package, Link2
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'overview' | 'platforms' | 'content' | 'revenue'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface Platform {
  id: string
  name: string
  slug?: string
  description?: string
  status?: string
  connected?: boolean
}

interface Distribution {
  id: string
  title?: string
  content_type?: string
  status?: string
  platform?: string
  created_at?: string
}

const tabs = [
  { id: 'overview' as TabType, label: 'Overview', icon: PieChart },
  { id: 'platforms' as TabType, label: 'Platforms', icon: Globe },
  { id: 'content' as TabType, label: 'Content', icon: Package },
  { id: 'revenue' as TabType, label: 'Revenue', icon: DollarSign },
]

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function PortfolioPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)

  // Fetch stats
  const { data: statsData, isLoading: loadingStats } = useQuery({
    queryKey: ['portfolio-stats'],
    queryFn: () => portfolioApi.stats(),
  })

  // Fetch platforms
  const { data: platformsData, isLoading: loadingPlatforms } = useQuery({
    queryKey: ['portfolio-platforms'],
    queryFn: () => portfolioApi.platforms(),
  })

  // Fetch accounts
  const { data: accountsData } = useQuery({
    queryKey: ['portfolio-accounts'],
    queryFn: () => portfolioApi.accounts(),
  })

  // Fetch content
  const { data: contentData, isLoading: loadingContent } = useQuery({
    queryKey: ['portfolio-content'],
    queryFn: () => portfolioApi.content(),
    enabled: activeTab === 'content' || activeTab === 'overview',
  })

  // Fetch revenue dashboard
  const { data: revenueData, isLoading: loadingRevenue } = useQuery({
    queryKey: ['portfolio-revenue'],
    queryFn: () => portfolioApi.revenueDashboard(),
    enabled: activeTab === 'revenue' || activeTab === 'overview',
  })

  const stats = statsData?.data || {}
  const platforms: Platform[] = platformsData?.data?.platforms || platformsData?.data || []
  const accounts = accountsData?.data?.accounts || accountsData?.data || []
  const content: Distribution[] = contentData?.data?.distributions || contentData?.data || []
  const revenue = revenueData?.data || {}

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-accent-green/20 flex items-center justify-center">
            <DollarSign size={28} className="text-accent-green" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Portfolio</h1>
            <p className="text-gray-400">Content distribution and revenue tracking</p>
          </div>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={() => setActionResult({ type: 'success', message: 'Connect platform coming soon!' })}
        >
          <Link2 size={16} />
          Connect Platform
        </button>
      </div>

      {/* Tabs */}
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
          {loadingStats ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Total Revenue</p>
                      <p className="text-2xl font-bold">{formatCurrency(stats.total_revenue || revenue.total || 0)}</p>
                    </div>
                    <DollarSign className="text-accent-green" size={24} />
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Platforms</p>
                      <p className="text-2xl font-bold">{stats.platforms || platforms.length}</p>
                    </div>
                    <Globe className="text-primary-400" size={24} />
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Connected</p>
                      <p className="text-2xl font-bold">{stats.connected || accounts.length}</p>
                    </div>
                    <Link2 className="text-accent-cyan" size={24} />
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Distributions</p>
                      <p className="text-2xl font-bold">{stats.distributions || content.length}</p>
                    </div>
                    <Package className="text-accent-amber" size={24} />
                  </div>
                </div>
              </div>

              {/* Platforms & Content */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Platforms */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Distribution Platforms</h3>
                  {loadingPlatforms ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="animate-spin" size={24} />
                    </div>
                  ) : platforms.length > 0 ? (
                    <div className="space-y-3">
                      {platforms.slice(0, 5).map((platform) => (
                        <div
                          key={platform.id}
                          className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                        >
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-lg bg-dark-bg flex items-center justify-center">
                              <Globe size={20} className="text-primary-400" />
                            </div>
                            <div>
                              <p className="font-medium text-sm">{platform.name}</p>
                              <p className="text-xs text-gray-500">{platform.slug || platform.description || 'Platform'}</p>
                            </div>
                          </div>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded',
                            platform.connected ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                          )}>
                            {platform.connected ? 'Connected' : 'Available'}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <Globe className="mx-auto mb-2" size={32} />
                      <p>No platforms available</p>
                    </div>
                  )}
                </div>

                {/* Recent Content */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Recent Distributions</h3>
                  {loadingContent ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="animate-spin" size={24} />
                    </div>
                  ) : content.length > 0 ? (
                    <div className="space-y-3">
                      {content.slice(0, 5).map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                        >
                          <div className="flex items-center gap-3">
                            <Package size={18} className="text-accent-amber" />
                            <div>
                              <p className="font-medium text-sm">{item.title || 'Untitled'}</p>
                              <p className="text-xs text-gray-500">{item.content_type || 'Content'}</p>
                            </div>
                          </div>
                          <span className={cn(
                            'text-xs px-2 py-1 rounded',
                            item.status === 'published' ? 'bg-accent-green/20 text-accent-green' :
                            item.status === 'pending' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                          )}>
                            {item.status || 'draft'}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <Package className="mx-auto mb-2" size={32} />
                      <p>No distributions yet</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Platforms Tab */}
      {activeTab === 'platforms' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Distribution Platforms</h3>
          {loadingPlatforms ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : platforms.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {platforms.map((platform) => (
                <div
                  key={platform.id}
                  className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="h-12 w-12 rounded-lg bg-dark-bg flex items-center justify-center">
                      <Globe size={24} className="text-primary-400" />
                    </div>
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      platform.connected ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                    )}>
                      {platform.connected ? 'Connected' : 'Available'}
                    </span>
                  </div>
                  <h4 className="font-medium mb-1">{platform.name}</h4>
                  <p className="text-sm text-gray-400 mb-3">{platform.description || 'Distribution platform'}</p>
                  <button
                    className="btn btn-secondary text-sm w-full"
                    onClick={() => setActionResult({ type: 'success', message: `${platform.connected ? 'Manage' : 'Connect'} ${platform.name}` })}
                  >
                    {platform.connected ? 'Manage' : 'Connect'}
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Globe className="mx-auto mb-2" size={48} />
              <p>No platforms available</p>
              <p className="text-sm text-gray-500 mt-1">Check back later for distribution platforms</p>
            </div>
          )}
        </div>
      )}

      {/* Content Tab */}
      {activeTab === 'content' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Distributed Content</h3>
          {loadingContent ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : content.length > 0 ? (
            <div className="space-y-3">
              {content.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-accent-amber/20 flex items-center justify-center">
                      <Package size={20} className="text-accent-amber" />
                    </div>
                    <div>
                      <p className="font-medium">{item.title || 'Untitled'}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{item.content_type || 'Content'}</span>
                        <span className="text-xs text-gray-500">{item.platform || 'Multiple'}</span>
                        <span className="text-xs text-gray-500">
                          {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      item.status === 'published' ? 'bg-accent-green/20 text-accent-green' :
                      item.status === 'pending' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                    )}>
                      {item.status || 'draft'}
                    </span>
                    <ChevronRight size={16} className="text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Package className="mx-auto mb-2" size={48} />
              <p>No content distributed</p>
              <p className="text-sm text-gray-500 mt-1">Distribute your first piece of content</p>
            </div>
          )}
        </div>
      )}

      {/* Revenue Tab */}
      {activeTab === 'revenue' && (
        <div className="space-y-6">
          {loadingRevenue ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-accent-green/20 to-accent-green/5">
                  <p className="text-sm text-gray-400 mb-1">Total Revenue</p>
                  <p className="text-3xl font-bold text-accent-green">{formatCurrency(revenue.total || 0)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">This Month</p>
                  <p className="text-2xl font-bold">{formatCurrency(revenue.this_month || 0)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Last Month</p>
                  <p className="text-2xl font-bold">{formatCurrency(revenue.last_month || 0)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Pending</p>
                  <p className="text-2xl font-bold text-accent-amber">{formatCurrency(revenue.pending || 0)}</p>
                </div>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Revenue by Platform</h3>
                {revenue.by_platform && Object.keys(revenue.by_platform).length > 0 ? (
                  <div className="space-y-4">
                    {Object.entries(revenue.by_platform).map(([platform, amount]) => (
                      <div key={platform} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Globe size={18} className="text-primary-400" />
                          <span className="capitalize">{platform}</span>
                        </div>
                        <span className="font-medium text-accent-green">{formatCurrency(Number(amount) || 0)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <BarChart3 className="mx-auto mb-2" size={32} />
                    <p>No revenue data available</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
