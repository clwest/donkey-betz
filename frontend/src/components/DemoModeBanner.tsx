/**
 * Session 1090: Demo Mode Banner
 *
 * Persistent banner at top of all pages when DEMO_MODE=true.
 * Polls /api/system/demo-status/ every 60s.
 */

import { useState, useEffect } from 'react'
import { Shield } from 'lucide-react'

interface DemoStatus {
  demo_mode: boolean
  governor_enabled: boolean
  allowlist_count: number
  max_executions_per_hour: number | null
}

export default function DemoModeBanner() {
  const [status, setStatus] = useState<DemoStatus | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('/api/system/demo-status/')
        if (res.ok) {
          setStatus(await res.json())
        }
      } catch {
        // silently ignore — banner just won't show
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 60000)
    return () => clearInterval(interval)
  }, [])

  if (!status?.demo_mode) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-[60] bg-gradient-to-r from-indigo-900/95 to-purple-900/95 border-b border-indigo-500/40 backdrop-blur-sm">
      <div className="max-w-screen-2xl mx-auto px-4 py-1.5">
        <div className="flex items-center justify-center gap-3 text-sm text-indigo-100">
          <Shield size={16} className="text-indigo-400" />
          <span className="font-semibold">DEMO MODE</span>
          <span className="text-indigo-300">|</span>
          <span>{status.allowlist_count} agents allowed</span>
          <span className="text-indigo-300">|</span>
          <span>{status.max_executions_per_hour}/hr cap</span>
          <span className="text-indigo-300">|</span>
          <span>Governor {status.governor_enabled ? 'ON' : 'OFF'}</span>
        </div>
      </div>
    </div>
  )
}

/**
 * Hook to get the banner height for layout padding.
 * Returns 32 when demo mode is active, 0 otherwise.
 */
export function useDemoModeBannerHeight(): number {
  const [active, setActive] = useState(false)

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('/api/system/demo-status/')
        if (res.ok) {
          const data = await res.json()
          setActive(data.demo_mode === true)
        }
      } catch {
        setActive(false)
      }
    }
    check()
    const interval = setInterval(check, 60000)
    return () => clearInterval(interval)
  }, [])

  return active ? 32 : 0
}
