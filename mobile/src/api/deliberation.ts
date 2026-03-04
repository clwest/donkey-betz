import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const RecentFailureSchema = z.object({
  id: z.string(),
  objective: z.string().default(''),
  failure_reason_code: z.string().default(''),
  failure_detail: z.string().default(''),
  created_at: z.string().nullable().default(null),
}).passthrough();

const FailureStatsSchema = z.object({
  hours: z.number().default(24),
  total_sessions: z.number().default(0),
  total_failed: z.number().default(0),
  total_failures: z.number().default(0),
  failure_rate: z.number().default(0),
  by_reason: z.record(z.string(), z.number()).default({}),
  recent_failures: z.array(RecentFailureSchema).default([]),
}).passthrough();

const BlogSchema = z.object({
  id: z.string(),
  title: z.string().default(''),
  status: z.string().default(''),
  publish_ready: z.boolean().default(false),
}).nullable().default(null);

const DeliberationSessionSchema = z.object({
  id: z.string(),
  session_type: z.string().default(''),
  status: z.string().default(''),
  objective: z.string().default(''),
  created_at: z.string().nullable().default(null),
  completed_at: z.string().nullable().default(null),
  trace_id: z.string().default(''),
  participant_count: z.number().default(0),
  turn_count: z.number().default(0),
  contract_count: z.number().default(0),
  failure_reason_code: z.string().default(''),
  failure_detail: z.string().default(''),
  blog: BlogSchema,
}).passthrough();

const SessionsListSchema = z.object({
  count: z.number().default(0),
  sessions: z.array(DeliberationSessionSchema).default([]),
});

const TurnSchema = z.object({
  turn_number: z.number(),
  agent_name: z.string().default(''),
  role: z.string().default(''),
  content: z.string().default(''),
  created_at: z.string().nullable().default(null),
}).passthrough();

const ContractSchema = z.object({
  contract_type: z.string().default(''),
  contract_data: z.record(z.string(), z.unknown()).default({}),
  created_at: z.string().nullable().default(null),
}).passthrough();

const SessionDetailSchema = z.object({
  id: z.string(),
  session_type: z.string().default(''),
  status: z.string().default(''),
  objective: z.string().default(''),
  participants: z.array(z.object({ name: z.string() }).passthrough()).default([]),
  evidence_pack: z.record(z.string(), z.unknown()).default({}),
  trace: z.record(z.string(), z.unknown()).default({}),
  trace_id: z.string().default(''),
  failure_reason_code: z.string().default(''),
  failure_detail: z.string().default(''),
  created_at: z.string().nullable().default(null),
  completed_at: z.string().nullable().default(null),
  turns: z.array(TurnSchema).default([]),
  contracts: z.array(ContractSchema).default([]),
}).passthrough();

// ── Exported Types ──────────────────────────────────────────────────────────

export type FailureStats = z.infer<typeof FailureStatsSchema>;
export type RecentFailure = z.infer<typeof RecentFailureSchema>;
export type DeliberationSession = z.infer<typeof DeliberationSessionSchema>;
export type SessionDetail = z.infer<typeof SessionDetailSchema>;

// ── Fallbacks ───────────────────────────────────────────────────────────────

const EMPTY_FAILURE_STATS: FailureStats = {
  hours: 24, total_sessions: 0, total_failed: 0, total_failures: 0,
  failure_rate: 0, by_reason: {}, recent_failures: [],
};

// ── Endpoints ───────────────────────────────────────────────────────────────

export async function getFailureStats(hours = 24): Promise<FailureStats> {
  const { data } = await http.get('/deliberation/failure-stats/', {
    params: { hours },
  });
  return safeParse(FailureStatsSchema, data, {
    endpoint: '/deliberation/failure-stats/',
    fallback: EMPTY_FAILURE_STATS,
  });
}

export async function listSessions(params?: {
  status?: string;
  limit?: number;
}): Promise<{ count: number; sessions: DeliberationSession[] }> {
  const { data } = await http.get('/deliberation/sessions/', { params });
  return safeParse(SessionsListSchema, data, {
    endpoint: '/deliberation/sessions/',
    fallback: { count: 0, sessions: [] },
  });
}

export async function getSession(id: string): Promise<SessionDetail> {
  const { data } = await http.get(`/deliberation/sessions/${id}/`);
  return safeParse(SessionDetailSchema, data, {
    endpoint: `/deliberation/sessions/${id}/`,
    fallback: { id, session_type: '', status: 'error', objective: 'Failed to load', participants: [], evidence_pack: {}, trace: {}, trace_id: '', failure_reason_code: '', failure_detail: '', created_at: null, completed_at: null, turns: [], contracts: [] },
  });
}
