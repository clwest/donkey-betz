import axios from 'axios';

// Simple API Configuration without import.meta or logger
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
export const MEDIA_BASE_URL = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8000';
export const DEFAULT_AUTH_TOKEN = 'cff3e8441c4e2490e970de2f921f0064e7cc88a7';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ${DEFAULT_AUTH_TOKEN}`,
  },
  timeout: 30000, // 30 seconds
});