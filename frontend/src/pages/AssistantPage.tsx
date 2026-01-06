import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { assistantApi, userLearningApi } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import {
  Send, Mic, MicOff, Loader2, Bot, User, Copy, RefreshCw,
  ThumbsUp, ThumbsDown, Trash2, Sparkles, AlertCircle,
  ChevronRight, CheckCircle, XCircle, Zap, MessageSquare,
  Heart, TrendingUp, Lightbulb, Palette, Settings2
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  tools_used?: string[]
  feedback?: 'positive' | 'negative'
}

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface AttentionItem {
  id: string
  title: string
  summary?: string
  priority: number
  severity: 'critical' | 'warning' | 'info'
  explanation?: string
  recommended_action?: string
  location?: string
  suggested_action?: string
}

interface UserPreference {
  id: string
  category: string
  preference: string
  confidence: number
  learned_from: string
}

interface StyleEvolution {
  date: string
  style: string
  change: 'added' | 'strengthened' | 'weakened'
}

interface LearningInsight {
  id: string
  type: string
  message: string
  actionable: boolean
}

type SidebarTab = 'context' | 'learning'

const quickActions = [
  { label: 'Generate an image', prompt: 'Generate an image of a futuristic city at sunset' },
  { label: 'Check system status', prompt: 'What is the current system status?' },
  { label: 'Run agent cycle', prompt: 'Run an agent cycle now' },
  { label: 'Show opportunities', prompt: 'What opportunities are available?' },
  { label: 'Create content', prompt: 'Help me create a blog post about AI' },
  { label: 'Analyze trends', prompt: 'What are the latest trending topics?' },
]

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [showSidebar, setShowSidebar] = useState(true)
  const [sidebarTab, setSidebarTab] = useState<SidebarTab>('context')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuthStore()

  // Fetch attention items
  const { data: attentionData } = useQuery({
    queryKey: ['attention-items'],
    queryFn: () => assistantApi.getAttentionItems(),
    enabled: isAuthenticated,
    retry: false,
  })

  // Fetch learning summary
  const { data: learningData } = useQuery({
    queryKey: ['assistant-learning'],
    queryFn: () => assistantApi.getLearning(),
    enabled: isAuthenticated,
    retry: false,
  })

  // User Learning Queries
  const { data: preferencesData } = useQuery({
    queryKey: ['user-preferences'],
    queryFn: () => userLearningApi.getAllPreferences(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  const { data: styleEvolutionData } = useQuery({
    queryKey: ['style-evolution'],
    queryFn: () => userLearningApi.getStyleEvolution(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  const { data: insightsData } = useQuery({
    queryKey: ['learning-insights'],
    queryFn: () => userLearningApi.getInsights(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  const { data: velocityData } = useQuery({
    queryKey: ['learning-velocity'],
    queryFn: () => userLearningApi.getVelocity(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  // Generate insights mutation
  const generateInsightsMutation = useMutation({
    mutationFn: () => userLearningApi.generateInsights(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'New insights generated!' })
      queryClient.invalidateQueries({ queryKey: ['learning-insights'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate insights' })
    },
  })

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: (message: string) => assistantApi.chat(message, { use_personal_assistant: true }),
    onSuccess: (response) => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response || response.data.message || 'No response',
        timestamp: new Date(),
        tools_used: response.data.tools_used || [],
      }
      setMessages((prev) => [...prev, assistantMessage])
    },
    onError: () => {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    },
  })

  // Voice transcription mutation
  const transcribeMutation = useMutation({
    mutationFn: (audioBlob: Blob) => assistantApi.transcribe(audioBlob),
    onSuccess: (response) => {
      const transcribedText = response.data.text || response.data.transcription
      if (transcribedText) {
        setInput(transcribedText)
        setActionResult({ type: 'success', message: 'Voice transcribed!' })
      }
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to transcribe voice' })
    },
  })

  // Feedback mutation
  const feedbackMutation = useMutation({
    mutationFn: ({ messageId, rating }: { messageId: string; rating: 'positive' | 'negative' }) =>
      assistantApi.feedback(messageId, rating),
    onSuccess: (_, variables) => {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === variables.messageId ? { ...msg, feedback: variables.rating } : msg
        )
      )
      setActionResult({ type: 'success', message: 'Feedback recorded. Thank you!' })
    },
  })

  // Reset mutation
  const resetMutation = useMutation({
    mutationFn: () => assistantApi.reset(),
    onSuccess: () => {
      setMessages([])
      setActionResult({ type: 'success', message: 'Conversation cleared' })
      queryClient.invalidateQueries({ queryKey: ['assistant-learning'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to reset assistant' })
    },
  })

  const attentionItems: AttentionItem[] = attentionData?.data?.items || []
  const learningSummary = learningData?.data || {}
  const userPreferences: UserPreference[] = preferencesData?.data?.preferences || preferencesData?.data || []
  const styleEvolution: StyleEvolution[] = styleEvolutionData?.data?.evolution || styleEvolutionData?.data || []
  const insights: LearningInsight[] = insightsData?.data?.insights || insightsData?.data || []
  const velocity = velocityData?.data || {}

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const sendMessage = async (messageText?: string) => {
    const text = messageText || input
    if (!text.trim() || chatMutation.isPending) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    chatMutation.mutate(text)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        transcribeMutation.mutate(audioBlob)
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Failed to start recording:', error)
      setActionResult({ type: 'error', message: 'Failed to access microphone' })
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    setActionResult({ type: 'success', message: 'Copied to clipboard' })
  }

  const regenerateResponse = (messageIndex: number) => {
    // Find the user message before this assistant message
    const userMessage = messages[messageIndex - 1]
    if (userMessage && userMessage.role === 'user') {
      // Remove the assistant message and regenerate
      setMessages((prev) => prev.slice(0, messageIndex))
      chatMutation.mutate(userMessage.content)
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
              <Bot size={20} className="text-primary-400" />
            </div>
            <div>
              <h2 className="font-semibold">AI Assistant</h2>
              <p className="text-sm text-gray-400">Powered by GPT-5-mini</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-secondary text-sm"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              {showSidebar ? 'Hide' : 'Show'} Panel
            </button>
            <button
              className="btn btn-secondary text-sm text-accent-red"
              onClick={() => resetMutation.mutate()}
              disabled={resetMutation.isPending || messages.length === 0}
            >
              {resetMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
              Clear
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto space-y-4 pb-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <Bot size={48} className="mb-4 opacity-50" />
              <p className="text-xl mb-2">How can I help you today?</p>
              <p className="text-sm mb-6">Ask me anything about your platform...</p>

              {/* Quick Actions */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-w-2xl">
                {quickActions.map((action) => (
                  <button
                    key={action.label}
                    onClick={() => sendMessage(action.prompt)}
                    className="p-3 rounded-lg border border-dark-border hover:border-primary-500 hover:bg-primary-500/10 transition-colors text-left"
                  >
                    <p className="text-sm text-white">{action.label}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                  <div className="h-8 w-8 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                    <Bot size={16} className="text-primary-400" />
                  </div>
                )}

                <div className={cn(
                  'max-w-[70%] group',
                  message.role === 'user' && 'order-first'
                )}>
                  <div
                    className={cn(
                      'rounded-lg px-4 py-2',
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-dark-card border border-dark-border'
                    )}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>

                    {/* Tools used */}
                    {message.tools_used && message.tools_used.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-dark-border">
                        {message.tools_used.map((tool) => (
                          <span
                            key={tool}
                            className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400"
                          >
                            {tool}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Message actions */}
                  <div className={cn(
                    'flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}>
                    <span className="text-xs text-gray-500 mr-2">
                      {message.timestamp.toLocaleTimeString()}
                    </span>

                    {message.role === 'assistant' && (
                      <>
                        <button
                          onClick={() => copyMessage(message.content)}
                          className="p-1 rounded hover:bg-dark-border"
                          title="Copy"
                        >
                          <Copy size={14} className="text-gray-400" />
                        </button>
                        <button
                          onClick={() => regenerateResponse(index)}
                          className="p-1 rounded hover:bg-dark-border"
                          title="Regenerate"
                          disabled={chatMutation.isPending}
                        >
                          <RefreshCw size={14} className="text-gray-400" />
                        </button>
                        <button
                          onClick={() => feedbackMutation.mutate({ messageId: message.id, rating: 'positive' })}
                          className={cn(
                            'p-1 rounded hover:bg-dark-border',
                            message.feedback === 'positive' && 'bg-accent-green/20'
                          )}
                          title="Good response"
                        >
                          <ThumbsUp size={14} className={message.feedback === 'positive' ? 'text-accent-green' : 'text-gray-400'} />
                        </button>
                        <button
                          onClick={() => feedbackMutation.mutate({ messageId: message.id, rating: 'negative' })}
                          className={cn(
                            'p-1 rounded hover:bg-dark-border',
                            message.feedback === 'negative' && 'bg-accent-red/20'
                          )}
                          title="Poor response"
                        >
                          <ThumbsDown size={14} className={message.feedback === 'negative' ? 'text-accent-red' : 'text-gray-400'} />
                        </button>
                      </>
                    )}
                  </div>
                </div>

                {message.role === 'user' && (
                  <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                    <User size={16} className="text-white" />
                  </div>
                )}
              </div>
            ))
          )}

          {chatMutation.isPending && (
            <div className="flex gap-3 justify-start">
              <div className="h-8 w-8 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                <Bot size={16} className="text-primary-400" />
              </div>
              <div className="bg-dark-card border border-dark-border rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-primary-400" />
                  <span className="text-sm text-gray-400">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-dark-border pt-4">
          <div className="flex gap-2">
            <button
              className={cn(
                'btn',
                isRecording ? 'btn-primary animate-pulse' : 'btn-secondary'
              )}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={transcribeMutation.isPending}
            >
              {transcribeMutation.isPending ? (
                <Loader2 size={20} className="animate-spin" />
              ) : isRecording ? (
                <MicOff size={20} />
              ) : (
                <Mic size={20} />
              )}
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isRecording ? 'Recording... Click mic to stop' : 'Type your message...'}
              className="input flex-1"
              disabled={chatMutation.isPending || isRecording}
            />
            <button
              onClick={() => sendMessage()}
              disabled={chatMutation.isPending || !input.trim()}
              className="btn btn-primary"
            >
              {chatMutation.isPending ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>

      {/* Sidebar */}
      {showSidebar && (
        <div className="w-80 flex flex-col overflow-hidden">
          {/* Sidebar Tabs */}
          <div className="flex gap-1 mb-4 p-1 bg-dark-bg rounded-lg">
            <button
              onClick={() => setSidebarTab('context')}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                sidebarTab === 'context' ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'
              )}
            >
              <Bot size={14} />
              Context
            </button>
            <button
              onClick={() => setSidebarTab('learning')}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                sidebarTab === 'learning' ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'
              )}
            >
              <Heart size={14} />
              Learning
            </button>
          </div>

          <div className="flex-1 overflow-auto space-y-4">
            {sidebarTab === 'context' ? (
              <>
                {/* Attention Items */}
                <div className="card">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertCircle size={18} className="text-accent-amber" />
                    <h3 className="font-semibold">Needs Attention</h3>
                    {attentionItems.length > 0 && (
                      <span className="ml-auto px-2 py-0.5 text-xs rounded-full bg-accent-amber/20 text-accent-amber">
                        {attentionItems.length}
                      </span>
                    )}
                  </div>
                  {attentionItems.length > 0 ? (
                    <div className="space-y-2">
                      {attentionItems.slice(0, 5).map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between p-2 rounded-lg bg-dark-bg hover:bg-dark-border cursor-pointer transition-colors group"
                          onClick={() => sendMessage(item.suggested_action || `Tell me about: ${item.title}`)}
                          title={item.explanation || item.summary || ''}
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            <span className={cn(
                              'h-2 w-2 rounded-full flex-shrink-0',
                              item.severity === 'critical' ? 'bg-accent-red animate-pulse' :
                              item.severity === 'warning' ? 'bg-accent-amber' : 'bg-accent-green'
                            )} />
                            <div className="min-w-0">
                              <span className="text-sm truncate block">{item.title}</span>
                              {item.location && (
                                <span className="text-xs text-gray-500 truncate block">{item.location}</span>
                              )}
                            </div>
                          </div>
                          <ChevronRight size={14} className="text-gray-500 flex-shrink-0 group-hover:text-primary-400" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-4">No items need attention</p>
                  )}
                </div>

                {/* Suggested Actions */}
                <div className="card">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles size={18} className="text-accent-cyan" />
                    <h3 className="font-semibold">Suggestions</h3>
                  </div>
                  <div className="space-y-2">
                    {quickActions.slice(0, 4).map((action) => (
                      <button
                        key={action.label}
                        onClick={() => sendMessage(action.prompt)}
                        className="w-full flex items-center gap-2 p-2 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors text-left"
                      >
                        <Zap size={14} className="text-accent-cyan flex-shrink-0" />
                        <span className="text-sm">{action.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Session Stats */}
                <div className="card">
                  <div className="flex items-center gap-2 mb-3">
                    <MessageSquare size={18} className="text-gray-400" />
                    <h3 className="font-semibold">This Session</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="text-center p-2 rounded-lg bg-dark-bg">
                      <p className="text-2xl font-bold">{messages.filter(m => m.role === 'user').length}</p>
                      <p className="text-xs text-gray-400">Messages</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-dark-bg">
                      <p className="text-2xl font-bold">
                        {messages.filter(m => m.tools_used && m.tools_used.length > 0).length}
                      </p>
                      <p className="text-xs text-gray-400">Tool Uses</p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* Learning Velocity */}
                <div className="card">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={18} className="text-accent-green" />
                    <h3 className="font-semibold">Learning Velocity</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Total Interactions</span>
                      <span className="font-medium">{velocity.total_interactions || learningSummary.total_interactions || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Preferences Learned</span>
                      <span className="font-medium">{velocity.preferences_count || learningSummary.preferences_count || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Learning Rate</span>
                      <span className="font-medium text-accent-green">
                        {velocity.learning_rate || '—'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Your Preferences */}
                <div className="card">
                  <div className="flex items-center gap-2 mb-3">
                    <Palette size={18} className="text-primary-400" />
                    <h3 className="font-semibold">Your Preferences</h3>
                  </div>
                  {Array.isArray(userPreferences) && userPreferences.length > 0 ? (
                    <div className="space-y-2">
                      {userPreferences.slice(0, 5).map((pref, idx) => (
                        <div
                          key={pref.id || idx}
                          className="p-2 rounded-lg bg-dark-bg"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-primary-400">{pref.category}</span>
                            <span className="text-xs text-gray-500">{Math.round(pref.confidence * 100)}%</span>
                          </div>
                          <p className="text-sm mt-1">{pref.preference}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-4">
                      As you use the assistant, your preferences will be learned automatically.
                    </p>
                  )}
                </div>

                {/* Style Evolution */}
                <div className="card">
                  <div className="flex items-center gap-2 mb-3">
                    <Settings2 size={18} className="text-accent-amber" />
                    <h3 className="font-semibold">Style Evolution</h3>
                  </div>
                  {Array.isArray(styleEvolution) && styleEvolution.length > 0 ? (
                    <div className="space-y-2">
                      {styleEvolution.slice(0, 4).map((item, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-2 p-2 rounded-lg bg-dark-bg"
                        >
                          <span className={cn(
                            'h-2 w-2 rounded-full flex-shrink-0',
                            item.change === 'added' ? 'bg-accent-green' :
                            item.change === 'strengthened' ? 'bg-accent-cyan' : 'bg-accent-amber'
                          )} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm truncate">{item.style}</p>
                            <p className="text-xs text-gray-500">{item.date}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-4">
                      Your style preferences will evolve over time.
                    </p>
                  )}
                </div>

                {/* Insights */}
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Lightbulb size={18} className="text-accent-cyan" />
                      <h3 className="font-semibold">Insights</h3>
                    </div>
                    <button
                      onClick={() => generateInsightsMutation.mutate()}
                      className="text-xs text-primary-400 hover:text-primary-300"
                      disabled={generateInsightsMutation.isPending}
                    >
                      {generateInsightsMutation.isPending ? (
                        <Loader2 size={12} className="animate-spin" />
                      ) : (
                        'Generate'
                      )}
                    </button>
                  </div>
                  {Array.isArray(insights) && insights.length > 0 ? (
                    <div className="space-y-2">
                      {insights.slice(0, 3).map((insight, idx) => (
                        <div
                          key={insight.id || idx}
                          className={cn(
                            'p-2 rounded-lg bg-dark-bg cursor-pointer hover:bg-dark-border transition-colors',
                            insight.actionable && 'border-l-2 border-accent-cyan'
                          )}
                          onClick={() => {
                            if (insight.actionable) {
                              sendMessage(`Help me with: ${insight.message}`)
                            }
                          }}
                        >
                          <p className="text-sm">{insight.message}</p>
                          {insight.actionable && (
                            <p className="text-xs text-accent-cyan mt-1">Click to take action</p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-4">
                      Click &quot;Generate&quot; to get personalized insights.
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
