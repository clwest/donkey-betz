/**
 * Session 948: Global PA Store
 *
 * Persists PA chat state across page navigations.
 * The PA dock can be open/closed and messages persist.
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string // ISO string for persistence
  tools_used?: string[]
  feedback?: 'positive' | 'negative'
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
    }),
    {
      name: 'pa-dock-state',
      // Only persist some fields
      partialize: (state) => ({
        isDockOpen: state.isDockOpen,
        isDockMinimized: state.isDockMinimized,
        messages: state.messages.slice(-50), // Keep last 50 messages
        currentInput: state.currentInput,
      }),
    }
  )
)

// Selector hooks
export const useIsDockOpen = () => usePAStore((s) => s.isDockOpen)
export const usePAMessages = () => usePAStore((s) => s.messages)
