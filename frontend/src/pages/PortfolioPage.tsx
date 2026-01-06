import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { portfolioApi } from '@/lib/api'
import {
  DollarSign, TrendingUp, TrendingDown, BarChart3, PieChart,
  Loader2, CheckCircle, XCircle, Download, Youtube, Instagram,
  Twitter, Globe, Play, Eye, ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'overview' | 'revenue' | 'channels' | 'content' | 'analytics'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface RevenueData {
  total: number
  this_month: number
  last_month: number
  growth_percent: number
}

interface Channel {
  id: string
  name: string
  platform: string
  subscribers: number
  revenue: number
  views: number
  status: 'active' | 'paused'
}

interface ContentItem {
  id: string
  title: string
  channel: string
  views: number
  revenue: number
  engagement_rate: number
  published_at: string
}

const tabs = [
  { id: 'overview' as TabType, label: 'Overview', icon: PieChart },
  { id: 'revenue' as TabType, label: 'Revenue', icon: DollarSign },
  { id: 'channels' as TabType, label: 'Channels', icon: Globe },
  { id: 'content' as TabType, label: 'Top Content', icon: Play },
  { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
]

const platformIcons: Record<string, React.ElementType> = {
  youtube: Youtube,
  instagram: Instagram,
  twitter: Twitter,
  web: Globe,
}

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

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

export default function PortfolioPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)

  // Fetch overview
  const { data: overviewData, isLoading: loadingOverview } = useQuery({
    queryKey: ['portfolio-overview'],
    queryFn: () => portfolioApi.overview(),
  })

  // Fetch revenue
  const { data: revenueData, isLoading: loadingRevenue } = useQuery({
    queryKey: ['portfolio-revenue'],
    queryFn: () => portfolioApi.revenue(),
    enabled: activeTab === 'revenue' || activeTab === 'overview',
  })

  // Fetch channels
  const { data: channelsData, isLoading: loadingChannels } = useQuery({
    queryKey: ['portfolio-channels'],
    queryFn: () => portfolioApi.channels(),
    enabled: activeTab === 'channels' || activeTab === 'overview',
  })

  // Fetch top content
  const { data: contentData, isLoading: loadingContent } = useQuery({
    queryKey: ['portfolio-top-content'],
    queryFn: () => portfolioApi.topContent(),
    enabled: activeTab === 'content',
  })

  // Fetch analytics
  const { data: analyticsData, isLoading: loadingAnalytics } = useQuery({
    queryKey: ['portfolio-analytics'],
    queryFn: () => portfolioApi.analytics(),
    enabled: activeTab === 'analytics',
  })

  const overview = overviewData?.data || {}
  const revenue: RevenueData = revenueData?.data || { total: 0, this_month: 0, last_month: 0, growth_percent: 0 }
  const channels: Channel[] = channelsData?.data?.channels || channelsData?.data || []
  const topContent: ContentItem[] = contentData?.data?.content || contentData?.data || []
  const analytics = analyticsData?.data || {}

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const response = await portfolioApi.exportRevenue(format)
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `revenue-export.${format}`
      a.click()
      setActionResult({ type: 'success', message: `Exported as ${format.toUpperCase()}` })
    } catch {
      setActionResult({ type: 'error', message: 'Export failed' })
    }
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
            <p className="text-gray-400">Revenue tracking and content distribution</p>
          </div>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={() => handleExport('csv')}
        >
          <Download size={16} />
          Export Data
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
          {loadingOverview ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Revenue Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Total Revenue</p>
                      <p className="text-2xl font-bold">{formatCurrency(revenue.total || overview.total_revenue || 0)}</p>
                    </div>
                    <DollarSign className="text-accent-green" size={24} />
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">This Month</p>
                      <p className="text-2xl font-bold">{formatCurrency(revenue.this_month || 0)}</p>
                      {revenue.growth_percent !== 0 && (
                        <p className={cn('text-xs flex items-center gap-1', revenue.growth_percent > 0 ? 'text-accent-green' : 'text-accent-red')}>
                          {revenue.growth_percent > 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                          {Math.abs(revenue.growth_percent)}% vs last month
                        </p>
                      )}
                    </div>
                    <BarChart3 className="text-primary-400" size={24} />
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Total Views</p>
                      <p className="text-2xl font-bold">{formatNumber(overview.total_views || 0)}</p>
                    </div>
                    <Eye className="text-accent-cyan" size={24} />
                  </div>
                </div>
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Active Channels</p>
                      <p className="text-2xl font-bold">{channels.filter(c => c.status === 'active').length || overview.active_channels || 0}</p>
                    </div>
                    <Globe className="text-accent-amber" size={24} />
                  </div>
                </div>
              </div>

              {/* Channels & Content */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Top Channels */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Top Channels</h3>
                  {loadingChannels ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="animate-spin" size={24} />
                    </div>
                  ) : channels.length > 0 ? (
                    <div className="space-y-3">
                      {channels.slice(0, 5).map((channel) => {
                        const PlatformIcon = platformIcons[channel.platform.toLowerCase()] || Globe
                        return (
                          <div
                            key={channel.id}
                            className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                          >
                            <div className="flex items-center gap-3">
                              <div className="h-10 w-10 rounded-lg bg-dark-bg flex items-center justify-center">
                                <PlatformIcon size={20} className="text-primary-400" />
                              </div>
                              <div>
                                <p className="font-medium text-sm">{channel.name}</p>
                                <p className="text-xs text-gray-500">{formatNumber(channel.subscribers)} subscribers</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-accent-green">{formatCurrency(channel.revenue)}</p>
                              <p className="text-xs text-gray-500">{formatNumber(channel.views)} views</p>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <Globe className="mx-auto mb-2" size={32} />
                      <p>No channels connected</p>
                    </div>
                  )}
                </div>

                {/* Revenue Breakdown */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Revenue Breakdown</h3>
                  <div className="space-y-4">
                    {channels.length > 0 ? (
                      channels.slice(0, 5).map((channel) => {
                        const percentage = revenue.total > 0 ? (channel.revenue / revenue.total) * 100 : 0
                        return (
                          <div key={channel.id}>
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm">{channel.name}</span>
                              <span className="text-sm font-medium">{formatCurrency(channel.revenue)}</span>
                            </div>
                            <div className="w-full h-2 bg-dark-bg rounded-full overflow-hidden">
                              <div
                                className="h-full bg-accent-green rounded-full"
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                          </div>
                        )
                      })
                    ) : (
                      <div className="text-center py-8 text-gray-400">
                        <PieChart className="mx-auto mb-2" size={32} />
                        <p>No revenue data</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </>
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
                  <p className="text-3xl font-bold text-accent-green">{formatCurrency(revenue.total)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">This Month</p>
                  <p className="text-2xl font-bold">{formatCurrency(revenue.this_month)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Last Month</p>
                  <p className="text-2xl font-bold">{formatCurrency(revenue.last_month)}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Growth</p>
                  <p className={cn('text-2xl font-bold flex items-center gap-2', revenue.growth_percent >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                    {revenue.growth_percent >= 0 ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                    {Math.abs(revenue.growth_percent)}%
                  </p>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Revenue by Channel</h3>
                  <div className="flex gap-2">
                    <button
                      className="btn btn-secondary text-sm"
                      onClick={() => handleExport('json')}
                    >
                      JSON
                    </button>
                    <button
                      className="btn btn-secondary text-sm"
                      onClick={() => handleExport('csv')}
                    >
                      CSV
                    </button>
                  </div>
                </div>
                {channels.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-400 border-b border-dark-border">
                          <th className="pb-3">Channel</th>
                          <th className="pb-3">Platform</th>
                          <th className="pb-3 text-right">Revenue</th>
                          <th className="pb-3 text-right">Views</th>
                          <th className="pb-3 text-right">RPM</th>
                        </tr>
                      </thead>
                      <tbody>
                        {channels.map((channel) => (
                          <tr key={channel.id} className="border-b border-dark-border hover:bg-dark-bg/50">
                            <td className="py-3 font-medium">{channel.name}</td>
                            <td className="py-3 capitalize">{channel.platform}</td>
                            <td className="py-3 text-right text-accent-green">{formatCurrency(channel.revenue)}</td>
                            <td className="py-3 text-right">{formatNumber(channel.views)}</td>
                            <td className="py-3 text-right">
                              ${channel.views > 0 ? ((channel.revenue / channel.views) * 1000).toFixed(2) : '0.00'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <DollarSign className="mx-auto mb-2" size={48} />
                    <p>No revenue data available</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* Channels Tab */}
      {activeTab === 'channels' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Distribution Channels</h3>
          {loadingChannels ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : channels.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {channels.map((channel) => {
                const PlatformIcon = platformIcons[channel.platform.toLowerCase()] || Globe
                return (
                  <div
                    key={channel.id}
                    className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="h-12 w-12 rounded-lg bg-dark-bg flex items-center justify-center">
                        <PlatformIcon size={24} className="text-primary-400" />
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        channel.status === 'active' ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-amber/20 text-accent-amber'
                      )}>
                        {channel.status}
                      </span>
                    </div>
                    <h4 className="font-medium mb-1">{channel.name}</h4>
                    <p className="text-sm text-gray-400 capitalize mb-3">{channel.platform}</p>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <p className="text-sm font-medium">{formatNumber(channel.subscribers)}</p>
                        <p className="text-xs text-gray-500">Subs</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">{formatNumber(channel.views)}</p>
                        <p className="text-xs text-gray-500">Views</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-accent-green">{formatCurrency(channel.revenue)}</p>
                        <p className="text-xs text-gray-500">Revenue</p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Globe className="mx-auto mb-2" size={48} />
              <p>No channels connected</p>
              <p className="text-sm text-gray-500 mt-1">Connect your distribution channels to track performance</p>
            </div>
          )}
        </div>
      )}

      {/* Top Content Tab */}
      {activeTab === 'content' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Top Performing Content</h3>
          {loadingContent ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : topContent.length > 0 ? (
            <div className="space-y-3">
              {topContent.map((item, idx) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center text-lg font-bold text-primary-400">
                      {idx + 1}
                    </div>
                    <div>
                      <p className="font-medium">{item.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{item.channel}</span>
                        <span className="text-xs text-gray-500">{new Date(item.published_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="font-medium">{formatNumber(item.views)}</p>
                      <p className="text-xs text-gray-500">views</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-accent-green">{formatCurrency(item.revenue)}</p>
                      <p className="text-xs text-gray-500">revenue</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{item.engagement_rate.toFixed(1)}%</p>
                      <p className="text-xs text-gray-500">engagement</p>
                    </div>
                    <ChevronRight size={16} className="text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Play className="mx-auto mb-2" size={48} />
              <p>No content data available</p>
              <p className="text-sm text-gray-500 mt-1">Publish content to see performance metrics</p>
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {loadingAnalytics ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Avg. RPM</p>
                  <p className="text-2xl font-bold">${analytics.avg_rpm?.toFixed(2) || '0.00'}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Avg. Engagement</p>
                  <p className="text-2xl font-bold">{analytics.avg_engagement?.toFixed(1) || 0}%</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Total Content</p>
                  <p className="text-2xl font-bold">{analytics.total_content || 0}</p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-400 mb-1">Best Day</p>
                  <p className="text-2xl font-bold">{analytics.best_day || 'N/A'}</p>
                </div>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Performance Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <h4 className="font-medium mb-2">Best Performing Platform</h4>
                    <p className="text-2xl font-bold text-primary-400">{analytics.best_platform || 'YouTube'}</p>
                    <p className="text-sm text-gray-400 mt-1">{analytics.best_platform_revenue ? formatCurrency(analytics.best_platform_revenue) : 'No data'} in revenue</p>
                  </div>
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <h4 className="font-medium mb-2">Best Content Type</h4>
                    <p className="text-2xl font-bold text-accent-green">{analytics.best_content_type || 'Video'}</p>
                    <p className="text-sm text-gray-400 mt-1">{analytics.best_type_engagement?.toFixed(1) || 0}% avg engagement</p>
                  </div>
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <h4 className="font-medium mb-2">Peak Hours</h4>
                    <p className="text-2xl font-bold text-accent-amber">{analytics.peak_hours || '2PM - 6PM'}</p>
                    <p className="text-sm text-gray-400 mt-1">Best time to publish</p>
                  </div>
                  <div className="p-4 rounded-lg bg-dark-bg">
                    <h4 className="font-medium mb-2">Growth Trend</h4>
                    <p className={cn('text-2xl font-bold flex items-center gap-2', (analytics.growth_trend || 0) >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                      {(analytics.growth_trend || 0) >= 0 ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                      {Math.abs(analytics.growth_trend || 0)}%
                    </p>
                    <p className="text-sm text-gray-400 mt-1">Month over month</p>
                  </div>
                </div>
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
