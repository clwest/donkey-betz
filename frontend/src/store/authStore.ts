import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Logger } from '../utils/logger';

interface User {
  id: string;
  username: string;
  email: string;
  credits?: number;
  subscription?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  rememberToken: string | null;
  rememberMe: boolean;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User) => void;
  setToken: (token: string, rememberMe?: boolean) => void;
  logout: () => void;
  initAuth: () => void;
  validateSession: () => Promise<boolean>;
}

// Default user for development (chris account)
const defaultUser: User = {
  id: '2',
  username: 'chris',
  email: 'chris@example.com',
  credits: 10000,
  subscription: 'premium'
};

// Check if we have auth in localStorage at initialization
const getInitialAuthState = () => {
  const token = localStorage.getItem('authToken');
  const storedState = localStorage.getItem('auth-storage');
  
  if (token && storedState) {
    try {
      const parsed = JSON.parse(storedState);
      const { user } = parsed.state || {};
      if (user) {
        return {
          user,
          token,
          isAuthenticated: true,
          isLoading: false
        };
      }
    } catch (e) {
      console.error('Failed to parse initial auth state:', e);
    }
  }
  
  // If no valid auth found, use chris user with actual token from database
  // Chris token: 993f8273f70877e23b5c7d2f92ed30562a089fe3
  const chrisToken = '993f8273f70877e23b5c7d2f92ed30562a089fe3';
  localStorage.setItem('authToken', chrisToken);
  
  return {
    user: defaultUser,
    token: chrisToken,
    rememberToken: null,
    rememberMe: false,
    isAuthenticated: true,
    isLoading: false
  };
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      ...getInitialAuthState(),

      setUser: (user) => {
        console.log('🔐 AuthStore: setUser called with:', user);
        Logger.state('AuthStore', 'Set user', { userId: user.id, username: user.username });
        set({ user, isAuthenticated: true });
        console.log('🔐 AuthStore: User set, isAuthenticated: true');
      },
      
      setToken: (token, rememberMe = false) => {
        console.log('🔐 AuthStore: setToken called with:', token, 'rememberMe:', rememberMe);
        Logger.state('AuthStore', 'Set token', { tokenPrefix: token.substring(0, 10) + '...', rememberMe });
        
        localStorage.setItem('authToken', token);
        
        if (rememberMe) {
          // Store remember me token for 30 days
          const rememberData = {
            token,
            expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
          };
          localStorage.setItem('rememberToken', JSON.stringify(rememberData));
        }
        
        set({ token, isAuthenticated: true, rememberMe });
        console.log('🔐 AuthStore: Token stored in localStorage and state');
      },
      
      logout: () => {
        console.log('🔐 AuthStore: logout called');
        Logger.state('AuthStore', 'User logout');
        localStorage.removeItem('authToken');
        localStorage.removeItem('auth-storage');
        localStorage.removeItem('rememberToken');
        set({ user: null, token: null, rememberToken: null, rememberMe: false, isAuthenticated: false });
        console.log('🔐 AuthStore: User logged out, storage cleared');
      },
      
      initAuth: () => {
        const token = localStorage.getItem('authToken');
        console.log('🔐 AuthStore: initAuth called, token in localStorage:', !!token);
        Logger.state('AuthStore', 'Initialize auth', { hasToken: !!token });
        
        // Only authenticate if we have a stored token and user
        if (token) {
          const storedState = localStorage.getItem('auth-storage');
          console.log('🔐 AuthStore: Found auth-storage:', !!storedState);
          if (storedState) {
            try {
              const parsed = JSON.parse(storedState);
              const { user } = parsed.state || {};
              console.log('🔐 AuthStore: Parsed user from storage:', user);
              if (user) {
                set({
                  token,
                  isAuthenticated: true,
                  user
                });
                console.log('🔐 AuthStore: Auth restored successfully');
                Logger.state('AuthStore', 'Auth restored from storage', { hasUser: true });
                return;
              }
            } catch (e) {
              console.error('🔐 AuthStore: Failed to parse stored auth:', e);
              Logger.state('AuthStore', 'Failed to parse stored auth');
            }
          }
        }
        
        // No valid auth found
        console.log('🔐 AuthStore: No valid auth found, setting to unauthenticated');
        set({
          token: null,
          isAuthenticated: false,
          user: null
        });
        Logger.state('AuthStore', 'No auth found', { hasUser: false });
      },
      
      validateSession: async () => {
        console.log('🔐 AuthStore: validateSession called');
        
        // Check for remember token first
        const rememberTokenStr = localStorage.getItem('rememberToken');
        if (rememberTokenStr) {
          try {
            const rememberData = JSON.parse(rememberTokenStr);
            const expires = new Date(rememberData.expires);
            
            if (expires > new Date()) {
              // Token is still valid
              console.log('🔐 AuthStore: Remember token is valid');
              
              // Validate with backend
              const response = await fetch('http://localhost:8000/api/auth/validate-token/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: rememberData.token })
              });
              
              const data = await response.json();
              
              if (data.valid) {
                set({
                  token: rememberData.token,
                  user: data.user,
                  isAuthenticated: true,
                  rememberMe: true
                });
                return true;
              }
            } else {
              // Token expired, remove it
              localStorage.removeItem('rememberToken');
            }
          } catch (e) {
            console.error('🔐 AuthStore: Failed to validate remember token:', e);
          }
        }
        
        // Check regular token
        const token = localStorage.getItem('authToken');
        if (token) {
          try {
            const response = await fetch('http://localhost:8000/api/auth/validate-token/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ token })
            });
            
            const data = await response.json();
            
            if (data.valid) {
              set({
                token,
                user: data.user,
                isAuthenticated: true
              });
              return true;
            }
          } catch (e) {
            console.error('🔐 AuthStore: Failed to validate token:', e);
          }
        }
        
        return false;
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);