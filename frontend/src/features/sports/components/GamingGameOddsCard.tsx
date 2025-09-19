import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Calendar, 
  MapPin, 
  Users,
  FireIcon,
  BoltIcon,
  TrophyIcon,
  ClockIcon
} from 'lucide-react';
import { format } from 'date-fns';
import { getGameOdds, getMarkets, Game, BettingMarket, OddsLine } from '../api/sports';
import { formatGameTime, formatTimeOnlyMST } from '../../../utils/dateFormatting';

interface GamingGameOddsCardProps {
  game: Game;
  onSelectGame?: (game: Game) => void;
}

export function GamingGameOddsCard({ game, onSelectGame }: GamingGameOddsCardProps) {
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

  const getGamingStatus = (status: string) => {
    switch (status) {
      case 'live':
        return (
          <div className="bg-card bg-card">
            <div className="bg-card"></div>
            LIVE
          </div>
        );
      case 'scheduled':
        return (
          <div className="bg-card">
            <ClockIcon className="w-3 h-3 mr-1" />
            SCHEDULED
          </div>
        );
      case 'final':
        return (
          <div className="bg-card">
            <TrophyIcon className="w-3 h-3 mr-1" />
            FINAL
          </div>
        );
      default:
        return (
          <div className="bg-card">
            {status.toUpperCase()}
          </div>
        );
    }
  };

  const { day, time } = formatGameTime(game.scheduled_start);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-card bg-card cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Gaming Border Glow Effect */}
      <div className="bg-card"></div>
      
      <div className="space-y-4">
        {/* Gaming Header */}
        <div className="bg-card">
          <div className="flex items-center gap-3">
            {getGamingStatus(game.status)}
            {game.league && (
              <div className="bg-card">{game.league}</div>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm bg-card">
            <Calendar className="h-3 w-3" />
            {day}
            <span className="bg-card">•</span>
            {time} MST
          </div>
        </div>

        {/* Gaming Team Matchup */}
        <div className="bg-card">
          {/* Away Team */}
          <div className="bg-card">
            <div className="bg-card">
              {(game.away_team_name || game.away_team?.name || 'AWAY').substring(0, 2).toUpperCase()}
            </div>
            <div className="bg-card">
              <div className="bg-card">
                {game.away_team_name || game.away_team?.name || 'Away Team'}
              </div>
              <div className="bg-card">AWAY</div>
            </div>
            {game.away_score !== null && (
              <div className="bg-card">
                {game.away_score}
              </div>
            )}
            {markets.length > 0 && markets[0].odds_lines?.length > 0 && (
              <div className="bg-card ml-auto">
                <div className="bg-card">
                  {formatOdds(markets[0].odds_lines[0].away_odds)}
                </div>
              </div>
            )}
          </div>

          {/* Gaming VS Divider */}
          <div className="bg-card">
            <div className="bg-card">VS</div>
            <div className="bg-card"></div>
          </div>

          {/* Home Team */}
          <div className="bg-card">
            <div className="bg-card bg-card">
              {(game.home_team_name || game.home_team?.name || 'HOME').substring(0, 2).toUpperCase()}
            </div>
            <div className="bg-card">
              <div className="bg-card">
                {game.home_team_name || game.home_team?.name || 'Home Team'}
              </div>
              <div className="bg-card">HOME</div>
            </div>
            {game.home_score !== null && (
              <div className="bg-card bg-card">
                {game.home_score}
              </div>
            )}
            {markets.length > 0 && markets[0].odds_lines?.length > 0 && (
              <div className="bg-card ml-auto">
                <div className="bg-card">
                  {formatOdds(markets[0].odds_lines[0].home_odds)}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gaming Venue */}
        {game.venue_name && (
          <div className="flex items-center gap-2 bg-card text-sm pt-3 border-t border-bg-card">
            <MapPin className="h-3 w-3" />
            <span>{game.venue_name}</span>
            {game.venue_city && (
              <>
                <span className="bg-card">•</span>
                <span>{game.venue_city}</span>
              </>
            )}
          </div>
        )}

        {/* Expanded Gaming Markets */}
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="bg-card"
          >
            <div className="flex items-center gap-2 mb-4">
              <h4 className="text-sm font-bold bg-card">BETTING MARKETS</h4>
              <div className="w-16 h-0.5 bg-bg-card rounded"></div>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="bg-card mx-auto mb-2"></div>
                <div className="bg-card">Loading odds...</div>
              </div>
            ) : markets.length > 0 ? (
              <div className="space-y-4">
                {markets.map((market) => (
                  <div key={market.id} className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="bg-card font-bold">{market.market_type}</span>
                      <div className="w-8 h-0.5 bg-bg-card rounded"></div>
                    </div>
                    
                    <div className="bg-card">
                      {market.odds_lines?.map((line) => (
                        <div key={line.id} className="bg-card">
                          <div className="bg-card mb-2">{line.sportsbook}</div>
                          <div className="space-y-1">
                            {line.home_odds && (
                              <div className="bg-card text-sm">
                                H: {formatOdds(line.home_odds)}
                              </div>
                            )}
                            {line.away_odds && (
                              <div className="bg-card text-sm">
                                A: {formatOdds(line.away_odds)}
                              </div>
                            )}
                            {line.total_line && (
                              <div className="bg-card text-xs bg-card">
                                O/U {line.total_line}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-card text-center py-8">
                <TrendingDown className="w-12 h-12 mx-auto mb-4 bg-card" />
                <div className="bg-card mb-2">NO ODDS AVAILABLE</div>
                <p className="bg-card">Check back later for updates</p>
              </div>
            )}
            
            {/* Gaming Action Button */}
            {onSelectGame && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-card bg-card w-full mt-6 bg-card"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectGame(game);
                }}
              >
                <div className="bg-card"></div>
                <div className="flex items-center justify-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  <span className="bg-card font-bold">VIEW BETTING OPTIONS</span>
                </div>
              </motion.button>
            )}
          </motion.div>
        )}

        {/* Expansion Indicator */}
        <div className="flex items-center justify-center pt-2">
          <motion.div
            animate={{ rotate: expanded ? 180 : 0 }}
            className="w-6 h-6 bg-card"
          >
            <TrendingDown className="w-full h-full" />
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}