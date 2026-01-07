import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { timeTravelApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'
import {
  History,
  Clock,
  GitBranch,
  Flag,
  Bookmark,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Search,
  RefreshCw,
  ChevronRight,
  Play,
  Target,
  Lightbulb,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
interface TimeSession {
  id: string
  agent_id: string
  agent_name: string
  context: string
  started_at: string
  ended_at?: string
  is_active: boolean
  is_bookmarked: boolean
  decision_count: number
  decisions?: Decision[]
}

interface Decision {
  id: string
  session_id: string
  decision_type: string
  description: string
  options_considered: string[]
  chosen_option: string
  reasoning: string
  outcome?: string
  success?: boolean
  is_flagged: boolean
  flag_reason?: string
  created_at: string
  annotations?: Annotation[]
}

interface Annotation {
  id: string
  text: string
  created_at: string
}

// Decision type configuration
const DECISION_TYPE_CONFIG: Record<string, { icon: typeof Target; color: string; bgColor: string; label: string }> = {
  strategic: { icon: Target, color: 'text-purple-400', bgColor: 'bg-purple-500/20', label: 'Strategic' },
  tactical: { icon: GitBranch, color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Tactical' },
  creative: { icon: Lightbulb, color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', label: 'Creative' },
  analytical: { icon: Search, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Analytical' },
  operational: { icon: Play, color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Operational' },
}

const getDecisionConfig = (type: string) => {
  return DECISION_TYPE_CONFIG[type?.toLowerCase()] || DECISION_TYPE_CONFIG.tactical
}

const formatDuration = (startedAt: string, endedAt?: string) => {
  const start = new Date(startedAt)
  const end = endedAt ? new Date(endedAt) : new Date()
  const diff = end.getTime() - start.getTime()

  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(minutes / 60)

  if (hours > 0) return `${hours}h ${minutes % 60}m`
  return `${minutes}m`
}

export default function TimeTravelPage() {
  const [selectedSession, setSelectedSession] = useState<TimeSession | null>(null)
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'sessions' | 'flagged'>('sessions')

  // Fetch overview
  const { data: overviewData, isLoading: loadingOverview, refetch: refetchOverview } = useQuery({
    queryKey: ['time-travel-overview'],
    queryFn: async () => {
      const response = await timeTravelApi.overview()
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch flagged decisions
  const { data: flaggedData, isLoading: loadingFlagged } = useQuery({
    queryKey: ['time-travel-flagged'],
    queryFn: async () => {
      const response = await timeTravelApi.flaggedDecisions(50)
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch session detail when selected
  const { data: sessionDetailData } = useQuery({
    queryKey: ['time-travel-session', selectedSession?.id],
    queryFn: async () => {
      if (!selectedSession?.id) return null
      const response = await timeTravelApi.sessionDetail(selectedSession.id)
      return response.data
    },
    enabled: !!selectedSession?.id,
    staleTime: 30000,
  })

  // Parse data
  const sessions: TimeSession[] = overviewData?.sessions || overviewData || []
  const flaggedDecisions: Decision[] = flaggedData?.decisions || flaggedData || []
  const sessionDetail = sessionDetailData || selectedSession

  // Filter sessions
  const filteredSessions = sessions.filter(session =>
    session.agent_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.context?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Calculate stats
  const totalSessions = sessions.length
  const activeSessions = sessions.filter(s => s.is_active).length
  const totalDecisions = sessions.reduce((sum, s) => sum + (s.decision_count || 0), 0)

  // Select first session on load
  useEffect(() => {
    if (sessions.length > 0 && !selectedSession) {
      setSelectedSession(sessions[0])
    }
  }, [sessions, selectedSession])

  const isLoading = loadingOverview

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb currentPage="Time Travel" />
          <p className="text-sm text-gray-400 mt-1">
            Decision tracking, session replay, and outcome analysis
          </p>
        </div>
        <button
          onClick={() => refetchOverview()}
          className="flex items-center gap-2 px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:text-white hover:bg-dark-bg transition-colors"
        >
          <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <History className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalSessions}</p>
              <p className="text-xs text-gray-400">Total Sessions</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Play className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{activeSessions}</p>
              <p className="text-xs text-gray-400">Active Sessions</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <GitBranch className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalDecisions}</p>
              <p className="text-xs text-gray-400">Total Decisions</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <Flag className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{flaggedDecisions.length}</p>
              <p className="text-xs text-gray-400">Flagged for Review</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel - Sessions List */}
        <div className="col-span-2 space-y-4">
          {/* Tabs */}
          <div className="flex items-center gap-2 border-b border-dark-border pb-2">
            <button
              onClick={() => setActiveTab('sessions')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'sessions'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <History size={16} className="inline mr-2" />
              Sessions ({sessions.length})
            </button>
            <button
              onClick={() => setActiveTab('flagged')}
              className={cn(
                'px-4 py-2 rounded-t-lg text-sm font-medium transition-colors',
                activeTab === 'flagged'
                  ? 'bg-dark-card text-white border border-dark-border border-b-0'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Flag size={16} className="inline mr-2" />
              Flagged ({flaggedDecisions.length})
            </button>
          </div>

          {activeTab === 'sessions' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              {/* Search */}
              <div className="p-4 border-b border-dark-border">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search sessions..."
                    className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Sessions List */}
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingOverview ? (
                  <div className="p-8 text-center text-gray-400">Loading sessions...</div>
                ) : filteredSessions.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">No sessions found</div>
                ) : (
                  filteredSessions.map((session) => (
                    <button
                      key={session.id}
                      onClick={() => {
                        setSelectedSession(session)
                        setSelectedDecision(null)
                      }}
                      className={cn(
                        'w-full p-4 flex items-center gap-4 hover:bg-dark-bg transition-colors text-left',
                        selectedSession?.id === session.id && 'bg-dark-bg'
                      )}
                    >
                      {/* Status Icon */}
                      <div className={cn(
                        'p-3 rounded-full',
                        session.is_active ? 'bg-green-500/20' : 'bg-gray-500/20'
                      )}>
                        {session.is_active ? (
                          <Play className="w-5 h-5 text-green-400" />
                        ) : (
                          <History className="w-5 h-5 text-gray-400" />
                        )}
                      </div>

                      {/* Session Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white truncate">{session.agent_name}</span>
                          {session.is_bookmarked && (
                            <Bookmark size={14} className="text-yellow-400 fill-yellow-400" />
                          )}
                          {session.is_active && (
                            <span className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400">
                              Active
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-400 truncate mt-1">
                          {session.context || 'No context provided'}
                        </p>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <GitBranch size={12} />
                            {session.decision_count} decisions
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock size={12} />
                            {formatDuration(session.started_at, session.ended_at)}
                          </span>
                        </div>
                      </div>

                      <ChevronRight size={16} className="text-gray-500" />
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'flagged' && (
            <div className="bg-dark-card rounded-lg border border-dark-border">
              <div className="p-4 border-b border-dark-border">
                <h3 className="font-medium text-white">Flagged Decisions</h3>
                <p className="text-xs text-gray-400 mt-1">Decisions marked for review or follow-up</p>
              </div>
              <div className="divide-y divide-dark-border max-h-[600px] overflow-y-auto">
                {loadingFlagged ? (
                  <div className="p-8 text-center text-gray-400">Loading flagged decisions...</div>
                ) : flaggedDecisions.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">No flagged decisions</div>
                ) : (
                  flaggedDecisions.map((decision) => {
                    const config = getDecisionConfig(decision.decision_type)
                    const Icon = config.icon

                    return (
                      <button
                        key={decision.id}
                        onClick={() => setSelectedDecision(decision)}
                        className={cn(
                          'w-full p-4 flex items-start gap-4 hover:bg-dark-bg transition-colors text-left',
                          selectedDecision?.id === decision.id && 'bg-dark-bg'
                        )}
                      >
                        <div className={cn('p-2 rounded-lg', config.bgColor)}>
                          <Icon className={cn('w-4 h-4', config.color)} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white truncate">
                              {decision.description}
                            </span>
                            <Flag size={14} className="text-yellow-400" />
                          </div>
                          <p className="text-sm text-yellow-400/80 mt-1">
                            {decision.flag_reason || 'No reason provided'}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(decision.created_at).toLocaleString()}
                          </p>
                        </div>
                      </button>
                    )
                  })
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Session/Decision Detail */}
        <div className="space-y-4">
          {selectedDecision ? (
            // Decision Detail View
            <>
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <button
                  onClick={() => setSelectedDecision(null)}
                  className="text-sm text-gray-400 hover:text-white mb-3"
                >
                  ← Back to session
                </button>
                {(() => {
                  const config = getDecisionConfig(selectedDecision.decision_type)
                  const Icon = config.icon

                  return (
                    <>
                      <div className="flex items-center gap-3 mb-4">
                        <div className={cn('p-2 rounded-lg', config.bgColor)}>
                          <Icon className={cn('w-5 h-5', config.color)} />
                        </div>
                        <div>
                          <span className={cn('text-xs px-2 py-0.5 rounded', config.bgColor, config.color)}>
                            {config.label}
                          </span>
                        </div>
                      </div>
                      <h3 className="font-medium text-white">{selectedDecision.description}</h3>
                    </>
                  )
                })()}
              </div>

              {/* Reasoning */}
              {selectedDecision.reasoning && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-2 flex items-center gap-2">
                    <Lightbulb size={16} className="text-yellow-400" />
                    Reasoning
                  </h4>
                  <p className="text-sm text-gray-300">{selectedDecision.reasoning}</p>
                </div>
              )}

              {/* Options Considered */}
              {(selectedDecision.options_considered || []).length > 0 && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-2">Options Considered</h4>
                  <div className="space-y-2">
                    {selectedDecision.options_considered.map((option, i) => (
                      <div
                        key={i}
                        className={cn(
                          'p-2 rounded text-sm',
                          option === selectedDecision.chosen_option
                            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                            : 'bg-dark-bg text-gray-300'
                        )}
                      >
                        {option === selectedDecision.chosen_option && (
                          <CheckCircle size={14} className="inline mr-2" />
                        )}
                        {option}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Outcome */}
              {selectedDecision.outcome && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-2 flex items-center gap-2">
                    {selectedDecision.success ? (
                      <CheckCircle size={16} className="text-green-400" />
                    ) : selectedDecision.success === false ? (
                      <XCircle size={16} className="text-red-400" />
                    ) : (
                      <AlertTriangle size={16} className="text-yellow-400" />
                    )}
                    Outcome
                  </h4>
                  <p className="text-sm text-gray-300">{selectedDecision.outcome}</p>
                </div>
              )}
            </>
          ) : selectedSession ? (
            // Session Detail View
            <>
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                <div className="text-center">
                  <div className={cn(
                    'inline-flex items-center justify-center w-16 h-16 rounded-full mb-4',
                    sessionDetail?.is_active ? 'bg-green-500/20' : 'bg-purple-500/20'
                  )}>
                    {sessionDetail?.is_active ? (
                      <Play className="w-8 h-8 text-green-400" />
                    ) : (
                      <History className="w-8 h-8 text-purple-400" />
                    )}
                  </div>

                  <h3 className="text-lg font-medium text-white">{sessionDetail?.agent_name}</h3>

                  <div className="flex items-center justify-center gap-2 mt-2">
                    {sessionDetail?.is_active && (
                      <span className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400">
                        Active
                      </span>
                    )}
                    {sessionDetail?.is_bookmarked && (
                      <span className="text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 flex items-center gap-1">
                        <Bookmark size={12} /> Bookmarked
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-gray-400 mt-3">
                    {sessionDetail?.context || 'No context provided'}
                  </p>
                </div>

                {/* Session Stats */}
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">{sessionDetail?.decision_count || 0}</div>
                    <div className="text-xs text-gray-400">Decisions</div>
                  </div>
                  <div className="text-center p-3 bg-dark-bg rounded-lg">
                    <div className="text-lg font-bold text-white">
                      {formatDuration(sessionDetail?.started_at || '', sessionDetail?.ended_at)}
                    </div>
                    <div className="text-xs text-gray-400">Duration</div>
                  </div>
                </div>
              </div>

              {/* Decisions in Session */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <GitBranch size={16} className="text-blue-400" />
                  Decision Timeline
                </h4>
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {(sessionDetail?.decisions || []).length === 0 ? (
                    <p className="text-sm text-gray-400">No decisions recorded yet</p>
                  ) : (
                    (sessionDetail?.decisions || []).map((decision: Decision) => {
                      const config = getDecisionConfig(decision.decision_type)
                      const Icon = config.icon

                      return (
                        <button
                          key={decision.id}
                          onClick={() => setSelectedDecision(decision)}
                          className="w-full p-3 bg-dark-bg rounded-lg hover:bg-dark-border/50 transition-colors text-left"
                        >
                          <div className="flex items-center gap-2">
                            <Icon className={cn('w-4 h-4', config.color)} />
                            <span className="text-sm text-white truncate flex-1">
                              {decision.description}
                            </span>
                            {decision.is_flagged && (
                              <Flag size={12} className="text-yellow-400" />
                            )}
                            {decision.success === true && (
                              <CheckCircle size={12} className="text-green-400" />
                            )}
                            {decision.success === false && (
                              <XCircle size={12} className="text-red-400" />
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(decision.created_at).toLocaleTimeString()}
                          </p>
                        </button>
                      )
                    })
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              <History size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Select a session to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
