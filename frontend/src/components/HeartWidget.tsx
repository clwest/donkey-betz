/**
 * Session 702: HEART Widget - System Health Monitor
 *
 * Displays the health status of all 6 body parts:
 * - Brain (ThinkingAgent)
 * - Nervous System (LLM/ML Routers)
 * - Organs (72 Agents)
 * - Sensory (77 Spiders)
 * - Skin (Workspace Manager)
 * - Memory (Database & Redis)
 */

import { useQuery } from '@tanstack/react-query'
import { heartApi } from '@/lib/api'
import { useWebSocket } from '@/hooks/useWebSocket'
import {
  Heart,
  Brain,
  Zap,
  Users,
  Eye,
  Hand,
  Database,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useState, useEffect } from 'react'

// Body part icons and display names
const BODY_PARTS = {
  brain: { icon: Brain, label: 'Brain', description: 'ThinkingAgent' },
  nervous_system: { icon: Zap, label: 'Nervous', description: 'LLM Routers' },
  organs: { icon: Users, label: 'Organs', description: '72 Agents' },
  sensory: { icon: Eye, label: 'Sensory', description: '77 Spiders' },
  skin: { icon: Hand, label: 'Skin', description: 'Workspace' },
  memory: { icon: Database, label: 'Memory', description: 'DB + Redis' },
} as const

type BodyPart = keyof typeof BODY_PARTS

interface ComponentStatus {
  component: string
  display_name: string
  status: 'healthy' | 'degraded' | 'critical' | 'unknown'
  is_healthy: boolean
  response_time_ms?: number
  details?: Record<string, unknown>
  last_error?: string
}

interface HeartStatus {
  success: boolean
  health_score: number
  overall_status: 'healthy' | 'degraded' | 'critical' | 'unknown'
  is_alive: boolean
  last_check: string | null
  components: Record<string, ComponentStatus>
}

interface HeartWidgetProps {
  compact?: boolean
  showRefresh?: boolean
  onRefresh?: () => void
}

function getStatusColor(status: string, isHealthy?: boolean | null) {
  if (isHealthy === true || status === 'healthy') return 'text-accent-green'
  if (status === 'degraded') return 'text-accent-amber'
  if (status === 'critical' || isHealthy === false) return 'text-accent-red'
  return 'text-gray-400'
}

function getStatusBg(status: string, isHealthy?: boolean | null) {
  if (isHealthy === true || status === 'healthy') return 'bg-accent-green/20'
  if (status === 'degraded') return 'bg-accent-amber/20'
  if (status === 'critical' || isHealthy === false) return 'bg-accent-red/20'
  return 'bg-gray-500/20'
}

function HealthGauge({ score, status }: { score: number; status: string }) {
  const color = status === 'healthy' ? '#22c55e' : status === 'degraded' ? '#f59e0b' : '#ef4444'

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
          {score.toFixed(0)}%
        </p>
        <p className="text-xs text-gray-400 capitalize">{status}</p>
      </div>
    </div>
  )
}

function BodyPartIndicator({
  part,
  status,
  compact,
}: {
  part: BodyPart
  status?: ComponentStatus
  compact?: boolean
}) {
  const { icon: Icon, label, description } = BODY_PARTS[part]
  const isHealthy = status?.is_healthy ?? null
  const partStatus = status?.status ?? 'unknown'

  if (compact) {
    return (
      <div
        className={cn(
          'flex flex-col items-center gap-1 p-2 rounded-lg transition-colors',
          getStatusBg(partStatus, isHealthy)
        )}
        title={`${label}: ${partStatus}${status?.last_error ? `\n${status.last_error}` : ''}`}
      >
        <Icon size={18} className={getStatusColor(partStatus, isHealthy)} />
        <span className="text-[10px] text-gray-400">{label}</span>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg transition-colors border',
        getStatusBg(partStatus, isHealthy),
        isHealthy ? 'border-accent-green/30' : isHealthy === false ? 'border-accent-red/30' : 'border-dark-border'
      )}
    >
      <div
        className={cn(
          'h-10 w-10 rounded-lg flex items-center justify-center',
          getStatusBg(partStatus, isHealthy)
        )}
      >
        <Icon size={20} className={getStatusColor(partStatus, isHealthy)} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-medium text-sm">{label}</p>
          {isHealthy === true && <CheckCircle size={12} className="text-accent-green" />}
          {isHealthy === false && <XCircle size={12} className="text-accent-red" />}
        </div>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
      {status?.response_time_ms && (
        <span className="text-xs text-gray-500">{status.response_time_ms}ms</span>
      )}
    </div>
  )
}

export default function HeartWidget({ compact = false, showRefresh = true, onRefresh }: HeartWidgetProps) {
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  // Fetch heart status with polling every 30 seconds
  const {
    data: heartData,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['heart-status'],
    queryFn: () => heartApi.status(),
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
    if (heartData?.data?.last_check) {
      setLastUpdate(new Date(heartData.data.last_check))
    }
  }, [heartData])

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

  const status: HeartStatus = heartData?.data || {
    success: false,
    health_score: 0,
    overall_status: 'unknown',
    is_alive: false,
    last_check: null,
    components: {},
  }

  const bodyParts: BodyPart[] = ['brain', 'nervous_system', 'organs', 'sensory', 'skin', 'memory']

  if (compact) {
    // Compact view for smaller spaces
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Heart size={16} className={getStatusColor(status.overall_status)} />
            <span className="font-medium text-sm">System Health</span>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                'text-sm font-bold',
                getStatusColor(status.overall_status)
              )}
            >
              {status.health_score.toFixed(0)}%
            </span>
            {showRefresh && (
              <button
                onClick={handleRefresh}
                disabled={isFetching}
                className="p-1 rounded hover:bg-dark-bg transition-colors"
                title="Refresh health status"
              >
                <RefreshCw
                  size={14}
                  className={cn('text-gray-400', isFetching && 'animate-spin')}
                />
              </button>
            )}
          </div>
        </div>
        <div className="grid grid-cols-6 gap-1">
          {bodyParts.map((part) => (
            <BodyPartIndicator
              key={part}
              part={part}
              status={status.components[part]}
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
          <HealthGauge score={status.health_score} status={status.overall_status} />
        </div>
        <div className="flex flex-col items-end gap-1">
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
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              Last check: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      <h3 className="text-sm font-medium text-gray-400 mb-3">Body Part Status</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {bodyParts.map((part) => (
          <BodyPartIndicator
            key={part}
            part={part}
            status={status.components[part]}
          />
        ))}
      </div>

      {/* Summary stats */}
      <div className="mt-4 pt-4 border-t border-dark-border flex items-center justify-between text-xs text-gray-500">
        <span>
          {Object.values(status.components).filter((c) => c?.is_healthy).length}/
          {Object.keys(status.components).length} components healthy
        </span>
        <span className={cn(
          'px-2 py-1 rounded',
          status.is_alive ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-red/20 text-accent-red'
        )}>
          {status.is_alive ? 'System Alive' : 'System Down'}
        </span>
      </div>
    </div>
  )
}
