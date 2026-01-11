import { useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Bell, Search } from 'lucide-react'
import { reasoningApi } from '@/lib/api'

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/assistant': 'AI Assistant',
  '/agents': 'Agent Collaboration',
  '/intelligence': 'Intelligence Command Center',
  '/content': 'Content Studio',
  '/settings': 'Settings',
}

export default function Header() {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'Donkey Betz'

  // Session 745: Fetch pending actions count for notification badge
  const { data: pendingActionsData } = useQuery({
    queryKey: ['pending-actions-count'],
    queryFn: () => reasoningApi.pendingActions(),
    refetchInterval: 60000, // Refresh every minute
    staleTime: 30000, // Consider data fresh for 30 seconds
  })
  const pendingActionsCount = pendingActionsData?.data?.count ?? pendingActionsData?.data?.actions?.length ?? 0

  return (
    <header className="flex h-16 items-center justify-between border-b border-dark-border bg-dark-card px-6">
      <h2 className="text-lg font-semibold">{title}</h2>

      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"
          />
          <input
            type="text"
            placeholder="Search..."
            className="input w-64 pl-10"
          />
        </div>

        {/* Notifications - Session 745: Real pending actions count */}
        <button className="relative text-gray-400 hover:text-white transition-colors">
          <Bell size={20} />
          {pendingActionsCount > 0 && (
            <span className="absolute -right-1 -top-1 h-4 w-4 rounded-full bg-accent-red text-xs flex items-center justify-center">
              {pendingActionsCount > 99 ? '99+' : pendingActionsCount}
            </span>
          )}
        </button>
      </div>
    </header>
  )
}
