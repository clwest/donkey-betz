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
  { name: 'Opportunities Hub', href: '/opportunities', icon: CurrencyDollarIcon, iconActive: CurrencyDollarIconSolid, badge: '🚀 UNIFIED' },
  { name: 'Profile', href: '/profile', icon: UserCircleIcon, iconActive: UserCircleIconSolid },
  { name: 'Revenue Command', href: '/revenue', icon: BanknotesIcon, iconActive: BanknotesIconSolid, badge: '💰 TRACK' },
  { name: 'Command & Control', href: '/control-center', icon: BeakerIcon, iconActive: BeakerIconSolid, badge: '🎯 SYSTEM' },
  { name: 'Neural Orchestra', href: '/neural-orchestra', icon: CpuChipIcon, iconActive: CpuChipIconSolid, badge: 'LIVE' },
  { name: 'Agent Hub', href: '/agent-hub', icon: UserGroupIcon, iconActive: UserGroupIconSolid },
  { name: 'Workflow Engine', href: '/workflows', icon: CircleStackIcon, iconActive: CircleStackIconSolid },
  { name: 'Content Studio', href: '/studio', icon: SparklesIcon, iconActive: SparklesIconSolid },
  { name: 'Media Vault', href: '/gallery', icon: PhotoIcon, iconActive: PhotoIconSolid },
  // { name: 'Characters', href: '/character', icon: UserGroupIcon, iconActive: UserGroupIconSolid, badge: 'NEW' }, // Hidden - on backburner
  { name: 'Campaign Manager', href: '/campaigns', icon: MegaphoneIcon, iconActive: MegaphoneIconSolid },
  { name: 'Library', href: '/ebooks', icon: BookOpenIcon, iconActive: BookOpenIconSolid },
  { name: 'Voice Studio', href: '/voice', icon: MicrophoneIcon, iconActive: MicrophoneIconSolid },
  { name: 'AI Config', href: '/ai-settings', icon: Cog6ToothIcon, iconActive: Cog6ToothIconSolid },
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
        'relative flex flex-col transition-all duration-300',
        collapsed ? 'w-20' : 'w-64'
      )}
      style={{
        background: 'var(--gaming-bg-secondary)',
        borderRight: '1px solid var(--gaming-border)',
        backdropFilter: 'blur(20px)'
      }}
    >
      {/* Gaming Logo */}
      <div className="flex h-16 items-center justify-between px-6">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg relative overflow-hidden" 
                 style={{ background: 'var(--gaming-gradient-primary)' }}>
              <div className="absolute inset-0 animate-pulse" 
                   style={{ boxShadow: 'var(--gaming-glow-primary)' }}></div>
            </div>
            <span className="text-xl font-bold text-gradient gaming-logo-text">Donkey Betz</span>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 rounded-lg mx-auto relative overflow-hidden" 
               style={{ background: 'var(--gaming-gradient-primary)' }}>
            <div className="absolute inset-0 animate-pulse" 
                 style={{ boxShadow: 'var(--gaming-glow-primary)' }}></div>
          </div>
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
                'group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 relative overflow-hidden',
                isActive
                  ? 'text-white gaming-nav-active'
                  : 'hover:text-white gaming-nav-item'
              )
            }
            style={({ isActive }) => ({
              background: isActive 
                ? 'rgba(0, 255, 255, 0.1)' 
                : 'transparent',
              borderLeft: isActive 
                ? '3px solid var(--gaming-neon-cyan)' 
                : '3px solid transparent',
              color: isActive 
                ? 'var(--gaming-text-primary)' 
                : 'var(--gaming-text-secondary)'
            })}
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
                      <span className="px-2 py-0.5 text-xs font-bold text-white rounded-full gaming-badge" 
                            style={{ 
                              background: 'var(--gaming-gradient-neon)',
                              boxShadow: 'var(--gaming-glow-subtle)',
                              animation: 'pulse 2s ease-in-out infinite'
                            }}>
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

      {/* Gaming Profile and Logout */}
      <div className="px-3 py-4 space-y-2" style={{ borderTop: '1px solid var(--gaming-border)' }}>
        <NavLink
          to="/profile"
          className={({ isActive }) =>
            clsx(
              'group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200',
              isActive
                ? 'text-white'
                : 'gaming-nav-item'
            )
          }
          style={({ isActive }) => ({
            background: isActive 
              ? 'rgba(0, 255, 255, 0.1)' 
              : 'transparent',
            borderLeft: isActive 
              ? '3px solid var(--gaming-neon-cyan)' 
              : '3px solid transparent',
            color: isActive 
              ? 'var(--gaming-text-primary)' 
              : 'var(--gaming-text-secondary)'
          })}
        >
          {({ isActive }) => (
            <>
              {isActive ? (
                <UserCircleIconSolid className="h-5 w-5 flex-shrink-0" />
              ) : (
                <UserCircleIcon className="h-5 w-5 flex-shrink-0" />
              )}
              {!collapsed && <span className="flex-1">Profile</span>}
            </>
          )}
        </NavLink>

        {/* Gaming User info and logout */}
        {!collapsed && (
          <div className="px-3 py-2 text-xs" style={{ color: 'var(--gaming-text-muted)' }}>
            Signed in as <span className="text-neon-cyan">{user?.username}</span>
          </div>
        )}
        
        <button
          onClick={handleLogout}
          className="w-full group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 gaming-logout-btn"
          style={{
            color: 'var(--gaming-text-muted)',
            border: '1px solid transparent'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 20, 147, 0.1)';
            e.currentTarget.style.borderColor = 'var(--gaming-neon-pink)';
            e.currentTarget.style.color = 'var(--gaming-neon-pink)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.borderColor = 'transparent';
            e.currentTarget.style.color = 'var(--gaming-text-muted)';
          }}
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span className="flex-1 text-left">Sign Out</span>}
        </button>
      </div>

      {/* Gaming Collapse toggle */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-20 z-10 flex h-6 w-6 items-center justify-center rounded-full transition-all duration-200"
        style={{
          background: 'var(--gaming-bg-elevated)',
          border: '1px solid var(--gaming-border)',
          color: 'var(--gaming-text-muted)'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = 'var(--gaming-neon-cyan)';
          e.currentTarget.style.color = 'var(--gaming-neon-cyan)';
          e.currentTarget.style.boxShadow = 'var(--gaming-glow-subtle)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'var(--gaming-border)';
          e.currentTarget.style.color = 'var(--gaming-text-muted)';
          e.currentTarget.style.boxShadow = 'none';
        }}
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