/**
 * Professional Sports Betting Hub Dashboard
 * 
 * Real-time sports data across 12+ leagues with professional betting interface
 * Featuring live games, trending matches, and comprehensive sports coverage
 * 
 * LIVE DATA SOURCES:
 * ✅ ESPN API - Live scores, schedules, team stats
 * ✅ TheSportsDB - Team info, venues, historical data  
 * ✅ The Odds API - Betting lines and market data
 * ✅ Real-time WebSocket updates for live games
 */

import React, { useState, useEffect } from 'react';
import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../../components/common/Tabs';
import { Select, SelectItem } from '../../../components/common/Select';
import { toast } from 'sonner';
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
  Signal
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
  formatTeamRecord,
  getTodayDateString
} from '../api/sports';

interface SportsType {
  sport_type: SportType;
  name: string;
  count: number;
}

export default function MultiSportsDashboard() {
  const [selectedSport, setSelectedSport] = useState<SportType>(SportType.NFL);
  const [selectedDate, setSelectedDate] = useState<string>(getTodayDateString());
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  
  // Data state
  const [sportsTypes, setSportsTypes] = useState<SportsType[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [liveGames, setLiveGames] = useState<Game[]>([]);
  const [trendingGames, setTrendingGames] = useState<Game[]>([]);

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
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (selectedSport) {
      loadGamesForSport();
    }
  }, [selectedSport, selectedDate]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load all data in parallel
      const [sportsTypesData, liveGamesData, trendingGamesData] = await Promise.all([
        getSportsTypes(),
        getLiveGames(),
        getTrendingGames(20)
      ]);

      setSportsTypes(sportsTypesData);
      setLiveGames(liveGamesData);
      setTrendingGames(trendingGamesData);

      // Set default sport to the one with the most leagues
      if (sportsTypesData.length > 0) {
        const defaultSport = sportsTypesData.reduce((prev, current) => 
          prev.count > current.count ? prev : current
        );
        setSelectedSport(defaultSport.sport_type);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load sports data');
    } finally {
      setLoading(false);
    }
  };

  const loadGamesForSport = async () => {
    if (!selectedSport) return;

    try {
      const [leaguesData, gamesData] = await Promise.all([
        listLeagues(selectedSport),
        getGamesBySport(selectedSport, selectedDate)
      ]);

      setLeagues(leaguesData);
      setGames(gamesData);
    } catch (error) {
      console.error('Error loading games for sport:', error);
      toast.error(`Failed to load ${getSportDisplayName(selectedSport)} games`);
    }
  };

  const handleSyncData = async () => {
    setSyncing(true);
    try {
      const result = await syncSportsData({
        leagues: true,
        teams: true,
        games: true,
        odds: true,
        sport: selectedSport
      });

      if (result.success) {
        toast.success(result.message);
        await loadDashboardData();
        await loadGamesForSport();
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      console.error('Error syncing data:', error);
      toast.error('Failed to sync sports data');
    } finally {
      setSyncing(false);
    }
  };

  const renderGameCard = (game: Game, contextSport?: SportType) => {
    const isLive = isGameLive(game);
    const isFinished = isGameFinished(game);
    const isScheduled = game.status === 'scheduled';
    const sportType = contextSport || getSportTypeFromLeague(game.league);
    
    return (
      <Card 
        key={game.id} 
        hover
        className={`
          relative transition-all duration-300
          ${isLive ? 'ring-2 ring-red-500 shadow-lg shadow-red-500/20' : ''} 
          ${isFinished ? 'ring-1 ring-green-500/50' : ''}
          ${isScheduled ? 'ring-1 ring-primary-500/50' : ''}
          border-l-4 ${isLive ? 'border-l-red-500' : isFinished ? 'border-l-green-500' : 'border-l-primary-500'}
        `}
      >
        {/* Live indicator overlay */}
        {isLive && (
          <div className="absolute top-3 right-3 flex items-center space-x-1">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-xs font-bold text-red-400 uppercase tracking-wide">Live</span>
          </div>
        )}

        <div className="space-y-4">
          {/* Header with status and venue */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Badge 
                variant={isLive ? 'destructive' : isFinished ? 'success' : 'default'}
                className={`
                  font-bold text-xs px-3 py-1 flex items-center gap-1
                  ${isLive ? 'animate-pulse' : ''}
                `}
              >
                {isLive && <Zap className="w-3 h-3" />}
                {isFinished && <Trophy className="w-3 h-3" />}
                {isScheduled && <Timer className="w-3 h-3" />}
                {getGameStatusDisplay(game.status)}
              </Badge>
              
              {/* Sport emoji */}
              <div className="text-lg">{getSportEmoji(sportType)}</div>
            </div>

            {game.venue_name && (
              <div className="text-xs text-gray-400 flex items-center bg-dark-800 px-2 py-1 rounded-full">
                <MapPin className="w-3 h-3 mr-1" />
                <span className="font-medium">{game.venue_name}</span>
              </div>
            )}
          </div>

          {/* Teams matchup */}
          <div className="space-y-3">
            {/* Away Team */}
            <div className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg border border-dark-700">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-dark-700 rounded-full flex items-center justify-center">
                  <span className="text-xs font-bold text-gray-400">A</span>
                </div>
                <div>
                  <div className="font-bold text-white">{game.away_team_name}</div>
                  {game.away_team.current_record && (
                    <div className="text-xs text-gray-400 font-medium">
                      ({formatTeamRecord(game.away_team.current_record)})
                    </div>
                  )}
                </div>
              </div>
              {game.away_score !== null && (
                <div className="text-2xl font-bold text-white bg-dark-700 px-3 py-1 rounded-lg">
                  {game.away_score}
                </div>
              )}
            </div>

            {/* VS Divider */}
            <div className="flex items-center justify-center">
              <div className="bg-primary-500/20 px-3 py-1 rounded-full">
                <span className="text-xs font-bold text-primary-400">VS</span>
              </div>
            </div>

            {/* Home Team */}
            <div className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg border border-dark-700">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-500/20 rounded-full flex items-center justify-center">
                  <span className="text-xs font-bold text-primary-400">H</span>
                </div>
                <div>
                  <div className="font-bold text-white">{game.home_team_name}</div>
                  {game.home_team.current_record && (
                    <div className="text-xs text-gray-400 font-medium">
                      ({formatTeamRecord(game.home_team.current_record)})
                    </div>
                  )}
                </div>
              </div>
              {game.home_score !== null && (
                <div className="text-2xl font-bold text-white bg-dark-700 px-3 py-1 rounded-lg">
                  {game.home_score}
                </div>
              )}
            </div>
          </div>

          {/* Footer with game details */}
          <div className="pt-4 border-t border-dark-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1 text-xs text-gray-400">
                <Clock className="w-3 h-3" />
                <span className="font-medium">{formatGameTime(game.scheduled_start)}</span>
              </div>
              <div className="flex items-center space-x-2">
                {game.week && (
                  <Badge variant="outline" className="text-xs">Week {game.week}</Badge>
                )}
                {game.season && (
                  <Badge variant="outline" className="text-xs">{game.season}</Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>
    );
  };

  const renderSportsOverview = () => (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
      {sportsTypes.map((sport) => (
        <Card 
          key={sport.sport_type}
          hover
          className={`
            cursor-pointer transition-all duration-300
            ${selectedSport === sport.sport_type 
              ? 'ring-2 ring-primary-500 shadow-lg shadow-primary-500/20' 
              : ''
            }
            border-t-4 border-t-primary-500
          `}
          onClick={() => setSelectedSport(sport.sport_type)}
        >
          <div className="p-6 text-center space-y-3">
            <div className="text-4xl transform transition-transform hover:scale-110">
              {getSportEmoji(sport.sport_type)}
            </div>
            <div className="font-bold text-sm text-white">
              {getSportDisplayName(sport.sport_type)}
            </div>
            <div className="flex items-center justify-center">
              <Badge variant="secondary" className="text-xs px-2 py-1">
                {sport.count} league{sport.count !== 1 ? 's' : ''}
              </Badge>
            </div>
            {selectedSport === sport.sport_type && (
              <div className="flex justify-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
              </div>
            )}
          </div>
        </Card>
      ))}
    </div>
  );

  const renderLiveGames = () => (
    <div className="space-y-6">
      {/* Live Games Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Zap className="w-6 h-6 text-red-500 animate-pulse" />
            <h3 className="text-2xl font-bold text-white">Live Games</h3>
          </div>
          <Badge variant="destructive" className="px-3 py-1 font-bold animate-pulse">
            {liveGames.length} LIVE
          </Badge>
        </div>
        
        {/* Real-time indicator */}
        <div className="flex items-center space-x-2 bg-green-500/20 px-3 py-2 rounded-full border border-green-500/30">
          <Signal className="w-4 h-4 text-green-400" />
          <span className="text-sm font-bold text-green-400">REAL-TIME DATA</span>
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      {liveGames.length === 0 ? (
        <Card className="border-2 border-dashed border-dark-700">
          <div className="p-8 text-center space-y-4">
            <Activity className="w-12 h-12 text-gray-400 mx-auto" />
            <h4 className="text-lg font-semibold text-gray-300">No Live Games</h4>
            <p className="text-gray-500">Check back during game times for live action!</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {liveGames.map(renderGameCard)}
        </div>
      )}
    </div>
  );

  const renderTrendingGames = () => (
    <div className="space-y-6">
      {/* Trending Games Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-6 h-6 text-green-400" />
            <h3 className="text-2xl font-bold text-white">Trending Games</h3>
          </div>
          <Badge variant="success" className="px-3 py-1 font-bold">
            {trendingGames.length} HOT
          </Badge>
        </div>
        
        {/* Data source indicator */}
        <div className="flex items-center space-x-2 bg-blue-500/20 px-3 py-2 rounded-full border border-blue-500/30">
          <Database className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-bold text-blue-400">ESPN + ODDS API</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {trendingGames.slice(0, 12).map(renderGameCard)}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-4">
        <div className="relative">
          <RefreshCw className="w-12 h-12 animate-spin text-primary-500" />
          <div className="absolute inset-0 w-12 h-12 border-4 border-primary-500/20 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <div className="text-center space-y-2">
          <h3 className="text-lg font-semibold text-white">Loading Sports Data</h3>
          <p className="text-gray-400">Fetching live data from ESPN, TheSportsDB, and The Odds API...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Professional Header */}
      <div className="glass-dark rounded-xl p-8">
        <div className="flex items-center justify-between">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-primary-400" />
              </div>
              <h1 className="text-4xl font-bold text-white">Sports Betting Hub</h1>
            </div>
            
            {/* Live data indicators */}
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2 bg-green-500/20 px-3 py-1 rounded-full">
                <Wifi className="w-4 h-4 text-green-400" />
                <span className="text-sm font-bold text-green-400">LIVE ESPN DATA</span>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              </div>
              
              <div className="flex items-center space-x-2 bg-blue-500/20 px-3 py-1 rounded-full">
                <Database className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-bold text-blue-400">THESPORTSDB</span>
              </div>
              
              <div className="flex items-center space-x-2 bg-purple-500/20 px-3 py-1 rounded-full">
                <TrendingUp className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-bold text-purple-400">ODDS API</span>
              </div>
            </div>
            
            <p className="text-gray-300 text-lg">
              Professional sports betting intelligence with real-time data from multiple sources
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Live games counter */}
            {liveGames.length > 0 && (
              <div className="bg-red-500/20 border border-red-500/30 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-red-400 animate-pulse" />
                  <span className="font-bold text-red-400">{liveGames.length} LIVE</span>
                </div>
              </div>
            )}
            
            <Button
              onClick={handleSyncData}
              disabled={syncing}
              variant="secondary"
            >
              {syncing ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Sync Data
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-8">

        {/* Sports Overview */}
        <Card className="border-t-4 border-t-primary-500">
          <div className="p-6 border-b border-dark-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Star className="w-6 h-6 text-primary-400" />
                <span className="text-xl text-white">Sports Coverage</span>
                <Badge variant="secondary" className="ml-2">
                  {sportsTypes.length} Sports Available
                </Badge>
              </div>
              
              {/* Coverage stats */}
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-1 text-gray-400">
                  <Trophy className="w-4 h-4" />
                  <span>{sportsTypes.reduce((sum, sport) => sum + sport.count, 0)} Total Leagues</span>
                </div>
              </div>
            </div>
          </div>
          <div className="p-6">
            {renderSportsOverview()}
          </div>
        </Card>

        {/* Main Content Tabs */}
        <Card>
          <div className="p-6">
            <Tabs defaultValue="live" className="space-y-6">
              <div className="flex items-center justify-between">
                <TabsList>
                  <TabsTrigger value="live" className="font-bold">
                    <Zap className="w-4 h-4 mr-2" />
                    Live Games
                  </TabsTrigger>
                  <TabsTrigger value="trending" className="font-bold">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Trending
                  </TabsTrigger>
                  <TabsTrigger value="sport" className="font-bold">
                    <Trophy className="w-4 h-4 mr-2" />
                    By Sport
                  </TabsTrigger>
                </TabsList>

                {/* Enhanced Date Selector */}
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="input text-sm"
                  />
                </div>
              </div>

        <TabsContent value="live">
          {renderLiveGames()}
        </TabsContent>

        <TabsContent value="trending">
          {renderTrendingGames()}
        </TabsContent>

              <TabsContent value="sport">
                <div className="space-y-6">
                  {/* Enhanced Sport and League Selector */}
                  <div className="glass-dark p-6 rounded-lg border border-dark-700">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-white">Sport Selection</h3>
                      <div className="flex items-center space-x-2 text-sm text-gray-400">
                        <Database className="w-4 h-4" />
                        <span>Real-time league data</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <Select 
                        value={selectedSport} 
                        onValueChange={(value) => setSelectedSport(value as SportType)}
                      >
                        {sportsTypes.map((sport) => (
                          <SelectItem key={sport.sport_type} value={sport.sport_type}>
                            <div className="flex items-center space-x-3 py-1">
                              <span className="text-lg">{getSportEmoji(sport.sport_type)}</span>
                              <span className="font-medium">{getSportDisplayName(sport.sport_type)}</span>
                              <Badge variant="outline" className="ml-auto">
                                {sport.count} leagues
                              </Badge>
                            </div>
                          </SelectItem>
                        ))}
                      </Select>

                      {leagues.length > 0 && (
                        <div className="flex items-center space-x-2 bg-green-500/20 px-4 py-2 rounded-lg border border-green-500/30">
                          <Users className="w-4 h-4 text-green-400" />
                          <span className="text-sm font-medium text-green-400">
                            {leagues.length} active league{leagues.length !== 1 ? 's' : ''}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Games for Selected Sport */}
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-3xl">{getSportEmoji(selectedSport)}</span>
                        <div>
                          <h3 className="text-2xl font-bold text-white">
                            {getSportDisplayName(selectedSport)} Games
                          </h3>
                          <p className="text-gray-400">Live data from ESPN and partner APIs</p>
                        </div>
                        <Badge variant="outline" className="font-bold px-3 py-1">
                          {games.length} games
                        </Badge>
                      </div>
                    </div>

                    {games.length === 0 ? (
                      <Card className="border-2 border-dashed border-dark-700">
                        <div className="p-12 text-center space-y-4">
                          <div className="text-6xl text-gray-500">{getSportEmoji(selectedSport)}</div>
                          <div>
                            <h4 className="text-lg font-semibold text-gray-300 mb-2">
                              No games found for {getSportDisplayName(selectedSport)}
                            </h4>
                            <p className="text-gray-500">
                              Try selecting a different date or sync data to get the latest games
                            </p>
                          </div>
                          <Button 
                            onClick={handleSyncData} 
                            variant="outline" 
                            className="mt-4"
                            disabled={syncing}
                          >
                            {syncing ? (
                              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <RefreshCw className="w-4 h-4 mr-2" />
                            )}
                            Sync Latest Data
                          </Button>
                        </div>
                      </Card>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {games.map(game => renderGameCard(game, selectedSport))}
                      </div>
                    )}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </Card>
      </div>
    </div>
  );
}