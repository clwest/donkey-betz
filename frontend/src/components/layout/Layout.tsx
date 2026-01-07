import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import GlobalAlertBanner, { useAlertBannerHeight } from '@/components/GlobalAlertBanner'

export default function Layout() {
  const bannerHeight = useAlertBannerHeight()

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
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
