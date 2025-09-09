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
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;
  initAuth: () => void;
}

// Default user for development (testuser account)
const defaultUser: User = {
  id: '2',
  username: 'testuser',
  email: 'testuser@example.com',
  credits: 1000,
  subscription: 'premium'
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null, // Start with no user
      token: null, // Start with no token
      isAuthenticated: false, // Start unauthenticated
      isLoading: false,

      setUser: (user) => {
        console.log('🔐 AuthStore: setUser called with:', user);
        Logger.state('AuthStore', 'Set user', { userId: user.id, username: user.username });
        set({ user, isAuthenticated: true });
        console.log('🔐 AuthStore: User set, isAuthenticated: true');
      },
      
      setToken: (token) => {
        console.log('🔐 AuthStore: setToken called with:', token);
        Logger.state('AuthStore', 'Set token', { tokenPrefix: token.substring(0, 10) + '...' });
        localStorage.setItem('authToken', token);
        set({ token, isAuthenticated: true });
        console.log('🔐 AuthStore: Token stored in localStorage and state');
      },
      
      logout: () => {
        console.log('🔐 AuthStore: logout called');
        Logger.state('AuthStore', 'User logout');
        localStorage.removeItem('authToken');
        localStorage.removeItem('auth-storage');
        set({ user: null, token: null, isAuthenticated: false });
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
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);