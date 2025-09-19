/**
 * Agent Channels - "Slack for AI Agents"
 * 
 * Real-time agent collaboration viewer that allows users to watch agents
 * think, communicate, and work together in Slack-style channels.
 * 
 * Uses hybrid REST API + WebSocket approach for optimal performance.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { buildWsUrl } from '../../config/api.config';
import { agentChannelsService } from '../../services/agentChannels.service';
import type { 
  AgentChannel, 
  ChannelMessage, 
  ChannelMembership,
  PostMessageRequest 
} from '../../services/agentChannels.service';
import { 
  MessageCircle, 
  Users, 
  Activity, 
  Search, 
  Settings, 
  Volume2, 
  VolumeX, 
  Play, 
  Pause, 
  Download,
  Hash,
  Clock,
  User,
  Send,
  Plus,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

interface UseWebSocketOptions {
  onMessage?: (message: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  autoReconnect?: boolean;
}

// WebSocket hook for real-time updates
function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    try {
      const wsUrl = url.startsWith('ws') ? url : buildWsUrl(url);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
        options.onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          options.onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setSocket(null);
        options.onDisconnect?.();

        // Auto-reconnect logic
        if (options.autoReconnect && reconnectAttempts.current < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000));
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      setSocket(ws);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [url, options]);

  useEffect(() => {
    connect();
    return () => {
      socket?.close();
    };
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, isConnected]);

  return { isConnected, sendMessage };
}

export const AgentChannels: React.FC = () => {
  const [channels, setChannels] = useState<AgentChannel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<AgentChannel | null>(null);
  const [messages, setMessages] = useState<ChannelMessage[]>([]);
  const [members, setMembers] = useState<ChannelMembership[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [messageInput, setMessageInput] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingData, setRecordingData] = useState<any[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Load channels from REST API
  const loadChannels = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await agentChannelsService.channels.listChannels({
        is_active: true,
        page_size: 100
      });
      setChannels(response.results);
    } catch (err) {
      console.error('Failed to load channels:', err);
      setError('Failed to load channels. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Load messages for selected channel
  const loadChannelMessages = async (channelId: string) => {
    try {
      setLoadingMessages(true);
      setError(null);
      const response = await agentChannelsService.channels.getChannelMessages(channelId, {
        page_size: 50
      });
      setMessages(response.results.reverse()); // Reverse to show oldest first
      
      // Load members
      const membersData = await agentChannelsService.channels.getChannelMembers(channelId);
      setMembers(membersData);
    } catch (err) {
      console.error('Failed to load messages:', err);
      setError('Failed to load messages. Please try again.');
    } finally {
      setLoadingMessages(false);
    }
  };

  // Send message to channel
  const sendMessage = async () => {
    if (!selectedChannel || !messageInput.trim()) return;

    try {
      const messageData: PostMessageRequest = {
        content: messageInput,
        message_type: 'user_message'
      };
      
      const newMessage = await agentChannelsService.channels.postMessage(
        selectedChannel.id,
        messageData
      );
      
      // Add to local state immediately
      setMessages(prev => [...prev, newMessage]);
      setMessageInput('');
      
      // Play notification sound
      if (soundEnabled && audioRef.current) {
        audioRef.current.currentTime = 0;
        audioRef.current.play().catch(e => console.log('Audio play failed:', e));
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message. Please try again.');
    }
  };

  // WebSocket connection for real-time updates
  const { isConnected, sendMessage: sendWsMessage } = useWebSocket('/ws/channels/', {
    onMessage: (message) => {
      console.log('[AgentChannels] WebSocket message:', message);
      
      if (message.type === 'channel_message' || message.type === 'agent_message') {
        const newMessage = message.data || message;
        
        // Add to messages if it's for the selected channel
        if (selectedChannel && (
          newMessage.channel === selectedChannel.id ||
          newMessage.channel_id === selectedChannel.id
        )) {
          setMessages(prev => {
            // Avoid duplicates
            if (prev.some(m => m.id === newMessage.id)) {
              return prev;
            }
            return [...prev, newMessage];
          });
          
          // Play notification sound
          if (soundEnabled && audioRef.current) {
            audioRef.current.currentTime = 0;
            audioRef.current.play().catch(e => console.log('Audio play failed:', e));
          }
        }
        
        // Update channel message count
        setChannels(prev => prev.map(channel => 
          channel.id === (newMessage.channel || newMessage.channel_id)
            ? { ...channel, message_count: (channel.message_count || 0) + 1 }
            : channel
        ));
        
        // Add to recording if active
        if (isRecording) {
          setRecordingData(prev => [...prev, {
            timestamp: new Date().toISOString(),
            channel: selectedChannel?.name,
            message: newMessage
          }]);
        }
      }
    },
    onConnect: () => {
      console.log('[AgentChannels] Connected to WebSocket');
      // Subscribe to selected channel if any
      if (selectedChannel) {
        sendWsMessage({
          type: 'subscribe_channel',
          channel_id: selectedChannel.id
        });
      }
    },
    onDisconnect: () => {
      console.log('[AgentChannels] Disconnected from WebSocket');
    },
    autoReconnect: true
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  // Load channels on mount
  useEffect(() => {
    loadChannels();
  }, []);

  // Load messages when channel changes
  useEffect(() => {
    if (selectedChannel) {
      loadChannelMessages(selectedChannel.id);
      
      // Subscribe to channel updates via WebSocket
      if (isConnected) {
        sendWsMessage({
          type: 'subscribe_channel',
          channel_id: selectedChannel.id
        });
      }
    }
  }, [selectedChannel, isConnected]);

  // Auto-select first channel when channels are loaded
  useEffect(() => {
    if (channels.length > 0 && !selectedChannel) {
      const activeChannels = channels.filter(c => c.is_active);
      setSelectedChannel(activeChannels[0] || channels[0]);
    }
  }, [channels, selectedChannel]);

  const formatMessageTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const getMessageTypeIcon = (type: string) => {
    switch (type) {
      case 'agent_message': return '🤖';
      case 'task_update': return '⚡';
      case 'tool_usage': return '🔧';
      case 'collaboration_request': return '🤝';
      case 'status_update': return '📊';
      case 'system_message': return '📢';
      case 'user_message': return '👤';
      case 'result_share': return '📤';
      case 'error_report': return '❌';
      default: return '💬';
    }
  };

  const getMessageTypeColor = (type: string) => {
    switch (type) {
      case 'agent_message': return 'bg-blue-500';
      case 'task_update': return 'bg-yellow-500';
      case 'tool_usage': return 'bg-green-500';
      case 'collaboration_request': return 'bg-purple-500';
      case 'status_update': return 'bg-muted/50';
      case 'system_message': return 'bg-red-500';
      case 'user_message': return 'bg-indigo-500';
      case 'result_share': return 'bg-teal-500';
      case 'error_report': return 'bg-red-600';
      default: return 'bg-blue-500';
    }
  };

  const exportRecording = () => {
    const dataStr = JSON.stringify(recordingData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `agent-chat-recording-${new Date().toISOString().slice(0,19)}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const filteredMessages = messages.filter(message =>
    !searchQuery || 
    message.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    message.agent_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    message.user_username?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
                <MessageCircle className="h-8 w-8 text-foreground" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-foreground">
                  Agent Channels
                </h1>
                <p className="text-slate-600 dark:text-slate-300 mt-1">
                  Watch AI agents think, collaborate, and work together in real-time
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Refresh button */}
              <button
                onClick={loadChannels}
                className="p-2 rounded-lg bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 transition-colors"
                title="Refresh channels"
              >
                <RefreshCw className="h-4 w-4 text-slate-600 dark:text-slate-400" />
              </button>
              
              {/* Recording Controls */}
              <button
                onClick={() => {
                  if (isRecording) {
                    setIsRecording(false);
                  } else {
                    setIsRecording(true);
                    setRecordingData([]);
                  }
                }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 text-foreground' 
                    : 'bg-blue-500 hover:bg-blue-600 text-foreground'
                }`}
              >
                {isRecording ? (
                  <>
                    <Pause className="h-4 w-4" />
                    Stop Recording
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Start Recording
                  </>
                )}
              </button>
              
              {recordingData.length > 0 && (
                <button
                  onClick={exportRecording}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 font-medium transition-colors"
                >
                  <Download className="h-4 w-4" />
                  Export ({recordingData.length})
                </button>
              )}
              
              {/* Connection Status */}
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                isConnected 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-500' 
                  : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-500'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`} />
                <span className="text-sm font-medium">
                  {isConnected ? 'Live' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Error Alert */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-500" />
              <p className="text-red-800 dark:text-red-300">{error}</p>
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-12 gap-6 h-[800px]">
          {/* Channel Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="col-span-3"
          >
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg h-full flex flex-col">
              <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-foreground mb-4 flex items-center">
                  <Users className="h-5 w-5 mr-2 text-blue-500" />
                  Active Channels ({channels.length})
                </h3>
                
                {/* Controls */}
                <div className="flex items-center gap-2 mb-4">
                  <button
                    onClick={() => setSoundEnabled(!soundEnabled)}
                    className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 transition-colors"
                  >
                    {soundEnabled ? 
                      <Volume2 className="h-4 w-4 text-slate-600 dark:text-slate-400" /> : 
                      <VolumeX className="h-4 w-4 text-slate-600 dark:text-slate-400" />
                    }
                  </button>
                  <button
                    onClick={() => setAutoScroll(!autoScroll)}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      autoScroll 
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-500' 
                        : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'
                    }`}
                  >
                    {autoScroll ? 'Auto' : 'Manual'}
                  </button>
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4">
                <div className="space-y-2">
                  {channels.map((channel) => (
                    <div
                      key={channel.id}
                      onClick={() => setSelectedChannel(channel)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        selectedChannel?.id === channel.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30' 
                          : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            channel.is_active ? 'bg-green-500' : 'bg-gray-400'
                          }`} />
                          <Hash className="h-4 w-4 text-slate-500" />
                          <span className="font-medium text-sm text-slate-900 dark:text-foreground truncate">
                            {channel.display_name || channel.name}
                          </span>
                        </div>
                        {channel.message_count > 0 && (
                          <span className="text-xs bg-slate-200 dark:bg-slate-600 text-slate-600 dark:text-slate-300 px-2 py-1 rounded">
                            {channel.message_count}
                          </span>
                        )}
                      </div>
                      
                      <div className="text-xs text-slate-500 dark:text-slate-400 mb-2 truncate">
                        {channel.description || 'Agent collaboration channel'}
                      </div>
                      
                      {channel.member_count !== undefined && (
                        <div className="flex items-center text-xs text-slate-400">
                          <Activity className="h-3 w-3 mr-1" />
                          {channel.member_count} members
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Chat Area */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="col-span-9"
          >
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg h-full flex flex-col">
              {/* Chat Header */}
              <div className="p-6 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-750">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Hash className="h-5 w-5 text-blue-500" />
                    <h2 className="text-xl font-semibold text-slate-900 dark:text-foreground">
                      {selectedChannel?.display_name || selectedChannel?.name || 'Select a channel'}
                    </h2>
                    {selectedChannel?.is_active && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-500 text-xs font-medium rounded">
                        Live
                      </span>
                    )}
                    {isRecording && (
                      <span className="px-2 py-1 bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-500 text-xs font-medium rounded animate-pulse">
                        Recording
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                      <input
                        type="text"
                        placeholder="Search messages..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-64 pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-foreground text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <button className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 transition-colors">
                      <Settings className="h-4 w-4 text-slate-600 dark:text-slate-400" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6">
                {selectedChannel ? (
                  <div className="space-y-4">
                    {loadingMessages ? (
                      <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                        <p className="mt-4 text-slate-500 dark:text-slate-400">Loading messages...</p>
                      </div>
                    ) : filteredMessages.length === 0 ? (
                      <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                        <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p className="text-lg">No messages in this channel yet.</p>
                        <p className="text-sm mt-2">
                          Be the first to send a message or wait for agent communications.
                        </p>
                      </div>
                    ) : (
                      filteredMessages.map((message) => (
                        <div key={message.id} className="flex gap-3 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                          {/* Avatar */}
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-foreground text-sm font-medium">
                              {getMessageTypeIcon(message.message_type)}
                            </div>
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            {/* Message Header */}
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-slate-900 dark:text-foreground text-sm">
                                {message.agent_name || message.user_username || 'System'}
                              </span>
                              <span className={`px-2 py-1 rounded text-xs text-foreground ${getMessageTypeColor(message.message_type)}`}>
                                {message.message_type.replace('_', ' ')}
                              </span>
                              <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {formatMessageTime(message.timestamp || message.created_at)}
                              </span>
                            </div>
                            
                            {/* Message Content */}
                            <div className="text-slate-700 dark:text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">
                              {message.content}
                            </div>
                            
                            {/* Rich Content */}
                            {message.rich_content && Object.keys(message.rich_content).length > 0 && (
                              <div className="mt-2 p-3 bg-slate-100 dark:bg-slate-700 rounded-lg text-sm">
                                <pre className="overflow-auto text-xs">
                                  {JSON.stringify(message.rich_content, null, 2)}
                                </pre>
                              </div>
                            )}
                            
                            {/* Reactions */}
                            {message.reactions && Object.keys(message.reactions).length > 0 && (
                              <div className="mt-2 flex gap-2">
                                {Object.entries(message.reactions).map(([emoji, users]) => (
                                  <span
                                    key={emoji}
                                    className="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-xs flex items-center gap-1"
                                  >
                                    <span>{emoji}</span>
                                    <span className="text-slate-600 dark:text-slate-400">{users.length}</span>
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                    <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">Select a channel to view agent communications</p>
                  </div>
                )}
              </div>

              {/* Message Input */}
              {selectedChannel && (
                <div className="p-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Type a message..."
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-foreground focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!messageInput.trim()}
                      className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-300 disabled:cursor-not-allowed text-foreground rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                      <Send className="h-4 w-4" />
                      Send
                    </button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* Hidden audio element for notifications */}
      <audio ref={audioRef} preload="auto">
        <source src="data:audio/wav;base64,UklGRvIAAABXQVZFZm10IBAAAAABAAABACAAQIDAJAEAIQABAAEBAAEBAEECA..." type="audio/wav" />
      </audio>
    </div>
  );
};