// Session 1035: Git Tab — workspace git status, commit, branch
// Wraps existing workspaceApi.gitStatus/gitCommit/gitBranch

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  GitBranch,
  GitCommit,
  Loader2,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  FileText,
  Plus,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { workspaceApi } from '@/lib/api'
import type { Workspace } from '../types'

interface GitTabProps {
  activeWorkspace: Workspace
  showSuccess: (msg: string) => void
  showError: (msg: string) => void
}

export function GitTab({ activeWorkspace, showSuccess, showError }: GitTabProps) {
  const queryClient = useQueryClient()
  const [commitMessage, setCommitMessage] = useState('')
  const [newBranch, setNewBranch] = useState('')

  const { data: gitData, isLoading, refetch } = useQuery({
    queryKey: ['workspace-git-status', activeWorkspace.id],
    queryFn: async () => {
      const res = await workspaceApi.gitStatus(activeWorkspace.id)
      return res.data
    },
  })

  const commitMutation = useMutation({
    mutationFn: (data: { message: string }) =>
      workspaceApi.gitCommit(activeWorkspace.id, data),
    onSuccess: () => {
      showSuccess('Committed successfully')
      setCommitMessage('')
      queryClient.invalidateQueries({ queryKey: ['workspace-git-status'] })
    },
    onError: () => showError('Commit failed'),
  })

  const branchMutation = useMutation({
    mutationFn: (data: { branch_name: string; checkout: boolean }) =>
      workspaceApi.gitBranch(activeWorkspace.id, data),
    onSuccess: () => {
      showSuccess('Branch created')
      setNewBranch('')
      queryClient.invalidateQueries({ queryKey: ['workspace-git-status'] })
    },
    onError: () => showError('Failed to create branch'),
  })

  const git = gitData as any

  const isGitRepo = activeWorkspace.is_git_repo ||
    activeWorkspace.workspace_type === 'git_remote' ||
    !!activeWorkspace.git_remote_url

  if (!isGitRepo) {
    return (
      <div className="card text-center py-12">
        <GitBranch size={48} className="mx-auto text-gray-500 mb-4" />
        <h3 className="text-lg font-medium mb-2">Not a Git Repository</h3>
        <p className="text-sm text-gray-400">This workspace is not initialized as a git repository.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <GitBranch size={20} className="text-primary-400" />
          Git Status
        </h2>
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="btn btn-secondary flex items-center gap-2 text-sm"
        >
          {isLoading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          Refresh
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-primary-400" size={32} />
        </div>
      ) : (
        <>
          {/* Branch Info */}
          {git && (
            <div className="card">
              <div className="flex items-center gap-3 mb-4">
                <GitBranch size={18} className="text-primary-400" />
                <span className="text-sm font-medium">Current Branch:</span>
                <span className="text-sm font-mono text-primary-400">
                  {git.branch || git.current_branch || 'unknown'}
                </span>
              </div>

              {/* Status summary */}
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Plus size={14} className="text-accent-green" />
                  <span className="text-gray-400">Staged:</span>
                  <span className="font-medium">{git.staged?.length || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertCircle size={14} className="text-accent-amber" />
                  <span className="text-gray-400">Modified:</span>
                  <span className="font-medium">{git.modified?.length || git.unstaged?.length || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileText size={14} className="text-gray-400" />
                  <span className="text-gray-400">Untracked:</span>
                  <span className="font-medium">{git.untracked?.length || 0}</span>
                </div>
              </div>
            </div>
          )}

          {/* Changed Files */}
          {git && (
            <div className="card">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Changed Files</h3>
              {((git.staged?.length || 0) + (git.modified?.length || git.unstaged?.length || 0) + (git.untracked?.length || 0)) === 0 ? (
                <div className="text-center py-6 text-gray-500">
                  <CheckCircle size={24} className="mx-auto mb-2" />
                  <p className="text-sm">Working tree clean</p>
                </div>
              ) : (
                <div className="space-y-1 max-h-64 overflow-y-auto">
                  {(git.staged || []).map((f: string) => (
                    <FileRow key={`s-${f}`} path={f} status="staged" />
                  ))}
                  {(git.modified || git.unstaged || []).map((f: string) => (
                    <FileRow key={`m-${f}`} path={f} status="modified" />
                  ))}
                  {(git.untracked || []).map((f: string) => (
                    <FileRow key={`u-${f}`} path={f} status="untracked" />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Quick Commit */}
          <div className="card">
            <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
              <GitCommit size={14} />
              Quick Commit
            </h3>
            <div className="flex gap-3">
              <input
                type="text"
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
                placeholder="Commit message..."
                className="flex-1 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && commitMessage.trim()) {
                    commitMutation.mutate({ message: commitMessage.trim() })
                  }
                }}
              />
              <button
                onClick={() => commitMutation.mutate({ message: commitMessage.trim() })}
                disabled={!commitMessage.trim() || commitMutation.isPending}
                className="btn btn-primary flex items-center gap-2 text-sm"
              >
                {commitMutation.isPending ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <GitCommit size={14} />
                )}
                Commit
              </button>
            </div>
          </div>

          {/* Create Branch */}
          <div className="card">
            <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
              <GitBranch size={14} />
              Create Branch
            </h3>
            <div className="flex gap-3">
              <input
                type="text"
                value={newBranch}
                onChange={(e) => setNewBranch(e.target.value)}
                placeholder="Branch name..."
                className="flex-1 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && newBranch.trim()) {
                    branchMutation.mutate({ branch_name: newBranch.trim(), checkout: true })
                  }
                }}
              />
              <button
                onClick={() => branchMutation.mutate({ branch_name: newBranch.trim(), checkout: true })}
                disabled={!newBranch.trim() || branchMutation.isPending}
                className="btn btn-primary flex items-center gap-2 text-sm"
              >
                {branchMutation.isPending ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Plus size={14} />
                )}
                Create & Checkout
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function FileRow({ path, status }: { path: string; status: 'staged' | 'modified' | 'untracked' }) {
  const colors = {
    staged: 'text-accent-green',
    modified: 'text-accent-amber',
    untracked: 'text-gray-400',
  }
  const labels = {
    staged: 'S',
    modified: 'M',
    untracked: '?',
  }

  return (
    <div className="flex items-center gap-2 px-2 py-1.5 rounded text-sm bg-dark-bg">
      <span className={cn('font-mono text-xs w-4 text-center', colors[status])}>
        {labels[status]}
      </span>
      <span className="font-mono text-gray-300 truncate">{path}</span>
    </div>
  )
}
