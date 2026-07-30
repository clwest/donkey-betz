import { useState, useRef, useEffect, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Send, Bot, User as UserIcon, Loader2 } from 'lucide-react'
import { assistantApi } from '@/lib/api'
import { ChatMarkdown } from '@/components/ChatMarkdown'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

function makeId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export default function MyPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isPolling, setIsPolling] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Cleanup polling on unmount so navigating away kills the interval.
  useEffect(() => {
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [])

  const appendMessage = useCallback((role: 'user' | 'assistant', content: string) => {
    setMessages((prev) => [
      ...prev,
      { id: makeId(), role, content, timestamp: new Date() },
    ])
  }, [])

  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      assistantApi.paChat(message, {
        conversation_id: conversationId || undefined,
        source: 'web-my',
      }),
    onSuccess: (response) => {
      const taskId = response.data.task_id
      setIsPolling(true)

      // Guard against overlapping async callbacks (mirrors GlobalPADock pattern).
      let resolved = false

      pollRef.current = setInterval(async () => {
        if (resolved) return
        try {
          const status = await assistantApi.paChatStatus(taskId)
          if (resolved) return
          if (status.data.status === 'completed') {
            resolved = true
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)

            const content = status.data.content || 'No response'
            appendMessage('assistant', content)

            if (status.data.conversation_id && !conversationId) {
              setConversationId(status.data.conversation_id)
            }
          } else if (status.data.status === 'failed') {
            resolved = true
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            appendMessage(
              'assistant',
              status.data.error || 'Sorry, there was an error. Please try again.'
            )
          }
        } catch {
          resolved = true
          if (pollRef.current) clearInterval(pollRef.current)
          pollRef.current = null
          setIsPolling(false)
          appendMessage('assistant', 'Sorry, there was an error. Please try again.')
        }
      }, 2000)
    },
    onError: () => {
      appendMessage('assistant', 'Sorry, there was an error. Please try again.')
    },
  })

  const isBusy = chatMutation.isPending || isPolling

  const sendMessage = useCallback(() => {
    const text = input.trim()
    if (!text || isBusy) return
    appendMessage('user', text)
    chatMutation.mutate(text)
    setInput('')
  }, [input, isBusy, appendMessage, chatMutation])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col px-4 py-6">
      <div className="flex-1 space-y-4 overflow-y-auto pb-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-center text-gray-500 dark:text-gray-400">
            <div>
              <Bot size={40} className="mx-auto mb-3 text-gray-400" />
              <p className="text-lg font-medium">How can I help you today?</p>
              <p className="mt-1 text-sm">Ask a question or request a summary.</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300">
                <Bot size={18} />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-900 dark:bg-gray-800 dark:text-gray-100'
              }`}
            >
              {msg.role === 'assistant' ? (
                <ChatMarkdown content={msg.content} />
              ) : (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                <UserIcon size={18} />
              </div>
            )}
          </div>
        ))}

        {isBusy && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300">
              <Bot size={18} />
            </div>
            <div className="rounded-2xl bg-white px-4 py-2 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
              <Loader2 size={16} className="animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-200 pt-4 dark:border-gray-800">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Send a message..."
            rows={1}
            disabled={isBusy}
            className="flex-1 resize-none rounded-xl border border-gray-300 bg-white px-4 py-2 text-gray-900 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isBusy}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-600 text-white shadow-sm hover:bg-primary-500 disabled:cursor-not-allowed disabled:opacity-50"
            title="Send"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
