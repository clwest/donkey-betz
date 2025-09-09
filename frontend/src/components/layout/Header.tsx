import { MagnifyingGlassIcon, BellIcon, UserCircleIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { useAuthStore } from '../../store/authStore';
import { useStyleMemoryStore } from '../../store/styleMemoryStore';
import { useState } from 'react';
import { Button } from '../common/Button';

export function Header() {
  const [showSearch, setShowSearch] = useState(false);
  const { user } = useAuthStore();
  const { toggleInsights } = useStyleMemoryStore();

  return (
    <header className="h-16 glass-dark border-b border-white/5 flex items-center justify-between px-6">
      {/* Search */}
      <div className="flex-1 max-w-xl">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search or press ⌘K..."
            className="input pl-10 pr-4 py-2 w-full"
            onFocus={() => setShowSearch(true)}
            onBlur={() => setShowSearch(false)}
          />
          {showSearch && (
            <div className="absolute inset-x-0 top-full mt-2 glass rounded-lg p-4 z-50">
              <p className="text-sm text-gray-400">Start typing to search...</p>
            </div>
          )}
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Credits */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 glass rounded-lg">
          <span className="text-sm text-gray-400">Credits:</span>
          <span className="text-sm font-semibold text-white">
            {user?.credits || '∞'}
          </span>
        </div>

        {/* Quick actions */}
        <Button 
          variant="secondary" 
          size="sm"
          onClick={toggleInsights}
          className="mr-2"
        >
          <SparklesIcon className="h-4 w-4" />
          Style Memory
        </Button>
        
        <Button variant="primary" size="sm">
          Generate
        </Button>

        {/* Notifications */}
        <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
          <BellIcon className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full" />
        </button>

        {/* User menu */}
        <button className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 transition-colors">
          <UserCircleIcon className="h-6 w-6 text-gray-400" />
          <span className="text-sm text-gray-300 hidden sm:block">
            {user?.username || 'User'}
          </span>
        </button>
      </div>
    </header>
  );
}