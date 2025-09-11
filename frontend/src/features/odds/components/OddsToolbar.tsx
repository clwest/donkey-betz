import { useState, useEffect, useCallback } from 'react';
import { Button } from '../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { PlusIcon, TrashIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import type { ToolbarParams } from '../types';
import { FRACTIONAL_KELLY_OPTIONS, DEFAULT_TOOLBAR_PARAMS, STORAGE_KEYS } from '../types';

// Debounce hook to prevent excessive updates
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

interface OddsToolbarProps {
  params: ToolbarParams;
  onParamsChange: (params: ToolbarParams) => void;
  onAddRow: () => void;
  onClearRows: () => void;
  onRefreshRealData: () => void;
  rowCount: number;
  isLoadingRealData?: boolean;
}

export function OddsToolbar({
  params,
  onParamsChange,
  onAddRow,
  onClearRows,
  onRefreshRealData,
  rowCount,
  isLoadingRealData = false,
}: OddsToolbarProps) {
  // Local state for string inputs to prevent cursor jumping
  const [bankrollStr, setBankrollStr] = useState(String(params.bankroll));
  const [winProbStr, setWinProbStr] = useState(String(Math.round(params.winProbability * 100)));
  const [fractionalKelly, setFractionalKelly] = useState(params.fractionalKelly);

  // Debounced values for API calls
  const debouncedBankroll = useDebounce(bankrollStr, 500);
  const debouncedWinProb = useDebounce(winProbStr, 500);

  // Load params from localStorage on mount only
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.TOOLBAR_PARAMS);
    if (stored) {
      try {
        const parsedParams = JSON.parse(stored);
        setBankrollStr(String(parsedParams.bankroll));
        setWinProbStr(String(Math.round(parsedParams.winProbability * 100)));
        setFractionalKelly(parsedParams.fractionalKelly);
        // Don't call onParamsChange here - it will be triggered by the other useEffect
      } catch (error) {
        console.error('Failed to parse stored toolbar params:', error);
      }
    }
  }, []); // Empty dependencies - only run on mount

  // Update parent when debounced values change
  useEffect(() => {
    const bankroll = parseFloat(debouncedBankroll) || 0;
    const winProbability = (parseFloat(debouncedWinProb) || 0) / 100; // Convert to decimal
    
    const newParams: ToolbarParams = {
      bankroll,
      winProbability,
      fractionalKelly
    };
    
    // Save to localStorage
    localStorage.setItem(STORAGE_KEYS.TOOLBAR_PARAMS, JSON.stringify(newParams));
    
    // Notify parent
    onParamsChange(newParams);
  }, [debouncedBankroll, debouncedWinProb, fractionalKelly]); // Removed onParamsChange from deps

  const handleBankrollChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setBankrollStr(e.target.value);
  }, []);

  const handleWinProbabilityChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setWinProbStr(e.target.value);
  }, []);

  const handleFractionalKellyChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = parseFloat(e.target.value);
    setFractionalKelly(value);
  }, []);

  const resetToDefaults = useCallback(() => {
    setBankrollStr(String(DEFAULT_TOOLBAR_PARAMS.bankroll));
    setWinProbStr(String(Math.round(DEFAULT_TOOLBAR_PARAMS.winProbability * 100)));
    setFractionalKelly(DEFAULT_TOOLBAR_PARAMS.fractionalKelly);
  }, []);

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Betting Parameters</CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={resetToDefaults}
            className="text-sm"
          >
            Reset Defaults
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">

        {/* Parameter Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Bankroll */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              Bankroll ($)
            </label>
            <input
              type="number"
              value={bankrollStr}
              onChange={handleBankrollChange}
              min="0"
              step="100"
              className="w-full px-3 py-2 bg-dark-700/50 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              placeholder="Enter bankroll amount"
            />
          </div>

          {/* Win Probability */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              Win Probability (%)
            </label>
            <input
              type="number"
              value={winProbStr}
              onChange={handleWinProbabilityChange}
              min="0"
              max="100"
              step="1"
              className="w-full px-3 py-2 bg-dark-700/50 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              placeholder="Enter win probability"
            />
          </div>

          {/* Fractional Kelly */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              Kelly Fraction
            </label>
            <select
              value={fractionalKelly}
              onChange={handleFractionalKellyChange}
              className="w-full px-3 py-2 bg-dark-700/50 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            >
              {FRACTIONAL_KELLY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value} className="bg-dark-700">
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-dark-700">
          <div className="flex items-center gap-3">
            <Button
              size="sm"
              onClick={onAddRow}
              className="flex items-center gap-2"
            >
              <PlusIcon className="w-4 h-4" />
              Add Row
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onRefreshRealData}
              disabled={isLoadingRealData}
              className="flex items-center gap-2 text-blue-400 border-blue-500/50 hover:bg-blue-500/10"
            >
              <ArrowPathIcon className={`w-4 h-4 ${isLoadingRealData ? 'animate-spin' : ''}`} />
              {isLoadingRealData ? 'Loading...' : 'Refresh Real Data'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onClearRows}
              disabled={rowCount === 0}
              className="flex items-center gap-2 text-red-400 border-red-500/50 hover:bg-red-500/10"
            >
              <TrashIcon className="w-4 h-4" />
              Clear Rows
            </Button>
          </div>

          {/* Summary Info */}
          <div className="text-sm text-gray-400">
            {rowCount} row{rowCount !== 1 ? 's' : ''} • Bankroll: ${(parseFloat(bankrollStr) || 0).toLocaleString()} • Win Rate: {winProbStr}%
          </div>
        </div>
      </CardContent>
    </Card>
  );
}