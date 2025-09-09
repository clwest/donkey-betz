import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type { 
  Agent, 
  AgentInstance, 
  AgentOrchestration,
  BettingOpportunity,
  OddsCalculationRequest,
  OddsCalculationResponse
} from '../services/agent-orchestra.service';
import {
  AgentOrchestraService,
  getWebSocketManager 
} from '../services/agent-orchestra.service';
import { toast } from 'sonner';

interface AgentOrchestraState {
  // Agents
  agents: Agent[];
  selectedAgent: Agent | null;
  agentsLoading: boolean;
  agentsError: string | null;

  // Instances
  instances: AgentInstance[];
  selectedInstance: AgentInstance | null;
  instancesLoading: boolean;
  instancesError: string | null;

  // Orchestrations
  orchestrations: AgentOrchestration[];
  selectedOrchestration: AgentOrchestration | null;
  orchestrationsLoading: boolean;
  orchestrationsError: string | null;

  // Agent Orchestra Tools
  oddsCalculations: Record<string, OddsCalculationResponse>;
  bettingOpportunities: BettingOpportunity[];
  toolsLoading: boolean;
  toolsError: string | null;

  // WebSocket
  wsConnected: boolean;
  wsConnecting: boolean;

  // Actions
  fetchAgents: () => Promise<void>;
  selectAgent: (agent: Agent | null) => void;
  executeAgent: (agentType: string, taskDescription: string, parameters?: Record<string, any>) => Promise<AgentInstance>;
  suggestAgents: (taskDescription: string) => Promise<Agent[]>;

  fetchInstances: () => Promise<void>;
  selectInstance: (instance: AgentInstance | null) => void;
  updateInstanceStatus: (instanceId: string) => Promise<void>;

  fetchOrchestrations: () => Promise<void>;
  selectOrchestration: (orchestration: AgentOrchestration | null) => void;
  orchestrateTask: (taskDescription: string, agents?: string[], autoRoute?: boolean) => Promise<AgentOrchestration>;

  // Agent Orchestra Tools
  calculateOdds: (request: OddsCalculationRequest, calculationId?: string) => Promise<OddsCalculationResponse>;
  analyzeBetting: (sport: string, context?: string) => Promise<BettingOpportunity[]>;

  connectWebSocket: () => Promise<void>;
  disconnectWebSocket: () => void;
  setupWebSocketListeners: () => void;

  // Utility actions
  clearErrors: () => void;
  reset: () => void;
}

const initialState = {
  agents: [],
  selectedAgent: null,
  agentsLoading: false,
  agentsError: null,

  instances: [],
  selectedInstance: null,
  instancesLoading: false,
  instancesError: null,

  orchestrations: [],
  selectedOrchestration: null,
  orchestrationsLoading: false,
  orchestrationsError: null,

  // Agent Orchestra Tools
  oddsCalculations: {},
  bettingOpportunities: [],
  toolsLoading: false,
  toolsError: null,

  wsConnected: false,
  wsConnecting: false,
};

export const useAgentOrchestraStore = create<AgentOrchestraState>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,

    // Agent Actions
    fetchAgents: async () => {
      set({ agentsLoading: true, agentsError: null });
      try {
        const agents = await AgentOrchestraService.getAgents();
        // Ensure agents is always an array
        const agentsArray = Array.isArray(agents) ? agents : [];
        set({ agents: agentsArray, agentsLoading: false });
      } catch (error: any) {
        set({ 
          agentsError: error.userMessage || 'Failed to fetch agents', 
          agentsLoading: false 
        });
        toast.error('Failed to load agents');
      }
    },

    selectAgent: (agent: Agent | null) => {
      set({ selectedAgent: agent });
    },

    executeAgent: async (agentType: string, taskDescription: string, parameters?: Record<string, any>) => {
      try {
        const instance = await AgentOrchestraService.executeAgent({
          agent_type: agentType,
          task_description: taskDescription,
          parameters
        });
        
        // Add to instances list
        const { instances } = get();
        set({ instances: [instance, ...instances] });
        
        // Subscribe to updates if WebSocket is connected
        const wsManager = getWebSocketManager();
        if (wsManager.isConnected()) {
          wsManager.subscribeToInstance(instance.id);
        }
        
        toast.success('Agent execution started');
        return instance;
      } catch (error: any) {
        toast.error(error.userMessage || 'Failed to execute agent');
        throw error;
      }
    },

    suggestAgents: async (taskDescription: string) => {
      try {
        const suggestions = await AgentOrchestraService.suggestAgent(taskDescription);
        return suggestions.map(s => s.agent);
      } catch (error: any) {
        toast.error('Failed to get agent suggestions');
        return [];
      }
    },

    // Instance Actions
    fetchInstances: async () => {
      set({ instancesLoading: true, instancesError: null });
      try {
        const instances = await AgentOrchestraService.getInstances();
        // Ensure instances is always an array
        const instancesArray = Array.isArray(instances) ? instances : [];
        set({ instances: instancesArray, instancesLoading: false });
      } catch (error: any) {
        set({ 
          instancesError: error.userMessage || 'Failed to fetch instances', 
          instancesLoading: false 
        });
        toast.error('Failed to load agent instances');
      }
    },

    selectInstance: (instance: AgentInstance | null) => {
      set({ selectedInstance: instance });
    },

    updateInstanceStatus: async (instanceId: string) => {
      try {
        const updatedInstance = await AgentOrchestraService.getInstanceStatus(instanceId);
        const { instances } = get();
        const updatedInstances = instances.map(instance => 
          instance.id === instanceId ? updatedInstance : instance
        );
        set({ instances: updatedInstances });
        
        // Update selected instance if it's the one being updated
        const { selectedInstance } = get();
        if (selectedInstance?.id === instanceId) {
          set({ selectedInstance: updatedInstance });
        }
      } catch (error: any) {
        console.error('Failed to update instance status:', error);
      }
    },

    // Orchestration Actions
    fetchOrchestrations: async () => {
      set({ orchestrationsLoading: true, orchestrationsError: null });
      try {
        const orchestrations = await AgentOrchestraService.getOrchestrations();
        // Ensure orchestrations is always an array
        const orchestrationsArray = Array.isArray(orchestrations) ? orchestrations : [];
        set({ orchestrations: orchestrationsArray, orchestrationsLoading: false });
      } catch (error: any) {
        set({ 
          orchestrationsError: error.userMessage || 'Failed to fetch orchestrations', 
          orchestrationsLoading: false 
        });
        toast.error('Failed to load orchestrations');
      }
    },

    selectOrchestration: (orchestration: AgentOrchestration | null) => {
      set({ selectedOrchestration: orchestration });
    },

    orchestrateTask: async (taskDescription: string, agents?: string[], autoRoute = true) => {
      try {
        const orchestration = await AgentOrchestraService.orchestrateTask({
          task_description: taskDescription,
          agents,
          auto_route: autoRoute
        });
        
        // Add to orchestrations list
        const { orchestrations } = get();
        set({ orchestrations: [orchestration, ...orchestrations] });
        
        // Subscribe to updates if WebSocket is connected
        const wsManager = getWebSocketManager();
        if (wsManager.isConnected()) {
          wsManager.subscribeToOrchestration(orchestration.id);
        }
        
        toast.success('Multi-agent orchestration started');
        return orchestration;
      } catch (error: any) {
        toast.error(error.userMessage || 'Failed to start orchestration');
        throw error;
      }
    },

    // Agent Orchestra Tools
    calculateOdds: async (request: OddsCalculationRequest, calculationId?: string) => {
      set({ toolsLoading: true, toolsError: null });
      try {
        const result = await AgentOrchestraService.calculateOdds(request);
        const { oddsCalculations } = get();
        const id = calculationId || `calc-${Date.now()}`;
        
        set({ 
          oddsCalculations: { ...oddsCalculations, [id]: result },
          toolsLoading: false 
        });
        
        return result;
      } catch (error: any) {
        const errorMessage = error instanceof Error ? error.message : 'Odds calculation failed';
        set({ toolsError: errorMessage, toolsLoading: false });
        throw error;
      }
    },

    analyzeBetting: async (sport: string, context?: string) => {
      console.log('[AgentOrchestraStore] analyzeBetting called with:', { sport, context });
      set({ toolsLoading: true, toolsError: null });
      try {
        console.log('[AgentOrchestraStore] Calling AgentOrchestraService.analyzeBettingOpportunity...');
        const opportunities = await AgentOrchestraService.analyzeBettingOpportunity({
          sport,
          context,
          odds: [{ home: 150, away: -200 }] // Sample for development
        });
        
        console.log('[AgentOrchestraStore] Received opportunities:', opportunities);
        set({ bettingOpportunities: opportunities, toolsLoading: false });
        return opportunities;
      } catch (error: any) {
        const errorMessage = error instanceof Error ? error.message : 'Betting analysis failed';
        console.error('[AgentOrchestraStore] analyzeBetting error:', error);
        set({ toolsError: errorMessage, toolsLoading: false });
        return [];
      }
    },

    // WebSocket Actions
    connectWebSocket: async () => {
      set({ wsConnecting: true });
      try {
        const wsManager = getWebSocketManager();
        await wsManager.connect('agents');
        set({ wsConnected: true, wsConnecting: false });
        get().setupWebSocketListeners();
        toast.success('Connected to real-time updates');
      } catch (error: any) {
        set({ wsConnected: false, wsConnecting: false });
        console.error('WebSocket connection failed:', error);
      }
    },

    disconnectWebSocket: () => {
      const wsManager = getWebSocketManager();
      wsManager.disconnect();
      set({ wsConnected: false, wsConnecting: false });
    },

    setupWebSocketListeners: () => {
      const wsManager = getWebSocketManager();
      
      // Instance updates
      wsManager.subscribe('instance_update', (data: any) => {
        const { instances } = get();
        const updatedInstances = instances.map(instance => 
          instance.id === data.instance_id 
            ? { ...instance, status: data.status, result: data.result }
            : instance
        );
        set({ instances: updatedInstances });
        
        // Update selected instance
        const { selectedInstance } = get();
        if (selectedInstance?.id === data.instance_id) {
          set({ 
            selectedInstance: { 
              ...selectedInstance, 
              status: data.status, 
              result: data.result 
            }
          });
        }
        
        // Show toast notification
        if (data.status === 'completed') {
          toast.success(`Agent task completed: ${data.instance_id}`);
        } else if (data.status === 'failed') {
          toast.error(`Agent task failed: ${data.instance_id}`);
        }
      });

      // Orchestration updates
      wsManager.subscribe('orchestration_update', (data: any) => {
        const { orchestrations } = get();
        const updatedOrchestrations = orchestrations.map(orch => 
          orch.id === data.orchestration_id 
            ? { ...orch, status: data.status, current_step: data.progress }
            : orch
        );
        set({ orchestrations: updatedOrchestrations });
        
        // Update selected orchestration
        const { selectedOrchestration } = get();
        if (selectedOrchestration?.id === data.orchestration_id) {
          set({ 
            selectedOrchestration: { 
              ...selectedOrchestration, 
              status: data.status, 
              current_step: data.progress 
            }
          });
        }
        
        // Show toast notification
        if (data.status === 'completed') {
          toast.success(`Multi-agent orchestration completed`);
        } else if (data.status === 'failed') {
          toast.error(`Multi-agent orchestration failed`);
        }
      });

      // Sports betting updates
      wsManager.subscribe('betting_update', (data: any) => {
        if (data.opportunities?.length > 0) {
          set({ 
            bettingOpportunities: data.opportunities 
          });
          toast.success(`New betting opportunities found!`);
        }
      });

      // Content generation updates (for compatibility)
      wsManager.subscribe('content_update', (data: any) => {
        if (data.status === 'completed') {
          toast.success('Content generation completed');
        } else if (data.status === 'failed') {
          toast.error('Content generation failed');
        }
      });
    },

    // Utility Actions
    clearErrors: () => {
      set({
        agentsError: null,
        instancesError: null,
        orchestrationsError: null,
        toolsError: null
      });
    },

    reset: () => {
      set(initialState);
    }
  }))
);

// Selectors
export const useAgentOrchestraSelectors = () => {
  const store = useAgentOrchestraStore();
  
  return {
    // Agent selectors
    availableAgents: store.agents,
    selectedAgent: store.selectedAgent,
    agentsLoading: store.agentsLoading,
    
    // Instance selectors
    runningInstances: store.instances.filter(i => i.status === 'processing'),
    completedInstances: store.instances.filter(i => i.status === 'completed'),
    failedInstances: store.instances.filter(i => i.status === 'failed'),
    recentInstances: store.instances.slice(0, 10),
    
    // Orchestration selectors
    activeOrchestrations: store.orchestrations.filter(o => o.status === 'processing'),
    completedOrchestrations: store.orchestrations.filter(o => o.status === 'completed'),
    
    // Agent Orchestra Tools
    oddsCalculations: store.oddsCalculations,
    bettingOpportunities: store.bettingOpportunities,
    toolsLoading: store.toolsLoading,
    toolsError: store.toolsError,
    hasOddsTools: Object.keys(store.oddsCalculations).length > 0,
    hasBettingOpportunities: store.bettingOpportunities.length > 0,
    
    // WebSocket status
    isConnected: store.wsConnected,
    isConnecting: store.wsConnecting
  };
};