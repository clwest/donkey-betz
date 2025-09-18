import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  MessageCircle,
  Send,
  Bot,
  User,
  Sparkles,
  RefreshCw,
  Download,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Settings,
  Zap,
  Brain,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  status?: 'sending' | 'sent' | 'error';
  metadata?: {
    model?: string;
    tokensUsed?: number;
    responseTime?: number;
    confidence?: number;
  };
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

const AssistantChatPage: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-5-mini');
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const models = [
    { value: 'gpt-5-mini', label: 'GPT-5 Mini', description: 'Fast and efficient' },
    { value: 'gpt-5', label: 'GPT-5', description: 'Most capable' },
    { value: 'claude-opus', label: 'Claude Opus', description: 'Best for analysis' },
    { value: 'claude-sonnet', label: 'Claude Sonnet', description: 'Balanced performance' }
  ];

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchConversations = async () => {
    try {
      const response = await api.get('/assistant/conversations/');
      const convos = response.data?.results || getMockConversations();
      setConversations(convos);
      
      if (convos.length > 0 && !activeConversation) {
        setActiveConversation(convos[0].id);
        setMessages(convos[0].messages);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
      const mockConvos = getMockConversations();
      setConversations(mockConvos);
      if (mockConvos.length > 0) {
        setActiveConversation(mockConvos[0].id);
        setMessages(mockConvos[0].messages);
      }
    }
  };

  const getMockConversations = (): Conversation[] => [
    {
      id: '1',
      title: 'Content Strategy Discussion',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [
        {
          id: '1',
          content: 'Hello! I need help creating a content strategy for my sports betting blog.',
          role: 'user',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          status: 'sent'
        },
        {
          id: '2',
          content: "I'd be happy to help you create a compelling content strategy for your sports betting blog! Let's start by understanding your target audience and goals.\n\nHere are some key areas we should cover:\n\n1. **Target Audience**: Who are your readers? (Casual bettors, pros, sports fans?)\n2. **Content Pillars**: What topics will you focus on?\n3. **Publishing Schedule**: How often will you post?\n4. **SEO Strategy**: What keywords should you target?\n\nWhat's your current experience level with sports betting content?",
          role: 'assistant',
          timestamp: new Date(Date.now() - 590000).toISOString(),
          status: 'sent',
          metadata: {
            model: 'gpt-5-mini',
            tokensUsed: 142,
            responseTime: 1200,
            confidence: 0.92
          }
        }
      ]
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date().toISOString(),
      status: 'sending'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);
    setLoading(true);

    try {
      const response = await api.post('/assistant/dev/chat/', {
        message: inputMessage,
        model: selectedModel,
        conversation_id: activeConversation
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        status: 'sent',
        metadata: {
          model: selectedModel,
          tokensUsed: response.data.tokens_used,
          responseTime: response.data.response_time,
          confidence: response.data.confidence
        }
      };

      setMessages(prev => [...prev.slice(0, -1), 
        { ...userMessage, status: 'sent' }, 
        assistantMessage
      ]);

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Mock response for demo
      const mockResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm here to help! However, there seems to be a connection issue. In the meantime, I can help you with:\n\n• Content strategy and planning\n• Sports betting analysis\n• Writing and editing assistance\n• Research and fact-checking\n• AI agent coordination\n\nWhat would you like to work on?",
        role: 'assistant',
        timestamp: new Date().toISOString(),
        status: 'sent',
        metadata: {
          model: selectedModel,
          tokensUsed: 89,
          responseTime: 800,
          confidence: 0.85
        }
      };

      setMessages(prev => [...prev.slice(0, -1), 
        { ...userMessage, status: 'sent' }, 
        mockResponse
      ]);
    } finally {
      setIsTyping(false);
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('Message copied to clipboard');
  };

  const rateMessage = (messageId: string, rating: 'up' | 'down') => {
    toast.success(`Feedback recorded: ${rating === 'up' ? 'Helpful' : 'Not helpful'}`);
  };

  const newConversation = () => {
    const newConvo: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    setConversations(prev => [newConvo, ...prev]);
    setActiveConversation(newConvo.id);
    setMessages([]);
  };

  const currentConversation = conversations.find(c => c.id === activeConversation);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-gray-900/70 backdrop-blur-lg border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <MessageCircle className="h-6 w-6 text-purple-500" />
                AI Assistant
              </h1>
              <p className="text-gray-400">Chat with your personal AI assistant</p>
            </div>
            <div className="flex items-center gap-4">
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger className="w-48 bg-gray-800 border-gray-700 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {models.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      <div className="flex flex-col">
                        <span className="font-medium">{model.label}</span>
                        <span className="text-xs text-gray-400">{model.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={newConversation}
                className="bg-purple-600 hover:bg-purple-700"
              >
                New Chat
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Conversations Sidebar */}
          <div className="lg:col-span-1">
            <Card className="bg-gray-800/50 border-gray-700 h-fit">
              <CardHeader>
                <CardTitle className="text-white text-lg">Conversations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 max-h-96 overflow-y-auto">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    onClick={() => {
                      setActiveConversation(conversation.id);
                      setMessages(conversation.messages);
                    }}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      activeConversation === conversation.id
                        ? 'bg-purple-600/20 border border-purple-600/50'
                        : 'bg-gray-700/50 hover:bg-gray-700/70'
                    }`}
                  >
                    <h4 className="font-medium text-white text-sm truncate">
                      {conversation.title}
                    </h4>
                    <p className="text-xs text-gray-400">
                      {new Date(conversation.updatedAt).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader className="border-b border-gray-700">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white">
                    {currentConversation?.title || 'New Conversation'}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge className="bg-green-600/20 text-green-400 border-green-600/50">
                      <Brain className="h-3 w-3 mr-1" />
                      {selectedModel}
                    </Badge>
                    <Button variant="ghost" size="sm">
                      <Settings className="h-4 w-4 text-gray-400" />
                    </Button>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="p-0">
                {/* Messages */}
                <div className="h-96 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 ? (
                    <div className="text-center py-12">
                      <Sparkles className="h-12 w-12 text-purple-500 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-white mb-2">
                        Start a new conversation
                      </h3>
                      <p className="text-gray-400 mb-6">
                        Ask me anything about content creation, sports analysis, or AI assistance
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                        {[
                          'Help me create a betting strategy',
                          'Generate content ideas for my blog',
                          'Analyze recent sports trends',
                          'Plan a content calendar'
                        ].map((suggestion, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            className="border-gray-600 text-gray-300 hover:bg-gray-700 text-left justify-start"
                            onClick={() => setInputMessage(suggestion)}
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex gap-3 ${
                          message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {message.role === 'assistant' && (
                          <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
                            <Bot className="h-4 w-4 text-white" />
                          </div>
                        )}
                        
                        <div className={`max-w-2xl ${
                          message.role === 'user' 
                            ? 'bg-purple-600 text-white' 
                            : 'bg-gray-700/50 text-gray-100'
                        } rounded-lg p-4`}>
                          <div className="prose prose-invert max-w-none">
                            <div className="whitespace-pre-wrap">
                              {message.content}
                            </div>
                          </div>
                          
                          <div className={`flex items-center justify-between mt-3 pt-3 border-t ${
                            message.role === 'user' 
                              ? 'border-purple-500' 
                              : 'border-gray-600'
                          }`}>
                            <div className="flex items-center gap-2 text-xs text-gray-300">
                              <Clock className="h-3 w-3" />
                              {new Date(message.timestamp).toLocaleTimeString()}
                              {message.metadata && (
                                <>
                                  <span>•</span>
                                  <Zap className="h-3 w-3" />
                                  {message.metadata.tokensUsed} tokens
                                  {message.metadata.responseTime && (
                                    <>
                                      <span>•</span>
                                      {message.metadata.responseTime}ms
                                    </>
                                  )}
                                </>
                              )}
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => copyMessage(message.content)}
                                className="h-6 w-6 p-0 hover:bg-gray-600"
                              >
                                <Copy className="h-3 w-3" />
                              </Button>
                              {message.role === 'assistant' && (
                                <>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => rateMessage(message.id, 'up')}
                                    className="h-6 w-6 p-0 hover:bg-gray-600"
                                  >
                                    <ThumbsUp className="h-3 w-3" />
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => rateMessage(message.id, 'down')}
                                    className="h-6 w-6 p-0 hover:bg-gray-600"
                                  >
                                    <ThumbsDown className="h-3 w-3" />
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {message.role === 'user' && (
                          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                            <User className="h-4 w-4 text-white" />
                          </div>
                        )}
                      </div>
                    ))
                  )}
                  
                  {isTyping && (
                    <div className="flex gap-3 justify-start">
                      <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="bg-gray-700/50 rounded-lg p-4">
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-100"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-200"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-gray-700">
                  <div className="flex gap-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message..."
                      disabled={loading}
                      className="bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-purple-500"
                    />
                    <Button
                      onClick={sendMessage}
                      disabled={!inputMessage.trim() || loading}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    Press Enter to send, Shift+Enter for new line
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssistantChatPage;