import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { analyticsApi } from '@/lib/api'
import { cn } from '@/lib/cn'
import {
  BarChart3,
  LineChart,
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  Bot,
  DollarSign,
  FileText,
  Download,
  AlertTriangle,
  Zap,
  Target,
  Loader2,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'

// Types
interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    color?: string
  }>
}

interface TopPerformer {
  id: string
  name: string
  category: string
  score: number
  change?: number
}

interface Anomaly {
  id: string
  metric: string
  description: string
  severity: 'high' | 'medium' | 'low'
  detected_at: string
  value?: number
  expected?: number
}

interface Report {
  id: string
  name: string
  type: string
  status: 'ready' | 'generating' | 'scheduled'
  created_at?: string
  size?: string
  format?: string
}

interface Forecast {
  metric: string
  current: number
  predicted: number
  confidence: number
  trend: 'up' | 'down' | 'stable'
}

type TabType = 'overview' | 'charts' | 'insights' | 'reports'
type PeriodType = '7d' | '30d' | '90d' | '1y'

export default function AnalyticsDashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [period, setPeriod] = useState<PeriodType>('30d')
  const [selectedChart, setSelectedChart] = useState<string>('agent-activity')
  const queryClient = useQueryClient()

  const periodDays = {
    '7d': 7,
    '30d': 30,
    '90d': 90,
    '1y': 365,
  }

  // Queries
  const { data: overviewData, isLoading: loadingOverview } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: () => analyticsApi.overview(),
  })

  const { data: summaryData } = useQuery({
    queryKey: ['analytics-summary', period],
    queryFn: () => analyticsApi.summary({ period }),
  })

  const { data: agentActivityData, isLoading: loadingAgentActivity } = useQuery({
    queryKey: ['analytics-agent-activity', period],
    queryFn: () => analyticsApi.charts.agentActivity({ days: periodDays[period] }),
    enabled: activeTab === 'charts' && selectedChart === 'agent-activity',
  })

  const { data: revenueData, isLoading: loadingRevenue } = useQuery({
    queryKey: ['analytics-revenue', period],
    queryFn: () => analyticsApi.charts.revenue({ days: periodDays[period] }),
    enabled: activeTab === 'charts' && selectedChart === 'revenue',
  })

  const { data: contentData, isLoading: loadingContent } = useQuery({
    queryKey: ['analytics-content', period],
    queryFn: () => analyticsApi.charts.contentProduction({ days: periodDays[period] }),
    enabled: activeTab === 'charts' && selectedChart === 'content',
  })

  const { data: systemHealthData, isLoading: loadingHealth } = useQuery({
    queryKey: ['analytics-health', period],
    queryFn: () => analyticsApi.charts.systemHealth({ days: periodDays[period] }),
    enabled: activeTab === 'charts' && selectedChart === 'system-health',
  })

  const { data: topPerformersData, isLoading: loadingPerformers } = useQuery({
    queryKey: ['analytics-top-performers'],
    queryFn: () => analyticsApi.v2.topPerformers({ limit: 10 }),
    enabled: activeTab === 'insights',
  })

  const { data: anomaliesData, isLoading: loadingAnomalies } = useQuery({
    queryKey: ['analytics-anomalies'],
    queryFn: () => analyticsApi.v2.anomalies(),
    enabled: activeTab === 'insights',
  })

  const { data: forecastData, isLoading: loadingForecast } = useQuery({
    queryKey: ['analytics-forecast'],
    queryFn: () => analyticsApi.v2.forecast({ days: 30 }),
    enabled: activeTab === 'insights',
  })

  const { data: reportsData, isLoading: loadingReports } = useQuery({
    queryKey: ['analytics-reports'],
    queryFn: () => analyticsApi.reports.list(),
    enabled: activeTab === 'reports',
  })

  // Mutations
  const generateReport = useMutation({
    mutationFn: (type: string) => analyticsApi.reports.generate({ type, period }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analytics-reports'] })
    },
  })

  // Data extraction
  const overview = overviewData?.data || {}
  const summary = summaryData?.data || {}
  const rawAgentActivity = agentActivityData?.data
  const agentActivity: ChartData = rawAgentActivity || { labels: [], datasets: [] }
  const rawRevenue = revenueData?.data
  const revenue: ChartData = rawRevenue || { labels: [], datasets: [] }
  const rawContent = contentData?.data
  const content: ChartData = rawContent || { labels: [], datasets: [] }
  const rawHealth = systemHealthData?.data
  const systemHealth: ChartData = rawHealth || { labels: [], datasets: [] }
  const rawPerformers = topPerformersData?.data?.performers || topPerformersData?.data
  const topPerformers: TopPerformer[] = Array.isArray(rawPerformers) ? rawPerformers : []
  const rawAnomalies = anomaliesData?.data?.anomalies || anomaliesData?.data
  const anomalies: Anomaly[] = Array.isArray(rawAnomalies) ? rawAnomalies : []
  const rawForecast = forecastData?.data?.forecasts || forecastData?.data
  const forecasts: Forecast[] = Array.isArray(rawForecast) ? rawForecast : []
  const rawReports = reportsData?.data?.reports || reportsData?.data
  const reports: Report[] = Array.isArray(rawReports) ? rawReports : []

  const tabs = [
    { id: 'overview' as TabType, label: 'Overview', icon: BarChart3 },
    { id: 'charts' as TabType, label: 'Charts', icon: LineChart },
    { id: 'insights' as TabType, label: 'Insights', icon: Zap },
    { id: 'reports' as TabType, label: 'Reports', icon: FileText },
  ]

  const chartOptions = [
    { id: 'agent-activity', label: 'Agent Activity', icon: Bot },
    { id: 'revenue', label: 'Revenue', icon: DollarSign },
    { id: 'content', label: 'Content Production', icon: FileText },
    { id: 'system-health', label: 'System Health', icon: Activity },
  ]

  const formatNumber = (num?: number) => {
    if (num === undefined || num === null) return '0'
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toLocaleString()
  }

  const formatCurrency = (amount?: number) => {
    if (amount === undefined || amount === null) return '$0'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString()
  }

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'high':
        return 'text-red-400 bg-red-500/20'
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/20'
      case 'low':
        return 'text-blue-400 bg-blue-500/20'
      default:
        return 'text-gray-400 bg-gray-500/20'
    }
  }

  const getChartLoading = () => {
    switch (selectedChart) {
      case 'agent-activity':
        return loadingAgentActivity
      case 'revenue':
        return loadingRevenue
      case 'content':
        return loadingContent
      case 'system-health':
        return loadingHealth
      default:
        return false
    }
  }

  const getChartData = (): ChartData => {
    switch (selectedChart) {
      case 'agent-activity':
        return agentActivity
      case 'revenue':
        return revenue
      case 'content':
        return content
      case 'system-health':
        return systemHealth
      default:
        return { labels: [], datasets: [] }
    }
  }

  // Simple bar chart renderer (visual representation)
  const renderSimpleChart = (data: ChartData) => {
    if (!data.labels?.length || !data.datasets?.length) {
      return (
        <div className="text-center py-12 text-gray-500">
          No data available for this period
        </div>
      )
    }

    const maxValue = Math.max(...data.datasets[0].data)

    return (
      <div className="space-y-2">
        {data.labels.slice(-10).map((label, idx) => {
          const value = data.datasets[0].data[data.labels.length - 10 + idx] || 0
          const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0

          return (
            <div key={label} className="flex items-center gap-3">
              <span className="w-20 text-xs text-gray-500 truncate">{label}</span>
              <div className="flex-1 h-6 bg-dark-bg rounded overflow-hidden">
                <div
                  className="h-full bg-primary-500 rounded transition-all"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <span className="w-16 text-sm text-right">{formatNumber(value)}</span>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/20">
            <BarChart3 className="h-6 w-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
            <p className="text-gray-400">Platform metrics, trends, and insights</p>
          </div>
        </div>

        {/* Period Selector */}
        <div className="flex items-center gap-2">
          {(['7d', '30d', '90d', '1y'] as PeriodType[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={cn(
                'px-3 py-1.5 text-sm rounded transition-colors',
                period === p
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-card text-gray-400 hover:text-white'
              )}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Bot className="h-4 w-4" />
            <span className="text-xs">Agent Executions</span>
          </div>
          <p className="text-2xl font-bold">{formatNumber(overview.agent_executions)}</p>
          {summary.agent_change && (
            <div className={cn(
              'flex items-center gap-1 text-xs mt-1',
              summary.agent_change > 0 ? 'text-accent-green' : 'text-red-400'
            )}>
              {summary.agent_change > 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
              {Math.abs(summary.agent_change)}%
            </div>
          )}
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <DollarSign className="h-4 w-4" />
            <span className="text-xs">Revenue</span>
          </div>
          <p className="text-2xl font-bold text-accent-green">{formatCurrency(overview.total_revenue)}</p>
          {summary.revenue_change && (
            <div className={cn(
              'flex items-center gap-1 text-xs mt-1',
              summary.revenue_change > 0 ? 'text-accent-green' : 'text-red-400'
            )}>
              {summary.revenue_change > 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
              {Math.abs(summary.revenue_change)}%
            </div>
          )}
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <FileText className="h-4 w-4" />
            <span className="text-xs">Content Created</span>
          </div>
          <p className="text-2xl font-bold">{formatNumber(overview.content_created)}</p>
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Users className="h-4 w-4" />
            <span className="text-xs">Collaborations</span>
          </div>
          <p className="text-2xl font-bold text-blue-400">{formatNumber(overview.collaborations)}</p>
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Activity className="h-4 w-4" />
            <span className="text-xs">Uptime</span>
          </div>
          <p className="text-2xl font-bold text-accent-green">{overview.uptime || 99.9}%</p>
        </div>

        <div className="card p-4">
          <div className="flex items-center gap-2 text-gray-400 mb-1">
            <Zap className="h-4 w-4" />
            <span className="text-xs">API Calls</span>
          </div>
          <p className="text-2xl font-bold">{formatNumber(overview.api_calls)}</p>
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
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Agent Activity Summary */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Bot className="h-5 w-5 text-cyan-400" />
                Agent Activity
              </h3>
              {loadingOverview ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Active Agents</span>
                    <span className="font-bold">{overview.active_agents || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Tasks Completed</span>
                    <span className="font-bold">{formatNumber(overview.tasks_completed)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Avg Response Time</span>
                    <span className="font-bold">{overview.avg_response_time || 0}ms</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Success Rate</span>
                    <span className="font-bold text-accent-green">{overview.success_rate || 0}%</span>
                  </div>
                </div>
              )}
            </div>

            {/* Revenue Summary */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-accent-green" />
                Revenue Summary
              </h3>
              {loadingOverview ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">This Month</span>
                    <span className="font-bold text-accent-green">{formatCurrency(overview.revenue_this_month)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Last Month</span>
                    <span className="font-bold">{formatCurrency(overview.revenue_last_month)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">YTD</span>
                    <span className="font-bold">{formatCurrency(overview.revenue_ytd)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Growth</span>
                    <span className={cn(
                      'font-bold',
                      (overview.revenue_growth || 0) > 0 ? 'text-accent-green' : 'text-red-400'
                    )}>
                      {(overview.revenue_growth || 0) > 0 ? '+' : ''}{overview.revenue_growth || 0}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Charts Tab */}
        {activeTab === 'charts' && (
          <div className="space-y-6">
            {/* Chart Selector */}
            <div className="flex gap-2">
              {chartOptions.map((opt) => {
                const Icon = opt.icon
                return (
                  <button
                    key={opt.id}
                    onClick={() => setSelectedChart(opt.id)}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
                      selectedChart === opt.id
                        ? 'bg-primary-600 text-white'
                        : 'bg-dark-card text-gray-400 hover:text-white'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {opt.label}
                  </button>
                )
              })}
            </div>

            {/* Chart Display */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">
                  {chartOptions.find(o => o.id === selectedChart)?.label}
                </h3>
                <button
                  onClick={() => queryClient.invalidateQueries({ queryKey: [`analytics-${selectedChart}`] })}
                  className="p-2 rounded hover:bg-dark-bg"
                >
                  <RefreshCw className="h-4 w-4" />
                </button>
              </div>

              {getChartLoading() ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                </div>
              ) : (
                renderSimpleChart(getChartData())
              )}
            </div>
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Performers */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="h-5 w-5 text-yellow-400" />
                Top Performers
              </h3>
              {loadingPerformers ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : topPerformers.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No data available</div>
              ) : (
                <div className="space-y-3">
                  {topPerformers.slice(0, 5).map((performer, idx) => (
                    <div key={performer.id} className="flex items-center gap-3">
                      <span className={cn(
                        'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                        idx === 0 ? 'bg-yellow-500 text-black' :
                        idx === 1 ? 'bg-gray-400 text-black' :
                        idx === 2 ? 'bg-amber-600 text-white' :
                        'bg-dark-bg text-gray-400'
                      )}>
                        {idx + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{performer.name}</p>
                        <p className="text-xs text-gray-500">{performer.category}</p>
                      </div>
                      <span className="font-bold">{performer.score}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Anomalies */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                Anomalies Detected
              </h3>
              {loadingAnomalies ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : anomalies.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="h-8 w-8 mx-auto mb-2 text-accent-green" />
                  No anomalies detected
                </div>
              ) : (
                <div className="space-y-3">
                  {anomalies.slice(0, 5).map((anomaly) => (
                    <div key={anomaly.id} className="p-3 rounded-lg bg-dark-bg">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={cn(
                          'px-2 py-0.5 text-xs rounded',
                          getSeverityColor(anomaly.severity)
                        )}>
                          {anomaly.severity}
                        </span>
                        <span className="font-medium">{anomaly.metric}</span>
                      </div>
                      <p className="text-sm text-gray-400">{anomaly.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Forecasts */}
            <div className="card p-6 lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-400" />
                30-Day Forecast
              </h3>
              {loadingForecast ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : forecasts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No forecast data available</div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {forecasts.slice(0, 4).map((forecast) => (
                    <div key={forecast.metric} className="p-4 rounded-lg bg-dark-bg">
                      <p className="text-sm text-gray-400 mb-2">{forecast.metric}</p>
                      <div className="flex items-end gap-2">
                        <span className="text-2xl font-bold">{formatNumber(forecast.predicted)}</span>
                        {forecast.trend === 'up' ? (
                          <TrendingUp className="h-5 w-5 text-accent-green" />
                        ) : forecast.trend === 'down' ? (
                          <TrendingDown className="h-5 w-5 text-red-400" />
                        ) : null}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {forecast.confidence}% confidence
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="space-y-6">
            {/* Generate Report */}
            <div className="card p-4">
              <h3 className="font-medium mb-3">Generate New Report</h3>
              <div className="flex gap-2">
                {['summary', 'detailed', 'executive'].map((type) => (
                  <button
                    key={type}
                    onClick={() => generateReport.mutate(type)}
                    disabled={generateReport.isPending}
                    className="btn-secondary capitalize"
                  >
                    {type} Report
                  </button>
                ))}
              </div>
            </div>

            {/* Reports List */}
            <div className="card">
              <div className="p-4 border-b border-dark-border">
                <h3 className="font-semibold">Available Reports</h3>
              </div>

              {loadingReports ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : reports.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No reports generated yet
                </div>
              ) : (
                <div className="divide-y divide-dark-border">
                  {reports.map((report) => (
                    <div key={report.id} className="p-4 flex items-center gap-4">
                      <div className="p-2 rounded-lg bg-dark-bg">
                        <FileText className="h-5 w-5 text-gray-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium">{report.name}</p>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span className="capitalize">{report.type}</span>
                          <span>•</span>
                          <span>{formatDate(report.created_at)}</span>
                          {report.size && (
                            <>
                              <span>•</span>
                              <span>{report.size}</span>
                            </>
                          )}
                        </div>
                      </div>
                      <span className={cn(
                        'px-2 py-1 text-xs rounded capitalize',
                        report.status === 'ready' ? 'bg-accent-green/20 text-accent-green' :
                        report.status === 'generating' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      )}>
                        {report.status}
                      </span>
                      {report.status === 'ready' && (
                        <button className="p-2 rounded hover:bg-dark-bg">
                          <Download className="h-4 w-4" />
                        </button>
                      )}
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
