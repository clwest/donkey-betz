/**
 * Session 816: Enhanced Operations Panel for Platform Command Center
 *
 * Complete overhaul of the Operations tab with:
 * - Stats dashboard with summary cards
 * - Enhanced filtering (type, date range, status)
 * - Timeline view with grouping options
 * - Full data display in OperationRow
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { workspaceApi } from '@/lib/api'
import {
  History, Search, Loader2, Filter, Calendar, ChevronDown, ChevronRight,
  CheckCircle, XCircle, Clock, RotateCcw, Eye, FileText, Code, Plus,
  Trash2, GitCommit, GitBranch, File, Terminal, Play, TestTube, Paintbrush,
  Rocket, AlertTriangle, Activity, Users, BarChart3,
  ChevronUp, Copy, Check
} from 'lucide-react'
import { cn } from '@/lib/cn'
import EntityLink from '@/components/EntityLink'

// =============================================================================
// Types
// =============================================================================

interface WorkspaceOperation {
  id: string
  operation_type: string
  file_path: string
  agent_name: string
  agent_task?: string
  description?: string
  success: boolean
  pending_review: boolean
  created_at: string
  diff?: string
  content_before?: string
  content_after?: string
  error_message?: string
  execution_time_ms?: number
  requires_review?: boolean
  reviewed_by_human?: boolean
  human_approved?: boolean | null
  can_rollback?: boolean
  rolled_back?: boolean
  // Command execution fields
  command?: string
  command_output?: string
  command_error?: string
  exit_code?: number
  // File size fields
  file_size_before?: number
  file_size_after?: number
}

interface WorkspaceStats {
  workspace_id: string
  workspace_name: string
  totals: {
    operations: number
    files_written: number
    commits: number
  }
  last_24h: {
    operations: number
    successful: number
    failed: number
  }
  last_7d: {
    operations: number
    by_type: Record<string, number>
    by_agent: Record<string, number>
  }
  pending_reviews: number
  rollback_available: number
}

type GroupBy = 'none' | 'date' | 'agent' | 'type' | 'file'
type DateRange = 'all' | '24h' | '7d' | '30d'

interface OperationsPanelProps {
  workspaceId: string
  operations: WorkspaceOperation[]
  isLoading: boolean
  onRollback: (id: string) => void
  onViewContent: (id: string) => void
  rollbackMutation: { isPending: boolean }
}

// =============================================================================
// Operation Type Helpers
// =============================================================================

const OPERATION_TYPES = [
  { value: 'file_create', label: 'Create File', icon: Plus, color: 'text-green-400' },
  { value: 'file_modify', label: 'Modify File', icon: Code, color: 'text-amber-400' },
  { value: 'file_delete', label: 'Delete File', icon: Trash2, color: 'text-red-400' },
  { value: 'file_rename', label: 'Rename File', icon: FileText, color: 'text-blue-400' },
  { value: 'command_exec', label: 'Run Command', icon: Terminal, color: 'text-purple-400' },
  { value: 'git_commit', label: 'Git Commit', icon: GitCommit, color: 'text-cyan-400' },
  { value: 'git_branch', label: 'Git Branch', icon: GitBranch, color: 'text-cyan-400' },
  { value: 'git_checkout', label: 'Git Checkout', icon: GitBranch, color: 'text-cyan-400' },
  { value: 'git_merge', label: 'Git Merge', icon: GitBranch, color: 'text-cyan-400' },
  { value: 'build_run', label: 'Run Build', icon: Play, color: 'text-orange-400' },
  { value: 'test_run', label: 'Run Tests', icon: TestTube, color: 'text-yellow-400' },
  { value: 'lint_run', label: 'Run Linter', icon: Paintbrush, color: 'text-pink-400' },
  { value: 'deploy', label: 'Deploy', icon: Rocket, color: 'text-emerald-400' },
]

const getOperationType = (type: string) => {
  return OPERATION_TYPES.find(t => t.value === type) || {
    value: type,
    label: type,
    icon: File,
    color: 'text-gray-400'
  }
}

// =============================================================================
// Stats Dashboard Component
// =============================================================================

function OperationsStatsDashboard({ stats, isLoading }: { stats?: WorkspaceStats; isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700 animate-pulse">
            <div className="h-6 w-12 bg-gray-700 rounded mb-1" />
            <div className="h-3 w-16 bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    )
  }

  if (!stats) return null

  const successRate = stats.last_24h.operations > 0
    ? Math.round((stats.last_24h.successful / stats.last_24h.operations) * 100)
    : 100

  const topAgents = Object.entries(stats.last_7d.by_agent || {})
    .sort(([,a], [,b]) => b - a)
    .slice(0, 3)

  const topTypes = Object.entries(stats.last_7d.by_type || {})
    .sort(([,a], [,b]) => b - a)
    .slice(0, 3)

  return (
    <div className="space-y-3 mb-4">
      {/* Main Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {/* Total Operations */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-1">
            <History className="w-4 h-4 text-cyan-400" />
            <span className="text-xl font-bold text-white">{stats.totals.operations}</span>
          </div>
          <div className="text-xs text-gray-400">Total Operations</div>
        </div>

        {/* 24h Operations */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-xl font-bold text-white">{stats.last_24h.operations}</span>
          </div>
          <div className="text-xs text-gray-400">Last 24 Hours</div>
        </div>

        {/* Success Rate */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className={cn("w-4 h-4", successRate >= 90 ? "text-green-400" : successRate >= 70 ? "text-yellow-400" : "text-red-400")} />
            <span className="text-xl font-bold text-white">{successRate}%</span>
          </div>
          <div className="text-xs text-gray-400">Success Rate (24h)</div>
        </div>

        {/* Failed */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-1">
            <XCircle className="w-4 h-4 text-red-400" />
            <span className="text-xl font-bold text-white">{stats.last_24h.failed}</span>
          </div>
          <div className="text-xs text-gray-400">Failed (24h)</div>
        </div>

        {/* Pending Reviews */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className={cn("w-4 h-4", stats.pending_reviews > 0 ? "text-amber-400" : "text-gray-500")} />
            <span className="text-xl font-bold text-white">{stats.pending_reviews}</span>
          </div>
          <div className="text-xs text-gray-400">Pending Review</div>
        </div>

        {/* Rollback Available */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-1">
            <RotateCcw className="w-4 h-4 text-purple-400" />
            <span className="text-xl font-bold text-white">{stats.rollback_available}</span>
          </div>
          <div className="text-xs text-gray-400">Can Rollback</div>
        </div>
      </div>

      {/* Breakdown Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* By Agent (7d) */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-medium text-gray-300">Top Agents (7d)</span>
          </div>
          <div className="space-y-1">
            {topAgents.length > 0 ? topAgents.map(([agent, count]) => (
              <div key={agent} className="flex items-center justify-between text-xs">
                <span className="text-gray-400 truncate max-w-[150px]">{agent}</span>
                <span className="text-white font-medium">{count}</span>
              </div>
            )) : (
              <div className="text-xs text-gray-500">No activity</div>
            )}
          </div>
        </div>

        {/* By Type (7d) */}
        <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-gray-300">By Type (7d)</span>
          </div>
          <div className="space-y-1">
            {topTypes.length > 0 ? topTypes.map(([type, count]) => {
              const opType = getOperationType(type)
              const Icon = opType.icon
              return (
                <div key={type} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5">
                    <Icon className={cn("w-3 h-3", opType.color)} />
                    <span className="text-gray-400">{opType.label}</span>
                  </div>
                  <span className="text-white font-medium">{count}</span>
                </div>
              )
            }) : (
              <div className="text-xs text-gray-500">No activity</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// Enhanced Filters Component
// =============================================================================

interface FiltersProps {
  search: string
  setSearch: (v: string) => void
  typeFilter: string
  setTypeFilter: (v: string) => void
  statusFilter: string
  setStatusFilter: (v: string) => void
  dateRange: DateRange
  setDateRange: (v: DateRange) => void
  groupBy: GroupBy
  setGroupBy: (v: GroupBy) => void
  totalCount: number
  filteredCount: number
}

function OperationsFilters({
  search, setSearch,
  typeFilter, setTypeFilter,
  statusFilter, setStatusFilter,
  dateRange, setDateRange,
  groupBy, setGroupBy,
  totalCount, filteredCount
}: FiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  return (
    <div className="space-y-3 mb-4">
      {/* Primary Row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search file, agent, or task..."
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Type Filter */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
        >
          <option value="">All Types</option>
          {OPERATION_TYPES.map(type => (
            <option key={type.value} value={type.value}>{type.label}</option>
          ))}
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
        >
          <option value="">All Status</option>
          <option value="success">✅ Success</option>
          <option value="failed">❌ Failed</option>
          <option value="pending">⏳ Pending Review</option>
          <option value="rolled_back">↩️ Rolled Back</option>
        </select>

        {/* Advanced Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={cn(
            "px-3 py-2 rounded-lg text-sm flex items-center gap-1.5 border transition-colors",
            showAdvanced
              ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30"
              : "bg-gray-800 text-gray-400 border-gray-700 hover:border-gray-600"
          )}
        >
          <Filter className="w-4 h-4" />
          Advanced
          {showAdvanced ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>

        {/* Count */}
        <span className="text-sm text-gray-400">
          {filteredCount === totalCount ? totalCount : `${filteredCount} / ${totalCount}`} operations
        </span>
      </div>

      {/* Advanced Row */}
      {showAdvanced && (
        <div className="flex flex-wrap items-center gap-3 pl-1 pt-2 border-t border-gray-700/50">
          {/* Date Range */}
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as DateRange)}
              className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyan-500"
            >
              <option value="all">All Time</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>

          {/* Group By */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Group:</span>
            <div className="flex rounded-lg border border-gray-700 overflow-hidden">
              {(['none', 'date', 'agent', 'type'] as GroupBy[]).map(g => (
                <button
                  key={g}
                  onClick={() => setGroupBy(g)}
                  className={cn(
                    "px-2.5 py-1 text-xs transition-colors",
                    groupBy === g
                      ? "bg-cyan-500/20 text-cyan-400"
                      : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                  )}
                >
                  {g === 'none' ? 'List' : g.charAt(0).toUpperCase() + g.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Enhanced Operation Row Component
// =============================================================================

interface EnhancedOperationRowProps {
  operation: WorkspaceOperation
  onRollback?: () => void
  onViewContent?: () => void
  isRollingBack?: boolean
}

function EnhancedOperationRow({ operation, onRollback, onViewContent, isRollingBack }: EnhancedOperationRowProps) {
  const [expanded, setExpanded] = useState(false)
  const [showDiff, setShowDiff] = useState(false)
  const [copied, setCopied] = useState(false)

  const opType = getOperationType(operation.operation_type)
  const Icon = opType.icon

  const isCommandOp = operation.operation_type === 'command_exec'
  const isFileOp = ['file_create', 'file_modify', 'file_delete', 'file_rename'].includes(operation.operation_type)

  // Session 833: Extract readable display name from file path
  const getDisplayInfo = () => {
    if (!operation.file_path) {
      return {
        title: operation.command?.slice(0, 50) || opType.label,
        subtitle: null,
        isMarkdown: false,
      }
    }

    const path = operation.file_path
    const parts = path.split('/')
    const filename = parts.pop() || path
    const directory = parts.join('/') || ''
    const isMarkdown = filename.endsWith('.md')

    // Try to make a human-readable title from the filename
    // e.g., "campaign_plan_quarterly_content_campaign_2026-01-26_18-24.md"
    // becomes "Campaign Plan: Quarterly Content Campaign"
    let title = filename
    if (isMarkdown) {
      // Remove extension and date suffix
      let name = filename.replace(/\.md$/, '').replace(/_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$/, '')
      // Convert snake_case to Title Case
      const words = name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      // Group common patterns
      if (words[0] === 'Campaign' && words[1] === 'Plan') {
        title = `Campaign Plan: ${words.slice(2).join(' ')}`
      } else if (words[0] === 'Research' || words[0] === 'Analysis') {
        title = `${words[0]}: ${words.slice(1).join(' ')}`
      } else {
        title = words.join(' ')
      }
    }

    return {
      title,
      subtitle: directory ? `${directory}/` : null,
      filename,
      isMarkdown,
    }
  }

  const displayInfo = getDisplayInfo()

  // Calculate lines changed for file operations
  const linesChanged = useMemo(() => {
    if (!isFileOp) return null
    const beforeLines = operation.content_before?.split('\n').length || 0
    const afterLines = operation.content_after?.split('\n').length || 0
    return {
      added: Math.max(0, afterLines - beforeLines),
      removed: Math.max(0, beforeLines - afterLines),
      total: Math.abs(afterLines - beforeLines)
    }
  }, [operation, isFileOp])

  // Format file size
  const formatSize = (bytes?: number) => {
    if (!bytes) return null
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={cn(
      "border rounded-lg overflow-hidden transition-all",
      operation.rolled_back
        ? "border-gray-600 bg-gray-800/30 opacity-70"
        : operation.success
          ? "border-gray-700 bg-gray-800/50"
          : "border-red-500/30 bg-red-500/5"
    )}>
      {/* Main Row */}
      <div
        className="p-3 cursor-pointer hover:bg-gray-700/30 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            {/* Expand/Collapse */}
            <button className="text-gray-500 hover:text-gray-300 flex-shrink-0">
              {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>

            {/* Type Icon */}
            <Icon className={cn("w-4 h-4 flex-shrink-0", opType.color)} />

            {/* Main Info - Session 833: Enhanced display */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm text-white">
                  {displayInfo.title}
                </span>
                {displayInfo.isMarkdown && (
                  <span className="text-xs px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400">MD</span>
                )}
                {operation.rolled_back && (
                  <span className="text-xs px-1.5 py-0.5 rounded bg-gray-500/20 text-gray-400 flex items-center gap-1">
                    <RotateCcw className="w-3 h-3" />
                    Rolled Back
                  </span>
                )}
                {linesChanged && linesChanged.total > 0 && (
                  <span className="text-xs text-gray-500">
                    {linesChanged.added > 0 && <span className="text-green-400">+{linesChanged.added}</span>}
                    {linesChanged.added > 0 && linesChanged.removed > 0 && '/'}
                    {linesChanged.removed > 0 && <span className="text-red-400">-{linesChanged.removed}</span>}
                  </span>
                )}
              </div>
              {/* Session 833: Show directory path and agent on separate line */}
              <div className="flex items-center gap-2 text-xs text-gray-500 mt-0.5">
                {displayInfo.subtitle && (
                  <>
                    <span className="truncate max-w-[200px]" title={operation.file_path}>{displayInfo.subtitle}</span>
                    <span>•</span>
                  </>
                )}
                <EntityLink type="agent" id={operation.agent_name} label={operation.agent_name} iconSize={10} className="text-xs" />
                <span>•</span>
                <span>{new Date(operation.created_at).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>

          {/* Status Badges */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {operation.success ? (
              <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Success
              </span>
            ) : (
              <span className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 flex items-center gap-1">
                <XCircle className="w-3 h-3" />
                Failed
              </span>
            )}
            {operation.reviewed_by_human && operation.human_approved === true && (
              <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400">Approved</span>
            )}
            {operation.reviewed_by_human && operation.human_approved === false && (
              <span className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400">Rejected</span>
            )}
            {(operation.requires_review || operation.pending_review) && !operation.reviewed_by_human && (
              <span className="text-xs px-2 py-1 rounded bg-amber-500/20 text-amber-400">Pending Review</span>
            )}
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t border-gray-700/50 p-3 space-y-3 bg-gray-900/30">
          {/* Agent Task */}
          {operation.agent_task && (
            <div>
              <div className="text-xs text-gray-500 mb-1">Task</div>
              <div className="text-sm text-gray-300 bg-gray-800/50 p-2 rounded">{operation.agent_task}</div>
            </div>
          )}

          {/* Description */}
          {operation.description && (
            <div>
              <div className="text-xs text-gray-500 mb-1">Description</div>
              <div className="text-sm text-gray-300">{operation.description}</div>
            </div>
          )}

          {/* Error Message */}
          {!operation.success && operation.error_message && (
            <div className="flex items-start gap-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-400">
              <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{operation.error_message}</span>
            </div>
          )}

          {/* Command Execution Details */}
          {isCommandOp && operation.command && (
            <div className="space-y-2">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-500">Command</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleCopy(operation.command || '') }}
                    className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                  >
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  </button>
                </div>
                <pre className="text-xs bg-gray-800 p-2 rounded overflow-x-auto font-mono text-cyan-400">
                  {operation.command}
                </pre>
              </div>
              {operation.exit_code !== undefined && (
                <div className="text-xs text-gray-400">
                  Exit code: <span className={operation.exit_code === 0 ? "text-green-400" : "text-red-400"}>
                    {operation.exit_code}
                  </span>
                </div>
              )}
              {operation.command_output && (
                <div>
                  <div className="text-xs text-gray-500 mb-1">Output</div>
                  <pre className="text-xs bg-gray-800 p-2 rounded overflow-x-auto max-h-40 overflow-y-auto font-mono text-gray-300">
                    {operation.command_output}
                  </pre>
                </div>
              )}
              {operation.command_error && (
                <div>
                  <div className="text-xs text-gray-500 mb-1">Error Output</div>
                  <pre className="text-xs bg-gray-800 p-2 rounded overflow-x-auto max-h-40 overflow-y-auto font-mono text-red-400">
                    {operation.command_error}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* File Size Info */}
          {isFileOp && (operation.file_size_before || operation.file_size_after) && (
            <div className="flex items-center gap-4 text-xs text-gray-400">
              {operation.file_size_before !== undefined && (
                <span>Before: {formatSize(operation.file_size_before)}</span>
              )}
              {operation.file_size_after !== undefined && (
                <span>After: {formatSize(operation.file_size_after)}</span>
              )}
            </div>
          )}

          {/* Diff Toggle */}
          {operation.diff && (
            <div>
              <button
                onClick={(e) => { e.stopPropagation(); setShowDiff(!showDiff) }}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                <Eye className="w-3 h-3" />
                {showDiff ? 'Hide Diff' : 'Show Diff'}
              </button>
              {showDiff && (
                <pre className="mt-2 text-xs bg-gray-800 p-2 rounded overflow-x-auto max-h-60 overflow-y-auto font-mono">
                  {operation.diff}
                </pre>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-2 border-t border-gray-700/50">
            {onViewContent && operation.success && (
              <button
                onClick={(e) => { e.stopPropagation(); onViewContent() }}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                <FileText className="w-3 h-3" />
                View Content
              </button>
            )}
            {onRollback && operation.success && operation.can_rollback && !operation.rolled_back && (
              <button
                onClick={(e) => { e.stopPropagation(); onRollback() }}
                disabled={isRollingBack}
                className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 disabled:opacity-50"
              >
                <RotateCcw className={cn("w-3 h-3", isRollingBack && "animate-spin")} />
                {isRollingBack ? 'Rolling back...' : 'Rollback'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Grouped Operations View
// =============================================================================

interface GroupedViewProps {
  operations: WorkspaceOperation[]
  groupBy: GroupBy
  onRollback: (id: string) => void
  onViewContent: (id: string) => void
  rollbackMutation: { isPending: boolean }
}

function GroupedOperationsView({ operations, groupBy, onRollback, onViewContent, rollbackMutation }: GroupedViewProps) {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())

  const groups = useMemo(() => {
    if (groupBy === 'none') return null

    const grouped: Record<string, WorkspaceOperation[]> = {}

    operations.forEach(op => {
      let key: string
      switch (groupBy) {
        case 'date':
          key = new Date(op.created_at).toLocaleDateString()
          break
        case 'agent':
          key = op.agent_name
          break
        case 'type':
          key = getOperationType(op.operation_type).label
          break
        case 'file':
          key = op.file_path || 'Commands'
          break
        default:
          key = 'Other'
      }
      if (!grouped[key]) grouped[key] = []
      grouped[key].push(op)
    })

    return Object.entries(grouped).sort(([,a], [,b]) => b.length - a.length)
  }, [operations, groupBy])

  const toggleGroup = (key: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  if (!groups) {
    return (
      <div className="space-y-2">
        {operations.map(op => (
          <EnhancedOperationRow
            key={op.id}
            operation={op}
            onRollback={() => onRollback(op.id)}
            onViewContent={() => onViewContent(op.id)}
            isRollingBack={rollbackMutation.isPending}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {groups.map(([key, ops]) => {
        const isExpanded = expandedGroups.has(key)
        const successCount = ops.filter(o => o.success).length
        const failedCount = ops.length - successCount

        return (
          <div key={key} className="border border-gray-700 rounded-lg overflow-hidden">
            {/* Group Header */}
            <button
              onClick={() => toggleGroup(key)}
              className="w-full px-4 py-3 bg-gray-800/70 hover:bg-gray-800 flex items-center justify-between transition-colors"
            >
              <div className="flex items-center gap-3">
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                )}
                <span className="font-medium text-white">{key}</span>
                <span className="text-sm text-gray-400">({ops.length})</span>
              </div>
              <div className="flex items-center gap-2">
                {successCount > 0 && (
                  <span className="text-xs text-green-400">{successCount} ✓</span>
                )}
                {failedCount > 0 && (
                  <span className="text-xs text-red-400">{failedCount} ✗</span>
                )}
              </div>
            </button>

            {/* Group Content */}
            {isExpanded && (
              <div className="p-3 space-y-2 bg-gray-900/30">
                {ops.map(op => (
                  <EnhancedOperationRow
                    key={op.id}
                    operation={op}
                    onRollback={() => onRollback(op.id)}
                    onViewContent={() => onViewContent(op.id)}
                    isRollingBack={rollbackMutation.isPending}
                  />
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// =============================================================================
// Main Operations Panel Component
// =============================================================================

export function OperationsPanel({
  workspaceId,
  operations,
  isLoading,
  onRollback,
  onViewContent,
  rollbackMutation
}: OperationsPanelProps) {
  // Filter State
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [dateRange, setDateRange] = useState<DateRange>('all')
  const [groupBy, setGroupBy] = useState<GroupBy>('none')

  // Stats Query
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['workspace-stats', workspaceId],
    queryFn: () => workspaceApi.stats(workspaceId),
    enabled: !!workspaceId,
  })

  const stats = statsData?.data as WorkspaceStats | undefined

  // Filter Operations
  const filteredOperations = useMemo(() => {
    let result = [...operations]

    // Search filter
    if (search) {
      const searchLower = search.toLowerCase()
      result = result.filter(op =>
        op.file_path?.toLowerCase().includes(searchLower) ||
        op.agent_name.toLowerCase().includes(searchLower) ||
        op.agent_task?.toLowerCase().includes(searchLower) ||
        op.description?.toLowerCase().includes(searchLower) ||
        op.command?.toLowerCase().includes(searchLower)
      )
    }

    // Type filter
    if (typeFilter) {
      result = result.filter(op => op.operation_type === typeFilter)
    }

    // Status filter
    if (statusFilter) {
      switch (statusFilter) {
        case 'success':
          result = result.filter(op => op.success && !op.rolled_back)
          break
        case 'failed':
          result = result.filter(op => !op.success)
          break
        case 'pending':
          result = result.filter(op => (op.requires_review || op.pending_review) && !op.reviewed_by_human)
          break
        case 'rolled_back':
          result = result.filter(op => op.rolled_back)
          break
      }
    }

    // Date range filter
    if (dateRange !== 'all') {
      const now = new Date()
      let cutoff: Date
      switch (dateRange) {
        case '24h':
          cutoff = new Date(now.getTime() - 24 * 60 * 60 * 1000)
          break
        case '7d':
          cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          break
        case '30d':
          cutoff = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          break
        default:
          cutoff = new Date(0)
      }
      result = result.filter(op => new Date(op.created_at) >= cutoff)
    }

    return result
  }, [operations, search, typeFilter, statusFilter, dateRange])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Stats Dashboard */}
      <OperationsStatsDashboard stats={stats} isLoading={statsLoading} />

      {/* Filters */}
      <OperationsFilters
        search={search}
        setSearch={setSearch}
        typeFilter={typeFilter}
        setTypeFilter={setTypeFilter}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        dateRange={dateRange}
        setDateRange={setDateRange}
        groupBy={groupBy}
        setGroupBy={setGroupBy}
        totalCount={operations.length}
        filteredCount={filteredOperations.length}
      />

      {/* Operations List */}
      {filteredOperations.length > 0 ? (
        <GroupedOperationsView
          operations={filteredOperations}
          groupBy={groupBy}
          onRollback={onRollback}
          onViewContent={onViewContent}
          rollbackMutation={rollbackMutation}
        />
      ) : (
        <div className="text-center py-12 bg-gray-800/30 rounded-lg border border-gray-700">
          <History className="w-12 h-12 mx-auto text-gray-500 mb-3" />
          <p className="text-gray-400 mb-1">No operations found</p>
          <p className="text-xs text-gray-500">
            {operations.length > 0 ? 'Try adjusting your filters' : 'Operations will appear here as agents work'}
          </p>
        </div>
      )}
    </div>
  )
}

export default OperationsPanel
