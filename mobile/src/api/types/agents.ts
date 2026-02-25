// ── Agent System Types ───────────────────────────────────────────────────────
// Matches backend response shapes from core/views_agent_orchestration.py
// and core/views_agent_execution.py

// ── Agent list (GET /v1/agents/list/) ────────────────────────────────────────

export interface AgentListItem {
  id: string;
  name: string;
  display_name: string;
  description: string;
  specialization: string;
  agent_type: string;
  is_active: boolean;
  isActive: boolean;
  total_executions: number;
  successful_executions: number;
  success_rate: number; // 0–100
  effectiveness_score: number; // 0–100
  lastActive: string | null;
  created_at: string;
}

export interface AgentListResponse {
  count: number;
  total: number;
  agents: AgentListItem[];
}

// ── Agent executions (GET /v1/agents/unified-executions/) ────────────────────

export type ExecutionStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface AgentExecution {
  id: string;
  agent_name: string;
  task: string;
  task_summary: string;
  status: ExecutionStatus;
  output_data: Record<string, any> | null;
  error_message: string | null;
  tokens_used: number | null;
  cost: number | null;
  execution_time_ms: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface UnifiedExecutionsResponse {
  success: boolean;
  data: {
    executions: AgentExecution[];
    count: number;
    limit: number;
  };
}

// ── Execution detail (GET /v1/agents/execution/{id}/) ────────────────────────

export interface ExecutionDetailResponse {
  success: boolean;
  data: {
    execution: AgentExecution & {
      agent_display_name: string;
      input_data: Record<string, any> | null;
    };
    related_memory: {
      id: string;
      title: string;
      content: string;
      valence: string;
      memory_type: string;
      importance_score: number;
    } | null;
  };
}

// ── Agents by specialization (GET /v1/agents/by-specialization/) ─────────────

export type AgentsBySpecialization = Record<
  string,
  Array<{ id: string; name: string }>
>;

// ── Body summary (GET /body/summary/) ────────────────────────────────────────
// Already typed in dashboard — re-export-friendly shapes here

export interface BodySystemInfo {
  status: string;
  emoji: string;
  healthy: boolean;
}

export interface BodySummary {
  success: boolean;
  timestamp: string;
  overall_health: string;
  health_score: number;
  healthy_systems: number;
  total_systems: number;
  systems: Record<string, BodySystemInfo>;
  alert_count: number;
}
