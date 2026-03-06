export type UUID = string
export type ISODateString = string

// --- Runs ---

export type RunStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

export type TriggerType = 'scheduled' | 'manual' | 'workflow' | 'autopilot' | 'retry' | 'unknown'
export type ImportanceLevel = 'action_required' | 'high_impact' | 'fyi' | 'routine'
export type NextActionType = 'review_deliverable' | 'approve_content' | 'preview_media' | 'investigate_failure' | 'retry_timeout' | 'fix_config' | 'rate_limited' | 'view_artifacts' | 'no_action'

export interface RunTrigger {
  type: TriggerType
  label: string
}

export interface RunImportance {
  level: ImportanceLevel
  reasons: string[]
}

export interface RunNextAction {
  type: NextActionType
  label: string
  href: string
  priority: 'primary' | 'secondary'
}

export interface RunArtifacts {
  deliverables: { id?: string; title?: string }[]
  blogs: { id?: string; title?: string }[]
  media: { id?: string; url?: string; media_type?: string }[]
  wagers: { id?: string }[]
  initiatives: { id?: string; name?: string }[]
}

export interface RunEnrichment {
  trigger: RunTrigger
  importance: RunImportance
  summary: string
  artifacts: RunArtifacts
  next_action: RunNextAction
}

export interface RunSummary {
  id: UUID
  agent_name: string
  task: string
  status: RunStatus
  created_at: ISODateString
  completed_at: ISODateString | null
  execution_time_ms: number | null
  tokens_used: number
  enrichment?: RunEnrichment
  cost?: number | string
  trace_id?: UUID | null
}

export interface RunDetail extends RunSummary {
  input_data: Record<string, unknown>
  output_data: Record<string, unknown>
  error_message: string
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

// --- Agent Fleet ---

export interface AgentFleetItem {
  id: UUID
  name: string
  agent_type: string
  specialization: string
  category: string
  effectiveness_score: number
  recent_total: number
  recent_completed: number
  recent_failed: number
  last_run_at: ISODateString | null
  cockpit_enabled: boolean
  paused_reason: string
  paused_at: ISODateString | null
}

export interface AgentFleetResponse {
  hours: number
  total: number
  items: AgentFleetItem[]
}

export interface AgentDetailResponse {
  ok: boolean
  agent: AgentFleetItem & {
    description: string
    total_executions: number
    successful_executions: number
  }
  recent_runs: RunSummary[]
}

export interface AgentActionResponse {
  ok: boolean
  agent_name: string
  enabled?: boolean
  task_id?: string
  status?: string
  paused_at?: ISODateString | null
  paused_reason?: string
  error?: string
}

// --- Queues ---

export interface QueueWorker {
  worker: string
  task_count: number
  failure_count: number
}

export interface QueueInfo {
  queue: string
  count: number
  failures: number
}

export interface QueueTask {
  task_name: string
  short_name: string
  count: number
  failures: number
  failure_rate: number
  avg_ms: number
}

export interface QueueFailure {
  task_id: string
  task_name: string
  short_name: string
  worker: string
  error_type: string
  error_message: string
  started_at: ISODateString | null
  queue: string
}

export interface QueuesOverviewResponse {
  window: string
  minutes: number
  generated_at: ISODateString
  summary: {
    workers_online: number
    tasks_total: number
    tasks_success: number
    tasks_failure: number
    tasks_started: number
    tasks_per_min: number
    failures_per_min: number
    avg_duration_ms: number
  }
  workers: QueueWorker[]
  queues: QueueInfo[]
  top_tasks: QueueTask[]
  recent_failures: QueueFailure[]
}

// --- Cost ---

export interface CostProviderRow {
  provider: string
  calls: number
  cost: number
  tokens: number
  avg_latency: number
  success_rate: number
}

export interface CostModelRow {
  model_id: string
  provider: string
  calls: number
  cost: number
  tokens: number
  avg_latency: number
}

export interface CostAgentRow {
  agent_name: string
  calls: number
  cost: number
  tokens: number
}

export interface CostOverviewResponse {
  hours: number
  generated_at: ISODateString
  overall: {
    total_calls: number
    successful: number
    total_cost: number
    total_tokens: number
    avg_latency_ms: number
    cost_delta_pct: number
    prev_cost: number
  }
  by_provider: CostProviderRow[]
  by_model: CostModelRow[]
  by_agent: CostAgentRow[]
}

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

// --- Run Trace ---

export interface TraceCeleryEvent {
  task_id: string
  task_name: string
  short_name: string
  queue: string
  worker: string
  status: string
  started_at: ISODateString | null
  finished_at: ISODateString | null
  duration_seconds: number | null
  rss_mb_start: number | null
  rss_mb_end: number | null
  rss_delta_mb: number | null
  error_type: string
  error_message: string
}

export interface TraceLLMCall {
  id: UUID
  provider: string
  model_id: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  cost: string
  latency_ms: number
  success: boolean
  error_type: string
  error_message: string
  created_at: ISODateString | null
}

export interface TraceAuditEntry {
  id: UUID
  actor: string
  action: string
  target_type: string
  created_at: ISODateString | null
}

export interface TraceTimelineEvent {
  type: 'run' | 'celery' | 'llm' | 'audit'
  subtype: string
  timestamp: string
  summary: string
  detail: string
}

export interface RunTraceResponse {
  run: RunDetail & { trace_id: UUID | null }
  celery_events: TraceCeleryEvent[]
  llm_calls: TraceLLMCall[]
  llm_summary: {
    total_calls: number
    total_cost: number
    total_tokens: number
    avg_latency_ms: number
  }
  audit_entries: TraceAuditEntry[]
  timeline: TraceTimelineEvent[]
}

// --- Config Control Plane ---

export interface ConfigProvider {
  id: UUID
  name: string
  display_name: string
  is_active: boolean
  is_available: boolean
  supports_tools: boolean
  supports_vision: boolean
  supports_streaming: boolean
  model_count: number
  last_health_check: ISODateString | null
}

export interface ConfigModel {
  id: UUID
  model_id: string
  provider: string
  is_active: boolean
}

export interface ConfigFlag {
  id: UUID
  key: string
  value: unknown
  description: string
  category: string
  is_sensitive: boolean
  updated_at: ISODateString | null
}

export interface ConfigOverviewResponse {
  providers: ConfigProvider[]
  models: ConfigModel[]
  flags: ConfigFlag[]
  env: {
    debug: boolean
    database: string
    redis: boolean
    celery_broker: boolean
    railway: boolean
  }
}

export interface ConfigToggleProviderResponse {
  ok: boolean
  provider: string
  is_active: boolean
}

export interface ConfigFlagsResponse {
  flags: ConfigFlag[]
}

export interface ConfigUpsertFlagResponse {
  ok: boolean
  id: UUID
  key: string
  value: unknown
  created: boolean
}

export interface ConfigChangeEntry {
  id: UUID
  actor: string
  action: string
  target_type: string
  target_id: string
  request_body: Record<string, unknown>
  response_summary: Record<string, unknown>
  created_at: ISODateString | null
}

export interface ConfigChangesResponse {
  hours: number
  total: number
  items: ConfigChangeEntry[]
}

// --- Autopilot ---

export interface AutopilotPolicy {
  id: UUID
  key: string
  label: string
  description: string
  enabled: boolean
  thresholds: Record<string, number>
  cooldown_minutes: number
  max_actions_per_run: number
  last_evaluated_at: ISODateString | null
  last_fired_at: ISODateString | null
}

export interface AutopilotPoliciesResponse {
  policies: AutopilotPolicy[]
}

export interface AutopilotToggleResponse {
  ok: boolean
  policy_id: string
  enabled: boolean
}

export interface AutopilotAction {
  policy_key: string
  proposed_action: string
  target_type: string
  target_id: string
  reason: string
  executed: boolean
  result: Record<string, unknown>
}

export interface AutopilotEvaluateResponse {
  ok: boolean
  mode: 'dry_run' | 'execute'
  actions: AutopilotAction[]
}

export interface AutopilotEvent {
  id: UUID
  policy_key: string
  mode: string
  proposed_action: string
  target_type: string
  target_id: string
  reason: string
  executed: boolean
  result: Record<string, unknown>
  created_at: ISODateString
}

export interface AutopilotHistoryResponse {
  total: number
  items: AutopilotEvent[]
}

// --- Incidents ---

export type IncidentStatus = 'open' | 'mitigating' | 'resolved'

export type IncidentEventType = 'note' | 'link' | 'status_change'

export interface IncidentSummary {
  id: UUID
  title: string
  severity: InboxSeverity
  status: IncidentStatus
  owner: string
  event_count: number
  link_count: number
  last_activity: ISODateString | null
  created_at: ISODateString
  updated_at: ISODateString
}

export interface IncidentListResponse {
  total: number
  offset: number
  limit: number
  items: IncidentSummary[]
}

export interface IncidentEvent {
  id: UUID
  event_type: IncidentEventType
  actor: string
  content: Record<string, unknown>
  created_at: ISODateString
}

export interface IncidentDetailResponse {
  ok: boolean
  incident: IncidentSummary & {
    resolution_summary: string
  }
  events: IncidentEvent[]
  event_count: number
}

export interface IncidentCreateResponse {
  ok: boolean
  id: UUID
  title: string
  severity: string
  status: string
  created_at: ISODateString
}

export interface IncidentUpdateResponse {
  ok: boolean
  id: UUID
  status: string
  severity: string
  owner: string
}

export interface IncidentAddEventResponse {
  ok: boolean
  id: UUID
  event_type: string
  content: Record<string, unknown>
  created_at: ISODateString
}

// --- Ops Runs ---

export type OpsRunType = 'ops_loop' | 'smoke_test' | 'deploy_verify' | 'manual'
export type OpsRunStatus = 'running' | 'passed' | 'failed' | 'partial'
export type OpsRunTrigger = 'beat' | 'pa_tool' | 'management_cmd' | 'manual'
export type OpsRunEventType = 'step_start' | 'step_pass' | 'step_fail' | 'info' | 'heartbeat'

export interface OpsRunSummary {
  id: UUID
  title: string
  run_type: OpsRunType
  status: OpsRunStatus
  triggered_by: OpsRunTrigger
  started_at: ISODateString
  finished_at: ISODateString | null
  event_count: number
  fail_count: number
  summary: Record<string, unknown>
}

export interface OpsRunListResponse {
  hours: number
  total: number
  items: OpsRunSummary[]
}

export interface OpsRunEvent {
  id: UUID
  event_type: OpsRunEventType
  label: string
  detail: Record<string, unknown>
  created_at: ISODateString
}

export interface OpsRunDetailResponse {
  ok: boolean
  run: OpsRunSummary
  events: OpsRunEvent[]
}

// --- Noise / North Star Metrics ---

export type NorthStarPath = 'revenue' | 'content' | 'sports' | 'none'

export interface NorthStarBucket {
  count: number
  pct: number
}

export interface RunsMetricsResponse {
  window_hours: number
  total_runs: number
  sampled: number
  by_agent: { agent_name: string; count: number }[]
  by_trigger_type: { trigger_type: string; count: number }[]
  by_importance_level: { level: string; count: number }[]
  by_next_action_type: { type: string; count: number }[]
  by_artifact_type: { type: string; count: number }[]
  north_star_coverage: Record<NorthStarPath, NorthStarBucket>
}

export interface ConversationMetricsResponse {
  window_hours: number
  total_conversations: number
  by_agent: { agent_name: string; count: number }[]
  by_type: { conversation_type: string; count: number }[]
  top_topics: { topic: string; count: number }[]
  zombie_rate: { zombies: number; total: number; pct: number }
}

export interface FocusModeStatus {
  enabled: boolean
  mode: 'gentle' | 'strict'
  objective_weights: Record<string, number>
  blocked_topics: string[]
  max_conversations_per_agent_per_hour: number
  max_total_conversations_per_hour: number
  require_north_star: boolean
  blocks_24h: number
}

// --- Ops ---

export interface PlatformConfigResponse {
  debug: boolean
  allowed_hosts: string[]
  installed_apps: string[]
  database_engine: string
  redis_url: string
  celery_broker: string
}
