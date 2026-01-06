import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { bettingApi } from '@/lib/api'
import {
  TrendingUp, TrendingDown, DollarSign, Target, Zap, AlertTriangle,
  RefreshCw, Loader2, Trophy, Activity, PieChart, BarChart3,
  Clock, CheckCircle, Flame, Search
} from 'lucide-react'
import { cn } from '@/lib/cn'

type BettingTab = 'overview' | 'arbitrage' | 'markets' | 'odds' | 'bankroll' | 'wagers'

const tabs = [
  { id: 'overview' as BettingTab, label: 'Overview', icon: PieChart },
  { id: 'arbitrage' as BettingTab, label: 'Arbitrage', icon: Flame },
  { id: 'markets' as BettingTab, label: 'Markets', icon: BarChart3 },
  { id: 'odds' as BettingTab, label: 'Live Odds', icon: Activity },
  { id: 'bankroll' as BettingTab, label: 'Bankroll', icon: DollarSign },
  { id: 'wagers' as BettingTab, label: 'My Wagers', icon: Trophy },
]

interface StatCardProps {
  label: string
  value: string | number
  icon: React.ElementType
  color: string
  trend?: { value: number; isPositive: boolean }
}

function StatCard({ label, value, icon: Icon, color, trend }: StatCardProps) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
          {trend && (
            <div className={cn('flex items-center gap-1 text-xs mt-1', trend.isPositive ? 'text-accent-green' : 'text-accent-red')}>
              {trend.isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
              <span>{trend.isPositive ? '+' : ''}{trend.value}%</span>
            </div>
          )}
        </div>
        <div className={cn('h-12 w-12 rounded-xl flex items-center justify-center', color)}>
          <Icon size={24} className="text-white" />
        </div>
      </div>
    </div>
  )
}

interface WagerRowProps {
  wager: {
    id: string
    bet_type: string
    pick: string
    odds: number
    stake: number
    status: string
    profit_loss?: number
    created_at: string
  }
}

function WagerRow({ wager }: WagerRowProps) {
  const statusColors: Record<string, string> = {
    pending: 'text-accent-amber bg-accent-amber/20',
    won: 'text-accent-green bg-accent-green/20',
    lost: 'text-accent-red bg-accent-red/20',
    cancelled: 'text-gray-400 bg-gray-400/20',
  }

  return (
    <tr className="border-b border-dark-border hover:bg-dark-bg/50">
      <td className="py-3 px-4">
        <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
          {wager.bet_type}
        </span>
      </td>
      <td className="py-3 px-4 font-medium">{wager.pick}</td>
      <td className="py-3 px-4">
        <span className={cn('font-mono', wager.odds > 0 ? 'text-accent-green' : 'text-accent-red')}>
          {wager.odds > 0 ? '+' : ''}{wager.odds}
        </span>
      </td>
      <td className="py-3 px-4 font-medium">${wager.stake.toFixed(2)}</td>
      <td className="py-3 px-4">
        <span className={cn('text-xs px-2 py-0.5 rounded', statusColors[wager.status] || statusColors.pending)}>
          {wager.status}
        </span>
      </td>
      <td className="py-3 px-4">
        {wager.profit_loss !== undefined ? (
          <span className={cn('font-medium', wager.profit_loss >= 0 ? 'text-accent-green' : 'text-accent-red')}>
            {wager.profit_loss >= 0 ? '+' : ''}${wager.profit_loss.toFixed(2)}
          </span>
        ) : (
          <span className="text-gray-500">-</span>
        )}
      </td>
    </tr>
  )
}

interface ArbitrageCardProps {
  arb: {
    event: string
    sport: string
    profit_percent: number
    bookmakers: { name: string; odds: number; pick: string }[]
    expires_at?: string
  }
}

function ArbitrageCard({ arb }: ArbitrageCardProps) {
  const profitPercent = arb.profit_percent ?? 0
  const isHot = profitPercent >= 1.5
  const bookmakers = arb.bookmakers ?? []

  return (
    <div className={cn(
      'card p-4 border-l-4',
      isHot ? 'border-l-accent-red' : 'border-l-accent-amber'
    )}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <h4 className="font-medium">{arb.event || 'Unknown Event'}</h4>
            {isHot && (
              <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-accent-red/20 text-accent-red">
                <Flame size={10} /> HOT
              </span>
            )}
          </div>
          <p className="text-sm text-gray-400">{arb.sport || 'Unknown Sport'}</p>
        </div>
        <div className="text-right">
          <p className={cn('text-xl font-bold', isHot ? 'text-accent-red' : 'text-accent-amber')}>
            +{profitPercent.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-500">guaranteed profit</p>
        </div>
      </div>
      <div className="space-y-2">
        {bookmakers.map((book, i) => (
          <div key={i} className="flex items-center justify-between p-2 rounded bg-dark-bg">
            <div>
              <span className="text-sm font-medium">{book.name || 'Unknown'}</span>
              <span className="text-gray-400 mx-2">→</span>
              <span className="text-sm text-primary-400">{book.pick || '-'}</span>
            </div>
            <span className="font-mono text-accent-green">
              {(book.odds ?? 0) > 0 ? '+' : ''}{book.odds ?? 0}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function BettingPage() {
  const [activeTab, setActiveTab] = useState<BettingTab>('overview')
  const [sportFilter, setSportFilter] = useState('all')

  // Fetch betting stats
  const { data: statsData, refetch: refetchStats } = useQuery({
    queryKey: ['betting-stats'],
    queryFn: () => bettingApi.stats(),
    refetchInterval: 60000, // Refresh every minute
  })

  // Fetch recent wagers
  const { data: wagersData, isLoading: wagersLoading } = useQuery({
    queryKey: ['betting-wagers'],
    queryFn: () => bettingApi.wagers(),
  })

  // Fetch arbitrage opportunities
  const { data: arbData, isLoading: arbLoading, refetch: refetchArb } = useQuery({
    queryKey: ['betting-arbitrage'],
    queryFn: () => bettingApi.arbitrageScan(),
    enabled: activeTab === 'arbitrage',
  })

  // Fetch live odds
  const { data: oddsData, isLoading: oddsLoading, refetch: refetchOdds } = useQuery({
    queryKey: ['betting-live-odds'],
    queryFn: () => bettingApi.liveOddsWithScores(),
    enabled: activeTab === 'odds',
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch bankroll
  const { data: bankrollData } = useQuery({
    queryKey: ['betting-bankroll'],
    queryFn: () => bettingApi.bankrollStats(),
    enabled: activeTab === 'bankroll',
  })

  // Fetch markets
  const { data: marketsData, isLoading: marketsLoading } = useQuery({
    queryKey: ['betting-markets'],
    queryFn: () => bettingApi.markets(),
    enabled: activeTab === 'markets',
  })

  const stats = statsData?.data || {}
  const wagers = wagersData?.data?.wagers || []
  const arbitrageOpps = arbData?.data?.opportunities || []
  const liveOdds = oddsData?.data?.games || []
  const bankroll = bankrollData?.data || {}
  const markets = marketsData?.data?.markets || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Betting Dashboard</h1>
          <p className="text-gray-400">Sports betting intelligence and arbitrage detection</p>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={() => {
            refetchStats()
            if (activeTab === 'arbitrage') refetchArb()
            if (activeTab === 'odds') refetchOdds()
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
            <StatCard
              label="Total P/L"
              value={`$${(stats.total_profit_loss || 0).toFixed(2)}`}
              icon={DollarSign}
              color="bg-primary-600"
              trend={{ value: stats.roi || 0, isPositive: (stats.roi || 0) >= 0 }}
            />
            <StatCard
              label="Win Rate"
              value={`${(stats.win_rate || 0).toFixed(1)}%`}
              icon={Target}
              color="bg-accent-green"
            />
            <StatCard
              label="Total Wagers"
              value={stats.total_wagers || 0}
              icon={Trophy}
              color="bg-accent-amber"
            />
            <StatCard
              label="Active Bets"
              value={stats.active_wagers || 0}
              icon={Activity}
              color="bg-accent-purple"
            />
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Recent Wagers */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Wagers</h3>
                <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                  {wagers.length} total
                </span>
              </div>
              {wagersLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 size={24} className="animate-spin text-primary-400" />
                </div>
              ) : wagers.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-400 border-b border-dark-border">
                        <th className="pb-2 px-2">Type</th>
                        <th className="pb-2 px-2">Pick</th>
                        <th className="pb-2 px-2">Odds</th>
                        <th className="pb-2 px-2">Stake</th>
                        <th className="pb-2 px-2">Status</th>
                        <th className="pb-2 px-2">P/L</th>
                      </tr>
                    </thead>
                    <tbody>
                      {wagers.slice(0, 5).map((wager: WagerRowProps['wager']) => (
                        <WagerRow key={wager.id} wager={wager} />
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Trophy size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No wagers yet</p>
                </div>
              )}
            </div>

            {/* Performance */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Performance</h3>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 rounded-lg bg-accent-green/10">
                  <p className="text-2xl font-bold text-accent-green">{stats.wins || 0}</p>
                  <p className="text-xs text-gray-400">Wins</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-accent-red/10">
                  <p className="text-2xl font-bold text-accent-red">{stats.losses || 0}</p>
                  <p className="text-xs text-gray-400">Losses</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-accent-amber/10">
                  <p className="text-2xl font-bold text-accent-amber">{stats.pending || 0}</p>
                  <p className="text-xs text-gray-400">Pending</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">ROI</span>
                  <span className={cn('font-medium', (stats.roi || 0) >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                    {(stats.roi || 0) >= 0 ? '+' : ''}{(stats.roi || 0).toFixed(2)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Average Stake</span>
                  <span className="font-medium">${(stats.avg_stake || 0).toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Best Win</span>
                  <span className="font-medium text-accent-green">+${(stats.best_win || 0).toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Current Streak</span>
                  <span className={cn('font-medium', (stats.streak || 0) >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                    {stats.streak || 0} {(stats.streak || 0) >= 0 ? 'W' : 'L'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Arbitrage Tab */}
      {activeTab === 'arbitrage' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="flex items-center gap-4">
            <select
              value={sportFilter}
              onChange={(e) => setSportFilter(e.target.value)}
              className="bg-dark-card border border-dark-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
            >
              <option value="all">All Sports</option>
              <option value="nfl">NFL</option>
              <option value="nba">NBA</option>
              <option value="mlb">MLB</option>
              <option value="nhl">NHL</option>
              <option value="soccer">Soccer</option>
            </select>
            <button
              className="btn btn-primary flex items-center gap-2"
              onClick={() => refetchArb()}
            >
              <Search size={16} />
              Scan Now
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              label="Total Arbs"
              value={arbitrageOpps.length}
              icon={Zap}
              color="bg-accent-pink"
            />
            <StatCard
              label="HOT (1.5%+)"
              value={arbitrageOpps.filter((a: ArbitrageCardProps['arb']) => a.profit_percent >= 1.5).length}
              icon={Flame}
              color="bg-accent-red"
            />
            <StatCard
              label="Avg Profit"
              value={`${(arbitrageOpps.reduce((acc: number, a: ArbitrageCardProps['arb']) => acc + a.profit_percent, 0) / (arbitrageOpps.length || 1)).toFixed(2)}%`}
              icon={TrendingUp}
              color="bg-accent-amber"
            />
            <StatCard
              label="Last Scan"
              value={new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              icon={Clock}
              color="bg-accent-green"
            />
          </div>

          {/* Arbitrage Cards */}
          {arbLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : arbitrageOpps.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {arbitrageOpps.map((arb: ArbitrageCardProps['arb'], i: number) => (
                <ArbitrageCard key={i} arb={arb} />
              ))}
            </div>
          ) : (
            <div className="card p-12 text-center">
              <AlertTriangle size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2">No Arbitrage Found</h3>
              <p className="text-gray-400">Click "Scan Now" to search for opportunities</p>
            </div>
          )}
        </div>
      )}

      {/* Markets Tab */}
      {activeTab === 'markets' && (
        <div className="space-y-6">
          {marketsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : markets.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {markets.map((market: { id: string; name: string; sport: string; event_count: number }, i: number) => (
                <div key={i} className="card p-4 hover:border-primary-500 transition-colors cursor-pointer">
                  <h4 className="font-medium mb-1">{market.name}</h4>
                  <p className="text-sm text-gray-400">{market.sport}</p>
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-dark-border">
                    <span className="text-xs text-gray-500">{market.event_count} events</span>
                    <Activity size={14} className="text-primary-400" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card p-12 text-center">
              <BarChart3 size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2">No Markets Available</h3>
              <p className="text-gray-400">Check back later for active betting markets</p>
            </div>
          )}
        </div>
      )}

      {/* Live Odds Tab */}
      {activeTab === 'odds' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-400">
              <Clock size={14} className="inline mr-1" />
              Auto-refreshes every 30 seconds
            </p>
            <button
              className="btn btn-secondary text-sm flex items-center gap-2"
              onClick={() => refetchOdds()}
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>

          {oddsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : liveOdds.length > 0 ? (
            <div className="space-y-4">
              {liveOdds.map((game: { id: string; home_team: string; away_team: string; sport: string; home_odds: number; away_odds: number; commence_time: string }, i: number) => (
                <div key={i} className="card p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                      {game.sport}
                    </span>
                    <span className="text-xs text-gray-500">{game.commence_time}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 items-center">
                    <div className="text-center">
                      <p className="font-medium">{game.away_team}</p>
                      <p className="text-lg font-bold text-accent-green mt-1">
                        {game.away_odds > 0 ? '+' : ''}{game.away_odds}
                      </p>
                    </div>
                    <div className="text-center text-gray-500">
                      <span className="text-sm">@</span>
                    </div>
                    <div className="text-center">
                      <p className="font-medium">{game.home_team}</p>
                      <p className="text-lg font-bold text-accent-green mt-1">
                        {game.home_odds > 0 ? '+' : ''}{game.home_odds}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card p-12 text-center">
              <Activity size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2">No Live Games</h3>
              <p className="text-gray-400">No games with live odds available right now</p>
            </div>
          )}
        </div>
      )}

      {/* Bankroll Tab */}
      {activeTab === 'bankroll' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              label="Total Bankroll"
              value={`$${(bankroll.total || 0).toFixed(2)}`}
              icon={DollarSign}
              color="bg-accent-green"
            />
            <StatCard
              label="At Risk"
              value={`$${(bankroll.at_risk || 0).toFixed(2)}`}
              icon={AlertTriangle}
              color="bg-accent-amber"
            />
            <StatCard
              label="Available"
              value={`$${(bankroll.available || 0).toFixed(2)}`}
              icon={CheckCircle}
              color="bg-primary-600"
            />
            <StatCard
              label="Kelly Suggested"
              value={`${(bankroll.kelly_percent || 0).toFixed(1)}%`}
              icon={Target}
              color="bg-accent-purple"
            />
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Bankroll Management Tips</h3>
            <div className="space-y-3 text-sm text-gray-400">
              <p>• Never bet more than 5% of your bankroll on a single wager</p>
              <p>• Use the Kelly Criterion to size your bets optimally</p>
              <p>• Track all bets to understand your true ROI</p>
              <p>• Set stop-loss limits to protect your bankroll</p>
            </div>
          </div>
        </div>
      )}

      {/* My Wagers Tab */}
      {activeTab === 'wagers' && (
        <div className="space-y-6">
          {wagersLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : wagers.length > 0 ? (
            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-dark-bg">
                    <tr className="text-left text-gray-400">
                      <th className="py-3 px-4">Type</th>
                      <th className="py-3 px-4">Pick</th>
                      <th className="py-3 px-4">Odds</th>
                      <th className="py-3 px-4">Stake</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">P/L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {wagers.map((wager: WagerRowProps['wager']) => (
                      <WagerRow key={wager.id} wager={wager} />
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="card p-12 text-center">
              <Trophy size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2">No Wagers Yet</h3>
              <p className="text-gray-400">Start placing bets to track your performance</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
