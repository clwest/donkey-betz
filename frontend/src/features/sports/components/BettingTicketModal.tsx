import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../../components/common/Tabs';
import { toast } from 'sonner';
import {
  Clock,
  MapPin,
  Cloud,
  Activity,
  TrendingUp,
  Calculator,
  Zap,
  Trophy,
  Target,
  DollarSign,
  Users,
  AlertTriangle,
  CheckCircle,
  X,
  Plus,
  Minus
} from 'lucide-react';
import type { Game } from '../api/sports';
import { getGameOdds } from '../api/sports';
import '../../../styles/gaming-theme.css';

interface BettingMarket {
  type: 'moneyline' | 'spread' | 'total' | 'prop';
  name: string;
  options: BettingOption[];
}

interface BettingOption {
  id: string;
  name: string;
  odds: number; // American odds (e.g., +150, -110)
  line?: number; // For spreads/totals
  implied_prob?: number;
  kelly_rec?: number;
}

interface BetSlipItem {
  gameId: string;
  market: string;
  option: BettingOption;
  stake?: number;
}

interface BettingTicketModalProps {
  game: Game | null;
  isOpen: boolean;
  onClose: () => void;
}

export function BettingTicketModal({ game, isOpen, onClose }: BettingTicketModalProps) {
  const [activeMarket, setActiveMarket] = useState<string>('moneyline');
  const [betSlip, setBetSlip] = useState<BetSlipItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [gameOdds, setGameOdds] = useState<any>(null);
  const [bankroll, setBankroll] = useState<number>(1000);
  const [kellyFraction, setKellyFraction] = useState<number>(0.25);
  const [defaultWinProb, setDefaultWinProb] = useState<number>(0.52);

  // Mock detailed game data (in production, this would come from APIs)
  const gameDetails = game ? {
    weather: {
      condition: "Clear",
      temperature: 72,
      humidity: 45,
      wind: "SW 8 mph"
    },
    injuries: [
      { team: game.home_team_name, player: "Starting QB", status: "Questionable", position: "QB" },
      { team: game.away_team_name, player: "Star WR", status: "Probable", position: "WR" }
    ],
    teamStats: {
      [game.home_team_name]: {
        record: "8-2",
        pointsFor: 245,
        pointsAgainst: 180,
        homeRecord: "5-0"
      },
      [game.away_team_name]: {
        record: "6-4", 
        pointsFor: 215,
        pointsAgainst: 195,
        awayRecord: "2-3"
      }
    },
    trends: [
      `${game.home_team_name} is 7-3 ATS at home`,
      `${game.away_team_name} is 4-6 ATS on the road`,
      "Under has hit in 6 of last 8 meetings",
      `${game.home_team_name} averages 31.2 PPG at home`
    ]
  } : null;

  // Mock betting markets
  const bettingMarkets: BettingMarket[] = game ? [
    {
      type: 'moneyline',
      name: 'Moneyline',
      options: [
        {
          id: 'ml_home',
          name: game.home_team_name,
          odds: -150,
          implied_prob: 60.0,
          kelly_rec: 2.5
        },
        {
          id: 'ml_away',
          name: game.away_team_name,
          odds: +130,
          implied_prob: 43.5,
          kelly_rec: 4.2
        }
      ]
    },
    {
      type: 'spread',
      name: 'Point Spread',
      options: [
        {
          id: 'spread_home',
          name: `${game.home_team_name} -3.5`,
          odds: -110,
          line: -3.5,
          implied_prob: 52.4,
          kelly_rec: 1.8
        },
        {
          id: 'spread_away',
          name: `${game.away_team_name} +3.5`,
          odds: -110,
          line: +3.5,
          implied_prob: 52.4,
          kelly_rec: 1.8
        }
      ]
    },
    {
      type: 'total',
      name: 'Total Points',
      options: [
        {
          id: 'total_over',
          name: 'Over 47.5',
          odds: -105,
          line: 47.5,
          implied_prob: 51.2,
          kelly_rec: 2.1
        },
        {
          id: 'total_under',
          name: 'Under 47.5',
          odds: -115,
          line: 47.5,
          implied_prob: 53.5,
          kelly_rec: 1.2
        }
      ]
    },
    {
      type: 'prop',
      name: 'Player Props',
      options: [
        {
          id: 'prop_qb_pass_yards',
          name: 'QB Passing Yards Over 275.5',
          odds: +105,
          line: 275.5,
          implied_prob: 48.8,
          kelly_rec: 3.1
        },
        {
          id: 'prop_first_td',
          name: 'First Touchdown Scorer',
          odds: +650,
          implied_prob: 13.3,
          kelly_rec: 5.5
        }
      ]
    }
  ] : [];

  const formatOdds = (odds: number) => {
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  const calculateImpliedProbability = (odds: number) => {
    if (odds > 0) {
      return 100 / (odds + 100);
    } else {
      return Math.abs(odds) / (Math.abs(odds) + 100);
    }
  };

  const calculateExpectedValue = (odds: number, winProb: number) => {
    const impliedProb = calculateImpliedProbability(odds);
    const decimal = odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
    return ((winProb * decimal) - 1) * 100;
  };

  const calculateKellyPercentage = (odds: number, winProb: number) => {
    const decimal = odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
    const kellyPercent = ((winProb * decimal - 1) / (decimal - 1)) * 100;
    return Math.max(0, kellyPercent); // Don't recommend negative kelly
  };

  const calculateKellyStake = (option: BettingOption, bankroll: number, winProb?: number) => {
    const prob = winProb || defaultWinProb;
    const kellyPercent = calculateKellyPercentage(option.odds, prob);
    const fractionalKelly = kellyPercent * kellyFraction / 100;
    return Math.round((fractionalKelly / 100) * bankroll);
  };

  const addToBetSlip = (market: string, option: BettingOption) => {
    if (!game) return;
    
    const newBet: BetSlipItem = {
      gameId: game.id,
      market,
      option,
      stake: calculateKellyStake(option, bankroll, defaultWinProb)
    };

    setBetSlip(prev => {
      // Remove if already exists, add if new
      const exists = prev.find(bet => bet.option.id === option.id);
      if (exists) {
        toast.info('Removed from bet slip');
        return prev.filter(bet => bet.option.id !== option.id);
      } else {
        toast.success('Added to bet slip');
        return [...prev, newBet];
      }
    });
  };

  const updateStake = (optionId: string, newStake: number) => {
    setBetSlip(prev => prev.map(bet => 
      bet.option.id === optionId ? { ...bet, stake: Math.max(0, newStake) } : bet
    ));
  };

  const isInBetSlip = (optionId: string) => {
    return betSlip.some(bet => bet.option.id === optionId);
  };

  const getTotalStake = () => {
    return betSlip.reduce((sum, bet) => sum + (bet.stake || 0), 0);
  };

  const getTotalPayout = () => {
    return betSlip.reduce((sum, bet) => {
      if (!bet.stake) return sum;
      const decimal = bet.option.odds > 0 ? 
        (bet.option.odds / 100) + 1 : 
        (100 / Math.abs(bet.option.odds)) + 1;
      return sum + (bet.stake * decimal);
    }, 0);
  };

  if (!game) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[98vw] w-[98vw] max-h-[98vh] min-h-[98vh] overflow-y-auto gaming-card !p-0">
        <div className="gaming-border-glow"></div>
        
        <DialogHeader className="border-b border-gaming-border pb-8">
          <div className="text-center mb-6">
            <div className="text-cyan-400 font-mono text-xl font-bold tracking-wider">
              🎯 DONKEY BETZ COMMAND CENTER 🎯
            </div>
            <div className="text-xs gaming-text-accent mt-2 tracking-wide">
              PROFESSIONAL BETTING TERMINAL • REAL-TIME ANALYTICS • KELLY CRITERION
            </div>
          </div>
          
          <DialogTitle className="text-3xl font-black gaming-text-primary flex items-center gap-4 justify-center">
            <div className="text-4xl">{game.league === 'NFL' ? '🏈' : game.league === 'NBA' ? '🏀' : '⚾'}</div>
            <div>
              <div className="flex items-center gap-4">
                {game.away_team_name} <span className="gaming-text-neon text-2xl">@</span> {game.home_team_name}
              </div>
              <div className="gaming-text-secondary text-lg font-mono mt-2">
                {game.league} • {new Date(game.scheduled_start).toLocaleDateString()} • {new Date(game.scheduled_start).toLocaleTimeString()}
              </div>
            </div>
          </DialogTitle>
        </DialogHeader>

        {/* 🎯 COMMAND CENTER LAYOUT - Ultra-Wide Spread */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-16 p-12">
          {/* Left Section: Game Details (2 columns) */}
          <div className="xl:col-span-2 space-y-12">
            {/* Compact Game Overview */}
            <div className="gaming-card">
              <div className="gaming-border-glow"></div>
              <div className="p-8">
                <h3 className="text-xl font-bold gaming-text-primary mb-4 flex items-center gap-2 border-b border-gaming-border pb-2">
                  <Activity className="w-5 h-5" />
                  MISSION INTELLIGENCE
                </h3>
                
                {/* Team Matchup - Horizontal */}
                <div className="flex items-center justify-between mb-4">
                  <div className="gaming-team">
                    <div className="gaming-team-avatar text-sm">
                      {game.away_team_name.substring(0, 3)}
                    </div>
                    <div>
                      <div className="gaming-team-name text-sm">{game.away_team_name}</div>
                      <div className="gaming-text-secondary text-xs">
                        {gameDetails?.teamStats[game.away_team_name]?.record} (Away: {gameDetails?.teamStats[game.away_team_name]?.awayRecord})
                      </div>
                    </div>
                  </div>
                  
                  <div className="gaming-text-neon text-xl font-bold">@</div>
                  
                  <div className="gaming-team gaming-home">
                    <div className="gaming-team-avatar gaming-home text-sm">
                      {game.home_team_name.substring(0, 3)}
                    </div>
                    <div>
                      <div className="gaming-team-name text-sm">{game.home_team_name}</div>
                      <div className="gaming-text-secondary text-xs">
                        {gameDetails?.teamStats[game.home_team_name]?.record} (Home: {gameDetails?.teamStats[game.home_team_name]?.homeRecord})
                      </div>
                    </div>
                  </div>
                </div>

                {/* Weather & Venue - Compact */}
                <div className="gaming-status bg-gaming-neon-cyan/20 border-gaming-neon-cyan text-gaming-neon-cyan p-3 text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      <span className="font-bold">{game.venue_name || 'Stadium TBD'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Cloud className="w-3 h-3" />
                      <span>{gameDetails?.weather.condition} {gameDetails?.weather.temperature}°F</span>
                    </div>
                  </div>
                  <div className="text-xs opacity-75">
                    Humidity: {gameDetails?.weather.humidity}% • Wind: {gameDetails?.weather.wind}
                  </div>
                </div>
              </div>
            </div>

            {/* Injuries & Trends - Side by Side */}
            <div className="grid grid-cols-2 gap-10">
              {/* Injury Report - Compact */}
              <div className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-8">
                  <h3 className="text-lg font-bold gaming-text-primary mb-4 flex items-center gap-2 border-b border-gaming-border pb-2">
                    <AlertTriangle className="w-5 h-5" />
                    INJURY REPORT
                  </h3>
                  <div className="space-y-2">
                    {gameDetails?.injuries.map((injury, idx) => (
                      <div key={idx} className="gaming-status text-xs p-2">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={injury.status === 'Questionable' ? 'destructive' : 'secondary'} className="text-xs">
                            {injury.status}
                          </Badge>
                          <span className="font-medium">{injury.player}</span>
                        </div>
                        <div className="gaming-text-secondary">
                          {injury.position} • {injury.team}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Betting Trends - Compact */}
              <div className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-8">
                  <h3 className="text-lg font-bold gaming-text-primary mb-4 flex items-center gap-2 border-b border-gaming-border pb-2">
                    <TrendingUp className="w-5 h-5" />
                    BETTING TRENDS
                  </h3>
                  <div className="space-y-1">
                    {gameDetails?.trends.map((trend, idx) => (
                      <div key={idx} className="gaming-text-secondary text-xs">
                        • {trend}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Middle Section: Betting Markets (1 column) */}
          <div className="space-y-12">
            <div className="gaming-card">
              <div className="gaming-border-glow"></div>
              <div className="p-10">
                <h3 className="text-xl font-bold gaming-text-primary mb-8 flex items-center gap-2 border-b border-gaming-border pb-4">
                  <Target className="w-5 h-5" />
                  BETTING MARKETS
                </h3>
                
                <Tabs value={activeMarket} onValueChange={setActiveMarket}>
                  <TabsList className="grid grid-cols-2 mb-10 bg-gaming-background">
                    <TabsTrigger value="moneyline" className="gaming-btn text-xs">Moneyline</TabsTrigger>
                    <TabsTrigger value="spread" className="gaming-btn text-xs">Spread</TabsTrigger>
                  </TabsList>
                  <TabsList className="grid grid-cols-2 mb-10 bg-gaming-background">
                    <TabsTrigger value="total" className="gaming-btn text-xs">Total</TabsTrigger>
                    <TabsTrigger value="prop" className="gaming-btn text-xs">Props</TabsTrigger>
                  </TabsList>

                  {bettingMarkets.map(market => (
                    <TabsContent key={market.type} value={market.type} className="space-y-6">
                      {market.options.map(option => {
                        const inSlip = isInBetSlip(option.id);
                        const kellyStake = calculateKellyStake(option, bankroll, defaultWinProb);
                        const expectedValue = calculateExpectedValue(option.odds, defaultWinProb);
                        const impliedProb = calculateImpliedProbability(option.odds);
                        
                        return (
                          <div
                            key={option.id}
                            className={`gaming-card cursor-pointer transition-all ${
                              inSlip ? 'gaming-bet-hot border-gaming-neon-green' : 'hover:border-gaming-neon-cyan'
                            }`}
                            onClick={() => addToBetSlip(market.name, option)}
                          >
                            <div className="p-6">
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <div className="font-bold gaming-text-primary text-sm">{option.name}</div>
                                  <div className="font-bold text-lg gaming-text-neon">
                                    {formatOdds(option.odds)}
                                  </div>
                                </div>
                                <div className="grid grid-cols-3 gap-2 text-xs">
                                  <div className="text-center">
                                    <div className="gaming-text-secondary">Implied</div>
                                    <div className="font-bold">{(impliedProb * 100).toFixed(1)}%</div>
                                  </div>
                                  <div className="text-center">
                                    <div className={expectedValue > 0 ? "text-green-400" : "text-red-400"}>EV</div>
                                    <div className={`font-bold ${expectedValue > 0 ? "text-green-400" : "text-red-400"}`}>
                                      {expectedValue > 0 ? '+' : ''}{expectedValue.toFixed(1)}%
                                    </div>
                                  </div>
                                  <div className="text-center">
                                    <div className="gaming-text-accent">Kelly</div>
                                    <div className="font-bold text-cyan-400">${kellyStake}</div>
                                  </div>
                                </div>
                                <div className="text-center">
                                  {inSlip ? (
                                    <CheckCircle className="w-5 h-5 text-green-400 mx-auto" />
                                  ) : (
                                    <Plus className="w-5 h-5 gaming-text-secondary mx-auto" />
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </TabsContent>
                  ))}
                </Tabs>
              </div>
            </div>
          </div>

          {/* Right Section: Calculator & Bet Slip (1 column) */}
          <div className="space-y-12">
            {/* Advanced Kelly Calculator */}
            <div className="gaming-card">
              <div className="gaming-border-glow"></div>
              <div className="p-6">
                <h3 className="text-xl font-bold gaming-text-primary mb-4 flex items-center gap-2">
                  <Calculator className="w-5 h-5 animate-pulse" />
                  Donkey Betz Calculator
                </h3>
                
                <div className="space-y-4">
                  {/* Bankroll Input */}
                  <div>
                    <label className="block gaming-text-secondary text-sm mb-2">Total Bankroll</label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-3 w-4 h-4 gaming-text-accent" />
                      <input
                        type="number"
                        value={bankroll}
                        onChange={(e) => setBankroll(Math.max(0, Number(e.target.value)))}
                        className="w-full gaming-card pl-10 pr-3 py-2 border border-gaming-border rounded gaming-text-primary font-mono"
                        min="0"
                        step="100"
                      />
                    </div>
                  </div>

                  {/* Win Probability */}
                  <div>
                    <label className="block gaming-text-secondary text-sm mb-2">
                      Default Win Probability ({(defaultWinProb * 100).toFixed(1)}%)
                    </label>
                    <input
                      type="range"
                      min="0.45"
                      max="0.65"
                      step="0.01"
                      value={defaultWinProb}
                      onChange={(e) => setDefaultWinProb(Number(e.target.value))}
                      className="w-full accent-cyan-500"
                    />
                    <div className="flex justify-between text-xs gaming-text-secondary mt-1">
                      <span>45% (Underdog)</span>
                      <span>52% (Balanced)</span>
                      <span>65% (Favorite)</span>
                    </div>
                  </div>
                  
                  {/* Kelly Fraction */}
                  <div>
                    <label className="block gaming-text-secondary text-sm mb-2">
                      Kelly Fraction ({(kellyFraction * 100).toFixed(0)}%)
                    </label>
                    <div className="grid grid-cols-4 gap-2 mb-2">
                      {[0.25, 0.5, 0.75, 1.0].map(fraction => (
                        <button
                          key={fraction}
                          onClick={() => setKellyFraction(fraction)}
                          className={`px-2 py-1 rounded text-xs font-bold transition-all ${
                            kellyFraction === fraction 
                              ? 'bg-cyan-500 text-black' 
                              : 'bg-gray-700 gaming-text-secondary hover:bg-gray-600'
                          }`}
                        >
                          {(fraction * 100).toFixed(0)}%
                        </button>
                      ))}
                    </div>
                    <input
                      type="range"
                      min="0.1"
                      max="1"
                      step="0.05"
                      value={kellyFraction}
                      onChange={(e) => setKellyFraction(Number(e.target.value))}
                      className="w-full accent-cyan-500"
                    />
                    <div className="flex justify-between text-xs gaming-text-secondary mt-1">
                      <span>10% (Ultra Safe)</span>
                      <span>25% (Conservative)</span>
                      <span>50% (Moderate)</span>
                      <span>100% (Full Kelly)</span>
                    </div>
                  </div>

                  {/* Risk Warning */}
                  {kellyFraction > 0.5 && (
                    <div className="flex items-center gap-2 p-3 bg-yellow-500/20 border border-yellow-500/50 rounded">
                      <AlertTriangle className="w-4 h-4 text-yellow-400" />
                      <div className="text-xs text-yellow-400">
                        <strong>High Risk:</strong> Using {'>'}
                        {(kellyFraction * 100).toFixed(0)}% Kelly increases volatility
                      </div>
                    </div>
                  )}

                  {/* Calculator Summary */}
                  <div className="space-y-2 p-4 bg-cyan-500/10 border border-cyan-500/30 rounded">
                    <div className="text-xs gaming-text-accent font-bold">CALCULATOR SETTINGS</div>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <div className="gaming-text-secondary">Bankroll</div>
                        <div className="font-bold gaming-text-primary">${bankroll.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="gaming-text-secondary">Win Prob</div>
                        <div className="font-bold gaming-text-primary">{(defaultWinProb * 100).toFixed(1)}%</div>
                      </div>
                      <div>
                        <div className="gaming-text-secondary">Kelly Fraction</div>
                        <div className="font-bold gaming-text-primary">{(kellyFraction * 100).toFixed(0)}%</div>
                      </div>
                      <div>
                        <div className="gaming-text-secondary">Max Stake</div>
                        <div className="font-bold text-cyan-400">${Math.round(bankroll * 0.1).toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bet Slip */}
            <div className="gaming-card">
              <div className="gaming-border-glow"></div>
              <div className="p-6">
                <h3 className="text-xl font-bold gaming-text-primary mb-4 flex items-center gap-2">
                  <DollarSign className="w-5 h-5" />
                  Bet Slip ({betSlip.length})
                </h3>

                {betSlip.length === 0 ? (
                  <div className="text-center py-8 gaming-text-secondary">
                    <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Select betting markets to build your slip</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {betSlip.map((bet, idx) => (
                      <div key={bet.option.id} className="gaming-card border-gaming-border">
                        <div className="p-8">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex-1">
                              <div className="font-medium gaming-text-primary text-sm">
                                {bet.option.name}
                              </div>
                              <div className="gaming-text-secondary text-xs">
                                {bet.market} • {formatOdds(bet.option.odds)}
                              </div>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setBetSlip(prev => prev.filter(b => b.option.id !== bet.option.id))}
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => updateStake(bet.option.id, (bet.stake || 0) - 5)}
                            >
                              <Minus className="w-4 h-4" />
                            </Button>
                            
                            <input
                              type="number"
                              value={bet.stake || 0}
                              onChange={(e) => updateStake(bet.option.id, Number(e.target.value))}
                              className="flex-1 gaming-card px-2 py-1 text-center text-sm border border-gaming-border rounded"
                              placeholder="Stake"
                            />
                            
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => updateStake(bet.option.id, (bet.stake || 0) + 5)}
                            >
                              <Plus className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* Bet Slip Summary */}
                    <div className="border-t border-gaming-border pt-4 space-y-2">
                      <div className="flex justify-between gaming-text-secondary text-sm">
                        <span>Total Stake:</span>
                        <span>${getTotalStake()}</span>
                      </div>
                      <div className="flex justify-between gaming-text-primary font-bold">
                        <span>Potential Payout:</span>
                        <span className="gaming-text-neon">${getTotalPayout().toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between gaming-text-secondary text-sm">
                        <span>Potential Profit:</span>
                        <span>${(getTotalPayout() - getTotalStake()).toFixed(2)}</span>
                      </div>
                    </div>

                    {/* Place Bet Button */}
                    <Button
                      className="w-full gaming-btn-active py-3 text-lg font-bold"
                      onClick={() => {
                        toast.success('🎯 Bets placed successfully!', {
                          description: `${betSlip.length} bets for $${getTotalStake()}`
                        });
                        setBetSlip([]);
                      }}
                      disabled={getTotalStake() === 0}
                    >
                      <Trophy className="w-5 h-5 mr-2" />
                      PLACE BETS
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}