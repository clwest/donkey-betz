import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  Home, Inbox, PlusCircle, Play, FolderOpen, AlertTriangle,
  Wrench, Settings, Zap, ArrowLeft, PanelLeft, PanelLeftClose, ShieldCheck, Bell, ScrollText, Bot,
  Layers, DollarSign, Cpu, SlidersHorizontal, ShieldAlert, Activity, Video,
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface CockpitSidebarProps {
  focusMode: boolean
  onToggleFocusMode: () => void
}

const primaryNav = [
  { path: '/cockpit', label: 'Today', icon: Home, end: true },
  { path: '/cockpit/inbox', label: 'Inbox', icon: Inbox },
  { path: '/cockpit/create', label: 'Create', icon: PlusCircle },
  { path: '/cockpit/runs', label: 'Runs', icon: Play },
  { path: '/cockpit/library', label: 'Library', icon: FolderOpen },
  { path: '/cockpit/errors', label: 'Errors', icon: AlertTriangle },
  { path: '/cockpit/approvals', label: 'Approvals', icon: ShieldCheck },
  { path: '/cockpit/alerts', label: 'Alerts', icon: Bell },
  { path: '/cockpit/agents', label: 'Agents', icon: Bot },
]

const secondaryNav = [
  { path: '/cockpit/ops', label: 'Ops', icon: Wrench },
  { path: '/cockpit/ops-runs', label: 'Ops Runs', icon: Activity },
  { path: '/cockpit/queues', label: 'Queues', icon: Layers },
  { path: '/cockpit/cost', label: 'Cost', icon: DollarSign },
  { path: '/cockpit/incidents', label: 'Incidents', icon: ShieldAlert },
  { path: '/cockpit/autopilot', label: 'Autopilot', icon: Cpu },
  { path: '/cockpit/obs', label: 'OBS', icon: Video },
  { path: '/cockpit/config', label: 'Config', icon: SlidersHorizontal },
  { path: '/cockpit/audit', label: 'Audit Log', icon: ScrollText },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function CockpitSidebar({ focusMode, onToggleFocusMode }: CockpitSidebarProps) {
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem('cockpit-sidebar-collapsed') === 'true'
  })

  const toggleCollapse = () => {
    setCollapsed((prev) => {
      const next = !prev
      localStorage.setItem('cockpit-sidebar-collapsed', String(next))
      return next
    })
  }

  const renderLink = (item: { path: string; label: string; icon: React.ElementType; end?: boolean }) => {
    const Icon = item.icon
    return (
      <NavLink
        key={item.path}
        to={item.path}
        end={item.end}
        className={({ isActive }) =>
          cn(
            'nav-link',
            isActive && 'active',
            collapsed && 'justify-center px-2',
          )
        }
        title={collapsed ? item.label : undefined}
      >
        <Icon size={20} />
        {!collapsed && <span>{item.label}</span>}
      </NavLink>
    )
  }

  return (
    <aside
      className={cn(
        'flex flex-col border-r border-dark-border bg-dark-card transition-all duration-200',
        collapsed ? 'w-16' : 'w-56',
      )}
    >
      {/* Header */}
      <div className="flex h-12 items-center justify-between border-b border-dark-border px-3">
        {!collapsed && (
          <span className="text-sm font-bold text-primary-400">Cockpit</span>
        )}
        <button
          onClick={toggleCollapse}
          className={cn(
            'p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-dark-border transition-colors',
            collapsed && 'mx-auto',
          )}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          {collapsed ? <PanelLeft size={18} /> : <PanelLeftClose size={18} />}
        </button>
      </div>

      {/* Primary nav */}
      <nav className={cn('flex-1 space-y-1 overflow-y-auto', collapsed ? 'p-2' : 'p-3')}>
        {primaryNav.map(renderLink)}

        {/* Separator */}
        <div className="my-2 border-t border-dark-border" />

        {secondaryNav.map(renderLink)}
      </nav>

      {/* Footer */}
      <div className={cn('border-t border-dark-border', collapsed ? 'p-2' : 'p-3 space-y-2')}>
        {/* Focus mode toggle */}
        <button
          onClick={onToggleFocusMode}
          className={cn(
            'flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-xs transition-colors',
            focusMode
              ? 'bg-primary-600/20 text-primary-400'
              : 'text-gray-400 hover:text-white hover:bg-dark-border',
            collapsed && 'justify-center',
          )}
          title={collapsed ? (focusMode ? 'Focus: On' : 'Focus: Off') : undefined}
        >
          <Zap size={16} />
          {!collapsed && <span>{focusMode ? 'Focus On' : 'Focus Off'}</span>}
        </button>

        {/* Back to classic */}
        <NavLink
          to="/"
          className={cn(
            'flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors',
            collapsed && 'justify-center',
          )}
          title={collapsed ? 'Back to Classic' : undefined}
        >
          <ArrowLeft size={16} />
          {!collapsed && <span>Back to Classic</span>}
        </NavLink>
      </div>
    </aside>
  )
}
