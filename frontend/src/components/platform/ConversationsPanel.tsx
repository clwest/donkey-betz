/**
 * Session 834: Conversations Panel for Command Tab
 *
 * Shows recent agent conversations with ability to start new goal-driven conversations.
 * Replaces the need for the separate Conversations page.
 *
 * Features:
 * - Time range filter (24h, 7d, 30d)
 * - Status filter (all, completed, in_progress)
 * - Stats overview (total, avg quality, messages)
 * - Start new goal-driven conversations
 * - Expandable conversation details
 */

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  MessageSquare,
  Plus,
  ChevronRight,
  ChevronDown,
  Loader2,
  Users,
  Clock,
  Target,
  CheckCircle,
  X,
  Sparkles,
  BarChart3,
  Filter,
  RefreshCw,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { conversationsApi, type TimeRange } from '@/lib/api'
import { ConversationDetailModal } from './ConversationDetailModal'

interface Conversation {
  id: string
  topic: string
  status: string
  message_count: number
  started_at: string
  completed_at?: string
  participants: Array<{ id: string; name: string }>
  objective?: string
  conclusion?: string
  quality_score?: number
  conversation_type?: string
}

type StatusFilter = 'all' | 'completed' | 'in_progress' | 'failed'

export function ConversationsPanel() {
  const queryClient = useQueryClient()
  const [showNewConversation, setShowNewConversation] = useState(false)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState<TimeRange>('7d')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  // Session 835: View conversation in modal instead of redirecting
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['conversations-panel', timeRange],
    queryFn: async () => {
      const res = await conversationsApi.list({ limit: 50, timeRange })
      return res.data
    },
    staleTime: 60000,
  })

  const allConversations: Conversation[] = data?.results || data?.conversations || []

  // Filter by status
  const conversations = useMemo(() => {
    if (statusFilter === 'all') return allConversations
    return allConversations.filter(c => c.status === statusFilter)
  }, [allConversations, statusFilter])

  // Calculate stats
  const stats = useMemo(() => {
    const completed = allConversations.filter(c => c.status === 'completed')
    const avgQuality = completed.length > 0
      ? Math.round(completed.reduce((sum, c) => sum + (c.quality_score || 0), 0) / completed.length)
      : 0
    const totalMessages = allConversations.reduce((sum, c) => sum + (c.message_count || 0), 0)
    const inProgress = allConversations.filter(c => c.status === 'in_progress').length

    return {
      total: allConversations.length,
      completed: completed.length,
      inProgress,
      avgQuality,
      totalMessages,
    }
  }, [allConversations])

  if (error) {
    return (
      <div className="card border-accent-red/50">
        <span className="text-accent-red">Failed to load conversations</span>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="text-accent-blue" size={18} />
          <h3 className="text-md font-semibold uppercase">Agent Conversations</h3>
          {stats.inProgress > 0 && (
            <span className="text-xs px-1.5 py-0.5 bg-accent-amber/20 text-accent-amber rounded animate-pulse">
              {stats.inProgress} active
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw size={14} className={isFetching ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={() => setShowNewConversation(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={16} />
            New Conversation
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-3">
        <div className="card py-3 text-center">
          <div className="text-xl font-bold text-white">{stats.total}</div>
          <div className="text-xs text-gray-400">Total</div>
        </div>
        <div className="card py-3 text-center">
          <div className="text-xl font-bold text-accent-green">{stats.completed}</div>
          <div className="text-xs text-gray-400">Completed</div>
        </div>
        <div className="card py-3 text-center">
          <div className={cn(
            'text-xl font-bold',
            stats.avgQuality >= 80 ? 'text-accent-green' :
            stats.avgQuality >= 60 ? 'text-accent-amber' : 'text-accent-red'
          )}>
            {stats.avgQuality}%
          </div>
          <div className="text-xs text-gray-400">Avg Quality</div>
        </div>
        <div className="card py-3 text-center">
          <div className="text-xl font-bold text-accent-blue">{stats.totalMessages}</div>
          <div className="text-xs text-gray-400">Messages</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          <Filter size={14} className="text-gray-500" />
          <span className="text-xs text-gray-500">Filters:</span>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as TimeRange)}
          className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs focus:border-primary-500 focus:outline-none"
        >
          <option value="24h">Last 24h</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="all">All time</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
          className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs focus:border-primary-500 focus:outline-none"
        >
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="in_progress">In Progress</option>
          <option value="failed">Failed</option>
        </select>
        <span className="text-xs text-gray-500 ml-auto">
          Showing {conversations.length} of {allConversations.length}
        </span>
      </div>

      {/* New Conversation Modal */}
      {showNewConversation && (
        <NewConversationModal
          onClose={() => setShowNewConversation(false)}
          onSuccess={() => {
            setShowNewConversation(false)
            queryClient.invalidateQueries({ queryKey: ['conversations-panel'] })
          }}
        />
      )}

      {/* Conversations List */}
      {isLoading ? (
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card animate-pulse h-20" />
          ))}
        </div>
      ) : conversations.length === 0 ? (
        <div className="card text-center py-8">
          <MessageSquare className="mx-auto text-gray-600 mb-3" size={32} />
          <p className="text-gray-400">No conversations found</p>
          <p className="text-xs text-gray-500 mt-1">
            {statusFilter !== 'all' ? 'Try changing the filters or ' : ''}
            Start a new conversation to see it here
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
          {conversations.slice(0, 20).map((conv) => (
            <ConversationCard
              key={conv.id}
              conversation={conv}
              isExpanded={expandedId === conv.id}
              onToggle={() => setExpandedId(expandedId === conv.id ? null : conv.id)}
              onViewFull={(id) => setSelectedConversationId(id)}
            />
          ))}
          {conversations.length > 20 && (
            <div className="text-center py-2 text-xs text-gray-500">
              + {conversations.length - 20} more conversations
            </div>
          )}
        </div>
      )}

      {/* Session 835: Conversation Detail Modal */}
      {selectedConversationId && (
        <ConversationDetailModal
          conversationId={selectedConversationId}
          onClose={() => setSelectedConversationId(null)}
        />
      )}
    </div>
  )
}

interface ConversationCardProps {
  conversation: Conversation
  isExpanded: boolean
  onToggle: () => void
  // Session 835: Callback to view full conversation in modal
  onViewFull: (id: string) => void
}

function ConversationCard({ conversation, isExpanded, onToggle, onViewFull }: ConversationCardProps) {
  const participants = conversation.participants?.map(p => p.name).join(' + ') || 'Unknown participants'

  const getStatusBadge = () => {
    switch (conversation.status) {
      case 'completed':
        return <span className="text-xs px-1.5 py-0.5 bg-accent-green/20 text-accent-green rounded">Completed</span>
      case 'in_progress':
        return <span className="text-xs px-1.5 py-0.5 bg-accent-amber/20 text-accent-amber rounded animate-pulse">In Progress</span>
      case 'failed':
        return <span className="text-xs px-1.5 py-0.5 bg-accent-red/20 text-accent-red rounded">Failed</span>
      default:
        return <span className="text-xs px-1.5 py-0.5 bg-gray-600 text-gray-400 rounded">{conversation.status}</span>
    }
  }

  const getTypeBadge = () => {
    if (!conversation.conversation_type || conversation.conversation_type === 'general') return null
    const colors: Record<string, string> = {
      analytical: 'bg-accent-blue/20 text-accent-blue',
      creative: 'bg-accent-purple/20 text-accent-purple',
      debate: 'bg-accent-red/20 text-accent-red',
      planning: 'bg-accent-amber/20 text-accent-amber',
      critique: 'bg-accent-cyan/20 text-accent-cyan',
    }
    return (
      <span className={cn('text-xs px-1.5 py-0.5 rounded capitalize', colors[conversation.conversation_type] || 'bg-gray-600 text-gray-400')}>
        {conversation.conversation_type}
      </span>
    )
  }

  return (
    <div
      className={cn(
        'card cursor-pointer transition-all',
        isExpanded ? 'ring-1 ring-primary-500/50' : 'hover:border-primary-500/50'
      )}
      onClick={onToggle}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-sm font-medium text-white truncate">{conversation.topic}</span>
            {getStatusBadge()}
            {getTypeBadge()}
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Users size={12} />
              {participants}
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare size={12} />
              {conversation.message_count} msgs
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {new Date(conversation.started_at).toLocaleDateString()}
            </span>
            {conversation.quality_score !== undefined && conversation.quality_score > 0 && (
              <span className={cn(
                'flex items-center gap-1',
                conversation.quality_score >= 80 ? 'text-accent-green' :
                conversation.quality_score >= 60 ? 'text-accent-amber' : 'text-accent-red'
              )}>
                <BarChart3 size={12} />
                {conversation.quality_score}%
              </span>
            )}
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown size={16} className="text-primary-400 flex-shrink-0" />
        ) : (
          <ChevronRight size={16} className="text-gray-500 flex-shrink-0" />
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-700/50 space-y-3">
          {conversation.objective && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1 flex items-center gap-1">
                <Target size={12} />
                Objective
              </h4>
              <p className="text-sm text-gray-300">{conversation.objective}</p>
            </div>
          )}

          {conversation.conclusion && (
            <div>
              <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1 flex items-center gap-1">
                <CheckCircle size={12} />
                Conclusion
              </h4>
              <p className="text-sm text-gray-300">{conversation.conclusion}</p>
            </div>
          )}

          {conversation.quality_score !== undefined && conversation.quality_score > 0 && (
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Quality Score:</span>
                <span className={cn(
                  'font-medium',
                  conversation.quality_score >= 80 ? 'text-accent-green' :
                  conversation.quality_score >= 60 ? 'text-accent-amber' : 'text-accent-red'
                )}>
                  {conversation.quality_score}%
                </span>
              </div>
              {conversation.completed_at && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Completed:</span>
                  <span className="text-white">{new Date(conversation.completed_at).toLocaleString()}</span>
                </div>
              )}
            </div>
          )}

          {/* Session 835: Open modal instead of redirecting */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              onViewFull(conversation.id)
            }}
            className="inline-flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
          >
            View Full Thread <ChevronRight size={12} />
          </button>
        </div>
      )}
    </div>
  )
}

interface NewConversationModalProps {
  onClose: () => void
  onSuccess: () => void
}

function NewConversationModal({ onClose, onSuccess }: NewConversationModalProps) {
  const [topic, setTopic] = useState('')
  const [conversationType, setConversationType] = useState<'analytical' | 'creative' | 'debate' | 'planning' | 'critique' | 'general'>('general')
  const [objective, setObjective] = useState('')
  const [successCriteria, setSuccessCriteria] = useState('')

  const createMutation = useMutation({
    mutationFn: () => conversationsApi.create({
      topic,
      conversation_type: conversationType,
      objective: objective || undefined,
      success_criteria: successCriteria ? successCriteria.split('\n').filter(s => s.trim()) : undefined,
      auto_select_agents: true,
    }),
    onSuccess: () => {
      onSuccess()
    },
  })

  const typeDescriptions: Record<string, string> = {
    general: 'Open-ended discussion on any topic',
    analytical: 'Data-driven analysis with evidence and metrics',
    creative: 'Brainstorming and creative ideation',
    debate: 'Structured pro/con discussion',
    planning: 'Strategic planning and roadmapping',
    critique: 'Constructive review and feedback',
  }

  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-lg w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700 flex-shrink-0">
          <div className="flex items-center gap-2">
            <Sparkles className="text-primary-400" size={20} />
            <h2 className="text-lg font-semibold">New Agent Conversation</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <div className="p-4 space-y-4 overflow-y-auto flex-1">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Topic *</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="What should the agents discuss?"
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Conversation Type</label>
            <select
              value={conversationType}
              onChange={(e) => setConversationType(e.target.value as any)}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
            >
              <option value="general">General Discussion</option>
              <option value="analytical">Analytical (Data-driven)</option>
              <option value="creative">Creative (Brainstorming)</option>
              <option value="debate">Debate (Pro/Con)</option>
              <option value="planning">Planning (Strategy)</option>
              <option value="critique">Critique (Review)</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">{typeDescriptions[conversationType]}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Objective (optional)</label>
            <textarea
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="What outcome are you looking for?"
              rows={2}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Success Criteria (optional)</label>
            <textarea
              value={successCriteria}
              onChange={(e) => setSuccessCriteria(e.target.value)}
              placeholder="One criterion per line..."
              rows={3}
              className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">Define what makes this conversation successful</p>
          </div>

          {/* Quick Topic Suggestions */}
          <div>
            <label className="block text-xs text-gray-500 mb-2">Quick Topics:</label>
            <div className="flex flex-wrap gap-2">
              {[
                'Market trends analysis',
                'Product improvement ideas',
                'Content strategy review',
                'Technical architecture',
                'User experience audit',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => setTopic(suggestion)}
                  className="text-xs px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 p-4 border-t border-gray-700 flex-shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => createMutation.mutate()}
            disabled={!topic.trim() || createMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
          >
            {createMutation.isPending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <MessageSquare size={16} />
            )}
            Start Conversation
          </button>
        </div>
      </div>
    </div>
  )
}
