import { useEffect } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/cn'
import {
  LayoutDashboard,
  MessageSquare,
  Bot,
  Brain,
  Palette,
  Settings,
  LogOut,
  User,
  TrendingUp,
  Scale,
  Radio,
  DollarSign,
  Shield,
  FolderCog,
  Cpu,
  Activity,
  Users,
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import {
  useUnifiedStore,
  usePendingDecisionsCount,
  useRunningPilotsCount,
  useCriticalGatesCount,
} from '@/stores/unifiedStore'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/assistant', label: 'AI Assistant', icon: MessageSquare },
  { path: '/human', label: 'Human', icon: User },
  { path: '/agents', label: 'Agents', icon: Bot },
  { path: '/intelligence', label: 'Intelligence', icon: Brain },
  { path: '/body-health', label: 'Body Health', icon: Activity },
  { path: '/hive-mind', label: 'Hive Mind', icon: Users },
  { path: '/workspace', label: 'Workspace', icon: FolderCog },
  { path: '/betting', label: 'Betting', icon: TrendingUp },
  { path: '/content', label: 'Content', icon: Palette },
  { path: '/legal', label: 'Legal', icon: Scale },
  { path: '/podcast', label: 'Podcast', icon: Radio },
  { path: '/portfolio', label: 'Portfolio', icon: DollarSign },
  { path: '/admin', label: 'Admin', icon: Shield },
  { path: '/llm-routing', label: 'LLM Routing', icon: Cpu },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const { logout, user } = useAuthStore()
  const navigate = useNavigate()

  // Unified store selectors for badges
  const pendingDecisions = usePendingDecisionsCount()
  const runningPilots = useRunningPilotsCount()
  const criticalGates = useCriticalGatesCount()
  const fetchAll = useUnifiedStore((s) => s.fetchAll)

  // Fetch unified data on mount
  useEffect(() => {
    fetchAll()
    // Refresh every 60 seconds
    const interval = setInterval(fetchAll, 60000)
    return () => clearInterval(interval)
  }, [fetchAll])

  // Badge counts for specific pages
  const getBadgeCount = (path: string): number | null => {
    switch (path) {
      case '/human':
        return pendingDecisions > 0 ? pendingDecisions : null
      case '/intelligence':
        return runningPilots > 0 || criticalGates > 0
          ? runningPilots + criticalGates
          : null
      default:
        return null
    }
  }

  return (
    <aside className="flex w-64 flex-col border-r border-dark-border bg-dark-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-dark-border px-6">
        <h1 className="text-xl font-bold text-primary-400">Donkey Betz</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map(({ path, label, icon: Icon }) => {
          const badge = getBadgeCount(path)
          return (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                cn('nav-link', isActive && 'active')
              }
            >
              <Icon size={20} />
              <span className="flex-1">{label}</span>
              {badge !== null && (
                <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-primary-600 px-1.5 text-xs font-medium text-white">
                  {badge > 99 ? '99+' : badge}
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-dark-border p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/profile')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            title="View Profile"
          >
            <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-medium">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="text-sm text-gray-300">{user?.username}</span>
          </button>
          <button
            onClick={() => logout()}
            className="text-gray-400 hover:text-white transition-colors"
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  )
}
