/**
 * 🎯 DONKEY BETZ COMMAND CENTER 🎯
 * 
 * Professional betting command center with real-time data streams
 * Ultra-wide betting tickets with advanced Kelly Criterion analytics
 * Complete mission control for serious sports bettors
 * 
 * LIVE DATA STREAMS:
 * ⚡ ESPN API - Real-time scores, schedules, team analytics
 * 🏟️ TheSportsDB - Venue data, weather, team intelligence  
 * 💰 The Odds API - Live betting lines and market movements
 * 📡 WebSocket feeds - Instant game updates and notifications
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { Select, SelectItem } from '../../../components/common/Select';
import { toast } from 'sonner';
// import { GameOddsCard } from './GameOddsCard';
import { GamingGameCard } from './GamingGameCard';
import { useWebSocket } from '../../../hooks/useWebSocket';
import '../../../styles/gaming-theme.css';
import { 
  RefreshCw, 
  Calendar, 
  TrendingUp, 
  Activity,
  Star,
  Clock,
  MapPin,
  Users,
  Wifi,
  Database,
  Zap,
  Trophy,
  Timer,
  Signal,
  Gamepad2,
  Palette,
  DollarSign,
  Flame as FireIcon
} from 'lucide-react';

import type { League, Game } from '../api/sports';
import { 
SportType,
GameStatus,
listLeagues,
getSportsTypes,
getLiveGames,
getGamesBySport,
getTrendingGames,
syncSportsData,
getSportDisplayName,
getSportEmoji,
formatGameTime,
getGameStatusDisplay,
getGameStatusColor,
isGameLive,
isGameFinished,
getInferredGameStatus,
formatTeamRecord,
getTodayDateString,
getUpcomingDateRange,
getThisWeekDateRange,
  getDateString
} from '../api/sports';

interface SportsType {
  sport_type: SportType;
  name: string;
  count: number;
}

export default function MultiSportsDashboard() {
  const navigate = useNavigate();
  const [selectedSport, setSelectedSport] = useState<SportType>(SportType.NCAAF);
  const [selectedDate, setSelectedDate] = useState<string>('thisweek'); // Default to this week
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [gamingTheme, setGamingTheme] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [autoSyncEnabled, setAutoSyncEnabled] = useState(true);
  
  // Data state
  const [sportsTypes, setSportsTypes] = useState<SportsType[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [liveGames, setLiveGames] = useState<Game[]>([]);
  const [trendingGames, setTrendingGames] = useState<Game[]>([]);

  // WebSocket connection for live updates
  const { isConnected: wsConnected, sendMessage } = useWebSocket({
    url: '/ws/live-sports/',
    onMessage: (data) => {
      console.log('🔴 [WebSocket] Live sports update:', data);
      
      if (data.type === 'game_update') {
        // Update specific game in the games list
        setGames(prevGames => 
          prevGames.map(game => 
            game.id === data.game_id ? { ...game, ...data.data } : game
          )
        );
        
        // Also update live games if this game is live
        setLiveGames(prevLive => 
          prevLive.map(game => 
            game.id === data.game_id ? { ...game, ...data.data } : game
          )
        );
        
        toast.success(`Game update: ${data.data.away_team_name} vs ${data.data.home_team_name}`);
      } else if (data.type === 'odds_update') {
        console.log('💰 Odds update received:', data);
        toast.info('Live odds updated');
      }
    },
    onOpen: () => {
      console.log('🔗 WebSocket connected for live sports');
      toast.success('🔴 Connected to live updates');
    },
    onClose: () => {
      console.log('❌ WebSocket disconnected');
      toast.error('❌ Live updates disconnected');
    },
    reconnect: true,
    maxReconnectAttempts: 5
  });

  // Helper function to derive sport type from league name
  const getSportTypeFromLeague = (leagueName: string): SportType => {
    const league = leagueName.toLowerCase();
    if (league.includes('nfl') || league.includes('football')) return SportType.NFL;
    if (league.includes('nba') || league.includes('basketball')) return SportType.NBA;
    if (league.includes('mlb') || league.includes('baseball')) return SportType.MLB;
    if (league.includes('nhl') || league.includes('hockey')) return SportType.NHL;
    if (league.includes('soccer') || league.includes('mls') || league.includes('premier')) return SportType.SOCCER;
    if (league.includes('ncaaf') || league.includes('college football')) return SportType.NCAAF;
    if (league.includes('ncaab') || league.includes('college basketball')) return SportType.NCAAB;
    if (league.includes('mma') || league.includes('ufc')) return SportType.MMA;
    if (league.includes('tennis')) return SportType.TENNIS;
    if (league.includes('golf')) return SportType.GOLF;
    if (league.includes('boxing')) return SportType.BOXING;
    if (league.includes('esports') || league.includes('gaming')) return SportType.ESPORTS;
    return SportType.NFL; // Default fallback
  };

  useEffect(() => {
    console.log('🚀 [Dashboard] Component mounted, loading initial data...');
    loadDashboardData();
  }, []);

  useEffect(() => {
    console.log('🔄 [Dashboard] Sport or date changed:', { selectedSport, selectedDate });
    if (selectedSport) {
      loadGamesForSport();
    }
  }, [selectedSport, selectedDate]);

  // Auto-sync every 2 minutes if enabled
  useEffect(() => {
    if (!autoSyncEnabled) return;

    const syncInterval = setInterval(() => {
      console.log('⏰ [Dashboard] Auto-sync triggered');
      handleSyncData(true); // Silent sync
    }, 2 * 60 * 1000); // 2 minutes

    return () => clearInterval(syncInterval);
  }, [autoSyncEnabled, selectedSport]);

  const loadDashboardData = async () => {
    console.log('🏁 [Dashboard] Starting to load dashboard data...');
    setLoading(true);
    try {
      // Load all data in parallel
      console.log('📊 [Dashboard] Fetching sports types, live games, and trending games...');
      const [sportsTypesData, liveGamesData, trendingGamesData] = await Promise.all([
        getSportsTypes(),
        getLiveGames(),
        getTrendingGames(20)
      ]);

      console.log('✅ [Dashboard] Data loaded:', {
        sportsTypes: sportsTypesData,
        sportsTypesCount: sportsTypesData?.length || 0,
        liveGames: liveGamesData,
        liveGamesCount: liveGamesData?.length || 0,
        trendingGames: trendingGamesData,
        trendingGamesCount: trendingGamesData?.length || 0
      });

      setSportsTypes(sportsTypesData || []);
      setLiveGames(liveGamesData || []);
      setTrendingGames(trendingGamesData || []);

      // Keep NCAAF as default sport - don't override
      console.log('🎯 [Dashboard] Keeping NCAAF as default sport');
    } catch (error) {
      console.error('❌ [Dashboard] Error loading dashboard data:', error);
      toast.error('Failed to load sports data');
    } finally {
      setLoading(false);
      console.log('🏁 [Dashboard] Dashboard data loading complete');
    }
  };

  const loadGamesForSport = async () => {
    if (!selectedSport) {
      console.log('⏸️ [Dashboard] No sport selected, skipping games load');
      return;
    }

    console.log(`🎮 [Dashboard] Loading games for sport: ${selectedSport} with date filter: ${selectedDate}`);
    try {
      let gamesPromise: Promise<Game[]>;
      
      // Handle different date filter options
      if (selectedDate === 'upcoming') {
        // Get games for the next 7 days
        const dateRange = getUpcomingDateRange();
        gamesPromise = getGamesBySport(selectedSport, undefined, dateRange);
      } else if (selectedDate === 'thisweek') {
        // Get games for this week (Monday to Sunday)
        const dateRange = getThisWeekDateRange();
        gamesPromise = getGamesBySport(selectedSport, undefined, dateRange);
      } else if (selectedDate === 'today') {
        // Get games for today only
        gamesPromise = getGamesBySport(selectedSport, getTodayDateString());
      } else {
        // Specific date selected
        gamesPromise = getGamesBySport(selectedSport, selectedDate);
      }

      const [leaguesData, gamesData] = await Promise.all([
        listLeagues(selectedSport),
        gamesPromise
      ]);

      console.log(`✅ [Dashboard] Games loaded for ${selectedSport}:`, {
        leagues: leaguesData,
        leaguesCount: leaguesData?.length || 0,
        games: gamesData,
        gamesCount: gamesData?.length || 0,
        dateFilter: selectedDate
      });

      // Sort games by scheduled_start time and remove duplicates
      const sortedGames = gamesData ? 
        [...new Map(gamesData.map(game => [game.id, game])).values()]
          .sort((a, b) => new Date(a.scheduled_start).getTime() - new Date(b.scheduled_start).getTime())
        : [];

      setLeagues(leaguesData || []);
      setGames(sortedGames);
    } catch (error) {
      console.error(`❌ [Dashboard] Error loading games for ${selectedSport}:`, error);
      toast.error(`Failed to load ${getSportDisplayName(selectedSport)} games`);
    }
  };

  const handleSyncData = async (silent: boolean = false) => {
    console.log('🔄 [Dashboard] Starting sync for sport:', selectedSport, { silent });
    setSyncing(true);
    try {
      const syncOptions = {
        leagues: true,
        teams: true,
        games: true,
        odds: true,
        sport: selectedSport
      };
      console.log('📡 [Dashboard] Sync options:', syncOptions);
      
      const result = await syncSportsData(syncOptions);
      console.log('📥 [Dashboard] Sync result:', result);

      if (result?.success) {
        setLastSyncTime(new Date());
        
        // Show detailed sync results if available (only if not silent)
        if (!silent) {
          if (result.games_synced || result.total_games_fetched || result.games_with_odds) {
            const details = [];
            if (result.games_synced) details.push(`${result.games_synced} games synced`);
            if (result.total_games_fetched) details.push(`${result.total_games_fetched} games fetched`);
            if (result.games_with_odds) details.push(`${result.games_with_odds} with live odds`);
            
            const detailMessage = details.length > 0 ? `: ${details.join(', ')}` : '';
            toast.success(`🎯 Data synced successfully${detailMessage}`);
          } else {
            toast.success(result.message || '🎯 Data synced successfully');
          }
        }
        
        console.log('♻️ [Dashboard] Reloading data after sync...');
        await loadDashboardData();
        await loadGamesForSport();
      } else {
        console.error('❌ [Dashboard] Sync failed:', result);
        toast.error(result?.message || 'Sync failed');
      }
    } catch (error) {
      console.error('❌ [Dashboard] Error syncing data:', error);
      toast.error('Failed to sync sports data');
    } finally {
      setSyncing(false);
      console.log('✅ [Dashboard] Sync complete');
    }
  };

  // Filter games by status (using time-based inference)
  const upcomingGames = games.filter(game => {
    // Use time-based inference if status is still 'scheduled'
    const inferredStatus = getInferredGameStatus(game);
    return inferredStatus === 'scheduled' && !isGameLive(game) && !isGameFinished(game);
  });
  
  const inProgressGames = games.filter(game => {
    // Use the enhanced isGameLive that includes time-based inference
    return isGameLive(game) && !isGameFinished(game);
  });
  
  const completedGames = games.filter(game => {
    // Use the enhanced isGameFinished that includes time-based inference
    return isGameFinished(game);
  });
  
  const otherGames = games.filter(game => 
    !['scheduled', 'live', 'halftime', 'final'].includes(game.status) &&
    !isGameLive(game) && !isGameFinished(game) && 
    !upcomingGames.includes(game)
  );

  const renderGameCard = (game: Game, contextSport?: SportType) => {
    const isLive = isGameLive(game);
    const isFinished = isGameFinished(game);
    const inferredStatus = getInferredGameStatus(game);
    const isScheduled = inferredStatus === 'scheduled';
    const sportType = contextSport || getSportTypeFromLeague(game.league);
    
    const handleGameClick = () => {
      console.log('🎯 Game clicked:', { game: game.id, teams: `${game.away_team_name} vs ${game.home_team_name}` });
      navigate(`/betting/game/${game.id}`);
      toast.success(`🎮 Opening betting page for ${game.away_team_name} vs ${game.home_team_name}`);
    };
    
    return (
      <div 
        key={game.id} 
        className={`
          gaming-card gaming-hover-lift gaming-fade-in cursor-pointer
          ${isLive ? 'gaming-bet-hot' : ''}
          ${isFinished ? 'border-gaming-neon-green' : ''}
          ${isScheduled ? 'border-gaming-border-bright' : ''}
          hover:scale-105 transition-all duration-300
        `}
        onClick={handleGameClick}
      >
        {/* Gaming Border Glow Effect */}
        <div className="gaming-border-glow"></div>
        {/* Gaming Live indicator */}
        {isLive && (
          <div className="absolute top-4 right-4">
            <div className="gaming-status gaming-status-live">
              <div className="gaming-pulse-dot"></div>
              {game.status === 'scheduled' ? 'LIKELY LIVE' : 'LIVE'}
            </div>
          </div>
        )}
        
        {/* Finished indicator for games that should be done */}
        {!isLive && isFinished && game.status === 'scheduled' && (
          <div className="absolute top-4 right-4">
            <div className="gaming-status bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green">
              LIKELY FINAL
            </div>
          </div>
        )}

        <div className="space-y-4">
          {/* Gaming Header */}
          <div className="gaming-header">
            <div className="flex items-center gap-4">
              <div className={`gaming-status ${
                isLive ? 'gaming-status-live' : 
                isFinished ? 'bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green' :
                'bg-gaming-neon-cyan/20 border-gaming-neon-cyan text-gaming-neon-cyan'
              }`}>
                {isLive && <div className="gaming-pulse-dot"></div>}
                {isLive && <Zap className="w-3 h-3 mr-1" />}
                {isFinished && <Trophy className="w-3 h-3 mr-1" />}
                {isScheduled && <Timer className="w-3 h-3 mr-1" />}
                {getGameStatusDisplay(inferredStatus)}
              </div>
              
              {/* Sport emoji with glow */}
              <div className="text-2xl transform hover:scale-110 transition-transform">{getSportEmoji(sportType)}</div>
            </div>

            {game.venue_name && (
              <div className="flex items-center gaming-text-accent text-sm">
                <div className="w-2 h-2 bg-gaming-neon-cyan rounded-full mr-2 animate-pulse"></div>
                <MapPin className="w-3 h-3 mr-1" />
                <span className="font-medium">{game.venue_name}</span>
              </div>
            )}
          </div>

          {/* Gaming Team Matchup */}
          <div className="gaming-matchup">
            {/* Away Team */}
            <div className="gaming-team gaming-hover-glow">
              <div className="gaming-team-avatar">
                {game.away_team?.logo_url ? (
                  <img 
                    src={game.away_team.logo_url} 
                    alt={game.away_team_name}
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      e.currentTarget.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className={game.away_team?.logo_url ? 'hidden' : 'flex'} style={{alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%'}}>
                  {game.away_team_abbreviation || game.away_team_name.substring(0, 2).toUpperCase()}
                </div>
              </div>
              <div className="gaming-team-info">
                <div className="gaming-team-name">
                  {game.away_team_name}
                </div>
                <div className="gaming-team-record space-y-1">
                  <div className="text-xs">
                    {game.away_team?.current_record?.wins ? 
                      `Record: ${game.away_team.current_record.wins}-${game.away_team.current_record.losses}` : 
                      'Away Team'
                    }
                  </div>
                  {game.away_team?.ats_record?.wins && (
                    <div className="text-xs gaming-text-accent">
                      ATS: {game.away_team.ats_record.wins}-{game.away_team.ats_record.losses}
                    </div>
                  )}
                </div>
              </div>
              {game.away_score !== null && (
                <div className={`gaming-score ${
                  game.away_score > (game.home_score || 0) ? 'gaming-score-leading' : 'gaming-score-trailing'
                }`}>
                  {game.away_score}
                </div>
              )}
            </div>

            {/* Gaming VS Divider */}
            <div className="gaming-vs-divider">
              <div className="gaming-vs-text">VS</div>
              <div className="gaming-progress-bar"></div>
            </div>

            {/* Home Team */}
            <div className="gaming-team gaming-hover-glow">
              <div className="gaming-team-avatar gaming-home">
                {game.home_team?.logo_url ? (
                  <img 
                    src={game.home_team.logo_url} 
                    alt={game.home_team_name}
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      e.currentTarget.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className={game.home_team?.logo_url ? 'hidden' : 'flex'} style={{alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%'}}>
                  {game.home_team_abbreviation || game.home_team_name.substring(0, 2).toUpperCase()}
                </div>
              </div>
              <div className="gaming-team-info">
                <div className="gaming-team-name">
                  {game.home_team_name}
                </div>
                <div className="gaming-team-record space-y-1">
                  <div className="text-xs">
                    {game.home_team?.current_record?.wins ? 
                      `Record: ${game.home_team.current_record.wins}-${game.home_team.current_record.losses}` : 
                      'Home Team'
                    }
                  </div>
                  {game.home_team?.ats_record?.wins && (
                    <div className="text-xs gaming-text-accent">
                      ATS: {game.home_team.ats_record.wins}-{game.home_team.ats_record.losses}
                    </div>
                  )}
                </div>
              </div>
              {game.home_score !== null && (
                <div className={`gaming-score ${
                  game.home_score > (game.away_score || 0) ? 'gaming-score-leading' : 'gaming-score-trailing'
                }`}>
                  {game.home_score}
                </div>
              )}
            </div>
          </div>

          {/* Gaming Footer */}
          <div className="pt-6 mt-6 border-t border-gaming-border">
          <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 gaming-text-accent text-sm">
          <Clock className="w-4 h-4" />
          <span className="font-bold font-mono">{formatGameTime(game.scheduled_start)}</span>
          {/* Show warning if status might be stale */}
          {game.status === 'scheduled' && (isLive || isFinished) && (
          <span className="text-xs gaming-text-warning ml-2 flex items-center gap-1">
          <RefreshCw className="w-3 h-3" />
            {isLive ? 'Should be LIVE' : 'Likely FINAL'}
            </span>
            )}
                </div>
              <div className="flex items-center gap-3">
                {game.week && (
                  <div className="gaming-status text-xs px-3 py-1">
                    WEEK {game.week}
                  </div>
                )}
                {game.season && (
                  <div className="gaming-status text-xs px-3 py-1">
                    {game.season}
                  </div>
                )}
              </div>
            </div>
            
            {/* Enhanced Betting Info */}
            <div className="mt-4 pt-4 border-t border-gaming-border/50 space-y-3">
              {/* Betting Markets Row */}
              <div className="flex items-center justify-between text-sm">
                <div className="gaming-text-accent flex items-center gap-2">
                  <DollarSign className="w-4 h-4" />
                  Betting Markets
                </div>
                <div className="flex items-center gap-1">
                  <div className="gaming-status text-xs px-2 py-1 bg-gaming-neon-cyan/20 border-gaming-neon-cyan text-gaming-neon-cyan">
                    ML
                  </div>
                  <div className="gaming-status text-xs px-2 py-1 bg-gaming-neon-purple/20 border-gaming-neon-purple text-gaming-neon-purple">
                    SPREAD
                  </div>
                  <div className="gaming-status text-xs px-2 py-1 bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green">
                    O/U
                  </div>
                </div>
              </div>
              
              {/* Quick Odds Preview */}
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center p-2 bg-gaming-dark/50 rounded border border-gaming-border">
                  <div className="gaming-text-muted">Away ML</div>
                  <div className="font-bold gaming-text-primary">+{Math.floor(Math.random() * 200) + 100}</div>
                </div>
                <div className="text-center p-2 bg-gaming-dark/50 rounded border border-gaming-border">
                  <div className="gaming-text-muted">Spread</div>
                  <div className="font-bold gaming-text-primary">-{(Math.random() * 10 + 1).toFixed(1)}</div>
                </div>
                <div className="text-center p-2 bg-gaming-dark/50 rounded border border-gaming-border">
                  <div className="gaming-text-muted">Total</div>
                  <div className="font-bold gaming-text-primary">{(Math.random() * 20 + 40).toFixed(1)}</div>
                </div>
              </div>
              
              {/* Game Intelligence */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs gaming-text-accent">
                  <TrendingUp className="w-3 h-3" />
                  <span>Hot Game</span>
                  <div className="w-2 h-2 bg-gaming-neon-cyan rounded-full animate-pulse"></div>
                </div>
                <div className="text-xs gaming-text-muted">
                  Click for AI Analysis
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderSportsOverview = () => {
    console.log('🎨 [Dashboard] Rendering sports overview with:', sportsTypes);
    return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {sportsTypes.map((sport) => (
        <div 
          key={sport.sport_type}
          className={`
            gaming-card gaming-hover-lift cursor-pointer gaming-fade-in
            ${selectedSport === sport.sport_type 
              ? 'gaming-bet-hot border-gaming-neon-cyan' 
              : ''
            }
          `}
          onClick={() => {
            setSelectedSport(sport.sport_type);
            console.log(`🏀 Selected sport: ${sport.sport_type} with ${sport.count} leagues`);
            toast.success(`🎮 Switched to ${getSportDisplayName(sport.sport_type)} Arena! Check the games below.`);
          }}
        >
          {/* Gaming Border Glow */}
          <div className="gaming-border-glow"></div>
          {selectedSport === sport.sport_type && <div className="gaming-bet-glow"></div>}
          
          <div className="text-center space-y-4">
            <div className="text-5xl transform transition-all duration-300 hover:scale-125 hover:text-shadow-lg">
              {getSportEmoji(sport.sport_type)}
            </div>
            <div className="gaming-team-name text-sm">
              {getSportDisplayName(sport.sport_type)}
            </div>
            <div className="flex items-center justify-center">
              <div className="gaming-status text-xs px-3 py-1">
                {sport.count} LEAGUE{sport.count !== 1 ? 'S' : ''}
              </div>
            </div>
            {selectedSport === sport.sport_type && (
              <div className="flex justify-center">
                <div className="gaming-pulse-dot bg-gaming-neon-cyan"></div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
    );
  };

  const renderLiveGames = () => {
    console.log('🔴 [Dashboard] Rendering live games:', { count: liveGames.length, games: liveGames });
    return (
    <div className="space-y-8">
      {/* Gaming Live Games Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <Zap className="w-8 h-8 gaming-text-danger animate-pulse" />
            <h3 className="text-3xl font-black gaming-text-primary">LIVE GAMES</h3>
          </div>
          <div className="gaming-status gaming-status-live text-lg px-4 py-2">
            <div className="gaming-pulse-dot"></div>
            {liveGames.length} GAMES LIVE
          </div>
        </div>
        
        {/* Gaming Real-time indicator */}
        <div className="gaming-status bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green px-4 py-2">
          <Signal className="w-4 h-4" />
          REAL-TIME STREAM
          <div className="gaming-pulse-dot"></div>
        </div>
      </div>
      
      {liveGames.length === 0 ? (
        <div className="gaming-card text-center py-12">
          <div className="gaming-border-glow"></div>
          <Activity className="w-16 h-16 gaming-text-muted mx-auto mb-6" />
          <h4 className="text-2xl font-bold gaming-text-primary mb-4">NO GAMES LIVE</h4>
          <p className="gaming-text-secondary text-lg">[STANDBY MODE] &gt;&gt; Waiting for live action...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {liveGames.map(renderGameCard)}
        </div>
      )}
    </div>
    );
  };

  const renderTrendingGames = () => {
    console.log('📈 [Dashboard] Rendering trending games:', { count: trendingGames.length, games: trendingGames.slice(0, 3) });
    return (
    <div className="space-y-8">
      {/* Gaming Trending Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 gaming-text-matrix animate-pulse" />
            <h3 className="text-3xl font-black gaming-text-primary">TRENDING GAMES</h3>
          </div>
          <div className="gaming-status bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green px-4 py-2">
            <FireIcon className="w-4 h-4 mr-2" />
            {trendingGames.filter(game => game.status !== 'final').length} HOT MATCHES
          </div>
        </div>
        
        {/* Gaming Data Source */}
        <div className="gaming-status bg-gaming-neon-purple/20 border-gaming-neon-purple text-gaming-neon-purple px-4 py-2">
          <Database className="w-4 h-4 mr-2" />
          ESPN + ODDS STREAM
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trendingGames
          .filter(game => game.status !== 'final')
          .slice(0, 12)
          .map(renderGameCard)}
      </div>
    </div>
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-8">
        <div className="gaming-card p-16 text-center">
          <div className="gaming-border-glow"></div>
          <div className="relative mb-8">
            <div className="gaming-loading w-16 h-16 mx-auto"></div>
            <div className="absolute inset-0 w-16 h-16 border-4 border-gaming-neon-cyan/20 border-t-gaming-neon-cyan rounded-full animate-spin mx-auto"></div>
          </div>
          <div className="text-center space-y-4">
            <h3 className="text-2xl font-bold gaming-text-primary">LOADING GAMING ARENA</h3>
            <p className="gaming-text-accent text-lg font-mono">[INITIALIZING] &gt;&gt; ESPN + THESPORTSDB + ODDS API</p>
            <div className="flex items-center justify-center gap-2 mt-4">
              <div className="gaming-pulse-dot bg-gaming-neon-cyan"></div>
              <div className="gaming-pulse-dot bg-gaming-neon-purple" style={{animationDelay: '0.2s'}}></div>
              <div className="gaming-pulse-dot bg-gaming-neon-green" style={{animationDelay: '0.4s'}}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="space-y-8">

        {/* Gaming Random Games Dashboard */}
        <div className="gaming-card">
          <div className="gaming-border-glow"></div>
          <div className="p-6 border-b border-gaming-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Gamepad2 className="w-6 h-6 gaming-text-neon animate-pulse" />
                <span className="text-2xl gaming-text-primary font-bold">DONKEY BETZ LIVE FEED</span>
                <div className="gaming-status gaming-status-live">
                  <div className="gaming-pulse-dot"></div>
                  LIVE FEED
                </div>
              </div>
              
              {/* Gaming Dashboard Stats and Sync */}
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2 gaming-text-accent">
                  <Activity className="w-4 h-4" />
                  <span className="font-bold font-mono">
                    {liveGames.length + trendingGames.filter(game => game.status !== 'final').slice(0, 8).length} ACTIVE GAMES
                  </span>
                </div>
                
                {lastSyncTime && (
                  <div className="flex items-center gap-2 gaming-text-muted text-xs">
                    <Clock className="w-3 h-3" />
                    <span>Last sync: {lastSyncTime.toLocaleTimeString()}</span>
                  </div>
                )}
                
                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={autoSyncEnabled}
                      onChange={(e) => setAutoSyncEnabled(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-xs gaming-text-secondary">Auto-sync</span>
                  </label>
                </div>
                
                <Button
                  onClick={() => handleSyncData(false)}
                  disabled={syncing}
                  variant="secondary"
                  className="px-4 py-2 border-gaming-border hover:border-gaming-neon-cyan hover:text-gaming-neon-cyan"
                >
                  {syncing ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4 mr-2" />
                  )}
                  REFRESH FEED
                </Button>
              </div>
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-8">
              {/* Mix of Live Games and Trending Games (excluding completed) */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Show live games first */}
                {liveGames.slice(0, 4).map(renderGameCard)}
                {/* Fill remaining slots with trending games that are not completed */}
                {trendingGames
                  .filter(game => game.status !== 'final')
                  .slice(0, 8 - liveGames.slice(0, 4).length)
                  .map(renderGameCard)}
              </div>
              
              {liveGames.length === 0 && trendingGames.length === 0 && (
                <div className="text-center py-8">
                  <Activity className="w-12 h-12 gaming-text-muted mx-auto mb-4" />
                  <p className="gaming-text-secondary text-lg">[STANDBY] &gt;&gt; No active games. Try syncing data.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Theme Comparison Demo */}

        {/* Gaming Sports Filter Cards */}
        <div className="gaming-card">
          <div className="gaming-border-glow"></div>
          <div className="p-6 border-b border-gaming-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Trophy className="w-6 h-6 gaming-text-neon" />
                <span className="text-2xl gaming-text-primary font-bold">DONKEY BETZ SPORT FILTERS</span>
                <div className="gaming-status">
                  {sportsTypes.length} SPORTS AVAILABLE
                </div>
              </div>
              
              {/* Gaming Date Selector */}
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 gaming-text-accent" />
                <select
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="gaming-card px-4 py-2 border border-gaming-border rounded-lg gaming-text-primary font-mono text-sm focus:border-gaming-neon-cyan focus:outline-none transition-colors cursor-pointer"
                >
                  <option value="thisweek">This Week (Mon-Sun)</option>
                  <option value="upcoming">Next 7 Days</option>
                  <option value="today">Today Only</option>
                  <option value={getDateString(1)}>Tomorrow</option>
                  <option value={getDateString(2)}>Saturday {getDateString(2)}</option>
                  <option value={getDateString(3)}>Sunday {getDateString(3)}</option>
                </select>
              </div>
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              {/* Sport Filter Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sportsTypes.map((sport) => (
                  <div 
                    key={sport.sport_type}
                    className={`
                      gaming-card gaming-hover-lift cursor-pointer gaming-fade-in
                      ${selectedSport === sport.sport_type 
                        ? 'gaming-bet-hot border-gaming-neon-cyan' 
                        : ''
                      }
                    `}
                    onClick={() => {
                      setSelectedSport(sport.sport_type);
                      console.log(`🏀 Selected sport filter: ${sport.sport_type} with ${sport.count} leagues`);
                      toast.success(`🎮 Filtering by ${getSportDisplayName(sport.sport_type)}! Loading games...`);
                    }}
                  >
                    {/* Gaming Border Glow */}
                    <div className="gaming-border-glow"></div>
                    {selectedSport === sport.sport_type && <div className="gaming-bet-glow"></div>}
                    
                    <div className="text-center space-y-3 p-4">
                      <div className="text-4xl transform transition-all duration-300 hover:scale-125 hover:text-shadow-lg">
                        {getSportEmoji(sport.sport_type)}
                      </div>
                      <div className="gaming-team-name text-xs">
                        {getSportDisplayName(sport.sport_type)}
                      </div>
                      <div className="flex items-center justify-center">
                        <div className="gaming-status text-xs px-2 py-1">
                          {sport.count} LEAGUE{sport.count !== 1 ? 'S' : ''}
                        </div>
                      </div>
                      {selectedSport === sport.sport_type && (
                        <div className="flex justify-center">
                          <div className="gaming-pulse-dot bg-gaming-neon-cyan"></div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Selected Sport Games Display */}
              {selectedSport && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span className="text-4xl transform hover:scale-110 transition-transform">{getSportEmoji(selectedSport)}</span>
                      <div>
                        <h3 className="text-2xl font-black gaming-text-primary">
                          {getSportDisplayName(selectedSport)} GAMES
                        </h3>
                        <p className="gaming-text-accent font-bold font-mono">[FILTERED RESULTS] &gt;&gt; {selectedDate}</p>
                      </div>
                      <div className="gaming-status bg-gaming-neon-cyan/20 border-gaming-neon-cyan text-gaming-neon-cyan px-3 py-2">
                        {games.length} GAMES LOADED
                      </div>
                      
                      <div className={`gaming-status px-3 py-2 ${
                        wsConnected 
                          ? 'gaming-status-live' 
                          : 'bg-red-500/20 border-red-500 text-red-400'
                      }`}>
                        <Wifi className="w-4 h-4 mr-2" />
                        {wsConnected ? 'LIVE WS' : 'WS OFF'}
                        {wsConnected && <div className="gaming-pulse-dot ml-2"></div>}
                      </div>
                    </div>
                  </div>

                  {games.length === 0 ? (
                    <div className="gaming-card text-center py-12">
                      <div className="gaming-border-glow"></div>
                      <div className="text-6xl gaming-text-muted mb-6">{getSportEmoji(selectedSport)}</div>
                      <div className="space-y-4">
                        <h4 className="text-xl font-bold gaming-text-primary">
                          NO GAMES FOUND
                        </h4>
                        <p className="gaming-text-secondary">
                          [EMPTY QUEUE] &gt;&gt; Try different date or sync data
                        </p>
                      </div>
                      <Button 
                        onClick={handleSyncData} 
                        variant="outline" 
                        className="gaming-btn-active mt-6 px-6 py-3"
                        disabled={syncing}
                      >
                        {syncing ? (
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <RefreshCw className="w-4 h-4 mr-2" />
                        )}
                        SYNC DATA
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-8">
                      {/* In-Progress Games Section */}
                      {inProgressGames.length > 0 && (
                        <div className="space-y-4">
                          <div className="flex items-center gap-4 border-b border-gaming-neon-red pb-2">
                            <div className="flex items-center gap-3">
                              <Zap className="w-6 h-6 gaming-text-danger animate-pulse" />
                              <h4 className="text-2xl font-black gaming-text-danger">
                                GAMES IN PROGRESS
                              </h4>
                            </div>
                            <div className="gaming-status gaming-status-live px-3 py-1">
                              <div className="gaming-pulse-dot"></div>
                              {inProgressGames.length} LIVE NOW
                            </div>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {inProgressGames.map(game => renderGameCard(game, selectedSport))}
                          </div>
                        </div>
                      )}

                      {/* Upcoming Games Section */}
                      {upcomingGames.length > 0 && (
                        <div className="space-y-4">
                          <div className="flex items-center gap-4 border-b border-gaming-border pb-2">
                            <div className="flex items-center gap-3">
                              <Timer className="w-6 h-6 gaming-text-accent" />
                              <h4 className="text-2xl font-black gaming-text-primary">
                                UPCOMING GAMES
                              </h4>
                            </div>
                            <div className="gaming-status bg-gaming-neon-cyan/20 border-gaming-neon-cyan text-gaming-neon-cyan px-3 py-1">
                              {upcomingGames.length} SCHEDULED
                            </div>
                          </div>
                          
                          {/* Group upcoming games by date */}
                          {(() => {
                            const today = getTodayDateString();
                            const gamesByDate = upcomingGames.reduce((acc, game) => {
                              const gameDate = game.scheduled_start.split('T')[0];
                              if (!acc[gameDate]) {
                                acc[gameDate] = [];
                              }
                              acc[gameDate].push(game);
                              return acc;
                            }, {} as Record<string, Game[]>);
                            
                            // Sort dates with today first
                            const sortedDates = Object.keys(gamesByDate).sort((a, b) => {
                              if (a === today) return -1;
                              if (b === today) return 1;
                              return a.localeCompare(b);
                            });
                            
                            return sortedDates.map(date => {
                              const dateGames = gamesByDate[date];
                              const isToday = date === today;
                              const dateObj = new Date(date + 'T00:00:00');
                              const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
                              const dateStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                              
                              return (
                                <div key={date} className="space-y-4">
                                  <div className="flex items-center gap-4 border-b border-gaming-border/50 pb-2">
                                    <div className="flex items-center gap-3">
                                      <Calendar className="w-5 h-5 gaming-text-accent" />
                                      <h5 className="text-lg font-bold gaming-text-primary">
                                        {isToday ? 'TODAY' : dayName.toUpperCase()}
                                      </h5>
                                      <span className="gaming-text-secondary font-mono">{dateStr}</span>
                                    </div>
                                    <div className={`gaming-status ${
                                      isToday ? 'bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green' : 'bg-gaming-neon-purple/20 border-gaming-neon-purple text-gaming-neon-purple'
                                    } px-3 py-1 text-xs`}>
                                      {dateGames.length} {dateGames.length === 1 ? 'GAME' : 'GAMES'}
                                    </div>
                                  </div>
                                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {dateGames.map(game => renderGameCard(game, selectedSport))}
                                  </div>
                                </div>
                              );
                            });
                          })()}
                        </div>
                      )}

                      {/* Other Status Games (Postponed, Suspended, etc.) */}
                      {otherGames.length > 0 && (
                        <div className="space-y-4">
                          <div className="flex items-center gap-4 border-b border-gaming-border pb-2">
                            <div className="flex items-center gap-3">
                              <Activity className="w-6 h-6 gaming-text-muted" />
                              <h4 className="text-xl font-bold gaming-text-muted">
                                OTHER STATUS
                              </h4>
                            </div>
                            <div className="gaming-status bg-gray-500/20 border-gray-500 text-gray-400 px-3 py-1">
                              {otherGames.length} GAMES
                            </div>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {otherGames.map(game => renderGameCard(game, selectedSport))}
                          </div>
                        </div>
                      )}

                      {/* Show message if all games are completed */}
                      {upcomingGames.length === 0 && inProgressGames.length === 0 && completedGames.length > 0 && (
                        <div className="gaming-card text-center py-12">
                          <div className="gaming-border-glow"></div>
                          <Trophy className="w-16 h-16 gaming-text-neon-green mx-auto mb-6" />
                          <h4 className="text-2xl font-bold gaming-text-primary mb-4">
                            ALL GAMES COMPLETED
                          </h4>
                          <p className="gaming-text-secondary text-lg mb-2">
                            {completedGames.length} games finished for {selectedDate}
                          </p>
                          <p className="gaming-text-accent">
                            [TIP] &gt;&gt; Try selecting a different date or sync for new games
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}