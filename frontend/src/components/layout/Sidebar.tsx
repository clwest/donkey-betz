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
  CalculatorIcon,
  CircleStackIcon,
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
  CalculatorIcon as CalculatorIconSolid,
  CircleStackIcon as CircleStackIconSolid,
} from '@heroicons/react/24/solid';
import clsx from 'clsx';
import { useAuthStore } from '../../store/authStore';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, iconActive: HomeIconSolid },
  { name: 'Workflows', href: '/workflows', icon: CpuChipIcon, iconActive: CpuChipIconSolid, badge: 'NEW' },
  { name: 'Multi-Agent Workflows', href: '/workflows-multi', icon: UserGroupIcon, iconActive: UserGroupIconSolid, badge: 'NEW' },
  { name: 'Agent Orchestra', href: '/agent-orchestra', icon: UserGroupIcon, iconActive: UserGroupIconSolid },
  { name: 'Orchestra (NEW)', href: '/orchestra', icon: CpuChipIcon, iconActive: CpuChipIconSolid, badge: 'NEW' },
  { name: 'Sports Betting', href: '/betting', icon: ChartBarIcon, iconActive: ChartBarIconSolid },
  { name: 'Odds Calculator', href: '/odds', icon: CalculatorIcon, iconActive: CalculatorIconSolid },
  { name: 'Creation Studio', href: '/studio', icon: SparklesIcon, iconActive: SparklesIconSolid },
  { name: 'Content Library', href: '/gallery', icon: PhotoIcon, iconActive: PhotoIconSolid },
  // { name: 'Characters', href: '/character', icon: UserGroupIcon, iconActive: UserGroupIconSolid, badge: 'NEW' }, // Hidden - on backburner
  { name: 'Campaigns', href: '/campaigns', icon: MegaphoneIcon, iconActive: MegaphoneIconSolid },
  { name: 'eBooks', href: '/ebooks', icon: BookOpenIcon, iconActive: BookOpenIconSolid },
  { name: 'Voice', href: '/voice', icon: MicrophoneIcon, iconActive: MicrophoneIconSolid },
  { name: 'Research', href: '/research', icon: AcademicCapIcon, iconActive: AcademicCapIconSolid },
  { name: 'My Knowledge', href: '/knowledge', icon: CloudArrowUpIcon, iconActive: CloudArrowUpIconSolid, badge: 'NEW' },
  { name: 'Agent Registry', href: '/agent-registry', icon: CircleStackIcon, iconActive: CircleStackIconSolid, badge: 'NEW' },
  { name: 'Prompt Diagnostics', href: '/prompt-diagnostics', icon: BeakerIcon, iconActive: BeakerIconSolid, badge: 'NEW' },
  { name: 'Feedback', href: '/feedback', icon: ChartBarIcon, iconActive: ChartBarIconSolid, badge: 'NEW' },
  { name: 'AI Settings', href: '/ai-settings', icon: Cog6ToothIcon, iconActive: Cog6ToothIconSolid },
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
        'relative flex flex-col glass-dark border-r border-white/5 transition-all duration-300',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between px-6">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg" />
            <span className="text-xl font-bold text-gradient">Donkey Betz</span>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 bg-gradient-primary rounded-lg mx-auto" />
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
                'group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200',
                isActive
                  ? 'bg-primary-500/20 text-white'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
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
                      <span className="px-2 py-0.5 text-xs font-bold text-white bg-gradient-primary rounded-full">
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

      {/* Profile and Logout */}
      <div className="px-3 py-4 border-t border-white/5 space-y-2">
        <NavLink
          to="/profile"
          className={({ isActive }) =>
            clsx(
              'group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200',
              isActive
                ? 'bg-primary-500/20 text-white'
                : 'text-gray-400 hover:bg-white/5 hover:text-white'
            )
          }
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

        {/* User info and logout */}
        {!collapsed && (
          <div className="px-3 py-2 text-xs text-gray-500">
            Signed in as <span className="text-gray-300">{user?.username}</span>
          </div>
        )}
        
        <button
          onClick={handleLogout}
          className="w-full group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 text-gray-400 hover:bg-red-500/10 hover:text-red-400"
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span className="flex-1 text-left">Sign Out</span>}
        </button>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-20 z-10 flex h-6 w-6 items-center justify-center rounded-full bg-dark-800 border border-dark-700 text-gray-400 hover:text-white transition-colors"
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