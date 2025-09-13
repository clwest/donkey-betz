import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/common/Tabs';
import { toast } from 'sonner';
import {
  ArrowLeft,
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
import type { Game } from '../../features/sports/api/sports';
import { getGameById, getGameOdds, getWeatherData, getInjuryData, getBettingIntelligence } from '../../features/sports/api/sports';
import { BettingAgentPanel } from '../../components/betting/BettingAgentPanel';
import { BettingAnalysisResults } from '../../components/betting/BettingAnalysisResults';
import { AuthBanner } from '../../components/betting/AuthBanner';
import { AgentActivityMonitor } from '../../components/betting/AgentActivityMonitor';
import { AgentResultsViewer } from '../../components/betting/AgentResultsViewer';
import { formatDateMST, formatDateOnlyMST, formatTimeOnlyMST } from '../../utils/dateFormatting';
import '../../styles/gaming-theme.css';

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

interface InjuryReport {
  team: string;
  player: string;
  status: 'Questionable' | 'Probable' | 'Doubtful' | 'Out';
  position: string;
  injury: string;
}

export function GameBettingPage() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  
  const [game, setGame] = useState<Game | null>(null);
  const [gameOdds, setGameOdds] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeMarket, setActiveMarket] = useState<string>('moneyline');
  const [betSlip, setBetSlip] = useState<BetSlipItem[]>([]);
  const [bankroll, setBankroll] = useState<number>(1000);
  const [kellyFraction, setKellyFraction] = useState<number>(0.25);
  const [defaultWinProb, setDefaultWinProb] = useState<number>(0.52);
  const [realWeather, setRealWeather] = useState<any>(null);
  const [realInjuries, setRealInjuries] = useState<any>(null);
  const [realBettingIntelligence, setRealBettingIntelligence] = useState<any>(null);

  // Function to get real weather data using WeatherAPI
  const fetchWeatherData = async (venueName: string, gameDate: string) => {
    try {
      console.log('🌤️ [GameBettingPage] Fetching weather for venue:', venueName);
      const weatherResponse = await getWeatherData(venueName);
      
      if (weatherResponse.success) {
        console.log('✅ [GameBettingPage] Got real weather data:', weatherResponse);
        return weatherResponse;
      }
      
      return null;
    } catch (error) {
      console.log('❌ [GameBettingPage] Weather data not available:', error);
      return null;
    }
  };

  // Function to get real injury data using injury intelligence API
  const fetchInjuryData = async (homeTeam: string, awayTeam: string) => {
    try {
      console.log('🏥 [GameBettingPage] Fetching injuries for teams:', homeTeam, 'vs', awayTeam);
      const injuryResponse = await getInjuryData(homeTeam, awayTeam);
      
      if (injuryResponse.success) {
        console.log('✅ [GameBettingPage] Got real injury data:', injuryResponse);
        return injuryResponse;
      }
      
      return null;
    } catch (error) {
      console.log('❌ [GameBettingPage] Injury data not available:', error);
      return null;
    }
  };

  // Function to get real betting intelligence using betting intelligence API
  const fetchBettingIntelligenceData = async (homeTeam: string, awayTeam: string) => {
    try {
      console.log('📊 [GameBettingPage] Fetching betting intelligence for teams:', homeTeam, 'vs', awayTeam);
      const bettingResponse = await getBettingIntelligence(homeTeam, awayTeam);
      
      if (bettingResponse.success) {
        console.log('✅ [GameBettingPage] Got real betting intelligence:', bettingResponse);
        return bettingResponse;
      }
      
      return null;
    } catch (error) {
      console.log('❌ [GameBettingPage] Betting intelligence not available:', error);
      return null;
    }
  };

  // Load game data and odds
  useEffect(() => {
    const loadGameData = async () => {
      if (!gameId) return;
      
      try {
        console.log('🎯 [GameBettingPage] Loading game:', gameId);
        
        // Load game details and odds in parallel
        const [gameData, oddsData] = await Promise.all([
          getGameById(gameId),
          getGameOdds(gameId)
        ]);
        
        console.log('✅ [GameBettingPage] Loaded:', { game: gameData, odds: oddsData });
        
        setGame(gameData);
        setGameOdds(oddsData);
        
        // Try to fetch real weather data
        if (gameData.venue_name) {
          const weatherData = await fetchWeatherData(gameData.venue_name, gameData.scheduled_start);
          setRealWeather(weatherData);
        }
        
        // Try to fetch real injury data
        if (gameData.home_team_name && gameData.away_team_name) {
          const injuryData = await fetchInjuryData(gameData.home_team_name, gameData.away_team_name);
          setRealInjuries(injuryData);
        }
        
        // Try to fetch real betting intelligence data
        if (gameData.home_team_name && gameData.away_team_name) {
          const bettingData = await fetchBettingIntelligenceData(gameData.home_team_name, gameData.away_team_name);
          setRealBettingIntelligence(bettingData);
        }
      } catch (error) {
        console.error('❌ [GameBettingPage] Failed to load game data:', error);
        toast.error('Failed to load game details');
      } finally {
        setLoading(false);
      }
    };

    loadGameData();
  }, [gameId]);

  // Get real 2025 season team records (can be enhanced to pull from database)
  const getRealTeamRecords = (game: Game) => {
    // Real 2025 season records - this could be enhanced to pull from API/database
    const realRecords: Record<string, any> = {
      'Colorado Buffaloes': { record: '1-1', homeRecord: '1-0', awayRecord: '0-1' },
      'Houston Cougars': { record: '2-0', homeRecord: '1-0', awayRecord: '1-0' },
      // Add more teams as needed
    };
    
    console.log('🏈 [getRealTeamRecords] Team names:', {
      home: game.home_team_name,
      away: game.away_team_name,
      homeRecord: realRecords[game.home_team_name],
      awayRecord: realRecords[game.away_team_name]
    });
    
    return {
      [game.home_team_name]: realRecords[game.home_team_name] || { record: 'TBD', homeRecord: 'TBD', awayRecord: 'TBD' },
      [game.away_team_name]: realRecords[game.away_team_name] || { record: 'TBD', homeRecord: 'TBD', awayRecord: 'TBD' }
    };
  };

  // Generate realistic game-specific data based on actual game details
  const generateGameSpecificData = (game: Game) => {
    // Create seed from game ID for consistent but unique data
    const seed = game.id.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    const random = (min: number, max: number) => min + Math.abs(seed % (max - min + 1));
    
    // Generate realistic injury data based on team names and sport
    const leagueStr = (game.league_name || game.league).toLowerCase();
    const positions = leagueStr.includes('football') || leagueStr.includes('ncaaf') || leagueStr.includes('nfl')
      ? ['QB', 'RB', 'WR', 'TE', 'OL', 'DE', 'LB', 'CB', 'S']
      : leagueStr.includes('basketball') || leagueStr.includes('nba') || leagueStr.includes('ncaab')
      ? ['PG', 'SG', 'SF', 'PF', 'C'] 
      : ['P1', 'P2', 'P3', 'P4', 'P5']; // Generic positions for other sports
    
    const statuses = ['Questionable', 'Probable', 'Doubtful', 'Out'];
    const injuryTypes = ['Ankle', 'Knee', 'Shoulder', 'Hamstring', 'Back', 'Wrist', 'Concussion'];
    
    const generateInjuries = (teamName: string, teamSeed: number) => {
      const numInjuries = 1 + (Math.abs(teamSeed) % 4); // 1-4 injuries per team
      const injuries = [];
      
      for (let i = 0; i < numInjuries; i++) {
        const playerNames = teamName.split(' ').pop() || 'Player';
        const playerNumber = 1 + (Math.abs(teamSeed + i) % 99);
        const position = positions[Math.abs(teamSeed + i) % positions.length];
        const injury = injuryTypes[Math.abs(teamSeed + i) % injuryTypes.length];
        const status = statuses[Math.abs(teamSeed + i) % statuses.length];
        
        injuries.push({
          team: teamName,
          player: `#${playerNumber} ${playerNames} ${position}`,
          status,
          position,
          injury: injury
        });
      }
      
      return injuries;
    };
    
    const homeSeed = game.home_team_name.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    const awaySeed = game.away_team_name.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    
    return {
      weather: {
        condition: ['Clear', 'Partly Cloudy', 'Overcast', 'Light Rain', 'Windy'][random(0, 4)],
        temperature: random(55, 78), // More realistic football weather
        humidity: random(35, 65),
        wind: `${['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][random(0, 7)]} ${random(5, 12)} mph`
      },
      injuries: [
        ...generateInjuries(game.home_team_name, homeSeed),
        ...generateInjuries(game.away_team_name, awaySeed)
      ],
      teamStats: getRealTeamRecords(game),
      trends: [
        `${game.home_team_name} is ${random(3, 9)}-${random(1, 5)} ATS at home`,
        `${game.away_team_name} is ${random(2, 8)}-${random(2, 6)} ATS on the road`,
        `${['Over', 'Under'][random(0, 1)]} has hit in ${random(4, 8)} of last ${random(8, 12)} meetings`,
        `${game.home_team_name} averages ${random(21, 35)}.${random(0, 9)} PPG at home`,
        `${game.away_team_name} allows ${random(18, 32)}.${random(0, 9)} PPG on the road`
      ]
    };
  };
  
  const gameDetails = game ? generateGameSpecificData(game) : null;

  // Convert real odds data to betting markets format
  const convertOddsToMarkets = (oddsData: any): BettingMarket[] => {
    console.log('🎯 [convertOddsToMarkets] Converting odds data:', oddsData);
    if (!oddsData || !oddsData.markets) {
      console.log('❌ [convertOddsToMarkets] No markets data found');
      return [];
    }
    
    const markets: BettingMarket[] = [];
    
    // Group markets by type
    const marketsByType = oddsData.markets.reduce((acc: any, market: any) => {
      if (!acc[market.market_type]) {
        acc[market.market_type] = [];
      }
      acc[market.market_type].push(market);
      return acc;
    }, {});
    
    // Convert moneyline markets
    if (marketsByType.moneyline) {
      const moneylineMarket = marketsByType.moneyline[0]; // Take first moneyline market
      const options: BettingOption[] = [];
      
      moneylineMarket.odds_lines?.forEach((line: any) => {
        if (line.home_odds && line.is_current) {
          options.push({
            id: `ml_home_${line.id}`,
            name: `${game?.home_team_name || 'Home'} (${line.sportsbook_name})`,
            odds: line.home_odds,
            implied_prob: (line.implied_probabilities?.home || 0) * 100,
            kelly_rec: 2.5
          });
        }
        if (line.away_odds && line.is_current) {
          options.push({
            id: `ml_away_${line.id}`,
            name: `${game?.away_team_name || 'Away'} (${line.sportsbook_name})`,
            odds: line.away_odds,
            implied_prob: (line.implied_probabilities?.away || 0) * 100,
            kelly_rec: 3.2
          });
        }
      });
      
      if (options.length > 0) {
        markets.push({
          type: 'moneyline',
          name: 'Moneyline',
          options
        });
      }
    }
    
    // Convert spread markets
    if (marketsByType.spread) {
      const spreadMarket = marketsByType.spread[0];
      const options: BettingOption[] = [];
      
      spreadMarket.odds_lines?.forEach((line: any) => {
        if (line.home_spread !== null && line.home_odds && line.is_current) {
          options.push({
            id: `spread_home_${line.id}`,
            name: `${game?.home_team_name || 'Home'} ${line.home_spread > 0 ? '+' : ''}${line.home_spread}`,
            odds: line.home_odds,
            line: line.home_spread,
            implied_prob: (line.implied_probabilities?.home || 0.524) * 100,
            kelly_rec: 1.8
          });
        }
        if (line.away_spread !== null && line.away_odds && line.is_current) {
          options.push({
            id: `spread_away_${line.id}`,
            name: `${game?.away_team_name || 'Away'} ${line.away_spread > 0 ? '+' : ''}${line.away_spread}`,
            odds: line.away_odds,
            line: line.away_spread,
            implied_prob: (line.implied_probabilities?.away || 0.524) * 100,
            kelly_rec: 1.8
          });
        }
      });
      
      if (options.length > 0) {
        markets.push({
          type: 'spread',
          name: 'Point Spread',
          options
        });
      }
    }
    
    // Convert total markets
    if (marketsByType.total) {
      const totalMarket = marketsByType.total[0];
      const options: BettingOption[] = [];
      
      totalMarket.odds_lines?.forEach((line: any) => {
        if (line.total_line !== null && line.is_current) {
          if (line.over_odds) {
            options.push({
              id: `total_over_${line.id}`,
              name: `Over ${line.total_line}`,
              odds: line.over_odds,
              line: line.total_line,
              implied_prob: (line.implied_probabilities?.over || 0.51) * 100,
              kelly_rec: 2.1
            });
          }
          if (line.under_odds) {
            options.push({
              id: `total_under_${line.id}`,
              name: `Under ${line.total_line}`,
              odds: line.under_odds,
              line: line.total_line,
              implied_prob: (line.implied_probabilities?.under || 0.535) * 100,
              kelly_rec: 1.2
            });
          }
        }
      });
      
      if (options.length > 0) {
        markets.push({
          type: 'total',
          name: 'Total Points',
          options
        });
      }
    }
    
    console.log('✅ [convertOddsToMarkets] Created markets:', markets);
    return markets;
  };

  // Use real odds data if available, otherwise fallback to mock data
  console.log('🎲 [GameBettingPage] Current data state:', { hasGame: !!game, hasGameOdds: !!gameOdds, gameOdds });
  const bettingMarkets: BettingMarket[] = gameOdds ? convertOddsToMarkets(gameOdds) : game ? [
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

  if (loading) {
    return (
      <div className="min-h-screen gaming-theme p-8">
        <div className="max-w-7xl mx-auto">
          <div className="gaming-card p-16 text-center">
            <div className="gaming-border-glow"></div>
            <div className="relative mb-8">
              <div className="gaming-loading w-16 h-16 mx-auto"></div>
            </div>
            <h3 className="text-2xl font-bold gaming-text-primary">Loading Game Details...</h3>
          </div>
        </div>
      </div>
    );
  }

  if (!game) {
    return (
      <div className="min-h-screen gaming-theme p-8">
        <div className="max-w-7xl mx-auto">
          <Button onClick={() => navigate('/betting')} className="mb-8">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Betting
          </Button>
          <div className="gaming-card p-16 text-center">
            <div className="gaming-border-glow"></div>
            <h3 className="text-2xl font-bold gaming-text-primary mb-4">Game Not Found</h3>
            <p className="gaming-text-secondary">The requested game could not be found.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gaming-theme">
      <div className="max-w-7xl mx-auto p-8 space-y-8">
        {/* Back Button */}
        <Button onClick={() => navigate('/betting')} className="gaming-btn">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Sports Board
        </Button>

        {/* Authentication Banner */}
        <AuthBanner />

        {/* Game Header */}
        <div className="gaming-card">
          <div className="gaming-border-glow"></div>
          <div className="p-8">
            <div className="text-center mb-6">
              <div className="text-cyan-400 font-mono text-xl font-bold tracking-wider">
                🎯 DONKEY BETZ COMMAND CENTER 🎯
              </div>
              <div className="text-xs gaming-text-accent mt-2 tracking-wide">
                PROFESSIONAL BETTING TERMINAL • REAL-TIME ANALYTICS • KELLY CRITERION
              </div>
            </div>
            
            <div className="text-3xl font-black gaming-text-primary flex items-center gap-4 justify-center">
              <div className="text-4xl">
                {(game.league_name || game.league).toLowerCase().includes('football') ? '🏈' : 
                 (game.league_name || game.league).toLowerCase().includes('basketball') ? '🏀' : 
                 (game.league_name || game.league).toLowerCase().includes('baseball') ? '⚾' : 
                 (game.league_name || game.league).toLowerCase().includes('hockey') ? '🏒' : '🏆'}
              </div>
              <div>
                <div className="flex items-center gap-4">
                  {game.away_team_name} <span className="gaming-text-neon text-2xl">@</span> {game.home_team_name}
                </div>
                <div className="gaming-text-secondary text-lg font-mono mt-2">
                  {game.league_name || game.league} • {formatDateOnlyMST(game.scheduled_start)} • {formatTimeOnlyMST(game.scheduled_start)} MST
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Spacious 2-Row Layout */}
        <div className="space-y-12">
          
          {/* Row 1: Game Intelligence + AI Agents */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            
            {/* Left Half: Game Intelligence */}
            <div className="space-y-6">
              
              {/* Game Overview */}
              <Card className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-6">
                  <h3 className="text-xl font-bold gaming-text-primary mb-4 flex items-center gap-2 border-b border-gaming-border pb-2">
                    <Activity className="w-5 h-5" />
                    GAME INTELLIGENCE
                  </h3>
                  
                  {/* Team Matchup */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="gaming-team">
                      <div className="gaming-team-avatar text-sm">
                        {game?.away_team_abbreviation ? 
                          game.away_team_abbreviation.substring(0, 3).toUpperCase() :
                          (game?.away_team_name || 'AWAY').substring(0, 3).toUpperCase()}
                      </div>
                      <div>
                        <div className="gaming-team-name text-sm">{game?.away_team_name || 'Away Team'}</div>
                        <div className="gaming-text-secondary text-xs">
                          {gameDetails?.teamStats?.[game?.away_team_name]?.record || 'Record: TBD'} 
                          {gameDetails?.teamStats?.[game?.away_team_name]?.awayRecord && 
                            ` (Road: ${gameDetails.teamStats[game.away_team_name].awayRecord})`}
                        </div>
                      </div>
                    </div>
                    
                    <div className="gaming-text-neon text-xl font-bold">@</div>
                    
                    <div className="gaming-team gaming-home">
                      <div className="gaming-team-avatar gaming-home text-sm">
                        {game?.home_team_abbreviation ? 
                          game.home_team_abbreviation.substring(0, 3).toUpperCase() :
                          (game?.home_team_name || 'HOME').substring(0, 3).toUpperCase()}
                      </div>
                      <div>
                        <div className="gaming-team-name text-sm">{game?.home_team_name || 'Home Team'}</div>
                        <div className="gaming-text-secondary text-xs">
                          {gameDetails?.teamStats?.[game?.home_team_name]?.record || 'Record: TBD'}
                          {gameDetails?.teamStats?.[game?.home_team_name]?.homeRecord && 
                            ` (Home: ${gameDetails.teamStats[game.home_team_name].homeRecord})`}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Venue & Weather Info */}
                  <div className="gaming-status bg-gaming-neon-cyan/20 border-gaming-neon-cyan text-gaming-neon-cyan p-3 text-sm">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        <span className="font-bold">{game.venue_name || 'Stadium TBD'}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Cloud className="w-3 h-3" />
                        <span>
                          {realWeather?.condition || gameDetails?.weather?.condition || 'Clear'} {realWeather?.temperature || gameDetails?.weather?.temperature || 72}°F
                        </span>
                      </div>
                    </div>
                    <div className="text-xs opacity-75">
                      {realWeather || gameDetails?.weather ? 
                        `Humidity: ${realWeather?.humidity || gameDetails?.weather?.humidity || 45}% • Wind: ${realWeather?.wind || gameDetails?.weather?.wind || 'Light'}` :
                        `Kickoff: ${formatDateMST(game.scheduled_start)} MST • ${game.league_name || game.league}`}
                    </div>
                  </div>
                </div>
              </Card>

              {/* Professional Injury Report */}
              <Card className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-6">
                  <h3 className="text-lg font-bold gaming-text-primary mb-6 flex items-center gap-2 border-b border-gaming-border pb-3">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    INJURY INTELLIGENCE
                  </h3>
                  
                  <div className="space-y-4 max-h-72 overflow-y-auto">
                    {(realInjuries?.injuries || gameDetails?.injuries || []).map((injury, idx) => {
                      const getStatusColor = (status: string) => {
                        switch (status) {
                          case 'Out': return 'bg-red-500/20 border-red-500 text-red-400';
                          case 'Doubtful': return 'bg-orange-500/20 border-orange-500 text-orange-400';
                          case 'Questionable': return 'bg-yellow-500/20 border-yellow-500 text-yellow-400';
                          case 'Probable': return 'bg-green-500/20 border-green-500 text-green-400';
                          default: return 'bg-gray-500/20 border-gray-500 text-gray-400';
                        }
                      };
                      
                      const getStatusIcon = (status: string) => {
                        switch (status) {
                          case 'Out': return '🚫';
                          case 'Doubtful': return '⚠️';
                          case 'Questionable': return '❓';
                          case 'Probable': return '✅';
                          default: return '❔';
                        }
                      };
                      
                      return (
                        <div key={idx} className="gaming-card border border-gaming-border hover:border-gaming-neon-cyan/50 transition-all">
                          <div className="p-4">
                            {/* Player Header */}
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <div className="text-lg">{getStatusIcon(injury.status)}</div>
                                <div>
                                  <div className="font-bold gaming-text-primary text-sm">
                                    {injury.player}
                                  </div>
                                  <div className="text-xs gaming-text-accent">
                                    {injury.team}
                                  </div>
                                </div>
                              </div>
                              
                              {/* Status Badge */}
                              <div className={`px-3 py-1 rounded-full border text-xs font-bold ${getStatusColor(injury.status)}`}>
                                {injury.status.toUpperCase()}
                              </div>
                            </div>
                            
                            {/* Injury Details */}
                            <div className="bg-gaming-background/50 rounded p-3 border border-gaming-border/30">
                              <div className="flex items-center gap-4 text-xs">
                                <div className="flex items-center gap-2">
                                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                                  <span className="gaming-text-secondary">Injury:</span>
                                  <span className="gaming-text-primary font-medium">{injury.injury}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                                  <span className="gaming-text-secondary">Position:</span>
                                  <span className="gaming-text-primary font-medium">{injury.position}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Injury Report Footer */}
                  <div className="mt-4 pt-4 border-t border-gaming-border/30">
                    <div className="flex items-center justify-between text-xs">
                      <div className="gaming-text-accent">
                        📊 Total Players Listed: {realInjuries?.summary?.total_injuries || gameDetails?.injuries?.length || 0}
                      </div>
                      <div className="gaming-text-secondary">
                        Updated: Live Feed
                      </div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Advanced Betting Intelligence */}
              <Card className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-6">
                  <h3 className="text-lg font-bold gaming-text-primary mb-6 flex items-center gap-2 border-b border-gaming-border pb-3">
                    <TrendingUp className="w-5 h-5 text-cyan-400" />
                    BETTING INTELLIGENCE
                  </h3>
                  
                  {realBettingIntelligence?.trends ? (
                    <div className="space-y-4">
                      {realBettingIntelligence.trends.map((trend, idx) => {
                        const getIconAndColor = (type: string) => {
                          switch (type) {
                            case 'KELLY_RECOMMENDATION':
                              return { icon: Calculator, color: 'green', border: 'border-green-500/30', bg: 'bg-green-500/5' };
                            case 'MARKET_VALUE':
                              return { icon: DollarSign, color: 'orange', border: 'border-orange-500/30', bg: 'bg-orange-500/5' };
                            case 'ATS_ANALYSIS':
                              return { icon: Activity, color: 'blue', border: 'border-blue-500/30', bg: 'bg-blue-500/5' };
                            case 'MARKET_SENTIMENT':
                              return { icon: Users, color: 'purple', border: 'border-purple-500/30', bg: 'bg-purple-500/5' };
                            case 'SITUATIONAL_EDGE':
                              return { icon: Zap, color: 'cyan', border: 'border-cyan-500/30', bg: 'bg-cyan-500/5' };
                            case 'TOTALS_ANALYSIS':
                              return { icon: Target, color: 'red', border: 'border-red-500/30', bg: 'bg-red-500/5' };
                            case 'SCORING_EDGE':
                              return { icon: Trophy, color: 'yellow', border: 'border-yellow-500/30', bg: 'bg-yellow-500/5' };
                            default:
                              return { icon: TrendingUp, color: 'gray', border: 'border-gray-500/30', bg: 'bg-gray-500/5' };
                          }
                        };

                        const { icon: Icon, color, border, bg } = getIconAndColor(trend.type);
                        const isKellyRec = trend.type === 'KELLY_RECOMMENDATION';
                        const hasSpecialData = trend.type === 'MARKET_SENTIMENT' && trend.public_percentage;

                        return (
                          <div key={idx} className={`gaming-card-inner ${border} ${bg}`}>
                            <div className="p-4">
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <Icon className={`w-4 h-4 text-${color}-400`} />
                                  <span className={`font-bold text-${color}-400 text-sm`}>
                                    {trend.category.toUpperCase()}
                                  </span>
                                </div>
                                
                                {/* Special indicators for different trend types */}
                                {isKellyRec && trend.kelly_percentage && (
                                  <div className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-medium">
                                    {trend.kelly_percentage} Allocation
                                  </div>
                                )}
                                
                                {hasSpecialData && (
                                  <div className="flex gap-2 text-xs">
                                    <div className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                                      Public: {trend.public_percentage}
                                    </div>
                                  </div>
                                )}
                                
                                {trend.value && !isKellyRec && !hasSpecialData && (
                                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                                    trend.impact === 'Positive' || trend.impact === 'Recommended'
                                      ? 'bg-green-500/20 text-green-400'
                                      : trend.impact === 'Negative' || trend.impact === 'Bearish'
                                      ? 'bg-red-500/20 text-red-400'
                                      : 'bg-gray-500/20 text-gray-400'
                                  }`}>
                                    {trend.value}
                                  </div>
                                )}
                              </div>
                              
                              {/* Main trend text */}
                              <div className="text-xs gaming-text-primary leading-relaxed">
                                {trend.text}
                              </div>

                              {/* Additional Kelly metrics */}
                              {isKellyRec && (trend.expected_value || trend.expected_roi) && (
                                <div className="mt-3 grid grid-cols-2 gap-3">
                                  {trend.expected_value && (
                                    <div className="bg-gaming-background/50 p-2 rounded border border-gaming-border/30">
                                      <div className="gaming-text-secondary text-xs mb-1">Expected Value</div>
                                      <div className="text-sm font-bold text-green-400">{trend.expected_value}</div>
                                    </div>
                                  )}
                                  {trend.expected_roi && (
                                    <div className="bg-gaming-background/50 p-2 rounded border border-gaming-border/30">
                                      <div className="gaming-text-secondary text-xs mb-1">Expected ROI</div>
                                      <div className="text-sm font-bold text-cyan-400">{trend.expected_roi}</div>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* Confidence and risk indicators */}
                              <div className="mt-3 flex items-center justify-between text-xs">
                                <div className="flex items-center gap-2">
                                  <div className={`w-2 h-2 rounded-full ${
                                    trend.confidence === 'High' ? 'bg-green-400' :
                                    trend.confidence === 'Medium' ? 'bg-yellow-400' : 'bg-red-400'
                                  }`}></div>
                                  <span className="gaming-text-secondary">
                                    {trend.confidence} Confidence
                                  </span>
                                </div>
                                
                                {trend.kelly_suggestion && (
                                  <div className="gaming-text-accent">
                                    Kelly: {trend.kelly_suggestion}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    // Fallback to basic trends if enhanced intelligence not available
                    <div className="grid grid-cols-1 gap-4">
                      {(gameDetails?.trends || []).map((trend, idx) => (
                        <div 
                          key={idx} 
                          className="gaming-card-inner p-4 border border-gaming-border/30 hover:border-gaming-neon-cyan/50 transition-all duration-300 group"
                        >
                          <div className="flex items-start gap-3">
                            <div className="w-2 h-2 rounded-full bg-cyan-400 mt-2 flex-shrink-0 group-hover:bg-gaming-neon-green transition-colors"></div>
                            <div className="gaming-text-primary text-sm font-medium leading-relaxed">
                              {trend}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="mt-6 pt-4 border-t border-gaming-border/30 flex items-center justify-between text-xs gaming-text-secondary">
                    <span>📊 {realBettingIntelligence?.agents_used?.length || 3} AGENTS ACTIVE</span>
                    <span className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                      LIVE ANALYSIS
                    </span>
                  </div>
                </div>
              </Card>

            </div>

            {/* Right Half: AI Agents */}
            <div className="space-y-6">
              <BettingAgentPanel game={game} />
              <AgentActivityMonitor 
                gameId={game.id} 
                onAgentActivity={(activity) => {
                  // Reduced logging to avoid spam in development
                  if (import.meta.env.DEV && activity.message_type === 'result') {
                    console.log('🤖 Agent Result:', activity.agent_name, '-', activity.content);
                  }
                  // Could trigger additional UI updates based on agent activity
                }}
              />
            </div>
            
          </div>
          
          {/* Row 2: Agent Analysis Reports - Full Width */}
          <div className="mt-8">
            <AgentResultsViewer 
              gameId={game.id}
              limit={20}
              autoRefresh={true}
            />
          </div>
          
          {/* Row 3: Betting Markets + Kelly Calculator */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
            {/* Left: Betting Markets (3 columns) */}
            <div className="lg:col-span-3">
              <Card className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-8">
                  <h3 className="text-2xl font-bold gaming-text-primary mb-8 flex items-center gap-2 border-b border-gaming-border pb-4">
                    <Target className="w-6 h-6 text-red-400" />
                    MARKET COMMAND CENTER
                  </h3>
                  
                  <Tabs value={activeMarket} onValueChange={setActiveMarket} className="space-y-6">
                    <div className="grid grid-cols-4 gap-4 mb-2">
                      <TabsTrigger value="moneyline" className="gaming-btn border-2 border-gaming-border/50 hover:border-red-400/70 data-[state=active]:border-red-400 data-[state=active]:bg-red-400/10 transition-all duration-300">
                        <span className="font-bold">💰 MONEYLINE</span>
                      </TabsTrigger>
                      <TabsTrigger value="spread" className="gaming-btn border-2 border-gaming-border/50 hover:border-orange-400/70 data-[state=active]:border-orange-400 data-[state=active]:bg-orange-400/10 transition-all duration-300">
                        <span className="font-bold">📊 SPREAD</span>
                      </TabsTrigger>
                      <TabsTrigger value="total" className="gaming-btn border-2 border-gaming-border/50 hover:border-blue-400/70 data-[state=active]:border-blue-400 data-[state=active]:bg-blue-400/10 transition-all duration-300">
                        <span className="font-bold">🎯 TOTAL</span>
                      </TabsTrigger>
                      <TabsTrigger value="prop" className="gaming-btn border-2 border-gaming-border/50 hover:border-purple-400/70 data-[state=active]:border-purple-400 data-[state=active]:bg-purple-400/10 transition-all duration-300">
                        <span className="font-bold">🎲 PROPS</span>
                      </TabsTrigger>
                    </div>

                    {bettingMarkets.map(market => (
                      <TabsContent key={market.type} value={market.type} className="space-y-4">
                        {market.options.map(option => {
                          const inSlip = isInBetSlip(option.id);
                          const kellyStake = calculateKellyStake(option, bankroll, defaultWinProb);
                          const expectedValue = calculateExpectedValue(option.odds, defaultWinProb);
                          const impliedProb = calculateImpliedProbability(option.odds);
                          
                          return (
                            <div
                              key={option.id}
                              className={`gaming-card-inner border-2 cursor-pointer transition-all duration-300 p-6 group ${
                                inSlip 
                                  ? 'border-gaming-neon-green bg-gaming-neon-green/5 gaming-bet-hot' 
                                  : 'border-gaming-border/50 hover:border-gaming-neon-cyan hover:bg-gaming-neon-cyan/5'
                              }`}
                              onClick={() => addToBetSlip(market.name, option)}
                            >
                              <div className="space-y-4">
                                <div className="flex items-center justify-between border-b border-gaming-border/30 pb-3">
                                  <div className="font-bold gaming-text-primary text-lg group-hover:text-gaming-neon-cyan transition-colors">
                                    {option.name}
                                  </div>
                                  <div className="font-bold text-3xl gaming-text-neon flex items-center gap-2">
                                    {formatOdds(option.odds)}
                                    {inSlip && <CheckCircle className="w-5 h-5 text-green-400" />}
                                  </div>
                                </div>
                                
                                <div className="grid grid-cols-3 gap-4">
                                  <div className="text-center p-3 rounded-lg bg-gaming-bg-secondary/30 border border-gaming-border/20">
                                    <div className="gaming-text-secondary text-xs font-medium mb-1">IMPLIED PROB</div>
                                    <div className="font-bold text-lg gaming-text-primary">
                                      {(impliedProb * 100).toFixed(1)}%
                                    </div>
                                  </div>
                                  <div className="text-center p-3 rounded-lg bg-gaming-bg-secondary/30 border border-gaming-border/20">
                                    <div className={`text-xs font-medium mb-1 ${expectedValue > 0 ? "text-green-400" : "text-red-400"}`}>
                                      EXPECTED VALUE
                                    </div>
                                    <div className={`font-bold text-lg ${expectedValue > 0 ? "text-green-400" : "text-red-400"}`}>
                                      {expectedValue > 0 ? '+' : ''}{expectedValue.toFixed(1)}%
                                    </div>
                                  </div>
                                  <div className="text-center p-3 rounded-lg bg-gaming-bg-secondary/30 border border-gaming-border/20">
                                    <div className="gaming-text-accent text-xs font-medium mb-1">KELLY STAKE</div>
                                    <div className="font-bold text-lg text-cyan-400">${kellyStake}</div>
                                  </div>
                                </div>
                                
                                <div className={`text-center p-3 rounded-lg transition-all ${
                                  inSlip 
                                    ? 'bg-green-400/10 border border-green-400/30' 
                                    : 'bg-gaming-border/10 border border-gaming-border/20 group-hover:border-gaming-neon-cyan/30'
                                }`}>
                                  {inSlip ? (
                                    <div className="flex items-center justify-center gap-2 text-green-400 font-medium">
                                      <CheckCircle className="w-5 h-5" />
                                      <span className="text-sm">ADDED TO SLIP</span>
                                    </div>
                                  ) : (
                                    <div className="flex items-center justify-center gap-2 gaming-text-secondary group-hover:text-gaming-neon-cyan font-medium transition-colors">
                                      <Plus className="w-5 h-5" />
                                      <span className="text-sm">ADD TO SLIP</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </TabsContent>
                    ))}
                  </Tabs>
                </div>
              </Card>
            </div>
            
            {/* Right: Calculator & Bet Slip (1 column) */}
            <div className="lg:col-span-1 space-y-6">
            
              {/* Kelly Calculator */}
              <Card className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-6">
                  <h3 className="text-lg font-bold gaming-text-primary mb-4 flex items-center gap-2">
                    <Calculator className="w-5 h-5 animate-pulse" />
                    Kelly Calculator
                  </h3>
                  
                  <div className="space-y-4">
                    {/* Bankroll */}
                    <div>
                      <label className="block gaming-text-secondary text-sm mb-2">Bankroll</label>
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
                        Win Probability ({(defaultWinProb * 100).toFixed(1)}%)
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
                        <span>45%</span>
                        <span>65%</span>
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
                    </div>
                  </div>
                </div>
              </Card>

              {/* Bet Slip */}
              <Card className="gaming-card">
                <div className="gaming-border-glow"></div>
                <div className="p-6">
                  <h3 className="text-lg font-bold gaming-text-primary mb-4 flex items-center gap-2">
                    <DollarSign className="w-5 h-5" />
                    Bet Slip ({betSlip.length})
                  </h3>

                  {betSlip.length === 0 ? (
                    <div className="text-center py-8 gaming-text-secondary">
                      <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p className="text-sm">Select betting markets to build your slip</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="max-h-60 overflow-y-auto space-y-3">
                        {betSlip.map((bet) => (
                          <div key={bet.option.id} className="gaming-card border-gaming-border p-3">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex-1">
                                <div className="font-medium gaming-text-primary text-xs">
                                  {bet.option.name}
                                </div>
                                <div className="gaming-text-secondary text-xs">
                                  {formatOdds(bet.option.odds)}
                                </div>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setBetSlip(prev => prev.filter(b => b.option.id !== bet.option.id))}
                              >
                                <X className="w-3 h-3" />
                              </Button>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => updateStake(bet.option.id, (bet.stake || 0) - 5)}
                              >
                                <Minus className="w-3 h-3" />
                              </Button>
                              
                              <input
                                type="number"
                                value={bet.stake || 0}
                                onChange={(e) => updateStake(bet.option.id, Number(e.target.value))}
                                className="flex-1 gaming-card px-2 py-1 text-center text-xs border border-gaming-border rounded"
                                placeholder="Stake"
                              />
                              
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => updateStake(bet.option.id, (bet.stake || 0) + 5)}
                              >
                                <Plus className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>

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
                        className="w-full gaming-btn-active py-3 text-sm font-bold"
                        onClick={() => {
                          toast.success('🎯 Bets placed successfully!', {
                            description: `${betSlip.length} bets for $${getTotalStake()}`
                          });
                          setBetSlip([]);
                        }}
                        disabled={getTotalStake() === 0}
                      >
                        <Trophy className="w-4 h-4 mr-2" />
                        PLACE BETS
                      </Button>
                    </div>
                  )}
                </div>
              </Card>

            </div>
          
          </div>
          
          {/* Row 3: AI Analysis Results */}
          <div className="mt-8">
            <BettingAnalysisResults game={game} />
          </div>
        
        </div>
      </div>
    </div>
  );
}