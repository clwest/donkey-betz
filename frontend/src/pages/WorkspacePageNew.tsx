// Session 825: Slim WorkspacePage Orchestrator
// Session 1035: Refocused to workspace-only tabs (Overview, Files, Operations, Git, Triggers)
// System-wide tabs moved to PlatformPage (/platform)

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import {
  FolderOpen,
  RefreshCw,
  Loader2,
  X,
  XCircle,
  Wifi,
  WifiOff,
  History,
  Plus,
  GitBranch,
  FileText,
  Code,
  Terminal,
  ChevronRight,
  Zap,
  LayoutDashboard,
  FolderTree,
  Package,
  Target,
  Palette,
  ClipboardList,
  Server,
  Radio,
  BookOpen,
  Briefcase,
  Mic,
  Brain,
  Lightbulb,
  Megaphone,
  FlaskConical,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { workspaceApi, workspaceOperationsApi } from '@/lib/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useSystemEvents } from '@/hooks/useWebSocket'
import { useAuthStore } from '@/stores/authStore'
import { CompactBreadcrumb } from '@/components/Breadcrumb'
import SmartOutputRenderer from '@/components/SmartOutputRenderer'

// Import workspace tab components
import {
  WorkTab,
  OpsConsoleTab,
  WorkspaceOverviewTab,
  HomeTab,
  FilesTab,
  OperationsTab,
  GitTab,
  TriggersTab,
  LaunchpadTab,
  DeliverablesTab,
  InitiativesTab,
  ContentStudioTab,
  BoardroomTab,
  SystemTab,
  DataIntelTab,
  KnowledgeTab,
  VoiceMarketplaceTab,
  AIConsciousnessTab,
  ConceptForgeTab,
  CareerTab,
  LearningJourneyTab,
  CampaignTab,
  Stage3EvaluationTab,
  AppTab,
  hasApp,
} from './workspace/tabs'
import { Toast } from './workspace/components'
import type { Workspace, WorkspaceTab, ActionResult } from './workspace/types'
// PLATFORM_TABS/LEGACY_TO_PLATFORM no longer needed — platform merged into workspace
import { useWorkspaceTabTracking } from '@/hooks/usePageTracking'

// Session 1078: 5 primary tabs with sub-tabs (was 21 flat tabs)
interface SubTab { id: string; label: string; icon: React.ComponentType<{ size?: number; className?: string }> }
interface PrimaryTab { id: string; label: string; icon: React.ComponentType<{ size?: number; className?: string }>; subTabs?: SubTab[] }

const primaryTabs: PrimaryTab[] = [
  { id: 'home', label: 'Home', icon: LayoutDashboard },
  {
    id: 'work', label: 'Work', icon: Briefcase,
    subTabs: [
      { id: 'queue', label: 'Queue', icon: ClipboardList },
      { id: 'deliverables', label: 'Deliverables', icon: Package },
      { id: 'initiatives', label: 'Initiatives', icon: Target },
    ],
  },
  {
    id: 'build', label: 'Build', icon: Palette,
    subTabs: [
      { id: 'content', label: 'Content Studio', icon: Palette },
      { id: 'campaigns', label: 'Campaigns', icon: Megaphone },
      { id: 'voices', label: 'Voices', icon: Mic },
      { id: 'conceptforge', label: 'ConceptForge', icon: Lightbulb },
    ],
  },
  {
    id: 'intelligence', label: 'Intelligence', icon: Radio,
    subTabs: [
      { id: 'dataintel', label: 'Data & Intel', icon: Radio },
      { id: 'knowledge', label: 'Knowledge', icon: BookOpen },
      { id: 'consciousness', label: 'AI Mind', icon: Brain },
    ],
  },
  {
    id: 'system', label: 'System', icon: Server,
    subTabs: [
      { id: 'ops', label: 'Operations', icon: History },
      { id: 'boardroom', label: 'Governance', icon: ClipboardList },
      { id: 'triggers', label: 'Automations', icon: Zap },
      { id: 'evaluation', label: 'Quality', icon: FlaskConical },
      { id: 'files', label: 'Files', icon: FolderTree },
      { id: 'git', label: 'Git', icon: GitBranch },
    ],
  },
]

// All valid primary + sub tab IDs for URL validation
const validPrimaryIds = new Set([...primaryTabs.map(t => t.id), 'app'])
const allSubTabIds = new Map<string, string>() // sub-id → parent-id
primaryTabs.forEach(p => p.subTabs?.forEach(s => allSubTabIds.set(s.id, p.id)))

// Legacy URL mapping: old tab IDs → new primary + sub
const legacyTabMapping: Record<string, { primary: string; sub?: string }> = {
  overview: { primary: 'home' },
  work: { primary: 'work', sub: 'queue' },
  launchpad: { primary: 'work', sub: 'queue' },
  deliverables: { primary: 'work', sub: 'deliverables' },
  initiatives: { primary: 'work', sub: 'initiatives' },
  content: { primary: 'build', sub: 'content' },
  campaigns: { primary: 'build', sub: 'campaigns' },
  voices: { primary: 'build', sub: 'voices' },
  conceptforge: { primary: 'build', sub: 'conceptforge' },
  dataintel: { primary: 'intelligence', sub: 'dataintel' },
  knowledge: { primary: 'intelligence', sub: 'knowledge' },
  consciousness: { primary: 'intelligence', sub: 'consciousness' },
  boardroom: { primary: 'system', sub: 'boardroom' },
  operations: { primary: 'system', sub: 'ops' },
  triggers: { primary: 'system', sub: 'triggers' },
  evaluation: { primary: 'system', sub: 'evaluation' },
  files: { primary: 'system', sub: 'files' },
  git: { primary: 'system', sub: 'git' },
  learning: { primary: 'intelligence', sub: 'knowledge' },
  career: { primary: 'work', sub: 'queue' },
  system: { primary: 'system', sub: 'ops' },
  infrastructure: { primary: 'system', sub: 'ops' },
  orchestration: { primary: 'system', sub: 'ops' },
  datasources: { primary: 'intelligence', sub: 'dataintel' },
  intelligence: { primary: 'intelligence', sub: 'dataintel' },
  governance: { primary: 'system', sub: 'boardroom' },
  command: { primary: 'home' },
}

// Default sub-tab for each primary
const defaultSubTab: Record<string, string> = {
  work: 'queue',
  build: 'content',
  intelligence: 'dataintel',
  system: 'ops',
}

// Workspace Selector Modal
function WorkspaceSelectorModal({
  workspaces,
  onSelect,
  onClose,
  onCreateNew,
}: {
  workspaces: Workspace[]
  onSelect: (id: string) => void
  onClose: () => void
  onCreateNew: () => void
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-lg mx-4 max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <h3 className="text-lg font-semibold">Select Workspace</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>
        <div className="p-4 space-y-2 overflow-y-auto max-h-96">
          {workspaces.map((ws) => (
            <div
              key={ws.id}
              className={cn(
                'w-full p-3 rounded-lg transition-colors',
                ws.is_active
                  ? 'bg-primary-500/20 border border-primary-500/50'
                  : 'bg-dark-bg hover:bg-dark-border'
              )}
            >
              <div className="flex items-center justify-between">
                <button
                  onClick={() => { onSelect(ws.id); onClose() }}
                  className="flex items-center gap-2 text-left flex-1"
                >
                  <FolderOpen size={18} className={ws.is_active ? 'text-primary-400' : 'text-gray-400'} />
                  <div>
                    <span className="font-medium">{ws.name}</span>
                    <p className="text-xs text-gray-500">{ws.workspace_type === 'sandbox' ? 'Business Workspace' : ws.path}</p>
                  </div>
                </button>
                <div className="flex items-center gap-2">
                  {ws.is_active && (
                    <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">Active</span>
                  )}
                  <a
                    href={`/workspace/${ws.id}`}
                    onClick={(e) => { e.stopPropagation(); onClose() }}
                    className="text-xs px-2 py-1 rounded bg-blue-600/20 text-blue-300 hover:bg-blue-600/30 transition-colors"
                  >
                    Dashboard
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="p-4 border-t border-dark-border space-y-2">
          <button
            onClick={() => window.location.href = '/workspace/new'}
            className="btn btn-primary w-full flex items-center justify-center gap-2"
          >
            <Zap size={16} />
            Create Business Workspace
          </button>
          <button
            onClick={onCreateNew}
            className="btn w-full flex items-center justify-center gap-2 text-xs text-gray-400 hover:text-gray-300 bg-transparent hover:bg-dark-border border border-dark-border rounded-lg py-2"
          >
            <Plus size={14} />
            Register Git Repo
          </button>
        </div>
      </div>
    </div>
  )
}

// Register Workspace Modal (simplified)
function RegisterWorkspaceModal({
  onClose,
  onSubmit,
  isLoading,
}: {
  onClose: () => void
  onSubmit: (data: { path: string; name?: string; description?: string }) => void
  isLoading: boolean
}) {
  const [path, setPath] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (path.trim()) {
      onSubmit({ path: path.trim(), name: name.trim() || undefined, description: description.trim() || undefined })
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-lg mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <h3 className="text-lg font-semibold">Register New Workspace</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Project Path *</label>
            <input
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="/path/to/your/project"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Name (optional)</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Project"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description (optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief project description"
              rows={2}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none resize-none"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isLoading || !path.trim()} className="btn btn-primary flex-1 flex items-center justify-center gap-2">
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
              Register
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Session 835: Format file path to readable title
function formatFilePathTitle(filePath: string): { title: string; category: string; badge?: string } {
  if (!filePath) return { title: 'Operation', category: '' }

  const parts = filePath.split('/')
  const filename = parts.pop() || filePath
  const directory = parts.join(' > ')
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
    .replace(/ > /g, ' › ')

  // Get badge from extension
  let badge: string | undefined
  if (filename.endsWith('.md')) badge = 'MD'
  else if (filename.endsWith('.json')) badge = 'JSON'
  else if (filename.endsWith('.py')) badge = 'PY'
  else if (filename.endsWith('.ts') || filename.endsWith('.tsx')) badge = 'TS'

  // Format filename
  let name = filename
    .replace(/\.(md|json|py|ts|tsx|js|jsx|txt|yaml|yml)$/, '')
    .replace(/_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$/, '')
    .replace(/_\d{4}-\d{2}-\d{2}$/, '')

  const words = name.split(/[-_]/).map((word) => {
    if (word.toLowerCase() === 'ai') return 'AI'
    if (word.toLowerCase() === 'api') return 'API'
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  })

  // Find type word for "Type: Description" format
  const typeWords = ['plan', 'report', 'analysis', 'research', 'argument', 'workflow', 'campaign', 'strategy', 'audit', 'review', 'script', 'episode', 'outline', 'brief', 'content']

  let title = ''
  for (let i = 0; i < words.length; i++) {
    if (typeWords.includes(words[i].toLowerCase()) && i < words.length - 1) {
      title = `${words.slice(0, i + 1).join(' ')}: ${words.slice(i + 1).join(' ')}`
      break
    }
  }
  if (!title) title = words.join(' ')

  return { title, category: directory, badge }
}

// Operation Content Viewer Modal
function OperationContentModal({
  operationId,
  onClose,
}: {
  operationId: string
  onClose: () => void
}) {
  const [viewMode, setViewMode] = useState<'rendered' | 'diff'>('rendered')
  const [showRawPath, setShowRawPath] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['workspace-operation-detail', operationId],
    queryFn: async () => {
      const res = await workspaceOperationsApi.detail(operationId)
      return res.data
    },
    enabled: !!operationId,
  })

  const operation = data as any

  // Session 833: Check if this is a markdown file
  const isMarkdownFile = operation?.file_path?.endsWith('.md')

  // Session 835: Format title from file path
  const { title: formattedTitle, category, badge } = formatFilePathTitle(operation?.file_path || '')

  // Session 833: Extract actual content from diff (removes +/- prefix lines)
  const extractContentFromDiff = (diff: string): string => {
    if (!diff) return ''
    const lines = diff.split('\n')
    const contentLines: string[] = []

    for (const line of lines) {
      // Skip diff headers
      if (line.startsWith('---') || line.startsWith('+++') || line.startsWith('@@') || line.startsWith('diff --git')) {
        continue
      }
      // For added lines (new file), strip the + prefix
      if (line.startsWith('+')) {
        contentLines.push(line.slice(1))
      }
      // For context lines (no prefix), include as-is
      else if (!line.startsWith('-')) {
        contentLines.push(line)
      }
      // Skip removed lines (we want the final state)
    }

    return contentLines.join('\n')
  }

  // Get the content to display (prefer file_content_after, fallback to extracted from diff)
  const getMarkdownContent = (): string => {
    if (operation?.file_content_after) {
      return operation.file_content_after
    }
    if (operation?.diff) {
      return extractContentFromDiff(operation.diff)
    }
    return ''
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <FileText className="text-primary-400" size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">{formattedTitle || 'Operation Details'}</h3>
                {badge && (
                  <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400 font-mono">
                    {badge}
                  </span>
                )}
              </div>
              {operation && (
                <>
                  <p className="text-xs text-gray-400">
                    {category && <span className="text-gray-500">{category} • </span>}
                    {operation.operation_type} • {operation.agent_name}
                    {operation.workspace_name && (
                      <span className="text-primary-400"> • {operation.workspace_name}</span>
                    )}
                  </p>
                  {operation.file_path && (
                    <p className="text-xs text-gray-500 font-mono mt-0.5 truncate max-w-lg" title={operation.file_path}>
                      {operation.file_path}
                    </p>
                  )}
                </>
              )}
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-primary-400" size={32} />
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center py-12 text-center">
              <XCircle className="text-accent-red mb-4" size={48} />
              <p className="text-gray-400">Failed to load operation details</p>
            </div>
          )}

          {operation && (
            <>
              {/* File path - collapsible */}
              {operation.file_path && (
                <div className="card">
                  <button
                    onClick={() => setShowRawPath(!showRawPath)}
                    className="w-full text-sm font-medium text-gray-400 flex items-center gap-2 hover:text-gray-300 transition-colors"
                  >
                    <FileText size={14} />
                    <span>Full Path</span>
                    <ChevronRight
                      size={14}
                      className={cn('transition-transform', showRawPath && 'rotate-90')}
                    />
                  </button>
                  {showRawPath && (
                    <code className="block mt-2 text-xs text-primary-400 bg-dark-bg p-2 rounded break-all">
                      {operation.file_path}
                    </code>
                  )}
                </div>
              )}

              {/* Diff / Rendered Content */}
              {operation.diff && (
                <div className="card">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-400 flex items-center gap-2">
                      <Code size={14} />
                      {isMarkdownFile ? 'Content' : 'Changes (Diff)'}
                      {isMarkdownFile && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400">Markdown</span>
                      )}
                    </h4>
                    {isMarkdownFile && (
                      <div className="flex rounded-lg border border-dark-border overflow-hidden">
                        <button
                          onClick={() => setViewMode('rendered')}
                          className={cn(
                            'px-3 py-1 text-xs transition-colors',
                            viewMode === 'rendered'
                              ? 'bg-primary-500/20 text-primary-400'
                              : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
                          )}
                        >
                          Rendered
                        </button>
                        <button
                          onClick={() => setViewMode('diff')}
                          className={cn(
                            'px-3 py-1 text-xs transition-colors',
                            viewMode === 'diff'
                              ? 'bg-primary-500/20 text-primary-400'
                              : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
                          )}
                        >
                          Diff
                        </button>
                      </div>
                    )}
                  </div>
                  {isMarkdownFile && viewMode === 'rendered' ? (
                    <div className="prose prose-invert prose-dark prose-sm max-w-none bg-dark-bg p-4 rounded overflow-y-auto max-h-96">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {getMarkdownContent()}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <pre className="text-xs bg-dark-bg p-3 rounded overflow-x-auto max-h-64 overflow-y-auto font-mono whitespace-pre-wrap">
                      {operation.diff}
                    </pre>
                  )}
                </div>
              )}

              {/* File content after (for creates/updates) */}
              {operation.file_content_after && !operation.diff && (
                <div className="card">
                  <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Code size={14} />
                    File Content
                    {operation.file_path?.endsWith('.md') && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400">Markdown</span>
                    )}
                  </h4>
                  {operation.file_path?.endsWith('.md') ? (
                    <div className="prose prose-invert prose-dark prose-sm max-w-none bg-dark-bg p-4 rounded overflow-y-auto max-h-96">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {operation.file_content_after}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <pre className="text-xs bg-dark-bg p-3 rounded overflow-x-auto max-h-96 overflow-y-auto font-mono whitespace-pre-wrap">
                      {operation.file_content_after}
                    </pre>
                  )}
                </div>
              )}

              {/* Command output (for git/command operations) */}
              {operation.command_output && (
                <div className="card">
                  <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Terminal size={14} />
                    Command Output
                  </h4>
                  <pre className="text-xs bg-dark-bg p-3 rounded overflow-x-auto max-h-64 overflow-y-auto font-mono whitespace-pre-wrap">
                    {operation.command_output}
                  </pre>
                </div>
              )}

              {/* Command (if present) */}
              {operation.command && (
                <div className="card">
                  <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Terminal size={14} />
                    Command
                  </h4>
                  <code className="text-sm text-accent-amber">{operation.command}</code>
                </div>
              )}

              {/* Error message */}
              {operation.error_message && (
                <div className="card border-accent-red/30">
                  <h4 className="text-sm font-medium text-accent-red mb-2 flex items-center gap-2">
                    <XCircle size={14} />
                    Error
                  </h4>
                  <pre className="text-xs text-accent-red/80 whitespace-pre-wrap">
                    {operation.error_message}
                  </pre>
                </div>
              )}

              {/* Agent Output Data - rendered nicely */}
              {operation.output_data && (
                <div className="card">
                  <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                    <Sparkles size={14} />
                    Agent Output
                  </h4>
                  <div className="bg-dark-bg rounded p-3 overflow-hidden">
                    <SmartOutputRenderer
                      data={operation.output_data}
                      agentName={operation.agent_name}
                      maxHeight="max-h-96"
                      showRawToggle={true}
                    />
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="card">
                <h4 className="text-sm font-medium text-gray-400 mb-2">Metadata</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                  <div>
                    <span className="text-gray-500">Agent:</span>
                    <p className="font-medium">{operation.agent_name}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Type:</span>
                    <p className="font-medium">{operation.operation_type}</p>
                  </div>
                  {operation.agent_execution_time_ms ? (
                    <div>
                      <span className="text-gray-500">Agent Time:</span>
                      <p className="font-medium text-primary-400">{operation.agent_execution_time_ms}ms</p>
                    </div>
                  ) : (
                    <div>
                      <span className="text-gray-500">File Op Time:</span>
                      <p className="font-medium">{operation.execution_time_ms || 0}ms</p>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <p className={cn('font-medium', operation.success ? 'text-accent-green' : 'text-accent-red')}>
                      {operation.success ? 'Success' : 'Failed'}
                    </p>
                  </div>
                  {operation.lines_changed !== undefined && (
                    <div>
                      <span className="text-gray-500">Lines Changed:</span>
                      <p className="font-medium">{operation.lines_changed}</p>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-500">Created:</span>
                    <p className="font-medium">{new Date(operation.created_at).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-dark-border flex-shrink-0">
          <button onClick={onClose} className="btn btn-secondary w-full">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default function WorkspacePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const rawUrlTab = searchParams.get('tab') || ''
  const rawUrlSub = searchParams.get('sub') || ''

  // Session 1078: Resolve initial tab from URL (handles legacy + new format)
  function resolveFromUrl(tab: string, sub: string): { primary: string; sub: string } {
    // New format: ?tab=work&sub=deliverables
    if (validPrimaryIds.has(tab)) {
      const defSub = defaultSubTab[tab] || ''
      return { primary: tab, sub: sub || defSub }
    }
    // Legacy format: ?tab=deliverables → maps to work/deliverables
    const legacy = legacyTabMapping[tab]
    if (legacy) return { primary: legacy.primary, sub: legacy.sub || defaultSubTab[legacy.primary] || '' }
    // Fallback
    return { primary: 'home', sub: '' }
  }

  const initial = resolveFromUrl(rawUrlTab, rawUrlSub)
  const [activePrimary, setActivePrimary] = useState(initial.primary)
  const [activeSub, setActiveSub] = useState(initial.sub)

  // Redirect legacy URLs once
  useEffect(() => {
    if (rawUrlTab && !validPrimaryIds.has(rawUrlTab) && legacyTabMapping[rawUrlTab]) {
      const mapped = legacyTabMapping[rawUrlTab]
      const params: Record<string, string> = { tab: mapped.primary }
      if (mapped.sub) params.sub = mapped.sub
      setSearchParams(params, { replace: true })
    }
  }, [rawUrlTab, setSearchParams])

  useWorkspaceTabTracking(activePrimary as WorkspaceTab)

  const handleTabChange = (tab: WorkspaceTab | string) => {
    // Support both old-style calls (from child components) and new primary tab clicks
    const legacy = legacyTabMapping[tab]
    if (legacy) {
      setActivePrimary(legacy.primary)
      setActiveSub(legacy.sub || defaultSubTab[legacy.primary] || '')
      const params: Record<string, string> = { tab: legacy.primary }
      if (legacy.sub) params.sub = legacy.sub
      setSearchParams(params, { replace: true })
      return
    }
    if (validPrimaryIds.has(tab)) {
      setActivePrimary(tab)
      const defSub = defaultSubTab[tab] || ''
      setActiveSub(defSub)
      const params: Record<string, string> = { tab }
      if (defSub) params.sub = defSub
      setSearchParams(params, { replace: true })
      return
    }
    // Direct sub-tab ID
    const parent = allSubTabIds.get(tab)
    if (parent) {
      setActivePrimary(parent)
      setActiveSub(tab)
      setSearchParams({ tab: parent, sub: tab }, { replace: true })
    }
  }

  const handleSubTabChange = (sub: string) => {
    setActiveSub(sub)
    setSearchParams({ tab: activePrimary, sub }, { replace: true })
  }

  const currentPrimaryDef = primaryTabs.find(t => t.id === activePrimary)

  const [showWorkspaceSelector, setShowWorkspaceSelector] = useState(false)
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [viewingOperationId, setViewingOperationId] = useState<string | null>(null)

  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuthStore()

  // WebSocket for real-time updates
  const { status: wsStatus } = useSystemEvents({
    onFileModified: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-files'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
    },
    onAgentExecutionComplete: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
    },
  })

  // Core workspace queries
  const { data: workspacesData, isLoading: loadingWorkspaces, error: workspacesError } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => workspaceApi.list(),
    retry: false,
    enabled: isAuthenticated,
  })

  const { data: activeWorkspaceData } = useQuery({
    queryKey: ['workspace-active'],
    queryFn: () => workspaceApi.getActive(),
    retry: false,
    enabled: isAuthenticated,
  })

  const activeWorkspace = activeWorkspaceData?.data as Workspace | undefined
  const workspaces = (workspacesData?.data?.results || workspacesData?.data || []) as Workspace[]

  // Dynamically add App tab if workspace has an embedded app
  const showAppTab = activeWorkspace && hasApp(activeWorkspace.name)
  const effectiveTabs: PrimaryTab[] = showAppTab
    ? [{ id: 'app', label: 'Launch App', icon: Zap } as PrimaryTab, ...primaryTabs]
    : primaryTabs

  // Sync active workspace to global store (used by PA dock for chat context)
  const setGlobalWorkspace = useWorkspaceStore(s => s.setActiveWorkspace)
  useEffect(() => {
    if (activeWorkspace) {
      setGlobalWorkspace({
        id: activeWorkspace.id,
        name: activeWorkspace.name,
        workspace_type: activeWorkspace.workspace_type,
        git_remote_url: activeWorkspace.git_remote_url,
      })
    }
  }, [activeWorkspace?.id, activeWorkspace?.name, setGlobalWorkspace])

  // Mutations
  const activateMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-active'] })
      showSuccess('Workspace activated')
    },
    onError: () => showError('Failed to activate workspace'),
  })

  const registerMutation = useMutation({
    mutationFn: (data: { path: string; name?: string; description?: string }) =>
      workspaceApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      setShowRegisterModal(false)
      showSuccess('Workspace registered successfully!')
    },
    onError: (error: any) => {
      const message = error?.response?.data?.error || 'Failed to register workspace'
      showError(message)
    },
  })

  const scanMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.scan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-stats'] })
      showSuccess('Workspace scanned')
    },
    onError: () => showError('Failed to scan workspace'),
  })

  // Helper functions
  const showSuccess = (message: string) => setActionResult({ type: 'success', message })
  const showError = (message: string) => setActionResult({ type: 'error', message })

  // Clear toast
  useEffect(() => {
    if (actionResult) {
      const timer = setTimeout(() => setActionResult(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [actionResult])

  // Loading state
  if (loadingWorkspaces) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  // Error state
  if (workspacesError) {
    const isAuthError =
      (workspacesError as { response?: { status?: number } })?.response?.status === 401 ||
      (workspacesError as { response?: { status?: number } })?.response?.status === 403

    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <div className="h-16 w-16 rounded-full bg-accent-red/20 flex items-center justify-center">
          <XCircle size={32} className="text-accent-red" />
        </div>
        <h2 className="text-xl font-semibold">
          {isAuthError ? 'Authentication Required' : 'Failed to Load Workspaces'}
        </h2>
        <p className="text-gray-400 text-center max-w-md">
          {isAuthError
            ? 'Please log in to access the Workspace Manager.'
            : 'Unable to connect to the Workspace API.'}
        </p>
        {isAuthError && (
          <a href="/login" className="btn btn-primary">
            Go to Login
          </a>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <CompactBreadcrumb currentPage="Workspace" className="mb-2" />
          <h1 className="text-2xl font-bold">Workspace</h1>
          <p className="text-sm text-gray-400 mt-1">Project workspace — files, operations, git, triggers</p>
        </div>
        <div className="flex items-center gap-3">
          {/* WebSocket status */}
          <div
            className={cn(
              'flex items-center gap-1.5 px-2 py-1 rounded text-xs',
              wsStatus === 'connected'
                ? 'bg-accent-green/10 text-accent-green'
                : wsStatus === 'connecting'
                ? 'bg-accent-amber/10 text-accent-amber'
                : 'bg-gray-500/10 text-gray-500'
            )}
            title={`WebSocket: ${wsStatus}`}
          >
            {wsStatus === 'connected' ? <Wifi size={12} /> : <WifiOff size={12} />}
            <span className="hidden sm:inline">
              {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? 'Connecting...' : 'Offline'}
            </span>
          </div>

          {/* Workspace selector */}
          <button
            onClick={() => setShowWorkspaceSelector(true)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <FolderOpen size={16} />
            {activeWorkspace?.name || 'Select Workspace'}
          </button>

          {/* Scan button */}
          {activeWorkspace && (
            <button
              onClick={() => scanMutation.mutate(activeWorkspace.id)}
              disabled={scanMutation.isPending}
              className="btn btn-secondary flex items-center gap-2"
            >
              {scanMutation.isPending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <RefreshCw size={16} />
              )}
              Scan
            </button>
          )}
        </div>
      </div>

      {/* No workspace selected */}
      {!activeWorkspace && (
        <div className="card text-center py-12">
          <FolderOpen size={48} className="mx-auto text-gray-500 mb-4" />
          <h3 className="text-lg font-medium mb-2">No Workspace Selected</h3>
          <p className="text-sm text-gray-400 mb-4">Select or register a workspace to get started</p>
          <button onClick={() => setShowWorkspaceSelector(true)} className="btn btn-primary">
            Select Workspace
          </button>
        </div>
      )}

      {/* Main content when workspace is selected */}
      {activeWorkspace && (
        <>
          {/* Primary Tab Navigation — 5 tabs */}
          <div className="flex items-center gap-1 border-b border-dark-border pb-2">
            {effectiveTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={cn(
                  'flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap',
                  activePrimary === tab.id
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'text-gray-500 hover:text-white hover:bg-dark-border/50'
                )}
              >
                <tab.icon size={15} />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Sub-Tab Navigation (if primary has sub-tabs) */}
          {currentPrimaryDef?.subTabs && currentPrimaryDef.subTabs.length > 0 && (
            <div className="flex items-center gap-1 pt-1 pb-2">
              {currentPrimaryDef.subTabs.map((sub) => (
                <button
                  key={sub.id}
                  onClick={() => handleSubTabChange(sub.id)}
                  className={cn(
                    'flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors whitespace-nowrap',
                    activeSub === sub.id
                      ? 'bg-gray-700/50 text-white'
                      : 'text-gray-500 hover:text-gray-300 hover:bg-dark-border/30'
                  )}
                >
                  <sub.icon size={12} />
                  {sub.label}
                </button>
              ))}
            </div>
          )}

          {/* ── Tab Content ────────────────────────────────────── */}

          {/* APP — embedded standalone app */}
          {activePrimary === 'app' && (
            <AppTab />
          )}

          {/* HOME */}
          {activePrimary === 'home' && (
            <HomeTab
              activeWorkspace={activeWorkspace}
              onNavigateTab={handleTabChange}
            />
          )}

          {/* WORK */}
          {activePrimary === 'work' && activeSub === 'queue' && (
            <WorkTab
              workspaceId={activeWorkspace.id}
              onNavigateTab={handleTabChange}
            />
          )}
          {activePrimary === 'work' && activeSub === 'deliverables' && (
            <DeliverablesTab />
          )}
          {activePrimary === 'work' && activeSub === 'initiatives' && (
            <InitiativesTab />
          )}

          {/* BUILD */}
          {activePrimary === 'build' && activeSub === 'content' && (
            <ContentStudioTab />
          )}
          {activePrimary === 'build' && activeSub === 'campaigns' && (
            <CampaignTab />
          )}
          {activePrimary === 'build' && activeSub === 'voices' && (
            <VoiceMarketplaceTab />
          )}
          {activePrimary === 'build' && activeSub === 'conceptforge' && (
            <ConceptForgeTab />
          )}

          {/* INTELLIGENCE */}
          {activePrimary === 'intelligence' && activeSub === 'dataintel' && (
            <DataIntelTab />
          )}
          {activePrimary === 'intelligence' && activeSub === 'knowledge' && (
            <KnowledgeTab />
          )}
          {activePrimary === 'intelligence' && activeSub === 'consciousness' && (
            <AIConsciousnessTab />
          )}

          {/* SYSTEM */}
          {activePrimary === 'system' && activeSub === 'ops' && (
            <div className="space-y-8">
              <OpsConsoleTab />
              <OperationsTab
                activeWorkspace={activeWorkspace}
                onViewFileContent={(operationId) => setViewingOperationId(operationId)}
                showSuccess={showSuccess}
                showError={showError}
              />
            </div>
          )}
          {activePrimary === 'system' && activeSub === 'boardroom' && (
            <BoardroomTab />
          )}
          {activePrimary === 'system' && activeSub === 'triggers' && (
            <TriggersTab
              showSuccess={showSuccess}
              showError={showError}
            />
          )}
          {activePrimary === 'system' && activeSub === 'evaluation' && (
            <Stage3EvaluationTab />
          )}
          {activePrimary === 'system' && activeSub === 'files' && (
            <FilesTab activeWorkspaceId={activeWorkspace.id} />
          )}
          {activePrimary === 'system' && activeSub === 'git' && (
            <GitTab
              activeWorkspace={activeWorkspace}
              showSuccess={showSuccess}
              showError={showError}
            />
          )}
        </>
      )}

      {/* Modals */}
      {showWorkspaceSelector && (
        <WorkspaceSelectorModal
          workspaces={workspaces}
          onSelect={(id) => activateMutation.mutate(id)}
          onClose={() => setShowWorkspaceSelector(false)}
          onCreateNew={() => {
            setShowWorkspaceSelector(false)
            setShowRegisterModal(true)
          }}
        />
      )}

      {showRegisterModal && (
        <RegisterWorkspaceModal
          onClose={() => setShowRegisterModal(false)}
          onSubmit={(data) => registerMutation.mutate(data)}
          isLoading={registerMutation.isPending}
        />
      )}

      {viewingOperationId && (
        <OperationContentModal
          operationId={viewingOperationId}
          onClose={() => setViewingOperationId(null)}
        />
      )}

      {/* Toast */}
      {actionResult && <Toast result={actionResult} onClose={() => setActionResult(null)} />}
    </div>
  )
}
