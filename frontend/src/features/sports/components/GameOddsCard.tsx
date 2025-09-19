import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, DollarSign, Calendar, MapPin, Users } from 'lucide-react';
import { format } from 'date-fns';
import { getGameOdds, getMarkets, Game, BettingMarket, OddsLine } from '../api/sports';
import { cn } from '@/lib/utils';

interface GameOddsCardProps {
  game: Game;
  onSelectGame?: (game: Game) => void;
}

export function GameOddsCard({ game, onSelectGame }: GameOddsCardProps) {
  const [markets, setMarkets] = useState<BettingMarket[]>([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (expanded) {
      loadMarkets();
    }
  }, [expanded, game.id]);

  const loadMarkets = async () => {
    try {
      setLoading(true);
      const marketsData = await getMarkets({ game_id: game.id });
      setMarkets(marketsData || []);
    } catch (error) {
      console.error('Failed to load markets:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatOdds = (odds: number) => {
    if (!odds) return '-';
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live':
        return 'bg-red-500';
      case 'scheduled':
        return 'bg-blue-500';
      case 'final':
        return 'bg-muted/50';
      default:
        return 'bg-gray-400';
    }
  };

  const gameDate = new Date(game.scheduled_start);
  const isToday = new Date().toDateString() === gameDate.toDateString();
  const isTomorrow = new Date(Date.now() + 86400000).toDateString() === gameDate.toDateString();

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setExpanded(!expanded)}>
      <div className="p-4">
        {/* Game Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Badge className={cn(getStatusColor(game.status), 'text-foreground')}>
              {game.status.toUpperCase()}
            </Badge>
            {game.league && (
              <Badge variant="outline">{game.league}</Badge>
            )}
          </div>
          <div className="text-sm text-muted-foreground flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {isToday ? 'Today' : isTomorrow ? 'Tomorrow' : format(gameDate, 'MMM d')}
            {' • '}
            {format(gameDate, 'h:mm a')}
          </div>
        </div>

        {/* Teams */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-lg font-semibold">
                {game.away_team_name || game.away_team?.name}
              </div>
              {game.away_score !== null && (
                <div className="text-2xl font-bold">{game.away_score}</div>
              )}
            </div>
            {markets.length > 0 && markets[0].odds_lines?.length > 0 && (
              <Badge variant="secondary" className="font-mono">
                {formatOdds(markets[0].odds_lines[0].away_odds)}
              </Badge>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-lg font-semibold">
                {game.home_team_name || game.home_team?.name}
              </div>
              {game.home_score !== null && (
                <div className="text-2xl font-bold">{game.home_score}</div>
              )}
            </div>
            {markets.length > 0 && markets[0].odds_lines?.length > 0 && (
              <Badge variant="secondary" className="font-mono">
                {formatOdds(markets[0].odds_lines[0].home_odds)}
              </Badge>
            )}
          </div>
        </div>

        {/* Venue */}
        {game.venue_name && (
          <div className="mt-3 pt-3 border-t flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-3 w-3" />
            {game.venue_name}
            {game.venue_city && `, ${game.venue_city}`}
          </div>
        )}

        {/* Expanded Markets */}
        {expanded && (
          <div className="mt-4 pt-4 border-t space-y-3">
            {loading ? (
              <div className="text-center py-4 text-muted-foreground">
                Loading odds...
              </div>
            ) : markets.length > 0 ? (
              markets.map((market) => (
                <div key={market.id} className="space-y-2">
                  <div className="font-medium text-sm">{market.market_type}</div>
                  <div className="grid grid-cols-2 gap-2">
                    {market.odds_lines?.map((line) => (
                      <div key={line.id} className="flex items-center justify-between text-sm bg-secondary/20 rounded px-2 py-1">
                        <span className="text-xs text-muted-foreground">{line.sportsbook}</span>
                        <span className="font-mono">
                          {line.home_odds && formatOdds(line.home_odds)}
                          {line.away_odds && ` / ${formatOdds(line.away_odds)}`}
                          {line.total_line && ` O/U ${line.total_line}`}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-muted-foreground">
                No odds available
              </div>
            )}
            
            {onSelectGame && (
              <Button 
                className="w-full mt-3"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectGame(game);
                }}
              >
                <DollarSign className="h-4 w-4 mr-2" />
                View Betting Options
              </Button>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}