import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workspaceApi, workspaceOperationsApi } from '@/lib/api'
import {
  FolderOpen, FileCode, GitBranch, History, CheckSquare, Plus,
  RefreshCw, ChevronRight, ChevronDown, File, Folder, Code,
  GitCommit, CheckCircle, XCircle,
  Loader2, Search, RotateCcw, Eye, Clock, Bot, X,
  FolderTree, Activity, Trash2
} from 'lucide-react'
import { cn } from '@/lib/cn'

type WorkspaceTab = 'overview' | 'files' | 'git' | 'operations' | 'reviews'

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
function OperationRow({ operation, onRollback, onReview }: {
  operation: WorkspaceOperation
  onRollback?: () => void
  onReview?: (approved: boolean) => void
}) {
  const [showDiff, setShowDiff] = useState(false)

  const getOperationIcon = (type: string) => {
    switch (type) {
      case 'file_create': return <Plus size={14} className="text-accent-green" />
      case 'file_update': return <Code size={14} className="text-accent-amber" />
      case 'file_delete': return <Trash2 size={14} className="text-accent-red" />
      case 'git_commit': return <GitCommit size={14} className="text-primary-400" />
      default: return <File size={14} className="text-gray-400" />
    }
  }

  return (
    <div className="border border-dark-border rounded-lg p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getOperationIcon(operation.operation_type)}
          <div>
            <p className="text-sm font-medium">{operation.file_path}</p>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Bot size={12} />
              <span>{operation.agent_name}</span>
              <span>•</span>
              <Clock size={12} />
              <span>{new Date(operation.created_at).toLocaleString()}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {operation.success ? (
            <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">Success</span>
          ) : (
            <span className="text-xs px-2 py-1 rounded bg-accent-red/20 text-accent-red">Failed</span>
          )}
          {operation.pending_review && (
            <span className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber">Pending Review</span>
          )}
        </div>
      </div>

      {operation.description && (
        <p className="text-xs text-gray-400">{operation.description}</p>
      )}

      <div className="flex items-center gap-2">
        {operation.diff && (
          <button
            onClick={() => setShowDiff(!showDiff)}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            <Eye size={12} />
            {showDiff ? 'Hide Diff' : 'Show Diff'}
          </button>
        )}
        {onRollback && operation.success && (
          <button
            onClick={onRollback}
            className="text-xs text-accent-amber hover:text-accent-amber/80 flex items-center gap-1"
          >
            <RotateCcw size={12} />
            Rollback
          </button>
        )}
        {onReview && operation.pending_review && (
          <>
            <button
              onClick={() => onReview(true)}
              className="text-xs text-accent-green hover:text-accent-green/80 flex items-center gap-1"
            >
              <CheckCircle size={12} />
              Approve
            </button>
            <button
              onClick={() => onReview(false)}
              className="text-xs text-accent-red hover:text-accent-red/80 flex items-center gap-1"
            >
              <XCircle size={12} />
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

// Register Workspace Modal
function RegisterWorkspaceModal({ onClose, onSubmit, isLoading }: {
  onClose: () => void
  onSubmit: (data: { path: string; name?: string; description?: string }) => void
  isLoading: boolean
}) {
  const [path, setPath] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!path) return
    onSubmit({ path, name: name || undefined, description: description || undefined })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Register Workspace</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Project Path *</label>
            <input
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="/path/to/project"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Name (optional)</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Project"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Description (optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description..."
              rows={2}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none resize-none"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isLoading || !path} className="btn btn-primary flex-1 flex items-center justify-center gap-2">
              {isLoading && <Loader2 size={16} className="animate-spin" />}
              Register
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// Git Commit Modal
function GitCommitModal({ onClose, onCommit, isLoading }: {
  onClose: () => void
  onCommit: (message: string) => void
  isLoading: boolean
}) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim()) return
    onCommit(message)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Create Commit</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>
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
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={isLoading || !message.trim()} className="btn btn-primary flex-1 flex items-center justify-center gap-2">
              {isLoading && <Loader2 size={16} className="animate-spin" />}
              <GitCommit size={16} />
              Commit
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function WorkspacePage() {
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('overview')
  const [showWorkspaceSelector, setShowWorkspaceSelector] = useState(false)
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [showCommitModal, setShowCommitModal] = useState(false)
  const [selectedFilePath, setSelectedFilePath] = useState<string>()
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [operationFilter, setOperationFilter] = useState<string>('')
  const queryClient = useQueryClient()

  // Queries
  const { data: workspacesData, isLoading: loadingWorkspaces, error: workspacesError } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => workspaceApi.list(),
    retry: false, // Don't retry on auth errors
  })

  const { data: activeWorkspaceData } = useQuery({
    queryKey: ['workspace-active'],
    queryFn: () => workspaceApi.getActive(),
    retry: false,
  })

  const { data: dashboardData, isLoading: loadingDashboard } = useQuery({
    queryKey: ['workspace-dashboard'],
    queryFn: () => workspaceApi.dashboard(),
    retry: false,
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

  const registerMutation = useMutation({
    mutationFn: (data: { path: string; name?: string; description?: string }) => workspaceApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      setShowRegisterModal(false)
      setActionResult({ type: 'success', message: 'Workspace registered' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to register workspace' })
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

  const reviewMutation = useMutation({
    mutationFn: ({ id, approved }: { id: string; approved: boolean }) =>
      workspaceOperationsApi.review(id, { approved }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
      setActionResult({ type: 'success', message: 'Review submitted' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to submit review' })
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
  const pendingReviews = (pendingReviewsData?.data?.results || pendingReviewsData?.data || []) as WorkspaceOperation[]
  const dashboard = dashboardData?.data || {}

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
          <h1 className="text-2xl font-bold">Workspace</h1>
          <p className="text-sm text-gray-400 mt-1">SKIN Layer - Agent Project Execution System</p>
        </div>
        <div className="flex items-center gap-3">
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

              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  title="Total Files"
                  value={stats.project?.total_files || dashboard.total_files || 0}
                  icon={File}
                  color="#8b5cf6"
                />
                <StatCard
                  title="Lines of Code"
                  value={stats.project?.total_lines_of_code || dashboard.total_lines || 0}
                  icon={Code}
                  color="#22c55e"
                />
                <StatCard
                  title="Operations (24h)"
                  value={stats.last_24h?.operations || 0}
                  icon={History}
                  color="#f59e0b"
                />
                <StatCard
                  title="Pending Reviews"
                  value={pendingReviews.length}
                  icon={CheckSquare}
                  color="#06b6d4"
                />
              </div>

              {/* Recent Operations */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Recent Operations</h3>
                {operations.length > 0 ? (
                  <div className="space-y-3">
                    {operations.slice(0, 5).map(op => (
                      <OperationRow key={op.id} operation={op} />
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
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* File Tree */}
              <div className="card lg:col-span-1">
                <h3 className="text-lg font-semibold mb-4">Files</h3>
                <div className="max-h-[500px] overflow-y-auto">
                  {files.length > 0 ? (
                    <FileTree files={files} onSelect={setSelectedFilePath} selectedPath={selectedFilePath} />
                  ) : (
                    <p className="text-gray-400 text-sm text-center py-8">No files found</p>
                  )}
                </div>
              </div>

              {/* File Content */}
              <div className="card lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4">
                  {selectedFilePath ? selectedFilePath.split('/').pop() : 'Select a file'}
                </h3>
                {selectedFilePath ? (
                  loadingFileContent ? (
                    <div className="flex items-center justify-center h-64">
                      <Loader2 size={24} className="animate-spin text-primary-400" />
                    </div>
                  ) : (
                    <pre className="text-xs bg-dark-bg p-4 rounded-lg overflow-auto max-h-[500px] font-mono">
                      {fileContentData?.data?.content || 'File is empty or could not be read'}
                    </pre>
                  )
                ) : (
                  <div className="text-gray-400 text-sm text-center py-16">
                    <FileCode size={32} className="mx-auto mb-2 opacity-50" />
                    <p>Select a file from the tree to view its content</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Git Tab */}
          {activeTab === 'git' && (
            <div className="space-y-6">
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
                  className="btn btn-primary flex items-center gap-2"
                >
                  <GitCommit size={16} />
                  New Commit
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
                      <span className="text-sm">Untracked Files</span>
                      <span className="text-sm text-gray-400">{gitStatus.untracked?.length || 0}</span>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Changed Files</h3>
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {(gitStatus.modified || []).map((file: string) => (
                      <div key={file} className="flex items-center gap-2 p-2 bg-dark-bg rounded text-sm">
                        <span className="text-accent-amber">M</span>
                        <span className="font-mono truncate">{file}</span>
                      </div>
                    ))}
                    {(gitStatus.staged || []).map((file: string) => (
                      <div key={file} className="flex items-center gap-2 p-2 bg-dark-bg rounded text-sm">
                        <span className="text-accent-green">A</span>
                        <span className="font-mono truncate">{file}</span>
                      </div>
                    ))}
                    {(!gitStatus.modified?.length && !gitStatus.staged?.length) && (
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
                  {pendingReviews.map(op => (
                    <OperationRow
                      key={op.id}
                      operation={op}
                      onReview={(approved) => reviewMutation.mutate({ id: op.id, approved })}
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
        />
      )}

      {/* Toast */}
      {actionResult && <Toast result={actionResult} onClose={() => setActionResult(null)} />}
    </div>
  )
}
