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

// Session 1172: Live tool-lifecycle ticker. The chat surface stays silent
// between user submit and final reply otherwise; a multi-tool turn looks
// indistinguishable from a stalled worker. `activeTool` holds the
// currently-running tool (or null); `recentTool` holds the last completed
// tool for a brief fade-out display. `seenSeqs` dedupes on WebSocket
// reconnect using (trace_id, seq) per the 1172-1 event contract.
interface ToolTickerEvent {
  trace_id: string
  seq: number
  tool_call_id: string
  tool_name: string
  started_at: string
  latency_ms?: number
  status?: 'ok' | 'error'
}

// Session 1175 PR-2b-3: Agent-completion banner event. Fired from the
// PA WS consumer when `fire_agent_followup_subscriptions` atomically
// flips an armed subscription to fired (backend persists the Rigby-authored
// ChatConversation row at the same moment — banner is the live signal,
// chat history is the load-bearing record).
//
// Dedupe at the store layer: the backend's atomic queryset update only
// fires ONCE per (execution_id, conversation_id), but if the WS reconnects
// mid-fade or a stale event lands, we don't want to re-flash the banner.
// `seenCompletions` is a bounded ring of execution_ids in arrival order.
interface AgentCompletionEvent {
  execution_id: string
  agent_name: string
  status: string
  completed_at: string
  error_signature?: string | null
  artifact_pointers?: Record<string, string[]>
  timestamp?: string
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

  // Session 1172: Tool ticker
  activeTool: ToolTickerEvent | null
  recentTool: ToolTickerEvent | null
  seenSeqs: Record<string, number[]>

  // Session 1175 PR-2b-3: Agent-completion banner
  // Session 1181 PR4: queue replaces single slot so multi-agent fanout doesn't
  // overwrite earlier completions before the user notices. recentAgentCompletion
  // retained as a derived alias for the queue head (back-compat with any caller
  // that reads it directly; the canonical source is agentCompletionQueue).
  recentAgentCompletion: AgentCompletionEvent | null
  agentCompletionQueue: AgentCompletionEvent[]
  seenCompletions: string[]  // bounded ring of execution_ids for dedupe

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

  // Session 1172: Tool ticker actions
  handleToolStarted: (event: ToolTickerEvent) => void
  handleToolCompleted: (event: ToolTickerEvent) => void
  clearToolTicker: () => void

  // Session 1175 PR-2b-3: Agent-completion banner actions
  // Session 1181 PR4: dismissAgentCompletion pops a single item by execution_id;
  // clearAgentCompletion still clears the whole queue (back-compat).
  handleAgentCompleted: (event: AgentCompletionEvent) => void
  dismissAgentCompletion: (execution_id: string) => void
  clearAgentCompletion: () => void
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

      // Session 1172: Tool ticker initial state
      activeTool: null,
      recentTool: null,
      seenSeqs: {},

      // Session 1175 PR-2b-3: Agent-completion banner initial state
      // Session 1181 PR4: queue replaces single slot; recentAgentCompletion
      // is a derived alias for queue[0] kept in sync for back-compat.
      recentAgentCompletion: null,
      agentCompletionQueue: [],
      seenCompletions: [],

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

      // Session 1172: Tool ticker actions. Dedupe by (trace_id, seq) so
      // out-of-order or duplicate WebSocket deliveries don't flicker the
      // ticker. Keep seenSeqs bounded per trace_id (last 32 seqs).
      handleToolStarted: (event) => set((state) => {
        const seen = state.seenSeqs[event.trace_id] || []
        if (seen.includes(event.seq)) return state
        const nextSeen = [...seen, event.seq].slice(-32)
        return {
          activeTool: event,
          recentTool: null,
          seenSeqs: { ...state.seenSeqs, [event.trace_id]: nextSeen },
        }
      }),

      handleToolCompleted: (event) => set((state) => {
        const seen = state.seenSeqs[event.trace_id] || []
        if (seen.includes(event.seq)) return state
        const nextSeen = [...seen, event.seq].slice(-32)
        // Clear `activeTool` only if it matches this completion's
        // tool_call_id — otherwise the user may have started another tool
        // already and we'd erase the live spinner mid-flight.
        const stillActive = state.activeTool && state.activeTool.tool_call_id !== event.tool_call_id
          ? state.activeTool
          : null
        return {
          activeTool: stillActive,
          recentTool: event,
          seenSeqs: { ...state.seenSeqs, [event.trace_id]: nextSeen },
        }
      }),

      clearToolTicker: () => set({ activeTool: null, recentTool: null }),

      // Session 1175 PR-2b-3: Agent-completion banner actions
      // Session 1181 PR4: append to queue (newest first) instead of overwriting
      // single slot. Multi-agent fanout previously dropped earlier completions
      // before the user noticed (Cell 7 finding). Queue is capped at 10 items
      // — burst of more than 10 concurrent completions drops oldest, which is
      // acceptable since the bubble chat-history row remains the load-bearing
      // record (server-side persisted via PR #2352).
      handleAgentCompleted: (event) => set((state) => {
        if (state.seenCompletions.includes(event.execution_id)) return state
        const nextQueue = [event, ...state.agentCompletionQueue].slice(0, 10)
        return {
          agentCompletionQueue: nextQueue,
          recentAgentCompletion: nextQueue[0] ?? null,
          seenCompletions: [...state.seenCompletions, event.execution_id].slice(-50),
        }
      }),

      // Pop a specific completion (e.g., user clicked dismiss on one toast, or
      // its auto-fade timer elapsed). Other queued completions keep their own
      // independent fade timers.
      dismissAgentCompletion: (execution_id) => set((state) => {
        const nextQueue = state.agentCompletionQueue.filter(
          (c) => c.execution_id !== execution_id,
        )
        return {
          agentCompletionQueue: nextQueue,
          recentAgentCompletion: nextQueue[0] ?? null,
        }
      }),

      clearAgentCompletion: () => set({
        agentCompletionQueue: [],
        recentAgentCompletion: null,
      }),
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

// Session 1172: Tool ticker selectors
export const usePAActiveTool = () => usePAStore((s) => s.activeTool)
export const usePARecentTool = () => usePAStore((s) => s.recentTool)

// Session 1175 PR-2b-3: Agent-completion banner selector
export const usePARecentAgentCompletion = () => usePAStore((s) => s.recentAgentCompletion)
// Session 1181 PR4: queue selector for multi-agent fanout — banner renders the
// whole stack (each item gets its own fade timer + dismiss). recentAgentCompletion
// remains as a derived alias for queue[0] for any other reader.
export const usePAAgentCompletionQueue = () => usePAStore((s) => s.agentCompletionQueue)
