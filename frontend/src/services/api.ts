/**
 * Unified API Service
 * Main API client for the Unified Donkey Betz platform
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { Logger } from '../utils/logger';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const DEFAULT_AUTH_TOKEN = import.meta.env.VITE_AUTH_TOKEN || '';

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Don't add auth token for login endpoint
        const isLoginEndpoint = config.url?.includes('/auth/login');
        
        // Add auth token if available (but not for login)
        if (!isLoginEndpoint) {
          const token = localStorage.getItem('authToken') || DEFAULT_AUTH_TOKEN;
          if (token) {
            config.headers.Authorization = `Token ${token}`;
          }
        }

        // Add custom headers for UCWSF
        config.headers['X-Client'] = 'web';
        config.headers['X-Version'] = '1.0.0';

        Logger.api('Request', config.method?.toUpperCase(), config.url, {
          headers: config.headers,
          data: config.data,
        });

        return config;
      },
      (error) => {
        Logger.error('API Request Error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        Logger.api('Response', response.status, response.config.url, {
          data: response.data,
        });
        return response;
      },
      (error) => {
        const { response } = error;
        
        Logger.error('API Response Error', {
          status: response?.status,
          url: response?.config?.url,
          data: response?.data,
        });

        // Handle 401 - Unauthorized
        if (response?.status === 401) {
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // HTTP Methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get(url, config);
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post(url, data, config);
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.put(url, data, config);
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.patch(url, data, config);
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete(url, config);
  }

  // Utility methods
  setAuthToken(token: string) {
    localStorage.setItem('authToken', token);
    this.client.defaults.headers.common.Authorization = `Token ${token}`;
  }

  clearAuthToken() {
    localStorage.removeItem('authToken');
    delete this.client.defaults.headers.common.Authorization;
  }

  getBaseURL() {
    return API_BASE_URL;
  }
}

// Create and export singleton instance
const api = new APIService();
export default api;