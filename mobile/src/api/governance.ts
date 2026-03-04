import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const ArtifactSchema = z.object({
  id: z.string(),
  title: z.string().default(''),
  content: z.string().default(''),
  status: z.string().default(''),
  classified: z.boolean().default(false),
  composite_score: z.number().default(0),
  confidence_score: z.number().default(0),
  created_at: z.string().default(''),
  source_agent: z.string().default(''),
  conversation_id: z.string().nullable().default(null),
}).passthrough();

const NeedsClassificationSchema = z.object({
  artifacts: z.array(ArtifactSchema).default([]),
  count: z.number().default(0),
  total_unclassified: z.number().default(0),
});

const PilotGateSchema = z.object({
  id: z.string(),
  decision_id: z.string().default(''),
  status: z.string().default('not_started'),
  risk_level: z.string().default('low'),
  checklist_progress: z.object({
    total: z.number().default(0),
    completed: z.number().default(0),
    percentage: z.number().default(0),
  }).default({ total: 0, completed: 0, percentage: 0 }),
  created_at: z.string().default(''),
}).passthrough();

const GatesListSchema = z.object({
  gates: z.array(PilotGateSchema).default([]),
  total: z.number().default(0),
  by_status: z.record(z.string(), z.number()).default({}),
});

// ── Exported Types ──────────────────────────────────────────────────────────

export type Artifact = z.infer<typeof ArtifactSchema>;
export type PilotGate = z.infer<typeof PilotGateSchema>;

export interface ClassificationPayload {
  what_is_this: 'research_finding' | 'actionable_recommendation' | 'scope_change' | 'risk_flag' | 'informational';
  who_is_it_for: 'platform' | 'end_users' | 'founder' | 'agents' | 'public';
  data_allowed: 'public_only' | 'internal_ops' | 'api_data' | 'user_data' | 'all';
  phase_approved: 'research' | 'prototype' | 'pilot' | 'production' | 'none';
  auto_approve?: boolean;
}

export interface GateDetail extends PilotGate {
  decision: { id: string; topic: string; decision_type: string };
  checklist: {
    total: number;
    completed: number;
    percentage: number;
    items: Array<{ id: string; item_type: string; title: string; description: string; status: 'pending' | 'completed' | 'blocked' }>;
  };
}

// ── Endpoints ───────────────────────────────────────────────────────────────

export async function listNeedsClassification(params?: {
  limit?: number;
}): Promise<{ artifacts: Artifact[]; count: number; total_unclassified: number }> {
  const { data } = await http.get('/artifacts/needs-classification/', { params });
  return safeParse(NeedsClassificationSchema, data, {
    endpoint: '/artifacts/needs-classification/',
    fallback: { artifacts: [], count: 0, total_unclassified: 0 },
  });
}

export async function classifyArtifact(
  id: string,
  payload: ClassificationPayload,
): Promise<{ success: boolean; message: string }> {
  const { data } = await http.post(`/artifacts/${id}/classify/`, payload);
  return data;
}

export async function listGates(params?: {
  limit?: number;
  status?: string;
}): Promise<{ gates: PilotGate[]; total: number; by_status: Record<string, number> }> {
  const { data } = await http.get('/pilot-gates/', { params });
  return safeParse(GatesListSchema, data, {
    endpoint: '/pilot-gates/',
    fallback: { gates: [], total: 0, by_status: {} },
  });
}

export async function getGate(id: string): Promise<{ gate: GateDetail }> {
  const { data } = await http.get(`/pilot-gates/${id}/`);
  return data;
}
