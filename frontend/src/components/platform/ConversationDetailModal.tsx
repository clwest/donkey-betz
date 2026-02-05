// Session 834: Conversation Detail Modal
// View full conversation details without leaving Workspace
// Session 926: Added ListenButton for TTS

import { useQuery } from '@tanstack/react-query'
import {
  X,
  MessageSquare,
  Users,
  Clock,
  Target,
  CheckCircle,
  AlertCircle,
  Loader2,
  Hash,
  Sparkles,
  User,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { conversationsApi } from '@/lib/api'
import { ListenButton, ListenAllButton } from '@/components/ListenButton'

interface ConversationDetailModalProps {
  conversationId: string
  onClose: () => void
}

interface Message {
  id: string
  agent: string
  agent_emoji?: string
  content: string
  sequence: number
  type?: string
  relevance?: number
  created_at?: string
}

interface Conversation {
  id: string
  topic: string
  type: string
  status: string
  objective?: string
  success_criteria?: string[]
  initiator: string
  initiator_emoji?: string
  participants: Array<{ name: string; emoji?: string }>
  messages: Message[]
  started_at: string
  ended_at?: string
  conclusion?: string
  insights?: string
}

export function ConversationDetailModal({ conversationId, onClose }: ConversationDetailModalProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['conversation-detail', conversationId],
    queryFn: async () => {
      const response = await conversationsApi.detail(conversationId)
      return response.data as { conversation: Conversation }
    },
  })

  const conversation = data?.conversation

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'concluded':
      case 'completed':
        return 'bg-green-500/20 text-green-400'
      case 'active':
      case 'in_progress':
        return 'bg-blue-500/20 text-blue-400'
      case 'failed':
        return 'bg-red-500/20 text-red-400'
      default:
        return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border bg-gradient-to-r from-blue-500/10 to-purple-500/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/20">
              <MessageSquare size={20} className="text-blue-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Conversation Details</h2>
              <p className="text-xs text-gray-400">Full conversation thread</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-dark-border transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle size={48} className="text-red-400 mb-4" />
              <p className="text-gray-400">Failed to load conversation</p>
            </div>
          ) : conversation ? (
            <>
              {/* Topic & Status */}
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-base font-medium text-white mb-2">{conversation.topic}</h3>
                    <div className="flex items-center gap-3 text-xs">
                      <span className={cn('px-2 py-1 rounded', getStatusColor(conversation.status))}>
                        {conversation.status}
                      </span>
                      <span className="text-gray-400 capitalize">{conversation.type}</span>
                      <span className="text-gray-500 flex items-center gap-1">
                        <Clock size={12} />
                        {conversation.started_at ? new Date(conversation.started_at).toLocaleString() : 'Unknown'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Objective */}
                {conversation.objective && (
                  <div className="mt-4 pt-4 border-t border-dark-border">
                    <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                      <Target size={12} />
                      Objective
                    </div>
                    <p className="text-sm text-gray-300">{conversation.objective}</p>
                  </div>
                )}

                {/* Success Criteria */}
                {conversation.success_criteria && conversation.success_criteria.length > 0 && (
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                      <CheckCircle size={12} />
                      Success Criteria
                    </div>
                    <ul className="space-y-1">
                      {conversation.success_criteria.map((criterion, idx) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                          <span className="text-green-400 mt-1">•</span>
                          {criterion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Participants */}
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
                  <Users size={12} />
                  Participants ({conversation.participants?.length || 0})
                </div>
                <div className="flex flex-wrap gap-2">
                  {conversation.participants?.map((p, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-primary-600/20 text-primary-400 rounded text-xs flex items-center gap-1"
                    >
                      {p.emoji || '🤖'} {p.name}
                    </span>
                  ))}
                </div>
              </div>

              {/* Conversation Thread */}
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Sparkles size={12} />
                    Conversation ({conversation.messages?.length || 0} messages)
                  </div>
                  {conversation.messages && conversation.messages.length > 0 && (
                    <ListenAllButton
                      messages={conversation.messages.map(msg => ({
                        text: msg.content,
                        agentName: msg.agent,
                      }))}
                      className="text-xs"
                    />
                  )}
                </div>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {conversation.messages?.map((msg, idx) => (
                    <div
                      key={msg.id || idx}
                      className="pl-3 border-l-2 border-primary-500/30"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{msg.agent_emoji || '🤖'}</span>
                          <span className="text-sm font-medium text-white">{msg.agent}</span>
                          <span className="text-xs text-gray-500">#{msg.sequence}</span>
                          {msg.type && (
                            <span className="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-400">
                              {msg.type}
                            </span>
                          )}
                        </div>
                        <ListenButton
                          text={msg.content}
                          agentName={msg.agent}
                          size="sm"
                          className="opacity-50 hover:opacity-100"
                        />
                      </div>
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  ))}
                  {(!conversation.messages || conversation.messages.length === 0) && (
                    <p className="text-sm text-gray-500 italic">No messages recorded</p>
                  )}
                </div>
              </div>

              {/* Conclusion */}
              {(conversation.conclusion || conversation.insights) && (
                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-xs text-green-400 mb-2">
                    <CheckCircle size={12} />
                    Conclusion
                  </div>
                  <p className="text-sm text-gray-300">{conversation.conclusion || conversation.insights}</p>
                </div>
              )}

              {/* Metadata */}
              <div className="flex items-center gap-4 text-xs text-gray-500 pt-2">
                <span className="flex items-center gap-1">
                  <Hash size={12} />
                  {conversation.id.slice(0, 8)}
                </span>
                <span className="flex items-center gap-1">
                  <User size={12} />
                  Initiated by: {conversation.initiator_emoji || '🤖'} {conversation.initiator}
                </span>
                {conversation.ended_at && (
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    Ended: {new Date(conversation.ended_at).toLocaleString()}
                  </span>
                )}
              </div>
            </>
          ) : (
            <p className="text-gray-400 text-center py-8">Conversation not found</p>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-dark-border bg-dark-bg/50">
          <button
            onClick={onClose}
            className="w-full py-2 px-4 bg-dark-border hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
