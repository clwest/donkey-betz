import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Donkey Betz API Configuration for React Native
// First try environment variables, then fall back to localhost
const getApiBaseUrl = () => {
  const envUrl = process.env.EXPO_PUBLIC_DONKEY_BETZ_API_URL || 
                 process.env.EXPO_PUBLIC_API_URL ||
                 Constants.expoConfig?.extra?.EXPO_PUBLIC_DONKEY_BETZ_API_URL ||
                 Constants.expoConfig?.extra?.EXPO_PUBLIC_API_URL ||
                 Constants.manifest?.extra?.EXPO_PUBLIC_DONKEY_BETZ_API_URL;
  
  if (envUrl) {
    return envUrl;
  }
  
  // Fallback to localhost
  return Platform.select({
    ios: 'http://localhost:8001/api/v1', // localhost works in iOS simulator
    android: 'http://10.0.2.2:8001/api/v1', // Android emulator special alias for localhost
    web: 'http://localhost:8001/api/v1',
  });
};

const getMediaBaseUrl = () => {
  const envUrl = process.env.EXPO_PUBLIC_DONKEY_BETZ_API_URL || 
                 process.env.EXPO_PUBLIC_API_URL ||
                 Constants.expoConfig?.extra?.EXPO_PUBLIC_DONKEY_BETZ_API_URL ||
                 Constants.expoConfig?.extra?.EXPO_PUBLIC_API_URL ||
                 Constants.manifest?.extra?.EXPO_PUBLIC_DONKEY_BETZ_API_URL;
  
  if (envUrl) {
    // Remove /api/v1 or /api from the end for media URL
    return envUrl.replace(/\/api(\/v1)?$/, '');
  }
  
  // Fallback to localhost
  return Platform.select({
    ios: 'http://localhost:8001', // localhost works in iOS simulator
    android: 'http://10.0.2.2:8001', // Android emulator special alias for localhost
    web: 'http://localhost:8001',
  });
};

export const API_BASE_URL = getApiBaseUrl();
export const MEDIA_BASE_URL = getMediaBaseUrl();

// Debug logging for API URLs
console.log('[API Config] Environment check:', {
  envApiUrl: process.env.EXPO_PUBLIC_AI_STUDIO_API_URL,
  envDbaoUrl: process.env.EXPO_PUBLIC_DBAO_API_URL,
  envWsUrl: process.env.EXPO_PUBLIC_WS_URL,
  finalApiUrl: API_BASE_URL,
  finalMediaUrl: MEDIA_BASE_URL,
  platform: Platform.OS
});

export const DEFAULT_AUTH_TOKEN = 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502'; // testuser token

// Storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'authToken',
  USER: 'user',
  REFRESH_TOKEN: 'refreshToken',
  SETTINGS: 'settings',
  OFFLINE_QUEUE: 'offlineQueue',
  CACHED_DATA: 'cachedData',
};

// Helper functions for AsyncStorage
export const storage = {
  setItem: async (key: string, value: string) => {
    try {
      await AsyncStorage.setItem(key, value);
    } catch (error) {
      console.error('Storage setItem error:', error);
    }
  },

  getItem: async (key: string): Promise<string | null> => {
    try {
      return await AsyncStorage.getItem(key);
    } catch (error) {
      console.error('Storage getItem error:', error);
      return null;
    }
  },

  removeItem: async (key: string) => {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('Storage removeItem error:', error);
    }
  },

  setObject: async (key: string, value: object) => {
    try {
      // Skip if value is null or undefined
      if (value === null || value === undefined) {
        return;
      }
      await AsyncStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      // console.error('Storage setObject error:', error);
    }
  },

  getObject: async <T>(key: string): Promise<T | null> => {
    try {
      const value = await AsyncStorage.getItem(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error('Storage getObject error:', error);
      return null;
    }
  },
};

// Helper function to convert relative media URLs to absolute URLs
export const getFullMediaURL = (relativePath: string): string => {
  if (!relativePath) return '';
  if (relativePath.startsWith('http')) return relativePath; // Already absolute
  return `${MEDIA_BASE_URL}${relativePath}`;
};

// Network status helper for offline support
export const isOnline = (): Promise<boolean> => {
  return new Promise((resolve) => {
    if (Platform.OS === 'web') {
      resolve(navigator.onLine);
    } else {
      // For React Native, we'll use a simple fetch test to the API root
      fetch(`${API_BASE_URL}/`, { 
        method: 'GET',
        headers: {
          'Authorization': `Token ${DEFAULT_AUTH_TOKEN}`
        }
      })
        .then(() => resolve(true))
        .catch(() => resolve(false));
    }
  });
};