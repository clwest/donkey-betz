import Constants from 'expo-constants';
import { Platform } from 'react-native';

export interface WebSocketMessage {
  type: string;
  message?: string;
  data?: any;
  timestamp?: string;
  session_id?: string;
  is_typing?: boolean;
  user?: string;
  context?: any;
}

export type WebSocketState = 'idle' | 'connecting' | 'open' | 'pong' | 'closed' | 'error';

export interface WebSocketClientOptions {
  url: string;
  authToken?: string;
  maxReconnectAttempts?: number;
  onStateChange?: (state: WebSocketState) => void;
  onMessage?: (message: WebSocketMessage | string) => void;
  onError?: (error: string) => void;
}

export interface ConnectionStatus {
  state: WebSocketState;
  isConnected: boolean;
  lastMessage: string;
  lastError: string;
  reconnectAttempts: number;
  url: string;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private state: WebSocketState = 'idle';
  private reconnectAttempts = 0;
  private reconnectTimeoutId: NodeJS.Timeout | null = null;
  private pingTimeoutId: NodeJS.Timeout | null = null;
  
  private readonly url: string;
  private readonly authToken?: string;
  private readonly maxReconnectAttempts: number;
  private readonly onStateChange?: (state: WebSocketState) => void;
  private readonly onMessage?: (message: WebSocketMessage | string) => void;
  private readonly onError?: (error: string) => void;

  constructor(options: WebSocketClientOptions) {
    this.url = options.url;
    this.authToken = options.authToken;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.onStateChange = options.onStateChange;
    this.onMessage = options.onMessage;
    this.onError = options.onError;
  }

  public get currentState(): WebSocketState {
    return this.state;
  }

  public get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public getStatus(): ConnectionStatus {
    return {
      state: this.state,
      isConnected: this.isConnected,
      lastMessage: '',
      lastError: '',
      reconnectAttempts: this.reconnectAttempts,
      url: this.url,
    };
  }

  private setState(newState: WebSocketState) {
    if (this.state !== newState) {
      this.state = newState;
      this.onStateChange?.(newState);
    }
  }

  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    this.cleanup();
    this.setState('connecting');

    try {
      const fullUrl = this.authToken 
        ? `${this.url}?token=${this.authToken}`
        : this.url;

      console.log(`[WebSocket] Connecting to: ${fullUrl}`);
      this.ws = new WebSocket(fullUrl);

      this.ws.onopen = () => {
        console.log('[WebSocket] Connected');
        this.setState('open');
        this.reconnectAttempts = 0;
        this.scheduleHeartbeat();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
        
        // Clear ping timeout on any message
        if (this.pingTimeoutId) {
          clearTimeout(this.pingTimeoutId);
          this.pingTimeoutId = null;
        }
      };

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        this.setState('error');
        this.onError?.('WebSocket connection error');
      };

      this.ws.onclose = (event) => {
        console.log(`[WebSocket] Closed: ${event.code} ${event.reason}`);
        this.setState('closed');
        this.ws = null;
        
        // Auto-reconnect unless manual close or max attempts reached
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        } else if (event.code === 4003) {
          this.onError?.('Authentication failed: Invalid or missing token');
        }
      };

      // Connection timeout
      setTimeout(() => {
        if (this.ws?.readyState === WebSocket.CONNECTING) {
          this.ws.close();
          this.setState('error');
          this.onError?.('Connection timeout');
        }
      }, 10000);

    } catch (error) {
      console.error('[WebSocket] Failed to create connection:', error);
      this.setState('error');
      this.onError?.(`Connection failed: ${error}`);
    }
  }

  private handleMessage(data: string) {
    try {
      const parsed = JSON.parse(data) as WebSocketMessage;
      
      if (parsed.type === 'pong' || parsed.type === 'context') {
        this.setState('pong');
        // Return to open state after showing pong
        setTimeout(() => this.setState('open'), 1000);
      }
      
      this.onMessage?.(parsed);
    } catch {
      // Handle non-JSON messages
      this.onMessage?.(data);
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    
    // Capped exponential backoff: delay = min(15000, 1000 * 2^attempts)
    const delay = Math.min(15000, 1000 * Math.pow(2, this.reconnectAttempts));
    
    console.log(`[WebSocket] Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    this.reconnectTimeoutId = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private scheduleHeartbeat(): void {
    // Send ping every 30 seconds to keep connection alive
    setTimeout(() => {
      if (this.isConnected) {
        this.sendPing();
        this.scheduleHeartbeat();
      }
    }, 30000);
  }

  public sendPing(): void {
    if (this.isConnected) {
      const pingMessage = {
        type: 'ping',
        timestamp: new Date().toISOString()
      };
      
      this.send(pingMessage);
      this.setState('pong');
      
      // Set ping timeout
      this.pingTimeoutId = setTimeout(() => {
        this.setState('error');
        this.onError?.('Ping timeout - no response received');
      }, 10000);
    } else {
      this.onError?.('Cannot send ping - not connected');
    }
  }

  public send(data: object | string): void {
    if (!this.isConnected) {
      this.onError?.('Cannot send message - not connected');
      return;
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.ws!.send(message);
    } catch (error) {
      console.error('[WebSocket] Send error:', error);
      this.onError?.(`Failed to send message: ${error}`);
    }
  }

  public close(): void {
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
    this.cleanup();
    
    if (this.ws) {
      this.ws.close(1000, 'Manual close');
    }
    
    this.setState('closed');
  }

  private cleanup(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
    
    if (this.pingTimeoutId) {
      clearTimeout(this.pingTimeoutId);
      this.pingTimeoutId = null;
    }
    
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onerror = null;
      this.ws.onclose = null;
    }
  }

  public destroy(): void {
    this.cleanup();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Factory functions to create WebSocket clients for different backends
export function createDonkeyBetzWebSocketClient(
  endpoint: string,
  options?: Partial<WebSocketClientOptions>
): WebSocketClient {
  const getWebSocketBaseURL = (): string => {
    const envUrl = process.env.EXPO_PUBLIC_WS_URL || 
                   Constants.expoConfig?.extra?.EXPO_PUBLIC_WS_URL;
                   
    if (envUrl) return envUrl;
    
    // Platform-specific defaults for Donkey Betz (port 8001)
    return Platform.select({
      ios: 'ws://localhost:8001',
      android: 'ws://10.0.2.2:8001',
      web: 'ws://localhost:8001',
      default: 'ws://localhost:8001'
    })!;
  };

  const baseUrl = getWebSocketBaseURL();
  const fullUrl = `${baseUrl}${endpoint}`;
  
  // Get auth token from environment or use default
  const authToken = process.env.EXPO_PUBLIC_AUTH_TOKEN || 
                   Constants.expoConfig?.extra?.EXPO_PUBLIC_AUTH_TOKEN ||
                   'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502';

  console.log('[DonkeyBetz WS Factory] Token check:', {
    fromEnv: process.env.EXPO_PUBLIC_AUTH_TOKEN,
    fromExtra: Constants.expoConfig?.extra?.EXPO_PUBLIC_AUTH_TOKEN,
    using: authToken?.substring(0, 8) + '...',
  });

  return new WebSocketClient({
    url: fullUrl,
    authToken,
    maxReconnectAttempts: 5,
    ...options,
  });
}

export function createDBAOWebSocketClient(
  endpoint: string,
  options?: Partial<WebSocketClientOptions>
): WebSocketClient {
  const getWebSocketBaseURL = (): string => {
    const envUrl = process.env.EXPO_PUBLIC_DBAO_WS_URL || 
                   Constants.expoConfig?.extra?.EXPO_PUBLIC_DBAO_WS_URL;
                   
    if (envUrl) return envUrl;
    
    // Platform-specific defaults for DBAO (now on port 8001)
    return Platform.select({
      ios: 'ws://localhost:8001',
      android: 'ws://10.0.2.2:8001',
      web: 'ws://localhost:8001',
      default: 'ws://localhost:8001'
    })!;
  };

  const baseUrl = getWebSocketBaseURL();
  const fullUrl = `${baseUrl}${endpoint}`;
  
  // Get auth token from environment or use default
  const authToken = process.env.EXPO_PUBLIC_AUTH_TOKEN || 
                   Constants.expoConfig?.extra?.EXPO_PUBLIC_AUTH_TOKEN ||
                   'c4ba8e9a9dc7baea61ee3063c3f74ce038a98502';

  console.log('[DBAO WS Factory] Token check:', {
    fromEnv: process.env.EXPO_PUBLIC_AUTH_TOKEN,
    fromExtra: Constants.expoConfig?.extra?.EXPO_PUBLIC_AUTH_TOKEN,
    using: authToken?.substring(0, 8) + '...',
  });

  return new WebSocketClient({
    url: fullUrl,
    authToken,
    maxReconnectAttempts: 5,
    ...options,
  });
}

// Generic factory function (backwards compatibility)
export function createWebSocketClient(
  endpoint: string,
  options?: Partial<WebSocketClientOptions>
): WebSocketClient {
  return createDonkeyBetzWebSocketClient(endpoint, options);
}

// Legacy alias for backward compatibility
export const createAIStudioWebSocketClient = createDonkeyBetzWebSocketClient;