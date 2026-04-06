// Session 847: Initiative Pipeline Dashboard
// Session 898: Added Completed filter and comprehensive origin trace view
// ChatGPT feedback: "Build 'Initiative Dashboard' View - One screen showing all initiatives"
// Shows: Initiative name, status, owner, progress bar (Stage 1-5), health indicator
import { useState } from 'react'
import { useWorkspaceStore } from '@/stores/workspaceStore'
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
  Flame,
  Archive,
  BarChart3,
  Layers,
  DollarSign,
  Shield,
  Beaker,
  Rocket,
  Wrench,
  ListTodo,
  Plus,
  Check,
  Square,
  AlertCircle,
  Play,
  Pause,
  List,
  LayoutGrid,
  Calendar,
  Settings,
  FastForward,
  ShieldCheck,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi, blogsApi } from '@/lib/api'
import { generateDocumentPDF } from '@/lib/pdfExport'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Session 906: Time duration helper for "time in stage" display
function formatTimeDuration(dateString: string): string {
  const created = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - created.getTime()

  const minutes = Math.floor(diffMs / (1000 * 60))
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (days > 0) return `${days}d ${hours % 24}h in stage`
  if (hours > 0) return `${hours}h ${minutes % 60}m in stage`
  if (minutes > 0) return `${minutes}m in stage`
  return 'Just created'
}

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
  // Session 901: Priority and categorization
  purpose?: string
  purpose_display?: string
  program?: string
  program_display?: string
  priority_score?: number
  priority_level?: 'critical' | 'high' | 'medium' | 'low'
  impact_score?: number
  urgency?: number
  confidence?: number
  revenue_potential?: number
  created_at: string
  updated_at: string
}

// Session 901: Stats interface
interface InitiativeStats {
  total: number
  active: number
  completed: number
  archived: number
  on_hold: number
  by_program: Record<string, number>
  by_purpose: Record<string, number>
  by_priority: {
    critical: number
    high: number
    medium: number
    low: number
  }
}

// Session 902: Action Item interface
interface ActionItem {
  id: string
  title: string
  description: string
  assigned_agent: string
  assigned_user_id: number | null
  timeline_text: string
  due_date: string | null
  estimated_hours: number | null
  status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'cancelled'
  priority: 'critical' | 'high' | 'medium' | 'low'
  started_at: string | null
  completed_at: string | null
  completed_by: string
  completion_notes: string
  blocked_reason: string
  is_overdue: boolean
  days_until_due: number | null
  source_conversation_id: string | null
  source_text: string
  order: number
  created_at: string
  updated_at: string
}

interface ActionItemsResponse {
  success: boolean
  initiative_id: string
  initiative_name: string
  count: number
  stats: {
    total: number
    pending: number
    in_progress: number
    completed: number
    blocked: number
    completion_rate: number
  }
  action_items: ActionItem[]
}

// Session 901: Priority indicator component
function PriorityBadge({ level }: { level?: string }) {
  const config = {
    critical: { icon: Flame, color: 'text-red-400 bg-red-500/20', label: 'Critical' },
    high: { icon: TrendingUp, color: 'text-orange-400 bg-orange-500/20', label: 'High' },
    medium: { icon: Circle, color: 'text-yellow-400 bg-yellow-500/20', label: 'Medium' },
    low: { icon: Circle, color: 'text-gray-400 bg-gray-500/20', label: 'Low' },
  }
  const cfg = config[level as keyof typeof config] || config.medium
  const Icon = cfg.icon
  return (
    <span className={cn('px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1', cfg.color)}>
      <Icon size={10} />
      {cfg.label}
    </span>
  )
}

// Session 901: Purpose icon mapping
function PurposeIcon({ purpose }: { purpose?: string }) {
  const icons: Record<string, typeof DollarSign> = {
    revenue: DollarSign,
    stability: Shield,
    learning: Beaker,
    expansion: Rocket,
    maintenance: Wrench,
  }
  const Icon = icons[purpose || 'learning'] || Beaker
  return <Icon size={12} />
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
        !isCompleted && health === 'blocked' && 'border-red-500/30',
        // Session 901: Highlight critical priority
        !isCompleted && initiative.priority_level === 'critical' && 'ring-1 ring-red-500/50'
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
            {/* Session 901: Purpose indicator */}
            {initiative.purpose && (
              <span className="text-gray-500" title={initiative.purpose_display}>
                <PurposeIcon purpose={initiative.purpose} />
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400 truncate">{initiative.description || 'No description'}</p>
        </div>
        <div className="flex items-center gap-2 ml-3">
          {/* Session 901: Priority badge */}
          {!isCompleted && initiative.priority_level && (
            <PriorityBadge level={initiative.priority_level} />
          )}
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
          {/* Session 901: Show program if available */}
          {initiative.program_display && initiative.program !== 'uncategorized' && (
            <span className="text-gray-500">{initiative.program_display}</span>
          )}
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

// Session 904: Compact list row for cleaner initiative display
function InitiativeRow({ initiative, onViewDetails }: { initiative: Initiative; onViewDetails: () => void }) {
  const health = getHealth(initiative)
  const isCompleted = initiative.status === 'COMPLETED'
  const currentStage = initiative.current_stage || 1

  return (
    <div
      className={cn(
        'flex items-center gap-4 px-4 py-3 border-b border-dark-border hover:bg-dark-card/50 transition-colors cursor-pointer group',
        isCompleted && 'bg-emerald-500/5',
        !isCompleted && health === 'blocked' && 'bg-red-500/5',
        !isCompleted && initiative.priority_level === 'critical' && 'border-l-2 border-l-red-500'
      )}
      onClick={onViewDetails}
    >
      {/* Stage indicator - compact colored bar */}
      <div className="flex gap-0.5 w-16 flex-shrink-0">
        {[1, 2, 3, 4, 5].map((stage) => (
          <div
            key={stage}
            className={cn(
              'h-1.5 flex-1 rounded-full',
              stage < currentStage && 'bg-green-500',
              stage === currentStage && 'bg-primary-500',
              stage > currentStage && 'bg-dark-border'
            )}
          />
        ))}
      </div>

      {/* Title - takes up available space */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={cn(
            'font-medium truncate',
            isCompleted && 'text-emerald-400'
          )}>
            {initiative.name}
          </span>
          {/* Only show badges for non-default states */}
          {!isCompleted && initiative.priority_level === 'critical' && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-500/20 text-red-400 flex-shrink-0">
              Critical
            </span>
          )}
          {!isCompleted && initiative.priority_level === 'high' && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-orange-500/20 text-orange-400 flex-shrink-0">
              High
            </span>
          )}
          {!isCompleted && health === 'blocked' && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-500/20 text-red-400 flex-shrink-0">
              Blocked
            </span>
          )}
          {!isCompleted && health === 'stale' && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-yellow-500/20 text-yellow-400 flex-shrink-0">
              Stale
            </span>
          )}
        </div>
      </div>

      {/* Progress - compact */}
      <div className="text-xs text-gray-400 w-20 text-right flex-shrink-0">
        {initiative.completion_percentage}%
        {initiative.approved_percentage > 0 && (
          <span className="text-green-400 ml-1">({initiative.approved_percentage}%)</span>
        )}
      </div>

      {/* Arrow - visible on hover */}
      <ChevronRight size={14} className="text-gray-500 group-hover:text-white transition-colors flex-shrink-0" />
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

  const [contentExpanded, setContentExpanded] = useState(false)

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

        <div className="p-6 overflow-y-auto flex-1 min-h-0">
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
              {/* Session 906: Enhanced document metadata with time tracking */}
              <div className="flex flex-wrap items-center gap-3 text-xs text-gray-400 mb-4 pb-4 border-b border-dark-border">
                {data.word_count && (
                  <span className="flex items-center gap-1">
                    <FileText size={12} />
                    {data.word_count} words
                  </span>
                )}
                {data.created_at && (
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    {new Date(data.created_at).toLocaleDateString()} {new Date(data.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                )}
                {data.created_at && (
                  <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">
                    <Clock size={12} />
                    {formatTimeDuration(data.created_at)}
                  </span>
                )}
                {data.status && (
                  <span className={cn(
                    "px-2 py-0.5 rounded",
                    data.status === 'draft' && "bg-blue-500/20 text-blue-400",
                    data.status === 'published' && "bg-green-500/20 text-green-400",
                    data.status === 'blocked' && "bg-red-500/20 text-red-400",
                  )}>
                    {data.status}
                  </span>
                )}
              </div>

              {/* Session 906: Check for Decision Gate status and show alert banner */}
              {(data.full_text || data.content || '').includes('Insufficient Data') && (
                <div className="mb-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
                  <div className="flex items-center gap-2 text-amber-400 font-medium text-sm">
                    <AlertTriangle size={16} />
                    Awaiting Data Collection
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    Research is blocked on insufficient data. A spider has been spawned to collect more information.
                    The system will automatically retry when data arrives.
                  </p>
                </div>
              )}

              {(data.full_text || data.content || '').includes('✅ Data Available') && (
                <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/30">
                  <div className="flex items-center gap-2 text-green-400 font-medium text-sm">
                    <CheckCircle2 size={16} />
                    Data Available - Ready for Progression
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    This stage has sufficient data and will be auto-progressed to the next stage.
                  </p>
                </div>
              )}

              {/* Session 943: Unified prose styling */}
              <div className="relative">
                <div className={`prose prose-invert prose-dark prose-sm max-w-none ${!contentExpanded ? 'max-h-[400px] overflow-hidden' : ''}`}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {data.full_text || data.content || 'No content available'}
                  </ReactMarkdown>
                </div>
                {!contentExpanded && (
                  <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-dark-card to-transparent pointer-events-none" />
                )}
                <button
                  onClick={() => setContentExpanded(!contentExpanded)}
                  className="mt-2 flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300 transition-colors"
                >
                  {contentExpanded ? (
                    <>
                      <ChevronUp size={14} />
                      Collapse document
                    </>
                  ) : (
                    <>
                      <ChevronDown size={14} />
                      Show full document
                    </>
                  )}
                </button>
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
  const [descriptionExpanded, setDescriptionExpanded] = useState(false)

  // Session 928: Start conversation about initiative
  const [isStartingConversation, setIsStartingConversation] = useState(false)
  const handleStartConversation = async () => {
    setIsStartingConversation(true)
    try {
      const res = await platformApi.startConversation(initiative.id, {
        conversation_type: 'analytical',
        auto_select_agents: true,
      })
      if (res.data.success && res.data.session_url) {
        // Navigate to the conversation
        window.location.href = res.data.session_url
      }
    } catch (error) {
      console.error('Failed to start conversation:', error)
      setIsStartingConversation(false)
    }
  }

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
          <div className="flex-1 min-w-0 mr-4">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold truncate">{initiative.name}</h3>
              <span className={cn(
                'px-2 py-0.5 rounded text-xs shrink-0',
                initiative.status === 'active' ? 'bg-green-500/20 text-green-400' :
                initiative.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                'bg-gray-500/20 text-gray-400'
              )}>
                {initiative.status}
              </span>
            </div>
            <p className="text-sm text-gray-400 line-clamp-2 mt-1">
              {initiative.description || 'No description'}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg transition-colors shrink-0">
            &times;
          </button>
        </div>

        <div className="p-4 space-y-4 overflow-y-auto flex-1 min-h-0">
          {/* Collapsible full description for long content */}
          {initiative.description && initiative.description.length > 200 && (
            <div className="border border-dark-border rounded-lg p-3">
              <button
                onClick={() => setDescriptionExpanded(!descriptionExpanded)}
                className="flex items-center justify-between w-full text-sm"
              >
                <span className="text-gray-400 flex items-center gap-2">
                  <FileText size={14} />
                  Full Description
                </span>
                {descriptionExpanded ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
              </button>
              {descriptionExpanded && (
                <p className="text-sm text-gray-300 mt-2 whitespace-pre-wrap">
                  {initiative.description}
                </p>
              )}
            </div>
          )}

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
          <div className="flex items-center gap-2">
            {/* Session 928: Discuss with Agents button */}
            <button
              onClick={handleStartConversation}
              disabled={isStartingConversation}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-primary-500 hover:bg-primary-600 disabled:bg-primary-500/50 text-white rounded-lg transition-colors"
            >
              {isStartingConversation ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <MessageSquare size={16} />
              )}
              Discuss with Agents
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
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
  const queryClient = useQueryClient()
  const [viewingDocument, setViewingDocument] = useState<{ id: string; stageName: string } | null>(null)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    origin: true,
    conversation: false,
    stages: true,
    rhythm: true,  // Session 914.7: Operating Rhythm section
    actionItems: true,
    deliverable: true,
    description: false,
  })
  const [newActionTitle, setNewActionTitle] = useState('')

  const { data, isLoading, isError } = useQuery({
    queryKey: ['initiative-trace', initiativeId],
    queryFn: async () => {
      const res = await platformApi.originTrace(initiativeId)
      return res.data
    },
  })

  // Session 914.7: Fetch operating rhythm data for this initiative
  const { data: rhythmData } = useQuery({
    queryKey: ['initiative-rhythm', initiativeId],
    queryFn: async () => {
      const res = await fetch(`/api/initiatives/${initiativeId}/rhythm/`, {
        credentials: 'include',
      })
      if (!res.ok) throw new Error('Failed to fetch rhythm data')
      return res.json()
    },
  })

  // Session 902: Fetch action items
  // Session 907: Added credentials: 'include' to fix 401 errors
  const { data: actionItemsData, isLoading: actionItemsLoading } = useQuery({
    queryKey: ['initiative-action-items', initiativeId],
    queryFn: async () => {
      const res = await fetch(`/api/initiatives/${initiativeId}/action-items/`, {
        credentials: 'include',
      })
      if (!res.ok) throw new Error('Failed to fetch action items')
      return res.json() as Promise<ActionItemsResponse>
    },
  })

  // Session 902: Update action item status
  // Session 907: Added credentials: 'include' to fix 401 errors
  const updateActionItem = useMutation({
    mutationFn: async ({ itemId, updates }: { itemId: string; updates: Record<string, unknown> }) => {
      const res = await fetch(`/api/action-items/${itemId}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(updates),
      })
      if (!res.ok) throw new Error('Failed to update action item')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiative-action-items', initiativeId] })
    },
  })

  // Session 902: Create action item
  // Session 907: Added credentials: 'include' to fix 401 errors
  const createActionItem = useMutation({
    mutationFn: async (title: string) => {
      const res = await fetch(`/api/initiatives/${initiativeId}/action-items/create/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ title, priority: 'medium' }),
      })
      if (!res.ok) throw new Error('Failed to create action item')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiative-action-items', initiativeId] })
      setNewActionTitle('')
    },
  })

  // Session 902: Extract action items from conversations
  // Session 907: Added credentials: 'include' to fix 401 errors
  const extractActionItems = useMutation({
    mutationFn: async () => {
      const res = await fetch(`/api/initiatives/${initiativeId}/action-items/extract/`, {
        method: 'POST',
        credentials: 'include',
      })
      if (!res.ok) throw new Error('Failed to extract action items')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiative-action-items', initiativeId] })
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
            <div className="flex-1 min-w-0 mr-4">
              <div className="flex items-center gap-3 mb-2">
                {trace.initiative.status === 'COMPLETED' ? (
                  <Trophy size={24} className="text-green-400 shrink-0" />
                ) : (
                  <FolderKanban size={24} className="text-primary-400 shrink-0" />
                )}
                <h2 className="text-xl font-bold truncate">{trace.initiative.name}</h2>
              </div>
              <p className="text-gray-400 text-sm mb-4 line-clamp-2">{trace.initiative.description}</p>

              {/* Session 907: Stage Completion + Priority/Purpose badges */}
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-dark-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
                      style={{ width: `${(trace.stages.filter(s => s.status === 'APPROVED').length / 5) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-green-400 font-medium">
                    {trace.stages.filter(s => s.status === 'APPROVED').length}/5 Stages
                  </span>
                </div>
                <span className={cn(
                  'px-2 py-1 rounded text-xs font-medium',
                  trace.initiative.status === 'COMPLETED' && 'bg-green-500/20 text-green-400',
                  trace.initiative.status === 'ACTIVE' && 'bg-blue-500/20 text-blue-400',
                )}>
                  {trace.initiative.status}
                </span>
                {/* Session 904: Show priority if set */}
                {trace.initiative.priority_level && trace.initiative.priority_level !== 'medium' && (
                  <span className={cn(
                    'px-2 py-1 rounded text-xs font-medium flex items-center gap-1',
                    trace.initiative.priority_level === 'critical' && 'bg-red-500/20 text-red-400',
                    trace.initiative.priority_level === 'high' && 'bg-orange-500/20 text-orange-400',
                    trace.initiative.priority_level === 'low' && 'bg-gray-500/20 text-gray-400',
                  )}>
                    {trace.initiative.priority_level === 'critical' && <Flame size={10} />}
                    {trace.initiative.priority_level.charAt(0).toUpperCase() + trace.initiative.priority_level.slice(1)} Priority
                  </span>
                )}
                {/* Session 904: Show purpose if set */}
                {trace.initiative.purpose && trace.initiative.purpose !== 'uncategorized' && (
                  <span className="px-2 py-1 rounded text-xs font-medium bg-purple-500/20 text-purple-400 flex items-center gap-1">
                    <PurposeIcon purpose={trace.initiative.purpose} />
                    {trace.initiative.purpose_display || trace.initiative.purpose}
                  </span>
                )}
              </div>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg shrink-0">
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
                {/* Session 907: Sum all stage document content lengths */}
                {(() => {
                  const totalChars = trace.stages.reduce((sum, s) => sum + (s.content_length || 0), 0);
                  return totalChars > 0 ? Math.round(totalChars / 1000) + 'k' : '—';
                })()}
              </div>
              <div className="text-xs text-gray-400">Content (chars)</div>
            </div>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto min-h-0 p-6 space-y-6">

          {/* Collapsible full description for long content */}
          {trace.initiative.description && trace.initiative.description.length > 200 && (
            <div className="border border-dark-border rounded-lg p-3">
              <button
                onClick={() => toggleSection('description')}
                className="flex items-center justify-between w-full text-sm"
              >
                <span className="text-gray-400 flex items-center gap-2">
                  <FileText size={14} />
                  Full Description
                </span>
                {expandedSections.description ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
              </button>
              {expandedSections.description && (
                <p className="text-sm text-gray-300 mt-2 whitespace-pre-wrap">
                  {trace.initiative.description}
                </p>
              )}
            </div>
          )}

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
                    <div className="flex items-center justify-between mb-1">
                      <div className="text-xs text-yellow-400">Trigger</div>
                      {trace.trigger.confidence && (
                        <span className="text-xs text-yellow-400">
                          {(trace.trigger.confidence * 100).toFixed(0)}% confidence
                        </span>
                      )}
                    </div>
                    <div className="font-medium">{trace.trigger.description}</div>
                  </div>
                )}

                {/* Session 904: Conversation Summary - shows synthesis and stats */}
                {trace.conversation && (
                  <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-blue-400">Conversation Summary</div>
                      <div className="flex items-center gap-3 text-xs text-gray-400">
                        {trace.conversation.contribution_count > 0 && (
                          <span>{trace.conversation.contribution_count} contributions</span>
                        )}
                        {trace.conversation.total_thinking_time > 0 && (
                          <span>{Math.round(trace.conversation.total_thinking_time / 1000)}s thinking</span>
                        )}
                      </div>
                    </div>
                    {trace.conversation.topic && (
                      <div className="text-sm">
                        <span className="text-gray-500">Topic:</span>{' '}
                        <span className="text-gray-300">{trace.conversation.topic}</span>
                      </div>
                    )}
                    {/* Session 904: Show objective if available */}
                    {trace.conversation.objective && (
                      <div className="text-sm">
                        <span className="text-gray-500">Objective:</span>{' '}
                        <span className="text-gray-300">{trace.conversation.objective}</span>
                      </div>
                    )}
                    {/* Session 904: Show success criteria if available */}
                    {trace.conversation.success_criteria && trace.conversation.success_criteria.length > 0 && (
                      <div className="text-sm">
                        <div className="text-gray-500 mb-1">Success Criteria:</div>
                        <ul className="list-disc list-inside text-gray-400 text-xs space-y-0.5">
                          {trace.conversation.success_criteria.slice(0, 5).map((criteria: string, idx: number) => (
                            <li key={idx}>{criteria}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {trace.conversation.synthesis_summary && (
                      <div className="text-sm text-gray-400 bg-dark-bg/50 p-2 rounded border-l-2 border-blue-500/30">
                        <div className="text-xs text-blue-400 mb-1">Synthesis</div>
                        {trace.conversation.synthesis_summary}
                      </div>
                    )}
                    {(trace.conversation.started_at || trace.conversation.completed_at) && (
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        {trace.conversation.started_at && (
                          <span>Started: {new Date(trace.conversation.started_at).toLocaleString()}</span>
                        )}
                        {trace.conversation.completed_at && (
                          <span>Completed: {new Date(trace.conversation.completed_at).toLocaleString()}</span>
                        )}
                      </div>
                    )}
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

          {/* SESSION 904: LIVE ACTIVITY SECTION */}
          {trace.active_work && trace.active_work.length > 0 && (
            <div className="border border-cyan-500/30 rounded-lg overflow-hidden bg-cyan-500/5">
              <div className="flex items-center gap-3 p-4 border-b border-cyan-500/20">
                <div className="relative">
                  <Loader2 size={18} className="text-cyan-400 animate-spin" />
                  <span className="absolute -top-1 -right-1 w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                </div>
                <span className="font-medium text-cyan-400">Live Activity</span>
                <span className="text-sm text-gray-400">{trace.active_work.filter(w => w.status !== 'completed').length} active</span>
              </div>
              <div className="p-4 space-y-3">
                {trace.active_work.map((work) => (
                  <div
                    key={work.id}
                    className={cn(
                      'flex items-center gap-4 p-3 rounded-lg border',
                      work.status === 'running' && 'bg-cyan-500/10 border-cyan-500/30',
                      work.status === 'completed' && 'bg-green-500/5 border-green-500/20',
                      work.status === 'pending' && 'bg-yellow-500/5 border-yellow-500/20',
                    )}
                  >
                    {/* Agent icon */}
                    <div className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center',
                      work.status === 'running' && 'bg-cyan-500/20',
                      work.status === 'completed' && 'bg-green-500/20',
                      work.status === 'pending' && 'bg-yellow-500/20',
                    )}>
                      {work.status === 'running' ? (
                        <Loader2 size={18} className="text-cyan-400 animate-spin" />
                      ) : work.status === 'completed' ? (
                        <CheckCircle2 size={18} className="text-green-400" />
                      ) : (
                        <Clock size={18} className="text-yellow-400" />
                      )}
                    </div>
                    {/* Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white">{work.agent_name}</span>
                        {work.stage_num && (
                          <span className="px-1.5 py-0.5 rounded text-xs bg-dark-border text-gray-400">
                            Stage {work.stage_num}
                          </span>
                        )}
                        <span className={cn(
                          'px-1.5 py-0.5 rounded text-xs',
                          work.status === 'running' && 'bg-cyan-500/20 text-cyan-400',
                          work.status === 'completed' && 'bg-green-500/20 text-green-400',
                          work.status === 'pending' && 'bg-yellow-500/20 text-yellow-400',
                        )}>
                          {work.status}
                        </span>
                      </div>
                      {work.current_step && (
                        <div className="text-sm text-gray-400 truncate">{work.current_step}</div>
                      )}
                      {work.task_description && !work.current_step && (
                        <div className="text-sm text-gray-500 truncate">{work.task_description}</div>
                      )}
                    </div>
                    {/* Progress */}
                    {work.status === 'running' && work.progress_percentage > 0 && (
                      <div className="text-right">
                        <div className="text-sm font-medium text-cyan-400">{work.progress_percentage}%</div>
                        <div className="w-16 h-1.5 bg-dark-border rounded-full overflow-hidden">
                          <div
                            className="h-full bg-cyan-400 transition-all"
                            style={{ width: `${work.progress_percentage}%` }}
                          />
                        </div>
                      </div>
                    )}
                    {work.status === 'completed' && work.execution_time_seconds && (
                      <div className="text-xs text-gray-500">
                        {work.execution_time_seconds}s
                      </div>
                    )}
                  </div>
                ))}
              </div>
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

          {/* SESSION 914.7: OPERATING RHYTHM SECTION */}
          <div className="border border-dark-border rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('rhythm')}
              className="w-full flex items-center justify-between p-4 bg-dark-bg hover:bg-dark-bg/80 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Calendar size={18} className="text-emerald-400" />
                <span className="font-medium">Operating Rhythm</span>
                {rhythmData?.is_daily_focus && (
                  <span className="px-2 py-0.5 rounded text-xs bg-emerald-500/20 text-emerald-400 flex items-center gap-1">
                    <Sparkles size={10} />
                    Daily Focus
                  </span>
                )}
                {rhythmData?.founder_intent?.set && (
                  <span className="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400">
                    Intent Set
                  </span>
                )}
                {!rhythmData?.can_auto_progress && rhythmData?.progression_blocked_reason && (
                  <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400 flex items-center gap-1">
                    <AlertCircle size={10} />
                    Blocked
                  </span>
                )}
              </div>
              {expandedSections.rhythm ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {expandedSections.rhythm && rhythmData?.success && (
              <div className="p-4 border-t border-dark-border space-y-4">
                {/* Progression Status */}
                <div className={cn(
                  "p-3 rounded-lg flex items-center gap-3",
                  rhythmData.can_auto_progress
                    ? "bg-green-500/10 border border-green-500/20"
                    : "bg-yellow-500/10 border border-yellow-500/20"
                )}>
                  {rhythmData.can_auto_progress ? (
                    <>
                      <CheckCircle2 size={18} className="text-green-400" />
                      <span className="text-green-400 font-medium">Ready to Progress</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle size={18} className="text-yellow-400" />
                      <div>
                        <span className="text-yellow-400 font-medium">Progression Blocked</span>
                        <p className="text-sm text-gray-400 mt-0.5">{rhythmData.progression_blocked_reason}</p>
                      </div>
                    </>
                  )}
                </div>

                {/* Daily Focus Status */}
                {rhythmData.is_daily_focus && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center gap-3">
                    <Sparkles size={18} className="text-emerald-400" />
                    <div>
                      <span className="text-emerald-400 font-medium">In Today's Daily Focus</span>
                      {rhythmData.daily_focus_date && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Since {new Date(rhythmData.daily_focus_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Daily Priorities */}
                {rhythmData.daily_priorities?.priorities?.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Target size={12} />
                      Today's Priorities
                      {!rhythmData.daily_priorities.is_current && (
                        <span className="px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400">Stale</span>
                      )}
                    </div>
                    <div className="space-y-1">
                      {rhythmData.daily_priorities.priorities.map((priority: string, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 text-sm">
                          <span className="w-5 h-5 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center text-xs font-bold">
                            {idx + 1}
                          </span>
                          <span className={cn(
                            rhythmData.priority_mapping?.is_mapped && rhythmData.priority_mapping?.priority_index === idx
                              ? "text-primary-400 font-medium"
                              : "text-gray-400"
                          )}>
                            {priority}
                          </span>
                          {rhythmData.priority_mapping?.is_mapped && rhythmData.priority_mapping?.priority_index === idx && (
                            <span className="text-xs text-primary-400">← Mapped</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Founder Intent */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-dark-bg/50 rounded-lg">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                      <Settings size={12} />
                      Founder Intent
                    </div>
                    {rhythmData.founder_intent?.set ? (
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <FastForward size={12} className="text-blue-400" />
                          <span className="text-sm capitalize">{rhythmData.founder_intent.execution_speed || 'balanced'}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Shield size={12} className="text-purple-400" />
                          <span className="text-sm capitalize">{rhythmData.founder_intent.risk_tolerance || 'medium'} risk</span>
                        </div>
                        {rhythmData.founder_intent.stop_rule && (
                          <div className="text-xs text-gray-400 mt-1 italic">
                            Stop: {rhythmData.founder_intent.stop_rule.slice(0, 50)}...
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-yellow-400">Not Set</span>
                    )}
                  </div>

                  <div className="p-3 bg-dark-bg/50 rounded-lg">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                      <ShieldCheck size={12} />
                      Boardroom
                    </div>
                    {rhythmData.boardroom?.required ? (
                      <div className="space-y-1">
                        {rhythmData.boardroom.approved ? (
                          <>
                            <span className="text-sm text-green-400 flex items-center gap-1">
                              <CheckCircle2 size={12} />
                              Approved
                            </span>
                            {rhythmData.boardroom.approved_by && (
                              <div className="text-xs text-gray-400">
                                by {rhythmData.boardroom.approved_by}
                              </div>
                            )}
                          </>
                        ) : (
                          <span className="text-sm text-yellow-400">Pending Approval</span>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">Not Required</span>
                    )}
                  </div>
                </div>

                {/* Execution Track */}
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-gray-400">Track:</span>
                  <span className={cn(
                    "px-2 py-0.5 rounded text-xs font-medium",
                    rhythmData.execution_track === 'fast_track' && "bg-blue-500/20 text-blue-400",
                    rhythmData.execution_track === 'institutional' && "bg-purple-500/20 text-purple-400",
                    rhythmData.execution_track === 'not_set' && "bg-gray-500/20 text-gray-400"
                  )}>
                    {rhythmData.execution_track === 'fast_track' ? 'Fast Track (Stage 1-2)' :
                     rhythmData.execution_track === 'institutional' ? 'Institutional (Full 5-Stage)' :
                     'Not Set'}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* SESSION 902: ACTION ITEMS SECTION */}
          <div className="border border-dark-border rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('actionItems')}
              className="w-full flex items-center justify-between p-4 bg-dark-bg hover:bg-dark-bg/80 transition-colors"
            >
              <div className="flex items-center gap-3">
                <ListTodo size={18} className="text-purple-400" />
                <span className="font-medium">Action Items</span>
                {actionItemsData?.stats && (
                  <span className="text-sm text-gray-400">
                    {actionItemsData.stats.completed}/{actionItemsData.stats.total} completed
                    {actionItemsData.stats.completion_rate > 0 && (
                      <span className="ml-1 text-green-400">({actionItemsData.stats.completion_rate}%)</span>
                    )}
                  </span>
                )}
              </div>
              {expandedSections.actionItems ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {expandedSections.actionItems && (
              <div className="p-4 border-t border-dark-border space-y-4">
                {/* Stats bar */}
                {actionItemsData?.stats && actionItemsData.stats.total > 0 && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="flex items-center gap-1 px-2 py-1 bg-gray-500/10 rounded text-gray-400">
                      <Circle size={8} /> {actionItemsData.stats.pending} pending
                    </span>
                    <span className="flex items-center gap-1 px-2 py-1 bg-blue-500/10 rounded text-blue-400">
                      <Play size={8} /> {actionItemsData.stats.in_progress} in progress
                    </span>
                    <span className="flex items-center gap-1 px-2 py-1 bg-green-500/10 rounded text-green-400">
                      <Check size={8} /> {actionItemsData.stats.completed} completed
                    </span>
                    {actionItemsData.stats.blocked > 0 && (
                      <span className="flex items-center gap-1 px-2 py-1 bg-red-500/10 rounded text-red-400">
                        <Pause size={8} /> {actionItemsData.stats.blocked} blocked
                      </span>
                    )}
                  </div>
                )}

                {/* Action buttons */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => extractActionItems.mutate()}
                    disabled={extractActionItems.isPending}
                    className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/10 hover:bg-purple-500/20 rounded text-purple-400 text-sm transition-colors disabled:opacity-50"
                  >
                    {extractActionItems.isPending ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : (
                      <Sparkles size={14} />
                    )}
                    Extract from Conversations
                  </button>
                </div>

                {/* Add new action item */}
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newActionTitle}
                    onChange={(e) => setNewActionTitle(e.target.value)}
                    placeholder="Add new action item..."
                    className="flex-1 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:outline-none focus:border-primary-500"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && newActionTitle.trim()) {
                        createActionItem.mutate(newActionTitle.trim())
                      }
                    }}
                  />
                  <button
                    onClick={() => newActionTitle.trim() && createActionItem.mutate(newActionTitle.trim())}
                    disabled={!newActionTitle.trim() || createActionItem.isPending}
                    className="p-2 bg-primary-500/10 hover:bg-primary-500/20 rounded-lg text-primary-400 disabled:opacity-50 transition-colors"
                  >
                    {createActionItem.isPending ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Plus size={16} />
                    )}
                  </button>
                </div>

                {/* Action items list */}
                {actionItemsLoading ? (
                  <div className="flex items-center justify-center py-4">
                    <Loader2 size={20} className="animate-spin text-gray-400" />
                  </div>
                ) : actionItemsData?.action_items && actionItemsData.action_items.length > 0 ? (
                  <div className="space-y-2">
                    {actionItemsData.action_items.map((item) => (
                      <div
                        key={item.id}
                        className={cn(
                          'flex items-start gap-3 p-3 rounded-lg border transition-colors',
                          item.status === 'completed' && 'bg-green-500/5 border-green-500/30 opacity-60',
                          item.status === 'in_progress' && 'bg-blue-500/5 border-blue-500/30',
                          item.status === 'blocked' && 'bg-red-500/5 border-red-500/30',
                          item.status === 'pending' && 'bg-dark-bg border-dark-border',
                        )}
                      >
                        {/* Checkbox */}
                        <button
                          onClick={() => {
                            const newStatus = item.status === 'completed' ? 'pending' :
                                            item.status === 'pending' ? 'in_progress' :
                                            item.status === 'in_progress' ? 'completed' : item.status
                            updateActionItem.mutate({ itemId: item.id, updates: { status: newStatus } })
                          }}
                          className={cn(
                            'mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors shrink-0',
                            item.status === 'completed' && 'bg-green-500 border-green-500 text-white',
                            item.status === 'in_progress' && 'bg-blue-500/20 border-blue-500',
                            item.status === 'blocked' && 'bg-red-500/20 border-red-500',
                            item.status === 'pending' && 'border-gray-500 hover:border-gray-400',
                          )}
                        >
                          {item.status === 'completed' && <Check size={12} />}
                          {item.status === 'in_progress' && <Play size={10} />}
                          {item.status === 'blocked' && <Pause size={10} />}
                        </button>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className={cn(
                            'font-medium text-sm',
                            item.status === 'completed' && 'line-through text-gray-500'
                          )}>
                            {item.title}
                          </div>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            {item.assigned_agent && (
                              <span className="text-xs px-1.5 py-0.5 bg-purple-500/10 text-purple-400 rounded">
                                {item.assigned_agent}
                              </span>
                            )}
                            {item.timeline_text && (
                              <span className="text-xs px-1.5 py-0.5 bg-gray-500/10 text-gray-400 rounded flex items-center gap-1">
                                <Clock size={10} />
                                {item.timeline_text}
                              </span>
                            )}
                            {item.is_overdue && (
                              <span className="text-xs px-1.5 py-0.5 bg-red-500/10 text-red-400 rounded flex items-center gap-1">
                                <AlertCircle size={10} />
                                Overdue
                              </span>
                            )}
                            <span className={cn(
                              'text-xs px-1.5 py-0.5 rounded',
                              item.priority === 'critical' && 'bg-red-500/10 text-red-400',
                              item.priority === 'high' && 'bg-orange-500/10 text-orange-400',
                              item.priority === 'medium' && 'bg-yellow-500/10 text-yellow-400',
                              item.priority === 'low' && 'bg-gray-500/10 text-gray-400',
                            )}>
                              {item.priority}
                            </span>
                          </div>
                          {item.blocked_reason && (
                            <div className="mt-2 text-xs text-red-400 bg-red-500/10 px-2 py-1 rounded">
                              Blocked: {item.blocked_reason}
                            </div>
                          )}
                        </div>

                        {/* Priority toggle */}
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => {
                              const priorities = ['low', 'medium', 'high', 'critical']
                              const currentIdx = priorities.indexOf(item.priority)
                              const nextPriority = priorities[(currentIdx + 1) % priorities.length]
                              updateActionItem.mutate({ itemId: item.id, updates: { priority: nextPriority } })
                            }}
                            className="p-1 hover:bg-dark-border rounded text-gray-400 hover:text-white transition-colors"
                            title="Change priority"
                          >
                            <Flame size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-500">
                    <ListTodo size={24} className="mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No action items yet</p>
                    <p className="text-xs mt-1">Click "Extract from Conversations" to find action items</p>
                  </div>
                )}
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
  // Session 901: Tab-based navigation
  // Session 921: Added 'health' tab for pipeline health monitoring
  const [activeTab, setActiveTab] = useState<'active' | 'portfolio' | 'archive' | 'stats' | 'health'>('active')
  const [filter, setFilter] = useState<'all' | 'active' | 'completed' | 'stale' | 'blocked'>('all')
  // Session 901: Expanded program groups
  const [expandedPrograms, setExpandedPrograms] = useState<Record<string, boolean>>({})
  // Session 904: View mode toggle - stages groups by pipeline progress
  const [viewMode, setViewMode] = useState<'list' | 'cards' | 'stages'>('stages')
  // Session 904: Expanded stages for stage view
  const [expandedStages, setExpandedStages] = useState<Record<number, boolean>>({1: true, 2: true, 3: true, 4: true, 5: true})

  const activeWsId = useWorkspaceStore(s => s.activeWorkspace?.id)

  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['initiatives', activeWsId],
    queryFn: async () => {
      const res = await platformApi.initiatives(
        activeWsId ? { workspace: activeWsId } : undefined
      )
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Session 921: Pipeline health monitoring - real-time progress visibility
  // Session 928: Fixed to use platformApi for auth
  const {
    data: pipelineHealth,
    isLoading: healthLoading,
    refetch: refetchHealth,
  } = useQuery({
    queryKey: ['pipeline-health'],
    queryFn: async () => {
      const res = await platformApi.pipelineHealth()
      return res.data
    },
    refetchInterval: 15000, // Refresh every 15 seconds for real-time feel
    enabled: activeTab === 'health', // Only fetch when on health tab
  })

  // Session 928: Blocker analysis - WHY initiatives are stuck
  const {
    data: blockerAnalysis,
    isLoading: blockerLoading,
  } = useQuery({
    queryKey: ['blocker-analysis'],
    queryFn: async () => {
      const res = await platformApi.diagnoseStuck(100)
      return res.data
    },
    refetchInterval: 60000, // Refresh every minute
    enabled: activeTab === 'health', // Only fetch when on health tab
  })

  const [populateMessage, setPopulateMessage] = useState<string | null>(null)

  const populateMutation = useMutation({
    mutationFn: () => platformApi.populateInitiatives(),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] })
      const data = res.data as { message?: string; created_count?: number }
      if (data.created_count && data.created_count > 0) {
        setPopulateMessage(data.message || `Created ${data.created_count} initiatives`)
      } else {
        setPopulateMessage('No new initiatives to create — all deliverables are already linked or have fewer than 3 items per group.')
      }
      setTimeout(() => setPopulateMessage(null), 6000)
    },
    onError: (err) => {
      setPopulateMessage(`Error: ${err instanceof Error ? err.message : 'Failed to populate'}`)
      setTimeout(() => setPopulateMessage(null), 6000)
    },
  })

  // Session 901: Get stats from API response
  const stats: InitiativeStats = data?.stats || {
    total: 0,
    active: 0,
    completed: 0,
    archived: 0,
    on_hold: 0,
    by_program: {},
    by_purpose: {},
    by_priority: { critical: 0, high: 0, medium: 0, low: 0 },
  }

  // Filter initiatives based on active tab
  const filteredInitiatives = (data?.initiatives || []).filter((init) => {
    if (activeTab === 'active') {
      // Active tab: show ACTIVE and ON_HOLD, filter by health
      if (init.status !== 'ACTIVE' && init.status !== 'ON_HOLD') return false
      if (filter === 'all') return true
      const health = getHealth(init)
      if (filter === 'active') return init.status === 'ACTIVE'
      if (filter === 'completed') return false // No completed in active tab
      return health === filter
    }
    if (activeTab === 'portfolio') {
      // Portfolio: show all active initiatives
      return init.status === 'ACTIVE' || init.status === 'ON_HOLD'
    }
    if (activeTab === 'archive') {
      // Archive: completed and archived
      return init.status === 'COMPLETED' || init.status === 'ARCHIVED'
    }
    return true
  })

  // Session 901: Group initiatives by program for portfolio view
  const groupedByProgram = filteredInitiatives.reduce((acc, init) => {
    const program = init.program || 'uncategorized'
    if (!acc[program]) acc[program] = []
    acc[program].push(init)
    return acc
  }, {} as Record<string, Initiative[]>)

  // Toggle program expansion
  const toggleProgram = (program: string) => {
    setExpandedPrograms(prev => ({ ...prev, [program]: !prev[program] }))
  }

  // Session 901: Calculate health-based stats locally
  const healthStats = {
    stale: data?.initiatives?.filter((i: Initiative) => getHealth(i) === 'stale').length || 0,
    blocked: data?.initiatives?.filter((i: Initiative) => getHealth(i) === 'blocked').length || 0,
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
    return (
      <div>
        <EmptyState onPopulate={() => populateMutation.mutate()} isPopulating={populateMutation.isPending} />
        {populateMessage && (
          <div className={cn(
            'mt-4 p-3 rounded-lg text-sm',
            populateMessage.startsWith('Error') ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
          )}>
            {populateMessage}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Session 901: Tab Navigation */}
      <div className="flex items-center justify-between border-b border-dark-border pb-4">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setActiveTab('active')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
              activeTab === 'active'
                ? 'bg-primary-500/20 text-primary-400'
                : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
            )}
          >
            <Zap size={16} />
            Active
            <span className="px-1.5 py-0.5 rounded bg-dark-border text-xs">{stats.active}</span>
          </button>
          <button
            onClick={() => setActiveTab('portfolio')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
              activeTab === 'portfolio'
                ? 'bg-blue-500/20 text-blue-400'
                : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
            )}
          >
            <Layers size={16} />
            Portfolio
          </button>
          <button
            onClick={() => setActiveTab('archive')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
              activeTab === 'archive'
                ? 'bg-emerald-500/20 text-emerald-400'
                : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
            )}
          >
            <Archive size={16} />
            Archive
            <span className="px-1.5 py-0.5 rounded bg-dark-border text-xs">{stats.completed + stats.archived}</span>
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
              activeTab === 'stats'
                ? 'bg-purple-500/20 text-purple-400'
                : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
            )}
          >
            <BarChart3 size={16} />
            Stats
          </button>
          {/* Session 921: Pipeline Health tab */}
          <button
            onClick={() => setActiveTab('health')}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
              activeTab === 'health'
                ? 'bg-cyan-500/20 text-cyan-400'
                : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
            )}
          >
            <Radio size={16} className={pipelineHealth?.health_status === 'healthy' ? 'animate-pulse' : ''} />
            Health
            {pipelineHealth?.health_status && (
              <span className={cn(
                'w-2 h-2 rounded-full',
                pipelineHealth.health_status === 'healthy' ? 'bg-green-400' :
                pipelineHealth.health_status === 'moderate' ? 'bg-yellow-400' :
                pipelineHealth.health_status === 'slow' ? 'bg-orange-400' :
                pipelineHealth.health_status === 'stalled' ? 'bg-red-400' :
                pipelineHealth.health_status === 'critical' ? 'bg-red-500 animate-pulse' :
                'bg-gray-400'
              )} />
            )}
          </button>
        </div>
        <button
          onClick={() => activeTab === 'health' ? refetchHealth() : refetch()}
          className="btn btn-ghost p-2"
          title="Refresh"
        >
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Active Tab: Execution Layer */}
      {activeTab === 'active' && (
        <>
          {/* Session 904: Filter bar with view toggle */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-500">Filter:</span>
              <button
                onClick={() => setFilter('all')}
                className={cn(
                  'px-3 py-1 rounded-full transition-colors',
                  filter === 'all' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                )}
              >
                All
              </button>
              {healthStats.stale > 0 && (
                <button
                  onClick={() => setFilter('stale')}
                  className={cn(
                    'px-3 py-1 rounded-full transition-colors',
                    filter === 'stale' ? 'bg-yellow-500/20 text-yellow-400' : 'text-gray-400 hover:text-white'
                  )}
                >
                  Stale ({healthStats.stale})
                </button>
              )}
              {healthStats.blocked > 0 && (
                <button
                  onClick={() => setFilter('blocked')}
                  className={cn(
                    'px-3 py-1 rounded-full transition-colors',
                    filter === 'blocked' ? 'bg-red-500/20 text-red-400' : 'text-gray-400 hover:text-white'
                  )}
                >
                  Blocked ({healthStats.blocked})
                </button>
              )}
              {/* Priority quick filters */}
              {stats.by_priority.critical > 0 && (
                <span className="ml-4 px-2 py-1 rounded bg-red-500/10 text-red-400 text-xs flex items-center gap-1">
                  <Flame size={10} />
                  {stats.by_priority.critical} Critical
                </span>
              )}
            </div>

            {/* Session 904: View mode toggle - stages/list/cards */}
            <div className="flex items-center gap-1 bg-dark-bg rounded-lg p-1">
              <button
                onClick={() => setViewMode('stages')}
                className={cn(
                  'p-1.5 rounded transition-colors',
                  viewMode === 'stages' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                )}
                title="Group by stage"
              >
                <Layers size={16} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'p-1.5 rounded transition-colors',
                  viewMode === 'list' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                )}
                title="List view"
              >
                <List size={16} />
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={cn(
                  'p-1.5 rounded transition-colors',
                  viewMode === 'cards' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                )}
                title="Card view"
              >
                <LayoutGrid size={16} />
              </button>
            </div>
          </div>

          {/* Session 904: Conditional rendering based on view mode */}
          {viewMode === 'stages' ? (
            /* Stages view - grouped by pipeline stage */
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((stageNum) => {
                const stageInitiatives = filteredInitiatives.filter(i => i.current_stage === stageNum)
                if (stageInitiatives.length === 0) return null

                return (
                  <div key={stageNum} className="border border-dark-border rounded-lg overflow-hidden">
                    <button
                      onClick={() => setExpandedStages(prev => ({ ...prev, [stageNum]: !prev[stageNum] }))}
                      className={cn(
                        'w-full flex items-center justify-between p-4 transition-colors',
                        stageNum === 1 && 'bg-blue-500/10 hover:bg-blue-500/15',
                        stageNum === 2 && 'bg-purple-500/10 hover:bg-purple-500/15',
                        stageNum === 3 && 'bg-yellow-500/10 hover:bg-yellow-500/15',
                        stageNum === 4 && 'bg-orange-500/10 hover:bg-orange-500/15',
                        stageNum === 5 && 'bg-green-500/10 hover:bg-green-500/15',
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          'w-8 h-8 rounded-full flex items-center justify-center font-bold',
                          stageNum === 1 && 'bg-blue-500/20 text-blue-400',
                          stageNum === 2 && 'bg-purple-500/20 text-purple-400',
                          stageNum === 3 && 'bg-yellow-500/20 text-yellow-400',
                          stageNum === 4 && 'bg-orange-500/20 text-orange-400',
                          stageNum === 5 && 'bg-green-500/20 text-green-400',
                        )}>
                          {stageNum}
                        </div>
                        <div className="text-left">
                          <span className="font-medium">{STAGE_NAMES[stageNum]}</span>
                          <span className="ml-2 px-2 py-0.5 rounded bg-dark-border text-xs text-gray-400">
                            {stageInitiatives.length}
                          </span>
                        </div>
                      </div>
                      {expandedStages[stageNum] ? (
                        <ChevronUp size={18} className="text-gray-400" />
                      ) : (
                        <ChevronDown size={18} className="text-gray-400" />
                      )}
                    </button>
                    {expandedStages[stageNum] && (
                      <div className="border-t border-dark-border bg-dark-card">
                        {stageInitiatives.map((initiative) => (
                          <InitiativeRow
                            key={initiative.id}
                            initiative={initiative}
                            onViewDetails={() => setComprehensiveInitiativeId(initiative.id)}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : viewMode === 'list' ? (
            /* List view - cleaner, more scannable */
            <div className="border border-dark-border rounded-lg overflow-hidden bg-dark-card">
              {/* Header row */}
              <div className="flex items-center gap-4 px-4 py-2 bg-dark-bg text-xs text-gray-500 border-b border-dark-border">
                <span className="w-16">Stage</span>
                <span className="flex-1">Initiative</span>
                <span className="w-20 text-right">Progress</span>
                <span className="w-4"></span>
              </div>
              {filteredInitiatives.map((initiative) => (
                <InitiativeRow
                  key={initiative.id}
                  initiative={initiative}
                  onViewDetails={() => setComprehensiveInitiativeId(initiative.id)}
                />
              ))}
            </div>
          ) : (
            /* Card view - original grid layout */
            <div className="grid gap-4 md:grid-cols-2">
              {filteredInitiatives.map((initiative) => (
                <InitiativeCard
                  key={initiative.id}
                  initiative={initiative}
                  onViewDetails={() => setComprehensiveInitiativeId(initiative.id)}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Portfolio Tab: Strategy Layer - Grouped by Program */}
      {activeTab === 'portfolio' && (
        <div className="space-y-4">
          {Object.entries(groupedByProgram)
            .sort(([, a], [, b]) => b.length - a.length) // Sort by count
            .map(([program, initiatives]) => (
              <div key={program} className="border border-dark-border rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleProgram(program)}
                  className="w-full flex items-center justify-between p-4 bg-dark-bg hover:bg-dark-bg/80 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Layers size={18} className="text-blue-400" />
                    <span className="font-medium capitalize">
                      {program.replace(/_/g, ' ')}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-dark-border text-xs text-gray-400">
                      {initiatives.length} initiatives
                    </span>
                  </div>
                  {expandedPrograms[program] !== false ? (
                    <ChevronUp size={18} />
                  ) : (
                    <ChevronDown size={18} />
                  )}
                </button>
                {expandedPrograms[program] !== false && (
                  <div className="p-4 border-t border-dark-border grid gap-3 md:grid-cols-2">
                    {initiatives.map((initiative) => (
                      <InitiativeCard
                        key={initiative.id}
                        initiative={initiative}
                        // Session 904: Always use comprehensive modal
                        onViewDetails={() => setComprehensiveInitiativeId(initiative.id)}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
        </div>
      )}

      {/* Archive Tab: Memory Layer */}
      {activeTab === 'archive' && (
        <>
          {/* Session 904: View toggle for Archive */}
          <div className="flex justify-end mb-4">
            <div className="flex items-center gap-1 bg-dark-bg rounded-lg p-1">
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'p-1.5 rounded transition-colors',
                  viewMode === 'list' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                )}
                title="List view"
              >
                <List size={16} />
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={cn(
                  'p-1.5 rounded transition-colors',
                  viewMode === 'cards' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                )}
                title="Card view"
              >
                <LayoutGrid size={16} />
              </button>
            </div>
          </div>
          {viewMode === 'list' ? (
            <div className="border border-dark-border rounded-lg overflow-hidden bg-dark-card">
              <div className="flex items-center gap-4 px-4 py-2 bg-dark-bg text-xs text-gray-500 border-b border-dark-border">
                <span className="w-16">Stage</span>
                <span className="flex-1">Initiative</span>
                <span className="w-20 text-right">Progress</span>
                <span className="w-4"></span>
              </div>
              {filteredInitiatives.map((initiative) => (
                <InitiativeRow
                  key={initiative.id}
                  initiative={initiative}
                  onViewDetails={() => setComprehensiveInitiativeId(initiative.id)}
                />
              ))}
              {filteredInitiatives.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  No archived initiatives yet
                </div>
              )}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {filteredInitiatives.map((initiative) => (
                <InitiativeCard
                  key={initiative.id}
                  initiative={initiative}
                  onViewDetails={() => setComprehensiveInitiativeId(initiative.id)}
                />
              ))}
              {filteredInitiatives.length === 0 && (
                <div className="col-span-2 text-center py-8 text-gray-400">
                  No archived initiatives yet
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Total Stats */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-4">Overview</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Total Initiatives</span>
                <span className="text-2xl font-bold text-primary-400">{stats.total}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Active</span>
                <span className="text-lg font-medium text-green-400">{stats.active}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Completed</span>
                <span className="text-lg font-medium text-emerald-400">{stats.completed}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Archived</span>
                <span className="text-lg font-medium text-gray-500">{stats.archived}</span>
              </div>
            </div>
          </div>

          {/* Priority Breakdown */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-4">By Priority</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-red-400">
                  <Flame size={14} /> Critical
                </span>
                <span className="font-medium">{stats.by_priority.critical}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-orange-400">
                  <TrendingUp size={14} /> High
                </span>
                <span className="font-medium">{stats.by_priority.high}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-yellow-400">
                  <Circle size={14} /> Medium
                </span>
                <span className="font-medium">{stats.by_priority.medium}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-gray-400">
                  <Circle size={14} /> Low
                </span>
                <span className="font-medium">{stats.by_priority.low}</span>
              </div>
            </div>
          </div>

          {/* By Program */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-4">By Program</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {Object.entries(stats.by_program)
                .sort(([, a], [, b]) => b - a)
                .map(([program, count]) => (
                  <div key={program} className="flex justify-between items-center">
                    <span className="text-gray-400 capitalize text-sm">
                      {program.replace(/_/g, ' ')}
                    </span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
            </div>
          </div>

          {/* By Purpose */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-4">By Purpose</h3>
            <div className="space-y-2">
              {Object.entries(stats.by_purpose)
                .sort(([, a], [, b]) => b - a)
                .map(([purpose, count]) => (
                  <div key={purpose} className="flex justify-between items-center">
                    <span className="flex items-center gap-2 text-gray-400 capitalize text-sm">
                      <PurposeIcon purpose={purpose} />
                      {purpose.replace(/_/g, ' ')}
                    </span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Session 921: Pipeline Health Tab - Real-time progress monitoring */}
      {activeTab === 'health' && (
        <div className="space-y-6">
          {healthLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary-400" />
            </div>
          ) : pipelineHealth ? (
            <>
              {/* Health Status Banner */}
              <div className={cn(
                'p-4 rounded-lg border flex items-center justify-between',
                pipelineHealth.health_status === 'healthy' ? 'bg-green-500/10 border-green-500/30' :
                pipelineHealth.health_status === 'moderate' ? 'bg-yellow-500/10 border-yellow-500/30' :
                pipelineHealth.health_status === 'slow' ? 'bg-orange-500/10 border-orange-500/30' :
                pipelineHealth.health_status === 'stalled' ? 'bg-red-500/10 border-red-500/30' :
                pipelineHealth.health_status === 'critical' ? 'bg-red-500/20 border-red-500/50' :
                'bg-dark-card border-dark-border'
              )}>
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'w-3 h-3 rounded-full',
                    pipelineHealth.health_status === 'healthy' ? 'bg-green-400 animate-pulse' :
                    pipelineHealth.health_status === 'moderate' ? 'bg-yellow-400' :
                    pipelineHealth.health_status === 'slow' ? 'bg-orange-400' :
                    pipelineHealth.health_status === 'stalled' ? 'bg-red-400' :
                    pipelineHealth.health_status === 'critical' ? 'bg-red-500 animate-pulse' :
                    'bg-gray-400'
                  )} />
                  <div>
                    <div className="font-medium capitalize">{pipelineHealth.health_status}</div>
                    <div className="text-sm text-gray-400">{pipelineHealth.health_message}</div>
                  </div>
                </div>
                <button
                  onClick={() => refetchHealth()}
                  className="btn btn-ghost p-2"
                  title="Refresh"
                >
                  <RefreshCw size={16} />
                </button>
              </div>

              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="text-gray-400 text-sm mb-1">Active Initiatives</div>
                  <div className="text-2xl font-bold text-primary-400">{pipelineHealth.summary?.active_count || 0}</div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="text-gray-400 text-sm mb-1">Moved (24h)</div>
                  <div className="text-2xl font-bold text-green-400">{pipelineHealth.summary?.moved_last_24h || 0}</div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="text-gray-400 text-sm mb-1">Transitions (1h)</div>
                  <div className="text-2xl font-bold text-blue-400">{pipelineHealth.summary?.transitions_last_1h || 0}</div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="text-gray-400 text-sm mb-1">Stale ({pipelineHealth.stale_threshold_hours}h+)</div>
                  <div className={cn(
                    'text-2xl font-bold',
                    (pipelineHealth.summary?.stale_count || 0) > 0 ? 'text-yellow-400' : 'text-gray-500'
                  )}>{pipelineHealth.summary?.stale_count || 0}</div>
                </div>
              </div>

              {/* Hourly Activity Chart */}
              {pipelineHealth.hourly_activity && pipelineHealth.hourly_activity.length > 0 && (
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-400 mb-4">Activity (Last 24 Hours)</h3>
                  <div className="flex items-end gap-1 h-24">
                    {pipelineHealth.hourly_activity.slice(0, 24).reverse().map((hour: { hour: number; transitions: number }, idx: number) => {
                      const maxTransitions = Math.max(...pipelineHealth.hourly_activity.map((h: { transitions: number }) => h.transitions), 1)
                      const height = (hour.transitions / maxTransitions) * 100
                      return (
                        <div
                          key={idx}
                          className="flex-1 bg-primary-500/30 hover:bg-primary-500/50 rounded-t transition-colors cursor-pointer group relative"
                          style={{ height: `${Math.max(height, 4)}%` }}
                          title={`${24 - idx}h ago: ${hour.transitions} transitions`}
                        >
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-dark-bg border border-dark-border rounded px-2 py-1 text-xs whitespace-nowrap z-10">
                            {24 - idx}h ago: {hour.transitions}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>24h ago</span>
                    <span>Now</span>
                  </div>
                </div>
              )}

              {/* Stage Distribution */}
              {pipelineHealth.stage_distribution && (
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-400 mb-4">Stage Distribution</h3>
                  <div className="grid gap-3 md:grid-cols-5">
                    {[1, 2, 3, 4, 5].map((stageNum) => {
                      const stageDist = pipelineHealth.stage_distribution[`stage_${stageNum}`] || {}
                      // Session 943: Use explicit count field (initiatives AT this stage)
                      const total = (stageDist as { count?: number }).count ?? 0
                      return (
                        <div key={stageNum} className="bg-dark-bg rounded-lg p-3">
                          <div className="text-xs text-gray-500 mb-2">Stage {stageNum}</div>
                          <div className="text-lg font-bold text-white mb-2">{total}</div>
                          <div className="space-y-1 text-xs">
                            {stageDist.approved && (
                              <div className="flex justify-between">
                                <span className="text-green-400">Approved</span>
                                <span>{stageDist.approved}</span>
                              </div>
                            )}
                            {stageDist.in_review && (
                              <div className="flex justify-between">
                                <span className="text-blue-400">In Review</span>
                                <span>{stageDist.in_review}</span>
                              </div>
                            )}
                            {stageDist.draft && (
                              <div className="flex justify-between">
                                <span className="text-yellow-400">Draft</span>
                                <span>{stageDist.draft}</span>
                              </div>
                            )}
                            {stageDist.pending && (
                              <div className="flex justify-between">
                                <span className="text-gray-400">Pending</span>
                                <span>{stageDist.pending}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Session 928: Blocker Analysis - WHY initiatives are stuck */}
              {blockerAnalysis && !blockerLoading && (
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-400 mb-4 flex items-center gap-2">
                    <AlertTriangle size={14} className="text-orange-400" />
                    Blocker Analysis (DRAFT Stages)
                  </h3>

                  {/* Summary Stats */}
                  <div className="grid gap-3 md:grid-cols-4 mb-4">
                    <div className="bg-dark-bg rounded-lg p-3">
                      <div className="text-xs text-gray-500">Checked</div>
                      <div className="text-xl font-bold text-white">{blockerAnalysis.summary?.total_checked || 0}</div>
                    </div>
                    <div className="bg-dark-bg rounded-lg p-3">
                      <div className="text-xs text-gray-500">Ready to Progress</div>
                      <div className="text-xl font-bold text-green-400">{blockerAnalysis.summary?.ready_to_progress || 0}</div>
                    </div>
                    <div className="bg-dark-bg rounded-lg p-3">
                      <div className="text-xs text-gray-500">Founder Intent Missing</div>
                      <div className="text-xl font-bold text-orange-400">{blockerAnalysis.summary?.founder_intent_missing || 0}</div>
                    </div>
                    <div className="bg-dark-bg rounded-lg p-3">
                      <div className="text-xs text-gray-500">Quality Failed</div>
                      <div className="text-xl font-bold text-red-400">{blockerAnalysis.summary?.quality_failed || 0}</div>
                    </div>
                  </div>

                  {/* Blocking Reasons Breakdown */}
                  {blockerAnalysis.blocking_reasons && Object.keys(blockerAnalysis.blocking_reasons).length > 0 && (
                    <div className="mb-4">
                      <div className="text-xs text-gray-500 mb-2">Top Blocking Reasons</div>
                      <div className="space-y-2">
                        {Object.entries(blockerAnalysis.blocking_reasons as Record<string, number>)
                          .slice(0, 5)
                          .map(([reason, count]) => {
                            const total = blockerAnalysis.summary?.total_checked || 1
                            const pct = Math.round((count / total) * 100)
                            return (
                              <div key={reason} className="flex items-center gap-3">
                                <div className="flex-1 bg-dark-bg rounded-full h-6 overflow-hidden">
                                  <div
                                    className={cn(
                                      'h-full flex items-center px-2 text-xs font-medium',
                                      reason === 'founder_intent_not_set' ? 'bg-orange-500/30 text-orange-400' :
                                      reason === 'no_document' ? 'bg-red-500/30 text-red-400' :
                                      reason === 'quality_check' ? 'bg-yellow-500/30 text-yellow-400' :
                                      'bg-gray-500/30 text-gray-400'
                                    )}
                                    style={{ width: `${Math.max(pct, 10)}%` }}
                                  >
                                    {reason.replace(/_/g, ' ')}
                                  </div>
                                </div>
                                <div className="text-sm text-gray-400 w-16 text-right">
                                  {count} ({pct}%)
                                </div>
                              </div>
                            )
                          })}
                      </div>
                    </div>
                  )}

                  {/* Rate Limit Stats */}
                  {blockerAnalysis.rate_limit_stats && (
                    <div className="bg-dark-bg rounded-lg p-3 text-xs">
                      <div className="text-gray-500 mb-1">Daily Rate Limit</div>
                      <div className="flex items-center gap-2">
                        <span className="text-white">
                          {blockerAnalysis.rate_limit_stats.progressions_today || 0} / {blockerAnalysis.rate_limit_stats.daily_limit || 40}
                        </span>
                        <span className="text-gray-600">progressions today</span>
                        {blockerAnalysis.rate_limit_stats.remaining > 0 && (
                          <span className="text-green-400 ml-auto">{blockerAnalysis.rate_limit_stats.remaining} remaining</span>
                        )}
                        {blockerAnalysis.rate_limit_stats.remaining === 0 && (
                          <span className="text-red-400 ml-auto">Limit reached</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Recent Activity Feed */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-400 mb-4 flex items-center gap-2">
                  <Radio size={14} className="text-green-400 animate-pulse" />
                  Live Activity Feed
                </h3>
                {pipelineHealth.recent_transitions && pipelineHealth.recent_transitions.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {pipelineHealth.recent_transitions.map((transition: {
                      id: string
                      initiative_name: string
                      stage_number: number
                      from_status: string
                      to_status: string
                      time_ago: string
                      triggered_by: string
                      quality_score?: number
                      had_error: boolean
                    }) => (
                      <div
                        key={transition.id}
                        className={cn(
                          'flex items-center gap-3 p-2 rounded-lg transition-colors',
                          transition.had_error ? 'bg-red-500/10' : 'bg-dark-bg hover:bg-dark-border/50'
                        )}
                      >
                        <div className={cn(
                          'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium',
                          transition.to_status === 'APPROVED' ? 'bg-green-500/20 text-green-400' :
                          transition.to_status === 'IN_REVIEW' ? 'bg-blue-500/20 text-blue-400' :
                          transition.to_status === 'DRAFT' ? 'bg-yellow-500/20 text-yellow-400' :
                          transition.to_status === 'REJECTED' ? 'bg-red-500/20 text-red-400' :
                          'bg-gray-500/20 text-gray-400'
                        )}>
                          S{transition.stage_number}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm text-white truncate">{transition.initiative_name}</div>
                          <div className="text-xs text-gray-400">
                            <span className="text-gray-500">{transition.from_status}</span>
                            <span className="mx-1">→</span>
                            <span className={cn(
                              transition.to_status === 'APPROVED' ? 'text-green-400' :
                              transition.to_status === 'IN_REVIEW' ? 'text-blue-400' :
                              transition.to_status === 'DRAFT' ? 'text-yellow-400' :
                              transition.to_status === 'REJECTED' ? 'text-red-400' :
                              'text-gray-400'
                            )}>{transition.to_status}</span>
                            {transition.quality_score && (
                              <span className="ml-2 text-primary-400">Q: {(transition.quality_score * 100).toFixed(0)}%</span>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-gray-500">{transition.time_ago}</div>
                          <div className="text-xs text-gray-600 truncate max-w-[100px]">{transition.triggered_by}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No recent transitions recorded
                  </div>
                )}
              </div>

              {/* Stale Initiatives Warning */}
              {pipelineHealth.stale_initiatives && pipelineHealth.stale_initiatives.length > 0 && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-yellow-400 mb-4 flex items-center gap-2">
                    <AlertTriangle size={14} />
                    Stale Initiatives ({pipelineHealth.stale_initiatives.length})
                  </h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {pipelineHealth.stale_initiatives.slice(0, 20).map((init: {
                      id: string
                      name: string
                      current_stage: number
                      days_stale: number
                      completion_pct: number
                    }) => (
                      <div key={init.id} className="flex items-center justify-between p-2 bg-dark-bg rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-6 h-6 rounded bg-yellow-500/20 text-yellow-400 flex items-center justify-center text-xs">
                            S{init.current_stage}
                          </div>
                          <span className="text-sm text-white truncate max-w-[300px]">{init.name}</span>
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-400">{init.completion_pct}%</span>
                          <span className="text-yellow-400">{init.days_stale}d stale</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 text-gray-400">
              Failed to load pipeline health data
            </div>
          )}
        </div>
      )}

      {filteredInitiatives.length === 0 && activeTab !== 'stats' && activeTab !== 'archive' && activeTab !== 'health' && (
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
