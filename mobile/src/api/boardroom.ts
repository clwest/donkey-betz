import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const AttentionItemSchema = z.object({
  id: z.string(),
  title: z.string().default(''),
  summary: z.string().default(''),
  urgency: z.enum(['critical', 'high', 'medium', 'low']).default('low'),
  status: z.string().default(''),
  item_type: z.string().default(''),
  source_type: z.string().default(''),
  source_agent: z.string().default(''),
  payload: z.record(z.string(), z.unknown()).default({}),
  priority_score: z.number().default(0),
  ml_recommendation: z.string().default(''),
  ml_confidence: z.number().default(0),
  decision: z.string().default(''),
  decision_feedback: z.string().default(''),
  decided_at: z.string().nullable().default(null),
  created_at: z.string().default(''),
  expires_at: z.string().nullable().default(null),
}).passthrough();

const AttentionListResponseSchema = z.object({
  success: z.boolean().default(true),
  items: z.array(AttentionItemSchema).default([]),
  count: z.number().default(0),
});

const AttentionDetailResponseSchema = z.object({
  success: z.boolean().default(true),
  item: AttentionItemSchema,
});

const DecisionSchema = z.object({
  id: z.string(),
  topic: z.string().default(''),
  decision_type: z.string().default(''),
  decision_type_display: z.string().default(''),
  impact_area: z.string().default(''),
  impact_area_display: z.string().default(''),
  key_insights: z.array(z.string()).default([]),
  recommended_stance: z.string().default(''),
  rationale: z.string().default(''),
  participants: z.array(z.string()).default([]),
  status: z.enum(['draft', 'review', 'canonical', 'rejected']).default('draft'),
  is_canonical: z.boolean().default(false),
  promoted_at: z.string().nullable().default(null),
  source_type: z.string().default(''),
  created_at: z.string().default(''),
  confidence_score: z.number().optional(),
}).passthrough();

const DecisionListResponseSchema = z.object({
  success: z.boolean().default(true),
  decisions: z.array(DecisionSchema).default([]),
  count: z.number().default(0),
  total: z.number().default(0),
  canonical_count: z.number().default(0),
});

const DecisionDetailResponseSchema = z.object({
  success: z.boolean().default(true),
  decision: DecisionSchema.extend({
    suggested_feature: z.string().default(''),
    rationale: z.string().default(''),
  }),
});

// ── Exported Types ──────────────────────────────────────────────────────────

export type AttentionItem = z.infer<typeof AttentionItemSchema>;
export type AttentionListResponse = z.infer<typeof AttentionListResponseSchema>;
export type AttentionDetailResponse = z.infer<typeof AttentionDetailResponseSchema>;
export type Decision = z.infer<typeof DecisionSchema>;
export type DecisionListResponse = z.infer<typeof DecisionListResponseSchema>;
export type DecisionDetailResponse = z.infer<typeof DecisionDetailResponseSchema>;

// ── Fallbacks ───────────────────────────────────────────────────────────────

const EMPTY_ATTENTION_LIST: AttentionListResponse = { success: false, items: [], count: 0 };
const EMPTY_DECISION_LIST: DecisionListResponse = { success: false, decisions: [], count: 0, total: 0, canonical_count: 0 };

// ── Attention endpoints ─────────────────────────────────────────────────────

export async function listAttention(params?: {
  limit?: number;
  urgency?: string;
  status?: string;
}): Promise<AttentionListResponse> {
  const { data } = await http.get('/human/attention/', { params });
  return safeParse(AttentionListResponseSchema, data, {
    endpoint: '/human/attention/',
    fallback: EMPTY_ATTENTION_LIST,
  });
}

export async function getAttention(id: string): Promise<AttentionDetailResponse> {
  const { data } = await http.get(`/human/attention/${id}/`);
  return safeParse(AttentionDetailResponseSchema, data, {
    endpoint: `/human/attention/${id}/`,
    fallback: { success: false, item: { id, title: 'Error loading', summary: '', urgency: 'low', status: '', item_type: '', source_type: '', source_agent: '', payload: {}, priority_score: 0, ml_recommendation: '', ml_confidence: 0, decision: '', decision_feedback: '', decided_at: null, created_at: '', expires_at: null } },
  });
}

export async function decideAttention(
  id: string,
  decision: string,
  feedback?: string,
): Promise<{ success: boolean; message: string }> {
  const { data } = await http.post(`/human/attention/${id}/decide/`, {
    decision,
    feedback,
  });
  return data;
}

export async function deferAttention(
  id: string,
  remindAt: string,
): Promise<{ success: boolean; message: string }> {
  const { data } = await http.post(`/human/attention/${id}/defer/`, {
    remind_at: remindAt,
  });
  return data;
}

// ── Decision endpoints ──────────────────────────────────────────────────────

export async function listDecisions(params?: {
  limit?: number;
  status?: string;
  decision_type?: string;
}): Promise<DecisionListResponse> {
  const { data } = await http.get('/boardroom/decisions/', { params });
  return safeParse(DecisionListResponseSchema, data, {
    endpoint: '/boardroom/decisions/',
    fallback: EMPTY_DECISION_LIST,
  });
}

export async function getDecision(id: string): Promise<DecisionDetailResponse> {
  const { data } = await http.get(`/decisions/${id}/`);
  return safeParse(DecisionDetailResponseSchema, data, {
    endpoint: `/decisions/${id}/`,
    fallback: { success: false, decision: { id, topic: 'Error loading', decision_type: '', decision_type_display: '', impact_area: '', impact_area_display: '', key_insights: [], recommended_stance: '', rationale: '', participants: [], status: 'draft', is_canonical: false, promoted_at: null, source_type: '', created_at: '', suggested_feature: '' } },
  });
}

export async function promoteDecision(
  id: string,
): Promise<{ success: boolean; message: string }> {
  const { data } = await http.post(`/boardroom/decisions/${id}/promote/`);
  return data;
}

export async function rejectDecision(
  id: string,
  reason?: string,
): Promise<{ success: boolean; message: string }> {
  const { data } = await http.post(`/boardroom/decisions/${id}/reject/`, { reason });
  return data;
}
