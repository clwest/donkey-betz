import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '../../../components/common/Button';
import { Card } from '../../../components/common/Card';
import { CalendarIcon, MagnifyingGlassIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { toast } from 'sonner';
import type { ToolbarParams } from '../types';
import { 
  FRACTIONAL_KELLY_OPTIONS, 
  DEFAULT_TOOLBAR_PARAMS, 
  STORAGE_KEYS 
} from '../types';
import { listLeagues, type League } from '../api/sports';

// Debounce hook to prevent excessive parameter changes
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

interface SportsToolbarProps {
  params: ToolbarParams;
  onParamsChange: (params: ToolbarParams) => void;
  onRefresh: () => void;
  loading?: boolean;
  gameCount?: number;
}

export function SportsToolbar({
  params,
  onParamsChange,
  onRefresh,
  loading = false,
  gameCount = 0,
}: SportsToolbarProps) {
  // Local state for immediate UI feedback
  const [bankrollStr, setBankrollStr] = useState(String(params.bankroll));
  const [winPercentageStr, setWinPercentageStr] = useState(String(params.winPercentage));
  const [fractionalKelly, setFractionalKelly] = useState(params.fractionalKelly);
  const [selectedLeague, setSelectedLeague] = useState(params.selectedLeague);
  const [selectedDate, setSelectedDate] = useState(params.selectedDate);
  const [selectedTeam, setSelectedTeam] = useState(params.selectedTeam || '');
  
  // State for dynamic league options
  const [leagueOptions, setLeagueOptions] = useState<League[]>([]);
  const [leaguesLoading, setLeaguesLoading] = useState(true);

  // Debounced values - these will trigger API calls after 200ms of no changes
  const debouncedBankroll = useDebounce(bankrollStr, 200);
  const debouncedWinPercentage = useDebounce(winPercentageStr, 200);
  const debouncedFractionalKelly = useDebounce(fractionalKelly, 200);
  const debouncedLeague = useDebounce(selectedLeague, 200);
  const debouncedDate = useDebounce(selectedDate, 200);
  const debouncedTeam = useDebounce(selectedTeam, 200);

  // Track initialization to prevent triggering onChange on mount
  const isInitialized = useRef(false);

  // Fetch leagues from API on mount
  useEffect(() => {
    const fetchLeagues = async () => {
      try {
        setLeaguesLoading(true);
        const leagues = await listLeagues();
        // Filter active leagues and sort by name
        const activeLeagues = leagues
          .filter(league => league.active)
          .sort((a, b) => a.name.localeCompare(b.name));
        
        setLeagueOptions(activeLeagues);
        
        // If NCAAF is available, use it as default, otherwise use first league
        const hasNCAAF = activeLeagues.some(league => league.id === 'NCAAF');
        const defaultLeague = hasNCAAF ? 'NCAAF' : (activeLeagues[0]?.id || '');
        
        // Only update if we don't have a selected league
        if (!selectedLeague && defaultLeague) {
          setSelectedLeague(defaultLeague);
        }
      } catch (error) {
        console.error('Failed to fetch leagues:', error);
        toast.error('Failed to load leagues. Using fallback list.');
        // Fallback to empty list - dropdown will be disabled
        setLeagueOptions([]);
      } finally {
        setLeaguesLoading(false);
      }
    };
    
    fetchLeagues();
  }, []);

  // Load params from localStorage on mount only
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.SPORTS_TOOLBAR_PARAMS);
    if (stored) {
      try {
        const parsedParams = JSON.parse(stored);
        setBankrollStr(String(parsedParams.bankroll));
        setWinPercentageStr(String(parsedParams.winPercentage));
        setFractionalKelly(parsedParams.fractionalKelly);
        setSelectedLeague(parsedParams.selectedLeague);
        setSelectedDate(parsedParams.selectedDate);
        setSelectedTeam(parsedParams.selectedTeam || '');
        onParamsChange(parsedParams);
      } catch (error) {
        console.error('Failed to parse stored toolbar params:', error);
      }
    }
    
    isInitialized.current = true;
  }, []); // Empty dependencies - only run on mount

  // Update parent when debounced values change (after initialization)
  useEffect(() => {
    if (!isInitialized.current) return;

    const bankroll = parseFloat(debouncedBankroll) || DEFAULT_TOOLBAR_PARAMS.bankroll;
    const winPercentage = parseFloat(debouncedWinPercentage) || DEFAULT_TOOLBAR_PARAMS.winPercentage;
    
    const newParams: ToolbarParams = {
      bankroll,
      winPercentage,
      fractionalKelly: debouncedFractionalKelly,
      selectedLeague: debouncedLeague,
      selectedDate: debouncedDate,
      selectedTeam: debouncedTeam || undefined,
    };
    
    // Save to localStorage
    localStorage.setItem(STORAGE_KEYS.SPORTS_TOOLBAR_PARAMS, JSON.stringify(newParams));
    
    // Notify parent only if values actually changed
    const hasChanged = JSON.stringify(newParams) !== JSON.stringify(params);
    if (hasChanged) {
      onParamsChange(newParams);
    }
  }, [
    debouncedBankroll, 
    debouncedWinPercentage, 
    debouncedFractionalKelly, 
    debouncedLeague, 
    debouncedDate, 
    debouncedTeam,
    onParamsChange,
    params
  ]);

  const handleBankrollChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setBankrollStr(e.target.value);
  }, []);

  const handleWinPercentageChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setWinPercentageStr(e.target.value);
  }, []);

  const handleFractionalKellyChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = parseFloat(e.target.value);
    setFractionalKelly(value);
  }, []);

  const handleLeagueChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedLeague(e.target.value);
  }, []);

  const handleDateChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(e.target.value);
  }, []);

  const handleTeamChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedTeam(e.target.value);
  }, []);

  const resetToDefaults = useCallback(() => {
    setBankrollStr(String(DEFAULT_TOOLBAR_PARAMS.bankroll));
    setWinPercentageStr(String(DEFAULT_TOOLBAR_PARAMS.winPercentage));
    setFractionalKelly(DEFAULT_TOOLBAR_PARAMS.fractionalKelly);
    setSelectedLeague(DEFAULT_TOOLBAR_PARAMS.selectedLeague);
    setSelectedDate(DEFAULT_TOOLBAR_PARAMS.selectedDate);
    setSelectedTeam('');
  }, []);

  return (
    <Card className="mb-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Sports Betting Board</h2>
            <p className="text-sm text-gray-400 mt-1">
              {gameCount} games • Bankroll: ${(parseFloat(bankrollStr) || 0).toLocaleString()} • Win Rate: {winPercentageStr}%
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={resetToDefaults}
              className="text-sm"
            >
              Reset
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={onRefresh}
              loading={loading}
              className="flex items-center gap-2"
            >
              <ArrowPathIcon className="w-4 h-4" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* League */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              League
            </label>
            <select
              value={selectedLeague}
              onChange={handleLeagueChange}
              disabled={leaguesLoading || leagueOptions.length === 0}
              className="w-full px-3 py-2 bg-dark-700/50 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {leaguesLoading ? (
                <option value="" className="bg-dark-700">Loading leagues...</option>
              ) : leagueOptions.length === 0 ? (
                <option value="" className="bg-dark-700">No leagues available</option>
              ) : (
                leagueOptions.map((league) => (
                  <option key={league.id} value={league.id} className="bg-dark-700">
                    {league.name}
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Date */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              Date
            </label>
            <div className="relative">
              <input
                type="date"
                value={selectedDate}
                onChange={handleDateChange}
                className="w-full px-3 py-2 bg-dark-700/50 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              />
              <CalendarIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* Team Search */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              Team (Optional)
            </label>
            <div className="relative">
              <input
                type="text"
                value={selectedTeam}
                onChange={handleTeamChange}
                placeholder="Search teams..."
                className="w-full px-3 py-2 pl-9 bg-dark-700/50 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              />
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
          </div>

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
              placeholder="4000"
            />
          </div>

          {/* Win Probability */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">
              Win Rate (%)
            </label>
            <input
              type="number"
              value={winPercentageStr}
              onChange={handleWinPercentageChange}
              min="0"
              max="100"
              step="1"
              className="w-full px-3 py-2 bg-dark-700/50 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              placeholder="55"
            />
          </div>
        </div>

        {/* Kelly Fraction */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
      </div>
    </Card>
  );
}