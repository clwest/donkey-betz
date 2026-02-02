// Session 847: Initiative Pipeline Dashboard
// Session 898: Added Completed filter and comprehensive origin trace view
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
  ChevronDown,
  ChevronUp,
  FileText,
  ArrowRight,
  Sparkles,
  MessageSquare,
  GitBranch,
  Lightbulb,
  Download,
  Users,
  Zap,
  BookOpen,
  Trophy,
  Eye,
  Radio,
  Brain,
  Target,
  TrendingUp,
  Tag,
  Quote,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi, blogsApi } from '@/lib/api'
import { generateDocumentPDF } from '@/lib/pdfExport'

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
  const isCompleted = initiative.status === 'COMPLETED'

  return (
    <div
      className={cn(
        'bg-dark-card border rounded-lg p-4 hover:border-primary-500/50 transition-colors cursor-pointer',
        // Session 898: Special styling for completed initiatives
        isCompleted && 'border-emerald-500/30 bg-emerald-500/5',
        !isCompleted && health === 'healthy' && 'border-dark-border',
        !isCompleted && health === 'stale' && 'border-yellow-500/30',
        !isCompleted && health === 'blocked' && 'border-red-500/30'
      )}
      onClick={onViewDetails}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {/* Session 898: Trophy icon for completed initiatives */}
            {isCompleted ? (
              <Trophy size={16} className="text-emerald-400 flex-shrink-0" />
            ) : (
              <FolderKanban size={16} className="text-primary-400 flex-shrink-0" />
            )}
            <h3 className="font-medium truncate">{initiative.name}</h3>
          </div>
          <p className="text-xs text-gray-400 truncate">{initiative.description || 'No description'}</p>
        </div>
        <div className="flex items-center gap-2 ml-3">
          {/* Status/Health indicator - Session 898: Show Completed status */}
          {isCompleted ? (
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/20 text-emerald-400 flex items-center gap-1">
              <CheckCircle2 size={12} />
              Completed
            </span>
          ) : (
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
          )}
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
// Session 896: Added PDF download functionality
function DocumentViewerModal({
  documentId,
  stageName,
  initiativeName,
  onClose,
}: {
  documentId: string
  stageName: string
  initiativeName?: string
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

        <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-bg/50 shrink-0">
          {/* Session 896: PDF download button */}
          {data && (
            <button
              onClick={() => {
                generateDocumentPDF({
                  title: data.title,
                  content: data.full_text || data.content || '',
                  stageName: stageName,
                  initiativeName: initiativeName,
                  wordCount: data.word_count,
                  createdAt: data.created_at,
                  status: data.status,
                })
              }}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 rounded-lg transition-colors"
            >
              <Download size={16} />
              Download PDF
            </button>
          )}
          {!data && <div />}
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
        {/* Session 896: Added initiativeName for PDF export */}
        {viewingDocument && (
          <DocumentViewerModal
            documentId={viewingDocument.id}
            stageName={viewingDocument.stageName}
            initiativeName={initiative.name}
            onClose={() => setViewingDocument(null)}
          />
        )}
      </div>
    </div>
  )
}

// Session 898: Comprehensive Initiative Detail Modal with full origin trace
// Shows: Origin (trigger, conversation, agents), all stages with documents, summary
function ComprehensiveInitiativeModal({
  initiativeId,
  onClose,
}: {
  initiativeId: string
  onClose: () => void
}) {
  const [viewingDocument, setViewingDocument] = useState<{ id: string; stageName: string } | null>(null)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    origin: true,
    conversation: false,
    stages: true,
    deliverable: true,
  })

  const { data, isLoading, isError } = useQuery({
    queryKey: ['initiative-trace', initiativeId],
    queryFn: async () => {
      const res = await platformApi.originTrace(initiativeId)
      return res.data
    },
  })

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }))
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-dark-card border border-dark-border rounded-xl p-8">
          <Loader2 size={32} className="animate-spin text-primary-400 mx-auto" />
          <p className="text-gray-400 mt-4">Loading initiative details...</p>
        </div>
      </div>
    )
  }

  if (isError || !data?.success) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
        <div className="bg-dark-card border border-dark-border rounded-xl p-8 text-center">
          <AlertTriangle size={32} className="text-red-400 mx-auto mb-2" />
          <p className="text-gray-400">Failed to load initiative details</p>
          <button onClick={onClose} className="btn btn-ghost mt-4">Close</button>
        </div>
      </div>
    )
  }

  const trace = data.trace

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-5xl mx-4 max-h-[95vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with Summary */}
        <div className="p-6 border-b border-dark-border bg-gradient-to-r from-primary-500/10 to-purple-500/10 shrink-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                {trace.initiative.status === 'COMPLETED' ? (
                  <Trophy size={24} className="text-green-400" />
                ) : (
                  <FolderKanban size={24} className="text-primary-400" />
                )}
                <h2 className="text-xl font-bold">{trace.initiative.name}</h2>
              </div>
              <p className="text-gray-400 text-sm mb-4">{trace.initiative.description}</p>

              {/* Completeness Score */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-dark-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
                      style={{ width: `${trace.trace_completeness.completeness_score}%` }}
                    />
                  </div>
                  <span className="text-sm text-green-400 font-medium">
                    {trace.trace_completeness.completeness_score.toFixed(0)}% Complete
                  </span>
                </div>
                <span className={cn(
                  'px-2 py-1 rounded text-xs font-medium',
                  trace.initiative.status === 'COMPLETED' && 'bg-green-500/20 text-green-400',
                  trace.initiative.status === 'ACTIVE' && 'bg-blue-500/20 text-blue-400',
                )}>
                  {trace.initiative.status}
                </span>
              </div>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg">
              &times;
            </button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="text-center p-2 bg-dark-bg/50 rounded-lg">
              <div className="text-lg font-bold text-primary-400">{trace.agents.length}</div>
              <div className="text-xs text-gray-400">Agents</div>
            </div>
            <div className="text-center p-2 bg-dark-bg/50 rounded-lg">
              <div className="text-lg font-bold text-blue-400">
                {trace.conversation?.message_count || trace.conversation?.contribution_count || 0}
              </div>
              <div className="text-xs text-gray-400">Messages</div>
            </div>
            <div className="text-center p-2 bg-dark-bg/50 rounded-lg">
              <div className="text-lg font-bold text-green-400">
                {trace.stages.filter(s => s.status === 'APPROVED').length}/5
              </div>
              <div className="text-xs text-gray-400">Stages Done</div>
            </div>
            <div className="text-center p-2 bg-dark-bg/50 rounded-lg">
              <div className="text-lg font-bold text-purple-400">
                {trace.deliverable ? Math.round(trace.deliverable.content_length / 1000) + 'k' : '—'}
              </div>
              <div className="text-xs text-gray-400">Content (chars)</div>
            </div>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* ORIGIN SECTION */}
          <div className="border border-dark-border rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('origin')}
              className="w-full flex items-center justify-between p-4 bg-dark-bg hover:bg-dark-bg/80 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Zap size={18} className="text-yellow-400" />
                <span className="font-medium">Origin & Trigger</span>
                {/* Session 900: Show signal intelligence badge if present */}
                {trace.origin_signals?.signal_cluster && (
                  <span className="px-2 py-0.5 rounded text-xs bg-cyan-500/20 text-cyan-400 flex items-center gap-1">
                    <Radio size={10} />
                    Signal-Driven
                  </span>
                )}
                {trace.trigger && !trace.origin_signals?.signal_cluster && (
                  <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400">
                    {trace.trigger.type}
                  </span>
                )}
              </div>
              {expandedSections.origin ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {expandedSections.origin && (
              <div className="p-4 border-t border-dark-border space-y-4">
                {/* Session 900: Signal Intelligence - Origin Signals */}
                {trace.origin_signals?.signal_cluster && (
                  <div className="p-4 bg-cyan-500/5 border border-cyan-500/20 rounded-lg space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Radio size={16} className="text-cyan-400" />
                        <span className="text-sm font-medium text-cyan-400">Origin Signals</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-xs bg-cyan-500/20 text-cyan-400">
                        {trace.origin_signals.signal_cluster.pattern_type?.replace('_', ' ') || 'pattern'}
                      </span>
                    </div>

                    {/* Source Breakdown */}
                    {trace.origin_signals.signal_cluster.source_breakdown &&
                     Object.keys(trace.origin_signals.signal_cluster.source_breakdown).length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(trace.origin_signals.signal_cluster.source_breakdown).map(([source, count]) => (
                          <div
                            key={source}
                            className="flex items-center gap-2 px-3 py-1.5 bg-dark-bg rounded-lg"
                          >
                            <Radio size={12} className="text-cyan-400" />
                            <span className="text-sm capitalize">{source.replace('_', ' ')}</span>
                            <span className="text-xs text-cyan-400 font-medium">({String(count)})</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Pattern Metrics */}
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <TrendingUp size={12} className="text-green-400" />
                        <span className="text-gray-400">Strength:</span>
                        <span className="text-green-400 font-medium">
                          {(trace.origin_signals.signal_cluster.strength * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Brain size={12} className="text-blue-400" />
                        <span className="text-gray-400">Confidence:</span>
                        <span className="text-blue-400 font-medium">
                          {(trace.origin_signals.signal_cluster.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      {trace.origin_signals.signal_cluster.novelty > 0 && (
                        <div className="flex items-center gap-1">
                          <Sparkles size={12} className="text-purple-400" />
                          <span className="text-gray-400">Novelty:</span>
                          <span className="text-purple-400 font-medium">
                            {(trace.origin_signals.signal_cluster.novelty * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Keywords */}
                    {trace.origin_signals.signal_cluster.keywords &&
                     trace.origin_signals.signal_cluster.keywords.length > 0 && (
                      <div>
                        <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
                          <Tag size={10} />
                          Keywords
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {trace.origin_signals.signal_cluster.keywords.slice(0, 8).map((keyword, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 bg-dark-border rounded text-xs text-gray-300"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Sample Signals */}
                    {trace.origin_signals.signal_cluster.sample_signals &&
                     trace.origin_signals.signal_cluster.sample_signals.length > 0 && (
                      <div>
                        <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
                          <Quote size={10} />
                          Sample Signals
                        </div>
                        <div className="space-y-2">
                          {trace.origin_signals.signal_cluster.sample_signals.slice(0, 3).map((signal, idx) => (
                            <div
                              key={idx}
                              className="text-xs text-gray-400 pl-3 border-l-2 border-cyan-500/30"
                            >
                              <span className="text-cyan-400 font-medium capitalize">
                                {signal.source}:
                              </span>{' '}
                              {signal.text?.slice(0, 150)}{signal.text?.length > 150 ? '...' : ''}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Session 900: Auto Topic - WHY this topic was chosen */}
                {trace.origin_signals?.auto_topic && (
                  <div className="p-4 bg-orange-500/5 border border-orange-500/20 rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Target size={16} className="text-orange-400" />
                        <span className="text-sm font-medium text-orange-400">Auto Topic</span>
                      </div>
                      {trace.origin_signals.auto_topic.confidence > 0 && (
                        <span className="text-xs text-orange-400">
                          {(trace.origin_signals.auto_topic.confidence * 100).toFixed(0)}% confidence
                        </span>
                      )}
                    </div>
                    <div className="font-medium">{trace.origin_signals.auto_topic.name}</div>
                    {trace.origin_signals.auto_topic.rationale && (
                      <div className="text-sm text-gray-400 italic">
                        "{trace.origin_signals.auto_topic.rationale}"
                      </div>
                    )}
                    {trace.origin_signals.auto_topic.triggered_at && (
                      <div className="text-xs text-gray-500">
                        Triggered: {new Date(trace.origin_signals.auto_topic.triggered_at).toLocaleString()}
                      </div>
                    )}
                  </div>
                )}

                {/* Trigger */}
                {trace.trigger && (
                  <div className="p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-lg">
                    <div className="text-xs text-yellow-400 mb-1">Trigger</div>
                    <div className="font-medium">{trace.trigger.description}</div>
                  </div>
                )}

                {/* Agents */}
                {trace.agents.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                      <Users size={14} />
                      <span>Participating Agents</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {trace.agents.map((agent, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1.5 rounded-full bg-primary-500/10 text-primary-400 text-sm"
                        >
                          {agent}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Decision */}
                {trace.decision && (
                  <div className="p-3 bg-purple-500/5 border border-purple-500/20 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs text-purple-400">Decision Created</div>
                      <span className="px-2 py-0.5 rounded text-xs bg-purple-500/20 text-purple-400">
                        {trace.decision.artifact_type}
                      </span>
                    </div>
                    <div className="font-medium mb-2">{trace.decision.topic}</div>
                    {trace.decision.recommended_stance && (
                      <div className="text-sm text-gray-300 mb-2">
                        <span className="text-gray-500">Recommendation:</span> {trace.decision.recommended_stance}
                      </div>
                    )}
                    {trace.decision.key_insights && trace.decision.key_insights.length > 0 && (
                      <div className="space-y-1">
                        <div className="text-xs text-gray-500">Key Insights:</div>
                        {trace.decision.key_insights.slice(0, 3).map((insight, idx) => (
                          <div key={idx} className="text-xs text-gray-400 pl-3 border-l-2 border-purple-500/30">
                            {insight.slice(0, 200)}...
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* CONVERSATION SECTION */}
          {trace.conversation && (
            <div className="border border-dark-border rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('conversation')}
                className="w-full flex items-center justify-between p-4 bg-dark-bg hover:bg-dark-bg/80 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <MessageSquare size={18} className="text-blue-400" />
                  <span className="font-medium">Source Conversation</span>
                  <span className="text-sm text-gray-400">
                    {trace.conversation.message_count || trace.conversation.contribution_count || 0} messages
                  </span>
                  {trace.conversation.quality_score && (
                    <span className="px-2 py-0.5 rounded text-xs bg-green-500/20 text-green-400">
                      Quality: {trace.conversation.quality_score}
                    </span>
                  )}
                </div>
                {expandedSections.conversation ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </button>

              {expandedSections.conversation && (
                <div className="p-4 border-t border-dark-border space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Type:</span>{' '}
                      <span className="text-gray-300">{trace.conversation.type}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Status:</span>{' '}
                      <span className="text-gray-300">{trace.conversation.status}</span>
                    </div>
                    {trace.conversation.started_at && (
                      <div>
                        <span className="text-gray-500">Started:</span>{' '}
                        <span className="text-gray-300">
                          {new Date(trace.conversation.started_at).toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Conversation Topic */}
                  <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                    <div className="text-xs text-blue-400 mb-1">Topic</div>
                    <div className="text-sm">{trace.conversation.topic}</div>
                  </div>

                  {/* Session 899: Actual Conversation Messages */}
                  {trace.conversation.messages && trace.conversation.messages.length > 0 && (
                    <div className="space-y-3">
                      <div className="text-xs text-gray-500 font-medium">Conversation Transcript</div>
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {trace.conversation.messages.map((msg, idx) => (
                          <div
                            key={msg.id || idx}
                            className={cn(
                              'p-3 rounded-lg',
                              idx % 2 === 0
                                ? 'bg-blue-500/5 border border-blue-500/20 ml-0 mr-8'
                                : 'bg-purple-500/5 border border-purple-500/20 ml-8 mr-0'
                            )}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className={cn(
                                'text-xs font-medium',
                                idx % 2 === 0 ? 'text-blue-400' : 'text-purple-400'
                              )}>
                                {msg.agent_name}
                              </span>
                              <span className="text-xs text-gray-500">
                                {msg.message_type}
                              </span>
                            </div>
                            <div className="text-sm text-gray-300 whitespace-pre-wrap">
                              {msg.content}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Conclusion/Synthesis */}
                  {(trace.conversation.conclusion || trace.conversation.synthesis_summary) && (
                    <div className="p-3 bg-green-500/5 border border-green-500/20 rounded-lg">
                      <div className="text-xs text-green-400 mb-1">Conclusion</div>
                      <div className="text-sm text-gray-300">
                        {trace.conversation.conclusion || trace.conversation.synthesis_summary}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* STAGES SECTION */}
          <div className="border border-dark-border rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('stages')}
              className="w-full flex items-center justify-between p-4 bg-dark-bg hover:bg-dark-bg/80 transition-colors"
            >
              <div className="flex items-center gap-3">
                <GitBranch size={18} className="text-green-400" />
                <span className="font-medium">Pipeline Stages</span>
                <span className="text-sm text-gray-400">
                  {trace.stages.filter(s => s.status === 'APPROVED').length} of 5 approved
                </span>
              </div>
              {expandedSections.stages ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {expandedSections.stages && (
              <div className="p-4 border-t border-dark-border space-y-3">
                {trace.stages.map((stage) => (
                  <div
                    key={stage.stage}
                    className={cn(
                      'flex items-center gap-4 p-3 rounded-lg border transition-colors',
                      stage.status === 'APPROVED' && 'bg-green-500/5 border-green-500/30',
                      stage.status === 'DRAFT' && 'bg-yellow-500/5 border-yellow-500/30',
                      stage.status === 'PENDING' && 'bg-dark-bg border-dark-border',
                    )}
                  >
                    <div className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold',
                      stage.status === 'APPROVED' && 'bg-green-500/20 text-green-400',
                      stage.status === 'DRAFT' && 'bg-yellow-500/20 text-yellow-400',
                      stage.status === 'PENDING' && 'bg-dark-border text-gray-500',
                    )}>
                      {stage.status === 'APPROVED' ? <CheckCircle2 size={20} /> : stage.stage}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{stage.name}</div>
                      <div className="text-xs text-gray-400">
                        {stage.status === 'APPROVED' && stage.approved_at
                          ? `Approved ${new Date(stage.approved_at).toLocaleDateString()}`
                          : stage.status}
                      </div>
                    </div>
                    {stage.document_id && (
                      <button
                        onClick={() => setViewingDocument({ id: stage.document_id!, stageName: stage.name })}
                        className="flex items-center gap-2 px-3 py-2 bg-primary-500/10 hover:bg-primary-500/20 rounded-lg text-primary-400 text-sm transition-colors"
                      >
                        <Eye size={14} />
                        View Document
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* DELIVERABLE SECTION */}
          {trace.deliverable && (
            <div className="border border-dark-border rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('deliverable')}
                className="w-full flex items-center justify-between p-4 bg-dark-bg hover:bg-dark-bg/80 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <BookOpen size={18} className="text-emerald-400" />
                  <span className="font-medium">Final Deliverable</span>
                  <span className={cn(
                    'px-2 py-0.5 rounded text-xs',
                    trace.deliverable.status === 'published' && 'bg-green-500/20 text-green-400',
                    trace.deliverable.status === 'draft' && 'bg-yellow-500/20 text-yellow-400',
                  )}>
                    {trace.deliverable.status}
                  </span>
                </div>
                {expandedSections.deliverable ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </button>

              {expandedSections.deliverable && (
                <div className="p-4 border-t border-dark-border">
                  <div className="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
                    <div className="font-medium mb-2">{trace.deliverable.title}</div>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>{trace.deliverable.deliverable_type}</span>
                      <span>{Math.round(trace.deliverable.content_length / 1000)}k characters</span>
                      <span>{new Date(trace.deliverable.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* FLOW VISUALIZATION */}
          <div className="p-4 bg-dark-bg rounded-lg">
            <div className="text-xs text-gray-500 mb-3">Complete Journey</div>
            <div className="flex items-center justify-center gap-2 text-xs flex-wrap">
              {/* Session 900: Show signal-driven origin if present */}
              {trace.origin_signals?.signal_cluster && (
                <>
                  <span className="px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded flex items-center gap-1">
                    <Radio size={10} />
                    {trace.origin_signals.signal_cluster.total_signals ||
                     Object.values(trace.origin_signals.signal_cluster.source_breakdown || {}).reduce((a: number, b: unknown) => a + (Number(b) || 0), 0)} Signals
                  </span>
                  <ArrowRight size={12} className="text-gray-500" />
                </>
              )}
              {trace.origin_signals?.auto_topic && (
                <>
                  <span className="px-2 py-1 bg-orange-500/10 text-orange-400 rounded flex items-center gap-1">
                    <Target size={10} />
                    Auto Topic
                  </span>
                  <ArrowRight size={12} className="text-gray-500" />
                </>
              )}
              {trace.trigger && !trace.origin_signals?.signal_cluster && (
                <>
                  <span className="px-2 py-1 bg-yellow-500/10 text-yellow-400 rounded">
                    {trace.trigger.type} Trigger
                  </span>
                  <ArrowRight size={12} className="text-gray-500" />
                </>
              )}
              {trace.conversation && (
                <>
                  <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded">
                    {trace.conversation.message_count || trace.conversation.contribution_count || '?'} Messages
                  </span>
                  <ArrowRight size={12} className="text-gray-500" />
                </>
              )}
              {trace.decision && (
                <>
                  <span className="px-2 py-1 bg-purple-500/10 text-purple-400 rounded">Decision</span>
                  <ArrowRight size={12} className="text-gray-500" />
                </>
              )}
              <span className="px-2 py-1 bg-primary-500/10 text-primary-400 rounded">Initiative</span>
              <ArrowRight size={12} className="text-gray-500" />
              <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded">
                {trace.stages.filter(s => s.status === 'APPROVED').length} Stages
              </span>
              {trace.deliverable && (
                <>
                  <ArrowRight size={12} className="text-gray-500" />
                  <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded">
                    Deliverable
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-dark-border bg-dark-bg/50 shrink-0">
          <div className="text-xs text-gray-400">
            Created: {new Date(trace.initiative.created_at).toLocaleDateString()} •
            Updated: {new Date(trace.initiative.updated_at).toLocaleDateString()}
          </div>
          <button onClick={onClose} className="btn btn-ghost">Close</button>
        </div>

        {/* Document Viewer Modal */}
        {viewingDocument && (
          <DocumentViewerModal
            documentId={viewingDocument.id}
            stageName={viewingDocument.stageName}
            initiativeName={trace.initiative.name}
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
  // Session 898: Track comprehensive modal separately for completed initiatives
  const [comprehensiveInitiativeId, setComprehensiveInitiativeId] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'active' | 'completed' | 'stale' | 'blocked'>('all')

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
    // Session 898: Filter by completed status
    if (filter === 'completed') return init.status === 'COMPLETED'
    return health === filter
  })

  // Stats
  const stats = {
    total: data?.initiatives?.length || 0,
    active: data?.initiatives?.filter((i) => i.status === 'ACTIVE').length || 0,
    // Session 898: Track completed initiatives for comprehensive view
    completed: data?.initiatives?.filter((i) => i.status === 'COMPLETED').length || 0,
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
            {/* Session 898: Completed filter for comprehensive view */}
            {stats.completed > 0 && (
              <button
                onClick={() => setFilter('completed')}
                className={cn(
                  'px-3 py-1 rounded-full transition-colors flex items-center gap-1',
                  filter === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'text-gray-400 hover:text-white'
                )}
              >
                <Trophy size={14} />
                Completed ({stats.completed})
              </button>
            )}
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
            onViewDetails={() => {
              // Session 898: Open comprehensive modal for completed initiatives
              if (initiative.status === 'COMPLETED') {
                setComprehensiveInitiativeId(initiative.id)
              } else {
                setSelectedInitiative(initiative)
              }
            }}
          />
        ))}
      </div>

      {filteredInitiatives.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          No initiatives match the selected filter
        </div>
      )}

      {/* Detail modal - Basic view for active initiatives */}
      {selectedInitiative && (
        <InitiativeDetailModal
          initiative={selectedInitiative}
          onClose={() => setSelectedInitiative(null)}
        />
      )}

      {/* Session 898: Comprehensive modal for completed initiatives */}
      {comprehensiveInitiativeId && (
        <ComprehensiveInitiativeModal
          initiativeId={comprehensiveInitiativeId}
          onClose={() => setComprehensiveInitiativeId(null)}
        />
      )}
    </div>
  )
}
