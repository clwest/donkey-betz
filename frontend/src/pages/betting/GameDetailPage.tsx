import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  ArrowLeft, Activity, Brain, Target,
  Clock, MapPin, Thermometer, AlertTriangle, Trophy,
  Newspaper, PlayCircle, Shield,
  RefreshCw, Wifi, Plus, Minus, X
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { formatDistanceToNow } from 'date-fns';

// Import API functions
import { getGameById, getGameOdds, getWeatherData, getInjuryData, getBettingIntelligence } from '../../features/sports/api/sports';
import type { Game } from '../../features/sports/api/sports';

interface GameData {
  game: Game;
  odds: any;
  weather: any;
  injuries: any;
  intelligence: any;
  last_update: string;
}

interface BettingOption {
  id: string;
  name: string;
  odds: number;
  line?: number;
  implied_prob?: number;
  sportsbook?: string;
}

interface BetSlipItem {
  option: BettingOption;
  stake: number;
  market: string;
}

export const GameDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [gameData, setGameData] = useState<GameData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const [betSlip, setBetSlip] = useState<BetSlipItem[]>([]);
  const [bankroll, setBankroll] = useState(5000);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // WebSocket for live updates
  const { isConnected, sendMessage } = useWebSocket('/ws/sports/updates/', {
    onOpen: () => {
      if (id) {
        sendMessage({
          type: 'subscribe_game',
          game_id: id
        });
      }
    },
    onMessage: (data: any) => {
      if (data.type === 'game_updated' && data.game_id === id) {
        fetchGameData();
      }
    }
  });

  // Comprehensive data fetching
  const fetchGameData = async () => {
    if (!id) return;

    try {
      setLoading(true);

      // Fetch all data in parallel
      const [gameResult, oddsResult] = await Promise.all([
        getGameById(id),
        getGameOdds(id)
      ]);

      // Additional data fetching
      let weatherResult = null;
      let injuryResult = null;
      let intelligenceResult = null;

      if (gameResult.venue_name) {
        weatherResult = await getWeatherData(gameResult.venue_name);
      }

      if (gameResult.home_team_name && gameResult.away_team_name) {
        const [injuries, intelligence] = await Promise.all([
          getInjuryData(gameResult.home_team_name, gameResult.away_team_name),
          getBettingIntelligence(gameResult.home_team_name, gameResult.away_team_name)
        ]);
        injuryResult = injuries;
        intelligenceResult = intelligence;
      }

      setGameData({
        game: gameResult,
        odds: oddsResult,
        weather: weatherResult,
        injuries: injuryResult,
        intelligence: intelligenceResult,
        last_update: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error fetching game data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGameData();

    const interval = autoRefresh ? setInterval(fetchGameData, 30000) : null;
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [id, autoRefresh]);

  // Betting functions
  const addToBetSlip = (option: BettingOption, market: string) => {
    setBetSlip(prev => {
      const exists = prev.find(bet => bet.option.id === option.id);
      if (exists) {
        return prev.filter(bet => bet.option.id !== option.id);
      } else {
        return [...prev, { option, stake: 25, market }];
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
    return betSlip.reduce((sum, bet) => sum + bet.stake, 0);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-card">
        <div className="flex items-center justify-center min-h-screen">
          <div className="bg-card p-12">
            <div className="bg-card"></div>
            <div className="text-center">
              <div className="bg-card w-16 h-16 mx-auto mb-6"></div>
              <h3 className="text-xl font-bold bg-card">Loading Game Data...</h3>
              <p className="bg-card mt-2">Gathering intelligence from multiple sources</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!gameData?.game) {
    return (
      <div className="min-h-screen bg-card p-8">
        <div className="max-w-7xl mx-auto">
          <Button onClick={() => navigate('/betting')} className="mb-8 bg-card">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Sports Board
          </Button>
          <div className="bg-card p-16 text-center">
            <div className="bg-card"></div>
            <h3 className="text-2xl font-bold bg-card mb-4">Game Not Found</h3>
            <p className="bg-card">Unable to load game data</p>
          </div>
        </div>
      </div>
    );
  }

  const game = gameData.game;
  const isLive = game.status === 'live';

  return (
    <div className="min-h-screen bg-card">
      <div className="max-w-[1920px] mx-auto">

        {/* Header Strip */}
        <div className="border-b border-bg-card bg-bg-card/95 backdrop-blur sticky top-0 z-50">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  onClick={() => navigate('/betting')}
                  variant="ghost"
                  size="sm"
                  className="bg-card hover:bg-card"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Sports Board
                </Button>

                <Separator orientation="vertical" className="h-6" />

                <div className="flex items-center gap-3">
                  <div className="text-2xl">
                    {game.league_name?.toLowerCase().includes('football') ? '🏈' :
                     game.league_name?.toLowerCase().includes('basketball') ? '🏀' : '⚽'}
                  </div>
                  <div>
                    <h1 className="text-lg font-bold bg-card">
                      {game.away_team_name} @ {game.home_team_name}
                    </h1>
                    <div className="text-sm bg-card">
                      {game.league_name} • {new Date(game.scheduled_start).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                {isLive && (
                  <div className="flex items-center gap-2 px-3 py-1 bg-red-500/20 border border-red-500/50 rounded-full">
                    <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-red-500">LIVE</span>
                  </div>
                )}

                {isConnected && (
                  <div className="flex items-center gap-2 bg-card">
                    <Wifi className="w-4 h-4" />
                    <span className="text-sm">Connected</span>
                  </div>
                )}

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={autoRefresh ? 'bg-card' : 'bg-card'}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
                  {autoRefresh ? 'Auto' : 'Manual'}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-12 gap-6 p-6 min-h-screen">

          {/* Left Sidebar - Navigation & Quick Stats */}
          <div className="col-span-2 space-y-4">

            {/* Navigation */}
            <Card className="bg-card">
              <div className="bg-card"></div>
              <CardContent className="p-4">
                <div className="space-y-2">
                  {[
                    { id: 'dashboard', icon: Activity, label: 'Dashboard' },
                    { id: 'betting', icon: Target, label: 'Betting' },
                    { id: 'analysis', icon: Brain, label: 'AI Analysis' },
                    { id: 'news', icon: Newspaper, label: 'News & Intel' },
                    { id: 'live', icon: PlayCircle, label: 'Live Data' },
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setActiveView(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all ${
                        activeView === item.id
                          ? 'bg-bg-card/20 border border-bg-card/50 bg-card'
                          : 'hover:bg-bg-card/30 bg-card hover:bg-card'
                      }`}
                    >
                      <item.icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{item.label}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Game Status */}
            <Card className="bg-card">
              <div className="bg-card"></div>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-xs bg-card mb-2">GAME STATUS</div>

                  {isLive && game.home_score !== null && game.away_score !== null ? (
                    <div>
                      <div className="text-2xl font-bold bg-card mb-1">
                        {game.away_score} - {game.home_score}
                      </div>
                      <div className="text-xs bg-card">
                        Q{game.current_period || '1'} • {game.time_remaining || '15:00'}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="text-lg font-bold bg-card mb-1">
                        {new Date(game.scheduled_start).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                      <div className="text-xs bg-card">
                        {formatDistanceToNow(new Date(game.scheduled_start), { addSuffix: true })}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Bet Slip Summary */}
            {betSlip.length > 0 && (
              <Card className="bg-card">
                <div className="bg-card"></div>
                <CardContent className="p-4">
                  <div className="text-center">
                    <div className="text-xs bg-card mb-2">BET SLIP</div>
                    <div className="text-sm font-bold bg-card mb-1">
                      {betSlip.length} Selection{betSlip.length !== 1 ? 's' : ''}
                    </div>
                    <div className="text-xs bg-card">
                      ${getTotalStake()} Total Stake
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Main Content Area */}
          <div className="col-span-8">

            {activeView === 'dashboard' && <DashboardView gameData={gameData} />}
            {activeView === 'betting' && (
              <BettingView
                gameData={gameData}
                betSlip={betSlip}
                onAddToBetSlip={addToBetSlip}
                onUpdateStake={updateStake}
                isInBetSlip={isInBetSlip}
                bankroll={bankroll}
                setBankroll={setBankroll}
              />
            )}
            {activeView === 'analysis' && <AnalysisView gameData={gameData} />}
            {activeView === 'news' && <NewsView gameData={gameData} />}
            {activeView === 'live' && <LiveView gameData={gameData} />}
          </div>

          {/* Right Sidebar - Contextual Information */}
          <div className="col-span-2 space-y-4">

            {/* Weather */}
            <Card className="bg-card">
              <div className="bg-card"></div>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-xs bg-card mb-2">CONDITIONS</div>
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Thermometer className="w-4 h-4 bg-card" />
                    <span className="text-sm font-bold bg-card">
                      {gameData.weather?.temperature || 72}°F
                    </span>
                  </div>
                  <div className="text-xs bg-card">
                    {gameData.weather?.condition || 'Clear'}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Key Stats */}
            <Card className="bg-card">
              <div className="bg-card"></div>
              <CardContent className="p-4">
                <div className="text-xs bg-card mb-3">TEAM RECORDS</div>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs bg-card font-medium mb-1">
                      {game.away_team_name}
                    </div>
                    <div className="text-xs bg-card">
                      {game.away_team?.current_record?.wins || 0}-{game.away_team?.current_record?.losses || 0}
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <div className="text-xs bg-card font-medium mb-1">
                      {game.home_team_name}
                    </div>
                    <div className="text-xs bg-card">
                      {game.home_team?.current_record?.wins || 0}-{game.home_team?.current_record?.losses || 0}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Confidence */}
            <Card className="bg-card">
              <div className="bg-card"></div>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-xs bg-card mb-2">AI CONFIDENCE</div>
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-bg-card/20 flex items-center justify-center border border-bg-card/50">
                    <Brain className="w-5 h-5 text-bg-card" />
                  </div>
                  <div className="text-lg font-bold text-bg-card">87%</div>
                  <div className="text-xs bg-card">Analysis Ready</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard View Component
const DashboardView: React.FC<{ gameData: GameData }> = ({ gameData }) => {
  const game = gameData.game;

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-black bg-card mb-2">
              GAME COMMAND CENTER
            </h2>
            <p className="bg-card">
              Comprehensive betting intelligence for {game.away_team_name} @ {game.home_team_name}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-8 items-center">
            {/* Away Team */}
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-bg-card/30 flex items-center justify-center border border-bg-card">
                <span className="text-2xl font-bold bg-card">
                  {(game.away_team_abbreviation || game.away_team_name?.substring(0, 3) || 'AWY').toUpperCase()}
                </span>
              </div>
              <h3 className="text-xl font-bold bg-card mb-1">{game.away_team_name}</h3>
              <p className="bg-card">
                {game.away_team?.current_record?.wins || 0}-{game.away_team?.current_record?.losses || 0}
              </p>
              {game.away_score !== null && (
                <div className="text-4xl font-bold bg-card mt-3">
                  {game.away_score}
                </div>
              )}
            </div>

            {/* Center - Game Info */}
            <div className="text-center">
              <div className="bg-card text-6xl font-bold mb-4">VS</div>
              <div className="space-y-2">
                <div className="text-sm bg-card">
                  {new Date(game.scheduled_start).toLocaleDateString()}
                </div>
                <div className="text-sm bg-card">
                  {new Date(game.scheduled_start).toLocaleTimeString()}
                </div>
                <div className="flex items-center justify-center gap-2 text-sm bg-card">
                  <MapPin className="w-4 h-4" />
                  {game.venue_name}
                </div>
              </div>
            </div>

            {/* Home Team */}
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-bg-card/30 flex items-center justify-center border border-bg-card">
                <span className="text-2xl font-bold bg-card">
                  {(game.home_team_abbreviation || game.home_team_name?.substring(0, 3) || 'HOM').toUpperCase()}
                </span>
              </div>
              <h3 className="text-xl font-bold bg-card mb-1">{game.home_team_name}</h3>
              <p className="bg-card">
                {game.home_team?.current_record?.wins || 0}-{game.home_team?.current_record?.losses || 0}
              </p>
              {game.home_score !== null && (
                <div className="text-4xl font-bold bg-card mt-3">
                  {game.home_score}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Intelligence Grid */}
      <div className="grid grid-cols-2 gap-6">

        {/* Betting Intelligence */}
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 bg-card">
              <Brain className="w-5 h-5" />
              Betting Intelligence
            </CardTitle>
          </CardHeader>
          <CardContent>
            {gameData.intelligence?.trends?.slice(0, 3).map((trend: any, idx: number) => (
              <div key={idx} className="mb-4 p-3 bg-bg-card/20 rounded-lg border border-bg-card/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-bg-card rounded-full"></div>
                  <span className="text-sm font-medium bg-card">
                    {trend.category?.toUpperCase() || 'ANALYSIS'}
                  </span>
                </div>
                <p className="text-sm bg-card">{trend.text}</p>
              </div>
            )) || (
              <div className="text-center py-8">
                <Brain className="w-12 h-12 mx-auto mb-4 bg-card" />
                <p className="bg-card">AI analysis loading...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Injury Report */}
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 bg-card">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Injury Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            {gameData.injuries?.injuries?.slice(0, 3).map((injury: any, idx: number) => (
              <div key={idx} className="mb-4 p-3 bg-bg-card/20 rounded-lg border border-bg-card/30">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium bg-card">
                    {injury.player}
                  </span>
                  <Badge
                    className={`text-xs ${
                      injury.status === 'Out' ? 'bg-red-500/20 text-red-500' :
                      injury.status === 'Doubtful' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-yellow-500/20 text-yellow-500'
                    }`}
                  >
                    {injury.status}
                  </Badge>
                </div>
                <div className="text-xs bg-card">
                  {injury.team} • {injury.position} • {injury.injury}
                </div>
              </div>
            )) || (
              <div className="text-center py-8">
                <Shield className="w-12 h-12 mx-auto mb-4 bg-card" />
                <p className="bg-card">No injury reports available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Betting View Component
const BettingView: React.FC<{
  gameData: GameData;
  betSlip: BetSlipItem[];
  onAddToBetSlip: (option: BettingOption, market: string) => void;
  onUpdateStake: (optionId: string, stake: number) => void;
  isInBetSlip: (optionId: string) => boolean;
  bankroll: number;
  setBankroll: (amount: number) => void;
}> = ({ gameData, betSlip, onAddToBetSlip, onUpdateStake, isInBetSlip }) => {

  const [activeMarket, setActiveMarket] = useState('moneyline');

  return (
    <div className="space-y-6">
      {/* Market Selection */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardContent className="p-6">
          <div className="grid grid-cols-4 gap-4">
            {['moneyline', 'spread', 'total', 'props'].map((market) => (
              <button
                key={market}
                onClick={() => setActiveMarket(market)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  activeMarket === market
                    ? 'border-bg-card bg-bg-card/10 bg-card'
                    : 'border-bg-card hover:border-bg-card/50 bg-card'
                }`}
              >
                <div className="text-sm font-bold uppercase">
                  {market === 'moneyline' && '💰 Moneyline'}
                  {market === 'spread' && '📊 Spread'}
                  {market === 'total' && '🎯 Total'}
                  {market === 'props' && '🎲 Props'}
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Betting Options */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardContent className="p-6">
          <h3 className="text-xl font-bold bg-card mb-6">
            {activeMarket.charAt(0).toUpperCase() + activeMarket.slice(1)} Betting
          </h3>

          <div className="space-y-4">
            {/* Mock betting options - replace with real data */}
            {[
              { id: 'home_ml', name: gameData.game.home_team_name, odds: -150, market: 'moneyline' },
              { id: 'away_ml', name: gameData.game.away_team_name, odds: 130, market: 'moneyline' }
            ].map((option) => (
              <div
                key={option.id}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  isInBetSlip(option.id)
                    ? 'border-bg-card bg-bg-card/5'
                    : 'border-bg-card hover:border-bg-card'
                }`}
                onClick={() => onAddToBetSlip(option as BettingOption, option.market)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-bold bg-card">{option.name}</h4>
                    <p className="text-sm bg-card">Moneyline</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold bg-card">
                      {option.odds > 0 ? `+${option.odds}` : option.odds}
                    </div>
                    <div className="text-sm bg-card">
                      {((option.odds > 0 ? 100 / (option.odds + 100) : Math.abs(option.odds) / (Math.abs(option.odds) + 100)) * 100).toFixed(1)}% implied
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Bet Slip */}
      {betSlip.length > 0 && (
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 bg-card">
              <Target className="w-5 h-5" />
              Bet Slip ({betSlip.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {betSlip.map((bet) => (
                <div key={bet.option.id} className="p-3 bg-bg-card/20 rounded-lg border border-bg-card/30">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <div className="font-medium bg-card">{bet.option.name}</div>
                      <div className="text-sm bg-card">
                        {bet.option.odds > 0 ? `+${bet.option.odds}` : bet.option.odds}
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onUpdateStake(bet.option.id, 0)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onUpdateStake(bet.option.id, bet.stake - 5)}
                    >
                      <Minus className="w-3 h-3" />
                    </Button>

                    <input
                      type="number"
                      value={bet.stake}
                      onChange={(e) => onUpdateStake(bet.option.id, Number(e.target.value))}
                      className="flex-1 px-3 py-1 text-center bg-card border border-bg-card rounded"
                    />

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onUpdateStake(bet.option.id, bet.stake + 5)}
                    >
                      <Plus className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))}

              <Button className="w-full bg-card">
                <Trophy className="w-4 h-4 mr-2" />
                Place Bets (${betSlip.reduce((sum, bet) => sum + bet.stake, 0)})
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Analysis View Component
const AnalysisView: React.FC<{ gameData: GameData }> = ({ }) => {
  return (
    <div className="space-y-6">
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 bg-card">
            <Brain className="w-5 h-5" />
            AI Analysis Engine
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Brain className="w-16 h-16 mx-auto mb-4 bg-card" />
            <h3 className="text-xl font-bold bg-card mb-2">Deep Analysis Coming Soon</h3>
            <p className="bg-card">Advanced AI-powered game analysis and predictions</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// News View Component
const NewsView: React.FC<{ gameData: GameData }> = ({ }) => {
  return (
    <div className="space-y-6">
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 bg-card">
            <Newspaper className="w-5 h-5" />
            News & Intelligence
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Newspaper className="w-16 h-16 mx-auto mb-4 bg-card" />
            <h3 className="text-xl font-bold bg-card mb-2">News Feed Coming Soon</h3>
            <p className="bg-card">Real-time team news, injury updates, and expert analysis</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Live View Component
const LiveView: React.FC<{ gameData: GameData }> = ({ gameData }) => {
  const isLive = gameData.game.status === 'live';

  return (
    <div className="space-y-6">
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 bg-card">
            <PlayCircle className="w-5 h-5" />
            Live Game Data
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLive ? (
            <div className="text-center py-12">
              <PlayCircle className="w-16 h-16 mx-auto mb-4 text-bg-card animate-pulse" />
              <h3 className="text-xl font-bold bg-card mb-2">Game In Progress</h3>
              <p className="bg-card">Live play-by-play and statistics</p>
            </div>
          ) : (
            <div className="text-center py-12">
              <Clock className="w-16 h-16 mx-auto mb-4 bg-card" />
              <h3 className="text-xl font-bold bg-card mb-2">Game Not Started</h3>
              <p className="bg-card">
                Live data will be available when the game begins
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};