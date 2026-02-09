import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  TrendingUp,
  TrendingDown,
  BarChart2,
  AlertTriangle,
  FileText,
  Target,
  Loader2,
  ChevronDown,
  ChevronUp,
  Bookmark,
  Search,
  X,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { stockApi, type StockDashboard, type MarketBrief, type MarketBriefDetail, type StockAlert, type PredictionOutcome } from '@/lib/api'

// Sub-tab config
type SubTab = 'overview' | 'briefs' | 'alerts' | 'sec' | 'predictions'
const subTabs: Array<{ id: SubTab; label: string; icon: typeof TrendingUp }> = [
  { id: 'overview', label: 'Overview', icon: BarChart2 },
  { id: 'briefs', label: 'Market Briefs', icon: FileText },
  { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
  { id: 'sec', label: 'SEC Filings', icon: FileText },
  { id: 'predictions', label: 'Predictions', icon: Target },
]

// Alert type display config
const alertTypeConfig: Record<string, { label: string; color: string }> = {
  high_conviction_bull: { label: 'Bull', color: 'bg-green-500/20 text-green-400' },
  high_conviction_bear: { label: 'Bear', color: 'bg-red-500/20 text-red-400' },
  debate_zone: { label: 'Debate', color: 'bg-purple-500/20 text-purple-400' },
  risk_alert: { label: 'Risk', color: 'bg-orange-500/20 text-orange-400' },
  momentum_shift: { label: 'Momentum', color: 'bg-blue-500/20 text-blue-400' },
  institutional_activity: { label: 'Institutional', color: 'bg-cyan-500/20 text-cyan-400' },
  anomaly_detected: { label: 'Anomaly', color: 'bg-yellow-500/20 text-yellow-400' },
  earnings_alert: { label: 'Earnings', color: 'bg-indigo-500/20 text-indigo-400' },
}

const actionConfig: Record<string, { label: string; color: string }> = {
  watch: { label: 'Watch', color: 'text-gray-400' },
  research: { label: 'Research', color: 'text-blue-400' },
  consider_buy: { label: 'Consider Buy', color: 'text-green-400' },
  consider_sell: { label: 'Consider Sell', color: 'text-red-400' },
  hedge: { label: 'Hedge', color: 'text-amber-400' },
  avoid: { label: 'Avoid', color: 'text-red-500' },
}

export default function StockIntelligencePage() {
  const [activeTab, setActiveTab] = useState<SubTab>('overview')

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center gap-3 mb-4">
        <TrendingUp size={24} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Stock Intelligence</h1>
      </div>

      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'briefs' && <BriefsTab />}
      {activeTab === 'alerts' && <AlertsTab />}
      {activeTab === 'sec' && <SECFilingsTab />}
      {activeTab === 'predictions' && <PredictionsTab />}
    </div>
  )
}

// =============================================================================
// Overview Tab
// =============================================================================
function OverviewTab() {
  const { data, isLoading } = useQuery({
    queryKey: ['stock-dashboard'],
    queryFn: () => stockApi.dashboard().then(r => r.data as StockDashboard),
  })

  if (isLoading) return <LoadingSpinner />

  if (!data?.success) {
    return <div className="text-gray-400 text-center py-12">No stock data available yet.</div>
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Market Briefs" value={data.total_briefs} icon={<FileText size={18} />} />
        <StatCard label="Active Alerts" value={data.total_alerts} icon={<AlertTriangle size={18} />} />
        <StatCard
          label="7-Day Accuracy"
          value={data.prediction_accuracy_7d != null ? `${data.prediction_accuracy_7d}%` : 'N/A'}
          icon={<Target size={18} />}
          color={data.prediction_accuracy_7d != null && data.prediction_accuracy_7d >= 60 ? 'text-green-400' : undefined}
        />
        <StatCard label="SEC Filings" value={data.sec_filings_count} icon={<FileText size={18} />} />
      </div>

      {/* Latest Brief */}
      {data.latest_brief && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-300">Latest Brief - {data.latest_brief.brief_date}</h3>
            <span className={cn(
              'text-xs px-2 py-0.5 rounded',
              data.latest_brief.situation_health === 'OPERATIONAL'
                ? 'bg-green-500/20 text-green-400'
                : 'bg-yellow-500/20 text-yellow-400'
            )}>
              {data.latest_brief.situation_health}
            </span>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed">{data.latest_brief.executive_summary}</p>
          <div className="flex gap-4 mt-3 text-xs text-gray-500">
            <span>{data.latest_brief.total_stocks_analyzed} stocks analyzed</span>
            <span>{data.latest_brief.debate_zone_count} in debate zone</span>
          </div>
        </div>
      )}

      {/* Alert Type Breakdown */}
      {data.alert_counts_by_type && Object.keys(data.alert_counts_by_type).length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-300 mb-3">Alerts by Type</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.alert_counts_by_type).map(([type, count]) => {
              const config = alertTypeConfig[type] || { label: type, color: 'bg-gray-500/20 text-gray-400' }
              return (
                <span key={type} className={cn('px-2 py-1 rounded text-xs', config.color)}>
                  {config.label}: {count}
                </span>
              )
            })}
          </div>
        </div>
      )}

      {/* Prediction Stats */}
      {data.total_predictions > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-300 mb-3">Prediction Performance</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-white">{data.total_predictions}</div>
              <div className="text-xs text-gray-500">Total Predictions</div>
            </div>
            <div>
              <div className={cn('text-2xl font-bold', data.prediction_accuracy_7d != null && data.prediction_accuracy_7d >= 60 ? 'text-green-400' : 'text-gray-400')}>
                {data.prediction_accuracy_7d != null ? `${data.prediction_accuracy_7d}%` : 'N/A'}
              </div>
              <div className="text-xs text-gray-500">7-Day Accuracy</div>
            </div>
            <div>
              <div className={cn('text-2xl font-bold', data.prediction_accuracy_30d != null && data.prediction_accuracy_30d >= 60 ? 'text-green-400' : 'text-gray-400')}>
                {data.prediction_accuracy_30d != null ? `${data.prediction_accuracy_30d}%` : 'N/A'}
              </div>
              <div className="text-xs text-gray-500">30-Day Accuracy</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Market Briefs Tab
// =============================================================================
function BriefsTab() {
  const [offset, setOffset] = useState(0)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const limit = 10

  const { data, isLoading } = useQuery({
    queryKey: ['stock-briefs', offset],
    queryFn: () => stockApi.briefs({ limit, offset }).then(r => r.data),
  })

  const { data: detailData } = useQuery({
    queryKey: ['stock-brief-detail', expandedId],
    queryFn: () => expandedId ? stockApi.briefDetail(expandedId).then(r => r.data) : null,
    enabled: !!expandedId,
  })

  if (isLoading) return <LoadingSpinner />

  const briefs: MarketBrief[] = data?.results || []
  const total: number = data?.total || 0

  return (
    <div className="space-y-3">
      {briefs.length === 0 && <EmptyState message="No market briefs yet." />}
      {briefs.map((brief) => {
        const isExpanded = expandedId === brief.id
        const detail: MarketBriefDetail | null = isExpanded && detailData?.success ? detailData.brief : null
        return (
          <div key={brief.id} className="bg-dark-card border border-dark-border rounded-lg">
            <button
              onClick={() => setExpandedId(isExpanded ? null : brief.id)}
              className="w-full text-left p-4 flex items-center justify-between"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">{brief.brief_date}</span>
                  <HealthBadge health={brief.situation_health} />
                </div>
                <p className="text-sm text-gray-400 mt-1 truncate">{brief.executive_summary}</p>
              </div>
              <div className="flex items-center gap-3 ml-3 flex-shrink-0">
                <span className="text-xs text-gray-500">{brief.total_stocks_analyzed} stocks</span>
                {isExpanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
              </div>
            </button>

            {isExpanded && detail && (
              <div className="border-t border-dark-border p-4 space-y-4">
                <p className="text-sm text-gray-300 leading-relaxed">{detail.executive_summary}</p>

                {detail.high_conviction_opportunities.length > 0 && (
                  <JsonSection title="High Conviction Opportunities" items={detail.high_conviction_opportunities} color="text-green-400" />
                )}
                {detail.debate_zone.length > 0 && (
                  <JsonSection title="Debate Zone" items={detail.debate_zone} color="text-purple-400" />
                )}
                {detail.bullish_opportunities.length > 0 && (
                  <JsonSection title="Bullish Opportunities" items={detail.bullish_opportunities} color="text-green-300" />
                )}
                {detail.bearish_warnings.length > 0 && (
                  <JsonSection title="Bearish Warnings" items={detail.bearish_warnings} color="text-red-400" />
                )}
                {detail.risk_alerts.length > 0 && (
                  <JsonSection title="Risk Alerts" items={detail.risk_alerts} color="text-orange-400" />
                )}

                {detail.confidence_distribution && Object.keys(detail.confidence_distribution).length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium text-gray-400 uppercase mb-2">Confidence Distribution</h4>
                    <div className="flex gap-3">
                      {Object.entries(detail.confidence_distribution).map(([level, count]) => (
                        <span key={level} className="text-xs text-gray-300">
                          {level}: <span className="text-white font-medium">{String(count)}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}

      {/* Pagination */}
      {total > limit && (
        <PaginationControls offset={offset} limit={limit} total={total} onChange={setOffset} />
      )}
    </div>
  )
}

// =============================================================================
// Alerts Tab
// =============================================================================
function AlertsTab() {
  const [offset, setOffset] = useState(0)
  const [typeFilter, setTypeFilter] = useState('')
  const [symbolFilter, setSymbolFilter] = useState('')
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false)
  const limit = 20

  const { data, isLoading } = useQuery({
    queryKey: ['stock-alerts', offset, typeFilter, symbolFilter, bookmarkedOnly],
    queryFn: () => stockApi.alerts({
      limit,
      offset,
      type: typeFilter || undefined,
      symbol: symbolFilter || undefined,
      bookmarked: bookmarkedOnly || undefined,
    }).then(r => r.data),
  })

  if (isLoading) return <LoadingSpinner />

  const alerts: StockAlert[] = data?.results || []
  const total: number = data?.total || 0

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-2 items-center">
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setOffset(0) }}
          className="bg-gray-800 border border-dark-border rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Types</option>
          {Object.entries(alertTypeConfig).map(([value, { label }]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>

        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Symbol..."
            value={symbolFilter}
            onChange={(e) => { setSymbolFilter(e.target.value.toUpperCase()); setOffset(0) }}
            className="bg-gray-800 border border-dark-border rounded-lg pl-8 pr-7 py-1.5 text-sm text-gray-300 w-32"
          />
          {symbolFilter && (
            <button onClick={() => setSymbolFilter('')} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
              <X size={12} />
            </button>
          )}
        </div>

        <button
          onClick={() => { setBookmarkedOnly(!bookmarkedOnly); setOffset(0) }}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm border transition-colors',
            bookmarkedOnly
              ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
              : 'bg-gray-800 text-gray-400 border-dark-border hover:text-white'
          )}
        >
          <Bookmark size={14} />
          Bookmarked
        </button>

        <span className="text-xs text-gray-500 ml-auto">{total} alerts</span>
      </div>

      {/* Alert List */}
      {alerts.length === 0 && <EmptyState message="No alerts match your filters." />}
      {alerts.map((alert) => {
        const typeConf = alertTypeConfig[alert.alert_type] || { label: alert.alert_type, color: 'bg-gray-500/20 text-gray-400' }
        const actConf = actionConfig[alert.recommended_action] || { label: alert.recommended_action, color: 'text-gray-400' }
        return (
          <div key={alert.id} className="bg-dark-card border border-dark-border rounded-lg p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={cn('px-2 py-0.5 rounded text-xs', typeConf.color)}>{typeConf.label}</span>
                  <span className="text-sm font-mono font-bold text-white">{alert.symbol}</span>
                  {alert.company_name && <span className="text-xs text-gray-500">{alert.company_name}</span>}
                  {alert.bookmarked && <Bookmark size={12} className="text-amber-400 fill-amber-400" />}
                </div>
                <h4 className="text-sm text-white mt-1">{alert.title}</h4>
                <p className="text-xs text-gray-400 mt-1 line-clamp-2">{alert.summary}</p>
              </div>
              <div className="text-right flex-shrink-0 space-y-1">
                {alert.current_price != null && (
                  <div className="text-sm font-medium text-white">${alert.current_price.toFixed(2)}</div>
                )}
                {alert.price_change_24h != null && (
                  <div className={cn('text-xs', alert.price_change_24h >= 0 ? 'text-green-400' : 'text-red-400')}>
                    {alert.price_change_24h >= 0 ? '+' : ''}{alert.price_change_24h.toFixed(2)}%
                  </div>
                )}
                <div className={cn('text-xs font-medium', actConf.color)}>{actConf.label}</div>
              </div>
            </div>

            {/* Bull/Bear bars */}
            <div className="mt-3 flex items-center gap-2">
              <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden flex">
                <div className="bg-green-500 h-full" style={{ width: `${alert.bull_score}%` }} />
                <div className="bg-red-500 h-full" style={{ width: `${alert.bear_score}%` }} />
              </div>
              <span className="text-xs text-gray-500 w-24 text-right">
                {alert.confidence_score.toFixed(0)}% conf
              </span>
            </div>

            <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
              {alert.sector && <span>{alert.sector}</span>}
              {alert.detected_at && <span>{new Date(alert.detected_at).toLocaleDateString()}</span>}
            </div>
          </div>
        )
      })}

      {total > limit && (
        <PaginationControls offset={offset} limit={limit} total={total} onChange={setOffset} />
      )}
    </div>
  )
}

// =============================================================================
// SEC Filings Tab
// =============================================================================
function SECFilingsTab() {
  const [offset, setOffset] = useState(0)
  const limit = 20

  const { data, isLoading } = useQuery({
    queryKey: ['stock-sec-filings', offset],
    queryFn: () => stockApi.secFilings({ limit, offset }).then(r => r.data),
  })

  if (isLoading) return <LoadingSpinner />

  // SpiderData entries come as generic shape
  const filings: Array<{
    id: string
    spider_name: string
    source_url: string
    data_type: string
    raw_data: Record<string, unknown>
    relevance_score: number
    created_at: string
  }> = data?.results || []
  const total: number = data?.total || 0

  return (
    <div className="space-y-3">
      {filings.length === 0 && <EmptyState message="No SEC filings collected yet." />}
      {filings.map((f) => {
        const items = (f.raw_data?.items as Array<Record<string, string>>) || []
        return (
          <div key={f.id} className="bg-dark-card border border-dark-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white">{f.data_type || 'SEC Filing'}</span>
              <span className="text-xs text-gray-500">{new Date(f.created_at).toLocaleDateString()}</span>
            </div>
            {items.length > 0 ? (
              <div className="space-y-2">
                {items.slice(0, 5).map((item, idx) => (
                  <div key={idx} className="text-xs text-gray-400">
                    <span className="text-gray-300 font-medium">{item.title || item.name || `Item ${idx + 1}`}</span>
                    {item.description && <span className="ml-2">{item.description.slice(0, 150)}</span>}
                  </div>
                ))}
                {items.length > 5 && <span className="text-xs text-gray-500">+{items.length - 5} more items</span>}
              </div>
            ) : (
              <div className="text-xs text-gray-500">
                <a href={f.source_url} target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:underline">
                  {f.source_url}
                </a>
              </div>
            )}
            <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
              <span>Relevance: {f.relevance_score}%</span>
            </div>
          </div>
        )
      })}

      {total > limit && (
        <PaginationControls offset={offset} limit={limit} total={total} onChange={setOffset} />
      )}
    </div>
  )
}

// =============================================================================
// Predictions Tab
// =============================================================================
function PredictionsTab() {
  const [offset, setOffset] = useState(0)
  const [tickerFilter, setTickerFilter] = useState('')
  const limit = 20

  const { data, isLoading } = useQuery({
    queryKey: ['stock-predictions', offset, tickerFilter],
    queryFn: () => stockApi.predictions({
      limit,
      offset,
      ticker: tickerFilter || undefined,
    }).then(r => r.data),
  })

  if (isLoading) return <LoadingSpinner />

  const predictions: PredictionOutcome[] = data?.results || []
  const total: number = data?.total || 0
  const stats = data?.stats

  return (
    <div className="space-y-4">
      {/* Stats bar */}
      {stats && stats.evaluated_count > 0 && (
        <div className="flex gap-4 bg-dark-card border border-dark-border rounded-lg p-3">
          <div className="text-center">
            <div className="text-lg font-bold text-white">{stats.evaluated_count}</div>
            <div className="text-xs text-gray-500">Evaluated</div>
          </div>
          <div className="text-center">
            <div className={cn('text-lg font-bold', stats.accuracy_7d_pct != null && stats.accuracy_7d_pct >= 60 ? 'text-green-400' : 'text-gray-400')}>
              {stats.accuracy_7d_pct != null ? `${stats.accuracy_7d_pct}%` : 'N/A'}
            </div>
            <div className="text-xs text-gray-500">7-Day</div>
          </div>
          <div className="text-center">
            <div className={cn('text-lg font-bold', stats.accuracy_30d_pct != null && stats.accuracy_30d_pct >= 60 ? 'text-green-400' : 'text-gray-400')}>
              {stats.accuracy_30d_pct != null ? `${stats.accuracy_30d_pct}%` : 'N/A'}
            </div>
            <div className="text-xs text-gray-500">30-Day</div>
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="flex items-center gap-2">
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Ticker..."
            value={tickerFilter}
            onChange={(e) => { setTickerFilter(e.target.value.toUpperCase()); setOffset(0) }}
            className="bg-gray-800 border border-dark-border rounded-lg pl-8 pr-7 py-1.5 text-sm text-gray-300 w-32"
          />
          {tickerFilter && (
            <button onClick={() => setTickerFilter('')} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
              <X size={12} />
            </button>
          )}
        </div>
        <span className="text-xs text-gray-500 ml-auto">{total} predictions</span>
      </div>

      {/* Table */}
      {predictions.length === 0 && <EmptyState message="No predictions yet." />}
      {predictions.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-border text-left text-xs text-gray-500">
                <th className="pb-2 pr-3">Ticker</th>
                <th className="pb-2 pr-3">Type</th>
                <th className="pb-2 pr-3">Conviction</th>
                <th className="pb-2 pr-3">Predicted</th>
                <th className="pb-2 pr-3">Actual 7D</th>
                <th className="pb-2 pr-3">Actual 30D</th>
                <th className="pb-2 pr-3">7D</th>
                <th className="pb-2 pr-3">30D</th>
                <th className="pb-2">Date</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p) => (
                <tr key={p.id} className="border-b border-dark-border/50 hover:bg-gray-800/30">
                  <td className="py-2 pr-3 font-mono font-bold text-white">{p.ticker}</td>
                  <td className="py-2 pr-3">
                    <span className={cn(
                      'px-1.5 py-0.5 rounded text-xs',
                      p.prediction_type === 'BULL' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    )}>
                      {p.prediction_type === 'BULL' ? <TrendingUp size={10} className="inline mr-1" /> : <TrendingDown size={10} className="inline mr-1" />}
                      {p.prediction_type}
                    </span>
                  </td>
                  <td className="py-2 pr-3 text-xs text-gray-400">{p.conviction_level}</td>
                  <td className={cn('py-2 pr-3 text-xs', p.predicted_move >= 0 ? 'text-green-400' : 'text-red-400')}>
                    {p.predicted_move >= 0 ? '+' : ''}{p.predicted_move.toFixed(1)}%
                  </td>
                  <td className={cn('py-2 pr-3 text-xs', p.actual_move_7_days != null ? (p.actual_move_7_days >= 0 ? 'text-green-400' : 'text-red-400') : 'text-gray-600')}>
                    {p.actual_move_7_days != null ? `${p.actual_move_7_days >= 0 ? '+' : ''}${p.actual_move_7_days.toFixed(1)}%` : '--'}
                  </td>
                  <td className={cn('py-2 pr-3 text-xs', p.actual_move_30_days != null ? (p.actual_move_30_days >= 0 ? 'text-green-400' : 'text-red-400') : 'text-gray-600')}>
                    {p.actual_move_30_days != null ? `${p.actual_move_30_days >= 0 ? '+' : ''}${p.actual_move_30_days.toFixed(1)}%` : '--'}
                  </td>
                  <td className="py-2 pr-3">
                    <CorrectnessBadge value={p.was_correct_7_days} />
                  </td>
                  <td className="py-2 pr-3">
                    <CorrectnessBadge value={p.was_correct_30_days} />
                  </td>
                  <td className="py-2 text-xs text-gray-500">{p.prediction_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total > limit && (
        <PaginationControls offset={offset} limit={limit} total={total} onChange={setOffset} />
      )}
    </div>
  )
}

// =============================================================================
// Shared Components
// =============================================================================

function StatCard({ label, value, icon, color }: { label: string; value: number | string; icon: React.ReactNode; color?: string }) {
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-4">
      <div className="flex items-center gap-2 text-gray-400 mb-1">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <div className={cn('text-2xl font-bold', color || 'text-white')}>{value}</div>
    </div>
  )
}

function HealthBadge({ health }: { health: string }) {
  return (
    <span className={cn(
      'text-xs px-1.5 py-0.5 rounded',
      health === 'OPERATIONAL' ? 'bg-green-500/20 text-green-400' :
      health === 'DEGRADED' ? 'bg-yellow-500/20 text-yellow-400' :
      'bg-red-500/20 text-red-400'
    )}>
      {health}
    </span>
  )
}

function CorrectnessBadge({ value }: { value: boolean | null }) {
  if (value === null || value === undefined) return <span className="text-xs text-gray-600">--</span>
  return value
    ? <span className="text-xs text-green-400">Y</span>
    : <span className="text-xs text-red-400">N</span>
}

function JsonSection({ title, items, color }: { title: string; items: unknown[]; color: string }) {
  return (
    <div>
      <h4 className={cn('text-xs font-medium uppercase mb-2', color)}>{title} ({items.length})</h4>
      <div className="space-y-1">
        {items.slice(0, 5).map((item, idx) => (
          <div key={idx} className="text-xs text-gray-400 bg-gray-800/50 rounded px-2 py-1">
            {typeof item === 'string' ? item : JSON.stringify(item, null, 0).slice(0, 200)}
          </div>
        ))}
        {items.length > 5 && <span className="text-xs text-gray-500">+{items.length - 5} more</span>}
      </div>
    </div>
  )
}

function PaginationControls({ offset, limit, total, onChange }: { offset: number; limit: number; total: number; onChange: (n: number) => void }) {
  const page = Math.floor(offset / limit) + 1
  const totalPages = Math.ceil(total / limit)
  return (
    <div className="flex items-center justify-center gap-3 pt-2">
      <button
        onClick={() => onChange(Math.max(0, offset - limit))}
        disabled={offset === 0}
        className="px-3 py-1 text-sm rounded bg-gray-800 text-gray-400 disabled:opacity-30 hover:text-white"
      >
        Prev
      </button>
      <span className="text-xs text-gray-500">Page {page} of {totalPages}</span>
      <button
        onClick={() => onChange(offset + limit)}
        disabled={offset + limit >= total}
        className="px-3 py-1 text-sm rounded bg-gray-800 text-gray-400 disabled:opacity-30 hover:text-white"
      >
        Next
      </button>
    </div>
  )
}

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 size={24} className="animate-spin text-gray-400" />
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return <div className="text-gray-500 text-center py-8 text-sm">{message}</div>
}
