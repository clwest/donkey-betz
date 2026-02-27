import { api } from '@/lib/api'
import type {
  RunSummary,
  RunDetail,
  ErrorSummaryResponse,
  InboxResponse,
  OpsOverviewResponse,
  MediaItem,
  DeliverableItem,
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

// --- Library: Media ---

export interface MediaParams {
  kind?: string
  limit?: number
  offset?: number
}

export async function getMedia(params?: MediaParams) {
  const { data } = await api.get<MediaItem[]>('/images/history/', { params })
  return data
}

// --- Library: Deliverables ---

export interface DeliverableParams {
  status?: string
  type?: string
  limit?: number
  offset?: number
}

export async function getDeliverables(params?: DeliverableParams) {
  const { data } = await api.get<DeliverableItem[]>('/deliverables/', { params })
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
