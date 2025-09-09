export interface ToolbarParams {
  bankroll: number;
  winPercentage: number; // Store as percentage (0-100)
  fractionalKelly: number;
  selectedLeague: string;
  selectedDate: string; // YYYY-MM-DD format
  selectedTeam?: string;
}

export interface GameLine {
  id: string;
  team: string;
  side: 'home' | 'away';
  odds_american: number;
  implied_probability: number;
  kelly_percentage?: number;
  recommended_stake?: number;
  edge?: number;
  loading?: boolean;
  error?: string | null;
}

export interface GameData {
  id: string;
  league: string;
  away_team: string;
  home_team: string;
  game_date: string;
  status: string;
  venue?: string;
  moneylines: GameLine[];
}

export const DEFAULT_TOOLBAR_PARAMS: ToolbarParams = {
  bankroll: 4000,
  winPercentage: 55,
  fractionalKelly: 0.5,
  selectedLeague: 'NCAAF',
  selectedDate: new Date().toISOString().split('T')[0], // Today in YYYY-MM-DD
};

export const FRACTIONAL_KELLY_OPTIONS = [
  { value: 0.25, label: '25% Kelly' },
  { value: 0.5, label: '50% Kelly' },
  { value: 1.0, label: '100% Kelly' },
];

export const STORAGE_KEYS = {
  SPORTS_TOOLBAR_PARAMS: 'sports-toolbar-params',
} as const;