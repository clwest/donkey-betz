/**
 * WebSocket Manager with Auto-Reconnect and Health Checks
 * Fixes the issue where WebSockets don't initialize properly without hard refresh
 */

interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
}

class WebSocketManager {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageQueue: WebSocketMessage[] = [];
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private isIntentionallyClosed = false;
  private connectionPromise: Promise<void> | null = null;

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      debug: false,
      ...config
    };
  }

  /**
   * Connect to WebSocket with retry logic
   */
  async connect(): Promise<void> {
    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    this.connectionPromise = this._connect();
    return this.connectionPromise;
  }

  private async _connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.isIntentionallyClosed = false;
        
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.log('WebSocket already connected');
          resolve();
          return;
        }

        // Clean up existing connection
        this.cleanup();

        this.log(`Connecting to ${this.config.url}...`);
        this.ws = new WebSocket(this.config.url);

        this.ws.onopen = () => {
          this.log('WebSocket connected successfully');
          this.reconnectAttempts = 0;
          this.connectionPromise = null;
          
          // Start heartbeat
          this.startHeartbeat();
          
          // Send queued messages
          this.flushMessageQueue();
          
          // Notify listeners
          this.emit('connected', {});
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (e) {
            this.log('Failed to parse message:', event.data);
          }
        };

        this.ws.onerror = (error) => {
          this.log('WebSocket error:', error);
          this.emit('error', error);
        };

        this.ws.onclose = (event) => {
          this.log(`WebSocket closed: ${event.code} - ${event.reason}`);
          this.connectionPromise = null;
          
          // Stop heartbeat
          this.stopHeartbeat();
          
          // Notify listeners
          this.emit('disconnected', { code: event.code, reason: event.reason });
          
          // Attempt reconnection if not intentionally closed
          if (!this.isIntentionallyClosed) {
            this.scheduleReconnect();
          }
          
          // Only reject if this was the initial connection attempt
          if (this.reconnectAttempts === 0) {
            reject(new Error(`WebSocket connection failed: ${event.reason}`));
          }
        };

      } catch (error) {
        this.log('Failed to create WebSocket:', error);
        this.connectionPromise = null;
        reject(error);
      }
    });
  }

  /**
   * Send a message through WebSocket
   */
  send(message: WebSocketMessage): void {
    if (!message.timestamp) {
      message.timestamp = new Date().toISOString();
    }

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      this.log('Sent message:', message);
    } else {
      this.log('WebSocket not ready, queuing message:', message);
      this.messageQueue.push(message);
      
      // Try to reconnect if not already trying
      if (!this.reconnectTimeout) {
        this.connect();
      }
    }
  }

  /**
   * Subscribe to specific message types
   */
  on(type: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    
    this.listeners.get(type)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(type)?.delete(callback);
    };
  }

  /**
   * Close the WebSocket connection
   */
  disconnect(): void {
    this.log('Disconnecting WebSocket...');
    this.isIntentionallyClosed = true;
    this.cleanup();
  }

  /**
   * Force reconnect (useful after backend restart)
   */
  async forceReconnect(): Promise<void> {
    this.log('Forcing reconnection...');
    this.disconnect();
    await new Promise(resolve => setTimeout(resolve, 100));
    return this.connect();
  }

  /**
   * Get connection state
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  // Private methods

  private cleanup(): void {
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.onmessage = null;
      
      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.close();
      }
      
      this.ws = null;
    }
    
    this.stopHeartbeat();
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      this.log('Max reconnection attempts reached');
      this.emit('max_reconnect_reached', {});
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1),
      30000
    );

    this.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms...`);
    
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    this.log('Received message:', message);
    
    // Handle system messages
    if (message.type === 'pong') {
      return; // Heartbeat response
    }
    
    // Emit to specific listeners
    this.emit(message.type, message.data || message);
    
    // Emit to general listeners
    this.emit('message', message);
  }

  private emit(type: string, data: any): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in listener for ${type}:`, error);
        }
      });
    }
  }

  private log(...args: any[]): void {
    if (this.config.debug) {
      console.log('[WebSocketManager]', ...args);
    }
  }
}

// Singleton instances for different WebSocket connections
let dashboardWS: WebSocketManager | null = null;
let agentsWS: WebSocketManager | null = null;
let assistantWS: WebSocketManager | null = null;

/**
 * Get or create WebSocket connection for dashboard
 */
export function getDashboardWebSocket(): WebSocketManager {
  if (!dashboardWS) {
    dashboardWS = new WebSocketManager({
      url: 'ws://localhost:8000/ws/dashboard/',
      debug: true
    });
  }
  return dashboardWS;
}

/**
 * Get or create WebSocket connection for agents
 */
export function getAgentsWebSocket(): WebSocketManager {
  if (!agentsWS) {
    agentsWS = new WebSocketManager({
      url: 'ws://localhost:8000/ws/agents/',
      debug: true
    });
  }
  return agentsWS;
}

/**
 * Get or create WebSocket connection for AI assistant
 */
export function getAssistantWebSocket(): WebSocketManager {
  if (!assistantWS) {
    assistantWS = new WebSocketManager({
      url: 'ws://localhost:8000/ws/assistant/',
      debug: true
    });
  }
  return assistantWS;
}

/**
 * Initialize all WebSocket connections
 * Call this when the app starts or after backend restart
 */
export async function initializeWebSockets(): Promise<void> {
  console.log('Initializing WebSocket connections...');
  
  const connections = [
    getDashboardWebSocket().connect(),
    getAgentsWebSocket().connect(),
    getAssistantWebSocket().connect()
  ];
  
  try {
    await Promise.all(connections);
    console.log('All WebSocket connections established');
  } catch (error) {
    console.error('Some WebSocket connections failed:', error);
  }
}

/**
 * Force reconnect all WebSockets
 * Useful after backend restart or connection issues
 */
export async function reconnectAllWebSockets(): Promise<void> {
  console.log('Forcing reconnection of all WebSockets...');
  
  const reconnections = [];
  
  if (dashboardWS) {
    reconnections.push(dashboardWS.forceReconnect());
  }
  
  if (agentsWS) {
    reconnections.push(agentsWS.forceReconnect());
  }
  
  if (assistantWS) {
    reconnections.push(assistantWS.forceReconnect());
  }
  
  try {
    await Promise.all(reconnections);
    console.log('All WebSockets reconnected');
  } catch (error) {
    console.error('Some WebSocket reconnections failed:', error);
  }
}

export default WebSocketManager;
