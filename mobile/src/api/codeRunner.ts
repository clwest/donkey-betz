import { z } from 'zod';
import http from './http';
import { safeParse } from './safeParse';

// ── Schemas ──────────────────────────────────────────────────────────────────

const RunResponseSchema = z.object({
  run_id: z.string(),
}).passthrough();

const StatusResponseSchema = z.object({
  run_id: z.string(),
  status: z.enum(['queued', 'running', 'completed', 'failed']),
  mode: z.enum(['dry_run', 'apply']),
  workspace: z.string(),
  started_at: z.string().nullable(),
  finished_at: z.string().nullable(),
  exit_code: z.number().nullable(),
  created_at: z.string(),
}).passthrough();

const LogsResponseSchema = z.object({
  run_id: z.string(),
  lines: z.array(z.string()),
  total_lines: z.number(),
  truncated: z.boolean(),
  status: z.string(),
}).passthrough();

// ── Types ────────────────────────────────────────────────────────────────────

export type RunResponse = z.infer<typeof RunResponseSchema>;
export type StatusResponse = z.infer<typeof StatusResponseSchema>;
export type LogsResponse = z.infer<typeof LogsResponseSchema>;

// ── Fallbacks ────────────────────────────────────────────────────────────────

const EMPTY_STATUS: StatusResponse = {
  run_id: '',
  status: 'failed',
  mode: 'dry_run',
  workspace: 'mobile',
  started_at: null,
  finished_at: null,
  exit_code: null,
  created_at: new Date().toISOString(),
};

const EMPTY_LOGS: LogsResponse = {
  run_id: '',
  lines: [],
  total_lines: 0,
  truncated: false,
  status: 'failed',
};

// ── API Functions ────────────────────────────────────────────────────────────

export async function startCodeRun(
  task: string,
  mode: 'dry_run' | 'apply',
): Promise<RunResponse> {
  const { data } = await http.post('/v1/code/run/', { task, mode });
  return safeParse(RunResponseSchema, data, {
    endpoint: '/v1/code/run/',
    fallback: { run_id: '' },
  });
}

export async function getCodeRunStatus(runId: string): Promise<StatusResponse> {
  const { data } = await http.get(`/v1/code/status/${runId}/`);
  return safeParse(StatusResponseSchema, data, {
    endpoint: `/v1/code/status/${runId}/`,
    fallback: EMPTY_STATUS,
  });
}

export async function getCodeRunLogs(runId: string): Promise<LogsResponse> {
  const { data } = await http.get(`/v1/code/logs/${runId}/`);
  return safeParse(LogsResponseSchema, data, {
    endpoint: `/v1/code/logs/${runId}/`,
    fallback: EMPTY_LOGS,
  });
}
