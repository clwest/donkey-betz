import { useCallback } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import GlobalAlertBanner, { useAlertBannerHeight } from '@/components/GlobalAlertBanner'
import GlobalPADock from '@/components/GlobalPADock'
import { useSystemEvents } from '@/hooks/useWebSocket'
import { useUnifiedStore } from '@/stores/unifiedStore'
import { usePageTracking } from '@/hooks/usePageTracking'  // Session 971b: Route telemetry

export default function Layout() {
  // Session 971b: Track all route changes for telemetry
  usePageTracking()

  const location = useLocation()
  const bannerHeight = useAlertBannerHeight()

  const hideGlobalDock = location.pathname === '/'

  // Session 715: Wire system events to unified store
  const fetchAttentionStats = useUnifiedStore((s) => s.fetchAttentionStats)
  const fetchRunningPilots = useUnifiedStore((s) => s.fetchRunningPilots)
  const fetchCriticalGates = useUnifiedStore((s) => s.fetchCriticalGates)
  const fetchTopOpportunities = useUnifiedStore((s) => s.fetchTopOpportunities)

  // Event handlers that refresh unified store
  const handlePilotEvent = useCallback(() => {
    fetchRunningPilots()
    fetchCriticalGates()
  }, [fetchRunningPilots, fetchCriticalGates])

  const handleGateEvent = useCallback(() => {
    fetchCriticalGates()
    fetchAttentionStats()
  }, [fetchCriticalGates, fetchAttentionStats])

  const handleAgentExecution = useCallback(() => {
    // Agent executions may affect opportunities
    fetchTopOpportunities()
  }, [fetchTopOpportunities])

  // Subscribe to system events for real-time store updates
  useSystemEvents({
    onPilotStarted: handlePilotEvent,
    onPilotCompleted: handlePilotEvent,
    onGateBecameCritical: handleGateEvent,
    onAgentExecutionComplete: handleAgentExecution,
  })

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Session 713: Global Body Health Alert Banner */}
      <GlobalAlertBanner />

      <Sidebar />
      <div
        className="flex flex-1 flex-col overflow-hidden transition-all duration-200"
        style={{ paddingTop: bannerHeight > 0 ? `${bannerHeight}px` : undefined }}
      >
        <Header />
        <main className="flex-1 flex flex-col overflow-hidden p-6">
          <div className="flex-1 min-h-0 overflow-auto">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Session 948: Global PA Dock - hidden on Command Center (has built-in chat) */}
      {!hideGlobalDock && <GlobalPADock />}
    </div>
  )
}
