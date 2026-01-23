/**
 * Session 713: Body Store - Shared body health state across all pages
 * Session 715: Added request throttling to prevent 429 errors
 *
 * This store provides unified access to body vitals, alerts, and governance
 * status. All pages should use this store instead of making their own API calls.
 */

import { create } from 'zustand'
import { bodyApi } from '@/lib/api'

// ============================================================================
// Throttling Configuration
// ============================================================================

// Minimum time between fetches (in ms) - prevents rate limiting
const MIN_FETCH_INTERVAL = 5000 // 5 seconds

// Track in-flight requests to prevent duplicates
const inFlightRequests = {
  vitals: false,
  alerts: false,
}

// Track last fetch times
const lastFetchTimes: Record<string, Date | null> = {
  vitals: null,
  alerts: null,
}

// Check if enough time has passed since last fetch
const canFetch = (key: string): boolean => {
  const lastFetch = lastFetchTimes[key]
  if (!lastFetch) return true
  return Date.now() - lastFetch.getTime() > MIN_FETCH_INTERVAL
}

// Body system status types
export type BodyStatus = 'healthy' | 'degraded' | 'critical' | 'unknown'

export interface BodySystemStatus {
  status: string
  score: number
  emoji?: string
  alerts?: string[]
  details?: Record<string, unknown>
}

export interface BodyAlert {
  id: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  system: string
  message: string
  timestamp: string
  dismissed?: boolean
}

export interface BodyVitals {
  timestamp: string
  overall_health: BodyStatus
  health_score: number
  is_healthy: boolean
  systems: Record<string, BodySystemStatus>
  check_duration_ms: number
}

interface BodyState {
  // Core state
  vitals: BodyVitals | null
  alerts: BodyAlert[]
  lastFetch: Date | null
  isLoading: boolean
  error: string | null

  // Derived state
  overallStatus: BodyStatus
  healthScore: number
  blocksOperations: boolean
  criticalSystems: string[]

  // Actions
  fetchVitals: () => Promise<void>
  fetchAlerts: () => Promise<void>
  dismissAlert: (alertId: string) => void
  clearDismissedAlerts: () => void

  // Selectors (for governance)
  getSystemStatus: (system: string) => BodySystemStatus | null
  isSystemHealthy: (system: string) => boolean
  canPerformOperation: (operationType: 'pilot' | 'agent_execution' | 'file_write') => { allowed: boolean; reason?: string }
}

// Healthy status values for each system
const HEALTHY_STATUSES: Record<string, string[]> = {
  heart: ['healthy'],
  lungs: ['healthy', 'normal', 'optimal'],
  circulatory: ['flowing', 'healthy'],
  spine: ['aligned', 'healthy'],
  immune: ['healthy', 'protected'],
  digestive: ['healthy', 'processing', 'digesting'],
  muscular: ['strong', 'fit', 'healthy'],
}

// Check if a system is healthy based on status or score
function checkSystemHealthy(system: string, status?: BodySystemStatus): boolean {
  if (!status) return false
  const healthyStatuses = HEALTHY_STATUSES[system] || ['healthy']
  return healthyStatuses.includes(status.status) || status.score >= 80
}

export const useBodyStore = create<BodyState>((set, get) => ({
  // Initial state
  vitals: null,
  alerts: [],
  lastFetch: null,
  isLoading: false,
  error: null,

  // Derived state (computed from vitals)
  overallStatus: 'unknown',
  healthScore: 0,
  blocksOperations: false,
  criticalSystems: [],

  // Fetch body vitals from API (with throttling)
  fetchVitals: async () => {
    // Skip if request in flight or recently fetched
    if (inFlightRequests.vitals || !canFetch('vitals')) {
      return
    }

    inFlightRequests.vitals = true
    set({ isLoading: true, error: null })

    try {
      const response = await bodyApi.vitals(true)
      const vitals: BodyVitals = response.data

      // Find critical systems
      const criticalSystems: string[] = []
      if (vitals.systems) {
        Object.entries(vitals.systems).forEach(([system, status]) => {
          if (status.status === 'critical' || status.score < 20) {
            criticalSystems.push(system)
          }
        })
      }

      // Determine if operations should be blocked
      const blocksOperations = vitals.overall_health === 'critical' || criticalSystems.length >= 3

      lastFetchTimes.vitals = new Date()
      set({
        vitals,
        lastFetch: new Date(),
        isLoading: false,
        overallStatus: vitals.overall_health,
        healthScore: vitals.health_score,
        blocksOperations,
        criticalSystems,
      })
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch body vitals',
      })
    } finally {
      inFlightRequests.vitals = false
    }
  },

  // Fetch alerts from API (with throttling)
  fetchAlerts: async () => {
    // Skip if request in flight or recently fetched
    if (inFlightRequests.alerts || !canFetch('alerts')) {
      return
    }

    inFlightRequests.alerts = true
    try {
      const response = await bodyApi.alerts('info', 50)
      const alerts: BodyAlert[] = (response.data?.alerts || []).map((a: Record<string, unknown>, idx: number) => ({
        id: String(a.id || idx),
        severity: a.severity || 'info',
        system: a.system || 'unknown',
        message: a.message || '',
        timestamp: a.timestamp || new Date().toISOString(),
        dismissed: false,
      }))

      lastFetchTimes.alerts = new Date()
      set({ alerts })
    } catch (error) {
      console.error('Failed to fetch body alerts:', error)
    } finally {
      inFlightRequests.alerts = false
    }
  },

  // Dismiss an alert
  dismissAlert: (alertId: string) => {
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === alertId ? { ...a, dismissed: true } : a
      ),
    }))
  },

  // Clear all dismissed alerts
  clearDismissedAlerts: () => {
    set((state) => ({
      alerts: state.alerts.filter((a) => !a.dismissed),
    }))
  },

  // Get status for a specific system
  getSystemStatus: (system: string) => {
    const { vitals } = get()
    if (!vitals?.systems) return null
    return vitals.systems[system] || null
  },

  // Check if a system is healthy
  isSystemHealthy: (system: string) => {
    const status = get().getSystemStatus(system)
    return checkSystemHealthy(system, status || undefined)
  },

  // Check if an operation can be performed
  canPerformOperation: (operationType) => {
    const { vitals, overallStatus, criticalSystems } = get()

    if (!vitals) {
      return { allowed: true, reason: 'Body status unknown - proceeding with caution' }
    }

    switch (operationType) {
      case 'pilot':
        // Pilots blocked when body is critical or 3+ systems critical
        if (overallStatus === 'critical') {
          return {
            allowed: false,
            reason: `Body health is critical (${(vitals.health_score ?? 0).toFixed(0)}%). Cannot start new pilots until system recovers.`,
          }
        }
        if (criticalSystems.length >= 3) {
          return {
            allowed: false,
            reason: `${criticalSystems.length} body systems are critical (${criticalSystems.join(', ')}). Cannot start new pilots.`,
          }
        }
        if (overallStatus === 'degraded') {
          return {
            allowed: true,
            reason: `Body health is degraded (${(vitals.health_score ?? 0).toFixed(0)}%). Proceed with caution.`,
          }
        }
        return { allowed: true }

      case 'agent_execution':
        // Agent execution blocked when muscular system is paralyzed
        const muscular = vitals.systems?.muscular
        if (muscular?.status === 'paralyzed' || (muscular?.score || 0) < 20) {
          return {
            allowed: false,
            reason: 'Muscular system is paralyzed. Agent execution is blocked until recovery.',
          }
        }
        if (overallStatus === 'critical') {
          return {
            allowed: true,
            reason: 'Body health is critical. Agent execution may be degraded.',
          }
        }
        return { allowed: true }

      case 'file_write':
        // File writes blocked when spine is critical
        const spine = vitals.systems?.spine
        if (spine?.status === 'critical' || (spine?.score || 0) < 20) {
          return {
            allowed: false,
            reason: 'Spine (API routing) is critical. File writes are blocked until recovery.',
          }
        }
        if (overallStatus === 'critical') {
          return {
            allowed: true,
            reason: 'Body health is critical. File operations may fail.',
          }
        }
        return { allowed: true }

      default:
        return { allowed: true }
    }
  },
}))

// Selector hooks for common use cases
export const useBodyHealth = () => useBodyStore((state) => ({
  status: state.overallStatus,
  score: state.healthScore,
  isHealthy: state.overallStatus === 'healthy',
  blocksOperations: state.blocksOperations,
}))

export const useBodyAlerts = () => useBodyStore((state) => ({
  alerts: state.alerts.filter((a) => !a.dismissed),
  criticalAlerts: state.alerts.filter((a) => a.severity === 'critical' && !a.dismissed),
  dismissAlert: state.dismissAlert,
}))

export const useBodyGovernance = () => useBodyStore((state) => ({
  canStartPilot: state.canPerformOperation('pilot'),
  canExecuteAgent: state.canPerformOperation('agent_execution'),
  canWriteFile: state.canPerformOperation('file_write'),
}))
