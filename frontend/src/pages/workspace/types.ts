// Session 825: Workspace types - centralized type definitions
// Extracted from WorkspacePage.tsx for modular architecture
// Session 971b: Updated for 9-tab model (from 18)
// Session 1035: Split into workspace-only + platform tabs

// Workspace-only tab IDs (5 tabs)
export type WorkspaceTab =
  | 'overview'
  | 'files'
  | 'operations'
  | 'git'
  | 'triggers'
  | 'launchpad'

// Platform tab IDs (8 tabs — moved from workspace)
export type PlatformTab =
  | 'command'
  | 'initiatives'
  | 'boardroom'
  | 'evaluation'
  | 'content'
  | 'system'
  | 'dataintel'
  | 'knowledge'
  | 'learning'

// Set of platform tab IDs for redirect detection
export const PLATFORM_TABS = new Set<string>([
  'command', 'initiatives', 'boardroom', 'evaluation', 'content',
  'system', 'dataintel', 'knowledge', 'learning',
])

// Legacy tab IDs that should redirect to platform
export const LEGACY_TO_PLATFORM: Record<string, PlatformTab> = {
  infrastructure: 'system',
  orchestration: 'system',
  datasources: 'dataintel',
  intelligence: 'dataintel',
  governance: 'boardroom',
  consciousness: 'knowledge',
  conceptforge: 'content',
  career: 'content',
  voices: 'content',
}

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
 * Session 1035: Normalize platform tab params (legacy or current).
 * Used by PlatformPage to handle old bookmarks.
 */
export function normalizePlatformTab(tab: string): PlatformTab {
  if (PLATFORM_TABS.has(tab)) return tab as PlatformTab
  const legacy = LEGACY_TO_PLATFORM[tab]
  if (legacy) return legacy
  return 'command'
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

// Platform tab configuration
export interface PlatformTabConfig {
  id: PlatformTab
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
