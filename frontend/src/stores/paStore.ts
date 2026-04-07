/**
 * Session 948: Global PA Store
 * Session 974: Added conversation history (activeConversationId, conversations list, sidebar)
 *
 * Persists PA chat state across page navigations.
 * The PA dock can be open/closed and messages persist.
 * Both CommandCenterPage and GlobalPADock share this store.
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { assistantApi } from '@/lib/api'

interface AsyncJob {
  task_id: string
  agent: string
  status: 'pending' | 'started' | 'success' | 'failed'
  started_at?: string
  finished_at?: string
  duration_ms?: number
  image_url?: string
}

interface Message {
  id: string
  role: 'user' | 'assistant' | 'tool' | 'system'
  content: string
  timestamp: string // ISO string for persistence
  tools_used?: string[]
  async_jobs?: AsyncJob[]
  feedback?: 'positive' | 'negative'
  source?: string
}

interface ConversationSummary {
  conversation_id: string
  title: string
  message_count: number
  last_message_at: string | null
  preview: string
}

interface PAState {
  // User scoping — prevents conversation bleed between users
  userId: number | null

  // Dock visibility
  isDockOpen: boolean
  isDockMinimized: boolean

  // Messages
  messages: Message[]

  // Current input (for persistence)
  currentInput: string

  // Context awareness
  currentPage: string

  // Session 974: Conversation history
  activeConversationId: string | null
  conversations: ConversationSummary[]
  isSidebarOpen: boolean
  conversationsLoading: boolean

  // Actions
  syncUser: (userId: number | null) => void
  toggleDock: () => void
  openDock: () => void
  closeDock: () => void
  minimizeDock: () => void
  maximizeDock: () => void

  addMessage: (message: Omit<Message, 'id' | 'timestamp'> & { id?: string; timestamp?: string }) => void
  updateMessageFeedback: (messageId: string, feedback: 'positive' | 'negative') => void
  clearMessages: () => void

  setCurrentInput: (input: string) => void
  setCurrentPage: (page: string) => void

  // Session 974: Conversation actions
  setActiveConversation: (id: string) => Promise<void>
  startNewConversation: () => Promise<void>
  fetchConversations: () => Promise<void>
  toggleSidebar: () => void
  setActiveConversationId: (id: string | null) => void
}

// Guard against concurrent setActiveConversation calls (two sync queries racing)
let _syncInFlight = false

export const usePAStore = create<PAState>()(
  persist(
    (set, get) => ({
      // Initial state
      userId: null,
      isDockOpen: false,
      isDockMinimized: false,
      messages: [],
      currentInput: '',
      currentPage: '/',
      activeConversationId: null,
      conversations: [],
      isSidebarOpen: false,
      conversationsLoading: false,

      // User scoping: when user changes, wipe conversation state to prevent bleed
      syncUser: (newUserId: number | null) => {
        const current = get().userId
        if (current !== newUserId) {
          set({
            userId: newUserId,
            messages: [],
            activeConversationId: null,
            conversations: [],
            currentInput: '',
            conversationsLoading: false,
          })
        }
      },

      // Dock controls
      toggleDock: () => set((state) => ({ isDockOpen: !state.isDockOpen })),
      openDock: () => set({ isDockOpen: true, isDockMinimized: false }),
      closeDock: () => set({ isDockOpen: false }),
      minimizeDock: () => set({ isDockMinimized: true }),
      maximizeDock: () => set({ isDockMinimized: false }),

      // Message management — merge by ID to prevent duplicates from WebSocket + poll
      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: message.id || Date.now().toString(),
          timestamp: message.timestamp || new Date().toISOString(),
        }
        set((state) => {
          // Dedupe: check if message with this ID already exists
          const exists = state.messages.some((m) => m.id === newMessage.id)
          if (exists) return state

          // Also dedupe by content+role+source for optimistic messages
          const contentMatch = state.messages.some(
            (m) => m.content === newMessage.content && m.role === newMessage.role && m.source === newMessage.source
          )
          if (contentMatch) return state

          const merged = [...state.messages, newMessage]
          merged.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
          return { messages: merged }
        })
      },

      updateMessageFeedback: (messageId, feedback) => {
        const state = get()
        const msg = state.messages.find(m => m.id === messageId)
        const msgIndex = state.messages.filter(m => m.role === 'assistant').indexOf(msg!)

        // Update local state immediately
        set((s) => ({
          messages: s.messages.map((m) =>
            m.id === messageId ? { ...m, feedback } : m
          ),
        }))

        // Session 1085: Persist to backend
        try {
          const token = document.cookie.match(/sessionid=([^;]+)/)?.[1]
          fetch('/api/pa/feedback/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              conversation_id: state.activeConversationId || '',
              message_index: msgIndex >= 0 ? msgIndex : 0,
              rating: feedback === 'positive' ? 1 : -1,
            }),
          }).catch(() => {}) // Non-blocking
        } catch {}
      },

      clearMessages: () => set({ messages: [] }),

      setCurrentInput: (input) => set({ currentInput: input }),
      setCurrentPage: (page) => set({ currentPage: page }),

      // Session 974: Conversation actions
      setActiveConversationId: (id) => set({ activeConversationId: id }),

      setActiveConversation: async (id: string) => {
        if (_syncInFlight) return
        _syncInFlight = true
        try {
          const response = await assistantApi.getConversation(id)
          const data = response.data
          if (data.success) {
            set({
              activeConversationId: id,
              messages: data.messages.map((m: { id: string; role: 'user' | 'assistant' | 'tool' | 'system'; content: string; timestamp: string; tools_used?: string[]; source?: string }) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                timestamp: m.timestamp,
                tools_used: m.tools_used || [],
                source: m.source,
              })),
            })
          }
        } catch (err) {
          console.error('Failed to load conversation:', err)
        } finally {
          _syncInFlight = false
        }
      },

      startNewConversation: async () => {
        try {
          const response = await assistantApi.createConversation()
          const data = response.data
          if (data.success) {
            set({
              activeConversationId: data.conversation_id,
              messages: [],
            })
          }
        } catch (err) {
          console.error('Failed to create conversation:', err)
          // Fallback: just clear messages with a local ID
          set({
            activeConversationId: `pa-${Date.now().toString(36)}`,
            messages: [],
          })
        }
      },

      fetchConversations: async () => {
        if (get().conversationsLoading) return
        set({ conversationsLoading: true })
        try {
          const response = await assistantApi.listConversations()
          const data = response.data
          if (data.success) {
            set({ conversations: data.conversations })
          }
        } catch (err) {
          console.error('Failed to fetch conversations:', err)
        } finally {
          set({ conversationsLoading: false })
        }
      },

      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    }),
    {
      name: 'pa-dock-state',
      version: 3,
      migrate: (persisted: unknown, version: number) => {
        const state = persisted as Record<string, unknown>
        if (version < 2) {
          return {
            ...state,
            activeConversationId: null,
            conversations: [],
            isSidebarOpen: false,
            conversationsLoading: false,
            userId: null,
          }
        }
        if (version < 3) {
          // v3: user scoping — wipe conversation state from pre-scoped store
          return {
            ...state,
            userId: null,
            messages: [],
            activeConversationId: null,
            conversations: [],
          }
        }
        return state
      },
      // Only persist some fields
      partialize: (state) => ({
        userId: state.userId,
        isDockOpen: state.isDockOpen,
        isDockMinimized: state.isDockMinimized,
        messages: state.messages.slice(-50), // Keep last 50 messages
        currentInput: state.currentInput,
        activeConversationId: state.activeConversationId,
        isSidebarOpen: state.isSidebarOpen,
      }),
    }
  )
)

// Selector hooks
export const useIsDockOpen = () => usePAStore((s) => s.isDockOpen)
export const usePAMessages = () => usePAStore((s) => s.messages)
