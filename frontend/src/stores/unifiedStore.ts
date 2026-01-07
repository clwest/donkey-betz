/**
 * Session 714: Unified Store - Shared state across all pages
 *
 * This store provides unified access to:
 * - Pending decisions (attention items needing human action)
 * - Active opportunities (top opportunities to act on)
 * - Running pilots (currently executing pilots)
 * - Critical gates (gates needing attention)
 *
 * All pages can subscribe to this store to show consistent
 * badges, counts, and quick-access widgets without duplicate API calls.
 */

import { create } from 'zustand'
import { humanApi, opportunitiesApi, pilotsApi } from '@/lib/api'

// ============================================================================
// Types
// ============================================================================

export interface AttentionStats {
  total: number
  pending: number
  critical: number
  by_urgency: {
    critical: number
    high: number
    medium: number
    low: number
  }
}

export interface Opportunity {
  id: string
  title: string
  category: string
  score: number
  status: string
  source?: string
  created_at: string
  acted_at?: string
}

export interface RunningPilot {
  id: string
  name: string
  status: string
  hours_running: number
  started_at: string
  gate_id?: string
  decision_topic?: string
}

export interface CriticalGate {
  id: string
  decision_topic: string
  status: string
  risk_level: string
  checklist_percentage: number
  created_at: string
}

// ============================================================================
// Store Interface
// ============================================================================

interface UnifiedState {
  // Attention/Decisions
  attentionStats: AttentionStats | null
  pendingDecisionsCount: number

  // Opportunities
  topOpportunities: Opportunity[]
  activeOpportunity: Opportunity | null

  // Pilots
  runningPilots: RunningPilot[]
  runningPilotsCount: number

  // Gates
  criticalGates: CriticalGate[]
  criticalGatesCount: number

  // Loading states
  isLoadingAttention: boolean
  isLoadingOpportunities: boolean
  isLoadingPilots: boolean
  isLoadingGates: boolean

  // Error states
  error: string | null

  // Last fetch timestamps (for cache invalidation)
  lastFetch: {
    attention: Date | null
    opportunities: Date | null
    pilots: Date | null
    gates: Date | null
  }

  // Actions
  fetchAttentionStats: () => Promise<void>
  fetchTopOpportunities: (limit?: number) => Promise<void>
  fetchRunningPilots: () => Promise<void>
  fetchCriticalGates: () => Promise<void>
  fetchAll: () => Promise<void>

  // Setters for optimistic updates
  setActiveOpportunity: (opp: Opportunity | null) => void
  decrementPendingDecisions: () => void
  incrementPendingDecisions: () => void

  // Clear/reset
  clearError: () => void
  reset: () => void
}

// ============================================================================
// Store Implementation
// ============================================================================

export const useUnifiedStore = create<UnifiedState>((set, get) => ({
  // Initial state
  attentionStats: null,
  pendingDecisionsCount: 0,
  topOpportunities: [],
  activeOpportunity: null,
  runningPilots: [],
  runningPilotsCount: 0,
  criticalGates: [],
  criticalGatesCount: 0,
  isLoadingAttention: false,
  isLoadingOpportunities: false,
  isLoadingPilots: false,
  isLoadingGates: false,
  error: null,
  lastFetch: {
    attention: null,
    opportunities: null,
    pilots: null,
    gates: null,
  },

  // Fetch attention stats
  fetchAttentionStats: async () => {
    set({ isLoadingAttention: true })
    try {
      const response = await humanApi.attentionStats()
      const stats = response.data as AttentionStats

      set({
        attentionStats: stats,
        pendingDecisionsCount: stats?.pending || 0,
        isLoadingAttention: false,
        lastFetch: { ...get().lastFetch, attention: new Date() },
      })
    } catch (err) {
      console.error('[UnifiedStore] Failed to fetch attention stats:', err)
      set({
        isLoadingAttention: false,
        error: 'Failed to fetch attention stats',
      })
    }
  },

  // Fetch top opportunities
  fetchTopOpportunities: async (limit = 5) => {
    set({ isLoadingOpportunities: true })
    try {
      const response = await opportunitiesApi.top(limit)
      const opportunities = (response.data?.opportunities || response.data || []) as Opportunity[]

      set({
        topOpportunities: opportunities,
        isLoadingOpportunities: false,
        lastFetch: { ...get().lastFetch, opportunities: new Date() },
      })
    } catch (err) {
      console.error('[UnifiedStore] Failed to fetch opportunities:', err)
      set({
        isLoadingOpportunities: false,
        error: 'Failed to fetch opportunities',
      })
    }
  },

  // Fetch running pilots
  fetchRunningPilots: async () => {
    set({ isLoadingPilots: true })
    try {
      const response = await pilotsApi.dashboard()
      const data = response.data

      // Extract running pilots from dashboard data
      const running = (data?.running_pilots || data?.pilots?.filter?.((p: RunningPilot) => p.status === 'running') || []) as RunningPilot[]

      set({
        runningPilots: running,
        runningPilotsCount: running.length,
        isLoadingPilots: false,
        lastFetch: { ...get().lastFetch, pilots: new Date() },
      })
    } catch (err) {
      console.error('[UnifiedStore] Failed to fetch pilots:', err)
      set({
        isLoadingPilots: false,
        error: 'Failed to fetch pilots',
      })
    }
  },

  // Fetch critical gates
  fetchCriticalGates: async () => {
    set({ isLoadingGates: true })
    try {
      const response = await pilotsApi.gates()
      const gates = (response.data?.gates || response.data || []) as CriticalGate[]

      // Filter to critical/pending gates
      const critical = gates.filter(
        (g) => g.status === 'pending_review' || g.status === 'blocked' || g.risk_level === 'high'
      )

      set({
        criticalGates: critical,
        criticalGatesCount: critical.length,
        isLoadingGates: false,
        lastFetch: { ...get().lastFetch, gates: new Date() },
      })
    } catch (err) {
      console.error('[UnifiedStore] Failed to fetch gates:', err)
      set({
        isLoadingGates: false,
        error: 'Failed to fetch gates',
      })
    }
  },

  // Fetch all data
  fetchAll: async () => {
    const state = get()
    await Promise.all([
      state.fetchAttentionStats(),
      state.fetchTopOpportunities(),
      state.fetchRunningPilots(),
      state.fetchCriticalGates(),
    ])
  },

  // Optimistic update: set active opportunity
  setActiveOpportunity: (opp) => {
    set({ activeOpportunity: opp })
  },

  // Optimistic update: decrement pending decisions
  decrementPendingDecisions: () => {
    set((state) => ({
      pendingDecisionsCount: Math.max(0, state.pendingDecisionsCount - 1),
      attentionStats: state.attentionStats
        ? { ...state.attentionStats, pending: Math.max(0, state.attentionStats.pending - 1) }
        : null,
    }))
  },

  // Optimistic update: increment pending decisions
  incrementPendingDecisions: () => {
    set((state) => ({
      pendingDecisionsCount: state.pendingDecisionsCount + 1,
      attentionStats: state.attentionStats
        ? { ...state.attentionStats, pending: state.attentionStats.pending + 1 }
        : null,
    }))
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Reset store
  reset: () =>
    set({
      attentionStats: null,
      pendingDecisionsCount: 0,
      topOpportunities: [],
      activeOpportunity: null,
      runningPilots: [],
      runningPilotsCount: 0,
      criticalGates: [],
      criticalGatesCount: 0,
      error: null,
      lastFetch: {
        attention: null,
        opportunities: null,
        pilots: null,
        gates: null,
      },
    }),
}))

// ============================================================================
// Selector Hooks - Use these for specific data slices
// ============================================================================

/**
 * Get pending decisions count for badges
 */
export const usePendingDecisionsCount = () =>
  useUnifiedStore((state) => state.pendingDecisionsCount)

/**
 * Get running pilots count for badges
 */
export const useRunningPilotsCount = () =>
  useUnifiedStore((state) => state.runningPilotsCount)

/**
 * Get critical gates count for badges
 */
export const useCriticalGatesCount = () =>
  useUnifiedStore((state) => state.criticalGatesCount)

/**
 * Get top opportunities for sidebar widget
 */
export const useTopOpportunities = () =>
  useUnifiedStore((state) => state.topOpportunities)

/**
 * Get running pilots for sidebar widget
 */
export const useRunningPilots = () =>
  useUnifiedStore((state) => state.runningPilots)

/**
 * Get active opportunity being worked on
 */
export const useActiveOpportunity = () =>
  useUnifiedStore((state) => state.activeOpportunity)

/**
 * Check if any critical items need attention
 */
export const useHasCriticalItems = () =>
  useUnifiedStore(
    (state) =>
      state.pendingDecisionsCount > 0 ||
      state.criticalGatesCount > 0 ||
      (state.attentionStats?.critical || 0) > 0
  )

/**
 * Get combined badge count (decisions + critical gates)
 */
export const useTotalBadgeCount = () =>
  useUnifiedStore(
    (state) => state.pendingDecisionsCount + state.criticalGatesCount
  )

/**
 * Get loading state for any data
 */
export const useIsLoading = () =>
  useUnifiedStore(
    (state) =>
      state.isLoadingAttention ||
      state.isLoadingOpportunities ||
      state.isLoadingPilots ||
      state.isLoadingGates
  )
