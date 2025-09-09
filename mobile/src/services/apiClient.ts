import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_BASE_URL, DEFAULT_AUTH_TOKEN, storage, STORAGE_KEYS, isOnline } from './apiConfig';

// Types
export interface ApiError {
  message: string;
  status?: number;
  data?: any;
  userMessage?: string;
}

export interface RequestConfig extends AxiosRequestConfig {
  skipAuth?: boolean;
  skipQueue?: boolean;
  cache?: boolean;
  cacheKey?: string;
}

// Offline queue interface
interface QueuedRequest {
  id: string;
  config: RequestConfig;
  timestamp: number;
  retries: number;
}

class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;
  private offlineQueue: QueuedRequest[] = [];
  private isProcessingQueue = false;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    this.setupInterceptors();
    this.initializeAuth();
    this.loadOfflineQueue();
  }

  private async initializeAuth() {
    try {
      const token = await storage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      this.authToken = token || DEFAULT_AUTH_TOKEN;
      
      if (this.authToken) {
        this.client.defaults.headers.common['Authorization'] = `Token ${this.authToken}`;
      }
    } catch (error) {
      // console.error('Error initializing auth:', error);
      this.authToken = DEFAULT_AUTH_TOKEN;
      this.client.defaults.headers.common['Authorization'] = `Token ${DEFAULT_AUTH_TOKEN}`;
    }
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        // Ensure auth token is set
        if (!config.skipAuth && this.authToken) {
          config.headers.Authorization = `Token ${this.authToken}`;
        }

        // Add platform info
        config.headers['X-Platform'] = 'react-native';
        
        // console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        // console.error('[API] Request error:', error);
        return Promise.reject(this.createApiError(error));
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // console.log(`[API] ✓ ${response.config.url} (${response.status}`);
        return response;
      },
      async (error) => {
        // console.error(`[API] ✗ ${error.config?.url} (${error.response?.status}`);
        
        // Handle 401 unauthorized
        if (error.response?.status === 401) {
          await this.handleUnauthorized();
        }

        // Handle network errors for offline queueing
        if (!error.response && !error.config?.skipQueue) {
          // Check if it's actually a network issue or just CORS/connection refused
          const isNetworkError = error.code === 'ECONNREFUSED' || 
                                error.code === 'ENOTFOUND' || 
                                error.message?.includes('Network Error');
          
          if (isNetworkError) {
            // Log the actual error for debugging
            console.error('[API] Network error:', error.message);
            console.error('[API] Attempted URL:', error.config?.url);
            console.error('[API] Base URL:', API_BASE_URL);
          }
          
          await this.queueRequest(error.config);
          throw this.createApiError(error, 'Request queued for when connection is restored');
        }

        throw this.createApiError(error);
      }
    );
  }

  private createApiError(error: any, customMessage?: string): ApiError {
    const message = error.response?.data?.detail || 
                   error.response?.data?.error || 
                   error.response?.data?.message ||
                   error.message || 
                   'An unexpected error occurred';

    return {
      message,
      status: error.response?.status,
      data: error.response?.data,
      userMessage: customMessage || message,
    };
  }

  private async handleUnauthorized() {
    // console.log('[API] Handling unauthorized access');
    
    // Clear auth data
    await storage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    await storage.removeItem(STORAGE_KEYS.USER);
    
    this.authToken = null;
    delete this.client.defaults.headers.common['Authorization'];

    // TODO: Navigate to login screen
    // This would typically be handled by the auth store
  }

  // Offline queue management
  private async queueRequest(config: RequestConfig) {
    if (config.method?.toLowerCase() === 'get') return; // Don't queue GET requests

    const queuedRequest: QueuedRequest = {
      id: Date.now().toString(),
      config,
      timestamp: Date.now(),
      retries: 0,
    };

    this.offlineQueue.push(queuedRequest);
    await this.saveOfflineQueue();
  }

  private async loadOfflineQueue() {
    try {
      const queue = await storage.getObject<QueuedRequest[]>(STORAGE_KEYS.OFFLINE_QUEUE);
      if (queue) {
        this.offlineQueue = queue;
      }
    } catch (error) {
      console.error('Error loading offline queue:', error);
    }
  }

  private async saveOfflineQueue() {
    try {
      await storage.setObject(STORAGE_KEYS.OFFLINE_QUEUE, this.offlineQueue);
    } catch (error) {
      console.error('Error saving offline queue:', error);
    }
  }

  public async processOfflineQueue() {
    if (this.isProcessingQueue || this.offlineQueue.length === 0) return;

    this.isProcessingQueue = true;
    const online = await isOnline();

    if (!online) {
      this.isProcessingQueue = false;
      return;
    }

    // console.log(`[API] Processing ${this.offlineQueue.length} queued requests`);

    const processedIds: string[] = [];

    for (const request of this.offlineQueue) {
      try {
        await this.client.request(request.config);
        processedIds.push(request.id);
        // console.log(`[API] ✓ Processed queued request: ${request.config.url}`);
      } catch (error) {
        request.retries += 1;
        if (request.retries >= 3) {
          processedIds.push(request.id);
          // console.log(`[API] ✗ Gave up on queued request after 3 retries: ${request.config.url}`);
        }
      }
    }

    // Remove processed requests
    this.offlineQueue = this.offlineQueue.filter(req => !processedIds.includes(req.id));
    await this.saveOfflineQueue();

    this.isProcessingQueue = false;
  }

  // Auth methods
  public async setAuthToken(token: string) {
    this.authToken = token;
    this.client.defaults.headers.common['Authorization'] = `Token ${token}`;
    await storage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
  }

  public async clearAuth() {
    this.authToken = null;
    delete this.client.defaults.headers.common['Authorization'];
    await storage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    await storage.removeItem(STORAGE_KEYS.USER);
  }

  public getAuthToken(): string | null {
    return this.authToken;
  }

  // HTTP methods
  public async get<T = any>(url: string, config?: RequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  public async post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  public async put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  public async patch<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  public async delete<T = any>(url: string, config?: RequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // File upload helper
  public async uploadFile<T = any>(
    url: string, 
    file: any, 
    fieldName = 'file',
    additionalData?: Record<string, any>,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    
    // Handle React Native file upload
    if (file.uri) {
      formData.append(fieldName, {
        uri: file.uri,
        type: file.type || 'image/jpeg',
        name: file.name || 'upload.jpg',
      } as any);
    } else {
      formData.append(fieldName, file);
    }

    // Add additional data
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, String(value));
        }
      });
    }

    const config: RequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress ? (progressEvent) => {
        const progress = Math.round((progressEvent.loaded / (progressEvent.total || 1)) * 100);
        onProgress(progress);
      } : undefined,
    };

    const response = await this.client.post<T>(url, formData, config);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;