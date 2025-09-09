import axios from 'axios';

// Simple API Configuration without import.meta or logger
export const API_BASE_URL = 'http://localhost:8001/api';
export const MEDIA_BASE_URL = 'http://localhost:8001';
export const DEFAULT_AUTH_TOKEN = '993f8273f70877e23b5c7d2f92ed30562a089fe3';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ${DEFAULT_AUTH_TOKEN}`,
  },
  timeout: 30000, // 30 seconds
});