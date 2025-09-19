import { apiClient } from './api.config';
import { API_CONFIG } from '../config/api.config';

export interface Agent {
  id: string;
  name: string;
  description: string;
  specialization: string;
  capabilities: Capability[];
  source_file?: string;
  llm_provider: string;
  llm_model: string;
  personality_traits: Record<string, number>;
  trigger_keywords: string[];
  confidence_threshold: number;
  priority: number;
  created_at: string;
  updated_at: string;
  system_prompt?: string;
  usage_stats?: {
    usage_count: number;
    success_count: number;
    success_rate: number;
    last_used?: string;
  };
}

export interface Capability {
  name: string;
  description: string;
  category: string;
  required_tools: string[];
}

export interface DiscoveryStats {
  total_agents: number;
  by_source: {
    claude_files: number;
    builtin: number;
    database: number;
  };
  by_specialization: Record<string, number>;
  total_capabilities: number;
  last_scan?: string;
}

export interface UserUsageStats {
  total_sessions: number;
  sessions_with_executions: number;
  execution_rate: number;
  most_active_period: string;
  favorite_agent: string;
}

export interface PerformanceStats {
  average_response_time: number;
  success_rate: number;
  most_popular_capability: string;
  peak_usage_time: string;
  total_agent_calls_today: number;
  cache_hit_rate: number;
}

export interface AgentSuggestion {
  id: string;
  name: string;
  description: string;
  specialization: string;
  capabilities: string[];
  confidence_score: number;
  reasoning: string;
}

class AgentDiscoveryService {
  /**
   * Get all agent templates (150 available!)
   */
  async getAgentTemplates() {
    const response = await apiClient.get(API_CONFIG.endpoints.agents.templates);
    return response.data || response;
  }

  /**
   * Execute an agent with a task
   */
  async executeAgent(agentName: string, task: string, priority: string = 'medium') {
    const response = await apiClient.post(API_CONFIG.endpoints.agents.execute, {
      agent_name: agentName,
      task: task,
      priority: priority
    });
    return response.data || response;
  }

  /**
   * Get execution history
   */
  async getExecutions(params?: { limit?: number; status?: string }) {
    let url = API_CONFIG.endpoints.agents.executions;
    if (params) {
      const queryParams = new URLSearchParams();
      if (params.limit) queryParams.append('limit', params.limit.toString());
      if (params.status) queryParams.append('status', params.status);
      const queryString = queryParams.toString();
      if (queryString) url += '?' + queryString;
    }
    const response = await apiClient.get(url);
    return response.data || response;
  }

  /**
   * Discover best agents for a task
   */
  async discoverAgentsForTask(task: string, count: number = 3) {
    const response = await apiClient.post(API_CONFIG.endpoints.agents.discover, {
      task: task,
      count: count
    });
    return response.data || response;
  }

  /**
   * Discover all available agents from all sources
   */
  async discoverAllAgents(refresh = false) {
    // Use templates endpoint which returns all 150 agents
    const templates = await this.getAgentTemplates();
    
    // Transform templates to agent format
    const agents = Array.isArray(templates) ? templates : (templates.results || []);
    
    return {
      success: true,
      agents: agents.map((template: any) => ({
        id: template.id || template.name,
        name: template.name,
        description: template.description || '',
        specialization: template.category || template.specialization || 'general',
        capabilities: template.capabilities || [],
        source_file: template.source_file,
        llm_provider: template.llm_provider || 'openai',
        llm_model: template.llm_model || 'gpt-4',
        personality_traits: template.personality_traits || {},
        trigger_keywords: template.trigger_keywords || [],
        confidence_threshold: template.confidence_threshold || 0.7,
        priority: template.priority || 5,
        created_at: template.created_at || new Date().toISOString(),
        updated_at: template.updated_at || new Date().toISOString(),
        system_prompt: template.system_prompt,
        usage_stats: template.usage_stats
      })),
      total: agents.length
    };
  }

  /**
   * Get detailed information about a specific agent
   */
  async getAgentDetails(agentId: string) {
    const response = await apiClient.get(`/api/v1/agents/${agentId}/details/`);
    return response.data || response;
  }

  /**
   * Get comprehensive discovery statistics
   */
  async getDiscoveryStats() {
    const templates = await this.getAgentTemplates();
    const agents = Array.isArray(templates) ? templates : (templates.results || []);
    
    // Calculate stats from templates
    const stats: DiscoveryStats = {
      total_agents: agents.length,
      by_source: {
        claude_files: 0,
        builtin: 0,
        database: agents.length
      },
      by_specialization: {},
      total_capabilities: 0,
      last_scan: new Date().toISOString()
    };
    
    // Count by category/specialization
    agents.forEach((agent: any) => {
      const spec = agent.category || agent.specialization || 'general';
      stats.by_specialization[spec] = (stats.by_specialization[spec] || 0) + 1;
      
      // Count capabilities
      if (agent.capabilities && Array.isArray(agent.capabilities)) {
        stats.total_capabilities += agent.capabilities.length;
      }
    });
    
    return {
      success: true,
      discovery_stats: stats
    };
  }

  /**
   * Refresh agent discovery cache
   */
  async refreshDiscovery() {
    // Reload templates
    const templates = await this.getAgentTemplates();
    return {
      success: true,
      message: 'Agent templates refreshed',
      agent_count: Array.isArray(templates) ? templates.length : (templates.results?.length || 0)
    };
  }

  /**
   * Suggest the best agent for a given task
   */
  async suggestAgentForTask(task: string) {
    // Use the discover endpoint
    const response = await this.discoverAgentsForTask(task, 3);
    
    if (response.agents && response.agents.length > 0) {
      return {
        success: true,
        suggested_agent: response.agents[0],
        alternatives: response.agents.slice(1)
      };
    }
    
    return {
      success: false,
      error: 'No suitable agents found'
    };
  }

  /**
   * Search for agents by capability
   */
  async searchAgentsByCapability(capability: string) {
    const allAgents = await this.discoverAllAgents();
    
    const filtered = allAgents.agents.filter((agent: Agent) => {
      return agent.capabilities.some((cap: Capability) => 
        cap.name.toLowerCase().includes(capability.toLowerCase()) ||
        cap.description.toLowerCase().includes(capability.toLowerCase())
      );
    });
    
    return {
      success: true,
      agents: filtered
    };
  }

  /**
   * Test agent suggestion with multiple tasks
   */
  async testAgentSuggestions(tasks: string[]) {
    const results = [];
    
    for (const task of tasks) {
      try {
        const response = await this.suggestAgentForTask(task);
        results.push({
          task,
          success: response.success,
          suggested_agent: response.suggested_agent,
          alternatives: response.alternatives || [],
          fallback_suggestions: response.fallback_suggestions || []
        });
      } catch (error) {
        results.push({
          task,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
    
    return results;
  }

  /**
   * Get agents grouped by specialization
   */
  async getAgentsBySpecialization() {
    const response = await this.discoverAllAgents();
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to discover agents');
    }
    
    const agentsBySpec: Record<string, Agent[]> = {};
    
    response.agents.forEach((agent: Agent) => {
      if (!agentsBySpec[agent.specialization]) {
        agentsBySpec[agent.specialization] = [];
      }
      agentsBySpec[agent.specialization].push(agent);
    });
    
    // Sort agents within each specialization by priority
    Object.keys(agentsBySpec).forEach(spec => {
      agentsBySpec[spec].sort((a, b) => b.priority - a.priority);
    });
    
    return agentsBySpec;
  }

  /**
   * Get high-priority agents (priority >= 8)
   */
  async getHighPriorityAgents() {
    const response = await this.discoverAllAgents();
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to discover agents');
    }
    
    return response.agents.filter((agent: Agent) => agent.priority >= 8);
  }

  /**
   * Get agents by source type
   */
  async getAgentsBySource() {
    const response = await this.discoverAllAgents();
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to discover agents');
    }
    
    const agentsBySource = {
      builtin: [] as Agent[],
      claude_files: [] as Agent[],
      database: [] as Agent[]
    };
    
    response.agents.forEach((agent: Agent) => {
      if (agent.source_file) {
        agentsBySource.claude_files.push(agent);
      } else if (agent.id.startsWith('db_')) {
        agentsBySource.database.push(agent);
      } else {
        agentsBySource.builtin.push(agent);
      }
    });
    
    return agentsBySource;
  }

  /**
   * Get all unique capabilities across all agents
   */
  async getAllCapabilities() {
    const response = await this.discoverAllAgents();
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to discover agents');
    }
    
    const capabilitiesMap = new Map<string, Capability>();
    
    response.agents.forEach((agent: Agent) => {
      if (agent.capabilities && Array.isArray(agent.capabilities)) {
        agent.capabilities.forEach((cap: Capability) => {
          capabilitiesMap.set(cap.name, cap);
        });
      }
    });
    
    return Array.from(capabilitiesMap.values()).sort((a, b) => 
      a.name.localeCompare(b.name)
    );
  }

  /**
   * Get agents that can handle multiple capabilities
   */
  async getMultiCapabilityAgents() {
    const response = await this.discoverAllAgents();
    
    if (!response.success) {
      throw new Error(response.error || 'Failed to discover agents');
    }
    
    return response.agents
      .filter((agent: Agent) => agent.capabilities && agent.capabilities.length > 3)
      .sort((a, b) => (b.capabilities?.length || 0) - (a.capabilities?.length || 0));
  }

  /**
   * Analyze agent ecosystem health
   */
  async analyzeEcosystemHealth() {
    const [agentsResponse, statsResponse] = await Promise.all([
      this.discoverAllAgents(),
      this.getDiscoveryStats()
    ]);
    
    if (!agentsResponse.success || !statsResponse.success) {
      throw new Error('Failed to analyze ecosystem');
    }
    
    const agents: Agent[] = agentsResponse.agents;
    const stats: DiscoveryStats = statsResponse.discovery_stats;
    
    return {
      total_agents: agents.length,
      health_score: this.calculateHealthScore(agents, stats),
      coverage: {
        specializations: Object.keys(stats.by_specialization).length,
        providers: new Set(agents.map(a => a.llm_provider)).size,
        total_capabilities: stats.total_capabilities,
        average_capabilities_per_agent: stats.total_capabilities / agents.length
      },
      recommendations: this.generateHealthRecommendations(agents, stats)
    };
  }

  private calculateHealthScore(agents: Agent[], stats: DiscoveryStats): number {
    let score = 0;
    
    // Base score from agent count
    score += Math.min(agents.length * 0.5, 40); // Max 40 points for agent count (150 agents = 40 points)
    
    // Diversity score
    const specializations = Object.keys(stats.by_specialization).length;
    score += Math.min(specializations * 8, 32); // Max 32 points for specialization diversity
    
    // Capability coverage
    const avgCapabilities = stats.total_capabilities / agents.length;
    score += Math.min(avgCapabilities * 4, 20); // Max 20 points for capability coverage
    
    // Priority distribution
    const highPriorityAgents = agents.filter(a => a.priority >= 8).length;
    score += Math.min(highPriorityAgents * 2, 8); // Max 8 points for high-priority agents
    
    return Math.min(score, 100);
  }

  private generateHealthRecommendations(agents: Agent[], stats: DiscoveryStats): string[] {
    const recommendations = [];
    
    if (agents.length < 5) {
      recommendations.push('Consider adding more specialized agents to improve task coverage');
    } else if (agents.length >= 100) {
      recommendations.push('Excellent! You have a comprehensive agent ecosystem with ' + agents.length + ' agents');
    }
    
    if (Object.keys(stats.by_specialization).length < 4) {
      recommendations.push('Add agents with different specializations for better diversity');
    }
    
    const avgCapabilities = stats.total_capabilities / agents.length;
    if (avgCapabilities < 2) {
      recommendations.push('Consider adding more capabilities to existing agents');
    }
    
    const highPriorityAgents = agents.filter(a => a.priority >= 8).length;
    if (highPriorityAgents === 0) {
      recommendations.push('Set higher priorities for your most important agents');
    }
    
    if (recommendations.length === 0) {
      recommendations.push('Your agent ecosystem looks healthy! Consider monitoring usage patterns for optimization opportunities.');
    }
    
    return recommendations;
  }
}

export const agentDiscoveryService = new AgentDiscoveryService();