/**
 * Session 713: Body Governance Service
 *
 * Provides governance checks for operations based on body health status.
 * This service wraps the body store with additional utility functions
 * for use in components that need to check before performing operations.
 */

import { useBodyStore } from '@/stores/bodyStore'

export type OperationType = 'pilot' | 'agent_execution' | 'file_write' | 'hive_mind' | 'bulk_operation'

export interface GovernanceCheck {
  allowed: boolean
  reason?: string
  severity?: 'info' | 'warning' | 'error'
}

/**
 * Check if an operation is allowed based on current body health.
 * This is a direct function call (not a hook) for use in event handlers.
 */
export function checkBodyGovernance(operationType: OperationType): GovernanceCheck {
  const state = useBodyStore.getState()
  const check = state.canPerformOperation(operationType as 'pilot' | 'agent_execution' | 'file_write')

  return {
    allowed: check.allowed,
    reason: check.reason,
    severity: check.allowed ? (check.reason ? 'warning' : 'info') : 'error',
  }
}

/**
 * Check if the system is healthy enough for general operations.
 */
export function isSystemOperational(): boolean {
  const state = useBodyStore.getState()
  return !state.blocksOperations
}

/**
 * Get the current body health status summary.
 */
export function getBodyHealthSummary(): {
  status: string
  score: number
  criticalSystems: string[]
  blocksOperations: boolean
} {
  const state = useBodyStore.getState()
  return {
    status: state.overallStatus,
    score: state.healthScore,
    criticalSystems: state.criticalSystems,
    blocksOperations: state.blocksOperations,
  }
}

/**
 * Check multiple operations at once.
 */
export function checkMultipleOperations(
  operations: OperationType[]
): Record<OperationType, GovernanceCheck> {
  const results: Record<string, GovernanceCheck> = {}

  for (const op of operations) {
    results[op] = checkBodyGovernance(op)
  }

  return results as Record<OperationType, GovernanceCheck>
}

/**
 * Get a user-friendly message for body governance blocking.
 */
export function getGovernanceBlockMessage(operationType: OperationType): string {
  const check = checkBodyGovernance(operationType)

  if (check.allowed) {
    return check.reason || 'Operation allowed'
  }

  const operationNames: Record<OperationType, string> = {
    pilot: 'Starting a pilot',
    agent_execution: 'Agent execution',
    file_write: 'File operations',
    hive_mind: 'Hive Mind sessions',
    bulk_operation: 'Bulk operations',
  }

  return `${operationNames[operationType]} is currently blocked. ${check.reason || ''}`
}

/**
 * Escalate to human attention when body health is critical.
 * This can be called to notify the Human page of critical conditions.
 */
export async function escalateToHuman(
  reason: string,
  severity: 'low' | 'medium' | 'high' | 'critical' = 'high'
): Promise<void> {
  // This would typically call an API to create an attention item
  // For now, we log and could dispatch to a notification system
  console.warn(`[Body Governance] Escalation to Human: ${severity.toUpperCase()} - ${reason}`)

  // Future: Call human attention API
  // await humanApi.createAttentionItem({ reason, severity, source: 'body_governance' })
}

/**
 * Request body coordination when systems are degraded.
 */
export async function requestBodyCoordination(_systems?: string[]): Promise<void> {
  const { bodyApi } = await import('@/lib/api')

  try {
    await bodyApi.coordination.run()
    console.info('[Body Governance] Body coordination requested')
  } catch (error) {
    console.error('[Body Governance] Failed to request coordination:', error)
  }
}

/**
 * Governance configuration - can be adjusted based on requirements.
 */
export const GOVERNANCE_CONFIG = {
  // Minimum health score to allow pilots
  minPilotHealthScore: 40,

  // Minimum health score to allow bulk operations
  minBulkOperationScore: 60,

  // Maximum critical systems before blocking all operations
  maxCriticalSystemsBeforeBlock: 3,

  // Systems that are critical for specific operations
  criticalSystemsForOperations: {
    pilot: ['heart', 'lungs', 'spine'],
    agent_execution: ['muscular', 'spine'],
    file_write: ['spine', 'circulatory'],
    hive_mind: ['heart', 'spine', 'muscular'],
    bulk_operation: ['heart', 'lungs', 'spine', 'muscular'],
  },
}

/**
 * Advanced governance check with custom thresholds.
 */
export function checkAdvancedGovernance(
  operationType: OperationType,
  config?: Partial<typeof GOVERNANCE_CONFIG>
): GovernanceCheck {
  const state = useBodyStore.getState()
  const mergedConfig = { ...GOVERNANCE_CONFIG, ...config }

  // Basic check first
  const basicCheck = checkBodyGovernance(operationType)
  if (!basicCheck.allowed) {
    return basicCheck
  }

  // Check health score threshold
  const minScore = operationType === 'bulk_operation'
    ? mergedConfig.minBulkOperationScore
    : mergedConfig.minPilotHealthScore

  if (state.healthScore < minScore) {
    return {
      allowed: false,
      reason: `Health score (${(state.healthScore ?? 0).toFixed(0)}%) is below minimum required (${minScore}%) for ${operationType}`,
      severity: 'error',
    }
  }

  // Check critical systems for this operation
  const criticalForOp = mergedConfig.criticalSystemsForOperations[operationType] || []
  const affectedCritical = state.criticalSystems.filter((s) => criticalForOp.includes(s))

  if (affectedCritical.length > 0) {
    return {
      allowed: false,
      reason: `Critical systems required for ${operationType}: ${affectedCritical.join(', ')}`,
      severity: 'error',
    }
  }

  return { allowed: true }
}
