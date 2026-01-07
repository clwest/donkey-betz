/**
 * Session 713: Global Alert Banner
 *
 * Displays critical body health alerts across all pages.
 * Shows at the top of the layout when body health is degraded or critical.
 */

import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, AlertCircle, X, Heart, Activity, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useBodyStore, useBodyHealth, useBodyAlerts } from '@/stores/bodyStore'

interface GlobalAlertBannerProps {
  className?: string
}

export default function GlobalAlertBanner({ className }: GlobalAlertBannerProps) {
  const { status, score, blocksOperations } = useBodyHealth()
  const { criticalAlerts, dismissAlert } = useBodyAlerts()
  const fetchVitals = useBodyStore((state) => state.fetchVitals)
  const fetchAlerts = useBodyStore((state) => state.fetchAlerts)
  const criticalSystems = useBodyStore((state) => state.criticalSystems)

  // Fetch body vitals on mount and periodically
  useEffect(() => {
    fetchVitals()
    fetchAlerts()

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchVitals()
      fetchAlerts()
    }, 30000)

    return () => clearInterval(interval)
  }, [fetchVitals, fetchAlerts])

  // Don't show banner if body is healthy and no critical alerts
  if (status === 'healthy' && criticalAlerts.length === 0) {
    return null
  }

  // Determine banner style based on status
  const isCritical = status === 'critical' || blocksOperations
  const isDegraded = status === 'degraded'

  const bannerStyles = isCritical
    ? 'bg-gradient-to-r from-red-900/90 to-red-800/90 border-red-500/50 text-red-100'
    : isDegraded
    ? 'bg-gradient-to-r from-amber-900/90 to-amber-800/90 border-amber-500/50 text-amber-100'
    : 'bg-gradient-to-r from-blue-900/90 to-blue-800/90 border-blue-500/50 text-blue-100'

  const iconColor = isCritical ? 'text-red-400' : isDegraded ? 'text-amber-400' : 'text-blue-400'

  return (
    <div
      className={cn(
        'fixed top-0 left-0 right-0 z-50 border-b backdrop-blur-sm',
        bannerStyles,
        className
      )}
    >
      <div className="max-w-screen-2xl mx-auto px-4 py-2">
        <div className="flex items-center justify-between gap-4">
          {/* Left: Status indicator */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              {isCritical ? (
                <AlertTriangle className={cn('animate-pulse', iconColor)} size={20} />
              ) : (
                <AlertCircle className={iconColor} size={20} />
              )}
              <Heart
                className={cn(
                  'animate-pulse',
                  isCritical ? 'text-red-400' : isDegraded ? 'text-amber-400' : 'text-blue-400'
                )}
                size={16}
              />
            </div>

            <div className="flex flex-col">
              <span className="font-semibold text-sm">
                Body Health: {status.charAt(0).toUpperCase() + status.slice(1)} ({score.toFixed(0)}%)
              </span>
              {criticalSystems.length > 0 && (
                <span className="text-xs opacity-80">
                  Critical systems: {criticalSystems.map((s) => s.toUpperCase()).join(', ')}
                </span>
              )}
            </div>
          </div>

          {/* Center: Blocking message */}
          {blocksOperations && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/30 border border-red-500/50">
              <Activity size={14} className="animate-pulse" />
              <span className="text-xs font-medium">Operations Blocked - System Recovery Required</span>
            </div>
          )}

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            <Link
              to="/body-health"
              className={cn(
                'flex items-center gap-1 px-3 py-1 rounded-md text-sm font-medium transition-colors',
                isCritical
                  ? 'bg-red-500/30 hover:bg-red-500/40'
                  : isDegraded
                  ? 'bg-amber-500/30 hover:bg-amber-500/40'
                  : 'bg-blue-500/30 hover:bg-blue-500/40'
              )}
            >
              View Details
              <ExternalLink size={14} />
            </Link>
          </div>
        </div>

        {/* Critical alerts list (if any) */}
        {criticalAlerts.length > 0 && (
          <div className="mt-2 pt-2 border-t border-white/10">
            <div className="flex flex-wrap gap-2">
              {criticalAlerts.slice(0, 3).map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center gap-2 px-2 py-1 rounded bg-black/20 text-xs"
                >
                  <span className="font-medium uppercase">{alert.system}:</span>
                  <span className="opacity-90">{alert.message}</span>
                  <button
                    onClick={() => dismissAlert(alert.id)}
                    className="ml-1 opacity-60 hover:opacity-100"
                  >
                    <X size={12} />
                  </button>
                </div>
              ))}
              {criticalAlerts.length > 3 && (
                <Link
                  to="/body-health"
                  className="px-2 py-1 rounded bg-black/20 text-xs hover:bg-black/30"
                >
                  +{criticalAlerts.length - 3} more alerts
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Hook to get the banner height for layout offset.
 * Use this to add padding to the main content when banner is visible.
 */
export function useAlertBannerHeight(): number {
  const { status } = useBodyHealth()
  const { criticalAlerts } = useBodyAlerts()

  if (status === 'healthy' && criticalAlerts.length === 0) {
    return 0
  }

  // Base height + extra for alerts
  return criticalAlerts.length > 0 ? 80 : 48
}

/**
 * Compact version for use in page headers instead of global banner.
 */
export function CompactHealthIndicator({ className }: { className?: string }) {
  const { status, score } = useBodyHealth()
  const criticalSystems = useBodyStore((state) => state.criticalSystems)

  const statusColor =
    status === 'critical'
      ? 'text-red-400 bg-red-500/20'
      : status === 'degraded'
      ? 'text-amber-400 bg-amber-500/20'
      : 'text-green-400 bg-green-500/20'

  return (
    <Link
      to="/body-health"
      className={cn(
        'flex items-center gap-2 px-2 py-1 rounded-md transition-colors hover:opacity-80',
        statusColor,
        className
      )}
      title={`Body Health: ${status} (${score.toFixed(0)}%)${
        criticalSystems.length > 0 ? ` - Critical: ${criticalSystems.join(', ')}` : ''
      }`}
    >
      <Heart
        size={14}
        className={cn(
          status === 'critical' && 'animate-pulse',
          status === 'degraded' && 'animate-pulse'
        )}
      />
      <span className="text-xs font-medium">{score.toFixed(0)}%</span>
    </Link>
  )
}
