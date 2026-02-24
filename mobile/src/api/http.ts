import axios from 'axios';
import Constants from 'expo-constants';
import { getToken } from '../auth/tokenStore';

const API_BASE_URL =
  Constants.expoConfig?.extra?.apiBaseUrl ?? 'https://donkey-betz-platform-production.up.railway.app/api';

const http = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 90_000,
});

// ── Request interceptor: attach Token header ────────────────────────────────

http.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// ── Response interceptor: flag 401s ─────────────────────────────────────────
// The auth store listens for this and triggers sign-out when appropriate.
// We don't redirect here (no window.location in RN); the store handles it.

let onUnauthorized: (() => void) | null = null;

export function setOnUnauthorized(handler: () => void) {
  onUnauthorized = handler;
}

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const url = error.config?.url ?? '';
      const isAuthEndpoint = url.includes('/auth/') || url.includes('/login');
      if (isAuthEndpoint && onUnauthorized) {
        onUnauthorized();
      }
    }
    return Promise.reject(error);
  },
);

export default http;
