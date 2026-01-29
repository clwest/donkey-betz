// Session 847: Initiative Pipeline Dashboard
// ChatGPT feedback: "Build 'Initiative Dashboard' View - One screen showing all initiatives"
// Shows: Initiative name, status, owner, progress bar (Stage 1-5), health indicator
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  FolderKanban,
  RefreshCw,
  Loader2,
  CheckCircle2,
  Circle,
  Clock,
  AlertTriangle,
  ChevronRight,
  FileText,
  ArrowRight,
  Sparkles,
  MessageSquare,
  GitBranch,
  Lightbulb,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi, blogsApi } from '@/lib/api'

// Stage names for display
const STAGE_NAMES: Record<number, string> = {
  1: 'Research Brief',
  2: 'Prototype Plan',
  3: 'Evaluation',
  4: 'Tech Design',
  5: 'Pilot Execution',
}

// Session 849: Source decision for trace view
interface SourceDecision {
  id: string
  topic: string
  artifact_type: string
  suggested_feature: string
  conversation_id: string | null
  hive_session_id: string | null
  created_at: string
}

interface Initiative {
  id: string
  name: string
  description: string
  status: string
  current_stage: number
  completion_percentage: number
  // Session 857: Additional progress metrics
  approved_percentage?: number
  stages_with_work?: number
  stages: Record<number, {
    status: string
    stage_name: string
    document_id: string | null
    approved_at: string | null
  }>
  // Session 849: Trace data
  source_decision_id: string | null
  parent_topic: string
  source_decisions: SourceDecision[]
  created_at: string
  updated_at: string
}

// Health indicator based on status and update time
function getHealth(initiative: Initiative): 'healthy' | 'stale' | 'blocked' {
  const daysSinceUpdate = Math.floor(
    (Date.now() - new Date(initiative.updated_at).getTime()) / (1000 * 60 * 60 * 24)
  )

  // Check for rejected stages
  for (let i = 1; i <= 5; i++) {
    if (initiative.stages[i]?.status === 'REJECTED') {
      return 'blocked'
    }
  }

  // Check if current stage is stuck
  const currentStage = initiative.stages[initiative.current_stage]
  if (currentStage && !currentStage.document_id && daysSinceUpdate > 7) {
    return 'blocked'
  }

  // Check for staleness
  if (daysSinceUpdate > 14) {
    return 'stale'
  }

  return 'healthy'
}

// Stage progress indicator
function StageProgress({ initiative }: { initiative: Initiative }) {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((stageNum) => {
        const stage = initiative.stages[stageNum]
        const isApproved = stage?.status === 'APPROVED'
        const hasDraft = stage?.document_id && stage?.status !== 'APPROVED'
        const isCurrent = initiative.current_stage === stageNum
        const isRejected = stage?.status === 'REJECTED'

        return (
          <div
            key={stageNum}
            className="group relative"
          >
            <div
              className={cn(
                'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium transition-all',
                isApproved && 'bg-green-500/20 text-green-400 ring-2 ring-green-500/30',
                hasDraft && !isApproved && 'bg-yellow-500/20 text-yellow-400 ring-2 ring-yellow-500/30',
                isRejected && 'bg-red-500/20 text-red-400 ring-2 ring-red-500/30',
                !stage?.document_id && !isRejected && 'bg-dark-border text-gray-500',
                isCurrent && !isApproved && !isRejected && 'ring-2 ring-primary-500/50'
              )}
            >
              {isApproved ? (
                <CheckCircle2 size={14} />
              ) : isRejected ? (
                <AlertTriangle size={12} />
              ) : (
                stageNum
              )}
            </div>
            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-dark-card border border-dark-border rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              <div className="font-medium">{STAGE_NAMES[stageNum]}</div>
              <div className="text-gray-400">
                {isApproved ? 'Approved' : hasDraft ? 'Draft' : isRejected ? 'Rejected' : 'Pending'}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Single initiative card
function InitiativeCard({ initiative, onViewDetails }: { initiative: Initiative; onViewDetails: () => void }) {
  const health = getHealth(initiative)

  return (
    <div
      className={cn(
        'bg-dark-card border rounded-lg p-4 hover:border-primary-500/50 transition-colors cursor-pointer',
        health === 'healthy' && 'border-dark-border',
        health === 'stale' && 'border-yellow-500/30',
        health === 'blocked' && 'border-red-500/30'
      )}
      onClick={onViewDetails}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <FolderKanban size={16} className="text-primary-400 flex-shrink-0" />
            <h3 className="font-medium truncate">{initiative.name}</h3>
          </div>
          <p className="text-xs text-gray-400 truncate">{initiative.description || 'No description'}</p>
        </div>
        <div className="flex items-center gap-2 ml-3">
          {/* Health indicator */}
          <span
            className={cn(
              'px-2 py-0.5 rounded text-xs font-medium',
              health === 'healthy' && 'bg-green-500/20 text-green-400',
              health === 'stale' && 'bg-yellow-500/20 text-yellow-400',
              health === 'blocked' && 'bg-red-500/20 text-red-400'
            )}
          >
            {health === 'healthy' && 'On Track'}
            {health === 'stale' && 'Stale'}
            {health === 'blocked' && 'Blocked'}
          </span>
        </div>
      </div>

      {/* Progress section */}
      <div className="flex items-center justify-between">
        <StageProgress initiative={initiative} />
        <div className="flex items-center gap-3 text-xs text-gray-400">
          {/* Session 857: Show weighted progress and approved count */}
          <span>
            {initiative.completion_percentage}% progress
            {initiative.approved_percentage !== undefined && initiative.approved_percentage > 0 && (
              <span className="text-green-400 ml-1">({initiative.approved_percentage}% approved)</span>
            )}
          </span>
          <ChevronRight size={14} />
        </div>
      </div>
    </div>
  )
}

// Session 866: Document viewer modal for stage documents
function DocumentViewerModal({
  documentId,
  stageName,
  onClose,
}: {
  documentId: string
  stageName: string
  onClose: () => void
}) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['selfBlog', documentId],
    queryFn: async () => {
      const res = await blogsApi.get(documentId)
      return res.data.blog
    },
    enabled: !!documentId,
  })

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60]"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border shrink-0">
          <div className="flex items-center gap-3">
            <FileText size={20} className="text-primary-400" />
            <div>
              <h3 className="text-lg font-semibold">{stageName} Document</h3>
              {data?.title && (
                <p className="text-sm text-gray-400">{data.title}</p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            &times;
          </button>
        </div>

        <div className="p-6 overflow-y-auto flex-1">
          {isLoading && (
            <div className="flex items-center justify-center py-16">
              <Loader2 size={24} className="animate-spin text-primary-400" />
            </div>
          )}

          {isError && (
            <div className="text-center py-16">
              <AlertTriangle size={32} className="text-red-400 mx-auto mb-2" />
              <p className="text-gray-400">Failed to load document</p>
            </div>
          )}

          {data && !isLoading && (
            <div className="prose prose-invert max-w-none">
              {/* Document metadata */}
              <div className="flex items-center gap-4 text-xs text-gray-400 mb-4 pb-4 border-b border-dark-border">
                {data.word_count && <span>{data.word_count} words</span>}
                {data.created_at && (
                  <span>Created: {new Date(data.created_at).toLocaleDateString()}</span>
                )}
                {data.status && (
                  <span className="px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
                    {data.status}
                  </span>
                )}
              </div>

              {/* Document content */}
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {data.full_text || data.content || 'No content available'}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end p-4 border-t border-dark-border bg-dark-bg/50 shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Initiative detail modal
function InitiativeDetailModal({
  initiative,
  onClose,
}: {
  initiative: Initiative
  onClose: () => void
}) {
  // Session 866: State for viewing stage documents
  const [viewingDocument, setViewingDocument] = useState<{ id: string; stageName: string } | null>(null)

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border shrink-0">
          <div>
            <h3 className="text-lg font-semibold">{initiative.name}</h3>
            <p className="text-sm text-gray-400">{initiative.description || 'No description'}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg transition-colors">
            &times;
          </button>
        </div>

        <div className="p-4 space-y-4 overflow-y-auto flex-1">
          {/* Progress bar - Session 857: Show both progress and approved metrics */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-400">Overall Progress</span>
              <span className="font-medium">
                {initiative.completion_percentage}%
                {initiative.approved_percentage !== undefined && initiative.approved_percentage > 0 && (
                  <span className="text-green-400 text-xs ml-1">
                    ({initiative.approved_percentage}% approved)
                  </span>
                )}
              </span>
            </div>
            <div className="h-2 bg-dark-border rounded-full overflow-hidden relative">
              {/* Approved progress (green) */}
              {initiative.approved_percentage !== undefined && initiative.approved_percentage > 0 && (
                <div
                  className="absolute h-full bg-green-500 transition-all"
                  style={{ width: `${initiative.approved_percentage}%` }}
                />
              )}
              {/* Overall progress (primary color) */}
              <div
                className="h-full bg-gradient-to-r from-primary-500/50 to-primary-400/50 transition-all"
                style={{ width: `${initiative.completion_percentage}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Stage {initiative.current_stage} of 5</span>
              {initiative.stages_with_work !== undefined && (
                <span>{initiative.stages_with_work} stages with documents</span>
              )}
            </div>
          </div>

          {/* Stage list */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-400">Pipeline Stages</h4>
            {[1, 2, 3, 4, 5].map((stageNum) => {
              const stage = initiative.stages[stageNum]
              const isApproved = stage?.status === 'APPROVED'
              const hasDraft = stage?.document_id && stage?.status !== 'APPROVED'
              const isCurrent = initiative.current_stage === stageNum

              return (
                <div
                  key={stageNum}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg border',
                    isApproved && 'bg-green-500/10 border-green-500/30',
                    hasDraft && !isApproved && 'bg-yellow-500/10 border-yellow-500/30',
                    !stage?.document_id && 'bg-dark-bg border-dark-border',
                    isCurrent && !isApproved && 'ring-1 ring-primary-500/50'
                  )}
                >
                  <div
                    className={cn(
                      'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                      isApproved && 'bg-green-500/20 text-green-400',
                      hasDraft && !isApproved && 'bg-yellow-500/20 text-yellow-400',
                      !stage?.document_id && 'bg-dark-border text-gray-500'
                    )}
                  >
                    {isApproved ? <CheckCircle2 size={18} /> : stageNum}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{STAGE_NAMES[stageNum]}</span>
                      {isCurrent && !isApproved && (
                        <span className="px-1.5 py-0.5 rounded text-xs bg-primary-500/20 text-primary-400">
                          Current
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-400">
                      {isApproved
                        ? `Approved ${stage?.approved_at ? new Date(stage.approved_at).toLocaleDateString() : ''}`
                        : hasDraft
                          ? 'Document in draft'
                          : 'No document yet'}
                    </div>
                  </div>
                  {/* Session 866: Clickable document indicator to view content */}
                  {stage?.document_id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setViewingDocument({ id: stage.document_id!, stageName: STAGE_NAMES[stageNum] })
                      }}
                      className="p-2 bg-primary-500/10 hover:bg-primary-500/20 rounded-lg transition-colors"
                      title="View document"
                    >
                      <FileText size={16} className="text-primary-400" />
                    </button>
                  )}
                </div>
              )
            })}
          </div>

          {/* Session 849: Trace Panel - Show origin of this initiative */}
          {(initiative.source_decisions?.length > 0 || initiative.parent_topic) && (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-400 flex items-center gap-2">
                <GitBranch size={14} />
                Origin Trace
              </h4>

              {/* Parent Topic */}
              {initiative.parent_topic && (
                <div className="p-3 rounded-lg bg-dark-bg border border-dark-border">
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-1">
                    <Lightbulb size={12} />
                    Parent Topic
                  </div>
                  <div className="text-sm">{initiative.parent_topic}</div>
                </div>
              )}

              {/* Source Decisions */}
              {initiative.source_decisions?.map((decision) => (
                <div
                  key={decision.id}
                  className="p-3 rounded-lg bg-dark-bg border border-dark-border"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <MessageSquare size={14} className="text-primary-400" />
                      <span className="text-sm font-medium truncate max-w-xs">
                        {decision.topic}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-xs bg-primary-500/20 text-primary-400">
                      {decision.artifact_type}
                    </span>
                  </div>

                  {/* Suggested Feature Preview */}
                  {decision.suggested_feature && (
                    <div className="text-xs text-gray-400 mb-2 line-clamp-2">
                      {decision.suggested_feature}
                    </div>
                  )}

                  {/* Session 857: Show source info inline instead of external links */}
                  <div className="flex items-center gap-3 text-xs">
                    {decision.conversation_id && (
                      <span className="flex items-center gap-1 text-primary-400">
                        <MessageSquare size={12} />
                        From Conversation
                      </span>
                    )}
                    {decision.hive_session_id && (
                      <span className="flex items-center gap-1 text-primary-400">
                        <MessageSquare size={12} />
                        From Hive Session
                      </span>
                    )}
                    <span className="text-gray-500">
                      {new Date(decision.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}

              {/* Trace Summary */}
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>Conversation</span>
                <ArrowRight size={10} />
                <span>Decision</span>
                <ArrowRight size={10} />
                <span className="text-primary-400">Initiative</span>
                <ArrowRight size={10} />
                <span>Stage Documents</span>
              </div>
            </div>
          )}

        </div>

        {/* Footer with metadata */}
        <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-bg/50 shrink-0">
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span>Created: {new Date(initiative.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(initiative.updated_at).toLocaleDateString()}</span>
            <span className="capitalize">Status: {initiative.status.toLowerCase()}</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>

        {/* Session 866: Document viewer modal */}
        {viewingDocument && (
          <DocumentViewerModal
            documentId={viewingDocument.id}
            stageName={viewingDocument.stageName}
            onClose={() => setViewingDocument(null)}
          />
        )}
      </div>
    </div>
  )
}

// Empty state
function EmptyState({ onPopulate, isPopulating }: { onPopulate: () => void; isPopulating: boolean }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 rounded-full bg-primary-500/10 flex items-center justify-center mb-4">
        <FolderKanban size={32} className="text-primary-400" />
      </div>
      <h3 className="text-lg font-medium mb-2">No Initiatives Yet</h3>
      <p className="text-gray-400 max-w-md mb-6">
        Initiatives are auto-created when ThinkingAgent triggers actions like research or content creation.
        You can also populate from existing deliverables.
      </p>
      <button
        onClick={onPopulate}
        disabled={isPopulating}
        className="btn btn-primary flex items-center gap-2"
      >
        {isPopulating ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Populating...
          </>
        ) : (
          <>
            <Sparkles size={16} />
            Populate from Deliverables
          </>
        )}
      </button>
    </div>
  )
}

export function InitiativesTab() {
  const queryClient = useQueryClient()
  const [selectedInitiative, setSelectedInitiative] = useState<Initiative | null>(null)
  const [filter, setFilter] = useState<'all' | 'active' | 'stale' | 'blocked'>('all')

  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['initiatives'],
    queryFn: async () => {
      const res = await platformApi.initiatives()
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const populateMutation = useMutation({
    mutationFn: () => platformApi.populateInitiatives(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] })
    },
  })

  // Filter initiatives by health
  const filteredInitiatives = (data?.initiatives || []).filter((init) => {
    if (filter === 'all') return true
    const health = getHealth(init)
    if (filter === 'active') return init.status === 'ACTIVE'
    return health === filter
  })

  // Stats
  const stats = {
    total: data?.initiatives?.length || 0,
    active: data?.initiatives?.filter((i) => i.status === 'ACTIVE').length || 0,
    stale: data?.initiatives?.filter((i) => getHealth(i) === 'stale').length || 0,
    blocked: data?.initiatives?.filter((i) => getHealth(i) === 'blocked').length || 0,
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 size={24} className="animate-spin text-primary-400" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="text-center py-16">
        <AlertTriangle size={32} className="text-red-400 mx-auto mb-2" />
        <p className="text-gray-400">Failed to load initiatives</p>
        <button onClick={() => refetch()} className="btn btn-ghost mt-4">
          Try Again
        </button>
      </div>
    )
  }

  if (!data?.initiatives?.length) {
    return <EmptyState onPopulate={() => populateMutation.mutate()} isPopulating={populateMutation.isPending} />
  }

  return (
    <div className="space-y-6">
      {/* Header with stats */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold">Initiative Pipeline</h2>
          <div className="flex items-center gap-2 text-sm">
            <button
              onClick={() => setFilter('all')}
              className={cn(
                'px-3 py-1 rounded-full transition-colors',
                filter === 'all' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
              )}
            >
              All ({stats.total})
            </button>
            <button
              onClick={() => setFilter('active')}
              className={cn(
                'px-3 py-1 rounded-full transition-colors',
                filter === 'active' ? 'bg-green-500/20 text-green-400' : 'text-gray-400 hover:text-white'
              )}
            >
              Active ({stats.active})
            </button>
            {stats.stale > 0 && (
              <button
                onClick={() => setFilter('stale')}
                className={cn(
                  'px-3 py-1 rounded-full transition-colors',
                  filter === 'stale' ? 'bg-yellow-500/20 text-yellow-400' : 'text-gray-400 hover:text-white'
                )}
              >
                Stale ({stats.stale})
              </button>
            )}
            {stats.blocked > 0 && (
              <button
                onClick={() => setFilter('blocked')}
                className={cn(
                  'px-3 py-1 rounded-full transition-colors',
                  filter === 'blocked' ? 'bg-red-500/20 text-red-400' : 'text-gray-400 hover:text-white'
                )}
              >
                Blocked ({stats.blocked})
              </button>
            )}
          </div>
        </div>
        <button
          onClick={() => refetch()}
          className="btn btn-ghost p-2"
          title="Refresh"
        >
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Initiative grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredInitiatives.map((initiative) => (
          <InitiativeCard
            key={initiative.id}
            initiative={initiative}
            onViewDetails={() => setSelectedInitiative(initiative)}
          />
        ))}
      </div>

      {filteredInitiatives.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          No initiatives match the selected filter
        </div>
      )}

      {/* Detail modal */}
      {selectedInitiative && (
        <InitiativeDetailModal
          initiative={selectedInitiative}
          onClose={() => setSelectedInitiative(null)}
        />
      )}
    </div>
  )
}
