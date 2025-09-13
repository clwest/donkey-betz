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
          <div className="gaming-status gaming-status-live">
            <div className="gaming-pulse-dot"></div>
            LIVE
          </div>
        );
      case 'scheduled':
        return (
          <div className="gaming-status">
            <ClockIcon className="w-3 h-3 mr-1" />
            SCHEDULED
          </div>
        );
      case 'final':
        return (
          <div className="gaming-status">
            <TrophyIcon className="w-3 h-3 mr-1" />
            FINAL
          </div>
        );
      default:
        return (
          <div className="gaming-status">
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
      className="gaming-card gaming-hover-lift cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Gaming Border Glow Effect */}
      <div className="gaming-border-glow"></div>
      
      <div className="space-y-4">
        {/* Gaming Header */}
        <div className="gaming-header">
          <div className="flex items-center gap-3">
            {getGamingStatus(game.status)}
            {game.league && (
              <div className="gaming-league">{game.league}</div>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm gaming-text-muted">
            <Calendar className="h-3 w-3" />
            {day}
            <span className="gaming-text-accent">•</span>
            {time} MST
          </div>
        </div>

        {/* Gaming Team Matchup */}
        <div className="gaming-matchup">
          {/* Away Team */}
          <div className="gaming-team">
            <div className="gaming-team-avatar">
              {(game.away_team_name || game.away_team?.name || 'AWAY').substring(0, 2).toUpperCase()}
            </div>
            <div className="gaming-team-info">
              <div className="gaming-team-name">
                {game.away_team_name || game.away_team?.name || 'Away Team'}
              </div>
              <div className="gaming-team-record">AWAY</div>
            </div>
            {game.away_score !== null && (
              <div className="gaming-score">
                {game.away_score}
              </div>
            )}
            {markets.length > 0 && markets[0].odds_lines?.length > 0 && (
              <div className="gaming-bet-option ml-auto">
                <div className="gaming-bet-odds">
                  {formatOdds(markets[0].odds_lines[0].away_odds)}
                </div>
              </div>
            )}
          </div>

          {/* Gaming VS Divider */}
          <div className="gaming-vs-divider">
            <div className="gaming-vs-text">VS</div>
            <div className="gaming-progress-bar"></div>
          </div>

          {/* Home Team */}
          <div className="gaming-team">
            <div className="gaming-team-avatar gaming-home">
              {(game.home_team_name || game.home_team?.name || 'HOME').substring(0, 2).toUpperCase()}
            </div>
            <div className="gaming-team-info">
              <div className="gaming-team-name">
                {game.home_team_name || game.home_team?.name || 'Home Team'}
              </div>
              <div className="gaming-team-record">HOME</div>
            </div>
            {game.home_score !== null && (
              <div className="gaming-score gaming-score-leading">
                {game.home_score}
              </div>
            )}
            {markets.length > 0 && markets[0].odds_lines?.length > 0 && (
              <div className="gaming-bet-option ml-auto">
                <div className="gaming-bet-odds">
                  {formatOdds(markets[0].odds_lines[0].home_odds)}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gaming Venue */}
        {game.venue_name && (
          <div className="flex items-center gap-2 gaming-text-accent text-sm pt-3 border-t border-gaming-border">
            <MapPin className="h-3 w-3" />
            <span>{game.venue_name}</span>
            {game.venue_city && (
              <>
                <span className="gaming-text-muted">•</span>
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
            className="gaming-odds"
          >
            <div className="flex items-center gap-2 mb-4">
              <h4 className="text-sm font-bold gaming-text-primary">BETTING MARKETS</h4>
              <div className="w-16 h-0.5 bg-gaming-gradient-neon rounded"></div>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="gaming-loading mx-auto mb-2"></div>
                <div className="gaming-bet-label">Loading odds...</div>
              </div>
            ) : markets.length > 0 ? (
              <div className="space-y-4">
                {markets.map((market) => (
                  <div key={market.id} className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="gaming-bet-label font-bold">{market.market_type}</span>
                      <div className="w-8 h-0.5 bg-gaming-neon-cyan rounded"></div>
                    </div>
                    
                    <div className="gaming-odds-grid">
                      {market.odds_lines?.map((line) => (
                        <div key={line.id} className="gaming-bet-option">
                          <div className="gaming-bet-label mb-2">{line.sportsbook}</div>
                          <div className="space-y-1">
                            {line.home_odds && (
                              <div className="gaming-bet-odds text-sm">
                                H: {formatOdds(line.home_odds)}
                              </div>
                            )}
                            {line.away_odds && (
                              <div className="gaming-bet-odds text-sm">
                                A: {formatOdds(line.away_odds)}
                              </div>
                            )}
                            {line.total_line && (
                              <div className="gaming-bet-odds text-xs gaming-text-accent">
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
              <div className="gaming-card text-center py-8">
                <TrendingDown className="w-12 h-12 mx-auto mb-4 gaming-text-muted" />
                <div className="gaming-team-name mb-2">NO ODDS AVAILABLE</div>
                <p className="gaming-bet-label">Check back later for updates</p>
              </div>
            )}
            
            {/* Gaming Action Button */}
            {onSelectGame && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="gaming-bet-option gaming-bet-hot w-full mt-6 gaming-hover-glow"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectGame(game);
                }}
              >
                <div className="gaming-bet-glow"></div>
                <div className="flex items-center justify-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  <span className="gaming-bet-label font-bold">VIEW BETTING OPTIONS</span>
                </div>
              </motion.button>
            )}
          </motion.div>
        )}

        {/* Expansion Indicator */}
        <div className="flex items-center justify-center pt-2">
          <motion.div
            animate={{ rotate: expanded ? 180 : 0 }}
            className="w-6 h-6 gaming-text-accent"
          >
            <TrendingDown className="w-full h-full" />
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}