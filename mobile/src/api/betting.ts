import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const SportRecordSchema = z.object({
  wins: z.number().default(0),
  losses: z.number().default(0),
  profit: z.number().default(0),
}).passthrough();

const BettingStatsSchema = z.object({
  total_wagers: z.number().default(0),
  total_stake: z.number().default(0),
  total_profit_loss: z.number().default(0),
  wins: z.number().default(0),
  losses: z.number().default(0),
  pushes: z.number().default(0),
  pending: z.number().default(0),
  win_rate: z.number().default(0),
  roi: z.number().default(0),
  current_streak: z.number().default(0),
  longest_win_streak: z.number().default(0),
  longest_loss_streak: z.number().default(0),
  singles_record: SportRecordSchema.default({ wins: 0, losses: 0, profit: 0 }),
  parlays_record: SportRecordSchema.default({ wins: 0, losses: 0, profit: 0 }),
  stats_by_sport: z.record(z.string(), z.unknown()).default({}),
  last_updated: z.string().nullable().default(null),
}).passthrough();

const WagerLegSchema = z.object({
  event_id: z.string().default(''),
  sport: z.string().default(''),
  matchup: z.string().default(''),
  market_type: z.string().default(''),
  pick: z.string().default(''),
  odds: z.number().default(0),
  line: z.number().nullable().default(null),
  bookmaker: z.string().default(''),
  status: z.string().default(''),
  final_score: z.string().default(''),
}).passthrough();

const WagerSchema = z.object({
  id: z.string(),
  type: z.string().default('single'),
  bet_type: z.string().default(''),
  pick: z.string().default(''),
  odds: z.number().default(0),
  stake: z.number().default(0),
  potential_payout: z.number().default(0),
  status: z.string().default('pending'),
  profit_loss: z.number().nullable().default(null),
  result_amount: z.number().nullable().default(null),
  created_at: z.string().default(''),
  placed_at: z.string().default(''),
  settled_at: z.string().nullable().default(null),
  legs: z.array(WagerLegSchema).default([]),
  game_id: z.string().default(''),
  sport: z.string().default(''),
  matchup: z.string().default(''),
}).passthrough();

const GameSchema = z.object({
  event_id: z.string().default(''),
  sport_key: z.string().default(''),
  sport_name: z.string().default(''),
  commence_time: z.string().default(''),
  home_team: z.string().default(''),
  away_team: z.string().default(''),
  home_score: z.number().nullable().default(null),
  away_score: z.number().nullable().default(null),
  completed: z.boolean().default(false),
  predicted_winner: z.string().nullable().default(null),
  period: z.number().nullable().default(null),
  clock: z.string().nullable().default(null),
  status_detail: z.string().nullable().default(null),
}).passthrough();

const ArbitrageSchema = z.object({
  event: z.string().default(''),
  sport: z.string().default(''),
  profit_percent: z.number().default(0),
  bookmakers: z.array(z.object({
    name: z.string().default(''),
    odds: z.number().default(0),
    pick: z.string().default(''),
  }).passthrough()).default([]),
  expires_at: z.string().nullable().default(null),
}).passthrough();

const BriefSchema = z.object({
  brief: z.string().default(''),
  top_plays: z.array(z.unknown()).default([]),
}).passthrough();

const TrackRecordSchema = z.object({
  total_predictions: z.number().default(0),
  correct: z.number().default(0),
  incorrect: z.number().default(0),
  accuracy: z.number().default(0),
  by_sport: z.record(z.string(), z.unknown()).default({}),
}).passthrough();

// ── Exported Types ──────────────────────────────────────────────────────────

export type BettingStats = z.infer<typeof BettingStatsSchema>;
export type Wager = z.infer<typeof WagerSchema>;
export type Game = z.infer<typeof GameSchema>;
export type Arbitrage = z.infer<typeof ArbitrageSchema>;

// ── Fallbacks ───────────────────────────────────────────────────────────────

const EMPTY_STATS: BettingStats = {
  total_wagers: 0, total_stake: 0, total_profit_loss: 0,
  wins: 0, losses: 0, pushes: 0, pending: 0,
  win_rate: 0, roi: 0, current_streak: 0,
  longest_win_streak: 0, longest_loss_streak: 0,
  singles_record: { wins: 0, losses: 0, profit: 0 },
  parlays_record: { wins: 0, losses: 0, profit: 0 },
  stats_by_sport: {}, last_updated: null,
};

// ── Endpoints ───────────────────────────────────────────────────────────────

export async function getStats(): Promise<BettingStats> {
  const { data } = await http.get('/v1/betting/stats/');
  return safeParse(BettingStatsSchema, data, {
    endpoint: '/v1/betting/stats/',
    fallback: EMPTY_STATS,
  });
}

export async function getWagers(): Promise<Wager[]> {
  const { data } = await http.get('/v1/betting/wagers/');
  const raw = data?.wagers ?? data?.results ?? (Array.isArray(data) ? data : []);
  return raw.map((w: unknown) =>
    safeParse(WagerSchema, w, { endpoint: '/v1/betting/wagers/', fallback: null as any }),
  ).filter(Boolean);
}

export async function getRecentWagers(limit = 10): Promise<Wager[]> {
  const { data } = await http.get('/v1/betting/recent/', { params: { limit } });
  const raw = data?.wagers ?? data?.results ?? (Array.isArray(data) ? data : []);
  return raw.map((w: unknown) =>
    safeParse(WagerSchema, w, { endpoint: '/v1/betting/recent/', fallback: null as any }),
  ).filter(Boolean);
}

export async function getTodaysGames(sport?: string): Promise<Game[]> {
  const { data } = await http.get('/v1/betting/todays-games/', { params: sport ? { sport } : {} });
  const raw = data?.games ?? (Array.isArray(data) ? data : []);
  return raw.map((g: unknown) =>
    safeParse(GameSchema, g, { endpoint: '/v1/betting/todays-games/', fallback: null as any }),
  ).filter(Boolean);
}

export async function getBettingBrief(sport?: string): Promise<{ brief: string; top_plays: unknown[] }> {
  const { data } = await http.get('/v1/betting/brief/', { params: sport ? { sport } : {} });
  return safeParse(BriefSchema, data, {
    endpoint: '/v1/betting/brief/',
    fallback: { brief: '', top_plays: [] },
  });
}

export async function getArbitrage(): Promise<Arbitrage[]> {
  const { data } = await http.get('/v1/betting/arbitrage/scan/');
  const raw = data?.opportunities ?? (Array.isArray(data) ? data : []);
  return raw.map((a: unknown) =>
    safeParse(ArbitrageSchema, a, { endpoint: '/v1/betting/arbitrage/scan/', fallback: null as any }),
  ).filter(Boolean);
}

export async function getSharpAction(sport?: string): Promise<unknown> {
  const { data } = await http.get('/v1/betting/sharp-action/', { params: sport ? { sport } : {} });
  return data;
}

export async function getTrackRecord(params?: { sport?: string; days?: number }): Promise<z.infer<typeof TrackRecordSchema>> {
  const { data } = await http.get('/v1/betting/track-record/', { params });
  return safeParse(TrackRecordSchema, data, {
    endpoint: '/v1/betting/track-record/',
    fallback: { total_predictions: 0, correct: 0, incorrect: 0, accuracy: 0, by_sport: {} },
  });
}

export async function placeBet(payload: {
  game_id: string;
  bet_type: string;
  pick: string;
  odds: number;
  stake: number;
}): Promise<{ success: boolean; wager?: Wager; message?: string }> {
  const { data } = await http.post('/v1/betting/place/', payload);
  return data;
}

export async function getBankrollStats(): Promise<Record<string, unknown>> {
  const { data } = await http.get('/v1/odds/bankroll/stats/');
  return data;
}

export async function getLiveOdds(): Promise<Game[]> {
  const { data } = await http.get('/v1/sports/live-odds-scores/');
  const raw = data?.games ?? (Array.isArray(data) ? data : []);
  return raw.map((g: unknown) =>
    safeParse(GameSchema, g, { endpoint: '/v1/sports/live-odds-scores/', fallback: null as any }),
  ).filter(Boolean);
}
