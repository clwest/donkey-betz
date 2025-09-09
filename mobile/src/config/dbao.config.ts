/**
 * DBAO (Donkey Betz Agent Orchestra) Configuration for React Native
 */

// Environment-specific configuration
const isDevelopment = __DEV__;

export const DBAO_CONFIG = {
  // Base URLs  
  API_BASE_URL: isDevelopment ? 'http://localhost:8001/api/v1' : 'https://api.donkeybetz.com/api/v1',
  MEDIA_BASE_URL: isDevelopment ? 'http://localhost:8001' : 'https://api.donkeybetz.com',
  WS_BASE_URL: isDevelopment ? 'ws://localhost:8001' : 'wss://api.donkeybetz.com',

  // Authentication
  DEFAULT_AUTH_TOKEN: 'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502', // Updated to match working token

  // API Configuration
  DEFAULT_TIMEOUT: 30000, // 30 seconds
  MAX_RETRIES: 3,
  RETRY_BACKOFF_MS: 1000,

  // WebSocket Configuration
  WS_HEARTBEAT_INTERVAL: 30000, // 30 seconds
  WS_MAX_RECONNECT_ATTEMPTS: 5,
  WS_RECONNECT_DELAY: 1000,

  // Agent Orchestra Settings
  ENABLE_AGENT_SUGGESTIONS: true,
  ENABLE_REAL_TIME_UPDATES: true,
  ENABLE_BETTING_FEATURES: true,
  ENABLE_ORCHESTRATION: true,

  // Performance Settings
  ENABLE_REQUEST_CACHING: true,
  CACHE_TTL: 300000, // 5 minutes
  ENABLE_COMPRESSION: true,

  // UI Settings
  SHOW_ERROR_DETAILS: isDevelopment,
  ENABLE_DEBUG_LOGGING: isDevelopment,
  AUTO_CONNECT_WEBSOCKET: true,

  // Supported Agent Types
  AGENT_TYPES: [
    'business',
    'research', 
    'content',
    'technical',
    'marketing',
    'financial',
    'legal',
    'creative',
    'career',
    'communication'
  ] as const,

  // Sports Betting Configuration
  BETTING: {
    SUPPORTED_SPORTS: ['football', 'basketball', 'baseball', 'hockey', 'soccer'],
    DEFAULT_MIN_EDGE: 0.04, // 4%
    DEFAULT_CONFIDENCE_THRESHOLD: 0.6,
    MAX_CONCURRENT_ANALYSES: 3
  },

  // Error Handling
  ERROR_REPORTING: {
    ENABLED: true,
    AUTO_REPORT_CRASHES: true,
    INCLUDE_DEVICE_INFO: true
  }
} as const;

// Type definitions
export type AgentType = typeof DBAO_CONFIG.AGENT_TYPES[number];
export type SupportedSport = typeof DBAO_CONFIG.BETTING.SUPPORTED_SPORTS[number];

// Helper functions
export const getApiUrl = (endpoint: string): string => {
  const baseUrl = DBAO_CONFIG.API_BASE_URL;
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${normalizedEndpoint}`;
};

export const getMediaUrl = (path: string): string => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${DBAO_CONFIG.MEDIA_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
};

export const getWebSocketUrl = (endpoint: string = 'agents'): string => {
  return `${DBAO_CONFIG.WS_BASE_URL}/ws/${endpoint}/`;
};

// Validation helpers
export const isValidAgentType = (type: string): type is AgentType => {
  return DBAO_CONFIG.AGENT_TYPES.includes(type as AgentType);
};

export const isValidSport = (sport: string): sport is SupportedSport => {
  return DBAO_CONFIG.BETTING.SUPPORTED_SPORTS.includes(sport as SupportedSport);
};

// Configuration validation
export const validateConfig = (): boolean => {
  const requiredUrls = [
    DBAO_CONFIG.API_BASE_URL,
    DBAO_CONFIG.MEDIA_BASE_URL,
    DBAO_CONFIG.WS_BASE_URL
  ];

  const isValid = requiredUrls.every(url => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  });

  if (!isValid && isDevelopment) {
    console.warn('[DBAO Config] Invalid URL configuration detected');
  }

  return isValid;
};

// Initialize configuration validation in development
if (isDevelopment) {
  validateConfig();
}