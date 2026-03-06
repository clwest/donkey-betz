import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { bettingApi, humanApi, sportsHubApi } from '@/lib/api'
import {
  TrendingUp, TrendingDown, DollarSign, Target, Zap, AlertTriangle,
  RefreshCw, Loader2, Trophy, Activity, PieChart, BarChart3,
  Clock, CheckCircle, Flame, Search, Eye, XCircle, CircleDot,
  Award, Layers, ChevronDown, ChevronUp, History, Crosshair,
  Star, Swords, Brain, Newspaper, HeartPulse, Calendar, Plus,
  Calculator, ChevronRight, X, Info, FileText
} from 'lucide-react'
import { cn } from '@/lib/cn'

type BettingTab = 'hub' | 'games' | 'top_plays' | 'sharp' | 'arbitrage' | 'markets' | 'odds' | 'bankroll' | 'wagers' | 'watching' | 'records'

const tabs = [
  { id: 'hub' as BettingTab, label: 'Hub', icon: Newspaper },
  { id: 'games' as BettingTab, label: "Today's Games", icon: Swords },
  { id: 'top_plays' as BettingTab, label: 'Top Plays', icon: Star },
  { id: 'sharp' as BettingTab, label: 'Sharp Action', icon: Crosshair },
  { id: 'arbitrage' as BettingTab, label: 'Arbitrage', icon: Flame },
  { id: 'watching' as BettingTab, label: 'Watching', icon: Eye },
  { id: 'odds' as BettingTab, label: 'Live Odds', icon: Activity },
  { id: 'wagers' as BettingTab, label: 'My Wagers', icon: Trophy },
  { id: 'records' as BettingTab, label: 'Records', icon: BarChart3 },
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
              {profitLoss >= 0 ? '+' : ''}${(profitLoss ?? 0).toFixed(2)}
            </span>
          ) : wager.potential_payout ? (
            <span className="text-gray-400 text-sm">→ ${(wager.potential_payout ?? 0).toFixed(2)}</span>
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

function ArbitrageCard({ arb, totalStake }: ArbitrageCardProps & { totalStake?: number }) {
  const profitPercent = arb.profit_percent ?? 0
  const isHot = profitPercent >= 1.5
  const bookmakers = arb.bookmakers ?? []
  const stake = totalStake || 100

  // Calculate optimal stakes for each leg
  const decimalOdds = bookmakers.map(b => {
    const o = b.odds ?? 0
    return o > 0 ? 1 + o / 100 : 1 + 100 / Math.abs(o || 1)
  })
  const inverseSum = decimalOdds.reduce((acc, d) => acc + 1 / d, 0)
  const legStakes = decimalOdds.map(d => stake / (d * inverseSum))
  const guaranteedReturn = legStakes.length > 0 ? legStakes[0] * decimalOdds[0] : 0
  const guaranteedProfit = guaranteedReturn - stake

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
            +{(profitPercent ?? 0).toFixed(2)}%
          </p>
          <p className="text-xs text-gray-500">guaranteed profit</p>
        </div>
      </div>
      <div className="space-y-2">
        {bookmakers.map((book, i) => (
          <div key={i} className="flex items-center justify-between p-2 rounded bg-dark-bg">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{book.name || 'Unknown'}</span>
              <span className="text-gray-400">→</span>
              <span className="text-sm text-primary-400">{book.pick || '-'}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-accent-green text-sm">
                {(book.odds ?? 0) > 0 ? '+' : ''}{book.odds ?? 0}
              </span>
              {legStakes[i] > 0 && (
                <span className="text-xs font-mono text-white bg-primary-600/30 px-2 py-0.5 rounded">
                  ${legStakes[i].toFixed(2)}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
      {/* Profit summary */}
      {guaranteedProfit > 0 && (
        <div className="mt-3 p-2 rounded-lg bg-accent-green/5 border border-accent-green/20 flex items-center justify-between">
          <span className="text-xs text-gray-400">
            <Calculator size={12} className="inline mr-1" />
            With ${stake} total stake
          </span>
          <span className="text-sm font-bold text-accent-green">
            Profit: +${guaranteedProfit.toFixed(2)}
          </span>
        </div>
      )}
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
              <p className="text-xl font-bold text-cyan-400">+{(profitPercent ?? 0).toFixed(2)}%</p>
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
              {item.verification_profit >= 0 ? '+' : ''}${(item.verification_profit ?? 0).toFixed(2)}
            </span>
          )}
        </div>
      )}
    </div>
  )
}

// Pick Details Drawer — shows full prediction provenance
interface PickDetail {
  id: string
  sport_type: string
  predicted_winner: string
  confidence: number
  was_correct: boolean | null
  game_date: string
  matchup: string
  odds: number | null
  closing_odds: number | null
  home_team: string
  away_team: string
  home_score: number | null
  away_score: number | null
  game_status: string
  home_win_probability: number | null
  away_win_probability: number | null
  predicted_spread: number | null
  predicted_home_score: number | null
  predicted_away_score: number | null
  model_used: string
  bookmaker_count: number
  ai_reasoning: string
  key_factors: string[]
  created_at: string
  evaluated_at?: string
}

function PickDetailsDrawer({ pick, onClose, onLogWager }: {
  pick: PickDetail
  onClose: () => void
  onLogWager: (pick: PickDetail) => void
}) {
  const [showExplain, setShowExplain] = useState(false)

  const roiUnit = pick.was_correct !== null && pick.odds != null
    ? pick.was_correct
      ? (pick.odds < 0 ? 100 / Math.abs(pick.odds) : pick.odds / 100)
      : -1
    : null

  const openIp = pick.odds != null
    ? (pick.odds < 0 ? Math.abs(pick.odds) / (Math.abs(pick.odds) + 100) : 100 / (pick.odds + 100))
    : null
  const closeIp = pick.closing_odds != null
    ? (pick.closing_odds < 0 ? Math.abs(pick.closing_odds) / (Math.abs(pick.closing_odds) + 100) : 100 / (pick.closing_odds + 100))
    : null
  // CLV is only meaningful if closing_odds differs from odds_at_prediction
  const hasRealClosing = pick.closing_odds != null && pick.odds != null && pick.closing_odds !== pick.odds
  const clv = openIp != null && closeIp != null && hasRealClosing ? ((closeIp - openIp) * 100) : null

  const timeAgo = pick.created_at ? (() => {
    const mins = Math.round((Date.now() - new Date(pick.created_at).getTime()) / 60000)
    if (mins < 60) return `${mins}m ago`
    const hrs = Math.round(mins / 60)
    if (hrs < 24) return `${hrs}h ago`
    return `${Math.round(hrs / 24)}d ago`
  })() : null

  const isFinal = pick.home_score != null && pick.away_score != null
  const statusLabel = pick.was_correct === true ? 'W' : pick.was_correct === false ? 'L' : isFinal ? 'Final' : 'Pending'
  const statusColor = pick.was_correct === true ? 'bg-accent-green/20 text-accent-green' :
    pick.was_correct === false ? 'bg-accent-red/20 text-accent-red' : 'bg-accent-amber/20 text-accent-amber'

  return (
    <div className="fixed inset-0 z-50 flex justify-end" onClick={onClose}>
      <div className="absolute inset-0 bg-black/50" />
      <div
        className="relative w-full max-w-md bg-dark-card border-l border-dark-border h-full overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-dark-card border-b border-dark-border p-4 flex items-center justify-between z-10">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Info size={18} className="text-primary-400" />
            Pick Details
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-dark-bg rounded">
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* ═══ LAYER 1: PROOF STRIP (always visible, above the fold) ═══ */}
          <div className="card p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold tracking-wider text-gray-500 uppercase">Proof</span>
              <span className="text-[10px] text-gray-600" title="Odds captured at prediction time. Grading is deterministic from final scores. CLV uses closing line.">
                Market + Time + Result
              </span>
            </div>

            {/* Bet Definition */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400 uppercase font-medium">
                  {pick.sport_type}
                </span>
                <span className="text-xs text-gray-500">ML</span>
                <span className={cn('text-xs px-2 py-0.5 rounded font-bold', statusColor)}>
                  {statusLabel}
                </span>
              </div>
              <h4 className="text-base font-medium">{pick.matchup || `${pick.away_team} @ ${pick.home_team}`}</h4>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm font-semibold text-accent-purple">{pick.predicted_winner}</span>
                <span className="text-sm text-accent-purple">{pick.confidence}%</span>
              </div>
            </div>

            {/* Price at recommendation */}
            <div className="flex items-center gap-4 text-sm">
              <div>
                <span className="text-gray-500">Odds: </span>
                {pick.odds != null ? (
                  <span className={cn('font-mono font-medium', pick.odds > 0 ? 'text-accent-green' : 'text-white')}>
                    {pick.odds > 0 ? '+' : ''}{pick.odds}
                  </span>
                ) : <span className="text-gray-600 italic">not captured</span>}
              </div>
              {timeAgo && (
                <div>
                  <span className="text-gray-500">Predicted: </span>
                  <span className="text-gray-300">{timeAgo}</span>
                </div>
              )}
            </div>

            {/* Settlement anchor */}
            {isFinal && (
              <div className="flex items-center gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Final: </span>
                  <span className="font-bold">{pick.away_score} - {pick.home_score}</span>
                </div>
                {pick.was_correct === true && <span className="text-accent-green font-bold">Correct</span>}
                {pick.was_correct === false && <span className="text-accent-red font-bold">Incorrect</span>}
              </div>
            )}

            {/* CLV headline */}
            <div className="flex items-center gap-4 text-sm">
              {clv != null ? (
                <div>
                  <span className="text-gray-500">CLV: </span>
                  <span className={cn('font-mono font-medium', clv > 0 ? 'text-accent-green' : clv < 0 ? 'text-accent-red' : 'text-gray-400')}>
                    {clv > 0 ? '+' : ''}{clv.toFixed(2)}%
                  </span>
                </div>
              ) : pick.closing_odds != null ? (
                <div>
                  <span className="text-gray-500">Closing: </span>
                  <span className={cn('font-mono', pick.closing_odds > 0 ? 'text-accent-green' : 'text-white')}>
                    {pick.closing_odds > 0 ? '+' : ''}{pick.closing_odds}
                  </span>
                </div>
              ) : (
                <span className="text-gray-600 text-xs italic">CLV: pending (needs closing line)</span>
              )}
            </div>
          </div>

          {/* ═══ LAYER 2: CONTEXT (one scroll) ═══ */}
          <div className="card p-4">
            <h5 className="text-[10px] font-semibold tracking-wider text-gray-500 uppercase mb-3">Context</h5>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Bookmakers</span>
                <span className="font-medium">{pick.bookmaker_count || 'N/A'}</span>
              </div>
              {(pick.home_win_probability != null || pick.away_win_probability != null) && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Win Probability</span>
                  <span className="text-gray-300">
                    {pick.away_team?.split(' ').pop()} {pick.away_win_probability}% / {pick.home_team?.split(' ').pop()} {pick.home_win_probability}%
                  </span>
                </div>
              )}
              {roiUnit != null && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">ROI (1u flat)</span>
                  <span className={cn('font-mono font-medium', roiUnit >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                    {roiUnit >= 0 ? '+' : ''}{roiUnit.toFixed(2)}u
                  </span>
                </div>
              )}
              {pick.closing_odds != null && clv != null && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Closing Odds</span>
                  <span className={cn('font-mono', pick.closing_odds > 0 ? 'text-accent-green' : 'text-gray-300')}>
                    {pick.closing_odds > 0 ? '+' : ''}{pick.closing_odds}
                  </span>
                </div>
              )}
              {pick.evaluated_at && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Evaluated at</span>
                  <span className="text-gray-300">{new Date(pick.evaluated_at).toLocaleString()}</span>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Model</span>
                <span className="font-mono text-gray-300 text-xs">{pick.model_used || 'odds_consensus'}</span>
              </div>
            </div>
          </div>

          {/* ═══ LAYER 3: EXPLAINABILITY (expandable) ═══ */}
          {(pick.ai_reasoning || (pick.key_factors && pick.key_factors.length > 0) || pick.predicted_spread != null) && (
            <div className="card">
              <button
                onClick={() => setShowExplain(!showExplain)}
                className="w-full p-4 flex items-center justify-between text-sm font-medium text-gray-400 hover:text-white transition-colors"
              >
                <span className="flex items-center gap-2">
                  <Brain size={14} />
                  Why this pick?
                </span>
                {showExplain ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
              {showExplain && (
                <div className="px-4 pb-4 space-y-3">
                  {pick.ai_reasoning && (
                    <div>
                      <h6 className="text-xs font-semibold text-gray-500 mb-1">AI Reasoning</h6>
                      <p className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">{pick.ai_reasoning}</p>
                    </div>
                  )}
                  {pick.key_factors && pick.key_factors.length > 0 && (
                    <div>
                      <h6 className="text-xs font-semibold text-gray-500 mb-1">Key Factors</h6>
                      <ul className="space-y-1">
                        {pick.key_factors.map((factor, i) => (
                          <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                            <span className="text-primary-400 mt-0.5">&#x2022;</span>
                            <span>{typeof factor === 'string' ? factor : JSON.stringify(factor)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {pick.predicted_spread != null && (
                    <div className="text-sm text-gray-400">
                      Predicted spread: {pick.predicted_spread > 0 ? '+' : ''}{pick.predicted_spread}
                      {pick.predicted_home_score != null && pick.predicted_away_score != null && (
                        <span> | Score: {pick.predicted_away_score} - {pick.predicted_home_score}</span>
                      )}
                    </div>
                  )}
                  <div className="text-[10px] text-gray-600 pt-2 border-t border-dark-border">
                    Sources: odds via TheOddsSpider, scores via update_game_scores, eval via evaluate_completed_predictions
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Log as Wager button */}
          {pick.was_correct === null && (
            <button
              onClick={() => onLogWager(pick)}
              className="btn btn-primary w-full flex items-center justify-center gap-2"
            >
              <FileText size={16} />
              Log as Wager
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function BettingPage() {
  const [activeTab, setActiveTab] = useState<BettingTab>('hub')
  const [sportFilter, setSportFilter] = useState('all')
  const [watchingFilter, setWatchingFilter] = useState<'all' | 'pending' | 'verified'>('all')
  const [expandedWagers, setExpandedWagers] = useState<Set<string>>(new Set())
  const [expandedBookmakers, setExpandedBookmakers] = useState<Set<string>>(new Set())
  const [showWagerForm, setShowWagerForm] = useState(false)
  const [wagerForm, setWagerForm] = useState({ matchup: '', pick: '', odds: '-110', stake: '10', sport: '', bookmaker: '', market_type: 'h2h' })
  const [arbStake, setArbStake] = useState('100')
  const [selectedPick, setSelectedPick] = useState<PickDetail | null>(null)
  const [modelFilter, setModelFilter] = useState('')
  const [recordsView, setRecordsView] = useState<'ai' | 'user'>('ai')
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

  const [pickedId, setPickedId] = useState<string | null>(null)
  const quickPickMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => bettingApi.quickPick(data),
    onSuccess: (_resp, vars) => {
      queryClient.invalidateQueries({ queryKey: ['betting-stats'] })
      queryClient.invalidateQueries({ queryKey: ['betting-wagers'] })
      const id = String(vars.event_id || vars.pick || '')
      setPickedId(id)
      setTimeout(() => setPickedId(null), 2000)
    },
  })

  const placeBetMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => bettingApi.placeBet(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['betting-wagers'] })
      queryClient.invalidateQueries({ queryKey: ['betting-stats'] })
      queryClient.invalidateQueries({ queryKey: ['betting-bankroll'] })
      setShowWagerForm(false)
      setWagerForm({ matchup: '', pick: '', odds: '-110', stake: '10', sport: '', bookmaker: '', market_type: 'h2h' })
    },
  })

  // Log as Wager — prefill from pick details
  const handleLogWager = (pick: PickDetail) => {
    setWagerForm({
      matchup: pick.matchup || `${pick.away_team} @ ${pick.home_team}`,
      pick: pick.predicted_winner,
      odds: pick.odds != null ? String(pick.odds) : '-110',
      stake: '10',
      sport: pick.sport_type,
      bookmaker: '',
      market_type: 'h2h',
    })
    setSelectedPick(null)
    setShowWagerForm(true)
    setActiveTab('wagers')
  }

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

  // Session 995B: Today's games with predictions + scores
  const { data: gamesData, isLoading: gamesLoading, refetch: refetchGames } = useQuery({
    queryKey: ['betting-todays-games', sportFilter],
    queryFn: () => bettingApi.todaysGames(sportFilter !== 'all' ? sportFilter : undefined),
    enabled: activeTab === 'games',
    refetchInterval: 60000,
  })

  // Session 995B: Betting brief from coordinator
  const { data: briefData, isLoading: briefLoading, refetch: refetchBrief } = useQuery({
    queryKey: ['betting-brief'],
    queryFn: () => bettingApi.bettingBrief(),
    enabled: activeTab === 'top_plays',
  })

  // Session 995B: Sharp action signals
  const { data: sharpData, isLoading: sharpLoading, refetch: refetchSharp } = useQuery({
    queryKey: ['betting-sharp-action', sportFilter],
    queryFn: () => bettingApi.sharpAction(sportFilter !== 'all' ? sportFilter : undefined),
    enabled: activeTab === 'sharp',
  })

  // Session 998B: Hub feed queries
  const { data: hubNewsData, isLoading: hubNewsLoading } = useQuery({
    queryKey: ['hub-sports-news'],
    queryFn: () => sportsHubApi.getFeed('sports_news', 8),
    enabled: activeTab === 'hub',
  })
  const { data: hubInjuryData, isLoading: hubInjuryLoading } = useQuery({
    queryKey: ['hub-sports-injuries'],
    queryFn: () => sportsHubApi.getFeed('sports_injuries', 10),
    enabled: activeTab === 'hub',
  })

  // AI Track Record
  const { data: trackRecordData, isLoading: trackRecordLoading } = useQuery({
    queryKey: ['betting-track-record', modelFilter],
    queryFn: () => bettingApi.trackRecord(modelFilter ? { model: modelFilter } : undefined),
    enabled: activeTab === 'records' && recordsView === 'ai',
  })

  // Pipeline freshness
  const { data: pipelineData } = useQuery({
    queryKey: ['betting-pipeline-status'],
    queryFn: () => bettingApi.pipelineStatus(),
    enabled: activeTab === 'records' || activeTab === 'games',
    refetchInterval: 60000,
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

  // Session 995B: New intelligence data
  const todaysGames = gamesData?.data?.games || []
  const gameSports = gamesData?.data?.sports || []
  const briefResult = briefData?.data?.brief || {}
  const topPlays = briefResult.top_plays || []
  const sharpSignals = sharpData?.data?.signals || []

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

      {/* Session 998B: Hub Tab — Magazine-style sports betting landing */}
      {activeTab === 'hub' && (
        <div className="space-y-6">
          {/* Quick Stats Strip — reuse existing stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Win Rate" value={`${(stats.win_rate || 0).toFixed(1)}%`} icon={Target} color="bg-accent-green" />
            <StatCard label="ROI" value={`${(stats.roi || 0) >= 0 ? '+' : ''}${(stats.roi || 0).toFixed(1)}%`} icon={TrendingUp} color="bg-primary-600" />
            <StatCard label="Total P/L" value={`$${(stats.total_profit_loss || 0).toFixed(2)}`} icon={DollarSign} color="bg-accent-amber" />
            <StatCard label="Pending" value={stats.pending || 0} icon={Clock} color="bg-accent-purple" />
          </div>

          {/* Two-column layout: News + Sidebar */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* News Feed — 2/3 width */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Newspaper size={18} className="text-primary-400" />
                Sports News
              </h3>
              {hubNewsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 size={24} className="animate-spin text-primary-400" />
                </div>
              ) : (hubNewsData?.items || []).length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(hubNewsData?.items || []).map((item: any, i: number) => {
                    const title = item.title || item.spider_name || 'Sports Update'
                    const summary = (item.description || '').replace(/<[^>]*>/g, '').slice(0, 140)
                    const link = item.source_url || '#'
                    const timeAgo = item.created_at ? new Date(item.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''

                    return (
                      <a
                        key={`${item.id}-${i}`}
                        href={link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={cn(
                          'card p-4 hover:border-primary-500 transition-colors block',
                          i === 0 && 'md:col-span-2 border-l-4 border-l-primary-500'
                        )}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                            {item.spider_name || 'news'}
                          </span>
                          <span className="text-xs text-gray-500">{timeAgo}</span>
                        </div>
                        <h4 className={cn('font-medium mb-1', i === 0 ? 'text-lg' : 'text-sm')}>
                          {title}
                        </h4>
                        {summary && (
                          <p className="text-sm text-gray-400 line-clamp-2">{summary}</p>
                        )}
                      </a>
                    )
                  })}
                </div>
              ) : (
                <div className="card p-8 text-center">
                  <Newspaper size={32} className="mx-auto mb-2 text-gray-500" />
                  <p className="text-sm text-gray-400">No sports news yet</p>
                  <p className="text-xs text-gray-500 mt-1">News will appear after the next spider run</p>
                </div>
              )}
            </div>

            {/* Sidebar — 1/3 width */}
            <div className="space-y-6">
              {/* Injury Report */}
              <div className="card">
                <h3 className="text-base font-semibold flex items-center gap-2 mb-3">
                  <HeartPulse size={16} className="text-accent-red" />
                  Injury Report
                </h3>
                {hubInjuryLoading ? (
                  <div className="flex items-center justify-center py-4">
                    <Loader2 size={20} className="animate-spin text-primary-400" />
                  </div>
                ) : (hubInjuryData?.items || []).length > 0 ? (
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {(hubInjuryData?.items || []).map((item: any, i: number) => {
                      const title = item.title || 'Injury Update'
                      const timeAgo = item.created_at ? new Date(item.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''

                      return (
                        <div key={`${item.id}-${i}`} className="p-2 rounded bg-dark-bg text-sm">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-gray-200 line-clamp-1">{title}</span>
                            <span className="text-xs text-gray-500 flex-shrink-0 ml-2">{timeAgo}</span>
                          </div>
                          <span className="text-xs text-gray-500">{item.spider_name}</span>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <HeartPulse size={24} className="mx-auto mb-2 text-gray-500 opacity-50" />
                    <p className="text-xs text-gray-400">No injury data yet</p>
                  </div>
                )}
              </div>

              {/* Quick Links to other tabs */}
              <div className="card">
                <h3 className="text-base font-semibold mb-3">Quick Access</h3>
                <div className="space-y-2">
                  {[
                    { tab: 'top_plays' as BettingTab, label: 'Top Plays', icon: Star, color: 'text-accent-amber' },
                    { tab: 'games' as BettingTab, label: "Today's Games", icon: Swords, color: 'text-primary-400' },
                    { tab: 'sharp' as BettingTab, label: 'Sharp Action', icon: Crosshair, color: 'text-accent-red' },
                    { tab: 'arbitrage' as BettingTab, label: 'Arbitrage', icon: Flame, color: 'text-accent-amber' },
                  ].map(({ tab, label, icon: Icon, color }) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className="w-full flex items-center gap-3 p-2 rounded hover:bg-dark-bg transition-colors text-sm text-left"
                    >
                      <Icon size={16} className={color} />
                      <span>{label}</span>
                      <ChevronDown size={14} className="ml-auto text-gray-500 -rotate-90" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Session 995B: Today's Games Tab */}
      {activeTab === 'games' && (
        <div className="space-y-6">
          {/* Sport Filter + Refresh */}
          <div className="flex items-center gap-4">
            <select
              value={sportFilter}
              onChange={(e) => setSportFilter(e.target.value)}
              className="bg-dark-card border border-dark-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
            >
              <option value="all">All Sports</option>
              {gameSports.map((sk: string) => (
                <option key={sk} value={sk}>
                  {sk.replace('americanfootball_', 'NFL: ').replace('basketball_', 'NBA: ').replace('icehockey_', 'NHL: ').replace('baseball_', 'MLB: ').replace('soccer_', 'Soccer: ').replace('_', ' ')}
                </option>
              ))}
            </select>
            <button className="btn btn-primary flex items-center gap-2" onClick={() => refetchGames()}>
              <RefreshCw size={16} />
              Refresh
            </button>
            <span className="text-sm text-gray-400">{todaysGames.length} games</span>
            {/* Pipeline freshness */}
            {(() => {
              const p = pipelineData?.data?.pipeline
              if (!p) return null
              return (
                <span className="ml-auto text-xs text-gray-500" title={p.scores_updated?.timestamp || ''}>
                  Scores: {p.scores_updated?.ago || '—'} · Odds: {p.odds_updated?.ago || '—'}
                </span>
              )
            })()}
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Live" value={todaysGames.filter((g: any) => {
              const gt = g.commence_time ? new Date(g.commence_time) : null
              return gt && gt <= new Date() && !g.completed
            }).length} icon={Activity} color="bg-accent-red" />
            <StatCard label="AI Picks" value={todaysGames.filter((g: any) => g.predicted_winner).length} icon={Brain} color="bg-accent-purple" />
            <StatCard label="Completed" value={todaysGames.filter((g: any) => g.completed).length} icon={CheckCircle} color="bg-accent-green" />
            <StatCard label="Upcoming" value={todaysGames.filter((g: any) => {
              const gt = g.commence_time ? new Date(g.commence_time) : null
              return !g.completed && (!gt || gt > new Date())
            }).length} icon={Clock} color="bg-accent-amber" />
          </div>

          {/* Games List */}
          {gamesLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : todaysGames.length > 0 ? (
            <div className="space-y-3">
              {todaysGames.map((game: any, i: number) => {
                const hasScore = game.home_score != null && game.away_score != null
                const hasPrediction = !!game.predicted_winner
                const gameTime = game.commence_time ? new Date(game.commence_time) : null
                const isLive = gameTime && gameTime <= new Date() && !game.completed

                return (
                  <div key={game.event_id || i} className={cn(
                    'card p-4 border-l-4',
                    game.completed ? 'border-l-gray-500' :
                    isLive ? 'border-l-accent-red' :
                    hasPrediction ? 'border-l-accent-purple' : 'border-l-primary-500'
                  )}>
                    {/* Header: sport + time + status */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                          {(game.sport_name || game.sport_key || '').replace(/_/g, ' ')}
                        </span>
                        {isLive && (
                          <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-accent-red/20 text-accent-red animate-pulse">
                            <Activity size={10} /> LIVE
                          </span>
                        )}
                        {isLive && game.status_detail && (
                          <span className="text-xs font-medium text-accent-red">
                            {game.status_detail}
                          </span>
                        )}
                        {isLive && !game.status_detail && game.period > 0 && (
                          <span className="text-xs font-medium text-accent-red">
                            {game.period && game.clock ? `P${game.period} ${game.clock}` : `Period ${game.period}`}
                          </span>
                        )}
                        {game.completed && (
                          <span className="text-xs px-2 py-0.5 rounded bg-gray-500/20 text-gray-400">FINAL</span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {gameTime ? gameTime.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}
                      </span>
                    </div>

                    {/* Matchup + Odds + Score */}
                    <div className="grid grid-cols-7 gap-2 items-center">
                      {/* Away Team */}
                      <div className="col-span-2">
                        <p className="font-medium">{game.away_team}</p>
                        {game.away_odds && (
                          <div className="flex items-baseline gap-1.5">
                            <span className={cn('text-sm font-mono', game.away_odds > 0 ? 'text-accent-green' : 'text-accent-red')}>
                              {game.away_odds > 0 ? '+' : ''}{game.away_odds}
                            </span>
                            {game.away_implied_prob && (
                              <span className="text-[10px] text-gray-500">{game.away_implied_prob}%</span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Score / VS */}
                      <div className="col-span-3 text-center">
                        {hasScore ? (
                          <div>
                            <span className={cn('text-2xl font-bold', game.away_score > game.home_score ? 'text-accent-green' : 'text-gray-300')}>
                              {game.away_score}
                            </span>
                            <span className="text-gray-500 mx-3">-</span>
                            <span className={cn('text-2xl font-bold', game.home_score > game.away_score ? 'text-accent-green' : 'text-gray-300')}>
                              {game.home_score}
                            </span>
                          </div>
                        ) : (
                          <div className="space-y-1">
                            {game.home_spread != null && (
                              <p className="text-xs text-gray-400">
                                Spread: {game.home_spread > 0 ? '+' : ''}{game.home_spread}
                                {game.spread_home_odds && <span className="text-gray-500 ml-1">({game.spread_home_odds > 0 ? '+' : ''}{game.spread_home_odds})</span>}
                              </p>
                            )}
                            {game.total_line && (
                              <p className="text-xs text-gray-400">
                                O/U: {game.total_line}
                                {(game.over_odds || game.under_odds) && (
                                  <span className="text-gray-500 ml-1">
                                    ({game.over_odds ? `o${game.over_odds > 0 ? '+' : ''}${game.over_odds}` : ''}{game.over_odds && game.under_odds ? ' / ' : ''}{game.under_odds ? `u${game.under_odds > 0 ? '+' : ''}${game.under_odds}` : ''})
                                  </span>
                                )}
                              </p>
                            )}
                            {game.draw_odds && (
                              <p className="text-xs text-gray-500">Draw: {game.draw_odds > 0 ? '+' : ''}{game.draw_odds}</p>
                            )}
                            {!game.home_spread && !game.total_line && !game.draw_odds && (
                              <span className="text-gray-500 text-sm">vs</span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Home Team */}
                      <div className="col-span-2 text-right">
                        <p className="font-medium">{game.home_team}</p>
                        {game.home_odds && (
                          <div className="flex items-baseline gap-1.5 justify-end">
                            {game.home_implied_prob && (
                              <span className="text-[10px] text-gray-500">{game.home_implied_prob}%</span>
                            )}
                            <span className={cn('text-sm font-mono', game.home_odds > 0 ? 'text-accent-green' : 'text-accent-red')}>
                              {game.home_odds > 0 ? '+' : ''}{game.home_odds}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Bookmaker info + live score freshness */}
                    {(game.best_bookmaker || (isLive && game.last_updated)) && (
                      <div className="flex items-center justify-between mt-1.5 text-[10px] text-gray-500">
                        {game.best_bookmaker && (
                          <span>via {game.best_bookmaker}{game.bookmaker_count > 1 ? ` + ${game.bookmaker_count - 1} more` : ''}</span>
                        )}
                        {isLive && game.last_updated && (
                          <span>Updated {(() => {
                            const mins = Math.round((Date.now() - new Date(game.last_updated).getTime()) / 60000)
                            return mins < 1 ? 'just now' : `${mins}m ago`
                          })()}</span>
                        )}
                      </div>
                    )}

                    {/* Prediction Banner */}
                    {hasPrediction && (
                      <div className={cn(
                        'mt-3 p-2 rounded-lg flex items-center justify-between',
                        game.prediction_correct === true ? 'bg-accent-green/10 border border-accent-green/20' :
                        game.prediction_correct === false ? 'bg-accent-red/10 border border-accent-red/20' :
                        'bg-accent-purple/10 border border-accent-purple/20'
                      )}>
                        <div className="flex items-center gap-2">
                          <Brain size={14} className={cn(
                            game.prediction_correct === true ? 'text-accent-green' :
                            game.prediction_correct === false ? 'text-accent-red' :
                            'text-accent-purple'
                          )} />
                          <span className="text-sm">
                            AI Pick: <span className={cn('font-medium',
                              game.prediction_correct === true ? 'text-accent-green' :
                              game.prediction_correct === false ? 'text-accent-red' :
                              'text-accent-purple'
                            )}>{game.predicted_winner}</span>
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-accent-purple">{game.confidence}%</span>
                          {game.pick_type === 'value' && (
                            <span className="text-xs px-1.5 py-0.5 rounded bg-accent-amber/20 text-accent-amber font-bold">VALUE</span>
                          )}
                          {game.prediction_correct === true && (
                            <span className="text-xs px-1.5 py-0.5 rounded bg-accent-green/20 text-accent-green font-bold">W</span>
                          )}
                          {game.prediction_correct === false && (
                            <span className="text-xs px-1.5 py-0.5 rounded bg-accent-red/20 text-accent-red font-bold">L</span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Quick Pick buttons */}
                    {!game.completed && (
                      <div className="mt-3 flex items-center gap-2">
                        {[
                          { team: game.away_team, odds: game.away_odds },
                          { team: game.home_team, odds: game.home_odds },
                        ].map(({ team, odds }) => {
                          const pickKey = `${game.event_id}-${team}`
                          const isPicking = quickPickMutation.isPending && pickedId === null
                          const justPicked = pickedId === pickKey
                          return (
                            <button
                              key={team}
                              className={cn(
                                'flex-1 text-xs py-1.5 px-3 rounded-lg font-medium transition-all',
                                justPicked
                                  ? 'bg-accent-green/20 text-accent-green border border-accent-green/30'
                                  : 'bg-dark-bg hover:bg-primary-600/20 text-gray-300 hover:text-primary-400 border border-dark-border hover:border-primary-500/30'
                              )}
                              disabled={isPicking}
                              onClick={() => {
                                setPickedId(pickKey)
                                quickPickMutation.mutate({
                                  event_id: game.event_id || '',
                                  matchup: `${game.away_team} @ ${game.home_team}`,
                                  pick: team,
                                  odds: odds || -110,
                                  stake: 10,
                                  sport: game.sport_key || '',
                                  commence_time: game.commence_time || '',
                                  source: 'todays_games',
                                })
                              }}
                            >
                              {justPicked ? 'Picked!' : isPicking ? '...' : `Pick ${team}`}
                            </button>
                          )
                        })}
                      </div>
                    )}

                    {/* Bookmaker Odds Comparison */}
                    {game.h2h_odds && game.h2h_odds.length > 1 && (
                      <div className="mt-2">
                        <button
                          onClick={() => setExpandedBookmakers(prev => {
                            const next = new Set(prev)
                            next.has(game.event_id) ? next.delete(game.event_id) : next.add(game.event_id)
                            return next
                          })}
                          className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
                        >
                          <ChevronRight size={12} className={cn('transition-transform', expandedBookmakers.has(game.event_id) && 'rotate-90')} />
                          Compare {game.h2h_odds.length} bookmakers
                        </button>
                        {expandedBookmakers.has(game.event_id) && (
                          <div className="mt-2 grid grid-cols-1 gap-1 max-h-48 overflow-y-auto">
                            <div className="grid grid-cols-4 gap-2 text-[10px] text-gray-500 font-medium px-2 py-1">
                              <span>Book</span>
                              <span className="text-right">{game.away_team?.split(' ').pop()}</span>
                              <span className="text-right">{game.home_team?.split(' ').pop()}</span>
                              <span className="text-right">Draw</span>
                            </div>
                            {game.h2h_odds.map((book: any, bi: number) => (
                              <div key={bi} className="grid grid-cols-4 gap-2 text-xs px-2 py-1.5 rounded bg-dark-bg">
                                <span className="font-medium truncate">{book.bookmaker || book.bookmaker_key}</span>
                                <span className={cn('text-right font-mono', book.away_odds > 0 ? 'text-accent-green' : 'text-gray-300')}>
                                  {book.away_odds > 0 ? '+' : ''}{book.away_odds}
                                </span>
                                <span className={cn('text-right font-mono', book.home_odds > 0 ? 'text-accent-green' : 'text-gray-300')}>
                                  {book.home_odds > 0 ? '+' : ''}{book.home_odds}
                                </span>
                                <span className="text-right font-mono text-gray-500">
                                  {book.draw_odds ? (book.draw_odds > 0 ? '+' : '') + book.draw_odds : '—'}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="card p-12 text-center">
              <Swords size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2">No Games Today</h3>
              <p className="text-gray-400">Check back later or try a different sport filter</p>
            </div>
          )}
        </div>
      )}

      {/* Session 995B: Top Plays Tab */}
      {activeTab === 'top_plays' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-400">
              <Brain size={14} className="inline mr-1" />
              AI-ranked plays from 5 agents: GamePredictor, SportsOddsAnalyst, ArbitrageDetector, LineMovementAnalyzer, SharpActionDetector
            </p>
            <button className="btn btn-primary flex items-center gap-2" onClick={() => refetchBrief()}>
              <RefreshCw size={16} />
              Generate Brief
            </button>
          </div>

          {briefLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
              <span className="ml-3 text-gray-400">Running 5 agents... this may take a moment</span>
            </div>
          ) : (
            <>
              {/* Executive Summary */}
              {briefResult.executive_summary && (
                <div className="card p-5 border-l-4 border-l-accent-amber">
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <Star size={18} className="text-accent-amber" />
                    Executive Summary
                  </h3>
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                    {briefResult.executive_summary}
                  </pre>
                  {briefResult.agents_run && (
                    <div className="mt-3 flex items-center gap-2 flex-wrap">
                      <span className="text-xs text-gray-500">Agents:</span>
                      {briefResult.agents_run.map((agent: string) => (
                        <span key={agent} className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                          {agent}
                        </span>
                      ))}
                      {briefResult.generation_time_seconds && (
                        <span className="text-xs text-gray-500 ml-auto">
                          Generated in {briefResult.generation_time_seconds}s
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Top Plays Cards */}
              {topPlays.length > 0 ? (
                <div className="space-y-3">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Trophy size={18} className="text-accent-amber" />
                    Top Plays ({topPlays.length})
                  </h3>
                  {topPlays.map((play: any, i: number) => {
                    const sourceColors: Record<string, string> = {
                      GamePredictor: 'bg-accent-purple/20 text-accent-purple',
                      ArbitrageDetector: 'bg-accent-red/20 text-accent-red',
                      LineMovementAnalyzer: 'bg-accent-cyan/20 text-cyan-400',
                      SharpActionDetector: 'bg-accent-amber/20 text-accent-amber',
                      SportsOddsAnalyst: 'bg-accent-green/20 text-accent-green',
                    }
                    return (
                      <div key={i} className="card p-4 flex items-center gap-4">
                        {/* Rank */}
                        <div className={cn(
                          'h-10 w-10 rounded-full flex items-center justify-center font-bold text-lg flex-shrink-0',
                          i === 0 ? 'bg-accent-amber/20 text-accent-amber' :
                          i === 1 ? 'bg-gray-400/20 text-gray-300' :
                          i === 2 ? 'bg-amber-700/20 text-amber-600' :
                          'bg-dark-bg text-gray-400'
                        )}>
                          {i + 1}
                        </div>

                        {/* Details */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={cn('text-xs px-2 py-0.5 rounded', sourceColors[play.source] || 'bg-dark-bg text-gray-400')}>
                              {play.source}
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">
                              {play.type}
                            </span>
                            {play.sport && (
                              <span className="text-xs text-gray-500">{play.sport}</span>
                            )}
                          </div>
                          <p className="font-medium">{play.matchup}</p>
                          <p className="text-sm text-primary-400">{play.pick}</p>
                          {play.detail && (
                            <p className="text-xs text-gray-500 mt-1">{play.detail}</p>
                          )}
                        </div>

                        {/* Confidence + Log Pick */}
                        <div className="text-right flex-shrink-0 space-y-2">
                          <p className={cn(
                            'text-2xl font-bold',
                            play.confidence >= 85 ? 'text-accent-green' :
                            play.confidence >= 70 ? 'text-accent-amber' : 'text-gray-400'
                          )}>
                            {play.confidence}%
                          </p>
                          <p className="text-xs text-gray-500">confidence</p>
                          <button
                            className={cn(
                              'text-xs py-1 px-3 rounded-lg font-medium transition-all',
                              pickedId === `play-${i}`
                                ? 'bg-accent-green/20 text-accent-green'
                                : 'bg-primary-600/20 text-primary-400 hover:bg-primary-600/30'
                            )}
                            disabled={quickPickMutation.isPending}
                            onClick={() => {
                              setPickedId(`play-${i}`)
                              quickPickMutation.mutate({
                                matchup: play.matchup || '',
                                pick: play.pick || '',
                                odds: play.odds || -110,
                                stake: 10,
                                sport: play.sport || '',
                                source: 'top_plays',
                              })
                            }}
                          >
                            {pickedId === `play-${i}` ? 'Logged!' : quickPickMutation.isPending ? '...' : 'Log Pick'}
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : !briefResult.executive_summary ? (
                <div className="card p-12 text-center">
                  <Star size={48} className="mx-auto mb-4 text-gray-500" />
                  <h3 className="text-lg font-medium mb-2">No Brief Generated Yet</h3>
                  <p className="text-gray-400">Click "Generate Brief" to run all 5 betting intelligence agents</p>
                </div>
              ) : null}
            </>
          )}
        </div>
      )}

      {/* Session 995B: Sharp Action Tab */}
      {activeTab === 'sharp' && (
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <select
              value={sportFilter}
              onChange={(e) => setSportFilter(e.target.value)}
              className="bg-dark-card border border-dark-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
            >
              <option value="all">All Sports</option>
              <option value="americanfootball_nfl">NFL</option>
              <option value="americanfootball_ncaaf">NCAAF</option>
              <option value="basketball_nba">NBA</option>
              <option value="basketball_ncaab">NCAAB</option>
              <option value="baseball_mlb">MLB</option>
              <option value="icehockey_nhl">NHL</option>
              <option value="soccer_epl">EPL</option>
              <option value="soccer_spain_la_liga">La Liga</option>
              <option value="soccer_germany_bundesliga">Bundesliga</option>
              <option value="soccer_italy_serie_a">Serie A</option>
              <option value="soccer_usa_mls">MLS</option>
              <option value="soccer_uefa_champs_league">Champions League</option>
              <option value="mma_mixed_martial_arts">UFC / MMA</option>
            </select>
            <button className="btn btn-primary flex items-center gap-2" onClick={() => refetchSharp()}>
              <Crosshair size={16} />
              Scan Sharp Action
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total Signals" value={sharpSignals.length} icon={Crosshair} color="bg-primary-600" />
            <StatCard label="HOT" value={sharpSignals.filter((s: any) => s.rating === 'HOT').length} icon={Flame} color="bg-accent-red" />
            <StatCard label="WARM" value={sharpSignals.filter((s: any) => s.rating === 'WARM').length} icon={Zap} color="bg-accent-amber" />
            <StatCard label="Events Scanned" value={sharpData?.data?.events_scanned || 0} icon={Search} color="bg-accent-green" />
          </div>

          {/* LLM Analysis */}
          {sharpData?.data?.llm_analysis && (
            <div className="card p-4 border-l-4 border-l-accent-amber">
              <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <Brain size={14} className="text-accent-amber" />
                AI Sharp Action Analysis
              </h4>
              <div className="text-sm text-gray-300 space-y-1">
                {sharpData.data.llm_analysis.split('\n').map((line: string, idx: number) => {
                  if (!line.trim()) return <div key={idx} className="h-2" />
                  // Bold: **text**
                  const parts = line.split(/(\*\*[^*]+\*\*)/).map((part: string, pi: number) =>
                    part.startsWith('**') && part.endsWith('**')
                      ? <strong key={pi} className="text-white">{part.slice(2, -2)}</strong>
                      : <span key={pi}>{part}</span>
                  )
                  // Bullet lines
                  if (line.trim().startsWith('- ') || line.trim().startsWith('• ')) {
                    return <div key={idx} className="pl-4 flex gap-2"><span className="text-accent-amber">•</span><span>{parts}</span></div>
                  }
                  // Numbered lines
                  if (/^\d+\./.test(line.trim())) {
                    return <div key={idx} className="pl-2">{parts}</div>
                  }
                  return <div key={idx}>{parts}</div>
                })}
              </div>
            </div>
          )}

          {/* Signals */}
          {sharpLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : sharpSignals.length > 0 ? (
            <div className="space-y-4">
              {sharpSignals.map((signal: any, i: number) => {
                const isHot = signal.rating === 'HOT'
                const svs = signal.sharp_vs_soft || {}
                const homeTeam = signal.home_team || signal.matchup?.split(' @ ')[1] || 'Home'
                const awayTeam = signal.away_team || signal.matchup?.split(' @ ')[0] || 'Away'
                const bestStale = (signal.stale_lines || [])[0]
                const favoredSide = svs.sharp_favors
                const favoredTeam = favoredSide === 'home' ? homeTeam : favoredSide === 'away' ? awayTeam : null
                const gameTime = signal.commence_time ? new Date(signal.commence_time).toLocaleString([], {
                  month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
                }) : null

                return (
                  <div key={i} className={cn(
                    'card p-4 border-l-4',
                    isHot ? 'border-l-accent-red' : 'border-l-accent-amber'
                  )}>
                    {/* Header: matchup, rating badge, game time */}
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={cn(
                            'text-xs font-bold px-2 py-0.5 rounded',
                            isHot ? 'bg-accent-red/20 text-accent-red' : 'bg-accent-amber/20 text-accent-amber'
                          )}>
                            {signal.rating}
                          </span>
                          <h4 className="font-medium">{awayTeam} @ {homeTeam}</h4>
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-400">
                          <span>{signal.sport_name}</span>
                          <span>•</span>
                          <span>{signal.bookmaker_count} bookmakers</span>
                          {gameTime && (
                            <>
                              <span>•</span>
                              <span className="flex items-center gap-1">
                                <Calendar size={12} />
                                {gameTime}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className={cn(
                        'text-sm font-mono px-2 py-1 rounded',
                        isHot ? 'bg-accent-red/10 text-accent-red' : 'bg-accent-amber/10 text-accent-amber'
                      )}>
                        {signal.max_divergence} pts div
                      </div>
                    </div>

                    {/* Recommendation Box */}
                    {favoredTeam && (
                      <div className={cn(
                        'p-3 rounded-lg border mb-3',
                        isHot ? 'border-accent-red/30 bg-accent-red/5' : 'border-accent-amber/30 bg-accent-amber/5'
                      )}>
                        <div className="flex items-center gap-2 mb-1">
                          <Crosshair size={14} className={isHot ? 'text-accent-red' : 'text-accent-amber'} />
                          <span className="text-sm font-semibold text-white">
                            Sharp money on: <span className={isHot ? 'text-accent-red' : 'text-accent-amber'}>{favoredTeam} ({favoredSide} ML)</span>
                          </span>
                        </div>
                        {bestStale && (
                          <p className="text-sm text-gray-300 pl-6">
                            Best value: Bet {bestStale.better_side} ML at <span className="font-medium text-white">{bestStale.bookmaker}</span>
                            {' — '}{Math.max(bestStale.home_diff || 0, bestStale.away_diff || 0)} pts off market
                          </p>
                        )}
                      </div>
                    )}

                    {/* Sharp vs Soft inline + Odds Ranges */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 text-sm">
                      {svs.sharp_favors && (
                        <div className="flex items-center gap-4">
                          <span><span className="text-gray-400">Sharp:</span> <span className="font-mono">{svs.sharp_avg_home}</span> avg</span>
                          <span>•</span>
                          <span><span className="text-gray-400">Soft:</span> <span className="font-mono">{svs.soft_avg_home}</span> avg</span>
                          <span>•</span>
                          <span><span className="text-gray-400">Gap:</span> <span className="font-mono font-medium">{svs.divergence}</span> pts</span>
                        </div>
                      )}
                      <div className="flex items-center gap-4">
                        <span><span className="text-gray-400">Home ML:</span> <span className="font-mono">{signal.home_odds_range}</span></span>
                        <span className="text-gray-600">|</span>
                        <span><span className="text-gray-400">Away ML:</span> <span className="font-mono">{signal.away_odds_range}</span></span>
                      </div>
                    </div>

                    {/* Stale Lines — prominent */}
                    {signal.stale_lines && signal.stale_lines.length > 0 && (
                      <div className="border-t border-dark-border pt-2">
                        <p className="text-xs font-semibold text-accent-red mb-1.5 flex items-center gap-1">
                          <AlertTriangle size={12} />
                          Stale Lines (act fast)
                        </p>
                        <div className="space-y-1">
                          {signal.stale_lines.slice(0, 4).map((sl: any, j: number) => (
                            <div key={j} className="flex items-center justify-between text-sm bg-dark-bg rounded px-3 py-1.5">
                              <span className="font-medium">{sl.bookmaker}</span>
                              <span className="text-gray-400">
                                {sl.better_side} side
                                {sl.home_diff ? ` — home ${sl.home_diff} pts off` : ''}
                                {sl.away_diff ? `, away ${sl.away_diff} pts off` : ''}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="card p-12 text-center">
              <Crosshair size={48} className="mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-medium mb-2">No Sharp Action Detected</h3>
              <p className="text-gray-400">Click "Scan Sharp Action" to analyze bookmaker divergence</p>
            </div>
          )}
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

          {/* Stake Calculator Input */}
          <div className="flex items-center gap-3">
            <Calculator size={16} className="text-gray-400" />
            <label className="text-sm text-gray-400">Total stake:</label>
            <div className="flex items-center gap-1">
              <span className="text-sm text-gray-400">$</span>
              <input
                type="number"
                value={arbStake}
                onChange={(e) => setArbStake(e.target.value)}
                className="w-24 px-2 py-1.5 text-sm rounded bg-dark-card border border-dark-border focus:border-primary-500 focus:outline-none font-mono"
              />
            </div>
            <p className="text-xs text-gray-500">Bet sizes calculated per opportunity below</p>
          </div>

          {/* Arbitrage Cards */}
          {arbLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : arbitrageOpps.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {arbitrageOpps.map((arb: ArbitrageCardProps['arb'], i: number) => (
                <ArbitrageCard key={i} arb={arb} totalStake={parseFloat(arbStake) || 100} />
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
            <div className="space-y-3">
              {liveOdds.map((game: any, i: number) => {
                const live = game.live || {}
                const isLive = live.is_live
                const isFinal = live.is_final
                const hasScore = live.home_score != null && live.away_score != null
                const bookmakers = game.bookmakers || []

                return (
                  <div key={i} className={cn('card p-4 border-l-4', isLive ? 'border-l-accent-red' : isFinal ? 'border-l-gray-500' : 'border-l-primary-500')}>
                    {/* Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                          {(game.sport_key || game.sport || '').replace(/_/g, ' ')}
                        </span>
                        {isLive && (
                          <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-accent-red/20 text-accent-red animate-pulse">
                            <Activity size={10} /> LIVE
                          </span>
                        )}
                        {isLive && live.status_detail && (
                          <span className="text-xs font-medium text-accent-red">{live.status_detail}</span>
                        )}
                        {isLive && !live.status_detail && live.period > 0 && (
                          <span className="text-xs font-medium text-accent-red">P{live.period} {live.clock || ''}</span>
                        )}
                        {isFinal && <span className="text-xs px-2 py-0.5 rounded bg-gray-500/20 text-gray-400">FINAL</span>}
                      </div>
                      <span className="text-xs text-gray-500">
                        {game.commence_time ? new Date(game.commence_time).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : ''}
                      </span>
                    </div>

                    {/* Matchup with scores */}
                    <div className="grid grid-cols-7 gap-2 items-center">
                      <div className="col-span-2">
                        <p className="font-medium">{game.away_team}</p>
                      </div>
                      <div className="col-span-3 text-center">
                        {hasScore ? (
                          <div>
                            <span className={cn('text-2xl font-bold', live.away_score > live.home_score ? 'text-accent-green' : 'text-gray-300')}>
                              {live.away_score}
                            </span>
                            <span className="text-gray-500 mx-3">-</span>
                            <span className={cn('text-2xl font-bold', live.home_score > live.away_score ? 'text-accent-green' : 'text-gray-300')}>
                              {live.home_score}
                            </span>
                          </div>
                        ) : (
                          <span className="text-gray-500 text-sm">vs</span>
                        )}
                      </div>
                      <div className="col-span-2 text-right">
                        <p className="font-medium">{game.home_team}</p>
                      </div>
                    </div>

                    {/* Bookmaker odds grid */}
                    {bookmakers.length > 0 && (
                      <div className="mt-3 space-y-1">
                        <div className="grid grid-cols-4 gap-2 text-[10px] text-gray-500 font-medium px-2">
                          <span>Bookmaker</span>
                          <span className="text-right">ML Away</span>
                          <span className="text-right">ML Home</span>
                          <span className="text-right">Draw</span>
                        </div>
                        {bookmakers.slice(0, 6).map((bm: any, bi: number) => {
                          const h2h = bm.markets?.h2h?.outcomes || []
                          const awayOutcome = h2h.find((o: any) => o.name === game.away_team)
                          const homeOutcome = h2h.find((o: any) => o.name === game.home_team)
                          const drawOutcome = h2h.find((o: any) => o.name !== game.away_team && o.name !== game.home_team)
                          if (!awayOutcome && !homeOutcome) return null
                          return (
                            <div key={bi} className="grid grid-cols-4 gap-2 text-xs px-2 py-1.5 rounded bg-dark-bg">
                              <span className="font-medium truncate">{bm.title || bm.key}</span>
                              <span className="text-right font-mono text-gray-300">{awayOutcome?.price ?? '—'}</span>
                              <span className="text-right font-mono text-gray-300">{homeOutcome?.price ?? '—'}</span>
                              <span className="text-right font-mono text-gray-500">{drawOutcome?.price ?? '—'}</span>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              })}
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
                            ({game.spread_movement > 0 ? '+' : ''}{(game.spread_movement ?? 0).toFixed(1)})
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
                            ({game.total_movement > 0 ? '+' : ''}{(game.total_movement ?? 0).toFixed(1)})
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
      {activeTab === 'bankroll' && (() => {
        const bk = bankroll
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="Total Wagered"
                value={`$${(bk.total || bk.total_wagered || 0).toFixed(2)}`}
                icon={DollarSign}
                color="bg-primary-600"
              />
              <StatCard
                label="Net P/L"
                value={`${(bk.total_profit || 0) >= 0 ? '+' : ''}$${(bk.total_profit || 0).toFixed(2)}`}
                icon={TrendingUp}
                color={(bk.total_profit || 0) >= 0 ? 'bg-accent-green' : 'bg-accent-red'}
              />
              <StatCard
                label="At Risk"
                value={`$${(bk.at_risk || 0).toFixed(2)}`}
                icon={AlertTriangle}
                color="bg-accent-amber"
              />
              <StatCard
                label="ROI"
                value={`${(bk.roi || 0).toFixed(1)}%`}
                icon={Target}
                color={(bk.roi || 0) >= 0 ? 'bg-accent-green' : 'bg-accent-red'}
              />
            </div>

            {/* Detailed Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="card p-4 text-center">
                <p className="text-2xl font-bold">{bk.total_bets || 0}</p>
                <p className="text-xs text-gray-400">Total Bets</p>
              </div>
              <div className="card p-4 text-center">
                <p className="text-2xl font-bold text-accent-green">{bk.winning_bets || 0}</p>
                <p className="text-xs text-gray-400">Wins</p>
              </div>
              <div className="card p-4 text-center">
                <p className="text-2xl font-bold text-accent-red">{bk.losing_bets || 0}</p>
                <p className="text-xs text-gray-400">Losses</p>
              </div>
              <div className="card p-4 text-center">
                <p className="text-2xl font-bold">
                  {((bk.win_rate || 0) * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-400">Win Rate</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="card p-4">
                <h4 className="text-sm font-semibold mb-3 text-gray-400">Performance</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Avg Bet Size</span>
                    <span className="font-mono">${(bk.avg_bet_size || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Biggest Win</span>
                    <span className="font-mono text-accent-green">+${(bk.biggest_win || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Biggest Loss</span>
                    <span className="font-mono text-accent-red">${(bk.biggest_loss || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Pending Bets</span>
                    <span className="font-mono">{bk.pending_bets || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Pushes</span>
                    <span className="font-mono">{bk.pushes || 0}</span>
                  </div>
                  {bk.kelly_percent > 0 && (
                    <div className="flex justify-between pt-2 border-t border-dark-border">
                      <span className="text-gray-400">Kelly Bet Size</span>
                      <span className="font-mono text-accent-purple">{(bk.kelly_percent || 0).toFixed(1)}% of bankroll</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="card p-4">
                <h4 className="text-sm font-semibold mb-3 text-gray-400">Quick Tips</h4>
                <div className="space-y-3 text-sm text-gray-400">
                  <p>• Never bet more than 5% of your bankroll on a single wager</p>
                  <p>• Use the Kelly Criterion to size your bets optimally</p>
                  <p>• Track all bets to understand your true ROI</p>
                  <p>• Set stop-loss limits to protect your bankroll</p>
                </div>
              </div>
            </div>
          </div>
        )
      })()}

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

          {/* Add Wager Button + Form */}
          <div>
            <button
              onClick={() => setShowWagerForm(!showWagerForm)}
              className="btn btn-primary flex items-center gap-2"
            >
              <Plus size={16} />
              {showWagerForm ? 'Cancel' : 'Log Wager'}
            </button>

            {showWagerForm && (
              <div className="card p-4 mt-3 border border-primary-500/30">
                <h4 className="text-sm font-semibold mb-3">Log a New Wager</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Matchup / Event *</label>
                    <input
                      type="text"
                      value={wagerForm.matchup}
                      onChange={(e) => setWagerForm(f => ({ ...f, matchup: e.target.value }))}
                      placeholder="e.g., Lakers vs Celtics"
                      className="w-full px-3 py-2 text-sm rounded bg-dark-bg border border-dark-border focus:border-primary-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Your Pick *</label>
                    <input
                      type="text"
                      value={wagerForm.pick}
                      onChange={(e) => setWagerForm(f => ({ ...f, pick: e.target.value }))}
                      placeholder="e.g., Lakers -5.5"
                      className="w-full px-3 py-2 text-sm rounded bg-dark-bg border border-dark-border focus:border-primary-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Odds (American) *</label>
                    <input
                      type="text"
                      value={wagerForm.odds}
                      onChange={(e) => setWagerForm(f => ({ ...f, odds: e.target.value }))}
                      placeholder="-110"
                      className="w-full px-3 py-2 text-sm rounded bg-dark-bg border border-dark-border focus:border-primary-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Stake ($) *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={wagerForm.stake}
                      onChange={(e) => setWagerForm(f => ({ ...f, stake: e.target.value }))}
                      placeholder="10.00"
                      className="w-full px-3 py-2 text-sm rounded bg-dark-bg border border-dark-border focus:border-primary-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Sport</label>
                    <select
                      value={wagerForm.sport}
                      onChange={(e) => setWagerForm(f => ({ ...f, sport: e.target.value }))}
                      className="w-full px-3 py-2 text-sm rounded bg-dark-bg border border-dark-border focus:border-primary-500 focus:outline-none"
                    >
                      <option value="">Select sport</option>
                      <option value="basketball_nba">NBA</option>
                      <option value="basketball_ncaab">NCAAB</option>
                      <option value="americanfootball_nfl">NFL</option>
                      <option value="americanfootball_ncaaf">NCAAF</option>
                      <option value="baseball_mlb">MLB</option>
                      <option value="icehockey_nhl">NHL</option>
                      <option value="soccer_epl">EPL</option>
                      <option value="mma_mixed_martial_arts">UFC/MMA</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Bookmaker</label>
                    <select
                      value={wagerForm.bookmaker}
                      onChange={(e) => setWagerForm(f => ({ ...f, bookmaker: e.target.value }))}
                      className="w-full px-3 py-2 text-sm rounded bg-dark-bg border border-dark-border focus:border-primary-500 focus:outline-none"
                    >
                      <option value="">Select book</option>
                      <option value="FanDuel">FanDuel</option>
                      <option value="DraftKings">DraftKings</option>
                      <option value="BetMGM">BetMGM</option>
                      <option value="Caesars">Caesars</option>
                      <option value="PointsBet">PointsBet</option>
                      <option value="BetRivers">BetRivers</option>
                      <option value="Bovada">Bovada</option>
                      <option value="Pinnacle">Pinnacle</option>
                    </select>
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <p className="text-xs text-gray-500">
                    Potential payout: <span className="font-mono text-white">
                      ${(() => {
                        const odds = parseInt(wagerForm.odds) || -110
                        const stake = parseFloat(wagerForm.stake) || 0
                        const decimal = odds > 0 ? 1 + odds / 100 : 1 + 100 / Math.abs(odds)
                        return (stake * decimal).toFixed(2)
                      })()}
                    </span>
                  </p>
                  <button
                    onClick={() => {
                      if (!wagerForm.matchup || !wagerForm.pick || !wagerForm.stake) return
                      placeBetMutation.mutate({
                        stake: parseFloat(wagerForm.stake),
                        picks: [{
                          event_id: '',
                          sport: wagerForm.sport,
                          matchup: wagerForm.matchup,
                          market_type: wagerForm.market_type,
                          pick: wagerForm.pick,
                          odds: parseInt(wagerForm.odds) || -110,
                          bookmaker: wagerForm.bookmaker,
                        }]
                      })
                    }}
                    disabled={placeBetMutation.isPending || !wagerForm.matchup || !wagerForm.pick}
                    className="btn btn-primary flex items-center gap-2"
                  >
                    {placeBetMutation.isPending ? (
                      <><Loader2 size={14} className="animate-spin" /> Logging...</>
                    ) : (
                      <><Plus size={14} /> Log Wager</>
                    )}
                  </button>
                </div>
                {placeBetMutation.isError && (
                  <p className="text-xs text-accent-red mt-2">Failed to log wager. Please try again.</p>
                )}
              </div>
            )}
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

      {/* ═══ Combined Records Tab ═══ */}
      {activeTab === 'records' && (
        <div className="space-y-6">
          {/* AI / User Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setRecordsView('ai')}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                recordsView === 'ai' ? 'bg-primary-600 text-white' : 'bg-dark-bg text-gray-400 hover:text-white'
              )}
            >
              <Brain size={14} className="inline mr-2" />
              AI Predictions
            </button>
            <button
              onClick={() => setRecordsView('user')}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                recordsView === 'user' ? 'bg-primary-600 text-white' : 'bg-dark-bg text-gray-400 hover:text-white'
              )}
            >
              <Trophy size={14} className="inline mr-2" />
              My Betting
            </button>
          </div>

          {/* Pipeline Freshness Strip */}
          {(() => {
            const p = pipelineData?.data?.pipeline
            if (!p) return null
            const items = [
              { label: 'Odds', ...p.odds_updated },
              { label: 'Predictions', ...p.predictions_updated },
              { label: 'Scores', ...p.scores_updated },
              { label: 'Evaluations', ...p.evaluations_updated },
            ]
            return (
              <div className="flex items-center gap-4 text-xs text-gray-500 flex-wrap">
                {items.map(item => (
                  <span key={item.label} title={item.timestamp || 'Not available'}>
                    {item.label}: <span className="text-gray-400">{item.ago || '—'}</span>
                  </span>
                ))}
              </div>
            )
          })()}

          {/* ── AI Predictions View ── */}
          {recordsView === 'ai' && (
            <>
              {/* Model Filter Chips */}
              {(() => {
                const availableModels: string[] = trackRecordData?.data?.available_models || []
                return availableModels.length > 0 ? (
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm text-gray-400">Model:</span>
                    <button
                      onClick={() => setModelFilter('')}
                      className={cn(
                        'text-xs px-3 py-1.5 rounded-lg font-medium transition-colors',
                        !modelFilter ? 'bg-primary-600 text-white' : 'bg-dark-bg text-gray-400 hover:text-white'
                      )}
                    >
                      All
                    </button>
                    {availableModels.map((model: string) => (
                      <button
                        key={model}
                        onClick={() => setModelFilter(modelFilter === model ? '' : model)}
                        className={cn(
                          'text-xs px-3 py-1.5 rounded-lg font-medium transition-colors',
                          modelFilter === model ? 'bg-primary-600 text-white' : 'bg-dark-bg text-gray-400 hover:text-white'
                        )}
                      >
                        {model.replace(/_/g, ' ')}
                      </button>
                    ))}
                  </div>
                ) : null
              })()}

              {trackRecordLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 size={32} className="animate-spin text-primary-400" />
                </div>
              ) : (() => {
                const summary = trackRecordData?.data?.summary || {}
                const bySport = trackRecordData?.data?.by_sport || {}
                const recentPreds = trackRecordData?.data?.recent_predictions || []

                return (
                  <>
                    {/* Summary Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <StatCard
                        label="Accuracy"
                        value={`${summary.accuracy_percent ?? 0}%`}
                        icon={Target}
                        color={summary.accuracy_percent >= 55 ? 'bg-accent-green' : summary.accuracy_percent >= 50 ? 'bg-accent-amber' : 'bg-accent-red'}
                      />
                      <StatCard
                        label="Total Picks"
                        value={`${summary.correct_predictions ?? 0}-${summary.incorrect_predictions ?? 0}`}
                        icon={Brain}
                        color="bg-primary-600"
                      />
                      <StatCard
                        label="ROI"
                        value={summary.roi_percent != null ? `${summary.roi_percent > 0 ? '+' : ''}${summary.roi_percent}%` : 'N/A'}
                        icon={DollarSign}
                        color={summary.roi_percent > 0 ? 'bg-accent-green' : summary.roi_percent < 0 ? 'bg-accent-red' : 'bg-primary-600'}
                      />
                      <StatCard
                        label="Calibration"
                        value={`${summary.calibration_score ?? 0}%`}
                        icon={BarChart3}
                        color={summary.is_well_calibrated ? 'bg-accent-green' : 'bg-accent-amber'}
                      />
                    </div>
                    {summary.pending_predictions > 0 && (
                      <p className="text-xs text-gray-500 -mt-3">
                        {summary.pending_predictions} picks pending evaluation &middot; {summary.days_analyzed}d window
                        {summary.avg_clv != null && <span> &middot; Avg CLV: {summary.avg_clv > 0 ? '+' : ''}{summary.avg_clv}%</span>}
                      </p>
                    )}

                    {/* Sport x Bet Type Breakdown */}
                    {Object.keys(bySport).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold mb-3">By Sport</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                          {Object.entries(bySport).map(([sport, data]: [string, any]) => (
                            <div key={sport} className="card p-4">
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-medium uppercase text-sm">{sport}</span>
                                <span className={cn(
                                  'text-lg font-bold',
                                  data.accuracy >= 60 ? 'text-accent-green' :
                                  data.accuracy >= 50 ? 'text-accent-amber' : 'text-accent-red'
                                )}>{data.accuracy}%</span>
                              </div>
                              <div className="flex items-center gap-3 text-sm text-gray-400 mb-2">
                                <span className="text-accent-green">{data.correct}W</span>
                                <span className="text-accent-red">{data.incorrect}L</span>
                                <span>{data.total} total</span>
                              </div>
                              <div className="w-full bg-dark-border rounded-full h-2">
                                <div
                                  className={cn(
                                    'h-2 rounded-full',
                                    data.accuracy >= 60 ? 'bg-accent-green' :
                                    data.accuracy >= 50 ? 'bg-accent-amber' : 'bg-accent-red'
                                  )}
                                  style={{ width: `${Math.min(data.accuracy, 100)}%` }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recent Predictions Table */}
                    {recentPreds.length > 0 ? (
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-lg font-semibold">Recent Predictions</h3>
                          <span className="text-xs text-gray-500">Click a row for details</span>
                        </div>
                        <div className="card overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="border-b border-dark-border text-gray-400 text-left">
                                <th className="py-3 px-4">Date</th>
                                <th className="py-3 px-4">Sport</th>
                                <th className="py-3 px-4">Matchup</th>
                                <th className="py-3 px-4">Pick</th>
                                <th className="py-3 px-4">Odds</th>
                                <th className="py-3 px-4">Conf</th>
                                <th className="py-3 px-4">Result</th>
                              </tr>
                            </thead>
                            <tbody>
                              {recentPreds.map((pred: any) => (
                                <tr
                                  key={pred.id}
                                  className="border-b border-dark-border hover:bg-dark-bg/50 cursor-pointer"
                                  onClick={() => setSelectedPick(pred as PickDetail)}
                                >
                                  <td className="py-3 px-4 text-gray-400">{pred.game_date || '\u2014'}</td>
                                  <td className="py-3 px-4 uppercase text-xs">{pred.sport_type}</td>
                                  <td className="py-3 px-4 font-medium">{pred.matchup || '\u2014'}</td>
                                  <td className="py-3 px-4 font-medium">{pred.predicted_winner}</td>
                                  <td className="py-3 px-4">
                                    {pred.odds != null ? (
                                      <span className={cn('font-mono text-sm', pred.odds > 0 ? 'text-accent-green' : 'text-accent-red')}>
                                        {pred.odds > 0 ? '+' : ''}{pred.odds}
                                      </span>
                                    ) : <span className="text-gray-500">{'\u2014'}</span>}
                                  </td>
                                  <td className="py-3 px-4">
                                    <span className={cn(
                                      'font-medium',
                                      pred.confidence >= 75 ? 'text-accent-green' :
                                      pred.confidence >= 60 ? 'text-accent-amber' : 'text-gray-400'
                                    )}>{pred.confidence}%</span>
                                  </td>
                                  <td className="py-3 px-4">
                                    {pred.was_correct === null ? (
                                      <span className="text-xs text-gray-500">Pending</span>
                                    ) : pred.was_correct ? (
                                      <CheckCircle size={18} className="text-accent-green" />
                                    ) : (
                                      <XCircle size={18} className="text-accent-red" />
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ) : (
                      <div className="card p-12 text-center">
                        <BarChart3 size={48} className="mx-auto mb-4 text-gray-500" />
                        <h3 className="text-lg font-medium mb-2">No Evaluated Predictions Yet</h3>
                        <p className="text-gray-400">Predictions will appear here after outcomes are evaluated</p>
                      </div>
                    )}
                  </>
                )
              })()}
            </>
          )}

          {/* ── User Betting View ── */}
          {recordsView === 'user' && (
            <>
              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  label="Total P/L"
                  value={`$${(stats.total_profit_loss || 0).toFixed(2)}`}
                  icon={DollarSign}
                  color="bg-primary-600"
                  trend={{ value: stats.roi || 0, isPositive: (stats.roi || 0) >= 0 }}
                />
                <StatCard label="Win Rate" value={`${(stats.win_rate || 0).toFixed(1)}%`} icon={Target} color="bg-accent-green" />
                <StatCard label="Total Wagers" value={stats.total_wagers || 0} icon={Trophy} color="bg-accent-amber" />
                <StatCard label="Pending" value={stats.pending || 0} icon={Activity} color="bg-accent-purple" />
              </div>

              {/* Streaks */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  label="Current Streak"
                  value={`${Math.abs(stats.current_streak || 0)}${(stats.current_streak || 0) >= 0 ? 'W' : 'L'}`}
                  icon={Flame}
                  color={(stats.current_streak || 0) >= 0 ? "bg-accent-green" : "bg-accent-red"}
                />
                <StatCard label="Best Win Streak" value={stats.longest_win_streak || 0} icon={Award} color="bg-accent-green" />
                <StatCard label="Worst Loss Streak" value={stats.longest_loss_streak || 0} icon={TrendingDown} color="bg-accent-red" />
                <StatCard label="ROI" value={`${(stats.roi || 0) >= 0 ? '+' : ''}${(stats.roi || 0).toFixed(1)}%`} icon={TrendingUp} color="bg-primary-600" />
              </div>

              {/* Singles vs Parlays + Per-Sport */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Layers size={18} className="text-primary-400" />
                    Singles vs Parlays
                  </h3>
                  <div className="space-y-4">
                    <div className="p-3 rounded-lg bg-primary-600/10 border border-primary-600/20">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-primary-400">Singles</span>
                        <span className={cn('font-bold', singlesRecord.profit >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                          {singlesRecord.profit >= 0 ? '+' : ''}${(singlesRecord.profit ?? 0).toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-accent-green">{singlesRecord.wins}W</span>
                        <span className="text-accent-red">{singlesRecord.losses}L</span>
                      </div>
                    </div>
                    <div className="p-3 rounded-lg bg-accent-purple/10 border border-accent-purple/20">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-accent-purple">Parlays</span>
                        <span className={cn('font-bold', parlaysRecord.profit >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                          {parlaysRecord.profit >= 0 ? '+' : ''}${(parlaysRecord.profit ?? 0).toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-accent-green">{parlaysRecord.wins}W</span>
                        <span className="text-accent-red">{parlaysRecord.losses}L</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <BarChart3 size={18} className="text-accent-amber" />
                    By Sport
                  </h3>
                  {Object.keys(statsBySport).length > 0 ? (
                    <div className="space-y-3 max-h-[280px] overflow-y-auto">
                      {Object.entries(statsBySport).map(([sport, sportStats]) => {
                        const totalGames = sportStats.wins + sportStats.losses + (sportStats.pushes || 0)
                        const winRate = totalGames > 0 ? (sportStats.wins / totalGames) * 100 : 0
                        return (
                          <div key={sport} className="p-3 rounded-lg bg-dark-bg">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-sm">{sport.split('_').slice(1).join(' ').toUpperCase() || sport}</span>
                              <span className={cn('font-bold text-sm', sportStats.profit >= 0 ? 'text-accent-green' : 'text-accent-red')}>
                                {sportStats.profit >= 0 ? '+' : ''}${(sportStats.profit ?? 0).toFixed(2)}
                              </span>
                            </div>
                            <div className="flex items-center gap-3 text-xs">
                              <span className="text-accent-green">{sportStats.wins}W</span>
                              <span className="text-accent-red">{sportStats.losses}L</span>
                              <span className="text-gray-400">{(winRate ?? 0).toFixed(1)}%</span>
                            </div>
                            <div className="mt-2 h-1 rounded bg-dark-border overflow-hidden">
                              <div className="h-full bg-accent-green" style={{ width: `${winRate}%` }} />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <BarChart3 size={32} className="mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No sport data yet</p>
                      <p className="text-xs text-gray-500 mt-1">Place wagers to see per-sport performance</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Recent Wagers */}
              {wagers.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <History size={18} className="text-primary-400" />
                    Recent Wagers
                    <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400 ml-auto">{wagers.length}</span>
                  </h3>
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
                        {wagers.slice(0, 10).map((wager: WagerRowProps['wager']) => (
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
              )}
            </>
          )}
        </div>
      )}

      {/* Pick Details Drawer */}
      {selectedPick && (
        <PickDetailsDrawer
          pick={selectedPick}
          onClose={() => setSelectedPick(null)}
          onLogWager={handleLogWager}
        />
      )}
    </div>
  )
}
