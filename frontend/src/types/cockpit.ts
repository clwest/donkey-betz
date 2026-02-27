export type UUID = string
export type ISODateString = string

// --- Runs ---

export type RunStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

export interface RunSummary {
  id: UUID
  agent_name: string
  task: string
  status: RunStatus
  created_at: ISODateString
  completed_at: ISODateString | null
  execution_time_ms: number | null
  tokens_used: number
}

export interface RunDetail extends RunSummary {
  input_data: Record<string, unknown>
  output_data: Record<string, unknown>
  error_message: string
  cost: string
  trace_id: UUID | null
}

// --- Errors ---

export type FailureSourceType = 'agent' | 'celery'

export interface FailureSignatureSummary {
  signature: string
  source: FailureSourceType
  count: number
  last_seen: ISODateString
  sample_error: string
}

export interface ErrorSummaryResponse {
  hours: number
  total_failures: number
  signatures: FailureSignatureSummary[]
}

// --- Inbox ---

export type InboxItemType = 'decision' | 'gate' | 'error_signature' | 'failed_run'
export type InboxSeverity = 'critical' | 'high' | 'medium' | 'low'

export interface InboxItemCta {
  label: string
  route: string
}

export interface InboxItemSource {
  system: 'human_decisions' | 'gates' | 'errors' | 'runs'
  id: string
  status?: string
}

export interface InboxItem {
  id: string
  type: InboxItemType
  severity: InboxSeverity
  title: string
  subtitle?: string | null
  timestamp: ISODateString
  badges: string[]
  cta: InboxItemCta
  source: InboxItemSource
  preview?: { text?: string | null } | null
}

export interface InboxCounts {
  total: number
  decisions: number
  gates: number
  errors: number
  failed_runs: number
}

export interface InboxResponse {
  hours: number
  limit: number
  generated_at: ISODateString
  counts: InboxCounts
  items: InboxItem[]
}

// --- Alerts ---

export type AlertKind = 'error_spike' | 'agent_failure' | 'health' | 'approvals'
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low'

export interface AlertItem {
  id: string
  kind: AlertKind
  severity: AlertSeverity
  title: string
  detail: string
  created_at: ISODateString | null
}

export interface AlertsResponse {
  hours: number
  total: number
  items: AlertItem[]
}

// --- Remediation ---

export interface RunbookResponse {
  ok: boolean
  title: string
  steps: string[]
}

export interface RetryRunResponse {
  ok: boolean
  original_run_id: string
  new_task_id: string
  agent_name: string
  error?: string
}

export interface IncidentNoteResponse {
  ok: boolean
  id?: string
  title?: string
  slug?: string
  error?: string
}

// --- Approvals ---

export type ApprovalKind = 'decision' | 'gate'

export interface ApprovalItem {
  id: string
  kind: ApprovalKind
  title: string
  summary: string
  urgency: InboxSeverity
  status: string
  source_agent: string
  ml_recommendation: string
  created_at: ISODateString
}

export interface ApprovalsResponse {
  hours: number
  total: number
  items: ApprovalItem[]
}

export interface ApprovalActionResponse {
  ok: boolean
  id: string
  decision?: string
  action?: string
  status: string
  error?: string
}

// --- Library ---

export type LibraryItemKind = 'image' | 'video' | 'audio' | 'document'

export interface MediaItem {
  id: UUID
  kind: 'image' | 'video'
  title: string
  url: string
  thumbnail_url?: string
  sub_type: string
  prompt: string
  created_at: ISODateString
}

export interface DeliverableItem {
  id: UUID
  title: string
  deliverable_type: string
  category: string
  status: string
  agent_name: string
  quality_score: number
  is_saved: boolean
  created_at: ISODateString
}

export interface PaginatedResponse<T> {
  total: number
  offset: number
  limit: number
  items: T[]
}

// --- Create ---

export type RecipeId =
  | 'blog_post'
  | 'social_media'
  | 'legal_doc'
  | 'research_brief'
  | 'image'
  | 'video'

export interface CreateField {
  name: string
  label: string
  type: 'text' | 'textarea' | 'select'
  options?: string[]
  required?: boolean
}

export interface CreateRecipe {
  id: RecipeId
  label: string
  description: string
  icon: string
  fields: CreateField[]
}

// --- Audit Log ---

export interface AuditLogEntry {
  id: string
  actor: string
  action: string
  target_type: string
  target_id: string
  request_body: Record<string, unknown>
  response_summary: Record<string, unknown>
  ip_address: string | null
  created_at: ISODateString
}

export interface AuditLogResponse {
  hours: number
  total: number
  limit: number
  items: AuditLogEntry[]
}

// --- Ops ---

// --- Ops ---

export type HealthTone = 'green' | 'amber' | 'red' | 'gray'

export interface HealthCheck {
  key: string
  label: string
  tone: HealthTone
  status: string
  detail: string
}

export interface FailingAgent {
  agent_name: string
  failed_count: number
  total_count: number
  failure_rate: number
  last_failed_at: ISODateString | null
}

export interface OpsOverviewResponse {
  hours: number
  generated_at: ISODateString
  health: {
    overall_tone: HealthTone
    checks: HealthCheck[]
  }
  top_failing_agents: FailingAgent[]
  top_error_signatures: FailureSignatureSummary[]
  recent_failed_runs: RunSummary[]
}

export interface PlatformConfigResponse {
  debug: boolean
  allowed_hosts: string[]
  installed_apps: string[]
  database_engine: string
  redis_url: string
  celery_broker: string
}
