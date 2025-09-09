/**
 * Unified WebSocket Service for Personal Assistant
 * 
 * Features:
 * - Token-based authentication
 * - Automatic reconnection with exponential backoff (capped at 30 seconds)
 * - Message queuing during disconnection
 * - Connection status monitoring
 * - React hooks for easy component integration
 */

import { Platform } from 'react-native';
import { storage, STORAGE_KEYS, DEFAULT_AUTH_TOKEN } from './apiConfig';

// Types
export interface WebSocketMessage {
  type: 'message' | 'ping' | 'pong' | 'typing' | 'get_context' | 'context' | 'connection_established' | 'error';
  message?: string;
  session_id?: string;
  timestamp?: string;
  data?: any;
  is_typing?: boolean;
  user?: string;
  context?: any;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  session_id: string;
}

export type ConnectionState = 'idle' | 'connecting' | 'open' | 'pong' | 'closed' | 'error';

export interface ConnectionStatus {
  state: ConnectionState;
  isConnected: boolean;
  lastMessage: string;
  lastError: string;
  reconnectAttempts: number;
  url: string;
}

// Event handlers
type MessageHandler = (message: WebSocketMessage) => void;
type StatusHandler = (status: ConnectionStatus) => void;
type ChatHandler = (message: ChatMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private authToken: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private pingTimeout: NodeJS.Timeout | null = null;
  private messageQueue: WebSocketMessage[] = [];
  private isReconnecting = false;

  // Current status
  private status: ConnectionStatus = {
    state: 'idle',
    isConnected: false,
    lastMessage: '',
    lastError: '',
    reconnectAttempts: 0,
    url: '',
  };

  // Event handlers
  private messageHandlers = new Set<MessageHandler>();
  private statusHandlers = new Set<StatusHandler>();
  private chatHandlers = new Set<ChatHandler>();

  constructor() {
    // Determine WebSocket URL based on platform
    this.url = this.getWebSocketURL();
    this.status.url = this.url;
    
    // Initialize auth token
    this.initializeAuth();
  }

  private getWebSocketURL(): string {
    // Use environment variable if available, otherwise fall back to platform-specific defaults
    const envUrl = process.env.EXPO_PUBLIC_WS_URL;
    
    if (envUrl) {
      return `${envUrl}/ws/assistant/`;
    }
    
    // Platform-specific fallbacks for localhost:8001 (AI Studio)
    const baseUrl = Platform.select({
      ios: 'ws://localhost:8001',
      android: 'ws://10.0.2.2:8001', 
      web: 'ws://localhost:8001',
      default: 'ws://localhost:8001',
    });
    
    return `${baseUrl}/ws/assistant/`;
  }

  private async initializeAuth() {
    try {
      const token = await storage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      this.authToken = token || DEFAULT_AUTH_TOKEN;
      
      // Auto-connect if we have a token
      if (this.authToken && this.status.state === 'idle') {
        this.connect();
      }
    } catch (error) {
      console.warn('Failed to load auth token, using default:', error);
      this.authToken = DEFAULT_AUTH_TOKEN;
      this.connect();
    }
  }

  // Public methods
  public async connect(): Promise<void> {
    if (this.status.state === 'connecting' || this.status.state === 'open') {
      return; // Already connecting or connected
    }

    if (!this.authToken) {
      await this.initializeAuth();
      return;
    }

    this.cleanup();
    this.updateStatus({ state: 'connecting', lastError: '' });

    try {
      const authenticatedUrl = `${this.url}?token=${this.authToken}`;
      console.log(`[WebSocket] Connecting to: ${this.url} with token`);
      
      this.ws = new WebSocket(authenticatedUrl);
      this.setupEventHandlers();
      
      // Connection timeout
      setTimeout(() => {
        if (this.ws?.readyState === WebSocket.CONNECTING) {
          this.ws.close();
          this.updateStatus({ 
            state: 'error', 
            lastError: 'Connection timeout',
            isConnected: false 
          });
        }
      }, 15000); // 15 second timeout

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.updateStatus({
        state: 'error',
        isConnected: false,
        lastError: `Connection failed: ${error}`
      });
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.reconnectAttempts = 0; // Prevent auto-reconnect
    this.cleanup();
    this.updateStatus({ 
      state: 'closed', 
      isConnected: false,
      lastMessage: 'Manually disconnected'
    });
  }

  public send(message: WebSocketMessage): boolean {
    if (this.status.state === 'open' && this.ws) {
      try {
        this.ws.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('Failed to send message:', error);
        this.updateStatus({ lastError: `Send failed: ${error}` });
        
        // Queue message for retry
        this.messageQueue.push(message);
        return false;
      }
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(message);
      
      // Try to reconnect if not already trying
      if (this.status.state === 'closed' || this.status.state === 'error') {
        this.connect();
      }
      
      return false;
    }
  }

  // Convenience methods for common operations
  public sendChatMessage(message: string, sessionId?: string): boolean {
    return this.send({
      type: 'message',
      message,
      session_id: sessionId,
      timestamp: new Date().toISOString(),
    });
  }

  public sendPing(): boolean {
    const success = this.send({
      type: 'get_context',
      timestamp: new Date().toISOString(),
    });
    
    if (success) {
      this.updateStatus({ 
        state: 'pong',
        lastMessage: 'Ping sent (requesting context)' 
      });
      
      // Set timeout for response
      this.clearPingTimeout();
      this.pingTimeout = setTimeout(() => {
        this.updateStatus({ 
          state: 'error',
          lastError: 'Ping timeout - no response received' 
        });
      }, 10000);
    }
    
    return success;
  }

  public sendTyping(isTyping: boolean): boolean {
    return this.send({
      type: 'typing',
      is_typing: isTyping,
    });
  }

  // Event handler management
  public onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  public onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);
    // Immediately call with current status
    handler(this.status);
    return () => this.statusHandlers.delete(handler);
  }

  public onChatMessage(handler: ChatHandler): () => void {
    this.chatHandlers.add(handler);
    return () => this.chatHandlers.delete(handler);
  }

  // Getters
  public getStatus(): ConnectionStatus {
    return { ...this.status };
  }

  public isConnected(): boolean {
    return this.status.isConnected;
  }

  public getUrl(): string {
    return this.url;
  }

  // Private methods
  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.updateStatus({
        state: 'open',
        isConnected: true,
        lastMessage: 'Connected to WebSocket',
        lastError: '',
        reconnectAttempts: 0,
      });
      
      this.reconnectAttempts = 0;
      this.isReconnecting = false;
      
      // Process queued messages
      this.processMessageQueue();
      
      // Send initial ping after connection
      setTimeout(() => {
        this.sendPing();
      }, 1000);
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        this.handleMessage(data);
      } catch (error) {
        // Handle non-JSON messages as text
        const textMessage: WebSocketMessage = {
          type: 'message',
          message: event.data.toString(),
        };
        this.handleMessage(textMessage);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.updateStatus({
        state: 'error',
        isConnected: false,
        lastError: 'Connection error occurred',
      });
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.updateStatus({
        state: 'closed',
        isConnected: false,
      });

      let shouldReconnect = true;
      let errorMessage = '';

      // Handle specific close codes
      switch (event.code) {
        case 1000: // Normal closure
          shouldReconnect = false;
          errorMessage = 'Connection closed normally';
          break;
        case 1006: // Connection failed
          errorMessage = 'Connection failed: Server authentication error';
          break;
        case 4003: // Authentication failed
          errorMessage = 'Authentication failed: Invalid or missing token';
          shouldReconnect = this.reconnectAttempts === 0; // Only retry once for auth errors
          break;
        default:
          errorMessage = `Connection closed (${event.code}): ${event.reason || 'Unknown reason'}`;
      }

      this.updateStatus({ lastMessage: errorMessage });
      this.ws = null;

      // Auto-reconnect unless it was manual or auth error (after first attempt)
      if (shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts && !this.isReconnecting) {
        this.scheduleReconnect();
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    // Clear ping timeout for any valid message
    if (message.type === 'context' || message.type === 'pong') {
      this.clearPingTimeout();
      this.updateStatus({ 
        state: 'open', // Reset from pong state
        lastMessage: `Ping response: ${message.type} received`,
        lastError: '',
      });
    } else if (message.type === 'connection_established') {
      this.updateStatus({
        state: 'open',
        lastMessage: `Connected: ${message.message || 'Welcome!'}`,
        lastError: '',
      });
    } else if (message.type === 'error') {
      this.updateStatus({
        state: 'error',
        lastError: message.message || 'Server error occurred',
        lastMessage: `Error: ${message.message || 'Unknown error'}`,
      });
    } else if (message.type === 'message') {
      // Handle chat messages specially
      if (message.message && message.session_id) {
        const chatMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: message.message,
          created_at: message.timestamp || new Date().toISOString(),
          session_id: message.session_id,
        };
        
        this.chatHandlers.forEach(handler => handler(chatMessage));
      }
      
      // Update status
      const messageText = message.message || JSON.stringify(message.data || message);
      this.updateStatus({
        lastMessage: messageText.length > 50 
          ? `${messageText.substring(0, 50)}...` 
          : messageText,
      });
    }

    // Notify all message handlers
    this.messageHandlers.forEach(handler => handler(message));
  }

  private scheduleReconnect(): void {
    if (this.isReconnecting) return;
    
    this.isReconnecting = true;
    this.reconnectAttempts++;
    
    // Exponential backoff capped at 30 seconds
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
    
    this.updateStatus({ 
      lastMessage: `Reconnecting in ${Math.ceil(delay / 1000)}s... (attempt ${this.reconnectAttempts})`,
      reconnectAttempts: this.reconnectAttempts,
    });
    
    this.reconnectTimeout = setTimeout(async () => {
      // Reload auth token before reconnecting in case it was updated
      try {
        const token = await storage.getItem(STORAGE_KEYS.AUTH_TOKEN);
        this.authToken = token || DEFAULT_AUTH_TOKEN;
      } catch (error) {
        console.warn('Failed to reload auth token on reconnect:', error);
      }
      
      this.connect();
    }, delay);
  }

  private processMessageQueue(): void {
    if (this.messageQueue.length === 0) return;
    
    console.log(`[WebSocket] Processing ${this.messageQueue.length} queued messages`);
    
    // Send all queued messages
    const queue = [...this.messageQueue];
    this.messageQueue = [];
    
    queue.forEach(message => {
      this.send(message);
    });
  }

  private updateStatus(updates: Partial<ConnectionStatus>): void {
    this.status = { ...this.status, ...updates };
    this.statusHandlers.forEach(handler => handler(this.status));
  }

  private cleanup(): void {
    this.clearReconnectTimeout();
    this.clearPingTimeout();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  private clearPingTimeout(): void {
    if (this.pingTimeout) {
      clearTimeout(this.pingTimeout);
      this.pingTimeout = null;
    }
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();
export default webSocketService;