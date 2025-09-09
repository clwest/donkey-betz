/**
 * DBAO (Donkey Betz Agent Orchestra) Service for React Native
 * Provides agent orchestration and sports betting functionality
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { DBAO_CONFIG, getApiUrl, AgentType, SupportedSport } from '../config/dbao.config';

// Types
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

export interface AgentExecutionRequest {
  agent_type: string;
  task_description: string;
  parameters?: Record<string, any>;
}

export interface AgentSuggestion {
  agent: Agent;
  confidence: number;
  reasoning: string;
}

export interface BettingOpportunity {
  id: string;
  sport: string;
  game: string;
  bet_type: string;
  recommendation: 'bet' | 'avoid' | 'hedge';
  edge_percentage: number;
  confidence: number;
  suggested_stake: number;
  risk_level: 'low' | 'medium' | 'high';
  reasoning: string;
  odds: {
    current: number;
    fair_value: number;
    implied_probability: number;
  };
  created_at: string;
}

export interface BettingAnalysisRequest {
  sport: string;
  game_id?: string;
  analysis_type: 'game' | 'prop' | 'arbitrage' | 'live';
  parameters?: {
    min_edge?: number;
    confidence_threshold?: number;
    bankroll?: number;
    risk_tolerance?: 'conservative' | 'moderate' | 'aggressive';
  };
}

// HTTP Client with React Native optimizations
class DBAOHttpClient {
  private baseURL: string;
  private defaultTimeout: number;
  private maxRetries: number;
  private authToken: string | null = null;

  constructor() {
    this.baseURL = DBAO_CONFIG.API_BASE_URL;
    this.defaultTimeout = DBAO_CONFIG.DEFAULT_TIMEOUT;
    this.maxRetries = DBAO_CONFIG.MAX_RETRIES;
    this.loadAuthToken();
  }

  private async loadAuthToken(): Promise<void> {
    try {
      const token = await AsyncStorage.getItem('authToken');
      this.authToken = token || DBAO_CONFIG.DEFAULT_AUTH_TOKEN;
    } catch (error) {
      console.warn('[DBAO] Failed to load auth token:', error);
      this.authToken = DBAO_CONFIG.DEFAULT_AUTH_TOKEN;
    }
  }

  private async makeRequest<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any,
    options: {
      retries?: number;
      timeout?: number;
    } = {}
  ): Promise<T> {
    const { retries = this.maxRetries, timeout = this.defaultTimeout } = options;
    const url = endpoint.startsWith('http') ? endpoint : getApiUrl(endpoint);

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
          'X-Orchestrator': 'DBAO-ReactNative',
        };

        if (this.authToken) {
          headers.Authorization = `Token ${this.authToken}`;
        }

        const response = await fetch(url, {
          method,
          headers,
          body: data ? JSON.stringify(data) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Authentication required');
          }
          if (response.status === 404) {
            throw new Error('Resource not found');
          }
          if (response.status === 429) {
            // Rate limited - exponential backoff
            const delay = Math.pow(2, attempt) * 1000;
            await new Promise(resolve => setTimeout(resolve, delay));
            continue;
          }
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        return result;

      } catch (error: any) {
        const isLastAttempt = attempt === retries;
        
        if (error.name === 'AbortError') {
          if (!isLastAttempt) {
            console.warn(`[DBAO] Request timeout, retry ${attempt + 1}/${retries + 1}`);
            continue;
          }
          throw new Error('Request timeout');
        }

        if (error.message.includes('Network request failed') || error.message.includes('fetch')) {
          if (!isLastAttempt) {
            const delay = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
            console.warn(`[DBAO] Network error, retrying in ${Math.round(delay)}ms`);
            await new Promise(resolve => setTimeout(resolve, delay));
            continue;
          }
        }

        if (isLastAttempt) {
          console.error(`[DBAO] Request failed after ${retries + 1} attempts:`, error);
          throw error;
        }
      }
    }

    throw new Error('Max retries exceeded');
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.makeRequest<T>('GET', endpoint);
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>('POST', endpoint, data);
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>('PUT', endpoint, data);
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.makeRequest<T>('DELETE', endpoint);
  }
}

// DBAO Service
export class DBAOService {
  private static client = new DBAOHttpClient();

  // Agent Management
  static async getAgents(): Promise<Agent[]> {
    try {
      const data = await this.client.get<{ results?: Agent[]; data?: Agent[] } | Agent[]>('/agents');
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.results || data?.data || [];
    } catch (error) {
      console.error('[DBAO] Failed to fetch agents:', error);
      return [];
    }
  }

  static async getAgent(id: string): Promise<Agent | null> {
    try {
      return await this.client.get<Agent>(`/agents/${id}`);
    } catch (error) {
      console.warn('[DBAO] Failed to fetch agent:', error);
      return null;
    }
  }

  // Agent Execution
  static async executeAgent(request: AgentExecutionRequest): Promise<AgentInstance | null> {
    try {
      return await this.client.post<AgentInstance>('/execute', request);
    } catch (error) {
      console.error('[DBAO] Failed to execute agent:', error);
      throw new Error(`Agent execution failed: ${error.message}`);
    }
  }

  static async suggestAgents(taskDescription: string): Promise<AgentSuggestion[]> {
    try {
      const data = await this.client.post<{ suggestions?: AgentSuggestion[] } | AgentSuggestion[]>(
        '/suggest',
        { task_description: taskDescription }
      );
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.suggestions || [];
    } catch (error) {
      console.warn('[DBAO] Failed to get agent suggestions:', error);
      return [];
    }
  }

  static async routeTask(taskDescription: string): Promise<Agent | null> {
    try {
      const data = await this.client.post<{ agent: Agent } | Agent>(
        '/route',
        { task_description: taskDescription }
      );
      
      return 'agent' in data ? data.agent : data;
    } catch (error) {
      console.warn('[DBAO] Failed to route task:', error);
      return null;
    }
  }

  // Agent Instances
  static async getInstances(): Promise<AgentInstance[]> {
    try {
      const data = await this.client.get<{ results?: AgentInstance[]; data?: AgentInstance[] } | AgentInstance[]>('/instances');
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.results || data?.data || [];
    } catch (error) {
      console.error('[DBAO] Failed to fetch instances:', error);
      return [];
    }
  }

  static async getInstance(id: string): Promise<AgentInstance | null> {
    try {
      return await this.client.get<AgentInstance>(`/instances/${id}`);
    } catch (error) {
      console.warn('[DBAO] Failed to fetch instance:', error);
      return null;
    }
  }

  static async getInstanceStatus(id: string): Promise<AgentInstance | null> {
    try {
      return await this.client.get<AgentInstance>(`/status/${id}`);
    } catch (error) {
      console.warn('[DBAO] Failed to fetch instance status:', error);
      return null;
    }
  }

  // Sports Betting Integration
  static async analyzeBettingOpportunity(request: BettingAnalysisRequest): Promise<BettingOpportunity[]> {
    try {
      const data = await this.client.post<{ opportunities?: BettingOpportunity[] } | BettingOpportunity[]>(
        '/betting/analyze',
        request
      );
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.opportunities || [];
    } catch (error) {
      console.warn('[DBAO] Failed to analyze betting opportunity:', error);
      return [];
    }
  }

  static async getLiveOpportunities(sport?: string): Promise<BettingOpportunity[]> {
    try {
      const endpoint = sport ? `/betting/live?sport=${encodeURIComponent(sport)}` : '/betting/live';
      const data = await this.client.get<{ opportunities?: BettingOpportunity[] } | BettingOpportunity[]>(endpoint);
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.opportunities || [];
    } catch (error) {
      console.warn('[DBAO] Failed to get live opportunities:', error);
      return [];
    }
  }

  static async getArbitrageOpportunities(): Promise<BettingOpportunity[]> {
    try {
      const data = await this.client.get<{ opportunities?: BettingOpportunity[] } | BettingOpportunity[]>('/betting/arbitrage');
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.opportunities || [];
    } catch (error) {
      console.warn('[DBAO] Failed to get arbitrage opportunities:', error);
      return [];
    }
  }

  // Health Check
  static async healthCheck(): Promise<{ status: string; version: string } | null> {
    try {
      return await this.client.get<{ status: string; version: string }>('/health');
    } catch (error) {
      console.warn('[DBAO] Health check failed:', error);
      return null;
    }
  }
}