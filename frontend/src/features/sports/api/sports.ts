import { toast } from 'sonner';

// Get DBAO API URL from environment and strip trailing slash
// Using AI Content Studio backend on port 8001 which has the sports endpoints
const BASE = (import.meta.env.VITE_DBAO_API_URL || 'http://localhost:8001/api/v1').replace(/\/$/, '');
const DBAO_API_URL = BASE;

// Types for sports API responses
export interface League {
  id: string;
  name: string;
  abbrev?: string;
  active: boolean;
  sport?: string;
}

export interface Team {
  id: string;
  name: string;
  abbrev: string;
  location: string;
}

export interface Game {
  id: string;
  league: string;
  home_team_name: string;
  away_team_name: string;
  start_time: string; // ISO timestamp
  status: 'scheduled' | 'live' | 'completed';
  venue?: string;
  week?: number;
  season?: number;
  home_score?: number;
  away_score?: number;
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
  
  // Get auth token from localStorage - using AI Content Studio testuser token
  const token = localStorage.getItem('authToken') || 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502';
  
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
      
      // Handle paginated responses from Django REST Framework
      if (data && typeof data === 'object' && 'results' in data && Array.isArray(data.results)) {
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
 * Fetch available leagues from DBAO API
 * Returns active leagues that can be used for filtering
 */
export async function listLeagues(): Promise<League[]> {
  const url = `${BASE}/sports/leagues/`;
  // Get auth token from localStorage - using AI Content Studio testuser token
  const token = localStorage.getItem('authToken') || 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502';
  
  const r = await fetch(url, {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const t = await r.text();
  
  if (!r.ok) {
    console.error(`[WEB SPORTS] GET ${url} failed:`, t);
    throw new Error(`HTTP ${r.status}: ${t}`);
  }
  
  const j = JSON.parse(t);
  console.log('[WEB SPORTS] GET', url, '→', j?.length || 0);
  
  // Transform response to match our League interface
  // DBAO returns {code: "NCAAF", name: "NCAA Football"} 
  // We need {id: "NCAAF", name: "NCAA Football", active: true}
  const leagues = Array.isArray(j) ? j : [];
  return leagues.map(league => ({
    id: league.code || league.id,
    name: league.name,
    active: league.active !== false, // Default to true if not specified
    sport: league.sport,
    abbrev: league.abbrev
  }));
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
  
  return fetchApi<Game[]>(`/sports/games/?${searchParams.toString()}`);
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
  
  return fetchApi<Market[]>(`/sports/markets/?${searchParams.toString()}`);
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
  
  return fetchApi<KellyResponse>('/odds-calc/kelly-criterion/', {
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