/**
 * Agent Orchestra REST API Client
 * 
 * Provides REST API integration for the Agent Orchestra feature using:
 * - AI Studio API for health checks and orchestration
 * - DBAO WebSocket for real-time updates
 * - Proper error handling and response parsing
 */

import { toast } from 'sonner';
import { API_CONFIG, buildApiUrl, buildWsUrl } from '../../../config/api.config';

// Environment configuration
// Use AI Content Studio API for Orchestra endpoints (agents, instances, etc.)
// Agent/orchestra endpoints are under /api/v1/
const ORCH_REST = import.meta.env.VITE_API_URL || API_CONFIG.BASE_URL;
// Use AI Content Studio WebSocket URL for Agent Orchestra communication
const ORCH_WS_BASE = import.meta.env.VITE_WS_URL || API_CONFIG.WS_URL;
console.log('[Orchestra API] WebSocket base URL:', ORCH_WS_BASE);

// Types
export interface OrchestraHealth {
  status: 'healthy' | 'unhealthy' | 'degraded';
  version?: string;
  timestamp?: string;
  details?: Record<string, any>;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  specialization: string;
  capabilities: string[];
  required_tools: string[];
  system_prompt: string;
  personality_traits: Record<string, any>;
  llm_provider: 'openai' | 'anthropic';
  llm_model: string;
  created_at: string;
  updated_at: string;
}

export interface AgentInstance {
  id: string;
  template: Agent;
  task_description: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result: any;
  error_message: string | null;
  tokens_used: number;
  cost_estimate: number;
  execution_time: number;
  user: number;
  created_at: string;
  updated_at: string;
}

/**
 * Generic API request handler with error handling
 */
async function apiRequest<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  endpoint: string,
  data?: any
): Promise<T> {
  const url = `${ORCH_REST}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  try {
    // Get auth token from localStorage - using DBAO testuser token
    const token = localStorage.getItem('authToken') || 'cff3e8441c4e2490e970de2f921f0064e7cc88a7';
    
    const config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-Orchestra-Client': 'AI-Studio-Web',
        'Authorization': `Token ${token}`
      }
    };

    if (data && (method === 'POST' || method === 'PUT')) {
      config.body = JSON.stringify(data);
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.error || errorMessage;
      } catch {
        // Body already consumed, just use status message
        errorMessage = `${response.status} ${response.statusText}`;
      }
      
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error(`[Orchestra API] ${method} ${url} failed:`, message);
    toast.error(`API Error: ${message}`);
    throw error;
  }
}

/**
 * Check Orchestra health status
 * Using the main health endpoint since there's no dedicated orchestra health
 */
export async function orchHealth(): Promise<OrchestraHealth | null> {
  try {
    // Use the main health endpoint at /api/v1/health/
    const response = await fetch(`${ORCH_REST}/api/v1/health/`);
    const health = await response.json();
    return {
      status: health?.status === 'healthy' ? 'healthy' : 'unhealthy',
      version: health?.version,
      timestamp: health?.timestamp,
      details: health
    };
  } catch (error) {
    console.warn('[Orchestra] Health check failed:', error);
    return {
      status: 'unhealthy',
      details: { error: error instanceof Error ? error.message : 'Unknown error' }
    };
  }
}

/**
 * Fetch available agents
 */
export async function getAgents(): Promise<Agent[]> {
  try {
    // Fetch all agents with a large page size to avoid pagination
    // Note: Backend expects /api/v1/agents/templates/ with trailing slash, query params go after
    const response = await apiRequest<{ results?: Agent[]; data?: Agent[]; count?: number } | Agent[]>('GET', '/api/v1/agents/templates/?page_size=200');
    
    if (Array.isArray(response)) {
      return response;
    }
    
    return response?.results || response?.data || [];
  } catch (error) {
    console.error('[Orchestra] Failed to fetch agents:', error);
    return [];
  }
}

/**
 * Fetch agent instances (orchestrations)
 */
export async function getInstances(): Promise<AgentInstance[]> {
  try {
    const response = await apiRequest<any>('GET', '/api/v1/orchestrations/');
    
    // Handle nested data structure from API
    if (response?.data?.instances) {
      return response.data.instances;
    }
    
    // Fallback to other formats
    if (Array.isArray(response)) {
      return response;
    }
    
    return response?.results || response?.data || [];
  } catch (error) {
    console.error('[Orchestra] Failed to fetch instances:', error);
    return [];
  }
}

/**
 * Execute agent task
 */
export async function executeAgent(
  agentType: string, 
  taskDescription: string, 
  parameters?: Record<string, any>
): Promise<AgentInstance> {
  return apiRequest<AgentInstance>('POST', '/api/v1/execute/', {
    agent_type: agentType,
    task_description: taskDescription,
    parameters
  });
}

/**
 * Get WebSocket base URL for connections
 */
export function getWebSocketBase(): string {
  return ORCH_WS_BASE;
}