import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const PlatformSchema = z.object({
  id: z.string(),
  name: z.string().default(''),
  slug: z.string().default(''),
  description: z.string().default(''),
  status: z.string().default(''),
  connected: z.boolean().default(false),
}).passthrough();

const DistributionSchema = z.object({
  id: z.string(),
  title: z.string().default(''),
  content_type: z.string().default(''),
  status: z.string().default('draft'),
  platform: z.string().default(''),
  created_at: z.string().nullable().default(null),
}).passthrough();

const IntegrationSchema = z.object({
  id: z.string(),
  platform: z.string().default(''),
  status: z.enum(['active', 'inactive', 'error']).default('inactive'),
  last_sync: z.string().nullable().default(null),
  connected_at: z.string().nullable().default(null),
}).passthrough();

const RecommendationSchema = z.object({
  platform: z.object({
    id: z.string().default(''),
    name: z.string().default(''),
    type: z.string().default(''),
    commission: z.number().default(0),
  }).passthrough().nullable().default(null),
  recommendation_type: z.string().default(''),
  confidence_score: z.number().default(0),
  suggested_price: z.number().nullable().default(null),
  reasoning: z.string().default(''),
  estimated_revenue_potential: z.number().nullable().default(null),
}).passthrough();

const ComparisonSchema = z.object({
  platform: z.string().default(''),
  revenue: z.number().default(0),
  growth_percent: z.number().nullable().default(null),
  items_count: z.number().default(0),
}).passthrough();

const RevenueSchema = z.object({
  total: z.number().default(0),
  this_month: z.number().default(0),
  last_month: z.number().default(0),
  pending: z.number().default(0),
  by_platform: z.record(z.string(), z.number()).default({}),
}).passthrough();

const StatsSchema = z.object({
  total_revenue: z.number().default(0),
  platforms: z.number().default(0),
  connected: z.number().default(0),
  distributions: z.number().default(0),
}).passthrough();

// ── Exported Types ──────────────────────────────────────────────────────────

export type Platform = z.infer<typeof PlatformSchema>;
export type Distribution = z.infer<typeof DistributionSchema>;
export type Integration = z.infer<typeof IntegrationSchema>;
export type Recommendation = z.infer<typeof RecommendationSchema>;
export type PlatformComparison = z.infer<typeof ComparisonSchema>;
export type Revenue = z.infer<typeof RevenueSchema>;
export type PortfolioStats = z.infer<typeof StatsSchema>;

// ── Fallbacks ───────────────────────────────────────────────────────────────

const EMPTY_STATS: PortfolioStats = {
  total_revenue: 0, platforms: 0, connected: 0, distributions: 0,
};

const EMPTY_REVENUE: Revenue = {
  total: 0, this_month: 0, last_month: 0, pending: 0, by_platform: {},
};

// ── Endpoints ───────────────────────────────────────────────────────────────

export async function getStats(): Promise<PortfolioStats> {
  const { data } = await http.get('/distribution/stats/');
  return safeParse(StatsSchema, data, {
    endpoint: '/distribution/stats/',
    fallback: EMPTY_STATS,
  });
}

export async function getPlatforms(): Promise<Platform[]> {
  const { data } = await http.get('/distribution/platforms/');
  const raw = data?.platforms ?? (Array.isArray(data) ? data : []);
  return raw.map((p: unknown) =>
    safeParse(PlatformSchema, p, { endpoint: '/distribution/platforms/', fallback: null as any }),
  ).filter(Boolean);
}

export async function getContent(): Promise<Distribution[]> {
  const { data } = await http.get('/distribution/content/');
  const raw = data?.distributions ?? (Array.isArray(data) ? data : []);
  return raw.map((d: unknown) =>
    safeParse(DistributionSchema, d, { endpoint: '/distribution/content/', fallback: null as any }),
  ).filter(Boolean);
}

export async function getRevenueDashboard(): Promise<Revenue> {
  const { data } = await http.get('/distribution/revenue/dashboard/');
  return safeParse(RevenueSchema, data, {
    endpoint: '/distribution/revenue/dashboard/',
    fallback: EMPTY_REVENUE,
  });
}

export async function getRecommendations(): Promise<Recommendation[]> {
  const { data } = await http.get('/distribution/recommendations/');
  const raw = data?.recommendations ?? (Array.isArray(data) ? data : []);
  return raw.map((r: unknown) =>
    safeParse(RecommendationSchema, r, { endpoint: '/distribution/recommendations/', fallback: null as any }),
  ).filter(Boolean);
}

export async function getIntegrations(): Promise<Integration[]> {
  const { data } = await http.get('/distribution/integrations/');
  const raw = data?.integrations ?? (Array.isArray(data) ? data : []);
  return raw.map((i: unknown) =>
    safeParse(IntegrationSchema, i, { endpoint: '/distribution/integrations/', fallback: null as any }),
  ).filter(Boolean);
}

export async function comparePlatforms(): Promise<PlatformComparison[]> {
  const { data } = await http.get('/distribution/revenue/compare/');
  const raw = data?.platforms ?? (Array.isArray(data) ? data : []);
  return raw.map((c: unknown) =>
    safeParse(ComparisonSchema, c, { endpoint: '/distribution/revenue/compare/', fallback: null as any }),
  ).filter(Boolean);
}
