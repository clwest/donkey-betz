/**
 * Session 931: Unified Command Center
 *
 * Merges Home, AI Assistant, and Human pages into one unified experience:
 * - Header: Greeting + While Away stats + Body Health badge
 * - Main: AI Chat interface (70%)
 * - Sidebar: 4 tabs - Context, Attention, Controls, Learning (30%)
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSearchParams, useNavigate } from 'react-router-dom'
import {
  assistantApi, userLearningApi, bodyApi, humanApi, homeApi, agentsApi, orchestrationApi
} from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { useUnifiedStore } from '@/stores/unifiedStore'
import { usePAStore } from '@/stores/paStore'
import PAConversationSidebar from '@/components/PAConversationSidebar'
import { ChatMarkdown } from '@/components/ChatMarkdown'
import AsyncJobTracker from '@/components/AsyncJobTracker'
import {
  Send, Mic, MicOff, Loader2, Bot, User, Copy, RefreshCw, Activity,
  ThumbsUp, ThumbsDown, Trash2, Sparkles, AlertCircle,
  CheckCircle, XCircle, Zap, MessageSquare,
  Heart, TrendingUp, Lightbulb, Palette,
  Bell, ClipboardList, Play, Check, X, Clock, HelpCircle,
  Volume2, VolumeX, Moon, Eye, Pause, Sliders,
  Bug, ChevronDown, ChevronUp,
  ExternalLink, Workflow, Database,
  PanelLeftClose, PanelLeftOpen, Plus, Brain,
  BarChart3, Shield, BookOpen, Terminal,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// ============================================================================
// Types
// ============================================================================

interface VoiceSettings {
  voiceInputEnabled: boolean
  voiceOutputEnabled: boolean
  autoPlayTTS: boolean
  voiceMode: boolean
}

type VoiceState = 'idle' | 'requesting_mic' | 'recording' | 'transcribing' | 'thinking' | 'speaking'

interface AsyncJob {
  task_id: string
  agent: string
  status: 'pending' | 'started' | 'success' | 'failed'
  started_at?: string
  finished_at?: string
  duration_ms?: number
  image_url?: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  tools_used?: string[]
  async_jobs?: AsyncJob[]
  feedback?: 'positive' | 'negative'
  source?: string
}

interface BootData {
  greeting: {
    user_name: string
    time_of_day: 'morning' | 'afternoon' | 'evening'
  }
  while_away: {
    spider_findings: number
    high_score_dreams: number
    initiatives_progressed: number
    pending_decisions: number
    hours_since_visit: number
    intelligence_desks_ready: number
  }
  quick_stats: {
    agents_active: number
    system_health: 'healthy' | 'degraded'
  }
}

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

interface SystemState {
  system_paused: boolean
  review_mode: boolean
  quiet_mode: boolean
  quiet_mode_until: string | null
  paused_agents: string[]
  ml_confidence_threshold: number
  auto_approve_threshold: number
}

type SidebarTab = 'context' | 'attention' | 'controls' | 'learning'

// ============================================================================
// Constants
// ============================================================================

const DEFAULT_VOICE_SETTINGS: VoiceSettings = {
  voiceInputEnabled: false,
  voiceOutputEnabled: false,
  autoPlayTTS: false,
  voiceMode: false,
}

const VOICE_SETTINGS_KEY = 'assistant-voice-settings'

const quickActions = [
  { label: 'Generate an image', prompt: 'Generate an image of a futuristic city at sunset' },
  { label: 'Check system status', prompt: 'What is the current system status?' },
  { label: 'Show opportunities', prompt: 'What opportunities are available?' },
  { label: 'Create content', prompt: 'Help me create a blog post about AI' },
  { label: 'Analyze trends', prompt: 'What are the latest trending topics?' },
]

// ============================================================================
// Utility Functions
// ============================================================================

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

// ============================================================================
// Sub-Components
// ============================================================================

// Compact header with greeting and stats
function CommandHeader({
  bootData,
  bodyHealthScore,
  bodySystems,
  showWhileAway,
  setShowWhileAway,
}: {
  bootData?: BootData
  bodyHealthScore: number
  bodySystems: Record<string, { status?: string }>
  showWhileAway: boolean
  setShowWhileAway: (show: boolean) => void
}) {
  const greeting = bootData?.greeting
  const whileAway = bootData?.while_away
  const stats = bootData?.quick_stats

  const timeGreeting = greeting ? {
    morning: 'Good morning',
    afternoon: 'Good afternoon',
    evening: 'Good evening',
  }[greeting.time_of_day] : 'Welcome'

  const hasActivity = whileAway && (
    whileAway.spider_findings > 0 ||
    whileAway.high_score_dreams > 0 ||
    whileAway.initiatives_progressed > 0
  )

  return (
    <div className="border-b border-dark-border pb-3 mb-4">
      <div className="flex items-center justify-between">
        {/* Left: Greeting */}
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold text-white">
            {timeGreeting}{greeting ? `, ${greeting.user_name}` : ''}
          </h1>
          {stats && (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              {stats.system_health === 'healthy' ? (
                <CheckCircle size={14} className="text-accent-green" />
              ) : (
                <AlertCircle size={14} className="text-accent-amber" />
              )}
              <span>{stats.agents_active} agents</span>
            </div>
          )}
        </div>

        {/* Right: Body Health + While Away Toggle */}
        <div className="flex items-center gap-3">
          {/* Body Health Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-dark-card border border-dark-border">
            <Heart
              size={16}
              className={cn(
                'animate-pulse',
                bodyHealthScore >= 80 ? 'text-accent-green' :
                bodyHealthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
              )}
              fill="currentColor"
            />
            <span className={cn(
              'text-sm font-medium',
              bodyHealthScore >= 80 ? 'text-accent-green' :
              bodyHealthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
            )}>
              {bodyHealthScore.toFixed(0)}%
            </span>
            <div className="flex items-center gap-0.5 text-xs ml-1" title="Body Systems">
              <span>{bodySystems.heart?.status === 'healthy' ? '❤️' : '🖤'}</span>
              <span>{bodySystems.lungs?.status === 'healthy' ? '🫁' : '💨'}</span>
              <span>{bodySystems.spine?.status === 'aligned' ? '🦴' : '⚠️'}</span>
            </div>
          </div>

          {/* While Away Toggle */}
          {hasActivity && whileAway && whileAway.hours_since_visit >= 1 && (
            <button
              onClick={() => setShowWhileAway(!showWhileAway)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary-600/20 text-primary-400 hover:bg-primary-600/30 transition-colors"
            >
              <Bug size={14} />
              <span className="text-sm">
                {whileAway.spider_findings + whileAway.high_score_dreams + whileAway.initiatives_progressed} updates
              </span>
              {showWhileAway ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </div>
      </div>

      {/* While Away Expanded */}
      {showWhileAway && hasActivity && whileAway && (
        <div className="mt-3 flex flex-wrap gap-2">
          {whileAway.spider_findings > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-400/10">
              <Bug size={14} className="text-blue-400" />
              <span className="text-blue-400 font-medium">{whileAway.spider_findings}</span>
              <span className="text-gray-400 text-sm">findings</span>
            </div>
          )}
          {whileAway.high_score_dreams > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-yellow-400/10">
              <Lightbulb size={14} className="text-yellow-400" />
              <span className="text-yellow-400 font-medium">{whileAway.high_score_dreams}</span>
              <span className="text-gray-400 text-sm">ideas</span>
            </div>
          )}
          {whileAway.initiatives_progressed > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-400/10">
              <TrendingUp size={14} className="text-green-400" />
              <span className="text-green-400 font-medium">{whileAway.initiatives_progressed}</span>
              <span className="text-gray-400 text-sm">initiatives moved</span>
            </div>
          )}
          {whileAway.intelligence_desks_ready > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-400/10">
              <Brain size={14} className="text-purple-400" />
              <span className="text-purple-400 font-medium">{whileAway.intelligence_desks_ready}</span>
              <span className="text-gray-400 text-sm">intel desks ready</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Toast notification
function Toast({ result, onClose }: { result: { type: 'success' | 'error'; message: string }; onClose: () => void }) {
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

// ============================================================================
// Session 971b D: "Now" Hub — Attention + Active Work + System Pulse
// ============================================================================

interface NowHubProps {
  pendingDecisions: PendingDecision[]
  activeWork: {
    initiatives: {
      active_count: number
      by_stage: Record<string, number>
      recent: Array<{ id: string; name: string; current_stage: number; completion_percentage: number }>
    }
    agent_executions: {
      last_24h: number
      completed: number
      failed: number
      top_agents: Array<{ name: string; count: number }>
    }
    workflows: { running: number }
  } | null
  bodyHealthScore: number
  agentsActive: number
  systemHealth: string
  onNavigate: (tab: string) => void
}

const STAGE_NAMES: Record<number, string> = { 1: 'Research', 2: 'Analysis', 3: 'Strategy', 4: 'Execution', 5: 'Review' }

function NowHub({ pendingDecisions, activeWork, bodyHealthScore, agentsActive, systemHealth, onNavigate }: NowHubProps) {
  const urgentItems = pendingDecisions.filter(d => d.urgency === 'critical' || d.urgency === 'high')
  const initCount = activeWork?.initiatives?.active_count || 0
  const execCount = activeWork?.agent_executions?.last_24h || 0
  const hasWork = initCount > 0 || execCount > 0

  return (
    <div className="grid grid-cols-3 gap-3 mb-4">
      {/* Attention Queue */}
      <button
        onClick={() => onNavigate('boardroom')}
        className="bg-dark-card border border-dark-border rounded-lg p-3 text-left hover:border-primary-500/30 transition-colors group"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-xs font-medium text-gray-400 uppercase tracking-wide">
            <Bell size={12} />
            Attention
          </div>
          {urgentItems.length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-xs font-medium bg-accent-red/20 text-accent-red">
              {urgentItems.length}
            </span>
          )}
        </div>
        {urgentItems.length > 0 ? (
          <div className="space-y-1">
            {urgentItems.slice(0, 2).map(item => (
              <div key={item.id} className="flex items-center gap-2 text-sm">
                <span className={cn(
                  'w-1.5 h-1.5 rounded-full shrink-0',
                  item.urgency === 'critical' ? 'bg-accent-red' : 'bg-accent-amber'
                )} />
                <span className="text-gray-300 truncate">{item.title}</span>
              </div>
            ))}
            {urgentItems.length > 2 && (
              <span className="text-xs text-gray-500">+{urgentItems.length - 2} more</span>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No urgent items</p>
        )}
      </button>

      {/* Active Work */}
      <button
        onClick={() => onNavigate('initiatives')}
        className="bg-dark-card border border-dark-border rounded-lg p-3 text-left hover:border-primary-500/30 transition-colors group"
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-xs font-medium text-gray-400 uppercase tracking-wide">
            <Workflow size={12} />
            Active Work
          </div>
          {hasWork && (
            <span className="px-1.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400">
              {initCount}
            </span>
          )}
        </div>
        {hasWork ? (
          <div className="space-y-1.5">
            {/* Initiative pipeline summary */}
            {initCount > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap">
                {Object.entries(activeWork?.initiatives?.by_stage || {}).sort(([a], [b]) => Number(a) - Number(b)).map(([stage, count]) => (
                  <span key={stage} className="text-[10px] px-1.5 py-0.5 rounded bg-primary-600/15 text-gray-400">
                    {STAGE_NAMES[Number(stage)] || `S${stage}`}: {count}
                  </span>
                ))}
              </div>
            )}
            {/* Agent execution activity */}
            {execCount > 0 && (
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">{execCount} agent runs (24h)</span>
                {(activeWork?.agent_executions?.failed || 0) > 0 && (
                  <span className="text-accent-red">{activeWork?.agent_executions?.failed} failed</span>
                )}
              </div>
            )}
            {/* Top recent initiative */}
            {(activeWork?.initiatives?.recent?.length || 0) > 0 && (
              <div className="flex items-center gap-2 text-sm">
                <Workflow size={12} className="text-blue-400 shrink-0" />
                <span className="text-gray-300 truncate text-xs">{activeWork!.initiatives.recent[0].name}</span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No active tasks</p>
        )}
      </button>

      {/* System Pulse */}
      <button
        onClick={() => onNavigate('system')}
        className="bg-dark-card border border-dark-border rounded-lg p-3 text-left hover:border-primary-500/30 transition-colors group"
      >
        <div className="flex items-center gap-2 text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
          <Activity size={12} />
          System Pulse
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Health</span>
            <span className={cn(
              'font-medium',
              bodyHealthScore >= 80 ? 'text-accent-green' :
              bodyHealthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
            )}>
              {bodyHealthScore.toFixed(0)}%
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Agents</span>
            <span className="text-gray-300">{agentsActive} active</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Status</span>
            <span className={cn(
              'font-medium',
              systemHealth === 'healthy' ? 'text-accent-green' : 'text-accent-amber'
            )}>
              {systemHealth === 'healthy' ? 'Healthy' : 'Degraded'}
            </span>
          </div>
        </div>
      </button>
    </div>
  )
}

// ============================================================================
// Session 1000: Intelligence Desks Panel
// ============================================================================

interface DeskData {
  status: 'ready' | 'no_data'
  generated_at?: string
  executive_summary?: string
  summary?: string
  top_plays?: Array<Record<string, unknown>>
  agents_run?: string[]
  elapsed_seconds?: number
}

interface DesksResponse {
  desks: Record<string, DeskData>
  total_agents_activated: number
}

const DESK_CONFIG = [
  { key: 'stocks', label: 'Stocks', icon: TrendingUp, color: 'green' },
  { key: 'sports', label: 'Sports', icon: BarChart3, color: 'amber' },
  { key: 'blockchain', label: 'Blockchain', icon: Shield, color: 'cyan' },
  { key: 'narrative', label: 'Narrative', icon: BookOpen, color: 'purple' },
] as const

const colorMap: Record<string, { bg: string; text: string; border: string; badge: string }> = {
  green:  { bg: 'bg-green-400/5',  text: 'text-green-400',  border: 'border-green-500/20',  badge: 'bg-green-500/20 text-green-400' },
  amber:  { bg: 'bg-amber-400/5',  text: 'text-amber-400',  border: 'border-amber-500/20',  badge: 'bg-amber-500/20 text-amber-400' },
  cyan:   { bg: 'bg-cyan-400/5',   text: 'text-cyan-400',   border: 'border-cyan-500/20',   badge: 'bg-cyan-500/20 text-cyan-400' },
  purple: { bg: 'bg-purple-400/5', text: 'text-purple-400', border: 'border-purple-500/20', badge: 'bg-purple-500/20 text-purple-400' },
}

function IntelligenceDesksPanel({
  desksData,
  onTrigger,
  isTriggerPending,
}: {
  desksData?: DesksResponse
  onTrigger: () => void
  isTriggerPending: boolean
}) {
  const [expanded, setExpanded] = useState(false)
  const desks = desksData?.desks || {}
  const readyCount = Object.values(desks).filter(d => d.status === 'ready').length

  // Auto-expand when desks have fresh data
  useEffect(() => {
    if (readyCount > 0) setExpanded(true)
  }, [readyCount])

  return (
    <div className="mb-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-left group"
      >
        <div className="flex items-center gap-2">
          <Brain size={14} className="text-purple-400" />
          <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
            Intelligence Desks
          </span>
          {readyCount > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400">
              {readyCount}/4
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); onTrigger() }}
            disabled={isTriggerPending}
            className="px-2 py-1 text-xs rounded bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 transition-colors disabled:opacity-50"
          >
            {isTriggerPending ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              'Run All Desks'
            )}
          </button>
          {expanded ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
        </div>
      </button>

      {expanded && (
        <div className="grid grid-cols-4 gap-3 mt-3">
          {DESK_CONFIG.map(({ key, label, icon: Icon, color }) => {
            const desk = desks[key]
            const colors = colorMap[color]
            const isReady = desk?.status === 'ready'
            const summaryText = desk?.executive_summary || desk?.summary || ''
            const agentCount = desk?.agents_run?.length || 0
            const generatedAt = desk?.generated_at ? new Date(desk.generated_at) : null

            return (
              <div
                key={key}
                className={cn(
                  'rounded-lg border p-3 transition-colors',
                  isReady ? `${colors.bg} ${colors.border}` : 'bg-dark-card border-dark-border opacity-60'
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon size={14} className={isReady ? colors.text : 'text-gray-500'} />
                    <span className={cn('text-sm font-medium', isReady ? colors.text : 'text-gray-500')}>
                      {label}
                    </span>
                  </div>
                  <span className={cn(
                    'px-1.5 py-0.5 rounded text-[10px] font-medium',
                    isReady ? colors.badge : 'bg-gray-700/50 text-gray-500'
                  )}>
                    {isReady ? 'Ready' : 'No Data'}
                  </span>
                </div>

                {isReady && summaryText && (
                  <p className="text-xs text-gray-400 line-clamp-3 mb-2">
                    {summaryText.slice(0, 150)}{summaryText.length > 150 ? '...' : ''}
                  </p>
                )}

                <div className="flex items-center justify-between">
                  {agentCount > 0 && (
                    <span className="text-[10px] text-gray-500">{agentCount} agents</span>
                  )}
                  {generatedAt && (
                    <span className="text-[10px] text-gray-500" title={generatedAt.toLocaleString()}>
                      {generatedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Main Component
// ============================================================================

export default function CommandCenterPage() {
  const [searchParams] = useSearchParams()
  const initialMessage = searchParams.get('message') || ''

  // Session 974: Shared PA store for conversation persistence
  const paMessages = usePAStore((s) => s.messages)
  const addPAMessage = usePAStore((s) => s.addMessage)
  const clearPAMessages = usePAStore((s) => s.clearMessages)
  const activeConversationId = usePAStore((s) => s.activeConversationId)
  const setActiveConversationId = usePAStore((s) => s.setActiveConversationId)
  const isChatSidebarOpen = usePAStore((s) => s.isSidebarOpen)
  const toggleChatSidebar = usePAStore((s) => s.toggleSidebar)
  const startNewConversation = usePAStore((s) => s.startNewConversation)
  const fetchConversations = usePAStore((s) => s.fetchConversations)

  // Adapt store messages to local Message type (timestamps are ISO strings in store)
  const messages: Message[] = paMessages.map((m) => ({
    ...m,
    timestamp: new Date(m.timestamp),
  }))

  // Chat state
  const [input, setInput] = useState(initialMessage)
  const [isRecording, setIsRecording] = useState(false)
  const [actionResult, setActionResult] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  // UI state
  const [showSidebar, setShowSidebar] = useState(true)
  const [sidebarTab, setSidebarTab] = useState<SidebarTab>('context')
  const [showWhileAway, setShowWhileAway] = useState(false)
  const [showVoiceSettings, setShowVoiceSettings] = useState(false)
  const [isDashboardCollapsed, setIsDashboardCollapsed] = useState(() => {
    try { return localStorage.getItem('cc_dashboard_collapsed') === 'true' } catch { return false }
  })

  // Voice state
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>(loadVoiceSettings)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null)
  const [voiceState, setVoiceState] = useState<VoiceState>('idle')
  const micPermissionRef = useRef(false)

  // Session 974b: Async polling state
  const [isPolling, setIsPolling] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const isNearBottomRef = useRef(true)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuthStore()
  const navigate = useNavigate()

  // Session 974b: Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // Session 1042: Persist dashboard collapsed state
  useEffect(() => {
    try { localStorage.setItem('cc_dashboard_collapsed', String(isDashboardCollapsed)) } catch {}
  }, [isDashboardCollapsed])

  // Session 948: Navigate to Workspace tabs
  const goToWorkspace = useCallback((tab?: string) => {
    if (tab) {
      navigate(`/workspace?tab=${tab}`)
    } else {
      navigate('/workspace')
    }
  }, [navigate])

  // Auto-send initial message if provided
  useEffect(() => {
    if (initialMessage && messages.length === 0) {
      sendMessage(initialMessage)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Persist voice settings
  useEffect(() => {
    saveVoiceSettings(voiceSettings)
  }, [voiceSettings])

  // Live sync: poll server for new messages added by Claude Code or other clients
  const setActiveConversation = usePAStore((s) => s.setActiveConversation)
  useQuery({
    queryKey: ['pa-conversation-sync', activeConversationId],
    queryFn: async () => {
      if (!activeConversationId) return null
      const response = await assistantApi.getConversation(activeConversationId)
      const data = response.data
      const currentCount = usePAStore.getState().messages.length
      if (data.success && data.messages.length > currentCount) {
        // Server has more messages — sync them in
        setActiveConversation(activeConversationId)
      }
      return data
    },
    enabled: !!activeConversationId && !isPolling,
    refetchInterval: voiceSettings.voiceMode ? 2000 : 5000,
    refetchIntervalInBackground: false,
  })

  const updateVoiceSetting = useCallback(<K extends keyof VoiceSettings>(key: K, value: VoiceSettings[K]) => {
    setVoiceSettings(prev => ({ ...prev, [key]: value }))
  }, [])

  const toggleVoiceMode = useCallback(() => {
    setVoiceSettings(prev => {
      const next = !prev.voiceMode
      return {
        ...prev,
        voiceMode: next,
        voiceInputEnabled: next,
        voiceOutputEnabled: next,
        autoPlayTTS: next,
      }
    })
  }, [])

  // ============================================================================
  // Session 948: Unified Store for shared data with Workspace
  // ============================================================================

  const fetchAttentionStats = useUnifiedStore((s) => s.fetchAttentionStats)
  const fetchRunningPilots = useUnifiedStore((s) => s.fetchRunningPilots)

  // Fetch unified store data on mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchAttentionStats()
      fetchRunningPilots()
    }
  }, [isAuthenticated, fetchAttentionStats, fetchRunningPilots])

  // ============================================================================
  // Queries
  // ============================================================================

  // Boot data (greeting, while away, stats)
  const { data: bootData } = useQuery({
    queryKey: ['home-boot'],
    queryFn: async () => {
      const response = await homeApi.boot()
      return response.data as BootData
    },
    refetchInterval: 60000,
  })

  // Body health
  const { data: bodyVitalsResponse } = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 60000,
  })

  // Pending decisions
  const { data: pendingDecisionsData } = useQuery({
    queryKey: ['pending-decisions'],
    queryFn: () => humanApi.attentionStream({ limit: 20 }),
    enabled: isAuthenticated,
    refetchInterval: 30000,
  })

  // Session 1000C: Combined active work for NowHub (initiatives + agent executions + workflows)
  const { data: activeWorkData } = useQuery({
    queryKey: ['active-work'],
    queryFn: () => orchestrationApi.activeWork(),
    enabled: isAuthenticated,
    refetchInterval: 30000,
  })

  // System control state
  const { data: controlData } = useQuery({
    queryKey: ['human-control'],
    queryFn: () => humanApi.control(),
    enabled: isAuthenticated && sidebarTab === 'controls',
  })

  // Agents list for control panel
  const { data: agentsData } = useQuery({
    queryKey: ['agents-list'],
    queryFn: () => agentsApi.list(),
    enabled: isAuthenticated && sidebarTab === 'controls',
  })

  // Learning data
  const { data: learningData } = useQuery({
    queryKey: ['assistant-learning'],
    queryFn: () => assistantApi.getLearning(),
    enabled: isAuthenticated && sidebarTab === 'learning',
  })

  const { data: velocityData } = useQuery({
    queryKey: ['learning-velocity'],
    queryFn: () => userLearningApi.getVelocity(),
    enabled: isAuthenticated && sidebarTab === 'learning',
  })

  const { data: preferencesData } = useQuery({
    queryKey: ['user-preferences'],
    queryFn: () => userLearningApi.getAllPreferences(),
    enabled: isAuthenticated && sidebarTab === 'learning',
  })

  // Attention items for context tab
  const { data: attentionData } = useQuery({
    queryKey: ['attention-items'],
    queryFn: () => assistantApi.getAttentionItems(),
    enabled: isAuthenticated,
  })

  // Session 1000: Intelligence Desks
  const { data: desksData } = useQuery({
    queryKey: ['intelligence-desks'],
    queryFn: async () => {
      const res = await homeApi.intelligenceDesks()
      return res.data as DesksResponse
    },
    refetchInterval: 300000,
  })

  const triggerDesksMutation = useMutation({
    mutationFn: () => homeApi.triggerDesks(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Intelligence desks triggered — results in a few minutes' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to trigger intelligence desks' })
    },
  })

  // ============================================================================
  // Mutations
  // ============================================================================

  // Chat — Session 974b: Async dispatch + polling via Celery
  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      assistantApi.paChat(message, { conversation_id: activeConversationId || undefined, source: 'web' }),
    onSuccess: (response) => {
      const taskId = response.data.task_id
      setIsPolling(true)

      pollRef.current = setInterval(async () => {
        try {
          const status = await assistantApi.paChatStatus(taskId)
          if (status.data.status === 'completed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)

            const content = status.data.content || 'No response'
            const toolRuns = status.data.tool_runs || []
            const toolNames = toolRuns.map((r: Record<string, unknown>) => r.tool as string)
            // Extract async jobs from tool results (image generation, etc.)
            const asyncJobs: AsyncJob[] = toolRuns
              .filter((r: Record<string, unknown>) => {
                const result = r.result as Record<string, unknown> | undefined
                return result?.mode === 'async' && result?.task_id
              })
              .map((r: Record<string, unknown>) => {
                const result = r.result as Record<string, unknown>
                return {
                  task_id: result.task_id as string,
                  agent: (result.agent as string) || 'unknown',
                  status: 'pending' as const,
                }
              })
            addPAMessage({ role: 'assistant', content, tools_used: toolNames, async_jobs: asyncJobs.length > 0 ? asyncJobs : undefined, source: 'pa' })

            if (status.data.conversation_id && !activeConversationId) {
              setActiveConversationId(status.data.conversation_id)
            }
            fetchConversations()

            if (voiceSettings.autoPlayTTS && voiceSettings.voiceOutputEnabled) {
              const msgId = Date.now().toString()
              setSpeakingMessageId(msgId)
              ttsMutation.mutate(content)
            }
          } else if (status.data.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            addPAMessage({
              role: 'assistant',
              content: status.data.error || 'Sorry, there was an error. Please try again.',
            })
          }
        } catch {
          if (pollRef.current) clearInterval(pollRef.current)
          pollRef.current = null
          setIsPolling(false)
          addPAMessage({
            role: 'assistant',
            content: 'Sorry, there was an error. Please try again.',
          })
        }
      }, 2000)
    },
    onError: () => {
      addPAMessage({
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
      })
    },
  })

  const isBusy = chatMutation.isPending || isPolling

  // Voice transcription
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

  // Voice chat (auto-send)
  const voiceChatMutation = useMutation({
    mutationFn: (audioBlob: Blob) => {
      setVoiceState('transcribing')
      return assistantApi.voiceChat(audioBlob)
    },
    onSuccess: (response) => {
      const userText = response.data.user_text
      if (userText) {
        addPAMessage({ role: 'user', content: userText })
      }

      setVoiceState('thinking')
      const assistantResponse = response.data.assistant_message
      if (assistantResponse) {
        const rawContent = assistantResponse.response || assistantResponse.message || 'No response'
        const content = typeof rawContent === 'string' ? rawContent : JSON.stringify(rawContent)
        addPAMessage({
          role: 'assistant',
          content,
          tools_used: assistantResponse.tools_used || [],
        })

        if (voiceSettings.autoPlayTTS && voiceSettings.voiceOutputEnabled) {
          setVoiceState('speaking')
          speakMessage(Date.now().toString(), content)
        } else {
          setVoiceState('idle')
        }
      } else {
        setVoiceState('idle')
      }
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to process voice' })
      setVoiceState('idle')
    },
  })

  // TTS
  const ttsMutation = useMutation({
    mutationFn: (text: string) => assistantApi.speak(text),
    onSuccess: (response) => {
      if (response.data.success && response.data.audio) {
        const audioData = `data:${response.data.audio_format || 'audio/mpeg'};base64,${response.data.audio}`
        if (audioRef.current) {
          audioRef.current.src = audioData
          audioRef.current.onended = () => {
            setIsSpeaking(false)
            setSpeakingMessageId(null)
            setVoiceState('idle')
          }
          audioRef.current.play()
          setIsSpeaking(true)
        }
      } else {
        setVoiceState('idle')
      }
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate speech' })
      setIsSpeaking(false)
      setSpeakingMessageId(null)
      setVoiceState('idle')
    },
  })

  // Feedback
  const updateMessageFeedback = usePAStore((s) => s.updateMessageFeedback)
  const feedbackMutation = useMutation({
    mutationFn: ({ messageId, rating }: { messageId: string; rating: 'positive' | 'negative' }) =>
      assistantApi.feedback(messageId, rating),
    onSuccess: (_, variables) => {
      updateMessageFeedback(variables.messageId, variables.rating)
      setActionResult({ type: 'success', message: 'Feedback recorded!' })
    },
  })

  // Reset chat — Session 974: Clears store + starts new conversation
  const resetMutation = useMutation({
    mutationFn: () => assistantApi.reset(),
    onSuccess: () => {
      clearPAMessages()
      startNewConversation()
      setActionResult({ type: 'success', message: 'Conversation cleared' })
      queryClient.invalidateQueries({ queryKey: ['assistant-learning'] })
    },
  })

  // Control mutations
  const quietModeMutation = useMutation({
    mutationFn: ({ enabled }: { enabled: boolean }) => humanApi.setQuietMode(enabled),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['human-control'] }),
  })

  const reviewModeMutation = useMutation({
    mutationFn: (enabled: boolean) => humanApi.setReviewMode(enabled),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['human-control'] }),
  })

  const thresholdMutation = useMutation({
    mutationFn: (threshold: number) => humanApi.adjustThreshold(threshold),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['human-control'] }),
  })

  // ============================================================================
  // Derived Data
  // ============================================================================

  const bodyVitals = bodyVitalsResponse?.data || null
  const bodyHealthScore = bodyVitals?.health_score || 0
  const bodySystems = bodyVitals?.systems || {}

  const pendingDecisions: PendingDecision[] = pendingDecisionsData?.data?.items || []
  const pendingCount = pendingDecisions.length
  const activeWork = activeWorkData?.data || null

  const systemState: SystemState = controlData?.data?.system_state || {
    system_paused: false,
    review_mode: false,
    quiet_mode: false,
    quiet_mode_until: null,
    paused_agents: [],
    ml_confidence_threshold: 0.6,
    auto_approve_threshold: 0.85,
  }

  const agentsList = agentsData?.data?.agents || []
  const attentionItems = attentionData?.data?.items || []
  const learningSummary = learningData?.data || {}
  const velocity = velocityData?.data || {}
  const userPreferences = preferencesData?.data?.preferences || preferencesData?.data || []

  // ============================================================================
  // Handlers
  // ============================================================================

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Track whether user is near the bottom of the chat
  useEffect(() => {
    const container = chatContainerRef.current
    if (!container) return
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container
      isNearBottomRef.current = scrollHeight - scrollTop - clientHeight < 80
    }
    container.addEventListener('scroll', handleScroll, { passive: true })
    return () => container.removeEventListener('scroll', handleScroll)
  }, [])

  // Only auto-scroll when user is already near the bottom
  useEffect(() => {
    if (isNearBottomRef.current) {
      scrollToBottom()
    }
  }, [messages])

  useEffect(() => {
    if (actionResult) {
      const timer = setTimeout(() => setActionResult(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [actionResult])

  // Audio end handler
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

  const sendMessage = useCallback((messageText?: string) => {
    const text = messageText || input
    if (!text.trim() || isBusy) return

    addPAMessage({ role: 'user', content: text })
    setInput('')
    chatMutation.mutate(text)
  }, [input, isBusy, chatMutation, addPAMessage])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startRecording = async () => {
    if (isRecording) return // guard double-start
    try {
      setVoiceState('requesting_mic')
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true }
      })
      micPermissionRef.current = true

      // Prefer webm/opus, fall back to webm, then default
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : undefined
      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType || 'audio/webm' })
        stream.getTracks().forEach((track) => track.stop())
        if (audioBlob.size > 0) {
          if (voiceSettings.voiceInputEnabled || voiceSettings.voiceMode) {
            voiceChatMutation.mutate(audioBlob)
          } else {
            transcribeMutation.mutate(audioBlob)
          }
        } else {
          setVoiceState('idle')
        }
      }

      mediaRecorder.start()
      setIsRecording(true)
      setVoiceState('recording')
    } catch (error) {
      console.error('Failed to start recording:', error)
      setActionResult({ type: 'error', message: 'Microphone access denied or unavailable' })
      setVoiceState('idle')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      // voiceState transitions to 'transcribing' in voiceChatMutation.mutationFn
    }
  }

  const speakMessage = useCallback((messageId: string, text: string) => {
    if (isSpeaking && speakingMessageId === messageId) {
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
    const userMessage = messages[messageIndex - 1]
    if (userMessage && userMessage.role === 'user') {
      // Can't slice store messages directly, so just re-send
      chatMutation.mutate(userMessage.content)
    }
  }

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <CommandHeader
        bootData={bootData}
        bodyHealthScore={bodyHealthScore}
        bodySystems={bodySystems}
        showWhileAway={showWhileAway}
        setShowWhileAway={setShowWhileAway}
      />

      {/* Session 1042: Collapsible dashboard — click to toggle, gives chat more space */}
      {isDashboardCollapsed ? (
        <button
          onClick={() => setIsDashboardCollapsed(false)}
          className="flex items-center justify-between px-3 py-1.5 mb-2 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors group"
        >
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span className="flex items-center gap-1.5">
              <Bell size={11} />
              <span className="text-gray-300 font-medium">{pendingDecisions.filter(d => d.urgency === 'critical' || d.urgency === 'high').length}</span> attention
            </span>
            <span className="flex items-center gap-1.5">
              <Workflow size={11} />
              <span className="text-gray-300 font-medium">{activeWork?.initiatives?.active_count || 0}</span> active
            </span>
            <span className="flex items-center gap-1.5">
              <Activity size={11} />
              <span className={cn(
                'font-medium',
                bodyHealthScore >= 80 ? 'text-accent-green' : bodyHealthScore >= 50 ? 'text-accent-amber' : 'text-accent-red'
              )}>{bodyHealthScore.toFixed(0)}%</span> health
            </span>
          </div>
          <ChevronDown size={14} className="text-gray-500 group-hover:text-gray-300" />
        </button>
      ) : (
        <>
          <div className="flex items-center justify-end mb-1">
            <button
              onClick={() => setIsDashboardCollapsed(true)}
              className="flex items-center gap-1 px-2 py-0.5 text-[10px] text-gray-500 hover:text-gray-300 rounded hover:bg-dark-border transition-colors"
              title="Collapse dashboard to give chat more space"
            >
              <ChevronUp size={12} />
              Collapse
            </button>
          </div>
          {/* Session 971b D: "Now" Hub — Attention + Active Work + Pulse */}
          <NowHub
            pendingDecisions={pendingDecisions}
            activeWork={activeWork}
            bodyHealthScore={bodyHealthScore}
            agentsActive={bootData?.quick_stats?.agents_active || 0}
            systemHealth={bootData?.quick_stats?.system_health || 'healthy'}
            onNavigate={goToWorkspace}
          />

          {/* Session 1000: Intelligence Desks Panel */}
          <IntelligenceDesksPanel
            desksData={desksData}
            onTrigger={() => triggerDesksMutation.mutate()}
            isTriggerPending={triggerDesksMutation.isPending}
          />
        </>
      )}

      <div className="flex flex-1 gap-4 overflow-hidden">
        {/* Session 974: Conversation Sidebar */}
        {isChatSidebarOpen && (
          <PAConversationSidebar variant="panel" />
        )}

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Chat Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <button
                onClick={toggleChatSidebar}
                className="p-1.5 rounded-md hover:bg-dark-border text-gray-400 hover:text-white transition-colors"
                title={isChatSidebarOpen ? 'Hide conversations' : 'Show conversations'}
              >
                {isChatSidebarOpen ? <PanelLeftClose size={16} /> : <PanelLeftOpen size={16} />}
              </button>
              <div className="h-9 w-9 rounded-lg bg-primary-600/20 flex items-center justify-center">
                <Bot size={18} className="text-primary-400" />
              </div>
              <div>
                <h2 className="font-medium text-sm">AI Assistant</h2>
                <p className="text-xs text-gray-500">GPT-5-mini</p>
              </div>
            </div>
            <div className="flex gap-2">
              {/* Session 974: New Chat */}
              <button
                className="btn btn-sm btn-secondary"
                onClick={() => startNewConversation()}
                title="New Chat"
              >
                <Plus size={14} />
              </button>

              {/* Voice Mode Toggle */}
              <button
                className={cn(
                  'btn btn-sm gap-1.5 transition-all',
                  voiceSettings.voiceMode
                    ? 'bg-accent-green/20 text-accent-green border-accent-green/40 hover:bg-accent-green/30'
                    : 'btn-secondary'
                )}
                onClick={toggleVoiceMode}
                title={voiceSettings.voiceMode ? 'Disable Voice Mode' : 'Enable Voice Mode'}
              >
                {voiceSettings.voiceMode ? <Volume2 size={14} /> : <VolumeX size={14} />}
                <span className="text-xs font-medium">Voice {voiceSettings.voiceMode ? 'On' : 'Off'}</span>
              </button>

              {/* Voice State Indicator */}
              {voiceSettings.voiceMode && voiceState !== 'idle' && (
                <div className={cn(
                  'flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium',
                  voiceState === 'recording' && 'bg-accent-red/20 text-accent-red animate-pulse',
                  voiceState === 'requesting_mic' && 'bg-accent-amber/20 text-accent-amber',
                  voiceState === 'transcribing' && 'bg-primary-600/20 text-primary-400',
                  voiceState === 'thinking' && 'bg-primary-600/20 text-primary-400',
                  voiceState === 'speaking' && 'bg-accent-green/20 text-accent-green',
                )}>
                  {voiceState === 'recording' && <><Mic size={12} /> Recording...</>}
                  {voiceState === 'requesting_mic' && <><Loader2 size={12} className="animate-spin" /> Mic...</>}
                  {voiceState === 'transcribing' && <><Loader2 size={12} className="animate-spin" /> Transcribing...</>}
                  {voiceState === 'thinking' && <><Loader2 size={12} className="animate-spin" /> Thinking...</>}
                  {voiceState === 'speaking' && <><Volume2 size={12} /> Speaking...</>}
                </div>
              )}

              {/* Advanced Voice Settings */}
              <div className="relative">
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => setShowVoiceSettings(!showVoiceSettings)}
                  title="Voice Settings"
                >
                  <Sliders size={14} />
                </button>

                {showVoiceSettings && (
                  <div className="absolute right-0 top-full mt-2 w-64 bg-dark-card border border-dark-border rounded-lg shadow-xl z-50 p-3">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-sm">Voice Settings</h4>
                      <button onClick={() => setShowVoiceSettings(false)} className="p-1 rounded hover:bg-dark-border">
                        <X size={12} />
                      </button>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs">Voice Input</span>
                        <button
                          onClick={() => updateVoiceSetting('voiceInputEnabled', !voiceSettings.voiceInputEnabled)}
                          className={cn(
                            'w-8 h-5 rounded-full transition-colors relative',
                            voiceSettings.voiceInputEnabled ? 'bg-primary-600' : 'bg-dark-border'
                          )}
                        >
                          <span className={cn(
                            'absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform',
                            voiceSettings.voiceInputEnabled ? 'translate-x-3.5' : 'translate-x-0.5'
                          )} />
                        </button>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs">Voice Output</span>
                        <button
                          onClick={() => updateVoiceSetting('voiceOutputEnabled', !voiceSettings.voiceOutputEnabled)}
                          className={cn(
                            'w-8 h-5 rounded-full transition-colors relative',
                            voiceSettings.voiceOutputEnabled ? 'bg-primary-600' : 'bg-dark-border'
                          )}
                        >
                          <span className={cn(
                            'absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform',
                            voiceSettings.voiceOutputEnabled ? 'translate-x-3.5' : 'translate-x-0.5'
                          )} />
                        </button>
                      </div>
                      {voiceSettings.voiceOutputEnabled && (
                        <div className="flex items-center justify-between pl-3 border-l-2 border-primary-600/30">
                          <span className="text-xs">Auto-Play</span>
                          <button
                            onClick={() => updateVoiceSetting('autoPlayTTS', !voiceSettings.autoPlayTTS)}
                            className={cn(
                              'w-8 h-5 rounded-full transition-colors relative',
                              voiceSettings.autoPlayTTS ? 'bg-accent-green' : 'bg-dark-border'
                            )}
                          >
                            <span className={cn(
                              'absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform',
                              voiceSettings.autoPlayTTS ? 'translate-x-3.5' : 'translate-x-0.5'
                            )} />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <button
                className="btn btn-sm btn-secondary"
                onClick={() => setShowSidebar(!showSidebar)}
              >
                {showSidebar ? 'Hide' : 'Show'} Panel
              </button>
              <button
                className="btn btn-sm btn-secondary text-accent-red"
                onClick={() => { resetMutation.mutate(); stopSpeaking(); }}
                disabled={resetMutation.isPending || messages.length === 0}
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>

          {/* Conversation ID */}
          {activeConversationId && (
            <div className="flex items-center gap-2 px-3 py-1 text-xs text-gray-500">
              <span className="font-mono truncate">{activeConversationId}</span>
              <button
                onClick={() => navigator.clipboard.writeText(activeConversationId)}
                className="p-0.5 rounded hover:bg-dark-border"
                title="Copy conversation ID"
              >
                <Copy size={10} />
              </button>
            </div>
          )}

          {/* Messages */}
          <div ref={chatContainerRef} className="flex-1 overflow-auto space-y-3 pb-3">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Bot size={40} className="mb-3 opacity-50" />
                <p className="text-lg mb-1">How can I help you today?</p>
                {pendingCount > 0 && (
                  <p className="text-sm mb-4">
                    <span className="text-accent-amber font-medium">{pendingCount} items</span> need your attention
                  </p>
                )}

                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-w-xl">
                  {pendingCount > 0 && (
                    <button
                      onClick={() => sendMessage('What needs my attention?')}
                      className="p-2.5 rounded-lg border border-accent-amber/50 bg-accent-amber/10 hover:bg-accent-amber/20 transition-colors text-left col-span-2 md:col-span-3"
                    >
                      <div className="flex items-center gap-2">
                        <Bell size={14} className="text-accent-amber" />
                        <span className="text-sm text-white">Review {pendingCount} pending items</span>
                      </div>
                    </button>
                  )}
                  {quickActions.map((action) => (
                    <button
                      key={action.label}
                      onClick={() => sendMessage(action.prompt)}
                      className="p-2.5 rounded-lg border border-dark-border hover:border-primary-500 hover:bg-primary-500/10 transition-colors text-left"
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
                    'flex gap-2',
                    message.source === 'claude-code' ? 'justify-start' : message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {/* Avatar: PA (bot), Claude Code (terminal), or none for user */}
                  {message.role === 'assistant' && message.source !== 'claude-code' && (
                    <div className="h-7 w-7 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                      <Bot size={14} className="text-primary-400" />
                    </div>
                  )}
                  {message.source === 'claude-code' && (
                    <div className="h-7 w-7 rounded-full bg-emerald-600/20 flex items-center justify-center flex-shrink-0">
                      <Terminal size={14} className="text-emerald-400" />
                    </div>
                  )}

                  <div className={cn('max-w-[75%] group', message.role === 'user' && message.source !== 'claude-code' && 'order-first')}>
                    <div className={cn(
                      'rounded-lg px-3 py-2 text-sm',
                      message.source === 'claude-code'
                        ? 'bg-emerald-900/30 border border-emerald-500/20'
                        : message.role === 'user'
                          ? 'bg-primary-600 text-white'
                          : 'bg-dark-card border border-dark-border'
                    )}>
                      {message.role === 'assistant' ? (
                        <ChatMarkdown content={message.content} />
                      ) : (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      )}
                      {message.source === 'claude-code' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono mt-1 inline-block">
                          Claude Code
                        </span>
                      )}
                      {message.source === 'mobile' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 font-mono mt-1 inline-block">
                          Mobile
                        </span>
                      )}
                      {message.source === 'discord' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-mono mt-1 inline-block">
                          Discord
                        </span>
                      )}
                      {message.source && !['web', 'web-dock', 'pa', 'claude-code', 'mobile', 'discord'].includes(message.source) && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-mono mt-1 inline-block">
                          via {message.source}
                        </span>
                      )}
                      {message.tools_used && message.tools_used.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-dark-border/50">
                          {message.tools_used.map((tool) => (
                            <span key={tool} className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400">
                              {tool}
                            </span>
                          ))}
                        </div>
                      )}
                      {message.async_jobs && message.async_jobs.length > 0 && (
                        <AsyncJobTracker jobs={message.async_jobs} />
                      )}
                    </div>

                    {/* Message actions */}
                    <div className={cn(
                      'flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity',
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    )}>
                      <span className="text-xs text-gray-500 mr-1">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {message.role === 'assistant' && (
                        <>
                          {voiceSettings.voiceOutputEnabled && (
                            <button
                              onClick={() => speakMessage(message.id, message.content)}
                              className={cn('p-1 rounded hover:bg-dark-border', speakingMessageId === message.id && 'bg-primary-500/20')}
                              disabled={ttsMutation.isPending && speakingMessageId !== message.id}
                            >
                              {ttsMutation.isPending && speakingMessageId === message.id ? (
                                <Loader2 size={12} className="animate-spin text-primary-400" />
                              ) : speakingMessageId === message.id && isSpeaking ? (
                                <VolumeX size={12} className="text-primary-400" />
                              ) : (
                                <Volume2 size={12} className="text-gray-400" />
                              )}
                            </button>
                          )}
                          <button onClick={() => copyMessage(message.content)} className="p-1 rounded hover:bg-dark-border">
                            <Copy size={12} className="text-gray-400" />
                          </button>
                          <button
                            onClick={() => regenerateResponse(index)}
                            className="p-1 rounded hover:bg-dark-border"
                            disabled={isBusy}
                          >
                            <RefreshCw size={12} className="text-gray-400" />
                          </button>
                          <button
                            onClick={() => feedbackMutation.mutate({ messageId: message.id, rating: 'positive' })}
                            className={cn('p-1 rounded hover:bg-dark-border', message.feedback === 'positive' && 'bg-accent-green/20')}
                          >
                            <ThumbsUp size={12} className={message.feedback === 'positive' ? 'text-accent-green' : 'text-gray-400'} />
                          </button>
                          <button
                            onClick={() => feedbackMutation.mutate({ messageId: message.id, rating: 'negative' })}
                            className={cn('p-1 rounded hover:bg-dark-border', message.feedback === 'negative' && 'bg-accent-red/20')}
                          >
                            <ThumbsDown size={12} className={message.feedback === 'negative' ? 'text-accent-red' : 'text-gray-400'} />
                          </button>
                        </>
                      )}
                    </div>
                  </div>

                  {message.role === 'user' && (
                    <div className="h-7 w-7 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                      <User size={14} className="text-white" />
                    </div>
                  )}
                </div>
              ))
            )}

            {isBusy && (
              <div className="flex gap-2 justify-start">
                <div className="h-7 w-7 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                  <Bot size={14} className="text-primary-400" />
                </div>
                <div className="bg-dark-card border border-dark-border rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-3 w-3 animate-spin text-primary-400" />
                    <span className="text-xs text-gray-400">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-dark-border pt-3">
            <div className="flex gap-2">
              <button
                className={cn(
                  'btn btn-sm select-none touch-none',
                  isRecording ? 'btn-primary animate-pulse' :
                  voiceSettings.voiceMode ? 'btn-secondary ring-2 ring-accent-green/50' :
                  voiceSettings.voiceInputEnabled ? 'btn-secondary ring-2 ring-primary-500/50' : 'btn-secondary'
                )}
                // Push-to-talk in Voice Mode: hold to record, release to stop
                onPointerDown={voiceSettings.voiceMode && !isRecording ? (e) => { e.preventDefault(); startRecording() } : undefined}
                onPointerUp={voiceSettings.voiceMode && isRecording ? () => stopRecording() : undefined}
                onPointerLeave={voiceSettings.voiceMode && isRecording ? () => stopRecording() : undefined}
                onPointerCancel={voiceSettings.voiceMode && isRecording ? () => stopRecording() : undefined}
                // Click toggle when Voice Mode is off
                onClick={!voiceSettings.voiceMode ? (isRecording ? stopRecording : startRecording) : undefined}
                disabled={transcribeMutation.isPending || voiceChatMutation.isPending || voiceState === 'transcribing' || voiceState === 'thinking'}
                title={voiceSettings.voiceMode ? 'Hold to talk' : (isRecording ? 'Stop recording' : 'Start recording')}
              >
                {(voiceState === 'transcribing' || voiceState === 'thinking') ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : isRecording ? (
                  <MicOff size={16} className="text-accent-red" />
                ) : (
                  <Mic size={16} />
                )}
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={isRecording ? 'Recording...' : 'Type your message...'}
                className="input flex-1 text-sm"
                disabled={isBusy || isRecording || voiceChatMutation.isPending}
              />
              <button
                onClick={() => sendMessage()}
                disabled={isBusy || !input.trim() || voiceChatMutation.isPending}
                className="btn btn-sm btn-primary"
              >
                {isBusy ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        {showSidebar && (
          <div className="w-72 flex flex-col overflow-hidden border-l border-dark-border pl-4">
            {/* Sidebar Tabs */}
            <div className="flex gap-1 mb-3 p-1 bg-dark-bg rounded-lg">
              {[
                { id: 'context', icon: Bot, label: 'Context' },
                { id: 'attention', icon: Bell, label: 'Attention', badge: pendingCount },
                { id: 'controls', icon: Sliders, label: 'Controls' },
                { id: 'learning', icon: Heart, label: 'Learning' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setSidebarTab(tab.id as SidebarTab)}
                  className={cn(
                    'flex-1 flex items-center justify-center gap-1 px-2 py-1.5 rounded-md text-xs font-medium transition-colors relative',
                    sidebarTab === tab.id ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'
                  )}
                >
                  <tab.icon size={12} />
                  {tab.badge && tab.badge > 0 && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-accent-amber text-[10px] flex items-center justify-center">
                      {tab.badge > 9 ? '9+' : tab.badge}
                    </span>
                  )}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-auto space-y-3">
              {/* Context Tab */}
              {sidebarTab === 'context' && (
                <>
                  {/* Suggestions */}
                  <div className="card p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles size={14} className="text-accent-cyan" />
                      <h3 className="font-medium text-sm">Quick Actions</h3>
                    </div>
                    <div className="space-y-1.5">
                      {quickActions.slice(0, 4).map((action) => (
                        <button
                          key={action.label}
                          onClick={() => sendMessage(action.prompt)}
                          className="w-full flex items-center gap-2 p-2 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors text-left"
                        >
                          <Zap size={12} className="text-accent-cyan flex-shrink-0" />
                          <span className="text-xs">{action.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Attention Items Preview */}
                  {attentionItems.length > 0 && (
                    <div className="card p-3">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle size={14} className="text-accent-amber" />
                        <h3 className="font-medium text-sm">Needs Attention</h3>
                        <span className="ml-auto px-1.5 py-0.5 text-xs rounded-full bg-accent-amber/20 text-accent-amber">
                          {attentionItems.length}
                        </span>
                      </div>
                      <div className="space-y-1.5">
                        {attentionItems.slice(0, 3).map((item: { id: string; title: string; severity: string }) => (
                          <div
                            key={item.id}
                            className="flex items-center gap-2 p-2 rounded-lg bg-dark-bg cursor-pointer hover:bg-dark-border"
                            onClick={() => sendMessage(`Tell me about: ${item.title}`)}
                          >
                            <span className={cn(
                              'h-2 w-2 rounded-full flex-shrink-0',
                              item.severity === 'critical' ? 'bg-accent-red' :
                              item.severity === 'warning' ? 'bg-accent-amber' : 'bg-accent-green'
                            )} />
                            <span className="text-xs truncate">{item.title}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Session Stats */}
                  <div className="card p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare size={14} className="text-gray-400" />
                      <h3 className="font-medium text-sm">This Session</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="text-center p-2 rounded-lg bg-dark-bg">
                        <p className="text-lg font-bold">{messages.filter(m => m.role === 'user').length}</p>
                        <p className="text-xs text-gray-400">Messages</p>
                      </div>
                      <div className="text-center p-2 rounded-lg bg-dark-bg">
                        <p className="text-lg font-bold">
                          {messages.filter(m => m.tools_used && m.tools_used.length > 0).length}
                        </p>
                        <p className="text-xs text-gray-400">Tool Uses</p>
                      </div>
                    </div>
                  </div>

                  {/* Session 948: Workspace Quick Links */}
                  <div className="card p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <ExternalLink size={14} className="text-primary-400" />
                      <h3 className="font-medium text-sm">Workspace</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-1.5">
                      <button
                        onClick={() => goToWorkspace('initiatives')}
                        className="flex items-center gap-2 p-2 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors text-left"
                      >
                        <Workflow size={12} className="text-accent-cyan flex-shrink-0" />
                        <span className="text-xs">Initiatives</span>
                      </button>
                      <button
                        onClick={() => goToWorkspace('boardroom')}
                        className="flex items-center gap-2 p-2 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors text-left"
                      >
                        <ClipboardList size={12} className="text-accent-amber flex-shrink-0" />
                        <span className="text-xs">Boardroom</span>
                      </button>
                      <button
                        onClick={() => goToWorkspace('content')}
                        className="flex items-center gap-2 p-2 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors text-left"
                      >
                        <Palette size={12} className="text-accent-purple flex-shrink-0" />
                        <span className="text-xs">Content</span>
                      </button>
                      <button
                        onClick={() => goToWorkspace('datasources')}
                        className="flex items-center gap-2 p-2 rounded-lg bg-dark-bg hover:bg-dark-border transition-colors text-left"
                      >
                        <Database size={12} className="text-accent-green flex-shrink-0" />
                        <span className="text-xs">Data</span>
                      </button>
                    </div>
                  </div>
                </>
              )}

              {/* Attention Tab */}
              {sidebarTab === 'attention' && (
                <>
                  {pendingDecisions.length > 0 ? (
                    <div className="space-y-2">
                      {/* Batch Actions */}
                      <div className="flex gap-1.5 mb-2">
                        <button
                          onClick={() => sendMessage('Auto-execute all low-risk decisions')}
                          className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded-lg bg-accent-green/20 text-accent-green hover:bg-accent-green/30"
                        >
                          <Play size={10} />
                          Auto
                        </button>
                        <button
                          onClick={() => sendMessage('Approve all low priority items')}
                          className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30"
                        >
                          <Check size={10} />
                          Batch
                        </button>
                        <button
                          onClick={() => sendMessage('Defer all medium priority items')}
                          className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs rounded-lg bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30"
                        >
                          <Clock size={10} />
                          Defer
                        </button>
                      </div>

                      {/* Decision Items */}
                      {pendingDecisions.map((item) => {
                        const urgencyEmoji = { critical: '🚨', high: '⚠️', medium: '📋', low: 'ℹ️' }[item.urgency] || '📋'
                        const hasML = item.ml_recommendation && item.ml_confidence && item.ml_confidence > 0.7

                        return (
                          <div
                            key={item.id}
                            className={cn(
                              "p-2 rounded-lg bg-dark-bg",
                              hasML && "border border-accent-green/30"
                            )}
                          >
                            <div className="flex items-start gap-2">
                              <span className="text-sm">{urgencyEmoji}</span>
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-medium truncate">{item.title}</p>
                                <div className="flex items-center gap-2 mt-0.5">
                                  <span className="text-[10px] text-gray-500">{item.item_type}</span>
                                  {hasML && (
                                    <span className="text-[10px] text-accent-green flex items-center gap-0.5">
                                      <Sparkles size={8} />
                                      {item.ml_recommendation} ({Math.round((item.ml_confidence || 0) * 100)}%)
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-1 mt-2">
                              <button
                                onClick={() => sendMessage(`Approve: ${item.title}`)}
                                className="flex-1 p-1 rounded text-[10px] bg-accent-green/20 text-accent-green hover:bg-accent-green/30"
                              >
                                <Check size={10} className="mx-auto" />
                              </button>
                              <button
                                onClick={() => sendMessage(`Reject: ${item.title}`)}
                                className="flex-1 p-1 rounded text-[10px] bg-accent-red/20 text-accent-red hover:bg-accent-red/30"
                              >
                                <X size={10} className="mx-auto" />
                              </button>
                              <button
                                onClick={() => sendMessage(`Tell me more about: ${item.title}`)}
                                className="flex-1 p-1 rounded text-[10px] bg-primary-500/20 text-primary-400 hover:bg-primary-500/30"
                              >
                                <HelpCircle size={10} className="mx-auto" />
                              </button>
                            </div>
                          </div>
                        )
                      })}

                      {/* Session 948: Link to Workspace Boardroom */}
                      <button
                        onClick={() => goToWorkspace('boardroom')}
                        className="w-full mt-3 flex items-center justify-center gap-2 px-3 py-2 text-xs rounded-lg border border-dark-border hover:border-primary-500 hover:bg-primary-500/10 transition-colors"
                      >
                        <ExternalLink size={12} />
                        View all in Boardroom
                      </button>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <CheckCircle size={24} className="mx-auto mb-2 opacity-50" />
                      <p className="text-xs">No pending decisions</p>
                      <button
                        onClick={() => goToWorkspace('boardroom')}
                        className="mt-3 flex items-center justify-center gap-1 mx-auto text-xs text-primary-400 hover:text-primary-300"
                      >
                        <ExternalLink size={10} />
                        Open Boardroom
                      </button>
                    </div>
                  )}
                </>
              )}

              {/* Controls Tab */}
              {sidebarTab === 'controls' && (
                <>
                  {/* System Controls */}
                  <div className="card p-3">
                    <h3 className="font-medium text-sm mb-3">System Controls</h3>
                    <div className="space-y-3">
                      {/* Quiet Mode */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Moon size={14} className="text-accent-purple" />
                          <span className="text-xs">Quiet Mode</span>
                        </div>
                        <button
                          onClick={() => quietModeMutation.mutate({ enabled: !systemState.quiet_mode })}
                          disabled={quietModeMutation.isPending}
                          className={cn(
                            'px-2 py-0.5 rounded-full text-xs font-medium',
                            systemState.quiet_mode ? 'bg-accent-purple text-white' : 'bg-dark-border text-gray-400'
                          )}
                        >
                          {systemState.quiet_mode ? 'ON' : 'OFF'}
                        </button>
                      </div>

                      {/* Review Mode */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Eye size={14} className="text-accent-amber" />
                          <span className="text-xs">Review Mode</span>
                        </div>
                        <button
                          onClick={() => reviewModeMutation.mutate(!systemState.review_mode)}
                          disabled={reviewModeMutation.isPending}
                          className={cn(
                            'px-2 py-0.5 rounded-full text-xs font-medium',
                            systemState.review_mode ? 'bg-accent-amber text-white' : 'bg-dark-border text-gray-400'
                          )}
                        >
                          {systemState.review_mode ? 'ON' : 'OFF'}
                        </button>
                      </div>

                      {/* ML Threshold */}
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Bot size={14} className="text-primary-400" />
                          <span className="text-xs">ML Threshold</span>
                          <span className="ml-auto text-xs font-medium">
                            {Math.round((systemState.ml_confidence_threshold || 0.6) * 100)}%
                          </span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={Math.round((systemState.ml_confidence_threshold || 0.6) * 100)}
                          onChange={(e) => thresholdMutation.mutate(parseInt(e.target.value) / 100)}
                          className="w-full accent-primary-500 h-1"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Agent Control (first 10) */}
                  <div className="card p-3">
                    <h3 className="font-medium text-sm mb-2">Agents</h3>
                    <div className="space-y-1 max-h-48 overflow-auto">
                      {agentsList.slice(0, 10).map((agent: { name: string }) => {
                        const isPaused = systemState.paused_agents?.includes(agent.name)
                        return (
                          <div key={agent.name} className="flex items-center justify-between p-1.5 rounded bg-dark-bg">
                            <div className="flex items-center gap-2">
                              <span className={cn('h-1.5 w-1.5 rounded-full', isPaused ? 'bg-accent-red' : 'bg-accent-green')} />
                              <span className="text-xs truncate max-w-[120px]">{agent.name}</span>
                            </div>
                            <button
                              onClick={() => sendMessage(isPaused ? `Resume agent ${agent.name}` : `Pause agent ${agent.name}`)}
                              className={cn(
                                'p-1 rounded text-[10px]',
                                isPaused ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-red/20 text-accent-red'
                              )}
                            >
                              {isPaused ? <Play size={10} /> : <Pause size={10} />}
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </>
              )}

              {/* Learning Tab */}
              {sidebarTab === 'learning' && (
                <>
                  {/* Learning Velocity */}
                  <div className="card p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp size={14} className="text-accent-green" />
                      <h3 className="font-medium text-sm">Learning</h3>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">Interactions</span>
                        <span className="text-xs font-medium">{velocity.total_interactions || learningSummary.total_interactions || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">Preferences</span>
                        <span className="text-xs font-medium">{velocity.preferences_count || learningSummary.preferences_count || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">Learning Rate</span>
                        <span className="text-xs font-medium text-accent-green">{velocity.learning_rate || '—'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Preferences */}
                  <div className="card p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Palette size={14} className="text-primary-400" />
                      <h3 className="font-medium text-sm">Your Preferences</h3>
                    </div>
                    {Array.isArray(userPreferences) && userPreferences.length > 0 ? (
                      <div className="space-y-1.5">
                        {userPreferences.slice(0, 4).map((pref: { id?: string; category: string; preference: string; confidence: number }, idx: number) => (
                          <div key={pref.id || idx} className="p-2 rounded-lg bg-dark-bg">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] text-primary-400">{pref.category}</span>
                              <span className="text-[10px] text-gray-500">{Math.round(pref.confidence * 100)}%</span>
                            </div>
                            <p className="text-xs mt-0.5 truncate">{pref.preference}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-400 text-center py-3">
                        Preferences will be learned as you use the system.
                      </p>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Hidden audio element */}
      <audio ref={audioRef} className="hidden" />

      {/* Click outside to close voice settings */}
      {showVoiceSettings && (
        <div className="fixed inset-0 z-40" onClick={() => setShowVoiceSettings(false)} />
      )}

      {/* Toast */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
