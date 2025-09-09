import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { convertAmericanToDecimal, computeKelly } from '../features/odds/api/odds';
import type { OddsRow, ToolbarParams } from '../features/odds/types';

interface OddsState {
  // Odds calculation data
  rows: OddsRow[];
  params: ToolbarParams;
  
  // Loading states
  isCalculating: boolean;
  calculationErrors: Record<string, string>;
  
  // Actions
  updateRows: (rows: OddsRow[]) => void;
  updateParams: (params: ToolbarParams) => void;
  addRow: () => void;
  deleteRow: (rowId: string) => void;
  clearRows: () => void;
  calculateOdds: (rowId: string, american: number | string) => Promise<void>;
  recalculateAll: () => Promise<void>;
  
  // Utility actions
  reset: () => void;
}

const generateRowId = () => `odds-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

const initialState = {
  rows: [],
  params: {
    winProbability: 0.52,
    bankroll: 1000,
    fractionalKelly: 0.25
  },
  isCalculating: false,
  calculationErrors: {},
};

export const useOddsStore = create<OddsState>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,

    updateRows: (rows: OddsRow[]) => {
      set({ rows });
    },

    updateParams: (params: ToolbarParams) => {
      set({ params });
      // Avoid immediate recalculation to prevent infinite loops
      // Recalculation will be handled by component useEffect
    },

    addRow: () => {
      const { rows } = get();
      const newRow: OddsRow = {
        id: generateRowId(),
        book: '',
        market: '',
        american: '',
      };
      set({ rows: [...rows, newRow] });
    },

    deleteRow: (rowId: string) => {
      const { rows, calculationErrors } = get();
      const newErrors = { ...calculationErrors };
      delete newErrors[rowId];
      set({ 
        rows: rows.filter(row => row.id !== rowId),
        calculationErrors: newErrors
      });
    },

    clearRows: () => {
      set({ rows: [], calculationErrors: {} });
    },

    calculateOdds: async (rowId: string, american: number | string) => {
      const { rows, params, calculationErrors } = get();
      
      // Clear previous error for this row
      const newErrors = { ...calculationErrors };
      delete newErrors[rowId];
      set({ calculationErrors: newErrors });
      
      // Set loading state for this specific row
      const updatedRows = rows.map(row => 
        row.id === rowId 
          ? { ...row, loading: true, error: null }
          : row
      );
      set({ rows: updatedRows });

      try {
        // Get conversion data
        const conversion = await convertAmericanToDecimal(american);
        
        if (!conversion.success || !conversion.result) {
          throw new Error('Failed to convert odds');
        }

        // Get Kelly calculation
        const kelly = await computeKelly(
          american,
          params.winProbability,
          params.bankroll,
          params.fractionalKelly
        );

        if (!kelly.success || !kelly.result) {
          throw new Error('Failed to calculate Kelly criterion');
        }

        // Update row with calculated values
        const finalRows = rows.map(row => 
          row.id === rowId 
            ? {
                ...row,
                decimal: conversion.result!.decimal,
                implied: conversion.result!.implied_probability,
                ev: kelly.result!.edge * 100, // Convert edge to percentage for EV
                kelly: kelly.result!.kelly_percentage,
                stake: kelly.result!.recommended_stake,
                notes: kelly.result!.warnings,
                loading: false,
                error: null,
              }
            : row
        );
        set({ rows: finalRows });

      } catch (error: any) {
        const errorMessage = error instanceof Error ? error.message : 'Calculation failed';
        
        // Update row with error
        const errorRows = rows.map(row => 
          row.id === rowId 
            ? { ...row, loading: false, error: errorMessage }
            : row
        );
        set({ 
          rows: errorRows,
          calculationErrors: { ...calculationErrors, [rowId]: errorMessage }
        });
      }
    },

    recalculateAll: async () => {
      const { rows, calculateOdds } = get();
      set({ isCalculating: true });
      
      try {
        // Calculate each row that has valid American odds
        const calculations = rows
          .filter(row => row.american && row.american !== '')
          .map(row => calculateOdds(row.id, row.american));
        
        await Promise.all(calculations);
      } finally {
        set({ isCalculating: false });
      }
    },

    reset: () => {
      set(initialState);
    },
  }))
);

// Selectors - using zustand selectors to prevent infinite re-renders
export const useOddsSelectors = () => {
  const totalRows = useOddsStore(state => state.rows.length);
  const isCalculating = useOddsStore(state => state.isCalculating);
  const rows = useOddsStore(state => state.rows);
  const calculationErrors = useOddsStore(state => state.calculationErrors);
  
  const rowsWithLoading = rows.filter(row => row.loading);
  const isLoading = isCalculating || rowsWithLoading.length > 0;
  
  const positiveEvRows = rows.filter(row => (row.ev || 0) > 0).length;
  const totalRecommendedStakes = rows.reduce((sum, row) => 
    sum + (row.stake && (row.kelly || 0) >= 0 ? row.stake : 0), 0
  );
  const hasErrors = Object.keys(calculationErrors).length > 0;
  const validRows = rows.filter(row => row.american && row.american !== '');
  const errorRows = rows.filter(row => row.error);
  
  return {
    totalRows,
    positiveEvRows,
    totalRecommendedStakes,
    hasErrors,
    isLoading,
    validRows,
    errorRows,
  };
};