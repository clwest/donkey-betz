// Session 834: Cleaned up sidebar - consolidated items moved to Workspace tabs
// Session 1083: Option C layout — user menu popover + Reference submenu
import { useEffect, useRef, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/cn'
import {
  LayoutDashboard,
  MessageSquare,
  Bot,
  Palette,
  Settings,
  LogOut,
  User,
  TrendingUp,
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
  Command,
  Film,
  Landmark,
  FileUp,
  HelpCircle,
  Play,
  Package,
  ChevronDown,
  ChevronRight,
  BookOpen,
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { usePAStore } from '@/stores/paStore'
import {
  useUnifiedStore,
  usePendingDecisionsCount,
  useRunningPilotsCount,
  useCriticalGatesCount,
} from '@/stores/unifiedStore'

// Session 1083: Sidebar redesign (Option C, Rigby verdict)
// - Profile / Settings / Admin moved into the avatar popover at the bottom
// - Reference items (Documents, Docs Index, How it Works, Mythology Lab)
//   collapsed into a single expandable "Reference" section
// - Target: ~14 primary rail items
//
// Historical: consolidated workspace items live in Workspace tabs:
//   Infrastructure, Orchestration, Consciousness, Intelligence,
//   DataSources, Content Studio, Command. See Session 834 notes.
const navItems = [
  // Hub
  { path: '/', label: 'Command Center', icon: Command },
  { path: '/inbox', label: 'Messages', icon: MessageSquare },
  { path: '/workspace', label: 'Workspace', icon: FolderCog },

  // Studios
  { path: '/image-studio', label: 'Image Studio', icon: Palette },
  { path: '/video-studio', label: 'Video Studio', icon: Film },
  { path: '/content', label: 'Content', icon: LayoutGrid },
  { path: '/media', label: 'Media', icon: Package },

  // Agents & intelligence
  { path: '/executor', label: 'Executor', icon: Play },
  { path: '/agents', label: 'Agents', icon: Bot },
  { path: '/advisors', label: 'Advisors', icon: ShieldCheck },
  { path: '/stocks', label: 'Stock Intelligence', icon: TrendingUp },
  { path: '/government', label: 'Government', icon: Landmark },

  // Work surfaces
  { path: '/deliverables', label: 'Deliverables', icon: FileText },
  { path: '/analytics', label: 'Analytics', icon: LayoutDashboard },
  { path: '/betting', label: 'Betting', icon: DollarSign },
]

// Reference submenu — expandable group in the sidebar
const referenceItems = [
  { path: '/documents', label: 'Documents', icon: FileUp },
  { path: '/docs-index', label: 'Docs Index', icon: Book },
  { path: '/how-it-works', label: 'How it Works', icon: HelpCircle },
  { path: '/mythology-lab', label: 'Mythology Lab', icon: Beaker },
]

export default function Sidebar() {
  const { logout, user } = useAuthStore()
  const syncUser = usePAStore((s) => s.syncUser)
  const navigate = useNavigate()

  // Collapsed state - persist in localStorage
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebar-collapsed')
    return saved === 'true'
  })

  // Reference submenu expand/collapse (persisted)
  const [referenceOpen, setReferenceOpen] = useState(() => {
    return localStorage.getItem('sidebar-reference-open') === 'true'
  })
  const toggleReference = () => {
    const newState = !referenceOpen
    setReferenceOpen(newState)
    localStorage.setItem('sidebar-reference-open', String(newState))
  }

  // User menu popover
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef<HTMLDivElement | null>(null)
  useEffect(() => {
    if (!userMenuOpen) return
    const onClick = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [userMenuOpen])

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

  // Inbox unread count
  const [inboxUnread, setInboxUnread] = useState(0)

  // Fetch unified data on mount
  useEffect(() => {
    fetchAll()
    // Refresh every 60 seconds
    const interval = setInterval(fetchAll, 60000)
    return () => clearInterval(interval)
  }, [fetchAll])

  // Poll inbox unread count
  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const { api } = await import('@/lib/api')
        const res = await api.get('/inbox/unread-count/')
        if (res.data.success) setInboxUnread(res.data.unread_count)
      } catch { /* ignore */ }
    }
    fetchUnread()
    const interval = setInterval(fetchUnread, 30000)
    return () => clearInterval(interval)
  }, [])

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
      case '/inbox':
        return inboxUnread > 0 ? inboxUnread : null
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
        {navItems.map(({ path, label, icon: Icon }) => {
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

        {/* Reference group — expandable */}
        {isCollapsed ? (
          referenceItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                cn('nav-link justify-center px-2', isActive && 'active')
              }
              title={label}
            >
              <Icon size={20} />
            </NavLink>
          ))
        ) : (
          <>
            <button
              type="button"
              onClick={toggleReference}
              className="nav-link w-full"
              aria-expanded={referenceOpen}
            >
              <BookOpen size={20} />
              <span className="flex-1 text-left">Reference</span>
              {referenceOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
            {referenceOpen && (
              <div className="ml-4 space-y-1 border-l border-dark-border pl-2">
                {referenceItems.map(({ path, label, icon: Icon }) => (
                  <NavLink
                    key={path}
                    to={path}
                    className={({ isActive }) => cn('nav-link text-sm', isActive && 'active')}
                  >
                    <Icon size={16} />
                    <span className="flex-1">{label}</span>
                  </NavLink>
                ))}
              </div>
            )}
          </>
        )}
      </nav>

      {/* User Section — popover menu (Session 1083) */}
      <div
        ref={userMenuRef}
        className={cn('relative border-t border-dark-border', isCollapsed ? 'p-2' : 'p-4')}
      >
        <button
          type="button"
          onClick={() => setUserMenuOpen((v) => !v)}
          className={cn(
            'flex items-center gap-3 w-full hover:opacity-80 transition-opacity',
            isCollapsed && 'justify-center'
          )}
          title={user?.username || 'Account'}
          aria-haspopup="menu"
          aria-expanded={userMenuOpen}
        >
          <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-medium flex-shrink-0">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          {!isCollapsed && (
            <>
              <span className="text-sm text-gray-300 truncate flex-1 text-left">
                {user?.username}
              </span>
              <ChevronRight
                size={16}
                className={cn(
                  'text-gray-500 transition-transform',
                  userMenuOpen && 'rotate-90'
                )}
              />
            </>
          )}
        </button>

        {userMenuOpen && (
          <div
            role="menu"
            className={cn(
              'absolute z-50 rounded-lg border border-dark-border bg-dark-card shadow-xl py-1 min-w-[180px]',
              isCollapsed
                ? 'bottom-2 left-[calc(100%+8px)]'
                : 'bottom-[calc(100%-4px)] left-4 right-4'
            )}
          >
            <button
              type="button"
              role="menuitem"
              onClick={() => { setUserMenuOpen(false); navigate('/profile') }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-dark-hover"
            >
              <User size={16} /> Profile
            </button>
            <button
              type="button"
              role="menuitem"
              onClick={() => { setUserMenuOpen(false); navigate('/settings') }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-dark-hover"
            >
              <Settings size={16} /> Settings
            </button>
            {user?.platform_role !== 'reviewer' && (
              <button
                type="button"
                role="menuitem"
                onClick={() => { setUserMenuOpen(false); navigate('/admin') }}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-dark-hover"
              >
                <Shield size={16} /> Admin
              </button>
            )}
            <div className="my-1 border-t border-dark-border" />
            <button
              type="button"
              role="menuitem"
              onClick={() => { setUserMenuOpen(false); syncUser(null); logout() }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-dark-hover"
            >
              <LogOut size={16} /> Logout
            </button>
          </div>
        )}
      </div>
    </aside>
  )
}
