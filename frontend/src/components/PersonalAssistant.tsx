import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageCircle, Send, Bot, User, ThumbsUp, ThumbsDown,
  Brain, Sparkles, TrendingUp, RefreshCw, X, Minimize2,
  Maximize2, HelpCircle, Target, Lightbulb
} from 'lucide-react';
import { apiClient } from '../services/api.config';
import { toast } from 'sonner';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  confidence?: number;
  suggestions?: string[];
  actions?: string[];
  metadata?: any;
}

interface AssistantContext {
  personalization_score: number;
  confidence_level: number;
  recommendations: Array<{
    type: string;
    priority: string;
    title: string;
    description: string;
  }>;
}

export const PersonalAssistant: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [context, setContext] = useState<AssistantContext | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadContext();
      addWelcomeMessage();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadContext = async () => {
    try {
      const response = await apiClient.get('/api/assistant/dev/context/');
      setContext(response.data.context);
    } catch (error) {
      console.error('Failed to load assistant context:', error);
    }
  };

  const addWelcomeMessage = () => {
    const welcomeMessage: Message = {
      id: 'welcome',
      text: "Hi! I'm your personal AI assistant. I learn from our interactions to provide better help over time. How can I assist you today?",
      sender: 'assistant',
      timestamp: new Date(),
      confidence: 1,
      suggestions: ['Find job opportunities', 'Update my profile', 'View career insights', 'Get salary recommendations']
    };
    setMessages([welcomeMessage]);
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
      const response = await apiClient.post('/api/assistant/dev/chat/', {
        message: inputMessage,
        context: { timestamp: new Date().toISOString() }
      });

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        text: response.data.data.response,
        sender: 'assistant',
        timestamp: new Date(),
        confidence: response.data.data.confidence,
        suggestions: response.data.data.suggestions,
        actions: response.data.data.actions,
        metadata: response.data.data.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update context if personalization data is provided
      if (response.data.data.personalization) {
        setContext(prev => ({
          ...prev,
          personalization_score: response.data.data.personalization.score,
          recommendations: response.data.data.personalization.recommendations
        }));
      }
    } catch (error) {
      toast.error('Failed to send message');
      console.error('Chat error:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
    sendMessage();
  };

  const provideFeedback = async (messageId: string, feedback: 'positive' | 'negative') => {
    try {
      await apiClient.post('/api/assistant/dev/feedback/', {
        message_id: messageId,
        feedback: feedback
      });
      toast.success(`Feedback recorded. I'll learn from this!`);
    } catch (error) {
      console.error('Failed to provide feedback:', error);
    }
  };

  const resetAssistant = async () => {
    if (!confirm('This will reset all learned patterns. Are you sure?')) return;

    try {
      await apiClient.post('/api/assistant/dev/reset/');
      setMessages([]);
      setContext(null);
      addWelcomeMessage();
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

  if (!isOpen) {
    return (
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-lg z-50"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </motion.button>
    );
  }

  if (isMinimized) {
    return (
      <motion.div
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className="fixed bottom-6 right-6 bg-gray-800 rounded-lg p-3 shadow-xl z-50 flex items-center gap-3"
      >
        <Bot className="w-5 h-5 text-purple-400" />
        <span className="text-white font-medium">AI Assistant</span>
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 100 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 right-6 w-96 h-[600px] bg-gray-900 rounded-xl shadow-2xl z-50 flex flex-col border border-gray-700"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4 rounded-t-xl flex items-center justify-between">
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
            <h3 className="text-white font-semibold">Personal AI Assistant</h3>
            {context && (
              <div className="flex items-center gap-2 text-xs">
                <Brain className={`w-3 h-3 ${getPersonalizationColor(context.personalization_score)}`} />
                <span className="text-white/80">
                  Learning: {(context.personalization_score * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
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

      {/* Recommendations Bar */}
      {context && context.recommendations && context.recommendations.length > 0 && (
        <div className="bg-purple-600/10 border-b border-gray-700 p-2">
          <div className="flex items-center gap-2 text-xs">
            <Lightbulb className="w-3 h-3 text-yellow-400" />
            <span className="text-gray-400">Tip:</span>
            <span className="text-white/80">{context.recommendations[0]?.description}</span>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map(message => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] ${message.sender === 'user' ? 'order-2' : 'order-1'}`}>
                <div
                  className={`rounded-lg p-3 ${
                    message.sender === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-800 text-white border border-gray-700'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>

                  {/* Confidence indicator for assistant messages */}
                  {message.sender === 'assistant' && message.confidence !== undefined && (
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-green-400 opacity-${Math.round(message.confidence * 100)}" />
                        <span className="text-xs text-gray-400">
                          Confidence: {(message.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
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
                        className="text-xs px-3 py-1 bg-gray-800 text-gray-300 rounded-full hover:bg-gray-700 hover:text-white border border-gray-700"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}

                {/* Feedback buttons for assistant messages */}
                {message.sender === 'assistant' && message.id !== 'welcome' && (
                  <div className="mt-2 flex items-center gap-2">
                    <button
                      onClick={() => provideFeedback(message.id, 'positive')}
                      className="text-gray-500 hover:text-green-400"
                    >
                      <ThumbsUp className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => provideFeedback(message.id, 'negative')}
                      className="text-gray-500 hover:text-red-400"
                    >
                      <ThumbsDown className="w-3 h-3" />
                    </button>
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

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything..."
            className="flex-1 px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isTyping}
            className="w-10 h-10 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};