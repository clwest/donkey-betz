import http from './http';

// ── Types ────────────────────────────────────────────────────────────────────

export interface Artifact {
  id: string;
  title: string;
  content: string;
  status: string;
  classified: boolean;
  composite_score: number;
  confidence_score: number;
  created_at: string;
  source_agent: string;
  conversation_id: string | null;
}

export interface ClassificationPayload {
  what_is_this: 'research_finding' | 'actionable_recommendation' | 'scope_change' | 'risk_flag' | 'informational';
  who_is_it_for: 'platform' | 'end_users' | 'founder' | 'agents' | 'public';
  data_allowed: 'public_only' | 'internal_ops' | 'api_data' | 'user_data' | 'all';
  phase_approved: 'research' | 'prototype' | 'pilot' | 'production' | 'none';
  auto_approve?: boolean;
}

export interface PilotGate {
  id: string;
  decision_id: string;
  status: 'not_started' | 'in_progress' | 'ready' | 'approved' | 'blocked' | 'waived';
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  checklist_progress: {
    total: number;
    completed: number;
    percentage: number;
  };
  created_at: string;
}

export interface GateDetail extends PilotGate {
  decision: {
    id: string;
    topic: string;
    decision_type: string;
  };
  checklist: {
    total: number;
    completed: number;
    percentage: number;
    items: Array<{
      id: string;
      item_type: string;
      title: string;
      description: string;
      status: 'pending' | 'completed' | 'blocked';
    }>;
  };
}

// ── Endpoints ────────────────────────────────────────────────────────────────

export async function listNeedsClassification(params?: {
  limit?: number;
}): Promise<{ artifacts: Artifact[]; count: number; total_unclassified: number }> {
  const { data } = await http.get('/artifacts/needs-classification/', { params });
  return data;
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
  return data;
}

export async function getGate(id: string): Promise<{ gate: GateDetail }> {
  const { data } = await http.get(`/pilot-gates/${id}/`);
  return data;
}
