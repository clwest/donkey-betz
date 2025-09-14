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
  const [selectedSport, setSelectedSport] = useState<SportType | null>(null);
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

  // Team name mappings for better display
  const teamMappings: Record<string, { school: string; nickname: string }> = {
    // NCAAF Teams
    'OSU': { school: 'Ohio State', nickname: 'Buckeyes' },
    'OHIO': { school: 'Ohio', nickname: 'Bobcats' },
    'LSU': { school: 'LSU', nickname: 'Tigers' },
    'ALA': { school: 'Alabama', nickname: 'Crimson Tide' },
    'UGA': { school: 'Georgia', nickname: 'Bulldogs' },
    'MICH': { school: 'Michigan', nickname: 'Wolverines' },
    'ND': { school: 'Notre Dame', nickname: 'Fighting Irish' },
    'CLEM': { school: 'Clemson', nickname: 'Tigers' },
    'AUB': { school: 'Auburn', nickname: 'Tigers' },
    'MIZ': { school: 'Missouri', nickname: 'Tigers' },
    'FLA': { school: 'Florida', nickname: 'Gators' },
    'FSU': { school: 'Florida State', nickname: 'Seminoles' },
    'TAMU': { school: 'Texas A&M', nickname: 'Aggies' },
    'TA&M': { school: 'Texas A&M', nickname: 'Aggies' },
    'TEX': { school: 'Texas', nickname: 'Longhorns' },
    'OU': { school: 'Oklahoma', nickname: 'Sooners' },
    'USC': { school: 'USC', nickname: 'Trojans' },
    'UCLA': { school: 'UCLA', nickname: 'Bruins' },
    'ORE': { school: 'Oregon', nickname: 'Ducks' },
    'WASH': { school: 'Washington', nickname: 'Huskies' },
    'PSU': { school: 'Penn State', nickname: 'Nittany Lions' },
    'WISC': { school: 'Wisconsin', nickname: 'Badgers' },
    'IOWA': { school: 'Iowa', nickname: 'Hawkeyes' },
    'MSU': { school: 'Michigan State', nickname: 'Spartans' },
    'NEB': { school: 'Nebraska', nickname: 'Cornhuskers' },
    'ILL': { school: 'Illinois', nickname: 'Fighting Illini' },
    'NU': { school: 'Northwestern', nickname: 'Wildcats' },
    'VILL': { school: 'Villanova', nickname: 'Wildcats' },
    'WYO': { school: 'Wyoming', nickname: 'Cowboys' },
    'UTAH': { school: 'Utah', nickname: 'Utes' },
    'VAN': { school: 'Vanderbilt', nickname: 'Commodores' },
    'SC': { school: 'South Carolina', nickname: 'Gamecocks' },
    'ARK': { school: 'Arkansas', nickname: 'Razorbacks' },
    'MISS': { school: 'Ole Miss', nickname: 'Rebels' },
    'WMU': { school: 'Western Michigan', nickname: 'Broncos' },
    // NFL Teams
    'NE': { school: 'New England', nickname: 'Patriots' },
    'BUF': { school: 'Buffalo', nickname: 'Bills' },
    'MIA': { school: 'Miami', nickname: 'Dolphins' },
    'NYJ': { school: 'New York', nickname: 'Jets' },
    'KC': { school: 'Kansas City', nickname: 'Chiefs' },
    'GB': { school: 'Green Bay', nickname: 'Packers' },
    'PIT': { school: 'Pittsburgh', nickname: 'Steelers' },
    'DAL': { school: 'Dallas', nickname: 'Cowboys' },
    'COW': { school: 'Dallas', nickname: 'Cowboys' },
    'SF': { school: 'San Francisco', nickname: '49ers' },
    'SEA': { school: 'Seattle', nickname: 'Seahawks' },
    'LAR': { school: 'Los Angeles', nickname: 'Rams' },
    'PHI': { school: 'Philadelphia', nickname: 'Eagles' },
    'MIN': { school: 'Minnesota', nickname: 'Vikings' },
    'CHI': { school: 'Chicago', nickname: 'Bears' },
    'DET': { school: 'Detroit', nickname: 'Lions' }
  };

  const getTeamDisplayName = (abbreviation: string | undefined, fullName: string, sport: SportType): string => {
    if (!abbreviation) return fullName;
    const mapping = teamMappings[abbreviation.toUpperCase()];
    if (mapping) {
      return mapping.school;
    }
    // For NFL teams, just return the city/region part if available
    if (sport === SportType.NFL && fullName.includes(' ')) {
      return fullName.split(' ').slice(0, -1).join(' ');
    }
    return fullName;
  };

  const getTeamNickname = (abbreviation: string | undefined, fullName: string, sport: SportType): string => {
    if (!abbreviation) return '';
    const mapping = teamMappings[abbreviation.toUpperCase()];
    if (mapping) {
      return mapping.nickname;
    }
    // For NFL teams, return the nickname part if available
    if (sport === SportType.NFL && fullName.includes(' ')) {
      return fullName.split(' ').slice(-1)[0];
    }
    // For college teams, try to extract nickname from full name
    if ((sport === SportType.NCAAF || sport === SportType.NCAAB) && fullName) {
      // If it's already just the nickname, return empty to avoid duplication
      const commonNicknames = ['Tigers', 'Bulldogs', 'Wildcats', 'Bears', 'Eagles', 'Hawks', 'Lions'];
      if (commonNicknames.includes(fullName)) {
        return '';
      }
    }
    return '';
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

    // Comprehensive logging of game data
    console.log('🎮 [GAME CARD DATA]', {
      gameId: game.id,
      teams: `${game.away_team_name} vs ${game.home_team_name}`,
      sport: game.sport_type,
      league: game.league,
      status: game.status,
      inferredStatus: inferredStatus,
      scheduledStart: game.scheduled_start,
      venue: game.venue_name || game.venue,
      venueCity: game.venue_city,
      scores: {
        away: game.away_score,
        home: game.home_score
      },
      teamData: {
        away: {
          name: game.away_team_name,
          abbreviation: game.away_team?.abbreviation,
          logo: game.away_team?.logo_url,
          record: game.away_team?.current_record,
          city: game.away_team?.city,
          fullData: game.away_team
        },
        home: {
          name: game.home_team_name,
          abbreviation: game.home_team?.abbreviation,
          logo: game.home_team?.logo_url,
          record: game.home_team?.current_record,
          city: game.home_team?.city,
          fullData: game.home_team
        }
      },
      season: game.season,
      week: game.week,
      weatherData: game.weather_data,
      liveStats: game.live_stats,
      odds: game.odds,
      metadata: game.metadata,
      isLive,
      isFinished,
      isScheduled,
      fullGameObject: game
    });

    const handleGameClick = () => {
      console.log('🎯 Game clicked:', { game: game.id, teams: `${game.away_team_name} vs ${game.home_team_name}` });
      navigate(`/betting/game/${game.id}`);
      toast.success(`🎮 Opening betting page for ${game.away_team_name} vs ${game.home_team_name}`);
    };
    
    return (
      <div
        key={game.id}
        className={`
          gaming-card gaming-fade-in cursor-pointer
          ${isLive ? 'gaming-bet-hot' : ''}
          ${isFinished ? 'border-gaming-neon-green' : ''}
          ${isScheduled ? 'border-gaming-border-bright' : ''}
          transition-all duration-300
        `}
        style={{
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.boxShadow = '0 8px 30px rgba(0, 255, 255, 0.2)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '';
        }}
        onClick={handleGameClick}
      >
        {/* Subtle Border Glow Effect */}
        <div className="gaming-border-glow" style={{ opacity: 0.1 }}></div>
        {/* Clean status indicator - only for truly live games */}
        {isLive && game.status === 'live' && (
          <div className="absolute top-3 right-3 z-10">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-red-500/20 border border-red-500/50 rounded-full backdrop-blur-sm">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-xs font-semibold text-red-400">LIVE</span>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {/* Simplified Gaming Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              {/* Sport emoji */}
              <div className="text-xl opacity-80">{getSportEmoji(sportType)}</div>
              
              {/* Venue if available */}
              {game.venue_name && (
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <MapPin className="w-3 h-3" />
                  <span>{game.venue_name}</span>
                </div>
              )}
            </div>
            
            {/* Clean time display */}
            <div className="text-xs text-gray-400 font-mono">
              {formatGameTime(game.scheduled_start)}
            </div>
          </div>

          {/* Gaming Team Matchup */}
          <div className="gaming-matchup">
            {/* Away Team */}
            <div className="gaming-team" style={{
              padding: '8px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, rgba(0, 255, 255, 0.05), transparent)',
              transition: 'background 0.3s ease'
            }}>
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
                <div className="flex flex-col">
                  <div className="gaming-team-name text-sm font-bold">
                    {getTeamDisplayName(game.away_team?.abbreviation, game.away_team_name, sportType)}
                  </div>
                  <div className="text-xs text-gray-400">
                    {getTeamNickname(game.away_team?.abbreviation, game.away_team_name, sportType)}
                  </div>
                </div>
                <div className="gaming-team-record space-y-1 mt-1">
                  <div className="text-xs">
                    {game.away_team?.current_record?.wins !== undefined ?
                      `${game.away_team.current_record.wins}-${game.away_team.current_record.losses}` :
                      ''
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

            {/* Gaming VS Divider with Live Game Info */}
            <div className="gaming-vs-divider">
              <div className="gaming-vs-text">VS</div>
              {/* Live Game State Display */}
              {isLive && (
                <div className="mt-2 space-y-1">
                  {/* Period and Time */}
                  {(game.current_period || game.time_remaining) && (
                    <div className="flex items-center justify-center gap-2 text-xs">
                      {game.current_period && (
                        <span className="gaming-text-accent font-bold">
                          {sportType === 'nfl' || sportType === 'ncaaf' ? `Q${game.current_period}` :
                           sportType === 'nba' || sportType === 'ncaab' ? `P${game.current_period}` :
                           sportType === 'mlb' ? `Inning ${game.current_period}` :
                           sportType === 'nhl' ? `P${game.current_period}` :
                           game.current_period}
                        </span>
                      )}
                      {game.time_remaining && (
                        <span className="gaming-text-neon-green font-mono">
                          {game.time_remaining}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Football-specific: Down and Distance */}
                  {game.live_stats?.down_distance_text && (sportType === 'nfl' || sportType === 'ncaaf') && (
                    <div className="text-xs text-center gaming-text-secondary">
                      {game.live_stats.down_distance_text}
                    </div>
                  )}

                  {/* Possession Indicator */}
                  {game.live_stats?.possession && (
                    <div className="flex items-center justify-center gap-1 text-xs">
                      <span className="text-yellow-400">🏈</span>
                      <span className="gaming-text-accent">
                        {game.live_stats.possession === game.home_team?.abbreviation ? 'HOME' : 'AWAY'}
                      </span>
                    </div>
                  )}

                  {/* Red Zone Indicator */}
                  {game.live_stats?.is_red_zone && (
                    <div className="flex items-center justify-center">
                      <span className="px-2 py-0.5 bg-red-500/20 border border-red-500/50 rounded-full text-xs font-semibold text-red-400">
                        RED ZONE
                      </span>
                    </div>
                  )}
                </div>
              )}
              <div className="gaming-progress-bar"></div>
            </div>

            {/* Home Team */}
            <div className="gaming-team" style={{
              padding: '8px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, rgba(157, 78, 221, 0.05), transparent)',
              transition: 'background 0.3s ease'
            }}>
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
                <div className="flex flex-col">
                  <div className="gaming-team-name text-sm font-bold">
                    {getTeamDisplayName(game.home_team?.abbreviation, game.home_team_name, sportType)}
                  </div>
                  <div className="text-xs text-gray-400">
                    {getTeamNickname(game.home_team?.abbreviation, game.home_team_name, sportType)}
                  </div>
                </div>
                <div className="gaming-team-record space-y-1 mt-1">
                  <div className="text-xs">
                    {game.home_team?.current_record?.wins !== undefined ?
                      `${game.home_team.current_record.wins}-${game.home_team.current_record.losses}` :
                      ''
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

          {/* Simplified Footer */}
          <div className="pt-4 mt-4 border-t border-gaming-border/30">
            
            {/* Enhanced Betting Info with Real Odds */}
            <div className="space-y-3">
              {/* Weather info for outdoor games */}
              {game.weather_data && (game.weather_data.temperature || game.weather_data.condition) && (
                <div className="flex items-center gap-2 text-xs text-gray-400 bg-gray-800/30 rounded-lg px-3 py-2">
                  {game.weather_data.temperature && (
                    <>
                      <span>🌡️ {game.weather_data.temperature}°F</span>
                      {(game.weather_data.wind_mph || game.weather_data.condition) && <span>•</span>}
                    </>
                  )}
                  {game.weather_data.wind_mph && (
                    <>
                      <span>💨 {game.weather_data.wind_mph} mph</span>
                      {game.weather_data.condition && <span>•</span>}
                    </>
                  )}
                  {game.weather_data.condition && (
                    <span>{game.weather_data.condition}</span>
                  )}
                </div>
              )}

              {/* Timeouts display for live games */}
              {isLive && (game.live_stats?.timeouts_home !== undefined || game.live_stats?.timeouts_away !== undefined) && (
                <div className="flex items-center justify-between text-xs bg-gray-800/30 rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">Timeouts:</span>
                    <span className="gaming-text-secondary">
                      Away: {game.live_stats?.timeouts_away || 0}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="gaming-text-secondary">
                      Home: {game.live_stats?.timeouts_home || 0}
                    </span>
                  </div>
                </div>
              )}

              {/* Last Play for live games */}
              {isLive && game.live_stats?.last_play && (
                <div className="text-xs text-gray-400 bg-gray-800/30 rounded-lg px-3 py-2">
                  <span className="font-semibold text-gray-300">Last Play: </span>
                  {game.live_stats.last_play}
                </div>
              )}

              {/* Betting Lines */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-wrap">
                  {game.betting_markets && game.betting_markets.length > 0 ? (
                    <>
                      {(() => {
                        const mlMarket = game.betting_markets.find(m => m.market_type === 'h2h');
                        const spreadMarket = game.betting_markets.find(m => m.market_type === 'spreads');
                        const totalMarket = game.betting_markets.find(m => m.market_type === 'totals');

                        return (
                          <>
                            {mlMarket && (
                              <div className="flex flex-col bg-cyan-500/10 text-cyan-400 rounded px-2 py-1">
                                <span className="text-[10px] opacity-70">ML</span>
                                <span className="text-xs font-bold">
                                  {mlMarket.best_odds?.away || 'N/A'} / {mlMarket.best_odds?.home || 'N/A'}
                                </span>
                              </div>
                            )}
                            {spreadMarket && (
                              <div className="flex flex-col bg-purple-500/10 text-purple-400 rounded px-2 py-1">
                                <span className="text-[10px] opacity-70">SPREAD</span>
                                <span className="text-xs font-bold">
                                  {spreadMarket.spread || 'N/A'}
                                </span>
                              </div>
                            )}
                            {totalMarket && (
                              <div className="flex flex-col bg-green-500/10 text-green-400 rounded px-2 py-1">
                                <span className="text-[10px] opacity-70">O/U</span>
                                <span className="text-xs font-bold">
                                  {totalMarket.total || 'N/A'}
                                </span>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </>
                  ) : (
                    <div className="flex gap-2">
                      <span className="text-xs px-3 py-1.5 bg-gray-800/50 text-gray-500 rounded">
                        No odds available
                      </span>
                    </div>
                  )}
                </div>
                <button className="text-xs text-gray-400 hover:text-cyan-400 transition-colors flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Analyze
                </button>
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

  const renderGamesByLeague = () => {
    // Group games by league
    const gamesByLeague: Record<string, typeof trendingGames> = {};

    trendingGames.forEach(game => {
      const league = game.league || 'Other';
      if (!gamesByLeague[league]) {
        gamesByLeague[league] = [];
      }
      gamesByLeague[league].push(game);
    });

    // Define league display order and icons
    const leagueConfig: Record<string, { name: string; icon: string; color: string }> = {
      'NFL': { name: 'NFL', icon: '🏈', color: 'gaming-neon-cyan' },
      'NCAAF': { name: 'NCAAF', icon: '🏈', color: 'gaming-neon-purple' },
      'NBA': { name: 'NBA', icon: '🏀', color: 'gaming-neon-orange' },
      'NCAAB': { name: 'NCAAB', icon: '🏀', color: 'gaming-neon-yellow' },
      'MLB': { name: 'MLB', icon: '⚾', color: 'gaming-neon-green' },
      'NHL': { name: 'NHL', icon: '🏒', color: 'gaming-neon-blue' },
      'MMA': { name: 'MMA/UFC', icon: '🥊', color: 'gaming-neon-red' },
      'SOCCER': { name: 'Soccer', icon: '⚽', color: 'gaming-neon-green' },
    };

    const orderedLeagues = ['NFL', 'NCAAF', 'NBA', 'NCAAB', 'MLB', 'NHL', 'MMA', 'SOCCER'];

    return (
      <div className="space-y-12">
        {orderedLeagues.map(league => {
          const games = gamesByLeague[league];
          if (!games || games.length === 0) return null;

          const config = leagueConfig[league] || { name: league, icon: '🎮', color: 'gaming-neon-cyan' };
          const activeGames = games.filter(g => !isGameFinished(g));
          const liveGames = games.filter(g => isGameLive(g));
          const upcomingGames = games.filter(g => !isGameLive(g) && !isGameFinished(g));

          return (
            <div key={league} className="space-y-6">
              {/* League Section Header */}
              <div className="flex items-center justify-between border-b border-gaming-border pb-4">
                <div className="flex items-center gap-4">
                  <span className="text-3xl">{config.icon}</span>
                  <h2 className="text-2xl font-black gaming-text-primary">{config.name}</h2>
                  <div className={`gaming-status bg-${config.color}/20 border-${config.color} text-${config.color} px-3 py-1`}>
                    {activeGames.length} GAMES
                  </div>
                  {liveGames.length > 0 && (
                    <div className="gaming-status gaming-status-live">
                      <div className="gaming-pulse-dot"></div>
                      {liveGames.length} LIVE
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedSport(league as SportType)}
                    className="gaming-button-secondary px-4 py-2 text-sm"
                  >
                    View All {config.name}
                  </button>
                </div>
              </div>

              {/* Show Live Games First if any */}
              {liveGames.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 gaming-text-danger animate-pulse" />
                    <h3 className="text-lg font-bold gaming-text-danger">LIVE NOW</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {liveGames.slice(0, 6).map(renderGameCard)}
                  </div>
                </div>
              )}

              {/* Show Upcoming Games */}
              {upcomingGames.length > 0 && (
                <div className="space-y-4">
                  {liveGames.length > 0 && (
                    <div className="flex items-center gap-3">
                      <Calendar className="w-5 h-5 gaming-text-accent" />
                      <h3 className="text-lg font-bold gaming-text-primary">UPCOMING</h3>
                    </div>
                  )}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {upcomingGames.slice(0, liveGames.length > 0 ? 3 : 6).map(renderGameCard)}
                  </div>
                </div>
              )}

              {/* Show More Button if there are more games */}
              {activeGames.length > 6 && (
                <div className="text-center">
                  <button
                    onClick={() => setSelectedSport(league as SportType)}
                    className="gaming-button-primary px-6 py-3"
                  >
                    Show All {activeGames.length} {config.name} Games →
                  </button>
                </div>
              )}
            </div>
          );
        })}

        {/* Empty State if no games */}
        {Object.keys(gamesByLeague).length === 0 && (
          <div className="gaming-card text-center py-16">
            <div className="gaming-border-glow"></div>
            <Gamepad2 className="w-20 h-20 gaming-text-muted mx-auto mb-6" />
            <h3 className="text-2xl font-bold gaming-text-primary mb-4">NO GAMES AVAILABLE</h3>
            <p className="gaming-text-secondary">Check back later for upcoming matches</p>
          </div>
        )}
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

        {/* Unified Sports Command Center */}
        <div className="gaming-card">
          <div className="gaming-border-glow"></div>
          <div className="p-6 border-b border-gaming-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Trophy className="w-6 h-6 gaming-text-neon animate-pulse" />
                <span className="text-2xl gaming-text-primary font-bold">SPORTS COMMAND CENTER</span>
                <div className="gaming-status bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green">
                  {trendingGames.filter(g => g.status !== 'final').length} ACTIVE GAMES
                </div>
                {liveGames.length > 0 && (
                  <div className="gaming-status gaming-status-live">
                    <div className="gaming-pulse-dot"></div>
                    {liveGames.length} LIVE NOW
                  </div>
                )}
              </div>

              {/* Controls */}
              <div className="flex items-center gap-4 text-sm">
                {/* Date Selector */}
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 gaming-text-accent" />
                  <select
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="gaming-card px-3 py-1.5 border border-gaming-border rounded gaming-text-primary font-mono text-xs focus:border-gaming-neon-cyan focus:outline-none transition-colors cursor-pointer"
                  >
                    <option value="thisweek">This Week</option>
                    <option value="upcoming">Next 7 Days</option>
                    <option value="today">Today</option>
                    <option value={getDateString(1)}>Tomorrow</option>
                  </select>
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
                  REFRESH
                </Button>
              </div>
            </div>
          </div>

          {/* Sport Filter Tabs */}
          <div className="p-4 border-b border-gaming-border bg-gaming-bg/50">
            <div className="flex items-center gap-3 overflow-x-auto">
              {/* All Sports Tab */}
              <button
                onClick={() => setSelectedSport(null)}
                className={`
                  px-4 py-2 rounded-lg font-bold text-sm transition-all
                  ${!selectedSport
                    ? 'bg-gaming-neon-cyan/20 border border-gaming-neon-cyan text-gaming-neon-cyan'
                    : 'gaming-card border border-gaming-border hover:border-gaming-neon-cyan/50 gaming-text-secondary hover:gaming-text-primary'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span>🏆</span>
                  <span>ALL SPORTS</span>
                </div>
              </button>

              {/* Individual Sport Tabs */}
              {sportsTypes.map((sport) => (
                <button
                  key={sport.sport_type}
                  onClick={() => {
                    setSelectedSport(sport.sport_type);
                    console.log(`🏀 Selected sport: ${sport.sport_type}`);
                    toast.success(`🎮 Viewing ${getSportDisplayName(sport.sport_type)} games`);
                  }}
                  className={`
                    px-4 py-2 rounded-lg font-bold text-sm transition-all whitespace-nowrap
                    ${selectedSport === sport.sport_type
                      ? 'bg-gaming-neon-cyan/20 border border-gaming-neon-cyan text-gaming-neon-cyan'
                      : 'gaming-card border border-gaming-border hover:border-gaming-neon-cyan/50 gaming-text-secondary hover:gaming-text-primary'
                    }
                  `}
                >
                  <div className="flex items-center gap-2">
                    <span>{getSportEmoji(sport.sport_type)}</span>
                    <span>{getSportDisplayName(sport.sport_type)}</span>
                    <span className="text-xs opacity-70">({sport.count})</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Games Display Area */}
          <div className="p-6">
            {/* Show All Sports Grouped by League */}
            {!selectedSport ? (
              <div>
                {trendingGames.length > 0 ? (
                  renderGamesByLeague()
                ) : (
                  <div className="text-center py-12">
                    <Activity className="w-12 h-12 gaming-text-muted mx-auto mb-4" />
                    <p className="gaming-text-secondary text-lg">[NO GAMES] &gt;&gt; Try syncing data or adjusting date filter.</p>
                  </div>
                )}
              </div>
            ) : (
              /* Show Selected Sport Games */
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
  );
}