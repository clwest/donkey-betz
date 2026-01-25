/**
 * Session 815: Emergency Controls Component
 * Session 818: Made SKIN Lock toggleable, added interactivity
 *
 * Displays governance controls including SKIN lock, emergency halt,
 * and quarantine status. Part of the Platform Command Center.
 */

import { useState } from 'react'
import {
  AlertTriangle, Lock, Unlock, Power, Shield, AlertCircle,
  CheckCircle, Loader2, XCircle, Activity, ChevronRight, ExternalLink
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface EmergencyStatus {
  skin_lock: boolean
  skin_status: string
  quarantined_agents: string[]
  quarantined_count: number
  system_paused: boolean
  pending_critical_decisions: number
}

interface SystemOwner {
  name: string
  authority: string
  override_level: string
  contact: string
}

interface EmergencyControlsProps {
  emergency?: EmergencyStatus
  owner?: SystemOwner
  isLoading?: boolean
  onEmergencyHalt?: () => Promise<void>
  onSkinLockToggle?: (action: 'lock' | 'unlock' | 'toggle') => Promise<void>  // Session 818
}

export function EmergencyControls({
  emergency,
  owner,
  isLoading,
  onEmergencyHalt,
  onSkinLockToggle
}: EmergencyControlsProps) {
  const [isHalting, setIsHalting] = useState(false)
  const [isTogglingLock, setIsTogglingLock] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const handleHalt = async () => {
    if (!onEmergencyHalt) return

    setIsHalting(true)
    try {
      await onEmergencyHalt()
      setShowConfirm(false)
    } finally {
      setIsHalting(false)
    }
  }

  const handleSkinLockToggle = async () => {
    if (!onSkinLockToggle) return

    setIsTogglingLock(true)
    try {
      await onSkinLockToggle('toggle')
    } finally {
      setIsTogglingLock(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {/* Owner Card Skeleton */}
        <div className="card animate-pulse">
          <div className="h-4 bg-gray-700 rounded w-1/3 mb-3"></div>
          <div className="h-6 bg-gray-700 rounded w-1/2"></div>
        </div>
        {/* Controls Skeleton */}
        <div className="card animate-pulse">
          <div className="h-4 bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-8 bg-gray-700 rounded"></div>
            <div className="h-8 bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* System Owner Card */}
      {owner && (
        <div className="card border border-accent-blue/30 bg-gradient-to-br from-accent-blue/5 to-transparent">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-10 w-10 rounded-full bg-accent-blue/20 flex items-center justify-center">
              <Shield className="text-accent-blue" size={20} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">{owner.name}</h3>
              <span className="text-xs text-gray-400">System Owner</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Authority:</span>
              <span className="text-white ml-2">{owner.authority}</span>
            </div>
            <div>
              <span className="text-gray-500">Override:</span>
              <span className="text-white ml-2">{owner.override_level}</span>
            </div>
          </div>
        </div>
      )}

      {/* Emergency Controls Panel */}
      <div className="card border border-accent-red/20">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="text-accent-amber" size={18} />
          <h3 className="text-md font-semibold text-white uppercase">Emergency Controls</h3>
        </div>

        {emergency && (
          <div className="space-y-3">
            {/* SKIN Lock Status - Session 818: Now toggleable */}
            <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                {emergency.skin_lock ? (
                  <Lock className="text-accent-red" size={16} />
                ) : (
                  <Unlock className="text-accent-green" size={16} />
                )}
                <div>
                  <span className="text-sm text-white">SKIN Lock</span>
                  <span className={cn(
                    'ml-2 text-xs px-2 py-0.5 rounded',
                    emergency.skin_lock
                      ? 'bg-accent-red/20 text-accent-red'
                      : 'bg-accent-green/20 text-accent-green'
                  )}>
                    {emergency.skin_lock ? 'LOCKED' : 'OFF'}
                  </span>
                  <span className="text-xs text-gray-500 ml-2">{emergency.skin_status}</span>
                </div>
              </div>
              {onSkinLockToggle && (
                <button
                  onClick={handleSkinLockToggle}
                  disabled={isTogglingLock}
                  className={cn(
                    'flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-colors disabled:opacity-50',
                    emergency.skin_lock
                      ? 'bg-accent-green/20 hover:bg-accent-green/30 text-accent-green'
                      : 'bg-accent-red/20 hover:bg-accent-red/30 text-accent-red'
                  )}
                >
                  {isTogglingLock ? (
                    <Loader2 className="animate-spin" size={12} />
                  ) : emergency.skin_lock ? (
                    <Unlock size={12} />
                  ) : (
                    <Lock size={12} />
                  )}
                  {emergency.skin_lock ? 'Unlock' : 'Lock'}
                </button>
              )}
            </div>

            {/* Agent Quarantine - Session 818: Made clickable */}
            <a
              href="/ai-studio?tab=agents"
              className="flex items-center justify-between p-3 bg-gray-800/50 hover:bg-gray-800 rounded-lg transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Shield className={cn(
                  emergency.quarantined_count > 0 ? 'text-accent-amber' : 'text-accent-green'
                )} size={16} />
                <div>
                  <span className="text-sm text-white group-hover:text-primary-400 transition-colors">Agent Quarantine</span>
                  <span className={cn(
                    'ml-2 text-xs px-2 py-0.5 rounded',
                    emergency.quarantined_count > 0
                      ? 'bg-accent-amber/20 text-accent-amber'
                      : 'bg-accent-green/20 text-accent-green'
                  )}>
                    {emergency.quarantined_count}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">
                  {emergency.quarantined_count > 0
                    ? `${emergency.quarantined_agents.slice(0, 2).join(', ')}${emergency.quarantined_count > 2 ? '...' : ''}`
                    : 'None quarantined'}
                </span>
                <ChevronRight size={14} className="text-gray-600 group-hover:text-primary-400 transition-colors" />
              </div>
            </a>

            {/* System Status - Session 818: Made clickable */}
            <a
              href="/human?tab=body"
              className="flex items-center justify-between p-3 bg-gray-800/50 hover:bg-gray-800 rounded-lg transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Activity className={cn(
                  emergency.system_paused ? 'text-accent-red' : 'text-accent-green'
                )} size={16} />
                <div>
                  <span className="text-sm text-white group-hover:text-primary-400 transition-colors">System Status</span>
                  <span className={cn(
                    'ml-2 text-xs px-2 py-0.5 rounded',
                    emergency.system_paused
                      ? 'bg-accent-red/20 text-accent-red'
                      : 'bg-accent-green/20 text-accent-green'
                  )}>
                    {emergency.system_paused ? 'PAUSED' : 'RUNNING'}
                  </span>
                </div>
              </div>
              <ChevronRight size={14} className="text-gray-600 group-hover:text-primary-400 transition-colors" />
            </a>

            {/* Critical Decisions Warning */}
            {emergency.pending_critical_decisions > 0 && (
              <div className="flex items-center gap-2 p-3 bg-accent-red/10 border border-accent-red/30 rounded-lg">
                <AlertCircle className="text-accent-red" size={16} />
                <span className="text-sm text-accent-red">
                  {emergency.pending_critical_decisions} critical decision(s) pending
                </span>
              </div>
            )}

            {/* Emergency Halt Button */}
            <div className="pt-2 border-t border-gray-700/50">
              {!showConfirm ? (
                <button
                  onClick={() => setShowConfirm(true)}
                  className="w-full flex items-center justify-center gap-2 py-3 bg-accent-red/20 hover:bg-accent-red/30 border border-accent-red/50 rounded-lg text-accent-red font-medium transition-colors"
                >
                  <Power size={18} />
                  EMERGENCY HALT
                </button>
              ) : (
                <div className="p-3 bg-accent-red/10 border border-accent-red/30 rounded-lg">
                  <p className="text-sm text-accent-red mb-3">
                    Are you sure? This will flag all autonomous operations for review.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={handleHalt}
                      disabled={isHalting}
                      className="flex-1 flex items-center justify-center gap-2 py-2 bg-accent-red hover:bg-accent-red/80 rounded text-white font-medium transition-colors disabled:opacity-50"
                    >
                      {isHalting ? (
                        <Loader2 className="animate-spin" size={16} />
                      ) : (
                        <CheckCircle size={16} />
                      )}
                      Confirm Halt
                    </button>
                    <button
                      onClick={() => setShowConfirm(false)}
                      className="flex-1 flex items-center justify-center gap-2 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white transition-colors"
                    >
                      <XCircle size={16} />
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
