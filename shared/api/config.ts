/**
 * Shared API Configuration
 * Used by both React Web and React Native platforms
 */

export const API_CONFIG = {
  // Base URL - defaults, should be overridden by platform-specific config
  BASE_URL: 'http://localhost:8001/api',
  
  // Security Fix: Remove hardcoded token - get from environment or localStorage
  DEFAULT_TOKEN: process.env.REACT_APP_DEV_TOKEN || null,
  
  // Request timeout (30 seconds)
  TIMEOUT: 30000,
  
  // API version
  VERSION: 'v1',
  
  // Retry configuration
  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000,
    BACKOFF_MULTIPLIER: 2,
  },
  
  // Headers
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};

// Endpoint groups for organization
export const ENDPOINTS = {
  // Content generation
  CONTENT: {
    CREATE: '/content/create/',
    BATCH: '/content/batch/',
    BLOG_GENERATE: '/content/blog/generate/',
    SOCIAL_GENERATE: '/content/social/generate/',
    GALLERY: '/gallery/',
  },
  
  // Voice features
  VOICE: {
    TRANSCRIBE: '/voice/transcribe/',
    TTS: '/voice/tts/',
    STUDIO: '/voice/studio/',
  },
  
  // Video features
  VIDEO: {
    TEXT_TO_VIDEO: '/video/text-to-video/',
    IMAGE_TO_VIDEO: '/video/image-to-video/',
    STATUS: '/video/status/',
  },
  
  // Stability AI features
  STABILITY: {
    UPSCALE: '/stability/upscale/',
    INPAINT: '/stability/inpaint/',
    REMOVE_BACKGROUND: '/stability/remove-background/',
    THREE_D: '/stability/3d/',
  },
  
  // AI features
  AI: {
    STYLE_MEMORY: '/style-memory/',
    PROMPTING: '/prompting/',
    WORKFLOWS: '/workflows/',
    CHARACTERS: '/characters/',
  },
  
  // Analytics & Admin
  ADMIN: {
    DASHBOARD: '/dashboard/',
    FEEDBACK: '/feedback/',
    CAMPAIGNS: '/campaigns/',
    RESEARCH_BOOKS: '/research-books/',
  },
  
  // Auth
  AUTH: {
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/refresh/',
    PROFILE: '/auth/profile/',
  },
};

// Response status codes
export const STATUS_CODES = {
  SUCCESS: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500,
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized. Please log in again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  TIMEOUT: 'Request timed out. Please try again.',
  UNKNOWN: 'An unexpected error occurred.',
};