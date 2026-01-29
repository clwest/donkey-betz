// Session 825: Workspace types - centralized type definitions
// Extracted from WorkspacePage.tsx for modular architecture

export type WorkspaceTab =
  | 'command'
  | 'infrastructure'
  | 'orchestration'
  | 'content'
  | 'consciousness'
  | 'intelligence'
  | 'datasources'
  | 'governance'
  | 'initiatives'  // Session 847: Initiative Pipeline Dashboard
  | 'knowledge'
  | 'files'
  | 'operations'
  | 'triggers'  // Session 861B: WorkspaceTrigger autopilot queue
  | 'conceptforge'  // Session 865: ConceptForge Dossier Pipeline
  | 'career'  // Session 866: ATS Resume Optimizer
  | 'voices'  // Session 869: Voice Marketplace

// Sub-tab types for each main tab
export type InfrastructureSubTab = 'health' | 'integration' | 'services' | 'llm' | 'analytics' | 'billing'
export type OrchestrationSubTab = 'monitor' | 'workflows' | 'automation' | 'hivemind'
export type ConsciousnessSubTab = 'memory' | 'orchestra' | 'mood' | 'relationships' | 'capsules' | 'timetravel'
export type IntelligenceSubTab = 'reasoning' | 'safety' | 'collective'
export type DataSourcesSubTab = 'spiders' | 'feed' | 'learning'
export type ContentStudioSubTab = 'gallery' | 'channels' | 'blogs' | 'podcast' | 'distribution'

// Workspace context for project understanding
export interface WorkspaceContext {
  total_files: number
  total_directories: number
  total_lines_of_code: number
  file_type_counts: Record<string, number>
  file_tree: Record<string, string[]>
  key_files: Record<string, string>
  coding_patterns: Record<string, string>
  dependencies: Record<string, Record<string, string>>
  import_aliases: Record<string, string>
  directory_purposes: Record<string, string>
  last_scanned_at: string
  scan_duration_ms?: number
}

export interface Workspace {
  id: string
  name: string
  path: string
  description?: string
  is_active: boolean
  is_git_repo: boolean
  last_activity?: string
  stats?: {
    total_files: number
    total_lines_of_code: number
    operations_count: number
  }
  tech_stack?: Record<string, string>
  root_path?: string
  workspace_type?: string
  entry_points?: string[]
  context?: WorkspaceContext
}

export interface WorkspaceOperation {
  id: string
  operation_type: string
  file_path: string
  agent_name: string
  agent_task?: string  // Session 834: Task description for grouping related operations
  description?: string
  success: boolean
  pending_review: boolean
  created_at: string
  diff?: string
  content_before?: string
  content_after?: string
  // Session 855: API returns these field names
  file_content_before?: string
  file_content_after?: string
  workspace_name?: string
  error_message?: string
  execution_time_ms?: number
  agent_execution_time_ms?: number  // Session 855: Agent execution time from AgentExecution
  lines_changed?: number
  requires_review?: boolean
  reviewed_by_human?: boolean
  human_approved?: boolean | null
  can_rollback?: boolean
  rolled_back?: boolean
}

export interface FileNode {
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
  children?: FileNode[]
}

export interface ActionResult {
  type: 'success' | 'error'
  message: string
}

// Tab configuration
export interface TabConfig {
  id: WorkspaceTab
  label: string
  icon: React.ComponentType<{ size?: number; className?: string }>
  description?: string
}

// Sub-tab configuration
export interface SubTabConfig {
  id: string
  label: string
  icon?: React.ComponentType<{ size?: number; className?: string }>
}
