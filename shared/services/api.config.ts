import axios from 'axios';
import { Logger } from '../utils/logger';

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';
export const MEDIA_BASE_URL = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8001';
export const DEFAULT_AUTH_TOKEN = '504406afbc117727c55cd1244ff77ecebe791cc0';

// Helper function to convert relative media URLs to absolute URLs
export const getFullMediaURL = (relativePath: string): string => {
  if (!relativePath) return '';
  if (relativePath.startsWith('http')) return relativePath; // Already absolute
  return `${MEDIA_BASE_URL}${relativePath}`;
};

// Log API configuration on initialization
Logger.api('CONFIG', 'API Base URL', { baseURL: API_BASE_URL });
Logger.api('CONFIG', 'Default Auth Token', { token: DEFAULT_AUTH_TOKEN.substring(0, 10) + '...' });

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ${DEFAULT_AUTH_TOKEN}`,
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage if available
    const token = localStorage.getItem('authToken') || DEFAULT_AUTH_TOKEN;
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // Log the request
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

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Log successful response
    Logger.apiResponse(response.config.url || '', {
      status: response.status,
      data: response.data,
      headers: response.headers
    });
    return response;
  },
  (error) => {
    // Log error response
    Logger.apiResponse(error.config?.url || 'unknown', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
      code: error.code
    }, true);
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      Logger.warn('AUTH', 'Unauthorized access detected, redirecting to login');
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    
    // Extract error message
    const message = error.response?.data?.detail || 
                   error.response?.data?.error || 
                   error.message || 
                   'An unexpected error occurred';
    
    // Create a more user-friendly error
    const enhancedError = {
      ...error,
      userMessage: message,
      status: error.response?.status,
    };
    
    return Promise.reject(enhancedError);
  }
);

// Helper function for file uploads
export const createFormData = (data: Record<string, any>): FormData => {
  const formData = new FormData();
  
  Object.entries(data).forEach(([key, value]) => {
    if (value instanceof File) {
      formData.append(key, value);
    } else if (value instanceof Array) {
      value.forEach((item) => {
        formData.append(`${key}[]`, item);
      });
    } else if (value !== null && value !== undefined) {
      formData.append(key, String(value));
    }
  });
  
  return formData;
};