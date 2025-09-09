/**
 * React Native hooks for DBAO (Donkey Betz Agent Orchestra)
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import { 
  DBAOService, 
  Agent, 
  AgentInstance, 
  AgentSuggestion, 
  BettingOpportunity,
  AgentExecutionRequest,
  BettingAnalysisRequest
} from '../services/dbao.service';
import { DBAO_CONFIG, getWebSocketUrl, AgentType } from '../config/dbao.config';

// WebSocket Manager for React Native
class DBAOWebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = DBAO_CONFIG.WS_MAX_RECONNECT_ATTEMPTS;
  private reconnectDelay = DBAO_CONFIG.WS_RECONNECT_DELAY;
  private callbacks: Map<string, Function[]> = new Map();
  private connectionState: 'idle' | 'connecting' | 'open' | 'closed' = 'idle';
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageQueue: any[] = [];

  constructor(private token: string) {}

  async connect(endpoint: 'agents' | 'dashboard' = 'agents'): Promise<void> {
    if (this.connectionState === 'connecting' || this.connectionState === 'open') {
      return;
    }

    this.connectionState = 'connecting';

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${getWebSocketUrl(endpoint)}?token=${this.token}`;
        console.log('[DBAO WS] Connecting to:', wsUrl);
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('[DBAO WS] Connected successfully');
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
                data = { type: 'text', message: event.data };
              }
            } else {
              data = event.data;
            }
            
            this.handleMessage(data);
          } catch (error) {
            console.error('[DBAO WS] Message parsing error:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('[DBAO WS] Connection closed:', event.code, event.reason);
          this.connectionState = 'closed';
          this.stopHeartbeat();
          
          // Only reconnect for unexpected closures
          if (event.code !== 1000) {
            this.attemptReconnect(endpoint);
          }
        };

        this.ws.onerror = (error) => {
          console.error('[DBAO WS] Connection error:', error);
          this.connectionState = 'closed';
          reject(error);
        };

      } catch (error) {
        this.connectionState = 'closed';
        reject(error);
      }
    });
  }

  private handleMessage(data: any) {
    const { type } = data;
    const callbacks = this.callbacks.get(type) || [];
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('[DBAO WS] Callback error:', error);
      }
    });
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.connectionState === 'open') {
        this.send({ type: 'ping' });
      }
    }, DBAO_CONFIG.WS_HEARTBEAT_INTERVAL);
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  private attemptReconnect(endpoint: 'agents' | 'dashboard') {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[DBAO WS] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 15000);

    console.log(`[DBAO WS] Reconnecting in ${delay}ms (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect(endpoint).catch(console.error);
    }, delay);
  }

  send(message: any) {
    if (this.connectionState === 'open' && this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('[DBAO WS] Send error:', error);
        this.messageQueue.push(message);
      }
    } else {
      this.messageQueue.push(message);
      if (this.messageQueue.length > 100) {
        this.messageQueue.shift();
      }
    }
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

  subscribeToInstance(instanceId: string) {
    this.send({
      type: 'subscribe_instance',
      instance_id: instanceId
    });
  }

  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }
    this.connectionState = 'closed';
    this.callbacks.clear();
    this.messageQueue.length = 0;
    this.reconnectAttempts = 0;
  }

  isConnected(): boolean {
    return this.connectionState === 'open' && this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState() {
    return this.connectionState;
  }
}

// Singleton WebSocket manager
let wsManager: DBAOWebSocketManager | null = null;

const getWebSocketManager = async (): Promise<DBAOWebSocketManager> => {
  if (!wsManager) {
    const token = await AsyncStorage.getItem('authToken') || DBAO_CONFIG.DEFAULT_AUTH_TOKEN;
    wsManager = new DBAOWebSocketManager(token);
  }
  return wsManager;
};

// Agents Hook
export const useAgents = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await DBAOService.getAgents();
      setAgents(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch agents');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return { agents, loading, error, refetch: fetchAgents };
};

// Agent Execution Hook
export const useAgentExecution = () => {
  const [executing, setExecuting] = useState(false);
  const [instances, setInstances] = useState<AgentInstance[]>([]);
  const [error, setError] = useState<string | null>(null);

  const executeAgent = useCallback(async (request: AgentExecutionRequest): Promise<AgentInstance | null> => {
    setExecuting(true);
    setError(null);
    try {
      const instance = await DBAOService.executeAgent(request);
      if (instance) {
        setInstances(prev => [instance, ...prev]);
        
        // Subscribe to instance updates if WebSocket is available
        const ws = await getWebSocketManager();
        if (ws.isConnected()) {
          ws.subscribeToInstance(instance.id);
        }
      }
      return instance;
    } catch (err: any) {
      setError(err.message || 'Failed to execute agent');
      Alert.alert('Execution Error', err.message || 'Failed to execute agent');
      return null;
    } finally {
      setExecuting(false);
    }
  }, []);

  const suggestAgents = useCallback(async (taskDescription: string): Promise<AgentSuggestion[]> => {
    try {
      return await DBAOService.suggestAgents(taskDescription);
    } catch (err: any) {
      console.warn('[DBAO] Failed to get suggestions:', err);
      return [];
    }
  }, []);

  const fetchInstances = useCallback(async () => {
    try {
      const data = await DBAOService.getInstances();
      setInstances(data);
    } catch (err: any) {
      console.error('[DBAO] Failed to fetch instances:', err);
    }
  }, []);

  useEffect(() => {
    fetchInstances();
  }, [fetchInstances]);

  return {
    executing,
    instances,
    error,
    executeAgent,
    suggestAgents,
    refetchInstances: fetchInstances
  };
};

// WebSocket Hook
export const useWebSocket = () => {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const wsRef = useRef<DBAOWebSocketManager | null>(null);

  const connect = useCallback(async (endpoint: 'agents' | 'dashboard' = 'agents') => {
    if (connecting || connected) return;
    
    setConnecting(true);
    try {
      const ws = await getWebSocketManager();
      wsRef.current = ws;
      await ws.connect(endpoint);
      setConnected(true);
    } catch (error) {
      console.error('[DBAO] WebSocket connection failed:', error);
      Alert.alert('Connection Error', 'Failed to connect to real-time updates');
    } finally {
      setConnecting(false);
    }
  }, [connecting, connected]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }
    setConnected(false);
    setConnecting(false);
  }, []);

  const subscribe = useCallback((eventType: string, callback: Function) => {
    if (wsRef.current) {
      wsRef.current.subscribe(eventType, callback);
      return () => wsRef.current?.unsubscribe(eventType, callback);
    }
    return () => {};
  }, []);

  const send = useCallback((message: any) => {
    if (wsRef.current) {
      wsRef.current.send(message);
    }
  }, []);

  useEffect(() => {
    if (DBAO_CONFIG.AUTO_CONNECT_WEBSOCKET) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, []);

  return {
    connected,
    connecting,
    connect,
    disconnect,
    subscribe,
    send,
    isConnected: () => wsRef.current?.isConnected() || false
  };
};

// Sports Betting Hook
export const useBetting = () => {
  const [opportunities, setOpportunities] = useState<BettingOpportunity[]>([]);
  const [liveOpportunities, setLiveOpportunities] = useState<BettingOpportunity[]>([]);
  const [arbitrageOpportunities, setArbitrageOpportunities] = useState<BettingOpportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeBetting = useCallback(async (request: BettingAnalysisRequest) => {
    setLoading(true);
    setError(null);
    try {
      const data = await DBAOService.analyzeBettingOpportunity(request);
      setOpportunities(data);
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to analyze betting opportunities');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLiveOpportunities = useCallback(async (sport?: string) => {
    try {
      const data = await DBAOService.getLiveOpportunities(sport);
      setLiveOpportunities(data);
      return data;
    } catch (err: any) {
      console.warn('[DBAO] Failed to fetch live opportunities:', err);
      return [];
    }
  }, []);

  const fetchArbitrageOpportunities = useCallback(async () => {
    try {
      const data = await DBAOService.getArbitrageOpportunities();
      setArbitrageOpportunities(data);
      return data;
    } catch (err: any) {
      console.warn('[DBAO] Failed to fetch arbitrage opportunities:', err);
      return [];
    }
  }, []);

  return {
    opportunities,
    liveOpportunities,
    arbitrageOpportunities,
    loading,
    error,
    analyzeBetting,
    fetchLiveOpportunities,
    fetchArbitrageOpportunities
  };
};

// Combined DBAO Hook
export const useDBAAO = () => {
  const agents = useAgents();
  const execution = useAgentExecution();
  const websocket = useWebSocket();
  const betting = useBetting();

  const [healthStatus, setHealthStatus] = useState<{ status: string; version: string } | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const status = await DBAOService.healthCheck();
      setHealthStatus(status);
      return status;
    } catch (error) {
      console.warn('[DBAO] Health check failed:', error);
      return null;
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return {
    ...agents,
    ...execution,
    ...websocket,
    ...betting,
    healthStatus,
    checkHealth
  };
};