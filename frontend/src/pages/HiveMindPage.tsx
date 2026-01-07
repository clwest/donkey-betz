/**
 * Session 715: Hive Mind Page
 *
 * Multi-agent collaborative sessions where all relevant agents
 * work together on a problem simultaneously.
 */

import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { hiveMindApi } from '@/lib/api'
import { useSystemEvents } from '@/hooks/useWebSocket'
import {
  Brain,
  Users,
  Play,
  Clock,
  CheckCircle,
  Loader2,
  AlertCircle,
  ChevronRight,
  ChevronDown,
  Sparkles,
  MessageSquare,
  RefreshCw,
  Eye,
  Lightbulb,
  Target,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { CompactBreadcrumb } from '@/components/Breadcrumb'

// ============================================================================
// Types
// ============================================================================

interface HiveMindSession {
  id: string
  question: string
  status: 'initializing' | 'gathering' | 'synthesizing' | 'completed' | 'failed'
  participant_count: number
  contribution_count: number
  created_at: string
  completed_at: string | null
}

interface SessionDetail {
  id: string
  question: string
  context: string
  status: string
  synthesis: string
  synthesis_summary: string
  created_at: string
  started_at: string | null
  completed_at: string | null
  contribution_count: number
  total_thinking_time: number
}

interface Contribution {
  id: string
  agent: {
    id: string
    name: string
    specialization: string
  }
  contribution: string
  key_points: string[]
  perspective_type: string
  confidence_score: number
  status: 'pending' | 'thinking' | 'completed' | 'failed'
  thinking_time: number
  created_at: string
  completed_at: string | null
}

interface PreviewAgent {
  id: string
  name: string
  specialization: string
  description: string
}

// ============================================================================
// Helper Functions
// ============================================================================

const formatTimestamp = (timestamp: string | null | undefined): string => {
  if (!timestamp) return 'Just now'
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) return 'Just now'
  return date.toLocaleString()
}

const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}m ${seconds % 60}s`
}

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'text-green-400'
    case 'gathering':
    case 'synthesizing':
      return 'text-yellow-400'
    case 'failed':
      return 'text-red-400'
    default:
      return 'text-gray-400'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-green-400" />
    case 'gathering':
    case 'synthesizing':
      return <Loader2 className="h-4 w-4 text-yellow-400 animate-spin" />
    case 'failed':
      return <AlertCircle className="h-4 w-4 text-red-400" />
    default:
      return <Clock className="h-4 w-4 text-gray-400" />
  }
}

// ============================================================================
// Components
// ============================================================================

function StartSessionForm({
  onStart,
  isStarting,
}: {
  onStart: (question: string, context: string, maxAgents: number) => void
  isStarting: boolean
}) {
  const [question, setQuestion] = useState('')
  const [context, setContext] = useState('')
  const [maxAgents, setMaxAgents] = useState(8)
  const [showPreview, setShowPreview] = useState(false)

  const { data: previewData, isFetching: isPreviewing } = useQuery({
    queryKey: ['hive-mind-preview', question, maxAgents],
    queryFn: () => hiveMindApi.preview({ question, max_agents: maxAgents }),
    enabled: showPreview && question.length > 10,
  })

  const previewAgents = (previewData?.data?.agents || []) as PreviewAgent[]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (question.trim()) {
      onStart(question, context, maxAgents)
      setQuestion('')
      setContext('')
      setShowPreview(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Question for the Hive Mind
        </label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a complex question that benefits from multiple perspectives..."
          className="w-full h-24 px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          disabled={isStarting}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Additional Context (optional)
        </label>
        <textarea
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Provide any additional context or constraints..."
          className="w-full h-16 px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          disabled={isStarting}
        />
      </div>

      <div className="flex items-center gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Max Agents
          </label>
          <select
            value={maxAgents}
            onChange={(e) => setMaxAgents(Number(e.target.value))}
            className="px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={isStarting}
          >
            {[4, 6, 8, 10, 12].map((n) => (
              <option key={n} value={n}>
                {n} agents
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1" />

        <button
          type="button"
          onClick={() => setShowPreview(!showPreview)}
          disabled={question.length < 10}
          className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors disabled:opacity-50"
        >
          <Eye className="h-4 w-4 inline mr-1" />
          Preview Agents
        </button>

        <button
          type="submit"
          disabled={!question.trim() || isStarting}
          className="btn-primary flex items-center gap-2"
        >
          {isStarting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Starting...
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              Activate Hive Mind
            </>
          )}
        </button>
      </div>

      {/* Agent Preview */}
      {showPreview && question.length > 10 && (
        <div className="p-4 bg-dark-bg border border-dark-border rounded-lg">
          <h4 className="text-sm font-medium text-gray-300 mb-3">
            Agents that will participate:
          </h4>
          {isPreviewing ? (
            <div className="flex items-center gap-2 text-gray-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading preview...
            </div>
          ) : previewAgents.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {previewAgents.map((agent) => (
                <div
                  key={agent.id}
                  className="px-3 py-1.5 bg-dark-card rounded-lg border border-dark-border"
                  title={agent.description}
                >
                  <span className="text-sm text-white">{agent.name}</span>
                  <span className="text-xs text-gray-500 ml-2">
                    {agent.specialization}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              No matching agents found. Try rephrasing your question.
            </p>
          )}
        </div>
      )}
    </form>
  )
}

function SessionCard({
  session,
  isSelected,
  onClick,
}: {
  session: HiveMindSession
  isSelected: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full p-4 text-left rounded-lg border transition-colors',
        isSelected
          ? 'bg-primary-900/30 border-primary-500'
          : 'bg-dark-card border-dark-border hover:border-gray-600'
      )}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-purple-500/20">
          <Brain className="h-5 w-5 text-purple-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-white font-medium truncate">{session.question}</p>
          <div className="flex items-center gap-3 mt-2 text-sm">
            <span className="flex items-center gap-1 text-gray-400">
              <Users className="h-3.5 w-3.5" />
              {session.participant_count} agents
            </span>
            <span className="flex items-center gap-1 text-gray-400">
              <MessageSquare className="h-3.5 w-3.5" />
              {session.contribution_count} contributions
            </span>
            <span className={cn('flex items-center gap-1', getStatusColor(session.status))}>
              {getStatusIcon(session.status)}
              {session.status}
            </span>
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-gray-500 flex-shrink-0" />
      </div>
    </button>
  )
}

function ContributionCard({ contribution }: { contribution: Contribution }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="p-4 bg-dark-card rounded-lg border border-dark-border">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-blue-500/20 flex-shrink-0">
          <Sparkles className="h-4 w-4 text-blue-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-white font-medium">{contribution.agent.name}</span>
              <span className="text-gray-500 text-sm ml-2">
                {contribution.agent.specialization}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {contribution.confidence_score > 0 && (
                <span className="text-xs text-gray-500">
                  {Math.round(contribution.confidence_score * 100)}% confidence
                </span>
              )}
              {getStatusIcon(contribution.status)}
            </div>
          </div>

          {contribution.status === 'completed' && (
            <>
              <p className="text-gray-300 text-sm mt-2 line-clamp-3">
                {contribution.contribution}
              </p>

              {contribution.key_points && contribution.key_points.length > 0 && (
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="flex items-center gap-1 text-sm text-primary-400 mt-2 hover:text-primary-300"
                >
                  {expanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                  {contribution.key_points.length} key points
                </button>
              )}

              {expanded && contribution.key_points && (
                <ul className="mt-2 space-y-1 pl-4">
                  {contribution.key_points.map((point, i) => (
                    <li key={i} className="text-sm text-gray-400 flex items-start gap-2">
                      <Lightbulb className="h-3.5 w-3.5 text-yellow-400 mt-0.5 flex-shrink-0" />
                      {point}
                    </li>
                  ))}
                </ul>
              )}

              {contribution.thinking_time > 0 && (
                <p className="text-xs text-gray-500 mt-2">
                  Thinking time: {formatDuration(contribution.thinking_time)}
                </p>
              )}
            </>
          )}

          {contribution.status === 'pending' && (
            <p className="text-gray-500 text-sm mt-2">Waiting to contribute...</p>
          )}

          {contribution.status === 'thinking' && (
            <p className="text-yellow-400 text-sm mt-2 flex items-center gap-2">
              <Loader2 className="h-3 w-3 animate-spin" />
              Thinking...
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function SessionDetailPanel({
  sessionId,
  onClose,
}: {
  sessionId: string
  onClose: () => void
}) {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['hive-mind-session', sessionId],
    queryFn: () => hiveMindApi.detail(sessionId),
    refetchInterval: (query) => {
      // Poll every 2 seconds while session is in progress
      const session = query.state.data?.data?.session as SessionDetail | undefined
      if (session?.status === 'gathering' || session?.status === 'synthesizing') {
        return 2000
      }
      return false
    },
  })

  const session = data?.data?.session as SessionDetail | undefined
  const contributions = (data?.data?.contributions || []) as Contribution[]
  const progress = data?.data?.progress || 0

  // Subscribe to system events for this session
  useSystemEvents({
    onHiveMindStarted: useCallback(() => {
      queryClient.invalidateQueries({ queryKey: ['hive-mind-session', sessionId] })
    }, [queryClient, sessionId]),
  })

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="h-8 w-8 text-primary-400 animate-spin" />
      </div>
    )
  }

  if (error || !session) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-400">
        <AlertCircle className="h-12 w-12 mb-4" />
        <p>Failed to load session</p>
        <button onClick={onClose} className="mt-4 text-primary-400 hover:text-primary-300">
          Go back
        </button>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-dark-border">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-white">{session.question}</h3>
            {session.context && (
              <p className="text-sm text-gray-400 mt-1">{session.context}</p>
            )}
          </div>
          <div className="flex items-center gap-2 ml-4">
            <span className={cn('flex items-center gap-1', getStatusColor(session.status))}>
              {getStatusIcon(session.status)}
              {session.status}
            </span>
          </div>
        </div>

        {/* Progress bar for in-progress sessions */}
        {(session.status === 'gathering' || session.status === 'synthesizing') && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-400">Progress</span>
              <span className="text-white">{Math.round(progress)}%</span>
            </div>
            <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="flex items-center gap-6 mt-4 text-sm">
          <span className="text-gray-400">
            <Clock className="h-4 w-4 inline mr-1" />
            Started: {formatTimestamp(session.started_at)}
          </span>
          {session.completed_at && (
            <span className="text-gray-400">
              <CheckCircle className="h-4 w-4 inline mr-1" />
              Completed: {formatTimestamp(session.completed_at)}
            </span>
          )}
          {session.total_thinking_time > 0 && (
            <span className="text-gray-400">
              <Zap className="h-4 w-4 inline mr-1" />
              Total thinking: {formatDuration(session.total_thinking_time)}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Synthesis (if completed) */}
        {session.status === 'completed' && session.synthesis && (
          <div className="p-4 bg-gradient-to-br from-purple-900/30 to-blue-900/30 rounded-lg border border-purple-500/30">
            <h4 className="text-white font-medium flex items-center gap-2 mb-3">
              <Target className="h-5 w-5 text-purple-400" />
              Synthesized Answer
            </h4>
            <p className="text-gray-200 whitespace-pre-wrap">{session.synthesis}</p>
            {session.synthesis_summary && (
              <p className="text-sm text-gray-400 mt-4 pt-4 border-t border-purple-500/30">
                <strong>Summary:</strong> {session.synthesis_summary}
              </p>
            )}
          </div>
        )}

        {/* Contributions */}
        <div>
          <h4 className="text-white font-medium mb-4 flex items-center gap-2">
            <Users className="h-5 w-5 text-blue-400" />
            Agent Contributions ({contributions.length})
          </h4>
          <div className="space-y-3">
            {contributions.map((contribution) => (
              <ContributionCard key={contribution.id} contribution={contribution} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// Main Page
// ============================================================================

export default function HiveMindPage() {
  const queryClient = useQueryClient()
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)

  // Fetch sessions list
  const { data: sessionsData, isLoading: isLoadingSessions } = useQuery({
    queryKey: ['hive-mind-sessions'],
    queryFn: () => hiveMindApi.list(20),
  })

  const sessions = (sessionsData?.data?.sessions || []) as HiveMindSession[]

  // Start session mutation
  const startMutation = useMutation({
    mutationFn: (data: { question: string; context: string; maxAgents: number }) =>
      hiveMindApi.start({
        question: data.question,
        context: data.context,
        max_agents: data.maxAgents,
      }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['hive-mind-sessions'] })
      // Select the new session
      if (response.data?.session_id) {
        setSelectedSessionId(response.data.session_id)
      }
    },
  })

  // Subscribe to system events
  useSystemEvents({
    onHiveMindStarted: useCallback(() => {
      queryClient.invalidateQueries({ queryKey: ['hive-mind-sessions'] })
    }, [queryClient]),
  })

  const handleStartSession = (question: string, context: string, maxAgents: number) => {
    startMutation.mutate({ question, context, maxAgents })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <CompactBreadcrumb currentPage="Hive Mind" />
          <h1 className="text-2xl font-bold text-white mt-2 flex items-center gap-3">
            <Brain className="h-8 w-8 text-purple-400" />
            Hive Mind
          </h1>
          <p className="text-gray-400 mt-1">
            Multi-agent collaborative intelligence - all relevant agents working together
          </p>
        </div>
        <button
          onClick={() => queryClient.invalidateQueries({ queryKey: ['hive-mind-sessions'] })}
          className="p-2 text-gray-400 hover:text-white transition-colors"
          title="Refresh"
        >
          <RefreshCw className="h-5 w-5" />
        </button>
      </div>

      {/* Start New Session */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-yellow-400" />
          Start New Hive Mind Session
        </h2>
        <StartSessionForm
          onStart={handleStartSession}
          isStarting={startMutation.isPending}
        />
        {startMutation.isError && (
          <div className="mt-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
            Failed to start session: {(startMutation.error as Error)?.message || 'Unknown error'}
          </div>
        )}
      </div>

      {/* Sessions List and Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sessions List */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-blue-400" />
            Recent Sessions
          </h2>

          {isLoadingSessions ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 text-primary-400 animate-spin" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No hive mind sessions yet</p>
              <p className="text-sm mt-1">Start one above to see collective intelligence in action</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.map((session) => (
                <SessionCard
                  key={session.id}
                  session={session}
                  isSelected={selectedSessionId === session.id}
                  onClick={() => setSelectedSessionId(session.id)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Session Detail */}
        <div className="card min-h-[500px]">
          {selectedSessionId ? (
            <SessionDetailPanel
              sessionId={selectedSessionId}
              onClose={() => setSelectedSessionId(null)}
            />
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <Brain className="h-16 w-16 mb-4 opacity-30" />
              <p className="text-lg">Select a session to view details</p>
              <p className="text-sm mt-1">Or start a new hive mind session above</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
