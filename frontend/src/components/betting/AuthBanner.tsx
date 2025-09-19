import React from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { useAuthStore } from '../../store/authStore';
import { 
  UserIcon, 
  Lock, 
  Sparkles,
  Zap 
} from 'lucide-react';

interface AuthBannerProps {
  className?: string;
}

export function AuthBanner({ className }: AuthBannerProps) {
  const { user, isAuthenticated, setUser, setToken } = useAuthStore();
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const quickLogin = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const data = await response.json();
      
      if (data.token) {
        const userData = {
          id: data.user.id || String(Math.random()),
          username: data.user.username,
          email: data.user.email,
          credits: data.user.credits || 1000,
          subscription: data.user.subscription || 'premium'
        };
        
        setUser(userData);
        setToken(data.token);
        localStorage.setItem('authToken', data.token);
      }
    } catch (err: any) {
      console.error('Quick login error:', err);
      setError('Login failed - using demo token for testing');
      // Fallback to development token
      localStorage.setItem('authToken', '993f8273f70877e23b5c7d2f92ed30562a089fe3');
      setUser({
        id: 'demo',
        username: 'Demo User',
        email: 'demo@example.com',
        credits: 1000,
        subscription: 'premium'
      });
      setToken('993f8273f70877e23b5c7d2f92ed30562a089fe3');
    } finally {
      setIsLoading(false);
    }
  };

  if (isAuthenticated && user) {
    return (
      <Card className={`bg-card bg-bg-card/20 border-bg-card ${className}`}>
        <div className="bg-card bg-card"></div>
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-bg-card rounded-full flex items-center justify-center">
              <UserIcon className="w-4 h-4 text-foreground" />
            </div>
            <div>
              <div className="font-bold text-sm bg-card">
                {user.username}
              </div>
              <div className="text-xs bg-card">
                Ready for AI Analysis
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-card text-xs">
              <Sparkles className="w-3 h-3 mr-1" />
              100+ AGENTS
            </Badge>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`bg-card bg-bg-card/20 border-bg-card ${className}`}>
      <div className="bg-card bg-card"></div>
      <div className="p-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 bg-bg-card rounded-full flex items-center justify-center">
            <Lock className="w-4 h-4 text-foreground" />
          </div>
          <div>
            <div className="font-bold text-sm bg-card">
              🚀 Unlock AI Betting Agents
            </div>
            <div className="text-xs bg-card">
              Login to access 100+ specialist betting agents
            </div>
          </div>
        </div>
        
        <div className="mb-3">
          <div className="text-xs bg-card mb-2">Quick Login:</div>
          <div className="grid grid-cols-3 gap-2">
            <Button
              onClick={() => quickLogin('testuser', 'testpass123')}
              disabled={isLoading}
              size="sm"
              className="bg-card text-xs"
            >
              <UserIcon className="w-3 h-3 mr-1" />
              Test
            </Button>
            
            <Button
              onClick={() => quickLogin('demo', 'demo123')}
              disabled={isLoading}
              size="sm"
              className="bg-card text-xs"
            >
              <Zap className="w-3 h-3 mr-1" />
              Demo
            </Button>
            
            <Button
              onClick={() => quickLogin('admin', 'admin123')}
              disabled={isLoading}
              size="sm"
              className="bg-card text-xs"
            >
              <Sparkles className="w-3 h-3 mr-1" />
              Admin
            </Button>
          </div>
        </div>

        {error && (
          <div className="text-xs text-bg-card bg-bg-card/10 p-2 rounded">
            {error}
          </div>
        )}
        
        {isLoading && (
          <div className="text-xs bg-card">
            🔐 Authenticating...
          </div>
        )}
        
        <div className="text-xs bg-card mt-2">
          💡 After login, you'll have access to Kelly Criterion calculators, odds analyzers, and betting recommendation engines!
        </div>
      </div>
    </Card>
  );
}