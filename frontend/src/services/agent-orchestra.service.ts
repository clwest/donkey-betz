import { UCWSF_CONFIG } from './api.config';
import { Logger } from '../utils/logger';
import { toast } from 'sonner';

// DBAO API Configuration - unified on port 8000
const DBAO_BASE_URL = (import.meta.env.VITE_DBAO_API_URL || 'http://localhost:8000/api').replace(/\/$/,'');

// Helper to get current auth token dynamically
const getAuthToken = () => localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || '';

// Agent Orchestra Types
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
  execution_id: string;
  template: Agent;
  template_name?: string;
  task_description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result: any;
  error_message: string | null;
  error_details?: any;
  token_usage: any;
  total_cost: number;
  execution_time_seconds: number;
  user: number;
  created_at: string;
  updated_at: string;
  current_step?: string;
  progress_percentage?: number;
  started_at?: string;
  completed_at?: string;
}

export interface AgentOrchestration {
  id: string;
  task_description: string;
  agent_sequence: Agent[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  results: any[];
  current_step: number;
  total_steps: number;
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

export interface OrchestrationRequest {
  task_description: string;
  agents?: string[];
  auto_route?: boolean;
}

// Odds calculation and sports betting tools for Agent Orchestra
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

export interface OddsCalculationRequest {
  american_odds: string | number;
  win_probability: number;
  bankroll: number;
  kelly_fraction: number;
}

export interface OddsCalculationResponse {
  decimal: number;
  implied_probability: number;
  ev_percentage: number;
  kelly_percentage: number;
  recommended_stake: number;
  warnings: string[];
}

/**
 * Enhanced DBAO REST Client with comprehensive error handling and retry logic
 */
export class AgentOrchestraService {
  private static readonly BASE_ENDPOINTS = {
    AGENTS: '/v1/agents/list/',  // Fixed to use correct endpoint
    EXECUTE: '/v1/agents/execute/',  // Fixed to use correct endpoint path
    SUGGEST: '/v1/agents/suggest/',  // Fixed to use correct endpoint path
    ROUTE: '/v1/agents/route/',  // Fixed to use correct endpoint path
    INSTANCES: '/v1/instances/',  // Fixed: Use the correct instances endpoint
    STATUS: '/v1/agents/status/',  // Fixed to use correct endpoint path
    ORCHESTRATE: '/v1/agents/orchestrate/',  // Fixed to use correct endpoint path
    ORCHESTRATIONS: '/v1/orchestrations/',
    BETTING: '/v1/betting/',
    ODDS: '/v1/odds/',  // Sports odds uses v1
    HEALTH: '/v1/agents/health/'  // Fixed to use correct endpoint path
  } as const;

  // Mock data for development when DBAO backend is not available
  private static readonly MOCK_AGENTS: Agent[] = [
    {
      id: '1',
      name: 'Content Writer',
      description: 'Expert at creating engaging blog posts and articles',
      specialization: 'content-creation',
      capabilities: ['blog-writing', 'article-creation', 'copywriting'],
      required_tools: ['web-search', 'grammar-check'],
      system_prompt: 'You are an expert content writer...',
      personality_traits: { creativity: 0.8, analytical: 0.6 },
      llm_provider: 'openai',
      llm_model: 'gpt-5-mini',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2', 
      name: 'Data Analyst',
      description: 'Specialized in analyzing data and creating insights',
      specialization: 'data-analysis',
      capabilities: ['data-processing', 'visualization', 'reporting'],
      required_tools: ['python', 'pandas', 'matplotlib'],
      system_prompt: 'You are a skilled data analyst...',
      personality_traits: { analytical: 0.9, creativity: 0.4 },
      llm_provider: 'openai',
      llm_model: 'gpt-5-mini',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '3',
      name: 'Poker Vlogger Agent',
      description: 'Creates engaging poker vlogs with odds analysis, hand breakdowns, and strategy insights',
      specialization: 'poker-content',
      capabilities: [
        'poker-hand-analysis', 
        'pot-odds-calculation', 
        'kelly-criterion', 
        'bankroll-management',
        'vlog-script-writing',
        'tournament-strategy',
        'cash-game-analysis',
        'poker-storytelling'
      ],
      required_tools: ['odds-calculator', 'video-editing-prompts', 'poker-database'],
      system_prompt: `You are a professional poker vlogger who creates engaging content about poker strategy, hand analysis, and bankroll management. 
      
You have access to odds calculation tools and can:
- Analyze poker hands with pot odds and equity calculations
- Apply Kelly Criterion for optimal bet sizing
- Create compelling narratives around poker sessions
- Explain complex poker concepts in accessible ways
- Generate video scripts with proper pacing and hooks

Always include mathematical backing for your analysis and make content both educational and entertaining.`,
      personality_traits: { 
        analytical: 0.90, 
        storytelling: 0.85, 
        risk_assessment: 0.95,
        entertainment: 0.80
      },
      llm_provider: 'openai',
      llm_model: 'gpt-5-mini',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '4',
      name: 'Finance Intelligence Agent',
      description: 'Wall Street-grade financial analysis with 21+ real-time APIs',
      specialization: 'financial-analysis',
      capabilities: [
        'sec_filing_analysis',
        'real_time_stock_quotes',
        'market_sentiment_analysis',
        'reddit_sentiment_tracking',
        'competitive_intelligence',
        'industry_landscape_analysis',
        'crypto_market_analysis',
        'news_sentiment_aggregation',
        'technical_analysis',
        'fundamental_analysis',
        'options_flow_analysis',
        'insider_trading_tracking'
      ],
      required_tools: ['SEC', 'Alpha Vantage', 'Polygon.io', 'Yahoo Finance', 'Finnhub', 'Reddit', 'News API', 'CoinGecko'],
      system_prompt: 'You are a Wall Street financial analyst with access to real-time market data...',
      personality_traits: { analytical: 0.98, risk_assessment: 0.95, detail_oriented: 0.92 },
      llm_provider: 'openai',
      llm_model: 'gpt-5-mini',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

  /**
   * Normalizes endpoints to handle both /path and /path/ formats
   * Don't add trailing slash if the endpoint has query parameters
   */
  private static normalizeEndpoint(endpoint: string): string {
    // Don't add trailing slash if there are query parameters
    if (endpoint.includes('?')) {
      return endpoint;
    }
    return endpoint.endsWith('/') ? endpoint : `${endpoint}/`;
  }

  /**
   * Enhanced API call with retry logic and comprehensive error handling
   * Uses DBAO-specific API endpoints instead of main API
   */
  private static async makeRequest<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any,
    options: {
      retries?: number;
      backoffMs?: number;
      throwOnError?: boolean;
    } = {}
  ): Promise<T> {
    const { retries = 3, backoffMs = 1000, throwOnError = true } = options;
    const normalizedEndpoint = this.normalizeEndpoint(endpoint);
    const url = `${DBAO_BASE_URL}${normalizedEndpoint}`;
    console.log('[DBAO] makeRequest - endpoint:', endpoint, 'normalized:', normalizedEndpoint, 'final URL:', url);
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const config: RequestInit = { 
          method,
          headers: {
            'Content-Type': 'application/json',
            'X-Orchestrator': 'DBAO-Frontend',
            'Authorization': `Token ${getAuthToken()}`
          }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
          config.body = JSON.stringify(data);
        }

        const response = await fetch(url, config);
        const responseText = await response.text();

        if (!response.ok) {
          console.error(`[DBAO] ${method} ${url} failed:`, responseText);
          if (response.status === 401) {
            toast.error('Authentication required');
            Logger.warn('DBAO', `Unauthorized access to ${url}`, { endpoint: url });
            if (throwOnError) throw new Error(`Unauthorized: ${responseText}`);
            return null as T;
          }
          
          if (response.status === 404) {
            Logger.warn('DBAO', `Resource not found: ${url}`);
            if (throwOnError) throw new Error(`Not found: ${responseText}`);
            return null as T;
          }
          
          throw new Error(responseText || `HTTP ${response.status} ${response.statusText}`);
        }

        Logger.api(method, url, { success: true, attempt: attempt + 1 });
        
        // Parse JSON if we have content
        if (responseText.trim()) {
          return JSON.parse(responseText);
        }
        return {} as T;
        
      } catch (error: any) {
        const isLastAttempt = attempt === retries;
        
        // Handle network errors
        if (error instanceof TypeError && error.message.includes('fetch')) {
          if (!isLastAttempt) {
            const delay = backoffMs * Math.pow(2, attempt) + Math.random() * 1000; // Add jitter
            Logger.warn('DBAO', `Network error, retrying in ${Math.round(delay)}ms`, {
              attempt: attempt + 1,
              error: error.message,
              url
            });
            await new Promise(resolve => setTimeout(resolve, delay));
            continue;
          }
        }
        
        // Log and handle final error
        const userMessage = error.message || 'An unexpected error occurred';
        
        Logger.error('DBAO', {
          message: `API call failed: ${method} ${url}`,
          userMessage,
          attempts: attempt + 1
        });
        
        if (!error.message?.includes('Unauthorized')) {
          toast.error(userMessage);
        }
        
        if (throwOnError) throw error;
        return null as T;
      }
    }
    
    throw new Error(`Max retries (${retries}) exceeded`);
  }

  // Agent Management
  static async getAgents(): Promise<Agent[]> {
    try {
      // Fetch all agents with a large page size to get all 56+ agents
      const endpoint = `${this.BASE_ENDPOINTS.AGENTS}?page_size=100`;
      console.log('[DBAO] getAgents endpoint:', endpoint);
      const data = await this.makeRequest<{ results?: Agent[]; data?: Agent[] } | Agent[]>(
        'GET', 
        endpoint
      );
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.results || data?.data || [];
    } catch (error) {
      Logger.warn('DBAO', 'Backend agent endpoints not available, using mock data', error);
      // Return mock agents when backend is not available
      return [...this.MOCK_AGENTS];
    }
  }

  static async getAgent(id: string): Promise<Agent | null> {
    try {
      return await this.makeRequest<Agent>(
        'GET', 
        `${this.BASE_ENDPOINTS.AGENTS}/${id}`,
        undefined,
        { throwOnError: false }
      );
    } catch (error) {
      Logger.warn('DBAO', 'Backend agent endpoint not available, using mock data', error);
      // Return mock agent when backend is not available
      return this.MOCK_AGENTS.find(agent => agent.id === id) || null;
    }
  }

  // Agent Execution
  static async executeAgent(request: AgentExecutionRequest): Promise<AgentInstance | null> {
    const response = await this.makeRequest<any>(
      'POST', 
      this.BASE_ENDPOINTS.EXECUTE, 
      request
    );
    
    // Transform the response to match AgentInstance interface
    if (response && response.success) {
      // Get the template info from the backend response or fetch the agent template
      let template = null;
      
      if (response.template_id) {
        // Try to get the full template from the agents endpoint
        try {
          template = await this.getAgent(response.template_id);
        } catch (error) {
          console.warn('Failed to fetch template details:', error);
        }
      }
      
      // Fallback template if we couldn't fetch the full one
      if (!template) {
        template = {
          id: response.template_id || request.agent_type || 'unknown',
          name: response.template_name || response.agent_type || 'Unknown Agent',
          description: response.agent_description || request.task_description || 'Agent execution',
          specialization: response.agent_specialization || request.agent_type || 'general',
          capabilities: [],
          required_tools: [],
          system_prompt: '',
          personality_traits: {},
          llm_provider: 'openai',
          llm_model: 'gpt-5-mini',
          created_at: response.created_at || new Date().toISOString(),
          updated_at: response.updated_at || new Date().toISOString()
        };
      }

      return {
        id: response.instance_id || response.id,
        execution_id: response.execution_id || response.instance_id,
        template,
        task_description: request.task_description,
        status: response.status === 'running' ? 'processing' : response.status,
        result: response.result || null,
        error_message: response.error_message || null,
        error_details: response.error_details || null,
        token_usage: response.token_usage || {},
        total_cost: parseFloat(response.total_cost || '0'),
        execution_time_seconds: response.execution_time_seconds || response.execution_time || 0,
        user: response.user || 1,
        created_at: response.created_at || new Date().toISOString(),
        updated_at: response.updated_at || new Date().toISOString(),
        current_step: response.current_step,
        progress_percentage: response.progress_percentage || 0,
        started_at: response.started_at,
        completed_at: response.completed_at
      };
    }
    
    return null;
  }

  static async suggestAgent(taskDescription: string): Promise<AgentSuggestion[]> {
    try {
      const data = await this.makeRequest<{ suggestions?: AgentSuggestion[] } | AgentSuggestion[]>(
        'POST', 
        this.BASE_ENDPOINTS.SUGGEST, 
        { task_description: taskDescription }
      );
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.suggestions || [];
    } catch (error) {
      Logger.warn('DBAO', 'Failed to get agent suggestions', error);
      return [];
    }
  }

  static async routeTask(taskDescription: string): Promise<Agent | null> {
    try {
      const data = await this.makeRequest<{ agent: Agent } | Agent>(
        'POST', 
        this.BASE_ENDPOINTS.ROUTE, 
        { task_description: taskDescription }
      );
      
      return 'agent' in data ? data.agent : data;
    } catch (error) {
      Logger.warn('DBAO', 'Failed to route task', error);
      return null;
    }
  }

  // Agent Instances
  static async getInstances(): Promise<AgentInstance[]> {
    try {
      const data = await this.makeRequest<{ results?: any[]; data?: any[] } | any[]>(
        'GET', 
        this.BASE_ENDPOINTS.INSTANCES
      );
      
      let instances: any[] = [];
      if (Array.isArray(data)) {
        instances = data;
      } else {
        instances = data?.results || data?.data || [];
      }
      
      // Transform backend instances to match our interface
      return instances.map((instance): AgentInstance => ({
        id: instance.id,
        execution_id: instance.execution_id,
        template: {
          id: instance.template || 'unknown',
          name: instance.template_name || 'Unknown Agent',
          description: instance.task_description || 'Agent execution',
          specialization: instance.task_type || 'general',
          capabilities: [],
          required_tools: [],
          system_prompt: '',
          personality_traits: {},
          llm_provider: 'openai',
          llm_model: 'gpt-5-mini',
          created_at: instance.created_at,
          updated_at: instance.updated_at
        },
        template_name: instance.template_name,
        task_description: instance.task_description,
        status: instance.status as 'pending' | 'running' | 'completed' | 'failed',
        result: instance.result,
        error_message: instance.error_message,
        error_details: instance.error_details,
        token_usage: instance.token_usage || {},
        total_cost: parseFloat(instance.total_cost || '0'),
        execution_time_seconds: instance.execution_time_seconds || 0,
        user: instance.user || 1,
        created_at: instance.created_at,
        updated_at: instance.updated_at,
        current_step: instance.current_step,
        progress_percentage: instance.progress_percentage || 0,
        started_at: instance.started_at,
        completed_at: instance.completed_at
      }));
    } catch (error) {
      Logger.error('DBAO', error);
      return [];
    }
  }

  static async getInstance(id: string): Promise<AgentInstance | null> {
    return this.makeRequest<AgentInstance>(
      'GET', 
      `${this.BASE_ENDPOINTS.INSTANCES}/${id}`,
      undefined,
      { throwOnError: false }
    );
  }

  static async deleteInstance(id: string): Promise<boolean> {
    try {
      await this.makeRequest<any>(
        'DELETE',
        `${this.BASE_ENDPOINTS.INSTANCES}${id}/`
      );
      return true;
    } catch (error: any) {
      Logger.warn('DBAO', { message: 'Delete endpoint not available, simulating local delete', error, instanceId: id });
      
      // If backend doesn't support delete yet, we can simulate it by just removing from frontend
      // This provides the UI functionality while we wait for backend implementation
      if (error.message?.includes('403') || error.message?.includes('404') || error.message?.includes('Method not allowed')) {
        Logger.info('DBAO', `Simulating delete for instance ${id} (backend delete not yet implemented)`);
        return true; // Return true to allow frontend deletion
      }
      return false;
    }
  }

  static async deleteMultipleInstances(ids: string[]): Promise<{ successful: string[], failed: string[] }> {
    const successful: string[] = [];
    const failed: string[] = [];
    
    // Delete instances in parallel but with a limit to avoid overwhelming the server
    const batchSize = 5;
    for (let i = 0; i < ids.length; i += batchSize) {
      const batch = ids.slice(i, i + batchSize);
      const promises = batch.map(async (id) => {
        const success = await this.deleteInstance(id);
        if (success) {
          successful.push(id);
        } else {
          failed.push(id);
        }
      });
      
      await Promise.all(promises);
    }
    
    return { successful, failed };
  }

  static async getInstanceStatus(id: string): Promise<AgentInstance | null> {
    return this.makeRequest<AgentInstance>(
      'GET', 
      `${this.BASE_ENDPOINTS.STATUS}/${id}`,
      undefined,
      { throwOnError: false }
    );
  }

  // Orchestrations
  static async orchestrateTask(request: OrchestrationRequest): Promise<AgentOrchestration | null> {
    return this.makeRequest<AgentOrchestration>(
      'POST', 
      this.BASE_ENDPOINTS.ORCHESTRATE, 
      request
    );
  }

  static async getOrchestrations(): Promise<AgentOrchestration[]> {
    try {
      const data = await this.makeRequest<{ results?: AgentOrchestration[]; data?: AgentOrchestration[] } | AgentOrchestration[]>(
        'GET', 
        this.BASE_ENDPOINTS.ORCHESTRATIONS
      );
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.results || data?.data || [];
    } catch (error) {
      Logger.error('DBAO', error);
      return [];
    }
  }

  static async getOrchestration(id: string): Promise<AgentOrchestration | null> {
    return this.makeRequest<AgentOrchestration>(
      'GET', 
      `${this.BASE_ENDPOINTS.ORCHESTRATIONS}/${id}`,
      undefined,
      { throwOnError: false }
    );
  }

  // Sports Betting Live Opportunities
  static async getLiveOpportunities(): Promise<BettingOpportunity[]> {
    try {
      console.log('[DBAO] Fetching live betting opportunities');
      const data = await this.makeRequest<{ opportunities?: BettingOpportunity[]; success?: boolean } | BettingOpportunity[]>(
        'GET', 
        '/v1/sports/live-opportunities/'
      );
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.opportunities || [];
    } catch (error) {
      console.warn('[DBAO] Live opportunities unavailable, providing fallback');
      
      // Return empty array when endpoint is unavailable
      return [];
    }
  }

  // Agent Orchestra Tools - Odds Calculation & Sports Betting
  static async calculateOdds(request: OddsCalculationRequest): Promise<OddsCalculationResponse> {
    try {
      console.log('[DBAO] Calculating odds for agent:', request);
      const data = await this.makeRequest<OddsCalculationResponse>(
        'POST', 
        `${this.BASE_ENDPOINTS.ODDS}/calculate`, 
        request
      );
      
      return data;
    } catch (error) {
      console.warn('[DBAO] Odds calculation unavailable, using local fallback');
      
      // Local fallback calculation
      const american = typeof request.american_odds === 'string' 
        ? parseFloat(request.american_odds) 
        : request.american_odds;
      
      const decimal = american > 0 ? (american / 100) + 1 : (100 / Math.abs(american)) + 1;
      const impliedProbability = 1 / decimal;
      const edge = request.win_probability - impliedProbability;
      const kellyPercentage = edge > 0 ? (edge / (decimal - 1)) * request.kelly_fraction : 0;
      const recommendedStake = Math.max(0, kellyPercentage * request.bankroll);
      
      const warnings: string[] = [];
      if (edge <= 0) warnings.push('No positive expected value detected');
      if (kellyPercentage > 0.25) warnings.push('High Kelly percentage - consider reducing stake');
      
      return {
        decimal,
        implied_probability: impliedProbability,
        ev_percentage: edge * 100,
        kelly_percentage: kellyPercentage,
        recommended_stake: recommendedStake,
        warnings
      };
    }
  }

  static async analyzeBettingOpportunity(request: { 
    sport: string; 
    odds?: Array<{ home: number; away: number; [key: string]: number }>; 
    context?: string;
  }): Promise<BettingOpportunity[]> {
    try {
      console.log('[DBAO] Analyzing betting opportunity for agent:', request);
      const data = await this.makeRequest<{ opportunities?: BettingOpportunity[] } | BettingOpportunity[]>(
        'POST', 
        `${this.BASE_ENDPOINTS.BETTING}/analyze`, 
        request
      );
      
      if (Array.isArray(data)) {
        return data;
      }
      return data?.opportunities || [];
    } catch (error) {
      console.warn('[DBAO] Betting analysis unavailable, providing mock opportunity');
      
      // Return sample opportunity for agent testing
      return [{
        id: `mock-${Date.now()}`,
        sport: request.sport,
        game: 'Sample Game',
        bet_type: 'moneyline',
        recommendation: 'bet' as const,
        edge_percentage: 5.2,
        confidence: 0.75,
        suggested_stake: 50,
        risk_level: 'medium' as const,
        reasoning: 'Mock analysis for agent development',
        odds: {
          current: 150,
          fair_value: 140,
          implied_probability: 0.4
        },
        created_at: new Date().toISOString(),
      }];
    }
  }

  // Health Check
  static async healthCheck(): Promise<{ status: string; version: string } | null> {
    try {
      return await this.makeRequest<{ status: string; version: string }>(
        'GET', 
        this.BASE_ENDPOINTS.HEALTH,
        undefined,
        { throwOnError: false, retries: 1 }
      );
    } catch (error) {
      // Try the main API health endpoint if DBAO health is not available
      try {
        const response = await fetch(`${DBAO_BASE_URL}/health/`, {
          headers: {
            'Authorization': `Token ${getAuthToken()}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          return {
            status: data.status || 'healthy',
            version: data.service || 'ai-content-studio-api'
          };
        }
      } catch (fallbackError) {
        Logger.warn('DBAO', 'Health check failed for both DBAO and main API', fallbackError);
      }
      
      return null;
    }
  }
}

/**
 * Enhanced WebSocket Connection Manager with improved reconnection logic
 */
export class AgentWebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private baseReconnectDelay = 1000;
  private callbacks: Map<string, Function[]> = new Map();
  private connectionState: 'idle' | 'connecting' | 'open' | 'closing' | 'closed' = 'idle';
  private messageQueue: any[] = [];
  private heartbeatInterval: number | null = null;

  constructor(
    private token: string,
    private baseUrl: string = import.meta.env.VITE_DBAO_WS_URL || import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  ) {
    // UCWSF: Feature gate WebSocket connections
    if (!UCWSF_CONFIG.websockets) {
      Logger.warn('UCWSF', 'WebSockets disabled - using no-op manager');
      return;
    }
    
    // Validate WebSocket URL
    if (!baseUrl.startsWith('ws://') && !baseUrl.startsWith('wss://')) {
      throw new Error('WebSocket URL must start with ws:// or wss://');
    }
  }

  /**
   * Connect to WebSocket with enhanced error handling and state management
   */
  connect(endpoint: 'agents' | 'dashboard' = 'agents'): Promise<void> {
    // UCWSF: Skip WebSocket connection if disabled
    if (!UCWSF_CONFIG.websockets) {
      Logger.info('UCWSF', 'WebSocket connection skipped (disabled by feature flag)');
      return Promise.resolve();
    }
    
    if (this.connectionState === 'connecting' || this.connectionState === 'open') {
      Logger.warn('DBAO WebSocket', 'Already connected or connecting');
      return Promise.resolve();
    }

    this.connectionState = 'connecting';

    return new Promise((resolve, reject) => {
      try {
        // Construct WebSocket URL for DBAO
        const dbaoWsUrl = import.meta.env.VITE_DBAO_WS_URL || 'ws://localhost:8000';
        // Use the current authentication token
        const currentToken = localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || '';
        const wsUrl = `${dbaoWsUrl}/ws/${endpoint}/?token=${currentToken}`;
        Logger.debug('DBAO WebSocket', `Connecting to ${wsUrl}`);
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          Logger.api('WebSocket', 'Connected successfully');
          this.connectionState = 'open';
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            let data;
            if (typeof event.data === 'string') {
              try {
                data = JSON.parse(event.data);
              } catch {
                // Handle plain text messages
                data = { type: 'text', message: event.data };
              }
            } else {
              data = event.data;
            }
            
            this.handleMessage(data);
          } catch (error) {
            Logger.error('DBAO WebSocket', { message: 'Message parsing error', error });
          }
        };

        this.ws.onclose = (event) => {
          Logger.warn('DBAO WebSocket', `Connection closed: ${event.code} ${event.reason}`);
          this.connectionState = 'closed';
          this.stopHeartbeat();
          
          // Only attempt reconnect for unexpected closures
          if (event.code !== 1000) {
            this.attemptReconnect(endpoint);
          }
        };

        this.ws.onerror = (error) => {
          Logger.error('DBAO WebSocket', { message: 'Connection error', error });
          this.connectionState = 'closed';
          reject(error);
        };

      } catch (error) {
        this.connectionState = 'closed';
        Logger.error('DBAO WebSocket', { message: 'Failed to create connection', error });
        reject(error);
      }
    });
  }

  /**
   * Handle incoming WebSocket messages with error recovery
   */
  private handleMessage(data: any) {
    const { type } = data;
    Logger.debug('DBAO WebSocket', `Received message: ${type}`, data);
    
    const callbacks = this.callbacks.get(type) || [];
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        Logger.error('DBAO WebSocket', { message: 'Callback execution error', type, error });
      }
    });

    // Handle system messages
    if (type === 'pong') {
      Logger.debug('DBAO WebSocket', 'Heartbeat response received');
    }
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat() {
    this.stopHeartbeat(); // Clear any existing interval
    this.heartbeatInterval = window.setInterval(() => {
      if (this.connectionState === 'open') {
        this.send({ type: 'ping' });
      }
    }, 30000); // Send ping every 30 seconds
  }

  /**
   * Stop heartbeat interval
   */
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Flush queued messages when connection is restored
   */
  private flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  /**
   * Enhanced reconnection with exponential backoff and jitter
   */
  private attemptReconnect(endpoint: 'agents' | 'dashboard') {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      Logger.error('DBAO WebSocket', { message: 'Max reconnection attempts reached' });
      return;
    }

    this.reconnectAttempts++;
    
    // Exponential backoff with jitter: 1s → 2s → 4s → 8s → 15s (cap at 15s)
    const baseDelay = Math.min(this.baseReconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 15000);
    const jitter = Math.random() * 1000; // Add up to 1 second jitter
    const delay = baseDelay + jitter;

    Logger.warn('DBAO WebSocket', `Attempting to reconnect in ${Math.round(delay)}ms (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect(endpoint).catch((error) => {
        Logger.error('DBAO WebSocket', { message: 'Reconnection failed', error });
      });
    }, delay);
  }

  subscribe(eventType: string, callback: Function) {
    if (!this.callbacks.has(eventType)) {
      this.callbacks.set(eventType, []);
    }
    this.callbacks.get(eventType)!.push(callback);
  }

  unsubscribe(eventType: string, callback: Function) {
    const callbacks = this.callbacks.get(eventType);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Send message with queuing for offline resilience
   */
  send(message: any) {
    if (this.connectionState === 'open' && this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
        Logger.debug('DBAO WebSocket', 'Message sent', message);
      } catch (error) {
        Logger.error('DBAO WebSocket', { message: 'Failed to send message', error });
        this.messageQueue.push(message);
      }
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(message);
      Logger.warn('DBAO WebSocket', 'Message queued (not connected)', message);
      
      // Limit queue size to prevent memory issues
      if (this.messageQueue.length > 100) {
        this.messageQueue.shift(); // Remove oldest message
      }
    }
  }

  // Subscribe to specific instance updates
  subscribeToInstance(instanceId: string) {
    this.send({
      type: 'subscribe_instance',
      instance_id: instanceId
    });
  }

  // Subscribe to specific orchestration updates
  subscribeToOrchestration(orchestrationId: string) {
    this.send({
      type: 'subscribe_orchestration',
      orchestration_id: orchestrationId
    });
  }

  /**
   * Gracefully disconnect with cleanup
   */
  disconnect() {
    this.connectionState = 'closing';
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }
    
    this.connectionState = 'closed';
    this.callbacks.clear();
    this.messageQueue.length = 0;
    this.reconnectAttempts = 0;
    
    Logger.api('WebSocket', 'Disconnected');
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.connectionState === 'open' && this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get current connection state
   */
  getConnectionState(): 'idle' | 'connecting' | 'open' | 'closing' | 'closed' {
    return this.connectionState;
  }

  /**
   * Get connection statistics
   */
  getStats() {
    return {
      connectionState: this.connectionState,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      queuedMessages: this.messageQueue.length,
      subscribedEvents: Array.from(this.callbacks.keys()),
      isHeartbeatActive: this.heartbeatInterval !== null
    };
  }
}

// Singleton WebSocket manager instance
let wsManager: AgentWebSocketManager | null = null;

// Force reset the WebSocket manager (useful for development)
export const resetWebSocketManager = () => {
  if (wsManager) {
    wsManager.disconnect();
    wsManager = null;
  }
};

export const getWebSocketManager = (): AgentWebSocketManager => {
  if (!wsManager) {
    const token = localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || '';
    // Use DBAO WebSocket URL or fall back to main WebSocket URL
    const wsBaseUrl = import.meta.env.VITE_DBAO_WS_URL || import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    console.log('[DBAO] Creating WebSocket manager with URL:', wsBaseUrl);
    wsManager = new AgentWebSocketManager(token, wsBaseUrl);
  }
  return wsManager;
};

/**
 * Enhanced React Hook for WebSocket with state management
 */
export const useAgentWebSocket = () => {
  const manager = getWebSocketManager();
  
  const connect = async (endpoint: 'agents' | 'dashboard' = 'agents') => {
    try {
      if (!manager.isConnected()) {
        await manager.connect(endpoint);
        Logger.api('WebSocket Hook', 'Connected successfully');
      }
    } catch (error) {
      Logger.error('WebSocket Hook', { message: 'Connection failed', error });
      toast.error('Failed to connect to real-time updates');
      throw error;
    }
  };

  const subscribe = (eventType: string, callback: Function) => {
    manager.subscribe(eventType, callback);
    Logger.debug('WebSocket Hook', `Subscribed to ${eventType}`);
    return () => {
      manager.unsubscribe(eventType, callback);
      Logger.debug('WebSocket Hook', `Unsubscribed from ${eventType}`);
    };
  };

  const subscribeToInstance = (instanceId: string) => {
    if (!instanceId) {
      Logger.warn('WebSocket Hook', 'Invalid instance ID provided');
      return;
    }
    manager.subscribeToInstance(instanceId);
    Logger.debug('WebSocket Hook', `Subscribed to instance ${instanceId}`);
  };

  const subscribeToOrchestration = (orchestrationId: string) => {
    if (!orchestrationId) {
      Logger.warn('WebSocket Hook', 'Invalid orchestration ID provided');
      return;
    }
    manager.subscribeToOrchestration(orchestrationId);
    Logger.debug('WebSocket Hook', `Subscribed to orchestration ${orchestrationId}`);
  };

  const send = (message: any) => {
    if (!message || typeof message !== 'object') {
      Logger.warn('WebSocket Hook', 'Invalid message format');
      return;
    }
    manager.send(message);
  };

  const disconnect = () => {
    manager.disconnect();
    Logger.api('WebSocket Hook', 'Disconnected');
  };

  const isConnected = () => {
    return manager.isConnected();
  };

  const getConnectionState = () => {
    return manager.getConnectionState();
  };

  const getStats = () => {
    return manager.getStats();
  };

  return {
    connect,
    subscribe,
    subscribeToInstance,
    subscribeToOrchestration,
    send,
    disconnect,
    isConnected,
    getConnectionState,
    getStats
  };
};