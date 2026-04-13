import { useCallback } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import GlobalAlertBanner, { useAlertBannerHeight } from '@/components/GlobalAlertBanner'
import GlobalPADock from '@/components/GlobalPADock'
import { useSystemEvents } from '@/hooks/useWebSocket'
import { useUnifiedStore } from '@/stores/unifiedStore'
import { usePageTracking } from '@/hooks/usePageTracking'

export default function Layout() {
  usePageTracking()

  const location = useLocation()
  const bannerHeight = useAlertBannerHeight()

  // Hide floating PA dock on Command Center — it has its own built-in chat
  const hideGlobalDock = location.pathname === '/'

  const fetchAttentionStats = useUnifiedStore((s) => s.fetchAttentionStats)
  const fetchRunningPilots = useUnifiedStore((s) => s.fetchRunningPilots)
  const fetchCriticalGates = useUnifiedStore((s) => s.fetchCriticalGates)
  const fetchTopOpportunities = useUnifiedStore((s) => s.fetchTopOpportunities)

  const handlePilotEvent = useCallback(() => {
    fetchRunningPilots()
    fetchCriticalGates()
  }, [fetchRunningPilots, fetchCriticalGates])

  const handleGateEvent = useCallback(() => {
    fetchCriticalGates()
    fetchAttentionStats()
  }, [fetchCriticalGates, fetchAttentionStats])

  const handleAgentExecution = useCallback(() => {
    fetchTopOpportunities()
  }, [fetchTopOpportunities])

  useSystemEvents({
    onPilotStarted: handlePilotEvent,
    onPilotCompleted: handlePilotEvent,
    onGateBecameCritical: handleGateEvent,
    onAgentExecutionComplete: handleAgentExecution,
  })

  return (
    <div className="flex h-screen overflow-hidden">
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

      {!hideGlobalDock && <GlobalPADock />}
    </div>
  )
}
