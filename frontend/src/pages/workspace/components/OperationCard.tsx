// Session 825: Operation card component
// Extracted from WorkspacePage.tsx for reuse

import { useState } from 'react'
import {
  Plus, Code, Trash2, GitCommit, File,
  Clock, CheckCircle, XCircle, RotateCcw,
  Eye, FileText, Loader2
} from 'lucide-react'
import { cn } from '@/lib/cn'
import EntityLink from '@/components/EntityLink'
import type { WorkspaceOperation } from '../types'

interface OperationCardProps {
  operation: WorkspaceOperation
  onRollback?: () => void
  onReview?: (approved: boolean) => void
  onViewContent?: () => void
  isReviewing?: boolean
}

export function OperationCard({
  operation,
  onRollback,
  onReview,
  onViewContent,
  isReviewing,
}: OperationCardProps) {
  const [showDiff, setShowDiff] = useState(false)

  const getOperationIcon = (type: string) => {
    switch (type) {
      case 'file_create':
        return <Plus size={14} className="text-accent-green" />
      case 'file_update':
      case 'file_modify':
        return <Code size={14} className="text-accent-amber" />
      case 'file_delete':
        return <Trash2 size={14} className="text-accent-red" />
      case 'git_commit':
        return <GitCommit size={14} className="text-primary-400" />
      default:
        return <File size={14} className="text-gray-400" />
    }
  }

  const getReviewStatus = () => {
    if (!operation.reviewed_by_human) return null
    if (operation.human_approved === true) return 'approved'
    if (operation.human_approved === false) return 'rejected'
    return null
  }

  const reviewStatus = getReviewStatus()

  return (
    <div
      className={cn(
        'border rounded-lg p-3 space-y-2',
        operation.rolled_back
          ? 'border-gray-600 bg-dark-bg/50 opacity-70'
          : 'border-dark-border'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getOperationIcon(operation.operation_type)}
          <div>
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium">
                {operation.file_path || operation.operation_type}
              </p>
              {operation.rolled_back && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-gray-500/20 text-gray-400 flex items-center gap-1">
                  <RotateCcw size={10} />
                  Rolled Back
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
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
            <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">
              Success
            </span>
          ) : (
            <span className="text-xs px-2 py-1 rounded bg-accent-red/20 text-accent-red">
              Failed
            </span>
          )}
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
            <span className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber">
              Pending Review
            </span>
          )}
          {operation.can_rollback && !operation.rolled_back && operation.success && (
            <span
              className="text-xs px-1.5 py-0.5 rounded bg-primary-500/10 text-primary-400"
              title="Rollback available"
            >
              <RotateCcw size={12} />
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      {operation.description && (
        <p className="text-xs text-gray-400">{operation.description}</p>
      )}

      {/* Error message */}
      {!operation.success && operation.error_message && (
        <div className="flex items-start gap-2 p-2 bg-accent-red/10 border border-accent-red/20 rounded text-xs text-accent-red">
          <XCircle size={14} className="flex-shrink-0 mt-0.5" />
          <span>{operation.error_message}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        {onViewContent && operation.success && (
          <button
            onClick={onViewContent}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            <FileText size={12} />
            {['file_create', 'file_update', 'file_modify', 'file_delete', 'file_rename'].includes(
              operation.operation_type
            )
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
        {onRollback &&
          operation.success &&
          operation.can_rollback &&
          !operation.rolled_back && (
            <button
              onClick={onRollback}
              className="text-xs text-accent-amber hover:text-accent-amber/80 flex items-center gap-1"
            >
              <RotateCcw size={12} />
              Rollback
            </button>
          )}
        {onReview &&
          (operation.requires_review || operation.pending_review) &&
          !operation.reviewed_by_human && (
            <>
              <button
                onClick={() => onReview(true)}
                disabled={isReviewing}
                className={cn(
                  'text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition-all',
                  isReviewing
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30 border border-accent-green/30'
                )}
              >
                {isReviewing ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <CheckCircle size={12} />
                )}
                Approve
              </button>
              <button
                onClick={() => onReview(false)}
                disabled={isReviewing}
                className={cn(
                  'text-xs px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition-all',
                  isReviewing
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-accent-red/20 text-accent-red hover:bg-accent-red/30 border border-accent-red/30'
                )}
              >
                {isReviewing ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <XCircle size={12} />
                )}
                Reject
              </button>
            </>
          )}
      </div>

      {/* Diff view */}
      {showDiff && operation.diff && (
        <pre className="text-xs bg-dark-bg p-3 rounded overflow-x-auto max-h-64 overflow-y-auto font-mono">
          {operation.diff}
        </pre>
      )}
    </div>
  )
}
