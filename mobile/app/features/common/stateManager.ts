/**
 * Unified State Management with AsyncStorage Persistence
 * Handles offline/online state transitions and persistent storage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { storage } from './apiService';

// State types
export interface AppState {
  connectivity: {
    donkeyBetz: {
      apiStatus: 'unknown' | 'healthy' | 'unhealthy' | 'error';
      wsStatus: 'idle' | 'connecting' | 'open' | 'pong' | 'closed' | 'error';
      lastChecked: string | null;
      lastError: string | null;
    };
    dbao: {
      apiStatus: 'unknown' | 'healthy' | 'unhealthy' | 'error';
      wsStatus: 'idle' | 'connecting' | 'open' | 'pong' | 'closed' | 'error';
      lastChecked: string | null;
      lastError: string | null;
    };
    isOnline: boolean;
    lastGlobalCheck: string | null;
  };
  userPreferences: {
    autoConnectWebSockets: boolean;
    enablePushNotifications: boolean;
    offlineMode: boolean;
    debugMode: boolean;
  };
  sessionData: {
    sessionId: string | null;
    startTime: string | null;
    lastActivity: string | null;
  };
  cache: {
    apiResponses: Record<string, any>;
    lastCleared: string | null;
  };
}

// Default state
const defaultState: AppState = {
  connectivity: {
    donkeyBetz: {
      apiStatus: 'unknown',
      wsStatus: 'idle',
      lastChecked: null,
      lastError: null,
    },
    dbao: {
      apiStatus: 'unknown', 
      wsStatus: 'idle',
      lastChecked: null,
      lastError: null,
    },
    isOnline: true,
    lastGlobalCheck: null,
  },
  userPreferences: {
    autoConnectWebSockets: true,
    enablePushNotifications: true,
    offlineMode: false,
    debugMode: __DEV__,
  },
  sessionData: {
    sessionId: null,
    startTime: null,
    lastActivity: null,
  },
  cache: {
    apiResponses: {},
    lastCleared: null,
  },
};

// Storage keys
const STORAGE_KEYS = {
  APP_STATE: 'app_state',
  USER_PREFERENCES: 'user_preferences',
  SESSION_DATA: 'session_data',
  CACHE_DATA: 'cache_data',
  CONNECTIVITY_STATE: 'connectivity_state',
} as const;

// Event emitter for state changes
class StateEventEmitter {
  private listeners = new Map<string, Set<Function>>();

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      const eventListeners = this.listeners.get(event);
      if (eventListeners) {
        eventListeners.delete(callback);
      }
    };
  }

  emit(event: string, data?: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in state event listener for ${event}:`, error);
        }
      });
    }
  }
}

// State Manager class
class StateManager {
  private state: AppState = { ...defaultState };
  private eventEmitter = new StateEventEmitter();
  private isInitialized = false;
  private saveTimeout: NodeJS.Timeout | null = null;

  constructor() {
    this.initialize();
  }

  private async initialize() {
    try {
      await this.loadState();
      this.setupSession();
      this.isInitialized = true;
      this.eventEmitter.emit('initialized', this.state);
    } catch (error) {
      console.error('Failed to initialize state manager:', error);
      this.isInitialized = true; // Continue with default state
    }
  }

  private async loadState() {
    try {
      // Load different parts of the state separately for better performance
      const [
        connectivityState,
        userPreferences,
        sessionData,
        cacheData,
      ] = await Promise.all([
        storage.getItem<AppState['connectivity']>(STORAGE_KEYS.CONNECTIVITY_STATE),
        storage.getItem<AppState['userPreferences']>(STORAGE_KEYS.USER_PREFERENCES),
        storage.getItem<AppState['sessionData']>(STORAGE_KEYS.SESSION_DATA),
        storage.getItem<AppState['cache']>(STORAGE_KEYS.CACHE_DATA),
      ]);

      // Merge loaded state with defaults
      this.state = {
        ...defaultState,
        connectivity: connectivityState || defaultState.connectivity,
        userPreferences: { ...defaultState.userPreferences, ...userPreferences },
        sessionData: sessionData || defaultState.sessionData,
        cache: cacheData || defaultState.cache,
      };

      console.log('[StateManager] State loaded successfully');
    } catch (error) {
      console.error('[StateManager] Failed to load state:', error);
      this.state = { ...defaultState };
    }
  }

  private setupSession() {
    const now = new Date().toISOString();
    
    // Create new session if none exists
    if (!this.state.sessionData.sessionId) {
      this.state.sessionData = {
        sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        startTime: now,
        lastActivity: now,
      };
    } else {
      // Update last activity
      this.state.sessionData.lastActivity = now;
    }

    this.scheduleSave();
  }

  private scheduleSave() {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    this.saveTimeout = setTimeout(() => {
      this.saveState();
    }, 1000); // Debounce saves by 1 second
  }

  private async saveState() {
    try {
      // Save different parts separately for better performance and error isolation
      await Promise.all([
        storage.setItem(STORAGE_KEYS.CONNECTIVITY_STATE, this.state.connectivity),
        storage.setItem(STORAGE_KEYS.USER_PREFERENCES, this.state.userPreferences),
        storage.setItem(STORAGE_KEYS.SESSION_DATA, this.state.sessionData),
        storage.setItem(STORAGE_KEYS.CACHE_DATA, this.state.cache),
      ]);

      console.log('[StateManager] State saved successfully');
    } catch (error) {
      console.error('[StateManager] Failed to save state:', error);
    }
  }

  // Public methods
  public getState(): AppState {
    return { ...this.state };
  }

  public async waitForInitialization(): Promise<void> {
    if (this.isInitialized) return;
    
    return new Promise((resolve) => {
      const unsubscribe = this.eventEmitter.on('initialized', () => {
        unsubscribe();
        resolve();
      });
    });
  }

  // Connectivity state management
  public updateDonkeyBetzConnectivity(updates: Partial<AppState['connectivity']['donkeyBetz']>) {
    this.state.connectivity.donkeyBetz = {
      ...this.state.connectivity.donkeyBetz,
      ...updates,
      lastChecked: new Date().toISOString(),
    };
    this.scheduleSave();
    this.eventEmitter.emit('connectivity:donkeyBetz', this.state.connectivity.donkeyBetz);
    this.eventEmitter.emit('connectivity:changed', this.state.connectivity);
  }

  public updateDBAOConnectivity(updates: Partial<AppState['connectivity']['dbao']>) {
    this.state.connectivity.dbao = {
      ...this.state.connectivity.dbao,
      ...updates,
      lastChecked: new Date().toISOString(),
    };
    this.scheduleSave();
    this.eventEmitter.emit('connectivity:dbao', this.state.connectivity.dbao);
    this.eventEmitter.emit('connectivity:changed', this.state.connectivity);
  }

  public setOnlineStatus(isOnline: boolean) {
    this.state.connectivity.isOnline = isOnline;
    this.state.connectivity.lastGlobalCheck = new Date().toISOString();
    this.scheduleSave();
    this.eventEmitter.emit('connectivity:online', isOnline);
    this.eventEmitter.emit('connectivity:changed', this.state.connectivity);
  }

  // User preferences
  public updateUserPreferences(updates: Partial<AppState['userPreferences']>) {
    this.state.userPreferences = {
      ...this.state.userPreferences,
      ...updates,
    };
    this.scheduleSave();
    this.eventEmitter.emit('preferences:changed', this.state.userPreferences);
  }

  // Cache management
  public setCacheItem(key: string, value: any, ttl?: number) {
    const item = {
      value,
      timestamp: Date.now(),
      ttl: ttl || 5 * 60 * 1000, // Default 5 minutes
    };

    this.state.cache.apiResponses[key] = item;
    this.scheduleSave();
  }

  public getCacheItem<T>(key: string): T | null {
    const item = this.state.cache.apiResponses[key];
    if (!item) return null;

    // Check if item has expired
    if (Date.now() > item.timestamp + item.ttl) {
      delete this.state.cache.apiResponses[key];
      this.scheduleSave();
      return null;
    }

    return item.value;
  }

  public clearCache() {
    this.state.cache.apiResponses = {};
    this.state.cache.lastCleared = new Date().toISOString();
    this.scheduleSave();
    this.eventEmitter.emit('cache:cleared');
  }

  // Session management
  public updateActivity() {
    this.state.sessionData.lastActivity = new Date().toISOString();
    // Don't save immediately for activity updates to avoid too many writes
  }

  // Event subscription
  public on(event: string, callback: Function) {
    return this.eventEmitter.on(event, callback);
  }

  // Utility methods
  public getConnectivitySummary() {
    return {
      overall: this.isOverallHealthy() ? 'healthy' : 'degraded',
      donkeyBetz: this.state.connectivity.donkeyBetz,
      dbao: this.state.connectivity.dbao,
      isOnline: this.state.connectivity.isOnline,
    };
  }

  private isOverallHealthy(): boolean {
    const { donkeyBetz, dbao, isOnline } = this.state.connectivity;
    return isOnline && 
           (donkeyBetz.apiStatus === 'healthy' || donkeyBetz.apiStatus === 'unknown') &&
           (dbao.apiStatus === 'healthy' || dbao.apiStatus === 'unknown');
  }

  // Debug methods
  public debugLog() {
    if (this.state.userPreferences.debugMode) {
      console.log('[StateManager] Current State:', this.state);
    }
  }

  public async exportState(): Promise<string> {
    return JSON.stringify(this.state, null, 2);
  }

  public async importState(stateJson: string): Promise<boolean> {
    try {
      const importedState = JSON.parse(stateJson);
      this.state = { ...defaultState, ...importedState };
      await this.saveState();
      this.eventEmitter.emit('state:imported', this.state);
      return true;
    } catch (error) {
      console.error('[StateManager] Failed to import state:', error);
      return false;
    }
  }

  // Cleanup
  public async clearAllData() {
    try {
      await Promise.all([
        AsyncStorage.removeItem(STORAGE_KEYS.CONNECTIVITY_STATE),
        AsyncStorage.removeItem(STORAGE_KEYS.USER_PREFERENCES),
        AsyncStorage.removeItem(STORAGE_KEYS.SESSION_DATA),
        AsyncStorage.removeItem(STORAGE_KEYS.CACHE_DATA),
      ]);

      this.state = { ...defaultState };
      this.setupSession();
      this.eventEmitter.emit('state:reset', this.state);
      
      return true;
    } catch (error) {
      console.error('[StateManager] Failed to clear data:', error);
      return false;
    }
  }
}

// Export singleton instance
export const stateManager = new StateManager();

// Export hooks and utilities
export const useStateManager = () => stateManager;

// Event constants
export const STATE_EVENTS = {
  INITIALIZED: 'initialized',
  CONNECTIVITY_CHANGED: 'connectivity:changed',
  DONKEY_BETZ_CONNECTIVITY: 'connectivity:donkeyBetz',
  DBAO_CONNECTIVITY: 'connectivity:dbao',
  ONLINE_STATUS: 'connectivity:online',
  PREFERENCES_CHANGED: 'preferences:changed',
  CACHE_CLEARED: 'cache:cleared',
  STATE_IMPORTED: 'state:imported',
  STATE_RESET: 'state:reset',
} as const;

export default stateManager;