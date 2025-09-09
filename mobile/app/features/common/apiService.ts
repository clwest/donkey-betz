/**
 * Unified API Service for React Native
 * Handles both Donkey Betz and DBAO backend integrations
 */

import { Platform } from 'react-native';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Environment configuration
const getEnvironmentConfig = () => {
  // Donkey Betz (port 8001)
  const donkeyBetzApiUrl = process.env.EXPO_PUBLIC_DONKEY_BETZ_API_URL || 
                        Constants.expoConfig?.extra?.EXPO_PUBLIC_DONKEY_BETZ_API_URL ||
                        Platform.select({
                          ios: 'http://localhost:8001/api/v1',
                          android: 'http://10.0.2.2:8001/api/v1',
                          web: 'http://localhost:8001/api/v1',
                          default: 'http://localhost:8001/api/v1'
                        });

  // DBAO (now integrated on port 8001)
  const dbaoApiUrl = process.env.EXPO_PUBLIC_DBAO_API_URL || 
                     Constants.expoConfig?.extra?.EXPO_PUBLIC_DBAO_API_URL ||
                     Platform.select({
                       ios: 'http://localhost:8001',
                       android: 'http://10.0.2.2:8001',
                       web: 'http://localhost:8001',
                       default: 'http://localhost:8001'
                     });

  const authToken = process.env.EXPO_PUBLIC_AUTH_TOKEN || 
                   'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502';

  return {
    donkeyBetzApiUrl: donkeyBetzApiUrl?.replace(/\/+$/, ''), // Remove trailing slashes
    dbaoApiUrl: dbaoApiUrl?.replace(/\/+$/, ''), // Remove trailing slashes
    authToken,
  };
};

const config = getEnvironmentConfig();

// Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'error';
  message?: string;
  details?: any;
  timestamp: string;
}

// Storage utilities
const storage = {
  async getAuthToken(): Promise<string> {
    try {
      const token = await AsyncStorage.getItem('authToken') ||
                    await AsyncStorage.getItem('auth_token');
      return token || config.authToken;
    } catch (error) {
      console.warn('Failed to get auth token from storage:', error);
      return config.authToken;
    }
  },

  async setAuthToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('authToken', token);
    } catch (error) {
      console.error('Failed to save auth token:', error);
    }
  },

  async getItem<T>(key: string): Promise<T | null> {
    try {
      const value = await AsyncStorage.getItem(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error(`Failed to get ${key} from storage:`, error);
      return null;
    }
  },

  async setItem<T>(key: string, value: T): Promise<void> {
    try {
      await AsyncStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Failed to save ${key} to storage:`, error);
    }
  },
};

// Generic HTTP client
class HttpClient {
  constructor(
    private baseUrl: string,
    private defaultHeaders: Record<string, string> = {}
  ) {}

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = path.startsWith('http') ? path : `${this.baseUrl}${path}`;
    const authToken = await storage.getAuthToken();
    
    try {
      const response = await fetch(url, {
        timeout: 30000,
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${authToken}`,
          ...this.defaultHeaders,
          ...options.headers,
        },
      });

      const text = await response.text();
      let data: any;
      
      // Try to parse JSON, fallback to text
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = { message: text || response.statusText };
      }

      if (!response.ok) {
        return {
          success: false,
          error: data.message || data.detail || `HTTP ${response.status}: ${response.statusText}`,
          status: response.status,
          data,
        };
      }

      return {
        success: true,
        data,
        status: response.status,
      };
    } catch (error: any) {
      console.error(`API request failed for ${url}:`, error);
      return {
        success: false,
        error: error.message || 'Network request failed',
        status: 0,
      };
    }
  }

  async get<T>(path: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(path, { ...options, method: 'GET' });
  }

  async post<T>(
    path: string, 
    body?: any, 
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    return this.request<T>(path, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(
    path: string, 
    body?: any, 
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    return this.request<T>(path, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(path: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(path, { ...options, method: 'DELETE' });
  }

  async checkHealth(): Promise<HealthStatus> {
    const response = await this.get('/health/');
    return {
      status: response.success ? 'healthy' : 'unhealthy',
      message: response.success ? 'Service is healthy' : response.error,
      details: response.data,
      timestamp: new Date().toISOString(),
    };
  }
}

// Donkey Betz API client
export const donkeyBetzApi = new HttpClient(config.donkeyBetzApiUrl!, {
  'X-Client': 'React-Native',
  'X-Service': 'Donkey-Betz',
});

// DBAO API client  
export const dbaoApi = new HttpClient(config.dbaoApiUrl!, {
  'X-Client': 'React-Native',
  'X-Service': 'DBAO',
});

// Convenience functions for Donkey Betz
export const donkeyBetz = {
  // Content generation
  async generateContent(type: string, prompt: string, options?: any) {
    return donkeyBetzApi.post('/content/create/', {
      content_type: type,
      prompt,
      ...options,
    });
  },

  // Gallery
  async getGalleryItems(page = 1, pageSize = 20) {
    return donkeyBetzApi.get(`/gallery/?page=${page}&page_size=${pageSize}`);
  },

  // Voice services
  async transcribeAudio(audioFile: FormData) {
    return donkeyBetzApi.post('/voice/transcribe/', audioFile, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Dashboard stats
  async getDashboardStats() {
    return donkeyBetzApi.get('/dashboard/stats/');
  },

  // Health check
  async checkHealth(): Promise<HealthStatus> {
    return donkeyBetzApi.checkHealth();
  },
};

// Convenience functions for DBAO
export const dbao = {
  // Agent Orchestra
  async getAgents() {
    return dbaoApi.get('/api/agents/');
  },

  async createAgent(agentData: any) {
    return dbaoApi.post('/api/agents/', agentData);
  },

  // Sports Betting
  async getOdds(sport?: string, league?: string) {
    const params = new URLSearchParams();
    if (sport) params.append('sport', sport);
    if (league) params.append('league', league);
    return dbaoApi.get(`/api/odds/?${params.toString()}`);
  },

  async calculateKelly(odds: number, probability: number, bankroll: number) {
    return dbaoApi.post('/api/kelly/', {
      odds,
      probability,
      bankroll,
    });
  },

  // Health check
  async checkHealth(): Promise<HealthStatus> {
    return dbaoApi.checkHealth();
  },
};

// Unified health monitoring
export const healthMonitor = {
  async checkAllServices(): Promise<Record<string, HealthStatus>> {
    const [donkeyBetzHealth, dbaoHealth] = await Promise.allSettled([
      donkeyBetz.checkHealth(),
      dbao.checkHealth(),
    ]);

    return {
      donkeyBetz: donkeyBetzHealth.status === 'fulfilled' 
        ? donkeyBetzHealth.value 
        : { status: 'error', message: 'Failed to check Donkey Betz health', timestamp: new Date().toISOString() },
      
      dbao: dbaoHealth.status === 'fulfilled' 
        ? dbaoHealth.value 
        : { status: 'error', message: 'Failed to check DBAO health', timestamp: new Date().toISOString() },
    };
  },
};

// Configuration export for debugging
export const apiConfig = {
  donkeyBetzUrl: config.donkeyBetzApiUrl,
  dbaoUrl: config.dbaoApiUrl,
  hasAuthToken: !!config.authToken,
  platform: Platform.OS,
};

// Export storage utilities
export { storage };

// Debug logging
console.log('[API Service] Configuration:', {
  donkeyBetzUrl: config.donkeyBetzApiUrl,
  dbaoUrl: config.dbaoApiUrl,
  hasAuthToken: !!config.authToken,
  platform: Platform.OS,
});