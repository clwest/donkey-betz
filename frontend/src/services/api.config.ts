/**
 * Web App API Configuration
 * API client configuration for the web application
 */
import axios from 'axios';
import type { AxiosInstance } from 'axios';
import { Logger } from '../utils/logger';
import { API_CONFIG } from '../config/api.config';

// API Configuration - Dynamic URLs for development and production
export const API_BASE_URL = import.meta.env.VITE_API_URL || API_CONFIG.BASE_URL;
export const MEDIA_BASE_URL = import.meta.env.VITE_MEDIA_URL || API_CONFIG.BASE_URL;
export const DEFAULT_AUTH_TOKEN = import.meta.env.VITE_AUTH_TOKEN || ''; // No default token - users must authenticate

// UCWSF Feature Flags
export const UCWSF_CONFIG = {
  enhancedCors: import.meta.env.VITE_UCWSF_ENHANCED_CORS === 'true',
  websockets: import.meta.env.VITE_UCWSF_WEBSOCKETS === 'true',
  customHeaders: import.meta.env.VITE_UCWSF_CUSTOM_HEADERS === 'true',
};

// Helper function to convert relative media URLs to absolute URLs
export const getFullMediaURL = (relativePath: string): string => {
  if (!relativePath) return '';
  if (relativePath.startsWith('http')) return relativePath; // Already absolute
  return `${MEDIA_BASE_URL}${relativePath}`;
};

// Storage adapter interface
interface IStorageAdapter {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
  getObject<T = any>(key: string): Promise<T | null>;
  setObject(key: string, value: any): Promise<void>;
}

// Web-specific storage adapter that integrates with Logger
class WebStorageAdapter implements IStorageAdapter {
  async getItem(key: string): Promise<string | null> {
    return localStorage.getItem(key);
  }

  async setItem(key: string, value: string): Promise<void> {
    localStorage.setItem(key, value);
  }

  async removeItem(key: string): Promise<void> {
    localStorage.removeItem(key);
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

// Storage adapter instance
const storageAdapter = new WebStorageAdapter();

// Function to set storage adapter (for compatibility)
export const setStorageAdapter = (adapter: IStorageAdapter) => {
  // This is a no-op for now since we're using localStorage directly
};

// Create API client function
export const createAPIClient = (config: {
  baseURL: string;
  defaultToken?: string;
  enableLogging?: boolean;
  onUnauthorized?: () => void;
}): AxiosInstance => {
  const client = axios.create({
    baseURL: config.baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Don't set default token here - will be added via interceptor

  // Add response interceptor for unauthorized handling
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401 && config.onUnauthorized) {
        config.onUnauthorized();
      }
      return Promise.reject(error);
    }
  );

  return client;
};

// Log API configuration on initialization
Logger.api('CONFIG', 'API Base URL', { baseURL: API_BASE_URL });
Logger.api('CONFIG', 'Default Auth Token', { token: DEFAULT_AUTH_TOKEN.substring(0, 10) + '...' });

// Create API client with web-specific configuration
export const apiClient = createAPIClient({
  baseURL: API_BASE_URL,
  // Token will be added dynamically from localStorage via interceptor
  enableLogging: true,
  onUnauthorized: () => {
    // Temporarily disabled automatic redirect to prevent loops
    // Only redirect if we're not already on the login page AND not on dashboard
    if (!window.location.pathname.includes('/login') && 
        !window.location.pathname.includes('/dashboard') &&
        !window.location.pathname.includes('/gallery') &&
        !window.location.pathname.includes('/studio')) {
      console.log('🔐 API: Would redirect to login but currently disabled for debugging');
      // localStorage.removeItem('authToken');
      // localStorage.removeItem('auth-storage');
      // window.location.href = '/login';
    }
  },
});

// Add web-specific request interceptor for UCWSF custom headers and auth token
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token from localStorage if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Token ${token}`;
    }
    
    // UCWSF: Add custom headers if enabled (optional)
    // Temporarily disabled to avoid CORS issues
    // if (UCWSF_CONFIG.customHeaders) {
    //   // Add client version for debugging
    //   config.headers['X-Client-Version'] = '1.0.0';
    //   
    //   // Add any custom headers based on URL patterns
    //   if (config.url?.includes('/agent') || config.url?.includes('/orchestrat')) {
    //     config.headers['X-Agent-Request'] = 'true';
    //   }
    // }
    
    // Log the request with our custom logger
    Logger.api(
      config.method?.toUpperCase() || 'GET',
      config.url || '',
      {
        data: config.data,
        params: config.params,
        headers: {
          ...config.headers,
          Authorization: config.headers.Authorization ? 'Token ***' : undefined
        }
      }
    );
    
    return config;
  },
  (error) => {
    Logger.error('API Request Interceptor', error);
    return Promise.reject(error);
  }
);

// Add web-specific response interceptor for enhanced logging
apiClient.interceptors.response.use(
  (response) => {
    // Log successful response with our custom logger
    Logger.apiResponse(response.config.url || '', {
      status: response.status,
      data: response.data,
      headers: response.headers
    });
    return response;
  },
  (error) => {
    // Log error response with our custom logger
    Logger.apiResponse(error.config?.url || 'unknown', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
      code: error.code
    }, true);
    
    if (error.response?.status === 401) {
      Logger.warn('AUTH', 'Unauthorized access detected');
    }
    
    // The shared client already handles error transformation
    // Just pass it through
    return Promise.reject(error);
  }
);

// Helper function to create FormData
export const createFormData = (data: Record<string, any>): FormData => {
  const formData = new FormData();
  
  Object.keys(data).forEach(key => {
    const value = data[key];
    if (value !== null && value !== undefined) {
      if (value instanceof File || value instanceof Blob) {
        formData.append(key, value);
      } else if (typeof value === 'object') {
        formData.append(key, JSON.stringify(value));
      } else {
        formData.append(key, String(value));
      }
    }
  });
  
  return formData;
};

// API helpers export for compatibility
export const apiHelpers = {
  createFormData: (data: Record<string, any>, platform: string = 'web') => createFormData(data)
};