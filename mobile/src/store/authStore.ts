import { create } from 'zustand';
import { authService } from '../services/authService';
import { apiClient } from '../services/apiClient';
import { User } from '../types/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  checkAuth: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
  uploadAvatar: (imageFile: any) => Promise<void>;
  deleteAvatar: () => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  login: async (username: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await authService.login({
        username,
        password,
      });
      
      set({
        token: response.token,
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      // console.error('Login error:', error);
      set({ 
        isLoading: false, 
        error: error.userMessage || error.message || 'Login failed' 
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      set({ isLoading: true });
      await authService.logout();
      
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      // console.error('Logout error:', error);
      // Clear local state even if server logout fails
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  },

  register: async (email: string, password: string, name: string) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await authService.register({
        username: email.split('@')[0],
        email,
        password,
        first_name: name,
      });
      
      set({
        token: response.token,
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      // console.error('Registration error:', error);
      set({ 
        isLoading: false, 
        error: error.userMessage || error.message || 'Registration failed' 
      });
      throw error;
    }
  },

  checkAuth: async () => {
    try {
      set({ isLoading: true });
      
      // Check if we have stored auth data
      const user = await authService.getCurrentUser();
      const token = apiClient.getAuthToken();
      
      if (token && user) {
        // Verify auth status with server
        const isValid = await authService.checkAuthStatus();
        
        if (isValid) {
          const updatedUser = await authService.getCurrentUser();
          set({
            token,
            user: updatedUser,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } else {
          set({ 
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      } else {
        set({ 
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      }
    } catch (error: any) {
      console.error('Auth check error:', error);
      set({ 
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  },

  updateUser: async (userData: Partial<User>) => {
    try {
      const updatedUser = await authService.updateProfile(userData);
      set({ user: updatedUser });
    } catch (error: any) {
      console.error('Update user error:', error);
      set({ error: error.userMessage || error.message || 'Update failed' });
      throw error;
    }
  },

  uploadAvatar: async (imageFile: any) => {
    try {
      const updatedUser = await authService.uploadAvatar(imageFile);
      set({ user: updatedUser });
    } catch (error: any) {
      console.error('Upload avatar error:', error);
      set({ error: error.userMessage || error.message || 'Avatar upload failed' });
      throw error;
    }
  },

  deleteAvatar: async () => {
    try {
      const updatedUser = await authService.deleteAvatar();
      set({ user: updatedUser });
    } catch (error: any) {
      console.error('Delete avatar error:', error);
      set({ error: error.userMessage || error.message || 'Avatar deletion failed' });
      throw error;
    }
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    try {
      await authService.changePassword(currentPassword, newPassword);
    } catch (error: any) {
      console.error('Change password error:', error);
      set({ error: error.userMessage || error.message || 'Password change failed' });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));