/**
 * Shared API Module
 * Central export point for all shared functionality
 */

// API Configuration
export * from './api/config';
export * from './api/client';

// Types
export * from './types/api.types';

// Base Service
export * from './services/base.service';

// Re-export commonly used items for convenience
export { apiClient, apiHelpers, setStorageAdapter, getStorageAdapter } from './api/client';
export type { IStorageAdapter, APIClientConfig, APIError } from './api/client';
export { API_CONFIG, ENDPOINTS, STATUS_CODES, ERROR_MESSAGES } from './api/config';
export { BaseService } from './services/base.service';