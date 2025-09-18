import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import {
  MessageCircle, Send, Bot, User, ThumbsUp, ThumbsDown, X, Minimize2,
  Brain, Sparkles, TrendingUp, RefreshCw, Maximize2, Mic, MicOff,
  HelpCircle, Target, Lightbulb, Zap, Activity, BookOpen, Settings
} from 'lucide-react';
import { apiClient } from '../services/api.config';
import { assistantService } from '../services/assistant.service';
import { useAuthStore } from '../store/authStore';
import { toast } from 'sonner';
import PersonalAssistantInterview from './PersonalAssistantInterview';

interface Message {
  id: string;
  text: string;
  content?: string;
  sender: 'user' | 'assistant';
  role?: 'user' | 'assistant';
  timestamp: Date;
  confidence?: number;
  suggestions?: string[];
  actions?: string[];
  metadata?: any;
  feedback?: 'positive' | 'negative';
}

interface AssistantContext {
  personalization_score?: number;
  confidence_level?: number;
  recommendations?: Array<{
    type: string;
    priority: string;
    title: string;
    description: string;
  }>;
  page_context?: {
    page: string;
    features?: string[];
    suggestions?: string[];
  };
  first_name?: string;
  skills?: {
    top_skills?: string[];
  };
  system_status?: string;
}

interface UnifiedAssistantProps {
  className?: string;
}

export const UnifiedAIAssistant: React.FC<UnifiedAssistantProps> = ({ className }) => {
  const { user } = useAuthStore();
  const location = useLocation();

  // State management
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [context, setContext] = useState<AssistantContext | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showInterview, setShowInterview] = useState(false);

  // Voice recognition state
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef<any>(null);

  // UI refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + ' ';
          }
        }

        if (finalTranscript) {
          setInputMessage(prev => prev + finalTranscript);
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Load context and welcome message on open
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      initializeAssistant();
    }
  }, [isOpen]);

  // Update page context on location change
  useEffect(() => {
    updatePageContext();
  }, [location.pathname]);

  // Auto-scroll to latest message
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeAssistant = async () => {
    try {
      // Try to load personal context - first try dev endpoint, then regular
      const personalResponse = await apiClient.get('/api/assistant/dev/context/')
        .catch(() => apiClient.get('/api/assistant/context/'))
        .catch(() => null);

      if (personalResponse?.data?.context) {
        setContext(personalResponse.data.context);
      } else {
        // Set default context if endpoints are unavailable
        setContext({
          first_name: 'User',
          skills: { top_skills: [] },
          professional_profile: {
            experience_level: 'Unknown',
            profile_completeness: 0
          }
        });
      }

      // Generate a simple session ID for now
      const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);

      // Add personalized welcome message
      const welcomeMessage = createWelcomeMessage(personalResponse?.data?.context);
      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('Failed to initialize assistant:', error);
      addDefaultWelcomeMessage();
    }
  };

  const createWelcomeMessage = (contextData?: any): Message => {
    const userName = user?.first_name || user?.username || 'there';
    const personalizationScore = contextData?.personalization_score || 0;

    let text = `Hi ${userName}! I'm your unified AI assistant. `;

    if (personalizationScore > 0.3) {
      text += `I've learned from our ${contextData?.interaction_count || 0} interactions to better assist you. `;
    } else {
      text += `I combine neural intelligence with personal learning to provide the best assistance. `;
    }

    text += 'How can I help you today?';

    const suggestions = getContextualSuggestions();

    return {
      id: 'welcome',
      text,
      sender: 'assistant',
      timestamp: new Date(),
      confidence: 1,
      suggestions
    };
  };

  const addDefaultWelcomeMessage = () => {
    setMessages([{
      id: 'welcome-default',
      text: "Hi! I'm your AI assistant with neural intelligence and personal learning capabilities. How can I help you today?",
      sender: 'assistant',
      timestamp: new Date(),
      suggestions: ['Explore features', 'View my profile', 'Find opportunities', 'Get help']
    }]);
  };

  const getContextualSuggestions = (): string[] => {
    const path = location.pathname;

    if (path.includes('/profile')) {
      return ['Complete my profile', 'Find job matches', 'Update skills', 'View insights'];
    } else if (path.includes('/dashboard')) {
      return ['Show my stats', 'Recent activity', 'Top opportunities', 'Revenue insights'];
    } else if (path.includes('/agents')) {
      return ['Explain agents', 'Show capabilities', 'Run automation', 'Agent status'];
    } else {
      return ['Find opportunities', 'Update profile', 'View insights', 'Get recommendations'];
    }
  };

  const updatePageContext = () => {
    const pageContextMap: { [key: string]: any } = {
      '/profile': {
        page: 'Profile',
        features: ['Profile completion', 'Skills management', 'Job preferences'],
        icon: '👤'
      },
      '/dashboard': {
        page: 'Dashboard',
        features: ['Analytics', 'Revenue tracking', 'Activity monitoring'],
        icon: '📊'
      },
      '/agents': {
        page: 'Agents',
        features: ['149 AI agents', 'Orchestration', 'Automation'],
        icon: '🤖'
      },
      '/decision-command': {
        page: 'Decision Command',
        features: ['Opportunity analysis', 'AI recommendations', 'Quick actions'],
        icon: '🎯'
      }
    };

    const currentPath = Object.keys(pageContextMap).find(path =>
      location.pathname.startsWith(path)
    );

    if (currentPath && context) {
      setContext({
        ...context,
        page_context: pageContextMap[currentPath]
      });
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Prepare conversation history for context continuity
      const conversationHistory = messages.slice(-5).map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        message: msg.text || msg.content,
        timestamp: msg.timestamp.toISOString()
      }));

      // Try unified assistant first for full agent integration with memory
      let response = await apiClient.post('/api/unified/chat/', {
        message: inputMessage,
        conversation_history: conversationHistory,
        context: {
          page: location.pathname,
          session_id: sessionId,
          conversation_id: sessionId,
          user_context: context ? {
            first_name: context.first_name,
            skills: context.skills
          } : null
        }
      }).catch(() => null);

      // If neural assistant fails, fallback to dev assistant
      if (!response) {
        response = await apiClient.post('/api/assistant/dev/chat/', {
          message: inputMessage,
          conversation_history: conversationHistory,
          context: {
            page: location.pathname,
            session_id: sessionId,
            timestamp: new Date().toISOString(),
            conversation_id: sessionId,
            user_context: context ? {
              first_name: context.first_name,
              skills: context.skills,
              system_status: context.system_status
            } : null
          }
        }).catch(() => null);
      }

      // If both fail, try minimal fallback
      if (!response) {
        response = await apiClient.post('/api/assistant/minimal/chat/', {
          message: inputMessage,
          conversation_history: conversationHistory,
          session_id: sessionId,
          context: {
            page: location.pathname,
            conversation_id: sessionId,
            user_context: context ? {
              first_name: context.first_name,
              skills: context.skills
            } : null
          }
        }).catch(() => null);
      }

      if (response?.data) {
        const data = response.data.data || response.data;

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          text: data.response || data.message || 'I encountered an error processing your request.',
          sender: 'assistant',
          timestamp: new Date(),
          confidence: data.confidence,
          suggestions: data.suggestions || data.follow_up_suggestions,
          actions: data.actions,
          metadata: data.metadata
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Fallback response when backend is unavailable
        const fallbackMessage: Message = {
          id: `assistant-${Date.now()}`,
          text: `I understand you're asking about "${inputMessage}". The assistant backend is currently requiring authentication. To use the full AI capabilities, please ensure you're logged in or wait for the development endpoints to become available.

For now, I can tell you that this platform offers:
- AI-powered Personal Assistant with real-time learning
- 149 specialized agents for various tasks
- Memory system that remembers your preferences
- Job matching and income generation features
- Real-time data analysis and insights

Would you like to explore any specific feature?`,
          sender: 'assistant',
          timestamp: new Date(),
          confidence: 0.5,
          suggestions: ['Login to continue', 'Explore features', 'View documentation'],
          metadata: { fallback: true }
        };

        setMessages(prev => [...prev, fallbackMessage]);

        // Update context if personalization data is provided
        if (data.personalization) {
          setContext(prev => ({
            ...prev,
            personalization_score: data.personalization.score,
            recommendations: data.personalization.recommendations
          }));
        }
      }
    } catch (error: any) {
      console.error('Chat error:', error);

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
    setTimeout(() => sendMessage(), 100);
  };

  const provideFeedback = async (messageId: string, feedback: 'positive' | 'negative') => {
    try {
      // Update message with feedback
      setMessages(prev => prev.map(msg =>
        msg.id === messageId ? { ...msg, feedback } : msg
      ));

      // Send feedback to backend (no /api prefix needed)
      await apiClient.post('/assistant/feedback/', {
        message_id: messageId,
        feedback: feedback
      }).catch(() => {
        // Fallback to neural assistant feedback if available
        console.log('Feedback recorded locally');
      });

      toast.success(
        feedback === 'positive'
          ? 'Thanks for the feedback! I\'ll keep learning.'
          : 'I\'ll try to improve. Thanks for the feedback!'
      );
    } catch (error) {
      console.error('Failed to provide feedback:', error);
    }
  };

  const toggleListening = () => {
    if (!speechSupported || !recognitionRef.current) {
      toast.error('Speech recognition not supported in your browser');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
      toast.success('Listening... Speak now');
    }
  };

  const resetAssistant = async () => {
    if (!confirm('This will reset our conversation and learning history. Are you sure?')) return;

    try {
      await apiClient.post('/assistant/reset/').catch(() => null);
      setMessages([]);
      setContext(null);
      setSessionId(null);
      initializeAssistant();
      toast.success('Assistant reset successfully');
    } catch (error) {
      toast.error('Failed to reset assistant');
    }
  };

  const getPersonalizationColor = (score: number): string => {
    if (score < 0.3) return 'text-gray-400';
    if (score < 0.6) return 'text-yellow-400';
    if (score < 0.9) return 'text-blue-400';
    return 'text-green-400';
  };

  const getConfidenceIndicator = (confidence?: number): string => {
    if (!confidence) return '';
    if (confidence > 0.8) return '🟢';
    if (confidence > 0.5) return '🟡';
    return '🔴';
  };

  // Render closed state (floating button)
  if (!isOpen) {
    return (
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-xl z-50 hover:shadow-2xl transition-shadow ${className}`}
      >
        <MessageCircle className="w-7 h-7 text-white" />
        {context && context.personalization_score > 0 && (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            className="absolute -top-1 -right-1"
          >
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          </motion.div>
        )}
      </motion.button>
    );
  }

  // Render minimized state
  if (isMinimized) {
    return (
      <motion.div
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className="fixed bottom-4 right-4 bg-gray-800 rounded-xl p-4 shadow-xl z-50 flex items-center gap-3 border border-gray-700"
      >
        <div className="relative">
          <Bot className="w-6 h-6 text-purple-400" />
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-0"
          >
            <Sparkles className="w-6 h-6 text-yellow-300 opacity-30" />
          </motion.div>
        </div>
        <div>
          <span className="text-white font-medium">AI Assistant</span>
          {context && (
            <div className="text-xs text-gray-400">
              Learning: {context.personalization_score ? (context.personalization_score * 100).toFixed(0) : '0'}%
            </div>
          )}
        </div>
        <button
          onClick={() => setIsMinimized(false)}
          className="text-gray-400 hover:text-white"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-400 hover:text-white"
        >
          <X className="w-4 h-4" />
        </button>
      </motion.div>
    );
  }

  // Render full chat interface
  return (
    <motion.div
      initial={{ opacity: 0, y: 100 }}
      animate={{ opacity: 1, y: 0 }}
      className={`fixed bottom-4 right-4 w-[480px] h-[720px] bg-gray-900 rounded-xl shadow-2xl z-50 flex flex-col border border-gray-700 ${className}`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4 rounded-t-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Bot className="w-6 h-6 text-white" />
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0"
              >
                <Sparkles className="w-6 h-6 text-yellow-300 opacity-50" />
              </motion.div>
            </div>
            <div>
              <h3 className="text-white font-semibold flex items-center gap-2">
                Unified AI Assistant
                <Zap className="w-4 h-4 text-yellow-300" />
              </h3>
              {context && (
                <div className="flex items-center gap-2 text-xs">
                  <Brain className={`w-3 h-3 ${getPersonalizationColor(context.personalization_score || 0)}`} />
                  <span className="text-white/80">
                    Learning: {context.personalization_score ? (context.personalization_score * 100).toFixed(0) : '0'}%
                  </span>
                  {context.page_context?.page && (
                    <>
                      <span className="text-white/60">•</span>
                      <span className="text-white/80">{context.page_context.page}</span>
                    </>
                  )}
                  {context.system_status && (
                    <>
                      <span className="text-white/60">•</span>
                      <span className="text-white/70 text-xs">{context.system_status}</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {speechSupported && (
              <button
                onClick={toggleListening}
                className={`${isListening ? 'text-red-400' : 'text-white/80'} hover:text-white`}
                title={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>
            )}
            <button
              onClick={resetAssistant}
              className="text-white/80 hover:text-white"
              title="Reset Learning"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsMinimized(true)}
              className="text-white/80 hover:text-white"
            >
              <Minimize2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/80 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Recommendations/Tips Bar */}
      {context && context.recommendations && context.recommendations.length > 0 && (
        <div className="bg-purple-600/10 border-b border-gray-700 p-2">
          <div className="flex items-center gap-2 text-xs">
            <Lightbulb className="w-3 h-3 text-yellow-400" />
            <span className="text-gray-400">Tip:</span>
            <span className="text-white/80 truncate">{context.recommendations[0]?.description}</span>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/50">
        {/* Welcome message when no messages */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="bg-gray-800/50 rounded-xl p-6 max-w-sm">
              <Bot className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-white font-semibold mb-2">
                Welcome to your AI Assistant!
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                I'm here to help you with income opportunities, career advice, learning, and more.
                {context?.first_name && ` Nice to meet you, ${context.first_name}!`}
              </p>
              {context?.skills?.top_skills && context.skills.top_skills.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-gray-500 mb-2">I see you have skills in:</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {context.skills.top_skills.slice(0, 3).map((skill, index) => (
                      <span key={index} className="px-2 py-1 bg-purple-600/20 text-purple-300 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div className="mt-4 space-y-2">
                <button
                  onClick={() => setShowInterview(true)}
                  className="w-full px-3 py-2 bg-gradient-to-r from-purple-600/30 to-pink-600/30 text-purple-300 text-sm rounded-lg hover:from-purple-600/40 hover:to-pink-600/40 transition-colors border border-purple-500/30"
                >
                  🎙️ Start Personal Interview
                </button>
                <button
                  onClick={() => setInputMessage("What income opportunities are available for me?")}
                  className="w-full px-3 py-2 bg-purple-600/20 text-purple-300 text-sm rounded-lg hover:bg-purple-600/30 transition-colors"
                >
                  Find Income Opportunities
                </button>
                <button
                  onClick={() => setInputMessage("How can I improve my skills?")}
                  className="w-full px-3 py-2 bg-blue-600/20 text-blue-300 text-sm rounded-lg hover:bg-blue-600/30 transition-colors"
                >
                  Get Learning Advice
                </button>
              </div>
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map(message => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] ${message.sender === 'user' ? 'order-2' : 'order-1'}`}>
                <div
                  className={`rounded-xl p-4 shadow-lg ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white'
                      : 'bg-gray-800 text-white border border-gray-700'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.text || message.content}
                  </p>

                  {/* Confidence indicator */}
                  {message.sender === 'assistant' && message.confidence !== undefined && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-gray-400">
                      <span>{getConfidenceIndicator(message.confidence)}</span>
                      <span>Confidence: {(message.confidence * 100).toFixed(0)}%</span>
                    </div>
                  )}
                </div>

                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && showSuggestions && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="text-xs px-3 py-1 bg-gray-800 text-gray-300 rounded-full hover:bg-gray-700 hover:text-white border border-gray-700 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}

                {/* Feedback buttons */}
                {message.sender === 'assistant' && message.id !== 'welcome' && !message.feedback && (
                  <div className="mt-2 flex items-center gap-2">
                    <button
                      onClick={() => provideFeedback(message.id, 'positive')}
                      className="text-gray-500 hover:text-green-400 transition-colors"
                    >
                      <ThumbsUp className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => provideFeedback(message.id, 'negative')}
                      className="text-gray-500 hover:text-red-400 transition-colors"
                    >
                      <ThumbsDown className="w-3 h-3" />
                    </button>
                  </div>
                )}

                {/* Show feedback if provided */}
                {message.feedback && (
                  <div className="mt-1 text-xs text-gray-400">
                    {message.feedback === 'positive' ? '✅ Thanks!' : '📝 Noted'}
                  </div>
                )}
              </div>

              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                message.sender === 'user'
                  ? 'bg-purple-600 order-1 mr-2'
                  : 'bg-gray-800 border border-gray-700 order-2 ml-2'
              }`}>
                {message.sender === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-purple-400" />
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 text-gray-400"
          >
            <Bot className="w-4 h-4" />
            <div className="flex gap-1">
              <motion.div
                animate={{ y: [0, -5, 0] }}
                transition={{ duration: 0.5, repeat: Infinity, delay: 0 }}
                className="w-2 h-2 bg-gray-400 rounded-full"
              />
              <motion.div
                animate={{ y: [0, -5, 0] }}
                transition={{ duration: 0.5, repeat: Infinity, delay: 0.1 }}
                className="w-2 h-2 bg-gray-400 rounded-full"
              />
              <motion.div
                animate={{ y: [0, -5, 0] }}
                transition={{ duration: 0.5, repeat: Infinity, delay: 0.2 }}
                className="w-2 h-2 bg-gray-400 rounded-full"
              />
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-700 bg-gray-800/50">
        {/* Quick actions */}
        {showSuggestions && context?.skills?.top_skills && (
          <div className="mb-3 flex flex-wrap gap-2">
            {context.skills.top_skills.slice(0, 3).map((skill, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(`Tell me about opportunities in ${skill}`)}
                className="px-3 py-1 bg-purple-600/20 text-purple-300 text-xs rounded-full hover:bg-purple-600/30 transition-colors"
              >
                {skill}
              </button>
            ))}
          </div>
        )}

        <div className="flex items-end gap-3">
          <div className="flex-1">
            <textarea
              ref={inputRef as any}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder={isListening ? "🎤 Listening..." : "Ask me anything... (Shift+Enter for new line)"}
              className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 resize-none transition-all"
              rows={inputMessage.split('\n').length || 1}
              maxLength={1000}
              disabled={isListening}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isTyping}
            className="w-12 h-12 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors shadow-lg"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        {/* Status indicators */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <div className="flex items-center gap-2">
            {isListening && (
              <span className="flex items-center gap-1 text-red-400">
                <Activity className="w-3 h-3 animate-pulse" />
                Listening...
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {sessionId && <span>Session active</span>}
            {context?.personalization_score && context.personalization_score > 0 && (
              <span className={getPersonalizationColor(context.personalization_score)}>
                {Math.round(context.personalization_score * 100)}% personalized
              </span>
            )}
            {(!context?.personalization_score || context.personalization_score === 0) && (
              <span className="text-gray-400">
                Getting to know you...
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Personal Assistant Interview Modal */}
      <PersonalAssistantInterview
        isOpen={showInterview}
        onClose={() => setShowInterview(false)}
        onComplete={async (profile) => {
          console.log('Interview completed with profile:', profile);

          try {
            // Save profile to backend
            const response = await apiClient.put('/api/profile/extended/', profile);

            if (response.data.success) {
              toast.success('Profile setup complete! Your personal AI is now ready.');

              setContext(prev => ({
                ...prev,
                personalization_score: 0.8,
                first_name: profile.name || prev?.first_name,
                skills: { top_skills: profile.skills || [] }
              }));

              // Add welcome message with profile
              const welcomeMessage: Message = {
                id: `profile-complete-${Date.now()}`,
                text: `Great! I've saved your profile, ${profile.name}. Based on your ${profile.experience_level} experience and ${profile.income_goal} income goal, I'm ready to help you find opportunities in ${profile.work_preferences?.join(', ') || 'various areas'}. What would you like to work on first?`,
                sender: 'assistant',
                timestamp: new Date(),
                suggestions: ['Find job opportunities', 'Improve my skills', 'Build my portfolio', 'Network and connect'],
                confidence: 0.9
              };

              setMessages(prev => [...prev, welcomeMessage]);
            } else {
              throw new Error(response.data.error || 'Failed to save profile');
            }
          } catch (error) {
            console.error('Failed to save profile:', error);
            toast.error('Profile interview completed, but failed to save. You can retry saving later.');

            // Still update local context even if save failed
            setContext(prev => ({
              ...prev,
              personalization_score: 0.7,
              first_name: profile.name || prev?.first_name,
              skills: { top_skills: profile.skills || [] }
            }));

            // Add message with warning
            const welcomeMessage: Message = {
              id: `profile-complete-${Date.now()}`,
              text: `I've completed your interview, ${profile.name}! However, there was an issue saving your profile to the server. Your preferences are saved locally for now. Based on your ${profile.experience_level} experience and ${profile.income_goal} income goal, I'm ready to help you find opportunities. What would you like to work on first?`,
              sender: 'assistant',
              timestamp: new Date(),
              suggestions: ['Find job opportunities', 'Improve my skills', 'Build my portfolio', 'Retry profile save'],
              confidence: 0.8
            };

            setMessages(prev => [...prev, welcomeMessage]);
          }

          setShowInterview(false);
        }}
      />
    </motion.div>
  );
};