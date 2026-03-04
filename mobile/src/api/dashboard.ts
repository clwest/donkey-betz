import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const BodySummarySchema = z.object({
  overall_health: z.string(),
  health_score: z.number(),
  healthy_systems: z.number(),
  total_systems: z.number(),
  systems: z.record(z.string(), z.object({ status: z.string(), emoji: z.string() }).passthrough()),
  alert_count: z.number().default(0),
});

const AttentionStatsSchema = z.object({
  total_items: z.number(),
  pending_count: z.number(),
  by_urgency: z.object({
    critical: z.number().default(0),
    high: z.number().default(0),
    medium: z.number().default(0),
    low: z.number().default(0),
  }),
  by_status: z.record(z.string(), z.number()).default({}),
  by_item_type: z.record(z.string(), z.number()).default({}),
});

const GovernanceStatsSchema = z.object({
  total_decisions: z.number(),
  draft_count: z.number(),
  approved_count: z.number(),
  rejected_count: z.number(),
  promoted_count: z.number(),
  pending_review_count: z.number(),
  by_impact_area: z.record(z.string(), z.number()).default({}),
  by_decision_type: z.record(z.string(), z.number()).default({}),
});

const InitiativeSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.string().default('UNKNOWN'),
  current_stage: z.string().default(''),
  progress: z.number().default(0),
  created_at: z.string().default(''),
});

const ActivityItemSchema = z.object({
  type: z.string().default(''),
  icon: z.string().default(''),
  title: z.string(),
  subtitle: z.string().default(''),
  timestamp: z.string(),
});

const RecentActivitySchema = z.object({
  activities: z.array(ActivityItemSchema).default([]),
  counts: z.record(z.string(), z.number()).default({}),
  total: z.number().default(0),
});

const DashboardStatsSchema = z.object({
  total_revenue: z.number().default(0),
  active_opportunities: z.number().default(0),
  success_rate: z.number().default(0),
  active_agents: z.number().default(0),
  spider_data_points: z.number().default(0),
  agent_executions_24h: z.number().default(0),
});

// ── Exported Types (inferred from schemas) ──────────────────────────────────

export type BodySummary = z.infer<typeof BodySummarySchema>;
export type AttentionStats = z.infer<typeof AttentionStatsSchema>;
export type GovernanceStats = z.infer<typeof GovernanceStatsSchema>;
export type Initiative = z.infer<typeof InitiativeSchema>;
export type ActivityItem = z.infer<typeof ActivityItemSchema>;
export type RecentActivity = z.infer<typeof RecentActivitySchema>;
export type DashboardStats = z.infer<typeof DashboardStatsSchema>;

// ── Fallbacks ───────────────────────────────────────────────────────────────

const EMPTY_ATTENTION: AttentionStats = {
  total_items: 0, pending_count: 0,
  by_urgency: { critical: 0, high: 0, medium: 0, low: 0 },
  by_status: {}, by_item_type: {},
};

const EMPTY_GOVERNANCE: GovernanceStats = {
  total_decisions: 0, draft_count: 0, approved_count: 0,
  rejected_count: 0, promoted_count: 0, pending_review_count: 0,
  by_impact_area: {}, by_decision_type: {},
};

const EMPTY_ACTIVITY: RecentActivity = { activities: [], counts: {}, total: 0 };

const EMPTY_STATS: DashboardStats = {
  total_revenue: 0, active_opportunities: 0, success_rate: 0,
  active_agents: 0, spider_data_points: 0, agent_executions_24h: 0,
};

// ── Endpoints ───────────────────────────────────────────────────────────────

export async function getBodySummary(): Promise<BodySummary | null> {
  const { data } = await http.get('/body/summary/');
  return safeParse(BodySummarySchema, data, {
    endpoint: '/body/summary/',
    fallback: null as any,
  });
}

export async function getAttentionStats(): Promise<AttentionStats> {
  const { data } = await http.get('/human/attention/stats/');
  // API wraps payload in { stats: {...} }
  const inner = data?.stats ?? data;
  return safeParse(AttentionStatsSchema, inner, {
    endpoint: '/human/attention/stats/',
    fallback: EMPTY_ATTENTION,
  });
}

export async function getGovernanceStats(): Promise<GovernanceStats> {
  const { data } = await http.get('/boardroom/governance-stats/');
  // API returns { stats: { total, canonical, drafts, pending, ... } }
  const s = data?.stats ?? data;
  const normalized = {
    total_decisions: s.total ?? 0,
    draft_count: s.drafts ?? 0,
    approved_count: s.canonical ?? 0,
    rejected_count: 0,
    promoted_count: s.human_promoted ?? 0,
    pending_review_count: s.pending ?? 0,
    by_impact_area: {},
    by_decision_type: {},
  };
  return safeParse(GovernanceStatsSchema, normalized, {
    endpoint: '/boardroom/governance-stats/',
    fallback: EMPTY_GOVERNANCE,
  });
}

export async function getInitiatives(): Promise<Initiative[]> {
  const { data } = await http.get('/initiatives/');
  const raw = data?.results ?? data?.initiatives ?? [];
  return z.array(InitiativeSchema).catch([]).parse(raw);
}

export async function getRecentActivity(limit = 15): Promise<RecentActivity> {
  const { data } = await http.get('/recent-activity/', {
    params: { limit, hours: 72 },
  });
  return safeParse(RecentActivitySchema, data, {
    endpoint: '/recent-activity/',
    fallback: EMPTY_ACTIVITY,
  });
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await http.get('/dashboard/stats/');
  return safeParse(DashboardStatsSchema, data, {
    endpoint: '/dashboard/stats/',
    fallback: EMPTY_STATS,
  });
}
