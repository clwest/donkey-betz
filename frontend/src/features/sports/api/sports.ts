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

export interface TeamRecord {
  wins?: number;
  losses?: number;
  ties?: number;
  win_percentage?: number;
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
  current_record?: TeamRecord;
  ats_record?: TeamRecord;
  ou_record?: TeamRecord;
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
  league_name?: string;
  home_team: Team;
  away_team: Team;
  home_team_name: string;
  away_team_name: string;
  home_team_abbreviation?: string;
  away_team_abbreviation?: string;
  scheduled_start: string; // ISO timestamp
  status: GameStatus;
  venue_name?: string;
  venue_city?: string;
  week?: number;
  season?: string;
  home_score?: number;
  away_score?: number;
  current_period?: string;
  time_remaining?: string;
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

  // Get auth token from localStorage - allow public access for sports data
  const token = localStorage.getItem('authToken');

  // Get CSRF token from cookies
  const getCsrfToken = () => {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    return null;
  };

  // For public sports endpoints, allow access without authentication
  const publicEndpoints = ['/sports/', '/games/', '/leagues/', '/teams/', '/summary/'];
  const isPublicEndpoint = publicEndpoints.some(endpoint => path.includes(endpoint));

  if (!token && !isPublicEndpoint) {
    console.error('[Sports API] No auth token found - user must be logged in');
    toast.error('Please log in to access this feature');
    throw new Error('Authentication required');
  }

  try {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'X-DBAO-Client': 'AI-Studio-Web',
      ...options.headers,
    };

    // Add CSRF token for POST/PUT/DELETE requests
    const csrfToken = getCsrfToken();
    if (csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method || '')) {
      headers['X-CSRFToken'] = csrfToken;
    }

    // Only add Authorization header if we have a token
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // Include cookies for CSRF
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
  const result = await fetchApi<League[]>(`/v1/sports/leagues/?${params.toString()}`);
  console.log('🏆 [listLeagues] Got leagues:', result);
  return result;
}

/**
 * Get sports types with active leagues
 */
export async function getSportsTypes(): Promise<{ sport_type: SportType; name: string; count: number }[]> {
  console.log('📊 [getSportsTypes] Fetching sports summary');
  const result = await fetchApi<{ sport_type: SportType; name: string; count: number }[]>('/v1/sports/summary/');
  console.log('📊 [getSportsTypes] Got sports types:', result);
  return result;
}

/**
 * Get teams for a specific league
 */
export async function getTeams(leagueId: string): Promise<Team[]> {
  return fetchApi<Team[]>(`/v1/sports/teams/?league=${leagueId}`);
}

/**
 * Get live games across all sports
 */
export async function getLiveGames(): Promise<Game[]> {
  console.log('🔴 [getLiveGames] Fetching live games');
  const result = await fetchApi<Game[]>('/v1/sports/games/?status=live');
  console.log('🔴 [getLiveGames] Got live games:', result);
  return result;
}

/**
 * Get games by sport type
 */
export async function getGamesBySport(sportType: SportType, date?: string, dateRange?: { from: string; to: string }): Promise<Game[]> {
  const params = new URLSearchParams({ sport_type: sportType });

  if (dateRange) {
    params.append('date_from', dateRange.from);
    params.append('date_to', dateRange.to);
  } else if (date) {
    params.append('date', date);
  }

  // Add page_size to get more results
  params.append('page_size', '100');

  console.log('🎮 [getGamesBySport] Fetching games:', { sportType, date, dateRange, params: params.toString() });
  const result = await fetchApi<Game[]>(`/v1/sports/games/?${params.toString()}`);
  console.log('🎮 [getGamesBySport] Got games:', result);

  // Log detailed info about first game to check data
  if (result && result.length > 0) {
    const firstGame = result[0];
    console.log('🏈 [getGamesBySport] First game details:', {
      id: firstGame.id,
      teams: `${firstGame.away_team?.name} @ ${firstGame.home_team?.name}`,
      home_team: {
        name: firstGame.home_team?.name,
        logo_url: firstGame.home_team?.logo_url,
        current_record: firstGame.home_team?.current_record
      },
      away_team: {
        name: firstGame.away_team?.name,
        logo_url: firstGame.away_team?.logo_url,
        current_record: firstGame.away_team?.current_record
      },
      has_logos: !!(firstGame.home_team?.logo_url || firstGame.away_team?.logo_url),
      has_records: !!(firstGame.home_team?.current_record || firstGame.away_team?.current_record)
    });
  }

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
  const result = await fetchApi<BettingMarket[]>(`/v1/sports/markets/${query ? `?${query}` : ''}`);
  console.log('📊 [getMarkets] Got markets:', result);
  return result;
}

/**
 * Get game odds with all betting lines
 */
export async function getGameOdds(gameId: string): Promise<any> {
  console.log('💰 [getGameOdds] Fetching odds for game:', gameId);
  const result = await fetchApi<any>(`/v1/sports/games/${gameId}/odds/`);
  console.log('💰 [getGameOdds] Got odds:', result);
  return result;
}

/**
 * Get individual game by ID with full details
 */
export async function getGameById(gameId: string): Promise<Game> {
  console.log('🎮 [getGameById] Fetching game:', gameId);
  const result = await fetchApi<Game>(`/v1/sports/games/${gameId}/`);
  console.log('🎮 [getGameById] Got game:', result);
  return result;
}

/**
 * Get trending games with high betting volume
 */
export async function getTrendingGames(limit = 10): Promise<Game[]> {
  console.log('🔥 [getTrendingGames] Fetching trending games:', { limit });
  const result = await fetchApi<Game[]>(`/v1/sports/games/trending/?limit=${limit}`);
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
  
  return fetchApi(`/v1/sports/games/?${searchParams.toString()}`);
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
  
  return fetchApi<Market[]>(`/v1/sports/markets/?${searchParams.toString()}`);
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
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  const isTomorrow = date.toDateString() === new Date(now.getTime() + 24 * 60 * 60 * 1000).toDateString();
  const isYesterday = date.toDateString() === new Date(now.getTime() - 24 * 60 * 60 * 1000).toDateString();
  
  // For yesterday/today/tomorrow, show relative time
  if (isYesterday) {
    return 'Yesterday ' + date.toLocaleString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  }
  
  if (isToday) {
    return 'Today ' + date.toLocaleString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  }
  
  if (isTomorrow) {
    return 'Tomorrow ' + date.toLocaleString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  }
  
  // Otherwise show full date/time
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
 * Get complete game details with all odds from multiple sportsbooks
 */
export async function getGameDetails(gameId: string): Promise<any> {
  console.log('🎮 [getGameDetails] Fetching complete game details:', gameId);
  const result = await fetchApi<any>(`/v1/games/${gameId}/details/`);
  console.log('🎮 [getGameDetails] Got game details:', result);
  return result;
}

/**
 * Get AI Bookmaker analysis for a game
 */
export async function getBookmakerAnalysis(gameId: string): Promise<any> {
  console.log('🤖 [getBookmakerAnalysis] Fetching AI analysis for game:', gameId);
  const result = await fetchApi<any>(`/v1/games/${gameId}/bookmaker-analysis/`);
  console.log('🤖 [getBookmakerAnalysis] Got bookmaker analysis:', result);
  return result;
}

/**
 * Check if a game is live (with time-based inference)
 */
export function isGameLive(game: Game): boolean {
  // Check actual status first - handle various status formats from API
  const liveStatuses = [
    GameStatus.LIVE,
    GameStatus.HALFTIME,
    'status_in_progress',
    'status_end_period',
    'in_progress',
    'live',
    'halftime'
  ];

  if (liveStatuses.includes(game.status)) {
    return true;
  }

  // If status is 'scheduled' but game should have started, infer it's likely live
  if (game.status === GameStatus.SCHEDULED || game.status === 'status_scheduled') {
    const now = new Date();
    const gameTime = new Date(game.scheduled_start);
    const timeDiff = now.getTime() - gameTime.getTime();
    const hoursDiff = timeDiff / (1000 * 60 * 60);

    // If game started within last 4 hours, it's likely live
    // (most games don't last longer than 4 hours)
    if (hoursDiff >= 0 && hoursDiff <= 4) {
      return true;
    }
  }

  return false;
}

/**
 * Check if a game is finished (with time-based inference)
 */
export function isGameFinished(game: Game): boolean {
  // Check actual status first - handle various status formats from API
  const finalStatuses = [
    GameStatus.FINAL,
    'status_final',
    'final',
    'completed',
    'finished'
  ];

  if (finalStatuses.includes(game.status)) {
    return true;
  }

  // If status is 'scheduled' but game should be over, infer it's likely finished
  if (game.status === GameStatus.SCHEDULED || game.status === 'status_scheduled') {
    const now = new Date();
    const gameTime = new Date(game.scheduled_start);
    const timeDiff = now.getTime() - gameTime.getTime();
    const hoursDiff = timeDiff / (1000 * 60 * 60);

    // If game started more than 4 hours ago, it's likely finished
    // (most games finish within 4 hours)
    if (hoursDiff > 4) {
      return true;
    }
  }

  return false;
}

/**
 * Get inferred game status based on time if status is still 'scheduled'
 */
export function getInferredGameStatus(game: Game): GameStatus {
  // If status is not scheduled, return actual status
  if (game.status !== GameStatus.SCHEDULED) {
    return game.status;
  }
  
  const now = new Date();
  const gameTime = new Date(game.scheduled_start);
  const timeDiff = now.getTime() - gameTime.getTime();
  const hoursDiff = timeDiff / (1000 * 60 * 60);
  
  // Game hasn't started yet
  if (hoursDiff < 0) {
    return GameStatus.SCHEDULED;
  }
  
  // Game started within last 4 hours - likely live
  if (hoursDiff <= 4) {
    return GameStatus.LIVE;
  }
  
  // Game started more than 4 hours ago - likely finished
  return GameStatus.FINAL;
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
 * Get upcoming games date range (today to 7 days ahead)
 */
export function getUpcomingDateRange(): { from: string; to: string } {
  return {
    from: getTodayDateString(),
    to: getDateString(7)
  };
}

/**
 * Get this week's date range (Monday to Sunday)
 */
export function getThisWeekDateRange(): { from: string; to: string } {
  const today = new Date();
  const dayOfWeek = today.getDay();
  const monday = new Date(today);
  const sunday = new Date(today);
  
  // Get Monday (start of week)
  monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
  
  // Get Sunday (end of week)
  sunday.setDate(monday.getDate() + 6);
  
  return {
    from: monday.toISOString().split('T')[0],
    to: sunday.toISOString().split('T')[0]
  };
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
}): Promise<{
  success: boolean;
  message: string;
  games_synced?: number;
  total_games_fetched?: number;
  games_with_odds?: number;
  data?: any;
}> {
  console.log('🔄 [syncSportsData] Starting sync with options:', options);
  console.log('🔄 [syncSportsData] Syncing with ESPN + The Odds API');

  const result = await fetchApi<{
    success: boolean;
    message: string;
    games_synced?: number;
    total_games_fetched?: number;
    games_with_odds?: number;
    data?: any;
  }>('/v1/sports/sync/', {
    method: 'POST',
    body: JSON.stringify(options),
  });

  console.log('🔄 [syncSportsData] Full sync result:', {
    success: result.success,
    message: result.message,
    games_synced: result.games_synced,
    total_games_fetched: result.total_games_fetched,
    games_with_odds: result.games_with_odds,
    data: result.data,
    fullResult: result
  });

  return result;
}

/**
 * Get real weather data for a venue using WeatherAPI
 */
export async function getWeatherData(venue: string): Promise<{
  success: boolean;
  location?: string;
  condition?: string;
  temperature?: number;
  humidity?: number;
  wind?: string;
  wind_speed?: number;
  wind_direction?: string;
  feels_like?: number;
  uv_index?: number;
  visibility?: number;
  last_updated?: string;
  icon?: string;
}> {
  console.log('🌤️ [getWeatherData] Fetching weather for venue:', venue);
  
  const result = await fetchApi<{
    success: boolean;
    location?: string;
    condition?: string;
    temperature?: number;
    humidity?: number;
    wind?: string;
    wind_speed?: number;
    wind_direction?: string;
    feels_like?: number;
    uv_index?: number;
    visibility?: number;
    last_updated?: string;
    icon?: string;
  }>(`/v1/sports/weather/?venue=${encodeURIComponent(venue)}`);
  
  console.log('🌤️ [getWeatherData] Weather result:', result);
  return result;
}

/**
 * Get real injury data for teams using injury intelligence API
 */
export async function getInjuryData(homeTeam: string, awayTeam: string): Promise<{
  success: boolean;
  injuries?: Array<{
    team: string;
    player: string;
    jersey_number: number;
    position: string;
    injury: string;
    status: 'Questionable' | 'Probable' | 'Doubtful' | 'Out';
    impact_level: 'Low' | 'Medium' | 'High';
  }>;
  summary?: {
    total_injuries: number;
    players_out: number;
    questionable: number;
    last_updated: string;
    home_team_injuries: number;
    away_team_injuries: number;
  };
  teams?: {
    home_team: string;
    away_team: string;
  };
}> {
  console.log('🏥 [getInjuryData] Fetching injuries for teams:', homeTeam, 'vs', awayTeam);
  
  const result = await fetchApi<{
    success: boolean;
    injuries?: Array<{
      team: string;
      player: string;
      jersey_number: number;
      position: string;
      injury: string;
      status: 'Questionable' | 'Probable' | 'Doubtful' | 'Out';
      impact_level: 'Low' | 'Medium' | 'High';
    }>;
    summary?: {
      total_injuries: number;
      players_out: number;
      questionable: number;
      last_updated: string;
      home_team_injuries: number;
      away_team_injuries: number;
    };
    teams?: {
      home_team: string;
      away_team: string;
    };
  }>(`/v1/sports/injuries/?home_team=${encodeURIComponent(homeTeam)}&away_team=${encodeURIComponent(awayTeam)}`);
  
  console.log('🏥 [getInjuryData] Injury result:', result);
  return result;
}

/**
 * Get betting intelligence data for teams
 */
export async function getBettingIntelligence(homeTeam: string, awayTeam: string): Promise<{
  success: boolean;
  trends?: Array<{
    type: string;
    category: string;
    text: string;
    confidence: 'High' | 'Medium' | 'Low';
    impact: 'Positive' | 'Negative' | 'Neutral' | 'Recommended' | 'Pass' | 'Bearish' | 'Overpriced' | 'Follow Sharp';
    value?: string;
    kelly_suggestion?: string;
    kelly_percentage?: string;
    risk_level?: string;
    expected_value?: string;
    public_percentage?: string;
    sharp_indicator?: string;
    allocation_percent?: string;
    expected_roi?: string;
    efficiency_rating?: number;
    analysis?: string;
  }>;
  analysis?: {
    KELLY_RECOMMENDATION?: {
      allocation_percent: string;
      expected_roi: string;
      analysis: string;
    };
    MARKET_VALUE?: {
      efficiency_rating: number;
      analysis: string;
    };
    ATS_ANALYSIS?: {
      analysis: string;
    };
    MARKET_SENTIMENT?: {
      public_percentage: string;
      sharp_percentage: string;
      analysis: string;
    };
    SITUATIONAL_EDGE?: {
      analysis: string;
    };
    TOTALS_ANALYSIS?: {
      analysis: string;
    };
    SCORING_EDGE?: {
      analysis: string;
    };
  };
  summary?: {
    total_insights: number;
    value_opportunities: number;
    kelly_recommendations: number;
    market_efficiency: string;
    suggested_kelly_allocation: string;
    risk_assessment: string;
    edge_confidence: string;
    overall_recommendation: string;
    expected_roi: string;
    last_updated: string;
  };
  teams?: {
    home_team: string;
    away_team: string;
  };
  agents_used?: string[];
}> {
  console.log('📊 [getBettingIntelligence] Fetching betting intelligence for teams:', homeTeam, 'vs', awayTeam);
  
  const result = await fetchApi<{
    success: boolean;
    trends?: Array<{
      type: string;
      category: string;
      text: string;
      confidence: 'High' | 'Medium' | 'Low';
      impact: 'Positive' | 'Negative' | 'Neutral' | 'Recommended' | 'Pass' | 'Bearish' | 'Overpriced' | 'Follow Sharp';
      value?: string;
      kelly_suggestion?: string;
      kelly_percentage?: string;
      risk_level?: string;
      expected_value?: string;
      public_percentage?: string;
      sharp_indicator?: string;
      allocation_percent?: string;
      expected_roi?: string;
      efficiency_rating?: number;
      analysis?: string;
    }>;
    analysis?: {
      KELLY_RECOMMENDATION?: {
        allocation_percent: string;
        expected_roi: string;
        analysis: string;
      };
      MARKET_VALUE?: {
        efficiency_rating: number;
        analysis: string;
      };
      ATS_ANALYSIS?: {
        analysis: string;
      };
      MARKET_SENTIMENT?: {
        public_percentage: string;
        sharp_percentage: string;
        analysis: string;
      };
      SITUATIONAL_EDGE?: {
        analysis: string;
      };
      TOTALS_ANALYSIS?: {
        analysis: string;
      };
      SCORING_EDGE?: {
        analysis: string;
      };
    };
    summary?: {
      total_insights: number;
      value_opportunities: number;
      kelly_recommendations: number;
      market_efficiency: string;
      suggested_kelly_allocation: string;
      risk_assessment: string;
      edge_confidence: string;
      overall_recommendation: string;
      expected_roi: string;
      last_updated: string;
    };
    teams?: {
      home_team: string;
      away_team: string;
    };
    agents_used?: string[];
  }>(`/v1/sports/betting-intelligence/?home_team=${encodeURIComponent(homeTeam)}&away_team=${encodeURIComponent(awayTeam)}`);
  
  console.log('📊 [getBettingIntelligence] Betting intelligence result:', result);
  return result;
}

/**
 * Universal Intelligence API - Domain-agnostic decision analysis
 */
export interface DecisionContext {
  domain: 'SPORTS_BETTING' | 'TRADING' | 'CRYPTO' | 'REAL_ESTATE' | 'BUSINESS';
  entity_id: string;
  data_points: Record<string, any>;
  risk_level?: number;
  time_horizon?: string;
  constraints?: Record<string, any>;
}

export interface IntelligenceResult {
  primary_action: 'STRONG_EXECUTE' | 'EXECUTE' | 'WAIT' | 'AVOID' | 'STRONG_AVOID';
  confidence: number;
  position_sizing: {
    kelly_percentage: number;
    recommended_stake: number;
    max_exposure: number;
  };
  risk_assessment: {
    overall_risk: number;
    risk_factors: string[];
    mitigation_strategies: string[];
  };
  agent_consensus: {
    alpha_squadron: number;
    bravo_squadron: number;
    charlie_squadron: number;
    delta_squadron: number;
    echo_squadron: number;
  };
  similar_scenarios: Array<{
    domain: string;
    entity_id: string;
    timestamp: string;
    outcome: string;
    similarity: number;
  }>;
  cross_domain_patterns: Array<{
    pattern_name: string;
    confidence: number;
    description: string;
    historical_success_rate: number;
  }>;
  memory_references: string[];
  execution_plan?: string[];
}

export async function getUniversalIntelligence(context: DecisionContext): Promise<IntelligenceResult> {
  console.log('🧠 [Universal Intelligence] Analyzing decision context:', context);

  const result = await fetchApi<IntelligenceResult>('/v1/sports/intelligence/analyze/', {
    method: 'POST',
    body: JSON.stringify(context)
  });

  console.log('🧠 [Universal Intelligence] Analysis result:', result);
  return result;
}

/**
 * Search intelligence memory for similar patterns and decisions
 */
export interface MemorySearchQuery {
  query: string;
  domain?: string;
  limit?: number;
  time_range?: {
    start: string;
    end: string;
  };
}

export interface MemorySearchResult {
  memories: Array<{
    id: string;
    domain: string;
    entity_id: string;
    timestamp: string;
    context: Record<string, any>;
    decision: string;
    outcome?: string;
    similarity_score: number;
  }>;
  patterns_found: string[];
  total_results: number;
}

export async function searchMemory(query: MemorySearchQuery): Promise<MemorySearchResult> {
  console.log('🔍 [Memory Search] Searching intelligence memory:', query);

  const params = new URLSearchParams();
  params.append('query', query.query);
  if (query.domain) params.append('domain', query.domain);
  if (query.limit) params.append('limit', query.limit.toString());
  if (query.time_range) {
    params.append('start_time', query.time_range.start);
    params.append('end_time', query.time_range.end);
  }

  const result = await fetchApi<MemorySearchResult>(`/v1/sports/intelligence/memory/search/?${params.toString()}`);

  console.log('🔍 [Memory Search] Found', result.total_results, 'results');
  return result;
}

/**
 * Get pattern library - recognized patterns across all domains
 */
export interface Pattern {
  id: string;
  name: string;
  description: string;
  domains: string[];
  frequency: number;
  success_rate: number;
  last_seen: string;
  examples: Array<{
    domain: string;
    entity_id: string;
    timestamp: string;
    outcome: string;
  }>;
}

export async function getPatternLibrary(domain?: string): Promise<Pattern[]> {
  console.log('📚 [Pattern Library] Fetching patterns for domain:', domain || 'all');

  const url = domain
    ? `/v1/sports/intelligence/patterns/?domain=${domain}`
    : '/v1/sports/intelligence/patterns/';

  const result = await fetchApi<Pattern[]>(url);

  console.log('📚 [Pattern Library] Found', result.length, 'patterns');
  return result;
}

/**
 * Submit feedback on intelligence decision
 */
export interface IntelligenceFeedback {
  entity_id: string;
  domain: string;
  decision_id: string;
  outcome: 'SUCCESS' | 'FAILURE' | 'NEUTRAL';
  actual_return?: number;
  notes?: string;
}

export async function submitIntelligenceFeedback(feedback: IntelligenceFeedback): Promise<void> {
  console.log('📝 [Intelligence Feedback] Submitting feedback:', feedback);

  await fetchApi('/v1/sports/intelligence/feedback/', {
    method: 'POST',
    body: JSON.stringify(feedback)
  });

  console.log('📝 [Intelligence Feedback] Feedback submitted successfully');
}