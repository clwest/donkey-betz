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
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/assistant', label: 'AI Assistant', icon: MessageSquare },
  { path: '/human', label: 'Human', icon: User },
  { path: '/agents', label: 'Agents', icon: Bot },
  { path: '/intelligence', label: 'Intelligence', icon: Brain },
  { path: '/betting', label: 'Betting', icon: TrendingUp },
  { path: '/content', label: 'Content', icon: Palette },
  { path: '/legal', label: 'Legal', icon: Scale },
  { path: '/podcast', label: 'Podcast', icon: Radio },
  { path: '/portfolio', label: 'Portfolio', icon: DollarSign },
  { path: '/admin', label: 'Admin', icon: Shield },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const { logout, user } = useAuthStore()
  const navigate = useNavigate()

  return (
    <aside className="flex w-64 flex-col border-r border-dark-border bg-dark-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-dark-border px-6">
        <h1 className="text-xl font-bold text-primary-400">Donkey Betz</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              cn('nav-link', isActive && 'active')
            }
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
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
