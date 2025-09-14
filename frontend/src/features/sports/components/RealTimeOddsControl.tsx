import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { RefreshCw, Wifi, WifiOff, Clock, Activity } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { formatDistanceToNow } from 'date-fns';

interface GameStatus {
  game_id: string;
  matchup: string;
  league: string;
  status: string;
  start_time: string;
  last_odds_update: string | null;
  cache_status: 'fresh' | 'stale' | 'no_data';
  markets_count: number;
}

interface UpdateResult {
  games_enriched?: number;
  odds_added?: number;
  api_calls?: number;
  from_cache?: number;
  errors?: string[];
}

export const RealTimeOddsControl: React.FC = () => {
  const [games, setGames] = useState<GameStatus[]>([]);
  const [selectedLeague, setSelectedLeague] = useState<string>('all');
  const [updating, setUpdating] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [updateResult, setUpdateResult] = useState<UpdateResult | null>(null);

  // WebSocket connection
  const {
    isConnected,
    sendMessage,
    lastMessage
  } = useWebSocket('/ws/sports/updates/', {
    onOpen: () => {
      console.log('Connected to sports updates WebSocket');
      // Get initial status
      sendMessage({
        type: 'get_update_status',
        league: selectedLeague
      });
    },
    onMessage: (data) => {
      handleWebSocketMessage(data);
    }
  });

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'status_update':
        setGames(data.status || []);
        setLastUpdate(new Date());
        break;

      case 'update_started':
        setUpdating(data.game_id || data.league);
        break;

      case 'update_complete':
        setUpdating(null);
        setUpdateResult(data.result);
        // Refresh status after update
        sendMessage({
          type: 'get_update_status',
          league: selectedLeague
        });
        break;

      case 'update_failed':
        setUpdating(null);
        console.error('Update failed:', data.error);
        break;

      case 'odds_updated':
      case 'league_updated':
        // Refresh the games list
        sendMessage({
          type: 'get_update_status',
          league: selectedLeague
        });
        break;
    }
  };

  const forceUpdateGame = (gameId: string) => {
    if (!isConnected) return;

    setUpdating(gameId);
    sendMessage({
      type: 'force_odds_update',
      game_id: gameId
    });
  };

  const forceUpdateLeague = (league: string) => {
    if (!isConnected) return;

    setUpdating(league);
    sendMessage({
      type: 'force_odds_update',
      league: league
    });
  };

  const refreshStatus = () => {
    if (!isConnected) return;

    sendMessage({
      type: 'get_update_status',
      league: selectedLeague
    });
  };

  const getCacheStatusColor = (status: string) => {
    switch (status) {
      case 'fresh':
        return 'bg-green-100 text-green-800';
      case 'stale':
        return 'bg-yellow-100 text-yellow-800';
      case 'no_data':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getGameStatusColor = (status: string) => {
    if (status === 'live' || status === 'status_in_progress') {
      return 'bg-red-100 text-red-800';
    } else if (status === 'scheduled' || status === 'status_scheduled') {
      return 'bg-blue-100 text-blue-800';
    }
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Real-Time Odds Control
          </CardTitle>
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Badge className="bg-green-100 text-green-800">
                <Wifi className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            ) : (
              <Badge className="bg-red-100 text-red-800">
                <WifiOff className="h-3 w-3 mr-1" />
                Disconnected
              </Badge>
            )}
            {lastUpdate && (
              <span className="text-sm text-gray-500">
                Updated {formatDistanceToNow(lastUpdate, { addSuffix: true })}
              </span>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* League Filter and Controls */}
        <div className="flex gap-2 mb-4">
          <select
            value={selectedLeague}
            onChange={(e) => {
              setSelectedLeague(e.target.value);
              sendMessage({
                type: 'get_update_status',
                league: e.target.value
              });
            }}
            className="px-3 py-2 border rounded-md"
          >
            <option value="all">All Leagues</option>
            <option value="NFL">NFL</option>
            <option value="NCAAF">NCAAF</option>
            <option value="NBA">NBA</option>
            <option value="NCAAB">NCAAB</option>
          </select>

          <Button
            onClick={refreshStatus}
            disabled={!isConnected}
            variant="outline"
            size="sm"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh Status
          </Button>

          <Button
            onClick={() => forceUpdateLeague(selectedLeague === 'all' ? 'NFL' : selectedLeague)}
            disabled={!isConnected || updating !== null}
            variant="default"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${updating ? 'animate-spin' : ''}`} />
            Force Update {selectedLeague === 'all' ? 'All' : selectedLeague}
          </Button>
        </div>

        {/* Update Result Alert */}
        {updateResult && (
          <Alert className="mb-4">
            <AlertDescription>
              <div className="flex items-center justify-between">
                <div>
                  ✅ Updated {updateResult.games_enriched || 0} games with {updateResult.odds_added || 0} odds
                </div>
                <div className="text-sm text-gray-500">
                  API Calls: {updateResult.api_calls || 0} | From Cache: {updateResult.from_cache || 0}
                </div>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Games List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {games.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No games found. Try refreshing the status.
            </div>
          ) : (
            games.map((game) => (
              <div
                key={game.game_id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Badge className={getGameStatusColor(game.status)}>
                      {game.status}
                    </Badge>
                    <span className="font-medium">{game.matchup}</span>
                    <Badge variant="outline">{game.league}</Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(game.start_time).toLocaleString()}
                    </span>
                    {game.last_odds_update && (
                      <span>
                        Last update: {formatDistanceToNow(new Date(game.last_odds_update), { addSuffix: true })}
                      </span>
                    )}
                    <span>{game.markets_count} markets</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Badge className={getCacheStatusColor(game.cache_status)}>
                    {game.cache_status}
                  </Badge>
                  <Button
                    onClick={() => forceUpdateGame(game.game_id)}
                    disabled={!isConnected || updating === game.game_id}
                    variant="outline"
                    size="sm"
                  >
                    {updating === game.game_id ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Live Updater Status */}
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600">
            <div className="font-medium mb-1">💡 Auto-Update Schedule:</div>
            <div className="space-y-1">
              <div>• Live games: Updates every 30 minutes</div>
              <div>• Upcoming games: Updates every 2 hours</div>
              <div>• Pre-game (1hr before): Updates every 30 minutes</div>
            </div>
            <div className="mt-2">
              Run <code className="bg-gray-200 px-1 rounded">python manage.py live_odds_updater</code> for automatic updates
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};