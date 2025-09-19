/**
 * React Hook for WebSocket connections with auto-recovery
 * Fixes the hard refresh requirement issue
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { getDashboardWebSocket, getAgentsWebSocket, getAssistantWebSocket } from './websocket-manager';
import type WebSocketManager from './websocket-manager';

interface UseWebSocketOptions {
  endpoint: 'dashboard' | 'agents' | 'assistant';
  onMessage?: (data: any) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
  messageTypes?: string[];
  autoConnect?: boolean;
}

interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: any;
  connectionAttempts: number;
}

/**
 * React hook for WebSocket connections
 */
export function useWebSocket(options: UseWebSocketOptions) {
  const {
    endpoint,
    onMessage,
    onConnected,
    onDisconnected,
    messageTypes = [],
    autoConnect = true
  } = options;

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null,
    connectionAttempts: 0
  });

  const wsRef = useRef<WebSocketManager | null>(null);
  const unsubscribersRef = useRef<(() => void)[]>([]);

  // Get the appropriate WebSocket manager
  const getWebSocketManager = useCallback(() => {
    switch (endpoint) {
      case 'dashboard':
        return getDashboardWebSocket();
      case 'agents':
        return getAgentsWebSocket();
      case 'assistant':
        return getAssistantWebSocket();
      default:
        throw new Error(`Unknown endpoint: ${endpoint}`);
    }
  }, [endpoint]);

  // Send a message
  const sendMessage = useCallback((type: string, data?: any) => {
    if (!wsRef.current) {
      console.warn('WebSocket not initialized');
      return;
    }

    wsRef.current.send({
      type,
      data,
      timestamp: new Date().toISOString()
    });
  }, []);

  // Connect to WebSocket
  const connect = useCallback(async () => {
    if (state.isConnecting || state.isConnected) {
      return;
    }

    setState(prev => ({
      ...prev,
      isConnecting: true,
      error: null,
      connectionAttempts: prev.connectionAttempts + 1
    }));

    try {
      const ws = getWebSocketManager();
      wsRef.current = ws;

      // Set up event listeners
      const unsubscribers: (() => void)[] = [];

      // Connection events
      unsubscribers.push(
        ws.on('connected', () => {
          setState(prev => ({
            ...prev,
            isConnected: true,
            isConnecting: false,
            error: null
          }));
          onConnected?.();
        })
      );

      unsubscribers.push(
        ws.on('disconnected', () => {
          setState(prev => ({
            ...prev,
            isConnected: false,
            isConnecting: false
          }));
          onDisconnected?.();
        })
      );

      unsubscribers.push(
        ws.on('error', (error) => {
          setState(prev => ({
            ...prev,
            error: error?.message || 'WebSocket error',
            isConnecting: false
          }));
        })
      );

      // Message listeners
      if (onMessage) {
        unsubscribers.push(
          ws.on('message', (message) => {
            setState(prev => ({ ...prev, lastMessage: message }));
            onMessage(message);
          })
        );
      }

      // Subscribe to specific message types
      messageTypes.forEach(type => {
        unsubscribers.push(
          ws.on(type, (data) => {
            setState(prev => ({ ...prev, lastMessage: { type, data } }));
            onMessage?.({ type, data });
          })
        );
      });

      unsubscribersRef.current = unsubscribers;

      // Actually connect
      await ws.connect();

    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error: error?.message || 'Failed to connect'
      }));
    }
  }, [endpoint, state.isConnecting, state.isConnected, onConnected, onDisconnected, onMessage, messageTypes, getWebSocketManager]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }

    // Clean up listeners
    unsubscribersRef.current.forEach(unsub => unsub());
    unsubscribersRef.current = [];

    setState(prev => ({
      ...prev,
      isConnected: false,
      isConnecting: false
    }));
  }, []);

  // Force reconnect
  const reconnect = useCallback(async () => {
    disconnect();
    await new Promise(resolve => setTimeout(resolve, 100));
    await connect();
  }, [disconnect, connect]);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      if (autoConnect) {
        disconnect();
      }
    };
  }, [autoConnect]); // Only re-run if autoConnect changes

  return {
    ...state,
    sendMessage,
    connect,
    disconnect,
    reconnect
  };
}

/**
 * Hook to check backend health before connecting WebSockets
 */
export function useBackendHealth() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const checkCountRef = useRef(0);

  const checkHealth = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/health/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setIsHealthy(true);
        setError(null);
        return true;
      } else {
        throw new Error(`Health check failed: ${response.status}`);
      }
    } catch (err: any) {
      setError(err.message);
      return false;
    } finally {
      setIsChecking(false);
    }
  }, []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    
    const performHealthCheck = async () => {
      checkCountRef.current++;
      
      const healthy = await checkHealth();
      
      if (healthy) {
        // Backend is ready, stop checking
        if (intervalId) {
          clearInterval(intervalId);
        }
      } else if (checkCountRef.current >= 20) {
        // Stop after 20 attempts (about 10 seconds)
        if (intervalId) {
          clearInterval(intervalId);
        }
        setError('Backend not responding after 20 attempts');
      }
    };

    // Initial check
    performHealthCheck();

    // Set up interval for retries
    if (!isHealthy) {
      intervalId = setInterval(performHealthCheck, 500);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [checkHealth]);

  return {
    isHealthy,
    isChecking,
    error,
    checkHealth
  };
}

/**
 * WebSocket connection status component
 */
export function WebSocketStatus() {
  const dashboardWS = useWebSocket({
    endpoint: 'dashboard',
    autoConnect: true
  });

  const agentsWS = useWebSocket({
    endpoint: 'agents',
    autoConnect: true
  });

  const backendHealth = useBackendHealth();

  const getStatusColor = (isConnected: boolean) => {
    return isConnected ? 'bg-green-500' : 'bg-red-500';
  };

  const getStatusText = (isConnected: boolean, isConnecting: boolean) => {
    if (isConnecting) return 'Connecting...';
    return isConnected ? 'Connected' : 'Disconnected';
  };

  return (
    <div className="fixed bottom-4 right-4 bg-white dark:bg-card shadow-lg rounded-lg p-4 space-y-2">
      <div className="text-sm font-semibold mb-2">Connection Status</div>
      
      {/* Backend Health */}
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${backendHealth.isHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-xs">
          Backend: {backendHealth.isHealthy ? 'Healthy' : backendHealth.error || 'Checking...'}
        </span>
      </div>
      
      {/* Dashboard WebSocket */}
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${getStatusColor(dashboardWS.isConnected)}`} />
        <span className="text-xs">
          Dashboard: {getStatusText(dashboardWS.isConnected, dashboardWS.isConnecting)}
        </span>
      </div>
      
      {/* Agents WebSocket */}
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${getStatusColor(agentsWS.isConnected)}`} />
        <span className="text-xs">
          Agents: {getStatusText(agentsWS.isConnected, agentsWS.isConnecting)}
        </span>
      </div>
      
      {/* Reconnect button */}
      {(!dashboardWS.isConnected || !agentsWS.isConnected) && !dashboardWS.isConnecting && !agentsWS.isConnecting && (
        <button
          onClick={() => {
            dashboardWS.reconnect();
            agentsWS.reconnect();
          }}
          className="mt-2 px-3 py-1 bg-blue-500 text-foreground text-xs rounded hover:bg-blue-600"
        >
          Reconnect All
        </button>
      )}
    </div>
  );
}
