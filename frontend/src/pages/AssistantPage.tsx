import { useState, useRef, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { assistantApi, userLearningApi, legacyLearningApi, bodyApi, humanApi, type ToolRun } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import {
  Send, Mic, MicOff, Loader2, Bot, User, Copy, RefreshCw,
  ThumbsUp, ThumbsDown, Trash2, Sparkles, AlertCircle,
  ChevronRight, CheckCircle, XCircle, Zap, MessageSquare,
  Heart, TrendingUp, Lightbulb, Palette, Settings2, ExternalLink,
  Bell, ClipboardList, Play, Check, X, Clock, HelpCircle,
  Volume2, VolumeX, Settings, Wrench, Timer, Hash
} from 'lucide-react'
import { cn } from '@/lib/cn'
// Session 935: User Learning Components
import { GoalProgressDashboard } from '@/components/GoalProgressDashboard'
import { LearningInsightsPanel } from '@/components/LearningInsightsPanel'

// Session 894: Voice Mode Settings
interface VoiceSettings {
  voiceInputEnabled: boolean  // Auto-send after transcription
  voiceOutputEnabled: boolean // TTS for assistant responses
  autoPlayTTS: boolean        // Auto-play TTS when response arrives
}

const DEFAULT_VOICE_SETTINGS: VoiceSettings = {
  voiceInputEnabled: false,
  voiceOutputEnabled: false,
  autoPlayTTS: false,
}

const VOICE_SETTINGS_KEY = 'assistant-voice-settings'

function loadVoiceSettings(): VoiceSettings {
  try {
    const saved = localStorage.getItem(VOICE_SETTINGS_KEY)
    return saved ? { ...DEFAULT_VOICE_SETTINGS, ...JSON.parse(saved) } : DEFAULT_VOICE_SETTINGS
  } catch {
    return DEFAULT_VOICE_SETTINGS
  }
}

function saveVoiceSettings(settings: VoiceSettings): void {
  localStorage.setItem(VOICE_SETTINGS_KEY, JSON.stringify(settings))
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  tools_used?: string[]
  feedback?: 'positive' | 'negative'
  // Session 934: Enhanced fields from UnifiedPA
  tool_runs?: ToolRun[]
  trace_id?: string
  intent?: string
  routed_to?: string
  latency_ms?: number
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

// Session 796: Pending Decision interface
interface PendingDecision {
  id: string
  title: string
  summary: string
  urgency: 'critical' | 'high' | 'medium' | 'low'
  item_type: string
  source_agent: string
  ml_recommendation?: string
  ml_confidence?: number
  created_at: string
}

type SidebarTab = 'context' | 'learning'

// Session 796: Quick actions now include pending decisions
const baseQuickActions = [
  { label: 'Generate an image', prompt: 'Generate an image of a futuristic city at sunset' },
  { label: 'Check system status', prompt: 'What is the current system status?' },
  { label: 'Run agent cycle', prompt: 'Run an agent cycle now' },
  { label: 'Show opportunities', prompt: 'What opportunities are available?' },
  { label: 'Create content', prompt: 'Help me create a blog post about AI' },
  { label: 'Analyze trends', prompt: 'What are the latest trending topics?' },
]

// Session 934: Profile Completeness Card - shows how well the PA knows the user
function ProfileCompletenessCard() {
  const { data: completeness } = useQuery({
    queryKey: ['profile-completeness'],
    queryFn: async () => {
      // Try to get from PA context, fallback to cached value
      try {
        const response = await assistantApi.getPAContext()
        return response.data?.profile_completeness ?? 0
      } catch {
        return 0
      }
    },
    staleTime: 60000, // Cache for 1 minute
    refetchOnWindowFocus: false,
  })

  const percentage = completeness ?? 0
  const color = percentage >= 80 ? '#22c55e' : percentage >= 50 ? '#f59e0b' : '#ef4444'

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <User size={18} className="text-primary-400" />
          <h3 className="font-semibold">Profile Completeness</h3>
        </div>
        <span className="text-sm font-bold" style={{ color }}>
          {percentage}%
        </span>
      </div>
      <div className="h-2 rounded-full bg-dark-bg overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
      <p className="text-xs text-gray-400 mt-2">
        {percentage < 30 && 'Tell me about yourself to get personalized assistance'}
        {percentage >= 30 && percentage < 60 && 'Good start! Share more preferences for better results'}
        {percentage >= 60 && percentage < 80 && 'I know you well. Keep chatting to refine my understanding'}
        {percentage >= 80 && 'Excellent! I can provide highly personalized assistance'}
      </p>
    </div>
  )
}

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

  // Session 894: Voice Mode
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>(loadVoiceSettings)
  const [showVoiceSettings, setShowVoiceSettings] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Persist voice settings changes
  useEffect(() => {
    saveVoiceSettings(voiceSettings)
  }, [voiceSettings])

  const updateVoiceSetting = useCallback(<K extends keyof VoiceSettings>(key: K, value: VoiceSettings[K]) => {
    setVoiceSettings(prev => ({ ...prev, [key]: value }))
  }, [])

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
    queryFn: () => legacyLearningApi.getAllPreferences(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  const { data: styleEvolutionData } = useQuery({
    queryKey: ['style-evolution'],
    queryFn: () => legacyLearningApi.getStyleEvolution(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  const { data: insightsData } = useQuery({
    queryKey: ['learning-insights'],
    queryFn: () => legacyLearningApi.getInsights(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  const { data: velocityData } = useQuery({
    queryKey: ['learning-velocity'],
    queryFn: () => legacyLearningApi.getVelocity(),
    enabled: isAuthenticated && sidebarTab === 'learning',
    retry: false,
  })

  // Session 712: Body Health integration - Assistant aware of body state
  const { data: bodyVitalsResponse } = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 60000, // Refresh every 60 seconds
  })

  // Session 796: Pending decisions - Bridge Human Interface with PA
  const { data: pendingDecisionsData } = useQuery({
    queryKey: ['pending-decisions'],
    queryFn: () => humanApi.attentionStream({ limit: 10 }),
    enabled: isAuthenticated,
    refetchInterval: 30000, // Refresh every 30 seconds
    retry: false,
  })

  // Generate insights mutation
  const generateInsightsMutation = useMutation({
    mutationFn: () => legacyLearningApi.generateInsights(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'New insights generated!' })
      queryClient.invalidateQueries({ queryKey: ['learning-insights'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate insights' })
    },
  })

  // Session 934: Use UnifiedPA endpoint for enhanced visibility
  const chatMutation = useMutation({
    mutationFn: (message: string) => assistantApi.paChat(message),
    onSuccess: (response) => {
      const data = response.data
      // Ensure content is always a string
      const content = typeof data.content === 'string' ? data.content : JSON.stringify(data.content)

      const assistantMessage: Message = {
        id: data.trace_id || (Date.now() + 1).toString(),
        role: 'assistant',
        content,
        timestamp: new Date(),
        // Session 934: Include tool_runs with full details
        tool_runs: data.tool_runs || [],
        tools_used: data.tool_runs?.map(t => t.tool) || [],
        trace_id: data.trace_id,
        intent: data.intent || undefined,
        routed_to: data.routed_to || undefined,
        latency_ms: data.latency_ms,
      }
      setMessages((prev) => [...prev, assistantMessage])

      // Update profile completeness if available
      if (data.profile_completeness !== undefined) {
        queryClient.setQueryData(['profile-completeness'], data.profile_completeness)
      }

      // Session 894: Auto-play TTS if enabled
      if (voiceSettings.autoPlayTTS && voiceSettings.voiceOutputEnabled) {
        setSpeakingMessageId(assistantMessage.id)
        ttsMutation.mutate(content)
      }
    },
    onError: (error) => {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
      console.error('PA Chat error:', error)
    },
  })

  // Voice transcription mutation (transcribe only - puts text in input)
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

  // Session 894: Voice chat mutation (transcribe + auto-send to assistant)
  const voiceChatMutation = useMutation({
    mutationFn: (audioBlob: Blob) => assistantApi.voiceChat(audioBlob),
    onSuccess: (response) => {
      // Add user message from transcription
      const userText = response.data.user_text
      if (userText) {
        const userMessage: Message = {
          id: Date.now().toString(),
          role: 'user',
          content: userText,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, userMessage])
      }

      // Add assistant response
      const assistantResponse = response.data.assistant_message
      if (assistantResponse) {
        const rawContent = assistantResponse.response || assistantResponse.message || 'No response'
        const content = typeof rawContent === 'string' ? rawContent : JSON.stringify(rawContent)
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content,
          timestamp: new Date(),
          tools_used: assistantResponse.tools_used || [],
        }
        setMessages((prev) => [...prev, assistantMessage])

        // Auto-play TTS if enabled
        if (voiceSettings.autoPlayTTS && voiceSettings.voiceOutputEnabled) {
          speakMessage(assistantMessage.id, content)
        }
      }

      setActionResult({ type: 'success', message: 'Voice processed!' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to process voice' })
    },
  })

  // Session 894: TTS mutation (text-to-speech)
  const ttsMutation = useMutation({
    mutationFn: (text: string) => assistantApi.speak(text),
    onSuccess: (response, _variables) => {
      if (response.data.success && response.data.audio) {
        // Play the audio
        const audioData = `data:${response.data.audio_format || 'audio/mpeg'};base64,${response.data.audio}`
        if (audioRef.current) {
          audioRef.current.src = audioData
          audioRef.current.play()
          setIsSpeaking(true)
        }
      }
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate speech' })
      setIsSpeaking(false)
      setSpeakingMessageId(null)
    },
  })

  // Session 894: Speak a message
  const speakMessage = useCallback((messageId: string, text: string) => {
    if (isSpeaking && speakingMessageId === messageId) {
      // Stop current playback
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
      }
      setIsSpeaking(false)
      setSpeakingMessageId(null)
    } else {
      setSpeakingMessageId(messageId)
      ttsMutation.mutate(text)
    }
  }, [isSpeaking, speakingMessageId, ttsMutation])

  // Session 894: Handle audio end
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleEnded = () => {
      setIsSpeaking(false)
      setSpeakingMessageId(null)
    }

    audio.addEventListener('ended', handleEnded)
    return () => audio.removeEventListener('ended', handleEnded)
  }, [])

  // Feedback mutation - records to both conversation and user learning system
  const feedbackMutation = useMutation({
    mutationFn: async ({ messageId, rating }: { messageId: string; rating: 'positive' | 'negative' }) => {
      // Find the message to get agent info
      const message = messages.find(m => m.id === messageId)

      // Record conversation-level feedback
      await assistantApi.feedback(messageId, rating)

      // Session 935: Also record to user learning system if we have agent info
      if (message?.routed_to) {
        try {
          await userLearningApi.recordFeedback({
            agent_name: message.routed_to,
            rating: rating === 'positive' ? 1 : -1,
            execution_id: message.trace_id,
            task_description: message.intent || undefined,
            context_snapshot: {
              tools_used: message.tools_used,
              latency_ms: message.latency_ms,
            },
          })
        } catch (err) {
          // Don't fail the whole operation if learning feedback fails
          console.warn('Failed to record user learning feedback:', err)
        }
      }

      return { messageId, rating }
    },
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

  // Session 712: Body health data
  const bodyVitals = bodyVitalsResponse?.data || null
  const bodyHealthScore = bodyVitals?.health_score || 0
  const bodySystems = bodyVitals?.systems || {}

  // Session 796: Pending decisions data
  const pendingDecisions: PendingDecision[] = pendingDecisionsData?.data?.items || []
  const pendingCount = pendingDecisions.length

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
        // Session 894: Use voiceChat (auto-send) or transcribe based on settings
        if (voiceSettings.voiceInputEnabled) {
          voiceChatMutation.mutate(audioBlob)
        } else {
          transcribeMutation.mutate(audioBlob)
        }
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

  // Session 894: Stop any playing audio
  const stopSpeaking = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    setIsSpeaking(false)
    setSpeakingMessageId(null)
  }, [])

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
            {/* Session 894: Voice Mode Toggle */}
            <div className="relative">
              <button
                className={cn(
                  'btn text-sm flex items-center gap-1.5',
                  (voiceSettings.voiceInputEnabled || voiceSettings.voiceOutputEnabled)
                    ? 'btn-primary'
                    : 'btn-secondary'
                )}
                onClick={() => setShowVoiceSettings(!showVoiceSettings)}
                title="Voice Settings"
              >
                {voiceSettings.voiceOutputEnabled ? <Volume2 size={14} /> : <VolumeX size={14} />}
                Voice
                <Settings size={12} className="opacity-60" />
              </button>

              {/* Voice Settings Dropdown */}
              {showVoiceSettings && (
                <div className="absolute right-0 top-full mt-2 w-72 bg-dark-card border border-dark-border rounded-lg shadow-xl z-50 p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium">Voice Settings</h4>
                    <button
                      onClick={() => setShowVoiceSettings(false)}
                      className="p-1 rounded hover:bg-dark-border"
                    >
                      <X size={14} />
                    </button>
                  </div>

                  <div className="space-y-4">
                    {/* Voice Input Toggle */}
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">Voice Input Mode</p>
                        <p className="text-xs text-gray-400">Auto-send after recording</p>
                      </div>
                      <button
                        onClick={() => updateVoiceSetting('voiceInputEnabled', !voiceSettings.voiceInputEnabled)}
                        className={cn(
                          'w-10 h-6 rounded-full transition-colors relative',
                          voiceSettings.voiceInputEnabled ? 'bg-primary-600' : 'bg-dark-border'
                        )}
                      >
                        <span className={cn(
                          'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                          voiceSettings.voiceInputEnabled ? 'translate-x-5' : 'translate-x-1'
                        )} />
                      </button>
                    </div>

                    {/* Voice Output Toggle */}
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">Voice Output</p>
                        <p className="text-xs text-gray-400">Enable TTS for responses</p>
                      </div>
                      <button
                        onClick={() => updateVoiceSetting('voiceOutputEnabled', !voiceSettings.voiceOutputEnabled)}
                        className={cn(
                          'w-10 h-6 rounded-full transition-colors relative',
                          voiceSettings.voiceOutputEnabled ? 'bg-primary-600' : 'bg-dark-border'
                        )}
                      >
                        <span className={cn(
                          'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                          voiceSettings.voiceOutputEnabled ? 'translate-x-5' : 'translate-x-1'
                        )} />
                      </button>
                    </div>

                    {/* Auto-Play Toggle (only visible when output enabled) */}
                    {voiceSettings.voiceOutputEnabled && (
                      <div className="flex items-center justify-between pl-4 border-l-2 border-primary-600/30">
                        <div>
                          <p className="text-sm font-medium">Auto-Play</p>
                          <p className="text-xs text-gray-400">Speak responses automatically</p>
                        </div>
                        <button
                          onClick={() => updateVoiceSetting('autoPlayTTS', !voiceSettings.autoPlayTTS)}
                          className={cn(
                            'w-10 h-6 rounded-full transition-colors relative',
                            voiceSettings.autoPlayTTS ? 'bg-accent-green' : 'bg-dark-border'
                          )}
                        >
                          <span className={cn(
                            'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                            voiceSettings.autoPlayTTS ? 'translate-x-5' : 'translate-x-1'
                          )} />
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t border-dark-border">
                    <p className="text-xs text-gray-400">
                      {voiceSettings.voiceInputEnabled
                        ? '🎤 Recording will auto-send to assistant'
                        : '🎤 Recording will fill the input field'}
                    </p>
                  </div>
                </div>
              )}
            </div>

            <button
              className="btn btn-secondary text-sm"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              {showSidebar ? 'Hide' : 'Show'} Panel
            </button>
            <button
              className="btn btn-secondary text-sm text-accent-red"
              onClick={() => { resetMutation.mutate(); stopSpeaking(); }}
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
              {/* Session 796: Show pending decisions count in greeting */}
              {pendingCount > 0 ? (
                <p className="text-sm mb-6">
                  You have <span className="text-accent-amber font-medium">{pendingCount} item{pendingCount > 1 ? 's' : ''}</span> that need{pendingCount === 1 ? 's' : ''} your attention.
                </p>
              ) : (
                <p className="text-sm mb-6">Ask me anything about your platform...</p>
              )}

              {/* Session 796: Quick Actions with dynamic pending decisions */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-w-2xl">
                {/* Show Review Decisions first if there are pending items */}
                {pendingCount > 0 && (
                  <button
                    onClick={() => sendMessage('What needs my attention?')}
                    className="p-3 rounded-lg border border-accent-amber/50 bg-accent-amber/10 hover:border-accent-amber hover:bg-accent-amber/20 transition-colors text-left col-span-2 md:col-span-3"
                  >
                    <div className="flex items-center gap-2">
                      <Bell size={16} className="text-accent-amber" />
                      <p className="text-sm text-white">Review {pendingCount} pending decision{pendingCount > 1 ? 's' : ''}</p>
                    </div>
                  </button>
                )}
                {baseQuickActions.map((action) => (
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

                    {/* Session 934: Enhanced tool runs display */}
                    {message.tool_runs && message.tool_runs.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-dark-border space-y-1">
                        <div className="flex items-center gap-1 text-xs text-gray-400 mb-1">
                          <Wrench size={12} />
                          <span>Tools executed:</span>
                        </div>
                        {message.tool_runs.map((run, idx) => (
                          <div
                            key={`${run.tool}-${idx}`}
                            className={cn(
                              'flex items-center justify-between text-xs px-2 py-1 rounded',
                              run.ok ? 'bg-accent-green/10' : 'bg-accent-red/10'
                            )}
                          >
                            <div className="flex items-center gap-2">
                              {run.ok ? (
                                <CheckCircle size={12} className="text-accent-green" />
                              ) : (
                                <XCircle size={12} className="text-accent-red" />
                              )}
                              <span className={run.ok ? 'text-accent-green' : 'text-accent-red'}>
                                {run.tool}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                              <Timer size={10} />
                              <span>{run.latency_ms}ms</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Fallback: Simple tools_used display for legacy responses */}
                    {!message.tool_runs && message.tools_used && message.tools_used.length > 0 && (
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

                    {/* Session 934: Trace ID and routing info */}
                    {(message.trace_id || message.intent || message.latency_ms) && (
                      <div className="flex flex-wrap items-center gap-3 mt-2 pt-1 text-[10px] text-gray-500">
                        {message.trace_id && (
                          <span className="flex items-center gap-1" title="Trace ID for debugging">
                            <Hash size={10} />
                            {message.trace_id.slice(0, 12)}...
                          </span>
                        )}
                        {message.intent && (
                          <span className="px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400">
                            {message.intent}
                          </span>
                        )}
                        {message.routed_to && (
                          <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">
                            → {message.routed_to}
                          </span>
                        )}
                        {message.latency_ms && (
                          <span className="flex items-center gap-1">
                            <Timer size={10} />
                            {message.latency_ms}ms total
                          </span>
                        )}
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
                        {/* Session 894: Speaker button for TTS */}
                        {voiceSettings.voiceOutputEnabled && (
                          <button
                            onClick={() => speakMessage(message.id, message.content)}
                            className={cn(
                              'p-1 rounded hover:bg-dark-border',
                              speakingMessageId === message.id && 'bg-primary-500/20'
                            )}
                            title={speakingMessageId === message.id ? 'Stop speaking' : 'Speak this message'}
                            disabled={ttsMutation.isPending && speakingMessageId !== message.id}
                          >
                            {ttsMutation.isPending && speakingMessageId === message.id ? (
                              <Loader2 size={14} className="animate-spin text-primary-400" />
                            ) : speakingMessageId === message.id && isSpeaking ? (
                              <VolumeX size={14} className="text-primary-400" />
                            ) : (
                              <Volume2 size={14} className="text-gray-400" />
                            )}
                          </button>
                        )}
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
                isRecording ? 'btn-primary animate-pulse' :
                voiceSettings.voiceInputEnabled ? 'btn-secondary ring-2 ring-primary-500/50' : 'btn-secondary'
              )}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={transcribeMutation.isPending || voiceChatMutation.isPending}
              title={voiceSettings.voiceInputEnabled ? 'Voice mode: Auto-send enabled' : 'Click to record'}
            >
              {(transcribeMutation.isPending || voiceChatMutation.isPending) ? (
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
              placeholder={
                isRecording
                  ? voiceSettings.voiceInputEnabled
                    ? 'Recording... Will auto-send when stopped'
                    : 'Recording... Click mic to stop'
                  : voiceSettings.voiceInputEnabled
                    ? 'Voice mode active - speak or type...'
                    : 'Type your message...'
              }
              className="input flex-1"
              disabled={chatMutation.isPending || isRecording || voiceChatMutation.isPending}
            />
            <button
              onClick={() => sendMessage()}
              disabled={chatMutation.isPending || !input.trim() || voiceChatMutation.isPending}
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
            {voiceSettings.voiceInputEnabled
              ? 'Voice mode: Recording will auto-send to assistant'
              : 'Press Enter to send, Shift+Enter for new line'}
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
                {/* Session 712: Body Health Card - Assistant aware of body state */}
                {bodyVitals && (
                  <div className="card">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Heart
                          size={18}
                          className={cn(
                            'animate-pulse',
                            bodyHealthScore >= 80 ? 'text-accent-green' :
                            bodyHealthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
                          )}
                          fill="currentColor"
                        />
                        <h3 className="font-semibold">Body Health</h3>
                      </div>
                      <span className={cn(
                        'text-sm font-bold',
                        bodyHealthScore >= 80 ? 'text-accent-green' :
                        bodyHealthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
                      )}>
                        {(bodyHealthScore ?? 0).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-sm" title="Body Systems">
                        <span title={`Heart: ${bodySystems.heart?.status || 'unknown'}`}>
                          {bodySystems.heart?.status === 'healthy' ? '❤️' : '🖤'}
                        </span>
                        <span title={`Lungs: ${bodySystems.lungs?.status || 'unknown'}`}>
                          {bodySystems.lungs?.status === 'healthy' ? '🫁' : '💨'}
                        </span>
                        <span title={`Circulatory: ${bodySystems.circulatory?.status || 'unknown'}`}>
                          {bodySystems.circulatory?.status === 'flowing' ? '🩸' : '🧊'}
                        </span>
                        <span title={`Spine: ${bodySystems.spine?.status || 'unknown'}`}>
                          {bodySystems.spine?.status === 'aligned' ? '🦴' : '⚠️'}
                        </span>
                        <span title={`Immune: ${bodySystems.immune?.status || 'unknown'}`}>
                          {bodySystems.immune?.status === 'protected' ? '🛡️' : '🦠'}
                        </span>
                        <span title={`Digestive: ${bodySystems.digestive?.status || 'unknown'}`}>
                          {bodySystems.digestive?.status === 'healthy' ? '🍽️' : '🤢'}
                        </span>
                        <span title={`Muscular: ${bodySystems.muscular?.status || 'unknown'}`}>
                          {bodySystems.muscular?.status === 'strong' || bodySystems.muscular?.status === 'fit' ? '💪' : '😓'}
                        </span>
                      </div>
                      <a
                        href="/body-health"
                        className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300 transition-colors"
                      >
                        <span>Details</span>
                        <ExternalLink size={10} />
                      </a>
                    </div>
                  </div>
                )}

                {/* Session 934: Profile Completeness from UnifiedPA */}
                <ProfileCompletenessCard />

                {/* Session 796: Pending Decisions - Human Interface Bridge */}
                {pendingDecisions.length > 0 && (
                  <div className="card border-l-2 border-accent-amber">
                    <div className="flex items-center gap-2 mb-3">
                      <ClipboardList size={18} className="text-accent-amber" />
                      <h3 className="font-semibold">Pending Decisions</h3>
                      <span className="ml-auto px-2 py-0.5 text-xs rounded-full bg-accent-amber/20 text-accent-amber">
                        {pendingDecisions.length}
                      </span>
                    </div>

                    {/* Session 796: Batch Action Buttons */}
                    <div className="flex gap-2 mb-3">
                      <button
                        onClick={() => sendMessage('Auto-execute all low-risk decisions with high confidence')}
                        className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded-lg bg-accent-green/20 text-accent-green hover:bg-accent-green/30 transition-colors"
                        title="Auto-approve low-risk items with ML confidence ≥85%"
                      >
                        <Play size={12} />
                        Auto-Execute
                      </button>
                      <button
                        onClick={() => sendMessage('Approve all low priority items')}
                        className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
                        title="Batch approve all low priority items"
                      >
                        <Check size={12} />
                        Batch Low
                      </button>
                      <button
                        onClick={() => sendMessage('Defer all medium priority items until tomorrow')}
                        className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded-lg bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30 transition-colors"
                        title="Defer medium priority items"
                      >
                        <Clock size={12} />
                        Defer Med
                      </button>
                    </div>

                    <div className="space-y-2">
                      {pendingDecisions.slice(0, 5).map((item, idx) => {
                        const urgencyEmoji = {
                          critical: '🚨',
                          high: '⚠️',
                          medium: '📋',
                          low: 'ℹ️'
                        }[item.urgency] || '📋'

                        const hasMLRecommendation = item.ml_recommendation && item.ml_confidence && item.ml_confidence > 0.7

                        return (
                          <div
                            key={item.id}
                            className={cn(
                              "p-2 rounded-lg bg-dark-bg transition-colors",
                              hasMLRecommendation && "border border-accent-green/30"
                            )}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div
                                className="flex items-start gap-2 min-w-0 flex-1 cursor-pointer hover:opacity-80"
                                onClick={() => sendMessage(`Tell me more about decision ${idx + 1}: ${item.title}`)}
                              >
                                <span className="text-sm mt-0.5">{urgencyEmoji}</span>
                                <div className="min-w-0">
                                  <span className="text-sm block">{item.title.slice(0, 50)}{item.title.length > 50 ? '...' : ''}</span>
                                  <div className="flex items-center gap-2 mt-0.5">
                                    <span className="text-xs text-gray-500">{item.item_type}</span>
                                    {hasMLRecommendation && (
                                      <span className="text-xs text-accent-green flex items-center gap-1">
                                        <Sparkles size={10} />
                                        ML: {item.ml_recommendation} ({Math.round((item.ml_confidence || 0) * 100)}%)
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              {/* Quick Action Buttons */}
                              <div className="flex items-center gap-1 flex-shrink-0">
                                <button
                                  onClick={(e) => { e.stopPropagation(); sendMessage(`Approve decision ${idx + 1}: ${item.title}`) }}
                                  className="p-1 rounded hover:bg-accent-green/20 text-gray-400 hover:text-accent-green transition-colors"
                                  title="Approve"
                                >
                                  <Check size={14} />
                                </button>
                                <button
                                  onClick={(e) => { e.stopPropagation(); sendMessage(`Reject decision ${idx + 1}: ${item.title}`) }}
                                  className="p-1 rounded hover:bg-accent-red/20 text-gray-400 hover:text-accent-red transition-colors"
                                  title="Reject"
                                >
                                  <X size={14} />
                                </button>
                                <button
                                  onClick={(e) => { e.stopPropagation(); sendMessage(`Defer decision ${idx + 1}: ${item.title}`) }}
                                  className="p-1 rounded hover:bg-accent-amber/20 text-gray-400 hover:text-accent-amber transition-colors"
                                  title="Defer"
                                >
                                  <Clock size={14} />
                                </button>
                                <button
                                  onClick={(e) => { e.stopPropagation(); sendMessage(`Tell me more about decision ${idx + 1}: ${item.title}`) }}
                                  className="p-1 rounded hover:bg-primary-500/20 text-gray-400 hover:text-primary-400 transition-colors"
                                  title="More Info"
                                >
                                  <HelpCircle size={14} />
                                </button>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    <button
                      onClick={() => sendMessage('What needs my attention?')}
                      className="w-full mt-2 text-xs text-primary-400 hover:text-primary-300 py-1"
                    >
                      Review all {pendingDecisions.length} decisions →
                    </button>
                  </div>
                )}

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
                    {baseQuickActions.slice(0, 4).map((action) => (
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
                {/* Session 935: Goals Progress Dashboard */}
                <div className="card">
                  <GoalProgressDashboard compact maxItems={3} />
                </div>

                {/* Session 935: Learning Insights Panel */}
                <div className="card">
                  <LearningInsightsPanel compact />
                </div>

                {/* Legacy: Learning Velocity (kept for additional context) */}
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

                {/* Legacy: Insights with Generate button */}
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Lightbulb size={18} className="text-accent-cyan" />
                      <h3 className="font-semibold">Quick Insights</h3>
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

      {/* Session 894: Hidden audio element for TTS playback */}
      <audio ref={audioRef} className="hidden" />

      {/* Click outside to close voice settings */}
      {showVoiceSettings && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowVoiceSettings(false)}
        />
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
