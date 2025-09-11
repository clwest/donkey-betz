import { useState, useCallback, useRef, useEffect } from 'react';
import { Logger } from '../../../../utils/logger';

export interface WSProbeResult {
  success: boolean;
  status: 'disconnected' | 'connecting' | 'connected' | 'error';
  message: string;
  timestamp: number;
  responseTime?: number;
  lastPingTime?: number;
}

export interface WSProbeControls {
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
  sendPing: () => void;
  result: WSProbeResult;
}

/**
 * Custom hook for WebSocket probe with ping/pong testing
 * Connects to ${VITE_WS_URL}/ws/assistant/
 */
export function useWSProbe(): WSProbeControls {
  const [result, setResult] = useState<WSProbeResult>({
    success: false,
    status: 'disconnected',
    message: 'Not connected',
    timestamp: Date.now()
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const updateResult = useCallback((update: Partial<WSProbeResult>) => {
    setResult(prev => ({
      ...prev,
      ...update,
      timestamp: Date.now()
    }));
  }, []);

  const connect = useCallback(() => {
    // Clean up any existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const fullUrl = `${wsUrl}/ws/assistant/`;

    Logger.api('WS_PROBE', 'Attempting connection', { url: fullUrl });
    updateResult({
      status: 'connecting',
      message: 'Connecting to WebSocket...',
      success: false
    });

    const startTime = Date.now();

    try {
      const ws = new WebSocket(fullUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        const responseTime = Date.now() - startTime;
        Logger.api('WS_PROBE', 'Connection opened', { responseTime });
        updateResult({
          success: true,
          status: 'connected',
          message: 'WebSocket connected successfully',
          responseTime
        });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          Logger.api('WS_PROBE', 'Message received', { data });

          if (data.type === 'welcome') {
            updateResult({
              success: true,
              status: 'connected',
              message: 'WebSocket connected with welcome message',
            });
          } else if (data.type === 'pong') {
            const pingTime = Date.now() - (data.timestamp || 0);
            Logger.api('WS_PROBE', 'Pong received', { pingTime });
            updateResult({
              success: true,
              status: 'connected',
              message: `Ping successful (${pingTime}ms)`,
              lastPingTime: pingTime
            });
          }
        } catch (error) {
          Logger.warn('WS_PROBE', 'Invalid JSON message', { data: event.data });
        }
      };

      ws.onerror = (error) => {
        const responseTime = Date.now() - startTime;
        Logger.error('WS_PROBE', 'Connection error', { error, responseTime });
        updateResult({
          success: false,
          status: 'error',
          message: 'WebSocket connection error',
          responseTime
        });
      };

      ws.onclose = (event) => {
        const responseTime = Date.now() - startTime;
        Logger.api('WS_PROBE', 'Connection closed', { 
          code: event.code, 
          reason: event.reason, 
          wasClean: event.wasClean,
          responseTime 
        });
        
        updateResult({
          success: false,
          status: 'disconnected',
          message: event.wasClean 
            ? 'WebSocket disconnected' 
            : `WebSocket closed unexpectedly (${event.code})`,
          responseTime
        });

        wsRef.current = null;
      };

    } catch (error: any) {
      const responseTime = Date.now() - startTime;
      Logger.error('WS_PROBE', 'Connection failed', { error: error.message, responseTime });
      updateResult({
        success: false,
        status: 'error',
        message: `Connection failed: ${error.message}`,
        responseTime
      });
    }
  }, [updateResult]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      Logger.api('WS_PROBE', 'Disconnecting WebSocket');
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    updateResult({
      success: false,
      status: 'disconnected',
      message: 'Disconnected manually'
    });
  }, [updateResult]);

  const reconnect = useCallback(() => {
    Logger.api('WS_PROBE', 'Reconnecting WebSocket');
    disconnect();
    
    // Small delay before reconnecting
    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, 1000);
  }, [connect, disconnect]);

  const sendPing = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const pingMessage = {
        type: 'ping',
        timestamp: Date.now()
      };
      
      Logger.api('WS_PROBE', 'Sending ping', { message: pingMessage });
      wsRef.current.send(JSON.stringify(pingMessage));
      
      updateResult({
        status: 'connected',
        message: 'Ping sent, waiting for pong...'
      });

      // Set timeout for ping response
      if (pingTimeoutRef.current) {
        clearTimeout(pingTimeoutRef.current);
      }
      
      pingTimeoutRef.current = setTimeout(() => {
        updateResult({
          success: false,
          status: 'error',
          message: 'Ping timeout - no pong received'
        });
      }, 5000); // 5 second timeout

    } else {
      Logger.warn('WS_PROBE', 'Cannot send ping - WebSocket not connected');
      updateResult({
        success: false,
        status: wsRef.current ? 'connecting' : 'disconnected',
        message: 'Cannot send ping - WebSocket not connected'
      });
    }
  }, [updateResult]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingTimeoutRef.current) {
        clearTimeout(pingTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    connect,
    disconnect,
    reconnect,
    sendPing,
    result
  };
}