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
  AuditLogResponse,
  AgentFleetResponse,
  AgentDetailResponse,
  AgentActionResponse,
  QueuesOverviewResponse,
  CostOverviewResponse,
  AutopilotPoliciesResponse,
  AutopilotToggleResponse,
  AutopilotEvaluateResponse,
  AutopilotHistoryResponse,
  RunTraceResponse,
  ConfigOverviewResponse,
  ConfigToggleProviderResponse,
  ConfigFlagsResponse,
  ConfigUpsertFlagResponse,
  ConfigChangesResponse,
  IncidentListResponse,
  IncidentDetailResponse,
  IncidentCreateResponse,
  IncidentUpdateResponse,
  IncidentAddEventResponse,
  OpsRunListResponse,
  OpsRunDetailResponse,
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
  const { data } = await api.get(`/v1/agents/execution/${id}/`)
  // Backend wraps in {success, data: {execution: {...}}} — unwrap to flat RunDetail
  const exec = data?.data?.execution ?? data
  return exec as RunDetail
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

// --- Agent Fleet ---

export interface AgentFleetParams {
  q?: string
  hours?: number
  limit?: number
}

export async function getAgentFleet(params?: AgentFleetParams) {
  const { data } = await api.get<AgentFleetResponse>('/cockpit/agents/', { params })
  return data
}

export async function getAgentDetail(agentName: string) {
  const { data } = await api.get<AgentDetailResponse>(`/cockpit/agents/${agentName}/`)
  return data
}

export async function agentRunNow(agentName: string, payload?: { task?: string }) {
  const { data } = await api.post<AgentActionResponse>(`/cockpit/agents/${agentName}/run-now/`, payload ?? {})
  return data
}

export async function agentPause(agentName: string, payload?: { reason?: string }) {
  const { data } = await api.post<AgentActionResponse>(`/cockpit/agents/${agentName}/pause/`, payload ?? {})
  return data
}

export async function agentResume(agentName: string) {
  const { data } = await api.post<AgentActionResponse>(`/cockpit/agents/${agentName}/resume/`)
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
  // Session 1075: Media URLs from completed agent executions
  image_url?: string
  video_url?: string
  final_video_url?: string
  audio_url?: string
  file_url?: string
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

// --- Audit Log ---

export interface AuditLogParams {
  hours?: number
  limit?: number
  action?: string
}

export async function getAuditLog(params?: AuditLogParams) {
  const { data } = await api.get<AuditLogResponse>('/cockpit/audit/', { params })
  return data
}

// --- Queues ---

export type QueueWindow = '15m' | '60m' | '2h' | '6h' | '24h'

export async function getQueuesOverview(window: QueueWindow = '60m') {
  const { data } = await api.get<QueuesOverviewResponse>('/cockpit/queues/', { params: { window } })
  return data
}

// --- Cost ---

export interface CostParams {
  hours?: number
}

export async function getCostOverview(params?: CostParams) {
  const { data } = await api.get<CostOverviewResponse>('/cockpit/cost/', { params })
  return data
}

// --- Run Trace ---

export async function getRunTrace(runId: string) {
  const { data } = await api.get<RunTraceResponse>(`/cockpit/runs/${runId}/trace/`)
  return data
}

// --- Config Control Plane ---

export async function getConfigOverview() {
  const { data } = await api.get<ConfigOverviewResponse>('/cockpit/config/')
  return data
}

export async function toggleConfigProvider(providerId: string) {
  const { data } = await api.post<ConfigToggleProviderResponse>(`/cockpit/config/providers/${providerId}/toggle/`)
  return data
}

export async function getConfigFlags() {
  const { data } = await api.get<ConfigFlagsResponse>('/cockpit/config/flags/')
  return data
}

export async function upsertConfigFlag(payload: { key: string; value: unknown; description?: string; category?: string }) {
  const { data } = await api.post<ConfigUpsertFlagResponse>('/cockpit/config/flags/', payload)
  return data
}

export async function deleteConfigFlag(flagId: string) {
  const { data } = await api.post(`/cockpit/config/flags/${flagId}/delete/`)
  return data
}

export interface ConfigChangesParams {
  hours?: number
  limit?: number
}

export async function getConfigChanges(params?: ConfigChangesParams) {
  const { data } = await api.get<ConfigChangesResponse>('/cockpit/config/changes/', { params })
  return data
}

// --- Autopilot ---

export async function getAutopilotPolicies() {
  const { data } = await api.get<AutopilotPoliciesResponse>('/cockpit/autopilot/policies/')
  return data
}

export async function toggleAutopilotPolicy(policyId: string) {
  const { data } = await api.post<AutopilotToggleResponse>(`/cockpit/autopilot/policies/${policyId}/toggle/`)
  return data
}

export async function evaluateAutopilot(mode: 'dry_run' | 'execute' = 'dry_run') {
  const { data } = await api.post<AutopilotEvaluateResponse>('/cockpit/autopilot/evaluate/', { mode })
  return data
}

export interface AutopilotHistoryParams {
  hours?: number
  limit?: number
}

export async function getAutopilotHistory(params?: AutopilotHistoryParams) {
  const { data } = await api.get<AutopilotHistoryResponse>('/cockpit/autopilot/history/', { params })
  return data
}

// --- Incidents ---

export interface IncidentsParams {
  status?: string
  severity?: string
  q?: string
  limit?: number
  offset?: number
}

export async function getIncidents(params?: IncidentsParams) {
  const { data } = await api.get<IncidentListResponse>('/cockpit/incidents/', { params })
  return data
}

export async function createIncident(payload: { title: string; severity?: string; owner?: string; links?: { type: string; id: string; label?: string }[] }) {
  const { data } = await api.post<IncidentCreateResponse>('/cockpit/incidents/', payload)
  return data
}

export async function getIncidentDetail(incidentId: string) {
  const { data } = await api.get<IncidentDetailResponse>(`/cockpit/incidents/${incidentId}/`)
  return data
}

export async function updateIncident(incidentId: string, payload: { status?: string; severity?: string; owner?: string; resolution_summary?: string }) {
  const { data } = await api.post<IncidentUpdateResponse>(`/cockpit/incidents/${incidentId}/update/`, payload)
  return data
}

export async function addIncidentEvent(incidentId: string, payload: { event_type: 'note' | 'link'; text?: string; link_type?: string; link_id?: string; label?: string }) {
  const { data } = await api.post<IncidentAddEventResponse>(`/cockpit/incidents/${incidentId}/events/`, payload)
  return data
}

// --- Ops Runs ---

export interface OpsRunsParams {
  run_type?: string
  status?: string
  hours?: number
  limit?: number
}

export async function getOpsRuns(params?: OpsRunsParams) {
  const { data } = await api.get<OpsRunListResponse>('/cockpit/ops-runs/', { params })
  return data
}

export async function getOpsRunDetail(runId: string) {
  const { data } = await api.get<OpsRunDetailResponse>(`/cockpit/ops-runs/${runId}/`)
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
