/**
 * Session 702: HEART Widget - System Health Monitor
 * Session 712: Updated to use actual 7 body systems
 *
 * Displays the health status of all 7 body systems:
 * - HEART - Health monitoring (heartbeat, component checks)
 * - LUNGS - Resource/budget management (oxygen = API budget)
 * - CIRCULATORY - Data flow monitoring (blood = data pipelines)
 * - SPINE - Central API routing (neural pathways)
 * - IMMUNE - Security & threat detection
 * - DIGESTIVE - Data ingestion & processing (spider data)
 * - MUSCULAR - Agent work execution (strength = success rate)
 */

import { useQuery } from '@tanstack/react-query'
import { bodyApi } from '@/lib/api'
import { useWebSocket } from '@/hooks/useWebSocket'
import {
  Heart,
  Wind,
  Droplets,
  Bone,
  Shield,
  UtensilsCrossed,
  Dumbbell,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  ExternalLink,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useState, useEffect } from 'react'

// Session 712: Updated to actual 7 body systems
const BODY_SYSTEMS = {
  heart: { icon: Heart, label: 'Heart', description: 'Health Monitor', emoji: '❤️' },
  lungs: { icon: Wind, label: 'Lungs', description: 'Resource Budget', emoji: '🫁' },
  circulatory: { icon: Droplets, label: 'Circulatory', description: 'Data Flow', emoji: '🩸' },
  spine: { icon: Bone, label: 'Spine', description: 'API Router', emoji: '🦴' },
  immune: { icon: Shield, label: 'Immune', description: 'Security', emoji: '🛡️' },
  digestive: { icon: UtensilsCrossed, label: 'Digestive', description: 'Data Ingestion', emoji: '🍽️' },
  muscular: { icon: Dumbbell, label: 'Muscular', description: 'Agent Work', emoji: '💪' },
} as const

type BodySystem = keyof typeof BODY_SYSTEMS

// Session 712: Updated interfaces for body vitals API
interface SystemStatus {
  status: string
  score: number
  emoji?: string
  alerts?: string[]
  details?: Record<string, unknown>
}

interface BodyVitals {
  timestamp: string
  overall_health: 'healthy' | 'degraded' | 'critical' | 'unknown'
  health_score: number
  is_healthy: boolean
  systems: Record<string, SystemStatus>
  check_duration_ms: number
}

// Session 712: Healthy status values for each system
const HEALTHY_STATUSES: Record<string, string[]> = {
  heart: ['healthy'],
  lungs: ['healthy', 'normal', 'optimal'],
  circulatory: ['flowing', 'healthy'],
  spine: ['aligned', 'healthy'],
  immune: ['healthy', 'protected'],
  digestive: ['healthy', 'processing', 'digesting'],
  muscular: ['strong', 'fit', 'healthy'],
}

// Helper to determine if a system is healthy based on status or score
function isSystemHealthy(system: string, status?: SystemStatus): boolean {
  if (!status) return false
  const healthyStatuses = HEALTHY_STATUSES[system] || ['healthy']
  return healthyStatuses.includes(status.status) || status.score >= 80
}

interface HeartWidgetProps {
  compact?: boolean
  showRefresh?: boolean
  onRefresh?: () => void
}

// Session 712: Updated to handle various healthy status values
const ALL_HEALTHY_STATUSES = ['healthy', 'normal', 'optimal', 'flowing', 'aligned', 'protected', 'strong', 'fit', 'processing', 'digesting']
const DEGRADED_STATUSES = ['degraded', 'fatigued', 'sluggish', 'slow', 'depleted']
const CRITICAL_STATUSES = ['critical', 'blocked', 'strained', 'paralyzed', 'starving', 'bloated']

function getStatusColor(status: string, isHealthy?: boolean) {
  if (isHealthy === true || ALL_HEALTHY_STATUSES.includes(status)) return 'text-accent-green'
  if (DEGRADED_STATUSES.includes(status)) return 'text-accent-amber'
  if (CRITICAL_STATUSES.includes(status) || isHealthy === false) return 'text-accent-red'
  return 'text-gray-400'
}

function getStatusBg(status: string, isHealthy?: boolean) {
  if (isHealthy === true || ALL_HEALTHY_STATUSES.includes(status)) return 'bg-accent-green/20'
  if (DEGRADED_STATUSES.includes(status)) return 'bg-accent-amber/20'
  if (CRITICAL_STATUSES.includes(status) || isHealthy === false) return 'bg-accent-red/20'
  return 'bg-gray-500/20'
}

function HealthGauge({ score, status }: { score: number; status: string }) {
  // Session 712: Use score-based color determination
  const color = score >= 80 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444'

  return (
    <div className="flex items-center gap-3">
      <div className="relative h-16 w-16">
        {/* Background circle */}
        <svg className="h-16 w-16 -rotate-90 transform">
          <circle
            cx="32"
            cy="32"
            r="28"
            stroke="currentColor"
            strokeWidth="6"
            fill="none"
            className="text-dark-border"
          />
          <circle
            cx="32"
            cy="32"
            r="28"
            stroke={color}
            strokeWidth="6"
            fill="none"
            strokeDasharray={`${(score / 100) * 176} 176`}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>
        {/* Center icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <Heart size={20} style={{ color }} className="animate-pulse" />
        </div>
      </div>
      <div>
        <p className="text-2xl font-bold" style={{ color }}>
          {(score ?? 0).toFixed(0)}%
        </p>
        <p className="text-xs text-gray-400 capitalize">{status}</p>
      </div>
    </div>
  )
}

// Session 712: Updated to use BodySystem type
function BodySystemIndicator({
  system,
  status,
  compact,
}: {
  system: BodySystem
  status?: SystemStatus
  compact?: boolean
}) {
  const { icon: Icon, label, description, emoji } = BODY_SYSTEMS[system]
  // Session 712: Use helper to determine health from status/score
  const isHealthy = isSystemHealthy(system, status)
  const systemStatus = status?.status ?? 'unknown'
  const score = status?.score ?? 0

  if (compact) {
    return (
      <div
        className={cn(
          'flex flex-col items-center gap-1 p-2 rounded-lg transition-colors',
          getStatusBg(systemStatus, isHealthy)
        )}
        title={`${label}: ${systemStatus} (${(score ?? 0).toFixed(0)}%)`}
      >
        <span className="text-lg">{emoji}</span>
        <span className="text-[10px] text-gray-400">{label}</span>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg transition-colors border',
        getStatusBg(systemStatus, isHealthy),
        isHealthy ? 'border-accent-green/30' : isHealthy === false ? 'border-accent-red/30' : 'border-dark-border'
      )}
    >
      <div
        className={cn(
          'h-10 w-10 rounded-lg flex items-center justify-center',
          getStatusBg(systemStatus, isHealthy)
        )}
      >
        <Icon size={20} className={getStatusColor(systemStatus, isHealthy)} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-medium text-sm">{label}</p>
          {isHealthy === true && <CheckCircle size={12} className="text-accent-green" />}
          {isHealthy === false && <XCircle size={12} className="text-accent-red" />}
        </div>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
      <span className={cn(
        'text-sm font-medium',
        getStatusColor(systemStatus, isHealthy)
      )}>
        {(score ?? 0).toFixed(0)}%
      </span>
    </div>
  )
}

export default function HeartWidget({ compact = false, showRefresh = true, onRefresh }: HeartWidgetProps) {
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  // Session 712: Use body vitals API for unified body health
  const {
    data: bodyData,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 30000, // Poll every 30 seconds
    staleTime: 25000,
  })

  // WebSocket for real-time updates (optional - consumer may not exist yet)
  // The dashboard WebSocket is used as a fallback for heart updates
  useWebSocket('/dashboard', {
    onMessage: (data) => {
      // Listen for heartbeat updates broadcast to dashboard
      if (data && typeof data === 'object' && 'type' in data) {
        const msg = data as { type: string; health_score?: number }
        if (msg.type === 'heartbeat' && msg.health_score !== undefined) {
          refetch()
          setLastUpdate(new Date())
        }
      }
    },
  })

  // Update lastUpdate when data changes
  useEffect(() => {
    if (bodyData?.data?.timestamp) {
      setLastUpdate(new Date(bodyData.data.timestamp))
    }
  }, [bodyData])

  const handleRefresh = () => {
    refetch()
    onRefresh?.()
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="animate-spin text-primary-400" size={24} />
          <span className="ml-2 text-gray-400">Loading system health...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-center gap-3 p-4 rounded-lg bg-accent-red/10 border border-accent-red/30">
          <AlertTriangle className="text-accent-red" size={20} />
          <div>
            <p className="font-medium text-accent-red">Failed to load system health</p>
            <p className="text-xs text-gray-400">Check if the HEART service is running</p>
          </div>
          <button
            onClick={handleRefresh}
            className="ml-auto btn btn-secondary btn-sm"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Session 712: Use body vitals data structure
  const vitals: BodyVitals = bodyData?.data || {
    timestamp: new Date().toISOString(),
    overall_health: 'unknown',
    health_score: 0,
    systems: {},
    check_duration_ms: 0,
  }

  // Session 712: All 7 body systems
  const bodySystems: BodySystem[] = ['heart', 'lungs', 'circulatory', 'spine', 'immune', 'digestive', 'muscular']

  // Count healthy systems using the helper function
  const healthySystems = bodySystems.filter(system => isSystemHealthy(system, vitals.systems[system])).length
  const totalSystems = bodySystems.length

  if (compact) {
    // Compact view for smaller spaces
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Heart size={16} className={cn('animate-pulse', getStatusColor(vitals.overall_health))} />
            <span className="font-medium text-sm">Body Health</span>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                'text-sm font-bold',
                getStatusColor(vitals.overall_health)
              )}
            >
              {(vitals.health_score ?? 0).toFixed(0)}%
            </span>
            {showRefresh && (
              <button
                onClick={handleRefresh}
                disabled={isFetching}
                className="p-1 rounded hover:bg-dark-bg transition-colors"
                title="Refresh body health"
              >
                <RefreshCw
                  size={14}
                  className={cn('text-gray-400', isFetching && 'animate-spin')}
                />
              </button>
            )}
          </div>
        </div>
        <div className="grid grid-cols-7 gap-1">
          {bodySystems.map((system) => (
            <BodySystemIndicator
              key={system}
              system={system}
              status={vitals.systems[system]}
              compact
            />
          ))}
        </div>
      </div>
    )
  }

  // Full view
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <HealthGauge score={vitals.health_score} status={vitals.overall_health} />
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className="flex items-center gap-2">
            {showRefresh && (
              <button
                onClick={handleRefresh}
                disabled={isFetching}
                className="btn btn-secondary btn-sm flex items-center gap-2"
              >
                <RefreshCw size={14} className={cn(isFetching && 'animate-spin')} />
                Refresh
              </button>
            )}
            <a
              href="/workspace?tab=system"
              className="btn btn-secondary btn-sm flex items-center gap-2"
            >
              <ExternalLink size={14} />
              Details
            </a>
          </div>
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              Last check: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      <h3 className="text-sm font-medium text-gray-400 mb-3">Body Systems Status</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {bodySystems.map((system) => (
          <BodySystemIndicator
            key={system}
            system={system}
            status={vitals.systems[system]}
          />
        ))}
      </div>

      {/* Summary stats */}
      <div className="mt-4 pt-4 border-t border-dark-border flex items-center justify-between text-xs text-gray-500">
        <span>
          {healthySystems}/{totalSystems} systems healthy
        </span>
        <span className={cn(
          'px-2 py-1 rounded capitalize',
          vitals.overall_health === 'healthy' ? 'bg-accent-green/20 text-accent-green' :
          vitals.overall_health === 'degraded' ? 'bg-accent-amber/20 text-accent-amber' :
          'bg-accent-red/20 text-accent-red'
        )}>
          {vitals.overall_health}
        </span>
      </div>
    </div>
  )
}
