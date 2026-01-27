/**
 * Session 834: Conversations Panel for Command Tab
 *
 * Shows recent agent conversations with ability to start new goal-driven conversations.
 * Replaces the need for the separate Conversations page.
 */

import { useState } from 'react'
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
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { conversationsApi } from '@/lib/api'

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
}

export function ConversationsPanel() {
  const queryClient = useQueryClient()
  const [showNewConversation, setShowNewConversation] = useState(false)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery({
    queryKey: ['conversations-panel'],
    queryFn: async () => {
      const res = await conversationsApi.list({ limit: 10, timeRange: '7d' })
      return res.data
    },
    staleTime: 60000,
  })

  const conversations: Conversation[] = data?.results || data?.conversations || []

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
          {data && (
            <span className="text-xs text-gray-500">
              ({conversations.length} recent)
            </span>
          )}
        </div>
        <button
          onClick={() => setShowNewConversation(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          New Conversation
        </button>
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
          <p className="text-gray-400">No recent conversations</p>
          <p className="text-xs text-gray-500 mt-1">Start a new conversation to see it here</p>
        </div>
      ) : (
        <div className="space-y-2">
          {conversations.map((conv) => (
            <ConversationCard
              key={conv.id}
              conversation={conv}
              isExpanded={expandedId === conv.id}
              onToggle={() => setExpandedId(expandedId === conv.id ? null : conv.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

interface ConversationCardProps {
  conversation: Conversation
  isExpanded: boolean
  onToggle: () => void
}

function ConversationCard({ conversation, isExpanded, onToggle }: ConversationCardProps) {
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
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-white truncate">{conversation.topic}</span>
            {getStatusBadge()}
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Users size={12} />
              {participants}
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare size={12} />
              {conversation.message_count} messages
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {new Date(conversation.started_at).toLocaleDateString()}
            </span>
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

          {conversation.quality_score !== undefined && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">Quality Score:</span>
              <span className={cn(
                'text-sm font-medium',
                conversation.quality_score >= 80 ? 'text-accent-green' :
                conversation.quality_score >= 60 ? 'text-accent-amber' : 'text-accent-red'
              )}>
                {conversation.quality_score}%
              </span>
            </div>
          )}

          <a
            href={`/conversation-contract?id=${conversation.id}`}
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
          >
            View Full Conversation <ChevronRight size={12} />
          </a>
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

  const createMutation = useMutation({
    mutationFn: () => conversationsApi.create({
      topic,
      conversation_type: conversationType,
      objective: objective || undefined,
      auto_select_agents: true,
    }),
    onSuccess: () => {
      onSuccess()
    },
  })

  return (
    <div
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-lg w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <Sparkles className="text-primary-400" size={20} />
            <h2 className="text-lg font-semibold">New Agent Conversation</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <div className="p-4 space-y-4">
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
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 p-4 border-t border-gray-700">
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
