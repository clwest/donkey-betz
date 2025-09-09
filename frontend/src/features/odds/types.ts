export interface OddsRow {
  id: string;
  book: string;
  market: string;
  american: number | string;
  decimal?: number;
  implied?: number;
  ev?: number;
  kelly?: number;
  stake?: number;
  notes?: string[];
  loading?: boolean;
  error?: string | null;
}

export interface ToolbarParams {
  bankroll: number;
  winProbability: number; // Store as 0-1 internally
  fractionalKelly: number;
}

export const DEFAULT_TOOLBAR_PARAMS: ToolbarParams = {
  bankroll: 4000,
  winProbability: 0.58,
  fractionalKelly: 0.5,
};

export const FRACTIONAL_KELLY_OPTIONS = [
  { value: 0.25, label: '25% Kelly' },
  { value: 0.5, label: '50% Kelly' },  
  { value: 1.0, label: '100% Kelly' },
];

export const DEFAULT_ROWS: Omit<OddsRow, 'id'>[] = [
  { book: 'DraftKings', market: 'Team A ML', american: '+110' },
  { book: 'FanDuel', market: 'Team A ML', american: '+105' },
  { book: 'BetMGM', market: 'Team A ML', american: '+115' },
];

export const STORAGE_KEYS = {
  TOOLBAR_PARAMS: 'odds-toolbar-params',
  ROWS_DATA: 'odds-rows-data',
} as const;