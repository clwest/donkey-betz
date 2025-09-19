import { NavLink, useNavigate } from 'react-router-dom';
import {
  HomeIcon,
  CpuChipIcon,
  SparklesIcon,
  PhotoIcon,
  MegaphoneIcon,
  BookOpenIcon,
  MicrophoneIcon,
  AcademicCapIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  UserCircleIcon,
  UserGroupIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  CloudArrowUpIcon,
  ArrowRightOnRectangleIcon,
  BeakerIcon,
  CircleStackIcon,
  ChatBubbleLeftRightIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  CpuChipIcon as CpuChipIconSolid,
  SparklesIcon as SparklesIconSolid,
  PhotoIcon as PhotoIconSolid,
  MegaphoneIcon as MegaphoneIconSolid,
  BookOpenIcon as BookOpenIconSolid,
  MicrophoneIcon as MicrophoneIconSolid,
  AcademicCapIcon as AcademicCapIconSolid,
  UserCircleIcon as UserCircleIconSolid,
  UserGroupIcon as UserGroupIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  Cog6ToothIcon as Cog6ToothIconSolid,
  CloudArrowUpIcon as CloudArrowUpIconSolid,
  ArrowRightOnRectangleIcon as ArrowRightOnRectangleIconSolid,
  BeakerIcon as BeakerIconSolid,
  CircleStackIcon as CircleStackIconSolid,
  ChatBubbleLeftRightIcon as ChatBubbleLeftRightIconSolid,
  CurrencyDollarIcon as CurrencyDollarIconSolid,
  BanknotesIcon as BanknotesIconSolid,
} from '@heroicons/react/24/solid';
import clsx from 'clsx';
import { useAuthStore } from '../../store/authStore';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, iconActive: HomeIconSolid },
  { name: 'Command Center', href: '/command-center', icon: UserCircleIcon, iconActive: UserCircleIconSolid, badge: '🎯 UNIFIED' },
  { name: 'Neural Orchestra', href: '/neural-orchestra', icon: CpuChipIcon, iconActive: CpuChipIconSolid, badge: 'LIVE' },
  { name: 'Agent Hub', href: '/agent-hub', icon: UserGroupIcon, iconActive: UserGroupIconSolid },
  { name: 'Workflow Engine', href: '/workflows', icon: CircleStackIcon, iconActive: CircleStackIconSolid },
  { name: 'Content Studio', href: '/studio', icon: SparklesIcon, iconActive: SparklesIconSolid },
  { name: 'Media Vault', href: '/gallery', icon: PhotoIcon, iconActive: PhotoIconSolid },
  // { name: 'Characters', href: '/character', icon: UserGroupIcon, iconActive: UserGroupIconSolid, badge: 'NEW' }, // Hidden - on backburner
  { name: 'Library', href: '/ebooks', icon: BookOpenIcon, iconActive: BookOpenIconSolid },
  { name: 'Voice Studio', href: '/voice', icon: MicrophoneIcon, iconActive: MicrophoneIconSolid },
];

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login'); // Navigate to login page after logout
  };

  return (
    <div
      className={clsx(
        'relative flex flex-col transition-all duration-300 bg-card/95 backdrop-blur-md border-r border-border/50 shadow-dark-xl z-30',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Gaming glow accent line */}
      <div className="absolute inset-y-0 right-0 w-px bg-gradient-to-b from-transparent via-primary/30 to-transparent" />

      {/* Logo with enhanced styling */}
      <div className="flex h-16 items-center justify-between px-6 border-b border-border/30">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-primary shadow-glow-primary" />
            <span className="text-xl font-bold text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Donkey Betz
            </span>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 rounded-lg mx-auto bg-gradient-primary shadow-glow-primary" />
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              clsx(
                'group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 relative',
                isActive
                  ? 'bg-primary/10 text-primary border border-primary/30 shadow-glow-subtle backdrop-blur-sm'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/60 hover:border hover:border-border/60 backdrop-blur-sm'
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive ? (
                  <item.iconActive className="h-5 w-5 flex-shrink-0" />
                ) : (
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                )}
                {!collapsed && (
                  <>
                    <span className="flex-1">{item.name}</span>
                    {item.badge && (
                      <span className="px-2 py-0.5 text-xs font-bold bg-gradient-primary text-white rounded-full animate-pulse shadow-glow-primary">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User info and Logout */}
      <div className="px-3 py-4 space-y-2 border-t border-border/30">
        {!collapsed && (
          <div className="px-3 py-2 text-xs text-muted-foreground">
            Signed in as <span className="text-primary font-medium">{user?.username}</span>
          </div>
        )}

        <button
          onClick={handleLogout}
          className="w-full group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 text-muted-foreground hover:text-destructive hover:bg-destructive/10 backdrop-blur-sm border border-transparent hover:border-destructive/30 hover:shadow-glow-error"
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span className="flex-1 text-left">Sign Out</span>}
        </button>
      </div>

      {/* Collapse toggle with gaming enhancement */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-20 z-40 flex h-6 w-6 items-center justify-center rounded-full bg-card backdrop-blur-md border border-border/60 text-muted-foreground hover:text-primary hover:border-primary/60 hover:shadow-glow-subtle transition-all duration-200"
      >
        {collapsed ? (
          <ChevronRightIcon className="h-3 w-3" />
        ) : (
          <ChevronLeftIcon className="h-3 w-3" />
        )}
      </button>
    </div>
  );
}