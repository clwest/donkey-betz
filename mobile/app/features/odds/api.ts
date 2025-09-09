import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Get unified API URL from environment with platform-specific fallbacks
const getApiBaseUrl = (): string => {
  // Check environment variable first
  const envUrl = process.env.EXPO_PUBLIC_DBAO_API_URL;
  if (envUrl) {
    console.log('[DBAO API] Using environment URL:', envUrl);
    return envUrl;
  }
  
  // Fallback to port 8001 for all environments - Unified backend
  const baseUrl = Platform.select({
    ios: 'http://localhost:8001/api/v1',
    android: 'http://10.0.2.2:8001/api/v1', // Android emulator localhost alias
    web: 'http://localhost:8001/api/v1',
    default: 'http://localhost:8001/api/v1'
  }) || 'http://localhost:8001/api/v1';

  // Log what we're using to help debug
  console.log('[DBAO API] Using fallback URL:', baseUrl);
  
  return baseUrl;
};

const DBAO_API_URL = getApiBaseUrl();

console.log('[DBAO API] Environment check:', {
  fromProcess: process.env.EXPO_PUBLIC_DBAO_API_URL,
  fromProcessAPI: process.env.EXPO_PUBLIC_API_URL,
  fromExpoConfig: Constants.expoConfig?.extra?.EXPO_PUBLIC_DBAO_API_URL,
  fromManifest: Constants.manifest?.extra?.EXPO_PUBLIC_DBAO_API_URL,
  final: DBAO_API_URL,
  platform: Platform.OS
});

export interface OddsConvertRequest {
  odds: number | string;
  from_format: string;
  to_format: string;
}

export interface OddsConvertResponse {
  success: boolean;
  result: {
    american: string;
    decimal: number;
    fractional: string;
    hong_kong: number;
    indonesian: string;
    malay: string;
    implied_probability: number;
  };
}

export interface KellyRequest {
  decimal_odds: number;
  win_probability: number;
  bankroll: number;
  fractional_kelly: number;
}

export interface KellyResponse {
  expected_value: number;
  full_kelly_percentage: number;
  recommended_stake: number;
  is_positive_ev: boolean;
}

export class DBAOApiError extends Error {
  constructor(message: string, public status?: number, public data?: any) {
    super(message);
    this.name = 'DBAOApiError';
  }
}

class DBAOApiClient {
  private baseUrl: string;

  constructor() {
    // Always use port 8001 - this is where Django backend runs
    this.baseUrl = DBAO_API_URL;
    console.log('DBAO API configured with URL:', this.baseUrl);
  }

  public async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    if (!this.baseUrl) {
      throw new DBAOApiError('DBAO API URL not configured. Please check your environment settings.');
    }

    const fullUrl = `${this.baseUrl}${endpoint}`;
    console.log(`[DBAO API] Request: ${options.method || 'GET'} ${fullUrl}`);
    
    if (options.body) {
      console.log('[DBAO API] Request body:', options.body);
    }

    try {
      const response = await fetch(fullUrl, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      console.log(`[DBAO API] Response status: ${response.status}`);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        let errorData;
        
        try {
          errorData = await response.json();
          console.error('[DBAO API] Error response:', errorData);
          errorMessage = errorData.message || errorData.error || `Request failed with status ${response.status}`;
        } catch {
          errorMessage = `Request failed with status ${response.status}`;
        }
        
        throw new DBAOApiError(errorMessage, response.status, errorData);
      }

      const data = await response.json();
      console.log('[DBAO API] Success response:', data);
      return data;
    } catch (error) {
      if (error instanceof DBAOApiError) {
        console.error('[DBAO API] API Error:', error.message, error.status);
        throw error;
      }
      
      // Handle network errors
      if (error instanceof TypeError && error.message.includes('Network')) {
        console.error('[DBAO API] Network error:', error.message);
        throw new DBAOApiError('Network error: Unable to connect to DBAO API. Please check your connection.');
      }
      
      console.error('[DBAO API] Unexpected error:', error);
      throw new DBAOApiError(error instanceof Error ? error.message : 'Unknown API error');
    }
  }

  async convertOdds(request: OddsConvertRequest): Promise<OddsConvertResponse> {
    return this.request<OddsConvertResponse>('/odds/convert-odds/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async calculateKelly(request: KellyRequest): Promise<KellyResponse> {
    return this.request<KellyResponse>('/odds/kelly-criterion/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Test connection method
  async testConnection(): Promise<boolean> {
    if (!this.baseUrl) {
      console.warn('DBAO API connection test failed: No URL configured');
      return false;
    }
    
    try {
      // Try a simple odds conversion to test the connection
      const response = await this.convertOdds({ 
        odds: 100, 
        from_format: 'american', 
        to_format: 'decimal' 
      });
      return response.success === true;
    } catch (error) {
      console.warn('DBAO API connection test failed:', error);
      return false;
    }
  }
}

// Create a singleton instance immediately
const apiInstance = new DBAOApiClient();

export const dbaoApi = {
  convertOdds: async (request: OddsConvertRequest): Promise<OddsConvertResponse> => {
    // Ensure odds is properly formatted
    const formattedRequest = {
      ...request,
      odds: typeof request.odds === 'string' ? 
        parseFloat(request.odds.replace(/[+-]/g, '')) : 
        request.odds
    };
    return apiInstance.convertOdds(formattedRequest);
  },
  
  calculateKelly: async (request: KellyRequest): Promise<KellyResponse> => {
    return apiInstance.calculateKelly(request);
  },
  
  testConnection: async (): Promise<boolean> => {
    return apiInstance.testConnection();
  }
};

// Helper functions for odds validation and formatting
export const parseAmericanOdds = (input: string): string => {
  const cleaned = input.trim();
  
  // Handle empty input
  if (!cleaned) return '';
  
  // Remove any existing +/- at start for processing
  const withoutSign = cleaned.replace(/^[+-]/, '');
  
  // Check if it's a valid number
  if (!/^\d+$/.test(withoutSign)) {
    return cleaned; // Return as-is if not valid
  }
  
  const number = parseInt(withoutSign);
  
  // For positive odds, ensure + sign
  if (!cleaned.startsWith('-')) {
    return `+${number}`;
  }
  
  return `-${number}`;
};

export const isValidAmericanOdds = (odds: string): boolean => {
  const cleaned = odds.trim();
  if (!cleaned) return false;
  
  // Must start with + or -
  if (!cleaned.match(/^[+-]/)) return false;
  
  // Extract the number part
  const numberPart = cleaned.substring(1);
  
  // Must be a valid integer
  if (!/^\d+$/.test(numberPart)) return false;
  
  const number = parseInt(numberPart);
  
  // Must be at least 100 (standard odds minimum)
  return number >= 100;
};

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatPercentage = (value: number): string => {
  return `${value.toFixed(2)}%`;
};

// Sports API interfaces and methods
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
  // Additional fields from backend
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

export interface GamesRequest {
  league: string;
  date: string;
}

export interface MarketsRequest {
  league?: string;
  game_id?: string;
  kind?: string;
}

// Add sports API methods to existing DBAO client
const sportsApi = {
  leagues: async (): Promise<League[]> => {
    try {
      const response = await apiInstance.request<League[] | { results: League[] }>('/sports/leagues/');
      return Array.isArray(response) ? response : response.results || [];
    } catch (error) {
      console.warn('Failed to fetch leagues:', error);
      return [];
    }
  },

  games: async (params: GamesRequest): Promise<Game[]> => {
    try {
      // Normalize league ID: map "NCAA Football" to "NCAAF" if needed
      const normalizedParams = {
        ...params,
        league: params.league === "NCAA Football" ? "NCAAF" : params.league
      };
      
      const query = new URLSearchParams(normalizedParams).toString();
      console.log(`[Sports API] Fetching games with normalized params:`, normalizedParams);
      const response = await apiInstance.request<any[]>(`/sports/games/?${query}`);
      const games = Array.isArray(response) ? response : [];
      
      // Normalize field names from backend format to UI format
      const normalizedGames = games.map(game => ({
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
      
      console.log(`[Sports API] Normalized ${normalizedGames.length} games:`, normalizedGames);
      return normalizedGames;
    } catch (error) {
      console.warn('Failed to fetch games:', error);
      return [];
    }
  },

  markets: async (params: MarketsRequest): Promise<Market[]> => {
    try {
      const query = new URLSearchParams(params as any).toString();
      console.log(`[Sports API] Fetching markets with params:`, params);
      const response = await apiInstance.request<any[]>(`/sports/markets/?${query}`);
      
      // Handle the backend response format
      if (response && response.length > 0) {
        // Normalize market data from backend format to UI format
        const normalizedMarkets = response.map(market => ({
          id: market.id,
          game_id: market.game_id,
          kind: market.market_type || market.kind,
          name: `${market.selection === 'home' ? 'Home' : 'Away'} ${market.market_type || 'Moneyline'}`,
          price_american: parseAmericanOdds(market.odds || market.price_american || '+100'),
          implied_probability: market.implied_probability || 0.5
        }));
        
        console.log(`[Sports API] Normalized ${normalizedMarkets.length} markets:`, normalizedMarkets);
        return normalizedMarkets;
      }
      
      console.log(`[Sports API] No market data found`);
      return [];
    } catch (error) {
      console.warn('Failed to fetch markets:', error);
      return [];
    }
  },

  kelly: async (params: { odds_format: string, odds_value: string, win_probability: number, bankroll: number, fractional_kelly: number }) => {
    try {
      // Convert to backend expected format
      const backendParams = {
        odds_format: params.odds_format,
        odds: parseFloat(params.odds_value.replace(/[+-]/g, '')), // Remove + or - sign
        true_probability: params.win_probability,
        bankroll: params.bankroll,
        fractional_kelly: params.fractional_kelly
      };
      
      const response = await apiInstance.request<{ success: boolean, result: any }>('/odds/kelly-criterion/', {
        method: 'POST',
        body: JSON.stringify(backendParams),
      });
      
      if (response.success && response.result) {
        return {
          recommended_stake: response.result.recommended_stake,
          kelly_percentage: response.result.kelly_percentage,
          expected_value: response.result.edge * 100, // Convert to percentage
          is_positive_ev: response.result.edge > 0
        };
      }
      
      throw new Error('Invalid response from Kelly API');
    } catch (error) {
      console.warn('Failed to calculate Kelly criterion:', error);
      throw error;
    }
  }
};

// Export sports API methods
export { sportsApi };