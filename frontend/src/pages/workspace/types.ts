// Session 825: Workspace types - centralized type definitions
// Extracted from WorkspacePage.tsx for modular architecture
// Session 971b: Updated for 9-tab model (from 18)

// New canonical tab IDs (9 tabs)
export type WorkspaceTab =
  | 'command'
  | 'initiatives'
  | 'boardroom'
  | 'content'       // Session 971b: ContentStudio (absorbs conceptforge, voices, files in B2)
  | 'system'        // Session 971b: Merged Infra + Orchestration + Triggers
  | 'operations'
  | 'dataintel'     // Session 971b: Merged DataSources + Intelligence
  | 'knowledge'
  | 'learning'
  // Legacy tab IDs kept for normalizeWorkspaceTab() compatibility
  | 'infrastructure'
  | 'orchestration'
  | 'triggers'
  | 'datasources'
  | 'intelligence'
  | 'governance'
  | 'consciousness'
  | 'conceptforge'
  | 'career'
  | 'voices'
  | 'files'

// Sub-tab types for each main tab
export type InfrastructureSubTab = 'health' | 'integration' | 'services' | 'llm' | 'analytics' | 'billing'
export type OrchestrationSubTab = 'monitor' | 'workflows' | 'automation' | 'hivemind'
export type ConsciousnessSubTab = 'memory' | 'orchestra' | 'mood' | 'relationships' | 'capsules' | 'timetravel'
export type IntelligenceSubTab = 'reasoning' | 'safety' | 'collective'
export type DataSourcesSubTab = 'spiders' | 'feed' | 'learning'
export type ContentStudioSubTab = 'gallery' | 'channels' | 'blogs' | 'podcast' | 'distribution' | 'dossiers' | 'voices' | 'files' | 'campaigns' | 'deliverables'

// Session 971b: New merged tab sub-tab types
export type SystemSubTab = 'health' | 'integration' | 'services' | 'llm' | 'monitor' | 'workflows' | 'hivemind' | 'triggers' | 'toolcalls'
export type DataIntelSubTab = 'spiders' | 'feed' | 'learning' | 'reasoning' | 'collective' | 'safety'

/**
 * Session 971b: Normalize legacy tab params to new canonical IDs.
 * Old bookmarks like ?tab=infrastructure still work for 2-4 weeks.
 */
export function normalizeWorkspaceTab(tab: string): WorkspaceTab {
  const mapping: Record<string, WorkspaceTab> = {
    // New canonical IDs (pass through)
    command: 'command',
    initiatives: 'initiatives',
    boardroom: 'boardroom',
    content: 'content',
    system: 'system',
    operations: 'operations',
    dataintel: 'dataintel',
    knowledge: 'knowledge',
    learning: 'learning',

    // Legacy → new mappings
    infrastructure: 'system',
    orchestration: 'system',
    triggers: 'system',
    datasources: 'dataintel',
    intelligence: 'dataintel',
    governance: 'boardroom',       // Governance absorbed into Boardroom
    consciousness: 'knowledge',    // AI Mind → Knowledge (temporary until B2+)
    conceptforge: 'content',       // Dossiers → Content Studio
    career: 'content',             // Career → Content Studio (temporary)
    voices: 'content',             // Voices → Content Studio
    files: 'content',              // Files → Content Studio
  }

  return mapping[tab] || 'command'
}

/**
 * Session 971b: Map legacy tab to a default sub-tab in the new merged tab.
 * So ?tab=orchestration lands on the "monitor" sub-tab within System.
 */
export function legacyTabToSubTab(tab: string): string | undefined {
  const mapping: Record<string, string> = {
    infrastructure: 'health',
    orchestration: 'monitor',
    triggers: 'triggers',
    datasources: 'spiders',
    intelligence: 'reasoning',
    conceptforge: 'dossiers',
    voices: 'voices',
    files: 'files',
  }
  return mapping[tab]
}

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
