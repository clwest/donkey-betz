/**
 * Agent Activity Monitor - Simplified Agent Channels for Betting Page
 * 
 * Shows real-time agent communications during orchestration for
 * betting analysis. Provides visibility into what agents are doing.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { getWebSocketManager } from '../../services/agent-orchestra.service';
import { 
  MessageCircle, 
  Users, 
  Activity, 
  Volume2, 
  VolumeX,
  Play, 
  Pause,
  Clock,
  Bot,
  Zap,
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import '../../styles/gaming-theme.css';

interface AgentMessage {
  id: string;
  agent_id: string;
  agent_name: string;
  message_type: 'thinking' | 'analysis' | 'result' | 'coordination' | 'error';
  content: string;
  timestamp: string;
  status?: 'running' | 'completed' | 'error';
  phase?: string;
}

interface AgentActivityMonitorProps {
  gameId: string;
  onAgentActivity?: (activity: AgentMessage) => void;
  className?: string;
}

// Use shared WebSocket manager for agent activity
function useAgentWebSocket(gameId: string, options: {
  onMessage?: (message: AgentMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}) {
  const [isConnected, setIsConnected] = useState(false);
  const wsManagerRef = useRef(getWebSocketManager());
  const unsubscribeRef = useRef<(() => void) | null>(null);
  const hasSubscribedRef = useRef(false);

  useEffect(() => {
    const wsManager = wsManagerRef.current;
    
    // Connect if not already connected
    const initConnection = async () => {
      try {
        if (!wsManager.isConnected()) {
          await wsManager.connect('agents');
        }
        setIsConnected(true);
        // Only log in development and once per connection
        if (import.meta.env.DEV && !hasSubscribedRef.current) {
          console.log('🔗 Agent Activity Monitor using shared WebSocket for game:', gameId);
        }
        
        // Only subscribe once
        if (!hasSubscribedRef.current) {
          // Send subscription message for this game
          wsManager.send({
            type: 'subscribe',
            channel: `game_${gameId}`,
            game_id: gameId
          });
          hasSubscribedRef.current = true;
        }
        
        options.onConnect?.();
      } catch (error) {
        console.error('Failed to initialize WebSocket connection:', error);
        setIsConnected(false);
      }
    };

    initConnection();

    // Subscribe to agent progress messages
    const unsubscribe = wsManager.subscribe('agent_progress', (data: any) => {
      if (data.data && data.data.game_id === gameId) {
        const msgData = data.data;
        const message: AgentMessage = {
          id: msgData.id || `${Date.now()}-${Math.random()}`,
          agent_id: msgData.agent_id,
          agent_name: msgData.agent_name || msgData.agent_id,
          message_type: msgData.message_type || 'analysis',
          content: msgData.content || msgData.message || 'Processing...',
          timestamp: msgData.timestamp || new Date().toISOString(),
          status: msgData.status,
          phase: msgData.phase
        };
        options.onMessage?.(message);
      }
    });
    unsubscribeRef.current = unsubscribe;

    // Cleanup
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      // Unsubscribe from game channel when unmounting
      if (hasSubscribedRef.current) {
        wsManager.send({
          type: 'unsubscribe',
          channel: `game_${gameId}`
        });
        hasSubscribedRef.current = false;
      }
      options.onDisconnect?.();
    };
  }, [gameId]);

  const sendMessage = useCallback((message: any) => {
    wsManagerRef.current.send(message);
  }, []);

  return { isConnected, sendMessage };
}

// Agent Activity Monitor Component
export const AgentActivityMonitor: React.FC<AgentActivityMonitorProps> = ({
  gameId,
  onAgentActivity,
  className = ''
}) => {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageIdSetRef = useRef(new Set<string>());

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const { isConnected } = useAgentWebSocket(gameId, {
    onMessage: (message) => {
      // Prevent duplicate messages by checking ID
      if (messageIdSetRef.current.has(message.id)) {
        return;
      }
      messageIdSetRef.current.add(message.id);
      
      if (!isPaused) {
        setMessages(prev => {
          const newMessages = [...prev, message];
          // Keep only last 50 messages to prevent memory issues
          if (newMessages.length > 50) {
            const removed = newMessages.shift();
            if (removed) {
              messageIdSetRef.current.delete(removed.id);
            }
          }
          return newMessages;
        });
        onAgentActivity?.(message);
      }
    },
    onConnect: () => {
      // Only log meaningful connection events in development
      if (import.meta.env.DEV && messages.length === 0) {
        console.log('✅ Agent Activity Monitor ready');
      }
    },
    onDisconnect: () => {
      // Silent disconnect unless there's an issue
    }
  });

  const clearMessages = () => {
    setMessages([]);
    messageIdSetRef.current.clear();
  };

  const getMessageIcon = (type: AgentMessage['message_type']) => {
    switch (type) {
      case 'thinking':
        return <Clock className="w-4 h-4 text-blue-400" />;
      case 'analysis':
        return <Zap className="w-4 h-4 text-yellow-400" />;
      case 'result':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'coordination':
        return <Users className="w-4 h-4 text-purple-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <MessageCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getMessageStyle = (type: AgentMessage['message_type']) => {
    switch (type) {
      case 'thinking':
        return 'border-blue-500/30 bg-blue-900/10';
      case 'analysis':
        return 'border-yellow-500/30 bg-yellow-900/10';
      case 'result':
        return 'border-green-500/30 bg-green-900/10';
      case 'coordination':
        return 'border-purple-500/30 bg-purple-900/10';
      case 'error':
        return 'border-red-500/30 bg-red-900/10';
      default:
        return 'border-gaming-border/50 bg-gaming-bg/50';
    }
  };

  return (
    <Card className={`gaming-card ${className}`}>
      <div className="gaming-border-glow"></div>
      
      {/* Header */}
      <div className="p-4 border-b border-gaming-border flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h3 className="text-lg font-bold gaming-text-primary">Agent Activity Monitor</h3>
          <Badge variant={isConnected ? 'success' : 'destructive'} className="text-xs">
            {isConnected ? 'LIVE' : 'OFFLINE'}
          </Badge>
          {messages.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {messages.length} messages
            </Badge>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMuted(!isMuted)}
            className="gaming-btn p-2"
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsPaused(!isPaused)}
            className="gaming-btn p-2"
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={clearMessages}
            className="gaming-btn p-2"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMinimized(!isMinimized)}
            className="gaming-btn p-2"
          >
            {isMinimized ? '▲' : '▼'}
          </Button>
        </div>
      </div>
      
      {/* Messages Container */}
      {!isMinimized && (
        <div className="h-64 overflow-y-auto p-4 space-y-2 gaming-scrollbar">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <Bot className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Waiting for agent activity...</p>
              <p className="text-xs mt-1">Agents will appear here when analysis begins</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start gap-3 p-3 rounded-lg border transition-all animate-fadeIn ${getMessageStyle(msg.message_type)}`}
              >
                {getMessageIcon(msg.message_type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold text-gray-300">
                      {msg.agent_name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 break-words">
                    {msg.content}
                  </p>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      )}
    </Card>
  );
};

export default AgentActivityMonitor;