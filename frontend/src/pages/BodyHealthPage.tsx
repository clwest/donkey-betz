/**
 * Session 710: Body Health Dashboard
 * Session 722: Added BRAIN system
 * Session 723: Added SKIN system
 * Session 724: Added NERVOUS system
 *
 * Unified view of all 10 body systems health status.
 * Provides real-time monitoring of the AI body's health.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  bodyApi, heartApi, lungsApi, circulatoryApi, spineApi,
  immuneApi, digestiveApi, muscularApi, brainApi, skinApi, nervousApi
} from '@/lib/api'
import {
  Heart, Wind, Droplets, Bone, Shield, Apple, Dumbbell, Brain, Layers,
  AlertTriangle, CheckCircle, XCircle, Activity, RefreshCw,
  Info, Clock, X, Zap, Server, Database, Cpu, DollarSign,
  Users, GitBranch, Gauge, BarChart3, MessageSquare, Sparkles, FileEdit, FolderOpen
} from 'lucide-react'
import { cn } from '@/lib/cn'

// System configuration with icons and colors
const SYSTEM_CONFIG: Record<string, {
  icon: typeof Heart
  label: string
  color: string
  bgColor: string
  description: string
}> = {
  heart: {
    icon: Heart,
    label: 'HEART',
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    description: 'Core platform health monitoring'
  },
  lungs: {
    icon: Wind,
    label: 'LUNGS',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    description: 'Resource & budget management'
  },
  circulatory: {
    icon: Droplets,
    label: 'CIRCULATORY',
    color: 'text-pink-500',
    bgColor: 'bg-pink-500/10',
    description: 'Data flow monitoring'
  },
  spine: {
    icon: Bone,
    label: 'SPINE',
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10',
    description: 'Central API routing'
  },
  immune: {
    icon: Shield,
    label: 'IMMUNE',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    description: 'Security & threat detection'
  },
  digestive: {
    icon: Apple,
    label: 'DIGESTIVE',
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    description: 'Data ingestion & processing'
  },
  muscular: {
    icon: Dumbbell,
    label: 'MUSCULAR',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    description: 'Agent work execution'
  },
  brain: {
    icon: Brain,
    label: 'BRAIN',
    color: 'text-cyan-500',
    bgColor: 'bg-cyan-500/10',
    description: 'Cognitive processing'
  },
  skin: {
    icon: Layers,
    label: 'SKIN',
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
    description: 'Workspace output monitoring'
  },
  nervous: {
    icon: Zap,
    label: 'NERVOUS',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-400/10',
    description: 'WebSocket communication monitoring'
  }
}

// Status to visual mapping
const STATUS_CONFIG: Record<string, { color: string; icon: typeof CheckCircle }> = {
  healthy: { color: 'text-green-500', icon: CheckCircle },
  beating: { color: 'text-green-500', icon: CheckCircle },
  breathing: { color: 'text-green-500', icon: CheckCircle },
  flowing: { color: 'text-green-500', icon: CheckCircle },
  aligned: { color: 'text-green-500', icon: CheckCircle },
  strong: { color: 'text-green-500', icon: CheckCircle },
  fit: { color: 'text-green-500', icon: CheckCircle },
  comfortable: { color: 'text-green-500', icon: CheckCircle },

  // Warning states
  irregular: { color: 'text-yellow-500', icon: AlertTriangle },
  gasping: { color: 'text-yellow-500', icon: AlertTriangle },
  slow: { color: 'text-yellow-500', icon: AlertTriangle },
  strained: { color: 'text-yellow-500', icon: AlertTriangle },
  alert: { color: 'text-yellow-500', icon: AlertTriangle },
  sluggish: { color: 'text-yellow-500', icon: AlertTriangle },
  bloated: { color: 'text-yellow-500', icon: AlertTriangle },
  fatigued: { color: 'text-yellow-500', icon: AlertTriangle },
  elevated: { color: 'text-yellow-500', icon: AlertTriangle },
  tachycardia: { color: 'text-yellow-500', icon: AlertTriangle },
  congested: { color: 'text-yellow-500', icon: AlertTriangle },
  fighting: { color: 'text-yellow-500', icon: AlertTriangle },

  // Critical states
  critical: { color: 'text-red-500', icon: XCircle },
  flat: { color: 'text-red-500', icon: XCircle },
  suffocating: { color: 'text-red-500', icon: XCircle },
  blocked: { color: 'text-red-500', icon: XCircle },
  injured: { color: 'text-red-500', icon: XCircle },
  compromised: { color: 'text-red-500', icon: XCircle },
  overwhelmed: { color: 'text-red-500', icon: XCircle },
  starving: { color: 'text-red-500', icon: XCircle },
  paralyzed: { color: 'text-red-500', icon: XCircle },
  offline: { color: 'text-red-500', icon: XCircle },
  overloaded: { color: 'text-red-500', icon: XCircle },

  // Brain-specific states
  focused: { color: 'text-green-500', icon: CheckCircle },
  thinking: { color: 'text-green-500', icon: CheckCircle },
  foggy: { color: 'text-yellow-500', icon: AlertTriangle },
  resting: { color: 'text-blue-500', icon: Info },

  // Skin-specific states
  active: { color: 'text-green-500', icon: CheckCircle },
  sweating: { color: 'text-yellow-500', icon: AlertTriangle },
  irritated: { color: 'text-orange-500', icon: AlertTriangle },
  damaged: { color: 'text-red-500', icon: XCircle },
  healing: { color: 'text-blue-500', icon: Info },
  dormant: { color: 'text-gray-500', icon: Info },

  // Nervous-specific states
  responsive: { color: 'text-green-500', icon: CheckCircle },
  numb: { color: 'text-orange-500', icon: AlertTriangle },

  // Unknown
  unknown: { color: 'text-gray-500', icon: Info },
  error: { color: 'text-red-500', icon: XCircle },
}

// Types
interface SystemVitals {
  status: string
  score: number
  emoji: string
  alerts?: Array<{ message: string; severity: string }>
  details?: Record<string, unknown>
}

interface BodyVitals {
  success: boolean
  timestamp: string
  overall_health: string
  health_score: number
  systems: Record<string, SystemVitals>
  alerts: Array<{ system: string; message: string; severity: string; timestamp?: string }>
  recommendation?: string
}

interface BodyAlert {
  system: string
  message: string
  severity: string
  timestamp?: string
}

// System Card Component
function BodySystemCard({
  systemName,
  vitals,
  onClick
}: {
  systemName: string
  vitals: SystemVitals
  onClick?: () => void
}) {
  const config = SYSTEM_CONFIG[systemName]
  const statusConfig = STATUS_CONFIG[vitals.status] || STATUS_CONFIG.unknown
  const Icon = config?.icon || Activity
  const StatusIcon = statusConfig.icon

  return (
    <button
      onClick={onClick}
      className={cn(
        'p-4 rounded-lg border transition-all hover:shadow-md',
        'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700',
        'text-left w-full'
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={cn('p-2 rounded-lg', config?.bgColor || 'bg-gray-500/10')}>
          <Icon className={cn('w-5 h-5', config?.color || 'text-gray-400')} />
        </div>
        <div className="flex items-center gap-1">
          <StatusIcon className={cn('w-4 h-4', statusConfig.color)} />
          <span className="text-2xl">{vitals.emoji}</span>
        </div>
      </div>

      <h3 className="text-sm font-medium text-zinc-300 mb-1">
        {config?.label || systemName.toUpperCase()}
      </h3>

      <p className={cn('text-sm font-medium capitalize', statusConfig.color)}>
        {vitals.status}
      </p>

      <div className="mt-2 flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full transition-all',
              vitals.score >= 70 ? 'bg-green-500' :
              vitals.score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
            )}
            style={{ width: `${Math.max(0, Math.min(100, vitals.score))}%` }}
          />
        </div>
        <span className="text-xs text-zinc-500 w-8 text-right">
          {vitals.score.toFixed(0)}%
        </span>
      </div>

      <p className="text-xs text-zinc-600 mt-2">
        {config?.description || 'System monitoring'}
      </p>
    </button>
  )
}

// Alerts Feed Component
function BodyAlertsFeed({ alerts }: { alerts: BodyAlert[] }) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-8 text-zinc-500">
        <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
        <p>No active alerts</p>
        <p className="text-xs">All systems operating normally</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {alerts.map((alert, idx) => {
        const config = SYSTEM_CONFIG[alert.system]
        const Icon = config?.icon || Activity

        return (
          <div
            key={`${alert.system}-${idx}`}
            className={cn(
              'p-3 rounded-lg border flex items-start gap-3',
              alert.severity === 'critical' ? 'bg-red-500/10 border-red-500/30' :
              alert.severity === 'warning' ? 'bg-yellow-500/10 border-yellow-500/30' :
              'bg-blue-500/10 border-blue-500/30'
            )}
          >
            <Icon className={cn('w-4 h-4 mt-0.5', config?.color || 'text-gray-400')} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs font-medium text-zinc-400 uppercase">
                  {alert.system}
                </span>
                <span className={cn(
                  'text-xs px-1.5 py-0.5 rounded',
                  alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                  alert.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-blue-500/20 text-blue-400'
                )}>
                  {alert.severity}
                </span>
              </div>
              <p className="text-sm text-zinc-300">{alert.message}</p>
              {alert.timestamp && (
                <p className="text-xs text-zinc-600 mt-1 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// Health Score Gauge Component
function HealthScoreGauge({ score, status }: { score: number; status: string }) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return 'text-green-500'
    if (s >= 60) return 'text-yellow-500'
    if (s >= 40) return 'text-orange-500'
    return 'text-red-500'
  }

  const getStatusLabel = (st: string) => {
    switch (st) {
      case 'healthy': return 'Excellent'
      case 'good': return 'Good'
      case 'degraded': return 'Degraded'
      case 'critical': return 'Critical'
      case 'failing': return 'Failing'
      default: return st
    }
  }

  return (
    <div className="text-center">
      <div className="relative w-32 h-32 mx-auto">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-zinc-800"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${score * 3.52} 352`}
            strokeLinecap="round"
            className={getScoreColor(score)}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn('text-3xl font-bold', getScoreColor(score))}>
            {score.toFixed(0)}
          </span>
          <span className="text-xs text-zinc-500">/ 100</span>
        </div>
      </div>
      <p className={cn('mt-2 font-medium capitalize', getScoreColor(score))}>
        {getStatusLabel(status)}
      </p>
    </div>
  )
}

// ============================================================================
// Session 711: System Detail Panel - Shows detailed info when system selected
// ============================================================================

interface SystemDetailPanelProps {
  systemName: string
  onClose: () => void
}

function SystemDetailPanel({ systemName, onClose }: SystemDetailPanelProps) {
  const config = SYSTEM_CONFIG[systemName]
  const Icon = config?.icon || Activity

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={cn('p-3 rounded-lg', config?.bgColor || 'bg-gray-500/10')}>
            <Icon className={cn('w-6 h-6', config?.color || 'text-gray-400')} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-zinc-100">{config?.label || systemName.toUpperCase()} Details</h2>
            <p className="text-sm text-zinc-500">{config?.description}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors"
        >
          <X className="w-5 h-5 text-zinc-400" />
        </button>
      </div>

      {/* System-specific content */}
      {systemName === 'heart' && <HeartDetailView />}
      {systemName === 'lungs' && <LungsDetailView />}
      {systemName === 'circulatory' && <CirculatoryDetailView />}
      {systemName === 'spine' && <SpineDetailView />}
      {systemName === 'immune' && <ImmuneDetailView />}
      {systemName === 'digestive' && <DigestiveDetailView />}
      {systemName === 'muscular' && <MuscularDetailView />}
      {systemName === 'brain' && <BrainDetailView />}
      {systemName === 'skin' && <SkinDetailView />}
      {systemName === 'nervous' && <NervousDetailView />}
    </div>
  )
}

// HEART Detail View
function HeartDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['heartStatus'],
    queryFn: () => heartApi.status(),
  })

  const status = data?.data

  if (isLoading) return <DetailLoading />

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              status?.is_alive ? 'text-green-400' : 'text-red-400'
            )}>
              {status?.is_alive ? 'ALIVE' : 'DOWN'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.health_score || 0) >= 80 ? 'text-green-400' :
              (status?.health_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.health_score?.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Health Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {status?.components?.components_healthy || 0}/{status?.components?.components_checked || 0}
            </div>
            <div className="text-xs text-zinc-500">Components OK</div>
          </div>
        </div>
        {status?.last_check && (
          <div className="mt-3 text-center text-xs text-zinc-500">
            Last check: {new Date(status.last_check).toLocaleString()}
          </div>
        )}
      </div>

      {/* Components Grid */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">System Components</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {status?.components?.components && Object.entries(status.components.components).map(([name, comp]: [string, any]) => (
            <div key={name} className="bg-zinc-900/50 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {name === 'brain' && <Cpu className="w-4 h-4 text-purple-400" />}
                  {name === 'memory' && <Database className="w-4 h-4 text-blue-400" />}
                  {name === 'nervous_system' && <Zap className="w-4 h-4 text-yellow-400" />}
                  {name === 'organs' && <Users className="w-4 h-4 text-green-400" />}
                  {name === 'sensory' && <Activity className="w-4 h-4 text-pink-400" />}
                  {name === 'skin' && <Server className="w-4 h-4 text-cyan-400" />}
                  {!['brain', 'memory', 'nervous_system', 'organs', 'sensory', 'skin'].includes(name) && <Activity className="w-4 h-4 text-zinc-400" />}
                  <span className="text-sm font-medium text-zinc-300">{comp?.name || name.replace('_', ' ')}</span>
                </div>
                <span className={cn(
                  'px-2 py-0.5 rounded text-xs font-medium',
                  comp?.status === 'healthy' || comp?.status === 'connected' ? 'bg-green-500/20 text-green-400' :
                  comp?.status === 'degraded' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'
                )}>
                  {comp?.status || 'unknown'}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs text-zinc-500">
                <span>{comp?.response_time_ms ?? 0}ms response</span>
                <span>{comp?.uptime_percent_24h?.toFixed(1) || 100}% uptime (24h)</span>
              </div>
              {/* Component Details */}
              {comp?.details && (
                <div className="mt-2 pt-2 border-t border-zinc-700/50">
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(comp.details).map(([key, value]) => (
                      <span key={key} className="text-xs px-1.5 py-0.5 bg-zinc-800 rounded text-zinc-400">
                        {key}: {typeof value === 'object' && value !== null ? (Array.isArray(value) ? value.length : Object.keys(value).length) : String(value ?? 'null')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// LUNGS Detail View
function LungsDetailView() {
  const { data: statusData, isLoading: statusLoading } = useQuery({
    queryKey: ['lungsStatus'],
    queryFn: () => lungsApi.status(),
  })

  const { data: budgetsData } = useQuery({
    queryKey: ['lungsBudgets'],
    queryFn: () => lungsApi.budgets(),
  })

  const status = statusData?.data
  const budgets = budgetsData?.data?.budgets || []

  if (statusLoading) return <DetailLoading />

  return (
    <div className="space-y-4">
      {/* Today's Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Gauge className="w-4 h-4" />
          Budget Status
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-2xl font-bold text-blue-400">
              {status?.oxygen_level?.toFixed(1) || 100}%
            </div>
            <div className="text-xs text-zinc-500">Oxygen Level</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">
              ${status?.total_cost_today?.toFixed(4) || '0.00'}
            </div>
            <div className="text-xs text-zinc-500">Cost Today</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-400">
              {status?.total_calls_today || 0}
            </div>
            <div className="text-xs text-zinc-500">API Calls</div>
          </div>
        </div>
        <div className="mt-3">
          <div className="h-2 bg-zinc-700 rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all',
                (status?.oxygen_level || 100) >= 50 ? 'bg-blue-500' :
                (status?.oxygen_level || 100) >= 20 ? 'bg-yellow-500' : 'bg-red-500'
              )}
              style={{ width: `${status?.oxygen_level || 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Provider Status */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Activity className="w-4 h-4" />
          Provider Usage (Today)
        </h3>
        <div className="space-y-3">
          {status?.providers && Object.entries(status.providers).map(([name, provider]: [string, any]) => (
            <div key={name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm text-zinc-300 capitalize">{name.replace('_', ' ')}</span>
                <span className="text-xs text-zinc-500">
                  ${provider.cost_today?.toFixed(4) || '0.00'} • {provider.calls_today || 0} calls
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className={cn(
                  'text-xs font-medium',
                  provider.oxygen_level >= 80 ? 'text-green-400' :
                  provider.oxygen_level >= 50 ? 'text-yellow-400' : 'text-red-400'
                )}>
                  {provider.oxygen_level?.toFixed(1) || 100}%
                </span>
              </div>
            </div>
          ))}
          {!status?.providers && (
            <p className="text-sm text-zinc-500">No provider data available</p>
          )}
        </div>
      </div>

      {/* Budgets List */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <DollarSign className="w-4 h-4" />
          Budget Limits
        </h3>
        <div className="space-y-3">
          {budgets.slice(0, 6).map((budget: any) => {
            const limit = budget.cost_limit || budget.limit || budget.daily_limit || 0
            const providerName = budget.scope_identifier || ''
            const providerData = status?.providers?.[providerName]
            const used = providerData?.cost_today || 0
            const usagePercent = limit > 0 ? (used / limit) * 100 : 0

            return (
              <div key={budget.id || budget.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-zinc-300">{budget.name}</span>
                  <span className="text-xs text-zinc-500">
                    ${used.toFixed(2)} / ${limit.toFixed(2)}
                  </span>
                </div>
                <div className="w-24 h-2 bg-zinc-700 rounded-full overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full',
                      usagePercent < 50 ? 'bg-green-500' :
                      usagePercent < 80 ? 'bg-yellow-500' : 'bg-red-500'
                    )}
                    style={{ width: `${Math.min(100, usagePercent)}%` }}
                  />
                </div>
              </div>
            )
          })}
          {budgets.length === 0 && (
            <p className="text-sm text-zinc-500">No budgets configured</p>
          )}
        </div>
      </div>
    </div>
  )
}

// CIRCULATORY Detail View
function CirculatoryDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['circulatoryStatus'],
    queryFn: () => circulatoryApi.status(),
  })

  const status = data?.data

  if (isLoading) return <DetailLoading />

  // Count route stats
  const routes = status?.routes ? Object.entries(status.routes) : []
  const healthyRoutes = routes.filter(([_, r]: [string, any]) => r?.is_healthy).length
  const congestedRoutes = routes.filter(([_, r]: [string, any]) => r?.status === 'congested').length

  return (
    <div className="space-y-4">
      {/* Flow Status Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              status?.is_flowing ? 'text-green-400' : 'text-red-400'
            )}>
              {status?.is_flowing ? 'FLOWING' : 'BLOCKED'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.overall_score || 0) >= 80 ? 'text-green-400' :
              (status?.overall_score || 0) >= 60 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.overall_score?.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Health Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {healthyRoutes}/{routes.length}
            </div>
            <div className="text-xs text-zinc-500">Routes Healthy</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              congestedRoutes > 0 ? 'text-yellow-400' : 'text-green-400'
            )}>
              {congestedRoutes}
            </div>
            <div className="text-xs text-zinc-500">Congested</div>
          </div>
        </div>
      </div>

      {/* All Routes - Full Details */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <GitBranch className="w-4 h-4" />
          All Data Routes ({routes.length})
        </h3>
        <div className="space-y-2">
          {routes.map(([name, route]: [string, any]) => (
            <div
              key={name}
              className={cn(
                'p-3 rounded-lg border',
                route?.status === 'congested' ? 'bg-yellow-500/5 border-yellow-500/30' :
                !route?.is_healthy ? 'bg-red-500/5 border-red-500/30' :
                'bg-zinc-900/50 border-zinc-700/50'
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-zinc-300">{route?.display_name || name}</span>
                <span className={cn(
                  'px-2 py-0.5 rounded text-xs font-medium capitalize',
                  route?.status === 'flowing' ? 'bg-green-500/20 text-green-400' :
                  route?.status === 'congested' ? 'bg-yellow-500/20 text-yellow-400' :
                  route?.status === 'slow' ? 'bg-orange-500/20 text-orange-400' :
                  'bg-red-500/20 text-red-400'
                )}>
                  {route?.status || 'unknown'}
                </span>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div>
                  <span className="text-zinc-500">Depth:</span>
                  <span className={cn(
                    'ml-1 font-medium',
                    (route?.current_depth || 0) > 100 ? 'text-yellow-400' : 'text-zinc-300'
                  )}>
                    {route?.current_depth?.toLocaleString() || 0}
                  </span>
                </div>
                <div>
                  <span className="text-zinc-500">Health:</span>
                  <span className={cn(
                    'ml-1 font-medium',
                    (route?.health_score || 0) >= 80 ? 'text-green-400' :
                    (route?.health_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
                  )}>
                    {route?.health_score?.toFixed(0) || 0}%
                  </span>
                </div>
                <div>
                  <span className="text-zinc-500">Throughput:</span>
                  <span className="ml-1 text-zinc-300">{route?.throughput?.toFixed(1) || 0}/s</span>
                </div>
                <div>
                  <span className="text-zinc-500">Latency:</span>
                  <span className={cn(
                    'ml-1 font-medium',
                    (route?.latency_ms || 0) > 100 ? 'text-yellow-400' : 'text-zinc-300'
                  )}>
                    {route?.latency_ms?.toFixed(2) || 0}ms
                  </span>
                </div>
              </div>
            </div>
          ))}
          {routes.length === 0 && (
            <p className="text-sm text-zinc-500">No routes configured</p>
          )}
        </div>
      </div>
    </div>
  )
}

// SPINE Detail View
function SpineDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['spineStatus'],
    queryFn: () => spineApi.status(),
  })

  const status = data?.data

  if (isLoading) return <DetailLoading />

  const categories = status?.category_health ? Object.entries(status.category_health) : []

  return (
    <div className="space-y-4">
      {/* Alignment Status Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              status?.is_aligned ? 'text-green-400' : 'text-red-400'
            )}>
              {status?.is_aligned ? 'ALIGNED' : 'MISALIGNED'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.health_score || 0) >= 80 ? 'text-green-400' :
              (status?.health_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.health_score?.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Health Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {status?.healthy_patterns || 0}/{status?.total_patterns || 0}
            </div>
            <div className="text-xs text-zinc-500">Patterns OK</div>
          </div>
        </div>
      </div>

      {/* Route Status */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">Route Status</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className={cn(
              'text-xl font-bold',
              (status?.routes_blocked || 0) > 0 ? 'text-red-400' : 'text-green-400'
            )}>
              {status?.routes_blocked || 0}
            </div>
            <div className="text-xs text-zinc-500">Blocked</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className={cn(
              'text-xl font-bold',
              (status?.routes_rate_limited || 0) > 0 ? 'text-yellow-400' : 'text-green-400'
            )}>
              {status?.routes_rate_limited || 0}
            </div>
            <div className="text-xs text-zinc-500">Rate Limited</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className={cn(
              'text-xl font-bold',
              (status?.fallbacks_active || 0) > 0 ? 'text-orange-400' : 'text-green-400'
            )}>
              {status?.fallbacks_active || 0}
            </div>
            <div className="text-xs text-zinc-500">Fallbacks Active</div>
          </div>
        </div>
      </div>

      {/* Pattern Status */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">Pattern Health</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xl font-bold text-gray-300">{status?.total_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Total</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-green-400">{status?.healthy_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Healthy</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-yellow-400">{status?.degraded_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Degraded</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-red-400">{status?.failed_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Failed</div>
          </div>
        </div>
      </div>

      {/* Category Health */}
      {categories.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Category Health ({categories.length})</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            {categories.map(([name, cat]: [string, any]) => (
              <div key={name} className="bg-zinc-900/50 rounded-lg p-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-zinc-400 capitalize">{name}</span>
                  <span className={cn(
                    'text-xs font-medium',
                    (cat?.health_score || 0) >= 80 ? 'text-green-400' :
                    (cat?.health_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
                  )}>
                    {cat?.health_score?.toFixed(0) || 0}%
                  </span>
                </div>
                <div className="text-xs text-zinc-500 mt-1">
                  {cat?.pattern_count || 0} patterns
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Integration Status */}
      {status?.integrations && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Body Integrations</h3>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(status.integrations).map(([name, state]) => (
              <div key={name} className="bg-zinc-900/50 rounded-lg p-3 text-center">
                <div className={cn(
                  'text-sm font-medium capitalize',
                  state === 'connected' || state === 'healthy' || state === 'flowing' || state === 'normal'
                    ? 'text-green-400' : 'text-red-400'
                )}>
                  {String(state)}
                </div>
                <div className="text-xs text-zinc-500 capitalize mt-1">{name}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// IMMUNE Detail View
function ImmuneDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['immuneStatus'],
    queryFn: () => immuneApi.status(),
  })

  const status = data?.data

  if (isLoading) return <DetailLoading />

  const threatCategories = status?.threats_by_category ? Object.entries(status.threats_by_category) : []
  const threatSeverities = status?.threats_by_severity ? Object.entries(status.threats_by_severity) : []

  return (
    <div className="space-y-4">
      {/* Threat Level Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold uppercase',
              status?.threat_level === 'none' ? 'text-green-400' :
              status?.threat_level === 'low' ? 'text-blue-400' :
              status?.threat_level === 'elevated' ? 'text-yellow-400' :
              status?.threat_level === 'high' ? 'text-orange-400' : 'text-red-400'
            )}>
              {status?.threat_level || 'unknown'}
            </div>
            <div className="text-xs text-zinc-500">Threat Level</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.health_score || 0) >= 80 ? 'text-green-400' :
              (status?.health_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.health_score?.toFixed(0) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Health Score</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.active_threats || 0) > 0 ? 'text-red-400' : 'text-green-400'
            )}>
              {status?.active_threats || 0}
            </div>
            <div className="text-xs text-zinc-500">Active Threats</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.threats_detected_24h || 0) > 0 ? 'text-yellow-400' : 'text-green-400'
            )}>
              {status?.threats_detected_24h || 0}
            </div>
            <div className="text-xs text-zinc-500">Threats (24h)</div>
          </div>
        </div>
      </div>

      {/* Defense Patterns */}
      {status?.patterns && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Defense Patterns
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-blue-400">{status.patterns.active || 0}</div>
              <div className="text-xs text-zinc-500">Active Patterns</div>
            </div>
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className={cn(
                'text-xl font-bold',
                (status.patterns.triggered_24h || 0) > 0 ? 'text-yellow-400' : 'text-green-400'
              )}>
                {status.patterns.triggered_24h || 0}
              </div>
              <div className="text-xs text-zinc-500">Triggered (24h)</div>
            </div>
          </div>
        </div>
      )}

      {/* Quarantine */}
      {status?.quarantine && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Quarantine Status</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className={cn(
                'text-xl font-bold',
                (status.quarantine.total || 0) > 0 ? 'text-orange-400' : 'text-green-400'
              )}>
                {status.quarantine.total || 0}
              </div>
              <div className="text-xs text-zinc-500">Total</div>
            </div>
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className={cn(
                'text-xl font-bold',
                (status.quarantine.ips || 0) > 0 ? 'text-red-400' : 'text-green-400'
              )}>
                {status.quarantine.ips || 0}
              </div>
              <div className="text-xs text-zinc-500">Blocked IPs</div>
            </div>
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className={cn(
                'text-xl font-bold',
                (status.quarantine.users || 0) > 0 ? 'text-purple-400' : 'text-green-400'
              )}>
                {status.quarantine.users || 0}
              </div>
              <div className="text-xs text-zinc-500">Blocked Users</div>
            </div>
          </div>
        </div>
      )}

      {/* Threats by Category */}
      {threatCategories.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Threats by Category</h3>
          <div className="space-y-2">
            {threatCategories.map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <span className="text-sm text-zinc-400 capitalize">{category.replace('_', ' ')}</span>
                <span className="text-sm font-medium text-red-400">{String(count)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Threats by Severity */}
      {threatSeverities.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Threats by Severity</h3>
          <div className="grid grid-cols-4 gap-2">
            {threatSeverities.map(([severity, count]) => (
              <div key={severity} className="bg-zinc-900/50 rounded-lg p-2 text-center">
                <div className={cn(
                  'text-lg font-bold',
                  severity === 'critical' ? 'text-red-400' :
                  severity === 'high' ? 'text-orange-400' :
                  severity === 'medium' ? 'text-yellow-400' : 'text-blue-400'
                )}>
                  {String(count)}
                </div>
                <div className="text-xs text-zinc-500 capitalize">{severity}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// DIGESTIVE Detail View
function DigestiveDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['digestiveStatus'],
    queryFn: () => digestiveApi.status(),
  })

  const status = data?.data

  if (isLoading) return <DetailLoading />

  const bottlenecks = status?.bottlenecks || []

  return (
    <div className="space-y-4">
      {/* Digestion Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold uppercase',
              status?.overall_status === 'healthy' ? 'text-green-400' :
              status?.overall_status === 'sluggish' ? 'text-yellow-400' :
              status?.overall_status === 'bloated' ? 'text-orange-400' : 'text-red-400'
            )}>
              {status?.overall_status || 'unknown'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.digestion_score || 0) >= 80 ? 'text-green-400' :
              (status?.digestion_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.digestion_score?.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Efficiency</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              status?.is_digesting ? 'text-green-400' : 'text-yellow-400'
            )}>
              {status?.is_digesting ? 'ACTIVE' : 'IDLE'}
            </div>
            <div className="text-xs text-zinc-500">Processing</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.items_pending || 0) > 100 ? 'text-red-400' :
              (status?.items_pending || 0) > 0 ? 'text-yellow-400' : 'text-green-400'
            )}>
              {status?.items_pending || 0}
            </div>
            <div className="text-xs text-zinc-500">Pending</div>
          </div>
        </div>
      </div>

      {/* Pipeline Stages */}
      {status?.stages && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Pipeline Stages</h3>
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(status.stages).map(([stage, state]) => (
              <div key={stage} className="bg-zinc-900/50 rounded-lg p-3 text-center">
                <div className={cn(
                  'text-sm font-medium capitalize',
                  state === 'healthy' || state === 'active' ? 'text-green-400' :
                  state === 'sluggish' || state === 'slow' || state === 'idle' ? 'text-yellow-400' : 'text-red-400'
                )}>
                  {String(state)}
                </div>
                <div className="text-xs text-zinc-500 capitalize mt-1">{stage}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metabolism */}
      {status?.metabolism && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Metabolism Rates
          </h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-blue-400">
                {typeof status.metabolism.intake_rate === 'number'
                  ? status.metabolism.intake_rate.toFixed(1)
                  : 0}/min
              </div>
              <div className="text-xs text-zinc-500">Intake</div>
            </div>
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-orange-400">
                {typeof status.metabolism.processing_rate === 'number'
                  ? status.metabolism.processing_rate.toFixed(1)
                  : 0}/min
              </div>
              <div className="text-xs text-zinc-500">Processing</div>
            </div>
            <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-green-400">
                {typeof status.metabolism.output_rate === 'number'
                  ? status.metabolism.output_rate.toFixed(1)
                  : 0}/min
              </div>
              <div className="text-xs text-zinc-500">Output</div>
            </div>
          </div>
        </div>
      )}

      {/* Bottlenecks */}
      {bottlenecks.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            Bottlenecks Detected ({bottlenecks.length})
          </h3>
          <div className="space-y-2">
            {bottlenecks.map((bottleneck: any, idx: number) => (
              <div
                key={idx}
                className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-yellow-400">
                    {bottleneck.stage || bottleneck.name || `Bottleneck ${idx + 1}`}
                  </span>
                  {bottleneck.severity && (
                    <span className={cn(
                      'px-2 py-0.5 rounded text-xs',
                      bottleneck.severity === 'high' ? 'bg-red-500/20 text-red-400' :
                      bottleneck.severity === 'medium' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    )}>
                      {bottleneck.severity}
                    </span>
                  )}
                </div>
                {bottleneck.message && (
                  <p className="text-xs text-zinc-400 mt-1">{bottleneck.message}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// MUSCULAR Detail View
function MuscularDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['muscularStatus'],
    queryFn: () => muscularApi.status(),
  })

  const status = data?.data

  if (isLoading) return <DetailLoading />

  const weakMuscles = status?.weak_muscles || []
  const overworkedMuscles = status?.overworked_muscles || []

  return (
    <div className="space-y-4">
      {/* Strength Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold uppercase',
              status?.overall_status === 'strong' ? 'text-green-400' :
              status?.overall_status === 'fit' ? 'text-blue-400' :
              status?.overall_status === 'fatigued' ? 'text-yellow-400' :
              status?.overall_status === 'strained' ? 'text-orange-400' : 'text-red-400'
            )}>
              {status?.overall_status || 'unknown'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.strength_score || 0) >= 80 ? 'text-green-400' :
              (status?.strength_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.strength_score?.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Strength</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.success_rate_24h || 0) >= 90 ? 'text-green-400' :
              (status?.success_rate_24h || 0) >= 70 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.success_rate_24h?.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {status?.total_executions_24h?.toLocaleString() || 0}
            </div>
            <div className="text-xs text-zinc-500">Executions (24h)</div>
          </div>
        </div>
      </div>

      {/* Agent Stats */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Users className="w-4 h-4" />
          Agent Statistics
        </h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-zinc-300">{status?.total_agents || 0}</div>
            <div className="text-xs text-zinc-500">Total</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-green-400">{status?.active_agents || 0}</div>
            <div className="text-xs text-zinc-500">Active</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className={cn(
              'text-xl font-bold',
              (status?.fatigued_agents || 0) > 0 ? 'text-yellow-400' : 'text-green-400'
            )}>
              {status?.fatigued_agents || 0}
            </div>
            <div className="text-xs text-zinc-500">Fatigued</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className={cn(
              'text-xl font-bold',
              (status?.strained_agents || 0) > 0 ? 'text-red-400' : 'text-green-400'
            )}>
              {status?.strained_agents || 0}
            </div>
            <div className="text-xs text-zinc-500">Strained</div>
          </div>
        </div>
      </div>

      {/* Weak Muscles */}
      {weakMuscles.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            Weak Muscles ({weakMuscles.length})
          </h3>
          <div className="space-y-2">
            {weakMuscles.map((muscle: any, idx: number) => (
              <div
                key={idx}
                className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-yellow-400">
                    {muscle.agent || muscle.name || `Agent ${idx + 1}`}
                  </span>
                  {muscle.success_rate !== undefined && (
                    <span className="text-xs text-zinc-400">
                      {muscle.success_rate?.toFixed(1)}% success rate
                    </span>
                  )}
                </div>
                {muscle.issue && (
                  <p className="text-xs text-zinc-400 mt-1">{muscle.issue}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Overworked Muscles */}
      {overworkedMuscles.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-orange-400" />
            Overworked Muscles ({overworkedMuscles.length})
          </h3>
          <div className="space-y-2">
            {overworkedMuscles.map((muscle: any, idx: number) => (
              <div
                key={idx}
                className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-orange-400">
                    {muscle.agent || muscle.name || `Agent ${idx + 1}`}
                  </span>
                  {muscle.executions_24h !== undefined && (
                    <span className="text-xs text-zinc-400">
                      {muscle.executions_24h?.toLocaleString()} executions
                    </span>
                  )}
                </div>
                {muscle.issue && (
                  <p className="text-xs text-zinc-400 mt-1">{muscle.issue}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Good Message */}
      {weakMuscles.length === 0 && overworkedMuscles.length === 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4 text-center">
          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
          <p className="text-sm text-zinc-400">All agents performing well</p>
          <p className="text-xs text-zinc-500">No weak or overworked muscles detected</p>
        </div>
      )}
    </div>
  )
}

// BRAIN Detail View - Session 722
function BrainDetailView() {
  const { data, isLoading } = useQuery({
    queryKey: ['brainStatus'],
    queryFn: () => brainApi.status(),
  })

  const status = data?.data

  if (isLoading) return <DetailLoading />

  return (
    <div className="space-y-4">
      {/* Cognitive Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold uppercase',
              status?.overall_status === 'focused' ? 'text-green-400' :
              status?.overall_status === 'thinking' ? 'text-cyan-400' :
              status?.overall_status === 'resting' ? 'text-blue-400' :
              status?.overall_status === 'foggy' ? 'text-yellow-400' :
              status?.overall_status === 'overloaded' ? 'text-orange-400' : 'text-red-400'
            )}>
              {status?.overall_status || 'unknown'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              (status?.cognitive_score || 0) >= 80 ? 'text-green-400' :
              (status?.cognitive_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {status?.cognitive_score?.toFixed(1) || 0}%
            </div>
            <div className="text-xs text-zinc-500">Cognitive Score</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-2xl font-bold',
              status?.is_thinking ? 'text-cyan-400' : 'text-zinc-400'
            )}>
              {status?.is_thinking ? 'ACTIVE' : 'IDLE'}
            </div>
            <div className="text-xs text-zinc-500">Processing</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">
              {status?.active_conversations || 0}
            </div>
            <div className="text-xs text-zinc-500">Active Conversations</div>
          </div>
        </div>
      </div>

      {/* LLM Metrics */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-yellow-400" />
          LLM Activity (24h)
        </h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-blue-400">
              {status?.llm_calls_24h?.toLocaleString() || 0}
            </div>
            <div className="text-xs text-zinc-500">LLM Calls</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-cyan-400">
              {status?.tokens_total_24h?.toLocaleString() || 0}
            </div>
            <div className="text-xs text-zinc-500">Tokens Used</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-green-400">
              ${status?.cost_24h?.toFixed(2) || '0.00'}
            </div>
            <div className="text-xs text-zinc-500">Cost</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className={cn(
              'text-xl font-bold',
              (status?.avg_response_time_ms || 0) > 5000 ? 'text-yellow-400' : 'text-green-400'
            )}>
              {status?.avg_response_time_ms?.toLocaleString() || 0}ms
            </div>
            <div className="text-xs text-zinc-500">Avg Response</div>
          </div>
        </div>
      </div>

      {/* Agent Processing */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-purple-400" />
          Agent Activity
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-purple-400">
              {status?.agent_executions_24h?.toLocaleString() || 0}
            </div>
            <div className="text-xs text-zinc-500">Agent Executions (24h)</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-orange-400">
              {status?.rag_queries_24h || 0}
            </div>
            <div className="text-xs text-zinc-500">RAG Queries</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-3 text-center">
            <div className="text-xl font-bold text-pink-400">
              {status?.reasoning_chains_24h || 0}
            </div>
            <div className="text-xs text-zinc-500">Reasoning Chains</div>
          </div>
        </div>
      </div>

      {/* Cognitive Channels */}
      {status?.cognitive_channels && Object.keys(status.cognitive_channels).length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <Brain className="w-4 h-4 text-cyan-400" />
            Cognitive Channels
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {Object.entries(status.cognitive_channels).map(([name, channel]: [string, any]) => (
              <div key={name} className="bg-zinc-900/50 rounded-lg p-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-zinc-400 capitalize">{name.replace('_', ' ')}</span>
                  <span className={cn(
                    'px-1.5 py-0.5 rounded text-xs',
                    channel?.is_active ? 'bg-green-500/20 text-green-400' : 'bg-zinc-700 text-zinc-500'
                  )}>
                    {channel?.is_active ? 'Active' : 'Idle'}
                  </span>
                </div>
                <div className="text-xs text-zinc-500 mt-1">
                  {channel?.calls_24h || 0} calls • {channel?.tokens_24h?.toLocaleString() || 0} tokens
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Brain Status - All Good */}
      {(status?.cognitive_score || 0) >= 70 && (
        <div className="bg-zinc-800/50 rounded-lg p-4 text-center">
          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
          <p className="text-sm text-zinc-400">Brain processing normally</p>
          <p className="text-xs text-zinc-500">Cognitive functions optimal</p>
        </div>
      )}
    </div>
  )
}

// SKIN Detail View - Session 723 (Enhanced)
function SkinDetailView() {
  const [selectedWorkspace, setSelectedWorkspace] = useState<string | null>(null)

  // Use feel() for full data instead of status()
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['skinFeel'],
    queryFn: () => skinApi.feel(),
    refetchInterval: 60000, // Refresh every minute
  })

  const { data: workspacesData } = useQuery({
    queryKey: ['skinWorkspaces'],
    queryFn: () => skinApi.workspaces(),
  })

  const skin = data?.data
  const workspaces = workspacesData?.data?.workspaces || []
  const selectedWs = workspaces.find((w: any) => w.id === selectedWorkspace)

  if (isLoading) return <DetailLoading />

  // Helper to format bytes
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  // Helper for activity level color
  const getActivityColor = (level: string) => {
    switch (level) {
      case 'dormant': return 'text-gray-500'
      case 'low': return 'text-blue-400'
      case 'normal': return 'text-green-400'
      case 'high': return 'text-yellow-400'
      case 'intense': return 'text-red-400'
      default: return 'text-zinc-400'
    }
  }

  return (
    <div className="space-y-4">
      {/* Skin Health Summary */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-zinc-300">Skin Health Overview</h3>
          <button
            onClick={() => refetch()}
            className="text-xs text-zinc-500 hover:text-zinc-300 flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Refresh
          </button>
        </div>
        <div className="grid grid-cols-5 gap-3">
          <div className="text-center">
            <div className={cn(
              'text-xl font-bold uppercase',
              skin?.status === 'healthy' ? 'text-green-400' :
              skin?.status === 'active' ? 'text-green-400' :
              skin?.status === 'sweating' ? 'text-yellow-400' :
              skin?.status === 'irritated' ? 'text-orange-400' :
              skin?.status === 'healing' ? 'text-blue-400' :
              skin?.status === 'dormant' ? 'text-gray-400' : 'text-red-400'
            )}>
              {skin?.status || 'unknown'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className={cn(
              'text-xl font-bold',
              (skin?.health_score || 0) >= 80 ? 'text-green-400' :
              (skin?.health_score || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {skin?.health_score || 0}%
            </div>
            <div className="text-xs text-zinc-500">Health</div>
          </div>
          <div className="text-center">
            <div className={cn('text-xl font-bold', getActivityColor(skin?.activity?.level))}>
              {skin?.activity?.level?.toUpperCase() || 'N/A'}
            </div>
            <div className="text-xs text-zinc-500">Activity</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-amber-400">
              {skin?.workspaces?.active || 0}/{skin?.workspaces?.total || 0}
            </div>
            <div className="text-xs text-zinc-500">Workspaces</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-cyan-400">
              {skin?.check_duration_ms || 0}ms
            </div>
            <div className="text-xs text-zinc-500">Check Time</div>
          </div>
        </div>
      </div>

      {/* File Operations (24h) - Full Breakdown */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <FileEdit className="w-4 h-4 text-amber-400" />
          Workspace Operations (24h)
          <span className="text-xs text-zinc-600 font-normal ml-2">
            — file writes, shell commands, and git operations by agents
          </span>
        </h3>
        <div className="grid grid-cols-6 gap-2">
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Total workspace operations in the last 24 hours">
            <div className="text-lg font-bold text-blue-400">
              {skin?.operations_24h?.total || 0}
            </div>
            <div className="text-xs text-zinc-500">Total Ops</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="New files created by agents">
            <div className="text-lg font-bold text-green-400">
              {skin?.file_activity_24h?.created || 0}
            </div>
            <div className="text-xs text-zinc-500">Files Created</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Existing files modified by agents">
            <div className="text-lg font-bold text-cyan-400">
              {skin?.file_activity_24h?.modified || 0}
            </div>
            <div className="text-xs text-zinc-500">Files Modified</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Files deleted by agents">
            <div className="text-lg font-bold text-red-400">
              {skin?.file_activity_24h?.deleted || 0}
            </div>
            <div className="text-xs text-zinc-500">Files Deleted</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Shell commands executed by agents (npm, pip, etc.)">
            <div className="text-lg font-bold text-purple-400">
              {skin?.file_activity_24h?.commands || 0}
            </div>
            <div className="text-xs text-zinc-500">Shell Cmds</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Git operations (commit, push, pull, etc.)">
            <div className="text-lg font-bold text-orange-400">
              {skin?.file_activity_24h?.git_ops || 0}
            </div>
            <div className="text-xs text-zinc-500">Git Ops</div>
          </div>
        </div>
        {/* Metrics row */}
        <div className="grid grid-cols-4 gap-2 mt-2">
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Percentage of operations that completed successfully">
            <div className={cn(
              'text-lg font-bold',
              (skin?.operations_24h?.success_rate || 100) >= 90 ? 'text-green-400' :
              (skin?.operations_24h?.success_rate || 100) >= 70 ? 'text-yellow-400' : 'text-red-400'
            )}>
              {skin?.operations_24h?.success_rate || 100}%
            </div>
            <div className="text-xs text-zinc-500">Success Rate</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Total lines of code added, removed, or modified">
            <div className="text-lg font-bold text-pink-400">
              {skin?.file_activity_24h?.lines_changed?.toLocaleString() || 0}
            </div>
            <div className="text-xs text-zinc-500">Lines Changed</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Total bytes written to files">
            <div className="text-lg font-bold text-teal-400">
              {formatBytes(skin?.file_activity_24h?.bytes_written || 0)}
            </div>
            <div className="text-xs text-zinc-500">Data Written</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Average time to complete a workspace operation">
            <div className="text-lg font-bold text-indigo-400">
              {skin?.activity?.avg_op_time_ms || 0}ms
            </div>
            <div className="text-xs text-zinc-500">Avg Op Time</div>
          </div>
        </div>
      </div>

      {/* Agent Activity */}
      {skin?.agents && Object.keys(skin.agents.operation_counts || {}).length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-purple-400" />
            Agent Workspace Operations ({skin.agents.active_count} agents active in 24h)
          </h3>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs text-zinc-500">Most Active:</span>
            <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded text-xs font-medium">
              {skin.agents.most_active || 'None'}
            </span>
            <span className="text-xs text-zinc-600">
              (file writes, commands, git operations)
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {Object.entries(skin.agents.operation_counts || {}).map(([agent, count]) => (
              <div
                key={agent}
                className="bg-zinc-900/50 border border-zinc-700/50 rounded-lg p-2 flex items-center justify-between"
                title={`${agent} performed ${count} workspace operations in the last 24 hours`}
              >
                <span className="text-xs text-zinc-400 truncate flex-1">{agent}</span>
                <span className="text-sm font-bold text-zinc-300 ml-2">{count as number} <span className="text-xs text-zinc-500 font-normal">ops</span></span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rollback & Recovery */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <RefreshCw className="w-4 h-4 text-purple-400" />
          Healing & Recovery
        </h3>
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="File snapshots that can be restored to previous state">
            <div className="text-lg font-bold text-purple-400">
              {skin?.healing?.rollbacks_available || 0}
            </div>
            <div className="text-xs text-zinc-500">Snapshots Available</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Number of rollbacks performed in the last 24 hours">
            <div className={cn(
              'text-lg font-bold',
              (skin?.healing?.rollbacks_performed_24h || 0) > 0 ? 'text-blue-400' : 'text-zinc-500'
            )}>
              {skin?.healing?.rollbacks_performed_24h || 0}
            </div>
            <div className="text-xs text-zinc-500">Rollbacks (24h)</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Operations requiring human approval before execution">
            <div className={cn(
              'text-lg font-bold',
              (skin?.healing?.pending_reviews || 0) > 0 ? 'text-yellow-400' : 'text-green-400'
            )}>
              {skin?.healing?.pending_reviews || 0}
            </div>
            <div className="text-xs text-zinc-500">Pending Reviews</div>
          </div>
          <div className="bg-zinc-900/50 rounded-lg p-2 text-center" title="Operations blocked due to permission errors">
            <div className={cn(
              'text-lg font-bold',
              (skin?.issues?.permission_denials || 0) > 0 ? 'text-red-400' : 'text-green-400'
            )}>
              {skin?.issues?.permission_denials || 0}
            </div>
            <div className="text-xs text-zinc-500">Permission Denials</div>
          </div>
        </div>
      </div>

      {/* Workspace Selector */}
      {workspaces.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-zinc-300 flex items-center gap-2">
              <FolderOpen className="w-4 h-4 text-amber-400" />
              Workspaces ({workspaces.length})
            </h3>
            <select
              value={selectedWorkspace || ''}
              onChange={(e) => setSelectedWorkspace(e.target.value || null)}
              className="bg-zinc-900 border border-zinc-700 rounded px-2 py-1 text-xs text-zinc-300 focus:outline-none focus:ring-1 focus:ring-amber-500"
            >
              <option value="">All Workspaces</option>
              {workspaces.map((ws: any) => (
                <option key={ws.id} value={ws.id}>
                  {ws.name} {ws.is_active ? '(Active)' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Selected Workspace Details */}
          {selectedWs ? (
            <div className="bg-zinc-900/50 border border-amber-500/30 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="text-sm font-medium text-zinc-200">{selectedWs.name}</h4>
                  <p className="text-xs text-zinc-500 truncate max-w-md">{selectedWs.root_path}</p>
                </div>
                <span className={cn(
                  'px-2 py-1 rounded text-xs font-medium',
                  selectedWs.is_active ? 'bg-green-500/20 text-green-400' : 'bg-zinc-700 text-zinc-500'
                )}>
                  {selectedWs.workspace_type || 'local'}
                </span>
              </div>
              <div className="grid grid-cols-4 gap-3">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-400">{selectedWs.operations_24h || 0}</div>
                  <div className="text-xs text-zinc-500">Ops (24h)</div>
                </div>
                <div className="text-center">
                  <div className={cn(
                    'text-lg font-bold',
                    (selectedWs.success_rate_24h || 100) >= 90 ? 'text-green-400' : 'text-yellow-400'
                  )}>
                    {selectedWs.success_rate_24h || 100}%
                  </div>
                  <div className="text-xs text-zinc-500">Success</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-400">{selectedWs.total_operations || 0}</div>
                  <div className="text-xs text-zinc-500">Total Ops</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-zinc-400">
                    {selectedWs.last_operation
                      ? new Date(selectedWs.last_operation).toLocaleDateString()
                      : 'Never'}
                  </div>
                  <div className="text-xs text-zinc-500">Last Op</div>
                </div>
              </div>
            </div>
          ) : (
            /* All Workspaces List */
            <div className="space-y-2">
              {workspaces.map((workspace: any) => (
                <div
                  key={workspace.id}
                  onClick={() => setSelectedWorkspace(workspace.id)}
                  className="bg-zinc-900/50 border border-zinc-700/50 rounded-lg p-3 cursor-pointer hover:border-amber-500/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-zinc-300">{workspace.name}</span>
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        'text-xs font-medium',
                        (workspace.success_rate_24h || 100) >= 90 ? 'text-green-400' : 'text-yellow-400'
                      )}>
                        {workspace.success_rate_24h || 100}%
                      </span>
                      <span className={cn(
                        'px-2 py-0.5 rounded text-xs font-medium',
                        workspace.is_active ? 'bg-green-500/20 text-green-400' : 'bg-zinc-700 text-zinc-500'
                      )}>
                        {workspace.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-xs">
                    <div>
                      <span className="text-zinc-500">Ops 24h:</span>
                      <span className="ml-1 text-zinc-300">{workspace.operations_24h || 0}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Total:</span>
                      <span className="ml-1 text-zinc-300">{workspace.total_operations || 0}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Type:</span>
                      <span className="ml-1 text-zinc-300">{workspace.workspace_type || 'local'}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Last:</span>
                      <span className="ml-1 text-zinc-300">
                        {workspace.last_operation
                          ? new Date(workspace.last_operation).toLocaleDateString()
                          : 'Never'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Recent Errors */}
      {skin?.issues?.recent_errors && skin.issues.recent_errors.length > 0 && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-red-400 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Recent Errors ({skin.issues.recent_errors.length})
          </h3>
          <div className="space-y-2">
            {skin.issues.recent_errors.map((error: any, i: number) => (
              <div key={i} className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-red-400">{error.operation_type}</span>
                  <span className="text-xs text-zinc-500">
                    {error.created_at ? new Date(error.created_at).toLocaleString() : 'Unknown'}
                  </span>
                </div>
                <p className="text-xs text-zinc-400 truncate">{error.file_path}</p>
                <p className="text-xs text-red-300 mt-1">{error.error_message || 'Unknown error'}</p>
                <p className="text-xs text-zinc-500 mt-1">Agent: {error.agent_name || 'Unknown'}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skin Status - All Good */}
      {(skin?.health_score || 0) >= 70 && (!skin?.issues?.recent_errors || skin.issues.recent_errors.length === 0) && (
        <div className="bg-zinc-800/50 rounded-lg p-4 text-center">
          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
          <p className="text-sm text-zinc-400">Skin functioning normally</p>
          <p className="text-xs text-zinc-500">
            {skin?.agents?.active_count || 0} agents working across {skin?.workspaces?.active || 0} workspaces
          </p>
        </div>
      )}
    </div>
  )
}

// ============================================================================
// NERVOUS System Detail View - WebSocket Communication Monitoring
// ============================================================================

function NervousDetailView() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['nervousFeel'],
    queryFn: () => nervousApi.feel(),
    refetchInterval: 60000, // Refresh every 60 seconds
  })

  const nervous = data?.data

  if (isLoading) return <DetailLoading />
  if (error) {
    return (
      <div className="text-red-400 text-sm">
        Failed to load nervous data: {String(error)}
      </div>
    )
  }
  if (!nervous) return null

  const healthColor = (nervous.health_score || 0) >= 80 ? 'text-green-400' :
                     (nervous.health_score || 0) >= 60 ? 'text-cyan-400' :
                     (nervous.health_score || 0) >= 40 ? 'text-yellow-400' : 'text-red-400'

  const statusEmojiMap: Record<string, string> = {
    responsive: '⚡',
    active: '🔌',
    sluggish: '🐌',
    numb: '❄️',
    overloaded: '🔥',
    damaged: '💔',
    dormant: '💤',
  }
  const statusEmoji = statusEmojiMap[nervous.status as string] || '❓'

  return (
    <div className="space-y-4">
      {/* Header with Health Score */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{statusEmoji}</span>
          <div>
            <div className={cn('text-2xl font-bold', healthColor)}>
              {(nervous.health_score || 0).toFixed(1)}%
            </div>
            <div className="text-xs text-zinc-500 capitalize">{nervous.status || 'unknown'}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-zinc-500">Check Duration</div>
          <div className="text-sm text-zinc-300">{nervous.check_duration_ms || 0}ms</div>
        </div>
      </div>

      {/* Channel Layer (Redis) Status */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Database className="w-4 h-4" />
          Channel Layer (Redis)
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className={cn(
              'text-xl font-bold',
              nervous.channel_layer?.connected ? 'text-green-400' : 'text-red-400'
            )}>
              {nervous.channel_layer?.connected ? 'Connected' : 'Disconnected'}
            </div>
            <div className="text-xs text-zinc-500">Status</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-cyan-400">
              {(nervous.channel_layer?.redis_ping_ms || 0).toFixed(2)}ms
            </div>
            <div className="text-xs text-zinc-500">Ping Latency</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-zinc-300">
              {nervous.channel_layer?.redis_clients || 0}
            </div>
            <div className="text-xs text-zinc-500">Redis Clients</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-zinc-300">
              {nervous.channel_layer?.host || 'localhost'}:{nervous.channel_layer?.port || 6379}
            </div>
            <div className="text-xs text-zinc-500">Host</div>
          </div>
        </div>
      </div>

      {/* Consumer Statistics */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4" />
          WebSocket Consumers
        </h4>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center bg-zinc-900/50 rounded p-3">
            <div className="text-2xl font-bold text-yellow-400">
              {nervous.consumers?.total_routes || 0}
            </div>
            <div className="text-xs text-zinc-500">Total Routes</div>
          </div>
          <div className="text-center bg-zinc-900/50 rounded p-3">
            <div className="text-2xl font-bold text-purple-400">
              {nervous.consumers?.unique_consumers || 0}
            </div>
            <div className="text-xs text-zinc-500">Unique Consumers</div>
          </div>
        </div>

        {/* Consumer Categories */}
        {nervous.consumers?.categories && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {Object.entries(nervous.consumers.categories).map(([category, consumers]) => {
              const count = Array.isArray(consumers) ? consumers.length : 0
              if (count === 0) return null
              return (
                <div key={category} className="bg-zinc-900/30 rounded p-2 text-center">
                  <div className="text-lg font-bold text-zinc-300">{count}</div>
                  <div className="text-xs text-zinc-500 capitalize">{category}</div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Connection & Message Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Connection Stats */}
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Connections
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Active</span>
              <span className="text-green-400 font-medium">
                {nervous.connections?.active || 0}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Total (24h)</span>
              <span className="text-zinc-300">
                {nervous.connections?.total_24h || 0}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Errors (24h)</span>
              <span className={cn(
                'font-medium',
                (nervous.connections?.errors_24h || 0) > 0 ? 'text-red-400' : 'text-zinc-300'
              )}>
                {nervous.connections?.errors_24h || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Message Stats */}
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Messages
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Per Second</span>
              <span className="text-cyan-400 font-medium">
                {(nervous.messages?.per_second || 0).toFixed(2)}/s
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Total (24h)</span>
              <span className="text-zinc-300">
                {(nervous.messages?.total_24h || 0).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Avg Latency</span>
              <span className="text-zinc-300">
                {(nervous.messages?.avg_latency_ms || 0).toFixed(2)}ms
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Activity Level */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-zinc-500">Activity Level</span>
          <span className={cn(
            'px-3 py-1 rounded-full text-sm font-medium capitalize',
            nervous.activity_level === 'high' ? 'bg-green-500/20 text-green-400' :
            nervous.activity_level === 'medium' ? 'bg-cyan-500/20 text-cyan-400' :
            nervous.activity_level === 'low' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-zinc-500/20 text-zinc-400'
          )}>
            {nervous.activity_level || 'unknown'}
          </span>
        </div>
      </div>

      {/* Issues */}
      {nervous.issues && nervous.issues.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <h4 className="text-sm font-medium text-red-400 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Issues Detected ({nervous.issues.length})
          </h4>
          <div className="space-y-2">
            {nervous.issues.map((issue: string, idx: number) => (
              <div key={idx} className="flex items-start gap-2 text-sm">
                <XCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                <span className="text-red-300">{issue}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nervous Status - All Good */}
      {(nervous.health_score || 0) >= 80 && (!nervous.issues || nervous.issues.length === 0) && (
        <div className="bg-zinc-800/50 rounded-lg p-4 text-center">
          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
          <p className="text-sm text-zinc-400">Nervous system responsive</p>
          <p className="text-xs text-zinc-500">
            {nervous.consumers?.unique_consumers || 0} consumers across {nervous.consumers?.total_routes || 0} routes
          </p>
        </div>
      )}
    </div>
  )
}

// Loading component for detail views
function DetailLoading() {
  return (
    <div className="flex items-center justify-center py-8">
      <RefreshCw className="w-6 h-6 animate-spin text-zinc-500" />
      <span className="ml-2 text-zinc-500">Loading details...</span>
    </div>
  )
}

// ============================================================================
// Coordination Panel - Shows Body Coordinator status
// ============================================================================

function CoordinationPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['bodyCoordination'],
    queryFn: () => bodyApi.coordination?.status?.() || Promise.resolve({ data: null }),
    enabled: !!bodyApi.coordination,
  })

  const { data: throttleData } = useQuery({
    queryKey: ['bodyThrottle'],
    queryFn: () => bodyApi.throttle?.() || Promise.resolve({ data: null }),
    enabled: !!bodyApi.throttle,
  })

  const status = data?.data
  const throttle = throttleData?.data

  // If coordination API not available, don't show panel
  if (!status && !isLoading) return null

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium text-zinc-300 flex items-center gap-2">
          <Zap className="w-5 h-5 text-cyan-500" />
          Body Coordination
        </h2>
        {throttle?.is_throttled && (
          <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 text-sm rounded-full">
            Throttled ({((throttle.throttle_factor || 1) * 100).toFixed(0)}% capacity)
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-cyan-400">{status?.events_detected || 0}</div>
          <div className="text-xs text-zinc-500">Events Detected</div>
        </div>
        <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-green-400">{status?.responses_triggered || 0}</div>
          <div className="text-xs text-zinc-500">Responses</div>
        </div>
        <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
          <div className={cn(
            'text-xl font-bold',
            throttle?.is_throttled ? 'text-yellow-400' : 'text-green-400'
          )}>
            {throttle?.is_throttled ? 'Yes' : 'No'}
          </div>
          <div className="text-xs text-zinc-500">Throttled</div>
        </div>
        <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-zinc-300">
            {((throttle?.throttle_factor || 1) * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-zinc-500">Capacity</div>
        </div>
      </div>

      {status?.last_coordination && (
        <p className="text-xs text-zinc-600 mt-4 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Last coordination: {new Date(status.last_coordination).toLocaleString()}
        </p>
      )}
    </div>
  )
}

// Main Page Component
export default function BodyHealthPage() {
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)

  // Fetch body vitals
  const { data: vitalsData, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['bodyVitals'],
    queryFn: () => bodyApi.vitals(true),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const vitals = vitalsData?.data as BodyVitals | undefined

  // Fetch alerts
  const { data: alertsData } = useQuery({
    queryKey: ['bodyAlerts'],
    queryFn: () => bodyApi.alerts('info', 20),
    refetchInterval: 30000,
  })

  const alerts = (alertsData?.data?.alerts || []) as BodyAlert[]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-zinc-500 mx-auto mb-2" />
          <p className="text-zinc-500">Loading body health...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Body Health Dashboard</h1>
          <p className="text-sm text-zinc-500">
            Real-time monitoring of all 9 body systems
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg',
            'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700',
            'text-sm text-zinc-300 transition-all',
            isFetching && 'opacity-50 cursor-not-allowed'
          )}
        >
          <RefreshCw className={cn('w-4 h-4', isFetching && 'animate-spin')} />
          Refresh
        </button>
      </div>

      {/* System Detail Panel - Shows when a system is selected */}
      {selectedSystem && (
        <SystemDetailPanel
          systemName={selectedSystem}
          onClose={() => setSelectedSystem(null)}
        />
      )}

      {/* Overall Health Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Health Score */}
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
          <h2 className="text-sm font-medium text-zinc-400 mb-4">Overall Health</h2>
          <HealthScoreGauge
            score={vitals?.health_score || 0}
            status={vitals?.overall_health || 'unknown'}
          />
        </div>

        {/* Quick Stats */}
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
          <h2 className="text-sm font-medium text-zinc-400 mb-4">System Status</h2>
          <div className="space-y-3">
            {vitals?.systems && Object.entries(vitals.systems).map(([name, sys]) => {
              const config = SYSTEM_CONFIG[name]
              const statusConfig = STATUS_CONFIG[sys.status] || STATUS_CONFIG.unknown
              return (
                <div key={name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{sys.emoji}</span>
                    <span className="text-sm text-zinc-400">{config?.label || name}</span>
                  </div>
                  <span className={cn('text-sm capitalize', statusConfig.color)}>
                    {sys.status}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Alerts Summary */}
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
          <h2 className="text-sm font-medium text-zinc-400 mb-4">Active Alerts</h2>
          <div className="space-y-2">
            {alerts.length === 0 ? (
              <div className="text-center py-4">
                <CheckCircle className="w-6 h-6 mx-auto mb-2 text-green-500" />
                <p className="text-sm text-zinc-500">All systems normal</p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-zinc-400">Critical</span>
                  <span className="text-red-500 font-medium">
                    {alerts.filter(a => a.severity === 'critical').length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-zinc-400">Warning</span>
                  <span className="text-yellow-500 font-medium">
                    {alerts.filter(a => a.severity === 'warning').length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-zinc-400">Info</span>
                  <span className="text-blue-500 font-medium">
                    {alerts.filter(a => a.severity === 'info').length}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Body Systems Grid */}
      <div>
        <h2 className="text-lg font-medium text-zinc-300 mb-4">Body Systems</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {vitals?.systems && Object.entries(vitals.systems).map(([name, sys]) => (
            <BodySystemCard
              key={name}
              systemName={name}
              vitals={sys}
              onClick={() => setSelectedSystem(selectedSystem === name ? null : name)}
            />
          ))}
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
          <h2 className="text-lg font-medium text-zinc-300 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            Alert Feed
          </h2>
          <BodyAlertsFeed alerts={alerts} />
        </div>

        {/* Recommendation */}
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
          <h2 className="text-lg font-medium text-zinc-300 mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-blue-500" />
            Recommendation
          </h2>
          {vitals?.recommendation ? (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <p className="text-sm text-zinc-300">{vitals.recommendation}</p>
            </div>
          ) : (
            <div className="text-center py-8 text-zinc-500">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <p>System operating optimally</p>
              <p className="text-xs">No recommendations at this time</p>
            </div>
          )}

          {/* Last Update */}
          <div className="mt-4 pt-4 border-t border-zinc-800">
            <p className="text-xs text-zinc-600 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Last updated: {vitals?.timestamp ? new Date(vitals.timestamp).toLocaleString() : 'Never'}
            </p>
          </div>
        </div>
      </div>

      {/* Human Body Metaphor Legend */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
        <h2 className="text-lg font-medium text-zinc-300 mb-4">Human Body Metaphor</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 text-sm">
          <div>
            <span className="text-red-500 font-medium">HEART</span>
            <p className="text-zinc-500">Core platform health - Redis, DB, Celery, Django</p>
          </div>
          <div>
            <span className="text-blue-500 font-medium">LUNGS</span>
            <p className="text-zinc-500">Resource/budget management - Token limits, API costs</p>
          </div>
          <div>
            <span className="text-pink-500 font-medium">CIRCULATORY</span>
            <p className="text-zinc-500">Data flow monitoring - WebSocket, queues, pipelines</p>
          </div>
          <div>
            <span className="text-gray-400 font-medium">SPINE</span>
            <p className="text-zinc-500">Central API routing - Request/response handling</p>
          </div>
          <div>
            <span className="text-green-500 font-medium">IMMUNE</span>
            <p className="text-zinc-500">Security & threats - Rate limits, blocked IPs</p>
          </div>
          <div>
            <span className="text-orange-500 font-medium">DIGESTIVE</span>
            <p className="text-zinc-500">Data ingestion - Spider data processing</p>
          </div>
          <div>
            <span className="text-purple-500 font-medium">MUSCULAR</span>
            <p className="text-zinc-500">Agent execution - Work output, success rates</p>
          </div>
          <div>
            <span className="text-cyan-500 font-medium">BRAIN</span>
            <p className="text-zinc-500">Cognitive processing - LLM calls, reasoning</p>
          </div>
          <div>
            <span className="text-amber-500 font-medium">SKIN</span>
            <p className="text-zinc-500">Workspace outputs - File writes, project changes</p>
          </div>
        </div>
      </div>

      {/* Body Coordination Panel - Session 711 */}
      <CoordinationPanel />
    </div>
  )
}
