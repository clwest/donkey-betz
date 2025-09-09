/**
 * Shared API Client
 * Platform-agnostic axios instance with interceptors
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG, STATUS_CODES, ERROR_MESSAGES } from './config';

// Platform detection without React Native dependency
const getPlatform = (): 'web' | 'native' => {
  if (typeof window !== 'undefined' && typeof window.document !== 'undefined') {
    return 'web';
  }
  return 'native';
};

// Storage adapter interface
export interface IStorageAdapter {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
  getObject<T = any>(key: string): Promise<T | null>;
  setObject(key: string, value: any): Promise<void>;
}

// Default storage adapter for web
class WebStorageAdapter implements IStorageAdapter {
  async getItem(key: string): Promise<string | null> {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem(key);
    }
    return null;
  }

  async setItem(key: string, value: string): Promise<void> {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(key, value);
    }
  }

  async removeItem(key: string): Promise<void> {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(key);
    }
  }

  async getObject<T = any>(key: string): Promise<T | null> {
    const item = await this.getItem(key);
    if (item) {
      try {
        return JSON.parse(item);
      } catch {
        return null;
      }
    }
    return null;
  }

  async setObject(key: string, value: any): Promise<void> {
    await this.setItem(key, JSON.stringify(value));
  }
}

// Allow storage adapter to be injected for different platforms
let storageAdapter: IStorageAdapter = new WebStorageAdapter();

const setStorageAdapter = (adapter: IStorageAdapter) => {
  storageAdapter = adapter;
};

const getStorageAdapter = (): IStorageAdapter => {
  return storageAdapter;
}

// Request queue for offline support
interface QueuedRequest {
  id: string;
  config: AxiosRequestConfig;
  timestamp: number;
  retries: number;
}

class RequestQueue {
  private queue: QueuedRequest[] = [];
  private isProcessing: boolean = false;
  private storageKey = 'api_request_queue';
  
  constructor() {
    this.loadFromStorage();
  }
  
  private async loadFromStorage() {
    try {
      const stored = await storageAdapter.getObject<QueuedRequest[]>(this.storageKey);
      if (stored) {
        this.queue = stored;
      }
    } catch (error) {
      console.error('Failed to load request queue from storage:', error);
    }
  }
  
  private async saveToStorage() {
    try {
      await storageAdapter.setObject(this.storageKey, this.queue);
    } catch (error) {
      console.error('Failed to save request queue to storage:', error);
    }
  }
  
  add(config: AxiosRequestConfig) {
    // Only queue non-GET requests
    if (config.method?.toLowerCase() === 'get') return;
    
    const queuedRequest: QueuedRequest = {
      id: `${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
      config,
      timestamp: Date.now(),
      retries: 0,
    };
    
    this.queue.push(queuedRequest);
    this.saveToStorage();
  }
  
  async flush(client: AxiosInstance): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) return;
    
    this.isProcessing = true;
    const processedIds: string[] = [];
    
    for (const request of this.queue) {
      try {
        await client.request(request.config);
        processedIds.push(request.id);
        console.log(`[API] ✓ Processed queued request: ${request.config.url}`);
      } catch (error) {
        request.retries += 1;
        if (request.retries >= 3) {
          processedIds.push(request.id);
          console.error(`[API] ✗ Gave up on queued request after 3 retries: ${request.config.url}`);
        }
      }
    }
    
    // Remove processed requests
    this.queue = this.queue.filter(req => !processedIds.includes(req.id));
    await this.saveToStorage();
    
    this.isProcessing = false;
  }
  
  getQueueLength(): number {
    return this.queue.length;
  }
}

// API client configuration interface
export interface APIClientConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
  defaultToken?: string;
  enableLogging?: boolean;
  enableOfflineQueue?: boolean;
  onUnauthorized?: () => void;
}

// Enhanced API error type
export interface APIError {
  message: string;
  code: string;
  status?: number;
  details?: any;
  originalError?: AxiosError;
}

// Create the API client factory
export const createAPIClient = (config?: APIClientConfig): AxiosInstance => {
  const finalConfig = {
    baseURL: config?.baseURL || API_CONFIG.BASE_URL,
    timeout: config?.timeout || API_CONFIG.TIMEOUT,
    headers: config?.headers || API_CONFIG.HEADERS,
    defaultToken: config?.defaultToken || API_CONFIG.DEFAULT_TOKEN,
    enableLogging: config?.enableLogging ?? ((typeof process !== 'undefined' && (process as any).env?.NODE_ENV === 'development') || false),
    enableOfflineQueue: config?.enableOfflineQueue ?? true,
    onUnauthorized: config?.onUnauthorized,
  };
  
  const client = axios.create({
    baseURL: finalConfig.baseURL,
    timeout: finalConfig.timeout,
    headers: finalConfig.headers,
  });

  const requestQueue = new RequestQueue();

  // Request interceptor - Add auth token and logging
  client.interceptors.request.use(
    async (config) => {
      // Add auth token
      const token = await storageAdapter.getItem('authToken');
      const finalToken = token || finalConfig.defaultToken;
      
      if (finalToken) {
        config.headers.Authorization = `Token ${finalToken}`;
      }
      
      // Add platform header
      config.headers['X-Platform'] = getPlatform();
      
      // Add request ID for tracing
      config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;

      // Log request in development
      if (finalConfig.enableLogging) {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
          data: config.data,
          params: config.params,
        });
      }

      return config;
    },
    (error) => {
      if (finalConfig.enableLogging) {
        console.error('[API Request Error]', error);
      }
      return Promise.reject(error);
    }
  );

  // Response interceptor - Handle errors and logging
  client.interceptors.response.use(
    (response) => {
      // Log response in development
      if (finalConfig.enableLogging) {
        console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
          status: response.status,
          data: response.data,
        });
      }

      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config;

      // Handle different error scenarios
      if (!error.response) {
        // Network error - queue request for retry if enabled
        if (originalRequest && finalConfig.enableOfflineQueue) {
          requestQueue.add(originalRequest);
        }
        
        if (finalConfig.enableLogging) {
          console.error('[API Network Error]', error.message);
        }
        
        const apiError: APIError = {
          message: ERROR_MESSAGES.NETWORK_ERROR,
          code: 'NETWORK_ERROR',
          originalError: error,
        };
        
        return Promise.reject(apiError);
      }

      const { status, data } = error.response;

      // Log error details in development
      if (finalConfig.enableLogging) {
        console.error(`[API Error] ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`, {
          status,
          data,
        });
      }

      // Handle specific status codes
      switch (status) {
        case STATUS_CODES.UNAUTHORIZED:
          // Clear token
          await storageAdapter.removeItem('authToken');
          await storageAdapter.removeItem('user');
          
          // Call custom unauthorized handler if provided
          if (finalConfig.onUnauthorized) {
            finalConfig.onUnauthorized();
          } else if (getPlatform() === 'web' && typeof window !== 'undefined') {
            // Default web behavior - redirect to login
            window.location.href = '/login';
          }
          
          const unauthorizedError: APIError = {
            message: ERROR_MESSAGES.UNAUTHORIZED,
            code: 'UNAUTHORIZED',
            status,
            originalError: error,
          };
          
          return Promise.reject(unauthorizedError);

        case STATUS_CODES.SERVER_ERROR:
          const serverError: APIError = {
            message: ERROR_MESSAGES.SERVER_ERROR,
            code: 'SERVER_ERROR',
            status,
            originalError: error,
          };
          
          return Promise.reject(serverError);

        default:
          // Try to extract error message from response
          const errorMessage = 
            (data as any)?.error || 
            (data as any)?.message || 
            (data as any)?.detail ||
            ERROR_MESSAGES.UNKNOWN;

          const defaultError: APIError = {
            message: errorMessage,
            code: `ERROR_${status}`,
            status,
            details: data,
            originalError: error,
          };
          
          return Promise.reject(defaultError);
      }
    }
  );

  // Add utility methods to the client instance
  (client as any).flushQueue = () => requestQueue.flush(client);
  (client as any).getQueueLength = () => requestQueue.getQueueLength();
  (client as any).setAuthToken = async (token: string) => {
    await storageAdapter.setItem('authToken', token);
  };
  (client as any).clearAuth = async () => {
    await storageAdapter.removeItem('authToken');
    await storageAdapter.removeItem('user');
  };

  return client;
};

// Default client instance
export const apiClient = createAPIClient();

// Helper functions for common operations
export const apiHelpers = {
  // Handle file uploads - platform agnostic
  createFormData: (data: any, platform?: 'web' | 'native') => {
    const currentPlatform = platform || getPlatform();
    const formData = new FormData();
    
    Object.keys(data).forEach(key => {
      const value = data[key];
      
      if (currentPlatform === 'web') {
        // Web file handling
        if (value instanceof File) {
          formData.append(key, value);
        } else if (Array.isArray(value)) {
          value.forEach((item, index) => {
            if (item instanceof File) {
              formData.append(`${key}[${index}]`, item);
            } else {
              formData.append(`${key}[${index}]`, JSON.stringify(item));
            }
          });
        } else if (value !== undefined && value !== null) {
          formData.append(key, typeof value === 'string' ? value : JSON.stringify(value));
        }
      } else {
        // React Native file handling
        if (value?.uri) {
          // File object in React Native
          formData.append(key, {
            uri: value.uri,
            type: value.type || 'image/jpeg',
            name: value.name || 'file',
          } as any);
        } else if (Array.isArray(value)) {
          value.forEach((item, index) => {
            if (item?.uri) {
              formData.append(`${key}[${index}]`, {
                uri: item.uri,
                type: item.type || 'image/jpeg',
                name: item.name || `file_${index}`,
              } as any);
            } else {
              formData.append(`${key}[${index}]`, JSON.stringify(item));
            }
          });
        } else if (value !== undefined && value !== null) {
          formData.append(key, typeof value === 'string' ? value : JSON.stringify(value));
        }
      }
    });
    
    return formData;
  },

  // Handle pagination
  buildPaginationParams: (page: number = 1, limit: number = 20) => ({
    page,
    limit,
    offset: (page - 1) * limit,
  }),

  // Handle search/filter params
  buildFilterParams: (filters: Record<string, any>) => {
    const params: Record<string, string> = {};
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
        params[key] = String(filters[key]);
      }
    });
    return params;
  },

  // Retry logic for failed requests
  retryRequest: async (
    fn: () => Promise<any>,
    maxAttempts: number = API_CONFIG.RETRY.MAX_ATTEMPTS,
    delay: number = API_CONFIG.RETRY.DELAY
  ): Promise<any> => {
    let lastError: any;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        
        if (attempt < maxAttempts) {
          const waitTime = delay * Math.pow(API_CONFIG.RETRY.BACKOFF_MULTIPLIER, attempt - 1);
          await new Promise(resolve => setTimeout(resolve, waitTime));
        }
      }
    }
    
    throw lastError;
  },
};

// Export storage utilities
export { setStorageAdapter, getStorageAdapter };

// Type exports for consistency
export type { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError };