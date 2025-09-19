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
    <header className="h-16 flex items-center justify-between px-6 bg-card/95 backdrop-blur-md border-b border-border/50 shadow-dark-lg relative z-20">
      {/* Gaming glow accent line */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

      {/* Search */}
      <div className="flex-1 max-w-xl">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <input
            type="text"
            placeholder="Search or press ⌘K..."
            className="input pl-10 pr-4 py-2 w-full bg-background/60 backdrop-blur-sm border-border/60 focus:border-primary/60 focus:ring-2 focus:ring-primary/20 transition-all duration-200 group"
            onFocus={() => setShowSearch(true)}
            onBlur={() => setShowSearch(false)}
          />
          {showSearch && (
            <div className="absolute inset-x-0 top-full mt-2 rounded-lg p-4 z-50 glass border border-border/60 shadow-dark-xl animate-slide-down">
              <p className="text-sm text-muted-foreground">
                Start typing to search...
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Credits with gaming styling */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/80 backdrop-blur-sm border border-border/60 hover:border-primary/30 transition-all duration-200">
          <span className="text-sm text-muted-foreground">Credits:</span>
          <span className="text-sm font-semibold font-mono text-gradient bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            {user?.credits || '∞'}
          </span>
        </div>

        {/* Quick actions with enhanced styling */}
        <Button
          variant="secondary"
          size="sm"
          onClick={toggleInsights}
          className="mr-2 bg-secondary/20 backdrop-blur-sm border-secondary/30 hover:border-secondary/60 hover:bg-secondary/30 transition-all duration-200"
        >
          <SparklesIcon className="h-4 w-4" />
          Style Memory
        </Button>

        <Button
          variant="primary"
          size="sm"
          className="bg-gradient-primary hover:shadow-glow-primary transition-all duration-200"
        >
          Generate
        </Button>

        {/* Notifications with gaming glow */}
        <button className="relative p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent/60 backdrop-blur-sm transition-all duration-200 group">
          <BellIcon className="h-5 w-5 group-hover:drop-shadow-glow-cyan transition-all duration-200" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-accent-rose-500 rounded-full animate-pulse shadow-glow-error" />
        </button>

        {/* User menu with premium styling */}
        <button className="flex items-center gap-2 p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent/60 backdrop-blur-sm transition-all duration-200 group">
          <UserCircleIcon className="h-6 w-6 group-hover:drop-shadow-glow-cyan transition-all duration-200" />
          <span className="text-sm hidden sm:block font-medium">
            {user?.username || 'User'}
          </span>
        </button>
      </div>
    </header>
  );
}