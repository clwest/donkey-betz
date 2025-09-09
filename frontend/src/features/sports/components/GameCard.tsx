import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card } from '../../../components/common/Card';
import { Badge } from '../../../components/common/Badge';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';
import { ExclamationTriangleIcon, ClockIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
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

interface GameCardProps {
  game: GameData;
  params: ToolbarParams;
  className?: string;
}

export function GameCard({ game, params, className }: GameCardProps) {
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

  const renderMoneylineTile = (line: GameLine) => {
    const isPositiveEV = (line.edge || 0) > 0;
    const hasWarning = (line.kelly_percentage || 0) > 0.1; // High Kelly warning
    const shouldBet = (line.recommended_stake || 0) > 0;

    return (
      <motion.div
        key={line.id}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`glass rounded-lg p-4 border transition-all duration-200 ${
          isPositiveEV 
            ? 'border-green-500/30 bg-green-500/5 hover:border-green-500/50' 
            : 'border-gray-600/30 bg-gray-800/20 hover:border-gray-500/50'
        }`}
      >
        {/* Team Name */}
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-white text-sm">
            {line.team}
          </h4>
          {line.side === 'home' && (
            <Badge variant="outline" size="sm" className="text-xs">
              HOME
            </Badge>
          )}
        </div>

        {/* Odds and Probability Row */}
        <div className="space-y-2 mb-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">American Odds</span>
            <span className="font-semibold text-white">
              {formatAmericanOdds(line.odds_american)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Implied Prob</span>
            <span className="text-sm text-gray-300">
              {formatPercentage(line.implied_probability)}
            </span>
          </div>
        </div>

        {/* Kelly Calculation Results */}
        {line.loading && (
          <div className="flex items-center justify-center py-4">
            <LoadingSpinner size="sm" />
            <span className="text-xs text-gray-400 ml-2">Calculating...</span>
          </div>
        )}

        {line.error && !line.loading && (
          <div className="flex items-center py-2">
            <ExclamationTriangleIcon className="w-4 h-4 text-red-400 mr-2" />
            <span className="text-xs text-red-400">{line.error}</span>
          </div>
        )}

        {!line.loading && !line.error && line.kelly_percentage !== undefined && (
          <div className="space-y-2">
            {/* Edge/EV */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Edge (EV)</span>
              <Badge 
                variant={isPositiveEV ? 'success' : 'error'} 
                size="sm"
                className="text-xs"
              >
                {line.edge !== undefined ? `${(line.edge * 100).toFixed(2)}%` : 'N/A'}
              </Badge>
            </div>

            {/* Kelly Percentage */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Kelly %</span>
              <span className="text-sm text-gray-300">
                {formatPercentage(line.kelly_percentage)}
              </span>
            </div>

            {/* Recommended Stake */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Stake</span>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-medium ${
                  shouldBet ? 'text-green-400' : 'text-gray-500'
                }`}>
                  {formatCurrency(line.recommended_stake || 0)}
                </span>
                {hasWarning && shouldBet && (
                  <Badge variant="warning" size="sm">
                    High
                  </Badge>
                )}
              </div>
            </div>

            {/* Action Recommendation */}
            <div className="pt-2 border-t border-dark-600">
              {shouldBet ? (
                <div className="flex items-center text-green-400 text-xs">
                  <CheckCircleIcon className="w-4 h-4 mr-1" />
                  <span className="font-medium">RECOMMENDED</span>
                </div>
              ) : (
                <div className="flex items-center text-gray-500 text-xs">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
                  <span>NO BET</span>
                </div>
              )}
            </div>
          </div>
        )}
      </motion.div>
    );
  };

  const getStatusBadge = () => {
    switch (game.status) {
      case 'live':
        return <Badge variant="success" className="animate-pulse">LIVE</Badge>;
      case 'completed':
        return <Badge variant="secondary">FINAL</Badge>;
      default:
        return <Badge variant="info">SCHEDULED</Badge>;
    }
  };

  return (
    <Card className={`hover:border-primary-500/30 transition-all duration-200 ${className}`}>
      <div className="space-y-4">
        {/* Game Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">
              {game.away_team} @ {game.home_team}
            </h3>
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <div className="flex items-center">
                <ClockIcon className="w-4 h-4 mr-1" />
                {formatGameTime(game.game_date)}
              </div>
              {game.venue && (
                <span>{game.venue}</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <Badge variant="outline" size="sm">
              {game.league}
            </Badge>
          </div>
        </div>

        {/* Moneyline Tiles */}
        {moneylines.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-3">Moneylines</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {moneylines.map(renderMoneylineTile)}
            </div>
          </div>
        )}

        {/* No Lines Available */}
        {moneylines.length === 0 && (
          <div className="text-center py-4 text-gray-500">
            <ExclamationTriangleIcon className="w-6 h-6 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No moneyline yet.</p>
          </div>
        )}
      </div>
    </Card>
  );
}