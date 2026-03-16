// Session 825: Files Tab
// Session 826: Implemented real file browser with git status
// Session 826: Fixed issues from CodeReviewAgent:
//   - Reset state on workspace change
//   - Use Sets for O(1) git status lookups
//   - Refresh all queries (files, git, stats)
//   - Add error handling UI
// Extracted from WorkspacePage.tsx for modular architecture

import { useState, useEffect, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
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

export function FilesTab({ activeWorkspaceId }: FilesTabProps) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set(['src', 'core']))
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  // Session 826 Fix: Reset state when workspace changes
  useEffect(() => {
    setSelectedFile(null)
    setExpandedDirs(new Set(['src', 'core']))
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
    data: statsData,
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

  const files: FileNode[] = filesData?.tree || filesData?.files || []
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
