/**
 * Authentication utility functions
 */

/**
 * Get the current authentication token from localStorage
 * This provides a centralized way to access the token across the app
 */
export const getAuthToken = (): string => {
  return localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || '';
};

/**
 * Get authorization header with current token
 */
export const getAuthHeader = (): { Authorization: string } | {} => {
  const token = getAuthToken();
  return token ? { Authorization: `Token ${token}` } : {};
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

/**
 * Default token for development/testing
 * This should be replaced with proper authentication in production
 */
export const DEFAULT_DEV_TOKEN = '993f8273f70877e23b5c7d2f92ed30562a089fe3';

/**
 * Get auth token with fallback to default dev token
 * Use this only during development - production should require proper login
 */
export const getAuthTokenWithDevFallback = (): string => {
  const token = getAuthToken();
  if (!token) {
    console.warn('⚠️ No auth token found, using development fallback token');
    return DEFAULT_DEV_TOKEN;
  }
  return token;
};

/**
 * Get authorization header with dev fallback
 */
export const getAuthHeaderWithDevFallback = (): { Authorization: string } => {
  return { Authorization: `Token ${getAuthTokenWithDevFallback()}` };
};