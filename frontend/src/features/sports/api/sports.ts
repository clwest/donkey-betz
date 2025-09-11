import { toast } from 'sonner';
import { API_CONFIG } from '../../../config/api.config';

// Get DBAO API URL from environment and strip trailing slash
// Using AI Content Studio backend which has the sports endpoints  
const BASE = (import.meta.env.VITE_DBAO_API_URL || API_CONFIG.BASE_URL).replace(/\/$/, '');
const DBAO_API_URL = BASE;

// Enhanced types for multi-sport support
export interface League {
  id: string;
  name: string;
  abbreviation: string;
  sport_type: SportType;
  country: string;
  active: boolean;
  api_provider?: string;
  current_season?: string;
}

export enum SportType {
  NFL = 'nfl',
  NCAAF = 'ncaaf', 
  NBA = 'nba',
  NCAAB = 'ncaab',
  MLB = 'mlb',
  NHL = 'nhl',
  SOCCER = 'soccer',
  MMA = 'mma',
  TENNIS = 'tennis',
  GOLF = 'golf',
  BOXING = 'boxing',
  ESPORTS = 'esports'
}

export interface Team {
  id: string;
  name: string;
  abbreviation: string;
  city: string;
  league: string;
  conference?: string;
  division?: string;
  logo_url?: string;
  current_record?: Record<string, any>;
}

export interface BettingMarket {
  id: string;
  game_id: string;
  market_type: string;
  market_name: string;
  status: string;
  odds_lines?: OddsLine[];
}

export interface OddsLine {
  id: string;
  market_id: string;
  sportsbook: string;
  home_odds?: number;
  away_odds?: number;
  home_spread?: number;
  away_spread?: number;
  total_line?: number;
  over_odds?: number;
  under_odds?: number;
  decimal_odds?: number;
  is_current: boolean;
  updated_at: string;
}

export interface Game {
  id: string;
  external_id?: string;
  league: string;
  home_team: Team;
  away_team: Team;
  home_team_name: string;
  away_team_name: string;
  scheduled_start: string; // ISO timestamp
  status: GameStatus;
  venue_name?: string;
  venue_city?: string;
  week?: number;
  season?: string;
  home_score?: number;
  away_score?: number;
  weather_data?: Record<string, any>;
  live_stats?: Record<string, any>;
}

export enum GameStatus {
  SCHEDULED = 'scheduled',
  LIVE = 'live', 
  HALFTIME = 'halftime',
  FINAL = 'final',
  POSTPONED = 'postponed',
  CANCELLED = 'cancelled',
  SUSPENDED = 'suspended'
}

export interface Market {
  id: string;
  kind: 'moneyline' | 'spread' | 'total' | 'prop';
  book: string;
  lines: MarketLine[];
  game_info?: {
    id: string;
    home_team: string;
    away_team: string;
    start_time: string;
    league: string;
  };
  updated_at: string;
}

export interface MarketLine {
  id: string;
  side: 'home' | 'away';
  price_american: number; // e.g., +110, -150
  price_decimal: number;
  point: number | null;
  created_at: string;
}

export interface KellyPayload {
  odds_format: 'american';
  odds_value: number;
  win_probability: number;
  bankroll: number;
  fractional_kelly: number;
}

export interface KellyResponse {
  kelly_percentage: number;
  recommended_stake: number;
  edge: number;
  risk_level: string;
  warnings: string[];
}

// Generic API request handler with comprehensive error handling
async function fetchApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${DBAO_API_URL}${path}`;
  
  console.log('🔍 [Sports API] Request:', {
    method: options.method || 'GET',
    path,
    url,
    body: options.body ? JSON.parse(options.body as string) : undefined
  });
  
  // Get auth token from localStorage - no hardcoded fallback
  const token = localStorage.getItem('authToken');
  
  if (!token) {
    console.error('[Sports API] No auth token found - user must be logged in');
    toast.error('Please log in to access sports data');
    throw new Error('Authentication required');
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-DBAO-Client': 'AI-Studio-Web',
        'Authorization': `Token ${token}`,
        ...options.headers,
      },
    });

    // Read response as text first
    const responseText = await response.text();
    
    if (!response.ok) {
      console.error(`[Sports API] ${options.method || 'GET'} ${path} failed:`, responseText);
      toast.error(`API Error: ${responseText || `HTTP ${response.status}`}`);
      throw new Error(responseText || `HTTP ${response.status} ${response.statusText}`);
    }

    // Parse JSON if we have content
    if (responseText.trim()) {
      const data = JSON.parse(responseText);
      
      console.log('✅ [Sports API] Response:', {
        path,
        rawData: data,
        isPaginated: data && typeof data === 'object' && 'results' in data,
        dataLength: Array.isArray(data) ? data.length : (data?.results ? data.results.length : 'not array')
      });
      
      // Handle paginated responses from Django REST Framework
      if (data && typeof data === 'object' && 'results' in data && Array.isArray(data.results)) {
        console.log('📄 [Sports API] Paginated response, returning results array');
        return data.results as T;
      }
      
      return data;
    }
    
    return {} as T;
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const networkError = `Network error: Unable to connect to ${url}`;
      console.error('[Sports API] Network error:', networkError);
      toast.error(networkError);
      throw new Error(networkError);
    }
    
    // Re-throw other errors as they've already been handled
    throw error;
  }
}

/**
 * Fetch available leagues with enhanced multi-sport support
 * Now supports all major sports through ESPN, TheSportsDB, and other providers
 */
export async function listLeagues(sportType?: SportType): Promise<League[]> {
  const params = new URLSearchParams();
  if (sportType) {
    params.append('sport_type', sportType);
  }
  
  console.log('🏆 [listLeagues] Fetching leagues:', { sportType, params: params.toString() });
  const result = await fetchApi<League[]>(`/api/v1/sports/leagues/?${params.toString()}`);
  console.log('🏆 [listLeagues] Got leagues:', result);
  return result;
}

/**
 * Get sports types with active leagues
 */
export async function getSportsTypes(): Promise<{ sport_type: SportType; name: string; count: number }[]> {
  console.log('📊 [getSportsTypes] Fetching sports summary');
  const result = await fetchApi<{ sport_type: SportType; name: string; count: number }[]>('/api/v1/sports/summary/');
  console.log('📊 [getSportsTypes] Got sports types:', result);
  return result;
}

/**
 * Get teams for a specific league
 */
export async function getTeams(leagueId: string): Promise<Team[]> {
  return fetchApi<Team[]>(`/api/v1/sports/teams/?league=${leagueId}`);
}

/**
 * Get live games across all sports
 */
export async function getLiveGames(): Promise<Game[]> {
  console.log('🔴 [getLiveGames] Fetching live games');
  const result = await fetchApi<Game[]>('/api/v1/sports/games/?status=live');
  console.log('🔴 [getLiveGames] Got live games:', result);
  return result;
}

/**
 * Get games by sport type
 */
export async function getGamesBySport(sportType: SportType, date?: string): Promise<Game[]> {
  const params = new URLSearchParams({ sport_type: sportType });
  if (date) {
    params.append('date', date);
  }
  
  console.log('🎮 [getGamesBySport] Fetching games:', { sportType, date, params: params.toString() });
  const result = await fetchApi<Game[]>(`/api/v1/sports/games/?${params.toString()}`);
  console.log('🎮 [getGamesBySport] Got games:', result);
  return result;
}

/**
 * Get betting markets for a game or all markets
 */
export async function getMarkets(params?: { game_id?: string; market_type?: string }): Promise<BettingMarket[]> {
  const queryParams = new URLSearchParams();
  if (params?.game_id) queryParams.append('game', params.game_id);
  if (params?.market_type) queryParams.append('market_type', params.market_type);
  
  const query = queryParams.toString();
  console.log('📊 [getMarkets] Fetching markets:', { params, query });
  const result = await fetchApi<BettingMarket[]>(`/api/v1/sports/markets/${query ? `?${query}` : ''}`);
  console.log('📊 [getMarkets] Got markets:', result);
  return result;
}

/**
 * Get game odds with all betting lines
 */
export async function getGameOdds(gameId: string): Promise<any> {
  console.log('💰 [getGameOdds] Fetching odds for game:', gameId);
  const result = await fetchApi<any>(`/api/v1/sports/games/${gameId}/odds/`);
  console.log('💰 [getGameOdds] Got odds:', result);
  return result;
}

/**
 * Get trending games with high betting volume
 */
export async function getTrendingGames(limit = 10): Promise<Game[]> {
  console.log('🔥 [getTrendingGames] Fetching trending games:', { limit });
  const result = await fetchApi<Game[]>(`/api/v1/sports/games/trending/?limit=${limit}`);
  console.log('🔥 [getTrendingGames] Got trending games:', result);
  return result;
}

/**
 * Fetch available leagues (alias for backward compatibility)  
 */
export async function leagues(): Promise<League[]> {
  return listLeagues();
}

/**
 * Fetch games with optional filters
 * @param params.league - League identifier (e.g., 'NCAAF')
 * @param params.date - Date in YYYY-MM-DD format
 * @param params.team - Team name or abbreviation (optional)
 */
export async function games(params: {
  league: string;
  date?: string;
  team?: string;
}): Promise<Game[]> {
  const searchParams = new URLSearchParams({
    league: params.league,
    ...(params.date && { date: params.date }),
    ...(params.team && { team: params.team }),
  });
  
  const url = `${BASE}/sports/games/?${searchParams.toString()}`;
  console.log('[WEB SPORTS] GET', url);
  
  return fetchApi(`/api/v1/sports/games/?${searchParams.toString()}`);
}

/**
 * Fetch betting markets for a specific game
 * @param params.league - League identifier
 * @param params.game_id - Game ID
 * @param params.kind - Market type filter
 */
export async function markets(params: {
  league: string;
  game_id: string;
  kind: string;
}): Promise<Market[]> {
  const searchParams = new URLSearchParams({
    league: params.league,
    game_id: params.game_id,
    kind: params.kind,
    detailed: 'true', // Request full market data with lines
  });
  
  const url = `${BASE}/sports/markets/?${searchParams.toString()}`;
  console.log('[WEB SPORTS] GET', url);
  
  return fetchApi<Market[]>(`/api/v1/sports/markets/?${searchParams.toString()}`);
}

/**
 * Calculate Kelly criterion stake recommendation
 * @param payload - Kelly calculation parameters
 */
export async function kelly(payload: KellyPayload): Promise<KellyResponse> {
  // Transform frontend payload to match backend expectations
  const backendPayload = {
    odds: String(payload.odds_value),
    odds_format: payload.odds_format,
    true_probability: payload.win_probability,
    bankroll: payload.bankroll,
    kelly_multiplier: payload.fractional_kelly
  };
  
  return fetchApi<KellyResponse>('/api/v1/odds-calc/kelly-criterion/', {
    method: 'POST',
    body: JSON.stringify(backendPayload),
  });
}

// Utility functions for formatting and validation

/**
 * Format American odds for display
 */
export function formatAmericanOdds(odds: number): string {
  return odds > 0 ? `+${odds}` : `${odds}`;
}

/**
 * Convert decimal to percentage string
 */
export function formatPercentage(decimal: number, decimals = 1): string {
  return `${(decimal * 100).toFixed(decimals)}%`;
}

/**
 * Format currency values
 */
export function formatCurrency(value: number, decimals = 2): string {
  return `$${value.toFixed(decimals)}`;
}

/**
 * Validate if odds value is valid
 */
export function isValidOdds(odds: number): boolean {
  return !isNaN(odds) && isFinite(odds) && odds !== 0;
}

/**
 * Get implied probability from American odds
 */
export function getImpliedProbability(americanOdds: number): number {
  if (americanOdds > 0) {
    return 100 / (americanOdds + 100);
  } else {
    return Math.abs(americanOdds) / (Math.abs(americanOdds) + 100);
  }
}

/**
 * Parse date to user's local timezone
 */
export function formatGameTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
  });
}

/**
 * Get sport display name from SportType enum
 */
export function getSportDisplayName(sportType: SportType): string {
  const sportNames: Record<SportType, string> = {
    [SportType.NFL]: 'NFL',
    [SportType.NCAAF]: 'College Football',
    [SportType.NBA]: 'NBA',
    [SportType.NCAAB]: 'College Basketball',
    [SportType.MLB]: 'MLB',
    [SportType.NHL]: 'NHL',
    [SportType.SOCCER]: 'Soccer',
    [SportType.MMA]: 'MMA',
    [SportType.TENNIS]: 'Tennis',
    [SportType.GOLF]: 'Golf',
    [SportType.BOXING]: 'Boxing',
    [SportType.ESPORTS]: 'Esports'
  };
  
  return sportNames[sportType] || sportType;
}

/**
 * Get sport emoji for display
 */
export function getSportEmoji(sportType: SportType): string {
  const sportEmojis: Record<SportType, string> = {
    [SportType.NFL]: '🏈',
    [SportType.NCAAF]: '🏈',
    [SportType.NBA]: '🏀',
    [SportType.NCAAB]: '🏀',
    [SportType.MLB]: '⚾',
    [SportType.NHL]: '🏒',
    [SportType.SOCCER]: '⚽',
    [SportType.MMA]: '🥊',
    [SportType.TENNIS]: '🎾',
    [SportType.GOLF]: '⛳',
    [SportType.BOXING]: '🥊',
    [SportType.ESPORTS]: '🎮'
  };
  
  return sportEmojis[sportType] || '🏆';
}

/**
 * Check if a game is live
 */
export function isGameLive(game: Game): boolean {
  return [GameStatus.LIVE, GameStatus.HALFTIME].includes(game.status);
}

/**
 * Check if a game is finished
 */
export function isGameFinished(game: Game): boolean {
  return game.status === GameStatus.FINAL;
}

/**
 * Get game status display text
 */
export function getGameStatusDisplay(status: GameStatus): string {
  const statusMap: Record<GameStatus, string> = {
    [GameStatus.SCHEDULED]: 'Scheduled',
    [GameStatus.LIVE]: 'Live',
    [GameStatus.HALFTIME]: 'Halftime',
    [GameStatus.FINAL]: 'Final',
    [GameStatus.POSTPONED]: 'Postponed',
    [GameStatus.CANCELLED]: 'Cancelled',
    [GameStatus.SUSPENDED]: 'Suspended'
  };
  
  return statusMap[status] || status;
}

/**
 * Get color class for game status
 */
export function getGameStatusColor(status: GameStatus): string {
  const colorMap: Record<GameStatus, string> = {
    [GameStatus.SCHEDULED]: 'text-gray-600',
    [GameStatus.LIVE]: 'text-red-600 animate-pulse',
    [GameStatus.HALFTIME]: 'text-orange-600',
    [GameStatus.FINAL]: 'text-green-600',
    [GameStatus.POSTPONED]: 'text-yellow-600',
    [GameStatus.CANCELLED]: 'text-red-400',
    [GameStatus.SUSPENDED]: 'text-orange-400'
  };
  
  return colorMap[status] || 'text-gray-500';
}

/**
 * Format team record for display
 */
export function formatTeamRecord(record: Record<string, any>): string {
  if (!record) return '';
  
  const { wins = 0, losses = 0, ties = 0 } = record;
  
  if (ties > 0) {
    return `${wins}-${losses}-${ties}`;
  }
  
  return `${wins}-${losses}`;
}

/**
 * Get today's date in YYYY-MM-DD format
 */
export function getTodayDateString(): string {
  return new Date().toISOString().split('T')[0];
}

/**
 * Get date N days from today
 */
export function getDateString(daysFromToday: number): string {
  const date = new Date();
  date.setDate(date.getDate() + daysFromToday);
  return date.toISOString().split('T')[0];
}

/**
 * Sync sports data from all providers
 */
export async function syncSportsData(options: {
  leagues?: boolean;
  teams?: boolean;
  games?: boolean;
  odds?: boolean;
  sport?: SportType;
}): Promise<{ success: boolean; message: string }> {
  const params = new URLSearchParams();
  
  if (options.leagues) params.append('leagues', 'true');
  if (options.teams) params.append('teams', 'true');
  if (options.games) params.append('games', 'true');
  if (options.odds) params.append('odds', 'true');
  if (options.sport) params.append('sport', options.sport);
  
  console.log('🔄 [syncSportsData] Syncing sports data:', options);
  const result = await fetchApi<{ success: boolean; message: string }>('/api/v1/sports/sync/', {
    method: 'POST',
    body: JSON.stringify(options),
  });
  console.log('🔄 [syncSportsData] Sync result:', result);
  return result;
}