import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  ChatBubbleLeftRightIcon, 
  XMarkIcon, 
  PaperAirplaneIcon,
  ChevronDownIcon,
  SparklesIcon,
  MicrophoneIcon,
  StopIcon
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
  
  // Use chris as fallback for development if auth store doesn't have a user
  const currentUser = user || { 
    id: '2', 
    username: 'chris', 
    email: 'chris@example.com',
    credits: 10000,
    subscription: 'premium'
  };
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pageContext, setPageContext] = useState<PageContext | null>(null);
  const [userStats, setUserStats] = useState<any>(null);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Check for speech recognition support
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
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }
        
        if (finalTranscript) {
          setMessage(prev => prev + finalTranscript);
        } else if (interimTranscript) {
          // Show interim results (optional)
          const currentBase = message.substring(0, message.lastIndexOf(' ') + 1);
          setMessage(currentBase + interimTranscript);
        }
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'no-speech') {
          // Restart recognition if no speech detected
          setTimeout(() => startListening(), 100);
        }
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

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
    // Only load context if user is authenticated
    const token = localStorage.getItem('authToken');
    if (!token) {
      console.log('No auth token, skipping context load');
      return;
    }
    
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
      // Silently fail for 401 errors - user just isn't logged in
      if (error?.response?.status === 401) {
        console.log('User not authenticated, skipping context');
      } else {
        console.error('Failed to load context:', error);
      }
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || loading) return;
    
    // Check if user is authenticated
    const token = localStorage.getItem('authToken');
    if (!token && !currentUser) {
      const loginMessage: Message = {
        id: `login-${Date.now()}`,
        role: 'assistant',
        content: "Please log in to use the AI assistant. You can use the test credentials: username 'testuser', password 'testpass123' or 'demo'/'demo123'.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, loginMessage]);
      return;
    }

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

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (error) {
        console.error('Failed to start speech recognition:', error);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
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
            "fixed bottom-6 right-6 p-5",
            "bg-gradient-to-br from-purple-600 to-purple-800",
            "text-white rounded-full shadow-2xl",
            "hover:shadow-purple-500/30 hover:scale-110",
            "transition-all duration-300 z-50 group",
            "ring-2 ring-purple-500/20"
          )}
          aria-label="Open AI Assistant"
        >
          <ChatBubbleLeftRightIcon className="h-7 w-7" />
          {/* Pulse indicator for context awareness */}
          {pageContext && (
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-purple-400 rounded-full animate-pulse" />
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
          "fixed bottom-4 right-4 z-50",
          "animate-in fade-in slide-in-from-bottom-5 duration-300"
        )}>
          <div className={clsx(
            "glass rounded-2xl shadow-2xl",
            "shadow-purple-500/20",
            isMinimized ? "w-96" : "w-[520px] h-[720px]",
            "flex flex-col overflow-hidden",
            "border border-purple-500/20"
          )}>
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-800 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="h-10 w-10 bg-white/20 rounded-full flex items-center justify-center">
                      <SparklesIcon className="h-6 w-6 text-white" />
                    </div>
                    <span className="absolute bottom-0 right-0 h-3 w-3 bg-purple-400 rounded-full border-2 border-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-lg">AI Assistant</h3>
                    <p className="text-purple-100 text-sm opacity-90">
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
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                  {messages.length === 0 && (
                    <div className="text-center py-12">
                      <SparklesIcon className="h-12 w-12 text-purple-500/30 mx-auto mb-4" />
                      <p className="text-gray-300 mb-2 text-lg font-medium">
                        Hi {currentUser.username}! 👋
                      </p>
                      <p className="text-gray-400 text-base">
                        I'm your AI assistant. Ask me anything about content creation!
                      </p>
                      {userStats?.favorite_styles?.length > 0 && (
                        <p className="text-purple-500 text-sm mt-4">
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
                          'max-w-[85%] rounded-2xl px-5 py-3',
                          msg.role === 'user'
                            ? 'bg-gradient-to-br from-purple-600 to-purple-700 text-white'
                            : 'glass-dark text-gray-100'
                        )}
                      >
                        <p className="text-base whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                        <p className={clsx(
                          "text-xs mt-1 opacity-70",
                          msg.role === 'user' ? 'text-purple-100' : 'text-gray-400'
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
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <form onSubmit={handleSendMessage} className="p-5 border-t border-white/10 bg-dark-900/50">
                  <div className="flex space-x-2">
                    <input
                      ref={inputRef}
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder={isListening ? "Listening..." : "Type or speak your message..."}
                      disabled={loading}
                      className={clsx(
                        "flex-1 bg-dark-800/50 text-white text-base",
                        "px-5 py-3 rounded-xl",
                        "border border-white/10 focus:border-purple-500",
                        "focus:outline-none placeholder-gray-500",
                        "transition-colors",
                        isListening && "border-red-500 animate-pulse"
                      )}
                    />
                    {speechSupported && (
                      <button
                        type="button"
                        onClick={toggleListening}
                        disabled={loading}
                        className={clsx(
                          "px-4 py-3 rounded-xl",
                          isListening 
                            ? "bg-red-500 hover:bg-red-600 animate-pulse"
                            : "bg-dark-700 hover:bg-dark-600",
                          "text-white",
                          "disabled:opacity-50 disabled:cursor-not-allowed",
                          "transition-all duration-200",
                          "flex items-center justify-center"
                        )}
                        title={isListening ? "Stop recording" : "Start voice input"}
                      >
                        {isListening ? (
                          <StopIcon className="h-5 w-5" />
                        ) : (
                          <MicrophoneIcon className="h-5 w-5" />
                        )}
                      </button>
                    )}
                    <button
                      type="submit"
                      disabled={loading || !message.trim()}
                      className={clsx(
                        "px-4 py-3 rounded-xl",
                        "bg-gradient-to-r from-purple-600 to-purple-700",
                        "text-white hover:shadow-lg hover:shadow-purple-500/25",
                        "disabled:opacity-50 disabled:cursor-not-allowed",
                        "transition-all duration-200 hover:scale-105",
                        "flex items-center justify-center"
                      )}
                    >
                      <PaperAirplaneIcon className="h-5 w-5" />
                    </button>
                  </div>
                  <p className="text-xs text-gray-400 mt-2 text-center">
                    Powered by GPT-5 • {pageContext?.page || 'AI Content Studio'}
                    {speechSupported && ' • 🎤 Voice input enabled'}
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