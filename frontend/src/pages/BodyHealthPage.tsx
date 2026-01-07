/**
 * Session 710: Body Health Dashboard
 *
 * Unified view of all 7 body systems health status.
 * Provides real-time monitoring of the AI body's health.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  bodyApi, heartApi, lungsApi, circulatoryApi, spineApi,
  immuneApi, digestiveApi, muscularApi
} from '@/lib/api'
import {
  Heart, Wind, Droplets, Bone, Shield, Apple, Dumbbell,
  AlertTriangle, CheckCircle, XCircle, Activity, RefreshCw,
  Info, Clock, X, Zap, Server, Database, Cpu, DollarSign,
  Users, Lock, GitBranch, Gauge, BarChart3, Timer
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
      {/* Components Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {status?.components?.components && Object.entries(status.components.components).map(([name, comp]: [string, any]) => (
          <div key={name} className="bg-zinc-800/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              {name === 'brain' && <Cpu className="w-4 h-4 text-purple-400" />}
              {name === 'memory' && <Database className="w-4 h-4 text-blue-400" />}
              {name === 'nervous_system' && <Zap className="w-4 h-4 text-yellow-400" />}
              {name === 'organs' && <Users className="w-4 h-4 text-green-400" />}
              {name === 'sensory' && <Activity className="w-4 h-4 text-pink-400" />}
              {name === 'skin' && <Server className="w-4 h-4 text-cyan-400" />}
              {!['brain', 'memory', 'nervous_system', 'organs', 'sensory', 'skin'].includes(name) && <Activity className="w-4 h-4 text-zinc-400" />}
              <span className="text-sm font-medium text-zinc-300 capitalize">{name.replace('_', ' ')}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className={cn(
                'text-sm capitalize',
                comp?.status === 'healthy' || comp?.status === 'connected' ? 'text-green-500' :
                comp?.status === 'degraded' ? 'text-yellow-500' : 'text-red-500'
              )}>
                {comp?.status || 'unknown'}
              </span>
              {(comp?.response_time_ms !== undefined || comp?.latency_ms !== undefined) && (
                <span className="text-xs text-zinc-500">{comp.response_time_ms ?? comp.latency_ms}ms</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Health Score */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-zinc-400">Health Score</span>
          <span className={cn(
            'text-lg font-bold',
            (status?.health_score || 0) >= 80 ? 'text-green-500' :
            (status?.health_score || 0) >= 50 ? 'text-yellow-500' : 'text-red-500'
          )}>
            {status?.health_score?.toFixed(1) || 0}%
          </span>
        </div>
        <div className="mt-2 h-2 bg-zinc-700 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full',
              (status?.health_score || 0) >= 80 ? 'bg-green-500' :
              (status?.health_score || 0) >= 50 ? 'bg-yellow-500' : 'bg-red-500'
            )}
            style={{ width: `${status?.health_score || 0}%` }}
          />
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
      {/* Oxygen Levels */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Gauge className="w-4 h-4" />
          Oxygen Level (Budget)
        </h3>
        <div className="flex items-center gap-4">
          <div className="text-3xl font-bold text-blue-400">
            {status?.oxygen_level?.toFixed(1) || 0}%
          </div>
          <div className="flex-1">
            <div className="h-3 bg-zinc-700 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all',
                  (status?.oxygen_level || 0) >= 50 ? 'bg-blue-500' :
                  (status?.oxygen_level || 0) >= 20 ? 'bg-yellow-500' : 'bg-red-500'
                )}
                style={{ width: `${status?.oxygen_level || 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Budgets List */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <DollarSign className="w-4 h-4" />
          API Budgets
        </h3>
        <div className="space-y-3">
          {budgets.slice(0, 5).map((budget: any) => (
            <div key={budget.id || budget.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm text-zinc-300">{budget.name || budget.provider}</span>
                <span className="text-xs text-zinc-500">
                  ${budget.used?.toFixed(2) || 0} / ${budget.limit?.toFixed(2) || budget.daily_limit?.toFixed(2) || 0}
                </span>
              </div>
              <div className="w-24 h-2 bg-zinc-700 rounded-full overflow-hidden">
                <div
                  className={cn(
                    'h-full rounded-full',
                    ((budget.used || 0) / (budget.limit || budget.daily_limit || 1) * 100) < 50 ? 'bg-green-500' :
                    ((budget.used || 0) / (budget.limit || budget.daily_limit || 1) * 100) < 80 ? 'bg-yellow-500' : 'bg-red-500'
                  )}
                  style={{ width: `${Math.min(100, (budget.used || 0) / (budget.limit || budget.daily_limit || 1) * 100)}%` }}
                />
              </div>
            </div>
          ))}
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

  return (
    <div className="space-y-4">
      {/* Flow Status */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-zinc-300 flex items-center gap-2">
            <GitBranch className="w-4 h-4" />
            Data Flow Status
          </h3>
          <span className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            status?.is_flowing ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          )}>
            {status?.is_flowing ? 'Flowing' : 'Blocked'}
          </span>
        </div>
        <div className="text-2xl font-bold text-pink-400">
          {status?.overall_score?.toFixed(1) || 0}% Health
        </div>
      </div>

      {/* Routes */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">Active Routes</h3>
        <div className="space-y-2">
          {status?.routes && Object.entries(status.routes).slice(0, 5).map(([name, route]: [string, any]) => (
            <div key={name} className="flex items-center justify-between py-1 border-b border-zinc-700/50 last:border-0">
              <span className="text-sm text-zinc-400">{route?.display_name || name}</span>
              <div className="flex items-center gap-2">
                <span className={cn(
                  'text-xs capitalize',
                  route?.status === 'healthy' || route?.status === 'flowing' ? 'text-green-500' :
                  route?.status === 'slow' ? 'text-yellow-500' : 'text-red-500'
                )}>
                  {route?.status || 'unknown'}
                </span>
                {route?.latency_ms !== undefined && (
                  <span className="text-xs text-zinc-500">{route.latency_ms}ms</span>
                )}
              </div>
            </div>
          ))}
          {(!status?.routes || Object.keys(status.routes).length === 0) && (
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

  return (
    <div className="space-y-4">
      {/* Alignment Status */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-zinc-300">Spine Alignment</h3>
          <span className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            status?.is_aligned ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          )}>
            {status?.is_aligned ? 'Aligned' : 'Misaligned'}
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-300">{status?.total_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Total Patterns</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{status?.healthy_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Healthy</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">{status?.degraded_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Degraded</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{status?.failed_patterns || 0}</div>
            <div className="text-xs text-zinc-500">Failed</div>
          </div>
        </div>
      </div>

      {/* Integration Status */}
      {status?.integrations && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Body Integrations</h3>
          <div className="space-y-2">
            {Object.entries(status.integrations).map(([name, state]) => (
              <div key={name} className="flex items-center justify-between">
                <span className="text-sm text-zinc-400 capitalize">{name}</span>
                <span className={cn(
                  'text-sm capitalize',
                  state === 'connected' || state === 'healthy' ? 'text-green-500' : 'text-red-500'
                )}>
                  {String(state)}
                </span>
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

  return (
    <div className="space-y-4">
      {/* Threat Level */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-zinc-300 flex items-center gap-2">
            <Lock className="w-4 h-4" />
            Threat Level
          </h3>
          <span className={cn(
            'px-2 py-1 rounded text-xs font-medium uppercase',
            status?.threat_level === 'none' || status?.threat_level === 'low' ? 'bg-green-500/20 text-green-400' :
            status?.threat_level === 'elevated' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'
          )}>
            {status?.threat_level || 'unknown'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{status?.health_score?.toFixed(0) || 0}%</div>
            <div className="text-xs text-zinc-500">Immune Health</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{status?.active_threats || 0}</div>
            <div className="text-xs text-zinc-500">Active Threats</div>
          </div>
        </div>
      </div>

      {/* Quarantine */}
      {status?.quarantine && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Quarantine Status</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-xl font-bold text-zinc-300">{status.quarantine.total || 0}</div>
              <div className="text-xs text-zinc-500">Total</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-orange-400">{status.quarantine.ips || 0}</div>
              <div className="text-xs text-zinc-500">IPs</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-purple-400">{status.quarantine.users || 0}</div>
              <div className="text-xs text-zinc-500">Users</div>
            </div>
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

  return (
    <div className="space-y-4">
      {/* Digestion Score */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-zinc-300">Digestion Status</h3>
          <span className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            status?.is_digesting ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
          )}>
            {status?.is_digesting ? 'Active' : 'Idle'}
          </span>
        </div>
        <div className="text-2xl font-bold text-orange-400 mb-2">
          {status?.digestion_score?.toFixed(1) || 0}% Efficiency
        </div>
        <div className="text-sm text-zinc-500">
          {status?.items_pending || 0} items pending in queue
        </div>
      </div>

      {/* Pipeline Stages */}
      {status?.stages && (
        <div className="bg-zinc-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-zinc-300 mb-3">Pipeline Stages</h3>
          <div className="space-y-2">
            {Object.entries(status.stages).map(([stage, state]) => (
              <div key={stage} className="flex items-center justify-between">
                <span className="text-sm text-zinc-400 capitalize">{stage}</span>
                <span className={cn(
                  'text-sm capitalize',
                  state === 'healthy' || state === 'active' ? 'text-green-500' :
                  state === 'slow' || state === 'idle' ? 'text-yellow-500' : 'text-red-500'
                )}>
                  {String(state)}
                </span>
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
            <div className="text-center">
              <div className="text-xl font-bold text-blue-400">{status.metabolism.intake_rate || 0}/min</div>
              <div className="text-xs text-zinc-500">Intake</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-orange-400">{status.metabolism.processing_rate || 0}/min</div>
              <div className="text-xs text-zinc-500">Processing</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-green-400">{status.metabolism.output_rate || 0}/min</div>
              <div className="text-xs text-zinc-500">Output</div>
            </div>
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

  return (
    <div className="space-y-4">
      {/* Strength Score */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-zinc-300 flex items-center gap-2">
            <Users className="w-4 h-4" />
            Agent Execution
          </h3>
          <span className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            status?.is_strong ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
          )}>
            {status?.is_strong ? 'Strong' : 'Fatigued'}
          </span>
        </div>
        <div className="text-2xl font-bold text-purple-400 mb-2">
          {status?.strength_score?.toFixed(1) || 0}% Strength
        </div>
        <div className="text-sm text-zinc-500">
          {status?.success_rate_24h?.toFixed(1) || 0}% success rate (24h)
        </div>
      </div>

      {/* Agent Stats */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">Agent Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xl font-bold text-zinc-300">{status?.total_agents || 0}</div>
            <div className="text-xs text-zinc-500">Total</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-green-400">{status?.active_agents || 0}</div>
            <div className="text-xs text-zinc-500">Active</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-yellow-400">{status?.fatigued_agents || 0}</div>
            <div className="text-xs text-zinc-500">Fatigued</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-red-400">{status?.strained_agents || 0}</div>
            <div className="text-xs text-zinc-500">Strained</div>
          </div>
        </div>
      </div>

      {/* Executions */}
      <div className="bg-zinc-800/50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Timer className="w-4 h-4" />
          24h Executions
        </h3>
        <div className="text-2xl font-bold text-zinc-300">
          {status?.total_executions_24h?.toLocaleString() || 0}
        </div>
      </div>
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
            Real-time monitoring of all 7 body systems
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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
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
            <p className="text-zinc-500">Personal Assistant - The AI that talks to you</p>
          </div>
        </div>
      </div>

      {/* Body Coordination Panel - Session 711 */}
      <CoordinationPanel />
    </div>
  )
}
