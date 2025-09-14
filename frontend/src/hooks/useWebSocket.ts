import { useEffect, useRef, useState, useCallback } from 'react';

export interface WebSocketConfig {
  url: string;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(config: WebSocketConfig) {
  const {
    url,
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
  } = config;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isUnmountingRef = useRef(false);
  
  // Store callbacks in refs to avoid recreating the connection
  const configRef = useRef(config);
  configRef.current = config;

  const disconnect = useCallback(() => {
    isUnmountingRef.current = true;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      wsRef.current.close(1000, 'Disconnect requested');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  const connect = useCallback(() => {
    try {
      // Don't connect if we're unmounting or already connected
      if (isUnmountingRef.current) {
        return;
      }

      // Clean up existing connection
      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN || 
            wsRef.current.readyState === WebSocket.CONNECTING) {
          console.log('[WebSocket] Already connected or connecting, skipping...');
          return;
        }
        wsRef.current = null;
      }

      // Create WebSocket URL using API config
      let wsUrl: string;
      if (url.startsWith('ws://') || url.startsWith('wss://')) {
        // Already a full WebSocket URL
        wsUrl = url;
      } else {
        // Build URL using API config for proper backend connection
        const isDev = import.meta.env.MODE !== 'production';
        const wsBase = isDev ? 'ws://localhost:8000' : 
          (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host;
        wsUrl = `${wsBase}${url}`;
      }
      
      console.log('[WebSocket] Connecting to:', wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        configRef.current.onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WebSocket] Message received:', data);
          setLastMessage(data);
          configRef.current.onMessage?.(data);
        } catch (error) {
          console.error('[WebSocket] Error parsing message:', error);
          // If parsing fails, still set the raw message
          setLastMessage(event.data);
        }
      };

      ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected with code:', event.code, 'reason:', event.reason);
        setIsConnected(false);
        configRef.current.onClose?.();

        // Only reconnect if not unmounting and reconnect is enabled
        if (!isUnmountingRef.current && configRef.current.reconnect && event.code !== 1000) {
          reconnectAttemptsRef.current += 1;
          
          if (reconnectAttemptsRef.current <= maxReconnectAttempts) {
            console.log(`[WebSocket] Reconnecting... (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              if (!isUnmountingRef.current) {
                connect();
              }
            }, reconnectInterval);
          } else {
            console.log('[WebSocket] Max reconnection attempts reached');
          }
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        configRef.current.onError?.(error);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
    }
  }, [url, reconnectInterval, maxReconnectAttempts]);

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      wsRef.current.send(message);
      console.log('[WebSocket] Message sent:', data);
    } else {
      console.warn('[WebSocket] Cannot send message - not connected');
    }
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    isUnmountingRef.current = false;
    
    // Small delay to ensure component is mounted
    const connectTimeout = setTimeout(() => {
      if (!isUnmountingRef.current) {
        connect();
      }
    }, 100);
    
    return () => {
      clearTimeout(connectTimeout);
      disconnect();
    };
  }, [url]); // Only reconnect if URL changes

  return {
    isConnected,
    sendMessage,
    disconnect,
    reconnect: connect,
    lastMessage,
  };
}