import { API_CONFIG } from '../config/api.config';

// Get API URL from environment and strip trailing slash
const BASE_URL = (import.meta.env.VITE_DBAO_API_URL || API_CONFIG.BASE_URL).replace(/\/$/, '');

// Intelligence API Types
export interface SkynetStatus {
  skynet_status: 'ONLINE' | 'OFFLINE' | 'INITIALIZING';
  intelligence_engine: 'ACTIVE' | 'INACTIVE';
  live_opportunities: number;
  live_predictions: number;
  scan_interval: number;
  last_update: string;
  features: {
    sports_intelligence: boolean;
    arbitrage_detection: boolean;
    value_betting: boolean;
    cross_domain_analysis: boolean;
    pattern_recognition: boolean;
  };
}

export interface IntelligenceOpportunity {
  id: string;
  type: 'arbitrage' | 'value' | 'prediction' | 'pattern';
  domain: 'SPORTS_BETTING' | 'CRYPTO' | 'TRADING' | 'REAL_ESTATE' | 'BUSINESS';
  entity: string;
  description: string;
  edge: number;
  confidence: number;
  profit_potential: number;
  time_window: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  timestamp: string;
  status: 'active' | 'expired' | 'executed';
  metadata?: Record<string, any>;
}

export interface IntelligencePrediction {
  id: string;
  domain: string;
  prediction_type: string;
  entity: string;
  prediction: string;
  confidence: number;
  expected_outcome: string;
  time_horizon: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface OpportunitiesResponse {
  opportunities: IntelligenceOpportunity[];
  count: number;
  timestamp: string;
  scanner_status: string;
}

export interface PredictionsResponse {
  predictions: IntelligencePrediction[];
  count: number;
  timestamp: string;
  engine_status: string;
}

// API Error class for better error handling
export class IntelligenceAPIError extends Error {
  constructor(public status: number, public message: string, public details?: any) {
    super(message);
    this.name = 'IntelligenceAPIError';
  }
}

// Generic API request handler with comprehensive error handling
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;

  console.log('🧠 [Intelligence API] Request:', {
    method: options.method || 'GET',
    endpoint,
    url,
    body: options.body ? JSON.parse(options.body as string) : undefined
  });

  // Get auth token from localStorage
  const token = localStorage.getItem('authToken');

  // Get CSRF token from cookies
  const getCsrfToken = () => {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    return null;
  };

  try {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'X-DBAO-Client': 'AI-Studio-Intelligence',
      ...options.headers,
    };

    // Add CSRF token for POST/PUT/DELETE requests
    const csrfToken = getCsrfToken();
    if (csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method || '')) {
      headers['X-CSRFToken'] = csrfToken;
    }

    // Add Authorization header if available
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // Include cookies for CSRF
    });

    // Read response as text first
    const responseText = await response.text();

    if (!response.ok) {
      console.error(`[Intelligence API] ${options.method || 'GET'} ${endpoint} failed:`, responseText);
      throw new IntelligenceAPIError(
        response.status,
        responseText || `HTTP ${response.status} ${response.statusText}`,
        { endpoint, status: response.status }
      );
    }

    // Parse JSON if we have content
    if (responseText.trim()) {
      const data = JSON.parse(responseText);

      console.log('✅ [Intelligence API] Response:', {
        endpoint,
        data,
        dataLength: Array.isArray(data) ? data.length : (data?.count || 'not array')
      });

      return data;
    }

    return {} as T;
  } catch (error) {
    if (error instanceof IntelligenceAPIError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      const networkError = `Network error: Unable to connect to ${url}`;
      console.error('[Intelligence API] Network error:', networkError);
      throw new IntelligenceAPIError(0, networkError, { endpoint });
    }

    console.error('[Intelligence API] Unexpected error:', error);
    throw new IntelligenceAPIError(500, 'Unexpected error occurred', { endpoint, error });
  }
}

/**
 * Get Skynet Intelligence Engine status
 */
export async function getSkynetStatus(): Promise<SkynetStatus> {
  return apiRequest<SkynetStatus>('/api/v1/intelligence/skynet/status/');
}

/**
 * Get live market opportunities from the intelligence engine
 */
export async function getLiveOpportunities(): Promise<OpportunitiesResponse> {
  return apiRequest<OpportunitiesResponse>('/api/v1/intelligence/opportunities/');
}

/**
 * Get live intelligence predictions
 */
export async function getLivePredictions(): Promise<PredictionsResponse> {
  return apiRequest<PredictionsResponse>('/api/v1/intelligence/predictions/');
}

/**
 * Start the intelligence engine if it's not running
 */
export async function startIntelligenceEngine(): Promise<{ success: boolean; message: string }> {
  return apiRequest<{ success: boolean; message: string }>('/api/v1/intelligence/start/', {
    method: 'POST'
  });
}

/**
 * Stop the intelligence engine
 */
export async function stopIntelligenceEngine(): Promise<{ success: boolean; message: string }> {
  return apiRequest<{ success: boolean; message: string }>('/api/v1/intelligence/stop/', {
    method: 'POST'
  });
}

/**
 * Force refresh opportunities and predictions
 */
export async function refreshIntelligenceData(): Promise<{
  opportunities: number;
  predictions: number;
  timestamp: string;
}> {
  return apiRequest<{
    opportunities: number;
    predictions: number;
    timestamp: string;
  }>('/api/v1/intelligence/refresh/', {
    method: 'POST'
  });
}

/**
 * Get intelligence engine configuration
 */
export async function getIntelligenceConfig(): Promise<{
  scan_interval: number;
  domains_enabled: string[];
  thresholds: Record<string, number>;
  features: Record<string, boolean>;
}> {
  return apiRequest<{
    scan_interval: number;
    domains_enabled: string[];
    thresholds: Record<string, number>;
    features: Record<string, boolean>;
  }>('/api/v1/intelligence/config/');
}

/**
 * Update intelligence engine configuration
 */
export async function updateIntelligenceConfig(config: {
  scan_interval?: number;
  domains_enabled?: string[];
  thresholds?: Record<string, number>;
  features?: Record<string, boolean>;
}): Promise<{ success: boolean; message: string; config: any }> {
  return apiRequest<{ success: boolean; message: string; config: any }>('/api/v1/intelligence/config/', {
    method: 'PATCH',
    body: JSON.stringify(config)
  });
}

/**
 * Get detailed opportunity by ID
 */
export async function getOpportunityDetails(opportunityId: string): Promise<IntelligenceOpportunity & {
  analysis: Record<string, any>;
  historical_performance?: Record<string, any>;
  execution_plan?: string[];
}> {
  return apiRequest<IntelligenceOpportunity & {
    analysis: Record<string, any>;
    historical_performance?: Record<string, any>;
    execution_plan?: string[];
  }>(`/api/v1/intelligence/opportunities/${opportunityId}/`);
}

/**
 * Get detailed prediction by ID
 */
export async function getPredictionDetails(predictionId: string): Promise<IntelligencePrediction & {
  reasoning: string;
  supporting_data: Record<string, any>;
  similar_predictions?: any[];
}> {
  return apiRequest<IntelligencePrediction & {
    reasoning: string;
    supporting_data: Record<string, any>;
    similar_predictions?: any[];
  }>(`/api/v1/intelligence/predictions/${predictionId}/`);
}

/**
 * Execute an opportunity (mark as executed and potentially trigger actions)
 */
export async function executeOpportunity(opportunityId: string, params?: {
  stake_amount?: number;
  notes?: string;
}): Promise<{
  success: boolean;
  execution_id: string;
  message: string;
}> {
  return apiRequest<{
    success: boolean;
    execution_id: string;
    message: string;
  }>(`/api/v1/intelligence/opportunities/${opportunityId}/execute/`, {
    method: 'POST',
    body: JSON.stringify(params || {})
  });
}

/**
 * Get intelligence analytics and metrics
 */
export async function getIntelligenceAnalytics(timeRange: '1h' | '24h' | '7d' | '30d' = '24h'): Promise<{
  opportunity_metrics: {
    total_detected: number;
    executed: number;
    success_rate: number;
    avg_edge: number;
    total_profit: number;
  };
  prediction_metrics: {
    total_made: number;
    correct: number;
    accuracy: number;
    avg_confidence: number;
  };
  domain_breakdown: Record<string, {
    opportunities: number;
    predictions: number;
    success_rate: number;
  }>;
  timeline_data: Array<{
    timestamp: string;
    opportunities: number;
    predictions: number;
    executions: number;
  }>;
}> {
  return apiRequest<any>(`/api/v1/intelligence/analytics/?range=${timeRange}`);
}

/**
 * Submit feedback on intelligence performance
 */
export async function submitIntelligenceFeedback(feedback: {
  type: 'opportunity' | 'prediction' | 'general';
  entity_id?: string;
  rating: number; // 1-5
  comment: string;
  outcome?: 'success' | 'failure' | 'neutral';
  profit_loss?: number;
}): Promise<{ success: boolean; message: string }> {
  return apiRequest<{ success: boolean; message: string }>('/api/v1/intelligence/feedback/', {
    method: 'POST',
    body: JSON.stringify(feedback)
  });
}

/**
 * Health check for intelligence services
 */
export async function healthCheck(): Promise<{
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    skynet_engine: boolean;
    opportunity_scanner: boolean;
    prediction_engine: boolean;
    websocket_server: boolean;
  };
  last_check: string;
}> {
  return apiRequest<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    services: {
      skynet_engine: boolean;
      opportunity_scanner: boolean;
      prediction_engine: boolean;
      websocket_server: boolean;
    };
    last_check: string;
  }>('/api/v1/intelligence/health/');
}

// Export utility functions for working with intelligence data

/**
 * Format opportunity edge as percentage with color coding
 */
export function formatEdge(edge: number): { text: string; color: string } {
  const text = `${edge.toFixed(1)}%`;

  if (edge >= 5) return { text, color: 'text-green-500' };
  if (edge >= 3) return { text, color: 'text-yellow-500' };
  return { text, color: 'text-orange-500' };
}

/**
 * Format confidence as percentage with color coding
 */
export function formatConfidence(confidence: number): { text: string; color: string } {
  const text = `${(confidence * 100).toFixed(0)}%`;

  if (confidence >= 0.8) return { text, color: 'text-green-500' };
  if (confidence >= 0.6) return { text, color: 'text-yellow-500' };
  return { text, color: 'text-red-500' };
}

/**
 * Get domain icon for display
 */
export function getDomainIcon(domain: string): string {
  const icons: Record<string, string> = {
    'SPORTS_BETTING': '🏈',
    'CRYPTO': '₿',
    'TRADING': '📈',
    'REAL_ESTATE': '🏠',
    'BUSINESS': '💼'
  };

  return icons[domain] || '🎯';
}

/**
 * Get risk level color
 */
export function getRiskColor(risk: string): string {
  const colors: Record<string, string> = {
    'LOW': 'text-green-500 border-green-500/30',
    'MEDIUM': 'text-yellow-500 border-yellow-500/30',
    'HIGH': 'text-red-500 border-red-500/30'
  };

  return colors[risk] || 'text-gray-500 border-gray-500/30';
}

/**
 * Calculate time remaining for opportunity window
 */
export function getTimeRemaining(timestamp: string, window: number): {
  remaining: number;
  status: 'active' | 'expiring' | 'expired';
  display: string;
} {
  const created = new Date(timestamp).getTime();
  const now = Date.now();
  const elapsed = (now - created) / 1000; // in seconds
  const remaining = Math.max(0, window - elapsed);

  let status: 'active' | 'expiring' | 'expired' = 'active';
  if (remaining === 0) status = 'expired';
  else if (remaining < window * 0.2) status = 'expiring'; // Less than 20% remaining

  const display = remaining > 0 ? `${Math.floor(remaining)}s` : 'Expired';

  return { remaining, status, display };
}