import http from './http';

// ── Types ────────────────────────────────────────────────────────────────────

export interface Workspace {
  id: string;
  name: string;
  description: string;
  workspace_type: string;
  root_path: string;
  is_active: boolean;
  tech_stack: Record<string, unknown>;
  current_branch: string;
  total_operations: number;
  total_files_written: number;
  total_commits: number;
  last_operation_at: string | null;
  created_at: string;
  context_summary: string | null;
}

export interface WorkspaceOperation {
  id: string;
  workspace: string;
  workspace_name: string;
  agent_name: string;
  agent_task: string;
  operation_type: string;
  file_path: string;
  success: boolean;
  error_message: string;
  execution_time_ms: number;
  requires_review: boolean;
  reviewed_by_human: boolean;
  human_approved: boolean | null;
  can_rollback: boolean;
  rolled_back: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ── Endpoints ────────────────────────────────────────────────────────────────

export async function listWorkspaces(): Promise<PaginatedResponse<Workspace>> {
  const { data } = await http.get<PaginatedResponse<Workspace>>('/workspaces/');
  return data;
}

export async function listOperations(params?: {
  limit?: number;
  workspace?: string;
}): Promise<PaginatedResponse<WorkspaceOperation>> {
  const { data } = await http.get<PaginatedResponse<WorkspaceOperation>>(
    '/workspace-operations/',
    { params },
  );
  return data;
}

export async function getPendingReviews(): Promise<PaginatedResponse<WorkspaceOperation>> {
  // API returns { total, operations: [...] } instead of paginated format
  const { data } = await http.get<any>('/workspace-operations/pending-reviews/');
  if (data.operations) {
    return { count: data.total ?? data.operations.length, next: null, previous: null, results: data.operations };
  }
  return data;
}

export async function reviewOperation(
  id: string,
  approved: boolean,
  feedback?: string,
): Promise<void> {
  await http.post(`/workspace-operations/${id}/review/`, {
    approved,
    feedback,
  });
}
