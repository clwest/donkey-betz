// Session 825: Operations Tab
// Extracted from WorkspacePage.tsx for modular architecture
// Session 834: Added grouped view to link related operations

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Search,
  Loader2,
  History,
  ChevronDown,
  ChevronRight,
  Layers,
  List,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Bot,
} from 'lucide-react'
import { workspaceApi, workspaceOperationsApi } from '@/lib/api'
import { OperationCard } from '../components/OperationCard'
import { cn } from '@/lib/cn'
import type { Workspace, WorkspaceOperation } from '../types'

interface OperationsTabProps {
  activeWorkspace: Workspace | undefined
  onViewFileContent: (operationId: string) => void
  showSuccess: (message: string) => void
  showError: (message: string) => void
}

// Session 835: Group operations by directory path for better organization
interface OperationGroup {
  groupKey: string
  displayName: string
  category: string // Top-level category (financial, content, campaigns, etc.)
  operations: WorkspaceOperation[]
  agents: string[]
  totalSuccess: number
  totalFailed: number
  latestTime: string
  earliestTime: string
}

// Extract directory path from file_path for grouping
function getGroupKey(op: WorkspaceOperation): string {
  if (!op.file_path) {
    // Fall back to agent name for operations without file paths
    return `agent/${op.agent_name.toLowerCase().replace(/\s+/g, '_')}`
  }

  // Extract directory path (e.g., "financial/stocks" from "financial/stocks/report_xyz.md")
  const parts = op.file_path.split('/')
  if (parts.length <= 1) {
    return 'root'
  }

  // Use first 2 levels of directory for grouping
  // e.g., "financial/stocks", "content/podcasts", "campaigns/orchestration"
  return parts.slice(0, Math.min(2, parts.length - 1)).join('/')
}

// Format directory path into readable display name
function formatGroupName(groupKey: string): { displayName: string; category: string } {
  if (groupKey === 'root') {
    return { displayName: 'Root Files', category: 'other' }
  }

  if (groupKey.startsWith('agent/')) {
    const agentName = groupKey
      .replace('agent/', '')
      .split('_')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ')
    return { displayName: `${agentName} Operations`, category: 'agents' }
  }

  const parts = groupKey.split('/')
  const category = parts[0]

  // Format the full path nicely
  const formatted = parts
    .map((part) =>
      part
        .split(/[-_]/)
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ')
    )
    .join(' > ')

  return { displayName: formatted, category }
}

// Category icons/colors for visual distinction
const categoryStyles: Record<string, { color: string; icon: string }> = {
  financial: { color: 'text-green-400', icon: '💰' },
  content: { color: 'text-purple-400', icon: '📝' },
  campaigns: { color: 'text-blue-400', icon: '📢' },
  research: { color: 'text-yellow-400', icon: '🔬' },
  analysis: { color: 'text-orange-400', icon: '📊' },
  agents: { color: 'text-cyan-400', icon: '🤖' },
  other: { color: 'text-gray-400', icon: '📁' },
}

function groupOperationsByDirectory(operations: WorkspaceOperation[]): OperationGroup[] {
  const groups: Record<string, WorkspaceOperation[]> = {}

  operations.forEach((op) => {
    const groupKey = getGroupKey(op)
    if (!groups[groupKey]) {
      groups[groupKey] = []
    }
    groups[groupKey].push(op)
  })

  return Object.entries(groups)
    .map(([groupKey, ops]) => {
      const { displayName, category } = formatGroupName(groupKey)
      const agents = [...new Set(ops.map((op) => op.agent_name))]
      const successCount = ops.filter((op) => op.success).length
      const failedCount = ops.filter((op) => !op.success).length
      const times = ops.map((op) => new Date(op.created_at).getTime())

      return {
        groupKey,
        displayName,
        category,
        operations: ops.sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ),
        agents,
        totalSuccess: successCount,
        totalFailed: failedCount,
        latestTime: new Date(Math.max(...times)).toISOString(),
        earliestTime: new Date(Math.min(...times)).toISOString(),
      }
    })
    .sort((a, b) => new Date(b.latestTime).getTime() - new Date(a.latestTime).getTime())
}

// Collapsible operation group component
function OperationGroupCard({
  group,
  onRollback,
  onReview,
  onViewContent,
  reviewingOperationId,
}: {
  group: OperationGroup
  onRollback: (id: string) => void
  onReview: (id: string, approved: boolean) => void
  onViewContent: (id: string) => void
  reviewingOperationId: string | null
}) {
  const [isExpanded, setIsExpanded] = useState(false)

  const timeAgo = (date: string) => {
    const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000)
    if (seconds < 60) return 'just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
  }

  const style = categoryStyles[group.category] || categoryStyles.other

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
      {/* Group Header - Clickable */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center gap-3 hover:bg-dark-border/30 transition-colors text-left"
      >
        {/* Expand/Collapse Icon */}
        <div className="text-gray-400">
          {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
        </div>

        {/* Category Icon */}
        <span className="text-lg" title={group.category}>
          {style.icon}
        </span>

        {/* Group Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className={cn('font-medium text-sm truncate', style.color)}>
              {group.displayName}
            </h3>
            <span className="px-2 py-0.5 bg-primary-600/20 text-primary-400 text-xs rounded-full">
              {group.operations.length} {group.operations.length === 1 ? 'file' : 'files'}
            </span>
          </div>

          {/* Agents involved */}
          <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
            <Bot size={12} />
            <span className="truncate">{group.agents.slice(0, 3).join(', ')}{group.agents.length > 3 && ` +${group.agents.length - 3} more`}</span>
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 text-xs">
          {group.totalSuccess > 0 && (
            <span className="flex items-center gap-1 text-green-400">
              <CheckCircle size={14} />
              {group.totalSuccess}
            </span>
          )}
          {group.totalFailed > 0 && (
            <span className="flex items-center gap-1 text-red-400">
              <XCircle size={14} />
              {group.totalFailed}
            </span>
          )}
          <span className="flex items-center gap-1 text-gray-400">
            <Clock size={14} />
            {timeAgo(group.latestTime)}
          </span>
        </div>
      </button>

      {/* Expanded Content - Individual Operations */}
      {isExpanded && (
        <div className="border-t border-dark-border bg-dark-bg/50 p-3 space-y-2">
          {group.operations.map((operation) => (
            <OperationCard
              key={operation.id}
              operation={operation}
              onRollback={() => onRollback(operation.id)}
              onReview={(approved) => onReview(operation.id, approved)}
              onViewContent={() => onViewContent(operation.id)}
              isReviewing={reviewingOperationId === operation.id}
              compact
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function OperationsTab({
  activeWorkspace,
  onViewFileContent,
  showSuccess,
  showError,
}: OperationsTabProps) {
  const queryClient = useQueryClient()
  const [operationFilter, setOperationFilter] = useState('')
  const [reviewingOperationId, setReviewingOperationId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'grouped' | 'flat'>('grouped')

  // Operations query
  const { data: operationsData, isLoading: loadingOperations } = useQuery({
    queryKey: ['workspace-operations', activeWorkspace?.id],
    queryFn: () => (activeWorkspace ? workspaceApi.operations(activeWorkspace.id) : null),
    enabled: !!activeWorkspace?.id,
  })

  // Rollback mutation
  const rollbackMutation = useMutation({
    mutationFn: (operationId: string) => workspaceOperationsApi.rollback(operationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-files'] })
      showSuccess('Operation rolled back successfully')
    },
    onError: () => {
      showError('Failed to rollback operation')
    },
  })

  // Review mutation
  const reviewMutation = useMutation({
    mutationFn: ({ operationId, approved }: { operationId: string; approved: boolean }) =>
      workspaceOperationsApi.review(operationId, { approved }),
    onSuccess: (_, { approved }) => {
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
      showSuccess(approved ? 'Operation approved' : 'Operation rejected')
      setReviewingOperationId(null)
    },
    onError: () => {
      showError('Failed to review operation')
      setReviewingOperationId(null)
    },
  })

  // Filter and group operations
  const operations = (operationsData?.data?.results ||
    operationsData?.data ||
    []) as WorkspaceOperation[]

  const filteredOperations = useMemo(() => {
    if (!operationFilter) return operations
    const filter = operationFilter.toLowerCase()
    return operations.filter(
      (op) =>
        op.file_path?.toLowerCase().includes(filter) ||
        op.agent_name?.toLowerCase().includes(filter) ||
        op.operation_type?.toLowerCase().includes(filter) ||
        op.agent_task?.toLowerCase().includes(filter)
    )
  }, [operations, operationFilter])

  const groupedOperations = useMemo(
    () => groupOperationsByDirectory(filteredOperations),
    [filteredOperations]
  )

  const handleReview = (operationId: string, approved: boolean) => {
    setReviewingOperationId(operationId)
    reviewMutation.mutate({ operationId, approved })
  }

  return (
    <div className="space-y-4">
      {/* Filter & View Toggle */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
          <input
            type="text"
            placeholder="Filter operations..."
            value={operationFilter}
            onChange={(e) => setOperationFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
          />
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center bg-dark-bg border border-dark-border rounded-lg p-1">
          <button
            onClick={() => setViewMode('grouped')}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors',
              viewMode === 'grouped'
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white'
            )}
            title="Group related operations"
          >
            <Layers size={14} />
            Grouped
          </button>
          <button
            onClick={() => setViewMode('flat')}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors',
              viewMode === 'flat' ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'
            )}
            title="Show all operations"
          >
            <List size={14} />
            Flat
          </button>
        </div>
      </div>

      {/* Stats Row */}
      {filteredOperations.length > 0 && (
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <FileText size={12} />
            {filteredOperations.length} operations
          </span>
          {viewMode === 'grouped' && (
            <span className="flex items-center gap-1">
              <Layers size={12} />
              {groupedOperations.length} task groups
            </span>
          )}
          <span className="flex items-center gap-1 text-green-400">
            <CheckCircle size={12} />
            {filteredOperations.filter((op) => op.success).length} successful
          </span>
          <span className="flex items-center gap-1 text-red-400">
            <XCircle size={12} />
            {filteredOperations.filter((op) => !op.success).length} failed
          </span>
        </div>
      )}

      {/* Operations List */}
      {loadingOperations ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={24} className="animate-spin text-primary-400" />
        </div>
      ) : filteredOperations.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="h-16 w-16 rounded-full bg-dark-border flex items-center justify-center mb-4">
            <History size={32} className="text-gray-400" />
          </div>
          <h3 className="font-semibold text-lg">No operations yet</h3>
          <p className="text-sm text-gray-400 mt-1 max-w-sm">
            Agent file operations will appear here
          </p>
        </div>
      ) : viewMode === 'grouped' ? (
        // Grouped View
        <div className="space-y-3">
          {groupedOperations.map((group) => (
            <OperationGroupCard
              key={group.groupKey}
              group={group}
              onRollback={(id) => rollbackMutation.mutate(id)}
              onReview={handleReview}
              onViewContent={onViewFileContent}
              reviewingOperationId={reviewingOperationId}
            />
          ))}
        </div>
      ) : (
        // Flat View
        <div className="space-y-3">
          {filteredOperations.map((operation) => (
            <OperationCard
              key={operation.id}
              operation={operation}
              onRollback={() => rollbackMutation.mutate(operation.id)}
              onReview={(approved) => handleReview(operation.id, approved)}
              onViewContent={() => onViewFileContent(operation.id)}
              isReviewing={reviewingOperationId === operation.id}
            />
          ))}
        </div>
      )}
    </div>
  )
}
