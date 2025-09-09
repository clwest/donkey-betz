/**
 * React hooks for WebSocket integration
 * Provides easy-to-use hooks for components to interact with the WebSocket service
 */

import { useState, useEffect, useCallback } from 'react';
import webSocketService, { 
  WebSocketMessage, 
  ChatMessage, 
  ConnectionStatus, 
  ConnectionState 
} from '../services/websocketService';

/**
 * Hook for WebSocket connection status monitoring
 */
export function useWebSocketStatus() {
  const [status, setStatus] = useState<ConnectionStatus>(webSocketService.getStatus());

  useEffect(() => {
    const unsubscribe = webSocketService.onStatusChange(setStatus);
    return unsubscribe;
  }, []);

  const connect = useCallback(() => {
    webSocketService.connect();
  }, []);

  const disconnect = useCallback(() => {
    webSocketService.disconnect();
  }, []);

  const sendPing = useCallback(() => {
    return webSocketService.sendPing();
  }, []);

  return {
    ...status,
    connect,
    disconnect,
    sendPing,
  };
}

/**
 * Hook for WebSocket message handling
 */
export function useWebSocketMessages() {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);

  useEffect(() => {
    const unsubscribe = webSocketService.onMessage((message) => {
      setMessages(prev => [...prev, message]);
    });

    return unsubscribe;
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    return webSocketService.send(message);
  }, []);

  return {
    messages,
    clearMessages,
    sendMessage,
  };
}

/**
 * Hook for Personal Assistant chat functionality
 * This is the main hook that components should use for chat features
 */
export function usePersonalAssistantChat() {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('idle');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Listen for status changes
    const unsubscribeStatus = webSocketService.onStatusChange((status) => {
      setIsConnected(status.isConnected);
      setConnectionState(status.state);
      setError(status.lastError || null);
    });

    // Listen for incoming chat messages
    const unsubscribeChat = webSocketService.onChatMessage((message) => {
      setChatMessages(prev => [...prev, message]);
      setIsTyping(false); // Stop typing indicator when message arrives
    });

    // Listen for typing indicators
    const unsubscribeMessages = webSocketService.onMessage((message) => {
      if (message.type === 'typing' && message.is_typing !== undefined) {
        setIsTyping(message.is_typing);
      }
    });

    // Auto-connect if not already connected
    if (!isConnected && connectionState === 'idle') {
      webSocketService.connect();
    }

    return () => {
      unsubscribeStatus();
      unsubscribeChat();
      unsubscribeMessages();
    };
  }, [isConnected, connectionState]);

  const sendChatMessage = useCallback((message: string, sessionId?: string) => {
    if (!message.trim()) return false;

    // Add user message to chat immediately for optimistic UI
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message.trim(),
      created_at: new Date().toISOString(),
      session_id: sessionId || 'temp',
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setIsTyping(true); // Show typing indicator
    
    // Send to server
    const success = webSocketService.sendChatMessage(message, sessionId);
    
    if (!success) {
      // Remove optimistic message on failure
      setChatMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      setIsTyping(false);
      setError('Failed to send message - not connected');
    }
    
    return success;
  }, []);

  const sendTyping = useCallback((typing: boolean) => {
    return webSocketService.sendTyping(typing);
  }, []);

  const clearMessages = useCallback(() => {
    setChatMessages([]);
    setError(null);
  }, []);

  const connect = useCallback(() => {
    webSocketService.connect();
  }, []);

  const disconnect = useCallback(() => {
    webSocketService.disconnect();
  }, []);

  const ping = useCallback(() => {
    return webSocketService.sendPing();
  }, []);

  return {
    messages: chatMessages,
    isConnected,
    connectionState,
    isTyping,
    error,
    sendMessage: sendChatMessage,
    sendTyping,
    clearMessages,
    connect,
    disconnect,
    ping,
  };
}

/**
 * Simple hook for connection status only
 */
export function useWebSocketConnection() {
  const [isConnected, setIsConnected] = useState(false);
  const [state, setState] = useState<ConnectionState>('idle');

  useEffect(() => {
    const unsubscribe = webSocketService.onStatusChange((status) => {
      setIsConnected(status.isConnected);
      setState(status.state);
    });

    return unsubscribe;
  }, []);

  return { isConnected, state };
}