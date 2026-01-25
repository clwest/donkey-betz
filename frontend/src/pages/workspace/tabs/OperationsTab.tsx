// Session 825: Operations Tab
// Extracted from WorkspacePage.tsx for modular architecture

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Loader2, History } from 'lucide-react'
import { workspaceApi, workspaceOperationsApi } from '@/lib/api'
import { OperationCard } from '../components/OperationCard'
import type { Workspace, WorkspaceOperation } from '../types'

interface OperationsTabProps {
  activeWorkspace: Workspace | undefined
  onViewFileContent: (operationId: string) => void
  showSuccess: (message: string) => void
  showError: (message: string) => void
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

  // Operations query
  const { data: operationsData, isLoading: loadingOperations } = useQuery({
    queryKey: ['workspace-operations', activeWorkspace?.id],
    queryFn: () => activeWorkspace ? workspaceApi.operations(activeWorkspace.id) : null,
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

  // Filter operations
  const operations = (operationsData?.data?.results || operationsData?.data || []) as WorkspaceOperation[]
  const filteredOperations = useMemo(() => {
    if (!operationFilter) return operations
    const filter = operationFilter.toLowerCase()
    return operations.filter(
      (op) =>
        op.file_path?.toLowerCase().includes(filter) ||
        op.agent_name?.toLowerCase().includes(filter) ||
        op.operation_type?.toLowerCase().includes(filter)
    )
  }, [operations, operationFilter])

  const handleReview = (operationId: string, approved: boolean) => {
    setReviewingOperationId(operationId)
    reviewMutation.mutate({ operationId, approved })
  }

  return (
    <div className="space-y-4">
      {/* Filter */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
        <input
          type="text"
          placeholder="Filter operations..."
          value={operationFilter}
          onChange={(e) => setOperationFilter(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
        />
      </div>

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
      ) : (
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
