import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const StockAlertSchema = z.object({
  id: z.string(),
  alert_type: z.string().default(''),
  symbol: z.string().default(''),
  company_name: z.string().default(''),
  sector: z.string().default(''),
  title: z.string().default(''),
  summary: z.string().default(''),
  bull_case: z.string().default(''),
  bear_case: z.string().default(''),
  confidence_score: z.number().default(0),
  bull_score: z.number().default(0),
  bear_score: z.number().default(0),
  current_price: z.number().nullable().default(null),
  price_change_24h: z.number().nullable().default(null),
  recommended_action: z.string().default(''),
  bookmarked: z.boolean().default(false),
  detected_at: z.string().nullable().default(null),
}).passthrough();

const PredictionSchema = z.object({
  id: z.string(),
  ticker: z.string().default(''),
  prediction_type: z.string().default(''),
  conviction_level: z.string().default(''),
  predicted_move: z.number().default(0),
  price_at_prediction: z.number().default(0),
  prediction_date: z.string().default(''),
  actual_move_7_days: z.number().nullable().default(null),
  was_correct_7_days: z.boolean().nullable().default(null),
}).passthrough();

const LatestBriefSchema = z.object({
  id: z.string(),
  brief_date: z.string().default(''),
  executive_summary: z.string().default(''),
  total_stocks_analyzed: z.number().default(0),
  debate_zone_count: z.number().default(0),
  situation_health: z.string().default(''),
}).passthrough();

const MarketNewsSchema = z.object({
  spider_name: z.string().default(''),
  source: z.string().default(''),
  title: z.string().default(''),
  description: z.string().default(''),
  link: z.string().default(''),
  published: z.string().nullable().default(null),
  category: z.string().default(''),
}).passthrough();

const StockHubSchema = z.object({
  success: z.boolean().default(true),
  stats: z.object({
    total_briefs: z.number().default(0),
    total_alerts: z.number().default(0),
    total_predictions: z.number().default(0),
    accuracy_7d: z.number().nullable().default(null),
    accuracy_30d: z.number().nullable().default(null),
    sec_filings_count: z.number().default(0),
  }).passthrough().default({ total_briefs: 0, total_alerts: 0, total_predictions: 0, accuracy_7d: null, accuracy_30d: null, sec_filings_count: 0 }),
  latest_brief: LatestBriefSchema.nullable().default(null),
  top_alerts: z.array(StockAlertSchema).default([]),
  top_predictions: z.array(PredictionSchema).default([]),
  market_news: z.array(MarketNewsSchema).default([]),
  sec_recent: z.array(z.object({
    title: z.string().default(''),
    description: z.string().default(''),
    link: z.string().default(''),
    published: z.string().nullable().default(null),
    filing_type: z.string().default(''),
  }).passthrough()).default([]),
}).passthrough();

const TickerLookupSchema = z.object({
  success: z.boolean().default(false),
  symbol: z.string().default(''),
  live_quote: z.object({
    company_name: z.string().default(''),
    current_price: z.number().default(0),
    change_percent: z.number().default(0),
    sector: z.string().default(''),
    industry: z.string().default(''),
  }).passthrough().nullable().default(null),
  alerts: z.object({ results: z.array(StockAlertSchema).default([]), total: z.number().default(0) }).default({ results: [], total: 0 }),
  predictions: z.object({ results: z.array(PredictionSchema).default([]), total: z.number().default(0) }).default({ results: [], total: 0 }),
}).passthrough();

// ── Exported Types ──────────────────────────────────────────────────────────

export type StockHub = z.infer<typeof StockHubSchema>;
export type StockAlert = z.infer<typeof StockAlertSchema>;
export type Prediction = z.infer<typeof PredictionSchema>;
export type TickerLookup = z.infer<typeof TickerLookupSchema>;

// ── Fallbacks ───────────────────────────────────────────────────────────────

const EMPTY_HUB: StockHub = {
  success: false,
  stats: { total_briefs: 0, total_alerts: 0, total_predictions: 0, accuracy_7d: null, accuracy_30d: null, sec_filings_count: 0 },
  latest_brief: null, top_alerts: [], top_predictions: [], market_news: [], sec_recent: [],
};

// ── Endpoints ───────────────────────────────────────────────────────────────

export async function getHub(): Promise<StockHub> {
  const { data } = await http.get('/stocks/hub/');
  return safeParse(StockHubSchema, data, {
    endpoint: '/stocks/hub/',
    fallback: EMPTY_HUB,
  });
}

export async function getAlerts(params?: {
  limit?: number;
  offset?: number;
  type?: string;
  symbol?: string;
}): Promise<{ alerts: StockAlert[]; total: number }> {
  const { data } = await http.get('/stocks/alerts/', { params });
  return {
    alerts: (data?.alerts ?? data?.results ?? []).map((a: unknown) =>
      safeParse(StockAlertSchema, a, { endpoint: '/stocks/alerts/', fallback: null as any }),
    ).filter(Boolean),
    total: data?.total ?? 0,
  };
}

export async function getPredictions(params?: {
  limit?: number;
  ticker?: string;
}): Promise<{ predictions: Prediction[]; total: number }> {
  const { data } = await http.get('/stocks/predictions/', { params });
  return {
    predictions: (data?.predictions ?? data?.results ?? []).map((p: unknown) =>
      safeParse(PredictionSchema, p, { endpoint: '/stocks/predictions/', fallback: null as any }),
    ).filter(Boolean),
    total: data?.total ?? 0,
  };
}

export async function lookupTicker(symbol: string): Promise<TickerLookup> {
  const { data } = await http.get(`/stocks/ticker/${symbol.toUpperCase()}/`);
  return safeParse(TickerLookupSchema, data, {
    endpoint: `/stocks/ticker/${symbol}/`,
    fallback: { success: false, symbol, live_quote: null, alerts: { results: [], total: 0 }, predictions: { results: [], total: 0 } },
  });
}

export async function getMarketNews(params?: {
  limit?: number;
  source?: string;
}): Promise<{ results: z.infer<typeof MarketNewsSchema>[]; total: number }> {
  const { data } = await http.get('/stocks/market-news/', { params });
  return {
    results: data?.results ?? [],
    total: data?.total ?? 0,
  };
}
