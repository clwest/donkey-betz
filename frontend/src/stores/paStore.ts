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
  role: 'user' | 'assistant'
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
  toggleDock: () => void
  openDock: () => void
  closeDock: () => void
  minimizeDock: () => void
  maximizeDock: () => void

  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
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

export const usePAStore = create<PAState>()(
  persist(
    (set, get) => ({
      // Initial state
      isDockOpen: false,
      isDockMinimized: false,
      messages: [],
      currentInput: '',
      currentPage: '/',
      activeConversationId: null,
      conversations: [],
      isSidebarOpen: false,
      conversationsLoading: false,

      // Dock controls
      toggleDock: () => set((state) => ({ isDockOpen: !state.isDockOpen })),
      openDock: () => set({ isDockOpen: true, isDockMinimized: false }),
      closeDock: () => set({ isDockOpen: false }),
      minimizeDock: () => set({ isDockMinimized: true }),
      maximizeDock: () => set({ isDockMinimized: false }),

      // Message management
      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
        }
        set((state) => ({
          messages: [...state.messages, newMessage],
        }))
      },

      updateMessageFeedback: (messageId, feedback) => {
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === messageId ? { ...msg, feedback } : msg
          ),
        }))
      },

      clearMessages: () => set({ messages: [] }),

      setCurrentInput: (input) => set({ currentInput: input }),
      setCurrentPage: (page) => set({ currentPage: page }),

      // Session 974: Conversation actions
      setActiveConversationId: (id) => set({ activeConversationId: id }),

      setActiveConversation: async (id: string) => {
        try {
          const response = await assistantApi.getConversation(id)
          const data = response.data
          if (data.success) {
            set({
              activeConversationId: id,
              messages: data.messages.map((m: { id: string; role: 'user' | 'assistant'; content: string; timestamp: string; tools_used?: string[]; source?: string }) => ({
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
      version: 2,
      migrate: (persisted: unknown, version: number) => {
        const state = persisted as Record<string, unknown>
        if (version < 2) {
          return {
            ...state,
            activeConversationId: null,
            conversations: [],
            isSidebarOpen: false,
            conversationsLoading: false,
          }
        }
        return state
      },
      // Only persist some fields
      partialize: (state) => ({
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
