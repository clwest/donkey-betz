import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  MessageCircle, ChevronRight, X, Sparkles, Clock, CheckCircle,
  User, Briefcase, Target, Award, Send, SkipForward
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { apiClient } from '@/services/api.config';

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
  const wsRef = useRef<WebSocket | null>(null);

  const [loading, setLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [interviewState, setInterviewState] = useState<InterviewState | null>(null);
  const [response, setResponse] = useState<any>('');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [messageHistory, setMessageHistory] = useState<Array<{type: 'assistant' | 'user', content: string}>>([]);
  const [showQuickStart, setShowQuickStart] = useState(true);

  useEffect(() => {
    if (isOpen && !wsRef.current) {
      connectWebSocket();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [isOpen]);

  const connectWebSocket = () => {
    // Use development backend WebSocket URL
    const isDev = import.meta.env.MODE !== 'production';
    const wsUrl = isDev ? 'ws://localhost:8000/ws/interview/' :
      (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host + '/ws/interview/';

    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('Interview WebSocket connected');
      startInterview();
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    wsRef.current.onerror = (error) => {
      console.error('Interview WebSocket error:', error);
    };

    wsRef.current.onclose = () => {
      console.log('Interview WebSocket disconnected');
    };
  };

  const startInterview = async () => {
    setLoading(true);
    try {
      const quickStart = showQuickStart;
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'start_interview',
          quick_start: quickStart,
        }));
      }
    } catch (error) {
      console.error('Failed to start interview:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    if (data.question) {
      setCurrentQuestion(data.question);
      setInterviewState(data.state);

      // Add assistant message to history
      if (data.question.text) {
        setMessageHistory(prev => [...prev, {
          type: 'assistant',
          content: data.question.text
        }]);
      }
    }

    if (data.interview_complete) {
      handleInterviewComplete(data.profile);
    }

    if (data.insights) {
      // Show insights as they're discovered
      console.log('New insights:', data.insights);
    }
  };

  const submitResponse = () => {
    if (!currentQuestion) return;

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
      content: displayResponse
    }]);

    // Send response via WebSocket
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'interview_response',
        response: finalResponse,
      }));
    }

    // Reset input
    setResponse('');
    setSelectedOptions([]);
  };

  const handleInterviewComplete = (profile: any) => {
    onComplete(profile);
    onClose();
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

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="h-6 w-6 text-primary" />
              <div>
                <CardTitle>Personal AI Assistant Interview</CardTitle>
                <CardDescription>
                  Let's get to know each other • 8-10 minutes
                </CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {/* Progress Bar */}
        {interviewState && (
          <div className="px-6 py-3 border-b bg-muted/50">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {getPhaseIcon(interviewState.phase)}
                <span className="text-sm font-medium">
                  {getPhaseLabel(interviewState.phase)}
                </span>
              </div>
              <span className="text-sm text-muted-foreground">
                {Math.round(interviewState.completion_percentage)}% Complete
              </span>
            </div>
            <Progress value={interviewState.completion_percentage} className="h-2" />
          </div>
        )}

        <CardContent className="p-6 overflow-y-auto max-h-[60vh]">
          {/* Initial Welcome */}
          {!currentQuestion && showQuickStart && (
            <div className="space-y-4">
              <div className="text-center space-y-2">
                <Sparkles className="h-12 w-12 text-primary mx-auto" />
                <h3 className="text-lg font-semibold">Welcome to Your Personal AI Setup!</h3>
                <p className="text-muted-foreground">
                  I'll ask you some questions to understand your skills, experience, and goals.
                  This helps me find perfect income opportunities tailored just for you.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4">
                <Card className="p-4">
                  <div className="flex items-start gap-3">
                    <Clock className="h-5 w-5 text-primary mt-0.5" />
                    <div>
                      <h4 className="font-medium">Quick Start</h4>
                      <p className="text-sm text-muted-foreground">
                        2 minutes - Basic profile for immediate opportunities
                      </p>
                    </div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium">Full Interview</h4>
                      <p className="text-sm text-muted-foreground">
                        8-10 minutes - Deep understanding for best matches
                      </p>
                    </div>
                  </div>
                </Card>
              </div>

              <div className="flex gap-3 justify-center pt-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowQuickStart(false);
                    startInterview();
                  }}
                >
                  <Clock className="h-4 w-4 mr-2" />
                  Quick Start (2 min)
                </Button>
                <Button
                  onClick={() => {
                    setShowQuickStart(false);
                    startInterview();
                  }}
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Full Interview (8-10 min)
                </Button>
              </div>

              <Button
                variant="ghost"
                className="w-full"
                onClick={skipInterview}
              >
                <SkipForward className="h-4 w-4 mr-2" />
                Skip for now
              </Button>
            </div>
          )}

          {/* Current Question */}
          {currentQuestion && (
            <div className="space-y-4">
              {/* Message History */}
              <div className="space-y-3 mb-6">
                {messageHistory.slice(-5).map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        msg.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Input Section */}
              <div className="space-y-3">
                {/* Text Input */}
                {currentQuestion.input_type === 'text' && (
                  <Textarea
                    value={response}
                    onChange={(e) => setResponse(e.target.value)}
                    placeholder="Type your answer here..."
                    className="min-h-[100px]"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        submitResponse();
                      }
                    }}
                  />
                )}

                {/* Multiple Choice */}
                {currentQuestion.input_type === 'multiple_choice' && currentQuestion.options && (
                  <RadioGroup value={response} onValueChange={setResponse}>
                    {currentQuestion.options.map((option) => (
                      <div key={option} className="flex items-center space-x-2 p-2 hover:bg-muted rounded">
                        <RadioGroupItem value={option} id={option} />
                        <Label htmlFor={option} className="flex-1 cursor-pointer">
                          {option}
                        </Label>
                      </div>
                    ))}
                  </RadioGroup>
                )}

                {/* Multi Select */}
                {currentQuestion.input_type === 'multi_select' && currentQuestion.options && (
                  <div className="space-y-2">
                    {currentQuestion.options.map((option) => (
                      <div key={option} className="flex items-center space-x-2 p-2 hover:bg-muted rounded">
                        <Checkbox
                          id={option}
                          checked={selectedOptions.includes(option)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setSelectedOptions([...selectedOptions, option]);
                            } else {
                              setSelectedOptions(selectedOptions.filter(o => o !== option));
                            }
                          }}
                        />
                        <Label htmlFor={option} className="flex-1 cursor-pointer">
                          {option}
                        </Label>
                      </div>
                    ))}
                  </div>
                )}

                {/* Yes/No */}
                {currentQuestion.input_type === 'yes_no' && (
                  <div className="flex gap-3">
                    <Button
                      variant={response === 'yes' ? 'default' : 'outline'}
                      className="flex-1"
                      onClick={() => setResponse('yes')}
                    >
                      Yes
                    </Button>
                    <Button
                      variant={response === 'no' ? 'default' : 'outline'}
                      className="flex-1"
                      onClick={() => setResponse('no')}
                    >
                      No
                    </Button>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <div className="flex items-center justify-between pt-4 border-t">
                <Button
                  variant="ghost"
                  onClick={skipInterview}
                >
                  Skip Interview
                </Button>
                <Button
                  onClick={submitResponse}
                  disabled={
                    !response && selectedOptions.length === 0 &&
                    currentQuestion.required
                  }
                >
                  <Send className="h-4 w-4 mr-2" />
                  Continue
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PersonalAssistantInterview;