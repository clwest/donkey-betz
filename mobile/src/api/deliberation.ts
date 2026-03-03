import http from './http';

// ── Types ────────────────────────────────────────────────────────────────────

export interface FailureStats {
  hours: number;
  total_sessions: number;
  total_failed: number;
  failure_rate: number;
  by_reason: Record<string, number>;
  recent_failures: RecentFailure[];
}

export interface RecentFailure {
  id: string;
  objective: string;
  failure_reason_code: string;
  failure_detail: string;
  created_at: string | null;
}

export interface DeliberationSession {
  id: string;
  session_type: string;
  status: string;
  objective: string;
  created_at: string | null;
  completed_at: string | null;
  trace_id: string;
  participant_count: number;
  turn_count: number;
  contract_count: number;
  failure_reason_code: string;
  failure_detail: string;
  blog: {
    id: string;
    title: string;
    status: string;
    publish_ready: boolean;
  } | null;
}

export interface SessionDetail {
  id: string;
  session_type: string;
  status: string;
  objective: string;
  participants: Array<{ name: string; type?: string }>;
  evidence_pack: Record<string, unknown>;
  trace: Record<string, unknown>;
  trace_id: string;
  failure_reason_code: string;
  failure_detail: string;
  created_at: string | null;
  completed_at: string | null;
  turns: Array<{
    turn_number: number;
    agent_name: string;
    role: string;
    content: string;
    created_at: string | null;
  }>;
  contracts: Array<{
    contract_type: string;
    contract_data: Record<string, unknown>;
    created_at: string | null;
  }>;
}

// ── Endpoints ────────────────────────────────────────────────────────────────

export async function getFailureStats(hours = 24): Promise<FailureStats> {
  const { data } = await http.get<FailureStats>('/deliberation/failure-stats/', {
    params: { hours },
  });
  return data;
}

export async function listSessions(params?: {
  status?: string;
  limit?: number;
}): Promise<{ count: number; sessions: DeliberationSession[] }> {
  const { data } = await http.get('/deliberation/sessions/', { params });
  return data;
}

export async function getSession(id: string): Promise<SessionDetail> {
  const { data } = await http.get<SessionDetail>(`/deliberation/sessions/${id}/`);
  return data;
}
