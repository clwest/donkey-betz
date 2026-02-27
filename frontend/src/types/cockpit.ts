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

// --- Library ---

export type LibraryItemKind = 'image' | 'video' | 'audio' | 'document'

export interface MediaItem {
  id: UUID
  kind: LibraryItemKind
  title: string
  url: string
  thumbnail_url?: string
  created_at: ISODateString
}

export interface DeliverableItem {
  id: UUID
  title: string
  deliverable_type: string
  status: string
  created_at: ISODateString
  file_url?: string
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
