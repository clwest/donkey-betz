/**
 * Session 2971: Signal Intelligence UI — Workspace sub-tab.
 *
 * Deliverable ade9339f-c41f-48a5-9ce8-fa8beee696cc. Replaces reliance on
 * the separate signal-studio app. Reachable at
 *   /workspace?tab=intelligence&sub=signals
 *
 * Three views share a single window (24h/7d/30d) selector:
 *   - Dashboard: ingestion summary + coverage + cluster summary
 *   - Feed: paginated LegacySpiderData browse + row detail drawer
 *   - Clusters: SignalCluster explorer + cluster detail drawer
 */

import { useState } from 'react'
import { LayoutDashboard, Rss, Radar } from 'lucide-react'
import { cn } from '@/lib/cn'
import { SignalsDashboardView } from './SignalsDashboardView'
import { SignalsFeedView } from './SignalsFeedView'
import { SignalsClustersView } from './SignalsClustersView'

export type SignalsView = 'dashboard' | 'feed' | 'clusters'
export type SignalsWindow = 24 | 168 | 720  // hours: 24h / 7d / 30d

const WINDOW_OPTIONS: Array<{ hours: SignalsWindow; label: string; days: number }> = [
  { hours: 24, label: 'Last 24h', days: 1 },
  { hours: 168, label: 'Last 7d', days: 7 },
  { hours: 720, label: 'Last 30d', days: 30 },
]

const VIEW_TABS: Array<{ id: SignalsView; label: string; icon: typeof LayoutDashboard }> = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'feed', label: 'Feed Explorer', icon: Rss },
  { id: 'clusters', label: 'Cluster Explorer', icon: Radar },
]

export function SignalsTab() {
  const [view, setView] = useState<SignalsView>('dashboard')
  const [windowHours, setWindowHours] = useState<SignalsWindow>(168)
  const windowDays = WINDOW_OPTIONS.find(w => w.hours === windowHours)?.days ?? 7

  return (
    <div className="space-y-4">
      {/* Header — view switcher + window selector */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-3">
        <div className="flex gap-2 overflow-x-auto">
          {VIEW_TABS.map(tab => {
            const Icon = tab.icon
            const isActive = view === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setView(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
                  isActive
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
                )}
              >
                <Icon size={14} />
                {tab.label}
              </button>
            )
          })}
        </div>

        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-500">Window</span>
          <div className="flex rounded-lg border border-gray-800 overflow-hidden">
            {WINDOW_OPTIONS.map(opt => (
              <button
                key={opt.hours}
                onClick={() => setWindowHours(opt.hours)}
                className={cn(
                  'px-3 py-1.5 text-xs',
                  windowHours === opt.hours
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/50',
                )}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      {view === 'dashboard' && (
        <SignalsDashboardView
          windowHours={windowHours}
          windowDays={windowDays}
          onNavigate={setView}
        />
      )}
      {view === 'feed' && <SignalsFeedView windowHours={windowHours} />}
      {view === 'clusters' && <SignalsClustersView windowHours={windowHours} />}
    </div>
  )
}

export default SignalsTab
