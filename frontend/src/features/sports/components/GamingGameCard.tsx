import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';
import { 
  ExclamationTriangleIcon, 
  ClockIcon, 
  CheckCircleIcon,
  FireIcon,
  BoltIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';
import type { GameData, GameLine, ToolbarParams } from '../types';
import { 
  kelly, 
  formatAmericanOdds, 
  formatPercentage, 
  formatCurrency, 
  formatGameTime,
  getImpliedProbability,
  isValidOdds,
  type KellyPayload 
} from '../api/sports';

interface GamingGameCardProps {
  game: GameData;
  params: ToolbarParams;
  className?: string;
}

export function GamingGameCard({ game, params, className }: GamingGameCardProps) {
  const [moneylines, setMoneylines] = useState<GameLine[]>(game.moneylines);

  // Calculate Kelly stakes for all moneylines when parameters change
  const calculateKellyStakes = useCallback(async () => {
    // Only calculate if we have valid parameters
    if (!params.bankroll || !params.winPercentage || params.winPercentage <= 0 || params.winPercentage > 100) {
      return;
    }

    const currentLines = moneylines;
    const updatedLines = await Promise.all(
      currentLines.map(async (line) => {
        if (!isValidOdds(line.odds_american)) {
          return { ...line, loading: false, error: 'Invalid odds' };
        }

        try {
          // Set loading state
          const loadingLine = { ...line, loading: true, error: null };
          setMoneylines(prev => prev.map(l => l.id === line.id ? loadingLine : l));

          // Calculate Kelly criterion
          const kellyPayload: KellyPayload = {
            odds_format: 'american',
            odds_value: line.odds_american,
            win_probability: params.winPercentage / 100, // Convert percentage to decimal
            bankroll: params.bankroll,
            fractional_kelly: params.fractionalKelly,
          };

          const kellyResult = await kelly(kellyPayload);

          return {
            ...line,
            kelly_percentage: kellyResult.kelly_percentage,
            recommended_stake: kellyResult.recommended_stake,
            edge: kellyResult.edge,
            loading: false,
            error: null,
          };
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Kelly calculation failed';
          return {
            ...line,
            kelly_percentage: undefined,
            recommended_stake: undefined,
            edge: undefined,
            loading: false,
            error: errorMessage,
          };
        }
      })
    );

    setMoneylines(updatedLines);
  }, [params]);

  // Update local moneylines when game data changes
  useEffect(() => {
    setMoneylines(game.moneylines);
  }, [game.moneylines]);

  // Trigger Kelly calculations when parameters change
  useEffect(() => {
    const timeoutId = setTimeout(calculateKellyStakes, 100);
    return () => clearTimeout(timeoutId);
  }, [params.bankroll, params.winPercentage, params.fractionalKelly, calculateKellyStakes]);

  const renderGamingMoneylineTile = (line: GameLine) => {
    const isPositiveEV = (line.edge || 0) > 0;
    const hasWarning = (line.kelly_percentage || 0) > 0.1; // High Kelly warning
    const shouldBet = (line.recommended_stake || 0) > 0;
    const isHot = isPositiveEV && shouldBet;

    return (
      <motion.div
        key={line.id}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`bg-card ${isHot ? 'bg-card' : ''} bg-card`}
      >
        {/* Glow effect for hot bets */}
        {isHot && <div className="bg-card"></div>}
        
        {/* Team Name with Gaming Styling */}
        <div className="flex items-center justify-between mb-3">
          <h4 className="bg-card text-sm">
            {line.team}
          </h4>
          {line.side === 'home' && (
            <div className="bg-card">
              <TrophyIcon className="w-3 h-3 mr-1" />
              HOME
            </div>
          )}
        </div>

        {/* Odds Display with Cyberpunk Aesthetic */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between">
            <span className="bg-card">American Odds</span>
            <span className="bg-card">
              {formatAmericanOdds(line.odds_american)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="bg-card">Implied Prob</span>
            <span className="text-sm bg-card">
              {formatPercentage(line.implied_probability)}
            </span>
          </div>
        </div>

        {/* Gaming Loading Animation */}
        {line.loading && (
          <div className="flex items-center justify-center py-4">
            <div className="bg-card"></div>
            <span className="bg-card ml-2">Calculating...</span>
          </div>
        )}

        {/* Gaming Error Display */}
        {line.error && !line.loading && (
          <div className="flex items-center py-2">
            <ExclamationTriangleIcon className="w-4 h-4 bg-card mr-2" />
            <span className="text-xs bg-card">{line.error}</span>
          </div>
        )}

        {/* Kelly Results with Gaming Style */}
        {!line.loading && !line.error && line.kelly_percentage !== undefined && (
          <div className="space-y-3">
            {/* Edge/EV with Neon Styling */}
            <div className="flex items-center justify-between">
              <span className="bg-card">Edge (EV)</span>
              <div className={`bg-card ${isPositiveEV ? 'bg-card' : ''}`}>
                {isPositiveEV && <FireIcon className="w-3 h-3 mr-1" />}
                {line.edge !== undefined ? `${(line.edge * 100).toFixed(2)}%` : 'N/A'}
              </div>
            </div>

            {/* Kelly Percentage */}
            <div className="flex items-center justify-between">
              <span className="bg-card">Kelly %</span>
              <span className="text-sm bg-card">
                {formatPercentage(line.kelly_percentage)}
              </span>
            </div>

            {/* Recommended Stake with Gaming Glow */}
            <div className="flex items-center justify-between">
              <span className="bg-card">Stake</span>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-bold font-mono ${
                  shouldBet ? 'bg-card' : 'bg-card'
                }`}>
                  {formatCurrency(line.recommended_stake || 0)}
                </span>
                {hasWarning && shouldBet && (
                  <div className="bg-card">
                    <BoltIcon className="w-3 h-3 mr-1" />
                    HIGH
                  </div>
                )}
              </div>
            </div>

            {/* Action Recommendation with Gaming Aesthetics */}
            <div className="pt-3 border-t border-bg-card">
              {shouldBet ? (
                <div className="flex items-center bg-card text-xs font-bold">
                  <CheckCircleIcon className="w-4 h-4 mr-2" />
                  <span className="text-bg-card">RECOMMENDED BET</span>
                </div>
              ) : (
                <div className="flex items-center bg-card text-xs">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-2" />
                  <span>NO BET</span>
                </div>
              )}
            </div>
          </div>
        )}
      </motion.div>
    );
  };

  const getGamingStatusBadge = () => {
    switch (game.status) {
      case 'live':
        return (
          <div className="bg-card bg-card">
            <div className="bg-card"></div>
            LIVE
          </div>
        );
      case 'completed':
        return (
          <div className="bg-card">
            <TrophyIcon className="w-3 h-3 mr-1" />
            FINAL
          </div>
        );
      default:
        return (
          <div className="bg-card">
            <ClockIcon className="w-3 h-3 mr-1" />
            SCHEDULED
          </div>
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-card bg-card ${className}`}
    >
      {/* Gaming Border Glow Effect */}
      <div className="bg-card"></div>
      
      <div className="space-y-6">
        {/* Gaming Header */}
        <div className="bg-card">
          <div className="flex items-center gap-4">
            {getGamingStatusBadge()}
            <div className="bg-card">{game.league}</div>
          </div>
          <div className="flex items-center gap-2 text-xs bg-card">
            <ClockIcon className="w-4 h-4" />
            {formatGameTime(game.game_date)}
          </div>
        </div>

        {/* Gaming Team Matchup */}
        <div className="bg-card">
          {/* Away Team */}
          <div className="bg-card bg-card">
            <div className="bg-card">
              {game.away_team.substring(0, 2).toUpperCase()}
            </div>
            <div className="bg-card">
              <div className="bg-card">
                {game.away_team}
              </div>
              <div className="bg-card">AWAY</div>
            </div>
          </div>

          {/* Gaming VS Divider */}
          <div className="bg-card">
            <div className="bg-card">VS</div>
            <div className="bg-card"></div>
          </div>

          {/* Home Team */}
          <div className="bg-card bg-card">
            <div className="bg-card bg-card">
              {game.home_team.substring(0, 2).toUpperCase()}
            </div>
            <div className="bg-card">
              <div className="bg-card">
                {game.home_team}
              </div>
              <div className="bg-card">HOME</div>
            </div>
          </div>
        </div>

        {/* Gaming Venue Info */}
        {game.venue && (
          <div className="flex items-center bg-card text-sm">
            <div className="w-2 h-2 bg-bg-card rounded-full mr-2"></div>
            <span>{game.venue}</span>
          </div>
        )}

        {/* Gaming Moneyline Section */}
        {moneylines.length > 0 && (
          <div className="bg-card">
            <div className="flex items-center gap-2 mb-4">
              <h4 className="text-sm font-bold bg-card">MONEYLINES</h4>
              <div className="w-12 h-0.5 bg-bg-card rounded"></div>
            </div>
            <div className="bg-card">
              {moneylines.map(renderGamingMoneylineTile)}
            </div>
          </div>
        )}

        {/* No Lines Available - Gaming Style */}
        {moneylines.length === 0 && (
          <div className="bg-card text-center py-8">
            <ExclamationTriangleIcon className="w-12 h-12 mx-auto mb-4 bg-card" />
            <div className="bg-card mb-2">NO MONEYLINES</div>
            <p className="bg-card">Check back for updates</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}