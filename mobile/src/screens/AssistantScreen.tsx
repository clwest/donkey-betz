import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
  Animated,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { assistantService, ChatMessage } from '../services/assistantService';
import { usePersonalAssistantChat } from '../hooks/useWebSocket';

interface QuickAction {
  id: string;
  title: string;
  icon: string;
  command: string;
  description: string;
}

export default function AssistantScreen() {
  // WebSocket-based chat state
  const {
    messages: wsMessages,
    isConnected,
    connectionState,
    isTyping: assistantTyping,
    error: wsError,
    sendMessage: sendWSMessage,
    sendTyping,
    clearMessages,
    connect,
    disconnect,
    ping
  } = usePersonalAssistantChat();

  // Local UI state
  const [inputText, setInputText] = useState('');
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [fallbackMessages, setFallbackMessages] = useState<ChatMessage[]>([]);
  const [useWebSocket, setUseWebSocket] = useState(true);
  const scrollViewRef = useRef<ScrollView>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  // Determine which messages to show (WebSocket or fallback HTTP)
  const messages = useWebSocket ? wsMessages : fallbackMessages;
  const isLoading = useWebSocket ? (connectionState === 'connecting' || assistantTyping) : false;

  const quickActions: QuickAction[] = [
    {
      id: 'help',
      title: 'Help',
      icon: '❓',
      command: '/help',
      description: 'Get help with features'
    },
    {
      id: 'enhance',
      title: 'Enhance',
      icon: '✨',
      command: '/enhance ',
      description: 'Improve a prompt'
    },
    {
      id: 'search',
      title: 'Search',
      icon: '🔍',
      command: '/search ',
      description: 'Search knowledge'
    },
    {
      id: 'remember',
      title: 'Remember',
      icon: '🧠',
      command: '/remember ',
      description: 'Save information'
    },
  ];

  useEffect(() => {
    // Load history when component mounts or when switching to HTTP fallback
    if (!useWebSocket) {
      loadHistory();
    } else {
      // For WebSocket mode, we rely on the real-time messages
      setIsLoadingHistory(false);
    }
    
    // Fade in animation
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, [useWebSocket]);

  // Monitor WebSocket connection and switch to fallback if needed
  useEffect(() => {
    if (wsError && connectionState === 'error' && useWebSocket) {
      console.warn('WebSocket error, considering fallback to HTTP:', wsError);
      // Don't automatically switch - let user decide
    }
  }, [wsError, connectionState, useWebSocket]);

  const loadHistory = async () => {
    try {
      setIsLoadingHistory(true);
      const history = await assistantService.getHistory(20);
      // Reverse to show newest at bottom
      setFallbackMessages(history.messages.reverse());
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = inputText.trim();
    setInputText('');

    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    if (useWebSocket && isConnected) {
      // Send via WebSocket for real-time chat
      const success = sendWSMessage(userMessage);
      
      if (!success) {
        Alert.alert('Error', 'Failed to send message via WebSocket. Try again or switch to HTTP mode.');
      } else {
        // Send typing indicator
        sendTyping(true);
        
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
      }
    } else {
      // Fallback to HTTP API
      const tempUserMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: userMessage,
        created_at: new Date().toISOString(),
        session_id: 'temp'
      };

      setFallbackMessages(prev => [...prev, tempUserMessage]);

      try {
        const response = await assistantService.chat(userMessage);
        
        // Add assistant response
        const assistantMessage: ChatMessage = {
          id: response.message_id,
          role: 'assistant',
          content: response.response,
          created_at: new Date().toISOString(),
          session_id: response.session_id
        };

        setFallbackMessages(prev => [...prev, assistantMessage]);

        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
      } catch (error: any) {
        console.error('Chat error:', error);
        Alert.alert('Error', 'Failed to send message. Please try again.');
        
        // Remove the temporary user message on error
        setFallbackMessages(prev => prev.slice(0, -1));
      }
    }
  };

  const handleQuickAction = (action: QuickAction) => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setInputText(action.command);
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.role === 'user';
    const isAssistant = message.role === 'assistant';

    return (
      <View
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.assistantMessageContainer,
        ]}
      >
        {isAssistant && (
          <View style={styles.assistantAvatar}>
            <Text style={styles.assistantAvatarText}>🤖</Text>
          </View>
        )}
        
        <View
          style={[
            styles.messageBubble,
            isUser ? styles.userMessageBubble : styles.assistantMessageBubble,
          ]}
        >
          {isAssistant && (
            <LinearGradient
              colors={['rgba(102, 126, 234, 0.1)', 'rgba(118, 75, 162, 0.1)']}
              style={styles.assistantMessageGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            />
          )}
          
          <Text
            style={[
              styles.messageText,
              isUser ? styles.userMessageText : styles.assistantMessageText,
            ]}
          >
            {message.content}
          </Text>
          
          <Text
            style={[
              styles.messageTime,
              isUser ? styles.userMessageTime : styles.assistantMessageTime,
            ]}
          >
            {new Date(message.created_at).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </Text>
        </View>

        {isUser && (
          <View style={styles.userAvatar}>
            <Text style={styles.userAvatarText}>👤</Text>
          </View>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.keyboardContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        {/* Header */}
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          style={styles.header}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <View style={styles.headerContent}>
            <View style={styles.headerText}>
              <Text style={styles.headerTitle}>🤖 AI Assistant</Text>
              <Text style={styles.headerSubtitle}>
                Your intelligent content creation companion
              </Text>
            </View>
            
            {/* Connection Status & Mode Switch */}
            <View style={styles.headerControls}>
              <TouchableOpacity
                style={[styles.connectionStatus, isConnected && styles.connectionStatusOnline]}
                onPress={() => {
                  if (useWebSocket) {
                    isConnected ? disconnect() : connect();
                  }
                }}
                activeOpacity={0.8}
              >
                <Text style={styles.connectionDot}>
                  {useWebSocket ? (isConnected ? '🟢' : '🔴') : '📡'}
                </Text>
                <Text style={styles.connectionText}>
                  {useWebSocket 
                    ? (isConnected ? 'Live' : connectionState) 
                    : 'HTTP'
                  }
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={styles.modeSwitch}
                onPress={() => {
                  setUseWebSocket(!useWebSocket);
                  if (Platform.OS !== 'web') {
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                  }
                }}
                activeOpacity={0.8}
              >
                <Text style={styles.modeSwitchText}>
                  {useWebSocket ? 'WS' : 'HTTP'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
          
          {/* Error Banner */}
          {useWebSocket && wsError && (
            <View style={styles.errorBanner}>
              <Text style={styles.errorText}>⚠️ {wsError}</Text>
              <TouchableOpacity
                onPress={() => setUseWebSocket(false)}
                style={styles.errorAction}
              >
                <Text style={styles.errorActionText}>Use HTTP</Text>
              </TouchableOpacity>
            </View>
          )}
        </LinearGradient>

        {/* Quick Actions */}
        <View style={styles.quickActionsContainer}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.quickActionsContent}
          >
            {quickActions.map((action) => (
              <TouchableOpacity
                key={action.id}
                style={styles.quickActionButton}
                onPress={() => handleQuickAction(action)}
                activeOpacity={0.7}
              >
                <BlurView intensity={80} tint="light" style={styles.quickActionBlur}>
                  <Text style={styles.quickActionIcon}>{action.icon}</Text>
                  <Text style={styles.quickActionTitle}>{action.title}</Text>
                  <Text style={styles.quickActionDescription}>
                    {action.description}
                  </Text>
                </BlurView>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Chat Messages */}
        <Animated.View style={[styles.chatContainer, { opacity: fadeAnim }]}>
          {isLoadingHistory ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={theme.colors.primary.main} />
              <Text style={styles.loadingText}>Loading chat history...</Text>
            </View>
          ) : (
            <ScrollView
              ref={scrollViewRef}
              style={styles.messagesScroll}
              contentContainerStyle={styles.messagesContainer}
              onContentSizeChange={() => 
                scrollViewRef.current?.scrollToEnd({ animated: true })
              }
            >
              {messages.length === 0 ? (
                <View style={styles.emptyState}>
                  <Text style={styles.emptyStateIcon}>💬</Text>
                  <Text style={styles.emptyStateTitle}>Start a conversation</Text>
                  <Text style={styles.emptyStateText}>
                    Ask me anything about content creation, or try one of the quick actions above!
                  </Text>
                </View>
              ) : (
                messages.map((message) => (
                  <View key={message.id}>
                    {renderMessage(message)}
                  </View>
                ))
              )}
              
              {(isLoading || (useWebSocket && assistantTyping)) && (
                <View style={styles.typingIndicator}>
                  <View style={styles.assistantAvatar}>
                    <Text style={styles.assistantAvatarText}>🤖</Text>
                  </View>
                  <View style={styles.typingBubble}>
                    <ActivityIndicator size="small" color={theme.colors.primary.main} />
                    <Text style={styles.typingText}>
                      {useWebSocket ? 'AI is responding...' : 'AI is thinking...'}
                    </Text>
                  </View>
                </View>
              )}
            </ScrollView>
          )}
        </Animated.View>

        {/* Input Area */}
        <BlurView intensity={80} tint="light" style={styles.inputContainer}>
          <View style={styles.inputWrapper}>
            <TextInput
              style={styles.textInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Ask your AI assistant anything..."
              placeholderTextColor={theme.colors.text.secondary}
              multiline
              maxLength={1000}
              editable={!isLoading}
            />
            <TouchableOpacity
              style={[
                styles.sendButton,
                (!inputText.trim() || isLoading) && styles.sendButtonDisabled,
              ]}
              onPress={sendMessage}
              disabled={!inputText.trim() || isLoading}
              activeOpacity={0.7}
            >
              <LinearGradient
                colors={
                  inputText.trim() && !isLoading
                    ? theme.colors.primary.gradient
                    : ['#ccc', '#999']
                }
                style={styles.sendButtonGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <Text style={styles.sendButtonText}>
                  {isLoading ? '⏳' : '📤'}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </BlurView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  keyboardContainer: {
    flex: 1,
  },
  header: {
    padding: 20,
    paddingTop: 60,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerText: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  headerControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  connectionStatusOnline: {
    backgroundColor: 'rgba(34, 197, 94, 0.2)',
    borderColor: 'rgba(34, 197, 94, 0.5)',
  },
  connectionDot: {
    fontSize: 12,
    marginRight: 4,
  },
  connectionText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  modeSwitch: {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  modeSwitchText: {
    fontSize: 11,
    color: 'white',
    fontWeight: '700',
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    marginTop: 12,
    padding: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  errorText: {
    flex: 1,
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.9)',
    marginRight: 8,
  },
  errorAction: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  errorActionText: {
    fontSize: 11,
    color: 'white',
    fontWeight: '600',
  },
  quickActionsContainer: {
    backgroundColor: theme.colors.background.secondary,
    paddingVertical: 12,
  },
  quickActionsContent: {
    paddingHorizontal: 16,
    gap: 12,
  },
  quickActionButton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  quickActionBlur: {
    padding: 12,
    alignItems: 'center',
    minWidth: 80,
    backgroundColor: Platform.OS === 'android' ? 'rgba(255, 255, 255, 0.9)' : 'transparent',
  },
  quickActionIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  quickActionTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: 2,
  },
  quickActionDescription: {
    fontSize: 10,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  chatContainer: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    marginTop: 16,
  },
  messagesScroll: {
    flex: 1,
  },
  messagesContainer: {
    padding: 16,
    paddingBottom: 80,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyStateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'flex-end',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  assistantMessageContainer: {
    justifyContent: 'flex-start',
  },
  assistantAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.primary.main,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  assistantAvatarText: {
    fontSize: 16,
  },
  userAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.background.tertiary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  userAvatarText: {
    fontSize: 16,
  },
  messageBubble: {
    maxWidth: '75%',
    borderRadius: 16,
    padding: 12,
    position: 'relative',
  },
  userMessageBubble: {
    backgroundColor: theme.colors.primary.main,
  },
  assistantMessageBubble: {
    backgroundColor: theme.colors.background.secondary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  assistantMessageGradient: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: 16,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
    marginBottom: 4,
  },
  userMessageText: {
    color: 'white',
  },
  assistantMessageText: {
    color: theme.colors.text.primary,
  },
  messageTime: {
    fontSize: 12,
    opacity: 0.7,
  },
  userMessageTime: {
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'right',
  },
  assistantMessageTime: {
    color: theme.colors.text.secondary,
  },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  typingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 16,
    padding: 12,
    marginLeft: 8,
  },
  typingText: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginLeft: 8,
    fontStyle: 'italic',
  },
  inputContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: Platform.OS === 'android' ? 'rgba(255, 255, 255, 0.95)' : 'transparent',
  },
  inputWrapper: {
    flexDirection: 'row',
    padding: 16,
    paddingBottom: Platform.OS === 'ios' ? 32 : 16,
    alignItems: 'flex-end',
  },
  textInput: {
    flex: 1,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: theme.colors.text.primary,
    maxHeight: 120,
    marginRight: 12,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  sendButton: {
    borderRadius: 20,
    overflow: 'hidden',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonGradient: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonText: {
    fontSize: 18,
  },
});