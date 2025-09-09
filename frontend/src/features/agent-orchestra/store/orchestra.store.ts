/**
 * Agent Orchestra Store
 * 
 * Centralized state management for Agent Orchestra feature using:
 * - Zustand for state management
 * - Shared WebSocket client for real-time updates
 * - Type-safe interfaces and error handling
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { connectWS, type WSClient } from '../../../lib/ws/client';
import { 
  orchHealth, 
  getAgents, 
  getInstances, 
  executeAgent,
  getWebSocketBase,
  type OrchestraHealth,
  type Agent,
  type AgentInstance
} from '../api/orchestra';
import { toast } from 'sonner';

export interface OrchestraState {
  // Health status
  health: OrchestraHealth | null;
  healthLoading: boolean;

  // Agents
  agents: Agent[];
  agentsLoading: boolean;
  agentsError: string | null;

  // Instances
  instances: AgentInstance[];
  instancesLoading: boolean;
  instancesError: string | null;

  // WebSocket
  wsClient: WSClient | null;
  wsState: 'idle' | 'connecting' | 'open' | 'closed' | 'error';
  lastPing: Date | null;
  lastPong: Date | null;

  // Actions
  checkHealth: () => Promise<void>;
  fetchAgents: () => Promise<void>;
  fetchInstances: () => Promise<void>;
  executeAgentTask: (agentType: string, taskDescription: string, parameters?: Record<string, any>) => Promise<AgentInstance>;
  
  // WebSocket actions
  connectWS: () => Promise<void>;
  disconnectWS: () => void;
  sendPing: () => void;
  
  // Utility
  reset: () => void;
}

const initialState = {
  health: null,
  healthLoading: false,
  
  agents: [],
  agentsLoading: false,
  agentsError: null,
  
  instances: [],
  instancesLoading: false,
  instancesError: null,
  
  wsClient: null,
  wsState: 'idle' as const,
  lastPing: null,
  lastPong: null
};

export const useOrchestraStore = create<OrchestraState>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,

    checkHealth: async () => {
      set({ healthLoading: true });
      try {
        const health = await orchHealth();
        set({ health, healthLoading: false });
      } catch (error) {
        console.error('[Orchestra Store] Health check failed:', error);
        set({ 
          health: { 
            status: 'unhealthy', 
            details: { error: error instanceof Error ? error.message : 'Unknown error' } 
          }, 
          healthLoading: false 
        });
      }
    },

    fetchAgents: async () => {
      set({ agentsLoading: true, agentsError: null });
      try {
        const agents = await getAgents();
        set({ agents, agentsLoading: false });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch agents';
        set({ 
          agentsError: errorMessage, 
          agentsLoading: false,
          agents: []
        });
      }
    },

    fetchInstances: async () => {
      set({ instancesLoading: true, instancesError: null });
      try {
        const instances = await getInstances();
        set({ instances, instancesLoading: false });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch instances';
        set({ 
          instancesError: errorMessage, 
          instancesLoading: false,
          instances: []
        });
      }
    },

    executeAgentTask: async (agentType: string, taskDescription: string, parameters?: Record<string, any>) => {
      try {
        const instance = await executeAgent(agentType, taskDescription, parameters);
        
        // Add to instances list
        const { instances } = get();
        set({ instances: [instance, ...instances] });
        
        toast.success('Agent execution started');
        return instance;
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Failed to execute agent';
        toast.error(message);
        throw error;
      }
    },

    connectWS: async () => {
      const { wsClient } = get();
      
      // Don't reconnect if already connected
      if (wsClient && wsClient.isOpen()) {
        return;
      }

      // Clean up existing connection
      if (wsClient) {
        wsClient.close();
      }

      set({ wsState: 'connecting' });

      try {
        // Get auth token from localStorage
        const token = localStorage.getItem('authToken');
        
        // Orchestra connects to the unified backend WebSocket
        const wsBase = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
        const client = connectWS({
          base: wsBase,
          path: '/ws/agents/', // Unified WebSocket endpoint for agents
          token, // Add authentication token if available
          maxAttempts: 5,
          
          onOpen: () => {
            console.info('[Orchestra] WebSocket connected');
            set({ wsState: 'open' });
            toast.success('Real-time updates connected');
            
            // Send initial ping
            get().sendPing();
          },
          
          onMessage: (data) => {
            console.debug('[Orchestra] WebSocket message:', data);
            
            // Handle pong responses
            if (data.type === 'pong') {
              set({ lastPong: new Date() });
              return;
            }
            
            // Handle instance updates
            if (data.type === 'instance_update') {
              const { instances } = get();
              const updatedInstances = instances.map(instance => 
                instance.id === data.instance_id 
                  ? { ...instance, status: data.status, result: data.result, error_message: data.error }
                  : instance
              );
              set({ instances: updatedInstances });
              
              // Show notification
              if (data.status === 'completed') {
                toast.success(`Agent task completed: ${data.instance_id.slice(0, 8)}...`);
              } else if (data.status === 'failed') {
                toast.error(`Agent task failed: ${data.instance_id.slice(0, 8)}...`);
              }
            }
          },
          
          onClose: (event) => {
            console.warn('[Orchestra] WebSocket closed:', event.code, event.reason);
            set({ wsState: 'closed' });
            
            if (event.code !== 1000) {
              toast.warning('Real-time updates disconnected');
            }
          },
          
          onError: (error) => {
            // Only log errors in debug mode to reduce console spam
            if (import.meta.env.VITE_DEBUG_MODE === 'true') {
              console.debug('[Orchestra] WebSocket error detected');
            }
            set({ wsState: 'error' });
            // Don't show toast for every error to avoid spam
          }
        });

        set({ wsClient: client });
      } catch (error) {
        console.error('[Orchestra] Failed to connect WebSocket:', error);
        set({ wsState: 'error' });
        toast.error('Failed to connect real-time updates');
      }
    },

    disconnectWS: () => {
      const { wsClient } = get();
      if (wsClient) {
        wsClient.close();
        set({ wsClient: null, wsState: 'closed' });
      }
    },

    sendPing: () => {
      const { wsClient } = get();
      if (wsClient && wsClient.isOpen()) {
        wsClient.send({ type: 'ping' });
        set({ lastPing: new Date() });
      }
    },

    reset: () => {
      const { wsClient } = get();
      if (wsClient) {
        wsClient.close();
      }
      set(initialState);
    }
  }))
);

/**
 * Custom hook for Orchestra WebSocket functionality
 */
export function useOrchestraWS() {
  const { 
    wsState, 
    lastPing, 
    lastPong, 
    connectWS, 
    disconnectWS, 
    sendPing 
  } = useOrchestraStore();

  return {
    state: wsState,
    lastPing,
    lastPong,
    connect: connectWS,
    disconnect: disconnectWS,
    ping: sendPing,
    isConnected: wsState === 'open',
    isConnecting: wsState === 'connecting'
  };
}