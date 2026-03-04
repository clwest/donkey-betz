import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Zod Schemas ─────────────────────────────────────────────────────────────

const WorkspaceSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().default(''),
  workspace_type: z.string().default(''),
  root_path: z.string().default(''),
  is_active: z.boolean().default(false),
  tech_stack: z.record(z.string(), z.unknown()).default({}),
  current_branch: z.string().default(''),
  total_operations: z.number().default(0),
  total_files_written: z.number().default(0),
  total_commits: z.number().default(0),
  last_operation_at: z.string().nullable().default(null),
  created_at: z.string().default(''),
  context_summary: z.string().nullable().default(null),
});

const WorkspaceOperationSchema = z.object({
  id: z.string(),
  workspace: z.string().default(''),
  workspace_name: z.string().default(''),
  agent_name: z.string().default(''),
  agent_task: z.string().default(''),
  operation_type: z.string().default(''),
  file_path: z.string().default(''),
  success: z.boolean().default(true),
  error_message: z.string().default(''),
  execution_time_ms: z.number().default(0),
  requires_review: z.boolean().default(false),
  reviewed_by_human: z.boolean().default(false),
  human_approved: z.boolean().nullable().default(null),
  can_rollback: z.boolean().default(false),
  rolled_back: z.boolean().default(false),
  created_at: z.string().default(''),
});

const PaginatedWorkspacesSchema = z.object({
  count: z.number(),
  next: z.string().nullable().default(null),
  previous: z.string().nullable().default(null),
  results: z.array(WorkspaceSchema),
});

const PaginatedOperationsSchema = z.object({
  count: z.number(),
  next: z.string().nullable().default(null),
  previous: z.string().nullable().default(null),
  results: z.array(WorkspaceOperationSchema),
});

// ── Exported Types ──────────────────────────────────────────────────────────

export type Workspace = z.infer<typeof WorkspaceSchema>;
export type WorkspaceOperation = z.infer<typeof WorkspaceOperationSchema>;
export type PaginatedResponse<T> = { count: number; next: string | null; previous: string | null; results: T[] };

// ── Fallbacks ───────────────────────────────────────────────────────────────

const EMPTY_PAGINATED: PaginatedResponse<any> = { count: 0, next: null, previous: null, results: [] };

// ── Endpoints ───────────────────────────────────────────────────────────────

export async function listWorkspaces(): Promise<PaginatedResponse<Workspace>> {
  const { data } = await http.get('/workspaces/');
  return safeParse(PaginatedWorkspacesSchema, data, {
    endpoint: '/workspaces/',
    fallback: EMPTY_PAGINATED,
  });
}

export async function listOperations(params?: {
  limit?: number;
  workspace?: string;
}): Promise<PaginatedResponse<WorkspaceOperation>> {
  const { data } = await http.get('/workspace-operations/', { params });
  return safeParse(PaginatedOperationsSchema, data, {
    endpoint: '/workspace-operations/',
    fallback: EMPTY_PAGINATED,
  });
}

export async function getPendingReviews(): Promise<PaginatedResponse<WorkspaceOperation>> {
  const { data } = await http.get<any>('/workspace-operations/pending-reviews/');
  // API returns { total, operations: [...] } instead of paginated format
  const normalized = data.operations
    ? { count: data.total ?? data.operations.length, next: null, previous: null, results: data.operations }
    : data;
  return safeParse(PaginatedOperationsSchema, normalized, {
    endpoint: '/workspace-operations/pending-reviews/',
    fallback: EMPTY_PAGINATED,
  });
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
