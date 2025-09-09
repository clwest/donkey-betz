import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  ChatBubbleLeftRightIcon, 
  XMarkIcon, 
  PaperAirplaneIcon,
  ChevronDownIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { useAuthStore } from '../../store/authStore';
import { assistantService } from '../../services/assistant.service';
import clsx from 'clsx';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface PageContext {
  page: string;
  message: string;
  icon?: React.ReactNode;
}

export function ChatWidget() {
  const { user } = useAuthStore();
  const location = useLocation();
  
  // Fallback user for development if auth store doesn't have one
  const currentUser = user || { 
    id: '1', 
    username: 'testuser', 
    email: 'test@example.com' 
  };
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pageContext, setPageContext] = useState<PageContext | null>(null);
  const [userStats, setUserStats] = useState<any>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Get page context based on current route
  useEffect(() => {
    const path = location.pathname;
    let context: PageContext | null = null;

    if (path.includes('/studio')) {
      context = {
        page: 'Studio',
        message: "I see you're in the Studio! I can help you generate images, write blogs, or create social content. What would you like to create today?",
        icon: <SparklesIcon className="h-5 w-5" />
      };
    } else if (path.includes('/gallery')) {
      context = {
        page: 'Gallery',
        message: "Welcome to your Gallery! Need help organizing or finding something specific?"
      };
    } else if (path.includes('/campaigns')) {
      context = {
        page: 'Campaigns',
        message: "Managing your campaigns? I can help you create compelling content, analyze performance, or suggest optimizations."
      };
    } else if (path.includes('/ebooks')) {
      context = {
        page: 'eBooks',
        message: "Writing an eBook? I can help with outlines, chapter ideas, or content generation. What's your book about?"
      };
    } else if (path.includes('/voice')) {
      context = {
        page: 'Voice Studio',
        message: "In the Voice Studio! I can help transcribe your recordings or turn them into polished content."
      };
    } else if (path.includes('/dashboard')) {
      context = {
        page: 'Dashboard',
        message: `Welcome back${currentUser?.username ? `, ${currentUser.username}` : ''}! How can I assist you today?`
      };
    }

    setPageContext(context);
  }, [location.pathname]); // Only depend on pathname, not on changing stats

  // Load user context when widget opens
  useEffect(() => {
    if (isOpen && currentUser) {
      loadUserContext();
    }
  }, [isOpen]); // Only trigger when isOpen changes

  // Add contextual greeting when page context is set
  useEffect(() => {
    if (isOpen && messages.length === 0 && pageContext) {
      // Add contextual greeting
      const contextMessage: Message = {
        id: `context-${Date.now()}`,
        role: 'assistant',
        content: pageContext.message,
        timestamp: new Date().toISOString()
      };
      setMessages([contextMessage]);
    }
  }, [isOpen, pageContext?.page]); // Only trigger on page change, not content changes

  // Auto-scroll to bottom
  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      inputRef.current?.focus();
    }
  }, [messages, isOpen, isMinimized]);

  const loadUserContext = async () => {
    try {
      const response = await assistantService.getContext();
      if (response?.stats) {
        setUserStats({
          total_images: response.stats.total_images,
          total_blogs: response.stats.total_blogs,
          total_content: response.stats.total_images + response.stats.total_blogs + response.stats.total_social,
          favorite_styles: response.stats.favorite_styles,
          recent_topics: response.stats.recent_topics
        });
      }
    } catch (error) {
      console.error('Failed to load context:', error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || loading || !currentUser) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      // Add page context to message
      const contextualMessage = pageContext 
        ? `[User is on ${pageContext.page} page] ${userMessage.content}`
        : userMessage.content;

      console.log('Sending message with sessionId:', sessionId, 'type:', typeof sessionId);
      
      const response = await assistantService.sendMessage(
        contextualMessage,
        sessionId || undefined
      );

      console.log('Received response:', response);

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message || response.error || 'No response received',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.session_id) {
        console.log('Setting sessionId to:', response.session_id, 'type:', typeof response.session_id);
        // Ensure session_id is stored as a string
        setSessionId(String(response.session_id));
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: "I'm having trouble connecting. Please try again in a moment.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  // Always render the widget in development
  // if (!currentUser) return null;

  return (
    <>
      {/* Floating button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={clsx(
            "fixed bottom-6 right-6 p-4",
            "bg-gradient-to-br from-emerald-500 to-teal-600",
            "text-white rounded-full shadow-2xl",
            "hover:shadow-emerald-500/25 hover:scale-110",
            "transition-all duration-300 z-50 group"
          )}
          aria-label="Open AI Assistant"
        >
          <ChatBubbleLeftRightIcon className="h-6 w-6" />
          {/* Pulse indicator for context awareness */}
          {pageContext && (
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-emerald-400 rounded-full animate-pulse" />
          )}
          {/* Tooltip */}
          <span className={clsx(
            "absolute bottom-full right-0 mb-2 px-3 py-1",
            "bg-dark-800 text-white text-sm rounded-lg",
            "opacity-0 group-hover:opacity-100 transition-opacity",
            "whitespace-nowrap pointer-events-none"
          )}>
            AI Assistant {pageContext && `• ${pageContext.page} Help`}
          </span>
        </button>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className={clsx(
          "fixed bottom-6 right-6 z-50",
          "animate-in fade-in slide-in-from-bottom-5 duration-300"
        )}>
          <div className={clsx(
            "glass rounded-2xl shadow-2xl",
            isMinimized ? "w-80" : "w-96 h-[600px]",
            "flex flex-col overflow-hidden"
          )}>
            {/* Header */}
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="h-10 w-10 bg-white/20 rounded-full flex items-center justify-center">
                      <SparklesIcon className="h-6 w-6 text-white" />
                    </div>
                    <span className="absolute bottom-0 right-0 h-3 w-3 bg-green-400 rounded-full border-2 border-emerald-600" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">AI Assistant</h3>
                    <p className="text-emerald-100 text-xs">
                      {pageContext ? `Helping with ${pageContext.page}` : 'Always here to help'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setIsMinimized(!isMinimized)}
                    className="text-white/80 hover:text-white transition-colors p-1"
                  >
                    <ChevronDownIcon className={clsx(
                      "h-5 w-5 transition-transform",
                      isMinimized && "rotate-180"
                    )} />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-white/80 hover:text-white transition-colors p-1"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Chat content (hidden when minimized) */}
            {!isMinimized && (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 && (
                    <div className="text-center py-8">
                      <SparklesIcon className="h-12 w-12 text-emerald-500/30 mx-auto mb-4" />
                      <p className="text-gray-400 mb-2">
                        Hi {currentUser.username}! 👋
                      </p>
                      <p className="text-gray-500 text-sm">
                        I'm your AI assistant. Ask me anything about content creation!
                      </p>
                      {userStats?.favorite_styles?.length > 0 && (
                        <p className="text-emerald-500 text-xs mt-4">
                          I noticed you like {userStats.favorite_styles[0]} style images
                        </p>
                      )}
                    </div>
                  )}
                  
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={clsx(
                        'flex',
                        msg.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      <div
                        className={clsx(
                          'max-w-[85%] rounded-2xl px-4 py-2.5',
                          msg.role === 'user'
                            ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white'
                            : 'glass-dark text-gray-100'
                        )}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        <p className={clsx(
                          "text-xs mt-1 opacity-70",
                          msg.role === 'user' ? 'text-emerald-100' : 'text-gray-400'
                        )}>
                          {formatTime(msg.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {loading && (
                    <div className="flex justify-start">
                      <div className="glass-dark px-4 py-3 rounded-2xl">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <form onSubmit={handleSendMessage} className="p-4 border-t border-white/10">
                  <div className="flex space-x-2">
                    <input
                      ref={inputRef}
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Ask me anything..."
                      disabled={loading}
                      className={clsx(
                        "flex-1 bg-dark-800/50 text-white",
                        "px-4 py-2.5 rounded-xl",
                        "border border-white/10 focus:border-emerald-500",
                        "focus:outline-none placeholder-gray-500",
                        "transition-colors"
                      )}
                    />
                    <button
                      type="submit"
                      disabled={loading || !message.trim()}
                      className={clsx(
                        "p-2.5 rounded-xl",
                        "bg-gradient-to-r from-emerald-500 to-teal-600",
                        "text-white hover:shadow-lg hover:shadow-emerald-500/25",
                        "disabled:opacity-50 disabled:cursor-not-allowed",
                        "transition-all duration-200 hover:scale-105"
                      )}
                    >
                      <PaperAirplaneIcon className="h-5 w-5" />
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 text-center">
                    Powered by GPT-4 • {pageContext?.page || 'AI Content Studio'}
                  </p>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}