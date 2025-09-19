/**
 * Centralized API Configuration
 * Fixed to use correct /api/v1/agents/ endpoints
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

// Get auth token from environment or localStorage
const getAuthToken = () => {
  return localStorage.getItem('authToken') || 
         import.meta.env.VITE_AUTH_TOKEN || 
         '0fb2390dedd5cc47ec7e6a320e1477b31b7c0a97';
};

// Export configuration
export const API_CONFIG = {
  BASE_URL: getBaseUrl(),
  WS_URL: getWsUrl(),
  AUTH_TOKEN: getAuthToken(),
  
  // API endpoints - FIXED to use v1
  endpoints: {
    // Authentication
    auth: {
      login: '/api/v1/auth/login/',
      logout: '/api/v1/auth/logout/',
      register: '/api/v1/auth/register/',
      refresh: '/api/v1/auth/refresh/',
      profile: '/api/v1/auth/profile/',
      forgotPassword: '/api/v1/auth/forgot-password/',
      resetPassword: '/api/v1/auth/reset-password/',
    },
    
    // Assistant
    assistant: {
      chat: '/api/v1/assistant/chat/',
      ws: '/ws/assistant/',
    },
    
    // Agent Orchestra - FIXED to use correct v1 endpoints
    agents: {
      templates: '/api/v1/agents/templates/?page_size=200',
      execute: '/api/v1/agents/execute/',
      executions: '/api/v1/agents/executions/',
      discover: '/api/v1/agents/discover/',
      status: '/api/v1/agents/status/',
      ws: '/ws/agents/',
    },
    
    // Sports/Odds
    sports: {
      leagues: '/api/v1/sports/leagues/',
      games: '/api/v1/sports/games/',
      markets: '/api/v1/sports/markets/',
      odds: '/api/v1/odds/',
      kelly: '/api/v1/odds/kelly/',
    },
    
    // Content
    content: {
      generate: '/api/v1/content/generate/',
      images: '/api/v1/content/images/',
      videos: '/api/v1/content/videos/',
      upload: '/api/v1/content/upload/',
    },
    
    // Knowledge/RAG
    knowledge: {
      embeddings: '/api/v1/knowledge/embeddings/',
      search: '/api/v1/knowledge/search/',
      documents: '/api/v1/knowledge/documents/',
    },
    
    // Intelligence & Revenue
    intelligence: {
      revenue: '/api/v1/intelligence/revenue/',
      metrics: '/api/v1/intelligence/revenue/metrics/',
      opportunities: '/api/v1/intelligence/opportunities/',
    },
    
    // Health
    health: {
      check: '/api/v1/health/',
      status: '/api/v1/status/',
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

// API Request Helper with authentication - FIXED
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
  
  // Get auth token
  const token = getAuthToken();
  
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

// Axios-like API client for backwards compatibility
export const apiClient = {
  get: (url: string, config?: any) => apiRequest(url, { method: 'GET', ...config }),
  post: (url: string, data?: any, config?: any) => apiRequest(url, { method: 'POST', body: JSON.stringify(data), ...config }),
  put: (url: string, data?: any, config?: any) => apiRequest(url, { method: 'PUT', body: JSON.stringify(data), ...config }),
  delete: (url: string, config?: any) => apiRequest(url, { method: 'DELETE', ...config }),
  patch: (url: string, data?: any, config?: any) => apiRequest(url, { method: 'PATCH', body: JSON.stringify(data), ...config }),
};

// Export for backwards compatibility
export default API_CONFIG;