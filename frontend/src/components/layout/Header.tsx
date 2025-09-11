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
    <header 
      className="h-16 flex items-center justify-between px-6 backdrop-blur-xl relative"
      style={{
        background: 'var(--gaming-bg-secondary)',
        borderBottom: '1px solid var(--gaming-border)',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
      }}
    >
      {/* Gaming header glow effect */}
      <div 
        className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, var(--gaming-neon-cyan) 50%, transparent 100%)',
          height: '1px',
          top: 0
        }}
      />
      {/* Gaming Search */}
      <div className="flex-1 max-w-xl">
        <div className="relative">
          <MagnifyingGlassIcon 
            className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 transition-colors duration-200" 
            style={{ color: 'var(--gaming-text-muted)' }}
          />
          <input
            type="text"
            placeholder="Search or press ⌘K..."
            className="input pl-10 pr-4 py-2 w-full gaming-search"
            style={{
              background: 'var(--gaming-bg-tertiary)',
              border: '1px solid var(--gaming-border)',
              color: 'var(--gaming-text-primary)',
              borderRadius: '12px'
            }}
            onFocus={(e) => {
              setShowSearch(true);
              e.target.style.borderColor = 'var(--gaming-neon-cyan)';
              e.target.style.boxShadow = 'var(--gaming-glow-subtle)';
            }}
            onBlur={(e) => {
              setShowSearch(false);
              e.target.style.borderColor = 'var(--gaming-border)';
              e.target.style.boxShadow = 'none';
            }}
          />
          {showSearch && (
            <div 
              className="absolute inset-x-0 top-full mt-2 rounded-lg p-4 z-50 backdrop-blur-xl"
              style={{
                background: 'var(--gaming-bg-elevated)',
                border: '1px solid var(--gaming-border)',
                boxShadow: 'var(--gaming-glow-medium)'
              }}
            >
              <p className="text-sm" style={{ color: 'var(--gaming-text-muted)' }}>
                Start typing to search...
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Gaming Right side */}
      <div className="flex items-center gap-4">
        {/* Gaming Credits */}
        <div 
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg backdrop-blur-xl"
          style={{
            background: 'var(--gaming-bg-tertiary)',
            border: '1px solid var(--gaming-border)'
          }}
        >
          <span className="text-sm" style={{ color: 'var(--gaming-text-muted)' }}>Credits:</span>
          <span 
            className="text-sm font-semibold font-mono"
            style={{ color: 'var(--gaming-neon-green)' }}
          >
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

        {/* Gaming Notifications */}
        <button 
          className="relative p-2 transition-all duration-200 rounded-lg"
          style={{ color: 'var(--gaming-text-muted)' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--gaming-neon-cyan)';
            e.currentTarget.style.background = 'rgba(0, 255, 255, 0.05)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--gaming-text-muted)';
            e.currentTarget.style.background = 'transparent';
          }}
        >
          <BellIcon className="h-5 w-5" />
          <span 
            className="absolute top-1 right-1 h-2 w-2 rounded-full animate-pulse"
            style={{ background: 'var(--gaming-neon-pink)' }}
          />
        </button>

        {/* Gaming User menu */}
        <button 
          className="flex items-center gap-2 p-1.5 rounded-lg transition-all duration-200"
          style={{ color: 'var(--gaming-text-muted)' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(0, 255, 255, 0.05)';
            e.currentTarget.style.color = 'var(--gaming-text-primary)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = 'var(--gaming-text-muted)';
          }}
        >
          <UserCircleIcon className="h-6 w-6" />
          <span className="text-sm hidden sm:block">
            {user?.username || 'User'}
          </span>
        </button>
      </div>
    </header>
  );
}