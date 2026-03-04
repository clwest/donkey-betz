import http from './http';

// ── Types ────────────────────────────────────────────────────────────────────

export interface BodySummary {
  overall_health: string;
  health_score: number;
  healthy_systems: number;
  total_systems: number;
  systems: Record<string, { status: string; emoji: string }>;
  alert_count: number;
}

export interface AttentionStats {
  total_items: number;
  pending_count: number;
  by_urgency: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  by_status: Record<string, number>;
  by_item_type: Record<string, number>;
}

export interface GovernanceStats {
  total_decisions: number;
  draft_count: number;
  approved_count: number;
  rejected_count: number;
  promoted_count: number;
  pending_review_count: number;
  by_impact_area: Record<string, number>;
  by_decision_type: Record<string, number>;
}

export interface Initiative {
  id: string;
  name: string;
  status: string;
  current_stage: string;
  progress: number;
  created_at: string;
}

export interface ActivityItem {
  type: string;
  icon: string;
  title: string;
  subtitle: string;
  timestamp: string;
}

export interface RecentActivity {
  activities: ActivityItem[];
  counts: Record<string, number>;
  total: number;
}

export interface DashboardStats {
  total_revenue: number;
  active_opportunities: number;
  success_rate: number;
  active_agents: number;
  spider_data_points: number;
  agent_executions_24h: number;
}

// ── Endpoints ────────────────────────────────────────────────────────────────

export async function getBodySummary(): Promise<BodySummary> {
  const { data } = await http.get<BodySummary>('/body/summary/');
  return data;
}

export async function getAttentionStats(): Promise<AttentionStats> {
  // API wraps payload in { success, stats: {...} }
  const { data } = await http.get<{ stats: AttentionStats } & AttentionStats>(
    '/human/attention/stats/',
  );
  return (data as any).stats ?? data;
}

export async function getGovernanceStats(): Promise<GovernanceStats> {
  // API returns { stats: { total, canonical, drafts, pending, ... } }
  const { data } = await http.get<any>('/boardroom/governance-stats/');
  const s = data.stats ?? data;
  return {
    total_decisions: s.total ?? 0,
    draft_count: s.drafts ?? 0,
    approved_count: s.canonical ?? 0,
    rejected_count: 0,
    promoted_count: s.human_promoted ?? 0,
    pending_review_count: s.pending ?? 0,
    by_impact_area: {},
    by_decision_type: {},
  };
}

export async function getInitiatives(): Promise<Initiative[]> {
  const { data } = await http.get<{ results?: Initiative[]; initiatives?: Initiative[] }>(
    '/initiatives/',
  );
  return data.results ?? data.initiatives ?? [];
}

export async function getRecentActivity(limit = 15): Promise<RecentActivity> {
  const { data } = await http.get<RecentActivity>('/recent-activity/', {
    params: { limit, hours: 72 },
  });
  return data;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await http.get<DashboardStats>('/dashboard/stats/');
  return data;
}
