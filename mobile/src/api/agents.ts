import http from './http';
import type {
  AgentListResponse,
  AgentsBySpecialization,
  BodySummary,
  UnifiedExecutionsResponse,
} from './types/agents';

// ── List agents ──────────────────────────────────────────────────────────────

export async function listAgents(params?: {
  page?: number;
  page_size?: number;
  specialization?: string;
}): Promise<AgentListResponse> {
  const { data } = await http.get<AgentListResponse>('/v1/agents/list/', { params });
  return data;
}

// ── Agents by specialization ─────────────────────────────────────────────────

export async function getAgentsBySpecialization(): Promise<AgentsBySpecialization> {
  const { data } = await http.get<AgentsBySpecialization>('/v1/agents/by-specialization/');
  return data;
}

// ── Unified executions (all agents or filtered by name) ──────────────────────

export async function getExecutions(params?: {
  limit?: number;
  agent_name?: string;
  status?: string;
}): Promise<UnifiedExecutionsResponse> {
  const { data } = await http.get<UnifiedExecutionsResponse>(
    '/v1/agents/unified-executions/',
    { params },
  );
  return data;
}

// ── Body summary ─────────────────────────────────────────────────────────────

export async function getBodySummary(): Promise<BodySummary> {
  const { data } = await http.get<BodySummary>('/body/summary/');
  return data;
}
