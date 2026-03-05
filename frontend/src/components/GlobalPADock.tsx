/**
 * Session 948: Global PA Dock
 * Session 974: Switched to paChat API with conversation_id, added history overlay
 *
 * A persistent, dockable chat panel that appears on every page.
 * - Slides in from the right side
 * - Can be minimized to a floating button
 * - Preserves chat history across page navigations
 * - Aware of current page context
 * - Shares state with CommandCenterPage via paStore
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Bot, User, Send, X, Minus, Maximize2, MessageSquare,
  Loader2, Copy, ThumbsUp, ThumbsDown, Trash2, Clock, Plus, Terminal,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { assistantApi } from '@/lib/api'
import { usePAStore } from '@/stores/paStore'
import { ChatMarkdown } from './ChatMarkdown'
import PAConversationSidebar from './PAConversationSidebar'

export default function GlobalPADock() {
  const location = useLocation()
  const inputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // PA Store
  const {
    isDockOpen,
    isDockMinimized,
    messages,
    currentInput,
    activeConversationId,
    isSidebarOpen,
    toggleDock,
    closeDock,
    minimizeDock,
    maximizeDock,
    addMessage,
    updateMessageFeedback,
    clearMessages,
    setCurrentInput,
    setCurrentPage,
    setActiveConversationId,
    toggleSidebar,
    startNewConversation,
    fetchConversations,
    setActiveConversation,
  } = usePAStore()

  const [localInput, setLocalInput] = useState(currentInput)
  const [isPolling, setIsPolling] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // Update current page context
  useEffect(() => {
    setCurrentPage(location.pathname)
  }, [location.pathname, setCurrentPage])

  // Sync local input with store
  useEffect(() => {
    setCurrentInput(localInput)
  }, [localInput, setCurrentInput])

  // Auto-scroll to bottom
  useEffect(() => {
    if (isDockOpen && !isDockMinimized && !isSidebarOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isDockOpen, isDockMinimized, isSidebarOpen])

  // Focus input when dock opens
  useEffect(() => {
    if (isDockOpen && !isDockMinimized && !isSidebarOpen) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isDockOpen, isDockMinimized, isSidebarOpen])

  // Live sync: poll server for new messages from Claude Code or other clients
  useQuery({
    queryKey: ['pa-dock-sync', activeConversationId],
    queryFn: async () => {
      if (!activeConversationId) return null
      const response = await assistantApi.getConversation(activeConversationId)
      const data = response.data
      const currentCount = usePAStore.getState().messages.length
      if (data.success && data.messages.length > currentCount) {
        setActiveConversation(activeConversationId)
      }
      return data
    },
    enabled: !!activeConversationId && isDockOpen && !isPolling && !location.pathname.startsWith('/command-center'),
    refetchInterval: 5000,
    refetchIntervalInBackground: false,
  })

  // Session 974b: Chat mutation — dispatches Celery task, then polls for result
  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      assistantApi.paChat(message, {
        context: { current_page: location.pathname },
        conversation_id: activeConversationId || undefined,
        source: 'web-dock',
      }),
    onSuccess: (response) => {
      const taskId = response.data.task_id
      setIsPolling(true)

      pollRef.current = setInterval(async () => {
        try {
          const status = await assistantApi.paChatStatus(taskId)
          if (status.data.status === 'completed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)

            const content = status.data.content || 'No response'
            const toolNames = (status.data.tool_runs || []).map((r) => r.tool)
            const sourceLabel = status.data.source
            addMessage({ role: 'assistant', content, tools_used: toolNames, source: sourceLabel })

            if (status.data.conversation_id && !activeConversationId) {
              setActiveConversationId(status.data.conversation_id)
            }
            fetchConversations()
          } else if (status.data.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            addMessage({
              role: 'assistant',
              content: status.data.error || 'Sorry, there was an error. Please try again.',
            })
          }
        } catch {
          if (pollRef.current) clearInterval(pollRef.current)
          pollRef.current = null
          setIsPolling(false)
          addMessage({
            role: 'assistant',
            content: 'Sorry, there was an error. Please try again.',
          })
        }
      }, 2000)
    },
    onError: () => {
      addMessage({
        role: 'assistant',
        content: 'Sorry, there was an error. Please try again.',
      })
    },
  })

  const isBusy = chatMutation.isPending || isPolling

  const sendMessage = useCallback(() => {
    if (!localInput.trim() || isBusy) return

    addMessage({
      role: 'user',
      content: localInput,
    })
    chatMutation.mutate(localInput)
    setLocalInput('')
  }, [localInput, isBusy, chatMutation, addMessage])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  // Minimized floating button
  if (!isDockOpen) {
    return (
      <button
        onClick={toggleDock}
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-primary-600 shadow-lg hover:bg-primary-500 transition-all hover:scale-105 flex items-center justify-center group"
        title="Open AI Assistant"
      >
        <MessageSquare size={24} className="text-white" />
        {messages.length > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-accent-amber text-[10px] font-medium flex items-center justify-center text-white">
            {messages.length > 9 ? '9+' : messages.length}
          </span>
        )}
      </button>
    )
  }

  // Minimized dock (just header bar)
  if (isDockMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-50 w-72 bg-dark-card border border-dark-border rounded-lg shadow-xl">
        <div className="flex items-center justify-between p-3">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary-600/20 flex items-center justify-center">
              <Bot size={16} className="text-primary-400" />
            </div>
            <span className="text-sm font-medium">AI Assistant</span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={maximizeDock}
              className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
              title="Maximize"
            >
              <Maximize2 size={14} />
            </button>
            <button
              onClick={closeDock}
              className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
              title="Close"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Full dock
  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 h-[500px] bg-dark-card border border-dark-border rounded-xl shadow-2xl flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-dark-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-primary-600/20 flex items-center justify-center">
            <Bot size={16} className="text-primary-400" />
          </div>
          <div>
            <span className="text-sm font-medium">AI Assistant</span>
            <p className="text-[10px] text-gray-500">{location.pathname}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {/* Session 974: History toggle */}
          <button
            onClick={toggleSidebar}
            className={cn(
              'p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white',
              isSidebarOpen && 'bg-primary-600/20 text-primary-400'
            )}
            title="Conversation history"
          >
            <Clock size={14} />
          </button>
          {/* New chat */}
          <button
            onClick={() => startNewConversation()}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
            title="New chat"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={clearMessages}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-accent-red"
            title="Clear chat"
            disabled={messages.length === 0}
          >
            <Trash2 size={14} />
          </button>
          <button
            onClick={minimizeDock}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
            title="Minimize"
          >
            <Minus size={14} />
          </button>
          <button
            onClick={closeDock}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
            title="Close"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Messages or Sidebar Overlay */}
      <div className="flex-1 overflow-auto p-3 space-y-3 relative">
        {/* Session 974: Conversation history overlay */}
        {isSidebarOpen && (
          <PAConversationSidebar variant="overlay" />
        )}

        {!isSidebarOpen && (
          <>
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Bot size={32} className="mb-2 opacity-50" />
                <p className="text-sm mb-1">How can I help?</p>
                <p className="text-xs text-gray-500">I'm available on any page</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-2',
                    message.source === 'claude-code' ? 'justify-start' : message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && message.source !== 'claude-code' && (
                    <div className="h-6 w-6 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                      <Bot size={12} className="text-primary-400" />
                    </div>
                  )}
                  {message.source === 'claude-code' && (
                    <div className="h-6 w-6 rounded-full bg-emerald-600/20 flex items-center justify-center flex-shrink-0">
                      <Terminal size={12} className="text-emerald-400" />
                    </div>
                  )}

                  <div className={cn('max-w-[80%] group', message.role === 'user' && message.source !== 'claude-code' && 'order-first')}>
                    <div
                      className={cn(
                        'rounded-lg px-3 py-2 text-sm',
                        message.source === 'claude-code'
                          ? 'bg-emerald-900/30 border border-emerald-500/20'
                          : message.role === 'user'
                            ? 'bg-primary-600 text-white'
                            : 'bg-dark-bg border border-dark-border'
                      )}
                    >
                      {message.role === 'assistant' ? (
                        <ChatMarkdown content={message.content} />
                      ) : (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      )}
                      {message.tools_used && message.tools_used.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-dark-border/50">
                          {message.tools_used.map((tool) => (
                            <span
                              key={tool}
                              className="text-[10px] px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400"
                            >
                              {tool}
                            </span>
                          ))}
                        </div>
                      )}
                      {message.source === 'claude-code' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono mt-1 inline-block">
                          Claude Code
                        </span>
                      )}
                    </div>

                    {/* Message actions */}
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => copyMessage(message.content)}
                          className="p-1 rounded hover:bg-dark-border"
                        >
                          <Copy size={10} className="text-gray-400" />
                        </button>
                        <button
                          onClick={() => updateMessageFeedback(message.id, 'positive')}
                          className={cn(
                            'p-1 rounded hover:bg-dark-border',
                            message.feedback === 'positive' && 'bg-accent-green/20'
                          )}
                        >
                          <ThumbsUp
                            size={10}
                            className={message.feedback === 'positive' ? 'text-accent-green' : 'text-gray-400'}
                          />
                        </button>
                        <button
                          onClick={() => updateMessageFeedback(message.id, 'negative')}
                          className={cn(
                            'p-1 rounded hover:bg-dark-border',
                            message.feedback === 'negative' && 'bg-accent-red/20'
                          )}
                        >
                          <ThumbsDown
                            size={10}
                            className={message.feedback === 'negative' ? 'text-accent-red' : 'text-gray-400'}
                          />
                        </button>
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="h-6 w-6 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                      <User size={12} className="text-white" />
                    </div>
                  )}
                </div>
              ))
            )}

            {isBusy && (
              <div className="flex gap-2 justify-start">
                <div className="h-6 w-6 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                  <Bot size={12} className="text-primary-400" />
                </div>
                <div className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-3 w-3 animate-spin text-primary-400" />
                    <span className="text-xs text-gray-400">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      {!isSidebarOpen && (
        <div className="border-t border-dark-border p-3 flex-shrink-0">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={localInput}
              onChange={(e) => setLocalInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything..."
              className="input flex-1 text-sm py-2"
              disabled={isBusy}
            />
            <button
              onClick={sendMessage}
              disabled={isBusy || !localInput.trim()}
              className="btn btn-sm btn-primary px-3"
            >
              {isBusy ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Send size={14} />
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
