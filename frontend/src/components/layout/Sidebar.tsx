// Session 834: Cleaned up sidebar - consolidated items moved to Workspace tabs
import { useEffect, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/cn'
import {
  LayoutDashboard,
  MessageSquare,
  Gavel,
  Bot,
  Palette,
  Settings,
  LogOut,
  User,
  TrendingUp,
  Scale,
  DollarSign,
  Shield,
  ShieldCheck,
  FolderCog,
  LayoutGrid,
  FileText,
  Beaker,
  Book,
  PanelLeftClose,
  PanelLeft,
  Home,
  Command,
  Film,
  Landmark,
  FileUp,
  HelpCircle,
  Play,
  Zap,
  Package,
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import {
  useUnifiedStore,
  usePendingDecisionsCount,
  useRunningPilotsCount,
  useCriticalGatesCount,
} from '@/stores/unifiedStore'

// Session 834: Streamlined navigation
// Consolidated items are now in Workspace tabs:
// - Infrastructure tab: Body Health, Integration, LLM Routing, Analytics, Billing
// - Orchestration tab: Agent Monitor, Hive Mind, Autonomous
// - Consciousness tab: Memory Palace, Orchestra, Mood, Evolution, Relationships, Capsules, Time Travel
// - Intelligence tab: Reasoning, Collective
// - DataSources tab: Spiders, Spider Feed, Learning
// - Content Studio tab: Podcast, Channels, Blogs, Distribution
// - Command tab: Conversations, Dreams, Advisors
// Session 931: Unified Command Center replaces Home, AI Assistant, Human
// Session 857: Workspace is the modular content hub
const navItems = [
  // Focus Cockpit — solo-operator flow
  { path: '/cockpit', label: 'Focus Cockpit', icon: Zap },

  // Session 931: Command Center - Unified AI interface + controls
  { path: '/', label: 'Command Center', icon: Command },

  // Session 1035: Platform dashboard (system-wide tabs) + Workspace (project-specific)
  { path: '/platform', label: 'Platform', icon: LayoutGrid },
  { path: '/workspace', label: 'Workspace', icon: FolderCog },
  { path: '/image-studio', label: 'Image Studio', icon: Palette },
  { path: '/video-studio', label: 'Video Studio', icon: Film },

  // Session 1067: Full-page boardroom & governance
  { path: '/boardroom', label: 'Boardroom', icon: Gavel },
  { path: '/governance', label: 'Governance', icon: ShieldCheck },

  // Session 1076: Executor runs
  { path: '/executor', label: 'Executor', icon: Play },

  // Core Navigation
  { path: '/agents', label: 'Agents', icon: Bot },
  { path: '/stocks', label: 'Stock Intelligence', icon: TrendingUp },
  { path: '/government', label: 'Government', icon: Landmark },

  // Domain Features - Session 899/997B: Betting re-enabled
  { path: '/betting', label: 'Betting', icon: DollarSign },
  // { path: '/legal', label: 'Legal', icon: Scale },
  // { path: '/portfolio', label: 'Portfolio', icon: DollarSign },

  // Documents & Reference
  { path: '/deliverables', label: 'Deliverables', icon: Package },
  { path: '/documents', label: 'Documents', icon: FileUp },
  { path: '/docs-index', label: 'Docs Index', icon: Book },
  { path: '/how-it-works', label: 'How it Works', icon: HelpCircle },
  { path: '/mythology-lab', label: 'Mythology Lab', icon: Beaker },
  // Session 872: Removed Voices - available in Workspace tab

  // Admin & Settings
  { path: '/admin', label: 'Admin', icon: Shield },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const { logout, user } = useAuthStore()
  const navigate = useNavigate()

  // Collapsed state - persist in localStorage
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebar-collapsed')
    return saved === 'true'
  })

  // Toggle collapse and persist
  const toggleCollapse = () => {
    const newState = !isCollapsed
    setIsCollapsed(newState)
    localStorage.setItem('sidebar-collapsed', String(newState))
  }

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
      case '/boardroom':
        return pendingDecisions > 0 ? pendingDecisions : null
      case '/governance':
        return criticalGates > 0 ? criticalGates : null
      case '/workspace':
        // Show badge if there are running pilots or critical gates
        return runningPilots > 0 || criticalGates > 0
          ? runningPilots + criticalGates
          : null
      default:
        return null
    }
  }

  return (
    <aside
      className={cn(
        'flex flex-col border-r border-dark-border bg-dark-card transition-all duration-200',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo & Collapse Toggle */}
      <div className="flex h-16 items-center justify-between border-b border-dark-border px-3">
        {!isCollapsed && (
          <h1 className="text-xl font-bold text-primary-400 truncate">Donkey Betz</h1>
        )}
        <button
          onClick={toggleCollapse}
          className={cn(
            'p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-border transition-colors',
            isCollapsed && 'mx-auto'
          )}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
        </button>
      </div>

      {/* Navigation - scrollable area */}
      <nav className={cn('flex-1 overflow-y-auto space-y-1', isCollapsed ? 'p-2' : 'p-4')}>
        {navItems
          .filter(({ path }) => !(path === '/admin' && user?.platform_role === 'reviewer'))
          .map(({ path, label, icon: Icon }) => {
          const badge = getBadgeCount(path)
          return (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                cn(
                  'nav-link',
                  isActive && 'active',
                  isCollapsed && 'justify-center px-2'
                )
              }
              title={isCollapsed ? label : undefined}
            >
              <Icon size={20} />
              {!isCollapsed && <span className="flex-1">{label}</span>}
              {badge !== null && !isCollapsed && (
                <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-primary-600 px-1.5 text-xs font-medium text-white">
                  {badge > 99 ? '99+' : badge}
                </span>
              )}
              {badge !== null && isCollapsed && (
                <span className="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary-600 px-1 text-[10px] font-medium text-white">
                  {badge > 9 ? '9+' : badge}
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* User Section */}
      <div className={cn('border-t border-dark-border', isCollapsed ? 'p-2' : 'p-4')}>
        <div className={cn('flex items-center', isCollapsed ? 'justify-center' : 'justify-between')}>
          <button
            onClick={() => navigate('/profile')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            title={isCollapsed ? user?.username || 'Profile' : 'View Profile'}
          >
            <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-medium flex-shrink-0">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            {!isCollapsed && (
              <span className="text-sm text-gray-300 truncate">{user?.username}</span>
            )}
          </button>
          {!isCollapsed && (
            <button
              onClick={() => logout()}
              className="text-gray-400 hover:text-white transition-colors"
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          )}
        </div>
      </div>
    </aside>
  )
}
