import http from './http';

// ── Types ────────────────────────────────────────────────────────────────────

export interface AttentionItem {
  id: string;
  title: string;
  summary: string;
  urgency: 'critical' | 'high' | 'medium' | 'low';
  status: string;
  item_type: string;
  source_type: string;
  source_agent: string;
  payload: Record<string, unknown>;
  priority_score: number;
  ml_recommendation: string;
  ml_confidence: number;
  decision: string;
  decision_feedback: string;
  decided_at: string | null;
  created_at: string;
  expires_at: string | null;
}

export interface AttentionListResponse {
  success: boolean;
  items: AttentionItem[];
  count: number;
}

export interface AttentionDetailResponse {
  success: boolean;
  item: AttentionItem;
}

export interface Decision {
  id: string;
  topic: string;
  decision_type: string;
  decision_type_display: string;
  impact_area: string;
  impact_area_display: string;
  key_insights: string[];
  recommended_stance: string;
  rationale: string;
  participants: string[];
  status: 'draft' | 'review' | 'canonical' | 'rejected';
  is_canonical: boolean;
  promoted_at: string | null;
  source_type: string;
  created_at: string;
  confidence_score?: number;
}

export interface DecisionListResponse {
  success: boolean;
  decisions: Decision[];
  count: number;
  total: number;
  canonical_count: number;
}

export interface DecisionDetailResponse {
  success: boolean;
  decision: Decision & {
    suggested_feature: string;
    rationale: string;
  };
}

// ── Attention endpoints ──────────────────────────────────────────────────────

export async function listAttention(params?: {
  limit?: number;
  urgency?: string;
  status?: string;
}): Promise<AttentionListResponse> {
  const { data } = await http.get<AttentionListResponse>('/human/attention/', { params });
  return data;
}

export async function getAttention(id: string): Promise<AttentionDetailResponse> {
  const { data } = await http.get<AttentionDetailResponse>(`/human/attention/${id}/`);
  return data;
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

// ── Decision endpoints ───────────────────────────────────────────────────────

export async function listDecisions(params?: {
  limit?: number;
  status?: string;
  decision_type?: string;
}): Promise<DecisionListResponse> {
  const { data } = await http.get<DecisionListResponse>('/boardroom/decisions/', { params });
  return data;
}

export async function getDecision(id: string): Promise<DecisionDetailResponse> {
  const { data } = await http.get<DecisionDetailResponse>(`/decisions/${id}/`);
  return data;
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
