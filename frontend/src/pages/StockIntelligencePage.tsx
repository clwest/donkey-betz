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
  Activity,
  Newspaper,
  ExternalLink,
  ArrowUpRight,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { stockApi, type StockDashboard, type MarketBrief, type MarketBriefDetail, type StockAlert, type PredictionOutcome, type TickerLookupResult } from '@/lib/api'

// Sub-tab config
type SubTab = 'hub' | 'news' | 'ticker' | 'overview' | 'briefs' | 'alerts' | 'sec' | 'predictions'
const subTabs: Array<{ id: SubTab; label: string; icon: typeof TrendingUp }> = [
  { id: 'hub', label: 'Hub', icon: Activity },
  { id: 'news', label: 'News', icon: Newspaper },
  { id: 'ticker', label: 'Ticker Lookup', icon: Search },
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
  const [activeTab, setActiveTab] = useState<SubTab>('hub')

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
      {activeTab === 'hub' && <HubTab setActiveTab={setActiveTab} />}
      {activeTab === 'news' && <NewsTab />}
      {activeTab === 'ticker' && <TickerLookupTab />}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'briefs' && <BriefsTab />}
      {activeTab === 'alerts' && <AlertsTab />}
      {activeTab === 'sec' && <SECFilingsTab />}
      {activeTab === 'predictions' && <PredictionsTab />}
    </div>
  )
}

// =============================================================================
// Hub Tab
// =============================================================================

interface StockHubData {
  success: boolean
  stats: {
    total_briefs: number
    total_alerts: number
    total_predictions: number
    accuracy_7d: number | null
    accuracy_30d: number | null
    sec_filings_count: number
  }
  latest_brief: {
    id: string
    brief_date: string
    executive_summary: string
    total_stocks_analyzed: number
    debate_zone_count: number
    situation_health: string
  } | null
  top_alerts: Array<{
    id: string
    alert_type: string
    symbol: string
    company_name: string
    title: string
    summary: string
    confidence_score: number
    bull_score: number
    bear_score: number
    recommended_action: string
    detected_at: string | null
  }>
  top_predictions: Array<{
    id: string
    ticker: string
    prediction_type: string
    predicted_move: number
    actual_move_7_days: number | null
    was_correct_7_days: boolean | null
    prediction_date: string
  }>
  market_news: Array<{
    spider_name: string
    source: string
    title: string
    description: string
    link: string
    published: string | null
    category: string
  }>
  sec_recent: Array<{
    title: string
    description: string
    link: string
    published: string | null
  }>
}

function HubTab({ setActiveTab }: { setActiveTab: (tab: SubTab) => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['stock-hub'],
    queryFn: () => stockApi.hub().then(r => r.data as StockHubData),
  })

  if (isLoading) return <LoadingSpinner />
  if (!data?.success) return <div className="text-gray-400 text-center py-12">No data available yet.</div>

  const s = data.stats

  return (
    <div className="space-y-4">
      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Market Briefs" value={s.total_briefs} icon={<FileText size={18} />} />
        <StatCard label="Active Alerts" value={s.total_alerts} icon={<AlertTriangle size={18} />} />
        <StatCard
          label="7D Accuracy"
          value={s.accuracy_7d != null ? `${s.accuracy_7d}%` : 'N/A'}
          icon={<Target size={18} />}
          color={s.accuracy_7d != null && s.accuracy_7d >= 60 ? 'text-green-400' : undefined}
        />
        <StatCard label="SEC Filings" value={s.sec_filings_count} icon={<FileText size={18} />} />
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Latest Market Brief */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">Latest Market Brief</h3>
            <button onClick={() => setActiveTab('briefs')} className="text-xs text-primary-400 hover:text-primary-300">
              View all <ArrowUpRight size={10} className="inline" />
            </button>
          </div>
          {data.latest_brief ? (
            <>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium text-white">{data.latest_brief.brief_date}</span>
                <HealthBadge health={data.latest_brief.situation_health} />
              </div>
              <p className="text-sm text-gray-400 leading-relaxed line-clamp-4">{data.latest_brief.executive_summary}</p>
              <div className="flex gap-4 mt-3 text-xs text-gray-500">
                <span>{data.latest_brief.total_stocks_analyzed} stocks analyzed</span>
                <span>{data.latest_brief.debate_zone_count} in debate zone</span>
              </div>
            </>
          ) : (
            <p className="text-sm text-gray-500">No briefs yet.</p>
          )}
        </div>

        {/* Prediction Scorecard */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">Prediction Scorecard</h3>
            <button onClick={() => setActiveTab('predictions')} className="text-xs text-primary-400 hover:text-primary-300">
              View all <ArrowUpRight size={10} className="inline" />
            </button>
          </div>
          {data.top_predictions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-dark-border text-left text-gray-500">
                    <th className="pb-1.5 pr-2">Ticker</th>
                    <th className="pb-1.5 pr-2">Type</th>
                    <th className="pb-1.5 pr-2">Predicted</th>
                    <th className="pb-1.5 pr-2">Actual</th>
                    <th className="pb-1.5">Result</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_predictions.map((p) => (
                    <tr key={p.id} className="border-b border-dark-border/30">
                      <td className="py-1.5 pr-2 font-mono font-bold text-white">{p.ticker}</td>
                      <td className="py-1.5 pr-2">
                        <span className={cn(
                          'px-1.5 py-0.5 rounded',
                          p.prediction_type === 'BULL' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        )}>
                          {p.prediction_type}
                        </span>
                      </td>
                      <td className={cn('py-1.5 pr-2', p.predicted_move >= 0 ? 'text-green-400' : 'text-red-400')}>
                        {p.predicted_move >= 0 ? '+' : ''}{p.predicted_move.toFixed(1)}%
                      </td>
                      <td className={cn('py-1.5 pr-2', p.actual_move_7_days != null ? (p.actual_move_7_days >= 0 ? 'text-green-400' : 'text-red-400') : 'text-gray-600')}>
                        {p.actual_move_7_days != null ? `${p.actual_move_7_days >= 0 ? '+' : ''}${p.actual_move_7_days.toFixed(1)}%` : '--'}
                      </td>
                      <td className="py-1.5">
                        {p.was_correct_7_days === true
                          ? <span className="text-green-400 font-medium">W</span>
                          : p.was_correct_7_days === false
                            ? <span className="text-red-400 font-medium">L</span>
                            : <span className="text-gray-600">--</span>
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-gray-500">No evaluated predictions yet.</p>
          )}
        </div>

        {/* Top Alerts */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">Top Alerts</h3>
            <button onClick={() => setActiveTab('alerts')} className="text-xs text-primary-400 hover:text-primary-300">
              View all <ArrowUpRight size={10} className="inline" />
            </button>
          </div>
          {data.top_alerts.length > 0 ? (
            <div className="space-y-2">
              {data.top_alerts.map((a) => {
                const typeConf = alertTypeConfig[a.alert_type] || { label: a.alert_type, color: 'bg-gray-500/20 text-gray-400' }
                return (
                  <div key={a.id} className="bg-gray-800/50 rounded p-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={cn('px-1.5 py-0.5 rounded text-xs', typeConf.color)}>{typeConf.label}</span>
                      <span className="text-xs font-mono font-bold text-white">{a.symbol}</span>
                      <span className="text-xs text-gray-500 ml-auto">{a.confidence_score.toFixed(0)}%</span>
                    </div>
                    <p className="text-xs text-gray-400 truncate">{a.title}</p>
                    <div className="mt-1 flex items-center gap-1">
                      <div className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden flex">
                        <div className="bg-green-500 h-full" style={{ width: `${a.bull_score}%` }} />
                        <div className="bg-red-500 h-full" style={{ width: `${a.bear_score}%` }} />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No alerts yet.</p>
          )}
        </div>

        {/* Market News */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
              <Newspaper size={12} /> Market News
            </h3>
            <button onClick={() => setActiveTab('news')} className="text-xs text-primary-400 hover:text-primary-300">
              View all <ArrowUpRight size={10} className="inline" />
            </button>
          </div>
          {data.market_news.length > 0 ? (
            <div className="space-y-2">
              {data.market_news.map((item, idx) => (
                <div key={idx} className="flex items-start gap-2 group">
                  <div className="flex-1 min-w-0">
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-gray-300 hover:text-white line-clamp-1 group-hover:underline"
                    >
                      {item.title || 'Untitled'}
                      <ExternalLink size={9} className="inline ml-1 opacity-0 group-hover:opacity-100" />
                    </a>
                    <div className="flex items-center gap-2 mt-0.5">
                      <SourceBadge source={item.source} />
                      {item.published && (
                        <span className="text-xs text-gray-600">{timeAgo(item.published)}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No market news yet.</p>
          )}
        </div>
      </div>

      {/* SEC Filings — full width */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">Recent SEC Filings</h3>
          <button onClick={() => setActiveTab('sec')} className="text-xs text-primary-400 hover:text-primary-300">
            View all <ArrowUpRight size={10} className="inline" />
          </button>
        </div>
        {data.sec_recent.length > 0 ? (
          <div className="space-y-1.5">
            {data.sec_recent.map((f, idx) => (
              <div key={idx} className="flex items-center gap-3 text-xs">
                <a
                  href={f.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white hover:underline truncate flex-1"
                >
                  {f.title || 'SEC Filing'}
                  <ExternalLink size={9} className="inline ml-1 opacity-50" />
                </a>
                {f.published && (
                  <span className="text-gray-600 flex-shrink-0">{new Date(f.published).toLocaleDateString()}</span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No SEC filings yet.</p>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// News Tab
// =============================================================================

const sourceColorMap: Record<string, string> = {
  'MarketWatch': 'bg-blue-500/20 text-blue-400',
  'CNBC': 'bg-red-500/20 text-red-400',
  'Seeking Alpha': 'bg-green-500/20 text-green-400',
  'Investing.com': 'bg-orange-500/20 text-orange-400',
  'Yahoo Finance': 'bg-purple-500/20 text-purple-400',
  'Polygon': 'bg-cyan-500/20 text-cyan-400',
  'Finnhub': 'bg-teal-500/20 text-teal-400',
  'Financial News': 'bg-indigo-500/20 text-indigo-400',
}

function SourceBadge({ source }: { source: string }) {
  const color = sourceColorMap[source] || 'bg-gray-500/20 text-gray-400'
  return <span className={cn('px-1.5 py-0.5 rounded text-xs', color)}>{source}</span>
}

function timeAgo(dateStr: string): string {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  if (isNaN(then)) return dateStr
  const diffMs = now - then
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString()
}

interface MarketNewsData {
  success: boolean
  results: Array<{
    spider_name: string
    source: string
    title: string
    description: string
    link: string
    published: string | null
    category: string
  }>
  total: number
  limit: number
  offset: number
  sources: string[]
}

function NewsTab() {
  const [offset, setOffset] = useState(0)
  const [sourceFilter, setSourceFilter] = useState('')
  const limit = 20

  const { data, isLoading } = useQuery({
    queryKey: ['stock-market-news', offset, sourceFilter],
    queryFn: () => stockApi.marketNews({
      limit,
      offset,
      source: sourceFilter || undefined,
    }).then(r => r.data as MarketNewsData),
  })

  if (isLoading) return <LoadingSpinner />
  if (!data?.success) return <div className="text-gray-400 text-center py-12">No news data available yet.</div>

  const articles = data.results
  const total = data.total

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-3">
        <select
          value={sourceFilter}
          onChange={(e) => { setSourceFilter(e.target.value); setOffset(0) }}
          className="bg-gray-800 border border-dark-border rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value="">All Sources</option>
          {(data.sources || []).map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <span className="text-xs text-gray-500 ml-auto">{total} articles</span>
      </div>

      {/* News List */}
      {articles.length === 0 && <EmptyState message="No news articles match your filter." />}
      <div className="space-y-3">
        {articles.map((item, idx) => (
          <div key={`${item.link}-${idx}`} className="bg-dark-card border border-dark-border rounded-lg p-4 group">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-200 hover:text-white font-medium group-hover:underline"
                >
                  {item.title || 'Untitled'}
                  <ExternalLink size={11} className="inline ml-1.5 opacity-0 group-hover:opacity-100" />
                </a>
                {item.description && (
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">{item.description}</p>
                )}
                <div className="flex items-center gap-2 mt-2">
                  <SourceBadge source={item.source} />
                  {item.category && (
                    <span className="px-1.5 py-0.5 rounded text-xs bg-gray-700/50 text-gray-400">{item.category}</span>
                  )}
                  {item.published && (
                    <span className="text-xs text-gray-600">{timeAgo(item.published)}</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {total > limit && (
        <PaginationControls offset={offset} limit={limit} total={total} onChange={setOffset} />
      )}
    </div>
  )
}

// =============================================================================
// Ticker Lookup Tab
// =============================================================================

const momentumConfig: Record<string, { label: string; color: string }> = {
  STRONG_BULLISH: { label: 'Strong Bullish', color: 'bg-green-500/20 text-green-400' },
  BULLISH: { label: 'Bullish', color: 'bg-green-500/15 text-green-300' },
  SLIGHTLY_BULLISH: { label: 'Slightly Bullish', color: 'bg-green-500/10 text-green-200' },
  SLIGHTLY_BEARISH: { label: 'Slightly Bearish', color: 'bg-red-500/10 text-red-200' },
  BEARISH: { label: 'Bearish', color: 'bg-red-500/15 text-red-300' },
  STRONG_BEARISH: { label: 'Strong Bearish', color: 'bg-red-500/20 text-red-400' },
}

const signalConfig: Record<string, { label: string; color: string }> = {
  STRONG_BUY: { label: 'Strong Buy', color: 'bg-green-500/20 text-green-400' },
  BUY: { label: 'Buy', color: 'bg-green-500/15 text-green-300' },
  HOLD: { label: 'Hold', color: 'bg-gray-500/20 text-gray-300' },
  SELL: { label: 'Sell', color: 'bg-red-500/15 text-red-300' },
  STRONG_SELL: { label: 'Strong Sell', color: 'bg-red-500/20 text-red-400' },
}

const volatilityConfig: Record<string, { label: string; color: string }> = {
  LOW: { label: 'Low', color: 'bg-blue-500/10 text-blue-300' },
  MODERATE: { label: 'Moderate', color: 'bg-yellow-500/15 text-yellow-300' },
  HIGH: { label: 'High', color: 'bg-orange-500/20 text-orange-400' },
  EXTREME: { label: 'Extreme', color: 'bg-red-500/20 text-red-400' },
}

const sectionLabels: Record<string, string> = {
  high_conviction_opportunities: 'High Conviction',
  debate_zone: 'Debate Zone',
  bullish_opportunities: 'Bullish',
  bearish_warnings: 'Bearish',
}

function TickerLookupTab() {
  const [inputValue, setInputValue] = useState('')
  const [searchSymbol, setSearchSymbol] = useState('')

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['ticker-lookup', searchSymbol],
    queryFn: () => stockApi.tickerLookup(searchSymbol).then(r => r.data as TickerLookupResult),
    enabled: !!searchSymbol,
  })

  const handleSearch = () => {
    const trimmed = inputValue.trim().toUpperCase()
    if (trimmed) setSearchSymbol(trimmed)
  }

  const quote = data?.live_quote as Record<string, unknown> | null | undefined
  const analysis = quote?.analysis as Record<string, unknown> | undefined
  const companyName = quote?.company_name ? String(quote.company_name) : ''
  const sector = quote?.sector ? String(quote.sector) : ''
  const industry = quote?.industry ? String(quote.industry) : ''
  const currentPrice = Number(quote?.current_price || 0)
  const changePct = quote?.change_percent != null ? Number(quote.change_percent) : null

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1 max-w-xs">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Enter ticker symbol (e.g. AAPL)"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full bg-gray-800 border border-dark-border rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-gray-500"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={!inputValue.trim() || isLoading}
          className="px-4 py-2 rounded-lg bg-primary-500/20 text-primary-400 border border-primary-500/30 text-sm font-medium hover:bg-primary-500/30 disabled:opacity-40 transition-colors"
        >
          {isFetching ? <Loader2 size={14} className="animate-spin" /> : 'Lookup'}
        </button>
      </div>

      {!searchSymbol && (
        <div className="text-gray-500 text-center py-12 text-sm">
          Enter a ticker symbol above to see everything the platform knows about it.
        </div>
      )}

      {isLoading && <LoadingSpinner />}

      {data && !isLoading && (
        <div className="space-y-4">
          {/* Live Quote Hero Card */}
          {quote ? (
            <div className="bg-dark-card border border-dark-border rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xl font-mono font-bold text-white">{data.symbol}</span>
                    {companyName && <span className="text-sm text-gray-400">{companyName}</span>}
                  </div>
                  {sector && (
                    <span className="text-xs text-gray-500">{sector}{industry ? ` / ${industry}` : ''}</span>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">
                    ${currentPrice.toFixed(2)}
                  </div>
                  {changePct != null && (
                    <div className={cn('text-sm font-medium', changePct >= 0 ? 'text-green-400' : 'text-red-400')}>
                      {changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%
                    </div>
                  )}
                </div>
              </div>

              {/* Stats grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3 pt-3 border-t border-dark-border">
                {([
                  { label: 'Open', value: quote.open as number | undefined },
                  { label: 'Prev Close', value: quote.previous_close as number | undefined },
                  { label: 'Volume', value: quote.volume as number | undefined, fmt: 'volume' as const },
                  { label: 'Mkt Cap', value: quote.market_cap as number | undefined, fmt: 'cap' as const },
                  { label: 'Day Low', value: quote.day_low as number | undefined },
                  { label: 'Day High', value: quote.day_high as number | undefined },
                  { label: '52w Low', value: quote.fifty_two_week_low as number | undefined },
                  { label: '52w High', value: quote.fifty_two_week_high as number | undefined },
                ] as Array<{ label: string; value: number | undefined; fmt?: 'volume' | 'cap' }>).map(({ label, value, fmt }) => (
                  <div key={label} className="text-center">
                    <div className="text-xs text-gray-500">{label}</div>
                    <div className="text-sm font-medium text-gray-300">
                      {value != null
                        ? fmt === 'volume' ? Number(value).toLocaleString()
                        : fmt === 'cap' ? formatMarketCap(Number(value))
                        : `$${Number(value).toFixed(2)}`
                        : '--'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : searchSymbol && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center text-gray-500 text-sm">
              No live quote available for {data.symbol}
            </div>
          )}

          {/* Analysis Card */}
          {analysis && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-300 mb-3">Analysis</h3>
              <div className="flex flex-wrap gap-2">
                {analysis.momentum ? <AnalysisBadge prefix="Momentum" value={String(analysis.momentum)} config={momentumConfig} /> : null}
                {analysis.volatility ? <AnalysisBadge prefix="Volatility" value={String(analysis.volatility)} config={volatilityConfig} /> : null}
                {analysis.trading_signal ? <AnalysisBadge prefix="Signal" value={String(analysis.trading_signal)} config={signalConfig} /> : null}
              </div>
              {analysis.price_position != null && typeof analysis.price_position === 'object' && (analysis.price_position as Record<string, unknown>).percentage != null && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                    <span>52-Week Range Position</span>
                    <span>{Number((analysis.price_position as Record<string, unknown>).percentage).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-primary-500 rounded-full" style={{ width: `${Math.min(100, Math.max(0, Number((analysis.price_position as Record<string, unknown>).percentage)))}%` }} />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Alerts Section */}
          <CollapsibleSection title="Alerts" count={data.alerts.total}>
            {data.alerts.results.length === 0 ? (
              <EmptyState message="No alerts for this ticker." />
            ) : (
              <div className="space-y-3">
                {data.alerts.results.map((alert) => {
                  const typeConf = alertTypeConfig[alert.alert_type] || { label: alert.alert_type, color: 'bg-gray-500/20 text-gray-400' }
                  const actConf = actionConfig[alert.recommended_action] || { label: alert.recommended_action, color: 'text-gray-400' }
                  return (
                    <div key={alert.id} className="bg-gray-800/50 rounded-lg p-3">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className={cn('px-2 py-0.5 rounded text-xs', typeConf.color)}>{typeConf.label}</span>
                        <span className={cn('text-xs font-medium', actConf.color)}>{actConf.label}</span>
                        {alert.detected_at && <span className="text-xs text-gray-500 ml-auto">{new Date(alert.detected_at).toLocaleDateString()}</span>}
                      </div>
                      <h4 className="text-sm text-white">{alert.title}</h4>
                      <p className="text-xs text-gray-400 mt-1 line-clamp-2">{alert.summary}</p>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden flex">
                          <div className="bg-green-500 h-full" style={{ width: `${alert.bull_score}%` }} />
                          <div className="bg-red-500 h-full" style={{ width: `${alert.bear_score}%` }} />
                        </div>
                        <span className="text-xs text-gray-500">{alert.confidence_score.toFixed(0)}% conf</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CollapsibleSection>

          {/* Predictions Section */}
          <CollapsibleSection title="Predictions" count={data.predictions.total}>
            {data.predictions.results.length === 0 ? (
              <EmptyState message="No predictions for this ticker." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-dark-border text-left text-xs text-gray-500">
                      <th className="pb-2 pr-3">Type</th>
                      <th className="pb-2 pr-3">Conviction</th>
                      <th className="pb-2 pr-3">Predicted</th>
                      <th className="pb-2 pr-3">Actual 7D</th>
                      <th className="pb-2 pr-3">7D</th>
                      <th className="pb-2 pr-3">30D</th>
                      <th className="pb-2">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.predictions.results.map((p) => (
                      <tr key={p.id} className="border-b border-dark-border/50">
                        <td className="py-2 pr-3">
                          <span className={cn('px-1.5 py-0.5 rounded text-xs', p.prediction_type === 'BULL' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400')}>
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
                        <td className="py-2 pr-3"><CorrectnessBadge value={p.was_correct_7_days} /></td>
                        <td className="py-2 pr-3"><CorrectnessBadge value={p.was_correct_30_days} /></td>
                        <td className="py-2 text-xs text-gray-500">{p.prediction_date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CollapsibleSection>

          {/* Brief Mentions Section */}
          <CollapsibleSection title="Brief Mentions" count={data.brief_mentions.length}>
            {data.brief_mentions.length === 0 ? (
              <EmptyState message="Not mentioned in any recent briefs." />
            ) : (
              <div className="space-y-2">
                {data.brief_mentions.map((bm) => (
                  <div key={bm.brief_id} className="bg-gray-800/50 rounded-lg p-3">
                    <div className="text-sm font-medium text-white mb-1">{bm.brief_date}</div>
                    {bm.mentions.map((m, idx) => (
                      <div key={idx} className="flex items-center gap-2 flex-wrap text-xs mt-1">
                        <span className="px-1.5 py-0.5 rounded bg-primary-500/15 text-primary-300">
                          {sectionLabels[m.section] || m.section}
                        </span>
                        {m.recommendation && (
                          <span className={cn('px-1.5 py-0.5 rounded', {
                            'bg-green-500/20 text-green-400': m.recommendation === 'BULLISH',
                            'bg-red-500/20 text-red-400': m.recommendation === 'BEARISH',
                            'bg-purple-500/20 text-purple-400': m.recommendation === 'DEBATE',
                            'bg-gray-500/20 text-gray-400': !['BULLISH', 'BEARISH', 'DEBATE'].includes(m.recommendation),
                          })}>{m.recommendation}</span>
                        )}
                        {m.confidence && <span className="text-gray-500">{m.confidence}</span>}
                        {m.reasoning && <span className="text-gray-400 truncate max-w-md">{m.reasoning}</span>}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </CollapsibleSection>

          {/* SEC Filings Section */}
          <CollapsibleSection title="SEC Filings" count={data.sec_filings.total}>
            {data.sec_filings.results.length === 0 ? (
              <EmptyState message="No SEC filings found." />
            ) : (
              <div className="space-y-2">
                {data.sec_filings.results.map((f) => {
                  const items = (f.raw_data?.items as Array<Record<string, string>>) || []
                  return (
                    <div key={f.id} className="bg-gray-800/50 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-white">{f.data_type || 'SEC Filing'}</span>
                        <span className="text-xs text-gray-500">{f.created_at ? new Date(f.created_at).toLocaleDateString() : ''}</span>
                      </div>
                      {items.length > 0 ? (
                        <div className="space-y-1">
                          {items.slice(0, 3).map((item, idx) => (
                            <div key={idx} className="text-xs text-gray-400">
                              <span className="text-gray-300 font-medium">{item.title || item.name || `Item ${idx + 1}`}</span>
                              {item.description && <span className="ml-2">{item.description.slice(0, 120)}</span>}
                            </div>
                          ))}
                          {items.length > 3 && <span className="text-xs text-gray-500">+{items.length - 3} more</span>}
                        </div>
                      ) : f.source_url ? (
                        <a href={f.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary-400 hover:underline">{f.source_url}</a>
                      ) : null}
                    </div>
                  )
                })}
              </div>
            )}
          </CollapsibleSection>

          {/* Spider Data Section */}
          <CollapsibleSection title="Spider Data" count={data.spider_data.total}>
            {data.spider_data.results.length === 0 ? (
              <EmptyState message="No spider data mentioning this ticker." />
            ) : (
              <div className="space-y-2">
                {data.spider_data.results.map((s) => (
                  <div key={s.id} className="bg-gray-800/50 rounded-lg p-3 flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-300 text-xs">{s.spider_name}</span>
                        {s.data_type && <span className="text-xs text-gray-500">{s.data_type}</span>}
                      </div>
                      <p className="text-sm text-gray-300 truncate">{s.summary || 'No summary'}</p>
                    </div>
                    <span className="text-xs text-gray-500 flex-shrink-0">{s.created_at ? new Date(s.created_at).toLocaleDateString() : ''}</span>
                  </div>
                ))}
              </div>
            )}
          </CollapsibleSection>
        </div>
      )}
    </div>
  )
}

function formatMarketCap(value: number): string {
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`
  return `$${value.toLocaleString()}`
}

function CollapsibleSection({ title, count, children }: { title: string; count: number; children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(true)
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-gray-300">{title}</h3>
          <span className="px-1.5 py-0.5 rounded bg-gray-700 text-xs text-gray-400">{count}</span>
        </div>
        {isOpen ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
      </button>
      {isOpen && <div className="px-4 pb-4">{children}</div>}
    </div>
  )
}

function AnalysisBadge({ prefix, value, config }: { prefix: string; value: string; config: Record<string, { label: string; color: string }> }) {
  const cfg = config[value] || { label: value, color: 'bg-gray-500/20 text-gray-400' }
  return <span className={cn('px-2 py-1 rounded text-xs', cfg.color)}>{prefix}: {cfg.label}</span>
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
                {(alert.confidence_score * 100).toFixed(0)}% conf
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
      <div className="space-y-2">
        {items.slice(0, 10).map((item, idx) => {
          if (typeof item === 'string') {
            return (
              <div key={idx} className="text-xs text-gray-400 bg-gray-800/50 rounded px-2 py-1">
                {item}
              </div>
            )
          }
          const obj = item as Record<string, unknown>
          const ticker = obj.ticker as string | undefined
          const recommendation = obj.recommendation as string | undefined
          const confidence = obj.confidence as string | undefined
          const reasoning = obj.reasoning as string | undefined
          const bullCase = (obj.bull_case || obj.bull_rebuttal) as Record<string, unknown> | undefined
          const bearCase = (obj.bear_case || obj.bear_rebuttal) as Record<string, unknown> | undefined
          const bullArgs = (bullCase?.arguments as string[]) || []
          const bearArgs = (bearCase?.arguments as string[]) || []
          const bullRisks = (bullCase?.risks as string[]) || []
          const bearRisks = (bearCase?.risks as string[]) || []
          const targetUp = (bullCase?.target_upside as string) || ''
          const targetDown = (bearCase?.target_downside as string) || ''

          return (
            <div key={idx} className="bg-gray-800/50 rounded-lg p-3 space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono font-bold text-white">{ticker || `Item ${idx + 1}`}</span>
                {recommendation && (
                  <span className={cn('text-xs px-1.5 py-0.5 rounded', {
                    'bg-green-500/20 text-green-400': recommendation === 'BULLISH',
                    'bg-red-500/20 text-red-400': recommendation === 'BEARISH',
                    'bg-purple-500/20 text-purple-400': recommendation === 'DEBATE',
                    'bg-gray-500/20 text-gray-400': recommendation === 'NEUTRAL' || recommendation === 'MIXED',
                  })}>{recommendation}</span>
                )}
                {confidence && (
                  <span className="text-xs text-gray-500">{confidence} confidence</span>
                )}
                {targetUp && <span className="text-xs text-green-400 ml-auto">{targetUp}</span>}
                {targetDown && <span className="text-xs text-red-400 ml-auto">{targetDown}</span>}
              </div>

              {reasoning && <p className="text-xs text-gray-400 italic">{reasoning}</p>}

              {bullArgs.length > 0 && (
                <div>
                  <span className="text-xs text-green-500 font-medium">Bull:</span>
                  <ul className="ml-3 mt-0.5 space-y-0.5">
                    {bullArgs.slice(0, 3).map((arg, i) => (
                      <li key={i} className="text-xs text-gray-400">- {arg}</li>
                    ))}
                  </ul>
                </div>
              )}

              {bearArgs.length > 0 && (
                <div>
                  <span className="text-xs text-red-500 font-medium">Bear:</span>
                  <ul className="ml-3 mt-0.5 space-y-0.5">
                    {bearArgs.slice(0, 3).map((arg, i) => (
                      <li key={i} className="text-xs text-gray-400">- {arg}</li>
                    ))}
                  </ul>
                </div>
              )}

              {(bullRisks.length > 0 || bearRisks.length > 0) && (
                <div>
                  <span className="text-xs text-orange-500 font-medium">Risks:</span>
                  <ul className="ml-3 mt-0.5 space-y-0.5">
                    {[...bullRisks, ...bearRisks].slice(0, 3).map((risk, i) => (
                      <li key={i} className="text-xs text-gray-500">- {risk}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )
        })}
        {items.length > 10 && <span className="text-xs text-gray-500">+{items.length - 10} more</span>}
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
