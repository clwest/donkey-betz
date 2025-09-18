import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageCircle, Send, Bot, User, ThumbsUp, ThumbsDown,
  Brain, Sparkles, TrendingUp, RefreshCw, X, Minimize2,
  Maximize2, HelpCircle, Target, Lightbulb, CheckCircle2
} from 'lucide-react';
import { apiClient } from '../services/api.config';
import { toast } from 'sonner';
import { unifiedConnector } from '../services/UnifiedPlatformConnector';

// Global reference to interview WebSocket
let interviewSocket: WebSocket | null = null;

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

interface InterviewQuestion {
  id: string;
  phase: string;
  text: string;
  input_type: 'text' | 'multiple_choice' | 'multi_select' | 'scale' | 'yes_no';
  options?: string[];
  required: boolean;
  progress: number;
}

interface InterviewState {
  active: boolean;
  phase: string;
  completion_percentage: number;
  interview_type?: 'quick' | 'full';
  current_question?: InterviewQuestion;
  can_resume?: boolean;
  can_restart?: boolean;
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

interface PersonalAssistantProps {
  initialMessage?: string;
  context?: any;
  onSuggestion?: (field: string, value: any) => void;
  embedded?: boolean;
}

export const PersonalAssistant: React.FC<PersonalAssistantProps> = ({
  initialMessage,
  context: externalContext,
  onSuggestion,
  embedded = false
}) => {
  const [isOpen, setIsOpen] = useState(embedded ? true : false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [context, setContext] = useState<AssistantContext | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isConnectedToPlatform, setIsConnectedToPlatform] = useState(false);
  const [platformData, setPlatformData] = useState<any>(null);
  const [interviewMode, setInterviewMode] = useState(false);
  const [interviewState, setInterviewState] = useState<InterviewState>({
    active: false,
    phase: '',
    completion_percentage: 0
  });
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [interviewResponse, setInterviewResponse] = useState('');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [showIntroduction, setShowIntroduction] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if ((isOpen || embedded) && messages.length === 0) {
      if (!embedded) loadContext();
      connectToPlatform();

      // Check if this is first visit (no localStorage flag)
      const hasSeenIntro = localStorage.getItem('hasSeenAssistantIntro');
      if (!hasSeenIntro && !embedded) {
        setShowIntroduction(true);
        localStorage.setItem('hasSeenAssistantIntro', 'true');
      }

      // Check for interview mode first
      if (shouldStartInterview()) {
        connectToInterviewSystem();
      } else {
        addWelcomeMessage();
      }
    }
  }, [isOpen, embedded]);

  const shouldStartInterview = () => {
    // Check if we should start interview mode based on context or user state
    return externalContext && !externalContext.interview_completed;
  };

  const connectToInterviewSystem = async () => {
    try {
      // Connect to interview WebSocket
      const isDev = import.meta.env.MODE !== 'production';
      const wsUrl = isDev ? 'ws://localhost:8000/ws/interview/' :
        (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host + '/ws/interview/';

      const interviewSocket = new WebSocket(wsUrl);

      interviewSocket.onopen = () => {
        console.log('Connected to interview system');
        setInterviewMode(true);
      };

      interviewSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleInterviewMessage(data);
      };

      interviewSocket.onerror = (error) => {
        console.error('Interview WebSocket error:', error);
        // Fallback to regular assistant mode
        addWelcomeMessage();
      };

    } catch (error) {
      console.error('Failed to connect to interview system:', error);
      addWelcomeMessage();
    }
  };

  const handleInterviewMessage = (data: any) => {
    switch (data.type) {
      case 'connection':
        // Connected to interview system
        break;

      case 'interview_options':
        // Show interview start options
        const optionsMessage: Message = {
          id: 'interview_options',
          text: data.message,
          sender: 'assistant',
          timestamp: new Date(),
          suggestions: data.options.map((opt: any) => opt.title)
        };
        setMessages([optionsMessage]);
        break;

      case 'interview_started':
        setInterviewState({
          active: true,
          phase: 'started',
          completion_percentage: 0,
          interview_type: data.interview_type
        });
        setCurrentQuestion(data.question);

        const startMessage: Message = {
          id: 'interview_started',
          text: `Great! Starting your ${data.interview_type} interview (${data.estimated_time}). Let's begin!`,
          sender: 'assistant',
          timestamp: new Date()
        };
        setMessages([startMessage]);
        showCurrentQuestion(data.question);
        break;

      case 'next_question':
        setCurrentQuestion(data.question);
        setInterviewState(prev => ({
          ...prev,
          completion_percentage: data.question.progress
        }));
        showCurrentQuestion(data.question);
        break;

      case 'interview_completed':
        setInterviewState({
          active: false,
          phase: 'completed',
          completion_percentage: 100
        });
        setCurrentQuestion(null);

        const completionMessage: Message = {
          id: 'interview_completed',
          text: data.message,
          sender: 'assistant',
          timestamp: new Date(),
          suggestions: data.next_steps
        };
        setMessages(prev => [...prev, completionMessage]);
        setInterviewMode(false);
        break;

      case 'existing_interview':
        setInterviewState({
          active: false,
          phase: 'paused',
          completion_percentage: data.state.completion_percentage,
          can_resume: true
        });

        const resumeMessage: Message = {
          id: 'resume_option',
          text: data.message,
          sender: 'assistant',
          timestamp: new Date(),
          suggestions: ['Continue interview', 'Start over', 'Skip for now']
        };
        setMessages([resumeMessage]);
        break;

      case 'profile_exists':
        const profileMessage: Message = {
          id: 'profile_exists',
          text: data.message,
          sender: 'assistant',
          timestamp: new Date(),
          suggestions: ['Find opportunities', 'Update profile', 'Get recommendations']
        };
        setMessages([profileMessage]);
        setInterviewMode(false);
        break;
    }
  };

  const showCurrentQuestion = (question: InterviewQuestion) => {
    const questionMessage: Message = {
      id: question.id,
      text: question.text,
      sender: 'assistant',
      timestamp: new Date(),
      metadata: { question }
    };

    setMessages(prev => [...prev, questionMessage]);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadContext = async () => {
    try {
      const response = await apiClient.get('/assistant/dev/context/');
      setContext(response.data.context);
    } catch (error) {
      console.error('Failed to load assistant context:', error);
    }
  };

  const connectToPlatform = async () => {
    try {
      console.log('🔌 Personal Assistant connecting to Unified Platform...');

      const connected = await unifiedConnector.connect('personal_assistant');

      if (connected) {
        setIsConnectedToPlatform(true);

        // Set up platform message handlers
        unifiedConnector.connectPersonalAssistant((data) => {
          console.log('📨 Platform data received:', data);
          setPlatformData(data);

          // If Income Builder sends opportunities, show them to user
          if (data.top_opportunities && data.top_opportunities.length > 0) {
            const opportunityMessage: Message = {
              id: `platform-${Date.now()}`,
              text: `I found ${data.top_opportunities.length} income opportunities for you! Would you like me to help you explore them?`,
              sender: 'assistant',
              timestamp: new Date(),
              confidence: 0.95,
              suggestions: [
                'Show me the opportunities',
                'Analyze my best matches',
                'Create action plans',
                'Help me get started'
              ],
              metadata: { opportunities: data.top_opportunities }
            };
            setMessages(prev => [...prev, opportunityMessage]);
          }

          // Handle profile suggestions
          if (data.profile_suggestions) {
            const suggestionMessage: Message = {
              id: `suggestions-${Date.now()}`,
              text: data.message || 'I have some suggestions to improve your profile and increase your income potential.',
              sender: 'assistant',
              timestamp: new Date(),
              confidence: 0.9,
              suggestions: data.profile_suggestions,
              metadata: data
            };
            setMessages(prev => [...prev, suggestionMessage]);
          }
        });

        // Send current context to platform
        if (externalContext) {
          unifiedConnector.updateProfile(externalContext);
        }

        console.log('✅ Personal Assistant connected to platform');
      }
    } catch (error) {
      console.error('Failed to connect to platform:', error);
    }
  };

  const addWelcomeMessage = () => {
    const platformStatus = isConnectedToPlatform ? 'Connected to AI platform' : 'Connecting to AI platform...';

    const welcomeMessage: Message = {
      id: 'welcome',
      text: initialMessage || `Hi! I'm your personal AI assistant with real-time access to job opportunities and income streams. ${platformStatus}. Click the ❓ button above to learn more about what I can do, or just start chatting!`,
      sender: 'assistant',
      timestamp: new Date(),
      confidence: 1,
      suggestions: embedded && externalContext?.missingFields?.length > 0
        ? ['Help me with my professional summary', 'Add my work experience', 'List my skills', 'Complete my profile']
        : ['Find job opportunities', 'Find income streams', 'Start my interview', 'Get personalized recommendations', 'Learn what you can do']
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
      // First, try to handle via platform connector if connected
      if (isConnectedToPlatform && shouldUsePlatform(inputMessage)) {
        await handlePlatformMessage(inputMessage);
        return;
      }

      const response = await apiClient.post('/assistant/dev/chat/', {
        message: inputMessage,
        context: {
          timestamp: new Date().toISOString(),
          profile_context: externalContext, // Include profile context if available
          mode: embedded ? 'profile_builder' : 'general',
          platform_connected: isConnectedToPlatform,
          platform_data: platformData,
          conversation_history: messages.slice(-5).map(m => ({
            role: m.sender,
            content: m.text
          }))
        }
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

  const shouldUsePlatform = (message: string): boolean => {
    const platformKeywords = [
      'find opportunities', 'income streams', 'job search', 'opportunities',
      'analyze opportunities', 'get opportunities', 'find jobs', 'income',
      'revenue', 'money', 'earning', 'freelance', 'work'
    ];

    return platformKeywords.some(keyword =>
      message.toLowerCase().includes(keyword)
    );
  };

  const handlePlatformMessage = async (message: string) => {
    console.log('🎯 Handling platform message:', message);

    if (message.toLowerCase().includes('opportunities') || message.toLowerCase().includes('income')) {
      // Trigger opportunity analysis through platform
      unifiedConnector.send({
        type: 'analyze_opportunities',
        source: 'personal_assistant',
        data: {
          profile: externalContext,
          request: message
        }
      });

      const response: Message = {
        id: `platform-${Date.now()}`,
        text: "I'm analyzing real-time opportunities for you through our AI platform. This includes live job data, income streams, and personalized matches...",
        sender: 'assistant',
        timestamp: new Date(),
        confidence: 0.9
      };

      setMessages(prev => [...prev, response]);

    } else if (message.toLowerCase().includes('job search') || message.toLowerCase().includes('find jobs')) {
      // Trigger job search through spider network
      unifiedConnector.triggerJobSearch({
        skills: externalContext?.skills || [],
        location: externalContext?.location || 'remote',
        experience_level: externalContext?.experience_level || 'mid'
      });

      const response: Message = {
        id: `search-${Date.now()}`,
        text: "I'm activating our job spider network to find real opportunities across multiple platforms. This may take a few moments...",
        sender: 'assistant',
        timestamp: new Date(),
        confidence: 0.95,
        suggestions: ['Show me what you found', 'Filter by salary', 'Remote only']
      };

      setMessages(prev => [...prev, response]);
    }

    setIsTyping(false);
  };

  const handleSuggestionClick = (suggestion: string) => {
    // Handle special suggestion for learning about the assistant
    if (suggestion === 'Learn what you can do') {
      setShowIntroduction(true);
      return;
    }

    // Handle special suggestion for starting interview
    if (suggestion === 'Start my interview') {
      setShowIntroduction(false);
      if (!interviewMode && !externalContext?.interview_completed) {
        connectToInterviewSystem();
      }
      return;
    }

    if (interviewMode && currentQuestion) {
      handleInterviewSuggestion(suggestion);
    } else {
      setInputMessage(suggestion);
      sendMessage();
    }
  };

  const handleInterviewSuggestion = (suggestion: string) => {
    // Handle interview-specific suggestions
    if (suggestion.includes('Full Interview') || suggestion.includes('Quick Start')) {
      const quickStart = suggestion.includes('Quick Start');
      startInterview(quickStart);
    } else if (suggestion === 'Continue interview') {
      resumeInterview();
    } else if (suggestion === 'Start over') {
      restartInterview();
    } else if (suggestion === 'Skip for now') {
      setInterviewMode(false);
      addWelcomeMessage();
    } else {
      // Regular suggestion in interview mode
      submitInterviewResponse(suggestion);
    }
  };

  const startInterview = (quickStart: boolean = false) => {
    // Send start interview message to WebSocket
    if (interviewSocket && interviewSocket.readyState === WebSocket.OPEN) {
      interviewSocket.send(JSON.stringify({
        type: 'start_interview',
        quick_start: quickStart
      }));
    }
  };

  const resumeInterview = () => {
    if (interviewSocket && interviewSocket.readyState === WebSocket.OPEN) {
      interviewSocket.send(JSON.stringify({
        type: 'resume_interview'
      }));
    }
  };

  const restartInterview = (quickStart: boolean = false) => {
    if (interviewSocket && interviewSocket.readyState === WebSocket.OPEN) {
      interviewSocket.send(JSON.stringify({
        type: 'restart_interview',
        quick_start: quickStart
      }));
    }
  };

  const submitInterviewResponse = (response: string | string[]) => {
    if (interviewSocket && interviewSocket.readyState === WebSocket.OPEN) {
      interviewSocket.send(JSON.stringify({
        type: 'interview_response',
        response: response
      }));

      // Add user's response to messages
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        text: Array.isArray(response) ? response.join(', ') : response,
        sender: 'user',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);

      // Clear input
      setInterviewResponse('');
      setSelectedOptions([]);
    }
  };

  const handleInterviewSubmit = () => {
    if (!currentQuestion) return;

    let response: string | string[];

    if (currentQuestion.input_type === 'multi_select') {
      response = selectedOptions;
    } else {
      response = interviewResponse;
    }

    if ((Array.isArray(response) && response.length > 0) ||
        (typeof response === 'string' && response.trim())) {
      submitInterviewResponse(response);
    }
  };

  const handleOptionSelect = (option: string) => {
    if (currentQuestion?.input_type === 'multiple_choice') {
      setInterviewResponse(option);
    } else if (currentQuestion?.input_type === 'multi_select') {
      setSelectedOptions(prev =>
        prev.includes(option)
          ? prev.filter(o => o !== option)
          : [...prev, option]
      );
    }
  };

  const provideFeedback = async (messageId: string, feedback: 'positive' | 'negative') => {
    try {
      await apiClient.post('/assistant/dev/feedback/', {
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
      await apiClient.post('/assistant/dev/reset/');
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

  // Only show the floating button if not embedded and not open
  if (!embedded && !isOpen) {
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

  // Only show minimized state if not embedded
  if (!embedded && isMinimized) {
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
      initial={{ opacity: 0, y: embedded ? 0 : 100 }}
      animate={{ opacity: 1, y: 0 }}
      className={embedded
        ? "w-full h-full flex flex-col bg-gray-900"
        : "fixed bottom-6 right-6 w-96 h-[600px] bg-gray-900 rounded-xl shadow-2xl z-50 flex flex-col border border-gray-700"
      }
    >
      {/* Header - only show in non-embedded mode */}
      {!embedded && (
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
                {isConnectedToPlatform && (
                  <div className="flex items-center gap-1 text-xs">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-green-300">Platform Connected</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowIntroduction(true)}
            className="text-white/80 hover:text-white"
            title="Learn About Your AI Assistant"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
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
      )}

      {/* Introduction Modal */}
      {showIntroduction && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setShowIntroduction(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto border border-purple-500/30"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">Your Personal AI Assistant</h2>
                  <p className="text-purple-400">Powered by Neural Intelligence</p>
                </div>
              </div>
              <button
                onClick={() => setShowIntroduction(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-700/50 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-yellow-400" />
                  What I Can Do For You
                </h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5" />
                    <span>Find personalized income opportunities across 100+ sources</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5" />
                    <span>Analyze your skills and match them to high-paying opportunities</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5" />
                    <span>Create action plans and apply to opportunities automatically</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5" />
                    <span>Learn and adapt to your preferences over time</span>
                  </li>
                </ul>
              </div>

              <div className="bg-gray-700/50 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <Target className="w-4 h-4 text-blue-400" />
                  Getting Started
                </h3>
                <div className="space-y-3 text-gray-300">
                  <div>
                    <span className="text-purple-400 font-medium">Step 1: Complete Your Profile</span>
                    <p className="text-sm mt-1">I'll guide you through a 10-minute interview to understand your skills, experience, and goals.</p>
                  </div>
                  <div>
                    <span className="text-purple-400 font-medium">Step 2: Explore Opportunities</span>
                    <p className="text-sm mt-1">I'll analyze thousands of opportunities and present the best matches for you.</p>
                  </div>
                  <div>
                    <span className="text-purple-400 font-medium">Step 3: Take Action</span>
                    <p className="text-sm mt-1">Click "Quick Apply" to automatically submit applications with personalized cover letters.</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-700/50 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  How I Learn About You
                </h3>
                <p className="text-gray-300 text-sm">
                  Through our conversational interview, I discover:
                </p>
                <ul className="mt-2 space-y-1 text-gray-400 text-sm">
                  <li>• Your professional background and expertise</li>
                  <li>• Hidden talents and monetizable skills</li>
                  <li>• Income goals and work preferences</li>
                  <li>• Available time and commitment level</li>
                  <li>• Deal-breakers and constraints</li>
                </ul>
              </div>

              <div className="bg-purple-600/20 rounded-lg p-4 border border-purple-500/30">
                <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-yellow-400" />
                  Pro Tips
                </h3>
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li>💡 Be specific about your skills - the more I know, the better matches I find</li>
                  <li>💡 Set realistic income goals to get achievable opportunities</li>
                  <li>💡 Check back daily - I find new opportunities every hour</li>
                  <li>💡 Use the feedback buttons to help me learn your preferences</li>
                </ul>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowIntroduction(false);
                    if (!interviewMode && !externalContext?.interview_completed) {
                      connectToInterviewSystem();
                    }
                  }}
                  className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 transition-colors"
                >
                  Start Interview (10 min)
                </button>
                <button
                  onClick={() => setShowIntroduction(false)}
                  className="flex-1 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors"
                >
                  Explore First
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

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

      {/* Interview Progress Bar */}
      {interviewMode && interviewState.active && (
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Interview Progress</span>
            <span className="text-sm text-purple-400">
              {interviewState.completion_percentage.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${interviewState.completion_percentage}%` }}
            />
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

                {/* Interview Question Options */}
                {interviewMode && currentQuestion && message.metadata?.question && (
                  <div className="mt-3 space-y-2">
                    {currentQuestion.input_type === 'multiple_choice' && currentQuestion.options && (
                      <div className="space-y-2">
                        {currentQuestion.options.map((option, idx) => (
                          <button
                            key={idx}
                            onClick={() => {
                              handleOptionSelect(option);
                              submitInterviewResponse(option);
                            }}
                            className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg border border-gray-600 text-white transition-colors"
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}

                    {currentQuestion.input_type === 'multi_select' && currentQuestion.options && (
                      <div className="space-y-2">
                        <p className="text-xs text-gray-400 mb-2">Select all that apply:</p>
                        {currentQuestion.options.map((option, idx) => (
                          <label
                            key={idx}
                            className="flex items-center p-2 bg-gray-700 hover:bg-gray-600 rounded-lg cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={selectedOptions.includes(option)}
                              onChange={() => handleOptionSelect(option)}
                              className="mr-3 rounded"
                            />
                            <span className="text-white text-sm">{option}</span>
                          </label>
                        ))}
                        {selectedOptions.length > 0 && (
                          <button
                            onClick={() => submitInterviewResponse(selectedOptions)}
                            className="w-full mt-2 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-medium"
                          >
                            Continue ({selectedOptions.length} selected)
                          </button>
                        )}
                      </div>
                    )}

                    {currentQuestion.input_type === 'yes_no' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => submitInterviewResponse('Yes')}
                          className="flex-1 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white font-medium"
                        >
                          Yes
                        </button>
                        <button
                          onClick={() => submitInterviewResponse('No')}
                          className="flex-1 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-medium"
                        >
                          No
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Regular Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && showSuggestions && !currentQuestion && (
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
                {message.sender === 'assistant' && message.id !== 'welcome' && !interviewMode && (
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
        {interviewMode && currentQuestion && currentQuestion.input_type === 'text' ? (
          /* Interview Text Input */
          <div className="space-y-2">
            <textarea
              value={interviewResponse}
              onChange={(e) => setInterviewResponse(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleInterviewSubmit();
                }
              }}
              placeholder={currentQuestion.required ? "Your response (required)..." : "Your response (optional)..."}
              className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-purple-500 resize-none"
              rows={3}
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">
                {currentQuestion.required ? 'Required' : 'Optional'} • Press Enter to submit
              </span>
              <div className="flex gap-2">
                {!currentQuestion.required && (
                  <button
                    onClick={() => submitInterviewResponse('')}
                    className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300"
                  >
                    Skip
                  </button>
                )}
                <button
                  onClick={handleInterviewSubmit}
                  disabled={currentQuestion.required && !interviewResponse.trim()}
                  className="px-4 py-1 text-xs bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium"
                >
                  Submit
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Regular Chat Input */
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={interviewMode ? "Type your response..." : "Ask me anything..."}
              className="flex-1 px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-purple-500"
              disabled={interviewMode && currentQuestion && currentQuestion.input_type !== 'text'}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isTyping || (interviewMode && currentQuestion && currentQuestion.input_type !== 'text')}
              className="w-10 h-10 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default PersonalAssistant;