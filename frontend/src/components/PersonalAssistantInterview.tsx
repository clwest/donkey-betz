import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageCircle, ChevronRight, X, Sparkles, Clock, CheckCircle,
  User, Briefcase, Target, Award, Send, SkipForward, Bot,
  Lightbulb, Calendar, Timer, Brain, Zap, Star, TrendingUp
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { unifiedConnector } from '../services/UnifiedPlatformConnector';
import { toast } from 'sonner';

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
  phase: string;
  current_question_id: string;
  completion_percentage: number;
  insights: string[];
}

interface PersonalAssistantInterviewProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (profile: any) => void;
}

const PersonalAssistantInterview: React.FC<PersonalAssistantInterviewProps> = ({
  isOpen,
  onClose,
  onComplete,
}) => {
  const { user } = useAuthStore();

  const [loading, setLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [interviewState, setInterviewState] = useState<InterviewState | null>(null);
  const [response, setResponse] = useState<any>('');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [messageHistory, setMessageHistory] = useState<Array<{type: 'assistant' | 'user', content: string}>>([]);
  const [showQuickStart, setShowQuickStart] = useState(true);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isInterviewComplete, setIsInterviewComplete] = useState(false);
  const [extractedProfile, setExtractedProfile] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      initializeInterview();
    }
    return () => {
      // Cleanup unified connector listeners
      unifiedConnector.offMessage('interview_started', handleInterviewStarted);
      unifiedConnector.offMessage('interview_question', handleInterviewQuestion);
      unifiedConnector.offMessage('interview_completed', handleInterviewCompleted);
    };
  }, [isOpen]);

  const initializeInterview = async () => {
    setLoading(true);
    try {
      // Set up event listeners for interview events
      unifiedConnector.onMessage('interview_started', handleInterviewStarted);
      unifiedConnector.onMessage('interview_question', handleInterviewQuestion);
      unifiedConnector.onMessage('interview_completed', handleInterviewCompleted);
      unifiedConnector.onMessage('interview_error', handleInterviewError);

      // Connect to the unified platform
      await unifiedConnector.connect('personal_assistant');
      toast.success('Connected to Personal AI Assistant!');
      setLoading(false); // Important: Set loading to false on success!

    } catch (error) {
      console.error('Failed to initialize interview:', error);
      toast.error('Failed to connect to the interview system. Please try again.');
      setLoading(false);
    }
  };

  const startInterview = async (interviewType: 'quick' | 'comprehensive' = 'comprehensive') => {
    // Check authentication first
    if (!user) {
      toast.error('Please log in to start the interview');
      onClose();
      return;
    }

    setLoading(true);
    try {
      // Start interview through unified platform
      unifiedConnector.startPersonalAssistantInterview(interviewType, user.id.toString());
      setShowQuickStart(false);

    } catch (error) {
      console.error('Failed to start interview:', error);
      toast.error('Failed to start interview. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInterviewStarted = (data: any) => {
    console.log('🎙️ Interview started:', data);
    setSessionId(data.session_id);
    setInterviewState({
      phase: 'introduction',
      current_question_id: '',
      completion_percentage: 0,
      insights: []
    });

    // Don't simulate first question - wait for the actual question from backend
    // The backend will send the first question immediately after interview_started
    setLoading(false);
  };

  const handleInterviewQuestion = (data: any) => {
    console.log('❓ New interview question:', data);

    // Handle both formats: {question: {...}} and direct question object
    const question = data.question || data;

    // Check if we have an acknowledgment (conversational response)
    if (data.acknowledgment) {
      // Add the AI's acknowledgment to the message history
      setMessageHistory(prev => [...prev, {
        type: 'assistant',
        content: data.acknowledgment,
        isAcknowledgment: true
      }]);
    }

    // Make sure we have a valid question object with text
    if (question && typeof question === 'object') {
      // Extract the text - handle nested structure where text might be an object
      let questionText = question.text;
      if (typeof questionText === 'object' && questionText !== null && 'text' in questionText) {
        // If text is an object with a text property, use that
        questionText = questionText.text;
      }

      // Update the question object with the extracted text
      const normalizedQuestion = {
        ...question,
        text: questionText,
        conversational: data.conversation_style || false
      };

      console.log('📋 Question details:', {
        input_type: normalizedQuestion.input_type,
        has_options: !!normalizedQuestion.options,
        options: normalizedQuestion.options,
        text: normalizedQuestion.text,
        conversational: normalizedQuestion.conversational
      });

      setCurrentQuestion(normalizedQuestion);

      if (data.state) {
        setInterviewState(data.state);
      }

      // Add assistant message to history - ensure we're adding the text string
      // Only add if it's not already in the acknowledgment
      if (!data.acknowledgment || data.acknowledgment !== questionText) {
        setMessageHistory(prev => [...prev, {
          type: 'assistant',
          content: String(questionText || ''),  // Ensure it's a string
          isQuestion: true
        }]);
      }
    } else {
      console.warn('Invalid question data received:', data);
    }
  };

  const handleInterviewCompleted = (data: any) => {
    console.log('✅ Interview completed:', data);
    setIsInterviewComplete(true);
    setExtractedProfile(data.profile || buildBasicProfile());
    toast.success('Interview completed! Building your personalized profile...');
  };

  const handleInterviewError = (data: any) => {
    console.error('❌ Interview error:', data);
    const errorMessage = data.data?.message || data.message || 'An error occurred during the interview.';
    toast.error(errorMessage);

    // If authentication required, close the modal and prompt login
    if (errorMessage.includes('Authentication required')) {
      setLoading(false);
      onClose();
    }
  };

  const submitResponse = () => {
    if (!currentQuestion || !sessionId) return;

    let finalResponse = response;

    // Handle different input types
    if (currentQuestion.input_type === 'multi_select') {
      finalResponse = selectedOptions;
    } else if (currentQuestion.input_type === 'yes_no') {
      finalResponse = response === 'yes';
    }

    // Add user response to history
    let displayResponse = finalResponse;
    if (Array.isArray(finalResponse)) {
      displayResponse = finalResponse.join(', ');
    } else if (typeof finalResponse === 'boolean') {
      displayResponse = finalResponse ? 'Yes' : 'No';
    }

    setMessageHistory(prev => [...prev, {
      type: 'user',
      content: displayResponse.toString()
    }]);

    // Send response via unified platform
    unifiedConnector.processInterviewResponse(sessionId, finalResponse.toString(), currentQuestion.id);

    // Don't simulate next question - the backend will send the real next question
    // simulateNextQuestion(); // REMOVED - was causing duplicate questions

    // Reset input
    setResponse('');
    setSelectedOptions([]);
  };

  const simulateNextQuestion = () => {
    // For demo purposes, simulate progressing through different phases
    const currentProgress = interviewState?.completion_percentage || 0;
    const newProgress = Math.min(currentProgress + 20, 100);

    if (newProgress >= 100) {
      // Complete interview
      const profile = buildBasicProfile();
      handleInterviewCompleted({ profile });
      return;
    }

    // Generate next question based on progress
    const phases = ['introduction', 'skills_discovery', 'experience_deep_dive', 'goals_preferences'];
    const currentPhaseIndex = Math.floor(newProgress / 25);
    const currentPhase = phases[currentPhaseIndex] || 'goals_preferences';

    const nextQuestions = {
      introduction: {
        id: 'intro_skills',
        text: 'Great! Now, what are your strongest professional skills? Feel free to mention anything you\'re good at.',
        input_type: 'text' as const
      },
      skills_discovery: {
        id: 'skills_experience',
        text: 'How many years of professional experience do you have in your main field?',
        input_type: 'multiple_choice' as const,
        options: ['Less than 1 year', '1-3 years', '3-5 years', '5-10 years', '10+ years']
      },
      experience_deep_dive: {
        id: 'experience_goals',
        text: 'What\'s your target for additional monthly income?',
        input_type: 'multiple_choice' as const,
        options: ['$500-$1,000', '$1,000-$2,500', '$2,500-$5,000', '$5,000+', 'Just exploring']
      },
      goals_preferences: {
        id: 'goals_final',
        text: 'What type of work appeals to you most?',
        input_type: 'multiple_choice' as const,
        options: ['Freelancing', 'Remote work', 'Consulting', 'Creating products', 'Teaching', 'Open to anything']
      }
    };

    const nextQuestion: InterviewQuestion = {
      ...nextQuestions[currentPhase],
      phase: currentPhase,
      required: true,
      progress: newProgress
    };

    setCurrentQuestion(nextQuestion);
    setInterviewState(prev => prev ? {
      ...prev,
      phase: currentPhase,
      completion_percentage: newProgress,
      current_question_id: nextQuestion.id
    } : null);

    setMessageHistory(prev => [...prev, {
      type: 'assistant',
      content: nextQuestion.text
    }]);
  };

  const buildBasicProfile = () => {
    return {
      name: user?.first_name || user?.username || 'User',
      email: user?.email || '',
      skills: response.includes('skill') ? [response] : ['General skills'],
      experience_level: 'Beginner',
      income_goal: '$1,000-$2,500',
      work_preferences: ['Remote work'],
      completed_via: 'interview',
      profile_strength_score: 75,
      completeness_percentage: 100,
      setup_completed: true
    };
  };

  const handleInterviewComplete = (profile: any) => {
    setExtractedProfile(profile);
    setIsInterviewComplete(true);
  };

  const skipInterview = () => {
    // Quick profile setup - just basic info
    const quickProfile = {
      name: user?.username || '',
      email: user?.email || '',
      completed_via: 'skip',
      profile_strength_score: 10,
    };
    onComplete(quickProfile);
    onClose();
  };

  const getPhaseIcon = (phase: string) => {
    switch(phase) {
      case 'introduction': return <User className="h-4 w-4" />;
      case 'skills_discovery': return <Award className="h-4 w-4" />;
      case 'experience_deep_dive': return <Briefcase className="h-4 w-4" />;
      case 'goals_preferences': return <Target className="h-4 w-4" />;
      default: return <MessageCircle className="h-4 w-4" />;
    }
  };

  const getPhaseLabel = (phase: string) => {
    const labels: Record<string, string> = {
      'introduction': 'Getting Started',
      'skills_discovery': 'Your Skills',
      'experience_deep_dive': 'Experience',
      'goals_preferences': 'Goals & Preferences',
      'hidden_talents': 'Hidden Talents',
      'verification': 'Final Steps',
    };
    return labels[phase] || phase;
  };

  if (!isOpen) return null;

  // Show completion screen
  if (isInterviewComplete && extractedProfile) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-background rounded-xl border border-gray-700 p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        >
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-foreground" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">Interview Complete!</h2>
            <p className="text-muted-foreground">
              I've analyzed your responses and built your personalized profile.
            </p>
          </div>

          <div className="space-y-4 mb-6">
            <div className="bg-card/50 rounded-lg p-4">
              <h3 className="text-foreground font-semibold mb-2 flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-400" />
                Profile Summary
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Name:</span>
                  <span className="text-foreground ml-2">{extractedProfile.name}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Profile Score:</span>
                  <span className="text-green-500 ml-2">{extractedProfile.profile_strength_score}%</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Income Goal:</span>
                  <span className="text-foreground ml-2">{extractedProfile.income_goal}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Experience:</span>
                  <span className="text-foreground ml-2">{extractedProfile.experience_level}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                onComplete(extractedProfile);
                onClose();
              }}
              className="flex-1 bg-gradient-to-r from-purple-600 to-purple-700 text-foreground py-3 px-6 rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all flex items-center justify-center gap-2"
            >
              <ChevronRight className="w-5 h-5" />
              Continue to Dashboard
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-card text-muted-foreground rounded-lg hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-background rounded-xl border border-gray-700 w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-lg rounded-full flex items-center justify-center">
                  <Bot className="h-7 w-7 text-foreground" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-purple-600 animate-pulse" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                  Your Personal AI Assistant
                  <span className="text-xs bg-white/20 px-2 py-1 rounded-full">Live</span>
                </h2>
                <p className="text-foreground/80 text-sm">
                  I'm here to understand you and help you succeed • 8-10 minutes
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-foreground/80 hover:text-foreground p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        {interviewState && (
          <div className="px-6 py-3 border-b border-gray-700 bg-card/50">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-foreground">
                {getPhaseIcon(interviewState.phase)}
                <span className="text-sm font-medium">
                  {getPhaseLabel(interviewState.phase)}
                </span>
              </div>
              <span className="text-sm text-muted-foreground">
                {Math.round(interviewState.completion_percentage)}% Complete
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${interviewState.completion_percentage}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}

        <div className="flex-1 p-6 overflow-y-auto">
          {/* Initial Welcome */}
          {!currentQuestion && showQuickStart && (
            <div className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg animate-pulse">
                    <Bot className="w-6 h-6 text-foreground" />
                  </div>
                  <div className="flex-1 bg-card rounded-xl p-5 border border-gray-700">
                    <h3 className="text-lg font-semibold text-foreground mb-3">
                      👋 Hi! I'm your Personal AI Assistant
                    </h3>
                    <p className="text-muted-foreground leading-relaxed mb-3">
                      I'm here to get to know you better so I can help you find amazing income opportunities
                      that match your unique skills and goals.
                    </p>
                    <p className="text-muted-foreground leading-relaxed">
                      Think of this as a friendly conversation, not a formal interview. I'll ask about your
                      experience, what you're good at, and what you're looking for. The more I learn about
                      you, the better I can help you succeed!
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                <div className="bg-card/50 border border-gray-700 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                      <Clock className="h-4 w-4 text-blue-500" />
                    </div>
                    <div>
                      <h4 className="font-medium text-foreground">Quick Start</h4>
                      <p className="text-sm text-muted-foreground">
                        2 minutes - Basic profile for immediate opportunities
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-card/50 border border-gray-700 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    </div>
                    <div>
                      <h4 className="font-medium text-foreground">Full Interview</h4>
                      <p className="text-sm text-muted-foreground">
                        8-10 minutes - Deep understanding for best matches
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-3 pt-4">
                <button
                  onClick={() => startInterview('quick')}
                  className="w-full px-6 py-3 bg-blue-600 text-foreground rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Clock className="h-4 w-4" />
                  Quick Start (2 min)
                </button>
                <button
                  onClick={() => startInterview('comprehensive')}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-foreground rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all flex items-center justify-center gap-2"
                >
                  <Sparkles className="h-4 w-4" />
                  Full Interview (8-10 min)
                </button>
                <button
                  onClick={skipInterview}
                  className="w-full px-6 py-3 bg-card text-muted-foreground rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center gap-2"
                >
                  <SkipForward className="h-4 w-4" />
                  Skip for now
                </button>
              </div>
            </div>
          )}

          {/* Current Question */}
          {currentQuestion && (
            <div className="space-y-6">
              {/* Message History */}
              <div className="space-y-4 mb-6 max-h-[40vh] overflow-y-auto">
                <AnimatePresence>
                  {messageHistory.slice(-5).map((msg, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className="flex items-start gap-3 max-w-[85%]">
                        {msg.type === 'assistant' && (
                          <div className="relative">
                            <div className="w-9 h-9 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                              <Bot className="w-5 h-5 text-foreground" />
                            </div>
                            {msg.isAcknowledgment && (
                              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border border-gray-900" />
                            )}
                          </div>
                        )}
                        <div
                          className={`p-4 rounded-xl ${
                            msg.type === 'user'
                              ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-foreground shadow-md'
                              : msg.isAcknowledgment
                                ? 'bg-gradient-to-r from-gray-800 to-gray-750 text-foreground border border-gray-700 italic'
                                : 'bg-card text-foreground border border-gray-700 shadow-sm'
                          } ${msg.type === 'assistant' && 'animate-fadeIn'}`}
                        >
                          <p className={`text-sm leading-relaxed ${msg.isAcknowledgment ? 'italic' : ''}`}>
                            {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                          </p>
                        </div>
                        {msg.type === 'user' && (
                          <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                            <User className="w-5 h-5 text-foreground" />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* Input Section */}
              <div className="space-y-4">
                {/* Text Input */}
                {currentQuestion.input_type === 'text' && (
                  <textarea
                    value={response}
                    onChange={(e) => setResponse(e.target.value)}
                    placeholder="Type your answer here..."
                    className="w-full p-4 bg-card text-foreground rounded-lg border border-gray-700 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 resize-none min-h-[100px]"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        submitResponse();
                      }
                    }}
                  />
                )}

                {/* Multiple Choice */}
                {currentQuestion.input_type === 'multiple_choice' && currentQuestion.options && (
                  <div className="space-y-2">
                    {currentQuestion.options.map((option) => (
                      <button
                        key={option}
                        onClick={() => setResponse(option)}
                        className={`w-full p-3 text-left rounded-lg border transition-all ${
                          response === option
                            ? 'border-purple-500 bg-purple-500/20 text-purple-300'
                            : 'border-gray-700 bg-card/50 text-muted-foreground hover:border-gray-600'
                        }`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                )}

                {/* Multi Select */}
                {currentQuestion.input_type === 'multi_select' && currentQuestion.options && (
                  <div className="space-y-2">
                    {currentQuestion.options.map((option) => (
                      <button
                        key={option}
                        onClick={() => {
                          if (selectedOptions.includes(option)) {
                            setSelectedOptions(selectedOptions.filter(o => o !== option));
                          } else {
                            setSelectedOptions([...selectedOptions, option]);
                          }
                        }}
                        className={`w-full p-3 text-left rounded-lg border transition-all flex items-center gap-3 ${
                          selectedOptions.includes(option)
                            ? 'border-purple-500 bg-purple-500/20 text-purple-300'
                            : 'border-gray-700 bg-card/50 text-muted-foreground hover:border-gray-600'
                        }`}
                      >
                        <div className={`w-4 h-4 rounded border-2 ${
                          selectedOptions.includes(option)
                            ? 'bg-purple-500 border-purple-500'
                            : 'border-gray-500'
                        }`}>
                          {selectedOptions.includes(option) && (
                            <CheckCircle className="w-3 h-3 text-foreground" />
                          )}
                        </div>
                        {option}
                      </button>
                    ))}
                  </div>
                )}

                {/* Yes/No */}
                {currentQuestion.input_type === 'yes_no' && (
                  <div className="flex gap-3">
                    <button
                      onClick={() => setResponse('yes')}
                      className={`flex-1 p-3 rounded-lg border transition-all ${
                        response === 'yes'
                          ? 'border-green-500 bg-green-500/20 text-green-300'
                          : 'border-gray-700 bg-card/50 text-muted-foreground hover:border-gray-600'
                      }`}
                    >
                      Yes
                    </button>
                    <button
                      onClick={() => setResponse('no')}
                      className={`flex-1 p-3 rounded-lg border transition-all ${
                        response === 'no'
                          ? 'border-red-500 bg-red-500/20 text-red-300'
                          : 'border-gray-700 bg-card/50 text-muted-foreground hover:border-gray-600'
                      }`}
                    >
                      No
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="flex items-center justify-center py-8">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full"
              />
            </div>
          )}

          {/* Fallback if nothing else shows */}
          {!loading && !currentQuestion && !showQuickStart && !isInterviewComplete && (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">Interview system is ready.</p>
              <button
                onClick={() => setShowQuickStart(true)}
                className="px-6 py-2 bg-purple-600 text-foreground rounded-lg hover:bg-purple-700"
              >
                Start Interview
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        {currentQuestion && (
          <div className="p-6 border-t border-gray-700 bg-card/50">
            <div className="flex items-center justify-between">
              <button
                onClick={skipInterview}
                className="px-4 py-2 text-muted-foreground hover:text-muted-foreground transition-colors"
              >
                Skip Interview
              </button>
              <button
                onClick={submitResponse}
                disabled={
                  !response && selectedOptions.length === 0 &&
                  currentQuestion.required
                }
                className="px-6 py-2 bg-purple-600 text-foreground rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
                Continue
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default PersonalAssistantInterview;