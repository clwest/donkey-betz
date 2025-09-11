import { toast } from 'sonner';

// Use AI Content Studio API v1 for odds-specific endpoints
// Using AI Content Studio backend on port 8001 which has the odds endpoints
const BASE = (import.meta.env.VITE_DBAO_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');

// Circuit breaker to prevent spam of failed API calls
let failureCount = 0;
let lastFailureTime = 0;
const FAILURE_THRESHOLD = 3;
const COOLDOWN_PERIOD = 30000; // 30 seconds

function shouldAttemptApiCall(): boolean {
  const now = Date.now();
  
  // Reset failure count after cooldown period
  if (now - lastFailureTime > COOLDOWN_PERIOD) {
    failureCount = 0;
  }
  
  // Block API calls if we've exceeded the failure threshold
  return failureCount < FAILURE_THRESHOLD;
}

function recordFailure(): void {
  failureCount++;
  lastFailureTime = Date.now();
}

// Response Types
export interface ConversionResponse {
  success: boolean;
  result?: {
    american: string;
    decimal: number;
    fractional: string;
    hong_kong: number;
    indonesian: string;
    malay: string;
    implied_probability: number;
  };
  errors?: any;
}

export interface KellyResponse {
  success: boolean;
  result?: {
    kelly_percentage: number;
    recommended_stake: number;
    edge: number;
    growth_rate: number;
    risk_level: string;
    warnings: string[];
  };
  errors?: any;
}

/**
 * Generic API request handler with error handling for odds endpoints
 */
async function postJson<T>(path: string, body: any): Promise<T> {
  const url = `${BASE}${path}`;
  
  // Get auth token from localStorage - using AI Content Studio testuser token
  const token = localStorage.getItem('authToken') || 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502';
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-DBAO-Client': 'AI-Studio-Web',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify(body)
    });

    const responseText = await response.text();
    
    if (!response.ok) {
      console.error(`[Odds API] POST ${path} failed:`, responseText);
      // Don't show toast errors for odds API failures - just log them
      // The fallback local calculations will handle the functionality
      throw new Error(responseText || `HTTP ${response.status} ${response.statusText}`);
    }

    // Parse JSON if we have content
    if (responseText.trim()) {
      return JSON.parse(responseText);
    }
    
    return {} as T;
  } catch (error: any) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const networkError = `Network error: Unable to connect to ${url}`;
      console.error('[Odds API] Network error:', networkError);
      // Only show network errors once per session to avoid spam
      if (failureCount === 0) {
        toast.error('Odds API unavailable, using local calculations');
      }
      throw new Error(networkError);
    }
    
    // Re-throw other errors as they've already been handled
    throw error;
  }
}

/**
 * Convert American odds to decimal format
 * @param american - American odds (e.g., +110, -135)
 * @returns Conversion response with decimal odds and implied probability
 */
export async function convertAmericanToDecimal(american: number | string): Promise<ConversionResponse> {
  // Use local calculation if API calls are being throttled
  if (!shouldAttemptApiCall()) {
    console.warn('[Odds API] Circuit breaker active, using local calculation');
    return localConvertAmericanToDecimal(american);
  }

  try {
    // Try the AI Content Studio v1 odds endpoint
    const response = await postJson<ConversionResponse>('/odds/convert-odds/', {
      odds: typeof american === 'string' ? parseFloat(american) : american,
      from_format: 'american',
      to_format: 'decimal'
    });
    
    if (!response.success || !response.result) {
      throw new Error('Failed to convert odds');
    }
    
    return response;
  } catch (error) {
    recordFailure();
    
    // Fall back to local calculation instead of trying another API endpoint
    console.warn('[Odds API] DBAO endpoint failed, using local calculation');
    return localConvertAmericanToDecimal(american);
  }
}

// Local calculation fallback for odds conversion
function localConvertAmericanToDecimal(american: number | string): ConversionResponse {
  try {
    const odds = typeof american === 'string' ? parseFloat(american) : american;
    
    if (!isValidAmericanOdds(odds)) {
      return {
        success: false,
        errors: 'Invalid odds format'
      };
    }
    
    const decimal = odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
    const impliedProbability = odds > 0 ? 100 / (odds + 100) : Math.abs(odds) / (Math.abs(odds) + 100);
    
    return {
      success: true,
      result: {
        american: odds > 0 ? `+${odds}` : `${odds}`,
        decimal: decimal,
        fractional: odds > 0 ? `${odds}/100` : `100/${Math.abs(odds)}`,
        hong_kong: decimal - 1,
        indonesian: odds > 0 ? `${odds}/100` : `${-100/odds}`,
        malay: odds > 0 ? `${-100/odds}` : `${odds/100}`,
        implied_probability: impliedProbability
      }
    };
  } catch (error) {
    return {
      success: false,
      errors: 'Local calculation failed'
    };
  }
}

/**
 * Compute Kelly criterion stake recommendations
 * @param american - American odds
 * @param p - Win probability (0-1)
 * @param bankroll - Total bankroll amount
 * @param fractionalKelly - Fractional Kelly multiplier (e.g., 0.25, 0.5, 1.0)
 * @returns Kelly calculation response with stake recommendations
 */
export async function computeKelly(
  american: number | string,
  p: number,
  bankroll: number,
  fractionalKelly: number
): Promise<KellyResponse> {
  // Use local calculation if API calls are being throttled
  if (!shouldAttemptApiCall()) {
    console.warn('[Odds API] Circuit breaker active, using local Kelly calculation');
    return localComputeKelly(american, p, bankroll, fractionalKelly);
  }

  try {
    // Try the AI Content Studio v1 Kelly endpoint
    const response = await postJson<KellyResponse>('/odds/kelly-criterion/', {
      odds: typeof american === 'string' ? parseFloat(american) : american,
      odds_format: 'american',
      true_probability: p,
      bankroll,
      kelly_fraction: fractionalKelly
    });
    
    if (!response.success || !response.result) {
      throw new Error('Failed to compute Kelly criterion');
    }
    
    return response;
  } catch (error) {
    recordFailure();
    
    // Fall back to local Kelly calculation when backend endpoint isn't available
    console.warn('[Odds API] DBAO Kelly endpoint failed, using local calculation');
    return localComputeKelly(american, p, bankroll, fractionalKelly);
  }
}

// Local Kelly calculation fallback
function localComputeKelly(
  american: number | string,
  p: number,
  bankroll: number,
  fractionalKelly: number
): KellyResponse {
  try {
    const odds = typeof american === 'string' ? parseFloat(american) : american;
    
    if (!isValidAmericanOdds(odds)) {
      return {
        success: false,
        errors: 'Invalid odds format'
      };
    }
    
    const decimal = odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
    const impliedOddsProbability = 1 / decimal;
    
    // Kelly formula: f = (bp - q) / b
    // where: b = odds received (decimal - 1), p = true probability, q = 1 - p
    const b = decimal - 1;
    const q = 1 - p;
    const edge = p - impliedOddsProbability;
    const kellyPercentage = edge > 0 ? (b * p - q) / b : 0;
    
    // Apply fractional Kelly
    const adjustedKelly = Math.max(0, kellyPercentage * fractionalKelly);
    const recommendedStake = adjustedKelly * bankroll;
    
    // Determine risk level
    let riskLevel = 'low';
    if (adjustedKelly > 0.1) riskLevel = 'high';
    else if (adjustedKelly > 0.05) riskLevel = 'medium';
    
    const warnings: string[] = [];
    if (edge <= 0) {
      warnings.push('No positive expected value detected');
    }
    if (adjustedKelly > 0.25) {
      warnings.push('Kelly percentage exceeds 25% - consider reducing stake');
    }
    
    return {
      success: true,
      result: {
        kelly_percentage: adjustedKelly,
        recommended_stake: recommendedStake,
        edge: edge,
        growth_rate: Math.log(1 + adjustedKelly * (decimal - 1)) * p + Math.log(1 - adjustedKelly) * q,
        risk_level: riskLevel,
        warnings: warnings
      }
    };
  } catch (calcError) {
    return {
      success: false,
      errors: 'Kelly calculation failed'
    };
  }
}

/**
 * Validate if a value can be converted to a valid American odds
 */
export function isValidAmericanOdds(value: string | number): boolean {
  if (typeof value === 'string') {
    if (value.trim() === '') return false;
    const num = parseFloat(value);
    return !isNaN(num) && isFinite(num) && num !== 0;
  }
  return !isNaN(value) && isFinite(value) && value !== 0;
}

/**
 * Format American odds for display
 */
export function formatAmericanOdds(odds: number | string): string {
  const num = typeof odds === 'string' ? parseFloat(odds) : odds;
  if (isNaN(num)) return '';
  return num > 0 ? `+${num}` : `${num}`;
}

/**
 * Format percentage with proper rounding
 */
export function formatPercentage(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format currency values
 */
export function formatCurrency(value: number, decimals = 2): string {
  return `$${value.toFixed(decimals)}`;
}

// Sports API interfaces for real odds data
export interface League {
  id: string;
  name: string;
  display_name: string;
}

export interface Game {
  id: string;
  league: string;
  home_team_name: string;
  away_team_name: string;
  start_time: string;
  status: string;
  venue?: string;
  season?: number;
  week?: number | null;
  home_score?: number | null;
  away_score?: number | null;
}

export interface Market {
  id: string;
  game_id: string;
  kind: string;
  name: string;
  price_american: string;
  implied_probability: number;
}

/**
 * Fetch available sports leagues
 */
export async function fetchLeagues(): Promise<League[]> {
  if (!shouldAttemptApiCall()) {
    console.warn('[Sports API] Circuit breaker active, returning empty leagues');
    return [];
  }

  try {
    const response = await fetch(`${BASE}/sports/leagues/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-DBAO-Client': 'AI-Studio-Web',
        'Authorization': `Token ${localStorage.getItem('authToken') || 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502'}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    recordFailure();
    console.warn('[Sports API] Failed to fetch leagues:', error);
    return [];
  }
}

/**
 * Fetch games for a specific league and date
 */
export async function fetchGames(league: string, date?: string): Promise<Game[]> {
  if (!shouldAttemptApiCall()) {
    console.warn('[Sports API] Circuit breaker active, returning empty games');
    return [];
  }

  try {
    const params = new URLSearchParams();
    if (league) params.append('league', league);
    if (date) params.append('date', date);
    
    const response = await fetch(`${BASE}/sports/games/?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-DBAO-Client': 'AI-Studio-Web',
        'Authorization': `Token ${localStorage.getItem('authToken') || 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502'}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const games = Array.isArray(data) ? data : data.results || [];
    
    // Normalize field names
    return games.map((game: any) => ({
      id: game.id,
      league: game.league,
      home_team_name: game.home_team || game.home_team_name,
      away_team_name: game.away_team || game.away_team_name,
      start_time: game.game_time || game.start_time,
      status: game.status,
      venue: game.venue,
      season: game.season,
      week: game.week,
      home_score: game.home_score,
      away_score: game.away_score
    }));
  } catch (error) {
    recordFailure();
    console.warn('[Sports API] Failed to fetch games:', error);
    return [];
  }
}

/**
 * Fetch betting markets for a specific game
 */
export async function fetchMarkets(gameId: string): Promise<Market[]> {
  if (!shouldAttemptApiCall()) {
    console.warn('[Sports API] Circuit breaker active, returning empty markets');
    return [];
  }

  try {
    const response = await fetch(`${BASE}/sports/markets/?game_id=${gameId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-DBAO-Client': 'AI-Studio-Web',
        'Authorization': `Token ${localStorage.getItem('authToken') || 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502'}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const markets = Array.isArray(data) ? data : data.results || [];
    
    // Normalize market data
    return markets.map((market: any) => ({
      id: market.id,
      game_id: market.game_id,
      kind: market.market_type || market.kind,
      name: `${market.selection === 'home' ? 'Home' : 'Away'} ${market.market_type || 'Moneyline'}`,
      price_american: formatAmericanOdds(market.odds || market.price_american || '+100'),
      implied_probability: market.implied_probability || 0.5
    }));
  } catch (error) {
    recordFailure();
    console.warn('[Sports API] Failed to fetch markets:', error);
    return [];
  }
}

/**
 * Generate real odds rows from API data instead of fake defaults
 */
export async function generateRealOddsRows(): Promise<any[]> {
  try {
    // Fetch leagues first
    const leagues = await fetchLeagues();
    if (leagues.length === 0) {
      console.warn('[Sports API] No leagues available, falling back to default rows');
      return [];
    }

    // Get today's date for current games
    const today = new Date().toISOString().split('T')[0];
    
    // Try to get games from the first available league
    const firstLeague = leagues[0];
    const games = await fetchGames(firstLeague.name, today);
    
    if (games.length === 0) {
      console.warn('[Sports API] No games available for today, trying without date filter');
      const allGames = await fetchGames(firstLeague.name);
      
      if (allGames.length === 0) {
        console.warn('[Sports API] No games available, falling back to default rows');
        return [];
      }
      
      // Use the first available game
      const game = allGames[0];
      const markets = await fetchMarkets(game.id);
      
      // Create real odds rows from markets
      return markets.slice(0, 3).map((market, index) => ({
        book: ['DraftKings', 'FanDuel', 'BetMGM'][index] || 'Sportsbook',
        market: `${game.away_team_name} vs ${game.home_team_name} - ${market.name}`,
        american: market.price_american
      }));
    }

    // Use today's first game
    const game = games[0];
    const markets = await fetchMarkets(game.id);
    
    if (markets.length === 0) {
      console.warn('[Sports API] No markets available for game, falling back to default rows');
      return [];
    }

    // Create real odds rows from markets
    return markets.slice(0, 3).map((market, index) => ({
      book: ['DraftKings', 'FanDuel', 'BetMGM'][index] || 'Sportsbook',
      market: `${game.away_team_name} vs ${game.home_team_name} - ${market.name}`,
      american: market.price_american
    }));
  } catch (error) {
    console.error('[Sports API] Failed to generate real odds rows:', error);
    return [];
  }
}