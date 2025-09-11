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
  
  // Development defaults
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
    
    // Agent Orchestra
    orchestra: {
      agents: '/api/v1/agents/',
      execute: '/api/v1/agents/execute/',
      status: '/api/v1/agents/status/',
      ws: '/ws/orchestra/',
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

// Export for backwards compatibility
export default API_CONFIG;