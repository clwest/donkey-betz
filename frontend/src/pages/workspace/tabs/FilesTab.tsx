// Session 825: Files Tab
// Session 826: Implemented real file browser with git status
// Session 826: Fixed issues from CodeReviewAgent:
//   - Reset state on workspace change
//   - Use Sets for O(1) git status lookups
//   - Refresh all queries (files, git, stats)
//   - Add error handling UI
// Extracted from WorkspacePage.tsx for modular architecture

import { useState, useEffect, useMemo } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  FolderTree,
  FileText,
  GitBranch,
  CheckCircle,
  AlertCircle,
  Loader2,
  ChevronRight,
  ChevronDown,
  File,
  Folder,
  RefreshCw,
  Code,
  XCircle,
  Eye,
  Pencil,
  Save,
  History,
  FileCode2,
  AlertTriangle,
  Check,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { workspaceApi } from '@/lib/api'

interface FilesTabProps {
  activeWorkspaceId?: string
}

interface FileNode {
  name: string
  path: string
  type: 'file' | 'directory'
  children?: FileNode[]
  extension?: string
}

interface WorkspaceFileHistoryEntry {
  id: string
  agent_name?: string
  operation_type?: string
  success?: boolean
  created_at?: string
  file_path?: string
}

const TEXT_FILE_EXTENSIONS = new Set([
  'ts', 'tsx', 'js', 'jsx', 'mjs', 'cjs',
  'json', 'md', 'mdx', 'txt', 'yml', 'yaml',
  'py', 'html', 'css', 'scss', 'sass', 'less',
  'xml', 'svg', 'sql', 'env', 'ini', 'toml',
  'sh', 'bash', 'zsh', 'rb', 'go', 'rs',
  'java', 'kt', 'swift', 'php', 'graphql',
  'prisma', 'yaml', 'lock', 'cfg', 'conf',
  'dockerfile', 'gitignore', 'env.example',
])

function getFileExtension(path: string) {
  const fileName = path.split('/').pop() || path
  const lower = fileName.toLowerCase()
  if (lower === 'dockerfile' || lower === '.gitignore' || lower.startsWith('.env')) {
    return lower
  }
  const parts = fileName.split('.')
  return parts.length > 1 ? parts.pop()?.toLowerCase() || '' : ''
}

function isTextFilePath(path: string) {
  const ext = getFileExtension(path)
  return TEXT_FILE_EXTENSIONS.has(ext)
}

function formatTimestamp(value?: string) {
  if (!value) return 'Unknown'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function findNodeByPath(nodes: FileNode[], targetPath: string): FileNode | undefined {
  for (const node of nodes) {
    if (node.path === targetPath) return node
    if (node.children) {
      const found = findNodeByPath(node.children, targetPath)
      if (found) return found
    }
  }
  return undefined
}

export function FilesTab({ activeWorkspaceId }: FilesTabProps) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set(['src', 'core']))
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [draftContent, setDraftContent] = useState('')

  // Session 826 Fix: Reset state when workspace changes
  useEffect(() => {
    setSelectedFile(null)
    setExpandedDirs(new Set(['src', 'core']))
    setIsEditing(false)
    setDraftContent('')
  }, [activeWorkspaceId])

  // Fetch file tree
  const {
    data: filesData,
    isLoading: filesLoading,
    isFetching: filesFetching,
    error: filesError,
    refetch: refetchFiles,
  } = useQuery({
    queryKey: ['workspace-files', activeWorkspaceId],
    queryFn: async () => {
      if (!activeWorkspaceId) return null
      const res = await workspaceApi.files(activeWorkspaceId)
      return res.data
    },
    enabled: !!activeWorkspaceId,
  })

  // Fetch git status
  const {
    data: gitData,
    isLoading: gitLoading,
    isFetching: gitFetching,
    error: gitError,
    refetch: refetchGit,
  } = useQuery({
    queryKey: ['workspace-git-status', activeWorkspaceId],
    queryFn: async () => {
      if (!activeWorkspaceId) return null
      const res = await workspaceApi.gitStatus(activeWorkspaceId)
      return res.data
    },
    enabled: !!activeWorkspaceId,
  })

  // Fetch workspace stats
  const {
    isFetching: statsFetching,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ['workspace-stats', activeWorkspaceId],
    queryFn: async () => {
      if (!activeWorkspaceId) return null
      const res = await workspaceApi.stats(activeWorkspaceId)
      return res.data
    },
    enabled: !!activeWorkspaceId,
  })

  // Session 826 Fix: Combined fetching state for refresh button
  const isRefreshing = filesFetching || gitFetching || statsFetching

  // Session 826 Fix: Refresh all queries
  const refreshAll = async () => {
    await Promise.all([refetchFiles(), refetchGit(), refetchStats()])
  }

  // Session 826 Fix: Convert arrays to Sets for O(1) lookups
  const gitStatus = gitData || { branch: 'main', modified: [], untracked: [], staged: [] }
  const modifiedSet = useMemo(() => new Set(gitStatus.modified || []), [gitStatus.modified])
  const untrackedSet = useMemo(() => new Set(gitStatus.untracked || []), [gitStatus.untracked])
  const stagedSet = useMemo(() => new Set(gitStatus.staged || []), [gitStatus.staged])
  const files: FileNode[] = filesData?.tree || filesData?.files || []
  const selectedNode = selectedFile ? findNodeByPath(files, selectedFile) : undefined
  const selectedFileExtension = selectedFile ? (selectedNode?.extension || getFileExtension(selectedFile)) : ''
  const selectedFileIsText = selectedFile ? isTextFilePath(selectedFile) : false

  const {
    data: selectedFileData,
    isLoading: selectedFileLoading,
    isFetching: selectedFileFetching,
    error: selectedFileError,
    refetch: refetchSelectedFile,
  } = useQuery({
    queryKey: ['workspace-file-detail', activeWorkspaceId, selectedFile],
    queryFn: async () => {
      if (!activeWorkspaceId || !selectedFile) return null
      const res = await workspaceApi.readFile(activeWorkspaceId, selectedFile)
      return res.data as {
        workspace_id: string
        path: string
        content: string
        size?: number
        truncated?: boolean
      }
    },
    enabled: !!activeWorkspaceId && !!selectedFile,
  })

  const {
    data: fileHistoryData,
    isLoading: fileHistoryLoading,
    isFetching: fileHistoryFetching,
    error: fileHistoryError,
    refetch: refetchFileHistory,
  } = useQuery({
    queryKey: ['workspace-file-history', activeWorkspaceId, selectedFile],
    queryFn: async () => {
      if (!activeWorkspaceId || !selectedFile) return null
      const res = await workspaceApi.fileHistory(activeWorkspaceId, selectedFile)
      return res.data as {
        workspace_id: string
        file_path: string
        total_operations: number
        operations: WorkspaceFileHistoryEntry[]
      }
    },
    enabled: !!activeWorkspaceId && !!selectedFile,
  })

  const writeMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!activeWorkspaceId || !selectedFile) {
        throw new Error('No file selected')
      }
      return workspaceApi.writeFile(activeWorkspaceId, {
        path: selectedFile,
        content,
        agent: 'WebUI',
        description: 'Edited from workspace Files tab',
      })
    },
    onSuccess: async () => {
      setIsEditing(false)
      await Promise.all([
        refetchSelectedFile(),
        refetchFileHistory(),
        refreshAll(),
      ])
    },
  })

  useEffect(() => {
    if (selectedFileData?.content !== undefined && !isEditing) {
      setDraftContent(selectedFileData.content)
    }
  }, [selectedFileData?.content, isEditing])

  useEffect(() => {
    setIsEditing(false)
    setDraftContent('')
  }, [selectedFile])

  if (!activeWorkspaceId) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="h-16 w-16 rounded-full bg-dark-border flex items-center justify-center mb-4">
            <FolderTree size={32} className="text-gray-400" />
          </div>
          <h3 className="font-semibold text-lg">No Workspace Selected</h3>
          <p className="text-sm text-gray-400 mt-1">
            Select a workspace to browse files.
          </p>
        </div>
      </div>
    )
  }

  if (filesLoading || gitLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  // Session 826 Fix: Show error state
  if (filesError || gitError) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="h-16 w-16 rounded-full bg-red-500/20 flex items-center justify-center mb-4">
            <XCircle size={32} className="text-red-400" />
          </div>
          <h3 className="font-semibold text-lg">Failed to Load Workspace</h3>
          <p className="text-sm text-gray-400 mt-1">
            {(filesError as Error)?.message || (gitError as Error)?.message || 'Unknown error'}
          </p>
          <button
            type="button"
            onClick={() => refreshAll()}
            className="btn btn-secondary mt-4"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  const stats = filesData ? {
    total_files: filesData.total_files || 0,
    total_lines: 0,
    languages: {},
  } : { total_files: 0, total_lines: 0, languages: {} }

  const toggleDir = (path: string) => {
    setExpandedDirs((prev) => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  const getFileIcon = (file: FileNode) => {
    if (file.type === 'directory') {
      return expandedDirs.has(file.path) ? (
        <ChevronDown size={14} className="text-gray-500" />
      ) : (
        <ChevronRight size={14} className="text-gray-500" />
      )
    }

    // Get color based on extension
    const ext = file.extension?.toLowerCase() || ''
    const colors: Record<string, string> = {
      ts: 'text-blue-400',
      tsx: 'text-blue-400',
      js: 'text-yellow-400',
      jsx: 'text-yellow-400',
      py: 'text-green-400',
      json: 'text-amber-400',
      css: 'text-pink-400',
      md: 'text-gray-400',
    }

    return <File size={14} className={colors[ext] || 'text-gray-400'} />
  }

  const renderFileTree = (nodes: FileNode[], depth = 0) => {
    return nodes.map((node) => {
      const isExpanded = expandedDirs.has(node.path)
      // Session 826 Fix: O(1) Set lookups instead of O(n) array includes
      const isModified = modifiedSet.has(node.path)
      const isUntracked = untrackedSet.has(node.path)
      const isStaged = stagedSet.has(node.path)

      return (
        <div key={node.path}>
          <button
            type="button"
            onClick={() => {
              if (node.type === 'directory') {
                toggleDir(node.path)
              } else {
                setSelectedFile(node.path)
              }
            }}
            className={cn(
              'flex items-center gap-2 w-full py-1 px-2 rounded text-sm hover:bg-gray-800 transition-colors',
              selectedFile === node.path && 'bg-primary-500/20 text-primary-400'
            )}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
          >
            {node.type === 'directory' ? (
              <>
                {getFileIcon(node)}
                <Folder size={14} className="text-amber-400" />
              </>
            ) : (
              getFileIcon(node)
            )}
            <span className="flex-1 text-left truncate">{node.name}</span>
            {isModified && <span className="text-amber-400 text-xs">M</span>}
            {isUntracked && <span className="text-green-400 text-xs">U</span>}
            {isStaged && <span className="text-blue-400 text-xs">S</span>}
          </button>
          {node.type === 'directory' && isExpanded && node.children && (
            renderFileTree(node.children, depth + 1)
          )}
        </div>
      )
    })
  }

  return (
    <div className="space-y-4">
      {/* Header with stats */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-semibold">File Browser</h3>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <GitBranch size={14} />
            <span>{gitStatus.branch || 'main'}</span>
          </div>
        </div>
        <button
          type="button"
          onClick={refreshAll}
          disabled={isRefreshing}
          className="btn btn-secondary flex items-center gap-2 text-sm"
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <FileText size={14} className="text-primary-400" />
            <span className="text-xs text-gray-500">Files</span>
          </div>
          <div className="text-xl font-bold">{stats.total_files || files.length}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <Code size={14} className="text-accent-green" />
            <span className="text-xs text-gray-500">Lines</span>
          </div>
          <div className="text-xl font-bold">{(stats.total_lines || 0).toLocaleString()}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircle size={14} className="text-accent-amber" />
            <span className="text-xs text-gray-500">Modified</span>
          </div>
          <div className="text-xl font-bold">{gitStatus.modified?.length || 0}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle size={14} className="text-accent-cyan" />
            <span className="text-xs text-gray-500">Staged</span>
          </div>
          <div className="text-xl font-bold">{gitStatus.staged?.length || 0}</div>
        </div>
      </div>

      {/* File Tree */}
      <div className="card max-h-96 overflow-y-auto">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Project Files</h4>
        {files.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <FolderTree className="mx-auto mb-2" size={24} />
            <p className="text-sm">No files found</p>
            <p className="text-xs text-gray-600 mt-1">
              Run a workspace scan to index files
            </p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {renderFileTree(files)}
          </div>
        )}
      </div>

      {/* File Preview and History */}
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
        <div className="card min-h-[28rem] flex flex-col">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-2">
              <Eye size={14} className="text-primary-400" />
              <h4 className="text-sm font-medium text-gray-300">File Preview</h4>
            </div>
            {selectedFile && selectedFileIsText && !isEditing && (
              <button
                type="button"
                onClick={() => {
                  setDraftContent(selectedFileData?.content || '')
                  setIsEditing(true)
                }}
                disabled={selectedFileLoading || !!selectedFileError}
                className="btn btn-secondary flex items-center gap-2 text-xs"
              >
                <Pencil size={12} />
                Edit
              </button>
            )}
          </div>

          {!selectedFile ? (
            <div className="flex flex-1 items-center justify-center text-center text-gray-500 py-12">
              <div>
                <FileCode2 size={32} className="mx-auto mb-3 text-gray-600" />
                <p className="text-sm">Select a file to preview its contents.</p>
              </div>
            </div>
          ) : selectedFileLoading || selectedFileFetching ? (
            <div className="flex flex-1 items-center justify-center py-12">
              <Loader2 className="animate-spin text-primary-400" size={24} />
            </div>
          ) : selectedFileError ? (
            <div className="flex flex-1 items-center justify-center text-center py-12">
              <div>
                <XCircle size={32} className="mx-auto mb-3 text-red-400" />
                <p className="text-sm text-red-300">
                  {(selectedFileError as Error)?.message || 'Failed to load file'}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-1 flex-col gap-3">
              <div className="rounded-lg border border-dark-border bg-dark-bg/60 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-xs uppercase tracking-wide text-gray-500">Selected File</p>
                    <p className="truncate font-mono text-sm text-gray-200">{selectedFile}</p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <span>{selectedFileExtension || 'no extension'}</span>
                    {selectedFileData?.truncated && (
                      <span className="rounded bg-amber-500/15 px-2 py-1 text-amber-300">
                        Truncated
                      </span>
                    )}
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
                  <span>Size: {(selectedFileData?.size || 0).toLocaleString()} chars</span>
                  <span>Workspace edits stay scoped to this workspace.</span>
                </div>
              </div>

              {isEditing ? (
                <div className="flex flex-1 flex-col gap-3">
                  <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-200">
                    <div className="flex items-start gap-2">
                      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                      <div className="space-y-1">
                        <p>Edits are scoped to this workspace and may affect git status.</p>
                        <p>Review your changes before saving or committing.</p>
                      </div>
                    </div>
                  </div>
                  <textarea
                    value={draftContent}
                    onChange={(e) => setDraftContent(e.target.value)}
                    className="min-h-[22rem] w-full flex-1 rounded-lg border border-dark-border bg-dark-bg/90 p-3 font-mono text-sm text-gray-100 outline-none ring-0 focus:border-primary-500"
                    spellCheck={false}
                    aria-label="Workspace file editor"
                  />
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-xs text-gray-500">
                      Saving will write the file in the active workspace and may create a new workspace operation.
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          setIsEditing(false)
                          setDraftContent(selectedFileData?.content || '')
                        }}
                        className="btn btn-secondary text-xs"
                        disabled={writeMutation.isPending}
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={() => writeMutation.mutate(draftContent)}
                        className="btn btn-primary flex items-center gap-2 text-xs"
                        disabled={writeMutation.isPending}
                      >
                        {writeMutation.isPending ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />}
                        Save
                      </button>
                    </div>
                  </div>
                  {writeMutation.isError && (
                    <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-200">
                      {(writeMutation.error as Error)?.message || 'Failed to save file'}
                    </div>
                  )}
                  {writeMutation.isSuccess && (
                    <div className="rounded-lg border border-green-500/30 bg-green-500/10 px-3 py-2 text-xs text-green-200">
                      <div className="flex items-center gap-2">
                        <Check size={12} />
                        <span>
                          Saved successfully. Refresh the preview or git status if you want to review the change.
                        </span>
                      </div>
                      {writeMutation.data?.data?.operation_id && (
                        <p className="mt-1 font-mono text-[11px] text-green-100/80">
                          Operation ID: {writeMutation.data.data.operation_id}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <>
                  <div className="flex-1 rounded-lg border border-dark-border bg-dark-bg/80 p-3">
                    <pre className="max-h-[22rem] overflow-auto whitespace-pre-wrap break-words font-mono text-sm leading-6 text-gray-200">
                      {selectedFileData?.content || ''}
                    </pre>
                  </div>
                  <div className="flex items-center justify-between gap-3 text-xs text-gray-500">
                    <span>
                      {selectedFileData?.truncated ? 'Preview truncated for large file.' : 'Full file content loaded.'}
                    </span>
                    {selectedFileIsText ? (
                      <span className="inline-flex items-center gap-1 text-green-300">
                        <Check size={12} />
                        Editable text file
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-300">
                        <AlertTriangle size={12} />
                        Preview only
                      </span>
                    )}
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        <div className="card min-h-[28rem] flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <History size={14} className="text-primary-400" />
            <h4 className="text-sm font-medium text-gray-300">File History</h4>
          </div>

          {!selectedFile ? (
            <div className="flex flex-1 items-center justify-center text-center text-gray-500 py-12">
              <div>
                <History size={32} className="mx-auto mb-3 text-gray-600" />
                <p className="text-sm">Select a file to see recent operations.</p>
              </div>
            </div>
          ) : fileHistoryLoading || fileHistoryFetching ? (
            <div className="flex flex-1 items-center justify-center py-12">
              <Loader2 className="animate-spin text-primary-400" size={24} />
            </div>
          ) : fileHistoryError ? (
            <div className="flex flex-1 items-center justify-center text-center py-12">
              <div>
                <XCircle size={32} className="mx-auto mb-3 text-red-400" />
                <p className="text-sm text-red-300">
                  {(fileHistoryError as Error)?.message || 'Failed to load file history'}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex-1 space-y-2 overflow-auto pr-1">
              {((fileHistoryData?.operations || []) as WorkspaceFileHistoryEntry[]).length === 0 ? (
                <div className="rounded-lg border border-dashed border-dark-border px-3 py-6 text-center text-sm text-gray-500">
                  No history yet for this file.
                </div>
              ) : (
                (fileHistoryData?.operations || []).map((op) => (
                  <div
                    key={op.id}
                    className={cn(
                      'rounded-lg border px-3 py-3 text-sm',
                      op.success ? 'border-green-500/20 bg-green-500/5' : 'border-red-500/20 bg-red-500/5'
                    )}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium text-gray-100">
                          {op.operation_type || 'operation'}
                        </p>
                        <p className="mt-0.5 text-xs text-gray-400">
                          {op.agent_name || 'Unknown agent'}
                        </p>
                      </div>
                      <span
                        className={cn(
                          'rounded-full px-2 py-1 text-[11px] font-medium',
                          op.success ? 'bg-green-500/15 text-green-300' : 'bg-red-500/15 text-red-300'
                        )}
                      >
                        {op.success ? 'Success' : 'Failed'}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center justify-between gap-3 text-xs text-gray-500">
                      <span className="truncate">Path: {op.file_path || selectedFile}</span>
                      <span>{formatTimestamp(op.created_at)}</span>
                    </div>
                  </div>
                ))
              )}
              <div className="rounded-lg border border-dark-border bg-dark-bg/60 px-3 py-3 text-xs text-gray-500">
                <p className="flex items-center gap-2 text-gray-300">
                  <AlertTriangle size={12} className="text-amber-300" />
                  File history is scoped to this workspace and reflects saved workspace operations.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Git Changes */}
      {(gitStatus.modified?.length > 0 || gitStatus.untracked?.length > 0) && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Pending Changes</h4>
          <div className="space-y-2">
            {gitStatus.modified?.slice(0, 5).map((file: string) => (
              <div key={file} className="flex items-center gap-2 text-sm">
                <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 text-xs">M</span>
                <span className="text-gray-300 truncate">{file}</span>
              </div>
            ))}
            {gitStatus.untracked?.slice(0, 5).map((file: string) => (
              <div key={file} className="flex items-center gap-2 text-sm">
                <span className="px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 text-xs">U</span>
                <span className="text-gray-300 truncate">{file}</span>
              </div>
            ))}
            {((gitStatus.modified?.length || 0) + (gitStatus.untracked?.length || 0)) > 10 && (
              <p className="text-xs text-gray-500">
                And {(gitStatus.modified?.length || 0) + (gitStatus.untracked?.length || 0) - 10} more...
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
