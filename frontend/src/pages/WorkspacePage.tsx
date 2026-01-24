import React, { useState, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workspaceApi, workspaceOperationsApi, bodyApi, docsIndexApi, DocsDocument, DocsDetailResponse } from '@/lib/api'
// Session 714: Real-time system events
import { useSystemEvents } from '@/hooks/useWebSocket'
import {
  FolderOpen, FileCode, GitBranch, History, CheckSquare, Plus,
  RefreshCw, ChevronRight, ChevronDown, File, Folder, Code,
  GitCommit, CheckCircle, XCircle, AlertTriangle,
  Loader2, Search, RotateCcw, Eye, Clock, X,
  FolderTree, Activity, Trash2, Heart, ExternalLink,
  FileEdit, Users, PieChart, Calendar, Wifi, WifiOff, FileText, Copy, Check,
  // Session 780: Icons for project context sections
  Key, Puzzle, Package, Link2, Map,
  // Session 784: Docs tab icon
  Book, ArrowRight
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useBodyGovernance } from '@/stores/bodyStore'
import { useAuthStore } from '@/stores/authStore'
import EntityLink from '@/components/EntityLink'
import { CompactBreadcrumb } from '@/components/Breadcrumb'

type WorkspaceTab = 'overview' | 'files' | 'git' | 'operations' | 'reviews' | 'docs'

// Session 780: WorkspaceContext interface for project understanding
interface WorkspaceContext {
  total_files: number
  total_directories: number
  total_lines_of_code: number
  file_type_counts: Record<string, number>
  file_tree: Record<string, string[]>
  key_files: Record<string, string>  // main_entry, routes, api_client, models, urls, settings
  coding_patterns: Record<string, string>  // component_pattern, hook_pattern, api_pattern, test_pattern
  dependencies: Record<string, Record<string, string>>  // { frontend: {react: "18.2.0"}, backend: {...} }
  import_aliases: Record<string, string>  // @/components → src/components
  directory_purposes: Record<string, string>  // directory → purpose description
  last_scanned_at: string
  scan_duration_ms?: number
}

interface Workspace {
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
  // Session 776: Tech stack data
  tech_stack?: Record<string, string>
  root_path?: string
  workspace_type?: string
  entry_points?: string[]
  // Session 780: Full workspace context
  context?: WorkspaceContext
}

interface WorkspaceOperation {
  id: string
  operation_type: string
  file_path: string
  agent_name: string
  description?: string
  success: boolean
  pending_review: boolean
  created_at: string
  diff?: string
  content_before?: string
  content_after?: string
  // Session 776: Added hidden fields
  error_message?: string
  execution_time_ms?: number
  requires_review?: boolean
  reviewed_by_human?: boolean
  human_approved?: boolean | null
  can_rollback?: boolean
  rolled_back?: boolean
}

interface FileNode {
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
  children?: FileNode[]
}

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

const tabs = [
  { id: 'overview' as WorkspaceTab, label: 'Overview', icon: Activity },
  { id: 'files' as WorkspaceTab, label: 'Files', icon: FolderTree },
  { id: 'git' as WorkspaceTab, label: 'Git', icon: GitBranch },
  { id: 'operations' as WorkspaceTab, label: 'Operations', icon: History },
  { id: 'reviews' as WorkspaceTab, label: 'Reviews', icon: CheckSquare },
  { id: 'docs' as WorkspaceTab, label: 'Docs', icon: Book },
]

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color }: { title: string; value: string | number; icon: React.ElementType; color: string }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{typeof value === 'number' ? value.toLocaleString() : value}</p>
        </div>
        <div className="h-12 w-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          <Icon size={24} style={{ color }} />
        </div>
      </div>
    </div>
  )
}

// Tree Node Item Component (separate component for proper key handling)
function TreeNodeItem({
  node,
  depth,
  expanded,
  selectedPath,
  onToggle,
  onSelect
}: {
  node: FileNode
  depth: number
  expanded: Set<string>
  selectedPath?: string
  onToggle: (path: string) => void
  onSelect: (path: string) => void
}) {
  const isExpanded = expanded.has(node.path)
  const isSelected = selectedPath === node.path
  const isDir = node.type === 'directory'

  return (
    <div>
      <div
        className={cn(
          'flex items-center gap-2 px-2 py-1 cursor-pointer rounded hover:bg-dark-border/50 transition-colors',
          isSelected && 'bg-primary-500/20 text-primary-400'
        )}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => isDir ? onToggle(node.path) : onSelect(node.path)}
      >
        {isDir ? (
          isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />
        ) : (
          <span className="w-[14px]" />
        )}
        {isDir ? (
          <Folder size={14} className="text-accent-amber" />
        ) : (
          <FileCode size={14} className="text-accent-cyan" />
        )}
        <span className="text-sm truncate">{node.name}</span>
      </div>
      {isDir && isExpanded && node.children && node.children.map(child => (
        <TreeNodeItem
          key={child.path}
          node={child}
          depth={depth + 1}
          expanded={expanded}
          selectedPath={selectedPath}
          onToggle={onToggle}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}

// File Tree Component
function FileTree({ files, onSelect, selectedPath }: { files: FileNode[]; onSelect: (path: string) => void; selectedPath?: string }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const toggleExpand = (path: string) => {
    const newExpanded = new Set(expanded)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpanded(newExpanded)
  }

  return (
    <div className="text-sm">
      {files.map(file => (
        <TreeNodeItem
          key={file.path}
          node={file}
          depth={0}
          expanded={expanded}
          selectedPath={selectedPath}
          onToggle={toggleExpand}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}

// Operation Row Component
// Session 780: Added isReviewing prop for loading state
function OperationRow({ operation, onRollback, onReview, onViewContent, isReviewing }: {
  operation: WorkspaceOperation
  onRollback?: () => void
  onReview?: (approved: boolean) => void
  onViewContent?: () => void  // Session 779: View file content callback
  isReviewing?: boolean  // Session 780: Loading state for review buttons
}) {
  const [showDiff, setShowDiff] = useState(false)

  const getOperationIcon = (type: string) => {
    switch (type) {
      case 'file_create': return <Plus size={14} className="text-accent-green" />
      case 'file_update': return <Code size={14} className="text-accent-amber" />
      case 'file_modify': return <Code size={14} className="text-accent-amber" />
      case 'file_delete': return <Trash2 size={14} className="text-accent-red" />
      case 'git_commit': return <GitCommit size={14} className="text-primary-400" />
      default: return <File size={14} className="text-gray-400" />
    }
  }

  // Session 776: Determine review status after human review
  const getReviewStatus = () => {
    if (!operation.reviewed_by_human) return null
    if (operation.human_approved === true) return 'approved'
    if (operation.human_approved === false) return 'rejected'
    return null
  }
  const reviewStatus = getReviewStatus()

  return (
    <div className={cn(
      "border rounded-lg p-3 space-y-2",
      operation.rolled_back ? "border-gray-600 bg-dark-bg/50 opacity-70" : "border-dark-border"
    )}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getOperationIcon(operation.operation_type)}
          <div>
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium">{operation.file_path || operation.operation_type}</p>
              {operation.rolled_back && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-gray-500/20 text-gray-400 flex items-center gap-1">
                  <RotateCcw size={10} />
                  Rolled Back
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              {/* Session 713: EntityLink for agent navigation */}
              <EntityLink
                type="agent"
                id={operation.agent_name}
                label={operation.agent_name}
                iconSize={12}
                className="text-xs"
              />
              <span>•</span>
              <Clock size={12} />
              <span>{new Date(operation.created_at).toLocaleString()}</span>
              {/* Session 776: Show execution time */}
              {operation.execution_time_ms !== undefined && (
                <>
                  <span>•</span>
                  <span>{operation.execution_time_ms}ms</span>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {operation.success ? (
            <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">Success</span>
          ) : (
            <span className="text-xs px-2 py-1 rounded bg-accent-red/20 text-accent-red">Failed</span>
          )}
          {/* Session 776: Show review status after human review */}
          {reviewStatus === 'approved' && (
            <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green flex items-center gap-1">
              <CheckCircle size={10} />
              Approved
            </span>
          )}
          {reviewStatus === 'rejected' && (
            <span className="text-xs px-2 py-1 rounded bg-accent-red/20 text-accent-red flex items-center gap-1">
              <XCircle size={10} />
              Rejected
            </span>
          )}
          {operation.pending_review && !operation.reviewed_by_human && (
            <span className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber">Pending Review</span>
          )}
          {/* Session 776: Show if rollback is available */}
          {operation.can_rollback && !operation.rolled_back && operation.success && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/10 text-primary-400" title="Rollback available">
              <RotateCcw size={12} />
            </span>
          )}
        </div>
      </div>

      {operation.description && (
        <p className="text-xs text-gray-400">{operation.description}</p>
      )}

      {/* Session 776: Show error message for failed operations */}
      {!operation.success && operation.error_message && (
        <div className="flex items-start gap-2 p-2 bg-accent-red/10 border border-accent-red/20 rounded text-xs text-accent-red">
          <XCircle size={14} className="flex-shrink-0 mt-0.5" />
          <span>{operation.error_message}</span>
        </div>
      )}

      <div className="flex items-center gap-2">
        {/* Session 799: View Content/Output button for all operations with content */}
        {onViewContent && operation.success && (
          <button
            onClick={onViewContent}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            <FileText size={12} />
            {['file_create', 'file_update', 'file_modify', 'file_delete', 'file_rename'].includes(operation.operation_type)
              ? 'View Content'
              : 'View Output'}
          </button>
        )}
        {operation.diff && (
          <button
            onClick={() => setShowDiff(!showDiff)}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            <Eye size={12} />
            {showDiff ? 'Hide Diff' : 'Show Diff'}
          </button>
        )}
        {onRollback && operation.success && operation.can_rollback && !operation.rolled_back && (
          <button
            onClick={onRollback}
            className="text-xs text-accent-amber hover:text-accent-amber/80 flex items-center gap-1"
          >
            <RotateCcw size={12} />
            Rollback
          </button>
        )}
        {/* Session 780: Fix - API returns requires_review not pending_review */}
        {/* Session 780: Added loading state and better button styling */}
        {onReview && (operation.requires_review || operation.pending_review) && !operation.reviewed_by_human && (
          <>
            <button
              onClick={() => onReview(true)}
              disabled={isReviewing}
              className={cn(
                "text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition-all",
                isReviewing
                  ? "bg-gray-600 text-gray-400 cursor-not-allowed"
                  : "bg-accent-green/20 text-accent-green hover:bg-accent-green/30 border border-accent-green/30"
              )}
            >
              {isReviewing ? <Loader2 size={12} className="animate-spin" /> : <CheckCircle size={12} />}
              Approve
            </button>
            <button
              onClick={() => onReview(false)}
              disabled={isReviewing}
              className={cn(
                "text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition-all",
                isReviewing
                  ? "bg-gray-600 text-gray-400 cursor-not-allowed"
                  : "bg-accent-red/20 text-accent-red hover:bg-accent-red/30 border border-accent-red/30"
              )}
            >
              {isReviewing ? <Loader2 size={12} className="animate-spin" /> : <XCircle size={12} />}
              Reject
            </button>
          </>
        )}
      </div>

      {showDiff && operation.diff && (
        <pre className="text-xs bg-dark-bg p-3 rounded overflow-x-auto max-h-64 overflow-y-auto font-mono">
          {operation.diff}
        </pre>
      )}
    </div>
  )
}

// Workspace Selector Modal
function WorkspaceSelectorModal({ workspaces, onSelect, onClose, onCreateNew }: {
  workspaces: Workspace[]
  onSelect: (id: string) => void
  onClose: () => void
  onCreateNew: () => void
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-lg mx-4 max-h-[80vh] overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <h3 className="text-lg font-semibold">Select Workspace</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>
        <div className="p-4 space-y-2 overflow-y-auto max-h-96">
          {workspaces.map(ws => (
            <button
              key={ws.id}
              onClick={() => { onSelect(ws.id); onClose() }}
              className={cn(
                'w-full p-3 rounded-lg text-left transition-colors',
                ws.is_active ? 'bg-primary-500/20 border border-primary-500/50' : 'bg-dark-bg hover:bg-dark-border'
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FolderOpen size={18} className={ws.is_active ? 'text-primary-400' : 'text-gray-400'} />
                  <span className="font-medium">{ws.name}</span>
                </div>
                {ws.is_active && (
                  <span className="text-xs px-2 py-1 rounded bg-primary-500/20 text-primary-400">Active</span>
                )}
              </div>
              <p className="text-xs text-gray-400 mt-1 truncate">{ws.path}</p>
            </button>
          ))}
        </div>
        <div className="p-4 border-t border-dark-border">
          <button
            onClick={onCreateNew}
            className="btn btn-primary w-full flex items-center justify-center gap-2"
          >
            <Plus size={16} />
            Register New Workspace
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 792: Enhanced Register Workspace Modal with GitHub support
function RegisterWorkspaceModal({ onClose, onSubmit, isLoading }: {
  onClose: () => void
  onSubmit: (data: { path?: string; github_url?: string; github_token?: string; name?: string; description?: string }) => void
  isLoading: boolean
}) {
  const [sourceType, setSourceType] = useState<'local' | 'github'>('local')
  const [path, setPath] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [githubToken, setGithubToken] = useState('')
  const [showToken, setShowToken] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const isValid = sourceType === 'local' ? !!path : !!githubUrl

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!isValid) return

    if (sourceType === 'local') {
      onSubmit({ path, name: name || undefined, description: description || undefined })
    } else {
      onSubmit({
        github_url: githubUrl,
        github_token: githubToken || undefined,
        name: name || undefined,
        description: description || undefined
      })
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-lg mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Register Workspace</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Source Type Toggle */}
        <div className="flex gap-2 mb-4 p-1 bg-dark-bg rounded-lg">
          <button
            type="button"
            onClick={() => setSourceType('local')}
            className={cn(
              'flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2',
              sourceType === 'local'
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white'
            )}
          >
            <Folder size={16} />
            Local Path
          </button>
          <button
            type="button"
            onClick={() => setSourceType('github')}
            className={cn(
              'flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2',
              sourceType === 'github'
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white'
            )}
          >
            <GitBranch size={16} />
            GitHub
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {sourceType === 'local' ? (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Project Path *</label>
              <input
                type="text"
                value={path}
                onChange={(e) => setPath(e.target.value)}
                placeholder="/path/to/project"
                className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
                required={sourceType === 'local'}
              />
              <p className="text-xs text-gray-500 mt-1">Absolute path to the project directory</p>
            </div>
          ) : (
            <>
              <div>
                <label className="block text-sm text-gray-400 mb-1">GitHub URL *</label>
                <input
                  type="text"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/username/repo.git"
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
                  required={sourceType === 'github'}
                />
                <p className="text-xs text-gray-500 mt-1">Public or private repository URL</p>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Personal Access Token
                  <span className="text-gray-500 ml-1">(for private repos)</span>
                </label>
                <div className="relative">
                  <input
                    type={showToken ? 'text' : 'password'}
                    value={githubToken}
                    onChange={(e) => setGithubToken(e.target.value)}
                    placeholder="ghp_xxxxxxxxxxxx"
                    className="w-full px-3 py-2 pr-10 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowToken(!showToken)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                  >
                    {showToken ? <Eye size={16} /> : <Eye size={16} className="opacity-50" />}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Required for private repos.{' '}
                  <a
                    href="https://github.com/settings/tokens/new?scopes=repo"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-400 hover:underline"
                  >
                    Create a token
                  </a>
                </p>
              </div>
            </>
          )}

          <div>
            <label className="block text-sm text-gray-400 mb-1">Name (optional)</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Project"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
            />
            <p className="text-xs text-gray-500 mt-1">Display name (auto-detected from path/URL if empty)</p>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Description (optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the project..."
              rows={2}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none resize-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !isValid}
              className="btn btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {isLoading && <Loader2 size={16} className="animate-spin" />}
              {sourceType === 'github' ? 'Clone & Register' : 'Register'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Git Commit Modal
function GitCommitModal({ onClose, onCommit, isLoading, bodyGovernance }: {
  onClose: () => void
  onCommit: (message: string) => void
  isLoading: boolean
  bodyGovernance?: { allowed: boolean; reason?: string }
}) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim()) return
    if (bodyGovernance && !bodyGovernance.allowed) return
    onCommit(message)
  }

  const isBlocked = bodyGovernance && !bodyGovernance.allowed

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Create Commit</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Session 713: Body Governance Warning */}
        {bodyGovernance?.reason && (
          <div className={cn(
            'flex items-start gap-3 p-3 rounded-lg mb-4',
            isBlocked
              ? 'bg-red-500/20 border border-red-500/30 text-red-200'
              : 'bg-amber-500/20 border border-amber-500/30 text-amber-200'
          )}>
            {isBlocked ? (
              <Heart size={18} className="text-red-400 animate-pulse flex-shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle size={18} className="text-amber-400 flex-shrink-0 mt-0.5" />
            )}
            <div className="text-sm">
              <p className="font-medium">{isBlocked ? 'Operation Blocked' : 'Health Warning'}</p>
              <p className="opacity-90 mt-0.5">{bodyGovernance.reason}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Commit Message *</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Describe your changes..."
              rows={3}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none resize-none"
              required
              disabled={isBlocked}
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !message.trim() || isBlocked}
              className={cn(
                'btn flex-1 flex items-center justify-center gap-2',
                isBlocked ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn-primary'
              )}
              title={isBlocked ? bodyGovernance?.reason : undefined}
            >
              {isLoading && <Loader2 size={16} className="animate-spin" />}
              <GitCommit size={16} />
              {isBlocked ? 'Blocked' : 'Commit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Session 776: Git Branch Modal
function GitBranchModal({ onClose, onCreate, isLoading, bodyGovernance, currentBranch }: {
  onClose: () => void
  onCreate: (branchName: string) => void
  isLoading: boolean
  bodyGovernance?: { allowed: boolean; reason?: string }
  currentBranch?: string
}) {
  const [branchName, setBranchName] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!branchName.trim()) return
    if (bodyGovernance && !bodyGovernance.allowed) return
    onCreate(branchName)
  }

  const isBlocked = bodyGovernance && !bodyGovernance.allowed

  // Validate branch name (no spaces, special chars, etc.)
  const isValidBranchName = branchName.trim().length > 0 && /^[a-zA-Z0-9_\-./]+$/.test(branchName)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Create New Branch</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Current Branch Info */}
        {currentBranch && (
          <div className="flex items-center gap-2 p-3 bg-dark-bg rounded-lg mb-4 text-sm">
            <GitBranch size={16} className="text-primary-400" />
            <span className="text-gray-400">From:</span>
            <span className="font-mono text-primary-400">{currentBranch}</span>
          </div>
        )}

        {/* Body Governance Warning */}
        {bodyGovernance?.reason && (
          <div className={cn(
            'flex items-start gap-3 p-3 rounded-lg mb-4',
            isBlocked
              ? 'bg-red-500/20 border border-red-500/30 text-red-200'
              : 'bg-amber-500/20 border border-amber-500/30 text-amber-200'
          )}>
            {isBlocked ? (
              <Heart size={18} className="text-red-400 animate-pulse flex-shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle size={18} className="text-amber-400 flex-shrink-0 mt-0.5" />
            )}
            <div className="text-sm">
              <p className="font-medium">{isBlocked ? 'Operation Blocked' : 'Health Warning'}</p>
              <p className="opacity-90 mt-0.5">{bodyGovernance.reason}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Branch Name *</label>
            <input
              type="text"
              value={branchName}
              onChange={(e) => setBranchName(e.target.value)}
              placeholder="feature/my-new-feature"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none font-mono"
              required
              disabled={isBlocked}
            />
            {branchName && !isValidBranchName && (
              <p className="text-xs text-accent-amber mt-1">
                Branch names can only contain letters, numbers, hyphens, underscores, dots, and slashes
              </p>
            )}
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !isValidBranchName || isBlocked}
              className={cn(
                'btn flex-1 flex items-center justify-center gap-2',
                isBlocked ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn-primary'
              )}
              title={isBlocked ? bodyGovernance?.reason : undefined}
            >
              {isLoading && <Loader2 size={16} className="animate-spin" />}
              <GitBranch size={16} />
              {isBlocked ? 'Blocked' : 'Create Branch'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Session 776: File History Modal
function FileHistoryModal({ filePath, operations, isLoading, onClose }: {
  filePath: string
  operations: WorkspaceOperation[]
  isLoading: boolean
  onClose: () => void
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div>
            <h3 className="text-lg font-semibold">File History</h3>
            <p className="text-xs text-gray-400 font-mono mt-1">{filePath}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 size={24} className="animate-spin text-primary-400" />
            </div>
          ) : operations.length > 0 ? (
            <div className="space-y-3">
              {operations.map(op => (
                <OperationRow key={op.id} operation={op} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <History size={32} className="mx-auto text-gray-500 mb-2" />
              <p className="text-gray-400">No operations recorded for this file</p>
            </div>
          )}
        </div>
        <div className="p-4 border-t border-dark-border flex justify-between items-center">
          <span className="text-sm text-gray-400">{operations.length} operation{operations.length !== 1 ? 's' : ''}</span>
          <button onClick={onClose} className="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  )
}

// Session 779: File Content Modal - View content of workspace operation outputs
interface OperationDetail {
  id: string
  file_path: string
  file_content_after?: string
  file_content_before?: string
  operation_type: string
  agent_name: string
  agent_task?: string
  created_at: string
  diff?: string
  success: boolean
  // Session 799: Command operation fields
  command?: string
  command_output?: string
  command_error?: string
  exit_code?: number
  execution_time_ms?: number
  error_message?: string
  lines_changed?: number
}

function FileContentModal({ operation, isLoading, onClose }: {
  operation: OperationDetail | null
  isLoading: boolean
  onClose: () => void
}) {
  const [copied, setCopied] = useState(false)
  const [showRaw, setShowRaw] = useState(false)
  const [activeView, setActiveView] = useState<'content' | 'diff' | 'output'>('content')

  // Session 799: Determine what content to show based on operation type
  const isFileOperation = ['file_create', 'file_modify', 'file_update', 'file_delete', 'file_rename'].includes(operation?.operation_type || '')
  const isCommandOperation = ['command_exec', 'build_run', 'test_run', 'lint_run', 'deploy'].includes(operation?.operation_type || '')
  const isGitOperation = ['git_commit', 'git_branch', 'git_checkout', 'git_merge'].includes(operation?.operation_type || '')

  // Get the primary content to display
  const getContent = () => {
    if (!operation) return ''

    if (isFileOperation) {
      if (activeView === 'diff' && operation.diff) return operation.diff
      return operation.file_content_after || ''
    }

    if (isCommandOperation || isGitOperation) {
      if (activeView === 'output') return operation.command_output || ''
      if (operation.command_error) return `Command: ${operation.command || 'N/A'}\n\nOutput:\n${operation.command_output || '(no output)'}\n\nError:\n${operation.command_error}`
      return `Command: ${operation.command || 'N/A'}\n\nOutput:\n${operation.command_output || '(no output)'}`
    }

    return operation.file_content_after || operation.command_output || ''
  }

  const content = getContent()
  const isMarkdown = operation?.file_path?.endsWith('.md') || operation?.file_path?.endsWith('.markdown')
  const fileName = operation?.file_path?.split('/').pop() || operation?.operation_type || 'Unknown'
  const hasDiff = isFileOperation && operation?.diff
  const hasCommandOutput = (isCommandOperation || isGitOperation) && operation?.command_output

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Simple markdown to HTML conversion for display
  const renderMarkdown = (text: string) => {
    let html = text
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-4 mb-2 text-white">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold mt-6 mb-3 text-white">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-6 mb-4 text-white">$1</h1>')
      .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-dark-bg px-1.5 py-0.5 rounded text-primary-400 text-sm">$1</code>')
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-dark-bg p-3 rounded-lg my-3 overflow-x-auto text-sm"><code>$2</code></pre>')
      .replace(/^\s*[-*]\s+(.*)$/gim, '<li class="ml-4 list-disc">$1</li>')
      .replace(/^---+$/gim, '<hr class="border-dark-border my-4" />')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-primary-400 hover:underline" target="_blank" rel="noopener">$1</a>')
      .replace(/\n\n/g, '</p><p class="my-2">')
      .replace(/\n/g, '<br />')

    return `<p class="my-2">${html}</p>`
  }

  // Get operation type label
  const getOperationLabel = () => {
    const labels: Record<string, string> = {
      'file_create': 'File Created',
      'file_modify': 'File Modified',
      'file_update': 'File Updated',
      'file_delete': 'File Deleted',
      'file_rename': 'File Renamed',
      'command_exec': 'Command Executed',
      'git_commit': 'Git Commit',
      'git_branch': 'Git Branch',
      'git_checkout': 'Git Checkout',
      'git_merge': 'Git Merge',
      'build_run': 'Build Run',
      'test_run': 'Test Run',
      'lint_run': 'Lint Run',
      'deploy': 'Deploy',
    }
    return labels[operation?.operation_type || ''] || operation?.operation_type || 'Operation'
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border flex-shrink-0">
          <div className="flex items-center gap-3">
            <FileText size={20} className="text-primary-400" />
            <div>
              <h3 className="text-lg font-semibold">{fileName}</h3>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <span className="font-mono">{operation?.file_path || getOperationLabel()}</span>
                {operation?.lines_changed !== undefined && operation.lines_changed > 0 && (
                  <span className="px-1.5 py-0.5 rounded bg-accent-amber/20 text-accent-amber">
                    {operation.lines_changed} lines changed
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {operation?.agent_name && (
              <span className="text-xs px-2 py-1 rounded bg-primary-500/10 text-primary-400">
                {operation.agent_name}
              </span>
            )}
            {operation?.execution_time_ms !== undefined && (
              <span className="text-xs px-2 py-1 rounded bg-dark-border text-gray-400">
                {operation.execution_time_ms}ms
              </span>
            )}
            <button onClick={onClose} className="text-gray-400 hover:text-white">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Agent Task (if available) */}
        {operation?.agent_task && (
          <div className="px-4 py-2 border-b border-dark-border bg-dark-bg/30">
            <p className="text-xs text-gray-400">
              <span className="text-gray-500">Task:</span> {operation.agent_task}
            </p>
          </div>
        )}

        {/* Toolbar */}
        {!isLoading && (
          <div className="flex items-center justify-between p-2 border-b border-dark-border bg-dark-bg/50 flex-shrink-0">
            <div className="flex items-center gap-2">
              {/* View toggle buttons */}
              {isFileOperation && (
                <>
                  <button
                    onClick={() => setActiveView('content')}
                    className={cn(
                      "text-xs px-2 py-1 rounded transition-colors",
                      activeView === 'content' ? "bg-primary-500/20 text-primary-400" : "bg-dark-border text-gray-400 hover:text-white"
                    )}
                  >
                    Content
                  </button>
                  {hasDiff && (
                    <button
                      onClick={() => setActiveView('diff')}
                      className={cn(
                        "text-xs px-2 py-1 rounded transition-colors",
                        activeView === 'diff' ? "bg-primary-500/20 text-primary-400" : "bg-dark-border text-gray-400 hover:text-white"
                      )}
                    >
                      Diff
                    </button>
                  )}
                </>
              )}
              {isMarkdown && activeView === 'content' && (
                <button
                  onClick={() => setShowRaw(!showRaw)}
                  className={cn(
                    "text-xs px-2 py-1 rounded transition-colors",
                    showRaw ? "bg-primary-500/20 text-primary-400" : "bg-dark-border text-gray-400 hover:text-white"
                  )}
                >
                  {showRaw ? 'Rendered' : 'Raw'}
                </button>
              )}
              {content && (
                <span className="text-xs text-gray-500">
                  {content.length.toLocaleString()} characters • {content.split('\n').length} lines
                </span>
              )}
            </div>
            {content && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs px-2 py-1 rounded bg-dark-border text-gray-400 hover:text-white transition-colors"
              >
                {copied ? <Check size={12} className="text-accent-green" /> : <Copy size={12} />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : !content ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-400">
              <FileText size={48} className="mb-4 opacity-50" />
              <p>No content available</p>
              <p className="text-xs mt-1">
                {isFileOperation
                  ? 'The file content was not stored for this operation'
                  : isCommandOperation || isGitOperation
                    ? 'No command output was captured'
                    : 'No details available for this operation'}
              </p>
            </div>
          ) : activeView === 'diff' ? (
            <pre className="text-sm font-mono whitespace-pre-wrap break-words leading-relaxed">
              {content.split('\n').map((line, i) => (
                <div
                  key={i}
                  className={cn(
                    "px-2 -mx-2",
                    line.startsWith('+') && !line.startsWith('+++') ? 'bg-accent-green/10 text-accent-green' :
                    line.startsWith('-') && !line.startsWith('---') ? 'bg-accent-red/10 text-accent-red' :
                    line.startsWith('@@') ? 'bg-primary-500/10 text-primary-400' :
                    'text-gray-300'
                  )}
                >
                  {line}
                </div>
              ))}
            </pre>
          ) : isMarkdown && !showRaw ? (
            <div
              className="prose prose-invert prose-sm max-w-none text-gray-300"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
            />
          ) : (
            <pre className="text-sm font-mono whitespace-pre-wrap break-words text-gray-300 leading-relaxed">
              {content}
            </pre>
          )}
        </div>

        {/* Error section (for failed operations) */}
        {operation?.error_message && (
          <div className="mx-4 mb-4 p-3 bg-accent-red/10 border border-accent-red/20 rounded-lg">
            <div className="flex items-start gap-2 text-sm text-accent-red">
              <XCircle size={16} className="flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Error</p>
                <p className="text-xs mt-1 opacity-80">{operation.error_message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-dark-border flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-4 text-xs text-gray-400">
            {operation?.created_at && (
              <span>Created: {new Date(operation.created_at).toLocaleString()}</span>
            )}
            {operation?.exit_code !== undefined && (
              <span className={cn(
                "px-1.5 py-0.5 rounded",
                operation.exit_code === 0 ? "bg-accent-green/20 text-accent-green" : "bg-accent-red/20 text-accent-red"
              )}>
                Exit code: {operation.exit_code}
              </span>
            )}
          </div>
          <button onClick={onClose} className="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  )
}

export default function WorkspacePage() {
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('overview')
  const [showWorkspaceSelector, setShowWorkspaceSelector] = useState(false)
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [showCommitModal, setShowCommitModal] = useState(false)
  const [showBranchModal, setShowBranchModal] = useState(false)
  const [selectedFilePath, setSelectedFilePath] = useState<string>()
  const [showFileHistory, setShowFileHistory] = useState(false)
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [operationFilter, setOperationFilter] = useState<string>('')
  // Session 779: File content modal state
  const [showFileContent, setShowFileContent] = useState(false)
  const [selectedOperationId, setSelectedOperationId] = useState<string | null>(null)
  // Session 780: Track which operation is being reviewed for loading state
  const [reviewingOperationId, setReviewingOperationId] = useState<string | null>(null)
  // Session 784: Docs tab state
  const [docsSearch, setDocsSearch] = useState('')
  const [docsStatusFilter, setDocsStatusFilter] = useState<string>('')
  const [docsTypeFilter, setDocsTypeFilter] = useState<string>('')
  const [selectedDocPath, setSelectedDocPath] = useState<string | null>(null)
  // Session 785: Collapsible Directory Map
  const [directoryMapExpanded, setDirectoryMapExpanded] = useState(false)
  const queryClient = useQueryClient()

  // Session 714: Real-time event handlers - refresh data when file events occur
  const handleFileModified = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['workspace-files'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-git-status'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-stats'] })
  }, [queryClient])

  // Session 776: Handler for agent execution events that might affect workspace
  const handleAgentExecution = useCallback(() => {
    // Agent executions may create workspace operations
    queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-stats'] })
  }, [queryClient])

  // Session 714: Subscribe to system events
  // Session 776: Added agent execution handlers for workspace operation updates
  const { status: wsStatus } = useSystemEvents({
    onFileModified: handleFileModified,
    onAgentExecutionComplete: handleAgentExecution,
  })

  // Session 713: Body Governance - Check file write permissions
  const { canWriteFile } = useBodyGovernance()

  // Session 797: Auth gating for API queries
  const { isAuthenticated } = useAuthStore()

  // Queries
  const { data: workspacesData, isLoading: loadingWorkspaces, error: workspacesError } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => workspaceApi.list(),
    retry: false, // Don't retry on auth errors
    enabled: isAuthenticated, // Session 797: Gate on auth
  })

  const { data: activeWorkspaceData } = useQuery({
    queryKey: ['workspace-active'],
    queryFn: () => workspaceApi.getActive(),
    retry: false,
    enabled: isAuthenticated, // Session 797: Gate on auth
  })

  const { data: dashboardData, isLoading: loadingDashboard } = useQuery({
    queryKey: ['workspace-dashboard'],
    queryFn: () => workspaceApi.dashboard(),
    retry: false,
    enabled: isAuthenticated, // Session 797: Gate on auth
  })

  const activeWorkspace = activeWorkspaceData?.data as Workspace | undefined
  const workspaces = (workspacesData?.data?.results || workspacesData?.data || []) as Workspace[]

  // Active workspace stats
  const { data: statsData } = useQuery({
    queryKey: ['workspace-stats', activeWorkspace?.id],
    queryFn: () => activeWorkspace ? workspaceApi.stats(activeWorkspace.id) : null,
    enabled: !!activeWorkspace?.id,
  })

  // Git status
  const { data: gitStatusData, refetch: refetchGitStatus } = useQuery({
    queryKey: ['workspace-git-status', activeWorkspace?.id],
    queryFn: () => activeWorkspace ? workspaceApi.gitStatus(activeWorkspace.id) : null,
    enabled: !!activeWorkspace?.id && activeTab === 'git',
  })

  // Files (mock for now - API returns flat list, we'd need to build tree)
  const { data: filesData } = useQuery({
    queryKey: ['workspace-files', activeWorkspace?.id],
    queryFn: () => activeWorkspace ? workspaceApi.files(activeWorkspace.id, '**/*') : null,
    enabled: !!activeWorkspace?.id && activeTab === 'files',
  })

  // File content
  const { data: fileContentData, isLoading: loadingFileContent } = useQuery({
    queryKey: ['workspace-file', activeWorkspace?.id, selectedFilePath],
    queryFn: () => activeWorkspace && selectedFilePath ? workspaceApi.readFile(activeWorkspace.id, selectedFilePath) : null,
    enabled: !!activeWorkspace?.id && !!selectedFilePath,
  })

  // Session 776: File history for selected file
  const { data: fileHistoryData, isLoading: loadingFileHistory } = useQuery({
    queryKey: ['workspace-file-history', activeWorkspace?.id, selectedFilePath],
    queryFn: () => activeWorkspace && selectedFilePath ? workspaceApi.fileHistory(activeWorkspace.id, selectedFilePath) : null,
    enabled: !!activeWorkspace?.id && !!selectedFilePath && showFileHistory,
  })

  // Operations
  const { data: operationsData, isLoading: loadingOperations } = useQuery({
    queryKey: ['workspace-operations', activeWorkspace?.id],
    queryFn: () => activeWorkspace ? workspaceApi.operations(activeWorkspace.id) : null,
    enabled: !!activeWorkspace?.id,
  })

  // Pending reviews
  const { data: pendingReviewsData } = useQuery({
    queryKey: ['workspace-pending-reviews'],
    queryFn: () => workspaceOperationsApi.pendingReviews(),
    enabled: activeTab === 'reviews',
    retry: false,
  })

  // Session 779: Fetch operation detail for file content viewing
  const { data: operationDetailData, isLoading: loadingOperationDetail } = useQuery({
    queryKey: ['workspace-operation-detail', selectedOperationId],
    queryFn: () => selectedOperationId ? workspaceOperationsApi.detail(selectedOperationId) : null,
    enabled: !!selectedOperationId && showFileContent,
  })

  // Session 712: Body Health integration - SKIN connected to Body
  const { data: bodyVitalsResponse } = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 60000, // Refresh every 60 seconds
  })

  // Session 784: Docs tab queries - auto-filter by workspace name/tech stack
  const workspaceSearchTerms = activeWorkspace
    ? [activeWorkspace.name, ...(activeWorkspace.path?.split('/').slice(-2) || [])].filter(Boolean).join(' ')
    : ''

  const { data: docsData, isLoading: loadingDocs } = useQuery({
    queryKey: ['workspace-docs', docsSearch || workspaceSearchTerms, docsStatusFilter, docsTypeFilter],
    queryFn: async () => {
      const params: Record<string, string> = {}
      // Use workspace-based search by default, or user's explicit search
      const searchTerm = docsSearch || workspaceSearchTerms
      if (searchTerm) params.search = searchTerm
      if (docsStatusFilter) params.status = docsStatusFilter
      if (docsTypeFilter) params.type = docsTypeFilter
      params.limit = '50'
      const res = await docsIndexApi.index(params)
      return res.data
    },
    enabled: activeTab === 'docs',
  })

  const { data: docsStatsData } = useQuery({
    queryKey: ['docs-stats'],
    queryFn: async () => {
      const res = await docsIndexApi.stats()
      return res.data
    },
    enabled: activeTab === 'docs',
  })

  const { data: selectedDocData, isLoading: loadingDocDetail } = useQuery<DocsDetailResponse>({
    queryKey: ['docs-detail', selectedDocPath],
    queryFn: async () => {
      const res = await docsIndexApi.detail(selectedDocPath!)
      return res.data
    },
    enabled: !!selectedDocPath && activeTab === 'docs',
  })

  // Mutations
  const activateMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-active'] })
      setActionResult({ type: 'success', message: 'Workspace activated' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to activate workspace' })
    },
  })

  // Session 792: Enhanced mutation to support GitHub URLs
  const registerMutation = useMutation({
    mutationFn: (data: {
      path?: string
      github_url?: string
      github_token?: string
      name?: string
      description?: string
    }) => workspaceApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      setShowRegisterModal(false)
      setActionResult({ type: 'success', message: 'Workspace registered successfully!' })
    },
    onError: (error: any) => {
      const message = error?.response?.data?.error || 'Failed to register workspace'
      setActionResult({ type: 'error', message })
    },
  })

  const scanMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.scan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-stats'] })
      setActionResult({ type: 'success', message: 'Workspace scanned' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to scan workspace' })
    },
  })

  const commitMutation = useMutation({
    mutationFn: ({ id, message }: { id: string; message: string }) => workspaceApi.gitCommit(id, { message }),
    onSuccess: () => {
      refetchGitStatus()
      setShowCommitModal(false)
      setActionResult({ type: 'success', message: 'Commit created' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to create commit' })
    },
  })

  // Session 776: Git Branch Creation
  const createBranchMutation = useMutation({
    mutationFn: ({ id, branchName }: { id: string; branchName: string }) =>
      workspaceApi.gitBranch(id, { branch_name: branchName }),
    onSuccess: (data) => {
      refetchGitStatus()
      setShowBranchModal(false)
      setActionResult({ type: 'success', message: `Branch "${data?.data?.branch_name}" created` })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to create branch' })
    },
  })

  const rollbackMutation = useMutation({
    mutationFn: (operationId: string) => workspaceOperationsApi.rollback(operationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
      setActionResult({ type: 'success', message: 'Operation rolled back' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to rollback operation' })
    },
  })

  // Session 780: Updated to clear reviewingOperationId on success/error
  const reviewMutation = useMutation({
    mutationFn: ({ id, approved }: { id: string; approved: boolean }) =>
      workspaceOperationsApi.review(id, { approved }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
      setActionResult({ type: 'success', message: 'Review submitted' })
      setReviewingOperationId(null)  // Clear loading state
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to submit review' })
      setReviewingOperationId(null)  // Clear loading state on error too
    },
  })

  // Clear toast
  useEffect(() => {
    if (actionResult) {
      const timer = setTimeout(() => setActionResult(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [actionResult])

  const stats = statsData?.data || {}
  const gitStatus = gitStatusData?.data || {}
  const operations = (operationsData?.data?.results || operationsData?.data || []) as WorkspaceOperation[]
  // Session 780: Fix - API returns { total, operations } not { results }
  const pendingReviews = (pendingReviewsData?.data?.operations || pendingReviewsData?.data?.results || []) as WorkspaceOperation[]
  const dashboard = dashboardData?.data || {}

  // Session 712: Body health data
  const bodyVitals = bodyVitalsResponse?.data || null
  const bodyHealthScore = bodyVitals?.health_score || 0
  const bodyOverallStatus = bodyVitals?.overall_health || 'unknown'
  const bodySystems = bodyVitals?.systems || {}

  // Use hierarchical tree from API (new format returns 'tree' with proper structure)
  const files: FileNode[] = filesData?.data?.tree || []

  const filteredOperations = operationFilter
    ? operations.filter(op =>
        op.file_path.toLowerCase().includes(operationFilter.toLowerCase()) ||
        op.agent_name.toLowerCase().includes(operationFilter.toLowerCase())
      )
    : operations

  if (loadingWorkspaces || loadingDashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  // Handle authentication/authorization errors
  if (workspacesError) {
    const isAuthError = (workspacesError as { response?: { status?: number } })?.response?.status === 401 ||
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
            ? 'Please log in to access the Workspace Manager. The SKIN Layer API requires authentication.'
            : 'Unable to connect to the Workspace API. Please check that the backend is running.'}
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
          {/* Session 713: Breadcrumb navigation */}
          <CompactBreadcrumb currentPage="Workspace" className="mb-2" />
          <h1 className="text-2xl font-bold">Workspace</h1>
          <p className="text-sm text-gray-400 mt-1">SKIN Layer - Agent Project Execution System</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Session 776: WebSocket status indicator */}
          <div
            className={cn(
              'flex items-center gap-1.5 px-2 py-1 rounded text-xs',
              wsStatus === 'connected' ? 'bg-accent-green/10 text-accent-green' :
              wsStatus === 'connecting' ? 'bg-accent-amber/10 text-accent-amber' :
              'bg-gray-500/10 text-gray-500'
            )}
            title={`WebSocket: ${wsStatus}${wsStatus === 'connected' ? ' - Real-time updates active' : ''}`}
          >
            {wsStatus === 'connected' ? <Wifi size={12} /> : <WifiOff size={12} />}
            <span className="hidden sm:inline">
              {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? 'Connecting...' : 'Offline'}
            </span>
          </div>
          <button
            onClick={() => setShowWorkspaceSelector(true)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <FolderOpen size={16} />
            {activeWorkspace?.name || 'Select Workspace'}
          </button>
          {activeWorkspace && (
            <button
              onClick={() => scanMutation.mutate(activeWorkspace.id)}
              disabled={scanMutation.isPending}
              className="btn btn-secondary flex items-center gap-2"
            >
              {scanMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
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
          <button
            onClick={() => setShowWorkspaceSelector(true)}
            className="btn btn-primary"
          >
            Select Workspace
          </button>
        </div>
      )}

      {/* Main content when workspace is selected */}
      {activeWorkspace && (
        <>
          {/* Tabs */}
          <div className="flex gap-2 border-b border-dark-border pb-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors',
                  activeTab === tab.id
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
                )}
              >
                <tab.icon size={16} />
                {tab.label}
                {tab.id === 'reviews' && pendingReviews.length > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 rounded-full bg-accent-amber/20 text-accent-amber text-xs">
                    {pendingReviews.length}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Active Workspace Info */}
              <div className="card">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">{activeWorkspace.name}</h3>
                    <p className="text-sm text-gray-400 font-mono mt-1">{activeWorkspace.path}</p>
                    {activeWorkspace.description && (
                      <p className="text-sm text-gray-500 mt-2">{activeWorkspace.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {stats.project?.last_scanned && (
                      <span className="text-xs text-gray-500 flex items-center gap-1">
                        <Calendar size={12} />
                        Scanned {new Date(stats.project.last_scanned).toLocaleDateString()}
                      </span>
                    )}
                    {activeWorkspace.is_git_repo && (
                      <span className="text-xs px-2 py-1 rounded bg-primary-500/20 text-primary-400 flex items-center gap-1">
                        <GitBranch size={12} />
                        Git
                      </span>
                    )}
                    <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">Active</span>
                  </div>
                </div>
              </div>

              {/* Stats Row 1: Project Stats */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Total Files"
                  value={stats.project?.total_files || dashboard.total_files || 0}
                  icon={File}
                  color="#8b5cf6"
                />
                <StatCard
                  title="Directories"
                  value={stats.project?.total_directories || 0}
                  icon={Folder}
                  color="#a855f7"
                />
                <StatCard
                  title="Lines of Code"
                  value={stats.project?.total_lines_of_code || dashboard.total_lines || 0}
                  icon={Code}
                  color="#22c55e"
                />
                <StatCard
                  title="Pending Reviews"
                  value={pendingReviews.length}
                  icon={CheckSquare}
                  color="#06b6d4"
                />
              </div>

              {/* Stats Row 2: Operations Stats */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Total Operations"
                  value={stats.totals?.operations || 0}
                  icon={Activity}
                  color="#3b82f6"
                />
                <StatCard
                  title="Files Written"
                  value={stats.totals?.files_written || 0}
                  icon={FileEdit}
                  color="#10b981"
                />
                <StatCard
                  title="Git Commits"
                  value={stats.totals?.commits || 0}
                  icon={GitCommit}
                  color="#f59e0b"
                />
                <StatCard
                  title="Rollbacks Available"
                  value={stats.rollback_available || 0}
                  icon={RotateCcw}
                  color="#ef4444"
                />
              </div>

              {/* 24h Activity Breakdown */}
              {stats.last_24h && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Last 24 Hours</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-dark-bg rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Operations</span>
                        <span className="text-xl font-bold">{stats.last_24h.operations || 0}</span>
                      </div>
                    </div>
                    <div className="bg-dark-bg rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Successful</span>
                        <span className="text-xl font-bold text-accent-green">{stats.last_24h.successful || 0}</span>
                      </div>
                      {stats.last_24h.operations > 0 && (
                        <div className="mt-2 h-1.5 bg-dark-border rounded-full overflow-hidden">
                          <div
                            className="h-full bg-accent-green rounded-full"
                            style={{ width: `${((stats.last_24h.successful || 0) / stats.last_24h.operations) * 100}%` }}
                          />
                        </div>
                      )}
                    </div>
                    <div className="bg-dark-bg rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Failed</span>
                        <span className="text-xl font-bold text-accent-red">{stats.last_24h.failed || 0}</span>
                      </div>
                      {stats.last_24h.operations > 0 && (
                        <div className="mt-2 h-1.5 bg-dark-border rounded-full overflow-hidden">
                          <div
                            className="h-full bg-accent-red rounded-full"
                            style={{ width: `${((stats.last_24h.failed || 0) / stats.last_24h.operations) * 100}%` }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* 7-Day Trends */}
              {stats.last_7d && (stats.last_7d.by_type || stats.last_7d.by_agent) && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* By Type */}
                  {stats.last_7d.by_type && Object.keys(stats.last_7d.by_type).length > 0 && (
                    <div className="card">
                      <div className="flex items-center gap-2 mb-4">
                        <PieChart size={18} className="text-primary-400" />
                        <h3 className="text-lg font-semibold">7-Day by Type</h3>
                      </div>
                      <div className="space-y-2">
                        {Object.entries(stats.last_7d.by_type).map(([type, count]) => (
                          <div key={type} className="flex items-center justify-between p-2 bg-dark-bg rounded">
                            <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
                            <span className="text-sm font-medium text-primary-400">{count as number}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* By Agent */}
                  {stats.last_7d.by_agent && Object.keys(stats.last_7d.by_agent).length > 0 && (
                    <div className="card">
                      <div className="flex items-center gap-2 mb-4">
                        <Users size={18} className="text-accent-cyan" />
                        <h3 className="text-lg font-semibold">7-Day by Agent</h3>
                      </div>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {Object.entries(stats.last_7d.by_agent)
                          .sort((a, b) => (b[1] as number) - (a[1] as number))
                          .slice(0, 10)
                          .map(([agent, count]) => (
                            <div key={agent} className="flex items-center justify-between p-2 bg-dark-bg rounded">
                              <span className="text-sm">{agent}</span>
                              <span className="text-sm font-medium text-accent-cyan">{count as number}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* File Types Breakdown */}
              {stats.project?.file_types && Object.keys(stats.project.file_types).length > 0 && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <FileCode size={18} className="text-accent-amber" />
                    <h3 className="text-lg font-semibold">File Types</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(stats.project.file_types)
                      .sort((a, b) => (b[1] as number) - (a[1] as number))
                      .slice(0, 20)
                      .map(([ext, count]) => (
                        <span
                          key={ext}
                          className="px-3 py-1.5 bg-dark-bg rounded-lg text-sm flex items-center gap-2"
                        >
                          <span className="text-accent-amber font-mono">{ext}</span>
                          <span className="text-gray-400">{count as number}</span>
                        </span>
                      ))}
                  </div>
                </div>
              )}

              {/* Session 776: Tech Stack Display */}
              {activeWorkspace?.tech_stack && Object.keys(activeWorkspace.tech_stack).length > 0 && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <Code size={18} className="text-accent-cyan" />
                    <h3 className="text-lg font-semibold">Tech Stack</h3>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {Object.entries(activeWorkspace.tech_stack).map(([category, technology]) => (
                      <div key={category} className="bg-dark-bg rounded-lg p-3">
                        <p className="text-xs text-gray-400 capitalize mb-1">{category.replace('_', ' ')}</p>
                        <p className="text-sm font-medium text-accent-cyan">{technology}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session 780: Key Files - Important project files for agents */}
              {activeWorkspace?.context?.key_files && Object.keys(activeWorkspace.context.key_files).length > 0 && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <Key size={18} className="text-accent-green" />
                    <h3 className="text-lg font-semibold">Key Files</h3>
                    <span className="text-xs text-gray-500">Entry points agents use</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {Object.entries(activeWorkspace.context.key_files).map(([role, filePath]) => (
                      <div key={role} className="bg-dark-bg rounded-lg p-3 flex items-start gap-3">
                        <FileCode size={16} className="text-accent-green flex-shrink-0 mt-0.5" />
                        <div className="min-w-0">
                          <p className="text-xs text-gray-400 capitalize mb-1">{role.replace(/_/g, ' ')}</p>
                          <p className="text-sm font-mono text-gray-200 truncate" title={filePath}>{filePath}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session 780: Coding Patterns - Detected conventions */}
              {activeWorkspace?.context?.coding_patterns && Object.keys(activeWorkspace.context.coding_patterns).length > 0 && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <Puzzle size={18} className="text-primary-400" />
                    <h3 className="text-lg font-semibold">Coding Patterns</h3>
                    <span className="text-xs text-gray-500">Detected conventions</span>
                  </div>
                  <div className="space-y-2">
                    {Object.entries(activeWorkspace.context.coding_patterns).map(([pattern, description]) => (
                      <div key={pattern} className="flex items-start gap-3 p-2 bg-dark-bg rounded-lg">
                        <Code size={14} className="text-primary-400 flex-shrink-0 mt-1" />
                        <div>
                          <span className="text-sm font-medium capitalize">{pattern.replace(/_/g, ' ')}</span>
                          <p className="text-xs text-gray-400 mt-0.5">{description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session 780: Dependencies - Project packages */}
              {activeWorkspace?.context?.dependencies && Object.keys(activeWorkspace.context.dependencies).length > 0 && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <Package size={18} className="text-accent-amber" />
                    <h3 className="text-lg font-semibold">Dependencies</h3>
                  </div>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {Object.entries(activeWorkspace.context.dependencies).map(([category, packages]) => (
                      <div key={category} className="bg-dark-bg rounded-lg p-4">
                        <h4 className="text-sm font-medium capitalize mb-3 text-accent-amber">{category}</h4>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(packages as Record<string, string>).slice(0, 15).map(([pkg, version]) => (
                            <span
                              key={pkg}
                              className="px-2 py-1 bg-dark-border rounded text-xs"
                              title={`${pkg}@${version}`}
                            >
                              <span className="text-gray-300">{pkg}</span>
                              <span className="text-gray-500 ml-1">@{version}</span>
                            </span>
                          ))}
                          {Object.keys(packages as Record<string, string>).length > 15 && (
                            <span className="px-2 py-1 bg-dark-border rounded text-xs text-gray-500">
                              +{Object.keys(packages as Record<string, string>).length - 15} more
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session 780: Import Aliases - Path shortcuts */}
              {activeWorkspace?.context?.import_aliases && Object.keys(activeWorkspace.context.import_aliases).length > 0 && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <Link2 size={18} className="text-accent-purple" />
                    <h3 className="text-lg font-semibold">Import Aliases</h3>
                    <span className="text-xs text-gray-500">Path shortcuts</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(activeWorkspace.context.import_aliases).map(([alias, realPath]) => (
                      <div key={alias} className="flex items-center gap-2 px-3 py-2 bg-dark-bg rounded-lg">
                        <span className="text-sm font-mono text-accent-purple">{alias}</span>
                        <ChevronRight size={14} className="text-gray-500" />
                        <span className="text-sm font-mono text-gray-400">{realPath}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session 780: Directory Purposes - What each folder is for */}
              {/* Session 785: Made collapsible to reduce scrolling */}
              {activeWorkspace?.context?.directory_purposes && Object.keys(activeWorkspace.context.directory_purposes).length > 0 && (
                <div className="card">
                  <button
                    onClick={() => setDirectoryMapExpanded(!directoryMapExpanded)}
                    className="w-full flex items-center justify-between cursor-pointer hover:bg-dark-bg/50 -m-4 p-4 rounded-lg transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <Map size={18} className="text-accent-red" />
                      <h3 className="text-lg font-semibold">Directory Map</h3>
                      <span className="text-xs text-gray-500">
                        {Object.keys(activeWorkspace.context.directory_purposes).length} folders
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {!directoryMapExpanded && (
                        <span className="text-xs text-gray-500">Click to expand</span>
                      )}
                      {directoryMapExpanded ? (
                        <ChevronDown size={18} className="text-gray-400" />
                      ) : (
                        <ChevronRight size={18} className="text-gray-400" />
                      )}
                    </div>
                  </button>
                  {directoryMapExpanded && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-4">
                      {Object.entries(activeWorkspace.context.directory_purposes).map(([dir, purpose]) => (
                        <div key={dir} className="flex items-start gap-2 p-2 bg-dark-bg rounded-lg">
                          <Folder size={14} className="text-accent-amber flex-shrink-0 mt-1" />
                          <div className="min-w-0">
                            <p className="text-sm font-mono text-gray-200 truncate" title={dir}>{dir}</p>
                            <p className="text-xs text-gray-400 mt-0.5">{purpose}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Session 712: Body Health Card - SKIN connected to Body */}
              {bodyVitals && (
                <div className="card">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {/* Animated Heart */}
                      <div className={cn(
                        'h-14 w-14 rounded-xl flex items-center justify-center',
                        bodyHealthScore >= 80 ? 'bg-accent-green/20' :
                        bodyHealthScore >= 50 ? 'bg-accent-amber/20' : 'bg-accent-red/20'
                      )}>
                        <Heart
                          size={28}
                          className={cn(
                            'animate-pulse',
                            bodyHealthScore >= 80 ? 'text-accent-green' :
                            bodyHealthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
                          )}
                          fill="currentColor"
                        />
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Body Health</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-2xl font-bold">{(bodyHealthScore ?? 0).toFixed(0)}%</span>
                          <span className={cn(
                            'text-xs px-2 py-0.5 rounded capitalize',
                            bodyOverallStatus === 'healthy' ? 'bg-accent-green/20 text-accent-green' :
                            bodyOverallStatus === 'degraded' ? 'bg-accent-amber/20 text-accent-amber' :
                            'bg-accent-red/20 text-accent-red'
                          )}>
                            {bodyOverallStatus}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Body Systems Status Strip */}
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1 text-lg" title="Body Systems">
                        <span title={`Heart: ${bodySystems.heart?.status || 'unknown'}`}>
                          {bodySystems.heart?.status === 'healthy' ? '❤️' : bodySystems.heart?.status === 'degraded' ? '💛' : '🖤'}
                        </span>
                        <span title={`Lungs: ${bodySystems.lungs?.status || 'unknown'}`}>
                          {bodySystems.lungs?.status === 'healthy' ? '🫁' : bodySystems.lungs?.status === 'depleted' ? '😤' : '💨'}
                        </span>
                        <span title={`Circulatory: ${bodySystems.circulatory?.status || 'unknown'}`}>
                          {bodySystems.circulatory?.status === 'flowing' ? '🩸' : '🧊'}
                        </span>
                        <span title={`Spine: ${bodySystems.spine?.status || 'unknown'}`}>
                          {bodySystems.spine?.status === 'aligned' ? '🦴' : '⚠️'}
                        </span>
                        <span title={`Immune: ${bodySystems.immune?.status || 'unknown'}`}>
                          {bodySystems.immune?.status === 'protected' ? '🛡️' : '🦠'}
                        </span>
                        <span title={`Digestive: ${bodySystems.digestive?.status || 'unknown'}`}>
                          {bodySystems.digestive?.status === 'healthy' ? '🍽️' : '🤢'}
                        </span>
                        <span title={`Muscular: ${bodySystems.muscular?.status || 'unknown'}`}>
                          {bodySystems.muscular?.status === 'strong' || bodySystems.muscular?.status === 'fit' ? '💪' : '😓'}
                        </span>
                      </div>
                      <a
                        href="/body-health"
                        className="flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300 transition-colors"
                      >
                        <span>View Details</span>
                        <ExternalLink size={14} />
                      </a>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-3">
                    🧬 SKIN Layer connected to AI Body — Workspace is how agents touch the real world
                  </p>
                </div>
              )}

              {/* Recent Operations */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Recent Operations</h3>
                {operations.length > 0 ? (
                  <div className="space-y-3">
                    {operations.slice(0, 5).map(op => (
                      <OperationRow
                        key={op.id}
                        operation={op}
                        onViewContent={() => {
                          setSelectedOperationId(op.id)
                          setShowFileContent(true)
                        }}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-sm text-center py-8">No operations yet</p>
                )}
              </div>
            </div>
          )}

          {/* Files Tab */}
          {activeTab === 'files' && (
            <div className="space-y-6">
              {/* Files Stats Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm">
                    <File size={16} className="text-primary-400" />
                    <span className="text-gray-400">Files:</span>
                    <span className="font-medium">{filesData?.data?.total_files || 0}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Folder size={16} className="text-accent-amber" />
                    <span className="text-gray-400">Directories:</span>
                    <span className="font-medium">{filesData?.data?.total_directories || 0}</span>
                  </div>
                </div>
                {filesData?.data?.last_scanned && (
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Calendar size={12} />
                    <span>Last scanned: {new Date(filesData.data.last_scanned).toLocaleString()}</span>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* File Tree */}
                <div className="card lg:col-span-1">
                  <h3 className="text-lg font-semibold mb-4">Files</h3>
                  <div className="max-h-[500px] overflow-y-auto">
                    {files.length > 0 ? (
                      <FileTree files={files} onSelect={setSelectedFilePath} selectedPath={selectedFilePath} />
                    ) : (
                      <p className="text-gray-400 text-sm text-center py-8">No files found. Try scanning the workspace.</p>
                    )}
                  </div>
                </div>

                {/* File Content */}
                <div className="card lg:col-span-2">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">
                      {selectedFilePath ? selectedFilePath.split('/').pop() : 'Select a file'}
                    </h3>
                    {selectedFilePath && (
                      <div className="flex items-center gap-3">
                        {/* Session 776: View History button */}
                        <button
                          onClick={() => setShowFileHistory(true)}
                          className="btn btn-secondary btn-sm flex items-center gap-1.5"
                        >
                          <History size={14} />
                          View History
                        </button>
                        {fileContentData?.data && (
                          <div className="flex items-center gap-3 text-xs text-gray-500">
                            {fileContentData.data.size !== undefined && (
                              <span>{((fileContentData.data?.size ?? 0) / 1024).toFixed(1)} KB</span>
                            )}
                            {fileContentData.data.truncated && (
                              <span className="px-2 py-0.5 bg-accent-amber/20 text-accent-amber rounded">
                                Truncated (file too large)
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  {selectedFilePath ? (
                    loadingFileContent ? (
                      <div className="flex items-center justify-center h-64">
                        <Loader2 size={24} className="animate-spin text-primary-400" />
                      </div>
                    ) : (
                      <>
                        {fileContentData?.data?.truncated && (
                          <div className="flex items-center gap-2 p-2 mb-2 bg-accent-amber/10 border border-accent-amber/20 rounded text-xs text-accent-amber">
                            <AlertTriangle size={14} />
                            <span>File content truncated. Only showing first 100KB.</span>
                          </div>
                        )}
                        <pre className="text-xs bg-dark-bg p-4 rounded-lg overflow-auto max-h-[500px] font-mono">
                          {fileContentData?.data?.content || 'File is empty or could not be read'}
                        </pre>
                      </>
                    )
                  ) : (
                    <div className="text-gray-400 text-sm text-center py-16">
                      <FileCode size={32} className="mx-auto mb-2 opacity-50" />
                      <p>Select a file from the tree to view its content</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Git Tab */}
          {activeTab === 'git' && (
            <div className="space-y-6">
              {/* Session 713: Body Governance Warning for Git Operations */}
              {canWriteFile.reason && (
                <div className={cn(
                  'flex items-center gap-3 p-3 rounded-lg',
                  !canWriteFile.allowed
                    ? 'bg-red-500/20 border border-red-500/30'
                    : 'bg-amber-500/20 border border-amber-500/30'
                )}>
                  {!canWriteFile.allowed ? (
                    <Heart size={18} className="text-red-400 animate-pulse" />
                  ) : (
                    <AlertTriangle size={18} className="text-amber-400" />
                  )}
                  <span className={cn(
                    'text-sm',
                    !canWriteFile.allowed ? 'text-red-200' : 'text-amber-200'
                  )}>
                    {canWriteFile.reason}
                  </span>
                </div>
              )}

              {/* Git Actions */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => refetchGitStatus()}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <RefreshCw size={16} />
                  Refresh Status
                </button>
                <button
                  onClick={() => setShowCommitModal(true)}
                  disabled={!canWriteFile.allowed}
                  className={cn(
                    'btn flex items-center gap-2',
                    canWriteFile.allowed ? 'btn-primary' : 'btn-secondary opacity-50 cursor-not-allowed'
                  )}
                  title={!canWriteFile.allowed ? canWriteFile.reason : undefined}
                >
                  <GitCommit size={16} />
                  New Commit
                  {!canWriteFile.allowed && (
                    <Heart size={14} className="text-red-400 animate-pulse ml-1" />
                  )}
                </button>
                {/* Session 776: New Branch button */}
                <button
                  onClick={() => setShowBranchModal(true)}
                  disabled={!canWriteFile.allowed}
                  className={cn(
                    'btn flex items-center gap-2',
                    canWriteFile.allowed ? 'btn-secondary' : 'btn-secondary opacity-50 cursor-not-allowed'
                  )}
                  title={!canWriteFile.allowed ? canWriteFile.reason : undefined}
                >
                  <GitBranch size={16} />
                  New Branch
                  {!canWriteFile.allowed && (
                    <Heart size={14} className="text-red-400 animate-pulse ml-1" />
                  )}
                </button>
              </div>

              {/* Git Status */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Status</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-2 bg-dark-bg rounded">
                      <span className="text-sm">Branch</span>
                      <span className="text-sm font-mono text-primary-400">{gitStatus.branch || 'main'}</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-dark-bg rounded">
                      <span className="text-sm">Modified Files</span>
                      <span className="text-sm text-accent-amber">{gitStatus.modified?.length || 0}</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-dark-bg rounded">
                      <span className="text-sm">Staged Files</span>
                      <span className="text-sm text-accent-green">{gitStatus.staged?.length || 0}</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-dark-bg rounded">
                      <span className="text-sm">Deleted Files</span>
                      <span className="text-sm text-accent-red">{gitStatus.deleted?.length || 0}</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-dark-bg rounded">
                      <span className="text-sm">Untracked Files</span>
                      <span className="text-sm text-gray-400">{gitStatus.untracked?.length || 0}</span>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Changed Files</h3>
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {(gitStatus.staged || []).map((file: string) => (
                      <div key={`staged-${file}`} className="flex items-center gap-2 p-2 bg-dark-bg rounded text-sm">
                        <span className="text-accent-green font-medium w-4">A</span>
                        <span className="font-mono truncate">{file}</span>
                      </div>
                    ))}
                    {(gitStatus.modified || []).map((file: string) => (
                      <div key={`mod-${file}`} className="flex items-center gap-2 p-2 bg-dark-bg rounded text-sm">
                        <span className="text-accent-amber font-medium w-4">M</span>
                        <span className="font-mono truncate">{file}</span>
                      </div>
                    ))}
                    {(gitStatus.deleted || []).map((file: string) => (
                      <div key={`del-${file}`} className="flex items-center gap-2 p-2 bg-dark-bg rounded text-sm">
                        <span className="text-accent-red font-medium w-4">D</span>
                        <span className="font-mono truncate line-through opacity-70">{file}</span>
                      </div>
                    ))}
                    {(gitStatus.untracked || []).map((file: string) => (
                      <div key={`new-${file}`} className="flex items-center gap-2 p-2 bg-dark-bg rounded text-sm">
                        <span className="text-gray-500 font-medium w-4">?</span>
                        <span className="font-mono truncate text-gray-400">{file}</span>
                      </div>
                    ))}
                    {(!gitStatus.modified?.length && !gitStatus.staged?.length && !gitStatus.deleted?.length && !gitStatus.untracked?.length) && (
                      <p className="text-gray-400 text-sm text-center py-4">Working tree clean</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Operations Tab */}
          {activeTab === 'operations' && (
            <div className="space-y-4">
              {/* Filter */}
              <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-sm">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={operationFilter}
                    onChange={(e) => setOperationFilter(e.target.value)}
                    placeholder="Filter by file or agent..."
                    className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
                  />
                </div>
                <span className="text-sm text-gray-400">{filteredOperations.length} operations</span>
              </div>

              {/* Operations List */}
              {loadingOperations ? (
                <div className="flex items-center justify-center h-32">
                  <Loader2 size={24} className="animate-spin text-primary-400" />
                </div>
              ) : filteredOperations.length > 0 ? (
                <div className="space-y-3">
                  {filteredOperations.map(op => (
                    <OperationRow
                      key={op.id}
                      operation={op}
                      onRollback={() => rollbackMutation.mutate(op.id)}
                      onViewContent={() => {
                        setSelectedOperationId(op.id)
                        setShowFileContent(true)
                      }}
                    />
                  ))}
                </div>
              ) : (
                <div className="card text-center py-12">
                  <History size={32} className="mx-auto text-gray-500 mb-2" />
                  <p className="text-gray-400">No operations found</p>
                </div>
              )}
            </div>
          )}

          {/* Reviews Tab */}
          {activeTab === 'reviews' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Pending Reviews ({pendingReviews.length})</h3>
              {pendingReviews.length > 0 ? (
                <div className="space-y-3">
                  {/* Session 780: Added isReviewing prop for button loading state */}
                  {pendingReviews.map(op => (
                    <OperationRow
                      key={op.id}
                      operation={op}
                      onReview={(approved) => {
                        setReviewingOperationId(op.id)  // Track which operation is being reviewed
                        reviewMutation.mutate({ id: op.id, approved })
                      }}
                      onViewContent={() => {
                        setSelectedOperationId(op.id)
                        setShowFileContent(true)
                      }}
                      isReviewing={reviewMutation.isPending && reviewingOperationId === op.id}
                    />
                  ))}
                </div>
              ) : (
                <div className="card text-center py-12">
                  <CheckSquare size={32} className="mx-auto text-gray-500 mb-2" />
                  <p className="text-gray-400">No pending reviews</p>
                </div>
              )}
            </div>
          )}

          {/* Session 784: Docs Tab - Documentation relevant to this workspace */}
          {activeTab === 'docs' && (
            <div className="space-y-4">
              {/* Stats Row */}
              {docsStatsData && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div className="text-xl font-bold text-cyan-400">{docsStatsData.total_documents}</div>
                    <div className="text-xs text-gray-400">Total Docs</div>
                  </div>
                  <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div className="text-xl font-bold text-green-400">{docsStatsData.by_status?.active || 0}</div>
                    <div className="text-xs text-gray-400">Active</div>
                  </div>
                  <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div className="text-xl font-bold text-purple-400">{docsStatsData.graph.total_links}</div>
                    <div className="text-xs text-gray-400">Cross-Links</div>
                  </div>
                  <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div className="text-xl font-bold text-yellow-400">{docsData?.filtered_count || 0}</div>
                    <div className="text-xs text-gray-400">Matching</div>
                  </div>
                </div>
              )}

              {/* Filters */}
              <div className="flex flex-wrap gap-3">
                <div className="relative flex-1 min-w-[200px]">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    placeholder={`Search docs (default: ${workspaceSearchTerms || 'all'})...`}
                    value={docsSearch}
                    onChange={(e) => setDocsSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <select
                  value={docsStatusFilter}
                  onChange={(e) => setDocsStatusFilter(e.target.value)}
                  className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
                >
                  <option value="">All Statuses</option>
                  {docsData?.filters?.statuses?.map((status: string) => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
                <select
                  value={docsTypeFilter}
                  onChange={(e) => setDocsTypeFilter(e.target.value)}
                  className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
                >
                  <option value="">All Types</option>
                  {docsData?.filters?.types?.map((type: string) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
                <a
                  href="/docs-index"
                  className="px-3 py-2 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-lg text-sm hover:bg-cyan-500/30 flex items-center gap-1"
                >
                  <ExternalLink size={14} />
                  Full Index
                </a>
              </div>

              {/* Results */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Doc List */}
                <div className="lg:col-span-2 space-y-2">
                  {loadingDocs ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
                    </div>
                  ) : docsData?.documents?.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                      <Book className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No matching documents</p>
                    </div>
                  ) : (
                    docsData?.documents?.map((doc: DocsDocument) => {
                      const isOrphan = doc.inbound_links_count === 0 && doc.outbound_links.length === 0
                      return (
                        <button
                          key={doc.path}
                          onClick={() => setSelectedDocPath(doc.path)}
                          className={cn(
                            'w-full text-left p-3 rounded-lg border transition-all',
                            selectedDocPath === doc.path
                              ? 'bg-cyan-500/10 border-cyan-500/50'
                              : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                          )}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1 flex-wrap">
                                <span className={cn(
                                  'px-1.5 py-0.5 text-xs rounded border',
                                  doc.status === 'active' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                                  doc.status === 'superseded' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                                  doc.status === 'deprecated' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                                  'bg-gray-500/20 text-gray-400 border-gray-500/30'
                                )}>
                                  {doc.status}
                                </span>
                                {doc.type && <span className="text-xs text-purple-400">{doc.type}</span>}
                                {isOrphan && (
                                  <span className="text-xs text-yellow-500 flex items-center gap-1">
                                    <AlertTriangle className="w-3 h-3" />
                                    orphan
                                  </span>
                                )}
                              </div>
                              <h4 className="font-medium text-sm truncate">{doc.title || doc.path.split('/').pop()}</h4>
                              <p className="text-xs text-gray-500 truncate">{doc.path}</p>
                            </div>
                            <div className="flex items-center gap-3 text-xs text-gray-400 flex-shrink-0">
                              <span className="flex items-center gap-1" title="Outbound links">
                                <ArrowRight className="w-3 h-3" />
                                {doc.outbound_links.length}
                              </span>
                              <span className="flex items-center gap-1" title="Inbound links">
                                <Link2 className="w-3 h-3" />
                                {doc.inbound_links_count}
                              </span>
                            </div>
                          </div>
                        </button>
                      )
                    })
                  )}
                </div>

                {/* Doc Detail Panel */}
                <div className="card lg:col-span-1">
                  {selectedDocPath ? (
                    loadingDocDetail ? (
                      <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
                      </div>
                    ) : selectedDocData?.document ? (
                      <div className="space-y-4">
                        <div className="flex items-start justify-between">
                          <h4 className="font-semibold text-sm truncate flex-1">
                            {selectedDocData.document.title || selectedDocData.document.path.split('/').pop()}
                          </h4>
                          <button
                            onClick={() => setSelectedDocPath(null)}
                            className="p-1 hover:bg-gray-700 rounded"
                          >
                            <X className="w-4 h-4 text-gray-400" />
                          </button>
                        </div>
                        <p className="text-xs text-gray-500 break-all">{selectedDocData.document.path}</p>

                        {/* Status & Info */}
                        <div className="flex flex-wrap gap-2">
                          <span className={cn(
                            'px-2 py-0.5 text-xs rounded border',
                            selectedDocData.document.status === 'active' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                            selectedDocData.document.status === 'superseded' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                            'bg-gray-500/20 text-gray-400 border-gray-500/30'
                          )}>
                            {selectedDocData.document.status}
                          </span>
                          <span className="px-2 py-0.5 text-xs rounded border border-gray-600 text-gray-400">
                            {selectedDocData.document.lines} lines
                          </span>
                        </div>

                        {/* Orphan Warning */}
                        {selectedDocData.is_orphan && (
                          <div className="p-2 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400 flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                            <span>Orphan: No inbound or outbound links</span>
                          </div>
                        )}

                        {/* Outbound Links */}
                        <div>
                          <h5 className="text-xs font-medium text-gray-400 mb-2 flex items-center gap-1">
                            <ArrowRight className="w-3 h-3" />
                            Outbound ({selectedDocData.document.outbound_links.length})
                          </h5>
                          <div className="space-y-1 max-h-32 overflow-y-auto">
                            {selectedDocData.document.outbound_links.slice(0, 5).map((link, i) => (
                              <div key={i} className="text-xs p-1.5 bg-gray-800/50 rounded truncate">
                                <span className="text-cyan-400">{link.target}</span>
                                <span className="text-gray-500 ml-1">({link.occurrences}x)</span>
                              </div>
                            ))}
                            {selectedDocData.document.outbound_links.length > 5 && (
                              <p className="text-xs text-gray-500">+{selectedDocData.document.outbound_links.length - 5} more</p>
                            )}
                          </div>
                        </div>

                        {/* Inbound Links */}
                        <div>
                          <h5 className="text-xs font-medium text-gray-400 mb-2 flex items-center gap-1">
                            <Link2 className="w-3 h-3" />
                            Inbound ({selectedDocData.inbound_count})
                          </h5>
                          <div className="space-y-1 max-h-32 overflow-y-auto">
                            {selectedDocData.inbound_links.slice(0, 5).map((link, i) => (
                              <div key={i} className="text-xs p-1.5 bg-gray-800/50 rounded truncate">
                                <span className="text-green-400">{link.title || link.source}</span>
                                <span className="text-gray-500 ml-1">({link.occurrences}x)</span>
                              </div>
                            ))}
                            {selectedDocData.inbound_count > 5 && (
                              <p className="text-xs text-gray-500">+{selectedDocData.inbound_count - 5} more</p>
                            )}
                          </div>
                        </div>

                        {/* Open Full */}
                        <a
                          href={`/docs-index?search=${encodeURIComponent(selectedDocData.document.path)}`}
                          className="block w-full text-center px-3 py-2 bg-cyan-500/20 text-cyan-400 rounded text-sm hover:bg-cyan-500/30"
                        >
                          View in Full Index
                        </a>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <p>Document not found</p>
                      </div>
                    )
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <Book className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">Select a document to view details</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Modals */}
      {showWorkspaceSelector && (
        <WorkspaceSelectorModal
          workspaces={workspaces}
          onSelect={(id) => activateMutation.mutate(id)}
          onClose={() => setShowWorkspaceSelector(false)}
          onCreateNew={() => { setShowWorkspaceSelector(false); setShowRegisterModal(true) }}
        />
      )}

      {showRegisterModal && (
        <RegisterWorkspaceModal
          onClose={() => setShowRegisterModal(false)}
          onSubmit={(data) => registerMutation.mutate(data)}
          isLoading={registerMutation.isPending}
        />
      )}

      {showCommitModal && activeWorkspace && (
        <GitCommitModal
          onClose={() => setShowCommitModal(false)}
          onCommit={(message) => commitMutation.mutate({ id: activeWorkspace.id, message })}
          isLoading={commitMutation.isPending}
          bodyGovernance={canWriteFile}
        />
      )}

      {/* Session 776: Git Branch Modal */}
      {showBranchModal && activeWorkspace && (
        <GitBranchModal
          onClose={() => setShowBranchModal(false)}
          onCreate={(branchName) => createBranchMutation.mutate({ id: activeWorkspace.id, branchName })}
          isLoading={createBranchMutation.isPending}
          bodyGovernance={canWriteFile}
          currentBranch={gitStatus.branch}
        />
      )}

      {/* Session 776: File History Modal */}
      {showFileHistory && selectedFilePath && (
        <FileHistoryModal
          filePath={selectedFilePath}
          operations={(fileHistoryData?.data?.operations || []) as WorkspaceOperation[]}
          isLoading={loadingFileHistory}
          onClose={() => setShowFileHistory(false)}
        />
      )}

      {/* Session 779: File Content Modal - View content of workspace operation outputs */}
      {showFileContent && (
        <FileContentModal
          operation={operationDetailData?.data as OperationDetail | null}
          isLoading={loadingOperationDetail}
          onClose={() => {
            setShowFileContent(false)
            setSelectedOperationId(null)
          }}
        />
      )}

      {/* Toast */}
      {actionResult && <Toast result={actionResult} onClose={() => setActionResult(null)} />}
    </div>
  )
}
