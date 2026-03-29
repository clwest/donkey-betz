import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Home, Inbox, PlusCircle, Play, FolderOpen, AlertTriangle,
  Wrench, Settings, Zap, ArrowLeft, PanelLeft, PanelLeftClose, ShieldCheck, Bell, ScrollText, Bot,
  Layers, DollarSign, Cpu, SlidersHorizontal, ShieldAlert, Activity, Video,
  ChevronDown, Globe, Briefcase, X,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { getVipContext } from '@/lib/cockpitApi'
import { workspaceApi } from '@/lib/api'

interface CockpitSidebarProps {
  focusMode: boolean
  onToggleFocusMode: () => void
}

// Pages visible to everyone (admin + VIP)
const coreNav = [
  { path: '/cockpit', label: 'Today', icon: Home, end: true },
  { path: '/cockpit/library', label: 'Library', icon: FolderOpen },
]

// Pages visible to admin only (hidden from VIP)
const adminPrimaryNav = [
  { path: '/cockpit/inbox', label: 'Inbox', icon: Inbox },
  { path: '/cockpit/create', label: 'Create', icon: PlusCircle },
  { path: '/cockpit/runs', label: 'Runs', icon: Play },
  { path: '/cockpit/errors', label: 'Errors', icon: AlertTriangle },
  { path: '/cockpit/approvals', label: 'Approvals', icon: ShieldCheck },
  { path: '/cockpit/alerts', label: 'Alerts', icon: Bell },
  { path: '/cockpit/agents', label: 'Agents', icon: Bot },
]

const adminSecondaryNav = [
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
  const [wsDropdownOpen, setWsDropdownOpen] = useState(false)

  const activeWorkspace = useWorkspaceStore((s) => s.activeWorkspace)
  const setActiveWorkspace = useWorkspaceStore((s) => s.setActiveWorkspace)

  // VIP context
  const { data: vipContext } = useQuery({
    queryKey: ['vip-context'],
    queryFn: getVipContext,
    staleTime: 5 * 60 * 1000,
  })
  const isVip = vipContext?.is_vip ?? false

  // Fetch workspaces (admin only)
  const { data: workspacesData } = useQuery({
    queryKey: ['workspaces-list'],
    queryFn: async () => {
      const res = await workspaceApi.list()
      return res.data
    },
    enabled: !isVip,
    staleTime: 60_000,
  })
  const workspaces = (workspacesData?.workspaces || workspacesData || []) as Array<{
    id: string
    name: string
    workspace_type?: string
    is_active?: boolean
  }>

  // VIP users auto-select their workspace
  if (isVip && vipContext?.workspace_id && !activeWorkspace) {
    setActiveWorkspace({
      id: vipContext.workspace_id,
      name: vipContext.workspace_name || 'Workspace',
    })
  }

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

      {/* Workspace Switcher */}
      {!collapsed && !isVip && (
        <div className="relative px-3 pt-3 pb-1">
          <button
            onClick={() => setWsDropdownOpen(!wsDropdownOpen)}
            className={cn(
              'w-full flex items-center justify-between gap-2 px-2.5 py-2 rounded-lg text-xs transition-colors border',
              activeWorkspace
                ? 'border-primary-500/40 bg-primary-500/10 text-primary-300'
                : 'border-dark-border bg-dark-card text-gray-400 hover:text-gray-200 hover:border-gray-600',
            )}
          >
            <div className="flex items-center gap-2 min-w-0">
              {activeWorkspace ? <Briefcase size={14} /> : <Globe size={14} />}
              <span className="truncate">
                {activeWorkspace ? activeWorkspace.name : 'All Workspaces'}
              </span>
            </div>
            <ChevronDown size={14} className={cn('transition-transform', wsDropdownOpen && 'rotate-180')} />
          </button>

          {/* Dropdown */}
          {wsDropdownOpen && (
            <div className="absolute left-3 right-3 top-full mt-1 bg-dark-card border border-dark-border rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
              {/* Global option */}
              <button
                onClick={() => {
                  setActiveWorkspace(null)
                  setWsDropdownOpen(false)
                }}
                className={cn(
                  'w-full flex items-center gap-2 px-3 py-2 text-xs hover:bg-gray-800 transition-colors',
                  !activeWorkspace ? 'text-primary-400' : 'text-gray-400',
                )}
              >
                <Globe size={14} />
                All Workspaces
              </button>
              <div className="border-t border-dark-border" />
              {workspaces.map((ws) => (
                <button
                  key={ws.id}
                  onClick={() => {
                    setActiveWorkspace({ id: ws.id, name: ws.name, workspace_type: ws.workspace_type })
                    setWsDropdownOpen(false)
                  }}
                  className={cn(
                    'w-full flex items-center gap-2 px-3 py-2 text-xs hover:bg-gray-800 transition-colors',
                    activeWorkspace?.id === ws.id ? 'text-primary-400' : 'text-gray-300',
                  )}
                >
                  <Briefcase size={14} />
                  <span className="truncate">{ws.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Workspace scope pill (collapsed mode) */}
      {collapsed && activeWorkspace && (
        <div className="px-2 pt-2">
          <button
            onClick={() => setActiveWorkspace(null)}
            className="w-full p-1.5 rounded-lg bg-primary-500/10 text-primary-400 hover:bg-primary-500/20 transition-colors"
            title={`Workspace: ${activeWorkspace.name} (click to clear)`}
          >
            <Briefcase size={16} className="mx-auto" />
          </button>
        </div>
      )}

      {/* VIP workspace indicator */}
      {!collapsed && isVip && activeWorkspace && (
        <div className="px-3 pt-3 pb-1">
          <div className="flex items-center gap-2 px-2.5 py-2 rounded-lg border border-primary-500/40 bg-primary-500/10 text-primary-300 text-xs">
            <Briefcase size={14} />
            <span className="truncate">{activeWorkspace.name}</span>
          </div>
        </div>
      )}

      {/* Primary nav */}
      <nav className={cn('flex-1 space-y-1 overflow-y-auto', collapsed ? 'p-2' : 'p-3')}>
        {coreNav.map(renderLink)}

        {!isVip && (
          <>
            {adminPrimaryNav.map(renderLink)}
            {/* Separator */}
            <div className="my-2 border-t border-dark-border" />
            {adminSecondaryNav.map(renderLink)}
          </>
        )}
      </nav>

      {/* Footer */}
      <div className={cn('border-t border-dark-border', collapsed ? 'p-2' : 'p-3 space-y-2')}>
        {/* Focus mode toggle (admin only) */}
        {!isVip && (
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
        )}

        {/* Back to classic (admin only) */}
        {!isVip && (
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
        )}
      </div>
    </aside>
  )
}
