/**
 * Session 974: PA Conversation Sidebar
 *
 * ChatGPT-style conversation list sidebar for the PA chat.
 * Two variants:
 * - "panel": narrow left panel (w-64) for CommandCenterPage
 * - "overlay": full-width overlay replacing messages for GlobalPADock
 */

import { useEffect } from 'react'
import { Plus, MessageSquare, Loader2 } from 'lucide-react'
import { cn } from '@/lib/cn'
import { usePAStore } from '@/stores/paStore'

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

interface PAConversationSidebarProps {
  variant: 'panel' | 'overlay'
}

export default function PAConversationSidebar({ variant }: PAConversationSidebarProps) {
  const {
    conversations,
    activeConversationId,
    conversationsLoading,
    fetchConversations,
    setActiveConversation,
    startNewConversation,
    toggleSidebar,
  } = usePAStore()

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations])

  const handleSelect = (id: string) => {
    setActiveConversation(id)
    if (variant === 'overlay') {
      toggleSidebar()
    }
  }

  const handleNewChat = () => {
    startNewConversation()
    if (variant === 'overlay') {
      toggleSidebar()
    }
  }

  const isPanel = variant === 'panel'

  return (
    <div
      className={cn(
        'flex flex-col bg-dark-bg border-dark-border overflow-hidden',
        isPanel
          ? 'w-56 border-r shrink-0'
          : 'absolute inset-0 z-10 bg-dark-card'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-dark-border shrink-0">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
          Conversations
        </span>
        <button
          onClick={handleNewChat}
          className="p-1.5 rounded-md hover:bg-dark-border text-gray-400 hover:text-white transition-colors"
          title="New Chat"
        >
          <Plus size={14} />
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-auto">
        {conversationsLoading && conversations.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={16} className="animate-spin text-gray-500" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
            <MessageSquare size={20} className="text-gray-600 mb-2" />
            <p className="text-xs text-gray-500">No conversations yet</p>
            <p className="text-xs text-gray-600 mt-1">Start chatting to create one</p>
          </div>
        ) : (
          <div className="py-1">
            {conversations.map((conv) => (
              <button
                key={conv.conversation_id}
                onClick={() => handleSelect(conv.conversation_id)}
                className={cn(
                  'w-full text-left px-3 py-2.5 hover:bg-dark-border/50 transition-colors border-l-2',
                  conv.conversation_id === activeConversationId
                    ? 'bg-primary-600/10 border-primary-500 text-white'
                    : 'border-transparent text-gray-300'
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-xs font-medium truncate flex-1">{conv.title}</p>
                  <span className="text-[10px] text-gray-500 shrink-0">
                    {timeAgo(conv.last_message_at)}
                  </span>
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[10px] text-gray-500">
                    {conv.message_count} msg{conv.message_count !== 1 ? 's' : ''}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Overlay close */}
      {!isPanel && (
        <button
          onClick={toggleSidebar}
          className="p-2 border-t border-dark-border text-xs text-gray-400 hover:text-white hover:bg-dark-border transition-colors text-center"
        >
          Back to chat
        </button>
      )}
    </div>
  )
}
