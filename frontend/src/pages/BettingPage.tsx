import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { bettingApi, humanApi } from '@/lib/api'
import {
  TrendingUp, TrendingDown, DollarSign, Target, Zap, AlertTriangle,
  RefreshCw, Loader2, Trophy, Activity, PieChart, BarChart3,
  Clock, CheckCircle, Flame, Search, Eye, XCircle, CircleDot,
  Award, Layers, ChevronDown, ChevronUp, History
} from 'lucide-react'
import { cn } from '@/lib/cn'

type BettingTab = 'overview' | 'arbitrage' | 'markets' | 'odds' | 'bankroll' | 'wagers' | 'watching'

const tabs = [
  { id: 'overview' as BettingTab, label: 'Overview', icon: PieChart },
  { id: 'arbitrage' as BettingTab, label: 'Arbitrage', icon: Flame },
  { id: 'watching' as BettingTab, label: 'Watching', icon: Eye },
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

// Session 746: Rich stats interfaces
interface RecordBreakdown {
  wins: number
  losses: number
  profit: number
}

interface SportStats {
  wins: number
  losses: number
  pushes?: number
  profit: number
  wagers: number
}

interface BettingStatsData {
  total_wagers: number
  total_stake: number
  total_profit_loss: number
  wins: number
  losses: number
  pushes: number
  pending: number
  win_rate: number
  roi: number
  current_streak: number
  longest_win_streak: number
  longest_loss_streak: number
  singles_record: RecordBreakdown
  parlays_record: RecordBreakdown
  stats_by_sport: Record<string, SportStats>
  last_updated: string
}

interface WagerLeg {
  event_id: string
  sport: string
  matchup: string
  market_type: string
  pick: string
  odds: number
  line: number | null
  bookmaker: string
  status: string
  final_score: string
}

interface WagerRowProps {
  wager: {
    id: string
    type: string
    bet_type: string
    pick: string
    odds: number
    stake: number
    potential_payout: number
    status: string
    profit_loss?: number
    result_amount?: number
    created_at: string
    placed_at: string
    settled_at?: string
    legs?: WagerLeg[]
  }
  onExpand?: (id: string) => void
  isExpanded?: boolean
}

function WagerRow({ wager, onExpand, isExpanded }: WagerRowProps) {
  const statusColors: Record<string, string> = {
    pending: 'text-accent-amber bg-accent-amber/20',
    won: 'text-accent-green bg-accent-green/20',
    lost: 'text-accent-red bg-accent-red/20',
    push: 'text-accent-purple bg-accent-purple/20',
    cancelled: 'text-gray-400 bg-gray-400/20',
  }

  const profitLoss = wager.result_amount ?? wager.profit_loss
  const legs = wager.legs || []
  const hasLegs = legs.length > 0

  return (
    <>
      <tr
        className={cn(
          "border-b border-dark-border hover:bg-dark-bg/50 transition-colors",
          hasLegs && "cursor-pointer"
        )}
        onClick={() => hasLegs && onExpand?.(wager.id)}
      >
        <td className="py-3 px-4">
          <div className="flex items-center gap-2">
            {hasLegs && (
              isExpanded ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />
            )}
            <span className={cn(
              "text-xs px-2 py-0.5 rounded",
              wager.type === 'parlay' ? "bg-accent-purple/20 text-accent-purple" : "bg-primary-600/20 text-primary-400"
            )}>
              {wager.type === 'parlay' ? `${legs.length}-leg Parlay` : wager.bet_type || 'Single'}
            </span>
          </div>
        </td>
        <td className="py-3 px-4 font-medium">
          {wager.type === 'parlay' && legs.length > 0 ? (
            <span className="text-sm">{legs[0]?.matchup || 'Multiple Events'}</span>
          ) : (
            wager.pick || legs[0]?.pick || '-'
          )}
        </td>
        <td className="py-3 px-4">
          <span className={cn('font-mono', wager.odds > 0 ? 'text-accent-green' : 'text-accent-red')}>
            {wager.odds > 0 ? '+' : ''}{wager.odds}
          </span>
        </td>
        <td className="py-3 px-4 font-medium">${wager.stake?.toFixed(2) || '0.00'}</td>
        <td className="py-3 px-4">
          <span className={cn('text-xs px-2 py-0.5 rounded', statusColors[wager.status] || statusColors.pending)}>
            {wager.status}
          </span>
        </td>
        <td className="py-3 px-4">
          {profitLoss !== undefined && profitLoss !== null ? (
            <span className={cn('font-medium', profitLoss >= 0 ? 'text-accent-green' : 'text-accent-red')}>
              {profitLoss >= 0 ? '+' : ''}${profitLoss.toFixed(2)}
            </span>
          ) : wager.potential_payout ? (
            <span className="text-gray-400 text-sm">→ ${wager.potential_payout.toFixed(2)}</span>
          ) : (
            <span className="text-gray-500">-</span>
          )}
        </td>
        <td className="py-3 px-4 text-xs text-gray-500">
          {wager.settled_at ? (
            <span className="flex items-center gap-1">
              <CheckCircle size={12} className="text-accent-green" />
              {new Date(wager.settled_at).toLocaleDateString()}
            </span>
          ) : wager.placed_at ? (
            new Date(wager.placed_at).toLocaleDateString()
          ) : wager.created_at ? (
            new Date(wager.created_at).toLocaleDateString()
          ) : '-'}
        </td>
      </tr>
      {/* Expanded leg details */}
      {isExpanded && hasLegs && (
        <tr className="bg-dark-bg/30">
          <td colSpan={7} className="px-6 py-3">
            <div className="space-y-2">
              <div className="text-xs text-gray-400 mb-2 flex items-center gap-2">
                <Layers size={12} />
                {legs.length} Leg{legs.length > 1 ? 's' : ''} in this wager
              </div>
              {legs.map((leg, i) => (
                <div
                  key={i}
                  className={cn(
                    "flex items-center justify-between p-2 rounded border-l-2",
                    leg.status === 'won' ? 'bg-accent-green/5 border-accent-green' :
                    leg.status === 'lost' ? 'bg-accent-red/5 border-accent-red' :
                    leg.status === 'push' ? 'bg-accent-purple/5 border-accent-purple' :
                    'bg-dark-card border-dark-border'
                  )}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-1.5 py-0.5 rounded bg-dark-border text-gray-400">
                        {leg.sport?.split('_')[1]?.toUpperCase() || leg.sport}
                      </span>
                      <span className="font-medium text-sm">{leg.matchup}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                      <span>{leg.market_type}: <span className="text-primary-400">{leg.pick}</span></span>
                      {leg.line && <span>Line: {leg.line}</span>}
                      <span>@ {leg.bookmaker}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={cn('font-mono text-sm', leg.odds > 0 ? 'text-accent-green' : 'text-accent-red')}>
                      {leg.odds > 0 ? '+' : ''}{leg.odds}
                    </span>
                    {leg.final_score && (
                      <div className="text-xs text-gray-400 mt-1">Final: {leg.final_score}</div>
                    )}
                    <span className={cn(
                      'text-xs px-1.5 py-0.5 rounded ml-2',
                      statusColors[leg.status] || 'bg-gray-500/20 text-gray-400'
                    )}>
                      {leg.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </td>
        </tr>
      )}
    </>
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

// Session 746: Watched Item interface
interface WatchedItem {
  id: string
  title: string
  description: string
  item_type: string
  source_agent?: string
  payload?: {
    event?: string
    sport?: string
    profit_percent?: number
    bookmakers?: { name: string; odds: number; pick: string }[]
    game_time?: string
    expires_at?: string
  }
  created_at: string
  verification_outcome?: 'pending' | 'won' | 'lost' | 'push' | 'cancelled' | null
  verification_profit?: number | null
  verification_notes?: string
  verified_at?: string | null
}

interface WatchedItemCardProps {
  item: WatchedItem
  onVerify: (itemId: string, outcome: string, profit?: number, notes?: string) => void
  isVerifying: boolean
}

// Session 746: Watched Item Card with verification UI
function WatchedItemCard({ item, onVerify, isVerifying }: WatchedItemCardProps) {
  const [showVerifyPanel, setShowVerifyPanel] = useState(false)
  const [verifyOutcome, setVerifyOutcome] = useState<string>('won')
  const [verifyProfit, setVerifyProfit] = useState<string>('')
  const [verifyNotes, setVerifyNotes] = useState<string>('')

  const payload = item.payload || {}
  const profitPercent = payload.profit_percent ?? 0
  const bookmakers = payload.bookmakers ?? []
  const isPending = item.verification_outcome === 'pending' || !item.verification_outcome

  const handleVerify = () => {
    const profit = verifyProfit ? parseFloat(verifyProfit) : undefined
    onVerify(item.id, verifyOutcome, profit, verifyNotes)
    setShowVerifyPanel(false)
  }

  const outcomeColors: Record<string, string> = {
    pending: 'bg-cyan-500/20 text-cyan-400',
    won: 'bg-accent-green/20 text-accent-green',
    lost: 'bg-accent-red/20 text-accent-red',
    push: 'bg-accent-amber/20 text-accent-amber',
    cancelled: 'bg-gray-500/20 text-gray-400',
  }

  return (
    <div className="card p-4 border-l-4 border-l-cyan-500">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <Eye size={16} className="text-cyan-400" />
            <h4 className="font-medium">{payload.event || item.title || 'Watched Opportunity'}</h4>
            <span className={cn('text-xs px-2 py-0.5 rounded', outcomeColors[item.verification_outcome || 'pending'])}>
              {item.verification_outcome || 'pending'}
            </span>
          </div>
          <p className="text-sm text-gray-400">{payload.sport || item.source_agent || 'Arbitrage'}</p>
          <p className="text-xs text-gray-500 mt-1">
            <Clock size={10} className="inline mr-1" />
            Watching since {new Date(item.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="text-right">
          {profitPercent > 0 && (
            <>
              <p className="text-xl font-bold text-cyan-400">+{profitPercent.toFixed(2)}%</p>
              <p className="text-xs text-gray-500">expected profit</p>
            </>
          )}
        </div>
      </div>

      {/* Bookmaker Details */}
      {bookmakers.length > 0 && (
        <div className="space-y-2 mb-3">
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
      )}

      {/* Description if no bookmakers */}
      {bookmakers.length === 0 && item.description && (
        <p className="text-sm text-gray-400 mb-3">{item.description}</p>
      )}

      {/* Verification Panel */}
      {isPending && !showVerifyPanel && (
        <button
          onClick={() => setShowVerifyPanel(true)}
          className="btn btn-sm bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 w-full"
        >
          <CheckCircle size={14} className="mr-2" />
          Record Outcome
        </button>
      )}

      {showVerifyPanel && (
        <div className="mt-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
          <h5 className="text-sm font-medium mb-3">Record Verification</h5>

          {/* Outcome Buttons */}
          <div className="flex gap-2 mb-3">
            {[
              { value: 'won', label: 'Won', icon: CheckCircle, color: 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30' },
              { value: 'lost', label: 'Lost', icon: XCircle, color: 'bg-accent-red/20 text-accent-red hover:bg-accent-red/30' },
              { value: 'push', label: 'Push', icon: CircleDot, color: 'bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30' },
              { value: 'cancelled', label: 'Cancelled', icon: XCircle, color: 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30' },
            ].map(({ value, label, icon: Icon, color }) => (
              <button
                key={value}
                onClick={() => setVerifyOutcome(value)}
                className={cn(
                  'flex-1 py-2 px-3 rounded text-xs font-medium transition-colors flex items-center justify-center gap-1',
                  verifyOutcome === value ? color + ' ring-1 ring-current' : 'bg-dark-card hover:bg-dark-border'
                )}
              >
                <Icon size={12} />
                {label}
              </button>
            ))}
          </div>

          {/* Profit Input */}
          <div className="mb-3">
            <label className="text-xs text-gray-400 mb-1 block">Profit/Loss ($)</label>
            <input
              type="number"
              step="0.01"
              value={verifyProfit}
              onChange={(e) => setVerifyProfit(e.target.value)}
              placeholder="e.g., 25.50 or -10.00"
              className="w-full px-3 py-2 text-sm rounded bg-dark-card border border-dark-border focus:border-primary-500 focus:outline-none"
            />
          </div>

          {/* Notes Input */}
          <div className="mb-3">
            <label className="text-xs text-gray-400 mb-1 block">Notes (optional)</label>
            <input
              type="text"
              value={verifyNotes}
              onChange={(e) => setVerifyNotes(e.target.value)}
              placeholder="e.g., Game went to overtime"
              className="w-full px-3 py-2 text-sm rounded bg-dark-card border border-dark-border focus:border-primary-500 focus:outline-none"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              onClick={() => setShowVerifyPanel(false)}
              className="btn btn-sm flex-1"
            >
              Cancel
            </button>
            <button
              onClick={handleVerify}
              disabled={isVerifying}
              className="btn btn-sm btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {isVerifying ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle size={14} />
                  Save
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Verified Result Display */}
      {!isPending && (
        <div className={cn(
          'mt-3 p-3 rounded-lg flex items-center justify-between',
          item.verification_outcome === 'won' ? 'bg-accent-green/10' :
          item.verification_outcome === 'lost' ? 'bg-accent-red/10' : 'bg-gray-500/10'
        )}>
          <div>
            <span className="text-sm font-medium">
              {item.verification_outcome === 'won' ? 'Would Have Won!' :
               item.verification_outcome === 'lost' ? 'Would Have Lost' :
               item.verification_outcome === 'push' ? 'Push (Tie)' : 'Cancelled'}
            </span>
            {item.verification_notes && (
              <p className="text-xs text-gray-400 mt-1">{item.verification_notes}</p>
            )}
          </div>
          {item.verification_profit !== null && item.verification_profit !== undefined && (
            <span className={cn(
              'text-lg font-bold',
              item.verification_profit >= 0 ? 'text-accent-green' : 'text-accent-red'
            )}>
              {item.verification_profit >= 0 ? '+' : ''}${item.verification_profit.toFixed(2)}
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default function BettingPage() {
  const [activeTab, setActiveTab] = useState<BettingTab>('overview')
  const [sportFilter, setSportFilter] = useState('all')
  const [watchingFilter, setWatchingFilter] = useState<'all' | 'pending' | 'verified'>('all')
  const [expandedWagers, setExpandedWagers] = useState<Set<string>>(new Set())
  const [showDetailedStats, setShowDetailedStats] = useState(false)
  const queryClient = useQueryClient()

  const toggleWagerExpand = (wagerId: string) => {
    setExpandedWagers(prev => {
      const newSet = new Set(prev)
      if (newSet.has(wagerId)) {
        newSet.delete(wagerId)
      } else {
        newSet.add(wagerId)
      }
      return newSet
    })
  }

  // Session 746: Fetch watched items
  const { data: watchedData, isLoading: watchedLoading, refetch: refetchWatched } = useQuery({
    queryKey: ['betting-watched', watchingFilter],
    queryFn: () => humanApi.attention({
      limit: 100,
      status: watchingFilter === 'all' ? ['watching', 'verified'] :
              watchingFilter === 'pending' ? ['watching'] : ['verified'],
    }),
    enabled: activeTab === 'watching',
  })

  // Session 746: Verification mutation
  const verifyMutation = useMutation({
    mutationFn: ({ itemId, outcome, profit, notes }: { itemId: string; outcome: string; profit?: number; notes?: string }) =>
      humanApi.verify(itemId, outcome, profit, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['betting-watched'] })
    },
  })

  const watchedItems: WatchedItem[] = (watchedData?.data?.items || []).filter(
    (item: WatchedItem) => item.item_type === 'arbitrage'
  )

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

  // Session 745: Fetch line movement data
  const { data: lineMovementData, isLoading: lineMovementLoading } = useQuery({
    queryKey: ['betting-line-movement'],
    queryFn: () => bettingApi.lineMovement(),
    enabled: activeTab === 'odds',
    refetchInterval: 60000, // Refresh every minute
  })

  const stats: Partial<BettingStatsData> = statsData?.data?.stats || statsData?.data || {}
  const wagers = wagersData?.data?.wagers || []
  const singlesRecord = stats.singles_record || { wins: 0, losses: 0, profit: 0 }
  const parlaysRecord = stats.parlays_record || { wins: 0, losses: 0, profit: 0 }
  const statsBySport = stats.stats_by_sport || {}
  const arbitrageOpps = arbData?.data?.opportunities || []
  const liveOdds = oddsData?.data?.games || []
  const bankroll = bankrollData?.data || {}
  const markets = marketsData?.data?.markets || []
  // Session 745: Line movement data
  const lineMovement = lineMovementData?.data?.games || []

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
          {/* Stats Grid - Primary Row */}
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
              label="Pending"
              value={stats.pending || 0}
              icon={Activity}
              color="bg-accent-purple"
            />
          </div>

          {/* Stats Grid - Secondary Row (Streak Stats) */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              label="Current Streak"
              value={`${stats.current_streak || 0}${(stats.current_streak || 0) >= 0 ? 'W' : 'L'}`}
              icon={Flame}
              color={(stats.current_streak || 0) >= 0 ? "bg-accent-green" : "bg-accent-red"}
            />
            <StatCard
              label="Best Win Streak"
              value={stats.longest_win_streak || 0}
              icon={Award}
              color="bg-accent-green"
            />
            <StatCard
              label="Worst Loss Streak"
              value={stats.longest_loss_streak || 0}
              icon={TrendingDown}
              color="bg-accent-red"
            />
            <StatCard
              label="Pushes"
              value={stats.pushes || 0}
              icon={CircleDot}
              color="bg-gray-600"
            />
          </div>

          {/* Detailed Stats Toggle */}
          <button
            onClick={() => setShowDetailedStats(!showDetailedStats)}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            {showDetailedStats ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            {showDetailedStats ? 'Hide' : 'Show'} Detailed Breakdown
          </button>

          {/* Detailed Stats Panel */}
          {showDetailedStats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Singles vs Parlays */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Layers size={18} className="text-primary-400" />
                  Singles vs Parlays
                </h3>
                <div className="space-y-4">
                  {/* Singles */}
                  <div className="p-3 rounded-lg bg-primary-600/10 border border-primary-600/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-primary-400">Singles</span>
                      <span className={cn(
                        'font-bold',
                        singlesRecord.profit >= 0 ? 'text-accent-green' : 'text-accent-red'
                      )}>
                        {singlesRecord.profit >= 0 ? '+' : ''}${singlesRecord.profit.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-accent-green">{singlesRecord.wins}W</span>
                      <span className="text-accent-red">{singlesRecord.losses}L</span>
                      <span className="text-gray-400">
                        {singlesRecord.wins + singlesRecord.losses > 0
                          ? `${((singlesRecord.wins / (singlesRecord.wins + singlesRecord.losses)) * 100).toFixed(1)}%`
                          : '0%'
                        } win rate
                      </span>
                    </div>
                  </div>
                  {/* Parlays */}
                  <div className="p-3 rounded-lg bg-accent-purple/10 border border-accent-purple/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-accent-purple">Parlays</span>
                      <span className={cn(
                        'font-bold',
                        parlaysRecord.profit >= 0 ? 'text-accent-green' : 'text-accent-red'
                      )}>
                        {parlaysRecord.profit >= 0 ? '+' : ''}${parlaysRecord.profit.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-accent-green">{parlaysRecord.wins}W</span>
                      <span className="text-accent-red">{parlaysRecord.losses}L</span>
                      <span className="text-gray-400">
                        {parlaysRecord.wins + parlaysRecord.losses > 0
                          ? `${((parlaysRecord.wins / (parlaysRecord.wins + parlaysRecord.losses)) * 100).toFixed(1)}%`
                          : '0%'
                        } win rate
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Per-Sport Breakdown */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 size={18} className="text-accent-amber" />
                  Performance by Sport
                </h3>
                {Object.keys(statsBySport).length > 0 ? (
                  <div className="space-y-3 max-h-[280px] overflow-y-auto">
                    {Object.entries(statsBySport).map(([sport, sportStats]) => {
                      const totalGames = sportStats.wins + sportStats.losses + (sportStats.pushes || 0)
                      const winRate = totalGames > 0 ? (sportStats.wins / totalGames) * 100 : 0
                      return (
                        <div key={sport} className="p-3 rounded-lg bg-dark-bg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-sm">
                              {sport.split('_').slice(1).join(' ').toUpperCase() || sport}
                            </span>
                            <span className={cn(
                              'font-bold text-sm',
                              sportStats.profit >= 0 ? 'text-accent-green' : 'text-accent-red'
                            )}>
                              {sportStats.profit >= 0 ? '+' : ''}${sportStats.profit.toFixed(2)}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 text-xs">
                            <span className="text-accent-green">{sportStats.wins}W</span>
                            <span className="text-accent-red">{sportStats.losses}L</span>
                            {sportStats.pushes && sportStats.pushes > 0 && (
                              <span className="text-gray-400">{sportStats.pushes}P</span>
                            )}
                            <span className="text-gray-500">|</span>
                            <span className="text-gray-400">{winRate.toFixed(1)}% win rate</span>
                            {sportStats.wagers && (
                              <span className="text-gray-500">{sportStats.wagers} wagers</span>
                            )}
                          </div>
                          {/* Mini progress bar */}
                          <div className="mt-2 h-1 rounded bg-dark-border overflow-hidden">
                            <div
                              className="h-full bg-accent-green"
                              style={{ width: `${winRate}%` }}
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <BarChart3 size={32} className="mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No sport-specific data yet</p>
                    <p className="text-xs text-gray-500 mt-1">Place wagers to see per-sport performance</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Recent Wagers */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <History size={18} className="text-primary-400" />
                  Recent Wagers
                </h3>
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
                        <th className="pb-2 px-2">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {wagers.slice(0, 5).map((wager: WagerRowProps['wager']) => (
                        <WagerRow
                          key={wager.id}
                          wager={wager}
                          onExpand={toggleWagerExpand}
                          isExpanded={expandedWagers.has(wager.id)}
                        />
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
              <div className="grid grid-cols-4 gap-3 mb-4">
                <div className="text-center p-2 rounded-lg bg-accent-green/10">
                  <p className="text-xl font-bold text-accent-green">{stats.wins || 0}</p>
                  <p className="text-xs text-gray-400">Wins</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-accent-red/10">
                  <p className="text-xl font-bold text-accent-red">{stats.losses || 0}</p>
                  <p className="text-xs text-gray-400">Losses</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-accent-purple/10">
                  <p className="text-xl font-bold text-accent-purple">{stats.pushes || 0}</p>
                  <p className="text-xs text-gray-400">Pushes</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-accent-amber/10">
                  <p className="text-xl font-bold text-accent-amber">{stats.pending || 0}</p>
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
                  <span className="text-gray-400">Total Staked</span>
                  <span className="font-medium">${(stats.total_stake || 0).toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Current Streak</span>
                  <span className={cn('font-medium', (stats.current_streak || 0) >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                    {Math.abs(stats.current_streak || 0)} {(stats.current_streak || 0) >= 0 ? 'W' : 'L'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Best Streak</span>
                  <span className="font-medium text-accent-green">{stats.longest_win_streak || 0}W</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Last Updated</span>
                  <span className="text-xs text-gray-500">
                    {stats.last_updated ? new Date(stats.last_updated).toLocaleString() : '-'}
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

      {/* Session 746: Watching Tab */}
      {activeTab === 'watching' && (
        <div className="space-y-6">
          {/* Header with filters */}
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400">Filter:</span>
              {[
                { value: 'all', label: 'All', color: 'bg-primary-600' },
                { value: 'pending', label: 'Pending', color: 'bg-cyan-500' },
                { value: 'verified', label: 'Verified', color: 'bg-accent-green' },
              ].map(({ value, label, color }) => (
                <button
                  key={value}
                  onClick={() => setWatchingFilter(value as typeof watchingFilter)}
                  className={cn(
                    'px-3 py-1.5 rounded text-xs font-medium transition-colors',
                    watchingFilter === value
                      ? `${color} text-white`
                      : 'bg-dark-card text-gray-400 hover:text-white'
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
            <button
              className="btn btn-secondary text-sm flex items-center gap-2"
              onClick={() => refetchWatched()}
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              label="Watching"
              value={watchedItems.filter(i => i.verification_outcome === 'pending' || !i.verification_outcome).length}
              icon={Eye}
              color="bg-cyan-500"
            />
            <StatCard
              label="Would Have Won"
              value={watchedItems.filter(i => i.verification_outcome === 'won').length}
              icon={CheckCircle}
              color="bg-accent-green"
            />
            <StatCard
              label="Would Have Lost"
              value={watchedItems.filter(i => i.verification_outcome === 'lost').length}
              icon={XCircle}
              color="bg-accent-red"
            />
            <StatCard
              label="Paper P/L"
              value={`$${watchedItems
                .filter(i => i.verification_profit != null)
                .reduce((acc, i) => acc + (i.verification_profit || 0), 0)
                .toFixed(2)}`}
              icon={DollarSign}
              color="bg-accent-amber"
            />
          </div>

          {/* Watched Items */}
          {watchedLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : watchedItems.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {watchedItems.map((item) => (
                <WatchedItemCard
                  key={item.id}
                  item={item}
                  onVerify={(itemId, outcome, profit, notes) =>
                    verifyMutation.mutate({ itemId, outcome, profit, notes })
                  }
                  isVerifying={verifyMutation.isPending}
                />
              ))}
            </div>
          ) : (
            <div className="card p-12 text-center">
              <Eye size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2">No Watched Opportunities</h3>
              <p className="text-gray-400">
                Use "Watch & Verify" on the Human page to track arbitrage opportunities without betting.
                <br />
                After games complete, come back here to record outcomes and track paper trading performance.
              </p>
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

          {/* Session 745: Line Movement Section */}
          <div className="card mt-6">
            <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <TrendingUp className="text-accent-cyan" size={20} />
              Line Movement
            </h3>
            {lineMovementLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="animate-spin" size={20} />
              </div>
            ) : lineMovement.length > 0 ? (
              <div className="space-y-3">
                {lineMovement.slice(0, 8).map((game: { game_id: string; home_team: string; away_team: string; sport_key: string; open_spread: number | null; current_spread: number | null; spread_movement: number; open_total: number | null; current_total: number | null; total_movement: number; has_significant_movement: boolean }) => (
                  <div
                    key={game.game_id}
                    className={cn(
                      'p-3 rounded-lg border transition-colors',
                      game.has_significant_movement ? 'border-accent-amber/50 bg-accent-amber/5' : 'border-dark-border'
                    )}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{game.away_team} @ {game.home_team}</span>
                        {game.has_significant_movement && (
                          <span className="px-1.5 py-0.5 text-xs rounded bg-accent-amber/20 text-accent-amber">
                            Sharp Move
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">{game.sport_key?.split('_')[1]?.toUpperCase()}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Spread: </span>
                        <span className="text-gray-300">
                          {game.open_spread !== null ? game.open_spread : 'N/A'} → {game.current_spread !== null ? game.current_spread : 'N/A'}
                        </span>
                        {game.spread_movement !== 0 && (
                          <span className={cn('ml-2', game.spread_movement > 0 ? 'text-accent-green' : 'text-accent-red')}>
                            ({game.spread_movement > 0 ? '+' : ''}{game.spread_movement.toFixed(1)})
                          </span>
                        )}
                      </div>
                      <div>
                        <span className="text-gray-400">Total: </span>
                        <span className="text-gray-300">
                          {game.open_total !== null ? game.open_total : 'N/A'} → {game.current_total !== null ? game.current_total : 'N/A'}
                        </span>
                        {game.total_movement !== 0 && (
                          <span className={cn('ml-2', game.total_movement > 0 ? 'text-accent-green' : 'text-accent-red')}>
                            ({game.total_movement > 0 ? '+' : ''}{game.total_movement.toFixed(1)})
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-400">
                <TrendingUp className="mx-auto mb-2 opacity-50" size={24} />
                <p className="text-sm">No line movement data</p>
                <p className="text-xs text-gray-500 mt-1">Line movement will appear when odds change</p>
              </div>
            )}
          </div>
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
          {/* Wager Stats Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
                  <Trophy size={20} className="text-primary-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{wagers.length}</p>
                  <p className="text-xs text-gray-400">Total Wagers</p>
                </div>
              </div>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-accent-amber/20 flex items-center justify-center">
                  <Clock size={20} className="text-accent-amber" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{wagers.filter((w: WagerRowProps['wager']) => w.status === 'pending').length}</p>
                  <p className="text-xs text-gray-400">Pending</p>
                </div>
              </div>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-accent-green/20 flex items-center justify-center">
                  <CheckCircle size={20} className="text-accent-green" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{wagers.filter((w: WagerRowProps['wager']) => w.settled_at).length}</p>
                  <p className="text-xs text-gray-400">Settled</p>
                </div>
              </div>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                  <Layers size={20} className="text-accent-purple" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{wagers.filter((w: WagerRowProps['wager']) => w.type === 'parlay').length}</p>
                  <p className="text-xs text-gray-400">Parlays</p>
                </div>
              </div>
            </div>
          </div>

          {/* Help text */}
          <p className="text-xs text-gray-500">
            <ChevronDown size={12} className="inline mr-1" />
            Click on a wager row to expand and see leg details
          </p>

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
                      <th className="py-3 px-4">Pick/Event</th>
                      <th className="py-3 px-4">Odds</th>
                      <th className="py-3 px-4">Stake</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">P/L</th>
                      <th className="py-3 px-4">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {wagers.map((wager: WagerRowProps['wager']) => (
                      <WagerRow
                        key={wager.id}
                        wager={wager}
                        onExpand={toggleWagerExpand}
                        isExpanded={expandedWagers.has(wager.id)}
                      />
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
