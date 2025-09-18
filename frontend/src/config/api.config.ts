/**
 * Centralized API Configuration
 * Supports dynamic URLs for development and production
 */

// Get base URL from environment or use dynamic detection
const getBaseUrl = () => {
  // Check for Vite environment variable overrides first
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace('/api', ''); // Remove /api if included
  }
  
  // Check if we're in production (Vite's MODE)
  if (import.meta.env.MODE === 'production') {
    // Use the current window location for production
    return window.location.origin;
  }
  
  // Development defaults
  return 'http://localhost:8000';
};

const getWsUrl = () => {
  // Check for Vite environment variable overrides first
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  
  // Check if we're in production
  if (import.meta.env.MODE === 'production') {
    // Use secure WebSocket in production
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}`;
  }
  
  // Development defaults - WebSocket runs on same port as API (8000)
  return 'ws://localhost:8000';
};

// Export configuration
export const API_CONFIG = {
  BASE_URL: getBaseUrl(),
  WS_URL: getWsUrl(),
  
  // API endpoints
  endpoints: {
    // Authentication
    auth: {
      login: '/api/v1/auth/login/',
      logout: '/api/v1/auth/logout/',
      register: '/api/v1/auth/register/',
      refresh: '/v1/auth/refresh/',
      profile: '/v1/auth/profile/',
      forgotPassword: '/v1/auth/forgot-password/',
      resetPassword: '/v1/auth/reset-password/',
    },
    
    // Assistant
    assistant: {
      chat: '/v1/assistant/chat/',
      ws: '/ws/assistant/',
    },
    
    // Agent Orchestra
    orchestra: {
      agents: '/v1/agents/',
      execute: '/v1/agents/execute/',
      status: '/v1/agents/status/',
      ws: '/ws/orchestra/',
    },
    
    // Sports/Odds
    sports: {
      leagues: '/v1/sports/leagues/',
      games: '/v1/sports/games/',
      markets: '/v1/sports/markets/',
      odds: '/v1/odds/',
      kelly: '/v1/odds/kelly/',
    },
    
    // Content
    content: {
      generate: '/v1/content/generate/',
      images: '/v1/content/images/',
      videos: '/v1/content/videos/',
      upload: '/v1/content/upload/',
    },
    
    // Knowledge/RAG
    knowledge: {
      embeddings: '/v1/knowledge/embeddings/',
      search: '/v1/knowledge/search/',
      documents: '/v1/knowledge/documents/',
    },
    
    // Health
    health: {
      check: '/v1/health/',
      status: '/v1/status/',
    },
  },
};

// Helper functions for building full URLs
export const buildApiUrl = (endpoint: string): string => {
  const baseUrl = API_CONFIG.BASE_URL;
  return `${baseUrl}${endpoint}`;
};

export const buildWsUrl = (endpoint: string): string => {
  const wsUrl = API_CONFIG.WS_URL;
  return `${wsUrl}${endpoint}`;
};

// API Request Helper with authentication
export async function apiRequest<T = any>(
  endpoint: string, 
  options: RequestInit & { params?: Record<string, any> } = {}
): Promise<T> {
  const { params, ...requestOptions } = options;
  
  // Build the full URL
  let url = endpoint.startsWith('http') ? endpoint : buildApiUrl(endpoint);
  
  // Add query parameters if provided
  if (params) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, String(value));
      }
    });
    const queryString = queryParams.toString();
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString;
    }
  }
  
  // Get auth token from localStorage
  const token = localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN;
  
  // Prepare headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...requestOptions.headers,
  };
  
  // Add auth token if available
  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }
  
  try {
    const response = await fetch(url, {
      ...requestOptions,
      headers,
    });
    
    // Handle non-OK responses
    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.error || errorMessage;
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    
    // Handle empty responses
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return {} as T;
    }
    
    // Parse JSON response
    return await response.json();
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
}

// Export for backwards compatibility
export default API_CONFIG;