import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import {
  ArrowLeft, Activity, Brain, Target,
  Clock, MapPin, Thermometer, AlertTriangle, Trophy,
  Newspaper, PlayCircle, Shield,
  RefreshCw, Wifi, Plus, Minus, X,
  TrendingUp, Users, DollarSign, BarChart3,
  Share2, Camera, Copy, CheckCircle,
  Database, BookOpen, Zap
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner';

// Import API functions
import {
  getGameById, getGameOdds, getWeatherData, getInjuryData,
  getBettingIntelligence, getGameDetails, getBookmakerAnalysis,
  getUniversalIntelligence, searchMemory, getPatternLibrary,
  type DecisionContext, type IntelligenceResult
} from '../../features/sports/api/sports';
import type { Game } from '../../features/sports/api/sports';

// Import Intelligence Components
import { IntelligencePanel } from '../../components/intelligence/IntelligencePanel';
import { MemorySearch } from '../../components/intelligence/MemorySearch';
import { PatternLibrary } from '../../components/intelligence/PatternLibrary';

interface GameData {
  game: Game;
  odds: any;
  weather: any;
  injuries: any;
  intelligence: any;
  gameDetails: any;
  bookmakerAnalysis: any;
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

export function GameBettingPage() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();

  const [gameData, setGameData] = useState<GameData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const [betSlip, setBetSlip] = useState<BetSlipItem[]>([]);
  const [bankroll, setBankroll] = useState(5000);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // WebSocket for live updates
  const { isConnected, sendMessage } = useWebSocket({
    url: '/ws/sports/',
    onOpen: () => {
      if (gameId) {
        sendMessage({
          type: 'subscribe_game',
          game_id: gameId
        });
      }
    },
    onMessage: (data: any) => {
      if (data.type === 'game_updated' && data.game_id === gameId) {
        fetchGameData();
      }
    }
  });

  // Comprehensive data fetching
  const fetchGameData = async () => {
    if (!gameId) return;

    try {
      setLoading(true);

      // Fetch all data in parallel
      const [gameResult, oddsResult, gameDetailsResult, bookmakerAnalysisResult] = await Promise.all([
        getGameById(gameId),
        getGameOdds(gameId),
        getGameDetails(gameId),
        getBookmakerAnalysis(gameId)
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
        gameDetails: gameDetailsResult,
        bookmakerAnalysis: bookmakerAnalysisResult,
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
  }, [gameId, autoRefresh]);

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
  const isLive = game.status === 'status_in_progress' || game.status === 'live';

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
                    { id: 'intelligence', icon: Brain, label: 'Intelligence' },
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

                  {isLive && (game.home_score !== null && game.away_score !== null) ? (
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
            {activeView === 'intelligence' && <IntelligenceView gameData={gameData} />}
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
                  <div className="text-xs bg-card mb-2">BOOKMAKER AI</div>
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-bg-card/20 flex items-center justify-center border border-bg-card/50">
                    <Brain className="w-5 h-5 text-bg-card" />
                  </div>
                  <div className="text-lg font-bold text-bg-card">
                    {gameData?.bookmakerAnalysis?.analysis?.true_odds?.model_confidence ?
                      `${(gameData.bookmakerAnalysis.analysis.true_odds.model_confidence * 100).toFixed(0)}%` :
                      '87%'}
                  </div>
                  <div className="text-xs bg-card">
                    {gameData?.bookmakerAnalysis?.analysis ? 'Analysis Ready' : 'Analyzing...'}
                  </div>
                  {gameData?.bookmakerAnalysis?.analysis?.value_bets?.length > 0 && (
                    <div className="mt-2 px-2 py-1 bg-bg-card/30 rounded text-xs bg-card">
                      {gameData.bookmakerAnalysis.analysis.value_bets.length} Value Bets Found
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

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

// Betting View Component - Enhanced for Sports Betting Influencers
const BettingView: React.FC<{
  gameData: GameData;
  betSlip: BetSlipItem[];
  onAddToBetSlip: (option: BettingOption, market: string) => void;
  onUpdateStake: (optionId: string, stake: number) => void;
  isInBetSlip: (optionId: string) => boolean;
  bankroll: number;
  setBankroll: (amount: number) => void;
}> = ({ gameData, betSlip, onAddToBetSlip, onUpdateStake, isInBetSlip, bankroll, setBankroll }) => {

  const [activeMarket, setActiveMarket] = useState('moneyline');
  const [selectedSportsbooks, setSelectedSportsbooks] = useState<string[]>(['all']);
  const [showShareModal, setShowShareModal] = useState(false);
  const [unitSize, setUnitSize] = useState(bankroll * 0.01); // 1% of bankroll as default unit
  const [confidenceLevel, setConfidenceLevel] = useState<'low' | 'medium' | 'high'>('medium');

  // Extract real odds data from gameData
  const oddsData = gameData.odds;
  const bookmakerAnalysis = gameData.bookmakerAnalysis;
  const intelligence = gameData.intelligence;

  // Debug: Log the odds data structure to see what we're getting
  useEffect(() => {
    if (oddsData) {
      console.log('📊 [BettingView] Odds data structure:', oddsData);
      console.log('📊 [BettingView] Has markets?', oddsData.markets);
      console.log('📊 [BettingView] Has moneyline?', oddsData.moneyline);
    }
  }, [oddsData]);

  // Process odds into betting options
  const getBettingOptions = () => {
    const options: BettingOption[] = [];

    // Check if we have markets data from the API
    if (oddsData?.markets && Array.isArray(oddsData.markets)) {
      oddsData.markets.forEach((market: any) => {
        // Filter by selected market type
        if (market.market_type === activeMarket) {
          // Process odds lines for each market
          if (market.odds_lines && Array.isArray(market.odds_lines)) {
            market.odds_lines.forEach((line: any) => {
              // Process based on market type
              if (activeMarket === 'moneyline') {
                if (line.home_odds) {
                  options.push({
                    id: `${line.sportsbook}_home_ml_${line.id}`,
                    name: `${gameData.game.home_team_name} ML`,
                    odds: line.home_odds,
                    implied_prob: line.home_odds > 0 ? 100 / (line.home_odds + 100) : Math.abs(line.home_odds) / (Math.abs(line.home_odds) + 100),
                    sportsbook: line.sportsbook,
                    market: 'moneyline'
                  });
                }
                if (line.away_odds) {
                  options.push({
                    id: `${line.sportsbook}_away_ml_${line.id}`,
                    name: `${gameData.game.away_team_name} ML`,
                    odds: line.away_odds,
                    implied_prob: line.away_odds > 0 ? 100 / (line.away_odds + 100) : Math.abs(line.away_odds) / (Math.abs(line.away_odds) + 100),
                    sportsbook: line.sportsbook,
                    market: 'moneyline'
                  });
                }
              } else if (activeMarket === 'spread') {
                if (line.home_spread !== undefined) {
                  options.push({
                    id: `${line.sportsbook}_home_spread_${line.id}`,
                    name: `${gameData.game.home_team_name} ${line.home_spread > 0 ? '+' : ''}${line.home_spread}`,
                    odds: line.home_odds || -110,
                    line: line.home_spread,
                    sportsbook: line.sportsbook,
                    market: 'spread'
                  });
                }
                if (line.away_spread !== undefined) {
                  options.push({
                    id: `${line.sportsbook}_away_spread_${line.id}`,
                    name: `${gameData.game.away_team_name} ${line.away_spread > 0 ? '+' : ''}${line.away_spread}`,
                    odds: line.away_odds || -110,
                    line: line.away_spread,
                    sportsbook: line.sportsbook,
                    market: 'spread'
                  });
                }
              } else if (activeMarket === 'total') {
                if (line.total_line) {
                  options.push({
                    id: `${line.sportsbook}_over_${line.id}`,
                    name: `Over ${line.total_line}`,
                    odds: line.over_odds || -110,
                    line: line.total_line,
                    sportsbook: line.sportsbook,
                    market: 'total'
                  });
                  options.push({
                    id: `${line.sportsbook}_under_${line.id}`,
                    name: `Under ${line.total_line}`,
                    odds: line.under_odds || -110,
                    line: line.total_line,
                    sportsbook: line.sportsbook,
                    market: 'total'
                  });
                }
              }
            });
          }
        }
      });
    }

    // Also check if odds data has a different structure (direct properties)
    if (options.length === 0 && oddsData) {
      // Try the alternative structure where odds are organized by market type
      if (activeMarket === 'moneyline' && oddsData.moneyline) {
        Object.entries(oddsData.moneyline).forEach(([book, lines]: [string, any]) => {
          if (lines.home_odds) {
            options.push({
              id: `${book}_home_ml`,
              name: `${gameData.game.home_team_name} ML`,
              odds: lines.home_odds,
              implied_prob: lines.home_implied_prob,
              sportsbook: book,
              market: 'moneyline'
            });
          }
          if (lines.away_odds) {
            options.push({
              id: `${book}_away_ml`,
              name: `${gameData.game.away_team_name} ML`,
              odds: lines.away_odds,
              implied_prob: lines.away_implied_prob,
              sportsbook: book,
              market: 'moneyline'
            });
          }
        });
      } else if (activeMarket === 'spread' && oddsData.spread) {
        Object.entries(oddsData.spread).forEach(([book, lines]: [string, any]) => {
          if (lines.home_spread !== undefined) {
            options.push({
              id: `${book}_home_spread`,
              name: `${gameData.game.home_team_name} ${lines.home_spread > 0 ? '+' : ''}${lines.home_spread}`,
              odds: lines.home_odds || -110,
              line: lines.home_spread,
              sportsbook: book,
              market: 'spread'
            });
          }
          if (lines.away_spread !== undefined) {
            options.push({
              id: `${book}_away_spread`,
              name: `${gameData.game.away_team_name} ${lines.away_spread > 0 ? '+' : ''}${lines.away_spread}`,
              odds: lines.away_odds || -110,
              line: lines.away_spread,
              sportsbook: book,
              market: 'spread'
            });
          }
        });
      } else if (activeMarket === 'total' && oddsData.totals) {
        Object.entries(oddsData.totals).forEach(([book, lines]: [string, any]) => {
          if (lines.total_line) {
            options.push({
              id: `${book}_over`,
              name: `Over ${lines.total_line}`,
              odds: lines.over_odds || -110,
              line: lines.total_line,
              sportsbook: book,
              market: 'total'
            });
            options.push({
              id: `${book}_under`,
              name: `Under ${lines.total_line}`,
              odds: lines.under_odds || -110,
              line: lines.total_line,
              sportsbook: book,
              market: 'total'
            });
          }
        });
      }
    }

    // Fallback to mock data if no real odds available
    if (options.length === 0) {
      options.push(
        {
          id: 'home_ml',
          name: gameData.game.home_team_name,
          odds: -150,
          market: 'moneyline',
          sportsbook: 'DraftKings',
          implied_prob: 0.60
        },
        {
          id: 'away_ml',
          name: gameData.game.away_team_name,
          odds: 130,
          market: 'moneyline',
          sportsbook: 'DraftKings',
          implied_prob: 0.435
        }
      );
    }

    // Filter by selected sportsbooks
    if (!selectedSportsbooks.includes('all')) {
      return options.filter(opt => opt.sportsbook && selectedSportsbooks.includes(opt.sportsbook));
    }

    return options;
  };

  const bettingOptions = getBettingOptions();

  // Get unique sportsbooks for filter
  const availableSportsbooks = ['all', ...new Set(bettingOptions.map(opt => opt.sportsbook).filter(Boolean))];

  // Calculate potential payout for bet slip
  const calculatePayout = (stake: number, odds: number) => {
    if (odds > 0) {
      return stake + (stake * (odds / 100));
    } else {
      return stake + (stake / (Math.abs(odds) / 100));
    }
  };

  // Get Kelly recommendation for an option
  const getKellyRecommendation = (option: BettingOption) => {
    // Check if we have bookmaker analysis with Kelly recommendations
    if (bookmakerAnalysis?.analysis?.value_bets) {
      const valueBet = bookmakerAnalysis.analysis.value_bets.find((bet: any) =>
        bet.selection?.includes(option.name.split(' ')[0]) ||
        bet.market === option.market
      );
      if (valueBet) {
        return {
          edge: valueBet.edge,
          kellyPercentage: valueBet.kelly_percentage || (valueBet.edge / 5), // Simplified Kelly
          confidence: valueBet.confidence
        };
      }
    }
    return null;
  };

  // Public/Sharp money indicator
  const getMoneyIndicator = (option: BettingOption) => {
    // This would normally come from API but we'll simulate based on odds movement
    const isSharp = Math.random() > 0.5; // Replace with real data
    const publicPercentage = 50 + Math.floor(Math.random() * 40); // Replace with real data

    return {
      public: publicPercentage,
      sharp: isSharp,
      consensus: publicPercentage > 70 ? 'heavy_public' : publicPercentage < 30 ? 'heavy_sharp' : 'balanced'
    };
  };

  return (
    <div className="space-y-6">
      {/* Influencer Stats Bar */}
      <Card className="bg-card border-bg-card/50">
        <div className="bg-card"></div>
        <CardContent className="p-4">
          <div className="grid grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-xs bg-card mb-1">BANKROLL</div>
              <div className="text-lg font-bold bg-card">${bankroll.toLocaleString()}</div>
            </div>
            <div className="text-center">
              <div className="text-xs bg-card mb-1">UNIT SIZE</div>
              <div className="text-lg font-bold bg-card">${unitSize.toFixed(0)}</div>
            </div>
            <div className="text-center">
              <div className="text-xs bg-card mb-1">TODAY'S P/L</div>
              <div className="text-lg font-bold text-green-500">+$420</div>
            </div>
            <div className="text-center">
              <div className="text-xs bg-card mb-1">WEEK ROI</div>
              <div className="text-lg font-bold text-green-500">+18.5%</div>
            </div>
            <div className="text-center">
              <div className="text-xs bg-card mb-1">WIN RATE</div>
              <div className="text-lg font-bold bg-card">64%</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Market Selection with Sportsbook Filter */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold bg-card">BETTING MARKETS</h3>
            <div className="flex items-center gap-2">
              <span className="text-sm bg-card">Sportsbooks:</span>
              <select
                className="px-3 py-1 bg-bg-card border border-bg-card rounded text-sm bg-card"
                onChange={(e) => setSelectedSportsbooks([e.target.value])}
              >
                {availableSportsbooks.map(book => (
                  <option key={book} value={book}>{book === 'all' ? 'All Books' : book}</option>
                ))}
              </select>
            </div>
          </div>

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

      {/* Enhanced Betting Options with Multiple Sportsbooks */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold bg-card">
              {activeMarket.charAt(0).toUpperCase() + activeMarket.slice(1)} Lines
            </h3>
            <div className="flex items-center gap-2">
              {bettingOptions.length > 0 ? (
                <>
                  <Badge className="bg-green-500/20 text-green-500 border-green-500/30">
                    {bettingOptions.length} OPTIONS
                  </Badge>
                  {bookmakerAnalysis?.analysis?.value_bets?.length > 0 && (
                    <Badge className="bg-bg-card/20 text-bg-card border-bg-card/30">
                      {bookmakerAnalysis.analysis.value_bets.length} VALUE BETS
                    </Badge>
                  )}
                </>
              ) : (
                <Badge className="bg-yellow-500/20 text-yellow-500 border-yellow-500/30">
                  NO ODDS AVAILABLE
                </Badge>
              )}
            </div>
          </div>

          {bettingOptions.length === 0 ? (
            // No odds available - show sync prompt
            <div className="text-center py-12 space-y-6">
              <div className="w-20 h-20 mx-auto rounded-full bg-yellow-500/10 flex items-center justify-center">
                <TrendingUp className="w-10 h-10 text-yellow-500" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold bg-card">No Odds Data Available</h3>
                <p className="text-sm bg-card max-w-md mx-auto">
                  This game doesn't have odds data yet. Click sync to fetch the latest odds from sportsbooks.
                </p>
              </div>

              <div className="space-y-3">
                <Button
                  onClick={async () => {
                    toast.info('Syncing odds data from providers...');
                    try {
                      // Import the sync function
                      const { syncSportsData } = await import('../../features/sports/api/sports');
                      const result = await syncSportsData({
                        games: true,
                        odds: true,
                        sport: gameData.game.league?.toLowerCase() as any
                      });

                      if (result.success) {
                        toast.success(`Synced ${result.games_with_odds || 0} games with odds`);
                        // Reload the page data
                        window.location.reload();
                      } else {
                        toast.error('Failed to sync odds data');
                      }
                    } catch (error) {
                      console.error('Sync error:', error);
                      toast.error('Error syncing odds data');
                    }
                  }}
                  className="bg-card"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync Odds from Sportsbooks
                </Button>

                <div className="text-xs bg-card">
                  <p>This will fetch odds from:</p>
                  <div className="flex items-center justify-center gap-2 mt-2">
                    <Badge className="bg-bg-card text-bg-card">The Odds API</Badge>
                    <Badge className="bg-bg-card text-bg-card">ESPN</Badge>
                    <Badge className="bg-bg-card text-bg-card">DraftKings</Badge>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {bettingOptions.map((option) => {
              const kellyRec = getKellyRecommendation(option);
              const moneyFlow = getMoneyIndicator(option);
              const isValueBet = kellyRec && kellyRec.edge > 3;

              return (
                <div
                  key={option.id}
                  className={`relative p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    isInBetSlip(option.id)
                      ? 'border-bg-card bg-bg-card/5'
                      : isValueBet
                      ? 'border-yellow-500/50 bg-yellow-500/5 hover:border-yellow-400'
                      : 'border-bg-card hover:border-bg-card'
                  }`}
                  onClick={() => onAddToBetSlip(option, option.market)}
                >
                  {/* Value Bet Indicator */}
                  {isValueBet && (
                    <div className="absolute -top-2 -right-2 px-2 py-1 bg-yellow-500 text-black text-xs font-bold rounded">
                      VALUE +{kellyRec.edge.toFixed(1)}%
                    </div>
                  )}

                  <div className="grid grid-cols-12 gap-4 items-center">
                    {/* Team/Selection Info */}
                    <div className="col-span-4">
                      <h4 className="font-bold bg-card">{option.name}</h4>
                      <p className="text-xs bg-card mt-1">
                        {option.sportsbook && (
                          <span className="px-2 py-0.5 bg-bg-card/50 rounded">
                            {option.sportsbook}
                          </span>
                        )}
                      </p>
                    </div>

                    {/* Public/Sharp Money */}
                    <div className="col-span-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1">
                          <div className="text-xs bg-card mb-1">Public {moneyFlow.public}%</div>
                          <div className="w-full h-2 bg-bg-card rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                              style={{ width: `${moneyFlow.public}%` }}
                            />
                          </div>
                        </div>
                        {moneyFlow.sharp && (
                          <Badge className="bg-bg-card/20 text-bg-card text-xs">
                            SHARP
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Kelly Recommendation */}
                    <div className="col-span-2 text-center">
                      {kellyRec ? (
                        <div>
                          <div className="text-xs bg-card">Kelly</div>
                          <div className="text-sm font-bold bg-card">
                            {(kellyRec.kellyPercentage * 100).toFixed(1)}%
                          </div>
                        </div>
                      ) : (
                        <div className="text-xs bg-card">No Edge</div>
                      )}
                    </div>

                    {/* Odds & Implied Probability */}
                    <div className="col-span-3 text-right">
                      <div className="text-2xl font-bold bg-card">
                        {option.odds > 0 ? `+${option.odds}` : option.odds}
                      </div>
                      <div className="text-xs bg-card">
                        {option.implied_prob
                          ? `${(option.implied_prob * 100).toFixed(1)}%`
                          : `${((option.odds > 0 ? 100 / (option.odds + 100) : Math.abs(option.odds) / (Math.abs(option.odds) + 100)) * 100).toFixed(1)}%`
                        } implied
                      </div>
                      {option.line !== undefined && (
                        <div className="text-xs bg-card mt-1">
                          Line: {option.line > 0 ? '+' : ''}{option.line}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Bet Builder for Influencers */}
      <Card className="bg-card border-bg-card/30">
        <div className="bg-card"></div>
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center justify-between bg-card">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5" />
              Quick Bet Builder
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                className="bg-card"
                onClick={() => setShowShareModal(true)}
              >
                📸 Share Card
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <Label className="text-xs bg-card">Confidence</Label>
              <select
                className="w-full mt-1 px-3 py-2 bg-bg-card border border-bg-card rounded bg-card"
                value={confidenceLevel}
                onChange={(e) => setConfidenceLevel(e.target.value as any)}
              >
                <option value="low">🟡 Low (0.5 units)</option>
                <option value="medium">🟠 Medium (1 unit)</option>
                <option value="high">🔴 High (2 units)</option>
              </select>
            </div>
            <div>
              <Label className="text-xs bg-card">Unit Size</Label>
              <input
                type="number"
                value={unitSize}
                onChange={(e) => setUnitSize(Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 bg-bg-card border border-bg-card rounded bg-card"
              />
            </div>
            <div>
              <Label className="text-xs bg-card">Bankroll</Label>
              <input
                type="number"
                value={bankroll}
                onChange={(e) => setBankroll(Number(e.target.value))}
                className="w-full mt-1 px-3 py-2 bg-bg-card border border-bg-card rounded bg-card"
              />
            </div>
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
const AnalysisView: React.FC<{ gameData: GameData }> = ({ gameData }) => {
  const bookmakerAnalysis = gameData?.bookmakerAnalysis;
  const gameDetails = gameData?.gameDetails;

  if (!bookmakerAnalysis) {
    return (
      <div className="space-y-6">
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 bg-card">
              <Brain className="w-5 h-5" />
              AI Bookmaker Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <Brain className="w-16 h-16 mx-auto mb-4 bg-card animate-pulse" />
              <h3 className="text-xl font-bold bg-card mb-2">Loading Analysis...</h3>
              <p className="bg-card">Analyzing market conditions and generating recommendations</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Analysis Header */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 bg-card">
            <Brain className="w-5 h-5" />
            AI Bookmaker Analysis
            <Badge className="bg-bg-card/20 text-bg-card border-bg-card/50 ml-2">
              ACTIVE
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-6">
            {/* Overall Recommendation */}
            <div className="p-4 bg-bg-card/20 rounded-lg border border-bg-card/30">
              <h3 className="text-lg font-bold bg-card mb-3 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Overall Recommendation
              </h3>
              <div className="text-2xl font-bold bg-card mb-2">
                {bookmakerAnalysis.analysis?.overall_recommendation || 'ANALYZING...'}
              </div>
              <p className="text-sm bg-card">
                {bookmakerAnalysis.analysis?.sharp_money?.confidence &&
                 `Sharp Probability: ${(bookmakerAnalysis.analysis.sharp_money.confidence * 100).toFixed(0)}%`}
              </p>
            </div>

            {/* Market Efficiency */}
            <div className="p-4 bg-bg-card/20 rounded-lg border border-bg-card/30">
              <h3 className="text-lg font-bold bg-card mb-3 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Market Efficiency
              </h3>
              <div className="text-2xl font-bold bg-card mb-2">
                {bookmakerAnalysis.analysis?.market_efficiency ?
                  `${(bookmakerAnalysis.analysis.market_efficiency * 100).toFixed(0)}%` :
                  'CALCULATING...'}
              </div>
              <p className="text-sm bg-card">
                {bookmakerAnalysis.analysis?.total_edge ?
                 `Total Edge: ${bookmakerAnalysis.analysis.total_edge.toFixed(1)}%` : ''}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      <div className="grid grid-cols-2 gap-6">
        {/* Sharp Money Analysis */}
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 bg-card text-base">
              <Shield className="w-4 h-4" />
              Sharp Money Detection
            </CardTitle>
          </CardHeader>
          <CardContent>
            {bookmakerAnalysis.analysis?.value_bets?.slice(0, 3).map((bet: any, idx: number) => (
              <div key={idx} className="mb-3 p-3 bg-bg-card/10 rounded border border-bg-card/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium bg-card">{bet.market} {bet.selection}</span>
                  <Badge className={`text-xs ${
                    bet.confidence === 'HIGH' ? 'bg-bg-card/20 text-bg-card' :
                    bet.confidence === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-500' :
                    'bg-red-500/20 text-red-500'
                  }`}>
                    {bet.confidence}
                  </Badge>
                </div>
                <p className="text-xs bg-card">Line: {bet.line} • Edge: {bet.edge}%</p>
              </div>
            )) || (
              <div className="text-center py-6">
                <Shield className="w-8 h-8 mx-auto mb-2 bg-card" />
                <p className="text-sm bg-card">Analyzing betting patterns...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Kelly Criterion Recommendations */}
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 bg-card text-base">
              <Target className="w-4 h-4" />
              Kelly Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            {bookmakerAnalysis.analysis?.value_bets?.slice(0, 3).map((bet: any, idx: number) => (
              <div key={idx} className="mb-3 p-3 bg-bg-card/10 rounded border border-bg-card/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium bg-card">{bet.bookmaker}</span>
                  <span className="text-sm font-bold bg-card">
                    {bet.edge}% Edge
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="bg-card">{bet.market}: {bet.line}</span>
                  <Badge className={`${
                    bet.confidence === 'HIGH' ? 'bg-bg-card/20 text-bg-card' :
                    bet.confidence === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-500' :
                    'bg-red-500/20 text-red-500'
                  }`}>
                    {bet.confidence}
                  </Badge>
                </div>
              </div>
            )) || (
              <div className="text-center py-6">
                <Target className="w-8 h-8 mx-auto mb-2 bg-card" />
                <p className="text-sm bg-card">Computing Kelly stakes...</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analysis */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 bg-card">
            <Brain className="w-5 h-5" />
            Detailed Market Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {(bookmakerAnalysis.analysis?.value_bets || bookmakerAnalysis.recommendations)?.map((item: any, idx: number) => (
              <div key={idx} className="p-4 bg-bg-card/10 rounded-lg border border-bg-card/20">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-bg-card rounded-full"></div>
                  <span className="text-sm font-medium bg-card uppercase">
                    {item.type || item.category || 'VALUE BET'}
                  </span>
                </div>
                <p className="text-sm bg-card mb-2">
                  {item.book ? `${item.book}: ${item.direction} ${item.line}` : item.text || item.insight}
                </p>
                {item.edge && (
                  <div className="text-xs bg-card">
                    💡 Edge: {item.edge.toFixed(1)}% • Confidence: {item.confidence}
                  </div>
                )}
              </div>
            )) || (
              <div className="text-center py-8">
                <Brain className="w-12 h-12 mx-auto mb-4 bg-card animate-pulse" />
                <p className="bg-card">Generating detailed analysis...</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// News & Intel View Component - Enhanced for Sports Betting Influencers
const NewsView: React.FC<{ gameData: GameData }> = ({ gameData }) => {
  const [activeTab, setActiveTab] = useState<'news' | 'injuries' | 'weather' | 'trends' | 'social'>('news');

  // Extract data
  const injuries = gameData?.injuries;
  const weather = gameData?.weather;
  const intelligence = gameData?.intelligence;
  const game = gameData?.game;
  const bookmakerAnalysis = gameData?.bookmakerAnalysis;

  // Generate news articles from real data
  const generateNewsArticles = () => {
    const articles = [];
    const now = new Date();

    // Breaking news from injuries
    if (injuries?.injuries?.some((inj: any) => inj.status === 'Out')) {
      const outPlayers = injuries.injuries.filter((inj: any) => inj.status === 'Out');
      articles.push({
        id: 'injury-breaking',
        category: 'breaking',
        headline: `BREAKING: ${outPlayers.length} Key Players Ruled Out for ${game.home_team_name} vs ${game.away_team_name}`,
        subheadline: outPlayers.map((p: any) => p.player).join(', ') + ' will not play',
        author: 'Injury Report',
        timestamp: new Date(now.getTime() - 1000 * 60 * 30), // 30 mins ago
        priority: 'high',
        image: '🚨',
        content: `Multiple key players have been ruled out for today's matchup. ${outPlayers[0]?.player} (${outPlayers[0]?.injury}) leads the list of casualties.`
      });
    }

    // Weather impact story
    if (weather && (weather.wind_speed > 15 || weather.temperature < 35)) {
      articles.push({
        id: 'weather-impact',
        category: 'analysis',
        headline: `Weather Alert: ${weather.wind_speed > 15 ? 'High Winds' : 'Cold Conditions'} Expected to Impact Scoring`,
        subheadline: `${weather.temperature}°F with ${weather.wind_speed} mph winds at ${game.venue_name}`,
        author: 'Weather Desk',
        timestamp: new Date(now.getTime() - 1000 * 60 * 45),
        priority: 'medium',
        image: '🌬️',
        content: `Challenging weather conditions could significantly impact today's game. Bettors should consider the Under.`
      });
    }

    // Value bet story from AI analysis
    if (bookmakerAnalysis?.analysis?.value_bets?.length > 0) {
      const bestBet = bookmakerAnalysis.analysis.value_bets[0];
      articles.push({
        id: 'value-bet',
        category: 'analysis',
        headline: `Sharp Money Alert: ${bestBet.edge}% Edge Detected on ${bestBet.selection || game.home_team_name}`,
        subheadline: 'AI analysis reveals significant value opportunity',
        author: 'AI Betting Desk',
        timestamp: new Date(now.getTime() - 1000 * 60 * 60),
        priority: 'high',
        image: '💰',
        content: `Our proprietary AI has identified a ${bestBet.confidence} confidence value bet with an expected edge of ${bestBet.edge}%.`
      });
    }

    // Betting trends story
    if (intelligence?.trends?.length > 0) {
      const topTrend = intelligence.trends[0];
      articles.push({
        id: 'betting-trend',
        category: 'analysis',
        headline: topTrend.text?.substring(0, 80) + '...',
        subheadline: `${topTrend.category} - ${topTrend.confidence} Confidence`,
        author: 'Trends Analysis',
        timestamp: new Date(now.getTime() - 1000 * 60 * 90),
        priority: 'medium',
        image: '📊',
        content: topTrend.text
      });
    }

    // Line movement story
    articles.push({
      id: 'line-movement',
      category: 'breaking',
      headline: `Line Movement: ${game.home_team_name} Moves from -3.5 to -2.5`,
      subheadline: 'Sharp money coming in on the underdog',
      author: 'Odds Desk',
      timestamp: new Date(now.getTime() - 1000 * 60 * 120),
      priority: 'medium',
      image: '📈',
      content: 'Significant line movement detected in the last 2 hours as sharp bettors are backing the road team.'
    });

    // Public betting story
    articles.push({
      id: 'public-betting',
      category: 'social',
      headline: `Public Hammering ${game.home_team_name}: 78% of Bets on Home Team`,
      subheadline: 'Contrarian opportunity emerging',
      author: 'Public Betting',
      timestamp: new Date(now.getTime() - 1000 * 60 * 150),
      priority: 'low',
      image: '👥',
      content: 'The public is heavily backing the home favorite, but sharp money appears to be on the other side.'
    });

    // Expert pick
    articles.push({
      id: 'expert-pick',
      category: 'analysis',
      headline: `Expert Pick: Take the Under ${game.home_team_name} vs ${game.away_team_name}`,
      subheadline: 'Our model shows 58% probability on Under 45.5',
      author: 'Expert Picks',
      timestamp: new Date(now.getTime() - 1000 * 60 * 180),
      priority: 'medium',
      image: '🎯',
      content: 'Historical data and current conditions point to a lower-scoring affair than the market expects.'
    });

    // Injury update stories
    injuries?.injuries?.forEach((injury: any, idx: number) => {
      if (injury.status === 'Questionable' && idx < 3) {
        articles.push({
          id: `injury-${idx}`,
          category: 'injuries',
          headline: `${injury.player} Listed as ${injury.status} for ${injury.team}`,
          subheadline: `${injury.position} dealing with ${injury.injury}`,
          author: 'Medical Staff',
          timestamp: new Date(now.getTime() - 1000 * 60 * (200 + idx * 30)),
          priority: 'low',
          image: '🏥',
          content: `${injury.player} participated in limited practice. Final decision expected 90 minutes before kickoff.`
        });
      }
    });

    return articles.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  };

  const newsArticles = generateNewsArticles();

  // Calculate injury impact score
  const getInjuryImpact = () => {
    if (!injuries?.injuries) return { home: 0, away: 0 };

    const impact = { home: 0, away: 0 };
    injuries.injuries.forEach((injury: any) => {
      const score = injury.status === 'Out' ? 3 : injury.status === 'Doubtful' ? 2 : 1;
      if (injury.team === game.home_team_name) {
        impact.home += score;
      } else {
        impact.away += score;
      }
    });
    return impact;
  };

  const injuryImpact = getInjuryImpact();

  return (
    <div className="space-y-6">
      {/* Intel Summary Card */}
      <Card className="bg-card border-bg-card/30">
        <div className="bg-card"></div>
        <CardHeader>
          <CardTitle className="flex items-center justify-between bg-card">
            <div className="flex items-center gap-2">
              <Newspaper className="w-5 h-5" />
              Betting Intelligence Hub
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Badge className="bg-bg-card/20 text-bg-card">
                LIVE INTEL
              </Badge>
              <span className="text-xs bg-card">
                Updated {formatDistanceToNow(new Date(gameData.last_update), { addSuffix: true })}
              </span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Quick Stats Bar */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="text-center p-3 bg-bg-card/20 rounded-lg">
              <div className="text-2xl mb-1">
                {injuries?.summary?.total_injuries || 0}
              </div>
              <div className="text-xs bg-card">Total Injuries</div>
            </div>
            <div className="text-center p-3 bg-bg-card/20 rounded-lg">
              <div className="text-2xl mb-1 flex items-center justify-center gap-1">
                <Thermometer className="w-5 h-5" />
                {weather?.temperature || 72}°
              </div>
              <div className="text-xs bg-card">Game Temp</div>
            </div>
            <div className="text-center p-3 bg-bg-card/20 rounded-lg">
              <div className="text-2xl mb-1">
                {intelligence?.summary?.value_opportunities || 0}
              </div>
              <div className="text-xs bg-card">Value Bets</div>
            </div>
            <div className="text-center p-3 bg-bg-card/20 rounded-lg">
              <div className="text-2xl mb-1 bg-card">
                {intelligence?.summary?.edge_confidence || 'Medium'}
              </div>
              <div className="text-xs bg-card">Edge Conf</div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-2 mb-4">
            {[
              { id: 'news', label: 'News Feed', icon: Newspaper },
              { id: 'injuries', label: 'Injury Report', icon: AlertTriangle },
              { id: 'weather', label: 'Weather Impact', icon: Thermometer },
              { id: 'trends', label: 'Betting Trends', icon: TrendingUp },
              { id: 'social', label: 'Social Pulse', icon: Users }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                  activeTab === tab.id
                    ? 'bg-bg-card/20 border border-bg-card/50 bg-card'
                    : 'bg-bg-card/20 hover:bg-bg-card/30 bg-card'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Content Area */}
      {activeTab === 'news' && (
        <div className="space-y-4">
          {/* Breaking News Banner */}
          {newsArticles.filter(a => a.priority === 'high').length > 0 && (
            <Card className="bg-card border-red-500/30 bg-red-500/5">
              <div className="bg-card"></div>
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-red-500/20 text-red-500 animate-pulse">BREAKING</Badge>
                  <span className="text-xs bg-card">
                    {formatDistanceToNow(newsArticles.filter(a => a.priority === 'high')[0].timestamp, { addSuffix: true })}
                  </span>
                </div>
                <h2 className="text-lg font-bold bg-card mb-1">
                  {newsArticles.filter(a => a.priority === 'high')[0].headline}
                </h2>
                <p className="text-sm bg-card">
                  {newsArticles.filter(a => a.priority === 'high')[0].subheadline}
                </p>
              </CardContent>
            </Card>
          )}

          {/* News Articles Grid */}
          <div className="grid grid-cols-1 gap-4">
            {newsArticles.slice(0, 10).map((article) => (
              <Card key={article.id} className="bg-card hover:border-bg-card/50 transition-all cursor-pointer">
                <div className="bg-card"></div>
                <CardContent className="p-4">
                  <div className="flex gap-4">
                    {/* Article Icon */}
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-lg bg-bg-card/30 flex items-center justify-center text-2xl">
                        {article.image}
                      </div>
                    </div>

                    {/* Article Content */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge className={`text-xs ${
                            article.category === 'breaking' ? 'bg-red-500/20 text-red-500' :
                            article.category === 'injuries' ? 'bg-yellow-500/20 text-yellow-500' :
                            article.category === 'analysis' ? 'bg-bg-card/20 text-bg-card' :
                            'bg-bg-card text-bg-card'
                          }`}>
                            {article.category.toUpperCase()}
                          </Badge>
                          <span className="text-xs bg-card">
                            {article.author}
                          </span>
                          <span className="text-xs bg-card">•</span>
                          <span className="text-xs bg-card">
                            {formatDistanceToNow(article.timestamp, { addSuffix: true })}
                          </span>
                        </div>
                      </div>

                      <h3 className="font-bold bg-card mb-1 hover:bg-card transition-colors">
                        {article.headline}
                      </h3>
                      <p className="text-sm bg-card mb-2">
                        {article.subheadline}
                      </p>
                      <p className="text-xs bg-card line-clamp-2">
                        {article.content}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Load More Button */}
          {newsArticles.length > 10 && (
            <div className="text-center">
              <Button variant="outline" className="bg-card">
                Load More Stories
              </Button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'injuries' && (
        <div className="grid grid-cols-2 gap-6">
          {/* Home Team Injuries */}
          <Card className="bg-card">
            <div className="bg-card"></div>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center justify-between bg-card">
                <span className="text-base">{game.home_team_name}</span>
                <Badge className={`text-xs ${
                  injuryImpact.home > 5 ? 'bg-red-500/20 text-red-500' :
                  injuryImpact.home > 2 ? 'bg-yellow-500/20 text-yellow-500' :
                  'bg-green-500/20 text-green-500'
                }`}>
                  Impact: {injuryImpact.home > 5 ? 'HIGH' : injuryImpact.home > 2 ? 'MEDIUM' : 'LOW'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {injuries?.injuries?.filter((inj: any) => inj.team === game.home_team_name).map((injury: any, idx: number) => (
                  <div key={idx} className="p-3 bg-bg-card/20 rounded-lg border border-bg-card/30">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <div className="font-medium bg-card">{injury.player}</div>
                        <div className="text-xs bg-card">{injury.position} • #{injury.jersey_number || 'N/A'}</div>
                      </div>
                      <Badge className={`text-xs ${
                        injury.status === 'Out' ? 'bg-red-500/20 text-red-500 border-red-500/30' :
                        injury.status === 'Doubtful' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                        injury.status === 'Questionable' ? 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30' :
                        'bg-green-500/20 text-green-500 border-green-500/30'
                      }`}>
                        {injury.status}
                      </Badge>
                    </div>
                    <div className="text-xs bg-card">{injury.injury}</div>
                    {injury.impact_level && (
                      <div className="mt-2 flex items-center gap-2">
                        <span className="text-xs bg-card">Impact:</span>
                        <div className="flex gap-1">
                          {[1, 2, 3].map((level) => (
                            <div
                              key={level}
                              className={`w-2 h-2 rounded-full ${
                                level <= (injury.impact_level === 'High' ? 3 : injury.impact_level === 'Medium' ? 2 : 1)
                                  ? 'bg-bg-card'
                                  : 'bg-bg-card'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )) || (
                  <div className="text-center py-8 bg-card">
                    <Shield className="w-8 h-8 mx-auto mb-2" />
                    <p className="text-sm">No injuries reported</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Away Team Injuries */}
          <Card className="bg-card">
            <div className="bg-card"></div>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center justify-between bg-card">
                <span className="text-base">{game.away_team_name}</span>
                <Badge className={`text-xs ${
                  injuryImpact.away > 5 ? 'bg-red-500/20 text-red-500' :
                  injuryImpact.away > 2 ? 'bg-yellow-500/20 text-yellow-500' :
                  'bg-green-500/20 text-green-500'
                }`}>
                  Impact: {injuryImpact.away > 5 ? 'HIGH' : injuryImpact.away > 2 ? 'MEDIUM' : 'LOW'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {injuries?.injuries?.filter((inj: any) => inj.team === game.away_team_name).map((injury: any, idx: number) => (
                  <div key={idx} className="p-3 bg-bg-card/20 rounded-lg border border-bg-card/30">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <div className="font-medium bg-card">{injury.player}</div>
                        <div className="text-xs bg-card">{injury.position} • #{injury.jersey_number || 'N/A'}</div>
                      </div>
                      <Badge className={`text-xs ${
                        injury.status === 'Out' ? 'bg-red-500/20 text-red-500 border-red-500/30' :
                        injury.status === 'Doubtful' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                        injury.status === 'Questionable' ? 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30' :
                        'bg-green-500/20 text-green-500 border-green-500/30'
                      }`}>
                        {injury.status}
                      </Badge>
                    </div>
                    <div className="text-xs bg-card">{injury.injury}</div>
                    {injury.impact_level && (
                      <div className="mt-2 flex items-center gap-2">
                        <span className="text-xs bg-card">Impact:</span>
                        <div className="flex gap-1">
                          {[1, 2, 3].map((level) => (
                            <div
                              key={level}
                              className={`w-2 h-2 rounded-full ${
                                level <= (injury.impact_level === 'High' ? 3 : injury.impact_level === 'Medium' ? 2 : 1)
                                  ? 'bg-bg-card'
                                  : 'bg-bg-card'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )) || (
                  <div className="text-center py-8 bg-card">
                    <Shield className="w-8 h-8 mx-auto mb-2" />
                    <p className="text-sm">No injuries reported</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'weather' && (
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-bold bg-card flex items-center gap-2">
                  <Thermometer className="w-5 h-5" />
                  Weather Conditions
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-bg-card/20 rounded-lg">
                    <span className="bg-card">Temperature</span>
                    <span className="font-bold bg-card">{weather?.temperature || 72}°F</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-bg-card/20 rounded-lg">
                    <span className="bg-card">Wind Speed</span>
                    <span className="font-bold bg-card">{weather?.wind_speed || 5} mph</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-bg-card/20 rounded-lg">
                    <span className="bg-card">Humidity</span>
                    <span className="font-bold bg-card">{weather?.humidity || 50}%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-bg-card/20 rounded-lg">
                    <span className="bg-card">Condition</span>
                    <span className="font-bold bg-card">{weather?.condition || 'Clear'}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-bold bg-card">Betting Impact</h3>
                <div className="space-y-3">
                  <div className="p-4 bg-bg-card/10 rounded-lg border border-bg-card/20">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="bg-bg-card/20 text-bg-card text-xs">TOTAL</Badge>
                      <span className="text-sm font-medium bg-card">Over/Under Impact</span>
                    </div>
                    <p className="text-sm bg-card">
                      {weather?.wind_speed > 15 ? 'Strong winds favor UNDER' :
                       weather?.temperature < 32 ? 'Cold weather favors UNDER' :
                       weather?.temperature > 85 ? 'Hot weather may increase scoring' :
                       'Neutral conditions for totals'}
                    </p>
                  </div>
                  <div className="p-4 bg-bg-card/10 rounded-lg border border-bg-card/20">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="bg-bg-card/20 text-bg-card text-xs">SPREAD</Badge>
                      <span className="text-sm font-medium bg-card">Home Field Advantage</span>
                    </div>
                    <p className="text-sm bg-card">
                      {weather?.condition?.includes('Rain') || weather?.condition?.includes('Snow') ?
                       'Weather conditions may neutralize home advantage' :
                       'Normal home field advantage applies'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'trends' && (
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardContent className="p-6">
            <div className="space-y-4">
              <h3 className="text-lg font-bold bg-card flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Key Betting Trends & Intelligence
              </h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {intelligence?.trends?.map((trend: any, idx: number) => (
                  <div key={idx} className="p-4 bg-bg-card/10 rounded-lg border border-bg-card/20">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          trend.confidence === 'High' ? 'bg-bg-card' :
                          trend.confidence === 'Medium' ? 'bg-yellow-400' :
                          'bg-orange-400'
                        }`} />
                        <span className="text-sm font-medium bg-card uppercase">
                          {trend.category || trend.type || 'INSIGHT'}
                        </span>
                      </div>
                      <Badge className={`text-xs ${
                        trend.impact === 'Positive' || trend.impact === 'Recommended' ? 'bg-green-500/20 text-green-500' :
                        trend.impact === 'Negative' || trend.impact === 'Pass' ? 'bg-red-500/20 text-red-500' :
                        'bg-yellow-500/20 text-yellow-500'
                      }`}>
                        {trend.impact}
                      </Badge>
                    </div>
                    <p className="text-sm bg-card mb-2">{trend.text}</p>
                    {trend.kelly_percentage && (
                      <div className="flex items-center gap-4 text-xs bg-card">
                        <span>Kelly: {trend.kelly_percentage}</span>
                        {trend.expected_value && <span>EV: {trend.expected_value}</span>}
                        {trend.risk_level && <span>Risk: {trend.risk_level}</span>}
                      </div>
                    )}
                  </div>
                )) || (
                  <div className="text-center py-8">
                    <TrendingUp className="w-12 h-12 mx-auto mb-4 bg-card" />
                    <p className="bg-card">Loading betting intelligence...</p>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'social' && (
        <Card className="bg-card">
          <div className="bg-card"></div>
          <CardContent className="p-6">
            <div className="text-center py-12">
              <Users className="w-16 h-16 mx-auto mb-4 bg-card" />
              <h3 className="text-xl font-bold bg-card mb-2">Social Sentiment Analysis</h3>
              <p className="bg-card mb-6">Track what the betting community is saying</p>

              <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
                <div className="p-4 bg-bg-card/20 rounded-lg">
                  <div className="text-2xl font-bold bg-card mb-1">67%</div>
                  <div className="text-xs bg-card">Public on {game.home_team_name}</div>
                </div>
                <div className="p-4 bg-bg-card/20 rounded-lg">
                  <div className="text-2xl font-bold bg-card mb-1">⚡</div>
                  <div className="text-xs bg-card">High Activity</div>
                </div>
                <div className="p-4 bg-bg-card/20 rounded-lg">
                  <div className="text-2xl font-bold text-green-500 mb-1">+4.5</div>
                  <div className="text-xs bg-card">Line Movement</div>
                </div>
              </div>

              <div className="mt-6 text-xs bg-card">
                Social data integration coming soon with Twitter/X and Reddit APIs
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Live View Component
const LiveView: React.FC<{ gameData: GameData }> = ({ gameData }) => {
  const isLive = gameData.game.status === 'status_in_progress' || gameData.game.status === 'live';

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

// Intelligence View - Universal Intelligence System
const IntelligenceView: React.FC<{ gameData: GameData }> = ({ gameData }) => {
  const [intelligenceResult, setIntelligenceResult] = useState<IntelligenceResult | null>(null);
  const [selectedTab, setSelectedTab] = useState('analysis');

  const handleIntelligenceDecision = (result: IntelligenceResult) => {
    setIntelligenceResult(result);
    // Additional handling like updating bet slip based on recommendations
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-card">
        <div className="bg-card"></div>
        <CardContent className="p-6">
          <div className="text-center">
            <h2 className="text-4xl font-black bg-card mb-2">
              UNIVERSAL INTELLIGENCE
            </h2>
            <p className="bg-card">
              102 specialized agents analyzing across 5 squadrons
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6">
        {[
          { id: 'analysis', label: 'AI Analysis', icon: Brain },
          { id: 'memory', label: 'Memory Search', icon: Database },
          { id: 'patterns', label: 'Pattern Library', icon: BookOpen },
        ].map((tab) => (
          <Button
            key={tab.id}
            variant={selectedTab === tab.id ? 'default' : 'outline'}
            onClick={() => setSelectedTab(tab.id)}
            className={selectedTab === tab.id ? 'bg-bg-card/20 border-bg-card' : ''}
          >
            <tab.icon className="w-4 h-4 mr-2" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Tab Content */}
      {selectedTab === 'analysis' && (
        <div className="grid grid-cols-1 gap-6">
          <IntelligencePanel
            gameId={gameData.game.id}
            gameData={gameData}
            onDecision={handleIntelligenceDecision}
          />

          {/* Additional Analysis Cards */}
          {intelligenceResult && (
            <div className="grid grid-cols-2 gap-4">
              {/* Quick Actions Based on Intelligence */}
              <Card className="bg-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-yellow-500" />
                    Recommended Actions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Primary Action:</span>
                      <Badge className={`${
                        intelligenceResult.primary_action.includes('EXECUTE') ? 'bg-green-500' : 'bg-yellow-500'
                      } text-foreground`}>
                        {intelligenceResult.primary_action}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Confidence:</span>
                      <span className="font-bold">{(intelligenceResult.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Kelly Stake:</span>
                      <span className="font-bold text-bg-card">
                        ${intelligenceResult.position_sizing.recommended_stake}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Risk Summary */}
              <Card className="bg-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-red-500" />
                    Risk Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Overall Risk:</span>
                      <Progress value={intelligenceResult.risk_assessment.overall_risk * 100} className="w-20" />
                    </div>
                    <div className="text-xs text-muted-foreground mt-2">
                      Top Risk Factors:
                    </div>
                    {intelligenceResult.risk_assessment.risk_factors.slice(0, 2).map((factor, idx) => (
                      <div key={idx} className="text-xs flex items-start gap-1">
                        <AlertTriangle className="h-3 w-3 text-yellow-500 mt-0.5" />
                        <span>{factor}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}

      {selectedTab === 'memory' && (
        <MemorySearch
          domain="SPORTS_BETTING"
          entityId={gameData.game.id}
          onMemorySelect={(memory) => {
            console.log('Selected memory:', memory);
            // Handle memory selection
          }}
        />
      )}

      {selectedTab === 'patterns' && (
        <PatternLibrary
          domain="SPORTS_BETTING"
          onPatternSelect={(pattern) => {
            console.log('Selected pattern:', pattern);
            // Handle pattern selection
          }}
        />
      )}
    </div>
  );
};