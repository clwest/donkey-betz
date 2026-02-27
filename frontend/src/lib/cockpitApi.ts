import { api } from '@/lib/api'
import type {
  RunSummary,
  RunDetail,
  ErrorSummaryResponse,
  InboxResponse,
  OpsOverviewResponse,
  MediaItem,
  DeliverableItem,
  PaginatedResponse,
  AlertsResponse,
  RunbookResponse,
  RetryRunResponse,
  IncidentNoteResponse,
  ApprovalsResponse,
  ApprovalActionResponse,
  PlatformConfigResponse,
} from '@/types/cockpit'

// --- Runs ---

export interface RunsParams {
  status?: string
  agent?: string
  hours?: number
  limit?: number
}

export async function getRuns(params?: RunsParams) {
  const { data } = await api.get<RunSummary[]>('/cockpit/runs/', { params })
  return data
}

export async function getRunDetail(id: string) {
  const { data } = await api.get<RunDetail>(`/v1/agents/execution/${id}/`)
  return data
}

// --- Errors ---

export async function getErrorSummary(hours = 24) {
  const { data } = await api.get<ErrorSummaryResponse>('/cockpit/errors/', {
    params: { hours },
  })
  return data
}

// --- Inbox ---

export interface InboxParams {
  hours?: number
  limit?: number
}

export async function getInbox(params?: InboxParams) {
  const { data } = await api.get<InboxResponse>('/cockpit/inbox/', { params })
  return data
}

// --- Alerts ---

export interface AlertsParams {
  hours?: number
}

export async function getAlerts(params?: AlertsParams) {
  const { data } = await api.get<AlertsResponse>('/cockpit/alerts/', { params })
  return data
}

// --- Remediation ---

export async function getRunbook(alertKind: string) {
  const { data } = await api.get<RunbookResponse>(`/cockpit/remediate/runbook/${alertKind}/`)
  return data
}

export async function retryRun(runId: string) {
  const { data } = await api.post<RetryRunResponse>(`/cockpit/remediate/retry-run/${runId}/`)
  return data
}

export async function createIncidentNote(payload: { title: string; detail?: string; source_type?: string; source_id?: string }) {
  const { data } = await api.post<IncidentNoteResponse>('/cockpit/remediate/incident-note/', payload)
  return data
}

// --- Approvals ---

export interface ApprovalsParams {
  hours?: number
  limit?: number
}

export async function getApprovals(params?: ApprovalsParams) {
  const { data } = await api.get<ApprovalsResponse>('/cockpit/approvals/', { params })
  return data
}

export async function decideApproval(kind: 'decision' | 'gate', id: string, payload: Record<string, string>) {
  const path = kind === 'decision'
    ? `/cockpit/approvals/decision/${id}/decide/`
    : `/cockpit/approvals/gate/${id}/decide/`
  const { data } = await api.post<ApprovalActionResponse>(path, payload)
  return data
}

// --- Library: Deliverables ---

export interface DeliverableParams {
  q?: string
  type?: string
  days?: number
  limit?: number
  offset?: number
}

export async function getDeliverables(params?: DeliverableParams) {
  const { data } = await api.get<PaginatedResponse<DeliverableItem>>('/cockpit/library/deliverables/', { params })
  return data
}

// --- Library: Media ---

export interface MediaParams {
  media_type?: string
  days?: number
  limit?: number
  offset?: number
}

export async function getMedia(params?: MediaParams) {
  const { data } = await api.get<PaginatedResponse<MediaItem>>('/cockpit/library/media/', { params })
  return data
}

// --- Create ---

export interface CreateBlogPayload {
  topic: string
  style?: string
  length?: string
  citations?: boolean
}

export interface CreateTalkingVideoPayload {
  script: string
  voice?: string
  mode?: string
  sync_mode?: string
  lipsync_model?: string
  image_url?: string
  color_grade?: string
}

export interface CreateResponse {
  ok: boolean
  run_id?: string
  job_id?: string
  status: string
  created_at: string
  next: { route: string; poll_run_detail?: boolean }
}

export interface JobStatusResponse {
  job_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'unknown'
  progress: number | null
  error: string | null
}

export async function createBlog(payload: CreateBlogPayload) {
  const { data } = await api.post<CreateResponse>('/cockpit/create/blog/', payload)
  return data
}

export async function createTalkingVideo(payload: CreateTalkingVideoPayload) {
  const { data } = await api.post<CreateResponse>('/cockpit/create/talking-video/', payload)
  return data
}

export async function getJobStatus(jobId: string) {
  const { data } = await api.get<JobStatusResponse>(`/cockpit/create/status/${jobId}/`)
  return data
}

// --- Ops ---

export interface OpsParams {
  hours?: number
  limit?: number
}

export async function getOpsOverview(params?: OpsParams) {
  const { data } = await api.get<OpsOverviewResponse>('/cockpit/ops/overview/', { params })
  return data
}

export async function getPlatformConfig() {
  const { data } = await api.get<PlatformConfigResponse>('/internal/config-snapshot/')
  return data
}
