import { api } from '@/lib/api'
import type {
  RunSummary,
  RunDetail,
  ErrorSummaryResponse,
  MediaItem,
  DeliverableItem,
  OpsHealthOverview,
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

// --- Ops ---

export async function getHealthOverview() {
  const { data } = await api.get<OpsHealthOverview>('/v1/health/')
  return data
}

export async function getPlatformConfig() {
  const { data } = await api.get<PlatformConfigResponse>('/internal/config-snapshot/')
  return data
}
