import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

// Separate interface for sports betting opportunities
export interface BettingOpportunity {
  id: string;
  sport: string;
  game: string;
  market: string;
  odds: number;
  book: string;
  ev: number;
  kelly: number;
  recommendedStake: number;
  confidence: number;
  analysis?: string;
  createdAt: string;
  expiresAt?: string;
}

export interface SportsBettingAnalysisRequest {
  sport: string;
  game_id?: string;
  odds?: Array<{ home: number; away: number; [key: string]: number }>;
  bankroll?: number;
  kelly_fraction?: number;
  analysis_type?: 'game' | 'player' | 'prop';
}

interface SportsState {
  // Sports Betting Data
  bettingOpportunities: BettingOpportunity[];
  liveBettingOpportunities: BettingOpportunity[];
  arbitrageOpportunities: BettingOpportunity[];
  
  // Loading states
  bettingLoading: boolean;
  bettingError: string | null;
  
  // Selected data
  selectedOpportunity: BettingOpportunity | null;
  selectedSport: string | null;
  
  // Actions
  fetchBettingOpportunities: (sport?: string) => Promise<void>;
  fetchLiveOpportunities: (sport?: string) => Promise<void>;
  fetchArbitrageOpportunities: () => Promise<void>;
  analyzeBetting: (request: SportsBettingAnalysisRequest) => Promise<BettingOpportunity[]>;
  
  selectOpportunity: (opportunity: BettingOpportunity | null) => void;
  selectSport: (sport: string | null) => void;
  
  // Utility actions
  clearErrors: () => void;
  reset: () => void;
}

const initialState = {
  bettingOpportunities: [],
  liveBettingOpportunities: [],
  arbitrageOpportunities: [],
  bettingLoading: false,
  bettingError: null,
  selectedOpportunity: null,
  selectedSport: null,
};

// Mock sports API service (to replace the mixed functionality from agent-orchestra.service.ts)
class SportsService {
  private static BASE_URL = import.meta.env.VITE_DBAO_API_URL || 'http://localhost:8000/api/v1';
  
  static async analyzeBettingOpportunity(request: SportsBettingAnalysisRequest): Promise<BettingOpportunity[]> {
    try {
      console.log('[Sports API] Analyzing betting opportunity:', request);
      
      const response = await fetch(`${this.BASE_URL}/sports/betting/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Sports-Client': 'AI-Studio-Web'
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return Array.isArray(data) ? data : data.opportunities || [];
    } catch (error) {
      console.warn('[Sports API] Betting analysis unavailable, using mock data');
      
      // Return mock opportunities for development
      return [
        {
          id: `mock-${Date.now()}`,
          sport: request.sport,
          game: 'Sample Game',
          market: 'Moneyline',
          odds: 150,
          book: 'MockBook',
          ev: 5.2,
          kelly: 0.03,
          recommendedStake: request.bankroll ? request.bankroll * 0.03 : 30,
          confidence: 0.75,
          analysis: 'Mock analysis for development',
          createdAt: new Date().toISOString(),
        }
      ];
    }
  }
  
  static async getLiveOpportunities(sport?: string): Promise<BettingOpportunity[]> {
    try {
      const endpoint = sport 
        ? `${this.BASE_URL}/sports/betting/live?sport=${encodeURIComponent(sport)}`
        : `${this.BASE_URL}/sports/betting/live`;
      
      const response = await fetch(endpoint, {
        headers: {
          'X-Sports-Client': 'AI-Studio-Web'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return Array.isArray(data) ? data : data.opportunities || [];
    } catch (error) {
      console.warn('[Sports API] Live opportunities unavailable');
      return [];
    }
  }
  
  static async getArbitrageOpportunities(): Promise<BettingOpportunity[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/sports/betting/arbitrage`, {
        headers: {
          'X-Sports-Client': 'AI-Studio-Web'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return Array.isArray(data) ? data : data.opportunities || [];
    } catch (error) {
      console.warn('[Sports API] Arbitrage opportunities unavailable');
      return [];
    }
  }
}

export const useSportsStore = create<SportsState>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,

    fetchBettingOpportunities: async (sport?: string) => {
      set({ bettingLoading: true, bettingError: null });
      try {
        // Provide sample analysis request
        const opportunities = await SportsService.analyzeBettingOpportunity({
          sport: sport || 'nfl',
          odds: [{ home: 150, away: -200 }], // Sample odds
          bankroll: 1000,
          kelly_fraction: 0.25
        });
        set({ bettingOpportunities: opportunities, bettingLoading: false });
      } catch (error: any) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch betting opportunities';
        set({ bettingError: errorMessage, bettingLoading: false });
      }
    },

    fetchLiveOpportunities: async (sport?: string) => {
      set({ bettingLoading: true });
      try {
        const opportunities = await SportsService.getLiveOpportunities(sport);
        set({ liveBettingOpportunities: opportunities, bettingLoading: false });
      } catch (error: any) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch live opportunities';
        set({ bettingError: errorMessage, bettingLoading: false });
      }
    },

    fetchArbitrageOpportunities: async () => {
      set({ bettingLoading: true });
      try {
        const opportunities = await SportsService.getArbitrageOpportunities();
        set({ arbitrageOpportunities: opportunities, bettingLoading: false });
      } catch (error: any) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch arbitrage opportunities';
        set({ bettingError: errorMessage, bettingLoading: false });
      }
    },

    analyzeBetting: async (request: SportsBettingAnalysisRequest) => {
      try {
        const opportunities = await SportsService.analyzeBettingOpportunity(request);
        // Update the main opportunities array
        set({ bettingOpportunities: opportunities });
        return opportunities;
      } catch (error: any) {
        const errorMessage = error instanceof Error ? error.message : 'Analysis failed';
        set({ bettingError: errorMessage });
        return [];
      }
    },

    selectOpportunity: (opportunity: BettingOpportunity | null) => {
      set({ selectedOpportunity: opportunity });
    },

    selectSport: (sport: string | null) => {
      set({ selectedSport: sport });
    },

    clearErrors: () => {
      set({ bettingError: null });
    },

    reset: () => {
      set(initialState);
    },
  }))
);

// Selectors
export const useSportsSelectors = () => {
  const store = useSportsStore();
  
  return {
    // Computed values
    totalOpportunities: store.bettingOpportunities.length,
    positiveEvOpportunities: store.bettingOpportunities.filter(opp => opp.ev > 0).length,
    highConfidenceOpportunities: store.bettingOpportunities.filter(opp => opp.confidence > 0.8).length,
    totalArbitrageOpportunities: store.arbitrageOpportunities.length,
    totalLiveOpportunities: store.liveBettingOpportunities.length,
    
    // Status checks
    hasOpportunities: store.bettingOpportunities.length > 0,
    hasErrors: !!store.bettingError,
    isLoading: store.bettingLoading,
    
    // Filtered data
    highValueOpportunities: store.bettingOpportunities.filter(opp => opp.ev > 5),
    recentOpportunities: store.bettingOpportunities
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 10),
  };
};