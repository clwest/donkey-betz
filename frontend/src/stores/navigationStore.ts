/**
 * Session 713: Navigation Store - Cross-Page Navigation Context
 *
 * Tracks navigation context so pages know where the user came from
 * and can provide contextual breadcrumbs and "back" navigation.
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface NavigationContext {
  fromPage: string
  entityType?: string
  entityId?: string
  entityLabel?: string
  timestamp: string
  [key: string]: unknown
}

interface NavigationState {
  // Current context (where we came from)
  context: NavigationContext | null

  // Navigation history (last 10 navigations)
  history: NavigationContext[]

  // Recently viewed entities (for quick access)
  recentEntities: {
    type: string
    id: string
    label: string
    page: string
    timestamp: string
  }[]

  // Actions
  setContext: (ctx: NavigationContext) => void
  clearContext: () => void
  addToHistory: (ctx: NavigationContext) => void
  addRecentEntity: (entity: { type: string; id: string; label: string; page: string }) => void
  clearHistory: () => void
}

export const useNavigationStore = create<NavigationState>()(
  persist(
    (set, get) => ({
      context: null,
      history: [],
      recentEntities: [],

      setContext: (ctx) => {
        const current = get().context

        // Add previous context to history if it exists
        if (current) {
          get().addToHistory(current)
        }

        set({ context: ctx })

        // Also track as recent entity if it has entity info
        if (ctx.entityType && ctx.entityId && ctx.entityLabel) {
          get().addRecentEntity({
            type: ctx.entityType,
            id: ctx.entityId,
            label: ctx.entityLabel,
            page: ctx.fromPage,
          })
        }
      },

      clearContext: () => set({ context: null }),

      addToHistory: (ctx) => {
        set((state) => ({
          history: [ctx, ...state.history.slice(0, 9)], // Keep last 10
        }))
      },

      addRecentEntity: (entity) => {
        set((state) => {
          // Remove duplicates
          const filtered = state.recentEntities.filter(
            (e) => !(e.type === entity.type && e.id === entity.id)
          )

          return {
            recentEntities: [
              { ...entity, timestamp: new Date().toISOString() },
              ...filtered.slice(0, 19), // Keep last 20
            ],
          }
        })
      },

      clearHistory: () => set({ history: [], recentEntities: [] }),
    }),
    {
      name: 'navigation-store',
      partialize: (state) => ({
        // Only persist recent entities (not context/history which are session-specific)
        recentEntities: state.recentEntities,
      }),
    }
  )
)

// Selector hooks
export const useNavigationContext = () => useNavigationStore((state) => state.context)
export const useNavigationHistory = () => useNavigationStore((state) => state.history)
export const useRecentEntities = () => useNavigationStore((state) => state.recentEntities)

/**
 * Get page label from path
 */
export function getPageLabel(path: string): string {
  const pageLabels: Record<string, string> = {
    '/': 'Dashboard',
    '/assistant': 'Assistant',
    '/human': 'Human',
    '/agents': 'Agents',
    '/intelligence': 'Intelligence',
    '/body-health': 'Body Health',
    '/workspace': 'Workspace',
    '/llm-routing': 'LLM Routing',
  }

  return pageLabels[path] || path.replace('/', '').replace(/-/g, ' ') || 'Unknown'
}

/**
 * Build breadcrumb from navigation context
 */
export function buildBreadcrumb(context: NavigationContext | null): {
  label: string
  path: string
} | null {
  if (!context?.fromPage) return null

  return {
    label: getPageLabel(context.fromPage),
    path: context.fromPage,
  }
}
