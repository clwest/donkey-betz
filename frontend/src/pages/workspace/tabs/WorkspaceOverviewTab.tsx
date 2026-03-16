// Session 1035: Workspace Overview Tab — default landing for refocused /workspace
// Shows workspace info, stats, recent operations, quick actions

import { useQuery } from '@tanstack/react-query'
import {
  FolderOpen,
  GitBranch,
  FileText,
  History,
  Code,
  RefreshCw,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  FolderTree,
  Activity,
  ExternalLink,
  Rocket,
} from 'lucide-react'
import { workspaceApi, workspaceOperationsApi } from '@/lib/api'
import type { Workspace, WorkspaceTab } from '../types'

interface WorkspaceOverviewTabProps {
  activeWorkspace: Workspace
  onNavigateTab: (tab: WorkspaceTab) => void
  onScan: () => void
  isScanPending: boolean
}

export function WorkspaceOverviewTab({
  activeWorkspace,
  onNavigateTab,
  onScan,
  isScanPending,
}: WorkspaceOverviewTabProps) {
  // Workspace detail (includes scan context with files/LOC)
  const { data: detailData, isLoading: loadingStats } = useQuery({
    queryKey: ['workspace-detail', activeWorkspace.id],
    queryFn: async () => {
      const res = await workspaceApi.detail(activeWorkspace.id)
      return res.data
    },
  })

  // Recent operations — filtered by workspace ID
  const { data: opsData, isLoading: loadingOps } = useQuery({
    queryKey: ['workspace-operations-recent', activeWorkspace.id],
    queryFn: async () => {
      const res = await workspaceOperationsApi.list({ workspace: activeWorkspace.id } as any)
      return res.data
    },
  })

  // Build stats from workspace detail (scan context)
  const detail = detailData as any
  const stats = detail?.context ? {
    total_files: detail.context.total_files,
    total_lines_of_code: detail.context.total_lines_of_code,
    operations_count: detail.total_operations || activeWorkspace.stats?.operations_count,
  } : activeWorkspace.stats || null
  const operations = ((opsData as any)?.results || opsData || []).slice(0, 10)

  // Extract tech stack info
  const techStack = activeWorkspace.tech_stack || activeWorkspace.context?.dependencies || {}
  const techStackEntries = Object.entries(techStack).slice(0, 6)

  return (
    <div className="space-y-6">
      {/* Workspace Info Card */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <FolderOpen className="text-primary-400" size={24} />
            </div>
            <div>
              <h2 className="text-lg font-semibold">{activeWorkspace.name}</h2>
              <p className="text-sm text-gray-400 font-mono">{activeWorkspace.path}</p>
              <div className="flex items-center gap-3 mt-1">
                {activeWorkspace.workspace_type && (
                  <span className="text-xs px-2 py-0.5 rounded bg-primary-500/10 text-primary-400">
                    {activeWorkspace.workspace_type}
                  </span>
                )}
                {activeWorkspace.is_git_repo && (
                  <span className="flex items-center gap-1 text-xs text-gray-400">
                    <GitBranch size={12} /> Git repo
                  </span>
                )}
                {(activeWorkspace as any).git_remote_url && (
                  <a
                    href={(activeWorkspace as any).git_remote_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-primary-400 hover:underline"
                  >
                    <ExternalLink size={12} /> GitHub
                  </a>
                )}
              </div>
            </div>
          </div>
          {activeWorkspace.description && (
            <p className="text-sm text-gray-400 max-w-sm text-right">{activeWorkspace.description}</p>
          )}
        </div>

        {/* Tech stack tags */}
        {techStackEntries.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-dark-border">
            {techStackEntries.map(([key, val]) => (
              <span
                key={key}
                className="text-xs px-2 py-1 rounded bg-dark-bg text-gray-300"
              >
                {key}{typeof val === 'string' && val ? `: ${val}` : ''}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Files"
          value={stats?.total_files ?? activeWorkspace.stats?.total_files ?? '-'}
          icon={FileText}
          loading={loadingStats}
        />
        <StatCard
          label="Lines of Code"
          value={stats?.total_lines_of_code ?? activeWorkspace.stats?.total_lines_of_code ?? '-'}
          icon={Code}
          loading={loadingStats}
          formatNumber
        />
        <StatCard
          label="Operations"
          value={stats?.operations_count ?? activeWorkspace.stats?.operations_count ?? '-'}
          icon={History}
          loading={loadingStats}
        />
        <StatCard
          label="Last Scanned"
          value={activeWorkspace.context?.last_scanned_at
            ? new Date(activeWorkspace.context.last_scanned_at).toLocaleDateString()
            : 'Never'}
          icon={RefreshCw}
          loading={false}
        />
      </div>

      {/* Quick Actions + Recent Ops side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="card">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button
              onClick={onScan}
              disabled={isScanPending}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors text-left"
            >
              {isScanPending ? (
                <Loader2 size={16} className="animate-spin text-primary-400" />
              ) : (
                <RefreshCw size={16} className="text-primary-400" />
              )}
              <span className="text-sm">Scan Workspace</span>
            </button>
            <button
              onClick={() => onNavigateTab('files')}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors text-left"
            >
              <FolderTree size={16} className="text-accent-amber" />
              <span className="text-sm">Browse Files</span>
            </button>
            <button
              onClick={() => onNavigateTab('git')}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors text-left"
            >
              <GitBranch size={16} className="text-accent-green" />
              <span className="text-sm">Git Status</span>
            </button>
            <button
              onClick={() => onNavigateTab('operations')}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors text-left"
            >
              <History size={16} className="text-blue-400" />
              <span className="text-sm">View All Operations</span>
            </button>
            <button
              onClick={() => onNavigateTab('triggers')}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors text-left"
            >
              <Zap size={16} className="text-purple-400" />
              <span className="text-sm">Manage Triggers</span>
            </button>
            <button
              onClick={() => onNavigateTab('launchpad')}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-green-500/10 hover:bg-green-500/20 transition-colors text-left border border-green-500/20"
            >
              <Rocket size={16} className="text-green-400" />
              <span className="text-sm font-medium text-green-400">Launchpad — Deploy & Preview</span>
            </button>
          </div>
        </div>

        {/* Recent Operations */}
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-400">Recent Operations</h3>
            <button
              onClick={() => onNavigateTab('operations')}
              className="text-xs text-primary-400 hover:text-primary-300"
            >
              View all
            </button>
          </div>

          {loadingOps ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="animate-spin text-primary-400" size={24} />
            </div>
          ) : operations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Activity size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">No operations yet</p>
            </div>
          ) : (
            <div className="space-y-1.5">
              {operations.map((op: any) => (
                <div
                  key={op.id}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg bg-dark-bg text-sm"
                >
                  {op.success ? (
                    <CheckCircle size={14} className="text-accent-green flex-shrink-0" />
                  ) : (
                    <XCircle size={14} className="text-accent-red flex-shrink-0" />
                  )}
                  <span className="flex-1 truncate text-gray-300">
                    {op.operation_type}: {op.file_path?.split('/').pop() || op.description || 'Operation'}
                  </span>
                  <span className="text-xs text-gray-500 flex-shrink-0">
                    {op.agent_name}
                  </span>
                  <span className="text-xs text-gray-600 flex-shrink-0">
                    <Clock size={10} className="inline mr-1" />
                    {new Date(op.created_at).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Simple stat card component
function StatCard({
  label,
  value,
  icon: Icon,
  loading,
  formatNumber,
}: {
  label: string
  value: string | number
  icon: React.ComponentType<any>
  loading: boolean
  formatNumber?: boolean
}) {
  const displayValue = formatNumber && typeof value === 'number'
    ? value.toLocaleString()
    : value

  return (
    <div className="card flex items-center gap-3">
      <div className="h-10 w-10 rounded-lg bg-primary-500/10 flex items-center justify-center flex-shrink-0">
        <Icon size={18} className="text-primary-400" />
      </div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        {loading ? (
          <div className="h-5 w-12 bg-dark-border rounded animate-pulse mt-0.5" />
        ) : (
          <p className="text-lg font-semibold">{displayValue}</p>
        )}
      </div>
    </div>
  )
}
