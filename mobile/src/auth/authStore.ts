import { create } from 'zustand';
import type { AuthUser } from './tokenStore';
import {
  getToken,
  setToken,
  clearToken,
  getStoredUser,
  setStoredUser,
  clearStoredUser,
} from './tokenStore';
import { setOnUnauthorized } from '../api/http';
import * as authService from './authService';

// ── Types ────────────────────────────────────────────────────────────────────

export type AuthStatus = 'loading' | 'signedIn' | 'signedOut';

interface AuthState {
  status: AuthStatus;
  user: AuthUser | null;

  /** Restore session from secure store on app launch. */
  hydrate: () => Promise<void>;

  /** Sign in with username + password. Stores token + user. */
  signIn: (username: string, password: string) => Promise<void>;

  /** Sign out. Clears token + user from secure store. */
  signOut: () => Promise<void>;
}

// ── Store ────────────────────────────────────────────────────────────────────

export const useAuthStore = create<AuthState>((set, get) => {
  // Wire up 401 handler so the HTTP client can trigger sign-out
  setOnUnauthorized(() => {
    const { status } = get();
    if (status === 'signedIn') {
      get().signOut();
    }
  });

  return {
    status: 'loading',
    user: null,

    hydrate: async () => {
      try {
        const token = await getToken();
        const user = await getStoredUser();
        if (token && user) {
          // Validate the token is still good
          try {
            const result = await authService.validateToken(token);
            if (result.valid && result.user) {
              await setStoredUser(result.user);
              set({ status: 'signedIn', user: result.user });
              return;
            }
            // Explicit invalid token — sign out
          } catch {
            // Network/server error — trust cached token + user
            // so a Railway hiccup doesn't log everyone out
            set({ status: 'signedIn', user });
            return;
          }
        }
      } catch {
        // SecureStore read failed — fall through to signed out
      }
      await clearToken();
      await clearStoredUser();
      set({ status: 'signedOut', user: null });
    },

    signIn: async (username, password) => {
      const { token, user } = await authService.login(username, password);
      await setToken(token);
      await setStoredUser(user);
      set({ status: 'signedIn', user });
    },

    signOut: async () => {
      await authService.logout();
      await clearToken();
      await clearStoredUser();
      set({ status: 'signedOut', user: null });
    },
  };
});
