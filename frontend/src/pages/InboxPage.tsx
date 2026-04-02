/**
 * InboxPage — In-app messaging between platform users.
 *
 * Thread list + message detail with real-time updates.
 * Users can message each other directly or via Rigby routing.
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { MessageSquare, Send, ArrowLeft, Mail, MailOpen, Users } from 'lucide-react'

interface Participant {
  id: number
  username: string
}

interface ThreadMessage {
  body: string
  sender: { id: number | null; username: string | null }
  sender_type: string
  created_at: string
  metadata?: Record<string, unknown>
}

interface Thread {
  id: string
  subject: string
  thread_type: string
  participants: Participant[]
  unread_count: number
  is_muted: boolean
  last_message: {
    body: string | null
    sender: string | null
    created_at: string | null
  } | null
  updated_at: string
  created_at: string
}

export default function InboxPage() {
  const { user } = useAuthStore()
  const [threads, setThreads] = useState<Thread[]>([])
  const [selectedThread, setSelectedThread] = useState<string | null>(null)
  const [messages, setMessages] = useState<ThreadMessage[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [newRecipient, setNewRecipient] = useState('')
  const [newSubject, setNewSubject] = useState('')
  const [showCompose, setShowCompose] = useState(false)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const fetchThreads = useCallback(async () => {
    try {
      const res = await api.get('/inbox/threads/')
      if (res.data.success) {
        setThreads(res.data.threads)
      }
    } catch (err) {
      console.error('Failed to fetch threads:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchMessages = useCallback(async (threadId: string) => {
    try {
      const res = await api.get(`/inbox/threads/${threadId}/messages/`)
      if (res.data.success) {
        setMessages(res.data.messages)
        // Mark as read
        api.post(`/inbox/threads/${threadId}/read/`).catch(() => {})
      }
    } catch (err) {
      console.error('Failed to fetch messages:', err)
    }
  }, [])

  useEffect(() => {
    fetchThreads()
    // Poll for new threads every 15s
    const interval = setInterval(fetchThreads, 15000)
    return () => clearInterval(interval)
  }, [fetchThreads])

  useEffect(() => {
    if (selectedThread) {
      fetchMessages(selectedThread)
      // Poll messages every 5s when viewing a thread
      const interval = setInterval(() => fetchMessages(selectedThread), 5000)
      return () => clearInterval(interval)
    }
  }, [selectedThread, fetchMessages])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedThread) return
    setSending(true)
    try {
      const res = await api.post(`/inbox/threads/${selectedThread}/messages/`, {
        body: newMessage.trim(),
      })
      if (res.data.success) {
        setNewMessage('')
        fetchMessages(selectedThread)
        fetchThreads()
      }
    } catch (err) {
      console.error('Failed to send message:', err)
    } finally {
      setSending(false)
    }
  }

  const handleCompose = async () => {
    if (!newRecipient.trim() || !newMessage.trim()) return
    setSending(true)
    try {
      const res = await api.post('/inbox/threads/', {
        participant_usernames: [newRecipient.trim()],
        message: newMessage.trim(),
        subject: newSubject.trim(),
        thread_type: 'dm',
      })
      if (res.data.success) {
        setNewMessage('')
        setNewRecipient('')
        setNewSubject('')
        setShowCompose(false)
        setSelectedThread(res.data.thread.id)
        fetchThreads()
      }
    } catch (err) {
      console.error('Failed to create thread:', err)
    } finally {
      setSending(false)
    }
  }

  const selectedThreadData = threads.find((t) => t.id === selectedThread)

  const formatTime = (iso: string) => {
    const d = new Date(iso)
    const now = new Date()
    const diff = now.getTime() - d.getTime()
    if (diff < 60000) return 'just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }

  return (
    <div className="flex h-[calc(100vh-64px)] bg-gray-950">
      {/* Thread List */}
      <div className={`${selectedThread ? 'hidden md:flex' : 'flex'} flex-col w-full md:w-80 lg:w-96 border-r border-gray-800`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <MessageSquare className="text-blue-400" size={20} />
            <h1 className="text-lg font-semibold text-white">Messages</h1>
          </div>
          <button
            onClick={() => { setShowCompose(true); setSelectedThread(null) }}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg transition-colors"
          >
            New
          </button>
        </div>

        {/* Thread list */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading...</div>
          ) : threads.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Mail className="mx-auto mb-2 text-gray-600" size={32} />
              <p>No messages yet</p>
              <p className="text-sm mt-1">Start a conversation or ask Rigby to send a message</p>
            </div>
          ) : (
            threads.map((thread) => (
              <button
                key={thread.id}
                onClick={() => { setSelectedThread(thread.id); setShowCompose(false) }}
                className={`w-full text-left p-4 border-b border-gray-800/50 hover:bg-gray-900/50 transition-colors ${
                  selectedThread === thread.id ? 'bg-gray-900 border-l-2 border-l-blue-500' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-white text-sm">
                    {thread.participants.map((p) => p.username).join(', ') || 'Unknown'}
                  </span>
                  {thread.unread_count > 0 && (
                    <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">
                      {thread.unread_count}
                    </span>
                  )}
                </div>
                {thread.subject && (
                  <div className="text-xs text-gray-400 mb-0.5">{thread.subject}</div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400 truncate max-w-[200px]">
                    {thread.last_message?.body || 'No messages'}
                  </span>
                  <span className="text-xs text-gray-600 ml-2 shrink-0">
                    {thread.last_message?.created_at ? formatTime(thread.last_message.created_at) : ''}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Message Detail / Compose */}
      <div className="flex-1 flex flex-col">
        {showCompose ? (
          /* Compose new message */
          <div className="flex-1 flex flex-col">
            <div className="flex items-center gap-3 p-4 border-b border-gray-800">
              <button onClick={() => setShowCompose(false)} className="text-gray-400 hover:text-white md:hidden">
                <ArrowLeft size={20} />
              </button>
              <h2 className="text-white font-medium">New Message</h2>
            </div>
            <div className="p-4 space-y-3 border-b border-gray-800">
              <div>
                <label className="text-xs text-gray-500 mb-1 block">To</label>
                <input
                  type="text"
                  value={newRecipient}
                  onChange={(e) => setNewRecipient(e.target.value)}
                  placeholder="Username..."
                  className="w-full bg-gray-900 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Subject (optional)</label>
                <input
                  type="text"
                  value={newSubject}
                  onChange={(e) => setNewSubject(e.target.value)}
                  placeholder="Subject..."
                  className="w-full bg-gray-900 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex-1" />
            <div className="p-4 border-t border-gray-800">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleCompose()}
                  placeholder="Type your message..."
                  className="flex-1 bg-gray-900 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={handleCompose}
                  disabled={sending || !newMessage.trim() || !newRecipient.trim()}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        ) : selectedThread && selectedThreadData ? (
          /* Thread detail */
          <div className="flex-1 flex flex-col">
            {/* Thread header */}
            <div className="flex items-center gap-3 p-4 border-b border-gray-800">
              <button
                onClick={() => setSelectedThread(null)}
                className="text-gray-400 hover:text-white md:hidden"
              >
                <ArrowLeft size={20} />
              </button>
              <Users className="text-blue-400" size={18} />
              <div>
                <h2 className="text-white font-medium text-sm">
                  {selectedThreadData.participants.map((p) => p.username).join(', ')}
                </h2>
                {selectedThreadData.subject && (
                  <p className="text-xs text-gray-500">{selectedThreadData.subject}</p>
                )}
              </div>
              {selectedThreadData.thread_type === 'rigby_routed' && (
                <span className="ml-auto text-xs bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded">
                  via Rigby
                </span>
              )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((msg, i) => {
                const isMe = msg.sender?.id === user?.id
                return (
                  <div key={i} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-[75%] rounded-lg px-3 py-2 ${
                        isMe
                          ? 'bg-blue-600 text-white'
                          : msg.sender_type === 'rigby'
                          ? 'bg-purple-900/40 text-purple-100 border border-purple-800/50'
                          : 'bg-gray-800 text-gray-100'
                      }`}
                    >
                      {!isMe && (
                        <div className="text-xs font-medium mb-0.5 opacity-70">
                          {msg.sender?.username || msg.sender_type}
                          {msg.sender_type === 'rigby' && ' (via Rigby)'}
                        </div>
                      )}
                      <p className="text-sm whitespace-pre-wrap">{msg.body}</p>
                      <div className="text-xs opacity-50 mt-1 text-right">
                        {formatTime(msg.created_at)}
                      </div>
                    </div>
                  </div>
                )
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Composer */}
            <div className="p-4 border-t border-gray-800">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 bg-gray-900 text-white border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={sending || !newMessage.trim()}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Empty state */
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MailOpen className="mx-auto mb-3 text-gray-600" size={48} />
              <p className="text-lg">Select a conversation</p>
              <p className="text-sm mt-1">or start a new one</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
