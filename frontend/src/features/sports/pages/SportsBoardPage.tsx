import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { SportsToolbar } from '../components/SportsToolbar';
import { GameCard } from '../components/GameCard';
import { Card } from '../../../components/common/Card';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';
import { 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline';
import type { ToolbarParams, GameData, GameLine } from '../types';
import { DEFAULT_TOOLBAR_PARAMS } from '../types';
import { games, leagues, markets, type Game, type Market } from '../api/sports';
import { throttledMap, sportsApiThrottler } from '../../../utils/requestThrottle';

export function SportsBoardPage() {
  const [params, setParams] = useState<ToolbarParams>(DEFAULT_TOOLBAR_PARAMS);
  const [gameData, setGameData] = useState<GameData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch games based on current parameters
  const fetchGames = useCallback(async () => {
    if (!params.selectedLeague) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch games for the selected league and date
      const gamesResult = await games({
        league: params.selectedLeague,
        date: params.selectedDate,
        team: params.selectedTeam,
      });

      // Transform games into GameData format and fetch moneylines for each
      // Use throttledMap to avoid rate limiting (429 errors)
      const transformedGames = await throttledMap(
        gamesResult,
        async (game: Game, index: number): Promise<GameData> => {
          let moneylines: GameLine[] = [];

          try {
            // Fetch moneyline markets for this game
            const gameMarkets = await markets({
              league: params.selectedLeague,
              game_id: game.id,
              kind: 'moneyline',
            });

            // Transform market lines into GameLine format
            moneylines = gameMarkets.flatMap((market: Market) => 
              (market.lines || []).map(line => ({
                id: line.id,
                team: line.side === 'home' ? game.home_team_name : game.away_team_name,
                side: line.side,
                odds_american: line.price_american,
                implied_probability: line.price_decimal ? 1 / line.price_decimal : 0,
              }))
            );
          } catch (marketError) {
            // Log error but don't fail the entire game fetch
            console.warn(`Failed to fetch markets for game ${game.id}:`, marketError);
            // Leave moneylines empty - GameCard will show "No moneylines available"
            moneylines = [];
          }

          return {
            id: game.id,
            league: game.league,
            away_team: game.away_team_name,
            home_team: game.home_team_name,
            game_date: game.start_time,
            status: game.status,
            venue: game.venue,
            moneylines,
          };
        },
        sportsApiThrottler
      );

      setGameData(transformedGames);
      
      if (transformedGames.length === 0) {
        toast.info(`No games found for ${params.selectedLeague} on ${params.selectedDate}`);
      } else {
        toast.success(`Found ${transformedGames.length} games`);
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch games';
      console.error('Failed to fetch games:', error);
      setError(errorMessage);
      toast.error(`Failed to load games: ${errorMessage}`);
      
      // Show sample data on API failure for development
      if (errorMessage.includes('Network error') || errorMessage.includes('fetch')) {
        console.log('Showing sample data due to network error');
        setGameData(getSampleGames(params.selectedLeague));
      }
    } finally {
      setLoading(false);
    }
  }, [params.selectedLeague, params.selectedDate, params.selectedTeam]);

  // Handle parameter changes from toolbar
  const handleParamsChange = useCallback((newParams: ToolbarParams) => {
    setParams(newParams);
  }, []);

  // Refresh games manually
  const handleRefresh = useCallback(() => {
    fetchGames();
  }, [fetchGames]);

  // Fetch games when key parameters change
  useEffect(() => {
    fetchGames();
  }, [params.selectedLeague, params.selectedDate, params.selectedTeam]);

  // Sample games for development/fallback
  const getSampleGames = (league: string): GameData[] => [
    {
      id: 'sample-1',
      league,
      away_team: 'Alabama Crimson Tide',
      home_team: 'Georgia Bulldogs',
      game_date: new Date().toISOString(),
      status: 'scheduled',
      venue: 'Sanford Stadium',
      moneylines: [
        {
          id: 'sample-1-away',
          team: 'Alabama Crimson Tide',
          side: 'away',
          odds_american: 110,
          implied_probability: 0.476,
        },
        {
          id: 'sample-1-home',
          team: 'Georgia Bulldogs',
          side: 'home',
          odds_american: -130,
          implied_probability: 0.565,
        },
      ],
    },
    {
      id: 'sample-2',
      league,
      away_team: 'Ohio State Buckeyes',
      home_team: 'Michigan Wolverines',
      game_date: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
      status: 'scheduled',
      venue: 'Michigan Stadium',
      moneylines: [
        {
          id: 'sample-2-away',
          team: 'Ohio State Buckeyes',
          side: 'away',
          odds_american: -150,
          implied_probability: 0.600,
        },
        {
          id: 'sample-2-home',
          team: 'Michigan Wolverines',
          side: 'home',
          odds_american: 125,
          implied_probability: 0.444,
        },
      ],
    },
  ];

  const totalRecommendedStakes = gameData.reduce((total, game) => {
    return total + game.moneylines.reduce((gameTotal, line) => {
      return gameTotal + ((line.recommended_stake && line.recommended_stake > 0) ? line.recommended_stake : 0);
    }, 0);
  }, 0);

  const positiveEVCount = gameData.reduce((count, game) => {
    return count + game.moneylines.filter(line => (line.edge || 0) > 0).length;
  }, 0);

  return (
    <div className="min-h-screen bg-dark-900 text-white">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
            <ChartBarIcon className="h-8 w-8 mr-3 text-green-400" />
            Sports Betting Board
          </h1>
          <p className="text-gray-400 text-lg">
            Real-time NCAAF moneylines with Kelly criterion stake recommendations
          </p>
        </div>

        {/* Toolbar */}
        <SportsToolbar
          params={params}
          onParamsChange={handleParamsChange}
          onRefresh={handleRefresh}
          loading={loading}
          gameCount={gameData.length}
        />

        {/* Stats Summary */}
        {gameData.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="glass rounded-lg p-4 border border-green-500/20 bg-green-500/5">
              <div className="text-green-300 text-sm font-medium">Games Found</div>
              <div className="text-green-400 text-2xl font-bold">{gameData.length}</div>
            </div>
            <div className="glass rounded-lg p-4 border border-blue-500/20 bg-blue-500/5">
              <div className="text-blue-300 text-sm font-medium">Positive EV Bets</div>
              <div className="text-blue-400 text-2xl font-bold">{positiveEVCount}</div>
            </div>
            <div className="glass rounded-lg p-4 border border-yellow-500/20 bg-yellow-500/5">
              <div className="text-yellow-300 text-sm font-medium">Total Recommended Stakes</div>
              <div className="text-yellow-400 text-2xl font-bold">${totalRecommendedStakes.toFixed(2)}</div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <Card className="py-12 text-center">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-gray-400 text-lg">Loading games...</p>
            <p className="text-gray-500 text-sm mt-2">
              Fetching {params.selectedLeague} games for {params.selectedDate}
            </p>
          </Card>
        )}

        {/* Error State */}
        {error && !loading && gameData.length === 0 && (
          <Card className="py-12 text-center border-red-500/20 bg-red-500/5">
            <ExclamationTriangleIcon className="h-16 w-16 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-red-300 mb-2">
              Failed to Load Games
            </h3>
            <p className="text-red-400 mb-4 max-w-md mx-auto">
              {error}
            </p>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </Card>
        )}

        {/* Games Grid */}
        <AnimatePresence mode="wait">
          {!loading && gameData.length > 0 && (
            <motion.div
              key="games-grid"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {gameData.map((game, index) => (
                <motion.div
                  key={game.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <GameCard
                    game={game}
                    params={params}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* No Games Found */}
          {!loading && gameData.length === 0 && !error && (
            <motion.div
              key="no-games"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Card className="py-12 text-center">
                <InformationCircleIcon className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-300 mb-2">
                  No Games Found
                </h3>
                <p className="text-gray-400 mb-4 max-w-md mx-auto">
                  No {params.selectedLeague} games found for {params.selectedDate}
                  {params.selectedTeam && ` involving ${params.selectedTeam}`}.
                </p>
                <p className="text-gray-500 text-sm mb-4">
                  Try selecting a different date or league, or remove team filters.
                </p>
                <button
                  onClick={handleRefresh}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                >
                  Refresh
                </button>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Help Section */}
        <div className="mt-8">
          <Card>
            <h3 className="text-lg font-semibold text-white mb-3">How to Use the Sports Board</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-300">
              <div className="space-y-2">
                <p><strong>Kelly Stakes:</strong> Optimal bet size based on your edge and bankroll</p>
                <p><strong>Positive EV:</strong> Green badges indicate profitable betting opportunities</p>
                <p><strong>High Kelly Warning:</strong> Stakes over 10% of bankroll are flagged</p>
              </div>
              <div className="space-y-2">
                <p><strong>Debounced Updates:</strong> Parameters update after 200ms of no changes</p>
                <p><strong>Real-time Data:</strong> Refresh button fetches latest odds</p>
                <p><strong>Team Filter:</strong> Optional team name search to find specific matchups</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}