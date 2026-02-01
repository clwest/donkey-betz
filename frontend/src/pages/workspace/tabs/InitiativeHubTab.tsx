// Session 899: Initiative Hub - Unified Command Center
// Everything flows: Trigger → Conversation → Decision → Initiative → Stages → Deliverable
// No more scattered panels - one view to see the complete story

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  FolderKanban,
  RefreshCw,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  ChevronDown,
  FileText,
  ArrowRight,
  MessageSquare,
  Lightbulb,
  Users,
  Zap,
  BookOpen,
  Trophy,
  Eye,
  GitBranch,
  Clock,
  Sparkles,
  Ghost,
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

// Document viewer modal (reused from InitiativesTab)
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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60]" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border shrink-0">
          <div className="flex items-center gap-3">
            <FileText size={20} className="text-primary-400" />
            <div>
              <h3 className="text-lg font-semibold">{stageName} Document</h3>
              {data?.title && <p className="text-sm text-gray-400">{data.title}</p>}
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg">
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
          {data && (
            <div className="prose prose-invert max-w-none">
              <div className="flex items-center gap-4 text-xs text-gray-400 mb-4 pb-4 border-b border-dark-border">
                {data.word_count && <span>{data.word_count} words</span>}
                {data.created_at && <span>Created: {new Date(data.created_at).toLocaleDateString()}</span>}
              </div>
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {data.full_text || data.content || 'No content available'}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end p-4 border-t border-dark-border shrink-0">
          <button onClick={onClose} className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Single Initiative Card - Expandable to show full story
function InitiativeCard({ initiative }: { initiative: any }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [viewingDocument, setViewingDocument] = useState<{ id: string; stageName: string } | null>(null)

  const isCompleted = initiative.status === 'COMPLETED'
  const stagesApproved = initiative.stages.filter((s: any) => s.status === 'APPROVED').length

  return (
    <div className={cn(
      'border rounded-lg overflow-hidden transition-all',
      isCompleted ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-dark-border bg-dark-card'
    )}>
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-dark-bg/50 transition-colors text-left"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {isCompleted ? (
            <Trophy size={20} className="text-emerald-400 flex-shrink-0" />
          ) : (
            <FolderKanban size={20} className="text-primary-400 flex-shrink-0" />
          )}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-medium truncate">{initiative.name}</h3>
              <span className={cn(
                'px-2 py-0.5 rounded text-xs font-medium flex-shrink-0',
                isCompleted && 'bg-emerald-500/20 text-emerald-400',
                initiative.status === 'ACTIVE' && 'bg-blue-500/20 text-blue-400',
              )}>
                {initiative.status}
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
              {initiative.trigger && (
                <span className="flex items-center gap-1">
                  <Zap size={10} />
                  {initiative.trigger.type}
                </span>
              )}
              {initiative.agents.length > 0 && (
                <span className="flex items-center gap-1">
                  <Users size={10} />
                  {initiative.agents.length} agents
                </span>
              )}
              <span className="flex items-center gap-1">
                <GitBranch size={10} />
                {stagesApproved}/5 stages
              </span>
              <span className="flex items-center gap-1">
                <Clock size={10} />
                {new Date(initiative.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Completeness indicator */}
        <div className="flex items-center gap-3 ml-4">
          <div className="w-16 h-2 bg-dark-border rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full transition-all',
                initiative.completeness_score >= 80 ? 'bg-emerald-500' : 'bg-primary-500'
              )}
              style={{ width: `${initiative.completeness_score}%` }}
            />
          </div>
          <span className="text-xs text-gray-400 w-8">{initiative.completeness_score}%</span>
          {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
        </div>
      </button>

      {/* Expanded Content - Full story */}
      {isExpanded && (
        <div className="border-t border-dark-border p-4 space-y-4 bg-dark-bg/30">
          {/* Description */}
          {initiative.description && (
            <p className="text-sm text-gray-300">{initiative.description}</p>
          )}

          {/* Flow Visualization */}
          <div className="flex items-center gap-2 text-xs flex-wrap py-2">
            {initiative.trigger && (
              <>
                <span className="px-2 py-1 bg-yellow-500/10 text-yellow-400 rounded flex items-center gap-1">
                  <Zap size={10} />
                  {initiative.trigger.type}
                </span>
                <ArrowRight size={12} className="text-gray-500" />
              </>
            )}
            {initiative.conversation && (
              <>
                <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded flex items-center gap-1">
                  <MessageSquare size={10} />
                  {initiative.conversation.message_count || initiative.conversation.contribution_count || '?'} messages
                </span>
                <ArrowRight size={12} className="text-gray-500" />
              </>
            )}
            {initiative.decision && (
              <>
                <span className="px-2 py-1 bg-purple-500/10 text-purple-400 rounded">Decision</span>
                <ArrowRight size={12} className="text-gray-500" />
              </>
            )}
            <span className="px-2 py-1 bg-primary-500/10 text-primary-400 rounded">Initiative</span>
            <ArrowRight size={12} className="text-gray-500" />
            <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded">{stagesApproved} Stages</span>
            {initiative.deliverable && (
              <>
                <ArrowRight size={12} className="text-gray-500" />
                <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded flex items-center gap-1">
                  <BookOpen size={10} />
                  Deliverable
                </span>
              </>
            )}
          </div>

          {/* Conversation Section */}
          {initiative.conversation && (
            <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
              <div className="flex items-center gap-2 text-sm font-medium text-blue-400 mb-2">
                <MessageSquare size={14} />
                Source Conversation
              </div>
              <div className="text-sm text-gray-300 mb-2">{initiative.conversation.topic}</div>
              {initiative.conversation.conclusion && (
                <div className="text-xs text-gray-400 bg-blue-500/10 p-2 rounded">
                  <span className="text-blue-400">Conclusion:</span> {initiative.conversation.conclusion}
                </div>
              )}
              {initiative.agents.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {initiative.agents.map((agent: string, idx: number) => (
                    <span key={idx} className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 text-xs">
                      {agent}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Decision Section */}
          {initiative.decision && (
            <div className="p-3 bg-purple-500/5 border border-purple-500/20 rounded-lg">
              <div className="flex items-center gap-2 text-sm font-medium text-purple-400 mb-2">
                <Lightbulb size={14} />
                Decision: {initiative.decision.artifact_type}
              </div>
              <div className="text-sm text-gray-300 mb-2">{initiative.decision.topic}</div>
              {initiative.decision.recommended_stance && (
                <div className="text-xs text-gray-400">
                  <span className="text-purple-400">Recommendation:</span> {initiative.decision.recommended_stance}
                </div>
              )}
              {initiative.decision.key_insights?.length > 0 && (
                <div className="mt-2 space-y-1">
                  {initiative.decision.key_insights.slice(0, 2).map((insight: string, idx: number) => (
                    <div key={idx} className="text-xs text-gray-400 pl-2 border-l-2 border-purple-500/30">
                      {insight.slice(0, 150)}...
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Stages Section */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-400 flex items-center gap-2">
              <GitBranch size={14} />
              Pipeline Stages
            </div>
            <div className="grid gap-2">
              {initiative.stages.map((stage: any) => (
                <div
                  key={stage.stage}
                  className={cn(
                    'flex items-center gap-3 p-2 rounded-lg border',
                    stage.status === 'APPROVED' && 'bg-green-500/5 border-green-500/30',
                    stage.status === 'DRAFT' && 'bg-yellow-500/5 border-yellow-500/30',
                    stage.status === 'PENDING' && 'bg-dark-bg border-dark-border',
                  )}
                >
                  <div className={cn(
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                    stage.status === 'APPROVED' && 'bg-green-500/20 text-green-400',
                    stage.status === 'DRAFT' && 'bg-yellow-500/20 text-yellow-400',
                    stage.status === 'PENDING' && 'bg-dark-border text-gray-500',
                  )}>
                    {stage.status === 'APPROVED' ? <CheckCircle2 size={14} /> : stage.stage}
                  </div>
                  <div className="flex-1">
                    <span className="text-sm">{stage.name}</span>
                    <span className="text-xs text-gray-500 ml-2">
                      {stage.status === 'APPROVED' && stage.approved_at
                        ? `Approved ${new Date(stage.approved_at).toLocaleDateString()}`
                        : stage.status}
                    </span>
                  </div>
                  {stage.document_id && (
                    <button
                      onClick={() => setViewingDocument({ id: stage.document_id, stageName: stage.name })}
                      className="flex items-center gap-1 px-2 py-1 bg-primary-500/10 hover:bg-primary-500/20 rounded text-primary-400 text-xs"
                    >
                      <Eye size={12} />
                      View
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Deliverable Section */}
          {initiative.deliverable && (
            <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
              <div className="flex items-center gap-2 text-sm font-medium text-emerald-400 mb-2">
                <BookOpen size={14} />
                Final Deliverable
              </div>
              <div className="text-sm text-gray-300">{initiative.deliverable.title}</div>
              <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                <span>{initiative.deliverable.deliverable_type}</span>
                <span>{Math.round(initiative.deliverable.content_length / 1000)}k characters</span>
                <span className={cn(
                  'px-1.5 py-0.5 rounded',
                  initiative.deliverable.status === 'published' && 'bg-emerald-500/20 text-emerald-400',
                )}>
                  {initiative.deliverable.status}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Document viewer modal */}
      {viewingDocument && (
        <DocumentViewerModal
          documentId={viewingDocument.id}
          stageName={viewingDocument.stageName}
          onClose={() => setViewingDocument(null)}
        />
      )}
    </div>
  )
}

// Orphaned item card (conversation or dream without initiative)
function OrphanedItemCard({ item, type }: { item: any; type: 'conversation' | 'dream' }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border border-gray-700 bg-gray-800/30 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-800/50 transition-colors text-left"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {type === 'conversation' ? (
            <MessageSquare size={16} className="text-blue-400 flex-shrink-0" />
          ) : (
            <Sparkles size={16} className="text-purple-400 flex-shrink-0" />
          )}
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">
              {type === 'conversation' ? item.topic : item.title}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500 mt-0.5">
              {type === 'conversation' ? (
                <>
                  <span>{item.agents?.join(', ') || 'Unknown agents'}</span>
                  <span>•</span>
                  <span>{item.message_count} messages</span>
                </>
              ) : (
                <>
                  <span>{item.agent}</span>
                  <span>•</span>
                  <span>{item.dream_type || 'Dream'}</span>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">
            {new Date(type === 'conversation' ? item.started_at : item.dreamed_at).toLocaleDateString()}
          </span>
          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </div>
      </button>

      {isExpanded && (
        <div className="border-t border-gray-700 p-3 bg-gray-800/20">
          {type === 'conversation' && item.conclusion && (
            <div className="text-xs text-gray-400">
              <span className="text-blue-400">Conclusion:</span> {item.conclusion}
            </div>
          )}
          {type === 'dream' && item.content_preview && (
            <div className="text-xs text-gray-400">{item.content_preview}</div>
          )}
          <div className="text-xs text-yellow-500 mt-2 flex items-center gap-1">
            <Ghost size={12} />
            Not yet linked to an initiative
          </div>
        </div>
      )}
    </div>
  )
}

export function InitiativeHubTab() {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')
  const [showOrphaned, setShowOrphaned] = useState(true)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['initiative-hub'],
    queryFn: async () => {
      const res = await platformApi.initiativeHub()
      return res.data
    },
    refetchInterval: 60000, // Refresh every minute
  })

  const filteredInitiatives = (data?.initiatives || []).filter((init: any) => {
    if (filter === 'all') return true
    if (filter === 'active') return init.status === 'ACTIVE'
    if (filter === 'completed') return init.status === 'COMPLETED'
    return true
  })

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
        <p className="text-gray-400">Failed to load Initiative Hub</p>
        <button onClick={() => refetch()} className="btn btn-ghost mt-4">Try Again</button>
      </div>
    )
  }

  const stats = data?.stats
  const orphaned = data?.orphaned

  return (
    <div className="space-y-6">
      {/* Stats Bar */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-primary-400">{stats?.total_initiatives || 0}</div>
          <div className="text-xs text-gray-400">Total Initiatives</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">{stats?.active_initiatives || 0}</div>
          <div className="text-xs text-gray-400">Active</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-emerald-400">{stats?.completed_initiatives || 0}</div>
          <div className="text-xs text-gray-400">Completed</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-yellow-400">
            {(stats?.orphaned_conversations || 0) + (stats?.orphaned_dreams || 0)}
          </div>
          <div className="text-xs text-gray-400">Orphaned Items</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-400">{Math.round(stats?.avg_completeness || 0)}%</div>
          <div className="text-xs text-gray-400">Avg Completeness</div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter('all')}
            className={cn(
              'px-3 py-1.5 rounded-lg text-sm transition-colors',
              filter === 'all' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
            )}
          >
            All ({data?.initiatives?.length || 0})
          </button>
          <button
            onClick={() => setFilter('active')}
            className={cn(
              'px-3 py-1.5 rounded-lg text-sm transition-colors',
              filter === 'active' ? 'bg-blue-500/20 text-blue-400' : 'text-gray-400 hover:text-white'
            )}
          >
            Active ({stats?.active_initiatives || 0})
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={cn(
              'px-3 py-1.5 rounded-lg text-sm transition-colors flex items-center gap-1',
              filter === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'text-gray-400 hover:text-white'
            )}
          >
            <Trophy size={14} />
            Completed ({stats?.completed_initiatives || 0})
          </button>
        </div>
        <button onClick={() => refetch()} className="btn btn-ghost p-2" title="Refresh">
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Initiatives List */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-400 flex items-center gap-2">
          <FolderKanban size={16} />
          Initiatives ({filteredInitiatives.length})
        </h3>
        {filteredInitiatives.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No initiatives match the selected filter</div>
        ) : (
          <div className="space-y-2">
            {filteredInitiatives.map((initiative: any) => (
              <InitiativeCard key={initiative.id} initiative={initiative} />
            ))}
          </div>
        )}
      </div>

      {/* Orphaned Section */}
      {showOrphaned && orphaned && ((orphaned.conversations?.length || 0) + (orphaned.dreams?.length || 0) > 0) && (
        <div className="space-y-3">
          <button
            onClick={() => setShowOrphaned(!showOrphaned)}
            className="flex items-center gap-2 text-sm font-medium text-gray-400 hover:text-white"
          >
            <Ghost size={16} />
            Orphaned Items ({(orphaned.conversations?.length || 0) + (orphaned.dreams?.length || 0)})
            <span className="text-xs text-yellow-500">(not yet linked to initiatives)</span>
          </button>

          {/* Orphaned Conversations */}
          {orphaned.conversations?.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs text-gray-500">Conversations ({orphaned.conversations.length})</div>
              {orphaned.conversations.slice(0, 5).map((conv: any) => (
                <OrphanedItemCard key={conv.id} item={conv} type="conversation" />
              ))}
            </div>
          )}

          {/* Orphaned Dreams */}
          {orphaned.dreams?.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs text-gray-500">Dreams ({orphaned.dreams.length})</div>
              {orphaned.dreams.slice(0, 5).map((dream: any) => (
                <OrphanedItemCard key={dream.id} item={dream} type="dream" />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
