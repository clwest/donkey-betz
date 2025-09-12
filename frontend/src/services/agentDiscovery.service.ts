import { apiClient } from './api.config';

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
   * Discover all available agents from all sources
   */
  async discoverAllAgents(refresh = false) {
    const params = refresh ? '?refresh=true' : '';
    const response = await apiClient.get(`/v1/agents/discover/${params}`);
    return response.data;
  }

  /**
   * Get detailed information about a specific agent
   */
  async getAgentDetails(agentId: string) {
    const response = await apiClient.get(`/v1/agents/${agentId}/details/`);
    return response.data;
  }

  /**
   * Get comprehensive discovery statistics
   */
  async getDiscoveryStats() {
    const response = await apiClient.get('/v1/agents/discovery/stats/');
    return response.data;
  }

  /**
   * Refresh agent discovery cache
   */
  async refreshDiscovery() {
    const response = await apiClient.post('/v1/agents/discovery/refresh/');
    return response.data;
  }

  /**
   * Suggest the best agent for a given task
   */
  async suggestAgentForTask(task: string) {
    const response = await apiClient.post('/v1/agents/suggest/', {
      task
    });
    return response.data;
  }

  /**
   * Search for agents by capability
   */
  async searchAgentsByCapability(capability: string) {
    const response = await apiClient.get(`/v1/agents/search/?capability=${encodeURIComponent(capability)}`);
    return response.data;
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
      agent.capabilities.forEach((cap: Capability) => {
        capabilitiesMap.set(cap.name, cap);
      });
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
      .filter((agent: Agent) => agent.capabilities.length > 3)
      .sort((a, b) => b.capabilities.length - a.capabilities.length);
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
    score += Math.min(agents.length * 10, 40); // Max 40 points for agent count
    
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